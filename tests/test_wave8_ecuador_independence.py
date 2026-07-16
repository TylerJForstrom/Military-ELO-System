import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_ecuador_independence import (
    WAVE8_ECUADOR_INDEPENDENCE_CONTRACT_IDS,
    WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS,
    WAVE8_ECUADOR_INDEPENDENCE_ENTITIES,
    WAVE8_ECUADOR_INDEPENDENCE_FINAL_AUDIT_SIGNATURE,
    WAVE8_ECUADOR_INDEPENDENCE_HOLD_IDS,
    WAVE8_ECUADOR_INDEPENDENCE_RESERVED_IDS,
    WAVE8_ECUADOR_INDEPENDENCE_SOURCES,
    install_wave8_ecuador_independence_entities,
    install_wave8_ecuador_independence_sources,
    promote_wave8_ecuador_independence_contracts,
    validate_wave8_ecuador_independence_queue_contracts,
    wave8_ecuador_independence_cohort_counts,
    wave8_ecuador_independence_counts,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_ecuador_independence_"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


EXPECTED_SIDES = {
    "hced-Huachi1820-1": ({"spanish_empire"}, {"free_province_guayaquil_1820_1822"}),
    "hced-Tanizahua1821-1": ({"spanish_empire"}, {"free_province_guayaquil_1820_1822"}),
    "hced-Yaguachi1821-1": ({"sucre_quito_liberating_army_1821_1822"}, {"spanish_empire"}),
    "hced-Huachi1821-1": ({"spanish_empire"}, {"sucre_quito_liberating_army_1821_1822"}),
    "hced-Pichincha1822-1": ({"sucre_quito_liberating_army_1821_1822"}, {"spanish_empire"}),
    "hced-Ibarra1823-1": ({"gran_colombia_1819_1831"}, {"agualongo_pasto_royalist_force_ibarra_1823"}),
}


class Wave8EcuadorIndependenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows()

    def _emit(self):
        new_entity_ids = {entity["id"] for entity in WAVE8_ECUADOR_INDEPENDENCE_ENTITIES}
        entities = {
            entity["id"]: entity
            for entity in _json(ROOT / "data" / "release" / "entities.json")
            if entity["id"] not in new_entity_ids
        }
        install_wave8_ecuador_independence_entities(entities)
        existing = [
            event
            for event in _json(ROOT / "data" / "release" / "events.json")
            if event.get("hced_candidate_id") not in WAVE8_ECUADOR_INDEPENDENCE_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, promote_wave8_ecuador_independence_contracts(
            self.rows, entities, existing
        )

    def test_signature_inventory_counts_and_cohorts_are_pinned(self) -> None:
        payload = {
            "contracts": WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS,
            "entities": WAVE8_ECUADOR_INDEPENDENCE_ENTITIES,
            "holds": {},
            "sources": WAVE8_ECUADOR_INDEPENDENCE_SOURCES,
        }
        signature = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self.assertEqual(signature, WAVE8_ECUADOR_INDEPENDENCE_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(WAVE8_ECUADOR_INDEPENDENCE_CONTRACT_IDS, set(EXPECTED_SIDES))
        self.assertEqual(WAVE8_ECUADOR_INDEPENDENCE_RESERVED_IDS, WAVE8_ECUADOR_INDEPENDENCE_CONTRACT_IDS)
        self.assertEqual(WAVE8_ECUADOR_INDEPENDENCE_HOLD_IDS, frozenset())
        self.assertEqual(
            wave8_ecuador_independence_counts(),
            {
                "promotion_contracts": 6,
                "holds": 0,
                "reviewed_hced_rows": 6,
                "new_entities": 4,
                "new_sources": 6,
            },
        )
        self.assertEqual(
            wave8_ecuador_independence_cohort_counts(),
            {
                "guayaquil_independence_campaign": 2,
                "pasto_royalist_rebellion": 1,
                "sucre_quito_campaign": 3,
            },
        )

    def test_all_six_queue_rows_are_exactly_pinned_and_fail_closed(self) -> None:
        indexed = {
            row["candidate_id"]: row
            for row in self.rows
            if row.get("candidate_id") in WAVE8_ECUADOR_INDEPENDENCE_CONTRACT_IDS
        }
        self.assertEqual(set(indexed), set(EXPECTED_SIDES))
        for candidate_id, contract in WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS.items():
            self.assertEqual(
                canonical_hced_row_sha256(indexed[candidate_id]),
                contract["raw_row_sha256"],
            )
        self.assertEqual(
            validate_wave8_ecuador_independence_queue_contracts(self.rows),
            {"promotion_contracts": 6, "holds": 0, "reviewed_hced_rows": 6},
        )

        changed = copy.deepcopy(self.rows)
        next(row for row in changed if row["candidate_id"] == "hced-Pichincha1822-1")[
            "winner_raw"
        ] = "Spain"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_ecuador_independence_queue_contracts(changed)

    def test_entities_and_sources_are_bounded_parseable_and_installable(self) -> None:
        for entity in WAVE8_ECUADOR_INDEPENDENCE_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIsNotNone(entity["end_year"])
            self.assertNotEqual(entity["name"], "Ecuador")
            self.assertTrue(
                "inherit" in entity["continuity_note"].casefold()
                or "do not receive" in entity["continuity_note"].casefold()
            )
        for source in WAVE8_ECUADOR_INDEPENDENCE_SOURCES:
            Source.from_dict(source)

        entities = {}
        sources = {}
        install_wave8_ecuador_independence_entities(entities)
        install_wave8_ecuador_independence_sources(sources)
        self.assertEqual(set(entities), {entity["id"] for entity in WAVE8_ECUADOR_INDEPENDENCE_ENTITIES})
        self.assertEqual(set(sources), {source["id"] for source in WAVE8_ECUADOR_INDEPENDENCE_SOURCES})

    def test_emission_preserves_six_tactical_outcomes_without_modern_ecuador(self) -> None:
        _, events = self._emit()
        self.assertEqual(len(events), 6)
        by_candidate = {event["hced_candidate_id"]: event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_SIDES))
        for candidate_id, (expected_winners, expected_losers) in EXPECTED_SIDES.items():
            event = by_candidate[candidate_id]
            Event.from_dict(event)
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
            self.assertEqual((winners, losers), (expected_winners, expected_losers))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertNotIn("ecuador", winners | losers)
            contract = WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS[candidate_id]
            self.assertFalse(contract["source_outcome_override"])
            self.assertTrue(contract["actor_override"])

    def test_direct_outcome_sources_are_distinct_from_identity_only_evidence(self) -> None:
        source_by_id = {source["id"]: source for source in WAVE8_ECUADOR_INDEPENDENCE_SOURCES}
        for contract in WAVE8_ECUADOR_INDEPENDENCE_CONTRACTS.values():
            self.assertTrue(contract["outcome_source_ids"])
            self.assertTrue(set(contract["outcome_source_ids"]) <= set(contract["evidence_refs"]))
            self.assertEqual(
                set(contract["outcome_source_family_ids"]),
                {source_by_id[source_id]["source_family_id"] for source_id in contract["outcome_source_ids"]},
            )
            for source_id in contract["outcome_source_ids"]:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])


if __name__ == "__main__":
    unittest.main()
