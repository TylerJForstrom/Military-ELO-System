from __future__ import annotations

"""UCDP conflict-termination episode promotion."""

import re
from collections import Counter
from typing import Any

from .common import (
    _deduplicate,
    _resolve_label_tiers,
    _slug,
    _strategic_participants,
    normalize_label,
)
from .policy import (
    UCDP_ACTOR_PARTY_POLICIES,
    UCDP_CURATED_EXCLUSIONS,
    UCDP_GW_CODE_POLICIES,
    UCDP_WAR_TYPES,
    _gw_policy_seed_id,
)

_UCDP_PARENTHETICAL = re.compile(r"^(.*?)\s*\((.*)\)\s*$")


def _ucdp_label_variants(name: Any) -> list[str]:
    label = str(name or "").strip()
    if label.lower().startswith("government of "):
        label = label[len("government of "):]
    match = _UCDP_PARENTHETICAL.match(label)
    variants = [label] if not match else [match.group(1), match.group(2)]
    return [variant for variant in (v.strip() for v in variants) if variant]


def resolve_ucdp_party(
    name: Any,
    gwno: Any,
    low_year: int,
    high_year: int,
    context: dict[str, Any],
) -> tuple[str | None, dict[str, Any] | None, str | None]:
    """Resolve a UCDP party to a unique time-bounded identity.

    A Gleditsch-Ward code with an explicit policy is authoritative: outside
    its windows the party stays unresolved, never falling back to name
    matching. Otherwise the label (stripped of "Government of ", with
    parenthetical variants derived) resolves through the shared exact-alias
    tiers; every derived variant must resolve, and to the same entity —
    ambiguity always fails. Returns ``(entity_id, polity, method)``.
    """
    code = str(gwno or "").strip()
    if code in UCDP_GW_CODE_POLICIES:
        seed_id = _gw_policy_seed_id(code, low_year, high_year)
        return seed_id, None, ("gw_code_policy" if seed_id else None)
    variants = _ucdp_label_variants(name)
    if not variants:
        return None, None, None
    entity_ids: set[str] = set()
    polity: dict[str, Any] | None = None
    tiers: list[str] = []
    for variant in variants:
        entity_id, variant_polity, tier = _resolve_label_tiers(
            normalize_label(variant),
            low_year,
            high_year,
            context,
            require_observation_coherence=False,
        )
        if not entity_id:
            return None, None, None
        entity_ids.add(entity_id)
        if variant_polity is not None:
            polity = variant_polity
        tiers.append(str(tier))
    if len(entity_ids) != 1:
        return None, None, None
    method = {
        "seed_alias": "seed_label",
        "cliopatria_alias": "cliopatria_label",
        "cliopatria_alias_to_seed": "cliopatria_label",
    }.get(tiers[0], tiers[0])
    return next(iter(entity_ids)), polity, method


def _ucdp_split(value: Any) -> list[str]:
    return [part.strip() for part in str(value or "").split(",") if part.strip()]


def _ucdp_int(value: Any) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def promote_ucdp_termination_episodes(
    conflict_rows: list[dict[str, Any]],
    dyad_rows: list[dict[str, Any]],
    promoted_war_index: list[tuple[str, str | None, int, int, frozenset[str], dict[str, str]]],
    resolver: Any,
    curated_exclusions: dict[tuple[str, str], str] | None = None,
) -> dict[str, Any]:
    """Promote UCDP conflict-termination victory episodes as strategic events.

    The promotion unit is the conflict-level terminal episode; the dyad file
    is a consistency reference only and is never promoted. Only outcome codes
    3 and 4 (victories) can produce events — peace agreements, ceasefires,
    low activity, and actor cessation stay staged, because peace is not a
    loss and unknown stays unknown. Both sides must consist entirely of
    state primaries resolving to unique time-bounded identities; episodes
    duplicating an already-promoted strategic event (shared entity on each
    side with year overlap), contradicted by a terminal dyad row, or linked
    by end date to an oppositely-oriented victory assertion (the Six-Day
    rule) stay staged. Severity is capped at limited; secondary supporters
    are recorded as provenance and never receive an outcome.
    """
    if curated_exclusions is None:
        curated_exclusions = UCDP_CURATED_EXCLUSIONS
    events: list[dict[str, Any]] = []
    rejections: Counter[str] = Counter()
    duplicate_details: list[dict[str, Any]] = []
    resolved_polities: dict[str, dict[str, Any]] = {}

    def parse_primaries(raw: dict[str, Any], side: str) -> list[tuple[str, str]] | None:
        names = _ucdp_split(raw.get(f"side_{side}"))
        codes = _ucdp_split(raw.get(f"gwno_{side}"))
        if not names:
            return None
        conflict_key = str(raw.get("conflict_id", "")).strip()
        policy_side = all(
            not name.lower().startswith("government of ")
            and (conflict_key, normalize_label(name)) in UCDP_ACTOR_PARTY_POLICIES
            for name in names
        )
        if policy_side and not codes:
            # A curated actor party is admitted without a GW code; its
            # identity comes only from the conflict-scoped actor policy.
            return [(name, "") for name in names]
        if len(names) != len(codes):
            return None
        if not all(name.lower().startswith("government of ") for name in names):
            return None
        return list(zip(names, codes))

    def resolve_party(
        conflict_key: str, name: Any, code: Any, low_year: int, high_year: int
    ) -> tuple[str | None, dict[str, Any] | None, str | None]:
        policies = UCDP_ACTOR_PARTY_POLICIES.get((conflict_key, normalize_label(name)))
        if policies is not None:
            matches = [
                entity_id
                for start_year, end_year, entity_id in policies
                if low_year >= start_year and high_year <= end_year
            ]
            entity_id = matches[0] if len(set(matches)) == 1 else None
            return entity_id, None, ("actor_party_policy" if entity_id else None)
        return resolver(name, code, low_year, high_year)

    def parse_secondaries(raw: dict[str, Any], side: str) -> list[tuple[str, str | None]]:
        names = _ucdp_split(raw.get(f"side_{side}_2nd"))
        codes = _ucdp_split(raw.get(f"gwno_{side}_2nd"))
        if len(names) == len(codes):
            return list(zip(names, codes))
        return [(name, None) for name in names]

    def best_effort_ids(
        parties: list[tuple[str, str | None]], low_year: int, high_year: int,
        conflict_key: str = "",
    ) -> set[str]:
        resolved: set[str] = set()
        for name, code in parties:
            entity_id, _, _ = resolve_party(conflict_key, name, code, low_year, high_year)
            if entity_id:
                resolved.add(entity_id)
        return resolved

    # Pre-pass over every terminal victory assertion in the file, independent
    # of its own gate outcomes, resolved best-effort. Feeds the ledger-cluster
    # map (an accepted episode of a conflict whose sibling deduplicates
    # against ledger war W inherits W's cluster) and the linked-episode index
    # (assertions sharing an exact end date and a resolved entity).
    assertions: list[dict[str, Any]] = []
    for candidate in conflict_rows:
        raw = candidate.get("raw", {})
        if str(raw.get("c_epterm", "")).strip() != "1":
            continue
        outcome_code = str(raw.get("c_outcome", "")).strip()
        if outcome_code not in {"3", "4"}:
            continue
        start = _ucdp_int(raw.get("c_ep_startyear"))
        end = _ucdp_int(raw.get("c_ep_endyear"))
        if start is None or end is None:
            continue
        side_a = parse_primaries(raw, "a") or []
        side_b = parse_primaries(raw, "b") or []
        conflict_key = str(raw.get("conflict_id", "")).strip()
        primary_a = best_effort_ids(side_a, start, end, conflict_key)
        primary_b = best_effort_ids(side_b, start, end, conflict_key)
        dedup_a = primary_a | best_effort_ids(parse_secondaries(raw, "a"), start, end, conflict_key)
        dedup_b = primary_b | best_effort_ids(parse_secondaries(raw, "b"), start, end, conflict_key)
        winners, losers = (
            (primary_a, primary_b) if outcome_code == "3" else (primary_b, primary_a)
        )
        assertions.append(
            {
                "conflict_id": str(raw.get("conflict_id", "")).strip(),
                "epno": str(raw.get("c_epno", "")).strip(),
                "start": start,
                "end": end,
                "end_date": str(raw.get("c_ependdate", "")).strip(),
                "winners": winners,
                "losers": losers,
                "dedup_a": dedup_a,
                "dedup_b": dedup_b,
            }
        )

    ledger_clusters: dict[str, dict[str, str]] = {}
    for assertion in assertions:
        for event_id, cluster_id, war_low, war_high, entities, _ in promoted_war_index:
            if war_low > assertion["end"] or war_high < assertion["start"]:
                continue
            if assertion["dedup_a"] & entities and assertion["dedup_b"] & entities:
                if cluster_id:
                    ledger_clusters.setdefault(assertion["conflict_id"], {})[
                        cluster_id
                    ] = event_id
    linked_by_date: dict[str, list[dict[str, Any]]] = {}
    for assertion in assertions:
        if assertion["end_date"]:
            linked_by_date.setdefault(assertion["end_date"], []).append(assertion)

    # Dyad reference file: quarantine rows failing year sanity (never silently
    # repaired), count the blank-outcome terminal row, index the sane
    # terminal remainder for the consistency scan.
    dyad_rows_quarantined_corrupt = 0
    dyad_terminal_blank_outcome = 0
    dyads_by_conflict: dict[str, list[dict[str, Any]]] = {}
    for candidate in dyad_rows:
        raw = candidate.get("raw", {})
        year = _ucdp_int(raw.get("year"))
        if year is None or not 1900 <= year <= 2035:
            dyad_rows_quarantined_corrupt += 1
            continue
        if str(raw.get("d_epterm", "")).strip() != "1":
            # Non-terminal annual rows never gate a promotion; a blank
            # episode-end year here just means the episode is ongoing.
            continue
        if not str(raw.get("d_outcome", "")).strip():
            dyad_terminal_blank_outcome += 1
            continue
        start = _ucdp_int(raw.get("d_ep_startyear"))
        end = _ucdp_int(raw.get("d_ep_endyear"))
        if start is None or end is None:
            # A terminal row without sane episode years cannot be scanned;
            # quarantine it explicitly rather than silently repairing it.
            dyad_rows_quarantined_corrupt += 1
            continue
        dyads_by_conflict.setdefault(str(raw.get("conflict_id", "")).strip(), []).append(raw)

    def sort_key(candidate: dict[str, Any]) -> tuple[int, int, int]:
        raw = candidate.get("raw", {})
        return (
            _ucdp_int(raw.get("c_ep_endyear")) or 0,
            _ucdp_int(raw.get("conflict_id")) or 0,
            _ucdp_int(raw.get("c_epno")) or 0,
        )

    accepted_index: list[tuple[str, str | None, int, int, frozenset[str], dict[str, str]]] = []

    for candidate in sorted(conflict_rows, key=sort_key):
        raw = candidate.get("raw", {})
        conflict_id = str(raw.get("conflict_id", "")).strip()
        year = _ucdp_int(raw.get("year"))
        if not conflict_id or year is None or not 1900 <= year <= 2035:
            rejections["malformed_source_row"] += 1
            continue
        if str(raw.get("c_epterm", "")).strip() != "1":
            rejections["not_terminal_episode"] += 1
            continue
        outcome_code = str(raw.get("c_outcome", "")).strip()
        if outcome_code == "1":
            rejections["outcome_peace_agreement"] += 1
            continue
        if outcome_code == "2":
            rejections["outcome_ceasefire"] += 1
            continue
        if outcome_code == "5":
            rejections["outcome_low_activity"] += 1
            continue
        if outcome_code == "6":
            rejections["outcome_actor_ceased"] += 1
            continue
        if outcome_code not in {"3", "4"}:
            rejections["outcome_missing_or_unknown"] += 1
            continue
        low_year = _ucdp_int(raw.get("c_ep_startyear"))
        high_year = _ucdp_int(raw.get("c_ep_endyear"))
        if low_year is None or high_year is None:
            rejections["missing_or_invalid_episode_years"] += 1
            continue
        side_a_parties = parse_primaries(raw, "a")
        side_b_parties = parse_primaries(raw, "b")
        if side_a_parties is None or side_b_parties is None:
            rejections["nonstate_primary_party"] += 1
            continue

        party_resolutions: list[dict[str, Any]] = []
        pending_polities: dict[str, dict[str, Any]] = {}
        side_ids: list[list[str]] = []
        side_codes: list[set[str]] = []
        unresolved = False
        for side_name, parties in (("side_a", side_a_parties), ("side_b", side_b_parties)):
            resolved: list[str] = []
            for name, code in parties:
                entity_id, polity, method = resolve_party(
                    conflict_id, name, code, low_year, high_year
                )
                if not entity_id:
                    unresolved = True
                    break
                if polity is not None:
                    pending_polities[entity_id] = polity
                resolved.append(entity_id)
                party_resolutions.append(
                    {
                        "name": name,
                        "gwno": code,
                        "side": side_name,
                        "entity_id": entity_id,
                        "method": method,
                    }
                )
            if unresolved:
                break
            side_ids.append(_deduplicate(resolved))
            side_codes.append({code for _, code in parties})
        if unresolved:
            rejections["unresolved_time_bounded_party"] += 1
            continue
        side_a_ids, side_b_ids = side_ids
        if not side_a_ids or not side_b_ids or set(side_a_ids) & set(side_b_ids):
            rejections["same_or_empty_opposing_side"] += 1
            continue

        epno = str(raw.get("c_epno", "")).strip()
        exclusion_reason = curated_exclusions.get((conflict_id, epno))
        if exclusion_reason:
            rejections["documented_side_attribution_dispute"] += 1
            continue

        winners_ids, losers_ids = (
            (set(side_a_ids), set(side_b_ids))
            if outcome_code == "3"
            else (set(side_b_ids), set(side_a_ids))
        )
        winner_codes, loser_codes = (
            (side_codes[0], side_codes[1])
            if outcome_code == "3"
            else (side_codes[1], side_codes[0])
        )
        primary_pair_codes = winner_codes | loser_codes

        secondaries_a = parse_secondaries(raw, "a")
        secondaries_b = parse_secondaries(raw, "b")
        dedup_a = set(side_a_ids) | best_effort_ids(secondaries_a, low_year, high_year, conflict_id)
        dedup_b = set(side_b_ids) | best_effort_ids(secondaries_b, low_year, high_year, conflict_id)
        duplicate_event = None
        for event_id, cluster_id, war_low, war_high, entities, terminations in (
            *promoted_war_index,
            *accepted_index,
        ):
            if war_low > high_year or war_high < low_year:
                continue
            if dedup_a & entities and dedup_b & entities:
                duplicate_event = (event_id, terminations)
                break
        if duplicate_event is not None:
            event_id, terminations = duplicate_event
            agrees = contradicts = False
            for entity_id in winners_ids:
                termination = str(terminations.get(entity_id, ""))
                if "victory" in termination:
                    agrees = True
                elif "defeat" in termination:
                    contradicts = True
            for entity_id in losers_ids:
                termination = str(terminations.get(entity_id, ""))
                if "defeat" in termination:
                    agrees = True
                elif "victory" in termination:
                    contradicts = True
            orientation = (
                "contradicts" if contradicts else "agrees" if agrees else "undetermined"
            )
            duplicate_details.append(
                {
                    "conflict_id": conflict_id,
                    "c_epno": epno,
                    "matched_event_id": event_id,
                    "orientation": orientation,
                }
            )
            rejections["duplicate_of_promoted_strategic_event"] += 1
            continue

        dyad_checks: list[dict[str, Any]] = []
        dyad_contradiction = False
        for dyad_raw in dyads_by_conflict.get(conflict_id, []):
            dyad_start = _ucdp_int(dyad_raw.get("d_ep_startyear"))
            dyad_end = _ucdp_int(dyad_raw.get("d_ep_endyear"))
            if dyad_start is None or dyad_end is None:
                continue
            if dyad_start > high_year or dyad_end < low_year:
                continue
            dyad_outcome = str(dyad_raw.get("d_outcome", "")).strip()
            status = "nonvictory_terminal_ignored"
            if dyad_outcome in {"3", "4"}:
                dyad_a = set(_ucdp_split(dyad_raw.get("gwno_a")))
                dyad_b = set(_ucdp_split(dyad_raw.get("gwno_b")))
                dyad_winners, dyad_losers = (
                    (dyad_a, dyad_b) if dyad_outcome == "3" else (dyad_b, dyad_a)
                )
                if dyad_winners & loser_codes or dyad_losers & winner_codes:
                    dyad_contradiction = True
                else:
                    status = "consistent_victory"
            elif dyad_outcome in {"1", "2"}:
                dyad_pair = set(_ucdp_split(dyad_raw.get("gwno_a"))) | set(
                    _ucdp_split(dyad_raw.get("gwno_b"))
                )
                # The same state pair the conflict level calls a victory is
                # called a negotiated ending at the dyad level: mixed evidence
                # quarantines the episode; nothing is rated.
                if dyad_pair and dyad_pair <= primary_pair_codes:
                    dyad_contradiction = True
            dyad_checks.append(
                {
                    "dyad_id": str(dyad_raw.get("dyad_id", "")).strip(),
                    "d_epid": str(dyad_raw.get("d_epid", "")).strip(),
                    "d_ep_startyear": dyad_start,
                    "d_ep_endyear": dyad_end,
                    "d_outcome": dyad_outcome,
                    "status": status,
                }
            )
            if dyad_contradiction:
                break
        if dyad_contradiction:
            rejections["dyad_conflict_outcome_contradiction"] += 1
            continue

        end_date = str(raw.get("c_ependdate", "")).strip()
        linked_contradiction = False
        linked_group = False
        for assertion in linked_by_date.get(end_date, []) if end_date else []:
            if assertion["conflict_id"] == conflict_id and assertion["epno"] == epno:
                continue
            assertion_entities = assertion["winners"] | assertion["losers"]
            if not ((winners_ids | losers_ids) & assertion_entities):
                continue
            linked_group = True
            if winners_ids & assertion["losers"] or losers_ids & assertion["winners"]:
                linked_contradiction = True
                break
        if linked_contradiction:
            rejections["contradictory_linked_episode_outcomes"] += 1
            continue

        intensity = str(raw.get("intensity_level", "")).strip()
        incompatibility = str(raw.get("incompatibility", "")).strip()
        scale = "major_war" if intensity == "2" else "campaign"
        stakes = "major" if incompatibility in {"2", "3"} else "limited"
        end_precision = str(raw.get("c_ependprec", "")).strip()
        has_secondaries = bool(secondaries_a or secondaries_b)
        confidence = 0.74
        if has_secondaries:
            confidence -= 0.05
        if end_precision not in {"1", "2", "3"}:
            confidence -= 0.03
        confidence = round(confidence, 2)
        participant_uniform = 0.72 if scale == "major_war" else 0.52

        display_a = " & ".join(
            name[len("Government of "):] if name.lower().startswith("government of ") else name
            for name, _ in side_a_parties
        )
        display_b = " & ".join(
            name[len("Government of "):] if name.lower().startswith("government of ") else name
            for name, _ in side_b_parties
        )
        territory = str(raw.get("territory_name", "")).strip()
        display_name = f"{display_a}–{display_b} conflict termination {low_year}"
        if high_year != low_year:
            display_name += f"–{high_year}"
        if territory:
            display_name += f" ({territory})"

        conflict_ledger = ledger_clusters.get(conflict_id, {})
        inherited_from = None
        if len(conflict_ledger) == 1:
            cluster_id, inherited_from = next(iter(conflict_ledger.items()))
        elif linked_group and end_date:
            cluster_id = f"ucdp_linked_{_slug(end_date, 24)}"
        else:
            cluster_id = f"ucdp_conflict_{_slug(conflict_id, 24)}"

        type_of_conflict = str(raw.get("type_of_conflict", "")).strip()
        if type_of_conflict not in UCDP_WAR_TYPES:
            rejections["unmapped_type_of_conflict"] += 1
            continue

        resolved_polities.update(pending_polities)
        epid = str(raw.get("c_epid", "")).strip()
        event = {
            "id": f"ucdp_term_{conflict_id}_ep{epno}_{_slug(display_name, 40)}",
            "name": display_name,
            "year": low_year,
            "end_year": high_year,
            "event_type": "war",
            "war_type": UCDP_WAR_TYPES[type_of_conflict],
            "scale": scale,
            "stakes": stakes,
            "decisiveness": 0.74,
            "confidence": confidence,
            "geographic_scope": 0.68 if scale == "major_war" else 0.44,
            "domain": "mixed",
            "cluster_id": cluster_id,
            "date_precision": "year",
            "sequence": int(epid) if epid.isdigit() else 0,
            "summary": (
                "Provisional strategic outcome promoted mechanically from UCDP "
                "conflict-termination episode codes. Episode-level victory (code "
                "3/4) only; severity capped at limited; secondary supporters "
                "carry no outcome. Pending claim-level human review."
            ),
            "participants": _strategic_participants(
                side_a_ids,
                side_b_ids,
                "side_a" if outcome_code == "3" else "side_b",
                confidence,
                stakes=participant_uniform,
                national_scale=participant_uniform,
                note=(
                    "Episode-level UCDP conflict-termination outcome; existential "
                    "or regime-ending severity is never inferred from UCDP "
                    "termination codes."
                ),
            ),
            "source_ids": ["ucdp_termination_conflict", "ucdp_termination_dyad"],
            "status": "complete",
            "ucdp_conflict_id": conflict_id,
            "ucdp_episode_id": epid,
            "ucdp_episode_number": epno,
            "ucdp_outcome_code": outcome_code,
            "ucdp_episode_end_date": end_date or None,
            "ucdp_end_date_precision": end_precision or None,
            "ucdp_incompatibility": incompatibility or None,
            "ucdp_intensity_level_terminal_year": intensity or None,
            "ucdp_territory_name": territory or None,
            "candidate_id": str(candidate.get("candidate_id")),
            "ucdp_party_resolutions": party_resolutions,
            "ucdp_secondary_parties": {
                "side_a": [
                    {
                        "name": name,
                        "gwno": code,
                        "resolved_entity_id": resolve_party(
                            conflict_id, name, code, low_year, high_year
                        )[0],
                    }
                    for name, code in secondaries_a
                ],
                "side_b": [
                    {
                        "name": name,
                        "gwno": code,
                        "resolved_entity_id": resolve_party(
                            conflict_id, name, code, low_year, high_year
                        )[0],
                    }
                    for name, code in secondaries_b
                ],
            },
            "ucdp_dyad_checks": dyad_checks,
        }
        if inherited_from:
            event["ucdp_cluster_inherited_from"] = inherited_from
        if type_of_conflict != "2":
            # Absence means type 2 (interstate), mirroring the ledger's
            # identity_resolution absence convention, so previously promoted
            # interstate events stay byte-identical.
            event["ucdp_type_of_conflict"] = type_of_conflict
        events.append(event)
        accepted_index.append(
            (
                event["id"],
                cluster_id,
                low_year,
                high_year,
                frozenset([*side_a_ids, *side_b_ids]),
                {
                    str(participant["entity_id"]): str(participant["termination"])
                    for participant in event["participants"]
                },
            )
        )

    return {
        "events": events,
        "rejections": rejections,
        "rows_total": len(conflict_rows),
        "episodes_promoted": len(events),
        "dyad_rows_total": len(dyad_rows),
        "dyad_rows_quarantined_corrupt": dyad_rows_quarantined_corrupt,
        "dyad_terminal_blank_outcome": dyad_terminal_blank_outcome,
        "duplicate_details": duplicate_details,
        "resolved_polities": resolved_polities,
    }
