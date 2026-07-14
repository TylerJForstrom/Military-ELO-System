import unittest

from military_elo.audit import audit_dataset
from military_elo.config import ModelConfig
from military_elo.coverage import _explicit_outcome_families
from military_elo.models import Entity, Event, Source, TACTICAL_DIMENSIONS
from military_elo.promotion.hced import (
    promote_hced_crosswalk_rows,
    promote_hced_label_rows,
)
from military_elo.promotion.iwbd import promote_iwbd_battles
from military_elo.promotion.iwd import aggregate_iwd_parent_wars
from military_elo.promotion.ucdp import promote_ucdp_termination_episodes


def _assert_contract(test, event, source_id, family_id):
    test.assertEqual(event["outcome_source_ids"], [source_id])
    test.assertEqual(event["outcome_source_family_ids"], [family_id])
    test.assertIn(source_id, event["source_ids"])


class PromotionOutcomeSourceContractTests(unittest.TestCase):
    def test_hced_crosswalk_promotion_emits_direct_dataset_only(self):
        row = {
            "candidate_id": "hced-crosswalk-focused-1",
            "source_record_id": "hced-crosswalk-focused-1",
            "name": "Focused crosswalk engagement",
            "year_low": 1900,
            "year_best": 1900,
            "year_high": 1900,
            "side_1_raw": "Alpha",
            "side_2_raw": "Beta",
            "winner_raw": "Alpha",
            "loser_raw": "Beta",
            "seshat_side_1_candidates": ["alpha-code"],
            "seshat_side_2_candidates": ["beta-code"],
            "war_names": [],
            "scale_raw": 2,
            "source_row": 1,
        }
        owners = {
            "alpha-code": [
                {
                    "canonical_name_candidate": "Alpha",
                    "start_year": 1800,
                    "end_year": 2000,
                    "seshat_ids": ["alpha-code"],
                }
            ],
            "beta-code": [
                {
                    "canonical_name_candidate": "Beta",
                    "start_year": 1800,
                    "end_year": 2000,
                    "seshat_ids": ["beta-code"],
                }
            ],
        }

        result = promote_hced_crosswalk_rows(
            [row], owners, set(), lambda polity: None
        )
        self.assertEqual(len(result["events"]), 1)
        event = result["events"][0]
        self.assertIn("hced_seshat_crosswalk", event["source_ids"])
        self.assertIn("cliopatria_v020", event["source_ids"])
        _assert_contract(self, event, "hced_dataset", "hced")

    def test_hced_label_promotion_emits_direct_dataset_only(self):
        row = {
            "candidate_id": "hced-focused-1",
            "source_record_id": "hced-focused-1",
            "name": "Focused engagement",
            "year_low": 1900,
            "year_best": 1900,
            "year_high": 1900,
            "side_1_raw": "Alpha",
            "side_2_raw": "Beta",
            "winner_raw": "Alpha",
            "loser_raw": "Beta",
            "seshat_side_1_candidates": [],
            "seshat_side_2_candidates": [],
            "war_names": [],
            "scale_raw": 2,
            "source_row": 1,
        }

        def resolve_code(code, low_year, high_year):
            return f"code_{code}", None, None

        def resolve_label(label, low_year, high_year):
            return f"entity_{str(label).lower()}", None, None, "seed_alias"

        result = promote_hced_label_rows(
            [row], set(), set(), resolve_code, resolve_label, curated_exclusions={}
        )
        self.assertEqual(result["accepted"], 1)
        _assert_contract(
            self, result["events"][0], "hced_dataset", "hced"
        )

    def test_iwd_parent_promotion_emits_direct_dataset_only(self):
        component = {
            "candidate_id": "iwd-focused-1",
            "source_component_id": "1",
            "parent_war_id": "1",
            "parent_war_name": "FocusedWar1900",
            "name": "FocusedWar_Alpha_1900",
            "start_year": 1900,
            "end_year": 1900,
            "terminal_outcome_code": "1",
            "initiators": [{"name": "Alpha", "cow_code": "1"}],
            "targets": [{"name": "Beta", "cow_code": "2"}],
        }

        def resolve_party(name, cow_code, low_year, high_year):
            return f"entity_{name.lower()}", None

        result = aggregate_iwd_parent_wars(
            [component], [], resolve_party, curated_parent_exclusions={}
        )
        self.assertEqual(result["parents_promoted"], 1)
        _assert_contract(self, result["events"][0], "iwd_dataset", "iwd")

    def test_iwbd_promotion_excludes_registry_from_outcome_contract(self):
        battle = {
            "candidate_id": "iwbd-1-1-1",
            "name": "Focused battle",
            "war_name": "Focused war",
            "start_date": "1900-01-01",
            "end_date": "1900-01-02",
            "attacker_raw": "Alpha",
            "defender_raw": "Beta",
            "winner_raw": "Alpha",
            "battle_level_victor_role": "Attacker",
            "war_level_victor_role": "Initiator",
            "duration_days": "1",
            "source_row": 1,
        }

        def resolve_label(label, low_year, high_year):
            return f"entity_{str(label).lower()}", None

        result = promote_iwbd_battles(
            [battle],
            curated_seed_keys=set(),
            hced_event_keys=set(),
            resolve_label=resolve_label,
            hced_war_cluster_spans={},
            iwd_parent_ids=set(),
            curated_exclusions={},
        )
        self.assertEqual(result["battles_promoted"], 1)
        event = result["events"][0]
        self.assertIn("cliopatria_v020", event["source_ids"])
        _assert_contract(self, event, "iwbd_dataset", "iwbd")

    def test_ucdp_promotion_excludes_dyad_crosscheck_from_outcome_contract(self):
        episode = {
            "candidate_id": "ucdp-focused-1",
            "raw": {
                "conflict_id": "1",
                "c_epno": "1",
                "c_epid": "101",
                "year": "1901",
                "c_ep_startyear": "1900",
                "c_ep_endyear": "1901",
                "c_epterm": "1",
                "c_outcome": "3",
                "side_a": "Government of Alpha",
                "gwno_a": "1",
                "side_b": "Government of Beta",
                "gwno_b": "2",
                "side_a_2nd": "",
                "gwno_a_2nd": "",
                "side_b_2nd": "",
                "gwno_b_2nd": "",
                "c_ependdate": "",
                "c_ependprec": "1",
                "intensity_level": "1",
                "incompatibility": "1",
                "territory_name": "",
                "type_of_conflict": "2",
            },
        }

        def resolve_party(name, gwno, low_year, high_year):
            normalized = str(name).lower().removeprefix("government of ")
            return f"entity_{normalized}", None, "seed_label"

        result = promote_ucdp_termination_episodes(
            [episode], [], [], resolve_party, curated_exclusions={}
        )
        self.assertEqual(result["episodes_promoted"], 1)
        event = result["events"][0]
        self.assertIn("ucdp_termination_dyad", event["source_ids"])
        _assert_contract(
            self,
            event,
            "ucdp_termination_conflict",
            "ucdp_conflict_termination",
        )


class CoveragePrecedenceTests(unittest.TestCase):
    def test_event_contract_precedes_generic_outcome_role_fallback(self):
        sources = {
            "hced_dataset": {
                "id": "hced_dataset",
                "source_family_id": "hced",
                "evidence_roles": ["outcome"],
            },
            "other_dataset": {
                "id": "other_dataset",
                "source_family_id": "other",
                "evidence_role": "outcome",
            },
        }
        families, unusable, contract = _explicit_outcome_families(
            {
                "source_ids": ["hced_dataset", "other_dataset"],
                "outcome_source_ids": ["hced_dataset"],
                "outcome_source_family_ids": ["hced"],
            },
            sources,
        )
        self.assertTrue(contract)
        self.assertEqual(families, {"hced"})
        self.assertEqual(unusable, {})

    def test_empty_explicit_contract_does_not_fall_back_to_generic_source(self):
        families, unusable, contract = _explicit_outcome_families(
            {
                "source_ids": ["hced_dataset"],
                "outcome_source_family_ids": [],
            },
            {
                "hced_dataset": {
                    "source_family_id": "hced",
                    "evidence_roles": ["outcome"],
                }
            },
        )
        self.assertTrue(contract)
        self.assertEqual(families, set())
        self.assertEqual(unusable["missing"], 1)

    def test_generic_fallback_accepts_canonical_and_legacy_explicit_roles(self):
        event = {"source_ids": ["dataset"]}
        role_contracts = (
            {"evidence_roles": ["outcome"]},
            {"evidence_role": "outcome"},
            {"supports_outcome": True},
            {"outcome_evidence": True},
            {"claim_type": "outcome"},
        )
        for role_contract in role_contracts:
            with self.subTest(role_contract=role_contract):
                sources = {
                    "dataset": {
                        "source_family_id": "hced",
                        **role_contract,
                    }
                }
                self.assertEqual(
                    _explicit_outcome_families(event, sources),
                    ({"hced"}, {}, True),
                )

    def test_non_outcome_crosswalk_registry_dyad_and_manual_sources_do_not_count(self):
        sources = {
            "hced_seshat_crosswalk": {
                "source_family_id": "hced_seshat_crosswalk_file_11018172",
                "evidence_roles": ["identity_crosswalk"],
            },
            "cliopatria_v020": {
                "source_family_id": "cliopatria_v0_2_0",
                "evidence_roles": ["identity_registry"],
            },
            "ucdp_termination_dyad": {
                "source_family_id": "ucdp_conflict_termination",
                "evidence_roles": ["outcome_consistency_crosscheck"],
            },
            "curated_manual": {
                "source_family_id": "manual_reference",
                "evidence_roles": [
                    "curated_reference_pending_claim_level_outcome_locator"
                ],
            },
        }
        event = {"source_ids": sorted(sources)}

        self.assertEqual(
            _explicit_outcome_families(event, sources), (set(), {}, False)
        )


def _source(source_id="hced_dataset", family="hced", roles=("outcome",)):
    source = Source(source_id, "Source", "https://example.test/source")
    object.__setattr__(source, "source_family_id", family)
    object.__setattr__(source, "evidence_roles", tuple(roles))
    return source


def _event(source_ids=("hced_dataset",), outcome_ids=("hced_dataset",), families=("hced",)):
    event = Event.from_dict(
        {
            "id": "event-1",
            "name": "Event",
            "year": 1900,
            "event_type": "engagement",
            "participants": [
                {
                    "entity_id": "alpha",
                    "side": "a",
                    "outcome": {dimension: 1 for dimension in TACTICAL_DIMENSIONS},
                },
                {
                    "entity_id": "beta",
                    "side": "b",
                    "outcome": {dimension: 0 for dimension in TACTICAL_DIMENSIONS},
                },
            ],
            "source_ids": list(source_ids),
        }
    )
    object.__setattr__(event, "outcome_source_ids", tuple(outcome_ids))
    object.__setattr__(event, "outcome_source_family_ids", tuple(families))
    return event


def _audit_codes(event, sources):
    entities = [
        Entity("alpha", "Alpha", "state", 1800, 2000),
        Entity("beta", "Beta", "state", 1800, 2000),
    ]
    return {
        issue.code
        for issue in audit_dataset(entities, [event], sources, ModelConfig())
    }


class OutcomeSourceAuditTests(unittest.TestCase):
    def test_valid_paired_contract_passes_every_outcome_source_invariant(self):
        contract_codes = {
            code
            for code in _audit_codes(
                _event(), {"hced_dataset": _source()}
            )
            if "outcome_source" in code or "direct_outcome" in code
        }
        self.assertEqual(contract_codes, set())

    def test_registered_future_outcome_source_and_family_need_no_core_whitelist(self):
        event = _event(
            source_ids=("reviewed_source",),
            outcome_ids=("reviewed_source",),
            families=("reviewed_family",),
        )
        source = _source("reviewed_source", family="reviewed_family")
        contract_codes = {
            code
            for code in _audit_codes(event, {"reviewed_source": source})
            if "outcome_source" in code or "direct_outcome" in code
        }
        self.assertEqual(contract_codes, set())

    def test_pair_subset_role_family_and_known_source_invariants_fail_closed(self):
        cases = (
            (
                "unpaired",
                _event(families=()),
                {"hced_dataset": _source()},
                "unpaired_outcome_source_contract",
            ),
            (
                "duplicate",
                _event(
                    outcome_ids=("hced_dataset", "hced_dataset"),
                    families=("hced",),
                ),
                {"hced_dataset": _source()},
                "noncanonical_outcome_source_ids",
            ),
            (
                "not_generic_link",
                _event(source_ids=(), outcome_ids=("hced_dataset",)),
                {"hced_dataset": _source()},
                "outcome_source_not_linked",
            ),
            (
                "missing_source",
                _event(),
                {},
                "unknown_outcome_source",
            ),
            (
                "missing_role",
                _event(),
                {"hced_dataset": _source(roles=("identity_crosswalk",))},
                "outcome_source_missing_outcome_role",
            ),
            (
                "declared_family_mismatch",
                _event(families=("iwd",)),
                {"hced_dataset": _source()},
                "outcome_source_family_set_mismatch",
            ),
            (
                "unregistered_declared_family",
                _event(families=("invented",)),
                {"hced_dataset": _source()},
                "outcome_source_family_set_mismatch",
            ),
        )
        for label, event, sources, expected_code in cases:
            with self.subTest(label=label):
                self.assertIn(expected_code, _audit_codes(event, sources))


if __name__ == "__main__":
    unittest.main()
