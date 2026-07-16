"""Exact Wave 8 dispositions for HCED rows labelled ``Cherokee Indians``.

The source label spans unrelated eighteenth-century Cherokee war parties and
an 1839 Texas refugee fighting party.  This lane therefore rates only exact,
event-bounded formations.  It creates no timeless ethnic Cherokee identity,
does not transfer an Elo between the 1760--61 and 1839 conflicts, and does not
turn the compound Fort Prince George violence into an invented result.
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
    "WAVE8_CHEROKEE_CONTRACT_IDS",
    "WAVE8_CHEROKEE_CONTRACTS",
    "WAVE8_CHEROKEE_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS",
    "WAVE8_CHEROKEE_ENTITIES",
    "WAVE8_CHEROKEE_EXCLUSION_IDS",
    "WAVE8_CHEROKEE_EXCLUSIONS",
    "WAVE8_CHEROKEE_EXPECTED_CANDIDATE_IDS",
    "WAVE8_CHEROKEE_FINAL_AUDIT_SIGNATURE",
    "WAVE8_CHEROKEE_HOLD_IDS",
    "WAVE8_CHEROKEE_HOLDS",
    "WAVE8_CHEROKEE_INTEGRATION_DISPOSITIONS",
    "WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_CHEROKEE_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_CHEROKEE_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_CHEROKEE_OUTCOME_OVERRIDES",
    "WAVE8_CHEROKEE_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_CHEROKEE_RESERVED_IDS",
    "WAVE8_CHEROKEE_SOURCES",
    "install_wave8_cherokee_entities",
    "install_wave8_cherokee_sources",
    "promote_wave8_cherokee_contracts",
    "validate_wave8_cherokee_integration_dispositions",
    "validate_wave8_cherokee_queue_contracts",
    "wave8_cherokee_audit_signature",
    "wave8_cherokee_cohort_counts",
    "wave8_cherokee_counts",
    "wave8_cherokee_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Cherokee exact-formation audit"
_EVENT_ID_PREFIX = "hced_wave8_cherokee_"

_ECHOE_1760_CHEROKEE_ID = "first_echoe_cherokee_fighting_force_1760"
_MONTGOMERIE_1760_ID = "montgomerie_british_sc_force_echoe_1760"
_LOUDOUN_CHEROKEE_ID = "fort_loudoun_overhill_cherokee_siege_force_1760"
_LOUDOUN_GARRISON_ID = "fort_loudoun_south_carolina_garrison_1760"
_GRANT_1761_ID = "grant_british_sc_indigenous_allied_force_echoe_1761"
_ECHOE_1761_CHEROKEE_ID = "second_echoe_cherokee_fighting_force_1761"
_SAN_SABA_TEXAS_ID = "burleson_texas_lipan_tonkawa_force_san_saba_1839"
_SAN_SABA_CHEROKEE_ID = "egg_bowles_cherokee_fighting_party_san_saba_1839"


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


WAVE8_CHEROKEE_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_cherokee_ncpedia_etchoe",
        "Etchoe, Battle of",
        "https://www.ncpedia.org/etchoe-battle",
        "NC Government & Heritage Library; University of North Carolina Press",
        "state_library_scholarly_encyclopedia",
        "unc_press_encyclopedia_of_north_carolina",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_cherokee_dncr_echoe_1760",
        "Cherokee Victory (Q-6)",
        "https://www.dncr.nc.gov/blog/2024/01/23/cherokee-victory-q-6",
        "North Carolina Department of Natural and Cultural Resources",
        "state_historical_marker_research",
        "nc_historical_marker_program_q6",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_cherokee_dncr_echoe_1761",
        "Cherokee Defeat (Q-5)",
        "https://www.dncr.nc.gov/blog/2024/01/23/cherokee-defeat-q-5",
        "North Carolina Department of Natural and Cultural Resources",
        "state_historical_marker_research",
        "nc_historical_marker_program_q5",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_cherokee_scencyclopedia_fort_prince_george",
        "Fort Prince George",
        "https://www.scencyclopedia.org/sce/entries/fort-prince-george/",
        "University of South Carolina, Institute for Southern Studies",
        "university_scholarly_encyclopedia",
        "usc_south_carolina_encyclopedia",
    ),
    _source(
        "wave8_cherokee_tn_archaeology_fort_loudoun",
        "Fort Loudoun in Tennessee: 1756-1760",
        (
            "https://www.tn.gov/content/dam/tn/environment/archaeology/"
            "documents/researchseries/arch_rs17_fort_loudoun_2010.pdf"
        ),
        "Tennessee Division of Archaeology",
        "state_archaeology_research_monograph",
        "tennessee_archaeology_research_series_17",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_cherokee_fort_loudoun_state_history",
        "History - Fort Loudoun State Historic Area",
        "https://fortloudoun.com/history/",
        "Fort Loudoun State Historic Area, Tennessee",
        "state_historic_site_history",
        "fort_loudoun_state_historic_area",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_cherokee_ncpedia_french_indian_war",
        "French and Indian War",
        "https://www.ncpedia.org/french-and-indian-war",
        "NC Government & Heritage Library; University of North Carolina Press",
        "state_library_scholarly_encyclopedia",
        "unc_press_french_indian_war_entry",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_cherokee_tsha_cherokee_war",
        "Cherokee War",
        "https://www.tshaonline.org/handbook/entries/cherokee-war",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "texas_state_historical_association_cherokee_war",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_cherokee_unt_indian_allies_thesis",
        "In Justice to Our Indian Allies: The Government of Texas and Her Indian Allies, 1836-1867",
        (
            "https://digital.library.unt.edu/ark:/67531/metadc9010/"
            "m2/1/high_res_d/thesis.pdf"
        ),
        "University of North Texas",
        "institutional_scholarly_thesis_with_primary_report",
        "unt_miller_texas_indian_allies_thesis",
        outcome=True,
        crosscheck=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No rating is inherited by a Cherokee nation, clan, town, modern "
            "tribal government, colonial province, constituent regiment, allied "
            "people, descendant community, or later force."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_CHEROKEE_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _ECHOE_1760_CHEROKEE_ID,
        "Oconostota's Cherokee fighting force at the First Battle of Echoe (1760)",
        "event_bounded_indigenous_force",
        1760,
        "Cherokee Middle Towns, present-day North Carolina",
        ["wave8_cherokee_dncr_echoe_1760", "wave8_cherokee_ncpedia_etchoe"],
        (
            "The warriors directly attested under Oconostota at the 27 June "
            "ambush; this record neither absorbs noncombatants nor opens a "
            "generic Cherokee fallback."
        ),
    ),
    _entity(
        _MONTGOMERIE_1760_ID,
        "Montgomerie's British-South Carolina expedition at Echoe (1760)",
        "event_bounded_colonial_force",
        1760,
        "Cherokee Middle Towns, present-day North Carolina",
        ["wave8_cherokee_dncr_echoe_1760", "wave8_cherokee_ncpedia_etchoe"],
        (
            "The exact expeditionary force of British regulars and South "
            "Carolina provincials led by Archibald Montgomerie at Echoe."
        ),
    ),
    _entity(
        _LOUDOUN_CHEROKEE_ID,
        "Overhill Cherokee siege force at Fort Loudoun (1760)",
        "event_bounded_indigenous_siege_force",
        1760,
        "Overhill Cherokee country, present-day Tennessee",
        [
            "wave8_cherokee_fort_loudoun_state_history",
            "wave8_cherokee_ncpedia_french_indian_war",
            "wave8_cherokee_tn_archaeology_fort_loudoun",
        ],
        (
            "The Overhill warriors directly attested in the March-August siege "
            "that forced the fort's capitulation; the later attack on the "
            "evacuating column is excluded from this identity and result."
        ),
    ),
    _entity(
        _LOUDOUN_GARRISON_ID,
        "South Carolina Independent Company garrison at Fort Loudoun (1760)",
        "event_bounded_colonial_garrison",
        1760,
        "Fort Loudoun, present-day Tennessee",
        [
            "wave8_cherokee_fort_loudoun_state_history",
            "wave8_cherokee_ncpedia_french_indian_war",
            "wave8_cherokee_tn_archaeology_fort_loudoun",
        ],
        (
            "The fort garrison commanded by Paul Demere through the capitulation; "
            "civilian family members and the later attacked evacuation column are "
            "not rated as additional participants."
        ),
    ),
    _entity(
        _GRANT_1761_ID,
        "Grant's British-South Carolina-Indigenous allied force at Echoe (1761)",
        "event_bounded_allied_colonial_force",
        1761,
        "Cherokee Middle Towns, present-day North Carolina",
        ["wave8_cherokee_dncr_echoe_1761", "wave8_cherokee_ncpedia_etchoe"],
        (
            "James Grant's exact battle force, including British regulars, South "
            "Carolina provincials, and the directly attested Catawba, Chickasaw, "
            "and Mohawk allies; no component receives a separate result."
        ),
    ),
    _entity(
        _ECHOE_1761_CHEROKEE_ID,
        "Oconostota's Cherokee fighting force at the Second Battle of Echoe (1761)",
        "event_bounded_indigenous_force",
        1761,
        "Cherokee Middle Towns, present-day North Carolina",
        ["wave8_cherokee_dncr_echoe_1761", "wave8_cherokee_ncpedia_etchoe"],
        (
            "The warriors directly attested under Oconostota in the 10 June "
            "engagement; this is not an Elo continuation from the distinct 1760 "
            "force or from any later Cherokee polity."
        ),
    ),
    _entity(
        _SAN_SABA_TEXAS_ID,
        "Burleson's Republic of Texas-Lipan-Tonkawa force at San Saba (1839)",
        "event_bounded_allied_frontier_force",
        1839,
        "Colorado-San Saba river confluence, Republic of Texas",
        [
            "wave8_cherokee_tsha_cherokee_war",
            "wave8_cherokee_unt_indian_allies_thesis",
        ],
        (
            "Edward Burleson's exact field force, including Republic regulars "
            "and volunteers with Lipan and Tonkawa scouts and battlefield allies."
        ),
    ),
    _entity(
        _SAN_SABA_CHEROKEE_ID,
        "Egg and John Bowles's Cherokee fighting party at San Saba (1839)",
        "event_bounded_refugee_fighting_party",
        1839,
        "Colorado-San Saba river confluence, Republic of Texas",
        [
            "wave8_cherokee_tsha_cherokee_war",
            "wave8_cherokee_unt_indian_allies_thesis",
        ],
        (
            "Only the armed party led by Egg and John Bowles in the Christmas Day "
            "fight is rated. The accompanying women and children, the July Neches "
            "force, and Cherokee governments elsewhere are excluded."
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
    "hced-Etchoe1760-1": (
        "8c358181ecf6f7d6bb5fd598a323fc952cb92385e467ee4f414eb1c72c0011a2"
    ),
    "hced-Etchoe1761-1": (
        "15c96fb694f6bf8619f3bca244fb4b30be6a7b3e43e6add10b96118e361e2223"
    ),
    "hced-Fort Loudoun1760-1": (
        "67a5faafb37b3392bb78aa71c28a1e413f68c24b379ac50566174150bfafdac2"
    ),
    "hced-Fort Prince George1760-1": (
        "40e068d04f40a97e280e15bbeccf5a43f21e61ba9da0a36749ae9ac4543b0a87"
    ),
    "hced-San Saba1839-1": (
        "6f60d4dd80db09397aeacebfd1f6277146e6b182aa2466997782d64e526fd55e"
    ),
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
    source_by_id = {str(source["id"]): source for source in WAVE8_CHEROKEE_SOURCES}
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
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
    }


WAVE8_CHEROKEE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Etchoe1760-1": _contract(
        "hced-Etchoe1760-1",
        _canonical("First Battle of Echoe", 1760, "27 June 1760"),
        "anglo_cherokee_war_1760_1761",
        [_ECHOE_1760_CHEROKEE_ID],
        [_MONTGOMERIE_1760_ID],
        ["wave8_cherokee_dncr_echoe_1760", "wave8_cherokee_ncpedia_etchoe"],
        ["wave8_cherokee_dncr_echoe_1760", "wave8_cherokee_ncpedia_etchoe"],
        (
            "North Carolina's historical program and scholarly encyclopedia agree "
            "that Oconostota's force defeated Montgomerie's British regular and "
            "South Carolina provincial expedition. The raw point is near Franklin, "
            "not the reviewed battlefield south near Tessantee/modern Otto, and is "
            "withheld."
        ),
        confidence=0.93,
    ),
    "hced-Fort Loudoun1760-1": _contract(
        "hced-Fort Loudoun1760-1",
        _canonical(
            "Siege of Fort Loudoun",
            1760,
            "March-7 August 1760; capitulation ended the siege",
            date_precision="month_to_day",
            granularity="siege",
        ),
        "anglo_cherokee_war_1760_1761",
        [_LOUDOUN_CHEROKEE_ID],
        [_LOUDOUN_GARRISON_ID],
        [
            "wave8_cherokee_fort_loudoun_state_history",
            "wave8_cherokee_ncpedia_french_indian_war",
            "wave8_cherokee_tn_archaeology_fort_loudoun",
        ],
        [
            "wave8_cherokee_fort_loudoun_state_history",
            "wave8_cherokee_ncpedia_french_indian_war",
            "wave8_cherokee_tn_archaeology_fort_loudoun",
        ],
        (
            "The competitive result is the months-long siege ending in the South "
            "Carolina garrison's capitulation. The attack on the evacuating column "
            "three days later is a separate massacre episode and is not emitted as "
            "another result. The fort-site coordinate and country are retained."
        ),
        confidence=0.94,
    ),
    "hced-Etchoe1761-1": _contract(
        "hced-Etchoe1761-1",
        _canonical("Second Battle of Echoe", 1761, "10 June 1761"),
        "anglo_cherokee_war_1760_1761",
        [_GRANT_1761_ID],
        [_ECHOE_1761_CHEROKEE_ID],
        ["wave8_cherokee_dncr_echoe_1761", "wave8_cherokee_ncpedia_etchoe"],
        ["wave8_cherokee_dncr_echoe_1761", "wave8_cherokee_ncpedia_etchoe"],
        (
            "The reviewed sources identify Grant's mixed British, provincial, and "
            "Indigenous-allied force, nearly five hours of fighting, and the "
            "Cherokee withdrawal. The shared raw Etchoe point does not distinguish "
            "this battlefield from the separate 1760 site and is withheld."
        ),
        confidence=0.93,
    ),
    "hced-San Saba1839-1": _contract(
        "hced-San Saba1839-1",
        _canonical(
            "Fight near the mouth of the San Saba River",
            1839,
            "25 December 1839",
        ),
        "texas_cherokee_san_saba_1839",
        [_SAN_SABA_TEXAS_ID],
        [_SAN_SABA_CHEROKEE_ID],
        [
            "wave8_cherokee_tsha_cherokee_war",
            "wave8_cherokee_unt_indian_allies_thesis",
        ],
        [
            "wave8_cherokee_tsha_cherokee_war",
            "wave8_cherokee_unt_indian_allies_thesis",
        ],
        (
            "The TSHA account and UNT study of Burleson's report identify a brisk "
            "fight, the Republic-Lipan-Tonkawa force, the armed party under Egg and "
            "John Bowles, and the Texas-allied victory. Captured women and children "
            "are not rated. The raw coordinate is the U.S. centroid rather than the "
            "Colorado-San Saba confluence and is withheld."
        ),
        confidence=0.88,
    ),
}


WAVE8_CHEROKEE_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Fort Prince George1760-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Fort Prince George1760-1"],
        "canonical_event": _canonical(
            "Fort Prince George ambush, hostage killings, and siege",
            1760,
            "16 February-June 1760",
            date_precision="month_range",
            granularity="compound_ambush_massacre_and_siege",
        ),
        "hold_category": "compound_violence_without_single_tactical_outcome",
        "hold_reason": (
            "On 16 February Oconostota's concealed warriors mortally wounded the "
            "fort commander during a parley; the Independent Company garrison then "
            "killed the confined Cherokee hostages, and a sporadic siege continued "
            "until Montgomery relieved the post in June. HCED's North Carolina "
            "actor is wrong, the hostage killings are not a competitive British "
            "victory, and the compound sequence has no single defensible tactical "
            "winner. It cannot produce an Elo result and is never made a draw."
        ),
        "evidence_refs": [
            "wave8_cherokee_ncpedia_etchoe",
            "wave8_cherokee_scencyclopedia_fort_prince_george",
        ],
    }
}

# This hold is a terminal exclusion from tactical Elo, not a deferred draw.
WAVE8_CHEROKEE_EXCLUSIONS = WAVE8_CHEROKEE_HOLDS
WAVE8_CHEROKEE_CONTRACT_IDS = frozenset(WAVE8_CHEROKEE_CONTRACTS)
WAVE8_CHEROKEE_HOLD_IDS = frozenset(WAVE8_CHEROKEE_HOLDS)
WAVE8_CHEROKEE_EXCLUSION_IDS = WAVE8_CHEROKEE_HOLD_IDS
WAVE8_CHEROKEE_RESERVED_IDS = WAVE8_CHEROKEE_CONTRACT_IDS | WAVE8_CHEROKEE_HOLD_IDS
WAVE8_CHEROKEE_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


# Both Etchoe rows share a town/area point that does not distinguish the two
# reviewed battlefields. San Saba uses the U.S. centroid. Fort Loudoun's point
# is the reviewed fort site. All four modern-country assertions remain valid.
WAVE8_CHEROKEE_POINT_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Etchoe1760-1",
        "hced-Etchoe1761-1",
        "hced-San Saba1839-1",
    }
)
WAVE8_CHEROKEE_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_CHEROKEE_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_CHEROKEE_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_CHEROKEE_COUNTRY_QUARANTINE_ADDITIONS,
}


# Every promoted result agrees with the raw HCED side order. Fort Prince
# George is excluded rather than silently reversed or converted to a draw.
WAVE8_CHEROKEE_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


# No exact IWBD twin exists in the locked snapshot. These normalized aliases
# make future same-name/same-year additions fail closed for review.
WAVE8_CHEROKEE_IWBD_ZERO_OVERLAP_AUDIT: dict[str, tuple[str, ...]] = {
    "1760": (
        "battle of echoe",
        "battle of etchoe",
        "battle of fort prince george",
        "echoe",
        "etchoe",
        "first battle of echoe",
        "first battle of etchoe",
        "fort loudon",
        "fort loudoun",
        "fort prince george",
        "siege of fort loudon",
        "siege of fort loudoun",
    ),
    "1761": (
        "battle of echoe",
        "battle of etchoe",
        "echoe",
        "etchoe",
        "second battle of echoe",
        "second battle of etchoe",
    ),
    "1839": (
        "battle at san saba",
        "battle near the mouth of the san saba river",
        "fight near the mouth of the san saba river",
        "san saba",
        "san saba fight",
    ),
}
WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}


# Neches is the July 1839 campaign engagement. San Saba is a distinct fight on
# 25 December against a smaller refugee party; neither may deduplicate the other.
WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Neches1839-1": {
        "source_dataset": "hced",
        "disposition": "related_distinct_event",
        "relationship": "same_war_different_engagement_date_and_fighting_force",
        "raw_row_sha256": (
            "cec8def02dd30a11a3178061abf24892984e76f77e45529c56a8770e69f3c3e1"
        ),
        "reason": (
            "Neches records the 15-16 July battle against Chief Bowl's larger "
            "East Texas force. San Saba records Burleson's separate 25 December "
            "fight against the refugee party led by Egg and John Bowles."
        ),
    }
}
WAVE8_CHEROKEE_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS,
    **WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_CHEROKEE_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_CHEROKEE_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_CHEROKEE_ENTITIES,
        "expected_candidate_ids": sorted(WAVE8_CHEROKEE_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_CHEROKEE_HOLDS,
        "integration_dispositions": WAVE8_CHEROKEE_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_CHEROKEE_IWBD_ZERO_OVERLAP_AUDIT,
        "outcome_overrides": WAVE8_CHEROKEE_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_CHEROKEE_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_CHEROKEE_SOURCES,
    }


def wave8_cherokee_audit_signature() -> str:
    """Return the SHA-256 pin over the complete audited lane state."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


# Patched to the measured payload after the fixtures and dispositions are final.
WAVE8_CHEROKEE_FINAL_AUDIT_SIGNATURE = (
    "6dd3baaf39ce5e1849d9f5bc174c71e867abebc00cf992945283def276c3e543"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_CHEROKEE_CONTRACTS), len(WAVE8_CHEROKEE_HOLDS)) != (4, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_CHEROKEE_ENTITIES), len(WAVE8_CHEROKEE_SOURCES)) != (8, 9):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_CHEROKEE_RESERVED_IDS != WAVE8_CHEROKEE_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_CHEROKEE_CONTRACT_IDS & WAVE8_CHEROKEE_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotions and holds overlap")
    if WAVE8_CHEROKEE_EXCLUSIONS is not WAVE8_CHEROKEE_HOLDS:
        raise ValueError(f"{_LANE_NAME} exclusion inventory diverged")
    if wave8_cherokee_audit_signature() != WAVE8_CHEROKEE_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_CHEROKEE_SOURCES}
    if len(source_by_id) != len(WAVE8_CHEROKEE_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_CHEROKEE_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_CHEROKEE_ENTITIES}
    expected_windows = {
        _ECHOE_1760_CHEROKEE_ID: (1760, 1760),
        _MONTGOMERIE_1760_ID: (1760, 1760),
        _LOUDOUN_CHEROKEE_ID: (1760, 1760),
        _LOUDOUN_GARRISON_ID: (1760, 1760),
        _GRANT_1761_ID: (1761, 1761),
        _ECHOE_1761_CHEROKEE_ID: (1761, 1761),
        _SAN_SABA_TEXAS_ID: (1839, 1839),
        _SAN_SABA_CHEROKEE_ID: (1839, 1839),
    }
    if set(entity_by_id) != set(expected_windows):
        raise ValueError(f"{_LANE_NAME} identity inventory changed")
    for entity_id, entity in entity_by_id.items():
        if (entity["start_year"], entity["end_year"]) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} identity window changed")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern tribal government" not in note:
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if normalize_label(entity["name"]) in {
            "cherokee",
            "cherokee indian",
            "cherokee indians",
        }:
            raise ValueError(f"{_LANE_NAME} installed a timeless ethnic identity")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    expected_precisions = {
        "hced-Etchoe1760-1": "day",
        "hced-Etchoe1761-1": "day",
        "hced-Fort Loudoun1760-1": "month_to_day",
        "hced-San Saba1839-1": "day",
    }
    expected_granularities = {
        "hced-Etchoe1760-1": "engagement",
        "hced-Etchoe1761-1": "engagement",
        "hced-Fort Loudoun1760-1": "siege",
        "hced-San Saba1839-1": "engagement",
    }
    for candidate_id, contract in WAVE8_CHEROKEE_CONTRACTS.items():
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
        if canonical["date_precision"] != expected_precisions[candidate_id]:
            raise ValueError(f"{_LANE_NAME} canonical date precision drifted")
        if canonical["granularity"] != expected_granularities[candidate_id]:
            raise ValueError(f"{_LANE_NAME} canonical granularity drifted")

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        used_entities.update(set(side_1) | set(side_2))
        year = int(canonical["year_low"])
        for entity_id in set(side_1) | set(side_2):
            start, end = expected_windows[entity_id]
            if not start <= year <= end:
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")

        if contract["result_type"] != "win" or contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} invented a draw or unknown result")
        if contract["war_type"] != "colonial_anti_colonial":
            raise ValueError(f"{_LANE_NAME} war-type contract drifted")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")
        if contract["source_outcome_override"] is not False:
            raise ValueError(f"{_LANE_NAME} contains an outcome override")
        if contract["outcome_reversal"] is not False:
            raise ValueError(f"{_LANE_NAME} contains an outcome reversal")

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
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")

    forbidden_hold_keys = {
        "losers",
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
        "winners",
    }
    for candidate_id, hold in WAVE8_CHEROKEE_HOLDS.items():
        if hold["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} hold hash table drifted")
        if forbidden_hold_keys & set(hold):
            raise ValueError(f"{_LANE_NAME} hold contains a rateable result")
        if hold["canonical_event"]["granularity"] != "compound_ambush_massacre_and_siege":
            raise ValueError(f"{_LANE_NAME} hold granularity drifted")
        reason = str(hold["hold_reason"]).casefold()
        for phrase in (
            "no single defensible tactical winner",
            "cannot produce an elo result",
            "never made a draw",
        ):
            if phrase not in reason:
                raise ValueError(f"{_LANE_NAME} hold rationale is incomplete")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence drifted")
        used_sources.update(evidence)

    used_sources.update(
        source_id
        for entity in WAVE8_CHEROKEE_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    expected_points = {
        "hced-Etchoe1760-1",
        "hced-Etchoe1761-1",
        "hced-San Saba1839-1",
    }
    if WAVE8_CHEROKEE_POINT_QUARANTINE_ADDITIONS != expected_points:
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_CHEROKEE_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country quarantine contract changed")
    if not expected_points <= WAVE8_CHEROKEE_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} quarantine references an unpromoted row")
    if WAVE8_CHEROKEE_OUTCOME_OVERRIDES or WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} empty result/duplicate inventory changed")

    if set(WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS) != {"hced-Neches1839-1"}:
        raise ValueError(f"{_LANE_NAME} cross-lane boundary changed")
    if WAVE8_CHEROKEE_INTEGRATION_DISPOSITIONS != WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} integration disposition inventory changed")
    if set(WAVE8_CHEROKEE_IWBD_ZERO_OVERLAP_AUDIT) != {"1760", "1761", "1839"}:
        raise ValueError(f"{_LANE_NAME} IWBD zero-overlap years changed")
    for aliases in WAVE8_CHEROKEE_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(aliases) or any(
            alias != normalize_label(alias) for alias in aliases
        ):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
    audited_names = {
        (int(year), normalize_label(name))
        for year, names in WAVE8_CHEROKEE_IWBD_ZERO_OVERLAP_AUDIT.items()
        for name in names
    }
    canonical_names = {
        (
            int(contract["canonical_event"]["year_low"]),
            normalize_label(contract["canonical_event"]["name"]),
        )
        for contract in WAVE8_CHEROKEE_CONTRACTS.values()
    }
    if not canonical_names <= audited_names:
        raise ValueError(f"{_LANE_NAME} canonical duplicate audit is incomplete")


def _is_exact_cherokee_label(value: Any) -> bool:
    return normalize_label(value) == "cherokee indians"


def validate_wave8_cherokee_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate the five-row exact-label inventory and every row fingerprint."""

    _validate_static()
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_CHEROKEE_CONTRACTS,
        WAVE8_CHEROKEE_HOLDS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_cherokee_label(row.get("side_1_raw"))
        or _is_exact_cherokee_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_CHEROKEE_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Cherokee Indians inventory changed: "
            f"{sorted(exact_label_ids)}"
        )
    return counts


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best"):
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


def validate_wave8_cherokee_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on the Neches boundary and future probable duplicates."""

    validate_wave8_cherokee_queue_contracts(hced_rows)
    related_id = "hced-Neches1839-1"
    related = [row for row in hced_rows if str(row.get("candidate_id")) == related_id]
    if len(related) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one related {related_id} row, found {len(related)}"
        )
    expected_hash = WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS[related_id][
        "raw_row_sha256"
    ]
    if canonical_hced_row_sha256(related[0]) != expected_hash:
        raise ValueError(f"{_LANE_NAME} related Neches fingerprint changed")

    audited = {
        (int(year), normalize_label(name))
        for year, names in WAVE8_CHEROKEE_IWBD_ZERO_OVERLAP_AUDIT.items()
        for name in names
    }
    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _row_year(row) is not None
        and (_row_year(row), normalize_label(row.get("name"))) in audited
    )
    if iwbd_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): {iwbd_matches}"
        )

    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if _row_year(event) is not None
        and (_row_year(event), normalize_label(event.get("name"))) in audited
        and event.get("hced_candidate_id") not in WAVE8_CHEROKEE_CONTRACT_IDS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable release duplicate(s): {release_matches}"
        )
    return {
        "cross_lane_hced_dispositions": len(WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS),
        "integration_dispositions": len(WAVE8_CHEROKEE_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "release_probable_twins": 0,
    }


def install_wave8_cherokee_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_CHEROKEE_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_cherokee_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_CHEROKEE_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_CHEROKEE_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_CHEROKEE_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_cherokee_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_cherokee_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_CHEROKEE_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_cherokee_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_CHEROKEE_CONTRACTS.values()
            ).items()
        )
    )


def wave8_cherokee_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_CHEROKEE_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(WAVE8_CHEROKEE_CROSS_LANE_DISPOSITIONS),
        "holds": len(WAVE8_CHEROKEE_HOLDS),
        "integration_dispositions": len(WAVE8_CHEROKEE_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_CHEROKEE_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_CHEROKEE_ENTITIES),
        "new_sources": len(WAVE8_CHEROKEE_SOURCES),
        "newly_rated_events": len(WAVE8_CHEROKEE_CONTRACTS),
        "outcome_overrides": len(WAVE8_CHEROKEE_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_CHEROKEE_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_CHEROKEE_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_CHEROKEE_RESERVED_IDS),
    }


def wave8_cherokee_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_CHEROKEE_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_CHEROKEE_POINT_QUARANTINE_ADDITIONS,
    }
