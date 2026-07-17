import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_macedon as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_exact import promote_exact_hced_contracts


ROOT = Path(__file__).resolve().parents[1]
ANTIGONID = "clio_gr_antigonid_emp_bce277_3bbcbfdf"
ATHENIAN_DEFENDERS = "athenian_defenders_chremonidean_siege_264_262_bce"
SELLASIA_ALLIANCE = "antigonus_hellenic_alliance_sellasia_222_bce"
PTOLEMAIC_EGYPT = "ptolemaic_egypt_305_bce"
ROME = "roman_republic"
SPARTA = "sparta"
EVENT_PREFIX = "hced_wave8_macedon_"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8MacedonTests(unittest.TestCase):
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
        lane_entity_ids = {str(item["id"]) for item in lane.WAVE8_MACEDON_ENTITIES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane.install_wave8_macedon_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_MACEDON_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_macedon_contracts(self.hced, entities, existing)

    def _is_integrated(self) -> bool:
        return (
            "accepted_wave8_macedon_hced_events"
            in self.release_metadata.get("promotion", {})
        )

    def test_complete_label_inventory_and_raw_rows_are_pinned(self) -> None:
        relevant = {
            str(row["candidate_id"]): row
            for row in self.hced
            if any(
                normalize_label(row.get(key)) == "macedon"
                for key in ("side_1_raw", "side_2_raw")
            )
        }
        self.assertEqual(set(relevant), lane.WAVE8_MACEDON_RESERVED_IDS)
        self.assertEqual(len(relevant), 6)
        for candidate_id, expected_hash in lane.WAVE8_MACEDON_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(relevant[candidate_id]), expected_hash
                )

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_macedon_queue_contracts(self.hced),
            {
                "exact_label_rows": 6,
                "holds": 2,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 6,
            },
        )
        if not self._is_integrated():
            self.assertEqual(
                lane.validate_wave8_macedon_funnel(self.funnel),
                {
                    "events_touched": 6,
                    "holds": 2,
                    "sole_blocker_events": 3,
                    "unresolved_side_attempts": 6,
                    "zero_time_valid_candidates": 6,
                },
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"]
                ["wave8_macedon_exact_label_funnel_audit"],
                lane.WAVE8_MACEDON_FUNNEL_AUDIT,
            )

    def test_three_narrow_identities_open_no_generic_alias(self) -> None:
        entities = {str(item["id"]): item for item in lane.WAVE8_MACEDON_ENTITIES}
        self.assertEqual(
            set(entities), {ANTIGONID, ATHENIAN_DEFENDERS, SELLASIA_ALLIANCE}
        )
        self.assertEqual(
            (entities[ANTIGONID]["start_year"], entities[ANTIGONID]["end_year"]),
            (-277, -168),
        )
        self.assertEqual(
            (
                entities[ATHENIAN_DEFENDERS]["start_year"],
                entities[ATHENIAN_DEFENDERS]["end_year"],
            ),
            (-264, -262),
        )
        self.assertEqual(
            (
                entities[SELLASIA_ALLIANCE]["start_year"],
                entities[SELLASIA_ALLIANCE]["end_year"],
            ),
            (-222, -222),
        )
        for entity in entities.values():
            self.assertEqual(entity["aliases"], [])
            self.assertNotEqual(normalize_label(entity["name"]), "macedon")
            Entity.from_dict(entity)

    def test_sources_parse_and_promotions_have_two_outcome_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_MACEDON_SOURCES), 14)
        for source in lane.WAVE8_MACEDON_SOURCES:
            Source.from_dict(source)
        for candidate_id, contract in lane.WAVE8_MACEDON_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
                self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertLessEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )

    def test_four_events_promote_with_canonical_names_and_ranges(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_MACEDON_CONTRACT_IDS)
        self.assertEqual(
            {
                candidate_id: (
                    event["name"],
                    event["year"],
                    event["end_year"],
                    event["date_precision"],
                    event["reviewed_granularity"],
                )
                for candidate_id, event in events.items()
            },
            {
                "hced-Andros-245-1": (
                    "Battle of Andros",
                    -246,
                    -245,
                    "range",
                    "naval_battle",
                ),
                "hced-Athens, Greece-264-1": (
                    "Antigonid siege and capture of Athens",
                    -264,
                    -262,
                    "range",
                    "siege",
                ),
                "hced-Callicinus-171-1": (
                    "Battle of Callinicus",
                    -171,
                    -171,
                    "year",
                    "pitched_battle",
                ),
                "hced-Sellasia-222-1": (
                    "Battle of Sellasia",
                    -222,
                    -222,
                    "year",
                    "pitched_battle",
                ),
            },
        )
        for event in events.values():
            self.assertEqual(event["war_type"], "interstate_limited")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            Event.from_dict(event)

    def test_actor_corrections_are_tactical_and_explicit(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}

        def outcomes(candidate_id):
            return {
                item["entity_id"]: item["termination"]
                for item in events[candidate_id]["participants"]
            }

        self.assertEqual(
            outcomes("hced-Andros-245-1"),
            {ANTIGONID: "engagement_victory", PTOLEMAIC_EGYPT: "engagement_defeat"},
        )
        self.assertEqual(
            outcomes("hced-Athens, Greece-264-1"),
            {
                ANTIGONID: "engagement_victory",
                ATHENIAN_DEFENDERS: "engagement_defeat",
            },
        )
        self.assertEqual(
            outcomes("hced-Callicinus-171-1"),
            {ANTIGONID: "engagement_victory", ROME: "engagement_defeat"},
        )
        self.assertEqual(
            outcomes("hced-Sellasia-222-1"),
            {SELLASIA_ALLIANCE: "engagement_victory", SPARTA: "engagement_defeat"},
        )
        for event in events.values():
            self.assertIn("no generic label fallback or strategic result", event["summary"])

    def test_date_overrides_are_closed_and_fail_without_direct_sources(self) -> None:
        self.assertEqual(
            {
                candidate_id
                for candidate_id, contract in lane.WAVE8_MACEDON_CONTRACTS.items()
                if contract["source_date_override"]
            },
            {"hced-Andros-245-1", "hced-Athens, Greece-264-1"},
        )
        contracts = copy.deepcopy(lane.WAVE8_MACEDON_CONTRACTS)
        contracts["hced-Andros-245-1"]["date_source_ids"] = []
        entities, existing = self._installed()
        with self.assertRaisesRegex(ValueError, "date override lacks"):
            promote_exact_hced_contracts(
                self.hced,
                entities,
                existing,
                contracts,
                lane_name="Macedon date-override test",
                event_id_prefix="test_",
            )

    def test_chios_conflict_is_a_hold_not_an_invented_draw(self) -> None:
        hold = lane.WAVE8_MACEDON_HOLDS["hced-Chios-201-1"]
        self.assertEqual(hold["hold_category"], "contradictory_outcome_sources")
        self.assertIn("unknown is not converted", hold["hold_reason"])
        self.assertNotIn("result_type", hold)
        self.assertNotIn("winner_side", hold)
        self.assertNotIn("hced-Chios-201-1", lane.WAVE8_MACEDON_CONTRACT_IDS)

    def test_thessaly_sign_error_and_two_battles_remain_staged(self) -> None:
        hold = lane.WAVE8_MACEDON_HOLDS["hced-Thessaly353-1"]
        self.assertEqual(hold["hold_category"], "date_and_engagement_ambiguity")
        self.assertIn("positive 353 year", hold["hold_reason"])
        self.assertIn("twice", hold["hold_reason"])
        self.assertNotIn("result_type", hold)
        self.assertNotIn("hced-Thessaly353-1", lane.WAVE8_MACEDON_CONTRACT_IDS)

    def test_unbound_hced_points_are_withheld_but_country_is_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_MACEDON_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_MACEDON_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_MACEDON_COUNTRY_QUARANTINE_ADDITIONS)
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Greece")
            self.assertIn("location_provenance", event)

    def test_no_probable_cross_source_twins(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_macedon_integration_dispositions(
                self.hced, self.iwbd, existing
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_installers_are_idempotent_and_collision_safe(self) -> None:
        entities = {}
        lane.install_wave8_macedon_entities(entities)
        lane.install_wave8_macedon_entities(entities)
        self.assertEqual(len(entities), 3)
        entities[ANTIGONID]["name"] = "drift"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_macedon_entities(entities)

        sources = {}
        lane.install_wave8_macedon_sources(sources)
        lane.install_wave8_macedon_sources(sources)
        self.assertEqual(len(sources), 14)
        first_id = str(lane.WAVE8_MACEDON_SOURCES[0]["id"])
        sources[first_id]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_macedon_sources(sources)

    def test_row_drift_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Chios-201-1"
        )
        row["winner_raw"] = "draw"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_macedon_queue_contracts(tampered)

        entities, existing = self._installed()
        existing.append(
            {
                "id": "duplicate",
                "name": "Battle of Sellasia",
                "year": -222,
                "participants": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_macedon_contracts(self.hced, entities, existing)

    def test_signature_counts_and_cohorts_are_pinned(self) -> None:
        self.assertNotEqual(lane.WAVE8_MACEDON_FINAL_AUDIT_SIGNATURE, "__PENDING__")
        self.assertEqual(
            lane.wave8_macedon_audit_signature(),
            lane.WAVE8_MACEDON_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_macedon_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 2,
                "new_entities": 3,
                "new_sources": 14,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 6,
                "source_date_overrides": 2,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_macedon_cohort_counts(),
            {
                "antigonid_macedonia_hellenistic_wars": 1,
                "chremonidean_war_athens_siege": 1,
                "cleomenean_war_sellasia": 1,
                "third_macedonian_war_callinicus": 1,
            },
        )

    def test_release_artifacts_are_preintegration_or_exactly_integrated(self) -> None:
        release_events = {
            str(row.get("hced_candidate_id")): row
            for row in self.release_events
            if row.get("hced_candidate_id") in lane.WAVE8_MACEDON_RESERVED_IDS
        }
        if not self._is_integrated():
            self.assertFalse(release_events)
            return

        self.assertEqual(set(release_events), lane.WAVE8_MACEDON_CONTRACT_IDS)
        release_entity_ids = {str(row["id"]) for row in self.release_entities}
        self.assertLessEqual(
            {ANTIGONID, ATHENIAN_DEFENDERS, SELLASIA_ALLIANCE}, release_entity_ids
        )
        release_source_ids = {str(row["id"]) for row in self.release_sources}
        self.assertLessEqual(
            {str(row["id"]) for row in lane.WAVE8_MACEDON_SOURCES},
            release_source_ids,
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_macedon_hced_events"], 4)
        self.assertEqual(
            promotion["wave8_macedon_candidate_ids"],
            sorted(lane.WAVE8_MACEDON_CONTRACT_IDS),
        )
        statuses = {
            row["id"]: row["status"]
            for row in self.registry["entities"]
            if row["id"] in {ANTIGONID, ATHENIAN_DEFENDERS, SELLASIA_ALLIANCE}
        }
        self.assertEqual(
            statuses,
            {ANTIGONID: "rated", ATHENIAN_DEFENDERS: "rated", SELLASIA_ALLIANCE: "rated"},
        )
        coverage = self.registry["coverage"]
        self.assertEqual(len(self.release_entities), 1_001)
        self.assertEqual(len(self.release_events), 5_345)
        self.assertEqual(len(self.registry["entities"]), 2_350)
        self.assertEqual(coverage["rated_entities"], 994)
        self.assertEqual(coverage["unresolved_event_candidates"], 18_049)
        location = coverage["hced_location_assertions"]
        self.assertEqual(location["hced_candidate_bindings"], 5_081)
        self.assertEqual(location["candidate_keyed_reviewed_contracts"], 771)
        self.assertEqual(location["geojson_points"], 4_734)
        self.assertEqual(location["modern_location_country_assertions"], 4_986)
        self.assertEqual(location["location_provenance_objects"], 5_035)
        self.assertEqual(location["point_fields_withheld_by_quarantine"], 347)
        self.assertEqual(location["unique_events_with_any_quarantined_field"], 395)


if __name__ == "__main__":
    unittest.main()
