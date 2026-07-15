from __future__ import annotations

"""Read-only HCED co-war diagnostics and conservative identity proposals.

The report in this module is deliberately separate from release promotion.  It
uses the same normalized labels, time-bounded identities, and front-gate
policies as the HCED label pass, but it never creates an event or changes an
entity.  Co-war propagation emits review suggestions only when a rooted,
deterministic constraint has one time-valid answer.
"""

import hashlib
import json
import math
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .promotion.common import (
    _candidate_entity_id,
    _candidate_labels,
    _candidate_overlaps_entity,
    _candidate_policy_seed,
    _entity_covers,
    _event_key,
    _resolve_code,
    _seed_entity_labels,
    _slug,
    normalize_label,
    read_jsonl,
)
from .promotion.hced import _hced_label_row_key, resolve_hced_side_label
from .promotion.hced_location import hced_candidate_id
from .promotion.policy import (
    HCED_CURATED_EXCLUSIONS,
    HCED_FACTION_LABELS,
    HCED_LABEL_CURATED_EXCLUSIONS,
    HCED_LABEL_POLICIES,
    HCED_PENDING_SPLIT_LABELS,
    HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS,
    IDENTITY_DENY_WINDOWS,
)
from .promotion.wave6_1500_1799 import (
    WAVE6_HCED_RESERVED_IDS,
)
from .promotion.wave6_1800_2021_holds import WAVE6_HCED_CURATED_EXCLUSIONS
from .promotion.wave6_1800_2021_policy import (
    WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS,
)
from .promotion.wave6_1800_2021_registry import (
    WAVE6_1800_2021_ENTITY_OVERRIDES,
)
from .promotion.wave6_pre1500 import (
    WAVE6_PRE1500_CURATED_EXCLUSIONS,
    WAVE6_PRE1500_ENTITIES,
    resolve_wave6_pre1500_candidate_side_label,
)


SCHEMA_VERSION = "military-elo-war-constraints-v1"
MIN_BINARY_ANCHOR_ROWS = 2

_PROJECT_CROSSWALK_EXCLUSIONS = {
    **HCED_CURATED_EXCLUSIONS,
    **WAVE6_PRE1500_CURATED_EXCLUSIONS,
    **WAVE6_HCED_CURATED_EXCLUSIONS,
}


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _file_fingerprint(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    payload = source.read_bytes()
    return {
        "name": source.name,
        "bytes": len(payload),
        "sha256": _sha256_bytes(payload),
    }


def _normalized_war_names(row: Mapping[str, Any]) -> tuple[str, ...]:
    names = {normalize_label(name) for name in row.get("war_names", [])}
    names.discard("")
    return tuple(sorted(names))


def _valid_interval(row: Mapping[str, Any]) -> tuple[int, int] | None:
    if row.get("year_low") is None or row.get("year_high") is None:
        return None
    low = int(row["year_low"])
    high = int(row["year_high"])
    if high < low:
        return None
    return low, high


def _outcome_aligned(row: Mapping[str, Any]) -> bool:
    winner = normalize_label(row.get("winner_raw"))
    loser = normalize_label(row.get("loser_raw"))
    side_1 = normalize_label(row.get("side_1_raw"))
    side_2 = normalize_label(row.get("side_2_raw"))
    if winner in {"draw", "inconclusive", "stalemate"}:
        return True
    return bool(winner and loser and winner == side_1 and loser == side_2)


def _mapped_candidate_id(
    polity: Mapping[str, Any],
    seed_by_id: Mapping[str, dict[str, Any]],
    seed_label_index: Mapping[str, set[str]],
) -> str:
    candidate = dict(polity)
    mapped_seed = _candidate_policy_seed(candidate, dict(seed_by_id))
    if not mapped_seed:
        name_matches = seed_label_index.get(
            normalize_label(candidate.get("canonical_name_candidate")), set()
        )
        if len(name_matches) == 1:
            named_seed = next(iter(name_matches))
            named_entity = seed_by_id.get(named_seed)
            if named_entity and _candidate_overlaps_entity(candidate, named_entity):
                mapped_seed = named_seed
    return mapped_seed or _candidate_entity_id(candidate)


def _candidate_entity_row(polity: Mapping[str, Any], entity_id: str) -> dict[str, Any]:
    groups = list(polity.get("temporal_coverage_groups", []))
    return {
        "id": entity_id,
        "name": str(polity.get("canonical_name_candidate") or entity_id),
        "start_year": int(polity["start_year"]),
        "end_year": int(polity["end_year"]),
        "identity_status": "source_candidate",
        "coverage_discontinuous": len(groups) > 1,
        "candidate_ids": [str(polity.get("candidate_id") or "")],
    }


def _merge_entity_metadata(
    target: dict[str, Any], source: Mapping[str, Any]
) -> dict[str, Any]:
    candidate_ids = {
        *map(str, target.get("candidate_ids", [])),
        *map(str, source.get("candidate_ids", [])),
    }
    candidate_ids.discard("")
    target["candidate_ids"] = sorted(candidate_ids)
    target["coverage_discontinuous"] = bool(
        target.get("coverage_discontinuous")
        or source.get("coverage_discontinuous")
    )
    return target


def _build_identity_context(
    seed_entities: list[dict[str, Any]],
    polities: list[dict[str, Any]],
    *,
    project_policy: bool,
) -> dict[str, Any]:
    curated: dict[str, dict[str, Any]] = {
        str(entity["id"]): deepcopy(entity) for entity in seed_entities
    }
    if project_policy:
        for entity in WAVE6_PRE1500_ENTITIES:
            curated[str(entity["id"])] = deepcopy(entity)
        for entity in WAVE6_1800_2021_ENTITY_OVERRIDES:
            curated[str(entity["id"])] = deepcopy(entity)

    seed_rows = list(curated.values())
    seed_by_id = {str(entity["id"]): entity for entity in seed_rows}
    seed_label_index: dict[str, set[str]] = defaultdict(set)
    for entity in seed_rows:
        for label in (entity.get("name"), *entity.get("aliases", [])):
            normalized = normalize_label(label)
            if normalized:
                seed_label_index[normalized].add(str(entity["id"]))

    candidate_alias_index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    owners: dict[str, list[dict[str, Any]]] = defaultdict(list)
    entity_labels: dict[str, set[str]] = {
        str(entity["id"]): _seed_entity_labels(entity) for entity in seed_rows
    }
    entity_catalog: dict[str, dict[str, Any]] = {}
    for entity in seed_rows:
        entity_catalog[str(entity["id"])] = {
            "id": str(entity["id"]),
            "name": str(entity.get("name") or entity["id"]),
            "start_year": int(entity["start_year"]),
            "end_year": (
                int(entity["end_year"])
                if entity.get("end_year") is not None
                else None
            ),
            "identity_status": "curated",
            "coverage_discontinuous": False,
            "candidate_ids": [],
        }

    polity_rows = [row for row in polities if row.get("record_type") == "POLITY"]
    for polity in polity_rows:
        for code in polity.get("seshat_ids", []):
            owners[str(code)].append(polity)
        labels = _candidate_labels(polity)
        for label in labels:
            candidate_alias_index[label].append(polity)
        entity_id = _mapped_candidate_id(polity, seed_by_id, seed_label_index)
        entity_labels.setdefault(entity_id, set()).update(labels)
        candidate_row = _candidate_entity_row(polity, entity_id)
        if entity_id in entity_catalog:
            _merge_entity_metadata(entity_catalog[entity_id], candidate_row)
        else:
            entity_catalog[entity_id] = candidate_row

    return {
        "seed_entities": seed_rows,
        "seed_by_id": seed_by_id,
        "seed_label_index": dict(seed_label_index),
        "polities": polity_rows,
        "owners": dict(owners),
        "candidate_alias_index": dict(candidate_alias_index),
        "entity_labels": entity_labels,
        "entity_catalog": entity_catalog,
        # Candidate identities enter this mapping only after a successful
        # crosswalk observation, matching the release builder's materialization
        # order. Curated identities are available from the start.
        "release_entities": {key: deepcopy(value) for key, value in curated.items()},
        "label_observations": {},
    }


def _candidate_matches(
    label: Any,
    low_year: int,
    high_year: int,
    context: Mapping[str, Any],
) -> list[dict[str, Any]]:
    normalized = normalize_label(label)
    if not normalized:
        return []
    matches: dict[str, dict[str, Any]] = {}

    def add(entity_id: str, evidence: str) -> None:
        metadata = context["entity_catalog"].get(entity_id)
        if metadata is None:
            release_entity = context["release_entities"].get(entity_id)
            if release_entity is None:
                return
            metadata = {
                "id": entity_id,
                "name": str(release_entity.get("name") or entity_id),
                "start_year": int(release_entity["start_year"]),
                "end_year": (
                    int(release_entity["end_year"])
                    if release_entity.get("end_year") is not None
                    else None
                ),
                "identity_status": "curated",
                "coverage_discontinuous": False,
                "candidate_ids": [],
            }
        row = matches.setdefault(
            entity_id,
            {
                "entity_id": entity_id,
                "name": str(metadata["name"]),
                "start_year": int(metadata["start_year"]),
                "end_year": metadata.get("end_year"),
                "identity_status": str(metadata.get("identity_status") or "unknown"),
                "coverage_discontinuous": bool(
                    metadata.get("coverage_discontinuous")
                ),
                "candidate_ids": sorted(map(str, metadata.get("candidate_ids", []))),
                "evidence": [],
            },
        )
        if evidence not in row["evidence"]:
            row["evidence"].append(evidence)

    for entity in context["seed_entities"]:
        if normalized in _seed_entity_labels(entity):
            add(str(entity["id"]), "curated_exact_label")

    for _, _, entity_id in context["label_observations"].get(normalized, []):
        add(str(entity_id), "seshat_crosswalk_observation")

    for polity in context["candidate_alias_index"].get(normalized, []):
        entity_id = _mapped_candidate_id(
            polity, context["seed_by_id"], context["seed_label_index"]
        )
        add(entity_id, "cliopatria_exact_label")

    result = []
    for entity_id in sorted(matches):
        row = matches[entity_id]
        row["evidence"].sort()
        end = row.get("end_year")
        row["time_valid"] = int(row["start_year"]) <= low_year and (
            end is None or int(end) >= high_year
        )
        result.append(row)
    return result


def _overlaps_deny_window(label: str, low_year: int, high_year: int) -> bool:
    return any(
        not (high_year < deny_low or low_year > deny_high)
        for deny_low, deny_high in IDENTITY_DENY_WINDOWS.get(label, ())
    )


def _detailed_label_failure(
    label: Any,
    low_year: int,
    high_year: int,
    reason: str | None,
    candidates: list[dict[str, Any]],
) -> str:
    normalized = normalize_label(label)
    if reason in {
        "blank_side_label",
        "faction_label_not_a_polity",
        "label_pending_identity_split",
        "label_outside_policy_window",
    }:
        return str(reason)
    if _overlaps_deny_window(normalized, low_year, high_year):
        return "identity_deny_window"
    valid = [candidate for candidate in candidates if candidate["time_valid"]]
    if not candidates:
        return "zero_label_candidates"
    if len(candidates) == 1 and not valid:
        return "single_label_candidate_outside_interval"
    if not valid:
        return "multiple_label_candidates_outside_interval"
    if len(valid) > 1:
        return "multiple_time_valid_label_candidates"
    return "candidate_rejected_by_policy_or_coherence_guard"


def _side_key(candidate_id: str, side_name: str) -> str:
    return f"{candidate_id}:{side_name}"


def _resolve_side(
    row: dict[str, Any],
    side_name: str,
    context: dict[str, Any],
    *,
    project_policy: bool,
) -> dict[str, Any]:
    low_year, high_year = _valid_interval(row) or (0, -1)
    side_number = 1 if side_name == "side_1" else 2
    label = row.get(f"side_{side_number}_raw")
    normalized = normalize_label(label)
    codes = tuple(
        sorted(
            {
                str(code)
                for code in row.get(f"seshat_side_{side_number}_candidates", [])
                if str(code)
            }
        )
    )
    candidate_id = hced_candidate_id(row)
    exact_contract = (
        WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS.get(candidate_id)
        if project_policy
        else None
    )
    reviewed_binding = (
        HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS.get(candidate_id)
        if project_policy
        else None
    )
    if exact_contract is not None:
        entity_ids = tuple(
            sorted(map(str, exact_contract[f"side_{side_number}"]))
        )
        return {
            "key": _side_key(candidate_id, side_name),
            "side": side_name,
            "label": normalized,
            "label_raw": "" if label is None else str(label),
            "codes": list(codes),
            "entity_ids": list(entity_ids),
            "initial_entity_ids": list(entity_ids),
            "resolution": "exact_reviewed_candidate_contract",
            "tier": "exact_reviewed_candidate_contract",
            "reason": None,
            "failure_case": None,
            "candidate_entities": _candidate_matches(
                label, low_year, high_year, context
            ),
        }

    if codes:
        resolved: list[str] = []
        failure_reason: str | None = None
        for code in codes:
            expected_id = (
                reviewed_binding.get("code_bindings", {}).get(code)
                if reviewed_binding is not None
                else None
            )
            if expected_id is not None:
                entity = context["release_entities"].get(expected_id)
                if entity is not None and _entity_covers(entity, low_year, high_year):
                    entity_id, polity, reason = expected_id, None, None
                else:
                    entity_id, polity, reason = None, None, "reviewed_identity_outside_interval"
            else:
                entity_id, polity, reason = _resolve_code(
                    code, low_year, high_year, context["owners"]
                )
            if not entity_id:
                failure_reason = reason or "unresolved_seshat_code"
                break
            if polity is not None:
                candidate_entity_id = _candidate_entity_id(polity)
                context["release_entities"].setdefault(
                    candidate_entity_id,
                    {
                        "id": candidate_entity_id,
                        "name": str(polity.get("canonical_name_candidate") or candidate_entity_id),
                        "start_year": int(polity["start_year"]),
                        "end_year": int(polity["end_year"]),
                    },
                )
            resolved.append(str(entity_id))
        entity_ids = sorted(set(resolved)) if failure_reason is None else []
        return {
            "key": _side_key(candidate_id, side_name),
            "side": side_name,
            "label": normalized,
            "label_raw": "" if label is None else str(label),
            "codes": list(codes),
            "entity_ids": entity_ids,
            "initial_entity_ids": list(entity_ids),
            "resolution": "seshat_crosswalk" if entity_ids else "unresolved",
            "tier": "seshat_crosswalk" if entity_ids else None,
            "reason": failure_reason,
            "failure_case": (
                None
                if entity_ids
                else f"seshat_code_{failure_reason or 'unresolved'}"
            ),
            "candidate_entities": _candidate_matches(
                label, low_year, high_year, context
            ),
        }

    if project_policy:
        entity_id, polity, reason, tier = resolve_wave6_pre1500_candidate_side_label(
            row,
            label,
            low_year,
            high_year,
            context,
            lambda generic_label, generic_low, generic_high: resolve_hced_side_label(
                generic_label, generic_low, generic_high, context
            ),
        )
    else:
        entity_id, polity, reason, tier = resolve_hced_side_label(
            label, low_year, high_year, context
        )
    if polity is not None and entity_id:
        context["release_entities"].setdefault(
            str(entity_id),
            {
                "id": str(entity_id),
                "name": str(polity.get("canonical_name_candidate") or entity_id),
                "start_year": int(polity["start_year"]),
                "end_year": int(polity["end_year"]),
            },
        )
    candidates = _candidate_matches(label, low_year, high_year, context)
    entity_ids = [str(entity_id)] if entity_id else []
    return {
        "key": _side_key(candidate_id, side_name),
        "side": side_name,
        "label": normalized,
        "label_raw": "" if label is None else str(label),
        "codes": [],
        "entity_ids": entity_ids,
        "initial_entity_ids": list(entity_ids),
        "resolution": "current_label_rule" if entity_id else "unresolved",
        "tier": tier,
        "reason": reason,
        "failure_case": (
            None
            if entity_id
            else _detailed_label_failure(
                label, low_year, high_year, reason, candidates
            )
        ),
        "candidate_entities": candidates,
    }


def _row_display_name(row: Mapping[str, Any]) -> str:
    return str(
        row.get("name")
        or row.get("source_record_id")
        or row.get("candidate_id")
        or "Unnamed HCED row"
    )


def _row_location(row: Mapping[str, Any]) -> dict[str, Any]:
    country = str(row.get("modern_location_country") or "").strip()
    try:
        latitude = float(row["latitude"]) if row.get("latitude") not in (None, "") else None
        longitude = float(row["longitude"]) if row.get("longitude") not in (None, "") else None
    except (TypeError, ValueError):
        latitude = longitude = None
    return {
        "modern_location_country": country or None,
        "latitude": latitude,
        "longitude": longitude,
    }


def _prepare_observations(
    hced_rows: list[dict[str, Any]],
    seed_events: list[dict[str, Any]],
    context: dict[str, Any],
    *,
    project_policy: bool,
) -> tuple[dict[str, list[tuple[int, int, str]]], set[str], set[tuple[str, int]]]:
    observations: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    accepted_ids: set[str] = set()
    accepted_keys: set[tuple[str, int]] = set()
    curated_seed_keys = {
        _event_key(str(event["name"]), int(event["year"])) for event in seed_events
    }
    exclusions = _PROJECT_CROSSWALK_EXCLUSIONS if project_policy else {}
    reserved = WAVE6_HCED_RESERVED_IDS if project_policy else frozenset()

    for row in hced_rows:
        candidate_id = hced_candidate_id(row)
        interval = _valid_interval(row)
        exact_contract = (
            WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS.get(candidate_id)
            if project_policy
            else None
        )
        codes_1 = row.get("seshat_side_1_candidates", [])
        codes_2 = row.get("seshat_side_2_candidates", [])
        if (
            candidate_id in exclusions
            or candidate_id in reserved
            or row.get("duplicate_source_id")
            or interval is None
            or (exact_contract is None and (not codes_1 or not codes_2))
            or not _outcome_aligned(row)
        ):
            continue
        low_year, high_year = interval
        sides = [
            _resolve_side(row, "side_1", context, project_policy=project_policy),
            _resolve_side(row, "side_2", context, project_policy=project_policy),
        ]
        if any(not side["entity_ids"] for side in sides):
            continue
        if set(sides[0]["entity_ids"]) & set(sides[1]["entity_ids"]):
            continue
        event_key = _event_key(_row_display_name(row), int(row["year_best"]))
        if event_key in curated_seed_keys:
            continue
        accepted_ids.add(candidate_id)
        accepted_keys.add(event_key)
        reviewed_targets: set[str] = set()
        if exact_contract is not None:
            reviewed_targets.update(map(str, exact_contract["side_1"]))
            reviewed_targets.update(map(str, exact_contract["side_2"]))
        binding = (
            HCED_REVIEWED_CROSSWALK_IDENTITY_BINDINGS.get(candidate_id)
            if project_policy
            else None
        )
        if binding is not None:
            reviewed_targets.update(map(str, binding["code_bindings"].values()))
        for side in sides:
            if len(side["entity_ids"]) != 1:
                continue
            entity_id = side["entity_ids"][0]
            if entity_id in reviewed_targets or not side["label"]:
                continue
            observations[side["label"]].append((low_year, high_year, entity_id))
    return (
        {label: sorted(values) for label, values in sorted(observations.items())},
        accepted_ids,
        accepted_keys,
    )


def _classify_rows(
    hced_rows: list[dict[str, Any]],
    seed_events: list[dict[str, Any]],
    context: dict[str, Any],
    crosswalk_accepted_ids: set[str],
    crosswalk_accepted_keys: set[tuple[str, int]],
    *,
    project_policy: bool,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    row_states: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    curated_seed_keys = {
        _event_key(str(event["name"]), int(event["year"])) for event in seed_events
    }
    promoted_keys = set(crosswalk_accepted_keys)
    accepted_label_keys: set[tuple[str, int, str]] = set()
    exclusions = _PROJECT_CROSSWALK_EXCLUSIONS if project_policy else {}
    reserved = WAVE6_HCED_RESERVED_IDS if project_policy else frozenset()
    label_exclusions = HCED_LABEL_CURATED_EXCLUSIONS if project_policy else {}

    for source_order, row in enumerate(hced_rows):
        candidate_id = hced_candidate_id(row)
        interval = _valid_interval(row)
        exact_contract = (
            WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS.get(candidate_id)
            if project_policy
            else None
        )
        codes_1 = row.get("seshat_side_1_candidates", [])
        codes_2 = row.get("seshat_side_2_candidates", [])
        label_pass = exact_contract is None and (not codes_1 or not codes_2)
        war_keys = _normalized_war_names(row)
        state: dict[str, Any] = {
            "candidate_id": candidate_id,
            "source_order": source_order,
            "name": _row_display_name(row),
            "year_low": interval[0] if interval else None,
            "year_best": row.get("year_best"),
            "year_high": interval[1] if interval else None,
            "war_keys": list(war_keys),
            "war_names": sorted({str(name).strip() for name in row.get("war_names", []) if str(name).strip()}),
            "location": _row_location(row),
            "event_type": str(row.get("proposed_event_type") or "engagement"),
            "label_pass": label_pass,
            "status": "outside_scope",
            "row_failure_cases": [],
            "proposal_eligible": False,
            "sides": [],
            "source_snapshot": str(row.get("source_snapshot") or ""),
        }
        if candidate_id in reserved:
            state["status"] = "candidate_keyed_lane"
        elif candidate_id in exclusions:
            state["status"] = "curated_exclusion"
        elif row.get("duplicate_source_id"):
            state["status"] = "duplicate_source_id"
        elif interval is None:
            state["status"] = "missing_or_invalid_year"
        else:
            state["sides"] = [
                _resolve_side(row, "side_1", context, project_policy=project_policy),
                _resolve_side(row, "side_2", context, project_policy=project_policy),
            ]
            side_failures = [
                side["failure_case"]
                for side in state["sides"]
                if side.get("failure_case")
            ]
            if candidate_id in crosswalk_accepted_ids:
                state["status"] = "crosswalk_resolved"
            elif not label_pass:
                state["status"] = "crosswalk_staged"
                state["row_failure_cases"].extend(side_failures)
            elif candidate_id in label_exclusions:
                state["status"] = "label_curated_exclusion"
                state["row_failure_cases"].append("curated_row_exclusion")
            elif not _outcome_aligned(row):
                state["status"] = "label_other_staged"
                state["row_failure_cases"].append("label_outcome_not_aligned")
            elif side_failures:
                state["status"] = "label_identity_unresolved"
                state["row_failure_cases"].extend(side_failures)
                # Proposals can address missing uncoded-side identities only;
                # a broken Seshat code or a row-level semantic failure remains
                # outside the propagation gate.
                state["proposal_eligible"] = all(
                    not side["codes"] or side["entity_ids"]
                    for side in state["sides"]
                )
            elif (
                not state["sides"][0]["entity_ids"]
                or not state["sides"][1]["entity_ids"]
                or set(state["sides"][0]["entity_ids"])
                & set(state["sides"][1]["entity_ids"])
            ):
                state["status"] = "label_other_staged"
                state["row_failure_cases"].append("same_or_empty_opposing_side")
            else:
                event_key = _event_key(state["name"], int(row["year_best"]))
                label_key = _hced_label_row_key(row, state["name"], int(row["year_best"]))
                if event_key in curated_seed_keys:
                    state["status"] = "label_other_staged"
                    state["row_failure_cases"].append("duplicate_of_curated_seed")
                elif event_key in promoted_keys or label_key in accepted_label_keys:
                    state["status"] = "label_other_staged"
                    state["row_failure_cases"].append("duplicate_of_promoted_event")
                else:
                    state["status"] = "label_resolved"
                    promoted_keys.add(event_key)
                    accepted_label_keys.add(label_key)
        state["row_failure_cases"] = sorted(set(state["row_failure_cases"]))
        status_counts[state["status"]] += 1
        row_states.append(state)
    return row_states, status_counts


def _entity_metadata(
    entity_id: str, context: Mapping[str, Any]
) -> dict[str, Any] | None:
    metadata = context["entity_catalog"].get(entity_id)
    if metadata is not None:
        return metadata
    entity = context["release_entities"].get(entity_id)
    if entity is None:
        return None
    return {
        "id": entity_id,
        "name": str(entity.get("name") or entity_id),
        "start_year": int(entity["start_year"]),
        "end_year": entity.get("end_year"),
        "identity_status": "curated",
        "coverage_discontinuous": False,
    }


def _proposal_gate(
    side: Mapping[str, Any],
    row: Mapping[str, Any],
    entity_id: str,
    war_rows: list[dict[str, Any]],
    context: Mapping[str, Any],
) -> str | None:
    label = str(side["label"])
    if not label:
        return "blank_side_label"
    if label in HCED_FACTION_LABELS:
        return "faction_label_not_a_polity"
    if label in HCED_PENDING_SPLIT_LABELS:
        return "known_multi_regime_or_pending_split_label"
    if label in HCED_LABEL_POLICIES:
        return "declared_label_policy_is_authoritative"
    if _overlaps_deny_window(label, int(row["year_low"]), int(row["year_high"])):
        return "identity_deny_window"
    entity = _entity_metadata(entity_id, context)
    if entity is None:
        return "proposed_entity_missing_from_identity_context"
    if not _entity_covers(entity, int(row["year_low"]), int(row["year_high"])):
        return "proposed_entity_outside_event_interval"
    if entity.get("coverage_discontinuous"):
        return "discontinuous_source_identity_envelope"
    valid_candidates = {
        str(candidate["entity_id"])
        for candidate in side["candidate_entities"]
        if candidate["time_valid"]
    }
    if valid_candidates and valid_candidates != {entity_id}:
        return "conflicting_time_valid_label_candidate"
    if any(
        candidate["coverage_discontinuous"]
        for candidate in side["candidate_entities"]
        if candidate["entity_id"] == entity_id
    ):
        return "discontinuous_source_identity_envelope"

    # A label whose exact candidates change inside one normalized war is a
    # succession/multi-regime envelope.  Co-war evidence must not bridge it.
    candidate_ids_across_war: set[str] = set()
    for other_row in war_rows:
        for other_side in other_row["sides"]:
            if other_side["label"] != label:
                continue
            candidate_ids_across_war.update(
                str(candidate["entity_id"])
                for candidate in other_side["candidate_entities"]
                if candidate["time_valid"]
            )
            candidate_ids_across_war.update(map(str, other_side["initial_entity_ids"]))
    if len(candidate_ids_across_war) > 1:
        return "war_spans_conflicting_identity_intervals"
    return None


def _working_ids(side: Mapping[str, Any], proposals: Mapping[str, dict[str, Any]]) -> tuple[str, ...]:
    if side["initial_entity_ids"]:
        return tuple(map(str, side["initial_entity_ids"]))
    proposal = proposals.get(str(side["key"]))
    return (str(proposal["entity_id"]),) if proposal is not None else ()


def _fixed_point_proposals(
    row_states: list[dict[str, Any]],
    context: Mapping[str, Any],
) -> tuple[dict[str, dict[str, Any]], Counter[str], int]:
    wars: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in row_states:
        if row["status"] not in {
            "crosswalk_resolved",
            "label_resolved",
            "label_identity_unresolved",
        }:
            continue
        for war_key in row["war_keys"]:
            wars[war_key].append(row)

    proposals: dict[str, dict[str, Any]] = {}
    rejected: Counter[str] = Counter()
    rejection_keys: set[tuple[str, str, str]] = set()
    rounds = 0

    def reject(side_key: str, war_key: str, reason: str) -> None:
        key = (side_key, war_key, reason)
        if key not in rejection_keys:
            rejection_keys.add(key)
            rejected[reason] += 1

    while True:
        pending: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for war_key in sorted(wars):
            war_rows = sorted(wars[war_key], key=lambda row: (row["source_order"], row["candidate_id"]))
            label_anchors: dict[str, set[str]] = defaultdict(set)
            anchor_sides: dict[tuple[str, str], list[str]] = defaultdict(list)
            seshat_entities: set[str] = set()
            coalition_present = False
            initial_pair_rows: list[tuple[str, str, str]] = []
            resolved_entities: set[str] = set()

            for row in war_rows:
                ids_by_side = []
                for side in row["sides"]:
                    ids = _working_ids(side, proposals)
                    ids_by_side.append(ids)
                    if len(ids) > 1:
                        coalition_present = True
                    if len(ids) == 1:
                        entity_id = ids[0]
                        resolved_entities.add(entity_id)
                        if side["label"]:
                            label_anchors[side["label"]].add(entity_id)
                            anchor_sides[(side["label"], entity_id)].append(side["key"])
                        if side["resolution"] in {
                            "seshat_crosswalk",
                            "exact_reviewed_candidate_contract",
                        }:
                            seshat_entities.add(entity_id)
                if (
                    len(ids_by_side) == 2
                    and len(ids_by_side[0]) == 1
                    and len(ids_by_side[1]) == 1
                    and ids_by_side[0][0] != ids_by_side[1][0]
                    and all(side["initial_entity_ids"] for side in row["sides"])
                ):
                    pair = tuple(sorted((ids_by_side[0][0], ids_by_side[1][0])))
                    initial_pair_rows.append((pair[0], pair[1], row["candidate_id"]))

            root_pairs = {(left, right) for left, right, _ in initial_pair_rows}
            binary_pair: tuple[str, str] | None = None
            if (
                not coalition_present
                and len(root_pairs) == 1
                and len(initial_pair_rows) >= MIN_BINARY_ANCHOR_ROWS
            ):
                candidate_pair = next(iter(root_pairs))
                if set(candidate_pair).issubset(seshat_entities) and resolved_entities.issubset(
                    set(candidate_pair)
                ):
                    binary_pair = candidate_pair

            for row in war_rows:
                if not row["proposal_eligible"]:
                    continue
                for side_index, side in enumerate(row["sides"]):
                    side_key = str(side["key"])
                    if _working_ids(side, proposals) or side["codes"]:
                        continue
                    label_ids = label_anchors.get(side["label"], set())
                    entity_id: str | None = None
                    rule: str | None = None
                    evidence_side_keys: list[str] = []
                    if len(label_ids) == 1:
                        entity_id = next(iter(label_ids))
                        rule = "same_normalized_label_in_war"
                        evidence_side_keys = sorted(
                            anchor_sides[(side["label"], entity_id)]
                        )
                    elif len(label_ids) > 1:
                        reject(side_key, war_key, "conflicting_same_label_war_anchors")
                        continue
                    elif binary_pair is not None:
                        opponent = row["sides"][1 - side_index]
                        opponent_ids = _working_ids(opponent, proposals)
                        if len(opponent_ids) == 1 and opponent_ids[0] in binary_pair:
                            entity_id = (
                                binary_pair[1]
                                if opponent_ids[0] == binary_pair[0]
                                else binary_pair[0]
                            )
                            # Every occurrence of this unresolved label in the
                            # war must face the same known opponent.  This keeps
                            # coalition labels from borrowing a binary edge.
                            opponents: set[str] = set()
                            for other_row in war_rows:
                                for other_index, other_side in enumerate(other_row["sides"]):
                                    if other_side["label"] != side["label"]:
                                        continue
                                    other_opponent = other_row["sides"][1 - other_index]
                                    other_ids = _working_ids(other_opponent, proposals)
                                    if len(other_ids) == 1:
                                        opponents.add(other_ids[0])
                            if opponents != {opponent_ids[0]}:
                                reject(side_key, war_key, "inconsistent_opponent_constraints")
                                continue
                            rule = "strict_binary_war_complement"
                            evidence_side_keys = sorted(
                                {
                                    side_key_value
                                    for left, right, candidate_id in initial_pair_rows
                                    if (left, right) == binary_pair
                                    for side_key_value in (
                                        f"{candidate_id}:side_1",
                                        f"{candidate_id}:side_2",
                                    )
                                }
                            )
                    if entity_id is None or rule is None:
                        reject(side_key, war_key, "insufficient_rooted_war_constraints")
                        continue
                    gate_failure = _proposal_gate(
                        side, row, entity_id, war_rows, context
                    )
                    if gate_failure:
                        reject(side_key, war_key, gate_failure)
                        continue
                    pending[side_key].append(
                        {
                            "side_key": side_key,
                            "candidate_id": row["candidate_id"],
                            "side": side["side"],
                            "label": side["label"],
                            "entity_id": entity_id,
                            "rule": rule,
                            "war_key": war_key,
                            "evidence_side_keys": evidence_side_keys,
                            "event_interval": [row["year_low"], row["year_high"]],
                        }
                    )

        accepted_this_round: dict[str, dict[str, Any]] = {}
        for side_key in sorted(pending):
            candidates = pending[side_key]
            entity_ids = {str(candidate["entity_id"]) for candidate in candidates}
            if len(entity_ids) != 1:
                for candidate in candidates:
                    reject(side_key, candidate["war_key"], "cross_war_proposal_conflict")
                continue
            entity_id = next(iter(entity_ids))
            rules = sorted({str(candidate["rule"]) for candidate in candidates})
            war_keys = sorted({str(candidate["war_key"]) for candidate in candidates})
            evidence = sorted(
                {
                    str(item)
                    for candidate in candidates
                    for item in candidate["evidence_side_keys"]
                }
            )
            first = sorted(
                candidates,
                key=lambda item: (
                    item["candidate_id"], item["side"], item["war_key"], item["rule"]
                ),
            )[0]
            accepted_this_round[side_key] = {
                "side_key": side_key,
                "candidate_id": first["candidate_id"],
                "side": first["side"],
                "normalized_label": first["label"],
                "entity_id": entity_id,
                "proposal_round": rounds + 1,
                "rules": rules,
                "war_keys": war_keys,
                "event_interval": first["event_interval"],
                "evidence_side_keys": evidence,
                "provenance": (
                    "Review-only co-war constraint rooted in current Seshat/code or "
                    "deterministic label resolutions. It is not an outcome assertion "
                    "and is never joined into the release automatically."
                ),
                "release_effect": "none",
            }
        if not accepted_this_round:
            break
        proposals.update(accepted_this_round)
        rounds += 1
    return proposals, rejected, rounds


def _network_components(results: Mapping[str, Any] | None) -> dict[str, int]:
    if not results:
        return {}
    components: dict[str, int] = {}
    for entity in results.get("entities", []):
        if entity.get("network_component") is None:
            continue
        components[str(entity["id"])] = int(entity["network_component"])
    return components


def _event_evidence_counts(
    release_events: Iterable[Mapping[str, Any]],
) -> tuple[Counter[str], Counter[tuple[str, str]]]:
    entity_counts: Counter[str] = Counter()
    pair_counts: Counter[tuple[str, str]] = Counter()
    for event in release_events:
        if event.get("status") == "excluded":
            continue
        participants = list(event.get("participants", []))
        ids = sorted({str(participant.get("entity_id")) for participant in participants if participant.get("entity_id")})
        entity_counts.update(ids)
        sides: dict[str, set[str]] = defaultdict(set)
        for participant in participants:
            if participant.get("entity_id") and participant.get("side") is not None:
                sides[str(participant["side"])].add(str(participant["entity_id"]))
        side_names = sorted(sides)
        for index, left_side in enumerate(side_names):
            for right_side in side_names[index + 1 :]:
                for left in sides[left_side]:
                    for right in sides[right_side]:
                        if left != right:
                            pair_counts[tuple(sorted((left, right)))] += 1
    return entity_counts, pair_counts


def information_value_score(
    entity_a: str | None,
    entity_b: str | None,
    *,
    event_type: str,
    entity_event_counts: Mapping[str, int],
    pair_event_counts: Mapping[tuple[str, str], int],
    network_components: Mapping[str, int],
) -> dict[str, Any]:
    """Return a documented prioritization heuristic, not a covariance estimate.

    Novel identities, cross-component edges, and strategic layers receive more
    weight. Repeated evidence for the same entities and pair decays as the
    inverse square root. This makes a bridge or strategic result outrank the
    hundredth tactical observation in an already dense dyad.
    """

    count_a = int(entity_event_counts.get(entity_a or "", 0))
    count_b = int(entity_event_counts.get(entity_b or "", 0))
    novelty = (
        1.0 / math.sqrt(1.0 + count_a) + 1.0 / math.sqrt(1.0 + count_b)
    ) / 2.0
    pair = tuple(sorted((entity_a, entity_b))) if entity_a and entity_b and entity_a != entity_b else None
    pair_count = int(pair_event_counts.get(pair, 0)) if pair else 0
    redundancy_decay = 1.0 / math.sqrt(1.0 + pair_count)
    component_a = network_components.get(entity_a or "")
    component_b = network_components.get(entity_b or "")
    if component_a is not None and component_b is not None:
        connectivity_multiplier = 3.0 if component_a != component_b else 1.0
        connectivity_case = (
            "bridges_existing_components"
            if component_a != component_b
            else "within_existing_component"
        )
    elif component_a is not None or component_b is not None:
        connectivity_multiplier = 1.8
        connectivity_case = "attaches_unassigned_identity"
    else:
        connectivity_multiplier = 1.25
        connectivity_case = "both_identities_unassigned_or_unknown"
    layer_multiplier = {
        "engagement": 1.0,
        "battle": 1.0,
        "campaign": 2.0,
        "war": 4.0,
    }.get(normalize_label(event_type), 1.0)
    score = round(
        100.0
        * novelty
        * redundancy_decay
        * connectivity_multiplier
        * layer_multiplier,
        6,
    )
    return {
        "score": score,
        "definition": (
            "100 × inverse-sqrt entity novelty × inverse-sqrt pair redundancy "
            "× connectivity multiplier × evidence-layer multiplier; a queue-order "
            "heuristic, not a modeled posterior uncertainty reduction."
        ),
        "entity_event_counts": {"a": count_a, "b": count_b},
        "existing_pair_event_count": pair_count,
        "novelty_factor": round(novelty, 9),
        "redundancy_decay": round(redundancy_decay, 9),
        "connectivity_case": connectivity_case,
        "connectivity_multiplier": connectivity_multiplier,
        "network_components": {"a": component_a, "b": component_b},
        "layer_multiplier": layer_multiplier,
    }


def _resolved_or_placeholder(
    side: Mapping[str, Any],
    proposals: Mapping[str, dict[str, Any]],
) -> str | None:
    ids = _working_ids(side, proposals)
    return ids[0] if len(ids) == 1 else None


def _war_report_rows(
    row_states: list[dict[str, Any]],
    proposals: Mapping[str, dict[str, Any]],
    rejected: Mapping[str, int],
    context: Mapping[str, Any],
    release_events: list[dict[str, Any]],
    results: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    del rejected  # Top-level gate counts are reported once, without duplication.
    wars: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in row_states:
        if row["status"] not in {
            "crosswalk_resolved",
            "label_resolved",
            "label_identity_unresolved",
        }:
            continue
        for war_key in row["war_keys"]:
            wars[war_key].append(row)
    components = _network_components(results)
    entity_counts, pair_counts = _event_evidence_counts(release_events)
    reports: list[dict[str, Any]] = []

    for war_key in sorted(wars):
        rows = sorted(wars[war_key], key=lambda row: (row["source_order"], row["candidate_id"]))
        unresolved = [row for row in rows if row["status"] == "label_identity_unresolved"]
        if not unresolved:
            continue
        label_stats: dict[str, dict[str, Any]] = {}
        candidate_entities: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        failure_cases: Counter[str] = Counter()
        anchor_identity_rows: dict[str, set[str]] = defaultdict(set)
        anchor_codes: dict[str, set[str]] = defaultdict(set)
        counterpart_identity_rows: dict[str, set[str]] = defaultdict(set)
        resolved_context_pairs: Counter[tuple[str, str]] = Counter()
        proposal_ready_rows: list[str] = []
        proposal_rows: list[dict[str, Any]] = []
        bridge_pairs: dict[tuple[str, str], dict[str, Any]] = {}
        information_rows: list[tuple[float, str, dict[str, Any]]] = []

        for row in rows:
            side_ids = [_resolved_or_placeholder(side, proposals) for side in row["sides"]]
            if all(side_ids) and side_ids[0] != side_ids[1]:
                resolved_context_pairs[tuple(sorted((str(side_ids[0]), str(side_ids[1]))))] += 1
            for side in row["sides"]:
                if len(side["initial_entity_ids"]) == 1 and side["resolution"] in {
                    "seshat_crosswalk",
                    "exact_reviewed_candidate_contract",
                }:
                    entity_id = str(side["initial_entity_ids"][0])
                    anchor_identity_rows[entity_id].add(row["candidate_id"])
                    anchor_codes[entity_id].update(map(str, side["codes"]))
            if row not in unresolved:
                continue
            failure_cases.update(row["row_failure_cases"])
            all_final_ids: list[str | None] = []
            proposed_in_row = False
            for side in row["sides"]:
                stats = label_stats.setdefault(
                    side["label"],
                    {
                        "normalized_label": side["label"],
                        "raw_labels": set(),
                        "occurrences": 0,
                        "unresolved_occurrences": 0,
                        "sides": set(),
                    },
                )
                stats["raw_labels"].add(side["label_raw"])
                stats["occurrences"] += 1
                stats["sides"].add(side["side"])
                if not side["initial_entity_ids"]:
                    stats["unresolved_occurrences"] += 1
                for candidate in side["candidate_entities"]:
                    candidate_entities[side["label"]][candidate["entity_id"]] = candidate
                final_id = _resolved_or_placeholder(side, proposals)
                all_final_ids.append(final_id)
                if len(side["initial_entity_ids"]) == 1:
                    counterpart_identity_rows[str(side["initial_entity_ids"][0])].add(
                        row["candidate_id"]
                    )
                proposal = proposals.get(side["key"])
                if proposal is not None:
                    proposed_in_row = True
                    proposal_rows.append(proposal)
            ready = (
                proposed_in_row
                and all(all_final_ids)
                and all_final_ids[0] != all_final_ids[1]
            )
            if ready:
                proposal_ready_rows.append(row["candidate_id"])
            entity_a = all_final_ids[0]
            entity_b = all_final_ids[1]
            info = information_value_score(
                entity_a,
                entity_b,
                event_type=row["event_type"],
                entity_event_counts=entity_counts,
                pair_event_counts=pair_counts,
                network_components=components,
            )
            information_rows.append((float(info["score"]), row["candidate_id"], info))
            if entity_a and entity_b and entity_a != entity_b:
                component_a = components.get(entity_a)
                component_b = components.get(entity_b)
                if component_a != component_b:
                    pair = tuple(sorted((entity_a, entity_b)))
                    bridge_pairs[pair] = {
                        "entity_ids": list(pair),
                        "network_components": sorted(
                            {component for component in (component_a, component_b) if component is not None}
                        ),
                        "case": (
                            "bridges_existing_components"
                            if component_a is not None and component_b is not None
                            else "attaches_unassigned_identity"
                        ),
                    }

        countries = sorted(
            {
                str(row["location"]["modern_location_country"])
                for row in unresolved
                if row["location"]["modern_location_country"]
            }
        )
        points = sorted(
            {
                (float(row["location"]["latitude"]), float(row["location"]["longitude"]))
                for row in unresolved
                if row["location"]["latitude"] is not None
                and row["location"]["longitude"] is not None
            }
        )
        coordinate_bounds = None
        if points:
            coordinate_bounds = {
                "south": min(point[0] for point in points),
                "north": max(point[0] for point in points),
                "west": min(point[1] for point in points),
                "east": max(point[1] for point in points),
            }
        top_info = max(
            information_rows,
            key=lambda item: (item[0], item[1]),
        )
        reports.append(
            {
                "war_key": war_key,
                "display_names": sorted(
                    {
                        display
                        for row in rows
                        for display in row["war_names"]
                        if normalize_label(display) == war_key
                    }
                ),
                "rows_total": len(rows),
                "label_pass_rows": sum(bool(row["label_pass"]) for row in rows),
                "identity_unresolved_rows": len(unresolved),
                "identity_unresolved_row_ids": sorted(row["candidate_id"] for row in unresolved),
                "years": {
                    "low": min(int(row["year_low"]) for row in unresolved),
                    "high": max(int(row["year_high"]) for row in unresolved),
                    "observed_years": sorted(
                        {
                            int(row["year_best"])
                            for row in unresolved
                            if row["year_best"] is not None
                        }
                    ),
                },
                "locations": {
                    "modern_location_countries": countries,
                    "distinct_coordinate_points": len(points),
                    "coordinate_bounds": coordinate_bounds,
                },
                "distinct_labels_and_sides": [
                    {
                        **{key: value for key, value in stats.items() if key not in {"raw_labels", "sides"}},
                        "raw_labels": sorted(label for label in stats["raw_labels"] if label),
                        "sides": sorted(stats["sides"]),
                    }
                    for _, stats in sorted(label_stats.items())
                ],
                "seshat_anchors": {
                    "rows": len({row_id for values in anchor_identity_rows.values() for row_id in values}),
                    "identities": [
                        {
                            "entity_id": entity_id,
                            "name": str((_entity_metadata(entity_id, context) or {}).get("name") or entity_id),
                            "row_count": len(anchor_identity_rows[entity_id]),
                            "row_ids": sorted(anchor_identity_rows[entity_id]),
                            "seshat_codes": sorted(anchor_codes[entity_id]),
                        }
                        for entity_id in sorted(anchor_identity_rows)
                    ],
                },
                "already_resolved_counterparts": {
                    "rows": len({row_id for values in counterpart_identity_rows.values() for row_id in values}),
                    "identities": [
                        {
                            "entity_id": entity_id,
                            "name": str((_entity_metadata(entity_id, context) or {}).get("name") or entity_id),
                            "row_count": len(counterpart_identity_rows[entity_id]),
                            "row_ids": sorted(counterpart_identity_rows[entity_id]),
                        }
                        for entity_id in sorted(counterpart_identity_rows)
                    ],
                },
                "resolved_context_pairs": [
                    {"entity_ids": list(pair), "rows": count}
                    for pair, count in sorted(resolved_context_pairs.items())
                ],
                "candidate_entities_by_label": [
                    {
                        "normalized_label": label,
                        "candidates": [
                            candidate_entities[label][entity_id]
                            for entity_id in sorted(candidate_entities[label])
                        ],
                    }
                    for label in sorted(candidate_entities)
                ],
                "failure_cases": dict(sorted(failure_cases.items())),
                "constraint_proposals": sorted(
                    {proposal["side_key"]: proposal for proposal in proposal_rows}.values(),
                    key=lambda proposal: proposal["side_key"],
                ),
                "proposal_ready_rows": sorted(set(proposal_ready_rows)),
                "opponent_component_bridging_potential": {
                    "pairs": [bridge_pairs[pair] for pair in sorted(bridge_pairs)],
                    "pair_count": len(bridge_pairs),
                },
                "information_value": {
                    **top_info[2],
                    "score_basis_row_id": top_info[1],
                    "aggregation": (
                        "Maximum unresolved-row score, not a sum; war volume does not "
                        "overpower marginal-information and connectivity decay."
                    ),
                },
            }
        )
    return sorted(
        reports,
        key=lambda war: (
            -float(war["information_value"]["score"]),
            -int(war["identity_unresolved_rows"]),
            str(war["war_key"]),
        ),
    )


def analyze_war_constraints(
    hced_rows: list[dict[str, Any]],
    polity_rows: list[dict[str, Any]],
    seed_entities: list[dict[str, Any]],
    seed_events: list[dict[str, Any]],
    *,
    release_events: list[dict[str, Any]] | None = None,
    results: Mapping[str, Any] | None = None,
    project_policy: bool = False,
    input_fingerprints: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic, read-only co-war report from in-memory records."""

    context = _build_identity_context(
        seed_entities, polity_rows, project_policy=project_policy
    )
    observations, crosswalk_ids, crosswalk_keys = _prepare_observations(
        hced_rows,
        seed_events,
        context,
        project_policy=project_policy,
    )
    context["label_observations"] = observations
    context.update(
        {
            "polity_alias_index": context["candidate_alias_index"],
        }
    )
    row_states, status_counts = _classify_rows(
        hced_rows,
        seed_events,
        context,
        crosswalk_ids,
        crosswalk_keys,
        project_policy=project_policy,
    )
    proposals, gate_rejections, rounds = _fixed_point_proposals(row_states, context)
    release_event_rows = list(release_events or [])
    wars = _war_report_rows(
        row_states,
        proposals,
        gate_rejections,
        context,
        release_event_rows,
        results,
    )

    unresolved_rows = [
        row for row in row_states if row["status"] == "label_identity_unresolved"
    ]
    unresolved_with_war = [row for row in unresolved_rows if row["war_keys"]]
    war_keys_with_seshat_anchor = {
        war["war_key"] for war in wars if war["seshat_anchors"]["rows"] > 0
    }
    unresolved_in_anchored_war = {
        row["candidate_id"]
        for row in unresolved_with_war
        if set(row["war_keys"]) & war_keys_with_seshat_anchor
    }
    proposal_ready_rows = {
        row_id for war in wars for row_id in war["proposal_ready_rows"]
    }
    failure_cases: Counter[str] = Counter()
    for row in unresolved_rows:
        failure_cases.update(row["row_failure_cases"])

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "read_only": True,
        "release_mutation": "none",
        "provenance": {
            "input_fingerprints": dict(sorted((input_fingerprints or {}).items())),
            "source_snapshots": sorted(
                {
                    row["source_snapshot"]
                    for row in row_states
                    if row["source_snapshot"]
                }
            ),
            "project_policy_applied": project_policy,
        },
        "method": {
            "war_grouping": "Exact normalize_label(war_names) keys; no fuzzy war merge.",
            "current_resolution": (
                "Seshat/code policies and the HCED label front gates are evaluated "
                "with full event-interval coverage and unique exact-normalized aliases."
            ),
            "fixed_point": (
                "Suggestions propagate only from already-resolved sides by the same "
                "normalized label, or by a strict binary-war complement rooted in at "
                f"least {MIN_BINARY_ANCHOR_ROWS} fully resolved rows and Seshat/code "
                "anchors for both identities. New suggestions may unlock a later round."
            ),
            "hard_rejections": [
                "blank, faction, pending-split, explicit-policy, and deny-window labels",
                "out-of-interval or discontinuous identities",
                "multiple or conflicting time-valid candidates",
                "war-spanning identity changes",
                "coalition or non-binary war envelopes for complement propagation",
                "cross-war proposal conflicts",
            ],
            "proposal_semantics": (
                "A proposal is a review lead, not a promotion, participant adjudication, "
                "outcome assertion, or permission to modify the release."
            ),
            "information_value": (
                "A transparent queue-order heuristic weights identity novelty, pair "
                "redundancy, opponent-component bridging, and evidence layer. It is not "
                "a fitted D-optimal design or a posterior uncertainty estimate."
            ),
        },
        "summary": {
            "hced_rows": len(hced_rows),
            "crosswalk_resolved_rows": status_counts["crosswalk_resolved"],
            "label_pass_rows": sum(row["label_pass"] for row in row_states if row["status"] not in {"candidate_keyed_lane", "curated_exclusion", "duplicate_source_id", "missing_or_invalid_year"}),
            "label_resolved_rows": status_counts["label_resolved"],
            "label_identity_unresolved_rows": len(unresolved_rows),
            "label_other_staged_rows": status_counts["label_other_staged"] + status_counts["label_curated_exclusion"],
            "identity_unresolved_rows_with_war": len(unresolved_with_war),
            "identity_unresolved_rows_without_war": len(unresolved_rows) - len(unresolved_with_war),
            "identity_unresolved_rows_in_seshat_anchored_war": len(unresolved_in_anchored_war),
            "normalized_wars_with_identity_unresolved_rows": len(wars),
            "failure_cases": dict(sorted(failure_cases.items())),
            "fixed_point_rounds": rounds,
            "review_only_proposed_sides": len(proposals),
            "genuinely_unambiguous_rows_under_gate": len(proposal_ready_rows),
            "proposal_ready_row_ids": sorted(proposal_ready_rows),
            "proposal_gate_rejections": dict(sorted(gate_rejections.items())),
            "row_statuses": dict(sorted(status_counts.items())),
        },
        "rankings": {
            "by_information_value": [
                {
                    "rank": index + 1,
                    "war_key": war["war_key"],
                    "score": war["information_value"]["score"],
                    "identity_unresolved_rows": war["identity_unresolved_rows"],
                    "proposal_ready_rows": len(war["proposal_ready_rows"]),
                    "bridging_pairs": war["opponent_component_bridging_potential"]["pair_count"],
                }
                for index, war in enumerate(wars)
            ],
            "by_unresolved_volume": [
                {
                    "rank": index + 1,
                    "war_key": war["war_key"],
                    "identity_unresolved_rows": war["identity_unresolved_rows"],
                    "information_value_score": war["information_value"]["score"],
                    "proposal_ready_rows": len(war["proposal_ready_rows"]),
                }
                for index, war in enumerate(
                    sorted(
                        wars,
                        key=lambda war: (
                            -int(war["identity_unresolved_rows"]),
                            -float(war["information_value"]["score"]),
                            str(war["war_key"]),
                        ),
                    )
                )
            ],
        },
        "proposals": [proposals[key] for key in sorted(proposals)],
        "wars": wars,
    }
    body["determinism"] = {
        "canonical_body_sha256": _sha256_bytes(_canonical_bytes(body)),
        "ordering": "All maps and repeated records use explicit lexical/numeric sort keys.",
    }
    return body


def build_current_war_constraint_report(
    review_root: str | Path,
    seed_root: str | Path,
    release_root: str | Path,
    *,
    results_path: str | Path | None = None,
) -> dict[str, Any]:
    """Load the project's current corpus and build the read-only report."""

    review = Path(review_root)
    seed = Path(seed_root)
    release = Path(release_root)
    hced_path = review / "hced-candidates.jsonl"
    polity_path = review / "cliopatria-entity-candidates.jsonl"
    seed_entities_path = seed / "entities.json"
    seed_events_path = seed / "events.json"
    release_events_path = release / "events.json"
    paths = {
        "hced_candidates": hced_path,
        "cliopatria_candidates": polity_path,
        "seed_entities": seed_entities_path,
        "seed_events": seed_events_path,
        "release_events": release_events_path,
    }
    if results_path is not None:
        paths["results"] = Path(results_path)
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise ValueError("Missing war-constraint input(s): " + ", ".join(missing))
    results = _read_json(results_path) if results_path is not None else None
    return analyze_war_constraints(
        read_jsonl(hced_path),
        read_jsonl(polity_path),
        _read_json(seed_entities_path),
        _read_json(seed_events_path),
        release_events=_read_json(release_events_path),
        results=results,
        project_policy=True,
        input_fingerprints={key: _file_fingerprint(path) for key, path in paths.items()},
    )


def render_war_constraint_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_war_constraint_markdown(
    report: Mapping[str, Any], *, top: int = 20
) -> str:
    summary = report["summary"]
    lines = [
        "# HCED unresolved co-war constraint report",
        "",
        "> Read-only diagnostic. Proposals are review leads and never modify the release.",
        "",
        "## Measured scope",
        "",
        f"- HCED rows: {summary['hced_rows']:,}",
        f"- Label-pass rows: {summary['label_pass_rows']:,}",
        f"- Identity-unresolved label-pass rows: {summary['label_identity_unresolved_rows']:,}",
        f"- Identity-unresolved rows with a normalized war: {summary['identity_unresolved_rows_with_war']:,}",
        f"- Those linked to a war with a Seshat/code anchor: {summary['identity_unresolved_rows_in_seshat_anchored_war']:,}",
        f"- Review-only proposed sides: {summary['review_only_proposed_sides']:,}",
        f"- Genuinely unambiguous rows under the hard gate: {summary['genuinely_unambiguous_rows_under_gate']:,}",
        f"- Fixed-point rounds: {summary['fixed_point_rounds']:,}",
        "",
        "## Highest information-value wars",
        "",
        "| Rank | Normalized war | Score | Unresolved rows | Ready rows | Bridge pairs |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for row in report["rankings"]["by_information_value"][: max(0, top)]:
        lines.append(
            f"| {row['rank']} | {row['war_key']} | {row['score']:.6f} | "
            f"{row['identity_unresolved_rows']} | {row['proposal_ready_rows']} | "
            f"{row['bridging_pairs']} |"
        )
    lines.extend(
        [
            "",
            "## Largest unresolved wars",
            "",
            "| Rank | Normalized war | Unresolved rows | Information score | Ready rows |",
            "|---:|---|---:|---:|---:|",
        ]
    )
    for row in report["rankings"]["by_unresolved_volume"][: max(0, top)]:
        lines.append(
            f"| {row['rank']} | {row['war_key']} | {row['identity_unresolved_rows']} | "
            f"{row['information_value_score']:.6f} | {row['proposal_ready_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Proposal gate",
            "",
            report["method"]["fixed_point"],
            "",
            "The information score is only a transparent queue-order heuristic. "
            "It is not a posterior uncertainty estimate and volume is not summed.",
            "",
            f"Canonical report-body SHA-256: `{report['determinism']['canonical_body_sha256']}`",
            "",
        ]
    )
    return "\n".join(lines)


def write_war_constraint_report(
    report: Mapping[str, Any],
    output_dir: str | Path,
    *,
    basename: str = "war-constraints",
    top: int = 20,
) -> tuple[Path, Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    json_path = destination / f"{basename}.json"
    markdown_path = destination / f"{basename}.md"
    json_path.write_text(render_war_constraint_json(report), encoding="utf-8")
    markdown_path.write_text(
        render_war_constraint_markdown(report, top=top), encoding="utf-8"
    )
    return json_path, markdown_path
