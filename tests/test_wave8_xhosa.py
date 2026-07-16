import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave8_xhosa import (
    WAVE8_XHOSA_CONTRACT_IDS,
    WAVE8_XHOSA_CONTRACTS,
    WAVE8_XHOSA_ENTITIES,
    WAVE8_XHOSA_FINAL_AUDIT_SIGNATURE,
    WAVE8_XHOSA_HOLD_IDS,
    WAVE8_XHOSA_HOLDS,
    WAVE8_XHOSA_RESERVED_IDS,
    WAVE8_XHOSA_SOURCES,
    install_wave8_xhosa_entities,
    install_wave8_xhosa_sources,
    promote_wave8_xhosa_contracts,
    validate_wave8_xhosa_queue_contracts,
    wave8_xhosa_cohort_counts,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _audit_signature() -> str:
    lines = []
    for disposition, inventory in (
        ("promote", WAVE8_XHOSA_CONTRACTS),
        ("hold", WAVE8_XHOSA_HOLDS),
    ):
        for candidate_id, item in sorted(inventory.items()):
            lines.append(
                "|".join(
                    (
                        disposition,
                        candidate_id,
                        item["raw_row_sha256"],
                        item["canonical_event"]["canonical_key"],
                        ",".join(item.get("side_1_entity_ids", [])),
                        ",".join(item.get("side_2_entity_ids", [])),
                        str(item.get("winner_side", "")),
                        str(bool(item.get("source_outcome_override"))),
                        ",".join(item.get("outcome_source_ids", [])),
                        item.get("hold_category", ""),
                    )
                )
            )
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


class Wave8XhosaTests(unittest.TestCase):
    def _entities_and_existing(self):
        lane_ids = {entity["id"] for entity in WAVE8_XHOSA_ENTITIES}
        entities = {
            entity["id"]: entity
            for entity in _json(ROOT / "data/release/entities.json")
            if entity["id"] not in lane_ids
        }
        install_wave8_xhosa_entities(entities)
        existing = [
            event
            for event in _json(ROOT / "data/release/events.json")
            if event.get("hced_candidate_id") not in WAVE8_XHOSA_CONTRACT_IDS
        ]
        return entities, existing

    def test_inventory_is_disjoint_counted_and_signature_pinned(self) -> None:
        self.assertEqual(
            (len(WAVE8_XHOSA_CONTRACT_IDS), len(WAVE8_XHOSA_HOLD_IDS)),
            (10, 9),
        )
        self.assertFalse(WAVE8_XHOSA_CONTRACT_IDS & WAVE8_XHOSA_HOLD_IDS)
        self.assertEqual(
            WAVE8_XHOSA_RESERVED_IDS,
            WAVE8_XHOSA_CONTRACT_IDS | WAVE8_XHOSA_HOLD_IDS,
        )
        self.assertEqual(_audit_signature(), WAVE8_XHOSA_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            wave8_xhosa_cohort_counts(),
            {
                "eighth_frontier_war": 2,
                "fifth_frontier_war": 1,
                "ninth_frontier_war": 3,
                "seventh_frontier_war": 3,
                "xhosa_civil_war": 1,
            },
        )

    def test_entities_are_event_bounded_and_sources_parse(self) -> None:
        self.assertEqual((len(WAVE8_XHOSA_ENTITIES), len(WAVE8_XHOSA_SOURCES)), (22, 32))
        self.assertEqual(len({entity["id"] for entity in WAVE8_XHOSA_ENTITIES}), 22)
        self.assertEqual(len({source["id"] for source in WAVE8_XHOSA_SOURCES}), 32)
        for entity in WAVE8_XHOSA_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
        for source in WAVE8_XHOSA_SOURCES:
            Source.from_dict(source)

    def test_no_generic_xhosa_identity_exists(self) -> None:
        entity_ids = {entity["id"] for entity in WAVE8_XHOSA_ENTITIES}
        self.assertTrue({"xhosa", "xhosa_kingdom"}.isdisjoint(entity_ids))
        self.assertFalse(
            any(
                entity["name"].casefold() in {"xhosa", "xhosa kingdom"}
                for entity in WAVE8_XHOSA_ENTITIES
            )
        )
        installed: dict[str, dict] = {}
        install_wave8_xhosa_entities(installed)
        self.assertEqual(set(installed), entity_ids)
        sources: dict[str, dict] = {}
        install_wave8_xhosa_sources(sources)
        self.assertEqual(set(sources), {source["id"] for source in WAVE8_XHOSA_SOURCES})

    def test_queue_hashes_validate_and_drift_fails_closed(self) -> None:
        rows = _rows()
        self.assertEqual(
            validate_wave8_xhosa_queue_contracts(rows),
            {"promotion_contracts": 10, "holds": 9, "reviewed_hced_rows": 19},
        )
        changed = copy.deepcopy(rows)
        target = next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Boomah Pass1850-1"
        )
        target["winner_raw"] = "United Kingdom"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_xhosa_queue_contracts(changed)

    def test_contract_sides_are_precise_and_holds_never_emit(self) -> None:
        expected_sides = {
            candidate_id: (
                tuple(contract["side_1_entity_ids"]),
                tuple(contract["side_2_entity_ids"]),
            )
            for candidate_id, contract in WAVE8_XHOSA_CONTRACTS.items()
        }
        self.assertEqual(
            expected_sides["hced-Ibeka1877-1"],
            (
                (
                    "frontier_armed_mounted_police_ibeka_1877",
                    "veldman_bikitsha_mfengu_levies_ibeka_1877",
                ),
                ("sigcawu_sarhili_gcaleka_force_ibeka_1877",),
            ),
        )
        self.assertEqual(
            expected_sides["hced-Kentani1878-1"][0],
            (
                "united_kingdom",
                "cape_colonial_forces_centane_1878",
                "veldman_poswa_mfengu_levies_centane_1878",
            ),
        )
        entities, existing = self._entities_and_existing()
        events = promote_wave8_xhosa_contracts(_rows(), entities, existing)
        self.assertEqual({event["hced_candidate_id"] for event in events}, WAVE8_XHOSA_CONTRACT_IDS)
        self.assertTrue(WAVE8_XHOSA_HOLD_IDS.isdisjoint({event["hced_candidate_id"] for event in events}))
        by_id = {event["hced_candidate_id"]: event for event in events}
        for candidate_id, contract in WAVE8_XHOSA_CONTRACTS.items():
            event = by_id[candidate_id]
            winner_ids = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["side"] == "side_a"
            }
            loser_ids = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["side"] == "side_b"
            }
            expected_winners = set(contract[f"side_{contract['winner_side']}_entity_ids"])
            expected_losers = set(contract[f"side_{3 - contract['winner_side']}_entity_ids"])
            self.assertEqual((winner_ids, loser_ids), (expected_winners, expected_losers))

    def test_only_two_source_backed_outcome_reversals(self) -> None:
        override_ids = {
            candidate_id
            for candidate_id, contract in WAVE8_XHOSA_CONTRACTS.items()
            if contract["source_outcome_override"]
        }
        self.assertEqual(
            override_ids,
            {"hced-Amalinda1818-1", "hced-Fish River1851-1"},
        )
        entities, existing = self._entities_and_existing()
        by_id = {
            event["hced_candidate_id"]: event
            for event in promote_wave8_xhosa_contracts(_rows(), entities, existing)
        }
        amalinde = by_id["hced-Amalinda1818-1"]
        self.assertEqual(
            amalinde["outcome_source_ids"],
            ["saho_ngqika_ndlambe", "samhs_amalinde_1818"],
        )
        self.assertEqual(
            {
                p["entity_id"]
                for p in amalinde["participants"]
                if p["side"] == "side_a"
            },
            {"mdushane_ndlambe_hintsa_gcaleka_coalition_1818"},
        )
        fish_river = by_id["hced-Fish River1851-1"]
        self.assertEqual(
            fish_river["outcome_source_ids"],
            ["samhs_fish_river_bush_1851"],
        )
        self.assertEqual(
            {
                p["entity_id"]
                for p in fish_river["participants"]
                if p["side"] == "side_a"
            },
            {"siyolo_amandlambe_force_1851", "fish_river_khoi_rebel_contingent_1851"},
        )
        for candidate_id in WAVE8_XHOSA_CONTRACT_IDS - override_ids:
            self.assertEqual(by_id[candidate_id]["outcome_source_ids"], ["hced_dataset"])

    def test_emitted_events_have_exact_provenance(self) -> None:
        entities, existing = self._entities_and_existing()
        events = promote_wave8_xhosa_contracts(_rows(), entities, existing)
        self.assertEqual(len(events), 10)
        for event in events:
            Event.from_dict(event)
            contract = WAVE8_XHOSA_CONTRACTS[event["hced_candidate_id"]]
            self.assertTrue(event["id"].startswith("hced_wave8_xhosa_"))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["canonical_event_key"], contract["canonical_event"]["canonical_key"])
            self.assertEqual(
                event["source_ids"],
                ["hced_dataset", *contract["evidence_refs"]],
            )
            self.assertIn("Candidate-keyed Wave 8 tactical assertion", event["summary"])
            self.assertEqual(event["reviewed_granularity"], "engagement")
        by_id = {event["hced_candidate_id"]: event for event in events}
        self.assertEqual(by_id["hced-Boomah Pass1850-1"]["aliases"], ["Boomah Pass"])
        self.assertEqual(by_id["hced-Kentani1878-1"]["aliases"], ["Kentani"])
        self.assertEqual(by_id["hced-NAxama1878-1"]["aliases"], ["NAxama"])


if __name__ == "__main__":
    unittest.main()
