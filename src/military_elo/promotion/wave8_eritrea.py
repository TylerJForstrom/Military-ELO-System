"""Candidate-keyed Wave 8 audit for HCED's exact ``Eritrea`` label.

The locked queue contains eight exact-label rows.  Four post-independence
state rows are already owned by the release and are pinned here as external
dispositions.  Four pre-independence rows are promoted only after replacing
the anachronistic country label with event-bounded Eritrean People's
Liberation Front (EPLF) formations.  The lane opens no generic alias and never
passes a rating from the EPLF to the State of Eritrea, the Eritrean Liberation
Front (ELF), a generic ``Eritrean Rebels`` label, or a composite Ethiopian
rebel coalition.

Keren (1977-1978) and Nakfa (1977-1988) are reviewed as operational campaigns,
not invented point battles.  Unknown outcomes remain unknown; no unknown is
converted to a draw.
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
    operationalize_campaign_outcomes,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


_LANE_NAME = "Wave 8 Eritrea exact-actor audit"
_MODULE_OWNER = "wave8_eritrea"
_EVENT_ID_PREFIX = "hced_wave8_eritrea_"

_ETHIOPIA_ID = "clio_q115_1942_f6caec22"
_STATE_ERITREA_ID = "clio_q986_1992_ada8dae7"
_KEREN_EPLF_ID = "eplf_keren_defense_force_1977_1978"
_NAKFA_EPLF_ID = "eplf_nakfa_front_1977_1988"
_BARENTU_EPLF_ID = "eplf_barentu_assault_force_1985"
_AFABET_EPLF_ID = "eplf_afabet_field_force_1988"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    roles: Iterable[str],
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
        "evidence_roles": sorted(set(map(str, roles))),
    }


WAVE8_ERITREA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_eritrea_hrw_total_war",
        "Evil Days: 30 Years of War and Famine in Ethiopia — Total War in Eritrea, 1978-84",
        "https://www.hrw.org/reports/pdfs/e/ethiopia/ethiopia.919/c7redsta.pdf",
        "Africa Watch / Human Rights Watch",
        "independent_contemporaneous_human_rights_history",
        "hrw_evil_days_total_war",
        {
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        },
    ),
    _source(
        "wave8_eritrea_hrw_barentu",
        "Evil Days — War and the Use of Relief as a Weapon in Eritrea, 1984-88",
        "https://www.hrw.org/reports/pdfs/e/ethiopia/ethiopia.919/d0barent.pdf",
        "Africa Watch / Human Rights Watch",
        "independent_contemporaneous_human_rights_history",
        "hrw_evil_days_barentu",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_eritrea_hrw_afabet",
        "Evil Days — The Road to Asmara: Eritrea, 1988-91",
        "https://www.hrw.org/reports/pdfs/e/ethiopia/ethiopia.919/d4afabet.pdf",
        "Africa Watch / Human Rights Watch",
        "independent_contemporaneous_human_rights_history",
        "hrw_evil_days_afabet",
        {
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        },
    ),
    _source(
        "wave8_eritrea_loc_afabet",
        "Ethiopia: Government Defeats in Eritrea and Tigray",
        "https://countrystudies.us/ethiopia/36.htm",
        "U.S. Library of Congress, Federal Research Division",
        "federal_country_study",
        "loc_ethiopia_country_study",
        {"outcome", "outcome_consistency_crosscheck"},
    ),
    _source(
        "wave8_eritrea_tareke_afabet",
        "From Af Abet to Shire: the defeat and demise of Ethiopia's Red Army, 1988-89",
        "https://doi.org/10.1017/S0022278X04000114",
        "Cambridge University Press, Journal of Modern African Studies",
        "peer_reviewed_military_history",
        "tareke_afabet_shire_2004",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_eritrea_tareke_nakfa",
        "Nakfa: Even the Mountains Fought",
        "https://doi.org/10.12987/yale/9780300156157.003.0007",
        "Yale University Press",
        "scholarly_military_history_book_chapter",
        "tareke_ethiopian_revolution_nakfa",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_eritrea_jude_nakfa",
        "Making or un-making states: when does war have formative effects?",
        "https://doi.org/10.1177/13540661211053628",
        "SAGE, European Journal of International Relations",
        "peer_reviewed_state_formation_history",
        "jude_war_state_formation_2022",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_eritrea_ucalgary_keren",
        "Map of Ethiopia and Eritrea",
        (
            "https://ucp.manifoldapp.org/read/"
            "secession-and-separatist-conflicts-in-postcolonial-africa/"
            "section/e9100900-9389-4ae9-a282-fdb792a55be1"
        ),
        "University of Calgary Press",
        "open_access_scholarly_book",
        "ucalgary_secession_conflicts_eritrea",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_eritrea_dia_1985",
        "Ethiopia: 1985 military operations in northern Ethiopia",
        "https://www.dia.mil/FOIA/FOIA-Electronic-Reading-Room/FileId/238426/",
        "U.S. Defense Intelligence Agency FOIA Electronic Reading Room",
        "declassified_contemporaneous_intelligence_assessment",
        "dia_ethiopia_1985_operations",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_eritrea_un_coi_history",
        "Detailed findings of the Commission of Inquiry on Human Rights in Eritrea, chapter III",
        (
            "https://www.ohchr.org/Documents/HRBodies/HRCouncil/CoIEritrea/"
            "A_HRC_29_CRP-1_Chapter_III.pdf"
        ),
        "United Nations Human Rights Council",
        "united_nations_commission_history",
        "un_coi_eritrea_chapter_iii",
        {"identity_boundary_or_context_reference"},
    ),
    _source(
        "wave8_eritrea_ucdp_actor_26_1",
        "UCDP Actor Dataset version 26.1",
        "https://ucdp.uu.se/downloads/",
        "Uppsala Conflict Data Program",
        "curated_conflict_actor_dataset",
        "ucdp_actor_26_1",
        {"identity_boundary_or_context_reference"},
    ),
    _source(
        "wave8_eritrea_hrw_horn_war",
        "The Horn of Africa War: Mass Expulsions and the Nationality Issue",
        "https://www.hrw.org/report/2003/01/29/horn-africa-war/mass-expulsions-and-nationality-issue",
        "Human Rights Watch",
        "independent_postwar_investigation",
        "hrw_horn_of_africa_war_2003",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_eritrea_eecc_western_front",
        "Eritrea-Ethiopia Claims Commission: Western Front Partial Award",
        "https://legal.un.org/riaa/cases/vol_XXVI/291-349.pdf",
        "United Nations Reports of International Arbitral Awards",
        "international_arbitral_award",
        "eecc_western_front_award",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_eritrea_eecc_central_front",
        "Eritrea-Ethiopia Claims Commission case documents: Central Front Partial Awards",
        "https://pca-cpa.org/en/cases/71/",
        "Permanent Court of Arbitration",
        "international_arbitral_case_record",
        "eecc_central_front_awards",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_eritrea_un_report_2000",
        "Report of the Secretary-General on Eritrea and Ethiopia, S/2000/530",
        "https://documents.un.org/doc/undoc/gen/n00/461/18/pdf/n0046118.pdf",
        "United Nations Security Council",
        "contemporaneous_un_secretary_general_report",
        "un_sg_eritrea_ethiopia_2000",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_eritrea_un_badme_1998",
        "Letter transmitting Eritrea's 20 May 1998 statement, S/1998/417",
        "https://digitallibrary.un.org/record/254443/files/S_1998_417-EN.pdf",
        "United Nations Security Council Digital Library",
        "contemporaneous_diplomatic_primary_document",
        "un_security_council_badme_1998",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
)

_SOURCE_BY_ID = {str(item["id"]): item for item in WAVE8_ERITREA_SOURCES}
_SOURCE_FAMILY_BY_ID = {
    source_id: str(item["source_family_id"])
    for source_id, item in _SOURCE_BY_ID.items()
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
        "continuity_note": note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


_NO_BRIDGE = (
    " No rating is inherited by the ELF, a generic Eritrean Rebels label, "
    "the 1991 Provisional Government, the PFDJ, the State of Eritrea, or any "
    "Ethiopian rebel coalition."
)

WAVE8_ERITREA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _KEREN_EPLF_ID,
        "EPLF Keren Defensive Force (1977-1978)",
        "campaign_force",
        1977,
        1978,
        {
            "wave8_eritrea_hrw_total_war",
            "wave8_eritrea_ucalgary_keren",
            "wave8_eritrea_ucdp_actor_26_1",
            "wave8_eritrea_un_coi_history",
        },
        (
            "Campaign-bounded EPLF formation defending Keren through the "
            "November 1978 Ethiopian offensive and strategic withdrawal. It is "
            "not the separate ELF, Eritrean civilians, or an Eritrean state."
            + _NO_BRIDGE
        ),
    ),
    _entity(
        _NAKFA_EPLF_ID,
        "EPLF Nakfa Front (1977-1988)",
        "defensive_front",
        1977,
        1988,
        {
            "wave8_eritrea_hrw_total_war",
            "wave8_eritrea_jude_nakfa",
            "wave8_eritrea_tareke_nakfa",
            "wave8_eritrea_ucdp_actor_26_1",
            "wave8_eritrea_un_coi_history",
        },
        (
            "Campaign-bounded EPLF defensive organization at Nakfa and its "
            "approaches. It represents the source row's sustained front, not "
            "every EPLF unit or the Eritrean population."
            + _NO_BRIDGE
        ),
    ),
    _entity(
        _BARENTU_EPLF_ID,
        "EPLF Barentu Assault Force (July 1985)",
        "assault_force",
        1985,
        1985,
        {
            "wave8_eritrea_dia_1985",
            "wave8_eritrea_hrw_barentu",
            "wave8_eritrea_ucdp_actor_26_1",
            "wave8_eritrea_un_coi_history",
        },
        (
            "Engagement-bounded EPLF force that captured Barentu in July 1985. "
            "It excludes the later Ethiopian counteroffensive, other Eritrean "
            "fronts, civilians, and a continuous national army."
            + _NO_BRIDGE
        ),
    ),
    _entity(
        _AFABET_EPLF_ID,
        "EPLF Afabet Field Force (17-19 March 1988)",
        "field_force",
        1988,
        1988,
        {
            "wave8_eritrea_hrw_afabet",
            "wave8_eritrea_loc_afabet",
            "wave8_eritrea_tareke_afabet",
            "wave8_eritrea_ucdp_actor_26_1",
            "wave8_eritrea_un_coi_history",
        },
        (
            "Engagement-bounded EPLF field force that defeated Ethiopia's "
            "Northern Command at Afabet. It is not a retrospective State of "
            "Eritrea army identity."
            + _NO_BRIDGE
        ),
    ),
)


WAVE8_ERITREA_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_ERITREA_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)
WAVE8_ERITREA_ROW_HASHES: dict[str, str] = {
    "hced-Addis Ababa1991-1": "c743004579d8037cec5b470037779bdebac698c21cfe11a3c44413f52fe36538",
    "hced-Afabet1988-1": "8e19b250c2a66085a32c5ef07ee57d80f4e43f3901caf63a4b067190723eb4b2",
    "hced-Asosa1990-1991-1": "3fce1e2431ad7cc42e1122493e6b91c29f1a16d6a96e914c703e3316a45359f7",
    "hced-Assab1991-1": "eae47486367be08330cf39f1b9c5c25b97445da5689bd73ff9ccc9a520b1284a",
    "hced-Badme1998-1": "1f72e7cbafeb0e4f16dfb3c73b0c140a2d536b034ace9a696753fdc8e2ed61e4",
    "hced-Badme1999-1": "ee307cce2fc50dbed61db44d4fc6f19ce612665800f81a057809c5859fd98738",
    "hced-Barentu1985-1": "f656a2313c7a0d7e8d013da0262dd24ce65124332a93d56d312b7d2a9d2bedfa",
    "hced-Barentu2000-1": "ce17ab82e77fb3e208717083e7892c49d15facd7a489ae5102981c1ec32358e9",
    "hced-Dekemhare1990-1991-1": "0e37854dff6227ee9a8f332bae75a58678331bd18a25df40e13609c7858ff562",
    "hced-Inda Silase1989-1": "4a4ea3108666d6399002a7d7b37bdc834ce467fe0e3b46b8d76b960b4a2f42f0",
    "hced-Keren1977-1978-1": "860078716b698678b20fc1ac9e829ebbd76899fc9b82852092af122b4926176a",
    "hced-Massawa1977-1": "fc2d47d47d86252bbb428cad1899fc1e0985a43aae0c53b2fad6393e979b188c",
    "hced-Massawa1990-1": "7fc9e9a0dc9accc6a1c85386f31a43538248d5f125b250230b127cfa80517199",
    "hced-Nakfa1977-1988-1": "55cb3fc8ce2f7faa87bc4f37618ca47f105a7457dfde8f1b589a03a74322b056",
    "hced-Tsorona1999-1": "654f0874b7cf05716c38c1ec35f068c909f7cc77d7f3198d1876d983aceefbc6",
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
    confidence: float,
    event_type: str,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_ERITREA_ROW_HASHES[candidate_id],
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
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_ERITREA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Keren1977-1978-1": _contract(
        "hced-Keren1977-1978-1",
        _canonical(
            "Ethiopian campaign to recapture Keren",
            1977,
            1978,
            "1977-26 November 1978; decisive recapture in November 1978",
            "year_range_end_day",
            "campaign",
        ),
        "ethiopian_keren_offensive_1977_1978",
        [_ETHIOPIA_ID],
        [_KEREN_EPLF_ID],
        1,
        {
            "wave8_eritrea_hrw_total_war",
            "wave8_eritrea_ucalgary_keren",
            "wave8_eritrea_un_coi_history",
        },
        {
            "wave8_eritrea_hrw_total_war",
            "wave8_eritrea_ucalgary_keren",
        },
        (
            "The Ethiopian offensive forced the EPLF to abandon Keren on 26 "
            "November 1978. The inconclusive Elabored battle is not recoded as "
            "a victory; the rated outcome is the longer Keren campaign and "
            "recapture recorded by HCED's 1977-1978 interval."
        ),
        confidence=0.88,
        event_type="campaign",
    ),
    "hced-Nakfa1977-1988-1": _contract(
        "hced-Nakfa1977-1988-1",
        _canonical(
            "Defense of the Nakfa front",
            1977,
            1988,
            "1977-1988",
            "year_range",
            "campaign",
        ),
        "eplf_nakfa_defensive_front_1977_1988",
        [_NAKFA_EPLF_ID],
        [_ETHIOPIA_ID],
        1,
        {
            "wave8_eritrea_hrw_total_war",
            "wave8_eritrea_jude_nakfa",
            "wave8_eritrea_tareke_nakfa",
            "wave8_eritrea_un_coi_history",
        },
        {
            "wave8_eritrea_hrw_total_war",
            "wave8_eritrea_jude_nakfa",
            "wave8_eritrea_tareke_nakfa",
        },
        (
            "HCED's eleven-year row is retained as an operational front outcome, "
            "not split into invented battles. Independent histories agree that "
            "repeated Ethiopian offensives failed to take the EPLF's Nakfa base."
        ),
        confidence=0.87,
        event_type="campaign",
    ),
    "hced-Barentu1985-1": _contract(
        "hced-Barentu1985-1",
        _canonical(
            "EPLF capture of Barentu",
            1985,
            1985,
            "July 1985",
            "month",
            "engagement",
        ),
        "eplf_barentu_capture_1985",
        [_BARENTU_EPLF_ID],
        [_ETHIOPIA_ID],
        1,
        {
            "wave8_eritrea_dia_1985",
            "wave8_eritrea_hrw_barentu",
            "wave8_eritrea_un_coi_history",
        },
        {"wave8_eritrea_dia_1985", "wave8_eritrea_hrw_barentu"},
        (
            "The rated action is the EPLF's July capture, which both sources "
            "distinguish from Ethiopia's successful counteroffensive weeks later. "
            "That later recapture is not silently folded into this result."
        ),
        confidence=0.93,
        event_type="engagement",
    ),
    "hced-Afabet1988-1": _contract(
        "hced-Afabet1988-1",
        _canonical(
            "Battle of Afabet",
            1988,
            1988,
            "17-19 March 1988",
            "day_range",
            "engagement",
        ),
        "eplf_afabet_1988",
        [_AFABET_EPLF_ID],
        [_ETHIOPIA_ID],
        1,
        {
            "wave8_eritrea_hrw_afabet",
            "wave8_eritrea_loc_afabet",
            "wave8_eritrea_tareke_afabet",
        },
        {
            "wave8_eritrea_hrw_afabet",
            "wave8_eritrea_loc_afabet",
            "wave8_eritrea_tareke_afabet",
        },
        (
            "The EPLF overwhelmed Ethiopia's Northern Command at Afabet in a "
            "source-attested three-day tactical victory. The actor is the 1988 "
            "EPLF field force, never the later State of Eritrea."
        ),
        confidence=0.97,
        event_type="engagement",
    ),
}

WAVE8_ERITREA_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_ERITREA_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_ERITREA_EXCLUSIONS = WAVE8_ERITREA_TERMINAL_EXCLUSIONS


def _existing_disposition(
    candidate_id: str,
    owner_event_id: str,
    reviewed_winner_id: str,
    evidence_refs: Iterable[str],
    note: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_ERITREA_ROW_HASHES[candidate_id],
        "disposition": "existing_release",
        "owner_event_id": owner_event_id,
        "expected_entity_ids": sorted({_ETHIOPIA_ID, _STATE_ERITREA_ID}),
        "reviewed_winner_id": reviewed_winner_id,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "note": note,
    }


WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Badme1998-1": _existing_disposition(
        "hced-Badme1998-1",
        "hced_label_hced_badme1998_1",
        _STATE_ERITREA_ID,
        {"wave8_eritrea_hrw_horn_war", "wave8_eritrea_un_badme_1998"},
        (
            "The post-independence interstate actor is correctly the State of "
            "Eritrea. The existing HCED owner is retained and is not re-emitted."
        ),
    ),
    "hced-Badme1999-1": _existing_disposition(
        "hced-Badme1999-1",
        "hced_label_hced_badme1999_1",
        _ETHIOPIA_ID,
        {"wave8_eritrea_eecc_western_front", "wave8_eritrea_hrw_horn_war"},
        (
            "The existing state-versus-state event records Ethiopia's late-"
            "February recapture of Badme and remains the canonical HCED owner."
        ),
    ),
    "hced-Barentu2000-1": _existing_disposition(
        "hced-Barentu2000-1",
        "hced_label_hced_barentu2000_1",
        _ETHIOPIA_ID,
        {"wave8_eritrea_eecc_western_front", "wave8_eritrea_un_report_2000"},
        (
            "The existing event records Ethiopia's May 2000 capture of Barentu; "
            "the independent State of Eritrea is the correct opposing polity."
        ),
    ),
    "hced-Tsorona1999-1": _existing_disposition(
        "hced-Tsorona1999-1",
        "hced_label_hced_tsorona1999_1",
        _STATE_ERITREA_ID,
        {"wave8_eritrea_eecc_central_front", "wave8_eritrea_hrw_horn_war"},
        (
            "The existing state-versus-state event records Eritrea's repulse of "
            "the March 1999 Ethiopian offensive on the Tsorona front."
        ),
    ),
}
WAVE8_ERITREA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS = (
    WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS
)
WAVE8_ERITREA_EXTERNAL_OWNER_DISPOSITIONS = (
    WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS
)


def _related_hced(
    candidate_id: str,
    raw_labels: Iterable[str],
    boundary: str,
    evidence_refs: Iterable[str],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_ERITREA_ROW_HASHES[candidate_id],
        "disposition": "outside_exact_eritrea_lane",
        "raw_labels": sorted(set(map(str, raw_labels))),
        "actor_boundary": boundary,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
    }


WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Addis Ababa1991-1": _related_hced(
        "hced-Addis Ababa1991-1",
        {"Ethiopian Rebels", "Ethiopia"},
        (
            "The EPRDF/TPLF-led seizure of Addis Ababa is an Ethiopian rebel "
            "coalition event. EPLF cooperation does not make it an Eritrea exact-"
            "label row or transfer this lane's actors into that coalition."
        ),
        {"wave8_eritrea_hrw_afabet", "wave8_eritrea_ucdp_actor_26_1"},
    ),
    "hced-Asosa1990-1991-1": _related_hced(
        "hced-Asosa1990-1991-1",
        {"Oromo Rebels, Eritrea", "Ethiopia"},
        (
            "The composite label requires an independently sourced Oromo/Eritrean "
            "coalition. It is neither the Afabet force nor the State of Eritrea."
        ),
        {"wave8_eritrea_ucdp_actor_26_1", "wave8_eritrea_un_coi_history"},
    ),
    "hced-Assab1991-1": _related_hced(
        "hced-Assab1991-1",
        {"Eritrean Rebels", "Ethiopia"},
        (
            "The generic rebel label and 1991 transition require a separate "
            "Assab operation audit; no exact Eritrea contract absorbs it."
        ),
        {"wave8_eritrea_hrw_afabet", "wave8_eritrea_un_coi_history"},
    ),
    "hced-Dekemhare1990-1991-1": _related_hced(
        "hced-Dekemhare1990-1991-1",
        {"Eritrean Rebels", "Ethiopia"},
        (
            "The two-year generic rebel campaign needs its own bounded formation "
            "and outcome review; it is outside this literal-label inventory."
        ),
        {"wave8_eritrea_hrw_afabet", "wave8_eritrea_ucdp_actor_26_1"},
    ),
    "hced-Inda Silase1989-1": _related_hced(
        "hced-Inda Silase1989-1",
        {"Tigrayan Rebels, Eritrea", "Ethiopia"},
        (
            "The composite TPLF/EPLF label is a separate coalition boundary. It "
            "cannot inherit an EPLF-only or State of Eritrea rating."
        ),
        {"wave8_eritrea_tareke_afabet", "wave8_eritrea_ucdp_actor_26_1"},
    ),
    "hced-Massawa1977-1": _related_hced(
        "hced-Massawa1977-1",
        {"Ethiopia, USSR", "Eritrean Rebels"},
        (
            "Massawa combines Ethiopian/Soviet support and a generic rebel side; "
            "the responsible front composition must be audited independently."
        ),
        {"wave8_eritrea_hrw_total_war", "wave8_eritrea_un_coi_history"},
    ),
    "hced-Massawa1990-1": _related_hced(
        "hced-Massawa1990-1",
        {"Eritrean Rebels", "Ethiopia"},
        (
            "Operation Fenkil is a distinct Massawa campaign with its own force "
            "and naval/ground boundaries; this lane does not absorb it."
        ),
        {"wave8_eritrea_hrw_afabet", "wave8_eritrea_ucdp_actor_26_1"},
    ),
}
WAVE8_ERITREA_CROSS_LANE_DISPOSITIONS = WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS
WAVE8_ERITREA_HCED_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}


def _iwbd_duplicate(
    owner_hced_candidate_id: str,
    owner_event_id: str,
    name: str,
    start_date: str,
    end_date: str,
    winner_raw: str,
    evidence_refs: Iterable[str],
) -> dict[str, Any]:
    return {
        "disposition": "duplicate_of_existing_hced_owner",
        "owner_hced_candidate_id": owner_hced_candidate_id,
        "owner_event_id": owner_event_id,
        "expected_name": name,
        "expected_start_date": start_date,
        "expected_end_date": end_date,
        "expected_winner_raw": winner_raw,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
    }


WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-219-84-1691": _iwbd_duplicate(
        "hced-Badme1998-1",
        "hced_label_hced_badme1998_1",
        "Badme 1",
        "1998-05-06",
        "1998-05-06",
        "Eritrea",
        {"wave8_eritrea_hrw_horn_war", "wave8_eritrea_un_badme_1998"},
    ),
    "iwbd-219-84-1693": _iwbd_duplicate(
        "hced-Badme1999-1",
        "hced_label_hced_badme1999_1",
        "Badme 2 (b)",
        "1999-02-25",
        "1999-02-26",
        "Ethiopia",
        {"wave8_eritrea_eecc_western_front", "wave8_eritrea_hrw_horn_war"},
    ),
    "iwbd-219-84-1694": _iwbd_duplicate(
        "hced-Tsorona1999-1",
        "hced_label_hced_tsorona1999_1",
        "Tsorona",
        "1999-03-16",
        "1999-03-18",
        "Eritrea",
        {"wave8_eritrea_eecc_central_front", "wave8_eritrea_hrw_horn_war"},
    ),
    "iwbd-219-84-1695": _iwbd_duplicate(
        "hced-Barentu2000-1",
        "hced_label_hced_barentu2000_1",
        "Barentu",
        "2000-05-17",
        "2000-05-18",
        "Ethiopia",
        {"wave8_eritrea_eecc_western_front", "wave8_eritrea_un_report_2000"},
    ),
}

WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-219-84-1692": {
        "disposition": "related_but_distinct_operation",
        "expected_name": "Badme 2 (a)",
        "expected_start_date": "1999-02-06",
        "expected_end_date": "1999-02-10",
        "expected_winner_raw": "Eritrea",
        "not_owner_hced_candidate_id": "hced-Badme1999-1",
        "evidence_refs": sorted(
            {"wave8_eritrea_eecc_western_front", "wave8_eritrea_hrw_horn_war"}
        ),
        "note": (
            "This earlier February action has the opposite winner from HCED's "
            "Badme 1999 row and is not silently deduplicated into it."
        ),
    }
}

WAVE8_ERITREA_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Afabet1988-1": {
        "aliases": ["afabet", "battle of afabet"],
        "years": [1988],
    },
    "hced-Barentu1985-1": {
        "aliases": ["barentu", "eplf capture of barentu"],
        "years": [1985],
    },
    "hced-Keren1977-1978-1": {
        "aliases": ["ethiopian campaign to recapture keren", "keren"],
        "years": [1977, 1978],
    },
    "hced-Nakfa1977-1988-1": {
        "aliases": ["defense of the nakfa front", "nakfa", "nacfa"],
        "years": list(range(1977, 1989)),
    },
}

WAVE8_ERITREA_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}

WAVE8_ERITREA_CONTRACT_IDS = frozenset(WAVE8_ERITREA_CONTRACTS)
WAVE8_ERITREA_HOLD_IDS = frozenset(WAVE8_ERITREA_HOLDS)
WAVE8_ERITREA_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_ERITREA_TERMINAL_EXCLUSIONS
)
WAVE8_ERITREA_EXISTING_RELEASE_IDS = frozenset(
    WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS
)
WAVE8_ERITREA_EXTERNAL_OWNER_IDS = WAVE8_ERITREA_EXISTING_RELEASE_IDS
WAVE8_ERITREA_RESERVED_IDS = WAVE8_ERITREA_CONTRACT_IDS | WAVE8_ERITREA_HOLD_IDS
WAVE8_ERITREA_UNRESOLVED_IDS = WAVE8_ERITREA_RESERVED_IDS
WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_ERITREA_CONTRACT_IDS | WAVE8_ERITREA_EXISTING_RELEASE_IDS
)
WAVE8_ERITREA_RELATED_HCED_IDS = frozenset(
    WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS
)
WAVE8_ERITREA_REVIEWED_CANDIDATE_IDS = frozenset(
    WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS | WAVE8_ERITREA_RELATED_HCED_IDS
)

WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS = WAVE8_ERITREA_CONTRACT_IDS
WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_ERITREA_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_ERITREA_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Afabet1988-1": {
        "actions": ["withhold_point"],
        "reference_source_ids": [
            "wave8_eritrea_hrw_afabet",
            "wave8_eritrea_loc_afabet",
        ],
        "reason": (
            "HCED supplies a town point, while the three-day battle covered "
            "Afabet and the surrounding Northern Command positions."
        ),
    },
    "hced-Barentu1985-1": {
        "actions": ["withhold_point"],
        "reference_source_ids": [
            "wave8_eritrea_dia_1985",
            "wave8_eritrea_hrw_barentu",
        ],
        "reason": (
            "The raw town centroid does not establish the assault lines or the "
            "multi-day military footprint."
        ),
    },
    "hced-Keren1977-1978-1": {
        "actions": ["withhold_point"],
        "reference_source_ids": [
            "wave8_eritrea_hrw_total_war",
            "wave8_eritrea_ucalgary_keren",
        ],
        "reason": (
            "A city centroid cannot represent the 1977-1978 Keren campaign, "
            "Elabored fighting, withdrawal routes, and approach axes."
        ),
    },
    "hced-Nakfa1977-1988-1": {
        "actions": ["withhold_point"],
        "reference_source_ids": [
            "wave8_eritrea_jude_nakfa",
            "wave8_eritrea_tareke_nakfa",
        ],
        "reason": (
            "An eleven-year defensive front cannot be represented by HCED's "
            "single Nakfa settlement point."
        ),
    },
}

WAVE8_ERITREA_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"existing_release:{key}": value
        for key, value in WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS.items()
    },
    **{
        f"related_hced:{key}": value
        for key, value in WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS.items()
    },
    **{
        f"iwbd_duplicate:{key}": value
        for key, value in WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS.items()
    },
    **{
        f"iwbd_related:{key}": value
        for key, value in WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS.items()
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_ERITREA_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_ERITREA_ENTITIES,
        "existing_release_dispositions": (
            WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS),
        "hced_queue_sha256": WAVE8_ERITREA_HCED_QUEUE_SHA256,
        "holds": WAVE8_ERITREA_HOLDS,
        "integration_dispositions": WAVE8_ERITREA_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_queue_sha256": WAVE8_ERITREA_IWBD_QUEUE_SHA256,
        "iwbd_zero_overlap_audit": WAVE8_ERITREA_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_ERITREA_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_ERITREA_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS,
        "related_iwbd_dispositions": WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS,
        "row_hashes": WAVE8_ERITREA_ROW_HASHES,
        "sources": WAVE8_ERITREA_SOURCES,
        "terminal_exclusions": WAVE8_ERITREA_TERMINAL_EXCLUSIONS,
    }


def wave8_eritrea_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_ERITREA_FINAL_AUDIT_SIGNATURE = (
    "a77029399a6dc84ec69e317f98909edb5d448c915ba63b01a62892c91deb00cd"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    materialized = list(map(str, values))
    return materialized == sorted(set(materialized))


def _validate_static() -> None:
    source_ids = [str(item["id"]) for item in WAVE8_ERITREA_SOURCES]
    families = [str(item["source_family_id"]) for item in WAVE8_ERITREA_SOURCES]
    if len(source_ids) != 16 or len(source_ids) != len(set(source_ids)):
        raise ValueError(f"{_LANE_NAME} source inventory changed")
    if len(families) != len(set(families)):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_ERITREA_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(item["id"]): item for item in WAVE8_ERITREA_ENTITIES}
    if len(entity_by_id) != 4 or len(entity_by_id) != len(WAVE8_ERITREA_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity inventory changed")
    forbidden_entity_ids = {_ETHIOPIA_ID, _STATE_ERITREA_ID, "eritrea", "eplf", "elf"}
    if set(entity_by_id) & forbidden_entity_ids:
        raise ValueError(f"{_LANE_NAME} opened a generic identity bridge")
    for entity in WAVE8_ERITREA_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} entity opens a label fallback")
        if int(entity["start_year"]) > int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} entity window is inverted")
        note = str(entity["continuity_note"]).casefold()
        for phrase in (
            "no rating is inherited",
            "state of eritrea",
            "generic eritrean rebels",
        ):
            if phrase not in note:
                raise ValueError(f"{_LANE_NAME} continuity guard is incomplete")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} entity cites an unknown source")

    expected_contract_ids = {
        "hced-Afabet1988-1",
        "hced-Barentu1985-1",
        "hced-Keren1977-1978-1",
        "hced-Nakfa1977-1988-1",
    }
    if set(WAVE8_ERITREA_CONTRACTS) != expected_contract_ids:
        raise ValueError(f"{_LANE_NAME} contract inventory changed")
    if WAVE8_ERITREA_HOLDS or WAVE8_ERITREA_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited nonpromotion")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_ERITREA_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_ERITREA_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract hash drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} canonical key drifted")
        if contract["event_type"] not in {"campaign", "engagement"}:
            raise ValueError(f"{_LANE_NAME} event type drifted")
        if canonical["granularity"] != contract["event_type"]:
            raise ValueError(f"{_LANE_NAME} event granularity drifted")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        participants = side_1 | side_2
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} invalid opposing sides")
        if _STATE_ERITREA_ID in participants:
            raise ValueError(f"{_LANE_NAME} backdated the State of Eritrea")
        new_participants = participants & set(entity_by_id)
        if len(new_participants) != 1 or _ETHIOPIA_ID not in participants:
            raise ValueError(f"{_LANE_NAME} actor boundary drifted")
        used_entities.update(new_participants)
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        for entity_id in new_participants:
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= low <= high <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an entity window")
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] not in {1, 2}
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"] is not True
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
            raise ValueError(f"{_LANE_NAME} outcome families drifted")
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")

    expected_external = {
        "hced-Badme1998-1",
        "hced-Badme1999-1",
        "hced-Barentu2000-1",
        "hced-Tsorona1999-1",
    }
    if set(WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS) != expected_external:
        raise ValueError(f"{_LANE_NAME} existing-release inventory changed")
    for candidate_id, item in WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS.items():
        if item["raw_row_sha256"] != WAVE8_ERITREA_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} existing-release hash drifted")
        if set(item["expected_entity_ids"]) != {_ETHIOPIA_ID, _STATE_ERITREA_ID}:
            raise ValueError(f"{_LANE_NAME} state actor disposition drifted")
        if item["reviewed_winner_id"] not in item["expected_entity_ids"]:
            raise ValueError(f"{_LANE_NAME} existing winner drifted")
        refs = list(map(str, item["evidence_refs"]))
        if len(refs) < 2 or not _is_sorted_unique(refs) or not set(refs) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} existing-release evidence drifted")
        used_sources.update(refs)

    expected_related = {
        "hced-Addis Ababa1991-1",
        "hced-Asosa1990-1991-1",
        "hced-Assab1991-1",
        "hced-Dekemhare1990-1991-1",
        "hced-Inda Silase1989-1",
        "hced-Massawa1977-1",
        "hced-Massawa1990-1",
    }
    if set(WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS) != expected_related:
        raise ValueError(f"{_LANE_NAME} related HCED inventory changed")
    for candidate_id, item in WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS.items():
        if item["raw_row_sha256"] != WAVE8_ERITREA_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} related HCED hash drifted")
        if not item["actor_boundary"] or not item["raw_labels"]:
            raise ValueError(f"{_LANE_NAME} related actor boundary is empty")
        refs = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} related HCED evidence drifted")
        used_sources.update(refs)

    if set(WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS) != {
        "iwbd-219-84-1691",
        "iwbd-219-84-1693",
        "iwbd-219-84-1694",
        "iwbd-219-84-1695",
    }:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    if set(WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS) != {"iwbd-219-84-1692"}:
        raise ValueError(f"{_LANE_NAME} related IWBD inventory changed")
    for inventory in (
        WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS,
        WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS,
    ):
        for item in inventory.values():
            refs = list(map(str, item["evidence_refs"]))
            if not _is_sorted_unique(refs) or not set(refs) <= set(_SOURCE_BY_ID):
                raise ValueError(f"{_LANE_NAME} IWBD evidence drifted")
            used_sources.update(refs)

    used_sources.update(
        source_id
        for entity in WAVE8_ERITREA_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(_SOURCE_BY_ID):
        missing = sorted(set(_SOURCE_BY_ID) - used_sources)
        extra = sorted(used_sources - set(_SOURCE_BY_ID))
        raise ValueError(
            f"{_LANE_NAME} sources are not exactly consumed; missing={missing}, extra={extra}"
        )

    if WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS != WAVE8_ERITREA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_ERITREA_LOCATION_QUARANTINE_REASONS) != WAVE8_ERITREA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    for item in WAVE8_ERITREA_LOCATION_QUARANTINE_REASONS.values():
        if item["actions"] != ["withhold_point"] or not item["reason"]:
            raise ValueError(f"{_LANE_NAME} location action drifted")
        if not set(item["reference_source_ids"]) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} location review cites an unknown source")
    if WAVE8_ERITREA_OUTCOME_OVERRIDES or WAVE8_ERITREA_HCED_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} empty outcome/HCED disposition changed")


def _rows_by_id(rows: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        result.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    return result


def _validate_hced_rows(
    indexed: Mapping[str, list[dict[str, Any]]],
    candidate_ids: Iterable[str],
) -> None:
    for candidate_id in candidate_ids:
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one HCED row {candidate_id}, found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != WAVE8_ERITREA_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} HCED fingerprint changed for {candidate_id}")


def validate_wave8_eritrea_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate the complete exact-label inventory and adjacent actor boundaries."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ERITREA_CONTRACTS,
        WAVE8_ERITREA_HOLDS,
        lane_name=_LANE_NAME,
    )
    indexed = _rows_by_id(hced_rows)
    _validate_hced_rows(indexed, WAVE8_ERITREA_REVIEWED_CANDIDATE_IDS)

    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == "eritrea"
        or normalize_label(row.get("side_2_raw")) == "eritrea"
    }
    if exact_ids != WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Eritrea inventory changed: {sorted(exact_ids)}"
        )

    eritrean_rebels_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == "eritrean rebels"
        or normalize_label(row.get("side_2_raw")) == "eritrean rebels"
    }
    if eritrean_rebels_ids != {
        "hced-Assab1991-1",
        "hced-Dekemhare1990-1991-1",
        "hced-Massawa1977-1",
        "hced-Massawa1990-1",
    }:
        raise ValueError(f"{_LANE_NAME} Eritrean Rebels boundary changed")

    for candidate_id, contract in WAVE8_ERITREA_CONTRACTS.items():
        row = indexed[candidate_id][0]
        winner_side = int(contract["winner_side"])
        if row.get("winner_raw") != row.get(f"side_{winner_side}_raw"):
            raise ValueError(f"{_LANE_NAME} winner drifted for {candidate_id}")
        if row.get("loser_raw") != row.get(f"side_{3 - winner_side}_raw"):
            raise ValueError(f"{_LANE_NAME} loser drifted for {candidate_id}")
        if row.get("winner_loser_complete") is not True:
            raise ValueError(f"{_LANE_NAME} incomplete outcome for {candidate_id}")
    return {
        "existing_release_dispositions": len(
            WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS
        ),
        "holds": result["holds"],
        "promotion_contracts": result["promotion_contracts"],
        "related_hced_dispositions": len(WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS),
        "reviewed_exact_label_rows": len(WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS),
        "reviewed_hced_rows": len(WAVE8_ERITREA_REVIEWED_CANDIDATE_IDS),
        "terminal_exclusions": len(WAVE8_ERITREA_TERMINAL_EXCLUSIONS),
        "unresolved_exact_label_rows": len(WAVE8_ERITREA_RESERVED_IDS),
    }


def _event_entity_ids(event: Mapping[str, Any]) -> set[str]:
    return {
        str(item["entity_id"])
        for item in event.get("participants", [])
        if isinstance(item, Mapping) and item.get("entity_id") is not None
    }


def _event_winner_ids(event: Mapping[str, Any]) -> set[str]:
    return {
        str(item["entity_id"])
        for item in event.get("participants", [])
        if isinstance(item, Mapping)
        and "victory" in str(item.get("termination", ""))
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        try:
            if row.get(field) is not None:
                return int(row[field])
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        value = str(row.get(field) or "")
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


def validate_wave8_eritrea_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin release/IWBD owners and fail closed on undeclared probable twins."""

    validate_wave8_eritrea_queue_contracts(hced_rows)
    events = list(existing_events)
    for candidate_id, disposition in WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS.items():
        matches = [
            event for event in events if event.get("hced_candidate_id") == candidate_id
        ]
        if len(matches) != 1:
            raise ValueError(
                f"{_LANE_NAME} existing owner {candidate_id} expected exactly one "
                f"event, found {len(matches)}"
            )
        event = matches[0]
        if str(event.get("id") or "") != disposition["owner_event_id"]:
            raise ValueError(f"{_LANE_NAME} existing owner ID changed for {candidate_id}")
        if _event_entity_ids(event) != set(disposition["expected_entity_ids"]):
            raise ValueError(f"{_LANE_NAME} existing participants changed for {candidate_id}")
        if _event_winner_ids(event) != {disposition["reviewed_winner_id"]}:
            raise ValueError(f"{_LANE_NAME} existing winner changed for {candidate_id}")
    reserved_release = sorted(
        str(event.get("id") or "<missing-id>")
        for event in events
        if event.get("hced_candidate_id") in WAVE8_ERITREA_RESERVED_IDS
    )
    if reserved_release:
        raise ValueError(
            f"{_LANE_NAME} reserved candidates already promoted: {reserved_release}"
        )

    iwbd_by_id = _rows_by_id(iwbd_rows)
    for candidate_id, disposition in {
        **WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS,
        **WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS,
    }.items():
        rows = iwbd_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} IWBD disposition {candidate_id} expected exactly "
                f"one row, found {len(rows)}"
            )
        row = rows[0]
        expected = {
            "name": disposition["expected_name"],
            "start_date": disposition["expected_start_date"],
            "end_date": disposition["expected_end_date"],
            "winner_raw": disposition["expected_winner_raw"],
        }
        actual = {field: row.get(field) for field in expected}
        if actual != expected:
            raise ValueError(f"{_LANE_NAME} IWBD disposition changed for {candidate_id}")

    audited_pairs = {
        (int(year), normalize_label(alias))
        for item in WAVE8_ERITREA_IWBD_ZERO_OVERLAP_AUDIT.values()
        for year in item["years"]
        for alias in item["aliases"]
    }
    declared_iwbd = (
        set(WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS)
        | set(WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS)
    )
    collisions = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if str(row.get("candidate_id") or "") not in declared_iwbd
        and (_row_year(row), normalize_label(row.get("name"))) in audited_pairs
    )
    if collisions:
        raise ValueError(
            f"{_LANE_NAME} undeclared probable IWBD twin(s): {collisions}"
        )
    return {
        "existing_release_dispositions": len(
            WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS
        ),
        "integration_dispositions": len(WAVE8_ERITREA_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "iwbd_related_dispositions": len(
            WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_ERITREA_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "related_hced_dispositions": len(WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS),
    }


def install_wave8_eritrea_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ERITREA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_eritrea_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_ERITREA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_event_review(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        contract = WAVE8_ERITREA_CONTRACTS[candidate_id]
        if candidate_id in WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS:
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
            operationalize_campaign_outcomes(event)
            for participant in event["participants"]:
                termination = str(participant.get("termination", ""))
                if "victory" in termination:
                    participant["termination"] = "campaign_victory"
                elif "defeat" in termination:
                    participant["termination"] = "campaign_defeat"


def promote_wave8_eritrea_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit four reviewed outcomes; existing owners and related rows emit none."""

    validate_wave8_eritrea_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ERITREA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_event_review(events)
    return events


def wave8_eritrea_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in WAVE8_ERITREA_CONTRACTS.values()
            ).items()
        )
    )


def wave8_eritrea_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_ERITREA_CROSS_LANE_DISPOSITIONS
        ),
        "exact_label_rows": len(WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS),
        "existing_release_dispositions": len(
            WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS
        ),
        "external_owner_contracts": len(WAVE8_ERITREA_EXTERNAL_OWNER_IDS),
        "holds": len(WAVE8_ERITREA_HOLDS),
        "integration_dispositions": len(WAVE8_ERITREA_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_related_dispositions": len(
            WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_ERITREA_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_ERITREA_ENTITIES),
        "new_sources": len(WAVE8_ERITREA_SOURCES),
        "newly_rated_events": len(WAVE8_ERITREA_CONTRACTS),
        "outcome_overrides": len(WAVE8_ERITREA_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_ERITREA_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_ERITREA_REVIEWED_CANDIDATE_IDS),
        "terminal_exclusions": len(WAVE8_ERITREA_TERMINAL_EXCLUSION_IDS),
        "unresolved_exact_label_rows": len(WAVE8_ERITREA_RESERVED_IDS),
    }


def wave8_eritrea_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS,
    }


__all__ = (
    "WAVE8_ERITREA_CONTRACT_IDS",
    "WAVE8_ERITREA_CONTRACTS",
    "WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ERITREA_CROSS_LANE_DISPOSITIONS",
    "WAVE8_ERITREA_ENTITIES",
    "WAVE8_ERITREA_EXCLUSIONS",
    "WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS",
    "WAVE8_ERITREA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_ERITREA_EXISTING_RELEASE_IDS",
    "WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS",
    "WAVE8_ERITREA_EXTERNAL_OWNER_DISPOSITIONS",
    "WAVE8_ERITREA_EXTERNAL_OWNER_IDS",
    "WAVE8_ERITREA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ERITREA_HCED_DUPLICATE_DISPOSITIONS",
    "WAVE8_ERITREA_HCED_QUEUE_SHA256",
    "WAVE8_ERITREA_HOLD_IDS",
    "WAVE8_ERITREA_HOLDS",
    "WAVE8_ERITREA_INTEGRATION_DISPOSITIONS",
    "WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_ERITREA_IWBD_QUEUE_SHA256",
    "WAVE8_ERITREA_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_ERITREA_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_ERITREA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_ERITREA_OUTCOME_OVERRIDES",
    "WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS",
    "WAVE8_ERITREA_RELATED_HCED_IDS",
    "WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS",
    "WAVE8_ERITREA_RESERVED_IDS",
    "WAVE8_ERITREA_REVIEWED_CANDIDATE_IDS",
    "WAVE8_ERITREA_ROW_HASHES",
    "WAVE8_ERITREA_SOURCES",
    "WAVE8_ERITREA_TERMINAL_EXCLUSION_IDS",
    "WAVE8_ERITREA_TERMINAL_EXCLUSIONS",
    "WAVE8_ERITREA_UNRESOLVED_IDS",
    "install_wave8_eritrea_entities",
    "install_wave8_eritrea_sources",
    "promote_wave8_eritrea_contracts",
    "validate_wave8_eritrea_integration_dispositions",
    "validate_wave8_eritrea_queue_contracts",
    "wave8_eritrea_audit_signature",
    "wave8_eritrea_cohort_counts",
    "wave8_eritrea_counts",
    "wave8_eritrea_location_quarantine_additions",
)
