"""Shared orchestration bundle for five independently audited exact HCED lanes.

The underlying Bilbao, Great Northern War, Georgian uprising, Sertorian, and
Polisario modules remain the authorities for row fingerprints and historical
contracts.  This module only combines their disjoint inventories so the main
release builder needs one reservation, installation, promotion, and accounting
hook.  It opens no label aliases and performs no discovery-based promotion.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

from .wave8_bilbao import (
    WAVE8_BILBAO_CONTRACT_IDS,
    WAVE8_BILBAO_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_BILBAO_ENTITIES,
    WAVE8_BILBAO_FINAL_AUDIT_SIGNATURE,
    WAVE8_BILBAO_FUNNEL_AUDIT,
    WAVE8_BILBAO_HOLDS,
    WAVE8_BILBAO_LOCATION_QUARANTINE_REASONS,
    WAVE8_BILBAO_POINT_QUARANTINE_ADDITIONS,
    WAVE8_BILBAO_RESERVED_IDS,
    WAVE8_BILBAO_SOURCES,
    install_wave8_bilbao_entities,
    install_wave8_bilbao_sources,
    promote_wave8_bilbao_contracts,
    validate_wave8_bilbao_current_artifact_state,
    validate_wave8_bilbao_discovery_dispositions,
    validate_wave8_bilbao_integration_dispositions,
    validate_wave8_bilbao_queue_contracts,
    wave8_bilbao_metadata,
)
from .wave8_georgian_uprising import (
    WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS,
    WAVE8_GEORGIAN_UPRISING_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_GEORGIAN_UPRISING_ENTITIES,
    WAVE8_GEORGIAN_UPRISING_FINAL_AUDIT_SIGNATURE,
    WAVE8_GEORGIAN_UPRISING_HOLDS,
    WAVE8_GEORGIAN_UPRISING_LOCATION_QUARANTINE_REASONS,
    WAVE8_GEORGIAN_UPRISING_POINT_QUARANTINE_ADDITIONS,
    WAVE8_GEORGIAN_UPRISING_RESERVED_IDS,
    WAVE8_GEORGIAN_UPRISING_SOURCES,
    install_wave8_georgian_uprising_entities,
    install_wave8_georgian_uprising_sources,
    promote_wave8_georgian_uprising_contracts,
    validate_wave8_georgian_uprising_existing_entities,
    validate_wave8_georgian_uprising_integration_dispositions,
    validate_wave8_georgian_uprising_queue_contracts,
    wave8_georgian_uprising_metadata,
)
from .wave8_great_northern_exact import (
    WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS,
    WAVE8_GREAT_NORTHERN_EXACT_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_GREAT_NORTHERN_EXACT_ENTITIES,
    WAVE8_GREAT_NORTHERN_EXACT_FINAL_AUDIT_SIGNATURE,
    WAVE8_GREAT_NORTHERN_EXACT_HOLDS,
    WAVE8_GREAT_NORTHERN_EXACT_LOCATION_REVIEWS,
    WAVE8_GREAT_NORTHERN_EXACT_POINT_QUARANTINE_ADDITIONS,
    WAVE8_GREAT_NORTHERN_EXACT_RESERVED_IDS,
    WAVE8_GREAT_NORTHERN_EXACT_SOURCES,
    install_wave8_great_northern_exact_entities,
    install_wave8_great_northern_exact_sources,
    promote_wave8_great_northern_exact_contracts,
    validate_wave8_great_northern_exact_existing_entities,
    validate_wave8_great_northern_exact_integration_dispositions,
    validate_wave8_great_northern_exact_queue_contracts,
    wave8_great_northern_exact_metadata,
)
from .wave8_polisario import (
    WAVE8_POLISARIO_CONTRACT_IDS,
    WAVE8_POLISARIO_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_POLISARIO_ENTITIES,
    WAVE8_POLISARIO_FINAL_AUDIT_SIGNATURE,
    WAVE8_POLISARIO_HOLDS,
    WAVE8_POLISARIO_LOCATION_QUARANTINE_REASONS,
    WAVE8_POLISARIO_POINT_QUARANTINE_ADDITIONS,
    WAVE8_POLISARIO_RESERVED_IDS,
    WAVE8_POLISARIO_SOURCES,
    install_wave8_polisario_entities,
    install_wave8_polisario_sources,
    promote_wave8_polisario_contracts,
    validate_wave8_polisario_emissions,
    validate_wave8_polisario_integration_dispositions,
    validate_wave8_polisario_queue_contracts,
    wave8_polisario_metadata,
)
from .wave8_sertorian import (
    WAVE8_SERTORIAN_CONTRACT_IDS,
    WAVE8_SERTORIAN_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_SERTORIAN_ENTITIES,
    WAVE8_SERTORIAN_FINAL_AUDIT_SIGNATURE,
    WAVE8_SERTORIAN_HOLDS,
    WAVE8_SERTORIAN_LOCATION_QUARANTINE_REASONS,
    WAVE8_SERTORIAN_POINT_QUARANTINE_ADDITIONS,
    WAVE8_SERTORIAN_RESERVED_IDS,
    WAVE8_SERTORIAN_SOURCES,
    WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS,
    install_wave8_sertorian_entities,
    install_wave8_sertorian_sources,
    promote_wave8_sertorian_contracts,
    validate_wave8_sertorian_discovery_dispositions,
    validate_wave8_sertorian_queue_contracts,
    wave8_sertorian_metadata,
)


__all__ = (
    "WAVE8_FOLLOWUP_C_CONTRACT_IDS",
    "WAVE8_FOLLOWUP_C_BILBAO_FUNNEL_AUDIT",
    "WAVE8_FOLLOWUP_C_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_FOLLOWUP_C_ENTITIES",
    "WAVE8_FOLLOWUP_C_FINAL_AUDIT_SIGNATURE",
    "WAVE8_FOLLOWUP_C_HOLDS",
    "WAVE8_FOLLOWUP_C_LOCATION_QUARANTINE_REASONS",
    "WAVE8_FOLLOWUP_C_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_FOLLOWUP_C_RESERVED_IDS",
    "WAVE8_FOLLOWUP_C_SOURCES",
    "WAVE8_FOLLOWUP_C_TERMINAL_EXCLUSIONS",
    "install_wave8_followup_c_entities",
    "install_wave8_followup_c_sources",
    "promote_wave8_followup_c_contracts",
    "validate_wave8_followup_c_current_artifact_state",
    "validate_wave8_followup_c_discovery_dispositions",
    "validate_wave8_followup_c_existing_entities",
    "validate_wave8_followup_c_integration_dispositions",
    "validate_wave8_followup_c_queue_contracts",
    "wave8_followup_c_audit_signature",
    "wave8_followup_c_counts",
    "wave8_followup_c_metadata",
)


_LANES = (
    ("bilbao", WAVE8_BILBAO_CONTRACT_IDS, WAVE8_BILBAO_RESERVED_IDS),
    (
        "great_northern_exact",
        WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS,
        WAVE8_GREAT_NORTHERN_EXACT_RESERVED_IDS,
    ),
    (
        "georgian_uprising",
        WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS,
        WAVE8_GEORGIAN_UPRISING_RESERVED_IDS,
    ),
    ("sertorian", WAVE8_SERTORIAN_CONTRACT_IDS, WAVE8_SERTORIAN_RESERVED_IDS),
    ("polisario", WAVE8_POLISARIO_CONTRACT_IDS, WAVE8_POLISARIO_RESERVED_IDS),
)

WAVE8_FOLLOWUP_C_BILBAO_FUNNEL_AUDIT = WAVE8_BILBAO_FUNNEL_AUDIT


def _merge_maps(*maps: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for mapping in maps:
        overlap = set(merged) & set(mapping)
        if overlap:
            raise ValueError(f"Wave 8 follow-up C map collision: {sorted(overlap)}")
        merged.update({str(key): dict(value) for key, value in mapping.items()})
    return merged


WAVE8_FOLLOWUP_C_CONTRACT_IDS = frozenset().union(
    *(contract_ids for _, contract_ids, _ in _LANES)
)
WAVE8_FOLLOWUP_C_RESERVED_IDS = frozenset().union(
    *(reserved_ids for _, _, reserved_ids in _LANES)
)
WAVE8_FOLLOWUP_C_ENTITIES = (
    *WAVE8_BILBAO_ENTITIES,
    *WAVE8_GREAT_NORTHERN_EXACT_ENTITIES,
    *WAVE8_GEORGIAN_UPRISING_ENTITIES,
    *WAVE8_SERTORIAN_ENTITIES,
    *WAVE8_POLISARIO_ENTITIES,
)
WAVE8_FOLLOWUP_C_SOURCES = (
    *WAVE8_BILBAO_SOURCES,
    *WAVE8_GREAT_NORTHERN_EXACT_SOURCES,
    *WAVE8_GEORGIAN_UPRISING_SOURCES,
    *WAVE8_SERTORIAN_SOURCES,
    *WAVE8_POLISARIO_SOURCES,
)
WAVE8_FOLLOWUP_C_HOLDS = _merge_maps(
    WAVE8_BILBAO_HOLDS,
    WAVE8_GREAT_NORTHERN_EXACT_HOLDS,
    WAVE8_GEORGIAN_UPRISING_HOLDS,
    WAVE8_SERTORIAN_HOLDS,
    WAVE8_POLISARIO_HOLDS,
)
WAVE8_FOLLOWUP_C_TERMINAL_EXCLUSIONS = _merge_maps(
    WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS,
)
WAVE8_FOLLOWUP_C_POINT_QUARANTINE_ADDITIONS = frozenset().union(
    WAVE8_BILBAO_POINT_QUARANTINE_ADDITIONS,
    WAVE8_GREAT_NORTHERN_EXACT_POINT_QUARANTINE_ADDITIONS,
    WAVE8_GEORGIAN_UPRISING_POINT_QUARANTINE_ADDITIONS,
    WAVE8_SERTORIAN_POINT_QUARANTINE_ADDITIONS,
    WAVE8_POLISARIO_POINT_QUARANTINE_ADDITIONS,
) & WAVE8_FOLLOWUP_C_CONTRACT_IDS
WAVE8_FOLLOWUP_C_COUNTRY_QUARANTINE_ADDITIONS = frozenset().union(
    WAVE8_BILBAO_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_GREAT_NORTHERN_EXACT_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_GEORGIAN_UPRISING_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_SERTORIAN_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_POLISARIO_COUNTRY_QUARANTINE_ADDITIONS,
)
WAVE8_FOLLOWUP_C_LOCATION_QUARANTINE_REASONS = _merge_maps(
    WAVE8_BILBAO_LOCATION_QUARANTINE_REASONS,
    WAVE8_GREAT_NORTHERN_EXACT_LOCATION_REVIEWS,
    WAVE8_GEORGIAN_UPRISING_LOCATION_QUARANTINE_REASONS,
    WAVE8_SERTORIAN_LOCATION_QUARANTINE_REASONS,
    WAVE8_POLISARIO_LOCATION_QUARANTINE_REASONS,
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def wave8_followup_c_audit_signature() -> str:
    payload = {
        "contract_ids": sorted(WAVE8_FOLLOWUP_C_CONTRACT_IDS),
        "country_quarantine": sorted(WAVE8_FOLLOWUP_C_COUNTRY_QUARANTINE_ADDITIONS),
        "entity_ids": sorted(str(item["id"]) for item in WAVE8_FOLLOWUP_C_ENTITIES),
        "holds": WAVE8_FOLLOWUP_C_HOLDS,
        "lane_signatures": {
            "bilbao": WAVE8_BILBAO_FINAL_AUDIT_SIGNATURE,
            "georgian_uprising": WAVE8_GEORGIAN_UPRISING_FINAL_AUDIT_SIGNATURE,
            "great_northern_exact": WAVE8_GREAT_NORTHERN_EXACT_FINAL_AUDIT_SIGNATURE,
            "polisario": WAVE8_POLISARIO_FINAL_AUDIT_SIGNATURE,
            "sertorian": WAVE8_SERTORIAN_FINAL_AUDIT_SIGNATURE,
        },
        "location_reasons": WAVE8_FOLLOWUP_C_LOCATION_QUARANTINE_REASONS,
        "point_quarantine": sorted(WAVE8_FOLLOWUP_C_POINT_QUARANTINE_ADDITIONS),
        "reserved_ids": sorted(WAVE8_FOLLOWUP_C_RESERVED_IDS),
        "source_ids": sorted(str(item["id"]) for item in WAVE8_FOLLOWUP_C_SOURCES),
        "terminal_exclusions": WAVE8_FOLLOWUP_C_TERMINAL_EXCLUSIONS,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


WAVE8_FOLLOWUP_C_FINAL_AUDIT_SIGNATURE = (
    "0b2d2f35a82e714b90f82983ed899faa432e975c8c72b55dabfe777f9f662632"
)


def _validate_static() -> None:
    contract_sets = [set(contract_ids) for _, contract_ids, _ in _LANES]
    reserved_sets = [set(reserved_ids) for _, _, reserved_ids in _LANES]
    if sum(map(len, contract_sets)) != len(WAVE8_FOLLOWUP_C_CONTRACT_IDS):
        raise ValueError("Wave 8 follow-up C promotion inventories overlap")
    if sum(map(len, reserved_sets)) != len(WAVE8_FOLLOWUP_C_RESERVED_IDS):
        raise ValueError("Wave 8 follow-up C reservation inventories overlap")
    nonratings = set(WAVE8_FOLLOWUP_C_HOLDS) | set(
        WAVE8_FOLLOWUP_C_TERMINAL_EXCLUSIONS
    )
    if WAVE8_FOLLOWUP_C_CONTRACT_IDS & nonratings:
        raise ValueError("Wave 8 follow-up C promotion/nonrating inventories overlap")
    if set(WAVE8_FOLLOWUP_C_HOLDS) & set(WAVE8_FOLLOWUP_C_TERMINAL_EXCLUSIONS):
        raise ValueError("Wave 8 follow-up C hold/exclusion inventories overlap")
    if WAVE8_FOLLOWUP_C_RESERVED_IDS != (
        WAVE8_FOLLOWUP_C_CONTRACT_IDS
        | set(WAVE8_FOLLOWUP_C_HOLDS)
        | set(WAVE8_FOLLOWUP_C_TERMINAL_EXCLUSIONS)
    ):
        raise ValueError("Wave 8 follow-up C disposition inventory drift")
    entity_ids = [str(item["id"]) for item in WAVE8_FOLLOWUP_C_ENTITIES]
    source_ids = [str(item["id"]) for item in WAVE8_FOLLOWUP_C_SOURCES]
    if len(entity_ids) != len(set(entity_ids)):
        raise ValueError("Wave 8 follow-up C entity collision")
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("Wave 8 follow-up C source collision")
    if wave8_followup_c_audit_signature() != WAVE8_FOLLOWUP_C_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 follow-up C final audit signature changed")


def validate_wave8_followup_c_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    _validate_static()
    return {
        "bilbao": validate_wave8_bilbao_queue_contracts(hced_rows),
        "georgian_uprising": validate_wave8_georgian_uprising_queue_contracts(
            hced_rows
        ),
        "great_northern_exact": validate_wave8_great_northern_exact_queue_contracts(
            hced_rows
        ),
        "polisario": validate_wave8_polisario_queue_contracts(hced_rows),
        "sertorian": validate_wave8_sertorian_queue_contracts(hced_rows),
    }


def validate_wave8_followup_c_discovery_dispositions(
    wikidata_battle_rows: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    _validate_static()
    return {
        "bilbao": validate_wave8_bilbao_discovery_dispositions(
            wikidata_battle_rows
        ),
        "sertorian": validate_wave8_sertorian_discovery_dispositions(
            wikidata_battle_rows
        ),
    }


def install_wave8_followup_c_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_wave8_bilbao_entities(release_entities)
    install_wave8_great_northern_exact_entities(release_entities)
    install_wave8_georgian_uprising_entities(release_entities)
    install_wave8_sertorian_entities(release_entities)
    install_wave8_polisario_entities(release_entities)


def validate_wave8_followup_c_existing_entities(
    release_entities: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    _validate_static()
    return {
        "georgian_uprising": validate_wave8_georgian_uprising_existing_entities(
            release_entities
        ),
        "great_northern_exact": validate_wave8_great_northern_exact_existing_entities(
            release_entities
        ),
    }


def install_wave8_followup_c_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_wave8_bilbao_sources(sources_by_id)
    install_wave8_great_northern_exact_sources(sources_by_id)
    install_wave8_georgian_uprising_sources(sources_by_id)
    install_wave8_sertorian_sources(sources_by_id)
    install_wave8_polisario_sources(sources_by_id)


def promote_wave8_followup_c_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    _validate_static()
    existing = list(existing_events)
    promoted: list[dict[str, Any]] = []
    for promoter in (
        promote_wave8_bilbao_contracts,
        promote_wave8_great_northern_exact_contracts,
        promote_wave8_georgian_uprising_contracts,
        promote_wave8_sertorian_contracts,
        promote_wave8_polisario_contracts,
    ):
        lane_events = promoter(hced_rows, release_entities, [*existing, *promoted])
        promoted.extend(lane_events)
    validate_wave8_polisario_emissions(
        event
        for event in promoted
        if event.get("hced_candidate_id") in WAVE8_POLISARIO_CONTRACT_IDS
    )
    if len(promoted) != len(WAVE8_FOLLOWUP_C_CONTRACT_IDS):
        raise ValueError("Wave 8 follow-up C promotion count drift")
    return promoted


def validate_wave8_followup_c_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwd_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    events = list(existing_events)
    return {
        "bilbao": validate_wave8_bilbao_integration_dispositions(
            hced_rows, iwd_rows, iwbd_rows, events
        ),
        "georgian_uprising": (
            validate_wave8_georgian_uprising_integration_dispositions(
                hced_rows, iwbd_rows, events
            )
        ),
        "great_northern_exact": (
            validate_wave8_great_northern_exact_integration_dispositions(
                hced_rows, iwbd_rows, events
            )
        ),
        "polisario": validate_wave8_polisario_integration_dispositions(
            hced_rows, iwbd_rows, events
        ),
    }


def validate_wave8_followup_c_current_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    return {
        "bilbao": validate_wave8_bilbao_current_artifact_state(
            release_events, release_entities, release_sources
        )
    }


def wave8_followup_c_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_FOLLOWUP_C_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "holds": len(WAVE8_FOLLOWUP_C_HOLDS),
        "new_entities": len(WAVE8_FOLLOWUP_C_ENTITIES),
        "new_sources": len(WAVE8_FOLLOWUP_C_SOURCES),
        "newly_rated_events": len(WAVE8_FOLLOWUP_C_CONTRACT_IDS),
        "point_quarantine_additions": len(
            WAVE8_FOLLOWUP_C_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_FOLLOWUP_C_CONTRACT_IDS),
        "reviewed_hced_rows": len(WAVE8_FOLLOWUP_C_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_FOLLOWUP_C_TERMINAL_EXCLUSIONS),
    }


def wave8_followup_c_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_followup_c_counts(),
        "final_audit_signature": WAVE8_FOLLOWUP_C_FINAL_AUDIT_SIGNATURE,
        "lanes": {
            "bilbao": wave8_bilbao_metadata(),
            "georgian_uprising": wave8_georgian_uprising_metadata(),
            "great_northern_exact": wave8_great_northern_exact_metadata(),
            "polisario": wave8_polisario_metadata(),
            "sertorian": wave8_sertorian_metadata(),
        },
        "promoted_candidate_ids": sorted(WAVE8_FOLLOWUP_C_CONTRACT_IDS),
        "reserved_candidate_ids": sorted(WAVE8_FOLLOWUP_C_RESERVED_IDS),
    }


if WAVE8_FOLLOWUP_C_FINAL_AUDIT_SIGNATURE != "TO_BE_SEALED":
    _validate_static()
