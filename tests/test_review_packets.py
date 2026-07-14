import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from military_elo.claims import Claim, EvidenceLink, SourceLocator
from military_elo.models import Event
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
        changed_payload = build_gold_set_document(
            [
                {"id": "b", "region": "Europe", "rating": 1801},
                {"id": "a", "region": "Asia", "rank": 1},
            ],
            1,
            seed=4,
            stratify_by=("region",),
        )
        self.assertEqual(first["population_manifest"], changed_payload["population_manifest"])
        self.assertNotEqual(first["population_digest"], changed_payload["population_digest"])
        self.assertRegex(first["population_digest"], r"^sha256:[0-9a-f]{64}$")
        serialized_selection = json.dumps(first["records"], sort_keys=True)
        self.assertNotIn("rating", serialized_selection)
        self.assertNotIn("rank", serialized_selection)

    def test_canonical_string_date_is_stratified_by_era(self):
        document = build_gold_set_document(
            [
                {
                    "id": "event-1914",
                    "date_interval": {
                        "start": {
                            "low": "1914-07-28",
                            "best": "1914-07-28",
                            "high": "1914-07-28",
                            "precision": "day",
                        },
                        "end": {
                            "low": "1914-07-28",
                            "best": "1914-07-28",
                            "high": "1914-07-28",
                            "precision": "day",
                        },
                    },
                }
            ],
            1,
            seed=7,
        )
        self.assertEqual(document["strata_population"][0]["stratum"]["era"], "modern")

        malformed = build_gold_set_document(
            [
                {
                    "id": "event-bool-date",
                    "date_interval": {
                        "start": {"low": True, "best": True, "high": True},
                    },
                }
            ],
            1,
            seed=7,
        )
        self.assertEqual(
            malformed["strata_population"][0]["stratum"]["era"],
            "unknown",
        )

    def test_sampling_requires_integer_seed_and_nonblank_string_ids(self):
        records = [{"id": "record-a"}]
        for invalid_seed in (None, True, False, 1.5, "7"):
            with self.subTest(seed=invalid_seed):
                with self.assertRaises(TypeError):
                    sample_gold_set(records, 1, seed=invalid_seed)
                with self.assertRaises(TypeError):
                    build_gold_set_document(records, 1, seed=invalid_seed)

        for invalid_id in (" ", False, 7, {}, []):
            with self.subTest(record_id=invalid_id):
                with self.assertRaises(ValueError):
                    sample_gold_set([{"id": invalid_id}], 1, seed=7)
                with self.assertRaises(ValueError):
                    sample_gold_set(
                        [{"review_unit_id": invalid_id}],
                        1,
                        seed=7,
                        id_field="review_unit_id",
                    )

    def test_sampling_requires_integer_size_and_ordered_unique_strata(self):
        records = [{"id": "record-a", "region": "Europe"}]
        for invalid_size in (True, False, 1.0, 1.5, "1"):
            with self.subTest(size=invalid_size), self.assertRaises(TypeError):
                sample_gold_set(records, invalid_size, seed=7)
            with self.subTest(document_size=invalid_size), self.assertRaises(TypeError):
                build_gold_set_document(records, invalid_size, seed=7)

        invalid_strata = (
            "region",
            b"region",
            {"region"},
            frozenset({"region"}),
            ("region", "region"),
            ("region", " "),
            ("region", 7),
        )
        for invalid in invalid_strata:
            with self.subTest(stratify_by=invalid), self.assertRaises(
                (TypeError, ValueError)
            ):
                sample_gold_set(records, 1, seed=7, stratify_by=invalid)

        fields = (name for name in ("region", "source_family"))
        document = build_gold_set_document(
            records,
            1,
            seed=7,
            stratify_by=fields,
        )
        self.assertEqual(document["stratify_by"], ["region", "source_family"])
        self.assertEqual(
            set(document["strata_population"][0]["stratum"]),
            {"region", "source_family"},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "records.json"
            output_path = Path(temp_dir) / "gold.json"
            input_path.write_text(json.dumps(records), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "sample_gold_set.py"),
                    str(input_path),
                    "--output",
                    str(output_path),
                    "--size",
                    "1.5",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output_path.exists())

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

    def test_packet_rejects_invalid_direct_adjudication_metadata(self):
        link = EvidenceLink(
            "evidence-a",
            "claim-a",
            source_locator(),
            "supports",
            "family-a",
        )
        invalid_decisions = (
            Adjudication(
                "confidence-high",
                "claim-a",
                "reviewer-a",
                "accepted",
                "Evidence supports the claim.",
                "1.0",
                confidence=2,
            ),
            Adjudication(
                "blank-stage",
                "claim-a",
                "reviewer-a",
                "accepted",
                "Evidence supports the claim.",
                "1.0",
                review_stage="  ",
            ),
            Adjudication(
                "typed-reviewed-at",
                "claim-a",
                "reviewer-a",
                "accepted",
                "Evidence supports the claim.",
                "1.0",
                reviewed_at=123,
            ),
        )
        for decision in invalid_decisions:
            with self.subTest(decision=decision.id), self.assertRaisesRegex(
                ValueError, "Invalid append-only adjudication history"
            ):
                build_review_packet(
                    self._events(),
                    self._claims(),
                    [decision],
                    evidence_links=[link],
                    include_prior_decisions=True,
                )

    def test_prior_decision_evidence_is_included_from_its_claim(self):
        claim = Claim(
            "claim-a",
            "event-1",
            "winner",
            "side-a",
            "categorical",
            provenance=(source_locator(),),
            evidence_ids=("evidence-decision",),
        )
        link = EvidenceLink(
            "evidence-decision",
            "claim-a",
            source_locator(),
            "context",
            "family-a",
        )
        decision = Adjudication(
            "decision-a",
            "claim-a",
            "reviewer-a",
            "needs_more_evidence",
            "The contextual source was considered.",
            "1.0",
            evidence_ids_considered=("evidence-decision",),
        )
        packet = build_review_packet(
            [{"id": "event-1", "name": "Event", "claim_ids": ["claim-a"]}],
            [claim],
            [decision],
            evidence_links=[link],
            include_prior_decisions=True,
        )
        self.assertEqual(
            [item["id"] for item in packet["evidence_links"]],
            ["evidence-decision"],
        )
        self.assertEqual(
            packet["adjudications"][0]["evidence_ids_considered"],
            ["evidence-decision"],
        )

    def test_prior_decision_rejects_considered_evidence_unreferenced_by_claim(self):
        claim = Claim(
            "claim-a",
            "event-1",
            "winner",
            "side-a",
            "categorical",
            provenance=(source_locator(),),
        )
        link = EvidenceLink(
            "evidence-decision",
            "claim-a",
            source_locator(),
            "context",
            "family-a",
        )
        decision = Adjudication(
            "decision-a",
            "claim-a",
            "reviewer-a",
            "needs_more_evidence",
            "The contextual source was considered.",
            "1.0",
            evidence_ids_considered=("evidence-decision",),
        )
        with self.assertRaisesRegex(ValueError, "not referenced by claim claim-a"):
            build_review_packet(
                [{"id": "event-1", "name": "Event", "claim_ids": ["claim-a"]}],
                [claim],
                [decision],
                evidence_links=[link],
                include_prior_decisions=True,
            )

    def test_prior_decision_rejects_missing_considered_evidence(self):
        claim = Claim(
            "claim-a",
            "event-1",
            "winner",
            "side-a",
            "categorical",
            provenance=(source_locator(),),
        )
        decision = Adjudication(
            "decision-a",
            "claim-a",
            "reviewer-a",
            "needs_more_evidence",
            "A missing link was recorded.",
            "1.0",
            evidence_ids_considered=("missing-link",),
        )
        with self.assertRaisesRegex(ValueError, "unknown evidence link missing-link"):
            build_review_packet(
                [{"id": "event-1", "name": "Event", "claim_ids": ["claim-a"]}],
                [claim],
                [decision],
                include_prior_decisions=True,
            )

    def test_prior_decision_rejects_cross_claim_considered_evidence(self):
        claim_a = Claim(
            "claim-a",
            "event-1",
            "winner",
            "side-a",
            "categorical",
            provenance=(source_locator(),),
        )
        claim_b = Claim(
            "claim-b",
            "event-2",
            "reported_strength",
            1000,
            "estimate",
            provenance=(source_locator(),),
            evidence_ids=("evidence-b",),
        )
        link = EvidenceLink(
            "evidence-b",
            "claim-b",
            source_locator(),
            "supports",
            "family-a",
        )
        decision = Adjudication(
            "decision-a",
            "claim-a",
            "reviewer-a",
            "needs_more_evidence",
            "A source for another assertion was considered.",
            "1.0",
            evidence_ids_considered=("evidence-b",),
        )
        with self.assertRaisesRegex(ValueError, "for claim claim-b, not claim-a"):
            build_review_packet(
                [{"id": "event-1", "name": "Event", "claim_ids": ["claim-a"]}],
                [claim_a, claim_b],
                [decision],
                evidence_links=[link],
                include_prior_decisions=True,
            )

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

    def test_prior_decision_rationale_rejects_non_numeric_model_references(self):
        evidence_claim = Claim(
            "claim-a",
            "event-1",
            "winner",
            "a",
            "categorical",
            provenance=(source_locator(),),
        )
        for rationale in (
            "Accepted because the Elo ranking was higher.",
            "The rating rank favored this side.",
            "The model rating favored this side.",
            "Elo score: 1700",
            "The Elo model placed side A first.",
            "Rankings were higher.",
            "Ratings favored side A.",
            "K-factor was 32.",
            "The model's score favored this side.",
            "The model-derived score favored this side.",
            "The model_score favored this side.",
            "The model placed this side first.",
            "ratings were 1700 and 1800",
            "deltas were 12.5",
            "Elo stood at 1700",
            "Elo equals 1700",
        ):
            leaked = Adjudication(
                "decision-a",
                "claim-a",
                "reviewer-a",
                "accepted",
                rationale,
                "1.0",
            )
            with self.subTest(rationale=rationale):
                with self.assertRaises(ValueError):
                    build_review_packet(
                        [{"id": "event-1", "name": "Event", "claim_ids": ["claim-a"]}],
                        [evidence_claim],
                        [leaked],
                        include_prior_decisions=True,
                    )

        ordinary = Adjudication(
            "decision-history",
            "claim-a",
            "reviewer-a",
            "accepted",
            "The cited dispatch and roster support the asserted participant.",
            "1.0",
        )
        packet = build_review_packet(
            [{"id": "event-1", "name": "Event"}],
            [evidence_claim],
            [ordinary],
            include_prior_decisions=True,
        )
        self.assertEqual(packet["adjudications"][0]["id"], "decision-history")

        historical_rationale = Adjudication(
            "decision-historical-rank",
            "claim-a",
            "reviewer-a",
            "accepted",
            "The commander rank was captain and the ship rating was third rate.",
            "1.0",
        )
        build_review_packet(
            [{"id": "event-1", "name": "Event"}],
            [evidence_claim],
            [historical_rationale],
            include_prior_decisions=True,
        )

    def test_prior_decision_validation_is_scoped_and_ordered(self):
        selected = Claim(
            "claim-a", "event-a", "winner", "a", "categorical",
            provenance=(source_locator(),),
        )
        unrelated = Claim(
            "claim-b", "event-b", "winner", "b", "categorical",
            provenance=(source_locator(),),
        )
        decisions = [
            Adjudication(
                "decision-a", "claim-a", "reviewer-a", "accepted",
                "The cited dispatch supports the assertion.", "1.0",
            ),
            Adjudication(
                "decision-b", "claim-b", "reviewer-b", "accepted",
                "The rating is 1900.", "1.0",
            ),
        ]
        packet = build_review_packet(
            [
                {"id": "event-a", "name": "A"},
                {"id": "event-b", "name": "B"},
            ],
            [selected, unrelated],
            decisions,
            event_ids=["event-a"],
            include_prior_decisions=True,
        )
        self.assertEqual(
            [item["id"] for item in packet["adjudications"]], ["decision-a"]
        )
        extensible_code = Adjudication(
            "decision-code",
            "claim-a",
            "elo-reviewer",
            "rank-1-pending",
            "The cited dispatch requires another review pass.",
            "rating-codebook-v1",
            reviewed_at="2026-07-14T00:00:00Z",
        )
        coded_packet = build_review_packet(
            [{"id": "event-a", "name": "A"}],
            [selected],
            [extensible_code],
            include_prior_decisions=True,
        )
        self.assertEqual(
            coded_packet["adjudications"][0]["decision"], "rank-1-pending"
        )
        with self.assertRaises(TypeError):
            build_review_packet(
                [{"id": "event-a", "name": "A"}],
                [selected],
                {decisions[0]},
                include_prior_decisions=True,
            )

    def test_include_prior_decisions_requires_boolean(self):
        for invalid in (None, 0, 1, "false", [], {}):
            with self.subTest(value=invalid), self.assertRaises(TypeError):
                build_review_packet(
                    [{"id": "event-1", "name": "Event"}],
                    [],
                    include_prior_decisions=invalid,
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

    def test_event_filter_keeps_hierarchy_external_without_expanding_scope(self):
        events = [
            {
                "id": "event-parent",
                "name": "Parent",
                "child_event_ids": ["event-child"],
                "claim_ids": ["claim-parent"],
            },
            {
                "id": "event-child",
                "name": "Child",
                "parent_event_id": "event-parent",
                "child_event_ids": ["event-grandchild"],
                "claim_ids": ["claim-child"],
            },
            {
                "id": "event-grandchild",
                "name": "Grandchild",
                "parent_event_ids": ["event-child"],
                "claim_ids": ["claim-grandchild"],
            },
        ]
        claims = [
            Claim(
                f"claim-{name}",
                f"event-{name}",
                "historical_context",
                name,
                "categorical",
                provenance=(source_locator(),),
            )
            for name in ("parent", "child", "grandchild")
        ]
        packet = build_review_packet(events, claims, event_ids=["event-child"])
        self.assertEqual(
            [item["id"] for item in packet["events"]],
            ["event-child"],
        )
        self.assertEqual(
            [item["id"] for item in packet["claims"]],
            ["claim-child"],
        )
        self.assertEqual(
            packet["external_event_ids"],
            ["event-grandchild", "event-parent"],
        )

        missing_parent = build_review_packet(
            [
                {
                    "id": "event-child",
                    "name": "Child",
                    "parent_event_id": "missing-parent",
                }
            ],
            [],
            event_ids=["event-child"],
        )
        self.assertEqual(missing_parent["external_event_ids"], ["missing-parent"])
        self.assertNotIn("hierarchy_closed", missing_parent)

        reverse_child = build_review_packet(
            [
                {"id": "parent", "name": "Parent"},
                {"id": "child", "name": "Child", "parent_event_id": "parent"},
            ],
            [],
            event_ids=["parent"],
        )
        self.assertEqual(reverse_child["external_event_ids"], ["child"])
        reverse_parent = build_review_packet(
            [
                {"id": "parent", "name": "Parent", "child_event_ids": ["child"]},
                {"id": "child", "name": "Child"},
            ],
            [],
            event_ids=["child"],
        )
        self.assertEqual(reverse_parent["external_event_ids"], ["parent"])

    def test_packet_rejects_internal_hierarchy_inconsistency(self):
        for link in (
            {"parent_event_id": "event-e"},
            {"parent_event_ids": ["event-e"]},
            {"child_event_ids": ["event-e"]},
        ):
            with self.subTest(link=link), self.assertRaises(ValueError):
                build_review_packet(
                    [{"id": "event-e", "name": "E", **link}], []
                )

        with self.assertRaisesRegex(ValueError, "hierarchy cycle"):
            build_review_packet(
                [
                    {"id": "event-a", "name": "A", "child_event_ids": ["event-b"]},
                    {"id": "event-b", "name": "B", "child_event_ids": ["event-a"]},
                ],
                [],
            )

        with self.assertRaisesRegex(ValueError, "disjoint date intervals"):
            build_review_packet(
                [
                    {
                        "id": "event-parent",
                        "name": "Parent",
                        "child_event_ids": ["event-child"],
                        "date_interval": {"start": 1900, "end": 1901},
                    },
                    {
                        "id": "event-child",
                        "name": "Child",
                        "parent_event_id": "event-parent",
                        "date_interval": {"start": 2000, "end": 2001},
                    },
                ],
                [],
            )

    def test_packet_canonicalizes_compatibility_dates_and_checks_episodes(self):
        for interval in (
            {"start_best": 1914, "end_best": 1918, "precision": "year"},
            {"start": 1914, "end": 1918},
        ):
            packet = build_review_packet(
                [{"id": "event-1", "name": "Event", "date_interval": interval}],
                [],
            )
            canonical = packet["events"][0]["date_interval"]
            self.assertEqual(canonical["start"]["best"], 1914)
            self.assertEqual(canonical["end"]["best"], 1918)
            self.assertEqual(set(canonical), {"start", "end"})

        legacy = build_review_packet(
            [{"id": "event-legacy", "name": "Legacy", "year": 1914, "end_year": 1918}],
            [],
        )
        self.assertEqual(
            legacy["events"][0]["date_interval"]["start"]["precision"],
            "year",
        )
        self.assertEqual(
            legacy["events"][0]["date_interval"]["end"]["best"],
            1918,
        )

        with self.assertRaisesRegex(ValueError, "does not overlap event"):
            build_review_packet(
                [
                    {
                        "id": "event-episode",
                        "name": "Episode event",
                        "date_interval": {"start": 1914, "end": 1918},
                        "participation_episodes": [
                            {
                                "id": "episode-1",
                                "entity_id": "entity-a",
                                "side": "a",
                                "role": "primary",
                                "entry": 2000,
                                "exit": 2001,
                            }
                        ],
                    }
                ],
                [],
            )

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

    def test_packet_refuses_structured_model_metric_labels(self):
        payloads = (
            "Elo is 1700",
            "Elo 1700",
            "Elo was 1700",
            "Elo favoured side A",
            "Elo score: 1700",
            "Elo points: 1700",
            "The rating is 1900",
            "The rating was 1900",
            "The rank was 1",
            "The model assigned this side a score of 0.8.",
            "The model placed this side first.",
            "commander rank was captain; rank: 1",
            "ship rating was third; rating: 1700",
            {"ranking": 1},
            {"metric": "rating", "value": 1700},
            {"metric_name": "elo", "metric_value": 1700},
            {"name": "rating", "value": 1700},
            {"metric": "ranking", "value": 1},
            ["elo", 1700],
            ["rank", "second"],
            ["rank", {"position": "second"}],
            {"kind": "model effect", "value": 0.25},
            {"name": "rating", "value": "1700"},
            ["elo", "1700"],
            {"metric": "ranking", "value": "1"},
            {"note": "leaderboard rank: 2"},
            [{"label": "elo"}, {"value": 1700}],
            {"model": {"score": 0.8}},
            {"model": {"result": {"score": 0.8}}},
            {"model": {"prediction": 0.7}},
            {"method": {"name": "model"}, "result": {"value": 0.9}},
            {"entity_id": {"elo": 2000}},
            {"source_id": [{"rating": 1900}]},
            {"claim_id": {"model_output": 0.8}},
            {"namespace": "model", "metric": "score", "value": 0.8},
            {"metadata": {"label": "rating"}, "value": "1e3"},
            {"ELOScore": 1700},
            {"leaderBoard": [1, 2]},
            {"expected_score": 0.75},
            {"top_10_probability": 0.2},
            {"rating": True},
            {"name": "rating", "value": "1,700"},
            {"name": "rating", "value": "NaN"},
            {"name": "rating", "value": "Infinity"},
            ["elo", [[[[[[1700]]]]]]],
            ["elo", *(["x"] * 128), 1700],
        )
        for index, payload in enumerate(payloads):
            malicious = Claim(
                f"claim-metric-{index}",
                "event-1",
                "historical_context",
                payload,
                None,
                provenance=(source_locator(),),
            )
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    build_review_packet(
                        [{"id": "event-1", "name": "Event"}], [malicious]
                    )

        historical_claims = [
            Claim(
                "claim-command-rank",
                "event-1",
                "commander_rank",
                {
                    "commander_rank": "captain",
                    "description": "commander rank was captain",
                    "seniority_order": 1,
                },
                "named rank",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-military-rank",
                "event-1",
                "military_rank",
                {"rank": "captain"},
                "named rank",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-river-delta",
                "event-1",
                "river_delta",
                {
                    "kind": "river delta",
                    "description": "river delta",
                    "charted_year": 1914,
                },
                "named geography",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-officer-rank",
                "event-1",
                "officer_rank",
                {"rank": "captain"},
                "named rank",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-naval-rating",
                "event-1",
                "naval_rating",
                {"rating": "third rate"},
                "naval classification",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-ship-rating",
                "event-1",
                "ship_rating",
                {
                    "kind": "ship rating",
                    "class_number": "3",
                    "description": "ship/naval rating of 3",
                },
                "naval classification",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-sibling-rank",
                "event-1",
                "historical_context",
                {"rank": "captain", "commander": "John Smith", "year": 1914},
                "named rank",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-sibling-rating",
                "event-1",
                "historical_context",
                {"rating": "third", "ship": "HMS Victory", "guns": 104},
                "naval classification",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-sibling-delta",
                "event-1",
                "historical_context",
                {"delta": "Nile", "feature_type": "river", "area_km2": 24000},
                "named geography",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-kind-rank",
                "event-1",
                "historical_context",
                {"kind": "commander rank", "label": "rank", "year": 1914},
                "named rank",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-kind-delta",
                "event-1",
                "historical_context",
                {"kind": "river delta", "measure": "delta", "charted_year": 1914},
                "named geography",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-location-delta",
                "event-1",
                "battle_location",
                {"region": "Nile Delta", "year": 1914},
                "named geography",
                provenance=(source_locator(),),
            ),
            Claim(
                "claim-rifle-model",
                "event-1",
                "equipment",
                {"model": "M1 Garand", "caliber": ".30-06"},
                "model designation",
                provenance=(source_locator(),),
            ),
        ]
        packet = build_review_packet(
            [{"id": "event-1", "name": "Event"}], historical_claims
        )
        self.assertEqual(
            [item["id"] for item in packet["claims"]],
            [
                "claim-command-rank",
                "claim-kind-delta",
                "claim-kind-rank",
                "claim-location-delta",
                "claim-military-rank",
                "claim-naval-rating",
                "claim-officer-rank",
                "claim-rifle-model",
                "claim-river-delta",
                "claim-ship-rating",
                "claim-sibling-delta",
                "claim-sibling-rank",
                "claim-sibling-rating",
            ],
        )

        for rank_title in (
            "first lieutenant",
            "second lieutenant",
            "first sergeant",
            "third officer",
        ):
            historical_rank = Claim(
                f"claim-title-{rank_title.replace(' ', '-')}",
                "event-1",
                "military_rank",
                {"rank": rank_title},
                "named rank",
                provenance=(source_locator(),),
            )
            with self.subTest(rank_title=rank_title):
                build_review_packet(
                    [{"id": "event-1", "name": "Event"}], [historical_rank]
                )

        for rank_value in (1, "1", "1st", "higher"):
            numeric_rank = Claim(
                f"claim-numeric-rank-{rank_value}",
                "event-1",
                "military_rank",
                {"rank": rank_value},
                "ordinal rank",
                provenance=(source_locator(),),
            )
            with self.subTest(rank_value=rank_value):
                with self.assertRaises(ValueError):
                    build_review_packet(
                        [{"id": "event-1", "name": "Event"}], [numeric_rank]
                    )

        for namespace in ("elo", "leaderboard", "model"):
            namespaced_rank = Claim(
                f"claim-namespaced-rank-{namespace}",
                "event-1",
                "military_rank",
                {"rank": "captain", "namespace": namespace},
                "named rank",
                provenance=(source_locator(),),
            )
            with self.subTest(namespace=namespace):
                with self.assertRaises(ValueError):
                    build_review_packet(
                        [{"id": "event-1", "name": "Event"}], [namespaced_rank]
                    )

    def test_packet_refuses_model_predicates_and_compound_output_keys(self):
        event = [{"id": "event-1", "name": "Event"}]
        for predicate in (
            "rating",
            "elo",
            "rank",
            "delta",
            "median_rank",
            "elo_rating",
            "leaderboard_rank",
            "rating_delta",
            "operational_rating",
            "model_prediction",
            "elorating",
            "eloscore",
            "modelrating",
            "leaderboardrank",
            "modelprediction",
        ):
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
            "elo_rating",
            "leaderboard_rank",
            "rating_delta",
            "tactical_rating",
            "ELOScore",
            "ELORating",
            "ELORank",
            "E.L.O.",
            "e_l_o",
            "e-l-o",
            "leaderBoard",
            "leader_board",
            "leader-board",
            "ratings",
            "rankings",
            "ranks",
            "leaderboards",
            "entityRatings",
            "expectedScore",
            "top_10_probability",
            "win_probability",
            "KFactor",
            "model_prediction",
            "elorating",
            "eloscore",
            "modelrating",
            "leaderboardrank",
            "modelprediction",
        ):
            malicious = Claim(
                f"claim-key-{key}",
                "event-1",
                "historical_context",
                {key: 1700},
                None,
                provenance=(source_locator(),),
            )
            with self.subTest(key=key), self.assertRaises(ValueError):
                build_review_packet(event, [malicious])

        for allowed_predicate in ("nile_delta", "danube_delta"):
            allowed = Claim(
                f"claim-{allowed_predicate}",
                "event-1",
                allowed_predicate,
                {"year": 1914},
                "named geography",
                provenance=(source_locator(),),
            )
            build_review_packet(event, [allowed])

    def test_claim_value_and_precision_are_scanned_as_one_evidence_payload(self):
        for value, precision in (
            (1700, "Elo"),
            ("Elo", 1700),
            (1700, {"label": "rating"}),
            ({"label": "Elo score"}, "1700"),
        ):
            leaked = Claim(
                "claim-combined",
                "event-1",
                "historical_context",
                value,
                precision,
                provenance=(source_locator(),),
            )
            with self.subTest(value=value, precision=precision), self.assertRaises(
                ValueError
            ):
                build_review_packet(
                    [{"id": "event-1", "name": "Event"}], [leaked]
                )

    def test_claim_notes_and_human_citations_are_scanned_without_id_pairing(self):
        note_leak = Claim(
            "claim-note",
            "event-1",
            "historical_context",
            "ordinary evidence",
            "quoted synthesis",
            provenance=(source_locator(),),
            note="Elo 1700",
        )
        citation_locator = SourceLocator(
            source_id="source-a",
            edition="v1",
            page=10,
            checksum=CHECKSUM,
            language="en",
            source_family="family-a",
            creator="Source Author",
            citation="The Elo rating was 1700.",
        )
        citation_leak = Claim(
            "claim-citation",
            "event-1",
            "historical_context",
            "ordinary evidence",
            "quoted synthesis",
            provenance=(citation_locator,),
        )
        for leaked in (note_leak, citation_leak):
            with self.subTest(claim=leaked.id), self.assertRaises(ValueError):
                build_review_packet(
                    [{"id": "event-1", "name": "Event"}], [leaked]
                )

        bibliographic_locator = SourceLocator(
            source_id="source-a",
            edition="elo-rating-edition-1",
            page=10,
            checksum=CHECKSUM,
            language="en",
            source_family="family-a",
            creator="Arpad Elo",
            citation="Biographical reference edition.",
        )
        bibliographic = Claim(
            "claim-bibliographic",
            "event-1",
            "authorship",
            "named creator",
            "bibliographic",
            provenance=(bibliographic_locator,),
        )
        build_review_packet(
            [{"id": "event-1", "name": "Event"}], [bibliographic]
        )

    def test_historical_context_is_invariant_to_claim_id_and_subject(self):
        historical_values = (
            ({"rating": "third", "ship": "HMS Victory", "guns": 104}, "naval classification"),
            ({"delta": "Nile", "feature_type": "river", "area_km2": 24000}, "named geography"),
        )
        for index, (value, precision) in enumerate(historical_values):
            for claim_id, subject in (
                (f"c-{index}", "event-1"),
                (f"ship-rating-river-delta-{index}", "ship-rating-river-delta"),
            ):
                with self.subTest(value=value, claim_id=claim_id):
                    build_review_packet(
                        [{"id": "event-1", "name": "Event", "claim_ids": [claim_id]}],
                        [
                            Claim(
                                claim_id,
                                subject,
                                "historical_context",
                                value,
                                precision,
                                provenance=(source_locator(),),
                            )
                        ],
                    )

        for claim_id in ("c", "ship-rating-river-delta"):
            for value in ({"rating": "third"}, {"delta": "positive"}):
                with self.subTest(claim_id=claim_id, value=value), self.assertRaises(
                    ValueError
                ):
                    build_review_packet(
                        [{"id": "event-1", "name": "Event"}],
                        [
                            Claim(
                                claim_id,
                                "event-1",
                                "historical_context",
                                value,
                                "reported wording",
                                provenance=(source_locator(),),
                            )
                        ],
                    )

        identity_invariant = Claim(
            "opaque-claim",
            "event-1",
            "military_rank",
            {
                "entity_id": "elo-rating-rank-delta",
                "rank": "captain",
                "commander": "John Smith",
                "year": 1914,
            },
            "named rank",
            provenance=(source_locator(),),
        )
        build_review_packet(
            [{"id": "event-1", "name": "Event"}], [identity_invariant]
        )

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

    def test_packet_closes_claim_groups_and_their_recursive_evidence(self):
        selected = Claim(
            "claim-a",
            "episode-1",
            "entry_date",
            "1914-08-01",
            "day",
            provenance=(source_locator(),),
            claim_group_id="group-g",
            exclusive=True,
        )
        group_peer = Claim(
            "claim-b",
            "event-elsewhere",
            "commander",
            "person-b",
            "named_person",
            provenance=(source_locator(),),
            contradicts=("claim-c",),
            claim_group_id="group-g",
            exclusive=True,
            evidence_ids=("evidence-b",),
        )
        contradicted = Claim(
            "claim-c",
            "archive-series",
            "authorship",
            "person-c",
            "named_person",
            provenance=(source_locator(),),
            evidence_ids=("evidence-c",),
        )
        links = [
            EvidenceLink(
                "evidence-b",
                "claim-b",
                source_locator(),
                "supports",
                "family-a",
            ),
            EvidenceLink(
                "evidence-c",
                "claim-c",
                source_locator(),
                "contradicts",
                "family-a",
            ),
        ]
        packet = build_review_packet(
            [{"id": "event-1", "name": "Event", "claim_ids": ["claim-a"]}],
            [selected, group_peer, contradicted],
            evidence_links=links,
        )
        self.assertEqual(
            [item["id"] for item in packet["claims"]],
            ["claim-a", "claim-b", "claim-c"],
        )
        self.assertEqual(
            [item["id"] for item in packet["evidence_links"]],
            ["evidence-b", "evidence-c"],
        )

    def test_packet_rejects_self_contradiction_and_inconsistent_exclusive_group(self):
        self_contradicting = Claim(
            "claim-self",
            "event-1",
            "winner",
            "a",
            "categorical",
            provenance=(source_locator(),),
            contradicts=("claim-self",),
        )
        with self.assertRaisesRegex(ValueError, "cannot contradict itself"):
            build_review_packet(
                [{"id": "event-1", "name": "Event"}], [self_contradicting]
            )

        claims = [
            Claim(
                "claim-a", "event-1", "winner", "a", "categorical",
                provenance=(source_locator(),), claim_group_id="group", exclusive=True,
            ),
            Claim(
                "claim-b", "elsewhere", "winner", "b", "categorical",
                provenance=(source_locator(),), claim_group_id="group", exclusive=False,
            ),
        ]
        with self.assertRaisesRegex(ValueError, "inconsistent exclusive"):
            build_review_packet(
                [{"id": "event-1", "name": "Event", "claim_ids": ["claim-a"]}],
                claims,
            )

    def test_empty_event_selection_selects_nothing(self):
        packet = build_review_packet(self._events(), self._claims(), event_ids=[])
        self.assertEqual(packet["events"], [])
        self.assertEqual(packet["claims"], [])

    def test_event_selection_requires_nonblank_string_ids(self):
        for malformed in (True, 7, {}, [" "] , [False], [["event-1"]]):
            with self.subTest(event_ids=malformed):
                with self.assertRaises(ValueError):
                    build_review_packet(self._events(), self._claims(), event_ids=malformed)

    def test_direct_claim_and_link_objects_are_validated_before_emission(self):
        invalid_status = Claim(
            "claim-status",
            "event-1",
            "winner",
            "a",
            "categorical",
            status="accepted",
            provenance=(source_locator(),),
        )
        evidence_free = Claim(
            "claim-empty",
            "event-1",
            "winner",
            "a",
            "categorical",
        )
        for invalid_claim in (invalid_status, evidence_free):
            with self.subTest(claim=invalid_claim.id):
                with self.assertRaises(ValueError):
                    build_review_packet(
                        [{"id": "event-1", "name": "Event"}], [invalid_claim]
                    )

        linked_claim = Claim(
            "claim-link",
            "event-1",
            "winner",
            "a",
            "categorical",
            provenance=(source_locator(),),
            evidence_ids=("evidence-link",),
        )
        bad_locator = SourceLocator(
            source_id="source-a",
            edition="v1",
            url="https://example.test/a b",
            checksum=CHECKSUM,
            language="en",
            source_family="family-a",
        )
        control_locator = SourceLocator(
            source_id="source-a",
            edition="v1",
            url="https://example.test/a\x00b",
            checksum=CHECKSUM,
            language="en",
            source_family="family-a",
        )
        invalid_links = (
            EvidenceLink(
                "evidence-link",
                "claim-link",
                source_locator(),
                "votes",
                "family-a",
            ),
            EvidenceLink(
                "evidence-link",
                "claim-link",
                bad_locator,
                "supports",
                "family-a",
            ),
            EvidenceLink(
                "evidence-link",
                "claim-link",
                control_locator,
                "supports",
                "family-a",
            ),
        )
        for invalid_link in invalid_links:
            with self.subTest(relationship=invalid_link.relationship, url=invalid_link.locator.url):
                with self.assertRaises(ValueError):
                    build_review_packet(
                        [{"id": "event-1", "name": "Event"}],
                        [linked_claim],
                        evidence_links=[invalid_link],
                    )

    def test_event_evidence_view_rejects_invalid_canonical_fields(self):
        invalid_events = (
            {
                "id": "event-date",
                "name": "Date",
                "date_interval": {
                    "start": {"low": 0, "best": 0, "high": 0, "precision": "year"},
                    "end": {"low": 1, "best": 1, "high": 1, "precision": "year"},
                },
            },
            {
                "id": "event-geometry",
                "name": "Geometry",
                "geometry": {"type": "NotGeoJSON", "coordinates": [1, 2]},
            },
            {
                "id": "event-point",
                "name": "Point",
                "geometry": {"type": "Point", "coordinates": [[1, 2], [3, 4]]},
            },
            {
                "id": "event-episode",
                "name": "Episode",
                "participation_episodes": [
                    {
                        "id": "episode-1",
                        "entity_id": "entity-a",
                        "side": "a",
                        "role": "primary",
                        "contribution": 2.0,
                    }
                ],
            },
            {
                "id": "event-empty-episode",
                "name": "Empty",
                "participation_episodes": [{}],
            },
            {"id": "event-type", "name": "Metadata", "event_type": 123},
            {"id": "event-layer", "name": "Metadata", "layer": 123},
            {"id": "event-domain", "name": "Metadata", "domain": 123},
            {"id": "event-region", "name": "Metadata", "region": 123},
            {"id": "event-status", "name": "Metadata", "status": 123},
        )
        for invalid_event in invalid_events:
            with self.subTest(event_id=invalid_event["id"]):
                with self.assertRaises((TypeError, ValueError)):
                    build_review_packet([invalid_event], [])

    def test_packet_enforces_geojson_coordinate_shapes(self):
        invalid_geometries = (
            {"type": "Point", "coordinates": [1, 2, [3]]},
            {"type": "MultiPoint", "coordinates": [1, 2]},
            {"type": "LineString", "coordinates": []},
            {"type": "LineString", "coordinates": [[1, 2]]},
            {"type": "Polygon", "coordinates": []},
            {"type": "Polygon", "coordinates": [1, 2]},
            {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1]]],
            },
            {"type": "MultiLineString", "coordinates": [1, 2]},
            {"type": "MultiPolygon", "coordinates": [1, 2]},
            {
                "type": "GeometryCollection",
                "geometries": [{"type": "Point", "coordinates": [1, 2, [3]]}],
            },
        )
        for index, geometry in enumerate(invalid_geometries):
            with self.subTest(geometry=geometry), self.assertRaises(ValueError):
                build_review_packet(
                    [{"id": f"bad-{index}", "name": "Bad", "geometry": geometry}],
                    [],
                )

        valid_geometries = (
            {"type": "Point", "coordinates": [1, 2, 3]},
            {"type": "MultiPoint", "coordinates": [[1, 2], [3, 4]]},
            {"type": "LineString", "coordinates": [[1, 2], [3, 4]]},
            {
                "type": "MultiLineString",
                "coordinates": [[[1, 2], [3, 4]]],
            },
            {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]],
            },
            {
                "type": "MultiPolygon",
                "coordinates": [[[[0, 0], [1, 0], [1, 1], [0, 0]]]],
            },
            {
                "type": "GeometryCollection",
                "geometries": [{"type": "Point", "coordinates": [1, 2]}],
            },
        )
        for index, geometry in enumerate(valid_geometries):
            with self.subTest(geometry=geometry):
                build_review_packet(
                    [{"id": f"valid-{index}", "name": "Valid", "geometry": geometry}],
                    [],
                )

    def test_legacy_participants_receive_deterministic_review_identity(self):
        packet = build_review_packet(
            [
                {
                    "id": "event-1",
                    "name": "Event",
                    "participants": [{"entity_id": "entity-a", "side": "a"}],
                }
            ],
            [],
        )
        episode = packet["events"][0]["participation_episodes"][0]
        self.assertEqual(
            {key: value for key, value in episode.items() if key != "id"},
            {"entity_id": "entity-a", "side": "a", "role": "unknown"},
        )
        self.assertRegex(
            episode["id"],
            r"^event-1:participant:[0-9a-f]{64}:1$",
        )

    def test_event_and_episode_aliases_normalize_before_packet_identity(self):
        canonical_entry = {
            "low": 1914,
            "best": 1914,
            "high": 1914,
            "precision": "exact",
        }
        packets = [
            build_review_packet(
                [
                    {
                        "event_id": "event-1",
                        "canonical_name": "Event",
                        "participants": [
                            {"entity_id": "entity-a", "side": "a", field: value}
                        ],
                    }
                ],
                [],
            )
            for field, value in (
                ("entry", 1914),
                ("entry", canonical_entry),
                ("entry_date", 1914),
            )
        ]
        episode_ids = {
            packet["events"][0]["participation_episodes"][0]["id"]
            for packet in packets
        }
        self.assertEqual(len(episode_ids), 1)
        self.assertEqual(packets[0]["events"][0]["id"], "event-1")
        self.assertEqual(packets[0]["events"][0]["name"], "Event")

        explicit = build_review_packet(
            [
                {
                    "id": "event-1",
                    "name": "Event",
                    "participation_episodes": [
                        {
                            "episode_id": "episode-alias",
                            "entity_id": "entity-a",
                            "side": "a",
                            "role": "primary",
                        }
                    ],
                }
            ],
            [],
        )
        self.assertEqual(
            explicit["events"][0]["participation_episodes"][0]["id"],
            "episode-alias",
        )

        for malformed in (
            {"id": "event-1", "event_id": "other", "name": "Event"},
            {"id": "event-1", "name": "Event", "canonical_name": "Other"},
            {
                "id": "event-1",
                "name": "Event",
                "participants": [
                    {
                        "entity_id": "entity-a",
                        "side": "a",
                        "entry": 1914,
                        "entry_date": 1914,
                    }
                ],
            },
        ):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                build_review_packet([malformed], [])

        legacy_event = Event.from_dict(
            {
                "id": "legacy-model-event",
                "name": "Legacy model event",
                "year": 1914,
                "event_type": "engagement",
                "participants": [
                    {"entity_id": "a", "side": "one"},
                    {"entity_id": "b", "side": "two"},
                ],
                "source_ids": [],
                "geometry": {"type": "Point", "coordinates": [1, 2]},
            }
        )
        legacy_packet = build_review_packet([legacy_event], [])
        self.assertEqual(
            legacy_packet["events"][0]["geometry"],
            {"type": "Point", "coordinates": [1, 2]},
        )

    def test_legacy_participant_synthetic_ids_are_input_order_independent(self):
        participants = [
            {"entity_id": "entity-a", "side": "a", "role": "primary"},
            {"entity_id": "entity-b", "side": "b", "role": "supporting"},
            {"entity_id": "entity-a", "side": "a", "role": "primary"},
        ]
        first = build_review_packet(
            [{"id": "event-1", "name": "Event", "participants": participants}],
            [],
        )
        second = build_review_packet(
            [
                {
                    "id": "event-1",
                    "name": "Event",
                    "participants": list(reversed(participants)),
                }
            ],
            [],
        )
        self.assertEqual(first, second)
        self.assertEqual(
            json.dumps(first, sort_keys=True, separators=(",", ":")),
            json.dumps(second, sort_keys=True, separators=(",", ":")),
        )
        episode_ids = [
            item["id"] for item in first["events"][0]["participation_episodes"]
        ]
        self.assertEqual(len(episode_ids), len(set(episode_ids)))
        self.assertTrue(any(item.endswith(":2") for item in episode_ids))

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
                "expected_strength": 1000,
                "actual_strength": 900,
            },
            precision="quoted_synthesis",
            provenance=(source_locator(),),
        )
        packet = build_review_packet([{"id": "event-1", "name": "Event"}], [historical])
        self.assertEqual(packet["claims"][0]["value"]["expected"], "relief before winter")
        numeric = Claim(
            "claim-numeric-expectation",
            "event-1",
            "reported_strength",
            {"expected": 1000, "actual": 900},
            "reported figures",
            provenance=(source_locator(),),
        )
        numeric_packet = build_review_packet(
            [{"id": "event-1", "name": "Event"}], [numeric]
        )
        self.assertEqual(
            numeric_packet["claims"][0]["value"],
            {"actual": 900, "expected": 1000},
        )

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

    def test_review_packet_cli_rejects_malformed_selection_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            events = root / "events.json"
            claims = root / "claims.json"
            selection = root / "selection.json"
            output = root / "packet.json"
            events.write_text(json.dumps(self._events()), encoding="utf-8")
            claims.write_text(
                json.dumps([item.to_dict() for item in self._claims()]),
                encoding="utf-8",
            )
            selection.write_text(json.dumps({"records": [{"id": False}]}), encoding="utf-8")
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
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
