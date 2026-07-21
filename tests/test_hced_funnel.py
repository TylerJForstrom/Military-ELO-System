from __future__ import annotations

import json
import unittest
from pathlib import Path

from military_elo.promotion.common import (
    _candidate_entity_id,
    _candidate_labels,
    _seed_entity_labels,
    normalize_label,
)
from military_elo.promotion.hced_funnel import (
    analyze_hced_unresolved_labels,
    build_hced_unresolved_funnel,
    classify_label_failure,
    recompute_hced_marginal_yield,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = PROJECT_ROOT / "data" / "review"


def _entity(entity_id: str, name: str, start: int, end: int | None, aliases=()):
    return {
        "id": entity_id,
        "name": name,
        "start_year": start,
        "end_year": end,
        "aliases": list(aliases),
    }


def _context(seeds=(), polities=()):
    seeds = list(seeds)
    polities = list(polities)
    seed_by_id = {entity["id"]: entity for entity in seeds}
    seed_label_index = {}
    for entity in seeds:
        for label in _seed_entity_labels(entity):
            seed_label_index.setdefault(label, set()).add(entity["id"])
    polity_alias_index = {}
    for polity in polities:
        for label in _candidate_labels(polity):
            polity_alias_index.setdefault(label, []).append(polity)
    release_entities = {entity["id"]: entity for entity in seeds}
    for polity in polities:
        release_entities[_candidate_entity_id(polity)] = {
            "id": _candidate_entity_id(polity),
            "name": polity["canonical_name_candidate"],
            "start_year": polity["start_year"],
            "end_year": polity["end_year"],
            "aliases": polity.get("aliases", []),
        }
    entity_labels = {
        entity["id"]: _seed_entity_labels(entity) for entity in seeds
    }
    for polity in polities:
        entity_labels[_candidate_entity_id(polity)] = _candidate_labels(polity)
    return {
        "seed_entities": seeds,
        "seed_by_id": seed_by_id,
        "seed_label_index": seed_label_index,
        "label_observations": {},
        "release_entities": release_entities,
        "entity_labels": entity_labels,
        "polity_alias_index": polity_alias_index,
    }


def _candidate(
    candidate_id: str,
    year: int,
    side_1: str,
    side_2: str,
    *,
    side_1_codes=(),
    side_2_codes=(),
):
    return {
        "candidate_id": candidate_id,
        "source_record_id": candidate_id.removeprefix("hced-"),
        "name": candidate_id,
        "year_low": year,
        "year_best": year,
        "year_high": year,
        "side_1_raw": side_1,
        "side_2_raw": side_2,
        "winner_raw": side_1,
        "loser_raw": side_2,
        "seshat_side_1_candidates": list(side_1_codes),
        "seshat_side_2_candidates": list(side_2_codes),
        "war_names": ["Fixture War"],
    }


class FailureClassificationTests(unittest.TestCase):
    def test_required_failure_cases_are_distinct(self) -> None:
        empty = _context()
        self.assertEqual(
            classify_label_failure("missing", 1900, 1900, empty)["failure_case"],
            "zero_time_valid_candidates",
        )

        old = _context([_entity("old", "Old State", 100, 200)])
        self.assertEqual(
            classify_label_failure("old state", 300, 300, old)["failure_case"],
            "one_wrong_interval_candidate",
        )

        ambiguous = _context(
            [
                _entity("one", "First", 100, 200, aliases=("Shared",)),
                _entity("two", "Second", 100, 200, aliases=("Shared",)),
            ]
        )
        self.assertEqual(
            classify_label_failure("shared", 150, 150, ambiguous)["failure_case"],
            "multiple_time_valid_candidates",
        )

        denied = _context([_entity("turkey", "Turkey", 1900, None)])
        self.assertEqual(
            classify_label_failure("turkey", 1920, 1920, denied)["failure_case"],
            "policy_denied_window",
        )


class FunnelFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [
            _candidate("hced-e1", 1901, "X", "Known A", side_2_codes=("a",)),
            _candidate("hced-e2", 1902, "X", "Known C", side_2_codes=("c",)),
            _candidate("hced-e3", 1903, "X", "Y"),
        ]
        self.ledger = [
            {
                "participants": [
                    {"entity_id": "entity_a"},
                    {"entity_id": "entity_b"},
                ]
            },
            {
                "participants": [
                    {"entity_id": "entity_c"},
                    {"entity_id": "entity_d"},
                ]
            },
        ]

    @staticmethod
    def _resolve_code(code, low_year, high_year):
        del low_year, high_year
        return {"a": "entity_a", "c": "entity_c"}.get(code), None, None

    @staticmethod
    def _resolve_label(candidate, label, low_year, high_year):
        del candidate, label, low_year, high_year
        return None, None, "no_unique_time_valid_label_match", None

    @staticmethod
    def _inspect(label, low_year, high_year):
        del label, low_year, high_year
        return {
            "failure_case": "zero_time_valid_candidates",
            "candidate_ids": [],
            "time_valid_candidate_ids": [],
        }

    def _report(self):
        return analyze_hced_unresolved_labels(
            self.rows,
            resolve_code=self._resolve_code,
            resolve_candidate_side_label=self._resolve_label,
            inspect_failure=self._inspect,
            ledger_events=self.ledger,
            batch_size=5,
        )

    def test_counts_components_and_centuries(self) -> None:
        report = self._report()
        labels = {row["label"]: row for row in report["labels"]}
        self.assertEqual(labels["x"]["events_touched"], 3)
        self.assertEqual(labels["x"]["sole_blocker_events"], 2)
        self.assertEqual(labels["x"]["components_touched"], 2)
        self.assertEqual(labels["x"]["components_bridged"], 1)
        self.assertEqual(labels["x"]["centuries"], {"CE_20": 3})
        self.assertEqual(labels["y"]["sole_blocker_events"], 0)

    def test_greedy_recomputes_after_each_selection(self) -> None:
        report = self._report()
        ranking = report["greedy_batch"]["ranking"]
        self.assertEqual(
            [(row["label"], row["marginal_events"]) for row in ranking],
            [("x", 2), ("y", 1)],
        )
        self.assertEqual(ranking[-1]["cumulative_events"], 3)

        recomputed = recompute_hced_marginal_yield(
            report["row_label_data"],
            self.ledger,
            batch_size=5,
            preselected_labels=("x",),
        )
        self.assertEqual(recomputed[0]["label"], "y")
        self.assertEqual(recomputed[0]["marginal_events"], 1)
        self.assertEqual(recomputed[0]["cumulative_events"], 3)

    def test_report_is_deterministic_and_exposes_rows(self) -> None:
        first = self._report()
        second = self._report()
        self.assertEqual(
            json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)
        )
        row = first["row_label_data"][0]
        self.assertEqual(row["candidate_id"], "hced-e1")
        self.assertEqual(row["blocker_labels"], ["x"])
        self.assertEqual(row["resolved_counterpart_entity_ids"], ["entity_a"])
        self.assertTrue(row["greedy_eligible"])


@unittest.skipUnless(
    (REVIEW_ROOT / "hced-candidates.jsonl").is_file()
    and (REVIEW_ROOT / "cliopatria-entity-candidates.jsonl").is_file(),
    "machine-local locked review queues are not present",
)
class CurrentCorpusFunnelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_hced_unresolved_funnel(
            PROJECT_ROOT / "data" / "seed",
            REVIEW_ROOT,
            PROJECT_ROOT / "data" / "release" / "events.json",
            batch_size=50,
        )

    def test_current_locked_corpus_invariants(self) -> None:
        summary = self.report["summary"]
        self.assertEqual(summary["deferred_label_rows"], 3002)
        self.assertEqual(summary["published_hced_candidate_rows_excluded"], 2493)
        self.assertEqual(summary["events_touched"], 2163)
        self.assertEqual(summary["unresolved_labels"], 2180)
        self.assertEqual(summary["sole_blocker_events"], 973)
        first = self.report["greedy_batch"]["ranking"][0]
        self.assertEqual(
            (first["label"], first["marginal_events"]),
            ("wurtemburg", 3),
        )
        self.assertFalse(
            {"algeria", "cheyenne", "libya"}
            & {str(row.get("label")) for row in self.report["labels"]}
        )
        published = {
            str(event["hced_candidate_id"])
            for event in json.loads(
                (PROJECT_ROOT / "data" / "release" / "events.json").read_text(
                    encoding="utf-8"
                )
            )
            if event.get("hced_candidate_id") is not None
        }
        reported = {row["candidate_id"] for row in self.report["row_label_data"]}
        self.assertFalse(published & reported)

    def test_csa_is_already_resolved_not_an_unresolved_headline(self) -> None:
        exact_labels = {row["label"] for row in self.report["labels"]}
        self.assertNotIn("confederate states of america", exact_labels)
        ledger = json.loads(
            (PROJECT_ROOT / "data" / "release" / "events.json").read_text(
                encoding="utf-8"
            )
        )
        csa_events = [
            event
            for event in ledger
            if any(
                participant["entity_id"] == "clio_q81931_1861_f3bc20bd"
                for participant in event["participants"]
            )
        ]
        self.assertEqual(len(csa_events), 365)


if __name__ == "__main__":
    unittest.main()
