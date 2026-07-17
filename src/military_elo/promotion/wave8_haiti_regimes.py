"""Candidate-keyed Wave 8 audit for HCED's exact ``Haiti`` label.

The five locked rows span three distinct Haitian constitutional regimes and
the creation of the Dominican First Republic.  This lane therefore never
installs a generic ``Haiti`` or ``Dominican Republic`` alias.  Four rows have
independently supported tactical outcomes and are promoted through exact,
time-bounded identities.  The combined Cabeza de Las Marias / Las Hicoteas
row compresses several engagements and incompatible tactical-versus-strategic
descriptions, so its result remains unknown.  Unknown is never a draw.

The 1849 boundary is intentionally exact-date keyed: El Numero occurred on
17 April while Soulouque was still president of the Republic; he was
proclaimed emperor on 26 August.  Both identities mechanically cover 1849
because entity records have year precision, but no label resolver can reach
either identity and only the pinned event contract selects the correct one.
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
    "WAVE8_HAITI_REGIMES_CONTRACT_IDS",
    "WAVE8_HAITI_REGIMES_CONTRACTS",
    "WAVE8_HAITI_REGIMES_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_HAITI_REGIMES_ENTITIES",
    "WAVE8_HAITI_REGIMES_EXPECTED_CANDIDATE_IDS",
    "WAVE8_HAITI_REGIMES_FINAL_AUDIT_SIGNATURE",
    "WAVE8_HAITI_REGIMES_FUNNEL_AUDIT",
    "WAVE8_HAITI_REGIMES_HOLD_IDS",
    "WAVE8_HAITI_REGIMES_HOLDS",
    "WAVE8_HAITI_REGIMES_LOCATION_QUARANTINE_REASONS",
    "WAVE8_HAITI_REGIMES_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_HAITI_REGIMES_RESERVED_IDS",
    "WAVE8_HAITI_REGIMES_ROW_HASHES",
    "WAVE8_HAITI_REGIMES_SOURCES",
    "install_wave8_haiti_regimes_entities",
    "install_wave8_haiti_regimes_sources",
    "promote_wave8_haiti_regimes_contracts",
    "validate_wave8_haiti_regimes_funnel",
    "validate_wave8_haiti_regimes_integration_dispositions",
    "validate_wave8_haiti_regimes_queue_contracts",
    "wave8_haiti_regimes_audit_signature",
    "wave8_haiti_regimes_cohort_counts",
    "wave8_haiti_regimes_counts",
    "wave8_haiti_regimes_location_quarantine_additions",
    "wave8_haiti_regimes_metadata",
)


_LANE_NAME = "Wave 8 exact Haiti constitutional-regime audit"
_MODULE_OWNER = "military_elo.promotion.wave8_haiti_regimes"
_EVENT_ID_PREFIX = "hced_wave8_haiti_regimes_"
_EXACT_LABEL = "haiti"

_FIRST_EMPIRE_HAITI_ID = "first_empire_haiti_1804_1806"
_REPUBLIC_HAITI_ID = "republic_haiti_reunified_1820_1849"
_SECOND_EMPIRE_HAITI_ID = "second_empire_haiti_1849_1859"
_FIRST_DOMINICAN_REPUBLIC_ID = "first_dominican_republic_1844_1861"
_SANTO_DOMINGO_DEFENSE_ID = "ferrand_santo_domingo_defense_1805"


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


WAVE8_HAITI_REGIMES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_haiti_embassy_monarchs",
        "Haitian monarchs: Jacques I",
        "https://embassyofhaiti.eu/haitian-monarchs/",
        "Embassy of the Republic of Haiti",
        "official_state_history",
        "embassy_haiti_monarchs",
        crosscheck=True,
    ),
    _source(
        "wave8_haiti_embassy_faustin",
        "Haitian monarchs: Faustin I",
        "https://embassyofhaiti.eu/haitian-monarchs/4/",
        "Embassy of the Republic of Haiti",
        "official_state_history",
        "embassy_haiti_monarchs",
        crosscheck=True,
    ),
    _source(
        "wave8_haiti_larousse_soulouque",
        "Faustin Soulouque",
        "https://www.larousse.fr/encyclopedie/personnage/Faustin_Soulouque/144938",
        "Larousse",
        "scholarly_encyclopedia",
        "larousse_soulouque",
        crosscheck=True,
    ),
    _source(
        "wave8_haiti_openedition_state_genesis",
        "Genese de l'Etat haitien (1804-1859): constitutions, continuities and ruptures",
        "https://books.openedition.org/editionsmsh/65486",
        "Editions de la Maison des sciences de l'homme / OpenEdition",
        "scholarly_book_chapter",
        "hurbon_genese_etat_haitien",
        crosscheck=True,
    ),
    _source(
        "wave8_haiti_dominican_judiciary_first_republic",
        "The Judicial Branch in the First Republic (1844-1861)",
        "https://poderjudicial.gob.do/sobre-nosotros/historia/",
        "Judicial Branch of the Dominican Republic",
        "official_institutional_history",
        "dominican_judiciary_history",
        crosscheck=True,
    ),
    _source(
        "wave8_haiti_dominican_presidency_independence",
        "National symbols: the first Dominican flag and independence",
        "https://www.presidencia.gob.do/acerca-de-rd/simbolos-patrios",
        "Presidency of the Dominican Republic",
        "official_state_history",
        "dominican_presidency_symbols",
        crosscheck=True,
    ),
    _source(
        "wave8_haiti_clio_independence_2020",
        "A machete o a tiro limpio? De armas blancas y de fuego en la guerra de Independencia",
        "https://catalogo.academiadominicanahistoria.org.do/opac-tmpl/files/ppcodice/Clio-2020-200-075-140.pdf",
        "Academia Dominicana de la Historia, Clio 200",
        "peer_reviewed_historical_article_with_primary_reports",
        "espinal_clio_2020_independence",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haiti_clio_azua_1962",
        "La primera batalla de marzo",
        "https://catalogo.academiadominicanahistoria.org.do/opac-tmpl/files/ppcodice/CLIO-1962-118-119-035-067.pdf",
        "Academia Dominicana de la Historia, Clio 118-119",
        "historical_article_with_dominican_french_and_haitian_accounts",
        "beras_clio_1962_azua",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haiti_clio_el_numero_1950",
        "Documentos para la historia: report of the action at El Numero",
        "https://catalogo.academiadominicanahistoria.org.do/opac-tmpl/files/ppcodice/Clio-1950-018-088-120-140.pdf",
        "Academia Dominicana de la Historia, Clio 88",
        "edited_primary_military_report",
        "clio_1950_el_numero_report",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haiti_clio_sabana_1956",
        "Batalla de Sabana Larga",
        "https://catalogo.academiadominicanahistoria.org.do/opac-tmpl/files/ppcodice/Clio-1956-024-107-128-136.pdf",
        "Academia Dominicana de la Historia, Clio 107",
        "historical_battle_study",
        "ricardo_clio_1956_sabana_larga",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haiti_clio_dessalines_2022",
        "La expedicion haitiana de Dessalines a Santo Domingo en 1805",
        "https://catalogo.academiadominicanahistoria.org.do/opac-tmpl/files/clio/Clio-2022-91-203.pdf",
        "Academia Dominicana de la Historia, Clio 203",
        "peer_reviewed_campaign_history_with_primary_accounts",
        "reyes_clio_2022_dessalines",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haiti_loc_santo_domingo_map",
        "Plan du siege de Santo Domingo par Dessalines, forme et leve en 1805",
        "https://www.loc.gov/resource/g4954s.ct000102/",
        "Library of Congress",
        "contemporary_campaign_map",
        "loc_santo_domingo_1805_map",
        outcome=True,
        crosscheck=True,
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_HAITI_REGIMES_SOURCES}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
    *,
    predecessors: Iterable[str] = (),
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start_year,
        "end_year": end_year,
        "region": region,
        "aliases": [],
        "predecessors": sorted(set(map(str, predecessors))),
        "continuity_note": (
            boundary_note
            + " No generic Haiti, Dominican Republic, France, or campaign label "
            "resolves to this record. Predecessor links are lineage metadata and "
            "transfer no Elo."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_HAITI_REGIMES_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _FIRST_EMPIRE_HAITI_ID,
        "First Empire of Haiti (1804-1806)",
        "empire",
        1804,
        1806,
        "Haiti",
        ["wave8_haiti_embassy_monarchs", "wave8_haiti_clio_dessalines_2022"],
        (
            "Bounded to the independent state proclaimed in 1804 under Jacques I "
            "and ended by Dessalines's death and the 1806 political split."
        ),
    ),
    _entity(
        _REPUBLIC_HAITI_ID,
        "Reunified Republic of Haiti (1820-26 August 1849)",
        "republic",
        1820,
        1849,
        "Haiti and, until 1844, all Hispaniola",
        [
            "wave8_haiti_embassy_faustin",
            "wave8_haiti_larousse_soulouque",
            "wave8_haiti_openedition_state_genesis",
        ],
        (
            "Bounded from reunification after the northern kingdom's collapse in "
            "1820 through Soulouque's imperial proclamation on 26 August 1849. "
            "Its 1849 year overlap with the Second Empire is mechanical only; the "
            "17 April El Numero contract is selected by exact event date."
        ),
    ),
    _entity(
        _SECOND_EMPIRE_HAITI_ID,
        "Second Empire of Haiti (26 August 1849-1859)",
        "empire",
        1849,
        1859,
        "Haiti",
        [
            "wave8_haiti_clio_independence_2020",
            "wave8_haiti_embassy_faustin",
            "wave8_haiti_larousse_soulouque",
        ],
        (
            "Bounded from Faustin I's proclamation on 26 August 1849 through the "
            "fall of the empire in 1859. Its 1849 year overlap with the preceding "
            "Republic is mechanical only; no generic year-only resolution is open."
        ),
        predecessors=[_REPUBLIC_HAITI_ID],
    ),
    _entity(
        _FIRST_DOMINICAN_REPUBLIC_ID,
        "First Dominican Republic (1844-1861)",
        "republic",
        1844,
        1861,
        "Eastern Hispaniola",
        [
            "wave8_haiti_dominican_judiciary_first_republic",
            "wave8_haiti_dominican_presidency_independence",
        ],
        (
            "Bounded from the 27 February 1844 independence proclamation through "
            "the 18 March 1861 annexation to Spain. It is distinct from the 1865 "
            "restored republic and from the modern continuous-country envelope."
        ),
    ),
    _entity(
        _SANTO_DOMINGO_DEFENSE_ID,
        "Ferrand's Santo Domingo defensive force (March 1805)",
        "event_bounded_colonial_defense",
        1805,
        1805,
        "Walled city of Santo Domingo",
        ["wave8_haiti_clio_dessalines_2022", "wave8_haiti_loc_santo_domingo_map"],
        (
            "Bounded to General Jean-Louis Ferrand's French-commanded garrison and "
            "local defenders during the March 1805 siege; it does not stand for "
            "France or Santo Domingo in another action."
        ),
    ),
)


WAVE8_HAITI_REGIMES_ROW_HASHES: dict[str, str] = {
    "hced-Azua1844-1": "2c59fbed65521ed79b5d5b6004c5275db64da25638db65d2f6d97fbae1b6c4cb",
    "hced-Cabeza de las Marias and las Hicoteas1844-1": "60efe67f6f9cff2c3305003890e4c01cc30ce90278fe010caa125266c99eb8b4",
    "hced-El Numero1849-1": "fac408e00c7ebe0beae2880f30a8640bfa254fd48dbcb5be557256b9b92d27a2",
    "hced-Sabana Larga1856-1": "b1e041908f7fcf8f14bb28f203671a43c9929f485b7b2a3e737c1d2757dfc3cf",
    "hced-Santo Domingo1805-1": "100b9326b4d08e44f7e10a2bc51ab70346637df2d57ffa692e551cf4033f36fe",
}

WAVE8_HAITI_REGIMES_FUNNEL_AUDIT: dict[str, Any] = {
    "event_candidate_id_sha256": "d335346c74accdde228bcbb518484d8edb67019c67eb69a90c7f2720d1253baf",
    "events_touched": 5,
    "label": _EXACT_LABEL,
    "sole_blocker_events": 3,
    "zero_time_valid_candidates": 5,
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
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


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1: Iterable[str],
    side_2: Iterable[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    war_type: str = "interstate",
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_HAITI_REGIMES_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_time_bounded_regime_or_force",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_HAITI_REGIMES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Santo Domingo1805-1": _contract(
        "hced-Santo Domingo1805-1",
        _canonical(
            "Siege of Santo Domingo (1805)",
            1805,
            "5-28 March 1805",
            "day_range",
            "three_week_siege_and_haitian_withdrawal",
        ),
        "first_empire_haiti",
        [_SANTO_DOMINGO_DEFENSE_ID],
        [_FIRST_EMPIRE_HAITI_ID],
        1,
        [
            "wave8_haiti_clio_dessalines_2022",
            "wave8_haiti_embassy_monarchs",
            "wave8_haiti_loc_santo_domingo_map",
        ],
        ["wave8_haiti_clio_dessalines_2022", "wave8_haiti_loc_santo_domingo_map"],
        (
            "The reviewed campaign history records that Dessalines failed to take "
            "the fortified city and withdrew after the French squadron appeared; "
            "the contemporary map independently records the siege being lifted. "
            "The win is limited to defense of the city, not the wider campaign."
        ),
        confidence=0.88,
    ),
    "hced-Azua1844-1": _contract(
        "hced-Azua1844-1",
        _canonical(
            "Battle of Azua (19 March 1844)",
            1844,
            "19 March 1844",
            "day",
            "single_battle_and_haitian_withdrawal",
        ),
        "republic_haiti_dominican_first_republic",
        [_FIRST_DOMINICAN_REPUBLIC_ID],
        [_REPUBLIC_HAITI_ID],
        1,
        [
            "wave8_haiti_clio_azua_1962",
            "wave8_haiti_clio_independence_2020",
            "wave8_haiti_dominican_presidency_independence",
            "wave8_haiti_openedition_state_genesis",
        ],
        ["wave8_haiti_clio_azua_1962", "wave8_haiti_clio_independence_2020"],
        (
            "Dominican, French-consular, and Haitian-account synthesis supports a "
            "Dominican battlefield success and Haitian withdrawal at Azua. The "
            "contract does not rate the full independence war."
        ),
        confidence=0.88,
    ),
    "hced-El Numero1849-1": _contract(
        "hced-El Numero1849-1",
        _canonical(
            "Battle of El Numero",
            1849,
            "17 April 1849",
            "day",
            "single_entrenchment_assault_and_haitian_rout",
        ),
        "republic_haiti_dominican_first_republic",
        [_FIRST_DOMINICAN_REPUBLIC_ID],
        [_REPUBLIC_HAITI_ID],
        1,
        [
            "wave8_haiti_clio_el_numero_1950",
            "wave8_haiti_clio_independence_2020",
            "wave8_haiti_embassy_faustin",
            "wave8_haiti_larousse_soulouque",
        ],
        ["wave8_haiti_clio_el_numero_1950", "wave8_haiti_clio_independence_2020"],
        (
            "The 17 April date and French-consular report place the action before "
            "Soulouque's 26 August imperial proclamation and describe the Haitian "
            "army abandoning its entrenchments and artillery."
        ),
        confidence=0.92,
    ),
    "hced-Sabana Larga1856-1": _contract(
        "hced-Sabana Larga1856-1",
        _canonical(
            "Battle of Sabana Larga",
            1856,
            "24 January 1856",
            "day",
            "single_day_battle_and_haitian_rout",
        ),
        "second_empire_haiti_dominican_first_republic",
        [_FIRST_DOMINICAN_REPUBLIC_ID],
        [_SECOND_EMPIRE_HAITI_ID],
        1,
        [
            "wave8_haiti_clio_independence_2020",
            "wave8_haiti_clio_sabana_1956",
            "wave8_haiti_dominican_judiciary_first_republic",
            "wave8_haiti_embassy_faustin",
        ],
        ["wave8_haiti_clio_independence_2020", "wave8_haiti_clio_sabana_1956"],
        (
            "The contemporary Dominican battle report and independent battle study "
            "agree on the 24 January date, defeat, and retreat of Faustin I's army. "
            "The contract is tactical and does not encode the war termination."
        ),
        confidence=0.94,
    ),
}


WAVE8_HAITI_REGIMES_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Cabeza de las Marias and las Hicoteas1844-1": {
        "raw_row_sha256": WAVE8_HAITI_REGIMES_ROW_HASHES[
            "hced-Cabeza de las Marias and las Hicoteas1844-1"
        ],
        "canonical_event": _canonical(
            "Skirmishes at Cabeza de Las Marias and Las Hicoteas",
            1844,
            "13-18 March 1844",
            "day_range",
            "multiple_skirmishes_compressed_into_one_row",
        ),
        "cohort": "republic_haiti_dominican_first_republic",
        "disposition": "hold",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "evidence_refs": [
            "wave8_haiti_clio_azua_1962",
            "wave8_haiti_clio_independence_2020",
        ],
        "hold_reason": (
            "Not promoted: the source row joins Cabeza de Las Marias and Las "
            "Hicoteas across several days. Accounts distinguish a Dominican "
            "withdrawal at one position from delaying or repulsing actions at the "
            "other, while later summaries alternate between a Haitian tactical win "
            "and a Dominican strategic success. One aggregate winner would invent "
            "granularity and certainty; this unknown is not a draw."
        ),
    }
}

WAVE8_HAITI_REGIMES_CONTRACT_IDS = frozenset(WAVE8_HAITI_REGIMES_CONTRACTS)
WAVE8_HAITI_REGIMES_HOLD_IDS = frozenset(WAVE8_HAITI_REGIMES_HOLDS)
WAVE8_HAITI_REGIMES_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_HAITI_REGIMES_ROW_HASHES
)
WAVE8_HAITI_REGIMES_RESERVED_IDS = WAVE8_HAITI_REGIMES_EXPECTED_CANDIDATE_IDS

WAVE8_HAITI_REGIMES_POINT_QUARANTINE_ADDITIONS = WAVE8_HAITI_REGIMES_CONTRACT_IDS
WAVE8_HAITI_REGIMES_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_HAITI_REGIMES_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "HCED supplies a point but the reviewed sources establish the named "
            "engagement or siege, not the exact source coordinate; retain the "
            "modern-country assertion and withhold the unaudited point."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_HAITI_REGIMES_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_HAITI_REGIMES_CONTRACTS,
        "entities": WAVE8_HAITI_REGIMES_ENTITIES,
        "funnel": WAVE8_HAITI_REGIMES_FUNNEL_AUDIT,
        "holds": WAVE8_HAITI_REGIMES_HOLDS,
        "location_reasons": WAVE8_HAITI_REGIMES_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_HAITI_REGIMES_ROW_HASHES,
        "sources": WAVE8_HAITI_REGIMES_SOURCES,
    }


def wave8_haiti_regimes_audit_signature() -> str:
    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_HAITI_REGIMES_FINAL_AUDIT_SIGNATURE = (
    "cb078b4e46fd7bc655585248475d0867ddad24abc0e98a5b6f4c1a2cb28e6394"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if len(_SOURCE_BY_ID) != len(WAVE8_HAITI_REGIMES_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_HAITI_REGIMES_ENTITIES}
    if len(entity_by_id) != len(WAVE8_HAITI_REGIMES_ENTITIES):
        raise ValueError(f"{_LANE_NAME} duplicate entity id")
    if WAVE8_HAITI_REGIMES_CONTRACT_IDS & WAVE8_HAITI_REGIMES_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_HAITI_REGIMES_RESERVED_IDS != WAVE8_HAITI_REGIMES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation drift")
    if WAVE8_HAITI_REGIMES_POINT_QUARANTINE_ADDITIONS != WAVE8_HAITI_REGIMES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point review incomplete")
    if WAVE8_HAITI_REGIMES_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    if set(WAVE8_HAITI_REGIMES_LOCATION_QUARANTINE_REASONS) != WAVE8_HAITI_REGIMES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for entity in WAVE8_HAITI_REGIMES_ENTITIES:
        if entity["aliases"]:
            raise ValueError(f"{_LANE_NAME} opened a generic identity alias")
        source_ids = list(map(str, entity["source_ids"]))
        if not source_ids or not _is_sorted_unique(source_ids):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(source_ids) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} entity references an unknown source")
        used_sources.update(source_ids)

    republic = entity_by_id[_REPUBLIC_HAITI_ID]
    empire = entity_by_id[_SECOND_EMPIRE_HAITI_ID]
    if (republic["end_year"], empire["start_year"]) != (1849, 1849):
        raise ValueError(f"{_LANE_NAME} exact 1849 boundary drift")
    for text in (republic["continuity_note"], empire["continuity_note"]):
        if "mechanical" not in text or "generic" not in text:
            raise ValueError(f"{_LANE_NAME} 1849 fail-closed note weakened")

    for candidate_id, contract in WAVE8_HAITI_REGIMES_CONTRACTS.items():
        if contract["disposition"] != "promote" or contract["result_type"] != "win":
            raise ValueError(f"{_LANE_NAME} contract disposition drift: {candidate_id}")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} unexpected outcome override: {candidate_id}")
        for side_key in ("side_1_entity_ids", "side_2_entity_ids"):
            side = list(map(str, contract[side_key]))
            if not side or not set(side) <= set(entity_by_id):
                raise ValueError(f"{_LANE_NAME} unknown exact actor: {candidate_id}")
            used_entities.update(side)
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence is not canonical: {candidate_id}")
        if not set(outcomes) <= set(evidence) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} contains an unused entity fixture")
    hold = WAVE8_HAITI_REGIMES_HOLDS[
        "hced-Cabeza de las Marias and las Hicoteas1844-1"
    ]
    if hold["result_type"] != "unknown" or hold["unknown_is_never_draw"] is not True:
        raise ValueError(f"{_LANE_NAME} unknown/draw guard weakened")
    if any(key in hold for key in ("winner_side", "side_1_entity_ids", "side_2_entity_ids")):
        raise ValueError(f"{_LANE_NAME} hold acquired invented sides")
    used_sources.update(map(str, hold["evidence_refs"]))
    if used_sources != set(_SOURCE_BY_ID):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_haiti_regimes_audit_signature() != WAVE8_HAITI_REGIMES_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_haiti_regimes_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _EXACT_LABEL
        or normalize_label(row.get("side_2_raw")) == _EXACT_LABEL
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_HAITI_REGIMES_EXPECTED_CANDIDATE_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_HAITI_REGIMES_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("year_low") != row.get("year_high") or row.get("year_best") != row.get("year_low"):
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if row.get("winner_raw") not in {row.get("side_1_raw"), row.get("side_2_raw")}:
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True:
            raise ValueError(f"{_LANE_NAME} winner/loser completeness changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_HAITI_REGIMES_CONTRACTS,
        WAVE8_HAITI_REGIMES_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_haiti_regimes_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    labels = [row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL]
    if len(labels) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    label = labels[0]
    checks = {
        "event_candidate_id_sha256": str(label.get("event_candidate_id_sha256")),
        "events_touched": int(label.get("events_touched", -1)),
        "label": str(label.get("label")),
        "sole_blocker_events": int(label.get("sole_blocker_events", -1)),
        "zero_time_valid_candidates": int(
            label.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
        ),
    }
    if checks != WAVE8_HAITI_REGIMES_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed: {checks}")
    return {
        "events_touched": checks["events_touched"],
        "sole_blocker_events": checks["sole_blocker_events"],
        "zero_time_valid_candidates": checks["zero_time_valid_candidates"],
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "batyear"):
        value = row.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
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


_RAW_EVENT_NAMES = {
    "hced-Azua1844-1": "Azua",
    "hced-Cabeza de las Marias and las Hicoteas1844-1": (
        "Cabeza de las marias and las hicoteas"
    ),
    "hced-El Numero1849-1": "El Numero",
    "hced-Sabana Larga1856-1": "Sabana Larga",
    "hced-Santo Domingo1805-1": "Santo Domingo",
}


_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(item["canonical_event"]["year_low"]),
        normalize_label(alias),
    )
    for candidate_id, item in {
        **WAVE8_HAITI_REGIMES_CONTRACTS,
        **WAVE8_HAITI_REGIMES_HOLDS,
    }.items()
    for alias in {
        item["canonical_event"]["name"],
        _RAW_EVENT_NAMES[candidate_id],
    }
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any((year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row))


def validate_wave8_haiti_regimes_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_haiti_regimes_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_HAITI_REGIMES_EXPECTED_CANDIDATE_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_HAITI_REGIMES_CONTRACT_IDS
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


def install_wave8_haiti_regimes_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_HAITI_REGIMES_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_haiti_regimes_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_HAITI_REGIMES_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_HAITI_REGIMES_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_HAITI_REGIMES_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_haiti_regimes_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_haiti_regimes_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_HAITI_REGIMES_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_haiti_regimes_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_HAITI_REGIMES_CONTRACTS.values(),
                    *WAVE8_HAITI_REGIMES_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_haiti_regimes_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(WAVE8_HAITI_REGIMES_COUNTRY_QUARANTINE_ADDITIONS),
        "holds": len(WAVE8_HAITI_REGIMES_HOLDS),
        "new_entities": len(WAVE8_HAITI_REGIMES_ENTITIES),
        "new_sources": len(WAVE8_HAITI_REGIMES_SOURCES),
        "newly_rated_events": len(WAVE8_HAITI_REGIMES_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(WAVE8_HAITI_REGIMES_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_HAITI_REGIMES_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_HAITI_REGIMES_EXPECTED_CANDIDATE_IDS),
        "terminal_exclusions": 0,
    }


def wave8_haiti_regimes_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_HAITI_REGIMES_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_HAITI_REGIMES_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_haiti_regimes_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_haiti_regimes_counts(),
        "cohorts": wave8_haiti_regimes_cohort_counts(),
        "final_audit_signature": WAVE8_HAITI_REGIMES_FINAL_AUDIT_SIGNATURE,
        "hold_ids": sorted(WAVE8_HAITI_REGIMES_HOLD_IDS),
        "promoted_candidate_ids": sorted(WAVE8_HAITI_REGIMES_CONTRACT_IDS),
    }
