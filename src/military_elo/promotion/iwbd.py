from __future__ import annotations

"""Interstate War Battle Dataset tactical promotion."""

import re
from collections import Counter
from datetime import date
from typing import Any

from .common import (
    _cross_source_event_keys,
    _domain,
    _event_key,
    _participants,
    _slug,
    _war_tokens,
    _war_tokens_match,
    normalize_label,
)
from .policy import (
    IDENTITY_DENY_WINDOWS,
    IWBD_COALITION_SIDE_LABELS,
    IWBD_CURATED_EXCLUSIONS,
)

_IWBD_CANDIDATE_ID = re.compile(r"^iwbd-(-?\d+)-(-?\d+)-(\d+)$")


def _iwbd_id_parts(candidate_id: str) -> tuple[str, str, str] | None:
    match = _IWBD_CANDIDATE_ID.match(candidate_id)
    return (match.group(1), match.group(2), match.group(3)) if match else None


def _iwbd_dates(row: dict[str, Any]) -> tuple[date, date] | None:
    try:
        start = date.fromisoformat(str(row.get("start_date")))
        end = date.fromisoformat(str(row.get("end_date")))
    except (TypeError, ValueError):
        return None
    return (start, end) if end >= start else None


def _iwbd_base_war(row: dict[str, Any]) -> str:
    return re.sub(r"\s*\(.*\)$", "", str(row.get("war_name") or ""))


def _matches_hced_exact(
    hced_event_keys: set[tuple[str, int]] | dict[tuple[str, int], dict[str, Any]],
    exact_lookup_keys: set[tuple[str, int]],
) -> bool:
    if isinstance(hced_event_keys, dict):
        return any(
            bool(hced_event_keys.get(key, {}).get("exact"))
            for key in exact_lookup_keys
        )
    # Set input remains supported for focused callers that exercise only the
    # exact name/year gate. Production builds pass the orientation-aware index.
    return bool(exact_lookup_keys & hced_event_keys)


def _matches_hced_fuzzy(
    hced_event_keys: set[tuple[str, int]] | dict[tuple[str, int], dict[str, Any]],
    cross_source_lookup_keys: set[tuple[str, int]],
    outcome_signature: tuple[frozenset[str], frozenset[str]],
) -> bool:
    if not isinstance(hced_event_keys, dict):
        return False
    return any(
        outcome_signature in hced_event_keys.get(key, {}).get("outcomes", set())
        for key in cross_source_lookup_keys
    )


def promote_iwbd_battles(
    candidates: list[dict[str, Any]],
    curated_seed_keys: set[tuple[str, int]],
    hced_event_keys: set[tuple[str, int]] | dict[tuple[str, int], dict[str, Any]],
    resolve_label: Any,
    hced_war_cluster_spans: dict[str, list[Any]],
    iwd_parent_ids: set[str],
    curated_exclusions: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Promote non-duplicate IWBD battles as provisional tactical engagements.

    A battle enters only when it is not a duplicate of any curated seed event,
    any non-curated-excluded HCED candidate (promoted or staged), or an earlier
    accepted IWBD row. Exact normalized names use a one-year tolerance;
    base-name fuzzy matches require one recognized suffix path to extend the
    other, in the same year with an agreeing oriented outcome. Its
    date span must not strictly contain a differently-named battle of the same
    war (campaign umbrellas stay staged); its coded victor must match a named
    side (the inconclusive pair is a coded tactical stalemate, never a guess);
    both sides must be single polities resolving to unique time-bounded
    identities outside declared deny windows; and severity is capped at
    limited. The war-level victor code is ignored entirely: battles never
    update the strategic layer.
    """
    events: list[dict[str, Any]] = []
    rejections: Counter[str] = Counter()
    resolved_polities: dict[str, dict[str, Any]] = {}
    seen_keys: set[tuple[str, int]] = set()

    # Containment pre-pass over every row with a name and valid dates (not
    # just survivors), so the umbrella gate is order-independent: an IWBD
    # record whose span strictly contains a differently-named battle of the
    # same war is a presumptive campaign umbrella and stays staged.
    if curated_exclusions is None:
        curated_exclusions = IWBD_CURATED_EXCLUSIONS
    war_groups: dict[tuple[str, str], list[tuple[str, date, date]]] = {}
    for row in candidates:
        if str(row.get("candidate_id")) in curated_exclusions:
            continue
        name = str(row.get("name") or "")
        parsed = _iwbd_dates(row)
        parts = _iwbd_id_parts(str(row.get("candidate_id") or ""))
        if not name or parsed is None or parts is None:
            continue
        war_groups.setdefault(
            (parts[0], str(row.get("war_name") or "")), []
        ).append((name, parsed[0], parsed[1]))

    accepted_rows: list[dict[str, Any]] = []
    for row in sorted(candidates, key=lambda r: int(r.get("source_row") or 0)):
        if str(row.get("candidate_id")) in curated_exclusions:
            rejections["curated_exclusion"] += 1
            continue
        name = str(row.get("name") or "")
        if not name:
            rejections["missing_battle_name"] += 1
            continue
        parsed = _iwbd_dates(row)
        if parsed is None:
            rejections["missing_or_invalid_date"] += 1
            continue
        start, end = parsed
        year_low, year_high = start.year, end.year
        attacker = row.get("attacker_raw")
        defender = row.get("defender_raw")
        if not attacker or not defender:
            rejections["missing_belligerent_label"] += 1
            continue
        attacker, defender = str(attacker), str(defender)

        lookup_keys = {_event_key(name, year) for year in range(year_low - 1, year_high + 2)}
        hced_fuzzy_lookup_keys = {
            key
            for year in range(year_low, year_high + 1)
            for key in _cross_source_event_keys(name, year, lookup=True)
        }
        exact_keys = {_event_key(name, year) for year in range(year_low, year_high + 1)}
        if lookup_keys & seen_keys:
            rejections["duplicate_within_iwbd"] += 1
            continue
        if lookup_keys & curated_seed_keys:
            rejections["duplicate_of_curated_seed"] += 1
            continue

        parts = _iwbd_id_parts(str(row.get("candidate_id") or ""))
        if parts is None:
            rejections["malformed_candidate_id"] += 1
            continue
        cow_number = parts[0]
        normalized_name = normalize_label(name)
        span_days = (end - start).days
        contained = False
        for other_name, other_start, other_end in war_groups.get(
            (cow_number, str(row.get("war_name") or "")), []
        ):
            if normalize_label(other_name) == normalized_name:
                continue
            if (
                start <= other_start
                and end >= other_end
                and span_days > (other_end - other_start).days
            ):
                contained = True
                break
        if contained:
            rejections["contains_constituent_iwbd_rows"] += 1
            continue

        winner = normalize_label(row.get("winner_raw"))
        role = str(row.get("battle_level_victor_role") or "")
        normalized_attacker = normalize_label(attacker)
        normalized_defender = normalize_label(defender)
        draw = winner == "inconclusive" and normalize_label(role) == "inconclusive"
        if not draw and not (
            (role == "Attacker" and winner == normalized_attacker)
            or (role == "Defender" and winner == normalized_defender)
        ):
            rejections["outcome_not_aligned_to_battle_sides"] += 1
            continue

        if _matches_hced_exact(hced_event_keys, lookup_keys):
            rejections["duplicate_of_hced_battle"] += 1
            continue

        if any(
            "/" in label or "," in label or "(" in label
            or normalize_label(label) in IWBD_COALITION_SIDE_LABELS
            for label in (attacker, defender)
        ):
            rejections["coalition_or_composite_side"] += 1
            continue

        denied = False
        for label in (attacker, defender):
            for deny_low, deny_high in IDENTITY_DENY_WINDOWS.get(
                normalize_label(label), ()
            ):
                if not (year_high < deny_low or year_low > deny_high):
                    denied = True
                    break
            if denied:
                break
        if denied:
            rejections["unresolved_time_bounded_belligerent"] += 1
            continue
        attacker_id, attacker_polity = resolve_label(attacker, year_low, year_high)
        defender_id, defender_polity = resolve_label(defender, year_low, year_high)
        if not attacker_id or not defender_id:
            rejections["unresolved_time_bounded_belligerent"] += 1
            continue
        if attacker_id == defender_id:
            rejections["same_or_empty_opposing_side"] += 1
            continue
        if draw:
            fuzzy_signature = (
                frozenset({attacker_id, defender_id}),
                frozenset(),
            )
        elif winner == normalized_attacker:
            fuzzy_signature = (frozenset({attacker_id}), frozenset({defender_id}))
        else:
            fuzzy_signature = (frozenset({defender_id}), frozenset({attacker_id}))
        if _matches_hced_fuzzy(
            hced_event_keys, hced_fuzzy_lookup_keys, fuzzy_signature
        ):
            rejections["duplicate_of_hced_battle"] += 1
            continue
        # Only an eligible row claims its exact name/year keys. A malformed or
        # otherwise rejected earlier copy must not suppress a later valid row;
        # source-row order remains the deterministic tie-break between valid
        # duplicates.
        seen_keys |= exact_keys
        for entity_id, polity in (
            (attacker_id, attacker_polity),
            (defender_id, defender_polity),
        ):
            if polity is not None:
                resolved_polities[entity_id] = polity

        accepted_rows.append(
            {
                "row": row,
                "name": name,
                "start": start,
                "end": end,
                "attacker_id": attacker_id,
                "defender_id": defender_id,
                "draw": draw,
                "victor_role": role,
                "cow_number": cow_number,
                "iwd_number": parts[1],
                "base_war": _iwbd_base_war(row),
            }
        )

    # Cluster assignment is per war, never per row: all accepted battles of
    # one (cowNum, theater-stripped war) group share exactly one tactical
    # down-weighting cluster — an existing HCED war cluster when the war-name
    # tokens match exactly one with year overlap, else the IWD parent-war
    # family for a joinable iwdNum (the parent war id itself, never a
    # component id), else a distinct iwbd_war_* fallback.
    group_rows: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for accepted in accepted_rows:
        group_rows.setdefault((accepted["cow_number"], accepted["base_war"]), []).append(accepted)
    group_clusters: dict[tuple[str, str], str] = {}
    for (cow_number, base_war), rows in group_rows.items():
        group_low = min(item["start"].year for item in rows)
        group_high = max(item["end"].year for item in rows)
        war_tokens = _war_tokens(base_war)
        matches = [
            cluster_id
            for cluster_id, (tokens, span_low, span_high) in hced_war_cluster_spans.items()
            if _war_tokens_match(war_tokens, tokens)
            and group_low <= span_high
            and group_high >= span_low
        ]
        if len(set(matches)) == 1:
            group_clusters[(cow_number, base_war)] = matches[0]
        elif rows[0]["iwd_number"] != "-9" and rows[0]["iwd_number"] in iwd_parent_ids:
            group_clusters[(cow_number, base_war)] = (
                f"iwd_parent_{_slug(rows[0]['iwd_number'], 24)}"
            )
        else:
            group_clusters[(cow_number, base_war)] = (
                f"iwbd_war_{cow_number}_{_slug(base_war, 40)}"
            )

    for accepted in accepted_rows:
        row = accepted["row"]
        name = accepted["name"]
        start, end = accepted["start"], accepted["end"]
        draw = accepted["draw"]
        if draw or accepted["victor_role"] == "Attacker":
            side_a, side_b = [accepted["attacker_id"]], [accepted["defender_id"]]
        else:
            side_a, side_b = [accepted["defender_id"]], [accepted["attacker_id"]]
        candidate_id = str(row.get("candidate_id"))
        events.append(
            {
                "id": f"iwbd_{_slug(candidate_id, 24)}_{_slug(name, 44)}",
                "name": name,
                "year": start.year,
                "end_year": end.year,
                "event_type": "engagement",
                "war_type": "interstate_limited",
                "scale": "battle",
                "stakes": "limited",
                "decisiveness": 0.32 if draw else 0.66,
                "confidence": 0.70,
                "geographic_scope": 0.26,
                "domain": _domain(row.get("war_name")),
                "cluster_id": group_clusters[(accepted["cow_number"], accepted["base_war"])],
                "date_precision": "day",
                "sequence": int(row.get("source_row") or 0),
                "summary": (
                    "Provisional tactical result from IWBD. The victor is coded by "
                    "tactical control of the attacker's objective; this does not "
                    "describe casualties, magnitude, or the enclosing war's "
                    "strategic outcome, which is never inferred from battle results."
                ),
                "participants": _participants(
                    side_a,
                    side_b,
                    draw,
                    0.70,
                    2,
                    note=(
                        "Provisional IWBD tactical coding; the enclosing war's "
                        "strategic outcome is not inferred from battle results."
                    ),
                ),
                "source_ids": ["iwbd_dataset", "cliopatria_v020"],
                "status": "complete",
                "iwbd_candidate_id": candidate_id,
                "iwbd_war_name": str(row.get("war_name") or ""),
                "iwbd_cow_war_number": accepted["cow_number"],
                "iwbd_iwd_war_number": (
                    accepted["iwd_number"] if accepted["iwd_number"] != "-9" else None
                ),
                "iwbd_battle_level_victor_role": str(row.get("battle_level_victor_role") or ""),
                "iwbd_duration_days": row.get("duration_days"),
            }
        )

    return {
        "events": events,
        "rejections": rejections,
        "battles_total": len(candidates),
        "battles_promoted": len(events),
        "resolved_polities": resolved_polities,
    }
