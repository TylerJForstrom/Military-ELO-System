"""Exact Wave 8 dispositions for HCED rows labelled ``Nez Perce Indians``.

The raw label collapses a people, several non-treaty bands, attached Palouse
and Cayuse allies, a changing body of warriors, and the families travelling
with them.  This lane therefore creates no timeless ethnic identity.  It
rates the exact White Bird fighting force and the joined July-October 1877
campaign fighting formation only; noncombatants, treaty bands, descendants,
and modern tribal governments never receive or inherit a rating.

All five rows have independently defensible tactical dispositions.  Big Hole
and Clearwater reverse HCED's proposals with direct evidence: the nimíipuu
counterattack defeated Gibbon's infantry at Big Hole, while Howard's force
forced the Clearwater withdrawal and took the camp and supplies.  Neither a
contested strategic consequence nor an unknown result is converted to a draw.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_NEZ_PERCE_CONTRACT_IDS",
    "WAVE8_NEZ_PERCE_CONTRACTS",
    "WAVE8_NEZ_PERCE_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_NEZ_PERCE_CROSS_LANE_DISPOSITIONS",
    "WAVE8_NEZ_PERCE_ENTITIES",
    "WAVE8_NEZ_PERCE_EXCLUSION_IDS",
    "WAVE8_NEZ_PERCE_EXCLUSIONS",
    "WAVE8_NEZ_PERCE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_NEZ_PERCE_EXPECTED_CANDIDATE_IDS",
    "WAVE8_NEZ_PERCE_FINAL_AUDIT_SIGNATURE",
    "WAVE8_NEZ_PERCE_HOLD_IDS",
    "WAVE8_NEZ_PERCE_HOLDS",
    "WAVE8_NEZ_PERCE_INTEGRATION_DISPOSITIONS",
    "WAVE8_NEZ_PERCE_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_NEZ_PERCE_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_REASONS",
    "WAVE8_NEZ_PERCE_NONPROMOTIONS",
    "WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES",
    "WAVE8_NEZ_PERCE_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_NEZ_PERCE_RESERVED_IDS",
    "WAVE8_NEZ_PERCE_SOURCES",
    "WAVE8_NEZ_PERCE_TERMINAL_EXCLUSION_IDS",
    "WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS",
    "install_wave8_nez_perce_entities",
    "install_wave8_nez_perce_sources",
    "promote_wave8_nez_perce_contracts",
    "validate_wave8_nez_perce_integration_dispositions",
    "validate_wave8_nez_perce_queue_contracts",
    "wave8_nez_perce_audit_signature",
    "wave8_nez_perce_cohort_counts",
    "wave8_nez_perce_counts",
    "wave8_nez_perce_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Nez Perce exact-force audit"
_MODULE_OWNER = "wave8_nez_perce"
_EVENT_ID_PREFIX = "hced_wave8_nez_perce_"

_UNITED_STATES_ID = "united_states"
_WHITE_BIRD_FORCE_ID = "white_bird_non_treaty_nimiipuu_fighting_force_1877"
_CAMPAIGN_FORCE_ID = "non_treaty_nimiipuu_allied_campaign_force_1877"


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


WAVE8_NEZ_PERCE_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_nez_perce_nps_white_bird",
        "Visit White Bird Battlefield",
        "https://www.nps.gov/nepe/planyourvisit/visit-white-bird-battlefield.htm",
        "U.S. National Park Service, Nez Perce National Historical Park",
        "federal_battlefield_history_and_location_reference",
        "nps_nez_perce_battlefield_interpretation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_nez_perce_army_white_bird",
        (
            "Staff Ride Handbook and Atlas for the Battle of White Bird Canyon, "
            "17 June 1877"
        ),
        (
            "https://www.armyupress.army.mil/Portals/7/educational-services/"
            "staff-rides/StaffRideHB_AtlasofWhiteBirdCanyon.pdf"
        ),
        "U.S. Army Combat Studies Institute Press",
        "scholarly_official_military_history",
        "collins_army_white_bird_staff_ride",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_nez_perce_nps_clearwater",
        "Visit Clearwater Battlefield",
        "https://www.nps.gov/nepe/planyourvisit/visit-clearwater-battlefield.htm",
        "U.S. National Park Service, Nez Perce National Historical Park",
        "federal_battlefield_history_and_location_reference",
        "nps_nez_perce_battlefield_interpretation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_nez_perce_greene_campaign",
        "Nez Perce Summer, 1877: The U.S. Army and the Nee-Me-Poo Crisis",
        "https://npshistory.com/publications/nepe/greene/contents.htm",
        (
            "Montana Historical Society Press; National Park Service historic "
            "resource study"
        ),
        "scholarly_military_history_monograph",
        "greene_nez_perce_summer_1877",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_nez_perce_nps_big_hole",
        "Montana: Big Hole National Battlefield",
        "https://www.nps.gov/articles/bighole.htm",
        "U.S. National Park Service",
        "federal_battlefield_history",
        "nps_nez_perce_battlefield_interpretation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_nez_perce_scott_big_hole",
        "A Sharp Little Affair: The Archeology of the Big Hole Battlefield",
        "https://npshistory.com/publications/biho/sharp-little-affair.pdf",
        "National Park Service Midwest Archeological Center; J & L Reprint Company",
        "scholarly_historical_archaeology_monograph",
        "scott_big_hole_battlefield_archaeology",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_nez_perce_nps_big_hole_location",
        "Directions - Big Hole National Battlefield",
        "https://www.nps.gov/biho/planyourvisit/directions.htm",
        "U.S. National Park Service, Big Hole National Battlefield",
        "federal_battlefield_location_reference",
        "nps_nez_perce_battlefield_interpretation",
    ),
    _source(
        "wave8_nez_perce_nps_canyon_creek",
        "Visit Canyon Creek",
        "https://www.nps.gov/nepe/planyourvisit/visit-canyon-creek.htm",
        "U.S. National Park Service, Nez Perce National Historical Park",
        "federal_battlefield_history_and_location_reference",
        "nps_nez_perce_battlefield_interpretation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_nez_perce_nps_bear_paw",
        "Visit Bear Paw Battlefield",
        "https://www.nps.gov/nepe/planyourvisit/visit-bear-paw-battlefield.htm",
        "U.S. National Park Service, Nez Perce National Historical Park",
        "federal_battlefield_history_and_location_reference",
        "nps_nez_perce_battlefield_interpretation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_nez_perce_army_campaign",
        "The Nez Perce War of 1877",
        "https://www.army.mil/article/28124/the_nez_perce_war_of_1877",
        "U.S. Army Heritage and Education Center",
        "official_military_history_reference",
        "army_heritage_nez_perce_war_1877",
        outcome=True,
        crosscheck=True,
    ),
)


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_NEZ_PERCE_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    region: str,
    source_ids: Iterable[str],
    continuity_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 1877,
        "end_year": 1877,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": continuity_note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_NEZ_PERCE_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _WHITE_BIRD_FORCE_ID,
        "Non-treaty nimíipuu fighting force at White Bird Canyon (1877)",
        "engagement_bounded_indigenous_fighting_force",
        "White Bird Canyon, Idaho Territory",
        [
            "wave8_nez_perce_army_white_bird",
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_white_bird",
        ],
        (
            "Only the armed warriors from the associated non-treaty bands who "
            "fought on 17 June are rated. This formation closes before Looking "
            "Glass's band joined in July. Noncombatants and the travelling families "
            "are excluded. No rating is inherited by the nimíipuu as a people, a "
            "treaty band, a descendant community, or any modern tribal government."
        ),
    ),
    _entity(
        _CAMPAIGN_FORCE_ID,
        (
            "Joined non-treaty nimíipuu and allied campaign fighting force "
            "(July-October 1877)"
        ),
        "campaign_bounded_indigenous_allied_fighting_force",
        "Idaho and Montana Territories during the 1877 flight",
        [
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_bear_paw",
            "wave8_nez_perce_nps_big_hole",
            "wave8_nez_perce_nps_canyon_creek",
            "wave8_nez_perce_nps_clearwater",
        ],
        (
            "Campaign-bounded continuity begins after Looking Glass's band joined "
            "the mobile formation in July and ends with the Bear Paw surrender and "
            "escape in October. It covers the changing body of armed warriors from "
            "the joined non-treaty bands and attached Palouse, Cayuse, or other "
            "allies only while fighting with that formation. Noncombatants and the "
            "travelling families are excluded. No rating is inherited by any band "
            "or allied people separately, the nimíipuu as a people, descendants, "
            "or any modern tribal government."
        ),
    ),
)


_ROW_HASHES = {
    "hced-Bear Paw Mountains1877-1": (
        "50b177bcdfb087aaff4756af41892907a8fbe7cc6329d1790276b6f677acd66d"
    ),
    "hced-Big Hole River1877-1": (
        "e20ddf0abed7a31c42c18ad6df69d5f72f8ab365579abe8154da35cb801d73ac"
    ),
    "hced-Canyon Creek1877-1": (
        "3aae3a253ad0d2c53e198ec4af0ed764152f9564ffca82d6f9ce7480d9a4cad4"
    ),
    "hced-Clearwater1877-1": (
        "8c9d046239f2690c7a70cbe14ef9b1921160674aeda48e0d218989995e849365"
    ),
    "hced-White Bird Canyon1877-1": (
        "431b4074b6e30dbb7451a0182ced903afc5eff88f90968b3db3c90d9807e9073"
    ),
}


def _canonical(
    name: str,
    date_text: str,
    *,
    date_precision: str = "day",
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:1877:1877",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": 1877,
        "year_high": 1877,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    source_outcome_override: bool = False,
    outcome_reversal: bool = False,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "nez_perce_war_1877",
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": outcome_reversal,
        "actor_override": True,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_NEZ_PERCE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-White Bird Canyon1877-1": _contract(
        "hced-White Bird Canyon1877-1",
        _canonical("Battle of White Bird Canyon", "17 June 1877"),
        [_WHITE_BIRD_FORCE_ID],
        [_UNITED_STATES_ID],
        1,
        [
            "wave8_nez_perce_army_white_bird",
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_white_bird",
        ],
        [
            "wave8_nez_perce_army_white_bird",
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_white_bird",
        ],
        (
            "The NPS and Army tactical study agree that the warriors routed "
            "Perry's cavalry, retained the field, and recovered abandoned arms. "
            "The event-bounded force excludes the families sheltering nearby. The "
            "raw point is about five kilometres from the NPS published battlefield "
            "reference and is withheld; the modern-country assertion is retained."
        ),
        confidence=0.95,
    ),
    "hced-Clearwater1877-1": _contract(
        "hced-Clearwater1877-1",
        _canonical(
            "Battle of the Clearwater",
            "11-12 July 1877",
            date_precision="day_range",
        ),
        [_CAMPAIGN_FORCE_ID],
        [_UNITED_STATES_ID],
        2,
        [
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_clearwater",
        ],
        [
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_clearwater",
        ],
        (
            "The first day's check of Howard was not the two-day result. On 12 "
            "July the army gained the upper hand, forced the withdrawal, and took "
            "the camp and substantial supplies; Greene consequently adjudicates a "
            "narrow army tactical victory despite low nimíipuu losses and a "
            "successful escape. This directly reverses HCED's winner proposal and "
            "does not turn the mixed campaign consequence into a draw. The raw "
            "point resolves near the Clearwater locality rather than the NPS "
            "Battle Ridge reference and is withheld."
        ),
        confidence=0.84,
        source_outcome_override=True,
        outcome_reversal=True,
    ),
    "hced-Big Hole River1877-1": _contract(
        "hced-Big Hole River1877-1",
        _canonical(
            "Battle of the Big Hole",
            "9-10 August 1877",
            date_precision="day_range",
        ),
        [_UNITED_STATES_ID],
        [_CAMPAIGN_FORCE_ID],
        2,
        [
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_big_hole",
            "wave8_nez_perce_nps_big_hole_location",
            "wave8_nez_perce_scott_big_hole",
        ],
        [
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_big_hole",
            "wave8_nez_perce_scott_big_hole",
        ],
        (
            "The surprise attack killed many people, including noncombatants, but "
            "the reviewed tactical result is the warriors' successful counterattack: "
            "Gibbon's infantry retreated, the howitzer was captured, the army was "
            "besieged, and the travelling group escaped. Scott's battlefield study "
            "calls the infantry loss decisive. This reverses HCED's United States "
            "winner proposal without rating the killed families as participants. "
            "The raw coordinate lies within the preserved Big Hole battlefield "
            "landscape and is retained with its unreviewed-source provenance."
        ),
        confidence=0.89,
        source_outcome_override=True,
        outcome_reversal=True,
    ),
    "hced-Canyon Creek1877-1": _contract(
        "hced-Canyon Creek1877-1",
        _canonical("Battle of Canyon Creek", "13 September 1877"),
        [_CAMPAIGN_FORCE_ID],
        [_UNITED_STATES_ID],
        1,
        [
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_canyon_creek",
        ],
        [
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_canyon_creek",
        ],
        (
            "This result is limited to the rearguard mission: warriors stopped "
            "Sturgis from cutting off the moving column and most of the horse herd, "
            "then disengaged after the column escaped. It does not deny positional "
            "advances by the cavalry or losses to Crow scouts, and it infers no "
            "campaign victory. The raw point is near Helena, hundreds of kilometres "
            "west of the NPS Canyon Creek reference north of Laurel, and is withheld."
        ),
        confidence=0.87,
    ),
    "hced-Bear Paw Mountains1877-1": _contract(
        "hced-Bear Paw Mountains1877-1",
        _canonical(
            "Battle of Bear Paw",
            "30 September-5 October 1877",
            date_precision="day_range",
            granularity="battle_and_siege",
        ),
        [_UNITED_STATES_ID],
        [_CAMPAIGN_FORCE_ID],
        1,
        [
            "wave8_nez_perce_army_campaign",
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_bear_paw",
        ],
        [
            "wave8_nez_perce_army_campaign",
            "wave8_nez_perce_greene_campaign",
            "wave8_nez_perce_nps_bear_paw",
        ],
        (
            "Miles's attack became a five-day siege ending when more than 400 "
            "nimíipuu ceased fighting and surrendered. White Bird's separate escape "
            "party does not erase that tactical capitulation or become another "
            "rated result. The raw point is in the Bear Paw Mountains but materially "
            "west of the NPS battlefield coordinate near Snake Creek and is withheld."
        ),
        confidence=0.94,
    ),
}


# Every audited row has a mechanically defensible engagement result. These
# explicit empty inventories prevent an unreviewed unknown from becoming a draw.
WAVE8_NEZ_PERCE_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_NEZ_PERCE_EXCLUSIONS = WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS
WAVE8_NEZ_PERCE_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_NEZ_PERCE_HOLDS,
    **WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS,
}

WAVE8_NEZ_PERCE_CONTRACT_IDS = frozenset(WAVE8_NEZ_PERCE_CONTRACTS)
WAVE8_NEZ_PERCE_HOLD_IDS = frozenset(WAVE8_NEZ_PERCE_HOLDS)
WAVE8_NEZ_PERCE_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS
)
WAVE8_NEZ_PERCE_EXCLUSION_IDS = WAVE8_NEZ_PERCE_TERMINAL_EXCLUSION_IDS
WAVE8_NEZ_PERCE_RESERVED_IDS = frozenset(
    WAVE8_NEZ_PERCE_CONTRACT_IDS
    | WAVE8_NEZ_PERCE_HOLD_IDS
    | WAVE8_NEZ_PERCE_TERMINAL_EXCLUSION_IDS
)
WAVE8_NEZ_PERCE_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


# The Big Hole row is the only promoted coordinate consistent with the
# reviewed battlefield landscape. All five modern-country assertions are valid.
WAVE8_NEZ_PERCE_POINT_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Bear Paw Mountains1877-1",
        "hced-Canyon Creek1877-1",
        "hced-Clearwater1877-1",
        "hced-White Bird Canyon1877-1",
    }
)
WAVE8_NEZ_PERCE_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_NEZ_PERCE_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_NEZ_PERCE_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Bear Paw Mountains1877-1": {
        "field": "geometry",
        "raw_point": [-109.5130951, 48.2888807],
        "reference_source_id": "wave8_nez_perce_nps_bear_paw",
        "reviewed_reference_point": [-109.2133528, 48.3778750],
        "reason": (
            "The raw mountain-area point is roughly 24 kilometres from the NPS "
            "battlefield reference at Snake Creek and is not a battle-site assertion."
        ),
    },
    "hced-Canyon Creek1877-1": {
        "field": "geometry",
        "raw_point": [-112.2645583, 46.8067243],
        "reference_source_id": "wave8_nez_perce_nps_canyon_creek",
        "reviewed_reference_point": [-108.7957611, 45.7757722],
        "reason": (
            "The raw point is near Helena and more than 280 kilometres from the "
            "NPS battlefield reference north of Laurel."
        ),
    },
    "hced-Clearwater1877-1": {
        "field": "geometry",
        "raw_point": [-115.8997290, 46.0223922],
        "reference_source_id": "wave8_nez_perce_nps_clearwater",
        "reviewed_reference_point": [-115.9752833, 46.0762583],
        "reason": (
            "The raw point is about eight kilometres from the NPS Battle Ridge "
            "reference and instead resolves toward the Clearwater locality."
        ),
    },
    "hced-White Bird Canyon1877-1": {
        "field": "geometry",
        "raw_point": [-116.3297299, 45.7515498],
        "reference_source_id": "wave8_nez_perce_nps_white_bird",
        "reviewed_reference_point": [-116.2777417, 45.7790056],
        "reason": (
            "The raw point is about five kilometres from the NPS published "
            "battlefield reference and is not retained as an exact battle point."
        ),
    },
}


WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Big Hole River1877-1": {
        "raw_winner_raw": "United States",
        "raw_loser_raw": "Nez Perce Indians",
        "corrected_winner_side": 2,
        "corrected_winner_entity_ids": [_CAMPAIGN_FORCE_ID],
        "corrected_loser_entity_ids": [_UNITED_STATES_ID],
        "override_kind": "sourced_tactical_outcome_reversal",
        "rationale": (
            "The warriors' counterattack drove Gibbon's infantry back, captured "
            "the howitzer, besieged the command, and enabled the travelling group "
            "to escape; the archaeological study calls the infantry loss decisive."
        ),
        "outcome_source_ids": WAVE8_NEZ_PERCE_CONTRACTS[
            "hced-Big Hole River1877-1"
        ]["outcome_source_ids"],
        "outcome_source_family_ids": WAVE8_NEZ_PERCE_CONTRACTS[
            "hced-Big Hole River1877-1"
        ]["outcome_source_family_ids"],
    },
    "hced-Clearwater1877-1": {
        "raw_winner_raw": "Nez Perce Indians",
        "raw_loser_raw": "United States",
        "corrected_winner_side": 2,
        "corrected_winner_entity_ids": [_UNITED_STATES_ID],
        "corrected_loser_entity_ids": [_CAMPAIGN_FORCE_ID],
        "override_kind": "sourced_tactical_outcome_reversal",
        "rationale": (
            "The complete two-day result, rather than the first-day check, ended "
            "with Howard's force compelling withdrawal and taking the camp and "
            "supplies; the nimíipuu escape is retained as context, not a draw."
        ),
        "outcome_source_ids": WAVE8_NEZ_PERCE_CONTRACTS[
            "hced-Clearwater1877-1"
        ]["outcome_source_ids"],
        "outcome_source_family_ids": WAVE8_NEZ_PERCE_CONTRACTS[
            "hced-Clearwater1877-1"
        ]["outcome_source_family_ids"],
    },
}


WAVE8_NEZ_PERCE_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_NEZ_PERCE_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_NEZ_PERCE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_NEZ_PERCE_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {}


# Candidate-keyed negative duplicate audit over the locked IWBD, HCED, and
# release inventories. Alternate spellings are included so future probable
# twins fail closed instead of silently acquiring a second owner.
WAVE8_NEZ_PERCE_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Bear Paw Mountains1877-1": {
        "aliases": (
            "battle of bear paw",
            "battle of bear paw mountains",
            "battle of bears paw",
            "battle of bears paw mountains",
            "battle of snake creek",
            "bear paw",
            "bear paw battlefield",
            "bear paw mountains",
            "bears paw",
            "bears paw mountains",
            "snake creek",
        ),
        "years": (1877,),
    },
    "hced-Big Hole River1877-1": {
        "aliases": (
            "battle of big hole",
            "battle of big hole river",
            "battle of the big hole",
            "big hole",
            "big hole battlefield",
            "big hole river",
        ),
        "years": (1877,),
    },
    "hced-Canyon Creek1877-1": {
        "aliases": (
            "battle of canyon creek",
            "canyon creek",
            "canyon creek battle",
        ),
        "years": (1877,),
    },
    "hced-Clearwater1877-1": {
        "aliases": (
            "battle of clearwater",
            "battle of south fork clearwater",
            "battle of the clearwater",
            "clearwater",
            "clearwater battle",
            "south fork clearwater",
            "south fork of the clearwater",
        ),
        "years": (1877,),
    },
    "hced-White Bird Canyon1877-1": {
        "aliases": (
            "battle of white bird canyon",
            "battle of whitebird canyon",
            "white bird canyon",
            "whitebird canyon",
        ),
        "years": (1877,),
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_NEZ_PERCE_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_NEZ_PERCE_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_NEZ_PERCE_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_NEZ_PERCE_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_NEZ_PERCE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_NEZ_PERCE_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_NEZ_PERCE_HOLDS,
        "integration_dispositions": WAVE8_NEZ_PERCE_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_NEZ_PERCE_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_NEZ_PERCE_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_NEZ_PERCE_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_NEZ_PERCE_SOURCES,
        "terminal_exclusions": WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS,
    }


def wave8_nez_perce_audit_signature() -> str:
    """Return the SHA-256 pin over the complete audited lane state."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


# Patched to the measured payload after fixtures and dispositions are final.
WAVE8_NEZ_PERCE_FINAL_AUDIT_SIGNATURE = (
    "81982feab3afaae43358a022f075fc063ea310b395e1f6abb8b95c575ffd40d1"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_NEZ_PERCE_CONTRACTS),
        len(WAVE8_NEZ_PERCE_HOLDS),
        len(WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS),
    ) != (5, 0, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_NEZ_PERCE_ENTITIES), len(WAVE8_NEZ_PERCE_SOURCES)) != (2, 10):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_NEZ_PERCE_RESERVED_IDS != WAVE8_NEZ_PERCE_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    dispositions = (
        WAVE8_NEZ_PERCE_CONTRACT_IDS,
        WAVE8_NEZ_PERCE_HOLD_IDS,
        WAVE8_NEZ_PERCE_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(3)
        for j in range(i + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if WAVE8_NEZ_PERCE_EXCLUSIONS is not WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion inventory diverged")
    if wave8_nez_perce_audit_signature() != WAVE8_NEZ_PERCE_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_NEZ_PERCE_SOURCES
    }
    if len(source_by_id) != len(WAVE8_NEZ_PERCE_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_NEZ_PERCE_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_NEZ_PERCE_ENTITIES
    }
    expected_windows = {
        _WHITE_BIRD_FORCE_ID: (1877, 1877),
        _CAMPAIGN_FORCE_ID: (1877, 1877),
    }
    if set(entity_by_id) != set(expected_windows):
        raise ValueError(f"{_LANE_NAME} bounded identity inventory changed")
    forbidden_identity_names = {
        "nez perce",
        "nez perce indian",
        "nez perce indians",
        "nimiipuu",
    }
    for entity_id, entity in entity_by_id.items():
        if (entity["start_year"], entity["end_year"]) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} identity window changed")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} opened a generic identity fallback")
        if normalize_label(entity["name"]) in forbidden_identity_names:
            raise ValueError(f"{_LANE_NAME} installed a timeless ethnic identity")
        note = str(entity["continuity_note"]).casefold()
        for phrase in (
            "no rating is inherited",
            "noncombatants",
            "modern tribal government",
        ):
            if phrase not in note:
                raise ValueError(f"{_LANE_NAME} identity firewall is incomplete")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    expected_contracts = {
        "hced-Bear Paw Mountains1877-1": (
            [_UNITED_STATES_ID],
            [_CAMPAIGN_FORCE_ID],
            1,
            "day_range",
            "battle_and_siege",
        ),
        "hced-Big Hole River1877-1": (
            [_UNITED_STATES_ID],
            [_CAMPAIGN_FORCE_ID],
            2,
            "day_range",
            "engagement",
        ),
        "hced-Canyon Creek1877-1": (
            [_CAMPAIGN_FORCE_ID],
            [_UNITED_STATES_ID],
            1,
            "day",
            "engagement",
        ),
        "hced-Clearwater1877-1": (
            [_CAMPAIGN_FORCE_ID],
            [_UNITED_STATES_ID],
            2,
            "day_range",
            "engagement",
        ),
        "hced-White Bird Canyon1877-1": (
            [_WHITE_BIRD_FORCE_ID],
            [_UNITED_STATES_ID],
            1,
            "day",
            "engagement",
        ),
    }
    used_new_entities: set[str] = set()
    used_sources: set[str] = set()
    override_ids: set[str] = set()
    for candidate_id, contract in WAVE8_NEZ_PERCE_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        row_hash = str(contract["raw_row_sha256"])
        if len(row_hash) != 64 or any(c not in "0123456789abcdef" for c in row_hash):
            raise ValueError(f"{_LANE_NAME} has an invalid queue hash")

        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if (canonical["year_low"], canonical["year_high"]) != (1877, 1877):
            raise ValueError(f"{_LANE_NAME} widened the HCED year")

        expected_side_1, expected_side_2, winner_side, precision, granularity = (
            expected_contracts[candidate_id]
        )
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if side_1 != expected_side_1 or side_2 != expected_side_2:
            raise ValueError(f"{_LANE_NAME} actor contract drifted")
        if canonical["date_precision"] != precision:
            raise ValueError(f"{_LANE_NAME} date precision drifted")
        if canonical["granularity"] != granularity:
            raise ValueError(f"{_LANE_NAME} event granularity drifted")
        if contract["result_type"] != "win" or contract["winner_side"] != winner_side:
            raise ValueError(f"{_LANE_NAME} invented a draw or outcome")
        if contract["war_type"] != "colonial_anti_colonial":
            raise ValueError(f"{_LANE_NAME} war-type contract drifted")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor resolution is not explicit")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
        used_new_entities.update((set(side_1) | set(side_2)) & set(entity_by_id))

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

        if contract["source_outcome_override"]:
            override_ids.add(candidate_id)
            if contract["outcome_reversal"] is not True:
                raise ValueError(f"{_LANE_NAME} outcome reversal is not explicit")
        elif contract["outcome_reversal"] is not False:
            raise ValueError(f"{_LANE_NAME} mislabeled an outcome reversal")

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identities are not exactly consumed")
    expected_override_ids = {
        "hced-Big Hole River1877-1",
        "hced-Clearwater1877-1",
    }
    if override_ids != expected_override_ids:
        raise ValueError(f"{_LANE_NAME} outcome override inventory changed")
    if set(WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES) != override_ids:
        raise ValueError(f"{_LANE_NAME} outcome override metadata drifted")
    for candidate_id, override in WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES.items():
        contract = WAVE8_NEZ_PERCE_CONTRACTS[candidate_id]
        winner_side = int(override["corrected_winner_side"])
        loser_side = 3 - winner_side
        if (
            winner_side != contract["winner_side"]
            or override["corrected_winner_entity_ids"]
            != contract[f"side_{winner_side}_entity_ids"]
            or override["corrected_loser_entity_ids"]
            != contract[f"side_{loser_side}_entity_ids"]
            or override["outcome_source_ids"] != contract["outcome_source_ids"]
            or override["outcome_source_family_ids"]
            != contract["outcome_source_family_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} corrected outcome metadata drifted")

    used_sources.update(
        source_id
        for entity in WAVE8_NEZ_PERCE_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    expected_points = {
        "hced-Bear Paw Mountains1877-1",
        "hced-Canyon Creek1877-1",
        "hced-Clearwater1877-1",
        "hced-White Bird Canyon1877-1",
    }
    if WAVE8_NEZ_PERCE_POINT_QUARANTINE_ADDITIONS != expected_points:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_NEZ_PERCE_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if not expected_points <= WAVE8_NEZ_PERCE_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} quarantined an unpromoted row")
    if set(WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_REASONS) != expected_points:
        raise ValueError(f"{_LANE_NAME} location reasons are incomplete")
    for candidate_id, reason in WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_REASONS.items():
        if reason["field"] != "geometry":
            raise ValueError(f"{_LANE_NAME} location quarantine field drifted")
        if reason["reference_source_id"] not in source_by_id:
            raise ValueError(f"{_LANE_NAME} location reason names an unknown source")
        if len(reason["raw_point"]) != 2 or len(reason["reviewed_reference_point"]) != 2:
            raise ValueError(f"{_LANE_NAME} location reason has a malformed point")

    if (
        WAVE8_NEZ_PERCE_HOLDS
        or WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS
        or WAVE8_NEZ_PERCE_NONPROMOTIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty nonpromotion inventory changed")
    if (
        WAVE8_NEZ_PERCE_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_NEZ_PERCE_CROSS_LANE_DISPOSITIONS
        or WAVE8_NEZ_PERCE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_NEZ_PERCE_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty duplicate inventories changed")
    if set(WAVE8_NEZ_PERCE_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_NEZ_PERCE_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    audited_pairs: set[tuple[int, str]] = set()
    for item in WAVE8_NEZ_PERCE_IWBD_ZERO_OVERLAP_AUDIT.values():
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
            int(contract["canonical_event"]["year_low"]),
            normalize_label(contract["canonical_event"]["name"]),
        )
        for contract in WAVE8_NEZ_PERCE_CONTRACTS.values()
    }
    if not canonical_pairs <= audited_pairs:
        raise ValueError(f"{_LANE_NAME} canonical duplicate audit is incomplete")


def _is_exact_nez_perce_label(value: Any) -> bool:
    return normalize_label(value) == "nez perce indians"


def validate_wave8_nez_perce_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all and only the five exact-label rows and their fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_NEZ_PERCE_CONTRACTS,
        WAVE8_NEZ_PERCE_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_nez_perce_label(row.get("side_1_raw"))
        or _is_exact_nez_perce_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_NEZ_PERCE_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Nez Perce Indians inventory changed: "
            f"{sorted(exact_label_ids)}"
        )
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_NEZ_PERCE_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS),
    }


def _year(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best"):
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
        for item in WAVE8_NEZ_PERCE_IWBD_ZERO_OVERLAP_AUDIT.values()
        for year in item["years"]
        for alias in item["aliases"]
    }


def validate_wave8_nez_perce_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin zero duplicates and fail on any future probable event twin."""

    validate_wave8_nez_perce_queue_contracts(hced_rows)
    audited = _audited_name_year_pairs()

    hced_collisions = []
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id") or "")
        if candidate_id in WAVE8_NEZ_PERCE_RESERVED_IDS:
            continue
        year = _row_year(row)
        name = normalize_label(row.get("name"))
        if year is not None and (year, name) in audited:
            hced_collisions.append(candidate_id or "<missing-id>")
    if hced_collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): "
            f"{sorted(hced_collisions)}"
        )

    iwbd_collisions = []
    for row in iwbd_rows:
        year = _row_year(row)
        name = normalize_label(row.get("name"))
        if year is not None and (year, name) in audited:
            iwbd_collisions.append(str(row.get("candidate_id") or "<missing-id>"))
    if iwbd_collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): "
            f"{sorted(iwbd_collisions)}"
        )

    release_collisions = []
    for event in existing_events:
        candidate_id = str(event.get("hced_candidate_id") or "")
        if candidate_id in WAVE8_NEZ_PERCE_RESERVED_IDS:
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
        "cross_lane_hced_dispositions": len(WAVE8_NEZ_PERCE_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_NEZ_PERCE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(WAVE8_NEZ_PERCE_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_NEZ_PERCE_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
    }


def install_wave8_nez_perce_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_NEZ_PERCE_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_nez_perce_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_NEZ_PERCE_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_NEZ_PERCE_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_NEZ_PERCE_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_nez_perce_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_nez_perce_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_NEZ_PERCE_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_nez_perce_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_NEZ_PERCE_CONTRACTS.values(),
                    *WAVE8_NEZ_PERCE_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_nez_perce_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_NEZ_PERCE_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_NEZ_PERCE_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_NEZ_PERCE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_NEZ_PERCE_HOLDS),
        "integration_dispositions": len(WAVE8_NEZ_PERCE_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_NEZ_PERCE_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_NEZ_PERCE_ENTITIES),
        "new_sources": len(WAVE8_NEZ_PERCE_SOURCES),
        "newly_rated_events": len(WAVE8_NEZ_PERCE_CONTRACTS),
        "outcome_overrides": len(WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_NEZ_PERCE_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_NEZ_PERCE_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_NEZ_PERCE_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS),
    }


def wave8_nez_perce_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_NEZ_PERCE_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_NEZ_PERCE_POINT_QUARANTINE_ADDITIONS,
    }
