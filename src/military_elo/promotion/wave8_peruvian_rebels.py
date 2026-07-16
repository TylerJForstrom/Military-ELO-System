"""Exact Wave 8 audit for HCED's generic ``Peruvian Rebels`` cohort.

The six sole-blocker rows span three different independence-era formations and
one corrupt chronology.  This lane binds each promoted engagement to the
documented event- or campaign-bounded forces.  It deliberately creates no
timeless Peruvian-rebel identity and does not transfer a result to modern Peru.
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
    "WAVE8_PERUVIAN_REBELS_CONTRACT_IDS",
    "WAVE8_PERUVIAN_REBELS_CONTRACTS",
    "WAVE8_PERUVIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_PERUVIAN_REBELS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_PERUVIAN_REBELS_ENTITIES",
    "WAVE8_PERUVIAN_REBELS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_PERUVIAN_REBELS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_PERUVIAN_REBELS_HOLD_IDS",
    "WAVE8_PERUVIAN_REBELS_HOLDS",
    "WAVE8_PERUVIAN_REBELS_INTEGRATION_DISPOSITIONS",
    "WAVE8_PERUVIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_PERUVIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_PERUVIAN_REBELS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_PERUVIAN_REBELS_OUTCOME_OVERRIDES",
    "WAVE8_PERUVIAN_REBELS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_PERUVIAN_REBELS_RESERVED_IDS",
    "WAVE8_PERUVIAN_REBELS_SOURCES",
    "install_wave8_peruvian_rebels_entities",
    "install_wave8_peruvian_rebels_sources",
    "promote_wave8_peruvian_rebels_contracts",
    "validate_wave8_peruvian_rebels_integration_dispositions",
    "validate_wave8_peruvian_rebels_queue_contracts",
    "wave8_peruvian_rebels_audit_signature",
    "wave8_peruvian_rebels_cohort_counts",
    "wave8_peruvian_rebels_counts",
    "wave8_peruvian_rebels_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Peruvian rebel formations"
_EVENT_ID_PREFIX = "hced_wave8_peruvian_rebels_"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = True,
    chronology_conflict: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if chronology_conflict:
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


WAVE8_PERUVIAN_REBELS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_peruvian_rebels_pucp_cuzco_junta_1814",
        "1814: La junta de gobierno del Cuzco y el sur andino",
        "https://repositorio.pucp.edu.pe/items/1bacb037-de6a-4437-999d-e00bfc69b430",
        "Pontificia Universidad Catolica del Peru; IFEA",
        "open_access_scholarly_volume",
        "pucp_ifea_cuzco_junta_1814",
        outcome=False,
    ),
    _source(
        "wave8_peruvian_rebels_cehmp_apacheta",
        "Efemeride del 9 de noviembre de 1814: Batalla de Apacheta",
        (
            "https://cehmp.wordpress.com/2024/11/10/"
            "efemeride-del-9-de-noviembre-de-1814-batalla-de-apacheta/"
        ),
        "Centro de Estudios Historico Militares del Peru",
        "institutional_military_history",
        "peru_center_historical_military_apacheta",
    ),
    _source(
        "wave8_peruvian_rebels_bicentenario_cuzco_1814_readings",
        "Lecturas de la Independencia: la revolucion del Cuzco de 1814",
        (
            "https://bicentenario.gob.pe/biblioteca/storage/app/uploads/public/"
            "66c/663/064/66c6630642ffa238415020.pdf"
        ),
        "Proyecto Especial Bicentenario del Peru",
        "government_scholarly_compilation",
        "peru_bicentenario_cuzco_1814_readings",
    ),
    _source(
        "wave8_peruvian_rebels_garcia_camba_memorias",
        "Memorias para la historia de las armas espanolas en el Peru",
        "https://bvpb.mcu.es/es/consulta/registro.do?id=398125",
        "Biblioteca Virtual del Patrimonio Bibliografico, Ministry of Culture of Spain",
        "digitized_near_contemporary_military_account",
        "garcia_camba_peru_military_memories",
    ),
    _source(
        "wave8_peruvian_rebels_redalyc_puno_alto_peru",
        "Acciones revolucionarias en America Latina: Puno y el Alto Peru durante el proceso de independencia",
        "https://www.redalyc.org/journal/5717/571768450005/",
        "Revista Revoluciones / Redalyc",
        "peer_reviewed_historical_article",
        "puno_alto_peru_independence_article",
    ),
    _source(
        "wave8_peruvian_rebels_bicentenario_torata",
        "Bicentenario de las batallas de Torata y Moquegua: valor y sacrificio del Peru",
        "https://bicentenario.gob.pe/batallas-torata-moquegua-sacrificio/",
        "Proyecto Especial Bicentenario del Peru",
        "government_military_history",
        "peru_bicentenario_torata_moquegua",
    ),
    _source(
        "wave8_peruvian_rebels_municipality_torata_history",
        "Historia de Torata: batalla del 19 de enero de 1823",
        "https://anterior.munitorata.gob.pe/historia/",
        "Municipalidad Distrital de Torata",
        "municipal_history",
        "torata_municipal_history",
    ),
    _source(
        "wave8_peruvian_rebels_bicentenario_junin_part",
        "Victoria por la independencia: parte de la batalla de Junin",
        "https://bicentenario.gob.pe/parte-batalla-junin-1824/",
        "Proyecto Especial Bicentenario del Peru",
        "government_transcription_of_primary_battle_report",
        "peru_bicentenario_junin_primary_part",
    ),
    _source(
        "wave8_peruvian_rebels_peruvian_army_junin",
        "Homenaje a la gesta de Junin y Dia del Arma de Caballeria",
        (
            "https://www.gob.pe/institucion/ejercito/noticias/813715-"
            "homenaje-a-la-gesta-de-junin-y-dia-del-arma-de-caballeria"
        ),
        "Ejercito del Peru",
        "official_military_history",
        "peruvian_army_junin_history",
    ),
    _source(
        "wave8_peruvian_rebels_bicentenario_ayacucho",
        "La batalla de Ayacucho y su capitulacion",
        (
            "https://bicentenario.gob.pe/"
            "batalla-de-ayacucho-hito-en-la-consolidacion-de-la-independencia-americana/"
        ),
        "Proyecto Especial Bicentenario del Peru",
        "government_history",
        "peru_bicentenario_ayacucho_history",
    ),
    _source(
        "wave8_peruvian_rebels_agn_ayacucho_article",
        "La batalla de Ayacucho (9 de diciembre de 1824)",
        "https://revista.agn.gob.pe/ojs/index.php/ragn/article/view/18",
        "Archivo General de la Nacion del Peru",
        "scholarly_archival_article",
        "peru_agn_ayacucho_article",
    ),
    _source(
        "wave8_peruvian_rebels_bicentenario_ayacucho_primary",
        "Homenaje a la victoria de Ayacucho: battle report and capitulation",
        (
            "https://repositorio.bicentenario.gob.pe/bitstream/handle/"
            "20.500.12934/90/Homenaje%20victoria%20Ayacucho.pdf"
            "?isAllowed=y&sequence=3"
        ),
        "Repositorio Bicentenario del Peru",
        "digitized_primary_document_compilation",
        "ayacucho_primary_document_compilation",
    ),
    _source(
        "wave8_peruvian_rebels_culture_ministry_pasco_1820",
        "Proyecto Bicentenario conmemora los 200 anos de la Batalla de Pasco",
        (
            "https://www.gob.pe/institucion/cultura/noticias/319423-"
            "proyecto-bicentenario-conmemora-los-200-anos-de-la-batalla-de-pasco-"
            "este-6-de-diciembre"
        ),
        "Ministerio de Cultura del Peru",
        "government_chronology",
        "peru_ministry_culture_pasco_1820",
        outcome=False,
        chronology_conflict=True,
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
            + " No rating is inherited by modern Peru, modern Spain, a generic "
            "rebel or royalist label, any constituent nationality, or a later force."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_PERUVIAN_REBELS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "pumacahua_angulo_cuzco_junta_army_apacheta_1814",
        "Pumacahua and Angulo's Cuzco Junta army at Apacheta (1814)",
        "event_bounded_revolutionary_army",
        1814,
        "Southern Andes",
        [
            "wave8_peruvian_rebels_bicentenario_cuzco_1814_readings",
            "wave8_peruvian_rebels_cehmp_apacheta",
            "wave8_peruvian_rebels_pucp_cuzco_junta_1814",
        ],
        "Engagement-bounded force led by Mateo Pumacahua and Vicente Angulo at Apacheta.",
    ),
    _entity(
        "picoaga_moscoso_arequipa_royalist_force_apacheta_1814",
        "Picoaga and Moscoso's Arequipa royalist force at Apacheta (1814)",
        "event_bounded_royalist_force",
        1814,
        "Southern Andes",
        [
            "wave8_peruvian_rebels_bicentenario_cuzco_1814_readings",
            "wave8_peruvian_rebels_cehmp_apacheta",
        ],
        "Engagement-bounded Arequipa defense organized by Francisco Picoaga and Jose Gabriel Moscoso.",
    ),
    _entity(
        "ramirez_royalist_division_chacaltaya_1814",
        "Juan Ramirez Orozco's royalist division at Chacaltaya (1814)",
        "event_bounded_royalist_division",
        1814,
        "Upper Peru",
        [
            "wave8_peruvian_rebels_garcia_camba_memorias",
            "wave8_peruvian_rebels_redalyc_puno_alto_peru",
        ],
        "Engagement-bounded royalist division sent from the Army of Upper Peru under Juan Ramirez Orozco.",
    ),
    _entity(
        "pinedo_munecas_cuzco_expedition_chacaltaya_1814",
        "Pinedo and Munecas's Cuzco expedition at Chacaltaya (1814)",
        "event_bounded_revolutionary_expedition",
        1814,
        "Upper Peru",
        [
            "wave8_peruvian_rebels_garcia_camba_memorias",
            "wave8_peruvian_rebels_pucp_cuzco_junta_1814",
            "wave8_peruvian_rebels_redalyc_puno_alto_peru",
        ],
        "Engagement-bounded Cuzco Junta expedition led by Jose Manuel Pinedo and Ildefonso de las Munecas.",
    ),
    _entity(
        "valdes_royalist_southern_division_torata_1823",
        "Geronimo Valdes's southern royalist division at Torata (1823)",
        "event_bounded_royalist_division",
        1823,
        "Southern Peru",
        [
            "wave8_peruvian_rebels_bicentenario_torata",
            "wave8_peruvian_rebels_municipality_torata_history",
        ],
        "Engagement-bounded southern royalist formation commanded by Geronimo Valdes at Torata.",
    ),
    _entity(
        "alvarado_liberating_army_south_torata_1823",
        "Rudecindo Alvarado's Liberating Army of the South at Torata (1823)",
        "event_bounded_multinational_army",
        1823,
        "Southern Peru",
        [
            "wave8_peruvian_rebels_bicentenario_torata",
            "wave8_peruvian_rebels_municipality_torata_history",
        ],
        "Engagement-bounded Peruvian, Rioplatense, and Chilean army under Rudecindo Alvarado.",
    ),
    _entity(
        "united_liberating_army_peru_campaign_1824",
        "United Liberating Army of Peru (1824 campaign)",
        "campaign_bounded_multinational_army",
        1824,
        "Central and Southern Peru",
        [
            "wave8_peruvian_rebels_agn_ayacucho_article",
            "wave8_peruvian_rebels_bicentenario_ayacucho",
            "wave8_peruvian_rebels_bicentenario_ayacucho_primary",
            "wave8_peruvian_rebels_bicentenario_junin_part",
            "wave8_peruvian_rebels_peruvian_army_junin",
        ],
        "Campaign-bounded combined liberating army employed at Junin and Ayacucho in 1824.",
    ),
    _entity(
        "royal_army_peru_campaign_1824",
        "Royal Army of Peru (1824 campaign)",
        "campaign_bounded_royalist_army",
        1824,
        "Central and Southern Peru",
        [
            "wave8_peruvian_rebels_agn_ayacucho_article",
            "wave8_peruvian_rebels_bicentenario_ayacucho",
            "wave8_peruvian_rebels_bicentenario_ayacucho_primary",
            "wave8_peruvian_rebels_bicentenario_junin_part",
        ],
        "Campaign-bounded army under Canterac and La Serna in the final 1824 campaign.",
    ),
)


_ROW_HASHES = {
    "hced-Apacheta1814-1": "a8040d287cdc6d8e0cbce4e42b955fe107283065e1c9df5e30fb10fb7c671c34",
    "hced-Ayacucho1824-1": "ab59ccac03d10e02bc3da67e5ed0ec62e2c31c7f5d46396187686a40dbe98a40",
    "hced-Cerro de Pasco1862-1": "673d6f8ef86f2bbee5b287cf21fb1424456ccf4e38dd933d736a9f03cfad0918",
    "hced-Chacaltaya1814-1": "5fa5575652d2b5bae5f0d9ed19221222a719190fc790441c5cdf47672d4be973",
    "hced-Junin1824-1": "cc4a8f202ff0b99c7795987924c48bf2ac2e68b6b407dddf62dfc37a1bdee556",
    "hced-Torata1823-1": "73c1b049b3f0161236452704eeb6605c396bbb6a02365f0e812eaecc8b530400",
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str = "day",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": "engagement",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: list[str],
    side_2_entity_ids: list[str],
    evidence_refs: list[str],
    outcome_source_ids: list[str],
    outcome_source_family_ids: list[str],
    audit_note: str,
    historical_review: dict[str, Any],
    *,
    confidence: float,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": side_1_entity_ids,
        "side_2_entity_ids": side_2_entity_ids,
        "result_type": "win",
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": sorted(evidence_refs),
        "outcome_source_ids": sorted(outcome_source_ids),
        "outcome_source_family_ids": sorted(outcome_source_family_ids),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "audit_note": audit_note,
        "historical_review": historical_review,
    }


WAVE8_PERUVIAN_REBELS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Apacheta1814-1": _contract(
        "hced-Apacheta1814-1",
        _canonical(
            "Battle of La Apacheta",
            1814,
            "9-10 November 1814 (source date variance)",
            date_precision="day_range",
        ),
        "cuzco_junta_rebellion_1814",
        ["pumacahua_angulo_cuzco_junta_army_apacheta_1814"],
        ["picoaga_moscoso_arequipa_royalist_force_apacheta_1814"],
        [
            "wave8_peruvian_rebels_bicentenario_cuzco_1814_readings",
            "wave8_peruvian_rebels_cehmp_apacheta",
            "wave8_peruvian_rebels_pucp_cuzco_junta_1814",
        ],
        [
            "wave8_peruvian_rebels_bicentenario_cuzco_1814_readings",
            "wave8_peruvian_rebels_cehmp_apacheta",
        ],
        [
            "peru_bicentenario_cuzco_1814_readings",
            "peru_center_historical_military_apacheta",
        ],
        (
            "Pumacahua and Vicente Angulo's Cuzco Junta force defeated the "
            "Arequipa royalist defense and occupied the city. The sources differ "
            "by one day, so the date is recorded as a narrow range. HCED's point "
            "is far from the documented Arequipa-area battlefield and is withheld."
        ),
        {
            "outcome": "cuzco_junta_victory",
            "revolutionary_commanders": ["Mateo Pumacahua", "Vicente Angulo"],
            "royalist_commanders": ["Francisco Picoaga", "Jose Gabriel Moscoso"],
        },
        confidence=0.90,
    ),
    "hced-Chacaltaya1814-1": _contract(
        "hced-Chacaltaya1814-1",
        _canonical("Battle of Chacaltaya (Achocalla)", 1814, "2 November 1814"),
        "cuzco_junta_rebellion_1814",
        ["ramirez_royalist_division_chacaltaya_1814"],
        ["pinedo_munecas_cuzco_expedition_chacaltaya_1814"],
        [
            "wave8_peruvian_rebels_garcia_camba_memorias",
            "wave8_peruvian_rebels_pucp_cuzco_junta_1814",
            "wave8_peruvian_rebels_redalyc_puno_alto_peru",
        ],
        [
            "wave8_peruvian_rebels_garcia_camba_memorias",
            "wave8_peruvian_rebels_redalyc_puno_alto_peru",
        ],
        [
            "garcia_camba_peru_military_memories",
            "puno_alto_peru_independence_article",
        ],
        (
            "Ramirez Orozco's royalist division defeated the Pinedo-Munecas "
            "expedition near Achocalla and recovered La Paz. The generic source "
            "labels are not bridged to Spain or Peru. The staged mountain point "
            "does not establish the battlefield and is withheld."
        ),
        {
            "outcome": "royalist_victory",
            "revolutionary_commanders": ["Jose Manuel Pinedo", "Ildefonso de las Munecas"],
            "royalist_commander": "Juan Ramirez Orozco",
        },
        confidence=0.93,
    ),
    "hced-Torata1823-1": _contract(
        "hced-Torata1823-1",
        _canonical("Battle of Torata", 1823, "19 January 1823"),
        "first_intermediate_ports_campaign_1822_1823",
        ["valdes_royalist_southern_division_torata_1823"],
        ["alvarado_liberating_army_south_torata_1823"],
        [
            "wave8_peruvian_rebels_bicentenario_torata",
            "wave8_peruvian_rebels_municipality_torata_history",
        ],
        [
            "wave8_peruvian_rebels_bicentenario_torata",
            "wave8_peruvian_rebels_municipality_torata_history",
        ],
        ["peru_bicentenario_torata_moquegua", "torata_municipal_history"],
        (
            "Valdes's southern royalist force held the heights and defeated "
            "Alvarado's multinational Liberating Army of the South on 19 January. "
            "The town-centroid coordinate is not asserted as a precise battlefield."
        ),
        {
            "outcome": "royalist_victory",
            "revolutionary_commander": "Rudecindo Alvarado",
            "royalist_commander": "Geronimo Valdes",
        },
        confidence=0.95,
    ),
    "hced-Junin1824-1": _contract(
        "hced-Junin1824-1",
        _canonical("Battle of Junin", 1824, "6 August 1824"),
        "final_peru_campaign_1824",
        ["united_liberating_army_peru_campaign_1824"],
        ["royal_army_peru_campaign_1824"],
        [
            "wave8_peruvian_rebels_bicentenario_junin_part",
            "wave8_peruvian_rebels_peruvian_army_junin",
        ],
        [
            "wave8_peruvian_rebels_bicentenario_junin_part",
            "wave8_peruvian_rebels_peruvian_army_junin",
        ],
        ["peru_bicentenario_junin_primary_part", "peruvian_army_junin_history"],
        (
            "The United Liberating Army's cavalry defeated Canterac's Royal Army "
            "cavalry on 6 August. The multinational campaign army receives one "
            "result; its national components do not each receive a full inferred "
            "win. HCED's Junin town point is outside Chacamarca and is withheld."
        ),
        {
            "outcome": "united_liberating_army_victory",
            "liberating_command": ["Simon Bolivar", "Mariano Necochea", "Andres de Santa Cruz"],
            "royalist_commander": "Jose de Canterac",
        },
        confidence=0.97,
    ),
    "hced-Ayacucho1824-1": _contract(
        "hced-Ayacucho1824-1",
        _canonical("Battle of Ayacucho", 1824, "9 December 1824"),
        "final_peru_campaign_1824",
        ["united_liberating_army_peru_campaign_1824"],
        ["royal_army_peru_campaign_1824"],
        [
            "wave8_peruvian_rebels_agn_ayacucho_article",
            "wave8_peruvian_rebels_bicentenario_ayacucho",
            "wave8_peruvian_rebels_bicentenario_ayacucho_primary",
        ],
        [
            "wave8_peruvian_rebels_agn_ayacucho_article",
            "wave8_peruvian_rebels_bicentenario_ayacucho",
            "wave8_peruvian_rebels_bicentenario_ayacucho_primary",
        ],
        [
            "ayacucho_primary_document_compilation",
            "peru_agn_ayacucho_article",
            "peru_bicentenario_ayacucho_history",
        ],
        (
            "Sucre's United Liberating Army defeated the Royal Army of Peru and "
            "secured its capitulation on 9 December. The coalition is retained as "
            "one campaign actor rather than distributing a full win to modern "
            "states. HCED's Ayacucho-city coordinate is not the Quinua battlefield."
        ),
        {
            "outcome": "united_liberating_army_victory",
            "liberating_commander": "Antonio Jose de Sucre",
            "royalist_commanders": ["Jose de la Serna", "Jose de Canterac"],
        },
        confidence=0.98,
    ),
}


WAVE8_PERUVIAN_REBELS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Cerro de Pasco1862-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Cerro de Pasco1862-1"],
        "cohort": "corrupt_source_chronology",
        "hold_category": "source_year_conflicts_with_documented_event",
        "source_assertion": {
            "name": "Cerro de Pasco",
            "year_low": 1862,
            "year_high": 1862,
            "winner_raw": "Peruvian Rebels",
            "loser_raw": "Spain",
        },
        "documented_event": {
            "name": "Battle of Pasco",
            "date": "6 December 1820",
            "winner": "Alvarez de Arenales's patriot division",
            "loser": "Diego O'Reilly's royalist force",
        },
        "evidence_refs": ["wave8_peruvian_rebels_culture_ministry_pasco_1820"],
        "hold_reason": (
            "The Ministry of Culture dates the Cerro de Pasco battle to 6 December "
            "1820 and identifies Arenales's victory over O'Reilly. No authoritative "
            "source supports a separate 1862 Peruvian-rebel battle against Spain at "
            "Cerro de Pasco. The row is terminally excluded without silently moving "
            "it forty-two years, inventing an 1862 actor, or converting uncertainty "
            "into a draw."
        ),
    }
}


WAVE8_PERUVIAN_REBELS_CONTRACT_IDS = frozenset(WAVE8_PERUVIAN_REBELS_CONTRACTS)
WAVE8_PERUVIAN_REBELS_HOLD_IDS = frozenset(WAVE8_PERUVIAN_REBELS_HOLDS)
WAVE8_PERUVIAN_REBELS_RESERVED_IDS = (
    WAVE8_PERUVIAN_REBELS_CONTRACT_IDS | WAVE8_PERUVIAN_REBELS_HOLD_IDS
)
WAVE8_PERUVIAN_REBELS_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


# Every promoted row carries a settlement, city, mountain, or municipality
# point rather than a reviewed battlefield point.  Countries are accurate and
# retained; exact coordinates are withheld rather than corrected.
WAVE8_PERUVIAN_REBELS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_PERUVIAN_REBELS_CONTRACT_IDS
)
WAVE8_PERUVIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_PERUVIAN_REBELS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_PERUVIAN_REBELS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_PERUVIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_PERUVIAN_REBELS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_PERUVIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_PERUVIAN_REBELS_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_PERUVIAN_REBELS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {}


# No exact or plausible IWBD twin exists in the locked snapshot.  These aliases
# make the negative audit fail closed if a future snapshot adds one.
WAVE8_PERUVIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, tuple[str, ...]] = {
    "1814": (
        "apacheta",
        "battle of apacheta",
        "battle of chacaltaya",
        "chacaltaya",
        "achocalla",
        "battle of achocalla",
    ),
    "1823": ("battle of torata", "torata"),
    "1824": ("ayacucho", "battle of ayacucho", "battle of junin", "junin"),
    "1862": ("battle of cerro de pasco", "cerro de pasco"),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_PERUVIAN_REBELS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_PERUVIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_PERUVIAN_REBELS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_PERUVIAN_REBELS_ENTITIES,
        "expected_candidate_ids": sorted(
            WAVE8_PERUVIAN_REBELS_EXPECTED_CANDIDATE_IDS
        ),
        "holds": WAVE8_PERUVIAN_REBELS_HOLDS,
        "integration_dispositions": WAVE8_PERUVIAN_REBELS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_PERUVIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_PERUVIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT,
        "outcome_overrides": WAVE8_PERUVIAN_REBELS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_PERUVIAN_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_PERUVIAN_REBELS_SOURCES,
    }


def wave8_peruvian_rebels_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_PERUVIAN_REBELS_FINAL_AUDIT_SIGNATURE = (
    "9559371dcf6666273aaa65c8e871c5ff6bcb1118e8321cd3b40747b97ab94cd0"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_PERUVIAN_REBELS_CONTRACTS), len(WAVE8_PERUVIAN_REBELS_HOLDS)) != (
        5,
        1,
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_PERUVIAN_REBELS_ENTITIES), len(WAVE8_PERUVIAN_REBELS_SOURCES)) != (
        8,
        13,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_PERUVIAN_REBELS_RESERVED_IDS != WAVE8_PERUVIAN_REBELS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_PERUVIAN_REBELS_CONTRACT_IDS & WAVE8_PERUVIAN_REBELS_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotions and holds overlap")
    if wave8_peruvian_rebels_audit_signature() != WAVE8_PERUVIAN_REBELS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_PERUVIAN_REBELS_SOURCES
    }
    if len(source_by_id) != len(WAVE8_PERUVIAN_REBELS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_PERUVIAN_REBELS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_PERUVIAN_REBELS_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_PERUVIAN_REBELS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    for entity in WAVE8_PERUVIAN_REBELS_ENTITIES:
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} identity is not tightly bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if normalize_label(entity["name"]) in {
            "peru",
            "peruvian rebels",
            "spain",
            "spanish empire",
        }:
            raise ValueError(f"{_LANE_NAME} created a generic identity")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_PERUVIAN_REBELS_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["year_low"] != canonical["year_high"]:
            raise ValueError(f"{_LANE_NAME} widened an HCED year")
        if canonical["granularity"] != "engagement":
            raise ValueError(f"{_LANE_NAME} promoted a non-engagement")

        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (side_1 | side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        used_entities.update(side_1 | side_2)
        year = int(canonical["year_low"])
        for entity_id in side_1 | side_2:
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")

        if contract["result_type"] != "win" or contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} invented a draw or unknown result")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} contains an undeclared outcome override")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if not outcomes or not _is_sorted_unique(outcomes) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")
    used_sources.update(
        source_id
        for entity in WAVE8_PERUVIAN_REBELS_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    for hold in WAVE8_PERUVIAN_REBELS_HOLDS.values():
        used_sources.update(map(str, hold["evidence_refs"]))
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    hold = WAVE8_PERUVIAN_REBELS_HOLDS["hced-Cerro de Pasco1862-1"]
    if hold["raw_row_sha256"] != _ROW_HASHES["hced-Cerro de Pasco1862-1"]:
        raise ValueError(f"{_LANE_NAME} hold hash drifted")
    if hold["source_assertion"]["year_low"] != 1862 or hold["documented_event"]["date"] != "6 December 1820":
        raise ValueError(f"{_LANE_NAME} chronology hold drifted")
    if any(key in hold for key in ("winner_side", "result_type")):
        raise ValueError(f"{_LANE_NAME} hold invents a rated result")

    if WAVE8_PERUVIAN_REBELS_POINT_QUARANTINE_ADDITIONS != WAVE8_PERUVIAN_REBELS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_PERUVIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country quarantine contract changed")
    if (
        WAVE8_PERUVIAN_REBELS_OUTCOME_OVERRIDES
        or WAVE8_PERUVIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_PERUVIAN_REBELS_CROSS_LANE_DISPOSITIONS
        or WAVE8_PERUVIAN_REBELS_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty integration inventories changed")


def validate_wave8_peruvian_rebels_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_PERUVIAN_REBELS_CONTRACTS,
        WAVE8_PERUVIAN_REBELS_HOLDS,
        lane_name=_LANE_NAME,
    )


def _iwbd_year(row: Mapping[str, Any]) -> int | None:
    for field in ("start_date", "end_date"):
        value = row.get(field)
        if isinstance(value, str) and len(value) >= 4 and value[:4].lstrip("-").isdigit():
            try:
                return int(value[:4])
            except ValueError:
                pass
    value = row.get("year")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def validate_wave8_peruvian_rebels_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin the HCED inventory and fail on a future probable IWBD twin."""

    validate_wave8_peruvian_rebels_queue_contracts(hced_rows)
    audited = {
        (int(year), normalize_label(name))
        for year, names in WAVE8_PERUVIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT.items()
        for name in names
    }
    collisions = []
    for row in iwbd_rows:
        year = _iwbd_year(row)
        name = normalize_label(row.get("name"))
        if year is not None and (year, name) in audited:
            collisions.append(str(row.get("candidate_id") or "<missing-id>"))
    if collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): {sorted(collisions)}"
        )
    return {
        "cross_lane_hced_dispositions": 0,
        "integration_dispositions": 0,
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_peruvian_rebels_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_PERUVIAN_REBELS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_peruvian_rebels_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_PERUVIAN_REBELS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_PERUVIAN_REBELS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_PERUVIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_peruvian_rebels_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_peruvian_rebels_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_PERUVIAN_REBELS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_peruvian_rebels_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_PERUVIAN_REBELS_CONTRACTS.values(),
                    *WAVE8_PERUVIAN_REBELS_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_peruvian_rebels_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_PERUVIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_PERUVIAN_REBELS_CROSS_LANE_DISPOSITIONS
        ),
        "holds": len(WAVE8_PERUVIAN_REBELS_HOLDS),
        "integration_dispositions": len(
            WAVE8_PERUVIAN_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_PERUVIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_PERUVIAN_REBELS_ENTITIES),
        "new_sources": len(WAVE8_PERUVIAN_REBELS_SOURCES),
        "newly_rated_events": len(WAVE8_PERUVIAN_REBELS_CONTRACTS),
        "outcome_overrides": len(WAVE8_PERUVIAN_REBELS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_PERUVIAN_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_PERUVIAN_REBELS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_PERUVIAN_REBELS_RESERVED_IDS),
    }


def wave8_peruvian_rebels_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_PERUVIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_PERUVIAN_REBELS_POINT_QUARANTINE_ADDITIONS,
    }
