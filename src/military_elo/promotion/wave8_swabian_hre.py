"""Fail-closed audit of eight Swabian city-league and 1499 war rows.

HCED's labels collapse two different leagues and several event-specific
coalitions into ``Swabian League``, ``Switzerland``, ``German Princes``, and
``Holy Roman Empire``.  This lane opens none of those labels.  Each reviewed
engagement instead receives two alias-free, event-bounded force identities.

All eight source rows encode a complete side-1 tactical victory and the
independent reviewed sources support that polarity.  Six winnerless Wikidata
twins remain discovery-only: their missing winners stay unknown and are never
converted to draws or independently rated events.
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
    "WAVE8_SWABIAN_HRE_CONTRACT_IDS",
    "WAVE8_SWABIAN_HRE_CONTRACTS",
    "WAVE8_SWABIAN_HRE_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SWABIAN_HRE_DISCOVERY_EXPECTED",
    "WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES",
    "WAVE8_SWABIAN_HRE_DISCOVERY_TWINS",
    "WAVE8_SWABIAN_HRE_ENTITIES",
    "WAVE8_SWABIAN_HRE_EXPECTED_CANDIDATE_IDS",
    "WAVE8_SWABIAN_HRE_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SWABIAN_HRE_FUNNEL_AUDIT",
    "WAVE8_SWABIAN_HRE_HOLDS",
    "WAVE8_SWABIAN_HRE_INTEGRATION_DISPOSITIONS",
    "WAVE8_SWABIAN_HRE_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_SWABIAN_HRE_LOCATION_QUARANTINE_REASONS",
    "WAVE8_SWABIAN_HRE_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SWABIAN_HRE_RESERVED_IDS",
    "WAVE8_SWABIAN_HRE_ROW_HASHES",
    "WAVE8_SWABIAN_HRE_SOURCES",
    "install_wave8_swabian_hre_entities",
    "install_wave8_swabian_hre_sources",
    "promote_wave8_swabian_hre_contracts",
    "validate_wave8_swabian_hre_current_artifact_state",
    "validate_wave8_swabian_hre_discovery_dispositions",
    "validate_wave8_swabian_hre_funnel",
    "validate_wave8_swabian_hre_integration_dispositions",
    "validate_wave8_swabian_hre_queue_contracts",
    "wave8_swabian_hre_audit_signature",
    "wave8_swabian_hre_cohort_counts",
    "wave8_swabian_hre_counts",
    "wave8_swabian_hre_metadata",
)


_LANE_NAME = "Wave 8 exact Swabian city-league and 1499 war audit"
_MODULE_OWNER = "military_elo.promotion.wave8_swabian_hre"
_EVENT_ID_PREFIX = "hced_wave8_swabian_hre_"
_EXACT_LABEL = "swabian league"

_CALVEN_THREE_LEAGUES = "three_leagues_confederate_field_host_calven_1499"
_CALVEN_MAXIMILIANIAN = "maximilianian_tyrolean_vinschgau_host_calven_1499"
_DOFFINGEN_WURTTEMBERG = "wurttemberg_princely_coalition_doffingen_1388"
_DOFFINGEN_CITY_LEAGUE = "swabian_city_league_field_host_doffingen_1388"
_FRASTENZ_CONFEDERATE = "confederate_field_host_frastenz_1499"
_FRASTENZ_MAXIMILIANIAN = (
    "maximilianian_tyrolean_vorderoesterreich_host_frastenz_1499"
)
_HARD_CONFEDERATE = "confederate_field_host_hard_1499"
_HARD_HABSBURG_SWABIAN = "habsburg_swabian_field_host_hard_1499"
_REUTLINGEN_CITY = "reutlingen_city_force_1377"
_REUTLINGEN_WURTTEMBERG = "ulrich_wurttemberg_field_force_reutlingen_1377"
_SCHWADERLOH_CONFEDERATE = "confederate_thurgau_field_host_schwaderloh_1499"
_SCHWADERLOH_IMPERIAL = "imperial_swabian_konstanz_host_schwaderloh_1499"
_TRIESEN_CONFEDERATE = "buendner_confederate_field_host_triesen_1499"
_TRIESEN_SWABIAN = "habsburg_allied_swabian_landsknechts_triesen_1499"
_ULM_DEFENDERS = "ulm_city_defenders_1376"
_ULM_IMPERIAL = "charles_iv_imperial_princely_siege_host_ulm_1376"


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
        "accessed": "2026-07-21",
        "source_family_id": source_family_id,
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    }


WAVE8_SWABIAN_HRE_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_swabian_hre_archivalia_ulm_chronology",
        "Zur Datierung der Belagerung Ulms 1376",
        "https://archivalia.hypotheses.org/64555",
        "Archivalia",
        "source_critical_historical_note",
        "archivalia_ulm_1376_chronology",
    ),
    _source(
        "wave8_swabian_hre_erara_chur_calven",
        "Contemporary Chur account of the Swabian War (Calven, p. 238)",
        "https://www.e-rara.ch/download/pdf/27096893.pdf",
        "e-rara / Swiss electronic rare-book library",
        "digitized_contemporary_chronicle",
        "chur_contemporary_swabian_war_account",
    ),
    _source(
        "wave8_swabian_hre_frastanz_niederstaetter",
        "Die Schlacht bei Frastanz",
        (
            "https://frastanz.at/fileadmin/leben_in_frastanz/Geschichte/"
            "Die_Schlacht_bei_Frastanz.pdf"
        ),
        "Marktgemeinde Frastanz",
        "municipal_scholarly_history",
        "niederstaetter_frastanz_study",
    ),
    _source(
        "wave8_swabian_hre_grafenau_doffingen",
        "Geschichte der Gemeinde Grafenau: Schlacht bei Döffingen",
        "https://www.gemeindegrafenau.de/gemeinde-wirtschaft/geschichte",
        "Gemeinde Grafenau",
        "official_municipal_history",
        "grafenau_doffingen_history",
    ),
    _source(
        "wave8_swabian_hre_graubuenden_calven",
        "Chronologie: Schwabenkrieg / Schlacht an der Calven",
        "https://500.gr.ch/chronologie/",
        "Kanton Graubünden, 500 Jahre Freistaat Drei Bünde",
        "official_cantonal_history",
        "graubuenden_three_leagues_chronology",
    ),
    _source(
        "wave8_swabian_hre_hlb_cities_war",
        "Städtekrieg, 1387/1389",
        (
            "https://www.historisches-lexikon-bayerns.de/Lexikon/"
            "St%C3%A4dtekrieg%2C_1387/1389"
        ),
        "Historisches Lexikon Bayerns",
        "scholarly_historical_encyclopedia",
        "hlb_cities_war_1387_1389",
    ),
    _source(
        "wave8_swabian_hre_hlb_swabian_war",
        "Schwabenkrieg/Schweizerkrieg, 1499",
        "https://www.historisches-lexikon-bayerns.de/Lexikon/Artikel_45514",
        "Historisches Lexikon Bayerns",
        "scholarly_historical_encyclopedia",
        "hlb_swabian_war_1499",
    ),
    _source(
        "wave8_swabian_hre_hll_triesen",
        "Schlacht bei Triesen",
        "https://historisches-lexikon.li/Schlacht_bei_Triesen",
        "Historisches Lexikon des Fürstentums Liechtenstein",
        "national_scholarly_encyclopedia",
        "hll_triesen_battle",
    ),
    _source(
        "wave8_swabian_hre_hls_swabian_war",
        "Schwabenkrieg",
        "https://hls-dhs-dss.ch/de/articles/008888/",
        "Historisches Lexikon der Schweiz",
        "national_scholarly_encyclopedia",
        "hls_swabian_war_1499",
    ),
    _source(
        "wave8_swabian_hre_isos_triboltingen",
        "Bundesinventar ISOS: Triboltingen",
        "https://api.isos.bak.admin.ch/ob/3665/doc/ISOS_3665.pdf",
        "Bundesamt für Kultur, Schweizerische Eidgenossenschaft",
        "official_federal_settlement_inventory",
        "swiss_isos_triboltingen",
    ),
    _source(
        "wave8_swabian_hre_joerg_city_league",
        "Der Rheinisch-Schwäbische Städtebund und der I. Städtekrieg",
        (
            "https://kath-akademie-bayern.de/mediathek-eintrag/"
            "der-rheinisch-schwaebische-staedtebund-und-der-i-staedtekrieg-"
            "reichsstaedtische-interessenwahrung-zwischen-koenigtum-und-fuersten/"
        ),
        "Katholische Akademie in Bayern",
        "scholarly_history_lecture",
        "joerg_rhenish_swabian_city_league",
    ),
    _source(
        "wave8_swabian_hre_leo_bw_doffingen",
        "Döffingen - Altgemeinde~Teilort",
        (
            "https://www.leo-bw.de/fr/web/guest/detail-gis/-/Detail/details/"
            "ORT/labw_ortslexikon/288/D%C3%B6ffingen"
        ),
        "LEO-BW / Landesarchiv Baden-Württemberg",
        "official_state_historical_portal",
        "leo_bw_doffingen",
    ),
    _source(
        "wave8_swabian_hre_reutlingen_rgb",
        "Reutlinger Geschichtsblätter, Ausgabe 2020",
        (
            "https://publikationen.uni-tuebingen.de/xmlui/bitstream/handle/"
            "10900/149386/RGB_Ausgabe_2020_Online.pdf?isAllowed=y&sequence=1"
        ),
        "Stadtarchiv Reutlingen / Universität Tübingen repository",
        "scholarly_local_history_journal",
        "reutlinger_geschichtsblaetter_2020",
    ),
    _source(
        "wave8_swabian_hre_staelin_reutlingen",
        "Wirtembergische Geschichte, Band 3: Reutlingen 1377",
        "https://dl.ub.uni-freiburg.de/diglit/staelin1856-3/0341/ocr",
        "Universitätsbibliothek Freiburg digital collections",
        "digitized_historical_monograph",
        "staelin_wirtembergische_geschichte_v3",
    ),
    _source(
        "wave8_swabian_hre_ulm_city_history",
        "Die Geschichte der Stadt Ulm",
        "https://www.ulm.de/tourismus/stadtgeschichte/geschichte-der-stadt",
        "Stadt Ulm",
        "official_municipal_history",
        "ulm_official_city_history",
    ),
    _source(
        "wave8_swabian_hre_wilnet_schwaderloh",
        "Die Schlacht bei Schwaderloh",
        "https://www.wilnet.ch/files/documents/Die_Schlacht_bei_Schwaderloh.pdf",
        "WilNet / Stadtlexikon Wil",
        "scholarly_regional_battle_study",
        "wilnet_schwaderloh_study",
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_SWABIAN_HRE_SOURCES
}


_EVENT_SOURCE_IDS: dict[str, tuple[str, ...]] = {
    "hced-Calven1499-1": (
        "wave8_swabian_hre_erara_chur_calven",
        "wave8_swabian_hre_graubuenden_calven",
        "wave8_swabian_hre_hlb_swabian_war",
    ),
    "hced-Doffingen1388-1": (
        "wave8_swabian_hre_grafenau_doffingen",
        "wave8_swabian_hre_hlb_cities_war",
        "wave8_swabian_hre_leo_bw_doffingen",
    ),
    "hced-Frastenz1499-1": (
        "wave8_swabian_hre_frastanz_niederstaetter",
        "wave8_swabian_hre_hlb_swabian_war",
        "wave8_swabian_hre_hls_swabian_war",
    ),
    "hced-Hard1499-1": (
        "wave8_swabian_hre_hlb_swabian_war",
        "wave8_swabian_hre_hls_swabian_war",
    ),
    "hced-Reutlingen1377-1": (
        "wave8_swabian_hre_hlb_cities_war",
        "wave8_swabian_hre_reutlingen_rgb",
        "wave8_swabian_hre_staelin_reutlingen",
    ),
    "hced-Schwaderloch1499-1": (
        "wave8_swabian_hre_hlb_swabian_war",
        "wave8_swabian_hre_hls_swabian_war",
        "wave8_swabian_hre_isos_triboltingen",
        "wave8_swabian_hre_wilnet_schwaderloh",
    ),
    "hced-Triesen1499-1": (
        "wave8_swabian_hre_hll_triesen",
        "wave8_swabian_hre_hls_swabian_war",
    ),
    "hced-Ulm1376-1": (
        "wave8_swabian_hre_archivalia_ulm_chronology",
        "wave8_swabian_hre_hlb_cities_war",
        "wave8_swabian_hre_joerg_city_league",
        "wave8_swabian_hre_ulm_city_history",
    ),
}


def _entity(
    entity_id: str,
    name: str,
    year: int,
    region: str,
    source_ids: Iterable[str],
    continuity_note: str,
    *,
    kind: str = "event_bounded_field_force",
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
        "continuity_note": continuity_note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_SWABIAN_HRE_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _CALVEN_THREE_LEAGUES,
        "Three Leagues-led field host at Calven (1499)",
        1499,
        "Vinschgau and the Münstertal",
        _EVENT_SOURCE_IDS["hced-Calven1499-1"],
        (
            "Bounded to the Three Leagues-led host, including Confederate "
            "auxiliaries, that fought at Calven. It is not a Swiss "
            "Confederation continuity identity and has no Switzerland alias."
        ),
    ),
    _entity(
        _CALVEN_MAXIMILIANIAN,
        "Maximilianian Tyrolean-Vinschgau host at Calven (1499)",
        1499,
        "Vinschgau and the Münstertal",
        _EVENT_SOURCE_IDS["hced-Calven1499-1"],
        (
            "Bounded to Maximilian I's Tyrolean and Vinschgau royal host at "
            "Calven. It is neither a generic Habsburg nor Swabian League polity."
        ),
    ),
    _entity(
        _DOFFINGEN_WURTTEMBERG,
        "Württemberg-led princely coalition at Döffingen (1388)",
        1388,
        "Württemberg and Swabia",
        _EVENT_SOURCE_IDS["hced-Doffingen1388-1"],
        (
            "Bounded to Eberhard II of Württemberg's princely and noble "
            "coalition at Döffingen; the raw German Princes label never resolves."
        ),
    ),
    _entity(
        _DOFFINGEN_CITY_LEAGUE,
        "Swabian League of Cities field host at Döffingen (1388)",
        1388,
        "Swabia",
        _EVENT_SOURCE_IDS["hced-Doffingen1388-1"],
        (
            "Bounded to the 1376-1389 city league's field army at Döffingen. "
            "It is distinct from the league founded in 1488 and has no bare "
            "Swabian League alias."
        ),
    ),
    _entity(
        _FRASTENZ_CONFEDERATE,
        "Swiss Confederate field host at Frastanz (1499)",
        1499,
        "Vorarlberg",
        _EVENT_SOURCE_IDS["hced-Frastenz1499-1"],
        (
            "Bounded to the Confederate field host at Frastanz; it does not "
            "open a Switzerland or Swiss Confederation continuity identity."
        ),
    ),
    _entity(
        _FRASTENZ_MAXIMILIANIAN,
        "Maximilianian Tyrolean-Vorderösterreich host at Frastanz (1499)",
        1499,
        "Vorarlberg",
        _EVENT_SOURCE_IDS["hced-Frastenz1499-1"],
        (
            "Bounded to the Tyrolean, Vorderösterreich, Vorarlberg, and allied "
            "contingents at Frastanz; no Habsburg, HRE, or league alias is added."
        ),
    ),
    _entity(
        _HARD_CONFEDERATE,
        "Swiss Confederate field host at Hard (1499)",
        1499,
        "Rhine delta near Hard",
        _EVENT_SOURCE_IDS["hced-Hard1499-1"],
        (
            "Bounded to the Confederate field host at Hard; it has no broad "
            "Swiss or Switzerland alias and carries no cross-event continuity."
        ),
    ),
    _entity(
        _HARD_HABSBURG_SWABIAN,
        "Habsburg-allied Swabian field host at Hard (1499)",
        1499,
        "Rhine delta near Hard",
        _EVENT_SOURCE_IDS["hced-Hard1499-1"],
        (
            "Bounded to the Habsburg-allied host containing substantial 1488 "
            "league forces at Hard. It is not a generic Habsburg or league polity."
        ),
    ),
    _entity(
        _REUTLINGEN_CITY,
        "Reutlingen civic force (1377)",
        1377,
        "Reutlingen",
        _EVENT_SOURCE_IDS["hced-Reutlingen1377-1"],
        (
            "Bounded to Reutlingen's civic infantry in the reviewed battle, "
            "not to every member or operation of the Swabian League of Cities."
        ),
    ),
    _entity(
        _REUTLINGEN_WURTTEMBERG,
        "Count Ulrich of Württemberg's field force at Reutlingen (1377)",
        1377,
        "Reutlingen and Württemberg",
        _EVENT_SOURCE_IDS["hced-Reutlingen1377-1"],
        (
            "Bounded to Count Ulrich's mounted and knightly force at Reutlingen. "
            "The raw Holy Roman Empire label is rejected as an actor identity."
        ),
    ),
    _entity(
        _SCHWADERLOH_CONFEDERATE,
        "Confederate-Thurgau field host at Schwaderloh (1499)",
        1499,
        "Thurgau near Triboltingen",
        _EVENT_SOURCE_IDS["hced-Schwaderloch1499-1"],
        (
            "Bounded to the Confederate and Thurgau counterattack force in the "
            "named Schwaderloh action; it has no Switzerland alias."
        ),
    ),
    _entity(
        _SCHWADERLOH_IMPERIAL,
        "Imperial-Swabian Constance raiding host at Schwaderloh (1499)",
        1499,
        "Constance and Thurgau",
        _EVENT_SOURCE_IDS["hced-Schwaderloch1499-1"],
        (
            "Bounded to the imperial and Swabian raiding host from the Constance "
            "area. It is not an HRE-wide or generic Swabian League identity."
        ),
    ),
    _entity(
        _TRIESEN_CONFEDERATE,
        "Bündner-Confederate field host at Triesen (1499)",
        1499,
        "Triesen and the Alpine Rhine valley",
        _EVENT_SOURCE_IDS["hced-Triesen1499-1"],
        (
            "Bounded to the Bündner-Confederate pursuing and relief force at "
            "Triesen; it does not open a Swiss state or population identity."
        ),
    ),
    _entity(
        _TRIESEN_SWABIAN,
        "Habsburg-allied Swabian landsknechts at Triesen (1499)",
        1499,
        "Triesen and the Alpine Rhine valley",
        _EVENT_SOURCE_IDS["hced-Triesen1499-1"],
        (
            "Bounded to the Habsburg-allied landsknechts retreating from St. "
            "Luzisteig; no Habsburg or Swabian League alias is created."
        ),
    ),
    _entity(
        _ULM_DEFENDERS,
        "Ulm civic defenders (1376)",
        1376,
        "Ulm",
        _EVENT_SOURCE_IDS["hced-Ulm1376-1"],
        (
            "Bounded to Ulm and its city-league defenders during Charles IV's "
            "1376 siege; it does not represent the whole city league over time."
        ),
        kind="event_bounded_siege_force",
    ),
    _entity(
        _ULM_IMPERIAL,
        "Charles IV's imperial-princely siege host at Ulm (1376)",
        1376,
        "Ulm",
        _EVENT_SOURCE_IDS["hced-Ulm1376-1"],
        (
            "Bounded to Charles IV's imperial-princely siege host at Ulm. It "
            "does not resolve Holy Roman Empire, HRE, or German Princes labels."
        ),
        kind="event_bounded_siege_force",
    ),
)

_ENTITY_BY_ID = {
    str(entity["id"]): entity for entity in WAVE8_SWABIAN_HRE_ENTITIES
}


WAVE8_SWABIAN_HRE_ROW_HASHES: dict[str, str] = {
    "hced-Calven1499-1": (
        "24873e0203c606b02f0b3e6a014851e48a3e6916c07a3cc8256f7fceb71a0a9d"
    ),
    "hced-Doffingen1388-1": (
        "7705f95a5039588352dd22517239bfb50a82f6bda18019c4aed8b8ff0f2d6801"
    ),
    "hced-Frastenz1499-1": (
        "102eee9198f6f228061989318060d05880ac5260bf3c6f58307c1872876e49c5"
    ),
    "hced-Hard1499-1": (
        "0144c09102942d33fb65533b3c8a2c29986e0dc8a7e92b9b1a8bed449695940c"
    ),
    "hced-Reutlingen1377-1": (
        "72dc18e36339f54002521a36f34fe795395b562285f439ba7a11584cbbc7a127"
    ),
    "hced-Schwaderloch1499-1": (
        "4ad58e960545dd867167658fd9381052306cc5627229531d2ce9d8e1ef063350"
    ),
    "hced-Triesen1499-1": (
        "7a7a4d2fc6e9da5a50aa3e2c4f3b1f44f3f4e12ccef7c6e0f07537f5677f459f"
    ),
    "hced-Ulm1376-1": (
        "db337ec870aaed28d9899c17ef2cc52bc159846e31c1dbe7f3922badfe9455cc"
    ),
}
WAVE8_SWABIAN_HRE_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_SWABIAN_HRE_ROW_HASHES
)


WAVE8_SWABIAN_HRE_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "5bc31f10696ff8762040a3293ff62dfb0fe284db18931ca13bd0250730512afa"
    ),
    "events_touched": 8,
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 8,
    },
    "label": _EXACT_LABEL,
    "rated_counterpart_entities": 0,
    "sole_blocker_events": 0,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 8,
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    start_date: str,
    end_date: str,
    *,
    date_precision: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": date_precision,
        "date_text": date_text,
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


_EXPECTED_SIDES: dict[str, tuple[list[str], list[str]]] = {
    "hced-Calven1499-1": ([_CALVEN_THREE_LEAGUES], [_CALVEN_MAXIMILIANIAN]),
    "hced-Doffingen1388-1": (
        [_DOFFINGEN_WURTTEMBERG],
        [_DOFFINGEN_CITY_LEAGUE],
    ),
    "hced-Frastenz1499-1": (
        [_FRASTENZ_CONFEDERATE],
        [_FRASTENZ_MAXIMILIANIAN],
    ),
    "hced-Hard1499-1": ([_HARD_CONFEDERATE], [_HARD_HABSBURG_SWABIAN]),
    "hced-Reutlingen1377-1": (
        [_REUTLINGEN_CITY],
        [_REUTLINGEN_WURTTEMBERG],
    ),
    "hced-Schwaderloch1499-1": (
        [_SCHWADERLOH_CONFEDERATE],
        [_SCHWADERLOH_IMPERIAL],
    ),
    "hced-Triesen1499-1": ([_TRIESEN_CONFEDERATE], [_TRIESEN_SWABIAN]),
    "hced-Ulm1376-1": ([_ULM_DEFENDERS], [_ULM_IMPERIAL]),
}


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(_EVENT_SOURCE_IDS[candidate_id])
    side_1, side_2 = _EXPECTED_SIDES[candidate_id]
    return {
        "raw_row_sha256": WAVE8_SWABIAN_HRE_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(side_1),
        "side_2_entity_ids": list(side_2),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate_limited",
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
            source_id: [
                "actor_identity_boundary",
                "exact_date_or_date_range",
                "tactical_outcome",
            ]
            for source_id in outcomes
        },
        "date_source_ids": outcomes,
        "source_date_refinement": True,
        "source_date_override": False,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "calendar_style": "unspecified_in_cited_sources",
        "actor_override": "candidate_keyed_event_bounded_opposing_forces",
        "expected_scale_level": 2,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_SWABIAN_HRE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Calven1499-1": _contract(
        "hced-Calven1499-1",
        _canonical(
            "Battle of Calven",
            1499,
            "22 May 1499; calendar style unspecified in the cited sources",
            "1499-05-22",
            "1499-05-22",
            date_precision="source_stated_day_calendar_unspecified",
            granularity="single_battle_in_the_swabian_war",
        ),
        "swabian_war_1499",
        (
            "The official Graubünden chronology and contemporary Chur account "
            "identify the Three Leagues-led victory over Maximilian's Tyrolean-"
            "Vinschgau host. The raw Switzerland label is not inherited."
        ),
        confidence=0.98,
    ),
    "hced-Doffingen1388-1": _contract(
        "hced-Doffingen1388-1",
        _canonical(
            "Battle of Döffingen",
            1388,
            "23 August 1388; calendar style unspecified in the cited sources",
            "1388-08-23",
            "1388-08-23",
            date_precision="source_stated_day_calendar_unspecified",
            granularity="single_battle_in_the_south_german_cities_war",
        ),
        "swabian_city_league_wars_1376_1388",
        (
            "The reviewed state, municipal, and scholarly histories support "
            "Eberhard II's coalition defeating the 1376-1389 city league army. "
            "German Princes is treated only as a noisy raw label."
        ),
        confidence=0.98,
    ),
    "hced-Frastenz1499-1": _contract(
        "hced-Frastenz1499-1",
        _canonical(
            "Battle of Frastanz",
            1499,
            "20 April 1499; calendar style unspecified in the cited sources",
            "1499-04-20",
            "1499-04-20",
            date_precision="source_stated_day_calendar_unspecified",
            granularity="single_battle_in_the_swabian_war",
        ),
        "swabian_war_1499",
        (
            "The municipal study and independent national lexicons support the "
            "Confederate victory over a Tyrolean, Vorderösterreich, Vorarlberg, "
            "and allied composite rather than a timeless Swabian polity."
        ),
        confidence=0.99,
    ),
    "hced-Hard1499-1": _contract(
        "hced-Hard1499-1",
        _canonical(
            "Battle of Hard",
            1499,
            (
                "20-22 February 1499; best date 20 February; calendar style "
                "unspecified in the cited sources"
            ),
            "1499-02-20",
            "1499-02-22",
            date_precision="source_bounded_day_range_calendar_unspecified",
            granularity="single_battle_in_the_swabian_war",
        ),
        "swabian_war_1499",
        (
            "Independent historical lexicons agree on the Confederate victory "
            "over the Habsburg-allied host, while differing between 20 and 22 "
            "February. The contract preserves that source-bounded date range."
        ),
        confidence=0.91,
    ),
    "hced-Reutlingen1377-1": _contract(
        "hced-Reutlingen1377-1",
        _canonical(
            "Battle of Reutlingen",
            1377,
            (
                "14-21 May 1377; best date 14 May; calendar style unspecified "
                "in the cited sources"
            ),
            "1377-05-14",
            "1377-05-21",
            date_precision="source_bounded_day_range_calendar_unspecified",
            granularity="single_battle_in_the_swabian_city_league_conflict",
        ),
        "swabian_city_league_wars_1376_1388",
        (
            "Modern scholarship favors 14 May while an older study gives 21 "
            "May. Both support Reutlingen's civic victory over Count Ulrich's "
            "force, not a victory over the Holy Roman Empire as one actor."
        ),
        confidence=0.92,
    ),
    "hced-Schwaderloch1499-1": _contract(
        "hced-Schwaderloch1499-1",
        _canonical(
            "Battle of Schwaderloh",
            1499,
            "11 April 1499; calendar style unspecified in the cited sources",
            "1499-04-11",
            "1499-04-11",
            date_precision="source_stated_day_calendar_unspecified",
            granularity="single_multiphase_battle_in_the_swabian_war",
        ),
        "swabian_war_1499",
        (
            "The initial setback at Ermatingen and the counterattack above "
            "Triboltingen are retained as one named action. The overall outcome "
            "is a Confederate victory, not a draw."
        ),
        confidence=0.99,
    ),
    "hced-Triesen1499-1": _contract(
        "hced-Triesen1499-1",
        _canonical(
            "Battle of Triesen",
            1499,
            "12 February 1499; calendar style unspecified in the cited sources",
            "1499-02-12",
            "1499-02-12",
            date_precision="source_stated_day_calendar_unspecified",
            granularity="single_battle_in_the_swabian_war",
        ),
        "swabian_war_1499",
        (
            "The Liechtenstein historical lexicon supports the Bündner-"
            "Confederate victory over Habsburg-allied Swabian landsknechts "
            "retreating from St. Luzisteig."
        ),
        confidence=0.98,
    ),
    "hced-Ulm1376-1": _contract(
        "hced-Ulm1376-1",
        _canonical(
            "Siege of Ulm (1376)",
            1376,
            (
                "30 September-9 October 1376; best-supported core ends 6/7 "
                "October; calendar style unspecified in the cited sources"
            ),
            "1376-09-30",
            "1376-10-09",
            date_precision="source_bounded_day_range_calendar_unspecified",
            granularity="single_imperial_siege_and_withdrawal_at_ulm",
        ),
        "swabian_city_league_wars_1376_1388",
        (
            "The city and source-critical histories support Ulm's defenders "
            "surviving Charles IV's siege and forcing withdrawal. This bounded "
            "defender victory is neither an unknown result nor a draw."
        ),
        confidence=0.93,
    ),
}

WAVE8_SWABIAN_HRE_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_SWABIAN_HRE_CONTRACT_IDS = frozenset(WAVE8_SWABIAN_HRE_CONTRACTS)
WAVE8_SWABIAN_HRE_RESERVED_IDS = WAVE8_SWABIAN_HRE_CONTRACT_IDS


WAVE8_SWABIAN_HRE_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_SWABIAN_HRE_CONTRACT_IDS
)
WAVE8_SWABIAN_HRE_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Calven1499-1"}
)
WAVE8_SWABIAN_HRE_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_SWABIAN_HRE_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_SWABIAN_HRE_COUNTRY_QUARANTINE_ADDITIONS,
}

_POINT_REASONS: dict[str, str] = {
    "hced-Calven1499-1": "reviewed_battle_location_mismatch",
    "hced-Doffingen1388-1": "candidate_keyed_point_not_independently_verified",
    "hced-Frastenz1499-1": "candidate_keyed_point_not_independently_verified",
    "hced-Hard1499-1": "candidate_keyed_point_not_independently_verified",
    "hced-Reutlingen1377-1": "reviewed_battle_location_mismatch",
    "hced-Schwaderloch1499-1": "reviewed_battle_location_mismatch",
    "hced-Triesen1499-1": "uncertain_battle_site_and_coordinate_mismatch",
    "hced-Ulm1376-1": "candidate_keyed_point_not_independently_verified",
}
WAVE8_SWABIAN_HRE_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": (
            ["withhold_country", "withhold_point"]
            if candidate_id in WAVE8_SWABIAN_HRE_COUNTRY_QUARANTINE_ADDITIONS
            else ["withhold_point"]
        ),
        "point_reason_code": _POINT_REASONS[candidate_id],
        "country_reason_code": (
            "reviewed_modern_jurisdiction_mismatch"
            if candidate_id in WAVE8_SWABIAN_HRE_COUNTRY_QUARANTINE_ADDITIONS
            else None
        ),
        "evidence_refs": sorted(_EVENT_SOURCE_IDS[candidate_id]),
    }
    for candidate_id in sorted(WAVE8_SWABIAN_HRE_CONTRACT_IDS)
}


WAVE8_SWABIAN_HRE_DISCOVERY_TWINS: dict[str, str] = {
    "hced-Calven1499-1": "Q462099",
    "hced-Doffingen1388-1": "Q873286",
    "hced-Frastenz1499-1": "Q477778",
    "hced-Hard1499-1": "Q1398703",
    "hced-Reutlingen1377-1": "Q136753967",
    "hced-Schwaderloch1499-1": "Q319467",
}
WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q136753967": (
        "2eb9bac5113cf1449b8596b4a19f234ae94839181b4110282c23dc76c5340e0f"
    ),
    "Q1398703": (
        "a4dba9e0486c514437e658dd2218465069092dd117b6a31398fca61a6bf08a55"
    ),
    "Q319467": (
        "39d2b0ccdf7f8217553ab1dafdfa780d8e90b469b2f51d7d056fe2dd8c95cce7"
    ),
    "Q462099": (
        "8fb34162342eb9b06ecaa9580d733b466ba9ebec7e4c781c9820fd1c0d590f28"
    ),
    "Q477778": (
        "be417acab0266d10dff4883228b0ed1b0d0cd556949bbf349ecf6f3b0f005bbf"
    ),
    "Q873286": (
        "1da9222368aac0e65e9e35befc3534ffeff8c2fb0971a6be52add45d0589f717"
    ),
}
WAVE8_SWABIAN_HRE_DISCOVERY_EXPECTED: dict[str, dict[str, Any]] = {
    "Q136753967": {
        "date": "1377-05-22T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Reutlingen",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
    },
    "Q1398703": {
        "date": "1499-02-20T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Hard",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
    },
    "Q319467": {
        "date": "1499-04-20T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Schwaderloh",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
    },
    "Q462099": {
        "date": "1499-05-31T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Calven",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
    },
    "Q477778": {
        "date": "1499-04-20T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Frastanz",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
    },
    "Q873286": {
        "date": "1388-08-31T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Döffingen",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
    },
}
WAVE8_SWABIAN_HRE_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    discovery_id: {
        "source_dataset": "wikidata-battles",
        "disposition": "discovery_only_duplicate",
        "hced_candidate_id": hced_id,
        "outcome_disposition": "unknown_never_draw",
    }
    for hced_id, discovery_id in sorted(WAVE8_SWABIAN_HRE_DISCOVERY_TWINS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_SWABIAN_HRE_CONTRACTS,
        "discovery_expected": WAVE8_SWABIAN_HRE_DISCOVERY_EXPECTED,
        "discovery_row_hashes": WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES,
        "discovery_twins": WAVE8_SWABIAN_HRE_DISCOVERY_TWINS,
        "entities": WAVE8_SWABIAN_HRE_ENTITIES,
        "funnel": WAVE8_SWABIAN_HRE_FUNNEL_AUDIT,
        "holds": WAVE8_SWABIAN_HRE_HOLDS,
        "integration_dispositions": WAVE8_SWABIAN_HRE_INTEGRATION_DISPOSITIONS,
        "location_reasons": WAVE8_SWABIAN_HRE_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_SWABIAN_HRE_ROW_HASHES,
        "sources": WAVE8_SWABIAN_HRE_SOURCES,
    }


def wave8_swabian_hre_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_SWABIAN_HRE_FINAL_AUDIT_SIGNATURE = (
    "1d1385b8e83910915fbd4f3e7b736c6fd3efa04b30525658007bea3333b3ea8d"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = set(_ENTITY_BY_ID)
    if len(source_ids) != len(WAVE8_SWABIAN_HRE_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if len(entity_ids) != len(WAVE8_SWABIAN_HRE_ENTITIES):
        raise ValueError(f"{_LANE_NAME} duplicate entity id")
    if (
        WAVE8_SWABIAN_HRE_CONTRACT_IDS
        != WAVE8_SWABIAN_HRE_EXPECTED_CANDIDATE_IDS
        or WAVE8_SWABIAN_HRE_RESERVED_IDS
        != WAVE8_SWABIAN_HRE_CONTRACT_IDS
        or WAVE8_SWABIAN_HRE_HOLDS
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if len(WAVE8_SWABIAN_HRE_ENTITIES) != 16:
        raise ValueError(f"{_LANE_NAME} bounded entity inventory drift")

    expected_urls = {
        str(source["id"]): str(source["url"])
        for source in WAVE8_SWABIAN_HRE_SOURCES
    }
    if len(expected_urls) != 16:
        raise ValueError(f"{_LANE_NAME} source inventory drift")
    for source_id, source in _SOURCE_BY_ID.items():
        if source["url"] != expected_urls[source_id]:
            raise ValueError(f"{_LANE_NAME} canonical source URL drift: {source_id}")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source role order drift: {source_id}")
        if "outcome" not in source["evidence_roles"]:
            raise ValueError(f"{_LANE_NAME} non-outcome source used for result")

    forbidden_aliases = {
        "german princes",
        "habsburg",
        "holy roman empire",
        "hre",
        "swabian league",
        "switzerland",
        "swiss confederation",
    }
    for entity_id, entity in _ENTITY_BY_ID.items():
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} entity acquired alias/continuity: {entity_id}")
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} entity window widened: {entity_id}")
        if not set(entity["source_ids"]) <= source_ids:
            raise ValueError(f"{_LANE_NAME} entity source closure drift: {entity_id}")
        if {
            normalize_label(alias) for alias in entity["aliases"]
        } & forbidden_aliases:
            raise ValueError(f"{_LANE_NAME} broad alias introduced: {entity_id}")

    used_sources: set[str] = set()
    used_entities: set[str] = set()
    for candidate_id, contract in WAVE8_SWABIAN_HRE_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or contract["source_date_override"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome disposition drift: {candidate_id}")
        sides = (
            list(map(str, contract["side_1_entity_ids"])),
            list(map(str, contract["side_2_entity_ids"])),
        )
        if sides != _EXPECTED_SIDES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} exact actor drift: {candidate_id}")
        if any(entity_id not in entity_ids for side in sides for entity_id in side):
            raise ValueError(f"{_LANE_NAME} unbounded actor used: {candidate_id}")
        used_entities.update((*sides[0], *sides[1]))

        canonical = contract["canonical_event"]
        year = int(canonical["year_low"])
        if (
            int(canonical["year_high"]) != year
            or canonical["canonical_key"]
            != f"{_slug(str(canonical['name']))}:{year}:{year}"
            or not str(canonical["date_text"])
            or not str(canonical["start_date"])
            or not str(canonical["end_date"])
            or "calendar_unspecified" not in str(canonical["date_precision"])
            or int(contract["expected_scale_level"]) != 2
            or contract["calendar_style"] != "unspecified_in_cited_sources"
        ):
            raise ValueError(f"{_LANE_NAME} date/granularity drift: {candidate_id}")

        outcomes = list(map(str, contract["outcome_source_ids"]))
        evidence = list(map(str, contract["evidence_refs"]))
        dates = list(map(str, contract["date_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        expected_sources = sorted(_EVENT_SOURCE_IDS[candidate_id])
        expected_families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in expected_sources
            }
        )
        if (
            outcomes != expected_sources
            or evidence != outcomes
            or dates != outcomes
            or families != expected_families
            or len(families) < 2
            or contract["source_date_refinement"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} source closure drift: {candidate_id}")
        role_map = contract["event_evidence_roles"]
        if set(role_map) != set(outcomes):
            raise ValueError(f"{_LANE_NAME} event source-role closure drift")
        for roles in role_map.values():
            if not _is_sorted_unique(roles) or not roles:
                raise ValueError(f"{_LANE_NAME} event-specific source roles drift")
        used_sources.update(outcomes)

    if used_entities != entity_ids:
        raise ValueError(f"{_LANE_NAME} bounded entities are not exactly consumed")
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if WAVE8_SWABIAN_HRE_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_SWABIAN_HRE_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine drift")
    if WAVE8_SWABIAN_HRE_COUNTRY_QUARANTINE_ADDITIONS != {
        "hced-Calven1499-1"
    }:
        raise ValueError(f"{_LANE_NAME} country quarantine drift")
    if set(WAVE8_SWABIAN_HRE_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_SWABIAN_HRE_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location review inventory drift")
    if set(WAVE8_SWABIAN_HRE_DISCOVERY_TWINS.values()) != set(
        WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES
    ) or set(WAVE8_SWABIAN_HRE_DISCOVERY_EXPECTED) != set(
        WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} discovery inventory drift")
    if any(
        item["outcome_disposition"] != "unknown_never_draw"
        for item in WAVE8_SWABIAN_HRE_DISCOVERY_EXPECTED.values()
    ):
        raise ValueError(f"{_LANE_NAME} unknown-is-never-draw guard drift")
    if set(WAVE8_SWABIAN_HRE_INTEGRATION_DISPOSITIONS) != set(
        WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} integration disposition drift")
    if (
        wave8_swabian_hre_audit_signature()
        != WAVE8_SWABIAN_HRE_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


_EXPECTED_RAW_SIDES: dict[str, tuple[str, str, str, str, int]] = {
    "hced-Calven1499-1": (
        "Switzerland",
        "Swabian League",
        "Switzerland",
        "Swabian League",
        1499,
    ),
    "hced-Doffingen1388-1": (
        "German Princes",
        "Swabian League",
        "German Princes",
        "Swabian League",
        1388,
    ),
    "hced-Frastenz1499-1": (
        "Switzerland",
        "Swabian League",
        "Switzerland",
        "Swabian League",
        1499,
    ),
    "hced-Hard1499-1": (
        "Switzerland",
        "Swabian League",
        "Switzerland",
        "Swabian League",
        1499,
    ),
    "hced-Reutlingen1377-1": (
        "Swabian League",
        "Holy Roman Empire",
        "Swabian League",
        "Holy Roman Empire",
        1377,
    ),
    "hced-Schwaderloch1499-1": (
        "Switzerland",
        "Swabian League",
        "Switzerland",
        "Swabian League",
        1499,
    ),
    "hced-Triesen1499-1": (
        "Switzerland",
        "Swabian League",
        "Switzerland",
        "Swabian League",
        1499,
    ),
    "hced-Ulm1376-1": (
        "Swabian League",
        "Holy Roman Empire",
        "Swabian League",
        "Holy Roman Empire",
        1376,
    ),
}


def validate_wave8_swabian_hre_queue_contracts(
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
    if exact_ids != WAVE8_SWABIAN_HRE_RESERVED_IDS or len(exact) != len(
        exact_ids
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_SWABIAN_HRE_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        side_1, side_2, winner, loser, year = _EXPECTED_RAW_SIDES[candidate_id]
        if (
            row.get("side_1_raw") != side_1
            or row.get("side_2_raw") != side_2
            or row.get("winner_raw") != winner
            or row.get("loser_raw") != loser
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("do_not_rate_automatically") is not True
            or row.get("duplicate_source_id") is not False
            or (row.get("year_low"), row.get("year_best"), row.get("year_high"))
            != (year, year, year)
        ):
            raise ValueError(f"{_LANE_NAME} locked source row drift: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SWABIAN_HRE_CONTRACTS,
        WAVE8_SWABIAN_HRE_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_swabian_hre_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    rows = [
        row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL
    ]
    if len(rows) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    row = rows[0]
    actual = {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "failure_cases": {
            key: int(row.get("failure_cases", {}).get(key, -1))
            for key in WAVE8_SWABIAN_HRE_FUNNEL_AUDIT["failure_cases"]
        },
        "label": str(row.get("label")),
        "rated_counterpart_entities": int(row.get("rated_counterpart_entities", -1)),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, row.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
    }
    if actual != WAVE8_SWABIAN_HRE_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pin changed: {actual}")
    return {
        "events_touched": actual["events_touched"],
        "sole_blocker_events": actual["sole_blocker_events"],
        "unresolved_side_attempts": actual["unresolved_side_attempts"],
        "zero_time_valid_candidates": actual["failure_cases"][
            "zero_time_valid_candidates"
        ],
    }


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def validate_wave8_swabian_hre_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in (
        WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} discovery row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}")
        expected = WAVE8_SWABIAN_HRE_DISCOVERY_EXPECTED[candidate_id]
        participant_labels = sorted(
            str(participant.get("label"))
            for participant in row.get("participants", [])
        )
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("name") != expected["name"]
            or row.get("date") != expected["date"]
            or row.get("end_date") != expected["end_date"]
            or row.get("kind") != expected["kind"]
            or participant_labels != expected["participant_labels"]
            or row.get("winners") != []
        ):
            raise ValueError(
                f"{_LANE_NAME} discovery non-rating guard changed: {candidate_id}"
            )
    return {
        "discovery_nonrating_twins": len(
            WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES
        ),
        "discovery_promotions": 0,
        "unknown_never_draw_rows": len(
            WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES
        ),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "start_year", "year_start"):
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
        row.get("war_name"),
    ]
    aliases = row.get("aliases", []) or []
    values.extend([aliases] if isinstance(aliases, str) else aliases)
    return {normalize_label(value) for value in values if normalize_label(value)}


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Calven1499-1": {"Battle of Calven", "Calven"},
    "hced-Doffingen1388-1": {"Battle of Döffingen", "Doffingen", "Döffingen"},
    "hced-Frastenz1499-1": {"Battle of Frastanz", "Frastanz", "Frastenz"},
    "hced-Hard1499-1": {"Battle of Hard", "Hard"},
    "hced-Reutlingen1377-1": {"Battle of Reutlingen", "Reutlingen"},
    "hced-Schwaderloch1499-1": {
        "Battle of Schwaderloh",
        "Schwaderloch",
        "Schwaderloh",
    },
    "hced-Triesen1499-1": {"Battle of Triesen", "Triesen"},
    "hced-Ulm1376-1": {"Siege of Ulm", "Siege of Ulm (1376)", "Ulm"},
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(WAVE8_SWABIAN_HRE_CONTRACTS[candidate_id]["canonical_event"]["year_low"]),
        normalize_label(alias),
    )
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
)
_EVENT_NAMES = frozenset(
    normalize_label(alias) for aliases in _EVENT_ALIASES.values() for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    matched_names = _row_names(row) & _EVENT_NAMES
    if not matched_names:
        return False
    year = _row_year(row)
    if year is None:
        return True
    return any((year, name) in _DUPLICATE_MATCH_KEYS for name in matched_names)


def validate_wave8_swabian_hre_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwd_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Prove that no unreviewed HCED/IWD/IWBD/release twin can double-rate."""

    validate_wave8_swabian_hre_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_SWABIAN_HRE_RESERVED_IDS
        and _is_probable_twin(row)
    )
    iwd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwd_rows
        if _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    existing = list(existing_events)
    owned = [
        event
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_SWABIAN_HRE_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    if owned:
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        if owned_ids != WAVE8_SWABIAN_HRE_CONTRACT_IDS or len(owned) != len(
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
            WAVE8_SWABIAN_HRE_INTEGRATION_DISPOSITIONS
        ),
        "existing_release_owned_events": len(owned),
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwd_probable_twins": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_swabian_hre_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SWABIAN_HRE_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_swabian_hre_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SWABIAN_HRE_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SWABIAN_HRE_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SWABIAN_HRE_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_swabian_hre_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_swabian_hre_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SWABIAN_HRE_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def validate_wave8_swabian_hre_current_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Require the lane's events, entities, and sources to be absent or complete."""

    _validate_static()
    events = list(release_events)
    owned = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_SWABIAN_HRE_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    entity_by_id = {
        str(entity.get("id")): entity
        for entity in release_entities
        if str(entity.get("id")) in _ENTITY_BY_ID
    }
    source_by_id = {
        str(source.get("id")): source
        for source in release_sources
        if str(source.get("id")) in _SOURCE_BY_ID
    }
    complete_counts = (
        len(WAVE8_SWABIAN_HRE_CONTRACT_IDS),
        len(WAVE8_SWABIAN_HRE_ENTITIES),
        len(WAVE8_SWABIAN_HRE_SOURCES),
    )
    actual_counts = (len(owned), len(entity_by_id), len(source_by_id))
    if actual_counts not in {(0, 0, 0), complete_counts}:
        raise ValueError(
            f"{_LANE_NAME} current release artifacts are partial: {actual_counts}"
        )
    if actual_counts == (0, 0, 0):
        return {
            "artifact_state": "absent",
            "installed_entities": 0,
            "installed_sources": 0,
            "promoted_events": 0,
        }
    if entity_by_id != _ENTITY_BY_ID or source_by_id != _SOURCE_BY_ID:
        raise ValueError(f"{_LANE_NAME} current entity/source artifact drift")

    by_candidate = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_candidate) != WAVE8_SWABIAN_HRE_CONTRACT_IDS or len(owned) != len(
        by_candidate
    ):
        raise ValueError(f"{_LANE_NAME} current event candidate inventory drift")
    retained_countries = {
        "hced-Doffingen1388-1": "Germany",
        "hced-Frastenz1499-1": "Austria",
        "hced-Hard1499-1": "Austria",
        "hced-Reutlingen1377-1": "Germany",
        "hced-Schwaderloch1499-1": "Switzerland",
        "hced-Triesen1499-1": "Liechtenstein",
        "hced-Ulm1376-1": "Germany",
    }
    for candidate_id, contract in WAVE8_SWABIAN_HRE_CONTRACTS.items():
        event = by_candidate[candidate_id]
        canonical = contract["canonical_event"]
        expected_id = f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        side_1, side_2 = _EXPECTED_SIDES[candidate_id]
        if (
            event.get("id") != expected_id
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year"))
            != (canonical["year_low"], canonical["year_high"])
            or event.get("event_type") != "engagement"
            or event.get("date_precision") != canonical["date_precision"]
            or event.get("reviewed_granularity") != canonical["granularity"]
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids")
            != contract["outcome_source_family_ids"]
            or float(event.get("confidence", -1.0))
            != float(contract["confidence"])
        ):
            raise ValueError(f"{_LANE_NAME} current event drift: {candidate_id}")
        expected_participants = expected_exact_hced_win_participants(
            side_1,
            side_2,
            confidence=float(contract["confidence"]),
            scale_level=int(contract["expected_scale_level"]),
            lane_name=_LANE_NAME,
        )
        if event.get("participants") != expected_participants:
            raise ValueError(f"{_LANE_NAME} participant drift: {candidate_id}")
        if "geometry" in event:
            raise ValueError(f"{_LANE_NAME} quarantined point leaked: {candidate_id}")
        if candidate_id == "hced-Calven1499-1":
            if "modern_location_country" in event or "location_provenance" in event:
                raise ValueError(f"{_LANE_NAME} Calven location quarantine drift")
        elif (
            event.get("modern_location_country") != retained_countries[candidate_id]
            or "location_provenance" not in event
        ):
            raise ValueError(f"{_LANE_NAME} retained country drift: {candidate_id}")
    return {
        "artifact_state": "integrated",
        "installed_entities": len(entity_by_id),
        "installed_sources": len(source_by_id),
        "promoted_events": len(owned),
    }


def wave8_swabian_hre_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_SWABIAN_HRE_CONTRACTS.values(),
                    *WAVE8_SWABIAN_HRE_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_swabian_hre_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_SWABIAN_HRE_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_nonrating_records": len(
            WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES
        ),
        "holds": 0,
        "integration_dispositions": len(
            WAVE8_SWABIAN_HRE_INTEGRATION_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_SWABIAN_HRE_ENTITIES),
        "new_sources": len(WAVE8_SWABIAN_HRE_SOURCES),
        "newly_rated_events": len(WAVE8_SWABIAN_HRE_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_SWABIAN_HRE_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_SWABIAN_HRE_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_SWABIAN_HRE_RESERVED_IDS),
        "terminal_exclusions": 0,
        "unknown_discovery_outcomes": len(
            WAVE8_SWABIAN_HRE_DISCOVERY_ROW_HASHES
        ),
    }


def wave8_swabian_hre_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_swabian_hre_counts(),
        "cohorts": wave8_swabian_hre_cohort_counts(),
        "discovery_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_SWABIAN_HRE_INTEGRATION_DISPOSITIONS.items()
            )
        ],
        "final_audit_signature": WAVE8_SWABIAN_HRE_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_SWABIAN_HRE_CONTRACT_IDS),
    }


_validate_static()
