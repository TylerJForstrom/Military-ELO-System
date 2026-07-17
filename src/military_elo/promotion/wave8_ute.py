"""Candidate-keyed Wave 8 audit for HCED's exact ``Ute Indians`` label.

The locked queue contains four exact-label rows.  Two support narrowly bounded
tactical ratings: Fauntleroy's 28 April 1855 attack near Poncha Pass and the
opening 29 September 1879 Thornburgh action at Milk Creek.  Spanish Fork is
held because a year-only row cannot select between two separately documented
April 1863 actions.  Red Canyon is terminally excluded as an opposite-result
duplicate/conflation of the same Milk Creek action owned by the White River
row.

Every rated participant is an event-year fighting formation.  Nothing in this
lane creates a generic Ute, Ute-band, United States, or U.S. Army identity;
noncombatants and modern tribal governments never inherit these ratings.
Unknown is never converted to a draw, and no campaign-level result is inferred
from a tactical phase.
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
    "WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS",
    "WAVE8_UTE_ALTERNATE_LABEL_AUDIT",
    "WAVE8_UTE_CONTRACT_IDS",
    "WAVE8_UTE_CONTRACTS",
    "WAVE8_UTE_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_UTE_CROSS_LANE_DISPOSITIONS",
    "WAVE8_UTE_CROSS_SPELLING_DUPLICATE_AUDIT",
    "WAVE8_UTE_ENTITIES",
    "WAVE8_UTE_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_UTE_EXCLUSION_IDS",
    "WAVE8_UTE_EXCLUSIONS",
    "WAVE8_UTE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_UTE_EXPECTED_CANDIDATE_IDS",
    "WAVE8_UTE_FINAL_AUDIT_SIGNATURE",
    "WAVE8_UTE_FUNNEL_EVENT_CANDIDATE_ID_SHA256",
    "WAVE8_UTE_HCED_QUEUE_SHA256",
    "WAVE8_UTE_HOLD_IDS",
    "WAVE8_UTE_HOLDS",
    "WAVE8_UTE_INTEGRATION_DISPOSITIONS",
    "WAVE8_UTE_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_UTE_IWBD_QUEUE_SHA256",
    "WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_UTE_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_UTE_LOCATION_QUARANTINE_REASONS",
    "WAVE8_UTE_NONPROMOTIONS",
    "WAVE8_UTE_OPPOSITE_RESULT_AUDIT",
    "WAVE8_UTE_OUTCOME_OVERRIDES",
    "WAVE8_UTE_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_UTE_RELATED_HCED_DISPOSITIONS",
    "WAVE8_UTE_RESERVED_IDS",
    "WAVE8_UTE_ROW_HASHES",
    "WAVE8_UTE_SOURCES",
    "WAVE8_UTE_TERMINAL_EXCLUSION_IDS",
    "WAVE8_UTE_TERMINAL_EXCLUSIONS",
    "install_wave8_ute_entities",
    "install_wave8_ute_sources",
    "promote_wave8_ute_contracts",
    "validate_wave8_ute_integration_dispositions",
    "validate_wave8_ute_queue_contracts",
    "wave8_ute_audit_signature",
    "wave8_ute_cohort_counts",
    "wave8_ute_counts",
    "wave8_ute_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Ute Indians exact-force audit"
_MODULE_OWNER = "wave8_ute"
_EVENT_ID_PREFIX = "hced_wave8_ute_"

_PONCHA_UTE_FORCE_ID = "blancos_moache_ute_fighting_force_poncha_1855"
_PONCHA_US_COLUMN_ID = "fauntleroy_poncha_pass_column_1855"
_MILK_CREEK_UTE_FORCE_ID = "chief_jack_white_river_ute_force_milk_creek_1879"
_MILK_CREEK_US_COLUMN_ID = "thornburgh_5th_cavalry_expedition_milk_creek_1879"


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
        "evidence_roles": sorted(roles),
    }


WAVE8_UTE_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_ute_nps_fort_union_study",
        "Fort Union National Monument Historic Resource Study, Chapter 3",
        "https://npshistory.com/publications/foun/hrs/chap3.htm",
        "U.S. National Park Service",
        "federal_historic_resource_study",
        "nps_fort_union_historic_resource_study",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_ute_army_historical_foundation_almanac",
        "Army Almanac 2025, Volume 30, Issue 2",
        "https://armyhistory.org/army-almanac-2025-volume-30-issue-2/",
        "The Army Historical Foundation",
        "institutional_military_history",
        "army_historical_foundation_almanac_2025",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_ute_clodfelter_warfare",
        "Warfare and Armed Conflicts: A Statistical Encyclopedia",
        "https://books.google.com/books?id=8urEDgAAQBAJ&pg=PA266&vq=Poncha",
        "McFarland / Google Books",
        "scholarly_reference_work",
        "clodfelter_warfare_armed_conflicts",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_ute_colorado_ute_unit",
        "Ute People: Colorado's Original Inhabitants",
        (
            "https://ccia.colorado.gov/sites/ccia/files/documents/"
            "Ute%20Unit%201%20Pages.pdf"
        ),
        "Colorado Commission of Indian Affairs",
        "state_government_tribal_history_curriculum",
        "colorado_commission_indian_affairs_ute_unit",
    ),
    _source(
        "wave8_ute_southern_ute_history",
        "Southern Ute Indian Tribe history",
        "https://www.southernute-nsn.gov/history/",
        "Southern Ute Indian Tribe",
        "official_tribal_government_history",
        "southern_ute_official_history",
    ),
    _source(
        "wave8_ute_official_records_1863",
        "The War of the Rebellion: Official Records, Series I, Volume L, Part I",
        "https://archive.org/details/cu31924077730129",
        "U.S. War Department / Cornell University Library",
        "digitized_government_primary_documents",
        "official_records_pacific_coast_1863",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_ute_nps_second_california_cavalry",
        "2nd Regiment, California Cavalry",
        (
            "https://www.nps.gov/civilwar/search-battle-units-detail.htm"
            "?battleUnitCode=UCA0002RC"
        ),
        "U.S. National Park Service",
        "federal_military_unit_reference",
        "nps_second_california_cavalry",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_ute_usu_mccarthy_thesis",
        "Civil War Military Operations in Utah and Nevada, 1862-1865",
        (
            "https://digitalcommons.usu.edu/context/etd/article/4122/"
            "viewcontent/1975_McCarthy_Max.pdf"
        ),
        "Utah State University",
        "scholarly_history_thesis",
        "mccarthy_utah_nevada_operations_1975",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_ute_army_csi_campaign_1879",
        "The Ute Campaign of 1879: A Study in the Use of the Military Instrument",
        (
            "https://www.armyupress.army.mil/Portals/7/combat-studies-"
            "institute/csi-books/the-ute-campaign-1879.pdf"
        ),
        "U.S. Army Combat Studies Institute Press",
        "federal_military_campaign_study",
        "santala_ute_campaign_1879",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_ute_army_history_74",
        "Army History, No. 74",
        (
            "https://ky.ng.mil/Portals/59/Army%20History%20Magazine/"
            "Issues%20by%20PDF/Army_History_Magazine_74.pdf"
        ),
        "U.S. Army Center of Military History",
        "federal_peer_reviewed_military_history",
        "army_history_magazine_74",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_ute_uofutah_troubled_trails",
        "Troubled Trails: The Meeker Affair and the Expulsion of Utes from Colorado",
        "https://uofupress.com/books/troubled-trails/",
        "University of Utah Press",
        "scholarly_monograph",
        "simmons_troubled_trails",
    ),
    _source(
        "wave8_ute_oupress_last_war_trail",
        "The Last War Trail: The Utes and the Settlement of Colorado",
        "https://www.oupress.com/9780806110431/the-last-war-trail/",
        "University of Oklahoma Press",
        "scholarly_monograph_with_ute_oral_account",
        "jefferson_last_war_trail",
    ),
    _source(
        "wave8_ute_nps_fort_da_russell_nhl",
        "Fort D. A. Russell National Historic Landmark documentation",
        "https://npgallery.nps.gov/NRHP/GetAsset/NHLS/69000191_text",
        "U.S. National Park Service",
        "federal_historic_landmark_documentation",
        "nps_fort_da_russell_nhl",
    ),
)


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_UTE_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    source_ids: Iterable[str],
    scope: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": "North America",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            f"{scope} This identity exists only for the named event and year. "
            "No rating is inherited by the Ute people, any ethnic label or "
            "historical band outside this action, noncombatants, a modern tribal "
            "government, the United States, the U.S. Army, or another formation."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_UTE_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _PONCHA_UTE_FORCE_ID,
        "Chief Blanco's Moache Ute fighting force near Poncha Pass (1855)",
        "event_bounded_band_fighting_force",
        1855,
        [
            "wave8_ute_colorado_ute_unit",
            "wave8_ute_nps_fort_union_study",
            "wave8_ute_southern_ute_history",
        ],
        (
            "Event-bounded fighters identified in the reviewed campaign account "
            "with Chief Blanco and the Moache band; families who escaped the camp "
            "are expressly not participants."
        ),
    ),
    _entity(
        _PONCHA_US_COLUMN_ID,
        "Fauntleroy's regular-volunteer column near Poncha Pass (1855)",
        "event_bounded_military_column",
        1855,
        [
            "wave8_ute_army_historical_foundation_almanac",
            "wave8_ute_nps_fort_union_study",
        ],
        (
            "Event-bounded force under Lt. Col. Thomas T. Fauntleroy, comprising "
            "the regular and New Mexico volunteer companies used in this action."
        ),
    ),
    _entity(
        _MILK_CREEK_UTE_FORCE_ID,
        "Chief Jack's White River Ute fighting force at Milk Creek (1879)",
        "event_bounded_band_fighting_force",
        1879,
        [
            "wave8_ute_army_csi_campaign_1879",
            "wave8_ute_oupress_last_war_trail",
            "wave8_ute_uofutah_troubled_trails",
        ],
        (
            "Event-bounded White River Ute fighters under Chief Jack in the "
            "opening Thornburgh action; no rating is assigned to agency residents."
        ),
    ),
    _entity(
        _MILK_CREEK_US_COLUMN_ID,
        "Thornburgh's 5th Cavalry expedition at Milk Creek (1879)",
        "event_bounded_cavalry_expedition",
        1879,
        [
            "wave8_ute_army_csi_campaign_1879",
            "wave8_ute_army_history_74",
            "wave8_ute_nps_fort_da_russell_nhl",
        ],
        (
            "Event-bounded expedition under Maj. Thomas T. Thornburgh, including "
            "the 5th Cavalry companies engaged and forced back to the wagon defense."
        ),
    ),
)


WAVE8_UTE_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_UTE_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)
WAVE8_UTE_EXACT_CANDIDATE_ID_SHA256 = (
    "872d0c8a08e78afa72654bc1173b3522dfd038f6860757ad74464b9682e000f4"
)
WAVE8_UTE_FUNNEL_EVENT_CANDIDATE_ID_SHA256 = (
    WAVE8_UTE_EXACT_CANDIDATE_ID_SHA256
)
WAVE8_UTE_ROW_HASHES: dict[str, str] = {
    "hced-Poncha Pass1855-1": (
        "e69abdca457c25fd6f53d53246d9ee5e022ad11198a4c88bebf69b0de4ecd56f"
    ),
    "hced-Red Canyon1879-1": (
        "822ff39ebc665f8a41b2ce31135dfeff869ed21084be151162cdc235ebe7ddae"
    ),
    "hced-Spanish Fork Canon1863-1": (
        "32ac76f122bb911d8d037842e95f26e883bff06c28e8004b91d3e4c57f47b78e"
    ),
    "hced-White River1879-1": (
        "068abe411a8e81640c22e348c631ebab434968445d2ba747df47f2f345e4d8aa"
    ),
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str = "day",
    granularity: str = "engagement",
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
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_UTE_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
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


_MILK_CREEK_CANONICAL = _canonical(
    "Opening action at Milk Creek",
    1879,
    "29 September 1879",
    granularity="engagement_phase",
)


WAVE8_UTE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Poncha Pass1855-1": _contract(
        "hced-Poncha Pass1855-1",
        _canonical(
            "Battle near Poncha Pass",
            1855,
            "28 April 1855",
        ),
        "fauntleroy_ute_campaign_1855",
        [_PONCHA_US_COLUMN_ID],
        [_PONCHA_UTE_FORCE_ID],
        [
            "wave8_ute_army_historical_foundation_almanac",
            "wave8_ute_clodfelter_warfare",
            "wave8_ute_colorado_ute_unit",
            "wave8_ute_nps_fort_union_study",
            "wave8_ute_southern_ute_history",
        ],
        [
            "wave8_ute_army_historical_foundation_almanac",
            "wave8_ute_clodfelter_warfare",
            "wave8_ute_nps_fort_union_study",
        ],
        (
            "The federal historic study describes Fauntleroy's force attacking "
            "Chief Blanco's Moache camp on 28 April, the fighters resisting until "
            "their families escaped, and the Ute force then being routed. The "
            "rating is this tactical action only, not the 1855 campaign or a people."
        ),
        confidence=0.94,
    ),
    "hced-White River1879-1": _contract(
        "hced-White River1879-1",
        _MILK_CREEK_CANONICAL,
        "white_river_ute_campaign_1879",
        [_MILK_CREEK_UTE_FORCE_ID],
        [_MILK_CREEK_US_COLUMN_ID],
        [
            "wave8_ute_army_csi_campaign_1879",
            "wave8_ute_army_history_74",
            "wave8_ute_clodfelter_warfare",
            "wave8_ute_nps_fort_da_russell_nhl",
            "wave8_ute_oupress_last_war_trail",
            "wave8_ute_uofutah_troubled_trails",
        ],
        [
            "wave8_ute_army_csi_campaign_1879",
            "wave8_ute_army_history_74",
            "wave8_ute_clodfelter_warfare",
        ],
        (
            "The contract is limited to the opening 29 September action: Chief "
            "Jack's force compelled Thornburgh's command to withdraw to its wagons, "
            "killed Thornburgh, and held the surrounding high ground. It does not "
            "rate the ensuing siege, relief, Meeker killings, or campaign settlement."
        ),
        confidence=0.95,
    ),
}


def _nonpromotion(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    historical_review: Mapping[str, Any],
    *,
    terminal: bool,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_UTE_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "disposition": "terminal_exclusion" if terminal else "hold",
        "terminal_exclusion": terminal,
        "hold_category": category,
        "hold_reason": reason,
        "reviewed_outcome": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_granularity": str(canonical_event["granularity"]),
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "terminal_hced_owner" if terminal else "held_hced_owner",
        },
        "historical_review": dict(historical_review),
    }


WAVE8_UTE_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Spanish Fork Canon1863-1": _nonpromotion(
        "hced-Spanish Fork Canon1863-1",
        _canonical(
            "Spanish Fork Canyon actions",
            1863,
            "4 and 15 April 1863",
            date_precision="multiple_days",
            granularity="ambiguous_same_name_engagements",
        ),
        "utah_black_hawk_war_precursor_1863",
        "same_name_same_year_actions_and_actor_ambiguity",
        (
            "The Official Records and NPS unit chronology separately list actions "
            "on 4 April under Capt. George F. Price and 15 April under Col. George "
            "S. Evans. HCED supplies only a year and one name, so selecting either "
            "action, merging their losses, or assigning one Ute band would invent "
            "scope. The row remains unknown and unknown is never a draw."
        ),
        [
            "wave8_ute_colorado_ute_unit",
            "wave8_ute_nps_second_california_cavalry",
            "wave8_ute_official_records_1863",
            "wave8_ute_usu_mccarthy_thesis",
        ],
        {
            "alternative_1": {
                "date": "4 April 1863",
                "us_formation": "Capt. George F. Price's 2nd California Cavalry detachment",
                "scope": "initial Spanish Fork Canyon action and 5 April pursuit",
            },
            "alternative_2": {
                "date": "15 April 1863",
                "us_formation": "Col. George S. Evans's 2nd California Cavalry column",
                "scope": "separate fourteen-mile canyon pursuit",
            },
            "source_actor_boundary": (
                "Contemporary reports use a generic Indian label while later "
                "accounts vary between Ute and Gosiute identification."
            ),
            "selection_rule": "no unique event, force, or band can be selected",
        },
        terminal=False,
    )
}


WAVE8_UTE_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Red Canyon1879-1": _nonpromotion(
        "hced-Red Canyon1879-1",
        _MILK_CREEK_CANONICAL,
        "white_river_ute_campaign_1879",
        "opposite_result_duplicate_and_campaign_phase_conflation",
        (
            "Red Canyon and White River point to the Thornburgh-Milk Creek action, "
            "but HCED gives them opposite winners. The reviewed sources support a "
            "Ute tactical success in the opening action and a later relief/withdrawal "
            "without a second, independently bounded U.S. battlefield victory. The "
            "White River row owns the narrow rateable action; this duplicate is not "
            "a draw and no second outcome is invented."
        ),
        [
            "wave8_ute_army_csi_campaign_1879",
            "wave8_ute_army_history_74",
            "wave8_ute_clodfelter_warfare",
            "wave8_ute_oupress_last_war_trail",
            "wave8_ute_uofutah_troubled_trails",
        ],
        {
            "canonical_owner_candidate_id": "hced-White River1879-1",
            "canonical_owner_scope": "opening action at Milk Creek, 29 September 1879",
            "raw_claimed_result": "United States victory",
            "reviewed_opening_result": "White River Ute tactical victory",
            "later_scope": "siege through relief and negotiated campaign aftermath",
            "independent_second_engagement": False,
        },
        terminal=True,
    )
}

WAVE8_UTE_EXCLUSIONS = WAVE8_UTE_TERMINAL_EXCLUSIONS
WAVE8_UTE_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_UTE_HOLDS,
    **WAVE8_UTE_TERMINAL_EXCLUSIONS,
}

WAVE8_UTE_CONTRACT_IDS = frozenset(WAVE8_UTE_CONTRACTS)
WAVE8_UTE_HOLD_IDS = frozenset(WAVE8_UTE_HOLDS)
WAVE8_UTE_TERMINAL_EXCLUSION_IDS = frozenset(WAVE8_UTE_TERMINAL_EXCLUSIONS)
WAVE8_UTE_EXCLUSION_IDS = WAVE8_UTE_TERMINAL_EXCLUSION_IDS
WAVE8_UTE_RESERVED_IDS = frozenset(
    WAVE8_UTE_CONTRACT_IDS
    | WAVE8_UTE_HOLD_IDS
    | WAVE8_UTE_TERMINAL_EXCLUSION_IDS
)
WAVE8_UTE_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_UTE_ROW_HASHES)


# Both promoted source points are insufficiently supported as exact battlefield
# points. Their modern-country assertions remain valid. Holds/exclusions never
# enter location output and therefore do not need quarantine entries.
WAVE8_UTE_POINT_QUARANTINE_ADDITIONS = WAVE8_UTE_CONTRACT_IDS
WAVE8_UTE_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_UTE_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_UTE_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_UTE_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_UTE_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Poncha Pass1855-1": {
        "field": "geometry",
        "raw_point": [-106.0957163, 38.4222195],
        "reference_source_id": "wave8_ute_nps_fort_union_study",
        "reviewed_location": (
            "Ute camp near the Arkansas River, described as about twenty miles "
            "from Poncha Pass"
        ),
        "reason": (
            "HCED supplies a pass-area point, while the federal study places the "
            "camp roughly twenty miles from the pass; no exact coordinate is inferred."
        ),
    },
    "hced-White River1879-1": {
        "field": "geometry",
        "raw_point": [-107.918803, 40.051041],
        "reference_source_id": "wave8_ute_army_csi_campaign_1879",
        "reviewed_location": "Milk Creek battlefield north of present-day Meeker, Colorado",
        "reason": (
            "The campaign study maps the Thornburgh action at Milk Creek, but the "
            "HCED White River point does not identify that battlefield precisely."
        ),
    },
}


WAVE8_UTE_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


WAVE8_UTE_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Red Canyon1879-1": {
        "raw_row_sha256": WAVE8_UTE_ROW_HASHES["hced-Red Canyon1879-1"],
        "related_hced_candidate_id": "hced-White River1879-1",
        "related_raw_row_sha256": WAVE8_UTE_ROW_HASHES["hced-White River1879-1"],
        "disposition": "opposite_result_duplicate",
        "relationship": "same_thornburgh_milk_creek_action_and_campaign_scope",
        "owner_module": _MODULE_OWNER,
        "canonical_owner_candidate_id": "hced-White River1879-1",
        "reason": (
            "The Red Canyon U.S.-win row cannot be separated into a second rated "
            "event from the White River Ute-win row without double-rating Milk Creek."
        ),
        "evidence_refs": sorted(
            [
                "wave8_ute_army_csi_campaign_1879",
                "wave8_ute_army_history_74",
                "wave8_ute_clodfelter_warfare",
            ]
        ),
    }
}


_ADJACENT_ROW_HASHES = {
    "hced-Adobe Walls1864-1": (
        "957ce353c339375d96c44d93768d5d52f58efd863c9a2163cd230a894faf548d"
    ),
    "hced-Bear River1863-1": (
        "9f87f9ea40ce0222c7b8923c0e944645717bbaebdb8ac8f2c466ac0714ce7ffc"
    ),
    "hced-Cieneguilla1854-1": (
        "6277589d940190b3e8f6e1d5c13e49b75c5a22f8d999860b6e8b6fb97e5daac3"
    ),
    "hced-Spanish Armada1588-1": (
        "b98b8a606d1bf7067f59d7e5fc9a1ea5f7626fca2e6a3cf4328f8c16fac9027a"
    ),
}

WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Adobe Walls1864-1": {
        "raw_row_sha256": _ADJACENT_ROW_HASHES["hced-Adobe Walls1864-1"],
        "disposition": "separate_comanche_lane_hold",
        "owner_module": "wave8_comanche",
        "boundary": "Ute scouts in Carson's coalition do not make the opposing Comanche row a Ute event",
        "evidence_refs": [],
    },
    "hced-Bear River1863-1": {
        "raw_row_sha256": _ADJACENT_ROW_HASHES["hced-Bear River1863-1"],
        "disposition": "separate_shoshone_event",
        "owner_module": "not_wave8_ute",
        "boundary": "Utah geography and spelling are not a Ute actor identity; HCED names Shoshone",
        "evidence_refs": [],
    },
    "hced-Cieneguilla1854-1": {
        "raw_row_sha256": _ADJACENT_ROW_HASHES["hced-Cieneguilla1854-1"],
        "disposition": "existing_north_america_lane_hold",
        "owner_module": "wave8_north_america",
        "boundary": "accounts vary on Jicarilla and Ute participation, so no Ute force is inferred",
        "evidence_refs": [],
    },
    "hced-Spanish Armada1588-1": {
        "raw_row_sha256": _ADJACENT_ROW_HASHES["hced-Spanish Armada1588-1"],
        "disposition": "participant_token_false_positive",
        "owner_module": "not_wave8_ute",
        "boundary": "the word Ute appears only in noisy participants metadata; the sides are England and Spain",
        "evidence_refs": [],
    },
}
WAVE8_UTE_CROSS_LANE_DISPOSITIONS = WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS


WAVE8_UTE_ALTERNATE_LABEL_AUDIT: dict[str, Any] = {
    "exact_source_labels": ["Ute Indians"],
    "reviewed_alternate_side_labels": [
        "capote ute",
        "moache ute",
        "mouache ute",
        "muache ute",
        "pahvant ute",
        "sanpete ute",
        "tabeguache ute",
        "taviwac ute",
        "uintah ute",
        "uncompahgre ute",
        "unitah ute",
        "ute",
        "ute indian",
        "utes",
        "weeminuche ute",
        "white river ute",
        "white river utes",
        "yampa ute",
    ],
    "matched_alternate_side_candidate_ids": [],
    "participant_only_false_positive_candidate_ids": [
        "hced-Spanish Armada1588-1"
    ],
    "same_campaign_component_candidate_ids": [
        "hced-Adobe Walls1864-1",
        "hced-Cieneguilla1854-1",
    ],
    "separate_neighbor_candidate_ids": ["hced-Bear River1863-1"],
}


WAVE8_UTE_OPPOSITE_RESULT_AUDIT: dict[str, Any] = {
    "same_event_opposite_result_pairs": [
        ["hced-Red Canyon1879-1", "hced-White River1879-1"]
    ],
    "canonical_owner_candidate_id": "hced-White River1879-1",
    "terminal_exclusion_candidate_id": "hced-Red Canyon1879-1",
    "owner_result": "White River Ute tactical victory in the opening action",
    "excluded_raw_result": "United States victory",
    "campaign_result_inferred": False,
}
WAVE8_UTE_CROSS_SPELLING_DUPLICATE_AUDIT: dict[str, Any] = {
    "exact_source_labels": ["Ute Indians"],
    "alternate_side_labels": WAVE8_UTE_ALTERNATE_LABEL_AUDIT[
        "reviewed_alternate_side_labels"
    ],
    "same_event_candidate_pairs": WAVE8_UTE_OPPOSITE_RESULT_AUDIT[
        "same_event_opposite_result_pairs"
    ],
    "iwbd_matching_candidate_ids": [],
    "existing_release_matching_event_ids": [],
}


WAVE8_UTE_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_UTE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Poncha Pass1855-1": {
        "aliases": (
            "battle near poncha pass",
            "battle of poncha pass",
            "poncha pass",
        ),
        "years": (1855,),
    },
    "hced-Red Canyon1879-1": {
        "aliases": (
            "battle of milk creek",
            "milk creek",
            "milk creek siege",
            "opening action at milk creek",
            "red canyon",
            "thornburgh ambush",
            "thornburgh ambush at milk creek",
            "thornburgh disaster",
            "white river",
        ),
        "years": (1879,),
    },
    "hced-Spanish Fork Canon1863-1": {
        "aliases": (
            "battle of spanish fork canyon",
            "spanish fork canon",
            "spanish fork canyon",
            "spanish fork canyon actions",
        ),
        "years": (1863,),
    },
    "hced-White River1879-1": {
        "aliases": (
            "battle of milk creek",
            "milk creek",
            "milk creek siege",
            "opening action at milk creek",
            "red canyon",
            "thornburgh ambush",
            "thornburgh ambush at milk creek",
            "thornburgh disaster",
            "white river",
        ),
        "years": (1879,),
    },
}


_EXACT_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        candidate_id: {
            "disposition": "promotion_contract",
            "owner_module": _MODULE_OWNER,
            "raw_row_sha256": WAVE8_UTE_ROW_HASHES[candidate_id],
        }
        for candidate_id in sorted(WAVE8_UTE_CONTRACT_IDS)
    },
    **{
        candidate_id: {
            "disposition": WAVE8_UTE_NONPROMOTIONS[candidate_id]["disposition"],
            "owner_module": _MODULE_OWNER,
            "raw_row_sha256": WAVE8_UTE_ROW_HASHES[candidate_id],
        }
        for candidate_id in sorted(WAVE8_UTE_NONPROMOTIONS)
    },
}
WAVE8_UTE_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"exact:{candidate_id}": disposition
        for candidate_id, disposition in _EXACT_DISPOSITIONS.items()
    },
    **{
        f"related_hced:{candidate_id}": disposition
        for candidate_id, disposition in WAVE8_UTE_RELATED_HCED_DISPOSITIONS.items()
    },
    **{
        f"cross_lane:{candidate_id}": disposition
        for candidate_id, disposition in WAVE8_UTE_CROSS_LANE_DISPOSITIONS.items()
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_hced_dispositions": WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS,
        "alternate_label_audit": WAVE8_UTE_ALTERNATE_LABEL_AUDIT,
        "contracts": WAVE8_UTE_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_UTE_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_spelling_duplicate_audit": WAVE8_UTE_CROSS_SPELLING_DUPLICATE_AUDIT,
        "entities": WAVE8_UTE_ENTITIES,
        "exact_candidate_id_sha256": WAVE8_UTE_EXACT_CANDIDATE_ID_SHA256,
        "existing_release_duplicate_dispositions": (
            WAVE8_UTE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_UTE_EXPECTED_CANDIDATE_IDS),
        "hced_queue_sha256": WAVE8_UTE_HCED_QUEUE_SHA256,
        "holds": WAVE8_UTE_HOLDS,
        "integration_dispositions": WAVE8_UTE_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_UTE_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_queue_sha256": WAVE8_UTE_IWBD_QUEUE_SHA256,
        "iwbd_zero_overlap_audit": WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_UTE_LOCATION_QUARANTINE_REASONS,
        "opposite_result_audit": WAVE8_UTE_OPPOSITE_RESULT_AUDIT,
        "outcome_overrides": WAVE8_UTE_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(WAVE8_UTE_POINT_QUARANTINE_ADDITIONS),
        "related_hced_dispositions": WAVE8_UTE_RELATED_HCED_DISPOSITIONS,
        "row_hashes": WAVE8_UTE_ROW_HASHES,
        "sources": WAVE8_UTE_SOURCES,
        "terminal_exclusions": WAVE8_UTE_TERMINAL_EXCLUSIONS,
    }


def wave8_ute_audit_signature() -> str:
    """Return the SHA-256 pin over the complete audited lane state."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


# Filled from the complete canonical payload; any change requires re-audit.
WAVE8_UTE_FINAL_AUDIT_SIGNATURE = (
    "2da93181e5a6ffcaa1f4b75fea4f890f77419dfff4ba6ef0ebc74d69badba300"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_UTE_CONTRACTS),
        len(WAVE8_UTE_HOLDS),
        len(WAVE8_UTE_TERMINAL_EXCLUSIONS),
    ) != (2, 1, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_UTE_ENTITIES), len(WAVE8_UTE_SOURCES)) != (4, 13):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_UTE_RESERVED_IDS != WAVE8_UTE_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact inventory is incomplete")
    dispositions = (
        WAVE8_UTE_CONTRACT_IDS,
        WAVE8_UTE_HOLD_IDS,
        WAVE8_UTE_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(3)
        for j in range(i + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if WAVE8_UTE_EXCLUSIONS is not WAVE8_UTE_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion inventory diverged")
    if any(
        len(value) != 64
        for value in (
            WAVE8_UTE_HCED_QUEUE_SHA256,
            WAVE8_UTE_IWBD_QUEUE_SHA256,
            WAVE8_UTE_EXACT_CANDIDATE_ID_SHA256,
            *WAVE8_UTE_ROW_HASHES.values(),
            *_ADJACENT_ROW_HASHES.values(),
        )
    ):
        raise ValueError(f"{_LANE_NAME} snapshot hash inventory drifted")
    expected_id_digest = hashlib.sha256(
        ("\n".join(sorted(WAVE8_UTE_EXPECTED_CANDIDATE_IDS)) + "\n").encode()
    ).hexdigest()
    if expected_id_digest != WAVE8_UTE_EXACT_CANDIDATE_ID_SHA256:
        raise ValueError(f"{_LANE_NAME} exact candidate digest drifted")
    if WAVE8_UTE_FUNNEL_EVENT_CANDIDATE_ID_SHA256 != expected_id_digest:
        raise ValueError(f"{_LANE_NAME} funnel digest drifted")
    if wave8_ute_audit_signature() != WAVE8_UTE_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_UTE_SOURCES}
    if len(source_by_id) != len(WAVE8_UTE_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_UTE_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_UTE_ENTITIES}
    if len(entity_by_id) != len(WAVE8_UTE_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "united states",
        "us army",
        "ute",
        "ute indians",
        "white river utes",
    }
    used_sources: set[str] = set()
    for entity in WAVE8_UTE_ENTITIES:
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity is not event-year bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a timeless identity")
        note = str(entity["continuity_note"]).casefold()
        for phrase in (
            "no rating is inherited",
            "ethnic label",
            "noncombatants",
            "modern tribal government",
            "united states",
        ):
            if phrase not in note:
                raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(entity["source_ids"]) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")
        used_sources.update(map(str, entity["source_ids"]))

    expected_contracts = {
        "hced-Poncha Pass1855-1": (
            1855,
            "day",
            "engagement",
            [_PONCHA_US_COLUMN_ID],
            [_PONCHA_UTE_FORCE_ID],
        ),
        "hced-White River1879-1": (
            1879,
            "day",
            "engagement_phase",
            [_MILK_CREEK_UTE_FORCE_ID],
            [_MILK_CREEK_US_COLUMN_ID],
        ),
    }
    used_entities: set[str] = set()
    for candidate_id, expected in expected_contracts.items():
        contract = WAVE8_UTE_CONTRACTS[candidate_id]
        year, precision, granularity, side_1_expected, side_2_expected = expected
        if contract["raw_row_sha256"] != WAVE8_UTE_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract row hash drifted")
        canonical = contract["canonical_event"]
        if (
            canonical["canonical_key"]
            != f"{_slug(str(canonical['name']))}:{year}:{year}"
            or canonical["year_low"] != year
            or canonical["year_high"] != year
            or canonical["date_precision"] != precision
            or canonical["granularity"] != granularity
            or not canonical["date_text"]
        ):
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if side_1 != side_1_expected or side_2 != side_2_expected:
            raise ValueError(f"{_LANE_NAME} actor contract drifted")
        if set(side_1) & set(side_2) or not side_1 or not side_2:
            raise ValueError(f"{_LANE_NAME} opposing sides are invalid")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} contract uses an unknown entity")
        used_entities.update(side_1)
        used_entities.update(side_2)
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["actor_override"] is not True
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} promotion ownership drifted")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if (
            len(outcomes) < 2
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        expected_families = sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} used a non-outcome source")
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identities are not exactly consumed")

    forbidden_nonpromotion_keys = {
        "losers",
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
        "winners",
    }
    for candidate_id, item in WAVE8_UTE_NONPROMOTIONS.items():
        if item["raw_row_sha256"] != WAVE8_UTE_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} nonpromotion hash drifted")
        if forbidden_nonpromotion_keys & set(item):
            raise ValueError(f"{_LANE_NAME} nonpromotion contains a rateable result")
        expected_terminal = candidate_id in WAVE8_UTE_TERMINAL_EXCLUSION_IDS
        expected_disposition = "terminal_exclusion" if expected_terminal else "hold"
        expected_status = "terminal_hced_owner" if expected_terminal else "held_hced_owner"
        if (
            item["disposition"] != expected_disposition
            or item["terminal_exclusion"] is not expected_terminal
            or item["reviewed_outcome"] != "unknown"
            or item["unknown_is_never_draw"] is not True
            or item["duplicate_ownership"]
            != {"owner_module": _MODULE_OWNER, "status": expected_status}
        ):
            raise ValueError(f"{_LANE_NAME} nonpromotion became rateable")
        if "draw" not in str(item["hold_reason"]).casefold():
            raise ValueError(f"{_LANE_NAME} unknown/draw policy drifted")
        evidence = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} nonpromotion evidence drifted")
        used_sources.update(evidence)

    if set(WAVE8_UTE_RELATED_HCED_DISPOSITIONS) != {"hced-Red Canyon1879-1"}:
        raise ValueError(f"{_LANE_NAME} related HCED inventory changed")
    related = WAVE8_UTE_RELATED_HCED_DISPOSITIONS["hced-Red Canyon1879-1"]
    if (
        related["related_hced_candidate_id"] != "hced-White River1879-1"
        or related["disposition"] != "opposite_result_duplicate"
        or related["canonical_owner_candidate_id"] != "hced-White River1879-1"
        or related["owner_module"] != _MODULE_OWNER
    ):
        raise ValueError(f"{_LANE_NAME} opposite-result ownership drifted")
    used_sources.update(map(str, related["evidence_refs"]))

    if set(WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS) != set(_ADJACENT_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} adjacent actor inventory changed")
    if WAVE8_UTE_CROSS_LANE_DISPOSITIONS is not WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} cross-lane inventory diverged")
    for candidate_id, item in WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS.items():
        if item["raw_row_sha256"] != _ADJACENT_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} adjacent-row hash drifted")
        if not item["owner_module"] or not item["boundary"]:
            raise ValueError(f"{_LANE_NAME} adjacent ownership is incomplete")

    alternate_labels = WAVE8_UTE_ALTERNATE_LABEL_AUDIT[
        "reviewed_alternate_side_labels"
    ]
    if not _is_sorted_unique(alternate_labels):
        raise ValueError(f"{_LANE_NAME} alternate labels are not canonical")
    if any(label != normalize_label(label) for label in alternate_labels):
        raise ValueError(f"{_LANE_NAME} alternate labels are not normalized")
    if WAVE8_UTE_ALTERNATE_LABEL_AUDIT[
        "matched_alternate_side_candidate_ids"
    ]:
        raise ValueError(f"{_LANE_NAME} alternate-label inventory changed")
    if WAVE8_UTE_OPPOSITE_RESULT_AUDIT[
        "same_event_opposite_result_pairs"
    ] != [["hced-Red Canyon1879-1", "hced-White River1879-1"]]:
        raise ValueError(f"{_LANE_NAME} opposite-result pair drifted")
    if WAVE8_UTE_OPPOSITE_RESULT_AUDIT["campaign_result_inferred"] is not False:
        raise ValueError(f"{_LANE_NAME} inferred a campaign result")

    if WAVE8_UTE_POINT_QUARANTINE_ADDITIONS != WAVE8_UTE_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_UTE_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_UTE_LOCATION_QUARANTINE_REASONS) != WAVE8_UTE_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reasons are incomplete")
    for item in WAVE8_UTE_LOCATION_QUARANTINE_REASONS.values():
        if (
            item["field"] != "geometry"
            or len(item["raw_point"]) != 2
            or not item["reviewed_location"]
            or item["reference_source_id"] not in source_by_id
        ):
            raise ValueError(f"{_LANE_NAME} location quarantine drifted")

    if (
        WAVE8_UTE_OUTCOME_OVERRIDES
        or WAVE8_UTE_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_UTE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty duplicate/override audit changed")
    if set(WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_UTE_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate-name audit is incomplete")
    for item in WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(item["aliases"]):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if any(alias != normalize_label(alias) for alias in item["aliases"]):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not normalized")
        if tuple(item["years"]) != tuple(sorted(set(map(int, item["years"])))):
            raise ValueError(f"{_LANE_NAME} duplicate years are not canonical")

    expected_integration = {
        **{
            f"exact:{key}": value for key, value in _EXACT_DISPOSITIONS.items()
        },
        **{
            f"related_hced:{key}": value
            for key, value in WAVE8_UTE_RELATED_HCED_DISPOSITIONS.items()
        },
        **{
            f"cross_lane:{key}": value
            for key, value in WAVE8_UTE_CROSS_LANE_DISPOSITIONS.items()
        },
    }
    if WAVE8_UTE_INTEGRATION_DISPOSITIONS != expected_integration:
        raise ValueError(f"{_LANE_NAME} integration inventory changed")
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")


def _is_exact_ute_label(value: Any) -> bool:
    return normalize_label(value) == "ute indians"


def _queue_sha256(rows: Iterable[Mapping[str, Any]]) -> str:
    payload = "".join(
        json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n"
        for row in rows
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_wave8_ute_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate the complete locked queue and all four exact-label rows."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_UTE_CONTRACTS,
        WAVE8_UTE_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_ute_label(row.get("side_1_raw"))
        or _is_exact_ute_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_UTE_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Ute Indians inventory changed: {sorted(exact_ids)}"
        )
    alternate_labels = set(
        WAVE8_UTE_ALTERNATE_LABEL_AUDIT["reviewed_alternate_side_labels"]
    )
    alternate_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) in alternate_labels
        or normalize_label(row.get("side_2_raw")) in alternate_labels
    }
    if alternate_ids:
        raise ValueError(
            f"{_LANE_NAME} alternate Ute side-label inventory changed: "
            f"{sorted(alternate_ids)}"
        )
    actual_queue_hash = _queue_sha256(hced_rows)
    if actual_queue_hash != WAVE8_UTE_HCED_QUEUE_SHA256:
        raise ValueError(
            f"{_LANE_NAME} HCED queue snapshot changed "
            f"({actual_queue_hash} != {WAVE8_UTE_HCED_QUEUE_SHA256})"
        )
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_UTE_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_UTE_TERMINAL_EXCLUSIONS),
    }


def _year(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        parsed = _year(row.get(field))
        if parsed is not None:
            return parsed
    for field in ("start_date", "end_date"):
        text = str(row.get(field) or "")
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4])
    return None


def _audited_name_year_pairs() -> set[tuple[int, str]]:
    return {
        (int(year), normalize_label(alias))
        for item in WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT.values()
        for year in item["years"]
        for alias in item["aliases"]
    }


def validate_wave8_ute_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Validate adjacent ownership, duplicate surfaces, and release overlap."""

    _validate_static()
    audited = _audited_name_year_pairs()
    adjacent_ids = set(WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS)

    hced_collisions = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id") or "")
        not in (WAVE8_UTE_RESERVED_IDS | adjacent_ids)
        and (_row_year(row), normalize_label(row.get("name"))) in audited
    )
    if hced_collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_collisions}"
        )

    iwbd_collisions = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name"))) in audited
    )
    if iwbd_collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): {iwbd_collisions}"
        )

    events = list(existing_events)
    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for event in events:
        candidate_id = event.get("hced_candidate_id")
        if candidate_id is not None:
            by_candidate.setdefault(str(candidate_id), []).append(event)
    nonpromotion_overlap = WAVE8_UTE_NONPROMOTIONS.keys() & by_candidate.keys()
    if nonpromotion_overlap:
        raise ValueError(
            f"{_LANE_NAME} nonpromotion entered release: "
            f"{sorted(nonpromotion_overlap)}"
        )
    lane_overlap = WAVE8_UTE_CONTRACT_IDS & by_candidate.keys()
    if len(lane_overlap) not in {0, len(WAVE8_UTE_CONTRACT_IDS)}:
        raise ValueError(
            f"{_LANE_NAME} partial release integration: {sorted(lane_overlap)}"
        )
    for candidate_id in lane_overlap:
        owned = by_candidate[candidate_id]
        if len(owned) != 1:
            raise ValueError(
                f"{_LANE_NAME} partial or duplicate release overlap for {candidate_id}"
            )
        event = owned[0]
        canonical = WAVE8_UTE_CONTRACTS[candidate_id]["canonical_event"]
        if (
            not str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or normalize_label(event.get("name")) != normalize_label(canonical["name"])
            or _row_year(event) != canonical["year_low"]
        ):
            raise ValueError(f"{_LANE_NAME} release owner drifted for {candidate_id}")

    release_collisions: list[str] = []
    for event in events:
        candidate_id = str(event.get("hced_candidate_id") or "")
        if candidate_id in WAVE8_UTE_CONTRACT_IDS:
            continue
        year = _row_year(event)
        names = {
            normalize_label(event.get("name")),
            *map(normalize_label, event.get("aliases", [])),
        }
        if year is not None and any((year, name) in audited for name in names):
            release_collisions.append(str(event.get("id") or "<missing-id>"))
    if release_collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): "
            f"{sorted(release_collisions)}"
        )

    hced_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        hced_by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, item in WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS.items():
        rows = hced_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one adjacent HCED row {candidate_id}, "
                f"found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != item["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} adjacent HCED fingerprint changed")
    validate_wave8_ute_queue_contracts(hced_rows)
    if _queue_sha256(iwbd_rows) != WAVE8_UTE_IWBD_QUEUE_SHA256:
        raise ValueError(f"{_LANE_NAME} IWBD queue snapshot changed")

    return {
        "adjacent_hced_dispositions": len(WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_UTE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(WAVE8_UTE_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_UTE_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_probable_twins": 0,
        "release_lane_overlap": len(lane_overlap),
        "related_hced_dispositions": len(WAVE8_UTE_RELATED_HCED_DISPOSITIONS),
    }


def install_wave8_ute_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_UTE_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_ute_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_UTE_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_UTE_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_UTE_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_ute_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_ute_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_UTE_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_ute_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_UTE_CONTRACTS.values(),
                    *WAVE8_UTE_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_ute_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_hced_dispositions": len(WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS),
        "country_quarantine_additions": len(WAVE8_UTE_COUNTRY_QUARANTINE_ADDITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_UTE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_UTE_HOLDS),
        "integration_dispositions": len(WAVE8_UTE_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_UTE_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_zero_overlap_candidates": len(WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT),
        "new_entities": len(WAVE8_UTE_ENTITIES),
        "new_sources": len(WAVE8_UTE_SOURCES),
        "newly_rated_events": len(WAVE8_UTE_CONTRACTS),
        "opposite_result_pairs": len(
            WAVE8_UTE_OPPOSITE_RESULT_AUDIT["same_event_opposite_result_pairs"]
        ),
        "outcome_overrides": len(WAVE8_UTE_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(WAVE8_UTE_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_UTE_CONTRACTS),
        "related_hced_dispositions": len(WAVE8_UTE_RELATED_HCED_DISPOSITIONS),
        "reviewed_hced_rows": len(WAVE8_UTE_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_UTE_TERMINAL_EXCLUSIONS),
    }


def wave8_ute_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable promoted-only location quarantine additions."""

    _validate_static()
    return {
        "country": WAVE8_UTE_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_UTE_POINT_QUARANTINE_ADDITIONS,
    }
