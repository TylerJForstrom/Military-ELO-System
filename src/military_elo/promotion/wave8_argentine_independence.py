"""Exact Wave 8 audit for Argentine-independence HCED rows."""

from __future__ import annotations

import copy
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


_LANE_NAME = "Wave 8 Argentine independence"
_ARGENTINE_CLUSTER_ID = "hced_war_argentine_war_of_independence"
_CHILEAN_CLUSTER_ID = "hced_war_chilean_war_of_independence"

# This signature pins the complete audit: source fixtures, bounded identities,
# exact row hashes, promotions, terminal exclusion, and reserved inventory.
WAVE8_ARGENTINE_INDEPENDENCE_FINAL_AUDIT_SIGNATURE = (
    "aaf88553210099f411904f91e4c03c5fdddac18ae69e3b167fbb84440fb0060e"
)


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    family: str,
    *,
    source_type: str,
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
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": family,
        "evidence_roles": sorted(roles),
    }


WAVE8_ARGENTINE_INDEPENDENCE_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_argentine_independence_navy_overview",
        "La Guerra de la Independencia (1810-1824)",
        "https://www.argentina.gob.ar/armada/nueva-historia-naval/independencia-1810",
        "Argentine Navy, Government of Argentina",
        "argentine_navy_independence_history",
        source_type="official_military_history",
        outcome=True,
    ),
    _source(
        "wave8_argentine_independence_navy_brown",
        "Almirante Guillermo Brown",
        "https://www.argentina.gob.ar/armada/historia-naval/heroes-navales/almirante-guillermo-brown",
        "Argentine Navy, Government of Argentina",
        "argentine_navy_brown_history",
        source_type="official_military_history",
        outcome=True,
    ),
    _source(
        "wave8_argentine_independence_navy_segui",
        "Vicealmirante Francisco José Seguí",
        "https://www.argentina.gob.ar/armada/historia-naval/heroes-navales/vicealmirante-francisco-jose-segui",
        "Argentine Navy, Government of Argentina",
        "argentine_navy_segui_history",
        source_type="official_military_history",
    ),
    _source(
        "wave8_argentine_independence_morea_auxiliary_army",
        (
            "El proceso de profesionalización del Ejército Auxiliar del Perú "
            "durante las guerras de independencia"
        ),
        "https://cerac.unlpam.edu.ar/index.php/quintosol/article/view/131",
        "Quinto Sol, Universidad Nacional de La Pampa",
        "quinto_sol_unlpam_auxiliary_army",
        source_type="academic_journal",
    ),
    _source(
        "wave8_argentine_independence_cotagaita_suipacha",
        "7 de noviembre: Batalla de Suipacha, la primera victoria Patria",
        "https://www.argentina.gob.ar/node/285004",
        "Government of Argentina",
        "argentina_gob_ar_independence_history",
        source_type="official_history",
        outcome=True,
    ),
    _source(
        "wave8_argentine_independence_polastrelli_huaqui",
        (
            "Derrotas militares, ¿acusaciones políticas? Los juicios contra los "
            "jefes de las campañas al Paraguay y al Alto Perú, 1811-1813"
        ),
        "https://cerac.unlpam.edu.ar/index.php/quintosol/article/view/2559",
        "Quinto Sol, Universidad Nacional de La Pampa",
        "quinto_sol_unlpam_huaqui",
        source_type="academic_journal",
        outcome=True,
    ),
    _source(
        "wave8_argentine_independence_unla_belgrano",
        "El legado de Belgrano",
        (
            "https://www.unla.edu.ar/documentos/centros/manuel_ugarte/"
            "El%20legado%20de%20Belgrano.pdf"
        ),
        "Universidad Nacional de Lanús",
        "unla_manuel_ugarte_belgrano",
        source_type="academic_reference",
        outcome=True,
    ),
    _source(
        "wave8_argentine_independence_unc_belgrano",
        "Biografía de Manuel Belgrano",
        (
            "https://www.eco.unc.edu.ar/recursos-de-informacion/?catid=31&"
            "id=330%3Abiografia-de-manuel-belgrano&view=article"
        ),
        "Faculty of Economic Sciences, National University of Córdoba",
        "unc_belgrano_history",
        source_type="university_reference",
        outcome=True,
    ),
    _source(
        "wave8_argentine_independence_anh_index",
        "Historia de la Nación Argentina, volume XI: General index",
        (
            "https://repositorio.anh.org.ar/jspui/bitstream/anh/57/1/"
            "BaANH44820_Historia_de_la_Nacion_Argentina_11_-_"
            "Academia_Nacional_de_la_Historia.pdf"
        ),
        "Academia Nacional de la Historia (Argentina)",
        "academia_nacional_historia_argentina",
        source_type="academic_reference",
        outcome=True,
    ),
    _source(
        "wave8_argentine_independence_rah_olaneta",
        "Pedro Antonio de Olañeta Marquiegui",
        "https://historia-hispanica.rah.es/biografias/34084-pedro-antonio-de-olaneta-marquiegui",
        "Real Academia de la Historia",
        "real_academia_historia_olaneta",
        source_type="national_academy_reference",
    ),
    _source(
        "wave8_argentine_independence_unju_leon",
        "Día Grande de Jujuy: Batalla de León",
        "https://unjudiario.unju.edu.ar/jujuy/dia-grande-de-jujuy-batalla-de-leon",
        "Universidad Nacional de Jujuy",
        "national_university_jujuy_leon",
        source_type="university_history",
        outcome=True,
    ),
    _source(
        "wave8_argentine_independence_jujuy_government_leon",
        (
            "Sadir valoró el espíritu de lucha del pueblo jujeño durante la "
            "conmemoración del Día Grande de Jujuy"
        ),
        (
            "https://prensa.jujuy.gob.ar/carlos-sadir/sadir-valoro-el-espiritu-"
            "lucha-del-pueblo-jujeno-la-conmemoracion-del-dia-grande-jujuy-n119251"
        ),
        "Government of Jujuy Province",
        "jujuy_government_history",
        source_type="official_history",
        outcome=True,
    ),
    _source(
        "wave8_argentine_independence_memoria_cancha_rayada",
        "Guerras de independencia",
        "https://www.memoriachilena.gob.cl/602/w3-article-97864.html",
        "Memoria Chilena, National Library of Chile",
        "memoria_chilena_independence_history",
        source_type="official_library_reference",
        outcome=True,
    ),
    _source(
        "wave8_argentine_independence_chile_academy_cancha_rayada",
        "Combate o desastre de Cancha Rayada",
        (
            "https://www.academiahistoriamilitar.cl/academia/"
            "combate-o-desastre-de-cancha-rayada/"
        ),
        "Academia de Historia Militar de Chile",
        "chile_military_history_academy_cancha_rayada",
        source_type="institutional_military_history",
        outcome=True,
    ),
)


def _event_entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    source_ids: list[str],
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
            f"{boundary_note} No rating is inherited by any predecessor, "
            "successor, umbrella polity, similarly named force, or other engagement."
        ),
        "source_ids": sorted(source_ids),
    }


WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES: tuple[dict[str, Any], ...] = (
    _event_entity(
        "primera_junta_auxiliary_army_cotagaita_1810",
        "Primera Junta auxiliary army at Cotagaita (1810)",
        "revolutionary_army",
        1810,
        "Upper Peru",
        [
            "wave8_argentine_independence_cotagaita_suipacha",
            "wave8_argentine_independence_morea_auxiliary_army",
        ],
        (
            "Event-bounded first auxiliary expedition organized by the Primera "
            "Junta and militarily commanded by Antonio González Balcarce."
        ),
    ),
    _event_entity(
        "cordoba_royalist_force_cotagaita_1810",
        "José de Córdoba's royalist force at Cotagaita (1810)",
        "royalist_field_force",
        1810,
        "Upper Peru",
        ["wave8_argentine_independence_cotagaita_suipacha"],
        (
            "Event-bounded Spanish royalist force under José de Córdoba y Rojas "
            "at the Cotagaita positions."
        ),
    ),
    _event_entity(
        "junta_grande_auxiliary_army_huaqui_1811",
        "Junta Grande auxiliary army at Huaqui (1811)",
        "revolutionary_army",
        1811,
        "Upper Peru",
        [
            "wave8_argentine_independence_morea_auxiliary_army",
            "wave8_argentine_independence_polastrelli_huaqui",
        ],
        (
            "Event-bounded Army Auxiliary of Peru sent by the Junta Grande, with "
            "Juan José Castelli holding political authority and Antonio González "
            "Balcarce the military command."
        ),
    ),
    _event_entity(
        "goyeneche_royalist_army_huaqui_1811",
        "José Manuel de Goyeneche's royalist army at Huaqui (1811)",
        "royalist_army",
        1811,
        "Upper Peru",
        ["wave8_argentine_independence_polastrelli_huaqui"],
        (
            "Event-bounded Spanish royalist army of the Viceroyalty of Peru under "
            "José Manuel de Goyeneche."
        ),
    ),
    _event_entity(
        "united_provinces_zelaya_detachment_pequereque_1813",
        "Cornelio Zelaya's Army of the North detachment at Pequereque (1813)",
        "revolutionary_cavalry_detachment",
        1813,
        "Upper Peru",
        [
            "wave8_argentine_independence_anh_index",
            "wave8_argentine_independence_unla_belgrano",
        ],
        (
            "Event-bounded advance-guard cavalry detachment of the United "
            "Provinces' Army of the North under Cornelio Zelaya."
        ),
    ),
    _event_entity(
        "olaneta_royalist_detachment_pequereque_1813",
        "Pedro Antonio de Olañeta's royalist detachment at Pequereque (1813)",
        "royalist_detachment",
        1813,
        "Upper Peru",
        [
            "wave8_argentine_independence_anh_index",
            "wave8_argentine_independence_rah_olaneta",
        ],
        (
            "Event-bounded Spanish royalist detachment commanded by Pedro Antonio "
            "de Olañeta in the Second Upper Peru campaign."
        ),
    ),
    _event_entity(
        "united_provinces_army_north_ayohuma_1813",
        "United Provinces Army of the North at Ayohuma (1813)",
        "revolutionary_army",
        1813,
        "Upper Peru",
        [
            "wave8_argentine_independence_unc_belgrano",
            "wave8_argentine_independence_unla_belgrano",
        ],
        (
            "Event-bounded United Provinces Army of the North under Manuel "
            "Belgrano at Ayohuma."
        ),
    ),
    _event_entity(
        "pezuela_royalist_army_ayohuma_1813",
        "Joaquín de la Pezuela's royalist army at Ayohuma (1813)",
        "royalist_army",
        1813,
        "Upper Peru",
        [
            "wave8_argentine_independence_unc_belgrano",
            "wave8_argentine_independence_unla_belgrano",
        ],
        (
            "Event-bounded Spanish royalist Army of Upper Peru under Joaquín de "
            "la Pezuela."
        ),
    ),
    _event_entity(
        "united_provinces_nother_naval_division_1814",
        "Tomás Nother's United Provinces naval division (1814)",
        "revolutionary_naval_division",
        1814,
        "Río de la Plata and Uruguay River",
        [
            "wave8_argentine_independence_navy_overview",
            "wave8_argentine_independence_navy_segui",
        ],
        (
            "Event-bounded naval division of the United Provinces under Tomás "
            "Nother at Arroyo de la China."
        ),
    ),
    _event_entity(
        "romarate_montevideo_royalist_squadron_1814",
        "Jacinto de Romarate's Montevideo royalist squadron (1814)",
        "royalist_naval_squadron",
        1814,
        "Río de la Plata and Uruguay River",
        [
            "wave8_argentine_independence_navy_brown",
            "wave8_argentine_independence_navy_overview",
        ],
        (
            "Event-bounded Spanish royalist squadron from Montevideo under "
            "Jacinto de Romarate at Arroyo de la China."
        ),
    ),
    _event_entity(
        "gorriti_jujuy_militia_leon_1821",
        "José Ignacio Gorriti's Jujuy militia at León (1821)",
        "local_revolutionary_militia",
        1821,
        "Jujuy jurisdiction, Salta",
        [
            "wave8_argentine_independence_jujuy_government_leon",
            "wave8_argentine_independence_unju_leon",
        ],
        (
            "Event-bounded local Jujuy gaucho militia under José Ignacio Gorriti; "
            "it is not projected backward or forward as a national Argentine army."
        ),
    ),
    _event_entity(
        "marquiegui_royalist_vanguard_leon_1821",
        "Guillermo Marquiegui's royalist vanguard at León (1821)",
        "royalist_vanguard",
        1821,
        "Jujuy jurisdiction, Salta",
        [
            "wave8_argentine_independence_jujuy_government_leon",
            "wave8_argentine_independence_unju_leon",
        ],
        (
            "Event-bounded Spanish royalist invasion vanguard under Guillermo "
            "Marquiegui, within Pedro Antonio de Olañeta's larger command."
        ),
    ),
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


def _war_label_review(
    raw_war_name: str,
    expected_raw_cluster_id: str,
    classification: str,
    evidence_source_ids: list[str],
) -> dict[str, Any]:
    return {
        "raw_war_names": [raw_war_name],
        "expected_raw_cluster_id": expected_raw_cluster_id,
        "reviewed_war_name": "Argentine War of Independence",
        "reviewed_cluster_id": _ARGENTINE_CLUSTER_ID,
        "classification": classification,
        "evidence_source_ids": sorted(evidence_source_ids),
    }


_ROW_HASHES: dict[str, str] = {
    "hced-Arroyo de la China1814-1": (
        "9617ba97c7a36e9e6ba90f1bad3346c7ec9bbb02ebf4a41df65ef6d858e751b6"
    ),
    "hced-Ayohuma1813-1": (
        "a4e6c95ad3d8d8b720b03319c664462efd055a848362df0ade2c09084ac43989"
    ),
    "hced-Cancha Rayada1813-1": (
        "22eaae0ed180f592b0303cdaf1c6c42b77b97b6ed4c370450b62be2a1528f16e"
    ),
    "hced-Cotagaita1810-1": (
        "817abd96fea2807deb517721263997351e11c35f796791025354f5ceca4e4fdd"
    ),
    "hced-Huaqui1811-1": (
        "455e0765f5d273cb368c2f705acc44c74ce5ec5f56f55989011146da67eafc47"
    ),
    "hced-Jujuy1821-1": (
        "de33ae21d49f30cf2b40ba6d364099ccd929974ad5f109b1cb7f14bb50d70f59"
    ),
    "hced-Pequereque1813-1": (
        "d11a255fc73008e2ae52ee3529a2ecd98768f98d40c115270413b308c06c92ae"
    ),
}


WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Cotagaita1810-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Cotagaita1810-1"],
        "canonical_event": _canonical("Combat of Cotagaita", 1810),
        "exact_date": "1810-10-27",
        "cohort": "first_upper_peru_campaign",
        "side_1_entity_ids": ["cordoba_royalist_force_cotagaita_1810"],
        "side_2_entity_ids": ["primera_junta_auxiliary_army_cotagaita_1810"],
        "winner_side": 1,
        "result_type": "win",
        "war_type": "colonial_anti_colonial",
        "evidence_refs": sorted(
            [
                "wave8_argentine_independence_cotagaita_suipacha",
                "wave8_argentine_independence_morea_auxiliary_army",
            ]
        ),
        "outcome_source_ids": [
            "wave8_argentine_independence_cotagaita_suipacha"
        ],
        "outcome_source_family_ids": [
            "argentina_gob_ar_independence_history"
        ],
        "source_outcome_override": False,
        "actor_override": True,
        "historical_review": {
            "event_scope": "competitive_engagement",
            "revolutionary_authority": "Primera Junta of the Río de la Plata",
            "revolutionary_force": "First Auxiliary Expedition to Upper Peru",
            "revolutionary_commander": "Antonio González Balcarce",
            "revolutionary_side": 2,
            "royalist_authority": "Spanish royalist command in Upper Peru",
            "royalist_force": "Fortified Cotagaita royalist force",
            "royalist_commander": "José de Córdoba y Rojas",
            "royalist_side": 1,
            "outcome": "royalist_victory",
        },
        "war_label_review": _war_label_review(
            "Argentine War of Independence",
            _ARGENTINE_CLUSTER_ID,
            "confirmed_argentine_upper_peru_theatre",
            ["wave8_argentine_independence_cotagaita_suipacha"],
        ),
        "reservations": [
            (
                "Juan José Castelli's political role is not substituted for "
                "Balcarce's military command."
            ),
            (
                "The result is the 27 October tactical repulse, not a campaign "
                "result inferred from the later victory at Suipacha."
            ),
        ],
        "audit_note": (
            "The Primera Junta's first auxiliary expedition under Balcarce was "
            "repulsed from José de Córdoba's fortified positions on 27 October "
            "1810; the raw generic revolutionary label is not retained."
        ),
    },
    "hced-Huaqui1811-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Huaqui1811-1"],
        "canonical_event": _canonical("Battle of Huaqui", 1811),
        "exact_date": "1811-06-20",
        "cohort": "first_upper_peru_campaign",
        "side_1_entity_ids": ["goyeneche_royalist_army_huaqui_1811"],
        "side_2_entity_ids": ["junta_grande_auxiliary_army_huaqui_1811"],
        "winner_side": 1,
        "result_type": "win",
        "war_type": "colonial_anti_colonial",
        "evidence_refs": sorted(
            [
                "wave8_argentine_independence_morea_auxiliary_army",
                "wave8_argentine_independence_polastrelli_huaqui",
            ]
        ),
        "outcome_source_ids": [
            "wave8_argentine_independence_polastrelli_huaqui"
        ],
        "outcome_source_family_ids": ["quinto_sol_unlpam_huaqui"],
        "source_outcome_override": False,
        "actor_override": True,
        "historical_review": {
            "event_scope": "competitive_engagement",
            "revolutionary_authority": "Junta Grande of the Río de la Plata",
            "revolutionary_force": "Army Auxiliary of Peru",
            "revolutionary_commander": "Antonio González Balcarce",
            "revolutionary_side": 2,
            "royalist_authority": "Viceroyalty of Peru royalist command",
            "royalist_force": "Goyeneche's royalist army",
            "royalist_commander": "José Manuel de Goyeneche",
            "royalist_side": 1,
            "outcome": "royalist_victory",
        },
        "war_label_review": _war_label_review(
            "Argentine War of Independence",
            _ARGENTINE_CLUSTER_ID,
            "confirmed_argentine_upper_peru_theatre",
            ["wave8_argentine_independence_polastrelli_huaqui"],
        ),
        "reservations": [
            (
                "Castelli's supreme political authority and Balcarce's military "
                "command remain distinct in the identity review."
            ),
            (
                "The ensuing collapse of the first Upper Peru expedition is not "
                "rated as an additional strategic result."
            ),
        ],
        "audit_note": (
            "On 20 June 1811 Goyeneche's royalist army defeated the Junta Grande's "
            "Army Auxiliary of Peru under Balcarce at Huaqui."
        ),
    },
    "hced-Pequereque1813-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Pequereque1813-1"],
        "canonical_event": _canonical("Combat of Pequereque", 1813),
        "exact_date": "1813-06-19",
        "cohort": "second_upper_peru_campaign",
        "side_1_entity_ids": [
            "united_provinces_zelaya_detachment_pequereque_1813"
        ],
        "side_2_entity_ids": ["olaneta_royalist_detachment_pequereque_1813"],
        "winner_side": 1,
        "result_type": "win",
        "war_type": "colonial_anti_colonial",
        "evidence_refs": sorted(
            [
                "wave8_argentine_independence_anh_index",
                "wave8_argentine_independence_rah_olaneta",
                "wave8_argentine_independence_unla_belgrano",
            ]
        ),
        "outcome_source_ids": ["wave8_argentine_independence_anh_index"],
        "outcome_source_family_ids": [
            "academia_nacional_historia_argentina"
        ],
        "source_outcome_override": False,
        "actor_override": True,
        "historical_review": {
            "event_scope": "limited_competitive_advance_guard_engagement",
            "revolutionary_authority": "United Provinces of the Río de la Plata",
            "revolutionary_force": "Army of the North cavalry advance guard",
            "revolutionary_commander": "Cornelio Zelaya",
            "revolutionary_side": 1,
            "royalist_authority": "Spanish royalist command in Upper Peru",
            "royalist_force": "Olañeta's royalist detachment",
            "royalist_commander": "Pedro Antonio de Olañeta",
            "royalist_side": 2,
            "outcome": "revolutionary_victory",
        },
        "war_label_review": _war_label_review(
            "Chilean War of Independence",
            _CHILEAN_CLUSTER_ID,
            "corrected_mislabeled_chilean_theatre",
            [
                "wave8_argentine_independence_anh_index",
                "wave8_argentine_independence_rah_olaneta",
            ],
        ),
        "reservations": [
            (
                "The five-and-a-half-hour advance-guard action is rated as a "
                "limited engagement, not as the whole campaign."
            ),
            (
                "The royalist reoccupation of Pequereque days later does not "
                "reverse Zelaya's tactical result on 19 June."
            ),
            (
                "The Chilean-war label is corrected by inference from the exact "
                "Upper Peru event, commanders, and campaign context."
            ),
        ],
        "audit_note": (
            "The Academy index records Zelaya's patriot victory over the royalists "
            "on 19 June 1813. The reviewed commanders and Upper Peru campaign make "
            "HCED's Chilean-war label a source-record misclassification."
        ),
    },
    "hced-Ayohuma1813-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Ayohuma1813-1"],
        "canonical_event": _canonical("Battle of Ayohuma", 1813),
        "exact_date": "1813-11-14",
        "cohort": "second_upper_peru_campaign",
        "side_1_entity_ids": ["pezuela_royalist_army_ayohuma_1813"],
        "side_2_entity_ids": ["united_provinces_army_north_ayohuma_1813"],
        "winner_side": 1,
        "result_type": "win",
        "war_type": "colonial_anti_colonial",
        "evidence_refs": sorted(
            [
                "wave8_argentine_independence_unc_belgrano",
                "wave8_argentine_independence_unla_belgrano",
            ]
        ),
        "outcome_source_ids": ["wave8_argentine_independence_unc_belgrano"],
        "outcome_source_family_ids": ["unc_belgrano_history"],
        "source_outcome_override": False,
        "actor_override": True,
        "historical_review": {
            "event_scope": "competitive_engagement",
            "revolutionary_authority": "United Provinces of the Río de la Plata",
            "revolutionary_force": "Army of the North",
            "revolutionary_commander": "Manuel Belgrano",
            "revolutionary_side": 2,
            "royalist_authority": "Viceroyalty of Peru royalist command",
            "royalist_force": "Royalist Army of Upper Peru",
            "royalist_commander": "Joaquín de la Pezuela",
            "royalist_side": 1,
            "outcome": "royalist_victory",
        },
        "war_label_review": _war_label_review(
            "Argentine War",
            "hced_war_argentine_war",
            "normalized_imprecise_argentine_war_label",
            [
                "wave8_argentine_independence_unc_belgrano",
                "wave8_argentine_independence_unla_belgrano",
            ],
        ),
        "reservations": [
            (
                "The event-bounded Ayohuma army identity does not inherit ratings "
                "from Belgrano's other Army of the North engagements."
            ),
            (
                "The campaign's strategic consequences are not promoted as a "
                "second result."
            ),
        ],
        "audit_note": (
            "On 14 November 1813 Pezuela's royalist army defeated Manuel Belgrano's "
            "United Provinces Army of the North at Ayohuma."
        ),
    },
    "hced-Arroyo de la China1814-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Arroyo de la China1814-1"],
        "canonical_event": _canonical("Naval Combat of Arroyo de la China", 1814),
        "exact_date": "1814-03-28",
        "cohort": "naval_campaign_1814",
        "side_1_entity_ids": ["romarate_montevideo_royalist_squadron_1814"],
        "side_2_entity_ids": ["united_provinces_nother_naval_division_1814"],
        "winner_side": 1,
        "result_type": "win",
        "war_type": "colonial_anti_colonial",
        "evidence_refs": sorted(
            [
                "wave8_argentine_independence_navy_brown",
                "wave8_argentine_independence_navy_overview",
                "wave8_argentine_independence_navy_segui",
            ]
        ),
        "outcome_source_ids": [
            "wave8_argentine_independence_navy_overview"
        ],
        "outcome_source_family_ids": [
            "argentine_navy_independence_history"
        ],
        "source_outcome_override": False,
        "actor_override": True,
        "historical_review": {
            "event_scope": "competitive_naval_engagement",
            "revolutionary_authority": (
                "Supreme Directory of the United Provinces of the Río de la Plata"
            ),
            "revolutionary_force": "Nother's naval division",
            "revolutionary_commander": "Tomás Nother",
            "revolutionary_side": 2,
            "royalist_authority": "Spanish royalist government of Montevideo",
            "royalist_force": "Romarate's royalist squadron",
            "royalist_commander": "Jacinto de Romarate",
            "royalist_side": 1,
            "outcome": "royalist_victory",
        },
        "war_label_review": _war_label_review(
            "War of Independence",
            "hced_war_war_of_independence",
            "normalized_imprecise_independence_label",
            [
                "wave8_argentine_independence_navy_brown",
                "wave8_argentine_independence_navy_overview",
            ],
        ),
        "reservations": [
            (
                "The raw place label also names a January 1814 land action in the "
                "civil conflict; HCED's Sea theatre and Spanish opponent resolve "
                "this row only to the 28 March naval combat."
            ),
            (
                "The United Provinces division and Montevideo squadron are bounded "
                "to this engagement rather than inherited from umbrella navies."
            ),
        ],
        "audit_note": (
            "The Argentine Navy records Romarate's royalist victory over Nother's "
            "United Provinces division on 28 March 1814; the same-name January land "
            "action is excluded from this row."
        ),
    },
    "hced-Jujuy1821-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Jujuy1821-1"],
        "canonical_event": _canonical("Battle of León (Día Grande de Jujuy)", 1821),
        "exact_date": "1821-04-27",
        "cohort": "jujuy_defense_1821",
        "side_1_entity_ids": ["gorriti_jujuy_militia_leon_1821"],
        "side_2_entity_ids": ["marquiegui_royalist_vanguard_leon_1821"],
        "winner_side": 1,
        "result_type": "win",
        "war_type": "colonial_anti_colonial",
        "evidence_refs": sorted(
            [
                "wave8_argentine_independence_jujuy_government_leon",
                "wave8_argentine_independence_unju_leon",
            ]
        ),
        "outcome_source_ids": [
            "wave8_argentine_independence_jujuy_government_leon"
        ],
        "outcome_source_family_ids": ["jujuy_government_history"],
        "source_outcome_override": False,
        "actor_override": True,
        "historical_review": {
            "event_scope": "competitive_engagement",
            "revolutionary_authority": (
                "Local Jujuy jurisdiction within Salta after the central collapse"
            ),
            "revolutionary_force": "Jujuy gaucho militia",
            "revolutionary_commander": "José Ignacio Gorriti",
            "revolutionary_side": 1,
            "royalist_authority": "Spanish royalist command in Upper Peru",
            "royalist_force": "Marquiegui's invasion vanguard",
            "royalist_commander": "Guillermo Marquiegui",
            "royalist_side": 2,
            "outcome": "revolutionary_victory",
        },
        "war_label_review": _war_label_review(
            "Argentine War of Independence",
            _ARGENTINE_CLUSTER_ID,
            "confirmed_argentine_jujuy_theatre",
            [
                "wave8_argentine_independence_jujuy_government_leon",
                "wave8_argentine_independence_unju_leon",
            ],
        ),
        "reservations": [
            (
                "The raw city label is canonicalized to the attested Battle of "
                "León; the HCED San Salvador de Jujuy point remains a place-level "
                "location assertion, not exact battlefield geometry."
            ),
            (
                "No centralized Argentine-state identity is invented for 1821: "
                "the reviewed source places Jujuy within Salta amid national anarchy."
            ),
        ],
        "audit_note": (
            "The 27 April 1821 Battle of León was a local Jujuy militia victory "
            "under Gorriti over Marquiegui's royalist vanguard, not a timeless "
            "national-rebel identity."
        ),
    },
}


WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS: dict[
    str, dict[str, Any]
] = {
    "hced-Cancha Rayada1813-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Cancha Rayada1813-1"],
        "canonical_event": _canonical("Combat of Cancha Rayada", 1814),
        "disposition": "terminal_exclusion",
        "hold_category": "misdated_reversed_chilean_event",
        "raw_queue_assertion": {
            "year": 1813,
            "winner_raw": "Argentinian Rebels",
            "loser_raw": "Pro-Spanish Guerillas",
            "war_names": ["Chilean War of Independence"],
        },
        "reviewed_event": {
            "exact_date": "1814-03-29",
            "event_scope": "competitive_engagement",
            "revolutionary_authority": "Chilean patriot government",
            "revolutionary_force": "Chilean patriot force",
            "revolutionary_commander": "Manuel Blanco Encalada",
            "royalist_authority": "Spanish royalist command in Chile",
            "royalist_force": "Royalist force at Cancha Rayada",
            "royalist_commander": "Ángel Calvo",
            "outcome": "royalist_victory",
            "theatre": "Chilean War of Independence",
        },
        "war_label_review": {
            "raw_war_names": ["Chilean War of Independence"],
            "expected_raw_cluster_id": _CHILEAN_CLUSTER_ID,
            "reviewed_war_name": "Chilean War of Independence",
            "reviewed_cluster_id": _CHILEAN_CLUSTER_ID,
            "classification": "confirmed_chilean_theatre_outside_argentine_lane",
            "evidence_source_ids": sorted(
                [
                    "wave8_argentine_independence_chile_academy_cancha_rayada",
                    "wave8_argentine_independence_memoria_cancha_rayada",
                ]
            ),
        },
        "reservations": [
            (
                "Authoritative Chilean sources date the named combat to 29 March "
                "1814 and give the victory to Ángel Calvo's royalists."
            ),
            (
                "The 1813 Cancha Rayada locality was associated with the patriot "
                "camp and San Carlos campaign, but no defensible named 1813 patriot "
                "victory matching this row was found."
            ),
            (
                "This 1814 combat must also remain distinct from the second Battle "
                "of Cancha Rayada in 1818."
            ),
        ],
        "hold_reason": (
            "The row is both one year early and outcome-reversed for the attested "
            "named combat. It also belongs to the Chilean, not Argentine, theatre, "
            "so repairing it inside this lane would create a different event."
        ),
        "evidence_refs": sorted(
            [
                "wave8_argentine_independence_chile_academy_cancha_rayada",
                "wave8_argentine_independence_memoria_cancha_rayada",
            ]
        ),
    },
}

# The shared exact-wave API calls nonpromotions holds. This row is conclusively
# excluded rather than left as an open research question.
WAVE8_ARGENTINE_INDEPENDENCE_HOLDS = (
    WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS
)

WAVE8_ARGENTINE_INDEPENDENCE_CONTRACT_IDS = frozenset(
    WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS
)
WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS
)
WAVE8_ARGENTINE_INDEPENDENCE_HOLD_IDS = (
    WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSION_IDS
)
WAVE8_ARGENTINE_INDEPENDENCE_RESERVED_IDS = (
    WAVE8_ARGENTINE_INDEPENDENCE_CONTRACT_IDS
    | WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSION_IDS
)
WAVE8_ARGENTINE_INDEPENDENCE_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def wave8_argentine_independence_signature() -> str:
    payload = {
        "contracts": WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS,
        "entities": WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES,
        "expected_candidate_ids": sorted(
            WAVE8_ARGENTINE_INDEPENDENCE_EXPECTED_CANDIDATE_IDS
        ),
        "row_hashes": _ROW_HASHES,
        "sources": WAVE8_ARGENTINE_INDEPENDENCE_SOURCES,
        "terminal_exclusions": WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS),
        len(WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS),
    ) != (6, 1):
        raise ValueError("Wave 8 Argentine-independence disposition changed")
    if (
        WAVE8_ARGENTINE_INDEPENDENCE_RESERVED_IDS
        != WAVE8_ARGENTINE_INDEPENDENCE_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError("Wave 8 Argentine-independence reservations are incomplete")
    if (
        WAVE8_ARGENTINE_INDEPENDENCE_CONTRACT_IDS
        & WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSION_IDS
    ):
        raise ValueError("Wave 8 Argentine-independence dispositions overlap")
    if (
        wave8_argentine_independence_signature()
        != WAVE8_ARGENTINE_INDEPENDENCE_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError("Wave 8 Argentine-independence audit signature changed")

    source_by_id = {
        str(source["id"]): source
        for source in WAVE8_ARGENTINE_INDEPENDENCE_SOURCES
    }
    if len(source_by_id) != len(WAVE8_ARGENTINE_INDEPENDENCE_SOURCES):
        raise ValueError("Wave 8 Argentine-independence source IDs are not unique")
    entity_by_id = {
        str(entity["id"]): entity
        for entity in WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES):
        raise ValueError("Wave 8 Argentine-independence entity IDs are not unique")
    if (len(source_by_id), len(entity_by_id)) != (14, 12):
        raise ValueError("Wave 8 Argentine-independence fixture inventory changed")

    forbidden_identity_labels = {
        "argentine rebels",
        "argentinian rebels",
        "argentine revolutionaries",
        "argentinian revolutionaries",
    }
    for entity in WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(
                "Wave 8 Argentine-independence identities must be alias-free"
            )
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(
                "Wave 8 Argentine-independence identity is not event-bounded"
            )
        if str(entity["name"]).casefold() in forbidden_identity_labels:
            raise ValueError(
                "Wave 8 Argentine-independence opened a generic rebel identity"
            )
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(
                "Wave 8 Argentine-independence identity permits rating inheritance"
            )
        entity_sources = list(map(str, entity["source_ids"]))
        if entity_sources != sorted(set(entity_sources)):
            raise ValueError(
                "Wave 8 Argentine-independence entity sources are nondeterministic"
            )
        if not set(entity_sources) <= set(source_by_id):
            raise ValueError(
                "Wave 8 Argentine-independence identity names an unknown source"
            )

    used_entity_ids: set[str] = set()
    for candidate_id, contract in WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(
                "Wave 8 Argentine-independence promotion hash table drifted"
            )
        if (
            contract["result_type"] != "win"
            or int(contract["winner_side"]) != 1
            or contract["source_outcome_override"]
        ):
            raise ValueError(
                "Wave 8 Argentine-independence promotion outcome changed"
            )
        if contract["actor_override"] is not True:
            raise ValueError(
                "Wave 8 Argentine-independence actor correction is not explicit"
            )

        exact_date = str(contract["exact_date"])
        canonical = contract["canonical_event"]
        if int(exact_date[:4]) != int(canonical["year_low"]):
            raise ValueError(
                "Wave 8 Argentine-independence exact date and queue year diverge"
            )
        if not contract["reservations"] or any(
            not str(item).strip() for item in contract["reservations"]
        ):
            raise ValueError(
                "Wave 8 Argentine-independence promotion lacks reservations"
            )

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        side_ids = [*side_1, *side_2]
        if not side_1 or not side_2 or len(side_ids) != len(set(side_ids)):
            raise ValueError("Wave 8 Argentine-independence sides overlap")
        used_entity_ids.update(side_ids)
        for entity_id in side_ids:
            entity = entity_by_id.get(entity_id)
            if entity is None:
                raise ValueError(
                    "Wave 8 Argentine-independence promotion uses an unknown identity"
                )
            if not (
                int(entity["start_year"])
                <= int(canonical["year_low"])
                <= int(entity["end_year"])
            ):
                raise ValueError(
                    "Wave 8 Argentine-independence identity window changed"
                )

        historical = contract["historical_review"]
        revolutionary_side = int(historical["revolutionary_side"])
        royalist_side = int(historical["royalist_side"])
        if {revolutionary_side, royalist_side} != {1, 2}:
            raise ValueError(
                "Wave 8 Argentine-independence actor-side review is invalid"
            )
        expected_winner_side = (
            revolutionary_side
            if historical["outcome"] == "revolutionary_victory"
            else royalist_side
        )
        if historical["outcome"] not in {
            "revolutionary_victory",
            "royalist_victory",
        } or expected_winner_side != int(contract["winner_side"]):
            raise ValueError(
                "Wave 8 Argentine-independence reviewed outcome is inconsistent"
            )

        evidence = list(map(str, contract["evidence_refs"]))
        outcome_sources = list(map(str, contract["outcome_source_ids"]))
        if evidence != sorted(set(evidence)) or outcome_sources != sorted(
            set(outcome_sources)
        ):
            raise ValueError(
                "Wave 8 Argentine-independence provenance is nondeterministic"
            )
        if not outcome_sources or not set(outcome_sources) <= set(evidence):
            raise ValueError(
                "Wave 8 Argentine-independence lacks direct outcome sources"
            )
        if not set(evidence) <= set(source_by_id):
            raise ValueError(
                "Wave 8 Argentine-independence names an unknown source"
            )
        for source_id in outcome_sources:
            if "outcome" not in source_by_id[source_id]["evidence_roles"]:
                raise ValueError(
                    "Wave 8 Argentine-independence outcome source lacks outcome role"
                )
        expected_families = sorted(
            {
                str(source_by_id[source_id]["source_family_id"])
                for source_id in outcome_sources
            }
        )
        if contract["outcome_source_family_ids"] != expected_families:
            raise ValueError(
                "Wave 8 Argentine-independence outcome families changed"
            )

        theatre = contract["war_label_review"]
        theatre_evidence = list(map(str, theatre["evidence_source_ids"]))
        if theatre_evidence != sorted(set(theatre_evidence)) or not set(
            theatre_evidence
        ) <= set(evidence):
            raise ValueError(
                "Wave 8 Argentine-independence theatre review lacks provenance"
            )
        if theatre["reviewed_cluster_id"] != _ARGENTINE_CLUSTER_ID:
            raise ValueError(
                "Wave 8 Argentine-independence reviewed cluster changed"
            )

    if used_entity_ids != set(entity_by_id):
        raise ValueError(
            "Wave 8 Argentine-independence contains an unused or missing identity"
        )

    cancha = WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS[
        "hced-Cancha Rayada1813-1"
    ]
    if cancha["raw_row_sha256"] != _ROW_HASHES["hced-Cancha Rayada1813-1"]:
        raise ValueError("Wave 8 Argentine-independence exclusion hash changed")
    if cancha["disposition"] != "terminal_exclusion" or cancha[
        "hold_category"
    ] != "misdated_reversed_chilean_event":
        raise ValueError("Wave 8 Argentine-independence exclusion changed")
    if (
        cancha["raw_queue_assertion"]["year"],
        cancha["reviewed_event"]["exact_date"],
        cancha["reviewed_event"]["outcome"],
    ) != (1813, "1814-03-29", "royalist_victory"):
        raise ValueError("Wave 8 Cancha Rayada adjudication changed")
    if cancha["war_label_review"]["reviewed_cluster_id"] != _CHILEAN_CLUSTER_ID:
        raise ValueError("Wave 8 Cancha Rayada theatre adjudication changed")
    exclusion_evidence = list(map(str, cancha["evidence_refs"]))
    if exclusion_evidence != sorted(set(exclusion_evidence)) or not set(
        exclusion_evidence
    ) <= set(source_by_id):
        raise ValueError("Wave 8 Cancha Rayada provenance changed")
    if not cancha["reservations"]:
        raise ValueError("Wave 8 Cancha Rayada reservations are incomplete")


def validate_wave8_argentine_independence_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS,
        WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS,
        lane_name=_LANE_NAME,
    )


def install_wave8_argentine_independence_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_ARGENTINE_INDEPENDENCE_SOURCES,
        lane_name=_LANE_NAME,
    )


def install_wave8_argentine_independence_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES,
        lane_name=_LANE_NAME,
    )


def _apply_reviewed_theatres(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reviewed_events: list[dict[str, Any]] = []
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        contract = WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS[candidate_id]
        theatre = contract["war_label_review"]
        expected_raw_cluster = str(theatre["expected_raw_cluster_id"])
        if event.get("cluster_id") != expected_raw_cluster:
            raise ValueError(
                f"{_LANE_NAME} raw theatre drift for {candidate_id}: "
                f"{event.get('cluster_id')} != {expected_raw_cluster}"
            )
        reviewed = copy.deepcopy(event)
        reviewed["cluster_id"] = str(theatre["reviewed_cluster_id"])
        reviewed["reviewed_exact_date"] = str(contract["exact_date"])
        reviewed["historical_review"] = copy.deepcopy(contract["historical_review"])
        reviewed["historical_theatre_review"] = copy.deepcopy(theatre)
        reviewed["reservations"] = copy.deepcopy(contract["reservations"])
        reviewed_events.append(reviewed)
    return reviewed_events


def promote_wave8_argentine_independence_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_argentine_independence_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix="hced_wave8_argentine_independence_",
    )
    return _apply_reviewed_theatres(events)


def wave8_argentine_independence_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS.values()
            ).items()
        )
    )


def wave8_argentine_independence_counts() -> dict[str, int]:
    return {
        "holds": len(WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS),
        "newly_rated_events": len(WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS),
        "promotion_contracts": len(WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_ARGENTINE_INDEPENDENCE_RESERVED_IDS),
        "terminal_exclusions": len(
            WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS
        ),
    }
