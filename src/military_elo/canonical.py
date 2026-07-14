"""Claim-neutral event identity, uncertain dates, and participation intervals.

Machine dates use signed BCE/CE years with no year zero.  Month/day validation
uses the proleptic Gregorian calendar as a storage convention, without implying
that historical sources used that calendar contemporaneously.  These fields are
evidence data only; the rating engine does not interpret them in this workstream.
"""

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from .claims import canonicalize_json


DateValue = int | str
DateKey = tuple[int, int, int]


_DATE_PATTERN = re.compile(
    r"(?P<year>-?[0-9]{1,6})(?:-(?P<month>[0-9]{2})(?:-(?P<day>[0-9]{2}))?)?"
)


def _string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value == ():
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise TypeError(f"{field_name} must be an array of strings")
    if any(not isinstance(item, str) for item in value):
        raise TypeError(f"{field_name} must contain only strings")
    return tuple(value)


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


def _date_validation_error(value: DateValue) -> str | None:
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
        if isinstance(raw, (str, int)) and not isinstance(raw, bool):
            return cls.exact(raw)
        if not isinstance(raw, dict):
            raise TypeError("UncertainDate must be an object, signed year, or date string")
        return cls(
            low=raw.get("low", raw.get("earliest")),
            best=raw.get("best"),
            high=raw.get("high", raw.get("latest")),
            precision=raw.get("precision", "unknown"),
        )


@dataclass(frozen=True)
class UncertainDateInterval:
    """Independently uncertain start and end dates for an event."""

    start: UncertainDate
    end: UncertainDate

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
    def from_dict(cls, raw: dict[str, Any]) -> "UncertainDateInterval":
        if "start" in raw or "end" in raw:
            if "start" not in raw or "end" not in raw:
                raise ValueError("date_interval requires both start and end")
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
                    set(_string_tuple(self.claim_ids, "ParticipationEpisode.claim_ids"))
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
    def from_dict(cls, raw: dict[str, Any]) -> "ParticipationEpisode":
        entry_raw = raw.get("entry", raw.get("entry_date"))
        exit_raw = raw.get("exit", raw.get("exit_date"))
        return cls(
            id=str(raw.get("id", raw.get("episode_id", ""))),
            entity_id=str(raw.get("entity_id", "")),
            side=str(raw.get("side", "")),
            role=str(raw.get("role", "unknown")),
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
            claim_ids=_string_tuple(
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
    geometry: dict[str, Any] | None = None
    participation_episodes: tuple[ParticipationEpisode, ...] = field(default_factory=tuple)
    claim_ids: tuple[str, ...] = field(default_factory=tuple)
    adjudication_ids: tuple[str, ...] = field(default_factory=tuple)
    event_type: str | None = None
    layer: str | None = None
    domain: str | None = None
    region: str | None = None
    status: str = "proposed"

    def __post_init__(self) -> None:
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
                        _string_tuple(
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
                        _string_tuple(
                            self.child_event_ids, "CanonicalEvent.child_event_ids"
                        )
                    )
                )
            ),
        )
        if not isinstance(self.participation_episodes, (list, tuple)):
            raise TypeError("CanonicalEvent.participation_episodes must be an array")
        object.__setattr__(self, "participation_episodes", tuple(self.participation_episodes))
        object.__setattr__(
            self,
            "claim_ids",
            tuple(sorted(set(_string_tuple(self.claim_ids, "CanonicalEvent.claim_ids")))),
        )
        object.__setattr__(
            self,
            "adjudication_ids",
            tuple(
                sorted(
                    set(
                        _string_tuple(
                            self.adjudication_ids, "CanonicalEvent.adjudication_ids"
                        )
                    )
                )
            ),
        )
        if self.geometry is not None:
            geometry = canonicalize_json(deepcopy(self.geometry))
            if not isinstance(geometry, dict):
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
        for name in ("event_type", "layer", "domain", "region"):
            value = getattr(self, name)
            if value is not None:
                result[name] = value
        return result

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CanonicalEvent":
        parent_raw = raw["parent_event_ids"] if "parent_event_ids" in raw else []
        if isinstance(parent_raw, (str, bytes)) or not isinstance(parent_raw, (list, tuple)):
            raise TypeError("CanonicalEvent.parent_event_ids must be an array of strings")
        if raw.get("parent_event_id") is not None:
            if not isinstance(raw["parent_event_id"], str):
                raise TypeError("CanonicalEvent.parent_event_id must be a string or null")
            parent_raw = [*parent_raw, raw["parent_event_id"]]
        child_raw = raw["child_event_ids"] if "child_event_ids" in raw else []
        if isinstance(child_raw, (str, bytes)) or not isinstance(child_raw, (list, tuple)):
            raise TypeError("CanonicalEvent.child_event_ids must be an array of strings")
        episodes_raw = (
            raw["participation_episodes"] if "participation_episodes" in raw else []
        )
        if not isinstance(episodes_raw, (list, tuple)):
            raise TypeError("CanonicalEvent.participation_episodes must be an array")
        return cls(
            id=str(raw.get("id", raw.get("event_id", ""))),
            name=str(raw.get("name", raw.get("canonical_name", ""))),
            aliases=_string_tuple(
                raw["aliases"] if "aliases" in raw else [], "CanonicalEvent.aliases"
            ),
            parent_event_ids=_string_tuple(
                parent_raw, "CanonicalEvent.parent_event_ids"
            ),
            child_event_ids=_string_tuple(
                child_raw, "CanonicalEvent.child_event_ids"
            ),
            date_interval=(
                UncertainDateInterval.from_dict(raw["date_interval"])
                if raw.get("date_interval") is not None
                else None
            ),
            geometry=raw.get("geometry"),
            participation_episodes=tuple(
                ParticipationEpisode.from_dict(item)
                for item in episodes_raw
            ),
            claim_ids=_string_tuple(
                raw["claim_ids"] if "claim_ids" in raw else [],
                "CanonicalEvent.claim_ids",
            ),
            adjudication_ids=_string_tuple(
                raw["adjudication_ids"] if "adjudication_ids" in raw else [],
                "CanonicalEvent.adjudication_ids",
            ),
            event_type=str(raw["event_type"]) if raw.get("event_type") is not None else None,
            layer=str(raw["layer"]) if raw.get("layer") is not None else None,
            domain=str(raw["domain"]) if raw.get("domain") is not None else None,
            region=str(raw["region"]) if raw.get("region") is not None else None,
            status=str(raw.get("status", "proposed")),
        )
