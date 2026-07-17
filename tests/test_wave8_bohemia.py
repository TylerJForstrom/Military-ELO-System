import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_bohemia as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_bohemia_"

OTTOKAR_HOST = "ottokar_ii_bohemian_royal_host_1260_1278"
BELA_COALITION = "bela_iv_hungarian_led_coalition_kressenbrunn_1260"
RUDOLF_COALITION = "rudolf_ladislaus_allied_host_marchfeld_1278"
BOHEMIAN_ESTATES = "bohemian_estates_revolt_forces_1618_1620"
BUQUOY_FORCE = "buquoy_imperial_army_zablati_1619"
IMPERIAL_LEAGUE = "imperial_catholic_league_army_white_mountain_1620"

EXPECTED_HASHES = {
    "hced-Kressenbrunn1260-1": (
        "8bf1d9b26f3835952a23dfc78f0e31666e52ce0348f08579c56e3d22b91989f2"
    ),
    "hced-Marchfeld1278-1": (
        "b252599622656fdbeeeede39402f849c566a0f62cd0f7b5f6c901e132032f4fb"
    ),
    "hced-Sablat1619-1": (
        "5336ea6198b45d7675cac966b3cbac6c93eebd31e97a3ed3f71fb7ff6a2cd403"
    ),
    "hced-White Mountain1620-1": (
        "f26b7b81236eae2a1399070e9f110767c7df6138e7b7b20a5447d22e6421e084"
    ),
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8BohemiaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "bohemia"
            or normalize_label(row.get("side_2_raw")) == "bohemia"
        ]

    def _installed(self):
        lane_entity_ids = {str(item["id"]) for item in lane.WAVE8_BOHEMIA_ENTITIES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane_source_ids = {str(item["id"]) for item in lane.WAVE8_BOHEMIA_SOURCES}
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_BOHEMIA_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_bohemia_entities(entities)
        lane.install_wave8_bohemia_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_bohemia_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_and_row_hashes_are_pinned(self) -> None:
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(set(by_id), set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_BOHEMIA_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            lane.WAVE8_BOHEMIA_EXPECTED_CANDIDATE_IDS,
            frozenset(EXPECTED_HASHES),
        )
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(by_id[candidate_id]),
                    expected_hash,
                )
                self.assertIs(by_id[candidate_id]["winner_loser_complete"], True)
                self.assertEqual(by_id[candidate_id]["massacre_raw"], "No")

    def test_queue_and_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_bohemia_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 4,
                "holds": 0,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
            },
        )
        historical_funnel = {
            "labels": [
                {
                    "candidate_ids": [],
                    "event_candidate_id_sha256": (
                        "74e0345fa1ff4b4929c547db72cdc8430464a4e91f7f0cc66dce1e90281c3650"
                    ),
                    "events_touched": 4,
                    "failure_cases": {"zero_time_valid_candidates": 4},
                    "label": "bohemia",
                    "sole_blocker_events": 3,
                }
            ]
        }
        self.assertEqual(
            lane.validate_wave8_bohemia_funnel(historical_funnel),
            {
                "events_touched": 4,
                "sole_blocker_events": 3,
                "zero_time_valid_candidates": 4,
            },
        )
        self.assertFalse(
            any(
                row.get("label") == "bohemia"
                for row in self.funnel.get("labels", [])
            ),
            "the completed Bohemia lane must not remain unresolved",
        )

    def test_all_four_rows_promote_without_invented_draws_or_reversals(self) -> None:
        self.assertEqual(lane.WAVE8_BOHEMIA_CONTRACT_IDS, set(EXPECTED_HASHES))
        self.assertFalse(lane.WAVE8_BOHEMIA_HOLDS)
        for contract in lane.WAVE8_BOHEMIA_CONTRACTS.values():
            self.assertEqual(contract["disposition"], "promote")
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_entities_are_exactly_bounded_and_have_no_generic_aliases(self) -> None:
        entities = {str(item["id"]): item for item in lane.WAVE8_BOHEMIA_ENTITIES}
        self.assertEqual(
            set(entities),
            {
                OTTOKAR_HOST,
                BELA_COALITION,
                RUDOLF_COALITION,
                BOHEMIAN_ESTATES,
                BUQUOY_FORCE,
                IMPERIAL_LEAGUE,
            },
        )
        expected_windows = {
            OTTOKAR_HOST: (1260, 1278),
            BELA_COALITION: (1260, 1260),
            RUDOLF_COALITION: (1278, 1278),
            BOHEMIAN_ESTATES: (1618, 1620),
            BUQUOY_FORCE: (1619, 1619),
            IMPERIAL_LEAGUE: (1620, 1620),
        }
        for entity_id, entity in entities.items():
            with self.subTest(entity_id=entity_id):
                self.assertEqual(
                    (entity["start_year"], entity["end_year"]),
                    expected_windows[entity_id],
                )
                self.assertEqual(entity["aliases"], [])
                self.assertIn("No generic Bohemia", entity["continuity_note"])
                Entity.from_dict(entity)

    def test_sources_parse_and_every_result_has_independent_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_BOHEMIA_SOURCES), 10)
        for source in lane.WAVE8_BOHEMIA_SOURCES:
            Source.from_dict(source)
        for candidate_id, contract in lane.WAVE8_BOHEMIA_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertEqual(
                    contract["outcome_source_family_ids"],
                    sorted(set(contract["outcome_source_family_ids"])),
                )
                self.assertLessEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )

    def test_promoted_events_have_exact_actors_and_tactical_results(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        expected = {
            "hced-Kressenbrunn1260-1": (
                "Battle of Kressenbrunn",
                {OTTOKAR_HOST},
                {BELA_COALITION},
            ),
            "hced-Marchfeld1278-1": (
                "Battle on the Marchfeld",
                {RUDOLF_COALITION},
                {OTTOKAR_HOST},
            ),
            "hced-Sablat1619-1": (
                "Battle of Záblatí",
                {BUQUOY_FORCE},
                {BOHEMIAN_ESTATES},
            ),
            "hced-White Mountain1620-1": (
                "Battle of White Mountain",
                {IMPERIAL_LEAGUE},
                {BOHEMIAN_ESTATES},
            ),
        }
        self.assertEqual(set(events), set(expected))
        for candidate_id, (name, winners, losers) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(event["name"], name)
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if item["termination"] == "engagement_victory"
                    },
                    winners,
                )
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if item["termination"] == "engagement_defeat"
                    },
                    losers,
                )
                Event.from_dict(event)

    def test_dates_and_war_types_are_explicit(self) -> None:
        expected = {
            "hced-Kressenbrunn1260-1": ("12 July 1260", "interstate"),
            "hced-Marchfeld1278-1": ("26 August 1278", "interstate"),
            "hced-Sablat1619-1": ("10 June 1619", "civil_war"),
            "hced-White Mountain1620-1": ("8 November 1620", "civil_war"),
        }
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        for candidate_id, (date_text, war_type) in expected.items():
            contract = lane.WAVE8_BOHEMIA_CONTRACTS[candidate_id]
            self.assertEqual(contract["canonical_event"]["date_text"], date_text)
            self.assertEqual(contract["canonical_event"]["date_precision"], "day")
            self.assertEqual(events[candidate_id]["date_precision"], "day")
            self.assertEqual(events[candidate_id]["war_type"], war_type)

    def test_points_are_withheld_but_reviewed_countries_are_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_BOHEMIA_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_BOHEMIA_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_BOHEMIA_COUNTRY_QUARANTINE_ADDITIONS)
        expected_countries = {
            "hced-Kressenbrunn1260-1": "Austria",
            "hced-Marchfeld1278-1": "Austria",
            "hced-Sablat1619-1": "Czechia",
            "hced-White Mountain1620-1": "Czechia",
        }
        for event in self._events():
            candidate_id = str(event["hced_candidate_id"])
            self.assertNotIn("geometry", event)
            self.assertEqual(
                event["modern_location_country"],
                expected_countries[candidate_id],
            )
            self.assertIn("location_provenance", event)

    def test_current_release_artifacts_include_the_lane_exactly_once(self) -> None:
        events = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_BOHEMIA_CONTRACT_IDS
        ]
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in events},
            lane.WAVE8_BOHEMIA_CONTRACT_IDS,
        )
        self.assertEqual(len(events), 4)
        self.assertTrue(
            all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in events)
        )
        expected_countries = {
            "hced-Kressenbrunn1260-1": "Austria",
            "hced-Marchfeld1278-1": "Austria",
            "hced-Sablat1619-1": "Czechia",
            "hced-White Mountain1620-1": "Czechia",
        }
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(
                event["modern_location_country"],
                expected_countries[str(event["hced_candidate_id"])],
            )
            Event.from_dict(event)

        entity_ids = {str(item["id"]) for item in lane.WAVE8_BOHEMIA_ENTITIES}
        release_entities = {str(item["id"]): item for item in self.release_entities}
        self.assertLessEqual(entity_ids, set(release_entities))
        self.assertTrue(
            all(not release_entities[entity_id]["aliases"] for entity_id in entity_ids)
        )
        registry_entities = {
            str(item["id"]): item for item in self.registry["entities"]
        }
        self.assertLessEqual(entity_ids, set(registry_entities))
        self.assertTrue(
            all(
                registry_entities[entity_id]["status"] == "rated"
                for entity_id in entity_ids
            )
        )

        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_bohemia_hced_events"], 4)
        self.assertEqual(
            promotion["wave8_bohemia_candidate_ids"],
            sorted(lane.WAVE8_BOHEMIA_CONTRACT_IDS),
        )
        self.assertEqual(promotion["wave8_bohemia_holds"], [])
        self.assertEqual(
            promotion["wave8_bohemia_final_audit_signature"],
            lane.WAVE8_BOHEMIA_FINAL_AUDIT_SIGNATURE,
        )

        coverage = self.registry["coverage"]
        self.assertEqual(coverage["candidate_keyed_wave8_bohemia_hced_events"], 4)
        self.assertEqual(coverage["rated_events"], len(self.release_events))
        self.assertEqual(coverage["registry_polities"], len(self.registry["entities"]))
        self.assertEqual(
            coverage["rated_entities"],
            len(
                {
                    participant["entity_id"]
                    for event in self.release_events
                    for participant in event["participants"]
                }
            ),
        )

    def test_duplicate_audit_is_zero_and_future_spelling_twins_fail_closed(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_bohemia_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )
        future = [
            *copy.deepcopy(self.iwbd_rows),
            {"candidate_id": "iwbd-future", "batname": "Bílá Hora", "batyear": 1620},
        ]
        with self.assertRaises(ValueError):
            lane.validate_wave8_bohemia_integration_dispositions(
                self.hced_rows,
                future,
                existing,
            )

    def test_queue_tampering_duplicates_and_massacre_drift_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        target = next(
            row
            for row in tampered
            if row.get("candidate_id") == "hced-Marchfeld1278-1"
        )
        target["winner_raw"] = "Bohemia"
        with self.assertRaises(ValueError):
            lane.validate_wave8_bohemia_queue_contracts(tampered)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(
            copy.deepcopy(
                next(
                    row
                    for row in duplicated
                    if row.get("candidate_id") == "hced-Sablat1619-1"
                )
            )
        )
        with self.assertRaises(ValueError):
            lane.validate_wave8_bohemia_queue_contracts(duplicated)

        massacre = copy.deepcopy(self.hced_rows)
        target = next(
            row
            for row in massacre
            if row.get("candidate_id") == "hced-White Mountain1620-1"
        )
        target["massacre_raw"] = "Massacre"
        with self.assertRaises(ValueError):
            lane.validate_wave8_bohemia_queue_contracts(massacre)

    def test_installers_and_candidate_collisions_fail_closed(self) -> None:
        entities, sources, existing = self._installed()
        lane.install_wave8_bohemia_entities(entities)
        lane.install_wave8_bohemia_sources(sources)
        events = lane.promote_wave8_bohemia_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaises(ValueError):
            lane.promote_wave8_bohemia_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

    def test_counts_cohorts_and_final_signature_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_bohemia_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 0,
                "new_entities": 6,
                "new_sources": 10,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_bohemia_cohort_counts(),
            {"bohemian_estates_revolt": 2, "ottokar_ii_royal_wars": 2},
        )
        self.assertEqual(
            lane.wave8_bohemia_audit_signature(),
            "903e280d26411c4605be5f97b1a42124ff98bec40184c5fa82334b1dee782813",
        )
        self.assertEqual(
            lane.wave8_bohemia_audit_signature(),
            lane.WAVE8_BOHEMIA_FINAL_AUDIT_SIGNATURE,
        )


if __name__ == "__main__":
    unittest.main()
