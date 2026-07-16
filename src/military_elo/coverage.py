from __future__ import annotations

import json
import math
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Mapping

from .canonical import (
    geometry_validation_error,
    hced_point_geometry_validation_error,
)
from .models import OPERATIONAL_DIMENSIONS, STRATEGIC_DIMENSIONS, TACTICAL_DIMENSIONS
from .promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256,
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_EXPECTED_CANDIDATE_BINDINGS,
    HCED_EXPECTED_CANDIDATE_KEYED_REVIEWED_CONTRACTS,
    HCED_EXPECTED_COUNTRY_ASSERTIONS,
    HCED_EXPECTED_POINT_ASSERTIONS,
    HCED_EXPECTED_PROVENANCE_OBJECTS,
    HCED_EXPECTED_QUARANTINE_OVERLAP,
    HCED_EXPECTED_QUARANTINE_UNION,
    HCED_LOCATION_QUARANTINE_POLICY_SHA256,
    HCED_POINT_QUARANTINE_CANDIDATE_SHA256,
    HCED_POINT_QUARANTINE_IDS,
    HCED_SOURCE_BLANK_COUNTRY_IDS,
)


REPORT_SCHEMA_VERSION = "1.0"
UNKNOWN = "unknown"
UNCLASSIFIED = "unclassified"

# These are the two identity queues excluded by the release builder when it
# reports event-like candidates. Keeping the same definition avoids silently
# changing the published denominator in a downstream report.
IDENTITY_QUEUE_FILES = frozenset(
    {
        "cliopatria-entity-candidates.jsonl",
        "ucdp-actor-26.1-candidates.jsonl",
    }
)

# Numeric analysis periods deliberately avoid asserting one universal set of
# culturally meaningful historical era names.
ERA_BINS: tuple[tuple[str, int | None, int | None], ...] = (
    ("before_500_bce", None, -501),
    ("500_bce_to_499_ce", -500, 499),
    ("500_to_1499", 500, 1499),
    ("1500_to_1799", 1500, 1799),
    ("1800_to_1945", 1800, 1945),
    ("1946_and_later", 1946, None),
)

LAYER_BY_EVENT_TYPE = {
    "engagement": "tactical",
    "campaign": "operational",
    "war": "strategic",
}
EXPECTED_DIMENSIONS = {
    "tactical": tuple(sorted(TACTICAL_DIMENSIONS)),
    "operational": tuple(sorted(OPERATIONAL_DIMENSIONS)),
    "strategic": tuple(sorted(STRATEGIC_DIMENSIONS)),
}
OBJECTIVE_DIMENSION_BY_LAYER = {
    "tactical": "mission_objective",
    "operational": "campaign_objective",
    "strategic": "political_objectives",
}

# Only explicit queue timestamps are eligible for aging. Retrieval dates and
# source snapshot dates are intentionally absent: they do not establish when a
# candidate entered the unresolved review queue.
QUEUE_TIMESTAMP_FIELDS = (
    "queued_at",
    "staged_at",
)
UNRESOLVED_STATUS_VALUES = frozenset({"unresolved", "pending_resolution"})


class CoverageInputError(ValueError):
    """Raised when a coverage input exists but is structurally invalid."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CoverageInputError(f"Required coverage input is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CoverageInputError(f"Invalid JSON in {path}: {exc}") from exc


def _json_list(path: Path) -> list[dict[str, Any]]:
    value = _load_json(path)
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise CoverageInputError(f"Expected a JSON array of objects in {path}")
    return value


def _json_object(path: Path) -> dict[str, Any]:
    value = _load_json(path)
    if not isinstance(value, dict):
        raise CoverageInputError(f"Expected a JSON object in {path}")
    return value


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _as_nonnegative_int(value: Any) -> int | None:
    if _is_int(value) and value >= 0:
        return value
    return None


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _category(value: Any) -> str:
    if not _present(value):
        return UNKNOWN
    text = str(value).strip()
    lowered = text.casefold()
    if lowered in {"unknown", "none", "null", "n/a", "na"}:
        return UNKNOWN
    if lowered in {"unclassified", "not classified"}:
        return UNCLASSIFIED
    return text


def _counts(
    counter: Counter[str],
    *,
    include_unknown: bool = True,
    include_unclassified: bool = False,
) -> dict[str, int]:
    if include_unknown:
        counter.setdefault(UNKNOWN, 0)
    if include_unclassified:
        counter.setdefault(UNCLASSIFIED, 0)
    return {
        key: int(counter[key])
        for key in sorted(counter, key=lambda item: (item.casefold(), item))
    }


def _count_metric(
    count: int,
    *,
    unit: str,
    definition: str,
    source: str,
) -> dict[str, Any]:
    return {
        "availability": "available",
        "count": int(count),
        "definition": definition,
        "source": source,
        "unit": unit,
    }


def _unavailable_count(*, unit: str, definition: str, reason: str) -> dict[str, Any]:
    return {
        "availability": "not_available",
        "count": None,
        "definition": definition,
        "reason": reason,
        "source": None,
        "unit": unit,
    }


def _ratio(
    numerator: int,
    denominator: int,
    *,
    unit: str,
    definition: str,
) -> dict[str, Any]:
    if denominator < 0 or numerator < 0:
        raise ValueError("Coverage ratios cannot use negative counts")
    availability = "available" if denominator else "not_applicable"
    return {
        "availability": availability,
        "definition": definition,
        "denominator": int(denominator),
        "numerator": int(numerator),
        "unit": unit,
        "value": round(numerator / denominator, 6) if denominator else None,
    }


def _unavailable_ratio(*, unit: str, definition: str, reason: str) -> dict[str, Any]:
    return {
        "availability": "not_available",
        "definition": definition,
        "denominator": None,
        "numerator": None,
        "reason": reason,
        "unit": unit,
        "value": None,
    }


def _event_layer(event: Mapping[str, Any]) -> str:
    return LAYER_BY_EVENT_TYPE.get(
        str(event.get("event_type", "")).strip().casefold(), UNKNOWN
    )


def _rated_events(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        event
        for event in events
        if str(event.get("status", "complete")).strip().casefold() == "complete"
    ]


def _era_for_year(value: Any) -> str:
    if not _is_int(value):
        return UNKNOWN
    for label, low, high in ERA_BINS:
        if (low is None or value >= low) and (high is None or value <= high):
            return label
    return UNKNOWN


def _source_family_value(
    source: Mapping[str, Any],
) -> tuple[str | None, str | None, bool]:
    for key in ("source_family_id", "source_family", "family_id", "family"):
        if key not in source:
            continue
        value = source.get(key)
        if _present(value):
            family = _category(value)
            if family not in {UNKNOWN, UNCLASSIFIED}:
                return family, None, True
            return None, family, True
        return None, "missing", True
    return None, None, False


def _has_outcome_role(source: Mapping[str, Any]) -> bool:
    roles = source.get("evidence_roles")
    if isinstance(roles, (list, tuple, set)) and any(
        str(role).strip().casefold() == "outcome" for role in roles
    ):
        return True

    # Preserve the reporter's legacy explicit contracts for older artifacts.
    # Current Source records emit only canonical plural evidence_roles.
    if source.get("supports_outcome") is True or source.get("outcome_evidence") is True:
        return True
    values: list[Any] = []
    for key in ("evidence_role", "claim_type", "claim_types"):
        value = source.get(key)
        if isinstance(value, (list, tuple, set)):
            values.extend(value)
        elif value is not None:
            values.append(value)
    return any(
        str(value).strip().casefold() in {"outcome", "outcomes"} for value in values
    )


def _family_values(value: Any) -> tuple[set[str], Counter[str]]:
    if isinstance(value, str):
        candidates: Iterable[Any] = (value,)
    elif isinstance(value, (list, tuple, set)):
        candidates = value
    else:
        return set(), Counter({"missing": 1})
    result: set[str] = set()
    unusable: Counter[str] = Counter()
    saw_candidate = False
    for candidate in candidates:
        saw_candidate = True
        if isinstance(candidate, dict):
            family, unusable_value, _ = _source_family_value(candidate)
            if family:
                result.add(family)
            elif unusable_value:
                unusable[unusable_value] += 1
        elif _present(candidate):
            family = _category(candidate)
            if family not in {UNKNOWN, UNCLASSIFIED}:
                result.add(family)
            else:
                unusable[family] += 1
        else:
            unusable["missing"] += 1
    if not saw_candidate:
        unusable["missing"] += 1
    return result, unusable


def _explicit_outcome_families(
    event: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]]
) -> tuple[set[str], Counter[str], bool]:
    families: set[str] = set()
    unusable: Counter[str] = Counter()
    explicit_contract = False

    # An event-level outcome contract always wins. In particular, a malformed
    # or intentionally empty explicit contract must remain visible as unusable;
    # generic provenance links cannot silently fill it in.
    family_contract_present = False
    for key in ("outcome_source_family_ids", "outcome_source_families"):
        if key in event:
            family_contract_present = True
            explicit_contract = True
            values, unusable_values = _family_values(event.get(key))
            families.update(values)
            unusable.update(unusable_values)

    # Older event-level contracts that carry only outcome source IDs remain
    # readable. The canonical paired contract also declares family IDs, whose
    # exact agreement with the source-derived set is enforced by the audit.
    outcome_source_ids = event.get("outcome_source_ids")
    outcome_source_contract_present = "outcome_source_ids" in event
    if outcome_source_contract_present:
        explicit_contract = True
    if not family_contract_present and outcome_source_contract_present:
        if isinstance(outcome_source_ids, (list, tuple, set)) and outcome_source_ids:
            for source_id in outcome_source_ids:
                source = sources.get(str(source_id))
                if source:
                    family, unusable_value, _ = _source_family_value(source)
                    if family:
                        families.add(family)
                    else:
                        unusable[unusable_value or "missing"] += 1
                else:
                    unusable["missing_source"] += 1
        else:
            unusable["missing"] += 1

    if explicit_contract:
        return families, unusable, True

    # Generic source_ids are eligible only when source metadata explicitly
    # labels both its family and the canonical plural outcome-evidence role.
    # IDs, publishers, titles and URLs are never used to guess a family.
    source_ids = event.get("source_ids")
    if isinstance(source_ids, (list, tuple, set)):
        for source_id in source_ids:
            source = sources.get(str(source_id))
            if source and _has_outcome_role(source):
                explicit_contract = True
                family, unusable_value, _ = _source_family_value(source)
                if family:
                    families.add(family)
                else:
                    unusable[unusable_value or "missing"] += 1

    return families, unusable, explicit_contract


def _outcome_source_family_report(
    events: list[dict[str, Any]], sources: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    per_event: dict[str, int] = {}
    events_by_family: Counter[str] = Counter()
    family_count_distribution: Counter[str] = Counter()
    events_with_data = 0
    events_with_multiple = 0
    events_with_contract = 0
    events_with_unusable_mapping = 0
    unusable_mapping_categories: Counter[str] = Counter()

    for index, event in enumerate(events):
        event_id = str(event.get("id") or f"event_index_{index}")
        families, unusable, explicit_contract = _explicit_outcome_families(
            event, sources
        )
        events_with_contract += int(explicit_contract)
        if unusable:
            events_with_unusable_mapping += 1
            unusable_mapping_categories.update(unusable)
        if families:
            events_with_data += 1
            family_count_distribution[str(len(families))] += 1
            per_event[event_id] = len(families)
            if len(families) >= 2:
                events_with_multiple += 1
            for family in families:
                events_by_family[family] += 1

    definition = (
        "Distinct explicitly mapped outcome-evidence source families per rated event. "
        "Source IDs, URLs, titles, publishers and identity crosswalks are not treated as families."
    )
    if not events_with_data:
        if events_with_unusable_mapping:
            reason = (
                "Explicit outcome-family contracts are present, but none supplies a usable classified "
                "family identifier. Unknown, unclassified and missing mappings remain unavailable."
            )
        else:
            reason = (
                "No rated event supplies an explicit outcome-family list, an explicit outcome-source list "
                "backed by a family mapping, or a generic source link whose metadata declares both family "
                "and outcome role. Source ID counts are not a substitute."
            )
        return {
            "absent_explicit_mapping_event_count": len(events) - events_with_contract,
            "availability": "not_available",
            "definition": definition,
            "event_count": len(events),
            "events_by_family": {},
            "events_with_explicit_family_data": 0,
            "events_without_explicit_family_data": len(events),
            "events_with_explicit_contract": events_with_contract,
            "events_with_unusable_explicit_mapping": events_with_unusable_mapping,
            "explicit_mapping_coverage": _ratio(
                0,
                len(events),
                unit="proportion_of_rated_events",
                definition="Rated events with an explicit outcome-source-family mapping.",
            ),
            "family_count_distribution": {},
            "multiple_family_coverage": _unavailable_ratio(
                unit="proportion_of_explicitly_mapped_events",
                definition="Explicitly mapped rated events supported by at least two outcome-source families.",
                reason=reason,
            ),
            "per_event_counts": {},
            "reason": reason,
            "unmapped_event_count": len(events),
            "unusable_mapping_categories": _counts(
                unusable_mapping_categories, include_unknown=False
            ),
            "unit": "rated events",
        }

    availability = (
        "available" if events_with_data == len(events) else "partially_available"
    )
    return {
        "absent_explicit_mapping_event_count": len(events) - events_with_contract,
        "availability": availability,
        "definition": definition,
        "event_count": len(events),
        "events_by_family": _counts(events_by_family, include_unknown=False),
        "events_with_explicit_family_data": events_with_data,
        "events_without_explicit_family_data": len(events) - events_with_data,
        "events_with_explicit_contract": events_with_contract,
        "events_with_unusable_explicit_mapping": events_with_unusable_mapping,
        "explicit_mapping_coverage": _ratio(
            events_with_data,
            len(events),
            unit="proportion_of_rated_events",
            definition="Rated events with an explicit outcome-source-family mapping.",
        ),
        "family_count_distribution": {
            key: int(family_count_distribution[key])
            for key in sorted(family_count_distribution, key=lambda item: int(item))
        },
        "multiple_family_coverage": _ratio(
            events_with_multiple,
            events_with_data,
            unit="proportion_of_explicitly_mapped_events",
            definition="Explicitly mapped rated events supported by at least two outcome-source families.",
        ),
        "per_event_counts": {key: per_event[key] for key in sorted(per_event)},
        "reason": None,
        "unmapped_event_count": len(events) - events_with_data,
        "unusable_mapping_categories": _counts(
            unusable_mapping_categories, include_unknown=False
        ),
        "unit": "rated events",
    }


def _parse_reference_date(value: str | None, *, strict: bool) -> date | None:
    if value is None:
        return None
    text = value if strict else value.strip()
    try:
        if strict:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
                raise ValueError("not an exact ISO calendar date")
        elif not text:
            return None
        return date.fromisoformat(text if strict else text[:10])
    except (TypeError, ValueError) as exc:
        if strict:
            raise CoverageInputError(
                f"Invalid --as-of date: {value!r}; expected YYYY-MM-DD"
            ) from exc
        return None


def _parse_queue_timestamp(value: Any) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        if len(text) == 10:
            return date.fromisoformat(text)
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _is_unresolved_review_record(record: Mapping[str, Any]) -> bool:
    if record.get("unresolved") is True:
        return True
    value = record.get("resolution_status")
    return (
        isinstance(value, str) and value.strip().casefold() in UNRESOLVED_STATUS_VALUES
    )


def _age_bucket(days: int) -> str:
    if days < 0:
        return "future_timestamp"
    if days <= 30:
        return "0_to_30_days"
    if days <= 90:
        return "31_to_90_days"
    if days <= 180:
        return "91_to_180_days"
    if days <= 365:
        return "181_to_365_days"
    return "366_days_or_more"


def _scan_review(
    review_dir: Path | None, reference_date: date | None
) -> dict[str, Any]:
    empty = {
        "directory_supplied": False,
        "files_present": False,
        "queue_files_present": False,
        "counts_by_file": {},
        "event_like_count": None,
        "record_count": None,
        "status_counts": {},
        "aging": {
            "availability": "not_available",
            "age_buckets": {},
            "definition": "Age of explicitly unresolved event-like review candidates from an explicit queue timestamp to the declared reference date.",
            "reason": "No machine-local review queue was supplied.",
            "reference_date": reference_date.isoformat() if reference_date else None,
            "timestamp_coverage": _unavailable_ratio(
                unit="proportion_of_unresolved_candidates",
                definition="Explicitly unresolved review candidates carrying a parseable queue timestamp.",
                reason="No machine-local review queue was supplied.",
            ),
            "unit": "days",
        },
    }
    if review_dir is None:
        return empty
    if not review_dir.exists() or not review_dir.is_dir():
        raise CoverageInputError(f"Review input is not a directory: {review_dir}")

    paths = sorted(review_dir.glob("*.jsonl"), key=lambda path: path.name)
    if not paths:
        result = dict(empty)
        result.update(
            {
                "directory_supplied": True,
                "event_like_count": 0,
                "files_present": True,
                "record_count": 0,
            }
        )
        result["aging"] = {
            "availability": "not_applicable",
            "age_buckets": {},
            "definition": "Age of explicitly unresolved event-like review candidates from an explicit queue timestamp to the declared reference date.",
            "reason": "The supplied review directory contains no event-like queue rows.",
            "reference_date": reference_date.isoformat() if reference_date else None,
            "timestamp_coverage": _ratio(
                0,
                0,
                unit="proportion_of_unresolved_candidates",
                definition="Explicitly unresolved review candidates carrying a parseable queue timestamp.",
            ),
            "unit": "days",
        }
        return result

    counts_by_file: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    unresolved_count = 0
    explicit_timestamp_count = 0
    valid_ages: list[int] = []
    invalid_timestamp_count = 0
    missing_timestamp_count = 0
    timestamp_fields: Counter[str] = Counter()
    event_like_explicit_timestamp_count = 0

    for path in paths:
        is_event_like = path.name not in IDENTITY_QUEUE_FILES
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise CoverageInputError(
                        f"Invalid JSONL record in {path} at line {line_number}: {exc}"
                    ) from exc
                if not isinstance(record, dict):
                    raise CoverageInputError(
                        f"Expected an object in {path} at line {line_number}"
                    )
                counts_by_file[path.name] += 1
                status_counts[_category(record.get("review_status"))] += 1
                if is_event_like and any(
                    _present(record.get(field)) for field in QUEUE_TIMESTAMP_FIELDS
                ):
                    event_like_explicit_timestamp_count += 1
                if not is_event_like or not _is_unresolved_review_record(record):
                    continue
                unresolved_count += 1
                timestamp_field = next(
                    (
                        field
                        for field in QUEUE_TIMESTAMP_FIELDS
                        if _present(record.get(field))
                    ),
                    None,
                )
                if timestamp_field is None:
                    missing_timestamp_count += 1
                    continue
                explicit_timestamp_count += 1
                timestamp_fields[timestamp_field] += 1
                queued_date = _parse_queue_timestamp(record.get(timestamp_field))
                if queued_date is None:
                    invalid_timestamp_count += 1
                elif reference_date is not None:
                    valid_ages.append((reference_date - queued_date).days)

    record_count = sum(counts_by_file.values())
    event_like_count = sum(
        count
        for filename, count in counts_by_file.items()
        if filename not in IDENTITY_QUEUE_FILES
    )

    aging_definition = (
        "Age of explicitly unresolved event-like review candidates from an explicit queue "
        "timestamp to the declared reference date. Retrieval and source-snapshot dates are excluded."
    )
    if event_like_count == 0:
        aging = {
            "availability": "not_applicable",
            "age_buckets": {},
            "definition": aging_definition,
            "reason": "The supplied review directory contains no event-like queue rows.",
            "reference_date": reference_date.isoformat() if reference_date else None,
            "timestamp_coverage": _ratio(
                0,
                0,
                unit="proportion_of_unresolved_candidates",
                definition="Explicitly unresolved review candidates carrying a parseable queue timestamp.",
            ),
            "unit": "days",
        }
    elif unresolved_count == 0:
        timestamp_note = (
            " No event-like review record has an explicit queue timestamp."
            if event_like_explicit_timestamp_count == 0
            else " Queue timestamps exist on some records but cannot be linked to unresolved status."
        )
        reason = (
            "No review record carries an explicit row-level unresolved marker. The existing "
            "needs-review status also applies to mechanically promoted rows and is not reinterpreted."
            + timestamp_note
        )
        aging = {
            "availability": "not_available",
            "age_buckets": {},
            "definition": aging_definition,
            "reason": reason,
            "reference_date": reference_date.isoformat() if reference_date else None,
            "timestamp_coverage": _unavailable_ratio(
                unit="proportion_of_unresolved_candidates",
                definition="Explicitly unresolved review candidates carrying a parseable queue timestamp.",
                reason=reason,
            ),
            "unit": "days",
        }
    elif explicit_timestamp_count == 0:
        reason = "Unresolved review records have no explicit queue timestamp; aging is unavailable, not zero."
        aging = {
            "availability": "not_available",
            "age_buckets": {},
            "definition": aging_definition,
            "reason": reason,
            "reference_date": reference_date.isoformat() if reference_date else None,
            "timestamp_coverage": _ratio(
                0,
                unresolved_count,
                unit="proportion_of_unresolved_candidates",
                definition="Explicitly unresolved review candidates carrying a parseable queue timestamp.",
            ),
            "unit": "days",
        }
    elif reference_date is None:
        reason = "Queue timestamps exist, but no deterministic reference date was supplied or declared."
        aging = {
            "availability": "not_available",
            "age_buckets": {},
            "definition": aging_definition,
            "reason": reason,
            "reference_date": None,
            "timestamp_coverage": _ratio(
                explicit_timestamp_count - invalid_timestamp_count,
                unresolved_count,
                unit="proportion_of_unresolved_candidates",
                definition="Explicitly unresolved review candidates carrying a parseable queue timestamp.",
            ),
            "unit": "days",
        }
    elif not valid_ages:
        reason = "All explicit queue timestamps are invalid."
        aging = {
            "availability": "not_available",
            "age_buckets": {},
            "definition": aging_definition,
            "reason": reason,
            "reference_date": reference_date.isoformat(),
            "timestamp_coverage": _ratio(
                0,
                unresolved_count,
                unit="proportion_of_unresolved_candidates",
                definition="Explicitly unresolved review candidates carrying a parseable queue timestamp.",
            ),
            "unit": "days",
        }
    else:
        buckets = Counter(_age_bucket(days) for days in valid_ages)
        for label in (
            "0_to_30_days",
            "31_to_90_days",
            "91_to_180_days",
            "181_to_365_days",
            "366_days_or_more",
            "future_timestamp",
        ):
            buckets.setdefault(label, 0)
        unavailable_records = missing_timestamp_count + invalid_timestamp_count
        aging = {
            "availability": (
                "available" if unavailable_records == 0 else "partially_available"
            ),
            "age_buckets": {key: int(buckets[key]) for key in sorted(buckets)},
            "definition": aging_definition,
            "invalid_timestamp_count": invalid_timestamp_count,
            "maximum_age_days": max(valid_ages),
            "median_age_days": float(median(valid_ages)),
            "minimum_age_days": min(valid_ages),
            "missing_timestamp_count": missing_timestamp_count,
            "reason": None,
            "reference_date": reference_date.isoformat(),
            "timestamp_coverage": _ratio(
                len(valid_ages),
                unresolved_count,
                unit="proportion_of_unresolved_candidates",
                definition="Explicitly unresolved review candidates carrying a parseable queue timestamp.",
            ),
            "timestamp_fields_used": _counts(timestamp_fields),
            "unit": "days",
        }

    return {
        "aging": aging,
        "counts_by_file": {
            key: int(counts_by_file[key]) for key in sorted(counts_by_file)
        },
        "directory_supplied": True,
        "event_like_count": int(event_like_count),
        "files_present": True,
        "queue_files_present": True,
        "record_count": int(record_count),
        "status_counts": _counts(status_counts),
    }


def _coverage_metadata(
    metadata: Mapping[str, Any], registry: Mapping[str, Any] | None
) -> tuple[dict[str, Any], dict[str, int] | None, str | None]:
    registry_coverage = registry.get("coverage") if isinstance(registry, dict) else None
    if not isinstance(registry_coverage, dict):
        registry_coverage = {}
    promotion = metadata.get("promotion")
    if not isinstance(promotion, dict):
        promotion = {}

    queue_counts_source = None
    queue_counts_present = False
    if "source_queue_counts" in registry_coverage:
        queue_counts_raw = registry_coverage["source_queue_counts"]
        queue_counts_source = "registry.coverage.source_queue_counts"
        queue_counts_present = True
    elif "source_queue_counts" in promotion:
        queue_counts_raw = promotion["source_queue_counts"]
        queue_counts_source = "release.metadata.promotion.source_queue_counts"
        queue_counts_present = True
    else:
        queue_counts_raw = None
    if not queue_counts_present:
        return dict(registry_coverage), None, None
    queue_counts: dict[str, int] = {}
    if not isinstance(queue_counts_raw, dict):
        raise CoverageInputError(
            f"{queue_counts_source} must be an object of nonnegative integer counts"
        )
    for key, value in queue_counts_raw.items():
        count = _as_nonnegative_int(value)
        if count is None:
            raise CoverageInputError(
                f"{queue_counts_source}.{key} must be a nonnegative integer"
            )
        queue_counts[str(key)] = count
    return (
        dict(registry_coverage),
        {key: queue_counts[key] for key in sorted(queue_counts)},
        queue_counts_source,
    )


def _hced_location_policy_report(
    coverage_metadata: Mapping[str, Any],
    *,
    required: bool = False,
) -> dict[str, Any]:
    raw = coverage_metadata.get("hced_location_assertions")
    if raw is None:
        if required:
            raise CoverageInputError(
                "registry.coverage.hced_location_assertions is required for "
                "candidate-bound HCED events"
            )
        return {
            "availability": "not_available",
            "reason": "Registry coverage does not declare an HCED location policy.",
        }
    if not isinstance(raw, Mapping):
        raise CoverageInputError(
            "registry.coverage.hced_location_assertions must be an object"
        )
    expected_counts = {
        "hced_candidate_bindings": HCED_EXPECTED_CANDIDATE_BINDINGS,
        "candidate_keyed_reviewed_contracts": (
            HCED_EXPECTED_CANDIDATE_KEYED_REVIEWED_CONTRACTS
        ),
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
    }
    counts: dict[str, int] = {}
    for field_name, expected_count in expected_counts.items():
        count = _as_nonnegative_int(raw.get(field_name))
        if count != expected_count:
            raise CoverageInputError(
                "registry.coverage.hced_location_assertions."
                f"{field_name} must equal the final audited count {expected_count}"
            )
        counts[field_name] = count
    expected_hashes = {
        "point_quarantine_candidate_manifest_sha256": (
            HCED_POINT_QUARANTINE_CANDIDATE_SHA256
        ),
        "country_quarantine_candidate_manifest_sha256": (
            HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256
        ),
        "quarantine_policy_sha256": HCED_LOCATION_QUARANTINE_POLICY_SHA256,
    }
    hashes: dict[str, str] = {}
    for field_name, expected_hash in expected_hashes.items():
        value = raw.get(field_name)
        if value != expected_hash:
            raise CoverageInputError(
                "registry.coverage.hced_location_assertions."
                f"{field_name} must equal the final audited digest {expected_hash}"
            )
        hashes[field_name] = value
    assertion_status = raw.get("assertion_status")
    expected_assertion_status = {
        "unreviewed_source_assertion": HCED_EXPECTED_PROVENANCE_OBJECTS,
    }
    if assertion_status != expected_assertion_status:
        raise CoverageInputError(
            "registry.coverage.hced_location_assertions.assertion_status "
            f"must equal {expected_assertion_status!r}"
        )
    verified = raw.get("verified_location_assertions")
    verified_reason = verified.get("reason") if isinstance(verified, Mapping) else None
    if (
        not isinstance(verified, Mapping)
        or set(verified) != {"availability", "count", "reason"}
        or verified.get("availability") != "not_available"
        or verified.get("count") is not None
        or not isinstance(verified_reason, str)
        or not verified_reason.strip()
        or verified_reason != verified_reason.strip()
    ):
        raise CoverageInputError(
            "registry HCED verified-location coverage must be declared "
            "not_available with null count and a nonblank exact reason"
        )
    expected_fields = {
        *expected_counts,
        *expected_hashes,
        "assertion_status",
        "verified_location_assertions",
    }
    if set(raw) != expected_fields:
        raise CoverageInputError(
            "registry.coverage.hced_location_assertions must contain exactly "
            "the final audited policy fields"
        )
    return {
        "availability": "available",
        "definition": (
            "Declared frozen HCED quarantine-policy counts. These values come from "
            "the audited candidate-ID manifests and are not inferred from absent fields."
        ),
        **counts,
        **hashes,
        "assertion_status": dict(assertion_status),
        "verified_location_assertions": dict(verified),
    }


def _stage_funnel(
    events: list[dict[str, Any]],
    metadata: Mapping[str, Any],
    coverage: Mapping[str, Any],
    metadata_queue_counts: Mapping[str, int] | None,
    metadata_queue_counts_source: str | None,
    review_scan: Mapping[str, Any],
) -> dict[str, Any]:
    rated_count = len(events)
    raw_count = None
    raw_source = None
    for source_name, candidate in (
        ("registry.coverage.raw_source_records", coverage.get("raw_source_records")),
        ("release.metadata.raw_source_records", metadata.get("raw_source_records")),
        ("release.metadata.raw_record_count", metadata.get("raw_record_count")),
    ):
        parsed = _as_nonnegative_int(candidate)
        if parsed is not None:
            raw_count = parsed
            raw_source = source_name
            break

    if metadata_queue_counts is not None:
        staged_count = sum(metadata_queue_counts.values())
        event_like_count = sum(
            count
            for filename, count in metadata_queue_counts.items()
            if filename not in IDENTITY_QUEUE_FILES
        )
        staged_source = metadata_queue_counts_source or "declared source_queue_counts"
    elif review_scan.get("files_present"):
        staged_count = int(review_scan["record_count"])
        event_like_count = int(review_scan["event_like_count"])
        staged_source = "review JSONL files"
    else:
        staged_count = None
        event_like_count = None
        staged_source = None

    unresolved_count = _as_nonnegative_int(coverage.get("unresolved_event_candidates"))
    curated_seed_count = _as_nonnegative_int(coverage.get("curated_seed_events"))
    candidate_keyed_keys = tuple(
        sorted(
            key
            for key in coverage
            if key.startswith("candidate_keyed_") and key.endswith("_events")
        )
    )
    provisional_keys = (
        "provisional_hced_events",
        "provisional_hced_label_events",
        *candidate_keyed_keys,
        "provisional_iwd_wars",
        "provisional_iwbd_battles",
        "provisional_ucdp_events",
    )
    provisional_values = [
        _as_nonnegative_int(coverage.get(key)) for key in provisional_keys
    ]
    provisional_count = (
        sum(value for value in provisional_values if value is not None)
        if all(value is not None for value in provisional_values)
        else None
    )

    raw_metric = (
        _count_metric(
            raw_count,
            unit="source records",
            definition="Physical or logical raw source records before candidate staging, only when an input declares that count explicitly.",
            source=raw_source or "",
        )
        if raw_count is not None
        else _unavailable_count(
            unit="source records",
            definition="Physical or logical raw source records before candidate staging, only when an input declares that count explicitly.",
            reason="Raw snapshots are outside this report's input contract and no explicit raw-record count is declared.",
        )
    )
    staged_metric = (
        _count_metric(
            staged_count,
            unit="staged review records",
            definition="All staged source-candidate records, including identity and event-like queues.",
            source=staged_source or "",
        )
        if staged_count is not None
        else _unavailable_count(
            unit="staged review records",
            definition="All staged source-candidate records, including identity and event-like queues.",
            reason="Neither review JSONL files nor declared source-queue counts are available.",
        )
    )
    event_like_metric = (
        _count_metric(
            event_like_count,
            unit="event-like candidates",
            definition="Staged records excluding the declared Cliopatria polity and UCDP actor identity queues.",
            source=staged_source or "",
        )
        if event_like_count is not None
        else _unavailable_count(
            unit="event-like candidates",
            definition="Staged records excluding the declared Cliopatria polity and UCDP actor identity queues.",
            reason="No staged queue counts are available.",
        )
    )
    unresolved_metric = (
        _count_metric(
            unresolved_count,
            unit="event-like candidates",
            definition="Release-declared event-like candidates remaining outside the rating ledger after promotion-unit adjustments.",
            source="registry.coverage.unresolved_event_candidates",
        )
        if unresolved_count is not None
        else _unavailable_count(
            unit="event-like candidates",
            definition="Release-declared event-like candidates remaining outside the rating ledger after promotion-unit adjustments.",
            reason="No release-declared unresolved-event-candidate count is available; review status labels are not reinterpreted as a replacement model.",
        )
    )
    adjudicated_metric = _unavailable_count(
        unit="claim-adjudicated events",
        definition="Events with canonical records proving completion of claim-level human adjudication.",
        reason=(
            "The supported inputs contain no canonical claim-level adjudication records. Curated seed "
            "membership is reported separately and is not treated as proof of formal adjudication."
        ),
    )
    curated_seed_metric = (
        _count_metric(
            curated_seed_count,
            unit="curated seed events",
            definition="Foundation events explicitly counted as curated seed records; this is not a claim-level adjudication status.",
            source="registry.coverage.curated_seed_events",
        )
        if curated_seed_count is not None
        else _unavailable_count(
            unit="curated seed events",
            definition="Foundation events explicitly counted as curated seed records; this is not a claim-level adjudication status.",
            reason="The release does not declare a curated-seed event count.",
        )
    )
    provisional_metric = (
        _count_metric(
            provisional_count,
            unit="provisional rating events",
            definition="Rule-promoted source-derived events that enter ratings but remain pending claim-level human adjudication.",
            source="registry.coverage provisional tranche counts",
        )
        if provisional_count is not None
        else _unavailable_count(
            unit="provisional rating events",
            definition="Rule-promoted source-derived events that enter ratings but remain pending claim-level human adjudication.",
            reason="One or more release-declared provisional tranche counts are absent.",
        )
    )

    promotion = metadata.get("promotion")
    if not isinstance(promotion, dict):
        promotion = {}

    def declared_iwd_metric(
        declarations: tuple[tuple[str, Mapping[str, Any], str], ...],
        *,
        unit: str,
        definition: str,
    ) -> dict[str, Any]:
        for source, document, key in declarations:
            if key not in document:
                continue
            count = _as_nonnegative_int(document.get(key))
            if count is None:
                raise CoverageInputError(f"{source} must be a nonnegative integer")
            return _count_metric(
                count,
                unit=unit,
                definition=definition,
                source=source,
            )
        return _unavailable_count(
            unit=unit,
            definition=definition,
            reason="No supported input declares this IWD counter.",
        )

    iwd_components_aggregated = declared_iwd_metric(
        (
            (
                "registry.coverage.iwd_components_aggregated",
                coverage,
                "iwd_components_aggregated",
            ),
            (
                "release.metadata.promotion.iwd_components_aggregated",
                promotion,
                "iwd_components_aggregated",
            ),
        ),
        unit="IWD component records used in aggregation",
        definition=(
            "IWD component records whose usable evidence contributed to an aggregated "
            "rated parent-war event."
        ),
    )
    iwd_components_attached = declared_iwd_metric(
        (
            (
                "registry.coverage.iwd_components_attached_to_rated_parents",
                coverage,
                "iwd_components_attached_to_rated_parents",
            ),
            (
                "release.metadata.promotion.iwd_components_attached_to_rated_parents",
                promotion,
                "iwd_components_attached_to_rated_parents",
            ),
        ),
        unit="IWD component records attached to rated parent wars",
        definition=(
            "All IWD component records attached for provenance to accepted rated parent-war "
            "events, including attached records not used in the aggregate."
        ),
    )
    iwd_parent_wars_rated = declared_iwd_metric(
        (
            (
                "registry.coverage.provisional_iwd_wars",
                coverage,
                "provisional_iwd_wars",
            ),
            (
                "release.metadata.promotion.accepted_iwd_wars",
                promotion,
                "accepted_iwd_wars",
            ),
        ),
        unit="rated IWD parent-war events",
        definition=(
            "Accepted IWD parent wars represented as one event each in the provisional rating ledger."
        ),
    )
    reconciliation_metrics = (
        iwd_components_aggregated,
        iwd_components_attached,
        iwd_parent_wars_rated,
    )
    available_reconciliation_metrics = sum(
        metric["availability"] == "available" for metric in reconciliation_metrics
    )
    unit_reconciliation = {
        "availability": (
            "available"
            if available_reconciliation_metrics == len(reconciliation_metrics)
            else "partially_available"
            if available_reconciliation_metrics
            else "not_available"
        ),
        "definition": (
            "IWD aggregation, attachment, and rated-parent counts have different units and are "
            "reported independently; equality between any two is not assumed."
        ),
        "iwd_components_aggregated": iwd_components_aggregated,
        "iwd_components_attached_to_rated_parents": iwd_components_attached,
        "iwd_parent_wars_rated": iwd_parent_wars_rated,
    }

    return {
        "adjudicated": adjudicated_metric,
        "curated_seed": curated_seed_metric,
        "event_like": event_like_metric,
        "is_strictly_nested": False,
        "note": (
            "This is a stage scorecard, not a retention funnel: curated seed events need not originate "
            "in the staged queues, curated status is not formal claim adjudication, and provisional rated "
            "events are not equivalent to human adjudication."
        ),
        "rated": _count_metric(
            rated_count,
            unit="rating events",
            definition="Release ledger events whose status is complete (missing legacy status defaults to complete).",
            source="data/release/events.json",
        ),
        "rated_provisional": provisional_metric,
        "raw": raw_metric,
        "staged": staged_metric,
        "unit_reconciliation": unit_reconciliation,
        "unresolved": unresolved_metric,
    }


def _event_counts(
    events: list[dict[str, Any]],
    entity_rows: Iterable[Mapping[str, Any]],
    source_families: Mapping[str, Any],
) -> dict[str, Any]:
    entity_regions = {
        str(row.get("id")): _category(row.get("region"))
        for row in entity_rows
        if _present(row.get("id"))
    }
    by_era: Counter[str] = Counter()
    by_region: Counter[str] = Counter()
    by_participant_entity_region: Counter[str] = Counter()
    by_layer: Counter[str] = Counter()
    by_domain: Counter[str] = Counter()
    by_war_type: Counter[str] = Counter()
    by_date_precision: Counter[str] = Counter()
    by_event_type: Counter[str] = Counter()
    explicit_layer_count = 0
    layer_mismatch_ids: list[str] = []

    for index, event in enumerate(events):
        by_era[_era_for_year(event.get("end_year"))] += 1
        canonical_layer = _event_layer(event)
        by_layer[canonical_layer] += 1
        if _present(event.get("layer")):
            explicit_layer_count += 1
            explicit_layer = _category(event.get("layer")).casefold()
            if explicit_layer != canonical_layer:
                layer_mismatch_ids.append(
                    str(event.get("id") or f"event_index_{index}")
                )
        by_domain[_category(event.get("domain"))] += 1
        by_war_type[_category(event.get("war_type"))] += 1
        by_date_precision[_category(event.get("date_precision"))] += 1
        by_event_type[_category(event.get("event_type"))] += 1
        by_region[_category(event.get("region"))] += 1

        regions: set[str] = set()
        participants = event.get("participants")
        if isinstance(participants, list):
            for participant in participants:
                if not isinstance(participant, dict):
                    regions.add(UNKNOWN)
                    continue
                entity_id = participant.get("entity_id")
                if not _present(entity_id):
                    regions.add(UNKNOWN)
                else:
                    regions.add(entity_regions.get(str(entity_id), UNKNOWN))
        if not regions:
            regions.add(UNKNOWN)
        for region in regions:
            by_participant_entity_region[region] += 1

    for label, _, _ in ERA_BINS:
        by_era.setdefault(label, 0)
    by_era.setdefault(UNKNOWN, 0)
    for layer in (*sorted(set(LAYER_BY_EVENT_TYPE.values())), UNKNOWN):
        by_layer.setdefault(layer, 0)

    if source_families.get("availability") == "not_available":
        by_source_family: dict[str, Any] = {
            "availability": "not_available",
            "counts": {},
            "definition": source_families.get("definition"),
            "reason": source_families.get("reason"),
            "unmapped_event_count": source_families.get(
                "unmapped_event_count", len(events)
            ),
            "unit": "event-family incidences",
        }
    else:
        by_source_family = {
            "availability": source_families.get("availability"),
            "counts": dict(source_families.get("events_by_family", {})),
            "definition": (
                "Rated-event incidences by explicitly mapped outcome-source family; one event may "
                "appear under more than one family, so counts need not sum to the event total."
            ),
            "reason": None,
            "unmapped_event_count": source_families.get("unmapped_event_count", 0),
            "unit": "event-family incidences",
        }

    return {
        "by_date_precision": _counts(by_date_precision),
        "by_domain": _counts(by_domain),
        "by_era": _counts(by_era),
        "by_event_type": _counts(by_event_type),
        "by_layer": _counts(by_layer),
        "by_participant_entity_region": _counts(
            by_participant_entity_region, include_unclassified=True
        ),
        "by_region": _counts(by_region, include_unclassified=True),
        "by_source_family": by_source_family,
        "by_war_type": _counts(by_war_type),
        "era_definitions": [
            {"label": label, "start_year": low, "end_year": high}
            for label, low, high in ERA_BINS
        ],
        "era_assignment": (
            "Each event is assigned once from end_year, matching the project's existing coverage chronology; "
            "an event spanning an analysis-period boundary is not duplicated across bins."
        ),
        "participant_entity_region_definition": (
            "Distinct participant-entity regions represented in each event. This is not event geography; "
            "an event spanning regions is counted once in each, so counts may exceed total events."
        ),
        "region_definition": (
            "Explicit event-location region. Participant entity regions are not substituted when this field is absent."
        ),
        "explicit_layer_consistency": _ratio(
            explicit_layer_count - len(layer_mismatch_ids),
            explicit_layer_count,
            unit="proportion_of_events_with_explicit_layer",
            definition="Events whose optional explicit layer agrees with the canonical event_type-to-layer mapping.",
        ),
        "explicit_layer_field_count": explicit_layer_count,
        "explicit_layer_mismatch_count": len(layer_mismatch_ids),
        "explicit_layer_mismatch_event_ids": sorted(layer_mismatch_ids),
        "scope": "rated events",
        "total": len(events),
        "unit": "events",
    }


def _valid_coordinate(value: Any, low: float, high: float) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return low <= value <= high
    if isinstance(value, float):
        return math.isfinite(value) and low <= value <= high
    return False


def _geojson_positions(geometry: Mapping[str, Any]) -> list[Any]:
    geometry_type = geometry.get("type")
    if geometry_type == "GeometryCollection":
        positions: list[Any] = []
        for member in geometry["geometries"]:
            positions.extend(_geojson_positions(member))
        return positions

    coordinates = geometry["coordinates"]
    if geometry_type == "Point":
        return [coordinates]
    if geometry_type in {"MultiPoint", "LineString"}:
        return list(coordinates)
    if geometry_type == "MultiLineString":
        return [position for line in coordinates for position in line]
    if geometry_type == "Polygon":
        return [position for ring in coordinates for position in ring]
    return [
        position for polygon in coordinates for ring in polygon for position in ring
    ]


def _geojson_coverage(value: Any) -> tuple[bool, bool]:
    if geometry_validation_error(value) is not None:
        return False, False
    positions = _geojson_positions(value)
    has_in_range_position = any(
        (
            _valid_coordinate(position[0], -180, 180)
            and _valid_coordinate(position[1], -90, 90)
        )
        for position in positions
    )
    return True, has_in_range_position


def _has_location(event: Mapping[str, Any]) -> bool:
    for key in (
        "location_name",
        "place",
        "place_id",
        "modern_location_country",
        "country",
    ):
        if _present(event.get(key)):
            return True
    location = event.get("location")
    if isinstance(location, str) and _present(location):
        return True
    if isinstance(location, dict) and any(
        _present(location.get(key))
        for key in ("name", "label", "place", "place_id", "country", "region")
    ):
        return True
    locations = event.get("locations")
    if isinstance(locations, (list, tuple)):
        for item in locations:
            if isinstance(item, str) and _present(item):
                return True
            if isinstance(item, dict) and any(
                _present(item.get(key))
                for key in ("name", "label", "place", "place_id", "country", "region")
            ):
                return True
    geometry_valid, has_position = _geojson_coverage(event.get("geometry"))
    if geometry_valid and has_position:
        return True
    return _has_coordinates(event)


def _has_coordinates(event: Mapping[str, Any]) -> bool:
    if _valid_coordinate(event.get("latitude"), -90, 90) and _valid_coordinate(
        event.get("longitude"), -180, 180
    ):
        return True
    coordinates = event.get("coordinates")
    if isinstance(coordinates, (list, tuple)) and len(coordinates) >= 2:
        return _valid_coordinate(coordinates[0], -180, 180) and _valid_coordinate(
            coordinates[1], -90, 90
        )
    if isinstance(coordinates, dict):
        return _valid_coordinate(
            coordinates.get("latitude"), -90, 90
        ) and _valid_coordinate(coordinates.get("longitude"), -180, 180)
    location = event.get("location")
    if isinstance(location, dict):
        if _valid_coordinate(location.get("latitude"), -90, 90) and _valid_coordinate(
            location.get("longitude"), -180, 180
        ):
            return True
    geometry_valid, has_position = _geojson_coverage(event.get("geometry"))
    return geometry_valid and has_position


def _unreviewed_hced_location_flags(
    event: Mapping[str, Any],
) -> tuple[bool, bool, bool]:
    """Return strict ``(point, jurisdiction_label, any_location)`` flags."""

    provenance = event.get("location_provenance")
    if not isinstance(provenance, Mapping):
        return False, False, False
    if set(provenance) != {
        "source_id",
        "source_record_id",
        "assertion_status",
        "coordinate_precision",
    }:
        return False, False, False
    candidate_id = event.get("hced_candidate_id")
    source_ids = event.get("source_ids")
    source_record_id = provenance.get("source_record_id")
    valid_binding = (
        isinstance(candidate_id, str)
        and bool(candidate_id.strip())
        and candidate_id == candidate_id.strip()
        and isinstance(source_ids, (list, tuple))
        and "hced_dataset" in source_ids
        and provenance.get("source_id") == "hced_dataset"
        and isinstance(source_record_id, str)
        and bool(source_record_id.strip())
        and source_record_id == source_record_id.strip()
        and provenance.get("assertion_status") == "unreviewed_source_assertion"
        and provenance.get("coordinate_precision") == "unknown"
    )
    if not valid_binding:
        return False, False, False
    country = event.get("modern_location_country")
    has_country = (
        isinstance(country, str)
        and bool(country.strip())
        and country == country.strip()
    )
    geometry = event.get("geometry")
    has_point = hced_point_geometry_validation_error(geometry) is None
    if has_point:
        longitude, latitude = geometry["coordinates"]
        has_point = not (longitude == 0 and latitude == 0)
    return has_point, has_country, has_point or has_country


def _valid_unreviewed_hced_location_provenance(event: Mapping[str, Any]) -> bool:
    return _unreviewed_hced_location_flags(event)[2]


def _parent_event_references(event: Mapping[str, Any]) -> set[str]:
    references: set[str] = set()
    singular = event.get("parent_event_id")
    if isinstance(singular, str) and singular.strip():
        references.add(singular)
    plural = event.get("parent_event_ids")
    if isinstance(plural, (list, tuple)):
        references.update(
            value for value in plural if isinstance(value, str) and value.strip()
        )
    return references


def _has_objective_statement(participant: Mapping[str, Any]) -> bool:
    return any(
        _present(participant.get(key))
        for key in (
            "objective",
            "objectives",
            "stated_objective",
            "documented_objective",
            "mission_description",
            "political_objective",
        )
    )


def _field_completeness(events: list[dict[str, Any]]) -> dict[str, Any]:
    event_count = len(events)
    participants: list[tuple[dict[str, Any], str]] = []
    event_ids = {str(event.get("id")) for event in events if _present(event.get("id"))}

    dates_start = 0
    dates_end = 0
    precision = 0
    valid_intervals = 0
    locations = 0
    coordinates = 0
    modern_location_countries = 0
    location_provenance_objects = 0
    valid_unreviewed_location_provenance = 0
    unreviewed_source_locations = 0
    unreviewed_source_points = 0
    explicit_location_region = 0
    at_least_two_participants = 0
    opposing_sides = 0
    parent_links = 0
    parent_reference_count = 0
    resolvable_parent_references = 0
    cluster_links = 0
    any_hierarchy_links = 0

    for event in events:
        start = event.get("year")
        end = event.get("end_year")
        dates_start += int(_is_int(start))
        dates_end += int(_is_int(end))
        precision += int(_category(event.get("date_precision")) != UNKNOWN)
        valid_intervals += int(_is_int(start) and _is_int(end) and end >= start)
        has_location = _has_location(event)
        locations += int(has_location)
        coordinates += int(_has_coordinates(event))
        has_location_provenance = isinstance(event.get("location_provenance"), Mapping)
        location_provenance_objects += int(has_location_provenance)
        (
            has_unreviewed_point,
            has_unreviewed_country,
            has_unreviewed_location,
        ) = _unreviewed_hced_location_flags(event)
        modern_location_countries += int(has_unreviewed_country)
        unreviewed_source_points += int(has_unreviewed_point)
        valid_unreviewed_location_provenance += int(has_unreviewed_location)
        unreviewed_source_locations += int(has_unreviewed_location)
        explicit_location_region += int(
            _category(event.get("region")) not in {UNKNOWN, UNCLASSIFIED}
        )

        raw_participants = event.get("participants")
        participant_rows = (
            [row for row in raw_participants if isinstance(row, dict)]
            if isinstance(raw_participants, list)
            else []
        )
        layer = _event_layer(event)
        participants.extend((row, layer) for row in participant_rows)
        at_least_two_participants += int(len(participant_rows) >= 2)
        sides = {
            str(row.get("side")).strip()
            for row in participant_rows
            if _present(row.get("side"))
        }
        opposing_sides += int(len(sides) >= 2)

        parent_references = _parent_event_references(event)
        has_parent = bool(parent_references)
        has_cluster = _present(event.get("cluster_id"))
        parent_links += int(has_parent)
        parent_reference_count += len(parent_references)
        cluster_links += int(has_cluster)
        any_hierarchy_links += int(has_parent or has_cluster)
        resolvable_parent_references += len(parent_references & event_ids)

    participant_count = len(participants)
    participant_entity_ids = sum(
        _present(row.get("entity_id")) for row, _ in participants
    )
    participant_sides = sum(_present(row.get("side")) for row, _ in participants)
    explicit_roles = sum(_present(row.get("role")) for row, _ in participants)
    documented_objectives = sum(
        _has_objective_statement(row) for row, _ in participants
    )
    objective_outcomes = 0
    objective_applicable = 0
    role_counts: Counter[str] = Counter()
    complete_vectors = 0
    outcome_slot_present = 0
    outcome_slot_total = 0
    unknown_layer_participants = 0
    dimension_present: Counter[str] = Counter()
    dimension_applicable: Counter[str] = Counter()

    for participant, layer in participants:
        role_counts[_category(participant.get("role"))] += 1
        outcome = participant.get("outcome")
        if not isinstance(outcome, dict):
            outcome = {}
        expected = EXPECTED_DIMENSIONS.get(layer)
        if expected is None:
            unknown_layer_participants += 1
            continue
        objective_dimension = OBJECTIVE_DIMENSION_BY_LAYER[layer]
        objective_applicable += 1
        objective_outcomes += int(
            objective_dimension in outcome
            and outcome.get(objective_dimension) is not None
        )
        complete = True
        for dimension in expected:
            scoped_dimension = f"{layer}.{dimension}"
            dimension_applicable[scoped_dimension] += 1
            outcome_slot_total += 1
            if dimension in outcome and outcome.get(dimension) is not None:
                dimension_present[scoped_dimension] += 1
                outcome_slot_present += 1
            else:
                complete = False
        complete_vectors += int(complete)

    by_dimension = {
        dimension: _ratio(
            dimension_present[dimension],
            dimension_applicable[dimension],
            unit="proportion_of_applicable_participants",
            definition=f"Applicable participant outcome vectors with a non-null {dimension} value.",
        )
        for dimension in sorted(dimension_applicable)
    }

    return {
        "dates": {
            "date_precision_explicit": _ratio(
                precision,
                event_count,
                unit="proportion_of_rated_events",
                definition="Rated events with a nonblank, non-unknown date_precision field.",
            ),
            "end_year_present": _ratio(
                dates_end,
                event_count,
                unit="proportion_of_rated_events",
                definition="Rated events with an integer end_year.",
            ),
            "ordered_interval": _ratio(
                valid_intervals,
                event_count,
                unit="proportion_of_rated_events",
                definition="Rated events with integer start/end years and end_year greater than or equal to year.",
            ),
            "start_year_present": _ratio(
                dates_start,
                event_count,
                unit="proportion_of_rated_events",
                definition="Rated events with an integer year.",
            ),
        },
        "hierarchy": {
            "any_parent_or_cluster_link": _ratio(
                any_hierarchy_links,
                event_count,
                unit="proportion_of_rated_events",
                definition="Rated events with at least one nonblank parent_event_id or parent_event_ids reference, or a nonblank cluster_id. Absence can be legitimate for a top-level or unclustered event.",
            ),
            "cluster_link_present": _ratio(
                cluster_links,
                event_count,
                unit="proportion_of_rated_events",
                definition="Rated events with a nonblank cluster_id.",
            ),
            "parent_link_present": _ratio(
                parent_links,
                event_count,
                unit="proportion_of_rated_events",
                definition="Rated events with at least one distinct nonblank parent reference from parent_event_id or parent_event_ids. This is link coverage, not a claim every event needs a parent.",
            ),
            "parent_link_resolves_within_ledger": _ratio(
                resolvable_parent_references,
                parent_reference_count,
                unit="proportion_of_parent_links",
                definition="Distinct parent references from parent_event_id and parent_event_ids resolving to rated event IDs in this ledger, deduplicated within each child event.",
            ),
        },
        "locations": {
            "coordinates_present": _ratio(
                coordinates,
                event_count,
                unit="proportion_of_rated_events",
                definition=(
                    "Rated events with an explicit finite numeric latitude/longitude pair or "
                    "a structurally valid GeoJSON geometry containing such a longitude/latitude position; "
                    "geographic_scope is not a location. This measures field presence, not "
                    "verified geographic truth."
                ),
            ),
            "event_location_present": _ratio(
                locations,
                event_count,
                unit="proportion_of_rated_events",
                definition=(
                    "Rated events with an explicit named/structured location, a valid numeric "
                    "coordinate pair, or a structurally valid supported GeoJSON geometry "
                    "containing at least one in-range longitude/latitude position. This is a "
                    "presence-only aggregate and does not classify the assertion as verified."
                ),
            ),
            "event_region_present": _ratio(
                explicit_location_region,
                event_count,
                unit="proportion_of_rated_events",
                definition="Rated events with an explicit classified event-region field; participant entity regions are not substituted.",
            ),
            "location_provenance_contract_valid": _ratio(
                valid_unreviewed_location_provenance,
                location_provenance_objects,
                unit="proportion_of_location_provenance_objects",
                definition=(
                    "Location-provenance objects matching the closed HCED transcription "
                    "contract: source hced_dataset, a nonblank exact source record ID, "
                    "unreviewed_source_assertion status, and unknown coordinate precision."
                ),
            ),
            "location_provenance_present": _ratio(
                location_provenance_objects,
                event_count,
                unit="proportion_of_rated_events",
                definition=(
                    "Rated events carrying a location_provenance object. Object presence "
                    "alone is not verification."
                ),
            ),
            "modern_location_country_present": _ratio(
                modern_location_countries,
                event_count,
                unit="proportion_of_rated_events",
                definition=(
                    "Rated events carrying a provenance-bound, nonblank HCED "
                    "modern_location_country source field. The value is a source-transcribed "
                    "geographic-jurisdiction label, not inferred sovereign-country truth."
                ),
            ),
            "hced_unreviewed_point_assertion_present": _ratio(
                unreviewed_source_points,
                event_count,
                unit="proportion_of_rated_events",
                definition=(
                    "Rated events carrying an exact provenance-bound HCED GeoJSON Point. "
                    "These source-transcribed Points are unreviewed and have unknown precision."
                ),
            ),
            "hced_unreviewed_geographic_jurisdiction_label_present": _ratio(
                modern_location_countries,
                event_count,
                unit="proportion_of_rated_events",
                definition=(
                    "Rated events carrying a provenance-bound HCED geographic-jurisdiction "
                    "label transcribed from modern_location_country; this is not sovereign-country truth."
                ),
            ),
            "hced_unreviewed_location_assertion_present": _ratio(
                unreviewed_source_locations,
                event_count,
                unit="proportion_of_rated_events",
                definition=(
                    "Rated events carrying at least one provenance-bound HCED location field "
                    "(strict Point or geographic-jurisdiction label), classified as an unreviewed "
                    "source assertion with unknown coordinate precision."
                ),
            ),
            "unreviewed_source_assertion_present": _ratio(
                unreviewed_source_locations,
                event_count,
                unit="proportion_of_rated_events",
                definition=(
                    "Rated events with an exact HCED candidate binding, linked hced_dataset "
                    "source, closed provenance, and at least one strict HCED Point or "
                    "geographic-jurisdiction label. This is unreviewed source transcription, "
                    "not verification."
                ),
            ),
            "verified_location_assertion_present": _unavailable_ratio(
                unit="proportion_of_rated_events",
                definition=(
                    "Rated events whose event location is explicitly established as verified "
                    "under a reviewed-location provenance contract."
                ),
                reason=(
                    "The supplied release has no reviewed-location provenance contract; "
                    "unreviewed HCED transcriptions and locations with unknown status cannot "
                    "be reclassified as verified."
                ),
            ),
        },
        "objectives": {
            "documented_objective_statement": _ratio(
                documented_objectives,
                participant_count,
                unit="proportion_of_participant_records",
                definition="Participant records with an explicit objective statement field. A numeric attainment score alone is not an objective statement.",
            ),
            "objective_attainment_dimension": _ratio(
                objective_outcomes,
                objective_applicable,
                unit="proportion_of_applicable_participants",
                definition="Participants with the layer-specific objective-attainment outcome dimension; this does not establish that the objective itself is documented.",
            ),
        },
        "outcome_dimensions": {
            "by_dimension": by_dimension,
            "complete_expected_vector": _ratio(
                complete_vectors,
                participant_count - unknown_layer_participants,
                unit="proportion_of_participants_on_known_layers",
                definition="Participants carrying every expected outcome dimension for their rating layer.",
            ),
            "expected_dimension_slots_present": _ratio(
                outcome_slot_present,
                outcome_slot_total,
                unit="proportion_of_expected_outcome_slots",
                definition="Non-null expected outcome-dimension values across participants on known layers.",
            ),
            "unknown_layer_participants": _count_metric(
                unknown_layer_participants,
                unit="participant records",
                definition="Participant records whose event layer is unknown, so no expected outcome vector can be selected.",
                source="data/release/events.json",
            ),
        },
        "participants": {
            "at_least_two_participant_records": _ratio(
                at_least_two_participants,
                event_count,
                unit="proportion_of_rated_events",
                definition="Rated events with at least two participant objects.",
            ),
            "entity_id_present": _ratio(
                participant_entity_ids,
                participant_count,
                unit="proportion_of_participant_records",
                definition="Participant records with a nonblank entity_id.",
            ),
            "opposing_sides_explicit": _ratio(
                opposing_sides,
                event_count,
                unit="proportion_of_rated_events",
                definition="Rated events with at least two distinct nonblank participant side labels.",
            ),
            "participant_count": participant_count,
            "side_present": _ratio(
                participant_sides,
                participant_count,
                unit="proportion_of_participant_records",
                definition="Participant records with a nonblank side.",
            ),
        },
        "roles": {
            "explicit_role": _ratio(
                explicit_roles,
                participant_count,
                unit="proportion_of_participant_records",
                definition="Participant records with an explicit nonblank role field; model defaults are not imputed by this report.",
            ),
            "role_counts": _counts(role_counts),
        },
        "scope": "rated events and their participant records",
    }


def _rejection_report(metadata: Mapping[str, Any]) -> dict[str, Any]:
    promotion = metadata.get("promotion")
    if not isinstance(promotion, dict):
        return {
            "availability": "not_available",
            "definition": "Pipeline-specific declared rejection counters; units differ by pipeline and are never summed globally.",
            "pipelines": {},
            "reason": "Release metadata has no promotion object.",
        }

    unit_by_pipeline = {
        "hced": "HCED candidate rows",
        "hced_label": "HCED label-pass candidate rows",
        "iwd": "IWD parent wars",
        "iwbd": "IWBD battle candidates",
        "ucdp": "UCDP termination candidate rows",
    }
    pipelines: dict[str, Any] = {}
    for key, value in promotion.items():
        if not key.endswith("_rejections"):
            continue
        if not isinstance(value, dict):
            raise CoverageInputError(
                f"release.metadata.promotion.{key} must be an object of nonnegative integer counts"
            )
        pipeline = key[: -len("_rejections")]
        reasons: dict[str, int] = {}
        for reason, count_value in value.items():
            count = _as_nonnegative_int(count_value)
            if count is None:
                raise CoverageInputError(
                    f"release.metadata.promotion.{key}.{reason} must be a nonnegative integer"
                )
            reasons[str(reason)] = count
        pipelines[pipeline] = {
            "definition": f"Declared rejection reasons emitted by the {pipeline} promotion pipeline.",
            "reason_counts": {reason: reasons[reason] for reason in sorted(reasons)},
            "total": sum(reasons.values()),
            "unit": unit_by_pipeline.get(pipeline, "pipeline candidates"),
            "unknown_or_unclassified_reason_count": _unavailable_count(
                unit=unit_by_pipeline.get(pipeline, "pipeline candidates"),
                definition="Rejected candidates lacking a declared reason category.",
                reason="The release exposes named counters but no separate unknown-reason counter.",
            ),
        }
    if not pipelines:
        return {
            "availability": "not_available",
            "definition": "Pipeline-specific declared rejection counters; units differ by pipeline and are never summed globally.",
            "pipelines": {},
            "reason": "Release metadata has no declared rejection counter maps.",
        }
    return {
        "availability": "available",
        "definition": (
            "Pipeline-specific declared rejection counters. HCED passes, IWD parents, IWBD battles "
            "and UCDP rows have different units, so this report deliberately supplies no global sum."
        ),
        "pipelines": {key: pipelines[key] for key in sorted(pipelines)},
        "reason": None,
    }


def _registry_coverage(
    registry: Mapping[str, Any] | None,
    rated_events: list[dict[str, Any]],
    results: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(registry, dict) or not isinstance(registry.get("entities"), list):
        reason = "No registry document was supplied."
        return {
            "availability": "not_available",
            "definition": "Registry identities represented by at least one participant in a rated event.",
            "reason": reason,
            "registry_to_rating_ratio": _unavailable_ratio(
                unit="proportion_of_registry_identities",
                definition="Registry identities represented by at least one rated-event participant.",
                reason=reason,
            ),
        }

    registry_rows = [row for row in registry["entities"] if isinstance(row, dict)]
    registry_ids = {
        str(row.get("id")) for row in registry_rows if _present(row.get("id"))
    }
    rated_ids = {
        str(participant.get("entity_id"))
        for event in rated_events
        for participant in event.get("participants", [])
        if isinstance(participant, dict) and _present(participant.get("entity_id"))
    }
    covered_ids = rated_ids & registry_ids
    missing_ids = sorted(rated_ids - registry_ids)
    status_counts = Counter(_category(row.get("status")) for row in registry_rows)
    identity_status_counts = Counter(
        _category(row.get("identity_status")) for row in registry_rows
    )

    result_ids: set[str] = set()
    result_table_supplied = isinstance(results, dict) and isinstance(
        results.get("entities"), list
    )
    if result_table_supplied:
        result_ids = {
            str(row.get("id"))
            for row in results["entities"]
            if isinstance(row, dict) and _present(row.get("id"))
        }

    result_alignment = (
        {
            "availability": "available",
            "registry_identities_in_results": _ratio(
                len(result_ids & registry_ids),
                len(registry_ids),
                unit="proportion_of_registry_identities",
                definition="Registry identities appearing in the supplied rating-results entity table.",
            ),
            "results_entity_ids_missing_from_registry": sorted(
                result_ids - registry_ids
            ),
        }
        if result_table_supplied
        else {
            "availability": "not_available",
            "reason": "No results entity table was supplied.",
        }
    )

    return {
        "availability": "available",
        "definition": "Registry identities represented by at least one participant in a rated event.",
        "identity_status_counts": _counts(identity_status_counts),
        "rated_entity_ids_missing_from_registry": missing_ids,
        "rated_entities_in_registry": len(covered_ids),
        "rated_entity_ids_total": len(rated_ids),
        "registry_entities_total": len(registry_ids),
        "registry_status_counts": _counts(status_counts),
        "registry_to_rating_ratio": _ratio(
            len(covered_ids),
            len(registry_ids),
            unit="proportion_of_registry_identities",
            definition="Registry identities represented by at least one rated-event participant.",
        ),
        "results_alignment": result_alignment,
        "unrated_registry_entities": len(registry_ids - rated_ids),
    }


def _component_sort_key(value: str) -> tuple[int, int | str]:
    try:
        return (0, int(value))
    except ValueError:
        return (1, value)


def _network_report(results: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(results, dict):
        return {
            "availability": "not_available",
            "definition": "Opponent-network connected components among rated result entities.",
            "reason": "No rating-results document was supplied.",
        }
    raw_rows = results.get("entities")
    if not isinstance(raw_rows, list):
        return {
            "availability": "not_available",
            "definition": "Opponent-network connected components among rated result entities.",
            "reason": "The supplied results document has no entity table.",
        }

    component_members: dict[str, list[dict[str, Any]]] = {}
    missing_component_rows: list[dict[str, Any]] = []
    for index, row in enumerate(raw_rows):
        if not isinstance(row, dict):
            continue
        component = row.get("network_component")
        item = {
            "entity_id": str(row.get("id") or f"result_entity_index_{index}"),
            "name": str(
                row.get("name") or row.get("id") or f"result_entity_index_{index}"
            ),
        }
        if component is None or (isinstance(component, str) and not component.strip()):
            missing_component_rows.append(item)
            continue
        component_members.setdefault(str(component), []).append(item)

    if not component_members:
        return {
            "availability": "not_available",
            "definition": "Opponent-network connected components among rated result entities.",
            "entities_missing_component": len(missing_component_rows),
            "reason": "No result entity has an explicit network_component value.",
        }

    component_sizes = {
        component: len(component_members[component])
        for component in sorted(component_members, key=_component_sort_key)
    }
    isolated: list[dict[str, Any]] = []
    for component in sorted(component_members, key=_component_sort_key):
        members = component_members[component]
        if len(members) == 1:
            isolated.append({**members[0], "network_component": component})
    isolated.sort(key=lambda row: (row["name"].casefold(), row["entity_id"]))
    assigned_count = sum(component_sizes.values())
    largest = max(component_sizes.values()) if component_sizes else 0
    return {
        "availability": (
            "available" if not missing_component_rows else "partially_available"
        ),
        "component_count": len(component_sizes),
        "component_sizes": component_sizes,
        "definition": "Opponent-network connected components among rated result entities.",
        "entities_assigned_to_components": assigned_count,
        "entities_missing_component": len(missing_component_rows),
        "isolated_entities": isolated,
        "isolated_entity_count": len(isolated),
        "isolated_entity_share": _ratio(
            len(isolated),
            assigned_count,
            unit="proportion_of_network_assigned_entities",
            definition="Network-assigned result entities whose connected component has size one.",
        ),
        "largest_component_share": _ratio(
            largest,
            assigned_count,
            unit="proportion_of_network_assigned_entities",
            definition="Network-assigned result entities in the largest connected component.",
        ),
    }


def build_coverage_report(
    data_dir: str | Path,
    *,
    review_dir: str | Path | None = None,
    registry_path: str | Path | None = None,
    results_path: str | Path | None = None,
    as_of: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic scientific coverage report from existing artifacts.

    The function never mutates release, review, registry, or results inputs. It
    deliberately returns unavailable metrics when an input lacks the evidence
    needed to define a denominator or an independence/aging claim. Formal
    adjudication is never inferred from curated membership or review/event
    statuses; it remains unavailable until canonical claim records exist.
    """

    root = Path(data_dir)
    events_all = _json_list(root / "events.json")
    entity_rows = _json_list(root / "entities.json")
    source_rows = _json_list(root / "sources.json")
    metadata_path = root / "metadata.json"
    metadata = _json_object(metadata_path) if metadata_path.exists() else {}
    registry = _json_object(Path(registry_path)) if registry_path is not None else None
    results = _json_object(Path(results_path)) if results_path is not None else None
    reference_date = _parse_reference_date(as_of, strict=True)
    if reference_date is None:
        reference_date = _parse_reference_date(
            str(metadata.get("as_of")) if _present(metadata.get("as_of")) else None,
            strict=False,
        )

    rated_events = _rated_events(events_all)
    sources = {
        str(row.get("id")): row for row in source_rows if _present(row.get("id"))
    }
    review_scan = _scan_review(
        Path(review_dir) if review_dir is not None else None, reference_date
    )
    (
        coverage_metadata,
        metadata_queue_counts,
        metadata_queue_counts_source,
    ) = _coverage_metadata(metadata, registry)
    source_family_report = _outcome_source_family_report(rated_events, sources)

    # Prefer release entity regions, then fill only missing IDs from the wider
    # registry. Registry status is never used to infer a rating.
    combined_entity_rows: list[Mapping[str, Any]] = list(entity_rows)
    release_entity_ids = {
        str(row.get("id")) for row in entity_rows if _present(row.get("id"))
    }
    if isinstance(registry, dict) and isinstance(registry.get("entities"), list):
        combined_entity_rows.extend(
            row
            for row in registry["entities"]
            if isinstance(row, dict) and str(row.get("id")) not in release_entity_ids
        )

    stage_funnel = _stage_funnel(
        rated_events,
        metadata,
        coverage_metadata,
        metadata_queue_counts,
        metadata_queue_counts_source,
        review_scan,
    )
    registry_report = _registry_coverage(registry, rated_events, results)

    consistency_checks: dict[str, Any] = {}
    if review_scan.get("directory_supplied") and metadata_queue_counts is not None:
        actual = review_scan.get("counts_by_file", {})
        filenames = sorted(set(actual) | set(metadata_queue_counts))
        mismatches = {
            filename: {
                "declared": int(metadata_queue_counts.get(filename, 0)),
                "observed": int(actual.get(filename, 0)),
            }
            for filename in filenames
            if int(metadata_queue_counts.get(filename, 0))
            != int(actual.get(filename, 0))
        }
        consistency_checks["review_queue_counts"] = {
            "availability": "available",
            "matches": not mismatches,
            "mismatches": mismatches,
        }
    else:
        consistency_checks["review_queue_counts"] = {
            "availability": "not_available",
            "matches": None,
            "reason": "Both physical review queues and declared queue counts are required.",
        }

    observed = {
        "curated_seed_events": stage_funnel["curated_seed"],
        "event_like_candidates": stage_funnel["event_like"],
        "rated_events": stage_funnel["rated"],
        "registry_entities": (
            _count_metric(
                int(registry_report["registry_entities_total"]),
                unit="registry identities",
                definition="Time-bounded identities present in the supplied registry.",
                source="registry entities",
            )
            if registry_report.get("availability") == "available"
            else _unavailable_count(
                unit="registry identities",
                definition="Time-bounded identities present in the supplied registry.",
                reason="No registry document was supplied.",
            )
        ),
        "staged_records": stage_funnel["staged"],
    }

    return {
        "consistency_checks": consistency_checks,
        "event_counts": _event_counts(
            rated_events, combined_entity_rows, source_family_report
        ),
        "field_completeness": _field_completeness(rated_events),
        "historical_completeness": {
            **_unavailable_ratio(
                unit="proportion_of_all_historical_military_events",
                definition="Estimated share of all historical military events represented by this corpus.",
                reason=(
                    "No bounded historical-event universe or probability sampling frame exists in the supplied "
                    "inputs. Observed registry, queue and ledger counts are not an estimate of true historical completeness."
                ),
            ),
            "denominator_known": False,
            "estimate": None,
            "status": "not_estimated",
        },
        "hced_location_policy": _hced_location_policy_report(
            coverage_metadata,
            required=(
                registry is not None
                and any(
                    _present(event.get("hced_candidate_id")) for event in rated_events
                )
            ),
        ),
        "network": _network_report(results),
        "observed_coverage": observed,
        "outcome_source_families": source_family_report,
        "registry_to_rating": registry_report,
        "rejections": _rejection_report(metadata),
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "scope": {
            "dataset_id": metadata.get("dataset_id"),
            "reference_date": reference_date.isoformat() if reference_date else None,
            "release_version": metadata.get("version"),
            "registry_supplied": registry is not None,
            "results_supplied": results is not None,
            "review_directory_supplied": bool(review_scan.get("directory_supplied")),
            "review_files_supplied": bool(review_scan.get("queue_files_present")),
        },
        "stage_funnel": stage_funnel,
        "unresolved_queue_aging": review_scan["aging"],
        "warnings": [
            "Observed coverage is not true historical completeness.",
            "Curated seed membership is not treated as proof of formal claim-level adjudication.",
            "Rated provisional source assertions are not equivalent to human-adjudicated events.",
            "Unknown and unclassified values are retained as explicit categories.",
            "Participant-region counts describe represented actors, not event locations.",
            "Location field-presence totals can include modern, unreviewed source assertions; verified event-location coverage is unavailable.",
        ],
    }


def render_json(report: Mapping[str, Any]) -> str:
    """Serialize a report deterministically."""

    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _display_count(metric: Mapping[str, Any]) -> str:
    count = metric.get("count")
    return f"{count:,}" if isinstance(count, int) else "not available"


def _display_ratio(metric: Mapping[str, Any]) -> str:
    value = metric.get("value")
    return f"{100 * value:.1f}%" if isinstance(value, (int, float)) else "not available"


def _append_distribution(
    lines: list[str],
    title: str,
    counts: Mapping[str, Any],
    *,
    count_label: str = "Events",
) -> None:
    lines.extend(
        [
            f"### {title}",
            "",
            f"| Value | {_markdown_cell(count_label)} |",
            "|---|---:|",
        ]
    )
    for key in sorted(counts, key=lambda item: (str(item).casefold(), str(item))):
        value = counts[key]
        lines.append(f"| {_markdown_cell(key)} | {int(value):,} |")
    lines.append("")


def _append_ratio_group(lines: list[str], title: str, group: Mapping[str, Any]) -> None:
    lines.extend(
        [
            f"### {title}",
            "",
            "| Metric | Numerator | Denominator | Coverage | Unit | Availability | Definition | Reason |",
            "|---|---:|---:|---:|---|---|---|---|",
        ]
    )
    found = False
    for key in sorted(group):
        metric = group[key]
        if not isinstance(metric, dict) or "numerator" not in metric:
            continue
        found = True
        numerator = metric.get("numerator")
        denominator = metric.get("denominator")
        numerator_text = (
            f"{numerator:,}" if isinstance(numerator, int) else "not available"
        )
        denominator_text = (
            f"{denominator:,}" if isinstance(denominator, int) else "not available"
        )
        lines.append(
            f"| {_markdown_cell(key)} | {numerator_text} | {denominator_text} | "
            f"{_display_ratio(metric)} | {_markdown_cell(metric.get('unit', ''))} | "
            f"{_markdown_cell(metric.get('availability'))} | "
            f"{_markdown_cell(metric.get('definition', ''))} | "
            f"{_markdown_cell(metric.get('reason') or '')} |"
        )
    if not found:
        lines.append(
            "| not available | not available | not available | not available | "
            "not available | not_available |  |  |"
        )
    lines.append("")


def _append_count_metric_group(
    lines: list[str], title: str, group: Mapping[str, Any]
) -> None:
    lines.extend(
        [
            f"### {title}",
            "",
            "| Metric | Count | Unit | Availability | Definition | Source | Reason |",
            "|---|---:|---|---|---|---|---|",
        ]
    )
    found = False
    for key in sorted(group):
        metric = group[key]
        if not isinstance(metric, dict) or "count" not in metric:
            continue
        found = True
        lines.append(
            f"| {_markdown_cell(key)} | {_display_count(metric)} | "
            f"{_markdown_cell(metric.get('unit', ''))} | "
            f"{_markdown_cell(metric.get('availability', 'not_available'))} | "
            f"{_markdown_cell(metric.get('definition', ''))} | "
            f"{_markdown_cell(metric.get('source') or '')} | "
            f"{_markdown_cell(metric.get('reason') or '')} |"
        )
    if not found:
        lines.append("| not available | not available |  | not_available |  |  |  |")
    lines.append("")


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render a deterministic human-readable view of a coverage report."""

    lines = [
        "# Military History Elo coverage and quality report",
        "",
        "> Observed corpus coverage is not an estimate of true historical completeness. Rated provisional source assertions are not the same as human-adjudicated events.",
        "",
        "## Stage scorecard",
        "",
        "| Stage | Count | Unit | Availability | Definition | Source | Reason |",
        "|---|---:|---|---|---|---|---|",
    ]
    funnel = report.get("stage_funnel", {})
    for stage in (
        "raw",
        "staged",
        "event_like",
        "unresolved",
        "curated_seed",
        "adjudicated",
        "rated_provisional",
        "rated",
    ):
        metric = funnel.get(stage, {}) if isinstance(funnel, dict) else {}
        lines.append(
            f"| {stage} | {_display_count(metric)} | {_markdown_cell(metric.get('unit', ''))} | "
            f"{_markdown_cell(metric.get('availability', 'not_available'))} | "
            f"{_markdown_cell(metric.get('definition', ''))} | "
            f"{_markdown_cell(metric.get('source') or '')} | "
            f"{_markdown_cell(metric.get('reason') or '')} |"
        )
    if isinstance(funnel, dict) and funnel.get("note"):
        lines.extend(["", str(funnel["note"]), ""])
    reconciliation = (
        funnel.get("unit_reconciliation", {}) if isinstance(funnel, dict) else {}
    )
    if isinstance(reconciliation, dict):
        _append_count_metric_group(lines, "IWD unit reconciliation", reconciliation)

    completeness = report.get("historical_completeness", {})
    lines.extend(
        [
            "## Historical completeness",
            "",
            f"Availability: `{_markdown_cell(completeness.get('availability', 'not_available'))}`.",
            "",
            str(completeness.get("reason", "No estimate is available.")),
            "",
        ]
    )
    if isinstance(completeness, dict):
        _append_ratio_group(
            lines,
            "Historical completeness ratio contract",
            {"historical_completeness": completeness},
        )

    event_counts = report.get("event_counts", {})
    if isinstance(event_counts, dict):
        lines.extend(["## Rated event profile", ""])
        for key, title in (
            ("by_era", "Analysis era"),
            ("by_region", "Event location region"),
            (
                "by_participant_entity_region",
                "Participant-entity region (non-exclusive)",
            ),
            ("by_layer", "Rating layer"),
            ("by_domain", "Domain"),
            ("by_war_type", "War type"),
            ("by_date_precision", "Date precision"),
        ):
            counts = event_counts.get(key)
            if isinstance(counts, dict):
                _append_distribution(lines, title, counts)
        layer_consistency = event_counts.get("explicit_layer_consistency")
        if isinstance(layer_consistency, dict):
            _append_ratio_group(
                lines,
                "Layer contract checks",
                {"explicit_layer_consistency": layer_consistency},
            )
            mismatch_ids = event_counts.get("explicit_layer_mismatch_event_ids", [])
            lines.extend(
                [
                    f"Explicit layer mismatches: "
                    f"{event_counts.get('explicit_layer_mismatch_count', 0):,}.",
                    "",
                ]
            )
            if mismatch_ids:
                lines.extend(
                    [
                        "Mismatched event IDs: "
                        + ", ".join(
                            f"`{_markdown_cell(value)}`" for value in mismatch_ids
                        ),
                        "",
                    ]
                )
        source_family_counts = event_counts.get("by_source_family", {})
        lines.extend(["### Outcome-source family", ""])
        if (
            isinstance(source_family_counts, dict)
            and source_family_counts.get("availability") != "not_available"
        ):
            counts = source_family_counts.get("counts", {})
            lines.extend(["| Family | Event incidences |", "|---|---:|"])
            for family in sorted(counts):
                lines.append(f"| {_markdown_cell(family)} | {int(counts[family]):,} |")
            lines.append("")
        else:
            lines.extend(
                [
                    f"Not available: {_markdown_cell(source_family_counts.get('reason', 'no explicit mapping'))}",
                    "",
                ]
            )

    field = report.get("field_completeness", {})
    if isinstance(field, dict):
        lines.extend(["## Field completeness", ""])
        for key, title in (
            ("dates", "Dates"),
            ("locations", "Locations"),
            ("participants", "Participants"),
            ("roles", "Roles"),
            ("objectives", "Objectives"),
            ("hierarchy", "Hierarchy"),
        ):
            group = field.get(key)
            if isinstance(group, dict):
                _append_ratio_group(lines, title, group)
        roles = field.get("roles", {})
        if isinstance(roles, dict) and isinstance(roles.get("role_counts"), dict):
            _append_distribution(
                lines,
                "Explicit role categories",
                roles["role_counts"],
                count_label="Participant records",
            )
        outcome = field.get("outcome_dimensions")
        if isinstance(outcome, dict):
            _append_ratio_group(lines, "Outcome dimensions", outcome)
            by_dimension = outcome.get("by_dimension")
            if isinstance(by_dimension, dict):
                _append_ratio_group(
                    lines, "Outcome dimensions by layer and field", by_dimension
                )

    hced_policy = report.get("hced_location_policy", {})
    lines.extend(["## Declared HCED location quarantine policy", ""])
    if isinstance(hced_policy, dict) and hced_policy.get("availability") == "available":
        lines.extend(
            [
                str(hced_policy.get("definition", "")),
                "",
                "| Declared policy field | Value |",
                "|---|---:|",
            ]
        )
        for field_name in (
            "point_fields_withheld_by_quarantine",
            "country_or_jurisdiction_fields_withheld_by_quarantine",
            "source_blank_country_fields",
            "point_country_quarantine_overlap",
            "unique_events_with_any_quarantined_field",
        ):
            lines.append(
                f"| {_markdown_cell(field_name)} | {int(hced_policy[field_name]):,} |"
            )
        lines.extend(
            [
                "",
                "Point candidate-manifest SHA-256: "
                f"`{hced_policy['point_quarantine_candidate_manifest_sha256']}`.",
                "",
                "Country/jurisdiction candidate-manifest SHA-256: "
                f"`{hced_policy['country_quarantine_candidate_manifest_sha256']}`.",
                "",
                "Verified location coverage: `not_available`.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "Not available: "
                f"{_markdown_cell(hced_policy.get('reason', 'no declared policy'))}",
                "",
            ]
        )

    families = report.get("outcome_source_families", {})
    lines.extend(["## Independent outcome-source families", ""])
    if isinstance(families, dict):
        lines.extend(
            [
                f"Availability: `{_markdown_cell(families.get('availability', 'not_available'))}`. "
                f"Events with usable explicit mappings: "
                f"{families.get('events_with_explicit_family_data', 0):,} of "
                f"{families.get('event_count', 0):,}; events without a usable mapping: "
                f"{families.get('unmapped_event_count', 0):,}; events carrying at least "
                f"one unusable explicit mapping value: "
                f"{families.get('events_with_unusable_explicit_mapping', 0):,}.",
                "",
            ]
        )
        if families.get("reason"):
            lines.extend([f"Reason: {_markdown_cell(families.get('reason'))}", ""])
        unusable_categories = families.get("unusable_mapping_categories", {})
        if isinstance(unusable_categories, dict) and unusable_categories:
            _append_distribution(
                lines,
                "Unusable explicit outcome-family mapping values",
                unusable_categories,
                count_label="Mapping values",
            )
        _append_ratio_group(
            lines,
            "Outcome-source family ratios",
            {
                "explicit_mapping_coverage": families.get("explicit_mapping_coverage"),
                "multiple_family_coverage": families.get("multiple_family_coverage"),
            },
        )

    registry = report.get("registry_to_rating", {})
    lines.extend(["## Registry-to-rating coverage", ""])
    if isinstance(registry, dict) and registry.get("availability") == "available":
        ratio = registry.get("registry_to_rating_ratio", {})
        lines.extend(
            [
                f"{registry.get('rated_entities_in_registry', 0):,} of "
                f"{registry.get('registry_entities_total', 0):,} registry identities appear in rated events "
                f"({_display_ratio(ratio)}).",
                "",
            ]
        )
    else:
        lines.extend(
            [f"Not available: {_markdown_cell(registry.get('reason', ''))}", ""]
        )
    if isinstance(registry, dict):
        _append_ratio_group(
            lines,
            "Registry-to-rating ratio",
            {"registry_to_rating_ratio": registry.get("registry_to_rating_ratio")},
        )
        results_alignment = registry.get("results_alignment", {})
        if isinstance(results_alignment, dict):
            alignment_ratio = results_alignment.get("registry_identities_in_results")
            if isinstance(alignment_ratio, dict):
                _append_ratio_group(
                    lines,
                    "Registry-to-results alignment",
                    {"registry_identities_in_results": alignment_ratio},
                )

    network = report.get("network", {})
    lines.extend(["## Opponent network", ""])
    if isinstance(network, dict) and network.get("availability") != "not_available":
        lines.extend(
            [
                f"Availability: `{_markdown_cell(network.get('availability'))}`. Components: "
                f"{network.get('component_count', 0):,}; entities assigned to a component: "
                f"{network.get('entities_assigned_to_components', 0):,}; entities missing a component: "
                f"{network.get('entities_missing_component', 0):,}; isolated entities: "
                f"{network.get('isolated_entity_count', 0):,}.",
                "",
                "| Component | Entities |",
                "|---|---:|",
            ]
        )
        sizes = network.get("component_sizes", {})
        for component in sorted(sizes, key=lambda item: _component_sort_key(str(item))):
            lines.append(f"| {_markdown_cell(component)} | {int(sizes[component]):,} |")
        lines.append("")
        isolated = network.get("isolated_entities", [])
        if isolated:
            lines.extend(["Isolated entities:", ""])
            for row in isolated:
                lines.append(
                    f"- {_markdown_cell(row.get('name'))} (`{_markdown_cell(row.get('entity_id'))}`)"
                )
            lines.append("")
        _append_ratio_group(
            lines,
            "Opponent-network ratios",
            {
                "isolated_entity_share": network.get("isolated_entity_share"),
                "largest_component_share": network.get("largest_component_share"),
            },
        )
    else:
        lines.extend(
            [f"Not available: {_markdown_cell(network.get('reason', ''))}", ""]
        )

    rejections = report.get("rejections", {})
    lines.extend(["## Rejection reasons", ""])
    if isinstance(rejections, dict) and rejections.get("availability") == "available":
        lines.extend(["| Pipeline | Reason | Count | Unit |", "|---|---|---:|---|"])
        pipelines = rejections.get("pipelines", {})
        for pipeline in sorted(pipelines):
            item = pipelines[pipeline]
            for reason, count in item.get("reason_counts", {}).items():
                lines.append(
                    f"| {_markdown_cell(pipeline)} | {_markdown_cell(reason)} | {int(count):,} | "
                    f"{_markdown_cell(item.get('unit', ''))} |"
                )
        lines.append("")
    else:
        lines.extend(
            [f"Not available: {_markdown_cell(rejections.get('reason', ''))}", ""]
        )

    aging = report.get("unresolved_queue_aging", {})
    lines.extend(["## Unresolved queue aging", ""])
    if isinstance(aging, dict) and aging.get("availability") in {
        "available",
        "partially_available",
    }:
        lines.extend(
            [
                f"Reference date: `{aging.get('reference_date')}`; median age: "
                f"{aging.get('median_age_days')} days. Missing timestamps: "
                f"{aging.get('missing_timestamp_count', 0):,}; invalid timestamps: "
                f"{aging.get('invalid_timestamp_count', 0):,}.",
                "",
                "| Age bucket | Candidates |",
                "|---|---:|",
            ]
        )
        for bucket, count in aging.get("age_buckets", {}).items():
            lines.append(f"| {_markdown_cell(bucket)} | {int(count):,} |")
        lines.append("")
    elif isinstance(aging, dict) and aging.get("availability") == "not_applicable":
        lines.extend([f"Not applicable: {_markdown_cell(aging.get('reason', ''))}", ""])
    else:
        lines.extend([f"Not available: {_markdown_cell(aging.get('reason', ''))}", ""])
    if isinstance(aging, dict):
        timestamp_coverage = aging.get("timestamp_coverage")
        if isinstance(timestamp_coverage, dict):
            _append_ratio_group(
                lines,
                "Queue-timestamp coverage",
                {"timestamp_coverage": timestamp_coverage},
            )

    lines.extend(
        [
            "## Interpretation limits",
            "",
            "- Counts describe supplied artifacts and their declared processing stages, not all historical events.",
            "- Unknown and unclassified values remain explicit rather than being redistributed or imputed.",
            "- Source-family independence is reported only from an explicit outcome-family mapping.",
            "- Queue age is reported only from explicit queue timestamps and a deterministic reference date.",
            "",
        ]
    )
    return "\n".join(lines)


def write_coverage_report(
    report: Mapping[str, Any], output_dir: str | Path, *, basename: str = "coverage"
) -> tuple[Path, Path]:
    """Write deterministic JSON and Markdown files to an explicit directory."""

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", basename) or basename in {
        ".",
        "..",
    }:
        raise ValueError(
            "Coverage output basename must be one safe filename component using letters, digits, '.', '_', or '-'."
        )
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    json_path = destination / f"{basename}.json"
    markdown_path = destination / f"{basename}.md"
    json_path.write_bytes(render_json(report).encode("utf-8"))
    markdown_path.write_bytes(render_markdown(report).encode("utf-8"))
    return json_path, markdown_path


# Descriptive aliases keep the public API readable without changing the short
# renderer names used internally.
render_coverage_json = render_json
render_coverage_markdown = render_markdown
