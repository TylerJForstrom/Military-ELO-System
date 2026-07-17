import json
import hashlib
import math
import unittest
from collections import Counter
from pathlib import Path

from military_elo.audit import audit_dataset, audit_evidence
from military_elo.canonical import (
    CanonicalEvent,
    LocationProvenance,
    geometry_validation_error,
    hced_point_geometry_validation_error,
)
from military_elo.coverage import _field_completeness
from military_elo.config import ModelConfig
from military_elo.engine import EloEngine
from military_elo.models import Entity, Event, Participant, Source
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_CANDIDATE_IDS,
    HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256,
    HCED_COUNTRY_QUARANTINE_EVENT_SHA256,
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_EXPECTED_QUARANTINE_OVERLAP,
    HCED_EXPECTED_QUARANTINE_UNION,
    HCED_LOCATION_MACHINE_LOCAL_AUDIT_SNAPSHOT_SHA256,
    HCED_LOCATION_QUARANTINE_POLICY_SHA256,
    HCED_POINT_QUARANTINE_CANDIDATE_IDS,
    HCED_POINT_QUARANTINE_CANDIDATE_SHA256,
    HCED_POINT_QUARANTINE_EVENT_SHA256,
    HCED_POINT_QUARANTINE_IDS,
    build_hced_location_fields,
    hced_candidate_id,
    parse_hced_point,
)
from military_elo.promotion.orchestrator import (
    _index_hced_candidates,
    _validate_hced_event_source_parity,
)


PROVENANCE = {
    "source_id": "hced_dataset",
    "source_record_id": "Exact Source Record",
    "assertion_status": "unreviewed_source_assertion",
    "coordinate_precision": "unknown",
}
ROOT = Path(__file__).resolve().parents[1]


def _candidate(candidate_id: str = "hced-Exact Source Record1900-1") -> dict:
    return {
        "candidate_id": candidate_id,
        "source_record_id": "Exact Source Record",
        "modern_location_country": "Source jurisdiction label",
        "latitude": "12.5",
        "longitude": "-45.25",
        "name": "Shared name",
        "year_best": 1900,
    }


def _rating_event(*, with_location: bool) -> Event:
    location = (
        {
            "hced_candidate_id": "hced-Exact Source Record1900-1",
            "modern_location_country": "Source jurisdiction label",
            "geometry": {"type": "Point", "coordinates": [-45.25, 12.5]},
            "location_provenance": PROVENANCE,
        }
        if with_location
        else {}
    )
    return Event.from_dict(
        {
            "id": "event-1",
            "name": "Event",
            "year": 1900,
            "end_year": 1900,
            "event_type": "engagement",
            "war_type": "interstate_limited",
            "scale": "battle",
            "stakes": "limited",
            "decisiveness": 0.7,
            "confidence": 0.8,
            "participants": [
                {
                    "entity_id": "a",
                    "side": "a",
                    "outcome": {"battlefield_control": 1.0},
                },
                {
                    "entity_id": "b",
                    "side": "b",
                    "outcome": {"battlefield_control": 0.0},
                },
            ],
            "source_ids": ["hced_dataset"],
            **location,
        }
    )


class HcedPointParserTests(unittest.TestCase):
    def test_quarantine_module_imports_with_final_manifest_sizes(self) -> None:
        self.assertEqual(len(HCED_POINT_QUARANTINE_CANDIDATE_IDS), 340)
        self.assertEqual(len(HCED_COUNTRY_QUARANTINE_CANDIDATE_IDS), 94)

    def test_tracked_policy_hashes_duplicates_overlap_and_snapshot_provenance(self) -> None:
        def sorted_newline_hash(values: tuple[str, ...]) -> str:
            payload = "".join(f"{value}\n" for value in sorted(values))
            return hashlib.sha256(payload.encode("utf-8")).hexdigest()

        self.assertEqual(
            HCED_LOCATION_MACHINE_LOCAL_AUDIT_SNAPSHOT_SHA256,
            "670300a7dd145c675fa5219d3d6cbe371d1437c358174650c3124baeb9eea954",
        )
        policy_path = ROOT / "data" / "policy" / "hced-location-quarantine.tsv"
        policy_bytes = policy_path.read_bytes()
        self.assertTrue(policy_bytes.endswith(b"\n"))
        self.assertEqual(
            hashlib.sha256(policy_bytes).hexdigest(),
            HCED_LOCATION_QUARANTINE_POLICY_SHA256,
        )
        lines = policy_bytes.decode("utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "candidate_id\tevent_id\tfield\treason_codes",
        )
        rows = [line.split("\t") for line in lines[1:]]
        self.assertEqual(len(rows), 434)
        self.assertTrue(all(len(row) == 4 and all(row) for row in rows))
        self.assertEqual(rows, sorted(rows))
        self.assertEqual(
            Counter(row[2] for row in rows),
            {"geometry": 340, "modern_location_country": 94},
        )
        point_rows = [row for row in rows if row[2] == "geometry"]
        country_rows = [
            row for row in rows if row[2] == "modern_location_country"
        ]
        self.assertEqual(
            tuple(row[0] for row in point_rows),
            HCED_POINT_QUARANTINE_CANDIDATE_IDS,
        )
        self.assertEqual(
            tuple(row[0] for row in country_rows),
            HCED_COUNTRY_QUARANTINE_CANDIDATE_IDS,
        )
        self.assertEqual(
            sorted_newline_hash(tuple(row[1] for row in point_rows)),
            HCED_POINT_QUARANTINE_EVENT_SHA256,
        )
        self.assertEqual(
            sorted_newline_hash(tuple(row[1] for row in country_rows)),
            HCED_COUNTRY_QUARANTINE_EVENT_SHA256,
        )
        self.assertEqual(
            len(HCED_POINT_QUARANTINE_CANDIDATE_IDS),
            len(set(HCED_POINT_QUARANTINE_CANDIDATE_IDS)),
        )
        self.assertEqual(
            len(HCED_COUNTRY_QUARANTINE_CANDIDATE_IDS),
            len(set(HCED_COUNTRY_QUARANTINE_CANDIDATE_IDS)),
        )
        self.assertEqual(
            tuple(sorted(HCED_POINT_QUARANTINE_CANDIDATE_IDS)),
            HCED_POINT_QUARANTINE_CANDIDATE_IDS,
        )
        self.assertEqual(
            tuple(sorted(HCED_COUNTRY_QUARANTINE_CANDIDATE_IDS)),
            HCED_COUNTRY_QUARANTINE_CANDIDATE_IDS,
        )
        self.assertEqual(
            sorted_newline_hash(HCED_POINT_QUARANTINE_CANDIDATE_IDS),
            HCED_POINT_QUARANTINE_CANDIDATE_SHA256,
        )
        self.assertEqual(
            sorted_newline_hash(HCED_COUNTRY_QUARANTINE_CANDIDATE_IDS),
            HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256,
        )
        self.assertEqual(
            len(HCED_POINT_QUARANTINE_IDS & HCED_COUNTRY_QUARANTINE_IDS),
            HCED_EXPECTED_QUARANTINE_OVERLAP,
        )
        self.assertEqual(
            len(HCED_POINT_QUARANTINE_IDS | HCED_COUNTRY_QUARANTINE_IDS),
            HCED_EXPECTED_QUARANTINE_UNION,
        )
        self.assertEqual(
            HCED_POINT_QUARANTINE_EVENT_SHA256,
            "ddcc837d94e1d6930265d9b73260fca40b17674ce6b7f2c2aafa72895e149d5b",
        )
        self.assertEqual(
            HCED_COUNTRY_QUARANTINE_EVENT_SHA256,
            "a8d96507bcbfef9498b8d8f1d5e8310e8eb7555832c928ded353adad26a5353c",
        )

    def test_valid_pair_is_emitted_in_longitude_latitude_order(self) -> None:
        self.assertEqual(
            parse_hced_point("12.5", "-45.25"),
            {"type": "Point", "coordinates": [-45.25, 12.5]},
        )
        self.assertEqual(
            parse_hced_point(-90, 180),
            {"type": "Point", "coordinates": [180.0, -90.0]},
        )

    def test_bool_blank_malformed_nonfinite_and_range_fail_closed(self) -> None:
        invalid_pairs = [
            (True, 1),
            (1, False),
            ("", "1"),
            (" ", "1"),
            (" 1", "2"),
            ("1", "2 "),
            (None, 1),
            ("north", "1"),
            ("1", "1,2"),
            ("1e1", "2"),
            (math.nan, 1),
            (1, math.inf),
            (91, 1),
            (-91, 1),
            (1, 181),
            (1, -181),
            ([1], 2),
            (1, {"longitude": 2}),
        ]
        for latitude, longitude in invalid_pairs:
            with self.subTest(latitude=latitude, longitude=longitude):
                self.assertIsNone(parse_hced_point(latitude, longitude))

    def test_hced_zero_sentinel_and_apparent_swap_are_not_corrected(self) -> None:
        self.assertIsNone(parse_hced_point(0, 0))
        self.assertIsNone(parse_hced_point(120, 45))
        self.assertIsNone(parse_hced_point(45, 200))
        self.assertEqual(
            parse_hced_point(0, 12),
            {"type": "Point", "coordinates": [12.0, 0.0]},
        )
        self.assertIsNone(
            geometry_validation_error(
                {"type": "Point", "coordinates": [0, 0]}
            ),
            "the source-specific HCED sentinel rule must not outlaw GeoJSON [0, 0]",
        )


class HcedLocationBindingTests(unittest.TestCase):
    def test_source_parity_gate_rejects_valid_but_wrong_location_values(self) -> None:
        candidate = _candidate()
        event = {
            "id": "hced_hced_exact_source_record1900_1",
            "source_ids": ["hced_dataset"],
            **build_hced_location_fields(
                candidate,
                point_quarantine_ids=frozenset(),
                country_quarantine_ids=frozenset(),
            ),
        }
        _validate_hced_event_source_parity(event, candidate)
        mutations = [
            {
                **event,
                "geometry": {"type": "Point", "coordinates": [-44.25, 12.5]},
            },
            {**event, "modern_location_country": "Different valid label"},
            {
                **event,
                "location_provenance": {
                    **event["location_provenance"],
                    "source_record_id": "Different Source Record",
                },
            },
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                _validate_hced_event_source_parity(mutation, candidate)

    def test_authoritative_candidate_index_rejects_duplicate_ids(self) -> None:
        candidate = _candidate()
        with self.assertRaisesRegex(ValueError, "Duplicate HCED candidate_id"):
            _index_hced_candidates([candidate, dict(candidate)])

    def test_location_fields_copy_exact_ids_text_and_closed_provenance(self) -> None:
        candidate = _candidate()
        result = build_hced_location_fields(
            candidate,
            point_quarantine_ids=frozenset(),
            country_quarantine_ids=frozenset(),
        )
        self.assertEqual(result["hced_candidate_id"], candidate["candidate_id"])
        self.assertEqual(
            result["modern_location_country"],
            candidate["modern_location_country"],
        )
        self.assertEqual(
            result["geometry"],
            {"type": "Point", "coordinates": [-45.25, 12.5]},
        )
        self.assertEqual(result["location_provenance"], PROVENANCE)
        self.assertEqual(
            set(result["location_provenance"]),
            {
                "source_id",
                "source_record_id",
                "assertion_status",
                "coordinate_precision",
            },
        )

    def test_quarantine_is_candidate_id_only_and_fields_are_withheld(self) -> None:
        quarantined = _candidate("hced-shared-name-1900-a")
        same_name_year = _candidate("hced-shared-name-1900-b")
        point_quarantine = frozenset({quarantined["candidate_id"]})
        country_quarantine = frozenset({quarantined["candidate_id"]})

        withheld = build_hced_location_fields(
            quarantined,
            point_quarantine_ids=point_quarantine,
            country_quarantine_ids=country_quarantine,
        )
        self.assertEqual(
            withheld,
            {"hced_candidate_id": quarantined["candidate_id"]},
        )
        retained = build_hced_location_fields(
            same_name_year,
            point_quarantine_ids=point_quarantine,
            country_quarantine_ids=country_quarantine,
        )
        self.assertIn("geometry", retained)
        self.assertIn("modern_location_country", retained)
        self.assertNotIn("quarantine_reason", json.dumps(retained))

    def test_one_surviving_field_still_carries_provenance(self) -> None:
        candidate = _candidate()
        point_withheld = build_hced_location_fields(
            candidate,
            point_quarantine_ids=frozenset({candidate["candidate_id"]}),
            country_quarantine_ids=frozenset(),
        )
        self.assertNotIn("geometry", point_withheld)
        self.assertIn("modern_location_country", point_withheld)
        self.assertEqual(point_withheld["location_provenance"], PROVENANCE)

        country_withheld = build_hced_location_fields(
            candidate,
            point_quarantine_ids=frozenset(),
            country_quarantine_ids=frozenset({candidate["candidate_id"]}),
        )
        self.assertIn("geometry", country_withheld)
        self.assertNotIn("modern_location_country", country_withheld)
        self.assertEqual(country_withheld["location_provenance"], PROVENANCE)

    def test_candidate_id_is_never_coerced_or_trimmed(self) -> None:
        for invalid in (None, 7, True, "", " hced-x", "hced-x "):
            with self.subTest(invalid=invalid), self.assertRaises(
                (TypeError, ValueError)
            ):
                hced_candidate_id({"candidate_id": invalid})

    def test_crosswalk_promotion_carries_the_exact_candidate_id(self) -> None:
        row = {
            **_candidate("hced-Exact punctuation, and spaces1900-1"),
            "year_low": 1900,
            "year_high": 1900,
            "side_1_raw": "Alpha",
            "side_2_raw": "Beta",
            "winner_raw": "Alpha",
            "loser_raw": "Beta",
            "seshat_side_1_candidates": ["alpha"],
            "seshat_side_2_candidates": ["beta"],
            "war_names": [],
            "scale_raw": 2,
            "source_row": 1,
        }
        owners = {
            code: [
                {
                    "candidate_id": f"clio-{code}",
                    "canonical_name_candidate": code.title(),
                    "start_year": 1800,
                    "end_year": 2000,
                    "seshat_ids": [code],
                }
            ]
            for code in ("alpha", "beta")
        }
        result = promote_hced_crosswalk_rows(
            [row], owners, set(), lambda polity: None
        )
        self.assertEqual(
            result["events"][0]["hced_candidate_id"], row["candidate_id"]
        )


class LocationModelExportCoverageTests(unittest.TestCase):
    def test_hced_geometry_contract_rejects_non_point_and_bad_ordinates(self) -> None:
        invalid_geometries = [
            {"type": "LineString", "coordinates": [[1, 2], [3, 4]]},
            {"type": "Point", "coordinates": [1, 2, 3]},
            {"type": "Point", "coordinates": [True, 2]},
            {"type": "Point", "coordinates": [1, math.inf]},
            {"type": "Point", "coordinates": [181, 2]},
            {"type": "Point", "coordinates": [1, -91]},
            {
                "type": "Point",
                "coordinates": [1, 2],
                "quarantine_reason": "must-not-publish",
            },
        ]
        event_template = _rating_event(with_location=True).to_dict()
        canonical_template = {
            "id": "event-1",
            "name": "Event",
            "source_ids": ["hced_dataset"],
            "hced_candidate_id": "hced-Exact Source Record1900-1",
            "modern_location_country": "Source jurisdiction label",
            "location_provenance": PROVENANCE,
        }
        for geometry in invalid_geometries:
            with self.subTest(geometry=geometry):
                self.assertIsNotNone(hced_point_geometry_validation_error(geometry))
                with self.assertRaises(ValueError):
                    Event.from_dict({**event_template, "geometry": geometry})
                with self.assertRaises(ValueError):
                    CanonicalEvent.from_dict(
                        {**canonical_template, "geometry": geometry}
                    )

    def test_hced_point_boundaries_and_zero_are_valid_without_narrowing_legacy(self) -> None:
        for coordinates in ([-180, -90], [180, 90], [0, 0]):
            with self.subTest(coordinates=coordinates):
                geometry = {"type": "Point", "coordinates": coordinates}
                self.assertIsNone(hced_point_geometry_validation_error(geometry))
                event = Event.from_dict(
                    {
                        **_rating_event(with_location=True).to_dict(),
                        "geometry": geometry,
                    }
                )
                self.assertEqual(event.to_dict()["geometry"], geometry)
                canonical = CanonicalEvent.from_dict(
                    {
                        "id": "event-1",
                        "name": "Event",
                        "source_ids": ["hced_dataset"],
                        "hced_candidate_id": "hced-Exact Source Record1900-1",
                        "geometry": geometry,
                        "location_provenance": PROVENANCE,
                    }
                )
                self.assertEqual(canonical.to_dict()["geometry"], geometry)

        legacy_line = {
            "type": "LineString",
            "coordinates": [[0, 0], [1, 1]],
        }
        self.assertEqual(
            CanonicalEvent("legacy", "Legacy", geometry=legacy_line).to_dict()[
                "geometry"
            ],
            legacy_line,
        )
        self.assertIsNone(
            geometry_validation_error({"type": "Point", "coordinates": [0, 0]})
        )

    def test_audit_rechecks_strict_hced_geometry_after_model_boundary(self) -> None:
        invalid_geometries = [
            {"type": "LineString", "coordinates": [[1, 2], [3, 4]]},
            {"type": "Point", "coordinates": [1, 2, 3]},
            {"type": "Point", "coordinates": [False, 2]},
            {"type": "Point", "coordinates": [1, float("nan")]},
            {"type": "Point", "coordinates": [-181, 2]},
            {"type": "Point", "coordinates": [1, 91]},
            {
                "type": "Point",
                "coordinates": [1, 2],
                "quarantine_reason": "must-not-publish",
            },
        ]
        records = []
        provenance = LocationProvenance.from_dict(PROVENANCE)
        for index, geometry in enumerate(invalid_geometries):
            event = CanonicalEvent(f"bad-{index}", "Bad")
            object.__setattr__(event, "geometry", geometry)
            object.__setattr__(event, "hced_candidate_id", f"hced-bad-{index}")
            object.__setattr__(event, "location_provenance", provenance)
            records.append(event)
        codes_by_id = {
            issue.record_id: issue.code
            for issue in audit_evidence(canonical_events=records)
        }
        self.assertEqual(
            codes_by_id,
            {f"bad-{index}": "invalid_hced_location_geometry" for index in range(7)},
        )

    def test_canonical_audit_rechecks_source_registry_and_provenance_linkage(self) -> None:
        event = CanonicalEvent.from_dict(
            {
                "id": "canonical-location",
                "name": "Canonical location",
                "source_ids": ["hced_dataset"],
                "hced_candidate_id": "hced-canonical-location-1",
                "geometry": {"type": "Point", "coordinates": [1, 2]},
                "location_provenance": PROVENANCE,
            }
        )
        unknown_codes = {
            issue.code
            for issue in audit_evidence(canonical_events=[event], sources={})
        }
        self.assertIn("unknown_canonical_event_source", unknown_codes)

        object.__setattr__(event, "source_ids", ())
        linked_source = Source(
            "hced_dataset", "HCED", "https://example.test/hced"
        )
        unlinked_codes = {
            issue.code
            for issue in audit_evidence(
                canonical_events=[event],
                sources={linked_source.id: linked_source},
            )
        }
        self.assertIn(
            "canonical_location_provenance_source_not_linked", unlinked_codes
        )

    def test_schema_conditionally_requires_the_exact_hced_point_shape(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "event.schema.json").read_text(encoding="utf-8")
        )
        hced_point = schema["$defs"]["hcedLocationPoint"]
        self.assertEqual(hced_point["properties"]["type"], {"const": "Point"})
        self.assertFalse(hced_point["additionalProperties"])
        coordinates = hced_point["properties"]["coordinates"]
        self.assertEqual(coordinates["minItems"], 2)
        self.assertEqual(coordinates["maxItems"], 2)
        self.assertFalse(coordinates["items"])
        self.assertEqual(
            coordinates["prefixItems"],
            [
                {"type": "number", "minimum": -180, "maximum": 180},
                {"type": "number", "minimum": -90, "maximum": 90},
            ],
        )
        generic_position = schema["$defs"]["position"]
        self.assertEqual(generic_position["minItems"], 2)
        self.assertNotIn("maxItems", generic_position)
        conditions = schema["allOf"]
        self.assertIn(
            {
                "if": {"required": ["hced_candidate_id", "geometry"]},
                "then": {
                    "required": ["location_provenance"],
                    "properties": {
                        "geometry": {"$ref": "#/$defs/hcedLocationPoint"}
                    },
                },
            },
            conditions,
        )
        self.assertIn(
            {
                "if": {"required": ["hced_candidate_id"]},
                "then": {
                    "required": ["source_ids"],
                    "properties": {
                        "source_ids": {"contains": {"const": "hced_dataset"}}
                    },
                },
            },
            conditions,
        )
        self.assertIn(
            {
                "if": {
                    "required": ["outcome_source_ids"],
                    "properties": {
                        "outcome_source_ids": {
                            "contains": {"const": "hced_dataset"}
                        }
                    },
                },
                "then": {"required": ["hced_candidate_id"]},
            },
            conditions,
        )

    def test_candidate_and_hced_outcome_bindings_fail_closed(self) -> None:
        plain = _rating_event(with_location=False).to_dict()
        with self.assertRaisesRegex(ValueError, "requires hced_dataset"):
            Event.from_dict(
                {
                    **plain,
                    "source_ids": ["other_source"],
                    "hced_candidate_id": "hced-exact-1",
                }
            )
        with self.assertRaisesRegex(ValueError, "HCED outcome source"):
            Event.from_dict(
                {
                    **plain,
                    "outcome_source_ids": ["hced_dataset"],
                    "outcome_source_family_ids": ["hced"],
                }
            )
        with self.assertRaisesRegex(ValueError, "requires hced_dataset"):
            CanonicalEvent(
                "canonical-unlinked",
                "Unlinked",
                hced_candidate_id="hced-exact-1",
            )

    def test_dataset_audit_rejects_missing_or_duplicate_candidate_bindings(self) -> None:
        base = _rating_event(with_location=False).to_dict()
        first = Event.from_dict(
            {**base, "id": "event-1", "hced_candidate_id": "hced-shared-1"}
        )
        second = Event.from_dict(
            {**base, "id": "event-2", "hced_candidate_id": "hced-shared-1"}
        )
        located_base = _rating_event(with_location=True).to_dict()
        located_first = Event.from_dict(
            {
                **located_base,
                "id": "located-1",
                "hced_candidate_id": "hced-located-1",
            }
        )
        located_second = Event.from_dict(
            {
                **located_base,
                "id": "located-2",
                "hced_candidate_id": "hced-located-2",
            }
        )
        unbound = Event.from_dict({**base, "id": "event-unbound"})
        object.__setattr__(unbound, "outcome_source_ids", ("hced_dataset",))
        object.__setattr__(unbound, "outcome_source_family_ids", ("hced",))
        entities = [
            Entity("a", "A", "state", 1800, source_ids=("hced_dataset",)),
            Entity("b", "B", "state", 1800, source_ids=("hced_dataset",)),
        ]
        source = Source("hced_dataset", "HCED", "https://example.test/hced")
        codes = {
            issue.code
            for issue in audit_dataset(
                entities,
                [first, second, located_first, located_second, unbound],
                {source.id: source},
                ModelConfig(),
            )
        }
        self.assertIn("duplicate_hced_candidate_binding", codes)
        self.assertIn("duplicate_location_provenance_binding", codes)
        self.assertIn("hced_outcome_without_candidate_binding", codes)

    def test_closed_provenance_round_trips_through_both_event_models(self) -> None:
        event = _rating_event(with_location=True)
        self.assertEqual(Event.from_dict(event.to_dict()), event)
        self.assertEqual(
            json.loads(json.dumps(event.to_dict()))["location_provenance"],
            PROVENANCE,
        )

        canonical = CanonicalEvent.from_dict(
            {
                "id": "event-1",
                "name": "Event",
                "source_ids": ["hced_dataset"],
                "hced_candidate_id": "hced-Exact Source Record1900-1",
                "modern_location_country": "Source jurisdiction label",
                "geometry": {"type": "Point", "coordinates": [-45.25, 12.5]},
                "location_provenance": PROVENANCE,
            }
        )
        self.assertEqual(CanonicalEvent.from_dict(canonical.to_dict()), canonical)

    def test_provenance_rejects_unknown_missing_or_noncanonical_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown field"):
            LocationProvenance.from_dict({**PROVENANCE, "reason": "quarantined"})
        for field_name in PROVENANCE:
            with self.subTest(missing=field_name), self.assertRaises(ValueError):
                LocationProvenance.from_dict(
                    {key: value for key, value in PROVENANCE.items() if key != field_name}
                )
        for field_name, bad_value in (
            ("source_id", "other"),
            ("assertion_status", "verified"),
            ("coordinate_precision", "decimal_digits"),
        ):
            with self.subTest(field=field_name), self.assertRaises(ValueError):
                LocationProvenance.from_dict({**PROVENANCE, field_name: bad_value})

    def test_engine_export_adds_only_metadata_and_leaves_numerics_identical(self) -> None:
        entities = [
            Entity("a", "A", "state", 1800, source_ids=("hced_dataset",)),
            Entity("b", "B", "state", 1800, source_ids=("hced_dataset",)),
        ]
        plain_engine = EloEngine().run(entities, [_rating_event(with_location=False)])
        located_engine = EloEngine().run(entities, [_rating_event(with_location=True)])
        self.assertEqual(plain_engine.leaderboard(), located_engine.leaderboard())
        self.assertEqual(plain_engine.history, located_engine.history)

        source = Source("hced_dataset", "HCED", "https://example.test/hced")
        exported = located_engine.export({source.id: source})["events"][0]
        self.assertEqual(
            {
                key: exported[key]
                for key in (
                    "hced_candidate_id",
                    "modern_location_country",
                    "geometry",
                    "location_provenance",
                )
            },
            {
                "hced_candidate_id": "hced-Exact Source Record1900-1",
                "modern_location_country": "Source jurisdiction label",
                "geometry": {"type": "Point", "coordinates": [-45.25, 12.5]},
                "location_provenance": PROVENANCE,
            },
        )

    def test_coverage_separates_presence_unreviewed_and_verified(self) -> None:
        located = {
            "id": "located",
            "year": 1900,
            "end_year": 1900,
            "event_type": "engagement",
            "participants": [],
            "source_ids": ["hced_dataset"],
            "hced_candidate_id": "hced-located-1900-1",
            "modern_location_country": "Source jurisdiction label",
            "geometry": {"type": "Point", "coordinates": [0, 0]},
            "location_provenance": PROVENANCE,
        }
        status_unknown = {
            "id": "unknown-status",
            "year": 1901,
            "end_year": 1901,
            "event_type": "engagement",
            "participants": [],
            "geometry": {"type": "Point", "coordinates": [10, 20]},
        }
        locations = _field_completeness([located, status_unknown])["locations"]
        self.assertEqual(locations["coordinates_present"]["numerator"], 2)
        self.assertEqual(locations["event_location_present"]["numerator"], 2)
        self.assertEqual(
            locations["modern_location_country_present"]["numerator"], 1
        )
        self.assertEqual(locations["location_provenance_present"]["numerator"], 1)
        self.assertEqual(
            locations["unreviewed_source_assertion_present"]["numerator"], 1
        )
        self.assertEqual(
            locations["hced_unreviewed_point_assertion_present"]["numerator"],
            0,
        )
        self.assertEqual(
            locations[
                "hced_unreviewed_geographic_jurisdiction_label_present"
            ]["numerator"],
            1,
        )
        self.assertEqual(
            locations["hced_unreviewed_location_assertion_present"]["numerator"],
            1,
        )
        self.assertEqual(
            locations["verified_location_assertion_present"]["availability"],
            "not_available",
        )
        self.assertIsNone(
            locations["verified_location_assertion_present"]["numerator"]
        )

    def test_unrelated_location_or_missing_source_link_is_not_hced_coverage(self) -> None:
        unrelated = {
            "id": "unrelated",
            "participants": [],
            "location_name": "Elsewhere",
            "location_provenance": PROVENANCE,
        }
        missing_link = {
            "id": "missing-link",
            "participants": [],
            "source_ids": ["other_source"],
            "hced_candidate_id": "hced-missing-link-1",
            "modern_location_country": "Source label",
            "geometry": {"type": "Point", "coordinates": [1, 2]},
            "location_provenance": PROVENANCE,
        }
        locations = _field_completeness([unrelated, missing_link])["locations"]
        self.assertEqual(locations["event_location_present"]["numerator"], 2)
        self.assertEqual(locations["coordinates_present"]["numerator"], 1)
        for metric in (
            "modern_location_country_present",
            "hced_unreviewed_point_assertion_present",
            "hced_unreviewed_geographic_jurisdiction_label_present",
            "hced_unreviewed_location_assertion_present",
            "unreviewed_source_assertion_present",
            "location_provenance_contract_valid",
        ):
            with self.subTest(metric=metric):
                self.assertEqual(locations[metric]["numerator"], 0)

    def test_signed_zero_point_is_generic_presence_but_not_hced_assertion(self) -> None:
        for coordinates in (
            [0, 0],
            [-0.0, 0.0],
            [0.0, -0.0],
            [-0.0, -0.0],
        ):
            event = {
                "id": "zero",
                "participants": [],
                "source_ids": ["hced_dataset"],
                "hced_candidate_id": "hced-zero-1",
                "geometry": {"type": "Point", "coordinates": coordinates},
                "location_provenance": PROVENANCE,
            }
            locations = _field_completeness([event])["locations"]
            with self.subTest(coordinates=coordinates):
                self.assertEqual(locations["coordinates_present"]["numerator"], 1)
                self.assertEqual(locations["event_location_present"]["numerator"], 1)
                self.assertEqual(
                    locations["hced_unreviewed_point_assertion_present"][
                        "numerator"
                    ],
                    0,
                )
                self.assertEqual(
                    locations["hced_unreviewed_location_assertion_present"][
                        "numerator"
                    ],
                    0,
                )
                self.assertEqual(
                    locations["unreviewed_source_assertion_present"]["numerator"],
                    0,
                )


if __name__ == "__main__":
    unittest.main()
