"""Candidate-keyed audit of HCED's remaining Bannock-labelled rows.

The five locked rows span two conflicts and cannot share a generic Bannock
identity.  Birch Creek promotes as a United States tactical victory over the
joined 1878 Bannock and Northern Paiute resistance forces.  Vinegar Hill
promotes as a conflict-bounded Tukudeka/Sheepeater victory over Catley's
United States column in 1879.  Both results have two independent source
families and open no generic label-resolution path.

South Mountain/Battle Creek is held because the source winner conflicts with
the reviewed accounts.  Silver Creek is held because attack, rally, pursuit,
and reinforcement evidence does not yield one unambiguous tactical winner.
Pendleton/Miles's Fight is held because contemporary and modern accounts
conflict over the Umatilla role and the opposing coalition.  Unknown is never
converted into a draw.
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
    "WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS",
    "WAVE8_BANNOCK_SHEEPEATER_CONTRACTS",
    "WAVE8_BANNOCK_SHEEPEATER_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_BANNOCK_SHEEPEATER_ENTITIES",
    "WAVE8_BANNOCK_SHEEPEATER_EXPECTED_CANDIDATE_IDS",
    "WAVE8_BANNOCK_SHEEPEATER_FINAL_AUDIT_SIGNATURE",
    "WAVE8_BANNOCK_SHEEPEATER_FUNNEL_AUDIT",
    "WAVE8_BANNOCK_SHEEPEATER_HOLD_IDS",
    "WAVE8_BANNOCK_SHEEPEATER_HOLDS",
    "WAVE8_BANNOCK_SHEEPEATER_LOCATION_QUARANTINE_REASONS",
    "WAVE8_BANNOCK_SHEEPEATER_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_BANNOCK_SHEEPEATER_RESERVED_IDS",
    "WAVE8_BANNOCK_SHEEPEATER_ROW_HASHES",
    "WAVE8_BANNOCK_SHEEPEATER_SOURCES",
    "install_wave8_bannock_sheepeater_entities",
    "install_wave8_bannock_sheepeater_sources",
    "promote_wave8_bannock_sheepeater_contracts",
    "validate_wave8_bannock_sheepeater_funnel",
    "validate_wave8_bannock_sheepeater_integration_dispositions",
    "validate_wave8_bannock_sheepeater_queue_contracts",
    "wave8_bannock_sheepeater_audit_signature",
    "wave8_bannock_sheepeater_cohort_counts",
    "wave8_bannock_sheepeater_counts",
    "wave8_bannock_sheepeater_location_quarantine_additions",
    "wave8_bannock_sheepeater_metadata",
)


_LANE_NAME = "Wave 8 Bannock and Sheepeater exact-force audit"
_MODULE_OWNER = "military_elo.promotion.wave8_bannock_sheepeater"
_EVENT_ID_PREFIX = "hced_wave8_bannock_sheepeater_"

_UNITED_STATES = "united_states"
_BANNOCK_1878 = "bannock_resistance_force_1878"
_NORTHERN_PAIUTE_1878 = "northern_paiute_resistance_force_1878"
_TUKUDEKA_VINEGAR_1879 = "tukudeka_sheepeater_defenders_vinegar_hill_1879"

_RELEVANT_LABELS = frozenset(
    {
        "bannock indians",
        "bannock indians peyoute indians",
        "bannock indians shoshoni indians",
    }
)


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
        "accessed": "2026-07-17",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_BANNOCK_SHEEPEATER_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_bannock_wa_guard_official_history",
        (
            "The Official History of the Washington National Guard, Volume 4: "
            "Washington Territorial Militia in the Bannock Indian War of 1878"
        ),
        "https://mil.wa.gov/asset/5ba41fe2e4c77",
        "Washington Military Department",
        "official_history_with_transcribed_field_telegrams",
        "washington_guard_bannock_war_official_history",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_bannock_ebsco_history",
        "Bannock War",
        "https://www.ebsco.com/research-starters/history/bannock-war",
        "EBSCO Research Starters",
        "scholarly_reference_entry",
        "ebsco_bannock_war_history",
        [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    ),
    _source(
        "wave8_bannock_nps_john_day",
        "The Peoples of John Day: An Ethnographic and Ethnohistoric Overview",
        "https://irma.nps.gov/DataStore/DownloadFile/707094",
        "U.S. National Park Service and Portland State University",
        "federal_ethnographic_and_ethnohistoric_study",
        "deur_bloom_wynia_brown_john_day_2023",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_bannock_idaho_state_history",
        "Bannock War at Camas Prairie",
        (
            "https://history.idaho.gov/wp-content/uploads/"
            "0474_Bannock-War-at-Camas-Prairie.pdf"
        ),
        "Idaho State Historical Society",
        "state_historical_reference_series",
        "idaho_historical_reference_474_bannock_war",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_bannock_nps_miles_fight",
        "Preserving Miles's Fight of the 1878 Bannock War",
        (
            "https://home.nps.gov/articles/000/"
            "preserving-mile-s-fight-of-the-1878-bannock-war.htm"
        ),
        "U.S. National Park Service",
        "official_battlefield_public_history",
        "nps_miles_fight_bannock_war",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_bannock_columbus_dispatch_miles",
        "Dispatch on Miles's Pendleton fight, 16 July 1878",
        (
            "https://gahistoricnewspapers.galileo.usg.edu/lccn/sn89053815/"
            "1878-07-16/ed-1/seq-1/ocr/"
        ),
        "Columbus Daily Enquirer-Sun / Digital Library of Georgia",
        "contemporary_newspaper_dispatch",
        "columbus_enquirer_sun_1878_miles_dispatch",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_sheepeater_usfs_campaign_report",
        "The Sheepeater Campaign: an archaeological and historical assessment",
        (
            "https://objects.lib.uidaho.edu/taylorarchive/"
            "b08-PayetteNationalForestLiterature79.pdf"
        ),
        "USDA Forest Service / University of Idaho Library",
        "federal_cultural_resource_history_report",
        "usfs_sheepeater_campaign_assessment",
        [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    ),
    _source(
        "wave8_sheepeater_muhlenberg_account",
        "Sheepeater Indian Campaign: Vinegar Hill participant account",
        "https://objects.lib.uidaho.edu/twrs/Parker__1968_Indian_Wars.pdf",
        "University of Idaho Library Digital Initiatives",
        "edited_participant_account_compilation",
        "muhlenberg_shearer_vinegar_hill_account",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_sheepeater_nps_ethnohistory",
        "An Ethnohistorical Overview of Groups with Ties to Fort Vancouver",
        (
            "https://www.nps.gov/fova/learn/historyculture/upload/"
            "Ethnohistorical-Overview-by-Deur-Accessible-PDF.pdf"
        ),
        "U.S. National Park Service",
        "federal_ethnohistorical_study",
        "deur_fort_vancouver_ethnohistory",
        ["identity_boundary_or_context_reference"],
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_BANNOCK_SHEEPEATER_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    year: int,
    kind: str,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No generic Bannock, Paiute, Shoshone, Sheepeater, reservation, "
            "or modern tribal-government alias resolves to this identity. It "
            "inherits no Elo from another conflict, band, people, or successor."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_BANNOCK_SHEEPEATER_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _BANNOCK_1878,
        "Bannock resistance force in the Bannock War (1878)",
        1878,
        "conflict_bounded_indigenous_force",
        "Idaho and eastern Oregon",
        {
            "wave8_bannock_ebsco_history",
            "wave8_bannock_nps_john_day",
            "wave8_bannock_wa_guard_official_history",
        },
        (
            "Bounded to the Bannock fighters who left Fort Hall and joined the "
            "Northern Paiute campaign in eastern Oregon during 1878."
        ),
    ),
    _entity(
        _NORTHERN_PAIUTE_1878,
        "Northern Paiute resistance force in the Bannock War (1878)",
        1878,
        "conflict_bounded_indigenous_force",
        "Malheur Reservation and eastern Oregon",
        {
            "wave8_bannock_ebsco_history",
            "wave8_bannock_nps_john_day",
            "wave8_bannock_wa_guard_official_history",
        },
        (
            "Bounded to the minority of Northern Paiute fighters led by Egan and "
            "Oytes who joined the 1878 Bannock campaign; it excludes Northern "
            "Paiute people who did not participate."
        ),
    ),
    _entity(
        _TUKUDEKA_VINEGAR_1879,
        "Tukudeka/Sheepeater defenders at Vinegar Hill (1879)",
        1879,
        "engagement_bounded_indigenous_force",
        "Big Creek and the Middle Fork Salmon River, central Idaho",
        {
            "wave8_sheepeater_muhlenberg_account",
            "wave8_sheepeater_nps_ethnohistory",
            "wave8_sheepeater_usfs_campaign_report",
        },
        (
            "Bounded to the small Tukudeka/Sheepeater defending force that "
            "opposed Lieutenant Henry Catley's column around Big Creek and "
            "Vinegar Hill in July 1879."
        ),
    ),
)


WAVE8_BANNOCK_SHEEPEATER_ROW_HASHES: dict[str, str] = {
    "hced-Battle Creek, Idaho1878-1": (
        "e33005c170ca723cbe411d8145e3c293558d244dc0b6cd74eec7fffb2cae2544"
    ),
    "hced-Birch Creek1878-1": (
        "598afb357ce67c44e48a2827c1b79de59c6257bd1592a8697d68859fd1b74f95"
    ),
    "hced-Pendleton1878-1": (
        "071a2d7e63931dd3b4b9e685b3b333b31b03bd6a987d820d864e8adb0c99cc69"
    ),
    "hced-Silver Creek, Oregon1878-1": (
        "8b2a7040bd3b5a2b276e5be9a006f5a23afeeb5462bf8aeb7c2f31b79d35b8c9"
    ),
    "hced-Vinegar Hill, Idaho1879-1": (
        "cc80ed31c5016492520667f21518fc59053588c412ed2b81f64fb9d675a39855"
    ),
}

WAVE8_BANNOCK_SHEEPEATER_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_BANNOCK_SHEEPEATER_ROW_HASHES
)


WAVE8_BANNOCK_SHEEPEATER_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "bannock indians": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "7aa376c2bda025659e86fc804f92b0807faf0ca45d89ea1782a1ef826ab99236"
        ),
        "events_touched": 3,
        "label": "bannock indians",
        "sole_blocker_events": 3,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 3,
        "zero_time_valid_candidates": 3,
    },
    "bannock indians peyoute indians": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "d40885be9d0669d6e14a58ed6e5d20566e85bcfd8a943f8dbc727b43ece11c61"
        ),
        "events_touched": 1,
        "label": "bannock indians peyoute indians",
        "sole_blocker_events": 1,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 1,
        "zero_time_valid_candidates": 1,
    },
    "bannock indians shoshoni indians": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "e8f919ade19bcc08dbf9da600d850aec25e2143efc2d446076f68ab240e520c1"
        ),
        "events_touched": 1,
        "label": "bannock indians shoshoni indians",
        "sole_blocker_events": 1,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 1,
        "zero_time_valid_candidates": 1,
    },
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "day",
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_BANNOCK_SHEEPEATER_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "bannock_and_sheepeater_exact_force_audit",
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "colonial_anti_colonial",
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
        "actor_override": "candidate_keyed_conflict_bounded_indigenous_forces",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_BANNOCK_SHEEPEATER_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Birch Creek1878-1": _contract(
        "hced-Birch Creek1878-1",
        _canonical(
            "Battle of Birch Creek",
            1878,
            "8 July 1878",
            "single_battle_at_head_of_birch_and_butter_creeks",
        ),
        [_UNITED_STATES],
        [_BANNOCK_1878, _NORTHERN_PAIUTE_1878],
        1,
        {
            "wave8_bannock_ebsco_history",
            "wave8_bannock_nps_john_day",
            "wave8_bannock_wa_guard_official_history",
        },
        {
            "wave8_bannock_ebsco_history",
            "wave8_bannock_wa_guard_official_history",
        },
        (
            "Howard's next-day field telegram reports the United States column "
            "taking successive defended heights, dislodging the force three "
            "times, and pursuing it for miles. EBSCO independently records a "
            "defeat at Birch Creek on 8 July. The NPS study fixes the joined "
            "Bannock and Northern Paiute campaign identity; only the tactical "
            "engagement is rated."
        ),
        0.96,
    ),
    "hced-Vinegar Hill, Idaho1879-1": _contract(
        "hced-Vinegar Hill, Idaho1879-1",
        _canonical(
            "Vinegar Hill action",
            1879,
            "29-31 July 1879",
            "multi_day_big_creek_and_vinegar_hill_engagement",
        ),
        [_TUKUDEKA_VINEGAR_1879],
        [_UNITED_STATES],
        1,
        {
            "wave8_sheepeater_muhlenberg_account",
            "wave8_sheepeater_nps_ethnohistory",
            "wave8_sheepeater_usfs_campaign_report",
        },
        {
            "wave8_sheepeater_muhlenberg_account",
            "wave8_sheepeater_usfs_campaign_report",
        },
        (
            "The participant-account compilation and independent Forest Service "
            "historical assessment describe Catley's command being checked at "
            "Big Creek, trapped at Vinegar Hill, and retreating after abandoning "
            "supplies. The NPS ethnography bounds the opposing actor to the 1879 "
            "Tukudeka/Sheepeater band. No broader Bannock or Shoshone identity or "
            "campaign termination is inferred."
        ),
        0.93,
    ),
}


def _hold(
    candidate_id: str,
    category: str,
    evidence_refs: Iterable[str],
    reason: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_BANNOCK_SHEEPEATER_ROW_HASHES[candidate_id],
        "cohort": "bannock_and_sheepeater_exact_force_audit",
        "disposition": "hold",
        "hold_category": category,
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "hold_reason": reason,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "review_hold_owner",
        },
    }


WAVE8_BANNOCK_SHEEPEATER_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Battle Creek, Idaho1878-1": _hold(
        "hced-Battle Creek, Idaho1878-1",
        "source_outcome_contradiction",
        {
            "wave8_bannock_ebsco_history",
            "wave8_bannock_idaho_state_history",
        },
        (
            "The row is the 8 June South Mountain action near Silver City. The "
            "Idaho history records deaths on both sides without a tactical winner, "
            "while EBSCO describes Buffalo Horn's unit as defeated by volunteers. "
            "Neither supports HCED's categorical Bannock victory, so the result "
            "remains unknown rather than reversed or drawn."
        ),
    ),
    "hced-Silver Creek, Oregon1878-1": _hold(
        "hced-Silver Creek, Oregon1878-1",
        "tactical_outcome_not_uniquely_defensible",
        {
            "wave8_bannock_idaho_state_history",
            "wave8_bannock_nps_john_day",
            "wave8_bannock_wa_guard_official_history",
        },
        (
            "The initial field report records a surprise and charge, but also an "
            "enemy rally and Bernard's request for reinforcements. A later Idaho "
            "summary calls Silver Creek a defeat, while the NPS chronology only "
            "records the force moving on. The available evidence does not support "
            "one bounded tactical winner with the required confidence."
        ),
    ),
    "hced-Pendleton1878-1": _hold(
        "hced-Pendleton1878-1",
        "coalition_identity_conflict",
        {
            "wave8_bannock_columbus_dispatch_miles",
            "wave8_bannock_nps_miles_fight",
            "wave8_bannock_wa_guard_official_history",
        },
        (
            "Miles's field result is defensible, but the participant contract is "
            "not: the modern NPS account places Umatilla fighters with the United "
            "States and labels the opposition Shoshone-Bannock, while a "
            "contemporary dispatch says the Umatillas remained spectators and "
            "HCED lists Bannock-Paiute. The row stays staged until that coalition "
            "conflict is resolved."
        ),
    ),
}


WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS = frozenset(
    WAVE8_BANNOCK_SHEEPEATER_CONTRACTS
)
WAVE8_BANNOCK_SHEEPEATER_HOLD_IDS = frozenset(
    WAVE8_BANNOCK_SHEEPEATER_HOLDS
)
WAVE8_BANNOCK_SHEEPEATER_RESERVED_IDS = frozenset(
    {
        *WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS,
        *WAVE8_BANNOCK_SHEEPEATER_HOLD_IDS,
    }
)
WAVE8_BANNOCK_SHEEPEATER_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS
)
WAVE8_BANNOCK_SHEEPEATER_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = (
    frozenset()
)
WAVE8_BANNOCK_SHEEPEATER_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    "hced-Birch Creek1878-1": {
        "actions": ["withhold_point"],
        "reason": (
            "HCED's coordinate is in Idaho, while the reviewed sources place the "
            "battle near the heads of Birch and Butter Creeks south of Pilot "
            "Rock, Oregon. Retain the United States country assertion and "
            "withhold the mismatched point."
        ),
        "evidence_refs": [
            "wave8_bannock_nps_john_day",
            "wave8_bannock_wa_guard_official_history",
        ],
    },
    "hced-Vinegar Hill, Idaho1879-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources identify the Big Creek/Vinegar Hill setting "
            "but do not independently verify HCED's exact coordinate. Retain the "
            "United States country assertion and withhold the point."
        ),
        "evidence_refs": [
            "wave8_sheepeater_muhlenberg_account",
            "wave8_sheepeater_usfs_campaign_report",
        ],
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_BANNOCK_SHEEPEATER_CONTRACTS,
        "entities": WAVE8_BANNOCK_SHEEPEATER_ENTITIES,
        "funnel": WAVE8_BANNOCK_SHEEPEATER_FUNNEL_AUDIT,
        "holds": WAVE8_BANNOCK_SHEEPEATER_HOLDS,
        "location_reasons": WAVE8_BANNOCK_SHEEPEATER_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_BANNOCK_SHEEPEATER_ROW_HASHES,
        "sources": WAVE8_BANNOCK_SHEEPEATER_SOURCES,
    }


def wave8_bannock_sheepeater_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_BANNOCK_SHEEPEATER_FINAL_AUDIT_SIGNATURE = (
    "ca71631f9a2c01edd2dee39cee2cacd8b15748c240291473d693d0d1f38e5f93"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_by_id = {
        str(entity["id"]): entity
        for entity in WAVE8_BANNOCK_SHEEPEATER_ENTITIES
    }
    if len(source_ids) != len(WAVE8_BANNOCK_SHEEPEATER_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if len(entity_by_id) != len(WAVE8_BANNOCK_SHEEPEATER_ENTITIES):
        raise ValueError(f"{_LANE_NAME} duplicate entity id")
    if WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS & WAVE8_BANNOCK_SHEEPEATER_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_BANNOCK_SHEEPEATER_RESERVED_IDS != set(
        WAVE8_BANNOCK_SHEEPEATER_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_BANNOCK_SHEEPEATER_RESERVED_IDS != (
        WAVE8_BANNOCK_SHEEPEATER_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} candidate inventory drift")
    if (
        WAVE8_BANNOCK_SHEEPEATER_POINT_QUARANTINE_ADDITIONS
        != WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS
        or WAVE8_BANNOCK_SHEEPEATER_COUNTRY_QUARANTINE_ADDITIONS
        or set(WAVE8_BANNOCK_SHEEPEATER_LOCATION_QUARANTINE_REASONS)
        != WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location policy drift")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    expected_windows = {
        _BANNOCK_1878: (1878, 1878),
        _NORTHERN_PAIUTE_1878: (1878, 1878),
        _TUKUDEKA_VINEGAR_1879: (1879, 1879),
    }
    for entity_id, entity in entity_by_id.items():
        if entity.get("aliases") or (
            entity.get("start_year"), entity.get("end_year")
        ) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} entity escaped exact boundary")
        refs = list(map(str, entity.get("source_ids", [])))
        if not refs or not _is_sorted_unique(refs) or not set(refs) <= source_ids:
            raise ValueError(f"{_LANE_NAME} entity evidence drift: {entity_id}")
        used_sources.update(refs)

    expected_sides = {
        "hced-Birch Creek1878-1": (
            [_UNITED_STATES],
            [_BANNOCK_1878, _NORTHERN_PAIUTE_1878],
            1,
        ),
        "hced-Vinegar Hill, Idaho1879-1": (
            [_TUKUDEKA_VINEGAR_1879],
            [_UNITED_STATES],
            1,
        ),
    }
    for candidate_id, contract in WAVE8_BANNOCK_SHEEPEATER_CONTRACTS.items():
        sides = (
            contract["side_1_entity_ids"],
            contract["side_2_entity_ids"],
            contract["winner_side"],
        )
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["war_type"] != "colonial_anti_colonial"
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or sides != expected_sides[candidate_id]
        ):
            raise ValueError(f"{_LANE_NAME} actor/outcome drift: {candidate_id}")
        used_entities.update(
            (
                set(contract["side_1_entity_ids"])
                | set(contract["side_2_entity_ids"])
            )
            - {_UNITED_STATES}
        )
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence) <= source_ids
        ):
            raise ValueError(f"{_LANE_NAME} contract evidence drift: {candidate_id}")
        families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)

    expected_hold_categories = {
        "hced-Battle Creek, Idaho1878-1": "source_outcome_contradiction",
        "hced-Pendleton1878-1": "coalition_identity_conflict",
        "hced-Silver Creek, Oregon1878-1": (
            "tactical_outcome_not_uniquely_defensible"
        ),
    }
    for candidate_id, hold in WAVE8_BANNOCK_SHEEPEATER_HOLDS.items():
        if (
            hold["disposition"] != "hold"
            or hold["hold_category"] != expected_hold_categories[candidate_id]
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} hold drift: {candidate_id}")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} hold evidence drift: {candidate_id}")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} contains an unused identity")
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if (
        wave8_bannock_sheepeater_audit_signature()
        != WAVE8_BANNOCK_SHEEPEATER_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def _row_is_relevant(row: Mapping[str, Any]) -> bool:
    return any(
        normalize_label(row.get(key)) in _RELEVANT_LABELS
        for key in ("side_1_raw", "side_2_raw")
    )


def validate_wave8_bannock_sheepeater_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    relevant = [row for row in hced_rows if _row_is_relevant(row)]
    by_id = {str(row.get("candidate_id")): row for row in relevant}
    if (
        set(by_id) != WAVE8_BANNOCK_SHEEPEATER_EXPECTED_CANDIDATE_IDS
        or len(relevant) != len(by_id)
    ):
        raise ValueError(f"{_LANE_NAME} complete label inventory changed")

    for candidate_id, expected_hash in WAVE8_BANNOCK_SHEEPEATER_ROW_HASHES.items():
        row = by_id[candidate_id]
        year = 1879 if "1879" in candidate_id else 1878
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            (row.get("year_low"), row.get("year_best"), row.get("year_high"))
            != (year, year, year)
            or row.get("winner_raw")
            not in {row.get("side_1_raw"), row.get("side_2_raw")}
            or row.get("loser_raw")
            not in {row.get("side_1_raw"), row.get("side_2_raw")}
            or row.get("winner_raw") == row.get("loser_raw")
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
        ):
            raise ValueError(f"{_LANE_NAME} source semantics changed: {candidate_id}")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_BANNOCK_SHEEPEATER_CONTRACTS,
        WAVE8_BANNOCK_SHEEPEATER_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "complete_bannock_label_rows": len(relevant),
        "distinct_source_conflicts": 2,
    }


def _funnel_projection(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "label": str(row.get("label")),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, row.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
        "zero_time_valid_candidates": int(
            row.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
        ),
    }


def validate_wave8_bannock_sheepeater_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    by_label = {str(row.get("label")): row for row in funnel.get("labels", [])}
    for label, expected in WAVE8_BANNOCK_SHEEPEATER_FUNNEL_AUDIT.items():
        actual = _funnel_projection(by_label.get(label, {}))
        if actual != expected:
            raise ValueError(f"{_LANE_NAME} funnel pin changed for {label}: {actual}")
    return {
        "events_touched": sum(
            item["events_touched"]
            for item in WAVE8_BANNOCK_SHEEPEATER_FUNNEL_AUDIT.values()
        ),
        "labels": len(WAVE8_BANNOCK_SHEEPEATER_FUNNEL_AUDIT),
        "sole_blocker_events": sum(
            item["sole_blocker_events"]
            for item in WAVE8_BANNOCK_SHEEPEATER_FUNNEL_AUDIT.values()
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


_DUPLICATE_MATCH_KEYS = frozenset(
    {
        (1878, normalize_label("Birch Creek")),
        (1878, normalize_label("Battle of Birch Creek")),
        (1879, normalize_label("Vinegar Hill, Idaho")),
        (1879, normalize_label("Vinegar Hill action")),
        (1879, normalize_label("Battle of Vinegar Hill")),
    }
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_bannock_sheepeater_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_bannock_sheepeater_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_BANNOCK_SHEEPEATER_RESERVED_IDS
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
        if event.get("hced_candidate_id")
        not in WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS
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


def install_wave8_bannock_sheepeater_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_BANNOCK_SHEEPEATER_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_bannock_sheepeater_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_BANNOCK_SHEEPEATER_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_BANNOCK_SHEEPEATER_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_BANNOCK_SHEEPEATER_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_bannock_sheepeater_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_bannock_sheepeater_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_BANNOCK_SHEEPEATER_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_bannock_sheepeater_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_BANNOCK_SHEEPEATER_CONTRACTS.values(),
                    *WAVE8_BANNOCK_SHEEPEATER_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_bannock_sheepeater_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": len(WAVE8_BANNOCK_SHEEPEATER_HOLDS),
        "new_entities": len(WAVE8_BANNOCK_SHEEPEATER_ENTITIES),
        "new_sources": len(WAVE8_BANNOCK_SHEEPEATER_SOURCES),
        "newly_rated_events": len(WAVE8_BANNOCK_SHEEPEATER_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_BANNOCK_SHEEPEATER_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_BANNOCK_SHEEPEATER_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_BANNOCK_SHEEPEATER_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_bannock_sheepeater_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_BANNOCK_SHEEPEATER_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_BANNOCK_SHEEPEATER_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_bannock_sheepeater_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_bannock_sheepeater_counts(),
        "cohorts": wave8_bannock_sheepeater_cohort_counts(),
        "final_audit_signature": WAVE8_BANNOCK_SHEEPEATER_FINAL_AUDIT_SIGNATURE,
        "hold_candidate_ids": sorted(WAVE8_BANNOCK_SHEEPEATER_HOLD_IDS),
        "promoted_candidate_ids": sorted(WAVE8_BANNOCK_SHEEPEATER_CONTRACT_IDS),
    }


_validate_static()
