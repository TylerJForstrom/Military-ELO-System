"""Candidate-keyed Wave 8 audit for HCED's exact ``Sauk Indians`` label.

The four locked rows all belong to the 1832 Black Hawk War, but they do not
license a timeless Sauk polity.  Black Hawk's British Band was a changing,
multiethnic body of Sauk, Meskwaki, and some Kickapoo people, while the
opposing United States side combined different Illinois, Michigan Territory,
regular-army, and riverine formations from one action to the next.  This lane
therefore creates a separate event-bounded fighting identity for each side of
each promoted action.  No rating is inherited by a people, modern tribal
government, civilian family group, the United States as a whole, or a military
service across time.

Stillman's Run, Wisconsin Heights, and Bad Axe have independently supported
event-level outcomes.  Bad Axe is recorded as an engagement followed by a
massacre, and its rated British Band identity excludes every noncombatant.
Kellogg's Grove remains unknown: the year-only row does not distinguish the
16 and 25 June actions, and reputable accounts conflict over the tactical
winner of the latter.  Unknown is never converted to a draw.
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
    "WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS",
    "WAVE8_SAUK_ADJACENT_LITERAL_LABEL_INVENTORY",
    "WAVE8_SAUK_CONTRACT_IDS",
    "WAVE8_SAUK_CONTRACTS",
    "WAVE8_SAUK_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SAUK_CROSS_LANE_DISPOSITIONS",
    "WAVE8_SAUK_ENTITIES",
    "WAVE8_SAUK_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_SAUK_EXCLUSION_IDS",
    "WAVE8_SAUK_EXCLUSIONS",
    "WAVE8_SAUK_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_SAUK_EXPECTED_CANDIDATE_IDS",
    "WAVE8_SAUK_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SAUK_FUNNEL_AUDIT",
    "WAVE8_SAUK_HCED_DUPLICATE_DISPOSITIONS",
    "WAVE8_SAUK_HCED_QUEUE_SHA256",
    "WAVE8_SAUK_HOLD_IDS",
    "WAVE8_SAUK_HOLDS",
    "WAVE8_SAUK_INTEGRATION_DISPOSITIONS",
    "WAVE8_SAUK_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_SAUK_IWBD_QUEUE_SHA256",
    "WAVE8_SAUK_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_SAUK_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_SAUK_LOCATION_QUARANTINE_REASONS",
    "WAVE8_SAUK_NONPROMOTIONS",
    "WAVE8_SAUK_OUTCOME_OVERRIDES",
    "WAVE8_SAUK_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SAUK_RELATED_HCED_DISPOSITIONS",
    "WAVE8_SAUK_RESERVED_IDS",
    "WAVE8_SAUK_ROW_DISPOSITIONS",
    "WAVE8_SAUK_ROW_HASHES",
    "WAVE8_SAUK_SCOPE_AND_OPPOSITE_RESULT_AUDIT",
    "WAVE8_SAUK_SOURCES",
    "WAVE8_SAUK_TERMINAL_EXCLUSION_IDS",
    "WAVE8_SAUK_TERMINAL_EXCLUSIONS",
    "install_wave8_sauk_entities",
    "install_wave8_sauk_sources",
    "promote_wave8_sauk_contracts",
    "validate_wave8_sauk_funnel",
    "validate_wave8_sauk_integration_dispositions",
    "validate_wave8_sauk_queue_contracts",
    "wave8_sauk_audit_signature",
    "wave8_sauk_cohort_counts",
    "wave8_sauk_counts",
    "wave8_sauk_location_quarantine_additions",
    "wave8_sauk_metadata",
    "wave8_sauk_row_dispositions",
)


_LANE_NAME = "Wave 8 exact Sauk Indians Black Hawk War audit"
_MODULE_OWNER = "military_elo.promotion.wave8_sauk"
_EVENT_ID_PREFIX = "hced_wave8_sauk_"
_EXACT_LABEL = "sauk indians"

_STILLMAN_BAND_ID = "black_hawk_british_band_war_party_stillmans_run_1832"
_STILLMAN_MILITIA_ID = "stillman_bailey_illinois_militia_detachment_1832"
_WISCONSIN_BAND_ID = "black_hawk_british_band_rearguard_wisconsin_heights_1832"
_WISCONSIN_MILITIA_ID = "henry_dodge_combined_militia_wisconsin_heights_1832"
_BAD_AXE_BAND_ID = "black_hawk_british_band_fighting_remnant_bad_axe_1832"
_BAD_AXE_US_FORCE_ID = "atkinson_combined_us_force_bad_axe_1832"


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
    if outcome and crosscheck:
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


WAVE8_SAUK_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_sauk_meskwaki_history",
        "The Meskwaki Nation's History",
        "https://www.meskwaki.org/history/",
        "Sac & Fox Tribe of the Mississippi in Iowa",
        "official_tribal_history",
        "meskwaki_nation_official_history",
    ),
    _source(
        "wave8_sauk_sac_fox_bad_axe",
        "Nemishatenemo ehthakiwiyani: Black Hawk War and Bad Axe history",
        (
            "https://www.sacandfoxnation-nsn.gov/wp-content/uploads/"
            "2021/01/August_2020.pdf"
        ),
        "Sac and Fox Nation",
        "official_tribal_publication",
        "sac_and_fox_nation_bad_axe_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_sauk_army_indian_wars",
        "Indian Wars: Black Hawk campaign, 26 April-30 September 1832",
        (
            "https://history.army.mil/Research/Reference-Topics/"
            "Army-Campaigns/Brief-Summaries/Indian-Wars/"
        ),
        "U.S. Army Center of Military History",
        "official_military_history",
        "us_army_cmh_black_hawk_campaign",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_sauk_illinois_dnr_apple_river",
        "Apple River Fort and the Black Hawk War",
        (
            "https://dnrhistoric.illinois.gov/experience/sites/northwest/"
            "apple-river.html"
        ),
        "Illinois Department of Natural Resources, Historic Preservation",
        "official_state_historic_site_history",
        "illinois_dnr_apple_river_black_hawk_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_sauk_whs_historic_indians",
        "Wisconsin's Indians Since 1634: Cultural Resource Management Plan",
        (
            "https://wisconsinhistory.org/MediaFileLocation/"
            "xkzjatfm/wi-shpo-crmp-volume-1-historic-indians.pdf"
        ),
        "Wisconsin Historical Society, State Historic Preservation Office",
        "official_state_historic_context",
        "wisconsin_shpo_historic_indians_context",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_sauk_whs_dodge_wisconsin_heights",
        "The Battle of Wisconsin Heights: Henry Dodge's account",
        (
            "https://www.wisconsinhistory.org/pdfs/lessons/"
            "EDU-Account-BlackHawkWar1832-Henry-Dodge.pdf"
        ),
        "Wisconsin Historical Society",
        "published_contemporary_command_report",
        "henry_dodge_wisconsin_heights_primary_account",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_sauk_whs_black_hawk_wisconsin_heights",
        "The Battle of Wisconsin Heights: Black Hawk's account",
        (
            "https://www.wisconsinhistory.org/pdfs/lessons/"
            "EDU-Account-BlackHawkWar1832-Black-Hawk.pdf"
        ),
        "Wisconsin Historical Society",
        "published_indigenous_primary_account",
        "black_hawk_wisconsin_heights_primary_account",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_sauk_whs_atkinson_bad_axe",
        "The Battle of Bad Axe: General Atkinson's account",
        (
            "https://www.wisconsinhistory.org/pdfs/lessons/"
            "EDU-Account-BlackHawkWar1832-General-Atkinson.pdf"
        ),
        "Wisconsin Historical Society",
        "published_contemporary_command_report",
        "henry_atkinson_bad_axe_primary_account",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_sauk_oupress_jung",
        "The Black Hawk War of 1832",
        "https://www.oupress.com/9780806139944/the-black-hawk-war-of-1832/",
        "University of Oklahoma Press",
        "scholarly_monograph",
        "patrick_jung_black_hawk_war_monograph",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_sauk_uiowa_black_hawk",
        "Black Hawk",
        "https://uipress.lib.uiowa.edu/bdi/DetailsPage.aspx?id=31",
        "University of Iowa Libraries and University of Iowa Press",
        "scholarly_biographical_reference",
        "university_iowa_black_hawk_biography",
    ),
    _source(
        "wave8_sauk_uillinois_black_hawk",
        "Black Hawk: An Autobiography",
        "https://www.press.uillinois.edu/books/?id=p723254",
        "University of Illinois Press",
        "scholarly_edited_primary_source",
        "university_illinois_black_hawk_autobiography",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_sauk_lincoln_log_kellogg",
        "The Lincoln Log: 25-26 June 1832 at Kellogg's Grove",
        (
            "https://www.thelincolnlog.org/Results.aspx?"
            "month=6&type=CalendarMonth&year=1832"
        ),
        "Abraham Lincoln Association",
        "scholarly_documentary_chronology",
        "lincoln_log_kelloggs_grove_chronology",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_sauk_nps_kelloggs_grove",
        "Kellogg's Grove, National Register Information System 78001191",
        "https://npgallery.nps.gov/AssetDetail/NRIS/78001191",
        "U.S. National Park Service",
        "official_national_register_record",
        "nps_kelloggs_grove_register_record",
    ),
    _source(
        "wave8_sauk_whs_wisconsin_heights_register",
        "Wisconsin Heights Battlefield, National Register record",
        "https://www.wisconsinhistory.org/Records/NationalRegister/NR1815",
        "Wisconsin Historical Society",
        "official_state_and_national_register_record",
        "wisconsin_heights_battlefield_register_record",
    ),
    _source(
        "wave8_sauk_illinois_stillman_register",
        "National Register of Historic Places in Illinois",
        (
            "https://dnrhistoric.illinois.gov/content/dam/soi/en/web/"
            "dnrhistoric/preserve/siteassets/pages/places/"
            "national-register-listings-in-illinois-updated-june-2022.pdf"
        ),
        "Illinois Department of Natural Resources, Historic Preservation",
        "official_state_national_register_inventory",
        "illinois_national_register_stillmans_run",
    ),
    _source(
        "wave8_sauk_whs_bad_axe_marker",
        "Bad Axe Battlefield Site Marker",
        "https://www.wisconsinhistory.org/Records/Image/IM37846",
        "Wisconsin Historical Society",
        "official_historical_collection_location_record",
        "wisconsin_historical_society_bad_axe_marker",
    ),
    _source(
        "wave8_sauk_whs_black_hawk_route",
        "Black Hawk's Route Through Wisconsin",
        "https://www.wisconsinhistory.org/record/map/W0135UO",
        "Wisconsin Historical Society",
        "official_historical_map_catalog_record",
        "wisconsin_historical_society_black_hawk_route_map",
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_SAUK_SOURCES}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    source_ids: Iterable[str],
    scope: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 1832,
        "end_year": 1832,
        "region": "North America",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            f"{scope} This identity exists only for the named 1832 action. "
            "No rating is inherited by the Sauk or Meskwaki peoples, any "
            "Kickapoo participants, civilians, noncombatants, or accompanying families, a "
            "modern tribal government, the United States as a whole, the U.S. "
            "Army, a territorial or state militia, or any formation across time."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_SAUK_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _STILLMAN_BAND_ID,
        "Black Hawk's British Band war party at Stillman's Run (1832)",
        "event_bounded_multiethnic_war_party",
        [
            "wave8_sauk_army_indian_wars",
            "wave8_sauk_illinois_dnr_apple_river",
            "wave8_sauk_oupress_jung",
            "wave8_sauk_uiowa_black_hawk",
        ],
        (
            "Event-bounded warriors under Black Hawk; the British Band included "
            "Sauk, Meskwaki, and some Kickapoo members and is not a generic tribe."
        ),
    ),
    _entity(
        _STILLMAN_MILITIA_ID,
        "Stillman-Bailey Illinois militia detachment at Stillman's Run (1832)",
        "event_bounded_militia_detachment",
        [
            "wave8_sauk_army_indian_wars",
            "wave8_sauk_illinois_dnr_apple_river",
            "wave8_sauk_illinois_stillman_register",
        ],
        "Event-bounded Illinois volunteer detachment under Isaiah Stillman and David Bailey.",
    ),
    _entity(
        _WISCONSIN_BAND_ID,
        "Black Hawk's British Band rearguard at Wisconsin Heights (1832)",
        "event_bounded_multiethnic_rearguard",
        [
            "wave8_sauk_meskwaki_history",
            "wave8_sauk_whs_black_hawk_route",
            "wave8_sauk_whs_black_hawk_wisconsin_heights",
            "wave8_sauk_whs_dodge_wisconsin_heights",
        ],
        (
            "Event-bounded rearguard of roughly fifty warriors that covered the "
            "British Band families' Wisconsin River crossing."
        ),
    ),
    _entity(
        _WISCONSIN_MILITIA_ID,
        "Henry-Dodge combined militia force at Wisconsin Heights (1832)",
        "event_bounded_combined_militia_force",
        [
            "wave8_sauk_army_indian_wars",
            "wave8_sauk_whs_dodge_wisconsin_heights",
            "wave8_sauk_whs_wisconsin_heights_register",
        ],
        (
            "Event-bounded Illinois volunteers under James D. Henry and Michigan "
            "Territory mounted volunteers under Henry Dodge."
        ),
    ),
    _entity(
        _BAD_AXE_BAND_ID,
        "British Band fighting remnant at Bad Axe (1832)",
        "event_bounded_multiethnic_fighting_remnant",
        [
            "wave8_sauk_meskwaki_history",
            "wave8_sauk_sac_fox_bad_axe",
            "wave8_sauk_whs_atkinson_bad_axe",
            "wave8_sauk_whs_historic_indians",
        ],
        (
            "Event-bounded armed defenders at Bad Axe only. Women, children, "
            "elders, captives, swimmers, and every other noncombatant killed or "
            "displaced during the massacre are expressly outside this identity."
        ),
    ),
    _entity(
        _BAD_AXE_US_FORCE_ID,
        "Atkinson's combined U.S. force at Bad Axe (1832)",
        "event_bounded_combined_regular_militia_river_force",
        [
            "wave8_sauk_army_indian_wars",
            "wave8_sauk_whs_atkinson_bad_axe",
            "wave8_sauk_whs_bad_axe_marker",
        ],
        (
            "Event-bounded U.S. regulars, Illinois and Michigan Territory "
            "volunteers, and the armed steamboat element engaged at Bad Axe."
        ),
    ),
)


WAVE8_SAUK_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_SAUK_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)
WAVE8_SAUK_ROW_HASHES: dict[str, str] = {
    "hced-Bad Axe1832-1": (
        "b3424ee2b465fb9f8de8fc90cccafc3b15265560d73362edce6b2325a4521f82"
    ),
    "hced-Kelloggs Grove1832-1": (
        "b0bb092a16351619c4c692cb803540cb81fffa40ac486d9e3b9b4d505fe3487c"
    ),
    "hced-Rock River1832-1": (
        "e50eda3594bbec024d32fcff66b4c1589d71efc709eee582cf2b404c9431ab77"
    ),
    "hced-Wisconsin Heights1832-1": (
        "c496f0b04d8e4e0787443680ab74f11a0276ab142d3170e9d37bea053d4e80e7"
    ),
}
WAVE8_SAUK_EXACT_CANDIDATE_ID_SHA256 = (
    "d309fd7b74d14a6eb9795fda0cfdb111d934cfcdf61edef0273b123ccc82942f"
)

WAVE8_SAUK_FUNNEL_AUDIT: dict[str, Any] = {
    "event_candidate_id_sha256": WAVE8_SAUK_EXACT_CANDIDATE_ID_SHA256,
    "events_touched": 4,
    "newly_unblocked_candidate_id_sha256": WAVE8_SAUK_EXACT_CANDIDATE_ID_SHA256,
    "sole_blocker_events": 4,
}


def _canonical(
    name: str,
    date_text: str,
    *,
    date_precision: str = "day",
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:1832:1832",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": 1832,
        "year_high": 1832,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    winner_side: int,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_SAUK_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "black_hawk_war_1832",
        "disposition": "promote",
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "event_bounded_mixed_band_and_us_formation",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_SAUK_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Rock River1832-1": _contract(
        "hced-Rock River1832-1",
        _canonical("Battle of Stillman's Run", "14 May 1832"),
        [_STILLMAN_BAND_ID],
        [_STILLMAN_MILITIA_ID],
        [
            "wave8_sauk_army_indian_wars",
            "wave8_sauk_illinois_dnr_apple_river",
            "wave8_sauk_illinois_stillman_register",
            "wave8_sauk_oupress_jung",
            "wave8_sauk_uiowa_black_hawk",
        ],
        [
            "wave8_sauk_army_indian_wars",
            "wave8_sauk_illinois_dnr_apple_river",
            "wave8_sauk_oupress_jung",
        ],
        (
            "HCED's Rock River row is the 14 May action conventionally named "
            "Stillman's Run. Official Illinois and Army histories agree that "
            "Black Hawk's warriors routed the volunteer detachment. The raw point "
            "does not match the registered Stillman Valley battlefield and is withheld."
        ),
        winner_side=1,
        confidence=0.96,
    ),
    "hced-Wisconsin Heights1832-1": _contract(
        "hced-Wisconsin Heights1832-1",
        _canonical("Battle of Wisconsin Heights", "21 July 1832"),
        [_WISCONSIN_MILITIA_ID],
        [_WISCONSIN_BAND_ID],
        [
            "wave8_sauk_army_indian_wars",
            "wave8_sauk_oupress_jung",
            "wave8_sauk_whs_black_hawk_route",
            "wave8_sauk_whs_black_hawk_wisconsin_heights",
            "wave8_sauk_whs_dodge_wisconsin_heights",
            "wave8_sauk_whs_historic_indians",
            "wave8_sauk_whs_wisconsin_heights_register",
        ],
        [
            "wave8_sauk_army_indian_wars",
            "wave8_sauk_whs_black_hawk_wisconsin_heights",
            "wave8_sauk_whs_dodge_wisconsin_heights",
            "wave8_sauk_whs_historic_indians",
        ],
        (
            "Dodge's report and the Army history support the militia's battlefield "
            "victory: the rearguard was dislodged and driven to the river. Black "
            "Hawk's account independently establishes that his holding action also "
            "achieved its protective purpose. The rating is only the contested-field "
            "result, at reduced confidence, not a denial of that successful withdrawal."
        ),
        winner_side=1,
        confidence=0.82,
    ),
    "hced-Bad Axe1832-1": _contract(
        "hced-Bad Axe1832-1",
        _canonical(
            "Battle and massacre at Bad Axe",
            "1-2 August 1832",
            date_precision="day_range",
            granularity="engagement_followed_by_massacre",
        ),
        [_BAD_AXE_US_FORCE_ID],
        [_BAD_AXE_BAND_ID],
        [
            "wave8_sauk_army_indian_wars",
            "wave8_sauk_oupress_jung",
            "wave8_sauk_sac_fox_bad_axe",
            "wave8_sauk_whs_atkinson_bad_axe",
            "wave8_sauk_whs_bad_axe_marker",
            "wave8_sauk_whs_historic_indians",
        ],
        [
            "wave8_sauk_army_indian_wars",
            "wave8_sauk_oupress_jung",
            "wave8_sauk_sac_fox_bad_axe",
            "wave8_sauk_whs_atkinson_bad_axe",
            "wave8_sauk_whs_historic_indians",
        ],
        (
            "The reviewed sources converge on a decisive U.S. combat victory and "
            "the destruction of the remaining armed resistance. They also document "
            "the killing of fleeing noncombatants. Only the event-bounded fighting "
            "formations are rated; civilian deaths are not transformed into an Elo "
            "result. The two-day river-and-island footprint is not reduced to HCED's point."
        ),
        winner_side=1,
        confidence=0.94,
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    evidence_refs: Iterable[str],
    hold_reason: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_SAUK_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "black_hawk_war_1832",
        "disposition": "hold",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "hold_reason": hold_reason,
    }


WAVE8_SAUK_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Kelloggs Grove1832-1": _hold(
        "hced-Kelloggs Grove1832-1",
        _canonical(
            "Kellogg's Grove engagements",
            "16 and 25 June 1832",
            date_precision="multiple_days",
            granularity="ambiguous_same_place_multi_engagement_record",
        ),
        [
            "wave8_sauk_illinois_dnr_apple_river",
            "wave8_sauk_lincoln_log_kellogg",
            "wave8_sauk_nps_kelloggs_grove",
            "wave8_sauk_oupress_jung",
            "wave8_sauk_uillinois_black_hawk",
        ],
        (
            "Not promoted: Kellogg's Grove hosted separate actions on 16 and 25 "
            "June, while HCED supplies only place and year. The current Illinois "
            "site history describes U.S. pressure forcing Black Hawk north, but "
            "Black Hawk's account and modern scholarship treat the 25 June action "
            "as his last military success. These accounts conflict. Choosing an "
            "episode or tactical winner "
            "would invent certainty; the unresolved outcome is not a draw."
        ),
    ),
}

WAVE8_SAUK_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_SAUK_EXCLUSIONS = WAVE8_SAUK_TERMINAL_EXCLUSIONS
WAVE8_SAUK_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_SAUK_HOLDS,
    **WAVE8_SAUK_TERMINAL_EXCLUSIONS,
}

WAVE8_SAUK_CONTRACT_IDS = frozenset(WAVE8_SAUK_CONTRACTS)
WAVE8_SAUK_HOLD_IDS = frozenset(WAVE8_SAUK_HOLDS)
WAVE8_SAUK_TERMINAL_EXCLUSION_IDS = frozenset(WAVE8_SAUK_TERMINAL_EXCLUSIONS)
WAVE8_SAUK_EXCLUSION_IDS = WAVE8_SAUK_TERMINAL_EXCLUSION_IDS
WAVE8_SAUK_RESERVED_IDS = frozenset(
    WAVE8_SAUK_CONTRACT_IDS
    | WAVE8_SAUK_HOLD_IDS
    | WAVE8_SAUK_TERMINAL_EXCLUSION_IDS
)
WAVE8_SAUK_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_SAUK_ROW_HASHES)
WAVE8_SAUK_ROW_DISPOSITIONS = {
    **{candidate_id: "promote" for candidate_id in WAVE8_SAUK_CONTRACT_IDS},
    **{candidate_id: "hold" for candidate_id in WAVE8_SAUK_HOLD_IDS},
}


WAVE8_SAUK_POINT_QUARANTINE_ADDITIONS = frozenset(WAVE8_SAUK_CONTRACT_IDS)
WAVE8_SAUK_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_SAUK_LOCATION_QUARANTINE_ADDITIONS = {
    "country": WAVE8_SAUK_COUNTRY_QUARANTINE_ADDITIONS,
    "point": WAVE8_SAUK_POINT_QUARANTINE_ADDITIONS,
}
WAVE8_SAUK_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Rock River1832-1": {
        "actions": ["withhold_point"],
        "evidence_refs": ["wave8_sauk_illinois_stillman_register"],
        "reason": (
            "HCED's coordinate is materially displaced from the registered "
            "Stillman's Run site at Roosevelt and Spruce Streets in Stillman "
            "Valley. The United States modern-country assertion remains valid."
        ),
    },
    "hced-Wisconsin Heights1832-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_sauk_whs_black_hawk_route",
            "wave8_sauk_whs_wisconsin_heights_register",
        ],
        "reason": (
            "The registered battlefield is a site southeast of the County Y and "
            "State 78 junction, while HCED supplies an unverified point for a "
            "multi-position rearguard action. The United States country is retained."
        ),
    },
    "hced-Bad Axe1832-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_sauk_whs_atkinson_bad_axe",
            "wave8_sauk_whs_bad_axe_marker",
        ],
        "reason": (
            "The reviewed action extended across the river bank, sloughs, willow "
            "islands, and Mississippi crossing over two days. A single HCED point "
            "cannot represent that footprint; the United States country is retained."
        ),
    },
}


WAVE8_SAUK_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_SAUK_HCED_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_SAUK_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_SAUK_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}


WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Pecatonica1832-1": {
        "raw_row_sha256": (
            "d721827b8f598cd586833273241de24a88e1c9dc6af3dfda65e22e4cf69936f6"
        ),
        "literal_label": "sawk indians",
        "disposition": "adjacent_misspelled_label_separate_exact_lane",
        "owner_module": None,
        "outcome_not_adjudicated": True,
        "boundary_note": (
            "A distinct Pecatonica engagement under HCED's literal 'Sawk Indians' "
            "label; this exact 'Sauk Indians' lane neither promotes nor excludes it."
        ),
        "evidence_refs": [
            "wave8_sauk_oupress_jung",
            "wave8_sauk_whs_historic_indians",
        ],
    },
    "hced-Rock Island Rapids1814-1": {
        "raw_row_sha256": (
            "c7cb00b6e3a9c82f92320c8a8e187ca6713a55d71735da69198c191779b3f1d5"
        ),
        "literal_label": "sauk indians fox indians kickapoo indians",
        "disposition": "distinct_1814_multi_actor_coalition",
        "owner_module": None,
        "outcome_not_adjudicated": True,
        "boundary_note": (
            "War of 1812 coalition row, eighteen years before the Black Hawk War; "
            "it cannot inherit any 1832 British Band event identity."
        ),
        "evidence_refs": [
            "wave8_sauk_meskwaki_history",
            "wave8_sauk_uiowa_black_hawk",
        ],
    },
}
WAVE8_SAUK_RELATED_HCED_DISPOSITIONS = WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS
WAVE8_SAUK_ADJACENT_LITERAL_LABEL_INVENTORY: dict[str, frozenset[str]] = {
    "sauk indians fox indians kickapoo indians": frozenset(
        {"hced-Rock Island Rapids1814-1"}
    ),
    "sawk indians": frozenset({"hced-Pecatonica1832-1"}),
}


WAVE8_SAUK_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "wave8_kickapoo": {
        "disposition": "composite_1814_row_outside_both_exact_label_lanes",
        "other_module": "military_elo.promotion.wave8_kickapoo",
        "candidate_ids": ["hced-Rock Island Rapids1814-1"],
        "reason": (
            "Kickapoo participation in the 1814 coalition does not make that row "
            "an exact Kickapoo or exact Sauk fixture. Neither lane claims it."
        ),
        "evidence_refs": [
            "wave8_sauk_meskwaki_history",
            "wave8_sauk_uiowa_black_hawk",
        ],
    }
}


WAVE8_SAUK_SCOPE_AND_OPPOSITE_RESULT_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Rock River1832-1": {
        "canonical_action": "Stillman's Run, 14 May 1832",
        "scope": "single engagement",
        "reviewed_result": "British Band tactical victory",
        "opposite_result_boundary": (
            "Later U.S. victories at Wisconsin Heights and Bad Axe are distinct actions."
        ),
    },
    "hced-Kelloggs Grove1832-1": {
        "canonical_action": "two Kellogg's Grove actions, 16 and 25 June 1832",
        "scope": "ambiguous same-place multi-engagement row",
        "reviewed_result": "unknown",
        "opposite_result_boundary": (
            "U.S.-victory and British-Band-success readings are both attested; no draw."
        ),
    },
    "hced-Wisconsin Heights1832-1": {
        "canonical_action": "Wisconsin Heights, 21 July 1832",
        "scope": "single rearguard engagement",
        "reviewed_result": "U.S. battlefield victory",
        "opposite_result_boundary": (
            "Black Hawk's successful protective withdrawal is preserved in confidence "
            "and scope, not substituted for the contested-field result."
        ),
    },
    "hced-Bad Axe1832-1": {
        "canonical_action": "Bad Axe, 1-2 August 1832",
        "scope": "engagement followed by massacre",
        "reviewed_result": "U.S. combat victory",
        "opposite_result_boundary": (
            "Civilians killed while fleeing are outside both rated formations."
        ),
    },
    "hced-Pecatonica1832-1": {
        "canonical_action": "Pecatonica, 16 June 1832",
        "scope": "adjacent misspelled-label engagement",
        "reviewed_result": "not adjudicated in this lane",
        "opposite_result_boundary": "Distinct row, place, formation, and literal label.",
    },
    "hced-Rock Island Rapids1814-1": {
        "canonical_action": "Rock Island Rapids, 1814",
        "scope": "adjacent multi-actor War of 1812 coalition",
        "reviewed_result": "not adjudicated in this lane",
        "opposite_result_boundary": "Distinct war, year, coalition, and formation.",
    },
}


WAVE8_SAUK_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Bad Axe1832-1": {
        "aliases": sorted(
            {
                "bad axe",
                "bad axe massacre",
                "battle and massacre at bad axe",
                "battle of bad axe",
                "massacre at bad axe",
            }
        ),
        "years": [1832, 1832],
    },
    "hced-Kelloggs Grove1832-1": {
        "aliases": sorted(
            {
                "battle of kellogg s grove",
                "battle of kelloggs grove",
                "kellogg s grove",
                "kelloggs grove",
                "second battle of kellogg s grove",
            }
        ),
        "years": [1832, 1832],
    },
    "hced-Rock River1832-1": {
        "aliases": sorted(
            {
                "battle of stillman s run",
                "battle of stillmans run",
                "old man s creek",
                "rock river",
                "stillman s run",
                "stillmans run",
            }
        ),
        "years": [1832, 1832],
    },
    "hced-Wisconsin Heights1832-1": {
        "aliases": sorted(
            {"battle of wisconsin heights", "wisconsin heights"}
        ),
        "years": [1832, 1832],
    },
}

WAVE8_SAUK_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"adjacent_hced:{candidate_id}": disposition
        for candidate_id, disposition in WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS.items()
    },
    **{
        f"cross_lane:{module_name}": disposition
        for module_name, disposition in WAVE8_SAUK_CROSS_LANE_DISPOSITIONS.items()
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_hced_dispositions": WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS,
        "adjacent_literal_label_inventory": {
            key: sorted(value)
            for key, value in WAVE8_SAUK_ADJACENT_LITERAL_LABEL_INVENTORY.items()
        },
        "contracts": WAVE8_SAUK_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_SAUK_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_SAUK_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_SAUK_ENTITIES,
        "exact_candidate_id_sha256": WAVE8_SAUK_EXACT_CANDIDATE_ID_SHA256,
        "existing_release_duplicate_dispositions": (
            WAVE8_SAUK_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_SAUK_EXPECTED_CANDIDATE_IDS),
        "funnel_audit": WAVE8_SAUK_FUNNEL_AUDIT,
        "hced_duplicate_dispositions": WAVE8_SAUK_HCED_DUPLICATE_DISPOSITIONS,
        "hced_queue_sha256": WAVE8_SAUK_HCED_QUEUE_SHA256,
        "holds": WAVE8_SAUK_HOLDS,
        "integration_dispositions": WAVE8_SAUK_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_SAUK_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_queue_sha256": WAVE8_SAUK_IWBD_QUEUE_SHA256,
        "iwbd_zero_overlap_audit": WAVE8_SAUK_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_SAUK_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_SAUK_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(WAVE8_SAUK_POINT_QUARANTINE_ADDITIONS),
        "row_hashes": WAVE8_SAUK_ROW_HASHES,
        "scope_and_opposite_result_audit": WAVE8_SAUK_SCOPE_AND_OPPOSITE_RESULT_AUDIT,
        "sources": WAVE8_SAUK_SOURCES,
        "terminal_exclusions": WAVE8_SAUK_TERMINAL_EXCLUSIONS,
    }


def wave8_sauk_audit_signature() -> str:
    """Return the SHA-256 pin over the complete audited lane state."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


# Mechanically measured from the complete payload above.  Any fixture,
# evidence, boundary, or disposition change requires a conscious re-sign.
WAVE8_SAUK_FINAL_AUDIT_SIGNATURE = (
    "ec90a3cb838235b310db77628cea405066d7e46e0b306ecef369b0c4b8178b93"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_SAUK_CONTRACTS),
        len(WAVE8_SAUK_HOLDS),
        len(WAVE8_SAUK_TERMINAL_EXCLUSIONS),
    ) != (3, 1, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_SAUK_ENTITIES), len(WAVE8_SAUK_SOURCES)) != (6, 17):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_SAUK_RESERVED_IDS != WAVE8_SAUK_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_SAUK_CONTRACT_IDS & WAVE8_SAUK_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion and hold inventories overlap")
    if WAVE8_SAUK_EXCLUSIONS is not WAVE8_SAUK_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion inventory diverged")
    if any(
        len(value) != 64
        for value in (
            WAVE8_SAUK_HCED_QUEUE_SHA256,
            WAVE8_SAUK_IWBD_QUEUE_SHA256,
            WAVE8_SAUK_EXACT_CANDIDATE_ID_SHA256,
            *WAVE8_SAUK_ROW_HASHES.values(),
        )
    ):
        raise ValueError(f"{_LANE_NAME} snapshot hash inventory drifted")
    if wave8_sauk_audit_signature() != WAVE8_SAUK_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_SAUK_SOURCES}
    if len(source_by_id) != len(WAVE8_SAUK_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    families = {str(source["source_family_id"]) for source in WAVE8_SAUK_SOURCES}
    if len(families) < 14:
        raise ValueError(f"{_LANE_NAME} source-family independence weakened")
    for source in WAVE8_SAUK_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_SAUK_ENTITIES}
    if len(entity_by_id) != len(WAVE8_SAUK_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    for entity in WAVE8_SAUK_ENTITIES:
        if (
            entity["start_year"] != 1832
            or entity["end_year"] != 1832
            or entity["aliases"]
            or entity["predecessors"]
        ):
            raise ValueError(f"{_LANE_NAME} entity escaped its event window")
        note = str(entity["continuity_note"]).casefold()
        for phrase in (
            "no rating is inherited",
            "modern tribal government",
            "united states as a whole",
            "noncombatant",
        ):
            if phrase not in note:
                raise ValueError(f"{_LANE_NAME} identity boundary weakened")
        source_ids = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(source_ids) or not set(source_ids) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity provenance drifted")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_SAUK_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_SAUK_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if (
            canonical["canonical_key"] != expected_key
            or canonical["year_low"] != 1832
            or canonical["year_high"] != 1832
            or not canonical["date_text"]
        ):
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if len(side_1) != 1 or len(side_2) != 1 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} opposing actor boundary changed")
        used_entities.update(side_1 + side_2)
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or int(contract["winner_side"]) not in {1, 2}
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"]
            != "event_bounded_mixed_band_and_us_formation"
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
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if (
            len(outcomes) < 3
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance weakened")
        expected_families = sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if families != expected_families or len(families) < 3:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")

    for candidate_id, hold in WAVE8_SAUK_HOLDS.items():
        if (
            hold["raw_row_sha256"] != WAVE8_SAUK_ROW_HASHES[candidate_id]
            or hold["disposition"] != "hold"
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} hold became rateable")
        for forbidden in (
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "outcome_source_ids",
            "outcome_source_family_ids",
        ):
            if forbidden in hold:
                raise ValueError(f"{_LANE_NAME} hold asserts an outcome")
        reason = str(hold["hold_reason"]).casefold()
        for phrase in ("not promoted", "16 and 25", "conflict", "not a draw"):
            if phrase not in reason:
                raise ValueError(f"{_LANE_NAME} Kellogg hold boundary weakened")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence drifted")
        used_sources.update(evidence)

    if (
        WAVE8_SAUK_TERMINAL_EXCLUSIONS
        or WAVE8_SAUK_OUTCOME_OVERRIDES
        or WAVE8_SAUK_HCED_DUPLICATE_DISPOSITIONS
        or WAVE8_SAUK_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_SAUK_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")
    if WAVE8_SAUK_POINT_QUARANTINE_ADDITIONS != WAVE8_SAUK_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_SAUK_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    if set(WAVE8_SAUK_LOCATION_QUARANTINE_REASONS) != WAVE8_SAUK_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    for review in WAVE8_SAUK_LOCATION_QUARANTINE_REASONS.values():
        if review["actions"] != ["withhold_point"] or not review["reason"]:
            raise ValueError(f"{_LANE_NAME} location policy drifted")
        evidence = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence drifted")
        used_sources.update(evidence)

    if set(WAVE8_SAUK_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_SAUK_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for audit in WAVE8_SAUK_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, audit["aliases"]))
        years = list(map(int, audit["years"]))
        if (
            not aliases
            or not _is_sorted_unique(aliases)
            or aliases != list(map(normalize_label, aliases))
            or years != [1832, 1832]
        ):
            raise ValueError(f"{_LANE_NAME} duplicate audit drifted")

    expected_adjacent = {
        "hced-Pecatonica1832-1",
        "hced-Rock Island Rapids1814-1",
    }
    if set(WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS) != expected_adjacent:
        raise ValueError(f"{_LANE_NAME} adjacent HCED audit changed")
    if set().union(*WAVE8_SAUK_ADJACENT_LITERAL_LABEL_INVENTORY.values()) != expected_adjacent:
        raise ValueError(f"{_LANE_NAME} adjacent literal-label inventory changed")
    for candidate_id, disposition in WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS.items():
        if (
            len(str(disposition["raw_row_sha256"])) != 64
            or disposition["outcome_not_adjudicated"] is not True
            or disposition["owner_module"] is not None
            or candidate_id in WAVE8_SAUK_RESERVED_IDS
        ):
            raise ValueError(f"{_LANE_NAME} adjacent ownership boundary changed")
        evidence = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} adjacent evidence drifted")
        used_sources.update(evidence)
    if set(WAVE8_SAUK_SCOPE_AND_OPPOSITE_RESULT_AUDIT) != (
        WAVE8_SAUK_EXPECTED_CANDIDATE_IDS | expected_adjacent
    ):
        raise ValueError(f"{_LANE_NAME} scope/opposite-result audit changed")
    if set(WAVE8_SAUK_INTEGRATION_DISPOSITIONS) != {
        "adjacent_hced:hced-Pecatonica1832-1",
        "adjacent_hced:hced-Rock Island Rapids1814-1",
        "cross_lane:wave8_kickapoo",
    }:
        raise ValueError(f"{_LANE_NAME} integration disposition inventory changed")

    for disposition in WAVE8_SAUK_CROSS_LANE_DISPOSITIONS.values():
        evidence = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} cross-lane evidence drifted")
        used_sources.update(evidence)
    used_sources.update(
        source_id
        for entity in WAVE8_SAUK_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(
            f"{_LANE_NAME} source fixtures are not exactly consumed: "
            f"{sorted(set(source_by_id) - used_sources)}"
        )


def _is_exact_label(value: Any) -> bool:
    return normalize_label(value) == _EXACT_LABEL


def validate_wave8_sauk_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin all and only the four exact-label rows and their dispositions."""

    _validate_static()
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SAUK_CONTRACTS,
        WAVE8_SAUK_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_label(row.get("side_1_raw"))
        or _is_exact_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_SAUK_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed: {sorted(exact_ids)}")
    return {
        "holds": len(WAVE8_SAUK_HOLDS),
        "promotion_contracts": counts["promotion_contracts"],
        "reviewed_hced_rows": len(WAVE8_SAUK_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_SAUK_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_sauk_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    """Pin the four-row unresolved-label funnel without installing an alias."""

    _validate_static()
    labels = funnel.get("labels")
    if not isinstance(labels, list):
        raise ValueError(f"{_LANE_NAME} funnel labels are unavailable")
    matches = [item for item in labels if item.get("label") == _EXACT_LABEL]
    if len(matches) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label row")
    label = matches[0]
    for key in ("event_candidate_id_sha256", "events_touched", "sole_blocker_events"):
        if label.get(key) != WAVE8_SAUK_FUNNEL_AUDIT[key]:
            raise ValueError(f"{_LANE_NAME} funnel {key} changed")
    failures = label.get("failure_cases")
    if not isinstance(failures, Mapping) or failures.get("zero_time_valid_candidates") != 4:
        raise ValueError(f"{_LANE_NAME} funnel failure case changed")
    if label.get("candidate_ids") or label.get("time_valid_candidate_ids"):
        raise ValueError(f"{_LANE_NAME} unexpectedly acquired a generic identity")

    greedy = funnel.get("greedy_batch")
    ranking = greedy.get("ranking") if isinstance(greedy, Mapping) else None
    if not isinstance(ranking, list):
        raise ValueError(f"{_LANE_NAME} greedy ranking is unavailable")
    ranked = [item for item in ranking if item.get("label") == _EXACT_LABEL]
    if len(ranked) != 1:
        raise ValueError(f"{_LANE_NAME} expected one greedy ranking row")
    if (
        ranked[0].get("events_touched") != 4
        or ranked[0].get("marginal_events") != 4
        or ranked[0].get("newly_unblocked_candidate_id_sha256")
        != WAVE8_SAUK_FUNNEL_AUDIT["newly_unblocked_candidate_id_sha256"]
    ):
        raise ValueError(f"{_LANE_NAME} greedy audit changed")

    row_data = funnel.get("row_label_data")
    if not isinstance(row_data, list):
        raise ValueError(f"{_LANE_NAME} row-label data are unavailable")
    audited: set[str] = set()
    for row in row_data:
        failures = row.get("label_failures")
        matching = (
            [item for item in failures if item.get("label") == _EXACT_LABEL]
            if isinstance(failures, list)
            else []
        )
        if matching:
            if (
                len(matching) != 1
                or matching[0].get("failure_case") != "zero_time_valid_candidates"
                or row.get("sole_blocker_label") != _EXACT_LABEL
            ):
                raise ValueError(f"{_LANE_NAME} row funnel boundary changed")
            audited.add(str(row.get("candidate_id")))
    if audited != WAVE8_SAUK_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} funnel cohort changed")
    return {"exact_label_rows": 4, "shared_label_rows": 0, "sole_blocker_rows": 4}


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        value = row.get(field)
        try:
            if value is not None:
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


_DUPLICATE_MATCH_KEYS = {
    (year, alias)
    for audit in WAVE8_SAUK_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
}


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {normalize_label(row.get("name"))}
    aliases = row.get("aliases")
    if isinstance(aliases, list):
        names.update(normalize_label(alias) for alias in aliases)
    return names - {""}


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_sauk_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on future twins and pin adjacent actor/spelling boundaries."""

    validate_wave8_sauk_queue_contracts(hced_rows)
    hced_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        hced_by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, disposition in WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS.items():
        rows = hced_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one adjacent HCED row {candidate_id}, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if canonical_hced_row_sha256(row) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} adjacent HCED row changed: {candidate_id}")
        labels = {
            normalize_label(row.get("side_1_raw")),
            normalize_label(row.get("side_2_raw")),
        }
        if disposition["literal_label"] not in labels:
            raise ValueError(f"{_LANE_NAME} adjacent literal label changed: {candidate_id}")

    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_SAUK_EXPECTED_CANDIDATE_IDS
        and _is_probable_twin(row)
    )
    if hced_twins:
        raise ValueError(f"{_LANE_NAME} unreviewed HCED twin(s): {hced_twins}")
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    if iwbd_twins:
        raise ValueError(f"{_LANE_NAME} unreviewed IWBD twin(s): {iwbd_twins}")
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_SAUK_CONTRACT_IDS
        and _is_probable_twin(event)
    )
    if release_twins:
        raise ValueError(f"{_LANE_NAME} unreviewed existing-release twin(s): {release_twins}")
    return {
        "adjacent_hced_dispositions": len(WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS),
        "cross_lane_dispositions": len(WAVE8_SAUK_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": 0,
        "hced_duplicate_dispositions": 0,
        "integration_dispositions": len(WAVE8_SAUK_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(WAVE8_SAUK_IWBD_ZERO_OVERLAP_AUDIT),
    }


def install_wave8_sauk_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SAUK_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_sauk_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SAUK_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SAUK_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SAUK_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_sauk_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_sauk_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SAUK_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_sauk_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (*WAVE8_SAUK_CONTRACTS.values(), *WAVE8_SAUK_HOLDS.values())
            ).items()
        )
    )


def wave8_sauk_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_hced_dispositions": len(WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS),
        "country_quarantine_additions": 0,
        "cross_lane_dispositions": len(WAVE8_SAUK_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": 0,
        "hced_duplicate_dispositions": 0,
        "holds": len(WAVE8_SAUK_HOLDS),
        "integration_dispositions": len(WAVE8_SAUK_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_zero_overlap_candidates": len(WAVE8_SAUK_IWBD_ZERO_OVERLAP_AUDIT),
        "new_entities": len(WAVE8_SAUK_ENTITIES),
        "new_sources": len(WAVE8_SAUK_SOURCES),
        "newly_rated_events": len(WAVE8_SAUK_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(WAVE8_SAUK_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_SAUK_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_SAUK_EXPECTED_CANDIDATE_IDS),
        "terminal_exclusions": 0,
    }


def wave8_sauk_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_SAUK_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_SAUK_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_sauk_row_dispositions() -> dict[str, str]:
    _validate_static()
    return dict(sorted(WAVE8_SAUK_ROW_DISPOSITIONS.items()))


def wave8_sauk_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_sauk_counts(),
        "cohorts": wave8_sauk_cohort_counts(),
        "final_audit_signature": WAVE8_SAUK_FINAL_AUDIT_SIGNATURE,
        "hold_ids": sorted(WAVE8_SAUK_HOLD_IDS),
        "promoted_candidate_ids": sorted(WAVE8_SAUK_CONTRACT_IDS),
        "adjacent_hced_candidate_ids": sorted(WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS),
    }
