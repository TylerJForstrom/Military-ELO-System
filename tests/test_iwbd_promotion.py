import json
import re
import unittest
from datetime import date
from pathlib import Path

from military_elo.models import TACTICAL_DIMENSIONS
from military_elo.release import (
    IWBD_COALITION_SIDE_LABELS,
    IWBD_CURATED_EXCLUSIONS,
    IDENTITY_DENY_WINDOWS,
    _cross_source_event_keys,
    _event_key,
    _war_tokens,
    _war_tokens_match,
    normalize_label,
    promote_iwbd_battles,
)
from military_elo.promotion.policy import (
    IWBD_REVIEWED_IDENTITY_BINDINGS,
    IWBD_REVIEWED_IDENTITY_COHORTS,
    IWBD_REVIEWED_CONCURRENT_DISTINCT_RELATIONS,
)
from military_elo.promotion.orchestrator import (
    EFFECTIVE_IWBD_REVIEWED_IDENTITY_BINDINGS,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_EVENTS = PROJECT_ROOT / "data" / "release" / "events.json"
RELEASE_METADATA = PROJECT_ROOT / "data" / "release" / "metadata.json"
REGISTRY = PROJECT_ROOT / "data" / "catalog" / "registry.json"
IWBD_CANDIDATES = PROJECT_ROOT / "data" / "review" / "iwbd-candidates.jsonl"
IWD_CANDIDATES = PROJECT_ROOT / "data" / "review" / "iwd-1.21-candidates.jsonl"

LIMITED_RESULT_CLASSES = {
    "limited_victory",
    "limited_defeat",
    "stalemate_or_inconclusive",
}


def _battle(
    candidate_id,
    name,
    war_name,
    start,
    end,
    attacker,
    defender,
    winner,
    role,
    war_level_role="Initiator",
):
    try:
        duration = str((date.fromisoformat(end) - date.fromisoformat(start)).days)
    except (TypeError, ValueError):
        duration = None
    return {
        "candidate_id": candidate_id,
        "name": name,
        "war_name": war_name,
        "start_date": start,
        "end_date": end,
        "attacker_raw": attacker,
        "defender_raw": defender,
        "winner_raw": winner,
        "battle_level_victor_role": role,
        "war_level_victor_role": war_level_role,
        "duration_days": duration,
        "source_row": int(candidate_id.rsplit("-", 1)[-1]),
        "source": "iwbd",
    }


def _snake(label):
    return re.sub(r"[^a-z0-9]+", "_", str(label).lower()).strip("_")


def _resolve_all(label, low_year, high_year):
    return f"entity_{_snake(label)}", None


def _promote(candidates, **overrides):
    arguments = {
        "curated_seed_keys": set(),
        "hced_event_keys": set(),
        "resolve_label": _resolve_all,
        "hced_war_cluster_spans": {},
        "iwd_parent_ids": set(),
    }
    arguments.update(overrides)
    return promote_iwbd_battles(candidates, **arguments)


class DedupTests(unittest.TestCase):
    def test_hced_duplicate_is_excluded_not_promoted(self) -> None:
        candidates = [
            _battle(
                "iwbd-1-1-3",
                "Cadiz",
                "Franco-Spanish",
                "1823-08-31",
                "1823-09-23",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
        ]
        result = _promote(candidates, hced_event_keys={_event_key("Cadiz", 1823)})
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 1)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["battles_promoted"], 0)

    def test_dedup_uses_all_hced_candidates_not_only_promoted(self) -> None:
        # The key set is built from every HCED candidate, including rows that
        # themselves failed HCED promotion (uncoded side, unresolved identity):
        # a staged HCED row may promote via a later milestone, and no battle
        # may ever be able to enter the ledger twice.
        staged_only_hced_keys = {_event_key("Trocadero", 1823)}
        candidates = [
            _battle(
                "iwbd-1-1-2",
                "Trocadero",
                "Franco-Spanish",
                "1823-08-31",
                "1823-08-31",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
        ]
        result = _promote(candidates, hced_event_keys=staged_only_hced_keys)
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 1)
        self.assertEqual(result["events"], [])

    def test_name_year_window_tolerates_one_year_offset(self) -> None:
        hced_keys = {_event_key("Alma", 1854)}
        near = [
            _battle(
                "iwbd-22-8-40",
                "Alma",
                "Crimean",
                "1855-06-01",
                "1855-06-02",
                "France",
                "Russia",
                "France",
                "Attacker",
            ),
        ]
        result = _promote(near, hced_event_keys=hced_keys)
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 1)
        self.assertEqual(result["events"], [])

        far = [
            _battle(
                "iwbd-22-8-41",
                "Alma",
                "Crimean",
                "1856-06-01",
                "1856-06-02",
                "France",
                "Russia",
                "France",
                "Attacker",
            ),
        ]
        result = _promote(far, hced_event_keys=hced_keys)
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 0)
        self.assertEqual(len(result["events"]), 1)

    def test_hced_keys_cover_interior_years_of_wide_ranges(self) -> None:
        # A wide-span HCED candidate (Nakfa 1977-1988) contributes a key for
        # every interior year, so an IWBD battle dated in the middle of the
        # span can never slip past the dedup gate.
        hced_keys = {_event_key("Nakfa", year) for year in range(1977, 1989)}
        candidates = [
            _battle(
                "iwbd-186-79-1400",
                "Nakfa",
                "Eritrean",
                "1982-02-15",
                "1982-03-20",
                "Ethiopia",
                "Eritrea",
                "Eritrea",
                "Defender",
            ),
        ]
        result = _promote(candidates, hced_event_keys=hced_keys)
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 1)
        self.assertEqual(result["events"], [])

    def test_battle_and_siege_prefixes_are_stripped_before_matching(self) -> None:
        candidates = [
            _battle(
                "iwbd-1-1-3",
                "Siege of Cadiz",
                "Franco-Spanish",
                "1823-08-31",
                "1823-09-23",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
        ]
        result = _promote(candidates, hced_event_keys={_event_key("Cadiz", 1823)})
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 1)
        self.assertEqual(result["events"], [])

    def test_cross_source_ordinal_spellings_are_canonicalized(self) -> None:
        candidate = _battle(
            "iwbd-1-1-101",
            "Plevna 1",
            "Example War",
            "1900-01-01",
            "1900-01-02",
            "A",
            "B",
            "A",
            "Attacker",
        )
        hced_key = _event_key("Plevna (1st)", 1900)
        result = _promote(
            [candidate],
            hced_event_keys={hced_key: {"exact": True, "outcomes": set()}},
        )
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 1)
        self.assertEqual(result["events"], [])

    def test_cross_source_compatible_suffix_paths_are_canonicalized(self) -> None:
        cases = (
            ("Al Faw 2", "Al Faw"),
            ("Binh Gia (a)", "Binh Gia"),
            ("Plevna 1 (a)", "Plevna (1st)"),
        )
        for index, (iwbd_name, hced_name) in enumerate(cases, start=1):
            with self.subTest(iwbd=iwbd_name, hced=hced_name):
                candidate = _battle(
                    f"iwbd-1-1-{100 + index}",
                    iwbd_name,
                    "Example War",
                    "1900-01-01",
                    "1900-01-02",
                    "A",
                    "B",
                    "A",
                    "Attacker",
                )
                result = _promote(
                    [candidate],
                    hced_event_keys={
                        key: {
                            "exact": False,
                            "outcomes": {
                                (frozenset({"entity_a"}), frozenset({"entity_b"}))
                            },
                        }
                        for key in _cross_source_event_keys(hced_name, 1900)
                    },
                )
                self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 1)
                self.assertEqual(result["events"], [])

    def test_different_explicit_suffix_branches_do_not_share_a_fuzzy_key(self) -> None:
        cases = (
            ("Plevna 2", "Plevna 1"),
            ("Plevna 1 (b)", "Plevna 1 (a)"),
        )
        outcome = (frozenset({"entity_a"}), frozenset({"entity_b"}))
        for index, (iwbd_name, hced_name) in enumerate(cases, start=1):
            with self.subTest(iwbd=iwbd_name, hced=hced_name):
                candidate = _battle(
                    f"iwbd-1-1-{103 + index}",
                    iwbd_name,
                    "Example War",
                    "1900-01-01",
                    "1900-01-02",
                    "A",
                    "B",
                    "A",
                    "Attacker",
                )
                hced_index = {
                    _event_key(hced_name, 1900): {
                        "exact": True,
                        "outcomes": set(),
                    },
                    **{
                        key: {"exact": False, "outcomes": {outcome}}
                        for key in _cross_source_event_keys(hced_name, 1900)
                    },
                }
                result = _promote([candidate], hced_event_keys=hced_index)
                self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 0)
                self.assertEqual(len(result["events"]), 1)

    def test_arbitrary_terminal_number_is_not_treated_as_an_ordinal(self) -> None:
        candidate = _battle(
            "iwbd-1-1-105",
            "Hill 203",
            "Example War",
            "1900-01-01",
            "1900-01-02",
            "A",
            "B",
            "A",
            "Attacker",
        )
        outcome = (frozenset({"entity_a"}), frozenset({"entity_b"}))
        hced_index = {
            key: {"exact": False, "outcomes": {outcome}}
            for key in _cross_source_event_keys("Hill", 1900)
        }
        result = _promote([candidate], hced_event_keys=hced_index)
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 0)
        self.assertEqual(len(result["events"]), 1)

    def test_unsuffixed_name_does_not_dedup_different_outcome_sides(self) -> None:
        candidate = _battle(
            "iwbd-1-1-104",
            "Al Faw 2",
            "Example War",
            "1900-01-01",
            "1900-01-02",
            "A",
            "B",
            "A",
            "Attacker",
        )
        hced_index = {
            key: {
                "exact": False,
                "outcomes": {(frozenset({"entity_c"}), frozenset({"entity_d"}))},
            }
            for key in _cross_source_event_keys("Al Faw", 1900)
        }
        result = _promote([candidate], hced_event_keys=hced_index)
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 0)
        self.assertEqual(len(result["events"]), 1)

    def test_unsuffixed_name_does_not_use_exact_match_year_tolerance(self) -> None:
        candidate = _battle(
            "iwbd-219-84-1692",
            "Badme 2 (a)",
            "Badme Border",
            "1999-02-06",
            "1999-02-10",
            "Ethiopia",
            "Eritrea",
            "Eritrea",
            "Defender",
        )
        same_orientation_previous_year = (
            frozenset({"entity_eritrea"}),
            frozenset({"entity_ethiopia"}),
        )
        opposite_orientation_same_year = (
            frozenset({"entity_ethiopia"}),
            frozenset({"entity_eritrea"}),
        )
        hced_index = {}
        for year, outcome in (
            (1998, same_orientation_previous_year),
            (1999, opposite_orientation_same_year),
        ):
            hced_index[_event_key("Badme", year)] = {
                "exact": True,
                "outcomes": set(),
            }
            for key in _cross_source_event_keys("Badme", year):
                hced_index[key] = {"exact": False, "outcomes": {outcome}}
        result = _promote([candidate], hced_event_keys=hced_index)
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 0)
        self.assertEqual(
            [event["iwbd_candidate_id"] for event in result["events"]],
            ["iwbd-219-84-1692"],
        )

    def test_curated_iwbd_exclusion_is_counted_before_other_gates(self) -> None:
        candidate_id = next(iter(IWBD_CURATED_EXCLUSIONS))
        result = _promote(
            [
                _battle(
                    candidate_id,
                    "Excluded battle",
                    "Example War",
                    "1900-01-01",
                    "1900-01-02",
                    "A",
                    "B",
                    "A",
                    "Attacker",
                )
            ]
        )
        self.assertEqual(result["rejections"]["curated_exclusion"], 1)
        self.assertEqual(result["events"], [])

    def test_curated_seed_battle_is_excluded(self) -> None:
        candidates = [
            _battle(
                "iwbd-139-53-700",
                "Midway",
                "World War II (Pacific)",
                "1942-06-04",
                "1942-06-07",
                "United States",
                "Japan",
                "United States",
                "Defender",
            ),
        ]
        result = _promote(candidates, curated_seed_keys={_event_key("Midway", 1942)})
        self.assertEqual(result["rejections"]["duplicate_of_curated_seed"], 1)
        self.assertEqual(result["events"], [])

    def test_same_battle_in_two_iwbd_wars_enters_once(self) -> None:
        # Vilna 1920 is coded under both the Lithuanian-Polish and the
        # Russo-Polish wars; the first occurrence by source_row wins.
        first = _battle(
            "iwbd-103-41-610",
            "Vilna",
            "Lithuanian-Polish",
            "1920-10-08",
            "1920-10-09",
            "Poland",
            "Lithuania",
            "Poland",
            "Attacker",
        )
        second = _battle(
            "iwbd--9--9-620",
            "Vilna",
            "Russo-Polish",
            "1920-10-08",
            "1920-10-09",
            "Poland",
            "Russia",
            "Poland",
            "Attacker",
        )
        result = _promote([second, first])
        self.assertEqual(result["rejections"]["duplicate_within_iwbd"], 1)
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(result["events"][0]["iwbd_candidate_id"], "iwbd-103-41-610")

    def test_each_hced_duplicate_is_counted_in_its_source_lane(self) -> None:
        # Rejected rows do not claim within-IWBD keys; both copies therefore
        # receive the accurate HCED-duplicate disposition.
        rows = [
            _battle(
                "iwbd-1-1-3",
                "Cadiz",
                "Franco-Spanish",
                "1823-08-31",
                "1823-09-23",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
            _battle(
                "iwbd-1-1-4",
                "Cadiz",
                "Franco-Spanish",
                "1823-09-01",
                "1823-09-23",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
        ]
        result = _promote(rows, hced_event_keys={_event_key("Cadiz", 1823)})
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 2)
        self.assertEqual(result["rejections"]["duplicate_within_iwbd"], 0)
        self.assertEqual(result["events"], [])

    def test_rejected_earlier_copy_does_not_suppress_valid_later_copy(self) -> None:
        rows = [
            _battle(
                "iwbd-1-1-1",
                "Example",
                "Example War",
                "1900-01-01",
                "1900-01-02",
                "A",
                "B",
                "C",
                "Attacker",
            ),
            _battle(
                "iwbd-1-1-2",
                "Example",
                "Example War",
                "1900-01-01",
                "1900-01-02",
                "A",
                "B",
                "A",
                "Attacker",
            ),
        ]
        result = _promote(rows)
        self.assertEqual(result["rejections"]["outcome_not_aligned_to_battle_sides"], 1)
        self.assertEqual(result["rejections"]["duplicate_within_iwbd"], 0)
        self.assertEqual(
            [event["iwbd_candidate_id"] for event in result["events"]],
            ["iwbd-1-1-2"],
        )


class ContainmentTests(unittest.TestCase):
    def _plevna_umbrella(self, source_row=281):
        return _battle(
            f"iwbd-61-22-{source_row}",
            "Plevna",
            "Second Russo-Turkish",
            "1877-07-20",
            "1877-12-10",
            "Russia",
            "Turkey",
            "Russia",
            "Attacker",
        )

    def _plevna_constituent(self, source_row=279):
        return _battle(
            f"iwbd-61-22-{source_row}",
            "Plevna 2",
            "Second Russo-Turkish",
            "1877-07-30",
            "1877-07-31",
            "Russia",
            "Turkey",
            "Turkey",
            "Defender",
        )

    def test_umbrella_containing_shorter_sibling_is_staged(self) -> None:
        result = _promote([self._plevna_constituent(279), self._plevna_umbrella(281)])
        self.assertEqual(result["rejections"]["contains_constituent_iwbd_rows"], 1)
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(result["events"][0]["name"], "Plevna 2")

    def test_containment_is_order_independent(self) -> None:
        # The umbrella precedes its constituent by source_row; the pre-pass
        # groups all named, dated rows, so it is still staged.
        result = _promote([self._plevna_umbrella(100), self._plevna_constituent(200)])
        self.assertEqual(result["rejections"]["contains_constituent_iwbd_rows"], 1)
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(result["events"][0]["name"], "Plevna 2")

    def test_equal_spans_do_not_contain_each_other(self) -> None:
        rows = [
            _battle(
                "iwbd-61-22-300",
                "Shipka Pass",
                "Second Russo-Turkish",
                "1877-08-21",
                "1877-08-26",
                "Turkey",
                "Russia",
                "Russia",
                "Defender",
            ),
            _battle(
                "iwbd-61-22-301",
                "Lovcha",
                "Second Russo-Turkish",
                "1877-08-21",
                "1877-08-26",
                "Russia",
                "Turkey",
                "Russia",
                "Attacker",
            ),
        ]
        result = _promote(rows)
        self.assertEqual(result["rejections"]["contains_constituent_iwbd_rows"], 0)
        self.assertEqual(len(result["events"]), 2)

    def test_same_normalized_name_is_dedup_not_containment(self) -> None:
        rows = [
            _battle(
                "iwbd-61-22-281",
                "Plevna",
                "Second Russo-Turkish",
                "1877-07-20",
                "1877-12-10",
                "Russia",
                "Turkey",
                "Russia",
                "Attacker",
            ),
            _battle(
                "iwbd-61-22-282",
                "Plevna",
                "Second Russo-Turkish",
                "1877-09-01",
                "1877-09-03",
                "Russia",
                "Turkey",
                "Turkey",
                "Defender",
            ),
        ]
        result = _promote(rows)
        self.assertEqual(result["rejections"]["duplicate_within_iwbd"], 1)
        self.assertEqual(result["rejections"]["contains_constituent_iwbd_rows"], 0)
        self.assertEqual(len(result["events"]), 1)

    def test_containment_requires_same_cow_war_and_war_name(self) -> None:
        # The raw war_name (theater suffix retained) is part of the grouping
        # key, so a long Pacific engagement never "contains" a short European
        # one merely by date bracketing.
        rows = [
            _battle(
                "iwbd-139-53-710",
                "Guadalcanal",
                "World War II (Pacific)",
                "1942-08-07",
                "1943-02-09",
                "United States",
                "Japan",
                "United States",
                "Attacker",
            ),
            _battle(
                "iwbd-139-53-711",
                "El Alamein 2",
                "World War II (Europe)",
                "1942-10-23",
                "1942-11-05",
                "United Kingdom",
                "Germany",
                "United Kingdom",
                "Attacker",
            ),
        ]
        result = _promote(rows)
        self.assertEqual(result["rejections"]["contains_constituent_iwbd_rows"], 0)
        self.assertEqual(len(result["events"]), 2)

    def test_container_is_staged_even_if_constituent_fails_later_gates(self) -> None:
        # The constituent is itself an HCED duplicate; the umbrella is still a
        # campaign umbrella (its fighting enters via HCED), so both stay out.
        rows = [self._plevna_constituent(279), self._plevna_umbrella(281)]
        result = _promote(rows, hced_event_keys={_event_key("Plevna 2", 1877)})
        self.assertEqual(result["rejections"]["duplicate_of_hced_battle"], 1)
        self.assertEqual(result["rejections"]["contains_constituent_iwbd_rows"], 1)
        self.assertEqual(result["events"], [])

    @staticmethod
    def _reviewed_mishan_rows():
        chalainor = _battle(
            "iwbd-118-45-840",
            "Chalainor 2",
            "Manchurian",
            "1929-11-17",
            "1929-11-17",
            "USSR",
            "China",
            "USSR",
            "Attacker",
        )
        chalainor["duration_days"] = "1"
        mishan = _battle(
            "iwbd-118-45-842",
            "Mishan",
            "Manchurian",
            "1929-11-17",
            "1929-11-18",
            "USSR",
            "China",
            "USSR",
            "Attacker",
        )
        mishan["duration_days"] = "2"
        return chalainor, mishan

    def test_reviewed_mishan_relation_promotes_both_distinct_operations(self) -> None:
        chalainor, mishan = self._reviewed_mishan_rows()
        result = _promote([mishan, chalainor])
        self.assertEqual(result["rejections"]["contains_constituent_iwbd_rows"], 0)
        self.assertEqual(
            {event["iwbd_candidate_id"] for event in result["events"]},
            {"iwbd-118-45-840", "iwbd-118-45-842"},
        )

    def test_reviewed_mishan_relation_fails_on_missing_sibling(self) -> None:
        _, mishan = self._reviewed_mishan_rows()
        with self.assertRaisesRegex(ValueError, "pinned sibling iwbd-118-45-840"):
            _promote([mishan])

    def test_reviewed_mishan_relation_fails_on_fingerprint_drift(self) -> None:
        chalainor, mishan = self._reviewed_mishan_rows()
        chalainor["name"] = "Dalainor 2"
        with self.assertRaisesRegex(ValueError, "source fingerprint changed"):
            _promote([chalainor, mishan])

    def test_reviewed_mishan_relation_fails_on_new_contained_sibling(self) -> None:
        chalainor, mishan = self._reviewed_mishan_rows()
        extra = _battle(
            "iwbd-118-45-999",
            "Unreviewed operation",
            "Manchurian",
            "1929-11-18",
            "1929-11-18",
            "USSR",
            "China",
            "USSR",
            "Attacker",
        )
        with self.assertRaisesRegex(ValueError, "contained sibling set changed"):
            _promote([chalainor, mishan, extra])


class OutcomeTests(unittest.TestCase):
    def test_inconclusive_is_a_coded_stalemate_not_unknown(self) -> None:
        candidates = [
            _battle(
                "iwbd-106-77-905",
                "Dezful",
                "Iran-Iraq",
                "1981-01-05",
                "1981-01-08",
                "Iran",
                "Iraq",
                "Inconclusive",
                "Inconclusive",
            ),
        ]
        result = _promote(candidates)
        self.assertEqual(len(result["events"]), 1)
        event = result["events"][0]
        self.assertEqual(event["decisiveness"], 0.32)
        for participant in event["participants"]:
            self.assertEqual(participant["result_class"], "stalemate_or_inconclusive")
            self.assertEqual(participant["termination"], "inconclusive_engagement")
            self.assertEqual(
                participant["outcome"],
                {dimension: 0.50 for dimension in TACTICAL_DIMENSIONS},
            )

    def test_missing_winner_is_never_coerced_into_a_result(self) -> None:
        candidates = [
            _battle(
                "iwbd-106-77-906",
                "Mehran",
                "Iran-Iraq",
                "1986-05-14",
                "1986-05-17",
                "Iraq",
                "Iran",
                "",
                "",
            ),
        ]
        result = _promote(candidates)
        self.assertEqual(result["rejections"]["outcome_not_aligned_to_battle_sides"], 1)
        self.assertEqual(result["events"], [])

    def test_winner_must_match_a_named_side(self) -> None:
        candidates = [
            _battle(
                "iwbd-1-1-5",
                "Irun",
                "Franco-Spanish",
                "1823-04-10",
                "1823-04-11",
                "France",
                "Spain",
                "Sweden",
                "Attacker",
            ),
        ]
        result = _promote(candidates)
        self.assertEqual(result["rejections"]["outcome_not_aligned_to_battle_sides"], 1)
        self.assertEqual(result["events"], [])

    def test_victor_role_must_agree_with_winner_label(self) -> None:
        candidates = [
            _battle(
                "iwbd-1-1-6",
                "Pamplona",
                "Franco-Spanish",
                "1823-09-10",
                "1823-09-16",
                "France",
                "Spain",
                "Spain",
                "Attacker",
            ),
        ]
        result = _promote(candidates)
        self.assertEqual(result["rejections"]["outcome_not_aligned_to_battle_sides"], 1)
        self.assertEqual(result["events"], [])

    def test_war_level_victor_is_ignored(self) -> None:
        # The war-level victor code describes the enclosing war, a different
        # evidence layer; flipping it changes nothing at the battle layer.
        def build(war_level_role):
            return _battle(
                "iwbd-1-1-7",
                "Bidasoa",
                "Franco-Spanish",
                "1823-04-07",
                "1823-04-07",
                "France",
                "Spain",
                "France",
                "Attacker",
                war_level_role=war_level_role,
            )

        as_initiator = _promote([build("Initiator")])
        as_target = _promote([build("Target")])
        self.assertEqual(len(as_initiator["events"]), 1)
        self.assertEqual(len(as_target["events"]), 1)
        self.assertEqual(
            as_initiator["events"][0]["participants"],
            as_target["events"][0]["participants"],
        )

    def test_severity_never_exceeds_limited(self) -> None:
        candidates = [
            _battle(
                "iwbd-1-1-8",
                "Logrono",
                "Franco-Spanish",
                "1823-04-17",
                "1823-04-18",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
        ]
        result = _promote(candidates)
        event = result["events"][0]
        for participant in event["participants"]:
            self.assertIn(participant["result_class"], LIMITED_RESULT_CLASSES)
            self.assertLessEqual(set(participant["outcome"]), TACTICAL_DIMENSIONS)

    def test_confidence_and_scale_defaults_are_pinned(self) -> None:
        candidates = [
            _battle(
                "iwbd-1-1-9",
                "Sarria",
                "Franco-Spanish",
                "1823-05-20",
                "1823-05-21",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
        ]
        result = _promote(candidates)
        event = result["events"][0]
        self.assertEqual(event["confidence"], 0.70)
        self.assertEqual(event["scale"], "battle")
        self.assertEqual(event["stakes"], "limited")
        self.assertEqual(event["decisiveness"], 0.66)
        self.assertEqual(event["geographic_scope"], 0.26)
        self.assertEqual(event["event_type"], "engagement")
        self.assertEqual(event["date_precision"], "day")
        winner = next(p for p in event["participants"] if p["side"] == "side_a")
        self.assertEqual(winner["entity_id"], "entity_france")
        self.assertEqual(winner["outcome"]["battlefield_control"], 0.79)
        self.assertEqual(winner["stakes"], 0.50)
        self.assertEqual(winner["national_scale"], 0.32)
        self.assertEqual(winner["evidence_confidence"], 0.70)


class IdentityTests(unittest.TestCase):
    def test_coalition_labels_stay_staged(self) -> None:
        self.assertIn("allies", IWBD_COALITION_SIDE_LABELS)
        candidates = [
            _battle(
                "iwbd-139-53-720",
                "Falaise",
                "World War II (Europe)",
                "1944-08-12",
                "1944-08-21",
                "Allies",
                "Germany",
                "Allies",
                "Attacker",
            ),
        ]
        result = _promote(candidates)
        self.assertEqual(result["rejections"]["coalition_or_composite_side"], 1)
        self.assertEqual(result["events"], [])

    def test_composite_slash_and_comma_labels_stay_staged(self) -> None:
        rows = [
            _battle(
                "iwbd-217--9-1680",
                "Cenepa 0",
                "Cenepa Valley",
                "1995-01-26",
                "1995-01-27",
                "Argentina/Brazil",
                "Peru",
                "Argentina/Brazil",
                "Attacker",
            ),
            _battle(
                "iwbd-40-14-500",
                "Gaeta",
                "Neapolitan",
                "1860-11-05",
                "1861-02-13",
                "France, Two Sicilies",
                "Sardinia",
                "Sardinia",
                "Defender",
            ),
        ]
        result = _promote(rows)
        self.assertEqual(result["rejections"]["coalition_or_composite_side"], 2)
        self.assertEqual(result["events"], [])

    @staticmethod
    def _reviewed_abtao():
        row = _battle(
            "iwbd-52-18-185",
            "Abtao",
            "Naval War",
            "1866-02-07",
            "1866-02-07",
            "Spain",
            "Chile/Peru",
            "Inconclusive",
            "Inconclusive",
            war_level_role="Inconclusive",
        )
        row["duration_days"] = "1"
        return row

    @staticmethod
    def _abtao_resolver(label, low_year, high_year):
        entity_ids = {
            "Spain": "spanish_empire",
            "Chile": "clio_ch_chile_rep_1_1812_3b31ba25",
            "Peru": "clio_q419_1822_a6e12c5b",
        }
        entity_id = entity_ids.get(label)
        return entity_id, ({"id": entity_id} if entity_id else None)

    def test_reviewed_abtao_composition_is_exact_and_weighted(self) -> None:
        result = _promote([self._reviewed_abtao()], resolve_label=self._abtao_resolver)
        self.assertEqual(result["rejections"]["coalition_or_composite_side"], 0)
        self.assertEqual(len(result["events"]), 1)
        participants = {
            participant["entity_id"]: participant
            for participant in result["events"][0]["participants"]
        }
        self.assertEqual(
            set(participants),
            {
                "spanish_empire",
                "clio_ch_chile_rep_1_1812_3b31ba25",
                "clio_q419_1822_a6e12c5b",
            },
        )
        self.assertEqual(participants["spanish_empire"]["contribution"], 1.0)
        self.assertEqual(
            participants["clio_ch_chile_rep_1_1812_3b31ba25"]["contribution"],
            0.5,
        )
        self.assertEqual(participants["clio_q419_1822_a6e12c5b"]["contribution"], 0.5)
        self.assertEqual(
            {participant["result_class"] for participant in participants.values()},
            {"stalemate_or_inconclusive"},
        )

    def test_reviewed_abtao_fails_on_source_fingerprint_drift(self) -> None:
        row = self._reviewed_abtao()
        row["defender_raw"] = "Chile / Peru"
        with self.assertRaisesRegex(ValueError, "source fingerprint changed"):
            _promote([row], resolve_label=self._abtao_resolver)

    def test_reviewed_abtao_fails_on_resolver_drift(self) -> None:
        def stale_resolver(label, low_year, high_year):
            entity_id, polity = self._abtao_resolver(label, low_year, high_year)
            if label == "Peru":
                return "generic_peru", polity
            return entity_id, polity

        with self.assertRaisesRegex(ValueError, "resolver returned 'generic_peru'"):
            _promote([self._reviewed_abtao()], resolve_label=stale_resolver)

    def test_parenthesized_faction_labels_stay_staged(self) -> None:
        candidates = [
            _battle(
                "iwbd-60-21-270",
                "Pasaquina",
                "Central American",
                "1876-04-15",
                "1876-04-16",
                "El Salvador (Medina)",
                "Guatemala",
                "El Salvador (Medina)",
                "Attacker",
            ),
        ]
        result = _promote(candidates)
        self.assertEqual(result["rejections"]["coalition_or_composite_side"], 1)
        self.assertEqual(result["events"], [])

    def test_unresolved_label_quarantines_the_battle(self) -> None:
        def resolver(label, low_year, high_year):
            if label == "Mexico":
                return None, None
            return _resolve_all(label, low_year, high_year)

        candidates = [
            _battle(
                "iwbd-43-15-520",
                "Puebla",
                "Franco-Mexican",
                "1862-05-05",
                "1862-05-05",
                "France",
                "Mexico",
                "Mexico",
                "Defender",
            ),
        ]
        result = _promote(candidates, resolve_label=resolver)
        self.assertEqual(result["rejections"]["unresolved_time_bounded_belligerent"], 1)
        self.assertEqual(result["events"], [])

    def test_deny_window_beats_the_resolver(self) -> None:
        self.assertEqual(IDENTITY_DENY_WINDOWS["turkey"], ((1919, 1923),))

        def resolver(label, low_year, high_year):
            # This stub WOULD resolve "Turkey" in 1921 (to the identity the
            # deny window exists to protect); the window is checked first.
            return _resolve_all(label, low_year, high_year)

        inside = [
            _battle(
                "iwbd-108-43-630",
                "Sakarya",
                "Second Greco-Turkish",
                "1921-08-23",
                "1921-09-13",
                "Greece",
                "Turkey",
                "Turkey",
                "Defender",
            ),
        ]
        result = _promote(inside, resolve_label=resolver)
        self.assertEqual(result["rejections"]["unresolved_time_bounded_belligerent"], 1)
        self.assertEqual(result["events"], [])

        opening_year = [
            _battle(
                "iwbd-115-43-809",
                "Aydin",
                "Greco-Turkish",
                "1919-06-27",
                "1919-07-04",
                "Greece",
                "Turkey",
                "Turkey",
                "Defender",
            ),
        ]
        result = _promote(opening_year, resolve_label=resolver)
        self.assertEqual(result["rejections"]["unresolved_time_bounded_belligerent"], 1)

        outside = [
            _battle(
                "iwbd-158--9-1500",
                "Post-window Clash",
                "Turco-Cypriot",
                "1924-06-01",
                "1924-06-02",
                "Greece",
                "Turkey",
                "Turkey",
                "Defender",
            ),
        ]
        result = _promote(outside, resolve_label=resolver)
        self.assertEqual(result["rejections"]["unresolved_time_bounded_belligerent"], 0)
        self.assertEqual(len(result["events"]), 1)

    def test_same_entity_on_both_sides_is_rejected(self) -> None:
        def resolver(label, low_year, high_year):
            return "entity_iran", None

        candidates = [
            _battle(
                "iwbd-106-77-910",
                "Khorramshahr 1",
                "Iran-Iraq",
                "1980-10-11",
                "1980-10-24",
                "Iran",
                "Iran ",
                "Iran",
                "Attacker",
            ),
        ]
        result = _promote(candidates, resolve_label=resolver)
        self.assertEqual(result["rejections"]["same_or_empty_opposing_side"], 1)
        self.assertEqual(result["events"], [])

    def test_resolver_is_called_with_full_event_span(self) -> None:
        calls = []

        def resolver(label, low_year, high_year):
            calls.append((label, low_year, high_year))
            return _resolve_all(label, low_year, high_year)

        candidates = [
            _battle(
                "iwbd-40-14-530",
                "Winter Lines",
                "Some War",
                "1919-08-01",
                "1920-02-10",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
        ]
        result = _promote(candidates, resolve_label=resolver)
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(len(calls), 2)
        for label, low_year, high_year in calls:
            self.assertEqual((low_year, high_year), (1919, 1920))

    def test_resolved_polities_are_returned_for_new_entities(self) -> None:
        ecuador = {
            "canonical_name_candidate": "Republic of Ecuador",
            "start_year": 1830,
        }

        def resolver(label, low_year, high_year):
            if label == "Ecuador":
                return "clio_q736_1834_da03bcc7", ecuador
            return _resolve_all(label, low_year, high_year)

        candidates = [
            _battle(
                "iwbd-217--9-1683",
                "Tiwintza 1",
                "Cenepa Valley",
                "1995-01-26",
                "1995-02-01",
                "Ecuador",
                "Peru",
                "Ecuador",
                "Attacker",
            ),
        ]
        result = _promote(candidates, resolve_label=resolver)
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(
            result["resolved_polities"], {"clio_q736_1834_da03bcc7": ecuador}
        )


class ClusterTests(unittest.TestCase):
    def test_cluster_joins_hced_war_cluster_when_war_tokens_match(self) -> None:
        spans = {"hced_war_korean_war": [_war_tokens("Korean War"), 1950, 1953]}
        candidates = [
            _battle(
                "iwbd-151-56-1000",
                "Chosin",
                "Korean",
                "1950-11-27",
                "1950-12-13",
                "China",
                "United States",
                "China",
                "Attacker",
            ),
        ]
        result = _promote(candidates, hced_war_cluster_spans=spans)
        self.assertEqual(result["events"][0]["cluster_id"], "hced_war_korean_war")

    def test_theater_suffix_is_stripped_before_matching(self) -> None:
        spans = {
            "hced_war_second_world_war": [_war_tokens("Second World War"), 1939, 1945]
        }
        candidates = [
            _battle(
                "iwbd-139-53-730",
                "Kohima",
                "World War II (Pacific)",
                "1944-04-04",
                "1944-06-22",
                "Japan",
                "United Kingdom",
                "United Kingdom",
                "Defender",
            ),
        ]
        result = _promote(candidates, hced_war_cluster_spans=spans)
        self.assertEqual(result["events"][0]["cluster_id"], "hced_war_second_world_war")

    def test_ambiguous_hced_cluster_match_falls_through(self) -> None:
        # Real-data analogue: "Second Russo-Turkish" token-matches both
        # hced_war_russo_turkish_war and hced_war_russo_turkish_wars; the
        # cluster falls through to the IWD family instead of guessing.
        spans = {
            "hced_war_russo_turkish_war": [
                _war_tokens("Russo-Turkish War"),
                1877,
                1878,
            ],
            "hced_war_russo_turkish_wars": [
                _war_tokens("Russo-Turkish Wars"),
                1806,
                1878,
            ],
        }
        candidates = [
            _battle(
                "iwbd-61-22-310",
                "Kars",
                "Second Russo-Turkish",
                "1877-11-17",
                "1877-11-18",
                "Russia",
                "Ottoman Empire",
                "Russia",
                "Attacker",
            ),
        ]
        result = _promote(
            candidates, hced_war_cluster_spans=spans, iwd_parent_ids={"22"}
        )
        self.assertEqual(result["events"][0]["cluster_id"], "iwd_parent_22")

    def test_iwd_parent_family_slugs_the_iwdnum_itself(self) -> None:
        # iwdNum is the IWD parent war id (largerwarid numbering), never an
        # IWD component id: an Iran-Iraq battle with iwdNum 77 must land in
        # iwd_parent_77, not in iwd_parent_38 (World War I) as the wrong
        # component-id join would put it. Membership alone cannot distinguish
        # the two joins; the emitted id can.
        candidates = [
            _battle(
                "iwbd-106-77-915",
                "Abadan",
                "Iran-Iraq",
                "1980-11-10",
                "1980-11-24",
                "Iraq",
                "Iran",
                "Iraq",
                "Attacker",
            ),
        ]
        result = _promote(candidates, iwd_parent_ids={"38", "77"})
        self.assertEqual(result["events"][0]["cluster_id"], "iwd_parent_77")

    def test_all_battles_of_one_war_share_one_cluster(self) -> None:
        # Cluster assignment is per war, never per row: a battle dated outside
        # the HCED cluster's observed span still joins its war-mates' cluster,
        # because splitting one war across clusters inflates n^-0.5 weight.
        spans = {"hced_war_korean_war": [_war_tokens("Korean War"), 1950, 1953]}
        candidates = [
            _battle(
                "iwbd-151-56-1001",
                "Inchon",
                "Korean",
                "1950-09-15",
                "1950-09-19",
                "United States",
                "North Korea",
                "United States",
                "Attacker",
            ),
            _battle(
                "iwbd-151-56-1002",
                "Late Outpost",
                "Korean",
                "1954-01-10",
                "1954-01-11",
                "North Korea",
                "United States",
                "United States",
                "Defender",
            ),
        ]
        result = _promote(candidates, hced_war_cluster_spans=spans)
        cluster_ids = {event["cluster_id"] for event in result["events"]}
        self.assertEqual(cluster_ids, {"hced_war_korean_war"})
        self.assertEqual(len(result["events"]), 2)

    def test_cow_minus_nine_wars_get_distinct_clusters(self) -> None:
        candidates = [
            _battle(
                "iwbd-217--9-1683",
                "Tiwintza 1",
                "Cenepa Valley",
                "1995-01-26",
                "1995-02-01",
                "Ecuador",
                "Peru",
                "Ecuador",
                "Attacker",
            ),
            _battle(
                "iwbd-158--9-1490",
                "Edchera",
                "Ifni",
                "1958-01-13",
                "1958-01-13",
                "Morocco",
                "Spain",
                "Morocco",
                "Attacker",
            ),
        ]
        result = _promote(candidates)
        clusters = {event["name"]: event["cluster_id"] for event in result["events"]}
        self.assertEqual(clusters["Tiwintza 1"], "iwbd_war_217_cenepa_valley")
        self.assertEqual(clusters["Edchera"], "iwbd_war_158_ifni")


class MalformedIdTests(unittest.TestCase):
    def test_malformed_candidate_id_is_rejected_under_its_own_counter(self) -> None:
        result = _promote(
            [
                _battle(
                    "iwbd_bad_format-1",
                    "Malformed",
                    "Franco-Spanish",
                    "1823-08-31",
                    "1823-08-31",
                    "France",
                    "Spain",
                    "France",
                    "Attacker",
                )
            ]
        )
        self.assertEqual(result["battles_promoted"], 0)
        self.assertEqual(result["rejections"]["malformed_candidate_id"], 1)

    def test_malformed_rows_are_excluded_from_containment_comparisons(self) -> None:
        # A malformed-id row has no war-group key, so it cannot stage an
        # umbrella; this pins the declared behavior that the containment
        # comparison set requires a parseable candidate id.
        result = _promote(
            [
                _battle(
                    "iwbd-61-22-281",
                    "Plevna",
                    "Second Russo-Turkish",
                    "1877-07-20",
                    "1877-12-10",
                    "Russia",
                    "Ottoman Empire",
                    "Russia",
                    "Attacker",
                ),
                _battle(
                    "not-an-iwbd-99",
                    "Plevna 2",
                    "Second Russo-Turkish",
                    "1877-07-30",
                    "1877-07-31",
                    "Russia",
                    "Ottoman Empire",
                    "Ottoman Empire",
                    "Defender",
                ),
            ]
        )
        self.assertEqual(result["rejections"]["malformed_candidate_id"], 1)
        # The umbrella is promoted because its only sibling was malformed.
        self.assertEqual(result["battles_promoted"], 1)
        self.assertEqual(result["events"][0]["name"], "Plevna")


class AccountingTests(unittest.TestCase):
    def test_every_row_is_counted_exactly_once(self) -> None:
        def resolver(label, low_year, high_year):
            if label == "Unmappable":
                return None, None
            return _resolve_all(label, low_year, high_year)

        candidates = [
            # accepted
            _battle(
                "iwbd-1-1-2",
                "Trocadero",
                "Franco-Spanish",
                "1823-08-31",
                "1823-08-31",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
            # missing battle name
            _battle(
                "iwbd-1-1-10",
                "",
                "Franco-Spanish",
                "1823-04-10",
                "1823-04-11",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
            # invalid date (end before start)
            _battle(
                "iwbd-1-1-11",
                "Backwards",
                "Franco-Spanish",
                "1823-05-02",
                "1823-05-01",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
            # missing belligerent label
            _battle(
                "iwbd-124-47-865",
                "Nameless Sides",
                "Chaco",
                "1932-09-07",
                "1932-09-29",
                "",
                "Bolivia",
                "Bolivia",
                "Defender",
            ),
            # curated seed duplicate
            _battle(
                "iwbd-139-53-700",
                "Midway",
                "World War II (Pacific)",
                "1942-06-04",
                "1942-06-07",
                "United States",
                "Japan",
                "United States",
                "Defender",
            ),
            # HCED duplicate
            _battle(
                "iwbd-1-1-3",
                "Cadiz",
                "Franco-Spanish",
                "1823-08-31",
                "1823-09-23",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
            # within-IWBD duplicate of the accepted first row
            _battle(
                "iwbd--9--9-900",
                "Trocadero",
                "Franco-Spanish",
                "1823-08-31",
                "1823-08-31",
                "France",
                "Spain",
                "France",
                "Attacker",
            ),
            # campaign umbrella over the constituent below
            _battle(
                "iwbd-61-22-281",
                "Plevna",
                "Second Russo-Turkish",
                "1877-07-20",
                "1877-12-10",
                "Russia",
                "Ottoman Empire",
                "Russia",
                "Attacker",
            ),
            # accepted constituent
            _battle(
                "iwbd-61-22-279",
                "Plevna 2",
                "Second Russo-Turkish",
                "1877-07-30",
                "1877-07-31",
                "Russia",
                "Ottoman Empire",
                "Ottoman Empire",
                "Defender",
            ),
            # winner not aligned to a named side
            _battle(
                "iwbd-1-1-5",
                "Irun",
                "Franco-Spanish",
                "1823-04-10",
                "1823-04-11",
                "France",
                "Spain",
                "Sweden",
                "Attacker",
            ),
            # coalition side
            _battle(
                "iwbd-139-53-720",
                "Falaise",
                "World War II (Europe)",
                "1944-08-12",
                "1944-08-21",
                "Allies",
                "Germany",
                "Allies",
                "Attacker",
            ),
            # unresolved identity
            _battle(
                "iwbd-43-15-520",
                "Puebla",
                "Franco-Mexican",
                "1862-05-05",
                "1862-05-05",
                "France",
                "Unmappable",
                "Unmappable",
                "Defender",
            ),
            # deny window
            _battle(
                "iwbd-108-43-630",
                "Sakarya",
                "Second Greco-Turkish",
                "1921-08-23",
                "1921-09-13",
                "Greece",
                "Turkey",
                "Turkey",
                "Defender",
            ),
            # same entity on both sides
            _battle(
                "iwbd-106-77-910",
                "Khorramshahr 1",
                "Iran-Iraq",
                "1980-10-11",
                "1980-10-24",
                "Iran",
                "Iran",
                "Iran",
                "Attacker",
            ),
        ]
        result = _promote(
            candidates,
            curated_seed_keys={_event_key("Midway", 1942)},
            hced_event_keys={_event_key("Cadiz", 1823)},
            resolve_label=resolver,
        )
        self.assertEqual(result["battles_total"], len(candidates))
        self.assertEqual(result["battles_promoted"], len(result["events"]))
        self.assertEqual(
            sum(result["rejections"].values()) + result["battles_promoted"],
            result["battles_total"],
        )
        self.assertEqual(result["battles_promoted"], 2)
        self.assertEqual(
            {event["name"] for event in result["events"]}, {"Trocadero", "Plevna 2"}
        )


@unittest.skipUnless(
    RELEASE_EVENTS.exists()
    and RELEASE_METADATA.exists()
    and REGISTRY.exists()
    and IWBD_CANDIDATES.exists()
    and IWD_CANDIDATES.exists(),
    "release, registry, and staged review artifacts not all built",
)
class ReleaseArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads(RELEASE_EVENTS.read_text(encoding="utf-8"))
        cls.metadata = json.loads(RELEASE_METADATA.read_text(encoding="utf-8"))
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.iwbd_events = [e for e in cls.events if str(e["id"]).startswith("iwbd_")]
        cls.hced_events = [e for e in cls.events if str(e["id"]).startswith("hced_")]
        cls.iwbd_candidates = {}
        with IWBD_CANDIDATES.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    cls.iwbd_candidates[str(row["candidate_id"])] = row
        cls.iwd_parents = {}
        with IWD_CANDIDATES.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    cls.iwd_parents.setdefault(str(row["parent_war_id"]), []).append(
                        row
                    )

    @staticmethod
    def _base_war(war_name):
        return re.sub(r"\s*\(.*\)$", "", str(war_name or ""))

    @unittest.skipUnless(
        (PROJECT_ROOT / "data" / "review" / "hced-candidates.jsonl").exists(),
        "staged HCED review queue not present",
    )
    def test_no_iwbd_event_matches_any_staged_hced_candidate(self) -> None:
        # Exercises the REAL dedup universe the build uses: full-year-range
        # keys over all staged HCED candidates (promoted or rejected), not
        # just the promoted events — a wide-span candidate's interior years
        # must also block.
        hced_keys = {}
        effective_hced_exclusions = {
            str(row["candidate_id"])
            for field_name in (
                "hced_curated_exclusions",
                "hced_label_curated_exclusions",
            )
            for row in self.metadata["promotion"][field_name]
        }

        def entry(key):
            return hced_keys.setdefault(key, {"exact": False, "outcomes": set()})

        review_path = PROJECT_ROOT / "data" / "review" / "hced-candidates.jsonl"
        with review_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                if str(row.get("candidate_id")) in effective_hced_exclusions:
                    continue
                name = str(row.get("name") or "")
                if not name:
                    continue
                year_low, year_high = row.get("year_low"), row.get("year_high")
                if year_low is None or year_high is None:
                    for year in {
                        row.get("year_low"),
                        row.get("year_best"),
                        row.get("year_high"),
                    }:
                        if year is not None:
                            entry(_event_key(name, int(year)))["exact"] = True
                    continue
                for year in range(int(year_low), int(year_high) + 1):
                    entry(_event_key(name, year))["exact"] = True

        def oriented_signature(event):
            winners = frozenset(
                p["entity_id"]
                for p in event["participants"]
                if "victory" in p.get("termination", "")
            )
            losers = frozenset(
                p["entity_id"]
                for p in event["participants"]
                if "defeat" in p.get("termination", "")
            )
            if winners or losers:
                return winners, losers
            return frozenset(p["entity_id"] for p in event["participants"]), frozenset()

        for event in self.hced_events:
            for year in range(int(event["year"]), int(event["end_year"]) + 1):
                for key in _cross_source_event_keys(event["name"], year):
                    entry(key)["outcomes"].add(oriented_signature(event))
        self.assertTrue(hced_keys)
        for event in self.iwbd_events:
            exact_lookup = {
                _event_key(str(event["name"]), year)
                for year in range(int(event["year"]) - 1, int(event["end_year"]) + 2)
            }
            fuzzy_lookup = {
                key
                for year in range(int(event["year"]), int(event["end_year"]) + 1)
                for key in _cross_source_event_keys(
                    str(event["name"]), year, lookup=True
                )
            }
            self.assertFalse(
                any(hced_keys.get(key, {}).get("exact") for key in exact_lookup)
                or any(
                    oriented_signature(event)
                    in hced_keys.get(key, {}).get("outcomes", set())
                    for key in fuzzy_lookup
                ),
                f"promoted IWBD event {event['id']} matches a staged HCED candidate",
            )

    def test_no_battle_appears_in_both_hced_and_iwbd_streams(self) -> None:
        self.assertTrue(self.iwbd_events)
        self.assertTrue(self.hced_events)

        def signature(event):
            return frozenset(
                (participant["entity_id"], participant["termination"])
                for participant in event["participants"]
            )

        hced_exact_index = set()
        hced_fuzzy_index = {}
        for event in self.hced_events:
            for year in range(
                int(event["year"]), int(event.get("end_year", event["year"])) + 1
            ):
                hced_exact_index.add(_event_key(str(event["name"]), year))
                for key in _cross_source_event_keys(str(event["name"]), year):
                    hced_fuzzy_index.setdefault(key, set()).add(signature(event))
        for event in self.iwbd_events:
            exact_lookup = {
                _event_key(str(event["name"]), year)
                for year in range(
                    int(event["year"]) - 1,
                    int(event.get("end_year", event["year"])) + 2,
                )
            }
            fuzzy_lookup = {
                key
                for year in range(
                    int(event["year"]),
                    int(event.get("end_year", event["year"])) + 1,
                )
                for key in _cross_source_event_keys(
                    str(event["name"]), year, lookup=True
                )
            }
            self.assertFalse(
                bool(exact_lookup & hced_exact_index)
                or any(
                    signature(event) in hced_fuzzy_index.get(key, set())
                    for key in fuzzy_lookup
                ),
                event["id"],
            )

    def test_badme_2a_survives_cross_year_fuzzy_match(self) -> None:
        promoted = {
            str(event.get("iwbd_candidate_id")): event for event in self.iwbd_events
        }
        self.assertIn("iwbd-219-84-1692", promoted)
        event = promoted["iwbd-219-84-1692"]
        self.assertEqual((event["year"], event["end_year"]), (1999, 1999))

    def test_compound_suffix_hced_duplicates_stay_staged(self) -> None:
        promoted = {str(event.get("iwbd_candidate_id")) for event in self.iwbd_events}
        self.assertTrue(
            {
                "iwbd-61-22-282",  # Plevna 1(a)
                "iwbd-61-22-283",  # Plevna 1(b)
                "iwbd-199-77-1626",  # Mehran 2(b)
                "iwbd-199-77-1628",  # Basra 4(b)
                "iwbd-219-84-1693",  # Badme 2(b)
            }.isdisjoint(promoted)
        )

    def test_verification_refuted_assertions_remain_in_the_ledger(self) -> None:
        retained_ids = {
            "hced_label_hced_newbury1643_1",
            "hced_label_hced_gainsborough1643_1",
            "hced_label_hced_bizani1913_1",
            "hced_label_hced_jannina1912_1",
            "hced_hced_isonzo_1st_1916_1",
            "hced_hced_isonzo_2nd_1916_1",
            "iwbd_iwbd_117_9_828_nieman_river",
        }
        event_ids = {str(event["id"]) for event in self.events}
        self.assertLessEqual(retained_ids, event_ids)

    def test_curated_iwbd_candidates_never_enter_the_ledger(self) -> None:
        promoted = {str(event.get("iwbd_candidate_id")) for event in self.iwbd_events}
        self.assertEqual(promoted & set(IWBD_CURATED_EXCLUSIONS), set())

    def test_no_iwbd_event_contains_a_sibling_iwbd_event(self) -> None:
        groups = {}
        for event in self.iwbd_events:
            candidate = self.iwbd_candidates[event["iwbd_candidate_id"]]
            start = date.fromisoformat(candidate["start_date"])
            end = date.fromisoformat(candidate["end_date"])
            key = (event["iwbd_cow_war_number"], event["iwbd_war_name"])
            groups.setdefault(key, []).append(
                (event["iwbd_candidate_id"], event["name"], start, end)
            )
        for key, rows in groups.items():
            for candidate_id, name, start, end in rows:
                for other_id, other_name, other_start, other_end in rows:
                    if normalize_label(other_name) == normalize_label(name):
                        continue
                    contains = (
                        start <= other_start
                        and end >= other_end
                        and (end - start).days > (other_end - other_start).days
                    )
                    if contains:
                        reviewed = set(
                            IWBD_REVIEWED_CONCURRENT_DISTINCT_RELATIONS.get(
                                candidate_id, {}
                            ).get("contained_candidates", {})
                        )
                        reviewed.update(
                            EFFECTIVE_IWBD_REVIEWED_IDENTITY_BINDINGS.get(
                                candidate_id, {}
                            ).get("contained_candidate_ids", ())
                        )
                        self.assertIn(
                            other_id,
                            reviewed,
                            f"{name} strictly contains unreviewed sibling "
                            f"{other_name} in {key}",
                        )

    def test_iwbd_war_groups_never_split_clusters(self) -> None:
        clusters_by_group = {}
        for event in self.iwbd_events:
            key = (
                event["iwbd_cow_war_number"],
                self._base_war(event["iwbd_war_name"]),
            )
            clusters_by_group.setdefault(key, set()).add(event["cluster_id"])
        for key, cluster_ids in clusters_by_group.items():
            self.assertEqual(
                len(cluster_ids), 1, f"war group {key} split across {cluster_ids}"
            )

    def test_iwd_parent_clusters_are_semantically_consistent(self) -> None:
        # tokens-OR-years: pure token matching fails legitimate naming
        # variants (Sino-Soviet1929 vs Manchurian, Falklands1982 vs Falkland
        # Islands); pure year overlap would miss nothing today but the
        # disjunction is what provably fails on the component-id join bug
        # (Iran-Iraq battles landing in the WWI cluster fail both prongs).
        checked = 0
        for event in self.iwbd_events:
            match = re.fullmatch(r"iwd_parent_(.+)", str(event["cluster_id"]))
            if not match:
                continue
            checked += 1
            parent_id = match.group(1)
            components = self.iwd_parents.get(parent_id)
            self.assertIsNotNone(
                components,
                f"{event['id']} clusters on unknown IWD parent {parent_id}",
            )
            parent_name = str(components[0].get("parent_war_name") or "")
            battle_tokens = _war_tokens(self._base_war(event["iwbd_war_name"]))
            tokens_ok = _war_tokens_match(_war_tokens(parent_name), battle_tokens)
            spans = [
                (int(row["start_year"]), int(row["end_year"]))
                for row in components
                if row.get("start_year") is not None and row.get("end_year") is not None
            ]
            years_ok = False
            if spans:
                parent_low = min(low for low, _ in spans)
                parent_high = max(high for _, high in spans)
                event_low = int(event["year"]) - 1
                event_high = int(event.get("end_year", event["year"])) + 1
                years_ok = parent_low <= event_high and parent_high >= event_low
            self.assertTrue(
                tokens_ok or years_ok,
                f"{event['id']} ({event['iwbd_war_name']}) joined IWD parent "
                f"{parent_id} ({parent_name}) with neither token nor year "
                "agreement",
            )
        self.assertGreater(checked, 0)

    def test_iwbd_events_carry_provenance(self) -> None:
        for event in self.iwbd_events:
            self.assertIn(event["iwbd_candidate_id"], self.iwbd_candidates)
            self.assertTrue(
                re.fullmatch(r"iwbd-(-?\d+)-(-?\d+)-(\d+)", event["iwbd_candidate_id"])
            )
            self.assertTrue(str(event["iwbd_war_name"]))
            self.assertTrue(str(event["iwbd_cow_war_number"]))
            self.assertIn("iwbd_iwd_war_number", event)
            self.assertIn("iwbd_battle_level_victor_role", event)
            self.assertIn("iwbd_duration_days", event)
            self.assertLessEqual(
                {"iwbd_dataset", "cliopatria_v020"}, set(event["source_ids"])
            )
            self.assertEqual(event["outcome_source_ids"], ["iwbd_dataset"])
            self.assertEqual(event["outcome_source_family_ids"], ["iwbd"])

    def test_iwbd_events_never_claim_major_severity(self) -> None:
        for event in self.iwbd_events:
            self.assertEqual(event["confidence"], 0.70)
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["scale"], "battle")
            self.assertIn(event["decisiveness"], (0.32, 0.66))
            for participant in event["participants"]:
                self.assertIn(participant["result_class"], LIMITED_RESULT_CLASSES)
                self.assertLessEqual(set(participant["outcome"]), TACTICAL_DIMENSIONS)

    def test_turkey_deny_window_allows_only_exact_tnm_contracts(self) -> None:
        # Bare Turkey is never resolved generically inside 1919-1923. The only
        # released exceptions are the complete, fingerprinted candidate
        # cohorts that bind that exact source assertion to the Turkish
        # National Movement rather than to the Ottoman Empire.
        expected_contract_ids = {
            candidate_id
            for cohort_name, candidate_ids in IWBD_REVIEWED_IDENTITY_COHORTS.items()
            if cohort_name.startswith("turkish_national_movement")
            for candidate_id in candidate_ids
        }
        observed_contract_ids = set()
        for event in self.iwbd_events:
            candidate = self.iwbd_candidates[event["iwbd_candidate_id"]]
            if (
                int(event.get("end_year", event["year"])) < 1919
                or int(event["year"]) > 1923
            ):
                continue
            turkey_roles = [
                role
                for role, field_name in (
                    ("attacker", "attacker_raw"),
                    ("defender", "defender_raw"),
                )
                if normalize_label(candidate.get(field_name)) == "turkey"
            ]
            if not turkey_roles:
                continue
            candidate_id = event["iwbd_candidate_id"]
            observed_contract_ids.add(candidate_id)
            self.assertIn(candidate_id, IWBD_REVIEWED_IDENTITY_BINDINGS)
            contract = IWBD_REVIEWED_IDENTITY_BINDINGS[candidate_id]
            for role in turkey_roles:
                self.assertIn(("Turkey", "turkish_national_movement"), contract[role])
            participant_ids = {
                participant["entity_id"] for participant in event["participants"]
            }
            self.assertIn("turkish_national_movement", participant_ids)
            self.assertNotIn("ottoman_empire", participant_ids)
        self.assertEqual(observed_contract_ids, expected_contract_ids)

    def test_japan_label_era_pins(self) -> None:
        # Unit-level pin of the declared era expectations: empire_japan's own
        # interval runs through 1947 (same continuous polity in its terminal
        # years, so no deny window), and 1950 stays unresolved.
        def resolver(label, low_year, high_year):
            if label == "Japan":
                if 1868 <= low_year and high_year <= 1947:
                    return "empire_japan", None
                return None, None
            return _resolve_all(label, low_year, high_year)

        in_interval = [
            _battle(
                "iwbd-999-99-1",
                "Terminal Era Clash",
                "Occupation Incident",
                "1946-03-01",
                "1947-02-01",
                "Japan",
                "Soviet Union",
                "Soviet Union",
                "Defender",
            ),
        ]
        result = _promote(in_interval, resolve_label=resolver)
        self.assertEqual(len(result["events"]), 1)
        entity_ids = {
            participant["entity_id"]
            for participant in result["events"][0]["participants"]
        }
        self.assertIn("empire_japan", entity_ids)

        post_interval = [
            _battle(
                "iwbd-999-99-2",
                "Postwar Clash",
                "Postwar Incident",
                "1950-03-01",
                "1950-03-02",
                "Japan",
                "Soviet Union",
                "Soviet Union",
                "Defender",
            ),
        ]
        result = _promote(post_interval, resolve_label=resolver)
        self.assertEqual(result["rejections"]["unresolved_time_bounded_belligerent"], 1)
        self.assertEqual(result["events"], [])

    def test_promotion_accounting_matches_events(self) -> None:
        promotion = self.metadata["promotion"]
        self.assertEqual(promotion["accepted_iwbd_battles"], len(self.iwbd_events))
        self.assertEqual(promotion["iwbd_battles_total"], 1708)
        self.assertEqual(
            sum(promotion["iwbd_rejections"].values())
            + promotion["accepted_iwbd_battles"],
            promotion["iwbd_battles_total"],
        )
        coverage = self.registry["coverage"]
        self.assertEqual(coverage["provisional_iwbd_battles"], len(self.iwbd_events))
        self.assertEqual(
            coverage["iwbd_battles_total"], promotion["iwbd_battles_total"]
        )


if __name__ == "__main__":
    unittest.main()
