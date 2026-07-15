from __future__ import annotations

import math
import statistics
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

from .claims import canonicalize_json
from .config import ModelConfig
from .models import Entity, Event, Participant, Source


@dataclass
class TrackState:
    rating: float
    uncertainty: float
    evidence: float = 0.0
    last_year: int | None = None


@dataclass
class EntityState:
    entity: Entity
    tactical: TrackState
    operational: TrackState
    strategic: TrackState
    peak: float
    peak_year: int
    events: int = 0
    wars: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    achievement: float = 0.0


@dataclass(frozen=True)
class ParticipantUpdate:
    entity_id: str
    side: str
    utility: float
    actual: float
    expected: float
    delta: float
    result_class: str
    importance: float


@dataclass(frozen=True)
class EventUpdate:
    event: Event
    track: str
    k_factor: float
    evidence_weight: float
    participants: tuple[ParticipantUpdate, ...]


class EloEngine:
    """Chronological, coalition-aware Elo with separate tactical and strategic tracks.

    Ratings are never inherited between predecessor and successor entities.  Entity
    links are descriptive metadata only; every entity is initialized at ``baseline``.
    """

    def __init__(self, config: ModelConfig | None = None) -> None:
        self.config = config or ModelConfig()
        self.config.validate()
        self.states: dict[str, EntityState] = {}
        self.history: dict[str, list[dict[str, float | int | str]]] = {}
        self.event_updates: list[EventUpdate] = []
        self._event_evidence_weights: dict[str, float] = {}

    def initialize(self, entities: Iterable[Entity]) -> None:
        self.states = {}
        self.history = {}
        self.event_updates = []
        self._event_evidence_weights = {}
        for entity in entities:
            if entity.id in self.states:
                raise ValueError(f"Duplicate entity id: {entity.id}")
            state = EntityState(
                entity=entity,
                tactical=TrackState(self.config.baseline, self.config.max_uncertainty),
                operational=TrackState(self.config.baseline, self.config.max_uncertainty),
                strategic=TrackState(self.config.baseline, self.config.max_uncertainty),
                peak=self.config.baseline,
                peak_year=entity.start_year,
            )
            self.states[entity.id] = state
            self.history[entity.id] = [self._history_point(state, entity.start_year, "origin", 0.0)]

    def run(self, entities: Iterable[Entity], events: Iterable[Event]) -> "EloEngine":
        self.initialize(entities)
        completed = [event for event in events if event.status == "complete"]
        cluster_counts = Counter(
            (event.track, event.cluster_id or event.parent_event_id)
            for event in completed
            if event.cluster_id or event.parent_event_id
        )
        self._event_evidence_weights = {
            event.id: (
                cluster_counts[(event.track, event.cluster_id or event.parent_event_id)]
                ** (-self.config.cluster_decay_exponent)
                if event.cluster_id or event.parent_event_id
                else 1.0
            )
            for event in completed
        }
        for event in sorted(completed, key=lambda item: (item.end_year, item.year, item.id)):
            self.apply_event(event)
        return self

    def apply_event(self, event: Event) -> EventUpdate:
        if len({p.side for p in event.participants}) < 2:
            raise ValueError(f"Event {event.id} requires at least two opposing sides")
        unknown = [p.entity_id for p in event.participants if p.entity_id not in self.states]
        if unknown:
            raise ValueError(f"Event {event.id} references unknown entities: {unknown}")

        track_name = event.track
        utilities = {p.entity_id: self._utility(event, p) for p in event.participants}
        exposures = {p.entity_id: self._exposure(p) for p in event.participants}
        side_totals: dict[str, float] = {}
        for participant in event.participants:
            side_totals[participant.side] = side_totals.get(participant.side, 0.0) + exposures[participant.entity_id]

        before: dict[str, float] = {}
        uncertainties: dict[str, float] = {}
        for participant in event.participants:
            track = self._track(self.states[participant.entity_id], track_name)
            before[participant.entity_id] = track.rating
            uncertainties[participant.entity_id] = self._inflated_uncertainty(track, event.end_year)

        raw_deltas = {p.entity_id: 0.0 for p in event.participants}
        expected_weighted = {p.entity_id: 0.0 for p in event.participants}
        actual_weighted = {p.entity_id: 0.0 for p in event.participants}
        comparison_weight = {p.entity_id: 0.0 for p in event.participants}
        evidence_weight = self._event_evidence_weights.get(event.id, 1.0)
        k_factor = self._event_k(event) * evidence_weight

        participants = list(event.participants)
        importance = {
            participant.entity_id: self._participant_importance(event, participant)
            for participant in participants
        }
        default_importance = self._participant_importance(event, None)
        for left_index, left in enumerate(participants):
            for right in participants[left_index + 1 :]:
                if left.side == right.side:
                    continue
                left_share = exposures[left.entity_id] / side_totals[left.side]
                right_share = exposures[right.entity_id] / side_totals[right.side]
                pair_weight = left_share * right_share
                pair_information = min(
                    1.5,
                    max(
                        0.5,
                        math.sqrt(importance[left.entity_id] * importance[right.entity_id])
                        / default_importance,
                    ),
                )
                actual_left = 0.5 + 0.5 * (utilities[left.entity_id] - utilities[right.entity_id])
                context = self._context_adjustment(left, right)
                expected_left = self._expected(before[left.entity_id], before[right.entity_id], context)
                pair_delta = k_factor * pair_weight * pair_information * (actual_left - expected_left)
                raw_deltas[left.entity_id] += pair_delta
                raw_deltas[right.entity_id] -= pair_delta
                for participant, actual, expected in (
                    (left, actual_left, expected_left),
                    (right, 1.0 - actual_left, 1.0 - expected_left),
                ):
                    expected_weighted[participant.entity_id] += expected * pair_weight
                    actual_weighted[participant.entity_id] += actual * pair_weight
                    comparison_weight[participant.entity_id] += pair_weight

        updates: list[ParticipantUpdate] = []
        for participant in participants:
            state = self.states[participant.entity_id]
            track = self._track(state, track_name)
            delta = raw_deltas[participant.entity_id]
            track.rating += delta
            confidence = (
                participant.evidence_confidence
                if participant.evidence_confidence is not None
                else event.confidence
            )
            information = (
                self.config.uncertainty_information_gain
                * confidence
                * min(1.0, exposures[participant.entity_id])
                * evidence_weight
            )
            track.uncertainty = max(
                self.config.min_uncertainty,
                uncertainties[participant.entity_id] * math.sqrt(max(0.35, 1.0 - information)),
            )
            track.evidence += evidence_weight
            track.last_year = event.end_year
            state.events += 1
            if event.event_type == "war":
                state.wars += 1
            weight = comparison_weight[participant.entity_id]
            actual = actual_weighted[participant.entity_id] / weight if weight else 0.5
            expected = expected_weighted[participant.entity_id] / weight if weight else 0.5
            layer_weight = {
                "tactical": self.config.tactical_composite_weight,
                "operational": self.config.operational_composite_weight,
                "strategic": self.config.strategic_composite_weight,
            }[track_name]
            state.achievement += (
                evidence_weight
                * layer_weight
                * importance[participant.entity_id]
                * exposures[participant.entity_id]
                * (2.0 * actual - 1.0)
                * (1.5 - expected)
            )
            result_class = participant.result_class or self.classify_result(actual)
            if actual > 0.56:
                state.wins += 1
            elif actual < 0.44:
                state.losses += 1
            else:
                state.draws += 1
            composite = self._composite(state)
            if composite > state.peak:
                state.peak = composite
                state.peak_year = event.end_year
            self.history[participant.entity_id].append(
                self._history_point(state, event.end_year, event.id, delta)
            )
            updates.append(
                ParticipantUpdate(
                    entity_id=participant.entity_id,
                    side=participant.side,
                    utility=utilities[participant.entity_id],
                    actual=actual,
                    expected=expected,
                    delta=delta,
                    result_class=result_class,
                    importance=importance[participant.entity_id],
                )
            )

        if abs(sum(update.delta for update in updates)) > 1e-7:
            raise AssertionError(f"Event {event.id} did not conserve rating points")
        event_update = EventUpdate(event, track_name, k_factor, evidence_weight, tuple(updates))
        self.event_updates.append(event_update)
        return event_update

    def _utility(self, event: Event, participant: Participant) -> float:
        if event.track == "tactical":
            weights = self.config.tactical_weights
        elif event.track == "operational":
            weights = self.config.operational_weights
        else:
            weights = self.config.strategic_weights.get(
                event.war_type, self.config.strategic_weights["interstate_limited"]
            )
        available = {key: weight for key, weight in weights.items() if key in participant.outcome}
        if not available:
            raise ValueError(f"{event.id}/{participant.entity_id} has no usable outcome dimensions")
        normalizer = sum(available.values())
        value = sum(participant.outcome[key] * weight for key, weight in available.items()) / normalizer
        confidence = (
            participant.evidence_confidence
            if participant.evidence_confidence is not None
            else event.confidence
        )
        # Uncertain evidence is conservatively pulled toward an inconclusive result.
        return 0.5 + (value - 0.5) * confidence

    def _exposure(self, participant: Participant) -> float:
        contribution = min(1.0, max(0.05, participant.contribution))
        role = self.config.role_multipliers.get(participant.role, 0.65)
        return contribution * role

    def _event_k(self, event: Event) -> float:
        base = {
            "tactical": self.config.tactical_k,
            "operational": self.config.operational_k,
            "strategic": self.config.strategic_k,
        }[event.track]
        scale = self.config.scale_multipliers.get(event.scale, 1.0)
        stakes = self.config.stakes_multipliers.get(event.stakes, 1.0)
        decisiveness = 0.75 + 0.50 * min(1.0, max(0.0, event.decisiveness))
        confidence = 0.25 + 0.75 * min(1.0, max(0.0, event.confidence))
        duration = min(1.15, 1.0 + 0.03 * math.log1p(max(0, event.end_year - event.year)))
        return min(self.config.max_k, max(self.config.min_k, base * scale * stakes * decisiveness * confidence * duration))

    def _participant_importance(self, event: Event, participant: Participant | None) -> float:
        stakes_default = {
            "low": 0.25,
            "limited": 0.50,
            "major": 0.75,
            "existential": 1.00,
        }.get(event.stakes, 0.50)
        national_default = {
            "skirmish": 0.10,
            "battle": 0.25,
            "campaign": 0.50,
            "theater": 0.70,
            "major_war": 0.80,
            "total_war": 1.00,
        }.get(event.scale, 0.50)
        scope_default = {
            "skirmish": 0.10,
            "battle": 0.20,
            "campaign": 0.40,
            "theater": 0.65,
            "major_war": 0.75,
            "total_war": 1.00,
        }.get(event.scale, 0.50)
        stakes = participant.stakes if participant and participant.stakes is not None else stakes_default
        national = (
            participant.national_scale
            if participant and participant.national_scale is not None
            else national_default
        )
        scope = event.geographic_scope if event.geographic_scope is not None else scope_default
        return min(3.0, max(0.25, 0.25 + 1.25 * stakes + 0.90 * national + 0.60 * scope))

    def _context_adjustment(self, left: Participant, right: Participant) -> float:
        adjustment = self.config.home_advantage_points * (left.home_advantage - right.home_advantage)
        if left.force_size and right.force_size and left.force_size > 0 and right.force_size > 0:
            adjustment += self.config.force_advantage_points_per_doubling * math.log2(
                left.force_size / right.force_size
            )
        return min(self.config.max_context_adjustment, max(-self.config.max_context_adjustment, adjustment))

    def _expected(self, left_rating: float, right_rating: float, context: float = 0.0) -> float:
        exponent = -((left_rating - right_rating + context) / self.config.elo_scale)
        return 1.0 / (1.0 + 10.0**exponent)

    def _inflated_uncertainty(self, track: TrackState, year: int) -> float:
        if track.last_year is None:
            return track.uncertainty
        gap = max(0, year - track.last_year)
        drift = min(100, gap) * self.config.uncertainty_drift_per_year
        return min(self.config.max_uncertainty, math.sqrt(track.uncertainty**2 + drift**2))

    @staticmethod
    def classify_result(actual: float) -> str:
        if actual <= 0.05:
            return "existential_defeat"
        if actual <= 0.20:
            return "major_strategic_defeat"
        if actual <= 0.40:
            return "limited_defeat"
        if actual < 0.47:
            return "negotiated_disadvantage"
        if actual <= 0.53:
            return "stalemate_or_inconclusive"
        if actual < 0.60:
            return "negotiated_advantage"
        if actual < 0.80:
            return "limited_victory"
        if actual < 0.95:
            return "major_strategic_victory"
        return "existential_victory"

    def _track(self, state: EntityState, name: str) -> TrackState:
        if name == "tactical":
            return state.tactical
        if name == "operational":
            return state.operational
        return state.strategic

    def _composite(self, state: EntityState) -> float:
        tactical_coverage = min(1.0, state.tactical.evidence / self.config.tactical_full_evidence)
        operational_coverage = min(
            1.0, state.operational.evidence / self.config.operational_full_evidence
        )
        strategic_coverage = min(1.0, state.strategic.evidence / self.config.strategic_full_evidence)
        tactical_weight = self.config.tactical_composite_weight * tactical_coverage
        operational_weight = self.config.operational_composite_weight * operational_coverage
        strategic_weight = self.config.strategic_composite_weight * strategic_coverage
        return (
            self.config.baseline
            + tactical_weight * (state.tactical.rating - self.config.baseline)
            + operational_weight * (state.operational.rating - self.config.baseline)
            + strategic_weight * (state.strategic.rating - self.config.baseline)
        )

    def _composite_uncertainty(self, state: EntityState) -> float:
        tactical_coverage = min(1.0, state.tactical.evidence / self.config.tactical_full_evidence)
        operational_coverage = min(
            1.0, state.operational.evidence / self.config.operational_full_evidence
        )
        strategic_coverage = min(1.0, state.strategic.evidence / self.config.strategic_full_evidence)
        evidence_coverage = (
            self.config.tactical_composite_weight * tactical_coverage
            + self.config.operational_composite_weight * operational_coverage
            + self.config.strategic_composite_weight * strategic_coverage
        )
        weighted = (
            self.config.tactical_composite_weight * state.tactical.uncertainty
            + self.config.operational_composite_weight * state.operational.uncertainty
            + self.config.strategic_composite_weight * state.strategic.uncertainty
        )
        return min(self.config.max_uncertainty, weighted + 80.0 * (1.0 - evidence_coverage))

    def _history_point(self, state: EntityState, year: int, event_id: str, delta: float) -> dict[str, float | int | str]:
        return {
            "year": year,
            "event_id": event_id,
            "tactical": round(state.tactical.rating, 3),
            "operational": round(state.operational.rating, 3),
            "strategic": round(state.strategic.rating, 3),
            "composite": round(self._composite(state), 3),
            "uncertainty": round(self._composite_uncertainty(state), 3),
            "delta": round(delta, 3),
        }

    @staticmethod
    def _percentiles(values: dict[str, float]) -> dict[str, float]:
        ordered = sorted(values.items(), key=lambda item: (item[1], item[0]))
        if len(ordered) <= 1:
            return {entity_id: 50.0 for entity_id in values}
        return {
            entity_id: 100.0 * index / (len(ordered) - 1)
            for index, (entity_id, _) in enumerate(ordered)
        }

    def network_components(self) -> dict[str, int]:
        parent = {entity_id: entity_id for entity_id in self.states}

        def find(item: str) -> str:
            while parent[item] != item:
                parent[item] = parent[parent[item]]
                item = parent[item]
            return item

        def union(left: str, right: str) -> None:
            left_root, right_root = find(left), find(right)
            if left_root != right_root:
                parent[max(left_root, right_root)] = min(left_root, right_root)

        for update in self.event_updates:
            participants = list(update.event.participants)
            for index, left in enumerate(participants):
                for right in participants[index + 1 :]:
                    if left.side != right.side:
                        union(left.entity_id, right.entity_id)
        roots = sorted({find(entity_id) for entity_id in self.states})
        root_ids = {root: index + 1 for index, root in enumerate(roots)}
        return {entity_id: root_ids[find(entity_id)] for entity_id in self.states}

    def leaderboard(self) -> list[dict[str, float | int | str | bool | None]]:
        components = self.network_components()
        component_sizes: dict[int, int] = {}
        for component in components.values():
            component_sizes[component] = component_sizes.get(component, 0) + 1
        peak_values: dict[int, dict[str, float]] = {}
        sustained_values: dict[int, dict[str, float]] = {}
        achievement_values: dict[int, dict[str, float]] = {}
        sustained_by_entity: dict[str, float] = {}
        for entity_id, state in self.states.items():
            component = components[entity_id]
            rated_points = [float(point["composite"]) for point in self.history[entity_id][1:]]
            sustained = statistics.median(rated_points) if rated_points else self.config.baseline
            sustained_by_entity[entity_id] = sustained
            peak_values.setdefault(component, {})[entity_id] = state.peak
            sustained_values.setdefault(component, {})[entity_id] = sustained
            achievement_values.setdefault(component, {})[entity_id] = state.achievement

        peak_percentiles = {component: self._percentiles(values) for component, values in peak_values.items()}
        sustained_percentiles = {
            component: self._percentiles(values) for component, values in sustained_values.items()
        }
        achievement_percentiles = {
            component: self._percentiles(values) for component, values in achievement_values.items()
        }
        rows: list[dict[str, float | int | str | None]] = []
        for entity_id, state in self.states.items():
            total = state.wins + state.losses + state.draws
            component = components[entity_id]
            effective_events = (
                state.tactical.evidence
                + state.operational.evidence
                + state.strategic.evidence
            )
            effective_wars = state.strategic.evidence
            historical_success_raw = (
                0.40 * peak_percentiles[component][entity_id]
                + 0.35 * sustained_percentiles[component][entity_id]
                + 0.25 * achievement_percentiles[component][entity_id]
            )
            evidence_coverage = (
                0.50 * min(1.0, effective_events / 5.0)
                + 0.30 * min(1.0, effective_wars / 3.0)
                + 0.20 * min(1.0, math.log1p(component_sizes[component]) / math.log(10.0))
            )
            uncertainty_reliability = max(
                0.0,
                min(
                    1.0,
                    1.0
                    - self._composite_uncertainty(state)
                    / self.config.max_uncertainty,
                ),
            )
            coverage = evidence_coverage * uncertainty_reliability
            historical_success = 50.0 + (historical_success_raw - 50.0) * coverage
            rows.append(
                {
                    "entity_id": entity_id,
                    "name": state.entity.name,
                    "composite": round(self._composite(state), 3),
                    "tactical": round(state.tactical.rating, 3),
                    "operational": round(state.operational.rating, 3),
                    "strategic": round(state.strategic.rating, 3),
                    "uncertainty": round(self._composite_uncertainty(state), 3),
                    "peak": round(state.peak, 3),
                    "peak_year": state.peak_year,
                    "sustained": round(sustained_by_entity[entity_id], 3),
                    "achievement": round(state.achievement, 3),
                    "historical_success": round(historical_success, 2),
                    "historical_success_raw": round(historical_success_raw, 2),
                    "coverage_factor": round(coverage, 3),
                    "effective_events": round(effective_events, 3),
                    "effective_wars": round(effective_wars, 3),
                    "network_component": component,
                    "established": (
                        effective_events >= 5
                        and effective_wars >= 3
                        and self._composite_uncertainty(state) <= 200
                    ),
                    "events": state.events,
                    "wars": state.wars,
                    "wins": state.wins,
                    "losses": state.losses,
                    "draws": state.draws,
                    "confidence": round(0.0 if total == 0 else 1.0 - self._composite_uncertainty(state) / self.config.max_uncertainty, 3),
                }
            )
        return sorted(rows, key=lambda row: (-float(row["historical_success"]), -float(row["composite"]), str(row["name"])))

    def export(self, sources: dict[str, Source], metadata: dict[str, object] | None = None) -> dict[str, object]:
        event_rows: list[dict[str, object]] = []
        for update in self.event_updates:
            event = update.event
            event_rows.append(
                {
                    "id": event.id,
                    "name": event.name,
                    "year": event.year,
                    "end_year": event.end_year,
                    "type": event.event_type,
                    "war_type": event.war_type,
                    "scale": event.scale,
                    "stakes": event.stakes,
                    "domain": event.domain,
                    "geographic_scope": event.geographic_scope,
                    "cluster_id": event.cluster_id,
                    "confidence": event.confidence,
                    "decisiveness": event.decisiveness,
                    "summary": event.summary,
                    "parent_event_id": event.parent_event_id,
                    "source_ids": list(event.source_ids),
                    **(
                        {
                            "outcome_source_ids": list(event.outcome_source_ids),
                            "outcome_source_family_ids": list(
                                event.outcome_source_family_ids
                            ),
                        }
                        if event.outcome_source_ids
                        else {}
                    ),
                    **(
                        {"hced_candidate_id": event.hced_candidate_id}
                        if event.hced_candidate_id is not None
                        else {}
                    ),
                    **(
                        {
                            "modern_location_country": event.modern_location_country
                        }
                        if event.modern_location_country is not None
                        else {}
                    ),
                    **(
                        {"geometry": canonicalize_json(event.geometry)}
                        if event.geometry is not None
                        else {}
                    ),
                    **(
                        {
                            "location_provenance": event.location_provenance.to_dict()
                        }
                        if event.location_provenance is not None
                        else {}
                    ),
                    "k_factor": round(update.k_factor, 3),
                    "evidence_weight": round(update.evidence_weight, 4),
                    "participants": [
                        {
                            "entity_id": item.entity_id,
                            "side": item.side,
                            "result_class": item.result_class,
                            "utility": round(item.utility, 3),
                            "actual": round(item.actual, 3),
                            "expected": round(item.expected, 3),
                            "delta": round(item.delta, 3),
                            "importance": round(item.importance, 3),
                            "termination": next(
                                (
                                    participant.termination
                                    for participant in event.participants
                                    if participant.entity_id == item.entity_id
                                ),
                                "unknown",
                            ),
                        }
                        for item in update.participants
                    ],
                    "sources": [
                        {
                            "id": sources[source_id].id,
                            "title": sources[source_id].title,
                            "url": sources[source_id].url,
                            **(
                                {
                                    "source_family_id": sources[
                                        source_id
                                    ].source_family_id,
                                    "evidence_roles": list(
                                        sources[source_id].evidence_roles
                                    ),
                                }
                                if sources[source_id].source_family_id
                                else {}
                            ),
                        }
                        for source_id in event.source_ids
                        if source_id in sources
                    ],
                }
            )
        components = self.network_components()
        component_sizes: dict[int, int] = {}
        for component in components.values():
            component_sizes[component] = component_sizes.get(component, 0) + 1
        output_metadata = {
            **(metadata or {}),
            "network_components": len(component_sizes),
            "component_sizes": component_sizes,
            "comparison_warning": "Ratings in disconnected opponent networks are not directly identifiable; the historical-success index uses within-network percentiles.",
        }
        return {
            "meta": output_metadata,
            "entities": [
                {
                    "id": state.entity.id,
                    "name": state.entity.name,
                    "kind": state.entity.kind,
                    "start_year": state.entity.start_year,
                    "end_year": state.entity.end_year,
                    "region": state.entity.region,
                    "predecessors": list(state.entity.predecessors),
                    "continuity_note": state.entity.continuity_note,
                    "network_component": components[state.entity.id],
                }
                for state in self.states.values()
            ],
            "series": self.history,
            "leaderboard": self.leaderboard(),
            "events": event_rows,
        }
