import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.wave8_african_states import (
    WAVE8_AFRICAN_STATES_CONTRACT_IDS,
    WAVE8_AFRICAN_STATES_CONTRACTS,
    WAVE8_AFRICAN_STATES_ENTITIES,
    WAVE8_AFRICAN_STATES_FINAL_AUDIT_SIGNATURE,
    WAVE8_AFRICAN_STATES_RESERVED_IDS,
    WAVE8_AFRICAN_STATES_SOURCES,
    install_wave8_african_states_entities,
    promote_wave8_african_states_contracts,
    validate_wave8_african_states_queue_contracts,
    wave8_african_states_cohort_counts,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _review_rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class Wave8AfricanStatesTests(unittest.TestCase):
    def test_inventory_and_audit_signature_are_exact(self) -> None:
        self.assertEqual(len(WAVE8_AFRICAN_STATES_CONTRACT_IDS), 9)
        self.assertEqual(WAVE8_AFRICAN_STATES_RESERVED_IDS, WAVE8_AFRICAN_STATES_CONTRACT_IDS)
        self.assertEqual(len(WAVE8_AFRICAN_STATES_ENTITIES), 3)
        self.assertEqual(len(WAVE8_AFRICAN_STATES_SOURCES), 4)
        lines = []
        for candidate_id, contract in sorted(WAVE8_AFRICAN_STATES_CONTRACTS.items()):
            lines.append(
                "|".join(
                    (
                        candidate_id,
                        contract["raw_row_sha256"],
                        contract["canonical_event"]["canonical_key"],
                        ",".join(contract["side_1_entity_ids"]),
                        ",".join(contract["side_2_entity_ids"]),
                    )
                )
            )
        self.assertEqual(
            hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest(),
            WAVE8_AFRICAN_STATES_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_african_states_cohort_counts(),
            {"dahomey_behanzin": 5, "ndebele_lobengula": 4},
        )

    def test_entities_and_sources_parse_and_are_alias_free(self) -> None:
        for entity in WAVE8_AFRICAN_STATES_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
        for source in WAVE8_AFRICAN_STATES_SOURCES:
            Source.from_dict(source)

    def test_queue_contracts_fail_closed_on_drift(self) -> None:
        rows = _review_rows()
        self.assertEqual(
            validate_wave8_african_states_queue_contracts(rows),
            {"promotion_contracts": 9, "reviewed_hced_rows": 9},
        )
        changed = copy.deepcopy(rows)
        target = next(row for row in changed if row["candidate_id"] == "hced-Abomey1892-1")
        target["winner_raw"] = "Dahomey"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_african_states_queue_contracts(changed)

    def test_all_contract_rows_are_reserved_from_generic_passes(self) -> None:
        rows = _review_rows()
        selected = [row for row in rows if row["candidate_id"] in WAVE8_AFRICAN_STATES_CONTRACT_IDS]
        result = promote_hced_crosswalk_rows(
            selected,
            owners={},
            curated_seed_keys=set(),
            ensure_candidate_entity=lambda polity: None,
            reserved_candidate_ids=WAVE8_AFRICAN_STATES_RESERVED_IDS,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["deferred_label_rows"], [])
        self.assertEqual(result["rejections"]["reserved_candidate_contract"], 9)

    def test_exact_events_bind_dahomey_ndebele_and_bsac(self) -> None:
        rows = _review_rows()
        entities = {entity["id"]: entity for entity in _json(ROOT / "data/release/entities.json")}
        install_wave8_african_states_entities(entities)
        existing = [
            event
            for event in _json(ROOT / "data/release/events.json")
            if event.get("hced_candidate_id") not in WAVE8_AFRICAN_STATES_CONTRACT_IDS
        ]
        events = promote_wave8_african_states_contracts(rows, entities, existing)
        self.assertEqual(len(events), 9)
        self.assertEqual({event["hced_candidate_id"] for event in events}, WAVE8_AFRICAN_STATES_CONTRACT_IDS)
        for event in events:
            Event.from_dict(event)
            self.assertEqual(event["war_type"], "colonial_anti_colonial")
            self.assertEqual(event["outcome_source_ids"], ["hced_dataset"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
        matabele = [event for event in events if event["hced_candidate_id"] in {
            "hced-Bembesi1893-1", "hced-Empadine1893-1", "hced-Shangani1893-1", "hced-Shangani Incident1893-1"
        }]
        participant_ids = {p["entity_id"] for event in matabele for p in event["participants"]}
        self.assertIn("ndebele_kingdom_lobengula", participant_ids)
        self.assertIn("british_south_africa_company_forces_1893", participant_ids)
        self.assertNotIn("united_kingdom", participant_ids)

    def test_release_artifacts_publish_exact_lane(self) -> None:
        events = _json(ROOT / "data/release/events.json")
        lane = [event for event in events if event.get("hced_candidate_id") in WAVE8_AFRICAN_STATES_CONTRACT_IDS]
        self.assertEqual(len(lane), 9)
        metadata = _json(ROOT / "data/release/metadata.json")
        promotion = metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_african_states_hced_events"], 9)
        self.assertEqual(promotion["wave8_african_states_cohort_counts"], {"dahomey_behanzin": 5, "ndebele_lobengula": 4})


if __name__ == "__main__":
    unittest.main()
