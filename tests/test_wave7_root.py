from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_root import (
    WAVE7_ROOT_CONTRACT_IDS,
    WAVE7_ROOT_ENTITIES,
    WAVE7_ROOT_ENTITY_IDS,
    WAVE7_ROOT_HOLD_IDS,
    WAVE7_ROOT_HOLDS,
    WAVE7_ROOT_OUTCOME_CORRECTION_IDS,
    WAVE7_ROOT_RESERVED_IDS,
    WAVE7_ROOT_SOURCE_IDS,
    WAVE7_ROOT_SOURCES,
    canonical_row_sha256,
    install_wave7_root_entities,
    install_wave7_root_sources,
    promote_wave7_root_contracts,
    validate_wave7_root_candidates,
    wave7_root_cohort_counts,
)


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "review" / "hced-candidates.jsonl"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


@unittest.skipUnless(QUEUE_PATH.is_file(), "locked HCED review queue is unavailable")
class Wave7RootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hced = _jsonl(QUEUE_PATH)
        cls.base_entities = {
            str(row["id"]): row
            for row in _json(ROOT / "data" / "release" / "entities.json")
        }
        cls.base_events = [
            event
            for event in _json(ROOT / "data" / "release" / "events.json")
            if event.get("hced_candidate_id") not in WAVE7_ROOT_CONTRACT_IDS
        ]

    def _promote(self):
        entities = copy.deepcopy(self.base_entities)
        install_wave7_root_entities(entities)
        events = promote_wave7_root_contracts(self.hced, entities, self.base_events)
        return entities, events

    def test_frozen_inventory_and_cohort_counts(self):
        self.assertEqual(len(WAVE7_ROOT_CONTRACT_IDS), 62)
        self.assertEqual(len(WAVE7_ROOT_HOLD_IDS), 4)
        self.assertEqual(len(WAVE7_ROOT_RESERVED_IDS), 66)
        self.assertTrue(WAVE7_ROOT_CONTRACT_IDS.isdisjoint(WAVE7_ROOT_HOLD_IDS))
        self.assertEqual(len(WAVE7_ROOT_ENTITY_IDS), 9)
        self.assertEqual(len(WAVE7_ROOT_SOURCE_IDS), 20)
        self.assertEqual(len(WAVE7_ROOT_OUTCOME_CORRECTION_IDS), 7)
        self.assertEqual(
            wave7_root_cohort_counts(),
            {
                "american_1775": 15,
                "biafra": 8,
                "hungarian_honved": 10,
                "murat_naples": 12,
                "red_sticks": 11,
                "vichy": 6,
            },
        )

    def test_entities_and_sources_are_bounded_and_parse(self):
        for raw in WAVE7_ROOT_ENTITIES:
            entity = Entity.from_dict(raw)
            self.assertEqual(entity.aliases, ())
            self.assertEqual(entity.predecessors, ())
            self.assertIn("No rating is inherited", entity.continuity_note)
            self.assertTrue(set(entity.source_ids) <= WAVE7_ROOT_SOURCE_IDS)
        for raw in WAVE7_ROOT_SOURCES:
            source = Source.from_dict(raw)
            self.assertTrue(source.url.startswith("https://"))
            self.assertTrue(source.source_family_id)
            self.assertIn("outcome_consistency_crosscheck", source.evidence_roles)
        source_by_id = {str(source["id"]): source for source in WAVE7_ROOT_SOURCES}
        for event_source_id in {
            "wave7_nps_revolution_timeline",
            "wave7_nigeria_civil_war_history",
            "wave7_nps_creek_war",
            "wave7_founders_emuckfaw",
            "wave7_hungary_military_museum",
        }:
            self.assertIn("outcome", source_by_id[event_source_id]["evidence_roles"])

    def test_installers_are_idempotent_and_reject_collisions(self):
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        install_wave7_root_entities(entities)
        install_wave7_root_sources(sources)
        expected_entities = copy.deepcopy(entities)
        expected_sources = copy.deepcopy(sources)
        install_wave7_root_entities(entities)
        install_wave7_root_sources(sources)
        self.assertEqual(entities, expected_entities)
        self.assertEqual(sources, expected_sources)

        entities[next(iter(WAVE7_ROOT_ENTITY_IDS))]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity ID collision"):
            install_wave7_root_entities(entities)
        sources[next(iter(WAVE7_ROOT_SOURCE_IDS))]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source ID collision"):
            install_wave7_root_sources(sources)

    def test_complete_queue_fingerprints_and_holds(self):
        validate_wave7_root_candidates(self.hced)
        rows = {str(row["candidate_id"]): row for row in self.hced}
        for candidate_id, hold in WAVE7_ROOT_HOLDS.items():
            self.assertEqual(
                canonical_row_sha256(rows[candidate_id]), hold["raw_sha256"]
            )
            self.assertTrue(hold["reason"])

        missing = [
            row
            for row in self.hced
            if row.get("candidate_id") != next(iter(WAVE7_ROOT_HOLD_IDS))
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave7_root_candidates(missing)

        tampered = copy.deepcopy(self.hced)
        target = next(
            row
            for row in tampered
            if row.get("candidate_id") in WAVE7_ROOT_CONTRACT_IDS
        )
        target["winner_raw"] = "tampered"
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            validate_wave7_root_candidates(tampered)

    def test_promoter_emits_exact_schema_valid_nonheld_events(self):
        _, events = self._promote()
        self.assertEqual(len(events), 62)
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in events},
            WAVE7_ROOT_CONTRACT_IDS,
        )
        self.assertFalse(
            {str(event["hced_candidate_id"]) for event in events} & WAVE7_ROOT_HOLD_IDS
        )
        self.assertEqual(len({event["id"] for event in events}), 62)
        self.assertEqual(len({event["canonical_event_key"] for event in events}), 62)
        for raw in events:
            Event.from_dict(raw)
            self.assertEqual(raw["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(raw["reviewed_granularity"], "engagement")
            self.assertTrue(raw["source_ids"])
            self.assertIn("hced_dataset", raw["source_ids"])

    def test_seven_historical_outcome_corrections_are_enforced(self):
        _, events = self._promote()
        corrected = {
            str(event["hced_candidate_id"]): event
            for event in events
            if event["historical_outcome_correction"]
        }
        self.assertEqual(set(corrected), WAVE7_ROOT_OUTCOME_CORRECTION_IDS)
        expected_victors = {
            "hced-Concord1775-1": {"american_revolutionary_forces_1775"},
            "hced-Onitsha1967-1": {"republic_biafra"},
            "hced-Buda1849-1": {"hungarian_honved_army_1848"},
            "hced-Pakozd1848-1": {"hungarian_honved_army_1848"},
        }
        for candidate_id, victors in expected_victors.items():
            actual = {
                str(participant["entity_id"])
                for participant in corrected[candidate_id]["participants"]
                if participant["termination"] == "engagement_victory"
            }
            self.assertEqual(actual, victors)
        for candidate_id in {
            "hced-Burnt Corn1813-1",
            "hced-Emuckfaw1814-1",
            "hced-Enotachopco1814-1",
        }:
            self.assertEqual(
                {
                    participant["termination"]
                    for participant in corrected[candidate_id]["participants"]
                },
                {"inconclusive_engagement"},
            )

    def test_existing_candidate_and_entity_window_fail_closed(self):
        entities = copy.deepcopy(self.base_entities)
        install_wave7_root_entities(entities)
        collision = {
            "name": "collision",
            "year": 1775,
            "hced_candidate_id": "hced-Concord1775-1",
        }
        with self.assertRaisesRegex(ValueError, "already promoted"):
            promote_wave7_root_contracts(self.hced, entities, [collision])

        entities["red_stick_creek_forces"]["start_year"] = 1814
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave7_root_contracts(self.hced, entities, self.base_events)


if __name__ == "__main__":
    unittest.main()
