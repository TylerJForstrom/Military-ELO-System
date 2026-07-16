"""Candidate-keyed Wave 8 audit for HCED's exact ``Kiowa Indians`` label.

The five locked rows span two different wars and several distinct formations.
This lane therefore installs only event- or campaign-bounded forces.  It never
creates a generic Kiowa identity, never transfers a rating to a modern people,
and leaves the contradictory Lost Valley outcome unknown rather than making it
a draw.
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
    "WAVE8_KIOWA_CONTRACT_IDS",
    "WAVE8_KIOWA_CONTRACTS",
    "WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS",
    "WAVE8_KIOWA_ENTITIES",
    "WAVE8_KIOWA_EXPECTED_CANDIDATE_IDS",
    "WAVE8_KIOWA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_KIOWA_HOLD_IDS",
    "WAVE8_KIOWA_HOLDS",
    "WAVE8_KIOWA_INTEGRATION_DISPOSITIONS",
    "WAVE8_KIOWA_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_KIOWA_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_KIOWA_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_KIOWA_OUTCOME_OVERRIDES",
    "WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS",
    "WAVE8_KIOWA_RESERVED_IDS",
    "WAVE8_KIOWA_SOURCES",
    "install_wave8_kiowa_entities",
    "install_wave8_kiowa_sources",
    "promote_wave8_kiowa_contracts",
    "validate_wave8_kiowa_integration_dispositions",
    "validate_wave8_kiowa_queue_contracts",
    "wave8_kiowa_audit_signature",
    "wave8_kiowa_cohort_counts",
    "wave8_kiowa_counts",
    "wave8_kiowa_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Kiowa exact-label audit"
_EVENT_ID_PREFIX = "hced_wave8_kiowa_"
_MODULE_OWNER = "wave8_kiowa"

_LITTLE_WICHITA_KIOWA = "kicking_bird_kiowa_war_party_little_wichita_1870"
_LITTLE_WICHITA_CAVALRY = "mclellan_sixth_cavalry_detachment_1870"
_LYMAN_BUFFALO_WARRIORS = (
    "lyman_buffalo_wallow_kiowa_comanche_warriors_1874"
)
_LYMAN_ESCORT = "lyman_supply_train_escort_1874"
_BUFFALO_DETAIL = "buffalo_wallow_dispatch_detail_1874"
_PALO_DURO_WARRIORS = "palo_duro_comanche_kiowa_cheyenne_war_parties_1874"
_PALO_DURO_COLUMN = "mackenzie_fourth_cavalry_tonkawa_column_1874"


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


WAVE8_KIOWA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_kiowa_tribe_history",
        "History of the Kiowa Tribe",
        "https://www.kiowatribe.org/about-us",
        "Kiowa Tribe",
        "official_tribal_history",
        "kiowa_tribe_history",
    ),
    _source(
        "wave8_kiowa_tsha_little_wichita",
        "Little Wichita River, Battle of the",
        "https://www.tshaonline.org/handbook/entries/little-wichita-river-battle-of-the",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "tsha_little_wichita",
        outcome=True,
    ),
    _source(
        "wave8_kiowa_tbh_frontier_timeline",
        "Timeline of Texas and the Western Frontier, 1866-1875",
        "https://www.texasbeyondhistory.net/forts/66-75.html",
        "Texas Archeological Research Laboratory, University of Texas at Austin",
        "university_public_history",
        "texas_beyond_history_frontier_timeline",
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_tsha_red_river_war",
        "Red River War",
        "https://www.tshaonline.org/handbook/entries/red-river-war",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "tsha_red_river_war",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_tsha_lone_wolf",
        "Lone Wolf",
        "https://www.tshaonline.org/handbook/entries/lone-wolf",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "tsha_lone_wolf",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_tsha_lost_valley",
        "Lost Valley",
        "https://www.tshaonline.org/handbook/entries/lost-valley",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "tsha_lost_valley",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_texas_ranger_jones",
        "John B. Jones, Texas Ranger Hall of Fame",
        "https://www.texasranger.org/Hall-of-Fame/Jones-John",
        "Texas Ranger Hall of Fame and Museum",
        "institutional_history",
        "texas_ranger_museum_jones",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_tbh_red_river_battles",
        "Red River War: The Battles",
        "https://www.texasbeyondhistory.net/redriver/battles.html",
        "Texas Archeological Research Laboratory, University of Texas at Austin",
        "university_archaeology_history",
        "texas_beyond_history_red_river_battles",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_thc_red_river_guide",
        "Red River War of 1874-1875: Clash of Cultures in the Texas Panhandle",
        "https://www.thc.texas.gov/public/upload/publications/red-river-war-2021.pdf",
        "Texas Historical Commission",
        "government_public_history",
        "texas_historical_commission_red_river_guide",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_nps_red_river_nrhp",
        "Battle Sites of the Red River War in the Texas Panhandle, 1874-1875",
        "https://npgallery.nps.gov/NRHP/GetAsset/NRHP/64500626_text",
        "U.S. National Park Service and Texas Historical Commission",
        "national_register_multiple_property_documentation",
        "nps_red_river_battle_sites_nrhp",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_tsha_lyman",
        "Lyman's Wagontrain",
        "https://www.tshaonline.org/handbook/entries/lymans-wagontrain",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "tsha_lymans_wagontrain",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_tsha_palo_duro",
        "Palo Duro Canyon, Battle of",
        "https://www.tshaonline.org/handbook/entries/palo-duro-canyon-battle-of",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "tsha_palo_duro",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_tpwd_palo_duro",
        "Palo Duro Canyon State Park History",
        "https://tpwd.texas.gov/state-parks/palo-duro-canyon/history",
        "Texas Parks and Wildlife Department",
        "government_site_history",
        "tpwd_palo_duro_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_army_lawton",
        "Two Decades on the Frontier: Henry W. Lawton",
        (
            "https://history.army.mil/Portals/143/Images/Publications/"
            "ArmyHistoryMag/pdf/20002009/AH63%28W%29.pdf?"
            "ver=kRfbRJG0lJ6qYd8u3mb3aQ%3D%3D"
        ),
        "U.S. Army Center of Military History",
        "official_military_history",
        "army_history_lawton_frontier",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kiowa_tribe_palo_duro_150",
        "Successful Commemoration of the Battle of Palo Duro Canyon",
        (
            "https://www.kiowatribe.org/sites/default/files/inline-files/"
            "September%202024%20Newsletter.pdf"
        ),
        "Kiowa Tribe",
        "official_tribal_commemoration",
        "kiowa_tribe_palo_duro_commemoration",
        crosscheck=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start: int,
    end: int,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start,
        "end_year": end,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No rating is inherited by a constituent nation, ethnic label, "
            "reservation population, descendant community, later force, or modern "
            "state."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_KIOWA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _LITTLE_WICHITA_KIOWA,
        "Kicking Bird's Kiowa war party at the Little Wichita River (1870)",
        "event_bounded_war_party",
        1870,
        1870,
        "Little Wichita River, Texas",
        ["wave8_kiowa_tribe_history", "wave8_kiowa_tsha_little_wichita"],
        (
            "Bounded to Kicking Bird's approximately one-hundred-person fighting "
            "party in the 12 July engagement; peaceful Kiowa factions and the "
            "whole Kiowa people are outside the identity."
        ),
    ),
    _entity(
        _LITTLE_WICHITA_CAVALRY,
        "McLellan's Sixth Cavalry detachment at the Little Wichita River (1870)",
        "event_bounded_military_detachment",
        1870,
        1870,
        "Little Wichita River, Texas",
        ["wave8_kiowa_tbh_frontier_timeline", "wave8_kiowa_tsha_little_wichita"],
        (
            "Bounded to Captain Curwen B. McLellan's pursued field detachment in "
            "the 12 July engagement, not the United States Army as a timeless actor."
        ),
    ),
    _entity(
        _LYMAN_BUFFALO_WARRIORS,
        "Kiowa-Comanche warriors linking Lyman's train and Buffalo Wallow (1874)",
        "campaign_bounded_allied_war_party",
        1874,
        1874,
        "Upper Washita and Gageby Creek, Southern Plains",
        [
            "wave8_kiowa_nps_red_river_nrhp",
            "wave8_kiowa_tbh_red_river_battles",
            "wave8_kiowa_tsha_lone_wolf",
        ],
        (
            "Bounded to the Kiowa-Comanche force at Lyman's 9-12 September siege "
            "and the approximately 125 warriors directly reported leaving that "
            "siege before the separate Buffalo Wallow engagement. The continuity "
            "is attested only across these linked actions."
        ),
    ),
    _entity(
        _LYMAN_ESCORT,
        "Wyllys Lyman's supply-train escort (1874)",
        "event_bounded_military_escort",
        1874,
        1874,
        "Upper Washita, Southern Plains",
        [
            "wave8_kiowa_nps_red_river_nrhp",
            "wave8_kiowa_tbh_red_river_battles",
            "wave8_kiowa_tsha_lyman",
        ],
        (
            "Bounded to Lyman's infantry, cavalry, armed teamsters, and defended "
            "wagon train during the 9-14 September siege."
        ),
    ),
    _entity(
        _BUFFALO_DETAIL,
        "Dixon-Chapman Sixth Cavalry dispatch detail at Buffalo Wallow (1874)",
        "event_bounded_dispatch_detail",
        1874,
        1874,
        "Gageby Creek-Washita divide, Texas Panhandle",
        ["wave8_kiowa_tbh_red_river_battles", "wave8_kiowa_thc_red_river_guide"],
        (
            "Bounded to civilian scouts Billy Dixon and Amos Chapman and the four "
            "Sixth Cavalry soldiers surrounded on 12 September."
        ),
    ),
    _entity(
        _PALO_DURO_WARRIORS,
        "Comanche-Kiowa-Cheyenne defending war parties at Palo Duro (1874)",
        "event_bounded_allied_war_parties",
        1874,
        1874,
        "Palo Duro Canyon, Texas",
        [
            "wave8_kiowa_tribe_palo_duro_150",
            "wave8_kiowa_tpwd_palo_duro",
            "wave8_kiowa_tsha_palo_duro",
        ],
        (
            "Bounded to the armed war parties that resisted Mackenzie's 28 "
            "September attack. Families, villages, prisoners, and noncombatants in "
            "the canyon are expressly outside the rated formation."
        ),
    ),
    _entity(
        _PALO_DURO_COLUMN,
        "Mackenzie's Fourth Cavalry-Tonkawa column at Palo Duro (1874)",
        "event_bounded_allied_column",
        1874,
        1874,
        "Palo Duro Canyon, Texas",
        [
            "wave8_kiowa_army_lawton",
            "wave8_kiowa_tpwd_palo_duro",
            "wave8_kiowa_tsha_palo_duro",
        ],
        (
            "Bounded to Colonel Ranald Mackenzie's Fourth Cavalry field column and "
            "the directly attested Tonkawa scouts in the 28 September action."
        ),
    ),
)


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


_ROW_HASHES = {
    "hced-Buffalo Wallow1874-1": (
        "494fd42f8f696f5126c97b3f030a8b24d9a386458c58d453d930fb1a2c16b284"
    ),
    "hced-Little Rock1870-1": (
        "038386b0a8e4561b58ac1d8dd8716942a59a53079bd20bbd386fea79413dd1c1"
    ),
    "hced-Lost Valley, Texas1874-1": (
        "d53373b3c2cbd2954892793066130bd1c057362e297175c9811590d7e68dc13e"
    ),
    "hced-Lymans Wagon Train1874-1": (
        "3d6612a05634fb9b3604d489ec260fbaf12f828ec80e65c70a1ab5f493c1eea5"
    ),
    "hced-Palo Duro1874-1": (
        "63bd54e335245dda179752a1cdc14d620403eed16873081bbf5cc44e0ba27efb"
    ),
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
) -> dict[str, Any]:
    source_by_id = {str(source["id"]): source for source in WAVE8_KIOWA_SOURCES}
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "audit_note": audit_note,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
    }


WAVE8_KIOWA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Little Rock1870-1": _contract(
        "hced-Little Rock1870-1",
        _canonical(
            "Battle of the Little Wichita River",
            1870,
            "12 July 1870",
        ),
        "little_wichita_campaign_1870",
        [_LITTLE_WICHITA_KIOWA],
        [_LITTLE_WICHITA_CAVALRY],
        [
            "wave8_kiowa_tbh_frontier_timeline",
            "wave8_kiowa_tribe_history",
            "wave8_kiowa_tsha_little_wichita",
        ],
        ["wave8_kiowa_tsha_little_wichita"],
        (
            "The raw 'Little Rock' label is corrected to the Little Wichita River "
            "engagement. Kicking Bird's bounded war party outmaneuvered and drove "
            "McLellan's Sixth Cavalry detachment into retreat. No result is assigned "
            "to the Kiowa people generally, and the uncertain raw point is withheld."
        ),
        confidence=0.94,
    ),
    "hced-Lymans Wagon Train1874-1": _contract(
        "hced-Lymans Wagon Train1874-1",
        _canonical(
            "Battle of Lyman's Wagon Train",
            1874,
            "9-14 September 1874",
            date_precision="day_range",
        ),
        "red_river_war_lyman_buffalo_actions_1874",
        [_LYMAN_ESCORT],
        [_LYMAN_BUFFALO_WARRIORS],
        [
            "wave8_kiowa_nps_red_river_nrhp",
            "wave8_kiowa_tbh_red_river_battles",
            "wave8_kiowa_tsha_lone_wolf",
            "wave8_kiowa_tsha_lyman",
        ],
        ["wave8_kiowa_tbh_red_river_battles", "wave8_kiowa_tsha_lyman"],
        (
            "The five-day event is the defended train and its failed siege, not "
            "the Red River War as a whole. Lyman's skirmish line repulsed the main "
            "assault, the besiegers abandoned the action, and the train rejoined "
            "Miles. The raw Oklahoma point is far from the reviewed battle area and "
            "is withheld."
        ),
        confidence=0.91,
    ),
    "hced-Buffalo Wallow1874-1": _contract(
        "hced-Buffalo Wallow1874-1",
        _canonical(
            "Battle of Buffalo Wallow",
            1874,
            "12 September 1874",
        ),
        "red_river_war_lyman_buffalo_actions_1874",
        [_BUFFALO_DETAIL],
        [_LYMAN_BUFFALO_WARRIORS],
        ["wave8_kiowa_tbh_red_river_battles", "wave8_kiowa_thc_red_river_guide"],
        ["wave8_kiowa_tbh_red_river_battles", "wave8_kiowa_thc_red_river_guide"],
        (
            "This is a separate dispatch-detail action on the day warriors began "
            "leaving Lyman's siege. The six defenders held their position until the "
            "attackers broke off and the surviving detail was recovered. The "
            "event uses the directly attested Kiowa-Comanche attackers, not HCED's "
            "Kiowa-only shorthand; its distant Oklahoma point is withheld."
        ),
        confidence=0.88,
    ),
    "hced-Palo Duro1874-1": _contract(
        "hced-Palo Duro1874-1",
        _canonical(
            "Battle of Palo Duro Canyon",
            1874,
            "28 September 1874",
        ),
        "red_river_war_palo_duro_1874",
        [_PALO_DURO_COLUMN],
        [_PALO_DURO_WARRIORS],
        [
            "wave8_kiowa_army_lawton",
            "wave8_kiowa_tribe_palo_duro_150",
            "wave8_kiowa_tbh_red_river_battles",
            "wave8_kiowa_tpwd_palo_duro",
            "wave8_kiowa_tsha_palo_duro",
        ],
        [
            "wave8_kiowa_army_lawton",
            "wave8_kiowa_tbh_red_river_battles",
            "wave8_kiowa_tpwd_palo_duro",
            "wave8_kiowa_tsha_palo_duro",
        ],
        (
            "Mackenzie's Fourth Cavalry and Tonkawa column defeated the armed "
            "Comanche, Kiowa, and Cheyenne resistance in the canyon. The rated "
            "opponent excludes families and noncombatants; captured villages, food, "
            "and horses are evidence of the tactical result, not extra Elo events. "
            "Because the action covered multiple canyon skirmishes and the National "
            "Register study did not verify a precise Palo Duro site, the raw point "
            "is withheld."
        ),
        confidence=0.96,
    ),
}


WAVE8_KIOWA_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Lost Valley, Texas1874-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Lost Valley, Texas1874-1"],
        "canonical_event": _canonical(
            "Lost Valley Fight",
            1874,
            "12 July 1874",
        ),
        "disposition": "hold",
        "hold_category": "contradictory_tactical_outcome_evidence",
        "reviewed_outcome": "unknown",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_actor_description": [
            "Lone Wolf's Kiowa-led war party, with composition reported differently",
            "John B. Jones's Texas Frontier Battalion detachment",
            "late Tenth Cavalry relief element in some accounts",
        ],
        "reviewed_granularity": "engagement",
        "hold_reason": (
            "The sources agree on a fought 12 July engagement but not on a unique "
            "tactical victor or even the complete coalition. The Lone Wolf and Red "
            "River War accounts emphasize the Rangers' losses, horse losses, and "
            "need for rescue; the Lost Valley and Ranger institutional accounts "
            "describe the Rangers as holding out or dispersing the attackers. The "
            "HCED Kiowa win is therefore not promoted, reversed, or relabelled as a "
            "draw. Unknown remains unknown pending stronger adjudication."
        ),
        "evidence_refs": [
            "wave8_kiowa_texas_ranger_jones",
            "wave8_kiowa_tsha_lone_wolf",
            "wave8_kiowa_tsha_lost_valley",
            "wave8_kiowa_tsha_red_river_war",
        ],
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "provisional_hced_hold",
        },
    }
}


WAVE8_KIOWA_CONTRACT_IDS = frozenset(WAVE8_KIOWA_CONTRACTS)
WAVE8_KIOWA_HOLD_IDS = frozenset(WAVE8_KIOWA_HOLDS)
WAVE8_KIOWA_RESERVED_IDS = WAVE8_KIOWA_CONTRACT_IDS | WAVE8_KIOWA_HOLD_IDS
WAVE8_KIOWA_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


# Every promoted raw coordinate is either demonstrably displaced or too precise
# for the reviewed event boundary. The valid modern-country field is retained.
WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS = frozenset(WAVE8_KIOWA_CONTRACT_IDS)
WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_KIOWA_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS,
}


# The locked IWBD snapshot has no same-name/year twin for any reviewed row.
WAVE8_KIOWA_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_KIOWA_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Buffalo Wallow1874-1": {
        "aliases": ("battle of buffalo wallow", "buffalo wallow"),
        "years": (1874, 1874),
    },
    "hced-Little Rock1870-1": {
        "aliases": (
            "battle of little wichita river",
            "battle of the little wichita river",
            "little wichita river",
        ),
        "years": (1870, 1870),
    },
    "hced-Lost Valley, Texas1874-1": {
        "aliases": ("lost valley", "lost valley fight"),
        "years": (1874, 1874),
    },
    "hced-Lymans Wagon Train1874-1": {
        "aliases": (
            "battle of lymans wagon train",
            "lymans wagon train",
            "upper washita",
        ),
        "years": (1874, 1874),
    },
    "hced-Palo Duro1874-1": {
        "aliases": ("battle of palo duro canyon", "palo duro", "palo duro canyon"),
        "years": (1874, 1874),
    },
}


# The locked Adobe Walls row is a different June engagement in the same war;
# Buffalo Wallow is separately rated even though its attackers came from the
# still-distinct Lyman siege. These pins prevent a future umbrella dedup.
WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Adobe Walls1874-1": {
        "raw_row_sha256": (
            "39f7628115b70c14c5dfa50d5bc142b3e52c377352431a8faf561b105237daa5"
        ),
        "disposition": "distinct_unowned_engagement",
        "relationship": "same_campaign_distinct_earlier_engagement",
        "owner_module": None,
        "reason": (
            "Second Adobe Walls occurred on 27 June, months before the Lyman, "
            "Buffalo Wallow, and Palo Duro actions. It is not a duplicate or a "
            "campaign umbrella and remains outside this exact-label lane because "
            "its full Comanche-Kiowa-Cheyenne-Arapaho coalition needs its own audit."
        ),
        "evidence_refs": [
            "wave8_kiowa_thc_red_river_guide",
            "wave8_kiowa_tsha_red_river_war",
        ],
    },
    "hced-Buffalo Wallow1874-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Buffalo Wallow1874-1"],
        "related_hced_candidate_id": "hced-Lymans Wagon Train1874-1",
        "related_raw_row_sha256": _ROW_HASHES["hced-Lymans Wagon Train1874-1"],
        "disposition": "distinct_linked_engagements",
        "relationship": "shared_attested_warrior_group_separate_battlefields",
        "owner_module": _MODULE_OWNER,
        "reason": (
            "About 125 warriors left the Lyman siege and then encountered the six-"
            "person dispatch detail at Buffalo Wallow. Shared personnel justify one "
            "short campaign identity; different objectives, locations, and event "
            "boundaries require two Elo events."
        ),
        "evidence_refs": [
            "wave8_kiowa_nps_red_river_nrhp",
            "wave8_kiowa_tbh_red_river_battles",
        ],
    },
}


# Existing Comanche and Cheyenne lanes own no candidate in this exact Kiowa
# inventory. Shared tribal components are formation membership, not duplicate
# event ownership and do not open an ethnic rating bridge.
WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "wave8_algiers_cheyenne": {
        "disposition": "shared_component_not_duplicate",
        "other_module": "wave8_algiers_cheyenne",
        "owned_candidate_ids": ["hced-Palo Duro1874-1"],
        "shared_component": "Southern Cheyenne war parties at Palo Duro",
        "reason": (
            "The Cheyenne audit owns different HCED rows. Palo Duro's exact mixed "
            "formation is owned here and creates no generic Cheyenne identity."
        ),
    },
    "wave8_comanche": {
        "disposition": "shared_component_not_duplicate",
        "other_module": "wave8_comanche",
        "owned_candidate_ids": [
            "hced-Buffalo Wallow1874-1",
            "hced-Lymans Wagon Train1874-1",
            "hced-Palo Duro1874-1",
        ],
        "shared_component": "Comanche participants in exact mixed formations",
        "reason": (
            "The Comanche audit owns different HCED rows. These exact linked and "
            "event-bounded mixed formations remain Kiowa-lane candidate owners and "
            "create no generic Comanche identity."
        ),
    },
}


WAVE8_KIOWA_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"related_hced:{candidate_id}": disposition
        for candidate_id, disposition in WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS.items()
    },
    **{
        f"cross_lane:{module}": disposition
        for module, disposition in WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS.items()
    },
}


# All four promoted orientations agree with HCED and direct evidence.
WAVE8_KIOWA_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_KIOWA_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_KIOWA_ENTITIES,
        "expected_candidate_ids": sorted(WAVE8_KIOWA_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_KIOWA_HOLDS,
        "integration_dispositions": WAVE8_KIOWA_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_KIOWA_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_KIOWA_IWBD_ZERO_OVERLAP_AUDIT,
        "outcome_overrides": WAVE8_KIOWA_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS,
        "sources": WAVE8_KIOWA_SOURCES,
    }


def wave8_kiowa_audit_signature() -> str:
    """Return the immutable digest of the complete Kiowa audit state."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_KIOWA_FINAL_AUDIT_SIGNATURE = (
    "0fdf31c406a8b64065daa1d9854831c7e3a27b3696004547dc47fb210bde4330"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_KIOWA_CONTRACTS), len(WAVE8_KIOWA_HOLDS)) != (4, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_KIOWA_ENTITIES), len(WAVE8_KIOWA_SOURCES)) != (7, 15):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_KIOWA_RESERVED_IDS != WAVE8_KIOWA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_KIOWA_CONTRACT_IDS & WAVE8_KIOWA_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if wave8_kiowa_audit_signature() != WAVE8_KIOWA_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_KIOWA_SOURCES}
    if len(source_by_id) != len(WAVE8_KIOWA_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_KIOWA_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_KIOWA_ENTITIES}
    if len(entity_by_id) != len(WAVE8_KIOWA_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "comanche",
        "comanche indians",
        "kiowa",
        "kiowa indians",
        "kiowa tribe",
        "southern cheyenne",
        "united states",
    }
    for entity in WAVE8_KIOWA_ENTITIES:
        low = int(entity["start_year"])
        high = int(entity["end_year"])
        if low > high or entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity is not tightly bounded")
        if str(entity["name"]).casefold() in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic identity")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern" not in note:
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_KIOWA_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (side_1 | side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        used_entities.update(side_1 | side_2)
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        for entity_id in side_1 | side_2:
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= low <= high <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"] is not True
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
        if not outcomes or not _is_sorted_unique(outcomes) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome families drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")

    hold = WAVE8_KIOWA_HOLDS["hced-Lost Valley, Texas1874-1"]
    if (
        hold["raw_row_sha256"] != _ROW_HASHES["hced-Lost Valley, Texas1874-1"]
        or hold["disposition"] != "hold"
        or hold["reviewed_outcome"] != "unknown"
        or hold["result_type"] != "unknown"
        or hold["unknown_is_never_draw"] is not True
        or "winner_side" in hold
        or "side_1_entity_ids" in hold
        or "side_2_entity_ids" in hold
    ):
        raise ValueError(f"{_LANE_NAME} Lost Valley hold became rateable")
    if "draw" not in str(hold["hold_reason"]).casefold():
        raise ValueError(f"{_LANE_NAME} Lost Valley unknown/draw policy drifted")
    if not set(map(str, hold["evidence_refs"])) <= set(source_by_id):
        raise ValueError(f"{_LANE_NAME} hold names an unknown source")
    used_sources.update(map(str, hold["evidence_refs"]))

    used_sources.update(
        source_id
        for entity in WAVE8_KIOWA_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    for disposition in WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS.values():
        if not set(map(str, disposition["evidence_refs"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} related HCED evidence drifted")
        used_sources.update(map(str, disposition["evidence_refs"]))
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")

    if WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS != WAVE8_KIOWA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if WAVE8_KIOWA_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} acquired an outcome override")
    if WAVE8_KIOWA_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an IWBD duplicate")
    if set(WAVE8_KIOWA_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_KIOWA_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} IWBD negative audit is incomplete")
    if set(WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS) != {
        "hced-Adobe Walls1874-1",
        "hced-Buffalo Wallow1874-1",
    }:
        raise ValueError(f"{_LANE_NAME} related HCED inventory changed")
    if set(WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS) != {
        "wave8_algiers_cheyenne",
        "wave8_comanche",
    }:
        raise ValueError(f"{_LANE_NAME} cross-lane inventory changed")
    if len(WAVE8_KIOWA_INTEGRATION_DISPOSITIONS) != 4:
        raise ValueError(f"{_LANE_NAME} integration inventory changed")


def _is_exact_kiowa_label(value: Any) -> bool:
    return normalize_label(value) == "kiowa indians"


def validate_wave8_kiowa_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate every exact-label row and its canonical raw-row fingerprint."""

    _validate_static()
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_KIOWA_CONTRACTS,
        WAVE8_KIOWA_HOLDS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_kiowa_label(row.get("side_1_raw"))
        or _is_exact_kiowa_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_KIOWA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Kiowa Indians inventory changed: {sorted(exact_ids)}"
        )
    return counts


def _date_year(value: Any) -> int | None:
    text = str(value or "")
    if len(text) < 4 or not text[:4].isdigit():
        return None
    return int(text[:4])


def validate_wave8_kiowa_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin linked HCED boundaries, cross-lane ownership, and IWBD nonoverlap."""

    validate_wave8_kiowa_queue_contracts(hced_rows)
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    adobe_id = "hced-Adobe Walls1874-1"
    adobe_rows = by_id.get(adobe_id, [])
    if len(adobe_rows) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one related HCED row {adobe_id}, "
            f"found {len(adobe_rows)}"
        )
    expected_adobe_hash = WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS[adobe_id][
        "raw_row_sha256"
    ]
    if canonical_hced_row_sha256(adobe_rows[0]) != expected_adobe_hash:
        raise ValueError(f"{_LANE_NAME} related Adobe Walls fingerprint changed")

    # Local imports avoid coupling module initialization while pinning ownership.
    from .wave8_algiers_cheyenne import (
        WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS,
    )
    from .wave8_comanche import WAVE8_COMANCHE_RESERVED_IDS

    other_owners = {
        "wave8_algiers_cheyenne": set(WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS),
        "wave8_comanche": set(WAVE8_COMANCHE_RESERVED_IDS),
    }
    for module, owned_ids in other_owners.items():
        overlap = WAVE8_KIOWA_RESERVED_IDS & owned_ids
        if overlap:
            raise ValueError(
                f"{_LANE_NAME} cross-lane candidate ownership collision with "
                f"{module}: {sorted(overlap)}"
            )

    normalized_audit = {
        candidate_id: {
            "aliases": {normalize_label(alias) for alias in item["aliases"]},
            "years": tuple(map(int, item["years"])),
        }
        for candidate_id, item in WAVE8_KIOWA_IWBD_ZERO_OVERLAP_AUDIT.items()
    }
    for row in iwbd_rows:
        start = _date_year(row.get("start_date"))
        end = _date_year(row.get("end_date"))
        if start is None or end is None:
            continue
        name = normalize_label(row.get("name"))
        for hced_id, audit in normalized_audit.items():
            low, high = audit["years"]
            if start <= high and end >= low and name in audit["aliases"]:
                raise ValueError(
                    f"{_LANE_NAME} found unreviewed plausible IWBD overlap "
                    f"{row.get('candidate_id')} for {hced_id}"
                )
    return {
        "cross_lane_hced_dispositions": len(WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS),
        "integration_dispositions": len(WAVE8_KIOWA_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_zero_overlap_candidates": len(WAVE8_KIOWA_IWBD_ZERO_OVERLAP_AUDIT),
        "related_hced_dispositions": len(WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS),
    }


def install_wave8_kiowa_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_KIOWA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_kiowa_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_KIOWA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_kiowa_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_kiowa_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_KIOWA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_kiowa_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_KIOWA_CONTRACTS.values()
            ).items()
        )
    )


def wave8_kiowa_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS),
        "holds": len(WAVE8_KIOWA_HOLDS),
        "integration_dispositions": len(WAVE8_KIOWA_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_KIOWA_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_KIOWA_ENTITIES),
        "new_sources": len(WAVE8_KIOWA_SOURCES),
        "newly_rated_events": len(WAVE8_KIOWA_CONTRACTS),
        "outcome_overrides": len(WAVE8_KIOWA_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_KIOWA_CONTRACTS),
        "related_hced_dispositions": len(WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS),
        "reviewed_hced_rows": len(WAVE8_KIOWA_RESERVED_IDS),
    }


def wave8_kiowa_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return promoted-only location additions for coordinated integration."""

    _validate_static()
    return {
        "country": WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS,
    }
