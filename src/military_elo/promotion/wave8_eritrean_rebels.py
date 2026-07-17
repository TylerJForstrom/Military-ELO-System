"""Candidate-keyed Wave 8 audit for HCED's exact ``Eritrean Rebels`` label.

The locked HCED queue contains four literal-label rows.  All four have direct,
independently cross-checked outcomes: the December 1977 EPLF assault on Massawa
was repulsed; Operation Fenkil captured Massawa in February 1990; the 1990-91
Dekemhare front ended in the town's capture; and Assab fell after the final
two-day offensive in May 1991.

This lane never turns ``Eritrean Rebels`` into a timeless polity.  It installs
four event- or campaign-bounded EPLF formations, reuses the already time-bounded
Ethiopia and Soviet Union entities, and explicitly remains disjoint from the
concurrent exact ``Eritrea`` lane and from Ethiopian/composite-rebel rows.
Unknown is never converted to a draw and no strategic war result is inferred.
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
    "WAVE8_ERITREAN_REBELS_CONTRACT_IDS",
    "WAVE8_ERITREAN_REBELS_CONTRACTS",
    "WAVE8_ERITREAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_ERITREAN_REBELS_ENTITIES",
    "WAVE8_ERITREAN_REBELS_EXCLUSION_IDS",
    "WAVE8_ERITREAN_REBELS_EXCLUSIONS",
    "WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_ERITREAN_REBELS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_ERITREAN_REBELS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS",
    "WAVE8_ERITREAN_REBELS_HCED_QUEUE_SHA256",
    "WAVE8_ERITREAN_REBELS_HOLD_IDS",
    "WAVE8_ERITREAN_REBELS_HOLDS",
    "WAVE8_ERITREAN_REBELS_INTEGRATION_DISPOSITIONS",
    "WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_ERITREAN_REBELS_IWBD_QUEUE_SHA256",
    "WAVE8_ERITREAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_ERITREAN_REBELS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_ERITREAN_REBELS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_ERITREAN_REBELS_NONPROMOTIONS",
    "WAVE8_ERITREAN_REBELS_OUTCOME_OVERRIDES",
    "WAVE8_ERITREAN_REBELS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS",
    "WAVE8_ERITREAN_REBELS_RESERVED_IDS",
    "WAVE8_ERITREAN_REBELS_ROW_HASHES",
    "WAVE8_ERITREAN_REBELS_SOURCES",
    "WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS",
    "install_wave8_eritrean_rebels_entities",
    "install_wave8_eritrean_rebels_sources",
    "promote_wave8_eritrean_rebels_contracts",
    "validate_wave8_eritrean_rebels_integration_dispositions",
    "validate_wave8_eritrean_rebels_queue_contracts",
    "wave8_eritrean_rebels_audit_signature",
    "wave8_eritrean_rebels_cohort_counts",
    "wave8_eritrean_rebels_counts",
    "wave8_eritrean_rebels_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Eritrean Rebels exact-actor audit"
_MODULE_OWNER = "wave8_eritrean_rebels"
_EVENT_ID_PREFIX = "hced_wave8_eritrean_rebels_"

_ETHIOPIA_ID = "clio_q115_1942_f6caec22"
_SOVIET_UNION_ID = "soviet_union"
_MASSAWA_1977_EPLF_ID = "eplf_massawa_assault_force_1977"
_FENKIL_EPLF_ID = "eplf_operation_fenkil_force_1990"
_DEKEMHARE_EPLF_ID = "eplf_dekemhare_front_force_1990_1991"
_ASSAB_EPLF_ID = "eplf_assab_offensive_force_1991"


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
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(roles)),
    }


WAVE8_ERITREAN_REBELS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_eritrean_rebels_africa_watch_evil_days",
        "Evil Days: 30 Years of War and Famine in Ethiopia",
        "https://opendata.uni-halle.de/bitstream/1981185920/108557/711/656410639.pdf",
        "Africa Watch / Human Rights Watch",
        "independent_contemporaneous_human_rights_history",
        "africa_watch_ethiopia_eritrea_reporting_1990_1991",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_eritrean_rebels_africa_watch_road_to_asmara",
        "The Road to Asmara: Eritrea, 1988-91",
        "https://www.hrw.org/reports/pdfs/e/ethiopia/ethiopia.919/d4afabet.pdf",
        "Africa Watch / Human Rights Watch",
        "independent_contemporaneous_human_rights_history",
        "africa_watch_ethiopia_eritrea_reporting_1990_1991",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_eritrean_rebels_hrw_world_report_1990",
        "World Report 1990: Ethiopia",
        "https://www.hrw.org/reports/1990/WR90/AFRICA.BOU-02.htm",
        "Human Rights Watch",
        "independent_contemporaneous_human_rights_report",
        "africa_watch_ethiopia_eritrea_reporting_1990_1991",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_eritrean_rebels_lrb_harding_1987",
        "Eritrean Revolution",
        "https://www.lrb.co.uk/the-paper/v09/n18/jeremy-harding/eritrean-revolution",
        "London Review of Books",
        "reported_historical_essay_with_field_observation",
        "harding_lrb_eritrean_revolution_1987",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_eritrean_rebels_frus_1978",
        "Eritrea: Prospects for the Coming Ethiopian Offensive",
        "https://history.state.gov/historicaldocuments/frus1977-80v17p1/d84",
        "U.S. Department of State, Office of the Historian",
        "declassified_contemporaneous_intelligence_assessment",
        "frus_horn_of_africa_1978_document_84",
        crosscheck=True,
    ),
    _source(
        "wave8_eritrean_rebels_tareke_massawa",
        "Massawa: The Denouement",
        "https://academic.oup.com/yale-scholarship-online/book/16340/chapter-abstract/171472017",
        "Yale University Press / Oxford Academic",
        "scholarly_military_history_book_chapter",
        "tareke_ethiopian_revolution_massawa_2009",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_eritrean_rebels_loc_country_study",
        "Ethiopia: Government Defeats in Eritrea and Tigray",
        "https://countrystudies.us/ethiopia/36.htm",
        "U.S. Library of Congress, Federal Research Division",
        "federal_country_study",
        "loc_ethiopia_country_study_1991",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_eritrean_rebels_wapo_eplf_communique",
        "For the Record: EPLF statement 'Eritrea Liberated at Last!!'",
        "https://www.washingtonpost.com/archive/opinions/1991/05/31/for-the-record/396ccebb-4a99-4abf-a35b-f8687caae4e7/",
        "The Washington Post; Eritrean People's Liberation Front",
        "published_belligerent_primary_communique",
        "eplf_27_may_1991_final_offensive_communique",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_eritrean_rebels_latimes_assab",
        "Ethiopia Rebels Take No. 2 City; Army Giving Up",
        "https://www.latimes.com/archives/la-xpm-1991-05-26-mn-3803-story.html",
        "Los Angeles Times",
        "contemporaneous_independent_newspaper_report",
        "hiltzik_latimes_26_may_1991",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_eritrean_rebels_yna_upi_assab",
        "Ethiopian rebels take complete control of northern region",
        "https://www.yna.co.kr/view/AKR19910526000200009",
        "United Press International / Yonhap News Agency archive",
        "contemporaneous_wire_service_archive",
        "upi_wire_assab_25_may_1991",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_eritrean_rebels_ayele_ethiopian_army",
        "The Ethiopian Army: From Victory to Collapse, 1977-1991",
        "https://nupress.northwestern.edu/9780810168053/the-ethiopian-army/",
        "Northwestern University Press",
        "scholarly_military_history_monograph",
        "ayele_ethiopian_army_2014",
        crosscheck=True,
    ),
    _source(
        "wave8_eritrean_rebels_un_coi_history",
        "Detailed findings of the Commission of Inquiry on Human Rights in Eritrea, chapter III",
        "https://www.ohchr.org/Documents/HRBodies/HRCouncil/CoIEritrea/A_HRC_29_CRP-1_Chapter_III.pdf",
        "United Nations Human Rights Council",
        "united_nations_commission_history",
        "un_coi_eritrea_chapter_iii",
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_ERITREAN_REBELS_SOURCES
}
_SOURCE_FAMILY_BY_ID = {
    source_id: str(source["source_family_id"])
    for source_id, source in _SOURCE_BY_ID.items()
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    low: int,
    high: int,
    source_ids: Iterable[str],
    note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": low,
        "end_year": high,
        "region": "Eritrea",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            note
            + " No rating is inherited by the Eritrean Liberation Front (ELF), "
            "a generic Eritrean Rebels label, civilians, another EPLF formation, "
            "the Provisional Government, PFDJ, or the State of Eritrea."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_ERITREAN_REBELS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _MASSAWA_1977_EPLF_ID,
        "EPLF Massawa Assault Force (December 1977)",
        "engagement_bounded_insurgent_assault_force",
        1977,
        1977,
        {
            "wave8_eritrean_rebels_africa_watch_evil_days",
            "wave8_eritrean_rebels_lrb_harding_1987",
            "wave8_eritrean_rebels_un_coi_history",
        },
        (
            "Engagement-bounded EPLF force that stormed the remaining Ethiopian "
            "port positions at Massawa and was repulsed in December 1977."
        ),
    ),
    _entity(
        _FENKIL_EPLF_ID,
        "EPLF Operation Fenkil Force (8-10 February 1990)",
        "engagement_bounded_combined_arms_force",
        1990,
        1990,
        {
            "wave8_eritrean_rebels_africa_watch_road_to_asmara",
            "wave8_eritrean_rebels_tareke_massawa",
            "wave8_eritrean_rebels_un_coi_history",
        },
        (
            "Engagement-bounded EPLF land and maritime force that captured "
            "Massawa during Operation Fenkil."
        ),
    ),
    _entity(
        _DEKEMHARE_EPLF_ID,
        "EPLF Dekemhare Front Force (1990-1991)",
        "campaign_bounded_insurgent_front",
        1990,
        1991,
        {
            "wave8_eritrean_rebels_africa_watch_road_to_asmara",
            "wave8_eritrean_rebels_loc_country_study",
            "wave8_eritrean_rebels_un_coi_history",
            "wave8_eritrean_rebels_wapo_eplf_communique",
        },
        (
            "Campaign-bounded EPLF formation on the Dekemhare front from the "
            "1990 fighting through the May 1991 encirclement and capture."
        ),
    ),
    _entity(
        _ASSAB_EPLF_ID,
        "EPLF Assab Offensive Force (24-25 May 1991)",
        "engagement_bounded_insurgent_offensive_force",
        1991,
        1991,
        {
            "wave8_eritrean_rebels_africa_watch_evil_days",
            "wave8_eritrean_rebels_latimes_assab",
            "wave8_eritrean_rebels_un_coi_history",
            "wave8_eritrean_rebels_wapo_eplf_communique",
            "wave8_eritrean_rebels_yna_upi_assab",
        },
        (
            "Engagement-bounded EPLF force that completed the Danakil advance and "
            "captured the final Ethiopian-held port at Assab."
        ),
    ),
)


WAVE8_ERITREAN_REBELS_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_ERITREAN_REBELS_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)
WAVE8_ERITREAN_REBELS_ROW_HASHES: dict[str, str] = {
    "hced-Addis Ababa1991-1": "c743004579d8037cec5b470037779bdebac698c21cfe11a3c44413f52fe36538",
    "hced-Asosa1990-1991-1": "3fce1e2431ad7cc42e1122493e6b91c29f1a16d6a96e914c703e3316a45359f7",
    "hced-Assab1991-1": "eae47486367be08330cf39f1b9c5c25b97445da5689bd73ff9ccc9a520b1284a",
    "hced-Dekemhare1990-1991-1": "0e37854dff6227ee9a8f332bae75a58678331bd18a25df40e13609c7858ff562",
    "hced-Inda Silase1989-1": "4a4ea3108666d6399002a7d7b37bdc834ce467fe0e3b46b8d76b960b4a2f42f0",
    "hced-Massawa1941-1": "086dfc15ad7234ce0e09634f029133accd9db18f3781ab8082f222babe5b7d6c",
    "hced-Massawa1977-1": "fc2d47d47d86252bbb428cad1899fc1e0985a43aae0c53b2fad6393e979b188c",
    "hced-Massawa1990-1": "7fc9e9a0dc9accc6a1c85386f31a43538248d5f125b250230b127cfa80517199",
}


def _canonical(
    name: str,
    low: int,
    high: int,
    date_text: str,
    date_precision: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{low}:{high}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": low,
        "year_high": high,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    reviewed_sides: Iterable[str],
    reviewed_outcome: str,
    event_boundary: str,
    event_type: str,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_ERITREAN_REBELS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "civil_war",
        "event_type": event_type,
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "direct_provenance": {
            "reviewed_date": canonical_event["date_text"],
            "reviewed_sides": list(map(str, reviewed_sides)),
            "reviewed_outcome": reviewed_outcome,
            "event_boundary": event_boundary,
        },
        "audit_note": audit_note,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
    }


WAVE8_ERITREAN_REBELS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Massawa1977-1": _contract(
        "hced-Massawa1977-1",
        _canonical(
            "First Battle of Massawa",
            1977,
            1977,
            "December 1977",
            "month",
            "engagement",
        ),
        "first_massawa_battle_1977",
        [_ETHIOPIA_ID, _SOVIET_UNION_ID],
        [_MASSAWA_1977_EPLF_ID],
        1,
        {
            "wave8_eritrean_rebels_africa_watch_evil_days",
            "wave8_eritrean_rebels_ayele_ethiopian_army",
            "wave8_eritrean_rebels_frus_1978",
            "wave8_eritrean_rebels_lrb_harding_1987",
            "wave8_eritrean_rebels_un_coi_history",
        },
        {
            "wave8_eritrean_rebels_africa_watch_evil_days",
            "wave8_eritrean_rebels_lrb_harding_1987",
        },
        (
            "Africa Watch records that the EPLF stormed Massawa and was repulsed "
            "with heavy casualties. Harding independently records Soviet vessels "
            "shelling the EPLF positions, so HCED's Ethiopian-Soviet winning side "
            "is retained without extending either actor beyond this engagement."
        ),
        reviewed_sides=[
            "Ethiopian Massawa garrison with Soviet naval fire support",
            "EPLF Massawa assault force",
        ],
        reviewed_outcome="Ethiopian-Soviet defensive victory; EPLF assault repulsed",
        event_boundary="December 1977 assault on the remaining port and pier positions",
        event_type="engagement",
        confidence=0.93,
    ),
    "hced-Massawa1990-1": _contract(
        "hced-Massawa1990-1",
        _canonical(
            "Second Battle of Massawa (Operation Fenkil)",
            1990,
            1990,
            "8-10 February 1990",
            "day_range",
            "engagement",
        ),
        "operation_fenkil_1990",
        [_FENKIL_EPLF_ID],
        [_ETHIOPIA_ID],
        1,
        {
            "wave8_eritrean_rebels_africa_watch_road_to_asmara",
            "wave8_eritrean_rebels_hrw_world_report_1990",
            "wave8_eritrean_rebels_tareke_massawa",
            "wave8_eritrean_rebels_un_coi_history",
        },
        {
            "wave8_eritrean_rebels_africa_watch_road_to_asmara",
            "wave8_eritrean_rebels_tareke_massawa",
        },
        (
            "Independent reporting and military history agree that the EPLF "
            "launched on 8 February and captured Massawa after a three-day battle. "
            "The contract ends with the port's capture and does not convert later "
            "bombardment or the war's final outcome into additional victories."
        ),
        reviewed_sides=[
            "EPLF Operation Fenkil land and maritime force",
            "Ethiopian Massawa garrison and relief forces",
        ],
        reviewed_outcome="EPLF tactical victory and capture of Massawa",
        event_boundary="8-10 February surprise attack, island defeat, and port capture",
        event_type="engagement",
        confidence=0.98,
    ),
    "hced-Dekemhare1990-1991-1": _contract(
        "hced-Dekemhare1990-1991-1",
        _canonical(
            "Dekemhare front campaign and capture",
            1990,
            1991,
            "August 1990-May 1991; final capture reported 19-24 May",
            "year_range_end_day_variance",
            "campaign",
        ),
        "dekemhare_front_1990_1991",
        [_DEKEMHARE_EPLF_ID],
        [_ETHIOPIA_ID],
        1,
        {
            "wave8_eritrean_rebels_africa_watch_road_to_asmara",
            "wave8_eritrean_rebels_ayele_ethiopian_army",
            "wave8_eritrean_rebels_loc_country_study",
            "wave8_eritrean_rebels_un_coi_history",
            "wave8_eritrean_rebels_wapo_eplf_communique",
        },
        {
            "wave8_eritrean_rebels_africa_watch_road_to_asmara",
            "wave8_eritrean_rebels_loc_country_study",
            "wave8_eritrean_rebels_wapo_eplf_communique",
        },
        (
            "The raw two-year interval is retained as an operational front, not "
            "collapsed into an invented point battle. Sources attest 1990 fighting, "
            "a final EPLF assault, the surrounding and capture of reinforcements, "
            "and the town's capture; contemporary accounts vary between 19 and 24 "
            "May for the endpoint, so no false day precision is chosen."
        ),
        reviewed_sides=[
            "EPLF Dekemhare front and final-offensive force",
            "Ethiopian Dekemhare garrison and Asmara reinforcements",
        ],
        reviewed_outcome="EPLF campaign victory; Dekemhare and reinforcements captured",
        event_boundary="1990 front fighting through the May 1991 capture of Dekemhare",
        event_type="campaign",
        confidence=0.91,
    ),
    "hced-Assab1991-1": _contract(
        "hced-Assab1991-1",
        _canonical(
            "Siege and capture of Assab",
            1991,
            1991,
            "24-25 May 1991",
            "day_range",
            "engagement",
        ),
        "final_assab_offensive_1991",
        [_ASSAB_EPLF_ID],
        [_ETHIOPIA_ID],
        1,
        {
            "wave8_eritrean_rebels_africa_watch_evil_days",
            "wave8_eritrean_rebels_africa_watch_road_to_asmara",
            "wave8_eritrean_rebels_ayele_ethiopian_army",
            "wave8_eritrean_rebels_latimes_assab",
            "wave8_eritrean_rebels_un_coi_history",
            "wave8_eritrean_rebels_wapo_eplf_communique",
            "wave8_eritrean_rebels_yna_upi_assab",
        },
        {
            "wave8_eritrean_rebels_africa_watch_evil_days",
            "wave8_eritrean_rebels_latimes_assab",
            "wave8_eritrean_rebels_wapo_eplf_communique",
            "wave8_eritrean_rebels_yna_upi_assab",
        },
        (
            "Africa Watch independently confirms the EPLF's Danakil advance and "
            "the subsequent taking of Assab. Contemporary reports identify a "
            "two-day siege/offensive ending on 25 May. The rated result is that "
            "bounded final stronghold action, not the political transfer of all "
            "Eritrea or the collapse of the Ethiopian government."
        ),
        reviewed_sides=[
            "EPLF Assab offensive force",
            "Ethiopian Assab port garrison",
        ],
        reviewed_outcome="EPLF tactical victory and capture of Assab",
        event_boundary="24-25 May two-day offensive against the final Assab stronghold",
        event_type="engagement",
        confidence=0.94,
    ),
}


WAVE8_ERITREAN_REBELS_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_ERITREAN_REBELS_EXCLUSIONS = WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS
WAVE8_ERITREAN_REBELS_NONPROMOTIONS: dict[str, dict[str, Any]] = {}

WAVE8_ERITREAN_REBELS_CONTRACT_IDS = frozenset(
    WAVE8_ERITREAN_REBELS_CONTRACTS
)
WAVE8_ERITREAN_REBELS_HOLD_IDS = frozenset(WAVE8_ERITREAN_REBELS_HOLDS)
WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS
)
WAVE8_ERITREAN_REBELS_EXCLUSION_IDS = (
    WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSION_IDS
)
WAVE8_ERITREAN_REBELS_RESERVED_IDS = frozenset(
    WAVE8_ERITREAN_REBELS_CONTRACT_IDS
    | WAVE8_ERITREAN_REBELS_HOLD_IDS
    | WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSION_IDS
)
WAVE8_ERITREAN_REBELS_EXPECTED_CANDIDATE_IDS = frozenset(
    {
        "hced-Assab1991-1",
        "hced-Dekemhare1990-1991-1",
        "hced-Massawa1977-1",
        "hced-Massawa1990-1",
    }
)


WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Addis Ababa1991-1": {
        "raw_row_sha256": WAVE8_ERITREAN_REBELS_ROW_HASHES[
            "hced-Addis Ababa1991-1"
        ],
        "disposition": "separate_ethiopian_rebel_coalition_lane",
        "raw_labels": ["Ethiopia", "Ethiopian Rebels"],
        "reason": (
            "The EPRDF/TPLF-led Addis Ababa action is not an EPLF-only event; "
            "cooperation between fronts cannot transfer ownership or Elo."
        ),
        "evidence_refs": [
            "wave8_eritrean_rebels_africa_watch_evil_days",
            "wave8_eritrean_rebels_un_coi_history",
        ],
    },
    "hced-Asosa1990-1991-1": {
        "raw_row_sha256": WAVE8_ERITREAN_REBELS_ROW_HASHES[
            "hced-Asosa1990-1991-1"
        ],
        "disposition": "separate_oromo_eritrean_composite_lane",
        "raw_labels": ["Ethiopia", "Oromo Rebels, Eritrea"],
        "reason": (
            "The composite Oromo/Eritrean side requires its own coalition audit "
            "and is not reduced to this exact EPLF actor lane."
        ),
        "evidence_refs": [
            "wave8_eritrean_rebels_africa_watch_road_to_asmara",
            "wave8_eritrean_rebels_un_coi_history",
        ],
    },
    "hced-Inda Silase1989-1": {
        "raw_row_sha256": WAVE8_ERITREAN_REBELS_ROW_HASHES[
            "hced-Inda Silase1989-1"
        ],
        "disposition": "separate_tigrayan_eritrean_composite_lane",
        "raw_labels": ["Ethiopia", "Tigrayan Rebels, Eritrea"],
        "reason": (
            "The TPLF/EPLF composite force is not an EPLF-only formation and "
            "cannot inherit one of this lane's campaign identities."
        ),
        "evidence_refs": [
            "wave8_eritrean_rebels_tareke_massawa",
            "wave8_eritrean_rebels_un_coi_history",
        ],
    },
}

_EXACT_ERITREA_OTHER_LANE_IDS = frozenset(
    {
        "hced-Afabet1988-1",
        "hced-Badme1998-1",
        "hced-Badme1999-1",
        "hced-Barentu1985-1",
        "hced-Barentu2000-1",
        "hced-Keren1977-1978-1",
        "hced-Nakfa1977-1988-1",
        "hced-Tsorona1999-1",
    }
)
WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "wave8_eritrea": {
        "disposition": "disjoint_exact_labels_and_candidate_ownership",
        "other_module": "wave8_eritrea",
        "owned_candidate_ids": sorted(WAVE8_ERITREAN_REBELS_RESERVED_IDS),
        "other_exact_candidate_ids": sorted(_EXACT_ERITREA_OTHER_LANE_IDS),
        "reason": (
            "The exact Eritrea lane owns only literal Eritrea rows and explicitly "
            "marks all four literal Eritrean Rebels rows for this separate audit."
        ),
        "evidence_refs": [
            "wave8_eritrean_rebels_africa_watch_evil_days",
            "wave8_eritrean_rebels_un_coi_history",
        ],
    },
    "ethiopia_related_rows": {
        "disposition": "outside_exact_eritrean_rebels_lane",
        "other_module": "future_candidate_keyed_composite_lanes",
        "owned_candidate_ids": sorted(WAVE8_ERITREAN_REBELS_RESERVED_IDS),
        "other_candidate_ids": sorted(
            WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS
        ),
        "reason": (
            "Generic Ethiopian Rebels and Oromo/Tigrayan composite rows need "
            "their own actor and outcome boundaries; this lane claims none."
        ),
        "evidence_refs": [
            "wave8_eritrean_rebels_africa_watch_road_to_asmara",
            "wave8_eritrean_rebels_un_coi_history",
        ],
    },
}


WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "hced-Massawa1941-1": {
        "raw_row_sha256": WAVE8_ERITREAN_REBELS_ROW_HASHES[
            "hced-Massawa1941-1"
        ],
        "disposition": "same_place_name_distinct_world_war_two_battle",
        "expected_name": "Massawa",
        "expected_year_low": 1941,
        "expected_year_high": 1941,
        "related_owner_candidate_ids": [
            "hced-Massawa1977-1",
            "hced-Massawa1990-1",
        ],
        "reason": (
            "The 1941 British/Free French capture from Italy is separated by "
            "decades, belligerents, and war from both Eritrean-independence rows."
        ),
        "evidence_refs": ["wave8_eritrean_rebels_tareke_massawa"],
    }
}
WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "iwbd-139-53-961": {
        "disposition": "same_place_name_distinct_world_war_two_battle",
        "expected_name": "Massawa",
        "expected_start_date": "1941-04-08",
        "expected_end_date": "1941-04-08",
        "expected_winner_raw": "Allies",
        "related_owner_candidate_ids": [
            "hced-Massawa1977-1",
            "hced-Massawa1990-1",
        ],
        "reason": "IWBD's 1941 Allies-Axis battle is not either EPLF Massawa action.",
        "evidence_refs": ["wave8_eritrean_rebels_tareke_massawa"],
    }
}
WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "hced_hced_massawa1941_1": {
        "disposition": "existing_distinct_world_war_two_event",
        "expected_hced_candidate_id": "hced-Massawa1941-1",
        "expected_name": "Massawa",
        "expected_year": 1941,
        "related_owner_candidate_ids": [
            "hced-Massawa1977-1",
            "hced-Massawa1990-1",
        ],
        "reason": "The released 1941 event remains a distinct, valid event.",
        "evidence_refs": ["wave8_eritrean_rebels_tareke_massawa"],
    }
}

WAVE8_ERITREAN_REBELS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"cross_lane:{key}": value
        for key, value in WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS.items()
    },
    **{
        f"related_hced:{key}": value
        for key, value in WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS.items()
    },
    **{
        f"hced_duplicate:{key}": value
        for key, value in WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS.items()
    },
    **{
        f"iwbd_duplicate:{key}": value
        for key, value in WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS.items()
    },
    **{
        f"existing_release:{key}": value
        for key, value in (
            WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
        )
    },
}

WAVE8_ERITREAN_REBELS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


WAVE8_ERITREAN_REBELS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_ERITREAN_REBELS_CONTRACT_IDS
)
WAVE8_ERITREAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_ERITREAN_REBELS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_ERITREAN_REBELS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_ERITREAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_ERITREAN_REBELS_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    "hced-Assab1991-1": {
        "actions": ["withhold_point"],
        "reference_source_ids": [
            "wave8_eritrean_rebels_africa_watch_evil_days",
            "wave8_eritrean_rebels_wapo_eplf_communique",
            "wave8_eritrean_rebels_yna_upi_assab",
        ],
        "reason": (
            "A modern Assab locality point cannot identify the port garrison, "
            "siege perimeter, naval facilities, and two-day offensive footprint."
        ),
    },
    "hced-Dekemhare1990-1991-1": {
        "actions": ["withhold_point"],
        "reference_source_ids": [
            "wave8_eritrean_rebels_africa_watch_road_to_asmara",
            "wave8_eritrean_rebels_loc_country_study",
        ],
        "reason": (
            "The town centroid cannot represent the 1990-91 front, assault axes, "
            "surrounded reinforcement column, and final capture footprint."
        ),
    },
    "hced-Massawa1977-1": {
        "actions": ["withhold_point"],
        "reference_source_ids": [
            "wave8_eritrean_rebels_africa_watch_evil_days",
            "wave8_eritrean_rebels_lrb_harding_1987",
        ],
        "reason": (
            "A city point cannot identify the occupied districts, long pier, port "
            "positions, Soviet offshore fire, and EPLF assault footprint."
        ),
    },
    "hced-Massawa1990-1": {
        "actions": ["withhold_point"],
        "reference_source_ids": [
            "wave8_eritrean_rebels_africa_watch_road_to_asmara",
            "wave8_eritrean_rebels_tareke_massawa",
        ],
        "reason": (
            "Operation Fenkil covered approaches, the port, islands, sea action, "
            "and relief routes; a city centroid is falsely precise."
        ),
    },
}


WAVE8_ERITREAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT: dict[
    str, dict[str, Any]
] = {
    "hced-Assab1991-1": {
        "aliases": sorted(
            {"aseb", "assab", "asseb", "capture of assab", "siege and capture of assab"}
        ),
        "years": [1991, 1991],
    },
    "hced-Dekemhare1990-1991-1": {
        "aliases": sorted(
            {
                "decamhare",
                "decamere",
                "dekemhare",
                "dekemhare front campaign and capture",
            }
        ),
        "years": [1990, 1991],
    },
    "hced-Massawa1977-1": {
        "aliases": sorted(
            {"battle of massawa", "first battle of massawa", "massawa", "mitsiwa"}
        ),
        "years": [1977, 1977],
    },
    "hced-Massawa1990-1": {
        "aliases": sorted(
            {
                "massawa",
                "mitsiwa",
                "operation fenkil",
                "second battle of massawa",
                "second battle of massawa operation fenkil",
            }
        ),
        "years": [1990, 1990],
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_ERITREAN_REBELS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_ERITREAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_ERITREAN_REBELS_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(
            WAVE8_ERITREAN_REBELS_EXPECTED_CANDIDATE_IDS
        ),
        "hced_duplicate_dispositions": (
            WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS
        ),
        "holds": WAVE8_ERITREAN_REBELS_HOLDS,
        "integration_dispositions": WAVE8_ERITREAN_REBELS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": (
            WAVE8_ERITREAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "location_quarantine_reasons": (
            WAVE8_ERITREAN_REBELS_LOCATION_QUARANTINE_REASONS
        ),
        "outcome_overrides": WAVE8_ERITREAN_REBELS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_ERITREAN_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": (
            WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS
        ),
        "row_hashes": WAVE8_ERITREAN_REBELS_ROW_HASHES,
        "sources": WAVE8_ERITREAN_REBELS_SOURCES,
        "terminal_exclusions": WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS,
    }


def wave8_eritrean_rebels_audit_signature() -> str:
    """Return the immutable digest of the complete lane adjudication."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_ERITREAN_REBELS_FINAL_AUDIT_SIGNATURE = (
    "af9e1fa773b2781781f953c3277ad0212daa0b1714bfaebc02cd18afae83fbc6"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    materialized = list(map(str, values))
    return materialized == sorted(set(materialized))


def _validate_static() -> None:
    if (
        len(WAVE8_ERITREAN_REBELS_CONTRACTS),
        len(WAVE8_ERITREAN_REBELS_HOLDS),
        len(WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS),
        len(WAVE8_ERITREAN_REBELS_ENTITIES),
        len(WAVE8_ERITREAN_REBELS_SOURCES),
    ) != (4, 0, 0, 4, 12):
        raise ValueError(f"{_LANE_NAME} inventory changed")
    if WAVE8_ERITREAN_REBELS_RESERVED_IDS != (
        WAVE8_ERITREAN_REBELS_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} ownership is incomplete")
    if wave8_eritrean_rebels_audit_signature() != (
        WAVE8_ERITREAN_REBELS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_ids = [str(source["id"]) for source in WAVE8_ERITREAN_REBELS_SOURCES]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_ERITREAN_REBELS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_ERITREAN_REBELS_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_ERITREAN_REBELS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_ids = {
        _ETHIOPIA_ID,
        _SOVIET_UNION_ID,
        "eplf",
        "eritrea",
        "eritrean_rebels",
    }
    if set(entity_by_id) & forbidden_ids:
        raise ValueError(f"{_LANE_NAME} opened a generic identity bridge")
    expected_windows = {
        _MASSAWA_1977_EPLF_ID: (1977, 1977),
        _FENKIL_EPLF_ID: (1990, 1990),
        _DEKEMHARE_EPLF_ID: (1990, 1991),
        _ASSAB_EPLF_ID: (1991, 1991),
    }
    for entity_id, entity in entity_by_id.items():
        if (entity["start_year"], entity["end_year"]) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} entity window drifted")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} entity opens a label fallback")
        note = str(entity["continuity_note"]).casefold()
        for phrase in (
            "no rating is inherited",
            "generic eritrean rebels",
            "state of eritrea",
            "another eplf formation",
        ):
            if phrase not in note:
                raise ValueError(f"{_LANE_NAME} continuity firewall is incomplete")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} entity cites an unknown source")

    expected_contracts = {
        "hced-Assab1991-1": (
            1991,
            1991,
            [_ASSAB_EPLF_ID],
            [_ETHIOPIA_ID],
            1,
            "engagement",
        ),
        "hced-Dekemhare1990-1991-1": (
            1990,
            1991,
            [_DEKEMHARE_EPLF_ID],
            [_ETHIOPIA_ID],
            1,
            "campaign",
        ),
        "hced-Massawa1977-1": (
            1977,
            1977,
            [_ETHIOPIA_ID, _SOVIET_UNION_ID],
            [_MASSAWA_1977_EPLF_ID],
            1,
            "engagement",
        ),
        "hced-Massawa1990-1": (
            1990,
            1990,
            [_FENKIL_EPLF_ID],
            [_ETHIOPIA_ID],
            1,
            "engagement",
        ),
    }
    if set(WAVE8_ERITREAN_REBELS_CONTRACTS) != set(expected_contracts):
        raise ValueError(f"{_LANE_NAME} contract inventory changed")
    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, expected in expected_contracts.items():
        contract = WAVE8_ERITREAN_REBELS_CONTRACTS[candidate_id]
        low, high, side_1, side_2, winner_side, event_type = expected
        if contract["raw_row_sha256"] != WAVE8_ERITREAN_REBELS_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract hash drifted")
        canonical = contract["canonical_event"]
        canonical_key = f"{_slug(str(canonical['name']))}:{low}:{high}"
        if (
            canonical["canonical_key"] != canonical_key
            or canonical["year_low"] != low
            or canonical["year_high"] != high
            or canonical["granularity"] != event_type
            or not canonical["date_text"]
        ):
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if (
            contract["side_1_entity_ids"] != side_1
            or contract["side_2_entity_ids"] != side_2
            or contract["winner_side"] != winner_side
            or contract["event_type"] != event_type
        ):
            raise ValueError(f"{_LANE_NAME} actor contract drifted")
        participants = set(side_1) | set(side_2)
        new_participants = participants & set(entity_by_id)
        if len(new_participants) != 1 or _ETHIOPIA_ID not in participants:
            raise ValueError(f"{_LANE_NAME} actor boundary drifted")
        if candidate_id == "hced-Massawa1977-1":
            if _SOVIET_UNION_ID not in participants:
                raise ValueError(f"{_LANE_NAME} lost attested Soviet participation")
        elif _SOVIET_UNION_ID in participants:
            raise ValueError(f"{_LANE_NAME} invented Soviet participation")
        for entity_id in new_participants:
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= low <= high <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an entity window")
        used_entities.update(new_participants)
        if (
            contract["result_type"] != "win"
            or contract["war_type"] != "civil_war"
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"] is not True
            or contract["duplicate_ownership"]
            != {"owner_module": _MODULE_OWNER, "status": "canonical_hced_owner"}
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if (
            len(outcomes) < 2
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in _SOURCE_BY_ID[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} cites non-outcome evidence")
        expected_families = sorted({_SOURCE_FAMILY_BY_ID[item] for item in outcomes})
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome sources are not independent")
        provenance = contract["direct_provenance"]
        if (
            not provenance["reviewed_date"]
            or not provenance["reviewed_sides"]
            or not provenance["reviewed_outcome"]
            or not provenance["event_boundary"]
        ):
            raise ValueError(f"{_LANE_NAME} direct provenance is incomplete")
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")

    if set(WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS) != {
        "hced-Addis Ababa1991-1",
        "hced-Asosa1990-1991-1",
        "hced-Inda Silase1989-1",
    }:
        raise ValueError(f"{_LANE_NAME} related HCED inventory changed")
    for candidate_id, item in WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS.items():
        if item["raw_row_sha256"] != WAVE8_ERITREAN_REBELS_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} related HCED hash drifted")
        refs = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} related HCED evidence drifted")
        used_sources.update(refs)

    if set(WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS) != {
        "ethiopia_related_rows",
        "wave8_eritrea",
    }:
        raise ValueError(f"{_LANE_NAME} cross-lane inventory changed")
    for item in WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS.values():
        if set(item["owned_candidate_ids"]) != WAVE8_ERITREAN_REBELS_RESERVED_IDS:
            raise ValueError(f"{_LANE_NAME} cross-lane ownership drifted")
        refs = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} cross-lane evidence drifted")
        used_sources.update(refs)

    if set(WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS) != {
        "hced-Massawa1941-1"
    }:
        raise ValueError(f"{_LANE_NAME} HCED duplicate inventory changed")
    if set(WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS) != {
        "iwbd-139-53-961"
    }:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    if set(WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS) != {
        "hced_hced_massawa1941_1"
    }:
        raise ValueError(f"{_LANE_NAME} release duplicate inventory changed")
    for inventory in (
        WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS,
        WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
        WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    ):
        for item in inventory.values():
            refs = list(map(str, item["evidence_refs"]))
            if not _is_sorted_unique(refs) or not set(refs) <= set(_SOURCE_BY_ID):
                raise ValueError(f"{_LANE_NAME} duplicate evidence drifted")
            used_sources.update(refs)

    used_sources.update(
        source_id
        for entity in WAVE8_ERITREAN_REBELS_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if WAVE8_ERITREAN_REBELS_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_ERITREAN_REBELS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_ERITREAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_ERITREAN_REBELS_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_ERITREAN_REBELS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    for item in WAVE8_ERITREAN_REBELS_LOCATION_QUARANTINE_REASONS.values():
        if item["actions"] != ["withhold_point"] or not item["reason"]:
            raise ValueError(f"{_LANE_NAME} location action drifted")
        if not set(item["reference_source_ids"]) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} location review cites an unknown source")
        used_sources.update(map(str, item["reference_source_ids"]))

    if WAVE8_ERITREAN_REBELS_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} acquired an outcome override")
    if set(WAVE8_ERITREAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_ERITREAN_REBELS_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for candidate_id, audit in WAVE8_ERITREAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT.items():
        aliases = list(map(str, audit["aliases"]))
        years = list(map(int, audit["years"]))
        if not aliases or not _is_sorted_unique(aliases):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if any(alias != normalize_label(alias) for alias in aliases):
            raise ValueError(f"{_LANE_NAME} duplicate alias is not normalized")
        if years != sorted(years) or len(years) != 2:
            raise ValueError(f"{_LANE_NAME} duplicate year window drifted")
        canonical = WAVE8_ERITREAN_REBELS_CONTRACTS[candidate_id]["canonical_event"]
        key = (int(canonical["year_low"]), normalize_label(canonical["name"]))
        audited = {
            (year, alias)
            for year in range(years[0], years[1] + 1)
            for alias in aliases
        }
        if key not in audited:
            raise ValueError(f"{_LANE_NAME} canonical duplicate audit is incomplete")

    if used_sources != set(_SOURCE_BY_ID):
        raise ValueError(
            f"{_LANE_NAME} sources are not exactly consumed; "
            f"missing={sorted(set(_SOURCE_BY_ID) - used_sources)}"
        )


def _rows_by_id(
    rows: Iterable[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        result.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    return result


def _validate_hced_fingerprint(
    indexed: Mapping[str, list[dict[str, Any]]], candidate_id: str
) -> None:
    rows = indexed.get(candidate_id, [])
    if len(rows) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one HCED row {candidate_id}, found {len(rows)}"
        )
    if canonical_hced_row_sha256(rows[0]) != WAVE8_ERITREAN_REBELS_ROW_HASHES[candidate_id]:
        raise ValueError(f"{_LANE_NAME} HCED fingerprint changed for {candidate_id}")


def validate_wave8_eritrean_rebels_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all and only the four exact-label rows and adjacent boundaries."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ERITREAN_REBELS_CONTRACTS,
        WAVE8_ERITREAN_REBELS_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    indexed = _rows_by_id(hced_rows)
    for candidate_id in WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS:
        _validate_hced_fingerprint(indexed, candidate_id)

    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == "eritrean rebels"
        or normalize_label(row.get("side_2_raw")) == "eritrean rebels"
    }
    if exact_ids != WAVE8_ERITREAN_REBELS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Eritrean Rebels inventory changed: "
            f"{sorted(exact_ids)}"
        )
    for candidate_id, contract in WAVE8_ERITREAN_REBELS_CONTRACTS.items():
        row = indexed[candidate_id][0]
        winner_side = int(contract["winner_side"])
        if row.get("winner_loser_complete") is not True:
            raise ValueError(f"{_LANE_NAME} incomplete outcome for {candidate_id}")
        if normalize_label(row.get("winner_raw")) in {
            "",
            "draw",
            "inconclusive",
            "stalemate",
        }:
            raise ValueError(f"{_LANE_NAME} unknown/draw outcome drifted")
        if row.get("winner_raw") != row.get(f"side_{winner_side}_raw"):
            raise ValueError(f"{_LANE_NAME} winner drifted for {candidate_id}")
        if row.get("loser_raw") != row.get(f"side_{3 - winner_side}_raw"):
            raise ValueError(f"{_LANE_NAME} loser drifted for {candidate_id}")
    return {
        "holds": result["holds"],
        "promotion_contracts": result["promotion_contracts"],
        "related_hced_dispositions": len(
            WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(
            WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS
        ),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        value = row.get(field)
        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        value = str(row.get(field) or "")
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


_DUPLICATE_MATCH_KEYS = {
    (year, alias)
    for audit in WAVE8_ERITREAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
}


def validate_wave8_eritrean_rebels_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin neighboring ownership and fail closed on any undeclared twin."""

    validate_wave8_eritrean_rebels_queue_contracts(hced_rows)
    hced_by_id = _rows_by_id(hced_rows)

    # Local import avoids initialization coupling while making the reciprocal
    # ownership boundary executable once the concurrent lane is present.
    from .wave8_eritrea import (
        WAVE8_ERITREA_ENTITIES,
        WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS,
        WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS,
    )

    if set(WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS) != _EXACT_ERITREA_OTHER_LANE_IDS:
        raise ValueError(f"{_LANE_NAME} concurrent exact Eritrea inventory changed")
    overlap = WAVE8_ERITREAN_REBELS_RESERVED_IDS & set(
        WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS
    )
    if overlap:
        raise ValueError(
            f"{_LANE_NAME} candidate collision with wave8_eritrea: {sorted(overlap)}"
        )
    expected_reciprocal = (
        WAVE8_ERITREAN_REBELS_RESERVED_IDS
        | set(WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS)
    )
    if not expected_reciprocal <= set(WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS):
        raise ValueError(f"{_LANE_NAME} reciprocal Eritrea boundary changed")
    for candidate_id in expected_reciprocal:
        if (
            WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS[candidate_id]["raw_row_sha256"]
            != WAVE8_ERITREAN_REBELS_ROW_HASHES[candidate_id]
        ):
            raise ValueError(f"{_LANE_NAME} reciprocal row hash changed")
    other_entity_ids = {str(entity["id"]) for entity in WAVE8_ERITREA_ENTITIES}
    own_entity_ids = {str(entity["id"]) for entity in WAVE8_ERITREAN_REBELS_ENTITIES}
    if own_entity_ids & other_entity_ids:
        raise ValueError(f"{_LANE_NAME} entity collision with wave8_eritrea")

    for candidate_id in (
        set(WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS)
        | set(WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS)
    ):
        _validate_hced_fingerprint(hced_by_id, candidate_id)

    for candidate_id, disposition in (
        WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS.items()
    ):
        rows = [
            row
            for row in iwbd_rows
            if str(row.get("candidate_id") or "") == candidate_id
        ]
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} IWBD disposition {candidate_id} expected one row, "
                f"found {len(rows)}"
            )
        row = rows[0]
        expected = {
            "name": disposition["expected_name"],
            "start_date": disposition["expected_start_date"],
            "end_date": disposition["expected_end_date"],
            "winner_raw": disposition["expected_winner_raw"],
        }
        if {field: row.get(field) for field in expected} != expected:
            raise ValueError(f"{_LANE_NAME} IWBD disposition changed")

    events = list(existing_events)
    for event_id, disposition in (
        WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
    ):
        matches = [event for event in events if str(event.get("id") or "") == event_id]
        if len(matches) != 1:
            raise ValueError(
                f"{_LANE_NAME} existing release disposition expected one event "
                f"{event_id}, found {len(matches)}"
            )
        event = matches[0]
        if (
            event.get("hced_candidate_id")
            != disposition["expected_hced_candidate_id"]
            or event.get("name") != disposition["expected_name"]
            or int(event.get("year")) != int(disposition["expected_year"])
        ):
            raise ValueError(f"{_LANE_NAME} existing release disposition changed")

    declared_hced = set(WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS)
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id") or "")
        not in (WAVE8_ERITREAN_REBELS_RESERVED_IDS | declared_hced)
        and (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if hced_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_matches}")

    declared_iwbd = set(WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS)
    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if str(row.get("candidate_id") or "") not in declared_iwbd
        and (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if iwbd_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_matches}")

    declared_release = set(
        WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    )
    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in events
        if str(event.get("id") or "") not in declared_release
        and event.get("hced_candidate_id") not in WAVE8_ERITREAN_REBELS_RESERVED_IDS
        and (_row_year(event), normalize_label(event.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_matches}"
        )

    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "hced_duplicate_dispositions": len(
            WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(
            WAVE8_ERITREAN_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_ERITREAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "related_hced_dispositions": len(
            WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS
        ),
    }


def install_wave8_eritrean_rebels_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ERITREAN_REBELS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_eritrean_rebels_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_ERITREAN_REBELS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_event_review(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        contract = WAVE8_ERITREAN_REBELS_CONTRACTS[candidate_id]
        if candidate_id in WAVE8_ERITREAN_REBELS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_ERITREAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)
        event_type = str(contract["event_type"])
        event["event_type"] = event_type
        if event_type == "campaign":
            event["summary"] = (
                "Candidate-keyed Wave 8 operational campaign assertion. The "
                "complete HCED interval, identities, and independent outcome "
                "evidence are pinned; no individual battle or strategic war "
                "outcome is invented. "
                + str(contract["audit_note"])
            )
            for participant in event["participants"]:
                termination = str(participant.get("termination", ""))
                if "victory" in termination:
                    participant["termination"] = "campaign_victory"
                elif "defeat" in termination:
                    participant["termination"] = "campaign_defeat"


def promote_wave8_eritrean_rebels_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit the four audited outcomes and no neighboring-lane event."""

    validate_wave8_eritrean_rebels_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ERITREAN_REBELS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_event_review(events)
    return events


def wave8_eritrean_rebels_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_ERITREAN_REBELS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_eritrean_rebels_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_ERITREAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "hced_duplicate_dispositions": len(
            WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_ERITREAN_REBELS_HOLDS),
        "integration_dispositions": len(
            WAVE8_ERITREAN_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_ERITREAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_ERITREAN_REBELS_ENTITIES),
        "new_sources": len(WAVE8_ERITREAN_REBELS_SOURCES),
        "newly_rated_events": len(WAVE8_ERITREAN_REBELS_CONTRACTS),
        "outcome_overrides": len(WAVE8_ERITREAN_REBELS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_ERITREAN_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_ERITREAN_REBELS_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_ERITREAN_REBELS_RESERVED_IDS),
        "terminal_exclusions": len(
            WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS
        ),
    }


def wave8_eritrean_rebels_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "point": frozenset(WAVE8_ERITREAN_REBELS_POINT_QUARANTINE_ADDITIONS),
        "country": frozenset(
            WAVE8_ERITREAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
    }
