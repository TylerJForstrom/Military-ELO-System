import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave8_first_saudi import (
    WAVE8_FIRST_SAUDI_CONTRACT_IDS,
    WAVE8_FIRST_SAUDI_CONTRACTS,
    WAVE8_FIRST_SAUDI_ENTITIES,
    WAVE8_FIRST_SAUDI_FINAL_AUDIT_SIGNATURE,
    WAVE8_FIRST_SAUDI_HOLD_IDS,
    WAVE8_FIRST_SAUDI_HOLDS,
    WAVE8_FIRST_SAUDI_RESERVED_IDS,
    WAVE8_FIRST_SAUDI_SOURCES,
    install_wave8_first_saudi_entities,
    promote_wave8_first_saudi_contracts,
    validate_wave8_first_saudi_queue_contracts,
    wave8_first_saudi_counts,
    wave8_first_saudi_signature,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text().splitlines() if line]


class Wave8FirstSaudiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows()
        cls.entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.events = _json(ROOT / "data" / "release" / "events.json")

    def test_inventory_signature_and_counts_are_pinned(self) -> None:
        self.assertEqual(len(WAVE8_FIRST_SAUDI_CONTRACT_IDS), 1)
        self.assertEqual(len(WAVE8_FIRST_SAUDI_HOLD_IDS), 5)
        self.assertEqual(
            WAVE8_FIRST_SAUDI_RESERVED_IDS,
            WAVE8_FIRST_SAUDI_CONTRACT_IDS | WAVE8_FIRST_SAUDI_HOLD_IDS,
        )
        self.assertEqual(
            wave8_first_saudi_signature(),
            WAVE8_FIRST_SAUDI_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_first_saudi_counts(),
            {
                "holds": 5,
                "newly_rated_events": 1,
                "promotion_contracts": 1,
                "reviewed_hced_rows": 6,
            },
        )

    def test_sources_and_identity_parse_without_generic_alias(self) -> None:
        self.assertEqual((len(WAVE8_FIRST_SAUDI_ENTITIES), len(WAVE8_FIRST_SAUDI_SOURCES)), (1, 3))
        for source in WAVE8_FIRST_SAUDI_SOURCES:
            Source.from_dict(source)
        entity = WAVE8_FIRST_SAUDI_ENTITIES[0]
        Entity.from_dict(entity)
        self.assertEqual(entity["id"], "first_saudi_state")
        self.assertEqual((entity["start_year"], entity["end_year"]), (1727, 1818))
        self.assertEqual(entity["aliases"], [])
        self.assertNotIn("House of Saud", entity["aliases"])

    def test_queue_contracts_fail_closed_on_drift(self) -> None:
        self.assertEqual(
            validate_wave8_first_saudi_queue_contracts(self.rows),
            {"promotion_contracts": 1, "holds": 5, "reviewed_hced_rows": 6},
        )
        changed = copy.deepcopy(self.rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Diriyah1818-1"
        )["winner_raw"] = "House of Saud"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_first_saudi_queue_contracts(changed)

    def test_holds_preserve_unknown_or_noncompetitive_records(self) -> None:
        self.assertEqual(
            WAVE8_FIRST_SAUDI_HOLDS["hced-Al Safra1812-1"]["hold_category"],
            "source_date_conflict",
        )
        self.assertEqual(
            WAVE8_FIRST_SAUDI_HOLDS["hced-Medina1812-1"]["hold_category"],
            "outcome_mechanism_disputed",
        )
        self.assertEqual(
            WAVE8_FIRST_SAUDI_HOLDS["hced-Nejd1817-1"]["hold_category"],
            "missing_event_date",
        )
        for candidate_id in ("hced-Jeddah1813-1", "hced-Mecca1813-1"):
            self.assertEqual(
                WAVE8_FIRST_SAUDI_HOLDS[candidate_id]["hold_category"],
                "noncompetitive_occupation",
            )

    def test_diriyah_credits_the_egyptian_field_army(self) -> None:
        entities = {entity["id"]: entity for entity in self.entities}
        install_wave8_first_saudi_entities(entities)
        existing = [
            event
            for event in self.events
            if event.get("hced_candidate_id") not in WAVE8_FIRST_SAUDI_CONTRACT_IDS
        ]
        emitted = promote_wave8_first_saudi_contracts(self.rows, entities, existing)
        self.assertEqual(len(emitted), 1)
        event = emitted[0]
        Event.from_dict(event)
        self.assertEqual(event["name"], "Siege of Diriyah")
        self.assertEqual(event["hced_candidate_id"], "hced-Diriyah1818-1")
        winners = {
            participant["entity_id"]
            for participant in event["participants"]
            if participant["termination"] == "engagement_victory"
        }
        losers = {
            participant["entity_id"]
            for participant in event["participants"]
            if participant["termination"] == "engagement_defeat"
        }
        self.assertEqual(winners, {"egypt_muhammad_ali"})
        self.assertEqual(losers, {"first_saudi_state"})
        self.assertNotIn("ottoman_empire", winners | losers)
        self.assertEqual(
            event["outcome_source_ids"],
            ["wave8_first_saudi_abdullah_diriyah"],
        )

    def test_only_diriyah_can_emit(self) -> None:
        self.assertEqual(set(WAVE8_FIRST_SAUDI_CONTRACTS), {"hced-Diriyah1818-1"})
        self.assertFalse(WAVE8_FIRST_SAUDI_HOLD_IDS & WAVE8_FIRST_SAUDI_CONTRACT_IDS)


if __name__ == "__main__":
    unittest.main()
