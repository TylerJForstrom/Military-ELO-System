import copy
import json
import unittest
from pathlib import Path

from military_elo.promotion.wave8_cossack_rebellions import (
    WAVE8_COSSACK_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_COSSACK_FINAL_AUDIT_SIGNATURE,
    WAVE8_COSSACK_POINT_QUARANTINE_ADDITIONS,
    WAVE8_COSSACK_REBELLIONS_CONTRACTS,
    WAVE8_COSSACK_REBELLIONS_ENTITIES,
    WAVE8_COSSACK_REBELLIONS_HOLDS,
    WAVE8_COSSACK_REBELLIONS_SOURCES,
    WAVE8_COSSACK_RESERVED_IDS,
    install_wave8_cossack_entities,
    promote_wave8_cossack_events,
    validate_wave8_cossack_inventory,
    wave8_cossack_audit_signature,
)


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "review" / "hced-candidates.jsonl"
ENTITIES = ROOT / "data" / "release" / "entities.json"
EVENTS = ROOT / "data" / "release" / "events.json"


def _queue_rows():
    return [json.loads(line) for line in QUEUE.read_text().splitlines() if line.strip()]


def _release_entities():
    return {entity["id"]: entity for entity in json.loads(ENTITIES.read_text())}


class Wave8CossackRebellionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = _queue_rows()
        cls.entities = _release_entities()
        install_wave8_cossack_entities(cls.entities)
        existing = [
            event
            for event in json.loads(EVENTS.read_text())
            if event.get("hced_candidate_id") not in WAVE8_COSSACK_RESERVED_IDS
        ]
        cls.promoted = promote_wave8_cossack_events(
            cls.rows, cls.entities, existing
        )

    def test_inventory_counts_signature_and_reserved_ids_are_exact(self):
        counts = validate_wave8_cossack_inventory(self.rows)
        self.assertEqual(
            counts,
            {"promotion_contracts": 6, "holds": 0, "reviewed_hced_rows": 6},
        )
        self.assertEqual(len(WAVE8_COSSACK_RESERVED_IDS), 6)
        self.assertEqual(WAVE8_COSSACK_REBELLIONS_HOLDS, {})
        self.assertEqual(
            wave8_cossack_audit_signature(),
            WAVE8_COSSACK_FINAL_AUDIT_SIGNATURE,
        )

    def test_queue_contracts_fail_closed_on_any_drift(self):
        for candidate_id in sorted(WAVE8_COSSACK_RESERVED_IDS):
            rows = copy.deepcopy(self.rows)
            row = next(r for r in rows if r.get("candidate_id") == candidate_id)
            row["winner_raw"] = "tampered"
            with self.subTest(candidate_id=candidate_id):
                with self.assertRaisesRegex(ValueError, "fingerprint changed"):
                    validate_wave8_cossack_inventory(rows)

    def test_six_exact_events_use_three_distinct_rebel_identities(self):
        self.assertEqual(len(self.promoted), 6)
        by_candidate = {e["hced_candidate_id"]: e for e in self.promoted}
        expected = {
            "hced-Kazan1774-1": (
                "Battle of Kazan",
                "russian_empire",
                "pugachev_rebellion_forces_1773_1775",
            ),
            "hced-Orenburg1773-1774-1": (
                "Siege of Orenburg",
                "russian_empire",
                "pugachev_rebellion_forces_1773_1775",
            ),
            "hced-Tatishchevo1774-1": (
                "Battle of Tatishcheva Fortress",
                "russian_empire",
                "pugachev_rebellion_forces_1773_1775",
            ),
            "hced-Ufa1773-1774-1": (
                "Siege and relief of Ufa",
                "russian_empire",
                "pugachev_rebellion_forces_1773_1775",
            ),
            "hced-Loyew1649-1": (
                "Battle of Loyew",
                "polish_lithuanian_commonwealth",
                "krychevsky_zaporozhian_army_loyew_1649",
            ),
            "hced-Zhovnyne1638-1": (
                "Battle of Zhovnyne",
                "polish_lithuanian_commonwealth",
                "ostryanyn_hunia_rebel_force_1638",
            ),
        }
        self.assertEqual(set(by_candidate), set(expected))
        for candidate_id, (name, winner, loser) in expected.items():
            event = by_candidate[candidate_id]
            self.assertEqual(event["name"], name)
            outcomes = {
                participant["entity_id"]: participant["result_class"]
                for participant in event["participants"]
            }
            self.assertEqual(outcomes[winner], "limited_victory")
            self.assertEqual(outcomes[loser], "limited_defeat")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")

    def test_entities_are_conflict_bounded_alias_free_and_not_generic(self):
        self.assertEqual(len(WAVE8_COSSACK_REBELLIONS_ENTITIES), 3)
        ids = {entity["id"] for entity in WAVE8_COSSACK_REBELLIONS_ENTITIES}
        self.assertNotIn("cossack_rebels", ids)
        self.assertNotIn("cossacks", ids)
        for entity in WAVE8_COSSACK_REBELLIONS_ENTITIES:
            self.assertEqual(entity["aliases"], [])
            self.assertIsInstance(entity["start_year"], int)
            self.assertIsInstance(entity["end_year"], int)
            self.assertLessEqual(entity["start_year"], entity["end_year"])

    def test_sources_are_explicit_and_every_contract_has_direct_outcome_evidence(self):
        source_ids = {source["id"] for source in WAVE8_COSSACK_REBELLIONS_SOURCES}
        self.assertEqual(len(source_ids), 6)
        for source in WAVE8_COSSACK_REBELLIONS_SOURCES:
            self.assertTrue(source["url"].startswith("https://"))
            self.assertTrue(source["source_family_id"])
            self.assertIn("identity_boundary_or_context_reference", source["evidence_roles"])
        for contract in WAVE8_COSSACK_REBELLIONS_CONTRACTS.values():
            self.assertTrue(contract["outcome_source_ids"])
            self.assertTrue(set(contract["outcome_source_ids"]) <= source_ids)
            self.assertTrue(contract["outcome_source_family_ids"])
            self.assertFalse(contract.get("source_outcome_override", False))

    def test_known_wrong_points_are_exported_for_fail_closed_quarantine(self):
        self.assertEqual(
            WAVE8_COSSACK_POINT_QUARANTINE_ADDITIONS,
            {"hced-Tatishchevo1774-1", "hced-Zhovnyne1638-1"},
        )
        self.assertEqual(WAVE8_COSSACK_COUNTRY_QUARANTINE_ADDITIONS, set())


if __name__ == "__main__":
    unittest.main()
