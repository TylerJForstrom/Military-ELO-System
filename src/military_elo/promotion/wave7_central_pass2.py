"""Candidate-fingerprinted Wave 7 Central/East pass-2 HCED promotions."""

from __future__ import annotations

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
from .wave7_central_pass2_data import (
    WAVE7_CENTRAL_PASS2_ENTITIES,
    WAVE7_CENTRAL_PASS2_FINAL_AUDIT_SIGNATURE,
    WAVE7_CENTRAL_PASS2_HOLDS,
    WAVE7_CENTRAL_PASS2_LABEL_WINDOWS,
    WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS,
    WAVE7_CENTRAL_PASS2_SOURCES,
    WAVE7_CENTRAL_PASS2_TRANSITION_YEAR_HOLDS,
)


WAVE7_CENTRAL_PASS2_PROMOTION_IDS = frozenset(WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS)
WAVE7_CENTRAL_PASS2_HOLD_IDS = frozenset(WAVE7_CENTRAL_PASS2_HOLDS)
WAVE7_CENTRAL_PASS2_RESERVED_IDS = (
    WAVE7_CENTRAL_PASS2_PROMOTION_IDS | WAVE7_CENTRAL_PASS2_HOLD_IDS
)
WAVE7_CENTRAL_PASS2_REUSED_ENTITY_IDS = frozenset(
    {
        "austrian_empire",
        "clio_it_papal_state_1_755_50394c66",
        "french_first_republic",
        "german_empire",
        "ottoman_empire",
        "roman_republic",
    }
)

_RAW_CONTRACT_FIELDS = (
    "candidate_id",
    "source_row",
    "name",
    "year_low",
    "year_high",
    "side_1_raw",
    "side_2_raw",
    "winner_raw",
    "loser_raw",
)


def canonical_row_sha256(row: Mapping[str, Any]) -> str:
    """Hash a complete queue row using canonical compact JSON."""

    payload = json.dumps(
        dict(row),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _raw_contract(row: Mapping[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in _RAW_CONTRACT_FIELDS}


def _rows_by_candidate_id(
    rows: Iterable[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            indexed.setdefault(candidate_id, []).append(row)
    return indexed


def _audit_signature() -> str:
    lines = [
        f"{candidate_id}|{contract['raw_row_sha256']}|promote"
        for candidate_id, contract in WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS.items()
    ]
    lines.extend(
        f"{candidate_id}|{contract['raw_row_sha256']}|hold"
        for candidate_id, contract in WAVE7_CENTRAL_PASS2_HOLDS.items()
    )
    return hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode()).hexdigest()


def _validate_fixture_inventory() -> None:
    if len(WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS) != 31:
        raise ValueError("Wave 7 Central/East pass 2 must contain 31 promotions")
    if len(WAVE7_CENTRAL_PASS2_HOLDS) != 11:
        raise ValueError("Wave 7 Central/East pass 2 must contain 11 holds")
    if len(WAVE7_CENTRAL_PASS2_ENTITIES) != 7:
        raise ValueError("Wave 7 Central/East pass-2 entity inventory changed")
    if len(WAVE7_CENTRAL_PASS2_SOURCES) != 16:
        raise ValueError("Wave 7 Central/East pass-2 source inventory changed")
    if WAVE7_CENTRAL_PASS2_PROMOTION_IDS & WAVE7_CENTRAL_PASS2_HOLD_IDS:
        raise ValueError("Wave 7 Central/East pass-2 promotion/hold overlap")
    if _audit_signature() != WAVE7_CENTRAL_PASS2_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 7 Central/East pass-2 audit signature changed")

    entity_ids = {str(entity["id"]) for entity in WAVE7_CENTRAL_PASS2_ENTITIES}
    source_ids = {str(source["id"]) for source in WAVE7_CENTRAL_PASS2_SOURCES}
    if len(entity_ids) != len(WAVE7_CENTRAL_PASS2_ENTITIES):
        raise ValueError("Wave 7 Central/East pass-2 entity IDs must be unique")
    if len(source_ids) != len(WAVE7_CENTRAL_PASS2_SOURCES):
        raise ValueError("Wave 7 Central/East pass-2 source IDs must be unique")

    for entity in WAVE7_CENTRAL_PASS2_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"Wave 7 pass-2 entity {entity['id']} must be alias-free")
        note = str(entity["continuity_note"]).casefold()
        if "no predecessor or successor rating is inherited" not in note:
            raise ValueError(f"Wave 7 pass-2 entity {entity['id']} permits inheritance")
        if not set(map(str, entity["source_ids"])) <= source_ids:
            raise ValueError(f"Wave 7 pass-2 entity {entity['id']} has unknown source")

    reviewed = {
        **WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS,
        **WAVE7_CENTRAL_PASS2_HOLDS,
    }
    if len(reviewed) != 42:
        raise ValueError("Wave 7 Central/East pass 2 must review exactly 42 rows")
    if len({str(row["raw_row_sha256"]) for row in reviewed.values()}) != 42:
        raise ValueError("Wave 7 Central/East pass-2 row hashes must be unique")
    for candidate_id, contract in reviewed.items():
        if contract["candidate_id"] != candidate_id:
            raise ValueError("Wave 7 Central/East pass-2 candidate-key drift")
        if set(contract["raw_contract"]) != set(_RAW_CONTRACT_FIELDS):
            raise ValueError(
                f"Wave 7 pass-2 semantic fields changed for {candidate_id}"
            )
        if contract["raw_contract"]["candidate_id"] != candidate_id:
            raise ValueError(f"Wave 7 pass-2 semantic candidate drift: {candidate_id}")
        if not set(map(str, contract.get("evidence_refs", ()))) <= source_ids:
            raise ValueError(
                f"Wave 7 pass-2 contract {candidate_id} has unknown source"
            )

    samnite_rows = [
        contract
        for contract in reviewed.values()
        if "samnit" in str(contract["raw_contract"]["side_1_raw"]).casefold()
        or "samnit" in str(contract["raw_contract"]["side_2_raw"]).casefold()
    ]
    if len(samnite_rows) != 14:
        raise ValueError("Current queue must retain all 14 Samnite-labelled reviews")
    if sum(bool(row["latent"]) for row in WAVE7_CENTRAL_PASS2_HOLDS.values()) != 10:
        raise ValueError("Wave 7 Central/East pass 2 must retain 10 latent holds")
    if (
        sum(
            row["category"] == "published_duplicate"
            for row in WAVE7_CENTRAL_PASS2_HOLDS.values()
        )
        != 1
    ):
        raise ValueError(
            "Wave 7 Central/East pass 2 must retain one published duplicate"
        )

    canonical_keys = {
        str(contract["canonical_event"]["canonical_key"])
        for contract in WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS.values()
    }
    if len(canonical_keys) != 31:
        raise ValueError("Wave 7 Central/East pass-2 canonical keys must be unique")
    allowed_entities = entity_ids | WAVE7_CENTRAL_PASS2_REUSED_ENTITY_IDS
    for contract in WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS.values():
        sides = {
            *map(str, contract["side_1_entity_ids"]),
            *map(str, contract["side_2_entity_ids"]),
        }
        if not sides <= allowed_entities:
            raise ValueError("Wave 7 pass-2 promotion names an undeclared entity")

    for label, windows in WAVE7_CENTRAL_PASS2_LABEL_WINDOWS.items():
        previous_high: int | None = None
        for low, high, identities in windows:
            if low > high or (previous_high is not None and low <= previous_high):
                raise ValueError(f"Wave 7 pass-2 generic windows overlap for {label}")
            if not set(identities) <= allowed_entities:
                raise ValueError(f"Wave 7 pass-2 window has unknown entity: {label}")
            previous_high = high


def _validate_exact_contracts(
    rows_by_id: Mapping[str, list[dict[str, Any]]],
    contracts: Mapping[str, Mapping[str, Any]],
    *,
    disposition: str,
) -> None:
    for candidate_id, contract in contracts.items():
        rows = rows_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"Wave 7 Central/East pass-2 {disposition} contract {candidate_id} "
                f"expected one queue row, found {len(rows)}"
            )
        row = rows[0]
        actual_hash = canonical_row_sha256(row)
        expected_hash = str(contract["raw_row_sha256"])
        if actual_hash != expected_hash:
            raise ValueError(
                f"Wave 7 Central/East pass-2 {candidate_id} raw-row fingerprint "
                f"changed ({actual_hash} != {expected_hash})"
            )
        if _raw_contract(row) != contract["raw_contract"]:
            raise ValueError(f"Wave 7 pass-2 {candidate_id} semantic fields changed")
        if hced_candidate_id(row) != candidate_id:
            raise ValueError(f"Wave 7 pass-2 candidate ID changed for {candidate_id}")


def validate_wave7_central_pass2_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all reviewed rows before allowing any pass-2 promotion."""

    _validate_fixture_inventory()
    rows_by_id = _rows_by_candidate_id(hced_rows)
    _validate_exact_contracts(
        rows_by_id,
        WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS,
        disposition="promotion",
    )
    _validate_exact_contracts(
        rows_by_id,
        WAVE7_CENTRAL_PASS2_HOLDS,
        disposition="hold",
    )
    return {
        "reviewed": 42,
        "promoted": 31,
        "held": 11,
        "latent_held": 10,
        "duplicate_held": 1,
    }


def install_wave7_central_pass2_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    """Install exact alias-free identities without replacing existing rows."""

    _validate_fixture_inventory()
    for fixture in WAVE7_CENTRAL_PASS2_ENTITIES:
        entity = dict(fixture)
        entity["aliases"] = list(fixture["aliases"])
        entity["predecessors"] = list(fixture["predecessors"])
        entity["source_ids"] = list(fixture["source_ids"])
        entity_id = str(entity["id"])
        existing = release_entities.get(entity_id)
        if existing is not None and existing != entity:
            raise ValueError(f"Wave 7 pass-2 entity ID collision for {entity_id}")
        release_entities[entity_id] = entity


def install_wave7_central_pass2_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    """Install official/academic context sources without replacing rows."""

    _validate_fixture_inventory()
    for fixture in WAVE7_CENTRAL_PASS2_SOURCES:
        source = dict(fixture)
        source["evidence_roles"] = list(fixture["evidence_roles"])
        source_id = str(source["id"])
        existing = sources_by_id.get(source_id)
        if existing is not None and existing != source:
            raise ValueError(f"Wave 7 pass-2 source ID collision for {source_id}")
        sources_by_id[source_id] = source


def resolve_wave7_central_pass2_identity_ids(
    label: Any,
    low_year: int,
    high_year: int,
    *,
    candidate_id: str | None = None,
) -> tuple[str, ...] | None:
    """Resolve exact reviewed rows or only the narrow frozen label windows."""

    _validate_fixture_inventory()
    if low_year > high_year:
        return None
    normalized = normalize_label(label)
    if not normalized:
        return None
    if candidate_id is not None:
        if candidate_id in WAVE7_CENTRAL_PASS2_HOLD_IDS:
            return None
        contract = WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS.get(candidate_id)
        if contract is None:
            return None
        raw = contract["raw_contract"]
        if (low_year, high_year) != (int(raw["year_low"]), int(raw["year_high"])):
            return None
        if normalized == normalize_label(raw["side_1_raw"]):
            return tuple(map(str, contract["side_1_entity_ids"]))
        if normalized == normalize_label(raw["side_2_raw"]):
            return tuple(map(str, contract["side_2_entity_ids"]))
        return None

    if any(
        low_year <= transition_year <= high_year
        for transition_year in WAVE7_CENTRAL_PASS2_TRANSITION_YEAR_HOLDS.get(
            normalized, frozenset()
        )
    ):
        return None
    for low, high, entity_ids in WAVE7_CENTRAL_PASS2_LABEL_WINDOWS.get(normalized, ()):
        if low <= low_year and high_year <= high:
            return tuple(entity_ids)
    return None


def _entity_covers(entity: Mapping[str, Any], low_year: int, high_year: int) -> bool:
    start_year = entity.get("start_year")
    end_year = entity.get("end_year")
    return (
        start_year is not None
        and int(start_year) <= low_year
        and (end_year is None or int(end_year) >= high_year)
    )


def promote_wave7_central_pass2_hced_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Promote exactly 31 audited rows; generic fallback is never consulted."""

    validate_wave7_central_pass2_queue_contracts(hced_rows)
    rows_by_id = _rows_by_candidate_id(hced_rows)
    existing_event_rows = list(existing_events)
    existing_candidate_ids = {
        str(event["hced_candidate_id"])
        for event in existing_event_rows
        if event.get("hced_candidate_id") is not None
    }
    collisions = sorted(existing_candidate_ids & WAVE7_CENTRAL_PASS2_PROMOTION_IDS)
    if collisions:
        raise ValueError(f"Wave 7 pass-2 HCED candidate already promoted: {collisions}")
    existing_keys = {
        _event_key(str(event["name"]), int(event["year"]))
        for event in existing_event_rows
    }

    events: list[dict[str, Any]] = []
    accepted_keys: set[tuple[str, int]] = set()
    ordered_contracts = sorted(
        WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS.items(),
        key=lambda item: (int(item[1]["canonical_event"]["year_low"]), item[0]),
    )
    for candidate_id, contract in ordered_contracts:
        candidate = rows_by_id[candidate_id][0]
        canonical = contract["canonical_event"]
        low_year = int(canonical["year_low"])
        high_year = int(canonical["year_high"])
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"Wave 7 pass-2 invalid opposing sides: {candidate_id}")
        for entity_id in (*side_1, *side_2):
            entity = release_entities.get(entity_id)
            if entity is None or not _entity_covers(entity, low_year, high_year):
                raise ValueError(
                    f"Wave 7 pass-2 entity-window violation for {candidate_id}: "
                    f"{entity_id}"
                )

        result = contract["result"]
        draw = result["type"] == "draw"
        if draw:
            if normalize_label(candidate.get("winner_raw")) not in {
                "draw",
                "inconclusive",
                "stalemate",
            }:
                raise ValueError(f"Wave 7 pass-2 draw drift for {candidate_id}")
            winner_side, loser_side = side_1, side_2
        else:
            winner_index = int(result["winner_side"])
            winner_label = candidate[f"side_{winner_index}_raw"]
            loser_label = candidate[f"side_{3 - winner_index}_raw"]
            if (
                candidate.get("winner_raw") != winner_label
                or candidate.get("loser_raw") != loser_label
            ):
                raise ValueError(f"Wave 7 pass-2 outcome/side drift: {candidate_id}")
            winner_side, loser_side = (
                (side_1, side_2) if winner_index == 1 else (side_2, side_1)
            )

        event_name = str(canonical["name"])
        event_key = _event_key(event_name, low_year)
        raw_event_key = _event_key(str(candidate["name"]), low_year)
        if event_key in existing_keys or raw_event_key in existing_keys:
            raise ValueError(f"Wave 7 pass-2 source-family duplicate: {candidate_id}")
        if event_key in accepted_keys:
            raise ValueError(f"Wave 7 pass-2 duplicate event key: {candidate_id}")
        accepted_keys.add(event_key)

        scale, scale_level = _scale(candidate)
        confidence = 0.82
        war_names = list(map(str, candidate.get("war_names", [])))
        cluster = _slug(war_names[0]) if war_names else None
        raw_name = str(candidate["name"])
        source_ids = ["hced_dataset", *map(str, contract["evidence_refs"])]
        location_fields = build_hced_location_fields(
            candidate,
            point_quarantine_ids=HCED_POINT_QUARANTINE_IDS,
            country_quarantine_ids=HCED_COUNTRY_QUARANTINE_IDS,
        )
        events.append(
            {
                "id": f"hced_wave7_central_p2_{_slug(candidate_id, 80)}",
                "name": event_name,
                "year": low_year,
                "end_year": high_year,
                "event_type": "engagement",
                "war_type": "interstate_limited",
                "scale": scale,
                "stakes": "major" if scale_level >= 4 else "limited",
                "decisiveness": round(min(0.90, 0.54 + 0.06 * scale_level), 2),
                "confidence": confidence,
                "geographic_scope": round(min(0.70, 0.08 + 0.09 * scale_level), 2),
                "domain": _domain(candidate.get("theatre_raw")),
                "cluster_id": f"hced_war_{cluster}" if cluster else None,
                "date_precision": "year",
                "sequence": int(candidate.get("source_row") or 0),
                "summary": (
                    "Candidate-keyed reviewed HCED result. The complete row, outcome "
                    "orientation, identity boundary, and hold inventory are "
                    "fingerprinted by the Wave 7 Central/East pass-2 contract. "
                    f"{contract['audit_note']}"
                ),
                "aliases": [raw_name] if raw_name != event_name else [],
                "participants": _participants(
                    winner_side,
                    loser_side,
                    draw,
                    confidence,
                    scale_level,
                    note=(
                        "Candidate-keyed Wave 7 Central/East pass-2 HCED tactical "
                        "contract; no broad label fallback or strategic result is inferred."
                    ),
                ),
                "source_ids": source_ids,
                "outcome_source_ids": ["hced_dataset"],
                "outcome_source_family_ids": ["hced"],
                "reviewed_granularity": "engagement",
                "canonical_event_key": str(canonical["canonical_key"]),
                "identity_resolution": "candidate_keyed_exact",
                "hced_candidate_id": candidate_id,
                "status": "complete",
                **location_fields,
            }
        )

    if len(events) != 31:
        raise ValueError(f"Wave 7 Central/East pass 2 promoted {len(events)} rows")
    return events


def wave7_central_pass2_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS.values()
            ).items()
        )
    )


def wave7_central_pass2_hold_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["category"])
                for contract in WAVE7_CENTRAL_PASS2_HOLDS.values()
            ).items()
        )
    )


_validate_fixture_inventory()
