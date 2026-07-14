from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .canonical import (
    ParticipationEpisode,
    UncertainDate,
    UncertainDateInterval,
    freeze_json,
)
from .claims import canonicalize_json


TACTICAL_DIMENSIONS = {
    "battlefield_control",
    "mission_objective",
    "force_preservation",
    "positional_gain",
}

OPERATIONAL_DIMENSIONS = {
    "campaign_objective",
    "theater_control",
    "force_preservation",
    "tempo_initiative",
    "logistics_sustainment",
}

STRATEGIC_DIMENSIONS = {
    "battlefield_outcome",
    "political_objectives",
    "territorial_outcome",
    "sovereignty_survival",
    "settlement_durability",
    "force_preservation",
}

SOURCE_EVIDENCE_ROLES = frozenset(
    {
        "curated_reference_pending_claim_level_outcome_locator",
        "derived_project_continuity_convention",
        "identity_boundary_or_context_reference",
        "identity_crosswalk",
        "identity_registry",
        "outcome",
        "outcome_consistency_crosscheck",
    }
)

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


def _canonical_stable_id_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    result = _stable_id_tuple(value, field_name)
    if any(item != item.strip() for item in result):
        raise ValueError(f"{field_name} must not contain surrounding whitespace")
    if result != tuple(sorted(set(result))):
        raise ValueError(f"{field_name} must be sorted and deduplicated")
    return result


@dataclass(frozen=True)
class Entity:
    id: str
    name: str
    kind: str
    start_year: int
    end_year: int | None = None
    region: str = "Unknown"
    aliases: tuple[str, ...] = ()
    predecessors: tuple[str, ...] = ()
    continuity_note: str = ""
    source_ids: tuple[str, ...] = ()
    claim_ids: tuple[str, ...] = ()
    adjudication_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "claim_ids",
            tuple(sorted(set(_stable_id_tuple(self.claim_ids, "Entity.claim_ids")))),
        )
        object.__setattr__(
            self,
            "adjudication_ids",
            tuple(
                sorted(
                    set(_stable_id_tuple(self.adjudication_ids, "Entity.adjudication_ids"))
                )
            ),
        )

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Entity":
        return cls(
            id=str(raw["id"]),
            name=str(raw["name"]),
            kind=str(raw.get("kind", "polity")),
            start_year=int(raw["start_year"]),
            end_year=int(raw["end_year"]) if raw.get("end_year") is not None else None,
            region=str(raw.get("region", "Unknown")),
            aliases=tuple(raw.get("aliases", [])),
            predecessors=tuple(raw.get("predecessors", [])),
            continuity_note=str(raw.get("continuity_note", "")),
            source_ids=tuple(raw.get("source_ids", [])),
            claim_ids=_stable_id_tuple(
                raw["claim_ids"] if "claim_ids" in raw else [],
                "Entity.claim_ids",
            ),
            adjudication_ids=_stable_id_tuple(
                raw["adjudication_ids"] if "adjudication_ids" in raw else [],
                "Entity.adjudication_ids",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "region": self.region,
            "aliases": list(self.aliases),
            "predecessors": list(self.predecessors),
            "continuity_note": self.continuity_note,
            "source_ids": list(self.source_ids),
        }
        if self.claim_ids:
            result["claim_ids"] = sorted(set(self.claim_ids))
        if self.adjudication_ids:
            result["adjudication_ids"] = sorted(set(self.adjudication_ids))
        return result


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    publisher: str = ""
    license: str = ""
    source_type: str = "secondary"
    accessed: str = ""
    source_family_id: str = ""
    evidence_roles: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.source_family_id, str):
            raise TypeError("Source.source_family_id must be a string")
        roles = _stable_id_tuple(self.evidence_roles, "Source.evidence_roles")
        has_family = bool(self.source_family_id)
        has_roles = bool(roles)
        if has_family != has_roles:
            raise ValueError(
                "Source.source_family_id and Source.evidence_roles must be supplied together"
            )
        if not has_family:
            object.__setattr__(self, "evidence_roles", ())
            return

        if not self.source_family_id.strip():
            raise ValueError("Source.source_family_id must be non-blank")
        if self.source_family_id != self.source_family_id.strip():
            raise ValueError(
                "Source.source_family_id must not contain surrounding whitespace"
            )
        unknown_roles = sorted(set(roles) - SOURCE_EVIDENCE_ROLES)
        if unknown_roles:
            allowed = ", ".join(sorted(SOURCE_EVIDENCE_ROLES))
            raise ValueError(
                "Source.evidence_roles contains non-canonical role(s) "
                f"{', '.join(unknown_roles)}; allowed roles: {allowed}"
            )
        object.__setattr__(self, "evidence_roles", tuple(sorted(set(roles))))

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Source":
        has_family = "source_family_id" in raw
        has_roles = "evidence_roles" in raw
        if has_family != has_roles:
            raise ValueError(
                "Source.source_family_id and Source.evidence_roles must be supplied together"
            )
        source_family_id = raw.get("source_family_id", "")
        evidence_roles = raw.get("evidence_roles", ())
        if has_family:
            if not isinstance(source_family_id, str):
                raise TypeError("Source.source_family_id must be a string")
            if not source_family_id.strip():
                raise ValueError("Source.source_family_id must be non-blank")
            parsed_roles = _stable_id_tuple(
                evidence_roles, "Source.evidence_roles"
            )
            if not parsed_roles:
                raise ValueError("Source.evidence_roles must be non-empty when supplied")
            evidence_roles = parsed_roles
        return cls(
            id=str(raw["id"]),
            title=str(raw["title"]),
            url=str(raw["url"]),
            publisher=str(raw.get("publisher", "")),
            license=str(raw.get("license", "")),
            source_type=str(raw.get("source_type", "secondary")),
            accessed=str(raw.get("accessed", "")),
            source_family_id=source_family_id,
            evidence_roles=evidence_roles,
        )

    def to_dict(self) -> dict[str, Any]:
        result = {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "publisher": self.publisher,
            "license": self.license,
            "source_type": self.source_type,
            "accessed": self.accessed,
        }
        if self.source_family_id:
            result["source_family_id"] = self.source_family_id
            result["evidence_roles"] = list(self.evidence_roles)
        return result


@dataclass(frozen=True)
class Participant:
    entity_id: str
    side: str
    role: str = "primary"
    contribution: float = 1.0
    outcome: dict[str, float] = field(default_factory=dict)
    result_class: str | None = None
    force_size: float | None = None
    home_advantage: float = 0.0
    evidence_confidence: float | None = None
    stakes: float | None = None
    national_scale: float | None = None
    termination: str = "unknown"
    note: str = ""
    entry: UncertainDate | None = None
    exit: UncertainDate | None = None
    objectives: tuple[str, ...] = ()
    claim_ids: tuple[str, ...] = ()
    adjudication_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("entry", "exit"):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, UncertainDate):
                raise TypeError(
                    f"Participant.{field_name} must be an UncertainDate or null"
                )
        object.__setattr__(
            self,
            "objectives",
            _string_tuple(self.objectives, "Participant.objectives"),
        )
        object.__setattr__(
            self,
            "claim_ids",
            tuple(sorted(set(_stable_id_tuple(self.claim_ids, "Participant.claim_ids")))),
        )
        object.__setattr__(
            self,
            "adjudication_ids",
            tuple(
                sorted(
                    set(
                        _stable_id_tuple(
                            self.adjudication_ids, "Participant.adjudication_ids"
                        )
                    )
                )
            ),
        )

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Participant":
        if "entry" in raw and "entry_date" in raw:
            raise ValueError("Participant cannot contain both entry and entry_date")
        if "exit" in raw and "exit_date" in raw:
            raise ValueError("Participant cannot contain both exit and exit_date")
        entry_raw = raw.get("entry", raw.get("entry_date"))
        exit_raw = raw.get("exit", raw.get("exit_date"))
        return cls(
            entity_id=str(raw["entity_id"]),
            side=str(raw["side"]),
            role=str(raw.get("role", "primary")),
            contribution=float(raw.get("contribution", 1.0)),
            outcome={str(k): float(v) for k, v in raw.get("outcome", {}).items()},
            result_class=raw.get("result_class"),
            force_size=float(raw["force_size"]) if raw.get("force_size") is not None else None,
            home_advantage=float(raw.get("home_advantage", 0.0)),
            evidence_confidence=(
                float(raw["evidence_confidence"])
                if raw.get("evidence_confidence") is not None
                else None
            ),
            stakes=float(raw["stakes"]) if raw.get("stakes") is not None else None,
            national_scale=(
                float(raw["national_scale"])
                if raw.get("national_scale") is not None
                else None
            ),
            termination=str(raw.get("termination", "unknown")),
            note=str(raw.get("note", "")),
            entry=UncertainDate.from_dict(entry_raw) if entry_raw is not None else None,
            exit=UncertainDate.from_dict(exit_raw) if exit_raw is not None else None,
            objectives=_string_tuple(
                raw["objectives"] if "objectives" in raw else [],
                "Participant.objectives",
            ),
            claim_ids=_stable_id_tuple(
                raw["claim_ids"] if "claim_ids" in raw else [],
                "Participant.claim_ids",
            ),
            adjudication_ids=_stable_id_tuple(
                raw["adjudication_ids"] if "adjudication_ids" in raw else [],
                "Participant.adjudication_ids",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "entity_id": self.entity_id,
            "side": self.side,
            "role": self.role,
            "contribution": self.contribution,
            "outcome": dict(sorted(self.outcome.items())),
            "result_class": self.result_class,
            "force_size": self.force_size,
            "home_advantage": self.home_advantage,
            "evidence_confidence": self.evidence_confidence,
            "stakes": self.stakes,
            "national_scale": self.national_scale,
            "termination": self.termination,
            "note": self.note,
        }
        if self.entry is not None:
            result["entry"] = self.entry.to_dict()
        if self.exit is not None:
            result["exit"] = self.exit.to_dict()
        if self.objectives:
            result["objectives"] = list(self.objectives)
        if self.claim_ids:
            result["claim_ids"] = sorted(set(self.claim_ids))
        if self.adjudication_ids:
            result["adjudication_ids"] = sorted(set(self.adjudication_ids))
        return result


@dataclass(frozen=True)
class Event:
    id: str
    name: str
    year: int
    end_year: int
    event_type: str
    war_type: str
    scale: str
    stakes: str
    decisiveness: float
    confidence: float
    participants: tuple[Participant, ...]
    source_ids: tuple[str, ...]
    parent_event_id: str | None = None
    status: str = "complete"
    sequence: int = 0
    summary: str = ""
    date_precision: str = "year"
    geographic_scope: float | None = None
    domain: str = "mixed"
    cluster_id: str | None = None
    aliases: tuple[str, ...] = ()
    parent_event_ids: tuple[str, ...] = ()
    child_event_ids: tuple[str, ...] = ()
    date_interval: UncertainDateInterval | None = None
    geometry: Mapping[str, Any] | None = None
    participation_episodes: tuple[ParticipationEpisode, ...] = ()
    claim_ids: tuple[str, ...] = ()
    adjudication_ids: tuple[str, ...] = ()
    outcome_source_ids: tuple[str, ...] = ()
    outcome_source_family_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.parent_event_id is not None:
            if not isinstance(self.parent_event_id, str):
                raise TypeError("Event.parent_event_id must be a string or null")
            if not self.parent_event_id.strip():
                raise ValueError(
                    "Event.parent_event_id must be non-blank when supplied"
                )
        if self.date_interval is not None and not isinstance(
            self.date_interval, UncertainDateInterval
        ):
            raise TypeError(
                "Event.date_interval must be an UncertainDateInterval or null"
            )
        object.__setattr__(
            self,
            "aliases",
            tuple(sorted(set(_string_tuple(self.aliases, "Event.aliases")))),
        )
        object.__setattr__(
            self,
            "parent_event_ids",
            tuple(
                sorted(
                    set(_stable_id_tuple(self.parent_event_ids, "Event.parent_event_ids"))
                )
            ),
        )
        object.__setattr__(
            self,
            "child_event_ids",
            tuple(
                sorted(
                    set(_stable_id_tuple(self.child_event_ids, "Event.child_event_ids"))
                )
            ),
        )
        if not isinstance(self.participation_episodes, (list, tuple)):
            raise TypeError("Event.participation_episodes must be an array")
        if any(
            not isinstance(item, ParticipationEpisode)
            for item in self.participation_episodes
        ):
            raise TypeError(
                "Event.participation_episodes must contain ParticipationEpisode objects"
            )
        object.__setattr__(self, "participation_episodes", tuple(self.participation_episodes))
        object.__setattr__(
            self,
            "claim_ids",
            tuple(sorted(set(_stable_id_tuple(self.claim_ids, "Event.claim_ids")))),
        )
        object.__setattr__(
            self,
            "adjudication_ids",
            tuple(
                sorted(
                    set(_stable_id_tuple(self.adjudication_ids, "Event.adjudication_ids"))
                )
            ),
        )
        source_ids = _stable_id_tuple(self.source_ids, "Event.source_ids")
        outcome_source_ids = _canonical_stable_id_tuple(
            self.outcome_source_ids,
            "Event.outcome_source_ids",
        )
        outcome_source_family_ids = _canonical_stable_id_tuple(
            self.outcome_source_family_ids,
            "Event.outcome_source_family_ids",
        )
        if bool(outcome_source_ids) != bool(outcome_source_family_ids):
            raise ValueError(
                "Event.outcome_source_ids and Event.outcome_source_family_ids "
                "must be populated together"
            )
        missing_outcome_sources = sorted(set(outcome_source_ids) - set(source_ids))
        if missing_outcome_sources:
            raise ValueError(
                "Event.outcome_source_ids must be a subset of Event.source_ids; "
                f"missing: {', '.join(missing_outcome_sources)}"
            )
        object.__setattr__(self, "source_ids", source_ids)
        object.__setattr__(self, "outcome_source_ids", outcome_source_ids)
        object.__setattr__(
            self, "outcome_source_family_ids", outcome_source_family_ids
        )
        if self.geometry is not None:
            geometry = freeze_json(self.geometry)
            if not isinstance(geometry, Mapping):
                raise TypeError("Event geometry must be a GeoJSON object")
            object.__setattr__(self, "geometry", geometry)

    @property
    def track(self) -> str:
        if self.event_type == "engagement":
            return "tactical"
        if self.event_type == "campaign":
            return "operational"
        return "strategic"

    @property
    def sort_key(self) -> tuple[int, int, str]:
        return (self.end_year, self.sequence, self.id)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Event":
        year = int(raw["year"])
        has_outcome_sources = "outcome_source_ids" in raw
        has_outcome_families = "outcome_source_family_ids" in raw
        if has_outcome_sources != has_outcome_families:
            raise ValueError(
                "Event.outcome_source_ids and Event.outcome_source_family_ids "
                "must be supplied together"
            )
        outcome_source_ids = _canonical_stable_id_tuple(
            raw["outcome_source_ids"] if has_outcome_sources else [],
            "Event.outcome_source_ids",
        )
        outcome_source_family_ids = _canonical_stable_id_tuple(
            raw["outcome_source_family_ids"] if has_outcome_families else [],
            "Event.outcome_source_family_ids",
        )
        if has_outcome_sources and (
            not outcome_source_ids or not outcome_source_family_ids
        ):
            raise ValueError(
                "Event.outcome_source_ids and Event.outcome_source_family_ids "
                "must be populated together"
            )
        episodes_raw = (
            raw["participation_episodes"] if "participation_episodes" in raw else []
        )
        if not isinstance(episodes_raw, (list, tuple)):
            raise TypeError("Event.participation_episodes must be an array")
        return cls(
            id=str(raw["id"]),
            name=str(raw["name"]),
            year=year,
            end_year=int(raw.get("end_year", year)),
            event_type=str(raw.get("event_type", raw.get("type", "war"))),
            war_type=str(raw.get("war_type", "interstate_limited")),
            scale=str(raw.get("scale", "battle")),
            stakes=str(raw.get("stakes", "limited")),
            decisiveness=float(raw.get("decisiveness", 0.5)),
            confidence=float(raw.get("confidence", 0.5)),
            participants=tuple(Participant.from_dict(p) for p in raw["participants"]),
            source_ids=_stable_id_tuple(
                raw["source_ids"] if "source_ids" in raw else [],
                "Event.source_ids",
            ),
            parent_event_id=raw.get("parent_event_id"),
            status=str(raw.get("status", "complete")),
            sequence=int(raw.get("sequence", 0)),
            summary=str(raw.get("summary", "")),
            date_precision=str(raw.get("date_precision", "year")),
            geographic_scope=(
                float(raw["geographic_scope"])
                if raw.get("geographic_scope") is not None
                else None
            ),
            domain=str(raw.get("domain", "mixed")),
            cluster_id=raw.get("cluster_id"),
            aliases=_string_tuple(
                raw["aliases"] if "aliases" in raw else [], "Event.aliases"
            ),
            parent_event_ids=_stable_id_tuple(
                raw["parent_event_ids"] if "parent_event_ids" in raw else [],
                "Event.parent_event_ids",
            ),
            child_event_ids=_stable_id_tuple(
                raw["child_event_ids"] if "child_event_ids" in raw else [],
                "Event.child_event_ids",
            ),
            date_interval=(
                UncertainDateInterval.from_dict(raw["date_interval"])
                if raw.get("date_interval") is not None
                else None
            ),
            geometry=raw["geometry"] if raw.get("geometry") is not None else None,
            participation_episodes=tuple(
                ParticipationEpisode.from_dict(item)
                for item in episodes_raw
            ),
            claim_ids=_stable_id_tuple(
                raw["claim_ids"] if "claim_ids" in raw else [], "Event.claim_ids"
            ),
            adjudication_ids=_stable_id_tuple(
                raw["adjudication_ids"] if "adjudication_ids" in raw else [],
                "Event.adjudication_ids",
            ),
            outcome_source_ids=outcome_source_ids,
            outcome_source_family_ids=outcome_source_family_ids,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "year": self.year,
            "end_year": self.end_year,
            "event_type": self.event_type,
            "war_type": self.war_type,
            "scale": self.scale,
            "stakes": self.stakes,
            "decisiveness": self.decisiveness,
            "confidence": self.confidence,
            "participants": [participant.to_dict() for participant in self.participants],
            "source_ids": list(self.source_ids),
            "parent_event_id": self.parent_event_id,
            "status": self.status,
            "sequence": self.sequence,
            "summary": self.summary,
            "date_precision": self.date_precision,
            "geographic_scope": self.geographic_scope,
            "domain": self.domain,
            "cluster_id": self.cluster_id,
        }
        if self.aliases:
            result["aliases"] = sorted(set(self.aliases))
        if self.parent_event_ids:
            result["parent_event_ids"] = sorted(set(self.parent_event_ids))
        if self.child_event_ids:
            result["child_event_ids"] = sorted(set(self.child_event_ids))
        if self.date_interval is not None:
            result["date_interval"] = self.date_interval.to_dict()
        if self.geometry is not None:
            result["geometry"] = canonicalize_json(self.geometry)
        if self.participation_episodes:
            result["participation_episodes"] = [
                episode.to_dict() for episode in self.participation_episodes
            ]
        if self.claim_ids:
            result["claim_ids"] = sorted(set(self.claim_ids))
        if self.adjudication_ids:
            result["adjudication_ids"] = sorted(set(self.adjudication_ids))
        if self.outcome_source_ids:
            result["outcome_source_ids"] = list(self.outcome_source_ids)
            result["outcome_source_family_ids"] = list(
                self.outcome_source_family_ids
            )
        return result
