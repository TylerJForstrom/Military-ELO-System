from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Iterable
from urllib.parse import urlparse

from .canonical import (
    CanonicalEvent,
    ParticipationEpisode,
    UncertainDate,
    UncertainDateInterval,
    date_bounds,
    geometry_validation_error,
)
from .claims import (
    CLAIM_STATUSES,
    Claim,
    EvidenceLink,
    SourceLocator,
    canonicalize_json,
    find_disagreements,
)
from .config import ModelConfig
from .models import (
    Entity,
    Event,
    OPERATIONAL_DIMENSIONS,
    Source,
    STRATEGIC_DIMENSIONS,
    TACTICAL_DIMENSIONS,
)
from .review import (
    Adjudication,
    active_adjudications,
    adjudication_history_errors,
    locator_url_is_valid,
    resolve_claims,
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


def _audit_outcome_source_contract(
    event: Event, sources: Mapping[str, Source]
) -> list[AuditIssue]:
    """Validate the explicit event-to-outcome-source contract when supplied."""

    raw_source_ids = getattr(event, "outcome_source_ids", ())
    raw_family_ids = getattr(event, "outcome_source_family_ids", ())
    source_contract_supplied = bool(raw_source_ids)
    family_contract_supplied = bool(raw_family_ids)
    if not source_contract_supplied and not family_contract_supplied:
        return []

    issues: list[AuditIssue] = []
    if source_contract_supplied != family_contract_supplied:
        issues.append(
            AuditIssue(
                "error",
                "unpaired_outcome_source_contract",
                event.id,
                "outcome_source_ids and outcome_source_family_ids must be supplied together",
            )
        )

    def canonical_values(value: object, field_name: str) -> tuple[str, ...]:
        if not isinstance(value, (list, tuple)):
            issues.append(
                AuditIssue(
                    "error",
                    f"noncanonical_{field_name}",
                    event.id,
                    f"{field_name} must be an exact deduplicated array of stable IDs",
                )
            )
            return ()
        values = tuple(
            item
            for item in value
            if isinstance(item, str) and item and item == item.strip()
        )
        if len(values) != len(value) or values != tuple(sorted(set(values))):
            issues.append(
                AuditIssue(
                    "error",
                    f"noncanonical_{field_name}",
                    event.id,
                    f"{field_name} must be sorted, non-blank, and deduplicated exactly",
                )
            )
        return values

    outcome_source_ids = canonical_values(raw_source_ids, "outcome_source_ids")
    declared_family_ids = canonical_values(
        raw_family_ids, "outcome_source_family_ids"
    )
    declared_family_set = set(declared_family_ids)

    linked_source_ids = set(event.source_ids)
    derived_family_ids: set[str] = set()
    for source_id in outcome_source_ids:
        if source_id not in linked_source_ids:
            issues.append(
                AuditIssue(
                    "error",
                    "outcome_source_not_linked",
                    event.id,
                    f"Outcome source {source_id} is not present in event.source_ids",
                )
            )

        source = sources.get(source_id)
        if source is None:
            issues.append(
                AuditIssue(
                    "error",
                    "unknown_outcome_source",
                    event.id,
                    f"Unknown outcome source id {source_id}",
                )
            )
            continue

        evidence_roles = getattr(source, "evidence_roles", ())
        if not isinstance(evidence_roles, (list, tuple, set)) or "outcome" not in {
            str(role).strip().casefold() for role in evidence_roles
        }:
            issues.append(
                AuditIssue(
                    "error",
                    "outcome_source_missing_outcome_role",
                    event.id,
                    f"Outcome source {source_id} must declare outcome in evidence_roles",
                )
            )

        source_family_id = getattr(source, "source_family_id", "")
        if (
            isinstance(source_family_id, str)
            and source_family_id.strip()
            and source_family_id == source_family_id.strip()
        ):
            derived_family_ids.add(source_family_id)
        else:
            issues.append(
                AuditIssue(
                    "error",
                    "outcome_source_missing_family",
                    event.id,
                    f"Outcome source {source_id} must declare source_family_id",
                )
            )

    if declared_family_set != derived_family_ids:
        issues.append(
            AuditIssue(
                "error",
                "outcome_source_family_set_mismatch",
                event.id,
                (
                    "Declared outcome_source_family_ids must exactly equal the "
                    "families derived from outcome_source_ids"
                ),
            )
        )

    return issues


def audit_dataset(
    entities: Iterable[Entity],
    events: Iterable[Event],
    sources: dict[str, Source],
    config: ModelConfig,
    *,
    claims: Iterable[Claim] = (),
    evidence_links: Iterable[EvidenceLink] = (),
    adjudications: Iterable[Adjudication] = (),
    canonical_events: Iterable[CanonicalEvent] = (),
) -> list[AuditIssue]:
    entity_list = list(entities)
    event_list = list(events)
    claim_list = list(claims)
    evidence_link_list = list(evidence_links)
    adjudication_list = list(adjudications)
    canonical_event_list = list(canonical_events)
    explicit_canonical_ids = {event.id for event in canonical_event_list}
    explicit_canonical_by_id: dict[str, CanonicalEvent] = {}
    for canonical_event in canonical_event_list:
        explicit_canonical_by_id.setdefault(canonical_event.id, canonical_event)
    embedded_canonical_events: list[CanonicalEvent] = []
    legacy_intervals_by_id: dict[str, UncertainDateInterval] = {}
    issues: list[AuditIssue] = []
    entity_map = {item.id: item for item in entity_list}
    event_ids = {item.id for item in event_list}
    known_event_ids = event_ids | explicit_canonical_ids
    claim_ids = {item.id for item in claim_list}
    adjudication_by_id: dict[str, Adjudication] = {}
    for adjudication in adjudication_list:
        adjudication_by_id.setdefault(adjudication.id, adjudication)

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
        for claim_id in entity.claim_ids:
            if claim_id not in claim_ids:
                issues.append(
                    AuditIssue(
                        "error",
                        "unknown_entity_claim",
                        entity.id,
                        f"Unknown claim {claim_id}",
                    )
                )
        for adjudication_id in entity.adjudication_ids:
            adjudication = adjudication_by_id.get(adjudication_id)
            if adjudication is None:
                issues.append(
                    AuditIssue(
                        "error",
                        "unknown_entity_adjudication",
                        entity.id,
                        f"Unknown adjudication {adjudication_id}",
                    )
                )
            elif adjudication.claim_id not in entity.claim_ids:
                issues.append(
                    AuditIssue(
                        "error",
                        "entity_adjudication_claim_mismatch",
                        entity.id,
                        (
                            f"Adjudication {adjudication_id} resolves claim "
                            f"{adjudication.claim_id}, which is not attached to this entity"
                        ),
                    )
                )

    valid_event_types = {"engagement", "campaign", "war"}
    valid_statuses = {"complete", "ongoing", "disputed", "excluded"}
    for event in event_list:
        event_attachment_claim_ids = set(event.claim_ids)
        for episode in event.participation_episodes:
            event_attachment_claim_ids.update(episode.claim_ids)
        valid_parent_event_id: str | None = None
        if event.parent_event_id is not None and (
            not isinstance(event.parent_event_id, str)
            or not event.parent_event_id.strip()
        ):
            issues.append(
                AuditIssue(
                    "error",
                    "invalid_parent_event_id",
                    event.id,
                    "parent_event_id must be a non-blank string or null",
                )
            )
        elif isinstance(event.parent_event_id, str):
            valid_parent_event_id = event.parent_event_id
        if valid_parent_event_id == event.id:
            issues.append(
                AuditIssue("error", "self_parent_event", event.id, "Event cannot be its own parent")
            )
        elif valid_parent_event_id and valid_parent_event_id not in known_event_ids:
            issues.append(
                AuditIssue(
                    "warning",
                    "unknown_parent_event",
                    event.id,
                    f"Unknown parent {valid_parent_event_id}",
                )
            )
        for claim_id in event.claim_ids:
            if claim_id not in claim_ids:
                issues.append(
                    AuditIssue(
                        "error", "unknown_event_claim", event.id, f"Unknown claim {claim_id}"
                    )
                )
        for adjudication_id in event.adjudication_ids:
            adjudication = adjudication_by_id.get(adjudication_id)
            if adjudication is None:
                issues.append(
                    AuditIssue(
                        "error",
                        "unknown_event_adjudication",
                        event.id,
                        f"Unknown adjudication {adjudication_id}",
                    )
                )
            elif adjudication.claim_id not in event_attachment_claim_ids:
                issues.append(
                    AuditIssue(
                        "error",
                        "event_adjudication_claim_mismatch",
                        event.id,
                        (
                            f"Adjudication {adjudication_id} resolves claim "
                            f"{adjudication.claim_id}, which is not attached to this event"
                        ),
                    )
                )
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
        issues.extend(_audit_outcome_source_contract(event, sources))
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
        legacy_event_interval = UncertainDateInterval(
            start=UncertainDate.exact(event.year, "year"),
            end=UncertainDate.exact(event.end_year, "year"),
        )
        audit_event_interval = event.date_interval or legacy_event_interval
        legacy_intervals_by_id.setdefault(event.id, audit_event_interval)
        if event.date_interval is not None:
            legacy_bounds = _interval_envelope(legacy_event_interval)
            evidence_bounds = _interval_envelope(event.date_interval)
            if (
                legacy_bounds is not None
                and evidence_bounds is not None
                and (
                    evidence_bounds[1] < legacy_bounds[0]
                    or evidence_bounds[0] > legacy_bounds[1]
                )
            ):
                issues.append(
                    AuditIssue(
                        "error",
                        "event_date_interval_mismatch",
                        event.id,
                        "Optional date_interval does not overlap legacy year/end_year",
                    )
                )
        explicit_interval = (
            explicit_canonical_by_id[event.id].date_interval
            if event.id in explicit_canonical_by_id
            else None
        )
        if explicit_interval is not None:
            effective_bounds = _interval_envelope(audit_event_interval)
            explicit_bounds = _interval_envelope(explicit_interval)
            if (
                effective_bounds is not None
                and explicit_bounds is not None
                and (
                    explicit_bounds[1] < effective_bounds[0]
                    or explicit_bounds[0] > effective_bounds[1]
                )
            ):
                issues.append(
                    AuditIssue(
                        "error",
                        "event_date_interval_mismatch",
                        event.id,
                        "Explicit canonical date_interval does not overlap the Event's effective interval",
                    )
                )
        for participant_index, participant in enumerate(event.participants):
            for claim_id in participant.claim_ids:
                if claim_id not in claim_ids:
                    issues.append(
                        AuditIssue(
                            "error",
                            "unknown_participant_claim",
                            event.id,
                            f"{participant.entity_id} references unknown claim {claim_id}",
                        )
                    )
            for adjudication_id in participant.adjudication_ids:
                adjudication = adjudication_by_id.get(adjudication_id)
                if adjudication is None:
                    issues.append(
                        AuditIssue(
                            "error",
                            "unknown_participant_adjudication",
                            event.id,
                            f"{participant.entity_id} references unknown adjudication {adjudication_id}",
                        )
                    )
                elif adjudication.claim_id not in participant.claim_ids:
                    issues.append(
                        AuditIssue(
                            "error",
                            "participant_adjudication_claim_mismatch",
                            event.id,
                            (
                                f"{participant.entity_id} attaches adjudication {adjudication_id} "
                                f"for unattached claim {adjudication.claim_id}"
                            ),
                        )
                    )
            interval_episode = ParticipationEpisode(
                id=f"{event.id}:participant:{participant_index}",
                entity_id=participant.entity_id,
                side=participant.side,
                role=participant.role,
                entry=participant.entry,
                exit=participant.exit,
            )
            for message in interval_episode.validation_errors():
                issues.append(
                    AuditIssue(
                        "error",
                        "invalid_participant_interval",
                        event.id,
                        f"{participant.entity_id}: {message}",
                    )
                )
            entity_for_interval = entity_map.get(participant.entity_id)
            issues.extend(
                _audit_episode_context(
                    event.id,
                    interval_episode,
                    audit_event_interval,
                    (
                        (entity_for_interval.start_year, entity_for_interval.end_year)
                        if entity_for_interval is not None
                        else None
                    ),
                )
            )
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

        has_canonical_evidence = any(
            (
                valid_parent_event_id is not None,
                event.aliases,
                event.parent_event_ids,
                event.child_event_ids,
                event.date_interval is not None,
                event.geometry is not None,
                event.participation_episodes,
                event.claim_ids,
            )
        )
        if has_canonical_evidence:
            parent_ids = tuple(
                sorted(
                    set(event.parent_event_ids)
                    | ({valid_parent_event_id} if valid_parent_event_id else set())
                )
            )
            embedded_event = CanonicalEvent(
                id=event.id,
                name=event.name,
                aliases=event.aliases,
                parent_event_ids=parent_ids,
                child_event_ids=event.child_event_ids,
                date_interval=audit_event_interval,
                geometry=event.geometry,
                participation_episodes=event.participation_episodes,
                claim_ids=(),
                adjudication_ids=(),
                event_type=event.event_type,
                layer=event.track,
                domain=event.domain,
                status="proposed",
            )
            embedded_canonical_events.append(embedded_event)

    canonical_event_list = [
        replace(event, date_interval=legacy_intervals_by_id[event.id])
        if event.date_interval is None and event.id in legacy_intervals_by_id
        else event
        for event in canonical_event_list
    ]
    canonical_event_list.extend(embedded_canonical_events)
    issues.extend(
        audit_evidence(
            claims=claim_list,
            evidence_links=evidence_link_list,
            adjudications=adjudication_list,
            canonical_events=canonical_event_list,
            sources=sources,
            entity_ids=set(entity_map),
            entity_lifespans={
                entity.id: (entity.start_year, entity.end_year)
                for entity in entity_list
            },
            known_event_ids=known_event_ids,
            allowed_event_overlays=Counter(
                event.id
                for event in embedded_canonical_events
                if event.id in explicit_canonical_ids
            ),
        )
    )
    return issues


_SHA256_PATTERN = re.compile(r"^(?:sha256:)?[0-9a-fA-F]{64}$")
_EVIDENCE_RELATIONSHIPS = {"supports", "contradicts", "context"}
_GEOJSON_TYPES = {
    "Point",
    "MultiPoint",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
    "GeometryCollection",
}


def _is_blank_text(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def _audit_source_locator(
    locator: SourceLocator,
    record_id: str,
    *,
    sources: dict[str, Source] | None,
) -> list[AuditIssue]:
    issues: list[AuditIssue] = []
    required = (
        ("source_id", locator.source_id),
        ("edition", locator.edition),
        ("checksum", locator.checksum),
        ("language", locator.language),
        ("source_family", locator.source_family),
    )
    for field_name, value in required:
        if not isinstance(value, str) or not value.strip():
            issues.append(
                AuditIssue(
                    "error",
                    f"missing_locator_{field_name}",
                    record_id,
                    f"Source locator requires {field_name}",
                )
            )
    for field_name in ("creator", "citation"):
        if not isinstance(getattr(locator, field_name), str):
            issues.append(
                AuditIssue(
                    "error",
                    f"invalid_locator_{field_name}",
                    record_id,
                    f"Source locator {field_name} must be a string",
                )
            )
    for field_name, value, allowed_types in (
        ("page", locator.page, (str, int)),
        ("row", locator.row, (str, int)),
        ("url", locator.url, (str,)),
    ):
        if value is None:
            continue
        if (
            isinstance(value, bool)
            or not isinstance(value, allowed_types)
            or (isinstance(value, str) and not value.strip())
        ):
            issues.append(
                AuditIssue(
                    "error",
                    "invalid_locator_anchor",
                    record_id,
                    f"Source locator {field_name} has an invalid type or blank value",
                )
            )
    if not locator.has_exact_anchor:
        issues.append(
            AuditIssue(
                "error",
                "inexact_source_locator",
                record_id,
                "Source locator requires a page, row, or URL",
            )
        )
    if (
        isinstance(locator.checksum, str)
        and locator.checksum.strip()
        and not _SHA256_PATTERN.fullmatch(locator.checksum)
    ):
        issues.append(
            AuditIssue(
                "error",
                "invalid_locator_checksum",
                record_id,
                "Source locator checksum must be a SHA-256 digest",
            )
        )
    if isinstance(locator.url, str) and locator.url.strip():
        if not locator_url_is_valid(locator.url):
            issues.append(
                AuditIssue(
                    "error",
                    "invalid_locator_url",
                    record_id,
                    "Source locator URL must be an absolute HTTP(S) URL",
                )
            )
    if (
        sources is not None
        and isinstance(locator.source_id, str)
        and locator.source_id.strip()
        and locator.source_id not in sources
    ):
        issues.append(
            AuditIssue(
                "error",
                "unknown_locator_source",
                record_id,
                f"Source metadata does not contain {locator.source_id}",
            )
        )
    return issues


def _audit_geometry(event: CanonicalEvent) -> list[AuditIssue]:
    if event.geometry is None:
        return []
    error = geometry_validation_error(event.geometry)
    if error is None:
        return []
    return [
        AuditIssue(
            "error",
            "invalid_event_geometry",
            event.id,
            error,
        )
    ]
def _audit_parent_child_dates(
    parent: CanonicalEvent,
    child: CanonicalEvent,
) -> list[AuditIssue]:
    if parent.date_interval is None or child.date_interval is None:
        return []
    parent_bounds = _interval_envelope(parent.date_interval)
    child_bounds = _interval_envelope(child.date_interval)
    if parent_bounds is None or child_bounds is None:
        return []
    if parent_bounds[1] < child_bounds[0] or child_bounds[1] < parent_bounds[0]:
        return [
            AuditIssue(
                "error",
                "parent_child_date_mismatch",
                child.id,
                (
                    f"Child event {child.id} has no possible date overlap with "
                    f"parent event {parent.id}"
                ),
            )
        ]
    return []


def _audit_episode_context(
    event_id: str,
    episode: ParticipationEpisode,
    event_interval: UncertainDateInterval | None,
    entity_lifespan: tuple[int, int | None] | None,
) -> list[AuditIssue]:
    issues: list[AuditIssue] = []
    points = (("entry", episode.entry), ("exit", episode.exit))
    event_bounds = _interval_envelope(event_interval) if event_interval is not None else None
    entity_low: tuple[int, int, int] | None = None
    entity_high: tuple[int, int, int] | None = None
    if entity_lifespan is not None:
        entity_start, entity_end = entity_lifespan
        entity_low = (entity_start, 1, 1)
        entity_high = (entity_end, 12, 31) if entity_end is not None else None
        if event_bounds is not None and (
            event_bounds[1] < entity_low
            or (entity_high is not None and event_bounds[0] > entity_high)
        ):
            issues.append(
                AuditIssue(
                    "error",
                    "episode_outside_entity_lifespan",
                    event_id,
                    (
                        f"Episode {episode.id}'s enclosing event interval does not overlap "
                        f"{episode.entity_id}'s lifespan"
                    ),
                )
            )
    if event_interval is not None:
        for label, point in points:
            if point is None:
                continue
            point_bounds = _uncertain_date_envelope(point)
            if point_bounds is None or event_bounds is None:
                continue
            if point_bounds[1] < event_bounds[0] or point_bounds[0] > event_bounds[1]:
                issues.append(
                    AuditIssue(
                        "error",
                        "episode_outside_event_interval",
                        event_id,
                        f"Episode {episode.id} {label} lies outside the enclosing event interval",
                    )
                )
    if entity_lifespan is not None:
        for label, point in points:
            if point is None:
                continue
            point_bounds = _uncertain_date_envelope(point)
            if point_bounds is None:
                continue
            assert entity_low is not None
            if point_bounds[1] < entity_low or (
                entity_high is not None and point_bounds[0] > entity_high
            ):
                issues.append(
                    AuditIssue(
                        "error",
                        "episode_outside_entity_lifespan",
                        event_id,
                        f"Episode {episode.id} {label} lies outside {episode.entity_id}'s lifespan",
                    )
                )
    return issues


def _uncertain_date_envelope(
    value: UncertainDate,
) -> tuple[tuple[int, int, int], tuple[int, int, int]] | None:
    earliest = date_bounds(value.earliest)
    latest = date_bounds(value.latest)
    if earliest is None or latest is None:
        return None
    return (earliest[0], latest[1])


def _interval_envelope(
    value: UncertainDateInterval,
) -> tuple[tuple[int, int, int], tuple[int, int, int]] | None:
    start = date_bounds(value.start.earliest)
    end = date_bounds(value.end.latest)
    if start is None or end is None:
        return None
    return (start[0], end[1])


def audit_evidence(
    claims: Iterable[Claim] = (),
    evidence_links: Iterable[EvidenceLink] = (),
    adjudications: Iterable[Adjudication] = (),
    canonical_events: Iterable[CanonicalEvent] = (),
    *,
    sources: dict[str, Source] | None = None,
    entity_ids: set[str] | None = None,
    entity_lifespans: dict[str, tuple[int, int | None]] | None = None,
    known_event_ids: set[str] | None = None,
    allowed_event_overlays: dict[str, int] | None = None,
) -> list[AuditIssue]:
    """Audit claim-centric evidence without making it rating-eligible."""

    claim_list = list(claims)
    link_list = list(evidence_links)
    decision_list = list(adjudications)
    event_list = list(canonical_events)
    issues: list[AuditIssue] = []

    claim_map: dict[str, Claim] = {}
    for claim in claim_list:
        if _is_blank_text(claim.id):
            issues.append(
                AuditIssue("error", "missing_claim_id", "claims", "Claims require stable ids")
            )
        elif claim.id in claim_map:
            issues.append(
                AuditIssue("error", "duplicate_claim", claim.id, "Claim ids must be unique")
            )
        else:
            claim_map[claim.id] = claim
        if _is_blank_text(claim.subject):
            issues.append(
                AuditIssue("error", "missing_claim_subject", claim.id, "Claim subject is required")
            )
        if _is_blank_text(claim.predicate):
            issues.append(
                AuditIssue("error", "missing_claim_predicate", claim.id, "Claim predicate is required")
            )
        if claim.status not in CLAIM_STATUSES:
            issues.append(
                AuditIssue(
                    "error",
                    "invalid_claim_status",
                    claim.id,
                    "Claim status is assertion lifecycle only: active, withdrawn, or superseded",
                )
            )
        if claim.impact not in (None, "ordinary", "high"):
            issues.append(
                AuditIssue(
                    "error",
                    "invalid_claim_impact",
                    claim.id,
                    "Claim impact must be ordinary or high",
                )
            )
        if claim.exclusive and not claim.claim_group_id:
            issues.append(
                AuditIssue(
                    "error",
                    "exclusive_claim_without_group",
                    claim.id,
                    "Mutually exclusive claims require claim_group_id",
                )
            )
        if claim.claim_group_id is not None and _is_blank_text(claim.claim_group_id):
            issues.append(
                AuditIssue(
                    "error",
                    "invalid_claim_group_id",
                    claim.id,
                    "claim_group_id must be a non-blank string when supplied",
                )
            )
        try:
            canonicalize_json(claim.value)
            canonicalize_json(claim.precision)
        except (TypeError, ValueError) as error:
            issues.append(
                AuditIssue("error", "invalid_claim_json", claim.id, str(error))
            )
        for locator in claim.provenance:
            issues.extend(_audit_source_locator(locator, claim.id, sources=sources))

    claim_groups: dict[str, list[Claim]] = {}
    for claim in claim_list:
        if claim.claim_group_id:
            claim_groups.setdefault(claim.claim_group_id, []).append(claim)
    for group_id, group in claim_groups.items():
        if any(item.exclusive is True for item in group) and any(
            item.exclusive is not True for item in group
        ):
            issues.append(
                AuditIssue(
                    "error",
                    "inconsistent_claim_group_exclusivity",
                    group_id,
                    "Every member of an exclusive claim group must declare exclusive=true",
                )
            )

    link_map: dict[str, EvidenceLink] = {}
    for link in link_list:
        if _is_blank_text(link.id):
            issues.append(
                AuditIssue(
                    "error", "missing_evidence_id", "evidence", "Evidence links require stable ids"
                )
            )
        elif link.id in link_map:
            issues.append(
                AuditIssue(
                    "error", "duplicate_evidence_link", link.id, "Evidence link ids must be unique"
                )
            )
        else:
            link_map[link.id] = link
        if _is_blank_text(link.claim_id):
            issues.append(
                AuditIssue(
                    "error",
                    "missing_evidence_claim",
                    link.id,
                    "Evidence link requires a stable claim_id",
                )
            )
        elif link.claim_id not in claim_map:
            issues.append(
                AuditIssue(
                    "error",
                    "unknown_evidence_claim",
                    link.id,
                    f"Unknown claim {link.claim_id}",
                )
            )
        elif link.id not in claim_map[link.claim_id].evidence_ids:
            issues.append(
                AuditIssue(
                    "error",
                    "unreferenced_evidence_link",
                    link.id,
                    f"Claim {link.claim_id} does not reference this evidence link",
                )
            )
        if link.relationship not in _EVIDENCE_RELATIONSHIPS:
            issues.append(
                AuditIssue(
                    "error",
                    "invalid_evidence_relationship",
                    link.id,
                    "Evidence relationship must be supports, contradicts, or context",
                )
            )
        if _is_blank_text(link.source_family):
            issues.append(
                AuditIssue(
                    "error",
                    "missing_evidence_source_family",
                    link.id,
                    "Evidence link requires an explicit source family",
                )
            )
        elif link.locator.source_family and link.source_family != link.locator.source_family:
            issues.append(
                AuditIssue(
                    "error",
                    "evidence_source_family_mismatch",
                    link.id,
                    "Evidence link and locator source families differ",
                )
            )
        issues.extend(_audit_source_locator(link.locator, link.id, sources=sources))

    for claim in claim_list:
        for evidence_id in claim.evidence_ids:
            link = link_map.get(evidence_id)
            if link is None:
                issues.append(
                    AuditIssue(
                        "error",
                        "unknown_claim_evidence",
                        claim.id,
                        f"Unknown evidence link {evidence_id}",
                    )
                )
            elif link.claim_id != claim.id:
                issues.append(
                    AuditIssue(
                        "error",
                        "cross_claim_evidence",
                        claim.id,
                        f"Evidence link {evidence_id} belongs to {link.claim_id}",
                    )
                )
        if not claim.provenance and not claim.evidence_ids:
            issues.append(
                AuditIssue(
                    "error",
                    "claim_without_evidence",
                    claim.id,
                    "Claim requires provenance or a typed evidence link",
                )
            )
        for other_id in claim.contradicts:
            if _is_blank_text(other_id):
                issues.append(
                    AuditIssue(
                        "error",
                        "invalid_contradictory_claim",
                        claim.id,
                        "Contradictory claim references require stable non-blank ids",
                    )
                )
            elif other_id == claim.id:
                issues.append(
                    AuditIssue(
                        "error",
                        "self_contradicting_claim",
                        claim.id,
                        "A claim cannot contradict itself",
                    )
                )
            elif other_id not in claim_map:
                issues.append(
                    AuditIssue(
                        "error",
                        "unknown_contradictory_claim",
                        claim.id,
                        f"Unknown contradictory claim {other_id}",
                    )
                )

    for disagreement in find_disagreements(claim_list):
        claim_ids = sorted(
            claim_id
            for alternative in disagreement["alternatives"]
            for claim_id in alternative["claim_ids"]
        )
        issues.append(
            AuditIssue(
                "warning",
                "claim_disagreement",
                ",".join(claim_ids),
                f"Competing values remain for {disagreement['subject']} / {disagreement['predicate']}",
            )
        )

    decision_map: dict[str, Adjudication] = {}
    for decision in decision_list:
        if _is_blank_text(decision.id):
            issues.append(
                AuditIssue(
                    "error",
                    "missing_adjudication_id",
                    "adjudications",
                    "Adjudications require stable ids",
                )
            )
        elif decision.id in decision_map:
            issues.append(
                AuditIssue(
                    "error",
                    "duplicate_adjudication",
                    decision.id,
                    "Adjudication ids must be unique",
                )
            )
        else:
            decision_map[decision.id] = decision
        if _is_blank_text(decision.claim_id) or decision.claim_id not in claim_map:
            issues.append(
                AuditIssue(
                    "error",
                    "unknown_adjudication_claim",
                    decision.id,
                    f"Unknown claim {decision.claim_id}",
                )
            )
        for field_name in ("reviewer", "decision", "rationale", "codebook_version"):
            if _is_blank_text(getattr(decision, field_name)):
                issues.append(
                    AuditIssue(
                        "error",
                        f"missing_adjudication_{field_name}",
                        decision.id,
                        f"Adjudication requires {field_name}",
                    )
                )
        if decision.confidence is not None and not 0 <= decision.confidence <= 1:
            issues.append(
                AuditIssue(
                    "error",
                    "invalid_adjudication_confidence",
                    decision.id,
                    "Adjudication confidence must be in 0..1",
                )
            )
        for evidence_id in decision.evidence_ids_considered:
            link = link_map.get(evidence_id)
            if link is None:
                issues.append(
                    AuditIssue(
                        "error",
                        "unknown_adjudication_evidence",
                        decision.id,
                        f"Unknown evidence link {evidence_id}",
                    )
                )
            elif link.claim_id != decision.claim_id:
                issues.append(
                    AuditIssue(
                        "error",
                        "cross_claim_adjudication_evidence",
                        decision.id,
                        f"Evidence link {evidence_id} belongs to {link.claim_id}",
                    )
                )

    for message in adjudication_history_errors(decision_list):
        issues.append(
            AuditIssue(
                "error",
                "invalid_adjudication_history",
                "adjudications",
                message,
            )
        )

    active_by_claim: dict[str, list[Adjudication]] = {}
    for decision in active_adjudications(decision_list):
        active_by_claim.setdefault(decision.claim_id, []).append(decision)
    for claim_id, decisions in active_by_claim.items():
        if len({item.decision for item in decisions}) > 1:
            issues.append(
                AuditIssue(
                    "warning",
                    "adjudication_disagreement",
                    claim_id,
                    "Parallel unsuperseded adjudications disagree",
                )
            )

    if not any(issue.code == "invalid_adjudication_history" for issue in issues):
        try:
            resolutions = resolve_claims(claim_list, decision_list)
        except ValueError as error:
            issues.append(
                AuditIssue("error", "invalid_claim_resolution", "claims", str(error))
            )
        else:
            for claim_id, resolution in resolutions.items():
                for reason in resolution.reasons:
                    if reason.startswith("high-impact acceptance"):
                        issues.append(
                            AuditIssue(
                                "warning",
                                "high_impact_second_review_required",
                                claim_id,
                                reason,
                            )
                        )
                    elif reason.startswith("mutually exclusive group"):
                        issues.append(
                            AuditIssue(
                                "error",
                                "mutually_exclusive_acceptance",
                                claim_id,
                                reason,
                            )
                        )

    event_map: dict[str, CanonicalEvent] = {}
    overlay_allowance = Counter(allowed_event_overlays or {})
    for event in event_list:
        if _is_blank_text(event.id):
            issues.append(
                AuditIssue(
                    "error", "missing_canonical_event_id", "events", "Canonical events require ids"
                )
            )
        elif event.id in event_map:
            if overlay_allowance[event.id] > 0:
                overlay_allowance[event.id] -= 1
            else:
                issues.append(
                    AuditIssue(
                        "error",
                        "duplicate_canonical_event",
                        event.id,
                        "Canonical event ids must be unique",
                    )
                )
        else:
            event_map[event.id] = event
        if _is_blank_text(event.name):
            issues.append(
                AuditIssue(
                    "error", "missing_canonical_event_name", event.id, "Canonical event name is required"
                )
            )
        if event.date_interval is not None:
            for message in event.date_interval.validation_errors():
                issues.append(
                    AuditIssue("error", "invalid_uncertain_date", event.id, message)
                )
        issues.extend(_audit_geometry(event))
        episode_ids: set[str] = set()
        for episode in event.participation_episodes:
            if _is_blank_text(episode.id):
                issues.append(
                    AuditIssue(
                        "error",
                        "missing_participation_episode_id",
                        event.id,
                        "Participation episodes require stable ids",
                    )
                )
            elif episode.id in episode_ids:
                issues.append(
                    AuditIssue(
                        "error",
                        "duplicate_participation_episode",
                        event.id,
                        f"Duplicate participation episode {episode.id}",
                    )
                )
            episode_ids.add(episode.id)
            if _is_blank_text(episode.entity_id):
                issues.append(
                    AuditIssue(
                        "error",
                        "missing_episode_entity",
                        event.id,
                        f"Episode {episode.id} requires entity_id",
                    )
                )
            elif entity_ids is not None and episode.entity_id not in entity_ids:
                issues.append(
                    AuditIssue(
                        "error",
                        "unknown_episode_entity",
                        event.id,
                        f"Unknown entity {episode.entity_id}",
                    )
                )
            if _is_blank_text(episode.side):
                issues.append(
                    AuditIssue(
                        "error", "missing_episode_side", event.id, f"Episode {episode.id} requires side"
                    )
                )
            if _is_blank_text(episode.role):
                issues.append(
                    AuditIssue(
                        "error", "missing_episode_role", event.id, f"Episode {episode.id} requires role"
                    )
                )
            for message in episode.validation_errors():
                issues.append(
                    AuditIssue(
                        "error", "invalid_participation_episode", event.id, f"{episode.id}: {message}"
                    )
                )
            issues.extend(
                _audit_episode_context(
                    event.id,
                    episode,
                    event.date_interval,
                    (
                        entity_lifespans.get(episode.entity_id)
                        if entity_lifespans is not None
                        else None
                    ),
                )
            )
            for claim_id in episode.claim_ids:
                if claim_id not in claim_map:
                    issues.append(
                        AuditIssue(
                            "error",
                            "unknown_episode_claim",
                            event.id,
                            f"Episode {episode.id} references unknown claim {claim_id}",
                        )
                    )
        for claim_id in event.claim_ids:
            if claim_id not in claim_map:
                issues.append(
                    AuditIssue(
                        "error",
                        "unknown_event_claim",
                        event.id,
                        f"Unknown claim {claim_id}",
                    )
                )
        event_attachment_claim_ids = set(event.claim_ids)
        for episode in event.participation_episodes:
            event_attachment_claim_ids.update(episode.claim_ids)
        for adjudication_id in event.adjudication_ids:
            adjudication = decision_map.get(adjudication_id)
            if adjudication is None:
                issues.append(
                    AuditIssue(
                        "error",
                        "unknown_canonical_event_adjudication",
                        event.id,
                        f"Unknown adjudication {adjudication_id}",
                    )
                )
            elif adjudication.claim_id not in event_attachment_claim_ids:
                issues.append(
                    AuditIssue(
                        "error",
                        "canonical_event_adjudication_claim_mismatch",
                        event.id,
                        (
                            f"Adjudication {adjudication_id} resolves claim "
                            f"{adjudication.claim_id}, which is not attached to this canonical event"
                        ),
                    )
                )

    known_hierarchy_ids = set(event_map)
    if known_event_ids is not None:
        known_hierarchy_ids.update(known_event_ids)
    graph: dict[str, set[str]] = {event_id: set() for event_id in event_map}
    temporal_pairs_checked: set[tuple[str, str]] = set()
    for event in event_list:
        for parent_id in event.parent_event_ids:
            if _is_blank_text(parent_id):
                issues.append(
                    AuditIssue(
                        "error",
                        "invalid_parent_event_id",
                        event.id,
                        "Parent event references require stable non-blank ids",
                    )
                )
            elif parent_id == event.id:
                issues.append(
                    AuditIssue(
                        "error", "self_parent_event", event.id, "Event cannot be its own parent"
                    )
                )
            elif parent_id not in known_hierarchy_ids:
                issues.append(
                    AuditIssue(
                        "warning", "unknown_parent_event", event.id, f"Unknown parent {parent_id}"
                    )
                )
            elif parent_id in event_map:
                if event.id in event_map:
                    graph[parent_id].add(event.id)
                    pair = (parent_id, event.id)
                    if pair not in temporal_pairs_checked:
                        temporal_pairs_checked.add(pair)
                        issues.extend(
                            _audit_parent_child_dates(event_map[parent_id], event)
                        )
                if event.id not in event_map[parent_id].child_event_ids:
                    issues.append(
                        AuditIssue(
                            "warning",
                            "nonreciprocal_event_link",
                            event.id,
                            f"Parent {parent_id} does not list this child",
                        )
                    )
        for child_id in event.child_event_ids:
            if _is_blank_text(child_id):
                issues.append(
                    AuditIssue(
                        "error",
                        "invalid_child_event_id",
                        event.id,
                        "Child event references require stable non-blank ids",
                    )
                )
            elif child_id == event.id:
                issues.append(
                    AuditIssue(
                        "error", "self_child_event", event.id, "Event cannot be its own child"
                    )
                )
            elif child_id not in known_hierarchy_ids:
                issues.append(
                    AuditIssue(
                        "warning", "unknown_child_event", event.id, f"Unknown child {child_id}"
                    )
                )
            elif child_id in event_map:
                if event.id in event_map:
                    graph[event.id].add(child_id)
                    pair = (event.id, child_id)
                    if pair not in temporal_pairs_checked:
                        temporal_pairs_checked.add(pair)
                        issues.extend(
                            _audit_parent_child_dates(event, event_map[child_id])
                        )
                if event.id not in event_map[child_id].parent_event_ids:
                    issues.append(
                        AuditIssue(
                            "warning",
                            "nonreciprocal_event_link",
                            event.id,
                            f"Child {child_id} does not list this parent",
                        )
                    )

    visiting: set[str] = set()
    visited: set[str] = set()
    cycle_nodes: set[str] = set()

    def visit_event(event_id: str) -> None:
        if event_id in visited:
            return
        if event_id in visiting:
            cycle_nodes.add(event_id)
            return
        visiting.add(event_id)
        for child_id in graph.get(event_id, set()):
            visit_event(child_id)
        visiting.remove(event_id)
        visited.add(event_id)

    for event_id in sorted(graph):
        visit_event(event_id)
    for event_id in sorted(cycle_nodes):
        issues.append(
            AuditIssue(
                "error", "event_hierarchy_cycle", event_id, "Canonical event hierarchy contains a cycle"
            )
        )
    return issues


def has_errors(issues: Iterable[AuditIssue]) -> bool:
    return any(issue.severity == "error" for issue in issues)
