"""Fail-closed WEST promotions for Wave 7."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _domain, _event_key, _participants, _scale, _slug
from .hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
    build_hced_location_fields,
    hced_candidate_id,
)
from .wave7_west_data import (
    WAVE7_WEST_AUDIT_SIGNATURE,
    WAVE7_WEST_BAVARIA_NEW_IDS,
    WAVE7_WEST_DUTCH_PROTECTED_IDS,
    WAVE7_WEST_ENTITIES,
    WAVE7_WEST_EXPECTED_HASHES,
    WAVE7_WEST_HCED_CONTRACTS,
    WAVE7_WEST_HCED_HOLDS,
    WAVE7_WEST_HOLD_IDS,
    WAVE7_WEST_NETHERLANDS_NEW_IDS,
    WAVE7_WEST_PROTECTED_RATED,
    WAVE7_WEST_ROSES_NEW_IDS,
    WAVE7_WEST_ROSES_PROTECTED_IDS,
    WAVE7_WEST_SOURCES,
)


WAVE7_WEST_HCED_CONTRACT_IDS = frozenset(WAVE7_WEST_HCED_CONTRACTS)
WAVE7_WEST_PROTECTED_RATED_IDS = frozenset(WAVE7_WEST_PROTECTED_RATED)
WAVE7_WEST_HCED_RESERVED_IDS = (
    WAVE7_WEST_HCED_CONTRACT_IDS | WAVE7_WEST_HOLD_IDS | WAVE7_WEST_PROTECTED_RATED_IDS
)


def canonical_row_sha256(row: Mapping[str, Any]) -> str:
    """Hash a complete queue row under the canonical Phase 1 JSON contract."""

    payload = json.dumps(
        dict(row),
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


def _validate_exact_rows(
    rows_by_id: Mapping[str, list[dict[str, Any]]],
    contracts: Mapping[str, Mapping[str, Any]],
    *,
    disposition: str,
) -> None:
    for candidate_id, contract in contracts.items():
        rows = rows_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"Wave 7 WEST {disposition} contract {candidate_id} expected "
                f"exactly one queue row, found {len(rows)}"
            )
        actual = canonical_row_sha256(rows[0])
        expected = str(contract["raw_row_sha256"])
        if actual != expected:
            raise ValueError(
                f"Wave 7 WEST {disposition} contract {candidate_id} raw-row "
                f"fingerprint changed ({actual} != {expected})"
            )


def _audit_signature() -> str:
    lines: list[str] = []
    for candidate_id, contract in WAVE7_WEST_HCED_CONTRACTS.items():
        lines.append(f"{candidate_id}|{contract['raw_row_sha256']}|promote")
    for candidate_id, contract in WAVE7_WEST_HCED_HOLDS.items():
        lines.append(
            f"{candidate_id}|{contract['raw_row_sha256']}|"
            f"hold:{contract['hold_category']}"
        )
    for candidate_id, contract in WAVE7_WEST_PROTECTED_RATED.items():
        lines.append(
            f"{candidate_id}|{contract['raw_row_sha256']}|"
            f"protect:{contract['expected_event_id']}"
        )
    return hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode("utf-8")).hexdigest()


def _validate_fixture_inventory() -> None:
    if len(WAVE7_WEST_HCED_CONTRACTS) != 29:
        raise ValueError("Wave 7 WEST must contain exactly 29 net-new promotions")
    if len(WAVE7_WEST_HCED_HOLDS) != 13:
        raise ValueError("Wave 7 WEST must contain exactly 13 explicit holds")
    if len(WAVE7_WEST_PROTECTED_RATED) != 15:
        raise ValueError("Wave 7 WEST must protect exactly 15 existing ratings")
    if len(WAVE7_WEST_ENTITIES) != 14 or len(WAVE7_WEST_SOURCES) != 17:
        raise ValueError("Wave 7 WEST entity/source inventory changed")
    inventories = (
        WAVE7_WEST_HCED_CONTRACT_IDS,
        WAVE7_WEST_HOLD_IDS,
        WAVE7_WEST_PROTECTED_RATED_IDS,
    )
    if any(
        left & right
        for index, left in enumerate(inventories)
        for right in inventories[index + 1 :]
    ):
        raise ValueError("Wave 7 WEST dispositions overlap")
    if WAVE7_WEST_HCED_RESERVED_IDS != frozenset(WAVE7_WEST_EXPECTED_HASHES):
        raise ValueError("Wave 7 WEST reviewed inventory is not the exact 57-row set")
    if len(WAVE7_WEST_ROSES_NEW_IDS) != 5:
        raise ValueError("Wave 7 WEST Roses net-new count changed")
    if len(WAVE7_WEST_ROSES_PROTECTED_IDS) != 13:
        raise ValueError("Wave 7 WEST Roses protected count changed")
    if len(WAVE7_WEST_BAVARIA_NEW_IDS) != 14:
        raise ValueError("Wave 7 WEST Bavaria count changed")
    if len(WAVE7_WEST_NETHERLANDS_NEW_IDS) != 10:
        raise ValueError("Wave 7 WEST Netherlands net-new count changed")
    if len(WAVE7_WEST_DUTCH_PROTECTED_IDS) != 2:
        raise ValueError("Wave 7 WEST Dutch protected count changed")
    if _audit_signature() != WAVE7_WEST_AUDIT_SIGNATURE:
        raise ValueError("Wave 7 WEST final audit signature changed")

    reviewed = {
        **WAVE7_WEST_HCED_CONTRACTS,
        **WAVE7_WEST_HCED_HOLDS,
        **WAVE7_WEST_PROTECTED_RATED,
    }
    raw_hashes: list[str] = []
    for candidate_id, contract in reviewed.items():
        if contract["raw_row"]["candidate_id"] != candidate_id:
            raise ValueError(f"Wave 7 WEST embedded candidate ID drift: {candidate_id}")
        actual_hash = canonical_row_sha256(contract["raw_row"])
        expected_hash = WAVE7_WEST_EXPECTED_HASHES[candidate_id]
        if actual_hash != expected_hash or contract["raw_row_sha256"] != expected_hash:
            raise ValueError(
                f"Wave 7 WEST embedded row fingerprint changed: {candidate_id}"
            )
        raw_hashes.append(expected_hash)
    if len(set(raw_hashes)) != 57:
        raise ValueError("Wave 7 WEST raw-row fingerprints must be unique")

    source_ids = {str(source["id"]) for source in WAVE7_WEST_SOURCES}
    entity_ids = {str(entity["id"]) for entity in WAVE7_WEST_ENTITIES}
    if len(source_ids) != len(WAVE7_WEST_SOURCES):
        raise ValueError("Wave 7 WEST source IDs must be unique")
    if len(entity_ids) != len(WAVE7_WEST_ENTITIES):
        raise ValueError("Wave 7 WEST entity IDs must be unique")
    for source in WAVE7_WEST_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError("Wave 7 WEST sources must be direct HTTPS records")
    for entity in WAVE7_WEST_ENTITIES:
        if not set(map(str, entity["source_ids"])) <= source_ids:
            raise ValueError(f"Wave 7 WEST entity {entity['id']} has unknown source")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(
                f"Wave 7 WEST entity {entity['id']} must be alias-free/non-inheriting"
            )
        if "no rating" not in str(entity["continuity_note"]).casefold():
            raise ValueError(
                f"Wave 7 WEST entity {entity['id']} lacks no-rating boundary"
            )
    for contract in (
        *WAVE7_WEST_HCED_CONTRACTS.values(),
        *WAVE7_WEST_HCED_HOLDS.values(),
    ):
        if not set(map(str, contract["evidence_refs"])) <= source_ids:
            raise ValueError("Wave 7 WEST contract cites an unknown direct source")
    canonical_keys = [
        str(contract["canonical_event"]["canonical_key"])
        for contract in WAVE7_WEST_HCED_CONTRACTS.values()
    ]
    if len(set(canonical_keys)) != 29:
        raise ValueError("Wave 7 WEST canonical event keys must be unique")
    prior_hold_resolutions = {
        candidate_id: contract.get("prior_wave6_hold_resolution")
        for candidate_id, contract in WAVE7_WEST_HCED_CONTRACTS.items()
        if contract.get("prior_wave6_hold_resolution") is not None
    }
    if prior_hold_resolutions != {
        "hced-Twt Hill1463-1": "corrected_exact_date",
        "hced-Bamburgh1464-1": "corrected_outcome",
        "hced-Caister Castle1469-1": "corrected_participants",
        "hced-Lose-Coat Field1470-1": "corrected_participants",
        "hced-Bosworth Field1485-1": "candidate_specific_coalition",
    }:
        raise ValueError("Wave 7 WEST prior Wave 6 hold resolutions changed")
    inherited_holds = {
        candidate_id
        for candidate_id, hold in WAVE7_WEST_HCED_HOLDS.items()
        if hold.get("inherited_wave6_hold")
    }
    if inherited_holds != {
        "hced-Dunstable1461-1",
        "hced-Ferrybridge1461-1",
    }:
        raise ValueError("Wave 7 WEST inherited Wave 6 holds changed")
    for contract in WAVE7_WEST_HCED_CONTRACTS.values():
        outcome_ids = set(map(str, contract["outcome_source_ids"]))
        if outcome_ids != {"hced_dataset"} and not outcome_ids <= set(
            map(str, contract["evidence_refs"])
        ):
            raise ValueError("Wave 7 WEST corrected outcome lacks direct evidence")


def validate_wave7_west_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Require all 57 reviewed rows before any WEST promotion can run."""

    _validate_fixture_inventory()
    rows_by_id = _rows_by_candidate_id(hced_rows)
    _validate_exact_rows(
        rows_by_id,
        WAVE7_WEST_HCED_CONTRACTS,
        disposition="promotion",
    )
    _validate_exact_rows(
        rows_by_id,
        WAVE7_WEST_HCED_HOLDS,
        disposition="hold",
    )
    _validate_exact_rows(
        rows_by_id,
        WAVE7_WEST_PROTECTED_RATED,
        disposition="protected",
    )
    return {
        "reviewed": 57,
        "net_new_promotions": 29,
        "holds": 13,
        "protected_existing": 15,
        "roses_rated_total": 18,
        "roses_net_new": 5,
        "roses_preserved_holds": 2,
        "bavaria_net_new": 14,
        "netherlands_net_new": 10,
    }


def install_wave7_west_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    """Install only the fourteen exact, alias-free WEST identities."""

    _validate_fixture_inventory()
    for fixture in WAVE7_WEST_ENTITIES:
        entity = dict(fixture)
        entity_id = str(entity["id"])
        existing = release_entities.get(entity_id)
        if existing is not None and existing != entity:
            raise ValueError(f"Wave 7 WEST entity ID collision for {entity_id}")
        release_entities[entity_id] = entity


def install_wave7_west_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    """Install direct official/academic sources without replacing a record."""

    _validate_fixture_inventory()
    for fixture in WAVE7_WEST_SOURCES:
        source = dict(fixture)
        source_id = str(source["id"])
        existing = sources_by_id.get(source_id)
        if existing is not None and existing != source:
            raise ValueError(f"Wave 7 WEST source ID collision for {source_id}")
        sources_by_id[source_id] = source


def _entity_covers(
    entity: Mapping[str, Any],
    low_year: int,
    high_year: int,
) -> bool:
    start_year = entity.get("start_year")
    end_year = entity.get("end_year")
    return (
        start_year is not None
        and int(start_year) <= low_year
        and (end_year is None or int(end_year) >= high_year)
    )


def validate_wave7_west_protected_events(
    existing_events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    """Prove that already-rated Roses and 1811 Dutch rows retain ownership."""

    _validate_fixture_inventory()
    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for event in existing_events:
        candidate_id = event.get("hced_candidate_id")
        if isinstance(candidate_id, str):
            by_candidate.setdefault(candidate_id, []).append(event)

    for candidate_id, contract in WAVE7_WEST_PROTECTED_RATED.items():
        events = by_candidate.get(candidate_id, [])
        if len(events) != 1:
            raise ValueError(
                f"Wave 7 WEST protected candidate {candidate_id} expected exactly "
                f"one existing event, found {len(events)}"
            )
        event = events[0]
        if event.get("id") != contract["expected_event_id"]:
            raise ValueError(
                f"Wave 7 WEST protected event ownership changed for {candidate_id}"
            )
        if event.get("identity_resolution") != contract["expected_identity_resolution"]:
            raise ValueError(
                f"Wave 7 WEST protected identity method changed for {candidate_id}"
            )
        expected = Counter(
            (item["entity_id"], item["termination"])
            for item in contract["expected_roster"]
        )
        actual = Counter(
            (participant.get("entity_id"), participant.get("termination"))
            for participant in event.get("participants", [])
        )
        if actual != expected:
            raise ValueError(
                f"Wave 7 WEST protected participant ownership changed for "
                f"{candidate_id}"
            )
        if candidate_id in WAVE7_WEST_DUTCH_PROTECTED_IDS and any(
            participant.get("entity_id") == "kingdom_netherlands_1815"
            for participant in event.get("participants", [])
        ):
            raise ValueError(
                f"Wave 7 WEST incorrectly migrated 1811 Dutch row {candidate_id}"
            )
    return {
        "protected_existing": 15,
        "protected_roses": 13,
        "protected_dutch_1811": 2,
    }


def _exact_date_interval(exact_date: Any) -> dict[str, str] | None:
    if not isinstance(exact_date, str) or not exact_date:
        return None
    return {"start": exact_date, "end": exact_date}


def promote_wave7_west_hced_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Promote exactly 29 net-new rows; no label fallback is consulted."""

    validate_wave7_west_queue_contracts(hced_rows)
    existing_events = list(existing_events)
    validate_wave7_west_protected_events(existing_events)
    rows_by_id = _rows_by_candidate_id(hced_rows)

    existing_candidate_ids = {
        str(event["hced_candidate_id"])
        for event in existing_events
        if event.get("hced_candidate_id") is not None
    }
    collisions = sorted(existing_candidate_ids & WAVE7_WEST_HCED_CONTRACT_IDS)
    if collisions:
        raise ValueError(f"Wave 7 WEST HCED candidate already promoted: {collisions}")
    existing_keys = {
        _event_key(str(event["name"]), int(event["year"])) for event in existing_events
    }

    events: list[dict[str, Any]] = []
    accepted_keys: set[tuple[str, int]] = set()
    ordered_contracts = sorted(
        WAVE7_WEST_HCED_CONTRACTS.items(),
        key=lambda item: (
            int(item[1]["canonical_event"]["year_low"]),
            item[0],
        ),
    )
    for candidate_id, contract in ordered_contracts:
        candidate = rows_by_id[candidate_id][0]
        if hced_candidate_id(candidate) != candidate_id:
            raise ValueError(f"Wave 7 WEST candidate ID changed for {candidate_id}")
        canonical = contract["canonical_event"]
        low_year = int(canonical["year_low"])
        high_year = int(canonical["year_high"])
        raw_window = (
            int(candidate["year_low"]),
            int(candidate["year_high"]),
        )
        if (low_year, high_year) != raw_window:
            if not (
                candidate_id == "hced-Twt Hill1463-1"
                and raw_window == (1463, 1463)
                and (low_year, high_year) == (1461, 1461)
                and contract.get("prior_wave6_hold_resolution")
                == "corrected_exact_date"
            ):
                raise ValueError(
                    f"Wave 7 WEST canonical date window drift for {candidate_id}"
                )

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"Wave 7 WEST invalid opposing sides for {candidate_id}")
        for entity_id in (*side_1, *side_2):
            entity = release_entities.get(entity_id)
            if entity is None or not _entity_covers(entity, low_year, high_year):
                raise ValueError(
                    f"Wave 7 WEST entity-window violation for {candidate_id}: "
                    f"{entity_id}"
                )

        winner_index = int(contract["result"]["winner_side"])
        winner_label = candidate[f"side_{winner_index}_raw"]
        loser_label = candidate[f"side_{3 - winner_index}_raw"]
        if contract.get("source_outcome_override"):
            if not (
                candidate_id == "hced-Bamburgh1464-1"
                and winner_index == 2
                and candidate.get("winner_raw") == candidate["side_1_raw"]
                and candidate.get("loser_raw") == candidate["side_2_raw"]
            ):
                raise ValueError(
                    f"Wave 7 WEST corrected outcome contract drift for {candidate_id}"
                )
        elif (
            candidate.get("winner_raw") != winner_label
            or candidate.get("loser_raw") != loser_label
        ):
            raise ValueError(f"Wave 7 WEST outcome/side drift for {candidate_id}")
        winner_side, loser_side = (
            (side_1, side_2) if winner_index == 1 else (side_2, side_1)
        )

        event_name = str(canonical["name"])
        event_key = _event_key(event_name, low_year)
        raw_event_key = _event_key(str(candidate["name"]), low_year)
        if event_key in existing_keys or raw_event_key in existing_keys:
            raise ValueError(f"Wave 7 WEST source-family duplicate for {candidate_id}")
        if event_key in accepted_keys:
            raise ValueError(
                f"Wave 7 WEST duplicate canonical event key for {candidate_id}"
            )
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
            "id": f"hced_wave7_west_{_slug(candidate_id, 80)}",
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
            "date_precision": str(canonical["date_precision"]),
            "sequence": int(candidate.get("source_row") or 0),
            "summary": (
                "Candidate-keyed reviewed HCED tactical result. The complete source "
                "row, outcome, participant roster, identity windows, and disposition "
                f"are pinned by the Wave 7 WEST contract. {contract['audit_note']}"
            ),
            "aliases": [raw_name] if raw_name != event_name else [],
            "participants": _participants(
                winner_side,
                loser_side,
                False,
                confidence,
                scale_level,
                note=(
                    "Candidate-keyed Wave 7 WEST tactical contract; no label fallback "
                    "or strategic war outcome is inferred."
                ),
            ),
            "source_ids": source_ids,
            "outcome_source_ids": list(map(str, contract["outcome_source_ids"])),
            "outcome_source_family_ids": list(
                map(str, contract["outcome_source_family_ids"])
            ),
            "reviewed_granularity": str(canonical["granularity"]),
            "canonical_event_key": str(canonical["canonical_key"]),
            "identity_resolution": "candidate_keyed_exact",
            "status": "complete",
            **location_fields,
        }
        if date_interval is not None:
            event["date_interval"] = date_interval
        events.append(event)

    if len(events) != 29:
        raise ValueError(f"Wave 7 WEST promoted {len(events)} rows instead of 29")
    return events


def wave7_west_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE7_WEST_HCED_CONTRACTS.values()
            ).items()
        )
    )
