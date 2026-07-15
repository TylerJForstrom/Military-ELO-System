import copy
import json
import unittest
from pathlib import Path

from military_elo.promotion.iwbd import promote_iwbd_battles
from military_elo.promotion.iwd import aggregate_iwd_parent_wars
from military_elo.promotion.policy import (
    HCED_LABEL_POLICIES,
    IDENTITY_DENY_WINDOWS,
    IWBD_CURATED_EXCLUSIONS,
    IWBD_REVIEWED_IDENTITY_BINDINGS,
    IWBD_REVIEWED_IDENTITY_COHORTS,
    IWD_COW_CODE_POLICIES,
    IWD_CURATED_PARENT_EXCLUSIONS,
    IWD_REVIEWED_PARENT_CONTRACTS,
)


ROOT = Path(__file__).resolve().parents[1]


def _party_rows(values):
    return [{"cow_code": code, "name": name} for code, name in values]


def _iwd_contract_rows(parent_ids=None):
    selected = set(parent_ids or IWD_REVIEWED_PARENT_CONTRACTS)
    rows = []
    for parent_id, contract in IWD_REVIEWED_PARENT_CONTRACTS.items():
        if parent_id not in selected:
            continue
        for candidate_id, fingerprint in contract["components"].items():
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "source_component_id": fingerprint["source_component_id"],
                    "parent_war_id": parent_id,
                    "parent_war_name": fingerprint["parent_war_name"],
                    "name": fingerprint["name"],
                    "start_year": int(fingerprint["start_year"]),
                    "end_year": int(fingerprint["end_year"]),
                    "initiators": _party_rows(fingerprint["initiators"]),
                    "targets": _party_rows(fingerprint["targets"]),
                    "allies": _party_rows(fingerprint["allies"]),
                    "adversaries": _party_rows(fingerprint["adversaries"]),
                    "terminal_outcome_code": fingerprint["terminal_outcome_code"],
                    "terminal_outcome": fingerprint["terminal_outcome"],
                    "joiner_decision": fingerprint["joiner_decision"] == "true",
                    "source_rows": [int(value) for value in fingerprint["source_rows"]],
                }
            )
    return rows


def _iwbd_contract_rows(candidate_ids=None):
    selected = set(candidate_ids or IWBD_REVIEWED_IDENTITY_BINDINGS)
    rows = []
    for candidate_id, contract in IWBD_REVIEWED_IDENTITY_BINDINGS.items():
        if candidate_id not in selected:
            continue
        row = {"candidate_id": candidate_id, **contract["fingerprint"]}
        row["source_row"] = int(row["source_row"])
        rows.append(row)
    return rows


def _exact_id_resolver(entity_id, low_year, high_year):
    return entity_id, None


class StrategicContractTests(unittest.TestCase):
    def test_contract_inventory_is_exactly_the_conservative_28(self):
        self.assertEqual(set(IWD_REVIEWED_PARENT_CONTRACTS), {
            "1", "39", "41", "43", "44", "57", "60", "91"
        })
        self.assertEqual(len(IWBD_REVIEWED_IDENTITY_BINDINGS), 20)
        turkey = {
            candidate_id
            for cohort, ids in IWBD_REVIEWED_IDENTITY_COHORTS.items()
            if cohort.startswith("turkish_national_movement")
            for candidate_id in ids
        }
        roc = {
            candidate_id
            for cohort, ids in IWBD_REVIEWED_IDENTITY_COHORTS.items()
            if cohort.startswith("roc_taiwan")
            for candidate_id in ids
        }
        self.assertEqual((len(turkey), len(roc)), (12, 6))
        self.assertEqual(8 + len(IWBD_REVIEWED_IDENTITY_BINDINGS), 28)

    def test_all_reviewed_iwd_parents_promote_once(self):
        result = aggregate_iwd_parent_wars(
            _iwd_contract_rows(),
            [],
            lambda name, code, low, high: (None, None),
            curated_parent_exclusions=IWD_CURATED_PARENT_EXCLUSIONS,
            reviewed_parent_contracts=IWD_REVIEWED_PARENT_CONTRACTS,
            resolve_reviewed_party=_exact_id_resolver,
            require_complete_reviewed_parents=True,
        )
        self.assertEqual(result["parents_promoted"], 8)
        self.assertEqual(
            {event["iwd_parent_war_id"] for event in result["events"]},
            set(IWD_REVIEWED_PARENT_CONTRACTS),
        )

    def test_iwd_component_set_and_fingerprint_drift_raise(self):
        missing_parent = [
            row for row in _iwd_contract_rows() if row["parent_war_id"] != "91"
        ]
        with self.assertRaisesRegex(ValueError, "complete parent is missing"):
            aggregate_iwd_parent_wars(
                missing_parent, [], lambda *args: (None, None),
                reviewed_parent_contracts=IWD_REVIEWED_PARENT_CONTRACTS,
                resolve_reviewed_party=_exact_id_resolver,
                require_complete_reviewed_parents=True,
            )

        rows = _iwd_contract_rows({"39"})
        with self.assertRaisesRegex(ValueError, "component set changed"):
            aggregate_iwd_parent_wars(
                rows[:-1], [], lambda *args: (None, None),
                reviewed_parent_contracts=IWD_REVIEWED_PARENT_CONTRACTS,
                resolve_reviewed_party=_exact_id_resolver,
            )

        changed = copy.deepcopy(rows)
        changed[0]["terminal_outcome_code"] = "1"
        with self.assertRaisesRegex(ValueError, "source fingerprint changed"):
            aggregate_iwd_parent_wars(
                changed, [], lambda *args: (None, None),
                reviewed_parent_contracts=IWD_REVIEWED_PARENT_CONTRACTS,
                resolve_reviewed_party=_exact_id_resolver,
            )

    def test_iwd_exact_id_resolver_drift_raises(self):
        with self.assertRaisesRegex(ValueError, "exact-ID resolver returned"):
            aggregate_iwd_parent_wars(
                _iwd_contract_rows({"1"}),
                [],
                lambda *args: (None, None),
                reviewed_parent_contracts=IWD_REVIEWED_PARENT_CONTRACTS,
                resolve_reviewed_party=lambda entity_id, low, high: ("wrong", None),
            )

    def test_all_reviewed_iwbd_battles_promote(self):
        result = promote_iwbd_battles(
            _iwbd_contract_rows(),
            set(),
            set(),
            lambda label, low, high: (None, None),
            {},
            set(IWD_REVIEWED_PARENT_CONTRACTS),
            reviewed_identity_bindings=IWBD_REVIEWED_IDENTITY_BINDINGS,
            reviewed_identity_cohorts=IWBD_REVIEWED_IDENTITY_COHORTS,
            resolve_reviewed_id=_exact_id_resolver,
            require_complete_reviewed_identity_cohorts=True,
        )
        self.assertEqual(result["battles_promoted"], 20)
        self.assertEqual(
            {event["iwbd_candidate_id"] for event in result["events"]},
            set(IWBD_REVIEWED_IDENTITY_BINDINGS),
        )

    def test_iwbd_cohort_and_fingerprint_drift_raise(self):
        missing_cohort = [
            row
            for row in _iwbd_contract_rows()
            if row["candidate_id"] != "iwbd-1-1-2"
        ]
        with self.assertRaisesRegex(ValueError, "candidate set incomplete"):
            promote_iwbd_battles(
                missing_cohort, set(), set(), lambda *args: (None, None), {}, set(),
                reviewed_identity_bindings=IWBD_REVIEWED_IDENTITY_BINDINGS,
                reviewed_identity_cohorts=IWBD_REVIEWED_IDENTITY_COHORTS,
                resolve_reviewed_id=_exact_id_resolver,
                require_complete_reviewed_identity_cohorts=True,
            )

        cohort = IWBD_REVIEWED_IDENTITY_COHORTS[
            "turkish_national_movement_greco_turkish"
        ]
        with self.assertRaisesRegex(ValueError, "candidate set incomplete"):
            promote_iwbd_battles(
                _iwbd_contract_rows(cohort[:-1]), set(), set(),
                lambda *args: (None, None), {}, set(),
                reviewed_identity_bindings=IWBD_REVIEWED_IDENTITY_BINDINGS,
                reviewed_identity_cohorts=IWBD_REVIEWED_IDENTITY_COHORTS,
                resolve_reviewed_id=_exact_id_resolver,
            )

        changed = _iwbd_contract_rows({"iwbd-1-1-2"})
        changed[0]["winner_raw"] = "Spain"
        with self.assertRaisesRegex(ValueError, "source fingerprint changed"):
            promote_iwbd_battles(
                changed, set(), set(), lambda *args: (None, None), {}, set(),
                reviewed_identity_bindings=IWBD_REVIEWED_IDENTITY_BINDINGS,
                reviewed_identity_cohorts=IWBD_REVIEWED_IDENTITY_COHORTS,
                resolve_reviewed_id=_exact_id_resolver,
            )

    def test_uncontracted_turkey_remains_denied(self):
        self.assertEqual(IDENTITY_DENY_WINDOWS["turkey"], ((1919, 1923),))
        row = {
            "candidate_id": "iwbd-999--9-9999",
            "source_row": 9999,
            "name": "Unreviewed clash",
            "war_name": "Unreviewed war",
            "start_date": "1921-01-01",
            "end_date": "1921-01-02",
            "duration_days": "2",
            "attacker_raw": "Turkey",
            "defender_raw": "Greece",
            "winner_raw": "Turkey",
            "battle_level_victor_role": "Attacker",
        }
        result = promote_iwbd_battles(
            [row], set(), set(),
            lambda label, low, high: (f"broad_{label.lower()}", None),
            {}, set(),
            reviewed_identity_bindings=IWBD_REVIEWED_IDENTITY_BINDINGS,
            reviewed_identity_cohorts=IWBD_REVIEWED_IDENTITY_COHORTS,
            resolve_reviewed_id=_exact_id_resolver,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(
            result["rejections"]["unresolved_time_bounded_belligerent"], 1
        )

    def test_uncontracted_latvia_remains_denied(self):
        self.assertEqual(IDENTITY_DENY_WINDOWS["latvia"], ((1918, 1991),))
        row = {
            "candidate_id": "iwbd-999--9-9998",
            "source_row": 9998,
            "name": "Unreviewed Latvian clash",
            "war_name": "Unreviewed war",
            "start_date": "1919-10-01",
            "end_date": "1919-10-02",
            "duration_days": "2",
            "attacker_raw": "Russia",
            "defender_raw": "Latvia",
            "winner_raw": "Latvia",
            "battle_level_victor_role": "Defender",
        }
        result = promote_iwbd_battles(
            [row], set(), set(),
            lambda label, low, high: (f"broad_{label.lower()}", None),
            {}, set(),
            reviewed_identity_bindings=IWBD_REVIEWED_IDENTITY_BINDINGS,
            reviewed_identity_cohorts=IWBD_REVIEWED_IDENTITY_COHORTS,
            resolve_reviewed_id=_exact_id_resolver,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(
            result["rejections"]["unresolved_time_bounded_belligerent"], 1
        )

    def test_corrected_unsafe_rows_are_explicitly_excluded(self):
        corrected_ids = {
            "iwbd-108-40-788",
            "iwbd-115-43-810",
            "iwbd-115-43-811",
            "iwbd-115-43-812",
        }
        self.assertLessEqual(corrected_ids, set(IWBD_CURATED_EXCLUSIONS))
        self.assertTrue(corrected_ids.isdisjoint(IWBD_REVIEWED_IDENTITY_BINDINGS))
        self.assertTrue(
            corrected_ids.isdisjoint(
                candidate_id
                for cohort in IWBD_REVIEWED_IDENTITY_COHORTS.values()
                for candidate_id in cohort
            )
        )
        rows = [
            {
                "candidate_id": "iwbd-108-40-788",
                "source_row": 788,
                "name": "Riga 2",
                "war_name": "Latvian Liberation",
                "start_date": "1919-10-08",
                "end_date": "1919-11-10",
                "duration_days": "34",
                "attacker_raw": "Russia",
                "defender_raw": "Latvia",
                "winner_raw": "Latvia",
                "battle_level_victor_role": "Defender",
            },
            {
                "candidate_id": "iwbd-115-43-810",
                "source_row": 810,
                "name": "Akbas",
                "war_name": "Second Greco-Turkish",
                "start_date": "1920-01-26",
                "end_date": "1920-01-27",
                "duration_days": "2",
                "attacker_raw": "Turkey",
                "defender_raw": "Greece",
                "winner_raw": "Turkey",
                "battle_level_victor_role": "Attacker",
            },
            {
                "candidate_id": "iwbd-115-43-811",
                "source_row": 811,
                "name": "Summer Offensive",
                "war_name": "Second Greco-Turkish",
                "start_date": "1920-06-15",
                "end_date": "1920-09-15",
                "duration_days": "93",
                "attacker_raw": "Greece",
                "defender_raw": "Turkey",
                "winner_raw": "Greece",
                "battle_level_victor_role": "Attacker",
            },
            {
                "candidate_id": "iwbd-115-43-812",
                "source_row": 812,
                "name": "Gediz",
                "war_name": "Second Greco-Turkish",
                "start_date": "1920-10-24",
                "end_date": "1920-11-12",
                "duration_days": "20",
                "attacker_raw": "Turkey",
                "defender_raw": "Greece",
                "winner_raw": "Inconclusive",
                "battle_level_victor_role": "Inconclusive",
            },
        ]
        result = promote_iwbd_battles(
            rows, set(), set(),
            lambda label, low, high: (f"broad_{label.lower()}", None),
            {}, set(),
            curated_exclusions=IWBD_CURATED_EXCLUSIONS,
            reviewed_identity_bindings=IWBD_REVIEWED_IDENTITY_BINDINGS,
            reviewed_identity_cohorts=IWBD_REVIEWED_IDENTITY_COHORTS,
            resolve_reviewed_id=_exact_id_resolver,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["curated_exclusion"], 4)

    def test_contract_identities_do_not_open_broad_resolvers(self):
        self.assertTrue({"220", "640", "713"}.isdisjoint(IWD_COW_CODE_POLICIES))
        self.assertTrue(
            {"taiwan", "turkey", "latvia", "estonia"}.isdisjoint(
                HCED_LABEL_POLICIES
            )
        )
        entities = {
            entity["id"]: entity
            for entity in json.loads(
                (ROOT / "data" / "seed" / "entities.json").read_text(encoding="utf-8")
            )
        }
        sources = {
            source["id"]
            for source in json.loads(
                (ROOT / "data" / "seed" / "sources.json").read_text(encoding="utf-8")
            )
        }
        self.assertNotIn("first_republic_latvia", entities)
        self.assertNotIn("latvia_president_state_history", sources)
        expected_windows = {
            "bourbon_restoration_france": (1815, 1830),
            "russian_sfsr": (1918, 1922),
            "first_republic_estonia": (1918, 1940),
            "turkish_national_movement": (1919, 1922),
        }
        for entity_id, window in expected_windows.items():
            with self.subTest(entity_id=entity_id):
                self.assertEqual(
                    (entities[entity_id]["start_year"], entities[entity_id]["end_year"]),
                    window,
                )
                self.assertEqual(entities[entity_id]["aliases"], [])


if __name__ == "__main__":
    unittest.main()
