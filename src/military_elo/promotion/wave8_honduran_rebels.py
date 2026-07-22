"""Fail-closed candidate audit of HCED's five Honduran-rebel rows.

The raw labels ``Honduran Rebels``, ``Honduran Government``, and
``Nicaragua, Honduran Rebels`` span unrelated forces over eighty years.  This
lane therefore promotes only three fingerprinted events and installs seven
alias-free, event- or conflict-bounded actors.  No broad label becomes an
alias and no rating flows to the enduring Honduras polity.

The Choluteca row collapses two separately dated actions and reverses their
reviewed result.  The San Marcos row cannot yet be bound safely to the Rio San
Marcos or Naranjo chronologies.  Both remain explicit unknown holds; unknown
is never converted to a draw.  The related La Esperanza HCED row, two IWBD
rows, and two Brecke parent-war records are discovery/coverage records only.
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
    "WAVE8_HONDURAN_REBELS_CONTRACT_IDS",
    "WAVE8_HONDURAN_REBELS_CONTRACTS",
    "WAVE8_HONDURAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_HONDURAN_REBELS_DISCOVERY_EXPECTED",
    "WAVE8_HONDURAN_REBELS_DISCOVERY_TWINS",
    "WAVE8_HONDURAN_REBELS_ENTITIES",
    "WAVE8_HONDURAN_REBELS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_HONDURAN_REBELS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_HONDURAN_REBELS_FUNNEL_AUDITS",
    "WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES",
    "WAVE8_HONDURAN_REBELS_HOLD_IDS",
    "WAVE8_HONDURAN_REBELS_HOLDS",
    "WAVE8_HONDURAN_REBELS_INTEGRATION_DISPOSITIONS",
    "WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES",
    "WAVE8_HONDURAN_REBELS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_EXPECTED",
    "WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_ROW_HASHES",
    "WAVE8_HONDURAN_REBELS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_HONDURAN_REBELS_RELATED_EVENT_BOUNDARIES",
    "WAVE8_HONDURAN_REBELS_REQUIRED_EXISTING_ENTITIES",
    "WAVE8_HONDURAN_REBELS_RESERVED_IDS",
    "WAVE8_HONDURAN_REBELS_ROW_HASHES",
    "WAVE8_HONDURAN_REBELS_SOURCES",
    "install_wave8_honduran_rebels_entities",
    "install_wave8_honduran_rebels_sources",
    "promote_wave8_honduran_rebels_contracts",
    "validate_wave8_honduran_rebels_current_artifact_state",
    "validate_wave8_honduran_rebels_discovery_dispositions",
    "validate_wave8_honduran_rebels_existing_entities",
    "validate_wave8_honduran_rebels_funnel",
    "validate_wave8_honduran_rebels_integration_dispositions",
    "validate_wave8_honduran_rebels_parent_coverage",
    "validate_wave8_honduran_rebels_queue_contracts",
    "wave8_honduran_rebels_audit_signature",
    "wave8_honduran_rebels_cohort_counts",
    "wave8_honduran_rebels_counts",
    "wave8_honduran_rebels_location_quarantine_additions",
    "wave8_honduran_rebels_metadata",
)


_LANE_NAME = "Wave 8 exact Honduran rebels audit"
_MODULE_OWNER = "military_elo.promotion.wave8_honduran_rebels"
_EVENT_ID_PREFIX = "hced_wave8_honduran_rebels_"
_EXACT_LABEL = "honduran rebels"
_COMPOSITE_LABEL = "nicaragua honduran rebels"
_AUDITED_LABELS = frozenset({_EXACT_LABEL, _COMPOSITE_LABEL})

_HONDURAS = "clio_q783_1840_cd44c8fd"
_DANLI_GOVERNMENT = "ferrera_division_of_operations_danli_1844"
_DANLI_LIBERATOR = "patricio_jimenez_liberator_division_danli_1844"
_ORTIZ_EXPEDITION = "anastasio_ortiz_nicaraguan_expedition_1893_1894"
_BONILLA_LIBERALS = "policarpo_bonilla_liberal_revolutionary_force_1893_1894"
_VASQUEZ_DEFENDERS = "domingo_vasquez_tegucigalpa_defense_force_1894"
_REVOLUTIONARY_COLUMNS_1924 = (
    "ferrera_tosta_martinez_funes_tegucigalpa_force_1924"
)
_COUNCIL_DEFENDERS_1924 = "council_of_ministers_tegucigalpa_defense_force_1924"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    direct_outcome: bool,
) -> dict[str, Any]:
    roles = {
        "identity_boundary_or_context_reference",
        "outcome_consistency_crosscheck",
    }
    if direct_outcome:
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


WAVE8_HONDURAN_REBELS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_honduran_rebels_garcia_buchard_1839_1845",
        (
            "Las disputas por el poder durante la primera etapa del proceso de "
            "construcción estatal en Honduras (1839–1845)"
        ),
        "https://dialnet.unirioja.es/descarga/articulo/5089074.pdf",
        "Intercambio, Universidad de Costa Rica",
        "scholarly_journal_article",
        "ucr_intercambio",
        direct_outcome=True,
    ),
    _source(
        "wave8_honduran_rebels_ariel_233_danli",
        (
            "Revista ARIEL No. 233: documentos judiciales y militares de Danlí "
            "y Texíguat"
        ),
        (
            "https://tzibalnaah.unah.edu.hn/bitstream/handle/123456789/16923/"
            "No.233.abr1971.pdf?isAllowed=y&sequence=1"
        ),
        "Tz'ibal Naah, Universidad Nacional Autónoma de Honduras",
        "digitized_archival_facsimile",
        "unah_archival_facsimiles",
        direct_outcome=True,
    ),
    _source(
        "wave8_honduran_rebels_secapph_el_paraiso",
        "Reseña histórica y geográfica del naciente pueblo de El Paraíso",
        (
            "https://secapph.gob.hn/wp-content/uploads/2025/06/"
            "RESENA-HISTORICA-Y-GEOGRAFICA-DEL-NACIENTE-PUEBLO-DEL-PARAISO.pdf"
        ),
        "Secretaria de las Culturas, las Artes y los Patrimonios de Honduras",
        "official_historical_monograph",
        "honduras_secapph",
        direct_outcome=True,
    ),
    _source(
        "wave8_honduran_rebels_bancroft_central_america_v3",
        "History of Central America, Volume III, 1801-1887",
        "https://www.gutenberg.org/files/62657/62657-h/62657-h.htm",
        "A. L. Bancroft and Company; Project Gutenberg edition",
        "scholarly_historical_monograph",
        "bancroft_central_america",
        direct_outcome=True,
    ),
    _source(
        "wave8_honduran_rebels_yoro_monograph",
        "Monografía del departamento de Yoro",
        (
            "https://www.cervantesvirtual.com/descargaPdf/"
            "monografia-del-departamento-de-yoro/"
        ),
        "Biblioteca Virtual Miguel de Cervantes",
        "digitized_honduran_departmental_monograph",
        "unah_departmental_monographs",
        direct_outcome=True,
    ),
    _source(
        "wave8_honduran_rebels_frus_1894_d295",
        "Foreign Relations of the United States, 1894, Document 295",
        "https://history.state.gov/historicaldocuments/frus1894/d295",
        "Office of the Historian, U.S. Department of State",
        "edited_primary_diplomatic_document",
        "us_state_frus_1894",
        direct_outcome=True,
    ),
    _source(
        "wave8_honduran_rebels_frus_1894_d307",
        "Foreign Relations of the United States, 1894, Document 307",
        "https://history.state.gov/historicaldocuments/frus1894/d307",
        "Office of the Historian, U.S. Department of State",
        "edited_primary_diplomatic_document",
        "us_state_frus_1894",
        direct_outcome=True,
    ),
    _source(
        "wave8_honduran_rebels_becerra_evolucion_historica",
        "Evolución histórica de Honduras",
        (
            "https://es.scribd.com/document/498046397/"
            "Evolucion-Historica-de-Honduras-Longino-Becerra"
        ),
        "Longino Becerra; digitized edition",
        "historical_monograph",
        "becerra_honduran_history",
        direct_outcome=True,
    ),
    _source(
        "wave8_honduran_rebels_sedesol_civil_war_1924",
        "La guerra civil de 1924 en Honduras",
        (
            "https://chepes.sedesol.gob.hn/wp-content/uploads/2025/09/"
            "LB016_La_guerra_civil_1924_en_Honduras_CHEPES_24-09-2025.pdf"
        ),
        "Editorial SEDESOL; ed. Yesenia Martínez García",
        "official_edited_historical_monograph",
        "sedesol_chepes_1924",
        direct_outcome=True,
    ),
    _source(
        "wave8_honduran_rebels_us_navy_expeditions_1901_1929",
        "List of Expeditions, 1901-1929",
        (
            "https://www.history.navy.mil/research/library/online-reading-room/"
            "title-list-alphabetically/l/list-of-expeditions-1901-1929.html"
        ),
        "Naval History and Heritage Command",
        "official_military_operations_reference",
        "us_navy_expedition_records",
        direct_outcome=False,
    ),
    _source(
        "wave8_honduran_rebels_frus_1924_d261",
        "Foreign Relations of the United States, 1924, Volume II, Document 261",
        "https://history.state.gov/historicaldocuments/frus1924v02/d261",
        "Office of the Historian, U.S. Department of State",
        "edited_primary_diplomatic_document",
        "us_state_frus_1924",
        direct_outcome=True,
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_HONDURAN_REBELS_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: Iterable[str],
    continuity_note: str,
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
        "continuity_note": continuity_note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_HONDURAN_REBELS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _DANLI_GOVERNMENT,
        "Ferrera government Division of Operations at Danlí",
        "event_bounded_government_field_force",
        1844,
        1844,
        "Danlí, Honduras",
        (
            "wave8_honduran_rebels_ariel_233_danli",
            "wave8_honduran_rebels_garcia_buchard_1839_1845",
            "wave8_honduran_rebels_secapph_el_paraiso",
        ),
        (
            "Only Francisco Ferrera's government Division of Operations in the "
            "20 December 1844 Danlí action. It inherits no rating from Honduras, "
            "a generic Honduran Government label, or Ferrera's forces elsewhere."
        ),
    ),
    _entity(
        _DANLI_LIBERATOR,
        "Patricio Jiménez’s Ejército Libertador division at Danlí",
        "event_bounded_rebel_field_force",
        1844,
        1844,
        "Danlí, Honduras",
        (
            "wave8_honduran_rebels_ariel_233_danli",
            "wave8_honduran_rebels_garcia_buchard_1839_1845",
            "wave8_honduran_rebels_secapph_el_paraiso",
        ),
        (
            "Only Patricio Jiménez’s Ejército Libertador division engaged at "
            "Danlí. It inherits no rating from a generic Honduran Rebels label, "
            "other anti-Ferrera forces, or later Honduran revolutions."
        ),
    ),
    _entity(
        _ORTIZ_EXPEDITION,
        "Nicaraguan expeditionary force under Anastasio Ortiz in Honduras",
        "conflict_bounded_foreign_expeditionary_force",
        1893,
        1894,
        "Honduras",
        (
            "wave8_honduran_rebels_becerra_evolucion_historica",
            "wave8_honduran_rebels_frus_1894_d295",
            "wave8_honduran_rebels_frus_1894_d307",
        ),
        (
            "Only Anastasio Ortiz's Nicaraguan expedition in the 1893-1894 "
            "Honduran revolution. It inherits no rating from Nicaragua generally, "
            "a combined Nicaragua-Honduran Rebels label, or later expeditions."
        ),
    ),
    _entity(
        _BONILLA_LIBERALS,
        "Policarpo Bonilla’s Honduran Liberal revolutionary force",
        "conflict_bounded_liberal_revolutionary_force",
        1893,
        1894,
        "Honduras",
        (
            "wave8_honduran_rebels_becerra_evolucion_historica",
            "wave8_honduran_rebels_frus_1894_d295",
            "wave8_honduran_rebels_frus_1894_d307",
        ),
        (
            "Only Policarpo Bonilla’s organized Liberal revolutionary force in "
            "the 1893-1894 campaign. It inherits no rating from the Liberal Party, "
            "a generic Honduran Rebels label, or later Bonilla governments."
        ),
    ),
    _entity(
        _VASQUEZ_DEFENDERS,
        "Domingo Vásquez government force defending Tegucigalpa",
        "event_bounded_government_defense_force",
        1894,
        1894,
        "Tegucigalpa, Honduras",
        (
            "wave8_honduran_rebels_becerra_evolucion_historica",
            "wave8_honduran_rebels_frus_1894_d295",
            "wave8_honduran_rebels_frus_1894_d307",
        ),
        (
            "Only Domingo Vásquez’s loyal force defending Tegucigalpa in January-"
            "February 1894. It inherits no rating from Honduras, a generic "
            "Honduran Government label, or other Vasquez forces."
        ),
    ),
    _entity(
        _REVOLUTIONARY_COLUMNS_1924,
        "Ferrera–Tosta–Martínez Funes revolutionary columns at Tegucigalpa",
        "event_bounded_revolutionary_assault_force",
        1924,
        1924,
        "Tegucigalpa, Honduras",
        (
            "wave8_honduran_rebels_frus_1924_d261",
            "wave8_honduran_rebels_sedesol_civil_war_1924",
        ),
        (
            "Only the Ferrera, Tosta, and Martínez Funes columns in the final "
            "27-28 April assault on Tegucigalpa. It inherits no rating from a "
            "generic Honduran Rebels label or any later claimant coalition."
        ),
    ),
    _entity(
        _COUNCIL_DEFENDERS_1924,
        "Council of Ministers loyalist defense force at Tegucigalpa",
        "event_bounded_loyalist_defense_force",
        1924,
        1924,
        "Tegucigalpa, Honduras",
        (
            "wave8_honduran_rebels_frus_1924_d261",
            "wave8_honduran_rebels_sedesol_civil_war_1924",
            "wave8_honduran_rebels_us_navy_expeditions_1901_1929",
        ),
        (
            "Only the Council of Ministers' loyalist defenders in the final "
            "Tegucigalpa assault. It inherits no rating from Honduras, a generic "
            "Honduran Government label, or U.S. protective detachments."
        ),
    ),
)

_ENTITY_BY_ID = {
    str(entity["id"]): entity for entity in WAVE8_HONDURAN_REBELS_ENTITIES
}


WAVE8_HONDURAN_REBELS_REQUIRED_EXISTING_ENTITIES: dict[str, dict[str, Any]] = {
    _HONDURAS: {
        "name": "Honduras",
        "kind": "polity",
        "start_year": 1840,
        "end_year": 2024,
        "aliases": ["Honduras"],
    }
}


WAVE8_HONDURAN_REBELS_ROW_HASHES: dict[str, str] = {
    "hced-Choluteca1894-1": (
        "a56d0d5710c6179db1bed371af4792c01db969757a518c9577428c3ac1b9ea71"
    ),
    "hced-Danli1844-1": (
        "c78a8296542fdb0c6c54bf49cee1243ca7cb428c8249062e706717286e80b9fe"
    ),
    "hced-San Marcos, Honduras1876-1": (
        "925128e76d54310d6d22fdc18e26b66e80801169d19e0fd4e29c24759bb3afcb"
    ),
    "hced-Tegucicalpa1894-1": (
        "07be61d8d8887f09cf4957f4e0113d72fafbdf3a2aa7be0e318e53caf181edc8"
    ),
    "hced-Tegucicalpa1924-1": (
        "11d7a09cf923c6278be801f9fba863841277ac4521caa7213657b24a49b319f2"
    ),
}
WAVE8_HONDURAN_REBELS_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_HONDURAN_REBELS_ROW_HASHES
)


WAVE8_HONDURAN_REBELS_FUNNEL_AUDITS: dict[str, dict[str, Any]] = {
    _EXACT_LABEL: {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "9a5e364cbe3cb795aa6211b084c9ef26afc3f6ebde627a54215f6ea874f1708b"
        ),
        "events_touched": 3,
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 3,
        },
        "label": _EXACT_LABEL,
        "rated_counterpart_entities": 1,
        "sole_blocker_events": 2,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 3,
    },
    _COMPOSITE_LABEL: {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "8f7255804d49d90e81cad91277a71a702b082a94578022d32196ea002079195d"
        ),
        "events_touched": 2,
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 2,
        },
        "label": _COMPOSITE_LABEL,
        "rated_counterpart_entities": 1,
        "sole_blocker_events": 2,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 2,
    },
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    start_date: str,
    end_date: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "day" if start_date == end_date else "day_range",
        "date_text": date_text,
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


_EVENT_EVIDENCE: dict[str, dict[str, tuple[str, ...]]] = {
    "hced-Danli1844-1": {
        "evidence": (
            "wave8_honduran_rebels_ariel_233_danli",
            "wave8_honduran_rebels_garcia_buchard_1839_1845",
            "wave8_honduran_rebels_secapph_el_paraiso",
        ),
        "dates": (
            "wave8_honduran_rebels_ariel_233_danli",
            "wave8_honduran_rebels_garcia_buchard_1839_1845",
        ),
        "outcomes": (
            "wave8_honduran_rebels_ariel_233_danli",
            "wave8_honduran_rebels_garcia_buchard_1839_1845",
            "wave8_honduran_rebels_secapph_el_paraiso",
        ),
    },
    "hced-Tegucicalpa1894-1": {
        "evidence": (
            "wave8_honduran_rebels_becerra_evolucion_historica",
            "wave8_honduran_rebels_frus_1894_d295",
            "wave8_honduran_rebels_frus_1894_d307",
        ),
        "dates": (
            "wave8_honduran_rebels_becerra_evolucion_historica",
            "wave8_honduran_rebels_frus_1894_d295",
            "wave8_honduran_rebels_frus_1894_d307",
        ),
        "outcomes": (
            "wave8_honduran_rebels_becerra_evolucion_historica",
            "wave8_honduran_rebels_frus_1894_d295",
            "wave8_honduran_rebels_frus_1894_d307",
        ),
    },
    "hced-Tegucicalpa1924-1": {
        "evidence": (
            "wave8_honduran_rebels_frus_1924_d261",
            "wave8_honduran_rebels_sedesol_civil_war_1924",
            "wave8_honduran_rebels_us_navy_expeditions_1901_1929",
        ),
        "dates": ("wave8_honduran_rebels_sedesol_civil_war_1924",),
        "outcomes": (
            "wave8_honduran_rebels_frus_1924_d261",
            "wave8_honduran_rebels_sedesol_civil_war_1924",
        ),
    },
}


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    war_type: str,
    actor_override: str,
    audit_note: str,
    *,
    parent_coverage_ids: Iterable[str] = (),
    excluded_participant_labels: Iterable[str] = (),
) -> dict[str, Any]:
    evidence = sorted(set(_EVENT_EVIDENCE[candidate_id]["evidence"]))
    dates = sorted(set(_EVENT_EVIDENCE[candidate_id]["dates"]))
    outcomes = sorted(set(_EVENT_EVIDENCE[candidate_id]["outcomes"]))
    role_map: dict[str, list[str]] = {}
    for source_id in evidence:
        roles = {"exact_actor_boundary"}
        if source_id in dates:
            roles.add("exact_event_date")
        if source_id in outcomes:
            roles.add("tactical_outcome")
        if (
            candidate_id == "hced-Tegucicalpa1924-1"
            and source_id
            == "wave8_honduran_rebels_us_navy_expeditions_1901_1929"
        ):
            roles.add("united_states_non_belligerent_boundary")
        role_map[source_id] = sorted(roles)
    return {
        "raw_row_sha256": WAVE8_HONDURAN_REBELS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1_entity_ids)),
        "side_2_entity_ids": list(map(str, side_2_entity_ids)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": 0.96,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "event_evidence_roles": role_map,
        "date_source_ids": dates,
        "source_date_refinement": True,
        "source_date_override": False,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": actor_override,
        "expected_scale_level": 2,
        "parent_coverage_ids": sorted(set(map(str, parent_coverage_ids))),
        "excluded_participant_labels": sorted(
            set(map(str, excluded_participant_labels))
        ),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_HONDURAN_REBELS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Danli1844-1": _contract(
        "hced-Danli1844-1",
        _canonical(
            "Battle of Danlí",
            1844,
            "20 December 1844",
            "1844-12-20",
            "1844-12-20",
            "single_decisive_battle",
        ),
        "honduran_internal_conflict_1844",
        (_DANLI_GOVERNMENT,),
        (_DANLI_LIBERATOR,),
        "internal_rebellion",
        "ferrera_division_vs_patricio_jimenez_liberator_division",
        (
            "The scholarly reconstruction, archival facsimiles, and Honduran "
            "local history identify the 20 December Danlí battle and Ferrera "
            "government victory. The actors are bounded to the engaged divisions; "
            "the broad government and rebel labels are not aliases."
        ),
        parent_coverage_ids=("brecke-2299",),
    ),
    "hced-Tegucicalpa1894-1": _contract(
        "hced-Tegucicalpa1894-1",
        _canonical(
            "Siege and capture of Tegucigalpa",
            1894,
            "23 January-22 February 1894",
            "1894-01-23",
            "1894-02-22",
            "siege_and_capital_capture",
        ),
        "honduran_liberal_revolution_1893_1894",
        (_ORTIZ_EXPEDITION, _BONILLA_LIBERALS),
        (_VASQUEZ_DEFENDERS,),
        "intrastate_with_foreign_intervention",
        "ortiz_expedition_and_bonilla_liberals_vs_vasquez_defenders",
        (
            "The diplomatic record and Honduran history distinguish the month-long "
            "Tegucigalpa siege from the earlier Choluteca actions and record the "
            "Ortiz-Bonilla coalition's capture of the capital. Nicaragua and the "
            "Honduran Liberals remain separate coalition members."
        ),
    ),
    "hced-Tegucicalpa1924-1": _contract(
        "hced-Tegucicalpa1924-1",
        _canonical(
            "Final assault and capture of Tegucigalpa",
            1924,
            "27-28 April 1924",
            "1924-04-27",
            "1924-04-28",
            "terminal_urban_assault_and_capital_capture",
        ),
        "honduran_civil_war_1924",
        (_REVOLUTIONARY_COLUMNS_1924,),
        (_COUNCIL_DEFENDERS_1924,),
        "civil_war",
        "revolutionary_columns_vs_council_loyalists_us_excluded",
        (
            "The Honduran civil-war history dates the final assault and capture to "
            "27-28 April. The diplomatic and U.S. Navy records bound U.S. activity "
            "to protection/intervention context; the United States is not encoded "
            "as a belligerent in this tactical event."
        ),
        parent_coverage_ids=("brecke-3146",),
        excluded_participant_labels=("The United States", "United States"),
    ),
}


WAVE8_HONDURAN_REBELS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Choluteca1894-1": {
        "raw_row_sha256": WAVE8_HONDURAN_REBELS_ROW_HASHES[
            "hced-Choluteca1894-1"
        ],
        "canonical_event": {
            "canonical_key": "choluteca-actions:1893:1894",
            "date_precision": "multiple_day_ranges",
            "date_text": (
                "30 December 1893-3 January 1894 and 15-17 January 1894"
            ),
            "start_date": "1893-12-30",
            "end_date": "1894-01-17",
            "granularity": "two_distinct_actions_collapsed_into_one_year_place_row",
            "name": "Choluteca actions",
            "year_low": 1893,
            "year_high": 1894,
        },
        "cohort": "honduran_liberal_revolution_1893_1894",
        "disposition": "hold",
        "hold_category": (
            "year_place_row_collapses_multiple_actions_and_source_outcome_"
            "contradiction"
        ),
        "reviewed_outcome": "unknown",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_components": [
            {
                "name": "Siege and capture of Choluteca",
                "start_date": "1893-12-30",
                "end_date": "1894-01-03",
                "reviewed_outcome": "liberal_nicaraguan_victory",
                "defender_boundary": "Vicente Williams and José María Estrada",
            },
            {
                "name": "Second Battle of Choluteca",
                "start_date": "1894-01-15",
                "end_date": "1894-01-17",
                "reviewed_outcome": "liberal_nicaraguan_victory",
                "defender_boundary": "Domingo Vásquez field force",
            },
        ],
        "reviewed_actor_description": [
            "Policarpo Bonilla’s Liberal force and Anastasio Ortiz’s Nicaraguan expedition",
            "separately constituted Choluteca defenders in two different actions",
        ],
        "evidence_refs": [
            "wave8_honduran_rebels_becerra_evolucion_historica",
            "wave8_honduran_rebels_frus_1894_d295",
            "wave8_honduran_rebels_frus_1894_d307",
        ],
        "hold_reason": (
            "HCED's year-place row compresses the 30 December-3 January siege and "
            "the 15-17 January battle even though the defenders differ. Reviewed "
            "sources describe Liberal/Nicaraguan victories, contradicting HCED's "
            "Honduras win. The lane neither reverses an aggregate row nor chooses "
            "one component arbitrarily: the candidate result remains unknown, "
            "never a draw."
        ),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "review_hold_owner",
        },
    },
    "hced-San Marcos, Honduras1876-1": {
        "raw_row_sha256": WAVE8_HONDURAN_REBELS_ROW_HASHES[
            "hced-San Marcos, Honduras1876-1"
        ],
        "canonical_event": {
            "canonical_key": "san-marcos-naranjo-identity-review:1876:1876",
            "date_precision": "conflicting_exact_days",
            "date_text": "13, 14, or 22 February 1876",
            "start_date": "1876-02-13",
            "end_date": "1876-02-22",
            "granularity": "unresolved_san_marcos_rio_san_marcos_naranjo_identity",
            "name": "San Marcos-Naranjo action",
            "year_low": 1876,
            "year_high": 1876,
        },
        "cohort": "honduran_medina_revolt_1876",
        "disposition": "hold",
        "hold_category": "unresolved_san_marcos_naranjo_identity_and_date_conflict",
        "reviewed_outcome": "unknown",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_actor_description": [
            "Leiva–Bográn Honduran government force",
            "José María Medina or Juan Antonio Medina-aligned force",
        ],
        "date_candidates": [
            {
                "date": "1876-02-13",
                "source_record": "iwbd-60-21-272",
                "place": "San Marcos (Honduras)",
            },
            {
                "date": "1876-02-14",
                "source_id": "wave8_honduran_rebels_secapph_el_paraiso",
                "place": "Rio San Marcos near Danli",
            },
            {
                "date": "1876-02-22",
                "source_id": "wave8_honduran_rebels_yoro_monograph",
                "place": "Naranjo",
            },
        ],
        "evidence_refs": [
            "wave8_honduran_rebels_bancroft_central_america_v3",
            "wave8_honduran_rebels_secapph_el_paraiso",
            "wave8_honduran_rebels_yoro_monograph",
        ],
        "hold_reason": (
            "IWBD gives San Marcos on 13 February; the Honduran local history gives "
            "Rio San Marcos on 14 February; Bancroft places Naranjo after 15 "
            "February; and the departmental monograph dates Naranjo to 22 February. "
            "HCED's raw token 'El Naranja' suggests but does not prove conflation. "
            "The likely government victory cannot be attached to one exact event "
            "safely, so the reviewed candidate stays unknown, never a draw."
        ),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "review_hold_owner",
        },
    },
}

WAVE8_HONDURAN_REBELS_CONTRACT_IDS = frozenset(
    WAVE8_HONDURAN_REBELS_CONTRACTS
)
WAVE8_HONDURAN_REBELS_HOLD_IDS = frozenset(WAVE8_HONDURAN_REBELS_HOLDS)
WAVE8_HONDURAN_REBELS_RESERVED_IDS = frozenset(
    WAVE8_HONDURAN_REBELS_CONTRACT_IDS | WAVE8_HONDURAN_REBELS_HOLD_IDS
)


WAVE8_HONDURAN_REBELS_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_HONDURAN_REBELS_CONTRACT_IDS
)
WAVE8_HONDURAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = (
    frozenset()
)

_LOCATION_REASON_TEXT: dict[str, str] = {
    "hced-Danli1844-1": (
        "HCED's Danlí point is a modern locality assertion, not an authenticated "
        "coordinate for the 20 December battlefield."
    ),
    "hced-Tegucicalpa1894-1": (
        "A single Tegucigalpa locality point cannot authenticate the month-long "
        "siege perimeter or the capital's capture locus."
    ),
    "hced-Tegucicalpa1924-1": (
        "A single Tegucigalpa locality point does not identify the 27-28 April "
        "assault positions or a defensible event centroid."
    ),
}
_RAW_POINTS: dict[str, list[float]] = {
    "hced-Danli1844-1": [-86.5703554, 14.0410953],
    "hced-Tegucicalpa1894-1": [-87.192136, 14.0722751],
    "hced-Tegucicalpa1924-1": [-87.192136, 14.0722751],
}
WAVE8_HONDURAN_REBELS_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "raw_point": _RAW_POINTS[candidate_id],
        "retained_country": "Honduras",
        "reason": (
            f"{_LOCATION_REASON_TEXT[candidate_id]} Retain modern country Honduras "
            "and location provenance; do not silently substitute a point."
        ),
        "evidence_refs": list(contract["evidence_refs"]),
    }
    for candidate_id, contract in sorted(
        WAVE8_HONDURAN_REBELS_CONTRACTS.items()
    )
}


WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "hced-La Esperanza1876-1": (
        "c67368cdc6a33be130b03bd68495cb44694183fcab127a57c2e4922d73a38e3e"
    )
}
WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "iwbd-60-21-271": (
        "bd8188b8687536e2672d7e7ef59518e3b8b25ea71ea259029812d870b8a0439a"
    ),
    "iwbd-60-21-272": (
        "a9be2ea59c1e0e3ed32f82943834b594571621fb9c7f7f124e519effcb51a25d"
    ),
}
WAVE8_HONDURAN_REBELS_DISCOVERY_TWINS: dict[str, str] = {
    "hced-La Esperanza1876-1": "iwbd-60-21-271",
    "hced-San Marcos, Honduras1876-1": "iwbd-60-21-272",
}
WAVE8_HONDURAN_REBELS_DISCOVERY_EXPECTED: dict[str, dict[str, Any]] = {
    "hced-La Esperanza1876-1": {
        "source_dataset": "hced",
        "name": "La Esperanza",
        "year": 1876,
        "side_1_raw": "former President Jose Maria Medina",
        "side_2_raw": "President Ponciano Levia",
        "winner_raw": "former President Jose Maria Medina",
        "relationship": "separate_earlier_1876_action_outside_exact_label_lane",
        "outcome_disposition": "unknown_never_draw",
    },
    "iwbd-60-21-271": {
        "source_dataset": "iwbd",
        "name": "La Esperanza (maybe shouldn't be in data)",
        "start_date": "1876-01-15",
        "end_date": "1876-01-15",
        "attacker_raw": "El Salvador (Medina)",
        "defender_raw": "Honduras (Levia)",
        "winner_raw": "El Salvador (Medina)",
        "battle_level_victor_role": "Attacker",
        "relationship": "probable_twin_of_hced_la_esperanza_outside_lane",
        "outcome_disposition": "unknown_never_draw",
    },
    "iwbd-60-21-272": {
        "source_dataset": "iwbd",
        "name": "San Marcos (Honduras)",
        "start_date": "1876-02-13",
        "end_date": "1876-02-13",
        "attacker_raw": "Honduras (Levia)",
        "defender_raw": "El Salvador (Medina)",
        "winner_raw": "Honduras (Levia)",
        "battle_level_victor_role": "Attacker",
        "relationship": "probable_twin_of_held_hced_san_marcos",
        "outcome_disposition": "unknown_never_draw",
    },
}


WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_ROW_HASHES: dict[str, str] = {
    "brecke-2299": (
        "3d2439fb92ebabb9476ae34ed8115ce588b2bdfc515362fba7a1dae4f4803175"
    ),
    "brecke-3146": (
        "81264bcbaba8be51abfe84e291e6f867c0e8bd3477f819ac5cbe787dc0a9feb2"
    ),
}
WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_EXPECTED: dict[
    str, dict[str, Any]
] = {
    "brecke-2299": {
        "common_name": "Second Central American War",
        "start_year": 1831,
        "start_month": None,
        "start_day": None,
        "end_year": 1845,
        "end_month": None,
        "end_day": None,
        "outcome_available": False,
        "rating_use": "coverage_cross_check_only",
        "relationship": "parent_catalog_interval_contains_danli_not_event_duplicate",
        "hced_candidate_id": "hced-Danli1844-1",
    },
    "brecke-3146": {
        "common_name": None,
        "start_year": 1924,
        "start_month": 2,
        "start_day": 9,
        "end_year": 1924,
        "end_month": 3,
        "end_day": 1,
        "outcome_available": False,
        "rating_use": "coverage_cross_check_only",
        "relationship": "parent_catalog_interval_ends_before_april_capital_capture",
        "hced_candidate_id": "hced-Tegucicalpa1924-1",
    },
}


WAVE8_HONDURAN_REBELS_RELATED_EVENT_BOUNDARIES: dict[
    str, dict[str, Any]
] = {
    "choluteca_vs_tegucigalpa_1894": {
        "candidate_ids": [
            "hced-Choluteca1894-1",
            "hced-Tegucicalpa1894-1",
        ],
        "disposition": "distinct_events_in_same_revolution",
        "reason": (
            "The Choluteca actions end before the separately bounded 23 January-"
            "22 February siege and capture of Tegucigalpa."
        ),
    },
    "la_esperanza_vs_san_marcos_1876": {
        "candidate_ids": [
            "hced-La Esperanza1876-1",
            "hced-San Marcos, Honduras1876-1",
        ],
        "disposition": "distinct_earlier_and_later_actions",
        "reason": (
            "The 15 January La Esperanza record precedes every San Marcos/Naranjo "
            "date candidate and is not consumed by this exact-label lane."
        ),
    },
    "san_marcos_vs_naranjo_1876": {
        "candidate_ids": ["hced-San Marcos, Honduras1876-1"],
        "disposition": "identity_unresolved_review_hold",
        "reason": (
            "Place-token and date evidence is insufficient to merge San Marcos, "
            "Rio San Marcos, El Naranja, and Naranjo into one rated event."
        ),
    },
}


WAVE8_HONDURAN_REBELS_INTEGRATION_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "hced-La Esperanza1876-1": {
        "source_dataset": "hced",
        "disposition": "discovery_only_separate_event_outside_lane",
        "outcome_disposition": "unknown_never_draw",
    },
    "iwbd-60-21-271": {
        "source_dataset": "iwbd",
        "disposition": "deduplicate_to_outside_lane_hced_discovery_hold",
        "hced_candidate_id": "hced-La Esperanza1876-1",
        "outcome_disposition": "unknown_never_draw",
    },
    "iwbd-60-21-272": {
        "source_dataset": "iwbd",
        "disposition": "deduplicate_to_hced_review_hold",
        "hced_candidate_id": "hced-San Marcos, Honduras1876-1",
        "outcome_disposition": "unknown_never_draw",
    },
    "brecke-2299": {
        "source_dataset": "brecke-conflict-catalog",
        "disposition": "coverage_only_parent_not_engagement_duplicate",
        "hced_candidate_id": "hced-Danli1844-1",
    },
    "brecke-3146": {
        "source_dataset": "brecke-conflict-catalog",
        "disposition": "coverage_only_parent_not_engagement_duplicate",
        "hced_candidate_id": "hced-Tegucicalpa1924-1",
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_HONDURAN_REBELS_CONTRACTS,
        "discovery_expected": WAVE8_HONDURAN_REBELS_DISCOVERY_EXPECTED,
        "discovery_twins": WAVE8_HONDURAN_REBELS_DISCOVERY_TWINS,
        "entities": WAVE8_HONDURAN_REBELS_ENTITIES,
        "funnel_audits": WAVE8_HONDURAN_REBELS_FUNNEL_AUDITS,
        "hced_discovery_hashes": WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES,
        "holds": WAVE8_HONDURAN_REBELS_HOLDS,
        "integration_dispositions": WAVE8_HONDURAN_REBELS_INTEGRATION_DISPOSITIONS,
        "iwbd_discovery_hashes": WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES,
        "location_reasons": WAVE8_HONDURAN_REBELS_LOCATION_QUARANTINE_REASONS,
        "parent_coverage_expected": WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_EXPECTED,
        "parent_coverage_hashes": WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_ROW_HASHES,
        "related_event_boundaries": WAVE8_HONDURAN_REBELS_RELATED_EVENT_BOUNDARIES,
        "required_existing_entities": WAVE8_HONDURAN_REBELS_REQUIRED_EXISTING_ENTITIES,
        "row_hashes": WAVE8_HONDURAN_REBELS_ROW_HASHES,
        "sources": WAVE8_HONDURAN_REBELS_SOURCES,
    }


def wave8_honduran_rebels_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_HONDURAN_REBELS_FINAL_AUDIT_SIGNATURE = (
    "969fb4191bf68eea22945fc82ec409fcf915c2cc8c4349d231669bdc84f84ff5"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = set(_ENTITY_BY_ID)
    if len(source_ids) != len(WAVE8_HONDURAN_REBELS_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if len(entity_ids) != len(WAVE8_HONDURAN_REBELS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} duplicate entity id")
    if len(source_ids) != 11 or len(
        {str(source["source_family_id"]) for source in _SOURCE_BY_ID.values()}
    ) != 10:
        raise ValueError(f"{_LANE_NAME} source/family inventory drift")

    expected_urls = {
        "wave8_honduran_rebels_ariel_233_danli": (
            "https://tzibalnaah.unah.edu.hn/bitstream/handle/123456789/16923/"
            "No.233.abr1971.pdf?isAllowed=y&sequence=1"
        ),
        "wave8_honduran_rebels_bancroft_central_america_v3": (
            "https://www.gutenberg.org/files/62657/62657-h/62657-h.htm"
        ),
        "wave8_honduran_rebels_becerra_evolucion_historica": (
            "https://es.scribd.com/document/498046397/"
            "Evolucion-Historica-de-Honduras-Longino-Becerra"
        ),
        "wave8_honduran_rebels_frus_1894_d295": (
            "https://history.state.gov/historicaldocuments/frus1894/d295"
        ),
        "wave8_honduran_rebels_frus_1894_d307": (
            "https://history.state.gov/historicaldocuments/frus1894/d307"
        ),
        "wave8_honduran_rebels_frus_1924_d261": (
            "https://history.state.gov/historicaldocuments/frus1924v02/d261"
        ),
        "wave8_honduran_rebels_garcia_buchard_1839_1845": (
            "https://dialnet.unirioja.es/descarga/articulo/5089074.pdf"
        ),
        "wave8_honduran_rebels_secapph_el_paraiso": (
            "https://secapph.gob.hn/wp-content/uploads/2025/06/"
            "RESENA-HISTORICA-Y-GEOGRAFICA-DEL-NACIENTE-PUEBLO-DEL-PARAISO.pdf"
        ),
        "wave8_honduran_rebels_sedesol_civil_war_1924": (
            "https://chepes.sedesol.gob.hn/wp-content/uploads/2025/09/"
            "LB016_La_guerra_civil_1924_en_Honduras_CHEPES_24-09-2025.pdf"
        ),
        "wave8_honduran_rebels_us_navy_expeditions_1901_1929": (
            "https://www.history.navy.mil/research/library/online-reading-room/"
            "title-list-alphabetically/l/list-of-expeditions-1901-1929.html"
        ),
        "wave8_honduran_rebels_yoro_monograph": (
            "https://www.cervantesvirtual.com/descargaPdf/"
            "monografia-del-departamento-de-yoro/"
        ),
    }
    for source_id, source in _SOURCE_BY_ID.items():
        if source["url"] != expected_urls[source_id]:
            raise ValueError(f"{_LANE_NAME} canonical source URL drift: {source_id}")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source role order drift: {source_id}")

    expected_entity_shape = {
        _DANLI_GOVERNMENT: (1844, 1844, "event_bounded_government_field_force"),
        _DANLI_LIBERATOR: (1844, 1844, "event_bounded_rebel_field_force"),
        _ORTIZ_EXPEDITION: (
            1893,
            1894,
            "conflict_bounded_foreign_expeditionary_force",
        ),
        _BONILLA_LIBERALS: (
            1893,
            1894,
            "conflict_bounded_liberal_revolutionary_force",
        ),
        _VASQUEZ_DEFENDERS: (
            1894,
            1894,
            "event_bounded_government_defense_force",
        ),
        _REVOLUTIONARY_COLUMNS_1924: (
            1924,
            1924,
            "event_bounded_revolutionary_assault_force",
        ),
        _COUNCIL_DEFENDERS_1924: (
            1924,
            1924,
            "event_bounded_loyalist_defense_force",
        ),
    }
    forbidden_aliases = {
        "honduran government",
        "honduran rebels",
        "nicaragua honduran rebels",
    }
    if entity_ids != set(expected_entity_shape):
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    for entity_id, entity in _ENTITY_BY_ID.items():
        start, end, kind = expected_entity_shape[entity_id]
        if (
            entity["start_year"],
            entity["end_year"],
            entity["kind"],
        ) != (start, end, kind):
            raise ValueError(f"{_LANE_NAME} identity boundary drift: {entity_id}")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identities must remain alias-free")
        if not set(map(str, entity["source_ids"])) <= source_ids:
            raise ValueError(f"{_LANE_NAME} entity source closure drift: {entity_id}")
        if not any(
            phrase in str(entity["continuity_note"]).casefold()
            for phrase in ("inherits no rating", "no rating")
        ):
            raise ValueError(f"{_LANE_NAME} identity continuity guard drift")
        if {
            normalize_label(alias) for alias in entity["aliases"]
        } & forbidden_aliases:
            raise ValueError(f"{_LANE_NAME} broad identity alias drift")

    if WAVE8_HONDURAN_REBELS_RESERVED_IDS != (
        WAVE8_HONDURAN_REBELS_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_HONDURAN_REBELS_CONTRACT_IDS & WAVE8_HONDURAN_REBELS_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if (
        len(WAVE8_HONDURAN_REBELS_CONTRACTS),
        len(WAVE8_HONDURAN_REBELS_HOLDS),
    ) != (3, 2):
        raise ValueError(f"{_LANE_NAME} disposition count drift")
    if (
        WAVE8_HONDURAN_REBELS_POINT_QUARANTINE_ADDITIONS
        != WAVE8_HONDURAN_REBELS_CONTRACT_IDS
        or WAVE8_HONDURAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        or set(WAVE8_HONDURAN_REBELS_LOCATION_QUARANTINE_REASONS)
        != WAVE8_HONDURAN_REBELS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location quarantine drift")

    expected_contracts = {
        "hced-Danli1844-1": (
            "Battle of Danlí",
            "20 December 1844",
            "1844-12-20",
            "1844-12-20",
            "day",
            "single_decisive_battle",
            [_DANLI_GOVERNMENT],
            [_DANLI_LIBERATOR],
            "internal_rebellion",
        ),
        "hced-Tegucicalpa1894-1": (
            "Siege and capture of Tegucigalpa",
            "23 January-22 February 1894",
            "1894-01-23",
            "1894-02-22",
            "day_range",
            "siege_and_capital_capture",
            [_ORTIZ_EXPEDITION, _BONILLA_LIBERALS],
            [_VASQUEZ_DEFENDERS],
            "intrastate_with_foreign_intervention",
        ),
        "hced-Tegucicalpa1924-1": (
            "Final assault and capture of Tegucigalpa",
            "27-28 April 1924",
            "1924-04-27",
            "1924-04-28",
            "day_range",
            "terminal_urban_assault_and_capital_capture",
            [_REVOLUTIONARY_COLUMNS_1924],
            [_COUNCIL_DEFENDERS_1924],
            "civil_war",
        ),
    }
    used_sources: set[str] = set()
    used_entities: set[str] = set()
    for candidate_id, contract in WAVE8_HONDURAN_REBELS_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or contract["source_date_override"]
            or contract["source_date_refinement"] is not True
            or float(contract["confidence"]) != 0.96
            or int(contract["expected_scale_level"]) != 2
        ):
            raise ValueError(f"{_LANE_NAME} contract disposition drift: {candidate_id}")
        (
            name,
            date_text,
            start_date,
            end_date,
            precision,
            granularity,
            side_1,
            side_2,
            war_type,
        ) = expected_contracts[candidate_id]
        year = int(candidate_id[-6:-2])
        canonical = contract["canonical_event"]
        if (
            canonical["canonical_key"] != f"{_slug(name)}:{year}:{year}"
            or canonical["name"] != name
            or canonical["date_text"] != date_text
            or canonical["start_date"] != start_date
            or canonical["end_date"] != end_date
            or canonical["date_precision"] != precision
            or canonical["granularity"] != granularity
            or (canonical["year_low"], canonical["year_high"]) != (year, year)
            or contract["side_1_entity_ids"] != side_1
            or contract["side_2_entity_ids"] != side_2
            or contract["war_type"] != war_type
        ):
            raise ValueError(f"{_LANE_NAME} exact contract drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        dates = list(map(str, contract["date_source_ids"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or not _is_sorted_unique(dates)
            or not _is_sorted_unique(outcomes)
            or not set(dates) <= set(evidence)
            or not set(outcomes) <= set(evidence)
            or not set(evidence) <= source_ids
            or len(contract["outcome_source_family_ids"]) < 2
        ):
            raise ValueError(f"{_LANE_NAME} source closure drift: {candidate_id}")
        expected_families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract["outcome_source_family_ids"] != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        if any(
            "outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} non-outcome source used for result")
        role_map = contract["event_evidence_roles"]
        if set(role_map) != set(evidence):
            raise ValueError(f"{_LANE_NAME} event source-role closure drift")
        if any(not roles or not _is_sorted_unique(roles) for roles in role_map.values()):
            raise ValueError(f"{_LANE_NAME} event source-role ordering drift")
        used_sources.update(evidence)
        used_entities.update(side_1)
        used_entities.update(side_2)

    expected_hold_categories = {
        "hced-Choluteca1894-1": (
            "year_place_row_collapses_multiple_actions_and_source_outcome_"
            "contradiction"
        ),
        "hced-San Marcos, Honduras1876-1": (
            "unresolved_san_marcos_naranjo_identity_and_date_conflict"
        ),
    }
    for candidate_id, hold in WAVE8_HONDURAN_REBELS_HOLDS.items():
        if (
            hold["disposition"] != "hold"
            or hold["hold_category"] != expected_hold_categories[candidate_id]
            or hold["reviewed_outcome"] != "unknown"
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
            or "winner_side" in hold
            or "never a draw" not in hold["hold_reason"]
        ):
            raise ValueError(f"{_LANE_NAME} unknown hold drift: {candidate_id}")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} hold evidence closure drift")
        used_sources.update(evidence)
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if used_entities != entity_ids or _HONDURAS in used_entities:
        raise ValueError(f"{_LANE_NAME} rated identity inventory drift")

    if set(WAVE8_HONDURAN_REBELS_DISCOVERY_TWINS) != {
        "hced-La Esperanza1876-1",
        "hced-San Marcos, Honduras1876-1",
    }:
        raise ValueError(f"{_LANE_NAME} discovery twin owner drift")
    if set(WAVE8_HONDURAN_REBELS_DISCOVERY_TWINS.values()) != set(
        WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} IWBD discovery inventory drift")
    discovery_ids = {
        *WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES,
        *WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES,
    }
    if set(WAVE8_HONDURAN_REBELS_DISCOVERY_EXPECTED) != discovery_ids:
        raise ValueError(f"{_LANE_NAME} discovery expectation drift")
    if any(
        item["outcome_disposition"] != "unknown_never_draw"
        for item in WAVE8_HONDURAN_REBELS_DISCOVERY_EXPECTED.values()
    ):
        raise ValueError(f"{_LANE_NAME} discovery outcome guard drift")
    integration_ids = {
        *discovery_ids,
        *WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_ROW_HASHES,
    }
    if set(WAVE8_HONDURAN_REBELS_INTEGRATION_DISPOSITIONS) != integration_ids:
        raise ValueError(f"{_LANE_NAME} integration disposition drift")
    if set(WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_EXPECTED) != set(
        WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} parent coverage inventory drift")
    if set(WAVE8_HONDURAN_REBELS_RELATED_EVENT_BOUNDARIES) != {
        "choluteca_vs_tegucigalpa_1894",
        "la_esperanza_vs_san_marcos_1876",
        "san_marcos_vs_naranjo_1876",
    }:
        raise ValueError(f"{_LANE_NAME} related-event boundary drift")
    if (
        WAVE8_HONDURAN_REBELS_FINAL_AUDIT_SIGNATURE != "TO_BE_FILLED"
        and wave8_honduran_rebels_audit_signature()
        != WAVE8_HONDURAN_REBELS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_honduran_rebels_existing_entities(
    release_entities: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    for entity_id, expected in (
        WAVE8_HONDURAN_REBELS_REQUIRED_EXISTING_ENTITIES.items()
    ):
        entity = release_entities.get(entity_id)
        if entity is None:
            raise ValueError(f"{_LANE_NAME} missing existing identity {entity_id}")
        projection = {key: entity.get(key) for key in expected}
        if projection != expected:
            raise ValueError(
                f"{_LANE_NAME} existing identity drift for {entity_id}: {projection}"
            )
    forbidden = {
        "honduran government",
        "honduran rebels",
        "nicaragua honduran rebels",
    }
    broad_aliases = {
        normalize_label(alias)
        for entity in release_entities.values()
        for alias in entity.get("aliases", []) or []
    } & forbidden
    if broad_aliases:
        raise ValueError(
            f"{_LANE_NAME} broad Honduran alias introduced: {sorted(broad_aliases)}"
        )
    return {
        "required_existing_entities": len(
            WAVE8_HONDURAN_REBELS_REQUIRED_EXISTING_ENTITIES
        )
    }


def validate_wave8_honduran_rebels_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) in _AUDITED_LABELS
        or normalize_label(row.get("side_2_raw")) in _AUDITED_LABELS
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_HONDURAN_REBELS_RESERVED_IDS or len(exact) != len(
        exact_ids
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    expected_label_inventory = {
        _EXACT_LABEL: {
            "hced-Danli1844-1",
            "hced-San Marcos, Honduras1876-1",
            "hced-Tegucicalpa1924-1",
        },
        _COMPOSITE_LABEL: {
            "hced-Choluteca1894-1",
            "hced-Tegucicalpa1894-1",
        },
    }
    for label, expected_ids in expected_label_inventory.items():
        actual_ids = {
            str(row.get("candidate_id"))
            for row in exact
            if label
            in {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
        }
        if actual_ids != expected_ids:
            raise ValueError(f"{_LANE_NAME} label inventory changed: {label}")

    expected_raw: dict[str, tuple[Any, ...]] = {
        "hced-Choluteca1894-1": (
            "Choluteca",
            1894,
            "Honduras",
            "Nicaragua, Honduran Rebels",
            "Honduras",
            "Nicaragua, Honduran Rebels",
            ["Central American", "Honduras", "Nicaraguan", "Honduran", "Tegucicalpa"],
            None,
        ),
        "hced-Danli1844-1": (
            "Danli",
            1844,
            "Honduran Government",
            "Honduran Rebels",
            "Honduran Government",
            "Honduran Rebels",
            ["Central American", "Honduras", "Comayagua"],
            None,
        ),
        "hced-San Marcos, Honduras1876-1": (
            "San Marcos, Honduras",
            1876,
            "Honduras",
            "Honduran Rebels",
            "Honduras",
            "Honduran Rebels",
            ["San Marcos", "Honduras", "Honduras", "Medina", "El Naranja"],
            None,
        ),
        "hced-Tegucicalpa1894-1": (
            "Tegucicalpa",
            1894,
            "Nicaragua, Honduran Rebels",
            "Honduras",
            "Nicaragua, Honduran Rebels",
            "Honduras",
            ["Tegucicalpa", "Central American", "Honduras", "Honduran"],
            None,
        ),
        "hced-Tegucicalpa1924-1": (
            "Tegucicalpa",
            1924,
            "Honduran Rebels",
            "Honduras",
            "Honduran Rebels",
            "Honduras",
            ["The United States"],
            None,
        ),
    }
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_HONDURAN_REBELS_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        (
            name,
            year,
            side_1,
            side_2,
            winner,
            loser,
            participants,
            scale,
        ) = expected_raw[candidate_id]
        if (
            row.get("name") != name
            or (row.get("year_low"), row.get("year_best"), row.get("year_high"))
            != (year, year, year)
            or row.get("side_1_raw") != side_1
            or row.get("side_2_raw") != side_2
            or row.get("winner_raw") != winner
            or row.get("loser_raw") != loser
            or row.get("participants_raw") != participants
            or row.get("scale_raw") != scale
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("modern_location_country") != "Honduras"
            or row.get("theatre_raw") != "Land"
            or row.get("do_not_rate_automatically") is not True
            or row.get("duplicate_source_id") is not False
        ):
            raise ValueError(f"{_LANE_NAME} locked source semantics changed: {candidate_id}")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_HONDURAN_REBELS_CONTRACTS,
        WAVE8_HONDURAN_REBELS_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "audited_label_rows": len(exact), "audited_labels": 2}


def validate_wave8_honduran_rebels_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    by_label: dict[str, list[Mapping[str, Any]]] = {
        label: [
            row for row in funnel.get("labels", []) if row.get("label") == label
        ]
        for label in _AUDITED_LABELS
    }
    for label, rows in by_label.items():
        if len(rows) != 1:
            raise ValueError(f"{_LANE_NAME} expected one funnel row for {label}")
        row = rows[0]
        expected = WAVE8_HONDURAN_REBELS_FUNNEL_AUDITS[label]
        actual = {
            "candidate_ids": list(map(str, row.get("candidate_ids", []))),
            "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
            "events_touched": int(row.get("events_touched", -1)),
            "failure_cases": {
                key: int(row.get("failure_cases", {}).get(key, -1))
                for key in expected["failure_cases"]
            },
            "label": str(row.get("label")),
            "rated_counterpart_entities": int(
                row.get("rated_counterpart_entities", -1)
            ),
            "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
            "time_valid_candidate_ids": list(
                map(str, row.get("time_valid_candidate_ids", []))
            ),
            "unresolved_side_attempts": int(
                row.get("unresolved_side_attempts", -1)
            ),
        }
        if actual != expected:
            raise ValueError(f"{_LANE_NAME} funnel pin changed for {label}: {actual}")
    return {
        "audited_labels": len(by_label),
        "events_touched": sum(
            int(row[0]["events_touched"]) for row in by_label.values()
        ),
        "sole_blocker_events": sum(
            int(row[0]["sole_blocker_events"]) for row in by_label.values()
        ),
        "unresolved_side_attempts": sum(
            int(row[0]["unresolved_side_attempts"]) for row in by_label.values()
        ),
        "zero_time_valid_candidates": sum(
            int(row[0]["failure_cases"]["zero_time_valid_candidates"])
            for row in by_label.values()
        ),
    }


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def validate_wave8_honduran_rebels_parent_coverage(
    brecke_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in brecke_rows:
        by_id.setdefault(str(row.get("brecke_id")), []).append(row)
    fields = (
        "common_name",
        "start_year",
        "start_month",
        "start_day",
        "end_year",
        "end_month",
        "end_day",
        "outcome_available",
        "rating_use",
    )
    for brecke_id, expected_hash in (
        WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_ROW_HASHES.items()
    ):
        rows = by_id.get(brecke_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} parent coverage {brecke_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} parent coverage fingerprint changed")
        expected = WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_EXPECTED[brecke_id]
        if {field: row.get(field) for field in fields} != {
            field: expected[field] for field in fields
        } or row.get("source") != "brecke-conflict-catalog":
            raise ValueError(f"{_LANE_NAME} parent coverage semantics changed")
    return {
        "parent_coverage_records": len(
            WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_ROW_HASHES
        ),
        "parent_event_duplicates": 0,
        "parent_outcomes_used": 0,
    }


def validate_wave8_honduran_rebels_discovery_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    brecke_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    hced_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        hced_by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in (
        WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES.items()
    ):
        rows = hced_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} HCED discovery {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} HCED discovery fingerprint changed")
        expected = WAVE8_HONDURAN_REBELS_DISCOVERY_EXPECTED[candidate_id]
        if (
            row.get("source") != expected["source_dataset"]
            or row.get("name") != expected["name"]
            or row.get("year_best") != expected["year"]
            or row.get("side_1_raw") != expected["side_1_raw"]
            or row.get("side_2_raw") != expected["side_2_raw"]
            or row.get("winner_raw") != expected["winner_raw"]
            or row.get("do_not_rate_automatically") is not True
        ):
            raise ValueError(f"{_LANE_NAME} HCED discovery semantics changed")

    iwbd_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in iwbd_rows:
        iwbd_by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    iwbd_fields = (
        "name",
        "start_date",
        "end_date",
        "attacker_raw",
        "defender_raw",
        "winner_raw",
        "battle_level_victor_role",
    )
    for candidate_id, expected_hash in (
        WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES.items()
    ):
        rows = iwbd_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} IWBD discovery {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(
                f"{_LANE_NAME} IWBD discovery fingerprint changed: {candidate_id}"
            )
        expected = WAVE8_HONDURAN_REBELS_DISCOVERY_EXPECTED[candidate_id]
        if (
            row.get("source") != expected["source_dataset"]
            or row.get("do_not_rate_automatically") is not True
            or {field: row.get(field) for field in iwbd_fields}
            != {field: expected[field] for field in iwbd_fields}
        ):
            raise ValueError(
                f"{_LANE_NAME} IWBD discovery semantics changed: {candidate_id}"
            )
    parent = validate_wave8_honduran_rebels_parent_coverage(brecke_rows)
    return {
        "discovery_nonrating_records": (
            len(WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES)
            + len(WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES)
            + parent["parent_coverage_records"]
        ),
        "discovery_promotions": 0,
        "discovery_twins": len(WAVE8_HONDURAN_REBELS_DISCOVERY_TWINS),
        "hced_discovery_records": len(
            WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES
        ),
        "iwbd_discovery_records": len(
            WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES
        ),
        "parent_coverage_records": parent["parent_coverage_records"],
        "unknown_never_draw_rows": (
            len(WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES)
            + len(WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES)
        ),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in (
        "year",
        "year_best",
        "year_low",
        "start_year",
        "year_start",
        "batyear",
    ):
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
    values = [
        row.get("name"),
        row.get("battle_name"),
        row.get("batname"),
        row.get("event_name"),
    ]
    aliases = row.get("aliases", []) or []
    if isinstance(aliases, str):
        values.append(aliases)
    else:
        values.extend(aliases)
    return {normalize_label(value) for value in values if normalize_label(value)}


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Choluteca1894-1": {
        "Choluteca",
        "Choluteca actions",
        "Siege of Choluteca",
        "Siege and capture of Choluteca",
        "Battle of Choluteca",
        "Second Battle of Choluteca",
    },
    "hced-Danli1844-1": {"Danli", "Danlí", "Battle of Danlí"},
    "hced-La Esperanza1876-1": {
        "La Esperanza",
        "La Esperanza (maybe shouldn't be in data)",
    },
    "hced-San Marcos, Honduras1876-1": {
        "San Marcos",
        "San Marcos, Honduras",
        "San Marcos (Honduras)",
        "Rio San Marcos",
        "El Naranja",
        "Naranjo",
        "Battle of Naranjo",
    },
    "hced-Tegucicalpa1894-1": {
        "Tegucicalpa",
        "Siege of Tegucigalpa",
        "Siege and capture of Tegucigalpa",
    },
    "hced-Tegucicalpa1924-1": {
        "Tegucicalpa",
        "Capture of Tegucigalpa",
        "Final assault and capture of Tegucigalpa",
    },
}
_EVENT_YEARS: dict[str, range] = {
    "hced-Choluteca1894-1": range(1893, 1895),
    "hced-Danli1844-1": range(1844, 1845),
    "hced-La Esperanza1876-1": range(1876, 1877),
    "hced-San Marcos, Honduras1876-1": range(1876, 1877),
    "hced-Tegucicalpa1894-1": range(1894, 1895),
    "hced-Tegucicalpa1924-1": range(1924, 1925),
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (year, normalize_label(alias))
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for year in _EVENT_YEARS[candidate_id]
    for alias in aliases
)
_EVENT_NAMES = frozenset(name for _, name in _DUPLICATE_MATCH_KEYS)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    matched_names = _row_names(row) & _EVENT_NAMES
    if not matched_names:
        return False
    year = _row_year(row)
    if year is None:
        return True
    return any((year, name) in _DUPLICATE_MATCH_KEYS for name in matched_names)


def validate_wave8_honduran_rebels_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwd_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    brecke_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Prove discovery ownership and absence of unreviewed event twins."""

    validate_wave8_honduran_rebels_queue_contracts(hced_rows)
    validate_wave8_honduran_rebels_discovery_dispositions(
        hced_rows, iwbd_rows, brecke_rows
    )
    known_hced = {
        *WAVE8_HONDURAN_REBELS_RESERVED_IDS,
        *WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES,
    }
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in known_hced
        and _is_probable_twin(row)
    )
    iwd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwd_rows
        if _is_probable_twin(row)
    )
    known_iwbd = set(WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES)
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if str(row.get("candidate_id")) not in known_iwbd
        and _is_probable_twin(row)
    )
    existing = list(existing_events)
    owned = [
        event
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_HONDURAN_REBELS_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    if owned:
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        if owned_ids != WAVE8_HONDURAN_REBELS_CONTRACT_IDS or len(owned) != len(
            owned_ids
        ):
            raise ValueError(f"{_LANE_NAME} current release ownership is partial")
        if any(
            not str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
            for event in owned
        ):
            raise ValueError(f"{_LANE_NAME} current release owner prefix changed")
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event not in owned and _is_probable_twin(event)
    )
    if hced_twins or iwd_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"iwd={iwd_twins}, iwbd={iwbd_twins}, release={release_twins}"
        )
    return {
        "discovery_nonrating_dispositions": len(
            WAVE8_HONDURAN_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "existing_release_owned_events": len(owned),
        "existing_release_probable_twins": 0,
        "hced_discovery_dispositions": len(
            WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES
        ),
        "hced_probable_twins": 0,
        "iwd_probable_twins": 0,
        "iwbd_discovery_dispositions": len(
            WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES
        ),
        "iwbd_probable_twins": 0,
        "parent_coverage_dispositions": len(
            WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_ROW_HASHES
        ),
    }


def install_wave8_honduran_rebels_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_HONDURAN_REBELS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_honduran_rebels_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_HONDURAN_REBELS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_HONDURAN_REBELS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_HONDURAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_honduran_rebels_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_honduran_rebels_queue_contracts(hced_rows)
    validate_wave8_honduran_rebels_existing_entities(release_entities)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_HONDURAN_REBELS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def validate_wave8_honduran_rebels_current_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Require Honduran lane artifacts to be wholly absent or complete."""

    _validate_static()
    events = list(release_events)
    owned = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_HONDURAN_REBELS_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    all_entity_by_id = {
        str(entity.get("id")): entity for entity in release_entities
    }
    validate_wave8_honduran_rebels_existing_entities(all_entity_by_id)
    entity_by_id = {
        entity_id: entity
        for entity_id, entity in all_entity_by_id.items()
        if entity_id in _ENTITY_BY_ID
    }
    source_by_id = {
        str(source.get("id")): source
        for source in release_sources
        if str(source.get("id")) in _SOURCE_BY_ID
    }
    state_counts = (len(owned), len(entity_by_id), len(source_by_id))
    absent = (0, 0, 0)
    complete = (
        len(WAVE8_HONDURAN_REBELS_CONTRACTS),
        len(WAVE8_HONDURAN_REBELS_ENTITIES),
        len(WAVE8_HONDURAN_REBELS_SOURCES),
    )
    if state_counts not in {absent, complete}:
        raise ValueError(
            f"{_LANE_NAME} current release artifacts are partial: {state_counts}"
        )
    if state_counts == absent:
        return {
            "artifact_state": "absent",
            "installed_entities": 0,
            "installed_sources": 0,
            "promoted_events": 0,
        }
    for entity_id, fixture in _ENTITY_BY_ID.items():
        if entity_by_id[entity_id] != fixture:
            raise ValueError(f"{_LANE_NAME} current release entity drift: {entity_id}")
    for source_id, fixture in _SOURCE_BY_ID.items():
        if source_by_id[source_id] != fixture:
            raise ValueError(f"{_LANE_NAME} current release source drift: {source_id}")

    by_candidate = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_candidate) != WAVE8_HONDURAN_REBELS_CONTRACT_IDS or len(
        owned
    ) != len(by_candidate):
        raise ValueError(f"{_LANE_NAME} current release candidate inventory changed")
    participant_ids: set[str] = set()
    for candidate_id, contract in WAVE8_HONDURAN_REBELS_CONTRACTS.items():
        event = by_candidate[candidate_id]
        canonical = contract["canonical_event"]
        year = int(canonical["year_low"])
        expected_id = f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        if (
            event.get("id") != expected_id
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year")) != (year, year)
            or event.get("event_type") != "engagement"
            or event.get("war_type") != contract["war_type"]
            or event.get("scale") != "battle"
            or event.get("date_precision") != canonical["date_precision"]
            or event.get("reviewed_granularity") != canonical["granularity"]
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids")
            != contract["outcome_source_family_ids"]
            or event.get("source_ids")
            != ["hced_dataset", *contract["evidence_refs"]]
            or float(event.get("confidence", -1.0)) != 0.96
            or event.get("domain") != "land"
        ):
            raise ValueError(f"{_LANE_NAME} current release event drift: {candidate_id}")
        expected_participants = expected_exact_hced_win_participants(
            contract["side_1_entity_ids"],
            contract["side_2_entity_ids"],
            confidence=0.96,
            scale_level=2,
            lane_name=_LANE_NAME,
        )
        if event.get("participants") != expected_participants:
            raise ValueError(
                f"{_LANE_NAME} current release participant drift: {candidate_id}"
            )
        participant_ids.update(
            str(participant["entity_id"])
            for participant in event.get("participants", [])
        )
        if (
            "geometry" in event
            or event.get("modern_location_country") != "Honduras"
            or "location_provenance" not in event
        ):
            raise ValueError(f"{_LANE_NAME} current release location drift: {candidate_id}")
    if participant_ids != set(_ENTITY_BY_ID) or _HONDURAS in participant_ids:
        raise ValueError(f"{_LANE_NAME} current release identity shortcut drift")
    if "united_states" in {
        str(participant["entity_id"])
        for participant in by_candidate["hced-Tegucicalpa1924-1"]["participants"]
    }:
        raise ValueError(f"{_LANE_NAME} United States belligerent boundary drift")
    return {
        "artifact_state": "integrated",
        "installed_entities": len(entity_by_id),
        "installed_sources": len(source_by_id),
        "promoted_events": len(owned),
    }


def wave8_honduran_rebels_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_HONDURAN_REBELS_CONTRACTS.values(),
                    *WAVE8_HONDURAN_REBELS_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_honduran_rebels_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_HONDURAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_nonrating_records": len(
            WAVE8_HONDURAN_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "discovery_twins": len(WAVE8_HONDURAN_REBELS_DISCOVERY_TWINS),
        "hced_discovery_records": len(
            WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES
        ),
        "holds": len(WAVE8_HONDURAN_REBELS_HOLDS),
        "integration_dispositions": len(
            WAVE8_HONDURAN_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_discovery_records": len(
            WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES
        ),
        "new_entities": len(WAVE8_HONDURAN_REBELS_ENTITIES),
        "new_source_families": len(
            {source["source_family_id"] for source in WAVE8_HONDURAN_REBELS_SOURCES}
        ),
        "new_sources": len(WAVE8_HONDURAN_REBELS_SOURCES),
        "newly_rated_events": len(WAVE8_HONDURAN_REBELS_CONTRACTS),
        "outcome_overrides": 0,
        "parent_coverage_records": len(
            WAVE8_HONDURAN_REBELS_PARENT_COVERAGE_ROW_HASHES
        ),
        "point_quarantine_additions": len(
            WAVE8_HONDURAN_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_HONDURAN_REBELS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_HONDURAN_REBELS_RESERVED_IDS),
        "terminal_exclusions": 0,
        "unknown_discovery_outcomes": (
            len(WAVE8_HONDURAN_REBELS_HCED_DISCOVERY_ROW_HASHES)
            + len(WAVE8_HONDURAN_REBELS_IWBD_DISCOVERY_ROW_HASHES)
        ),
    }


def wave8_honduran_rebels_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_HONDURAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_HONDURAN_REBELS_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_honduran_rebels_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_honduran_rebels_counts(),
        "cohorts": wave8_honduran_rebels_cohort_counts(),
        "country_quarantine_candidate_ids": sorted(
            WAVE8_HONDURAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_HONDURAN_REBELS_INTEGRATION_DISPOSITIONS.items()
            )
        ],
        "final_audit_signature": WAVE8_HONDURAN_REBELS_FINAL_AUDIT_SIGNATURE,
        "hold_candidate_ids": sorted(WAVE8_HONDURAN_REBELS_HOLD_IDS),
        "point_quarantine_candidate_ids": sorted(
            WAVE8_HONDURAN_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "promoted_candidate_ids": sorted(WAVE8_HONDURAN_REBELS_CONTRACT_IDS),
        "related_event_boundaries": WAVE8_HONDURAN_REBELS_RELATED_EVENT_BOUNDARIES,
        "source_family_count": len(
            {source["source_family_id"] for source in WAVE8_HONDURAN_REBELS_SOURCES}
        ),
    }


_validate_static()
