"""Exact Wave 8 dispositions for HCED rows labelled ``Kickapoo Indians``.

The locked HCED snapshot contains six exact-label rows, rather than the five
suggested by the stale unresolved-label funnel.  Four rows describe source-
attested competitive engagements and are promoted with event-bounded fighting
formations on both sides.  The Killough and Wichita Agency rows are terminally
excluded: one is a civilian massacre with unresolved attacker composition and
the other conflates an agency attack with the following Tonkawa massacre.

No fixture in this lane represents the Kickapoo people, an ethnic label, a
modern tribal government, Texas, the Confederacy, or a military service across
time.  Unknown and noncompetitive outcomes are never converted to draws.
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
    "WAVE8_KICKAPOO_CONTRACT_IDS",
    "WAVE8_KICKAPOO_CONTRACTS",
    "WAVE8_KICKAPOO_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS",
    "WAVE8_KICKAPOO_ENTITIES",
    "WAVE8_KICKAPOO_EXCLUSION_IDS",
    "WAVE8_KICKAPOO_EXCLUSIONS",
    "WAVE8_KICKAPOO_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_KICKAPOO_EXPECTED_CANDIDATE_IDS",
    "WAVE8_KICKAPOO_FINAL_AUDIT_SIGNATURE",
    "WAVE8_KICKAPOO_HCED_QUEUE_SHA256",
    "WAVE8_KICKAPOO_HOLD_IDS",
    "WAVE8_KICKAPOO_HOLDS",
    "WAVE8_KICKAPOO_INTEGRATION_DISPOSITIONS",
    "WAVE8_KICKAPOO_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_KICKAPOO_IWBD_QUEUE_SHA256",
    "WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_KICKAPOO_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_KICKAPOO_LOCATION_QUARANTINE_REASONS",
    "WAVE8_KICKAPOO_NONPROMOTIONS",
    "WAVE8_KICKAPOO_OUTCOME_OVERRIDES",
    "WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS",
    "WAVE8_KICKAPOO_RESERVED_IDS",
    "WAVE8_KICKAPOO_ROW_HASHES",
    "WAVE8_KICKAPOO_SOURCES",
    "WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS",
    "WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS",
    "install_wave8_kickapoo_entities",
    "install_wave8_kickapoo_sources",
    "promote_wave8_kickapoo_contracts",
    "validate_wave8_kickapoo_integration_dispositions",
    "validate_wave8_kickapoo_queue_contracts",
    "wave8_kickapoo_audit_signature",
    "wave8_kickapoo_cohort_counts",
    "wave8_kickapoo_counts",
    "wave8_kickapoo_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Kickapoo Indians exact-force audit"
_MODULE_OWNER = "wave8_kickapoo"
_EVENT_ID_PREFIX = "hced_wave8_kickapoo_"

_BATTLE_CREEK_WAR_PARTY_ID = "battle_creek_allied_indigenous_war_party_1838"
_BATTLE_CREEK_SURVEY_PARTY_ID = "battle_creek_armed_surveying_party_1838"
_KICKAPOO_TOWN_ALLIED_FORCE_ID = (
    "kickapoo_town_allied_indigenous_mexican_fighting_force_1838"
)
_RUSK_MILITIA_COLUMN_ID = "rusk_texas_militia_column_kickapoo_town_1838"
_LITTLE_CONCHO_DEFENDERS_ID = "machemanet_kickapoo_camp_defenders_1862"
_LITTLE_CONCHO_PATROL_ID = "confederate_cavalry_patrol_little_concho_1862"
_DOVE_CREEK_DEFENDERS_ID = "dove_creek_kickapoo_camp_defenders_1865"
_DOVE_CREEK_ASSAULT_FORCE_ID = (
    "dove_creek_confederate_texas_militia_assault_force_1865"
)


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


WAVE8_KICKAPOO_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_kickapoo_kttt_official",
        "Kickapoo Traditional Tribe of Texas",
        "https://kickapootexas.org/",
        "Kickapoo Traditional Tribe of Texas",
        "official_tribal_government_identity_reference",
        "kickapoo_traditional_tribe_of_texas",
    ),
    _source(
        "wave8_kickapoo_tsha_people",
        "Kickapoo Indians",
        "https://www.tshaonline.org/handbook/entries/kickapoo-indians",
        "Texas State Historical Association",
        "scholarly_state_historical_encyclopedia",
        "tsha_kickapoo_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kickapoo_tsha_battle_creek",
        "Battle Creek Fight",
        "https://www.tshaonline.org/handbook/entries/battle-creek-fight",
        "Texas State Historical Association",
        "scholarly_state_historical_encyclopedia",
        "tsha_battle_creek_fight",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kickapoo_thc_battle_creek_marker",
        "Battle Creek Burial Ground historical marker",
        "https://atlas.thc.texas.gov/Details/5349008271",
        "Texas Historical Commission",
        "state_government_historical_marker",
        "thc_battle_creek_marker",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kickapoo_tsha_cherokee_war",
        "Cherokee War",
        "https://www.tshaonline.org/handbook/entries/cherokee-war",
        "Texas State Historical Association",
        "scholarly_state_historical_encyclopedia",
        "tsha_cherokee_war",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kickapoo_thc_kickapoo_battlefield_marker",
        "Site of Kickapoo Battlefield historical marker",
        "https://atlas.thc.texas.gov/Details/5001008770/print",
        "Texas Historical Commission",
        "state_government_historical_marker",
        "thc_kickapoo_battlefield_marker",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kickapoo_govinfo_rusk_report",
        "Official account of the 16 October 1838 battle near Kickapoo village",
        (
            "https://www.govinfo.gov/content/pkg/"
            "SERIALSET-00512_00_00-172-0171-0000/pdf/"
            "SERIALSET-00512_00_00-172-0171-0000.pdf"
        ),
        "U.S. Government Publishing Office, U.S. Congressional Serial Set",
        "digitized_government_primary_document",
        "republic_of_texas_official_rusk_battle_report",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kickapoo_kshq_no_koaht",
        "No-ko-aht's Talk: A Kickapoo Chief's Account of the Kickapoo Indians",
        "https://www.kancoll.org/khq/1932/32_2_root.htm",
        "Kansas Historical Quarterly",
        "published_tribal_oral_history_primary_account",
        "no_koaht_little_concho_account",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kickapoo_gibson_monograph",
        "The Kickapoos: Lords of the Middle Border",
        "https://books.google.com/books?id=QDUiWKyyF4AC",
        "University of Oklahoma Press",
        "scholarly_monograph",
        "gibson_kickapoo_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kickapoo_tsha_knickerbocker",
        "Knickerbocker, Texas",
        "https://www.tshaonline.org/handbook/entries/knickerbocker-tx",
        "Texas State Historical Association",
        "scholarly_location_reference",
        "tsha_knickerbocker_location",
    ),
    _source(
        "wave8_kickapoo_tsha_dove_creek",
        "Dove Creek, Battle of",
        "https://www.tshaonline.org/handbook/entries/dove-creek-battle-of",
        "Texas State Historical Association",
        "scholarly_state_historical_encyclopedia",
        "tsha_dove_creek_battle",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kickapoo_or_dove_creek_inquiry",
        "Official inquiry into the Dove Creek expedition",
        "https://texashistory.unt.edu/ark:/67531/metapth139842/m1/42/",
        "U.S. War Department; University of North Texas Libraries",
        "digitized_federal_archival_primary_document",
        "official_records_dove_creek_inquiry",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kickapoo_pool_dove_creek",
        "The Battle of Dove Creek",
        "https://texashistory.unt.edu/ark:/67531/metapth101126/m1/482/",
        "Southwestern Historical Quarterly; University of North Texas Libraries",
        "peer_reviewed_scholarly_article",
        "pool_dove_creek_study",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kickapoo_tsha_killough",
        "Killough Massacre",
        "https://www.tshaonline.org/handbook/entries/killough-massacre",
        "Texas State Historical Association",
        "scholarly_state_historical_encyclopedia",
        "tsha_killough_massacre",
    ),
    _source(
        "wave8_kickapoo_nps_newtonia_study",
        "Newtonia Battlefields Special Resource Study",
        "https://parkplanning.nps.gov/showFile.cfm?projectID=31498&sfid=148234",
        "U.S. National Park Service",
        "federal_special_resource_study",
        "nps_newtonia_civil_war_indian_territory_study",
    ),
    _source(
        "wave8_kickapoo_ohs_tonkawa_massacre",
        "Tonkawa Massacre",
        "https://www.okhistory.org/publications/enc/entry?entry=TO005",
        "Oklahoma Historical Society",
        "scholarly_state_historical_encyclopedia",
        "ohs_tonkawa_massacre",
    ),
    _source(
        "wave8_kickapoo_connole_tonkawa",
        "A Terrible Truth: The Tonkawa Massacre of 1862",
        "https://gateway.okhistory.org/ark:/67531/metadc2017477/",
        "Chronicles of Oklahoma; Oklahoma Historical Society",
        "peer_reviewed_scholarly_article",
        "connole_tonkawa_massacre_study",
    ),
)


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_KICKAPOO_SOURCES
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
            "No rating is inherited by the Kickapoo people, any ethnic label, "
            "noncombatants or travelling families, a modern tribal government, "
            "Texas, the Confederacy, a military service, or any later formation."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_KICKAPOO_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _BATTLE_CREEK_WAR_PARTY_ID,
        "Battle Creek allied Kickapoo-Cherokee-Delaware war party (1838)",
        "war_party",
        1838,
        [
            "wave8_kickapoo_kttt_official",
            "wave8_kickapoo_thc_battle_creek_marker",
            "wave8_kickapoo_tsha_battle_creek",
            "wave8_kickapoo_tsha_people",
        ],
        (
            "Event-bounded armed coalition attested at Battle Creek; it excludes "
            "every civilian or unverified member of the named peoples."
        ),
    ),
    _entity(
        _BATTLE_CREEK_SURVEY_PARTY_ID,
        "Battle Creek armed surveying party (1838)",
        "armed_party",
        1838,
        [
            "wave8_kickapoo_thc_battle_creek_marker",
            "wave8_kickapoo_tsha_battle_creek",
        ],
        "The bounded party is the twenty-five armed surveyors in this fight.",
    ),
    _entity(
        _KICKAPOO_TOWN_ALLIED_FORCE_ID,
        "Kickapoo Town allied Indigenous-Mexican fighting force (1838)",
        "allied_fighting_force",
        1838,
        [
            "wave8_kickapoo_govinfo_rusk_report",
            "wave8_kickapoo_kttt_official",
            "wave8_kickapoo_tsha_cherokee_war",
            "wave8_kickapoo_tsha_people",
        ],
        (
            "Event-bounded defenders and allies encountered near Kickapoo Town; "
            "the fixture does not assert a stable intertribal coalition."
        ),
    ),
    _entity(
        _RUSK_MILITIA_COLUMN_ID,
        "Thomas J. Rusk's Texas militia column at Kickapoo Town (1838)",
        "militia_column",
        1838,
        [
            "wave8_kickapoo_govinfo_rusk_report",
            "wave8_kickapoo_thc_kickapoo_battlefield_marker",
            "wave8_kickapoo_tsha_cherokee_war",
        ],
        "Event-bounded Republic of Texas militia column under Thomas J. Rusk.",
    ),
    _entity(
        _LITTLE_CONCHO_DEFENDERS_ID,
        "Machemanet's Kickapoo camp defense force at Little Concho (1862)",
        "camp_defense_force",
        1862,
        [
            "wave8_kickapoo_gibson_monograph",
            "wave8_kickapoo_kshq_no_koaht",
            "wave8_kickapoo_kttt_official",
        ],
        (
            "Event-bounded fighters defending Machemanet's camp; accompanying "
            "families are expressly outside the rated formation."
        ),
    ),
    _entity(
        _LITTLE_CONCHO_PATROL_ID,
        "Confederate cavalry patrol at Little Concho (1862)",
        "cavalry_patrol",
        1862,
        [
            "wave8_kickapoo_gibson_monograph",
            "wave8_kickapoo_kshq_no_koaht",
        ],
        "Event-bounded mounted patrol that attacked the camp near Knickerbocker.",
    ),
    _entity(
        _DOVE_CREEK_DEFENDERS_ID,
        "Kickapoo camp defense force at Dove Creek (1865)",
        "camp_defense_force",
        1865,
        [
            "wave8_kickapoo_gibson_monograph",
            "wave8_kickapoo_kttt_official",
            "wave8_kickapoo_pool_dove_creek",
            "wave8_kickapoo_tsha_dove_creek",
            "wave8_kickapoo_tsha_people",
        ],
        (
            "Event-bounded fighters who defended the migrating camps; women, "
            "children, elders, and every other noncombatant are excluded."
        ),
    ),
    _entity(
        _DOVE_CREEK_ASSAULT_FORCE_ID,
        "Dove Creek Confederate-Texas militia assault force (1865)",
        "combined_assault_force",
        1865,
        [
            "wave8_kickapoo_or_dove_creek_inquiry",
            "wave8_kickapoo_pool_dove_creek",
            "wave8_kickapoo_tsha_dove_creek",
        ],
        (
            "Event-bounded combined Confederate cavalry and Texas frontier "
            "militia force assembled for the Dove Creek attack."
        ),
    ),
)


WAVE8_KICKAPOO_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_KICKAPOO_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)
WAVE8_KICKAPOO_ROW_HASHES: dict[str, str] = {
    "hced-Battle Creek, Texas1838-1": (
        "5833bba8079f29acc8ce74a0b08644753a1ba5931f2299edf900ccbe71c9cf7a"
    ),
    "hced-Dove Creek1865-1": (
        "2b3745128b539c57b34483dcd78912da81c9baf52e8ca59e1023085e0c2eda39"
    ),
    "hced-Kickapoo Town1838-1": (
        "90c57dea7caa1ca95fa5957a82b335a58dff59b2b8c94fa2e7d2ade5005ee15a"
    ),
    "hced-Killough Massacre1838-1": (
        "15459a01b094ac12bd1e2991c2b09bd2d265285dfa45f4815658abd05d47121f"
    ),
    "hced-Little Concho1862-1": (
        "731da8dc895eff1e3302e00c7e64efafff602c66805fb8c4907174e008ac4b46"
    ),
    "hced-Wichita Agency1862-1": (
        "7aa936e568ce02973c088328b3f9f279112e39cb9512c9a410ecfa34ce3cc82b"
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
        "raw_row_sha256": WAVE8_KICKAPOO_ROW_HASHES[candidate_id],
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


WAVE8_KICKAPOO_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Battle Creek, Texas1838-1": _contract(
        "hced-Battle Creek, Texas1838-1",
        _canonical("Battle Creek Fight", 1838, "8 October 1838"),
        "republic_of_texas_frontier_conflict_1838",
        [_BATTLE_CREEK_WAR_PARTY_ID],
        [_BATTLE_CREEK_SURVEY_PARTY_ID],
        [
            "wave8_kickapoo_thc_battle_creek_marker",
            "wave8_kickapoo_tsha_battle_creek",
            "wave8_kickapoo_tsha_people",
        ],
        [
            "wave8_kickapoo_thc_battle_creek_marker",
            "wave8_kickapoo_tsha_battle_creek",
        ],
        (
            "The twenty-five surveyors were surrounded for roughly twenty-four "
            "hours; eighteen were killed and seven escaped. The reviewed result is "
            "the allied war party's tactical victory, not a rating for any people. "
            "The raw coordinate is displaced from the state marker and is withheld."
        ),
        confidence=0.92,
    ),
    "hced-Kickapoo Town1838-1": _contract(
        "hced-Kickapoo Town1838-1",
        _canonical("Battle of Kickapoo Town", 1838, "16 October 1838"),
        "republic_of_texas_frontier_conflict_1838",
        [_RUSK_MILITIA_COLUMN_ID],
        [_KICKAPOO_TOWN_ALLIED_FORCE_ID],
        [
            "wave8_kickapoo_govinfo_rusk_report",
            "wave8_kickapoo_thc_kickapoo_battlefield_marker",
            "wave8_kickapoo_tsha_cherokee_war",
            "wave8_kickapoo_tsha_people",
        ],
        [
            "wave8_kickapoo_govinfo_rusk_report",
            "wave8_kickapoo_thc_kickapoo_battlefield_marker",
            "wave8_kickapoo_tsha_cherokee_war",
        ],
        (
            "The official report, state marker, and scholarly account agree that "
            "Rusk's militia charged and routed the allied force, then destroyed the "
            "village. This is a tactical engagement result only. The raw point is "
            "several kilometres from the marker reference and is withheld."
        ),
        confidence=0.96,
    ),
    "hced-Little Concho1862-1": _contract(
        "hced-Little Concho1862-1",
        _canonical(
            "Little Concho engagement",
            1862,
            "December 1862",
            date_precision="month",
        ),
        "kickapoo_migration_confederate_conflict_1862_1865",
        [_LITTLE_CONCHO_DEFENDERS_ID],
        [_LITTLE_CONCHO_PATROL_ID],
        [
            "wave8_kickapoo_gibson_monograph",
            "wave8_kickapoo_kshq_no_koaht",
            "wave8_kickapoo_tsha_knickerbocker",
        ],
        [
            "wave8_kickapoo_gibson_monograph",
            "wave8_kickapoo_kshq_no_koaht",
        ],
        (
            "No-ko-aht's account and the scholarly history describe the camp "
            "defenders repelling the mounted attack, with sixteen cavalrymen "
            "mortally wounded. The month-level date is retained and no later Dove "
            "Creek result is imported. HCED's point lies far from Knickerbocker and "
            "is withheld."
        ),
        confidence=0.86,
    ),
    "hced-Dove Creek1865-1": _contract(
        "hced-Dove Creek1865-1",
        _canonical("Battle of Dove Creek", 1865, "8 January 1865"),
        "kickapoo_migration_confederate_conflict_1862_1865",
        [_DOVE_CREEK_DEFENDERS_ID],
        [_DOVE_CREEK_ASSAULT_FORCE_ID],
        [
            "wave8_kickapoo_gibson_monograph",
            "wave8_kickapoo_or_dove_creek_inquiry",
            "wave8_kickapoo_pool_dove_creek",
            "wave8_kickapoo_tsha_dove_creek",
            "wave8_kickapoo_tsha_people",
        ],
        [
            "wave8_kickapoo_or_dove_creek_inquiry",
            "wave8_kickapoo_pool_dove_creek",
            "wave8_kickapoo_tsha_dove_creek",
        ],
        (
            "The archival inquiry and independent histories agree that the camp "
            "defenders repelled and routed the combined attacking force. The "
            "migrating families are not participants. The raw point is materially "
            "northeast of the reviewed Dove and Spring Creeks locality and is "
            "withheld."
        ),
        confidence=0.97,
    ),
}


WAVE8_KICKAPOO_HOLDS: dict[str, dict[str, Any]] = {}


def _terminal_exclusion(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    historical_review: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_KICKAPOO_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "hold_category": category,
        "hold_reason": reason,
        "reviewed_outcome": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_granularity": str(canonical_event["granularity"]),
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "terminal_hced_owner",
        },
        "historical_review": dict(historical_review),
    }


WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Killough Massacre1838-1": _terminal_exclusion(
        "hced-Killough Massacre1838-1",
        _canonical(
            "Killough settlement massacre",
            1838,
            "5 October 1838",
            granularity="civilian_massacre",
        ),
        "republic_of_texas_frontier_conflict_1838",
        "civilian_massacre_with_unresolved_attacker_composition",
        (
            "The event was an attack on a civilian settlement, not a competitive "
            "engagement. The detailed TSHA review says the exact attacking "
            "composition is unknown, while broader summaries associate subsequent "
            "violence with several peoples. HCED's United States side is also "
            "anachronistic for Republic of Texas territory. No exact Kickapoo "
            "fighting formation or Elo outcome can be recovered; unknown is never "
            "made a draw."
        ),
        [
            "wave8_kickapoo_tsha_killough",
            "wave8_kickapoo_tsha_people",
        ],
        {
            "attacked_group": "Killough settlement civilians",
            "competitive_event": False,
            "exact_attacker_composition": "unknown",
            "raw_side_problem": "United States is anachronistic in October 1838",
        },
    ),
    "hced-Wichita Agency1862-1": _terminal_exclusion(
        "hced-Wichita Agency1862-1",
        _canonical(
            "Sacking of the Wichita Agency and Tonkawa Massacre",
            1862,
            "23-24 October 1862",
            date_precision="day_range",
            granularity="composite_noncompetitive_massacre",
        ),
        "wichita_agency_tonkawa_massacre_1862",
        "composite_agency_attack_and_civilian_massacre",
        (
            "The row fuses two sequential episodes: the 23 October attack on the "
            "Wichita Agency and the 24 October killing of Tonkawa people. The NPS "
            "study expressly treats this violence as outside its definition of a "
            "battle, and the Oklahoma scholarship documents a massacre rather than "
            "opposing competitive formations. A Kickapoo component is attested, "
            "but neither episode licenses a timeless actor or an Elo result; "
            "unknown is never made a draw."
        ),
        [
            "wave8_kickapoo_connole_tonkawa",
            "wave8_kickapoo_nps_newtonia_study",
            "wave8_kickapoo_ohs_tonkawa_massacre",
        ],
        {
            "episode_1": "23 October attack on Wichita Agency personnel and property",
            "episode_2": "24 October Tonkawa massacre",
            "competitive_event": False,
            "repair_risk": "would merge two episodes and rate civilian victims",
        },
    ),
}

WAVE8_KICKAPOO_EXCLUSIONS = WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS
WAVE8_KICKAPOO_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_KICKAPOO_HOLDS,
    **WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS,
}

WAVE8_KICKAPOO_CONTRACT_IDS = frozenset(WAVE8_KICKAPOO_CONTRACTS)
WAVE8_KICKAPOO_HOLD_IDS = frozenset(WAVE8_KICKAPOO_HOLDS)
WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS
)
WAVE8_KICKAPOO_EXCLUSION_IDS = WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS
WAVE8_KICKAPOO_RESERVED_IDS = frozenset(
    WAVE8_KICKAPOO_CONTRACT_IDS
    | WAVE8_KICKAPOO_HOLD_IDS
    | WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS
)
WAVE8_KICKAPOO_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_KICKAPOO_ROW_HASHES)


# Location review is promoted-only. Every promoted raw point is displaced from
# or more precise than the reviewed source location; all four valid modern-
# country assertions remain. Excluded rows never enter location output.
WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_KICKAPOO_CONTRACT_IDS
)
WAVE8_KICKAPOO_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_KICKAPOO_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_KICKAPOO_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_KICKAPOO_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Battle Creek, Texas1838-1": {
        "field": "geometry",
        "raw_point": [-96.6309648, 31.9265462],
        "reference_source_id": "wave8_kickapoo_thc_battle_creek_marker",
        "reviewed_reference_point": [-96.73947833, 31.89110999],
        "reason": (
            "The HCED point is roughly eleven kilometres from the Texas marker "
            "reference and is not retained as an exact fight location."
        ),
    },
    "hced-Dove Creek1865-1": {
        "field": "geometry",
        "raw_point": [-100.4731302, 31.470453],
        "reference_source_id": "wave8_kickapoo_pool_dove_creek",
        "reviewed_reference_point": [-100.600833, 31.331111],
        "reason": (
            "The HCED point is materially northeast of the Dove and Spring Creeks "
            "battlefield locality described in the scholarly site review."
        ),
    },
    "hced-Kickapoo Town1838-1": {
        "field": "geometry",
        "raw_point": [-95.5222962, 32.0584983],
        "reference_source_id": "wave8_kickapoo_thc_kickapoo_battlefield_marker",
        "reviewed_reference_point": [-95.48846209, 32.02395208],
        "reason": (
            "The HCED point is about five kilometres from the Texas marker "
            "reference and is not retained as an exact battlefield coordinate."
        ),
    },
    "hced-Little Concho1862-1": {
        "field": "geometry",
        "raw_point": [-99.991057, 31.517953],
        "reference_source_id": "wave8_kickapoo_tsha_knickerbocker",
        "reviewed_reference_point": [-100.6231537, 31.2665549],
        "reason": (
            "The primary account places the action near a ranch about two miles "
            "from Knickerbocker; HCED's point is many tens of kilometres away."
        ),
    },
}


# All four promoted winner/loser orientations agree with HCED and the reviewed
# evidence. The two nonpromotions contain no corrected or inferred result.
WAVE8_KICKAPOO_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Battle Creek, Texas1838-1": {
        "raw_row_sha256": WAVE8_KICKAPOO_ROW_HASHES[
            "hced-Battle Creek, Texas1838-1"
        ],
        "related_hced_candidate_id": "hced-Kickapoo Town1838-1",
        "related_raw_row_sha256": WAVE8_KICKAPOO_ROW_HASHES[
            "hced-Kickapoo Town1838-1"
        ],
        "disposition": "distinct_linked_engagements",
        "relationship": "same_month_distinct_forces_sites_and_dates",
        "owner_module": _MODULE_OWNER,
        "reason": (
            "Battle Creek occurred on 8 October and Kickapoo Town on 16 October, "
            "with different objectives, sites, and bounded formations."
        ),
        "evidence_refs": [
            "wave8_kickapoo_govinfo_rusk_report",
            "wave8_kickapoo_tsha_battle_creek",
        ],
    },
    "hced-Killough Massacre1838-1": {
        "raw_row_sha256": WAVE8_KICKAPOO_ROW_HASHES[
            "hced-Killough Massacre1838-1"
        ],
        "related_hced_candidate_id": "hced-Kickapoo Town1838-1",
        "related_raw_row_sha256": WAVE8_KICKAPOO_ROW_HASHES[
            "hced-Kickapoo Town1838-1"
        ],
        "disposition": "distinct_massacre_and_later_engagement",
        "relationship": "linked_frontier_context_not_duplicate",
        "owner_module": _MODULE_OWNER,
        "reason": (
            "The 5 October civilian massacre and 16 October militia engagement "
            "have separate victims, forces, places, and event boundaries."
        ),
        "evidence_refs": [
            "wave8_kickapoo_govinfo_rusk_report",
            "wave8_kickapoo_tsha_killough",
        ],
    },
    "hced-Little Concho1862-1": {
        "raw_row_sha256": WAVE8_KICKAPOO_ROW_HASHES[
            "hced-Little Concho1862-1"
        ],
        "related_hced_candidate_id": "hced-Dove Creek1865-1",
        "related_raw_row_sha256": WAVE8_KICKAPOO_ROW_HASHES[
            "hced-Dove Creek1865-1"
        ],
        "disposition": "distinct_migration_conflict_engagements",
        "relationship": "different_year_force_location_and_attack",
        "owner_module": _MODULE_OWNER,
        "reason": (
            "The December 1862 Little Concho defense is not the January 1865 Dove "
            "Creek attack; the scholarly history treats them as separate actions."
        ),
        "evidence_refs": [
            "wave8_kickapoo_gibson_monograph",
            "wave8_kickapoo_kshq_no_koaht",
            "wave8_kickapoo_tsha_dove_creek",
        ],
    },
    "hced-Wichita Agency1862-1": {
        "raw_row_sha256": WAVE8_KICKAPOO_ROW_HASHES[
            "hced-Wichita Agency1862-1"
        ],
        "related_hced_candidate_id": "hced-Little Concho1862-1",
        "related_raw_row_sha256": WAVE8_KICKAPOO_ROW_HASHES[
            "hced-Little Concho1862-1"
        ],
        "disposition": "distinct_same_year_episodes",
        "relationship": "different_month_territory_actors_and_granularity",
        "owner_module": _MODULE_OWNER,
        "reason": (
            "The October agency attack and massacre in Indian Territory are not "
            "the December camp defense near Knickerbocker, Texas."
        ),
        "evidence_refs": [
            "wave8_kickapoo_kshq_no_koaht",
            "wave8_kickapoo_nps_newtonia_study",
        ],
    },
}


# Battle Creek includes attested Cherokee participants, but the exact-label
# Cherokee lane owns different candidates. Shared membership is not duplicate
# ownership and does not create a Cherokee or Kickapoo fallback identity.
WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "wave8_cherokee": {
        "disposition": "shared_component_not_duplicate",
        "other_module": "wave8_cherokee",
        "owned_candidate_ids": ["hced-Battle Creek, Texas1838-1"],
        "shared_component": "Cherokee participants in the Battle Creek war party",
        "reason": (
            "The Cherokee lane owns no candidate in this inventory. This lane owns "
            "the exact Battle Creek row and rates only its mixed event formation."
        ),
        "evidence_refs": ["wave8_kickapoo_tsha_battle_creek"],
    }
}


WAVE8_KICKAPOO_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_KICKAPOO_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_KICKAPOO_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"related_hced:{candidate_id}": disposition
        for candidate_id, disposition in (
            WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS.items()
        )
    },
    **{
        f"cross_lane:{module}": disposition
        for module, disposition in WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS.items()
    },
}


# Candidate-keyed negative duplicate audit for the locked HCED, IWBD, and
# existing-release inventories. Alternate titles make future twins fail closed.
WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Battle Creek, Texas1838-1": {
        "aliases": (
            "battle creek fight",
            "battle creek texas",
            "surveyors fight",
            "the surveyors fight",
        ),
        "years": (1838,),
    },
    "hced-Dove Creek1865-1": {
        "aliases": (
            "battle of dove creek",
            "dove creek",
            "dove creek battle",
        ),
        "years": (1865,),
    },
    "hced-Kickapoo Town1838-1": {
        "aliases": (
            "battle of kickapoo",
            "battle of kickapoo town",
            "kickapoo battlefield",
            "kickapoo town",
            "kickapoo village",
        ),
        "years": (1838,),
    },
    "hced-Killough Massacre1838-1": {
        "aliases": (
            "killough massacre",
            "killough settlement massacre",
        ),
        "years": (1838,),
    },
    "hced-Little Concho1862-1": {
        "aliases": (
            "battle of little concho",
            "little concho",
            "little concho engagement",
            "little concho river",
            "little concho river fight",
        ),
        "years": (1862,),
    },
    "hced-Wichita Agency1862-1": {
        "aliases": (
            "attack on wichita agency",
            "sacking of the wichita agency",
            "sacking of the wichita agency and tonkawa massacre",
            "tonkawa massacre",
            "wichita agency",
        ),
        "years": (1862,),
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_KICKAPOO_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_KICKAPOO_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_KICKAPOO_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_KICKAPOO_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_KICKAPOO_EXPECTED_CANDIDATE_IDS),
        "hced_queue_sha256": WAVE8_KICKAPOO_HCED_QUEUE_SHA256,
        "holds": WAVE8_KICKAPOO_HOLDS,
        "integration_dispositions": WAVE8_KICKAPOO_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_KICKAPOO_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_queue_sha256": WAVE8_KICKAPOO_IWBD_QUEUE_SHA256,
        "iwbd_zero_overlap_audit": WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_KICKAPOO_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_KICKAPOO_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS,
        "row_hashes": WAVE8_KICKAPOO_ROW_HASHES,
        "sources": WAVE8_KICKAPOO_SOURCES,
        "terminal_exclusions": WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS,
    }


def wave8_kickapoo_audit_signature() -> str:
    """Return the SHA-256 pin over the complete audited lane state."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


# Measured from the complete payload above. Any fixture or disposition change
# must be consciously re-audited and re-signed.
WAVE8_KICKAPOO_FINAL_AUDIT_SIGNATURE = (
    "56e4a6fcbd1be8225a07bebcd218c938481e079f6c38ec5c926ed8222f255106"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_KICKAPOO_CONTRACTS),
        len(WAVE8_KICKAPOO_HOLDS),
        len(WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS),
    ) != (4, 0, 2):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_KICKAPOO_ENTITIES), len(WAVE8_KICKAPOO_SOURCES)) != (8, 17):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_KICKAPOO_RESERVED_IDS != WAVE8_KICKAPOO_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    dispositions = (
        WAVE8_KICKAPOO_CONTRACT_IDS,
        WAVE8_KICKAPOO_HOLD_IDS,
        WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(3)
        for j in range(i + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if WAVE8_KICKAPOO_EXCLUSIONS is not WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion inventory diverged")
    if any(
        len(value) != 64
        for value in (
            WAVE8_KICKAPOO_HCED_QUEUE_SHA256,
            WAVE8_KICKAPOO_IWBD_QUEUE_SHA256,
            *WAVE8_KICKAPOO_ROW_HASHES.values(),
        )
    ):
        raise ValueError(f"{_LANE_NAME} snapshot hash inventory drifted")
    if wave8_kickapoo_audit_signature() != WAVE8_KICKAPOO_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_KICKAPOO_SOURCES
    }
    if len(source_by_id) != len(WAVE8_KICKAPOO_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_KICKAPOO_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_KICKAPOO_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_KICKAPOO_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "confederate states of america",
        "kickapoo",
        "kickapoo indians",
        "kickapoo traditional tribe of texas",
        "texas",
        "united states",
    }
    for entity in WAVE8_KICKAPOO_ENTITIES:
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity is not event-year bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a timeless identity")
        note = str(entity["continuity_note"]).casefold()
        required_firewalls = (
            "no rating is inherited",
            "noncombatants",
            "modern tribal government",
            "ethnic label",
        )
        if any(term not in note for term in required_firewalls):
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    expected_contracts = {
        "hced-Battle Creek, Texas1838-1": (
            1838,
            "day",
            [_BATTLE_CREEK_WAR_PARTY_ID],
            [_BATTLE_CREEK_SURVEY_PARTY_ID],
        ),
        "hced-Dove Creek1865-1": (
            1865,
            "day",
            [_DOVE_CREEK_DEFENDERS_ID],
            [_DOVE_CREEK_ASSAULT_FORCE_ID],
        ),
        "hced-Kickapoo Town1838-1": (
            1838,
            "day",
            [_RUSK_MILITIA_COLUMN_ID],
            [_KICKAPOO_TOWN_ALLIED_FORCE_ID],
        ),
        "hced-Little Concho1862-1": (
            1862,
            "month",
            [_LITTLE_CONCHO_DEFENDERS_ID],
            [_LITTLE_CONCHO_PATROL_ID],
        ),
    }
    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, expected in expected_contracts.items():
        contract = WAVE8_KICKAPOO_CONTRACTS[candidate_id]
        year, precision, expected_side_1, expected_side_2 = expected
        if contract["raw_row_sha256"] != WAVE8_KICKAPOO_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = f"{_slug(str(canonical['name']))}:{year}:{year}"
        if (
            canonical["canonical_key"] != expected_key
            or canonical["year_low"] != year
            or canonical["year_high"] != year
            or canonical["date_precision"] != precision
            or canonical["granularity"] != "engagement"
            or not canonical["date_text"]
        ):
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if side_1 != expected_side_1 or side_2 != expected_side_2:
            raise ValueError(f"{_LANE_NAME} actor contract drifted")
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unbounded identity")
        used_entities.update(side_1)
        used_entities.update(side_2)
        for entity_id in (*side_1, *side_2):
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["war_type"] != "colonial_anti_colonial"
            or contract["actor_override"] is not True
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
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
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        expected_families = sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
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
    for candidate_id, item in WAVE8_KICKAPOO_NONPROMOTIONS.items():
        if item["raw_row_sha256"] != WAVE8_KICKAPOO_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} nonpromotion hash drifted")
        if forbidden_nonpromotion_keys & set(item):
            raise ValueError(f"{_LANE_NAME} nonpromotion contains a rateable result")
        canonical = item["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} exclusion canonical key drifted")
        if (
            item["disposition"] != "terminal_exclusion"
            or item["terminal_exclusion"] is not True
            or item["reviewed_outcome"] != "unknown"
            or item["unknown_is_never_draw"] is not True
            or item["duplicate_ownership"]
            != {"owner_module": _MODULE_OWNER, "status": "terminal_hced_owner"}
        ):
            raise ValueError(f"{_LANE_NAME} terminal exclusion became rateable")
        evidence = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} nonpromotion evidence drifted")
        if "draw" not in str(item["hold_reason"]).casefold():
            raise ValueError(f"{_LANE_NAME} unknown/draw policy drifted")
        used_sources.update(evidence)

    used_sources.update(
        source_id
        for entity in WAVE8_KICKAPOO_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    expected_related = {
        "hced-Battle Creek, Texas1838-1",
        "hced-Killough Massacre1838-1",
        "hced-Little Concho1862-1",
        "hced-Wichita Agency1862-1",
    }
    if set(WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS) != expected_related:
        raise ValueError(f"{_LANE_NAME} related HCED inventory changed")
    for candidate_id, item in WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS.items():
        related_id = str(item["related_hced_candidate_id"])
        if (
            item["raw_row_sha256"] != WAVE8_KICKAPOO_ROW_HASHES[candidate_id]
            or item["related_raw_row_sha256"]
            != WAVE8_KICKAPOO_ROW_HASHES[related_id]
            or item["owner_module"] != _MODULE_OWNER
        ):
            raise ValueError(f"{_LANE_NAME} related HCED disposition drifted")
        evidence = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} related HCED evidence drifted")
        used_sources.update(evidence)

    if set(WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS) != {"wave8_cherokee"}:
        raise ValueError(f"{_LANE_NAME} cross-lane inventory changed")
    for item in WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS.values():
        if not set(item["owned_candidate_ids"]) <= WAVE8_KICKAPOO_RESERVED_IDS:
            raise ValueError(f"{_LANE_NAME} cross-lane ownership drifted")
        evidence = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} cross-lane evidence drifted")
        used_sources.update(evidence)
    expected_integration = {
        **{
            f"related_hced:{key}": value
            for key, value in WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS.items()
        },
        **{
            f"cross_lane:{key}": value
            for key, value in WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS.items()
        },
    }
    if WAVE8_KICKAPOO_INTEGRATION_DISPOSITIONS != expected_integration:
        raise ValueError(f"{_LANE_NAME} integration inventory changed")

    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS != WAVE8_KICKAPOO_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_KICKAPOO_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_KICKAPOO_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location reasons are incomplete")
    for reason in WAVE8_KICKAPOO_LOCATION_QUARANTINE_REASONS.values():
        if reason["field"] != "geometry":
            raise ValueError(f"{_LANE_NAME} location quarantine field drifted")
        if reason["reference_source_id"] not in source_by_id:
            raise ValueError(f"{_LANE_NAME} location reason names an unknown source")
        if len(reason["raw_point"]) != 2 or len(reason["reviewed_reference_point"]) != 2:
            raise ValueError(f"{_LANE_NAME} location reason has a malformed point")

    if (
        WAVE8_KICKAPOO_OUTCOME_OVERRIDES
        or WAVE8_KICKAPOO_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_KICKAPOO_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")
    if set(WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_KICKAPOO_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    audited_pairs: set[tuple[int, str]] = set()
    for item in WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = item["aliases"]
        years = item["years"]
        if not _is_sorted_unique(aliases) or any(
            alias != normalize_label(alias) for alias in aliases
        ):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if tuple(years) != tuple(sorted(set(map(int, years)))):
            raise ValueError(f"{_LANE_NAME} duplicate years are not canonical")
        audited_pairs.update(
            (int(year), normalize_label(alias))
            for year in years
            for alias in aliases
        )
    canonical_pairs = {
        (
            int(item["canonical_event"]["year_low"]),
            normalize_label(item["canonical_event"]["name"]),
        )
        for item in (
            *WAVE8_KICKAPOO_CONTRACTS.values(),
            *WAVE8_KICKAPOO_NONPROMOTIONS.values(),
        )
    }
    if not canonical_pairs <= audited_pairs:
        raise ValueError(f"{_LANE_NAME} canonical duplicate audit is incomplete")


def _is_exact_kickapoo_label(value: Any) -> bool:
    return normalize_label(value) == "kickapoo indians"


def validate_wave8_kickapoo_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all and only the six exact-label rows and their fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_KICKAPOO_CONTRACTS,
        WAVE8_KICKAPOO_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_kickapoo_label(row.get("side_1_raw"))
        or _is_exact_kickapoo_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_KICKAPOO_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Kickapoo Indians inventory changed: "
            f"{sorted(exact_label_ids)}"
        )
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_KICKAPOO_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS),
    }


def _year(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        year = _year(row.get(field))
        if year is not None:
            return year
    for field in ("start_date", "end_date"):
        text = str(row.get(field) or "")
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4])
    return None


def _audited_name_year_pairs() -> set[tuple[int, str]]:
    return {
        (int(year), normalize_label(alias))
        for item in WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT.values()
        for year in item["years"]
        for alias in item["aliases"]
    }


def validate_wave8_kickapoo_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin related rows and cross-lane ownership; fail on probable twins."""

    validate_wave8_kickapoo_queue_contracts(hced_rows)
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, item in WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS.items():
        related_id = str(item["related_hced_candidate_id"])
        for row_id, hash_field in (
            (candidate_id, "raw_row_sha256"),
            (related_id, "related_raw_row_sha256"),
        ):
            rows = by_id.get(row_id, [])
            if len(rows) != 1:
                raise ValueError(
                    f"{_LANE_NAME} expected one related HCED row {row_id}, "
                    f"found {len(rows)}"
                )
            if canonical_hced_row_sha256(rows[0]) != item[hash_field]:
                raise ValueError(f"{_LANE_NAME} related HCED fingerprint changed")

    # Local import avoids initialization coupling while pinning candidate owners.
    from .wave8_cherokee import WAVE8_CHEROKEE_RESERVED_IDS

    overlap = WAVE8_KICKAPOO_RESERVED_IDS & set(WAVE8_CHEROKEE_RESERVED_IDS)
    if overlap:
        raise ValueError(
            f"{_LANE_NAME} cross-lane ownership collision with wave8_cherokee: "
            f"{sorted(overlap)}"
        )

    audited = _audited_name_year_pairs()
    hced_collisions = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_KICKAPOO_RESERVED_IDS
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
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): "
            f"{iwbd_collisions}"
        )

    release_collisions = []
    for event in existing_events:
        candidate_id = str(event.get("hced_candidate_id") or "")
        if candidate_id in WAVE8_KICKAPOO_RESERVED_IDS:
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

    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_KICKAPOO_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(
            WAVE8_KICKAPOO_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_KICKAPOO_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "related_hced_dispositions": len(
            WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS
        ),
    }


def install_wave8_kickapoo_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_KICKAPOO_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_kickapoo_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_KICKAPOO_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_KICKAPOO_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_kickapoo_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_kickapoo_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_KICKAPOO_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_kickapoo_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_KICKAPOO_CONTRACTS.values(),
                    *WAVE8_KICKAPOO_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_kickapoo_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_KICKAPOO_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_KICKAPOO_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_KICKAPOO_HOLDS),
        "integration_dispositions": len(
            WAVE8_KICKAPOO_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_KICKAPOO_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_KICKAPOO_ENTITIES),
        "new_sources": len(WAVE8_KICKAPOO_SOURCES),
        "newly_rated_events": len(WAVE8_KICKAPOO_CONTRACTS),
        "outcome_overrides": len(WAVE8_KICKAPOO_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_KICKAPOO_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_KICKAPOO_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS),
    }


def wave8_kickapoo_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    """Return immutable promoted-only location quarantine additions."""

    _validate_static()
    return {
        "country": WAVE8_KICKAPOO_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS,
    }
