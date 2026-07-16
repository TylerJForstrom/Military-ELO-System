"""Exact Wave 8 dispositions for HCED's generic Canadian-rebel rows."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

from .common import _slug
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


_LANE_NAME = "Wave 8 Canadian resistance"
WAVE8_CANADIAN_RESISTANCE_FINAL_AUDIT_SIGNATURE = (
    "2c1bb2438f78acd9af6554d6c77eae12eed4fc1497b2ccea7ed4612179e8e270"
)


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    family: str,
    *,
    outcome: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": "official_history",
        "accessed": "2026-07-16",
        "source_family_id": family,
        "evidence_roles": roles,
    }


WAVE8_CANADIAN_RESISTANCE_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_canada_dominion_boundary",
        "The Statute of Westminster and the Dominion of Canada",
        "https://www.canada.ca/en/intergovernmental-affairs/services/federation/statute-westminster.html",
        "Government of Canada",
        "canada_intergovernmental_affairs",
    ),
    _source(
        "wave8_canada_batoche_history",
        "History of Batoche National Historic Site",
        "https://parks.canada.ca/lhn-nhs/sk/batoche/culture/histoire-history",
        "Parks Canada",
        "parks_canada_northwest_resistance",
        outcome=True,
    ),
    _source(
        "wave8_canada_battleford_history",
        "History of Fort Battleford National Historic Site",
        "https://parks.canada.ca/lhn-nhs/sk/battleford/culture/histoire-history",
        "Parks Canada",
        "parks_canada_northwest_resistance",
        outcome=True,
    ),
    _source(
        "wave8_canada_fish_creek_history",
        "Battle of Tourond's Coulee / Fish Creek National Historic Site",
        "https://parks.canada.ca/lhn-nhs/sk/tourond/culture",
        "Parks Canada",
        "parks_canada_northwest_resistance",
        outcome=True,
    ),
    _source(
        "wave8_canada_upper_canada_rebellion",
        "Transforming Relationships, 1815–1902: the Rebellions",
        (
            "https://www.canada.ca/en/department-national-defence/services/"
            "military-history/history-heritage/popular-books/aboriginal-people-"
            "canadian-military/transforming-relationships-1815-1902.html"
        ),
        "Department of National Defence, Canada",
        "canadian_military_history_directorate",
        outcome=True,
    ),
    _source(
        "wave8_canada_montgomery_tavern",
        "History of the 7th Toronto Regiment, Royal Canadian Artillery",
        "https://www.canada.ca/en/army/corporate/4-canadian-division/7-toronto-regiment.html",
        "Canadian Army",
        "canadian_army_unit_history",
        outcome=True,
    ),
)


WAVE8_CANADIAN_RESISTANCE_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "dominion_canada_1867_1931",
        "name": "Dominion of Canada (1867–1931)",
        "kind": "dominion",
        "start_year": 1867,
        "end_year": 1931,
        "region": "North America",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The confederated Dominion from 1867 through the 1931 Statute of "
            "Westminster boundary. No rating is inherited by the pre-Confederation "
            "colonies or the project's post-1931 Canada identity."
        ),
        "source_ids": ["wave8_canada_dominion_boundary"],
    },
    {
        "id": "metis_provisional_government_saskatchewan_1885",
        "name": "Métis Provisional Government of Saskatchewan (1885)",
        "kind": "provisional_government",
        "start_year": 1885,
        "end_year": 1885,
        "region": "North-West Territories",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Conflict-bounded provisional government at Batoche. No rating is "
            "inherited by Métis communities, the 1869–1870 Red River government, "
            "First Nations allies, or any generic Canadian-rebels label."
        ),
        "source_ids": ["wave8_canada_batoche_history"],
    },
    {
        "id": "duck_lake_first_nations_allied_force_1885",
        "name": "First Nations allied force at Duck Lake (1885)",
        "kind": "event_bounded_allied_force",
        "start_year": 1885,
        "end_year": 1885,
        "region": "North-West Territories",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Event-bounded Indigenous participants attested with the Métis at Duck "
            "Lake. No rating is inherited by any nation, band, later engagement, "
            "or umbrella Indigenous identity."
        ),
        "source_ids": ["wave8_canada_battleford_history"],
    },
    {
        "id": "batoche_first_nations_allied_defenders_1885",
        "name": "First Nations allied defenders at Batoche (1885)",
        "kind": "event_bounded_allied_force",
        "start_year": 1885,
        "end_year": 1885,
        "region": "North-West Territories",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Event-bounded First Nations defenders attested at Batoche alongside "
            "the Métis force. No rating is inherited by any nation, band, or later "
            "coalition."
        ),
        "source_ids": ["wave8_canada_batoche_history"],
    },
    {
        "id": "upper_canada_colonial_government_1791_1841",
        "name": "Colonial Government of Upper Canada (1791–1841)",
        "kind": "colony",
        "start_year": 1791,
        "end_year": 1841,
        "region": "North America",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The Upper Canada colonial government and loyal militia. No rating is "
            "inherited by Britain, the Province of Canada, or the later Dominion."
        ),
        "source_ids": [
            "wave8_canada_upper_canada_rebellion",
            "wave8_canada_montgomery_tavern",
        ],
    },
    {
        "id": "mackenzie_upper_canada_rebel_force_1837",
        "name": "Mackenzie's Upper Canada rebel force (1837)",
        "kind": "rebel_force",
        "start_year": 1837,
        "end_year": 1837,
        "region": "Upper Canada",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Event-bounded force rallied by William Lyon Mackenzie near Toronto. "
            "No rating is inherited by later Patriot raiders, Canadian reformers, "
            "or a generic Canadian-rebels identity."
        ),
        "source_ids": [
            "wave8_canada_upper_canada_rebellion",
            "wave8_canada_montgomery_tavern",
        ],
    },
)


def _canonical(name: str, year: int) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "year",
        "granularity": "engagement",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


WAVE8_CANADIAN_RESISTANCE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Batoche1885-1": {
        "raw_row_sha256": "7290e1baed83fdbd7566fdb6d3ac40760ac55794a5c86d51f891f28a56273dec",
        "canonical_event": _canonical("Battle of Batoche", 1885),
        "cohort": "northwest_resistance",
        "side_1_entity_ids": ["dominion_canada_1867_1931"],
        "side_2_entity_ids": [
            "batoche_first_nations_allied_defenders_1885",
            "metis_provisional_government_saskatchewan_1885",
        ],
        "winner_side": 1,
        "war_type": "internal_rebellion",
        "evidence_refs": ["wave8_canada_batoche_history", "wave8_canada_dominion_boundary"],
        "outcome_source_ids": ["wave8_canada_batoche_history"],
        "outcome_source_family_ids": ["parks_canada_northwest_resistance"],
        "source_outcome_override": False,
        "actor_override": "canadian_government_and_exact_resistance_coalition",
        "audit_note": (
            "Parks Canada identifies the Canadian government's only decisive "
            "victory of the campaign and separately attests Métis and First Nations "
            "defenders; the HCED British umbrella is not used."
        ),
    },
    "hced-Duck Lake1885-1": {
        "raw_row_sha256": "b5def48be6e1e2100523709f7573dd7fadbeb91e4fa8fcf1857499dfefae9f9a",
        "canonical_event": _canonical("Battle of Duck Lake", 1885),
        "cohort": "northwest_resistance",
        "side_1_entity_ids": [
            "duck_lake_first_nations_allied_force_1885",
            "metis_provisional_government_saskatchewan_1885",
        ],
        "side_2_entity_ids": ["dominion_canada_1867_1931"],
        "winner_side": 1,
        "war_type": "internal_rebellion",
        "evidence_refs": ["wave8_canada_battleford_history", "wave8_canada_dominion_boundary"],
        "outcome_source_ids": ["wave8_canada_battleford_history"],
        "outcome_source_family_ids": ["parks_canada_northwest_resistance"],
        "source_outcome_override": False,
        "actor_override": "metis_first_nations_coalition_and_canadian_government",
        "audit_note": (
            "Parks Canada records the combined Métis and Indigenous victory over "
            "Canadian forces; neither side is collapsed into HCED's umbrella labels."
        ),
    },
    "hced-Toronto1837-1": {
        "raw_row_sha256": "afbc9e9b202f7146126050d577f4bd3b9e5ecdcd788eaa5287afcf71406edc66",
        "canonical_event": _canonical("Battle of Montgomery's Tavern", 1837),
        "cohort": "upper_canada_rebellion",
        "side_1_entity_ids": ["upper_canada_colonial_government_1791_1841"],
        "side_2_entity_ids": ["mackenzie_upper_canada_rebel_force_1837"],
        "winner_side": 1,
        "war_type": "internal_rebellion",
        "evidence_refs": [
            "wave8_canada_montgomery_tavern",
            "wave8_canada_upper_canada_rebellion",
        ],
        "outcome_source_ids": ["wave8_canada_montgomery_tavern"],
        "outcome_source_family_ids": ["canadian_army_unit_history"],
        "source_outcome_override": False,
        "actor_override": "upper_canada_militia_not_united_kingdom",
        "audit_note": (
            "Canadian military histories identify the loyal militia's defeat and "
            "dispersal of Mackenzie's force at Montgomery's Tavern."
        ),
    },
}


WAVE8_CANADIAN_RESISTANCE_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Battleford1885-1": {
        "raw_row_sha256": "c06df56c06b71a52a32a5d115536a85988c4b544f0260ad494f9f9c0e9d93669",
        "canonical_event": _canonical("Battleford", 1885),
        "hold_category": "distinct_competitive_engagement_unverified",
        "hold_reason": (
            "The official site history describes gathering, negotiation attempts, "
            "movement, and later surrenders, not a distinct Canadian victory at "
            "Battleford matching this row."
        ),
        "evidence_refs": ["wave8_canada_battleford_history"],
    },
    "hced-Fish Creek1885-1": {
        "raw_row_sha256": "5229a305cfef274d60cebcc04f28c98687ff54aa888c0d886d56f52f18672c29",
        "canonical_event": _canonical("Battle of Tourond's Coulee / Fish Creek", 1885),
        "hold_category": "contradictory_outcome_evidence",
        "hold_reason": (
            "Parks Canada pages describe the result both as an indecisive stand-off "
            "and as a short-lived Métis triumph; neither supports HCED's Canadian "
            "victory strongly enough for an Elo result."
        ),
        "evidence_refs": [
            "wave8_canada_batoche_history",
            "wave8_canada_fish_creek_history",
        ],
    },
    "hced-Frenchmans Butte1885-1": {
        "raw_row_sha256": "82ad2e75a0b831294583bfe8a564864fe360fcb3ed7b1a8d2fbf3150b6f71dd2",
        "canonical_event": _canonical("Battle of Frenchman's Butte", 1885),
        "hold_category": "outcome_not_supported_as_victory",
        "hold_reason": (
            "Parks Canada classifies Frenchman's Butte as a stand-off, so HCED's "
            "generic rebel victory is not promoted as either a win or an invented draw."
        ),
        "evidence_refs": ["wave8_canada_batoche_history"],
    },
}


WAVE8_CANADIAN_RESISTANCE_CONTRACT_IDS = frozenset(WAVE8_CANADIAN_RESISTANCE_CONTRACTS)
WAVE8_CANADIAN_RESISTANCE_HOLD_IDS = frozenset(WAVE8_CANADIAN_RESISTANCE_HOLDS)
WAVE8_CANADIAN_RESISTANCE_RESERVED_IDS = (
    WAVE8_CANADIAN_RESISTANCE_CONTRACT_IDS | WAVE8_CANADIAN_RESISTANCE_HOLD_IDS
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def wave8_canadian_resistance_signature() -> str:
    return hashlib.sha256(
        _canonical_json(
            {
                "contracts": WAVE8_CANADIAN_RESISTANCE_CONTRACTS,
                "holds": WAVE8_CANADIAN_RESISTANCE_HOLDS,
            }
        ).encode()
    ).hexdigest()


def _validate_static() -> None:
    if (len(WAVE8_CANADIAN_RESISTANCE_CONTRACTS), len(WAVE8_CANADIAN_RESISTANCE_HOLDS)) != (3, 3):
        raise ValueError("Wave 8 Canadian-resistance disposition inventory changed")
    if wave8_canadian_resistance_signature() != WAVE8_CANADIAN_RESISTANCE_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 Canadian-resistance audit signature changed")
    if WAVE8_CANADIAN_RESISTANCE_CONTRACT_IDS & WAVE8_CANADIAN_RESISTANCE_HOLD_IDS:
        raise ValueError("Wave 8 Canadian-resistance dispositions overlap")
    source_ids = {str(source["id"]) for source in WAVE8_CANADIAN_RESISTANCE_SOURCES}
    for entity in WAVE8_CANADIAN_RESISTANCE_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError("Wave 8 Canadian-resistance identities must be alias-free")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError("Wave 8 Canadian-resistance identity permits inheritance")
        if not set(map(str, entity["source_ids"])) <= source_ids:
            raise ValueError("Wave 8 Canadian-resistance identity names an unknown source")
    for item in {**WAVE8_CANADIAN_RESISTANCE_CONTRACTS, **WAVE8_CANADIAN_RESISTANCE_HOLDS}.values():
        if not set(map(str, item["evidence_refs"])) <= source_ids:
            raise ValueError("Wave 8 Canadian-resistance item names an unknown source")


def validate_wave8_canadian_resistance_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_CANADIAN_RESISTANCE_CONTRACTS,
        WAVE8_CANADIAN_RESISTANCE_HOLDS,
        lane_name=_LANE_NAME,
    )


def install_wave8_canadian_resistance_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_CANADIAN_RESISTANCE_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_canadian_resistance_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_CANADIAN_RESISTANCE_SOURCES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_canadian_resistance_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_canadian_resistance_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_CANADIAN_RESISTANCE_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix="hced_wave8_canadian_resistance_",
    )


def wave8_canadian_resistance_counts() -> dict[str, int]:
    return {
        "holds": len(WAVE8_CANADIAN_RESISTANCE_HOLDS),
        "newly_rated_events": len(WAVE8_CANADIAN_RESISTANCE_CONTRACTS),
        "promotion_contracts": len(WAVE8_CANADIAN_RESISTANCE_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_CANADIAN_RESISTANCE_RESERVED_IDS),
    }
