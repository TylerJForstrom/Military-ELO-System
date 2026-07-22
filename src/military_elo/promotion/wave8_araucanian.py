"""Fail-closed Wave 8 audit for HCED's Araucanian/Mapuche routing labels.

The raw labels are not polity identities and never become aliases.  Four
source-audited sixteenth-century engagements are promoted with eight
event-bounded formations.  Tapalque remains held because its date and mixed
force composition are unresolved; Apeleg is terminally excluded as a
noncompetitive attack on a family camp.

Wikidata, Brecke, IWBD, IWD, generic Wikidata, and Cliopatria records are
discovery or duplicate evidence only.  Discovery never originates a rating,
and an unknown outcome is never converted to a draw.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    expected_exact_hced_win_participants,
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_ARAUCANIAN_AUDITED_RECORD_ID_SHA256",
    "WAVE8_ARAUCANIAN_AUDITED_RECORD_IDS",
    "WAVE8_ARAUCANIAN_BRECKE_DISPOSITIONS",
    "WAVE8_ARAUCANIAN_CONTRACT_IDS",
    "WAVE8_ARAUCANIAN_CONTRACTS",
    "WAVE8_ARAUCANIAN_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ARAUCANIAN_ENTITIES",
    "WAVE8_ARAUCANIAN_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ARAUCANIAN_FUNNEL_AUDIT",
    "WAVE8_ARAUCANIAN_HCED_HOMONYM_DISPOSITIONS",
    "WAVE8_ARAUCANIAN_HOLDS",
    "WAVE8_ARAUCANIAN_HOLD_IDS",
    "WAVE8_ARAUCANIAN_INPUT_SHA256",
    "WAVE8_ARAUCANIAN_IWBD_DISPOSITIONS",
    "WAVE8_ARAUCANIAN_LOCATION_QUARANTINE_REASONS",
    "WAVE8_ARAUCANIAN_NONPROMOTIONS",
    "WAVE8_ARAUCANIAN_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ARAUCANIAN_RESERVED_IDS",
    "WAVE8_ARAUCANIAN_ROW_HASHES",
    "WAVE8_ARAUCANIAN_SOURCE_ROW_SEMANTICS",
    "WAVE8_ARAUCANIAN_SOURCES",
    "WAVE8_ARAUCANIAN_TERMINAL_EXCLUSIONS",
    "WAVE8_ARAUCANIAN_TERMINAL_EXCLUSION_IDS",
    "WAVE8_ARAUCANIAN_WIKIDATA_DISPOSITIONS",
    "WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED",
    "WAVE8_ARAUCANIAN_WIKIDATA_ROW_HASHES",
    "install_wave8_araucanian_entities",
    "install_wave8_araucanian_sources",
    "promote_wave8_araucanian_contracts",
    "validate_wave8_araucanian_cross_source_inventory",
    "validate_wave8_araucanian_current_artifact_state",
    "validate_wave8_araucanian_discovery_dispositions",
    "validate_wave8_araucanian_emissions",
    "validate_wave8_araucanian_funnel",
    "validate_wave8_araucanian_queue_contracts",
    "wave8_araucanian_audit_signature",
    "wave8_araucanian_cohort_counts",
    "wave8_araucanian_counts",
    "wave8_araucanian_location_quarantine_additions",
    "wave8_araucanian_metadata",
)


_LANE_NAME = "Wave 8 exact Araucanian and Mapuche label audit"
_MODULE_OWNER = "military_elo.promotion.wave8_araucanian"
_EVENT_ID_PREFIX = "hced_wave8_araucanian_"
_OWNED_LABELS = frozenset(
    {"araucanian indians", "araucanians", "araucania", "mapuche", "mapuche rebels"}
)

_TUCAPEL_ALLIANCE = "lautaro_tucapel_lineage_alliance_1553_1554"
_VALDIVIA_TUCAPEL_COLUMN = "valdivia_tucapel_column_1553_1554"
_MARIGUENU_FORCE = "lautaro_mariguenu_force_1554"
_VILLAGRA_MARIGUENU_COLUMN = "villagra_mariguenu_column_1554"
_MATAQUITO_ASSAULT = "villagra_godinez_mataquito_assault_force_1557"
_MATAQUITO_DEFENDERS = "lautaro_mataquito_fort_force_1557"
_CURALABA_STRIKE = "pelantaro_curalaba_strike_force_1598"
_CURALABA_COLUMN = "onez_de_loyola_curalaba_column_1598"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = True,
) -> dict[str, Any]:
    roles = {"identity_boundary_or_context_reference"}
    if outcome:
        roles.add("outcome")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-21",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_ARAUCANIAN_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_araucanian_memoria_lautaro",
        "Lautaro (ca. 1534-1557)",
        "https://www.memoriachilena.gob.cl/602/w3-article-721.html",
        "Biblioteca Nacional de Chile / Memoria Chilena",
        "national_library_scholarly_mini_site",
        "memoria_chilena_lautaro_minisite",
    ),
    _source(
        "wave8_araucanian_memoria_tucapel",
        "Batalla de Tucapel",
        "https://www.memoriachilena.gob.cl/602/w3-article-95492.html",
        "Biblioteca Nacional de Chile / Memoria Chilena",
        "national_library_scholarly_mini_site",
        "memoria_chilena_lautaro_minisite",
    ),
    _source(
        "wave8_araucanian_memoria_mariguenu",
        "Batalla de Mariguen",
        "https://www.memoriachilena.gob.cl/602/w3-article-95491.html",
        "Biblioteca Nacional de Chile / Memoria Chilena",
        "national_library_scholarly_mini_site",
        "memoria_chilena_lautaro_minisite",
    ),
    _source(
        "wave8_araucanian_clement_mariguenu",
        "The Recruitment of Colonial Troops in Chile, 1550-1650",
        "https://journals.sagepub.com/doi/10.1177/0968344514523000",
        "War in History / SAGE",
        "peer_reviewed_history_article",
        "clement_war_in_history_2015",
    ),
    _source(
        "wave8_araucanian_gongora_marmolejo",
        "Historia de Chile desde su descubrimiento hasta el ano 1575",
        "https://www.cervantesvirtual.com/obra/historia-de-chile-desde-su-descubrimiento-hasta-el-ano-1575--0/",
        "Biblioteca Virtual Miguel de Cervantes",
        "primary_chronicle_in_scholarly_digital_edition",
        "gongora_marmolejo_1575",
    ),
    _source(
        "wave8_araucanian_marino_lobera_mataquito",
        "Cronica del Reino de Chile, chapter LV",
        "https://www.cervantesvirtual.com/obra-visor/cronica-del-reino-de-chile--0/html/feec70e8-82b1-11df-acc7-002185ce6064_2.html",
        "Biblioteca Virtual Miguel de Cervantes",
        "primary_chronicle_in_scholarly_digital_edition",
        "marino_de_lobera_cronica",
    ),
    _source(
        "wave8_araucanian_barros_arana_t2",
        "Historia General de Chile, tomo segundo",
        "https://www.cervantesvirtual.com/obra-visor/historia-general-de-chile-tomo-segundo--0/html/ff2db864-82b1-11df-acc7-002185ce6064_60.html",
        "Biblioteca Virtual Miguel de Cervantes",
        "scholarly_history_monograph_digital_edition",
        "barros_arana_historia_general_t2",
    ),
    _source(
        "wave8_araucanian_barros_arana_tucapel",
        "Combate de Tucapel y muerte de Pedro de Valdivia",
        "https://www.academiahistoriamilitar.cl/academia/wp-content/uploads/2021/12/COMBATE-DE-TUCAPEL-Y-MUERTE-DE-PEDRO-DE-VALDIVIA.pdf",
        "Academia de Historia Militar de Chile",
        "institutional_extract_of_scholarly_history",
        "barros_arana_historia_general_t1",
    ),
    _source(
        "wave8_araucanian_goicovich_curalaba",
        "La etapa de la conquista (1536-1598): origen y desarrollo del Estado indomito",
        "https://www.scielo.cl/scielo.php?pid=S0717-71942006000100004&script=sci_arttext",
        "Historia, Pontificia Universidad Catolica de Chile / SciELO",
        "peer_reviewed_history_article",
        "goicovich_historia_2006",
    ),
    _source(
        "wave8_araucanian_ahm_chile_t1",
        "Historia Militar de Chile, tomo I",
        "https://www.academiahistoriamilitar.cl/academia/wp-content/uploads/2022/03/TOMO-I-Historia_digital.pdf",
        "Academia de Historia Militar de Chile",
        "official_institutional_military_history",
        "academia_historia_militar_chile_t1",
    ),
    _source(
        "wave8_araucanian_barcos_lanteri_tapalque",
        "Fronteras, poder estatal y relaciones interetnicas en Buenos Aires",
        "https://www.anuarioiha.fahce.unlp.edu.ar/article/download/IHAe066/9637?inline=1",
        "Anuario del Instituto de Historia Argentina",
        "peer_reviewed_history_article",
        "barcos_lanteri_anuario_iha_2018",
    ),
    _source(
        "wave8_araucanian_bagaloni_pedrotta_san_jacinto",
        "Historical archaeology of the Battle of San Jacinto",
        "https://ri.conicet.gov.ar/bitstream/handle/11336/177034/CONICET_Digital_Nro.d91b4e41-c98b-4e7d-93ce-ecdc7dea68d5_B.pdf?isAllowed=y&sequence=2",
        "CONICET institutional repository",
        "peer_reviewed_historical_archaeology_article",
        "bagaloni_pedrotta_hist_arch_2018",
    ),
    _source(
        "wave8_araucanian_delrio_lenton_apeleg",
        "Discussing Indigenous Genocide in Argentina",
        "https://ri.conicet.gov.ar/bitstream/11336/58381/2/CONICET_Digital_Nro.29c0c222-f3de-4205-8bde-5b4fa32a0c11_A.pdf",
        "Genocide Studies and Prevention / CONICET repository",
        "peer_reviewed_genocide_studies_article",
        "delrio_lenton_et_al_gsp_2010",
    ),
    _source(
        "wave8_araucanian_archivo_nombre_apeleg",
        "El archivo y el nombre: genocidio, memorias y resistencias",
        "https://saantropologia.com.ar/wp-content/uploads/2023/11/El-archivo-y-el-nombre-FINAL-IMPRENTA.pdf",
        "Sociedad Argentina de Antropologia",
        "scholarly_anthropology_collection",
        "sociedad_argentina_antropologia_archivo_nombre",
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_ARAUCANIAN_SOURCES}

_TUCAPEL_SOURCES = (
    "wave8_araucanian_barros_arana_tucapel",
    "wave8_araucanian_gongora_marmolejo",
    "wave8_araucanian_memoria_lautaro",
    "wave8_araucanian_memoria_tucapel",
)
_MARIGUENU_SOURCES = (
    "wave8_araucanian_clement_mariguenu",
    "wave8_araucanian_gongora_marmolejo",
    "wave8_araucanian_memoria_lautaro",
    "wave8_araucanian_memoria_mariguenu",
)
_MATAQUITO_SOURCES = (
    "wave8_araucanian_barros_arana_t2",
    "wave8_araucanian_marino_lobera_mataquito",
    "wave8_araucanian_memoria_lautaro",
)
_CURALABA_SOURCES = (
    "wave8_araucanian_ahm_chile_t1",
    "wave8_araucanian_goicovich_curalaba",
    "wave8_araucanian_gongora_marmolejo",
)
_TAPALQUE_SOURCES = (
    "wave8_araucanian_bagaloni_pedrotta_san_jacinto",
    "wave8_araucanian_barcos_lanteri_tapalque",
)
_APELEG_SOURCES = (
    "wave8_araucanian_archivo_nombre_apeleg",
    "wave8_araucanian_delrio_lenton_apeleg",
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    source_ids: Iterable[str],
    boundary: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start_year,
        "end_year": end_year,
        "region": "south-central Chile",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary
            + " It has no ethnic, imperial, national, predecessor, successor, "
            "or cross-event alias and inherits no Elo."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_ARAUCANIAN_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _TUCAPEL_ALLIANCE,
        "Lautaro's lineage alliance at Tucapel (1553-1554 date envelope)",
        "event_bounded_lineage_alliance",
        1553,
        1554,
        _TUCAPEL_SOURCES,
        "Bounded to the force fighting Valdivia at the ruins of Fort Tucapel.",
    ),
    _entity(
        _VALDIVIA_TUCAPEL_COLUMN,
        "Valdivia's combined Tucapel column (1553-1554 date envelope)",
        "event_bounded_combined_column",
        1553,
        1554,
        _TUCAPEL_SOURCES,
        "Bounded to Valdivia's cavalry and source-attested Indigenous auxiliaries at Tucapel.",
    ),
    _entity(
        _MARIGUENU_FORCE,
        "Lautaro's Mariguenu battle force (1554)",
        "event_bounded_battle_force",
        1554,
        1554,
        _MARIGUENU_SOURCES,
        "Bounded to Lautaro's force in the February 1554 field battle.",
    ),
    _entity(
        _VILLAGRA_MARIGUENU_COLUMN,
        "Villagra's combined Mariguenu column (1554)",
        "event_bounded_combined_column",
        1554,
        1554,
        _MARIGUENU_SOURCES,
        "Bounded to Villagra's Spanish-led column and Indigenous auxiliaries at Mariguenu.",
    ),
    _entity(
        _MATAQUITO_ASSAULT,
        "Villagra and Godinez's combined Mataquito assault force (1557)",
        "event_bounded_combined_assault_force",
        1557,
        1557,
        _MATAQUITO_SOURCES,
        "Bounded to the Spanish-led and Indigenous-auxiliary assault on the fortified camp.",
    ),
    _entity(
        _MATAQUITO_DEFENDERS,
        "Lautaro's armed Mataquito fort defenders (1557)",
        "event_bounded_fortified_camp_force",
        1557,
        1557,
        _MATAQUITO_SOURCES,
        "Bounded only to armed defenders who fought in Lautaro's fortified camp.",
    ),
    _entity(
        _CURALABA_STRIKE,
        "Pelantaro's Curalaba strike force (1598)",
        "event_bounded_strike_force",
        1598,
        1598,
        _CURALABA_SOURCES,
        "Bounded to the force attacking the governor's camp on 23 December 1598.",
    ),
    _entity(
        _CURALABA_COLUMN,
        "Onez de Loyola's combined Curalaba column (1598)",
        "event_bounded_combined_column",
        1598,
        1598,
        _CURALABA_SOURCES,
        "Bounded to the governor's Spanish-led column and Indigenous allies at Curalaba.",
    ),
)

_ENTITY_BY_ID = {str(entity["id"]): entity for entity in WAVE8_ARAUCANIAN_ENTITIES}


WAVE8_ARAUCANIAN_INPUT_SHA256: dict[str, str] = {
    "brecke": "1868097be6c9015715b4dd210d5168e3a961bf8870f6081396fabae319c269dc",
    "cliopatria": "905b2d570bb5423d2576016f016b8c31850f9517fc55e58d63b831ad7ba2f289",
    "hced": "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf",
    "iwbd": "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7",
    "iwd": "0867947dadfb29e93a4697efa308fcf1acd78f90c90f8d860d344ac12dd883fd",
    "wikidata_battles": "5f67b193c58fe06947f965283c534d53a43d8ad8644a15995af39c6d6f55f22b",
    "wikidata_generic": "9a57ed9dbf4e2c59ea6185c699f00bbea6d07f5c90d5356ce501da449e8d0dd4",
}

WAVE8_ARAUCANIAN_ROW_HASHES: dict[str, str] = {
    "hced-Apeleg1883-1": "c867b980545a9d55cbd6e59a8c0ff4fd2c55173a3b6605248a350b59f06f813a",
    "hced-Curalaba1598-1": "4f2a6182a3b852fe522c50c42adb90fd95a597fc7d315f2386b98ead3d9a11b2",
    "hced-Mariguenu1554-1": "492867e8d45b65093a56b67f4945874dc9cf77fe7f9761bc02f0bfa5a7960987",
    "hced-Mataquito1557-1": "0d17ddd98cac396ca2b4f9e35c6819353c31ef1fe328da559b7e5608b5b41f2e",
    "hced-San Jacinto1899-1": "a961d4ca62b9b0abb7d8c1c39ad39f130f459ad7a13202cabf1fb011e664b9c4",
    "hced-Tapalque Creek1856-1": "17c1617ec0bee3d05de5be312f42806071b50936932198bdc900e43036f8d852",
    "hced-Tucapel1553-1": "ead685da410d51f83fd16132049025bad1477a0c8342185ce4157d65c967c01b",
}

_SOURCE_SEMANTIC_FIELDS = (
    "candidate_id",
    "do_not_rate_automatically",
    "duplicate_source_id",
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
    "year_high",
    "year_low",
)


def _semantics(
    candidate_id: str,
    name: str,
    year: int,
    side_1: str,
    side_2: str,
    winner: str,
    loser: str,
    massacre: str,
    country: str,
    latitude: str,
    longitude: str,
    war_name: str,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "do_not_rate_automatically": True,
        "duplicate_source_id": False,
        "latitude": latitude,
        "longitude": longitude,
        "loser_raw": loser,
        "massacre_raw": massacre,
        "modern_location_country": country,
        "name": name,
        "side_1_raw": side_1,
        "side_2_raw": side_2,
        "war_names": [war_name],
        "winner_loser_complete": True,
        "winner_raw": winner,
        "year_best": year,
        "year_high": year,
        "year_low": year,
    }


WAVE8_ARAUCANIAN_SOURCE_ROW_SEMANTICS: dict[str, dict[str, Any]] = {
    "hced-Apeleg1883-1": _semantics(
        "hced-Apeleg1883-1", "Apeleg", 1883, "Argentina", "Mapuche Rebels",
        "Argentina", "Mapuche Rebels", "No", "Argentina", "-42.782379",
        "-65.0224295", "y War of the Desert",
    ),
    "hced-Curalaba1598-1": _semantics(
        "hced-Curalaba1598-1", "Curalaba", 1598, "Araucania", "Spain",
        "Araucania", "Spain", "No", "Chile", "-33.5351231", "-70.781171",
        "Spanish Conquest of Chile",
    ),
    "hced-Mariguenu1554-1": _semantics(
        "hced-Mariguenu1554-1", "Mariguenu", 1554, "Araucanian Indians", "Spain",
        "Araucanian Indians", "Spain", "Battle followed by massacre", "Chile",
        "-33.45273", "-70.677044", "Spanish Conquest of Chile",
    ),
    "hced-Mataquito1557-1": _semantics(
        "hced-Mataquito1557-1", "Mataquito", 1557, "Spain", "Araucanian Indians",
        "Spain", "Araucanian Indians", "No", "Chile", "-35.0495842",
        "-72.0629353", "Spanish Conquest of Chile",
    ),
    "hced-San Jacinto1899-1": _semantics(
        "hced-San Jacinto1899-1", "San Jacinto", 1899, "United States",
        "Filippino Rebels", "United States", "Filippino Rebels", "No",
        "Philippines", "16.0856441", "120.4174941", "Philippine-American War",
    ),
    "hced-Tapalque Creek1856-1": _semantics(
        "hced-Tapalque Creek1856-1", "Tapalque Creek", 1856, "Mapuche", "Argentina",
        "Mapuche", "Argentina", "No", "Argentina", "-36.7253948",
        "-60.7624803", "War of the Desert",
    ),
    "hced-Tucapel1553-1": _semantics(
        "hced-Tucapel1553-1", "Tucapel", 1553, "Araucanians", "Spain",
        "Araucanians", "Spain", "No", "Chile", "-37.2923048", "-71.9512186",
        "Spanish Conquest of Chile",
    ),
}


def _uncertain_day_interval(low: str, high: str, precision: str) -> dict[str, Any]:
    best = low if low == high else None
    date = {"low": low, "best": best, "high": high, "precision": precision}
    return {"start": dict(date), "end": dict(date)}


def _canonical(
    name: str,
    year_low: int,
    year_high: int,
    date_precision: str,
    date_text: str,
    date_interval: Mapping[str, Any],
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{year_high}",
        "date_interval": dict(date_interval),
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": year_high,
    }


_EVENT_EVIDENCE_REFS: dict[str, tuple[str, ...]] = {
    "hced-Tucapel1553-1": _TUCAPEL_SOURCES,
    "hced-Mariguenu1554-1": _MARIGUENU_SOURCES,
    "hced-Mataquito1557-1": _MATAQUITO_SOURCES,
    "hced-Curalaba1598-1": _CURALABA_SOURCES,
}


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1: str,
    side_2: str,
    reviewed_outcome: str,
    audit_note: str,
    *,
    confidence: float,
    source_date_override: bool = False,
) -> dict[str, Any]:
    evidence = sorted(_EVENT_EVIDENCE_REFS[candidate_id])
    families = sorted(
        {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in evidence}
    )
    return {
        "raw_row_sha256": WAVE8_ARAUCANIAN_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "arauco_war_1553_1598_bounded_engagements",
        "side_1_entity_ids": [side_1],
        "side_2_entity_ids": [side_2],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": evidence,
        "outcome_source_family_ids": families,
        "date_source_ids": evidence,
        "source_date_override": source_date_override,
        "source_date_refinement": True,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_alias_free_event_bounded_combined_forces",
        "expected_scale_level": 2,
        "reviewed_outcome": reviewed_outcome,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_ARAUCANIAN_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Tucapel1553-1": _contract(
        "hced-Tucapel1553-1",
        _canonical(
            "Battle of Tucapel",
            1553,
            1554,
            "disputed_day",
            "25 December 1553 or 1 January 1554",
            _uncertain_day_interval("1553-12-25", "1554-01-01", "disputed_day"),
            "single_field_battle_at_historic_fort_tucapel_not_capture_or_execution",
        ),
        _TUCAPEL_ALLIANCE,
        _VALDIVIA_TUCAPEL_COLUMN,
        "Tactical victory for Lautaro's event-bounded lineage alliance",
        (
            "The date remains an explicit 1553-1554 uncertainty envelope. The battle "
            "rates once; Valdivia's capture and death are excluded aftermath."
        ),
        confidence=0.92,
        source_date_override=True,
    ),
    "hced-Mariguenu1554-1": _contract(
        "hced-Mariguenu1554-1",
        _canonical(
            "Battle of Mariguenu",
            1554,
            1554,
            "month",
            "February 1554 (23 or 26 February disputed)",
            _uncertain_day_interval("1554-02-23", "1554-02-26", "month_disputed_day"),
            "single_field_battle_not_post_battle_massacre",
        ),
        _MARIGUENU_FORCE,
        _VILLAGRA_MARIGUENU_COLUMN,
        "Tactical victory for Lautaro's event-bounded Mariguenu force",
        (
            "Only the February field battle is rated. Source disagreement prevents "
            "day precision, and subsequent killings cannot form another result."
        ),
        confidence=0.91,
    ),
    "hced-Mataquito1557-1": _contract(
        "hced-Mataquito1557-1",
        _canonical(
            "Battle of Mataquito",
            1557,
            1557,
            "day",
            "29 April 1557",
            _uncertain_day_interval("1557-04-29", "1557-04-29", "day"),
            "single_dawn_assault_on_fortified_armed_camp_not_campaign_or_civilian_harm",
        ),
        _MATAQUITO_ASSAULT,
        _MATAQUITO_DEFENDERS,
        "Tactical victory for Villagra and Godinez's combined assault force",
        (
            "The contract is restricted to the fortified camp's armed defenders. "
            "Civilians, captives, and later violence are excluded from participants."
        ),
        confidence=0.93,
    ),
    "hced-Curalaba1598-1": _contract(
        "hced-Curalaba1598-1",
        _canonical(
            "Battle of Curalaba",
            1598,
            1598,
            "day",
            "23 December 1598",
            _uncertain_day_interval("1598-12-23", "1598-12-23", "day"),
            "single_dawn_attack_on_governor_marching_camp_not_1598_1604_uprising",
        ),
        _CURALABA_STRIKE,
        _CURALABA_COLUMN,
        "Tactical victory for Pelantaro's event-bounded strike force",
        (
            "Only the attack on the governor's combined marching column is rated; "
            "the broader uprising and strategic consequences are excluded."
        ),
        confidence=0.95,
    ),
}


WAVE8_ARAUCANIAN_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Tapalque Creek1856-1": {
        "raw_row_sha256": WAVE8_ARAUCANIAN_ROW_HASHES["hced-Tapalque Creek1856-1"],
        "disposition": "hold",
        "hold_category": "date_and_composite_actor_contract_unresolved",
        "canonical_event": {
            "name": "Battle of San Jacinto / Tapalque Creek",
            "date_assertions": ["1855-10-29", "1856"],
            "granularity": "single_battle_but_year_and_force_composition_unresolved",
        },
        "reviewed_outcome": "confederated_indigenous_tactical_victory_attested",
        "automatic_rating": False,
        "unknown_is_never_draw": True,
        "evidence_refs": sorted(_TAPALQUE_SOURCES),
        "hold_reason": (
            "Scholarly sources conflict between 29 October 1855 and 1856. HCED also "
            "collapses Catriel, Cachul, and Calfucura's confederated force and Hornos's "
            "Buenos Aires army, which included Maica Indigenous lancers, into generic "
            "Mapuche and Argentina labels."
        ),
    }
}

WAVE8_ARAUCANIAN_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Apeleg1883-1": {
        "raw_row_sha256": WAVE8_ARAUCANIAN_ROW_HASHES["hced-Apeleg1883-1"],
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "exclusion_category": "noncompetitive_attack_on_indigenous_family_camp",
        "reviewed_granularity": "dawn_attack_on_family_camp_and_forced_removal",
        "reviewed_outcome": "not_rateable_civilian_mass_violence",
        "automatic_rating": False,
        "unknown_is_never_draw": True,
        "evidence_refs": sorted(_APELEG_SOURCES),
        "exclusion_reason": (
            "Scholarly evidence reports two soldiers killed against more than one "
            "hundred Indigenous people, including women and children, followed by "
            "deportation of survivors. HCED's Argentina-win and no-massacre fields "
            "cannot be converted into a competitive result."
        ),
    }
}

WAVE8_ARAUCANIAN_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_ARAUCANIAN_HOLDS,
    **WAVE8_ARAUCANIAN_TERMINAL_EXCLUSIONS,
}
WAVE8_ARAUCANIAN_CONTRACT_IDS = frozenset(WAVE8_ARAUCANIAN_CONTRACTS)
WAVE8_ARAUCANIAN_HOLD_IDS = frozenset(WAVE8_ARAUCANIAN_HOLDS)
WAVE8_ARAUCANIAN_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_ARAUCANIAN_TERMINAL_EXCLUSIONS
)
WAVE8_ARAUCANIAN_RESERVED_IDS = frozenset(
    WAVE8_ARAUCANIAN_CONTRACT_IDS
    | WAVE8_ARAUCANIAN_HOLD_IDS
    | WAVE8_ARAUCANIAN_TERMINAL_EXCLUSION_IDS
)


WAVE8_ARAUCANIAN_HCED_HOMONYM_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-San Jacinto1899-1": {
        "raw_row_sha256": WAVE8_ARAUCANIAN_ROW_HASHES["hced-San Jacinto1899-1"],
        "disposition": "existing_release_owner_outside_lane",
        "owner_event_id": "hced_label_hced_san_jacinto1899_1",
        "source_dataset": "hced",
        "automatic_rating": False,
        "reason": "Philippines homonym; preserve its existing Pangasinan release owner.",
    }
}


WAVE8_ARAUCANIAN_POINT_QUARANTINE_ADDITIONS = WAVE8_ARAUCANIAN_CONTRACT_IDS
WAVE8_ARAUCANIAN_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_ARAUCANIAN_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Tucapel1553-1": {
        "actions": ["withhold_point"],
        "raw_country": "Chile",
        "raw_point": [-71.9512186, -37.2923048],
        "reason_code": "modern_locality_homonym_not_historic_fort",
        "evidence_refs": sorted(_TUCAPEL_SOURCES),
    },
    "hced-Mariguenu1554-1": {
        "actions": ["withhold_point"],
        "raw_country": "Chile",
        "raw_point": [-70.677044, -33.45273],
        "reason_code": "reviewed_battle_location_mismatch",
        "evidence_refs": sorted(_MARIGUENU_SOURCES),
    },
    "hced-Mataquito1557-1": {
        "actions": ["withhold_point"],
        "raw_country": "Chile",
        "raw_point": [-72.0629353, -35.0495842],
        "reason_code": "candidate_keyed_point_not_independently_verified",
        "evidence_refs": sorted(_MATAQUITO_SOURCES),
    },
    "hced-Curalaba1598-1": {
        "actions": ["withhold_point"],
        "raw_country": "Chile",
        "raw_point": [-70.781171, -33.5351231],
        "reason_code": "reviewed_battle_location_mismatch",
        "evidence_refs": sorted(_CURALABA_SOURCES),
    },
}


WAVE8_ARAUCANIAN_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "araucanian indians": {
        "candidate_ids": [],
        "centuries": {"CE_16": 2},
        "components_bridged": 0,
        "components_touched": 1,
        "event_candidate_id_sha256": "1c9a29db0d3878a26055292613894a7069e937929404f6dc62a00a0c854e414a",
        "events_touched": 2,
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 2,
        },
        "label": "araucanian indians",
        "rated_counterpart_entities": 1,
        "sole_blocker_events": 2,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 2,
    },
    "araucania": {
        "candidate_ids": [], "centuries": {"CE_16": 1}, "components_bridged": 0,
        "components_touched": 1,
        "event_candidate_id_sha256": "b4ffe22444abc3cc4bec62dfc5b6a363c7883cd54ed10e78bc24b5891891c2af",
        "events_touched": 1,
        "failure_cases": {"multiple_time_valid_candidates": 0, "one_wrong_interval_candidate": 0, "policy_denied_window": 0, "resolver_guard_or_tier_conflict": 0, "zero_time_valid_candidates": 1},
        "label": "araucania", "rated_counterpart_entities": 1,
        "sole_blocker_events": 1, "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 1,
    },
    "araucanians": {
        "candidate_ids": [], "centuries": {"CE_16": 1}, "components_bridged": 0,
        "components_touched": 1,
        "event_candidate_id_sha256": "b640cc6f02f7f4aff07a04200262ca009c72b1a6c1e17b15fd382a0f622931fa",
        "events_touched": 1,
        "failure_cases": {"multiple_time_valid_candidates": 0, "one_wrong_interval_candidate": 0, "policy_denied_window": 0, "resolver_guard_or_tier_conflict": 0, "zero_time_valid_candidates": 1},
        "label": "araucanians", "rated_counterpart_entities": 1,
        "sole_blocker_events": 1, "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 1,
    },
    "mapuche": {
        "candidate_ids": [], "centuries": {"CE_19": 1}, "components_bridged": 0,
        "components_touched": 1,
        "event_candidate_id_sha256": "e49aa963579386a6675bdccf13f5287c333d08bf1fdb45e05992597058aeddd9",
        "events_touched": 1,
        "failure_cases": {"multiple_time_valid_candidates": 0, "one_wrong_interval_candidate": 0, "policy_denied_window": 0, "resolver_guard_or_tier_conflict": 0, "zero_time_valid_candidates": 1},
        "label": "mapuche", "rated_counterpart_entities": 1,
        "sole_blocker_events": 1, "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 1,
    },
    "mapuche rebels": {
        "candidate_ids": [], "centuries": {"CE_19": 1}, "components_bridged": 0,
        "components_touched": 1,
        "event_candidate_id_sha256": "b9574e01abbf6929f6138c5db42cd1a88dc025b1dbd05c228146f61785ff3d75",
        "events_touched": 1,
        "failure_cases": {"multiple_time_valid_candidates": 0, "one_wrong_interval_candidate": 0, "policy_denied_window": 0, "resolver_guard_or_tier_conflict": 0, "zero_time_valid_candidates": 1},
        "label": "mapuche rebels", "rated_counterpart_entities": 1,
        "sole_blocker_events": 1, "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 1,
    },
}


def _wd(
    raw_hash: str,
    name: str,
    kind: str,
    date: str,
    end_date: str | None,
    disposition: str,
    canonical_owner: str | None = None,
    date_disposition: str = "discovery_date_not_imported",
) -> dict[str, Any]:
    return {
        "raw_row_sha256": raw_hash,
        "name": name,
        "kind": kind,
        "date": date,
        "end_date": end_date,
        "winners": [],
        "disposition": disposition,
        "canonical_owner": canonical_owner,
        "date_disposition": date_disposition,
        "outcome_disposition": "unknown_never_draw",
        "automatic_rating": False,
    }


WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED: dict[str, dict[str, Any]] = {
    "Q104849178": _wd("d5208e9dfe455f4dfd360ceaf8091d1ddec7f82e0923f1bf87567ed05c785802", "Battle of Rio Bueno", "engagement", "1759-01-27T00:00:00Z", None, "hold_discovery_only"),
    "Q117218442": _wd("8f5318653ca9005ef3b4aab2ea23739b188c9c9180974cc0ea9af0088427993e", "Battle of Curaco", "engagement", "1868-11-19T00:00:00Z", None, "hold_discovery_only"),
    "Q124513678": _wd("550583d0573f7766b9088750c8dffe0338d0f59b0b64a4447df9be884300ea4a", "Battle of Los Robles", "engagement", "1630-05-14T00:00:00Z", None, "hold_discovery_only"),
    "Q134840158": _wd("974cf5eb4804359e175e0cf6733a754c8275da886f5eb9a9ed3a6dbff7adcfcf", "Battle of Itata", "engagement", "1564-01-25T00:00:00Z", None, "hold_discovery_only"),
    "Q134840190": _wd("f22deadcf8973197aaf7973296524b460ca8b9789e264442e86cb86f5dd43b72", "Battle of Vegas de Andalien", "engagement", "1564-02-01T00:00:00Z", None, "hold_discovery_only"),
    "Q134996426": _wd("dc430f00c7d060e3c826c84d2e309bbba7ef1ff0a7696b827f47070484069e50", "Battle of Talcamavida", "engagement", "1566-02-07T00:00:00Z", None, "hold_discovery_only"),
    "Q135643280": _wd("cf5994a8ad0238044516e5d7211fa94bb5bef0135fdd80aef266515c78cf4a1e", "Battle of Reynoguelen", "engagement", "1565-02-27T00:00:00Z", "1565-02-28T00:00:00Z", "hold_discovery_only"),
    "Q1616739": _wd("de7a9ec19c25811d770a1284f5b39afcabee8a7ef52fb3c523f28fdb09e3f346", "Battle of Reynoguelen", "engagement", "1536-07-25T00:00:00Z", None, "hold_discovery_only"),
    "Q1616748": _wd("4be4e48a2668aea6759470830a62f15cb089682aada1977331791adee12e9156", "Battle of Peteroa", "engagement", "1556-01-01T00:00:00Z", None, "hold_discovery_only"),
    "Q1617262": _wd("43233093bdc9b16114a9e43ed2850ef99b9a68badd13a20b97ea0a05d34055fd", "Battle of Quiapo", "engagement", "1558-12-23T00:00:00Z", None, "hold_discovery_only"),
    "Q1617531": _wd("2778ccfce8d80ee67b428021695db738e6556840562d7c2e6e68aa1370041ed3", "Battle of Penco", "engagement", "1550-03-12T00:00:00Z", None, "hold_discovery_only"),
    "Q16491212": _wd("88be8d121aded87d89d8aded25945b638e5da85ef7989bee0173a67e1178de2c", "Battle of Quechereguas", "engagement", "1868-04-25T00:00:00Z", "1868-04-26T00:00:00Z", "hold_discovery_only"),
    "Q2339158": _wd("9294974514bf8cb9c81bc9c901a67111e51655ca080793818dc43c589ccb83e9", "Battle of Millarapue", "engagement", "1557-12-10T00:00:00Z", None, "hold_discovery_only"),
    "Q3636322": _wd("3ba39c44adce8796919d78c6125969e7cb9296b600e321b6e1d024cfbe5db187", "Battle of Andalien", "engagement", "1550-02-06T00:00:00Z", None, "hold_discovery_only"),
    "Q3636323": _wd("4eb8e1997eeee6d86cdaf95d8fcfad91394de05d4b14c5fc1cdbb81b90bac008", "Battle of Angol", "engagement", "1564-04-04T00:00:00Z", None, "hold_discovery_only"),
    "Q3636379": _wd("84294d4bd3181240b83d254c3f0863d3446f5ac6b5f991ae96901ad14f1cd8d6", "Battle of Catirai", "engagement", "1569-01-17T00:00:00Z", None, "hold_discovery_only"),
    "Q3636492": _wd("a26ae860ab9f69985566735a2c9ba00a4c3b8af251ccf5ead17533ed6a2a7051", "Battle of Lagunillas", "engagement", "1557-11-18T00:00:00Z", None, "hold_discovery_only"),
    "Q3636592": _wd("de83a80f300cdd7c3602d2862bd5acb2e0e1cc385ffba6045c276a079d14da71", "Battle of Quilacura", "engagement", "1546-02-11T00:00:00Z", None, "hold_discovery_only"),
    "Q432297": _wd("e64c38af84a6600e59dd1403fbf9eddbc22bdfef02127c5bca99480fbbeca916", "Siege of Concepcion", "siege", "1564-02-11T00:00:00Z", "1564-04-11T00:00:00Z", "hold_discovery_only"),
    "Q5723320": _wd("fbedb4d91590f0f52ad1acf0d0d30a31f3757aa9edd5475161ec77b450010c76", "Battle of Fuerte de Arauco", "engagement", "1559-01-09T00:00:00Z", None, "hold_discovery_only"),
    "Q5803810": _wd("307b2ad1e191197e442e5c279c65ee29ff0f6713702292ae4dd70d0181e5f11b", "Boroa Disaster", "engagement", "1606-01-01T00:00:00Z", "1606-11-30T00:00:00Z", "hold_discovery_only"),
    "Q6086017": _wd("396465a86459a97fa3a40999d3de9405dc19b9f8c154712238b102836560b989", "First Siege of Fort Arauco", "siege", "1563-02-13T00:00:00Z", None, "hold_discovery_only"),
    "Q6123900": _wd("abfa948880b99af83bf9e64cc9f85ea585e14b3b043ae177c6079f132da6d364", "Second Siege of Arauco", "siege", "1563-04-24T00:00:00Z", "1563-06-05T00:00:00Z", "hold_discovery_only"),
    "Q85745908": _wd("da0424966b3f0292abf23acf1483800697a6248f6995a3fb9657f83de49eb578", "Battle of Rio Bueno", "engagement", "1654-01-11T00:00:00Z", None, "hold_discovery_only"),
    "Q2338555": _wd("83a32f574575b32979a263955af6da87aaaf4786ecb3d67213190446d5ea591c", "Battle of Marihuenu", "engagement", "1554-02-23T00:00:00Z", None, "duplicate_hced_owner", "hced-Mariguenu1554-1", "disputed_day_retained_only_as_source_assertion"),
    "Q1617667": _wd("0e7046c97583677752f1a2ed663851a376df9304d7d81fe6ae6398028ad38735", "Battle of Mataquito", "engagement", "1557-04-30T00:00:00Z", None, "duplicate_hced_owner", "hced-Mataquito1557-1", "wikidata_30_april_not_imported"),
    "Q645257": _wd("62ce91bd2d2873ded01a3a8c52bdab3265070f60f1d3acc116cf2d7279f8d625", "Battle of Tucapel", "engagement", "1554-01-04T00:00:00Z", None, "duplicate_hced_owner", "hced-Tucapel1553-1", "wikidata_4_january_not_imported"),
    "Q1629355": _wd("251b7afb2f57afd7a181e10cc53d5657c3f0dae0089f4e4daa57c5afb360df8f", "Disaster of Curalaba", "engagement", "1598-12-23T00:00:00Z", None, "duplicate_hced_owner", "hced-Curalaba1598-1", "corroborating_date_only_no_discovery_rating"),
    "Q51077807": _wd("0e9a3d7753ed7f2ff0283485279fe17331e7d5ca1de00c9cd5cb8f5e38f495b0", "Battle of San Jacinto", "engagement", "1855-01-01T00:00:00Z", None, "duplicate_held_hced_owner", "hced-Tapalque Creek1856-1", "year_placeholder_does_not_resolve_29_october_conflict"),
    "Q841278": _wd("83b5975f9a5c0aa1d835bf3585393731ce007680fb5a8e854081ecd9d887ba38", "Battle of San Jacinto", "engagement", "1836-04-21T00:00:00Z", None, "exclude_unrelated_san_jacinto_homonym"),
    "Q4872280": _wd("51fed8e7a6bb3f4fd0ba75f59e9c75a6a9def698dc58723613c6d8028c32a601", "Battle of San Jacinto", "engagement", "1856-09-14T00:00:00Z", None, "exclude_unrelated_san_jacinto_homonym"),
    "Q4872274": _wd("3e962f027f4033085f3e83c0a668c54c83d9efbc33b1ecfb9c6a3cd60435c244", "Battle of San Jacinto", "engagement", "1899-11-11T00:00:00Z", None, "duplicate_existing_release_owner_outside_lane", "hced_label_hced_san_jacinto1899_1"),
    "Q5722899": _wd("de1252f7872b242078f9de6f4437cdb9cd478dba3e983c249f361cc86716a900", "Battle of San Jacinto (1867)", "engagement", "1867-01-01T00:00:00Z", None, "exclude_unrelated_san_jacinto_homonym"),
}

WAVE8_ARAUCANIAN_WIKIDATA_ROW_HASHES = {
    candidate_id: str(expected["raw_row_sha256"])
    for candidate_id, expected in WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED.items()
}
WAVE8_ARAUCANIAN_WIKIDATA_DISPOSITIONS = {
    candidate_id: {
        key: expected[key]
        for key in (
            "automatic_rating", "canonical_owner", "date_disposition",
            "disposition", "outcome_disposition",
        )
    }
    for candidate_id, expected in WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED.items()
}

WAVE8_ARAUCANIAN_IWBD_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-40-14-142": {
        "raw_row_sha256": "84d7b4d37012a7f6f7c35243dd5383297fb6b6a7e0ddd5835768b333aedcbb32",
        "disposition": "exclude_unrelated_san_jacinto_homonym",
        "automatic_rating": False,
        "expected": {
            "name": "San Jacinto", "start_date": "1867-02-12",
            "end_date": "1867-02-12", "attacker_raw": "Mexico",
            "defender_raw": "France", "winner_raw": "Mexico",
            "battle_level_victor_role": "Attacker", "do_not_rate_automatically": True,
        },
    }
}

WAVE8_ARAUCANIAN_BRECKE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "brecke-2719": {
        "raw_row_sha256": "82228abae28f1420cd8e8f1cc250e17e2942bc07e46610c72564cc0405aafaf8",
        "disposition": "exclude_coverage_cross_check_only",
        "automatic_rating": False,
        "outcome_disposition": "unknown_never_draw",
        "expected": {
            "name_raw": "Chile-Araucaninan Indians, 1881-83",
            "start_year": 1881, "end_year": 1883,
            "outcome_available": False, "rating_use": "coverage_cross_check_only",
        },
    }
}

_WIKIDATA_HOMONYM_IDS = frozenset({"Q841278", "Q4872280", "Q4872274", "Q5722899"})
_WIKIDATA_RELEVANT_IDS = frozenset(WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED) - _WIKIDATA_HOMONYM_IDS
WAVE8_ARAUCANIAN_AUDITED_RECORD_IDS = frozenset(
    set(WAVE8_ARAUCANIAN_ROW_HASHES)
    | set(WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED)
    | set(WAVE8_ARAUCANIAN_IWBD_DISPOSITIONS)
    | set(WAVE8_ARAUCANIAN_BRECKE_DISPOSITIONS)
)
WAVE8_ARAUCANIAN_AUDITED_RECORD_ID_SHA256 = (
    "d35423568a77931b8436a45bc3c7bffe1ecd280baf5c883aaf8d15ab99d40a60"
)
_WIKIDATA_ALL_ID_SHA256 = "a5bc28bf2c8d4d73ad2259d4d27989da9a3a9ad62a1e67e1e3db971c2bb58052"
_WIKIDATA_RELEVANT_ID_SHA256 = "a58be88fab878ee47280ae057832f56ec732514ca100fc1821791947b2465d61"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "\n".join(sorted(map(str, values))) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _signature_payload() -> dict[str, Any]:
    return {
        "audited_record_digest": WAVE8_ARAUCANIAN_AUDITED_RECORD_ID_SHA256,
        "brecke_dispositions": WAVE8_ARAUCANIAN_BRECKE_DISPOSITIONS,
        "contracts": WAVE8_ARAUCANIAN_CONTRACTS,
        "country_quarantine": sorted(WAVE8_ARAUCANIAN_COUNTRY_QUARANTINE_ADDITIONS),
        "entities": WAVE8_ARAUCANIAN_ENTITIES,
        "funnel": WAVE8_ARAUCANIAN_FUNNEL_AUDIT,
        "hced_homonyms": WAVE8_ARAUCANIAN_HCED_HOMONYM_DISPOSITIONS,
        "holds": WAVE8_ARAUCANIAN_HOLDS,
        "input_sha256": WAVE8_ARAUCANIAN_INPUT_SHA256,
        "iwbd_dispositions": WAVE8_ARAUCANIAN_IWBD_DISPOSITIONS,
        "location_reasons": WAVE8_ARAUCANIAN_LOCATION_QUARANTINE_REASONS,
        "point_quarantine": sorted(WAVE8_ARAUCANIAN_POINT_QUARANTINE_ADDITIONS),
        "row_hashes": WAVE8_ARAUCANIAN_ROW_HASHES,
        "row_semantics": WAVE8_ARAUCANIAN_SOURCE_ROW_SEMANTICS,
        "sources": WAVE8_ARAUCANIAN_SOURCES,
        "terminal_exclusions": WAVE8_ARAUCANIAN_TERMINAL_EXCLUSIONS,
        "wikidata_expected": WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED,
    }


def wave8_araucanian_audit_signature() -> str:
    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_ARAUCANIAN_FINAL_AUDIT_SIGNATURE = (
    "2166530e7abd1e4f5c2d6e41cb61638ab17b2658eb4104feb6e1b4e064243c51"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_ARAUCANIAN_CONTRACTS), len(WAVE8_ARAUCANIAN_HOLDS), len(WAVE8_ARAUCANIAN_TERMINAL_EXCLUSIONS)) != (4, 1, 1):
        raise ValueError(f"{_LANE_NAME} HCED disposition inventory changed")
    if (len(WAVE8_ARAUCANIAN_ENTITIES), len(WAVE8_ARAUCANIAN_SOURCES)) != (8, 14):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_ARAUCANIAN_RESERVED_IDS != set(WAVE8_ARAUCANIAN_ROW_HASHES) - {"hced-San Jacinto1899-1"}:
        raise ValueError(f"{_LANE_NAME} reservation inventory changed")
    if set(WAVE8_ARAUCANIAN_SOURCE_ROW_SEMANTICS) != set(WAVE8_ARAUCANIAN_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} source semantic inventory changed")
    if any(tuple(row) != _SOURCE_SEMANTIC_FIELDS for row in WAVE8_ARAUCANIAN_SOURCE_ROW_SEMANTICS.values()):
        raise ValueError(f"{_LANE_NAME} source semantic projection changed")
    if len(WAVE8_ARAUCANIAN_AUDITED_RECORD_IDS) != 42 or _sorted_newline_sha256(WAVE8_ARAUCANIAN_AUDITED_RECORD_IDS) != WAVE8_ARAUCANIAN_AUDITED_RECORD_ID_SHA256:
        raise ValueError(f"{_LANE_NAME} 42-record audit inventory changed")
    if len(WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED) != 33 or len(_WIKIDATA_RELEVANT_IDS) != 29:
        raise ValueError(f"{_LANE_NAME} Wikidata inventory changed")
    if _sorted_newline_sha256(WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED) != _WIKIDATA_ALL_ID_SHA256 or _sorted_newline_sha256(_WIKIDATA_RELEVANT_IDS) != _WIKIDATA_RELEVANT_ID_SHA256:
        raise ValueError(f"{_LANE_NAME} Wikidata ID digest changed")

    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_ARAUCANIAN_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source ID")
    for source in WAVE8_ARAUCANIAN_SOURCES:
        if not str(source["url"]).startswith("https://") or "wikipedia.org" in str(source["url"]):
            raise ValueError(f"{_LANE_NAME} source authority changed")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    expected_windows = {
        _TUCAPEL_ALLIANCE: (1553, 1554), _VALDIVIA_TUCAPEL_COLUMN: (1553, 1554),
        _MARIGUENU_FORCE: (1554, 1554), _VILLAGRA_MARIGUENU_COLUMN: (1554, 1554),
        _MATAQUITO_ASSAULT: (1557, 1557), _MATAQUITO_DEFENDERS: (1557, 1557),
        _CURALABA_STRIKE: (1598, 1598), _CURALABA_COLUMN: (1598, 1598),
    }
    if set(_ENTITY_BY_ID) != set(expected_windows):
        raise ValueError(f"{_LANE_NAME} entity inventory changed")
    forbidden_ids = {"araucania", "araucanian_indians", "araucanians", "mapuche", "mapuche_rebels", "spain", "spanish_empire"}
    for entity_id, entity in _ENTITY_BY_ID.items():
        if entity_id in forbidden_ids or entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} generic actor or alias leaked")
        if (int(entity["start_year"]), int(entity["end_year"])) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} identity window changed: {entity_id}")
        if "inherits no elo" not in normalize_label(entity["continuity_note"]):
            raise ValueError(f"{_LANE_NAME} continuity firewall changed")
        if not _is_sorted_unique(entity["source_ids"]) or not set(entity["source_ids"]) <= source_ids:
            raise ValueError(f"{_LANE_NAME} entity evidence changed")

    expected_dates = {
        "hced-Tucapel1553-1": (1553, 1554, "disputed_day", "1553-12-25", None, "1554-01-01", True),
        "hced-Mariguenu1554-1": (1554, 1554, "month", "1554-02-23", None, "1554-02-26", False),
        "hced-Mataquito1557-1": (1557, 1557, "day", "1557-04-29", "1557-04-29", "1557-04-29", False),
        "hced-Curalaba1598-1": (1598, 1598, "day", "1598-12-23", "1598-12-23", "1598-12-23", False),
    }
    entity_use: Counter[str] = Counter()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_ARAUCANIAN_CONTRACTS.items():
        canonical = contract["canonical_event"]
        low, high, precision, date_low, date_best, date_high, override = expected_dates[candidate_id]
        date = canonical["date_interval"]["start"]
        if (
            contract["raw_row_sha256"] != WAVE8_ARAUCANIAN_ROW_HASHES[candidate_id]
            or contract["disposition"] != "promote" or contract["result_type"] != "win"
            or contract["winner_side"] != 1 or contract["source_outcome_override"]
            or contract["outcome_reversal"] or contract["source_date_override"] is not override
            or (canonical["year_low"], canonical["year_high"], canonical["date_precision"]) != (low, high, precision)
            or date != {"low": date_low, "best": date_best, "high": date_high, "precision": date["precision"]}
            or canonical["date_interval"]["end"] != date
            or canonical["canonical_key"] != f"{_slug(canonical['name'])}:{low}:{high}"
        ):
            raise ValueError(f"{_LANE_NAME} exact/date contract drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = sorted({_SOURCE_BY_ID[source_id]["source_family_id"] for source_id in outcomes})
        if not _is_sorted_unique(evidence) or outcomes != evidence or not set(evidence) <= source_ids or contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} evidence closure changed: {candidate_id}")
        actors = [*contract["side_1_entity_ids"], *contract["side_2_entity_ids"]]
        if len(actors) != 2 or set(actors) - set(_ENTITY_BY_ID):
            raise ValueError(f"{_LANE_NAME} actor boundary changed: {candidate_id}")
        entity_use.update(map(str, actors))
        used_sources.update(evidence)
    if entity_use != Counter({entity_id: 1 for entity_id in _ENTITY_BY_ID}):
        raise ValueError(f"{_LANE_NAME} entities are not consumed exactly once")

    forbidden_nonrating_fields = {"result_type", "winner_side", "side_1_entity_ids", "side_2_entity_ids"}
    for candidate_id, disposition in WAVE8_ARAUCANIAN_NONPROMOTIONS.items():
        if disposition["automatic_rating"] is not False or disposition["unknown_is_never_draw"] is not True or forbidden_nonrating_fields & set(disposition):
            raise ValueError(f"{_LANE_NAME} nonrating guard changed: {candidate_id}")
        refs = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= source_ids:
            raise ValueError(f"{_LANE_NAME} nonrating evidence changed: {candidate_id}")
        used_sources.update(refs)
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")

    if WAVE8_ARAUCANIAN_POINT_QUARANTINE_ADDITIONS != WAVE8_ARAUCANIAN_CONTRACT_IDS or WAVE8_ARAUCANIAN_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} location quarantine changed")
    if set(WAVE8_ARAUCANIAN_LOCATION_QUARANTINE_REASONS) != WAVE8_ARAUCANIAN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory changed")
    for item in WAVE8_ARAUCANIAN_LOCATION_QUARANTINE_REASONS.values():
        if item["actions"] != ["withhold_point"] or item["raw_country"] != "Chile":
            raise ValueError(f"{_LANE_NAME} point/country policy changed")

    wd_counts = Counter(item["disposition"] for item in WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED.values())
    if wd_counts["hold_discovery_only"] != 24 or sum(wd_counts.values()) != 33:
        raise ValueError(f"{_LANE_NAME} discovery disposition counts changed")
    if any(item["automatic_rating"] is not False or item["outcome_disposition"] != "unknown_never_draw" or item["winners"] for item in WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED.values()):
        raise ValueError(f"{_LANE_NAME} discovery nonrating guard changed")
    if WAVE8_ARAUCANIAN_BRECKE_DISPOSITIONS["brecke-2719"]["outcome_disposition"] != "unknown_never_draw":
        raise ValueError(f"{_LANE_NAME} Brecke unknown became a draw")

    if WAVE8_ARAUCANIAN_FINAL_AUDIT_SIGNATURE != "TO_BE_SEALED" and wave8_araucanian_audit_signature() != WAVE8_ARAUCANIAN_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_araucanian_queue_contracts(hced_rows: list[dict[str, Any]]) -> dict[str, int]:
    _validate_static()
    indexed: dict[str, list[dict[str, Any]]] = {}
    exact_rows: list[dict[str, Any]] = []
    homonyms: list[dict[str, Any]] = []
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id") or "")
        indexed.setdefault(candidate_id, []).append(row)
        sides = {normalize_label(row.get("side_1_raw")), normalize_label(row.get("side_2_raw"))}
        if sides & _OWNED_LABELS:
            exact_rows.append(row)
        if normalize_label(row.get("name")) == "san jacinto":
            homonyms.append(row)
    exact_ids = {str(row.get("candidate_id")) for row in exact_rows}
    if exact_ids != WAVE8_ARAUCANIAN_RESERVED_IDS or len(exact_rows) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact/adjacent label inventory changed")
    if [str(row.get("candidate_id")) for row in homonyms] != ["hced-San Jacinto1899-1"]:
        raise ValueError(f"{_LANE_NAME} exact San Jacinto homonym inventory changed")
    for candidate_id, expected_hash in WAVE8_ARAUCANIAN_ROW_HASHES.items():
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(f"{_LANE_NAME} HCED row {candidate_id} expected once, found {len(rows)}")
        row = rows[0]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        actual = {field: row.get(field) for field in _SOURCE_SEMANTIC_FIELDS}
        if actual != WAVE8_ARAUCANIAN_SOURCE_ROW_SEMANTICS[candidate_id]:
            raise ValueError(f"{_LANE_NAME} locked row semantics changed: {candidate_id}")
    precision_fields = {"date", "start_date", "end_date", "date_precision", "day", "month", "start_day", "start_month", "end_day", "end_month"}
    for candidate_id in ("hced-Tucapel1553-1", "hced-Mariguenu1554-1"):
        if precision_fields & set(indexed[candidate_id][0]):
            raise ValueError(f"{_LANE_NAME} source row increased date precision: {candidate_id}")
    validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ARAUCANIAN_CONTRACTS,
        WAVE8_ARAUCANIAN_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    return {
        "exact_and_adjacent_label_rows": 6,
        "hced_homonym_records": 1,
        "holds": 1,
        "promotion_contracts": 4,
        "reviewed_hced_rows": 7,
        "terminal_exclusions": 1,
    }


def validate_wave8_araucanian_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    rows = {str(row.get("label")): row for row in funnel.get("labels", []) if str(row.get("label")) in WAVE8_ARAUCANIAN_FUNNEL_AUDIT}
    if rows != WAVE8_ARAUCANIAN_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed")
    return {
        "labels": 5,
        "events_touched": sum(int(row["events_touched"]) for row in rows.values()),
        "sole_blocker_events": sum(int(row["sole_blocker_events"]) for row in rows.values()),
        "zero_time_valid_candidates": sum(int(row["failure_cases"]["zero_time_valid_candidates"]) for row in rows.values()),
    }


def _wikidata_scope(row: Mapping[str, Any]) -> bool:
    part_of_uris = {str(item.get("uri")) for item in row.get("part_of", []) or []}
    participant_uris = {str(item.get("uri")) for item in row.get("participants", []) or []}
    name = normalize_label(row.get("name"))
    exact_names = {
        "battle of marihuenu", "battle of mataquito", "battle of tucapel",
        "disaster of curalaba", "battle of fuerte de arauco",
        "first siege of fort arauco", "second siege of arauco",
    }
    return bool(
        part_of_uris & {"http://www.wikidata.org/entity/Q431806", "http://www.wikidata.org/entity/Q2422135"}
        or participant_uris & {"http://www.wikidata.org/entity/Q178484", "http://www.wikidata.org/entity/Q109424190"}
        or name in exact_names
        or name.startswith("battle of san jacinto")
    )


def validate_wave8_araucanian_discovery_dispositions(wikidata_rows: list[dict[str, Any]]) -> dict[str, int]:
    _validate_static()
    scoped = [row for row in wikidata_rows if _wikidata_scope(row)]
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in scoped:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    if set(by_id) != set(WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED) or len(scoped) != len(by_id):
        raise ValueError(f"{_LANE_NAME} Wikidata scope inventory changed")
    for candidate_id, expected in WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED.items():
        rows = by_id[candidate_id]
        if len(rows) != 1:
            raise ValueError(f"{_LANE_NAME} discovery row {candidate_id} expected once")
        row = rows[0]
        if _full_row_sha256(row) != expected["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}")
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or normalize_label(row.get("name")) != normalize_label(expected["name"])
            or row.get("kind") != expected["kind"]
            or row.get("date") != expected["date"]
            or row.get("end_date") != expected["end_date"]
            or row.get("winners") != []
            or expected["automatic_rating"] is not False
            or expected["outcome_disposition"] != "unknown_never_draw"
        ):
            raise ValueError(f"{_LANE_NAME} discovery nonrating guard changed: {candidate_id}")
    dispositions = Counter(item["disposition"] for item in WAVE8_ARAUCANIAN_WIKIDATA_EXPECTED.values())
    return {
        "discovery_nonrating_records": 33,
        "duplicate_discovery_records": 6,
        "held_discovery_records": dispositions["hold_discovery_only"],
        "unrelated_homonym_records": dispositions["exclude_unrelated_san_jacinto_homonym"],
        "unknown_never_draw_rows": 33,
    }


_NEAR_TERMS = ("araucan", "mapuche", "marihue", "mariguen", "mataquito", "tucapel", "curalaba", "tapalqu", "apeleg", "san jacinto")


def _near_discovery_row(row: Mapping[str, Any]) -> bool:
    text = _canonical_json(dict(row)).casefold()
    return any(term in text for term in _NEAR_TERMS)


def validate_wave8_araucanian_cross_source_inventory(
    hced_rows: list[dict[str, Any]],
    wikidata_battle_rows: list[dict[str, Any]],
    brecke_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    iwd_rows: list[dict[str, Any]],
    wikidata_generic_rows: list[dict[str, Any]],
    cliopatria_rows: list[dict[str, Any]],
) -> dict[str, int]:
    validate_wave8_araucanian_queue_contracts(hced_rows)
    validate_wave8_araucanian_discovery_dispositions(wikidata_battle_rows)

    iwbd = [row for row in iwbd_rows if normalize_label(row.get("name")) == "san jacinto"]
    if len(iwbd) != 1 or str(iwbd[0].get("candidate_id")) != "iwbd-40-14-142":
        raise ValueError(f"{_LANE_NAME} IWBD homonym inventory changed")
    iwbd_expected = WAVE8_ARAUCANIAN_IWBD_DISPOSITIONS["iwbd-40-14-142"]
    if _full_row_sha256(iwbd[0]) != iwbd_expected["raw_row_sha256"] or any(iwbd[0].get(key) != value for key, value in iwbd_expected["expected"].items()):
        raise ValueError(f"{_LANE_NAME} IWBD homonym fingerprint changed")

    brecke = [row for row in brecke_rows if "araucaninan indians" in normalize_label(row.get("name_raw"))]
    if len(brecke) != 1 or str(brecke[0].get("brecke_id")) != "brecke-2719":
        raise ValueError(f"{_LANE_NAME} Brecke coverage inventory changed")
    brecke_expected = WAVE8_ARAUCANIAN_BRECKE_DISPOSITIONS["brecke-2719"]
    if _full_row_sha256(brecke[0]) != brecke_expected["raw_row_sha256"] or any(brecke[0].get(key) != value for key, value in brecke_expected["expected"].items()):
        raise ValueError(f"{_LANE_NAME} Brecke fingerprint changed")

    zero_sets = {
        "iwd": [row for row in iwd_rows if _near_discovery_row(row)],
        "wikidata_generic": [row for row in wikidata_generic_rows if _near_discovery_row(row)],
        "cliopatria": [row for row in cliopatria_rows if _near_discovery_row(row)],
    }
    if any(zero_sets.values()):
        raise ValueError(f"{_LANE_NAME} zero-overlap discovery inventory changed")
    return {
        "audited_records": 42,
        "brecke_records": 1,
        "cliopatria_records": 0,
        "excluded_records": 13,
        "hced_records": 7,
        "held_records": 25,
        "iwbd_records": 1,
        "iwd_records": 0,
        "promoted_records": 4,
        "wikidata_battle_records": 33,
        "wikidata_generic_records": 0,
    }


def install_wave8_araucanian_entities(release_entities: dict[str, dict[str, Any]]) -> None:
    _validate_static()
    install_exact_entities(release_entities, WAVE8_ARAUCANIAN_ENTITIES, lane_name=_LANE_NAME)


def install_wave8_araucanian_sources(sources_by_id: dict[str, dict[str, Any]]) -> None:
    _validate_static()
    install_exact_sources(sources_by_id, WAVE8_ARAUCANIAN_SOURCES, lane_name=_LANE_NAME)


def _apply_location_quarantine(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_ARAUCANIAN_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_ARAUCANIAN_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def validate_wave8_araucanian_emissions(events: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    _validate_static()
    owned = list(events)
    by_id = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_id) != WAVE8_ARAUCANIAN_CONTRACT_IDS or len(owned) != len(by_id):
        raise ValueError(f"{_LANE_NAME} emitted inventory drift")
    participant_count = 0
    for candidate_id, contract in WAVE8_ARAUCANIAN_CONTRACTS.items():
        event = by_id[candidate_id]
        canonical = contract["canonical_event"]
        expected_participants = expected_exact_hced_win_participants(
            contract["side_1_entity_ids"], contract["side_2_entity_ids"],
            confidence=float(contract["confidence"]),
            scale_level=int(contract["expected_scale_level"]), lane_name=_LANE_NAME,
        )
        if (
            event.get("id") != f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year")) != (canonical["year_low"], canonical["year_high"])
            or event.get("date_precision") != canonical["date_precision"]
            or event.get("date_interval") != canonical["date_interval"]
            or event.get("reviewed_granularity") != canonical["granularity"]
            or event.get("participants") != expected_participants
            or event.get("aliases") != []
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("source_ids") != ["hced_dataset", *contract["evidence_refs"]]
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids") != contract["outcome_source_family_ids"]
            or "geometry" in event
            or event.get("modern_location_country") != "Chile"
        ):
            raise ValueError(f"{_LANE_NAME} emitted contract drift: {candidate_id}")
        if any("inconclusive" in str(participant.get("termination", "")) for participant in event["participants"]):
            raise ValueError(f"{_LANE_NAME} emitted unknown/draw drift: {candidate_id}")
        participant_count += len(event["participants"])
    return {"events": 4, "participants": participant_count, "retained_countries": 4, "retained_points": 0}


def promote_wave8_araucanian_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_araucanian_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows, release_entities, existing_events, WAVE8_ARAUCANIAN_CONTRACTS,
        lane_name=_LANE_NAME, event_id_prefix=_EVENT_ID_PREFIX,
    )
    for event in events:
        canonical = WAVE8_ARAUCANIAN_CONTRACTS[str(event["hced_candidate_id"])]["canonical_event"]
        event["aliases"] = []
        event["date_interval"] = json.loads(_canonical_json(canonical["date_interval"]))
    _apply_location_quarantine(events)
    validate_wave8_araucanian_emissions(events)
    return events


def validate_wave8_araucanian_current_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
    seed_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    _validate_static()
    release_events = list(release_events)
    seed_events = list(seed_events)
    forbidden_ids = WAVE8_ARAUCANIAN_HOLD_IDS | WAVE8_ARAUCANIAN_TERMINAL_EXCLUSION_IDS
    leaks = [str(event.get("id")) for event in (*release_events, *seed_events) if event.get("hced_candidate_id") in forbidden_ids]
    if leaks:
        raise ValueError(f"{_LANE_NAME} hold/exclusion leaked into a ledger: {leaks}")
    seed_overlap = {str(event.get("hced_candidate_id")) for event in seed_events if event.get("hced_candidate_id") in WAVE8_ARAUCANIAN_CONTRACT_IDS}
    if seed_overlap:
        raise ValueError(f"{_LANE_NAME} candidate events leaked into seed ledger")
    san_jacinto = [event for event in release_events if event.get("hced_candidate_id") == "hced-San Jacinto1899-1"]
    if len(san_jacinto) != 1 or san_jacinto[0].get("id") != "hced_label_hced_san_jacinto1899_1":
        raise ValueError(f"{_LANE_NAME} Philippines San Jacinto owner changed")
    owned = [event for event in release_events if event.get("hced_candidate_id") in WAVE8_ARAUCANIAN_CONTRACT_IDS or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)]
    entity_by_id = {str(entity.get("id")): entity for entity in release_entities}
    source_by_id = {str(source.get("id")): source for source in release_sources}
    present_entities = set(entity_by_id) & set(_ENTITY_BY_ID)
    present_sources = set(source_by_id) & set(_SOURCE_BY_ID)
    actual = (len(owned), len(present_entities), len(present_sources))
    expected = (4, 8, 14)
    if actual == (0, 0, 0):
        return {"artifact_state": "absent", "installed_entities": 0, "installed_sources": 0, "promoted_events": 0, "san_jacinto_external_owner": 1}
    if actual != expected:
        raise ValueError(f"{_LANE_NAME} current artifacts are partial: {actual}")
    for entity_id, fixture in _ENTITY_BY_ID.items():
        if entity_by_id[entity_id] != fixture:
            raise ValueError(f"{_LANE_NAME} current entity drift: {entity_id}")
    for source_id, fixture in _SOURCE_BY_ID.items():
        if source_by_id[source_id] != fixture:
            raise ValueError(f"{_LANE_NAME} current source drift: {source_id}")
    validate_wave8_araucanian_emissions(owned)
    return {"artifact_state": "integrated", "installed_entities": 8, "installed_sources": 14, "promoted_events": 4, "san_jacinto_external_owner": 1}


def wave8_araucanian_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(sorted(Counter(str(contract["cohort"]) for contract in WAVE8_ARAUCANIAN_CONTRACTS.values()).items()))


def wave8_araucanian_counts() -> dict[str, int]:
    _validate_static()
    return {
        "audited_source_records": 42,
        "country_quarantine_additions": 0,
        "discovery_nonrating_records": 35,
        "excluded_records": 13,
        "held_discovery_records": 24,
        "held_records": 25,
        "holds": 1,
        "new_entities": 8,
        "new_sources": 14,
        "newly_rated_events": 4,
        "outcome_overrides": 0,
        "point_quarantine_additions": 4,
        "promoted_records": 4,
        "promotion_contracts": 4,
        "reviewed_hced_rows": 7,
        "terminal_exclusions": 1,
        "unknown_discovery_outcomes": 34,
        "wikidata_nonrating_records": 33,
    }


def wave8_araucanian_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {"country": WAVE8_ARAUCANIAN_COUNTRY_QUARANTINE_ADDITIONS, "point": WAVE8_ARAUCANIAN_POINT_QUARANTINE_ADDITIONS}


def wave8_araucanian_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "audited_record_id_sha256": WAVE8_ARAUCANIAN_AUDITED_RECORD_ID_SHA256,
        "counts": wave8_araucanian_counts(),
        "cohorts": wave8_araucanian_cohort_counts(),
        "final_audit_signature": WAVE8_ARAUCANIAN_FINAL_AUDIT_SIGNATURE,
        "held_candidate_ids": sorted(WAVE8_ARAUCANIAN_HOLD_IDS),
        "point_quarantine_additions": sorted(WAVE8_ARAUCANIAN_POINT_QUARANTINE_ADDITIONS),
        "promoted_candidate_ids": sorted(WAVE8_ARAUCANIAN_CONTRACT_IDS),
        "reserved_candidate_ids": sorted(WAVE8_ARAUCANIAN_RESERVED_IDS),
        "terminal_exclusion_ids": sorted(WAVE8_ARAUCANIAN_TERMINAL_EXCLUSION_IDS),
        "wikidata_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(WAVE8_ARAUCANIAN_WIKIDATA_DISPOSITIONS.items())
        ],
    }


if WAVE8_ARAUCANIAN_FINAL_AUDIT_SIGNATURE != "TO_BE_SEALED":
    _validate_static()
