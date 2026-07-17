"""Candidate-keyed Wave 8 audit for HCED's exact ``Zulu Rebels`` label.

The five locked rows belong to two different conflicts.  Ivuna and
Hlophekhulu are engagements in the 1888 uSuthu rebellion in British
Zululand; Bobe Ridge, Mpukunyoni, and Mome Gorge belong to the 1906
Bambatha rebellion.  This lane therefore never creates a generic Zulu,
Zulu-rebel, United Kingdom, or South Africa alias.

Every result is independently source-supported and remains tactical.  The
1888 contracts distinguish Dinuzulu's uSuthu from Zibhebhu's Mandlakazi and
from the British field force with African auxiliaries.  The 1906 contracts
use campaign-bounded colonial and insurgent coalitions while explicitly
avoiding the claim that every component fought in every engagement.
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
    "WAVE8_ZULU_FORCES_CONTRACT_IDS",
    "WAVE8_ZULU_FORCES_CONTRACTS",
    "WAVE8_ZULU_FORCES_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ZULU_FORCES_ENTITIES",
    "WAVE8_ZULU_FORCES_EXPECTED_CANDIDATE_IDS",
    "WAVE8_ZULU_FORCES_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ZULU_FORCES_FUNNEL_AUDIT",
    "WAVE8_ZULU_FORCES_HOLD_IDS",
    "WAVE8_ZULU_FORCES_HOLDS",
    "WAVE8_ZULU_FORCES_LOCATION_QUARANTINE_REASONS",
    "WAVE8_ZULU_FORCES_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ZULU_FORCES_RESERVED_IDS",
    "WAVE8_ZULU_FORCES_ROW_HASHES",
    "WAVE8_ZULU_FORCES_SOURCES",
    "install_wave8_zulu_forces_entities",
    "install_wave8_zulu_forces_sources",
    "promote_wave8_zulu_forces_contracts",
    "validate_wave8_zulu_forces_funnel",
    "validate_wave8_zulu_forces_integration_dispositions",
    "validate_wave8_zulu_forces_queue_contracts",
    "wave8_zulu_forces_audit_signature",
    "wave8_zulu_forces_cohort_counts",
    "wave8_zulu_forces_counts",
    "wave8_zulu_forces_location_quarantine_additions",
    "wave8_zulu_forces_metadata",
)


_LANE_NAME = "Wave 8 exact Zulu campaign-force audit"
_MODULE_OWNER = "military_elo.promotion.wave8_zulu_forces"
_EVENT_ID_PREFIX = "hced_wave8_zulu_forces_"
_EXACT_LABEL = "zulu rebels"

_USUTHU_ID = "usuthu_dinuzulu_rebellion_force_1888"
_MANDLAKAZI_ID = "mandlakazi_zibhebhu_force_ivuna_1888"
_BRITISH_ZULULAND_FORCE_ID = "british_zululand_hlophekhulu_force_1888"
_NATAL_COLONIAL_FORCE_ID = "natal_led_bambatha_suppression_force_1906"
_BAMBATHA_INSURGENT_ID = "bambatha_sigananda_insurgent_coalition_1906"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
    crosscheck: bool = False,
) -> dict[str, Any]:
    roles = {"identity_boundary_or_context_reference"}
    if outcome:
        roles.add("outcome")
    if crosscheck:
        roles.add("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_ZULU_FORCES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_zulu_cambridge_prisoners",
        "Zulu Political Prisoners, 1872-1897",
        (
            "https://www.cambridge.org/core/books/imperial-incarceration/"
            "zulu-political-prisoners-18721897/21354AD11338C07AD5C1BF6288893297"
        ),
        "Cambridge University Press",
        "scholarly_book_chapter_with_primary_parliamentary_sources",
        "hynd_imperial_incarceration_zulu_prisoners",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_zulu_laband_ivuna",
        "The Battle of Ivuna (or Ndunu Hill)",
        "https://www.scribd.com/document/39469892/Natalia-10-1980-complete",
        "Natalia 10, Natal Society Foundation",
        "peer_reviewed_battle_study_with_primary_reports_and_oral_history",
        "laband_natalia_ivuna_1980",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_zulu_laband_divided_command",
        (
            "The Danger of Divided Command: British civil and military disputes "
            "over the conduct of the Zululand campaigns of 1879 and 1888"
        ),
        "https://pdfs.semanticscholar.org/b66a/724464f70ccc2ff0b0533fefbc693c172d47.pdf",
        "Journal of the Society for Army Historical Research 81(328)",
        "peer_reviewed_military_history_with_archival_sources",
        "laband_divided_command_2003",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_zulu_laband_dictionary",
        "Historical Dictionary of the Zulu Wars",
        (
            "https://sahistory.org.za/sites/default/files/archive-files/"
            "john_laband_historical_dictionary_of_the_zulu_wabook4me.org_.pdf"
        ),
        "Scarecrow Press / South African History Online archive",
        "scholarly_reference_book",
        "laband_historical_dictionary_zulu_wars",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_zulu_colenbrander_report",
        "An Account of the Zulu Rebellion of 1906",
        "https://www.natalia.org.za/Files/35/Natalia%2035%20pp10-28%20C.pdf",
        "Natalia 35, Natal Society Foundation",
        "edited_contemporaneous_administrative_report",
        "colenbrander_spencer_natalia_1906_report",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_zulu_coghlan_harte",
        "The record of a racist killer?",
        "https://www.natalia.org.za/Files/35/Natalia%2035%20pp29-56%20C.pdf",
        "Natalia 35, Natal Society Foundation",
        "scholarly_article_with_archival_soldier_record",
        "coghlan_harte_natalia_2005",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_zulu_gillings_mome",
        "The Bambata Rebellion of 1906: Nkandla Operations and Mome Gorge",
        "https://samilitaryhistory.org/vol081kg.html",
        "South African Military History Society, Military History Journal",
        "military_history_article_with_operational_sources",
        "gillings_bambata_mome_1989",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_zulu_paterson_1906",
        "The Natal Rebellion 1906: Some Military Perspectives",
        "https://samilitaryhistory.org/vol135hp.html",
        "South African Military History Society, Military History Journal",
        "military_history_article",
        "paterson_natal_rebellion_2006",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_zulu_umvoti_field_force",
        "Umvoti Mounted Rifles 1906-7",
        "https://samilitaryhistory.org/vol136mc.html",
        "South African Military History Society, Military History Journal",
        "regimental_and_operational_history",
        "coghlan_umvoti_field_force_2006",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_zulu_paperspast_mpukunyoni",
        "The Natal Rising: The Bunkinyoni Fight, 1 June 1906",
        "https://paperspast.natlib.govt.nz/newspapers/WT19060601.2.13.6",
        "Waikato Times / National Library of New Zealand Papers Past",
        "contemporary_newspaper_report",
        "waikato_times_mpukunyoni_1906",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_zulu_saho_bambatha",
        "Bambatha Rebellion 1906",
        "https://sahistory.org.za/article/bambatha-rebellion-1906",
        "South African History Online",
        "scholarly_public_history_reference",
        "saho_bambatha_rebellion",
        outcome=True,
        crosscheck=True,
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_ZULU_FORCES_SOURCES}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 1888 if entity_id.endswith("1888") else 1906,
        "end_year": 1888 if entity_id.endswith("1888") else 1906,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No generic Zulu, Zulu Rebels, United Kingdom, South Africa, or "
            "campaign label resolves to this record. It inherits no Elo from a "
            "predecessor, successor, dynasty, ethnic umbrella, or modern state."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_ZULU_FORCES_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _USUTHU_ID,
        "Dinuzulu's uSuthu rebellion force (1888)",
        "insurgent_coalition",
        "British Zululand",
        [
            "wave8_zulu_cambridge_prisoners",
            "wave8_zulu_laband_dictionary",
            "wave8_zulu_laband_ivuna",
        ],
        (
            "Bounded to the uSuthu adherents of Dinuzulu and aligned forces in the "
            "1888 rebellion, including Shingana's Hlophekhulu contingent. It is "
            "not the pre-1879 Zulu Kingdom or all uSuthu in another period."
        ),
    ),
    _entity(
        _MANDLAKAZI_ID,
        "Zibhebhu's Mandlakazi force at Ivuna (1888)",
        "event_bounded_allied_force",
        "Ndwandwe District, British Zululand",
        ["wave8_zulu_laband_dictionary", "wave8_zulu_laband_ivuna"],
        (
            "Bounded to Zibhebhu's Mandlakazi fighting force at Ivuna on 23 June "
            "1888. British alignment does not merge it with the nearby Zululand "
            "Police garrison, which the uSuthu did not assault."
        ),
    ),
    _entity(
        _BRITISH_ZULULAND_FORCE_ID,
        "British Zululand field force at Hlophekhulu (1888)",
        "event_bounded_colonial_field_force",
        "British Zululand",
        [
            "wave8_zulu_cambridge_prisoners",
            "wave8_zulu_laband_dictionary",
            "wave8_zulu_laband_divided_command",
        ],
        (
            "Bounded to Colonel Stabb's British troops and African auxiliaries "
            "that stormed Hlophekhulu on 2 July 1888; it is not a timeless United "
            "Kingdom result or an assertion that every auxiliary fought elsewhere."
        ),
    ),
    _entity(
        _NATAL_COLONIAL_FORCE_ID,
        "Natal-led colonial forces in the Bambatha Rebellion (1906)",
        "campaign_coalition_army",
        "Natal and British Zululand",
        [
            "wave8_zulu_colenbrander_report",
            "wave8_zulu_gillings_mome",
            "wave8_zulu_paterson_1906",
            "wave8_zulu_umvoti_field_force",
        ],
        (
            "Bounded to the 1906 colonial command and its event-specific columns, "
            "militia, police, and levies at Bobe, Mpukunyoni, and Mome. The shared "
            "campaign identity does not claim every component fought in each action."
        ),
    ),
    _entity(
        _BAMBATHA_INSURGENT_ID,
        "Bambatha-Sigananda insurgent coalition (1906)",
        "insurgent_coalition",
        "Natal and British Zululand",
        [
            "wave8_zulu_colenbrander_report",
            "wave8_zulu_gillings_mome",
            "wave8_zulu_saho_bambatha",
        ],
        (
            "Bounded to the anti-poll-tax insurgent coalition associated with "
            "Bambatha, Sigananda, and aligned chiefs during the 1906 campaign. It "
            "does not represent all Zulu people, clans, or later political actors."
        ),
    ),
)


WAVE8_ZULU_FORCES_ROW_HASHES: dict[str, str] = {
    "hced-Bobe1906-1": "dbe7b2a6abed9451af55f4d47e00dfca62b79419234ad7fde19c7d3e1f9f0db1",
    "hced-Hlophekhulu1888-1": "18e84445a5a96a2c9d4a6719503a2c84edca9f8effaa3a449edcf421d14261c6",
    "hced-Ivuna1888-1": "082e506dc869dbd1468e29584928317218e4adcd4b52674992fe486422c15b50",
    "hced-Mome1906-1": "b123f46e10af8cb741e47e62b660d5bf5069c285453f20581e55b68457e9916b",
    "hced-Mpukonyoni1906-1": "eb6e1eb8ec31367dbd434f875011418261b026391f7218dafec18303022cfaa5",
}

WAVE8_ZULU_FORCES_FUNNEL_AUDIT: dict[str, Any] = {
    "event_candidate_id_sha256": (
        "3286de59ed56479a5da77b5adc9ae8a6170e9cdc2bfec87a43898c87668db53c"
    ),
    "events_touched": 5,
    "label": _EXACT_LABEL,
    "sole_blocker_events": 3,
    "zero_time_valid_candidates": 5,
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
    cohort: str,
    side_1: Iterable[str],
    side_2: Iterable[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_ZULU_FORCES_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
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
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_event_or_campaign_bounded_force",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_ZULU_FORCES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Hlophekhulu1888-1": _contract(
        "hced-Hlophekhulu1888-1",
        _canonical(
            "Battle of Hlophekhulu",
            1888,
            "2 July 1888",
            "single_assault_on_mountain_stronghold",
        ),
        "usuthu_rebellion_1888",
        [_BRITISH_ZULULAND_FORCE_ID],
        [_USUTHU_ID],
        1,
        [
            "wave8_zulu_cambridge_prisoners",
            "wave8_zulu_laband_dictionary",
            "wave8_zulu_laband_divided_command",
        ],
        [
            "wave8_zulu_cambridge_prisoners",
            "wave8_zulu_laband_dictionary",
            "wave8_zulu_laband_divided_command",
        ],
        (
            "The archival military study and scholarly reference agree that "
            "Stabb's force expelled Shingana's uSuthu from Hlophekhulu on 2 July. "
            "The result is the stronghold action, not the rebellion's termination."
        ),
        confidence=0.92,
    ),
    "hced-Ivuna1888-1": _contract(
        "hced-Ivuna1888-1",
        _canonical(
            "Battle of Ivuna (Ndunu Hill)",
            1888,
            "23 June 1888",
            "single_battle_between_usuthu_and_mandlakazi",
        ),
        "usuthu_rebellion_1888",
        [_USUTHU_ID],
        [_MANDLAKAZI_ID],
        1,
        [
            "wave8_zulu_cambridge_prisoners",
            "wave8_zulu_laband_dictionary",
            "wave8_zulu_laband_ivuna",
        ],
        [
            "wave8_zulu_cambridge_prisoners",
            "wave8_zulu_laband_dictionary",
            "wave8_zulu_laband_ivuna",
        ],
        (
            "The dedicated battle study reconstructs the uSuthu rout of Zibhebhu's "
            "Mandlakazi and heavy Mandlakazi losses. The nearby Zululand Police "
            "fort fired but was deliberately bypassed, so it is not put on side 2."
        ),
        confidence=0.94,
    ),
    "hced-Bobe1906-1": _contract(
        "hced-Bobe1906-1",
        _canonical(
            "Battle of Bobe Ridge",
            1906,
            "5 May 1906",
            "single_rebel_assault_on_colonial_column",
        ),
        "bambatha_rebellion_1906",
        [_NATAL_COLONIAL_FORCE_ID],
        [_BAMBATHA_INSURGENT_ID],
        1,
        [
            "wave8_zulu_coghlan_harte",
            "wave8_zulu_colenbrander_report",
            "wave8_zulu_gillings_mome",
            "wave8_zulu_paterson_1906",
        ],
        [
            "wave8_zulu_coghlan_harte",
            "wave8_zulu_colenbrander_report",
            "wave8_zulu_gillings_mome",
        ],
        (
            "The contemporary administrative account records the determined rebel "
            "attack, roughly 70-80 rebel casualties, and ensuing desertions. The "
            "contract replaces HCED's anachronistic 'South Africa' side with the "
            "actual Natal-led column."
        ),
        confidence=0.90,
    ),
    "hced-Mpukonyoni1906-1": _contract(
        "hced-Mpukonyoni1906-1",
        _canonical(
            "Battle of Mpukunyoni",
            1906,
            "28 May 1906",
            "single_attack_on_umvoti_field_force_square",
        ),
        "bambatha_rebellion_1906",
        [_NATAL_COLONIAL_FORCE_ID],
        [_BAMBATHA_INSURGENT_ID],
        1,
        [
            "wave8_zulu_coghlan_harte",
            "wave8_zulu_colenbrander_report",
            "wave8_zulu_paperspast_mpukunyoni",
            "wave8_zulu_paterson_1906",
            "wave8_zulu_umvoti_field_force",
        ],
        [
            "wave8_zulu_colenbrander_report",
            "wave8_zulu_paperspast_mpukunyoni",
            "wave8_zulu_paterson_1906",
            "wave8_zulu_umvoti_field_force",
        ],
        (
            "The contemporary report, administrative account, and operational "
            "histories agree that Leuchars's square repulsed repeated attacks on 28 "
            "May. A secondary summary's 25 May typo is not used for the date pin."
        ),
        confidence=0.92,
    ),
    "hced-Mome1906-1": _contract(
        "hced-Mome1906-1",
        _canonical(
            "Battle of Mome Gorge",
            1906,
            "10 June 1906",
            "single_encirclement_and_breaking_of_rebel_field_force",
        ),
        "bambatha_rebellion_1906",
        [_NATAL_COLONIAL_FORCE_ID],
        [_BAMBATHA_INSURGENT_ID],
        1,
        [
            "wave8_zulu_coghlan_harte",
            "wave8_zulu_colenbrander_report",
            "wave8_zulu_gillings_mome",
            "wave8_zulu_paterson_1906",
            "wave8_zulu_saho_bambatha",
        ],
        [
            "wave8_zulu_coghlan_harte",
            "wave8_zulu_gillings_mome",
            "wave8_zulu_saho_bambatha",
        ],
        (
            "Independent operational and public-history accounts agree that the "
            "colonial force surrounded and defeated Bambatha's force at Mome Gorge "
            "on 10 June. Only the tactical engagement is rated."
        ),
        confidence=0.96,
    ),
}

WAVE8_ZULU_FORCES_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_ZULU_FORCES_CONTRACT_IDS = frozenset(WAVE8_ZULU_FORCES_CONTRACTS)
WAVE8_ZULU_FORCES_HOLD_IDS = frozenset(WAVE8_ZULU_FORCES_HOLDS)
WAVE8_ZULU_FORCES_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_ZULU_FORCES_ROW_HASHES)
WAVE8_ZULU_FORCES_RESERVED_IDS = WAVE8_ZULU_FORCES_EXPECTED_CANDIDATE_IDS

WAVE8_ZULU_FORCES_POINT_QUARANTINE_ADDITIONS = WAVE8_ZULU_FORCES_CONTRACT_IDS
WAVE8_ZULU_FORCES_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_ZULU_FORCES_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources identify the named battlefield and modern country "
            "but do not independently verify HCED's exact coordinate; retain the "
            "South Africa country assertion and withhold the unaudited point."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_ZULU_FORCES_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_ZULU_FORCES_CONTRACTS,
        "entities": WAVE8_ZULU_FORCES_ENTITIES,
        "funnel": WAVE8_ZULU_FORCES_FUNNEL_AUDIT,
        "holds": WAVE8_ZULU_FORCES_HOLDS,
        "location_reasons": WAVE8_ZULU_FORCES_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_ZULU_FORCES_ROW_HASHES,
        "sources": WAVE8_ZULU_FORCES_SOURCES,
    }


def wave8_zulu_forces_audit_signature() -> str:
    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_ZULU_FORCES_FINAL_AUDIT_SIGNATURE = (
    "2dff7d7890332360082184f05777b73b76a1f235d647d47b196c5cc373d3b941"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if len(_SOURCE_BY_ID) != len(WAVE8_ZULU_FORCES_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_ZULU_FORCES_ENTITIES}
    if len(entity_by_id) != len(WAVE8_ZULU_FORCES_ENTITIES):
        raise ValueError(f"{_LANE_NAME} duplicate entity id")
    if WAVE8_ZULU_FORCES_CONTRACT_IDS & WAVE8_ZULU_FORCES_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_ZULU_FORCES_RESERVED_IDS != WAVE8_ZULU_FORCES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation drift")
    if WAVE8_ZULU_FORCES_POINT_QUARANTINE_ADDITIONS != WAVE8_ZULU_FORCES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point review incomplete")
    if WAVE8_ZULU_FORCES_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    if set(WAVE8_ZULU_FORCES_LOCATION_QUARANTINE_REASONS) != WAVE8_ZULU_FORCES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for entity in WAVE8_ZULU_FORCES_ENTITIES:
        if entity["aliases"]:
            raise ValueError(f"{_LANE_NAME} opened a generic identity alias")
        if (entity["start_year"], entity["end_year"]) not in {(1888, 1888), (1906, 1906)}:
            raise ValueError(f"{_LANE_NAME} entity escaped conflict boundary")
        source_ids = list(map(str, entity["source_ids"]))
        if not source_ids or not _is_sorted_unique(source_ids):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(source_ids) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} entity references an unknown source")
        used_sources.update(source_ids)

    for candidate_id, contract in WAVE8_ZULU_FORCES_CONTRACTS.items():
        if contract["disposition"] != "promote" or contract["result_type"] != "win":
            raise ValueError(f"{_LANE_NAME} contract disposition drift: {candidate_id}")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} unexpected outcome override: {candidate_id}")
        for side_key in ("side_1_entity_ids", "side_2_entity_ids"):
            side = list(map(str, contract[side_key]))
            if not side or not set(side) <= set(entity_by_id):
                raise ValueError(f"{_LANE_NAME} unknown exact actor: {candidate_id}")
            used_entities.update(side)
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence is not canonical: {candidate_id}")
        if not set(outcomes) <= set(evidence) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} contains an unused entity fixture")
    if used_sources != set(_SOURCE_BY_ID):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_zulu_forces_audit_signature() != WAVE8_ZULU_FORCES_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_zulu_forces_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _EXACT_LABEL
        or normalize_label(row.get("side_2_raw")) == _EXACT_LABEL
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_ZULU_FORCES_EXPECTED_CANDIDATE_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_ZULU_FORCES_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("year_low") != row.get("year_high") or row.get("year_best") != row.get("year_low"):
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if row.get("winner_raw") not in {row.get("side_1_raw"), row.get("side_2_raw")}:
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True or row.get("massacre_raw") != "No":
            raise ValueError(f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ZULU_FORCES_CONTRACTS,
        WAVE8_ZULU_FORCES_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_zulu_forces_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    labels = [row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL]
    if len(labels) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    label = labels[0]
    checks = {
        "event_candidate_id_sha256": str(label.get("event_candidate_id_sha256")),
        "events_touched": int(label.get("events_touched", -1)),
        "label": str(label.get("label")),
        "sole_blocker_events": int(label.get("sole_blocker_events", -1)),
        "zero_time_valid_candidates": int(
            label.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
        ),
    }
    if checks != WAVE8_ZULU_FORCES_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed: {checks}")
    return {
        "events_touched": checks["events_touched"],
        "sole_blocker_events": checks["sole_blocker_events"],
        "zero_time_valid_candidates": checks["zero_time_valid_candidates"],
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "batyear"):
        value = row.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names: set[str] = set()
    for key in ("name", "battle_name", "batname", "event_name"):
        value = normalize_label(row.get(key))
        if value:
            names.add(value)
    for value in row.get("aliases", []) or []:
        normalized = normalize_label(value)
        if normalized:
            names.add(normalized)
    return names


_RAW_EVENT_NAMES = {
    "hced-Bobe1906-1": {"Bobe", "Bobe Ridge", "Bope Ridge"},
    "hced-Hlophekhulu1888-1": {"Hlophekhulu", "Hlopekhulu"},
    "hced-Ivuna1888-1": {"Ivuna", "Ndunu Hill"},
    "hced-Mome1906-1": {"Mome", "Mome Gorge", "Mhome Gorge"},
    "hced-Mpukonyoni1906-1": {"Mpukonyoni", "Mpukunyoni", "Mpukinyoni"},
}

_DUPLICATE_MATCH_KEYS = frozenset(
    (int(contract["canonical_event"]["year_low"]), normalize_label(alias))
    for candidate_id, contract in WAVE8_ZULU_FORCES_CONTRACTS.items()
    for alias in {
        contract["canonical_event"]["name"],
        *_RAW_EVENT_NAMES[candidate_id],
    }
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_zulu_forces_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_zulu_forces_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_ZULU_FORCES_EXPECTED_CANDIDATE_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_ZULU_FORCES_CONTRACT_IDS
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


def install_wave8_zulu_forces_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ZULU_FORCES_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_zulu_forces_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_ZULU_FORCES_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_ZULU_FORCES_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_ZULU_FORCES_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_zulu_forces_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_zulu_forces_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ZULU_FORCES_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_zulu_forces_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_ZULU_FORCES_CONTRACTS.values(),
                    *WAVE8_ZULU_FORCES_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_zulu_forces_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(WAVE8_ZULU_FORCES_COUNTRY_QUARANTINE_ADDITIONS),
        "holds": len(WAVE8_ZULU_FORCES_HOLDS),
        "new_entities": len(WAVE8_ZULU_FORCES_ENTITIES),
        "new_sources": len(WAVE8_ZULU_FORCES_SOURCES),
        "newly_rated_events": len(WAVE8_ZULU_FORCES_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(WAVE8_ZULU_FORCES_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_ZULU_FORCES_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_ZULU_FORCES_EXPECTED_CANDIDATE_IDS),
        "terminal_exclusions": 0,
    }


def wave8_zulu_forces_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_ZULU_FORCES_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_ZULU_FORCES_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_zulu_forces_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_zulu_forces_counts(),
        "cohorts": wave8_zulu_forces_cohort_counts(),
        "final_audit_signature": WAVE8_ZULU_FORCES_FINAL_AUDIT_SIGNATURE,
        "hold_ids": sorted(WAVE8_ZULU_FORCES_HOLD_IDS),
        "promoted_candidate_ids": sorted(WAVE8_ZULU_FORCES_CONTRACT_IDS),
    }


_validate_static()
