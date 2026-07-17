import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave8_canadian_resistance import (
    WAVE8_CANADIAN_RESISTANCE_CONTRACT_IDS,
    WAVE8_CANADIAN_RESISTANCE_CONTRACTS,
    WAVE8_CANADIAN_RESISTANCE_ENTITIES,
    WAVE8_CANADIAN_RESISTANCE_FINAL_AUDIT_SIGNATURE,
    WAVE8_CANADIAN_RESISTANCE_HOLD_IDS,
    WAVE8_CANADIAN_RESISTANCE_HOLDS,
    WAVE8_CANADIAN_RESISTANCE_RESERVED_IDS,
    WAVE8_CANADIAN_RESISTANCE_SOURCES,
    install_wave8_canadian_resistance_entities,
    promote_wave8_canadian_resistance_contracts,
    validate_wave8_canadian_resistance_queue_contracts,
    wave8_canadian_resistance_counts,
    wave8_canadian_resistance_signature,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class Wave8CanadianResistanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows()
        cls.entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.events = _json(ROOT / "data" / "release" / "events.json")

    def test_inventory_signature_and_counts_are_pinned(self) -> None:
        self.assertEqual((len(WAVE8_CANADIAN_RESISTANCE_CONTRACT_IDS), len(WAVE8_CANADIAN_RESISTANCE_HOLD_IDS)), (3, 3))
        self.assertEqual(
            WAVE8_CANADIAN_RESISTANCE_RESERVED_IDS,
            WAVE8_CANADIAN_RESISTANCE_CONTRACT_IDS | WAVE8_CANADIAN_RESISTANCE_HOLD_IDS,
        )
        self.assertEqual(
            wave8_canadian_resistance_signature(),
            WAVE8_CANADIAN_RESISTANCE_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_canadian_resistance_counts(),
            {"holds": 3, "newly_rated_events": 3, "promotion_contracts": 3, "reviewed_hced_rows": 6},
        )

    def test_sources_and_six_identities_are_bounded_alias_free(self) -> None:
        self.assertEqual((len(WAVE8_CANADIAN_RESISTANCE_ENTITIES), len(WAVE8_CANADIAN_RESISTANCE_SOURCES)), (6, 6))
        for source in WAVE8_CANADIAN_RESISTANCE_SOURCES:
            Source.from_dict(source)
        for entity in WAVE8_CANADIAN_RESISTANCE_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertNotEqual(entity["name"].casefold(), "canadian rebels")

    def test_queue_hashes_fail_closed(self) -> None:
        self.assertEqual(
            validate_wave8_canadian_resistance_queue_contracts(self.rows),
            {"promotion_contracts": 3, "holds": 3, "reviewed_hced_rows": 6},
        )
        changed = copy.deepcopy(self.rows)
        next(row for row in changed if row["candidate_id"] == "hced-Duck Lake1885-1")["winner_raw"] = "United Kingdom"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_canadian_resistance_queue_contracts(changed)

    def test_three_uncertain_rows_are_explicit_holds(self) -> None:
        self.assertEqual(
            WAVE8_CANADIAN_RESISTANCE_HOLDS["hced-Battleford1885-1"]["hold_category"],
            "distinct_competitive_engagement_unverified",
        )
        self.assertEqual(
            WAVE8_CANADIAN_RESISTANCE_HOLDS["hced-Fish Creek1885-1"]["hold_category"],
            "contradictory_outcome_evidence",
        )
        self.assertEqual(
            WAVE8_CANADIAN_RESISTANCE_HOLDS["hced-Frenchmans Butte1885-1"]["hold_category"],
            "outcome_not_supported_as_victory",
        )

    def test_exact_events_replace_british_and_rebel_umbrellas(self) -> None:
        entities = {entity["id"]: entity for entity in self.entities}
        install_wave8_canadian_resistance_entities(entities)
        existing = [event for event in self.events if event.get("hced_candidate_id") not in WAVE8_CANADIAN_RESISTANCE_CONTRACT_IDS]
        emitted = promote_wave8_canadian_resistance_contracts(self.rows, entities, existing)
        self.assertEqual({event["hced_candidate_id"] for event in emitted}, WAVE8_CANADIAN_RESISTANCE_CONTRACT_IDS)
        by_id = {event["hced_candidate_id"]: event for event in emitted}
        for event in emitted:
            Event.from_dict(event)
            participant_ids = {p["entity_id"] for p in event["participants"]}
            self.assertNotIn("united_kingdom", participant_ids)
            self.assertNotIn("canadian_rebels", participant_ids)
        batoche_losers = {
            p["entity_id"]
            for p in by_id["hced-Batoche1885-1"]["participants"]
            if p["termination"] == "engagement_defeat"
        }
        self.assertEqual(
            batoche_losers,
            {
                "batoche_first_nations_allied_defenders_1885",
                "metis_provisional_government_saskatchewan_1885",
            },
        )
        duck_winners = {
            p["entity_id"]
            for p in by_id["hced-Duck Lake1885-1"]["participants"]
            if p["termination"] == "engagement_victory"
        }
        self.assertEqual(
            duck_winners,
            {
                "duck_lake_first_nations_allied_force_1885",
                "metis_provisional_government_saskatchewan_1885",
            },
        )

    def test_no_outcome_is_reversed_to_grow_the_lane(self) -> None:
        for contract in WAVE8_CANADIAN_RESISTANCE_CONTRACTS.values():
            self.assertFalse(contract["source_outcome_override"])
            self.assertTrue(contract["outcome_source_ids"])


if __name__ == "__main__":
    unittest.main()
