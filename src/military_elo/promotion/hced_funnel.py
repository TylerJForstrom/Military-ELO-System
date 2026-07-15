from __future__ import annotations

"""Deterministic prioritization of unresolved HCED side labels.

This module is deliberately release-neutral. It reads the same immutable
queues and policy tables as the promotion pipeline, but it never writes to the
release, registry, or dashboard. The result is a planning upper bound:
selecting a label means "review enough time-bounded identities to make every
reported occurrence resolvable", not "add one timeless alias".
"""

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable

from .common import (
    _candidate_entity_id,
    _candidate_labels,
    _candidate_overlaps_entity,
    _candidate_policy_seed,
    _deduplicate,
    _entity_covers,
    _event_key,
    _resolve_code,
    _seed_entity_labels,
    normalize_label,
    read_jsonl,
)
from .hced import (
    _hced_label_row_key,
    promote_hced_crosswalk_rows,
    resolve_hced_side_label,
)
from .hced_location import hced_candidate_id
from .orchestrator import (
    EFFECTIVE_HCED_CURATED_EXCLUSIONS,
    WAVE6_HCED_VALIDATED_SOURCE_CONTRACTS,
)
from .policy import (
    HCED_LABEL_CURATED_EXCLUSIONS,
    HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
    IDENTITY_DENY_WINDOWS,
)
from .wave6_1500_1799 import WAVE6_HCED_RESERVED_IDS
from .wave6_1800_2021_policy import WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS
from .wave6_1800_2021_registry import WAVE6_1800_2021_ENTITY_OVERRIDES
from .wave6_pre1500 import (
    WAVE6_PRE1500_ENTITIES,
    resolve_wave6_pre1500_candidate_side_label,
    validate_wave6_pre1500_candidates,
)


NO_UNIQUE_MATCH = "no_unique_time_valid_label_match"
FAILURE_CASES = (
    "zero_time_valid_candidates",
    "multiple_time_valid_candidates",
    "one_wrong_interval_candidate",
    "policy_denied_window",
    "resolver_guard_or_tier_conflict",
)

ResolveCode = Callable[
    [str, int, int], tuple[str | None, dict[str, Any] | None, str | None]
]
ResolveLabel = Callable[
    [dict[str, Any], Any, int, int],
    tuple[str | None, dict[str, Any] | None, str | None, str | None],
]
InspectFailure = Callable[[str, int, int], dict[str, Any]]


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(values)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _century_key(year: int) -> str:
    """Return an unambiguous historical-century key.

    HCED uses signed astronomical-looking integer years but has no year-zero
    policy. Negative years are grouped as BCE, positive years as CE, and a
    literal zero is isolated instead of silently assigning it to either era.
    """

    if year == 0:
        return "YEAR_0"
    century = ((abs(year) - 1) // 100) + 1
    era = "BCE" if year < 0 else "CE"
    return f"{era}_{century:02d}"


class _UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}
        self.rank: dict[str, int] = {}

    def add(self, node: str) -> None:
        if node not in self.parent:
            self.parent[node] = node
            self.rank[node] = 0

    def contains(self, node: str) -> bool:
        return node in self.parent

    def find(self, node: str) -> str:
        parent = self.parent[node]
        if parent != node:
            self.parent[node] = self.find(parent)
        return self.parent[node]

    def union(self, left: str, right: str) -> bool:
        self.add(left)
        self.add(right)
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return False
        left_rank = self.rank[left_root]
        right_rank = self.rank[right_root]
        if left_rank < right_rank:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if left_rank == right_rank:
            self.rank[left_root] += 1
        return True

    def copy(self) -> _UnionFind:
        copied = _UnionFind()
        copied.parent = dict(self.parent)
        copied.rank = dict(self.rank)
        return copied


def _ledger_components(ledger_events: list[dict[str, Any]]) -> _UnionFind:
    components = _UnionFind()
    for index, event in enumerate(ledger_events):
        participants = event.get("participants")
        if not isinstance(participants, list):
            raise TypeError(f"ledger event {index} participants must be a list")
        entity_ids: list[str] = []
        for participant in participants:
            if not isinstance(participant, dict):
                raise TypeError(
                    f"ledger event {index} participant must be an object"
                )
            entity_id = participant.get("entity_id")
            if not isinstance(entity_id, str) or not entity_id.strip():
                raise ValueError(
                    f"ledger event {index} participant has invalid entity_id"
                )
            if entity_id != entity_id.strip():
                raise ValueError(
                    f"ledger event {index} participant entity_id has whitespace"
                )
            entity_ids.append(entity_id)
            components.add(entity_id)
        if entity_ids:
            anchor = entity_ids[0]
            for entity_id in entity_ids[1:]:
                components.union(anchor, entity_id)
    return components


def _matching_identity_intervals(
    normalized: str,
    context: dict[str, Any],
) -> dict[str, tuple[int, int | None]]:
    """Enumerate effective exact-label identities before time filtering.

    Cliopatria candidates that the live resolver maps onto a seed identity are
    represented by that seed interval. This prevents the diagnostic from
    claiming that a parallel candidate identity is a valid escape hatch.
    """

    matches: dict[str, tuple[int, int | None]] = {}

    def add(entity_id: str, start_year: Any, end_year: Any) -> None:
        interval = (
            int(start_year),
            int(end_year) if end_year is not None else None,
        )
        previous = matches.get(entity_id)
        if previous is not None and previous != interval:
            raise ValueError(
                f"identity {entity_id} has conflicting diagnostic intervals: "
                f"{previous} and {interval}"
            )
        matches[entity_id] = interval

    for entity in context["seed_entities"]:
        if normalized in _seed_entity_labels(entity):
            add(str(entity["id"]), entity["start_year"], entity.get("end_year"))

    release_entities = context["release_entities"]
    entity_labels = context["entity_labels"]
    for _, _, entity_id in context["label_observations"].get(normalized, []):
        entity = release_entities.get(entity_id)
        if entity is not None and normalized in entity_labels.get(entity_id, set()):
            add(entity_id, entity["start_year"], entity.get("end_year"))

    seed_by_id = context["seed_by_id"]
    seed_label_index = context["seed_label_index"]
    for polity in context["polity_alias_index"].get(normalized, []):
        mapped_seed = _candidate_policy_seed(polity, seed_by_id)
        if mapped_seed is None:
            name_matches = seed_label_index.get(
                normalize_label(polity.get("canonical_name_candidate")), set()
            )
            if len(name_matches) == 1:
                named_seed = next(iter(name_matches))
                named_entity = seed_by_id.get(named_seed)
                if named_entity and _candidate_overlaps_entity(polity, named_entity):
                    mapped_seed = named_seed
        if mapped_seed is not None:
            entity = seed_by_id.get(mapped_seed)
            if entity is None:
                raise ValueError(
                    f"Cliopatria label mapping targets missing seed {mapped_seed}"
                )
            add(mapped_seed, entity["start_year"], entity.get("end_year"))
        else:
            add(
                _candidate_entity_id(polity),
                polity["start_year"],
                polity["end_year"],
            )
    return matches


def classify_label_failure(
    normalized: str,
    low_year: int,
    high_year: int,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Split one generic no-unique rejection into an actionable case."""

    if not normalized or normalized != normalize_label(normalized):
        raise ValueError("failure classification requires a normalized label")
    if low_year > high_year:
        raise ValueError("failure classification interval is inverted")

    candidates = _matching_identity_intervals(normalized, context)
    valid_ids = sorted(
        entity_id
        for entity_id, (start_year, end_year) in candidates.items()
        if start_year <= low_year and (end_year is None or end_year >= high_year)
    )
    denied = any(
        not (high_year < deny_low or low_year > deny_high)
        for deny_low, deny_high in IDENTITY_DENY_WINDOWS.get(normalized, ())
    )
    if denied:
        failure_case = "policy_denied_window"
    elif len(valid_ids) > 1:
        failure_case = "multiple_time_valid_candidates"
    elif len(valid_ids) == 1:
        # Reaching this branch means the live tiered resolver still refused a
        # seemingly unique match. Keep it explicit instead of overclaiming a
        # safe identity edit.
        failure_case = "resolver_guard_or_tier_conflict"
    elif len(candidates) == 1:
        failure_case = "one_wrong_interval_candidate"
    else:
        failure_case = "zero_time_valid_candidates"
    return {
        "failure_case": failure_case,
        "candidate_ids": sorted(candidates),
        "time_valid_candidate_ids": valid_ids,
    }


def _empty_label_stat() -> dict[str, Any]:
    return {
        "events": set(),
        "sole_events": set(),
        "sole_resolved_entity_ids": set(),
        "failure_cases": Counter(),
        "centuries": Counter(),
        "candidate_ids": set(),
        "time_valid_candidate_ids": set(),
        "unresolved_side_attempts": 0,
    }


def _label_node(label: str) -> str:
    return f"unresolved-label:{label}"


def _newly_unblocked_events(
    candidate_events: list[dict[str, Any]],
    selected: set[str],
    candidate_label: str,
    already_unblocked: set[str],
) -> list[dict[str, Any]]:
    assumed = selected | {candidate_label}
    return [
        event
        for event in candidate_events
        if event["candidate_id"] not in already_unblocked
        and candidate_label in event["blockers"]
        and event["blockers"] <= assumed
    ]


def _marginal_component_joins(
    events: list[dict[str, Any]],
    components: _UnionFind,
    candidate_label: str,
) -> int:
    roots: set[str] = set()
    for event in events:
        for entity_id in event["resolved_entity_ids"]:
            if components.contains(entity_id):
                roots.add(components.find(entity_id))
        for label in event["blockers"]:
            if label == candidate_label:
                continue
            node = _label_node(label)
            if components.contains(node):
                roots.add(components.find(node))
    return max(0, len(roots) - 1)


def _install_planning_events(
    events: list[dict[str, Any]],
    components: _UnionFind,
) -> None:
    for event in events:
        nodes = [
            *event["resolved_entity_ids"],
            *[_label_node(label) for label in sorted(event["blockers"])],
        ]
        if not nodes:
            continue
        for node in nodes:
            components.add(node)
        anchor = nodes[0]
        for node in nodes[1:]:
            components.union(anchor, node)


def _greedy_ranking(
    planning_events: list[dict[str, Any]],
    label_stats: dict[str, dict[str, Any]],
    ledger_components: _UnionFind,
    batch_size: int,
    initial_selected: Iterable[str] = (),
) -> list[dict[str, Any]]:
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    components = ledger_components.copy()
    selected = {normalize_label(label) for label in initial_selected}
    selected.discard("")
    unblocked = {
        event["candidate_id"]
        for event in planning_events
        if event["blockers"] <= selected
    }
    _install_planning_events(
        [
            event
            for event in planning_events
            if event["candidate_id"] in unblocked
        ],
        components,
    )
    ranking: list[dict[str, Any]] = []
    events_by_label: dict[str, list[dict[str, Any]]] = {}
    for event in planning_events:
        for label in event["blockers"]:
            events_by_label.setdefault(label, []).append(event)

    while len(ranking) < batch_size:
        choices: list[tuple[int, int, int, str, list[dict[str, Any]]]] = []
        for label, stats in label_stats.items():
            if label in selected:
                continue
            newly = _newly_unblocked_events(
                events_by_label.get(label, []), selected, label, unblocked
            )
            if not newly:
                continue
            joins = _marginal_component_joins(newly, components, label)
            choices.append(
                (
                    len(newly),
                    joins,
                    len(stats["events"]),
                    label,
                    newly,
                )
            )
        if not choices:
            break
        choices.sort(key=lambda row: (-row[0], -row[1], -row[2], row[3]))
        marginal_events, joins, _, label, newly = choices[0]
        selected.add(label)
        newly_ids = sorted(event["candidate_id"] for event in newly)
        unblocked.update(newly_ids)
        _install_planning_events(newly, components)
        ranking.append(
            {
                "rank": len(ranking) + 1,
                "label": label,
                "marginal_events": marginal_events,
                "cumulative_events": len(unblocked),
                "marginal_components_bridged": joins,
                "events_touched": len(label_stats[label]["events"]),
                "newly_unblocked_candidate_id_sha256": _sorted_newline_sha256(
                    newly_ids
                ),
            }
        )
    return ranking


def recompute_hced_marginal_yield(
    row_label_data: list[dict[str, Any]],
    ledger_events: list[dict[str, Any]],
    *,
    batch_size: int = 50,
    preselected_labels: Iterable[str] = (),
) -> list[dict[str, Any]]:
    """Recompute the greedy ranking from serialized funnel row data.

    A downstream scorer can filter or enrich ``row_label_data`` and call this
    function without rebuilding the release. Only rows explicitly marked
    ``greedy_eligible`` enter the optimistic identity-unblocking universe.
    """

    planning_events: list[dict[str, Any]] = []
    label_stats: dict[str, dict[str, Any]] = {}
    seen_candidate_ids: set[str] = set()
    for row in row_label_data:
        if not row.get("greedy_eligible"):
            continue
        candidate_id = row.get("candidate_id")
        labels = row.get("blocker_labels")
        entities = row.get("resolved_counterpart_entity_ids")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ValueError("greedy row requires a nonblank candidate_id")
        if candidate_id in seen_candidate_ids:
            raise ValueError(f"duplicate greedy candidate_id {candidate_id}")
        if not isinstance(labels, list) or not labels:
            raise ValueError(f"greedy row {candidate_id} requires blocker_labels")
        blockers = {normalize_label(label) for label in labels}
        if "" in blockers or len(blockers) != len(labels):
            raise ValueError(
                f"greedy row {candidate_id} blocker_labels must be unique and normalized"
            )
        if not isinstance(entities, list) or any(
            not isinstance(entity_id, str) or not entity_id.strip()
            for entity_id in entities
        ):
            raise ValueError(
                f"greedy row {candidate_id} has invalid counterpart entity IDs"
            )
        seen_candidate_ids.add(candidate_id)
        planning_events.append(
            {
                "candidate_id": candidate_id,
                "blockers": blockers,
                "resolved_entity_ids": sorted(set(entities)),
            }
        )
        for label in blockers:
            label_stats.setdefault(label, {"events": set()})["events"].add(
                candidate_id
            )
    return _greedy_ranking(
        planning_events,
        label_stats,
        _ledger_components(ledger_events),
        batch_size,
        initial_selected=preselected_labels,
    )


def analyze_hced_unresolved_labels(
    deferred_rows: list[dict[str, Any]],
    *,
    resolve_code: ResolveCode,
    resolve_candidate_side_label: ResolveLabel,
    inspect_failure: InspectFailure,
    ledger_events: list[dict[str, Any]],
    curated_seed_keys: set[tuple[str, int]] | frozenset[tuple[str, int]] = frozenset(),
    promoted_event_keys: set[tuple[str, int]] | frozenset[tuple[str, int]] = frozenset(),
    curated_label_exclusions: dict[str, str] | None = None,
    batch_size: int = 50,
) -> dict[str, Any]:
    """Analyze every deferred row without changing promotion decisions.

    ``events_touched`` counts distinct HCED candidate rows containing a
    no-unique side-label failure. ``sole_blocker_events`` is stricter: exactly
    one side occurrence fails, that failure is this label, the other side
    resolves, and no known non-identity/duplicate gate prevents planning it.
    """

    if curated_label_exclusions is None:
        curated_label_exclusions = HCED_LABEL_CURATED_EXCLUSIONS
    components = _ledger_components(ledger_events)
    label_stats: dict[str, dict[str, Any]] = {}
    planning_events: list[dict[str, Any]] = []
    row_label_data: list[dict[str, Any]] = []
    exclusion_counts: Counter[str] = Counter()
    failure_case_totals: Counter[str] = Counter()
    touched_event_ids: set[str] = set()
    sole_event_ids: set[str] = set()
    planning_row_keys: set[tuple[str, int, str]] = set()

    for candidate in deferred_rows:
        candidate_id = hced_candidate_id(candidate)
        if candidate_id in curated_label_exclusions:
            exclusion_counts["curated_label_exclusion"] += 1
            continue
        try:
            low_year = int(candidate["year_low"])
            best_year = int(candidate["year_best"])
            high_year = int(candidate["year_high"])
        except (KeyError, TypeError, ValueError):
            exclusion_counts["missing_or_invalid_year"] += 1
            continue
        if low_year > high_year or not low_year <= best_year <= high_year:
            exclusion_counts["invalid_year_interval"] += 1
            continue

        winner = normalize_label(candidate.get("winner_raw"))
        loser = normalize_label(candidate.get("loser_raw"))
        side_a_label = normalize_label(candidate.get("side_1_raw"))
        side_b_label = normalize_label(candidate.get("side_2_raw"))
        draw = winner in {"draw", "inconclusive", "stalemate"}
        if not draw and (
            not winner or not loser or winner != side_a_label or loser != side_b_label
        ):
            exclusion_counts["label_outcome_not_aligned"] += 1
            continue

        event_name = str(
            candidate.get("name")
            or candidate.get("source_record_id")
            or "Unnamed engagement"
        )
        event_key = _event_key(event_name, best_year)
        duplicate_gate = event_key in curated_seed_keys or event_key in promoted_event_keys

        blocker_occurrences: Counter[str] = Counter()
        resolved_entity_ids: set[str] = set()
        has_other_blocker = False
        other_blockers: list[str] = []
        attempts: list[tuple[str, dict[str, Any]]] = []
        for codes, raw_label in (
            (
                _deduplicate(
                    map(str, candidate.get("seshat_side_1_candidates", []))
                ),
                candidate.get("side_1_raw"),
            ),
            (
                _deduplicate(
                    map(str, candidate.get("seshat_side_2_candidates", []))
                ),
                candidate.get("side_2_raw"),
            ),
        ):
            if codes:
                side_failed = False
                for code in codes:
                    entity_id, _, reason = resolve_code(code, low_year, high_year)
                    if entity_id is None:
                        blocker = f"other_identity_blocker:{reason or 'unresolved_entity'}"
                        exclusion_counts[blocker] += 1
                        other_blockers.append(blocker)
                        has_other_blocker = True
                        side_failed = True
                        break
                    resolved_entity_ids.add(entity_id)
                if side_failed:
                    continue
            else:
                entity_id, _, reason, _ = resolve_candidate_side_label(
                    candidate, raw_label, low_year, high_year
                )
                if entity_id is not None:
                    resolved_entity_ids.add(entity_id)
                    continue
                normalized = normalize_label(raw_label)
                if reason != NO_UNIQUE_MATCH or not normalized:
                    blocker = f"other_identity_blocker:{reason or 'unresolved_entity'}"
                    exclusion_counts[blocker] += 1
                    other_blockers.append(blocker)
                    has_other_blocker = True
                    continue
                inspection = inspect_failure(normalized, low_year, high_year)
                failure_case = inspection.get("failure_case")
                if failure_case not in FAILURE_CASES:
                    raise ValueError(
                        f"unknown HCED funnel failure case {failure_case!r}"
                    )
                attempts.append((normalized, inspection))
                blocker_occurrences[normalized] += 1

        if not attempts:
            continue

        labels_this_event = {label for label, _ in attempts}
        century = _century_key(best_year)
        for label in labels_this_event:
            stats = label_stats.setdefault(label, _empty_label_stat())
            stats["events"].add(candidate_id)
            stats["centuries"][century] += 1
            touched_event_ids.add(candidate_id)
        for label, inspection in attempts:
            stats = label_stats[label]
            stats["unresolved_side_attempts"] += 1
            failure_case = str(inspection["failure_case"])
            stats["failure_cases"][failure_case] += 1
            failure_case_totals[failure_case] += 1
            stats["candidate_ids"].update(
                map(str, inspection.get("candidate_ids", []))
            )
            stats["time_valid_candidate_ids"].update(
                map(str, inspection.get("time_valid_candidate_ids", []))
            )

        if duplicate_gate:
            exclusion_counts["duplicate_of_existing_event"] += 1
            other_blockers.append("duplicate_of_existing_event")
            has_other_blocker = True
        label_row_key = _hced_label_row_key(candidate, event_name, best_year)
        if label_row_key in planning_row_keys:
            exclusion_counts["duplicate_label_row_key"] += 1
            other_blockers.append("duplicate_label_row_key")
            has_other_blocker = True

        total_occurrences = sum(blocker_occurrences.values())
        if (
            not has_other_blocker
            and len(blocker_occurrences) == 1
            and total_occurrences == 1
        ):
            sole_label = next(iter(blocker_occurrences))
            stats = label_stats[sole_label]
            stats["sole_events"].add(candidate_id)
            stats["sole_resolved_entity_ids"].update(resolved_entity_ids)
            sole_event_ids.add(candidate_id)

        repeated_label = any(count != 1 for count in blocker_occurrences.values())
        if repeated_label:
            exclusion_counts["repeated_same_label_on_opposing_sides"] += 1
            other_blockers.append("repeated_same_label_on_opposing_sides")
        greedy_eligible = not has_other_blocker and not repeated_label
        row_label_data.append(
            {
                "candidate_id": candidate_id,
                "event_name": event_name,
                "year_low": low_year,
                "year_best": best_year,
                "year_high": high_year,
                "war_names": list(map(str, candidate.get("war_names", []))),
                "side_1_raw": candidate.get("side_1_raw"),
                "side_2_raw": candidate.get("side_2_raw"),
                "blocker_labels": sorted(blocker_occurrences),
                "label_failures": [
                    {
                        "label": label,
                        "failure_case": inspection["failure_case"],
                        "candidate_ids": list(inspection.get("candidate_ids", [])),
                        "time_valid_candidate_ids": list(
                            inspection.get("time_valid_candidate_ids", [])
                        ),
                    }
                    for label, inspection in attempts
                ],
                "resolved_counterpart_entity_ids": sorted(resolved_entity_ids),
                "other_blockers": sorted(set(other_blockers)),
                "greedy_eligible": greedy_eligible,
                "sole_blocker_label": (
                    next(iter(blocker_occurrences))
                    if greedy_eligible
                    and len(blocker_occurrences) == 1
                    and total_occurrences == 1
                    else None
                ),
            }
        )
        if not greedy_eligible:
            continue
        planning_row_keys.add(label_row_key)
        planning_events.append(
            {
                "candidate_id": candidate_id,
                "blockers": set(blocker_occurrences),
                "resolved_entity_ids": sorted(resolved_entity_ids),
                "year_low": low_year,
                "year_best": best_year,
                "year_high": high_year,
            }
        )

    label_rows: list[dict[str, Any]] = []
    for label, stats in label_stats.items():
        component_roots = {
            components.find(entity_id)
            for entity_id in stats["sole_resolved_entity_ids"]
            if components.contains(entity_id)
        }
        label_rows.append(
            {
                "label": label,
                "events_touched": len(stats["events"]),
                "sole_blocker_events": len(stats["sole_events"]),
                "unresolved_side_attempts": stats["unresolved_side_attempts"],
                "failure_cases": {
                    case: stats["failure_cases"].get(case, 0)
                    for case in FAILURE_CASES
                },
                "centuries": dict(sorted(stats["centuries"].items())),
                "components_touched": len(component_roots),
                "components_bridged": max(0, len(component_roots) - 1),
                "rated_counterpart_entities": len(
                    {
                        entity_id
                        for entity_id in stats["sole_resolved_entity_ids"]
                        if components.contains(entity_id)
                    }
                ),
                "candidate_ids": sorted(stats["candidate_ids"]),
                "time_valid_candidate_ids": sorted(
                    stats["time_valid_candidate_ids"]
                ),
                "event_candidate_id_sha256": _sorted_newline_sha256(
                    stats["events"]
                ),
            }
        )
    label_rows.sort(
        key=lambda row: (
            -row["sole_blocker_events"],
            -row["components_bridged"],
            -row["events_touched"],
            row["label"],
        )
    )

    greedy = _greedy_ranking(
        planning_events, label_stats, components, batch_size=batch_size
    )
    checkpoints: list[dict[str, Any]] = []
    for requested_size in (20, 50):
        available = min(requested_size, len(greedy))
        checkpoints.append(
            {
                "requested_identities": requested_size,
                "available_ranks": available,
                "cumulative_events": (
                    greedy[available - 1]["cumulative_events"] if available else 0
                ),
            }
        )

    return {
        "schema_version": "hced-unresolved-label-funnel-v1",
        "methodology": {
            "universe": (
                "Deferred HCED rows that reach the label pass and contain at "
                "least one no_unique_time_valid_label_match side failure."
            ),
            "events_touched": (
                "Distinct candidate rows containing the normalized unresolved label."
            ),
            "sole_blocker_events": (
                "Distinct rows with exactly one unresolved side occurrence, no "
                "other known gate, and this label as that occurrence."
            ),
            "failure_case_unit": "Unresolved side-label attempts, not rows.",
            "century_unit": (
                "Distinct touched rows by year_best; CE/BCE centuries use "
                "floor((abs(year)-1)/100)+1 and literal year 0 is YEAR_0."
            ),
            "components_bridged": (
                "For sole-blocker rows, collect the current rated-ledger "
                "connected components containing resolved counterpart entities; "
                "components_bridged is max(0, distinct_components-1)."
            ),
            "greedy_order": (
                "Recompute after every selection. Maximize newly identity-unblocked "
                "rows, then current planning-graph component joins, then total "
                "events touched, then normalized label lexicographically."
            ),
            "planning_caveat": (
                "Counts assume a reviewed selection supplies all necessary "
                "time-bounded identities for that label. Outcome, source, "
                "coalition, and policy review remain mandatory."
            ),
        },
        "summary": {
            "deferred_rows": len(deferred_rows),
            "unresolved_labels": len(label_rows),
            "events_touched": len(touched_event_ids),
            "sole_blocker_events": len(sole_event_ids),
            "greedy_eligible_events": len(planning_events),
            "multi_label_greedy_events": sum(
                len(event["blockers"]) > 1 for event in planning_events
            ),
            "unresolved_side_attempts": sum(failure_case_totals.values()),
            "failure_cases": {
                case: failure_case_totals.get(case, 0) for case in FAILURE_CASES
            },
            "excluded_or_other_blocker_rows": dict(sorted(exclusion_counts.items())),
        },
        "labels": label_rows,
        "row_label_data": sorted(
            row_label_data, key=lambda row: row["candidate_id"]
        ),
        "greedy_batch": {
            "max_identities": batch_size,
            "ranking": greedy,
            "checkpoints": checkpoints,
        },
    }


def _load_json_list(path: Path, description: str) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise TypeError(f"{description} must be a JSON array of objects")
    return value


def build_hced_unresolved_funnel(
    seed_dir: str | Path,
    review_root: str | Path,
    ledger_events_path: str | Path,
    *,
    batch_size: int = 50,
) -> dict[str, Any]:
    """Build the report from authoritative seed, review, and ledger inputs."""

    seed_root = Path(seed_dir)
    review = Path(review_root)
    ledger_path = Path(ledger_events_path)
    seed_entities_path = seed_root / "entities.json"
    seed_events_path = seed_root / "events.json"
    hced_path = review / "hced-candidates.jsonl"
    cliopatria_path = review / "cliopatria-entity-candidates.jsonl"

    seed_entities = _load_json_list(seed_entities_path, "seed entities")
    seed_events = _load_json_list(seed_events_path, "seed events")
    ledger_events = _load_json_list(ledger_path, "ledger events")
    original_seed_ids = {str(entity["id"]) for entity in seed_entities}
    wave6_ids = {str(entity["id"]) for entity in WAVE6_PRE1500_ENTITIES}
    collisions = sorted(original_seed_ids & wave6_ids)
    if collisions:
        raise ValueError(f"Wave 6 pre-1500 seed identity collision: {collisions}")
    seed_entities.extend(dict(entity) for entity in WAVE6_PRE1500_ENTITIES)
    seed_by_id = {str(entity["id"]): entity for entity in seed_entities}

    cliopatria = read_jsonl(cliopatria_path)
    polities = [row for row in cliopatria if row.get("record_type") == "POLITY"]
    hced = read_jsonl(hced_path)
    validate_wave6_pre1500_candidates(hced)
    owners: dict[str, list[dict[str, Any]]] = {}
    for candidate in polities:
        for code in candidate.get("seshat_ids", []):
            owners.setdefault(str(code), []).append(candidate)

    release_entities = {str(entity["id"]): dict(entity) for entity in seed_entities}
    release_entities.update(
        {str(entity["id"]): dict(entity) for entity in WAVE6_1800_2021_ENTITY_OVERRIDES}
    )

    def ensure_candidate_entity(polity: dict[str, Any]) -> str:
        entity_id = _candidate_entity_id(polity)
        if entity_id not in release_entities:
            release_entities[entity_id] = {
                "id": entity_id,
                "name": str(polity["canonical_name_candidate"]),
                "start_year": int(polity["start_year"]),
                "end_year": int(polity["end_year"]),
                "aliases": _deduplicate(
                    [
                        *map(str, polity.get("aliases", [])),
                        *map(str, polity.get("wikipedia_titles", [])),
                    ]
                ),
            }
        return entity_id

    def resolve_reviewed_identity(
        entity_id: str | None, low_year: int, high_year: int
    ) -> tuple[str | None, None]:
        if entity_id is None:
            return None, None
        entity = release_entities.get(entity_id)
        if entity is None or not _entity_covers(entity, low_year, high_year):
            return None, None
        return entity_id, None

    curated_seed_keys = {
        _event_key(str(event["name"]), int(event["year"])) for event in seed_events
    }
    crosswalk = promote_hced_crosswalk_rows(
        hced,
        owners,
        curated_seed_keys,
        ensure_candidate_entity,
        reviewed_identity_bindings=HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
        reviewed_candidate_contracts=WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS,
        validated_source_contracts=WAVE6_HCED_VALIDATED_SOURCE_CONTRACTS,
        curated_exclusions=EFFECTIVE_HCED_CURATED_EXCLUSIONS,
        resolve_reviewed_id=resolve_reviewed_identity,
        require_complete_reviewed_identity_bindings=True,
        reserved_candidate_ids=WAVE6_HCED_RESERVED_IDS,
    )

    seed_label_index: dict[str, set[str]] = {}
    for entity in seed_entities:
        for label in [entity.get("name"), *entity.get("aliases", [])]:
            normalized = normalize_label(label)
            if normalized:
                seed_label_index.setdefault(normalized, set()).add(str(entity["id"]))
    polity_alias_index: dict[str, list[dict[str, Any]]] = {}
    for polity in polities:
        for label in _candidate_labels(polity):
            polity_alias_index.setdefault(label, []).append(polity)
    entity_labels = {
        str(entity["id"]): _seed_entity_labels(entity) for entity in seed_entities
    }
    for polity in polities:
        entity_labels.setdefault(_candidate_entity_id(polity), set()).update(
            _candidate_labels(polity)
        )
    label_context: dict[str, Any] = {
        "seed_entities": seed_entities,
        "seed_by_id": seed_by_id,
        "seed_label_index": seed_label_index,
        "label_observations": crosswalk["label_observations"],
        "release_entities": release_entities,
        "entity_labels": entity_labels,
        "polity_alias_index": polity_alias_index,
    }

    def resolve_candidate_label(
        candidate: dict[str, Any], label: Any, low_year: int, high_year: int
    ) -> tuple[str | None, dict[str, Any] | None, str | None, str | None]:
        return resolve_wave6_pre1500_candidate_side_label(
            candidate,
            label,
            low_year,
            high_year,
            label_context,
            lambda generic_label, generic_low, generic_high: resolve_hced_side_label(
                generic_label, generic_low, generic_high, label_context
            ),
        )

    report = analyze_hced_unresolved_labels(
        crosswalk["deferred_label_rows"],
        resolve_code=lambda code, low_year, high_year: _resolve_code(
            code, low_year, high_year, owners
        ),
        resolve_candidate_side_label=resolve_candidate_label,
        inspect_failure=lambda label, low_year, high_year: classify_label_failure(
            label, low_year, high_year, label_context
        ),
        ledger_events=ledger_events,
        curated_seed_keys=curated_seed_keys,
        promoted_event_keys=crosswalk["promoted_event_keys"],
        batch_size=batch_size,
    )
    report["inputs"] = {
        "seed_entities_sha256": _file_sha256(seed_entities_path),
        "seed_events_sha256": _file_sha256(seed_events_path),
        "hced_candidates_sha256": _file_sha256(hced_path),
        "cliopatria_candidates_sha256": _file_sha256(cliopatria_path),
        "ledger_events_sha256": _file_sha256(ledger_path),
    }
    return report


def write_hced_unresolved_funnel(
    report: dict[str, Any], output_path: str | Path
) -> None:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
