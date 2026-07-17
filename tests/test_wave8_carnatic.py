import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_carnatic as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
CARNATIC = "clio_in_carnatic_sul_1713_80e63d27"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8CarnaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.cliopatria = _jsonl(
            ROOT / "data/review/cliopatria-entity-candidates.jsonl"
        )
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        lane.install_wave8_carnatic_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_CARNATIC_CONTRACT_IDS
            and not str(event.get("id", "")).startswith("hced_wave8_carnatic_")
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_carnatic_contracts(
            self.hced, entities, existing
        )

    def test_complete_arcot_inventory_and_row_hashes_are_pinned(self) -> None:
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if str(row.get("candidate_id")) in lane.WAVE8_CARNATIC_ROW_HASHES
        }
        self.assertEqual(set(rows), set(lane.WAVE8_CARNATIC_ROW_HASHES))
        self.assertEqual(len(rows), 9)
        for candidate_id, expected in lane.WAVE8_CARNATIC_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(canonical_hced_row_sha256(rows[candidate_id]), expected)
                self.assertIs(rows[candidate_id]["winner_loser_complete"], True)

    def test_queue_and_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_carnatic_queue_contracts(self.hced),
            {
                "arcot_related_rows": 9,
                "holds": 3,
                "legacy_crosswalk_rows": 3,
                "promotion_contracts": 3,
                "reserved_hced_rows": 6,
                "reviewed_hced_rows": 9,
            },
        )
        self.assertEqual(
            lane.validate_wave8_carnatic_funnel(self.funnel),
            {
                "events_touched": 5,
                "labels": 2,
                "sole_blocker_events": 5,
                "zero_time_valid_candidates": 5,
            },
        )

    def test_existing_registry_candidate_is_curated_without_arcot_aliases(self) -> None:
        candidate = next(
            row
            for row in self.cliopatria
            if row.get("canonical_name_candidate") == "Carnatic Sultanate"
        )
        self.assertEqual(candidate["candidate_id"], "cliopatria-905")
        self.assertEqual(candidate["seshat_ids"], ["in_carnatic_sul"])
        entity = lane.WAVE8_CARNATIC_ENTITIES[0]
        self.assertEqual(entity["id"], CARNATIC)
        self.assertEqual((entity["start_year"], entity["end_year"]), (1713, 1802))
        self.assertFalse(entity["aliases"])
        self.assertNotIn("arcot", [alias.lower() for alias in entity["aliases"]])
        Entity.from_dict(entity)

    def test_sources_parse_and_each_promotion_has_two_outcome_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_CARNATIC_SOURCES), 8)
        for source in lane.WAVE8_CARNATIC_SOURCES:
            Source.from_dict(source)
        for contract in lane.WAVE8_CARNATIC_CONTRACTS.values():
            self.assertEqual(len(contract["outcome_source_ids"]), 2)
            self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(set(contract["outcome_source_family_ids"])),
            )

    def test_dispositions_separate_promotions_holds_and_legacy_rows(self) -> None:
        self.assertEqual(
            lane.WAVE8_CARNATIC_CONTRACT_IDS,
            {
                "hced-Arcot1780-1",
                "hced-Damalcherry Pass1740-1",
                "hced-St Thome1746-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_CARNATIC_HOLD_IDS,
            {
                "hced-Ambur1749-1",
                "hced-Gingee1750-1",
                "hced-Trichinopoly1740-1741-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_CARNATIC_LEGACY_IDS,
            {
                "hced-Arcot1751-1",
                "hced-Seringham1752-1",
                "hced-Tiruvadi1750-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_CARNATIC_AUDITED_IDS,
            set(lane.WAVE8_CARNATIC_ROW_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_CARNATIC_RESERVED_IDS,
            lane.WAVE8_CARNATIC_CONTRACT_IDS | lane.WAVE8_CARNATIC_HOLD_IDS,
        )
        self.assertFalse(
            lane.WAVE8_CARNATIC_RESERVED_IDS & lane.WAVE8_CARNATIC_LEGACY_IDS
        )
        for hold in lane.WAVE8_CARNATIC_HOLDS.values():
            self.assertEqual(hold["disposition"], "hold")
            self.assertTrue(hold["reason_code"])

    def test_promotions_retain_locked_winners_and_carnatic_loser(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        expected_winners = {
            "hced-Damalcherry Pass1740-1": "maratha_confederacy",
            "hced-St Thome1746-1": "kingdom_france",
            "hced-Arcot1780-1": "kingdom_mysore",
        }
        self.assertEqual(set(events), set(expected_winners))
        for candidate_id, winner_id in expected_winners.items():
            event = events[candidate_id]
            outcomes = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(outcomes[winner_id], "engagement_victory")
            self.assertEqual(outcomes[CARNATIC], "engagement_defeat")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertFalse(
                lane.WAVE8_CARNATIC_CONTRACTS[candidate_id][
                    "source_outcome_override"
                ]
            )
            self.assertEqual(len(event["outcome_source_family_ids"]), 2)
            Event.from_dict(event)

    def test_canonical_names_years_and_confidence_are_pinned(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        expected = {
            "hced-Damalcherry Pass1740-1": (
                "Battle of Damalcherry Pass",
                1740,
                0.95,
            ),
            "hced-St Thome1746-1": ("Battle of St. Thome", 1746, 0.95),
            "hced-Arcot1780-1": ("Siege and Capture of Arcot", 1780, 0.92),
        }
        for candidate_id, (name, year, confidence) in expected.items():
            event = events[candidate_id]
            self.assertEqual(event["name"], name)
            self.assertEqual((event["year"], event["end_year"]), (year, year))
            self.assertEqual(event["confidence"], confidence)

    def test_points_are_withheld_and_india_is_retained(self) -> None:
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "India")
            self.assertIn("location_provenance", event)

    def test_legacy_crosswalk_events_remain_unchanged_without_carnatic(self) -> None:
        legacy = {
            str(event.get("hced_candidate_id")): event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_CARNATIC_LEGACY_IDS
        }
        self.assertEqual(set(legacy), lane.WAVE8_CARNATIC_LEGACY_IDS)
        for event in legacy.values():
            actors = {
                str(participant["entity_id"])
                for participant in event["participants"]
            }
            self.assertEqual(actors, {"united_kingdom", "kingdom_france"})
            self.assertNotIn(CARNATIC, actors)

    def test_no_probable_cross_source_twins_and_all_dispositions_hold(self) -> None:
        _, existing = self._installed()
        events = self._events()
        self.assertEqual(
            lane.validate_wave8_carnatic_integration_dispositions(
                self.hced, self.iwbd, [*existing, *events]
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
                "legacy_crosswalk_events_preserved": 3,
            },
        )

    def test_row_drift_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Damalcherry Pass1740-1"
        )
        row["winner_raw"] = "Arcot"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_carnatic_queue_contracts(tampered)

        entities, existing = self._installed()
        existing.append(
            {
                "id": "duplicate",
                "name": "Battle of Damalcherry Pass",
                "year": 1740,
                "participants": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_carnatic_contracts(
                self.hced, entities, existing
            )

    def test_source_and_entity_installers_are_idempotent_and_collision_safe(self) -> None:
        entities, _ = self._installed()
        before = copy.deepcopy(entities[CARNATIC])
        lane.install_wave8_carnatic_entities(entities)
        self.assertEqual(entities[CARNATIC], before)

        sources = {}
        lane.install_wave8_carnatic_sources(sources)
        lane.install_wave8_carnatic_sources(sources)
        self.assertEqual(len(sources), 8)
        sources["wave8_carnatic_orme_transactions"]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_carnatic_sources(sources)

    def test_signature_counts_and_cohorts_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_carnatic_audit_signature(),
            lane.WAVE8_CARNATIC_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_carnatic_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 3,
                "legacy_crosswalk_rows": 3,
                "new_entities": 1,
                "new_sources": 8,
                "newly_rated_events": 3,
                "outcome_overrides": 0,
                "point_quarantine_additions": 3,
                "promotion_contracts": 3,
                "reserved_hced_rows": 6,
                "reviewed_hced_rows": 9,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_carnatic_cohort_counts(),
            {
                "legacy_crosswalk_event_preserved": 3,
                "recognized_carnatic_state_forces": 3,
                "succession_and_coalition_holds": 3,
            },
        )


if __name__ == "__main__":
    unittest.main()
