"""Claim-neutral event identity, uncertain dates, and participation intervals.

Machine dates use signed BCE/CE years with no year zero.  Month/day validation
uses the proleptic Gregorian calendar as a storage convention, without implying
that historical sources used that calendar contemporaneously.  These fields are
evidence data only; the rating engine does not interpret them in this workstream.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from .claims import canonicalize_json


DateValue = int | str
DateKey = tuple[int, int, int]


_DATE_PATTERN = re.compile(
    r"(?P<year>-?[0-9]{1,6})(?:-(?P<month>[0-9]{2})(?:-(?P<day>[0-9]{2}))?)?"
)

_UNCERTAIN_DATE_FIELDS = frozenset(
    {"low", "best", "high", "precision", "earliest", "latest"}
)
_INTERVAL_FIELDS = frozenset(
    {
        "start",
        "end",
        "start_low",
        "start_best",
        "start_high",
        "start_precision",
        "end_low",
        "end_best",
        "end_high",
        "end_precision",
        "precision",
    }
)
_INTERVAL_FLAT_FIELDS = _INTERVAL_FIELDS - {"start", "end"}
_PARTICIPATION_EPISODE_FIELDS = frozenset(
    {
        "id",
        "episode_id",
        "entity_id",
        "side",
        "role",
        "entry",
        "entry_date",
        "exit",
        "exit_date",
        "contribution",
        "objectives",
        "claim_ids",
    }
)
_LOCATION_PROVENANCE_FIELDS = frozenset(
    {
        "source_id",
        "source_record_id",
        "assertion_status",
        "coordinate_precision",
    }
)


def _validate_known_fields(
    raw: Any, *, model_name: str, allowed_fields: frozenset[str]
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise TypeError(f"{model_name} must be a JSON object")
    unknown = sorted(set(raw) - allowed_fields)
    if unknown:
        raise ValueError(
            f"{model_name} contains unknown field(s): {', '.join(unknown)}"
        )
    return raw


def _required_nonblank_text(
    raw: dict[str, Any],
    name: str,
    *,
    model_name: str,
    alias: str | None = None,
) -> str:
    if alias is not None and name in raw and alias in raw:
        raise ValueError(f"{model_name} cannot contain both {name} and {alias}")
    if name in raw:
        value = raw[name]
    elif alias is not None and alias in raw:
        value = raw[alias]
    else:
        raise ValueError(f"{model_name}.{name} is required")
    if not isinstance(value, str):
        raise TypeError(f"{model_name}.{name} must be a string")
    if not value.strip():
        raise ValueError(f"{model_name}.{name} must be non-blank")
    return value


def _require_nonblank_text_value(value: Any, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    if not value.strip():
        raise ValueError(f"{field_name} must be non-blank")


def _optional_text_or_none(
    raw: dict[str, Any], name: str, *, model_name: str
) -> str | None:
    value = raw.get(name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{model_name}.{name} must be a string or null")
    return value


def _aliased_value(
    raw: dict[str, Any], name: str, alias: str, *, model_name: str
) -> Any:
    if name in raw and alias in raw:
        raise ValueError(f"{model_name} cannot contain both {name} and {alias}")
    return raw[name] if name in raw else raw.get(alias)


def _string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value == ():
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise TypeError(f"{field_name} must be an array of strings")
    if any(not isinstance(item, str) for item in value):
        raise TypeError(f"{field_name} must contain only strings")
    return tuple(value)


def _stable_id_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    result = _string_tuple(value, field_name)
    if any(not item.strip() for item in result):
        raise ValueError(f"{field_name} must contain only non-blank ids")
    return result


def freeze_json(value: Any) -> Any:
    """Return a detached, deeply immutable canonical JSON value.

    Objects become read-only mappings and arrays become tuples.  Passing the
    result back through ``canonicalize_json`` restores ordinary deterministic
    JSON dictionaries and lists for serialization.
    """

    normalized = canonicalize_json(value)

    def freeze(item: Any) -> Any:
        if isinstance(item, dict):
            return MappingProxyType(
                {key: freeze(item[key]) for key in sorted(item)}
            )
        if isinstance(item, list):
            return tuple(freeze(child) for child in item)
        return item

    return freeze(normalized)


_GEOJSON_TYPES = frozenset(
    {
        "Point",
        "MultiPoint",
        "LineString",
        "MultiLineString",
        "Polygon",
        "MultiPolygon",
        "GeometryCollection",
    }
)


def _is_finite_position_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    return False


def _position_error(value: Any, label: str) -> str | None:
    if not isinstance(value, (list, tuple)) or len(value) < 2:
        return f"{label} must be a position with at least two ordinates"
    if not all(_is_finite_position_number(item) for item in value):
        return f"{label} ordinates must be finite non-boolean numbers"
    return None


def _line_string_error(value: Any, label: str) -> str | None:
    if not isinstance(value, (list, tuple)) or len(value) < 2:
        return f"{label} must contain at least two positions"
    for index, position in enumerate(value):
        error = _position_error(position, f"{label}[{index}]")
        if error is not None:
            return error
    return None


def _linear_ring_error(value: Any, label: str) -> str | None:
    if not isinstance(value, (list, tuple)) or len(value) < 4:
        return f"{label} must contain at least four positions"
    for index, position in enumerate(value):
        error = _position_error(position, f"{label}[{index}]")
        if error is not None:
            return error
    if tuple(value[0]) != tuple(value[-1]):
        return f"{label} must be closed (first and last positions must match)"
    return None


def _polygon_error(value: Any, label: str) -> str | None:
    if not isinstance(value, (list, tuple)) or not value:
        return f"{label} must contain at least one linear ring"
    for index, ring in enumerate(value):
        error = _linear_ring_error(ring, f"{label}[{index}]")
        if error is not None:
            return error
    return None


def geometry_validation_error(geometry: Any) -> str | None:
    """Return the first strict GeoJSON geometry error, or ``None``.

    The evidence model accepts the seven GeoJSON geometry types and validates
    their coordinate nesting and minimum structural requirements.  Position
    ordinates must be finite JSON numbers; booleans are never coordinates.
    """

    if not isinstance(geometry, Mapping):
        return "Geometry must be a GeoJSON object"
    geometry_type = geometry.get("type")
    if geometry_type not in _GEOJSON_TYPES:
        return f"Unknown GeoJSON geometry type {geometry_type!r}"
    if geometry_type == "GeometryCollection":
        geometries = geometry.get("geometries")
        if not isinstance(geometries, (list, tuple)):
            return "GeometryCollection requires a geometries array"
        for index, member in enumerate(geometries):
            error = geometry_validation_error(member)
            if error is not None:
                return f"GeometryCollection member {index} is invalid: {error}"
        return None

    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, (list, tuple)):
        return f"{geometry_type} requires a coordinates array"
    if geometry_type == "Point":
        return _position_error(coordinates, "Point coordinates")
    if geometry_type == "MultiPoint":
        for index, position in enumerate(coordinates):
            error = _position_error(position, f"MultiPoint coordinates[{index}]")
            if error is not None:
                return error
        return None
    if geometry_type == "LineString":
        return _line_string_error(coordinates, "LineString coordinates")
    if geometry_type == "MultiLineString":
        for index, line in enumerate(coordinates):
            error = _line_string_error(
                line, f"MultiLineString coordinates[{index}]"
            )
            if error is not None:
                return error
        return None
    if geometry_type == "Polygon":
        return _polygon_error(coordinates, "Polygon coordinates")
    for index, polygon in enumerate(coordinates):
        error = _polygon_error(polygon, f"MultiPolygon coordinates[{index}]")
        if error is not None:
            return error
    return None


def hced_point_geometry_validation_error(geometry: Any) -> str | None:
    """Return an error unless an HCED assertion is an exact GeoJSON Point.

    This contract is intentionally narrower than the generic geometry model.
    It validates exactly two finite, non-boolean ordinates in GeoJSON order
    and does not apply the source-ingest ``(0, 0)`` sentinel rule.
    """

    if not isinstance(geometry, Mapping):
        return "HCED location geometry must be a GeoJSON object"
    if set(geometry) != {"type", "coordinates"}:
        return "HCED location geometry must contain exactly type and coordinates"
    if geometry.get("type") != "Point":
        return "HCED location geometry type must be exactly 'Point'"
    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, (list, tuple)) or len(coordinates) != 2:
        return "HCED Point coordinates must contain exactly two ordinates"
    if not all(_is_finite_position_number(value) for value in coordinates):
        return "HCED Point ordinates must be finite non-boolean numbers"
    longitude, latitude = coordinates
    if not -180 <= longitude <= 180:
        return "HCED Point longitude must be between -180 and 180"
    if not -90 <= latitude <= 90:
        return "HCED Point latitude must be between -90 and 90"
    return None


@dataclass(frozen=True)
class LocationProvenance:
    """Closed provenance for the source-transcribed HCED location assertion."""

    source_id: str
    source_record_id: str
    assertion_status: str
    coordinate_precision: str

    def __post_init__(self) -> None:
        for field_name in _LOCATION_PROVENANCE_FIELDS:
            value = getattr(self, field_name)
            _require_nonblank_text_value(
                value, f"LocationProvenance.{field_name}"
            )
            if value != value.strip():
                raise ValueError(
                    f"LocationProvenance.{field_name} must not contain "
                    "surrounding whitespace"
                )
        expected = {
            "source_id": "hced_dataset",
            "assertion_status": "unreviewed_source_assertion",
            "coordinate_precision": "unknown",
        }
        for field_name, expected_value in expected.items():
            if getattr(self, field_name) != expected_value:
                raise ValueError(
                    f"LocationProvenance.{field_name} must be {expected_value!r}"
                )

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "source_record_id": self.source_record_id,
            "assertion_status": self.assertion_status,
            "coordinate_precision": self.coordinate_precision,
        }

    @classmethod
    def from_dict(cls, raw: Any) -> "LocationProvenance":
        raw = _validate_known_fields(
            raw,
            model_name="LocationProvenance",
            allowed_fields=_LOCATION_PROVENANCE_FIELDS,
        )
        missing = sorted(_LOCATION_PROVENANCE_FIELDS - set(raw))
        if missing:
            raise ValueError(
                "LocationProvenance is missing required field(s): "
                + ", ".join(missing)
            )
        return cls(
            source_id=raw["source_id"],
            source_record_id=raw["source_record_id"],
            assertion_status=raw["assertion_status"],
            coordinate_precision=raw["coordinate_precision"],
        )


def _date_key(value: DateValue | None) -> DateKey | None:
    if value is None:
        return None
    if isinstance(value, int):
        return (value, 1, 1)
    match = _DATE_PATTERN.fullmatch(value.strip())
    if not match:
        return None
    year = int(match.group("year"))
    month = int(match.group("month") or 1)
    day = int(match.group("day") or 1)
    return (year, month, day)


def date_sort_key(value: DateValue | None) -> DateKey | None:
    """Return a comparable key for a valid date value, otherwise ``None``."""

    if value is None or _date_validation_error(value) is not None:
        return None
    return _date_key(value)


def date_bounds(value: DateValue | None) -> tuple[DateKey, DateKey] | None:
    """Return the full proleptic-Gregorian period represented by ``value``.

    A signed year spans January 1 through December 31, a year-month spans the
    whole month, and a day is a point interval.  Invalid values return
    ``None`` so callers can leave error reporting to ``validation_errors``.
    """

    if value is None or _date_validation_error(value) is not None:
        return None
    if isinstance(value, int):
        return ((value, 1, 1), (value, 12, 31))
    match = _DATE_PATTERN.fullmatch(value)
    if match is None:
        return None
    year = int(match.group("year"))
    month_raw = match.group("month")
    day_raw = match.group("day")
    if month_raw is None:
        return ((year, 1, 1), (year, 12, 31))
    month = int(month_raw)
    if day_raw is None:
        month_lengths = (
            31,
            29 if _is_leap_year(year) else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        )
        return ((year, month, 1), (year, month, month_lengths[month - 1]))
    day = int(day_raw)
    return ((year, month, day), (year, month, day))


def _astronomical_year(year: int) -> int:
    """Map the project's no-year-zero BCE/CE convention for leap arithmetic."""

    return year if year > 0 else year + 1


def _is_leap_year(year: int) -> bool:
    astronomical = _astronomical_year(year)
    return astronomical % 4 == 0 and (
        astronomical % 100 != 0 or astronomical % 400 == 0
    )


def _date_validation_error(value: Any) -> str | None:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        return "must be a signed year, YYYY-MM, or YYYY-MM-DD"
    if isinstance(value, int):
        return "year zero is invalid under the BCE/CE convention" if value == 0 else None
    match = _DATE_PATTERN.fullmatch(value)
    if not match:
        return "must be a signed year, YYYY-MM, or YYYY-MM-DD"
    year = int(match.group("year"))
    if year == 0:
        return "year zero is invalid under the BCE/CE convention"
    month_raw = match.group("month")
    day_raw = match.group("day")
    if month_raw is None:
        return None
    month = int(month_raw)
    if not 1 <= month <= 12:
        return "month must be in 01..12"
    if day_raw is None:
        return None
    day = int(day_raw)
    month_lengths = [31, 29 if _is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not 1 <= day <= month_lengths[month - 1]:
        return f"day is invalid for month {month:02d} in the proleptic Gregorian calendar"
    return None


def _coerce_date(value: Any) -> DateValue | None:
    if value is None or (
        isinstance(value, (str, int)) and not isinstance(value, bool)
    ):
        return value
    raise TypeError("Historical dates must be signed years, date strings, or null")


@dataclass(frozen=True)
class UncertainDate:
    """Low/best/high bounds using signed BCE/CE years with no year zero.

    Month/day validation uses the proleptic Gregorian calendar solely as a
    machine-readable date convention; it makes no claim that a source used
    that calendar contemporaneously.
    """

    low: DateValue | None = None
    best: DateValue | None = None
    high: DateValue | None = None
    precision: str = "unknown"

    def __post_init__(self) -> None:
        object.__setattr__(self, "low", _coerce_date(self.low))
        object.__setattr__(self, "best", _coerce_date(self.best))
        object.__setattr__(self, "high", _coerce_date(self.high))

    @classmethod
    def exact(cls, value: DateValue, precision: str = "exact") -> "UncertainDate":
        return cls(low=value, best=value, high=value, precision=precision)

    @property
    def earliest(self) -> DateValue | None:
        return self.low if self.low is not None else self.best if self.best is not None else self.high

    @property
    def latest(self) -> DateValue | None:
        return self.high if self.high is not None else self.best if self.best is not None else self.low

    def validation_errors(self) -> list[str]:
        errors: list[str] = []
        if not isinstance(self.precision, str) or not self.precision.strip():
            errors.append("precision must be a non-blank string")
        if self.low is None and self.best is None and self.high is None:
            errors.append("date has no low, best, or high value")
            return errors
        ordered = [
            ("low", self.low),
            ("best", self.best),
            ("high", self.high),
        ]
        invalid_names: set[str] = set()
        for name, value in ordered:
            if value is None:
                continue
            error = _date_validation_error(value)
            if error:
                errors.append(f"{name} date {error}")
                invalid_names.add(name)
        present = [(name, date_bounds(value)) for name, value in ordered if value is not None]
        for (left_name, left), (right_name, right) in zip(present, present[1:]):
            if (
                left_name not in invalid_names
                and right_name not in invalid_names
                and left is not None
                and right is not None
                and left[0] > right[1]
            ):
                errors.append(f"{left_name} date follows {right_name} date")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "low": self.low,
            "best": self.best,
            "high": self.high,
            "precision": self.precision,
        }

    @classmethod
    def from_dict(cls, raw: Any) -> "UncertainDate":
        """Parse a date, retaining ``earliest``/``latest`` only as aliases."""

        if isinstance(raw, (str, int)) and not isinstance(raw, bool):
            return cls.exact(raw)
        raw = _validate_known_fields(
            raw,
            model_name="UncertainDate",
            allowed_fields=_UNCERTAIN_DATE_FIELDS,
        )
        return cls(
            low=_aliased_value(
                raw, "low", "earliest", model_name="UncertainDate"
            ),
            best=raw.get("best"),
            high=_aliased_value(
                raw, "high", "latest", model_name="UncertainDate"
            ),
            precision=raw.get("precision", "unknown"),
        )


@dataclass(frozen=True)
class UncertainDateInterval:
    """Independently uncertain start and end dates for an event."""

    start: UncertainDate
    end: UncertainDate

    def __post_init__(self) -> None:
        for field_name in ("start", "end"):
            if not isinstance(getattr(self, field_name), UncertainDate):
                raise TypeError(
                    f"UncertainDateInterval.{field_name} must be an UncertainDate"
                )

    def validation_errors(self) -> list[str]:
        errors = [f"start {item}" for item in self.start.validation_errors()]
        errors.extend(f"end {item}" for item in self.end.validation_errors())
        start_best = date_bounds(self.start.best)
        end_best = date_bounds(self.end.best)
        if start_best is not None and end_best is not None and start_best[0] > end_best[1]:
            errors.append("best start date follows best end date")
        earliest_start = date_bounds(self.start.earliest)
        latest_end = date_bounds(self.end.latest)
        if (
            earliest_start is not None
            and latest_end is not None
            and earliest_start[0] > latest_end[1]
        ):
            errors.append("date bounds cannot form a non-negative interval")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {"start": self.start.to_dict(), "end": self.end.to_dict()}

    @classmethod
    def from_dict(cls, raw: Any) -> "UncertainDateInterval":
        """Parse canonical bounds or the explicit legacy flat-bound aliases."""

        raw = _validate_known_fields(
            raw,
            model_name="UncertainDateInterval",
            allowed_fields=_INTERVAL_FIELDS,
        )
        if "start" in raw or "end" in raw:
            if "start" not in raw or "end" not in raw:
                raise ValueError("date_interval requires both start and end")
            mixed = sorted(set(raw) & _INTERVAL_FLAT_FIELDS)
            if mixed:
                raise ValueError(
                    "UncertainDateInterval cannot mix start/end objects with "
                    f"flat compatibility fields: {', '.join(mixed)}"
                )
            return cls(
                start=UncertainDate.from_dict(raw["start"]),
                end=UncertainDate.from_dict(raw["end"]),
            )
        return cls(
            start=UncertainDate(
                low=raw.get("start_low"),
                best=raw.get("start_best"),
                high=raw.get("start_high"),
                precision=raw.get("start_precision", raw.get("precision", "unknown")),
            ),
            end=UncertainDate(
                low=raw.get("end_low"),
                best=raw.get("end_best"),
                high=raw.get("end_high"),
                precision=raw.get("end_precision", raw.get("precision", "unknown")),
            ),
        )


@dataclass(frozen=True)
class ParticipationEpisode:
    """One actor's bounded period of participation on one side of an event."""

    id: str
    entity_id: str
    side: str
    role: str
    entry: UncertainDate | None = None
    exit: UncertainDate | None = None
    contribution: float | None = None
    objectives: tuple[str, ...] = field(default_factory=tuple)
    claim_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for field_name in ("id", "entity_id", "side", "role"):
            _require_nonblank_text_value(
                getattr(self, field_name), f"ParticipationEpisode.{field_name}"
            )
        for field_name in ("entry", "exit"):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, UncertainDate):
                raise TypeError(
                    f"ParticipationEpisode.{field_name} must be an UncertainDate or null"
                )
        if self.contribution is not None and (
            isinstance(self.contribution, bool)
            or not isinstance(self.contribution, (int, float))
        ):
            raise TypeError("ParticipationEpisode.contribution must be a number or null")
        object.__setattr__(
            self,
            "objectives",
            _string_tuple(self.objectives, "ParticipationEpisode.objectives"),
        )
        object.__setattr__(
            self,
            "claim_ids",
            tuple(
                sorted(
                    set(_stable_id_tuple(self.claim_ids, "ParticipationEpisode.claim_ids"))
                )
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "entity_id": self.entity_id,
            "side": self.side,
            "role": self.role,
        }
        if self.entry is not None:
            result["entry"] = self.entry.to_dict()
        if self.exit is not None:
            result["exit"] = self.exit.to_dict()
        if self.contribution is not None:
            result["contribution"] = self.contribution
        if self.objectives:
            result["objectives"] = list(self.objectives)
        if self.claim_ids:
            result["claim_ids"] = sorted(set(self.claim_ids))
        return result

    def validation_errors(self) -> list[str]:
        errors: list[str] = []
        if self.entry is not None:
            errors.extend(f"entry {item}" for item in self.entry.validation_errors())
        if self.exit is not None:
            errors.extend(f"exit {item}" for item in self.exit.validation_errors())
        if self.contribution is not None and not 0 <= self.contribution <= 1:
            errors.append("contribution must be in 0..1 when known")
        if self.entry is not None and self.exit is not None:
            entry_best = date_bounds(self.entry.best)
            exit_best = date_bounds(self.exit.best)
            if (
                entry_best is not None
                and exit_best is not None
                and entry_best[0] > exit_best[1]
            ):
                errors.append("best entry date follows best exit date")
            earliest_entry = date_bounds(self.entry.earliest)
            latest_exit = date_bounds(self.exit.latest)
            if (
                earliest_entry is not None
                and latest_exit is not None
                and earliest_entry[0] > latest_exit[1]
            ):
                errors.append("entry/exit bounds cannot form a non-negative episode")
        return errors

    @classmethod
    def from_dict(cls, raw: Any) -> "ParticipationEpisode":
        """Parse one episode, retaining only documented compatibility aliases.

        ``episode_id``, ``entry_date``, and ``exit_date`` remain accepted as
        legacy aliases.  All other unknown fields fail closed, matching the
        nested event schema's ``additionalProperties: false`` contract.
        """

        raw = _validate_known_fields(
            raw,
            model_name="ParticipationEpisode",
            allowed_fields=_PARTICIPATION_EPISODE_FIELDS,
        )
        entry_raw = _aliased_value(
            raw, "entry", "entry_date", model_name="ParticipationEpisode"
        )
        exit_raw = _aliased_value(
            raw, "exit", "exit_date", model_name="ParticipationEpisode"
        )
        return cls(
            id=_required_nonblank_text(
                raw,
                "id",
                alias="episode_id",
                model_name="ParticipationEpisode",
            ),
            entity_id=_required_nonblank_text(
                raw, "entity_id", model_name="ParticipationEpisode"
            ),
            side=_required_nonblank_text(
                raw, "side", model_name="ParticipationEpisode"
            ),
            role=_required_nonblank_text(
                raw, "role", model_name="ParticipationEpisode"
            ),
            entry=UncertainDate.from_dict(entry_raw) if entry_raw is not None else None,
            exit=UncertainDate.from_dict(exit_raw) if exit_raw is not None else None,
            contribution=(
                raw["contribution"]
                if raw.get("contribution") is not None
                else None
            ),
            objectives=_string_tuple(
                raw["objectives"] if "objectives" in raw else [],
                "ParticipationEpisode.objectives",
            ),
            claim_ids=_stable_id_tuple(
                raw["claim_ids"] if "claim_ids" in raw else [],
                "ParticipationEpisode.claim_ids",
            ),
        )


@dataclass(frozen=True)
class CanonicalEvent:
    """Claim-neutral event identity and hierarchy record.

    ``status`` is review workflow metadata only.  It is never interpreted as
    rating eligibility by this module.
    """

    id: str
    name: str
    aliases: tuple[str, ...] = field(default_factory=tuple)
    parent_event_ids: tuple[str, ...] = field(default_factory=tuple)
    child_event_ids: tuple[str, ...] = field(default_factory=tuple)
    date_interval: UncertainDateInterval | None = None
    geometry: Mapping[str, Any] | None = None
    participation_episodes: tuple[ParticipationEpisode, ...] = field(default_factory=tuple)
    claim_ids: tuple[str, ...] = field(default_factory=tuple)
    adjudication_ids: tuple[str, ...] = field(default_factory=tuple)
    event_type: str | None = None
    layer: str | None = None
    domain: str | None = None
    region: str | None = None
    status: str = "proposed"
    hced_candidate_id: str | None = None
    modern_location_country: str | None = None
    location_provenance: LocationProvenance | None = None
    source_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for field_name in ("id", "name", "status"):
            _require_nonblank_text_value(
                getattr(self, field_name), f"CanonicalEvent.{field_name}"
            )
        for field_name in ("event_type", "layer", "domain", "region"):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, str):
                raise TypeError(
                    f"CanonicalEvent.{field_name} must be a string or null"
                )
        if self.date_interval is not None and not isinstance(
            self.date_interval, UncertainDateInterval
        ):
            raise TypeError(
                "CanonicalEvent.date_interval must be an UncertainDateInterval or null"
            )
        source_ids = tuple(
            sorted(set(_stable_id_tuple(self.source_ids, "CanonicalEvent.source_ids")))
        )
        if any(source_id != source_id.strip() for source_id in source_ids):
            raise ValueError(
                "CanonicalEvent.source_ids must not contain surrounding whitespace"
            )
        object.__setattr__(self, "source_ids", source_ids)
        for field_name in ("hced_candidate_id", "modern_location_country"):
            value = getattr(self, field_name)
            if value is None:
                continue
            _require_nonblank_text_value(value, f"CanonicalEvent.{field_name}")
            if value != value.strip():
                raise ValueError(
                    f"CanonicalEvent.{field_name} must not contain surrounding whitespace"
                )
        if self.location_provenance is not None and not isinstance(
            self.location_provenance, LocationProvenance
        ):
            raise TypeError(
                "CanonicalEvent.location_provenance must be a LocationProvenance or null"
            )
        if (
            self.hced_candidate_id is not None
            and "hced_dataset" not in self.source_ids
        ):
            raise ValueError(
                "CanonicalEvent.hced_candidate_id requires hced_dataset in source_ids"
            )
        if self.modern_location_country is not None and self.location_provenance is None:
            raise ValueError(
                "CanonicalEvent.modern_location_country requires location_provenance"
            )
        if self.location_provenance is not None:
            if self.hced_candidate_id is None:
                raise ValueError(
                    "CanonicalEvent.location_provenance requires hced_candidate_id"
                )
            if self.modern_location_country is None and self.geometry is None:
                raise ValueError(
                    "CanonicalEvent.location_provenance requires a location assertion"
                )
        if (
            self.hced_candidate_id is not None
            and self.geometry is not None
            and self.location_provenance is None
        ):
            raise ValueError(
                "CanonicalEvent HCED geometry requires location_provenance"
            )
        if self.hced_candidate_id is not None and self.geometry is not None:
            geometry_error = hced_point_geometry_validation_error(self.geometry)
            if geometry_error is not None:
                raise ValueError(geometry_error)
        object.__setattr__(
            self,
            "aliases",
            tuple(sorted(set(_string_tuple(self.aliases, "CanonicalEvent.aliases")))),
        )
        object.__setattr__(
            self,
            "parent_event_ids",
            tuple(
                sorted(
                    set(
                        _stable_id_tuple(
                            self.parent_event_ids, "CanonicalEvent.parent_event_ids"
                        )
                    )
                )
            ),
        )
        object.__setattr__(
            self,
            "child_event_ids",
            tuple(
                sorted(
                    set(
                        _stable_id_tuple(
                            self.child_event_ids, "CanonicalEvent.child_event_ids"
                        )
                    )
                )
            ),
        )
        if not isinstance(self.participation_episodes, (list, tuple)):
            raise TypeError("CanonicalEvent.participation_episodes must be an array")
        if any(
            not isinstance(item, ParticipationEpisode)
            for item in self.participation_episodes
        ):
            raise TypeError(
                "CanonicalEvent.participation_episodes must contain ParticipationEpisode objects"
            )
        object.__setattr__(self, "participation_episodes", tuple(self.participation_episodes))
        object.__setattr__(
            self,
            "claim_ids",
            tuple(sorted(set(_stable_id_tuple(self.claim_ids, "CanonicalEvent.claim_ids")))),
        )
        object.__setattr__(
            self,
            "adjudication_ids",
            tuple(
                sorted(
                    set(
                        _stable_id_tuple(
                            self.adjudication_ids, "CanonicalEvent.adjudication_ids"
                        )
                    )
                )
            ),
        )
        if self.geometry is not None:
            geometry = freeze_json(self.geometry)
            if not isinstance(geometry, Mapping):
                raise TypeError("Canonical event geometry must be a GeoJSON object")
            object.__setattr__(self, "geometry", geometry)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "aliases": sorted(set(self.aliases)),
            "parent_event_ids": sorted(set(self.parent_event_ids)),
            "child_event_ids": sorted(set(self.child_event_ids)),
            "participation_episodes": [
                episode.to_dict() for episode in self.participation_episodes
            ],
            "claim_ids": sorted(set(self.claim_ids)),
            "adjudication_ids": sorted(set(self.adjudication_ids)),
            "status": self.status,
        }
        if self.date_interval is not None:
            result["date_interval"] = self.date_interval.to_dict()
        if self.geometry is not None:
            result["geometry"] = canonicalize_json(self.geometry)
        if self.hced_candidate_id is not None:
            result["hced_candidate_id"] = self.hced_candidate_id
        if self.modern_location_country is not None:
            result["modern_location_country"] = self.modern_location_country
        if self.location_provenance is not None:
            result["location_provenance"] = self.location_provenance.to_dict()
        if self.source_ids:
            result["source_ids"] = list(self.source_ids)
        for name in ("event_type", "layer", "domain", "region"):
            value = getattr(self, name)
            if value is not None:
                result[name] = value
        return result

    @classmethod
    def from_dict(cls, raw: Any) -> "CanonicalEvent":
        if not isinstance(raw, dict):
            raise TypeError("CanonicalEvent must be a JSON object")
        parent_raw = raw["parent_event_ids"] if "parent_event_ids" in raw else []
        if isinstance(parent_raw, (str, bytes)) or not isinstance(parent_raw, (list, tuple)):
            raise TypeError("CanonicalEvent.parent_event_ids must be an array of strings")
        if raw.get("parent_event_id") is not None:
            if not isinstance(raw["parent_event_id"], str):
                raise TypeError("CanonicalEvent.parent_event_id must be a string or null")
            if not raw["parent_event_id"].strip():
                raise ValueError(
                    "CanonicalEvent.parent_event_id must be non-blank when supplied"
                )
            parent_raw = [*parent_raw, raw["parent_event_id"]]
        child_raw = raw["child_event_ids"] if "child_event_ids" in raw else []
        if isinstance(child_raw, (str, bytes)) or not isinstance(child_raw, (list, tuple)):
            raise TypeError("CanonicalEvent.child_event_ids must be an array of strings")
        episodes_raw = (
            raw["participation_episodes"] if "participation_episodes" in raw else []
        )
        if not isinstance(episodes_raw, (list, tuple)):
            raise TypeError("CanonicalEvent.participation_episodes must be an array")
        status = raw["status"] if "status" in raw else "proposed"
        if not isinstance(status, str):
            raise TypeError("CanonicalEvent.status must be a string")
        return cls(
            id=_required_nonblank_text(
                raw, "id", alias="event_id", model_name="CanonicalEvent"
            ),
            name=_required_nonblank_text(
                raw, "name", alias="canonical_name", model_name="CanonicalEvent"
            ),
            aliases=_string_tuple(
                raw["aliases"] if "aliases" in raw else [], "CanonicalEvent.aliases"
            ),
            parent_event_ids=_stable_id_tuple(
                parent_raw, "CanonicalEvent.parent_event_ids"
            ),
            child_event_ids=_stable_id_tuple(
                child_raw, "CanonicalEvent.child_event_ids"
            ),
            date_interval=(
                UncertainDateInterval.from_dict(raw["date_interval"])
                if raw.get("date_interval") is not None
                else None
            ),
            geometry=raw.get("geometry"),
            hced_candidate_id=_optional_text_or_none(
                raw, "hced_candidate_id", model_name="CanonicalEvent"
            ),
            modern_location_country=_optional_text_or_none(
                raw, "modern_location_country", model_name="CanonicalEvent"
            ),
            location_provenance=(
                LocationProvenance.from_dict(raw["location_provenance"])
                if raw.get("location_provenance") is not None
                else None
            ),
            source_ids=_stable_id_tuple(
                raw["source_ids"] if "source_ids" in raw else [],
                "CanonicalEvent.source_ids",
            ),
            participation_episodes=tuple(
                ParticipationEpisode.from_dict(item)
                for item in episodes_raw
            ),
            claim_ids=_stable_id_tuple(
                raw["claim_ids"] if "claim_ids" in raw else [],
                "CanonicalEvent.claim_ids",
            ),
            adjudication_ids=_stable_id_tuple(
                raw["adjudication_ids"] if "adjudication_ids" in raw else [],
                "CanonicalEvent.adjudication_ids",
            ),
            event_type=_optional_text_or_none(
                raw, "event_type", model_name="CanonicalEvent"
            ),
            layer=_optional_text_or_none(
                raw, "layer", model_name="CanonicalEvent"
            ),
            domain=_optional_text_or_none(
                raw, "domain", model_name="CanonicalEvent"
            ),
            region=_optional_text_or_none(
                raw, "region", model_name="CanonicalEvent"
            ),
            status=status,
        )
