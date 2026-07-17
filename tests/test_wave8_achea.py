import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_achea as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_PREFIX = "hced_wave8_achea_"
ACHAEAN = "clio_q244796_bce279_0be1ca53"
SPARTA = "sparta"

EXPECTED_HASHES = {
    "hced-Ladoceia-227-1": (
        "23092227dcae3210d2243a74b8eba96675ac51ee49b7e8809eaaad436a6ccd7e"
    ),
    "hced-Mantinea-207-1": (
        "2d4412bf39ab55704cf03db9689900b6edb353fe95dd35ea936d3d6deb448c51"
    ),
    "hced-Mount Barbosthene-192-1": (
        "504f679e2d700f5f99813c787f6fb72bb581ca07e8020f182e204efab2b39171"
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


class Wave8AcheaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_ACHEA_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        before = copy.deepcopy(entities)
        lane.install_wave8_achea_entities(entities)
        self.assertEqual(entities, before)
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_achea_contracts(self.hced, entities, existing)

    def test_exact_inventory_and_row_hashes_are_pinned(self) -> None:
        self.assertEqual(lane.WAVE8_ACHEA_ROW_HASHES, EXPECTED_HASHES)
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if str(row.get("candidate_id")) in EXPECTED_HASHES
        }
        self.assertEqual(set(rows), set(EXPECTED_HASHES))
        for candidate_id, expected in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(canonical_hced_row_sha256(rows[candidate_id]), expected)
                self.assertIs(rows[candidate_id]["winner_loser_complete"], True)
                self.assertEqual(rows[candidate_id]["massacre_raw"], "No")

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_achea_queue_contracts(self.hced),
            {
                "exact_label_rows": 3,
                "holds": 0,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 3,
            },
        )
        historical = {
            "labels": [
                {
                    "candidate_ids": [],
                    "event_candidate_id_sha256": (
                        "38f02d97127f467d00b055bd789b10ba4b1fe93c29b00e5e81b3be87b86aa657"
                    ),
                    "events_touched": 3,
                    "failure_cases": {"zero_time_valid_candidates": 3},
                    "label": "achea",
                    "sole_blocker_events": 3,
                }
            ]
        }
        self.assertEqual(
            lane.validate_wave8_achea_funnel(historical),
            {
                "events_touched": 3,
                "sole_blocker_events": 3,
                "zero_time_valid_candidates": 3,
            },
        )
        live = [
            row for row in self.funnel.get("labels", []) if row.get("label") == "achea"
        ]
        if live:
            lane.validate_wave8_achea_funnel(self.funnel)

    def test_all_three_rows_promote_without_holds_or_new_identity(self) -> None:
        self.assertEqual(lane.WAVE8_ACHEA_CONTRACT_IDS, set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_ACHEA_RESERVED_IDS, set(EXPECTED_HASHES))
        self.assertFalse(lane.WAVE8_ACHEA_HOLDS)
        self.assertFalse(lane.WAVE8_ACHEA_ENTITIES)

    def test_sources_parse_and_each_event_has_two_source_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_ACHEA_SOURCES), 5)
        for source in lane.WAVE8_ACHEA_SOURCES:
            Source.from_dict(source)
        for contract in lane.WAVE8_ACHEA_CONTRACTS.values():
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(set(contract["outcome_source_family_ids"])),
            )

    def test_existing_achaean_identity_is_time_bounded_without_achea_alias(self) -> None:
        entities = {str(item["id"]): item for item in self.release_entities}
        entity = entities[ACHAEAN]
        self.assertEqual(entity["name"], "Achaean League")
        self.assertEqual((entity["start_year"], entity["end_year"]), (-279, -145))
        self.assertNotIn("Achea", entity["aliases"])
        Entity.from_dict(entity)

    def test_promotions_retain_all_three_locked_tactical_outcomes(self) -> None:
        for contract in lane.WAVE8_ACHEA_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        expected = {
            "hced-Ladoceia-227-1": (SPARTA, ACHAEAN),
            "hced-Mantinea-207-1": (ACHAEAN, SPARTA),
            "hced-Mount Barbosthene-192-1": (ACHAEAN, SPARTA),
        }
        self.assertEqual(set(events), set(expected))
        for candidate_id, (winner, loser) in expected.items():
            event = events[candidate_id]
            outcomes = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(outcomes[winner], "engagement_victory")
            self.assertEqual(outcomes[loser], "engagement_defeat")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            Event.from_dict(event)

    def test_canonical_names_are_distinct_and_year_precise(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(events["hced-Ladoceia-227-1"]["name"], "Battle of Ladoceia")
        self.assertEqual(
            events["hced-Mantinea-207-1"]["name"],
            "Battle of Mantinea (207 BCE)",
        )
        self.assertEqual(
            events["hced-Mount Barbosthene-192-1"]["name"],
            "Battle near Mount Barbosthenes",
        )
        self.assertTrue(all(event["date_precision"] == "year" for event in events.values()))
        self.assertEqual(len({event["canonical_event_key"] for event in events.values()}), 3)

    def test_points_are_withheld_and_greece_is_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_ACHEA_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_ACHEA_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_ACHEA_COUNTRY_QUARANTINE_ADDITIONS)
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Greece")
            self.assertIn("location_provenance", event)

    def test_no_probable_cross_source_twins_exist(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_achea_integration_dispositions(
                self.hced, self.iwbd, existing
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_row_drift_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Mantinea-207-1"
        )
        row["winner_raw"] = "Sparta"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_achea_queue_contracts(tampered)

        entities, existing = self._installed()
        promoted = lane.promote_wave8_achea_contracts(self.hced, entities, existing)
        with self.assertRaisesRegex(ValueError, "already promoted"):
            lane.promote_wave8_achea_contracts(
                self.hced,
                entities,
                [*existing, *promoted],
            )

    def test_counts_signature_and_source_install_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_achea_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 0,
                "new_entities": 0,
                "new_sources": 5,
                "newly_rated_events": 3,
                "outcome_overrides": 0,
                "point_quarantine_additions": 3,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_achea_audit_signature(),
            "54a097ca2b6d7b7ce28d68ad6eecf0a5692903f777137f1c53257af176a62291",
        )
        self.assertEqual(
            lane.wave8_achea_audit_signature(),
            lane.WAVE8_ACHEA_FINAL_AUDIT_SIGNATURE,
        )
        source_ids = {str(source["id"]) for source in lane.WAVE8_ACHEA_SOURCES}
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in source_ids
        }
        lane.install_wave8_achea_sources(sources)
        once = copy.deepcopy(sources)
        lane.install_wave8_achea_sources(sources)
        self.assertEqual(sources, once)
        self.assertLessEqual(source_ids, set(sources))


if __name__ == "__main__":
    unittest.main()
