import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_spanish_liberals as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_PREFIX = "hced_wave8_spanish_liberals_"
ISABELINE = "isabeline_government_forces_first_carlist_war"
CARLIST = "carlist_army_first_war"

EXPECTED_HASHES = {
    "hced-Alegria1834-1": (
        "5643b7e99363ca42123a63f29efc2d24b7293dd3b85d589b61ba614042a2a9c8"
    ),
    "hced-Artaza1834-1": (
        "cd81f724365721250146a3c770797d27784a79b18a9381d3e770cf739db1dc79"
    ),
    "hced-Asarta1833-1": (
        "bd305efe2efa6c551c7c6950bac089f478c4f689a6acae330e0e0d458ac07ddc"
    ),
    "hced-Gulina1834-1": (
        "e67d3a294b116ddcf267b1bcd35aaf44cc63a44f478fdc3305f4dd55a3ad038e"
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


class Wave8SpanishLiberalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        lane_entity_ids = {
            str(item["id"]) for item in lane.WAVE8_SPANISH_LIBERALS_ENTITIES
        }
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_SPANISH_LIBERALS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        lane.install_wave8_spanish_liberals_entities(entities)
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_spanish_liberals_contracts(
            self.hced, entities, existing
        )

    def test_exact_inventory_and_row_hashes_are_pinned(self) -> None:
        self.assertEqual(lane.WAVE8_SPANISH_LIBERALS_ROW_HASHES, EXPECTED_HASHES)
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
            lane.validate_wave8_spanish_liberals_queue_contracts(self.hced),
            {
                "exact_label_rows": 4,
                "holds": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
            },
        )
        historical = {
            "labels": [
                {
                    "candidate_ids": [],
                    "event_candidate_id_sha256": (
                        "935b85664b28e3be3f7262bb8fa3e72877b51169a4c11c7aa055409029005838"
                    ),
                    "events_touched": 4,
                    "failure_cases": {"zero_time_valid_candidates": 4},
                    "label": "spanish liberals",
                    "sole_blocker_events": 3,
                }
            ]
        }
        self.assertEqual(
            lane.validate_wave8_spanish_liberals_funnel(historical),
            {
                "events_touched": 4,
                "sole_blocker_events": 3,
                "zero_time_valid_candidates": 4,
            },
        )
        live = [
            row
            for row in self.funnel.get("labels", [])
            if row.get("label") == "spanish liberals"
        ]
        if live:
            lane.validate_wave8_spanish_liberals_funnel(self.funnel)

    def test_two_promotions_and_two_source_critical_holds_partition_the_lane(self) -> None:
        self.assertEqual(
            lane.WAVE8_SPANISH_LIBERALS_CONTRACT_IDS,
            {"hced-Alegria1834-1", "hced-Gulina1834-1"},
        )
        self.assertEqual(
            lane.WAVE8_SPANISH_LIBERALS_HOLD_IDS,
            {"hced-Artaza1834-1", "hced-Asarta1833-1"},
        )
        self.assertEqual(
            lane.WAVE8_SPANISH_LIBERALS_RESERVED_IDS, set(EXPECTED_HASHES)
        )
        self.assertEqual(
            lane.WAVE8_SPANISH_LIBERALS_HOLDS["hced-Artaza1834-1"]["reason_code"],
            "locked_year_conflicts_with_attested_action",
        )
        self.assertEqual(
            lane.WAVE8_SPANISH_LIBERALS_HOLDS["hced-Asarta1833-1"]["reason_code"],
            "locked_winner_conflicts_with_tactical_record",
        )

    def test_sources_parse_and_each_promotion_has_two_independent_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_SPANISH_LIBERALS_SOURCES), 7)
        for source in lane.WAVE8_SPANISH_LIBERALS_SOURCES:
            Source.from_dict(source)
        for contract in lane.WAVE8_SPANISH_LIBERALS_CONTRACTS.values():
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(set(contract["outcome_source_family_ids"])),
            )

    def test_isabeline_identity_is_conflict_bounded_and_has_no_alias(self) -> None:
        self.assertEqual(len(lane.WAVE8_SPANISH_LIBERALS_ENTITIES), 1)
        entity = lane.WAVE8_SPANISH_LIBERALS_ENTITIES[0]
        self.assertEqual(entity["id"], ISABELINE)
        self.assertEqual((entity["start_year"], entity["end_year"]), (1833, 1840))
        self.assertEqual(entity["aliases"], [])
        self.assertIn("Only fingerprinted candidate-keyed contracts", entity["continuity_note"])
        Entity.from_dict(entity)

    def test_promotions_retain_locked_outcomes_without_override_or_draw(self) -> None:
        for contract in lane.WAVE8_SPANISH_LIBERALS_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_SPANISH_LIBERALS_CONTRACT_IDS)
        expected = {
            "hced-Alegria1834-1": (CARLIST, ISABELINE),
            "hced-Gulina1834-1": (ISABELINE, CARLIST),
        }
        for candidate_id, (winner, loser) in expected.items():
            event = events[candidate_id]
            outcomes = {p["entity_id"]: p["termination"] for p in event["participants"]}
            self.assertEqual(outcomes[winner], "engagement_victory")
            self.assertEqual(outcomes[loser], "engagement_defeat")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            Event.from_dict(event)

    def test_canonical_dates_are_day_precise_and_holds_emit_nothing(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(events["hced-Alegria1834-1"]["name"], "Battle of Alegría de Álava")
        self.assertEqual(events["hced-Gulina1834-1"]["name"], "Battle of Gulina")
        self.assertTrue(all(event["date_precision"] == "day" for event in events.values()))
        self.assertFalse(set(events) & lane.WAVE8_SPANISH_LIBERALS_HOLD_IDS)

    def test_points_are_withheld_and_reviewed_country_is_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_SPANISH_LIBERALS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_SPANISH_LIBERALS_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_SPANISH_LIBERALS_COUNTRY_QUARANTINE_ADDITIONS)
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Spain")
            self.assertIn("location_provenance", event)

    def test_no_probable_cross_source_twins_exist(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_spanish_liberals_integration_dispositions(
                self.hced, self.iwbd, existing
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_row_drift_fails_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item for item in tampered if item.get("candidate_id") == "hced-Gulina1834-1"
        )
        row["winner_raw"] = "Carlists"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_spanish_liberals_queue_contracts(tampered)

    def test_counts_and_final_signature_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_spanish_liberals_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 2,
                "new_entities": 1,
                "new_sources": 7,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_spanish_liberals_audit_signature(),
            "3d259d1dcd15f760474a546d217970f8129a84c0afd29d3d587fa7cbe274a101",
        )
        self.assertEqual(
            lane.wave8_spanish_liberals_audit_signature(),
            lane.WAVE8_SPANISH_LIBERALS_FINAL_AUDIT_SIGNATURE,
        )


if __name__ == "__main__":
    unittest.main()
