"""Candidate-keyed Wave 8 audit for HCED's exact ``Modoc Indians`` label.

The four locked rows all belong to the 1872--1873 Modoc War, but they do
not justify a timeless ethnic or national Modoc identity.  Three rows have
independently corroborated, event-bounded outcomes: the first attack on
Captain Jack's Stronghold, the second attack and occupation of the evacuated
Stronghold, and the Thomas--Wright patrol ambush near Schonchin Flow.  Each
uses a formation limited to that action and an equally bounded United States
formation.

The Lost River row stays staged.  The army occupied and burned the village
while Kintpuash's band escaped and the arrest/removal objective failed.  The
locked row says ``Draw`` but also marks its winner/loser record incomplete;
authoritative accounts describe those mixed facts without establishing one
shared result unit.  Treating that ambiguity as a draw, or silently selecting
one tactical/operational scope, would invent an outcome.

The second Stronghold row is an operational positional result, not a claim
that the Modoc force was captured or that the whole war ended.  The first
Stronghold and Thomas--Wright rows are engagements.  No generic ``Modoc``,
``United States``, militia, scout, or tribal alias is installed, and all three
promoted coordinates are locally quarantined pending a dedicated battlefield
location audit.
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


__all__ = (
    "WAVE8_MODOC_ADJACENT_LITERAL_LABEL_INVENTORY",
    "WAVE8_MODOC_CONTRACT_IDS",
    "WAVE8_MODOC_CONTRACTS",
    "WAVE8_MODOC_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_MODOC_CROSS_EVENT_BOUNDARIES",
    "WAVE8_MODOC_ENTITIES",
    "WAVE8_MODOC_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_MODOC_EXCLUSION_IDS",
    "WAVE8_MODOC_EXCLUSIONS",
    "WAVE8_MODOC_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_MODOC_EXPECTED_CANDIDATE_IDS",
    "WAVE8_MODOC_FINAL_AUDIT_SIGNATURE",
    "WAVE8_MODOC_FUNNEL_AUDIT",
    "WAVE8_MODOC_HOLD_IDS",
    "WAVE8_MODOC_HOLDS",
    "WAVE8_MODOC_INTEGRATION_DISPOSITIONS",
    "WAVE8_MODOC_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_MODOC_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_MODOC_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_MODOC_LOCATION_QUARANTINE_REASONS",
    "WAVE8_MODOC_NONPROMOTIONS",
    "WAVE8_MODOC_OPERATION_CONTRACT_IDS",
    "WAVE8_MODOC_OUTCOME_OVERRIDES",
    "WAVE8_MODOC_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_MODOC_RESERVED_IDS",
    "WAVE8_MODOC_ROW_DISPOSITIONS",
    "WAVE8_MODOC_ROW_HASHES",
    "WAVE8_MODOC_SCOPE_AND_OPPOSITE_RESULT_AUDIT",
    "WAVE8_MODOC_SOURCES",
    "WAVE8_MODOC_TERMINAL_EXCLUSION_IDS",
    "WAVE8_MODOC_TERMINAL_EXCLUSIONS",
    "WAVE8_MODOC_TOUCHED_CANDIDATE_IDS",
    "WAVE8_MODOC_WAR_INVENTORY_IDS",
    "install_wave8_modoc_entities",
    "install_wave8_modoc_sources",
    "promote_wave8_modoc_contracts",
    "validate_wave8_modoc_funnel",
    "validate_wave8_modoc_integration_dispositions",
    "validate_wave8_modoc_queue_contracts",
    "wave8_modoc_audit_signature",
    "wave8_modoc_cohort_counts",
    "wave8_modoc_counts",
    "wave8_modoc_location_quarantine_additions",
    "wave8_modoc_metadata",
    "wave8_modoc_row_dispositions",
)


_LANE_NAME = "Wave 8 exact Modoc Indians event-bounded formation audit"
_MODULE_OWNER = "military_elo.promotion.wave8_modoc"
_EVENT_ID_PREFIX = "hced_wave8_modoc_"
_EXACT_LABEL = "modoc indians"
_WAR_LABEL = "modoc indian war"

_FIRST_MODOC_ID = "kintpuash_modoc_stronghold_defenders_1873_01_17"
_FIRST_US_ID = "wheaton_joint_stronghold_assault_force_1873_01_17"
_SECOND_US_ID = "gillem_joint_stronghold_operation_1873_04_15_17"
_SECOND_MODOC_ID = "kintpuash_modoc_stronghold_defenders_1873_04_15_17"
_SCHONCHIN_MODOC_ID = "scarfaced_charley_modoc_ambush_party_1873_04_26"
_SCHONCHIN_US_ID = "thomas_wright_us_reconnaissance_patrol_1873_04_26"


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


WAVE8_MODOC_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_modoc_nps_modoc_war",
        "Modoc War: War in the Lava Beds",
        "https://www.nps.gov/labe/learn/historyculture/modoc-war.htm",
        "U.S. National Park Service, Lava Beds National Monument",
        "official_public_history",
        "nps_lava_beds_modoc_war_interpretation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_modoc_thompson_history",
        "Modoc War: Its Military History and Topography",
        "https://npshistory.com/publications/labe/thompson/index.htm",
        "National Park Service historical study / NPS History archive",
        "official_scholarly_military_history",
        "thompson_modoc_war_1971",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_modoc_army_cmh",
        "Indian Wars: Modocs, 1872-1873",
        (
            "https://history.army.mil/Research/Reference-Topics/"
            "Army-Campaigns/Brief-Summaries/Indian-Wars/"
        ),
        "U.S. Army Center of Military History",
        "official_military_history",
        "us_army_cmh_indian_wars_modocs",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_modoc_oregon_encyclopedia",
        "Modoc War",
        "https://www.oregonencyclopedia.org/articles/modoc_war/",
        "The Oregon Encyclopedia / Oregon Historical Society",
        "scholarly_state_encyclopedia",
        "mark_oregon_encyclopedia_modoc_war",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_modoc_nation_history",
        "Modoc Nation History",
        "https://modocnation.com/modoc-nation-history/",
        "Modoc Nation",
        "official_tribal_history",
        "modoc_nation_official_history",
    ),
    _source(
        "wave8_modoc_california_geology",
        "Captain Jack's Stronghold",
        (
            "https://npshistory.com/publications/geology/state/ca/"
            "cg-v45n5-1992-1.pdf"
        ),
        "California Department of Conservation, California Geology",
        "technical_historical_terrain_article",
        "wagner_captain_jacks_stronghold_1992",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_modoc_nrhp_stronghold",
        "Captain Jack's Stronghold National Register nomination",
        "https://npshistory.com/publications/labe/nr-stronghold.pdf",
        "National Register of Historic Places / National Park Service",
        "official_heritage_nomination",
        "nrhp_captain_jacks_stronghold_nomination",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_modoc_nps_thomas_wright",
        "Thomas-Wright Battlefield, Tulelake, California",
        "https://www.nps.gov/places/thomas-wright-battlefield-tulelake-ca.htm",
        "U.S. National Park Service, Lava Beds National Monument",
        "official_battlefield_interpretation",
        "nps_thomas_wright_battlefield_interpretation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_modoc_nahc_timeline",
        "Timeline of Genocide Incidents in the Northeast California Region",
        "https://nahc.ca.gov/cp/timelines/northeast/",
        "California Native American Heritage Commission",
        "official_evidence_timeline",
        "california_nahc_northeast_timeline",
    ),
    _source(
        "wave8_modoc_murray_ou_press",
        "The Modocs and Their War",
        "https://www.oupress.com/9780806113319/the-modocs-and-their-war/",
        "University of Oklahoma Press",
        "scholarly_monograph",
        "murray_modocs_and_their_war",
        crosscheck=True,
    ),
)


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
        "start_year": 1873,
        "end_year": 1873,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " The mechanical year window exists only because entity records use "
            "year precision; the prose date is the actual boundary. No rating is "
            "inherited from or passed to the Modoc people or Modoc Nation, the "
            "United States, state volunteers, Klamath or Warm Springs peoples, "
            "another Modoc War force, or any later formation."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_MODOC_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _FIRST_MODOC_ID,
        "Kintpuash's Modoc Stronghold defenders (17 January 1873)",
        "event_bounded_indigenous_defense_force",
        "Captain Jack's Stronghold, Lava Beds",
        (
            "Bounded to the Modoc warriors under Kintpuash who defended the "
            "Stronghold during the first coordinated assault on 17 January 1873."
        ),
        [
            "wave8_modoc_california_geology",
            "wave8_modoc_nation_history",
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_thompson_history",
        ],
    ),
    _entity(
        _FIRST_US_ID,
        "Wheaton's joint Stronghold assault force (17 January 1873)",
        "event_bounded_joint_assault_force",
        "Captain Jack's Stronghold approaches, Lava Beds",
        (
            "Bounded to Wheaton and Green's regular Army, Oregon and California "
            "volunteer, and Klamath-scout components committed to the 17 January "
            "assault; it is not a generic U.S. or state-militia identity."
        ),
        [
            "wave8_modoc_army_cmh",
            "wave8_modoc_california_geology",
            "wave8_modoc_thompson_history",
        ],
    ),
    _entity(
        _SECOND_US_ID,
        "Gillem's joint Stronghold operation force (15-17 April 1873)",
        "event_bounded_joint_operational_force",
        "Captain Jack's Stronghold and approaches, Lava Beds",
        (
            "Bounded to Gillem, Green, and Mason's regular Army components and "
            "Warm Springs scouts in the 15-17 April operation; it ends when the "
            "deserted Stronghold is occupied."
        ),
        [
            "wave8_modoc_california_geology",
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_thompson_history",
        ],
    ),
    _entity(
        _SECOND_MODOC_ID,
        "Kintpuash's Modoc Stronghold defenders (15-17 April 1873)",
        "event_bounded_indigenous_defense_force",
        "Captain Jack's Stronghold and southern escape route, Lava Beds",
        (
            "Bounded to the Modoc defenders resisting the second assault and "
            "evacuating through the southern lava trenches on 15-17 April; the "
            "successful escape is retained without converting position loss into "
            "capture or whole-war defeat."
        ),
        [
            "wave8_modoc_nation_history",
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_nrhp_stronghold",
            "wave8_modoc_thompson_history",
        ],
    ),
    _entity(
        _SCHONCHIN_MODOC_ID,
        "Scarfaced Charley's Modoc ambush party (26 April 1873)",
        "event_bounded_indigenous_ambush_force",
        "Schonchin Flow and Hardin Butte approaches, Lava Beds",
        (
            "Bounded to Scarfaced Charley's small party during the Thomas-Wright "
            "ambush on 26 April, after the Stronghold evacuation and before the "
            "later Dry Lake action."
        ),
        [
            "wave8_modoc_nation_history",
            "wave8_modoc_nps_thomas_wright",
            "wave8_modoc_oregon_encyclopedia",
            "wave8_modoc_thompson_history",
        ],
    ),
    _entity(
        _SCHONCHIN_US_ID,
        "Thomas-Wright U.S. reconnaissance patrol (26 April 1873)",
        "event_bounded_reconnaissance_patrol",
        "Schonchin Flow and Hardin Butte approaches, Lava Beds",
        (
            "Bounded to Captain Evan Thomas and Lieutenant Thomas Wright's Army "
            "reconnaissance patrol in the 26 April ambush. The twelve Warm Springs "
            "scouts trying to approach did not become a rated combatant formation "
            "in this contract."
        ),
        [
            "wave8_modoc_nps_thomas_wright",
            "wave8_modoc_oregon_encyclopedia",
            "wave8_modoc_thompson_history",
        ],
    ),
)


WAVE8_MODOC_ROW_HASHES: dict[str, str] = {
    "hced-Lava Beds (1st)1873-1": (
        "2114d7ae883f25611e15469f787b31fb65448b3f43528e533e98e77eed418362"
    ),
    "hced-Lava Beds (2nd)1873-1": (
        "47d8dc6cb8d1fe5c59bf0fd8867a9abd2e02d738f56ddac206be4c34733aca80"
    ),
    "hced-Lost River, California1872-1": (
        "3cd4ed9cedaef60433d726dd2a308942c829a14b4b2f61cd5d1fca30ef542739"
    ),
    "hced-Schonchin Flow1873-1": (
        "10d95645d894fc4dcc62b9c3e19c639df5863f8e5e4ce023ae016cbdbaf0a49a"
    ),
}

WAVE8_MODOC_EXACT_CANDIDATE_ID_SHA256 = (
    "c1c5d7e80c707e5d8964e5f77ad6073af54215dddefda04e5ebd9bda5fce4309"
)

WAVE8_MODOC_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "centuries": {"CE_19": 4},
    "components_bridged": 0,
    "components_touched": 1,
    "event_candidate_id_sha256": WAVE8_MODOC_EXACT_CANDIDATE_ID_SHA256,
    "events_touched": 4,
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 4,
    },
    "label": _EXACT_LABEL,
    "rated_counterpart_entities": 1,
    "sole_blocker_events": 4,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 4,
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str,
    granularity: str,
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


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_MODOC_SOURCES
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    event_type: str,
    reviewed_outcome: str,
    reviewed_sides: Iterable[str],
    winner_side: int,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "audit_note": audit_note,
        "canonical_event": canonical_event,
        "cohort": cohort,
        "confidence": confidence,
        "disposition": "promote",
        "event_type": event_type,
        "evidence_refs": evidence,
        "outcome_reversal": False,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "outcome_source_ids": outcomes,
        "raw_row_sha256": WAVE8_MODOC_ROW_HASHES[candidate_id],
        "result_type": "win",
        "reviewed_outcome": reviewed_outcome,
        "reviewed_sides": list(map(str, reviewed_sides)),
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "source_outcome_override": False,
        "war_type": "colonial_anti_colonial",
        "winner_side": winner_side,
    }


WAVE8_MODOC_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Lava Beds (1st)1873-1": _contract(
        "hced-Lava Beds (1st)1873-1",
        _canonical(
            "First Battle for Captain Jack's Stronghold",
            1873,
            "17 January 1873",
            date_precision="day",
            granularity="single_day_coordinated_stronghold_assault",
        ),
        "first_stronghold_assault_1873_01_17",
        [_FIRST_MODOC_ID],
        [_FIRST_US_ID],
        [
            "wave8_modoc_army_cmh",
            "wave8_modoc_california_geology",
            "wave8_modoc_nation_history",
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_nrhp_stronghold",
            "wave8_modoc_thompson_history",
        ],
        [
            "wave8_modoc_army_cmh",
            "wave8_modoc_california_geology",
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_nrhp_stronghold",
            "wave8_modoc_thompson_history",
        ],
        (
            "The contract rates the 17 January two-pronged assault only. The "
            "attackers failed to penetrate the Stronghold and withdrew after "
            "heavy casualties; the Modoc defenders retained the position without "
            "a combat death. It does not extend that defensive victory to the "
            "April assault or to the whole war."
        ),
        confidence=0.98,
        event_type="engagement",
        reviewed_outcome="Modoc defensive victory; first assault repulsed",
        reviewed_sides=[
            "Kintpuash's Modoc Stronghold defenders on 17 January",
            "Wheaton's joint regular-volunteer-scout assault force",
        ],
        winner_side=1,
    ),
    "hced-Lava Beds (2nd)1873-1": _contract(
        "hced-Lava Beds (2nd)1873-1",
        _canonical(
            "Second Battle for Captain Jack's Stronghold",
            1873,
            "15-17 April 1873",
            date_precision="day_range",
            granularity="three_day_stronghold_assault_and_position_capture",
        ),
        "second_stronghold_operation_1873_04_15_17",
        [_SECOND_US_ID],
        [_SECOND_MODOC_ID],
        [
            "wave8_modoc_california_geology",
            "wave8_modoc_nation_history",
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_nrhp_stronghold",
            "wave8_modoc_thompson_history",
        ],
        [
            "wave8_modoc_california_geology",
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_nrhp_stronghold",
            "wave8_modoc_thompson_history",
        ],
        (
            "The bounded objective is the fortified position: Gillem's forces "
            "advanced for three days, cut the defenders from Tule Lake, and "
            "occupied the Stronghold on 17 April. The Modoc force successfully "
            "evacuated south during the night. This is therefore a reduced-"
            "confidence U.S. positional operation victory, not destruction or "
            "capture of the defenders and not the end of the Modoc War."
        ),
        confidence=0.84,
        event_type="campaign",
        reviewed_outcome=(
            "United States positional operation victory; Stronghold occupied "
            "after Modoc evacuation"
        ),
        reviewed_sides=[
            "Gillem-Green-Mason joint Stronghold operation force",
            "Kintpuash's Modoc Stronghold defenders and evacuation force",
        ],
        winner_side=1,
    ),
    "hced-Schonchin Flow1873-1": _contract(
        "hced-Schonchin Flow1873-1",
        _canonical(
            "Thomas-Wright Battle at Schonchin Flow",
            1873,
            "26 April 1873",
            date_precision="day",
            granularity="reconnaissance_patrol_ambush",
        ),
        "thomas_wright_ambush_1873_04_26",
        [_SCHONCHIN_MODOC_ID],
        [_SCHONCHIN_US_ID],
        [
            "wave8_modoc_nation_history",
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_nps_thomas_wright",
            "wave8_modoc_oregon_encyclopedia",
            "wave8_modoc_thompson_history",
        ],
        [
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_nps_thomas_wright",
            "wave8_modoc_oregon_encyclopedia",
            "wave8_modoc_thompson_history",
        ],
        (
            "This contract rates Scarfaced Charley's 26 April ambush of the "
            "Thomas-Wright reconnaissance patrol. Roughly two-thirds of the "
            "patrol was killed or wounded before the surviving soldiers fled; "
            "the attacking party then ceased fire. It is distinct from both the "
            "Stronghold occupation and the later U.S. victory at Dry Lake."
        ),
        confidence=0.98,
        event_type="engagement",
        reviewed_outcome="Modoc tactical victory; reconnaissance patrol destroyed",
        reviewed_sides=[
            "Scarfaced Charley's Modoc Schonchin Flow ambush party",
            "Thomas-Wright U.S. Army reconnaissance patrol",
        ],
        winner_side=1,
    ),
}


WAVE8_MODOC_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Lost River, California1872-1": {
        "audit_note": (
            "The encounter combined a failed disarmament/arrest operation, an "
            "Army occupation and burning of Kintpuash's village, a separate "
            "civilian fight across the river, and the Modoc bands' successful "
            "escape to the Lava Beds. Authoritative accounts agree on those facts "
            "but do not establish one shared result scope. HCED's winner field "
            "says Draw while winner_loser_complete is false. No true draw, U.S. "
            "victory, or Modoc victory is asserted."
        ),
        "canonical_event": _canonical(
            "Battle of Lost River",
            1872,
            "29 November 1872",
            date_precision="day",
            granularity="multi_site_disarmament_and_village_fight",
        ),
        "disposition": "hold",
        "evidence_refs": [
            "wave8_modoc_army_cmh",
            "wave8_modoc_murray_ou_press",
            "wave8_modoc_nation_history",
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_oregon_encyclopedia",
            "wave8_modoc_thompson_history",
        ],
        "hold_reason": "scope_dependent_mixed_result_not_a_defensible_draw",
        "raw_row_sha256": WAVE8_MODOC_ROW_HASHES[
            "hced-Lost River, California1872-1"
        ],
        "reviewed_outcome": "unknown_at_locked_event_scope",
        "source_winner_raw": "Draw",
        "source_winner_loser_complete": False,
        "unknown_is_never_draw": True,
    }
}

WAVE8_MODOC_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_MODOC_EXCLUSIONS = WAVE8_MODOC_TERMINAL_EXCLUSIONS
WAVE8_MODOC_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_MODOC_HOLDS,
    **WAVE8_MODOC_TERMINAL_EXCLUSIONS,
}
WAVE8_MODOC_CONTRACT_IDS = frozenset(WAVE8_MODOC_CONTRACTS)
WAVE8_MODOC_HOLD_IDS = frozenset(WAVE8_MODOC_HOLDS)
WAVE8_MODOC_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_MODOC_TERMINAL_EXCLUSIONS
)
WAVE8_MODOC_EXCLUSION_IDS = WAVE8_MODOC_TERMINAL_EXCLUSION_IDS
WAVE8_MODOC_RESERVED_IDS = frozenset(
    WAVE8_MODOC_CONTRACT_IDS
    | WAVE8_MODOC_HOLD_IDS
    | WAVE8_MODOC_TERMINAL_EXCLUSION_IDS
)
WAVE8_MODOC_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_MODOC_ROW_HASHES)
WAVE8_MODOC_TOUCHED_CANDIDATE_IDS = WAVE8_MODOC_RESERVED_IDS
WAVE8_MODOC_WAR_INVENTORY_IDS = WAVE8_MODOC_EXPECTED_CANDIDATE_IDS
WAVE8_MODOC_OPERATION_CONTRACT_IDS = frozenset(
    candidate_id
    for candidate_id, contract in WAVE8_MODOC_CONTRACTS.items()
    if contract["event_type"] == "campaign"
)
WAVE8_MODOC_ROW_DISPOSITIONS = {
    **{candidate_id: "promote" for candidate_id in WAVE8_MODOC_CONTRACT_IDS},
    **{candidate_id: "hold" for candidate_id in WAVE8_MODOC_HOLD_IDS},
}


# All queue labels containing the token ``modoc`` are pinned.  The empty
# alternates are deliberate negative boundaries: they may not silently enter
# this exact-label lane if a future staging snapshot adds them.
WAVE8_MODOC_ADJACENT_LITERAL_LABEL_INVENTORY: dict[str, tuple[str, ...]] = {
    "captain jack s band": (),
    "modoc": (),
    "modoc indian": (),
    "modoc indians": tuple(sorted(WAVE8_MODOC_EXPECTED_CANDIDATE_IDS)),
    "modoc nation": (),
    "modocs": (),
}


WAVE8_MODOC_SCOPE_AND_OPPOSITE_RESULT_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Lost River, California1872-1": {
        "aliases": ["Battle of Lost River", "Lost River, California"],
        "audited_unit": "multi_site_disarmament_and_village_fight",
        "disposition": "hold_unknown_not_draw",
        "opposite_result_disposition": (
            "Village occupation and band escape answer different objectives; "
            "neither is converted into a win or a draw for this locked row."
        ),
        "owner_module": _MODULE_OWNER,
        "scope_note": "Opening Lost River action only; no later Lava Beds result.",
    },
    "hced-Lava Beds (1st)1873-1": {
        "aliases": [
            "First Battle for Captain Jack's Stronghold",
            "First Battle of the Stronghold",
            "Lava Beds (1st)",
        ],
        "audited_unit": "single_day_coordinated_stronghold_assault",
        "disposition": "promote_modoc_defensive_victory",
        "opposite_result_disposition": (
            "The U.S. result in the April second assault is a distinct operation, "
            "not an opposite-result duplicate of the January defeat."
        ),
        "owner_module": _MODULE_OWNER,
        "scope_note": "Only the 17 January assault and withdrawal are rated.",
    },
    "hced-Lava Beds (2nd)1873-1": {
        "aliases": [
            "Lava Beds (2nd)",
            "Second Battle for Captain Jack's Stronghold",
            "Second Battle of the Stronghold",
        ],
        "audited_unit": "three_day_stronghold_assault_and_position_capture",
        "disposition": "promote_us_positional_operation_victory",
        "opposite_result_disposition": (
            "The Modoc escape is preserved as a qualification, not promoted as "
            "an opposite result or erased by a claim of capture."
        ),
        "owner_module": _MODULE_OWNER,
        "scope_note": "The operation ends with occupation on 17 April.",
    },
    "hced-Schonchin Flow1873-1": {
        "aliases": [
            "Battle of Sand Butte",
            "Schonchin Flow",
            "Thomas-Wright Battle",
        ],
        "audited_unit": "reconnaissance_patrol_ambush",
        "disposition": "promote_modoc_tactical_victory",
        "opposite_result_disposition": (
            "The U.S. victory at Dry Lake on 10 May is a later engagement and "
            "not an opposite-result twin of the Thomas-Wright patrol disaster."
        ),
        "owner_module": _MODULE_OWNER,
        "scope_note": "Only the 26 April Thomas-Wright patrol is rated.",
    },
}


WAVE8_MODOC_CROSS_EVENT_BOUNDARIES: dict[str, dict[str, Any]] = {
    "lost_river_to_first_stronghold": {
        "candidate_ids": [
            "hced-Lost River, California1872-1",
            "hced-Lava Beds (1st)1873-1",
        ],
        "disposition": "distinct_opening_action_and_later_fortress_assault",
        "reason": (
            "Lost River occurred on 29 November 1872 at two village sites; the "
            "first Stronghold assault occurred seven weeks later at a new position."
        ),
    },
    "first_to_second_stronghold": {
        "candidate_ids": [
            "hced-Lava Beds (1st)1873-1",
            "hced-Lava Beds (2nd)1873-1",
        ],
        "disposition": "same_position_distinct_assaults_and_results",
        "reason": (
            "The January attack was repulsed; the separately organized 15-17 "
            "April operation occupied the evacuated Stronghold."
        ),
    },
    "second_stronghold_to_schonchin": {
        "candidate_ids": [
            "hced-Lava Beds (2nd)1873-1",
            "hced-Schonchin Flow1873-1",
        ],
        "disposition": "distinct_position_operation_and_patrol_ambush",
        "reason": (
            "The Thomas-Wright patrol left camp nine days after the Stronghold "
            "occupation and was ambushed by a different bounded Modoc party."
        ),
    },
}

WAVE8_MODOC_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    f"event_boundary:{key}": value
    for key, value in WAVE8_MODOC_CROSS_EVENT_BOUNDARIES.items()
}

WAVE8_MODOC_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_MODOC_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_MODOC_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


def _duplicate_audit(low: int, high: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": tuple(sorted(set(map(normalize_label, aliases)))),
        "years": (low, high),
    }


WAVE8_MODOC_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Lost River, California1872-1": _duplicate_audit(
        1872,
        1872,
        "Battle of Lost River",
        "Lost River",
        "Lost River, California",
    ),
    "hced-Lava Beds (1st)1873-1": _duplicate_audit(
        1873,
        1873,
        "Captain Jack's Stronghold",
        "First Battle for Captain Jack's Stronghold",
        "First Battle of the Stronghold",
        "Lava Beds (1st)",
    ),
    "hced-Lava Beds (2nd)1873-1": _duplicate_audit(
        1873,
        1873,
        "Captain Jack's Stronghold",
        "Lava Beds (2nd)",
        "Second Battle for Captain Jack's Stronghold",
        "Second Battle of the Stronghold",
    ),
    "hced-Schonchin Flow1873-1": _duplicate_audit(
        1873,
        1873,
        "Battle of Sand Butte",
        "Hardin Butte",
        "Schonchin Flow",
        "Thomas Wright Battlefield",
        "Thomas-Wright Battle",
    ),
}


WAVE8_MODOC_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Lava Beds (1st)1873-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_modoc_california_geology",
            "wave8_modoc_nahc_timeline",
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_thompson_history",
        ],
        "raw_point": [-121.5091537, 41.7749372],
        "retained_country": "United States",
        "reason": (
            "The attack crossed separate eastern and western approaches through "
            "the Stronghold lava terrain; the shared HCED point is not an "
            "authenticated clash coordinate for that dispersed line."
        ),
    },
    "hced-Lava Beds (2nd)1873-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_modoc_california_geology",
            "wave8_modoc_nahc_timeline",
            "wave8_modoc_nps_modoc_war",
            "wave8_modoc_nrhp_stronghold",
            "wave8_modoc_thompson_history",
        ],
        "raw_point": [-121.5091537, 41.7749372],
        "retained_country": "United States",
        "reason": (
            "The three-day operation spanned two assault fronts, artillery "
            "positions, the Stronghold perimeter, and a southern evacuation route; "
            "one point would falsely collapse the operation."
        ),
    },
    "hced-Schonchin Flow1873-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_modoc_california_geology",
            "wave8_modoc_nahc_timeline",
            "wave8_modoc_nps_thomas_wright",
            "wave8_modoc_oregon_encyclopedia",
            "wave8_modoc_thompson_history",
        ],
        "raw_point": [-121.5291498, 41.7382018],
        "retained_country": "United States",
        "reason": (
            "The source name refers to the lava flow, while the patrol halted in "
            "the basin by Hardin Butte and fire came from multiple ridges; the raw "
            "point is not retained as an exact ambush location."
        ),
    },
}
WAVE8_MODOC_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_MODOC_LOCATION_QUARANTINE_REASONS
)
WAVE8_MODOC_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_MODOC_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_MODOC_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_MODOC_COUNTRY_QUARANTINE_ADDITIONS,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(map(str, values))))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_literal_label_inventory": {
            label: list(candidate_ids)
            for label, candidate_ids in (
                WAVE8_MODOC_ADJACENT_LITERAL_LABEL_INVENTORY.items()
            )
        },
        "contracts": WAVE8_MODOC_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_MODOC_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_event_boundaries": WAVE8_MODOC_CROSS_EVENT_BOUNDARIES,
        "entities": WAVE8_MODOC_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_MODOC_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_MODOC_EXPECTED_CANDIDATE_IDS),
        "funnel_audit": WAVE8_MODOC_FUNNEL_AUDIT,
        "holds": WAVE8_MODOC_HOLDS,
        "integration_dispositions": WAVE8_MODOC_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_MODOC_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_MODOC_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_MODOC_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_MODOC_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_MODOC_POINT_QUARANTINE_ADDITIONS
        ),
        "row_dispositions": WAVE8_MODOC_ROW_DISPOSITIONS,
        "scope_and_opposite_result_audit": (
            WAVE8_MODOC_SCOPE_AND_OPPOSITE_RESULT_AUDIT
        ),
        "sources": WAVE8_MODOC_SOURCES,
        "terminal_exclusions": WAVE8_MODOC_TERMINAL_EXCLUSIONS,
    }


def wave8_modoc_audit_signature() -> str:
    """Return the deterministic digest of the complete Modoc adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_MODOC_FINAL_AUDIT_SIGNATURE = (
    "cbd881130cfb28e9ff147dd2da71b3751ad7fa833996f40b54a75f9963040e71"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_MODOC_CONTRACTS),
        len(WAVE8_MODOC_HOLDS),
        len(WAVE8_MODOC_TERMINAL_EXCLUSIONS),
    ) != (3, 1, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_MODOC_ENTITIES), len(WAVE8_MODOC_SOURCES)) != (6, 10):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_MODOC_RESERVED_IDS != WAVE8_MODOC_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if set(WAVE8_MODOC_ROW_DISPOSITIONS) != WAVE8_MODOC_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} row disposition inventory changed")
    if set(WAVE8_MODOC_ROW_DISPOSITIONS.values()) != {"hold", "promote"}:
        raise ValueError(f"{_LANE_NAME} row dispositions changed")
    if _sorted_newline_sha256(WAVE8_MODOC_EXPECTED_CANDIDATE_IDS) != (
        WAVE8_MODOC_EXACT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} exact-candidate digest changed")
    if (
        WAVE8_MODOC_FINAL_AUDIT_SIGNATURE != "__PENDING__"
        and wave8_modoc_audit_signature() != WAVE8_MODOC_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    disposition_sets = (
        WAVE8_MODOC_CONTRACT_IDS,
        WAVE8_MODOC_HOLD_IDS,
        WAVE8_MODOC_TERMINAL_EXCLUSION_IDS,
    )
    for index, left in enumerate(disposition_sets):
        for right in disposition_sets[index + 1 :]:
            if left & right:
                raise ValueError(f"{_LANE_NAME} dispositions overlap")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_MODOC_SOURCES
    }
    if len(source_by_id) != len(WAVE8_MODOC_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(
        {str(source["source_family_id"]) for source in WAVE8_MODOC_SOURCES}
    ) != len(WAVE8_MODOC_SOURCES):
        raise ValueError(f"{_LANE_NAME} source families are not unique")
    for source in WAVE8_MODOC_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if "wikipedia.org" in str(source["url"]):
            raise ValueError(f"{_LANE_NAME} uses a non-authoritative source")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_MODOC_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_MODOC_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_entity_ids = {
        "modoc",
        "modoc_indians",
        "modoc_nation",
        "united_states",
        "united_states_of_america",
        "us_united_states_of_america_reconstruction",
    }
    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for entity in WAVE8_MODOC_ENTITIES:
        entity_id = str(entity["id"])
        if entity_id in forbidden_entity_ids or entity["aliases"]:
            raise ValueError(f"{_LANE_NAME} installed a generic actor or alias")
        if (int(entity["start_year"]), int(entity["end_year"])) != (1873, 1873):
            raise ValueError(f"{_LANE_NAME} entity is not event-bounded")
        note = normalize_label(entity["continuity_note"])
        if "no rating is inherited" not in note:
            raise ValueError(f"{_LANE_NAME} continuity firewall changed")
        source_ids = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(source_ids) or not set(source_ids) <= set(
            source_by_id
        ):
            raise ValueError(f"{_LANE_NAME} entity sources changed")
        used_sources.update(source_ids)

    expected_sides = {
        "hced-Lava Beds (1st)1873-1": (
            {_FIRST_MODOC_ID},
            {_FIRST_US_ID},
            "engagement",
        ),
        "hced-Lava Beds (2nd)1873-1": (
            {_SECOND_US_ID},
            {_SECOND_MODOC_ID},
            "campaign",
        ),
        "hced-Schonchin Flow1873-1": (
            {_SCHONCHIN_MODOC_ID},
            {_SCHONCHIN_US_ID},
            "engagement",
        ),
    }
    for candidate_id, contract in WAVE8_MODOC_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_MODOC_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract row hash changed")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} canonical event key changed")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        expected_1, expected_2, event_type = expected_sides[candidate_id]
        if (side_1, side_2, contract["event_type"]) != (
            expected_1,
            expected_2,
            event_type,
        ):
            raise ValueError(f"{_LANE_NAME} event composition changed")
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} opposing sides changed")
        if not (side_1 | side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} contract uses an unknown entity")
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or int(contract["winner_side"]) != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or not set(evidence) <= set(source_by_id)
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome evidence changed")
        expected_families = sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        )
        if families != expected_families or len(families) < 3:
            raise ValueError(f"{_LANE_NAME} lacks independent outcome evidence")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        if not contract["reviewed_sides"] or not contract["reviewed_outcome"]:
            raise ValueError(f"{_LANE_NAME} participant audit changed")
        used_entities.update(side_1 | side_2)
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")

    hold = WAVE8_MODOC_HOLDS["hced-Lost River, California1872-1"]
    forbidden_hold_fields = {
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
    }
    if (
        hold["raw_row_sha256"]
        != WAVE8_MODOC_ROW_HASHES["hced-Lost River, California1872-1"]
        or hold["disposition"] != "hold"
        or hold["reviewed_outcome"] != "unknown_at_locked_event_scope"
        or hold["source_winner_raw"] != "Draw"
        or hold["source_winner_loser_complete"] is not False
        or hold["unknown_is_never_draw"] is not True
        or forbidden_hold_fields & set(hold)
    ):
        raise ValueError(f"{_LANE_NAME} Lost River hold changed")
    hold_evidence = list(map(str, hold["evidence_refs"]))
    if not _is_sorted_unique(hold_evidence) or not set(hold_evidence) <= set(
        source_by_id
    ):
        raise ValueError(f"{_LANE_NAME} hold evidence changed")
    used_sources.update(hold_evidence)

    if set(WAVE8_MODOC_SCOPE_AND_OPPOSITE_RESULT_AUDIT) != (
        WAVE8_MODOC_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} scope audit is incomplete")
    for candidate_id, audit in WAVE8_MODOC_SCOPE_AND_OPPOSITE_RESULT_AUDIT.items():
        if audit["owner_module"] != _MODULE_OWNER:
            raise ValueError(f"{_LANE_NAME} ownership audit changed")
        expected_granularity = (
            WAVE8_MODOC_CONTRACTS.get(candidate_id)
            or WAVE8_MODOC_HOLDS[candidate_id]
        )["canonical_event"]["granularity"]
        if audit["audited_unit"] != expected_granularity:
            raise ValueError(f"{_LANE_NAME} event scope changed")
        if not audit["opposite_result_disposition"] or not audit["scope_note"]:
            raise ValueError(f"{_LANE_NAME} opposite-result audit changed")

    if set(WAVE8_MODOC_CROSS_EVENT_BOUNDARIES) != {
        "first_to_second_stronghold",
        "lost_river_to_first_stronghold",
        "second_stronghold_to_schonchin",
    }:
        raise ValueError(f"{_LANE_NAME} cross-event boundaries changed")
    for item in WAVE8_MODOC_CROSS_EVENT_BOUNDARIES.values():
        candidate_ids = list(map(str, item["candidate_ids"]))
        if len(candidate_ids) != 2 or not set(candidate_ids) <= (
            WAVE8_MODOC_RESERVED_IDS
        ):
            raise ValueError(f"{_LANE_NAME} cross-event ownership changed")
    expected_integration = {
        f"event_boundary:{key}": value
        for key, value in WAVE8_MODOC_CROSS_EVENT_BOUNDARIES.items()
    }
    if WAVE8_MODOC_INTEGRATION_DISPOSITIONS != expected_integration:
        raise ValueError(f"{_LANE_NAME} integration dispositions changed")

    if set(WAVE8_MODOC_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_MODOC_CONTRACT_IDS
    ) or WAVE8_MODOC_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_MODOC_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine changed")
    if WAVE8_MODOC_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    for review in WAVE8_MODOC_LOCATION_QUARANTINE_REASONS.values():
        if (
            review["actions"] != ["withhold_point"]
            or review["retained_country"] != "United States"
        ):
            raise ValueError(f"{_LANE_NAME} location disposition changed")
        evidence = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(
            source_by_id
        ):
            raise ValueError(f"{_LANE_NAME} location evidence changed")
        used_sources.update(evidence)

    if set(WAVE8_MODOC_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_MODOC_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} IWBD negative audit is incomplete")
    for audit in WAVE8_MODOC_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, audit["aliases"]))
        low, high = map(int, audit["years"])
        if not _is_sorted_unique(aliases) or aliases != list(
            map(normalize_label, aliases)
        ):
            raise ValueError(f"{_LANE_NAME} alternate-name audit changed")
        if low > high:
            raise ValueError(f"{_LANE_NAME} duplicate interval changed")
    if (
        WAVE8_MODOC_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_MODOC_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_MODOC_OUTCOME_OVERRIDES
    ):
        raise ValueError(f"{_LANE_NAME} acquired an undeclared disposition")
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")


def _is_exact_label(value: Any) -> bool:
    return normalize_label(value) == _EXACT_LABEL


def validate_wave8_modoc_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin the complete exact label and Modoc-War queue inventory."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_MODOC_CONTRACTS,
        WAVE8_MODOC_HOLDS,
        lane_name=_LANE_NAME,
    )
    exact_ids: set[str] = set()
    war_ids: set[str] = set()
    token_labels: dict[str, set[str]] = {}
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id") or "")
        sides = [
            normalize_label(row.get("side_1_raw")),
            normalize_label(row.get("side_2_raw")),
        ]
        if any(label == _EXACT_LABEL for label in sides):
            exact_ids.add(candidate_id)
            if sum(label == _EXACT_LABEL for label in sides) != 1:
                raise ValueError(
                    f"{_LANE_NAME} exact-side ownership changed: {candidate_id}"
                )
        for label in sides:
            if "modoc" in label:
                token_labels.setdefault(label, set()).add(candidate_id)
        if any(
            normalize_label(war_name) == _WAR_LABEL
            for war_name in row.get("war_names", [])
        ):
            war_ids.add(candidate_id)
    if exact_ids != WAVE8_MODOC_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact-label inventory changed: {sorted(exact_ids)}"
        )
    if war_ids != WAVE8_MODOC_WAR_INVENTORY_IDS:
        raise ValueError(
            f"{_LANE_NAME} complete Modoc War inventory changed: {sorted(war_ids)}"
        )
    actual_inventory = {
        label: tuple(sorted(token_labels.get(label, set())))
        for label in WAVE8_MODOC_ADJACENT_LITERAL_LABEL_INVENTORY
    }
    unexpected_labels = set(token_labels) - set(
        WAVE8_MODOC_ADJACENT_LITERAL_LABEL_INVENTORY
    )
    if (
        actual_inventory != WAVE8_MODOC_ADJACENT_LITERAL_LABEL_INVENTORY
        or unexpected_labels
    ):
        raise ValueError(
            f"{_LANE_NAME} adjacent Modoc spelling inventory changed"
        )
    return {
        "holds": result["holds"],
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_MODOC_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_modoc_funnel(
    funnel: Mapping[str, Any],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin the unresolved funnel while accepting zero or full lane integration."""

    _validate_static()
    records = [
        record
        for record in funnel.get("labels", [])
        if normalize_label(record.get("label")) == _EXACT_LABEL
    ]
    if len(records) != 1 or records[0] != WAVE8_MODOC_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel record changed")
    overlap = {
        str(event.get("hced_candidate_id"))
        for event in existing_events
        if event.get("hced_candidate_id") in WAVE8_MODOC_CONTRACT_IDS
    }
    if overlap not in (set(), set(WAVE8_MODOC_CONTRACT_IDS)):
        raise ValueError(
            f"{_LANE_NAME} release overlap is partial: {sorted(overlap)}"
        )
    return {
        "events_touched": int(records[0]["events_touched"]),
        "release_lane_overlap": len(overlap),
        "sole_blocker_events": int(records[0]["sole_blocker_events"]),
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


def _probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    if year is None:
        return False
    name = normalize_label(row.get("name"))
    for audit in WAVE8_MODOC_IWBD_ZERO_OVERLAP_AUDIT.values():
        low, high = map(int, audit["years"])
        if low <= year <= high and name in audit["aliases"]:
            return True
    return False


def validate_wave8_modoc_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on duplicates, held-row leakage, and partial integration."""

    validate_wave8_modoc_queue_contracts(hced_rows)
    unexpected_iwbd = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _probable_twin(row)
    )
    if unexpected_iwbd:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): "
            f"{unexpected_iwbd}"
        )

    existing = list(existing_events)
    hold_leaks = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_MODOC_HOLD_IDS
    )
    if hold_leaks:
        raise ValueError(f"{_LANE_NAME} held Lost River row was rated: {hold_leaks}")

    overlap = {
        str(event.get("hced_candidate_id"))
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_MODOC_CONTRACT_IDS
    }
    if overlap not in (set(), set(WAVE8_MODOC_CONTRACT_IDS)):
        raise ValueError(
            f"{_LANE_NAME} release overlap is partial: {sorted(overlap)}"
        )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id") not in WAVE8_MODOC_CONTRACT_IDS
        and not str(event.get("id") or "").startswith(_EVENT_ID_PREFIX)
        and _probable_twin(event)
    )
    if release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable release duplicate(s): "
            f"{release_twins}"
        )
    return {
        "cross_event_boundaries": len(WAVE8_MODOC_CROSS_EVENT_BOUNDARIES),
        "existing_release_duplicate_dispositions": 0,
        "integration_dispositions": len(WAVE8_MODOC_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "release_lane_overlap": len(overlap),
        "release_probable_twins": 0,
    }


def install_wave8_modoc_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_MODOC_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_modoc_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_MODOC_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_event_review(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        contract = WAVE8_MODOC_CONTRACTS[candidate_id]
        if candidate_id in WAVE8_MODOC_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_MODOC_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)
        event_type = str(contract["event_type"])
        event["event_type"] = event_type
        if event_type == "campaign":
            event["summary"] = (
                "Candidate-keyed Wave 8 positional operation assertion. The "
                "complete HCED row, three-day objective, event-bounded formations, "
                "and independent outcome evidence are pinned. Occupation of the "
                "Stronghold is not converted into capture of the escaped Modoc "
                "force or the result of the whole war. "
                + str(contract["audit_note"])
            )
            operationalize_campaign_outcomes(event)
            for participant in event["participants"]:
                if participant["side"] == "side_a":
                    participant["termination"] = "campaign_victory"
                    participant["result_class"] = (
                        "operational_positional_victory"
                    )
                else:
                    participant["termination"] = "campaign_defeat"
                    participant["result_class"] = (
                        "operational_position_loss_with_force_escape"
                    )
                participant["note"] = (
                    f"Candidate-keyed {_LANE_NAME} positional-operation contract; "
                    "no force-capture or whole-war result is inferred."
                )


def promote_wave8_modoc_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit three bounded outcomes while leaving Lost River staged."""

    validate_wave8_modoc_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_MODOC_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_event_review(events)
    return events


def wave8_modoc_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_MODOC_CONTRACTS.values()
            ).items()
        )
    )


def wave8_modoc_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_literal_labels_audited": len(
            WAVE8_MODOC_ADJACENT_LITERAL_LABEL_INVENTORY
        ),
        "country_quarantine_additions": len(
            WAVE8_MODOC_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_event_boundaries": len(WAVE8_MODOC_CROSS_EVENT_BOUNDARIES),
        "engagement_events": len(WAVE8_MODOC_CONTRACT_IDS)
        - len(WAVE8_MODOC_OPERATION_CONTRACT_IDS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_MODOC_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_MODOC_HOLDS),
        "integration_dispositions": len(WAVE8_MODOC_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_MODOC_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_MODOC_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_MODOC_ENTITIES),
        "new_sources": len(WAVE8_MODOC_SOURCES),
        "newly_rated_events": len(WAVE8_MODOC_CONTRACTS),
        "operation_events": len(WAVE8_MODOC_OPERATION_CONTRACT_IDS),
        "outcome_overrides": len(WAVE8_MODOC_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_MODOC_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_MODOC_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_MODOC_EXPECTED_CANDIDATE_IDS),
        "scope_audits": len(WAVE8_MODOC_SCOPE_AND_OPPOSITE_RESULT_AUDIT),
        "sole_blocker_rows": int(WAVE8_MODOC_FUNNEL_AUDIT["sole_blocker_events"]),
        "terminal_exclusions": len(WAVE8_MODOC_TERMINAL_EXCLUSIONS),
        "touched_hced_rows": len(WAVE8_MODOC_TOUCHED_CANDIDATE_IDS),
    }


def wave8_modoc_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_MODOC_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_MODOC_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_modoc_row_dispositions() -> dict[str, str]:
    _validate_static()
    return dict(sorted(WAVE8_MODOC_ROW_DISPOSITIONS.items()))


def wave8_modoc_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "audit": "candidate_keyed_exact_label_event_bounded_formations",
        "counts": wave8_modoc_counts(),
        "cohorts": wave8_modoc_cohort_counts(),
        "final_audit_signature": WAVE8_MODOC_FINAL_AUDIT_SIGNATURE,
        "module_owner": _MODULE_OWNER,
        "row_dispositions": wave8_modoc_row_dispositions(),
    }
