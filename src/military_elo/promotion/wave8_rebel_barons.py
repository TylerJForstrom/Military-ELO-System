"""Candidate-keyed Wave 8 audit for HCED's exact ``Rebel Barons`` label.

The locked cohort contains six English civil-war rows from 1215 through 1266.
The label is not treated as a durable actor.  Every promoted side is an event-
or campaign-bounded formation attested for the particular siege, engagement,
or submission being rated; no result is inherited by England, a king, the
baronage, a family, or a modern state.

All six staged rows have a mechanically defensible side-one victory.  Axholme
is limited to Edward's containment operation and the rebels' negotiated
submission, not their later political or personal fates.  Bedford ends at the
garrison's surrender: the executions that followed are explicitly not modeled
as another competitive outcome.  Rochester in 1264 is limited to the defense
of the keep and the relief that caused the besiegers to withdraw.  There are no
draws, inferred strategic results, or silent dispositions in this lane.
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
    "WAVE8_REBEL_BARONS_CONTRACT_IDS",
    "WAVE8_REBEL_BARONS_CONTRACTS",
    "WAVE8_REBEL_BARONS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_REBEL_BARONS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_REBEL_BARONS_ENTITIES",
    "WAVE8_REBEL_BARONS_EXCLUSION_IDS",
    "WAVE8_REBEL_BARONS_EXCLUSIONS",
    "WAVE8_REBEL_BARONS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS",
    "WAVE8_REBEL_BARONS_EXTERNAL_OWNER_IDS",
    "WAVE8_REBEL_BARONS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_REBEL_BARONS_HOLD_IDS",
    "WAVE8_REBEL_BARONS_HOLDS",
    "WAVE8_REBEL_BARONS_INTEGRATION_DISPOSITIONS",
    "WAVE8_REBEL_BARONS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_REBEL_BARONS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_REBEL_BARONS_NONPROMOTIONS",
    "WAVE8_REBEL_BARONS_OUTCOME_OVERRIDES",
    "WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_REBEL_BARONS_RESERVED_IDS",
    "WAVE8_REBEL_BARONS_ROW_HASHES",
    "WAVE8_REBEL_BARONS_SOURCES",
    "WAVE8_REBEL_BARONS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS",
    "install_wave8_rebel_barons_entities",
    "install_wave8_rebel_barons_sources",
    "promote_wave8_rebel_barons_contracts",
    "validate_wave8_rebel_barons_integration_dispositions",
    "validate_wave8_rebel_barons_queue_contracts",
    "wave8_rebel_barons_audit_signature",
    "wave8_rebel_barons_cohort_counts",
    "wave8_rebel_barons_counts",
    "wave8_rebel_barons_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Rebel Barons actor audit"
_EVENT_ID_PREFIX = "hced_wave8_rebel_barons_"
_MODULE_OWNER = "military_elo.promotion.wave8_rebel_barons"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = True,
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


WAVE8_REBEL_BARONS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_rebel_barons_oakes_barons_war",
        "The Nature of War and its Impact on Society during the Barons' War, 1264-67",
        "https://theses.gla.ac.uk/6406/",
        "University of Glasgow",
        "doctoral_scholarly_military_history",
        "oakes_barons_war_thesis_2015",
        crosscheck=True,
    ),
    _source(
        "wave8_rebel_barons_prestwich_edward_i",
        "Edward I",
        "https://yalebooks.co.uk/book/9780300071573/edward-i/",
        "Yale University Press",
        "scholarly_historical_monograph",
        "prestwich_edward_i_1997",
        crosscheck=True,
    ),
    _source(
        "wave8_rebel_barons_carpenter_minority",
        "The Minority of Henry III",
        "https://books.google.com/books/about/The_Minority_of_Henry_III.html?id=93nNNQUyFwAC",
        "University of California Press",
        "scholarly_historical_monograph",
        "carpenter_minority_henry_iii_1990",
        crosscheck=True,
    ),
    _source(
        "wave8_rebel_barons_norgate_minority",
        "The Minority of Henry the Third",
        "https://www.gutenberg.org/files/54953/54953-h/54953-h.htm",
        "Macmillan; Project Gutenberg transcription",
        "primary_source_based_scholarly_synthesis",
        "norgate_minority_henry_iii_1912",
        crosscheck=True,
    ),
    _source(
        "wave8_rebel_barons_fine_rolls_bytham",
        "5 Henry III (28 October 1220-27 October 1221)",
        "https://finerollshenry3.org.uk/content/calendar/roll_015.html",
        "Henry III Fine Rolls Project",
        "scholarly_edition_of_primary_administrative_records",
        "fine_rolls_henry_iii_roll_015",
        outcome=False,
    ),
    _source(
        "wave8_rebel_barons_fine_rolls_bedford",
        "The Companions of Falkes de Breaute and the siege of Bedford Castle",
        "https://finerollshenry3.org.uk/content/month/fm-07-2007.html",
        "Henry III Fine Rolls Project",
        "scholarly_primary_source_commentary",
        "ray_fine_rolls_bedford_2007",
        crosscheck=True,
    ),
    _source(
        "wave8_rebel_barons_bedfordshire_archives",
        "Bedford Castle",
        "https://bedsarchives.bedford.gov.uk/CommunityArchives/Bedford/BedfordCastle.aspx",
        "Bedfordshire Archives and Bedford Borough Council",
        "institutional_archival_history",
        "bedfordshire_archives_bedford_castle",
        crosscheck=True,
    ),
    _source(
        "wave8_rebel_barons_magna_carta_rochester",
        "The fall of Rochester Castle",
        "https://magnacarta.cmp.uea.ac.uk/read/itinerary/The_fall_of_Rochester_Castle",
        "Magna Carta Project, University of East Anglia",
        "university_scholarly_primary_source_commentary",
        "vincent_magna_carta_rochester_1215",
        crosscheck=True,
    ),
    _source(
        "wave8_rebel_barons_english_heritage_rochester",
        "History of Rochester Castle",
        "https://www.english-heritage.org.uk/visit/places/rochester-castle/history/",
        "English Heritage",
        "official_heritage_history",
        "english_heritage_rochester_history",
        crosscheck=True,
    ),
    _source(
        "wave8_rebel_barons_historic_england_rochester",
        "Rochester Castle, National Heritage List for England entry 1011030",
        "https://historicengland.org.uk/listing/the-list/list-entry/1011030",
        "Historic England",
        "statutory_historic_environment_record",
        "historic_england_rochester_1011030",
        crosscheck=True,
    ),
    _source(
        "wave8_rebel_barons_derbyshire_her",
        "Site of the Battle of Chesterfield (apparent site), MDR5341",
        "https://her.derbyshire.gov.uk/Monument/MDR5341",
        "Derbyshire County Council Historic Environment Record",
        "official_historic_environment_record",
        "derbyshire_her_mdr5341",
        crosscheck=True,
    ),
)


_AXHOLME_ROYAL_ID = "lord_edward_royalist_containment_force_axholme_1265"
_AXHOLME_REBEL_ID = "montfort_de_eyville_wake_disinherited_force_axholme_1265"
_BYTHAM_ROYAL_ID = "henry_iii_royal_siege_host_bytham_1221"
_BYTHAM_REBEL_ID = "aumale_bytham_garrison_1221"
_BEDFORD_ROYAL_ID = "henry_iii_royal_siege_host_bedford_1224"
_BEDFORD_REBEL_ID = "william_de_breaute_bedford_garrison_1224"
_ROCHESTER_1215_ROYAL_ID = "king_john_royal_siege_army_rochester_1215"
_ROCHESTER_1215_REBEL_ID = "william_d_aubigny_baronial_garrison_rochester_1215"
_ROCHESTER_1264_ROYAL_ID = (
    "leybourne_warenne_garrison_and_royal_relief_force_rochester_1264"
)
_ROCHESTER_1264_REBEL_ID = "montfort_clare_baronial_siege_force_rochester_1264"
_CHESTERFIELD_ROYAL_ID = "henry_of_almain_royalist_force_chesterfield_1266"
_CHESTERFIELD_REBEL_ID = "ferrers_de_eyville_disinherited_force_chesterfield_1266"


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
        "continuity_note": note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_REBEL_BARONS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _AXHOLME_ROYAL_ID,
        "Lord Edward's royalist containment force in Axholme (1265)",
        "campaign_bounded_containment_force",
        1265,
        "Isle of Axholme, Lincolnshire",
        (
            "Bounded to the royalist forces and county levies used to contain the "
            "Axholme rebels through the November-December operation. No rating is "
            "inherited by Lord Edward, England, royalists generally, or any modern state."
        ),
        [
            "wave8_rebel_barons_oakes_barons_war",
            "wave8_rebel_barons_prestwich_edward_i",
        ],
    ),
    _entity(
        _AXHOLME_REBEL_ID,
        "Montfort-de Eyville-Wake Disinherited force in Axholme (1265)",
        "campaign_bounded_rebel_force",
        1265,
        "Isle of Axholme, Lincolnshire",
        (
            "Bounded to the Disinherited concentration contained in Axholme and "
            "represented in the Bickerdyke submission. No rating is inherited by "
            "the named leaders, rebel barons generally, their kin, or any modern state."
        ),
        [
            "wave8_rebel_barons_oakes_barons_war",
            "wave8_rebel_barons_prestwich_edward_i",
        ],
    ),
    _entity(
        _BYTHAM_ROYAL_ID,
        "Henry III's royal siege host at Castle Bytham (1221)",
        "event_bounded_siege_host",
        1221,
        "Castle Bytham, Lincolnshire",
        (
            "Bounded to the regency government's host that marched against and "
            "assaulted Castle Bytham on 3-8 February. No rating is inherited by "
            "Henry III, England, the royal household, or any modern state."
        ),
        [
            "wave8_rebel_barons_carpenter_minority",
            "wave8_rebel_barons_fine_rolls_bytham",
            "wave8_rebel_barons_norgate_minority",
        ],
    ),
    _entity(
        _BYTHAM_REBEL_ID,
        "Aumale's garrison at Castle Bytham (1221)",
        "event_bounded_siege_garrison",
        1221,
        "Castle Bytham, Lincolnshire",
        (
            "Bounded to the garrison that remained, resisted, and surrendered at "
            "Castle Bytham after William de Forz had fled. No rating is inherited "
            "by Aumale personally, his affinities, rebel barons, or any modern state."
        ),
        [
            "wave8_rebel_barons_carpenter_minority",
            "wave8_rebel_barons_norgate_minority",
        ],
    ),
    _entity(
        _BEDFORD_ROYAL_ID,
        "Henry III's royal siege host at Bedford Castle (1224)",
        "event_bounded_siege_host",
        1224,
        "Bedford Castle, Bedfordshire",
        (
            "Bounded to the royal host conducting the June-August siege of Bedford "
            "Castle. No rating is inherited by Henry III, England, later royal "
            "armies, or any modern state."
        ),
        [
            "wave8_rebel_barons_bedfordshire_archives",
            "wave8_rebel_barons_carpenter_minority",
            "wave8_rebel_barons_fine_rolls_bedford",
            "wave8_rebel_barons_norgate_minority",
        ],
    ),
    _entity(
        _BEDFORD_REBEL_ID,
        "William de Breaute's garrison at Bedford Castle (1224)",
        "event_bounded_siege_garrison",
        1224,
        "Bedford Castle, Bedfordshire",
        (
            "Bounded to the garrison commanded by William de Breaute while Falkes "
            "was absent. No rating is inherited by Falkes, William after surrender, "
            "their household, rebel barons, or any modern state."
        ),
        [
            "wave8_rebel_barons_bedfordshire_archives",
            "wave8_rebel_barons_fine_rolls_bedford",
            "wave8_rebel_barons_norgate_minority",
        ],
    ),
    _entity(
        _ROCHESTER_1215_ROYAL_ID,
        "King John's royal siege army at Rochester (1215)",
        "event_bounded_siege_army",
        1215,
        "Rochester Castle, Kent",
        (
            "Bounded to John's army during the 11 October-30 November siege and "
            "capture of Rochester Castle. No rating is inherited by King John, "
            "England, Plantagenets generally, or any modern state."
        ),
        [
            "wave8_rebel_barons_english_heritage_rochester",
            "wave8_rebel_barons_historic_england_rochester",
            "wave8_rebel_barons_magna_carta_rochester",
        ],
    ),
    _entity(
        _ROCHESTER_1215_REBEL_ID,
        "William d'Aubigny's baronial garrison at Rochester (1215)",
        "event_bounded_siege_garrison",
        1215,
        "Rochester Castle, Kent",
        (
            "Bounded to William d'Aubigny and the castle defenders who surrendered "
            "on 30 November. No rating is inherited by d'Aubigny, the London "
            "baronial coalition, rebel barons generally, or any modern state."
        ),
        [
            "wave8_rebel_barons_english_heritage_rochester",
            "wave8_rebel_barons_historic_england_rochester",
            "wave8_rebel_barons_magna_carta_rochester",
        ],
    ),
    _entity(
        _ROCHESTER_1264_ROYAL_ID,
        "Leybourne-Warenne garrison and royal relief force at Rochester (1264)",
        "event_bounded_defense_and_relief_force",
        1264,
        "Rochester, Kent",
        (
            "Bounded to the castle defense associated with Roger de Leybourne and "
            "John de Warenne together with the approaching royal relief that ended "
            "the siege. No rating is inherited by Henry III, royalists, the named "
            "lords in other actions, or any modern state."
        ),
        [
            "wave8_rebel_barons_english_heritage_rochester",
            "wave8_rebel_barons_historic_england_rochester",
            "wave8_rebel_barons_oakes_barons_war",
        ],
    ),
    _entity(
        _ROCHESTER_1264_REBEL_ID,
        "Montfort-Clare baronial siege force at Rochester (1264)",
        "event_bounded_siege_force",
        1264,
        "Rochester, Kent",
        (
            "Bounded to Simon de Montfort and Gilbert de Clare's besieging force "
            "from 17 to 26 April. No rating is inherited by either leader, their "
            "affinities, rebel barons generally, or any modern state."
        ),
        [
            "wave8_rebel_barons_english_heritage_rochester",
            "wave8_rebel_barons_historic_england_rochester",
            "wave8_rebel_barons_oakes_barons_war",
        ],
    ),
    _entity(
        _CHESTERFIELD_ROYAL_ID,
        "Henry of Almain's royalist force at Chesterfield (1266)",
        "event_bounded_field_force",
        1266,
        "Chesterfield, Derbyshire",
        (
            "Bounded to the royalist force that surprised and routed the rebel "
            "base at Chesterfield on 15 May. No rating is inherited by Henry of "
            "Almain, royalists generally, England, or any modern state."
        ),
        [
            "wave8_rebel_barons_derbyshire_her",
            "wave8_rebel_barons_oakes_barons_war",
        ],
    ),
    _entity(
        _CHESTERFIELD_REBEL_ID,
        "Ferrers-de Eyville Disinherited force at Chesterfield (1266)",
        "event_bounded_rebel_force",
        1266,
        "Chesterfield, Derbyshire",
        (
            "Bounded to the Disinherited fighters present at the Chesterfield base "
            "when Henry of Almain attacked; absent hunting contingents are excluded. "
            "No rating is inherited by Ferrers, de Eyville, their followers in "
            "other actions, rebel barons generally, or any modern state."
        ),
        [
            "wave8_rebel_barons_derbyshire_her",
            "wave8_rebel_barons_oakes_barons_war",
        ],
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


WAVE8_REBEL_BARONS_ROW_HASHES: dict[str, str] = {
    "hced-Axholme1265-1": "8069ce55234af30bfe1b9cd01e413ed9d312a65aa9e23f64257fe88f775c7dd5",
    "hced-Bedford1224-1": "092fd67664ebd3d744544a5a5546b71357b6057143dd93c45a18e1724328e03d",
    "hced-Bytham1221-1": "24ad76f2441c847056deb44a3c04a65b7b3e5dd1cd57ea7b1598eaa50ab4d155",
    "hced-Chesterfield1266-1": "7750bc6e78bc3599ff1160506e6258c124f454d6d12b9f7896e185ceedbc51c9",
    "hced-Rochester1215-1": "1a1723a2fbf26a6072ec8841b36dac971692eb3b8bb42c2206773084d55fe6b0",
    "hced-Rochester1264-1": "717e7e878f901501d5a1de0ba59e48a3876b6609604f4bb059766237f7ea5fc2",
}


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_REBEL_BARONS_SOURCES
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
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_REBEL_BARONS_ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": "civil_war",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
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


WAVE8_REBEL_BARONS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Rochester1215-1": _contract(
        "hced-Rochester1215-1",
        _canonical(
            "Siege of Rochester Castle (1215)",
            1215,
            "11 October-30 November 1215",
            date_precision="day_range",
            granularity="siege",
        ),
        "first_barons_war_1215_1217",
        [_ROCHESTER_1215_ROYAL_ID],
        [_ROCHESTER_1215_REBEL_ID],
        [
            "wave8_rebel_barons_english_heritage_rochester",
            "wave8_rebel_barons_historic_england_rochester",
            "wave8_rebel_barons_magna_carta_rochester",
        ],
        [
            "wave8_rebel_barons_english_heritage_rochester",
            "wave8_rebel_barons_historic_england_rochester",
            "wave8_rebel_barons_magna_carta_rochester",
        ],
        (
            "John's siege army captured the castle after the keep's defenders, "
            "commanded by William d'Aubigny, exhausted their provisions and "
            "surrendered on 30 November. The contract rates only that siege."
        ),
        confidence=0.98,
    ),
    "hced-Bytham1221-1": _contract(
        "hced-Bytham1221-1",
        _canonical(
            "Siege of Castle Bytham",
            1221,
            "3-8 February 1221",
            date_precision="day_range",
            granularity="siege",
        ),
        "post_first_barons_war_royal_recovery_1221_1224",
        [_BYTHAM_ROYAL_ID],
        [_BYTHAM_REBEL_ID],
        [
            "wave8_rebel_barons_carpenter_minority",
            "wave8_rebel_barons_fine_rolls_bytham",
            "wave8_rebel_barons_norgate_minority",
        ],
        [
            "wave8_rebel_barons_carpenter_minority",
            "wave8_rebel_barons_norgate_minority",
        ],
        (
            "The royal host assaulted Castle Bytham and accepted the garrison's "
            "unconditional surrender on 8 February. William de Forz had fled, so "
            "the losing identity is the remaining garrison, not Aumale personally."
        ),
        confidence=0.96,
    ),
    "hced-Bedford1224-1": _contract(
        "hced-Bedford1224-1",
        _canonical(
            "Siege of Bedford Castle (1224)",
            1224,
            "20 June-15 August 1224",
            date_precision="day_range",
            granularity="siege",
        ),
        "post_first_barons_war_royal_recovery_1221_1224",
        [_BEDFORD_ROYAL_ID],
        [_BEDFORD_REBEL_ID],
        [
            "wave8_rebel_barons_bedfordshire_archives",
            "wave8_rebel_barons_carpenter_minority",
            "wave8_rebel_barons_fine_rolls_bedford",
            "wave8_rebel_barons_norgate_minority",
        ],
        [
            "wave8_rebel_barons_bedfordshire_archives",
            "wave8_rebel_barons_fine_rolls_bedford",
            "wave8_rebel_barons_norgate_minority",
        ],
        (
            "Henry III's host forced the surrender of the garrison led by William "
            "de Breaute while Falkes was absent. The contract terminates at "
            "surrender; the subsequent hanging of surviving defenders is a "
            "post-surrender execution, not a second competitive result."
        ),
        confidence=0.98,
    ),
    "hced-Rochester1264-1": _contract(
        "hced-Rochester1264-1",
        _canonical(
            "Siege and relief of Rochester Castle (1264)",
            1264,
            "17-26 April 1264",
            date_precision="day_range",
            granularity="siege_and_relief",
        ),
        "second_barons_war_1264",
        [_ROCHESTER_1264_ROYAL_ID],
        [_ROCHESTER_1264_REBEL_ID],
        [
            "wave8_rebel_barons_english_heritage_rochester",
            "wave8_rebel_barons_historic_england_rochester",
            "wave8_rebel_barons_oakes_barons_war",
        ],
        [
            "wave8_rebel_barons_english_heritage_rochester",
            "wave8_rebel_barons_historic_england_rochester",
            "wave8_rebel_barons_oakes_barons_war",
        ],
        (
            "The Leybourne-Warenne defense retained the keep after the baronial "
            "force breached the town and outer castle; the approach of Henry III "
            "and Lord Edward caused Montfort and Clare to abandon the siege. The "
            "winner is the bounded defense-and-relief formation, not generic England."
        ),
        confidence=0.95,
    ),
    "hced-Axholme1265-1": _contract(
        "hced-Axholme1265-1",
        _canonical(
            "Axholme campaign and submission",
            1265,
            "November-December 1265",
            date_precision="month_range",
            granularity="campaign_and_submission",
        ),
        "post_evesham_disinherited_1265_1266",
        [_AXHOLME_ROYAL_ID],
        [_AXHOLME_REBEL_ID],
        [
            "wave8_rebel_barons_oakes_barons_war",
            "wave8_rebel_barons_prestwich_edward_i",
        ],
        [
            "wave8_rebel_barons_oakes_barons_war",
            "wave8_rebel_barons_prestwich_edward_i",
        ],
        (
            "Edward used county forces and temporary bridges to contain the "
            "Disinherited in Axholme, producing negotiated submission at "
            "Bickerdyke in December. Only containment and submission are rated; "
            "no later punishment, pardon, or durable strategic defeat is inferred."
        ),
        confidence=0.89,
    ),
    "hced-Chesterfield1266-1": _contract(
        "hced-Chesterfield1266-1",
        _canonical("Battle of Chesterfield", 1266, "15 May 1266"),
        "post_evesham_disinherited_1265_1266",
        [_CHESTERFIELD_ROYAL_ID],
        [_CHESTERFIELD_REBEL_ID],
        [
            "wave8_rebel_barons_derbyshire_her",
            "wave8_rebel_barons_oakes_barons_war",
        ],
        [
            "wave8_rebel_barons_derbyshire_her",
            "wave8_rebel_barons_oakes_barons_war",
        ],
        (
            "Henry of Almain surprised and routed the Disinherited base and "
            "captured Robert de Ferrers. De Eyville and guards broke out, and "
            "contingents away hunting are excluded from the losing formation; the "
            "contract does not rate every rebel baron in the region."
        ),
        confidence=0.96,
    ),
}


# Every non-promotion disposition is explicit even though this fully attested
# cohort requires none.  These immutable empty inventories prevent silent drops.
WAVE8_REBEL_BARONS_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_REBEL_BARONS_CROSS_LANE_DISPOSITIONS = (
    WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS
)
WAVE8_REBEL_BARONS_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_REBEL_BARONS_HOLDS,
    **WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS,
}
WAVE8_REBEL_BARONS_EXCLUSIONS = WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS

WAVE8_REBEL_BARONS_CONTRACT_IDS = frozenset(WAVE8_REBEL_BARONS_CONTRACTS)
WAVE8_REBEL_BARONS_HOLD_IDS = frozenset(WAVE8_REBEL_BARONS_HOLDS)
WAVE8_REBEL_BARONS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS
)
WAVE8_REBEL_BARONS_EXCLUSION_IDS = WAVE8_REBEL_BARONS_TERMINAL_EXCLUSION_IDS
WAVE8_REBEL_BARONS_EXTERNAL_OWNER_IDS = frozenset(
    WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS
)
WAVE8_REBEL_BARONS_RESERVED_IDS = (
    WAVE8_REBEL_BARONS_CONTRACT_IDS
    | WAVE8_REBEL_BARONS_HOLD_IDS
    | WAVE8_REBEL_BARONS_TERMINAL_EXCLUSION_IDS
)
WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_REBEL_BARONS_ROW_HASHES
)


WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Axholme1265-1": {
        "actions": ["withhold_point"],
        "reason": (
            "A single Axholme coordinate cannot represent the marshland containment "
            "operation, temporary bridge line, and Bickerdyke negotiation site."
        ),
    },
    "hced-Bedford1224-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The staged town coordinate is not a source-audited point for the "
            "eight-week castle, siegeworks, assaults, and mining footprint."
        ),
    },
    "hced-Bytham1221-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The village coordinate is not independently authenticated as the "
            "precise Castle Bytham siege and assault footprint."
        ),
    },
    "hced-Chesterfield1266-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The Historic Environment Record identifies an apparent, not exact, "
            "site and the action extended through the town; one centroid is unsafe."
        ),
    },
    "hced-Rochester1215-1": {
        "actions": ["withhold_point"],
        "reason": (
            "A city coordinate cannot represent the castle, siegeworks, mining, "
            "and assault footprint of the six-week 1215 siege."
        ),
    },
    "hced-Rochester1264-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The action covered the bridge, city, outer castle, keep, and an "
            "approaching relief force; the shared Rochester centroid is not enough."
        ),
    },
}
WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_REASONS
)
WAVE8_REBEL_BARONS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_REBEL_BARONS_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_REBEL_BARONS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_REBEL_BARONS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_REBEL_BARONS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_REBEL_BARONS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS,
    **WAVE8_REBEL_BARONS_IWBD_DUPLICATE_DISPOSITIONS,
    **WAVE8_REBEL_BARONS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
}


def _duplicate_audit(year: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": sorted({normalize_label(alias) for alias in aliases}),
        "years": [year, year],
    }


WAVE8_REBEL_BARONS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Axholme1265-1": _duplicate_audit(
        1265,
        "Axholme",
        "Axholme campaign and submission",
        "Bickerdyke",
        "Bycarr's Dyke",
        "Isle of Axholme",
        "Siege of Axholme",
    ),
    "hced-Bedford1224-1": _duplicate_audit(
        1224,
        "Bedford",
        "Bedford Castle",
        "Siege of Bedford",
        "Siege of Bedford Castle",
        "Siege of Bedford Castle (1224)",
    ),
    "hced-Bytham1221-1": _duplicate_audit(
        1221,
        "Bytham",
        "Castle Bytham",
        "Siege of Bytham",
        "Siege of Castle Bytham",
        "War of Bytham",
    ),
    "hced-Chesterfield1266-1": _duplicate_audit(
        1266,
        "Battle of Chesterfield",
        "Battle of Chesterfield 1266",
        "Chesterfield",
    ),
    "hced-Rochester1215-1": _duplicate_audit(
        1215,
        "Rochester",
        "Rochester Castle",
        "Siege of Rochester",
        "Siege of Rochester Castle",
        "Siege of Rochester Castle (1215)",
    ),
    "hced-Rochester1264-1": _duplicate_audit(
        1264,
        "Rochester",
        "Rochester Castle",
        "Rochester siege and relief",
        "Siege and relief of Rochester Castle (1264)",
        "Siege of Rochester",
        "Siege of Rochester Castle",
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_REBEL_BARONS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_REBEL_BARONS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_REBEL_BARONS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_REBEL_BARONS_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_REBEL_BARONS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(
            WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS
        ),
        "external_owner_dispositions": (
            WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS
        ),
        "holds": WAVE8_REBEL_BARONS_HOLDS,
        "integration_dispositions": WAVE8_REBEL_BARONS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_REBEL_BARONS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": WAVE8_REBEL_BARONS_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": (
            WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_REASONS
        ),
        "outcome_overrides": WAVE8_REBEL_BARONS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS
        ),
        "row_hashes": WAVE8_REBEL_BARONS_ROW_HASHES,
        "sources": WAVE8_REBEL_BARONS_SOURCES,
        "terminal_exclusions": WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS,
    }


def wave8_rebel_barons_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label adjudication."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_REBEL_BARONS_FINAL_AUDIT_SIGNATURE = (
    "00a0e4a8e50618b0c0da50750ad9e2af3e6f8adff2ca1af8a803045d7f3e1d45"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_REBEL_BARONS_CONTRACTS),
        len(WAVE8_REBEL_BARONS_HOLDS),
        len(WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS),
        len(WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS),
    ) != (6, 0, 0, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_REBEL_BARONS_ENTITIES), len(WAVE8_REBEL_BARONS_SOURCES)) != (
        12,
        11,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if (
        WAVE8_REBEL_BARONS_RESERVED_IDS | WAVE8_REBEL_BARONS_EXTERNAL_OWNER_IDS
        != WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    dispositions = (
        WAVE8_REBEL_BARONS_CONTRACT_IDS,
        WAVE8_REBEL_BARONS_HOLD_IDS,
        WAVE8_REBEL_BARONS_TERMINAL_EXCLUSION_IDS,
        WAVE8_REBEL_BARONS_EXTERNAL_OWNER_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(len(dispositions))
        for j in range(i + 1, len(dispositions))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if wave8_rebel_barons_audit_signature() != WAVE8_REBEL_BARONS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_REBEL_BARONS_SOURCES
    }
    if len(source_by_id) != len(WAVE8_REBEL_BARONS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(
        {str(source["source_family_id"]) for source in WAVE8_REBEL_BARONS_SOURCES}
    ) != len(WAVE8_REBEL_BARONS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_REBEL_BARONS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_REBEL_BARONS_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_REBEL_BARONS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {"england", "king henry iii", "king john", "rebel barons"}
    for entity in WAVE8_REBEL_BARONS_ENTITIES:
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} identity is not event/campaign bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern state" not in note:
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic identity")
        if not str(entity["kind"]).startswith(("event_bounded_", "campaign_bounded_")):
            raise ValueError(f"{_LANE_NAME} identity is not explicitly bounded")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_new_entities: set[str] = set()
    used_sources: set[str] = set()
    allowed_granularities = {
        "campaign_and_submission",
        "engagement",
        "siege",
        "siege_and_relief",
    }
    for candidate_id, contract in WAVE8_REBEL_BARONS_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_REBEL_BARONS_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["year_low"] != canonical["year_high"]:
            raise ValueError(f"{_LANE_NAME} promoted an unbounded year window")
        if canonical["granularity"] not in allowed_granularities:
            raise ValueError(f"{_LANE_NAME} promoted unsupported granularity")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        participants = set(side_1) | set(side_2)
        if not participants <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses a non-bounded identity")
        used_new_entities.update(participants)
        year = int(canonical["year_low"])
        if any(
            not int(entity_by_id[entity_id]["start_year"])
            <= year
            <= int(entity_by_id[entity_id]["end_year"])
            for entity_id in participants
        ):
            raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["actor_override"] is not True
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} outcome or actor policy drifted")
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
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")
    used_sources.update(
        source_id
        for entity in WAVE8_REBEL_BARONS_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_REBEL_BARONS_HOLDS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited hold")
    if WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited terminal exclusion")
    if WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited external owner")
    if WAVE8_REBEL_BARONS_CROSS_LANE_DISPOSITIONS is not (
        WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} external ownership alias drifted")
    if WAVE8_REBEL_BARONS_EXCLUSIONS is not WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion alias drifted")
    if (
        WAVE8_REBEL_BARONS_OUTCOME_OVERRIDES
        or WAVE8_REBEL_BARONS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_REBEL_BARONS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_REBEL_BARONS_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")

    if WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_REBEL_BARONS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_REBEL_BARONS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unsupported country quarantine")
    if set(WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location-review inventory changed")
    for review in WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_REASONS.values():
        if (
            not review["reason"]
            or not _is_sorted_unique(review["actions"])
            or review["actions"] != ["withhold_point"]
        ):
            raise ValueError(f"{_LANE_NAME} location review is not canonical")

    if set(WAVE8_REBEL_BARONS_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for candidate_id, audit in WAVE8_REBEL_BARONS_IWBD_ZERO_OVERLAP_AUDIT.items():
        aliases = list(map(str, audit["aliases"]))
        years = list(map(int, audit["years"]))
        if not aliases or not _is_sorted_unique(aliases):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if any(alias != normalize_label(alias) for alias in aliases):
            raise ValueError(f"{_LANE_NAME} duplicate alias is not normalized")
        if years != [years[0], years[0]]:
            raise ValueError(f"{_LANE_NAME} duplicate year window drifted")
        canonical = WAVE8_REBEL_BARONS_CONTRACTS[candidate_id]["canonical_event"]
        canonical_key = (int(canonical["year_low"]), normalize_label(canonical["name"]))
        item_keys = {(years[0], alias) for alias in aliases}
        if canonical_key not in item_keys:
            raise ValueError(f"{_LANE_NAME} canonical duplicate audit is incomplete")


def _is_exact_rebel_barons_label(value: Any) -> bool:
    return normalize_label(value) == "rebel barons"


def validate_wave8_rebel_barons_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all six exact-label rows and immutable queue fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_REBEL_BARONS_CONTRACTS,
        WAVE8_REBEL_BARONS_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_rebel_barons_label(row.get("side_1_raw"))
        or _is_exact_rebel_barons_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Rebel Barons inventory changed: "
            f"{sorted(exact_label_ids)}"
        )
    return {
        "external_owner_contracts": len(WAVE8_REBEL_BARONS_EXTERNAL_OWNER_IDS),
        "holds": len(WAVE8_REBEL_BARONS_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": (
            result["reviewed_hced_rows"]
            + len(WAVE8_REBEL_BARONS_EXTERNAL_OWNER_IDS)
        ),
        "terminal_exclusions": len(WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS),
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
    for audit in WAVE8_REBEL_BARONS_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
}


def validate_wave8_rebel_barons_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed if another queue or release lane adds an unreviewed twin."""

    validate_wave8_rebel_barons_queue_contracts(hced_rows)
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS
        and (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if hced_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_matches}"
        )
    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if iwbd_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_matches}"
        )
    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id")
        not in WAVE8_REBEL_BARONS_CONTRACT_IDS
        and (_row_year(event), normalize_label(event.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_matches}"
        )
    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_REBEL_BARONS_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_REBEL_BARONS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(
            WAVE8_REBEL_BARONS_EXTERNAL_OWNER_IDS
        ),
        "integration_dispositions": len(
            WAVE8_REBEL_BARONS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_REBEL_BARONS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_REBEL_BARONS_IWBD_ZERO_OVERLAP_AUDIT
        ),
    }


def install_wave8_rebel_barons_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_REBEL_BARONS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_rebel_barons_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_REBEL_BARONS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_REBEL_BARONS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_rebel_barons_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_rebel_barons_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_REBEL_BARONS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_rebel_barons_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_REBEL_BARONS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_rebel_barons_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_REBEL_BARONS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_REBEL_BARONS_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_REBEL_BARONS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(
            WAVE8_REBEL_BARONS_EXTERNAL_OWNER_IDS
        ),
        "holds": len(WAVE8_REBEL_BARONS_HOLDS),
        "integration_dispositions": len(
            WAVE8_REBEL_BARONS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_REBEL_BARONS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_REBEL_BARONS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_REBEL_BARONS_ENTITIES),
        "new_sources": len(WAVE8_REBEL_BARONS_SOURCES),
        "newly_rated_events": len(WAVE8_REBEL_BARONS_CONTRACTS),
        "outcome_overrides": len(WAVE8_REBEL_BARONS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_REBEL_BARONS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS),
        "terminal_exclusions": len(WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS),
    }


def wave8_rebel_barons_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_REBEL_BARONS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS,
    }
