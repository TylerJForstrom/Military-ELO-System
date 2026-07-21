import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_bannock_sheepeater as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
UNITED_STATES = "united_states"
BANNOCK = "bannock_resistance_force_1878"
NORTHERN_PAIUTE = "northern_paiute_resistance_force_1878"
TUKUDEKA = "tukudeka_sheepeater_defenders_vinegar_hill_1879"
EVENT_PREFIX = "hced_wave8_bannock_sheepeater_"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8BannockSheepeaterTests(unittest.TestCase):
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
            str(item["id"]) for item in lane.WAVE8_BANNOCK_SHEEPEATER_ENTITIES
        }
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane.install_wave8_bannock_sheepeater_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_bannock_sheepeater_contracts(
            self.hced,
            entities,
            existing,
        )

    def _is_integrated(self) -> bool:
        return (
            "accepted_wave8_bannock_sheepeater_hced_events"
            in self.release_metadata.get("promotion", {})
        )

    def test_complete_label_inventory_and_row_hashes_are_pinned(self) -> None:
        relevant = {
            str(row["candidate_id"]): row
            for row in self.hced
            if any(
                normalize_label(row.get(key))
                in {
                    "bannock indians",
                    "bannock indians peyoute indians",
                    "bannock indians shoshoni indians",
                }
                for key in ("side_1_raw", "side_2_raw")
            )
        }
        self.assertEqual(
            set(relevant), lane.WAVE8_BANNOCK_SHEEPEATER_EXPECTED_CANDIDATE_IDS
        )
        self.assertEqual(len(relevant), 5)
        for candidate_id, expected_hash in (
            lane.WAVE8_BANNOCK_SHEEPEATER_ROW_HASHES.items()
        ):
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(relevant[candidate_id]),
                    expected_hash,
                )

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_bannock_sheepeater_queue_contracts(self.hced),
            {
                "complete_bannock_label_rows": 5,
                "distinct_source_conflicts": 2,
                "holds": 3,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 5,
            },
        )
        if not self._is_integrated():
            self.assertEqual(
                lane.validate_wave8_bannock_sheepeater_funnel(self.funnel),
                {"events_touched": 5, "labels": 3, "sole_blocker_events": 5},
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"]
                ["wave8_bannock_sheepeater_exact_label_funnel_audit"],
                lane.WAVE8_BANNOCK_SHEEPEATER_FUNNEL_AUDIT,
            )

    def test_entities_are_exactly_bounded_and_open_no_generic_alias(self) -> None:
        entities = {
            str(item["id"]): item
            for item in lane.WAVE8_BANNOCK_SHEEPEATER_ENTITIES
        }
        self.assertEqual(set(entities), {BANNOCK, NORTHERN_PAIUTE, TUKUDEKA})
        self.assertEqual(
            (entities[BANNOCK]["start_year"], entities[BANNOCK]["end_year"]),
            (1878, 1878),
        )
        self.assertEqual(
            (
                entities[NORTHERN_PAIUTE]["start_year"],
                entities[NORTHERN_PAIUTE]["end_year"],
            ),
            (1878, 1878),
        )
        self.assertEqual(
            (entities[TUKUDEKA]["start_year"], entities[TUKUDEKA]["end_year"]),
            (1879, 1879),
        )
        for entity in entities.values():
            self.assertEqual(entity["aliases"], [])
            self.assertIn("No generic Bannock", entity["continuity_note"])
            Entity.from_dict(entity)

    def test_sources_parse_and_each_promotion_has_independent_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_BANNOCK_SHEEPEATER_SOURCES), 9)
        for source in lane.WAVE8_BANNOCK_SHEEPEATER_SOURCES:
            Source.from_dict(source)
        for candidate_id, contract in (
            lane.WAVE8_BANNOCK_SHEEPEATER_CONTRACTS.items()
        ):
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(len(contract["outcome_source_ids"]), 2)
                self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertLessEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])

    def test_only_birch_creek_and_vinegar_hill_promote(self) -> None:
        self.assertEqual(
            lane.WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS,
            {"hced-Birch Creek1878-1", "hced-Vinegar Hill, Idaho1879-1"},
        )
        self.assertEqual(
            lane.WAVE8_BANNOCK_SHEEPEATER_HOLD_IDS,
            {
                "hced-Battle Creek, Idaho1878-1",
                "hced-Pendleton1878-1",
                "hced-Silver Creek, Oregon1878-1",
            },
        )
        self.assertEqual(
            {event["hced_candidate_id"] for event in self._events()},
            lane.WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS,
        )

    def test_holds_preserve_unknowns_and_actor_conflicts(self) -> None:
        expected = {
            "hced-Battle Creek, Idaho1878-1": "source_outcome_contradiction",
            "hced-Pendleton1878-1": "coalition_identity_conflict",
            "hced-Silver Creek, Oregon1878-1": (
                "tactical_outcome_not_uniquely_defensible"
            ),
        }
        for candidate_id, category in expected.items():
            with self.subTest(candidate_id=candidate_id):
                hold = lane.WAVE8_BANNOCK_SHEEPEATER_HOLDS[candidate_id]
                self.assertEqual(hold["hold_category"], category)
                self.assertEqual(hold["result_type"], "unknown")
                self.assertIs(hold["unknown_is_never_draw"], True)
                self.assertNotIn("converted into a draw", hold["hold_reason"])
        self.assertIn(
            "spectators",
            lane.WAVE8_BANNOCK_SHEEPEATER_HOLDS["hced-Pendleton1878-1"]
            ["hold_reason"],
        )

    def test_promoted_events_lock_actors_dates_and_tactical_results(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        birch = events["hced-Birch Creek1878-1"]
        self.assertEqual(birch["name"], "Battle of Birch Creek")
        self.assertEqual((birch["year"], birch["end_year"]), (1878, 1878))
        self.assertEqual(
            {
                item["entity_id"]: item["termination"]
                for item in birch["participants"]
            },
            {
                UNITED_STATES: "engagement_victory",
                BANNOCK: "engagement_defeat",
                NORTHERN_PAIUTE: "engagement_defeat",
            },
        )

        vinegar = events["hced-Vinegar Hill, Idaho1879-1"]
        self.assertEqual(vinegar["name"], "Vinegar Hill action")
        self.assertEqual(
            (vinegar["year"], vinegar["end_year"]), (1879, 1879)
        )
        self.assertEqual(
            {
                item["entity_id"]: item["termination"]
                for item in vinegar["participants"]
            },
            {
                TUKUDEKA: "engagement_victory",
                UNITED_STATES: "engagement_defeat",
            },
        )
        for event in events.values():
            self.assertEqual(event["date_precision"], "day")
            self.assertEqual(event["war_type"], "colonial_anti_colonial")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            Event.from_dict(event)

    def test_mismatched_or_unverified_points_are_withheld(self) -> None:
        self.assertEqual(
            lane.WAVE8_BANNOCK_SHEEPEATER_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS,
        )
        self.assertFalse(
            lane.WAVE8_BANNOCK_SHEEPEATER_COUNTRY_QUARANTINE_ADDITIONS
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "United States")
            self.assertIn("location_provenance", event)

    def test_no_probable_cross_source_twins(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_bannock_sheepeater_integration_dispositions(
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
        lane.install_wave8_bannock_sheepeater_entities(entities)
        lane.install_wave8_bannock_sheepeater_entities(entities)
        self.assertEqual(len(entities), 3)
        entities[BANNOCK]["name"] = "drift"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_bannock_sheepeater_entities(entities)

        sources = {}
        lane.install_wave8_bannock_sheepeater_sources(sources)
        lane.install_wave8_bannock_sheepeater_sources(sources)
        self.assertEqual(len(sources), 9)
        first_id = str(lane.WAVE8_BANNOCK_SHEEPEATER_SOURCES[0]["id"])
        sources[first_id]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_bannock_sheepeater_sources(sources)

    def test_row_drift_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Birch Creek1878-1"
        )
        row["winner_raw"] = "Bannock Indians"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_bannock_sheepeater_queue_contracts(tampered)

        entities, existing = self._installed()
        existing.append(
            {
                "id": "duplicate",
                "name": "Battle of Birch Creek",
                "year": 1878,
                "participants": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_bannock_sheepeater_contracts(
                self.hced,
                entities,
                existing,
            )

    def test_signature_counts_and_cohort_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_bannock_sheepeater_audit_signature(),
            lane.WAVE8_BANNOCK_SHEEPEATER_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_bannock_sheepeater_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 3,
                "new_entities": 3,
                "new_sources": 9,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_bannock_sheepeater_cohort_counts(),
            {"bannock_and_sheepeater_exact_force_audit": 5},
        )

    def test_release_artifacts_are_preintegration_or_exactly_integrated(self) -> None:
        release_events = {
            str(row.get("hced_candidate_id")): row
            for row in self.release_events
            if row.get("hced_candidate_id")
            in lane.WAVE8_BANNOCK_SHEEPEATER_RESERVED_IDS
        }
        if not self._is_integrated():
            self.assertFalse(release_events)
            return

        self.assertEqual(
            set(release_events), lane.WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS
        )
        release_entity_ids = {str(row["id"]) for row in self.release_entities}
        self.assertLessEqual({BANNOCK, NORTHERN_PAIUTE, TUKUDEKA}, release_entity_ids)
        release_source_ids = {str(row["id"]) for row in self.release_sources}
        self.assertLessEqual(
            {str(row["id"]) for row in lane.WAVE8_BANNOCK_SHEEPEATER_SOURCES},
            release_source_ids,
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(
            promotion["accepted_wave8_bannock_sheepeater_hced_events"], 2
        )
        self.assertEqual(
            promotion["wave8_bannock_sheepeater_candidate_ids"],
            sorted(lane.WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS),
        )
        self.assertEqual(len(promotion["wave8_bannock_sheepeater_holds"]), 3)
        coverage = self.registry["coverage"]
        self.assertEqual(len(self.release_entities), 1_051)
        self.assertEqual(len(self.release_events), 5_466)
        self.assertEqual(len(self.registry["entities"]), 2_398)
        self.assertEqual(coverage["rated_entities"], 1_044)
        self.assertEqual(coverage["unresolved_event_candidates"], 36_877)
        location = coverage["hced_location_assertions"]
        self.assertEqual(location["hced_candidate_bindings"], 5_199)
        self.assertEqual(location["candidate_keyed_reviewed_contracts"], 828)
        self.assertEqual(location["geojson_points"], 4_803)
        self.assertEqual(location["modern_location_country_assertions"], 5_104)
        self.assertEqual(location["location_provenance_objects"], 5_153)
        self.assertEqual(location["point_fields_withheld_by_quarantine"], 396)
        self.assertEqual(location["unique_events_with_any_quarantined_field"], 444)


if __name__ == "__main__":
    unittest.main()
