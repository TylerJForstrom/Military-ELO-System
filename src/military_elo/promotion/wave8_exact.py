"""Reusable fail-closed machinery for candidate-keyed Wave 8 HCED lanes."""

from __future__ import annotations

import copy
from typing import Any, Iterable, Mapping

from .common import _domain, _event_key, _participants, _scale, _slug, normalize_label
from .hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
    build_hced_location_fields,
    hced_candidate_id,
)
from .wave7_global import canonical_hced_row_sha256


_DRAW_LABELS = {"draw", "inconclusive", "stalemate"}


def rows_by_candidate_id(
    rows: Iterable[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            result.setdefault(candidate_id, []).append(row)
    return result


def validate_exact_hced_inventory(
    hced_rows: list[dict[str, Any]],
    contracts: Mapping[str, Mapping[str, Any]],
    holds: Mapping[str, Mapping[str, Any]],
    *,
    lane_name: str,
) -> dict[str, int]:
    overlap = set(contracts) & set(holds)
    if overlap:
        raise ValueError(f"{lane_name} promotion and hold contracts overlap: {sorted(overlap)}")
    indexed = rows_by_candidate_id(hced_rows)
    for disposition, inventory in (("promotion", contracts), ("hold", holds)):
        for candidate_id, contract in inventory.items():
            rows = indexed.get(candidate_id, [])
            if len(rows) != 1:
                raise ValueError(
                    f"{lane_name} {disposition} {candidate_id} expected exactly one "
                    f"queue row, found {len(rows)}"
                )
            actual = canonical_hced_row_sha256(rows[0])
            expected = str(contract["raw_row_sha256"])
            if actual != expected:
                raise ValueError(
                    f"{lane_name} {disposition} {candidate_id} raw-row fingerprint "
                    f"changed ({actual} != {expected})"
                )
    return {
        "promotion_contracts": len(contracts),
        "holds": len(holds),
        "reviewed_hced_rows": len(contracts) + len(holds),
    }


def install_exact_sources(
    sources_by_id: dict[str, dict[str, Any]],
    fixtures: Iterable[Mapping[str, Any]],
    *,
    lane_name: str,
) -> None:
    for fixture in fixtures:
        source = copy.deepcopy(dict(fixture))
        source_id = str(source["id"])
        existing = sources_by_id.get(source_id)
        if existing is not None and existing != source:
            raise ValueError(f"{lane_name} source collision for {source_id}")
        sources_by_id[source_id] = source


def install_exact_entities(
    release_entities: dict[str, dict[str, Any]],
    fixtures: Iterable[Mapping[str, Any]],
    *,
    lane_name: str,
) -> None:
    for fixture in fixtures:
        entity = copy.deepcopy(dict(fixture))
        entity_id = str(entity["id"])
        existing = release_entities.get(entity_id)
        if existing is not None and existing != entity:
            raise ValueError(f"{lane_name} entity collision for {entity_id}")
        release_entities[entity_id] = entity


def _entity_covers(entity: Mapping[str, Any], low: int, high: int) -> bool:
    start = entity.get("start_year")
    end = entity.get("end_year")
    return start is not None and int(start) <= low and (end is None or int(end) >= high)


# Operational outcome vectors for lane-reclassified campaign events, mirroring
# the reviewed Chadian urban-campaign convention. An exact-contract event that
# a lane reclassifies from "engagement" to "campaign" moves to the operational
# rating track, so its participants must carry the operational dimension set:
# leaving the tactical vector in place makes the release audit warn on every
# dimension of every participant.
_OPERATIONAL_CAMPAIGN_WIN: dict[str, float] = {
    "campaign_objective": 0.86,
    "theater_control": 0.82,
    "force_preservation": 0.72,
    "tempo_initiative": 0.84,
    "logistics_sustainment": 0.78,
}
_OPERATIONAL_CAMPAIGN_LOSS: dict[str, float] = {
    key: round(1.0 - value, 2) for key, value in _OPERATIONAL_CAMPAIGN_WIN.items()
}


def operationalize_campaign_outcomes(event: dict[str, Any]) -> None:
    """Swap a reclassified campaign event's outcome vectors to operational.

    Side A is the winner side for every exact-contract win emission; no lane
    reclassifies a drawn engagement to a campaign, and this fails closed if
    one ever does rather than inventing a drawn operational vector.
    """
    for participant in event["participants"]:
        if "inconclusive" in str(participant.get("termination", "")):
            raise ValueError(
                f"campaign reclassification of a drawn engagement is not "
                f"supported: {event['id']}"
            )
        participant["outcome"] = dict(
            _OPERATIONAL_CAMPAIGN_WIN
            if participant["side"] == "side_a"
            else _OPERATIONAL_CAMPAIGN_LOSS
        )


def promote_exact_hced_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
    contracts: Mapping[str, Mapping[str, Any]],
    *,
    lane_name: str,
    event_id_prefix: str,
) -> list[dict[str, Any]]:
    indexed = rows_by_candidate_id(hced_rows)
    existing = list(existing_events)
    existing_candidates = {
        str(event["hced_candidate_id"])
        for event in existing
        if event.get("hced_candidate_id") is not None
    }
    collisions = sorted(existing_candidates & set(contracts))
    if collisions:
        raise ValueError(f"{lane_name} candidates already promoted: {collisions}")
    existing_keys = {
        _event_key(str(event["name"]), int(event["year"])) for event in existing
    }
    accepted_keys: set[tuple[str, int]] = set()
    events: list[dict[str, Any]] = []
    for candidate_id, contract in sorted(
        contracts.items(),
        key=lambda item: (int(item[1]["canonical_event"]["year_low"]), item[0]),
    ):
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(f"{lane_name} missing exact row for {candidate_id}")
        candidate = rows[0]
        if canonical_hced_row_sha256(candidate) != contract["raw_row_sha256"]:
            raise ValueError(f"{lane_name} raw-row fingerprint changed for {candidate_id}")
        if hced_candidate_id(candidate) != candidate_id:
            raise ValueError(f"{lane_name} candidate ID drift for {candidate_id}")

        canonical = contract["canonical_event"]
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        raw_low = int(candidate["year_low"])
        raw_high = int(candidate["year_high"])
        date_changed = (low, high) != (raw_low, raw_high)
        source_date_override = contract.get("source_date_override") is True
        if date_changed != source_date_override:
            raise ValueError(f"{lane_name} date drift for {candidate_id}")
        if source_date_override:
            date_source_ids = list(map(str, contract.get("date_source_ids", [])))
            evidence_refs = set(map(str, contract.get("evidence_refs", [])))
            if (
                not date_source_ids
                or date_source_ids != sorted(set(date_source_ids))
                or not set(date_source_ids) <= evidence_refs
            ):
                raise ValueError(
                    f"{lane_name} date override lacks closed direct sources for "
                    f"{candidate_id}"
                )
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{lane_name} invalid opposing sides for {candidate_id}")
        for entity_id in (*side_1, *side_2):
            entity = release_entities.get(entity_id)
            if entity is None or not _entity_covers(entity, low, high):
                raise ValueError(
                    f"{lane_name} entity-window violation for {candidate_id}: {entity_id}"
                )

        result_type = str(contract.get("result_type", "win"))
        if result_type not in {"win", "draw"}:
            raise ValueError(
                f"{lane_name} unsupported result type for {candidate_id}: {result_type}"
            )
        if contract.get("source_outcome_override") and not contract.get(
            "outcome_source_ids"
        ):
            raise ValueError(
                f"{lane_name} outcome override lacks direct sources for {candidate_id}"
            )
        is_draw = result_type == "draw"
        if is_draw:
            if normalize_label(candidate.get("winner_raw")) not in _DRAW_LABELS:
                raise ValueError(f"{lane_name} draw assertion drift for {candidate_id}")
            winners: list[str] = []
            losers: list[str] = []
        else:
            winner_side = int(contract["winner_side"])
            if winner_side not in {1, 2}:
                raise ValueError(f"{lane_name} invalid winner side for {candidate_id}")
            if not contract.get("source_outcome_override"):
                if candidate.get("winner_raw") != candidate.get(f"side_{winner_side}_raw"):
                    raise ValueError(f"{lane_name} outcome drift for {candidate_id}")
                if candidate.get("loser_raw") != candidate.get(f"side_{3 - winner_side}_raw"):
                    raise ValueError(f"{lane_name} loser drift for {candidate_id}")
            winners, losers = (
                (side_1, side_2) if winner_side == 1 else (side_2, side_1)
            )

        name = str(canonical["name"])
        key = _event_key(name, low)
        raw_key = _event_key(str(candidate["name"]), raw_low)
        if key in existing_keys or raw_key in existing_keys or key in accepted_keys:
            raise ValueError(f"{lane_name} duplicate event for {candidate_id}")
        accepted_keys.add(key)
        scale, scale_level = _scale(candidate)
        confidence = float(contract.get("confidence", 0.80 if low == high else 0.77))
        war_names = list(map(str, candidate.get("war_names", [])))
        cluster = _slug(war_names[0]) if war_names else None
        outcome_source_ids = list(
            map(str, contract.get("outcome_source_ids", ["hced_dataset"]))
        )
        outcome_family_ids = list(
            map(str, contract.get("outcome_source_family_ids", ["hced"]))
        )
        events.append(
            {
                "id": f"{event_id_prefix}{_slug(candidate_id, 80)}",
                "name": name,
                "year": low,
                "end_year": high,
                "event_type": "engagement",
                "war_type": str(contract.get("war_type", "colonial_anti_colonial")),
                "scale": scale,
                "stakes": "major" if scale_level >= 4 else "limited",
                "decisiveness": (
                    0.32 if is_draw else round(min(0.90, 0.54 + 0.06 * scale_level), 2)
                ),
                "confidence": confidence,
                "geographic_scope": round(min(0.70, 0.08 + 0.09 * scale_level), 2),
                "domain": _domain(candidate.get("theatre_raw")),
                "cluster_id": f"hced_war_{cluster}" if cluster else None,
                "date_precision": str(canonical.get("date_precision", "year")),
                "sequence": int(candidate.get("source_row") or 0),
                "summary": (
                    "Candidate-keyed Wave 8 tactical assertion. The complete source "
                    "row, identities, dates, disposition, and evidence set are pinned; "
                    "no generic label fallback or strategic result is inferred. "
                    + str(contract["audit_note"])
                ),
                "aliases": (
                    [str(candidate["name"])]
                    if str(candidate["name"]) != name
                    else []
                ),
                "participants": _participants(
                    side_1 if is_draw else winners,
                    side_2 if is_draw else losers,
                    is_draw,
                    confidence,
                    scale_level,
                    note=(
                        f"Candidate-keyed {lane_name} tactical contract; no label "
                        "fallback or strategic outcome is inferred."
                    ),
                ),
                "source_ids": ["hced_dataset", *map(str, contract["evidence_refs"])],
                "outcome_source_ids": outcome_source_ids,
                "outcome_source_family_ids": outcome_family_ids,
                "hced_candidate_id": candidate_id,
                "reviewed_granularity": str(canonical.get("granularity", "engagement")),
                "canonical_event_key": str(canonical["canonical_key"]),
                "identity_resolution": "candidate_keyed_exact",
                "status": "complete",
                **build_hced_location_fields(
                    candidate,
                    point_quarantine_ids=HCED_POINT_QUARANTINE_IDS,
                    country_quarantine_ids=HCED_COUNTRY_QUARANTINE_IDS,
                ),
            }
        )
    if len(events) != len(contracts):
        raise ValueError(
            f"{lane_name} promoted {len(events)} rows instead of {len(contracts)}"
        )
    return events
