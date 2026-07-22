"""Fail-closed exact audit of four HCED ``Cordova``-related rows.

Two independently attested operations rate: Simancas in 939 and the
1235-1236 conquest of Córdoba.  Calatañazor 1002 is a late legendary
construction, while the alleged Zamora 873 battle conflates later events;
both are terminal exclusions and emit no result.  The lane never opens a
generic Cordova, Córdoba, or Andalucía alias.

Six related Wikidata rows remain discovery-only.  Their empty winner fields
never originate an outcome, and disputed or distinct records remain staged.
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
    "WAVE8_CORDOVA_CONTRACT_IDS",
    "WAVE8_CORDOVA_CONTRACTS",
    "WAVE8_CORDOVA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_CORDOVA_DISCOVERY_EXPECTED",
    "WAVE8_CORDOVA_DISCOVERY_ROW_HASHES",
    "WAVE8_CORDOVA_ENTITIES",
    "WAVE8_CORDOVA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_CORDOVA_FUNNEL_AUDIT",
    "WAVE8_CORDOVA_HOLDS",
    "WAVE8_CORDOVA_INTEGRATION_DISPOSITIONS",
    "WAVE8_CORDOVA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_CORDOVA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_CORDOVA_RESERVED_IDS",
    "WAVE8_CORDOVA_ROW_HASHES",
    "WAVE8_CORDOVA_SOURCES",
    "WAVE8_CORDOVA_TERMINAL_EXCLUSION_IDS",
    "WAVE8_CORDOVA_TERMINAL_EXCLUSIONS",
    "install_wave8_cordova_entities",
    "install_wave8_cordova_sources",
    "promote_wave8_cordova_contracts",
    "validate_wave8_cordova_discovery_dispositions",
    "validate_wave8_cordova_existing_entities",
    "validate_wave8_cordova_funnel",
    "validate_wave8_cordova_integration_dispositions",
    "validate_wave8_cordova_queue_contracts",
    "wave8_cordova_audit_signature",
    "wave8_cordova_cohort_counts",
    "wave8_cordova_counts",
    "wave8_cordova_metadata",
)


_LANE_NAME = "Wave 8 exact Cordova historical audit"
_MODULE_OWNER = "military_elo.promotion.wave8_cordova"
_EVENT_ID_PREFIX = "hced_wave8_cordova_"

_CROWN_CASTILE = "crown_castile_1230"
_CORDOBA_DEFENDERS = "cordoba_muslim_defenders_1235_1236"
_KINGDOM_LEON = "clio_es_leon_k_911_229ce82d"
_CASTILIAN_CONTINGENT = "fernan_gonzalez_castilian_contingent_simancas_939"
_PAMPLONESE_CONTINGENT = "garcia_sanchez_i_pamplonese_contingent_simancas_939"
_CALIPHATE_CORDOBA = "clio_es_cordoba_cal_936_feb4eaea"


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
        "accessed": "2026-07-21",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_CORDOVA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_cordova_cordoba_museo_ejercito",
        "Conquista de Córdoba",
        (
            "https://ejercito.defensa.gob.es/museo/HECHOS_HISTORICOS/"
            "HECHOS_HISTORICOS/06.29_junio_Fernando_III_reconquista_"
            "Cordoba.html?__locale=es"
        ),
        "Museo del Ejercito, Ministerio de Defensa de Espana",
        "official_military_museum_history",
        "spain_defence_museo_ejercito_cordoba",
        outcome=True,
    ),
    _source(
        "wave8_cordova_cordoba_rodriguez_2022",
        "Royal Entries in Conquered Towns",
        (
            "https://cultureandhistory.revistas.csic.es/index.php/"
            "cultureandhistory/article/download/240/760"
        ),
        "Culture & History Digital Journal, CSIC",
        "peer_reviewed_history_article",
        "rodriguez_royal_entries_2022",
        outcome=True,
    ),
    _source(
        "wave8_cordova_simancas_kusku_2023",
        "Simancas Defeat of Andalusian Umayyad Caliph Abdurrahman III (939)",
        "https://dergipark.org.tr/en/pub/deusosbil/article/1109820",
        "Dokuz Eylul University Journal of Humanities",
        "peer_reviewed_history_article",
        "deu_kusku_simancas_2023",
        outcome=True,
    ),
    _source(
        "wave8_cordova_simancas_ags_guide",
        "Guía del investigador del Archivo General de Simancas",
        (
            "https://www.cultura.gob.es/dam/"
            "jcr%3A2794ac18-dfaf-4a7c-99a6-3a7e897b3e5c/"
            "guia-del-investigador.pdf"
        ),
        "Archivo General de Simancas, Ministerio de Cultura de Espana",
        "official_archival_guide",
        "spain_culture_ags_simancas_guide",
        outcome=True,
    ),
    _source(
        "wave8_cordova_simancas_chalmeta_1976",
        "Simancas y Alhándega",
        "https://dialnet.unirioja.es/servlet/articulo?codigo=741054",
        "Hispania, CSIC",
        "peer_reviewed_source_critical_history_article",
        "chalmeta_simancas_alhandega_1976",
        outcome=True,
    ),
    _source(
        "wave8_cordova_calatanazor_castellanos_2001",
        "La batalla de Calatañazor: mito y realidad",
        (
            "https://bibliotecavirtual.defensa.gob.es/BVMDefensa/es/"
            "catalogo_imagenes/grupo.do?path=306504"
        ),
        "Revista de Historia Militar / Biblioteca Virtual de Defensa",
        "source_critical_military_history_article",
        "rhm_castellanos_calatanazor_2001",
        crosscheck=True,
    ),
    _source(
        "wave8_cordova_calatanazor_biglieri_2024",
        "En Calatañazor: microrrelato, oralidad y escritura",
        "https://topicosdelseminario.buap.mx/index.php/topsem/article/view/885",
        "Topicos del Seminario, BUAP",
        "peer_reviewed_literary_history_article",
        "biglieri_calatanazor_2024",
        crosscheck=True,
    ),
    _source(
        "wave8_cordova_zamora_molenat_2017",
        "Medieval Zamora and its Andalusi frontier chronology",
        "https://journals.openedition.org/hamsa/742?lang=en",
        "Hamsa: Journal of Judaic and Islamic Studies",
        "peer_reviewed_medieval_history_article",
        "molenat_hamsa_2017",
        crosscheck=True,
    ),
    _source(
        "wave8_cordova_zamora_fierro_2004",
        "¿Hubo propaganda fatimí entre los Kutāma andalusíes?",
        (
            "https://al-qantara.revistas.csic.es/index.php/al-qantara/"
            "article/view/155"
        ),
        "Al-Qantara, CSIC",
        "peer_reviewed_islamic_history_article",
        "fierro_kutama_2004",
        crosscheck=True,
    ),
    _source(
        "wave8_cordova_zamora_garcia_2019",
        "Atilano de Zamora: santo, obispo y profeta",
        (
            "https://hispaniasacra.revistas.csic.es/index.php/"
            "hispaniasacra/article/view/803"
        ),
        "Hispania Sacra, CSIC",
        "peer_reviewed_medieval_history_article",
        "garcia_atilano_zamora_2019",
        crosscheck=True,
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_CORDOVA_SOURCES}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: Iterable[str],
    note: str,
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
            note
            + " The identity is alias-free and inherits or transfers no Elo "
            "outside the fingerprinted event. Generic Cordova, Córdoba, "
            "Andalucía, Castile, León, or Pamplona labels resolve nowhere "
            "through this lane."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_CORDOVA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _CORDOBA_DEFENDERS,
        "Muslim garrison and defenders of Córdoba (1235-1236)",
        "city_defense_force",
        1235,
        1236,
        "Córdoba, al-Andalus",
        {
            "wave8_cordova_cordoba_museo_ejercito",
            "wave8_cordova_cordoba_rodriguez_2022",
        },
        (
            "Bounded to the garrison and urban defenders engaged by Ferdinand "
            "III's forces from the Axerquia seizure through the city's surrender."
        ),
    ),
    _entity(
        _CASTILIAN_CONTINGENT,
        "Fernán González's Castilian contingent at Simancas (939)",
        "event_bounded_military_contingent",
        939,
        939,
        "Simancas and the Duero frontier",
        {
            "wave8_cordova_simancas_ags_guide",
            "wave8_cordova_simancas_chalmeta_1976",
            "wave8_cordova_simancas_kusku_2023",
        },
        (
            "Bounded to the Castilian contingent in Ramiro II's coalition at "
            "Simancas; it is not a continuity claim for a Castilian state."
        ),
    ),
    _entity(
        _PAMPLONESE_CONTINGENT,
        "García Sánchez I's Pamplonese contingent at Simancas (939)",
        "event_bounded_military_contingent",
        939,
        939,
        "Simancas and the Duero frontier",
        {
            "wave8_cordova_simancas_ags_guide",
            "wave8_cordova_simancas_chalmeta_1976",
            "wave8_cordova_simancas_kusku_2023",
        },
        (
            "Bounded to the Pamplonese contingent in Ramiro II's coalition at "
            "Simancas; it is not the Kingdom of Pamplona in another action."
        ),
    ),
)


WAVE8_CORDOVA_REQUIRED_EXISTING_ENTITIES: dict[str, dict[str, Any]] = {
    _CROWN_CASTILE: {
        "name": "Crown of Castile",
        "kind": "composite_monarchy",
        "start_year": 1230,
        "end_year": 1715,
        "aliases": [],
    },
    _KINGDOM_LEON: {
        "name": "Kingdom of León",
        "kind": "kingdom",
        "start_year": 911,
        "end_year": 1235,
        "aliases": ["Kingdom of León"],
    },
    _CALIPHATE_CORDOBA: {
        "name": "Caliphate of Córdoba",
        "kind": "caliphate",
        "start_year": 936,
        "end_year": 1071,
        "aliases": ["Caliphate of Córdoba"],
    },
}


WAVE8_CORDOVA_ROW_HASHES: dict[str, str] = {
    "hced-Calatanazar1002-1": (
        "25ef78d0b79342984fc0c30b4ce1956d8dc02cf72e93414536e44fc7d790c230"
    ),
    "hced-Cordova1236-1": (
        "f173450a0043074a8fe105c00fbe13f8e4453fba9eba8d09e681d60478f77ab3"
    ),
    "hced-Simancas, Valladolid939-1": (
        "570456029cf11bb7bcc50bd48a555e2c219e403c79026d59faa2903c6aad51fe"
    ),
    "hced-Zamora873-1": (
        "e727c88472ee0c477d40d482816dbf9dd7bb0eccc9ca3e5e21eaefb97a4ab13a"
    ),
}


def _canonical(
    name: str,
    year_low: int,
    year_high: int,
    date_text: str,
    start_date: str,
    end_date: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{year_high}",
        "date_precision": "day_range",
        "date_text": date_text,
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": year_high,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    source_ids: Iterable[str],
    audit_note: str,
    *,
    cohort: str,
    confidence: float,
    expected_scale_level: int,
    source_date_override: bool = False,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, source_ids)))
    contract: dict[str, Any] = {
        "raw_row_sha256": WAVE8_CORDOVA_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate",
        "confidence": confidence,
        "expected_scale_level": expected_scale_level,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "date_source_ids": outcomes,
        "source_date_override": source_date_override,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_exact_historical_forces",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }
    return contract


WAVE8_CORDOVA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Simancas, Valladolid939-1": _contract(
        "hced-Simancas, Valladolid939-1",
        _canonical(
            "Battle of Simancas",
            939,
            939,
            "6-9 August 939 (11-14 August proleptic Gregorian)",
            "0939-08-11",
            "0939-08-14",
            "single_simancas_battle_without_separate_alhandega_rating",
        ),
        [_KINGDOM_LEON, _CASTILIAN_CONTINGENT, _PAMPLONESE_CONTINGENT],
        [_CALIPHATE_CORDOBA],
        {
            "wave8_cordova_simancas_ags_guide",
            "wave8_cordova_simancas_chalmeta_1976",
            "wave8_cordova_simancas_kusku_2023",
        },
        (
            "The reviewed sources support Ramiro II's Leonese-led coalition "
            "defeating Abd al-Rahman III's army over 6-9 August 939. Alhandega "
            "is not separately rated because its relationship to the pursuit "
            "and battle remains source-critically disputed."
        ),
        cohort="simancas_campaign_939",
        confidence=0.94,
        expected_scale_level=3,
    ),
    "hced-Cordova1236-1": _contract(
        "hced-Cordova1236-1",
        _canonical(
            "Siege and conquest of Córdoba",
            1235,
            1236,
            "23 December 1235-29 June 1236",
            "1235-12-30",
            "1236-07-06",
            "continuous_axerquia_assault_siege_and_city_surrender",
        ),
        [_CROWN_CASTILE],
        [_CORDOBA_DEFENDERS],
        {
            "wave8_cordova_cordoba_museo_ejercito",
            "wave8_cordova_cordoba_rodriguez_2022",
        },
        (
            "The Axerquia seizure, subsequent siege, and surrender form one "
            "continuous conquest operation. Ibn Hud's relief army withdrew "
            "without combat and receives no participant rating."
        ),
        cohort="castilian_conquest_of_cordoba_1235_1236",
        confidence=0.95,
        expected_scale_level=2,
        source_date_override=True,
    ),
}


def _terminal_exclusion(
    candidate_id: str,
    evidence_refs: Iterable[str],
    reason: str,
    note: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_CORDOVA_ROW_HASHES[candidate_id],
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "exclusion_reason": reason,
        "reviewed_outcome": "not_rateable",
        "unknown_is_never_draw": True,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "audit_note": note,
    }


WAVE8_CORDOVA_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_CORDOVA_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Calatanazar1002-1": _terminal_exclusion(
        "hced-Calatanazar1002-1",
        {
            "wave8_cordova_calatanazor_biglieri_2024",
            "wave8_cordova_calatanazor_castellanos_2001",
        },
        "late_legend_without_defensible_historical_battle",
        (
            "The Calatañazor story is first attested centuries later and contains "
            "chronological, geographical, and participant anachronisms. It is "
            "not rewritten as Cervera and emits no outcome or participants."
        ),
    ),
    "hced-Zamora873-1": _terminal_exclusion(
        "hced-Zamora873-1",
        {
            "wave8_cordova_zamora_fierro_2004",
            "wave8_cordova_zamora_garcia_2019",
            "wave8_cordova_zamora_molenat_2017",
        },
        "uncorroborated_row_conflates_later_zamora_events",
        (
            "No reviewed source corroborates an 873 battle matching the row. "
            "Zamora's rebuilding belongs around 893-894 and the documented Day "
            "of Zamora to 901, with different actors. The row is not redated."
        ),
    ),
}

WAVE8_CORDOVA_CONTRACT_IDS = frozenset(WAVE8_CORDOVA_CONTRACTS)
WAVE8_CORDOVA_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_CORDOVA_TERMINAL_EXCLUSIONS
)
WAVE8_CORDOVA_RESERVED_IDS = frozenset(
    WAVE8_CORDOVA_CONTRACT_IDS | WAVE8_CORDOVA_TERMINAL_EXCLUSION_IDS
)

WAVE8_CORDOVA_POINT_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_CORDOVA_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_CORDOVA_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {}


WAVE8_CORDOVA_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q1518266": "825a2d54d2e8a15cbb66cdd37523a0a695b9f90b3ff9611378d8cddb5be2b47d",
    "Q1807089": "a26195fac9b4779d09e6cc1ec9119dd09cd9b3ec11d5f421e221e26367099374",
    "Q12216248": "8ca97deb7677c524db65b739abfefead0a31861643d94bfd9864407ee92c37c9",
    "Q125861402": "3f578f507415483787b0b4d45612a2fa696effffa88b9a8851370343226822da",
    "Q4870264": "2fef2bea67e021025f69121a1dd0c7bf56e2d3a2431bd7418155d9fc7cfb0c14",
    "Q5242957": "aa78ac15cf7439345f9e9f1dc3db800bc19d6c6cb3c7da6c01dc195147ccc6be",
}

WAVE8_CORDOVA_DISCOVERY_EXPECTED: dict[str, dict[str, Any]] = {
    "Q1518266": {
        "name": "Battle of Simancas",
        "date": "0939-07-24T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "participant_labels": [],
        "relationship": "exact_discovery_duplicate_with_rejected_date",
        "hced_candidate_id": "hced-Simancas, Valladolid939-1",
        "disposition": "discovery_only_duplicate",
        "date_disposition": "reject_unreferenced_conflicting_date",
    },
    "Q1807089": {
        "name": "Battle of Calatañazor",
        "date": "1002-07-01T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "participant_labels": [
            "Caliphate of Córdoba",
            "County of Castilla",
            "Kingdom of Leon",
            "Kingdom of Pamplona",
        ],
        "relationship": "exact_legendary_concept_twin",
        "hced_candidate_id": "hced-Calatanazar1002-1",
        "disposition": "discovery_only_terminally_excluded_concept",
        "date_disposition": "nonrating_legendary_date",
    },
    "Q12216248": {
        "name": "Siege of Córdoba",
        "date": "1235-12-30T00:00:00Z",
        "end_date": "1236-07-06T00:00:00Z",
        "kind": "siege",
        "participant_labels": [
            "Crown of Castile",
            "Taifa of Córdoba",
            "Taifa of Murcia",
        ],
        "relationship": "exact_discovery_duplicate",
        "hced_candidate_id": "hced-Cordova1236-1",
        "disposition": "discovery_only_duplicate",
        "date_disposition": "corroborating_range_only",
    },
    "Q125861402": {
        "name": "Battle of Alhandega",
        "date": "0939-08-01T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "participant_labels": ["Caliphate of Córdoba", "Kingdom of Leon"],
        "relationship": "adjacent_disputed_simancas_phase",
        "hced_candidate_id": "hced-Simancas, Valladolid939-1",
        "disposition": "discovery_only_adjudication_hold",
        "date_disposition": "unadopted_disputed_date",
    },
    "Q4870264": {
        "name": "Battle of Alhandic",
        "date": "0939-08-10T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "participant_labels": ["Caliphate of Córdoba", "Kingdom of Leon"],
        "relationship": "adjacent_probable_simancas_duplicate",
        "hced_candidate_id": "hced-Simancas, Valladolid939-1",
        "disposition": "discovery_only_adjudication_hold",
        "date_disposition": "unadopted_disputed_date",
    },
    "Q5242957": {
        "name": "Day of Zamora",
        "date": "0901-07-01T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "participant_labels": [],
        "relationship": "distinct_901_event_not_the_873_row",
        "hced_candidate_id": "hced-Zamora873-1",
        "disposition": "discovery_only_distinct_staged_event",
        "date_disposition": "retain_separately_staged",
    },
}

WAVE8_CORDOVA_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "source_dataset": "wikidata-battles",
        "disposition": expected["disposition"],
        "relationship": expected["relationship"],
        "hced_candidate_id": expected["hced_candidate_id"],
        "date_disposition": expected["date_disposition"],
        "outcome_disposition": "unknown_never_draw",
    }
    for candidate_id, expected in sorted(WAVE8_CORDOVA_DISCOVERY_EXPECTED.items())
}


WAVE8_CORDOVA_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "cordova": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "783a55177cd006c203675efb661939d29513cf21507c1ea4bdc766ea8852bbc0"
        ),
        "events_touched": 3,
        "sole_blocker_events": 2,
        "unresolved_side_attempts": 3,
        "zero_time_valid_candidates": 3,
    },
    "andalucia": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "2294ac22111e8134046e29eae76fc305e0f66bc8e356173f44482a4361d56155"
        ),
        "events_touched": 2,
        "sole_blocker_events": 1,
        "unresolved_side_attempts": 2,
        "zero_time_valid_candidates": 2,
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_CORDOVA_CONTRACTS,
        "discovery_expected": WAVE8_CORDOVA_DISCOVERY_EXPECTED,
        "discovery_row_hashes": WAVE8_CORDOVA_DISCOVERY_ROW_HASHES,
        "entities": WAVE8_CORDOVA_ENTITIES,
        "funnel": WAVE8_CORDOVA_FUNNEL_AUDIT,
        "holds": WAVE8_CORDOVA_HOLDS,
        "integration_dispositions": WAVE8_CORDOVA_INTEGRATION_DISPOSITIONS,
        "location_reasons": WAVE8_CORDOVA_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_CORDOVA_ROW_HASHES,
        "sources": WAVE8_CORDOVA_SOURCES,
        "terminal_exclusions": WAVE8_CORDOVA_TERMINAL_EXCLUSIONS,
    }


def wave8_cordova_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_CORDOVA_FINAL_AUDIT_SIGNATURE = (
    "92afa442ef9e36650c43743da0d86549ed2ef9e041924bf10a194f1bb1969f66"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_CORDOVA_CONTRACTS), len(WAVE8_CORDOVA_TERMINAL_EXCLUSIONS)) != (
        2,
        2,
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if WAVE8_CORDOVA_RESERVED_IDS != set(WAVE8_CORDOVA_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} reservation inventory changed")
    if WAVE8_CORDOVA_HOLDS:
        raise ValueError(f"{_LANE_NAME} acquired an unresolved HCED hold")
    if (
        WAVE8_CORDOVA_POINT_QUARANTINE_ADDITIONS
        or WAVE8_CORDOVA_COUNTRY_QUARANTINE_ADDITIONS
        or WAVE8_CORDOVA_LOCATION_QUARANTINE_REASONS
    ):
        raise ValueError(f"{_LANE_NAME} acquired a location quarantine")

    source_ids = set(_SOURCE_BY_ID)
    source_families = {
        str(source["source_family_id"]) for source in WAVE8_CORDOVA_SOURCES
    }
    if len(source_ids) != 10 or len(source_families) != 10:
        raise ValueError(f"{_LANE_NAME} source-family inventory changed")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_CORDOVA_ENTITIES}
    if len(entity_by_id) != 3:
        raise ValueError(f"{_LANE_NAME} exact entity inventory changed")
    used_sources: set[str] = set()
    used_new_entities: set[str] = set()
    allowed_entities = set(entity_by_id) | set(WAVE8_CORDOVA_REQUIRED_EXISTING_ENTITIES)
    for entity in WAVE8_CORDOVA_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} installed an alias or continuity bridge")
        refs = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(refs) or not set(refs) <= source_ids:
            raise ValueError(f"{_LANE_NAME} entity evidence changed")
        used_sources.update(refs)

    for candidate_id, contract in WAVE8_CORDOVA_CONTRACTS.items():
        if (
            contract["raw_row_sha256"] != WAVE8_CORDOVA_ROW_HASHES[candidate_id]
            or contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome contract changed: {candidate_id}")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} invalid sides: {candidate_id}")
        if not (side_1 | side_2) <= allowed_entities:
            raise ValueError(f"{_LANE_NAME} unknown participant: {candidate_id}")
        used_new_entities.update((side_1 | side_2) & set(entity_by_id))
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if (
            not _is_sorted_unique(evidence)
            or not _is_sorted_unique(outcomes)
            or set(outcomes) != set(evidence)
            or not set(evidence) <= source_ids
            or contract["outcome_source_family_ids"] != families
            or len(families) < 2
        ):
            raise ValueError(f"{_LANE_NAME} evidence closure changed: {candidate_id}")
        canonical = contract["canonical_event"]
        if (
            canonical["date_precision"] != "day_range"
            or not canonical["start_date"]
            or not canonical["end_date"]
        ):
            raise ValueError(f"{_LANE_NAME} exact date changed: {candidate_id}")
        used_sources.update(evidence)

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entity fixture is not exactly consumed")
    for candidate_id, exclusion in WAVE8_CORDOVA_TERMINAL_EXCLUSIONS.items():
        if (
            exclusion["raw_row_sha256"] != WAVE8_CORDOVA_ROW_HASHES[candidate_id]
            or exclusion["disposition"] != "terminal_exclusion"
            or exclusion["terminal_exclusion"] is not True
            or exclusion["unknown_is_never_draw"] is not True
            or {"result_type", "winner_side", "side_1_entity_ids", "side_2_entity_ids"}
            & set(exclusion)
        ):
            raise ValueError(f"{_LANE_NAME} exclusion changed: {candidate_id}")
        refs = list(map(str, exclusion["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= source_ids:
            raise ValueError(f"{_LANE_NAME} exclusion evidence changed: {candidate_id}")
        used_sources.update(refs)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if set(WAVE8_CORDOVA_DISCOVERY_EXPECTED) != set(
        WAVE8_CORDOVA_DISCOVERY_ROW_HASHES
    ) or set(WAVE8_CORDOVA_INTEGRATION_DISPOSITIONS) != set(
        WAVE8_CORDOVA_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} discovery inventory changed")
    if any(
        item["outcome_disposition"] != "unknown_never_draw"
        for item in WAVE8_CORDOVA_INTEGRATION_DISPOSITIONS.values()
    ):
        raise ValueError(f"{_LANE_NAME} discovery outcome guard changed")
    if wave8_cordova_audit_signature() != WAVE8_CORDOVA_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def _is_lane_row(row: Mapping[str, Any]) -> bool:
    return (
        normalize_label(row.get("side_1_raw")) == "cordova"
        or normalize_label(row.get("side_2_raw")) == "cordova"
        or normalize_label(row.get("name")) == "cordova"
    )


def validate_wave8_cordova_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [row for row in hced_rows if _is_lane_row(row)]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_CORDOVA_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact inventory changed: {sorted(exact_ids)}")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_CORDOVA_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("do_not_rate_automatically") is not True
        ):
            raise ValueError(f"{_LANE_NAME} source outcome guard changed: {candidate_id}")
    for candidate_id in WAVE8_CORDOVA_CONTRACT_IDS:
        row = by_id[candidate_id]
        if (
            row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
        ):
            raise ValueError(f"{_LANE_NAME} promoted outcome alignment changed")
    validate_exact_hced_inventory(
        hced_rows,
        WAVE8_CORDOVA_CONTRACTS,
        WAVE8_CORDOVA_TERMINAL_EXCLUSIONS,
        lane_name=_LANE_NAME,
    )
    return {
        "exact_rows": len(exact),
        "holds": 0,
        "promotion_contracts": len(WAVE8_CORDOVA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_CORDOVA_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_CORDOVA_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_cordova_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    by_label = {str(row.get("label")): row for row in funnel.get("labels", [])}
    for label, expected in WAVE8_CORDOVA_FUNNEL_AUDIT.items():
        row = by_label.get(label)
        if row is None:
            raise ValueError(f"{_LANE_NAME} missing historical funnel label: {label}")
        actual = {
            "candidate_ids": list(map(str, row.get("candidate_ids", []))),
            "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
            "events_touched": int(row.get("events_touched", -1)),
            "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
            "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
            "zero_time_valid_candidates": int(
                row.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
            ),
        }
        if actual != expected:
            raise ValueError(f"{_LANE_NAME} funnel pin changed for {label}: {actual}")
    return {
        "events_touched": sum(
            row["events_touched"] for row in WAVE8_CORDOVA_FUNNEL_AUDIT.values()
        ),
        "labels": len(WAVE8_CORDOVA_FUNNEL_AUDIT),
        "sole_blocker_events": sum(
            row["sole_blocker_events"] for row in WAVE8_CORDOVA_FUNNEL_AUDIT.values()
        ),
    }


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def validate_wave8_cordova_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in WAVE8_CORDOVA_DISCOVERY_ROW_HASHES.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} discovery row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}")
        expected = WAVE8_CORDOVA_DISCOVERY_EXPECTED[candidate_id]
        labels = sorted(
            normalize_label(participant.get("label"))
            for participant in row.get("participants", [])
        )
        expected_labels = sorted(
            normalize_label(label) for label in expected["participant_labels"]
        )
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("winners") != []
            or row.get("name") != expected["name"]
            or row.get("date") != expected["date"]
            or row.get("end_date") != expected["end_date"]
            or row.get("kind") != expected["kind"]
            or labels != expected_labels
        ):
            raise ValueError(
                f"{_LANE_NAME} discovery nonrating guard changed: {candidate_id}"
            )
    return {
        "discovery_nonrating_records": len(WAVE8_CORDOVA_DISCOVERY_ROW_HASHES),
        "discovery_promotions": 0,
        "distinct_staged_records": 1,
        "exact_twins": 3,
        "source_critical_holds": 2,
        "unknown_never_draw_rows": len(WAVE8_CORDOVA_DISCOVERY_ROW_HASHES),
    }


def validate_wave8_cordova_existing_entities(
    release_entities: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    for entity_id, expected in WAVE8_CORDOVA_REQUIRED_EXISTING_ENTITIES.items():
        entity = release_entities.get(entity_id)
        if entity is None:
            raise ValueError(f"{_LANE_NAME} missing existing identity: {entity_id}")
        actual = {key: entity.get(key) for key in expected}
        normalized_actual = {
            **actual,
            "name": normalize_label(actual["name"]),
            "aliases": [normalize_label(alias) for alias in actual["aliases"]],
        }
        normalized_expected = {
            **expected,
            "name": normalize_label(expected["name"]),
            "aliases": [normalize_label(alias) for alias in expected["aliases"]],
        }
        if normalized_actual != normalized_expected:
            raise ValueError(f"{_LANE_NAME} existing identity drift: {entity_id}")
    return {"required_existing_entities": len(WAVE8_CORDOVA_REQUIRED_EXISTING_ENTITIES)}


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Calatanazar1002-1": {
        "Calatanazar",
        "Calatañazor",
        "Battle of Calatañazor",
    },
    "hced-Cordova1236-1": {
        "Cordova",
        "Siege of Córdoba",
        "Siege and conquest of Córdoba",
    },
    "hced-Simancas, Valladolid939-1": {
        "Simancas",
        "Simancas, Valladolid",
        "Battle of Simancas",
    },
    "hced-Zamora873-1": {"Zamora", "Battle of Zamora"},
}


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "batyear"):
        try:
            if row.get(key) is not None:
                return int(row[key])
        except (TypeError, ValueError):
            pass
    for key in ("start_date", "date"):
        value = str(row.get(key) or "")
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names: set[str] = set()
    for key in ("name", "battle_name", "batname", "event_name"):
        value = normalize_label(row.get(key))
        if value:
            names.add(value)
    for value in row.get("aliases", []) or []:
        normalized = normalize_label(value)
        if normalized:
            names.add(normalized)
    return names


_DUPLICATE_YEARS: dict[str, tuple[int, int]] = {
    "hced-Calatanazar1002-1": (1002, 1002),
    "hced-Cordova1236-1": (1235, 1236),
    "hced-Simancas, Valladolid939-1": (939, 939),
    "hced-Zamora873-1": (873, 873),
}
_DUPLICATE_WINDOWS: tuple[tuple[int, int, frozenset[str]], ...] = tuple(
    _DUPLICATE_YEARS[candidate_id]
    + (frozenset(normalize_label(alias) for alias in aliases),)
    for candidate_id, aliases in _EVENT_ALIASES.items()
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    names = _row_names(row)
    return year is not None and any(
        low <= year <= high and bool(names & aliases)
        for low, high, aliases in _DUPLICATE_WINDOWS
    )


def validate_wave8_cordova_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_cordova_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_CORDOVA_RESERVED_IDS
        and _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_CORDOVA_CONTRACT_IDS
        and _is_probable_twin(event)
    )
    if hced_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"iwbd={iwbd_twins}, release={release_twins}"
        )
    return {
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_cordova_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    validate_wave8_cordova_existing_entities(release_entities)
    install_exact_entities(
        release_entities,
        WAVE8_CORDOVA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_cordova_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_CORDOVA_SOURCES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_cordova_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_cordova_queue_contracts(hced_rows)
    validate_wave8_cordova_existing_entities(release_entities)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_CORDOVA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        canonical = WAVE8_CORDOVA_CONTRACTS[candidate_id]["canonical_event"]
        event["aliases"] = []
        event["date_interval"] = {
            "start": str(canonical["start_date"]),
            "end": str(canonical["end_date"]),
        }
    return events


def wave8_cordova_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_CORDOVA_CONTRACTS.values()
            ).items()
        )
    )


def wave8_cordova_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "discovery_nonrating_records": len(WAVE8_CORDOVA_DISCOVERY_ROW_HASHES),
        "holds": 0,
        "integration_dispositions": len(WAVE8_CORDOVA_INTEGRATION_DISPOSITIONS),
        "new_entities": len(WAVE8_CORDOVA_ENTITIES),
        "new_sources": len(WAVE8_CORDOVA_SOURCES),
        "newly_rated_events": len(WAVE8_CORDOVA_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": 0,
        "promotion_contracts": len(WAVE8_CORDOVA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_CORDOVA_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_CORDOVA_TERMINAL_EXCLUSIONS),
        "unknown_discovery_outcomes": len(WAVE8_CORDOVA_DISCOVERY_ROW_HASHES),
    }


def wave8_cordova_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_cordova_counts(),
        "cohorts": wave8_cordova_cohort_counts(),
        "discovery_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_CORDOVA_INTEGRATION_DISPOSITIONS.items()
            )
        ],
        "final_audit_signature": WAVE8_CORDOVA_FINAL_AUDIT_SIGNATURE,
        "hold_candidate_ids": [],
        "promoted_candidate_ids": sorted(WAVE8_CORDOVA_CONTRACT_IDS),
        "terminal_exclusion_candidate_ids": sorted(
            WAVE8_CORDOVA_TERMINAL_EXCLUSION_IDS
        ),
    }


_validate_static()
