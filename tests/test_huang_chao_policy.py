import copy
import json
import unittest
from pathlib import Path

from military_elo.promotion import huang_chao_policy as lane
from military_elo.promotion.hced import resolve_hced_side_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_goguryeo import (
    WAVE8_GOGURYEO_ENTITIES,
    install_wave8_goguryeo_entities,
)


ROOT = Path(__file__).resolve().parents[1]
TANG = "clio_cn_tang_dyn_1_623_3e98c37b"
HUANG = "huang_chao_rebel_movement"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class HuangChaoPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seed_entities = _json(ROOT / "data/seed/entities.json")
        cls.cliopatria = _jsonl(
            ROOT / "data/review/cliopatria-entity-candidates.jsonl"
        )
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.events = _json(ROOT / "data/release/events.json")
        cls.entities = _json(ROOT / "data/release/entities.json")
        cls.metadata = _json(ROOT / "data/release/metadata.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")

    def test_exact_three_row_inventory_and_hashes_are_pinned(self):
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if str(row.get("candidate_id")) in lane.HUANG_CHAO_CONTRACT_IDS
        }
        self.assertEqual(set(rows), set(lane.HUANG_CHAO_ROW_HASHES))
        self.assertEqual(len(rows), 3)
        for candidate_id, expected_hash in lane.HUANG_CHAO_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(rows[candidate_id]),
                    expected_hash,
                )
                self.assertIs(rows[candidate_id]["do_not_rate_automatically"], True)
                self.assertIs(rows[candidate_id]["winner_loser_complete"], True)
                self.assertIn(
                    rows[candidate_id]["winner_raw"],
                    {
                        rows[candidate_id]["side_1_raw"],
                        rows[candidate_id]["side_2_raw"],
                    },
                )

    def test_queue_contract_is_exact_and_has_no_reversals(self):
        self.assertEqual(
            lane.validate_huang_chao_queue_contracts(self.hced),
            {
                "exact_label_rows": 3,
                "policy_promotions": 3,
                "source_outcome_reversals": 0,
            },
        )

    def test_label_policy_is_authoritative_and_time_bounded(self):
        self.assertEqual(
            resolve_hced_side_label("Huang Chao", 875, 884, {}),
            (HUANG, None, None, "label_policy"),
        )
        for low, high in ((874, 874), (884, 885), (900, 900)):
            with self.subTest(low=low, high=high):
                self.assertEqual(
                    resolve_hced_side_label("Huang Chao", low, high, {}),
                    (None, None, "label_outside_policy_window", None),
                )

    def test_curated_tang_seed_exactly_precedes_lane_fixture(self):
        self.assertEqual(
            lane.validate_huang_chao_seed_precedence(
                self.seed_entities,
                self.cliopatria,
            ),
            {
                "curated_seed_records": 2,
                "source_candidate_records": 1,
                "unlocked_policy_rows": 3,
            },
        )
        seed = {str(entity["id"]): entity for entity in self.seed_entities}
        fixture = {
            str(entity["id"]): entity for entity in WAVE8_GOGURYEO_ENTITIES
        }
        self.assertEqual(seed[TANG], fixture[TANG])
        self.assertFalse(seed[TANG]["aliases"])
        self.assertFalse(seed[HUANG]["aliases"])
        before = copy.deepcopy(seed[TANG])
        install_wave8_goguryeo_entities(seed)
        self.assertEqual(seed[TANG], before)

    def test_three_release_events_have_exact_tactical_outcomes(self):
        self.assertEqual(
            lane.validate_huang_chao_release(self.events),
            {
                "label_policy_events": 3,
                "source_outcome_reversals": 0,
                "tactical_events": 3,
            },
        )
        events = {
            str(event["hced_candidate_id"]): event
            for event in self.events
            if str(event.get("hced_candidate_id"))
            in lane.HUANG_CHAO_CONTRACT_IDS
        }
        expected_winners = {
            "hced-Chenzhou883-1": TANG,
            "hced-Guangzhou879-1": HUANG,
            "hced-Liangtian883-1": TANG,
        }
        for candidate_id, event in events.items():
            winners = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["termination"] == "engagement_victory"
            }
            self.assertEqual(winners, {expected_winners[candidate_id]})
            self.assertEqual(event["identity_resolution"], "label")
            self.assertEqual(event["confidence"], 0.64)
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["scale"], "battle")
            self.assertEqual(
                set(event["side_identity_resolution"].values()),
                {"label_policy", "seshat_crosswalk"},
            )

    def test_unknown_is_never_a_draw_and_massacre_does_not_replace_battle(self):
        events = [
            event
            for event in self.events
            if str(event.get("hced_candidate_id"))
            in lane.HUANG_CHAO_CONTRACT_IDS
        ]
        self.assertEqual(len(events), 3)
        for event in events:
            terminations = {
                participant["termination"] for participant in event["participants"]
            }
            self.assertEqual(
                terminations,
                {"engagement_victory", "engagement_defeat"},
            )
        guangzhou = next(
            event
            for event in events
            if event["hced_candidate_id"] == "hced-Guangzhou879-1"
        )
        self.assertEqual(guangzhou["name"], "Guangzhou")
        self.assertEqual((guangzhou["year"], guangzhou["end_year"]), (879, 879))

    def test_historical_funnel_pin_is_closed_in_current_funnel(self):
        self.assertEqual(
            lane.HUANG_CHAO_FUNNEL_AUDIT,
            {
                "candidate_ids": [],
                "event_candidate_id_sha256": (
                    "ce1b4ebc028cbd493d93121cf7de1d60acae8ec6050f60ad1c80b1ca5ee09d1f"
                ),
                "events_touched": 3,
                "label": "huang chao",
                "sole_blocker_events": 3,
                "zero_time_valid_candidates": 3,
            },
        )
        self.assertFalse(
            any(
                row.get("label") == "huang chao"
                for row in self.funnel.get("labels", [])
            )
        )

    def test_signature_metadata_and_release_counts_are_pinned(self):
        self.assertEqual(
            lane.huang_chao_audit_signature(),
            lane.HUANG_CHAO_FINAL_AUDIT_SIGNATURE,
        )
        promotion = self.metadata["promotion"]
        self.assertEqual(
            promotion["huang_chao_policy_metadata"],
            lane.huang_chao_metadata(),
        )
        self.assertEqual(
            promotion["huang_chao_seed_precedence_validation"][
                "unlocked_policy_rows"
            ],
            3,
        )
        self.assertEqual(
            promotion["huang_chao_release_validation"]["label_policy_events"],
            3,
        )
        coverage = self.registry["coverage"]
        self.assertEqual(self.metadata["record_counts_expected"]["events"], 5_422)
        self.assertEqual(coverage["rated_entities"], 1_019)
        self.assertEqual(coverage["unresolved_event_candidates"], 36_926)
        self.assertEqual(
            coverage["hced_location_assertions"]["hced_candidate_bindings"],
            5_158,
        )

    def test_row_seed_and_release_drift_fail_closed(self):
        rows = copy.deepcopy(self.hced)
        row = next(
            item
            for item in rows
            if item.get("candidate_id") == "hced-Guangzhou879-1"
        )
        row["winner_raw"] = "Tang China"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_huang_chao_queue_contracts(rows)

        seed = copy.deepcopy(self.seed_entities)
        tang = next(entity for entity in seed if entity.get("id") == TANG)
        tang["aliases"] = ["Tang"]
        with self.assertRaisesRegex(ValueError, "Tang seed precedence"):
            lane.validate_huang_chao_seed_precedence(seed, self.cliopatria)

        event = next(
            item
            for item in self.events
            if item.get("hced_candidate_id") == "hced-Chenzhou883-1"
        )
        with self.assertRaisesRegex(ValueError, "release ownership"):
            lane.validate_huang_chao_release(
                [*copy.deepcopy(self.events), copy.deepcopy(event)]
            )


if __name__ == "__main__":
    unittest.main()
