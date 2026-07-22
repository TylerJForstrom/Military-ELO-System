"""Fail-closed exact audit of HCED's three ``Somali Rebels`` rows.

Two tightly bounded Mogadishu outcomes rate.  The December 1990--January
1991 urban campaign ends with the United Somali Congress driving Siad Barre's
loyalists from the capital.  The 3--4 October 1993 raid, relief, and extraction
battle is a limited U.S.-led tactical victory even though its operational and
political consequences were adverse.  That layer-specific finding reverses
HCED's raw result without rating the wider intervention.

Dul Madoba remains an explicit unknown-not-draw hold because the tactical,
raid-objective, force-preservation, and political layers conflict.  UCDP and
Wikidata rows are fingerprinted discovery/context records only; none can
originate a rating automatically.  No generic ``Somali Rebels`` alias or
continuity bridge is introduced.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    expected_exact_hced_win_participants,
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_SOMALI_REBELS_CONTRACT_IDS",
    "WAVE8_SOMALI_REBELS_CONTRACTS",
    "WAVE8_SOMALI_REBELS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SOMALI_REBELS_DISCOVERY_DATE_QUARANTINES",
    "WAVE8_SOMALI_REBELS_ENTITIES",
    "WAVE8_SOMALI_REBELS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SOMALI_REBELS_FULL_ROW_HASHES",
    "WAVE8_SOMALI_REBELS_FUNNEL_AUDIT",
    "WAVE8_SOMALI_REBELS_HOLD_IDS",
    "WAVE8_SOMALI_REBELS_HOLDS",
    "WAVE8_SOMALI_REBELS_INTEGRATION_DISPOSITIONS",
    "WAVE8_SOMALI_REBELS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_SOMALI_REBELS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_ENTITIES",
    "WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_SOURCES",
    "WAVE8_SOMALI_REBELS_RESERVED_IDS",
    "WAVE8_SOMALI_REBELS_ROW_HASHES",
    "WAVE8_SOMALI_REBELS_SOURCES",
    "WAVE8_SOMALI_REBELS_UCDP_DISPOSITIONS",
    "WAVE8_SOMALI_REBELS_UCDP_ROW_HASHES",
    "WAVE8_SOMALI_REBELS_WIKIDATA_EXPECTED",
    "WAVE8_SOMALI_REBELS_WIKIDATA_MATCHES",
    "WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES",
    "install_wave8_somali_rebels_entities",
    "install_wave8_somali_rebels_sources",
    "promote_wave8_somali_rebels_contracts",
    "validate_wave8_somali_rebels_current_artifact_state",
    "validate_wave8_somali_rebels_discovery_dispositions",
    "validate_wave8_somali_rebels_emissions",
    "validate_wave8_somali_rebels_existing_boundaries",
    "validate_wave8_somali_rebels_funnel",
    "validate_wave8_somali_rebels_integration_dispositions",
    "validate_wave8_somali_rebels_queue_contracts",
    "validate_wave8_somali_rebels_required_sources",
    "validate_wave8_somali_rebels_ucdp_dispositions",
    "wave8_somali_rebels_audit_signature",
    "wave8_somali_rebels_cohort_counts",
    "wave8_somali_rebels_counts",
    "wave8_somali_rebels_location_quarantine_additions",
    "wave8_somali_rebels_metadata",
)


_LANE_NAME = "Wave 8 exact Somali rebels audit"
_MODULE_OWNER = "military_elo.promotion.wave8_somali_rebels"
_EVENT_ID_PREFIX = "hced_wave8_somali_rebels_"
_EXACT_LABEL = "somali rebels"
_COHORT = "somali_rebels_exact_1913_1993"

_USC_MOGADISHU = "united_somali_congress_mogadishu_force_1990_1991"
_BARRE_LOYALISTS = "siad_barre_loyalist_forces_mogadishu_1990_1991"
_SNA_AIDID = "somali_national_alliance_aidid_force_mogadishu_1993"
_TASK_FORCE_RANGER = "task_force_ranger_mogadishu_1993"
_RELIEF_FORCE = "mogadishu_multinational_relief_force_1993"
_DERVISH = "somali_dervish_movement_1899_1920"
_SOMALIA = "clio_q1045_1960_b5c3f32e"


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
        "accessed": "2026-07-21",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_SOMALI_REBELS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_somali_rebels_kakwenzire_dul_madoba_1984",
        "Richard Corfield and the Dul Madoba Incident",
        "https://arcadia.sba.uniroma3.it/handle/2307/2898",
        "Northeast African Studies",
        "scholarly_history_article",
        "kakwenzire_somali_studies_1984",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_somali_rebels_hansard_dul_madoba_1914",
        "Class V — Colonial Services: Somaliland",
        (
            "https://api.parliament.uk/historic-hansard/commons/1914/feb/24/"
            "class-v-colonial-services-somaliland"
        ),
        "UK Parliament",
        "parliamentary_record",
        "uk_parliament_hansard",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_somali_rebels_durham_archer_dul_madoba",
        "Catalogue of the papers of Sir G. F. Archer",
        (
            "https://reed.dur.ac.uk/xtf/view?"
            "docId=ark%2F32150_s15q47rn75v.xml"
        ),
        "Durham University Library Archives and Special Collections",
        "archival_catalogue",
        "durham_sudan_archive",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_somali_rebels_africa_watch_somalia_1992",
        "Somalia: A Government at War with Its Own People",
        "https://www.hrw.org/reports/pdfs/s/somalia/somalia922.pdf",
        "Africa Watch",
        "human_rights_investigative_report",
        "africa_watch_somalia_reporting_1992",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_somali_rebels_amnesty_somalia_1992",
        "Somalia: A Human Rights Disaster",
        "https://www.amnesty.org/ar/wp-content/uploads/2021/06/afr520011992en.pdf",
        "Amnesty International",
        "human_rights_investigative_report",
        "amnesty_international_somalia_reporting_1992",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_somali_rebels_us_army_somalia_1992_1994",
        "United States Forces, Somalia After Action Report and Historical Overview",
        (
            "https://history.army.mil/portals/143/Images/Publications/"
            "catalog/70-81-1.pdf"
        ),
        "U.S. Army Center of Military History",
        "official_military_history",
        "us_army_center_military_history",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_somali_rebels_us_army_fm_3_06_somalia",
        "Urban Operations, FM 3-06, Appendix C: Mogadishu",
        "https://irp.fas.org/doddir/army/fm3-06.pdf",
        "Department of the Army",
        "official_military_doctrine",
        "us_army_doctrine_fm_3_06",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_somali_rebels_cassidy_bsdr_2008",
        "Counterinsurgency and Military Culture: State Regulars versus Non-State Irregulars",
        "https://media.voog.com/0000/0051/2796/files/BSDR_10.pdf",
        "Baltic Security and Defence Review",
        "scholarly_military_analysis",
        "cassidy_counterinsurgency_military_culture_2008",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
)
_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_SOMALI_REBELS_SOURCES
}


WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_SOURCES: dict[str, dict[str, Any]] = {
    "jardine_mad_mullah_somaliland_1923": {
        "title": "The Mad Mullah of Somaliland",
        "url": "https://archive.org/details/TheMadMullahOfSomaliland",
        "publisher": "Herbert Jenkins Ltd.",
        "license": "linked_reference",
        "source_type": "digitized_administration_history",
        "accessed": "2026-07-16",
        "source_family_id": "somaliland_administration_history",
        "evidence_roles": ["identity_boundary_or_context_reference", "outcome"],
    },
    "ucdp_termination_dyad": {
        "title": "UCDP Conflict Termination Dataset v4-2024, dyad level",
        "url": (
            "https://ucdp.uu.se/downloads/monadterm/"
            "UCDPConflictTerminationDataset_v4_2024_Dyad.csv"
        ),
        "publisher": "Uppsala Conflict Data Program",
        "license": "CC-BY-4.0",
        "source_type": "structured_dataset",
        "accessed": "2026-07-13",
        "source_family_id": "ucdp_conflict_termination",
        "evidence_roles": ["outcome_consistency_crosscheck"],
    },
}
_SOURCE_FAMILY_BY_ID = {
    **{
        source_id: str(source["source_family_id"])
        for source_id, source in _SOURCE_BY_ID.items()
    },
    **{
        source_id: str(source["source_family_id"])
        for source_id, source in WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_SOURCES.items()
    },
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    note: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start_year,
        "end_year": end_year,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_SOMALI_REBELS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _USC_MOGADISHU,
        "United Somali Congress Mogadishu force (1990–1991)",
        "campaign_bounded_insurgent_force",
        1990,
        1991,
        "Mogadishu, Somalia",
        (
            "Alias-free identity bounded to the USC forces in the 30 December "
            "1990–26 January 1991 Mogadishu campaign. It does not inherit or "
            "transfer a rating to USC/SSA, USC/SNA, SRRC, Somali ethnicity, "
            "Somalia, a generic Somali Rebels label, or any successor faction."
        ),
        {
            "ucdp_termination_dyad",
            "wave8_somali_rebels_africa_watch_somalia_1992",
            "wave8_somali_rebels_amnesty_somalia_1992",
        },
    ),
    _entity(
        _BARRE_LOYALISTS,
        "Siad Barre loyalist forces in Mogadishu (1990–1991)",
        "campaign_bounded_government_force",
        1990,
        1991,
        "Mogadishu, Somalia",
        (
            "Alias-free identity bounded to the government and loyalist forces "
            "defending Mogadishu through Barre's expulsion on 26 January 1991. "
            "It is not Somalia as a timeless polity and inherits or transfers no "
            "rating to later governments, militias, or armed forces."
        ),
        {
            "ucdp_termination_dyad",
            "wave8_somali_rebels_africa_watch_somalia_1992",
            "wave8_somali_rebels_amnesty_somalia_1992",
        },
    ),
    _entity(
        _SNA_AIDID,
        "Somali National Alliance Aidid force in Mogadishu (1993)",
        "engagement_bounded_militia_force",
        1993,
        1993,
        "Mogadishu, Somalia",
        (
            "Alias-free identity bounded to Aidid-aligned SNA combatants in the "
            "3–4 October 1993 battle. It receives no rating continuity from the "
            "1990–1991 USC force and transfers none to USC/SSA, SRRC, Somalia, "
            "Somali ethnicity, or a generic Somali Rebels identity."
        ),
        {
            "wave8_somali_rebels_cassidy_bsdr_2008",
            "wave8_somali_rebels_us_army_fm_3_06_somalia",
            "wave8_somali_rebels_us_army_somalia_1992_1994",
        },
    ),
    _entity(
        _TASK_FORCE_RANGER,
        "Task Force Ranger in Mogadishu (3–4 October 1993)",
        "engagement_bounded_joint_task_force",
        1993,
        1993,
        "Mogadishu, Somalia",
        (
            "Alias-free identity for Task Force Ranger during the reviewed raid "
            "and extraction battle only. It is not the United States as a polity "
            "and transfers no rating to U.S., UNOSOM, UNITAF, or later forces."
        ),
        {
            "wave8_somali_rebels_cassidy_bsdr_2008",
            "wave8_somali_rebels_us_army_fm_3_06_somalia",
            "wave8_somali_rebels_us_army_somalia_1992_1994",
        },
    ),
    _entity(
        _RELIEF_FORCE,
        "Mogadishu multinational relief force (3–4 October 1993)",
        "engagement_bounded_multinational_relief_force",
        1993,
        1993,
        "Mogadishu, Somalia",
        (
            "Alias-free identity for the U.S. 10th Mountain/2-14 Infantry quick "
            "reaction force and participating Pakistani and Malaysian relief "
            "elements in the reviewed extraction. Constituent states and units "
            "do not inherit or transfer this event-bounded rating."
        ),
        {
            "wave8_somali_rebels_cassidy_bsdr_2008",
            "wave8_somali_rebels_us_army_fm_3_06_somalia",
            "wave8_somali_rebels_us_army_somalia_1992_1994",
        },
    ),
)


WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_ENTITIES: dict[str, dict[str, Any]] = {
    _DERVISH: {
        "name": "Somali Dervish movement (1899–1920)",
        "kind": "anti_colonial_movement_force",
        "start_year": 1899,
        "end_year": 1920,
        "aliases": [],
    },
    _SOMALIA: {
        "name": "Federal Republic of Somalia",
        "kind": "republic",
        "start_year": 1960,
        "end_year": 2024,
        "aliases": ["Somalia"],
    },
}


WAVE8_SOMALI_REBELS_ROW_HASHES: dict[str, str] = {
    "hced-Dul Madoba1913-1": (
        "a809d229ef24cd2f51d6510b6a5744de6dc33c84443f581175ab4dc659e12fa0"
    ),
    "hced-Mogadishu1990-1991-1": (
        "4e3a742792f47363cc7c9078550a805170d1faf489e6d5afc44c952aec9e0c0a"
    ),
    "hced-Mogadishu1993-1": (
        "76cc570e28c934282e969be3bb281b79788a06c8f1175f50a799da151a8e470a"
    ),
}
WAVE8_SOMALI_REBELS_FULL_ROW_HASHES: dict[str, str] = {
    "hced-Dul Madoba1913-1": (
        "973a52f82a270f2ba9adf225134b52e111adba8dd351cd0429a1bff03d33e05a"
    ),
    "hced-Mogadishu1990-1991-1": (
        "bd201fdd4e0d25c8ea03134dcc68acf33c6d8fd9877cb4c7fad1c781e815f803"
    ),
    "hced-Mogadishu1993-1": (
        "57503b7c3a9de5c4a72b83ec0d4ff383e8fa3cdc42cd0cc1bc85c704f06fe7c6"
    ),
}


WAVE8_SOMALI_REBELS_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "d9324955fff792afc7a9699d4124757878b0a0e7601e9663ab37a2e5bed5182d"
    ),
    "events_touched": 3,
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 3,
    },
    "label": _EXACT_LABEL,
    "rated_counterpart_entities": 2,
    "sole_blocker_events": 2,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 3,
}


def _canonical(
    name: str,
    year_low: int,
    year_high: int,
    date_text: str,
    start_date: str,
    end_date: str,
    granularity: str,
    *,
    date_precision: str = "day_range",
    approximate_times: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "canonical_key": f"{_slug(name)}:{year_low}:{year_high}",
        "date_precision": date_precision,
        "date_text": date_text,
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": year_high,
    }
    if approximate_times:
        result["approximate_local_times"] = dict(sorted(approximate_times.items()))
    return result


_EVENT_SOURCE_IDS: dict[str, tuple[str, ...]] = {
    "hced-Mogadishu1990-1991-1": (
        "ucdp_termination_dyad",
        "wave8_somali_rebels_africa_watch_somalia_1992",
        "wave8_somali_rebels_amnesty_somalia_1992",
    ),
    "hced-Mogadishu1993-1": (
        "wave8_somali_rebels_cassidy_bsdr_2008",
        "wave8_somali_rebels_us_army_fm_3_06_somalia",
        "wave8_somali_rebels_us_army_somalia_1992_1994",
    ),
}
_EVENT_OUTCOME_SOURCE_IDS: dict[str, tuple[str, ...]] = {
    "hced-Mogadishu1990-1991-1": (
        "wave8_somali_rebels_africa_watch_somalia_1992",
        "wave8_somali_rebels_amnesty_somalia_1992",
    ),
    "hced-Mogadishu1993-1": (
        "wave8_somali_rebels_cassidy_bsdr_2008",
        "wave8_somali_rebels_us_army_fm_3_06_somalia",
        "wave8_somali_rebels_us_army_somalia_1992_1994",
    ),
}


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    audit_note: str,
    *,
    winner_side: int,
    event_type: str,
    confidence: float,
    source_outcome_override: bool,
    expected_scale_level: int,
    reviewed_decisiveness: float,
) -> dict[str, Any]:
    evidence = sorted(_EVENT_SOURCE_IDS[candidate_id])
    outcomes = sorted(_EVENT_OUTCOME_SOURCE_IDS[candidate_id])
    return {
        "raw_row_sha256": WAVE8_SOMALI_REBELS_ROW_HASHES[candidate_id],
        "full_row_sha256": WAVE8_SOMALI_REBELS_FULL_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "side_1_entity_ids": list(map(str, side_1_entity_ids)),
        "side_2_entity_ids": list(map(str, side_2_entity_ids)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": winner_side,
        "event_type": event_type,
        "war_type": "internationalized_civil_war",
        "confidence": confidence,
        "reviewed_decisiveness": reviewed_decisiveness,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "date_source_ids": evidence,
        "source_date_refinement": True,
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": source_outcome_override,
        "actor_override": "candidate_keyed_alias_free_bounded_forces",
        "expected_scale_level": expected_scale_level,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_SOMALI_REBELS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Mogadishu1990-1991-1": _contract(
        "hced-Mogadishu1990-1991-1",
        _canonical(
            "Mogadishu urban campaign",
            1990,
            1991,
            "30 December 1990–26 January 1991",
            "1990-12-30",
            "1991-01-26",
            "urban_campaign_ending_in_barre_expulsion",
        ),
        [_USC_MOGADISHU],
        [_BARRE_LOYALISTS],
        (
            "Africa Watch and Amnesty independently describe weeks of urban "
            "fighting ending when the USC drove Siad Barre and his loyalists "
            "from Mogadishu. UCDP's broader dyad episode corroborates the 26 "
            "January endpoint but is not emitted as a second tactical event. "
            "The result is operational control of the capital, not a stable "
            "national settlement or the outcome of the Somali Civil War."
        ),
        winner_side=1,
        event_type="campaign",
        confidence=0.95,
        source_outcome_override=False,
        expected_scale_level=2,
        reviewed_decisiveness=0.76,
    ),
    "hced-Mogadishu1993-1": _contract(
        "hced-Mogadishu1993-1",
        _canonical(
            "Battle of Mogadishu",
            1993,
            1993,
            "3–4 October 1993",
            "1993-10-03",
            "1993-10-04",
            "direct_action_raid_relief_and_extraction_battle",
            approximate_times={
                "end": "06:30 on 4 October",
                "start": "15:30 on 3 October",
            },
        ),
        [_SNA_AIDID],
        [_TASK_FORCE_RANGER, _RELIEF_FORCE],
        (
            "HCED's raw Somali-rebel win is reversed only for the bounded raid, "
            "relief, and extraction engagement. The U.S. Army history records "
            "capture of the intended detainees and extraction; Army doctrine and "
            "independent scholarship characterize a tactical or Pyrrhic success "
            "that produced operational and political failure. Those wider layers "
            "are expressly excluded, so the intervention and later withdrawal "
            "receive no result here."
        ),
        winner_side=2,
        event_type="engagement",
        confidence=0.91,
        source_outcome_override=True,
        expected_scale_level=1,
        reviewed_decisiveness=0.34,
    ),
}


WAVE8_SOMALI_REBELS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Dul Madoba1913-1": {
        "raw_row_sha256": WAVE8_SOMALI_REBELS_ROW_HASHES[
            "hced-Dul Madoba1913-1"
        ],
        "full_row_sha256": WAVE8_SOMALI_REBELS_FULL_ROW_HASHES[
            "hced-Dul Madoba1913-1"
        ],
        "canonical_event": _canonical(
            "Dul Madoba engagement",
            1913,
            1913,
            "9 August 1913",
            "1913-08-09",
            "1913-08-09",
            "five_hour_pursuit_engagement_after_livestock_raid",
            date_precision="day",
        ),
        "cohort": _COHORT,
        "disposition": "hold",
        "terminal_exclusion": False,
        "emit_rated_event": False,
        "hold_category": "conflicting_tactical_and_operational_outcome_layers",
        "reviewed_outcome": "unknown_not_draw",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "bound_scoring_sides": [],
        "candidate_actor_boundaries": {
            "side_1_if_reopened": [
                "somaliland_camel_constabulary_dul_madoba_1913"
            ],
            "side_2_context_only": [_DERVISH],
            "excluded_context": ["local_dhulbahante_auxiliaries"],
        },
        "evidence_refs": sorted(
            {
                "jardine_mad_mullah_somaliland_1923",
                "wave8_somali_rebels_durham_archer_dul_madoba",
                "wave8_somali_rebels_hansard_dul_madoba_1914",
                "wave8_somali_rebels_kakwenzire_dul_madoba_1984",
            }
        ),
        "hold_reason": (
            "The sources support a real five-hour engagement on 9 August 1913, "
            "but battlefield withdrawal and reported Dervish losses conflict "
            "with the Camel Constabulary's severe destruction, failure to recover "
            "the raided stock, and the political assessment of a Dervish victory. "
            "No single reviewed result layer is defensible: unknown is not a draw."
        ),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "review_hold_owner",
        },
    }
}


WAVE8_SOMALI_REBELS_CONTRACT_IDS = frozenset(WAVE8_SOMALI_REBELS_CONTRACTS)
WAVE8_SOMALI_REBELS_HOLD_IDS = frozenset(WAVE8_SOMALI_REBELS_HOLDS)
WAVE8_SOMALI_REBELS_RESERVED_IDS = frozenset(WAVE8_SOMALI_REBELS_ROW_HASHES)


# All three HCED points are unsourced point proxies.  The two promoted urban
# events retain modern-country Somalia; the held Dul Madoba row emits nothing.
WAVE8_SOMALI_REBELS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_SOMALI_REBELS_RESERVED_IDS
)
WAVE8_SOMALI_REBELS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_SOMALI_REBELS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Dul Madoba1913-1": {
        "actions": ["withhold_point"],
        "raw_point": [45.7682263, 9.1758243],
        "retained_country": "Somalia",
        "evidence_refs": [
            "wave8_somali_rebels_durham_archer_dul_madoba",
            "wave8_somali_rebels_kakwenzire_dul_madoba_1984",
        ],
        "reason": (
            "The raw point is a similarly named gazetteer proxy about 13.9 km "
            "from the reported engagement area and is not an audited battlefield."
        ),
    },
    "hced-Mogadishu1990-1991-1": {
        "actions": ["withhold_point"],
        "raw_point": [45.3181623, 2.0469343],
        "retained_country": "Somalia",
        "evidence_refs": [
            "wave8_somali_rebels_africa_watch_somalia_1992",
            "wave8_somali_rebels_amnesty_somalia_1992",
        ],
        "reason": (
            "A modern city centroid cannot represent a month-long urban campaign "
            "with shifting fronts and the final loyalist withdrawal."
        ),
    },
    "hced-Mogadishu1993-1": {
        "actions": ["withhold_point"],
        "raw_point": [45.3181623, 2.0469343],
        "retained_country": "Somalia",
        "evidence_refs": [
            "wave8_somali_rebels_us_army_fm_3_06_somalia",
            "wave8_somali_rebels_us_army_somalia_1992_1994",
        ],
        "reason": (
            "The target building, two crash sites, convoy routes, and stadium "
            "form a distributed battle footprint, not one city-centroid point."
        ),
    },
}


WAVE8_SOMALI_REBELS_WIKIDATA_MATCHES: dict[str, str] = {
    "Q109561628": "hced-Dul Madoba1913-1",
    "Q52226": "hced-Mogadishu1993-1",
}
WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES: dict[str, str] = {
    "Q109561628": (
        "1b233abc666e82a0270797ac66825fe3aee023e9596919c8467f9878c77becc0"
    ),
    "Q52226": (
        "baf0e3a8b5fa976c6d96e6687c478c4d6388c278d81e6ac844e6ac3024bd5bcd"
    ),
}
WAVE8_SOMALI_REBELS_WIKIDATA_EXPECTED: dict[str, dict[str, Any]] = {
    "Q109561628": {
        "date": "1913-08-04T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Dul Madoba",
        "participant_labels": ["British Empire", "Dervish movement"],
        "relationship": "exact_discovery_duplicate_for_unknown_hold",
        "outcome_disposition": "unknown_never_draw",
        "date_disposition": "quarantine_discovery_date_use_reviewed_1913_08_09",
    },
    "Q52226": {
        "date": "1993-10-03T00:00:00Z",
        "end_date": "1993-10-04T00:00:00Z",
        "kind": "engagement",
        "name": "Battle of Mogadishu",
        "participant_labels": ["Somalia", "United States"],
        "relationship": "exact_discovery_duplicate_with_generic_participants",
        "outcome_disposition": "unknown_never_draw",
        "participant_disposition": "quarantine_generic_polity_participants",
    },
}
WAVE8_SOMALI_REBELS_DISCOVERY_DATE_QUARANTINES: dict[str, dict[str, str]] = {
    "Q109561628": {
        "discovery_date": "1913-08-04T00:00:00Z",
        "reviewed_date": "1913-08-09",
        "reason": "discovery_date_conflicts_with_independent_reviewed_sources",
    }
}


WAVE8_SOMALI_REBELS_UCDP_ROW_HASHES: dict[str, str] = {
    "ucdp-actor-26.1-493--493": (
        "4ea1416a5ed4c8d50fd73d8a43f70855616930f5972d00398deb543d8502becf"
    ),
    "ucdp-actor-26.1-494--494": (
        "8b059a46a135abdb873faeda44c97a9b0003fe3fb5e1dcec72d4bbd22c701961"
    ),
    "ucdp-termination-dyad-337-2158": (
        "43ac624afc8e1478c9120b0390cb821f9a086c00269ab5cf660e629aed9ca368"
    ),
    "ucdp-dyadic-26.1-746-1990-2174": (
        "6b687a6efddee0962426fc179e318bfd1fbecb397ecf6a938c0b395267772fd9"
    ),
    "ucdp-dyadic-26.1-746-1991-2175": (
        "ea1733b3a9df7839b96182f225599c61036065638ad7d64d7db1b98ce2d6da44"
    ),
    "ucdp-conflict-26.1-337-1990-1787": (
        "9f75a1c9d9c55717c61e5ee43bed97dda15b996290a18b5f4b09f479fbdc94c9"
    ),
    "ucdp-conflict-26.1-337-1991-1788": (
        "36753f2442e3e9f43f1a5e2f6d24f2749ca177b46636f456dfb2d9a1c4589d5f"
    ),
    "ucdp-termination-dyad-337-2161": (
        "251381e4b10ff6a65410aec3b7b33aa4b81b6a1fc4eef1e1608131cb1165e2a6"
    ),
    "ucdp-dyadic-26.1-747-1993-2178": (
        "0acb59e5dfe3401ba31fb3ede411588e236d3c1af5be306fcdef23fe9c4a1c9e"
    ),
    "ucdp-conflict-26.1-337-1993-1790": (
        "a7e7bf432f58f9d898068808755df29a1bf601e63ba069d6bfc3acc3f5597a2e"
    ),
}


def _ucdp_disposition(
    owner: str,
    scope: str,
    disposition: str,
    outcome_disposition: str,
) -> dict[str, Any]:
    return {
        "owner_hced_candidate_id": owner,
        "conflict_id": "337",
        "scope": scope,
        "disposition": disposition,
        "outcome_disposition": outcome_disposition,
        "automated_rating": False,
    }


WAVE8_SOMALI_REBELS_UCDP_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "ucdp-actor-26.1-493--493": _ucdp_disposition(
        "hced-Mogadishu1990-1991-1",
        "actor_identity_record",
        "identity_evidence_only_no_rating_continuity",
        "no_event_outcome",
    ),
    "ucdp-actor-26.1-494--494": _ucdp_disposition(
        "hced-Mogadishu1993-1",
        "actor_identity_record",
        "identity_evidence_only_no_rating_continuity",
        "no_event_outcome",
    ),
    "ucdp-termination-dyad-337-2158": _ucdp_disposition(
        "hced-Mogadishu1990-1991-1",
        "broader_strategic_dyad_episode",
        "endpoint_crosscheck_not_second_rated_event",
        "strategic_side_b_outcome_not_imported_as_tactical_result",
    ),
    "ucdp-dyadic-26.1-746-1990-2174": _ucdp_disposition(
        "hced-Mogadishu1990-1991-1",
        "annual_dyad_record",
        "broader_context_not_named_tactical_duplicate",
        "intensity_is_not_victory",
    ),
    "ucdp-dyadic-26.1-746-1991-2175": _ucdp_disposition(
        "hced-Mogadishu1990-1991-1",
        "annual_dyad_record",
        "broader_context_not_named_tactical_duplicate",
        "intensity_is_not_victory",
    ),
    "ucdp-conflict-26.1-337-1990-1787": _ucdp_disposition(
        "hced-Mogadishu1990-1991-1",
        "annual_multiactor_conflict_record",
        "broader_context_not_named_tactical_duplicate",
        "intensity_is_not_victory",
    ),
    "ucdp-conflict-26.1-337-1991-1788": _ucdp_disposition(
        "hced-Mogadishu1990-1991-1",
        "annual_multiactor_conflict_record",
        "broader_context_not_named_tactical_duplicate",
        "intensity_is_not_victory",
    ),
    "ucdp-termination-dyad-337-2161": _ucdp_disposition(
        "hced-Mogadishu1993-1",
        "government_versus_usc_sna_strategic_episode",
        "different_dyad_not_us_led_battle_duplicate",
        "unknown_never_draw",
    ),
    "ucdp-dyadic-26.1-747-1993-2178": _ucdp_disposition(
        "hced-Mogadishu1993-1",
        "government_versus_usc_sna_annual_dyad",
        "different_dyad_not_us_led_battle_duplicate",
        "intensity_is_not_victory",
    ),
    "ucdp-conflict-26.1-337-1993-1790": _ucdp_disposition(
        "hced-Mogadishu1993-1",
        "government_versus_usc_sna_annual_conflict",
        "different_dyad_not_us_led_battle_duplicate",
        "intensity_is_not_victory",
    ),
}


WAVE8_SOMALI_REBELS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"wikidata:{candidate_id}": {
            "source_dataset": "wikidata-battles",
            "disposition": (
                "discovery_only_context_for_unknown_hold"
                if owner in WAVE8_SOMALI_REBELS_HOLD_IDS
                else "discovery_only_duplicate"
            ),
            "hced_candidate_id": owner,
            "outcome_disposition": "unknown_never_draw",
            "relationship": WAVE8_SOMALI_REBELS_WIKIDATA_EXPECTED[candidate_id][
                "relationship"
            ],
        }
        for candidate_id, owner in sorted(
            WAVE8_SOMALI_REBELS_WIKIDATA_MATCHES.items()
        )
    },
    **{
        f"ucdp:{candidate_id}": {
            "source_dataset": "ucdp",
            **dict(disposition),
        }
        for candidate_id, disposition in sorted(
            WAVE8_SOMALI_REBELS_UCDP_DISPOSITIONS.items()
        )
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(map(str, values)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_SOMALI_REBELS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_SOMALI_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_date_quarantines": (
            WAVE8_SOMALI_REBELS_DISCOVERY_DATE_QUARANTINES
        ),
        "entities": WAVE8_SOMALI_REBELS_ENTITIES,
        "full_row_hashes": WAVE8_SOMALI_REBELS_FULL_ROW_HASHES,
        "funnel": WAVE8_SOMALI_REBELS_FUNNEL_AUDIT,
        "holds": WAVE8_SOMALI_REBELS_HOLDS,
        "integration_dispositions": WAVE8_SOMALI_REBELS_INTEGRATION_DISPOSITIONS,
        "location_reasons": WAVE8_SOMALI_REBELS_LOCATION_QUARANTINE_REASONS,
        "point_quarantine_additions": sorted(
            WAVE8_SOMALI_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "required_existing_entities": (
            WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_ENTITIES
        ),
        "required_existing_sources": (
            WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_SOURCES
        ),
        "row_hashes": WAVE8_SOMALI_REBELS_ROW_HASHES,
        "sources": WAVE8_SOMALI_REBELS_SOURCES,
        "ucdp_dispositions": WAVE8_SOMALI_REBELS_UCDP_DISPOSITIONS,
        "ucdp_row_hashes": WAVE8_SOMALI_REBELS_UCDP_ROW_HASHES,
        "wikidata_expected": WAVE8_SOMALI_REBELS_WIKIDATA_EXPECTED,
        "wikidata_matches": WAVE8_SOMALI_REBELS_WIKIDATA_MATCHES,
        "wikidata_row_hashes": WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES,
    }


def wave8_somali_rebels_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_SOMALI_REBELS_FINAL_AUDIT_SIGNATURE = (
    "3f2557082f71a3d581665ad35356aa6a1c455a06c1cc23dba33703fa675baed5"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static(*, check_signature: bool = True) -> None:
    source_ids = set(_SOURCE_BY_ID)
    required_source_ids = set(WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_SOURCES)
    available_source_ids = source_ids | required_source_ids
    if len(source_ids) != len(WAVE8_SOMALI_REBELS_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if source_ids & required_source_ids:
        raise ValueError(f"{_LANE_NAME} new/existing source inventory overlap")
    for source_id, source in _SOURCE_BY_ID.items():
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source role order drift: {source_id}")

    entities = {
        str(entity["id"]): entity for entity in WAVE8_SOMALI_REBELS_ENTITIES
    }
    expected_entities = {
        _USC_MOGADISHU,
        _BARRE_LOYALISTS,
        _SNA_AIDID,
        _TASK_FORCE_RANGER,
        _RELIEF_FORCE,
    }
    if set(entities) != expected_entities or len(entities) != 5:
        raise ValueError(f"{_LANE_NAME} identity inventory drift")
    for entity_id, entity in entities.items():
        if (
            entity["aliases"]
            or entity["predecessors"]
            or normalize_label(entity["name"]) == _EXACT_LABEL
            or not _is_sorted_unique(entity["source_ids"])
            or not set(map(str, entity["source_ids"])) <= available_source_ids
            or "rating" not in str(entity["continuity_note"]).casefold()
        ):
            raise ValueError(f"{_LANE_NAME} identity firewall drift: {entity_id}")
    if (entities[_USC_MOGADISHU]["start_year"], entities[_USC_MOGADISHU]["end_year"]) != (
        1990,
        1991,
    ) or (
        entities[_BARRE_LOYALISTS]["start_year"],
        entities[_BARRE_LOYALISTS]["end_year"],
    ) != (1990, 1991):
        raise ValueError(f"{_LANE_NAME} 1990-1991 identity window drift")
    for entity_id in (_SNA_AIDID, _TASK_FORCE_RANGER, _RELIEF_FORCE):
        if (entities[entity_id]["start_year"], entities[entity_id]["end_year"]) != (
            1993,
            1993,
        ):
            raise ValueError(f"{_LANE_NAME} 1993 identity window drift: {entity_id}")

    if set(WAVE8_SOMALI_REBELS_ROW_HASHES) != set(
        WAVE8_SOMALI_REBELS_FULL_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} row-hash inventory drift")
    if WAVE8_SOMALI_REBELS_RESERVED_IDS != set(
        WAVE8_SOMALI_REBELS_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} reservation inventory drift")
    if (
        WAVE8_SOMALI_REBELS_CONTRACT_IDS | WAVE8_SOMALI_REBELS_HOLD_IDS
    ) != WAVE8_SOMALI_REBELS_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} disposition partition drift")
    if WAVE8_SOMALI_REBELS_CONTRACT_IDS & WAVE8_SOMALI_REBELS_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if (len(WAVE8_SOMALI_REBELS_CONTRACTS), len(WAVE8_SOMALI_REBELS_HOLDS)) != (
        2,
        1,
    ):
        raise ValueError(f"{_LANE_NAME} disposition count drift")

    if _sorted_newline_sha256(WAVE8_SOMALI_REBELS_RESERVED_IDS) != (
        "d9324955fff792afc7a9699d4124757878b0a0e7601e9663ab37a2e5bed5182d"
    ):
        raise ValueError(f"{_LANE_NAME} reviewed candidate set changed")
    if _sorted_newline_sha256(WAVE8_SOMALI_REBELS_CONTRACT_IDS) != (
        "6566170fab122e976eeeeab200d7d42d8c72f6f6dc09aa86306427e46035c2a0"
    ):
        raise ValueError(f"{_LANE_NAME} promotion candidate set changed")
    if _sorted_newline_sha256(WAVE8_SOMALI_REBELS_HOLD_IDS) != (
        "97b8407a2349d598f8de26dfeeecf61f556e816534de62010b66452700be7ecd"
    ):
        raise ValueError(f"{_LANE_NAME} hold candidate set changed")
    if _sorted_newline_sha256(entities) != (
        "e4b2ab9ed02ad635627263358dbc8f97bafaf8e306860366d124ef52627d7089"
    ):
        raise ValueError(f"{_LANE_NAME} identity id set changed")
    if _sorted_newline_sha256(WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES) != (
        "352c52d0317290ee77978a9578cf766ef3958d790286d92f528a77c462e462b0"
    ):
        raise ValueError(f"{_LANE_NAME} Wikidata twin set changed")

    if WAVE8_SOMALI_REBELS_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_SOMALI_REBELS_RESERVED_IDS
    ) or WAVE8_SOMALI_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} location quarantine inventory drift")
    if set(WAVE8_SOMALI_REBELS_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_SOMALI_REBELS_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    expected_contracts = {
        "hced-Mogadishu1990-1991-1": {
            "name": "Mogadishu urban campaign",
            "years": (1990, 1991),
            "dates": ("1990-12-30", "1991-01-26"),
            "granularity": "urban_campaign_ending_in_barre_expulsion",
            "sides": ([_USC_MOGADISHU], [_BARRE_LOYALISTS]),
            "winner_side": 1,
            "event_type": "campaign",
            "confidence": 0.95,
            "decisiveness": 0.76,
            "override": False,
            "families": 2,
        },
        "hced-Mogadishu1993-1": {
            "name": "Battle of Mogadishu",
            "years": (1993, 1993),
            "dates": ("1993-10-03", "1993-10-04"),
            "granularity": "direct_action_raid_relief_and_extraction_battle",
            "sides": ([_SNA_AIDID], [_TASK_FORCE_RANGER, _RELIEF_FORCE]),
            "winner_side": 2,
            "event_type": "engagement",
            "confidence": 0.91,
            "decisiveness": 0.34,
            "override": True,
            "families": 3,
        },
    }
    used_sources = {
        str(source_id)
        for entity in WAVE8_SOMALI_REBELS_ENTITIES
        for source_id in entity["source_ids"]
    }
    for candidate_id, expected in expected_contracts.items():
        contract = WAVE8_SOMALI_REBELS_CONTRACTS[candidate_id]
        canonical = contract["canonical_event"]
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != expected["winner_side"]
            or contract["side_1_entity_ids"] != expected["sides"][0]
            or contract["side_2_entity_ids"] != expected["sides"][1]
            or contract["event_type"] != expected["event_type"]
            or contract["confidence"] != expected["confidence"]
            or contract["reviewed_decisiveness"] != expected["decisiveness"]
            or contract["source_outcome_override"] is not expected["override"]
            or contract["outcome_reversal"] is not expected["override"]
            or canonical["name"] != expected["name"]
            or (canonical["year_low"], canonical["year_high"])
            != expected["years"]
            or (canonical["start_date"], canonical["end_date"])
            != expected["dates"]
            or canonical["granularity"] != expected["granularity"]
            or canonical["date_precision"] != "day_range"
        ):
            raise ValueError(f"{_LANE_NAME} exact contract drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or outcomes != sorted(_EVENT_OUTCOME_SOURCE_IDS[candidate_id])
            or not set(outcomes) <= set(evidence)
            or families
            != sorted({_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes})
            or len(families) != expected["families"]
            or contract["date_source_ids"] != evidence
            or contract["source_date_refinement"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} source closure drift: {candidate_id}")
        used_sources.update(evidence)

    hold = WAVE8_SOMALI_REBELS_HOLDS["hced-Dul Madoba1913-1"]
    if (
        hold["disposition"] != "hold"
        or hold["terminal_exclusion"] is not False
        or hold["emit_rated_event"] is not False
        or hold["hold_category"]
        != "conflicting_tactical_and_operational_outcome_layers"
        or hold["reviewed_outcome"] != "unknown_not_draw"
        or hold["result_type"] != "unknown"
        or hold["unknown_is_never_draw"] is not True
        or hold["bound_scoring_sides"]
        or "winner_side" in hold
        or "unknown is not a draw" not in hold["hold_reason"].casefold()
    ):
        raise ValueError(f"{_LANE_NAME} unknown-not-draw hold drift")
    used_sources.update(map(str, hold["evidence_refs"]))
    for reason in WAVE8_SOMALI_REBELS_LOCATION_QUARANTINE_REASONS.values():
        if reason["actions"] != ["withhold_point"]:
            raise ValueError(f"{_LANE_NAME} location action drift")
        used_sources.update(map(str, reason["evidence_refs"]))
    if used_sources != available_source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    wikidata_ids = set(WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES)
    if (
        set(WAVE8_SOMALI_REBELS_WIKIDATA_MATCHES) != wikidata_ids
        or set(WAVE8_SOMALI_REBELS_WIKIDATA_EXPECTED) != wikidata_ids
        or set(WAVE8_SOMALI_REBELS_WIKIDATA_MATCHES.values())
        != {"hced-Dul Madoba1913-1", "hced-Mogadishu1993-1"}
        or set(WAVE8_SOMALI_REBELS_DISCOVERY_DATE_QUARANTINES)
        != {"Q109561628"}
    ):
        raise ValueError(f"{_LANE_NAME} Wikidata inventory drift")
    if set(WAVE8_SOMALI_REBELS_UCDP_ROW_HASHES) != set(
        WAVE8_SOMALI_REBELS_UCDP_DISPOSITIONS
    ) or len(WAVE8_SOMALI_REBELS_UCDP_ROW_HASHES) != 10:
        raise ValueError(f"{_LANE_NAME} UCDP inventory drift")
    if any(
        disposition["automated_rating"] is not False
        for disposition in WAVE8_SOMALI_REBELS_UCDP_DISPOSITIONS.values()
    ):
        raise ValueError(f"{_LANE_NAME} UCDP automatic-rating guard drift")
    if set(WAVE8_SOMALI_REBELS_INTEGRATION_DISPOSITIONS) != {
        *(f"wikidata:{candidate_id}" for candidate_id in wikidata_ids),
        *(
            f"ucdp:{candidate_id}"
            for candidate_id in WAVE8_SOMALI_REBELS_UCDP_ROW_HASHES
        ),
    }:
        raise ValueError(f"{_LANE_NAME} integration disposition drift")
    if check_signature and WAVE8_SOMALI_REBELS_FINAL_AUDIT_SIGNATURE != (
        "TO_BE_SEALED"
    ) and wave8_somali_rebels_audit_signature() != (
        WAVE8_SOMALI_REBELS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_somali_rebels_existing_boundaries(
    release_entities: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    """Pin existing Dervish/Somalia windows and reject a generic rebel alias."""

    _validate_static()
    for entity_id, expected in WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_ENTITIES.items():
        entity = release_entities.get(entity_id)
        if entity is None:
            raise ValueError(f"{_LANE_NAME} missing existing identity {entity_id}")
        projection = {key: entity.get(key) for key in expected}
        if projection != expected:
            raise ValueError(
                f"{_LANE_NAME} existing identity drift for {entity_id}: {projection}"
            )
    forbidden = sorted(
        str(entity.get("id"))
        for entity in release_entities.values()
        if any(
            normalize_label(alias) == _EXACT_LABEL
            for alias in entity.get("aliases", []) or []
        )
    )
    if forbidden:
        raise ValueError(
            f"{_LANE_NAME} generic Somali Rebels alias introduced: {forbidden}"
        )
    return {
        "forbidden_generic_aliases": 0,
        "required_existing_entities": len(
            WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_ENTITIES
        ),
    }


def validate_wave8_somali_rebels_required_sources(
    release_sources: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    for source_id, expected in WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_SOURCES.items():
        source = release_sources.get(source_id)
        if source is None:
            raise ValueError(f"{_LANE_NAME} missing existing source {source_id}")
        projection = {key: source.get(key) for key in expected}
        if projection != expected:
            raise ValueError(
                f"{_LANE_NAME} existing source drift for {source_id}: {projection}"
            )
    return {
        "required_existing_sources": len(
            WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_SOURCES
        )
    }


def validate_wave8_somali_rebels_queue_contracts(
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
    if exact_ids != WAVE8_SOMALI_REBELS_RESERVED_IDS or len(exact) != len(
        exact_ids
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    expected = {
        "hced-Dul Madoba1913-1": {
            "name": "Dul Madoba",
            "years": (1913, 1913, 1913),
            "sides": ("United Kingdom", "Somali Rebels"),
            "outcome": ("United Kingdom", "Somali Rebels"),
            "participants": [
                "Somaliland",
                "British",
                "Mullahs",
                "Idoweina",
                "Dervishes",
                "British",
            ],
            "scale": (None, None),
        },
        "hced-Mogadishu1990-1991-1": {
            "name": "Mogadishu",
            "years": (1990, 1990, 1991),
            "sides": ("Somali Rebels", "Siad Barre Government"),
            "outcome": ("Somali Rebels", "Siad Barre Government"),
            "participants": ["Somalian"],
            "scale": (None, None),
        },
        "hced-Mogadishu1993-1": {
            "name": "Mogadishu",
            "years": (1993, 1993, 1993),
            "sides": ("Somali Rebels", "United States"),
            "outcome": ("Somali Rebels", "United States"),
            "participants": [
                "Somalian",
                "Somalia",
                "Pakistani",
                "Mogadishu",
                "Americans",
                "Somalis",
                "US",
            ],
            "scale": ("1", "1"),
        },
    }
    for candidate_id, expected_hash in WAVE8_SOMALI_REBELS_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if _full_row_sha256(row) != WAVE8_SOMALI_REBELS_FULL_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} full row changed: {candidate_id}")
        semantics = expected[candidate_id]
        if (
            row.get("name") != semantics["name"]
            or (row.get("year_low"), row.get("year_best"), row.get("year_high"))
            != semantics["years"]
            or (row.get("side_1_raw"), row.get("side_2_raw"))
            != semantics["sides"]
            or (row.get("winner_raw"), row.get("loser_raw"))
            != semantics["outcome"]
            or row.get("participants_raw") != semantics["participants"]
            or (row.get("scale_raw"), row.get("scale_inferred_raw"))
            != semantics["scale"]
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("do_not_rate_automatically") is not True
            or row.get("duplicate_source_id") is not False
            or row.get("source") != "hced"
        ):
            raise ValueError(f"{_LANE_NAME} locked source semantics changed: {candidate_id}")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SOMALI_REBELS_CONTRACTS,
        WAVE8_SOMALI_REBELS_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_somali_rebels_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    rows = [
        row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL
    ]
    if len(rows) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    row = rows[0]
    actual = {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "failure_cases": {
            key: int(row.get("failure_cases", {}).get(key, -1))
            for key in WAVE8_SOMALI_REBELS_FUNNEL_AUDIT["failure_cases"]
        },
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
    }
    if actual != WAVE8_SOMALI_REBELS_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pin changed: {actual}")
    return {
        "events_touched": actual["events_touched"],
        "sole_blocker_events": actual["sole_blocker_events"],
        "unresolved_side_attempts": actual["unresolved_side_attempts"],
        "zero_time_valid_candidates": actual["failure_cases"][
            "zero_time_valid_candidates"
        ],
    }


def validate_wave8_somali_rebels_ucdp_dispositions(
    ucdp_rows: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[Mapping[str, Any]]] = {}
    for row in ucdp_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in WAVE8_SOMALI_REBELS_UCDP_ROW_HASHES.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} UCDP row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} UCDP fingerprint changed: {candidate_id}")
        raw = row.get("raw")
        if not isinstance(raw, Mapping):
            raise ValueError(f"{_LANE_NAME} UCDP raw payload missing: {candidate_id}")
        conflict_id = raw.get("ConflictId", raw.get("conflict_id"))
        if (
            row.get("do_not_rate_automatically") is not True
            or not str(row.get("source", "")).startswith("ucdp-")
            or str(conflict_id) != "337"
        ):
            raise ValueError(f"{_LANE_NAME} UCDP nonrating guard changed: {candidate_id}")

    actor_493 = by_id["ucdp-actor-26.1-493--493"][0]["raw"]
    actor_494 = by_id["ucdp-actor-26.1-494--494"][0]["raw"]
    term_1991 = by_id["ucdp-termination-dyad-337-2158"][0]["raw"]
    term_1993 = by_id["ucdp-termination-dyad-337-2161"][0]["raw"]
    if (
        (actor_493.get("ActorId"), actor_493.get("DyadId"), actor_493.get("NameData"))
        != ("502", "746", "USC/SSA")
        or (
            actor_494.get("ActorId"),
            actor_494.get("ActorIdPrev"),
            actor_494.get("DyadId"),
            actor_494.get("NameData"),
        )
        != ("503", "502", "747", "USC/SNA")
        or (
            term_1991.get("dyad_id"),
            term_1991.get("d_ependdate"),
            term_1991.get("d_outcome"),
        )
        != ("746", "1991-01-26", "4")
        or (term_1993.get("dyad_id"), term_1993.get("d_outcome"))
        != ("747", "")
    ):
        raise ValueError(f"{_LANE_NAME} UCDP actor/episode boundary changed")
    return {
        "actor_identity_records": 2,
        "automated_promotions": 0,
        "broader_or_distinct_context_records": 8,
        "ucdp_dispositions": len(WAVE8_SOMALI_REBELS_UCDP_DISPOSITIONS),
    }


def validate_wave8_somali_rebels_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
    ucdp_rows: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in (
        WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} Wikidata row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(
                f"{_LANE_NAME} Wikidata fingerprint changed: {candidate_id}"
            )
        expected = WAVE8_SOMALI_REBELS_WIKIDATA_EXPECTED[candidate_id]
        participant_labels = sorted(
            str(participant.get("label"))
            for participant in row.get("participants", [])
        )
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("name") != expected["name"]
            or row.get("date") != expected["date"]
            or row.get("end_date") != expected["end_date"]
            or row.get("kind") != expected["kind"]
            or participant_labels != expected["participant_labels"]
            or row.get("winners") != []
        ):
            raise ValueError(
                f"{_LANE_NAME} Wikidata nonrating guard changed: {candidate_id}"
            )
    supplied_ucdp = list(ucdp_rows)
    ucdp_count = 0
    if supplied_ucdp:
        ucdp_count = validate_wave8_somali_rebels_ucdp_dispositions(
            supplied_ucdp
        )["ucdp_dispositions"]
    return {
        "automated_promotions": 0,
        "discovery_date_quarantines": len(
            WAVE8_SOMALI_REBELS_DISCOVERY_DATE_QUARANTINES
        ),
        "ucdp_dispositions": ucdp_count,
        "unknown_never_draw_wikidata_rows": len(
            WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES
        ),
        "wikidata_nonrating_records": len(
            WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES
        ),
    }


def _row_years(row: Mapping[str, Any]) -> set[int]:
    years: set[int] = set()
    for key in ("year", "year_best", "year_low", "year_high", "end_year"):
        try:
            if row.get(key) is not None:
                years.add(int(row[key]))
        except (TypeError, ValueError):
            pass
    for key in ("start_date", "end_date", "date"):
        value = str(row.get(key) or "")
        if len(value) >= 4 and value[:4].isdigit():
            years.add(int(value[:4]))
    return years


def _row_names(row: Mapping[str, Any]) -> set[str]:
    values = [
        row.get("name"),
        row.get("battle_name"),
        row.get("batname"),
        row.get("event_name"),
        row.get("war_name"),
    ]
    aliases = row.get("aliases", []) or []
    if isinstance(aliases, str):
        values.append(aliases)
    else:
        values.extend(aliases)
    return {normalize_label(value) for value in values if normalize_label(value)}


_DUPLICATE_KEYS = frozenset(
    {
        (1913, normalize_label("Dul Madoba")),
        (1913, normalize_label("Battle of Dul Madoba")),
        (1990, normalize_label("Mogadishu")),
        (1990, normalize_label("Mogadishu urban campaign")),
        (1991, normalize_label("Mogadishu")),
        (1991, normalize_label("Mogadishu urban campaign")),
        (1993, normalize_label("Mogadishu")),
        (1993, normalize_label("Battle of Mogadishu")),
    }
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    return any(
        (year, name) in _DUPLICATE_KEYS
        for year in _row_years(row)
        for name in _row_names(row)
    )


def validate_wave8_somali_rebels_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwd_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
    *,
    wikidata_rows: Iterable[Mapping[str, Any]] = (),
    ucdp_rows: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on unreviewed twins and on discovery rows entering ratings."""

    validate_wave8_somali_rebels_queue_contracts(hced_rows)
    supplied_wikidata = [dict(row) for row in wikidata_rows]
    supplied_ucdp = list(ucdp_rows)
    if supplied_wikidata:
        validate_wave8_somali_rebels_discovery_dispositions(
            supplied_wikidata,
            supplied_ucdp,
        )
    elif supplied_ucdp:
        validate_wave8_somali_rebels_ucdp_dispositions(supplied_ucdp)

    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_SOMALI_REBELS_RESERVED_IDS
        and _is_probable_twin(row)
    )
    iwd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwd_rows
        if _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )

    existing = list(existing_events)
    released_holds = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_SOMALI_REBELS_HOLD_IDS
    )
    if released_holds:
        raise ValueError(f"{_LANE_NAME} unknown hold entered release: {released_holds}")
    owned = [
        event
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_SOMALI_REBELS_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    if owned:
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        if owned_ids != WAVE8_SOMALI_REBELS_CONTRACT_IDS or len(owned) != len(
            owned_ids
        ):
            raise ValueError(f"{_LANE_NAME} current release ownership is partial")
        validate_wave8_somali_rebels_emissions(owned)
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event not in owned and _is_probable_twin(event)
    )
    released_ucdp = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("ucdp_candidate_id")
        in WAVE8_SOMALI_REBELS_UCDP_DISPOSITIONS
        or event.get("source_candidate_id")
        in WAVE8_SOMALI_REBELS_UCDP_DISPOSITIONS
    )
    if hced_twins or iwd_twins or iwbd_twins or release_twins or released_ucdp:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"iwd={iwd_twins}, iwbd={iwbd_twins}, release={release_twins}, "
            f"ucdp_release={released_ucdp}"
        )
    return {
        "existing_release_owned_events": len(owned),
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "integration_dispositions": len(
            WAVE8_SOMALI_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "iwd_probable_twins": 0,
        "iwbd_probable_twins": 0,
        "ucdp_overlap_dispositions": (
            len(WAVE8_SOMALI_REBELS_UCDP_DISPOSITIONS) if supplied_ucdp else 0
        ),
        "wikidata_dispositions": (
            len(WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES)
            if supplied_wikidata
            else 0
        ),
    }


def install_wave8_somali_rebels_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SOMALI_REBELS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_somali_rebels_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SOMALI_REBELS_SOURCES,
        lane_name=_LANE_NAME,
    )


_OPERATIONAL_CAMPAIGN_WIN: dict[str, float] = {
    "campaign_objective": 0.86,
    "theater_control": 0.84,
    "force_preservation": 0.72,
    "tempo_initiative": 0.82,
    "logistics_sustainment": 0.76,
}
_OPERATIONAL_CAMPAIGN_LOSS: dict[str, float] = {
    key: round(1.0 - value, 2)
    for key, value in _OPERATIONAL_CAMPAIGN_WIN.items()
}


def _apply_event_review(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        contract = WAVE8_SOMALI_REBELS_CONTRACTS[candidate_id]
        canonical = contract["canonical_event"]
        if candidate_id in WAVE8_SOMALI_REBELS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SOMALI_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)
        event["event_type"] = str(contract["event_type"])
        event["decisiveness"] = float(contract["reviewed_decisiveness"])
        event["date_interval"] = {
            "start": str(canonical["start_date"]),
            "end": str(canonical["end_date"]),
        }
        if candidate_id == "hced-Mogadishu1990-1991-1":
            event["scale"] = "campaign"
            event["summary"] = (
                "Candidate-keyed Wave 8 operational urban-campaign assertion. "
                "The city campaign, bounded forces, exact endpoint, and outcome "
                "sources are pinned; no constituent engagement, national "
                "settlement, or whole-war result is inferred. "
                + str(contract["audit_note"])
            )
            for participant in event["participants"]:
                if participant["side"] == "side_a":
                    participant["outcome"] = dict(_OPERATIONAL_CAMPAIGN_WIN)
                    participant["termination"] = "campaign_victory"
                    participant["result_class"] = "major_operational_victory"
                else:
                    participant["outcome"] = dict(_OPERATIONAL_CAMPAIGN_LOSS)
                    participant["termination"] = "campaign_defeat"
                    participant["result_class"] = "major_operational_defeat"
                participant["note"] = (
                    f"Candidate-keyed {_LANE_NAME} operational contract; no "
                    "generic faction continuity or strategic civil-war result "
                    "is inferred."
                )
        else:
            event["summary"] = (
                "Candidate-keyed Wave 8 limited tactical assertion. The direct-"
                "action raid, relief, and extraction battle is isolated from the "
                "wider intervention and later political withdrawal. "
                + str(contract["audit_note"])
            )


def validate_wave8_somali_rebels_emissions(
    events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    owned = list(events)
    by_id = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_id) != WAVE8_SOMALI_REBELS_CONTRACT_IDS or len(owned) != len(by_id):
        raise ValueError(f"{_LANE_NAME} emitted inventory drift")
    participant_count = 0
    campaign_count = 0
    outcome_override_count = 0
    forbidden_entities = {_DERVISH, _SOMALIA, "united_states"}
    for candidate_id, contract in WAVE8_SOMALI_REBELS_CONTRACTS.items():
        event = by_id[candidate_id]
        canonical = contract["canonical_event"]
        if (
            event.get("id") != f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year"))
            != (canonical["year_low"], canonical["year_high"])
            or event.get("date_precision") != canonical["date_precision"]
            or event.get("date_interval")
            != {
                "start": canonical["start_date"],
                "end": canonical["end_date"],
            }
            or event.get("reviewed_granularity") != canonical["granularity"]
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("event_type") != contract["event_type"]
            or event.get("war_type") != contract["war_type"]
            or event.get("source_ids")
            != ["hced_dataset", *contract["evidence_refs"]]
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids")
            != contract["outcome_source_family_ids"]
            or float(event.get("confidence", -1.0))
            != float(contract["confidence"])
            or float(event.get("decisiveness", -1.0))
            != float(contract["reviewed_decisiveness"])
            or "geometry" in event
            or event.get("modern_location_country") != "Somalia"
            or event.get("location_provenance", {}).get("assertion_status")
            != "unreviewed_source_assertion"
        ):
            raise ValueError(f"{_LANE_NAME} emitted contract drift: {candidate_id}")
        participants = event.get("participants", [])
        participant_ids = {
            str(participant.get("entity_id")) for participant in participants
        }
        if participant_ids & forbidden_entities:
            raise ValueError(f"{_LANE_NAME} broad identity entered {candidate_id}")
        if any(
            "inconclusive" in str(participant.get("termination", ""))
            for participant in participants
        ):
            raise ValueError(f"{_LANE_NAME} unknown/draw drift: {candidate_id}")

        if candidate_id == "hced-Mogadishu1990-1991-1":
            if (
                event.get("scale") != "campaign"
                or len(participants) != 2
                or participants[0].get("entity_id") != _USC_MOGADISHU
                or participants[0].get("side") != "side_a"
                or participants[0].get("outcome") != _OPERATIONAL_CAMPAIGN_WIN
                or participants[0].get("termination") != "campaign_victory"
                or participants[0].get("result_class")
                != "major_operational_victory"
                or participants[1].get("entity_id") != _BARRE_LOYALISTS
                or participants[1].get("side") != "side_b"
                or participants[1].get("outcome") != _OPERATIONAL_CAMPAIGN_LOSS
                or participants[1].get("termination") != "campaign_defeat"
                or participants[1].get("result_class")
                != "major_operational_defeat"
            ):
                raise ValueError(f"{_LANE_NAME} operational campaign drift")
            campaign_count += 1
        else:
            expected_participants = expected_exact_hced_win_participants(
                contract["side_2_entity_ids"],
                contract["side_1_entity_ids"],
                confidence=float(contract["confidence"]),
                scale_level=int(contract["expected_scale_level"]),
                lane_name=_LANE_NAME,
            )
            if participants != expected_participants:
                raise ValueError(f"{_LANE_NAME} tactical reversal drift")
            if not (
                participant_ids
                == {_TASK_FORCE_RANGER, _RELIEF_FORCE, _SNA_AIDID}
                and all(
                    participant["side"] == "side_a"
                    for participant in participants
                    if participant["entity_id"]
                    in {_TASK_FORCE_RANGER, _RELIEF_FORCE}
                )
                and next(
                    participant for participant in participants
                    if participant["entity_id"] == _SNA_AIDID
                )["side"]
                == "side_b"
            ):
                raise ValueError(f"{_LANE_NAME} 1993 side polarity drift")
            outcome_override_count += 1
        participant_count += len(participants)
    return {
        "campaign_events": campaign_count,
        "events": len(owned),
        "outcome_overrides": outcome_override_count,
        "participants": participant_count,
        "retained_countries": len(owned),
        "retained_points": 0,
    }


def promote_wave8_somali_rebels_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_somali_rebels_queue_contracts(hced_rows)
    validate_wave8_somali_rebels_existing_boundaries(release_entities)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SOMALI_REBELS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_event_review(events)
    validate_wave8_somali_rebels_emissions(events)
    return events


def validate_wave8_somali_rebels_current_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Require Somali lane artifacts to be absent or atomically complete."""

    _validate_static()
    entities_by_id = {
        str(entity.get("id")): entity for entity in release_entities
    }
    sources_by_id = {str(source.get("id")): source for source in release_sources}
    validate_wave8_somali_rebels_existing_boundaries(entities_by_id)
    validate_wave8_somali_rebels_required_sources(sources_by_id)
    events = list(release_events)
    expected_entity_ids = {
        str(entity["id"]) for entity in WAVE8_SOMALI_REBELS_ENTITIES
    }
    expected_source_ids = set(_SOURCE_BY_ID)
    entity_overlap = expected_entity_ids & set(entities_by_id)
    source_overlap = expected_source_ids & set(sources_by_id)
    held_events = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_SOMALI_REBELS_HOLD_IDS
    ]
    if held_events:
        raise ValueError(f"{_LANE_NAME} unknown hold entered current release")
    owned = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_SOMALI_REBELS_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    any_present = bool(entity_overlap or source_overlap or owned)
    if not any_present:
        return {
            "artifact_state": "absent",
            "installed_entities": 0,
            "installed_sources": 0,
            "promoted_events": 0,
        }
    if (
        entity_overlap != expected_entity_ids
        or source_overlap != expected_source_ids
        or len(owned) != len(WAVE8_SOMALI_REBELS_CONTRACT_IDS)
    ):
        raise ValueError(f"{_LANE_NAME} current release artifacts are partial")
    for entity in WAVE8_SOMALI_REBELS_ENTITIES:
        if entities_by_id[str(entity["id"])] != entity:
            raise ValueError(f"{_LANE_NAME} current entity drift: {entity['id']}")
    for source_id, source in _SOURCE_BY_ID.items():
        if sources_by_id[source_id] != source:
            raise ValueError(f"{_LANE_NAME} current source drift: {source_id}")
    validate_wave8_somali_rebels_emissions(owned)
    return {
        "artifact_state": "integrated",
        "installed_entities": len(entity_overlap),
        "installed_sources": len(source_overlap),
        "promoted_events": len(owned),
    }


def wave8_somali_rebels_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_SOMALI_REBELS_CONTRACTS.values(),
                    *WAVE8_SOMALI_REBELS_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_somali_rebels_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_SOMALI_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_date_quarantines": len(
            WAVE8_SOMALI_REBELS_DISCOVERY_DATE_QUARANTINES
        ),
        "holds": len(WAVE8_SOMALI_REBELS_HOLDS),
        "integration_dispositions": len(
            WAVE8_SOMALI_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_SOMALI_REBELS_ENTITIES),
        "new_sources": len(WAVE8_SOMALI_REBELS_SOURCES),
        "newly_rated_events": len(WAVE8_SOMALI_REBELS_CONTRACTS),
        "outcome_overrides": sum(
            bool(contract["source_outcome_override"])
            for contract in WAVE8_SOMALI_REBELS_CONTRACTS.values()
        ),
        "point_quarantine_additions": len(
            WAVE8_SOMALI_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_SOMALI_REBELS_CONTRACTS),
        "required_existing_sources": len(
            WAVE8_SOMALI_REBELS_REQUIRED_EXISTING_SOURCES
        ),
        "reviewed_hced_rows": len(WAVE8_SOMALI_REBELS_RESERVED_IDS),
        "terminal_exclusions": 0,
        "ucdp_nonrating_records": len(WAVE8_SOMALI_REBELS_UCDP_ROW_HASHES),
        "unknown_holds": len(WAVE8_SOMALI_REBELS_HOLDS),
        "wikidata_nonrating_records": len(
            WAVE8_SOMALI_REBELS_WIKIDATA_ROW_HASHES
        ),
    }


def wave8_somali_rebels_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_SOMALI_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_SOMALI_REBELS_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_somali_rebels_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_somali_rebels_counts(),
        "cohorts": wave8_somali_rebels_cohort_counts(),
        "country_quarantine_additions": sorted(
            WAVE8_SOMALI_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_SOMALI_REBELS_INTEGRATION_DISPOSITIONS.items()
            )
        ],
        "final_audit_signature": WAVE8_SOMALI_REBELS_FINAL_AUDIT_SIGNATURE,
        "held_candidate_ids": sorted(WAVE8_SOMALI_REBELS_HOLD_IDS),
        "point_quarantine_additions": sorted(
            WAVE8_SOMALI_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "promoted_candidate_ids": sorted(WAVE8_SOMALI_REBELS_CONTRACT_IDS),
    }


_validate_static()
