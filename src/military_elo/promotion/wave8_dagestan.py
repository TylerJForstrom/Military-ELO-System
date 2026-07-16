"""Exact Wave 8 audit for HCED's generic ``Dagestan`` cohort.

The six reviewed rows span two distinct imamate regimes.  This lane binds the
1831 engagement to Ghazi Muhammad's Dagestani Imamate and the 1839--1853
engagements to Shamil's Caucasian Imamate.  It deliberately opens no generic
``Dagestan`` alias and carries no rating across the intervening succession.
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
    "WAVE8_DAGESTAN_CONTRACT_IDS",
    "WAVE8_DAGESTAN_CONTRACTS",
    "WAVE8_DAGESTAN_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_DAGESTAN_CROSS_LANE_DISPOSITIONS",
    "WAVE8_DAGESTAN_ENTITIES",
    "WAVE8_DAGESTAN_EXPECTED_CANDIDATE_IDS",
    "WAVE8_DAGESTAN_FINAL_AUDIT_SIGNATURE",
    "WAVE8_DAGESTAN_HOLD_IDS",
    "WAVE8_DAGESTAN_HOLDS",
    "WAVE8_DAGESTAN_INTEGRATION_DISPOSITIONS",
    "WAVE8_DAGESTAN_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_DAGESTAN_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_DAGESTAN_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_DAGESTAN_OUTCOME_OVERRIDES",
    "WAVE8_DAGESTAN_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_DAGESTAN_RESERVED_IDS",
    "WAVE8_DAGESTAN_SOURCES",
    "install_wave8_dagestan_entities",
    "install_wave8_dagestan_sources",
    "promote_wave8_dagestan_contracts",
    "validate_wave8_dagestan_integration_dispositions",
    "validate_wave8_dagestan_queue_contracts",
    "wave8_dagestan_audit_signature",
    "wave8_dagestan_cohort_counts",
    "wave8_dagestan_counts",
    "wave8_dagestan_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Dagestan imamate regimes"
_EVENT_ID_PREFIX = "hced_wave8_dagestan_"
_RUSSIAN_EMPIRE_ID = "russian_empire"
_GHAZI_IMAMATE_ID = "dagestani_imamate_ghazi_muhammad_1829_1832"
_SHAMIL_IMAMATE_ID = "caucasian_imamate_shamil_1834_1859"


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


WAVE8_DAGESTAN_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_dagestan_gammer_muslim_resistance",
        "Muslim Resistance to the Tsar: Shamil and the Conquest of Chechnia and Daghestan",
        (
            "https://api.pageplace.de/preview/"
            "DT0400.9781135308988_A24427534/preview-9781135308988_A24427534.pdf"
        ),
        "Routledge",
        "scholarly_monograph_preview",
        "gammer_muslim_resistance_monograph",
        crosscheck=True,
    ),
    _source(
        "wave8_dagestan_milyutin_1839",
        "Description of the Military Operations of 1839 in Northern Dagestan",
        "https://rusneb.ru/catalog/000199_000009_003542331/",
        "National Electronic Library of Russia; 1850 Military Educational Press edition",
        "digitized_participant_military_history",
        "milyutin_north_dagestan_1839",
        crosscheck=True,
    ),
    _source(
        "wave8_dagestan_bre_akhulgo",
        "Storming of Akhulgo, 1839",
        "https://old.bigenc.ru/domestic_history/text/1842769",
        "Great Russian Encyclopedia",
        "scholarly_encyclopedia",
        "great_russian_encyclopedia_akhulgo",
        crosscheck=True,
    ),
    _source(
        "wave8_dagestan_takhnaeva_akhulgo",
        "Akhulgo: On the Failed Peace Negotiations According to Local Chronicles and Official Russian Sources",
        "https://doi.org/10.32653/CH16185-103",
        "History, Archeology and Ethnography of the Caucasus",
        "peer_reviewed_historical_article",
        "takhnaeva_akhulgo_2020",
        crosscheck=True,
    ),
    _source(
        "wave8_dagestan_tdv_shamil",
        "Seyh Samil",
        "https://islamansiklopedisi.org.tr/seyh-samil",
        "TDV Encyclopedia of Islam",
        "scholarly_encyclopedia",
        "tdv_islam_encyclopedia_shamil",
        crosscheck=True,
    ),
    _source(
        "wave8_dagestan_nplg_orbeliani_chronology",
        "The Chronology of Grigol Orbeliani's Life and Work",
        (
            "https://dspace.nplg.gov.ge/bitstream/1234/327868/1/"
            "TheChronologyOfGrigolOrbelianisLifeAndWork.pdf"
        ),
        "National Parliamentary Library of Georgia",
        "institutional_historical_chronology",
        "nplg_orbeliani_chronology",
        crosscheck=True,
    ),
    _source(
        "wave8_dagestan_hadji_ali_eyewitness",
        "Hadji-Ali: An Eyewitness Account of Shamil's Gazavat",
        (
            "https://www.historycaucasus.com/blog/"
            "hadji-ali-an-eyewitness-account-of-shamils-gazavat"
        ),
        "Historical Memory of the North Caucasus; translated primary account",
        "translated_near_contemporary_primary_account",
        "hadji_ali_eyewitness_account",
        crosscheck=True,
    ),
    _source(
        "wave8_dagestan_bse_caucasian_war",
        "Caucasian War, 1817-1864",
        "https://www.booksite.ru/fulltext/1/001/008/057/377.htm",
        "Great Soviet Encyclopedia digital transcription",
        "scholarly_encyclopedia",
        "great_soviet_encyclopedia_caucasian_war",
        crosscheck=True,
    ),
)


WAVE8_DAGESTAN_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _GHAZI_IMAMATE_ID,
        "name": "Dagestani Imamate under Ghazi Muhammad",
        "kind": "theocratic_imamate",
        "start_year": 1829,
        "end_year": 1832,
        "region": "Northeastern Caucasus",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Regime-bounded imamate from Ghazi Muhammad's proclamation as imam "
            "of Dagestan in 1829 through his death at Gimrah in 1832. No rating "
            "is inherited by a generic Dagestan label, Hamza Bek's intervening "
            "regime, Shamil's later imamate, any ethnic community, or a modern state."
        ),
        "source_ids": ["wave8_dagestan_gammer_muslim_resistance"],
    },
    {
        "id": _SHAMIL_IMAMATE_ID,
        "name": "Caucasian Imamate under Imam Shamil",
        "kind": "theocratic_imamate",
        "start_year": 1834,
        "end_year": 1859,
        "region": "Northeastern Caucasus",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Regime-bounded Caucasian Imamate from Shamil's proclamation in "
            "September 1834 through his surrender in 1859. No rating is inherited "
            "by a generic Dagestan or Murid label, either earlier imam, Chechnya, "
            "any constituent people, or a modern state."
        ),
        "source_ids": [
            "wave8_dagestan_gammer_muslim_resistance",
            "wave8_dagestan_hadji_ali_eyewitness",
            "wave8_dagestan_tdv_shamil",
        ],
    },
)


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


_ROW_HASHES = {
    "hced-Aghdash Awkh1831-1": (
        "5635a7072bf490c68cf2d692e429ab59ee88afbedebae681aead7c3bdf3e1130"
    ),
    "hced-Akhulgo1839-1": (
        "483b74e08c8da8308115a51462f852a26f377a63907986109c3caf19d5693a68"
    ),
    "hced-Burtinah1839-1": (
        "c5cc816acd0ee80ee738cb2edfee935859c0612873b31e355b735ff7f5380f79"
    ),
    "hced-Girgil1847-1": (
        "a571f76e08358a4871d253ea40c9c6cd7e455b3d53f6b188af96f5e289e5abeb"
    ),
    "hced-Saltah1847-1": (
        "cd3afc6860b7ac4d3390ff279e93d17cfa31ef4926e91b658800a77f7b0a4a2e"
    ),
    "hced-Zakataly1853-1": (
        "72be61df57fa08a282ad29b8cc7b78392e59ae833ba058538956b24a93b90972"
    ),
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: list[str],
    side_2_entity_ids: list[str],
    winner_side: int,
    evidence_refs: list[str],
    outcome_source_ids: list[str],
    outcome_source_family_ids: list[str],
    audit_note: str,
    *,
    confidence: float,
    source_outcome_override: bool = False,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": side_1_entity_ids,
        "side_2_entity_ids": side_2_entity_ids,
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": sorted(evidence_refs),
        "outcome_source_ids": sorted(outcome_source_ids),
        "outcome_source_family_ids": sorted(outcome_source_family_ids),
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": source_outcome_override,
        "actor_override": True,
        "audit_note": audit_note,
    }


WAVE8_DAGESTAN_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Aghdash Awkh1831-1": _contract(
        "hced-Aghdash Awkh1831-1",
        _canonical("Battle of Aghdash 'Awkh", 1831, "13 July 1831"),
        "ghazi_muhammad_northern_dagestan_campaign_1831",
        [_GHAZI_IMAMATE_ID],
        [_RUSSIAN_EMPIRE_ID],
        1,
        ["wave8_dagestan_gammer_muslim_resistance"],
        ["wave8_dagestan_gammer_muslim_resistance"],
        ["gammer_muslim_resistance_monograph"],
        (
            "Gammer's archival chronology records the Russian relief force as "
            "defeated at Aghdash 'Awkh on 13 July. The victor is Ghazi Muhammad's "
            "1829-1832 imamate, not a timeless Dagestan polity. HCED's Azerbaijan "
            "point and country are incompatible with the documented 'Awkh setting."
        ),
        confidence=0.91,
    ),
    "hced-Akhulgo1839-1": _contract(
        "hced-Akhulgo1839-1",
        _canonical(
            "Siege of Akhulgo",
            1839,
            "24 June-11 September 1839",
            date_precision="day_range",
        ),
        "grabbe_northern_dagestan_campaign_1839",
        [_RUSSIAN_EMPIRE_ID],
        [_SHAMIL_IMAMATE_ID],
        1,
        [
            "wave8_dagestan_bre_akhulgo",
            "wave8_dagestan_gammer_muslim_resistance",
            "wave8_dagestan_milyutin_1839",
            "wave8_dagestan_takhnaeva_akhulgo",
        ],
        [
            "wave8_dagestan_bre_akhulgo",
            "wave8_dagestan_gammer_muslim_resistance",
            "wave8_dagestan_milyutin_1839",
            "wave8_dagestan_takhnaeva_akhulgo",
        ],
        [
            "gammer_muslim_resistance_monograph",
            "great_russian_encyclopedia_akhulgo",
            "milyutin_north_dagestan_1839",
            "takhnaeva_akhulgo_2020",
        ],
        (
            "Grabbe's army eventually stormed and occupied Akhulgo after the long "
            "siege; Shamil escaped, but the tactical fortress result was Russian. "
            "The staged point is about forty kilometres from Akhulgo and is withheld."
        ),
        confidence=0.95,
    ),
    "hced-Burtinah1839-1": _contract(
        "hced-Burtinah1839-1",
        _canonical("Battle of Burtinah (Burtunai)", 1839, "5 June 1839"),
        "grabbe_northern_dagestan_campaign_1839",
        [_RUSSIAN_EMPIRE_ID],
        [_SHAMIL_IMAMATE_ID],
        1,
        [
            "wave8_dagestan_gammer_muslim_resistance",
            "wave8_dagestan_milyutin_1839",
        ],
        [
            "wave8_dagestan_gammer_muslim_resistance",
            "wave8_dagestan_milyutin_1839",
        ],
        [
            "gammer_muslim_resistance_monograph",
            "milyutin_north_dagestan_1839",
        ],
        (
            "Milyutin's campaign account records the highlanders driven back "
            "toward Burtunai and pursued; Gammer dates the battle to 5 June. The "
            "HCED point is in Azerbaijan, roughly 270 km from Burtunai in Dagestan, "
            "so both point and modern-country fields are withheld."
        ),
        confidence=0.92,
    ),
    "hced-Girgil1847-1": _contract(
        "hced-Girgil1847-1",
        _canonical(
            "Battle of Girgil (Gergebil)",
            1847,
            "13-20 June 1847",
            date_precision="day_range",
        ),
        "vorontsov_dagestan_campaign_1847",
        [_RUSSIAN_EMPIRE_ID],
        [_SHAMIL_IMAMATE_ID],
        2,
        [
            "wave8_dagestan_gammer_muslim_resistance",
            "wave8_dagestan_tdv_shamil",
        ],
        [
            "wave8_dagestan_gammer_muslim_resistance",
            "wave8_dagestan_tdv_shamil",
        ],
        [
            "gammer_muslim_resistance_monograph",
            "tdv_islam_encyclopedia_shamil",
        ],
        (
            "Both scholarly chronologies describe Vorontsov's week-long 1847 "
            "assault on Girgil/Gergebil as repulsed with heavy Russian losses. "
            "HCED's Russian winner is therefore reversed on direct evidence. The "
            "staged point is far south of Gergebil and is withheld."
        ),
        confidence=0.93,
        source_outcome_override=True,
    ),
    "hced-Saltah1847-1": _contract(
        "hced-Saltah1847-1",
        _canonical(
            "Siege of Saltah (Salta)",
            1847,
            "6 August-27 September 1847",
            date_precision="day_range",
        ),
        "vorontsov_dagestan_campaign_1847",
        [_RUSSIAN_EMPIRE_ID],
        [_SHAMIL_IMAMATE_ID],
        1,
        [
            "wave8_dagestan_gammer_muslim_resistance",
            "wave8_dagestan_hadji_ali_eyewitness",
            "wave8_dagestan_nplg_orbeliani_chronology",
        ],
        [
            "wave8_dagestan_gammer_muslim_resistance",
            "wave8_dagestan_hadji_ali_eyewitness",
            "wave8_dagestan_nplg_orbeliani_chronology",
        ],
        [
            "gammer_muslim_resistance_monograph",
            "hadji_ali_eyewitness_account",
            "nplg_orbeliani_chronology",
        ],
        (
            "The siege ended with Russian occupation and destruction of Salta; "
            "the defending naibs broke out only with heavy losses. The HCED point "
            "matches the documented village closely and is retained."
        ),
        confidence=0.93,
    ),
    "hced-Zakataly1853-1": _contract(
        "hced-Zakataly1853-1",
        _canonical(
            "Battle of Zaqatala",
            1853,
            "25 August 1853 Old Style (6 September New Style)",
        ),
        "shamil_zaqatala_campaign_1853",
        [_RUSSIAN_EMPIRE_ID],
        [_SHAMIL_IMAMATE_ID],
        1,
        [
            "wave8_dagestan_bse_caucasian_war",
            "wave8_dagestan_hadji_ali_eyewitness",
            "wave8_dagestan_nplg_orbeliani_chronology",
        ],
        [
            "wave8_dagestan_bse_caucasian_war",
            "wave8_dagestan_hadji_ali_eyewitness",
            "wave8_dagestan_nplg_orbeliani_chronology",
        ],
        [
            "great_soviet_encyclopedia_caucasian_war",
            "hadji_ali_eyewitness_account",
            "nplg_orbeliani_chronology",
        ],
        (
            "Orbeliani's smaller Russian force repelled Shamil near Zaqatala and "
            "the Imamate force withdrew into the mountains. The dual date records "
            "the contemporary Russian Old Style convention; the staged Azerbaijan "
            "point is close to Zaqatala and is retained."
        ),
        confidence=0.91,
    ),
}


WAVE8_DAGESTAN_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_DAGESTAN_CONTRACT_IDS = frozenset(WAVE8_DAGESTAN_CONTRACTS)
WAVE8_DAGESTAN_HOLD_IDS = frozenset(WAVE8_DAGESTAN_HOLDS)
WAVE8_DAGESTAN_RESERVED_IDS = WAVE8_DAGESTAN_CONTRACT_IDS | WAVE8_DAGESTAN_HOLD_IDS
WAVE8_DAGESTAN_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


WAVE8_DAGESTAN_POINT_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Aghdash Awkh1831-1",
        "hced-Akhulgo1839-1",
        "hced-Burtinah1839-1",
        "hced-Girgil1847-1",
    }
)
WAVE8_DAGESTAN_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Aghdash Awkh1831-1",
        "hced-Burtinah1839-1",
    }
)
WAVE8_DAGESTAN_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_DAGESTAN_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_DAGESTAN_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_DAGESTAN_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Girgil1847-1": {
        "raw_winner_label": "Russia",
        "raw_loser_label": "Dagestan",
        "corrected_winner_side": 2,
        "corrected_winner_entity_ids": [_SHAMIL_IMAMATE_ID],
        "outcome_source_ids": [
            "wave8_dagestan_gammer_muslim_resistance",
            "wave8_dagestan_tdv_shamil",
        ],
        "outcome_source_family_ids": [
            "gammer_muslim_resistance_monograph",
            "tdv_islam_encyclopedia_shamil",
        ],
        "correction_note": (
            "Gammer and the TDV Encyclopedia both describe Vorontsov's "
            "June 1847 assault on Girgil/Gergebil as repulsed."
        ),
    }
}


# No exact or plausible IWBD twin exists in the locked snapshot.  The aliases
# and years below make that negative audit fail closed if a later snapshot adds
# an unreviewed probable duplicate.
WAVE8_DAGESTAN_IWBD_ZERO_OVERLAP_AUDIT: dict[str, tuple[str, ...]] = {
    "1831": (
        "aghdash awkh",
        "aghdash awkh battle",
        "aktash aukh",
        "battle of aghdash awkh",
    ),
    "1839": (
        "akhoulgo",
        "akhulgo",
        "battle of burtinah",
        "battle of burtunai",
        "burtinah",
        "burtunai",
        "siege of akhoulgo",
        "siege of akhulgo",
    ),
    "1847": (
        "battle of gergebil",
        "battle of girgil",
        "gergebil",
        "girgil",
        "salta",
        "saltah",
        "siege of salta",
        "siege of saltah",
    ),
    "1853": ("battle of zakataly", "battle of zaqatala", "zakataly", "zaqatala"),
}
WAVE8_DAGESTAN_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_DAGESTAN_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_DAGESTAN_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_DAGESTAN_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_DAGESTAN_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_DAGESTAN_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_DAGESTAN_ENTITIES,
        "expected_candidate_ids": sorted(WAVE8_DAGESTAN_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_DAGESTAN_HOLDS,
        "integration_dispositions": WAVE8_DAGESTAN_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_DAGESTAN_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_DAGESTAN_IWBD_ZERO_OVERLAP_AUDIT,
        "outcome_overrides": WAVE8_DAGESTAN_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_DAGESTAN_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_DAGESTAN_SOURCES,
    }


def wave8_dagestan_audit_signature() -> str:
    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


# Patched after the final payload is measured.
WAVE8_DAGESTAN_FINAL_AUDIT_SIGNATURE = (
    "e36dab58ac2c80149cfc1be8af387b7ad6591390a39b3d3780454f97f6d02b1c"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_DAGESTAN_CONTRACTS), len(WAVE8_DAGESTAN_HOLDS)) != (6, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_DAGESTAN_ENTITIES), len(WAVE8_DAGESTAN_SOURCES)) != (2, 8):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_DAGESTAN_RESERVED_IDS != WAVE8_DAGESTAN_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_DAGESTAN_CONTRACT_IDS & WAVE8_DAGESTAN_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotions and holds overlap")
    if wave8_dagestan_audit_signature() != WAVE8_DAGESTAN_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_DAGESTAN_SOURCES}
    if len(source_by_id) != len(WAVE8_DAGESTAN_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_DAGESTAN_SOURCES:
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_DAGESTAN_ENTITIES}
    if set(entity_by_id) != {_GHAZI_IMAMATE_ID, _SHAMIL_IMAMATE_ID}:
        raise ValueError(f"{_LANE_NAME} identity inventory changed")
    expected_windows = {
        _GHAZI_IMAMATE_ID: (1829, 1832),
        _SHAMIL_IMAMATE_ID: (1834, 1859),
    }
    for entity_id, entity in entity_by_id.items():
        if (entity["start_year"], entity["end_year"]) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} identity window changed")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if str(entity["name"]).casefold() == "dagestan":
            raise ValueError(f"{_LANE_NAME} created a generic Dagestan identity")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_new_entities: set[str] = set()
    allowed_entities = {_RUSSIAN_EMPIRE_ID, *entity_by_id}
    used_sources: set[str] = set()
    override_ids: set[str] = set()
    for candidate_id, contract in WAVE8_DAGESTAN_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        row_hash = str(contract["raw_row_sha256"])
        if len(row_hash) != 64 or any(c not in "0123456789abcdef" for c in row_hash):
            raise ValueError(f"{_LANE_NAME} has an invalid queue hash")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["granularity"] != "engagement":
            raise ValueError(f"{_LANE_NAME} promoted a non-engagement")

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= allowed_entities:
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        used_new_entities.update((set(side_1) | set(side_2)) & set(entity_by_id))
        year = int(canonical["year_low"])
        for entity_id in (set(side_1) | set(side_2)) & set(entity_by_id):
            start, end = expected_windows[entity_id]
            if not start <= year <= end:
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")

        if contract["result_type"] != "win" or contract["winner_side"] not in {1, 2}:
            raise ValueError(f"{_LANE_NAME} invented a draw or unknown result")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")
        if contract["outcome_reversal"] is not contract["source_outcome_override"]:
            raise ValueError(f"{_LANE_NAME} outcome reversal metadata drifted")
        if contract["source_outcome_override"]:
            override_ids.add(candidate_id)

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

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")
    used_sources.update(
        source_id
        for entity in WAVE8_DAGESTAN_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if override_ids != set(WAVE8_DAGESTAN_OUTCOME_OVERRIDES):
        raise ValueError(f"{_LANE_NAME} outcome override inventory drifted")
    for candidate_id, metadata in WAVE8_DAGESTAN_OUTCOME_OVERRIDES.items():
        contract = WAVE8_DAGESTAN_CONTRACTS[candidate_id]
        if (
            metadata["corrected_winner_side"] != contract["winner_side"]
            or metadata["corrected_winner_entity_ids"]
            != contract[f"side_{contract['winner_side']}_entity_ids"]
            or metadata["outcome_source_ids"] != contract["outcome_source_ids"]
            or metadata["outcome_source_family_ids"]
            != contract["outcome_source_family_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome override metadata drifted")

    expected_points = {
        "hced-Aghdash Awkh1831-1",
        "hced-Akhulgo1839-1",
        "hced-Burtinah1839-1",
        "hced-Girgil1847-1",
    }
    expected_countries = {
        "hced-Aghdash Awkh1831-1",
        "hced-Burtinah1839-1",
    }
    if WAVE8_DAGESTAN_POINT_QUARANTINE_ADDITIONS != expected_points:
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_DAGESTAN_COUNTRY_QUARANTINE_ADDITIONS != expected_countries:
        raise ValueError(f"{_LANE_NAME} country quarantine contract changed")
    if not (expected_points | expected_countries) <= WAVE8_DAGESTAN_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} quarantine references an unowned row")
    if (
        WAVE8_DAGESTAN_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_DAGESTAN_CROSS_LANE_DISPOSITIONS
        or WAVE8_DAGESTAN_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate disposition audit changed")


def validate_wave8_dagestan_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_DAGESTAN_CONTRACTS,
        WAVE8_DAGESTAN_HOLDS,
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


def validate_wave8_dagestan_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin the reviewed HCED inventory and fail on a future IWBD probable twin."""

    validate_wave8_dagestan_queue_contracts(hced_rows)
    audited = {
        (int(year), normalize_label(name))
        for year, names in WAVE8_DAGESTAN_IWBD_ZERO_OVERLAP_AUDIT.items()
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


def install_wave8_dagestan_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_DAGESTAN_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_dagestan_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_DAGESTAN_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_DAGESTAN_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_DAGESTAN_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_dagestan_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_dagestan_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_DAGESTAN_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_dagestan_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_DAGESTAN_CONTRACTS.values()
            ).items()
        )
    )


def wave8_dagestan_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_DAGESTAN_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_DAGESTAN_CROSS_LANE_DISPOSITIONS
        ),
        "holds": len(WAVE8_DAGESTAN_HOLDS),
        "integration_dispositions": len(WAVE8_DAGESTAN_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_DAGESTAN_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_DAGESTAN_ENTITIES),
        "new_sources": len(WAVE8_DAGESTAN_SOURCES),
        "newly_rated_events": len(WAVE8_DAGESTAN_CONTRACTS),
        "outcome_overrides": len(WAVE8_DAGESTAN_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_DAGESTAN_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_DAGESTAN_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_DAGESTAN_RESERVED_IDS),
    }


def wave8_dagestan_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_DAGESTAN_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_DAGESTAN_POINT_QUARANTINE_ADDITIONS,
    }
