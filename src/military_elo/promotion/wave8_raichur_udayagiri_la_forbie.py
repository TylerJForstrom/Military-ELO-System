"""Exact contracts for Raichur, Udayagiri, and La Forbie.

This lane promotes three fingerprinted HCED candidates without opening any
label alias or changing an identity window.  Raichur activates the existing
time-bounded Vijayanagara registry identity and reuses the released Bijapur
identity.  Udayagiri adds only its event-bounded Gajapati garrison.  La Forbie
uses four event-bounded formations so HCED's misspelling ``Abasid`` cannot
become an identity or resolver rule.

Ten neighboring rows remain explicit unknown-result holds.  Two outcome-less
Wikidata records are discovery-only duplicates, three additional HCED rows are
scope/ownership boundaries, and all promoted points are withheld while modern
country and source provenance remain available.  Unknown is never a draw.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_egypt_forces import WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ADJACENT_HCED_DISPOSITIONS",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_ROW_HASHES",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_TWINS",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_EXPECTED_RAW_OUTCOMES",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FINAL_AUDIT_SIGNATURE",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_ABSENT_LABELS",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_AUDIT",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLD_IDS",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LABEL_INVENTORY",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LOCATION_QUARANTINE_REASONS",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_RESERVED_IDS",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ROW_HASHES",
    "WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_SOURCES",
    "install_wave8_raichur_udayagiri_la_forbie_entities",
    "install_wave8_raichur_udayagiri_la_forbie_sources",
    "promote_wave8_raichur_udayagiri_la_forbie_contracts",
    "validate_wave8_raichur_udayagiri_la_forbie_current_artifact_state",
    "validate_wave8_raichur_udayagiri_la_forbie_discovery_dispositions",
    "validate_wave8_raichur_udayagiri_la_forbie_funnel",
    "validate_wave8_raichur_udayagiri_la_forbie_integration_dispositions",
    "validate_wave8_raichur_udayagiri_la_forbie_queue_contracts",
    "wave8_raichur_udayagiri_la_forbie_audit_signature",
    "wave8_raichur_udayagiri_la_forbie_cohort_counts",
    "wave8_raichur_udayagiri_la_forbie_counts",
    "wave8_raichur_udayagiri_la_forbie_metadata",
)


_LANE_NAME = "Wave 8 exact Raichur-Udayagiri-La Forbie audit"
_MODULE_OWNER = "military_elo.promotion.wave8_raichur_udayagiri_la_forbie"
_EVENT_ID_PREFIX = "hced_wave8_raichur_udayagiri_la_forbie_"

_VIJAYANAGARA = "clio_in_vijayanagara_emp_1344_0fe07dd4"
_BIJAPUR = "clio_in_bijapur_sultanate_1492_49a19c59"
_UDAYAGIRI_GARRISON = "tirumala_routaraya_gajapati_udayagiri_garrison_1513_1514"
_EGYPTIAN_AYYUBID = "al_salih_ayyub_egyptian_field_army_la_forbie_1244"
_KHWARAZMIAN_MERCENARIES = "khwarazmian_mercenary_contingent_la_forbie_1244"
_FRANKISH_HOST = "frankish_jerusalem_military_orders_host_la_forbie_1244"
_SYRIAN_AYYUBID_COALITION = "ayyubid_damascus_homs_kerak_coalition_la_forbie_1244"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-20",
        "source_family_id": source_family_id,
        "evidence_roles": ["identity_boundary_or_context_reference", "outcome"],
    }


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_rulf_eaton_raichur",
        (
            "Richard M. Eaton, ‘Kiss My Foot,’ Said the King: Firearms, "
            "Diplomacy, and the Battle for Raichur, 1520"
        ),
        "https://doi.org/10.1017/S0026749X07003289",
        "Cambridge University Press, Modern Asian Studies",
        "peer_reviewed_history_article",
        "eaton_battle_raichur_2009",
    ),
    _source(
        "wave8_rulf_sewell_paes_nuniz",
        (
            "Robert Sewell, A Forgotten Empire (Vijayanagar), including the "
            "Paes and Nuniz chronicles"
        ),
        "https://www.gutenberg.org/ebooks/3310",
        "Swan Sonnenschein / Project Gutenberg",
        "translated_primary_chronicles",
        "paes_nuniz_sewell_vijayanagara_chronicles",
    ),
    _source(
        "wave8_rulf_asi_udayagiri_epigraphy",
        (
            "Archaeological Survey of India historical and epigraphic "
            "compilation: Udayagiri campaign records"
        ),
        "https://ignca.gov.in/Asi_data/35371.pdf",
        "Archaeological Survey of India / IGNCA digital scan",
        "official_epigraphic_reference",
        "archaeological_survey_india_udayagiri_epigraphy",
    ),
    _source(
        "wave8_rulf_rao_shulman_subrahmanyam",
        (
            "Velcheru Narayana Rao, David Shulman, and Sanjay Subrahmanyam, "
            "A New Imperial Idiom in the Sixteenth Century"
        ),
        "https://books.openedition.org/ifp/7916",
        "Institut Français de Pondichéry / OpenEdition Books",
        "scholarly_history_chapter",
        "rao_shulman_subrahmanyam_vijayanagara",
    ),
    _source(
        "wave8_rulf_jackson_la_forbie",
        "Peter Jackson, The Crusades of 1239–41 and Their Aftermath",
        "https://doi.org/10.1017/S0041977X00053180",
        "Cambridge University Press, Bulletin of SOAS",
        "peer_reviewed_history_article",
        "jackson_crusades_1239_1241_aftermath",
    ),
    _source(
        "wave8_rulf_karakus_demirci_la_forbie",
        (
            "Nadir Karakuş and Mustafa Demirci, The Capture of al-Quds by the "
            "Khwarizm Turks and the Victory of La Forbie in 1244"
        ),
        "https://dergipark.org.tr/en/pub/did/article/1551219",
        "Diyanet İlmi Dergi / DergiPark",
        "peer_reviewed_history_article",
        "karakus_demirci_la_forbie_2024",
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source
    for source in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_SOURCES
}

_RAICHUR_SOURCES = ("wave8_rulf_eaton_raichur", "wave8_rulf_sewell_paes_nuniz")
_UDAYAGIRI_SOURCES = (
    "wave8_rulf_asi_udayagiri_epigraphy",
    "wave8_rulf_rao_shulman_subrahmanyam",
)
_LA_FORBIE_SOURCES = (
    "wave8_rulf_jackson_la_forbie",
    "wave8_rulf_karakus_demirci_la_forbie",
)


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


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _VIJAYANAGARA,
        "Vijayanagara Empire",
        "empire",
        1344,
        1571,
        "South India and the Deccan",
        ["cliopatria_v020", *_RAICHUR_SOURCES, *_UDAYAGIRI_SOURCES],
        (
            "Activates the existing 1344–1571 Cliopatria registry interval "
            "without changing either boundary. Only fingerprinted exact contracts "
            "may use it; the raw spellings Vijayanagar and Vijayanagara acquire no "
            "resolver alias, and no predecessor or successor inherits Elo."
        ),
    ),
    _entity(
        _UDAYAGIRI_GARRISON,
        "Tirumala Routaraya's Gajapati garrison at Udayagiri (1513–1514)",
        "military_formation",
        1513,
        1514,
        "Udayagiri, present-day Andhra Pradesh",
        _UDAYAGIRI_SOURCES,
        (
            "Event-bounded defending formation for the 1513–1514 siege only. "
            "It is not generic Orissa, the Gajapati state across time, another "
            "Udayagiri, or a continuity bridge to any predecessor or successor."
        ),
    ),
    _entity(
        _EGYPTIAN_AYYUBID,
        "al-Salih Ayyub's Egyptian Ayyubid field army at La Forbie (1244)",
        "military_formation",
        1244,
        1244,
        "La Forbie near Gaza",
        _LA_FORBIE_SOURCES,
        (
            "Event-bounded Egyptian Ayyubid formation at La Forbie only. It is "
            "not a generic Egypt identity, an Abbasid identity, or a vehicle for "
            "rating another Ayyubid army."
        ),
    ),
    _entity(
        _KHWARAZMIAN_MERCENARIES,
        "Displaced Khwarazmian mercenary contingent at La Forbie (1244)",
        "military_formation",
        1244,
        1244,
        "La Forbie near Gaza",
        _LA_FORBIE_SOURCES,
        (
            "Event-bounded post-imperial mercenary contingent at La Forbie. It "
            "does not inherit the Khwarezmid Empire's rating or extend that state "
            "identity beyond its reviewed use."
        ),
    ),
    _entity(
        _FRANKISH_HOST,
        "Frankish Jerusalem and military-orders host at La Forbie (1244)",
        "military_coalition",
        1244,
        1244,
        "La Forbie near Gaza",
        _LA_FORBIE_SOURCES,
        (
            "Event-bounded Kingdom of Jerusalem and military-orders host at La "
            "Forbie only; no timeless Crusader or Jerusalem polity is created."
        ),
    ),
    _entity(
        _SYRIAN_AYYUBID_COALITION,
        "Ayyubid Damascus–Homs–Kerak coalition at La Forbie (1244)",
        "military_coalition",
        1244,
        1244,
        "La Forbie near Gaza",
        _LA_FORBIE_SOURCES,
        (
            "Event-bounded Syrian Ayyubid coalition at La Forbie only. It does "
            "not merge Damascus, Homs, Kerak, Abbasid rule, or Ayyubid regimes "
            "outside this battle."
        ),
    ),
)


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ROW_HASHES: dict[str, str] = {
    "hced-Farrukhabad1750-1": "3f1b89b8269db2f53deb87a4c9b72c6f523f142248f5298349e123e36cd766c1",
    "hced-Farrukhabad1751-1": "858092c21e902294aff947057a9b88c59efacb600d34ecbaf3d806a15b10fefb",
    "hced-Herat1221-1222-1": "f57299531562b320db4ce2882a8ecc859ea50fb81008bdc543dcddf7ef282331",
    "hced-Kasganj1750-1": "82c8eeb3be1e1b0cc19725a35f3e50f4d3cc71bb93e9c401dfb4945b0a9b1387",
    "hced-Kauthal1367-1": "b135e849d3dacc8aca8dd1ba9a12556658d16b501523c4f959835be320fc5c7e",
    "hced-Krishna1398-1": "0f367d024e8ea6f2a865bc55b63e6d2c23b8f68ddacf45a6ae42f9ba2e5951c0",
    "hced-La Forbie1244-1": "20a67c1b608dda91d32ee2b32531da0ecd41898432d1b38270d37e33c334a487",
    "hced-Mudgal1443-1": "09fd28b80158bead63301e9565242e4af9c1b634a146102b2c24ca1cc9024a24",
    "hced-Nishapur1221-1": "b0b3923e46c824aad599653e29aadf61d4ee0d4dd846492d3e4005dbdbdfe7ae",
    "hced-Pangul1418-1": "f1a5f1e7c868ea82a42859df32b6330033d28dd69045ae3e492e1ceea114fb5e",
    "hced-Raichur1520-1": "44d7584ef815e646ac21ef903c211e95d578778cc70a5e08b60432363e6b6ea2",
    "hced-Udayagiri1513-1514-1": "736e492f0cfe215b4aed2e576ca156a74c381e597beb13e6469b9f8c7715fd8c",
    "hced-Vijayanagar1406-1": "9bb325ce0df2da438e60ab07178e9b3be722c1acf40748a4b3c6987c1cc4aee1",
}


def _raw(
    low: int,
    best: int,
    high: int,
    side_1: str | None,
    side_2: str | None,
    winner: str | None,
    loser: str | None,
    winner_loser_complete: bool,
    massacre: str,
) -> dict[str, Any]:
    return {
        "year_low": low,
        "year_best": best,
        "year_high": high,
        "side_1_raw": side_1,
        "side_2_raw": side_2,
        "winner_raw": winner,
        "loser_raw": loser,
        "winner_loser_complete": winner_loser_complete,
        "massacre_raw": massacre,
    }


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_EXPECTED_RAW_OUTCOMES: dict[
    str, dict[str, Any]
] = {
    "hced-Raichur1520-1": _raw(
        1520, 1520, 1520, "Vijayanagar", "Bijapur", "Vijayanagar", "Bijapur", True, "No"
    ),
    "hced-Udayagiri1513-1514-1": _raw(
        1513, 1514, 1514, "Vijayanagar", "Orissa", "Vijayanagar", "Orissa", True, "No"
    ),
    "hced-La Forbie1244-1": _raw(
        1244,
        1244,
        1244,
        "Khwarezm Empire, Abasid Sultan of Egypt",
        "Abasid Sultan of Damascus, Kingdom of Jerusalem",
        "Khwarezm Empire, Abasid Sultan of Egypt",
        "Abasid Sultan of Damascus, Kingdom of Jerusalem",
        True,
        "No",
    ),
    "hced-Kauthal1367-1": _raw(
        1367, 1367, 1367, "Bahmani Sultanate", "Vijayanagar", "Bahmani Sultanate", "Vijayanagar", True, "No"
    ),
    "hced-Krishna1398-1": _raw(
        1398, 1398, 1398, "Bahmani", "Vijayanagar", "Bahmani", "Vijayanagar", True, "No"
    ),
    "hced-Mudgal1443-1": _raw(
        1443, 1443, 1443, "Bahman", "Vijayanagar", "Bahman", "Vijayanagar", True, "No"
    ),
    "hced-Pangul1418-1": _raw(
        1418, 1418, 1418, "Vijayanagar", "Bahman", "Vijayanagar", "Bahman", True, "No"
    ),
    "hced-Vijayanagar1406-1": _raw(
        1406, 1406, 1406, "Bahman", "Vijayanagar", "Bahman", "Vijayanagar", True, "No"
    ),
    "hced-Farrukhabad1750-1": _raw(
        1750, 1750, 1750, "Pathans", "Mughal Empire", "Pathans", "Mughal Empire", True, "No"
    ),
    "hced-Kasganj1750-1": _raw(
        1750,
        1750,
        1750,
        "Pathans",
        "Mughal Wazir of Delhi",
        "Pathans",
        "Mughal Wazir of Delhi",
        True,
        "Battle followed by massacre",
    ),
    "hced-Farrukhabad1751-1": _raw(
        1751, 1751, 1751, "Marathas", "Pathans", "Marathas", "Pathans", True, "No"
    ),
    "hced-Herat1221-1222-1": _raw(
        1221, 1222, 1222, None, None, None, None, False, "Battle followed by massacre"
    ),
    "hced-Nishapur1221-1": _raw(
        1221, 1221, 1221, "Mongols", "Persia", "Mongols", "Persia", True, "Battle followed by massacre"
    ),
}


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LABEL_INVENTORY: dict[
    str, tuple[str, ...]
] = {
    "abasid sultan of damascus kingdom of jerusalem": ("hced-La Forbie1244-1",),
    "bahman": (
        "hced-Mudgal1443-1",
        "hced-Pangul1418-1",
        "hced-Vijayanagar1406-1",
    ),
    "bahmani": ("hced-Krishna1398-1",),
    "bahmani sultanate": ("hced-Kauthal1367-1", "hced-Kherla1428-1"),
    "bijapur": (
        "hced-Gingee1648-1",
        "hced-Koppal1677-1",
        "hced-Nesri1674-1",
        "hced-Panhala1660-1",
        "hced-Panhala1673-1",
        "hced-Ponda1675-1",
        "hced-Pratabgarh1659-1",
        "hced-Raichur1520-1",
        "hced-Tiruvadi1677-1",
        "hced-Umrani1673-1",
        "hced-Vellore1677-1678-1",
    ),
    "khwarezm empire abasid sultan of egypt": ("hced-La Forbie1244-1",),
    "orissa": ("hced-Udayagiri1513-1514-1",),
    "pathans": (
        "hced-Farrukhabad1750-1",
        "hced-Farrukhabad1751-1",
        "hced-Kasganj1750-1",
    ),
    "vijayanagar": (
        "hced-Kauthal1367-1",
        "hced-Kondavidu1515-1",
        "hced-Krishna1398-1",
        "hced-Mudgal1443-1",
        "hced-Pangul1418-1",
        "hced-Raichur1520-1",
        "hced-Talikota1565-1",
        "hced-Udayagiri1513-1514-1",
        "hced-Vijayanagar1406-1",
    ),
}


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "abasid sultan of damascus kingdom of jerusalem": {
        "candidate_ids": [],
        "event_candidate_id_sha256": "7e72c01b0e8d120e9b16da700f64e0e431220d45ede52b1162eef4d32d9b463b",
        "events_touched": 1,
        "label": "abasid sultan of damascus kingdom of jerusalem",
        "rated_counterpart_entities": 0,
        "sole_blocker_events": 0,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 1,
        "zero_time_valid_candidates": 1,
    },
    "bahman": {
        "candidate_ids": [],
        "event_candidate_id_sha256": "60d5593679fd2d7d9e84f9332a834852b1230732a17370fa719f86b2d795e887",
        "events_touched": 3,
        "label": "bahman",
        "rated_counterpart_entities": 0,
        "sole_blocker_events": 1,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 3,
        "zero_time_valid_candidates": 3,
    },
    "bijapur": {
        "candidate_ids": [],
        "event_candidate_id_sha256": "9101bb964c4972f5cbcf05bad1d36626652c3581f3b22e832ee61b5f9b8ed07d",
        "events_touched": 6,
        "label": "bijapur",
        "rated_counterpart_entities": 0,
        "sole_blocker_events": 0,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 6,
        "zero_time_valid_candidates": 6,
    },
    "orissa": {
        "candidate_ids": [],
        "event_candidate_id_sha256": "db70c548c82078bede310e51720b59b8628c94f5bd56bade592662a1ff6e6197",
        "events_touched": 1,
        "label": "orissa",
        "rated_counterpart_entities": 0,
        "sole_blocker_events": 0,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 1,
        "zero_time_valid_candidates": 1,
    },
    "pathans": {
        "candidate_ids": [],
        "event_candidate_id_sha256": "ae3f026c3f6123e642e6a039ea197f4b090631cc731db221f86e5b1449155f66",
        "events_touched": 3,
        "label": "pathans",
        "rated_counterpart_entities": 2,
        "sole_blocker_events": 2,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 3,
        "zero_time_valid_candidates": 3,
    },
    "vijayanagar": {
        "candidate_ids": [],
        "event_candidate_id_sha256": "704d203083f7eeeefd390cf6a8483cd46acdedaaac041fd966a4f2fe78cefcc1",
        "events_touched": 6,
        "label": "vijayanagar",
        "rated_counterpart_entities": 0,
        "sole_blocker_events": 2,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 6,
        "zero_time_valid_candidates": 6,
    },
}

WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_ABSENT_LABELS = frozenset(
    {"bahmani", "bahmani sultanate", "khwarezm empire abasid sultan of egypt"}
)


def _canonical(
    name: str,
    low: int,
    high: int,
    date_text: str,
    date_precision: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{low}:{high}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": low,
        "year_high": high,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    source_ids: Iterable[str],
    event_evidence_roles: Mapping[str, str],
    audit_note: str,
    *,
    confidence: float,
    war_type: str,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, source_ids)))
    return {
        "raw_row_sha256": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "event_evidence_roles": {
            source_id: str(event_evidence_roles[source_id]) for source_id in outcomes
        },
        "source_date_override": False,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_exact_existing_or_event_bounded_actors",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Raichur1520-1": _contract(
        "hced-Raichur1520-1",
        _canonical(
            "Battle of Raichur (1520)",
            1520,
            1520,
            "1520",
            "year",
            "pitched_battle_and_fortress_capture",
        ),
        "south_india_exact_promotions_1513_1520",
        [_VIJAYANAGARA],
        [_BIJAPUR],
        _RAICHUR_SOURCES,
        {
            "wave8_rulf_eaton_raichur": (
                "Identifies Krishna Raya's Vijayanagara army against Isma'il "
                "Adil Shah's Bijapur force and Bijapur as the defeated side."
            ),
            "wave8_rulf_sewell_paes_nuniz": (
                "The independent Paes/Nuniz chronicle family records "
                "Krishnadevaraya's Raichur campaign and victory."
            ),
        },
        (
            "Two independent families support the Vijayanagara tactical victory "
            "and recovery of Raichur from Bijapur. HCED participant noise naming "
            "Bahmani is not mapped to an actor."
        ),
        confidence=0.96,
        war_type="interstate",
    ),
    "hced-Udayagiri1513-1514-1": _contract(
        "hced-Udayagiri1513-1514-1",
        _canonical(
            "Siege and Capture of Udayagiri",
            1513,
            1514,
            "1513–1514",
            "year_range",
            "siege_and_capture",
        ),
        "south_india_exact_promotions_1513_1520",
        [_VIJAYANAGARA],
        [_UDAYAGIRI_GARRISON],
        _UDAYAGIRI_SOURCES,
        {
            "wave8_rulf_asi_udayagiri_epigraphy": (
                "Official epigraphic chronology records Krishnadevaraya's siege "
                "and the Vijayanagara capture of Udayagiri."
            ),
            "wave8_rulf_rao_shulman_subrahmanyam": (
                "Independent scholarship reconstructs the eastern campaign and "
                "Vijayanagara capture of Udayagiri."
            ),
        },
        (
            "The locked 1513–1514 interval is retained. The losing actor is the "
            "event-bounded Gajapati garrison, not the unbounded geographic label "
            "Orissa."
        ),
        confidence=0.94,
        war_type="interstate",
    ),
    "hced-La Forbie1244-1": _contract(
        "hced-La Forbie1244-1",
        _canonical(
            "Battle of La Forbie",
            1244,
            1244,
            "1244",
            "year",
            "pitched_battle",
        ),
        "la_forbie_exact_promotion_1244",
        [_EGYPTIAN_AYYUBID, _KHWARAZMIAN_MERCENARIES],
        [_FRANKISH_HOST, _SYRIAN_AYYUBID_COALITION],
        _LA_FORBIE_SOURCES,
        {
            "wave8_rulf_jackson_la_forbie": (
                "Independent scholarship records the Frankish army's severe "
                "defeat by the Egyptian and Khwarazmian allies."
            ),
            "wave8_rulf_karakus_demirci_la_forbie": (
                "Identifies the Khwarazmian-Egyptian victory over the Crusader "
                "and Damascus-Homs-Kerak alliance."
            ),
        },
        (
            "The decisive tactical coalition victory is rated with four exact "
            "formation identities. HCED's 'Abasid' coding error is preserved only "
            "in raw provenance and creates no alias. Disputed calendar dates from "
            "the discovery twin are not imported."
        ),
        confidence=0.92,
        war_type="interstate_religious",
    ),
}


def _hold(
    candidate_id: str,
    cohort: str,
    hold_category: str,
    hold_reason: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ROW_HASHES[candidate_id],
        "cohort": cohort,
        "disposition": "hold",
        "hold_category": hold_category,
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "evidence_refs": [],
        "hold_reason": hold_reason,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "review_hold_owner",
        },
    }


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Kauthal1367-1": _hold(
        "hced-Kauthal1367-1",
        "south_india_bahmani_scope_holds_1367_1443",
        "locked_year_conflicts_with_unreconciled_campaign_chronology",
        "The locked 1367 date is not reconciled with the competing 1366 chronology; no silent redate or widened interval is allowed.",
    ),
    "hced-Krishna1398-1": _hold(
        "hced-Krishna1398-1",
        "south_india_bahmani_scope_holds_1367_1443",
        "river_or_campaign_label_not_bounded_engagement",
        "Krishna is a river/campaign label and the staged row does not establish one independently bounded engagement.",
    ),
    "hced-Mudgal1443-1": _hold(
        "hced-Mudgal1443-1",
        "south_india_bahmani_scope_holds_1367_1443",
        "multiple_actions_with_changing_tactical_results",
        "The source tradition describes multiple actions and changing tactical winners before settlement; the row collapses them into one result.",
    ),
    "hced-Pangul1418-1": _hold(
        "hced-Pangul1418-1",
        "south_india_bahmani_scope_holds_1367_1443",
        "siege_counteroffensive_chronology_not_exact",
        "The siege and counteroffensive chronology does not establish an exact 1418 event contract.",
    ),
    "hced-Vijayanagar1406-1": _hold(
        "hced-Vijayanagar1406-1",
        "south_india_bahmani_scope_holds_1367_1443",
        "campaign_and_peace_not_single_battle",
        "Sources support a campaign and imposed peace, not a clean single battle; the queued point is also not a reviewed battlefield position.",
    ),
    "hced-Farrukhabad1750-1": _hold(
        "hced-Farrukhabad1750-1",
        "pathan_campaign_scope_holds_1750_1751",
        "competing_action_ownership_unresolved",
        "Participant strings mix Farrukhabad and Kasganj and do not safely assign this row between the distinct Khudaganj and Ram Chatauni actions.",
    ),
    "hced-Kasganj1750-1": _hold(
        "hced-Kasganj1750-1",
        "pathan_campaign_scope_holds_1750_1751",
        "competing_action_ownership_and_massacre_scope_unresolved",
        "The row collides with the neighboring 1750 record and combines battle with massacre; provenance does not establish which row owns which action.",
    ),
    "hced-Farrukhabad1751-1": _hold(
        "hced-Farrukhabad1751-1",
        "pathan_campaign_scope_holds_1750_1751",
        "multiple_actions_and_coalition_not_binary",
        "The record mixes Farrukhabad and Qadirganj and a Maratha–Awadh/Jat coalition; its binary actors are not safely bounded.",
    ),
    "hced-Herat1221-1222-1": _hold(
        "hced-Herat1221-1222-1",
        "khwarazm_adjacent_terminal_holds_1221_1222",
        "missing_sides_and_outcome_with_massacre_composite",
        "Both sides, winner, and loser are null; participant tokens and a battle-followed-by-massacre marker cannot create a competitive outcome.",
    ),
    "hced-Nishapur1221-1": _hold(
        "hced-Nishapur1221-1",
        "khwarazm_adjacent_terminal_holds_1221_1222",
        "generic_persia_actor_and_massacre_composite",
        "Khwarazmian appears only in participant noise while the raw loser is generic Persia and the row combines battle with city massacre.",
    ),
}


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS = frozenset(
    WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS
)
WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLD_IDS = frozenset(
    WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS
)
WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_RESERVED_IDS = frozenset(
    {
        *WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS,
        *WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLD_IDS,
    }
)


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ADJACENT_HCED_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "hced-Ascalon1247-1": {
        "raw_row_sha256": "96edaef632dfb8471c32c521375ea72573605d087bdf315de0bbbec232017779",
        "disposition": "existing_exact_release_owner",
        "owner_event_id": "hced_wave8_egypt_forces_hced_ascalon1247_1",
        "reason": "Distinct 1247 Ayyubid siege already owned by the Egypt-forces lane; it is not La Forbie.",
    },
    "hced-Kuban1222-1": {
        "raw_row_sha256": "278d9cede9f067fb731c945069ebf12b207f20524aa466676540b01477f760a6",
        "disposition": "distinct_actor_pair_remains_out_of_scope",
        "owner_event_id": None,
        "reason": "The queued actors are Mongols and Georgia; Khwarezmian occurs only in campaign-context participant noise.",
    },
    "hced-Otranto1917-1": {
        "raw_row_sha256": "f8fa2ca48628bd9d70c86a057034c8c6d16cc994325f6baaea22b6b871a8ce77",
        "disposition": "unrelated_existing_release_owner",
        "owner_event_id": "hced_hced_otranto1917_1",
        "reason": "World War I naval event; Otrar/Khwarezm text in participants is extraction contamination, not an actor.",
    },
}


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS
)
WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = (
    frozenset()
)
WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the named action and modern country "
            "but do not independently verify HCED's exact coordinate. Retain "
            "country and source provenance while withholding point geometry."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(
        WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS.items()
    )
}


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_TWINS: dict[str, str] = {
    "hced-La Forbie1244-1": "Q578201",
    "hced-Raichur1520-1": "Q4872151",
}
WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q4872151": "31243c7de4a2d73524b30c3f244a4f56c19a58a91fea60cc55fcc9b6512e12c6",
    "Q578201": "d8a0d2af592c6b315ef9df752f5a814909f81c0957e9fdeef116dd27d53fde23",
}


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_IWBD_ZERO_OVERLAP_AUDIT: dict[
    str, dict[str, Any]
] = {
    "hced-La Forbie1244-1": {
        "aliases": [
            "al harbiyah",
            "battle of forbie",
            "battle of la forbie",
            "forbie",
            "harbiyah",
            "la forbie",
        ],
        "years": [1244, 1244],
    },
    "hced-Raichur1520-1": {
        "aliases": ["battle of raichur", "raichur", "siege of raichur"],
        "years": [1520, 1520],
    },
    "hced-Udayagiri1513-1514-1": {
        "aliases": ["capture of udayagiri", "siege of udayagiri", "udayagiri"],
        "years": [1513, 1514],
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_hced_dispositions": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ADJACENT_HCED_DISPOSITIONS,
        "contracts": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS,
        "discovery_row_hashes": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_ROW_HASHES,
        "discovery_twins": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_TWINS,
        "entities": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES,
        "expected_raw_outcomes": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_EXPECTED_RAW_OUTCOMES,
        "funnel": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_AUDIT,
        "funnel_absent_labels": sorted(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_ABSENT_LABELS),
        "holds": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS,
        "iwbd_zero_overlap_audit": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_IWBD_ZERO_OVERLAP_AUDIT,
        "label_inventory": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LABEL_INVENTORY,
        "location_reasons": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ROW_HASHES,
        "sources": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_SOURCES,
    }


def wave8_raichur_udayagiri_la_forbie_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FINAL_AUDIT_SIGNATURE = (
    "af7110f2421a78c3b308cb7ebb192f5cb4939169f875b05a51aa2bba905923c7"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if any(
        not str(source["url"]).startswith("https://")
        or not source["source_family_id"]
        or source["evidence_roles"]
        != ["identity_boundary_or_context_reference", "outcome"]
        for source in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_SOURCES
    ):
        raise ValueError(f"{_LANE_NAME} source fixture drift")
    if len(
        {str(source["source_family_id"]) for source in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_SOURCES}
    ) != len(source_ids):
        raise ValueError(f"{_LANE_NAME} source families are not independent")

    expected_entity_ids = {
        _VIJAYANAGARA,
        _UDAYAGIRI_GARRISON,
        _EGYPTIAN_AYYUBID,
        _KHWARAZMIAN_MERCENARIES,
        _FRANKISH_HOST,
        _SYRIAN_AYYUBID_COALITION,
    }
    entities = {
        str(entity["id"]): entity
        for entity in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES
    }
    if set(entities) != expected_entity_ids:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    for entity in entities.values():
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} broad alias or continuity bridge opened")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity source order drift")
        if "abasid" in normalize_label(entity["name"]):
            raise ValueError(f"{_LANE_NAME} HCED coding error became an identity")
    if (
        entities[_VIJAYANAGARA]["start_year"],
        entities[_VIJAYANAGARA]["end_year"],
    ) != (1344, 1571):
        raise ValueError(f"{_LANE_NAME} Vijayanagara window drift")
    if (
        entities[_UDAYAGIRI_GARRISON]["start_year"],
        entities[_UDAYAGIRI_GARRISON]["end_year"],
    ) != (1513, 1514):
        raise ValueError(f"{_LANE_NAME} Udayagiri window drift")
    for entity_id in {
        _EGYPTIAN_AYYUBID,
        _KHWARAZMIAN_MERCENARIES,
        _FRANKISH_HOST,
        _SYRIAN_AYYUBID_COALITION,
    }:
        if (entities[entity_id]["start_year"], entities[entity_id]["end_year"]) != (
            1244,
            1244,
        ):
            raise ValueError(f"{_LANE_NAME} La Forbie identity window drift")

    if WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS & WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_RESERVED_IDS != set(
        WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ROW_HASHES
    ) or WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_RESERVED_IDS != set(
        WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_EXPECTED_RAW_OUTCOMES
    ):
        raise ValueError(f"{_LANE_NAME} exact disposition inventory drift")
    expected_actor_pairs = {
        "hced-Raichur1520-1": ({_VIJAYANAGARA}, {_BIJAPUR}),
        "hced-Udayagiri1513-1514-1": ({_VIJAYANAGARA}, {_UDAYAGIRI_GARRISON}),
        "hced-La Forbie1244-1": (
            {_EGYPTIAN_AYYUBID, _KHWARAZMIAN_MERCENARIES},
            {_FRANKISH_HOST, _SYRIAN_AYYUBID_COALITION},
        ),
    }
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_date_override"]
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome or date override drift: {candidate_id}")
        sides = (
            set(map(str, contract["side_1_entity_ids"])),
            set(map(str, contract["side_2_entity_ids"])),
        )
        if sides != expected_actor_pairs[candidate_id]:
            raise ValueError(f"{_LANE_NAME} actor drift: {candidate_id}")
        canonical = contract["canonical_event"]
        expected_raw = WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_EXPECTED_RAW_OUTCOMES[candidate_id]
        if (canonical["year_low"], canonical["year_high"]) != (
            expected_raw["year_low"],
            expected_raw["year_high"],
        ):
            raise ValueError(f"{_LANE_NAME} canonical year drift: {candidate_id}")
        outcomes = list(map(str, contract["outcome_source_ids"]))
        evidence = list(map(str, contract["evidence_refs"]))
        if (
            len(outcomes) != 2
            or not _is_sorted_unique(outcomes)
            or outcomes != evidence
            or not set(outcomes) <= source_ids
            or set(contract["event_evidence_roles"]) != set(outcomes)
            or any(not str(role).strip() for role in contract["event_evidence_roles"].values())
        ):
            raise ValueError(f"{_LANE_NAME} evidence closure drift: {candidate_id}")
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families or len(families) != 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(outcomes)
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    for candidate_id, hold in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS.items():
        if (
            hold["disposition"] != "hold"
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
            or hold["evidence_refs"]
            or not hold["hold_category"]
            or not hold["hold_reason"]
        ):
            raise ValueError(f"{_LANE_NAME} hold drift: {candidate_id}")

    if (
        WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_POINT_QUARANTINE_ADDITIONS
        != WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS
        or WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_COUNTRY_QUARANTINE_ADDITIONS
        or set(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LOCATION_QUARANTINE_REASONS)
        != WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location policy drift")
    if set(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_TWINS) != {
        "hced-Raichur1520-1",
        "hced-La Forbie1244-1",
    } or set(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_TWINS.values()) != set(
        WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} discovery inventory drift")
    if set(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate audit inventory drift")
    for audit in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, audit["aliases"]))
        years = list(map(int, audit["years"]))
        if (
            not _is_sorted_unique(aliases)
            or any(alias != normalize_label(alias) for alias in aliases)
            or len(years) != 2
            or years[0] > years[1]
        ):
            raise ValueError(f"{_LANE_NAME} duplicate audit drift")
    if WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES.get("hced-La Forbie1244-1") != WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ROW_HASHES["hced-La Forbie1244-1"]:
        raise ValueError(f"{_LANE_NAME} Egypt-forces adjacency fingerprint drift")
    if wave8_raichur_udayagiri_la_forbie_audit_signature() != WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def _actor_labels(row: Mapping[str, Any]) -> set[str]:
    return {
        normalize_label(row.get("side_1_raw")),
        normalize_label(row.get("side_2_raw")),
    }


def validate_wave8_raichur_udayagiri_la_forbie_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)

    scoped_hashes = {
        **WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ROW_HASHES,
        **{
            candidate_id: str(disposition["raw_row_sha256"])
            for candidate_id, disposition in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ADJACENT_HCED_DISPOSITIONS.items()
        },
    }
    for candidate_id, expected_hash in scoped_hashes.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} row {candidate_id} expected once, found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")

    for candidate_id, expected in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_EXPECTED_RAW_OUTCOMES.items():
        row = by_id[candidate_id][0]
        if any(row.get(field) != value for field, value in expected.items()):
            raise ValueError(f"{_LANE_NAME} raw outcome changed: {candidate_id}")
        if row.get("do_not_rate_automatically") is not True or row.get("duplicate_source_id") is not False:
            raise ValueError(f"{_LANE_NAME} queue review guard changed: {candidate_id}")

    for candidate_id in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS:
        row = by_id[candidate_id][0]
        if (
            row.get("winner_loser_complete") is not True
            or row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
            or row.get("massacre_raw") != "No"
            or normalize_label(row.get("winner_raw")) in {"draw", "inconclusive", "stalemate"}
        ):
            raise ValueError(f"{_LANE_NAME} promotable outcome guard changed: {candidate_id}")

    actual_label_inventory = {
        label: tuple(
            sorted(
                str(row.get("candidate_id"))
                for row in hced_rows
                if label in _actor_labels(row)
            )
        )
        for label in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LABEL_INVENTORY
    }
    if actual_label_inventory != WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LABEL_INVENTORY:
        raise ValueError(f"{_LANE_NAME} literal label inventory changed")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS,
        WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "adjacent_hced_rows": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ADJACENT_HCED_DISPOSITIONS),
        "literal_label_inventories": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_LABEL_INVENTORY),
        "reviewed_hced_rows_with_adjacency": len(scoped_hashes),
    }


def validate_wave8_raichur_udayagiri_la_forbie_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    labels = {str(row.get("label")): row for row in funnel.get("labels", [])}
    for absent in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_ABSENT_LABELS:
        if absent in labels:
            raise ValueError(f"{_LANE_NAME} formerly absent funnel label appeared: {absent}")
    for label, expected in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_AUDIT.items():
        row = labels.get(label)
        if row is None:
            raise ValueError(f"{_LANE_NAME} funnel label disappeared: {label}")
        actual = {
            "candidate_ids": list(map(str, row.get("candidate_ids", []))),
            "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
            "events_touched": int(row.get("events_touched", -1)),
            "label": str(row.get("label")),
            "rated_counterpart_entities": int(row.get("rated_counterpart_entities", -1)),
            "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
            "time_valid_candidate_ids": list(map(str, row.get("time_valid_candidate_ids", []))),
            "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
            "zero_time_valid_candidates": int(
                row.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
            ),
        }
        if actual != expected:
            raise ValueError(f"{_LANE_NAME} funnel pin changed for {label}: {actual}")
    return {
        "audited_labels": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_AUDIT),
        "events_touched": sum(
            int(row["events_touched"])
            for row in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_AUDIT.values()
        ),
        "sole_blocker_events": sum(
            int(row["sole_blocker_events"])
            for row in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_AUDIT.values()
        ),
        "unresolved_side_attempts": sum(
            int(row["unresolved_side_attempts"])
            for row in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FUNNEL_AUDIT.values()
        ),
    }


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def validate_wave8_raichur_udayagiri_la_forbie_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_ROW_HASHES.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} discovery row {candidate_id} expected once, found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}")
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("review_status") != "needs_review"
            or row.get("winners") != []
        ):
            raise ValueError(f"{_LANE_NAME} discovery non-rating guard changed: {candidate_id}")
    forbie = by_id["Q578201"][0]
    if (
        forbie.get("date") != "1244-10-24T00:00:00Z"
        or forbie.get("end_date") != "1244-10-25T00:00:00Z"
        or not forbie.get("participants")
    ):
        raise ValueError(f"{_LANE_NAME} La Forbie discovery context drift")
    raichur = by_id["Q4872151"][0]
    if raichur.get("date") != "1520-05-01T00:00:00Z" or raichur.get("participants") != []:
        raise ValueError(f"{_LANE_NAME} Raichur discovery context drift")
    return {
        "discovery_nonrating_twins": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_ROW_HASHES),
        "discovery_promotions": 0,
        "unknown_winner_rows": 2,
    }


def _row_years(row: Mapping[str, Any]) -> range:
    low: int | None = None
    high: int | None = None
    for field in ("year", "year_best", "year_low", "batyear"):
        try:
            if row.get(field) is not None:
                low = int(row[field])
                break
        except (TypeError, ValueError):
            pass
    for field in ("end_year", "year_high"):
        try:
            if row.get(field) is not None:
                high = int(row[field])
                break
        except (TypeError, ValueError):
            pass
    if low is None:
        for field in ("start_date", "date", "end_date"):
            text = str(row.get(field) or "")
            if len(text) >= 4 and text[:4].isdigit():
                low = int(text[:4])
                break
    if low is None:
        return range(0)
    if high is None:
        high = low
    return range(low, high + 1)


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


_DUPLICATE_MATCH_KEYS = frozenset(
    (year, alias)
    for audit in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    names = _row_names(row)
    return any((year, name) in _DUPLICATE_MATCH_KEYS for year in _row_years(row) for name in names)


def validate_wave8_raichur_udayagiri_la_forbie_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
    iwd_rows: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_raichur_udayagiri_la_forbie_queue_contracts(hced_rows)
    events = list(existing_events)
    event_by_candidate = {
        str(event["hced_candidate_id"]): event
        for event in events
        if event.get("hced_candidate_id") is not None
    }
    lane_overlap = WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS & set(event_by_candidate)
    if len(lane_overlap) not in {0, len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS)}:
        raise ValueError(f"{_LANE_NAME} partial release integration")
    for candidate_id in lane_overlap:
        if not str(event_by_candidate[candidate_id].get("id", "")).startswith(_EVENT_ID_PREFIX):
            raise ValueError(f"{_LANE_NAME} release owner drift: {candidate_id}")

    if events:
        for candidate_id, disposition in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ADJACENT_HCED_DISPOSITIONS.items():
            owner_id = disposition["owner_event_id"]
            owner = event_by_candidate.get(candidate_id)
            if owner_id is None:
                if owner is not None:
                    raise ValueError(f"{_LANE_NAME} adjacent no-owner row was promoted: {candidate_id}")
            elif owner is None or str(owner.get("id")) != owner_id:
                raise ValueError(f"{_LANE_NAME} adjacent release owner drift: {candidate_id}")

    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in {
            *WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_RESERVED_IDS,
            *WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ADJACENT_HCED_DISPOSITIONS,
        }
        and _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    iwd_twins = sorted(
        str(row.get("candidate_id") or row.get("id") or "<missing-id>")
        for row in iwd_rows
        if _is_probable_twin(row)
    )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in events
        if event.get("hced_candidate_id")
        not in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS
        and _is_probable_twin(event)
    )
    if hced_twins or iwbd_twins or iwd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, iwbd={iwbd_twins}, "
            f"iwd={iwd_twins}, release={release_twins}"
        )
    return {
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwd_probable_twins": 0,
        "iwbd_probable_twins": 0,
        "release_lane_overlap": len(lane_overlap),
    }


def install_wave8_raichur_udayagiri_la_forbie_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_raichur_udayagiri_la_forbie_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_raichur_udayagiri_la_forbie_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_raichur_udayagiri_la_forbie_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def _records_by_id(
    records: Iterable[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    return {str(record["id"]): record for record in records}


def validate_wave8_raichur_udayagiri_la_forbie_current_artifact_state(
    release_entities: Iterable[Mapping[str, Any]],
    release_events: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
    release_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Require entities, sources, events, and metadata to move together."""

    _validate_static()
    entity_by_id = _records_by_id(release_entities)
    source_by_id = _records_by_id(release_sources)
    events = list(release_events)
    expected_entity_ids = {
        str(entity["id"])
        for entity in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES
    }
    expected_source_ids = set(_SOURCE_BY_ID)
    entity_overlap = expected_entity_ids & set(entity_by_id)
    source_overlap = expected_source_ids & set(source_by_id)
    target_events = [
        event
        for event in events
        if event.get("hced_candidate_id")
        in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS
    ]
    prefixed_events = [
        event
        for event in events
        if str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    promotion = release_metadata.get("promotion", {}) if release_metadata is not None else {}
    marker = "accepted_wave8_raichur_udayagiri_la_forbie_hced_events"
    marker_present = marker in promotion
    any_present = bool(
        entity_overlap or source_overlap or target_events or prefixed_events or marker_present
    )
    if not any_present:
        return {
            "entity_records": 0,
            "event_records": 0,
            "integration_state": "preintegration",
            "metadata_marker": 0,
            "source_records": 0,
        }

    fully_present = (
        entity_overlap == expected_entity_ids
        and source_overlap == expected_source_ids
        and len(target_events) == len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS)
        and len(prefixed_events) == len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS)
        and (release_metadata is None or marker_present)
    )
    if not fully_present:
        raise ValueError(f"{_LANE_NAME} partial current-artifact integration")

    expected_entities = {
        str(entity["id"]): entity
        for entity in WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES
    }
    for entity_id, expected in expected_entities.items():
        if entity_by_id[entity_id] != expected:
            raise ValueError(f"{_LANE_NAME} current entity drift: {entity_id}")
    for source_id in expected_source_ids:
        if source_by_id[source_id] != _SOURCE_BY_ID[source_id]:
            raise ValueError(f"{_LANE_NAME} current source drift: {source_id}")

    event_by_candidate = {
        str(event["hced_candidate_id"]): event for event in target_events
    }
    if set(event_by_candidate) != WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} current event inventory drift")
    expected_countries = {
        "hced-La Forbie1244-1": "Israel",
        "hced-Raichur1520-1": "India",
        "hced-Udayagiri1513-1514-1": "India",
    }
    for candidate_id, event in event_by_candidate.items():
        contract = WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS[candidate_id]
        if not str(event.get("id", "")).startswith(_EVENT_ID_PREFIX):
            raise ValueError(f"{_LANE_NAME} current event owner drift: {candidate_id}")
        participant_ids = {
            str(participant.get("entity_id"))
            for participant in event.get("participants", [])
        }
        if participant_ids != {
            *map(str, contract["side_1_entity_ids"]),
            *map(str, contract["side_2_entity_ids"]),
        }:
            raise ValueError(f"{_LANE_NAME} current event actor drift: {candidate_id}")
        if "geometry" in event:
            raise ValueError(f"{_LANE_NAME} quarantined point entered release")
        if event.get("modern_location_country") != expected_countries[candidate_id] or not event.get("location_provenance"):
            raise ValueError(f"{_LANE_NAME} country/provenance drift: {candidate_id}")
        if set(map(str, event.get("outcome_source_ids", []))) != set(
            contract["outcome_source_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance drift: {candidate_id}")

    if release_metadata is not None:
        if int(promotion[marker]) != 3:
            raise ValueError(f"{_LANE_NAME} current metadata count drift")
        candidate_ids = promotion.get("wave8_raichur_udayagiri_la_forbie_candidate_ids")
        if candidate_ids is None or list(map(str, candidate_ids)) != sorted(
            WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS
        ):
            raise ValueError(f"{_LANE_NAME} current metadata inventory drift")

    return {
        "entity_records": len(entity_overlap),
        "event_records": len(target_events),
        "integration_state": "integrated",
        "metadata_marker": 1 if marker_present else 0,
        "source_records": len(source_overlap),
    }


def wave8_raichur_udayagiri_la_forbie_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS.values(),
                    *WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_raichur_udayagiri_la_forbie_counts() -> dict[str, int]:
    _validate_static()
    return {
        "activated_existing_registry_entities": 1,
        "adjacent_hced_dispositions": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ADJACENT_HCED_DISPOSITIONS),
        "country_quarantine_additions": 0,
        "discovery_nonrating_twins": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_ROW_HASHES),
        "holds": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLDS),
        "identity_window_changes": 0,
        "new_aliases": 0,
        "new_event_bounded_entities": 5,
        "new_sources": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_SOURCES),
        "newly_rated_events": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACTS),
        "release_entity_additions": len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ENTITIES),
        "reviewed_hced_rows": (
            len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_RESERVED_IDS)
            + len(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ADJACENT_HCED_DISPOSITIONS)
        ),
        "terminal_exclusions": 0,
    }


def wave8_raichur_udayagiri_la_forbie_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "adjacent_hced_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_ADJACENT_HCED_DISPOSITIONS.items()
            )
        ],
        "cohorts": wave8_raichur_udayagiri_la_forbie_cohort_counts(),
        "counts": wave8_raichur_udayagiri_la_forbie_counts(),
        "discovery_nonrating_candidate_ids": sorted(
            WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_DISCOVERY_ROW_HASHES
        ),
        "final_audit_signature": WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_FINAL_AUDIT_SIGNATURE,
        "hold_candidate_ids": sorted(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_HOLD_IDS),
        "promoted_candidate_ids": sorted(WAVE8_RAICHUR_UDAYAGIRI_LA_FORBIE_CONTRACT_IDS),
    }


_validate_static()
