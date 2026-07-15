from __future__ import annotations

"""Candidate-keyed early-modern promotions from the audited Wave 6 lane B."""

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _domain, _event_key, _participants, _scale, _slug, normalize_label
from .hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
    build_hced_location_fields,
    hced_candidate_id,
)
from .wave6_1500_1799_data import (
    WAVE6_ENTITIES,
    WAVE6_FINAL_AUDIT_SIGNATURE,
    WAVE6_HCED_CONTRACTS,
    WAVE6_HCED_EXCLUSIONS,
    WAVE6_HCED_HOLDS,
    WAVE6_SOURCES,
    WAVE6_WIKIDATA_EXCLUSIONS,
)


WAVE6_HCED_CONTRACT_IDS = frozenset(WAVE6_HCED_CONTRACTS)
WAVE6_HCED_EXCLUSION_IDS = frozenset(WAVE6_HCED_EXCLUSIONS)
WAVE6_HCED_HOLD_IDS = frozenset(WAVE6_HCED_HOLDS)
WAVE6_WIKIDATA_EXCLUSION_IDS = frozenset(WAVE6_WIKIDATA_EXCLUSIONS)
WAVE6_HCED_RESERVED_IDS = (
    WAVE6_HCED_CONTRACT_IDS | WAVE6_HCED_HOLD_IDS | WAVE6_HCED_EXCLUSION_IDS
)
WAVE6_HCED_NONPROMOTED_IDS = WAVE6_HCED_HOLD_IDS | WAVE6_HCED_EXCLUSION_IDS

_RAW_CONTRACT_FIELDS = (
    "candidate_id",
    "source_record_id",
    "source_row",
    "name",
    "year_low",
    "year_high",
    "side_1_raw",
    "side_2_raw",
    "winner_raw",
    "loser_raw",
    "war_names",
    "consulted_source_raw",
    "duplicate_source_id",
    "source_snapshot",
)


def canonical_row_sha256(row: Mapping[str, Any]) -> str:
    """Hash one complete queue row using the Phase 1 canonical JSON contract."""

    payload = json.dumps(
        dict(row),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _raw_contract(row: Mapping[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in _RAW_CONTRACT_FIELDS}


def _canonical_object_sha256(value: Mapping[str, Any]) -> str:
    payload = json.dumps(
        dict(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _rows_by_candidate_id(
    rows: Iterable[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            indexed.setdefault(candidate_id, []).append(row)
    return indexed


def _validate_exact_row_contracts(
    rows_by_id: Mapping[str, list[dict[str, Any]]],
    contracts: Mapping[str, Mapping[str, Any]],
    *,
    queue_name: str,
) -> None:
    for candidate_id, contract in contracts.items():
        rows = rows_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"Wave 6 {queue_name} contract {candidate_id} expected exactly one "
                f"queue row, found {len(rows)}"
            )
        actual = canonical_row_sha256(rows[0])
        expected = str(contract["raw_row_sha256"])
        if actual != expected:
            raise ValueError(
                f"Wave 6 {queue_name} contract {candidate_id} raw-row fingerprint "
                f"changed ({actual} != {expected})"
            )


def _validate_fixture_inventory() -> None:
    if len(WAVE6_HCED_CONTRACTS) != 76:
        raise ValueError("Wave 6 lane B must contain exactly 76 active promotion contracts")
    if len(WAVE6_HCED_HOLDS) != 4:
        raise ValueError("Wave 6 lane B must contain exactly 4 cross-lane evidence holds")
    if len(WAVE6_HCED_EXCLUSIONS) != 39:
        raise ValueError("Wave 6 lane B must contain exactly 39 HCED exclusions")
    if len(WAVE6_WIKIDATA_EXCLUSIONS) != 8:
        raise ValueError("Wave 6 lane B must contain exactly 8 Wikidata exclusions")
    if (
        WAVE6_HCED_CONTRACT_IDS & WAVE6_HCED_EXCLUSION_IDS
        or WAVE6_HCED_CONTRACT_IDS & WAVE6_HCED_HOLD_IDS
        or WAVE6_HCED_HOLD_IDS & WAVE6_HCED_EXCLUSION_IDS
    ):
        raise ValueError("Wave 6 promotion, hold, and exclusion inventories overlap")
    if len(WAVE6_ENTITIES) != 21 or len(WAVE6_SOURCES) != 40:
        raise ValueError("Wave 6 entity/source fixture inventory changed")

    reviewed_contracts = {**WAVE6_HCED_CONTRACTS, **WAVE6_HCED_HOLDS}
    canonical_keys = [
        str(contract["canonical_event"]["canonical_key"])
        for contract in reviewed_contracts.values()
    ]
    raw_hashes = [
        str(contract["raw_row_sha256"])
        for contract in reviewed_contracts.values()
    ]
    if len(set(canonical_keys)) != 80 or len(set(raw_hashes)) != 80:
        raise ValueError("Wave 6 canonical keys and raw-row hashes must be unique")
    signature_lines = [
        f"{candidate_id}|{contract['raw_row_sha256']}|"
        f"{contract['canonical_event']['canonical_key']}"
        for candidate_id, contract in reviewed_contracts.items()
    ]
    signature = hashlib.sha256(
        ("\n".join(sorted(signature_lines)) + "\n").encode("utf-8")
    ).hexdigest()
    if signature != WAVE6_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 6 final audit contract signature changed")
    if len({str(contract["cohort"]) for contract in reviewed_contracts.values()}) != 12:
        raise ValueError("Wave 6 promotion cohort inventory changed")
    if (
        sum(
            exclusion["category"] == "unsafe_imperial_collapse"
            for exclusion in WAVE6_HCED_EXCLUSIONS.values()
        )
        != 11
    ):
        raise ValueError("Wave 6 must retain all 11 generic HRE rows as exclusions")

    entity_ids = {str(entity["id"]) for entity in WAVE6_ENTITIES}
    source_ids = {str(source["id"]) for source in WAVE6_SOURCES}
    if len(entity_ids) != len(WAVE6_ENTITIES) or len(source_ids) != len(WAVE6_SOURCES):
        raise ValueError("Wave 6 entity/source IDs must be unique")
    for entity in WAVE6_ENTITIES:
        if not set(map(str, entity["source_ids"])) <= source_ids:
            raise ValueError(f"Wave 6 entity {entity['id']} names an unknown source")
        note = str(entity["continuity_note"]).casefold()
        if "no rating" not in note or entity["aliases"] or entity["predecessors"]:
            raise ValueError(
                f"Wave 6 entity {entity['id']} must be non-inheriting and alias-free"
            )
    for contract in reviewed_contracts.values():
        if not set(map(str, contract["evidence_refs"])) <= source_ids:
            raise ValueError("Wave 6 promotion contract names an unknown evidence source")
        if contract["raw_row_sha256"] != canonical_row_sha256(contract["raw_row"]):
            raise ValueError("Wave 6 embedded promotion row fingerprint changed")
        raw_contract = _raw_contract(contract["raw_row"])
        if raw_contract != contract["raw_contract"]:
            raise ValueError("Wave 6 embedded promotion semantic contract changed")
        if contract["raw_contract_sha256"] != _canonical_object_sha256(raw_contract):
            raise ValueError("Wave 6 embedded promotion semantic fingerprint changed")
    for exclusion in WAVE6_HCED_EXCLUSIONS.values():
        if exclusion["raw_row_sha256"] != canonical_row_sha256(exclusion["raw_row"]):
            raise ValueError("Wave 6 embedded HCED exclusion fingerprint changed")
    for exclusion in WAVE6_WIKIDATA_EXCLUSIONS.values():
        if exclusion["raw_row_sha256"] != canonical_row_sha256(exclusion["raw_row"]):
            raise ValueError("Wave 6 embedded Wikidata exclusion fingerprint changed")


def validate_wave6_queue_contracts(
    hced_rows: list[dict[str, Any]],
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Require the complete audited queue inventory before any lane row can move."""

    _validate_fixture_inventory()
    hced_by_id = _rows_by_candidate_id(hced_rows)
    wikidata_by_id = _rows_by_candidate_id(wikidata_rows)
    _validate_exact_row_contracts(
        hced_by_id,
        WAVE6_HCED_CONTRACTS,
        queue_name="HCED promotion",
    )
    _validate_exact_row_contracts(
        hced_by_id,
        WAVE6_HCED_EXCLUSIONS,
        queue_name="HCED exclusion",
    )
    _validate_exact_row_contracts(
        hced_by_id,
        WAVE6_HCED_HOLDS,
        queue_name="HCED hold",
    )
    _validate_exact_row_contracts(
        wikidata_by_id,
        WAVE6_WIKIDATA_EXCLUSIONS,
        queue_name="Wikidata exclusion",
    )
    for candidate_id, contract in {
        **WAVE6_HCED_CONTRACTS,
        **WAVE6_HCED_HOLDS,
    }.items():
        row = hced_by_id[candidate_id][0]
        raw_contract = _raw_contract(row)
        if raw_contract != contract["raw_contract"]:
            raise ValueError(
                f"Wave 6 HCED promotion contract {candidate_id} semantic fields changed"
            )
        if _canonical_object_sha256(raw_contract) != contract["raw_contract_sha256"]:
            raise ValueError(
                f"Wave 6 HCED promotion contract {candidate_id} semantic hash changed"
            )
    return {
        "promotion_contracts": len(WAVE6_HCED_CONTRACTS),
        "hced_holds": len(WAVE6_HCED_HOLDS),
        "hced_exclusions": len(WAVE6_HCED_EXCLUSIONS),
        "hced_held_total": len(WAVE6_HCED_HOLDS) + len(WAVE6_HCED_EXCLUSIONS),
        "wikidata_exclusions": len(WAVE6_WIKIDATA_EXCLUSIONS),
    }


def install_wave6_entities(release_entities: dict[str, dict[str, Any]]) -> None:
    """Install the 21 exact, non-inheriting identities after generic passes finish."""

    _validate_fixture_inventory()
    for fixture in WAVE6_ENTITIES:
        entity = dict(fixture)
        entity_id = str(entity["id"])
        existing = release_entities.get(entity_id)
        if existing is not None and existing != entity:
            raise ValueError(f"Wave 6 entity ID collision for {entity_id}")
        release_entities[entity_id] = entity


def install_wave6_sources(sources_by_id: dict[str, dict[str, Any]]) -> None:
    """Install official/academic boundary references without replacing a source."""

    _validate_fixture_inventory()
    for fixture in WAVE6_SOURCES:
        source = dict(fixture)
        source_id = str(source["id"])
        existing = sources_by_id.get(source_id)
        if existing is not None and existing != source:
            raise ValueError(f"Wave 6 source ID collision for {source_id}")
        sources_by_id[source_id] = source


def _entity_covers(entity: Mapping[str, Any], low_year: int, high_year: int) -> bool:
    start_year = entity.get("start_year")
    end_year = entity.get("end_year")
    return (
        start_year is not None
        and int(start_year) <= low_year
        and (end_year is None or int(end_year) >= high_year)
    )


def _exact_date_interval(exact_date: Any) -> dict[str, Any] | None:
    if not isinstance(exact_date, str) or not exact_date:
        return None
    return {"start": exact_date, "end": exact_date}


def promote_wave6_hced_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Promote only the 76 active fingerprinted rows; no label resolver is consulted."""

    _validate_fixture_inventory()
    rows_by_id = _rows_by_candidate_id(hced_rows)
    _validate_exact_row_contracts(
        rows_by_id,
        WAVE6_HCED_CONTRACTS,
        queue_name="HCED promotion",
    )

    existing_candidate_ids = {
        str(event["hced_candidate_id"])
        for event in existing_events
        if event.get("hced_candidate_id") is not None
    }
    collisions = sorted(existing_candidate_ids & WAVE6_HCED_CONTRACT_IDS)
    if collisions:
        raise ValueError(f"Wave 6 HCED candidate already promoted: {collisions}")
    existing_keys = {
        _event_key(str(event["name"]), int(event["year"]))
        for event in existing_events
    }

    events: list[dict[str, Any]] = []
    accepted_keys: set[tuple[str, int]] = set()
    ordered_contracts = sorted(
        WAVE6_HCED_CONTRACTS.items(),
        key=lambda item: (
            int(item[1]["canonical_event"]["year_low"]),
            item[0],
        ),
    )
    for candidate_id, contract in ordered_contracts:
        candidate = rows_by_id[candidate_id][0]
        if hced_candidate_id(candidate) != candidate_id:
            raise ValueError(f"Wave 6 HCED candidate ID changed for {candidate_id}")
        canonical = contract["canonical_event"]
        low_year = int(canonical["year_low"])
        high_year = int(canonical["year_high"])
        if (low_year, high_year) != (
            int(candidate["year_low"]),
            int(candidate["year_high"]),
        ):
            raise ValueError(f"Wave 6 canonical date window drift for {candidate_id}")

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"Wave 6 invalid opposing sides for {candidate_id}")
        for entity_id in (*side_1, *side_2):
            entity = release_entities.get(entity_id)
            if entity is None or not _entity_covers(entity, low_year, high_year):
                raise ValueError(
                    f"Wave 6 entity-window violation for {candidate_id}: {entity_id}"
                )

        result = contract["result"]
        draw = result["type"] == "draw"
        if draw:
            if normalize_label(candidate.get("winner_raw")) not in {
                "draw",
                "inconclusive",
                "stalemate",
            }:
                raise ValueError(f"Wave 6 draw orientation drift for {candidate_id}")
            winner_side, loser_side = side_1, side_2
        else:
            winner_index = int(result["winner_side"])
            if winner_index not in {1, 2}:
                raise ValueError(f"Wave 6 invalid winner side for {candidate_id}")
            winner_label = candidate[f"side_{winner_index}_raw"]
            loser_label = candidate[f"side_{3 - winner_index}_raw"]
            if (
                candidate.get("winner_raw") != winner_label
                or candidate.get("loser_raw") != loser_label
            ):
                raise ValueError(f"Wave 6 outcome/side drift for {candidate_id}")
            winner_side, loser_side = (
                (side_1, side_2) if winner_index == 1 else (side_2, side_1)
            )

        event_name = str(canonical["name"])
        event_key = _event_key(event_name, low_year)
        raw_event_key = _event_key(str(candidate["name"]), low_year)
        if event_key in existing_keys or raw_event_key in existing_keys:
            raise ValueError(f"Wave 6 source-family duplicate for {candidate_id}")
        if event_key in accepted_keys:
            raise ValueError(f"Wave 6 duplicate canonical event key for {candidate_id}")
        accepted_keys.add(event_key)

        scale, scale_level = _scale(candidate)
        confidence = round(0.80 - (0.03 if low_year != high_year else 0.0), 2)
        war_names = list(map(str, candidate.get("war_names", [])))
        cluster = _slug(war_names[0]) if war_names else None
        raw_name = str(candidate["name"])
        source_ids = ["hced_dataset", *map(str, contract["evidence_refs"])]
        date_interval = _exact_date_interval(canonical.get("exact_date"))
        location_fields = build_hced_location_fields(
            candidate,
            point_quarantine_ids=HCED_POINT_QUARANTINE_IDS,
            country_quarantine_ids=HCED_COUNTRY_QUARANTINE_IDS,
        )
        event: dict[str, Any] = {
            "id": f"hced_wave6_{_slug(candidate_id, 80)}",
            "name": event_name,
            "year": low_year,
            "end_year": high_year,
            "event_type": "engagement",
            "war_type": "interstate_limited",
            "scale": scale,
            "stakes": "major" if scale_level >= 4 else "limited",
            "decisiveness": (
                0.32 if draw else round(min(0.90, 0.54 + 0.06 * scale_level), 2)
            ),
            "confidence": confidence,
            "geographic_scope": round(min(0.70, 0.08 + 0.09 * scale_level), 2),
            "domain": _domain(candidate.get("theatre_raw")),
            "cluster_id": f"hced_war_{cluster}" if cluster else None,
            "date_precision": str(canonical["date_precision"]),
            "sequence": int(candidate.get("source_row") or 0),
            "summary": (
                "Candidate-keyed reviewed HCED result. The source row, outcome, "
                "participant roster, identity windows, date, granularity, and duplicate "
                f"status are pinned by the Wave 6 contract. {contract['audit_note']}"
            ),
            "aliases": [raw_name] if raw_name != event_name else [],
            "participants": _participants(
                winner_side,
                loser_side,
                draw,
                confidence,
                scale_level,
                note=(
                    "Candidate-keyed Wave 6 HCED tactical contract; no label fallback "
                    "or strategic war outcome is inferred."
                ),
            ),
            "source_ids": source_ids,
            "outcome_source_ids": ["hced_dataset"],
            "outcome_source_family_ids": ["hced"],
            "reviewed_granularity": str(canonical["granularity"]),
            "canonical_event_key": str(canonical["canonical_key"]),
            "identity_resolution": "candidate_keyed_exact",
            "status": "complete",
            **location_fields,
        }
        if date_interval is not None:
            event["date_interval"] = date_interval
        events.append(event)

    if len(events) != 76:
        raise ValueError(f"Wave 6 promoted {len(events)} HCED rows instead of 76")
    return events


def wave6_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(Counter(str(row["cohort"]) for row in WAVE6_HCED_CONTRACTS.values()).items())
    )
