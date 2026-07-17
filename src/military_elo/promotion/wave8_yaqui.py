"""Candidate-keyed Wave 8 audit for HCED's exact ``Yaqui`` label.

The task label calls this the ``Yaqui Indians`` lane, but the locked HCED
queue contains no literal ``Yaqui Indians`` side.  It contains four rows whose
normalized side is exactly ``yaqui``.  This module owns those four rows and
pins ``yaqui indians`` as an empty adjacent spelling so a future snapshot
cannot silently broaden the lane.

Three rows have mechanically defensible, event-bounded outcomes.  Agustin de
Vildosola's provincial force defeated a Yaqui-Mayo rebel force at Cerro del
Tambor in 1740.  On 5 May 1886 Marcos Carrillo's force occupied the El Anil
fortification after a fought action and the defenders' withdrawal.  One week
later Angel Martinez's combined force overran Cajeme's Buatachive positions
after a four-day siege and a three-hour final assault.  These results attach
only to the formations and action scopes defined here.

The 1868 Bacum row is terminally excluded.  Its locked massacre flag matches
the independently attested 18 February episode: peace-seeking Yaqui men,
women, and children were made prisoners, confined in the Santa Rosa church,
and fired on while the building burned.  They were not an opposing battlefield
formation.  A separate 10 January fight at Bacum is not substituted for the
locked massacre row, and civilian victims are not assigned an Elo defeat.

No generic Yaqui, Mayo, Spanish, Mexican, modern tribal, or state actor is
installed.  The three promoted points are locally quarantined while the modern
country ``Mexico`` is retained.  Unknown or non-rateable is never a draw.
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
    "WAVE8_YAQUI_ADJACENT_LITERAL_LABEL_INVENTORY",
    "WAVE8_YAQUI_CONTRACT_IDS",
    "WAVE8_YAQUI_CONTRACTS",
    "WAVE8_YAQUI_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS",
    "WAVE8_YAQUI_ENTITIES",
    "WAVE8_YAQUI_EVENT_BOUNDARIES",
    "WAVE8_YAQUI_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_YAQUI_EXCLUSION_IDS",
    "WAVE8_YAQUI_EXCLUSIONS",
    "WAVE8_YAQUI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_YAQUI_EXPECTED_CANDIDATE_IDS",
    "WAVE8_YAQUI_FINAL_AUDIT_SIGNATURE",
    "WAVE8_YAQUI_FUNNEL_AUDIT",
    "WAVE8_YAQUI_FUNNEL_EVENT_CANDIDATE_ID_SHA256",
    "WAVE8_YAQUI_HCED_DUPLICATE_DISPOSITIONS",
    "WAVE8_YAQUI_HCED_QUEUE_SHA256",
    "WAVE8_YAQUI_HOLD_IDS",
    "WAVE8_YAQUI_HOLDS",
    "WAVE8_YAQUI_INTEGRATION_DISPOSITIONS",
    "WAVE8_YAQUI_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_YAQUI_IWBD_QUEUE_SHA256",
    "WAVE8_YAQUI_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_YAQUI_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_YAQUI_LOCATION_QUARANTINE_REASONS",
    "WAVE8_YAQUI_NONPROMOTIONS",
    "WAVE8_YAQUI_OUTCOME_OVERRIDES",
    "WAVE8_YAQUI_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_YAQUI_RESERVED_IDS",
    "WAVE8_YAQUI_ROW_DISPOSITIONS",
    "WAVE8_YAQUI_ROW_HASHES",
    "WAVE8_YAQUI_SCOPE_AND_OPPOSITE_RESULT_AUDIT",
    "WAVE8_YAQUI_SOURCES",
    "WAVE8_YAQUI_SOURCE_ROW_SEMANTICS",
    "WAVE8_YAQUI_TERMINAL_EXCLUSION_IDS",
    "WAVE8_YAQUI_TERMINAL_EXCLUSIONS",
    "WAVE8_YAQUI_TOUCHED_CANDIDATE_IDS",
    "WAVE8_YAQUI_WAR_CANDIDATE_IDS",
    "WAVE8_YAQUI_WAR_LABEL_INVENTORY",
    "install_wave8_yaqui_entities",
    "install_wave8_yaqui_sources",
    "promote_wave8_yaqui_contracts",
    "validate_wave8_yaqui_funnel",
    "validate_wave8_yaqui_integration_dispositions",
    "validate_wave8_yaqui_queue_contracts",
    "wave8_yaqui_audit_signature",
    "wave8_yaqui_cohort_counts",
    "wave8_yaqui_counts",
    "wave8_yaqui_location_quarantine_additions",
    "wave8_yaqui_metadata",
    "wave8_yaqui_row_dispositions",
)


_LANE_NAME = "Wave 8 exact Yaqui event-bounded formation audit"
_MODULE_OWNER = "military_elo.promotion.wave8_yaqui"
_EVENT_ID_PREFIX = "hced_wave8_yaqui_"
_EXACT_LABEL = "yaqui"

_TAMBOR_SPANISH_ID = "vildosola_provincial_force_cerro_tambor_1740"
_TAMBOR_INDIGENOUS_ID = "yaqui_mayo_rebel_force_cerro_tambor_1740"
_ANIL_MEXICAN_ID = "carrillo_mexican_anil_operation_force_1886_05_03_05"
_ANIL_YAQUI_ID = "cajeme_yaqui_anil_defenders_1886_05_05"
_BUATACHIVE_MEXICAN_ID = (
    "martinez_mexican_buatachive_assault_force_1886_05_09_12"
)
_BUATACHIVE_YAQUI_ID = "cajeme_yaqui_buatachive_defenders_1886_05_09_12"


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
    roles = {"identity_boundary_or_context_reference"}
    if outcome:
        roles.add("outcome")
    if crosscheck:
        roles.add("outcome_consistency_crosscheck")
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


WAVE8_YAQUI_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_yaqui_troncoso_tomo_i",
        "Las guerras con las tribus Yaqui y Mayo del Estado de Sonora, Tomo I",
        (
            "https://bibliotecadigital.sonora.gob.mx/images/libros_digitales/"
            "Troncoso_Francisco_-_Las_guerras_con_las_tribus_yaqui_y_mayo."
            "_Tomo_I.pdf"
        ),
        (
            "Secretaria de Guerra y Marina; Gobierno del Estado de Sonora "
            "digital edition"
        ),
        "official_military_history_and_primary_report_compilation",
        "troncoso_yaqui_mayo_tomo_i",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_yaqui_spicer_cycles",
        "Cycles of Conquest, Chapter 2: Mayos and Yaquis",
        (
            "https://openaz-tst.library.arizona.edu/read/cycles-of-conquest/"
            "section/64cb831a-598b-47dc-b6e1-0a2b2a89ce20"
        ),
        "University of Arizona Press",
        "scholarly_monograph",
        "spicer_cycles_of_conquest_mayos_yaquis",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_yaqui_texas_band_history",
        "History",
        "https://www.tbyi.gov/history",
        "Texas Band of Yaqui Indians",
        "official_indigenous_history",
        "texas_band_of_yaqui_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_yaqui_gouy_gilbert",
        "Una resistencia india: II. Las guerras del Yaqui (siglo XIX)",
        "https://books.openedition.org/cemca/3359?lang=en",
        "Centro de Estudios Mexicanos y Centroamericanos / OpenEdition",
        "scholarly_monograph",
        "gouy_gilbert_una_resistencia_india",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_yaqui_cardenas_historia_mexicana",
        (
            "Lo que queremos es que salgan los blancos y las tropas: Yaquis y "
            "mexicanos en tiempos de revolucion (1910-1920)"
        ),
        "https://historiamexicana.colmex.mx/index.php/RHM/article/view/3421",
        "Historia Mexicana / El Colegio de Mexico",
        "peer_reviewed_historical_journal",
        "cardenas_historia_mexicana_3421",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_yaqui_acosta_sonora",
        "Apuntes historicos sonorenses",
        (
            "https://bibliotecadigital.sonora.gob.mx/images/libros_digitales/"
            "Acosta_Roberto_-_Apuntes_histricos_sonorenses_copy_1.pdf"
        ),
        "Biblioteca Digital de Sonora / Gobierno del Estado de Sonora",
        "regional_historical_monograph",
        "acosta_apuntes_historicos_sonorenses",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_yaqui_sonora_bacum_chronology",
        "Bacum municipal historical chronology",
        (
            "https://boletinoficial.sonora.gob.mx/images/boletines/2024/01/"
            "2024CCXIII6V.pdf"
        ),
        "Boletin Oficial del Gobierno del Estado de Sonora",
        "official_municipal_history",
        "sonora_bacum_official_chronology_2024",
        crosscheck=True,
    ),
    _source(
        "wave8_yaqui_inah_padilla_territorio",
        "Cicatrizando el Territorio: Los ductos y la criminalizacion de las luchas yaquis",
        (
            "https://revistas.inah.gob.mx/index.php/noroestedemexico/"
            "article/view/17176"
        ),
        "Noroeste de Mexico / Instituto Nacional de Antropologia e Historia",
        "scholarly_government_journal",
        "padilla_cicatrizando_territorio_inah",
        crosscheck=True,
    ),
    _source(
        "wave8_yaqui_mapping_rebellions_1740",
        "Yaqui rebellion 1740",
        (
            "https://mappingrebellions.com/encyclopaedia/"
            "?name_of_revolt=yaqui-rebellion-1740"
        ),
        "Encyclopaedia of Rebellions in the Early Modern Iberian World",
        "academic_rebellion_encyclopedia",
        "mapping_rebellions_yaqui_1740",
        crosscheck=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    boundary_note: str,
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
            boundary_note
            + " The mechanical year window exists only because entity records use "
            "year precision; the prose dates are the actual boundary. No rating is "
            "inherited from or passed to the Yaqui or Mayo peoples, a modern tribal "
            "government, Spain, Mexico, Sonora, or another campaign formation."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_YAQUI_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _TAMBOR_SPANISH_ID,
        "Vildosola's provincial force at Cerro del Tambor (1740)",
        "event_bounded_colonial_provincial_force",
        1740,
        "Cerro del Tambor between the Tecoripa frontier and Yaqui country",
        (
            "Bounded to Agustin de Vildosola's soldiers and militia in the "
            "single Cerro del Tambor action during the 1740 revolt."
        ),
        [
            "wave8_yaqui_acosta_sonora",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_troncoso_tomo_i",
        ],
    ),
    _entity(
        _TAMBOR_INDIGENOUS_ID,
        "Yaqui-Mayo rebel force at Cerro del Tambor (1740)",
        "event_bounded_indigenous_coalition_force",
        1740,
        "Cerro del Tambor at the edge of Yaqui country",
        (
            "Bounded to the Yaqui- and Mayo-associated fighting force defeated "
            "at Cerro del Tambor. The coalition description does not create a "
            "generic Yaqui, Mayo, Pima, or Four Rivers actor."
        ),
        [
            "wave8_yaqui_acosta_sonora",
            "wave8_yaqui_mapping_rebellions_1740",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_troncoso_tomo_i",
        ],
    ),
    _entity(
        _ANIL_MEXICAN_ID,
        "Carrillo's Mexican El Anil operation force (3-5 May 1886)",
        "event_bounded_mixed_federal_state_force",
        1886,
        "El Anil fortification in the Yaqui River country",
        (
            "Bounded to Marcos Carrillo's Mexican federal and Sonora components "
            "performing reconnaissance, siege works, and the fought occupation "
            "of El Anil from 3 through 5 May 1886."
        ),
        [
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_texas_band_history",
            "wave8_yaqui_troncoso_tomo_i",
        ],
    ),
    _entity(
        _ANIL_YAQUI_ID,
        "Cajeme's Yaqui El Anil defenders (5 May 1886)",
        "event_bounded_indigenous_defense_force",
        1886,
        "El Anil fortification and withdrawal route toward Buatachive",
        (
            "Bounded to the Yaqui fighters who attacked Carrillo's working line "
            "and then withdrew from El Anil toward Buatachive on 5 May 1886."
        ),
        [
            "wave8_yaqui_gouy_gilbert",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_troncoso_tomo_i",
        ],
    ),
    _entity(
        _BUATACHIVE_MEXICAN_ID,
        "Martinez's Mexican Buatachive assault force (9-12 May 1886)",
        "event_bounded_combined_siege_force",
        1886,
        "Buatachive positions in the Sierra del Bacatete",
        (
            "Bounded to Angel Martinez's combined columns under Carrillo, Otero, "
            "Torres, and subordinate commanders during the Buatachive siege and "
            "final assault of 9-12 May 1886."
        ),
        [
            "wave8_yaqui_cardenas_historia_mexicana",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_troncoso_tomo_i",
        ],
    ),
    _entity(
        _BUATACHIVE_YAQUI_ID,
        "Cajeme's Yaqui Buatachive defenders (9-12 May 1886)",
        "event_bounded_indigenous_fortified_defense_force",
        1886,
        "Buatachive positions and mountain escape routes, Sierra del Bacatete",
        (
            "Bounded to Cajeme's armed defenders in the Buatachive positions. "
            "Families confined within the position are not made combatants and "
            "are not assigned the force's Elo result."
        ),
        [
            "wave8_yaqui_gouy_gilbert",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_texas_band_history",
            "wave8_yaqui_troncoso_tomo_i",
        ],
    ),
)


WAVE8_YAQUI_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_YAQUI_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)
WAVE8_YAQUI_ROW_HASHES: dict[str, str] = {
    "hced-Anil1886-1": (
        "2e16f7706564f593fd6915ca26486962a5c1edac5c5f8d6a28c6ef6977115c11"
    ),
    "hced-Bacum1868-1": (
        "62df82df26a541d4328a19319e00d7050a3c6715e503e330e5c0e24b4f51db54"
    ),
    "hced-Buatachive1886-1": (
        "1d43b67a765e1d1bc33f553f914ce62edb81abba68510c9beaa29b6ad098b9bf"
    ),
    "hced-Mount Tambor1740-1": (
        "c8054c87809f483ba39889f50fd7d472d535c714e4ca7da316da10bbbbc28f83"
    ),
}

_SOURCE_SEMANTIC_FIELDS = (
    "latitude",
    "longitude",
    "loser_raw",
    "massacre_raw",
    "modern_location_country",
    "name",
    "side_1_raw",
    "side_2_raw",
    "war_names",
    "winner_loser_complete",
    "winner_raw",
    "year_best",
)

# ``canonical_hced_row_sha256`` intentionally fingerprints the shared HCED
# identity/orientation/location fields, but its shared field list omits the
# massacre and winner-completeness columns.  Those columns are mechanically
# decisive in this lane, so this signed projection closes that gap locally.
WAVE8_YAQUI_SOURCE_ROW_SEMANTICS: dict[str, dict[str, Any]] = {
    "hced-Anil1886-1": {
        "latitude": "25.9664053",
        "longitude": "-109.0571847",
        "loser_raw": "Yaqui",
        "massacre_raw": "Battle followed by massacre",
        "modern_location_country": "Mexico",
        "name": "Anil",
        "side_1_raw": "Mexico",
        "side_2_raw": "Yaqui",
        "war_names": ["Mexico-Yaqui War"],
        "winner_loser_complete": True,
        "winner_raw": "Mexico",
        "year_best": 1886,
    },
    "hced-Bacum1868-1": {
        "latitude": "27.5506671",
        "longitude": "-110.091967",
        "loser_raw": "Yaqui",
        "massacre_raw": "Yes",
        "modern_location_country": "Mexico",
        "name": "Bacum",
        "side_1_raw": "Mexico",
        "side_2_raw": "Yaqui",
        "war_names": ["Mexican-Yaqui War"],
        "winner_loser_complete": True,
        "winner_raw": "Mexico",
        "year_best": 1868,
    },
    "hced-Buatachive1886-1": {
        "latitude": "27.6337884",
        "longitude": "-110.2488105",
        "loser_raw": "Yaqui",
        "massacre_raw": "No",
        "modern_location_country": "Mexico",
        "name": "Buatachive",
        "side_1_raw": "Mexico",
        "side_2_raw": "Yaqui",
        "war_names": ["Mexico-Yaqui War"],
        "winner_loser_complete": True,
        "winner_raw": "Mexico",
        "year_best": 1886,
    },
    "hced-Mount Tambor1740-1": {
        "latitude": "19.510535",
        "longitude": "-105.0745437",
        "loser_raw": "Yaqui",
        "massacre_raw": "No",
        "modern_location_country": "Mexico",
        "name": "Mount Tambor",
        "side_1_raw": "Spain",
        "side_2_raw": "Yaqui",
        "war_names": ["Spanish-Yaqui War"],
        "winner_loser_complete": True,
        "winner_raw": "Spain",
        "year_best": 1740,
    },
}

WAVE8_YAQUI_EXACT_CANDIDATE_ID_SHA256 = (
    "cf1b11ff4f4dc2664e253719a5d5c2b5885b4148a1a1d79a340bddcc7c86d432"
)
WAVE8_YAQUI_FUNNEL_EVENT_CANDIDATE_ID_SHA256 = (
    WAVE8_YAQUI_EXACT_CANDIDATE_ID_SHA256
)

WAVE8_YAQUI_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "centuries": {"CE_18": 1, "CE_19": 3},
    "components_bridged": 0,
    "components_touched": 1,
    "event_candidate_id_sha256": WAVE8_YAQUI_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
    "events_touched": 4,
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 4,
    },
    "label": _EXACT_LABEL,
    "rated_counterpart_entities": 2,
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
    for source in WAVE8_YAQUI_SOURCES
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
    reviewed_sides: Iterable[str],
    reviewed_outcome: str,
    massacre_disposition: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "actor_override": True,
        "audit_note": audit_note,
        "canonical_event": canonical_event,
        "cohort": cohort,
        "confidence": confidence,
        "disposition": "promote",
        "event_type": "engagement",
        "evidence_refs": evidence,
        "massacre_disposition": massacre_disposition,
        "outcome_reversal": False,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "outcome_source_ids": outcomes,
        "raw_row_sha256": WAVE8_YAQUI_ROW_HASHES[candidate_id],
        "result_type": "win",
        "reviewed_outcome": reviewed_outcome,
        "reviewed_sides": list(map(str, reviewed_sides)),
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "source_outcome_override": False,
        "war_type": "colonial_anti_colonial",
        "winner_side": 1,
    }


WAVE8_YAQUI_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Mount Tambor1740-1": _contract(
        "hced-Mount Tambor1740-1",
        _canonical(
            "Battle of Cerro del Tambor",
            1740,
            "1740, before the later Otancahui battle; exact day not established",
            date_precision="year",
            granularity="single_battle_at_cerro_del_tambor",
        ),
        "yaqui_mayo_revolt_1740",
        [_TAMBOR_SPANISH_ID],
        [_TAMBOR_INDIGENOUS_ID],
        [
            "wave8_yaqui_acosta_sonora",
            "wave8_yaqui_mapping_rebellions_1740",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_troncoso_tomo_i",
        ],
        [
            "wave8_yaqui_acosta_sonora",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_troncoso_tomo_i",
        ],
        (
            "The contract rates only Vildosola's victory at Cerro del Tambor. "
            "The sources distinguish the later and larger Otancahui action, and "
            "reported casualty totals are not used to manufacture precision."
        ),
        [
            "Vildosola's provincial soldiers and militia at Cerro del Tambor",
            "the event-bounded Yaqui-Mayo rebel force at Cerro del Tambor",
        ],
        "Spanish provincial-force victory at Cerro del Tambor",
        "locked_no_massacre_flag_preserved_without_casualty_inference",
        confidence=0.90,
    ),
    "hced-Anil1886-1": _contract(
        "hced-Anil1886-1",
        _canonical(
            "Battle of El Anil",
            1886,
            "5 May 1886",
            date_precision="day",
            granularity="fortification_attack_withdrawal_and_occupation",
        ),
        "cajeme_campaign_1886",
        [_ANIL_MEXICAN_ID],
        [_ANIL_YAQUI_ID],
        [
            "wave8_yaqui_cardenas_historia_mexicana",
            "wave8_yaqui_gouy_gilbert",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_texas_band_history",
            "wave8_yaqui_troncoso_tomo_i",
        ],
        [
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_texas_band_history",
            "wave8_yaqui_troncoso_tomo_i",
        ],
        (
            "Carrillo's line was attacked during the siege works; the Mexican "
            "force dispersed the attack and occupied the abandoned fortification "
            "after the defenders withdrew toward Buatachive. This is the 1886 "
            "action, not the opposite-result Mexican defeat at El Anil in 1885."
        ),
        [
            "Carrillo's bounded Mexican federal-state El Anil operation force",
            "Cajeme's bounded Yaqui El Anil defense force",
        ],
        "Mexican tactical and positional victory; El Anil occupied",
        (
            "locked_battle_followed_by_massacre_tag_not_corroborated_at_el_anil_"
            "scope_and_not_rated"
        ),
        confidence=0.92,
    ),
    "hced-Buatachive1886-1": _contract(
        "hced-Buatachive1886-1",
        _canonical(
            "Battle of Buatachive",
            1886,
            "9-12 May 1886",
            date_precision="day_range",
            granularity="four_day_siege_and_three_hour_final_assault",
        ),
        "cajeme_campaign_1886",
        [_BUATACHIVE_MEXICAN_ID],
        [_BUATACHIVE_YAQUI_ID],
        [
            "wave8_yaqui_cardenas_historia_mexicana",
            "wave8_yaqui_gouy_gilbert",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_texas_band_history",
            "wave8_yaqui_troncoso_tomo_i",
        ],
        [
            "wave8_yaqui_cardenas_historia_mexicana",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_texas_band_history",
            "wave8_yaqui_troncoso_tomo_i",
        ],
        (
            "After siege work and preliminary fighting, Martinez's columns "
            "assaulted and overran the fortified positions on 12 May; surviving "
            "defenders, including Cajeme, fled into the mountains. The rating is "
            "limited to the armed formations. Captive and killed family members "
            "inside the position are not treated as defeated combatants."
        ),
        [
            "Martinez's bounded combined Mexican Buatachive assault force",
            "Cajeme's bounded armed Yaqui Buatachive defenders",
        ],
        "Mexican victory; Buatachive positions overrun after final assault",
        "civilian_harm_attested_despite_locked_no_flag_and_excluded_from_rating",
        confidence=0.96,
    ),
}


WAVE8_YAQUI_HOLDS: dict[str, dict[str, Any]] = {}

WAVE8_YAQUI_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Bacum1868-1": {
        "audit_note": (
            "The locked massacre flag aligns with the 18 February 1868 church "
            "episode. Six hundred peace-seeking Yaqui people were detained; after "
            "limited weapons were surrendered, 450 prisoners were confined in "
            "the Santa Rosa church. Ten leaders were executed and artillery fired "
            "on the unarmed crowd as the church burned. This was not a competitive "
            "Mexico-versus-Yaqui engagement."
        ),
        "canonical_event": _canonical(
            "Bacum church massacre",
            1868,
            "18 February 1868",
            date_precision="day",
            granularity="massacre_of_confined_peace_seeking_prisoners",
        ),
        "cohort": "yaqui_war_1867_1868",
        "disposition": "terminal_exclusion",
        "evidence_refs": [
            "wave8_yaqui_gouy_gilbert",
            "wave8_yaqui_inah_padilla_territorio",
            "wave8_yaqui_sonora_bacum_chronology",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_texas_band_history",
            "wave8_yaqui_troncoso_tomo_i",
        ],
        "exclusion_category": "noncompetitive_massacre_of_prisoners",
        "exclusion_reason": (
            "The victims were a confined peace-seeking prisoner population, not "
            "an opposing battlefield formation. A distinct 10 January battle at "
            "Bacum cannot be substituted for this massacre-tagged locked row. No "
            "Elo winner or loser is emitted; non-rateable is never a draw."
        ),
        "historical_review": {
            "attested_event": "Bacum church massacre",
            "attested_mexican_side": (
                "Salazar Bustamante's custodial force and artillery"
            ),
            "attested_victim_group": (
                "confined Yaqui men, women, children, and elders seeking peace"
            ),
            "competitive_event": False,
            "distinct_bacum_battle": "10 January 1868",
            "locked_massacre_raw": "Yes",
            "rating_risk": "would rate civilian and prisoner victimization",
        },
        "raw_row_sha256": WAVE8_YAQUI_ROW_HASHES["hced-Bacum1868-1"],
        "reviewed_outcome": "not_rateable_prisoner_massacre",
        "terminal_exclusion": True,
        "unknown_is_never_draw": True,
    }
}

WAVE8_YAQUI_EXCLUSIONS = WAVE8_YAQUI_TERMINAL_EXCLUSIONS
WAVE8_YAQUI_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_YAQUI_HOLDS,
    **WAVE8_YAQUI_TERMINAL_EXCLUSIONS,
}
WAVE8_YAQUI_CONTRACT_IDS = frozenset(WAVE8_YAQUI_CONTRACTS)
WAVE8_YAQUI_HOLD_IDS = frozenset(WAVE8_YAQUI_HOLDS)
WAVE8_YAQUI_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_YAQUI_TERMINAL_EXCLUSIONS
)
WAVE8_YAQUI_EXCLUSION_IDS = WAVE8_YAQUI_TERMINAL_EXCLUSION_IDS
WAVE8_YAQUI_RESERVED_IDS = frozenset(
    WAVE8_YAQUI_CONTRACT_IDS
    | WAVE8_YAQUI_HOLD_IDS
    | WAVE8_YAQUI_TERMINAL_EXCLUSION_IDS
)
WAVE8_YAQUI_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_YAQUI_ROW_HASHES)
WAVE8_YAQUI_TOUCHED_CANDIDATE_IDS = WAVE8_YAQUI_RESERVED_IDS
WAVE8_YAQUI_ROW_DISPOSITIONS = {
    **{candidate_id: "promote" for candidate_id in WAVE8_YAQUI_CONTRACT_IDS},
    **{candidate_id: "hold" for candidate_id in WAVE8_YAQUI_HOLD_IDS},
    **{
        candidate_id: "terminal_exclusion"
        for candidate_id in WAVE8_YAQUI_TERMINAL_EXCLUSION_IDS
    },
}


# Literal side spellings are a closed boundary.  The task's ``Yaqui Indians``
# wording is deliberately represented as an empty adjacent spelling because
# the locked queue itself says exactly ``Yaqui``.
WAVE8_YAQUI_ADJACENT_LITERAL_LABEL_INVENTORY: dict[str, tuple[str, ...]] = {
    "hiaki": (),
    "yaqui": tuple(sorted(WAVE8_YAQUI_EXPECTED_CANDIDATE_IDS)),
    "yaqui indian": (),
    "yaqui indians": (),
    "yaqui nation": (),
    "yaqui people": (),
    "yaquis": (),
    "yoeme": (),
}

WAVE8_YAQUI_WAR_LABEL_INVENTORY: dict[str, tuple[str, ...]] = {
    "mexican yaqui war": ("hced-Bacum1868-1",),
    "mexico yaqui war": tuple(
        sorted(("hced-Anil1886-1", "hced-Buatachive1886-1"))
    ),
    "spanish yaqui war": ("hced-Mount Tambor1740-1",),
}
WAVE8_YAQUI_WAR_CANDIDATE_IDS = frozenset(
    candidate_id
    for candidate_ids in WAVE8_YAQUI_WAR_LABEL_INVENTORY.values()
    for candidate_id in candidate_ids
)


WAVE8_YAQUI_SCOPE_AND_OPPOSITE_RESULT_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Anil1886-1": {
        "aliases": ["Anil", "Battle of El Anil", "El Anil"],
        "audited_unit": "fortification_attack_withdrawal_and_occupation",
        "disposition": "promote_mexican_1886_anil_victory",
        "opposite_result_disposition": (
            "Topete's Mexican defeat at the same fortification occurred in 1885. "
            "It is not merged with Carrillo's separately organized 1886 action."
        ),
        "owner_module": _MODULE_OWNER,
        "scope_note": "Only the fought occupation on 5 May 1886 is rated.",
    },
    "hced-Bacum1868-1": {
        "aliases": ["Bacum", "Bacum church massacre"],
        "audited_unit": "massacre_of_confined_peace_seeking_prisoners",
        "disposition": "terminally_exclude_noncompetitive_massacre",
        "opposite_result_disposition": (
            "Prado's 10 January battle at Bacum is a distinct event and cannot "
            "supply a competitive result to the massacre-tagged February row."
        ),
        "owner_module": _MODULE_OWNER,
        "scope_note": "The 18 February prisoner massacre is not Elo-rateable.",
    },
    "hced-Buatachive1886-1": {
        "aliases": ["Battle of Buatachive", "Buatachive"],
        "audited_unit": "four_day_siege_and_three_hour_final_assault",
        "disposition": "promote_mexican_buatachive_victory",
        "opposite_result_disposition": (
            "Cajeme's escape and continued guerrilla resistance do not reverse "
            "the attested loss of the bounded fortified position."
        ),
        "owner_module": _MODULE_OWNER,
        "scope_note": "Only the 9-12 May siege and assault are rated.",
    },
    "hced-Mount Tambor1740-1": {
        "aliases": ["Battle of Cerro del Tambor", "Mount Tambor"],
        "audited_unit": "single_battle_at_cerro_del_tambor",
        "disposition": "promote_vildosola_tambor_victory",
        "opposite_result_disposition": (
            "Huidobro's earlier retreat and the later Otancahui battle are "
            "separate campaign episodes, not alternate results for Tambor."
        ),
        "owner_module": _MODULE_OWNER,
        "scope_note": "Only Cerro del Tambor is rated; Otancahui remains distinct.",
    },
}


WAVE8_YAQUI_EVENT_BOUNDARIES: dict[str, dict[str, Any]] = {
    "anil_to_buatachive_1886": {
        "candidate_ids": ["hced-Anil1886-1", "hced-Buatachive1886-1"],
        "disposition": "distinct_fortifications_and_sequential_actions",
        "reason": (
            "El Anil was occupied on 5 May. The defenders withdrew toward the "
            "separately fortified Buatachive position, assaulted on 12 May."
        ),
    },
    "bacum_battle_to_church_massacre_1868": {
        "candidate_ids": ["hced-Bacum1868-1"],
        "disposition": "do_not_substitute_adjacent_battle_for_massacre_row",
        "reason": (
            "The 10 January fight and 18 February prisoner massacre occurred at "
            "Bacum in the same year, but the locked row's massacre flag owns the "
            "noncompetitive February episode."
        ),
    },
    "tambor_to_otancahui_1740": {
        "candidate_ids": ["hced-Mount Tambor1740-1"],
        "disposition": "distinct_successive_battles",
        "reason": (
            "Sources place Vildosola's Cerro del Tambor victory before a separate "
            "advance and battle at Otancahui; casualty totals for the two are not "
            "collapsed into one event."
        ),
    },
}


WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "exact_label_boundary": {
        "disposition": "own_exact_yaqui_rows_only",
        "evidence_refs": [
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_texas_band_history",
        ],
        "excluded_labels": [
            "Hiaki",
            "Yaqui Indian",
            "Yaqui Indians",
            "Yaqui Nation",
            "Yaqui people",
            "Yaquis",
            "Yoeme",
        ],
        "owned_candidate_ids": sorted(WAVE8_YAQUI_RESERVED_IDS),
    },
    "modern_tribal_governments": {
        "disposition": "no_identity_or_rating_inheritance",
        "evidence_refs": [
            "wave8_yaqui_inah_padilla_territorio",
            "wave8_yaqui_texas_band_history",
        ],
        "owned_candidate_ids": sorted(WAVE8_YAQUI_RESERVED_IDS),
        "reason": (
            "Historical action formations are not aliases for any modern Yaqui "
            "or Pascua Yaqui government or community."
        ),
    },
    "raw_state_and_coalition_labels": {
        "disposition": "resolve_only_event_bounded_formations",
        "evidence_refs": [
            "wave8_yaqui_mapping_rebellions_1740",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_troncoso_tomo_i",
        ],
        "owned_candidate_ids": sorted(WAVE8_YAQUI_CONTRACT_IDS),
        "reason": (
            "Spain, Mexico, Sonora, Yaqui, and Mayo remain raw context labels; "
            "only the six action-bounded formations are installed."
        ),
    },
}

WAVE8_YAQUI_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"event_boundary:{key}": value
        for key, value in WAVE8_YAQUI_EVENT_BOUNDARIES.items()
    },
    **{
        f"cross_lane:{key}": value
        for key, value in WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS.items()
    },
}

WAVE8_YAQUI_HCED_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_YAQUI_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_YAQUI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_YAQUI_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


def _duplicate_audit(year: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": tuple(sorted(set(map(normalize_label, aliases)))),
        "years": (year,),
    }


WAVE8_YAQUI_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Anil1886-1": _duplicate_audit(
        1886,
        "Action at El Anil",
        "Anil",
        "Battle of Anil",
        "Battle of El Anil",
        "El Anil",
    ),
    "hced-Bacum1868-1": _duplicate_audit(
        1868,
        "Bacum",
        "Bacum church massacre",
        "Bacum massacre",
        "Massacre at Bacum",
        "Santa Rosa de Bacum church massacre",
    ),
    "hced-Buatachive1886-1": _duplicate_audit(
        1886,
        "Battle of Buatachive",
        "Buatachive",
        "Siege of Buatachive",
    ),
    "hced-Mount Tambor1740-1": _duplicate_audit(
        1740,
        "Battle of Cerro del Tambor",
        "Battle of Mount Tambor",
        "Cerro del Tambor",
        "Mount Tambor",
    ),
}


WAVE8_YAQUI_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Anil1886-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_yaqui_cardenas_historia_mexicana",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_troncoso_tomo_i",
        ],
        "raw_point": [-109.0571847, 25.9664053],
        "retained_country": "Mexico",
        "reason": (
            "The HCED point is far south of the attested Yaqui River El Anil "
            "position between Potam and Bacum and is not a battlefield coordinate."
        ),
    },
    "hced-Buatachive1886-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_yaqui_gouy_gilbert",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_troncoso_tomo_i",
        ],
        "raw_point": [-110.2488105, 27.6337884],
        "retained_country": "Mexico",
        "reason": (
            "The four-day operation covered mountain approaches, siege lines, "
            "several fortified heights, and escape routes in the Bacatete. The "
            "raw point is not retained as an exact clash coordinate."
        ),
    },
    "hced-Mount Tambor1740-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_yaqui_acosta_sonora",
            "wave8_yaqui_spicer_cycles",
            "wave8_yaqui_troncoso_tomo_i",
        ],
        "raw_point": [-105.0745437, 19.510535],
        "retained_country": "Mexico",
        "reason": (
            "The HCED point lies on the Jalisco coast, while independent histories "
            "place Cerro del Tambor between the Tecoripa frontier and Yaqui "
            "country in Sonora. The point is demonstrably not the battle site."
        ),
    },
}
WAVE8_YAQUI_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_YAQUI_LOCATION_QUARANTINE_REASONS
)
WAVE8_YAQUI_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_YAQUI_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_YAQUI_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_YAQUI_COUNTRY_QUARANTINE_ADDITIONS,
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
                WAVE8_YAQUI_ADJACENT_LITERAL_LABEL_INVENTORY.items()
            )
        },
        "contracts": WAVE8_YAQUI_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_YAQUI_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_YAQUI_ENTITIES,
        "event_boundaries": WAVE8_YAQUI_EVENT_BOUNDARIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_YAQUI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_YAQUI_EXPECTED_CANDIDATE_IDS),
        "funnel_audit": WAVE8_YAQUI_FUNNEL_AUDIT,
        "hced_duplicate_dispositions": WAVE8_YAQUI_HCED_DUPLICATE_DISPOSITIONS,
        "hced_queue_sha256": WAVE8_YAQUI_HCED_QUEUE_SHA256,
        "holds": WAVE8_YAQUI_HOLDS,
        "integration_dispositions": WAVE8_YAQUI_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_YAQUI_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_queue_sha256": WAVE8_YAQUI_IWBD_QUEUE_SHA256,
        "iwbd_zero_overlap_audit": WAVE8_YAQUI_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_YAQUI_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_YAQUI_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_YAQUI_POINT_QUARANTINE_ADDITIONS
        ),
        "row_dispositions": WAVE8_YAQUI_ROW_DISPOSITIONS,
        "row_hashes": WAVE8_YAQUI_ROW_HASHES,
        "scope_and_opposite_result_audit": (
            WAVE8_YAQUI_SCOPE_AND_OPPOSITE_RESULT_AUDIT
        ),
        "sources": WAVE8_YAQUI_SOURCES,
        "source_row_semantics": WAVE8_YAQUI_SOURCE_ROW_SEMANTICS,
        "terminal_exclusions": WAVE8_YAQUI_TERMINAL_EXCLUSIONS,
        "war_label_inventory": {
            label: list(candidate_ids)
            for label, candidate_ids in WAVE8_YAQUI_WAR_LABEL_INVENTORY.items()
        },
    }


def wave8_yaqui_audit_signature() -> str:
    """Return the deterministic digest of the complete Yaqui adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_YAQUI_FINAL_AUDIT_SIGNATURE = (
    "b140805f5a808448872e1680d3557b4f32f49164ac137607c7030fd8b93d5cb5"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_YAQUI_CONTRACTS),
        len(WAVE8_YAQUI_HOLDS),
        len(WAVE8_YAQUI_TERMINAL_EXCLUSIONS),
    ) != (3, 0, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_YAQUI_ENTITIES), len(WAVE8_YAQUI_SOURCES)) != (6, 9):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_YAQUI_RESERVED_IDS != WAVE8_YAQUI_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if set(WAVE8_YAQUI_SOURCE_ROW_SEMANTICS) != (
        WAVE8_YAQUI_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} source semantics inventory changed")
    for candidate_id, semantics in WAVE8_YAQUI_SOURCE_ROW_SEMANTICS.items():
        if (
            tuple(semantics) != _SOURCE_SEMANTIC_FIELDS
            or semantics["winner_loser_complete"] is not True
            or semantics["winner_raw"] != semantics["side_1_raw"]
            or semantics["loser_raw"] != semantics["side_2_raw"]
            or normalize_label(semantics["side_2_raw"]) != _EXACT_LABEL
            or semantics["modern_location_country"] != "Mexico"
        ):
            raise ValueError(
                f"{_LANE_NAME} source semantics changed: {candidate_id}"
            )
    if WAVE8_YAQUI_WAR_CANDIDATE_IDS != WAVE8_YAQUI_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} war inventory is incomplete")
    if set(WAVE8_YAQUI_ROW_DISPOSITIONS) != WAVE8_YAQUI_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} row disposition inventory changed")
    if _sorted_newline_sha256(WAVE8_YAQUI_EXPECTED_CANDIDATE_IDS) != (
        WAVE8_YAQUI_EXACT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} exact candidate digest changed")
    if WAVE8_YAQUI_EXACT_CANDIDATE_ID_SHA256 != (
        WAVE8_YAQUI_FUNNEL_EVENT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} funnel candidate digest changed")
    if (
        WAVE8_YAQUI_FINAL_AUDIT_SIGNATURE != "__PENDING__"
        and wave8_yaqui_audit_signature() != WAVE8_YAQUI_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    dispositions = (
        WAVE8_YAQUI_CONTRACT_IDS,
        WAVE8_YAQUI_HOLD_IDS,
        WAVE8_YAQUI_TERMINAL_EXCLUSION_IDS,
    )
    for index, left in enumerate(dispositions):
        for right in dispositions[index + 1 :]:
            if left & right:
                raise ValueError(f"{_LANE_NAME} dispositions overlap")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_YAQUI_SOURCES
    }
    if len(source_by_id) != len(WAVE8_YAQUI_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(
        {str(source["source_family_id"]) for source in WAVE8_YAQUI_SOURCES}
    ) != len(WAVE8_YAQUI_SOURCES):
        raise ValueError(f"{_LANE_NAME} source families are not unique")
    for source in WAVE8_YAQUI_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if "wikipedia.org" in str(source["url"]):
            raise ValueError(f"{_LANE_NAME} uses a non-authoritative source")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_YAQUI_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_YAQUI_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_entity_ids = {
        "mexico",
        "mayo",
        "pascua_yaqui_tribe",
        "sonora",
        "spain",
        "yaqui",
        "yaqui_indians",
        "yaqui_nation",
    }
    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for entity in WAVE8_YAQUI_ENTITIES:
        entity_id = str(entity["id"])
        if entity_id in forbidden_entity_ids or entity["aliases"]:
            raise ValueError(f"{_LANE_NAME} installed a generic actor or alias")
        year = int(entity["start_year"])
        if (year, int(entity["end_year"])) not in {(1740, 1740), (1886, 1886)}:
            raise ValueError(f"{_LANE_NAME} entity is not event bounded")
        if "no rating is inherited" not in normalize_label(
            entity["continuity_note"]
        ):
            raise ValueError(f"{_LANE_NAME} continuity firewall changed")
        refs = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity sources changed")
        used_sources.update(refs)

    expected_sides = {
        "hced-Anil1886-1": ({_ANIL_MEXICAN_ID}, {_ANIL_YAQUI_ID}),
        "hced-Buatachive1886-1": (
            {_BUATACHIVE_MEXICAN_ID},
            {_BUATACHIVE_YAQUI_ID},
        ),
        "hced-Mount Tambor1740-1": (
            {_TAMBOR_SPANISH_ID},
            {_TAMBOR_INDIGENOUS_ID},
        ),
    }
    for candidate_id, contract in WAVE8_YAQUI_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_YAQUI_ROW_HASHES[candidate_id]:
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
        if (side_1, side_2) != expected_sides[candidate_id]:
            raise ValueError(f"{_LANE_NAME} event composition changed")
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} opposing sides changed")
        if not (side_1 | side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} contract uses an unknown entity")
        if (
            contract["actor_override"] is not True
            or contract["disposition"] != "promote"
            or contract["event_type"] != "engagement"
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
        if (
            not contract["reviewed_sides"]
            or not contract["reviewed_outcome"]
            or not contract["massacre_disposition"]
        ):
            raise ValueError(f"{_LANE_NAME} participant or harm audit changed")
        used_entities.update(side_1 | side_2)
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")

    exclusion = WAVE8_YAQUI_TERMINAL_EXCLUSIONS["hced-Bacum1868-1"]
    forbidden_nonpromotion_fields = {
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
    }
    if (
        exclusion["raw_row_sha256"]
        != WAVE8_YAQUI_ROW_HASHES["hced-Bacum1868-1"]
        or exclusion["disposition"] != "terminal_exclusion"
        or exclusion["terminal_exclusion"] is not True
        or exclusion["reviewed_outcome"] != "not_rateable_prisoner_massacre"
        or exclusion["unknown_is_never_draw"] is not True
        or exclusion["historical_review"]["competitive_event"] is not False
        or forbidden_nonpromotion_fields & set(exclusion)
    ):
        raise ValueError(f"{_LANE_NAME} Bacum exclusion changed")
    exclusion_refs = list(map(str, exclusion["evidence_refs"]))
    if not _is_sorted_unique(exclusion_refs) or not set(exclusion_refs) <= set(
        source_by_id
    ):
        raise ValueError(f"{_LANE_NAME} exclusion evidence changed")
    used_sources.update(exclusion_refs)

    if set(WAVE8_YAQUI_SCOPE_AND_OPPOSITE_RESULT_AUDIT) != (
        WAVE8_YAQUI_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} scope audit is incomplete")
    for candidate_id, audit in (
        WAVE8_YAQUI_SCOPE_AND_OPPOSITE_RESULT_AUDIT.items()
    ):
        if audit["owner_module"] != _MODULE_OWNER:
            raise ValueError(f"{_LANE_NAME} ownership audit changed")
        item = WAVE8_YAQUI_CONTRACTS.get(candidate_id) or (
            WAVE8_YAQUI_NONPROMOTIONS[candidate_id]
        )
        if audit["audited_unit"] != item["canonical_event"]["granularity"]:
            raise ValueError(f"{_LANE_NAME} event scope changed")
        if not audit["opposite_result_disposition"] or not audit["scope_note"]:
            raise ValueError(f"{_LANE_NAME} opposite-result audit changed")

    if set(WAVE8_YAQUI_EVENT_BOUNDARIES) != {
        "anil_to_buatachive_1886",
        "bacum_battle_to_church_massacre_1868",
        "tambor_to_otancahui_1740",
    }:
        raise ValueError(f"{_LANE_NAME} event-boundary inventory changed")
    for boundary in WAVE8_YAQUI_EVENT_BOUNDARIES.values():
        candidate_ids = list(map(str, boundary["candidate_ids"]))
        if not candidate_ids or not set(candidate_ids) <= WAVE8_YAQUI_RESERVED_IDS:
            raise ValueError(f"{_LANE_NAME} event-boundary ownership changed")
    if set(WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS) != {
        "exact_label_boundary",
        "modern_tribal_governments",
        "raw_state_and_coalition_labels",
    }:
        raise ValueError(f"{_LANE_NAME} cross-lane inventory changed")
    for audit in WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS.values():
        if not set(audit["owned_candidate_ids"]) <= WAVE8_YAQUI_RESERVED_IDS:
            raise ValueError(f"{_LANE_NAME} cross-lane ownership changed")
        refs = list(map(str, audit["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} cross-lane evidence changed")
        used_sources.update(refs)
    expected_integration = {
        **{
            f"event_boundary:{key}": value
            for key, value in WAVE8_YAQUI_EVENT_BOUNDARIES.items()
        },
        **{
            f"cross_lane:{key}": value
            for key, value in WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS.items()
        },
    }
    if WAVE8_YAQUI_INTEGRATION_DISPOSITIONS != expected_integration:
        raise ValueError(f"{_LANE_NAME} integration dispositions changed")

    if set(WAVE8_YAQUI_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_YAQUI_CONTRACT_IDS
    ) or WAVE8_YAQUI_POINT_QUARANTINE_ADDITIONS != WAVE8_YAQUI_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine changed")
    if WAVE8_YAQUI_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    for review in WAVE8_YAQUI_LOCATION_QUARANTINE_REASONS.values():
        if (
            review["actions"] != ["withhold_point"]
            or review["retained_country"] != "Mexico"
        ):
            raise ValueError(f"{_LANE_NAME} location disposition changed")
        refs = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence changed")
        used_sources.update(refs)

    if set(WAVE8_YAQUI_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_YAQUI_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for audit in WAVE8_YAQUI_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, audit["aliases"]))
        years = tuple(map(int, audit["years"]))
        if (
            not _is_sorted_unique(aliases)
            or aliases != list(map(normalize_label, aliases))
            or years != tuple(sorted(set(years)))
        ):
            raise ValueError(f"{_LANE_NAME} duplicate audit changed")
    if (
        WAVE8_YAQUI_HCED_DUPLICATE_DISPOSITIONS
        or WAVE8_YAQUI_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_YAQUI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_YAQUI_OUTCOME_OVERRIDES
    ):
        raise ValueError(f"{_LANE_NAME} acquired an undeclared disposition")
    if used_sources != set(source_by_id):
        raise ValueError(
            f"{_LANE_NAME} sources are not exactly consumed: "
            f"{sorted(set(source_by_id) - used_sources)}"
        )


def validate_wave8_yaqui_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin all and only the exact-label rows, spellings, wars, and hashes."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_YAQUI_CONTRACTS,
        WAVE8_YAQUI_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids: set[str] = set()
    rows_by_id: dict[str, dict[str, Any]] = {}
    tracked_labels: dict[str, set[str]] = {}
    war_labels: dict[str, set[str]] = {}
    known_adjacent = set(WAVE8_YAQUI_ADJACENT_LITERAL_LABEL_INVENTORY)
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id") or "")
        sides = [
            normalize_label(row.get("side_1_raw")),
            normalize_label(row.get("side_2_raw")),
        ]
        if any(label == _EXACT_LABEL for label in sides):
            exact_ids.add(candidate_id)
            rows_by_id[candidate_id] = row
            if sum(label == _EXACT_LABEL for label in sides) != 1:
                raise ValueError(
                    f"{_LANE_NAME} exact-side ownership changed: {candidate_id}"
                )
        for label in sides:
            if "yaqui" in label or label in known_adjacent:
                tracked_labels.setdefault(label, set()).add(candidate_id)
        for war_name in row.get("war_names", []):
            normalized = normalize_label(war_name)
            if "yaqui" in normalized:
                war_labels.setdefault(normalized, set()).add(candidate_id)
    if exact_ids != WAVE8_YAQUI_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Yaqui inventory changed: {sorted(exact_ids)}"
        )
    actual_semantics = {
        candidate_id: {
            field: rows_by_id[candidate_id].get(field)
            for field in _SOURCE_SEMANTIC_FIELDS
        }
        for candidate_id in sorted(rows_by_id)
    }
    if actual_semantics != WAVE8_YAQUI_SOURCE_ROW_SEMANTICS:
        raise ValueError(f"{_LANE_NAME} source semantics changed")
    actual_labels = {
        label: tuple(sorted(tracked_labels.get(label, set())))
        for label in WAVE8_YAQUI_ADJACENT_LITERAL_LABEL_INVENTORY
    }
    if (
        actual_labels != WAVE8_YAQUI_ADJACENT_LITERAL_LABEL_INVENTORY
        or set(tracked_labels) - known_adjacent
    ):
        raise ValueError(f"{_LANE_NAME} adjacent Yaqui spelling inventory changed")
    actual_wars = {
        label: tuple(sorted(candidate_ids))
        for label, candidate_ids in sorted(war_labels.items())
    }
    if actual_wars != WAVE8_YAQUI_WAR_LABEL_INVENTORY:
        raise ValueError(f"{_LANE_NAME} complete Yaqui war inventory changed")
    return {
        "holds": len(WAVE8_YAQUI_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_YAQUI_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_yaqui_funnel(
    funnel: Mapping[str, Any],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin the locked funnel record and enforce all-or-none release overlap."""

    _validate_static()
    records = [
        record
        for record in funnel.get("labels", [])
        if normalize_label(record.get("label")) == _EXACT_LABEL
    ]
    if len(records) != 1 or records[0] != WAVE8_YAQUI_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel record changed")
    overlap = {
        str(event.get("hced_candidate_id"))
        for event in existing_events
        if event.get("hced_candidate_id") in WAVE8_YAQUI_CONTRACT_IDS
    }
    if overlap not in (set(), set(WAVE8_YAQUI_CONTRACT_IDS)):
        raise ValueError(f"{_LANE_NAME} release overlap is partial: {sorted(overlap)}")
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


def _audited_name_year_pairs() -> set[tuple[int, str]]:
    return {
        (year, alias)
        for audit in WAVE8_YAQUI_IWBD_ZERO_OVERLAP_AUDIT.values()
        for year in map(int, audit["years"])
        for alias in map(str, audit["aliases"])
    }


def _probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    if year is None:
        return False
    names = {
        normalize_label(row.get("name")),
        *map(normalize_label, row.get("aliases", [])),
    }
    audited = _audited_name_year_pairs()
    return any((year, name) in audited for name in names)


def validate_wave8_yaqui_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on HCED/IWBD/release twins, leaks, and partial release."""

    validate_wave8_yaqui_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if row.get("candidate_id") not in WAVE8_YAQUI_RESERVED_IDS
        and _probable_twin(row)
    )
    if hced_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable HCED duplicate(s): {hced_twins}"
        )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _probable_twin(row)
    )
    if iwbd_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): {iwbd_twins}"
        )

    existing = list(existing_events)
    exclusion_leaks = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_YAQUI_TERMINAL_EXCLUSION_IDS
    )
    if exclusion_leaks:
        raise ValueError(
            f"{_LANE_NAME} terminally excluded Bacum massacre was rated: "
            f"{exclusion_leaks}"
        )
    overlap = {
        str(event.get("hced_candidate_id"))
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_YAQUI_CONTRACT_IDS
    }
    if overlap not in (set(), set(WAVE8_YAQUI_CONTRACT_IDS)):
        raise ValueError(f"{_LANE_NAME} release overlap is partial: {sorted(overlap)}")
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id") not in WAVE8_YAQUI_RESERVED_IDS
        and not str(event.get("id") or "").startswith(_EVENT_ID_PREFIX)
        and _probable_twin(event)
    )
    if release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable release duplicate(s): "
            f"{release_twins}"
        )
    return {
        "cross_event_boundaries": len(WAVE8_YAQUI_EVENT_BOUNDARIES),
        "cross_lane_dispositions": len(WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": 0,
        "hced_duplicate_dispositions": 0,
        "hced_probable_twins": 0,
        "integration_dispositions": len(WAVE8_YAQUI_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "release_lane_overlap": len(overlap),
        "release_probable_twins": 0,
    }


def install_wave8_yaqui_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_YAQUI_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_yaqui_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_YAQUI_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_YAQUI_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_YAQUI_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_yaqui_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit the three bounded outcomes and never emit the Bacum massacre."""

    validate_wave8_yaqui_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_YAQUI_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine(events)
    return events


def wave8_yaqui_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_YAQUI_CONTRACTS.values(),
                    *WAVE8_YAQUI_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_yaqui_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_literal_labels_audited": len(
            WAVE8_YAQUI_ADJACENT_LITERAL_LABEL_INVENTORY
        ),
        "country_quarantine_additions": len(
            WAVE8_YAQUI_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_event_boundaries": len(WAVE8_YAQUI_EVENT_BOUNDARIES),
        "cross_lane_dispositions": len(WAVE8_YAQUI_CROSS_LANE_DISPOSITIONS),
        "engagement_events": len(WAVE8_YAQUI_CONTRACT_IDS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_YAQUI_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "hced_duplicate_dispositions": len(
            WAVE8_YAQUI_HCED_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_YAQUI_HOLDS),
        "integration_dispositions": len(WAVE8_YAQUI_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_YAQUI_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_YAQUI_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_YAQUI_ENTITIES),
        "new_sources": len(WAVE8_YAQUI_SOURCES),
        "newly_rated_events": len(WAVE8_YAQUI_CONTRACTS),
        "outcome_overrides": len(WAVE8_YAQUI_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_YAQUI_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_YAQUI_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_YAQUI_EXPECTED_CANDIDATE_IDS),
        "scope_audits": len(WAVE8_YAQUI_SCOPE_AND_OPPOSITE_RESULT_AUDIT),
        "sole_blocker_rows": int(WAVE8_YAQUI_FUNNEL_AUDIT["sole_blocker_events"]),
        "terminal_exclusions": len(WAVE8_YAQUI_TERMINAL_EXCLUSIONS),
        "touched_hced_rows": len(WAVE8_YAQUI_TOUCHED_CANDIDATE_IDS),
        "war_labels_audited": len(WAVE8_YAQUI_WAR_LABEL_INVENTORY),
        "war_rows_audited": len(WAVE8_YAQUI_WAR_CANDIDATE_IDS),
    }


def wave8_yaqui_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_YAQUI_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_YAQUI_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_yaqui_row_dispositions() -> dict[str, str]:
    _validate_static()
    return dict(sorted(WAVE8_YAQUI_ROW_DISPOSITIONS.items()))


def wave8_yaqui_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "audit": "candidate_keyed_exact_label_event_bounded_formations",
        "cohorts": wave8_yaqui_cohort_counts(),
        "counts": wave8_yaqui_counts(),
        "final_audit_signature": WAVE8_YAQUI_FINAL_AUDIT_SIGNATURE,
        "module_owner": _MODULE_OWNER,
        "row_dispositions": wave8_yaqui_row_dispositions(),
    }
