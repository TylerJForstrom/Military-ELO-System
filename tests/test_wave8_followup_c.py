import copy
import json
import unittest
from pathlib import Path

from military_elo.promotion import wave8_followup_c as lane


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8FollowupCBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwd = _jsonl(ROOT / "data/review/iwd-1.21-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.wikidata = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        entity_ids = {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_C_ENTITIES}
        source_ids = {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_C_SOURCES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in entity_ids
        }
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_FOLLOWUP_C_CONTRACT_IDS
        ]
        lane.install_wave8_followup_c_entities(entities)
        lane.install_wave8_followup_c_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_followup_c_contracts(
            self.hced, entities, existing
        )

    def test_disjoint_combined_inventory_is_exact(self) -> None:
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_C_CONTRACT_IDS), 14)
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_C_RESERVED_IDS), 19)
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_C_HOLDS), 4)
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_C_TERMINAL_EXCLUSIONS), 1)
        self.assertEqual(
            lane.WAVE8_FOLLOWUP_C_RESERVED_IDS,
            lane.WAVE8_FOLLOWUP_C_CONTRACT_IDS
            | set(lane.WAVE8_FOLLOWUP_C_HOLDS)
            | set(lane.WAVE8_FOLLOWUP_C_TERMINAL_EXCLUSIONS),
        )

    def test_all_five_queue_validators_run_fail_closed(self) -> None:
        validation = lane.validate_wave8_followup_c_queue_contracts(self.hced)
        self.assertEqual(
            set(validation),
            {
                "bilbao",
                "georgian_uprising",
                "great_northern_exact",
                "polisario",
                "sertorian",
            },
        )
        self.assertEqual(
            sum(item["promotion_contracts"] for item in validation.values()),
            14,
        )
        self.assertEqual(
            sum(item["reviewed_hced_rows"] for item in validation.values()),
            19,
        )

    def test_entity_and_source_installation_is_complete_and_idempotent(self) -> None:
        entities, sources, _ = self._installed()
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_C_ENTITIES), 4)
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_C_SOURCES), 34)
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_C_ENTITIES},
            set(entities),
        )
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_C_SOURCES},
            set(sources),
        )
        before_entities = copy.deepcopy(entities)
        before_sources = copy.deepcopy(sources)
        lane.install_wave8_followup_c_entities(entities)
        lane.install_wave8_followup_c_sources(sources)
        self.assertEqual(entities, before_entities)
        self.assertEqual(sources, before_sources)
        self.assertEqual(
            lane.validate_wave8_followup_c_existing_entities(entities),
            {
                "georgian_uprising": {"required_existing_entities": 1},
                "great_northern_exact": {"required_existing_entities": 5},
            },
        )

    def test_bundle_emits_exactly_fourteen_reviewed_events(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 14)
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in events},
            lane.WAVE8_FOLLOWUP_C_CONTRACT_IDS,
        )
        self.assertTrue(
            all(event.get("identity_resolution") == "candidate_keyed_exact" for event in events)
        )
        self.assertFalse(
            any(
                "inconclusive"
                in {str(item.get("termination")) for item in event["participants"]}
                for event in events
            )
        )

    def test_unknowns_and_false_draw_duplicate_never_emit(self) -> None:
        emitted = {str(event["hced_candidate_id"]) for event in self._events()}
        self.assertFalse(emitted & set(lane.WAVE8_FOLLOWUP_C_HOLDS))
        self.assertFalse(
            emitted & set(lane.WAVE8_FOLLOWUP_C_TERMINAL_EXCLUSIONS)
        )
        for hold in lane.WAVE8_FOLLOWUP_C_HOLDS.values():
            self.assertEqual(hold["result_type"], "unknown")
            self.assertIs(hold["unknown_is_never_draw"], True)

    def test_location_review_union_is_pinned(self) -> None:
        self.assertEqual(
            len(lane.WAVE8_FOLLOWUP_C_POINT_QUARANTINE_ADDITIONS), 9
        )
        self.assertEqual(
            lane.WAVE8_FOLLOWUP_C_COUNTRY_QUARANTINE_ADDITIONS,
            {"hced-Oum Droussa1977-1"},
        )
        by_id = {str(event["hced_candidate_id"]): event for event in self._events()}
        for candidate_id in lane.WAVE8_FOLLOWUP_C_POINT_QUARANTINE_ADDITIONS:
            if candidate_id in by_id:
                self.assertNotIn("geometry", by_id[candidate_id])
        self.assertNotIn(
            "modern_location_country", by_id["hced-Oum Droussa1977-1"]
        )

    def test_discovery_and_cross_source_validators_all_pass(self) -> None:
        discovery = lane.validate_wave8_followup_c_discovery_dispositions(
            self.wikidata
        )
        self.assertEqual(set(discovery), {"bilbao", "sertorian"})
        entities, _, existing = self._installed()
        promoted = lane.promote_wave8_followup_c_contracts(
            self.hced, entities, existing
        )
        validation = lane.validate_wave8_followup_c_integration_dispositions(
            self.hced,
            self.iwd,
            self.iwbd,
            [*existing, *promoted],
        )
        self.assertEqual(
            set(validation),
            {"bilbao", "georgian_uprising", "great_northern_exact", "polisario"},
        )

    def test_counts_metadata_signature_and_duplicate_guard_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_followup_c_counts(),
            {
                "country_quarantine_additions": 1,
                "holds": 4,
                "new_entities": 4,
                "new_sources": 34,
                "newly_rated_events": 14,
                "point_quarantine_additions": 9,
                "promotion_contracts": 14,
                "reviewed_hced_rows": 19,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            lane.wave8_followup_c_audit_signature(),
            lane.WAVE8_FOLLOWUP_C_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_followup_c_metadata()
        self.assertEqual(
            set(metadata["lanes"]),
            {
                "bilbao",
                "georgian_uprising",
                "great_northern_exact",
                "polisario",
                "sertorian",
            },
        )
        entities, _, existing = self._installed()
        promoted = lane.promote_wave8_followup_c_contracts(
            self.hced, entities, existing
        )
        with self.assertRaisesRegex(ValueError, "already promoted"):
            lane.promote_wave8_followup_c_contracts(
                self.hced, entities, [*existing, *promoted]
            )


if __name__ == "__main__":
    unittest.main()
