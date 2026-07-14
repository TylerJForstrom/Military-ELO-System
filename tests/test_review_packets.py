import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from military_elo.claims import Claim, EvidenceLink, SourceLocator
from military_elo.review import (
    Adjudication,
    _allocate_sample,
    build_gold_set_document,
    build_review_packet,
    load_json_records,
    sample_gold_set,
)


ROOT = Path(__file__).resolve().parents[1]
CHECKSUM = "c" * 64


def make_records():
    records = []
    strata = [
        ("ancient", "Africa", "tactical", "land", "family-a"),
        ("medieval", "Asia", "operational", "mixed", "family-b"),
        ("modern", "Europe", "strategic", "naval", "family-c"),
        ("contemporary", "Americas", "tactical", "air", "family-d"),
    ]
    for group_index, values in enumerate(strata):
        era, region, layer, domain, family = values
        for item_index in range(5):
            records.append(
                {
                    "id": f"record-{group_index}-{item_index}",
                    "era": era,
                    "region": region,
                    "layer": layer,
                    "domain": domain,
                    "source_family": family,
                    "uncertain": {"low": item_index, "high": item_index + 1},
                }
            )
    return records


def source_locator():
    return SourceLocator(
        source_id="source-a",
        edition="v1",
        page=10,
        url="https://example.test/source#page=10",
        checksum=CHECKSUM,
        language="en",
        source_family="family-a",
        creator="Source Author",
    )


class GoldSetSamplingTests(unittest.TestCase):
    def test_sampling_is_seeded_stratified_and_input_order_independent(self):
        records = make_records()
        fields = ("era", "region", "layer", "domain", "source_family")
        first = sample_gold_set(records, 8, seed=17, stratify_by=fields)
        reordered = sample_gold_set(list(reversed(records)), 8, seed=17, stratify_by=fields)
        other_seed = sample_gold_set(records, 8, seed=19, stratify_by=fields)
        self.assertEqual(first, reordered)
        self.assertNotEqual(
            {item["id"] for item in first},
            {item["id"] for item in other_seed},
        )
        self.assertEqual(len({item["era"] for item in first}), 4)

    def test_gold_document_records_population_sample_and_unknown_strata(self):
        records = [
            {"id": "known", "era": "modern", "region": "Europe"},
            {"id": "unknown"},
        ]
        document = build_gold_set_document(
            records,
            2,
            seed=1900,
            stratify_by=("era", "region", "layer", "domain", "source_family"),
        )
        self.assertEqual(document["population_size"], 2)
        self.assertEqual(document["sample_size"], 2)
        unknown = next(
            item
            for item in document["strata_population"]
            if item["stratum"]["era"] == "unknown"
        )
        self.assertEqual(unknown["stratum"]["source_family"], "unknown")

    def test_generic_source_name_is_not_inferred_as_source_family(self):
        document = build_gold_set_document(
            [{"id": "record", "source": "dataset-release-name"}],
            1,
            seed=1,
            stratify_by=("source_family",),
        )
        self.assertEqual(
            document["strata_population"][0]["stratum"]["source_family"],
            "unknown",
        )

    def test_explicit_id_field_never_falls_back(self):
        with self.assertRaises(ValueError):
            sample_gold_set(
                [{"id": "fallback-only"}],
                1,
                seed=1,
                id_field="review_unit_id",
            )
        with self.assertRaises(ValueError):
            sample_gold_set(
                [
                    {"id": "one", "review_unit_id": "duplicate"},
                    {"id": "two", "review_unit_id": "duplicate"},
                ],
                1,
                seed=1,
                id_field="review_unit_id",
            )

    def test_largest_remainder_allocation_is_proportional_and_seeded_on_ties(self):
        self.assertEqual(
            _allocate_sample({("a",): 1, ("b",): 3, ("c",): 2}, 2, seed=1),
            {("a",): 0, ("b",): 1, ("c",): 1},
        )
        six = _allocate_sample({("a",): 2, ("b",): 2, ("c",): 5}, 6, seed=1)
        self.assertEqual(six[("c",)], 3)

        singleton_sizes = {("A",): 1, ("B",): 1, ("C",): 1}
        choices = {
            next(key for key, count in _allocate_sample(singleton_sizes, 1, seed=seed).items() if count)
            for seed in (1, 2, 4)
        }
        self.assertGreater(len(choices), 1)

    def test_population_digest_and_manifest_bind_ids_and_strata_without_model_output(self):
        records = [
            {"id": "b", "region": "Europe", "rating": 1800},
            {"id": "a", "region": "Asia", "rank": 1},
        ]
        first = build_gold_set_document(records, 1, seed=4, stratify_by=("region",))
        reordered = build_gold_set_document(
            list(reversed(records)), 1, seed=4, stratify_by=("region",)
        )
        self.assertEqual(first["population_digest"], reordered["population_digest"])
        self.assertEqual(first["population_manifest"], reordered["population_manifest"])
        self.assertRegex(first["population_digest"], r"^sha256:[0-9a-f]{64}$")
        serialized_selection = json.dumps(first["records"], sort_keys=True)
        self.assertNotIn("rating", serialized_selection)
        self.assertNotIn("rank", serialized_selection)

    def test_named_container_with_wrong_type_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "claims.json"
            path.write_text(json.dumps({"claims": {"id": "not-an-array"}}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_json_records(path, container_keys=("claims",))

    def test_json_and_jsonl_inputs_and_sampler_cli_are_deterministic(self):
        records = [
            {key: value for key, value in record.items() if key != "source_family"}
            for record in make_records()[:6]
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            json_path = root / "records.json"
            jsonl_path = root / "records.jsonl"
            output = root / "gold.json"
            json_path.write_text(json.dumps(records), encoding="utf-8")
            jsonl_path.write_text(
                "".join(json.dumps(item, sort_keys=True) + "\n" for item in records),
                encoding="utf-8",
            )
            self.assertEqual(load_json_records(json_path), load_json_records(jsonl_path))
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "sample_gold_set.py"),
                    str(jsonl_path),
                    "--output",
                    str(output),
                    "--size",
                    "3",
                    "--seed",
                    "23",
                    "--source-family",
                    f"{jsonl_path}=family-cli",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output_bytes = output.read_bytes()
            self.assertTrue(output_bytes.endswith(b"\n"))
            self.assertNotIn(b"\r\n", output_bytes)
            document = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(document["seed"], 23)
            self.assertEqual(
                {item["stratum"]["source_family"] for item in document["population_manifest"]},
                {"family-cli"},
            )

    def test_sampler_cli_refuses_in_repository_production_output(self):
        records = make_records()[:1]
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "records.json"
            input_path.write_text(json.dumps(records), encoding="utf-8")
            forbidden = ROOT / "data" / "release" / "gold-set-should-not-exist.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "sample_gold_set.py"),
                    str(input_path),
                    "--output",
                    str(forbidden),
                    "--size",
                    "1",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(forbidden.exists())


class ReviewPacketTests(unittest.TestCase):
    def _claims(self):
        return [
            Claim(
                id="claim-a",
                subject="event-1",
                predicate="winner",
                value="side-a",
                precision="categorical",
                provenance=(source_locator(),),
                contradicts=("claim-b",),
                evidence_ids=("evidence-a",),
            ),
            Claim(
                id="claim-b",
                subject="event-1",
                predicate="winner",
                value="side-b",
                precision="categorical",
                provenance=(source_locator(),),
                contradicts=("claim-a",),
            ),
        ]

    def _events(self):
        return [
            {
                "id": "event-1",
                "name": "Event",
                "aliases": ["Alternate name"],
                "event_type": "engagement",
                "domain": "land",
                "claim_ids": ["claim-a", "claim-b"],
                "participants": [
                    {
                        "entity_id": "entity-a",
                        "side": "a",
                        "role": "primary",
                        "contribution": 0.8,
                        "outcome": {"battlefield_control": 1.0},
                        "delta": 22.5,
                    }
                ],
                "rating": 1700,
                "rank": 1,
                "leaderboard": [{"entity": "entity-a"}],
                "sensitivity": {"p10": 1600},
            }
        ]

    def test_packet_preserves_disagreement_and_exact_evidence_but_not_model_effects(self):
        link = EvidenceLink(
            id="evidence-a",
            claim_id="claim-a",
            locator=source_locator(),
            relationship="supports",
            source_family="family-a",
        )
        prior = Adjudication(
            id="decision-a",
            claim_id="claim-a",
            reviewer="reviewer-a",
            decision="accepted",
            rationale="Evidence supports the claim.",
            codebook_version="1.0",
        )
        packet = build_review_packet(
            self._events(),
            self._claims(),
            [prior],
            evidence_links=[link],
        )
        self.assertTrue(packet["blinded"])
        self.assertFalse(packet["leaderboard_effects_included"])
        self.assertEqual(len(packet["claims"]), 2)
        self.assertEqual(len(packet["disagreements"]), 1)
        self.assertEqual(packet["evidence_links"][0]["locator"]["page"], 10)
        self.assertNotIn("adjudications", packet)
        serialized = json.dumps(packet, sort_keys=True)
        for forbidden in ('"rating"', '"rank"', '"delta"', '"leaderboard"', '"sensitivity"'):
            self.assertNotIn(forbidden, serialized)

    def test_prior_decisions_are_opt_in_and_supersession_history_is_preserved(self):
        first = Adjudication(
            "z-old",
            "claim-a",
            "reviewer-a",
            "needs_more_evidence",
            "Need another source.",
            "1.0",
        )
        second = Adjudication(
            "a-new",
            "claim-a",
            "reviewer-a",
            "accepted",
            "A second source was reviewed.",
            "1.0",
            supersedes=("z-old",),
        )
        link = EvidenceLink(
            "evidence-a",
            "claim-a",
            source_locator(),
            "supports",
            "family-a",
        )
        packet = build_review_packet(
            self._events(),
            self._claims(),
            [first, second],
            evidence_links=[link],
            include_prior_decisions=True,
        )
        self.assertEqual(
            [item["id"] for item in packet["adjudications"]],
            ["z-old", "a-new"],
        )
        self.assertEqual(packet["adjudications"][1]["supersedes"], ["z-old"])
        self.assertFalse(packet["blinded"])
        self.assertTrue(packet["prior_decisions_included"])

    def test_prior_decision_rationale_cannot_smuggle_model_output(self):
        evidence_claim = Claim(
            "claim-a",
            "event-1",
            "winner",
            "a",
            "categorical",
            provenance=(source_locator(),),
        )
        leaked = Adjudication(
            "decision-a",
            "claim-a",
            "reviewer-a",
            "accepted",
            "The current rating is 1900.",
            "1.0",
        )
        with self.assertRaises(ValueError):
            build_review_packet(
                [{"id": "event-1", "name": "Event"}],
                [evidence_claim],
                [leaked],
                include_prior_decisions=True,
            )

    def test_event_filter_includes_participation_episode_claim_references(self):
        events = [
            {
                "id": "event-1",
                "name": "Event",
                "participation_episodes": [
                    {
                        "id": "episode-1",
                        "entity_id": "entity-a",
                        "side": "a",
                        "role": "primary",
                        "claim_ids": ["claim-episode"],
                    }
                ],
            },
            {"id": "event-2", "name": "Other"},
        ]
        claims = [
            Claim(
                "claim-episode",
                "episode-1",
                "entry_date",
                "1914-08-01",
                "day",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-unrelated",
                "event-2",
                "winner",
                "side-b",
                "categorical",
                provenance=(source_locator(),),
            ),
        ]
        packet = build_review_packet(events, claims, event_ids=["event-1"])
        self.assertEqual([item["id"] for item in packet["claims"]], ["claim-episode"])

    def test_packet_refuses_model_output_hidden_inside_claim_value(self):
        for field in ("rating", "elo", "rank", "delta", "leaderboard"):
            with self.subTest(field=field):
                malicious = Claim(
                    id=f"claim-malicious-{field}",
                    subject="event-1",
                    predicate="context",
                    value={field: 1700},
                    precision=None,
                    provenance=(source_locator(),),
                )
                with self.assertRaises(ValueError):
                    build_review_packet([{"id": "event-1", "name": "Event"}], [malicious])

    def test_packet_refuses_model_predicates_and_compound_output_keys(self):
        event = [{"id": "event-1", "name": "Event"}]
        for predicate in ("rating", "elo", "rank", "delta", "median_rank"):
            with self.subTest(predicate=predicate):
                malicious = Claim(
                    f"claim-{predicate}",
                    "event-1",
                    predicate,
                    1700,
                    None,
                    provenance=(source_locator(),),
                )
                with self.assertRaises(ValueError):
                    build_review_packet(event, [malicious])
        for key in (
            "rating_before",
            "eloAfter",
            "median_rank",
            "coverage_factor_estimate",
            "model_outputs",
        ):
            malicious = Claim(
                f"claim-key-{key}",
                "event-1",
                "historical_context",
                {key: 1700},
                None,
                provenance=(source_locator(),),
            )
            with self.assertRaises(ValueError):
                build_review_packet(event, [malicious])

    def test_packet_rejects_dangling_claim_and_evidence_references(self):
        with self.assertRaises(ValueError):
            build_review_packet(
                [{"id": "event-1", "name": "Event", "claim_ids": ["missing"]}],
                [],
            )
        missing_evidence = Claim(
            "claim-a",
            "event-1",
            "winner",
            "a",
            "categorical",
            evidence_ids=("missing-evidence",),
        )
        with self.assertRaises(ValueError):
            build_review_packet([{"id": "event-1", "name": "Event"}], [missing_evidence])
        with self.assertRaises(ValueError):
            build_review_packet(
                [{"id": "event-1", "name": "Event", "claim_ids": "claim-a"}],
                [missing_evidence],
            )

    def test_packet_filters_unrelated_claims_and_closes_disagreement(self):
        selected = Claim(
            "claim-a",
            "episode-1",
            "entry",
            1914,
            "year",
            provenance=(source_locator(),),
            contradicts=("claim-b",),
        )
        alternative = Claim(
            "claim-b",
            "episode-1",
            "entry",
            1915,
            "year",
            provenance=(source_locator(),),
            contradicts=("claim-a",),
        )
        unrelated = Claim(
            "claim-secret",
            "event-2",
            "winner",
            "b",
            "categorical",
            provenance=(source_locator(),),
        )
        packet = build_review_packet(
            [
                {
                    "id": "event-1",
                    "name": "Event",
                    "participation_episodes": [
                        {
                            "id": "episode-1",
                            "entity_id": "entity-a",
                            "side": "a",
                            "role": "primary",
                            "claim_ids": ["claim-a"],
                        }
                    ],
                }
            ],
            [selected, alternative, unrelated],
        )
        self.assertEqual([item["id"] for item in packet["claims"]], ["claim-a", "claim-b"])
        self.assertEqual(len(packet["disagreements"]), 1)

    def test_empty_event_selection_selects_nothing(self):
        packet = build_review_packet(self._events(), self._claims(), event_ids=[])
        self.assertEqual(packet["events"], [])
        self.assertEqual(packet["claims"], [])

    def test_legitimate_expected_and_actual_source_evidence_is_not_censored(self):
        historical = Claim(
            id="claim-source-expectation",
            subject="event-1",
            predicate="reported_force_plan",
            value={
                "expected": "relief before winter",
                "actual": "relief arrived in spring",
                "importance": "described as a primary objective",
                "series": "archival dispatch series B",
            },
            precision="quoted_synthesis",
            provenance=(source_locator(),),
        )
        packet = build_review_packet([{"id": "event-1", "name": "Event"}], [historical])
        self.assertEqual(packet["claims"][0]["value"]["expected"], "relief before winter")

    def test_dict_event_set_fields_and_episode_order_are_deterministic(self):
        first = {
            "id": "event-1",
            "name": "Event",
            "aliases": ["B", "A", "A"],
            "source_ids": ["source-b", "source-a"],
            "participation_episodes": [
                {"id": "b", "entity_id": "b", "side": "b", "role": "primary"},
                {"id": "a", "entity_id": "a", "side": "a", "role": "primary"},
            ],
        }
        second = {
            **first,
            "aliases": ["A", "B"],
            "source_ids": ["source-a", "source-b"],
            "participation_episodes": list(reversed(first["participation_episodes"])),
        }
        self.assertEqual(build_review_packet([first], []), build_review_packet([second], []))

    def test_review_packet_cli_empty_selection_does_not_expand_to_all_events(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            events = root / "events.json"
            claims = root / "claims.json"
            selection = root / "selection.json"
            output = root / "packet.json"
            events.write_text(json.dumps(self._events()), encoding="utf-8")
            claims.write_text(json.dumps([item.to_dict() for item in self._claims()]), encoding="utf-8")
            selection.write_text(json.dumps({"records": []}), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_review_packet.py"),
                    "--events",
                    str(events),
                    "--claims",
                    str(claims),
                    "--selection",
                    str(selection),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(packet["events"], [])
            self.assertEqual(packet["claims"], [])


if __name__ == "__main__":
    unittest.main()
