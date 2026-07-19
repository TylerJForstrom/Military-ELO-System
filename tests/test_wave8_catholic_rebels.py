import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_catholic_rebels as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
KINGDOM_ENGLAND = "kingdom_england"
WESTERN_REBELS = "western_rebellion_insurgent_army_1549"
GORDON_MARIAN = "adam_gordon_marian_force_craibstone_1571"
FORBES_REGENT = "forbes_regent_force_craibstone_1571"
EVENT_PREFIX = "hced_wave8_catholic_rebels_"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8CatholicRebelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")

    def _installed(self):
        lane_entity_ids = {
            str(item["id"]) for item in lane.WAVE8_CATHOLIC_REBELS_ENTITIES
        }
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane.install_wave8_catholic_rebels_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_CATHOLIC_REBELS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_catholic_rebels_contracts(
            self.hced,
            entities,
            existing,
        )

    def _is_integrated(self) -> bool:
        return (
            "accepted_wave8_catholic_rebels_hced_events"
            in self.release_metadata.get("promotion", {})
        )

    def test_complete_label_inventory_and_row_hashes_are_pinned(self) -> None:
        relevant = {
            str(row["candidate_id"]): row
            for row in self.hced
            if any(
                normalize_label(row.get(key)) == "catholic rebels"
                for key in ("side_1_raw", "side_2_raw")
            )
        }
        self.assertEqual(set(relevant), lane.WAVE8_CATHOLIC_REBELS_RESERVED_IDS)
        self.assertEqual(len(relevant), 3)
        for candidate_id, expected_hash in lane.WAVE8_CATHOLIC_REBELS_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(relevant[candidate_id]),
                    expected_hash,
                )

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_catholic_rebels_queue_contracts(self.hced),
            {
                "exact_label_rows": 3,
                "holds": 0,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 3,
            },
        )
        if not self._is_integrated():
            self.assertEqual(
                lane.validate_wave8_catholic_rebels_funnel(self.funnel),
                {
                    "events_touched": 3,
                    "sole_blocker_events": 3,
                    "unresolved_side_attempts": 3,
                    "zero_time_valid_candidates": 3,
                },
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"]
                ["wave8_catholic_rebels_exact_label_funnel_audit"],
                lane.WAVE8_CATHOLIC_REBELS_FUNNEL_AUDIT,
            )

    def test_three_narrow_identities_open_no_generic_alias(self) -> None:
        entities = {
            str(item["id"]): item
            for item in lane.WAVE8_CATHOLIC_REBELS_ENTITIES
        }
        self.assertEqual(
            set(entities),
            {WESTERN_REBELS, GORDON_MARIAN, FORBES_REGENT},
        )
        self.assertEqual(
            (entities[WESTERN_REBELS]["start_year"], entities[WESTERN_REBELS]["end_year"]),
            (1549, 1549),
        )
        for entity_id in (GORDON_MARIAN, FORBES_REGENT):
            self.assertEqual(
                (entities[entity_id]["start_year"], entities[entity_id]["end_year"]),
                (1571, 1571),
            )
        for entity in entities.values():
            self.assertEqual(entity["aliases"], [])
            self.assertNotEqual(normalize_label(entity["name"]), "catholic rebels")
            Entity.from_dict(entity)

    def test_sources_parse_and_each_event_has_two_outcome_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_CATHOLIC_REBELS_SOURCES), 8)
        for source in lane.WAVE8_CATHOLIC_REBELS_SOURCES:
            Source.from_dict(source)
        for candidate_id, contract in lane.WAVE8_CATHOLIC_REBELS_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(len(contract["outcome_source_ids"]), 2)
                self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertLessEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )

    def test_all_three_distinct_battles_promote(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_CATHOLIC_REBELS_CONTRACT_IDS)
        self.assertEqual(
            {
                candidate_id: (event["name"], event["year"], event["date_precision"])
                for candidate_id, event in events.items()
            },
            {
                "hced-St Marys Clyst1549-1": (
                    "Battle of Clyst St Mary",
                    1549,
                    "year",
                ),
                "hced-Sampford Courtenay1549-1": (
                    "Battle of Sampford Courtenay",
                    1549,
                    "year",
                ),
                "hced-Craibstane1571-1": (
                    "Battle of Craibstone",
                    1571,
                    "year",
                ),
            },
        )
        for event in events.values():
            self.assertEqual(event["war_type"], "civil_war")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            Event.from_dict(event)

    def test_actor_split_and_craibstone_reversal_are_explicit(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}

        def outcomes(candidate_id):
            return {
                item["entity_id"]: item["termination"]
                for item in events[candidate_id]["participants"]
            }

        expected_western = {
            KINGDOM_ENGLAND: "engagement_victory",
            WESTERN_REBELS: "engagement_defeat",
        }
        self.assertEqual(outcomes("hced-St Marys Clyst1549-1"), expected_western)
        self.assertEqual(
            outcomes("hced-Sampford Courtenay1549-1"), expected_western
        )
        self.assertEqual(
            outcomes("hced-Craibstane1571-1"),
            {
                GORDON_MARIAN: "engagement_victory",
                FORBES_REGENT: "engagement_defeat",
            },
        )
        for candidate_id, contract in lane.WAVE8_CATHOLIC_REBELS_CONTRACTS.items():
            if candidate_id == "hced-Craibstane1571-1":
                self.assertTrue(contract["source_outcome_override"])
                self.assertTrue(contract["outcome_reversal"])
                self.assertEqual(contract["winner_side"], 2)
            else:
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])
                self.assertEqual(contract["winner_side"], 1)

    def test_clyst_prisoner_massacre_is_not_scored_as_an_event(self) -> None:
        clyst = lane.WAVE8_CATHOLIC_REBELS_CONTRACTS[
            "hced-St Marys Clyst1549-1"
        ]
        self.assertIn("separate atrocity", clyst["audit_note"])
        self.assertEqual(clyst["result_type"], "win")
        self.assertFalse(lane.WAVE8_CATHOLIC_REBELS_HOLDS)
        self.assertFalse(lane.WAVE8_CATHOLIC_REBELS_HOLD_IDS)

    def test_unbound_hced_points_are_withheld_but_country_is_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_CATHOLIC_REBELS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_CATHOLIC_REBELS_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_CATHOLIC_REBELS_COUNTRY_QUARANTINE_ADDITIONS)
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "United Kingdom")
            self.assertIn("location_provenance", event)

    def test_no_probable_cross_source_twins(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_catholic_rebels_integration_dispositions(
                self.hced,
                self.iwbd,
                existing,
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_installers_are_idempotent_and_collision_safe(self) -> None:
        entities = {}
        lane.install_wave8_catholic_rebels_entities(entities)
        lane.install_wave8_catholic_rebels_entities(entities)
        self.assertEqual(len(entities), 3)
        entities[WESTERN_REBELS]["name"] = "drift"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_catholic_rebels_entities(entities)

        sources = {}
        lane.install_wave8_catholic_rebels_sources(sources)
        lane.install_wave8_catholic_rebels_sources(sources)
        self.assertEqual(len(sources), 8)
        first_id = str(lane.WAVE8_CATHOLIC_REBELS_SOURCES[0]["id"])
        sources[first_id]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_catholic_rebels_sources(sources)

    def test_row_drift_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Craibstane1571-1"
        )
        row["winner_raw"] = "Catholic Rebels"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_catholic_rebels_queue_contracts(tampered)

        entities, existing = self._installed()
        existing.append(
            {
                "id": "duplicate",
                "name": "Battle of Craibstone",
                "year": 1571,
                "participants": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_catholic_rebels_contracts(
                self.hced,
                entities,
                existing,
            )

    def test_signature_counts_and_cohorts_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_catholic_rebels_audit_signature(),
            lane.WAVE8_CATHOLIC_REBELS_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_catholic_rebels_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 0,
                "new_entities": 3,
                "new_sources": 8,
                "newly_rated_events": 3,
                "outcome_overrides": 1,
                "point_quarantine_additions": 3,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_catholic_rebels_cohort_counts(),
            {
                "marian_civil_war_catholic_rebels_1571": 1,
                "western_rebellion_catholic_rebels_1549": 2,
            },
        )

    def test_release_artifacts_are_preintegration_or_exactly_integrated(self) -> None:
        release_events = {
            str(row.get("hced_candidate_id")): row
            for row in self.release_events
            if row.get("hced_candidate_id")
            in lane.WAVE8_CATHOLIC_REBELS_RESERVED_IDS
        }
        if not self._is_integrated():
            self.assertFalse(release_events)
            return

        self.assertEqual(set(release_events), lane.WAVE8_CATHOLIC_REBELS_CONTRACT_IDS)
        release_entity_ids = {str(row["id"]) for row in self.release_entities}
        self.assertLessEqual(
            {WESTERN_REBELS, GORDON_MARIAN, FORBES_REGENT},
            release_entity_ids,
        )
        release_source_ids = {str(row["id"]) for row in self.release_sources}
        self.assertLessEqual(
            {str(row["id"]) for row in lane.WAVE8_CATHOLIC_REBELS_SOURCES},
            release_source_ids,
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_catholic_rebels_hced_events"], 3)
        self.assertEqual(
            promotion["wave8_catholic_rebels_candidate_ids"],
            sorted(lane.WAVE8_CATHOLIC_REBELS_CONTRACT_IDS),
        )
        coverage = self.registry["coverage"]
        self.assertEqual(len(self.release_entities), 1_026)
        self.assertEqual(len(self.release_events), 5_419)
        self.assertEqual(len(self.registry["entities"]), 2_374)
        self.assertEqual(coverage["rated_entities"], 1_018)
        self.assertEqual(coverage["unresolved_event_candidates"], 36_929)
        location = coverage["hced_location_assertions"]
        self.assertEqual(location["hced_candidate_bindings"], 5_155)
        self.assertEqual(location["candidate_keyed_reviewed_contracts"], 787)
        self.assertEqual(location["geojson_points"], 4_798)
        self.assertEqual(location["modern_location_country_assertions"], 5_060)
        self.assertEqual(location["location_provenance_objects"], 5_109)
        self.assertEqual(location["point_fields_withheld_by_quarantine"], 357)
        self.assertEqual(location["unique_events_with_any_quarantined_field"], 405)


if __name__ == "__main__":
    unittest.main()
