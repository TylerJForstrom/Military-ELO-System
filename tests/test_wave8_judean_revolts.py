import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave8_judean_revolts import (
    WAVE8_JUDEAN_REVOLTS_CONTRACT_IDS,
    WAVE8_JUDEAN_REVOLTS_CONTRACTS,
    WAVE8_JUDEAN_REVOLTS_ENTITIES,
    WAVE8_JUDEAN_REVOLTS_FINAL_AUDIT_SIGNATURE,
    WAVE8_JUDEAN_REVOLTS_HOLD_IDS,
    WAVE8_JUDEAN_REVOLTS_HOLDS,
    WAVE8_JUDEAN_REVOLTS_RESERVED_IDS,
    WAVE8_JUDEAN_REVOLTS_SOURCES,
    install_wave8_judean_revolts_entities,
    promote_wave8_judean_revolts_contracts,
    validate_wave8_judean_revolts_queue_contracts,
    wave8_judean_revolts_counts,
    wave8_judean_revolts_signature,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text().splitlines() if line]


class Wave8JudeanRevoltsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows()
        cls.entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.events = _json(ROOT / "data" / "release" / "events.json")

    def test_inventory_signature_and_counts_are_pinned(self) -> None:
        self.assertEqual((len(WAVE8_JUDEAN_REVOLTS_CONTRACT_IDS), len(WAVE8_JUDEAN_REVOLTS_HOLD_IDS)), (2, 5))
        self.assertEqual(
            WAVE8_JUDEAN_REVOLTS_RESERVED_IDS,
            WAVE8_JUDEAN_REVOLTS_CONTRACT_IDS | WAVE8_JUDEAN_REVOLTS_HOLD_IDS,
        )
        self.assertEqual(
            wave8_judean_revolts_signature(),
            WAVE8_JUDEAN_REVOLTS_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_judean_revolts_counts(),
            {"holds": 5, "newly_rated_events": 2, "promotion_contracts": 2, "reviewed_hced_rows": 7},
        )

    def test_sources_and_identities_are_bounded_and_alias_free(self) -> None:
        self.assertEqual((len(WAVE8_JUDEAN_REVOLTS_ENTITIES), len(WAVE8_JUDEAN_REVOLTS_SOURCES)), (2, 5))
        for source in WAVE8_JUDEAN_REVOLTS_SOURCES:
            Source.from_dict(source)
        for entity in WAVE8_JUDEAN_REVOLTS_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertNotEqual(entity["name"].casefold(), "jewish rebels")

    def test_queue_hashes_fail_closed(self) -> None:
        self.assertEqual(
            validate_wave8_judean_revolts_queue_contracts(self.rows),
            {"promotion_contracts": 2, "holds": 5, "reviewed_hced_rows": 7},
        )
        changed = copy.deepcopy(self.rows)
        next(row for row in changed if row["candidate_id"] == "hced-Emmaus-166-1")["winner_raw"] = "Seleucid Empire"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_judean_revolts_queue_contracts(changed)

    def test_holds_preserve_date_and_granularity_uncertainty(self) -> None:
        self.assertEqual(
            WAVE8_JUDEAN_REVOLTS_HOLDS["hced-Aelia133-135-1"]["hold_category"],
            "campaign_or_massacre_not_distinct_engagement",
        )
        for candidate_id in (
            "hced-Beth Zachariah-164-1",
            "hced-Beth Zur-166-1",
            "hced-Elasa-161-1",
        ):
            self.assertEqual(
                WAVE8_JUDEAN_REVOLTS_HOLDS[candidate_id]["hold_category"],
                "source_date_conflict",
            )
        self.assertEqual(
            WAVE8_JUDEAN_REVOLTS_HOLDS["hced-Gophna-166-1"]["hold_category"],
            "distinct_engagement_unverified",
        )

    def test_two_exact_events_emit_with_distinct_revolt_identities(self) -> None:
        entities = {entity["id"]: entity for entity in self.entities}
        install_wave8_judean_revolts_entities(entities)
        existing = [
            event
            for event in self.events
            if event.get("hced_candidate_id") not in WAVE8_JUDEAN_REVOLTS_CONTRACT_IDS
        ]
        emitted = promote_wave8_judean_revolts_contracts(self.rows, entities, existing)
        self.assertEqual({event["hced_candidate_id"] for event in emitted}, WAVE8_JUDEAN_REVOLTS_CONTRACT_IDS)
        by_id = {event["hced_candidate_id"]: event for event in emitted}
        for event in emitted:
            Event.from_dict(event)
            winners = {
                p["entity_id"]
                for p in event["participants"]
                if p["termination"] == "engagement_victory"
            }
            losers = {
                p["entity_id"]
                for p in event["participants"]
                if p["termination"] == "engagement_defeat"
            }
            self.assertNotIn("jewish_rebels", winners | losers)
        self.assertEqual(
            {
                p["entity_id"]
                for p in by_id["hced-Beth Horon66-1"]["participants"]
                if p["termination"] == "engagement_victory"
            },
            {"great_jewish_revolt_judean_forces_66_73"},
        )
        self.assertEqual(
            {
                p["entity_id"]
                for p in by_id["hced-Emmaus-166-1"]["participants"]
                if p["termination"] == "engagement_victory"
            },
            {"maccabean_revolt_judean_forces_167_160_bce"},
        )

    def test_contract_outcomes_are_directly_sourced_not_reversed(self) -> None:
        source_by_id = {source["id"]: source for source in WAVE8_JUDEAN_REVOLTS_SOURCES}
        for contract in WAVE8_JUDEAN_REVOLTS_CONTRACTS.values():
            self.assertFalse(contract["source_outcome_override"])
            self.assertTrue(contract["outcome_source_ids"])
            self.assertTrue(
                all(
                    "outcome" in source_by_id[source_id]["evidence_roles"]
                    for source_id in contract["outcome_source_ids"]
                )
            )


if __name__ == "__main__":
    unittest.main()
