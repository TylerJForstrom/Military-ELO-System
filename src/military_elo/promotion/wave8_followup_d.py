"""Shared fail-closed bundle for the five follow-up D exact HCED lanes.

The lane modules remain authoritative for row fingerprints, historical
contracts, discovery dispositions, and source evidence.  This module only
combines their disjoint inventories for release orchestration.  It creates no
label policies or aliases and never treats a discovery candidate as a rating.
"""

from __future__ import annotations

import hashlib
import json
from types import ModuleType
from typing import Any, Iterable, Mapping

from . import wave8_cuban as cuban
from . import wave8_finnish_civil_war as finnish_civil_war
from . import wave8_irish_royalists as irish_royalists
from . import wave8_lower_canada as lower_canada
from . import wave8_swabian_hre as swabian_hre


__all__ = (
    "WAVE8_FOLLOWUP_D_CONTRACT_IDS",
    "WAVE8_FOLLOWUP_D_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_FOLLOWUP_D_ENTITIES",
    "WAVE8_FOLLOWUP_D_FINAL_AUDIT_SIGNATURE",
    "WAVE8_FOLLOWUP_D_FUNNEL_AUDITS",
    "WAVE8_FOLLOWUP_D_HOLDS",
    "WAVE8_FOLLOWUP_D_LOCATION_QUARANTINE_REASONS",
    "WAVE8_FOLLOWUP_D_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_FOLLOWUP_D_RESERVED_IDS",
    "WAVE8_FOLLOWUP_D_SOURCES",
    "install_wave8_followup_d_entities",
    "install_wave8_followup_d_sources",
    "promote_wave8_followup_d_contracts",
    "validate_wave8_followup_d_artifact_state",
    "validate_wave8_followup_d_discovery_dispositions",
    "validate_wave8_followup_d_queue_contracts",
    "wave8_followup_d_audit_signature",
    "wave8_followup_d_counts",
    "wave8_followup_d_metadata",
)


_LANES: tuple[tuple[str, ModuleType, str], ...] = (
    ("swabian_hre", swabian_hre, "WAVE8_SWABIAN_HRE"),
    ("cuban", cuban, "WAVE8_CUBAN"),
    ("lower_canada", lower_canada, "WAVE8_LOWER_CANADA"),
    ("irish_royalists", irish_royalists, "WAVE8_IRISH_ROYALISTS"),
    (
        "finnish_civil_war",
        finnish_civil_war,
        "WAVE8_FINNISH_CIVIL_WAR",
    ),
)


def _constant(module: ModuleType, prefix: str, suffix: str) -> Any:
    name = f"{prefix}_{suffix}"
    if not hasattr(module, name):
        raise ValueError(f"Wave 8 follow-up D lane omitted required {name}")
    return getattr(module, name)


def _merge_maps(*maps: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for mapping in maps:
        overlap = set(merged) & set(mapping)
        if overlap:
            raise ValueError(f"Wave 8 follow-up D map collision: {sorted(overlap)}")
        merged.update({str(key): dict(value) for key, value in mapping.items()})
    return merged


WAVE8_FOLLOWUP_D_CONTRACT_IDS = frozenset().union(
    *(
        _constant(module, prefix, "CONTRACT_IDS")
        for _, module, prefix in _LANES
    )
)
WAVE8_FOLLOWUP_D_RESERVED_IDS = frozenset().union(
    *(
        _constant(module, prefix, "RESERVED_IDS")
        for _, module, prefix in _LANES
    )
)
WAVE8_FOLLOWUP_D_ENTITIES = tuple(
    entity
    for _, module, prefix in _LANES
    for entity in _constant(module, prefix, "ENTITIES")
)
WAVE8_FOLLOWUP_D_SOURCES = tuple(
    source
    for _, module, prefix in _LANES
    for source in _constant(module, prefix, "SOURCES")
)
WAVE8_FOLLOWUP_D_FUNNEL_AUDITS = {
    name: _constant(module, prefix, "FUNNEL_AUDIT")
    for name, module, prefix in _LANES
}
WAVE8_FOLLOWUP_D_HOLDS = _merge_maps(
    *(
        _constant(module, prefix, "HOLDS")
        for _, module, prefix in _LANES
    )
)
WAVE8_FOLLOWUP_D_POINT_QUARANTINE_ADDITIONS = frozenset().union(
    *(
        _constant(module, prefix, "POINT_QUARANTINE_ADDITIONS")
        for _, module, prefix in _LANES
    )
) & WAVE8_FOLLOWUP_D_CONTRACT_IDS
WAVE8_FOLLOWUP_D_COUNTRY_QUARANTINE_ADDITIONS = frozenset().union(
    *(
        _constant(module, prefix, "COUNTRY_QUARANTINE_ADDITIONS")
        for _, module, prefix in _LANES
    )
)
WAVE8_FOLLOWUP_D_LOCATION_QUARANTINE_REASONS = _merge_maps(
    *(
        _constant(module, prefix, "LOCATION_QUARANTINE_REASONS")
        for _, module, prefix in _LANES
    )
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def wave8_followup_d_audit_signature() -> str:
    payload = {
        "contract_ids": sorted(WAVE8_FOLLOWUP_D_CONTRACT_IDS),
        "country_quarantine": sorted(
            WAVE8_FOLLOWUP_D_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entity_ids": sorted(str(item["id"]) for item in WAVE8_FOLLOWUP_D_ENTITIES),
        "holds": WAVE8_FOLLOWUP_D_HOLDS,
        "lane_signatures": {
            name: _constant(module, prefix, "FINAL_AUDIT_SIGNATURE")
            for name, module, prefix in _LANES
        },
        "location_reasons": WAVE8_FOLLOWUP_D_LOCATION_QUARANTINE_REASONS,
        "point_quarantine": sorted(WAVE8_FOLLOWUP_D_POINT_QUARANTINE_ADDITIONS),
        "reserved_ids": sorted(WAVE8_FOLLOWUP_D_RESERVED_IDS),
        "source_ids": sorted(str(item["id"]) for item in WAVE8_FOLLOWUP_D_SOURCES),
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


WAVE8_FOLLOWUP_D_FINAL_AUDIT_SIGNATURE = (
    "e261be61a3340effc1af26b9bc4077c70cd01b273862ffe706a5c9c5647d93c9"
)


def _validate_static() -> None:
    contract_sets = [
        set(_constant(module, prefix, "CONTRACT_IDS"))
        for _, module, prefix in _LANES
    ]
    reserved_sets = [
        set(_constant(module, prefix, "RESERVED_IDS"))
        for _, module, prefix in _LANES
    ]
    if sum(map(len, contract_sets)) != len(WAVE8_FOLLOWUP_D_CONTRACT_IDS):
        raise ValueError("Wave 8 follow-up D promotion inventories overlap")
    if sum(map(len, reserved_sets)) != len(WAVE8_FOLLOWUP_D_RESERVED_IDS):
        raise ValueError("Wave 8 follow-up D reservation inventories overlap")
    if WAVE8_FOLLOWUP_D_CONTRACT_IDS & set(WAVE8_FOLLOWUP_D_HOLDS):
        raise ValueError("Wave 8 follow-up D promotion/hold inventories overlap")
    if WAVE8_FOLLOWUP_D_RESERVED_IDS != (
        WAVE8_FOLLOWUP_D_CONTRACT_IDS | set(WAVE8_FOLLOWUP_D_HOLDS)
    ):
        raise ValueError("Wave 8 follow-up D disposition inventory drift")
    entity_ids = [str(item["id"]) for item in WAVE8_FOLLOWUP_D_ENTITIES]
    source_ids = [str(item["id"]) for item in WAVE8_FOLLOWUP_D_SOURCES]
    if len(entity_ids) != len(set(entity_ids)):
        raise ValueError("Wave 8 follow-up D entity collision")
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("Wave 8 follow-up D source collision")
    if len(WAVE8_FOLLOWUP_D_CONTRACT_IDS) != 20:
        raise ValueError("Wave 8 follow-up D promotion count drift")
    if len(WAVE8_FOLLOWUP_D_HOLDS) != 5:
        raise ValueError("Wave 8 follow-up D hold count drift")
    if WAVE8_FOLLOWUP_D_FINAL_AUDIT_SIGNATURE != "TO_BE_SEALED" and (
        wave8_followup_d_audit_signature()
        != WAVE8_FOLLOWUP_D_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError("Wave 8 follow-up D final audit signature changed")


def validate_wave8_followup_d_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    _validate_static()
    validations: dict[str, dict[str, int]] = {}
    for name, module, _ in _LANES:
        validator_name = f"validate_wave8_{name}_queue_contracts"
        validator = getattr(module, validator_name, None)
        if validator is None:
            raise ValueError(f"Wave 8 follow-up D lane omitted {validator_name}")
        validations[name] = validator(hced_rows)
    return validations


def validate_wave8_followup_d_discovery_dispositions(
    wikidata_battle_rows: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    _validate_static()
    validations: dict[str, dict[str, int]] = {}
    for name, module, _ in _LANES:
        validator = getattr(
            module,
            f"validate_wave8_{name}_discovery_dispositions",
            None,
        )
        if validator is not None:
            validations[name] = validator(wikidata_battle_rows)
    return validations


def install_wave8_followup_d_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    for name, module, _ in _LANES:
        getattr(module, f"install_wave8_{name}_entities")(release_entities)


def install_wave8_followup_d_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    for name, module, _ in _LANES:
        getattr(module, f"install_wave8_{name}_sources")(sources_by_id)


def promote_wave8_followup_d_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    _validate_static()
    existing = list(existing_events)
    promoted: list[dict[str, Any]] = []
    for name, module, _ in _LANES:
        promoter = getattr(module, f"promote_wave8_{name}_contracts")
        lane_events = promoter(hced_rows, release_entities, [*existing, *promoted])
        promoted.extend(lane_events)
    if len(promoted) != len(WAVE8_FOLLOWUP_D_CONTRACT_IDS):
        raise ValueError("Wave 8 follow-up D promotion count drift")
    return promoted


def validate_wave8_followup_d_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    events = list(release_events)
    candidate_counts: dict[str, int] = {}
    for event in events:
        candidate_id = str(event.get("hced_candidate_id", ""))
        if candidate_id in WAVE8_FOLLOWUP_D_RESERVED_IDS:
            candidate_counts[candidate_id] = candidate_counts.get(candidate_id, 0) + 1
    if set(candidate_counts) != WAVE8_FOLLOWUP_D_CONTRACT_IDS:
        raise ValueError("Wave 8 follow-up D artifact dispositions drift")
    if any(count != 1 for count in candidate_counts.values()):
        raise ValueError("Wave 8 follow-up D artifact candidate multiplicity drift")
    entity_ids = {str(item["id"]) for item in release_entities}
    source_ids = {str(item["id"]) for item in release_sources}
    required_entities = {str(item["id"]) for item in WAVE8_FOLLOWUP_D_ENTITIES}
    required_sources = {str(item["id"]) for item in WAVE8_FOLLOWUP_D_SOURCES}
    if not required_entities <= entity_ids:
        raise ValueError("Wave 8 follow-up D artifact entity inventory drift")
    if not required_sources <= source_ids:
        raise ValueError("Wave 8 follow-up D artifact source inventory drift")
    return {
        "entities_present": len(required_entities),
        "events_present": len(candidate_counts),
        "holds_absent": len(WAVE8_FOLLOWUP_D_HOLDS),
        "sources_present": len(required_sources),
    }


def wave8_followup_d_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_FOLLOWUP_D_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "holds": len(WAVE8_FOLLOWUP_D_HOLDS),
        "new_entities": len(WAVE8_FOLLOWUP_D_ENTITIES),
        "new_sources": len(WAVE8_FOLLOWUP_D_SOURCES),
        "newly_rated_events": len(WAVE8_FOLLOWUP_D_CONTRACT_IDS),
        "point_quarantine_additions": len(
            WAVE8_FOLLOWUP_D_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_FOLLOWUP_D_CONTRACT_IDS),
        "reviewed_hced_rows": len(WAVE8_FOLLOWUP_D_RESERVED_IDS),
    }


def wave8_followup_d_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_followup_d_counts(),
        "final_audit_signature": WAVE8_FOLLOWUP_D_FINAL_AUDIT_SIGNATURE,
        "funnel_audits": WAVE8_FOLLOWUP_D_FUNNEL_AUDITS,
        "lanes": {
            name: getattr(module, f"wave8_{name}_metadata")()
            for name, module, _ in _LANES
        },
        "promoted_candidate_ids": sorted(WAVE8_FOLLOWUP_D_CONTRACT_IDS),
        "reserved_candidate_ids": sorted(WAVE8_FOLLOWUP_D_RESERVED_IDS),
    }


if WAVE8_FOLLOWUP_D_FINAL_AUDIT_SIGNATURE != "TO_BE_SEALED":
    _validate_static()
