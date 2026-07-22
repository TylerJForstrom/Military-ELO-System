import copy
import json
import unittest
from pathlib import Path

from military_elo.promotion import wave8_followup_d as lane


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8FollowupDBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.wikidata = _jsonl(
            ROOT / "data/review/wikidata-battle-candidates.jsonl"
        )
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        entity_ids = {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_D_ENTITIES}
        source_ids = {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_D_SOURCES}
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
            not in lane.WAVE8_FOLLOWUP_D_CONTRACT_IDS
        ]
        lane.install_wave8_followup_d_entities(entities)
        lane.install_wave8_followup_d_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_followup_d_contracts(
            self.hced, entities, existing
        )

    def test_combined_inventory_is_disjoint_and_exact(self) -> None:
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_D_CONTRACT_IDS), 20)
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_D_RESERVED_IDS), 25)
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_D_HOLDS), 5)
        self.assertEqual(
            lane.WAVE8_FOLLOWUP_D_RESERVED_IDS,
            lane.WAVE8_FOLLOWUP_D_CONTRACT_IDS
            | set(lane.WAVE8_FOLLOWUP_D_HOLDS),
        )

    def test_all_five_queue_validators_run_fail_closed(self) -> None:
        validation = lane.validate_wave8_followup_d_queue_contracts(self.hced)
        self.assertEqual(
            set(validation),
            {
                "cuban",
                "finnish_civil_war",
                "irish_royalists",
                "lower_canada",
                "swabian_hre",
            },
        )
        self.assertEqual(
            sum(item["promotion_contracts"] for item in validation.values()),
            20,
        )
        self.assertEqual(
            sum(item["reviewed_hced_rows"] for item in validation.values()),
            25,
        )

    def test_entity_and_source_installation_is_complete_and_idempotent(self) -> None:
        entities, sources, _ = self._installed()
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_D_ENTITIES), 31)
        self.assertEqual(len(lane.WAVE8_FOLLOWUP_D_SOURCES), 58)
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_D_ENTITIES},
            set(entities),
        )
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_FOLLOWUP_D_SOURCES},
            set(sources),
        )
        before_entities = copy.deepcopy(entities)
        before_sources = copy.deepcopy(sources)
        lane.install_wave8_followup_d_entities(entities)
        lane.install_wave8_followup_d_sources(sources)
        self.assertEqual(entities, before_entities)
        self.assertEqual(sources, before_sources)

    def test_bundle_emits_exactly_twenty_reviewed_events(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 20)
        self.assertEqual(
            {str(event["hced_candidate_id"]) for event in events},
            lane.WAVE8_FOLLOWUP_D_CONTRACT_IDS,
        )
        self.assertTrue(
            all(
                event.get("identity_resolution") == "candidate_keyed_exact"
                for event in events
            )
        )

    def test_all_five_unknown_holds_never_emit_or_become_draws(self) -> None:
        emitted = {str(event["hced_candidate_id"]) for event in self._events()}
        self.assertFalse(emitted & set(lane.WAVE8_FOLLOWUP_D_HOLDS))
        for hold in lane.WAVE8_FOLLOWUP_D_HOLDS.values():
            self.assertEqual(hold["result_type"], "unknown")
            self.assertIs(hold["unknown_is_never_draw"], True)

    def test_location_quarantine_union_is_pinned(self) -> None:
        self.assertEqual(
            len(lane.WAVE8_FOLLOWUP_D_POINT_QUARANTINE_ADDITIONS), 15
        )
        self.assertEqual(
            lane.WAVE8_FOLLOWUP_D_COUNTRY_QUARANTINE_ADDITIONS,
            {"hced-Calven1499-1", "hced-Dungan Hill1647-1"},
        )
        by_id = {str(event["hced_candidate_id"]): event for event in self._events()}
        for candidate_id in lane.WAVE8_FOLLOWUP_D_POINT_QUARANTINE_ADDITIONS:
            self.assertNotIn("geometry", by_id[candidate_id])
        for candidate_id in lane.WAVE8_FOLLOWUP_D_COUNTRY_QUARANTINE_ADDITIONS:
            self.assertNotIn("modern_location_country", by_id[candidate_id])

    def test_discovery_candidates_remain_nonrating(self) -> None:
        validation = lane.validate_wave8_followup_d_discovery_dispositions(
            self.wikidata
        )
        self.assertGreaterEqual(len(validation), 4)
        emitted = {str(event["id"]) for event in self._events()}
        self.assertFalse(any(event_id.startswith("wikidata_") for event_id in emitted))

    def test_counts_signature_artifact_and_duplicate_guards_are_pinned(self) -> None:
        counts = lane.wave8_followup_d_counts()
        self.assertEqual(counts["newly_rated_events"], 20)
        self.assertEqual(counts["reviewed_hced_rows"], 25)
        self.assertEqual(counts["holds"], 5)
        self.assertEqual(counts["new_entities"], 31)
        self.assertEqual(counts["new_sources"], 58)
        self.assertEqual(counts["point_quarantine_additions"], 15)
        self.assertEqual(counts["country_quarantine_additions"], 2)
        self.assertEqual(
            lane.wave8_followup_d_audit_signature(),
            lane.WAVE8_FOLLOWUP_D_FINAL_AUDIT_SIGNATURE,
        )
        entities, sources, existing = self._installed()
        promoted = lane.promote_wave8_followup_d_contracts(
            self.hced, entities, existing
        )
        self.assertEqual(
            lane.validate_wave8_followup_d_artifact_state(
                [*existing, *promoted], entities.values(), sources.values()
            )["events_present"],
            20,
        )
        with self.assertRaisesRegex(ValueError, "already promoted"):
            lane.promote_wave8_followup_d_contracts(
                self.hced, entities, [*existing, *promoted]
            )


if __name__ == "__main__":
    unittest.main()
