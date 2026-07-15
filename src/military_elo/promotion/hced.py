from __future__ import annotations

"""HCED crosswalk and label-resolution promotion."""

from collections import Counter
from typing import Any

from .common import (
    _deduplicate,
    _domain,
    _event_key,
    _participants,
    _resolve_code,
    _resolve_label_tiers,
    _scale,
    _slug,
    _war_tokens,
    normalize_label,
)
from .hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
    build_hced_location_fields,
    hced_candidate_id,
)
from .policy import (
    HCED_CURATED_EXCLUSIONS,
    HCED_FACTION_LABELS,
    HCED_LABEL_CURATED_EXCLUSIONS,
    HCED_LABEL_POLICIES,
    HCED_PENDING_SPLIT_LABELS,
    _label_policy_seed_id,
)

def _hced_label_row_key(
    candidate: dict[str, Any], event_name: str, year: int
) -> tuple[str, int, str]:
    """Order-independent label-pass key with a source-row disambiguator."""
    source_identity = normalize_label(
        candidate.get("source_record_id") or candidate.get("candidate_id")
    )
    normalized_name, normalized_year = _event_key(event_name, year)
    return normalized_name, normalized_year, source_identity


def promote_hced_crosswalk_rows(
    candidates: list[dict[str, Any]],
    owners: dict[str, list[dict[str, Any]]],
    curated_seed_keys: set[tuple[str, int]],
    ensure_candidate_entity: Any,
) -> dict[str, Any]:
    """Promote HCED rows whose opposing sides both have Seshat codes."""
    events: list[dict[str, Any]] = []
    label_observations: dict[str, list[tuple[int, int, str]]] = {}
    rejections: Counter[str] = Counter()
    deferred_label_rows: list[dict[str, Any]] = []
    promoted_event_keys: set[tuple[str, int]] = set()
    cluster_spans: dict[str, list[Any]] = {}

    for candidate in candidates:
        candidate_id = hced_candidate_id(candidate)
        if candidate_id in HCED_CURATED_EXCLUSIONS:
            # Curated adjudications run before every other gate; the row is
            # counted, stays staged, and leaves every promotion universe
            # (including the IWBD dedup keys and label observations).
            rejections["curated_exclusion"] += 1
            continue
        if candidate.get("duplicate_source_id"):
            rejections["duplicate_source_id"] += 1
            continue
        if candidate.get("year_low") is None or candidate.get("year_high") is None:
            rejections["missing_or_invalid_year"] += 1
            continue
        low_year = int(candidate["year_low"])
        best_year = int(candidate["year_best"])
        high_year = int(candidate["year_high"])
        side_a_codes = _deduplicate(
            map(str, candidate.get("seshat_side_1_candidates", []))
        )
        side_b_codes = _deduplicate(
            map(str, candidate.get("seshat_side_2_candidates", []))
        )
        if not side_a_codes or not side_b_codes:
            # Rows lacking Seshat coding on a side are deferred to the second,
            # label-resolution promotion pass instead of being rejected here.
            deferred_label_rows.append(candidate)
            continue

        winner = normalize_label(candidate.get("winner_raw"))
        loser = normalize_label(candidate.get("loser_raw"))
        side_a_label = normalize_label(candidate.get("side_1_raw"))
        side_b_label = normalize_label(candidate.get("side_2_raw"))
        draw = winner in {"draw", "inconclusive", "stalemate"}
        # A blank winner is unknown, never a draw and never a vacuous match
        # against a blank side label.
        if not draw and (
            not winner or not loser or winner != side_a_label or loser != side_b_label
        ):
            rejections["outcome_not_aligned_to_crosswalk_sides"] += 1
            continue

        resolved_sides: list[list[str]] = []
        resolved_polities: dict[str, dict[str, Any]] = {}
        resolution_failed = False
        for codes in (side_a_codes, side_b_codes):
            resolved: list[str] = []
            for code in codes:
                entity_id, polity, reason = _resolve_code(
                    code, low_year, high_year, owners
                )
                if not entity_id:
                    rejections[reason or "unresolved_entity"] += 1
                    resolution_failed = True
                    break
                if polity:
                    resolved_polities[entity_id] = polity
                resolved.append(entity_id)
            if resolution_failed:
                break
            resolved_sides.append(_deduplicate(resolved))
        if resolution_failed:
            continue
        side_a, side_b = resolved_sides
        if not side_a or not side_b or set(side_a) & set(side_b):
            rejections["same_or_empty_opposing_side"] += 1
            continue

        event_name = str(
            candidate.get("name")
            or candidate.get("source_record_id")
            or "Unnamed engagement"
        )
        event_key = _event_key(event_name, best_year)
        if event_key in curated_seed_keys:
            rejections["duplicate_of_curated_seed"] += 1
            continue
        promoted_event_keys.add(event_key)

        for polity in resolved_polities.values():
            ensure_candidate_entity(polity)

        for label, entity_ids in (
            (side_a_label, side_a),
            (side_b_label, side_b),
        ):
            if label and len(entity_ids) == 1:
                label_observations.setdefault(label, []).append(
                    (low_year, high_year, entity_ids[0])
                )

        scale, scale_level = _scale(candidate)
        confidence = 0.73 if candidate.get("consulted_source_raw") else 0.67
        if low_year != high_year:
            confidence -= 0.03
        confidence = round(confidence, 2)
        war_names = list(map(str, candidate.get("war_names", [])))
        cluster = _slug(war_names[0]) if war_names else None
        if cluster:
            span = cluster_spans.setdefault(
                f"hced_war_{cluster}",
                [_war_tokens(war_names[0]), low_year, high_year],
            )
            span[1] = min(span[1], low_year)
            span[2] = max(span[2], high_year)
        events.append(
            {
                "id": f"hced_{_slug(candidate_id, 80)}",
                "name": event_name,
                "year": low_year,
                "end_year": high_year,
                "event_type": "engagement",
                "war_type": "interstate_limited",
                "scale": scale,
                "stakes": "major" if scale_level >= 4 else "limited",
                "decisiveness": 0.32
                if draw
                else round(min(0.90, 0.54 + 0.06 * scale_level), 2),
                "confidence": confidence,
                "geographic_scope": round(
                    min(0.70, 0.08 + 0.09 * scale_level), 2
                ),
                "domain": _domain(candidate.get("theatre_raw")),
                "cluster_id": f"hced_war_{cluster}" if cluster else None,
                "date_precision": "range" if low_year != high_year else "year",
                "sequence": int(candidate.get("source_row") or 0),
                "summary": (
                    "Provisional tactical result from HCED. Both opposing sides were resolved "
                    "through its Seshat crosswalk and a time-valid polity interval; this does "
                    "not infer the enclosing war's strategic outcome."
                ),
                "participants": _participants(
                    side_a,
                    side_b,
                    draw,
                    confidence,
                    scale_level,
                ),
                "source_ids": [
                    "hced_dataset",
                    "hced_seshat_crosswalk",
                    "cliopatria_v020",
                ],
                "outcome_source_ids": ["hced_dataset"],
                "outcome_source_family_ids": ["hced"],
                **build_hced_location_fields(
                    candidate,
                    point_quarantine_ids=HCED_POINT_QUARANTINE_IDS,
                    country_quarantine_ids=HCED_COUNTRY_QUARANTINE_IDS,
                ),
                "status": "complete",
            }
        )

    return {
        "events": events,
        "rejections": rejections,
        "deferred_label_rows": deferred_label_rows,
        "promoted_event_keys": promoted_event_keys,
        "label_observations": label_observations,
        "cluster_spans": cluster_spans,
    }


def resolve_hced_side_label(
    label: Any,
    low_year: int,
    high_year: int,
    context: dict[str, Any],
) -> tuple[str | None, dict[str, Any] | None, str | None, str | None]:
    """Resolve a bare HCED side label to a unique time-bounded identity.

    Returns ``(entity_id, polity, rejection_reason, tier)``. The three front
    gates (faction blocklist, pending-split set, label-policy table) are
    authoritative: a gated label never falls through to alias matching.
    """
    normalized = normalize_label(label)
    if not normalized:
        return None, None, "blank_side_label", None
    if normalized in HCED_FACTION_LABELS:
        return None, None, "faction_label_not_a_polity", None
    if normalized in HCED_PENDING_SPLIT_LABELS:
        return None, None, "label_pending_identity_split", None
    if normalized in HCED_LABEL_POLICIES:
        seed_id = _label_policy_seed_id(normalized, low_year, high_year)
        if seed_id:
            return seed_id, None, None, "label_policy"
        return None, None, "label_outside_policy_window", None
    entity_id, polity, tier = _resolve_label_tiers(
        normalized, low_year, high_year, context, require_observation_coherence=True
    )
    if entity_id:
        return entity_id, polity, None, tier
    return None, None, "no_unique_time_valid_label_match", None


def promote_hced_label_rows(
    deferred_rows: list[dict[str, Any]],
    curated_seed_keys: set[tuple[str, int]],
    promoted_event_keys: set[tuple[str, int]],
    resolve_code: Any,
    resolve_side_label: Any,
    curated_exclusions: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Second HCED promotion pass for rows lacking Seshat coding on a side.

    Deferred rows re-enter through a declared label-resolution ruleset: the
    coded side (if any) resolves through the unchanged Seshat-code path, the
    uncoded side only through explicit time-bounded label policies or exact
    time-valid alias matching with uniqueness. Label-resolved events carry
    reduced identity confidence and an ``identity_resolution`` provenance
    marker. Nothing here writes ``label_observations``: alias-derived
    resolutions must never launder themselves into the higher-trust
    observation tier, and results must not depend on row order.
    """
    if curated_exclusions is None:
        curated_exclusions = HCED_LABEL_CURATED_EXCLUSIONS
    events: list[dict[str, Any]] = []
    rejections: Counter[str] = Counter()
    resolved_polities: dict[str, dict[str, Any]] = {}
    observation_resolutions: Counter[tuple[str, str]] = Counter()
    cluster_spans: dict[str, list[Any]] = {}
    promoted_keys = set(promoted_event_keys)
    accepted_label_keys: set[tuple[str, int, str]] = set()

    for candidate in deferred_rows:
        candidate_id = hced_candidate_id(candidate)
        if candidate_id in curated_exclusions:
            # Curated adjudications run before every other gate: the row is
            # counted, never merged, and stays staged for human review.
            rejections["curated_row_exclusion"] += 1
            continue
        low_year = int(candidate["year_low"])
        best_year = int(candidate["year_best"])
        high_year = int(candidate["year_high"])
        winner = normalize_label(candidate.get("winner_raw"))
        loser = normalize_label(candidate.get("loser_raw"))
        side_a_label = normalize_label(candidate.get("side_1_raw"))
        side_b_label = normalize_label(candidate.get("side_2_raw"))
        draw = winner in {"draw", "inconclusive", "stalemate"}
        # A blank winner is unknown, never a draw and never a vacuous match
        # against a blank side label.
        if not draw and (
            not winner or not loser or winner != side_a_label or loser != side_b_label
        ):
            rejections["label_outcome_not_aligned"] += 1
            continue

        resolved_sides: list[list[str]] = []
        side_tiers: list[str] = []
        observation_hits: list[tuple[str, str]] = []
        pending_polities: dict[str, dict[str, Any]] = {}
        label_side_count = 0
        resolution_failed = False
        for codes, label in (
            (
                _deduplicate(map(str, candidate.get("seshat_side_1_candidates", []))),
                candidate.get("side_1_raw"),
            ),
            (
                _deduplicate(map(str, candidate.get("seshat_side_2_candidates", []))),
                candidate.get("side_2_raw"),
            ),
        ):
            resolved: list[str] = []
            if codes:
                for code in codes:
                    entity_id, polity, reason = resolve_code(code, low_year, high_year)
                    if not entity_id:
                        rejections[reason or "unresolved_entity"] += 1
                        resolution_failed = True
                        break
                    if polity:
                        pending_polities[entity_id] = polity
                    resolved.append(entity_id)
                side_tiers.append("seshat_crosswalk")
            else:
                entity_id, polity, reason, tier = resolve_side_label(
                    label, low_year, high_year
                )
                if not entity_id:
                    rejections[reason or "no_unique_time_valid_label_match"] += 1
                    resolution_failed = True
                else:
                    if polity:
                        pending_polities[entity_id] = polity
                    resolved.append(entity_id)
                    side_tiers.append(str(tier))
                    label_side_count += 1
                    if tier == "crosswalk_observation":
                        observation_hits.append((normalize_label(label), entity_id))
            if resolution_failed:
                break
            resolved_sides.append(_deduplicate(resolved))
        if resolution_failed:
            continue
        side_a, side_b = resolved_sides
        if not side_a or not side_b or set(side_a) & set(side_b):
            rejections["same_or_empty_opposing_side"] += 1
            continue

        event_name = str(
            candidate.get("name") or candidate.get("source_record_id") or "Unnamed engagement"
        )
        event_key = _event_key(event_name, best_year)
        if event_key in curated_seed_keys:
            rejections["duplicate_of_curated_seed"] += 1
            continue
        if event_key in promoted_keys:
            rejections["duplicate_of_promoted_event"] += 1
            continue
        label_row_key = _hced_label_row_key(candidate, event_name, best_year)
        if label_row_key in accepted_label_keys:
            rejections["duplicate_of_promoted_event"] += 1
            continue
        accepted_label_keys.add(label_row_key)
        resolved_polities.update(pending_polities)
        observation_resolutions.update(observation_hits)

        scale, scale_level = _scale(candidate)
        confidence = 0.73 if candidate.get("consulted_source_raw") else 0.67
        confidence -= 0.03 * label_side_count
        if low_year != high_year:
            confidence -= 0.03
        confidence = round(confidence, 2)
        war_names = list(map(str, candidate.get("war_names", [])))
        cluster = _slug(war_names[0]) if war_names else None
        if cluster:
            span = cluster_spans.setdefault(
                f"hced_war_{cluster}", [_war_tokens(war_names[0]), low_year, high_year]
            )
            span[1] = min(span[1], low_year)
            span[2] = max(span[2], high_year)
        source_ids = ["hced_dataset", "hced_seshat_crosswalk"]
        if any(entity_id.startswith("clio_") for entity_id in (*side_a, *side_b)):
            source_ids.append("cliopatria_v020")
        events.append(
            {
                "id": f"hced_label_{_slug(candidate_id, 74)}",
                "name": event_name,
                "year": low_year,
                "end_year": high_year,
                "event_type": "engagement",
                "war_type": "interstate_limited",
                "scale": scale,
                "stakes": "major" if scale_level >= 4 else "limited",
                "decisiveness": 0.32 if draw else round(min(0.90, 0.54 + 0.06 * scale_level), 2),
                "confidence": confidence,
                "geographic_scope": round(min(0.70, 0.08 + 0.09 * scale_level), 2),
                "domain": _domain(candidate.get("theatre_raw")),
                "cluster_id": f"hced_war_{cluster}" if cluster else None,
                "date_precision": "range" if low_year != high_year else "year",
                "sequence": int(candidate.get("source_row") or 0),
                "summary": (
                    "Provisional tactical result from HCED. At least one side lacked "
                    "Seshat crosswalk coding and was resolved by a declared, "
                    "time-bounded label policy or an exact time-valid alias match; "
                    "this carries lower identity confidence than crosswalk "
                    "resolution and does not infer the enclosing war's strategic "
                    "outcome."
                ),
                "identity_resolution": "label",
                "side_identity_resolution": {
                    "side_a": side_tiers[0],
                    "side_b": side_tiers[1],
                },
                "participants": _participants(
                    side_a,
                    side_b,
                    draw,
                    confidence,
                    scale_level,
                ),
                "source_ids": source_ids,
                "outcome_source_ids": ["hced_dataset"],
                "outcome_source_family_ids": ["hced"],
                **build_hced_location_fields(
                    candidate,
                    point_quarantine_ids=HCED_POINT_QUARANTINE_IDS,
                    country_quarantine_ids=HCED_COUNTRY_QUARANTINE_IDS,
                ),
                "status": "complete",
            }
        )

    return {
        "events": events,
        "rejections": rejections,
        "rows_total": len(deferred_rows),
        "accepted": len(events),
        "resolved_polities": resolved_polities,
        "observation_resolutions": [
            {"label": label, "entity_id": entity_id, "resolved_sides": count}
            for (label, entity_id), count in sorted(observation_resolutions.items())
        ],
        "cluster_spans": cluster_spans,
    }
