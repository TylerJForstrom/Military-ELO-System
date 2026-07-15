from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from military_elo.promotion.common import validate_exact_candidate_contracts
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.iwbd import promote_iwbd_battles
from military_elo.promotion.iwd import aggregate_iwd_parent_wars
from military_elo.promotion.orchestrator import (
    EFFECTIVE_IWBD_CURATED_EXCLUSIONS,
    WAVE6_HCED_VALIDATED_SOURCE_CONTRACTS,
    WAVE6_IWBD_VALIDATED_SOURCE_CONTRACTS,
)
from military_elo.promotion.wave6_1800_2021_holds import (
    WAVE6_CROSS_LANE_B_OMISSIONS,
    WAVE6_HCED_AUDITED_HOLD_IDS,
    WAVE6_HCED_COMPANION_EXCLUSION_IDS,
    WAVE6_HCED_CURATED_EXCLUSIONS,
    WAVE6_HCED_HELD_SOURCE_CONTRACTS,
    WAVE6_IWBD_CURATED_EXCLUSIONS,
    WAVE6_IWBD_BASELINE_PRESERVATION_REASONS,
    WAVE6_IWBD_BASELINE_PUBLISHED_HOLD_IDS,
    WAVE6_IWBD_HELD_SOURCE_CONTRACTS,
    WAVE6_IWD_CURATED_PARENT_EXCLUSIONS,
    WAVE6_IWD_HELD_PARENT_CONTRACTS,
)
from military_elo.promotion.wave6_1800_2021_policy import (
    WAVE6_EXPECTED_HELD_COUNTS,
    WAVE6_EXPECTED_IMPLEMENTED_COUNTS,
    WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS,
    WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS,
    WAVE6_IWBD_REVIEWED_IDENTITY_COHORTS,
    WAVE6_IWD_REVIEWED_PARENT_CONTRACTS,
)
from military_elo.promotion.wave6_1800_2021_registry import (
    WAVE6_1800_2021_ENTITY_OVERRIDES,
    WAVE6_1800_2021_SOURCES,
    WAVE6_REUSED_CANONICAL_ENTITY_IDS,
)


ROOT = Path(__file__).resolve().parents[1]
QUEUES = ROOT / "build" / "wave6-1800-2021" / "queues"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


class Wave6InventoryTests(unittest.TestCase):
    def test_exact_frozen_inventory(self):
        self.assertEqual(
            WAVE6_EXPECTED_IMPLEMENTED_COUNTS,
            {"hced": 74, "iwd": 1, "iwbd": 15, "total": 90},
        )
        self.assertEqual(len(WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS), 74)
        self.assertEqual(set(WAVE6_IWD_REVIEWED_PARENT_CONTRACTS), {"55"})
        self.assertEqual(len(WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS), 15)
        self.assertEqual(
            {
                candidate_id
                for cohort in WAVE6_IWBD_REVIEWED_IDENTITY_COHORTS.values()
                for candidate_id in cohort
            },
            set(WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS),
        )

    def test_exact_frozen_holds_and_cross_lane_omissions(self):
        self.assertEqual(
            WAVE6_EXPECTED_HELD_COUNTS, {"hced": 28, "iwd": 14, "iwbd": 219}
        )
        self.assertEqual(len(WAVE6_HCED_AUDITED_HOLD_IDS), 28)
        self.assertEqual(len(WAVE6_HCED_COMPANION_EXCLUSION_IDS), 15)
        self.assertEqual(len(WAVE6_IWD_CURATED_PARENT_EXCLUSIONS), 14)
        self.assertEqual(len(WAVE6_IWBD_HELD_SOURCE_CONTRACTS), 219)
        self.assertEqual(len(WAVE6_IWBD_CURATED_EXCLUSIONS), 197)
        self.assertEqual(len(WAVE6_IWBD_BASELINE_PUBLISHED_HOLD_IDS), 22)
        self.assertEqual(
            set(WAVE6_IWBD_BASELINE_PRESERVATION_REASONS),
            WAVE6_IWBD_BASELINE_PUBLISHED_HOLD_IDS,
        )
        self.assertTrue(
            WAVE6_IWBD_BASELINE_PUBLISHED_HOLD_IDS.isdisjoint(
                WAVE6_IWBD_CURATED_EXCLUSIONS
            )
        )
        self.assertTrue(
            set(WAVE6_CROSS_LANE_B_OMISSIONS).isdisjoint(
                WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS
            )
        )
        self.assertTrue(
            set(WAVE6_CROSS_LANE_B_OMISSIONS).isdisjoint(WAVE6_HCED_CURATED_EXCLUSIONS)
        )

    def test_mandatory_holds_and_wave5_regression_guards(self):
        for candidate_id in (
            "hced-Baler1896-1",
            "hced-Quinqua1899-1",
            "hced-Khartoum1884-1",
            "hced-Ojinaga1913-1",
        ):
            self.assertIn(candidate_id, WAVE6_HCED_AUDITED_HOLD_IDS)
        self.assertIn("66", WAVE6_IWD_CURATED_PARENT_EXCLUSIONS)
        self.assertIn("iwbd-100-36-421", WAVE6_IWBD_CURATED_EXCLUSIONS)
        self.assertIn("iwbd-207-80-1654", WAVE6_IWBD_CURATED_EXCLUSIONS)
        for candidate_id in (
            "iwbd-108-40-788",
            "iwbd-115-43-810",
            "iwbd-115-43-811",
            "iwbd-115-43-812",
        ):
            self.assertIn(candidate_id, EFFECTIVE_IWBD_CURATED_EXCLUSIONS)

    def test_cross_source_companions_are_exactly_excluded(self):
        self.assertEqual(len(WAVE6_HCED_COMPANION_EXCLUSION_IDS), 15)
        self.assertTrue(
            WAVE6_HCED_COMPANION_EXCLUSION_IDS <= set(WAVE6_HCED_HELD_SOURCE_CONTRACTS)
        )
        self.assertTrue(
            WAVE6_HCED_COMPANION_EXCLUSION_IDS <= set(WAVE6_HCED_CURATED_EXCLUSIONS)
        )

    def test_wave6_exclusions_never_target_a_published_wave5_event(self):
        events = _json(ROOT / "data" / "release" / "events.json")
        published_hced = {
            event["hced_candidate_id"]
            for event in events
            if event.get("hced_candidate_id")
        }
        published_iwbd = {
            event["iwbd_candidate_id"]
            for event in events
            if event.get("iwbd_candidate_id")
        }
        published_iwd = {
            event["iwd_parent_war_id"]
            for event in events
            if event.get("iwd_parent_war_id")
        }
        self.assertTrue(published_hced.isdisjoint(WAVE6_HCED_CURATED_EXCLUSIONS))
        self.assertTrue(published_iwbd.isdisjoint(WAVE6_IWBD_CURATED_EXCLUSIONS))
        self.assertTrue(published_iwd.isdisjoint(WAVE6_IWD_CURATED_PARENT_EXCLUSIONS))


class Wave6IdentityAndSourceTests(unittest.TestCase):
    def test_reuses_single_canonical_series(self):
        payload = repr(
            (
                WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS,
                WAVE6_IWD_REVIEWED_PARENT_CONTRACTS,
                WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS,
            )
        )
        for forbidden in (
            "spanish_restoration_monarchy",
            "spanish_bourbon_restoration",
            "state_israel",
            "transjordan_1946",
            "syrian_republic_1946",
            "syrian_arab_republic",
            "kingdom_egypt",
            "khedivate_egypt",
            "united_arab_republic_egypt",
        ):
            self.assertNotIn(forbidden, payload)
        for canonical in (
            "spanish_empire",
            "egypt_muhammad_ali",
            "clio_q801_1948_5abea45e",
            "clio_q810_1947_98de647a",
            "clio_q41137_1973_b05dea50",
            "kingdom_iraq",
        ):
            self.assertIn(canonical, payload)

    def test_registry_has_one_row_per_entity_and_preserves_open_us_uk(self):
        ids = [entity["id"] for entity in WAVE6_1800_2021_ENTITY_OVERRIDES]
        self.assertEqual(len(ids), len(set(ids)))
        seed = {
            entity["id"]: entity
            for entity in _json(ROOT / "data" / "seed" / "entities.json")
        }
        self.assertIsNone(seed["united_states"]["end_year"])
        self.assertIsNone(seed["united_kingdom"]["end_year"])

    def test_reused_series_have_old_events_and_are_not_replaced(self):
        release_events = _json(ROOT / "data" / "release" / "events.json")
        old_events_by_entity = {
            entity_id: {
                event["id"]
                for event in release_events
                if any(p["entity_id"] == entity_id for p in event["participants"])
            }
            for entity_id in WAVE6_REUSED_CANONICAL_ENTITY_IDS
        }
        self.assertTrue(all(old_events_by_entity.values()))
        excluded_candidates = {
            *WAVE6_HCED_CURATED_EXCLUSIONS,
            *WAVE6_IWBD_CURATED_EXCLUSIONS,
        }
        for entity_id, event_ids in old_events_by_entity.items():
            removed = {
                event["id"]
                for event in release_events
                if event["id"] in event_ids
                and (
                    event.get("hced_candidate_id") in excluded_candidates
                    or event.get("iwbd_candidate_id") in excluded_candidates
                )
            }
            self.assertEqual(removed, set(), entity_id)
        override_ids = {entity["id"] for entity in WAVE6_1800_2021_ENTITY_OVERRIDES}
        widened = {
            "egypt_muhammad_ali",
            "clio_q801_1948_5abea45e",
            "clio_q810_1947_98de647a",
            "clio_q41137_1973_b05dea50",
        }
        self.assertTrue(widened <= override_ids)

    def test_every_new_source_declares_family_metadata(self):
        ids = [source["id"] for source in WAVE6_1800_2021_SOURCES]
        self.assertEqual(len(ids), len(set(ids)))
        for source in WAVE6_1800_2021_SOURCES:
            self.assertTrue(source["source_family_id"])
            self.assertTrue(source["evidence_roles"])


@unittest.skipUnless(
    (QUEUES / "hced-candidates.jsonl").exists(),
    "lane-local audited queues are not present",
)
class Wave6QueueContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hced = _jsonl(QUEUES / "hced-candidates.jsonl")
        cls.iwd = _jsonl(QUEUES / "iwd-1.21-candidates.jsonl")
        cls.iwbd = _jsonl(QUEUES / "iwbd-candidates.jsonl")
        entities = {
            entity["id"]: entity
            for entity in _json(ROOT / "data" / "seed" / "entities.json")
        }
        entities.update(
            {entity["id"]: entity for entity in WAVE6_1800_2021_ENTITY_OVERRIDES}
        )
        cls.entities = entities

    def _resolve(self, entity_id, low_year, high_year):
        entity = self.entities.get(entity_id)
        end_year = entity.get("end_year") if entity else None
        if (
            entity
            and entity["start_year"] <= low_year
            and (end_year is None or end_year >= high_year)
        ):
            return entity_id, None
        return None, None

    def test_all_safe_and_held_source_fingerprints_match(self):
        validate_exact_candidate_contracts(
            self.hced,
            WAVE6_HCED_VALIDATED_SOURCE_CONTRACTS,
            description="HCED Wave 6 test",
            require_complete=True,
        )
        validate_exact_candidate_contracts(
            self.iwbd,
            WAVE6_IWBD_VALIDATED_SOURCE_CONTRACTS,
            description="IWBD Wave 6 test",
            require_complete=True,
        )

    def test_fingerprint_drift_fails_closed(self):
        row = next(
            row for row in self.hced if row["candidate_id"] == "hced-Binakayan1896-1"
        )
        changed = copy.deepcopy(row)
        changed["winner_raw"] = "Spain"
        with self.assertRaisesRegex(ValueError, "source fingerprint changed"):
            validate_exact_candidate_contracts(
                [changed],
                {
                    "hced-Binakayan1896-1": WAVE6_HCED_VALIDATED_SOURCE_CONTRACTS[
                        "hced-Binakayan1896-1"
                    ]
                },
                description="HCED Wave 6 test",
            )

    def test_exact_74_hced_promote_with_pinned_parties_and_outcomes(self):
        target = set(WAVE6_HCED_VALIDATED_SOURCE_CONTRACTS)
        rows = [row for row in self.hced if row["candidate_id"] in target]
        result = promote_hced_crosswalk_rows(
            rows,
            {},
            set(),
            lambda _: None,
            reviewed_candidate_contracts=WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS,
            validated_source_contracts=WAVE6_HCED_VALIDATED_SOURCE_CONTRACTS,
            curated_exclusions=WAVE6_HCED_CURATED_EXCLUSIONS,
            resolve_reviewed_id=self._resolve,
            require_complete_reviewed_identity_bindings=True,
        )
        self.assertEqual(len(result["events"]), 74)
        self.assertEqual(
            {event["identity_resolution"] for event in result["events"]},
            {"exact_reviewed_candidate_contract"},
        )

    def test_exact_parent_55_is_the_only_iwd_update(self):
        contracts = {
            **WAVE6_IWD_REVIEWED_PARENT_CONTRACTS,
            **WAVE6_IWD_HELD_PARENT_CONTRACTS,
        }
        rows = [row for row in self.iwd if row["parent_war_id"] in contracts]
        result = aggregate_iwd_parent_wars(
            rows,
            [],
            lambda *_: (None, None),
            curated_parent_exclusions=WAVE6_IWD_CURATED_PARENT_EXCLUSIONS,
            reviewed_parent_contracts=contracts,
            resolve_reviewed_party=self._resolve,
            require_complete_reviewed_parents=True,
        )
        self.assertEqual(
            [event["iwd_parent_war_id"] for event in result["events"]], ["55"]
        )

    def test_exact_15_iwbd_promote_and_coalitions_are_complete(self):
        target = {
            *WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS,
            *WAVE6_IWBD_CURATED_EXCLUSIONS,
        }
        rows = [row for row in self.iwbd if row["candidate_id"] in target]
        source_contracts = {
            candidate_id: contract
            for candidate_id, contract in WAVE6_IWBD_VALIDATED_SOURCE_CONTRACTS.items()
            if candidate_id in target
        }
        result = promote_iwbd_battles(
            rows,
            set(),
            {},
            lambda *_: (None, None),
            {},
            set(),
            curated_exclusions=WAVE6_IWBD_CURATED_EXCLUSIONS,
            reviewed_identity_bindings=WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS,
            validated_source_contracts=source_contracts,
            reviewed_identity_cohorts=WAVE6_IWBD_REVIEWED_IDENTITY_COHORTS,
            resolve_reviewed_id=self._resolve,
            require_complete_reviewed_identity_cohorts=True,
        )
        self.assertEqual(len(result["events"]), 15)
        by_id = {event["iwbd_candidate_id"]: event for event in result["events"]}
        sarandaporon = "iwbd-100-36-421"
        self.assertNotIn(sarandaporon, by_id)
        participants = {
            p["entity_id"] for p in by_id["iwbd-100-36-422"]["participants"]
        }
        self.assertEqual(
            participants, {"kingdom_montenegro", "kingdom_serbia", "ottoman_empire"}
        )


if __name__ == "__main__":
    unittest.main()
