import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave8_north_america import (
    WAVE8_NORTH_AMERICA_CONTRACT_IDS,
    WAVE8_NORTH_AMERICA_CONTRACTS,
    WAVE8_NORTH_AMERICA_ENTITIES,
    WAVE8_NORTH_AMERICA_FINAL_AUDIT_SIGNATURE,
    WAVE8_NORTH_AMERICA_HOLD_IDS,
    WAVE8_NORTH_AMERICA_HOLDS,
    WAVE8_NORTH_AMERICA_RESERVED_IDS,
    WAVE8_NORTH_AMERICA_SOURCES,
    install_wave8_north_america_entities,
    promote_wave8_north_america_contracts,
    validate_wave8_north_america_queue_contracts,
    wave8_north_america_cohort_counts,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class Wave8NorthAmericaTests(unittest.TestCase):
    def test_inventory_signature_and_cohorts_are_exact(self) -> None:
        self.assertEqual((len(WAVE8_NORTH_AMERICA_CONTRACT_IDS), len(WAVE8_NORTH_AMERICA_HOLD_IDS)), (22, 15))
        self.assertEqual(WAVE8_NORTH_AMERICA_RESERVED_IDS, WAVE8_NORTH_AMERICA_CONTRACT_IDS | WAVE8_NORTH_AMERICA_HOLD_IDS)
        lines = []
        for disposition, inventory in (("promote", WAVE8_NORTH_AMERICA_CONTRACTS), ("hold", WAVE8_NORTH_AMERICA_HOLDS)):
            for candidate_id, contract in sorted(inventory.items()):
                lines.append(f"{disposition}|{candidate_id}|{contract['raw_row_sha256']}|{contract['canonical_event']['canonical_key']}")
        self.assertEqual(hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest(), WAVE8_NORTH_AMERICA_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(sum(wave8_north_america_cohort_counts().values()), 22)

    def test_entities_sources_and_queue_contracts_validate(self) -> None:
        self.assertEqual((len(WAVE8_NORTH_AMERICA_ENTITIES), len(WAVE8_NORTH_AMERICA_SOURCES)), (11, 15))
        for entity in WAVE8_NORTH_AMERICA_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
        for source in WAVE8_NORTH_AMERICA_SOURCES:
            Source.from_dict(source)
        self.assertEqual(validate_wave8_north_america_queue_contracts(_rows()), {"promotion_contracts": 22, "holds": 15, "reviewed_hced_rows": 37})

    def test_queue_drift_fails_closed(self) -> None:
        changed = copy.deepcopy(_rows())
        next(row for row in changed if row["candidate_id"] == "hced-Tres Castillos1880-1")["winner_raw"] = "Mexico, Tarahumara Indians"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_north_america_queue_contracts(changed)

    def test_exact_events_apply_identity_and_outcome_corrections(self) -> None:
        entity_ids = {entity["id"] for entity in WAVE8_NORTH_AMERICA_ENTITIES}
        entities = {entity["id"]: entity for entity in _json(ROOT / "data/release/entities.json") if entity["id"] not in entity_ids}
        install_wave8_north_america_entities(entities)
        existing = [event for event in _json(ROOT / "data/release/events.json") if event.get("hced_candidate_id") not in WAVE8_NORTH_AMERICA_CONTRACT_IDS]
        events = promote_wave8_north_america_contracts(_rows(), entities, existing)
        self.assertEqual(len(events), 22)
        for event in events:
            Event.from_dict(event)
        by_id = {event["hced_candidate_id"]: event for event in events}
        self.assertEqual(by_id["hced-Birch Coulee1862-1"]["outcome_source_ids"], ["mnhs_birch_coulee_1862"])
        tres = by_id["hced-Tres Castillos1880-1"]
        self.assertEqual(tres["outcome_source_ids"], ["army_cmh_victorio_campaign_1880"])
        self.assertEqual({p["entity_id"] for p in tres["participants"] if p["side"] == "side_a"}, {"clio_mx_mexico_1_1868_ffbcfbae", "terrazas_tarahumara_auxiliaries_1880"})
        self.assertTrue(all(p["termination"] == "engagement_victory" for p in tres["participants"] if p["side"] == "side_a"))

    def test_massacres_and_unresolved_umbrella_rows_stay_unrated(self) -> None:
        for candidate_id in ("hced-Wounded Knee Creek1890-1", "hced-Janos Massacre1851-1", "hced-Skeleton Cave1872-1"):
            self.assertIn(candidate_id, WAVE8_NORTH_AMERICA_HOLD_IDS)
        events = _json(ROOT / "data/release/events.json")
        self.assertFalse(any(event.get("hced_candidate_id") in WAVE8_NORTH_AMERICA_HOLD_IDS for event in events))
        promotion = _json(ROOT / "data/release/metadata.json")["promotion"]
        self.assertEqual(promotion["accepted_wave8_north_america_hced_events"], 22)


if __name__ == "__main__":
    unittest.main()
