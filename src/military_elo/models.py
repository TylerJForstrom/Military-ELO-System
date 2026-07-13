from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
        )


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    publisher: str = ""
    license: str = ""
    source_type: str = "secondary"
    accessed: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Source":
        return cls(
            id=str(raw["id"]),
            title=str(raw["title"]),
            url=str(raw["url"]),
            publisher=str(raw.get("publisher", "")),
            license=str(raw.get("license", "")),
            source_type=str(raw.get("source_type", "secondary")),
            accessed=str(raw.get("accessed", "")),
        )


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

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Participant":
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
        )


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
            source_ids=tuple(raw.get("source_ids", [])),
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
        )
