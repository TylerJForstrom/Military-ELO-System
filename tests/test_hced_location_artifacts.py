import hashlib
import json
import copy
import shutil
import tempfile
import unittest
from pathlib import Path

from military_elo.coverage import (
    CoverageInputError,
    build_coverage_report,
    render_coverage_markdown,
)
from military_elo.build import _validate_hced_registry_coupling, build_results
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_EVENT_SHA256,
    HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256,
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_EXPECTED_CANDIDATE_BINDINGS,
    HCED_EXPECTED_COUNTRY_ASSERTIONS,
    HCED_EXPECTED_POINT_ASSERTIONS,
    HCED_EXPECTED_PROVENANCE_OBJECTS,
    HCED_LOCATION_QUARANTINE_POLICY_SHA256,
    HCED_LOCATION_WARNING,
    HCED_POINT_QUARANTINE_EVENT_SHA256,
    HCED_POINT_QUARANTINE_CANDIDATE_SHA256,
    HCED_POINT_QUARANTINE_IDS,
    HCED_SOURCE_BLANK_COUNTRY_IDS,
)
from military_elo.models import Event


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "data" / "release"
REGISTRY = ROOT / "data" / "catalog" / "registry.json"
RESULTS = ROOT / "web" / "data" / "results.json"
HCED_LOCATION_PROJECTION_SHA256 = (
    "a7372a2e17f73a4aa49325303be79c6bd415b24f9c3cecedaf5a7856b54e2835"
)


def _sorted_newline_hash(values: list[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(values))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class HcedLocationArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads((RELEASE / "events.json").read_text(encoding="utf-8"))
        cls.entities = json.loads(
            (RELEASE / "entities.json").read_text(encoding="utf-8")
        )
        cls.sources = json.loads(
            (RELEASE / "sources.json").read_text(encoding="utf-8")
        )
        cls.metadata = json.loads(
            (RELEASE / "metadata.json").read_text(encoding="utf-8")
        )
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.results = json.loads(RESULTS.read_text(encoding="utf-8"))
        cls.hced_events = [
            event
            for event in cls.events
            if event.get("outcome_source_family_ids") == ["hced"]
        ]
        cls.by_candidate = {
            event["hced_candidate_id"]: event for event in cls.hced_events
        }

    def test_exact_candidate_bijection_and_promotion_tranches(self) -> None:
        self.assertEqual(len(self.events), 4_406)
        self.assertEqual(len(self.hced_events), HCED_EXPECTED_CANDIDATE_BINDINGS)
        self.assertEqual(len(self.by_candidate), HCED_EXPECTED_CANDIDATE_BINDINGS)
        self.assertEqual(
            sum(event["id"].startswith("hced_hced_") for event in self.hced_events),
            1_824,
        )
        self.assertEqual(
            sum(event["id"].startswith("hced_label_") for event in self.hced_events),
            2_328,
        )
        for event in self.hced_events:
            with self.subTest(event_id=event["id"]):
                self.assertIsInstance(event["hced_candidate_id"], str)
                self.assertEqual(
                    event["hced_candidate_id"], event["hced_candidate_id"].strip()
                )
                self.assertIn("hced_dataset", event["source_ids"])

    def test_exact_quarantine_event_hashes_and_field_omission(self) -> None:
        point_event_ids = [
            event["id"]
            for event in self.hced_events
            if event["hced_candidate_id"] in HCED_POINT_QUARANTINE_IDS
        ]
        country_event_ids = [
            event["id"]
            for event in self.hced_events
            if event["hced_candidate_id"] in HCED_COUNTRY_QUARANTINE_IDS
        ]
        self.assertEqual(len(point_event_ids), 37)
        self.assertEqual(len(country_event_ids), 79)
        self.assertEqual(
            _sorted_newline_hash(point_event_ids),
            HCED_POINT_QUARANTINE_EVENT_SHA256,
        )
        self.assertEqual(
            _sorted_newline_hash(country_event_ids),
            HCED_COUNTRY_QUARANTINE_EVENT_SHA256,
        )

        missing_points = {
            event["hced_candidate_id"]
            for event in self.hced_events
            if "geometry" not in event
        }
        missing_countries = {
            event["hced_candidate_id"]
            for event in self.hced_events
            if "modern_location_country" not in event
        }
        self.assertEqual(missing_points, HCED_POINT_QUARANTINE_IDS)
        self.assertEqual(
            missing_countries,
            HCED_COUNTRY_QUARANTINE_IDS | HCED_SOURCE_BLANK_COUNTRY_IDS,
        )
        self.assertEqual(len(missing_points | missing_countries), 84)
        self.assertEqual(
            len(HCED_POINT_QUARANTINE_IDS & HCED_COUNTRY_QUARANTINE_IDS), 33
        )

    def test_final_counts_and_closed_unique_provenance(self) -> None:
        points = [event for event in self.events if "geometry" in event]
        countries = [
            event for event in self.events if "modern_location_country" in event
        ]
        provenance_events = [
            event for event in self.events if "location_provenance" in event
        ]
        self.assertEqual(len(points), HCED_EXPECTED_POINT_ASSERTIONS)
        self.assertEqual(len(countries), HCED_EXPECTED_COUNTRY_ASSERTIONS)
        self.assertEqual(len(provenance_events), HCED_EXPECTED_PROVENANCE_OBJECTS)
        self.assertFalse(any("location_name" in event for event in self.events))

        provenance_keys = set()
        expected_fields = {
            "source_id",
            "source_record_id",
            "assertion_status",
            "coordinate_precision",
        }
        for event in provenance_events:
            with self.subTest(event_id=event["id"]):
                provenance = event["location_provenance"]
                self.assertEqual(set(provenance), expected_fields)
                self.assertEqual(provenance["source_id"], "hced_dataset")
                self.assertEqual(
                    provenance["assertion_status"], "unreviewed_source_assertion"
                )
                self.assertEqual(provenance["coordinate_precision"], "unknown")
                self.assertEqual(
                    provenance["source_record_id"],
                    provenance["source_record_id"].strip(),
                )
                self.assertTrue(provenance["source_record_id"])
                self.assertIn("hced_dataset", event["source_ids"])
                self.assertTrue(
                    "geometry" in event or "modern_location_country" in event
                )
                provenance_keys.add(
                    (provenance["source_id"], provenance["source_record_id"])
                )
        self.assertEqual(len(provenance_keys), HCED_EXPECTED_PROVENANCE_OBJECTS)

    def test_full_candidate_bound_location_projection_digest(self) -> None:
        projection = []
        for event in sorted(
            (event for event in self.events if "hced_candidate_id" in event),
            key=lambda event: event["id"],
        ):
            projected = {
                "id": event["id"],
                "hced_candidate_id": event["hced_candidate_id"],
            }
            for field_name in (
                "geometry",
                "modern_location_country",
                "location_provenance",
            ):
                if field_name in event:
                    projected[field_name] = event[field_name]
            projection.append(projected)
        self.assertEqual(len(projection), HCED_EXPECTED_CANDIDATE_BINDINGS)
        self.assertEqual(
            _canonical_hash(projection),
            HCED_LOCATION_PROJECTION_SHA256,
        )

    def test_specific_quarantine_and_retention_controls(self) -> None:
        focchies = self.by_candidate["hced-Focchies1649-1"]
        self.assertNotIn("geometry", focchies)
        self.assertIn("modern_location_country", focchies)
        self.assertIn("location_provenance", focchies)

        amadiye = self.by_candidate["hced-Amadiye1973-1"]
        self.assertEqual(
            amadiye["geometry"],
            {"type": "Point", "coordinates": [35.807248, 32.90485]},
        )
        self.assertNotIn("modern_location_country", amadiye)
        self.assertIn("location_provenance", amadiye)

        for candidate_id in ("hced-Issus-333-1", "hced-Slaak1631-1"):
            event = self.by_candidate[candidate_id]
            self.assertNotIn("geometry", event)
            self.assertIn("modern_location_country", event)
            self.assertIn("location_provenance", event)

        sas = self.by_candidate["hced-Sas van Gent1644-1"]
        self.assertNotIn("geometry", sas)
        self.assertNotIn("modern_location_country", sas)
        self.assertNotIn("location_provenance", sas)

        saints = self.by_candidate["hced-Saints1782-1"]
        self.assertIn("geometry", saints)
        self.assertNotIn("modern_location_country", saints)
        self.assertIn("location_provenance", saints)

        yaunis = self.by_candidate["hced-Yaunis Khan1516-1"]
        self.assertEqual(yaunis["modern_location_country"], "West Bank and Gaza")
        self.assertIn("geometry", yaunis)
        self.assertIn("location_provenance", yaunis)

        duplicate_coordinate_controls = [
            self.by_candidate[f"hced-St Lucia{year}-1"]
            for year in (1778, 1780, 1794, 1796, 1803)
        ]
        self.assertEqual(
            {json.dumps(event["geometry"], sort_keys=True) for event in duplicate_coordinate_controls},
            {
                json.dumps(
                    {
                        "type": "Point",
                        "coordinates": [-60.9580922, 13.7203536],
                    },
                    sort_keys=True,
                )
            },
        )
        self.assertTrue(
            all("modern_location_country" not in event for event in duplicate_coordinate_controls)
        )

    def test_release_dashboard_location_and_global_warning_parity(self) -> None:
        dashboard_by_id = {event["id"]: event for event in self.results["events"]}
        self.assertEqual(set(dashboard_by_id), {event["id"] for event in self.events})
        for release_event in self.events:
            dashboard_event = dashboard_by_id[release_event["id"]]
            with self.subTest(event_id=release_event["id"]):
                for field_name in (
                    "hced_candidate_id",
                    "modern_location_country",
                    "geometry",
                    "location_provenance",
                ):
                    self.assertEqual(
                        dashboard_event.get(field_name), release_event.get(field_name)
                    )
        self.assertIn(HCED_LOCATION_WARNING, self.metadata["coverage_warnings"])
        self.assertIn(HCED_LOCATION_WARNING, self.results["meta"]["coverage_warnings"])

    def test_dashboard_rebuild_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = []
            audits = []
            for pass_number in (1, 2):
                output = root / f"results-{pass_number}.json"
                audit = root / f"audit-{pass_number}.json"
                build_results(
                    RELEASE,
                    output,
                    config_path=ROOT / "config" / "model.default.json",
                    registry_path=REGISTRY,
                    audit_path=audit,
                    simulations=3,
                )
                outputs.append(output.read_bytes())
                audits.append(audit.read_bytes())
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(audits[0], audits[1])
            self.assertEqual(json.loads(audits[0]), [])

    def test_dashboard_build_rejects_release_registry_location_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            release = root / "release"
            release.mkdir()
            for filename in (
                "entities.json",
                "events.json",
                "metadata.json",
                "sources.json",
            ):
                shutil.copy2(RELEASE / filename, release / filename)
            events = json.loads((release / "events.json").read_text(encoding="utf-8"))
            mutated = next(
                event
                for event in events
                if "geometry" in event and "modern_location_country" in event
            )
            mutated.pop("geometry")
            (release / "events.json").write_text(
                json.dumps(events, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            registry = root / "registry.json"
            shutil.copy2(REGISTRY, registry)
            output = root / "results.json"
            audit = root / "audit.json"
            with self.assertRaisesRegex(ValueError, "HCED registry coupling"):
                build_results(
                    release,
                    output,
                    registry_path=registry,
                    audit_path=audit,
                    simulations=0,
                )
            self.assertFalse(output.exists())
            self.assertEqual(json.loads(audit.read_text(encoding="utf-8")), [])

    def test_coupling_rejects_balanced_quarantine_field_swaps(self) -> None:
        baseline_counts = {
            field_name: sum(field_name in event for event in self.events)
            for field_name in (
                "geometry",
                "modern_location_country",
                "location_provenance",
            )
        }
        cases = (
            (
                "point_to_focchies",
                ("geometry",),
                "hced-Focchies1649-1",
                "geometry presence inconsistent",
            ),
            (
                "country_to_country_quarantine",
                ("modern_location_country",),
                "hced-Atlantic1915-1917-1",
                "country/jurisdiction presence inconsistent",
            ),
            (
                "country_to_source_blank_amadiye",
                ("modern_location_country",),
                "hced-Amadiye1973-1",
                "country/jurisdiction presence inconsistent",
            ),
            (
                "all_location_fields_to_fully_quarantined",
                (
                    "geometry",
                    "modern_location_country",
                    "location_provenance",
                ),
                "hced-Aleutians1942-1",
                "provenance presence inconsistent",
            ),
        )
        for case_name, fields, target_candidate_id, expected_message in cases:
            with self.subTest(case=case_name):
                events = copy.deepcopy(self.events)
                target = next(
                    event
                    for event in events
                    if event.get("hced_candidate_id") == target_candidate_id
                )
                source = next(
                    event
                    for event in events
                    if event.get("hced_candidate_id") is not None
                    and event.get("hced_candidate_id") != target_candidate_id
                    and all(field_name in event for field_name in fields)
                    and (
                        fields != ("geometry",)
                        or event.get("hced_candidate_id")
                        not in HCED_POINT_QUARANTINE_IDS
                    )
                )
                for field_name in fields:
                    self.assertNotIn(field_name, target)
                    target[field_name] = source.pop(field_name)
                self.assertEqual(
                    {
                        field_name: sum(field_name in event for event in events)
                        for field_name in baseline_counts
                    },
                    baseline_counts,
                )
                parsed_events = [Event.from_dict(target)] + [
                    Event.from_dict(event)
                    for event in events
                    if event["id"] != target["id"]
                ]
                with self.assertRaises(ValueError) as raised:
                    _validate_hced_registry_coupling(
                        parsed_events,
                        self.registry,
                        self.metadata,
                    )
                self.assertIn(
                    f"HCED registry coupling: event {target['id']} has "
                    + expected_message,
                    str(raised.exception),
                )

    def test_dashboard_build_rejects_missing_or_stale_coupling_declarations(self) -> None:
        cases = (
            "missing_declaration",
            "stale_policy_count",
            "stale_policy_hash",
            "stale_assertion_status",
            "verified_claim",
            "verified_count",
            "verified_blank_reason",
            "missing_warning",
        )
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                release = root / "release"
                release.mkdir()
                for filename in (
                    "entities.json",
                    "events.json",
                    "metadata.json",
                    "sources.json",
                ):
                    shutil.copy2(RELEASE / filename, release / filename)
                registry_document = json.loads(REGISTRY.read_text(encoding="utf-8"))
                declaration = registry_document["coverage"][
                    "hced_location_assertions"
                ]
                if case == "missing_declaration":
                    registry_document["coverage"].pop("hced_location_assertions")
                elif case == "stale_policy_count":
                    declaration["point_fields_withheld_by_quarantine"] = 33
                elif case == "stale_policy_hash":
                    declaration["point_quarantine_candidate_manifest_sha256"] = "0" * 64
                elif case == "stale_assertion_status":
                    declaration["assertion_status"] = {
                        "unreviewed_source_assertion": 3_979,
                    }
                elif case == "verified_claim":
                    declaration["verified_location_assertions"][
                        "availability"
                    ] = "available"
                elif case == "verified_count":
                    declaration["verified_location_assertions"]["count"] = 999
                elif case == "verified_blank_reason":
                    declaration["verified_location_assertions"]["reason"] = " "
                else:
                    metadata_path = release / "metadata.json"
                    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                    metadata["coverage_warnings"].remove(HCED_LOCATION_WARNING)
                    metadata_path.write_text(
                        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                    )
                registry = root / "registry.json"
                registry.write_text(
                    json.dumps(registry_document, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "HCED registry coupling"):
                    build_results(
                        release,
                        root / "results.json",
                        registry_path=registry,
                        audit_path=root / "audit.json",
                        simulations=0,
                    )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            release = root / "release"
            shutil.copytree(RELEASE, release)
            with self.assertRaisesRegex(ValueError, "a registry is required"):
                build_results(
                    release,
                    root / "results.json",
                    audit_path=root / "audit.json",
                    simulations=0,
                )

    def test_status_aware_coverage_has_final_counts(self) -> None:
        report = build_coverage_report(
            RELEASE,
            registry_path=REGISTRY,
            results_path=RESULTS,
        )
        locations = report["field_completeness"]["locations"]
        self.assertEqual(
            locations["coordinates_present"]["numerator"],
            HCED_EXPECTED_POINT_ASSERTIONS,
        )
        self.assertEqual(
            locations["event_location_present"]["numerator"],
            HCED_EXPECTED_PROVENANCE_OBJECTS,
        )
        self.assertEqual(
            locations["hced_unreviewed_point_assertion_present"]["numerator"],
            HCED_EXPECTED_POINT_ASSERTIONS,
        )
        self.assertEqual(
            locations[
                "hced_unreviewed_geographic_jurisdiction_label_present"
            ]["numerator"],
            HCED_EXPECTED_COUNTRY_ASSERTIONS,
        )
        self.assertEqual(
            locations["hced_unreviewed_location_assertion_present"]["numerator"],
            HCED_EXPECTED_PROVENANCE_OBJECTS,
        )
        self.assertEqual(
            locations["verified_location_assertion_present"]["availability"],
            "not_available",
        )
        self.assertIsNone(
            locations["verified_location_assertion_present"]["numerator"]
        )
        expected_policy = {
            "point_fields_withheld_by_quarantine": 37,
            "country_or_jurisdiction_fields_withheld_by_quarantine": 79,
            "source_blank_country_fields": 1,
            "point_country_quarantine_overlap": 33,
            "unique_events_with_any_quarantined_field": 83,
            "point_quarantine_candidate_manifest_sha256": (
                HCED_POINT_QUARANTINE_CANDIDATE_SHA256
            ),
            "country_quarantine_candidate_manifest_sha256": (
                HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256
            ),
            "quarantine_policy_sha256": HCED_LOCATION_QUARANTINE_POLICY_SHA256,
        }
        registry_policy = self.registry["coverage"]["hced_location_assertions"]
        results_policy = self.results["registry"]["coverage"][
            "hced_location_assertions"
        ]
        for field_name, expected in expected_policy.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(registry_policy[field_name], expected)
                self.assertEqual(results_policy[field_name], expected)
                self.assertEqual(report["hced_location_policy"][field_name], expected)
        self.assertEqual(
            report["hced_location_policy"]["verified_location_assertions"][
                "availability"
            ],
            "not_available",
        )
        markdown = render_coverage_markdown(report)
        self.assertIn("Declared HCED location quarantine policy", markdown)
        self.assertIn("point_fields_withheld_by_quarantine | 37", markdown)

    def test_coverage_rejects_contradictory_location_policy_declarations(self) -> None:
        cases = (
            "missing_declaration",
            "stale_policy_count",
            "stale_policy_hash",
            "stale_direct_count",
            "missing_direct_count",
            "stale_assertion_status",
            "verified_nonnull_count",
            "verified_blank_reason",
        )
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                registry_document = json.loads(REGISTRY.read_text(encoding="utf-8"))
                declaration = registry_document["coverage"][
                    "hced_location_assertions"
                ]
                if case == "missing_declaration":
                    registry_document["coverage"].pop("hced_location_assertions")
                elif case == "stale_policy_count":
                    declaration["point_fields_withheld_by_quarantine"] = 33
                elif case == "stale_policy_hash":
                    declaration["point_quarantine_candidate_manifest_sha256"] = "0" * 64
                elif case == "stale_direct_count":
                    declaration["geojson_points"] = 3_977
                elif case == "missing_direct_count":
                    declaration.pop("geojson_points")
                elif case == "stale_assertion_status":
                    declaration["assertion_status"] = {
                        "unreviewed_source_assertion": 3_979,
                    }
                elif case == "verified_nonnull_count":
                    declaration["verified_location_assertions"]["count"] = 999
                else:
                    declaration["verified_location_assertions"]["reason"] = " "
                registry = Path(temporary) / "registry.json"
                registry.write_text(
                    json.dumps(registry_document, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaises(CoverageInputError):
                    build_coverage_report(
                        RELEASE,
                        registry_path=registry,
                        results_path=RESULTS,
                    )


class Wave5CoupledArtifactOracleTests(unittest.TestCase):
    """Pin the rebuilt release/registry/dashboard boundary as one artifact set.

    Wave 5 adds reviewed tactical and strategic cohorts, so release, registry,
    and dashboard projections are pinned as one coupled artifact boundary.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads((RELEASE / "events.json").read_text(encoding="utf-8"))
        cls.entities = json.loads(
            (RELEASE / "entities.json").read_text(encoding="utf-8")
        )
        cls.sources = json.loads(
            (RELEASE / "sources.json").read_text(encoding="utf-8")
        )
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.results = json.loads(RESULTS.read_text(encoding="utf-8"))

    def test_release_projection_matches_the_coupled_wave5_build(self) -> None:
        projected_events = []
        for event in self.events:
            projected = {
                key: value
                for key, value in event.items()
                if key
                not in {
                    "modern_location_country",
                    "geometry",
                    "location_provenance",
                }
            }
            if event["id"].startswith("hced_hced_"):
                projected.pop("hced_candidate_id", None)
            projected_events.append(projected)
        self.assertEqual(
            _canonical_hash(projected_events),
            "d1c2a3b5c6a7fe4530d3e16eb186603b04c1a218feb426ab4e147dbad2ad6d95",
        )
        self.assertEqual(
            _canonical_hash(self.entities),
            "659887653b1a9644fcc70a233125c1376ffaf6de643c5ab56508e327ae299101",
        )
        self.assertEqual(
            _canonical_hash(self.sources),
            "206a7293c2c1de46ee591fe5b751bf403db5f9dfaec54c84cc067eff197fc41a",
        )
        self.assertEqual(
            _canonical_hash(self.registry["entities"]),
            "7b53c98866f335c0f4ea0f37ef514b95deb13ed8610fd6e6d4934a81945fffc3",
        )

    def test_dashboard_projection_matches_the_coupled_wave5_build(self) -> None:
        projected_events = [
            {
                key: value
                for key, value in event.items()
                if key
                not in {
                    "hced_candidate_id",
                    "modern_location_country",
                    "geometry",
                    "location_provenance",
                }
            }
            for event in self.results["events"]
        ]
        self.assertEqual(
            _canonical_hash(projected_events),
            "846ab2197992d144ca3e5a0318d7027acae188b94e3d6a51ca0df6c7a9f39cb7",
        )
        expected_hashes = {
            "entities": "e348f206ad3b960c35bf5f8132a759e776f025069db4c6f490a84d0690a5b2c9",
            "series": "b3306e56d48a5de1ac7c6cfcfc8433fa28b3ba73d05ac9a74d5d41425fe05011",
            "leaderboard": "eca7878d4e79a563c6897dbfca8c1a56cbd72cd92cb161e85313c6a190643957",
            "sensitivity": "741190ad1d419883377c271ea5aa312ea8fb09695182e8624779a2e5b01cedb0",
        }
        for field_name, expected_hash in expected_hashes.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    _canonical_hash(self.results[field_name]), expected_hash
                )


if __name__ == "__main__":
    unittest.main()
