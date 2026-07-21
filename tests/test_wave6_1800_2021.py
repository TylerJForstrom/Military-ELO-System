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
    WAVE6_HCED_IDENTITY_BOUNDARY_HOLD_REASONS,
    WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS,
    WAVE6_IWBD_IDENTITY_BOUNDARY_HOLD_REASONS,
    WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS,
    WAVE6_IWBD_REVIEWED_IDENTITY_COHORTS,
    WAVE6_IWD_IDENTITY_BOUNDARY_HOLD_REASONS,
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
            {"hced": 60, "iwd": 1, "iwbd": 9, "total": 70},
        )
        self.assertEqual(len(WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS), 60)
        self.assertEqual(set(WAVE6_IWD_REVIEWED_PARENT_CONTRACTS), {"55"})
        self.assertEqual(len(WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS), 9)
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
            WAVE6_EXPECTED_HELD_COUNTS, {"hced": 42, "iwd": 14, "iwbd": 225}
        )
        self.assertEqual(len(WAVE6_HCED_AUDITED_HOLD_IDS), 42)
        self.assertEqual(len(WAVE6_HCED_COMPANION_EXCLUSION_IDS), 15)
        self.assertEqual(len(WAVE6_IWD_CURATED_PARENT_EXCLUSIONS), 14)
        self.assertEqual(len(WAVE6_IWBD_HELD_SOURCE_CONTRACTS), 225)
        self.assertEqual(len(WAVE6_IWBD_CURATED_EXCLUSIONS), 203)
        self.assertEqual(len(WAVE6_HCED_IDENTITY_BOUNDARY_HOLD_REASONS), 14)
        self.assertEqual(len(WAVE6_IWD_IDENTITY_BOUNDARY_HOLD_REASONS), 0)
        self.assertEqual(len(WAVE6_IWBD_IDENTITY_BOUNDARY_HOLD_REASONS), 6)
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

    # Wave 6 exclusions are point-in-time adjudications, not permanent bans: a
    # later candidate-keyed lane may supersede one with its own reviewed
    # contract. Every such supersession must be pinned here explicitly, with
    # the owning lane, so an accidental double promotion still fails.
    WAVE6_HCED_EXCLUSIONS_SUPERSEDED_BY_LATER_CONTRACTS = {
        # Wave 8 Egypt-forces lane resolved the 1967 Sinai fronts that Wave 6
        # held for the then-unresolvable "Egypt" identity; each row is now a
        # candidate-keyed exact contract owned by hced_wave8_egypt_forces_*.
        "hced-Abu Ageila1967-1",
        "hced-Bir Gafgafa1967-1",
        "hced-Gaza1967-1",
        "hced-Jebel Libni1967-1",
        "hced-Mitla Pass1967-1",
        "hced-Rafa1967-1",
    }

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
        superseded = self.WAVE6_HCED_EXCLUSIONS_SUPERSEDED_BY_LATER_CONTRACTS
        self.assertEqual(
            published_hced & set(WAVE6_HCED_CURATED_EXCLUSIONS), superseded
        )
        for candidate_id in sorted(superseded):
            owners = {
                str(event["id"])
                for event in events
                if str(event.get("hced_candidate_id")) == candidate_id
            }
            self.assertEqual(len(owners), 1, candidate_id)
            self.assertTrue(
                next(iter(owners)).startswith("hced_wave8_egypt_forces_"),
                candidate_id,
            )
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
            "spanish_isabelline_monarchy",
            "kingdom_spain_amadeo_i",
            "first_spanish_republic",
            "kingdom_montenegro",
            "spanish_restoration_monarchy",
            "spanish_bourbon_restoration",
            "state_israel",
            "transjordan_1946",
            "syrian_republic_1946",
            "syrian_arab_republic",
            "khedivate_egypt",
            "united_arab_republic_egypt",
        ):
            self.assertNotIn(forbidden, payload)
        for canonical in (
            "spanish_empire",
            "clio_q236_1853_31d59baa",
            "kingdom_egypt_1922",
            "clio_sy_syria_modern_1946_86597c89",
            "clio_q139708_1944_bc8bee86",
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
        override_ids = {entity["id"] for entity in WAVE6_1800_2021_ENTITY_OVERRIDES}
        protected_existing_ids = {
            "egypt_muhammad_ali",
            "clio_q801_1948_5abea45e",
            "clio_q810_1947_98de647a",
            "clio_q41137_1973_b05dea50",
            *WAVE6_REUSED_CANONICAL_ENTITY_IDS,
        }
        self.assertTrue(protected_existing_ids.isdisjoint(override_ids))

    def test_every_new_source_declares_family_metadata(self):
        ids = [source["id"] for source in WAVE6_1800_2021_SOURCES]
        self.assertEqual(len(ids), len(set(ids)))
        for source in WAVE6_1800_2021_SOURCES:
            self.assertTrue(source["source_family_id"])
            self.assertEqual(
                source["evidence_roles"],
                [
                    "identity_boundary_or_context_reference",
                    "outcome_consistency_crosscheck",
                ],
            )


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
            for entity in _json(ROOT / "data" / "release" / "entities.json")
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

    def test_exact_60_hced_promote_with_pinned_parties_and_outcomes(self):
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
        self.assertEqual(len(result["events"]), 60)
        self.assertEqual(
            {event["identity_resolution"] for event in result["events"]},
            {"exact_reviewed_candidate_contract"},
        )

    def test_parent_55_promotes_after_all_identity_boundaries_are_curated(self):
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
        self.assertEqual(len(result["events"]), 1)
        event = result["events"][0]
        self.assertEqual(event["iwd_parent_war_id"], "55")
        self.assertEqual(
            {participant["entity_id"] for participant in event["participants"]},
            {
                "kingdom_iraq",
                "kingdom_egypt_1922",
                "clio_sy_syria_modern_1946_86597c89",
                "clio_q139708_1944_bc8bee86",
                "clio_q810_1947_98de647a",
                "clio_q801_1948_5abea45e",
            },
        )
        self.assertNotIn("55", WAVE6_IWD_CURATED_PARENT_EXCLUSIONS)

    def test_exact_8_iwbd_promote_and_coalitions_are_complete(self):
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
        self.assertEqual(len(result["events"]), 8)
        by_id = {event["iwbd_candidate_id"]: event for event in result["events"]}
        sarandaporon = "iwbd-100-36-421"
        self.assertNotIn(sarandaporon, by_id)
        participants = {
            p["entity_id"] for p in by_id["iwbd-100-36-422"]["participants"]
        }
        self.assertEqual(
            participants,
            {"clio_q236_1853_31d59baa", "kingdom_serbia", "ottoman_empire"},
        )


if __name__ == "__main__":
    unittest.main()
