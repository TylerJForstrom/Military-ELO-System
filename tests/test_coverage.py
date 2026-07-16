from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from typing import Any

from military_elo.coverage import (
    CoverageInputError,
    build_coverage_report,
    render_coverage_json,
    render_coverage_markdown,
    write_coverage_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows
        ),
        encoding="utf-8",
    )


def _outcome(layer: str, *, omit: str | None = None) -> dict[str, float]:
    dimensions = {
        "tactical": (
            "battlefield_control",
            "mission_objective",
            "force_preservation",
            "positional_gain",
        ),
        "operational": (
            "campaign_objective",
            "theater_control",
            "force_preservation",
            "tempo_initiative",
            "logistics_sustainment",
        ),
        "strategic": (
            "battlefield_outcome",
            "political_objectives",
            "territorial_outcome",
            "sovereignty_survival",
            "settlement_durability",
            "force_preservation",
        ),
    }[layer]
    return {dimension: 0.5 for dimension in dimensions if dimension != omit}


class CoverageFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.release = self.root / "release"
        self.review = self.root / "review"
        self.registry = self.root / "registry.json"
        self.results = self.root / "results.json"

        self.events = [
            {
                "id": "tactical_event",
                "name": "Synthetic tactical event",
                "year": -600,
                "end_year": -599,
                "event_type": "engagement",
                "war_type": "interstate_limited",
                "domain": "land",
                "date_precision": "year",
                "cluster_id": "cluster_one",
                "participants": [
                    {
                        "entity_id": "entity_a",
                        "side": "a",
                        "role": "primary",
                        "outcome": _outcome("tactical"),
                    },
                    {
                        "entity_id": "entity_b",
                        "side": "b",
                        "role": "primary",
                        "outcome": _outcome("tactical"),
                    },
                ],
                "source_ids": ["generic_source"],
            },
            {
                "id": "operational_event",
                "name": "Synthetic operational event",
                "year": 1800,
                "end_year": 1801,
                "event_type": "campaign",
                "war_type": "",
                "domain": "",
                "date_precision": None,
                "region": "Unclassified",
                "location": {"name": "Synthetic place", "latitude": 1, "longitude": 2},
                "cluster_id": "cluster_two",
                "parent_event_id": "tactical_event",
                "status": "complete",
                "participants": [
                    {
                        "entity_id": "entity_b",
                        "side": "a",
                        "objective": "Synthetic documented objective",
                        "outcome": _outcome("operational"),
                    },
                    {
                        "entity_id": "entity_c",
                        "side": "b",
                        "role": "supporting_ally",
                        "outcome": _outcome(
                            "operational", omit="logistics_sustainment"
                        ),
                    },
                ],
                "source_ids": ["generic_source", "family_source"],
            },
            {
                "id": "excluded_event",
                "name": "Excluded synthetic record",
                "year": 1900,
                "end_year": 1900,
                "event_type": "war",
                "status": "excluded",
                "participants": [
                    {
                        "entity_id": "entity_d",
                        "side": "a",
                        "role": "primary",
                        "outcome": _outcome("strategic"),
                    }
                ],
                "source_ids": ["generic_source"],
            },
        ]
        self.entities = [
            {
                "id": "entity_a",
                "name": "Entity A",
                "region": "Region A",
                "start_year": -1000,
            },
            {
                "id": "entity_b",
                "name": "Entity B",
                "region": "Unclassified",
                "start_year": -1000,
            },
            {
                "id": "entity_c",
                "name": "Entity C",
                "start_year": 1700,
            },
        ]
        self.sources = [
            {
                "id": "generic_source",
                "title": "Generic source",
                "url": "https://example.invalid/generic",
                "source_family_id": "must_not_count_without_outcome_role",
            },
            {
                "id": "family_source",
                "title": "Family source",
                "url": "https://example.invalid/family",
                "source_family_id": "family_b",
            },
        ]
        self.metadata = {
            "dataset_id": "synthetic-coverage-test",
            "version": "test",
            "as_of": "2026-07-13",
            "comprehensive": False,
            "promotion": {
                "source_queue_counts": {
                    "cliopatria-entity-candidates.jsonl": 1,
                    "hced-candidates.jsonl": 3,
                },
                "accepted_iwd_wars": 1,
                "iwd_components_aggregated": 2,
                "iwd_components_attached_to_rated_parents": 3,
                "hced_rejections": {
                    "missing_date": 1,
                    "unknown_identity": 0,
                },
                "iwbd_rejections": {"duplicate": 2},
            },
        }
        self.registry_document = {
            "entities": [
                {"id": "entity_a", "status": "rated", "identity_status": "curated"},
                {
                    "id": "entity_b",
                    "status": "provisional",
                    "identity_status": "source_candidate",
                },
                {
                    "id": "entity_c",
                    "status": "provisional",
                    "identity_status": "source_candidate",
                },
                {"id": "entity_d", "status": "unrated", "identity_status": "curated"},
            ],
            "coverage": {
                "registry_polities": 4,
                "rated_entities": 3,
                "rated_events": 2,
                "staged_source_records": 4,
                "unresolved_event_candidates": 2,
                "curated_seed_events": 1,
                "provisional_hced_events": 1,
                "provisional_hced_label_events": 0,
                "provisional_iwd_wars": 1,
                "provisional_iwbd_battles": 0,
                "provisional_ucdp_events": 0,
                "iwd_components_aggregated": 2,
                "source_queue_counts": {
                    "cliopatria-entity-candidates.jsonl": 1,
                    "hced-candidates.jsonl": 3,
                },
            },
        }
        self.results_document = {
            "entities": [
                {"id": "entity_a", "name": "Entity A", "network_component": 1},
                {"id": "entity_b", "name": "Entity B", "network_component": 1},
                {"id": "entity_c", "name": "Entity C", "network_component": 2},
            ]
        }
        self.review_rows = [
            {
                "candidate_id": f"candidate-{index}",
                "review_status": "needs_review",
                "do_not_rate_automatically": True,
            }
            for index in range(3)
        ]
        self._write_fixture()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_fixture(self) -> None:
        _write_json(self.release / "events.json", self.events)
        _write_json(self.release / "entities.json", self.entities)
        _write_json(self.release / "sources.json", self.sources)
        _write_json(self.release / "metadata.json", self.metadata)
        _write_json(self.registry, self.registry_document)
        _write_json(self.results, self.results_document)
        _write_jsonl(
            self.review / "cliopatria-entity-candidates.jsonl",
            [{"candidate_id": "identity-1", "review_status": "needs_review"}],
        )
        _write_jsonl(self.review / "hced-candidates.jsonl", self.review_rows)

    def _report(self, *, review: bool = True) -> dict[str, Any]:
        return build_coverage_report(
            self.release,
            review_dir=self.review if review else None,
            registry_path=self.registry,
            results_path=self.results,
        )

    def test_stage_scorecard_preserves_units_and_provisional_status(self) -> None:
        report = self._report()
        funnel = report["stage_funnel"]
        self.assertEqual(funnel["raw"]["availability"], "not_available")
        self.assertEqual(funnel["staged"]["count"], 4)
        self.assertEqual(funnel["event_like"]["count"], 3)
        self.assertEqual(funnel["unresolved"]["count"], 2)
        self.assertEqual(funnel["curated_seed"]["count"], 1)
        self.assertEqual(funnel["adjudicated"]["availability"], "not_available")
        self.assertIsNone(funnel["adjudicated"]["count"])
        self.assertIn("Curated seed membership", funnel["adjudicated"]["reason"])
        self.assertEqual(funnel["rated_provisional"]["count"], 2)
        self.assertEqual(funnel["rated"]["count"], 2)
        self.assertFalse(funnel["is_strictly_nested"])
        reconciliation = funnel["unit_reconciliation"]
        self.assertEqual(reconciliation["availability"], "available")
        self.assertEqual(reconciliation["iwd_components_aggregated"]["count"], 2)
        self.assertEqual(
            reconciliation["iwd_components_attached_to_rated_parents"]["count"], 3
        )
        self.assertEqual(reconciliation["iwd_parent_wars_rated"]["count"], 1)
        self.assertEqual(
            reconciliation["iwd_components_aggregated"]["source"],
            "registry.coverage.iwd_components_aggregated",
        )
        self.assertEqual(
            reconciliation["iwd_components_attached_to_rated_parents"]["source"],
            "release.metadata.promotion.iwd_components_attached_to_rated_parents",
        )
        for metric in (
            reconciliation["iwd_components_aggregated"],
            reconciliation["iwd_components_attached_to_rated_parents"],
            reconciliation["iwd_parent_wars_rated"],
        ):
            self.assertEqual(metric["availability"], "available")
            self.assertTrue(metric["unit"])
            self.assertTrue(metric["definition"])
        self.assertTrue(report["consistency_checks"]["review_queue_counts"]["matches"])
        self.assertTrue(report["scope"]["review_directory_supplied"])
        self.assertTrue(report["scope"]["review_files_supplied"])

    def test_registry_declared_empty_counts_override_metadata_and_physical_rows(
        self,
    ) -> None:
        self.registry_document["coverage"]["source_queue_counts"] = {}
        self.review_rows = [{"candidate_id": "physical-only"}]
        self._write_fixture()
        (self.review / "cliopatria-entity-candidates.jsonl").unlink()

        report = self._report()
        self.assertEqual(report["stage_funnel"]["staged"]["count"], 0)
        self.assertEqual(report["stage_funnel"]["event_like"]["count"], 0)
        self.assertEqual(
            report["stage_funnel"]["staged"]["source"],
            "registry.coverage.source_queue_counts",
        )
        self.assertEqual(
            report["stage_funnel"]["event_like"]["source"],
            "registry.coverage.source_queue_counts",
        )
        consistency = report["consistency_checks"]["review_queue_counts"]
        self.assertEqual(consistency["availability"], "available")
        self.assertFalse(consistency["matches"])
        self.assertEqual(
            consistency["mismatches"],
            {"hced-candidates.jsonl": {"declared": 0, "observed": 1}},
        )

    def test_metadata_declared_empty_counts_match_supplied_empty_review(self) -> None:
        self.registry_document["coverage"].pop("source_queue_counts")
        self.metadata["promotion"]["source_queue_counts"] = {}
        self._write_fixture()
        empty_review = self.root / "empty-review"
        empty_review.mkdir()

        report = build_coverage_report(
            self.release,
            review_dir=empty_review,
            registry_path=self.registry,
            results_path=self.results,
        )
        self.assertEqual(report["stage_funnel"]["staged"]["count"], 0)
        self.assertEqual(report["stage_funnel"]["event_like"]["count"], 0)
        consistency = report["consistency_checks"]["review_queue_counts"]
        self.assertEqual(consistency["availability"], "available")
        self.assertTrue(consistency["matches"])
        self.assertEqual(consistency["mismatches"], {})
        aging = report["unresolved_queue_aging"]
        self.assertEqual(aging["availability"], "not_applicable")
        self.assertEqual(aging["timestamp_coverage"]["numerator"], 0)
        self.assertEqual(aging["timestamp_coverage"]["denominator"], 0)
        self.assertEqual(aging["timestamp_coverage"]["availability"], "not_applicable")
        self.assertTrue(report["scope"]["review_directory_supplied"])
        self.assertFalse(report["scope"]["review_files_supplied"])
        markdown = render_coverage_markdown(report)
        self.assertIn(
            "Not applicable: The supplied review directory contains no event-like queue rows.",
            markdown,
        )
        self.assertNotIn("None days", markdown)
        self.assertNotIn("| Age bucket | Candidates |", markdown)
        self.assertIn("Queue-timestamp coverage", markdown)

    def test_declared_all_zero_counts_match_empty_review_corpora(self) -> None:
        self.registry_document["coverage"]["source_queue_counts"] = {
            "hced-candidates.jsonl": 0
        }
        self._write_fixture()
        for with_empty_file in (False, True):
            with self.subTest(with_empty_file=with_empty_file):
                review = self.root / f"zero-review-{int(with_empty_file)}"
                review.mkdir()
                if with_empty_file:
                    (review / "hced-candidates.jsonl").write_bytes(b"")
                report = build_coverage_report(
                    self.release,
                    review_dir=review,
                    registry_path=self.registry,
                    results_path=self.results,
                )
                self.assertEqual(report["stage_funnel"]["staged"]["count"], 0)
                self.assertEqual(report["stage_funnel"]["event_like"]["count"], 0)
                consistency = report["consistency_checks"]["review_queue_counts"]
                self.assertEqual(consistency["availability"], "available")
                self.assertTrue(consistency["matches"])
                self.assertEqual(consistency["mismatches"], {})
                aging = report["unresolved_queue_aging"]
                self.assertEqual(aging["availability"], "not_applicable")
                self.assertEqual(aging["timestamp_coverage"]["numerator"], 0)
                self.assertEqual(aging["timestamp_coverage"]["denominator"], 0)
                self.assertEqual(
                    report["scope"]["review_files_supplied"], with_empty_file
                )

    def test_identity_only_review_has_not_applicable_event_queue_aging(self) -> None:
        self.registry_document["coverage"]["source_queue_counts"] = {
            "cliopatria-entity-candidates.jsonl": 1
        }
        self._write_fixture()
        review = self.root / "identity-only-review"
        _write_jsonl(
            review / "cliopatria-entity-candidates.jsonl",
            [{"candidate_id": "identity-only", "review_status": "needs_review"}],
        )
        report = build_coverage_report(
            self.release,
            review_dir=review,
            registry_path=self.registry,
            results_path=self.results,
        )
        self.assertEqual(report["stage_funnel"]["staged"]["count"], 1)
        self.assertEqual(report["stage_funnel"]["event_like"]["count"], 0)
        self.assertTrue(report["consistency_checks"]["review_queue_counts"]["matches"])
        aging = report["unresolved_queue_aging"]
        self.assertEqual(aging["availability"], "not_applicable")
        self.assertEqual(aging["timestamp_coverage"]["numerator"], 0)
        self.assertEqual(aging["timestamp_coverage"]["denominator"], 0)
        self.assertIn("no event-like queue rows", aging["reason"])

    def test_absent_declarations_distinguish_empty_and_omitted_review(self) -> None:
        self.registry_document["coverage"].pop("source_queue_counts")
        self.metadata["promotion"].pop("source_queue_counts")
        self._write_fixture()
        empty_review = self.root / "empty-review"
        empty_review.mkdir()

        supplied = build_coverage_report(
            self.release,
            review_dir=empty_review,
            registry_path=self.registry,
            results_path=self.results,
        )
        self.assertEqual(supplied["stage_funnel"]["staged"]["count"], 0)
        self.assertEqual(supplied["stage_funnel"]["event_like"]["count"], 0)
        self.assertEqual(
            supplied["consistency_checks"]["review_queue_counts"]["availability"],
            "not_available",
        )

        omitted = build_coverage_report(
            self.release,
            registry_path=self.registry,
            results_path=self.results,
        )
        self.assertEqual(
            omitted["stage_funnel"]["staged"]["availability"], "not_available"
        )
        self.assertEqual(
            omitted["stage_funnel"]["event_like"]["availability"], "not_available"
        )
        self.assertFalse(omitted["scope"]["review_directory_supplied"])
        self.assertFalse(omitted["scope"]["review_files_supplied"])

    def test_nonempty_metadata_declaration_is_used_without_review_input(self) -> None:
        self.registry_document["coverage"].pop("source_queue_counts")
        self._write_fixture()

        report = self._report(review=False)
        self.assertEqual(report["stage_funnel"]["staged"]["count"], 4)
        self.assertEqual(report["stage_funnel"]["event_like"]["count"], 3)
        self.assertEqual(
            report["stage_funnel"]["staged"]["source"],
            "release.metadata.promotion.source_queue_counts",
        )
        self.assertEqual(
            report["stage_funnel"]["event_like"]["source"],
            "release.metadata.promotion.source_queue_counts",
        )
        self.assertEqual(
            report["consistency_checks"]["review_queue_counts"]["availability"],
            "not_available",
        )

    def test_event_profile_and_field_completeness_keep_unknown_explicit(self) -> None:
        report = self._report()
        counts = report["event_counts"]
        self.assertEqual(counts["total"], 2)
        self.assertEqual(counts["by_layer"]["tactical"], 1)
        self.assertEqual(counts["by_layer"]["operational"], 1)
        self.assertEqual(counts["by_layer"]["unknown"], 0)
        self.assertEqual(counts["by_domain"]["unknown"], 1)
        self.assertEqual(counts["by_region"]["unknown"], 1)
        self.assertEqual(counts["by_region"]["unclassified"], 1)
        self.assertIn("unclassified", counts["by_participant_entity_region"])
        self.assertIn("unknown", counts["by_participant_entity_region"])

        field = report["field_completeness"]
        self.assertEqual(field["locations"]["event_location_present"]["numerator"], 1)
        self.assertEqual(field["dates"]["date_precision_explicit"]["numerator"], 1)
        self.assertEqual(field["roles"]["explicit_role"]["numerator"], 3)
        self.assertEqual(
            field["objectives"]["documented_objective_statement"]["numerator"], 1
        )
        self.assertEqual(
            field["objectives"]["objective_attainment_dimension"]["numerator"], 4
        )
        self.assertEqual(
            field["outcome_dimensions"]["complete_expected_vector"]["numerator"], 3
        )
        self.assertEqual(field["hierarchy"]["parent_link_present"]["numerator"], 1)

    def test_era_boundaries_match_their_labels(self) -> None:
        self.events[0]["end_year"] = -500
        self.events[1]["end_year"] = -499
        self._write_fixture()
        by_era = self._report()["event_counts"]["by_era"]
        self.assertEqual(by_era["before_500_bce"], 0)
        self.assertEqual(by_era["500_bce_to_499_ce"], 2)

    def test_event_type_controls_layer_and_explicit_mismatch_is_reported(self) -> None:
        self.events[0]["event_type"] = "war"
        self.events[0]["layer"] = "tactical"
        self._write_fixture()
        counts = self._report()["event_counts"]
        self.assertEqual(counts["by_layer"]["strategic"], 1)
        self.assertEqual(counts["by_layer"]["tactical"], 0)
        self.assertEqual(counts["explicit_layer_mismatch_count"], 1)
        self.assertEqual(
            counts["explicit_layer_mismatch_event_ids"], ["tactical_event"]
        )
        self.assertEqual(counts["explicit_layer_consistency"]["numerator"], 0)
        self.assertEqual(counts["explicit_layer_consistency"]["denominator"], 1)

    def test_blank_and_nonnumeric_coordinates_are_not_present(self) -> None:
        self.events[1]["location"] = {"latitude": "", "longitude": ""}
        self.events[0]["latitude"] = "north"
        self.events[0]["longitude"] = "east"
        self._write_fixture()
        locations = self._report()["field_completeness"]["locations"]
        self.assertEqual(locations["coordinates_present"]["numerator"], 0)
        self.assertEqual(locations["event_location_present"]["numerator"], 0)

    def test_out_of_range_coordinates_are_not_present(self) -> None:
        self.events[1]["location"] = {"latitude": 91, "longitude": 181}
        self.events[0]["coordinates"] = [181, 91]
        self._write_fixture()
        locations = self._report()["field_completeness"]["locations"]
        self.assertEqual(locations["coordinates_present"]["numerator"], 0)
        self.assertEqual(locations["event_location_present"]["numerator"], 0)

    def test_geojson_point_counts_as_location_and_coordinates(self) -> None:
        for coordinates in ([12.5, 48.1], [180, 90], [-180.0, -90.0]):
            with self.subTest(coordinates=coordinates):
                self.events[0]["geometry"] = {
                    "type": "Point",
                    "coordinates": coordinates,
                }
                self._write_fixture()
                locations = self._report()["field_completeness"]["locations"]
                self.assertEqual(locations["coordinates_present"]["numerator"], 2)
                self.assertEqual(locations["event_location_present"]["numerator"], 2)

    def test_every_supported_geojson_type_is_recognized(self) -> None:
        ring = [[0, 0], [2, 0], [2, 2], [0, 0]]
        geometries = {
            "Point": {"type": "Point", "coordinates": [1, 1]},
            "MultiPoint": {"type": "MultiPoint", "coordinates": [[1, 1]]},
            "LineString": {
                "type": "LineString",
                "coordinates": [[0, 0], [1, 1]],
            },
            "MultiLineString": {
                "type": "MultiLineString",
                "coordinates": [[[0, 0], [1, 1]]],
            },
            "Polygon": {"type": "Polygon", "coordinates": [ring]},
            "MultiPolygon": {
                "type": "MultiPolygon",
                "coordinates": [[ring]],
            },
            "GeometryCollection": {
                "type": "GeometryCollection",
                "geometries": [{"type": "Point", "coordinates": [1, 1]}],
            },
        }
        for geometry_type, geometry in geometries.items():
            with self.subTest(geometry_type=geometry_type):
                self.events[0]["geometry"] = geometry
                self._write_fixture()
                locations = self._report()["field_completeness"]["locations"]
                self.assertEqual(locations["coordinates_present"]["numerator"], 2)
                self.assertEqual(locations["event_location_present"]["numerator"], 2)

    def test_invalid_geojson_is_not_credited(self) -> None:
        invalid_geometries = (
            {"type": "Unsupported", "coordinates": [1, 2]},
            {"type": "Point", "coordinates": [1]},
            {"type": "Point", "coordinates": [True, 2]},
            {"type": "Point", "coordinates": [float("nan"), 2]},
            {"type": "Point", "coordinates": [float("inf"), 2]},
            {"type": "Point", "coordinates": [181, 2]},
            {"type": "Point", "coordinates": [2, 91]},
            {"type": "Point", "coordinates": [10**400, 0]},
            {"type": "Point", "coordinates": [-(10**400), 0]},
            {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1]]],
            },
            {
                "type": "GeometryCollection",
                "geometries": [
                    {"type": "Point", "coordinates": [1, 2]},
                    {"type": "Point", "coordinates": [3]},
                ],
            },
        )
        self.events[1].pop("location")
        for geometry in invalid_geometries:
            with self.subTest(geometry=geometry):
                self.events[0]["geometry"] = geometry
                self._write_fixture()
                locations = self._report()["field_completeness"]["locations"]
                self.assertEqual(locations["coordinates_present"]["numerator"], 0)
                self.assertEqual(locations["event_location_present"]["numerator"], 0)

        self.events[0]["geometry"] = invalid_geometries[0]
        self.events[0]["location_name"] = "Independent legacy location"
        self.events[0]["coordinates"] = [12.5, 48.1]
        self._write_fixture()
        locations = self._report()["field_completeness"]["locations"]
        self.assertEqual(locations["coordinates_present"]["numerator"], 1)
        self.assertEqual(locations["event_location_present"]["numerator"], 1)

    def test_nested_geojson_collection_is_recognized(self) -> None:
        self.events[0]["geometry"] = {
            "type": "GeometryCollection",
            "geometries": [
                {
                    "type": "GeometryCollection",
                    "geometries": [
                        {
                            "type": "MultiLineString",
                            "coordinates": [[[0, 0], [1, 1]]],
                        }
                    ],
                }
            ],
        }
        self._write_fixture()
        locations = self._report()["field_completeness"]["locations"]
        self.assertEqual(locations["coordinates_present"]["numerator"], 2)
        self.assertEqual(locations["event_location_present"]["numerator"], 2)

        self.events[0]["geometry"] = {
            "type": "GeometryCollection",
            "geometries": [],
        }
        self._write_fixture()
        locations = self._report()["field_completeness"]["locations"]
        self.assertEqual(locations["coordinates_present"]["numerator"], 1)
        self.assertEqual(locations["event_location_present"]["numerator"], 1)

    def test_geojson_coordinate_presence_is_existential_after_validation(self) -> None:
        self.events[0]["geometry"] = {
            "type": "MultiPoint",
            "coordinates": [[181, 91], [12.5, 48.1]],
        }
        self._write_fixture()
        locations = self._report()["field_completeness"]["locations"]
        self.assertEqual(locations["coordinates_present"]["numerator"], 2)
        self.assertEqual(locations["event_location_present"]["numerator"], 2)

    def test_plural_parent_only_resolves_within_ledger(self) -> None:
        self.events[1].pop("parent_event_id")
        self.events[1]["parent_event_ids"] = ["tactical_event"]
        self._write_fixture()
        hierarchy = self._report()["field_completeness"]["hierarchy"]
        self.assertEqual(hierarchy["parent_link_present"]["numerator"], 1)
        self.assertEqual(
            hierarchy["parent_link_resolves_within_ledger"]["numerator"], 1
        )
        self.assertEqual(
            hierarchy["parent_link_resolves_within_ledger"]["denominator"], 1
        )

    def test_singular_and_plural_parent_duplicates_count_once(self) -> None:
        self.events[1]["parent_event_ids"] = ["tactical_event"]
        self._write_fixture()
        hierarchy = self._report()["field_completeness"]["hierarchy"]
        self.assertEqual(hierarchy["parent_link_present"]["numerator"], 1)
        self.assertEqual(
            hierarchy["parent_link_resolves_within_ledger"]["numerator"], 1
        )
        self.assertEqual(
            hierarchy["parent_link_resolves_within_ledger"]["denominator"], 1
        )

    def test_parent_reference_whitespace_is_not_normalized(self) -> None:
        self.events[1]["parent_event_ids"] = [" tactical_event "]
        self._write_fixture()
        resolution = self._report()["field_completeness"]["hierarchy"][
            "parent_link_resolves_within_ledger"
        ]
        self.assertEqual(resolution["numerator"], 1)
        self.assertEqual(resolution["denominator"], 2)

    def test_unresolved_plural_parent_is_denominator_only(self) -> None:
        self.events[1].pop("parent_event_id")
        self.events[1]["parent_event_ids"] = [
            "tactical_event",
            "operational_event",
            "missing_event",
        ]
        self._write_fixture()
        hierarchy = self._report()["field_completeness"]["hierarchy"]
        resolution = hierarchy["parent_link_resolves_within_ledger"]
        self.assertEqual(resolution["numerator"], 2)
        self.assertEqual(resolution["denominator"], 3)
        self.assertIn("parent_event_id", resolution["definition"])
        self.assertIn("parent_event_ids", resolution["definition"])

    def test_source_ids_do_not_become_source_families(self) -> None:
        families = self._report()["outcome_source_families"]
        self.assertEqual(families["availability"], "not_available")
        self.assertEqual(families["family_count_distribution"], {})
        self.assertEqual(families["unmapped_event_count"], 2)
        self.assertEqual(families["explicit_mapping_coverage"]["value"], 0.0)
        self.assertEqual(families["multiple_family_coverage"]["value"], None)
        self.assertIn("Source ID counts are not a substitute", families["reason"])

    def test_explicit_outcome_family_mapping_is_deduplicated(self) -> None:
        self.events[0]["outcome_source_family_ids"] = [
            "family_b",
            "family_a",
            "family_a",
        ]
        self.events[1]["outcome_source_ids"] = ["family_source"]
        self._write_fixture()
        families = self._report()["outcome_source_families"]
        self.assertEqual(families["availability"], "available")
        self.assertEqual(families["events_by_family"]["family_a"], 1)
        self.assertEqual(families["events_by_family"]["family_b"], 2)
        self.assertEqual(families["family_count_distribution"], {"1": 1, "2": 1})
        self.assertEqual(families["multiple_family_coverage"]["numerator"], 1)
        self.assertEqual(families["multiple_family_coverage"]["denominator"], 2)

    def test_partial_family_mapping_does_not_treat_unknown_as_zero(self) -> None:
        self.events[0]["outcome_source_family_ids"] = ["family_a", "family_b"]
        self._write_fixture()
        families = self._report()["outcome_source_families"]
        self.assertEqual(families["availability"], "partially_available")
        self.assertEqual(families["explicit_mapping_coverage"]["numerator"], 1)
        self.assertEqual(families["explicit_mapping_coverage"]["denominator"], 2)
        self.assertEqual(families["multiple_family_coverage"]["numerator"], 1)
        self.assertEqual(families["multiple_family_coverage"]["denominator"], 1)
        self.assertEqual(families["family_count_distribution"], {"2": 1})
        self.assertEqual(families["unmapped_event_count"], 1)
        self.assertNotIn("0", families["family_count_distribution"])
        self.assertNotIn("unknown", families["events_by_family"])

    def test_unclassified_family_values_remain_explicitly_unusable(self) -> None:
        self.events[0]["outcome_source_family_ids"] = ["family_a", "unclassified"]
        self._write_fixture()
        families = self._report()["outcome_source_families"]
        self.assertEqual(families["events_with_explicit_family_data"], 1)
        self.assertEqual(families["unusable_mapping_categories"]["unclassified"], 1)
        self.assertNotIn("unclassified", families["events_by_family"])
        markdown = render_coverage_markdown(self._report())
        self.assertIn("events without a usable mapping: 1", markdown)
        self.assertIn("mapping value: 1", markdown)
        self.assertIn("| unclassified | 1 |", markdown)

    def test_registry_coverage_uses_event_participants_not_registry_status(
        self,
    ) -> None:
        report = self._report()
        registry = report["registry_to_rating"]
        self.assertEqual(registry["rated_entities_in_registry"], 3)
        self.assertEqual(registry["registry_entities_total"], 4)
        self.assertEqual(registry["registry_to_rating_ratio"]["value"], 0.75)
        self.assertEqual(registry["registry_status_counts"]["rated"], 1)
        self.assertEqual(registry["registry_status_counts"]["provisional"], 2)

        network = report["network"]
        self.assertEqual(network["component_sizes"], {"1": 2, "2": 1})
        self.assertEqual(network["isolated_entity_count"], 1)
        self.assertEqual(network["isolated_entities"][0]["entity_id"], "entity_c")

    def test_queue_age_is_unavailable_without_disposition_and_timestamp(self) -> None:
        aging = self._report()["unresolved_queue_aging"]
        self.assertEqual(aging["availability"], "not_available")
        self.assertIsNone(aging["timestamp_coverage"]["value"])
        self.assertIn("not reinterpreted", aging["reason"])
        self.assertIn("explicit queue timestamp", aging["reason"].casefold())

    def test_queue_age_uses_only_explicit_unresolved_rows_and_timestamps(self) -> None:
        self.review_rows = [
            {
                "candidate_id": "old",
                "resolution_status": "unresolved",
                "queued_at": "2026-01-01",
            },
            {
                "candidate_id": "recent",
                "resolution_status": "unresolved",
                "queued_at": "2026-06-30T12:00:00Z",
            },
            {"candidate_id": "missing", "resolution_status": "unresolved"},
            {
                "candidate_id": "generic-needs-review",
                "review_status": "needs_review",
                "queued_at": "2025-01-01",
            },
        ]
        self.registry_document["coverage"]["source_queue_counts"][
            "hced-candidates.jsonl"
        ] = 4
        self.metadata["promotion"]["source_queue_counts"]["hced-candidates.jsonl"] = 4
        self._write_fixture()
        aging = self._report()["unresolved_queue_aging"]
        self.assertEqual(aging["availability"], "partially_available")
        self.assertEqual(aging["timestamp_coverage"]["numerator"], 2)
        self.assertEqual(aging["timestamp_coverage"]["denominator"], 3)
        self.assertEqual(aging["age_buckets"]["0_to_30_days"], 1)
        self.assertEqual(aging["age_buckets"]["181_to_365_days"], 1)
        self.assertEqual(aging["missing_timestamp_count"], 1)
        markdown = render_coverage_markdown(self._report())
        self.assertIn("Missing timestamps: 1; invalid timestamps: 0", markdown)
        self.assertIn("Queue-timestamp coverage", markdown)

    def test_created_at_is_not_a_queue_entry_timestamp(self) -> None:
        self.review_rows = [
            {
                "candidate_id": "created-assertion",
                "resolution_status": "unresolved",
                "created_at": "2026-01-01",
            }
        ]
        self.registry_document["coverage"]["source_queue_counts"][
            "hced-candidates.jsonl"
        ] = 1
        self.metadata["promotion"]["source_queue_counts"]["hced-candidates.jsonl"] = 1
        self._write_fixture()
        aging = self._report()["unresolved_queue_aging"]
        self.assertEqual(aging["availability"], "not_available")
        self.assertEqual(aging["timestamp_coverage"]["numerator"], 0)
        self.assertEqual(aging["timestamp_coverage"]["denominator"], 1)
        self.assertIn("no explicit queue timestamp", aging["reason"].casefold())

    def test_partial_network_coverage_stays_visible_in_markdown(self) -> None:
        self.results_document["entities"].append(
            {"id": "entity_d", "name": "Entity D", "network_component": None}
        )
        self._write_fixture()
        report = self._report()
        self.assertEqual(report["network"]["availability"], "partially_available")
        self.assertEqual(report["network"]["entities_missing_component"], 1)
        markdown = render_coverage_markdown(report)
        self.assertIn("entities missing a component: 1", markdown)
        self.assertIn("Opponent-network ratios", markdown)

    def test_rejections_preserve_pipeline_units_and_zero_counters(self) -> None:
        rejections = self._report()["rejections"]
        self.assertEqual(rejections["availability"], "available")
        self.assertEqual(rejections["pipelines"]["hced"]["total"], 1)
        self.assertEqual(
            rejections["pipelines"]["hced"]["reason_counts"]["unknown_identity"], 0
        )
        self.assertNotIn("global_total", rejections)

    def test_renderers_are_deterministic_and_write_paired_outputs(self) -> None:
        report = self._report()
        first = render_coverage_json(report)
        second = render_coverage_json(report)
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first), report)
        self.assertNotIn(str(self.root), first)
        markdown = render_coverage_markdown(report)
        self.assertEqual(markdown, render_coverage_markdown(report))
        self.assertIn("# Military History Elo coverage and quality report", markdown)
        self.assertIn("Observed corpus coverage is not an estimate", markdown)
        self.assertIn(
            "| Metric | Numerator | Denominator | Coverage | Unit | Availability | Definition | Reason |",
            markdown,
        )
        self.assertIn("iwd_components_aggregated", markdown)
        self.assertIn("iwd_components_attached_to_rated_parents", markdown)
        self.assertIn("iwd_parent_wars_rated", markdown)
        self.assertIn("Outcome-source family ratios", markdown)

        first_output = write_coverage_report(report, self.root / "paired-output-1")
        second_output = write_coverage_report(report, self.root / "paired-output-2")
        expected_bytes = (first.encode("utf-8"), markdown.encode("utf-8"))
        for first_path, second_path, expected in zip(
            first_output, second_output, expected_bytes, strict=True
        ):
            first_bytes = first_path.read_bytes()
            second_bytes = second_path.read_bytes()
            self.assertEqual(first_bytes, expected)
            self.assertEqual(second_bytes, expected)
            self.assertNotIn(b"\r\n", first_bytes)
            self.assertNotIn(b"\r\n", second_bytes)
            self.assertEqual(
                hashlib.sha256(first_bytes).hexdigest(),
                hashlib.sha256(second_bytes).hexdigest(),
            )

    def test_every_ratio_exposes_required_scientific_metadata(self) -> None:
        report = self._report()

        def visit(value: Any) -> None:
            if isinstance(value, dict):
                if "value" in value and "availability" in value:
                    for key in (
                        "numerator",
                        "denominator",
                        "unit",
                        "definition",
                        "availability",
                    ):
                        self.assertIn(key, value)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(report)

    def test_cli_writes_only_the_requested_paired_artifacts(self) -> None:
        destination = self.root / "cli-output"
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "report_coverage.py"),
                "--data",
                str(self.release),
                "--review",
                str(self.review),
                "--registry",
                str(self.registry),
                "--results",
                str(self.results),
                "--output-dir",
                str(destination),
            ],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            sorted(path.name for path in destination.iterdir()),
            ["coverage.json", "coverage.md"],
        )

    def test_cli_rejects_basename_path_escape(self) -> None:
        destination = self.root / "safe-output"
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "report_coverage.py"),
                "--data",
                str(self.release),
                "--registry",
                str(self.registry),
                "--results",
                str(self.results),
                "--output-dir",
                str(destination),
                "--basename",
                "../escaped",
            ],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse((self.root / "escaped.json").exists())
        self.assertFalse((self.root / "escaped.md").exists())

    def test_cli_rejects_explicitly_missing_optional_inputs(self) -> None:
        valid_inputs = {
            "--review": self.review,
            "--registry": self.registry,
            "--results": self.results,
        }
        for missing_flag in valid_inputs:
            with self.subTest(flag=missing_flag):
                arguments = [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "report_coverage.py"),
                    "--data",
                    str(self.release),
                    "--format",
                    "json",
                ]
                for flag, path in valid_inputs.items():
                    arguments.extend(
                        [
                            flag,
                            str(self.root / "missing-input")
                            if flag == missing_flag
                            else str(path),
                        ]
                    )
                completed = subprocess.run(
                    arguments,
                    cwd=PROJECT_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("missing-input", completed.stderr)

    def test_as_of_requires_an_exact_iso_date(self) -> None:
        for value in (
            "2026-07-13garbage",
            "2026-07-13T00:00:00",
            " 2026-07-13 ",
            "",
            "2026-02-30",
        ):
            with self.subTest(value=value), self.assertRaises(CoverageInputError):
                build_coverage_report(
                    self.release,
                    registry_path=self.registry,
                    as_of=value,
                )

    def test_cli_rejects_nonexact_as_of_date(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "report_coverage.py"),
                "--data",
                str(self.release),
                "--review",
                str(self.review),
                "--registry",
                str(self.registry),
                "--results",
                str(self.results),
                "--as-of",
                "2026-07-13T00:00:00",
                "--format",
                "json",
            ],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("expected YYYY-MM-DD", completed.stderr)


class CommittedCoverageArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_coverage_report(
            PROJECT_ROOT / "data" / "release",
            registry_path=PROJECT_ROOT / "data" / "catalog" / "registry.json",
            results_path=PROJECT_ROOT / "web" / "data" / "results.json",
        )
        cls.events = json.loads(
            (PROJECT_ROOT / "data" / "release" / "events.json").read_text(
                encoding="utf-8"
            )
        )
        cls.seed_events = json.loads(
            (PROJECT_ROOT / "data" / "seed" / "events.json").read_text(encoding="utf-8")
        )
        cls.sources = json.loads(
            (PROJECT_ROOT / "data" / "release" / "sources.json").read_text(
                encoding="utf-8"
            )
        )
        cls.results = json.loads(
            (PROJECT_ROOT / "web" / "data" / "results.json").read_text(encoding="utf-8")
        )
        cls.sources_by_id = {source["id"]: source for source in cls.sources}

    def test_report_matches_release_and_explicit_outcome_family_contract(self) -> None:
        rated_events = [
            event
            for event in self.events
            if str(event.get("status", "complete")).casefold() == "complete"
        ]
        self.assertEqual(len(rated_events), 4_797)
        self.assertEqual(self.report["event_counts"]["total"], len(rated_events))
        self.assertEqual(
            sum(self.report["event_counts"]["by_layer"].values()), len(rated_events)
        )
        self.assertEqual(
            self.report["event_counts"]["by_region"]["unknown"], len(rated_events)
        )
        self.assertEqual(
            self.report["historical_completeness"]["status"], "not_estimated"
        )
        families = self.report["outcome_source_families"]
        self.assertEqual(families["availability"], "partially_available")
        self.assertEqual(families["events_with_explicit_family_data"], 4_757)
        self.assertEqual(families["events_without_explicit_family_data"], 40)
        self.assertEqual(families["unmapped_event_count"], 40)
        self.assertEqual(
            families["events_by_family"],
            {
                "english_historical_review": 1,
                "founders_online_jefferson_papers": 2,
                "hced": 4_523,
                "historic_england": 3,
                "hungarian_military_history_institute": 2,
                "iwbd": 151,
                "iwd": 64,
                "national_park_service_creek_war": 1,
                "national_park_service_revolution": 1,
                "nigeria_national_library_civil_war": 1,
                "rcahmw_coflein": 1,
                "ucdp_conflict_termination": 7,
            },
        )
        self.assertEqual(families["family_count_distribution"], {"1": 4_757})
        self.assertEqual(families["explicit_mapping_coverage"]["numerator"], 4_757)
        self.assertEqual(families["explicit_mapping_coverage"]["denominator"], 4_797)
        self.assertEqual(families["multiple_family_coverage"]["numerator"], 0)
        self.assertEqual(families["multiple_family_coverage"]["denominator"], 4_757)
        self.assertEqual(set(families["per_event_counts"].values()), {1})

        mapped_ids = set(families["per_event_counts"])
        unmapped_ids = {event["id"] for event in rated_events} - mapped_ids
        seed_ids = {event["id"] for event in self.seed_events}
        self.assertEqual(unmapped_ids, seed_ids)
        self.assertEqual(len(unmapped_ids), 40)
        for event in rated_events:
            with self.subTest(event_id=event["id"]):
                if event["id"] in seed_ids:
                    self.assertNotIn("outcome_source_ids", event)
                    self.assertNotIn("outcome_source_family_ids", event)
                else:
                    self.assertEqual(len(event["outcome_source_ids"]), 1)
                    self.assertEqual(len(event["outcome_source_family_ids"]), 1)
                    self.assertTrue(
                        set(event["outcome_source_ids"]).issubset(event["source_ids"])
                    )

    def test_source_manifest_roles_keep_non_outcome_provenance_out_of_coverage(
        self,
    ) -> None:
        self.assertEqual(len(self.sources), 284)
        manifest_contract = sorted(
            (
                source["id"],
                source.get("source_family_id"),
                source.get("evidence_roles"),
            )
            for source in self.sources
        )
        manifest_digest = hashlib.sha256(
            json.dumps(
                manifest_contract,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            manifest_digest,
            "4b9e0458ae2dc5ae3ccf6900e60cf51c0a59fe517f6135cbf3cb80fe8cd4aa81",
        )
        self.assertTrue(
            all(
                source.get("source_family_id") and source.get("evidence_roles")
                for source in self.sources
            )
        )
        self.assertEqual(
            Counter(
                role for source in self.sources for role in source["evidence_roles"]
            ),
            {
                "curated_reference_pending_claim_level_outcome_locator": 70,
                "derived_project_continuity_convention": 1,
                "identity_boundary_or_context_reference": 223,
                "identity_crosswalk": 1,
                "identity_registry": 2,
                "outcome": 14,
                "outcome_consistency_crosscheck": 47,
            },
        )
        self.assertEqual(
            len({source["source_family_id"] for source in self.sources}), 176
        )
        outcome_source_ids = {
            source["id"]
            for source in self.sources
            if "outcome" in source["evidence_roles"]
        }
        self.assertEqual(
            outcome_source_ids,
            {
                "hced_dataset",
                "iwd_dataset",
                "iwbd_dataset",
                "ucdp_termination_conflict",
                "wave7_founders_emuckfaw",
                "wave7_hungary_military_museum",
                "wave7_nigeria_civil_war_history",
                "wave7_nps_creek_war",
                "wave7_nps_revolution_timeline",
                "wave7_west_ehr_lincolnshire_1470",
                "wave7_west_he_bamburgh",
                "wave7_west_he_bosworth",
                "wave7_west_he_caister",
                "wave7_west_rcahmw_twt",
            },
        )
        self.assertEqual(
            {
                source["id"]: source["source_family_id"]
                for source in self.sources
                if source["id"] in outcome_source_ids
            },
            {
                "hced_dataset": "hced",
                "iwd_dataset": "iwd",
                "iwbd_dataset": "iwbd",
                "ucdp_termination_conflict": "ucdp_conflict_termination",
                "wave7_founders_emuckfaw": "founders_online_jefferson_papers",
                "wave7_hungary_military_museum": "hungarian_military_history_institute",
                "wave7_nigeria_civil_war_history": "nigeria_national_library_civil_war",
                "wave7_nps_creek_war": "national_park_service_creek_war",
                "wave7_nps_revolution_timeline": "national_park_service_revolution",
                "wave7_west_ehr_lincolnshire_1470": "english_historical_review",
                "wave7_west_he_bamburgh": "historic_england",
                "wave7_west_he_bosworth": "historic_england",
                "wave7_west_he_caister": "historic_england",
                "wave7_west_rcahmw_twt": "rcahmw_coflein",
            },
        )
        expected_negative_controls = {
            "hced_seshat_crosswalk": (
                "hced_seshat_crosswalk_file_11018172",
                "identity_crosswalk",
            ),
            "cliopatria_polities": ("cliopatria_v0_2_0", "identity_registry"),
            "cliopatria_v020": ("cliopatria_v0_2_0", "identity_registry"),
            "ucdp_termination_dyad": (
                "ucdp_conflict_termination",
                "outcome_consistency_crosscheck",
            ),
        }
        for source_id, (family_id, evidence_role) in expected_negative_controls.items():
            with self.subTest(source_id=source_id):
                source = self.sources_by_id[source_id]
                self.assertEqual(source["source_family_id"], family_id)
                self.assertEqual(source["evidence_roles"], [evidence_role])
                self.assertNotIn("outcome", source["evidence_roles"])

        curated_references = [
            source
            for source in self.sources
            if source["evidence_roles"]
            == ["curated_reference_pending_claim_level_outcome_locator"]
        ]
        self.assertEqual(len(curated_references), 52)
        self.assertTrue(
            all(source["id"] not in outcome_source_ids for source in curated_references)
        )

    def test_dashboard_event_source_contract_matches_release_artifact(self) -> None:
        release_by_id = {event["id"]: event for event in self.events}
        dashboard_events = self.results["events"]
        dashboard_by_id = {event["id"]: event for event in dashboard_events}

        self.assertEqual(len(release_by_id), 4_797)
        self.assertEqual(len(dashboard_by_id), 4_797)
        self.assertEqual(set(dashboard_by_id), set(release_by_id))

        mapped = 0
        for event_id, release_event in release_by_id.items():
            with self.subTest(event_id=event_id):
                dashboard_event = dashboard_by_id[event_id]
                self.assertEqual(
                    dashboard_event["source_ids"], release_event["source_ids"]
                )
                for field_name in (
                    "outcome_source_ids",
                    "outcome_source_family_ids",
                ):
                    self.assertEqual(
                        dashboard_event.get(field_name),
                        release_event.get(field_name),
                    )

                expected_sources = [
                    {
                        "id": source["id"],
                        "title": source["title"],
                        "url": source["url"],
                        "source_family_id": source["source_family_id"],
                        # The dashboard round-trips Source through its
                        # canonical model, which sorts this set-like field.
                        "evidence_roles": sorted(source["evidence_roles"]),
                    }
                    for source_id in release_event["source_ids"]
                    for source in (self.sources_by_id[source_id],)
                ]
                self.assertEqual(dashboard_event["sources"], expected_sources)
                mapped += "outcome_source_ids" in dashboard_event

        self.assertEqual(mapped, 4_757)
        self.assertEqual(len(dashboard_events) - mapped, 40)

    def test_registry_coverage_is_an_observed_ratio_only(self) -> None:
        ratio = self.report["registry_to_rating"]["registry_to_rating_ratio"]
        self.assertEqual(
            ratio["numerator"],
            self.report["registry_to_rating"]["rated_entities_in_registry"],
        )
        self.assertEqual(
            ratio["denominator"],
            self.report["registry_to_rating"]["registry_entities_total"],
        )
        self.assertNotEqual(
            ratio["value"], self.report["historical_completeness"]["value"]
        )


if __name__ == "__main__":
    unittest.main()
