"""Candidate-keyed Wave 8 audit for HCED's exact plural ``Comanches`` label.

The four-row cohort is deliberately separate from :mod:`wave8_comanche`, which
owns six rows carrying the singular ``Comanche Indians`` label.  Neither lane
creates a generic Comanche polity.  Every rated actor below is bounded to one
documented action, and all singular-lane rows remain owned by that existing
module.

Two rows have defensible outcomes.  Antelope Hills is the 12 May 1858 series
of fights also called Little Robe Creek; Brushy Creek is the 25 February 1839
running engagement.  Blanco Canyon remains held because its source event
combines a successful Comanche horse raid and ambush with a U.S. relief,
withdrawal of the warriors, and later skirmishes.  Bandera Pass is terminally
excluded because modern archival review finds no contemporary account and the
purported date, personnel, and location conflict.  Neither nonpromotion is
turned into a draw.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave8_comanche import (
    WAVE8_COMANCHE_CONTRACTS,
    WAVE8_COMANCHE_HOLD_IDS,
    WAVE8_COMANCHE_RESERVED_IDS,
)
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_COMANCHES_CONTRACT_IDS",
    "WAVE8_COMANCHES_CONTRACTS",
    "WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_COMANCHES_ENTITIES",
    "WAVE8_COMANCHES_EXCLUSION_IDS",
    "WAVE8_COMANCHES_EXCLUSIONS",
    "WAVE8_COMANCHES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS",
    "WAVE8_COMANCHES_FINAL_AUDIT_SIGNATURE",
    "WAVE8_COMANCHES_HCED_ZERO_OVERLAP_AUDIT",
    "WAVE8_COMANCHES_HOLD_IDS",
    "WAVE8_COMANCHES_HOLDS",
    "WAVE8_COMANCHES_INTEGRATION_DISPOSITIONS",
    "WAVE8_COMANCHES_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_COMANCHES_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_COMANCHES_LOCATION_QUARANTINE_REASONS",
    "WAVE8_COMANCHES_NONPROMOTIONS",
    "WAVE8_COMANCHES_OUTCOME_OVERRIDES",
    "WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS",
    "WAVE8_COMANCHES_RESERVED_IDS",
    "WAVE8_COMANCHES_ROW_HASHES",
    "WAVE8_COMANCHES_SOURCES",
    "WAVE8_COMANCHES_TERMINAL_EXCLUSION_IDS",
    "WAVE8_COMANCHES_TERMINAL_EXCLUSIONS",
    "install_wave8_comanches_entities",
    "install_wave8_comanches_sources",
    "promote_wave8_comanches_contracts",
    "validate_wave8_comanches_integration_dispositions",
    "validate_wave8_comanches_queue_contracts",
    "wave8_comanches_audit_signature",
    "wave8_comanches_cohort_counts",
    "wave8_comanches_counts",
    "wave8_comanches_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact plural Comanches actor audit"
_EVENT_ID_PREFIX = "hced_wave8_comanches_"
_MODULE_OWNER = "military_elo.promotion.wave8_comanches"
_SINGULAR_MODULE_OWNER = "military_elo.promotion.wave8_comanche"


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
    event_identity_critique: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if crosscheck or event_identity_critique:
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


WAVE8_COMANCHES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_comanches_ohs_antelope_hills",
        "Antelope Hills, Battle of the",
        "https://www.okhistory.org/publications/enc/entry?entry=AN008",
        "Oklahoma Historical Society",
        "scholarly_state_encyclopedia",
        "rea_ohs_antelope_hills_2010",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_comanches_dickinson_little_robe",
        "Comanches defeated at the Battle of Little Robe Creek",
        "https://hd.housedivided.dickinson.edu/node/21702",
        "House Divided, Dickinson College",
        "university_civil_war_research_reference",
        "dickinson_house_divided_little_robe_1858",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_comanches_tsha_brushy_creek",
        "Brushy Creek, Battle of",
        "https://www.tshaonline.org/handbook/entries/brushy-creek-battle-of",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "thompson_tsha_brushy_creek",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_comanches_tsha_aaron_burleson",
        "Burleson, Aaron B.",
        "https://www.tshaonline.org/handbook/entries/burleson-aaron-b",
        "Texas State Historical Association",
        "scholarly_biographical_encyclopedia",
        "cutrer_tsha_aaron_burleson",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_comanches_williamson_county_brushy",
        "Williamson County history, 1837 to 1845",
        "https://www.wilcotx.gov/1568/1837-to-1845",
        "Williamson County, Texas",
        "official_local_government_history",
        "williamson_county_brushy_creek_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_comanches_thc_brushy_marker",
        "Battle of Brushy Creek historical marker, Atlas 5491009037",
        "https://atlas.thc.texas.gov/Details/5491009037",
        "Texas Historical Commission",
        "government_historical_marker_record",
        "thc_brushy_creek_marker_9037",
    ),
    _source(
        "wave8_comanches_ut_bandera_legend",
        "The Battle of Bandera Pass and the Making of Lone Star Legend",
        (
            "https://notevenpast.org/"
            "the-battle-of-bandera-pass-and-the-making-of-lone-star-legend/"
        ),
        "Department of History, University of Texas at Austin",
        "university_archival_public_history",
        "jennings_ut_bandera_pass_legend_2014",
        event_identity_critique=True,
    ),
    _source(
        "wave8_comanches_tsha_bandera_county",
        "Bandera County",
        "https://www.tshaonline.org/handbook/entries/bandera-county",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "tsha_bandera_county_history",
        event_identity_critique=True,
    ),
    _source(
        "wave8_comanches_tsha_blanco_canyon",
        "Blanco Canyon, Battle of",
        "https://www.tshaonline.org/handbook/entries/blanco-canyon-battle-of",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "anderson_tsha_blanco_canyon",
        crosscheck=True,
    ),
    _source(
        "wave8_comanches_tsha_quanah_parker",
        "Parker, Quanah",
        "https://www.tshaonline.org/handbook/entries/parker-quanah",
        "Texas State Historical Association",
        "scholarly_biographical_encyclopedia",
        "tsha_quanah_parker_biography",
        crosscheck=True,
    ),
    _source(
        "wave8_comanches_thc_freshwater_fork",
        "Battle of the Freshwater Fork of the Brazos, Atlas 5507018175",
        "https://atlas.thc.texas.gov/Details/5507018175",
        "Texas Historical Commission",
        "government_historical_marker_record",
        "thc_freshwater_fork_marker_18175",
        crosscheck=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    note: str,
    source_ids: Iterable[str],
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
            note
            + " No rating is inherited by any named commander, constituent nation, "
            "tribe, band, modern people, descendant community, or modern state."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_ANTELOPE_RANGERS_ID = "ford_texas_ranger_force_antelope_hills_1858"
_ANTELOPE_ALLIES_ID = "ford_indigenous_allied_force_antelope_hills_1858"
_ANTELOPE_COMANCHE_ID = "comanche_fighting_forces_little_robe_creek_1858"
_BRUSHY_TEXIAN_ID = "texas_ranger_militia_force_brushy_creek_1839"
_BRUSHY_COMANCHE_ID = "comanche_raiding_party_brushy_creek_1839"


WAVE8_COMANCHES_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _ANTELOPE_RANGERS_ID,
        "John S. Ford's Texas Ranger force at Antelope Hills (1858)",
        "event_bounded_ranger_force",
        1858,
        "Indian Territory, near Little Robe Creek",
        (
            "Bounded to the 102-ranger force led by John S. Ford in the 12 May "
            "Antelope Hills actions; it is not the United States Army and does not "
            "inherit a general Republic or State of Texas identity."
        ),
        [
            "wave8_comanches_dickinson_little_robe",
            "wave8_comanches_ohs_antelope_hills",
        ],
    ),
    _entity(
        _ANTELOPE_ALLIES_ID,
        "Indigenous allied fighting force at Antelope Hills (1858)",
        "event_bounded_allied_force",
        1858,
        "Indian Territory, near Little Robe Creek",
        (
            "Bounded to the 113 allied fighters, identified by the Oklahoma "
            "Historical Society as mainly Tonkawa, Anadarko, and Caddo, who fought "
            "with Ford's Rangers on 12 May. Unattested membership is not expanded."
        ),
        ["wave8_comanches_ohs_antelope_hills"],
    ),
    _entity(
        _ANTELOPE_COMANCHE_ID,
        "Comanche fighting forces at Little Robe Creek (1858)",
        "event_bounded_fighting_force",
        1858,
        "Indian Territory, near Little Robe Creek",
        (
            "Bounded to armed defenders of the attacked village and the neighboring "
            "Comanche reinforcements repulsed during the 12 May running action. "
            "Noncombatants in the village are not rated participants."
        ),
        [
            "wave8_comanches_dickinson_little_robe",
            "wave8_comanches_ohs_antelope_hills",
        ],
    ),
    _entity(
        _BRUSHY_TEXIAN_ID,
        "Republic of Texas ranger and militia force at Brushy Creek (1839)",
        "event_bounded_ranger_militia_force",
        1839,
        "Williamson County, Republic of Texas",
        (
            "Bounded to the ranger and local-militia parties in the 25 February "
            "running engagement, including Jacob Burleson's initial party and the "
            "Edward Burleson-Jesse Billingsley pursuit. Earlier and later frontier "
            "operations are excluded."
        ),
        [
            "wave8_comanches_thc_brushy_marker",
            "wave8_comanches_tsha_aaron_burleson",
            "wave8_comanches_tsha_brushy_creek",
            "wave8_comanches_williamson_county_brushy",
        ],
    ),
    _entity(
        _BRUSHY_COMANCHE_ID,
        "Comanche raiding party at Brushy Creek (1839)",
        "event_bounded_raiding_party",
        1839,
        "Williamson County, Republic of Texas",
        (
            "Bounded to the armed raiding party pursued and engaged north of Brushy "
            "Creek on 25 February. No band affiliation is supplied by the reviewed "
            "sources, and captives or other noncombatants are not rated."
        ),
        [
            "wave8_comanches_tsha_aaron_burleson",
            "wave8_comanches_tsha_brushy_creek",
            "wave8_comanches_williamson_county_brushy",
        ],
    ),
)


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


WAVE8_COMANCHES_ROW_HASHES: dict[str, str] = {
    "hced-Antelope Hills1858-1": (
        "1f99fa8fcf0f3b619bebd5ed703e0bb4b2b33cb566da14a88da0365c0f7f9cc5"
    ),
    "hced-Bandera Pass1841-1": (
        "cf2f183c29b15cdc78593adb1fb173582db33229264ca8e9d416bb89b1755039"
    ),
    "hced-Blanco Canyon1871-1": (
        "1dbaf68b8632e8c3d7bfa17852daf9d29f31ebb9a6235b0decfa028c6be4d006"
    ),
    "hced-Brushy Creek1839-1": (
        "555b4e888449b4a2e9453f7e5bfcc0df23f1082d9b61579afa6eb903da3fd919"
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
    source_by_id = {str(source["id"]): source for source in WAVE8_COMANCHES_SOURCES}
    outcome_ids = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_COMANCHES_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "winner_side": 1,
        "result_type": "win",
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcome_ids,
        "outcome_source_family_ids": sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcome_ids}
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


WAVE8_COMANCHES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Antelope Hills1858-1": _contract(
        "hced-Antelope Hills1858-1",
        _canonical(
            "Battle of the Antelope Hills (Little Robe Creek)",
            1858,
            "12 May 1858",
            date_precision="day",
            granularity="engagement_series",
        ),
        "antelope_hills_expedition_1858",
        [_ANTELOPE_ALLIES_ID, _ANTELOPE_RANGERS_ID],
        [_ANTELOPE_COMANCHE_ID],
        [
            "wave8_comanches_dickinson_little_robe",
            "wave8_comanches_ohs_antelope_hills",
        ],
        [
            "wave8_comanches_dickinson_little_robe",
            "wave8_comanches_ohs_antelope_hills",
        ],
        (
            "The Oklahoma Historical Society identifies Ford's 102 Texas Rangers, "
            "113 mainly Tonkawa-Anadarko-Caddo allies, the attacked Comanche "
            "village, and neighboring Comanche reinforcements. It records capture "
            "of the village and repulse of the reinforcements; Dickinson College "
            "independently records the Comanche defeat. The action is rated once as "
            "the one-day engagement series, not once per village or skirmish. The "
            "raw point is in Texas rather than the Oklahoma battlefield and is "
            "withheld."
        ),
        confidence=0.88,
    ),
    "hced-Brushy Creek1839-1": _contract(
        "hced-Brushy Creek1839-1",
        _canonical(
            "Battle of Brushy Creek",
            1839,
            "25 February 1839",
            date_precision="day",
            granularity="running_engagement",
        ),
        "brushy_creek_running_engagement_1839",
        [_BRUSHY_TEXIAN_ID],
        [_BRUSHY_COMANCHE_ID],
        [
            "wave8_comanches_thc_brushy_marker",
            "wave8_comanches_tsha_aaron_burleson",
            "wave8_comanches_tsha_brushy_creek",
            "wave8_comanches_williamson_county_brushy",
        ],
        [
            "wave8_comanches_tsha_aaron_burleson",
            "wave8_comanches_tsha_brushy_creek",
            "wave8_comanches_williamson_county_brushy",
        ],
        (
            "The reviewed accounts distinguish Jacob Burleson's failed opening "
            "charge from Edward Burleson's same-day pursuit and running fight. The "
            "Texas State Historical Association explicitly calls the completed "
            "battle a decisive defeat of the raiders; its battle narrative and the "
            "Williamson County history record the Comanche departure and reported "
            "losses. The whole bounded running engagement is rated once. The staged "
            "coordinate is west of the documented Taylor-area action and is withheld."
        ),
        confidence=0.82,
    ),
}


WAVE8_COMANCHES_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Blanco Canyon1871-1": {
        "raw_row_sha256": WAVE8_COMANCHES_ROW_HASHES["hced-Blanco Canyon1871-1"],
        "canonical_event": _canonical(
            "Blanco Canyon campaign actions",
            1871,
            "9-15 October 1871",
            date_precision="day_range",
            granularity="compound_raid_ambush_relief_and_pursuit",
        ),
        "hold_category": "compound_action_without_unique_tactical_winner",
        "hold_reason": (
            "HCED's single Comanche victory label collapses several different "
            "actions. Quanah Parker's force successfully stampeded the cavalry "
            "horses and ambushed a pursuing detachment; Mackenzie's main column and "
            "Tonkawa scouts then relieved that detachment and forced the warriors to "
            "withdraw; later pursuit and a separate skirmish produced additional "
            "losses on both sides. Sources characterize Mackenzie's overall campaign "
            "as unsuccessful, but that strategic assessment is not a unique tactical "
            "winner for the compound HCED row. The row remains staged and is not "
            "converted to a draw."
        ),
        "documented_components": [
            "9 October Comanche horse raid",
            "10 October Comanche ambush and U.S.-Tonkawa relief",
            "10-13 October pursuit ending in weather",
            "15 October skirmish during the return through Blanco Canyon",
        ],
        "evidence_refs": [
            "wave8_comanches_thc_freshwater_fork",
            "wave8_comanches_tsha_blanco_canyon",
            "wave8_comanches_tsha_quanah_parker",
        ],
    },
}


WAVE8_COMANCHES_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Bandera Pass1841-1": {
        "raw_row_sha256": WAVE8_COMANCHES_ROW_HASHES["hced-Bandera Pass1841-1"],
        "canonical_event": _canonical(
            "Purported Battle of Bandera Pass",
            1841,
            "purported 1841; published accounts also assign 1842 or 1843",
            date_precision="conflicting_year",
            granularity="unverifiable_legendary_assertion",
        ),
        "exclusion_category": "unverifiable_legend_and_conflicting_year",
        "exclusion_reason": (
            "The University of Texas archival review finds no memoir, official "
            "report, or contemporary press account for a fight of the claimed scale; "
            "it also shows that named participants do not fit the 1841 roster and "
            "that the probable location differs from the marker. The TSHA county "
            "history assigns 1842, while other retellings use 1843. The staged 1841 "
            "row therefore cannot be bound to a unique attested event, side roster, "
            "or outcome and is terminally excluded rather than promoted from legend."
        ),
        "evidence_refs": [
            "wave8_comanches_tsha_bandera_county",
            "wave8_comanches_ut_bandera_legend",
        ],
    },
}


WAVE8_COMANCHES_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_COMANCHES_HOLDS,
    **WAVE8_COMANCHES_TERMINAL_EXCLUSIONS,
}
WAVE8_COMANCHES_EXCLUSIONS = WAVE8_COMANCHES_TERMINAL_EXCLUSIONS
WAVE8_COMANCHES_CONTRACT_IDS = frozenset(WAVE8_COMANCHES_CONTRACTS)
WAVE8_COMANCHES_HOLD_IDS = frozenset(WAVE8_COMANCHES_HOLDS)
WAVE8_COMANCHES_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_COMANCHES_TERMINAL_EXCLUSIONS
)
WAVE8_COMANCHES_EXCLUSION_IDS = WAVE8_COMANCHES_TERMINAL_EXCLUSION_IDS
WAVE8_COMANCHES_RESERVED_IDS = frozenset(
    WAVE8_COMANCHES_CONTRACT_IDS
    | WAVE8_COMANCHES_HOLD_IDS
    | WAVE8_COMANCHES_TERMINAL_EXCLUSION_IDS
)
WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_COMANCHES_ROW_HASHES)


WAVE8_COMANCHES_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Antelope Hills1858-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The staged point is in Texas, while the reviewed sources place the "
            "battle north of the Canadian River near Little Robe Creek in present "
            "Ellis County, Oklahoma."
        ),
    },
    "hced-Brushy Creek1839-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The staged coordinate is near Cedar Park, not the documented running "
            "battle north of Brushy Creek in the Taylor and Post Oak Island area."
        ),
    },
}
WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_COMANCHES_LOCATION_QUARANTINE_REASONS
)
WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_COMANCHES_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_COMANCHES_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_COMANCHES_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_COMANCHES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_COMANCHES_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {}


# Explicit ownership audit for every row in the pre-existing singular-label lane.
# These are related by ethnonym only; none is an event twin of the plural cohort.
WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "owner_module": _SINGULAR_MODULE_OWNER,
        "owner_status": (
            "held_by_singular_lane"
            if candidate_id in WAVE8_COMANCHE_HOLD_IDS
            else "promoted_by_singular_lane"
        ),
        "shared_component": "Comanche participants",
        "reason": (
            "The existing singular Comanche lane owns this different candidate-keyed "
            "event. It shares an ethnonym but neither a candidate ID nor a canonical "
            "name-year key with the exact plural Comanches cohort."
        ),
    }
    for candidate_id in sorted(WAVE8_COMANCHE_RESERVED_IDS)
}


def _duplicate_audit(year: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": sorted({normalize_label(alias) for alias in aliases}),
        "years": [year, year],
    }


WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Antelope Hills1858-1": _duplicate_audit(
        1858,
        "Antelope Hills",
        "Battle of Antelope Hills",
        "Battle of the Antelope Hills",
        "Battle of the Antelope Hills (Little Robe Creek)",
        "Battle of Little Robe Creek",
        "Little Robe Creek",
    ),
    "hced-Bandera Pass1841-1": _duplicate_audit(
        1841,
        "Bandera Pass",
        "Battle of Bandera Pass",
        "Purported Battle of Bandera Pass",
    ),
    "hced-Blanco Canyon1871-1": _duplicate_audit(
        1871,
        "Battle of Blanco Canyon",
        "Blanco Canyon",
        "Blanco Canyon campaign actions",
    ),
    "hced-Brushy Creek1839-1": _duplicate_audit(
        1839,
        "Battle of Brushy Creek",
        "Brushy Creek",
    ),
}
WAVE8_COMANCHES_HCED_ZERO_OVERLAP_AUDIT = WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_COMANCHES_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_COMANCHES_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_COMANCHES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_COMANCHES_HOLDS,
        "integration_dispositions": WAVE8_COMANCHES_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_COMANCHES_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_COMANCHES_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_COMANCHES_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS
        ),
        "related_singular_lane_dispositions": (
            WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS
        ),
        "row_hashes": WAVE8_COMANCHES_ROW_HASHES,
        "sources": WAVE8_COMANCHES_SOURCES,
        "terminal_exclusions": WAVE8_COMANCHES_TERMINAL_EXCLUSIONS,
    }


def wave8_comanches_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label adjudication."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_COMANCHES_FINAL_AUDIT_SIGNATURE = (
    "c1560a4a536aaccb930b00712e9e2b4b136167ca44d5d03c92da5b0d5ba959a3"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    dispositions = (
        WAVE8_COMANCHES_CONTRACT_IDS,
        WAVE8_COMANCHES_HOLD_IDS,
        WAVE8_COMANCHES_TERMINAL_EXCLUSION_IDS,
    )
    if tuple(map(len, dispositions)) != (2, 1, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if any(
        dispositions[left] & dispositions[right]
        for left in range(len(dispositions))
        for right in range(left + 1, len(dispositions))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if WAVE8_COMANCHES_RESERVED_IDS != WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    if (len(WAVE8_COMANCHES_ENTITIES), len(WAVE8_COMANCHES_SOURCES)) != (5, 11):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if wave8_comanches_audit_signature() != WAVE8_COMANCHES_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_COMANCHES_SOURCES}
    if len(source_by_id) != len(WAVE8_COMANCHES_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({str(source["source_family_id"]) for source in WAVE8_COMANCHES_SOURCES}) != len(
        WAVE8_COMANCHES_SOURCES
    ):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_COMANCHES_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_COMANCHES_ENTITIES}
    if len(entity_by_id) != len(WAVE8_COMANCHES_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "comanche",
        "comanches",
        "comanche indians",
        "comanche nation",
        "texas",
        "united states",
    }
    for entity in WAVE8_COMANCHES_ENTITIES:
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} identity is not event bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if not str(entity["kind"]).startswith("event_bounded_"):
            raise ValueError(f"{_LANE_NAME} identity kind is not bounded")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic identity")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern state" not in note:
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_COMANCHES_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_COMANCHES_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract row hash drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} canonical key drifted")
        if canonical["date_precision"] != "day":
            raise ValueError(f"{_LANE_NAME} promoted an imprecise event")
        if canonical["granularity"] not in {"engagement_series", "running_engagement"}:
            raise ValueError(f"{_LANE_NAME} promoted unsupported granularity")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} invalid opposing sides")
        participants = set(side_1) | set(side_2)
        if not participants <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        used_entities.update(participants)
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} outcome policy drifted")
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
        if len(outcomes) < 2 or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} lacks independent outcome evidence")
        if not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome evidence is not cited")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome families are not independent")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")

    for inventory, category_key in (
        (WAVE8_COMANCHES_HOLDS, "hold_category"),
        (WAVE8_COMANCHES_TERMINAL_EXCLUSIONS, "exclusion_category"),
    ):
        for candidate_id, disposition in inventory.items():
            if disposition["raw_row_sha256"] != WAVE8_COMANCHES_ROW_HASHES[candidate_id]:
                raise ValueError(f"{_LANE_NAME} nonpromotion row hash drifted")
            if not disposition.get(category_key) or not disposition.get(
                "hold_reason" if category_key == "hold_category" else "exclusion_reason"
            ):
                raise ValueError(f"{_LANE_NAME} nonpromotion reason is incomplete")
            forbidden = {
                "result_type",
                "winner_side",
                "side_1_entity_ids",
                "side_2_entity_ids",
            }
            if forbidden & set(disposition):
                raise ValueError(f"{_LANE_NAME} nonpromotion contains a rated result")
            evidence = list(map(str, disposition["evidence_refs"]))
            if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
                raise ValueError(f"{_LANE_NAME} nonpromotion provenance drifted")
            used_sources.update(evidence)

    used_sources.update(
        source_id
        for entity in WAVE8_COMANCHES_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")

    if WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS != WAVE8_COMANCHES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    if set(WAVE8_COMANCHES_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    for review in WAVE8_COMANCHES_LOCATION_QUARANTINE_REASONS.values():
        if review["actions"] != ["withhold_point"] or not review["reason"]:
            raise ValueError(f"{_LANE_NAME} location review drifted")

    if (
        WAVE8_COMANCHES_OUTCOME_OVERRIDES
        or WAVE8_COMANCHES_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_COMANCHES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_COMANCHES_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty integration inventory changed")
    if WAVE8_COMANCHES_EXCLUSIONS is not WAVE8_COMANCHES_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion alias drifted")

    if set(WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS) != set(
        WAVE8_COMANCHE_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} singular-lane ownership audit is incomplete")
    if WAVE8_COMANCHES_RESERVED_IDS & WAVE8_COMANCHE_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} overlaps singular-lane candidate ownership")
    for candidate_id, disposition in (
        WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS.items()
    ):
        expected_status = (
            "held_by_singular_lane"
            if candidate_id in WAVE8_COMANCHE_HOLD_IDS
            else "promoted_by_singular_lane"
        )
        if disposition["owner_module"] != _SINGULAR_MODULE_OWNER:
            raise ValueError(f"{_LANE_NAME} singular owner changed")
        if disposition["owner_status"] != expected_status:
            raise ValueError(f"{_LANE_NAME} singular disposition changed")

    plural_keys = {
        (
            int(contract["canonical_event"]["year_low"]),
            normalize_label(contract["canonical_event"]["name"]),
        )
        for contract in WAVE8_COMANCHES_CONTRACTS.values()
    }
    singular_keys = {
        (
            int(contract["canonical_event"]["year_low"]),
            normalize_label(contract["canonical_event"]["name"]),
        )
        for contract in WAVE8_COMANCHE_CONTRACTS.values()
    }
    if plural_keys & singular_keys:
        raise ValueError(f"{_LANE_NAME} collides with a singular-lane canonical event")

    if set(WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for audit in WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(audit["aliases"]):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if any(alias != normalize_label(alias) for alias in audit["aliases"]):
            raise ValueError(f"{_LANE_NAME} duplicate alias is not normalized")
        if audit["years"] != [audit["years"][0], audit["years"][0]]:
            raise ValueError(f"{_LANE_NAME} duplicate year window drifted")


def _is_exact_comanches_label(value: Any) -> bool:
    return normalize_label(value) == "comanches"


def validate_wave8_comanches_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all four exact-label rows and immutable queue fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_COMANCHES_CONTRACTS,
        WAVE8_COMANCHES_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_comanches_label(row.get("side_1_raw"))
        or _is_exact_comanches_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Comanches inventory changed: {sorted(exact_ids)}"
        )
    return {
        "holds": len(WAVE8_COMANCHES_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_COMANCHES_TERMINAL_EXCLUSIONS),
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
        value = row.get(field)
        if isinstance(value, str):
            text = value.lstrip("-")
            if len(text) >= 4 and text[:4].isdigit():
                year = int(text[:4])
                return -year if value.startswith("-") else year
    return None


_DUPLICATE_MATCH_KEYS = {
    (year, alias)
    for audit in WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
}


def validate_wave8_comanches_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on an unreviewed HCED, IWBD, or release event twin."""

    validate_wave8_comanches_queue_contracts(hced_rows)
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS
        and (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if hced_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed HCED twin(s): {hced_matches}")
    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if iwbd_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed IWBD twin(s): {iwbd_matches}")
    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_COMANCHES_CONTRACT_IDS
        and (_row_year(event), normalize_label(event.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_matches}"
        )
    return {
        "existing_release_duplicate_dispositions": len(
            WAVE8_COMANCHES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(WAVE8_COMANCHES_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_COMANCHES_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "singular_lane_owned_rows": len(
            WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS
        ),
    }


def install_wave8_comanches_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_COMANCHES_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_comanches_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_COMANCHES_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_comanches_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_comanches_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_COMANCHES_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_comanches_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_COMANCHES_CONTRACTS.values()
            ).items()
        )
    )


def wave8_comanches_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_COMANCHES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_COMANCHES_HOLDS),
        "integration_dispositions": len(WAVE8_COMANCHES_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_COMANCHES_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_COMANCHES_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_COMANCHES_ENTITIES),
        "new_sources": len(WAVE8_COMANCHES_SOURCES),
        "newly_rated_events": len(WAVE8_COMANCHES_CONTRACTS),
        "outcome_overrides": len(WAVE8_COMANCHES_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_COMANCHES_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_COMANCHES_EXPECTED_CANDIDATE_IDS),
        "singular_lane_owned_rows": len(
            WAVE8_COMANCHES_RELATED_SINGULAR_LANE_DISPOSITIONS
        ),
        "terminal_exclusions": len(WAVE8_COMANCHES_TERMINAL_EXCLUSIONS),
    }


def wave8_comanches_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_COMANCHES_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_COMANCHES_POINT_QUARANTINE_ADDITIONS,
    }
