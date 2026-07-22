"""Candidate-keyed Wave 8 audit for HCED's ``Taliban, al Qaeda`` label.

The normalized exact label owns four 2001 records: Mazar-e Sharif, Kunduz,
Qala-i-Jangi, and Tora Bora.  All four have independently documented tactical
endpoints.  This lane therefore promotes all four while refusing to turn the
compound string into a timeless coalition.

Each event receives source-attested, event-bounded formations.  Taliban and
al-Qaeda elements are split only where the evidence identifies both.  The
Mazar contract does not invent a British tactical contingent from HCED's broad
campaign label, and the Tora Bora contract replaces HCED's imprecise
``Northern Alliance`` wording with the Ali-Zaman eastern Afghan militias that
actually fought there.  Tora Bora is rated only as local field control after
enemy resistance ended; bin Laden's escape and the failure of the wider
decapitation mission are explicitly not converted into a strategic victory.

All four records have exact IWBD twins, for which HCED is declared the single
canonical owner.  UCDP's related annual and termination records describe
strategic conflict/dyad episodes rather than these tactical engagements and
remain separately staged.  Unknown is never converted to a draw, and no
generic Taliban, al-Qaeda, Afghanistan, United States, United Kingdom, or
Afghan-opposition alias is installed.
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
    "WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS",
    "WAVE8_TALIBAN_AL_QAEDA_CONTRACTS",
    "WAVE8_TALIBAN_AL_QAEDA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_TALIBAN_AL_QAEDA_CROSS_LANE_DISPOSITIONS",
    "WAVE8_TALIBAN_AL_QAEDA_ENTITIES",
    "WAVE8_TALIBAN_AL_QAEDA_EXCLUSION_IDS",
    "WAVE8_TALIBAN_AL_QAEDA_EXCLUSIONS",
    "WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_BOUNDARIES",
    "WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_TALIBAN_AL_QAEDA_EXPECTED_CANDIDATE_IDS",
    "WAVE8_TALIBAN_AL_QAEDA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_TALIBAN_AL_QAEDA_FUNNEL_AUDIT",
    "WAVE8_TALIBAN_AL_QAEDA_HCED_DUPLICATE_DISPOSITIONS",
    "WAVE8_TALIBAN_AL_QAEDA_HCED_QUEUE_SHA256",
    "WAVE8_TALIBAN_AL_QAEDA_HOLD_IDS",
    "WAVE8_TALIBAN_AL_QAEDA_HOLDS",
    "WAVE8_TALIBAN_AL_QAEDA_INTEGRATION_DISPOSITIONS",
    "WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_TALIBAN_AL_QAEDA_IWBD_QUEUE_SHA256",
    "WAVE8_TALIBAN_AL_QAEDA_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_TALIBAN_AL_QAEDA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_TALIBAN_AL_QAEDA_NONPROMOTIONS",
    "WAVE8_TALIBAN_AL_QAEDA_OUTCOME_OVERRIDES",
    "WAVE8_TALIBAN_AL_QAEDA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS",
    "WAVE8_TALIBAN_AL_QAEDA_RESERVED_IDS",
    "WAVE8_TALIBAN_AL_QAEDA_ROW_HASHES",
    "WAVE8_TALIBAN_AL_QAEDA_SOURCES",
    "WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSION_IDS",
    "WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS",
    "WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS",
    "WAVE8_TALIBAN_AL_QAEDA_UCDP_QUEUE_SHA256",
    "install_wave8_taliban_al_qaeda_entities",
    "install_wave8_taliban_al_qaeda_sources",
    "promote_wave8_taliban_al_qaeda_contracts",
    "validate_wave8_taliban_al_qaeda_funnel",
    "validate_wave8_taliban_al_qaeda_integration_dispositions",
    "validate_wave8_taliban_al_qaeda_queue_contracts",
    "wave8_taliban_al_qaeda_audit_signature",
    "wave8_taliban_al_qaeda_cohort_counts",
    "wave8_taliban_al_qaeda_counts",
    "wave8_taliban_al_qaeda_location_quarantine_additions",
    "wave8_taliban_al_qaeda_metadata",
)


_LANE_NAME = "Wave 8 exact Taliban al Qaeda actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_taliban_al_qaeda"
_EVENT_ID_PREFIX = "hced_wave8_taliban_al_qaeda_"
_EXACT_LABEL = "taliban al qaeda"
_REVERSED_LABEL = "al qaeda taliban"
_SINGLE_LABEL = "taliban"


WAVE8_TALIBAN_AL_QAEDA_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_TALIBAN_AL_QAEDA_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)
WAVE8_TALIBAN_AL_QAEDA_UCDP_QUEUE_SHA256: dict[str, str] = {
    "ucdp-conflict-26.1-candidates.jsonl": (
        "cbc28e8d06b5fdd83b688ca0be45695e2d2d3bcc59b486d8f92522593ba619ee"
    ),
    "ucdp-dyadic-26.1-candidates.jsonl": (
        "c6e6f7deda305d38e78c987713817410ba3c4045904e22e86e12389fb4a622e4"
    ),
    "ucdp-termination-conflict-candidates.jsonl": (
        "4ce351ab0b0654b341ca8aba42ba82bd5a1955e7c6900351d0f179aae02a3219"
    ),
    "ucdp-termination-dyad-candidates.jsonl": (
        "49c8bead50aa966ee0c70ac023eca9dd81060668db180c1dcfd116c0e827218d"
    ),
}


WAVE8_TALIBAN_AL_QAEDA_ROW_HASHES: dict[str, str] = {
    "hced-Kunduz2001-1": (
        "bd4b2a3a84688c4d5c75422a4622193b8fca5369ce4a83897f56a9720600e6b8"
    ),
    "hced-Mazar-i-Sharif2001-1": (
        "c0f532d8be75594c945830dd7ded3b408792c1992d7413aeeef56b2f00ee7401"
    ),
    "hced-Qala-i-Jangi2001-1": (
        "be36eaed6345c599d4255dff2d6c8a15d2a0ba1eafd24dd09b0ba1fdb3f7c7f7"
    ),
    "hced-Tora Bora2001-1": (
        "0565c9f3aec81a775e512a2ea50de30752ccc12069f54929d5fe2f0059267c03"
    ),
}


WAVE8_TALIBAN_AL_QAEDA_FUNNEL_AUDIT: dict[str, Any] = {
    "label": _EXACT_LABEL,
    "event_candidate_id_sha256": (
        "d645a53ebb045ff8525088633cb44e88561e27deea3092c6ed4fcd283bdabb09"
    ),
    "events_touched": 4,
    "unresolved_side_attempts": 4,
    "sole_blocker_events": 4,
    "candidate_ids": [],
    "time_valid_candidate_ids": [],
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 4,
    },
    "centuries": {"CE_21": 4},
    "components_touched": 1,
    "components_bridged": 0,
    "rated_counterpart_entities": 1,
}


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
    dataset_boundary: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if crosscheck:
        roles.append("outcome_consistency_crosscheck")
    if dataset_boundary:
        roles.append("identity_boundary_or_context_reference")
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


WAVE8_TALIBAN_AL_QAEDA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_taliban_al_qaeda_army_oef",
        "Operation Enduring Freedom, September 2001-March 2002",
        (
            "https://history.army.mil/Portals/143/Images/Publications/"
            "Publication%20By%20Title%20Images/P%20Pdf/cmhPub_70-83-1v2.pdf"
        ),
        "U.S. Army Center of Military History",
        "official_military_history",
        "folse_army_cmh_oef_2022",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_army_modern_war",
        "Modern War in an Ancient Land: The U.S. Army in Afghanistan, 2001-2014, Volume I",
        "https://history.army.mil/portals/143/Images/Publications/catalog/59-1-p1.pdf",
        "U.S. Army Center of Military History",
        "official_operational_history",
        "degen_reardon_modern_war_volume1_2021",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_cia_swords_review",
        "Review: Afghan Napoleon and Swords of Lightning",
        (
            "https://www.cia.gov/resources/csi/static/"
            "Review4-Afghan-Napoleon-and-Swords-of-Lightning-Sep2022.pdf"
        ),
        "Central Intelligence Agency, Center for the Study of Intelligence",
        "official_intelligence_history_review",
        "cia_studies_intelligence_swords_review_2022",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_commons_2001",
        "The Campaign against International Terrorism: prospects after the fall of the Taliban",
        "https://researchbriefings.files.parliament.uk/documents/RP01-112/RP01-112.pdf",
        "House of Commons Library",
        "parliamentary_research_paper",
        "commons_library_rp01_112",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_un_human_rights_2002",
        "Report on the situation of human rights in Afghanistan, E/CN.4/2002/43",
        "https://digitallibrary.un.org/record/459912/files/E_CN.4_2002_43-EN.pdf",
        "United Nations Commission on Human Rights",
        "un_special_rapporteur_report",
        "un_hossain_afghanistan_2002",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_un_kunduz_2003",
        "Mission to Afghanistan, E/CN.4/2003/3/Add.4",
        "https://digitallibrary.un.org/record/487505/files/E_CN.4_2003_3_Add.4-EN.pdf",
        "United Nations Commission on Human Rights",
        "un_special_rapporteur_mission_report",
        "un_afghanistan_mission_2003",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_hrw_kunduz",
        "Afghanistan: Northern Alliance Must Accept Surrender Offer",
        "https://www.hrw.org/news/2001/11/20/afghanistan-northern-alliance-must-accept-surrender-offer",
        "Human Rights Watch",
        "contemporaneous_human_rights_report",
        "hrw_kunduz_surrender_2001",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_doj_lindh",
        "Affidavit in Support of a Criminal Complaint and an Arrest Warrant",
        "https://www.justice.gov/archives/ag/affidavit-support-criminal-complaint-and-arrest-warrant",
        "U.S. Department of Justice",
        "official_sworn_legal_record",
        "doj_lindh_affidavit_2002",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_amnesty_qala",
        "Afghanistan: urgent inquiry needed into violence in Qala-i-Jhangi",
        "https://www.amnesty.org/en/wp-content/uploads/2021/06/asa110362001en.pdf",
        "Amnesty International",
        "contemporaneous_human_rights_statement",
        "amnesty_qala_i_jhangi_2001",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_hansard_qala",
        "Afghanistan: Qala-i-Jhangi written answers, 13 December 2001",
        "https://hansard.parliament.uk/commons/2001-12-13/debates/0910a83d-6d25-4cb1-b6db-ad2b77d5a281/Afghanistan",
        "UK Parliament",
        "official_parliamentary_record",
        "uk_hansard_qala_i_jhangi_2001",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_army_mitchell_dsc",
        "Afghanistan SF leader gets first DSC since Vietnam",
        "https://www.army.mil/article-amp/1666/afghanistan_sf_leader_gets_first_dsc_since_vietnam",
        "U.S. Army",
        "official_award_history",
        "us_army_mitchell_dsc_qala_2007",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_senate_tora_bora",
        "Tora Bora Revisited: How We Failed to Get Bin Laden and Why It Matters Today",
        "https://www.govinfo.gov/content/pkg/CPRT-111SPRT53709/pdf/CPRT-111SPRT53709.pdf",
        "U.S. Senate Committee on Foreign Relations",
        "congressional_committee_report",
        "senate_foreign_relations_tora_bora_2009",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_911_commission",
        "The 9/11 Commission Report, chapter 10",
        "https://911commission.gov/report/911Report_Ch10.htm",
        "National Commission on Terrorist Attacks Upon the United States",
        "official_independent_commission_report",
        "nine_eleven_commission_chapter10",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_commons_2005",
        "Afghanistan: the culmination of the Bonn process",
        "https://researchbriefings.files.parliament.uk/documents/RP05-72/RP05-72.pdf",
        "House of Commons Library",
        "parliamentary_research_paper",
        "commons_library_rp05_72",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_australian_army_tora",
        "Operational Analysis of the Battle of Tora Bora, Afghanistan, 2001",
        "https://cove.army.gov.au/article/operational-analysis-battle-tora-bora-afghanistan-2001",
        "Australian Army",
        "official_professional_military_analysis",
        "australian_army_cove_tora_bora_2021",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_air_force_oef",
        "2001 - Operation Enduring Freedom",
        "https://www.afhistory.af.mil/FAQs/Fact-Sheets/Article/458975/2001-operation-enduring-freedom/",
        "U.S. Air Force Historical Support Division",
        "official_air_force_history",
        "usaf_oef_2001_fact_sheet",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_taliban_al_qaeda_ucdp_v26_1",
        "UCDP Conflict, Dyadic, and Conflict Termination datasets, version 26.1/4.2024.002",
        "https://ucdp.uu.se/downloads/",
        "Uppsala Conflict Data Program",
        "research_dataset_documentation",
        "ucdp_release_26_1_and_termination_4_2024_002",
        dataset_boundary=True,
    ),
)


_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_TALIBAN_AL_QAEDA_SOURCES
}
_SOURCE_FAMILY_BY_ID = {
    source_id: str(source["source_family_id"])
    for source_id, source in _SOURCE_BY_ID.items()
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    region: str,
    boundary_note: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 2001,
        "end_year": 2001,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No rating is inherited from or passed to the generic Taliban, "
            "al-Qaeda, Afghanistan, United States, United Kingdom, Northern "
            "Alliance, another Afghan faction, a later insurgency, or the "
            "strategic outcome of the 2001-2021 war."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_MAZAR_UF = "united_front_mazar_assault_force_2001"
_MAZAR_US = "us_special_operations_airpower_mazar_2001"
_MAZAR_TALIBAN = "taliban_mazar_garrison_2001"
_MAZAR_AQ = "al_qaeda_foreign_fighters_mazar_2001"
_KUNDUZ_UF = "united_front_kunduz_siege_force_2001"
_KUNDUZ_US = "us_special_operations_airpower_kunduz_2001"
_KUNDUZ_TALIBAN = "taliban_kunduz_garrison_2001"
_KUNDUZ_AQ = "al_qaeda_foreign_fighters_kunduz_2001"
_QALA_UF = "united_front_qala_jangi_recapture_force_2001"
_QALA_US = "us_qala_jangi_response_force_2001"
_QALA_UK = "uk_qala_jangi_special_forces_2001"
_QALA_TALIBAN = "taliban_prisoner_uprising_qala_jangi_2001"
_QALA_AQ = "al_qaeda_prisoner_uprising_qala_jangi_2001"
_TORA_AFGHAN = "ali_zaman_eastern_afghan_tora_bora_force_2001"
_TORA_US = "us_tora_bora_special_operations_airpower_2001"
_TORA_UK = "uk_tora_bora_special_forces_2001"
_TORA_TALIBAN = "taliban_tora_bora_supporting_fighters_2001"
_TORA_AQ = "al_qaeda_tora_bora_defenders_2001"


WAVE8_TALIBAN_AL_QAEDA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _MAZAR_UF,
        "Dostum-Atta-Mohaqiq United Front assault coalition at Mazar-e Sharif (2001)",
        "event_bounded_afghan_coalition",
        "Mazar-e Sharif approaches and city, Afghanistan",
        "Bounded to the United Front formations that captured Mazar on 9-10 November.",
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_cia_swords_review",
            "wave8_taliban_al_qaeda_un_human_rights_2002",
        ],
    ),
    _entity(
        _MAZAR_US,
        "U.S. special-operations and air-support force at Mazar-e Sharif (2001)",
        "event_bounded_foreign_support_force",
        "Mazar-e Sharif approaches, Afghanistan",
        "Bounded to U.S. special operations, CIA liaison, targeting, and air support in the Mazar capture.",
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_cia_swords_review",
            "wave8_taliban_al_qaeda_air_force_oef",
        ],
    ),
    _entity(
        _MAZAR_TALIBAN,
        "Taliban Mazar-e Sharif garrison (2001)",
        "event_bounded_nonstate_garrison",
        "Mazar-e Sharif, Afghanistan",
        "Bounded to the Taliban garrison and field defenders displaced from Mazar on 9-10 November.",
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_commons_2001",
            "wave8_taliban_al_qaeda_un_human_rights_2002",
        ],
    ),
    _entity(
        _MAZAR_AQ,
        "Al-Qaeda-linked foreign fighters at Mazar-e Sharif (2001)",
        "event_bounded_nonstate_formation",
        "Mazar-e Sharif and southern Balkh, Afghanistan",
        "Bounded to the Arab and other al-Qaeda-linked foreign formations reinforcing the Mazar front.",
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_cia_swords_review",
            "wave8_taliban_al_qaeda_commons_2001",
        ],
    ),
    _entity(
        _KUNDUZ_UF,
        "Daoud-Bariullah United Front siege coalition at Kunduz (2001)",
        "event_bounded_afghan_coalition",
        "Kunduz and its approaches, Afghanistan",
        "Bounded to United Front formations that encircled Kunduz and accepted its November surrender.",
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_commons_2001",
            "wave8_taliban_al_qaeda_hrw_kunduz",
        ],
    ),
    _entity(
        _KUNDUZ_US,
        "U.S. special-operations and air-support force at Kunduz (2001)",
        "event_bounded_foreign_support_force",
        "Kunduz Province, Afghanistan",
        "Bounded to U.S. teams and airpower supporting the Kunduz encirclement and surrender.",
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_army_modern_war",
            "wave8_taliban_al_qaeda_commons_2001",
        ],
    ),
    _entity(
        _KUNDUZ_TALIBAN,
        "Taliban Kunduz garrison (2001)",
        "event_bounded_nonstate_garrison",
        "Kunduz, Afghanistan",
        "Bounded to Taliban defenders encircled in Kunduz through their November surrender.",
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_hrw_kunduz",
            "wave8_taliban_al_qaeda_un_kunduz_2003",
        ],
    ),
    _entity(
        _KUNDUZ_AQ,
        "Al-Qaeda-linked foreign fighters in the Kunduz pocket (2001)",
        "event_bounded_nonstate_formation",
        "Kunduz, Afghanistan",
        "Bounded to the separately attested Arab and other al-Qaeda-linked foreign fighters in the Kunduz pocket.",
        [
            "wave8_taliban_al_qaeda_commons_2001",
            "wave8_taliban_al_qaeda_doj_lindh",
            "wave8_taliban_al_qaeda_hrw_kunduz",
        ],
    ),
    _entity(
        _QALA_UF,
        "United Front guard and recapture force at Qala-i-Jangi (2001)",
        "event_bounded_afghan_force",
        "Qala-i-Jangi fortress, Balkh, Afghanistan",
        "Bounded to Dostum, Atta, and Mohaqiq-aligned forces defending and retaking the fortress.",
        [
            "wave8_taliban_al_qaeda_amnesty_qala",
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_commons_2001",
        ],
    ),
    _entity(
        _QALA_US,
        "U.S. rescue, special-operations, and air-support force at Qala-i-Jangi (2001)",
        "event_bounded_foreign_support_force",
        "Qala-i-Jangi fortress, Balkh, Afghanistan",
        "Bounded to the CIA, U.S. special-operations, quick-reaction, and air elements in the fortress battle.",
        [
            "wave8_taliban_al_qaeda_army_mitchell_dsc",
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_doj_lindh",
        ],
    ),
    _entity(
        _QALA_UK,
        "British special-forces response at Qala-i-Jangi (2001)",
        "event_bounded_foreign_support_force",
        "Qala-i-Jangi fortress, Balkh, Afghanistan",
        "Bounded to the British special-forces personnel directly attested in the fortress response.",
        [
            "wave8_taliban_al_qaeda_amnesty_qala",
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_hansard_qala",
        ],
    ),
    _entity(
        _QALA_TALIBAN,
        "Taliban prisoners in the Qala-i-Jangi uprising (2001)",
        "event_bounded_captive_combatant_formation",
        "Qala-i-Jangi fortress, Balkh, Afghanistan",
        "Bounded to Taliban captives who resumed organized resistance inside the fortress.",
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_doj_lindh",
            "wave8_taliban_al_qaeda_hansard_qala",
        ],
    ),
    _entity(
        _QALA_AQ,
        "Al-Qaeda-trained foreign prisoners in the Qala-i-Jangi uprising (2001)",
        "event_bounded_captive_combatant_formation",
        "Qala-i-Jangi fortress, Balkh, Afghanistan",
        "Bounded to the separately attested al-Qaeda-trained and affiliated foreign captives who joined the uprising.",
        [
            "wave8_taliban_al_qaeda_army_mitchell_dsc",
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_doj_lindh",
        ],
    ),
    _entity(
        _TORA_AFGHAN,
        "Ali-Zaman eastern Afghan assault force at Tora Bora (2001)",
        "event_bounded_afghan_coalition",
        "Tora Bora, Nangarhar, Afghanistan",
        "Bounded to the rival Hazrat Ali and Haji Zaman militias used for the Tora Bora ground assault; it is not silently relabeled as the Northern Alliance.",
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_australian_army_tora",
            "wave8_taliban_al_qaeda_senate_tora_bora",
        ],
    ),
    _entity(
        _TORA_US,
        "U.S. special-operations and air force at Tora Bora (2001)",
        "event_bounded_foreign_assault_force",
        "Tora Bora, Nangarhar, Afghanistan",
        "Bounded to U.S. CIA, special-operations, and air elements used in the December cave-complex battle.",
        [
            "wave8_taliban_al_qaeda_911_commission",
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_senate_tora_bora",
        ],
    ),
    _entity(
        _TORA_UK,
        "British special-forces contingent at Tora Bora (2001)",
        "event_bounded_foreign_assault_force",
        "Tora Bora, Nangarhar, Afghanistan",
        "Bounded to British special-forces personnel directly attested in Task Force 11 and the December assault.",
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_commons_2001",
            "wave8_taliban_al_qaeda_senate_tora_bora",
        ],
    ),
    _entity(
        _TORA_TALIBAN,
        "Taliban supporting fighters at Tora Bora (2001)",
        "event_bounded_nonstate_formation",
        "Tora Bora, Nangarhar, Afghanistan",
        "Bounded only to Taliban commanders and fighters separately attested at the Tora Bora positions and surrender talks.",
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_commons_2001",
            "wave8_taliban_al_qaeda_commons_2005",
        ],
    ),
    _entity(
        _TORA_AQ,
        "Al-Qaeda defenders of the Tora Bora complex (2001)",
        "event_bounded_nonstate_formation",
        "Tora Bora, Nangarhar, Afghanistan",
        "Bounded to al-Qaeda forces defending the cave complex through the end of organized resistance in December.",
        [
            "wave8_taliban_al_qaeda_911_commission",
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_senate_tora_bora",
        ],
    ),
)


def _canonical(
    name: str,
    date_text: str,
    date_precision: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "year_low": 2001,
        "year_high": 2001,
        "date_text": date_text,
        "date_precision": date_precision,
        "granularity": granularity,
        "canonical_key": f"{_slug(name)}:2001:2001",
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    actor_boundary_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcome_ids = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_TALIBAN_AL_QAEDA_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "side_1_entity_ids": list(map(str, side_1_entity_ids)),
        "side_2_entity_ids": list(map(str, side_2_entity_ids)),
        "winner_side": 1,
        "result_type": "win",
        "war_type": "civil_war_foreign_intervention",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcome_ids,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcome_ids}
        ),
        "cohort": "afghanistan_2001_tactical",
        "disposition": "promote",
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "source_attested_event_bounded_formations",
        "actor_boundary_note": actor_boundary_note,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_TALIBAN_AL_QAEDA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Mazar-i-Sharif2001-1": _contract(
        "hced-Mazar-i-Sharif2001-1",
        _canonical(
            "Capture of Mazar-e Sharif (2001)",
            "9-10 November 2001",
            "day_range",
            "city_capture_operation",
        ),
        [_MAZAR_UF, _MAZAR_US],
        [_MAZAR_TALIBAN, _MAZAR_AQ],
        [
            "wave8_taliban_al_qaeda_air_force_oef",
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_cia_swords_review",
            "wave8_taliban_al_qaeda_commons_2001",
            "wave8_taliban_al_qaeda_un_human_rights_2002",
        ],
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_cia_swords_review",
            "wave8_taliban_al_qaeda_commons_2001",
            "wave8_taliban_al_qaeda_un_human_rights_2002",
        ],
        (
            "United Front formations, U.S. special operations, CIA liaison, "
            "and U.S. airpower took the city as the Taliban garrison and its "
            "separately attested al-Qaeda-linked foreign allies retreated. "
            "This is the city-capture result, not the whole northern campaign."
        ),
        (
            "HCED's United Kingdom token is campaign-level: no reviewed source "
            "places a British tactical formation in the 9-10 November capture, "
            "so none is invented or rated."
        ),
        confidence=0.86,
    ),
    "hced-Kunduz2001-1": _contract(
        "hced-Kunduz2001-1",
        _canonical(
            "Siege and surrender of Kunduz (2001)",
            "14-25 November 2001",
            "day_range",
            "siege_surrender_and_city_capture",
        ),
        [_KUNDUZ_UF, _KUNDUZ_US],
        [_KUNDUZ_TALIBAN, _KUNDUZ_AQ],
        [
            "wave8_taliban_al_qaeda_army_modern_war",
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_commons_2001",
            "wave8_taliban_al_qaeda_doj_lindh",
            "wave8_taliban_al_qaeda_hrw_kunduz",
            "wave8_taliban_al_qaeda_un_kunduz_2003",
        ],
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_commons_2001",
            "wave8_taliban_al_qaeda_hrw_kunduz",
            "wave8_taliban_al_qaeda_un_kunduz_2003",
        ],
        (
            "United Front forces, backed by U.S. airpower and special operations, "
            "encircled Kunduz; Taliban defenders and separately identified "
            "foreign al-Qaeda-linked formations surrendered or were captured. "
            "The rating ends with local capitulation, before prisoner transfers."
        ),
        (
            "The foreign-fighter component is kept separate from the Taliban "
            "garrison; neither is generalized beyond the Kunduz pocket."
        ),
        confidence=0.84,
    ),
    "hced-Qala-i-Jangi2001-1": _contract(
        "hced-Qala-i-Jangi2001-1",
        _canonical(
            "Suppression of the Qala-i-Jangi uprising",
            "25-29 November 2001",
            "day_range",
            "fortress_prison_uprising_and_recapture",
        ),
        [_QALA_UF, _QALA_US, _QALA_UK],
        [_QALA_TALIBAN, _QALA_AQ],
        [
            "wave8_taliban_al_qaeda_amnesty_qala",
            "wave8_taliban_al_qaeda_army_mitchell_dsc",
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_commons_2001",
            "wave8_taliban_al_qaeda_doj_lindh",
            "wave8_taliban_al_qaeda_hansard_qala",
        ],
        [
            "wave8_taliban_al_qaeda_amnesty_qala",
            "wave8_taliban_al_qaeda_army_mitchell_dsc",
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_doj_lindh",
            "wave8_taliban_al_qaeda_hansard_qala",
        ],
        (
            "After prisoners seized part of the fortress, United Front troops "
            "with U.S. and British support retook it and the remaining fighters "
            "surrendered. The rating records control of the fortress, not a "
            "judgment on detention practices, proportionality, or prisoner deaths."
        ),
        (
            "Sworn, official, and independent records identify both Taliban "
            "captives and al-Qaeda-trained or affiliated foreign fighters; the "
            "two bounded formations are not merged into one timeless actor."
        ),
        confidence=0.83,
    ),
    "hced-Tora Bora2001-1": _contract(
        "hced-Tora Bora2001-1",
        _canonical(
            "End of organized resistance at Tora Bora (2001)",
            "6-19 December 2001",
            "day_range",
            "mountain_complex_assault_and_enemy_withdrawal",
        ),
        [_TORA_AFGHAN, _TORA_US, _TORA_UK],
        [_TORA_TALIBAN, _TORA_AQ],
        [
            "wave8_taliban_al_qaeda_911_commission",
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_australian_army_tora",
            "wave8_taliban_al_qaeda_commons_2001",
            "wave8_taliban_al_qaeda_commons_2005",
            "wave8_taliban_al_qaeda_senate_tora_bora",
        ],
        [
            "wave8_taliban_al_qaeda_army_oef",
            "wave8_taliban_al_qaeda_australian_army_tora",
            "wave8_taliban_al_qaeda_commons_2005",
            "wave8_taliban_al_qaeda_senate_tora_bora",
        ],
        (
            "Coalition forces ended organized resistance and secured the local "
            "complex, while bin Laden and substantial al-Qaeda elements escaped. "
            "Only tactical field control is rated; the failed decapitation mission "
            "and the wider Afghanistan war receive no inferred victory."
        ),
        (
            "HCED's Northern Alliance token is corrected to the source-attested "
            "Hazrat Ali and Haji Zaman eastern Afghan militias. Taliban commanders "
            "and fighters are rated separately from al-Qaeda's principal defenders."
        ),
        confidence=0.72,
    ),
}


WAVE8_TALIBAN_AL_QAEDA_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_TALIBAN_AL_QAEDA_EXCLUSIONS = WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS
WAVE8_TALIBAN_AL_QAEDA_NONPROMOTIONS: dict[str, dict[str, Any]] = {}
WAVE8_TALIBAN_AL_QAEDA_HCED_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_TALIBAN_AL_QAEDA_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}

WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS = frozenset(
    WAVE8_TALIBAN_AL_QAEDA_CONTRACTS
)
WAVE8_TALIBAN_AL_QAEDA_HOLD_IDS = frozenset(WAVE8_TALIBAN_AL_QAEDA_HOLDS)
WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS
)
WAVE8_TALIBAN_AL_QAEDA_EXCLUSION_IDS = (
    WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSION_IDS
)
WAVE8_TALIBAN_AL_QAEDA_RESERVED_IDS = frozenset(
    WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS
    | WAVE8_TALIBAN_AL_QAEDA_HOLD_IDS
    | WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSION_IDS
)
WAVE8_TALIBAN_AL_QAEDA_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_TALIBAN_AL_QAEDA_ROW_HASHES
)


WAVE8_TALIBAN_AL_QAEDA_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS
)
WAVE8_TALIBAN_AL_QAEDA_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_TALIBAN_AL_QAEDA_LOCATION_QUARANTINE_ADDITIONS = {
    "country": WAVE8_TALIBAN_AL_QAEDA_COUNTRY_QUARANTINE_ADDITIONS,
    "point": WAVE8_TALIBAN_AL_QAEDA_POINT_QUARANTINE_ADDITIONS,
}
WAVE8_TALIBAN_AL_QAEDA_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "retained_country": "Afghanistan",
        "evidence_refs": sorted(
            set(contract["outcome_source_ids"][:2])
        ),
        "reason": (
            "HCED's point is a city, fortress vicinity, or broad mountain-complex "
            "centroid rather than an independently audited tactical footprint. "
            "The modern country Afghanistan is correct and remains published."
        ),
    }
    for candidate_id, contract in WAVE8_TALIBAN_AL_QAEDA_CONTRACTS.items()
}


WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "hced-Kabul1996-1": {
        "raw_row_sha256": (
            "1b4e5f7d13f1dbad2bfed1ed96f96d78098ed15fe07b45ff614b8ab5e120f224"
        ),
        "normalized_label": _SINGLE_LABEL,
        "disposition": "distinct_single_taliban_label_future_lane",
        "owner_module": None,
        "outcome_not_adjudicated": True,
        "boundary_note": (
            "A separate 1996 Afghan civil-war row against Massoud and Hekmatyar; "
            "it is neither an al-Qaeda compound row nor one of the 2001 battles."
        ),
    },
    "hced-Kabul2001-1": {
        "raw_row_sha256": (
            "71db0d14c3a117ac25349bad9173f51eee4ea9578472f2cbda82d13cc9c83233"
        ),
        "normalized_label": _SINGLE_LABEL,
        "disposition": "distinct_existing_release_owner",
        "owner_event_id": "hced_label_hced_kabul2001_1",
        "boundary_note": (
            "The capture of Kabul is separately released and does not duplicate "
            "Mazar, Kunduz, Qala-i-Jangi, or Tora Bora."
        ),
    },
    "hced-Kandahar2001-1": {
        "raw_row_sha256": (
            "bd54205d98c29e082856703a277c0063e1600143e89edf53e61f31dda0e57e26"
        ),
        "normalized_label": _SINGLE_LABEL,
        "disposition": "distinct_existing_release_owner",
        "owner_event_id": "hced_label_hced_kandahar2001_1",
        "boundary_note": (
            "The surrender of Kandahar is separately released and does not "
            "duplicate any northern or Tora Bora tactical contract."
        ),
    },
    "hced-Operation Anaconda2002-1": {
        "raw_row_sha256": (
            "1ea7a5ce4a1046bff20415235654d91dec102b2c6e6743bcee03852531a58981"
        ),
        "normalized_label": _REVERSED_LABEL,
        "disposition": "separate_reversed_compound_label_lane",
        "owner_module": "military_elo.promotion.wave8_al_qaeda_taliban",
        "owner_event_id": (
            "hced_wave8_al_qaeda_taliban_"
            "hced_operation_anaconda2002_1"
        ),
        "outcome_not_adjudicated": False,
        "boundary_note": (
            "The reversed al-Qaeda/Taliban spelling belongs to a distinct funnel "
            "lane. Its candidate ID says 2002 while the locked year fields say "
            "2001, a drift that this lane does not repair or silently absorb."
        ),
    },
    "hced-Operation Mongoose2003-1": {
        "raw_row_sha256": (
            "005bfbacf0527db7d168b6dcd891aa8c227005b6d3338e2580dc92926da7c39f"
        ),
        "normalized_label": _REVERSED_LABEL,
        "disposition": "separate_reversed_compound_label_lane",
        "owner_module": "military_elo.promotion.wave8_al_qaeda_taliban",
        "owner_event_id": (
            "hced_wave8_al_qaeda_taliban_"
            "hced_operation_mongoose2003_1"
        ),
        "outcome_not_adjudicated": False,
        "boundary_note": (
            "A distinct 2003 operation under the reversed compound spelling; "
            "its actor and event boundaries require their own audit."
        ),
    },
}


WAVE8_TALIBAN_AL_QAEDA_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "exact_taliban_lane": {
        "candidate_ids": sorted(
            {
                "hced-Kabul1996-1",
                "hced-Kabul2001-1",
                "hced-Kandahar2001-1",
            }
        ),
        "disposition": "single_label_owned_outside_compound_lane",
    },
    "reversed_al_qaeda_taliban_lane": {
        "candidate_ids": sorted(
            {
                "hced-Operation Anaconda2002-1",
                "hced-Operation Mongoose2003-1",
            }
        ),
        "disposition": "reversed_compound_owned_outside_exact_lane",
    },
}


WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_BOUNDARIES: dict[
    str, dict[str, Any]
] = {
    "afghanistan_war_2001_2021": {
        "expected_name": "War in Afghanistan",
        "expected_year": 2001,
        "expected_end_year": 2021,
        "expected_entity_ids": sorted(
            {"islamic_republic_afghanistan", "taliban", "united_states"}
        ),
        "disposition": "distinct_strategic_war_owner",
        "boundary_note": (
            "A twenty-year strategic seed event; no tactical result is deduced "
            "from or merged into it."
        ),
    },
    "taliban_offensive_2021": {
        "expected_name": "Taliban Offensive of 2021",
        "expected_year": 2021,
        "expected_end_year": 2021,
        "expected_entity_ids": sorted(
            {"islamic_republic_afghanistan", "taliban", "united_states"}
        ),
        "disposition": "distinct_later_campaign_owner",
        "boundary_note": "Twenty years later with different regimes and formations.",
    },
    "hced_label_hced_kabul2001_1": {
        "expected_name": "Kabul",
        "expected_year": 2001,
        "expected_end_year": 2001,
        "expected_hced_candidate_id": "hced-Kabul2001-1",
        "expected_entity_ids": ["taliban", "united_states"],
        "disposition": "distinct_existing_hced_owner",
        "boundary_note": "Different city capture and exact single-actor label.",
    },
    "hced_label_hced_kandahar2001_1": {
        "expected_name": "Kandahar",
        "expected_year": 2001,
        "expected_end_year": 2001,
        "expected_hced_candidate_id": "hced-Kandahar2001-1",
        "expected_entity_ids": ["taliban", "united_states"],
        "disposition": "distinct_existing_hced_owner",
        "boundary_note": "Different city surrender and exact single-actor label.",
    },
}


def _canonical_object_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _event_id(candidate_id: str) -> str:
    return f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"


WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "iwbd-225-87-1698": {
        "raw_row_sha256": (
            "6ea7d620b53b198a0c6884b3e4387ed2ae74d54a069f108e7d347e2abb3d7b2c"
        ),
        "owner_hced_candidate_id": "hced-Mazar-i-Sharif2001-1",
        "owner_event_id": _event_id("hced-Mazar-i-Sharif2001-1"),
        "expected_name": "Mazar-i-Sharif",
        "expected_start_date": "2001-11-09",
        "expected_end_date": "2001-11-10",
        "expected_winner_raw": "Allies/Northern Alliance",
        "disposition": "duplicate_of_canonical_hced_owner",
    },
    "iwbd-225-87-1700": {
        "raw_row_sha256": (
            "1b5423dd77f2941791954d22ae82c0bf093478c4eb9e99da6151e9174b74d16b"
        ),
        "owner_hced_candidate_id": "hced-Kunduz2001-1",
        "owner_event_id": _event_id("hced-Kunduz2001-1"),
        "expected_name": "Kunduz",
        "expected_start_date": "2001-11-14",
        "expected_end_date": "2001-11-26",
        "expected_winner_raw": "Allies/Northern Alliance",
        "disposition": "duplicate_of_canonical_hced_owner",
    },
    "iwbd-225-87-1701": {
        "raw_row_sha256": (
            "30d81e05299d516ca86a57cb4b0f0649c72d4ab57bfb8e35e4904c09c1376b50"
        ),
        "owner_hced_candidate_id": "hced-Qala-i-Jangi2001-1",
        "owner_event_id": _event_id("hced-Qala-i-Jangi2001-1"),
        "expected_name": "Qala-i-Jangi",
        "expected_start_date": "2001-11-24",
        "expected_end_date": "2001-11-27",
        "expected_winner_raw": "Allies/Northern Alliance",
        "disposition": "duplicate_of_canonical_hced_owner",
        "date_boundary_note": (
            "IWBD's 24-27 range is retained as source metadata; independent "
            "review dates the uprising and final surrender 25-29 November."
        ),
    },
    "iwbd-225-87-1703": {
        "raw_row_sha256": (
            "c056c6407ca0f1a14fd91bcd167fe1dce31813dcfccbabad19c66c97c5298485"
        ),
        "owner_hced_candidate_id": "hced-Tora Bora2001-1",
        "owner_event_id": _event_id("hced-Tora Bora2001-1"),
        "expected_name": "Tora Bora",
        "expected_start_date": "2001-12-06",
        "expected_end_date": "2001-12-17",
        "expected_winner_raw": "Allies/Northern Alliance",
        "disposition": "duplicate_of_canonical_hced_owner",
        "scope_boundary_note": (
            "The HCED owner uses audited eastern Afghan actors and extends to "
            "the official history's 19 December end of organized resistance."
        ),
    },
}


_UCDP_HASHES = {
    "ucdp-conflict-26.1-333-2001-1715": (
        "7ca7b4ec1017476e3c048cd059524052edc19f640bb16eea0e54f4a68811deaa"
    ),
    "ucdp-conflict-26.1-418-2001-2388": (
        "76ba1738bcfb205d951294abe791a8c5bf2038a9913e6a5c5f70eab31a658c58"
    ),
    "ucdp-dyadic-26.1-736-2001-2113": (
        "81476d93b029414b7b06fea8278bfe125c52922fe7bd93b760f1facc1c893583"
    ),
    "ucdp-dyadic-26.1-878-2001-2754": (
        "4270f6a9e0011326dbff943f5eb9d06c9dcd07316bf65b0b2c7cab20b52ced28"
    ),
    "ucdp-termination-conflict-333-1691": (
        "226a79a6015c95241e337cda420b3766e5938c46579520b96616150a3209cc2a"
    ),
    "ucdp-termination-conflict-418-2358": (
        "ca6276768e464a4d9e622ea835857e2dd8d6f255d631431482ad9756d41a65e5"
    ),
    "ucdp-termination-dyad-333-2102": (
        "6a5975df7513155c5f0c6b987f3f2a31383fc55dab666f19773ffe3a430f69b4"
    ),
    "ucdp-termination-dyad-418-2734": (
        "a91f1a9e89ccac9d242d252f7ccc33d0d09ea202902227b1775121c8612d2653"
    ),
}


def _ucdp_boundary(
    raw_row_sha256: str,
    conflict_id: str,
    scope: str,
    note: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": raw_row_sha256,
        "conflict_id": conflict_id,
        "scope": scope,
        "disposition": "related_strategic_record_not_tactical_duplicate",
        "evidence_refs": ["wave8_taliban_al_qaeda_ucdp_v26_1"],
        "boundary_note": note,
    }


WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "ucdp-conflict-26.1-333-2001-1715": _ucdp_boundary(
        _UCDP_HASHES["ucdp-conflict-26.1-333-2001-1715"],
        "333",
        "annual_conflict_record",
        "Government/UIFSA annual conflict intensity is not a named tactical battle.",
    ),
    "ucdp-dyadic-26.1-736-2001-2113": _ucdp_boundary(
        _UCDP_HASHES["ucdp-dyadic-26.1-736-2001-2113"],
        "333",
        "annual_dyad_record",
        "The Taliban-government/UIFSA dyad aggregates a year of conflict.",
    ),
    "ucdp-termination-conflict-333-1691": _ucdp_boundary(
        _UCDP_HASHES["ucdp-termination-conflict-333-1691"],
        "333",
        "strategic_conflict_episode",
        "No conflict-level termination is coded in this 2001 row.",
    ),
    "ucdp-termination-dyad-333-2102": _ucdp_boundary(
        _UCDP_HASHES["ucdp-termination-dyad-333-2102"],
        "333",
        "strategic_dyad_termination",
        "The 1996-2001 dyad termination is broader than all four engagements.",
    ),
    "ucdp-conflict-26.1-418-2001-2388": _ucdp_boundary(
        _UCDP_HASHES["ucdp-conflict-26.1-418-2001-2388"],
        "418",
        "annual_conflict_record",
        "The U.S.-al-Qaida annual conflict is global and location-coded to the USA.",
    ),
    "ucdp-dyadic-26.1-878-2001-2754": _ucdp_boundary(
        _UCDP_HASHES["ucdp-dyadic-26.1-878-2001-2754"],
        "418",
        "annual_dyad_record",
        "The U.S.-al-Qaida dyad does not identify any of the four battle outcomes.",
    ),
    "ucdp-termination-conflict-418-2358": _ucdp_boundary(
        _UCDP_HASHES["ucdp-termination-conflict-418-2358"],
        "418",
        "strategic_conflict_episode",
        "The open strategic episode has no 2001 termination or tactical name.",
    ),
    "ucdp-termination-dyad-418-2734": _ucdp_boundary(
        _UCDP_HASHES["ucdp-termination-dyad-418-2734"],
        "418",
        "strategic_dyad_episode",
        "The open dyad episode is not a tactical result and remains separately staged.",
    ),
}


WAVE8_TALIBAN_AL_QAEDA_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"related_hced:{candidate_id}": dict(disposition)
        for candidate_id, disposition in sorted(
            WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS.items()
        )
    },
    **{
        f"iwbd_duplicate:{candidate_id}": dict(disposition)
        for candidate_id, disposition in sorted(
            WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS.items()
        )
    },
    **{
        f"ucdp_boundary:{candidate_id}": dict(disposition)
        for candidate_id, disposition in sorted(
            WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS.items()
        )
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_TALIBAN_AL_QAEDA_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_TALIBAN_AL_QAEDA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": (
            WAVE8_TALIBAN_AL_QAEDA_CROSS_LANE_DISPOSITIONS
        ),
        "entities": WAVE8_TALIBAN_AL_QAEDA_ENTITIES,
        "existing_release_boundaries": (
            WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_BOUNDARIES
        ),
        "existing_release_duplicate_dispositions": (
            WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "funnel_audit": WAVE8_TALIBAN_AL_QAEDA_FUNNEL_AUDIT,
        "hced_duplicate_dispositions": (
            WAVE8_TALIBAN_AL_QAEDA_HCED_DUPLICATE_DISPOSITIONS
        ),
        "hced_queue_sha256": WAVE8_TALIBAN_AL_QAEDA_HCED_QUEUE_SHA256,
        "holds": WAVE8_TALIBAN_AL_QAEDA_HOLDS,
        "integration_dispositions": (
            WAVE8_TALIBAN_AL_QAEDA_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": (
            WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_queue_sha256": WAVE8_TALIBAN_AL_QAEDA_IWBD_QUEUE_SHA256,
        "location_quarantine_reasons": (
            WAVE8_TALIBAN_AL_QAEDA_LOCATION_QUARANTINE_REASONS
        ),
        "outcome_overrides": WAVE8_TALIBAN_AL_QAEDA_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_TALIBAN_AL_QAEDA_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": (
            WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS
        ),
        "row_hashes": WAVE8_TALIBAN_AL_QAEDA_ROW_HASHES,
        "sources": WAVE8_TALIBAN_AL_QAEDA_SOURCES,
        "terminal_exclusions": WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS,
        "ucdp_overlap_dispositions": (
            WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS
        ),
        "ucdp_queue_sha256": WAVE8_TALIBAN_AL_QAEDA_UCDP_QUEUE_SHA256,
    }


def wave8_taliban_al_qaeda_audit_signature() -> str:
    """Return the immutable digest of the complete four-row adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_TALIBAN_AL_QAEDA_FINAL_AUDIT_SIGNATURE = (
    "e3fd0f0047b3943534866b2bd51a786f3c00a645cf77bfe2125c81f1dad3d2bb"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(map(str, values))))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_TALIBAN_AL_QAEDA_CONTRACTS),
        len(WAVE8_TALIBAN_AL_QAEDA_HOLDS),
        len(WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS),
    ) != (4, 0, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (
        len(WAVE8_TALIBAN_AL_QAEDA_ENTITIES),
        len(WAVE8_TALIBAN_AL_QAEDA_SOURCES),
    ) != (18, 17):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_TALIBAN_AL_QAEDA_RESERVED_IDS != (
        WAVE8_TALIBAN_AL_QAEDA_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    if _sorted_newline_sha256(WAVE8_TALIBAN_AL_QAEDA_RESERVED_IDS) != (
        WAVE8_TALIBAN_AL_QAEDA_FUNNEL_AUDIT["event_candidate_id_sha256"]
    ):
        raise ValueError(f"{_LANE_NAME} candidate digest changed")
    if wave8_taliban_al_qaeda_audit_signature() != (
        WAVE8_TALIBAN_AL_QAEDA_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    if len(_SOURCE_BY_ID) != len(WAVE8_TALIBAN_AL_QAEDA_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(
        {str(source["source_family_id"]) for source in _SOURCE_BY_ID.values()}
    ) != len(WAVE8_TALIBAN_AL_QAEDA_SOURCES):
        raise ValueError(f"{_LANE_NAME} source-family independence weakened")
    for source in _SOURCE_BY_ID.values():
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity
        for entity in WAVE8_TALIBAN_AL_QAEDA_ENTITIES
    }
    if len(entity_by_id) != 18:
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    for entity in entity_by_id.values():
        if (entity["start_year"], entity["end_year"]) != (2001, 2001):
            raise ValueError(f"{_LANE_NAME} opened an entity window")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} opened a generic identity fallback")
        note = str(entity["continuity_note"]).casefold()
        for phrase in ("no rating is inherited", "generic taliban", "strategic"):
            if phrase not in note:
                raise ValueError(f"{_LANE_NAME} continuity boundary weakened")
        refs = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} entity sources are invalid")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_TALIBAN_AL_QAEDA_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_TALIBAN_AL_QAEDA_ROW_HASHES[
            candidate_id
        ]:
            raise ValueError(f"{_LANE_NAME} row hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = f"{_slug(str(canonical['name']))}:2001:2001"
        if (
            canonical["canonical_key"] != expected_key
            or canonical["year_low"] != 2001
            or canonical["year_high"] != 2001
            or not canonical["date_text"]
        ):
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if (
            not side_1
            or not side_2
            or set(side_1) & set(side_2)
            or not set(side_1 + side_2) <= set(entity_by_id)
        ):
            raise ValueError(f"{_LANE_NAME} opposing actor boundary changed")
        used_entities.update(side_1 + side_2)
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"]
            != "source_attested_event_bounded_formations"
            or not contract["actor_boundary_note"]
        ):
            raise ValueError(f"{_LANE_NAME} promotion semantics drifted")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or not set(evidence) <= set(_SOURCE_BY_ID)
            or len(outcomes) < 4
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
            or len(families) < 4
            or not _is_sorted_unique(families)
            or set(families)
            != {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance weakened")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entity fixtures are not exactly consumed")
    used_sources.update(
        source_id
        for entity in WAVE8_TALIBAN_AL_QAEDA_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    used_sources.update(
        source_id
        for item in WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS.values()
        for source_id in map(str, item["evidence_refs"])
    )
    if used_sources != set(_SOURCE_BY_ID):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    mazar = WAVE8_TALIBAN_AL_QAEDA_CONTRACTS[
        "hced-Mazar-i-Sharif2001-1"
    ]
    if _QALA_UK in mazar["side_1_entity_ids"] or "british" not in str(
        mazar["actor_boundary_note"]
    ).casefold():
        raise ValueError(f"{_LANE_NAME} invented British Mazar participation")
    tora = WAVE8_TALIBAN_AL_QAEDA_CONTRACTS["hced-Tora Bora2001-1"]
    if (
        _TORA_AFGHAN not in tora["side_1_entity_ids"]
        or _TORA_TALIBAN not in tora["side_2_entity_ids"]
        or _TORA_AQ not in tora["side_2_entity_ids"]
        or not all(
            phrase in str(tora["audit_note"]).casefold()
            for phrase in ("field control", "bin laden", "no inferred victory")
        )
    ):
        raise ValueError(f"{_LANE_NAME} Tora Bora scope boundary weakened")

    if set(WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS) != {
        "hced-Kabul1996-1",
        "hced-Kabul2001-1",
        "hced-Kandahar2001-1",
        "hced-Operation Anaconda2002-1",
        "hced-Operation Mongoose2003-1",
    }:
        raise ValueError(f"{_LANE_NAME} adjacent HCED inventory changed")
    if set(WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS) != {
        "iwbd-225-87-1698",
        "iwbd-225-87-1700",
        "iwbd-225-87-1701",
        "iwbd-225-87-1703",
    }:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    if set(WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS) != set(
        _UCDP_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} UCDP overlap inventory changed")
    if WAVE8_TALIBAN_AL_QAEDA_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_TALIBAN_AL_QAEDA_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_TALIBAN_AL_QAEDA_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    if (
        WAVE8_TALIBAN_AL_QAEDA_HOLDS
        or WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS
        or WAVE8_TALIBAN_AL_QAEDA_HCED_DUPLICATE_DISPOSITIONS
        or WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_TALIBAN_AL_QAEDA_OUTCOME_OVERRIDES
    ):
        raise ValueError(f"{_LANE_NAME} declared-empty inventory changed")


def _rows_by_id(
    rows: Iterable[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    result: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        result.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    return result


_EXPECTED_RAW_FIELDS: dict[str, dict[str, Any]] = {
    "hced-Mazar-i-Sharif2001-1": {
        "name": "Mazar-i-Sharif",
        "side_1_raw": "United States, United Kingdom, Northern Alliance",
        "side_2_raw": "Taliban, al Qaeda",
        "winner_raw": "United States, United Kingdom, Northern Alliance",
        "loser_raw": "Taliban, al Qaeda",
        "latitude": "36.6926167",
        "longitude": "67.1179511",
    },
    "hced-Kunduz2001-1": {
        "name": "Kunduz",
        "side_1_raw": "Northern Alliance, United States",
        "side_2_raw": "Taliban, Al Qaeda",
        "winner_raw": "Northern Alliance, United States",
        "loser_raw": "Taliban, Al Qaeda",
        "latitude": "36.7285907",
        "longitude": "68.8680663",
    },
    "hced-Qala-i-Jangi2001-1": {
        "name": "Qala-i-Jangi",
        "side_1_raw": "United States, United Kingdom, Northern Alliance",
        "side_2_raw": "Taliban, al Qaeda",
        "winner_raw": "United States, United Kingdom, Northern Alliance",
        "loser_raw": "Taliban, al Qaeda",
        "latitude": "36.6674951",
        "longitude": "66.9846531",
    },
    "hced-Tora Bora2001-1": {
        "name": "Tora Bora",
        "side_1_raw": "United States, United Kingdom, Northern Alliance",
        "side_2_raw": "Taliban, al Qaeda",
        "winner_raw": "United States, United Kingdom, Northern Alliance",
        "loser_raw": "Taliban, al Qaeda",
        "latitude": "34.1166714",
        "longitude": "70.2144783",
    },
}


def validate_wave8_taliban_al_qaeda_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate every exact-label row and each adjacent spelling boundary."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_TALIBAN_AL_QAEDA_CONTRACTS,
        WAVE8_TALIBAN_AL_QAEDA_HOLDS,
        lane_name=_LANE_NAME,
    )
    indexed = _rows_by_id(hced_rows)
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _EXACT_LABEL
        or normalize_label(row.get("side_2_raw")) == _EXACT_LABEL
    }
    if exact_ids != WAVE8_TALIBAN_AL_QAEDA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact inventory changed: {sorted(exact_ids)}"
        )

    for candidate_id, expected in _EXPECTED_RAW_FIELDS.items():
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(f"{_LANE_NAME} missing exact row {candidate_id}")
        row = rows[0]
        if any(row.get(field) != value for field, value in expected.items()):
            raise ValueError(f"{_LANE_NAME} raw semantics changed for {candidate_id}")
        if (
            row.get("year_low") != 2001
            or row.get("year_high") != 2001
            or row.get("year_best") != 2001
            or row.get("winner_loser_complete") is not True
            or normalize_label(row.get("side_2_raw")) != _EXACT_LABEL
        ):
            raise ValueError(f"{_LANE_NAME} date/outcome drift for {candidate_id}")

    reverse_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _REVERSED_LABEL
        or normalize_label(row.get("side_2_raw")) == _REVERSED_LABEL
    }
    single_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _SINGLE_LABEL
        or normalize_label(row.get("side_2_raw")) == _SINGLE_LABEL
    }
    if reverse_ids != {
        "hced-Operation Anaconda2002-1",
        "hced-Operation Mongoose2003-1",
    }:
        raise ValueError(f"{_LANE_NAME} reversed-label boundary changed")
    if single_ids != {
        "hced-Kabul1996-1",
        "hced-Kabul2001-1",
        "hced-Kandahar2001-1",
    }:
        raise ValueError(f"{_LANE_NAME} single-Taliban boundary changed")
    for candidate_id, disposition in (
        WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS.items()
    ):
        rows = indexed.get(candidate_id, [])
        if (
            len(rows) != 1
            or canonical_hced_row_sha256(rows[0])
            != disposition["raw_row_sha256"]
        ):
            raise ValueError(f"{_LANE_NAME} adjacent row changed: {candidate_id}")

    return {
        "adjacent_hced_dispositions": len(
            WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS
        ),
        "holds": result["holds"],
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(
            WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS
        ),
    }


def validate_wave8_taliban_al_qaeda_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    """Pin the exact four-row sole-blocker funnel record."""

    records = [
        record
        for record in funnel.get("labels", [])
        if record.get("label") == _EXACT_LABEL
    ]
    if len(records) != 1:
        raise ValueError(f"{_LANE_NAME} funnel label inventory changed")
    record = records[0]
    for key, expected in WAVE8_TALIBAN_AL_QAEDA_FUNNEL_AUDIT.items():
        if record.get(key) != expected:
            raise ValueError(f"{_LANE_NAME} funnel field changed: {key}")
    return {
        "exact_label_rows": int(record["events_touched"]),
        "shared_label_rows": int(record["events_touched"])
        - int(record["sole_blocker_events"]),
        "sole_blocker_rows": int(record["sole_blocker_events"]),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_low", "year_best"):
        value = row.get(field)
        try:
            if value not in (None, ""):
                return int(value)
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        value = row.get(field)
        if isinstance(value, str):
            text = value.lstrip("-")
            if len(text) >= 4 and text[:4].isdigit():
                year = int(text[:4])
                return -year if value.startswith("-") else year
    return None


_TACTICAL_ALIASES: dict[str, frozenset[str]] = {
    "hced-Mazar-i-Sharif2001-1": frozenset(
        map(
            normalize_label,
            (
                "Mazar-i-Sharif",
                "Mazar-e Sharif",
                "Capture of Mazar-e Sharif (2001)",
                "Fall of Mazar-e Sharif",
            ),
        )
    ),
    "hced-Kunduz2001-1": frozenset(
        map(
            normalize_label,
            ("Kunduz", "Konduz", "Siege and surrender of Kunduz (2001)"),
        )
    ),
    "hced-Qala-i-Jangi2001-1": frozenset(
        map(
            normalize_label,
            (
                "Qala-i-Jangi",
                "Qala-i-Janghi",
                "Qala-e-Jangi",
                "Suppression of the Qala-i-Jangi uprising",
            ),
        )
    ),
    "hced-Tora Bora2001-1": frozenset(
        map(
            normalize_label,
            ("Tora Bora", "End of organized resistance at Tora Bora (2001)"),
        )
    ),
}
_ALL_TACTICAL_ALIASES = frozenset().union(*_TACTICAL_ALIASES.values())


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {normalize_label(row.get("name"))}
    aliases = row.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]
    if isinstance(aliases, (list, tuple, set)):
        names.update(map(normalize_label, aliases))
    return {name for name in names if name}


def _participant_ids(event: Mapping[str, Any]) -> set[str]:
    participants = event.get("participants", [])
    if not isinstance(participants, list):
        return set()
    return {
        str(participant.get("entity_id"))
        for participant in participants
        if isinstance(participant, Mapping) and participant.get("entity_id")
    }


def validate_wave8_taliban_al_qaeda_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
    ucdp_rows: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin duplicate ownership and fail closed on any adjacent drift."""

    validate_wave8_taliban_al_qaeda_queue_contracts(hced_rows)

    iwbd_index = _rows_by_id(iwbd_rows)
    for candidate_id, disposition in (
        WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS.items()
    ):
        rows = iwbd_index.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(f"{_LANE_NAME} missing IWBD duplicate {candidate_id}")
        row = rows[0]
        if _canonical_object_sha256(row) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} IWBD fingerprint changed: {candidate_id}")
        expected = {
            "name": disposition["expected_name"],
            "start_date": disposition["expected_start_date"],
            "end_date": disposition["expected_end_date"],
            "winner_raw": disposition["expected_winner_raw"],
        }
        if any(row.get(key) != value for key, value in expected.items()):
            raise ValueError(f"{_LANE_NAME} IWBD outcome changed: {candidate_id}")

    declared_iwbd_ids = set(WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS)
    probable_iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if str(row.get("candidate_id")) not in declared_iwbd_ids
        and _row_year(row) == 2001
        and bool(_row_names(row) & _ALL_TACTICAL_ALIASES)
    )
    if probable_iwbd_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD twin(s): "
            f"{probable_iwbd_twins}"
        )

    supplied_ucdp_rows = list(ucdp_rows)
    if supplied_ucdp_rows:
        ucdp_index = _rows_by_id(supplied_ucdp_rows)
        for candidate_id, disposition in (
            WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS.items()
        ):
            rows = ucdp_index.get(candidate_id, [])
            if len(rows) != 1:
                raise ValueError(f"{_LANE_NAME} missing UCDP boundary {candidate_id}")
            if _canonical_object_sha256(rows[0]) != disposition["raw_row_sha256"]:
                raise ValueError(
                    f"{_LANE_NAME} UCDP boundary fingerprint changed: {candidate_id}"
                )

    existing = list(existing_events)
    lane_events = [
        event
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    lane_candidates = {
        str(event.get("hced_candidate_id")) for event in lane_events
    }
    if lane_candidates not in (
        set(),
        set(WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS),
    ) or len(lane_events) not in (0, len(WAVE8_TALIBAN_AL_QAEDA_CONTRACTS)):
        raise ValueError(f"{_LANE_NAME} release candidate overlap is partial")
    if lane_events:
        for event in lane_events:
            candidate_id = str(event.get("hced_candidate_id"))
            if event.get("id") != _event_id(candidate_id):
                raise ValueError(f"{_LANE_NAME} release candidate has a foreign owner")
            contract = WAVE8_TALIBAN_AL_QAEDA_CONTRACTS[candidate_id]
            expected_entities = set(contract["side_1_entity_ids"]) | set(
                contract["side_2_entity_ids"]
            )
            if _participant_ids(event) != expected_entities:
                raise ValueError(f"{_LANE_NAME} released actor boundary changed")

    if existing:
        by_event_id = {str(event.get("id")): event for event in existing}
        for event_id, boundary in (
            WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_BOUNDARIES.items()
        ):
            event = by_event_id.get(event_id)
            if event is None:
                raise ValueError(f"{_LANE_NAME} existing release boundary disappeared")
            if (
                event.get("name") != boundary["expected_name"]
                or _row_year(event) != boundary["expected_year"]
                or int(event.get("end_year", event.get("year")))
                != boundary["expected_end_year"]
                or _participant_ids(event) != set(boundary["expected_entity_ids"])
            ):
                raise ValueError(f"{_LANE_NAME} release boundary changed: {event_id}")
            expected_candidate = boundary.get("expected_hced_candidate_id")
            if expected_candidate is not None and event.get(
                "hced_candidate_id"
            ) != expected_candidate:
                raise ValueError(
                    f"{_LANE_NAME} release candidate boundary changed: {event_id}"
                )

    related_ids = set(WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS)
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id")
        not in WAVE8_TALIBAN_AL_QAEDA_CONTRACT_IDS
        and event.get("hced_candidate_id") not in related_ids
        and _row_year(event) == 2001
        and bool(_row_names(event) & _ALL_TACTICAL_ALIASES)
    )
    if release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_twins}"
        )
    released_ucdp = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("ucdp_candidate_id")
        in WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS
        or event.get("source_candidate_id")
        in WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS
    )
    if released_ucdp:
        raise ValueError(
            f"{_LANE_NAME} audited UCDP boundary unexpectedly released: "
            f"{released_ucdp}"
        )

    return {
        "adjacent_hced_dispositions": len(
            WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS
        ),
        "existing_release_boundaries": len(
            WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_BOUNDARIES
        ),
        "integration_dispositions": len(
            WAVE8_TALIBAN_AL_QAEDA_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "release_lane_overlap": len(lane_candidates),
        "ucdp_overlap_dispositions": (
            len(WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS)
            if supplied_ucdp_rows
            else 0
        ),
    }


def install_wave8_taliban_al_qaeda_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_TALIBAN_AL_QAEDA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_taliban_al_qaeda_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_TALIBAN_AL_QAEDA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_TALIBAN_AL_QAEDA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_TALIBAN_AL_QAEDA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_taliban_al_qaeda_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit four source-attested tactical wins and no timeless coalition."""

    validate_wave8_taliban_al_qaeda_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_TALIBAN_AL_QAEDA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine(events)
    return events


def wave8_taliban_al_qaeda_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_TALIBAN_AL_QAEDA_CONTRACTS.values()
            ).items()
        )
    )


def wave8_taliban_al_qaeda_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_hced_dispositions": len(
            WAVE8_TALIBAN_AL_QAEDA_RELATED_HCED_DISPOSITIONS
        ),
        "country_quarantine_additions": len(
            WAVE8_TALIBAN_AL_QAEDA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "existing_release_boundaries": len(
            WAVE8_TALIBAN_AL_QAEDA_EXISTING_RELEASE_BOUNDARIES
        ),
        "holds": len(WAVE8_TALIBAN_AL_QAEDA_HOLDS),
        "integration_dispositions": len(
            WAVE8_TALIBAN_AL_QAEDA_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_TALIBAN_AL_QAEDA_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_TALIBAN_AL_QAEDA_ENTITIES),
        "new_sources": len(WAVE8_TALIBAN_AL_QAEDA_SOURCES),
        "newly_rated_events": len(WAVE8_TALIBAN_AL_QAEDA_CONTRACTS),
        "outcome_overrides": len(WAVE8_TALIBAN_AL_QAEDA_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_TALIBAN_AL_QAEDA_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_TALIBAN_AL_QAEDA_CONTRACTS),
        "reviewed_hced_rows": len(
            WAVE8_TALIBAN_AL_QAEDA_EXPECTED_CANDIDATE_IDS
        ),
        "sole_blocker_rows": int(
            WAVE8_TALIBAN_AL_QAEDA_FUNNEL_AUDIT["sole_blocker_events"]
        ),
        "terminal_exclusions": len(
            WAVE8_TALIBAN_AL_QAEDA_TERMINAL_EXCLUSIONS
        ),
        "ucdp_overlap_dispositions": len(
            WAVE8_TALIBAN_AL_QAEDA_UCDP_OVERLAP_DISPOSITIONS
        ),
    }


def wave8_taliban_al_qaeda_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_TALIBAN_AL_QAEDA_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_TALIBAN_AL_QAEDA_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_taliban_al_qaeda_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "audit": "candidate_keyed_exact_compound_actor_with_tactical_scope",
        "counts": wave8_taliban_al_qaeda_counts(),
        "cohorts": wave8_taliban_al_qaeda_cohort_counts(),
        "final_audit_signature": WAVE8_TALIBAN_AL_QAEDA_FINAL_AUDIT_SIGNATURE,
        "funnel_audit": dict(WAVE8_TALIBAN_AL_QAEDA_FUNNEL_AUDIT),
        "module_owner": _MODULE_OWNER,
        "queue_sha256": {
            "hced": WAVE8_TALIBAN_AL_QAEDA_HCED_QUEUE_SHA256,
            "iwbd": WAVE8_TALIBAN_AL_QAEDA_IWBD_QUEUE_SHA256,
            "ucdp": dict(WAVE8_TALIBAN_AL_QAEDA_UCDP_QUEUE_SHA256),
        },
    }


_validate_static()
