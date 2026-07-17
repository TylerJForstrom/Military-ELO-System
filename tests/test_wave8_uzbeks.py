import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_uzbeks as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_PREFIX = "hced_wave8_uzbeks_"
SHAYBANI = "clio_uz_shaybanid_k_1497_9cfc6dff"
ABDULLAH = "abdullah_ii_abul_khayrid_khanate_1583_1598"
SAFAVID = "safavid_empire"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8UzbeksTests(unittest.TestCase):
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

    def _is_integrated(self) -> bool:
        return (
            "accepted_wave8_uzbeks_hced_events"
            in self.release_metadata.get("promotion", {})
        )

    def _installed(self):
        lane_entity_ids = {str(item["id"]) for item in lane.WAVE8_UZBEKS_ENTITIES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane.install_wave8_uzbeks_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_UZBEKS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_uzbeks_contracts(self.hced, entities, existing)

    def test_complete_literal_label_inventory_and_hashes_are_pinned(self) -> None:
        relevant = {
            str(row["candidate_id"]): row
            for row in self.hced
            if any(
                normalize_label(row.get(key)) == "uzbeks"
                for key in ("side_1_raw", "side_2_raw")
            )
        }
        self.assertEqual(set(relevant), lane.WAVE8_UZBEKS_RESERVED_IDS)
        self.assertEqual(len(relevant), 6)
        for candidate_id, expected in lane.WAVE8_UZBEKS_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(canonical_hced_row_sha256(relevant[candidate_id]), expected)

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_uzbeks_queue_contracts(self.hced),
            {
                "exact_label_rows": 6,
                "holds": 1,
                "promotion_contracts": 5,
                "reviewed_hced_rows": 6,
            },
        )
        if self._is_integrated():
            self.assertEqual(
                self.release_metadata["promotion"][
                    "wave8_uzbeks_exact_label_funnel_audit"
                ],
                lane.WAVE8_UZBEKS_FUNNEL_AUDIT,
            )
        else:
            self.assertEqual(
                lane.validate_wave8_uzbeks_funnel(self.funnel),
                {
                    "events_touched": 6,
                    "sole_blocker_events": 3,
                    "unresolved_side_attempts": 6,
                    "zero_time_valid_candidates": 6,
                },
            )

    def test_entities_are_time_bounded_and_open_no_generic_alias(self) -> None:
        entities = {str(item["id"]): item for item in lane.WAVE8_UZBEKS_ENTITIES}
        self.assertEqual(len(entities), 7)
        self.assertEqual(
            (entities[SHAYBANI]["start_year"], entities[SHAYBANI]["end_year"]),
            (1500, 1510),
        )
        self.assertEqual(
            (entities[ABDULLAH]["start_year"], entities[ABDULLAH]["end_year"]),
            (1583, 1598),
        )
        for entity in entities.values():
            self.assertEqual(entity["aliases"], [])
            self.assertNotIn(
                normalize_label(entity["name"]),
                {"uzbek", "uzbeks", "uzbekistan"},
            )
            Entity.from_dict(entity)

    def test_sources_parse_and_each_promotion_has_two_outcome_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_UZBEKS_SOURCES), 7)
        for source in lane.WAVE8_UZBEKS_SOURCES:
            Source.from_dict(source)
        for candidate_id, contract in lane.WAVE8_UZBEKS_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
                self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertLessEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )

    def test_five_events_promote_with_reviewed_names_and_ranges(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_UZBEKS_CONTRACT_IDS)
        self.assertEqual(
            {
                candidate_id: (
                    event["name"],
                    event["year"],
                    event["end_year"],
                    event["reviewed_granularity"],
                )
                for candidate_id, event in events.items()
            },
            {
                "hced-Akhsikath1503-1": (
                    "Battle of Akhsi (Archiyan)",
                    1503,
                    1503,
                    "pitched_battle",
                ),
                "hced-Herat1507-1": (
                    "Capture of the Herat citadel",
                    1507,
                    1507,
                    "siege_and_capitulation",
                ),
                "hced-Herat1528-1": (
                    "Relief of the siege of Herat",
                    1528,
                    1528,
                    "siege_relief",
                ),
                "hced-Herat1588-1": (
                    "Abu'l-Khayrid siege and capture of Herat",
                    1587,
                    1589,
                    "siege",
                ),
                "hced-Merv1510-1": (
                    "Battle of Mahmudi near Merv",
                    1510,
                    1510,
                    "pitched_battle",
                ),
            },
        )
        for event in events.values():
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["war_type"], "interstate_limited")
            Event.from_dict(event)

    def test_actor_corrections_are_explicit_and_tactical(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}

        def outcomes(candidate_id):
            return {
                item["entity_id"]: item["termination"]
                for item in events[candidate_id]["participants"]
            }

        self.assertEqual(
            outcomes("hced-Merv1510-1"),
            {SAFAVID: "engagement_victory", SHAYBANI: "engagement_defeat"},
        )
        self.assertEqual(
            outcomes("hced-Herat1588-1"),
            {ABDULLAH: "engagement_victory", SAFAVID: "engagement_defeat"},
        )
        self.assertEqual(len(outcomes("hced-Akhsikath1503-1")), 4)
        self.assertEqual(
            outcomes("hced-Akhsikath1503-1")[SHAYBANI], "engagement_victory"
        )

    def test_samarkand_is_held_not_reversed_or_drawn(self) -> None:
        self.assertEqual(
            lane.WAVE8_UZBEKS_HOLD_IDS,
            {"hced-Samarkand1497-1498-1"},
        )
        hold = lane.WAVE8_UZBEKS_HOLDS["hced-Samarkand1497-1498-1"]
        self.assertEqual(hold["hold_category"], "wrong_actors_and_reversed_outcome")
        self.assertNotIn("hced-Samarkand1497-1498-1", lane.WAVE8_UZBEKS_CONTRACTS)

    def test_all_five_points_are_quarantined_but_countries_remain(self) -> None:
        self.assertEqual(
            lane.WAVE8_UZBEKS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_UZBEKS_CONTRACT_IDS,
        )
        self.assertEqual(lane.WAVE8_UZBEKS_COUNTRY_QUARANTINE_ADDITIONS, set())
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertIn("modern_location_country", event)
            self.assertIn("location_provenance", event)

    def test_related_rows_and_duplicate_surfaces_are_reviewed(self) -> None:
        result = lane.validate_wave8_uzbeks_integration_dispositions(
            self.hced,
            self.iwbd,
            self.release_events,
        )
        self.assertEqual(result["related_hced_dispositions"], 3)
        self.assertEqual(result["iwbd_zero_overlap_candidates"], 6)
        self.assertIn(
            result["release_lane_events"],
            {0, len(lane.WAVE8_UZBEKS_CONTRACT_IDS)},
        )

    def test_signature_and_metadata_pin_the_complete_audit(self) -> None:
        self.assertNotIn(
            lane.WAVE8_UZBEKS_FINAL_AUDIT_SIGNATURE,
            {"", "TO_BE_PINNED", "__PENDING__"},
        )
        self.assertEqual(
            lane.wave8_uzbeks_audit_signature(),
            lane.WAVE8_UZBEKS_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_uzbeks_metadata()["row_dispositions"],
            {
                candidate_id: (
                    "promote"
                    if candidate_id in lane.WAVE8_UZBEKS_CONTRACT_IDS
                    else "hold"
                )
                for candidate_id in sorted(lane.WAVE8_UZBEKS_RESERVED_IDS)
            },
        )

    def test_integrated_release_matches_lane_when_present(self) -> None:
        if not self._is_integrated():
            self.skipTest("audit-only commit has not integrated this lane yet")
        events = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_UZBEKS_CONTRACT_IDS
        ]
        self.assertEqual(len(events), 5)
        self.assertEqual(
            self.release_metadata["promotion"]["accepted_wave8_uzbeks_hced_events"],
            5,
        )
        release_entity_ids = {str(item["id"]) for item in self.release_entities}
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_UZBEKS_ENTITIES},
            release_entity_ids,
        )
        release_source_ids = {str(item["id"]) for item in self.release_sources}
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_UZBEKS_SOURCES},
            release_source_ids,
        )
        registry_ids = {str(item["id"]) for item in self.registry}
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_UZBEKS_ENTITIES},
            registry_ids,
        )


if __name__ == "__main__":
    unittest.main()
