"""Shared fail-closed bundle for the five follow-up E exact HCED lanes.

The lane modules remain authoritative for historical contracts, source
evidence, row fingerprints, holds, terminal exclusions, and discovery
records.  This module combines their disjoint inventories in declared order
and adapts the few intentionally different lane interfaces explicitly.  It
does not create aliases, infer outcomes, or make discovery rows rateable.
"""

from __future__ import annotations

import hashlib
import json
from types import ModuleType
from typing import Any, Iterable, Mapping

from . import wave8_banu_bu_ali_berad as banu_bu_ali_berad
from . import wave8_cordova as cordova
from . import wave8_honduran_rebels as honduran_rebels
from . import wave8_saudi_arabia_exact as saudi_arabia_exact
from . import wave8_somali_rebels as somali_rebels


__all__ = (
    "WAVE8_FOLLOWUP_E_CONTRACT_IDS",
    "WAVE8_FOLLOWUP_E_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_FOLLOWUP_E_DISCOVERY_DISPOSITIONS",
    "WAVE8_FOLLOWUP_E_ENTITIES",
    "WAVE8_FOLLOWUP_E_FINAL_AUDIT_SIGNATURE",
    "WAVE8_FOLLOWUP_E_FUNNEL_AUDITS",
    "WAVE8_FOLLOWUP_E_HOLDS",
    "WAVE8_FOLLOWUP_E_LOCATION_QUARANTINE_REASONS",
    "WAVE8_FOLLOWUP_E_LOCATION_REVIEWS",
    "WAVE8_FOLLOWUP_E_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_FOLLOWUP_E_RESERVED_IDS",
    "WAVE8_FOLLOWUP_E_SOURCES",
    "WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS",
    "install_wave8_followup_e_entities",
    "install_wave8_followup_e_sources",
    "promote_wave8_followup_e_contracts",
    "validate_wave8_followup_e_artifact_state",
    "validate_wave8_followup_e_discovery_dispositions",
    "validate_wave8_followup_e_funnels",
    "validate_wave8_followup_e_integration_dispositions",
    "validate_wave8_followup_e_queue_contracts",
    "wave8_followup_e_audit_signature",
    "wave8_followup_e_counts",
    "wave8_followup_e_metadata",
)


_LANES: tuple[tuple[str, ModuleType, str], ...] = (
    ("cordova", cordova, "WAVE8_CORDOVA"),
    ("honduran_rebels", honduran_rebels, "WAVE8_HONDURAN_REBELS"),
    ("somali_rebels", somali_rebels, "WAVE8_SOMALI_REBELS"),
    (
        "banu_bu_ali_berad",
        banu_bu_ali_berad,
        "WAVE8_BANU_BU_ALI_BERAD",
    ),
    (
        "saudi_arabia_exact",
        saudi_arabia_exact,
        "WAVE8_SAUDI_ARABIA_EXACT",
    ),
)


def _constant(module: ModuleType, prefix: str, suffix: str) -> Any:
    name = f"{prefix}_{suffix}"
    if not hasattr(module, name):
        raise ValueError(f"Wave 8 follow-up E lane omitted required {name}")
    return getattr(module, name)


def _merge_maps(*maps: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for mapping in maps:
        overlap = set(merged) & set(mapping)
        if overlap:
            raise ValueError(f"Wave 8 follow-up E map collision: {sorted(overlap)}")
        merged.update({str(key): dict(value) for key, value in mapping.items()})
    return merged


def _assert_absent(module: ModuleType, prefix: str, suffix: str) -> None:
    name = f"{prefix}_{suffix}"
    if hasattr(module, name):
        raise ValueError(
            f"Wave 8 follow-up E explicit interface changed; review {name}"
        )


WAVE8_FOLLOWUP_E_CONTRACT_IDS = frozenset().union(
    *(
        _constant(module, prefix, "CONTRACT_IDS")
        for _, module, prefix in _LANES
    )
)
WAVE8_FOLLOWUP_E_RESERVED_IDS = frozenset().union(
    *(
        _constant(module, prefix, "RESERVED_IDS")
        for _, module, prefix in _LANES
    )
)
WAVE8_FOLLOWUP_E_ENTITIES = tuple(
    entity
    for _, module, prefix in _LANES
    for entity in _constant(module, prefix, "ENTITIES")
)
WAVE8_FOLLOWUP_E_SOURCES = tuple(
    source
    for _, module, prefix in _LANES
    for source in _constant(module, prefix, "SOURCES")
)
WAVE8_FOLLOWUP_E_HOLDS = _merge_maps(
    *(
        _constant(module, prefix, "HOLDS")
        for _, module, prefix in _LANES
    )
)

# Only Córdoba and Saudi Arabia declare terminal exclusions.  The absence of
# that interface in the other three lanes is intentional and guarded below.
_TERMINAL_EXCLUSIONS_BY_LANE: dict[
    str, Mapping[str, Mapping[str, Any]]
] = {
    "cordova": _constant(cordova, "WAVE8_CORDOVA", "TERMINAL_EXCLUSIONS"),
    "honduran_rebels": {},
    "somali_rebels": {},
    "banu_bu_ali_berad": {},
    "saudi_arabia_exact": _constant(
        saudi_arabia_exact,
        "WAVE8_SAUDI_ARABIA_EXACT",
        "TERMINAL_EXCLUSIONS",
    ),
}
WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS = _merge_maps(
    *(_TERMINAL_EXCLUSIONS_BY_LANE[name] for name, _, _ in _LANES)
)

# Funnel contracts are heterogeneous by design.  Somali exposes one row,
# three lanes expose label maps, and Saudi has no historical funnel pin.
WAVE8_FOLLOWUP_E_FUNNEL_AUDITS: dict[
    str, dict[str, Mapping[str, Any]]
] = {
    "cordova": dict(cordova.WAVE8_CORDOVA_FUNNEL_AUDIT),
    "honduran_rebels": dict(
        honduran_rebels.WAVE8_HONDURAN_REBELS_FUNNEL_AUDITS
    ),
    "somali_rebels": {
        str(somali_rebels.WAVE8_SOMALI_REBELS_FUNNEL_AUDIT["label"]): dict(
            somali_rebels.WAVE8_SOMALI_REBELS_FUNNEL_AUDIT
        )
    },
    "banu_bu_ali_berad": dict(
        banu_bu_ali_berad.WAVE8_BANU_BU_ALI_BERAD_FUNNEL_AUDIT
    ),
}

# Saudi calls this inventory LOCATION_REVIEWS because its terminal exclusion
# has a reviewed non-emission location.  The other lanes expose quarantine
# reasons.  Keep all reviews for audit, then publish only promoted-event
# quarantine reasons.
_LOCATION_REVIEWS_BY_LANE: dict[str, Mapping[str, Mapping[str, Any]]] = {
    "cordova": cordova.WAVE8_CORDOVA_LOCATION_QUARANTINE_REASONS,
    "honduran_rebels": (
        honduran_rebels.WAVE8_HONDURAN_REBELS_LOCATION_QUARANTINE_REASONS
    ),
    "somali_rebels": (
        somali_rebels.WAVE8_SOMALI_REBELS_LOCATION_QUARANTINE_REASONS
    ),
    "banu_bu_ali_berad": (
        banu_bu_ali_berad.WAVE8_BANU_BU_ALI_BERAD_LOCATION_QUARANTINE_REASONS
    ),
    "saudi_arabia_exact": (
        saudi_arabia_exact.WAVE8_SAUDI_ARABIA_EXACT_LOCATION_REVIEWS
    ),
}
WAVE8_FOLLOWUP_E_LOCATION_REVIEWS = _merge_maps(
    *(_LOCATION_REVIEWS_BY_LANE[name] for name, _, _ in _LANES)
)
_REVIEWED_POINT_QUARANTINE_IDS = frozenset().union(
    *(
        _constant(module, prefix, "POINT_QUARANTINE_ADDITIONS")
        for _, module, prefix in _LANES
    )
)
_REVIEWED_COUNTRY_QUARANTINE_IDS = frozenset().union(
    *(
        _constant(module, prefix, "COUNTRY_QUARANTINE_ADDITIONS")
        for _, module, prefix in _LANES
    )
)
WAVE8_FOLLOWUP_E_POINT_QUARANTINE_ADDITIONS = (
    _REVIEWED_POINT_QUARANTINE_IDS & WAVE8_FOLLOWUP_E_CONTRACT_IDS
)
WAVE8_FOLLOWUP_E_COUNTRY_QUARANTINE_ADDITIONS = (
    _REVIEWED_COUNTRY_QUARANTINE_IDS & WAVE8_FOLLOWUP_E_CONTRACT_IDS
)
_PUBLISHED_LOCATION_IDS = (
    WAVE8_FOLLOWUP_E_POINT_QUARANTINE_ADDITIONS
    | WAVE8_FOLLOWUP_E_COUNTRY_QUARANTINE_ADDITIONS
)
WAVE8_FOLLOWUP_E_LOCATION_QUARANTINE_REASONS = {
    candidate_id: dict(WAVE8_FOLLOWUP_E_LOCATION_REVIEWS[candidate_id])
    for candidate_id in sorted(_PUBLISHED_LOCATION_IDS)
}

# Preserve each lane's native discovery/adjacency schema under a lane key.
# Namespacing is deliberate: raw candidate identifiers may overlap datasets.
WAVE8_FOLLOWUP_E_DISCOVERY_DISPOSITIONS: dict[
    str, dict[str, Mapping[str, Any]]
] = {
    "cordova": dict(cordova.WAVE8_CORDOVA_INTEGRATION_DISPOSITIONS),
    "honduran_rebels": dict(
        honduran_rebels.WAVE8_HONDURAN_REBELS_INTEGRATION_DISPOSITIONS
    ),
    "somali_rebels": dict(
        somali_rebels.WAVE8_SOMALI_REBELS_INTEGRATION_DISPOSITIONS
    ),
    "banu_bu_ali_berad": dict(
        banu_bu_ali_berad.WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_DISPOSITIONS
    ),
    "saudi_arabia_exact": dict(
        saudi_arabia_exact.WAVE8_SAUDI_ARABIA_EXACT_INTEGRATION_DISPOSITIONS
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def wave8_followup_e_audit_signature() -> str:
    payload = {
        "contract_ids": sorted(WAVE8_FOLLOWUP_E_CONTRACT_IDS),
        "country_quarantine": sorted(
            WAVE8_FOLLOWUP_E_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_dispositions": WAVE8_FOLLOWUP_E_DISCOVERY_DISPOSITIONS,
        "entity_ids": sorted(str(item["id"]) for item in WAVE8_FOLLOWUP_E_ENTITIES),
        "funnel_audits": WAVE8_FOLLOWUP_E_FUNNEL_AUDITS,
        "holds": WAVE8_FOLLOWUP_E_HOLDS,
        "lane_order": [name for name, _, _ in _LANES],
        "lane_signatures": {
            name: _constant(module, prefix, "FINAL_AUDIT_SIGNATURE")
            for name, module, prefix in _LANES
        },
        "location_reasons": WAVE8_FOLLOWUP_E_LOCATION_QUARANTINE_REASONS,
        "location_reviews": WAVE8_FOLLOWUP_E_LOCATION_REVIEWS,
        "point_quarantine": sorted(
            WAVE8_FOLLOWUP_E_POINT_QUARANTINE_ADDITIONS
        ),
        "reserved_ids": sorted(WAVE8_FOLLOWUP_E_RESERVED_IDS),
        "source_ids": sorted(str(item["id"]) for item in WAVE8_FOLLOWUP_E_SOURCES),
        "terminal_exclusions": WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


WAVE8_FOLLOWUP_E_FINAL_AUDIT_SIGNATURE = (
    "9248d7b4019353e9c108cd0848edb0845bb8732804beec5f665890654274d5ee"
)


def _validate_interfaces() -> None:
    for module, prefix in (
        (honduran_rebels, "WAVE8_HONDURAN_REBELS"),
        (somali_rebels, "WAVE8_SOMALI_REBELS"),
        (banu_bu_ali_berad, "WAVE8_BANU_BU_ALI_BERAD"),
    ):
        _assert_absent(module, prefix, "TERMINAL_EXCLUSIONS")
    for module, prefix in (
        (cordova, "WAVE8_CORDOVA"),
        (honduran_rebels, "WAVE8_HONDURAN_REBELS"),
        (somali_rebels, "WAVE8_SOMALI_REBELS"),
        (banu_bu_ali_berad, "WAVE8_BANU_BU_ALI_BERAD"),
    ):
        _assert_absent(module, prefix, "LOCATION_REVIEWS")
    _assert_absent(
        saudi_arabia_exact,
        "WAVE8_SAUDI_ARABIA_EXACT",
        "LOCATION_QUARANTINE_REASONS",
    )
    for suffix in ("FUNNEL_AUDIT", "FUNNEL_AUDITS"):
        _assert_absent(
            saudi_arabia_exact,
            "WAVE8_SAUDI_ARABIA_EXACT",
            suffix,
        )


def _validate_static() -> None:
    _validate_interfaces()
    contract_sets: list[set[str]] = []
    reserved_sets: list[set[str]] = []
    hold_sets: list[set[str]] = []
    exclusion_sets: list[set[str]] = []
    for name, module, prefix in _LANES:
        contracts = set(_constant(module, prefix, "CONTRACT_IDS"))
        reserved = set(_constant(module, prefix, "RESERVED_IDS"))
        holds = set(_constant(module, prefix, "HOLDS"))
        exclusions = set(_TERMINAL_EXCLUSIONS_BY_LANE[name])
        dispositions = (contracts, holds, exclusions)
        if any(
            dispositions[left] & dispositions[right]
            for left in range(len(dispositions))
            for right in range(left + 1, len(dispositions))
        ):
            raise ValueError(f"Wave 8 follow-up E {name} dispositions overlap")
        if reserved != contracts | holds | exclusions:
            raise ValueError(f"Wave 8 follow-up E {name} reservation drift")
        signature = getattr(module, f"wave8_{name}_audit_signature")()
        if signature != _constant(module, prefix, "FINAL_AUDIT_SIGNATURE"):
            raise ValueError(f"Wave 8 follow-up E {name} lane signature drift")
        contract_sets.append(contracts)
        reserved_sets.append(reserved)
        hold_sets.append(holds)
        exclusion_sets.append(exclusions)

    for label, inventories, combined in (
        ("promotion", contract_sets, WAVE8_FOLLOWUP_E_CONTRACT_IDS),
        ("reservation", reserved_sets, WAVE8_FOLLOWUP_E_RESERVED_IDS),
        ("hold", hold_sets, WAVE8_FOLLOWUP_E_HOLDS),
        (
            "terminal exclusion",
            exclusion_sets,
            WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS,
        ),
    ):
        if sum(map(len, inventories)) != len(combined):
            raise ValueError(f"Wave 8 follow-up E {label} inventories overlap")

    if WAVE8_FOLLOWUP_E_RESERVED_IDS != (
        WAVE8_FOLLOWUP_E_CONTRACT_IDS
        | set(WAVE8_FOLLOWUP_E_HOLDS)
        | set(WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS)
    ):
        raise ValueError("Wave 8 follow-up E disposition inventory drift")

    for candidate_id, hold in WAVE8_FOLLOWUP_E_HOLDS.items():
        if (
            hold.get("disposition") != "hold"
            or hold.get("result_type") != "unknown"
            or hold.get("unknown_is_never_draw") is not True
            or hold.get("terminal_exclusion") is True
        ):
            raise ValueError(f"Wave 8 follow-up E hold guard drift: {candidate_id}")
    forbidden_result_keys = {
        "winner_side",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "result_type",
    }
    for candidate_id, exclusion in WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS.items():
        if (
            exclusion.get("disposition") != "terminal_exclusion"
            or exclusion.get("terminal_exclusion") is not True
            or exclusion.get("unknown_is_never_draw") is not True
            or forbidden_result_keys & set(exclusion)
        ):
            raise ValueError(
                f"Wave 8 follow-up E terminal exclusion drift: {candidate_id}"
            )

    entity_ids = [str(item["id"]) for item in WAVE8_FOLLOWUP_E_ENTITIES]
    source_ids = [str(item["id"]) for item in WAVE8_FOLLOWUP_E_SOURCES]
    if len(entity_ids) != len(set(entity_ids)):
        raise ValueError("Wave 8 follow-up E entity collision")
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("Wave 8 follow-up E source collision")

    if not (
        _REVIEWED_POINT_QUARANTINE_IDS
        | _REVIEWED_COUNTRY_QUARANTINE_IDS
    ) <= set(WAVE8_FOLLOWUP_E_LOCATION_REVIEWS):
        raise ValueError("Wave 8 follow-up E location review coverage drift")
    if set(WAVE8_FOLLOWUP_E_LOCATION_REVIEWS) - WAVE8_FOLLOWUP_E_RESERVED_IDS:
        raise ValueError("Wave 8 follow-up E location review escaped reservations")
    if set(WAVE8_FOLLOWUP_E_LOCATION_QUARANTINE_REASONS) != (
        _PUBLISHED_LOCATION_IDS
    ):
        raise ValueError("Wave 8 follow-up E published location reasons drift")
    if _REVIEWED_POINT_QUARANTINE_IDS - WAVE8_FOLLOWUP_E_CONTRACT_IDS != {
        "hced-Dul Madoba1913-1"
    }:
        raise ValueError("Wave 8 follow-up E nonpublished point review drift")
    if _REVIEWED_COUNTRY_QUARANTINE_IDS:
        raise ValueError("Wave 8 follow-up E acquired a country quarantine")

    funnel_labels = [
        label
        for audits in WAVE8_FOLLOWUP_E_FUNNEL_AUDITS.values()
        for label in audits
    ]
    if len(funnel_labels) != len(set(funnel_labels)):
        raise ValueError("Wave 8 follow-up E funnel-label collision")
    if set(WAVE8_FOLLOWUP_E_FUNNEL_AUDITS) != {
        "cordova",
        "honduran_rebels",
        "somali_rebels",
        "banu_bu_ali_berad",
    }:
        raise ValueError("Wave 8 follow-up E funnel interface drift")

    if (
        len(WAVE8_FOLLOWUP_E_CONTRACT_IDS),
        len(WAVE8_FOLLOWUP_E_RESERVED_IDS),
        len(WAVE8_FOLLOWUP_E_HOLDS),
        len(WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS),
        len(WAVE8_FOLLOWUP_E_ENTITIES),
        len(WAVE8_FOLLOWUP_E_SOURCES),
        len(WAVE8_FOLLOWUP_E_POINT_QUARANTINE_ADDITIONS),
        len(WAVE8_FOLLOWUP_E_COUNTRY_QUARANTINE_ADDITIONS),
    ) != (13, 19, 3, 3, 27, 47, 11, 0):
        raise ValueError("Wave 8 follow-up E verified aggregate counts drift")

    if WAVE8_FOLLOWUP_E_FINAL_AUDIT_SIGNATURE != "TO_BE_SEALED" and (
        wave8_followup_e_audit_signature()
        != WAVE8_FOLLOWUP_E_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError("Wave 8 follow-up E final audit signature changed")


def validate_wave8_followup_e_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    _validate_static()
    validations: dict[str, dict[str, int]] = {}
    for name, module, prefix in _LANES:
        validator = getattr(module, f"validate_wave8_{name}_queue_contracts")
        result = validator(hced_rows)
        expected = {
            "holds": len(_constant(module, prefix, "HOLDS")),
            "promotion_contracts": len(_constant(module, prefix, "CONTRACT_IDS")),
            "reviewed_hced_rows": len(_constant(module, prefix, "RESERVED_IDS")),
            "terminal_exclusions": len(_TERMINAL_EXCLUSIONS_BY_LANE[name]),
        }
        actual = {
            "holds": int(result.get("holds", 0)),
            "promotion_contracts": int(result.get("promotion_contracts", -1)),
            "reviewed_hced_rows": int(result.get("reviewed_hced_rows", -1)),
            "terminal_exclusions": int(result.get("terminal_exclusions", 0)),
        }
        if actual != expected:
            raise ValueError(f"Wave 8 follow-up E {name} queue count drift")
        validations[name] = result
    return validations


def validate_wave8_followup_e_funnels(
    funnel: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the four declared historical funnel interfaces.

    Saudi Arabia deliberately has no funnel constant, so adding one requires
    an explicit bundle review instead of being picked up silently.
    """

    _validate_static()
    return {
        "cordova": cordova.validate_wave8_cordova_funnel(funnel),
        "honduran_rebels": (
            honduran_rebels.validate_wave8_honduran_rebels_funnel(funnel)
        ),
        "somali_rebels": somali_rebels.validate_wave8_somali_rebels_funnel(
            funnel
        ),
        "banu_bu_ali_berad": (
            banu_bu_ali_berad.validate_wave8_banu_bu_ali_berad_funnel(funnel)
        ),
    }


def validate_wave8_followup_e_discovery_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    brecke_rows: list[dict[str, Any]],
    wikidata_rows: list[dict[str, Any]],
    ucdp_rows: Iterable[Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    """Route each lane's exact discovery inputs without auto-promotion."""

    _validate_static()
    ucdp = [dict(row) for row in ucdp_rows]
    validations = {
        "cordova": cordova.validate_wave8_cordova_discovery_dispositions(
            wikidata_rows
        ),
        "honduran_rebels": (
            honduran_rebels.validate_wave8_honduran_rebels_discovery_dispositions(
                hced_rows,
                iwbd_rows,
                brecke_rows,
            )
        ),
        "somali_rebels": (
            somali_rebels.validate_wave8_somali_rebels_discovery_dispositions(
                wikidata_rows,
                ucdp,
            )
        ),
        "banu_bu_ali_berad": (
            banu_bu_ali_berad.validate_wave8_banu_bu_ali_berad_discovery_dispositions(
                wikidata_rows
            )
        ),
        "saudi_arabia_exact": (
            saudi_arabia_exact.validate_wave8_saudi_arabia_exact_discovery_dispositions(
                wikidata_rows,
                iwbd_rows,
            )
        ),
    }
    for name, result in validations.items():
        if int(result.get("discovery_promotions", 0)) != 0 or int(
            result.get("automated_promotions", 0)
        ) != 0:
            raise ValueError(
                f"Wave 8 follow-up E {name} discovery became rating-eligible"
            )
    return validations


def validate_wave8_followup_e_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwd_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    brecke_rows: list[dict[str, Any]],
    wikidata_rows: list[dict[str, Any]],
    ucdp_rows: Iterable[Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    """Validate declared twins, adjacent records, and parent ownership."""

    _validate_static()
    ucdp = [dict(row) for row in ucdp_rows]
    existing = list(existing_events)
    discovery = validate_wave8_followup_e_discovery_dispositions(
        hced_rows,
        iwbd_rows,
        brecke_rows,
        wikidata_rows,
        ucdp,
    )
    return {
        "cordova": cordova.validate_wave8_cordova_integration_dispositions(
            hced_rows,
            iwbd_rows,
            existing,
        ),
        "honduran_rebels": (
            honduran_rebels.validate_wave8_honduran_rebels_integration_dispositions(
                hced_rows,
                iwd_rows,
                iwbd_rows,
                brecke_rows,
                existing,
            )
        ),
        "somali_rebels": (
            somali_rebels.validate_wave8_somali_rebels_integration_dispositions(
                hced_rows,
                iwd_rows,
                iwbd_rows,
                existing,
                wikidata_rows=wikidata_rows,
                ucdp_rows=ucdp,
            )
        ),
        # This lane intentionally has no broad probable-twin scanner; its
        # fingerprinted discovery validator is its declared integration edge.
        "banu_bu_ali_berad": discovery["banu_bu_ali_berad"],
        "saudi_arabia_exact": (
            saudi_arabia_exact.validate_wave8_saudi_arabia_exact_integration_dispositions(
                hced_rows,
                wikidata_rows,
                iwbd_rows,
                existing,
            )
        ),
    }


def install_wave8_followup_e_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    for name, module, _ in _LANES:
        getattr(module, f"install_wave8_{name}_entities")(release_entities)


def install_wave8_followup_e_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    for name, module, _ in _LANES:
        getattr(module, f"install_wave8_{name}_sources")(sources_by_id)


def promote_wave8_followup_e_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    _validate_static()
    existing = list(existing_events)
    promoted: list[dict[str, Any]] = []
    for name, module, prefix in _LANES:
        promoter = getattr(module, f"promote_wave8_{name}_contracts")
        lane_events = promoter(hced_rows, release_entities, [*existing, *promoted])
        lane_candidate_ids = {
            str(event.get("hced_candidate_id")) for event in lane_events
        }
        expected_ids = set(_constant(module, prefix, "CONTRACT_IDS"))
        if lane_candidate_ids != expected_ids or len(lane_events) != len(expected_ids):
            raise ValueError(f"Wave 8 follow-up E {name} promotion drift")
        promoted.extend(lane_events)

    candidate_ids = [str(event.get("hced_candidate_id")) for event in promoted]
    event_ids = [str(event.get("id")) for event in promoted]
    if (
        set(candidate_ids) != WAVE8_FOLLOWUP_E_CONTRACT_IDS
        or len(candidate_ids) != len(set(candidate_ids))
        or len(event_ids) != len(set(event_ids))
    ):
        raise ValueError("Wave 8 follow-up E aggregate promotion drift")
    return promoted


def validate_wave8_followup_e_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Accept an absent or fully integrated bundle and reject partial state."""

    _validate_static()
    events = list(release_events)
    entity_by_id = {str(item["id"]): item for item in release_entities}
    source_by_id = {str(item["id"]): item for item in release_sources}

    candidate_counts: dict[str, int] = {}
    for event in events:
        candidate_id = str(event.get("hced_candidate_id", ""))
        if candidate_id in WAVE8_FOLLOWUP_E_RESERVED_IDS:
            candidate_counts[candidate_id] = candidate_counts.get(candidate_id, 0) + 1
    forbidden = set(candidate_counts) & (
        set(WAVE8_FOLLOWUP_E_HOLDS)
        | set(WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS)
    )
    if forbidden:
        raise ValueError(
            "Wave 8 follow-up E nonrating disposition entered release: "
            f"{sorted(forbidden)}"
        )
    present_contracts = set(candidate_counts)
    if present_contracts not in (set(), set(WAVE8_FOLLOWUP_E_CONTRACT_IDS)):
        raise ValueError("Wave 8 follow-up E artifact event state is partial")
    if any(count != 1 for count in candidate_counts.values()):
        raise ValueError("Wave 8 follow-up E artifact candidate multiplicity drift")

    expected_entities = {
        str(item["id"]): item for item in WAVE8_FOLLOWUP_E_ENTITIES
    }
    expected_sources = {
        str(item["id"]): item for item in WAVE8_FOLLOWUP_E_SOURCES
    }
    present_entities = set(expected_entities) & set(entity_by_id)
    present_sources = set(expected_sources) & set(source_by_id)
    if present_entities not in (set(), set(expected_entities)):
        raise ValueError("Wave 8 follow-up E artifact entity state is partial")
    if present_sources not in (set(), set(expected_sources)):
        raise ValueError("Wave 8 follow-up E artifact source state is partial")
    for entity_id in present_entities:
        if dict(entity_by_id[entity_id]) != dict(expected_entities[entity_id]):
            raise ValueError(
                f"Wave 8 follow-up E artifact entity drift: {entity_id}"
            )
    for source_id in present_sources:
        if dict(source_by_id[source_id]) != dict(expected_sources[source_id]):
            raise ValueError(
                f"Wave 8 follow-up E artifact source drift: {source_id}"
            )

    integrated = bool(present_contracts)
    component_states = (
        integrated,
        bool(present_entities),
        bool(present_sources),
    )
    if len(set(component_states)) != 1:
        raise ValueError("Wave 8 follow-up E artifact components disagree")
    return {
        "artifact_state": "integrated" if integrated else "absent",
        "entities_present": len(present_entities),
        "events_present": len(present_contracts),
        "holds_absent": len(WAVE8_FOLLOWUP_E_HOLDS),
        "sources_present": len(present_sources),
        "terminal_exclusions_absent": len(
            WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS
        ),
    }


def wave8_followup_e_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_FOLLOWUP_E_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_nonrating_dispositions": sum(
            len(items) for items in WAVE8_FOLLOWUP_E_DISCOVERY_DISPOSITIONS.values()
        ),
        "holds": len(WAVE8_FOLLOWUP_E_HOLDS),
        "location_reviews": len(WAVE8_FOLLOWUP_E_LOCATION_REVIEWS),
        "new_entities": len(WAVE8_FOLLOWUP_E_ENTITIES),
        "new_sources": len(WAVE8_FOLLOWUP_E_SOURCES),
        "newly_rated_events": len(WAVE8_FOLLOWUP_E_CONTRACT_IDS),
        "point_quarantine_additions": len(
            WAVE8_FOLLOWUP_E_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_FOLLOWUP_E_CONTRACT_IDS),
        "reviewed_hced_rows": len(WAVE8_FOLLOWUP_E_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS),
    }


def wave8_followup_e_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_followup_e_counts(),
        "final_audit_signature": WAVE8_FOLLOWUP_E_FINAL_AUDIT_SIGNATURE,
        "funnel_audits": WAVE8_FOLLOWUP_E_FUNNEL_AUDITS,
        "hold_candidate_ids": sorted(WAVE8_FOLLOWUP_E_HOLDS),
        "lanes": {
            name: getattr(module, f"wave8_{name}_metadata")()
            for name, module, _ in _LANES
        },
        "location_review_candidate_ids": sorted(
            WAVE8_FOLLOWUP_E_LOCATION_REVIEWS
        ),
        "promoted_candidate_ids": sorted(WAVE8_FOLLOWUP_E_CONTRACT_IDS),
        "reserved_candidate_ids": sorted(WAVE8_FOLLOWUP_E_RESERVED_IDS),
        "terminal_exclusion_candidate_ids": sorted(
            WAVE8_FOLLOWUP_E_TERMINAL_EXCLUSIONS
        ),
    }


if WAVE8_FOLLOWUP_E_FINAL_AUDIT_SIGNATURE != "TO_BE_SEALED":
    _validate_static()
