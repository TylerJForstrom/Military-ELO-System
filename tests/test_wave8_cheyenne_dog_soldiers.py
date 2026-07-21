import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.promotion import wave8_cheyenne_dog_soldiers as lane
from military_elo.promotion.policy import HCED_LABEL_POLICIES
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_algiers_cheyenne import (
    WAVE8_ALGIERS_CHEYENNE_FINAL_AUDIT_SIGNATURE,
    validate_wave8_algiers_cheyenne_queue_contracts,
    wave8_algiers_cheyenne_audit_signature,
)


ROOT = Path(__file__).resolve().parents[1]
DOG_SOLDIERS = "cheyenne_dog_soldiers_band_1849_1869"
UNITED_STATES = "united_states"
EVENT_PREFIX = "hced_wave8_cheyenne_dog_soldiers_"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8CheyenneDogSoldiersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.events = _json(ROOT / "data/release/events.json")
        cls.entities = _json(ROOT / "data/release/entities.json")
        cls.sources = _json(ROOT / "data/release/sources.json")
        cls.metadata = _json(ROOT / "data/release/metadata.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")

    def _promote(self):
        entities = {str(item["id"]): copy.deepcopy(item) for item in self.entities}
        lane.install_wave8_cheyenne_dog_soldiers_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        return lane.promote_wave8_cheyenne_dog_soldiers_contracts(
            self.hced,
            entities,
            existing,
        )

    def test_exact_label_inventory_fingerprints_and_dispositions_are_pinned(self):
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if str(row.get("side_1_raw", "")).casefold() == "cheyenne"
            or str(row.get("side_2_raw", "")).casefold() == "cheyenne"
        }
        self.assertEqual(set(rows), set(lane.WAVE8_CHEYENNE_DOG_SOLDIERS_ROW_HASHES))
        for candidate_id, expected in lane.WAVE8_CHEYENNE_DOG_SOLDIERS_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(canonical_hced_row_sha256(rows[candidate_id]), expected)
                self.assertIs(rows[candidate_id]["do_not_rate_automatically"], True)
        self.assertEqual(
            lane.validate_wave8_cheyenne_dog_soldiers_queue_contracts(self.hced),
            {
                "exact_label_rows": 3,
                "holds": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 1,
            },
        )

    def test_identity_is_time_bounded_alias_free_and_never_globalized(self):
        self.assertEqual(len(lane.WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES), 1)
        entity = lane.WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES[0]
        self.assertEqual(entity["id"], DOG_SOLDIERS)
        self.assertEqual((entity["start_year"], entity["end_year"]), (1849, 1869))
        self.assertFalse(entity["aliases"])
        self.assertFalse(entity["predecessors"])
        self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
        self.assertNotIn("cheyenne", HCED_LABEL_POLICIES)
        self.assertTrue(
            all(
                "cheyenne" not in {str(alias).casefold() for alias in item.get("aliases", [])}
                for item in self.entities
            )
        )

    def test_promotions_are_two_high_confidence_us_tactical_wins_not_draws(self):
        events = self._promote()
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            lane.WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS,
        )
        for event in events:
            with self.subTest(event_id=event["id"]):
                self.assertTrue(event["id"].startswith(EVENT_PREFIX))
                self.assertEqual(event["confidence"], 0.92)
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                winner = [p for p in event["participants"] if p["side"] == "side_a"]
                loser = [p for p in event["participants"] if p["side"] == "side_b"]
                self.assertEqual([p["entity_id"] for p in winner], [UNITED_STATES])
                self.assertEqual([p["entity_id"] for p in loser], [DOG_SOLDIERS])
                self.assertTrue(all("victory" in p["termination"] for p in winner))
                self.assertTrue(all("defeat" in p["termination"] for p in loser))
                self.assertFalse(
                    any("inconclusive" in p["termination"] for p in event["participants"])
                )

    def test_beaver_point_is_withheld_while_country_and_provenance_remain(self):
        events = {event["hced_candidate_id"]: event for event in self._promote()}
        beaver = events["hced-Beaver Creek1868-1"]
        beecher = events["hced-Beecher Island1868-1"]
        self.assertNotIn("geometry", beaver)
        self.assertEqual(beaver["modern_location_country"], "United States")
        self.assertEqual(beaver["location_provenance"]["source_record_id"], "Beaver Creek1868")
        self.assertEqual(
            set(lane.WAVE8_CHEYENNE_DOG_SOLDIERS_POINT_QUARANTINE_ADDITIONS),
            {"hced-Beaver Creek1868-1"},
        )
        self.assertIn("geometry", beecher)

    def test_cedar_canyon_is_terminally_excluded_and_never_rated(self):
        exclusion = lane.WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS[
            "hced-Cedar Canyon1864-1"
        ]
        self.assertEqual(exclusion["disposition"], "terminal_exclusion")
        self.assertIs(exclusion["terminal_exclusion"], True)
        self.assertEqual(
            exclusion["hold_category"],
            "noncompetitive_attack_on_peace_village",
        )
        self.assertNotIn(
            "hced-Cedar Canyon1864-1",
            {event.get("hced_candidate_id") for event in self.events},
        )

    def test_sources_are_closed_and_each_promoted_outcome_has_two_families(self):
        source_by_id = {
            str(source["id"]): source
            for source in lane.WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES
        }
        self.assertEqual(len(source_by_id), 7)
        for contract in lane.WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS.values():
            outcomes = contract["outcome_source_ids"]
            self.assertEqual(outcomes, sorted(set(outcomes)))
            self.assertEqual(set(outcomes), set(contract["evidence_refs"]))
            self.assertTrue(set(outcomes) <= set(source_by_id))
            self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertTrue(
                all("outcome" in source_by_id[source_id]["evidence_roles"] for source_id in outcomes)
            )

    def test_frozen_algiers_cheyenne_validator_and_signature_survive_lane(self):
        before = validate_wave8_algiers_cheyenne_queue_contracts(self.hced)
        signature = wave8_algiers_cheyenne_audit_signature()
        self._promote()
        after = validate_wave8_algiers_cheyenne_queue_contracts(self.hced)
        self.assertEqual(after, before)
        self.assertEqual(signature, WAVE8_ALGIERS_CHEYENNE_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_algiers_cheyenne_audit_signature(), signature)

    def test_funnel_pin_is_reproducible_and_live_cheyenne_label_is_gone(self):
        historical = copy.deepcopy(lane.WAVE8_CHEYENNE_DOG_SOLDIERS_FUNNEL_AUDIT)
        zero = historical.pop("zero_time_valid_candidates")
        historical["failure_cases"] = {"zero_time_valid_candidates": zero}
        self.assertEqual(
            lane.validate_wave8_cheyenne_dog_soldiers_funnel({"labels": [historical]}),
            {
                "events_touched": 3,
                "sole_blocker_events": 3,
                "zero_time_valid_candidates": 3,
            },
        )
        self.assertFalse([row for row in self.funnel["labels"] if row["label"] == "cheyenne"])

    def test_row_drift_unknown_outcome_and_duplicate_release_fail_closed(self):
        tampered = copy.deepcopy(self.hced)
        row = next(item for item in tampered if item["candidate_id"] == "hced-Beaver Creek1868-1")
        row["winner_raw"] = "Unknown"
        with self.assertRaises(ValueError):
            lane.validate_wave8_cheyenne_dog_soldiers_queue_contracts(tampered)
        entities = {str(item["id"]): item for item in self.entities}
        duplicate = copy.deepcopy(self.events)
        duplicate.append({"hced_candidate_id": "hced-Beaver Creek1868-1", "name": "x", "year": 1868})
        with self.assertRaises(ValueError):
            lane.promote_wave8_cheyenne_dog_soldiers_contracts(self.hced, entities, duplicate)

    def test_integration_duplicate_audit_is_zero_and_fail_closed(self):
        existing = [
            event
            for event in self.events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS
        ]
        self.assertEqual(
            lane.validate_wave8_cheyenne_dog_soldiers_integration_dispositions(
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
        with self.assertRaises(ValueError):
            lane.validate_wave8_cheyenne_dog_soldiers_integration_dispositions(
                self.hced,
                [{"candidate_id": "iwbd-future", "name": "Beecher Island", "year": 1868}],
                existing,
            )

    def test_audit_signature_is_complete_and_pinned(self):
        payload = {
            "contracts": lane.WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS,
            "entities": lane.WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES,
            "funnel": lane.WAVE8_CHEYENNE_DOG_SOLDIERS_FUNNEL_AUDIT,
            "holds": lane.WAVE8_CHEYENNE_DOG_SOLDIERS_HOLDS,
            "location_reasons": lane.WAVE8_CHEYENNE_DOG_SOLDIERS_LOCATION_QUARANTINE_REASONS,
            "row_hashes": lane.WAVE8_CHEYENNE_DOG_SOLDIERS_ROW_HASHES,
            "sources": lane.WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES,
            "terminal_exclusions": lane.WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS,
        }
        measured = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self.assertEqual(measured, lane.WAVE8_CHEYENNE_DOG_SOLDIERS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(measured, lane.wave8_cheyenne_dog_soldiers_audit_signature())

    def test_integrated_artifacts_and_count_cascade_are_exact(self):
        owned = [
            event
            for event in self.events
            if event.get("hced_candidate_id")
            in lane.WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS
        ]
        self.assertEqual(len(owned), 2)
        self.assertEqual(len(self.events), 5_506)
        self.assertEqual(len(self.entities), 1_080)
        self.assertEqual(len(self.registry["entities"]), 2_419)
        coverage = self.registry["coverage"]
        self.assertEqual(coverage["rated_entities"], 1_073)
        self.assertEqual(coverage["unresolved_event_candidates"], 36_837)
        location = coverage["hced_location_assertions"]
        self.assertEqual(
            (
                location["hced_candidate_bindings"],
                location["candidate_keyed_reviewed_contracts"],
                location["geojson_points"],
                location["modern_location_country_assertions"],
                location["location_provenance_objects"],
            ),
            (5_239, 833, 4_836, 5_144, 5_193),
        )

    def test_integrated_metadata_registry_entity_and_sources_are_exact(self):
        promotion = self.metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_cheyenne_dog_soldiers_hced_events"], 2)
        self.assertEqual(
            promotion["wave8_cheyenne_dog_soldiers_counts"],
            lane.wave8_cheyenne_dog_soldiers_counts(),
        )
        self.assertEqual(
            promotion["wave8_cheyenne_dog_soldiers_frozen_lane_post_validation"],
            validate_wave8_algiers_cheyenne_queue_contracts(self.hced),
        )
        entity_by_id = {str(item["id"]): item for item in self.entities}
        registry_by_id = {str(item["id"]): item for item in self.registry["entities"]}
        self.assertEqual(entity_by_id[DOG_SOLDIERS], lane.WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES[0])
        self.assertEqual(registry_by_id[DOG_SOLDIERS]["status"], "rated")
        source_ids = {str(item["id"]) for item in self.sources}
        self.assertTrue(
            {str(item["id"]) for item in lane.WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES}
            <= source_ids
        )


if __name__ == "__main__":
    unittest.main()
