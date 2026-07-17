"""Candidate-keyed audit of HCED's four unresolved Sind/Sindh battles.

The source label spans two unrelated eras and several different actors.  This
lane therefore does not open ``Sind`` or ``Sindh`` as a generic alias.  It pins
four source rows and three narrow military identities: Raja Dahir's force at
Raor in 712, the Talpur amirs' coalition at Miani, and Mir Sher Muhammad's
remaining Talpur force at Dubba and Shahdadpur in 1843.

All four records contain complete, independently corroborated tactical results.
The exact dates of the medieval narrative are disputed, so Raor retains year
precision.  Unknown is never treated as a draw and no strategic outcome is
inferred from any engagement.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_SINDH_CONTRACT_IDS",
    "WAVE8_SINDH_CONTRACTS",
    "WAVE8_SINDH_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SINDH_ENTITIES",
    "WAVE8_SINDH_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SINDH_FUNNEL_AUDIT",
    "WAVE8_SINDH_HOLD_IDS",
    "WAVE8_SINDH_HOLDS",
    "WAVE8_SINDH_LOCATION_QUARANTINE_REASONS",
    "WAVE8_SINDH_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SINDH_RESERVED_IDS",
    "WAVE8_SINDH_ROW_HASHES",
    "WAVE8_SINDH_SOURCES",
    "install_wave8_sindh_entities",
    "install_wave8_sindh_sources",
    "promote_wave8_sindh_contracts",
    "validate_wave8_sindh_funnel",
    "validate_wave8_sindh_integration_dispositions",
    "validate_wave8_sindh_queue_contracts",
    "wave8_sindh_audit_signature",
    "wave8_sindh_cohort_counts",
    "wave8_sindh_counts",
    "wave8_sindh_metadata",
)


_LANE_NAME = "Wave 8 exact Sind/Sindh actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_sindh"
_EVENT_ID_PREFIX = "hced_wave8_sindh_"
_EXACT_LABELS = frozenset({"sind", "sindh"})
_COHORT = "sind_sindh_exact_labels_712_1843"

_UMAYYAD = "umayyad_caliphate"
_UNITED_KINGDOM = "united_kingdom"
_DAHIR_FORCE = "raja_dahir_sindh_force_raor_712"
_MIANI_COALITION = "talpur_amirs_coalition_miani_1843"
_SHER_MUHAMMAD_FORCE = "mir_sher_muhammad_talpur_resistance_1843"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    evidence_roles: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_SINDH_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_sindh_iranica_chachnama",
        "CAC-NAMA",
        "https://www.iranicaonline.org/articles/cac-nama/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_chachnama",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_sindh_basham_raor",
        "The Wonder That Was India",
        (
            "https://www.mahitoshnm.ac.in/studyMaterial/"
            "133147THE%20WONDER%20THAT%20WAS%20INDIA.pdf"
        ),
        "A. L. Basham / Sidgwick & Jackson",
        "scholarly_monograph",
        "basham_wonder_india",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_sindh_goi_raor",
        "The Battle of Raor",
        "https://ignca.gov.in/Asi_data/75359.pdf",
        "Government of India / IGNCA digitized collection",
        "government_digitized_historical_study",
        "goi_battle_raor_study",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_sindh_lambrick_battles",
        "The Sind Battles, 1843: Hyderabad (Dubba), Pir Ari and Shahdadpur",
        (
            "https://kitaab.sindh.org/"
            "The_Journal_of_the_Sindh_Historical_Society_"
            "%28Vol_6_No_4%29-N_M_Billimoria-1943-CS.pdf"
        ),
        "Journal of the Sindh Historical Society",
        "scholarly_journal_article",
        "lambrick_sind_battles_1943",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_sindh_nam_miani",
        "Scinde Campaign Medal 1843",
        "https://collection.nam.ac.uk/detail.php?acc=1962-09-35-73",
        "National Army Museum, London",
        "official_museum_collection_record",
        "national_army_museum_scinde_medal",
        ["outcome", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_sindh_heritage_miani",
        "Miani War Memorial, Hyderabad",
        "https://heritage.eftsindh.com/districts/hyderabad/miani-war-memorial.php",
        "Endowment Fund Trust for Preservation of the Heritage of Sindh",
        "official_heritage_record",
        "sindh_heritage_miani_memorial",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_sindh_bl_dubba",
        "Military and Naval Personnel: Battle of Dubba correspondence",
        "https://searcharchives.bl.uk/catalog/041-003792252",
        "British Library, India Office Records",
        "primary_archive_catalog_record",
        "british_library_dubba_correspondence",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_sindh_napier_scinde",
        "The Conquest of Scinde",
        "https://www.cambridge.org/core/books/conquest-of-scinde/900CEF0B09612986DC3417A3A0AF1DAD",
        "W. F. P. Napier / Cambridge University Press reissue",
        "contemporary_campaign_narrative",
        "napier_conquest_scinde_1845",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_sindh_talpur_structure",
        "Talpur Mirs: An Introduction",
        "https://talpur.org/royaltalpurs/talpurs-introduction/",
        "The Royal Talpurs and the Heritage of Sindh",
        "dynastic_history_reference",
        "royal_talpurs_structure",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_sindh_sindh_forest_history",
        "History of Sindh",
        "https://sindhforests.gov.pk/page-history-of-sindh",
        "Sindh Forest Department, Government of Sindh",
        "official_historical_synthesis",
        "sindh_government_history",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_SINDH_SOURCES}


# Empty aliases are intentional.  These identities are reachable only through
# the fingerprinted contracts below; neither historical spelling becomes a
# global resolver path.
WAVE8_SINDH_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _DAHIR_FORCE,
        "name": "Raja Dahir's Sindh force at Raor (712)",
        "kind": "event_bounded_royal_army",
        "start_year": 712,
        "end_year": 712,
        "region": "Lower Indus valley, Sindh",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to Raja Dahir's defending force in the pitched battle at "
            "Raor/Rawar in the 712 conquest narrative. The Chach-Nama's exact "
            "calendar chronology is internally disputed, so only HCED's year is "
            "asserted. No Elo is inherited from a generic Sindh identity, the "
            "whole Brahman dynasty, later resistance by Dahir's family, or any "
            "modern state or community."
        ),
        "source_ids": [
            "wave8_sindh_basham_raor",
            "wave8_sindh_goi_raor",
            "wave8_sindh_iranica_chachnama",
        ],
    },
    {
        "id": _MIANI_COALITION,
        "name": "Talpur amirs' coalition at Miani (1843)",
        "kind": "event_bounded_dynastic_coalition",
        "start_year": 1843,
        "end_year": 1843,
        "region": "Miani and Hyderabad, Sindh",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the combined Talpur forces that opposed Charles Napier at "
            "Miani on 17 February 1843. Talpur Sindh comprised multiple branches "
            "and states, and Mir Sher Muhammad's Mirpur Khas force did not reach "
            "this battlefield; the coalition therefore does not share Elo with "
            "his later resistance, Khairpur, a timeless Sindh, or modern Pakistan."
        ),
        "source_ids": [
            "wave8_sindh_heritage_miani",
            "wave8_sindh_lambrick_battles",
            "wave8_sindh_nam_miani",
            "wave8_sindh_sindh_forest_history",
            "wave8_sindh_talpur_structure",
        ],
    },
    {
        "id": _SHER_MUHAMMAD_FORCE,
        "name": "Mir Sher Muhammad's Talpur resistance (1843)",
        "kind": "campaign_bounded_dynastic_force",
        "start_year": 1843,
        "end_year": 1843,
        "region": "Hyderabad, Mirpur Khas, and Shahdadpur, Sindh",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to Mir Sher Muhammad Talpur's surviving field force from "
            "Dubba/Hyderabad on 24 March through its final Shahdadpur action on "
            "14 June 1843. It is not merged with the distinct Miani coalition, "
            "other Talpur branches, a generic Sindh identity, later princely "
            "Khairpur, or modern Pakistan."
        ),
        "source_ids": [
            "wave8_sindh_bl_dubba",
            "wave8_sindh_lambrick_battles",
            "wave8_sindh_napier_scinde",
            "wave8_sindh_sindh_forest_history",
            "wave8_sindh_talpur_structure",
        ],
    },
)


WAVE8_SINDH_ROW_HASHES: dict[str, str] = {
    "hced-Hyderabad, Pakistan1843-1": (
        "8e2482881e3eb4fdbb71a0b8c6f2031dbad9358b184e712473fe9657175bcac2"
    ),
    "hced-Miani1843-1": (
        "1401438f6eb8fbfd31d0f3c1d13cac672de78e7fee35ff2caeea14f40ec4291b"
    ),
    "hced-Raor712-1": (
        "9cbcc9d7d8da72be2138e2fbed4ac105a103b2fe9c44fdf180706b80ba9947a2"
    ),
    "hced-Shahdadpur1843-1": (
        "58e019e8e421ace138e9de826144aca9b636bf609bbfb19d8c01b5ce83371798"
    ),
}

WAVE8_SINDH_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "sind": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "bdb91af86844a890e6256e0a0346bf2ee28aeefb651d0e85cb9a26f6d74502cd"
        ),
        "events_touched": 1,
        "label": "sind",
        "rated_counterpart_entities": 1,
        "sole_blocker_events": 1,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 1,
        "zero_time_valid_candidates": 1,
    },
    "sindh": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "aec463faa2f53cc19140db2efb63dbe8505ffe8bf2e2ab4dcd7979706c2d5281"
        ),
        "events_touched": 3,
        "label": "sindh",
        "rated_counterpart_entities": 2,
        "sole_blocker_events": 3,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 3,
        "zero_time_valid_candidates": 3,
    },
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    granularity: str,
    *,
    date_precision: str = "year",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_sources: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_sources)))
    return {
        "raw_row_sha256": WAVE8_SINDH_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "side_1_entity_ids": list(map(str, side_1_entity_ids)),
        "side_2_entity_ids": list(map(str, side_2_entity_ids)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "imperial_conquest",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_time_bounded_sind_actor",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_SINDH_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Raor712-1": _contract(
        "hced-Raor712-1",
        _canonical(
            "Battle of Raor",
            712,
            "712; exact day withheld because the Chach-Nama chronology conflicts",
            "pitched_battle",
        ),
        [_UMAYYAD],
        [_DAHIR_FORCE],
        {
            "wave8_sindh_basham_raor",
            "wave8_sindh_goi_raor",
            "wave8_sindh_iranica_chachnama",
        },
        {"wave8_sindh_basham_raor", "wave8_sindh_goi_raor"},
        (
            "Independent historical studies preserve the source row's Umayyad "
            "battlefield victory and Raja Dahir's defeat in 712. The exact day "
            "and later stages of the conquest are not folded into this result."
        ),
        confidence=0.94,
    ),
    "hced-Miani1843-1": _contract(
        "hced-Miani1843-1",
        _canonical(
            "Battle of Miani",
            1843,
            "17 February 1843",
            "pitched_battle",
            date_precision="day",
        ),
        [_UNITED_KINGDOM],
        [_MIANI_COALITION],
        {
            "wave8_sindh_heritage_miani",
            "wave8_sindh_lambrick_battles",
            "wave8_sindh_nam_miani",
            "wave8_sindh_talpur_structure",
        },
        {
            "wave8_sindh_heritage_miani",
            "wave8_sindh_lambrick_battles",
            "wave8_sindh_nam_miani",
        },
        (
            "The official museum and Sindh heritage records independently date "
            "the battle to 17 February and corroborate the British tactical "
            "victory over the assembled Talpur amirs' forces."
        ),
        confidence=0.99,
    ),
    "hced-Hyderabad, Pakistan1843-1": _contract(
        "hced-Hyderabad, Pakistan1843-1",
        _canonical(
            "Battle of Dubba",
            1843,
            "24 March 1843",
            "pitched_battle",
            date_precision="day",
        ),
        [_UNITED_KINGDOM],
        [_SHER_MUHAMMAD_FORCE],
        {
            "wave8_sindh_bl_dubba",
            "wave8_sindh_lambrick_battles",
            "wave8_sindh_napier_scinde",
            "wave8_sindh_talpur_structure",
        },
        {
            "wave8_sindh_bl_dubba",
            "wave8_sindh_lambrick_battles",
            "wave8_sindh_napier_scinde",
        },
        (
            "HCED's generic Hyderabad title is canonicalized to Dubba, also "
            "called the Battle of Hyderabad. The India Office record fixes 24 "
            "March; the reviewed accounts preserve the British tactical victory "
            "over Mir Sher Muhammad's force."
        ),
        confidence=0.99,
    ),
    "hced-Shahdadpur1843-1": _contract(
        "hced-Shahdadpur1843-1",
        _canonical(
            "Battle of Shahdadpur",
            1843,
            "night of 13-14 June 1843",
            "night_engagement",
            date_precision="day_range",
        ),
        [_UNITED_KINGDOM],
        [_SHER_MUHAMMAD_FORCE],
        {
            "wave8_sindh_lambrick_battles",
            "wave8_sindh_napier_scinde",
            "wave8_sindh_talpur_structure",
        },
        {"wave8_sindh_lambrick_battles", "wave8_sindh_napier_scinde"},
        (
            "Lambrick's source-critical reconstruction and the contemporary "
            "campaign narrative describe John Jacob's dispersal of Mir Sher "
            "Muhammad's last field force and capture of its guns. Only that "
            "bounded tactical result is rated."
        ),
        confidence=0.97,
    ),
}

WAVE8_SINDH_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_SINDH_CONTRACT_IDS = frozenset(WAVE8_SINDH_CONTRACTS)
WAVE8_SINDH_HOLD_IDS = frozenset(WAVE8_SINDH_HOLDS)
WAVE8_SINDH_RESERVED_IDS = frozenset(
    {*WAVE8_SINDH_CONTRACT_IDS, *WAVE8_SINDH_HOLD_IDS}
)
WAVE8_SINDH_POINT_QUARANTINE_ADDITIONS = WAVE8_SINDH_CONTRACT_IDS
WAVE8_SINDH_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_SINDH_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The modern country is supported, but HCED supplies an unexplained "
            "city or regional point that is not independently verified as the "
            "reviewed battlefield; retain Pakistan and withhold geometry."
        ),
        "evidence_refs": sorted(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_SINDH_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_SINDH_CONTRACTS,
        "entities": WAVE8_SINDH_ENTITIES,
        "funnel": WAVE8_SINDH_FUNNEL_AUDIT,
        "holds": WAVE8_SINDH_HOLDS,
        "location_reasons": WAVE8_SINDH_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_SINDH_ROW_HASHES,
        "sources": WAVE8_SINDH_SOURCES,
    }


def wave8_sindh_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_SINDH_FINAL_AUDIT_SIGNATURE = (
    "1aca1949e53457432c212934415b7c9a0d7ed3525aedd0971636338fa46a03aa"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = {str(entity["id"]) for entity in WAVE8_SINDH_ENTITIES}
    if len(source_ids) != len(WAVE8_SINDH_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if entity_ids != {_DAHIR_FORCE, _MIANI_COALITION, _SHER_MUHAMMAD_FORCE}:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_SINDH_CONTRACT_IDS & WAVE8_SINDH_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_SINDH_RESERVED_IDS != set(WAVE8_SINDH_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_SINDH_POINT_QUARANTINE_ADDITIONS != WAVE8_SINDH_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_SINDH_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_SINDH_LOCATION_QUARANTINE_REASONS) != WAVE8_SINDH_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    expected_windows = {
        _DAHIR_FORCE: (712, 712),
        _MIANI_COALITION: (1843, 1843),
        _SHER_MUHAMMAD_FORCE: (1843, 1843),
    }
    used_sources: set[str] = set()
    for entity in WAVE8_SINDH_ENTITIES:
        entity_id = str(entity["id"])
        if entity["aliases"] or (
            entity["start_year"],
            entity["end_year"],
        ) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} identity boundary or alias drift")
        if normalize_label(entity["name"]) in _EXACT_LABELS:
            raise ValueError(f"{_LANE_NAME} generic Sind label opened")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity evidence order drift")
        used_sources.update(set(map(str, entity["source_ids"])) & source_ids)

    if WAVE8_SINDH_CONTRACT_IDS != set(WAVE8_SINDH_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} promotion inventory drift")
    expected_sides = {
        "hced-Raor712-1": ([_UMAYYAD], [_DAHIR_FORCE]),
        "hced-Miani1843-1": ([_UNITED_KINGDOM], [_MIANI_COALITION]),
        "hced-Hyderabad, Pakistan1843-1": (
            [_UNITED_KINGDOM],
            [_SHER_MUHAMMAD_FORCE],
        ),
        "hced-Shahdadpur1843-1": (
            [_UNITED_KINGDOM],
            [_SHER_MUHAMMAD_FORCE],
        ),
    }
    for candidate_id, contract in WAVE8_SINDH_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or (
                contract["side_1_entity_ids"],
                contract["side_2_entity_ids"],
            )
            != expected_sides[candidate_id]
        ):
            raise ValueError(f"{_LANE_NAME} outcome or actor drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence order drift: {candidate_id}")
        if not set(outcomes) <= set(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_sindh_audit_signature() != WAVE8_SINDH_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_sindh_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) in _EXACT_LABELS
        or normalize_label(row.get("side_2_raw")) in _EXACT_LABELS
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_SINDH_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_SINDH_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("year_low") != row.get("year_high") or row.get("year_best") != row.get(
            "year_low"
        ):
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if (
            row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
        ):
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SINDH_CONTRACTS,
        WAVE8_SINDH_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_sindh_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    labels = {
        str(row.get("label")): row
        for row in funnel.get("labels", [])
        if row.get("label") in _EXACT_LABELS
    }
    if set(labels) != _EXACT_LABELS:
        raise ValueError(f"{_LANE_NAME} expected both funnel labels")
    for label, expected in WAVE8_SINDH_FUNNEL_AUDIT.items():
        row = labels[label]
        checks = {
            "candidate_ids": list(map(str, row.get("candidate_ids", []))),
            "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
            "events_touched": int(row.get("events_touched", -1)),
            "label": str(row.get("label")),
            "rated_counterpart_entities": int(
                row.get("rated_counterpart_entities", -1)
            ),
            "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
            "time_valid_candidate_ids": list(
                map(str, row.get("time_valid_candidate_ids", []))
            ),
            "unresolved_side_attempts": int(
                row.get("unresolved_side_attempts", -1)
            ),
            "zero_time_valid_candidates": int(
                row.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
            ),
        }
        if checks != expected:
            raise ValueError(f"{_LANE_NAME} funnel pin changed for {label}: {checks}")
    return {
        "events_touched": sum(row["events_touched"] for row in WAVE8_SINDH_FUNNEL_AUDIT.values()),
        "sole_blocker_events": sum(
            row["sole_blocker_events"] for row in WAVE8_SINDH_FUNNEL_AUDIT.values()
        ),
        "unresolved_side_attempts": sum(
            row["unresolved_side_attempts"] for row in WAVE8_SINDH_FUNNEL_AUDIT.values()
        ),
        "zero_time_valid_candidates": sum(
            row["zero_time_valid_candidates"] for row in WAVE8_SINDH_FUNNEL_AUDIT.values()
        ),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "batyear"):
        try:
            if row.get(key) is not None:
                return int(row[key])
        except (TypeError, ValueError):
            pass
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


_DUPLICATE_ALIASES: dict[int, set[str]] = {
    712: {"Battle of Raor", "Raor", "Rawar", "Rewar"},
    1843: {
        "Battle of Miani",
        "Miani",
        "Meanee",
        "Meeanee",
        "Battle of Dubba",
        "Battle of Hyderabad",
        "Dubba",
        "Dubbo",
        "Hyderabad, Pakistan",
        "Battle of Shahdadpur",
        "Shahdadpur",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (year, normalize_label(alias))
    for year, aliases in _DUPLICATE_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_sindh_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_sindh_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_SINDH_RESERVED_IDS
        and _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_SINDH_CONTRACT_IDS
        and _is_probable_twin(event)
    )
    if hced_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"iwbd={iwbd_twins}, release={release_twins}"
        )
    return {
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_sindh_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SINDH_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_sindh_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SINDH_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SINDH_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SINDH_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_sindh_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_sindh_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SINDH_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_sindh_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_SINDH_CONTRACTS.values(),
                    *WAVE8_SINDH_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_sindh_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": len(WAVE8_SINDH_HOLDS),
        "new_entities": len(WAVE8_SINDH_ENTITIES),
        "new_sources": len(WAVE8_SINDH_SOURCES),
        "newly_rated_events": len(WAVE8_SINDH_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(WAVE8_SINDH_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_SINDH_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_SINDH_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_sindh_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_sindh_counts(),
        "cohorts": wave8_sindh_cohort_counts(),
        "final_audit_signature": WAVE8_SINDH_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_SINDH_CONTRACT_IDS),
        "hold_candidate_ids": sorted(WAVE8_SINDH_HOLD_IDS),
    }


_validate_static()
