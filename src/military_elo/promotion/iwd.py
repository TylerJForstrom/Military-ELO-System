from __future__ import annotations

"""Interstate War Data parent-war coalition promotion."""

import re
from collections import Counter
from typing import Any

from .common import (
    _deduplicate,
    _slug,
    _strategic_participants,
    _war_tokens,
    _war_tokens_match,
    normalize_label,
)

def _seed_war_token_spans(
    seed_events: list[dict[str, Any]],
) -> list[tuple[int, int, tuple[frozenset[str], ...]]]:
    return [
        (
            int(event["year"]),
            int(event.get("end_year", event["year"])),
            tuple(
                {
                    key
                    for key in (
                        _war_tokens(event.get("name")),
                        _war_tokens(event.get("cluster_id")),
                    )
                    if key
                }
            ),
        )
        for event in seed_events
        if event.get("event_type") == "war"
    ]


def _overlaps_seed_war(
    seed_war_spans: list[tuple[int, int, tuple[frozenset[str], ...]]],
    keys: Iterable[frozenset[str]],
    low_year: int,
    high_year: int,
) -> bool:
    key_list = [key for key in keys if key]
    for seed_low, seed_high, seed_keys in seed_war_spans:
        if high_year < seed_low or low_year > seed_high:
            continue
        for key in key_list:
            for seed_key in seed_keys:
                if _war_tokens_match(key, seed_key):
                    return True
    return False


def _humanize_war_name(value: Any) -> str:
    text = str(value or "").replace("_", " ")
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)
    text = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def aggregate_iwd_parent_wars(
    candidates: list[dict[str, Any]],
    seed_war_spans: list[tuple[int, int, tuple[frozenset[str], ...]]],
    resolve_party: Any,
    curated_parent_exclusions: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Aggregate IWD component wars into at most one strategic event per parent.

    Component records repeat one umbrella conflict across many dyads, so they
    never enter the ledger individually. Each ``parent_war_id`` group is
    reconstructed as two coalitions from its initiator/target pairs and rated
    once, only when every check passes:

    - at least one component has a terminal outcome, years, and both principals;
    - the parent does not overlap a curated seed war (naming variants included);
    - the opposition graph is two-colorable and connected — an entity coded on
      both sides quarantines the parent because no explicit time-bounded
      side-switch policy is defined;
    - component outcomes are unanimous once oriented to the reconstructed
      sides, so draws and mixed dyad results are never forced into one binary
      umbrella outcome;
    - every belligerent resolves to a unique time-bounded identity.

    Confidence drops when some component rows could not contribute, and all
    component rows are attached to the emitted event as provenance.
    """
    if curated_parent_exclusions is None:
        curated_parent_exclusions = {}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        parent_id = str(
            candidate.get("parent_war_id")
            or f"component_{candidate.get('source_component_id')}"
        )
        grouped.setdefault(parent_id, []).append(candidate)

    events: list[dict[str, Any]] = []
    rejections: Counter[str] = Counter()
    resolved_polities: dict[str, dict[str, Any]] = {}
    components_aggregated = 0
    components_attached = 0

    for parent_id in sorted(
        grouped, key=lambda value: (0, int(value)) if value.isdigit() else (1, value)
    ):
        if parent_id in curated_parent_exclusions:
            # A documented wrong-actor adjudication holds the whole parent
            # for human review; components stay staged, never merged.
            rejections["curated_exclusion"] += 1
            continue
        components = sorted(grouped[parent_id], key=lambda row: str(row.get("candidate_id")))
        parent_name = next(
            (str(row["parent_war_name"]) for row in components if row.get("parent_war_name")),
            "",
        )
        usable: list[dict[str, Any]] = []
        provenance: list[dict[str, Any]] = []
        for component in components:
            outcome_code = str(component.get("terminal_outcome_code") or "")
            if outcome_code not in {"1", "2", "3"}:
                status = "not_aggregated_missing_terminal_outcome"
            elif component.get("start_year") is None or component.get("end_year") is None:
                status = "not_aggregated_missing_year"
            elif not component.get("initiators") or not component.get("targets"):
                status = "not_aggregated_missing_principal_side"
            else:
                status = "aggregated"
                usable.append(component)
            provenance.append(
                {
                    "candidate_id": str(component.get("candidate_id")),
                    "component_name": str(component.get("name") or ""),
                    "terminal_outcome_code": outcome_code or None,
                    "status": status,
                }
            )
        if not usable:
            rejections["no_usable_component"] += 1
            continue

        low_year = min(int(component["start_year"]) for component in usable)
        high_year = max(int(component["end_year"]) for component in usable)

        keys = {_war_tokens(parent_name)}
        keys.update(_war_tokens(component.get("name")) for component in components)
        if _overlaps_seed_war(seed_war_spans, keys, low_year, high_year):
            rejections["overlaps_curated_strategic_event"] += 1
            continue

        parties: dict[str, dict[str, Any]] = {}
        opposed: dict[str, set[str]] = {}
        allied: dict[str, set[str]] = {}
        for component in usable:
            component_sides = []
            for field in ("initiators", "targets"):
                side_keys = []
                for party in component[field]:
                    key = str(party.get("cow_code") or f"name:{normalize_label(party.get('name'))}")
                    info = parties.setdefault(
                        key,
                        {"name": str(party.get("name") or ""), "cow_code": party.get("cow_code"), "years": []},
                    )
                    info["years"] += [int(component["start_year"]), int(component["end_year"])]
                    side_keys.append(key)
                component_sides.append(side_keys)
            initiator_keys, target_keys = component_sides
            for left in initiator_keys:
                for right in target_keys:
                    opposed.setdefault(left, set()).add(right)
                    opposed.setdefault(right, set()).add(left)
            for side_keys in component_sides:
                for left in side_keys:
                    for right in side_keys:
                        if left != right:
                            allied.setdefault(left, set()).add(right)

        colors: dict[str, int] = {}
        conflict = False
        graph_components = 0
        for start in sorted(parties):
            if start in colors:
                continue
            graph_components += 1
            stack: list[tuple[str, int]] = [(start, 0)]
            while stack:
                node, color = stack.pop()
                known = colors.get(node)
                if known is not None:
                    if known != color:
                        conflict = True
                        break
                    continue
                colors[node] = color
                stack.extend((neighbor, 1 - color) for neighbor in opposed.get(node, ()))
                stack.extend((neighbor, color) for neighbor in allied.get(node, ()))
            if conflict:
                break
        if conflict:
            # No explicit time-bounded side-switch policies are defined, so an
            # entity coded on both sides always quarantines the parent war.
            rejections["inconsistent_coalition_sides"] += 1
            continue
        if graph_components > 1:
            rejections["disconnected_coalition_graph"] += 1
            continue

        anchor_color = colors[min(parties)]
        outcomes: set[str] = set()
        for component in usable:
            code = str(component["terminal_outcome_code"])
            initiator_key = str(
                component["initiators"][0].get("cow_code")
                or f"name:{normalize_label(component['initiators'][0].get('name'))}"
            )
            if code == "3":
                outcomes.add("draw")
            elif (code == "1") == (colors[initiator_key] == anchor_color):
                outcomes.add("side_a")
            else:
                outcomes.add("side_b")
        if len(outcomes) != 1:
            rejections["mixed_component_outcomes"] += 1
            continue
        outcome = outcomes.pop()

        resolution: dict[str, str] = {}
        pending_polities: dict[str, dict[str, Any]] = {}
        unresolved = False
        for key in sorted(parties):
            info = parties[key]
            entity_id, polity = resolve_party(
                info["name"], info["cow_code"], min(info["years"]), max(info["years"])
            )
            if not entity_id:
                unresolved = True
                break
            resolution[key] = entity_id
            if polity is not None:
                pending_polities[entity_id] = polity
        if unresolved:
            rejections["unresolved_time_bounded_party"] += 1
            continue

        side_a = _deduplicate(
            resolution[key] for key in parties if colors[key] == anchor_color
        )
        side_b = _deduplicate(
            resolution[key] for key in parties if colors[key] != anchor_color
        )
        if not side_a or not side_b or set(side_a) & set(side_b):
            rejections["same_or_empty_opposing_side"] += 1
            continue

        resolved_polities.update(pending_polities)
        completeness = len(usable) / len(components)
        confidence = round(0.76 - 0.12 * (1.0 - completeness), 2)
        display_name = _humanize_war_name(parent_name) or f"IWD parent war {parent_id}"
        components_aggregated += len(usable)
        components_attached += len(components)
        events.append(
            {
                "id": f"iwd_war_{_slug(parent_id, 16)}_{_slug(display_name, 44)}",
                "name": display_name,
                "year": low_year,
                "end_year": high_year,
                "event_type": "war",
                "war_type": "world_war" if "world" in _war_tokens(parent_name) else "interstate_limited",
                "scale": "major_war",
                "stakes": "major",
                "decisiveness": 0.44 if outcome == "draw" else 0.74,
                "confidence": confidence,
                "geographic_scope": 0.68,
                "domain": "mixed",
                "cluster_id": f"iwd_parent_{_slug(parent_id, 24)}",
                "date_precision": "year",
                "sequence": int(parent_id) if parent_id.isdigit() else 0,
                "summary": (
                    "Coalition-aggregated strategic outcome from IWD v1.21: this parent "
                    f"conflict receives exactly one strategic update, built from "
                    f"{len(usable)} of {len(components)} component dyads with a unanimous "
                    "side-oriented outcome. Component rows are retained as provenance, and "
                    "existential severity is never inferred from IWD outcome codes."
                ),
                "participants": _strategic_participants(side_a, side_b, outcome, confidence),
                "source_ids": ["iwd_dataset"],
                "outcome_source_ids": ["iwd_dataset"],
                "outcome_source_family_ids": ["iwd"],
                "status": "complete",
                "iwd_parent_war_id": parent_id,
                "iwd_parent_war_name": parent_name or None,
                "iwd_components": provenance,
            }
        )

    return {
        "events": events,
        "parent_rejections": rejections,
        "parents_total": len(grouped),
        "parents_promoted": len(events),
        "components_total": len(candidates),
        "components_aggregated": components_aggregated,
        "components_attached": components_attached,
        "resolved_polities": resolved_polities,
    }
