from __future__ import annotations

import copy
import random
from collections import defaultdict
from statistics import median
from typing import Iterable

from .config import ModelConfig
from .engine import EloEngine
from .models import Entity, Event, Participant


def _percentile(values: list[float], proportion: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * proportion
    lower = int(index)
    upper = min(len(ordered) - 1, lower + 1)
    fraction = index - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def run_sensitivity(
    entities: Iterable[Entity],
    events: Iterable[Event],
    config: ModelConfig,
    simulations: int = 0,
    seed: int = 1900,
) -> dict[str, dict[str, float]]:
    """Monte Carlo uncertainty bands from outcome confidence and weight choices.

    This does not pretend that historical ambiguity is random in nature.  It is a
    reproducible stress test: low-confidence outcome values and model weights are
    perturbed more than high-confidence observations.
    """

    if simulations <= 0:
        return {}
    entity_list = list(entities)
    event_list = list(events)
    rng = random.Random(seed)
    ratings: dict[str, list[float]] = defaultdict(list)
    ranks: dict[str, list[int]] = defaultdict(list)

    for _ in range(simulations):
        sample_config = copy.deepcopy(config)
        for profile, weights in sample_config.strategic_weights.items():
            perturbed = {key: value * rng.uniform(0.85, 1.15) for key, value in weights.items()}
            total = sum(perturbed.values())
            sample_config.strategic_weights[profile] = {key: value / total for key, value in perturbed.items()}
        tactical = {key: value * rng.uniform(0.88, 1.12) for key, value in sample_config.tactical_weights.items()}
        tactical_total = sum(tactical.values())
        sample_config.tactical_weights = {key: value / tactical_total for key, value in tactical.items()}

        sampled_events: list[Event] = []
        for event in event_list:
            participants: list[Participant] = []
            sigma = (1.0 - event.confidence) * 0.18
            for participant in event.participants:
                participant_sigma = (
                    (1.0 - participant.evidence_confidence) * 0.18
                    if participant.evidence_confidence is not None
                    else sigma
                )
                outcome = {
                    key: min(1.0, max(0.0, value + rng.gauss(0.0, participant_sigma)))
                    for key, value in participant.outcome.items()
                }
                participants.append(
                    Participant(
                        entity_id=participant.entity_id,
                        side=participant.side,
                        role=participant.role,
                        contribution=participant.contribution,
                        outcome=outcome,
                        result_class=participant.result_class,
                        force_size=participant.force_size,
                        home_advantage=participant.home_advantage,
                        evidence_confidence=participant.evidence_confidence,
                        stakes=participant.stakes,
                        national_scale=participant.national_scale,
                        termination=participant.termination,
                        note=participant.note,
                    )
                )
            sampled_events.append(
                Event(
                    id=event.id,
                    name=event.name,
                    year=event.year,
                    end_year=event.end_year,
                    event_type=event.event_type,
                    war_type=event.war_type,
                    scale=event.scale,
                    stakes=event.stakes,
                    decisiveness=event.decisiveness,
                    confidence=event.confidence,
                    participants=tuple(participants),
                    source_ids=event.source_ids,
                    parent_event_id=event.parent_event_id,
                    status=event.status,
                    sequence=event.sequence,
                    summary=event.summary,
                    date_precision=event.date_precision,
                    geographic_scope=event.geographic_scope,
                    domain=event.domain,
                    cluster_id=event.cluster_id,
                )
            )
        leaderboard = EloEngine(sample_config).run(entity_list, sampled_events).leaderboard()
        for rank, row in enumerate(leaderboard, start=1):
            entity_id = str(row["entity_id"])
            ratings[entity_id].append(float(row["composite"]))
            ranks[entity_id].append(rank)

    return {
        entity_id: {
            "median": round(median(values), 3),
            "p10": round(_percentile(values, 0.10), 3),
            "p90": round(_percentile(values, 0.90), 3),
            "median_rank": round(median(ranks[entity_id]), 1),
            "top_10_probability": round(sum(rank <= 10 for rank in ranks[entity_id]) / simulations, 3),
        }
        for entity_id, values in ratings.items()
    }
