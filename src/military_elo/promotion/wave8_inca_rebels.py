"""Candidate-keyed Wave 8 audit for HCED's exact ``Inca Rebels`` label.

The four locked rows span two different political and military phases.  The
1536-1537 Cuzco revolt and Ollantaytambo action belong to Manco Inca's first
anti-conquest campaign; Huayna Pucara belongs to the final 1572 invasion of
the independent Vilcabamba state under Tupac Amaru.  They therefore cannot be
resolved through a timeless Inca, Peru, rebel, or Spanish-colonial identity.

Three rows have source-attested tactical outcomes and receive separate,
event-bounded formations.  The row dated Cuzco 1535 is terminally excluded:
the independently reviewed chronology places Manco's siege in 1536-1537, and
the queue already contains the same siege under 1537.  Rating both would
double-count one operation, while moving the 1535 row to a different year
would violate the locked-row contract.

No unknown is converted to a draw, no generic alias is installed, and every
promoted point is withheld pending a dedicated battlefield-location audit.
The modern country value Peru is retained.
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
    "WAVE8_INCA_REBELS_CONTRACT_IDS",
    "WAVE8_INCA_REBELS_CONTRACTS",
    "WAVE8_INCA_REBELS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_INCA_REBELS_ENTITIES",
    "WAVE8_INCA_REBELS_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_INCA_REBELS_EXCLUSION_IDS",
    "WAVE8_INCA_REBELS_EXCLUSIONS",
    "WAVE8_INCA_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_INCA_REBELS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_INCA_REBELS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_INCA_REBELS_FUNNEL_EVENT_CANDIDATE_ID_SHA256",
    "WAVE8_INCA_REBELS_HOLD_IDS",
    "WAVE8_INCA_REBELS_HOLDS",
    "WAVE8_INCA_REBELS_INTEGRATION_DISPOSITIONS",
    "WAVE8_INCA_REBELS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_INCA_REBELS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_INCA_REBELS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_INCA_REBELS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_INCA_REBELS_NONPROMOTIONS",
    "WAVE8_INCA_REBELS_OUTCOME_OVERRIDES",
    "WAVE8_INCA_REBELS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_INCA_REBELS_RELATED_HCED_DISPOSITIONS",
    "WAVE8_INCA_REBELS_RESERVED_IDS",
    "WAVE8_INCA_REBELS_ROW_HASHES",
    "WAVE8_INCA_REBELS_SOURCES",
    "WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS",
    "WAVE8_INCA_REBELS_TOUCHED_CANDIDATE_IDS",
    "install_wave8_inca_rebels_entities",
    "install_wave8_inca_rebels_sources",
    "promote_wave8_inca_rebels_contracts",
    "validate_wave8_inca_rebels_integration_dispositions",
    "validate_wave8_inca_rebels_queue_contracts",
    "wave8_inca_rebels_audit_signature",
    "wave8_inca_rebels_cohort_counts",
    "wave8_inca_rebels_counts",
    "wave8_inca_rebels_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Inca Rebels actor audit"
_EVENT_ID_PREFIX = "hced_wave8_inca_rebels_"
_MODULE_OWNER = "military_elo.promotion.wave8_inca_rebels"

_CUZCO_SPANISH_ID = "pizarro_spanish_allied_garrison_cuzco_1536_1537"
_CUZCO_INCA_ID = "manco_inca_rebel_siege_army_cuzco_1536_1537"
_OLLANTAY_INCA_ID = "manco_inca_ollantaytambo_defenders_1537"
_OLLANTAY_SPANISH_ID = "hernando_pizarro_ollantaytambo_expedition_1537"
_HUAYNA_SPANISH_ID = (
    "hurtado_arbieto_spanish_andean_expedition_huayna_pucara_1572"
)
_HUAYNA_INCA_ID = "tupac_amaru_vilcabamba_defenders_huayna_pucara_1572"

_EXISTING_INCA_ENTITY_ID = "clio_pe_inca_emp_1440_816cd40c"
_EXISTING_INCA_EVENTS = {
    "hced-Cajamarca1532-1": "hced_label_hced_cajamarca1532_1",
    "hced-Teocajas1534-1": "hced_label_hced_teocajas1534_1",
    "hced-Vilcaconga1524-1": "hced_label_hced_vilcaconga1524_1",
}


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool,
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


WAVE8_INCA_REBELS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_inca_rebels_titu_cusi_bauer",
        "An Inca Account of the Conquest of Peru",
        "https://www.ubcpress.ca/an-inca-account-of-the-conquest-of-peru",
        "University Press of Colorado / UBC Press",
        "translated_indigenous_primary_source",
        "titu_cusi_bauer_2005",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_inca_rebels_himmerich_cuzco",
        "The 1536 Siege of Cuzco: An Analysis of Inca and Spanish Warfare",
        "https://digitalrepository.unm.edu/clahr/vol7/iss4/2/",
        "Colonial Latin American Historical Review, University of New Mexico",
        "peer_reviewed_scholarly_article",
        "himmerich_y_valencia_cuzco_1998",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_inca_rebels_sheppard_cuzco",
        "Cuzco 1536-37: Battle for the Heart of the Inca Empire",
        "https://books.google.com/books?id=ADctEAAAQBAJ",
        "Bloomsbury / Osprey Campaign",
        "scholarly_military_history",
        "sheppard_cuzco_2021",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_inca_rebels_lavalle_pizarro",
        "Francisco Pizarro: El ano de todos los peligros (1536-1537)",
        "https://books.openedition.org/ifea/940",
        "Institut francais d'etudes andines",
        "scholarly_monograph_chapter",
        "lavalle_francisco_pizarro_2004",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_inca_rebels_pbs_ollantaytambo",
        "Conquistadors: Pizarro - the Great Rebellion and Ollantaytambo",
        "https://www.pbs.org/conquistadors/pizarro/pizarro_i03.html",
        "PBS",
        "public_history_documentary_reference",
        "pbs_conquistadors_pizarro_2001",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_inca_rebels_bauer_vilcabamba",
        "Voices from Vilcabamba: Accounts Chronicling the Fall of the Inca Empire",
        "https://upcolorado.com/media/acfupload/9781607324263_sample.pdf",
        "University Press of Colorado",
        "scholarly_edited_primary_sources",
        "bauer_vilcabamba_2016",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_inca_rebels_murua_huayna_pucara",
        "The General History of Peru, Book 1, chapter 81",
        "https://www.jstor.org/stable/jj.20367929.88",
        "University Press of Colorado / JSTOR",
        "translated_early_colonial_chronicle",
        "murua_bauer_gamarra_gonzales_2024",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_inca_rebels_oxford_vilcabamba",
        "Vilcabamba: Last Stronghold of the Inca",
        "https://doi.org/10.1093/oxfordhb/9780190219352.013.27",
        "Oxford University Press",
        "scholarly_handbook_chapter",
        "lee_oxford_vilcabamba_2018",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_inca_rebels_casevitz_huayna_pucara",
        "Al este de los Andes: sociedades amazonicas y andinas, siglos XV-XVII",
        (
            "https://centroderecursos.cultura.pe/sites/default/files/rb/pdf/"
            "Al-este-de-los-Andes-Relaciones-entre-las-sociedades-amazonicas-y-"
            "andinas-entre-los-siglos-XV-y-XVII.pdf"
        ),
        "Ministerio de Cultura del Peru / IFEA",
        "scholarly_edited_volume",
        "renard_casevitz_east_andes_2008",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_inca_rebels_treccani_cuzco",
        "Cuzco",
        "https://www.treccani.it/enciclopedia/cuzco/",
        "Istituto della Enciclopedia Italiana",
        "scholarly_encyclopedia",
        "treccani_cuzco",
        outcome=True,
        crosscheck=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    boundary_note: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start_year,
        "end_year": end_year,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No rating is inherited from or passed to the Inca Empire, the "
            "Neo-Inca state outside this operation, Peru, Spain, Indigenous "
            "allies as timeless peoples, or another rebel or colonial force."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_INCA_REBELS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _CUZCO_SPANISH_ID,
        "Hernando Pizarro's Spanish-allied garrison at Cuzco (1536-1537)",
        "event_bounded_siege_defense_coalition",
        1536,
        1537,
        "Cuzco and its immediate defenses",
        (
            "Bounded to the Spaniards and Cañari, Chachapoya, Huanca, and other "
            "Andean allies who held Cuzco during Manco Inca's siege."
        ),
        [
            "wave8_inca_rebels_himmerich_cuzco",
            "wave8_inca_rebels_lavalle_pizarro",
            "wave8_inca_rebels_sheppard_cuzco",
            "wave8_inca_rebels_titu_cusi_bauer",
        ],
    ),
    _entity(
        _CUZCO_INCA_ID,
        "Manco Inca's siege army at Cuzco (1536-1537)",
        "event_bounded_rebel_siege_coalition",
        1536,
        1537,
        "Cuzco basin",
        (
            "Bounded to Manco Inca's four-suyu mobilization and commanders around "
            "Cuzco; it ends with the failed siege and withdrawal."
        ),
        [
            "wave8_inca_rebels_himmerich_cuzco",
            "wave8_inca_rebels_lavalle_pizarro",
            "wave8_inca_rebels_sheppard_cuzco",
            "wave8_inca_rebels_titu_cusi_bauer",
        ],
    ),
    _entity(
        _OLLANTAY_INCA_ID,
        "Manco Inca's defenders at Ollantaytambo (1537)",
        "event_bounded_fortified_field_force",
        1537,
        1537,
        "Ollantaytambo and the Mascabamba plain",
        (
            "Bounded to Manco Inca's troops defending the terraces, town, river "
            "approaches, and flooded plain during the January action."
        ),
        [
            "wave8_inca_rebels_lavalle_pizarro",
            "wave8_inca_rebels_pbs_ollantaytambo",
            "wave8_inca_rebels_sheppard_cuzco",
            "wave8_inca_rebels_titu_cusi_bauer",
        ],
    ),
    _entity(
        _OLLANTAY_SPANISH_ID,
        "Hernando Pizarro's expedition at Ollantaytambo (1537)",
        "event_bounded_assault_coalition",
        1537,
        1537,
        "Ollantaytambo and the Mascabamba plain",
        (
            "Bounded to Hernando Pizarro's mounted and foot expedition and its "
            "Andean auxiliaries in the failed January assault."
        ),
        [
            "wave8_inca_rebels_lavalle_pizarro",
            "wave8_inca_rebels_pbs_ollantaytambo",
            "wave8_inca_rebels_sheppard_cuzco",
            "wave8_inca_rebels_titu_cusi_bauer",
        ],
    ),
    _entity(
        _HUAYNA_SPANISH_ID,
        "Hurtado de Arbieto's Spanish-Andean force at Huayna Pucara (1572)",
        "event_bounded_colonial_expedition",
        1572,
        1572,
        "Vilcabamba road and Huayna Pucara",
        (
            "Bounded to the royal expedition under Martin Hurtado de Arbieto, "
            "including Spanish companies and Cañari, Chachapoya, and other "
            "Andean allies engaged at the fortified ridge."
        ),
        [
            "wave8_inca_rebels_bauer_vilcabamba",
            "wave8_inca_rebels_casevitz_huayna_pucara",
            "wave8_inca_rebels_murua_huayna_pucara",
            "wave8_inca_rebels_oxford_vilcabamba",
        ],
    ),
    _entity(
        _HUAYNA_INCA_ID,
        "Tupac Amaru's Vilcabamba defenders at Huayna Pucara (1572)",
        "event_bounded_fortress_defense",
        1572,
        1572,
        "Vilcabamba road and Huayna Pucara",
        (
            "Bounded to the Vilcabamba captains and Anti archers defending the "
            "last fortified approach under Tupac Amaru's royal authority."
        ),
        [
            "wave8_inca_rebels_bauer_vilcabamba",
            "wave8_inca_rebels_casevitz_huayna_pucara",
            "wave8_inca_rebels_murua_huayna_pucara",
            "wave8_inca_rebels_oxford_vilcabamba",
        ],
    ),
)


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str = "year",
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


WAVE8_INCA_REBELS_ROW_HASHES: dict[str, str] = {
    "hced-Cuzco1535-1": (
        "3709c9a9a7ca767d971d893c552ced7ba0001fb8f68896252a12fdf6608cf875"
    ),
    "hced-Cuzco1537-1": (
        "3447079fefdc651c7b57d59c6b12093726b80513d17d8d9e52a848bab9c3d178"
    ),
    "hced-Huayna Pucara1572-1": (
        "1c5492d918e889c92295764383ee42a5c404697779e436a461d648249fafb961"
    ),
    "hced-Ollantaytambo1537-1": (
        "ccd9153278245f3894302400daf407a8d1703cba6c133a9dcb651bb22a8377fb"
    ),
}

_RELATED_ROW_HASHES = {
    "hced-Cuzco1532-1": (
        "ef0ad8dc6df7febc7b9ab58f66b7c4b9be3a3a6d7ca02fa22fbbf6554ceeadb7"
    ),
    "hced-Cuzco1780-1": (
        "90523a9a652fdff3cc7a2de53aa0e686ae9493105b9ca80d0ad3398df5464b4a"
    ),
}

_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_INCA_REBELS_SOURCES
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
    winner_side: int,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "audit_note": audit_note,
        "canonical_event": canonical_event,
        "cohort": cohort,
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "outcome_source_ids": outcomes,
        "raw_row_sha256": WAVE8_INCA_REBELS_ROW_HASHES[candidate_id],
        "result_type": "win",
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "source_outcome_override": False,
        "war_type": "colonial_anti_colonial",
        "winner_side": winner_side,
    }


WAVE8_INCA_REBELS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Cuzco1537-1": _contract(
        "hced-Cuzco1537-1",
        _canonical(
            "End of the Siege of Cuzco",
            1537,
            "early 1537",
            date_precision="season",
            granularity="siege_termination_and_withdrawal",
        ),
        "manco_inca_cuzco_revolt_1536_1537",
        [_CUZCO_SPANISH_ID],
        [_CUZCO_INCA_ID],
        [
            "wave8_inca_rebels_himmerich_cuzco",
            "wave8_inca_rebels_lavalle_pizarro",
            "wave8_inca_rebels_sheppard_cuzco",
            "wave8_inca_rebels_titu_cusi_bauer",
            "wave8_inca_rebels_treccani_cuzco",
        ],
        [
            "wave8_inca_rebels_himmerich_cuzco",
            "wave8_inca_rebels_lavalle_pizarro",
            "wave8_inca_rebels_sheppard_cuzco",
            "wave8_inca_rebels_titu_cusi_bauer",
        ],
        (
            "The contract rates only the siege's 1537 terminal phase: Manco's "
            "attempt to recover Cuzco failed, his field forces withdrew, and the "
            "Spanish-allied garrison retained the city. It does not create a "
            "second 1535 siege or treat Almagro's later seizure of Cuzco as an "
            "Inca-Spanish engagement."
        ),
        confidence=0.93,
        winner_side=1,
    ),
    "hced-Ollantaytambo1537-1": _contract(
        "hced-Ollantaytambo1537-1",
        _canonical(
            "Battle of Ollantaytambo",
            1537,
            "January 1537",
            date_precision="month",
            granularity="fortified_field_battle_and_forced_retreat",
        ),
        "manco_inca_ollantaytambo_defense_1537",
        [_OLLANTAY_INCA_ID],
        [_OLLANTAY_SPANISH_ID],
        [
            "wave8_inca_rebels_lavalle_pizarro",
            "wave8_inca_rebels_pbs_ollantaytambo",
            "wave8_inca_rebels_sheppard_cuzco",
            "wave8_inca_rebels_titu_cusi_bauer",
        ],
        [
            "wave8_inca_rebels_lavalle_pizarro",
            "wave8_inca_rebels_pbs_ollantaytambo",
            "wave8_inca_rebels_sheppard_cuzco",
        ],
        (
            "Manco Inca's fortified force stopped Hernando Pizarro's assault and "
            "forced the expedition back to Cuzco. Titu Cusi's account preserves "
            "the contemporary nuance that darkness ended fighting before the "
            "Spanish withdrawal; the contract records the independently attested "
            "defensive battlefield victory, not annihilation or final campaign "
            "success."
        ),
        confidence=0.96,
        winner_side=1,
    ),
    "hced-Huayna Pucara1572-1": _contract(
        "hced-Huayna Pucara1572-1",
        _canonical(
            "Capture of Huayna Pucara",
            1572,
            "22-23 June 1572",
            date_precision="day",
            granularity="fortified_position_assault_and_capitulation",
        ),
        "vilcabamba_final_campaign_1572",
        [_HUAYNA_SPANISH_ID],
        [_HUAYNA_INCA_ID],
        [
            "wave8_inca_rebels_bauer_vilcabamba",
            "wave8_inca_rebels_casevitz_huayna_pucara",
            "wave8_inca_rebels_murua_huayna_pucara",
            "wave8_inca_rebels_oxford_vilcabamba",
        ],
        [
            "wave8_inca_rebels_bauer_vilcabamba",
            "wave8_inca_rebels_casevitz_huayna_pucara",
            "wave8_inca_rebels_murua_huayna_pucara",
        ],
        (
            "The royal expedition exposed and overcame the fortified Huayna "
            "Pucara position, opening the road to Vilcabamba. The contract stops "
            "at that tactical position: it does not merge the next day's entry "
            "into the abandoned capital or the later capture of Tupac Amaru."
        ),
        confidence=0.94,
        winner_side=1,
    ),
}


WAVE8_INCA_REBELS_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Cuzco1535-1": {
        "audit_note": (
            "Independent Indigenous, scholarly-journal, monograph, and reference "
            "chronologies place Manco Inca's Cuzco siege in 1536-1537. No "
            "separate Spain-versus-Inca-Rebels battle at Cuzco in 1535 was "
            "located. The 1537 queue row owns the siege's terminal outcome; "
            "changing this locked row's year or rating both rows would invent or "
            "duplicate an event."
        ),
        "canonical_event": {
            "canonical_key": "siege_of_cuzco:1536:1537",
            "date_precision": "year_range",
            "date_text": "1536-1537",
            "granularity": "siege_campaign",
            "name": "Siege of Cuzco",
            "year_low": 1536,
            "year_high": 1537,
        },
        "disposition": "terminal_exclusion",
        "duplicate_ownership": {
            "owner_candidate_id": "hced-Cuzco1537-1",
            "owner_module": _MODULE_OWNER,
            "status": "same_siege_single_owner",
        },
        "evidence_refs": [
            "wave8_inca_rebels_himmerich_cuzco",
            "wave8_inca_rebels_lavalle_pizarro",
            "wave8_inca_rebels_sheppard_cuzco",
            "wave8_inca_rebels_titu_cusi_bauer",
            "wave8_inca_rebels_treccani_cuzco",
        ],
        "exclusion_reason": "misdated_duplicate_of_1536_1537_siege",
        "raw_row_sha256": WAVE8_INCA_REBELS_ROW_HASHES["hced-Cuzco1535-1"],
        "reviewed_outcome": "not_rateable_misdated_duplicate",
        "terminal_exclusion": True,
        "unknown_is_never_draw": True,
    }
}
WAVE8_INCA_REBELS_EXCLUSIONS = WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS
WAVE8_INCA_REBELS_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_INCA_REBELS_HOLDS,
    **WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS,
}

WAVE8_INCA_REBELS_CONTRACT_IDS = frozenset(WAVE8_INCA_REBELS_CONTRACTS)
WAVE8_INCA_REBELS_HOLD_IDS = frozenset(WAVE8_INCA_REBELS_HOLDS)
WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS
)
WAVE8_INCA_REBELS_EXCLUSION_IDS = WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS
WAVE8_INCA_REBELS_RESERVED_IDS = frozenset(
    WAVE8_INCA_REBELS_CONTRACT_IDS
    | WAVE8_INCA_REBELS_HOLD_IDS
    | WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS
)
WAVE8_INCA_REBELS_EXPECTED_CANDIDATE_IDS = WAVE8_INCA_REBELS_RESERVED_IDS
WAVE8_INCA_REBELS_TOUCHED_CANDIDATE_IDS = WAVE8_INCA_REBELS_RESERVED_IDS
WAVE8_INCA_REBELS_EXACT_CANDIDATE_ID_SHA256 = (
    "d0beccc8bced031cd7b7c4fe05ada0aea039aa15f9bc2ff6ad5d884dd7b08c65"
)
WAVE8_INCA_REBELS_FUNNEL_EVENT_CANDIDATE_ID_SHA256 = (
    "306e8bd1195fc82273c8dcdad2b51509617a99f63227f68684f241ff5d03a3e9"
)


WAVE8_INCA_REBELS_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Cuzco1535-1": {
        "disposition": "same_siege_single_owner",
        "evidence_refs": [
            "wave8_inca_rebels_himmerich_cuzco",
            "wave8_inca_rebels_sheppard_cuzco",
            "wave8_inca_rebels_titu_cusi_bauer",
        ],
        "owner_module": _MODULE_OWNER,
        "raw_row_sha256": WAVE8_INCA_REBELS_ROW_HASHES["hced-Cuzco1535-1"],
        "related_hced_candidate_id": "hced-Cuzco1537-1",
        "related_raw_row_sha256": WAVE8_INCA_REBELS_ROW_HASHES[
            "hced-Cuzco1537-1"
        ],
        "relationship": "misdated_duplicate_of_1536_1537_siege",
        "reason": (
            "Both rows describe the one Manco Inca siege. The 1537 row owns its "
            "terminal result; the unsupported 1535 row is terminally excluded."
        ),
    },
    "hced-Cuzco1532-1": {
        "disposition": "distinct_cuzco_event",
        "evidence_refs": ["wave8_inca_rebels_titu_cusi_bauer"],
        "owner_module": _MODULE_OWNER,
        "raw_row_sha256": _RELATED_ROW_HASHES["hced-Cuzco1532-1"],
        "related_hced_candidate_id": "hced-Cuzco1537-1",
        "related_raw_row_sha256": WAVE8_INCA_REBELS_ROW_HASHES[
            "hced-Cuzco1537-1"
        ],
        "relationship": "different_war_year_and_actors",
        "reason": (
            "The 1532 row is an Atahualpa-Huascar succession-war event, not "
            "Manco Inca's later anti-Spanish siege."
        ),
    },
    "hced-Cuzco1780-1": {
        "disposition": "distinct_cuzco_event",
        "evidence_refs": ["wave8_inca_rebels_treccani_cuzco"],
        "owner_module": _MODULE_OWNER,
        "raw_row_sha256": _RELATED_ROW_HASHES["hced-Cuzco1780-1"],
        "related_hced_candidate_id": "hced-Cuzco1537-1",
        "related_raw_row_sha256": WAVE8_INCA_REBELS_ROW_HASHES[
            "hced-Cuzco1537-1"
        ],
        "relationship": "different_century_rebellion_and_actors",
        "reason": (
            "The 1780 row belongs to the Tupac Amaru II rebellion more than two "
            "centuries later and shares only the city label."
        ),
    },
}


WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "existing_inca_empire_release_lane": {
        "disposition": "distinct_pre_rebellion_events_and_identity_boundary",
        "evidence_refs": [
            "wave8_inca_rebels_oxford_vilcabamba",
            "wave8_inca_rebels_titu_cusi_bauer",
        ],
        "existing_candidate_ids": sorted(_EXISTING_INCA_EVENTS),
        "existing_entity_id": _EXISTING_INCA_ENTITY_ID,
        "existing_event_ids": sorted(_EXISTING_INCA_EVENTS.values()),
        "other_module": "core_hced_label_promotion",
        "owned_candidate_ids": sorted(WAVE8_INCA_REBELS_RESERVED_IDS),
        "reason": (
            "Cajamarca, Teocajas, and Vilcaconga are separately owned conquest "
            "events. This lane does not reuse their broad Inca Empire identity "
            "for Manco Inca's revolt or Tupac Amaru's Vilcabamba defense."
        ),
    },
    "wave8_peruvian_rebels": {
        "disposition": "distinct_later_anti_colonial_lane",
        "evidence_refs": ["wave8_inca_rebels_oxford_vilcabamba"],
        "other_module": "wave8_peruvian_rebels",
        "owned_candidate_ids": sorted(WAVE8_INCA_REBELS_RESERVED_IDS),
        "reason": (
            "The Peruvian Rebels lane begins with nineteenth-century Cuzco and "
            "independence forces. Shared geography and anti-colonial context do "
            "not create common event or polity ownership."
        ),
    },
}

WAVE8_INCA_REBELS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_INCA_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_INCA_REBELS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"related_hced:{candidate_id}": disposition
        for candidate_id, disposition in WAVE8_INCA_REBELS_RELATED_HCED_DISPOSITIONS.items()
    },
    **{
        f"cross_lane:{lane}": disposition
        for lane, disposition in WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS.items()
    },
}


WAVE8_INCA_REBELS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Cuzco1537-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_inca_rebels_himmerich_cuzco",
            "wave8_inca_rebels_sheppard_cuzco",
        ],
        "raw_point": [-71.9674626, -13.53195],
        "retained_country": "Peru",
        "reason": (
            "A city-center coordinate cannot represent a ten-month siege, its "
            "camps, approaches, Sacsayhuaman fighting, and terminal withdrawal."
        ),
    },
    "hced-Ollantaytambo1537-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_inca_rebels_lavalle_pizarro",
            "wave8_inca_rebels_pbs_ollantaytambo",
        ],
        "raw_point": [-72.2698795, -13.2582838],
        "retained_country": "Peru",
        "reason": (
            "The action crossed the town, terraces, river approaches, and flooded "
            "plain; the staged locality point is not an authenticated clash point."
        ),
    },
    "hced-Huayna Pucara1572-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_inca_rebels_bauer_vilcabamba",
            "wave8_inca_rebels_casevitz_huayna_pucara",
        ],
        "raw_point": [-76.5351105, -10.3343742],
        "retained_country": "Peru",
        "reason": (
            "The scholarly account places Huayna Pucara on the Vilcabamba road; "
            "HCED's point is far outside that region and is not retained."
        ),
    },
}
WAVE8_INCA_REBELS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_INCA_REBELS_LOCATION_QUARANTINE_REASONS
)
WAVE8_INCA_REBELS_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_INCA_REBELS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_INCA_REBELS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_INCA_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_INCA_REBELS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


def _duplicate_audit(year: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": tuple(sorted(set(map(normalize_label, aliases)))),
        "years": (year,),
    }


WAVE8_INCA_REBELS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Cuzco1535-1": _duplicate_audit(
        1535,
        "Cuzco",
        "Cusco",
        "Siege of Cuzco",
        "Siege of Cusco",
    ),
    "hced-Cuzco1537-1": _duplicate_audit(
        1537,
        "Cuzco",
        "Cusco",
        "End of the Siege of Cuzco",
        "Siege of Cuzco",
        "Siege of Cusco",
    ),
    "hced-Ollantaytambo1537-1": _duplicate_audit(
        1537,
        "Battle of Ollantaytambo",
        "Ollantaytambo",
        "Ollantaytampu",
        "Tambo",
    ),
    "hced-Huayna Pucara1572-1": _duplicate_audit(
        1572,
        "Capture of Huayna Pucara",
        "Huayna Pucara",
        "Huayna Pukara",
        "Wayna Pucara",
        "Wayna Pukara",
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_INCA_REBELS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_INCA_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_INCA_REBELS_ENTITIES,
        "exact_candidate_ids": sorted(WAVE8_INCA_REBELS_EXPECTED_CANDIDATE_IDS),
        "existing_release_duplicate_dispositions": (
            WAVE8_INCA_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": WAVE8_INCA_REBELS_HOLDS,
        "integration_dispositions": WAVE8_INCA_REBELS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_INCA_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_INCA_REBELS_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": (
            WAVE8_INCA_REBELS_LOCATION_QUARANTINE_REASONS
        ),
        "outcome_overrides": WAVE8_INCA_REBELS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_INCA_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": WAVE8_INCA_REBELS_RELATED_HCED_DISPOSITIONS,
        "sources": WAVE8_INCA_REBELS_SOURCES,
        "terminal_exclusions": WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS,
    }


def wave8_inca_rebels_audit_signature() -> str:
    """Return the immutable digest of the complete Inca Rebels adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


# Measured from the complete immutable payload above.
WAVE8_INCA_REBELS_FINAL_AUDIT_SIGNATURE = (
    "e53ba498813db59fbe26b3a64e2b94f8e230b38cce75d8888484992cf09e93d0"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _candidate_id_sha256(values: Iterable[str]) -> str:
    return hashlib.sha256(
        "\n".join(sorted(map(str, values))).encode("utf-8")
    ).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_INCA_REBELS_CONTRACTS),
        len(WAVE8_INCA_REBELS_HOLDS),
        len(WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS),
    ) != (3, 0, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_INCA_REBELS_ENTITIES), len(WAVE8_INCA_REBELS_SOURCES)) != (
        6,
        10,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_INCA_REBELS_RESERVED_IDS != set(WAVE8_INCA_REBELS_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} exact-label reservation inventory changed")
    if _candidate_id_sha256(WAVE8_INCA_REBELS_EXPECTED_CANDIDATE_IDS) != (
        WAVE8_INCA_REBELS_EXACT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} exact candidate digest changed")
    if wave8_inca_rebels_audit_signature() != (
        WAVE8_INCA_REBELS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    dispositions = (
        WAVE8_INCA_REBELS_CONTRACT_IDS,
        WAVE8_INCA_REBELS_HOLD_IDS,
        WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS,
    )
    for index, left in enumerate(dispositions):
        for right in dispositions[index + 1 :]:
            if left & right:
                raise ValueError(f"{_LANE_NAME} dispositions overlap")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_INCA_REBELS_SOURCES
    }
    if len(source_by_id) != len(WAVE8_INCA_REBELS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    source_families = {
        str(source["source_family_id"]) for source in WAVE8_INCA_REBELS_SOURCES
    }
    if len(source_families) != len(WAVE8_INCA_REBELS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source-family independence changed")
    for source in WAVE8_INCA_REBELS_SOURCES:
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_INCA_REBELS_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_INCA_REBELS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_ids = {
        "inca",
        "inca_empire",
        _EXISTING_INCA_ENTITY_ID,
        "peru",
        "spain",
        "spanish_empire",
    }
    used_sources: set[str] = set()
    used_entities: set[str] = set()
    for entity in WAVE8_INCA_REBELS_ENTITIES:
        if str(entity["id"]) in forbidden_ids or entity["aliases"]:
            raise ValueError(f"{_LANE_NAME} installed a generic actor or alias")
        if int(entity["end_year"]) - int(entity["start_year"]) > 1:
            raise ValueError(f"{_LANE_NAME} entity is not operation-bounded")
        source_ids = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(source_ids) or not set(source_ids) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity source references changed")
        used_sources.update(source_ids)

    for candidate_id, contract in WAVE8_INCA_REBELS_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_INCA_REBELS_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract hash drifted")
        for field in ("evidence_refs", "outcome_source_ids", "outcome_source_family_ids"):
            if not _is_sorted_unique(contract[field]) or not contract[field]:
                raise ValueError(f"{_LANE_NAME} contract evidence is not canonical")
        evidence = set(map(str, contract["evidence_refs"]))
        outcomes = set(map(str, contract["outcome_source_ids"]))
        if not outcomes <= evidence or not evidence <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} contract evidence references changed")
        expected_families = {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        if set(contract["outcome_source_family_ids"]) != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome-family references changed")
        if len(expected_families) < 3:
            raise ValueError(f"{_LANE_NAME} outcome lacks independent corroboration")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} contract sides changed")
        if not (side_1 | side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} contract references unknown entity")
        if contract["result_type"] != "win" or contract["winner_side"] not in {1, 2}:
            raise ValueError(f"{_LANE_NAME} invented a non-victory contract")
        if contract["source_outcome_override"] is not False:
            raise ValueError(f"{_LANE_NAME} invented an outcome override")
        used_sources.update(evidence)
        used_entities.update(side_1 | side_2)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entity fixture is not exactly consumed")

    exclusion = WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS["hced-Cuzco1535-1"]
    forbidden_nonpromotion_keys = {
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_entity_ids",
        "winner_side",
    }
    if (
        exclusion["raw_row_sha256"]
        != WAVE8_INCA_REBELS_ROW_HASHES["hced-Cuzco1535-1"]
        or exclusion["disposition"] != "terminal_exclusion"
        or exclusion["terminal_exclusion"] is not True
        or exclusion["reviewed_outcome"] != "not_rateable_misdated_duplicate"
        or exclusion["unknown_is_never_draw"] is not True
        or forbidden_nonpromotion_keys & set(exclusion)
    ):
        raise ValueError(f"{_LANE_NAME} Cuzco 1535 exclusion changed")
    exclusion_sources = list(map(str, exclusion["evidence_refs"]))
    if not _is_sorted_unique(exclusion_sources) or not set(exclusion_sources) <= set(
        source_by_id
    ):
        raise ValueError(f"{_LANE_NAME} exclusion evidence changed")
    used_sources.update(exclusion_sources)

    for candidate_id, item in WAVE8_INCA_REBELS_RELATED_HCED_DISPOSITIONS.items():
        expected_hash = (
            WAVE8_INCA_REBELS_ROW_HASHES.get(candidate_id)
            or _RELATED_ROW_HASHES.get(candidate_id)
        )
        related_id = str(item["related_hced_candidate_id"])
        if (
            item["raw_row_sha256"] != expected_hash
            or item["related_raw_row_sha256"]
            != WAVE8_INCA_REBELS_ROW_HASHES[related_id]
            or item["owner_module"] != _MODULE_OWNER
        ):
            raise ValueError(f"{_LANE_NAME} related HCED disposition drifted")
        evidence = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} related HCED evidence drifted")
        used_sources.update(evidence)

    expected_cross_lanes = {
        "existing_inca_empire_release_lane",
        "wave8_peruvian_rebels",
    }
    if set(WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS) != expected_cross_lanes:
        raise ValueError(f"{_LANE_NAME} cross-lane inventory changed")
    for item in WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS.values():
        if set(item["owned_candidate_ids"]) != WAVE8_INCA_REBELS_RESERVED_IDS:
            raise ValueError(f"{_LANE_NAME} cross-lane ownership changed")
        evidence = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} cross-lane evidence drifted")
        used_sources.update(evidence)

    expected_integration = {
        **{
            f"related_hced:{key}": value
            for key, value in WAVE8_INCA_REBELS_RELATED_HCED_DISPOSITIONS.items()
        },
        **{
            f"cross_lane:{key}": value
            for key, value in WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS.items()
        },
    }
    if WAVE8_INCA_REBELS_INTEGRATION_DISPOSITIONS != expected_integration:
        raise ValueError(f"{_LANE_NAME} integration inventory changed")

    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if WAVE8_INCA_REBELS_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_INCA_REBELS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_INCA_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if (
        WAVE8_INCA_REBELS_OUTCOME_OVERRIDES
        or WAVE8_INCA_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_INCA_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")
    if set(WAVE8_INCA_REBELS_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_INCA_REBELS_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for audit in WAVE8_INCA_REBELS_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(audit["aliases"]):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if tuple(audit["years"]) != tuple(sorted(set(map(int, audit["years"])))):
            raise ValueError(f"{_LANE_NAME} duplicate years are not canonical")


def _is_exact_inca_rebels_label(value: Any) -> bool:
    return normalize_label(value) == "inca rebels"


def validate_wave8_inca_rebels_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all four exact-label rows and every disposition."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_INCA_REBELS_CONTRACTS,
        WAVE8_INCA_REBELS_HOLDS,
        lane_name=_LANE_NAME,
    )
    indexed: dict[str, list[dict[str, Any]]] = {}
    exact_ids: set[str] = set()
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id") or "")
        indexed.setdefault(candidate_id, []).append(row)
        if _is_exact_inca_rebels_label(
            row.get("side_1_raw")
        ) or _is_exact_inca_rebels_label(row.get("side_2_raw")):
            exact_ids.add(candidate_id)
    if exact_ids != WAVE8_INCA_REBELS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Inca Rebels inventory changed: {sorted(exact_ids)}"
        )
    for candidate_id in WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS:
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} disposition {candidate_id} expected exactly one "
                f"queue row, found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != WAVE8_INCA_REBELS_ROW_HASHES[
            candidate_id
        ]:
            raise ValueError(f"{_LANE_NAME} disposition hash changed for {candidate_id}")
    return {
        "holds": result["holds"],
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": len(WAVE8_INCA_REBELS_EXPECTED_CANDIDATE_IDS),
        "reviewed_unresolved_hced_rows": len(WAVE8_INCA_REBELS_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_INCA_REBELS_TERMINAL_EXCLUSION_IDS),
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


def validate_wave8_inca_rebels_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on related HCED rows and probable cross-dataset twins."""

    validate_wave8_inca_rebels_queue_contracts(hced_rows)
    hced_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        hced_by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, expected_hash in _RELATED_ROW_HASHES.items():
        rows = hced_by_id.get(candidate_id, [])
        if len(rows) != 1 or canonical_hced_row_sha256(rows[0]) != expected_hash:
            raise ValueError(f"{_LANE_NAME} related HCED row changed: {candidate_id}")

    audited = {
        (int(year), normalize_label(alias))
        for audit in WAVE8_INCA_REBELS_IWBD_ZERO_OVERLAP_AUDIT.values()
        for year in audit["years"]
        for alias in audit["aliases"]
    }
    unexpected_iwbd = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _row_year(row) is not None
        and (_row_year(row), normalize_label(row.get("name"))) in audited
    )
    if unexpected_iwbd:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): {unexpected_iwbd}"
        )

    existing = list(existing_events)
    unexpected_release = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id") not in WAVE8_INCA_REBELS_RESERVED_IDS
        and _row_year(event) is not None
        and (_row_year(event), normalize_label(event.get("name"))) in audited
    )
    if unexpected_release:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable release duplicate(s): "
            f"{unexpected_release}"
        )

    inca_owner_count = 0
    if existing:
        by_candidate = {
            str(event.get("hced_candidate_id")): event
            for event in existing
            if event.get("hced_candidate_id") in _EXISTING_INCA_EVENTS
        }
        if set(by_candidate) != set(_EXISTING_INCA_EVENTS):
            raise ValueError(f"{_LANE_NAME} existing Inca release ownership changed")
        for candidate_id, owner_event_id in _EXISTING_INCA_EVENTS.items():
            event = by_candidate[candidate_id]
            participant_ids = {
                str(participant.get("entity_id"))
                for participant in event.get("participants", [])
            }
            if (
                str(event.get("id")) != owner_event_id
                or _EXISTING_INCA_ENTITY_ID not in participant_ids
            ):
                raise ValueError(
                    f"{_LANE_NAME} existing Inca event owner changed: {candidate_id}"
                )
        inca_owner_count = len(by_candidate)

    return {
        "cross_lane_dispositions": len(WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS),
        "existing_inca_release_owners_verified": inca_owner_count,
        "existing_release_duplicate_dispositions": 0,
        "integration_dispositions": len(WAVE8_INCA_REBELS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "related_hced_dispositions": len(
            WAVE8_INCA_REBELS_RELATED_HCED_DISPOSITIONS
        ),
        "release_probable_twins": 0,
    }


def install_wave8_inca_rebels_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_INCA_REBELS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_inca_rebels_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_INCA_REBELS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_INCA_REBELS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_INCA_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_inca_rebels_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_inca_rebels_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_INCA_REBELS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_inca_rebels_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_INCA_REBELS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_inca_rebels_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_INCA_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": len(WAVE8_INCA_REBELS_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_INCA_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_INCA_REBELS_HOLDS),
        "integration_dispositions": len(
            WAVE8_INCA_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_INCA_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_INCA_REBELS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_INCA_REBELS_ENTITIES),
        "new_sources": len(WAVE8_INCA_REBELS_SOURCES),
        "newly_rated_events": len(WAVE8_INCA_REBELS_CONTRACTS),
        "outcome_overrides": len(WAVE8_INCA_REBELS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_INCA_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_INCA_REBELS_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_INCA_REBELS_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_INCA_REBELS_EXPECTED_CANDIDATE_IDS),
        "reviewed_unresolved_hced_rows": len(WAVE8_INCA_REBELS_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_INCA_REBELS_TERMINAL_EXCLUSIONS),
        "touched_hced_rows": len(WAVE8_INCA_REBELS_TOUCHED_CANDIDATE_IDS),
    }


def wave8_inca_rebels_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_INCA_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_INCA_REBELS_POINT_QUARANTINE_ADDITIONS,
    }
