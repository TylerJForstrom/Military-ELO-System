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
    validate_exact_candidate_contracts,
    validate_exact_source_contract,
)
from .policy import (
    IDENTITY_DENY_WINDOWS,
    IWBD_COALITION_SIDE_LABELS,
    IWBD_CURATED_EXCLUSIONS,
    IWBD_REVIEWED_CONCURRENT_DISTINCT_RELATIONS,
    IWBD_REVIEWED_PARTICIPANT_COMPOSITIONS,
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


def _iwbd_review_fingerprint(row: dict[str, Any]) -> dict[str, str]:
    """Return the semantic fields pinned by a candidate-specific review."""
    fields = (
        "source_row",
        "name",
        "war_name",
        "start_date",
        "end_date",
        "duration_days",
        "attacker_raw",
        "defender_raw",
        "winner_raw",
        "battle_level_victor_role",
    )
    return {
        field: "" if row.get(field) is None else str(row.get(field)) for field in fields
    }


def _validate_iwbd_review_fingerprint(
    candidate_id: str,
    row: dict[str, Any],
    expected: dict[str, str],
) -> None:
    actual = _iwbd_review_fingerprint(row)
    if actual == expected:
        return
    changed = ", ".join(
        field for field in expected if actual.get(field) != expected.get(field)
    )
    raise ValueError(
        f"stale IWBD reviewed policy for {candidate_id}: "
        f"source fingerprint changed ({changed})"
    )


def _validate_iwbd_review_policies(
    candidates: list[dict[str, Any]],
    reviewed_identity_bindings: dict[str, dict[str, Any]] | None = None,
    reviewed_identity_cohorts: dict[str, tuple[str, ...]] | None = None,
    require_complete_identity_cohorts: bool = False,
) -> None:
    """Fail closed when a present reviewed target or its pinned sibling drifts."""
    rows_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in candidates:
        rows_by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)

    review_tables = [
        IWBD_REVIEWED_PARTICIPANT_COMPOSITIONS,
        IWBD_REVIEWED_CONCURRENT_DISTINCT_RELATIONS,
    ]
    if reviewed_identity_bindings is not None:
        review_tables.append(reviewed_identity_bindings)
    for table in review_tables:
        for candidate_id, policy in table.items():
            rows = rows_by_id.get(candidate_id, [])
            if not rows:
                # Focused callers may pass a subset of IWBD. Once the reviewed
                # target is present, however, every pinned dependency is strict.
                continue
            if len(rows) != 1:
                raise ValueError(
                    f"stale IWBD reviewed policy for {candidate_id}: "
                    f"expected exactly one target row, found {len(rows)}"
                )
            if "source_contract" in policy:
                validate_exact_source_contract(
                    rows[0],
                    policy["source_contract"],
                    description=f"IWBD reviewed policy {candidate_id}",
                )
            else:
                _validate_iwbd_review_fingerprint(
                    candidate_id, rows[0], policy["fingerprint"]
                )
            for sibling_id, fingerprint in policy.get(
                "contained_candidates", {}
            ).items():
                sibling_rows = rows_by_id.get(sibling_id, [])
                if len(sibling_rows) != 1:
                    raise ValueError(
                        f"stale IWBD reviewed policy for {candidate_id}: "
                        f"expected exactly one pinned sibling {sibling_id}, "
                        f"found {len(sibling_rows)}"
                    )
                _validate_iwbd_review_fingerprint(
                    sibling_id, sibling_rows[0], fingerprint
                )

    if reviewed_identity_cohorts is None:
        return
    cohort_members = [
        candidate_id
        for candidate_ids in reviewed_identity_cohorts.values()
        for candidate_id in candidate_ids
    ]
    if len(cohort_members) != len(set(cohort_members)):
        raise ValueError("IWBD reviewed identity cohorts contain duplicate candidates")
    if reviewed_identity_bindings is not None and set(cohort_members) != set(
        reviewed_identity_bindings
    ):
        raise ValueError(
            "IWBD reviewed identity cohort inventory does not match binding inventory"
        )
    for cohort_name, candidate_ids in reviewed_identity_cohorts.items():
        expected = set(candidate_ids)
        present = expected & set(rows_by_id)
        if (require_complete_identity_cohorts or present) and present != expected:
            raise ValueError(
                f"stale IWBD reviewed cohort {cohort_name}: candidate set incomplete; "
                f"expected {sorted(expected)}, found {sorted(present)}"
            )


def _matches_hced_exact(
    hced_event_keys: set[tuple[str, int]] | dict[tuple[str, int], dict[str, Any]],
    exact_lookup_keys: set[tuple[str, int]],
) -> bool:
    if isinstance(hced_event_keys, dict):
        return any(
            bool(hced_event_keys.get(key, {}).get("exact")) for key in exact_lookup_keys
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
    reviewed_identity_bindings: dict[str, dict[str, Any]] | None = None,
    validated_source_contracts: dict[str, dict[str, Any]] | None = None,
    reviewed_identity_cohorts: dict[str, tuple[str, ...]] | None = None,
    resolve_reviewed_id: Any | None = None,
    require_complete_reviewed_identity_cohorts: bool = False,
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
    both sides must resolve to unique time-bounded identities outside declared
    deny windows. The sole reviewed composite-side policy reconstructs an exact
    candidate-keyed coalition, and the sole reviewed containment relation
    permits an exact concurrent-distinct sibling pair; both raise on source or
    resolver drift. Severity is capped at limited. The war-level victor code is
    ignored entirely: battles never update the strategic layer.
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
    if reviewed_identity_bindings is None:
        reviewed_identity_bindings = {}
    if validated_source_contracts is None:
        validated_source_contracts = {
            candidate_id: contract["source_contract"]
            for candidate_id, contract in reviewed_identity_bindings.items()
            if "source_contract" in contract
        }
    validate_exact_candidate_contracts(
        candidates,
        validated_source_contracts,
        description="IWBD Wave 6 contract",
        require_complete=require_complete_reviewed_identity_cohorts,
    )
    overlap = set(reviewed_identity_bindings) & set(
        IWBD_REVIEWED_PARTICIPANT_COMPOSITIONS
    )
    if overlap:
        raise ValueError(
            "IWBD candidates cannot have both identity and composition reviews: "
            f"{sorted(overlap)}"
        )
    _validate_iwbd_review_policies(
        candidates,
        reviewed_identity_bindings,
        reviewed_identity_cohorts,
        require_complete_reviewed_identity_cohorts,
    )
    war_groups: dict[tuple[str, str], list[tuple[str, str, date, date]]] = {}
    for row in candidates:
        if str(row.get("candidate_id")) in curated_exclusions:
            continue
        name = str(row.get("name") or "")
        parsed = _iwbd_dates(row)
        parts = _iwbd_id_parts(str(row.get("candidate_id") or ""))
        if not name or parsed is None or parts is None:
            continue
        war_groups.setdefault((parts[0], str(row.get("war_name") or "")), []).append(
            (str(row.get("candidate_id")), name, parsed[0], parsed[1])
        )

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

        lookup_keys = {
            _event_key(name, year) for year in range(year_low - 1, year_high + 2)
        }
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
        candidate_id = str(row.get("candidate_id") or "")
        contained_ids: set[str] = set()
        for other_id, other_name, other_start, other_end in war_groups.get(
            (cow_number, str(row.get("war_name") or "")), []
        ):
            if other_id == candidate_id:
                continue
            if normalize_label(other_name) == normalized_name:
                continue
            if (
                start <= other_start
                and end >= other_end
                and span_days > (other_end - other_start).days
            ):
                contained_ids.add(other_id)
        relation_policy = IWBD_REVIEWED_CONCURRENT_DISTINCT_RELATIONS.get(candidate_id)
        reviewed_relation_ids = set(
            reviewed_identity_bindings.get(candidate_id, {}).get(
                "contained_candidate_ids", ()
            )
        )
        if relation_policy is not None:
            expected_contained = set(relation_policy["contained_candidates"])
            if contained_ids != expected_contained:
                raise ValueError(
                    f"stale IWBD reviewed policy for {candidate_id}: "
                    f"contained sibling set changed; expected "
                    f"{sorted(expected_contained)}, found {sorted(contained_ids)}"
                )
        elif reviewed_relation_ids:
            if contained_ids != reviewed_relation_ids:
                raise ValueError(
                    f"stale IWBD reviewed policy for {candidate_id}: "
                    f"contained sibling set changed; expected "
                    f"{sorted(reviewed_relation_ids)}, found {sorted(contained_ids)}"
                )
        elif contained_ids:
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

        composition_policy = IWBD_REVIEWED_PARTICIPANT_COMPOSITIONS.get(candidate_id)
        identity_policy = reviewed_identity_bindings.get(candidate_id)
        if (
            composition_policy is None
            and identity_policy is None
            and any(
                "/" in label
                or "," in label
                or "(" in label
                or normalize_label(label) in IWBD_COALITION_SIDE_LABELS
                for label in (attacker, defender)
            )
        ):
            rejections["coalition_or_composite_side"] += 1
            continue

        if identity_policy is not None:
            attacker_specs = identity_policy["attacker"]
            defender_specs = identity_policy["defender"]
        elif composition_policy is None:
            attacker_specs = ((attacker, None),)
            defender_specs = ((defender, None),)
        else:
            attacker_specs = composition_policy["attacker"]
            defender_specs = composition_policy["defender"]

        denied = False
        for label, _ in (*attacker_specs, *defender_specs):
            # An exact candidate fingerprint plus an exact-ID binding is the
            # only path through a deny window. Uncontracted uses (especially
            # bare Turkey in 1919-1923) remain denied below.
            if identity_policy is not None:
                continue
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

        def resolve_side(
            specs: tuple[tuple[str, str | None], ...],
        ) -> list[tuple[str | None, dict[str, Any] | None]]:
            resolved: list[tuple[str | None, dict[str, Any] | None]] = []
            for label, expected_id in specs:
                if identity_policy is not None:
                    if resolve_reviewed_id is None:
                        raise ValueError(
                            f"reviewed IWBD candidate {candidate_id} requires "
                            "an exact-ID resolver"
                        )
                    entity_id, polity = resolve_reviewed_id(
                        expected_id, year_low, year_high
                    )
                else:
                    entity_id, polity = resolve_label(label, year_low, year_high)
                if expected_id is not None and entity_id != expected_id:
                    raise ValueError(
                        f"stale IWBD reviewed policy for {candidate_id}: "
                        f"resolver returned {entity_id!r} for {label!r}; "
                        f"expected {expected_id!r}"
                    )
                resolved.append((entity_id, polity))
            return resolved

        attacker_resolved = resolve_side(attacker_specs)
        defender_resolved = resolve_side(defender_specs)
        attacker_ids = [entity_id for entity_id, _ in attacker_resolved if entity_id]
        defender_ids = [entity_id for entity_id, _ in defender_resolved if entity_id]
        if len(attacker_ids) != len(attacker_specs) or len(defender_ids) != len(
            defender_specs
        ):
            rejections["unresolved_time_bounded_belligerent"] += 1
            continue
        if set(attacker_ids) & set(defender_ids):
            rejections["same_or_empty_opposing_side"] += 1
            continue
        if draw:
            fuzzy_signature = (
                frozenset({*attacker_ids, *defender_ids}),
                frozenset(),
            )
        elif winner == normalized_attacker:
            fuzzy_signature = (frozenset(attacker_ids), frozenset(defender_ids))
        else:
            fuzzy_signature = (frozenset(defender_ids), frozenset(attacker_ids))
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
        for entity_id, polity in (*attacker_resolved, *defender_resolved):
            if polity is not None:
                resolved_polities[entity_id] = polity

        accepted_rows.append(
            {
                "row": row,
                "name": name,
                "start": start,
                "end": end,
                "attacker_ids": attacker_ids,
                "defender_ids": defender_ids,
                "draw": draw,
                "victor_role": role,
                "cow_number": cow_number,
                "iwd_number": parts[1],
                "base_war": _iwbd_base_war(row),
                "evidence_source_ids": (
                    tuple(identity_policy.get("evidence_source_ids", ()))
                    if identity_policy is not None
                    else ()
                ),
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
        group_rows.setdefault(
            (accepted["cow_number"], accepted["base_war"]), []
        ).append(accepted)
    group_clusters: dict[tuple[str, str], str] = {}
    for (cow_number, base_war), rows in group_rows.items():
        group_low = min(item["start"].year for item in rows)
        group_high = max(item["end"].year for item in rows)
        war_tokens = _war_tokens(base_war)
        matches = [
            cluster_id
            for cluster_id, (
                tokens,
                span_low,
                span_high,
            ) in hced_war_cluster_spans.items()
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
            side_a, side_b = accepted["attacker_ids"], accepted["defender_ids"]
        else:
            side_a, side_b = accepted["defender_ids"], accepted["attacker_ids"]
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
                "cluster_id": group_clusters[
                    (accepted["cow_number"], accepted["base_war"])
                ],
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
                "source_ids": [
                    "iwbd_dataset",
                    "cliopatria_v020",
                    *accepted["evidence_source_ids"],
                ],
                "outcome_source_ids": ["iwbd_dataset"],
                "outcome_source_family_ids": ["iwbd"],
                "status": "complete",
                "iwbd_candidate_id": candidate_id,
                "iwbd_war_name": str(row.get("war_name") or ""),
                "iwbd_cow_war_number": accepted["cow_number"],
                "iwbd_iwd_war_number": (
                    accepted["iwd_number"] if accepted["iwd_number"] != "-9" else None
                ),
                "iwbd_battle_level_victor_role": str(
                    row.get("battle_level_victor_role") or ""
                ),
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
