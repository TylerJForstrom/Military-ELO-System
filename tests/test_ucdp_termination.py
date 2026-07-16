import json
import re
import unittest
from pathlib import Path

from military_elo.release import (
    UCDP_CURATED_EXCLUSIONS,
    UCDP_GW_CODE_POLICIES,
    _gw_policy_seed_id,
    _slug,
    _strategic_participants,
    promote_ucdp_termination_episodes,
    resolve_ucdp_party,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_EVENTS = PROJECT_ROOT / "data" / "release" / "events.json"
RELEASE_METADATA = PROJECT_ROOT / "data" / "release" / "metadata.json"
REGISTRY = PROJECT_ROOT / "data" / "catalog" / "registry.json"


def _episode(
    conflict_id,
    epno,
    start,
    end,
    outcome,
    side_a,
    gwno_a,
    side_b,
    gwno_b,
    *,
    epterm="1",
    ependdate=None,
    ependprec="1",
    intensity="1",
    incompatibility="1",
    second_a="",
    second_b="",
    gwno_second_a="",
    gwno_second_b="",
    type_of_conflict="2",
    territory="",
):
    return {
        "candidate_id": f"ucdp-term-{conflict_id}-{epno}",
        "raw": {
            "conflict_id": conflict_id,
            "c_epno": epno,
            "c_epid": f"{conflict_id}0{epno}",
            "year": str(end),
            "c_ep_startyear": str(start),
            "c_ep_endyear": str(end),
            "c_epterm": epterm,
            "c_outcome": outcome,
            "side_a": side_a,
            "gwno_a": gwno_a,
            "side_b": side_b,
            "gwno_b": gwno_b,
            "side_a_2nd": second_a,
            "gwno_a_2nd": gwno_second_a,
            "side_b_2nd": second_b,
            "gwno_b_2nd": gwno_second_b,
            "c_ependdate": ependdate or "",
            "c_ependprec": ependprec,
            "intensity_level": intensity,
            "incompatibility": incompatibility,
            "territory_name": territory,
            "type_of_conflict": type_of_conflict,
        },
    }


def _dyad(conflict_id, dyad_id, start, end, outcome, gwno_a, gwno_b, *, epterm="1"):
    return {
        "candidate_id": f"ucdp-dyad-{dyad_id}",
        "raw": {
            "conflict_id": conflict_id,
            "dyad_id": dyad_id,
            "d_epid": f"{dyad_id}01",
            "year": str(end),
            "d_ep_startyear": str(start),
            "d_ep_endyear": str(end),
            "d_epterm": epterm,
            "d_outcome": outcome,
            "gwno_a": gwno_a,
            "gwno_b": gwno_b,
        },
    }


def _war(event_id, cluster_id, low, high, entity_ids, terminations=None):
    return (event_id, cluster_id, low, high, frozenset(entity_ids), terminations or {})


def _snake(name):
    label = str(name).strip()
    if label.lower().startswith("government of "):
        label = label[len("government of "):]
    return "entity_" + re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


def _resolve_all(name, gwno, low_year, high_year):
    return _snake(name), None, "seed_label"


def _promote(episodes, dyads=(), war_index=(), resolver=_resolve_all, exclusions=None):
    return promote_ucdp_termination_episodes(
        list(episodes),
        list(dyads),
        list(war_index),
        resolver,
        curated_exclusions={} if exclusions is None else exclusions,
    )


def _label_context(seed_entities):
    return {
        "seed_entities": seed_entities,
        "release_entities": {},
        "entity_labels": {},
        "label_observations": {},
        "seed_by_id": {entity["id"]: entity for entity in seed_entities},
        "polity_alias_index": {},
        "seed_label_index": {},
    }


class _ExplosiveContext(dict):
    """A context whose consultation fails the test: policy codes must never
    fall through to label resolution."""

    def __getitem__(self, key):
        raise AssertionError("policy code fell through to the label path")

    def get(self, key, default=None):
        raise AssertionError("policy code fell through to the label path")


class GateTests(unittest.TestCase):
    def test_nonterminal_rows_are_never_rated(self) -> None:
        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200", epterm="0"),
            ]
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["not_terminal_episode"], 1)

    def test_peace_agreement_is_not_a_loss(self) -> None:
        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "1",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ]
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["outcome_peace_agreement"], 1)

    def test_ceasefire_is_not_an_outcome(self) -> None:
        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "2",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ]
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["outcome_ceasefire"], 1)

    def test_low_activity_is_not_an_outcome(self) -> None:
        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "5",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ]
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["outcome_low_activity"], 1)

    def test_actor_cessation_stays_staged(self) -> None:
        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "6",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ]
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["outcome_actor_ceased"], 1)

    def test_unknown_outcome_codes_are_never_coerced_into_results(self) -> None:
        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
                _episode("2", "1", 1970, 1971, "7",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ]
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["outcome_missing_or_unknown"], 2)

    def test_documented_side_attribution_dispute_stays_staged(self) -> None:
        episode = _episode("334", "1", 1974, 1974, "3",
                           "Government of China", "710",
                           "Government of Vietnam (North Vietnam)", "816")
        # Without the exclusion the episode is otherwise promotable.
        control = _promote([episode])
        self.assertEqual(control["episodes_promoted"], 1)
        result = _promote(
            [episode],
            exclusions={("334", "1"): "side_attribution_dispute: test"},
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["documented_side_attribution_dispute"], 1)
        # The real curated exclusion carries its documented reason verbatim.
        self.assertIn(("334", "1"), UCDP_CURATED_EXCLUSIONS)
        self.assertIn("Paracel", UCDP_CURATED_EXCLUSIONS[("334", "1")])

    def test_rejection_counters_sum_to_row_total(self) -> None:
        def resolver(name, gwno, low_year, high_year):
            if "Unmappable" in name:
                return None, None, None
            return _resolve_all(name, gwno, low_year, high_year)

        rows = [
            _episode("1", "1", 1970, 1971, "3",
                     "Government of Alpha", "100",
                     "Government of Beta", "200", epterm="0"),
            _episode("2", "1", 1970, 1971, "1",
                     "Government of Alpha", "100",
                     "Government of Beta", "200"),
            _episode("3", "1", 1970, 1971, "2",
                     "Government of Alpha", "100",
                     "Government of Beta", "200"),
            _episode("4", "1", 1970, 1971, "5",
                     "Government of Alpha", "100",
                     "Government of Beta", "200"),
            _episode("5", "1", 1970, 1971, "6",
                     "Government of Alpha", "100",
                     "Government of Beta", "200"),
            _episode("6", "1", 1970, 1971, "9",
                     "Government of Alpha", "100",
                     "Government of Beta", "200"),
            _episode("7", "1", 1970, 1971, "3",
                     "Government of Alpha", "100",
                     "Rebels of Beta", ""),
            _episode("8", "1", 1970, 1971, "3",
                     "Government of Unmappable", "100",
                     "Government of Beta", "200"),
            _episode("9", "1", 1980, 1981, "3",
                     "Government of Gamma", "300",
                     "Government of Delta", "400"),
        ]
        result = _promote(rows, resolver=resolver)
        self.assertEqual(result["rows_total"], 9)
        self.assertEqual(result["episodes_promoted"], 1)
        self.assertEqual(
            sum(result["rejections"].values()) + result["episodes_promoted"],
            result["rows_total"],
        )


class GwCodePolicyTests(unittest.TestCase):
    def test_gw_365_resolves_by_era_and_never_bridges_1918_1921(self) -> None:
        self.assertEqual(_gw_policy_seed_id("365", 1905, 1905), "russian_empire")
        self.assertEqual(_gw_policy_seed_id("365", 1956, 1956), "soviet_union")
        self.assertEqual(_gw_policy_seed_id("365", 1979, 1989), "soviet_union")
        self.assertIsNone(_gw_policy_seed_id("365", 1918, 1921))
        self.assertIsNone(_gw_policy_seed_id("365", 1917, 1922))
        self.assertIsNone(_gw_policy_seed_id("365", 1992, 1994))
        self.assertIsNone(_gw_policy_seed_id("999", 1956, 1956))

    def test_government_of_afghanistan_never_bridges_regimes(self) -> None:
        self.assertIsNone(_gw_policy_seed_id("700", 1979, 1979))
        self.assertIsNone(_gw_policy_seed_id("700", 2002, 2003))
        self.assertEqual(_gw_policy_seed_id("700", 1996, 2001), "taliban")
        self.assertEqual(
            _gw_policy_seed_id("700", 2004, 2021), "islamic_republic_afghanistan"
        )
        entity_id, polity, method = resolve_ucdp_party(
            "Government of Afghanistan", "700", 2001, 2001, _ExplosiveContext()
        )
        self.assertEqual((entity_id, polity, method), ("taliban", None, "gw_code_policy"))
        self.assertEqual(
            resolve_ucdp_party(
                "Government of Afghanistan", "700", 1979, 1979, _ExplosiveContext()
            ),
            (None, None, None),
        )

    def test_gw_816_ends_at_unification(self) -> None:
        self.assertEqual(_gw_policy_seed_id("816", 1974, 1974), "north_vietnam")
        self.assertIsNone(_gw_policy_seed_id("816", 1978, 1981))
        self.assertEqual(_gw_policy_seed_id("817", 1965, 1975), "south_vietnam")
        self.assertIsNone(_gw_policy_seed_id("817", 1976, 1976))

    def test_policy_codes_never_fall_through_to_labels(self) -> None:
        # A policy code outside its windows must stay unresolved without ever
        # consulting the label path, even when a label match would exist.
        gap_years = {
            "365": (1918, 1921),
            "816": (1978, 1981),
            "817": (1980, 1980),
            "700": (1979, 1979),
            "160": (1930, 1930),
            "355": (1908, 1908),
            "652": (1958, 1961),
        }
        self.assertEqual(set(gap_years), set(UCDP_GW_CODE_POLICIES))
        for code, (low, high) in gap_years.items():
            with self.subTest(code=code):
                self.assertEqual(
                    resolve_ucdp_party(
                        "Government of Anything", code, low, high, _ExplosiveContext()
                    ),
                    (None, None, None),
                )
        self.assertEqual(
            resolve_ucdp_party(
                "Government of Russia (Soviet Union)", "365", 1918, 1921,
                _ExplosiveContext(),
            ),
            (None, None, None),
        )


class IdentityTests(unittest.TestCase):
    def test_rebel_primary_party_stays_staged(self) -> None:
        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "PLO", ""),
            ]
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["nonstate_primary_party"], 1)

    def test_unresolved_party_quarantines_the_episode(self) -> None:
        def resolver(name, gwno, low_year, high_year):
            if "Beta" in name:
                return None, None, None
            return _resolve_all(name, gwno, low_year, high_year)

        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ],
            resolver=resolver,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["unresolved_time_bounded_party"], 1)

    def test_two_labels_resolving_to_one_entity_quarantine_the_episode(self) -> None:
        def resolver(name, gwno, low_year, high_year):
            return "entity_same", None, "seed_label"

        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ],
            resolver=resolver,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["same_or_empty_opposing_side"], 1)

    def test_parenthetical_label_variants_must_agree(self) -> None:
        agreeing = _label_context(
            [
                {
                    "id": "north_vietnam",
                    "name": "North Vietnam",
                    "aliases": ["Vietnam"],
                    "start_year": 1945,
                    "end_year": 1976,
                }
            ]
        )
        entity_id, _, method = resolve_ucdp_party(
            "Government of Vietnam (North Vietnam)", "", 1960, 1970, agreeing
        )
        self.assertEqual(entity_id, "north_vietnam")
        self.assertEqual(method, "seed_label")

        disagreeing = _label_context(
            [
                {
                    "id": "vietnam_unified",
                    "name": "Vietnam",
                    "aliases": [],
                    "start_year": 1900,
                    "end_year": 2000,
                },
                {
                    "id": "north_vietnam",
                    "name": "North Vietnam",
                    "aliases": [],
                    "start_year": 1945,
                    "end_year": 1976,
                },
            ]
        )
        self.assertEqual(
            resolve_ucdp_party(
                "Government of Vietnam (North Vietnam)", "", 1960, 1970, disagreeing
            ),
            (None, None, None),
        )

    def test_any_unresolvable_variant_fails_the_party(self) -> None:
        # Only the inner variant "North Vietnam" resolves; the base variant
        # "Vietnam" does not — strict semantics fail the whole party.
        context = _label_context(
            [
                {
                    "id": "north_vietnam",
                    "name": "North Vietnam",
                    "aliases": [],
                    "start_year": 1945,
                    "end_year": 1976,
                }
            ]
        )
        self.assertEqual(
            resolve_ucdp_party(
                "Government of Vietnam (North Vietnam)", "", 1960, 1970, context
            ),
            (None, None, None),
        )
        # Control: the inner variant alone resolves.
        entity_id, _, _ = resolve_ucdp_party(
            "Government of North Vietnam", "", 1960, 1970, context
        )
        self.assertEqual(entity_id, "north_vietnam")


class DedupTests(unittest.TestCase):
    def test_hungary_1956_defers_to_promoted_iwd_parent(self) -> None:
        war_index = [
            _war(
                "iwd_war_59_soviet_hungarian_1956",
                "iwd_parent_59",
                1956,
                1956,
                {"entity_hungary", "entity_soviet_union"},
                {"entity_soviet_union": "victory", "entity_hungary": "defeat"},
            )
        ]
        result = _promote(
            [
                _episode("250", "1", 1956, 1956, "4",
                         "Government of Hungary", "310",
                         "Government of Soviet Union", "365"),
            ],
            war_index=war_index,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["duplicate_of_promoted_strategic_event"], 1)
        self.assertEqual(
            result["duplicate_details"],
            [
                {
                    "conflict_id": "250",
                    "c_epno": "1",
                    "matched_event_id": "iwd_war_59_soviet_hungarian_1956",
                    "orientation": "agrees",
                }
            ],
        )

    def test_vietnam_1965_75_defers_to_curated_seed(self) -> None:
        war_index = [
            _war(
                "vietnam_war",
                "vietnam_war",
                1955,
                1975,
                {"entity_north_vietnam", "entity_south_vietnam", "entity_united_states"},
                {"entity_north_vietnam": "victory", "entity_south_vietnam": "defeat"},
            )
        ]
        result = _promote(
            [
                _episode("299", "1", 1965, 1975, "4",
                         "Government of South Vietnam", "817",
                         "Government of North Vietnam", "816"),
            ],
            war_index=war_index,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["duplicate_of_promoted_strategic_event"], 1)
        self.assertEqual(result["duplicate_details"][0]["matched_event_id"], "vietnam_war")

    def test_gulf_war_secondaries_widen_duplicate_detection(self) -> None:
        war_index = [
            _war(
                "iwd_war_82_gulf_war_1991",
                "iwd_parent_82",
                1990,
                1991,
                {"entity_iraq", "entity_united_states"},
            )
        ]
        without_secondary = _promote(
            [
                _episode("312", "1", 1990, 1991, "4",
                         "Government of Iraq", "645",
                         "Government of Kuwait", "690"),
            ],
            war_index=war_index,
        )
        self.assertEqual(without_secondary["episodes_promoted"], 1)
        with_secondary = _promote(
            [
                _episode("312", "1", 1990, 1991, "4",
                         "Government of Iraq", "645",
                         "Government of Kuwait", "690",
                         second_b="United States", gwno_second_b="2"),
            ],
            war_index=war_index,
        )
        self.assertEqual(with_secondary["events"], [])
        self.assertEqual(
            with_secondary["rejections"]["duplicate_of_promoted_strategic_event"], 1
        )

    def test_second_ogaden_1980_episode_is_a_new_event(self) -> None:
        war_index = [
            _war(
                "iwd_war_73_second_ogaden_1977_1978",
                "iwd_parent_73",
                1977,
                1978,
                {"entity_ethiopia", "entity_somalia"},
                {"entity_ethiopia": "victory", "entity_somalia": "defeat"},
            )
        ]
        result = _promote(
            [
                _episode("268", "3", 1980, 1980, "4",
                         "Government of Somalia", "520",
                         "Government of Ethiopia", "530"),
            ],
            war_index=war_index,
        )
        self.assertEqual(result["episodes_promoted"], 1)
        self.assertEqual(
            result["rejections"]["duplicate_of_promoted_strategic_event"], 0
        )

    def test_earlier_promoted_episode_blocks_overlapping_episode(self) -> None:
        result = _promote(
            [
                _episode("10", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
                _episode("11", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ]
        )
        self.assertEqual(result["episodes_promoted"], 1)
        self.assertEqual(result["events"][0]["ucdp_conflict_id"], "10")
        self.assertEqual(result["rejections"]["duplicate_of_promoted_strategic_event"], 1)
        self.assertEqual(
            result["duplicate_details"][0]["matched_event_id"],
            result["events"][0]["id"],
        )

    def test_dedup_requires_shared_entity_on_each_side(self) -> None:
        war_index = [
            _war("some_war", "some_cluster", 1970, 1971,
                 {"entity_alpha", "entity_x"})
        ]
        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ],
            war_index=war_index,
        )
        self.assertEqual(result["episodes_promoted"], 1)
        self.assertEqual(
            result["rejections"]["duplicate_of_promoted_strategic_event"], 0
        )

    def test_sibling_episode_inherits_the_ledger_cluster_of_its_deduped_twin(self) -> None:
        war_index = [
            _war(
                "iwd_war_73_second_ogaden_1977_1978",
                "iwd_parent_73",
                1977,
                1978,
                {"entity_ethiopia", "entity_somalia"},
                {"entity_ethiopia": "victory", "entity_somalia": "defeat"},
            )
        ]
        result = _promote(
            [
                _episode("268", "2", 1977, 1978, "4",
                         "Government of Somalia", "520",
                         "Government of Ethiopia", "530"),
                _episode("268", "3", 1980, 1980, "4",
                         "Government of Somalia", "520",
                         "Government of Ethiopia", "530"),
            ],
            war_index=war_index,
        )
        self.assertEqual(result["episodes_promoted"], 1)
        self.assertEqual(result["rejections"]["duplicate_of_promoted_strategic_event"], 1)
        event = result["events"][0]
        self.assertEqual(event["ucdp_episode_number"], "3")
        self.assertEqual(event["cluster_id"], "iwd_parent_73")
        self.assertEqual(
            event["ucdp_cluster_inherited_from"], "iwd_war_73_second_ogaden_1977_1978"
        )

    def test_two_distinct_ledger_clusters_fall_back_to_the_conflict_cluster(self) -> None:
        war_index = [
            _war("war_one", "cluster_one", 1970, 1971,
                 {"entity_alpha", "entity_beta"}),
            _war("war_two", "cluster_two", 1970, 1971,
                 {"entity_alpha", "entity_beta"}),
        ]
        result = _promote(
            [
                _episode("9", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
                _episode("9", "2", 1980, 1980, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ],
            war_index=war_index,
        )
        self.assertEqual(result["episodes_promoted"], 1)
        event = result["events"][0]
        self.assertEqual(event["cluster_id"], "ucdp_conflict_9")
        self.assertNotIn("ucdp_cluster_inherited_from", event)

    def test_duplicate_rejection_records_orientation(self) -> None:
        war_index = [
            _war(
                "yom_kippur",
                "iwd_parent_70",
                1973,
                1973,
                {"entity_egypt", "entity_israel"},
                {"entity_israel": "victory", "entity_egypt": "defeat"},
            )
        ]
        result = _promote(
            [
                _episode("11343", "3", 1973, 1973, "3",
                         "Government of Egypt", "651",
                         "Government of Israel", "666"),
            ],
            war_index=war_index,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["duplicate_details"][0]["orientation"], "contradicts")


class DyadConsistencyTests(unittest.TestCase):
    def _base_episode(self):
        return _episode("1", "1", 1970, 1971, "3",
                        "Government of Alpha", "100",
                        "Government of Beta", "200")

    def test_contradictory_dyad_victory_quarantines_the_episode(self) -> None:
        result = _promote(
            [self._base_episode()],
            dyads=[_dyad("1", "900", 1970, 1971, "3", "200", "100")],
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["dyad_conflict_outcome_contradiction"], 1)

    def test_same_pair_peace_agreement_dyad_contradicts_a_victory(self) -> None:
        result = _promote(
            [self._base_episode()],
            dyads=[_dyad("1", "900", 1970, 1971, "1", "100", "200")],
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["dyad_conflict_outcome_contradiction"], 1)

    def test_same_pair_ceasefire_dyad_contradicts_a_victory(self) -> None:
        result = _promote(
            [self._base_episode()],
            dyads=[_dyad("1", "900", 1970, 1971, "2", "100", "200")],
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["rejections"]["dyad_conflict_outcome_contradiction"], 1)

    def test_other_pair_peace_dyad_never_contradicts(self) -> None:
        result = _promote(
            [self._base_episode()],
            dyads=[_dyad("1", "900", 1970, 1971, "1", "100", "300")],
        )
        self.assertEqual(result["episodes_promoted"], 1)
        checks = result["events"][0]["ucdp_dyad_checks"]
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]["dyad_id"], "900")
        self.assertEqual(checks[0]["status"], "nonvictory_terminal_ignored")

    def test_low_activity_dyad_never_contradicts(self) -> None:
        result = _promote(
            [self._base_episode()],
            dyads=[_dyad("1", "900", 1970, 1971, "5", "200", "100")],
        )
        self.assertEqual(result["episodes_promoted"], 1)
        checks = result["events"][0]["ucdp_dyad_checks"]
        self.assertEqual(checks[0]["status"], "nonvictory_terminal_ignored")

    def test_corrupt_dyad_row_is_quarantined_not_repaired(self) -> None:
        corrupt = _dyad("1", "16562", 1970, 1971, "3", "100", "200")
        corrupt["raw"]["year"] = "8"
        result = _promote([self._base_episode()], dyads=[corrupt])
        self.assertEqual(result["dyad_rows_quarantined_corrupt"], 1)
        self.assertEqual(result["episodes_promoted"], 1)
        self.assertEqual(result["events"][0]["ucdp_dyad_checks"], [])

    def test_blank_outcome_terminal_dyad_is_counted_not_scanned(self) -> None:
        result = _promote(
            [self._base_episode()],
            dyads=[
                _dyad("1", "538", 1970, 1971, "", "100", "200"),
                _dyad("1", "901", 1970, 1971, "3", "100", "200"),
            ],
        )
        self.assertEqual(result["dyad_terminal_blank_outcome"], 1)
        self.assertEqual(result["episodes_promoted"], 1)
        checks = result["events"][0]["ucdp_dyad_checks"]
        self.assertEqual([c["dyad_id"] for c in checks], ["901"])
        self.assertEqual(checks[0]["status"], "consistent_victory")


class LinkedEpisodeTests(unittest.TestCase):
    def test_six_day_fronts_with_contradictory_orientations_all_stay_staged(self) -> None:
        rows = [
            _episode("301", "1", 1967, 1967, "3",
                     "Government of Israel", "666",
                     "Government of Jordan", "663",
                     ependdate="1967-06-10"),
            _episode("302", "1", 1967, 1967, "3",
                     "Government of Israel", "666",
                     "Government of Syria", "652",
                     ependdate="1967-06-10"),
            _episode("11343", "1", 1967, 1967, "3",
                     "Government of Egypt", "651",
                     "Government of Israel", "666",
                     ependdate="1967-06-10"),
        ]
        result = _promote(rows)
        self.assertEqual(result["events"], [])
        self.assertEqual(
            result["rejections"]["contradictory_linked_episode_outcomes"], 3
        )

    def test_consistent_same_day_fronts_promote_with_one_shared_cluster(self) -> None:
        rows = [
            _episode("301", "1", 1967, 1967, "3",
                     "Government of Israel", "666",
                     "Government of Jordan", "663",
                     ependdate="1967-06-10"),
            _episode("302", "1", 1967, 1967, "3",
                     "Government of Israel", "666",
                     "Government of Syria", "652",
                     ependdate="1967-06-10"),
        ]
        result = _promote(rows)
        self.assertEqual(result["episodes_promoted"], 2)
        expected_cluster = f"ucdp_linked_{_slug('1967-06-10', 24)}"
        clusters = {event["cluster_id"] for event in result["events"]}
        self.assertEqual(clusters, {expected_cluster})

    def test_different_end_dates_are_not_linked(self) -> None:
        rows = [
            _episode("20", "1", 1970, 1971, "3",
                     "Government of Alpha", "100",
                     "Government of Beta", "200",
                     ependdate="1971-05-01"),
            _episode("21", "1", 1970, 1971, "3",
                     "Government of Gamma", "300",
                     "Government of Alpha", "100",
                     ependdate="1971-08-01"),
        ]
        result = _promote(rows)
        self.assertEqual(result["episodes_promoted"], 2)
        clusters = sorted(event["cluster_id"] for event in result["events"])
        self.assertEqual(clusters, ["ucdp_conflict_20", "ucdp_conflict_21"])

    def test_ledger_cluster_beats_linked_cluster(self) -> None:
        war_index = [
            _war("w_old", "ledger_cluster_x", 1960, 1961,
                 {"entity_alpha", "entity_beta"}),
        ]
        rows = [
            _episode("30", "1", 1960, 1961, "3",
                     "Government of Alpha", "100",
                     "Government of Beta", "200"),
            _episode("30", "2", 1967, 1967, "3",
                     "Government of Alpha", "100",
                     "Government of Delta", "400",
                     ependdate="1967-06-10"),
            _episode("31", "1", 1967, 1967, "3",
                     "Government of Alpha", "100",
                     "Government of Epsilon", "500",
                     ependdate="1967-06-10"),
        ]
        result = _promote(rows, war_index=war_index)
        self.assertEqual(result["episodes_promoted"], 2)
        by_conflict = {event["ucdp_conflict_id"]: event for event in result["events"]}
        self.assertEqual(by_conflict["30"]["cluster_id"], "ledger_cluster_x")
        self.assertEqual(by_conflict["30"]["ucdp_cluster_inherited_from"], "w_old")
        self.assertEqual(
            by_conflict["31"]["cluster_id"], f"ucdp_linked_{_slug('1967-06-10', 24)}"
        )


class EmissionTests(unittest.TestCase):
    def test_severity_is_never_inferred_above_limited(self) -> None:
        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "4",
                         "Government of Alpha, Government of Gamma", "100,101",
                         "Government of Beta", "200"),
            ]
        )
        event = result["events"][0]
        self.assertEqual(event["event_type"], "war")
        self.assertEqual(event["war_type"], "interstate_limited")
        self.assertEqual(event["decisiveness"], 0.74)
        for participant in event["participants"]:
            self.assertIn(
                participant["result_class"], {"limited_victory", "limited_defeat"}
            )
            self.assertIn(participant["termination"], {"victory", "defeat"})
            self.assertGreaterEqual(participant["outcome"]["sovereignty_survival"], 0.7)
        losers = [p for p in event["participants"] if p["termination"] == "defeat"]
        self.assertEqual(len(losers), 2)
        self.assertEqual(losers[0]["outcome"]["sovereignty_survival"], 0.78)
        self.assertEqual(losers[0]["role"], "major_ally")
        self.assertEqual(losers[0]["contribution"], 0.5)

    def test_secondary_supporters_receive_no_outcome(self) -> None:
        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200",
                         second_a="Cuba"),
            ]
        )
        event = result["events"][0]
        rated_ids = {p["entity_id"] for p in event["participants"]}
        self.assertEqual(rated_ids, {"entity_alpha", "entity_beta"})
        self.assertNotIn("entity_cuba", rated_ids)
        secondaries = event["ucdp_secondary_parties"]["side_a"]
        self.assertEqual(len(secondaries), 1)
        self.assertEqual(secondaries[0]["name"], "Cuba")
        self.assertEqual(secondaries[0]["resolved_entity_id"], "entity_cuba")
        self.assertEqual(event["ucdp_secondary_parties"]["side_b"], [])

    def test_confidence_deductions(self) -> None:
        base = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ]
        )["events"][0]
        self.assertEqual(base["confidence"], 0.74)
        with_secondaries = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200",
                         second_b="Cuba"),
            ]
        )["events"][0]
        self.assertEqual(with_secondaries["confidence"], 0.69)
        year_precision = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200",
                         ependprec="5"),
            ]
        )["events"][0]
        self.assertEqual(year_precision["confidence"], 0.71)
        for event in (base, with_secondaries, year_precision):
            self.assertEqual(event["decisiveness"], 0.74)
            for participant in event["participants"]:
                self.assertEqual(
                    participant["evidence_confidence"], event["confidence"]
                )

    def test_scale_and_stakes_follow_declared_source_mappings(self) -> None:
        campaign_limited = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200",
                         intensity="1", incompatibility="1"),
            ]
        )["events"][0]
        self.assertEqual(campaign_limited["scale"], "campaign")
        self.assertEqual(campaign_limited["stakes"], "limited")
        major_war_major = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200",
                         intensity="2", incompatibility="2"),
            ]
        )["events"][0]
        self.assertEqual(major_war_major["scale"], "major_war")
        self.assertEqual(major_war_major["stakes"], "major")
        both_stakes = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200",
                         intensity="1", incompatibility="3"),
            ]
        )["events"][0]
        self.assertEqual(both_stakes["scale"], "campaign")
        self.assertEqual(both_stakes["stakes"], "major")

    def test_campaign_scale_participants_use_campaign_uniforms(self) -> None:
        campaign = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200",
                         intensity="1"),
            ]
        )["events"][0]
        self.assertEqual(campaign["geographic_scope"], 0.44)
        for participant in campaign["participants"]:
            self.assertEqual(participant["stakes"], 0.52)
            self.assertEqual(participant["national_scale"], 0.52)
        major = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200",
                         intensity="2"),
            ]
        )["events"][0]
        self.assertEqual(major["geographic_scope"], 0.68)
        for participant in major["participants"]:
            self.assertEqual(participant["stakes"], 0.72)
            self.assertEqual(participant["national_scale"], 0.72)

    def test_participant_note_is_ucdp_specific(self) -> None:
        result = _promote(
            [
                _episode("1", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ]
        )
        for participant in result["events"][0]["participants"]:
            self.assertIn("UCDP", participant["note"])
            self.assertNotIn("IWD", participant["note"])
        # The parametrized default keeps the IWD provenance sentence intact,
        # so committed IWD artifacts stay byte-identical.
        default_note = _strategic_participants(["a"], ["b"], "side_a", 0.7)[0]["note"]
        self.assertIn("IWD", default_note)

    def test_cluster_groups_episodes_of_one_conflict(self) -> None:
        result = _promote(
            [
                _episode("268", "1", 1970, 1971, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
                _episode("268", "2", 1980, 1980, "3",
                         "Government of Alpha", "100",
                         "Government of Beta", "200"),
            ]
        )
        self.assertEqual(result["episodes_promoted"], 2)
        clusters = {event["cluster_id"] for event in result["events"]}
        self.assertEqual(clusters, {"ucdp_conflict_268"})


@unittest.skipUnless(
    RELEASE_EVENTS.exists() and RELEASE_METADATA.exists() and REGISTRY.exists(),
    "release and registry artifacts not built",
)
class ReleaseArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads(RELEASE_EVENTS.read_text(encoding="utf-8"))
        cls.metadata = json.loads(RELEASE_METADATA.read_text(encoding="utf-8"))
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.ucdp_events = [
            e for e in cls.events if str(e["id"]).startswith("ucdp_term_")
        ]

    def test_release_has_at_most_one_event_per_ucdp_episode(self) -> None:
        self.assertTrue(self.ucdp_events)
        episode_keys = [
            (event["ucdp_conflict_id"], event["ucdp_episode_id"])
            for event in self.ucdp_events
        ]
        self.assertEqual(len(episode_keys), len(set(episode_keys)))
        event_ids = [event["id"] for event in self.ucdp_events]
        self.assertEqual(len(event_ids), len(set(event_ids)))

    def test_ucdp_events_never_claim_existential_outcomes(self) -> None:
        for event in self.ucdp_events:
            self.assertLessEqual(event["confidence"], 0.74)
            # war_type follows the source's type_of_conflict under the
            # exhaustive declared mapping; absence of the provenance field
            # means type 2 (interstate).
            conflict_type = event.get("ucdp_type_of_conflict", "2")
            self.assertEqual(
                event["war_type"],
                {
                    "1": "colonial_anti_colonial",
                    "2": "interstate_limited",
                    "3": "civil_war",
                    "4": "insurgency_intervention",
                }[conflict_type],
            )
            sides = {p["side"] for p in event["participants"]}
            self.assertGreaterEqual(len(sides), 2)
            for participant in event["participants"]:
                self.assertIn(
                    participant["result_class"], {"limited_victory", "limited_defeat"}
                )
                self.assertIn(participant["termination"], {"victory", "defeat"})
                self.assertGreaterEqual(
                    participant["outcome"]["sovereignty_survival"], 0.7
                )

    def test_six_day_war_is_not_in_the_ledger(self) -> None:
        blocked_conflicts = {"301", "302", "11343"}
        self.assertFalse(
            [
                event
                for event in self.ucdp_events
                if event["ucdp_conflict_id"] in blocked_conflicts
            ]
        )
        for prefix in ("ucdp_term_301_", "ucdp_term_302_", "ucdp_term_11343_"):
            self.assertFalse(
                [e for e in self.events if str(e["id"]).startswith(prefix)]
            )

    def test_paracel_1974_is_not_in_the_ledger(self) -> None:
        self.assertFalse(
            [e for e in self.ucdp_events if e["ucdp_conflict_id"] == "334"]
        )
        self.assertFalse(
            [e for e in self.events if str(e["id"]).startswith("ucdp_term_334_")]
        )
        exclusions = self.metadata["promotion"]["ucdp_curated_exclusions"]
        paracel = [
            entry
            for entry in exclusions
            if entry["conflict_id"] == "334" and entry["episode_number"] == "1"
        ]
        self.assertEqual(len(paracel), 1)
        self.assertIn("side_attribution_dispute", paracel[0]["reason"])

    def test_inherited_clusters_point_at_iwd_parents(self) -> None:
        by_conflict = {event["ucdp_conflict_id"]: event for event in self.ucdp_events}
        sino_indian = by_conflict["274"]
        self.assertEqual(sino_indian["cluster_id"], "iwd_parent_61")
        self.assertEqual(
            sino_indian["ucdp_cluster_inherited_from"], "iwd_war_61_sino_indian_1962"
        )
        ogaden = by_conflict["268"]
        self.assertEqual(ogaden["cluster_id"], "iwd_parent_73")
        for cluster_id in ("iwd_parent_61", "iwd_parent_73"):
            iwd_sharers = [
                e
                for e in self.events
                if str(e["id"]).startswith("iwd_war_")
                and e.get("cluster_id") == cluster_id
            ]
            self.assertEqual(len(iwd_sharers), 1, cluster_id)

    def test_promotion_accounting_matches_events(self) -> None:
        promotion = self.metadata["promotion"]
        self.assertEqual(promotion["accepted_ucdp_events"], len(self.ucdp_events))
        self.assertEqual(len(self.ucdp_events), 7)
        self.assertEqual(
            sum(promotion["ucdp_rejections"].values())
            + promotion["accepted_ucdp_events"],
            promotion["ucdp_termination_rows_total"],
        )
        self.assertEqual(
            len(promotion["ucdp_duplicate_details"]),
            promotion["ucdp_rejections"]["duplicate_of_promoted_strategic_event"],
        )

    def test_registry_coverage_counts_provisional_ucdp_events(self) -> None:
        coverage = self.registry["coverage"]
        self.assertEqual(coverage["provisional_ucdp_events"], len(self.ucdp_events))
        self.assertEqual(
            coverage["ucdp_termination_rows_total"],
            self.metadata["promotion"]["ucdp_termination_rows_total"],
        )


if __name__ == "__main__":
    unittest.main()
