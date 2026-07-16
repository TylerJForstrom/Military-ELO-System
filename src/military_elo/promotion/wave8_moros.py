"""Exact Wave 8 audit for HCED rows carrying the external label ``Moros``.

``Moro`` is not installed as an entity or alias.  Each row is instead bound to
the documented, time-bounded Maranao, Tausug, Maguindanao/Buayan, or colonial
military formation that actually fought the engagement.  Nothing in this lane
transfers a rating to a modern ethnic, religious, regional, or political group.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_MOROS_CONTRACTS",
    "WAVE8_MOROS_CONTRACT_IDS",
    "WAVE8_MOROS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_MOROS_CROSS_LANE_DUPLICATE_DISPOSITIONS",
    "WAVE8_MOROS_ENTITIES",
    "WAVE8_MOROS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_MOROS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_MOROS_HOLDS",
    "WAVE8_MOROS_HOLD_IDS",
    "WAVE8_MOROS_INTEGRATION_DISPOSITIONS",
    "WAVE8_MOROS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_MOROS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_MOROS_LOCATION_REVIEW",
    "WAVE8_MOROS_OUTCOME_OVERRIDES",
    "WAVE8_MOROS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_MOROS_RESERVED_IDS",
    "WAVE8_MOROS_SOURCES",
    "install_wave8_moros_entities",
    "install_wave8_moros_sources",
    "promote_wave8_moros_contracts",
    "validate_wave8_moros_queue_contracts",
    "wave8_moros_audit_signature",
    "wave8_moros_cohort_counts",
    "wave8_moros_counts",
    "wave8_moros_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Moros exact audit"
_EVENT_ID_PREFIX = "hced_wave8_moros_"
_UNITED_STATES_ID = "united_states"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = True,
    crosscheck: bool = False,
    government_work: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if crosscheck:
        roles.append("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "U.S. Government work" if government_work else "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_MOROS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_moros_us_army_campaign_summary",
        "Philippine Insurrection: Army Campaigns brief summary",
        (
            "https://history.army.mil/Research/Reference-Topics/"
            "Army-Campaigns/Brief-Summaries/Philippine-Insurrection/"
        ),
        "U.S. Army Center of Military History",
        "official_military_history",
        "us_army_campaign_summaries_philippines",
        crosscheck=True,
        government_work=True,
    ),
    _source(
        "wave8_moros_barmm_lanao_sites",
        "Site identification and validation in Lanao del Sur",
        (
            "https://bcpch.bangsamoro.gov.ph/"
            "bcpch-conducts-site-identification-and-validation-process-"
            "in-the-province-of-lanao-del-sur/"
        ),
        "Bangsamoro Commission for the Preservation of Cultural Heritage",
        "official_cultural_heritage_site_history",
        "barmm_bcpch_lanao_validation",
        crosscheck=True,
    ),
    _source(
        "wave8_moros_war_department_1904",
        "Annual Reports of the Secretary of War, 1904 Philippine volume",
        "https://books.google.com/books?id=1AsSAAAAYAAJ",
        "U.S. War Department, Government Printing Office",
        "digitized_official_primary_report",
        "us_war_department_1904_philippines",
        crosscheck=True,
        government_work=True,
    ),
    _source(
        "wave8_moros_army_counterinsurgency_history",
        "U.S. Army Counterinsurgency and Contingency Operations Doctrine, 1860-1941",
        (
            "https://www.govinfo.gov/content/pkg/"
            "GOVPUB-D114-PURL-gpo54108/pdf/GOVPUB-D114-PURL-gpo54108.pdf"
        ),
        "U.S. Army Center of Military History",
        "official_military_history_monograph",
        "us_army_counterinsurgency_doctrine_history",
        crosscheck=True,
        government_work=True,
    ),
    _source(
        "wave8_moros_orosa_sulu_1931",
        "Sulu Archipelago and Its People: The American Administration",
        (
            "https://suluarchipelagoanditspeople.wordpress.com/"
            "chapter-3-the-american-administration/"
        ),
        "Sixto Y. Orosa; digitized 1931 historical monograph",
        "digitized_historical_monograph",
        "orosa_sulu_archipelago_1931",
        crosscheck=True,
    ),
    _source(
        "wave8_moros_anu_muslim_mindanao",
        "Muslim Mindanao under American rule: resistance and administration",
        (
            "https://openresearch-repository.anu.edu.au/server/api/core/"
            "bitstreams/9e6e7637-7d7e-411e-b1c0-b762a546ff88/content"
        ),
        "Australian National University Open Research Repository",
        "scholarly_thesis",
        "anu_muslim_mindanao_study",
        crosscheck=True,
    ),
    _source(
        "wave8_moros_22d_infantry_datu_ali_archive",
        "The Datu Ali Expedition",
        "https://www.1-22infantry.org/history3/ali.htm",
        "1st Battalion, 22d Infantry historical archive",
        "unit_history_with_transcribed_primary_records",
        "first_battalion_22d_infantry_datu_ali",
        crosscheck=True,
    ),
    _source(
        "wave8_moros_ncca_bud_bagsak",
        "Bud Bagsak",
        "https://philippineculturaleducation.com.ph/bud-bagsak/",
        "National Commission for Culture and the Arts, Sagisag Kultura",
        "official_philippine_cultural_encyclopedia",
        "ncca_sagisag_kultura_bud_bagsak",
        crosscheck=True,
    ),
    _source(
        "wave8_moros_army_turning_victory",
        "Turning Victory Into Success: Military Operations After the Campaign",
        (
            "https://www.armyupress.army.mil/Portals/7/"
            "combat-studies-institute/csi-books/TurningVictoryIntoSuccess.pdf"
        ),
        "U.S. Army Combat Studies Institute / Army University Press",
        "official_military_history_monograph",
        "us_army_csi_turning_victory",
        crosscheck=True,
        government_work=True,
    ),
    _source(
        "wave8_moros_field_artillery_bud_bagsak",
        "The Battle of Bud Bagsak",
        (
            "https://tradocfcoeccafcoepfwprod.blob.core.usgovcloudapi.net/"
            "fires-bulletin-archive/1925/NOV_DEC_1925/"
            "NOV_DEC_1925_FULL_EDITION.pdf"
        ),
        "The Field Artillery Journal, November-December 1925",
        "official_military_professional_journal",
        "field_artillery_journal_bud_bagsak_1925",
        crosscheck=True,
        government_work=True,
    ),
)


_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_MOROS_SOURCES}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    continuity_note: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start_year,
        "end_year": end_year,
        "region": "Maritime Southeast Asia",
        "aliases": [],
        "predecessors": [],
        "continuity_note": continuity_note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_MOROS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "bayang_pandapatan_defenders_1902",
        "Sultan of Bayang's Fort Pandapatan defenders (1902)",
        "engagement_bounded_maranao_sultanate_force",
        1902,
        1902,
        (
            "The Sultan of Bayang and followers defending Fort Pandapatan on "
            "2 May 1902. No rating is inherited by other Maranao communities, "
            "a generic religious population, the modern Bangsamoro polity, or "
            "any predecessor or successor."
        ),
        [
            "wave8_moros_barmm_lanao_sites",
            "wave8_moros_us_army_campaign_summary",
        ],
    ),
    _entity(
        "bacolod_grande_defenders_1903",
        "Sultan of Bacolod Grande's kota defenders (1903)",
        "engagement_bounded_maranao_sultanate_force",
        1903,
        1903,
        (
            "The Sultan of Bacolod Grande and the force defending his Lake Lanao "
            "kota during 6-8 April 1903. No rating is inherited by Bacolod City, "
            "other Maranao communities, a generic religious population, the "
            "modern Bangsamoro polity, or any predecessor or successor."
        ),
        [
            "wave8_moros_army_counterinsurgency_history",
            "wave8_moros_barmm_lanao_sites",
            "wave8_moros_war_department_1904",
        ],
    ),
    _entity(
        "panglima_hassan_luuk_force_1903",
        "Panglima Hassan's Luuk resistance force (1903)",
        "campaign_bounded_tausug_chiefdom_force",
        1903,
        1903,
        (
            "Panglima Hassan's Luuk followers in the November 1903 Lake Siit "
            "operation. No rating is inherited by all Tausug people, the Sultanate "
            "of Sulu, a generic religious population, the modern Bangsamoro polity, "
            "or Hassan's later or earlier forces without a separate contract."
        ),
        [
            "wave8_moros_orosa_sulu_1931",
            "wave8_moros_war_department_1904",
        ],
    ),
    _entity(
        "datu_ali_buayan_resistance_1902_1905",
        "Datu Ali's Buayan resistance (1902-1905)",
        "regime_bounded_buayan_force",
        1902,
        1905,
        (
            "The force owing operational allegiance to Datu Ali during his bounded "
            "Buayan resistance, used here only for Kudarangan in 1904 and Malala in "
            "1905. No rating is inherited by all Maguindanao people, the historical "
            "Maguindanao sultanate envelope, a generic religious population, the "
            "modern Bangsamoro polity, or any predecessor or successor regime."
        ),
        [
            "wave8_moros_22d_infantry_datu_ali_archive",
            "wave8_moros_anu_muslim_mindanao",
            "wave8_moros_war_department_1904",
        ],
    ),
    _entity(
        "philippine_scouts_bud_bagsak_column_1913",
        "Philippine Scouts in the Bud Bagsak column (1913)",
        "engagement_bounded_colonial_military_formation",
        1913,
        1913,
        (
            "The Philippine Scout companies documented in the Bud Bagsak assault, "
            "kept distinct from the United States state participant. No rating is "
            "inherited by the modern Philippines, all Filipinos, other Scout units, "
            "or any predecessor or successor formation."
        ),
        [
            "wave8_moros_army_turning_victory",
            "wave8_moros_field_artillery_bud_bagsak",
        ],
    ),
    _entity(
        "datu_amil_lati_bud_bagsak_defenders_1913",
        "Datu Amil's Lati Ward defenders at Bud Bagsak (1913)",
        "engagement_bounded_tausug_resistance_force",
        1913,
        1913,
        (
            "The armed Lati Ward resistance led by Datu Amil and associated datus "
            "at Bud Bagsak, not the noncombatant population on the mountain. No "
            "rating is inherited by all Tausug people, the Sultanate of Sulu, a "
            "generic religious population, the modern Bangsamoro polity, or any "
            "predecessor or successor."
        ),
        [
            "wave8_moros_anu_muslim_mindanao",
            "wave8_moros_field_artillery_bud_bagsak",
            "wave8_moros_ncca_bud_bagsak",
        ],
    ),
)


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str = "day",
) -> dict[str, Any]:
    return {
        "name": name,
        "year_low": year,
        "year_high": year,
        "date_text": date_text,
        "date_precision": date_precision,
        "granularity": "engagement",
        "canonical_key": f"{_slug(name)}:{year}:{year}",
    }


def _families(source_ids: Iterable[str]) -> list[str]:
    return sorted(
        {
            str(_SOURCE_BY_ID[source_id]["source_family_id"])
            for source_id in source_ids
        }
    )


def _contract(
    row_hash: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    source_outcome_override: bool = False,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": row_hash,
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "winner_side": 1,
        "result_type": "win",
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": _families(outcomes),
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": source_outcome_override,
        "actor_override": "bounded_exact_opposing_forces",
        "audit_note": audit_note,
    }


WAVE8_MOROS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Bayan1902-1": _contract(
        "6d236eee05e93d371946429c9bfc0d16d6f05ffaf56a025e7e25da5c0901717a",
        _canonical("Battle of Bayang", 1902, "2 May 1902"),
        "lanao_resistance_1902_1903",
        [_UNITED_STATES_ID],
        ["bayang_pandapatan_defenders_1902"],
        [
            "wave8_moros_barmm_lanao_sites",
            "wave8_moros_us_army_campaign_summary",
        ],
        [
            "wave8_moros_barmm_lanao_sites",
            "wave8_moros_us_army_campaign_summary",
        ],
        (
            "Official U.S. Army history records Baldwin's defeat of the Sultan of "
            "Bayang's force on 2 May, while BARMM heritage validation identifies "
            "the Sultan and followers at Fort Pandapatan. The external label is not "
            "promoted as an identity."
        ),
        confidence=0.88,
    ),
    "hced-Bacolod1903-1": _contract(
        "56a44f6bd2ac63d4fb1fcc32b20c502a1c9cdc6443c01e91292e57b38f897138",
        _canonical("Battle of Bacolod Grande", 1903, "6-8 April 1903"),
        "lanao_resistance_1902_1903",
        [_UNITED_STATES_ID],
        ["bacolod_grande_defenders_1903"],
        [
            "wave8_moros_army_counterinsurgency_history",
            "wave8_moros_barmm_lanao_sites",
            "wave8_moros_war_department_1904",
        ],
        [
            "wave8_moros_army_counterinsurgency_history",
            "wave8_moros_barmm_lanao_sites",
            "wave8_moros_war_department_1904",
        ],
        (
            "The three-day Lake Lanao engagement and storming of the Bacolod kota "
            "are directly documented. The opponent is the Sultan's bounded fort "
            "force, and the raw point for namesake Bacolod City in Negros is withheld."
        ),
        confidence=0.87,
    ),
    "hced-Lake Seit1903-1": _contract(
        "1e025784f883aa2b8a9834e91e43022c053e0f8caf600abd76a68a32339f93b8",
        _canonical(
            "Battle of Lake Siit",
            1903,
            "November 1903",
            date_precision="month",
        ),
        "hassan_uprising_1903",
        [_UNITED_STATES_ID],
        ["panglima_hassan_luuk_force_1903"],
        [
            "wave8_moros_orosa_sulu_1931",
            "wave8_moros_war_department_1904",
        ],
        [
            "wave8_moros_orosa_sulu_1931",
            "wave8_moros_war_department_1904",
        ],
        (
            "The historical record identifies the Lake Siit action as the U.S. "
            "engagement with Panglima Hassan's Luuk force and records the force's "
            "defeat and Hassan's capture. No unsupported day within November is invented."
        ),
        confidence=0.82,
    ),
    "hced-Kudarangan1904-1": _contract(
        "33c892ba8d6e228a880ed68b2d34c4615122668c6d194365051a0843b891fcca",
        _canonical("Battle of Kudarangan", 1904, "10-11 March 1904"),
        "datu_ali_buayan_resistance_1904_1905",
        [_UNITED_STATES_ID],
        ["datu_ali_buayan_resistance_1902_1905"],
        [
            "wave8_moros_anu_muslim_mindanao",
            "wave8_moros_army_counterinsurgency_history",
            "wave8_moros_war_department_1904",
        ],
        [
            "wave8_moros_anu_muslim_mindanao",
            "wave8_moros_war_department_1904",
        ],
        (
            "HCED's incomplete Draw is rejected. The official chronology records a "
            "10 March bombardment followed by capture and destruction of Datu Ali's "
            "fort on 11 March; the scholarly account independently records the U.S. "
            "destruction of Ali's main fort. This is an explicit sourced win override."
        ),
        confidence=0.84,
        source_outcome_override=True,
    ),
    "hced-Malala1905-1": _contract(
        "17590c2d251e6b49a76f3b589c355a8fb23bedef9ce2f58eb97b85db4af42401",
        _canonical("Battle of the Malala River", 1905, "22 October 1905"),
        "datu_ali_buayan_resistance_1904_1905",
        [_UNITED_STATES_ID],
        ["datu_ali_buayan_resistance_1902_1905"],
        [
            "wave8_moros_22d_infantry_datu_ali_archive",
            "wave8_moros_anu_muslim_mindanao",
            "wave8_moros_us_army_campaign_summary",
        ],
        [
            "wave8_moros_22d_infantry_datu_ali_archive",
            "wave8_moros_anu_muslim_mindanao",
            "wave8_moros_us_army_campaign_summary",
        ],
        (
            "The sources identify McCoy's 22d Infantry provisional company, Datu "
            "Ali's own Buayan resistance force, the 22 October date, and the U.S. "
            "tactical success. The misleading raw point is withheld."
        ),
        confidence=0.87,
    ),
    "hced-Bud Bagsak1913-1": _contract(
        "282be40de5c8c42414840c676b5639c0131638aeff281848b1d18226580c4adc",
        _canonical("Battle of Bud Bagsak", 1913, "11-15 June 1913"),
        "bud_bagsak_disarmament_resistance_1913",
        [_UNITED_STATES_ID, "philippine_scouts_bud_bagsak_column_1913"],
        ["datu_amil_lati_bud_bagsak_defenders_1913"],
        [
            "wave8_moros_anu_muslim_mindanao",
            "wave8_moros_army_turning_victory",
            "wave8_moros_field_artillery_bud_bagsak",
            "wave8_moros_ncca_bud_bagsak",
            "wave8_moros_us_army_campaign_summary",
        ],
        [
            "wave8_moros_field_artillery_bud_bagsak",
            "wave8_moros_ncca_bud_bagsak",
            "wave8_moros_us_army_campaign_summary",
        ],
        (
            "Official U.S. and Philippine references agree on the 11-15 June "
            "engagement, U.S.-Philippine Scout victory, and Datu Amil's armed Lati "
            "Ward force. The identity excludes noncombatants present on the mountain."
        ),
        confidence=0.88,
    ),
}


# The entire six-row cohort has a defensible competitive result.  The empty
# inventory is still signed so a future hold cannot appear without review.
WAVE8_MOROS_HOLDS: dict[str, dict[str, Any]] = {}

WAVE8_MOROS_CONTRACT_IDS = frozenset(WAVE8_MOROS_CONTRACTS)
WAVE8_MOROS_HOLD_IDS = frozenset(WAVE8_MOROS_HOLDS)
WAVE8_MOROS_RESERVED_IDS = WAVE8_MOROS_CONTRACT_IDS | WAVE8_MOROS_HOLD_IDS
WAVE8_MOROS_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_MOROS_RESERVED_IDS)


WAVE8_MOROS_LOCATION_REVIEW: dict[str, dict[str, Any]] = {
    "hced-Bacolod1903-1": {
        "point_disposition": "quarantine",
        "country_disposition": "retain",
        "reason": (
            "The raw point resolves to namesake Bacolod City on Negros, while the "
            "engagement occurred at Bacolod Grande on Lake Lanao."
        ),
        "evidence_refs": ["wave8_moros_barmm_lanao_sites"],
    },
    "hced-Bayan1902-1": {
        "point_disposition": "quarantine",
        "country_disposition": "retain",
        "reason": (
            "The raw geocode is not a source-attested Fort Pandapatan battlefield "
            "point; BARMM validation locates the site only at Bayang."
        ),
        "evidence_refs": ["wave8_moros_barmm_lanao_sites"],
    },
    "hced-Bud Bagsak1913-1": {
        "point_disposition": "quarantine",
        "country_disposition": "retain",
        "reason": (
            "The row supplies an automated mountain-name point without direct "
            "coordinate provenance; only the Jolo/Sulu country location is retained."
        ),
        "evidence_refs": [
            "wave8_moros_field_artillery_bud_bagsak",
            "wave8_moros_ncca_bud_bagsak",
        ],
    },
    "hced-Kudarangan1904-1": {
        "point_disposition": "quarantine",
        "country_disposition": "retain",
        "reason": (
            "The sources identify Datu Ali's fortified position and Sar-Raya "
            "operation, not the exact modern-place centroid supplied by the row."
        ),
        "evidence_refs": ["wave8_moros_war_department_1904"],
    },
    "hced-Lake Seit1903-1": {
        "point_disposition": "quarantine",
        "country_disposition": "retain",
        "reason": (
            "The sources establish Lake Siit on Jolo but do not authenticate the "
            "row's exact automated coordinate as the engagement point."
        ),
        "evidence_refs": ["wave8_moros_orosa_sulu_1931"],
    },
    "hced-Malala1905-1": {
        "point_disposition": "quarantine",
        "country_disposition": "retain",
        "reason": (
            "The raw point is far north of the documented Malala River approach "
            "from Digos into Datu Ali's Cotabato/Buayan country."
        ),
        "evidence_refs": ["wave8_moros_22d_infantry_datu_ali_archive"],
    },
}

WAVE8_MOROS_POINT_QUARANTINE_ADDITIONS = frozenset(
    candidate_id
    for candidate_id, review in WAVE8_MOROS_LOCATION_REVIEW.items()
    if review["point_disposition"] == "quarantine"
)
WAVE8_MOROS_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    candidate_id
    for candidate_id, review in WAVE8_MOROS_LOCATION_REVIEW.items()
    if review["country_disposition"] == "quarantine"
)
WAVE8_MOROS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_MOROS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_MOROS_COUNTRY_QUARANTINE_ADDITIONS,
}


# The complete IWBD queue contains no Bayan/Bayang, Bacolod Grande, Lake Siit,
# Kudarangan, Malala River, or Bud Bagsak engagement.  No duplicate is invented.
WAVE8_MOROS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_MOROS_CROSS_LANE_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_MOROS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_MOROS_IWBD_DUPLICATE_DISPOSITIONS,
    **WAVE8_MOROS_CROSS_LANE_DUPLICATE_DISPOSITIONS,
}


WAVE8_MOROS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Kudarangan1904-1": {
        "raw_outcome": "Draw",
        "reviewed_outcome": "united_states_victory",
        "reason": (
            "The staged row is explicitly incomplete, while the official report "
            "records bombardment, capture, captured ordnance, and destruction of "
            "Datu Ali's fort on 10-11 March 1904."
        ),
        "evidence_refs": [
            "wave8_moros_anu_muslim_mindanao",
            "wave8_moros_war_department_1904",
        ],
    }
}


_EXPECTED_CONTRACT_IDS = frozenset(
    {
        "hced-Bacolod1903-1",
        "hced-Bayan1902-1",
        "hced-Bud Bagsak1913-1",
        "hced-Kudarangan1904-1",
        "hced-Lake Seit1903-1",
        "hced-Malala1905-1",
    }
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_MOROS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_MOROS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_duplicate_dispositions": (
            WAVE8_MOROS_CROSS_LANE_DUPLICATE_DISPOSITIONS
        ),
        "entities": WAVE8_MOROS_ENTITIES,
        "holds": WAVE8_MOROS_HOLDS,
        "iwbd_duplicate_dispositions": WAVE8_MOROS_IWBD_DUPLICATE_DISPOSITIONS,
        "location_review": WAVE8_MOROS_LOCATION_REVIEW,
        "outcome_overrides": WAVE8_MOROS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_MOROS_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_MOROS_SOURCES,
    }


def wave8_moros_audit_signature() -> str:
    """Return the immutable SHA-256 pin over the complete lane audit."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_MOROS_FINAL_AUDIT_SIGNATURE = (
    "503c11f15bc8979d536f66592135ad481efcc6b51cc558e780e854e701ea8921"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(values)
    return items == sorted(set(items))


def _validate_static() -> None:
    if WAVE8_MOROS_CONTRACT_IDS != _EXPECTED_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} promotion inventory changed")
    if WAVE8_MOROS_HOLDS or WAVE8_MOROS_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} unexpectedly added a nonpromotion")
    if WAVE8_MOROS_RESERVED_IDS != WAVE8_MOROS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reserved inventory changed")
    if wave8_moros_audit_signature() != WAVE8_MOROS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_MOROS_SOURCES}
    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_MOROS_ENTITIES}
    if len(source_by_id) != 10 or len(source_by_id) != len(WAVE8_MOROS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source inventory changed")
    if len(entity_by_id) != 6 or len(entity_by_id) != len(WAVE8_MOROS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity inventory changed")

    for source in WAVE8_MOROS_SOURCES:
        roles = list(map(str, source["evidence_roles"]))
        if not _is_sorted_unique(roles):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    for entity in WAVE8_MOROS_ENTITIES:
        if entity["start_year"] is None or entity["end_year"] is None:
            raise ValueError(f"{_LANE_NAME} installed an unbounded entity")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} opened a generic identity fallback")
        text = f"{entity['name']} {entity['continuity_note']}".casefold()
        if "no rating is inherited" not in text or "modern" not in text:
            raise ValueError(f"{_LANE_NAME} entity permits continuity inheritance")
        if str(entity["name"]).casefold().strip() in {"moro", "moros", "moro people"}:
            raise ValueError(f"{_LANE_NAME} installed a generic external label")
        source_ids = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(source_ids) or not set(source_ids) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity provenance drift")

    allowed_entity_ids = set(entity_by_id) | {_UNITED_STATES_ID}
    used_new_entity_ids: set[str] = set()
    for candidate_id, contract in WAVE8_MOROS_CONTRACTS.items():
        row_hash = str(contract["raw_row_sha256"])
        if len(row_hash) != 64 or any(char not in "0123456789abcdef" for char in row_hash):
            raise ValueError(f"{_LANE_NAME} invalid row hash for {candidate_id}")
        if contract["result_type"] != "win" or contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} invented a draw or noncanonical result")

        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} canonical key drift for {candidate_id}")
        if canonical["granularity"] != "engagement":
            raise ValueError(f"{_LANE_NAME} granularity drift for {candidate_id}")
        if canonical["date_precision"] not in {"day", "month"}:
            raise ValueError(f"{_LANE_NAME} unsupported date precision")

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory drift for {candidate_id}")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} invalid opposing sides for {candidate_id}")
        if not (set(side_1) | set(side_2)) <= allowed_entity_ids:
            raise ValueError(f"{_LANE_NAME} unknown entity for {candidate_id}")
        used_new_entity_ids.update((set(side_1) | set(side_2)) & set(entity_by_id))

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} source provenance drift for {candidate_id}")
        if not outcomes or not set(outcomes) <= set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} direct outcome source gap")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} non-outcome source used as direct evidence")
        if families != _families(outcomes) or not _is_sorted_unique(families):
            raise ValueError(f"{_LANE_NAME} source-family drift for {candidate_id}")

    if used_new_entity_ids != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")

    override_ids = {
        candidate_id
        for candidate_id, contract in WAVE8_MOROS_CONTRACTS.items()
        if contract["source_outcome_override"]
    }
    if override_ids != set(WAVE8_MOROS_OUTCOME_OVERRIDES):
        raise ValueError(f"{_LANE_NAME} outcome override inventory changed")
    if override_ids != {"hced-Kudarangan1904-1"}:
        raise ValueError(f"{_LANE_NAME} unexpected outcome override")

    if set(WAVE8_MOROS_LOCATION_REVIEW) != _EXPECTED_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location audit inventory changed")
    if WAVE8_MOROS_POINT_QUARANTINE_ADDITIONS != _EXPECTED_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_MOROS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    for candidate_id, review in WAVE8_MOROS_LOCATION_REVIEW.items():
        if review["point_disposition"] != "quarantine":
            raise ValueError(f"{_LANE_NAME} unreviewed point for {candidate_id}")
        if review["country_disposition"] != "retain":
            raise ValueError(f"{_LANE_NAME} country review drift for {candidate_id}")
        refs = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location provenance drift")

    if WAVE8_MOROS_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    if WAVE8_MOROS_CROSS_LANE_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} cross-lane duplicate inventory changed")
    if WAVE8_MOROS_INTEGRATION_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} integration disposition inventory changed")


def validate_wave8_moros_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_MOROS_CONTRACTS,
        WAVE8_MOROS_HOLDS,
        lane_name=_LANE_NAME,
    )


def install_wave8_moros_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_MOROS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_moros_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_MOROS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_MOROS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_MOROS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_moros_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_moros_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_MOROS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_moros_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_MOROS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_moros_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_MOROS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_duplicate_dispositions": len(
            WAVE8_MOROS_CROSS_LANE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_MOROS_HOLDS),
        "integration_dispositions": len(WAVE8_MOROS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_MOROS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_MOROS_ENTITIES),
        "new_sources": len(WAVE8_MOROS_SOURCES),
        "newly_rated_events": len(WAVE8_MOROS_CONTRACTS),
        "outcome_overrides": len(WAVE8_MOROS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_MOROS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_MOROS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_MOROS_RESERVED_IDS),
    }


def wave8_moros_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_MOROS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_MOROS_POINT_QUARANTINE_ADDITIONS,
    }
