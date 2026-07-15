from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from military_elo.promotion.common import _candidate_entity_id
from military_elo.war_constraints import (
    analyze_war_constraints,
    information_value_score,
    render_war_constraint_json,
    render_war_constraint_markdown,
    write_war_constraint_report,
)


def _polity(
    candidate_id: str,
    name: str,
    start: int,
    end: int,
    *,
    code: str | None = None,
    aliases: tuple[str, ...] = (),
    groups: tuple[tuple[int, int], ...] | None = None,
) -> dict:
    coverage = groups if groups is not None else ((start, end),)
    return {
        "candidate_id": candidate_id,
        "record_type": "POLITY",
        "canonical_name_candidate": name,
        "start_year": start,
        "end_year": end,
        "aliases": list(aliases),
        "wikipedia_titles": [],
        "seshat_ids": [code] if code else [],
        "wikidata_ids": [],
        "temporal_coverage_groups": [
            {"start_year": low, "end_year": high} for low, high in coverage
        ],
    }


def _row(
    candidate_id: str,
    year: int,
    side_1: str,
    side_2: str,
    *,
    codes_1: tuple[str, ...] = (),
    codes_2: tuple[str, ...] = (),
    war: str = "Binary War",
    event_type: str = "engagement",
    country: str = "Testland",
    latitude: str = "10.0",
    longitude: str = "20.0",
) -> dict:
    return {
        "candidate_id": candidate_id,
        "source_record_id": candidate_id.removeprefix("hced-"),
        "source_row": int(candidate_id.rsplit("-", 1)[-1]),
        "source_snapshot": "data/raw/hced/fixture.csv",
        "name": candidate_id,
        "year_low": year,
        "year_best": year,
        "year_high": year,
        "side_1_raw": side_1,
        "side_2_raw": side_2,
        "winner_raw": side_1,
        "loser_raw": side_2,
        "seshat_side_1_candidates": list(codes_1),
        "seshat_side_2_candidates": list(codes_2),
        "war_names": [war],
        "proposed_event_type": event_type,
        "modern_location_country": country,
        "latitude": latitude,
        "longitude": longitude,
        "duplicate_source_id": False,
    }


class WarConstraintFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.alpha = _polity(
            "cliopatria-alpha", "Alpha State", 1800, 1900, code="test_alpha"
        )
        self.beta = _polity(
            "cliopatria-beta", "Beta State", 1800, 1900, code="test_beta"
        )
        self.old_gamma = _polity(
            "cliopatria-old-gamma",
            "Old Gamma State",
            1700,
            1750,
            aliases=("Old Gamma",),
        )
        self.ambiguous_1 = _polity(
            "cliopatria-ambiguous-1",
            "Ambiguous North",
            1800,
            1900,
            aliases=("Ambiguous",),
        )
        self.ambiguous_2 = _polity(
            "cliopatria-ambiguous-2",
            "Ambiguous South",
            1800,
            1900,
            aliases=("Ambiguous",),
        )
        self.polities = [
            self.alpha,
            self.beta,
            self.old_gamma,
            self.ambiguous_1,
            self.ambiguous_2,
        ]
        self.rows = [
            _row(
                "hced-root-1",
                1850,
                "Masked Alpha",
                "Beta Army",
                codes_1=("test_alpha",),
                codes_2=("test_beta",),
                war="Binary-War",
            ),
            _row(
                "hced-root-2",
                1851,
                "Masked Alpha",
                "Beta Army",
                codes_1=("test_alpha",),
                codes_2=("test_beta",),
                war="Binary War",
            ),
            # Current observation coherence rejects Masked Alpha because it is
            # not an own label of Alpha State. Same-label war evidence can
            # still surface it as a review-only suggestion.
            _row(
                "hced-direct-3",
                1852,
                "Masked Alpha",
                "Beta Army",
                codes_2=("test_beta",),
            ),
            # Strict binary complement, followed by two later fixed-point
            # rounds for the all-uncoded row below.
            _row(
                "hced-complement-4",
                1853,
                "New Alpha Term",
                "Beta Army",
                codes_2=("test_beta",),
            ),
            _row(
                "hced-fixed-point-5",
                1854,
                "New Alpha Term",
                "New Beta Term",
            ),
            _row(
                "hced-faction-6",
                1855,
                "Rebels",
                "Beta Army",
                codes_2=("test_beta",),
            ),
            _row(
                "hced-ambiguous-7",
                1856,
                "Ambiguous",
                "Beta Army",
                codes_2=("test_beta",),
            ),
            _row(
                "hced-wrong-interval-8",
                1857,
                "Old Gamma",
                "Beta Army",
                codes_2=("test_beta",),
                war="Wrong Interval War",
            ),
            _row(
                "hced-zero-9",
                1858,
                "No Such Identity",
                "Beta Army",
                codes_2=("test_beta",),
                war="Zero Candidate War",
            ),
        ]

    def _report(self) -> dict:
        return analyze_war_constraints(
            copy.deepcopy(self.rows),
            copy.deepcopy(self.polities),
            [],
            [],
            release_events=[],
            results={"entities": []},
            input_fingerprints={"fixture": {"sha256": "0" * 64}},
        )

    def test_fixed_point_is_rooted_conservative_and_read_only(self) -> None:
        before = json.dumps(self.rows, sort_keys=True)
        report = self._report()
        self.assertEqual(json.dumps(self.rows, sort_keys=True), before)
        self.assertTrue(report["read_only"])
        self.assertEqual(report["release_mutation"], "none")

        proposals = {row["side_key"]: row for row in report["proposals"]}
        alpha_id = _candidate_entity_id(self.alpha)
        beta_id = _candidate_entity_id(self.beta)
        self.assertEqual(
            proposals["hced-direct-3:side_1"]["entity_id"], alpha_id
        )
        self.assertEqual(
            proposals["hced-complement-4:side_1"]["entity_id"], alpha_id
        )
        self.assertEqual(
            proposals["hced-fixed-point-5:side_1"]["entity_id"], alpha_id
        )
        self.assertEqual(
            proposals["hced-fixed-point-5:side_2"]["entity_id"], beta_id
        )
        self.assertGreaterEqual(report["summary"]["fixed_point_rounds"], 3)
        self.assertEqual(
            report["summary"]["genuinely_unambiguous_rows_under_gate"], 3
        )
        self.assertNotIn("hced-faction-6:side_1", proposals)
        self.assertNotIn("hced-ambiguous-7:side_1", proposals)
        self.assertGreater(
            report["summary"]["proposal_gate_rejections"].get(
                "faction_label_not_a_polity", 0
            ),
            0,
        )
        self.assertGreater(
            report["summary"]["proposal_gate_rejections"].get(
                "conflicting_time_valid_label_candidate", 0
            ),
            0,
        )
        self.assertTrue(
            all(proposal["release_effect"] == "none" for proposal in report["proposals"])
        )

    def test_failure_cases_wars_locations_and_candidates_are_explicit(self) -> None:
        report = self._report()
        failures = report["summary"]["failure_cases"]
        self.assertGreater(failures["zero_label_candidates"], 0)
        self.assertGreater(failures["single_label_candidate_outside_interval"], 0)
        self.assertGreater(failures["multiple_time_valid_label_candidates"], 0)

        wars = {war["war_key"]: war for war in report["wars"]}
        binary = wars["binary war"]
        self.assertEqual(binary["locations"]["modern_location_countries"], ["Testland"])
        self.assertEqual(binary["locations"]["distinct_coordinate_points"], 1)
        self.assertEqual(binary["years"]["low"], 1852)
        self.assertGreater(binary["seshat_anchors"]["rows"], 0)
        self.assertGreater(binary["already_resolved_counterparts"]["rows"], 0)
        candidate_labels = {
            row["normalized_label"]: row["candidates"]
            for row in binary["candidate_entities_by_label"]
        }
        self.assertEqual(len(candidate_labels["ambiguous"]), 2)
        self.assertIn("failure_cases", binary)

    def test_report_bytes_and_hash_are_deterministic(self) -> None:
        first = self._report()
        second = self._report()
        self.assertEqual(render_war_constraint_json(first), render_war_constraint_json(second))
        self.assertEqual(
            first["determinism"]["canonical_body_sha256"],
            second["determinism"]["canonical_body_sha256"],
        )
        self.assertRegex(first["determinism"]["canonical_body_sha256"], r"^[0-9a-f]{64}$")

    def test_artifact_writer_emits_paired_json_and_markdown(self) -> None:
        report = self._report()
        with tempfile.TemporaryDirectory() as temporary:
            json_path, markdown_path = write_war_constraint_report(
                report, temporary, top=2
            )
            self.assertTrue(json_path.is_file())
            self.assertTrue(markdown_path.is_file())
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), report)
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("Read-only diagnostic", markdown)
            self.assertIn("Highest information-value wars", markdown)
            self.assertEqual(markdown, render_war_constraint_markdown(report, top=2))


class InformationValueTests(unittest.TestCase):
    def test_component_bridge_strategic_event_outranks_dense_tactical_repeat(self) -> None:
        components = {"a": 1, "b": 1, "c": 2}
        dense = information_value_score(
            "a",
            "b",
            event_type="engagement",
            entity_event_counts={"a": 100, "b": 100, "c": 1},
            pair_event_counts={("a", "b"): 50},
            network_components=components,
        )
        bridge = information_value_score(
            "a",
            "c",
            event_type="war",
            entity_event_counts={"a": 100, "b": 100, "c": 1},
            pair_event_counts={},
            network_components=components,
        )
        self.assertGreater(bridge["score"], dense["score"])
        self.assertEqual(bridge["connectivity_case"], "bridges_existing_components")
        self.assertEqual(dense["connectivity_case"], "within_existing_component")


if __name__ == "__main__":
    unittest.main()
