"""Exact Wave 8 dispositions for HCED rows blocked on ``Comanche Indians``.

The lane is candidate-keyed and fail-closed.  Every rated Indigenous actor is
bound to the documented campaign, band, coalition, or engagement; no generic
Comanche identity is created and no result is inherited by a modern people.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_COMANCHE_CONTRACT_IDS",
    "WAVE8_COMANCHE_CONTRACTS",
    "WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_COMANCHE_ENTITIES",
    "WAVE8_COMANCHE_FINAL_AUDIT_SIGNATURE",
    "WAVE8_COMANCHE_HOLD_IDS",
    "WAVE8_COMANCHE_HOLDS",
    "WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITION_IDS",
    "WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_COMANCHE_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_COMANCHE_OUTCOME_OVERRIDE_IDS",
    "WAVE8_COMANCHE_OUTCOME_OVERRIDES",
    "WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_COMANCHE_RESERVED_IDS",
    "WAVE8_COMANCHE_SOURCES",
    "install_wave8_comanche_entities",
    "install_wave8_comanche_sources",
    "promote_wave8_comanche_contracts",
    "validate_wave8_comanche_queue_contracts",
    "wave8_comanche_audit_signature",
    "wave8_comanche_cohort_counts",
    "wave8_comanche_counts",
    "wave8_comanche_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Comanche"
_EVENT_ID_PREFIX = "hced_wave8_comanche_"

# This pin covers every disposition, fixture, direct-outcome assertion,
# quarantine addition, and the empty IWBD duplicate audit.
WAVE8_COMANCHE_FINAL_AUDIT_SIGNATURE = (
    "39ae130b1c3481644405240fb9cdc7a50e846f048084754ca464ac250a10e479"
)


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    government_work: bool = False,
    outcome: bool = True,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "US government work" if government_work else "linked_reference",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_COMANCHE_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_comanche_nps_indian_scouts",
        "Indian Scouts — Fort Union National Monument",
        "https://www.nps.gov/foun/learn/historyculture/indian-scouts.htm",
        "U.S. National Park Service",
        "government_history",
        "us_national_park_service",
        government_work=True,
    ),
    _source(
        "wave8_comanche_nps_santa_fe_trail_four_tribes",
        "The Santa Fe Trail's Impact on Four Indian Nations",
        (
            "https://www.nps.gov/safe/learn/historyculture/upload/"
            "Santa-Fe-Trail-Impact-on-Four-Tribes-508.pdf"
        ),
        "U.S. National Park Service",
        "government_ethnohistory",
        "us_national_park_service",
        government_work=True,
    ),
    _source(
        "wave8_comanche_tsha_first_adobe_walls",
        "Adobe Walls, First Battle of",
        "https://www.tshaonline.org/handbook/entries/adobe-walls-first-battle-of",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "texas_state_historical_association",
    ),
    _source(
        "wave8_comanche_thc_centennial_monuments",
        "Monuments Erected by the State of Texas to Commemorate the Centenary of Texas Independence",
        "https://www.thc.texas.gov/public/upload/preserve/TexasCentennial1938.pdf",
        "Texas Historical Commission",
        "government_historical_marker_compendium",
        "texas_historical_commission",
    ),
    _source(
        "wave8_comanche_army_mcoe_raids",
        "Learning the Long-Distance Raid: Comanche, Rangers and 2nd U.S. Cavalry on the Texas Frontier",
        (
            "https://www.benning.army.mil/armor/eARMOR/content/issues/"
            "2014/JUL_SEP/Jennings.html"
        ),
        "U.S. Army Maneuver Center of Excellence",
        "official_military_history",
        "us_army_armor_history",
        government_work=True,
    ),
    _source(
        "wave8_comanche_ohs_wichita_village",
        "Wichita Village, Battle of the",
        "https://www.okhistory.org/publications/enc/entry?entry=WI004",
        "Oklahoma Historical Society",
        "state_historical_encyclopedia",
        "oklahoma_historical_society",
    ),
    _source(
        "wave8_comanche_uok_without_quarter",
        "Without Quarter: The Wichita Expedition and the Fight on Crooked Creek",
        "https://www.oupress.com/9780806123677/without-quarter/",
        "University of Oklahoma Press",
        "scholarly_monograph",
        "university_of_oklahoma_press",
    ),
    _source(
        "wave8_comanche_thc_plum_creek",
        "Battle of Plum Creek historical marker — Atlas Number 5055009783",
        "https://atlas.thc.texas.gov/Details/5055009783",
        "Texas Historical Commission",
        "government_historical_marker",
        "texas_historical_commission",
    ),
    _source(
        "wave8_comanche_tsha_plum_creek",
        "Plum Creek, Battle of",
        "https://www.tshaonline.org/handbook/entries/plum-creek-battle-of",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "texas_state_historical_association",
    ),
    _source(
        "wave8_comanche_tsha_walkers_creek",
        "Walker's Creek, Battle of",
        "https://www.tshaonline.org/handbook/entries/walkers-creek-battle-of",
        "Texas State Historical Association",
        "scholarly_state_encyclopedia",
        "texas_state_historical_association",
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
            + " No rating is inherited by any constituent nation, band, modern "
            "people, descendant community, or later force."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_COMANCHE_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "wichita_expedition_us_army_force_1858_1859",
        "Van Dorn's U.S. Army force in the Wichita Expedition (1858–1859)",
        "campaign_force",
        1858,
        1859,
        "Southern Plains",
        ["wave8_comanche_army_mcoe_raids"],
        (
            "Campaign-bounded Second U.S. Cavalry and attached mounted-infantry "
            "force serving under Earl Van Dorn."
        ),
    ),
    _entity(
        "wichita_expedition_indigenous_auxiliaries_1858_1859",
        "Indigenous auxiliaries in the Wichita Expedition (1858–1859)",
        "campaign_bounded_allied_force",
        1858,
        1859,
        "Southern Plains",
        ["wave8_comanche_army_mcoe_raids"],
        (
            "Campaign-bounded Native scouts and auxiliaries directly attested with "
            "Van Dorn's column; uncertain constituent labels are not expanded."
        ),
    ),
    _entity(
        "wichita_village_comanche_fighting_force_1858",
        "Comanche fighting force at the Wichita Village (1858)",
        "event_bounded_force",
        1858,
        1858,
        "Indian Territory",
        [
            "wave8_comanche_army_mcoe_raids",
            "wave8_comanche_ohs_wichita_village",
        ],
        (
            "Engagement-bounded warriors who fought Van Dorn's column on 1 October; "
            "the identity does not absorb noncombatants in the attacked camp."
        ),
    ),
    _entity(
        "crooked_creek_comanche_fighting_force_1859",
        "Comanche fighting force at Crooked Creek (1859)",
        "event_bounded_force",
        1859,
        1859,
        "Kansas Territory",
        [
            "wave8_comanche_army_mcoe_raids",
            "wave8_comanche_uok_without_quarter",
        ],
        (
            "Engagement-bounded warriors who resisted the Wichita Expedition at "
            "Crooked Creek; no unattested Comanche band is supplied."
        ),
    ),
    _entity(
        "plum_creek_texian_force_1840",
        "Republic of Texas force at Plum Creek (1840)",
        "event_bounded_force",
        1840,
        1840,
        "Republic of Texas",
        ["wave8_comanche_thc_plum_creek", "wave8_comanche_tsha_plum_creek"],
        (
            "Engagement-bounded volunteer, militia, and ranger force assembled at "
            "Plum Creek under Felix Huston and subordinate commanders."
        ),
    ),
    _entity(
        "plum_creek_tonkawa_allies_1840",
        "Tonkawa allies at Plum Creek (1840)",
        "event_bounded_allied_force",
        1840,
        1840,
        "Republic of Texas",
        ["wave8_comanche_thc_plum_creek"],
        (
            "The thirteen Tonkawa participants directly identified with Edward "
            "Burleson's volunteers at Plum Creek."
        ),
    ),
    _entity(
        "plum_creek_comanche_kiowa_war_party_1840",
        "Comanche–Kiowa Great Raid war party at Plum Creek (1840)",
        "event_bounded_coalition",
        1840,
        1840,
        "Republic of Texas",
        ["wave8_comanche_thc_plum_creek"],
        (
            "Event-bounded Comanche and Kiowa war party returning from the Great "
            "Raid; neither nation receives a separate timeless identity."
        ),
    ),
    _entity(
        "walkers_creek_hays_ranger_detachment_1844",
        "Hays's Texas Ranger detachment at Walker's Creek (1844)",
        "event_bounded_force",
        1844,
        1844,
        "Republic of Texas",
        ["wave8_comanche_tsha_walkers_creek"],
        (
            "The fifteen-man ranger detachment commanded by John Coffee Hays in the "
            "8 June Walker's Creek action."
        ),
    ),
    _entity(
        "walkers_creek_comanche_waco_mexican_raiding_party_1844",
        "Comanche–Waco–Mexican raiding party at Walker's Creek (1844)",
        "event_bounded_coalition",
        1844,
        1844,
        "Republic of Texas",
        ["wave8_comanche_tsha_walkers_creek"],
        (
            "Event-bounded raiding party whose Comanche, Waco, and Mexican "
            "composition is reported by the Republic's acting war secretary."
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


def _contract(
    row_hash: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    outcome_source_family_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": row_hash,
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "winner_side": 1,
        "result_type": "win",
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": sorted(set(map(str, outcome_source_ids))),
        "outcome_source_family_ids": sorted(
            set(map(str, outcome_source_family_ids))
        ),
        "source_outcome_override": False,
        "actor_override": "bounded_exact_opposing_forces",
        "audit_note": audit_note,
    }


WAVE8_COMANCHE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Plum Creek, Texas1840-1": _contract(
        "d6b729fab715e47d20b5cb12672456f8d9d10d0e1c85a2580a0873c3d0df9da9",
        _canonical("Battle of Plum Creek", 1840, "12 August 1840"),
        "texas_comanche_conflict_1840_1844",
        ["plum_creek_texian_force_1840", "plum_creek_tonkawa_allies_1840"],
        ["plum_creek_comanche_kiowa_war_party_1840"],
        ["wave8_comanche_thc_plum_creek", "wave8_comanche_tsha_plum_creek"],
        ["wave8_comanche_thc_plum_creek"],
        ["texas_historical_commission"],
        (
            "The Texas Historical Commission identifies about 200 Texans, thirteen "
            "Tonkawa allies, and the Comanche–Kiowa war party, and directly records "
            "the Texian tactical success. The raw point is far from Lockhart and is "
            "withheld."
        ),
        confidence=0.88,
    ),
    "hced-Walkers Creek1844-1": _contract(
        "4024ec2a68a334f8689276dd21fe5feb0e87e48f572c3012dfe11acc51d4e53b",
        _canonical("Battle of Walker's Creek", 1844, "8 June 1844"),
        "texas_comanche_conflict_1840_1844",
        ["walkers_creek_hays_ranger_detachment_1844"],
        ["walkers_creek_comanche_waco_mexican_raiding_party_1844"],
        ["wave8_comanche_tsha_walkers_creek"],
        ["wave8_comanche_tsha_walkers_creek"],
        ["texas_state_historical_association"],
        (
            "Hays's report and the Republic war department record the ranger "
            "success and the mixed Comanche–Waco–Mexican opposing party. The raw "
            "point is not in the documented Sisterdale-area battlefield and is "
            "withheld."
        ),
        confidence=0.87,
    ),
    "hced-Rush Springs1858-1": _contract(
        "91e9ce237c363c15dd84c35df9dea8f68c0995b5419766c4459ee053704c56c1",
        _canonical("Battle of the Wichita Village", 1858, "1 October 1858"),
        "wichita_expedition_1858_1859",
        [
            "wichita_expedition_indigenous_auxiliaries_1858_1859",
            "wichita_expedition_us_army_force_1858_1859",
        ],
        ["wichita_village_comanche_fighting_force_1858"],
        [
            "wave8_comanche_army_mcoe_raids",
            "wave8_comanche_ohs_wichita_village",
        ],
        ["wave8_comanche_army_mcoe_raids"],
        ["us_army_armor_history"],
        (
            "The canonical event is the Battle of the Wichita Village, not an "
            "invented Rush Springs engagement. Direct official history records the "
            "U.S.-auxiliary tactical victory while distinguishing the fighting force "
            "from noncombatants killed in the village assault. The town-centroid "
            "point is withheld."
        ),
        confidence=0.85,
    ),
    "hced-Crooked Creek1859-1": _contract(
        "296423f5b2e6917503d7746f67e3eba9dd7eb7d215db5832458de9e94f9ceb4c",
        _canonical("Battle of Crooked Creek", 1859, "13 May 1859"),
        "wichita_expedition_1858_1859",
        [
            "wichita_expedition_indigenous_auxiliaries_1858_1859",
            "wichita_expedition_us_army_force_1858_1859",
        ],
        ["crooked_creek_comanche_fighting_force_1859"],
        [
            "wave8_comanche_army_mcoe_raids",
            "wave8_comanche_uok_without_quarter",
        ],
        [
            "wave8_comanche_army_mcoe_raids",
            "wave8_comanche_uok_without_quarter",
        ],
        ["university_of_oklahoma_press", "us_army_armor_history"],
        (
            "Official and scholarly histories identify the 13 May engagement and "
            "the Wichita Expedition's tactical victory after armed resistance. No "
            "unattested Comanche band is supplied, and the Oklahoma raw point is "
            "withheld for the Kansas event."
        ),
        confidence=0.86,
    ),
}


WAVE8_COMANCHE_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Adobe Walls1864-1": {
        "raw_row_sha256": (
            "957ce353c339375d96c44d93768d5d52f58efd863c9a2163cd230a894faf548d"
        ),
        "canonical_event": _canonical(
            "First Battle of Adobe Walls",
            1864,
            "November 1864 (reviewed sources differ between 25 and 26 November)",
            date_precision="year",
        ),
        "hold_category": "contradictory_outcome_evidence",
        "hold_reason": (
            "The coalition cannot be reduced to HCED's United States–Comanche pair: "
            "Carson's New Mexico Volunteers fought with Ute and Jicarilla Apache "
            "scouts against Kiowa, Comanche, and Kiowa-Apache participants. More "
            "importantly, the TSHA account credits Carson with a decisive victory "
            "while two NPS histories describe a failed expedition/retreat and the "
            "Kiowa–Comanche force driving it from the field. The row is neither kept "
            "as a U.S. win nor reversed or converted into a draw."
        ),
        "documented_coalition_components": {
            "carson_column": [
                "First Cavalry, New Mexico Volunteers",
                "Jicarilla Apache scouts",
                "Ute scouts",
            ],
            "southern_plains_force": [
                "Comanche participants",
                "Kiowa participants",
                "Kiowa-Apache participants",
            ],
        },
        "evidence_refs": [
            "wave8_comanche_nps_indian_scouts",
            "wave8_comanche_nps_santa_fe_trail_four_tribes",
            "wave8_comanche_tsha_first_adobe_walls",
        ],
    },
    "hced-Colorado1840-1": {
        "raw_row_sha256": (
            "7cee0a370329e6e3fa452e9ca9aff24b6ea31301a2b211af6b84334a58f4954e"
        ),
        "canonical_event": _canonical(
            "Colorado",
            1840,
            "1840 (exact event unresolved)",
            date_precision="year",
            granularity="unresolved_source_assertion",
        ),
        "hold_category": "ambiguous_event_identity_and_noncompetitive_massacre",
        "hold_reason": (
            "The bare name Colorado and mixed participant tokens do not safely "
            "distinguish the separately documented 12 August Battle of Plum Creek "
            "from Moore's 24 October destruction of a Comanche village on the upper "
            "Colorado. HCED also marks the row as a battle followed by massacre, and "
            "the government marker records one-sided killing and capture at the "
            "village. No canonical engagement or second Elo result is invented."
        ),
        "evidence_refs": [
            "wave8_comanche_thc_centennial_monuments",
            "wave8_comanche_thc_plum_creek",
        ],
    },
}


WAVE8_COMANCHE_CONTRACT_IDS = frozenset(WAVE8_COMANCHE_CONTRACTS)
WAVE8_COMANCHE_HOLD_IDS = frozenset(WAVE8_COMANCHE_HOLDS)
WAVE8_COMANCHE_RESERVED_IDS = WAVE8_COMANCHE_CONTRACT_IDS | WAVE8_COMANCHE_HOLD_IDS


# These additions are lane-owned integration contracts.  They are applied to
# emitted events here without mutating the shared quarantine manifests.
WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Crooked Creek1859-1",
        "hced-Plum Creek, Texas1840-1",
        "hced-Rush Springs1858-1",
        "hced-Walkers Creek1844-1",
    }
)
WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_COMANCHE_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS,
}


# IWBD has no exact or containing event for this six-row cohort.
WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITION_IDS = frozenset(
    WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITIONS
)


# Every promoted winner agrees with the raw HCED winner and a direct source.
WAVE8_COMANCHE_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_COMANCHE_OUTCOME_OVERRIDE_IDS = frozenset(WAVE8_COMANCHE_OUTCOME_OVERRIDES)


_EXPECTED_CONTRACT_IDS = frozenset(
    {
        "hced-Crooked Creek1859-1",
        "hced-Plum Creek, Texas1840-1",
        "hced-Rush Springs1858-1",
        "hced-Walkers Creek1844-1",
    }
)
_EXPECTED_HOLD_IDS = frozenset(
    {"hced-Adobe Walls1864-1", "hced-Colorado1840-1"}
)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_COMANCHE_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_COMANCHE_ENTITIES,
        "holds": WAVE8_COMANCHE_HOLDS,
        "iwbd_duplicate_dispositions": WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITIONS,
        "outcome_overrides": WAVE8_COMANCHE_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_COMANCHE_SOURCES,
    }


def wave8_comanche_audit_signature() -> str:
    """Return the SHA-256 pin over the complete audited lane state."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(values)
    return items == sorted(set(items))


def _validate_static() -> None:
    if WAVE8_COMANCHE_CONTRACT_IDS != _EXPECTED_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} promotion inventory changed")
    if WAVE8_COMANCHE_HOLD_IDS != _EXPECTED_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} hold inventory changed")
    if WAVE8_COMANCHE_CONTRACT_IDS & WAVE8_COMANCHE_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion and hold inventories overlap")
    if wave8_comanche_audit_signature() != WAVE8_COMANCHE_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_COMANCHE_SOURCES}
    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_COMANCHE_ENTITIES}
    if len(source_by_id) != 10 or len(entity_by_id) != 9:
        raise ValueError(f"{_LANE_NAME} source/entity inventory changed")
    if len(source_by_id) != len(WAVE8_COMANCHE_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(entity_by_id) != len(WAVE8_COMANCHE_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")

    for source in WAVE8_COMANCHE_SOURCES:
        roles = list(map(str, source["evidence_roles"]))
        if not _is_sorted_unique(roles):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    forbidden_exact_names = {
        "comanche",
        "comanche indians",
        "comanche nation",
        "kiowa",
        "tonkawa",
    }
    for entity in WAVE8_COMANCHE_ENTITIES:
        if entity["start_year"] is None or entity["end_year"] is None:
            raise ValueError(f"{_LANE_NAME} identity is not time-bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern" not in note:
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if str(entity["name"]).casefold() in forbidden_exact_names:
            raise ValueError(f"{_LANE_NAME} installed a timeless identity")
        source_ids = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(source_ids) or not set(source_ids) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity provenance is not canonical")

    used_entity_ids: set[str] = set()
    for candidate_id, contract in WAVE8_COMANCHE_CONTRACTS.items():
        row_hash = str(contract["raw_row_sha256"])
        if len(row_hash) != 64 or any(char not in "0123456789abcdef" for char in row_hash):
            raise ValueError(f"{_LANE_NAME} invalid queue hash for {candidate_id}")
        if contract.get("result_type") != "win" or contract.get("winner_side") != 1:
            raise ValueError(f"{_LANE_NAME} non-direct result for {candidate_id}")
        if contract.get("source_outcome_override") is not False:
            raise ValueError(f"{_LANE_NAME} outcome override for {candidate_id}")

        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} canonical key drift for {candidate_id}")
        if canonical["date_precision"] != "day" or canonical["granularity"] != "engagement":
            raise ValueError(f"{_LANE_NAME} date/granularity drift for {candidate_id}")
        if not str(canonical["date_text"]).strip():
            raise ValueError(f"{_LANE_NAME} missing canonical date for {candidate_id}")

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} invalid opposing sides for {candidate_id}")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} unknown entity for {candidate_id}")
        used_entity_ids.update(side_1)
        used_entity_ids.update(side_2)

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} source provenance drift for {candidate_id}")
        if not _is_sorted_unique(families):
            raise ValueError(f"{_LANE_NAME} family provenance drift for {candidate_id}")
        if not outcomes or not set(outcomes) <= set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} direct source gap for {candidate_id}")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} non-outcome source for {candidate_id}")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome family drift for {candidate_id}")

    if used_entity_ids != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")

    for candidate_id, hold in WAVE8_COMANCHE_HOLDS.items():
        row_hash = str(hold["raw_row_sha256"])
        if len(row_hash) != 64 or any(char not in "0123456789abcdef" for char in row_hash):
            raise ValueError(f"{_LANE_NAME} invalid hold hash for {candidate_id}")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold provenance drift for {candidate_id}")
        if {"winner_side", "result_type", "side_1_entity_ids", "side_2_entity_ids"} & set(hold):
            raise ValueError(f"{_LANE_NAME} hold contains a rateable result")

    adobe_components = WAVE8_COMANCHE_HOLDS["hced-Adobe Walls1864-1"][
        "documented_coalition_components"
    ]
    if adobe_components != {
        "carson_column": [
            "First Cavalry, New Mexico Volunteers",
            "Jicarilla Apache scouts",
            "Ute scouts",
        ],
        "southern_plains_force": [
            "Comanche participants",
            "Kiowa participants",
            "Kiowa-Apache participants",
        ],
    }:
        raise ValueError(f"{_LANE_NAME} Adobe Walls coalition audit changed")

    if WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS != _EXPECTED_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    if WAVE8_COMANCHE_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} outcome override inventory changed")


def validate_wave8_comanche_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_COMANCHE_CONTRACTS,
        WAVE8_COMANCHE_HOLDS,
        lane_name=_LANE_NAME,
    )


def install_wave8_comanche_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_COMANCHE_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_comanche_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_COMANCHE_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_comanche_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_comanche_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_COMANCHE_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_comanche_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "holds": len(WAVE8_COMANCHE_HOLDS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_COMANCHE_ENTITIES),
        "new_sources": len(WAVE8_COMANCHE_SOURCES),
        "newly_rated_events": len(WAVE8_COMANCHE_CONTRACTS),
        "outcome_overrides": len(WAVE8_COMANCHE_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_COMANCHE_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_COMANCHE_RESERVED_IDS),
    }


def wave8_comanche_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_COMANCHE_CONTRACTS.values()
            ).items()
        )
    )


def wave8_comanche_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS,
    }
