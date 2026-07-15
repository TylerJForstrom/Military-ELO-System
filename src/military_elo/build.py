from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from .audit import audit_dataset, has_errors
from .canonical import hced_point_geometry_validation_error
from .config import ModelConfig
from .engine import EloEngine
from .models import Entity, Event, Source
from .promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256,
    HCED_EXPECTED_CANDIDATE_BINDINGS,
    HCED_EXPECTED_COUNTRY_ASSERTIONS,
    HCED_EXPECTED_POINT_ASSERTIONS,
    HCED_EXPECTED_PROVENANCE_OBJECTS,
    HCED_EXPECTED_QUARANTINE_OVERLAP,
    HCED_EXPECTED_QUARANTINE_UNION,
    HCED_LOCATION_WARNING,
    HCED_LOCATION_QUARANTINE_POLICY_SHA256,
    HCED_POINT_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_CANDIDATE_SHA256,
    HCED_SOURCE_BLANK_COUNTRY_IDS,
)
from .sensitivity import run_sensitivity


def load_records(data_dir: str | Path) -> tuple[list[Entity], list[Event], dict[str, Source], dict[str, Any]]:
    root = Path(data_dir)
    entity_raw = json.loads((root / "entities.json").read_text(encoding="utf-8"))
    event_raw = json.loads((root / "events.json").read_text(encoding="utf-8"))
    source_raw = json.loads((root / "sources.json").read_text(encoding="utf-8"))
    metadata_path = root / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    entities = [Entity.from_dict(item) for item in entity_raw]
    events = [Event.from_dict(item) for item in event_raw]
    sources = {item.id: item for item in (Source.from_dict(row) for row in source_raw)}
    return entities, events, sources, metadata


def _validate_hced_registry_coupling(
    events: list[Event],
    registry_document: dict[str, Any],
    metadata: dict[str, Any],
) -> None:
    hced_events = [event for event in events if event.hced_candidate_id is not None]
    if not hced_events:
        return
    coverage = registry_document.get("coverage")
    if not isinstance(coverage, dict):
        raise ValueError(
            "HCED registry coupling: registry coverage is required for candidate-bound events"
        )
    declared = coverage.get("hced_location_assertions")
    if declared is None:
        raise ValueError(
            "HCED registry coupling: hced_location_assertions declaration is required"
        )
    if not isinstance(declared, dict):
        raise ValueError(
            "registry.coverage.hced_location_assertions must be an object"
        )

    coverage_warnings = metadata.get("coverage_warnings")
    if (
        not isinstance(coverage_warnings, list)
        or HCED_LOCATION_WARNING not in coverage_warnings
    ):
        raise ValueError(
            "HCED registry coupling: release metadata lacks the exact location warning"
        )
    candidate_ids: list[str] = []
    provenance_keys: set[tuple[str, str]] = set()
    point_count = 0
    country_count = 0
    provenance_count = 0
    for event in hced_events:
        candidate_id = event.hced_candidate_id
        if candidate_id is None:
            raise ValueError(
                f"HCED registry coupling: event {event.id} lacks a candidate binding"
            )
        candidate_ids.append(candidate_id)
        if "hced_dataset" not in event.source_ids:
            raise ValueError(
                f"HCED registry coupling: event {event.id} lacks hced_dataset linkage"
            )
        point_should_survive = candidate_id not in HCED_POINT_QUARANTINE_IDS
        country_should_survive = candidate_id not in (
            HCED_COUNTRY_QUARANTINE_IDS | HCED_SOURCE_BLANK_COUNTRY_IDS
        )
        location_should_survive = point_should_survive or country_should_survive
        if (event.location_provenance is not None) != location_should_survive:
            raise ValueError(
                "HCED registry coupling: event "
                f"{event.id} has provenance presence inconsistent with its "
                "publishable HCED location fields"
            )
        if (event.geometry is not None) != point_should_survive:
            raise ValueError(
                "HCED registry coupling: event "
                f"{event.id} has geometry presence inconsistent with the frozen "
                "candidate quarantine manifest"
            )
        if (event.modern_location_country is not None) != country_should_survive:
            raise ValueError(
                "HCED registry coupling: event "
                f"{event.id} has country/jurisdiction presence inconsistent with "
                "the frozen candidate quarantine and source-blank manifests"
            )
        if event.geometry is not None:
            geometry_error = hced_point_geometry_validation_error(event.geometry)
            if geometry_error is not None:
                raise ValueError(
                    f"HCED registry coupling: event {event.id}: {geometry_error}"
                )
            longitude, latitude = event.geometry["coordinates"]
            if longitude == 0 and latitude == 0:
                raise ValueError(
                    f"HCED registry coupling: event {event.id} publishes the (0,0) sentinel"
                )
            point_count += 1
        if event.modern_location_country is not None:
            country_count += 1
        if event.location_provenance is not None:
            provenance_key = (
                event.location_provenance.source_id,
                event.location_provenance.source_record_id,
            )
            if provenance_key in provenance_keys:
                raise ValueError(
                    "HCED registry coupling: duplicate location provenance key"
                )
            provenance_keys.add(provenance_key)
            provenance_count += 1

    measured = {
        "hced_candidate_bindings": len(candidate_ids),
        "geojson_points": point_count,
        "modern_location_country_assertions": country_count,
        "location_provenance_objects": provenance_count,
    }
    expected = {
        "hced_candidate_bindings": HCED_EXPECTED_CANDIDATE_BINDINGS,
        "geojson_points": HCED_EXPECTED_POINT_ASSERTIONS,
        "modern_location_country_assertions": HCED_EXPECTED_COUNTRY_ASSERTIONS,
        "location_provenance_objects": HCED_EXPECTED_PROVENANCE_OBJECTS,
        "point_fields_withheld_by_quarantine": len(HCED_POINT_QUARANTINE_IDS),
        "country_or_jurisdiction_fields_withheld_by_quarantine": len(
            HCED_COUNTRY_QUARANTINE_IDS
        ),
        "source_blank_country_fields": len(HCED_SOURCE_BLANK_COUNTRY_IDS),
        "point_country_quarantine_overlap": HCED_EXPECTED_QUARANTINE_OVERLAP,
        "unique_events_with_any_quarantined_field": HCED_EXPECTED_QUARANTINE_UNION,
        "point_quarantine_candidate_manifest_sha256": (
            HCED_POINT_QUARANTINE_CANDIDATE_SHA256
        ),
        "country_quarantine_candidate_manifest_sha256": (
            HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256
        ),
        "quarantine_policy_sha256": HCED_LOCATION_QUARANTINE_POLICY_SHA256,
    }
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("HCED registry coupling: candidate bindings are not unique")
    for field_name, expected_value in expected.items():
        declared_value = declared.get(field_name)
        if declared_value != expected_value:
            raise ValueError(
                "HCED registry coupling: declared "
                f"{field_name} {declared_value!r} != final pin {expected_value}"
            )
        if field_name in measured and measured[field_name] != declared_value:
            raise ValueError(
                "HCED registry coupling: measured "
                f"{field_name} {measured[field_name]} != declared {declared_value}"
            )
    expected_assertion_status = {
        "unreviewed_source_assertion": HCED_EXPECTED_PROVENANCE_OBJECTS,
    }
    if declared.get("assertion_status") != expected_assertion_status:
        raise ValueError(
            "HCED registry coupling: declared assertion_status must equal "
            f"{expected_assertion_status!r}"
        )
    verified = declared.get("verified_location_assertions")
    verified_reason = verified.get("reason") if isinstance(verified, dict) else None
    if (
        not isinstance(verified, dict)
        or set(verified) != {"availability", "count", "reason"}
        or verified.get("availability") != "not_available"
        or verified.get("count") is not None
        or not isinstance(verified_reason, str)
        or not verified_reason.strip()
        or verified_reason != verified_reason.strip()
    ):
        raise ValueError(
            "HCED registry coupling: verified-location coverage must be "
            "not_available with null count and a nonblank exact reason"
        )


def build_results(
    data_dir: str | Path,
    output_path: str | Path,
    config_path: str | Path | None = None,
    audit_path: str | Path | None = None,
    simulations: int = 0,
    registry_path: str | Path | None = None,
) -> dict[str, object]:
    entities, events, sources, metadata = load_records(data_dir)
    config = ModelConfig.from_file(config_path) if config_path else ModelConfig()
    issues = audit_dataset(entities, events, sources, config)
    if audit_path:
        destination = Path(audit_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps([issue.as_dict() for issue in issues], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if has_errors(issues):
        messages = "\n".join(f"{issue.code}: {issue.record_id}: {issue.message}" for issue in issues if issue.severity == "error")
        raise ValueError(f"Dataset audit failed:\n{messages}")

    registry_document: dict[str, Any] | None = None
    if registry_path:
        registry_raw = json.loads(Path(registry_path).read_text(encoding="utf-8"))
        if not isinstance(registry_raw, dict):
            raise ValueError("Registry document must be a JSON object")
        registry_document = registry_raw
        _validate_hced_registry_coupling(events, registry_document, metadata)
    elif any(event.hced_candidate_id is not None for event in events):
        raise ValueError(
            "HCED registry coupling: a registry is required for candidate-bound events"
        )

    engine = EloEngine(config).run(entities, events)
    source_coverage = metadata.get("coverage", {})
    if not isinstance(source_coverage, dict):
        source_coverage = {}
    metadata = {
        **metadata,
        "generated": date.today().isoformat(),
        "model_version": "0.2.0",
        "baseline": config.baseline,
        "rated_events": len(engine.event_updates),
        "entities": len(entities),
        "audit_warnings": sum(issue.severity == "warning" for issue in issues),
        "simulations": simulations,
        "coverage": {
            **source_coverage,
            "event_types": dict(Counter(event.event_type for event in events if event.status == "complete")),
            "war_types": dict(Counter(event.war_type for event in events if event.status == "complete")),
            "domains": dict(Counter(event.domain for event in events if event.status == "complete")),
            "confidence": {
                "high_0.80_to_1.00": sum(event.confidence >= 0.80 for event in events if event.status == "complete"),
                "medium_0.55_to_0.79": sum(0.55 <= event.confidence < 0.80 for event in events if event.status == "complete"),
                "low_below_0.55": sum(event.confidence < 0.55 for event in events if event.status == "complete"),
            },
            "by_century": dict(
                sorted(
                    Counter(
                        (event.end_year // 100) * 100
                        for event in events
                        if event.status == "complete"
                    ).items()
                )
            ),
        },
    }
    results = engine.export(sources, metadata)
    if registry_document is not None:
        results["registry"] = registry_document
    sensitivity = run_sensitivity(entities, events, config, simulations=simulations)
    if sensitivity:
        results["sensitivity"] = sensitivity
        for row in results["leaderboard"]:  # type: ignore[index]
            row["sensitivity"] = sensitivity.get(row["entity_id"], {})
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return results
