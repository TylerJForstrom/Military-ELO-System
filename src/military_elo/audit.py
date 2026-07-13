from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .config import ModelConfig
from .models import (
    Entity,
    Event,
    OPERATIONAL_DIMENSIONS,
    Source,
    STRATEGIC_DIMENSIONS,
    TACTICAL_DIMENSIONS,
)


@dataclass(frozen=True)
class AuditIssue:
    severity: str
    code: str
    record_id: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "record_id": self.record_id,
            "message": self.message,
        }


def audit_dataset(
    entities: Iterable[Entity],
    events: Iterable[Event],
    sources: dict[str, Source],
    config: ModelConfig,
) -> list[AuditIssue]:
    entity_list = list(entities)
    event_list = list(events)
    issues: list[AuditIssue] = []
    entity_map = {item.id: item for item in entity_list}

    if len(entity_map) != len(entity_list):
        issues.append(AuditIssue("error", "duplicate_entity", "entities", "Entity ids must be unique"))
    if len({item.id for item in event_list}) != len(event_list):
        issues.append(AuditIssue("error", "duplicate_event", "events", "Event ids must be unique"))

    for entity in entity_list:
        if entity.end_year is not None and entity.end_year < entity.start_year:
            issues.append(
                AuditIssue("error", "invalid_entity_dates", entity.id, "end_year precedes start_year")
            )
        for predecessor in entity.predecessors:
            if predecessor == entity.id:
                issues.append(
                    AuditIssue("error", "self_predecessor", entity.id, "An entity cannot precede itself")
                )
            elif predecessor not in entity_map:
                issues.append(
                    AuditIssue("warning", "unknown_predecessor", entity.id, f"Unknown predecessor {predecessor}")
                )
        if not entity.source_ids:
            issues.append(
                AuditIssue("warning", "unsourced_entity", entity.id, "Entity boundary has no cited source")
            )

    valid_event_types = {"engagement", "campaign", "war"}
    valid_statuses = {"complete", "ongoing", "disputed", "excluded"}
    for event in event_list:
        if event.event_type not in valid_event_types:
            issues.append(
                AuditIssue("error", "invalid_event_type", event.id, f"Unknown type {event.event_type}")
            )
        if event.status not in valid_statuses:
            issues.append(AuditIssue("error", "invalid_status", event.id, f"Unknown status {event.status}"))
        if event.end_year < event.year:
            issues.append(AuditIssue("error", "invalid_event_dates", event.id, "end_year precedes year"))
        if not 0 <= event.confidence <= 1:
            issues.append(AuditIssue("error", "invalid_confidence", event.id, "confidence must be 0..1"))
        if not 0 <= event.decisiveness <= 1:
            issues.append(AuditIssue("error", "invalid_decisiveness", event.id, "decisiveness must be 0..1"))
        if event.geographic_scope is not None and not 0 <= event.geographic_scope <= 1:
            issues.append(
                AuditIssue("error", "invalid_geographic_scope", event.id, "geographic_scope must be 0..1")
            )
        if len({participant.side for participant in event.participants}) < 2:
            issues.append(AuditIssue("error", "single_side", event.id, "At least two sides are required"))
        if event.status == "complete" and not event.source_ids:
            issues.append(AuditIssue("error", "unsourced_event", event.id, "Rated events require a source"))
        for source_id in event.source_ids:
            if source_id not in sources:
                issues.append(
                    AuditIssue("error", "unknown_source", event.id, f"Unknown source id {source_id}")
                )
        expected_dimensions = {
            "tactical": TACTICAL_DIMENSIONS,
            "operational": OPERATIONAL_DIMENSIONS,
            "strategic": STRATEGIC_DIMENSIONS,
        }[event.track]
        if event.track == "tactical":
            profile = config.tactical_weights
        elif event.track == "operational":
            profile = config.operational_weights
        else:
            profile = config.strategic_weights.get(
                event.war_type, config.strategic_weights["interstate_limited"]
            )
        for participant in event.participants:
            entity = entity_map.get(participant.entity_id)
            if entity is None:
                issues.append(
                    AuditIssue("error", "unknown_participant", event.id, f"Unknown entity {participant.entity_id}")
                )
                continue
            if event.end_year < entity.start_year or (
                entity.end_year is not None and event.year > entity.end_year
            ):
                issues.append(
                    AuditIssue(
                        "error",
                        "outside_entity_lifespan",
                        event.id,
                        f"{entity.name} is not active during {event.year}..{event.end_year}",
                    )
                )
            if not 0 < participant.contribution <= 1:
                issues.append(
                    AuditIssue("error", "invalid_contribution", event.id, "contribution must be in (0, 1]")
                )
            for dimension, value in participant.outcome.items():
                if dimension not in expected_dimensions:
                    issues.append(
                        AuditIssue(
                            "warning",
                            "unexpected_dimension",
                            event.id,
                            f"{dimension} is not used for {event.track} events",
                        )
                    )
                if not 0 <= value <= 1:
                    issues.append(
                        AuditIssue("error", "invalid_outcome", event.id, f"{dimension} must be 0..1")
                    )
            missing = [dimension for dimension in profile if dimension not in participant.outcome]
            if missing:
                issues.append(
                    AuditIssue(
                        "warning",
                        "partial_outcome_vector",
                        event.id,
                        f"{participant.entity_id} lacks dimensions: {', '.join(missing)}",
                    )
                )
            if participant.evidence_confidence is not None and not 0 <= participant.evidence_confidence <= 1:
                issues.append(
                    AuditIssue(
                        "error",
                        "invalid_participant_confidence",
                        event.id,
                        "participant evidence confidence must be 0..1",
                    )
                )
            for field_name, value in (
                ("stakes", participant.stakes),
                ("national_scale", participant.national_scale),
            ):
                if value is not None and not 0 <= value <= 1:
                    issues.append(
                        AuditIssue(
                            "error",
                            f"invalid_participant_{field_name}",
                            event.id,
                            f"participant {field_name} must be 0..1",
                        )
                    )

    return issues


def has_errors(issues: Iterable[AuditIssue]) -> bool:
    return any(issue.severity == "error" for issue in issues)
