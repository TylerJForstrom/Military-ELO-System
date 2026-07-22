"""Fail-closed exact audit of eight HCED Finnish Civil War rows.

Four independently documented battles rate: Oulu, Rautu, Tampere, and
Viipuri.  Their participants are alias-free 1918 military identities; none
inherits the Elo of the Republic of Finland, the Russian SFSR, or the USSR.
The other four source rows collapse multilateral or multi-engagement
sequences.  They remain explicit unknown holds and are never draws.

Seven matching Wikidata records are discovery-only.  Their empty winner
fields cannot originate a rating or override the reviewed HCED contracts.
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
    "WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS",
    "WAVE8_FINNISH_CIVIL_WAR_CONTRACTS",
    "WAVE8_FINNISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_EXPECTED",
    "WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_MATCHES",
    "WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_ROW_HASHES",
    "WAVE8_FINNISH_CIVIL_WAR_ENTITIES",
    "WAVE8_FINNISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE",
    "WAVE8_FINNISH_CIVIL_WAR_FUNNEL_AUDIT",
    "WAVE8_FINNISH_CIVIL_WAR_HOLD_IDS",
    "WAVE8_FINNISH_CIVIL_WAR_HOLDS",
    "WAVE8_FINNISH_CIVIL_WAR_INTEGRATION_DISPOSITIONS",
    "WAVE8_FINNISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS",
    "WAVE8_FINNISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_FINNISH_CIVIL_WAR_RESERVED_IDS",
    "WAVE8_FINNISH_CIVIL_WAR_ROW_HASHES",
    "WAVE8_FINNISH_CIVIL_WAR_SOURCES",
    "install_wave8_finnish_civil_war_entities",
    "install_wave8_finnish_civil_war_sources",
    "promote_wave8_finnish_civil_war_contracts",
    "validate_wave8_finnish_civil_war_discovery_dispositions",
    "validate_wave8_finnish_civil_war_emissions",
    "validate_wave8_finnish_civil_war_funnel",
    "validate_wave8_finnish_civil_war_integration_dispositions",
    "validate_wave8_finnish_civil_war_queue_contracts",
    "wave8_finnish_civil_war_audit_signature",
    "wave8_finnish_civil_war_cohort_counts",
    "wave8_finnish_civil_war_counts",
    "wave8_finnish_civil_war_metadata",
)


_LANE_NAME = "Wave 8 exact Finnish Civil War audit"
_MODULE_OWNER = "military_elo.promotion.wave8_finnish_civil_war"
_EVENT_ID_PREFIX = "hced_wave8_finnish_civil_war_"
_COHORT = "finnish_civil_war_exact_1918"

_WHITE = "finnish_white_army_1918"
_RED = "finnish_red_guard_1918"
_OULU_GARRISON = "oulu_russian_garrison_1918"
_RAUTU_DETACHMENTS = "petrograd_red_detachments_rautu_1918"

_LANE_SIDE_LABELS = frozenset(
    {
        "bolsheviks",
        "finland",
        "finnish reds",
        "finnish whites",
        "russian bolsheviks",
        "ussr",
    }
)
_LANE_WAR_NAMES = frozenset({"Finnish War", "Finnish War of Independence"})


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    evidence_roles: Iterable[str],
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
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_FINNISH_CIVIL_WAR_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_finnish_1914_1918_overview",
        "Finnish Civil War 1918",
        "https://encyclopedia.1914-1918-online.net/article/finnish-civil-war-1918/",
        "1914-1918 Online: International Encyclopedia of the First World War",
        "peer_reviewed_scholarly_encyclopedia",
        "1914_1918_online_finnish_civil_war",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_finnish_1914_1918_tampere",
        "Tampere, Battle of",
        "https://encyclopedia.1914-1918-online.net/article/tampere-battle-of/",
        "1914-1918 Online: International Encyclopedia of the First World War",
        "peer_reviewed_scholarly_encyclopedia",
        "1914_1918_online_tampere",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_finnish_city_oulu_history",
        "Oulussa taisteltiin sisällissodan aikana, mutta terroria oli vähän",
        (
            "https://www.munoulu.fi/kulttuuri/oulussa-taisteltiin-"
            "sis%C3%A4llissodan-aikana-mutta-terroria-oli-v%C3%A4h%C3%A4n/"
        ),
        "City of Oulu",
        "official_municipal_history",
        "city_of_oulu_civil_war_history",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_finnish_enqvist_coastal_defence",
        (
            "Kellä saaret ja selät on hallussaan: Rannikkopuolustuksen "
            "aluekysymykset autonomisessa ja itsenäisessä Suomessa"
        ),
        "https://www.doria.fi/bitstream/10024/74458/1/864586_taitto_web_2.pdf",
        "Finnish National Defence University, Department of Military History",
        "scholarly_military_history_monograph",
        "enqvist_finnish_coastal_defence_2007",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_finnish_hovilainen_rautu_dates",
        "Raudun taistelu 21.2.1918-5.4.1918",
        "https://jyu.finna.fi/Record/arto.014087642",
        "Kansalliskirjasto Arto via JYKDOK",
        "scholarly_article_catalog_record",
        "hovilainen_rautu_2014",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_finnish_kemppi_oulu_record",
        "Scholarly article record for the Battle of Oulu",
        "https://www.finna.fi/Record/arto.013266593",
        "Finna / Kansalliskirjasto Arto",
        "scholarly_article_catalog_record",
        "kemppi_battle_of_oulu",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_finnish_kirkkonummi_1918",
        "1918 Kirkkonummella",
        (
            "https://kirkkonummi.fi/matkailu/kulttuuri-ja-museo/"
            "paikallishistoriaa-kulttuuri/1918-kirkkonummella/"
        ),
        "Municipality of Kirkkonummi",
        "official_municipal_history",
        "kirkkonummi_1918_local_history",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_finnish_lahteenmaki_rautu",
        "Maailmojen rajalla: Kannaksen rajamaa ja poliittiset murtumat 1911-1944",
        "https://www.doria.fi/bitstream/10024/182959/1/HT243_opt.pdf",
        "Suomalaisen Kirjallisuuden Seura",
        "peer_reviewed_history_monograph",
        "lahteenmaki_maailmojen_rajalla_2009",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_finnish_manninen_rautu",
        "Raudun taistelut 1918 Pietarista katsottuna",
        "https://jyu.finna.fi/Record/arto.013357343",
        "Kansalliskirjasto Arto via JYKDOK",
        "scholarly_military_history_article_record",
        "manninen_rautu_sotilasaikakauslehti_2015",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_finnish_mantta_vilppula_history",
        "Kansallinen perinne, osa 2: vuoden 1918 tapahtumat Vilppulassa",
        (
            "https://manttavilppula.fi/wp-content/uploads/2024/03/"
            "kansallinenperinne_osa2.pdf"
        ),
        "City of Mänttä-Vilppula",
        "official_municipal_history",
        "mantta_vilppula_civil_war_history",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_finnish_ruovesi_doctoral_record",
        "Sisällissodan arvet maalaispitäjässä: Ruovesi vuosina 1918-1930",
        (
            "https://researchportal.tuni.fi/en/publications/"
            "sis%C3%A4llissodan-arvet-maalaispit%C3%A4j%C3%A4ss%C3%A4-ruovesi-"
            "vuosina-1918-1930/"
        ),
        "Tampere University Research Portal",
        "doctoral_research_record",
        "tampere_university_ruovesi_doctoral_research",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_finnish_ruovesi_thesis",
        "Ruovesi vuoden 1918 sisällissodassa",
        (
            "https://trepo.tuni.fi/bitstream/handle/10024/84117/"
            "gradu06332.pdf?isAllowed=y&sequence=1"
        ),
        "Tampere University Trepo",
        "archive_based_history_thesis",
        "tampere_university_ruovesi_thesis",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_finnish_sjoblom_aland",
        "Military decision-making and the Åland question in 1918",
        (
            "https://www.doria.fi/bitstream/handle/10024/155725/"
            "Max%20Sj%C3%B6blom_v%C3%A4it%C3%B6skirja__verkko.pdf?"
            "isAllowed=y&sequence=1"
        ),
        "Finnish National Defence University / Doria",
        "doctoral_dissertation",
        "sjoblom_aland_dissertation",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_finnish_sks_viipuri",
        "The Battle of Viipuri and its aftermath in April 1918",
        "https://journal.fi/vskst/article/view/128044/77218",
        "Suomalaisen Kirjallisuuden Seura / Journal.fi",
        "peer_reviewed_history_chapter",
        "sks_viipuri_1918_chapter",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_finnish_swedish_archives_aland",
        "Ålands nationstillhörighet",
        (
            "https://sok.riksarkivet.se/historier/finska-kriget/"
            "alands-nationstillhorighet/"
        ),
        "Swedish National Archives",
        "official_archival_history",
        "swedish_national_archives_aland_1918",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_finnish_uppslagsverket_aland",
        "Ålandsexpeditionen",
        "https://www.uppslagsverket.fi/sv/view-170045-Aalandsexpeditionen",
        "Uppslagsverket Finland",
        "scholarly_national_encyclopedia",
        "uppslagsverket_finland_aland_expedition",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_finnish_vapriikki_connections",
        "The Finnish Civil War and its international connections",
        (
            "https://tampere1918.fi/en/"
            "the-finnish-civil-war-and-its-international-connections/"
        ),
        "Museum Centre Vapriikki / Tampere 1918",
        "official_museum_history",
        "vapriikki_tampere_1918_history",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_finnish_yle_oulu",
        "Oulun taistelun historical review with University of Oulu historian Olavi Fält",
        "https://yle.fi/a/3-10048411",
        "Yle",
        "public_broadcaster_historical_report",
        "yle_oulu_battle_2018",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_finnish_yle_sigurds",
        "Sigurdsin kaartin vaiheet helmikuussa 1918",
        "https://yle.fi/aihe/a/20-207977",
        "Yle",
        "public_broadcaster_archival_history",
        "yle_sigurds_archival_history",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_FINNISH_CIVIL_WAR_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    region: str,
    note: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 1918,
        "end_year": 1918,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_FINNISH_CIVIL_WAR_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _WHITE,
        "Finnish White Army (1918)",
        "civil_war_faction_army",
        "Finland and the 1918 Karelian fronts",
        (
            "Alias-free military identity bounded to the White Army during the "
            "1918 Finnish Civil War. It is not the Republic of Finland and does "
            "not inherit or transfer that state's rating; bare Finland, White, "
            "Finnish Whites, predecessor, and successor labels resolve nowhere."
        ),
        {
            "wave8_finnish_1914_1918_overview",
            "wave8_finnish_vapriikki_connections",
        },
    ),
    _entity(
        _RED,
        "Finnish Red Guard (1918)",
        "civil_war_faction_army",
        "Red Finland and its 1918 fronts",
        (
            "Alias-free military identity bounded to the Finnish Red Guard in "
            "1918. It is distinct from Russian revolutionary forces and does not "
            "inherit or transfer any Finnish-state, Russian-SFSR, Soviet, labor-"
            "movement, predecessor, or successor rating."
        ),
        {
            "wave8_finnish_1914_1918_overview",
            "wave8_finnish_vapriikki_connections",
        },
    ),
    _entity(
        _OULU_GARRISON,
        "Oulu Russian garrison (1918)",
        "event_bounded_garrison",
        "Oulu, Finland",
        (
            "Alias-free identity for the local Russian garrison that supported "
            "the Red side during the 2-3 February Battle of Oulu. It is not the "
            "Russian SFSR, the USSR, or a generic Bolshevik polity and inherits "
            "or transfers no rating beyond this reviewed event."
        ),
        {
            "wave8_finnish_city_oulu_history",
            "wave8_finnish_yle_oulu",
        },
    ),
    _entity(
        _RAUTU_DETACHMENTS,
        "Petrograd Red Army and volunteer detachments at Rautu (1918)",
        "event_bounded_joint_detachment",
        "Rautu and the Karelian Isthmus",
        (
            "Alias-free identity for the Petrograd volunteers and Red Army "
            "detachments documented at Rautu in 1918. It is not a continuity "
            "bridge to the Russian SFSR or USSR and inherits or transfers no "
            "rating outside the fingerprinted Rautu contract."
        ),
        {
            "wave8_finnish_lahteenmaki_rautu",
            "wave8_finnish_manninen_rautu",
        },
    ),
)


WAVE8_FINNISH_CIVIL_WAR_ROW_HASHES: dict[str, str] = {
    "hced-Aland1918-1": (
        "038ee0befb47d722d931f2a84c3492811cdeb8223d783298b7b24fe1ac5b5f52"
    ),
    "hced-Oulo1918-1": (
        "f5c755515b1f381fac6a4eff4dfd4892bd92096e16a6728becd154da2af47a63"
    ),
    "hced-Rautu1918-1": (
        "ab2a0a02f6a2c2cbf7afcb2c9237a539d637aeefcba08fb8bebf159164d979d5"
    ),
    "hced-Ruovesi1918-1": (
        "9771543cc768a823bbdd58147c3df523d8a84a45584ca08250d415851071c37c"
    ),
    "hced-Sigurds1918-1": (
        "00088d1db647599f7ef6aa70a66ec79e9bf67956cac2e3cf48a4b7ee2cd1857b"
    ),
    "hced-Tampere1918-1": (
        "1231b94b6ac2165ac0594913db6f135bc12cbdebd57f25a1e8346a1c827804e3"
    ),
    "hced-Vilppula1918-1": (
        "39b3bd4b9458573ccd494812f56bf76be55c7de902d00642a87e0f580758b869"
    ),
    "hced-Vyborg1918-1": (
        "30c5358629858af1a854221739d5dab7185ec0d9ba59a729f69f229623626a4d"
    ),
}


WAVE8_FINNISH_CIVIL_WAR_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "finnish reds": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "cb3031764271e0ce17a6f69ae5c0549201a00fbb6f4c4b9a9e71a684874eb76b"
        ),
        "events_touched": 2,
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 2,
        },
        "label": "finnish reds",
        "rated_counterpart_entities": 0,
        "sole_blocker_events": 0,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 2,
    },
    "finnish whites": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "f2187b6540ccc7be65ebd19ddab107c5d3817594f27b07dcc2184e3e31fe94e2"
        ),
        "events_touched": 5,
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 5,
        },
        "label": "finnish whites",
        "rated_counterpart_entities": 0,
        "sole_blocker_events": 0,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 5,
    },
    "russian bolsheviks": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "5527457b1cdc10298ab2fab404eb7494eae7bd25a87b7f7a8154621e53b4a271"
        ),
        "events_touched": 5,
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 5,
        },
        "label": "russian bolsheviks",
        "rated_counterpart_entities": 2,
        "sole_blocker_events": 2,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 5,
    },
}


def _canonical(
    name: str,
    date_text: str,
    start_date: str,
    end_date: str | None,
    granularity: str,
    *,
    date_precision: str = "day_range",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:1918:1918",
        "date_precision": date_precision,
        "date_text": date_text,
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity,
        "name": name,
        "year_low": 1918,
        "year_high": 1918,
    }


_EVENT_SOURCE_IDS: dict[str, tuple[str, ...]] = {
    "hced-Oulo1918-1": (
        "wave8_finnish_city_oulu_history",
        "wave8_finnish_kemppi_oulu_record",
        "wave8_finnish_yle_oulu",
    ),
    "hced-Rautu1918-1": (
        "wave8_finnish_hovilainen_rautu_dates",
        "wave8_finnish_lahteenmaki_rautu",
        "wave8_finnish_manninen_rautu",
    ),
    "hced-Tampere1918-1": (
        "wave8_finnish_1914_1918_tampere",
        "wave8_finnish_vapriikki_connections",
    ),
    "hced-Vyborg1918-1": (
        "wave8_finnish_1914_1918_overview",
        "wave8_finnish_sks_viipuri",
    ),
}

_EVENT_OUTCOME_SOURCE_IDS: dict[str, tuple[str, ...]] = {
    candidate_id: tuple(
        source_id
        for source_id in source_ids
        if "outcome" in _SOURCE_BY_ID[source_id]["evidence_roles"]
    )
    for candidate_id, source_ids in _EVENT_SOURCE_IDS.items()
}


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    expected_scale_level: int,
) -> dict[str, Any]:
    evidence = sorted(_EVENT_SOURCE_IDS[candidate_id])
    outcomes = sorted(_EVENT_OUTCOME_SOURCE_IDS[candidate_id])
    return {
        "raw_row_sha256": WAVE8_FINNISH_CIVIL_WAR_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "civil_war",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "date_source_ids": evidence,
        "source_date_refinement": True,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_alias_free_1918_military_identities",
        "expected_scale_level": expected_scale_level,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_FINNISH_CIVIL_WAR_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Oulo1918-1": _contract(
        "hced-Oulo1918-1",
        _canonical(
            "Battle of Oulu",
            "2-3 February 1918",
            "1918-02-02",
            "1918-02-03",
            "city_battle_and_garrison_surrender",
        ),
        [_WHITE],
        [_RED, _OULU_GARRISON],
        (
            "Municipal, public-broadcaster, and scholarly records agree that "
            "White forces defeated the Finnish Red and local Russian-garrison "
            "defenders on 2-3 February. The Russian garrison is event-bounded; "
            "no Russian-SFSR or Soviet continuity is inferred."
        ),
        confidence=0.96,
        expected_scale_level=1,
    ),
    "hced-Rautu1918-1": _contract(
        "hced-Rautu1918-1",
        _canonical(
            "Battle of Rautu",
            "21 February-5 April 1918",
            "1918-02-21",
            "1918-04-05",
            "prolonged_station_centered_battle_and_failed_breakout",
        ),
        [_WHITE],
        [_RED, _RAUTU_DETACHMENTS],
        (
            "Independent scholarly records pin the prolonged Rautu fighting and "
            "White victory. The contract rates only the competitive battle and "
            "failed Red breakout; executions, noncombatant deaths, and later "
            "atrocity evidence are excluded from the outcome."
        ),
        confidence=0.95,
        expected_scale_level=2,
    ),
    "hced-Tampere1918-1": _contract(
        "hced-Tampere1918-1",
        _canonical(
            "Battle of Tampere",
            "15 March-6 April 1918",
            "1918-03-15",
            "1918-04-06",
            "major_urban_battle_and_capture",
        ),
        [_WHITE],
        [_RED],
        (
            "The dedicated scholarly account and Vapriikki history agree on the "
            "White capture after the 15 March-6 April battle. The reviewed "
            "battle starts on 15 March, not Wikidata's broader offensive date."
        ),
        confidence=0.99,
        expected_scale_level=2,
    ),
    "hced-Vyborg1918-1": _contract(
        "hced-Vyborg1918-1",
        _canonical(
            "Battle of Viipuri",
            "24-29 April 1918",
            "1918-04-24",
            "1918-04-29",
            "urban_encirclement_assault_and_red_surrender",
        ),
        [_WHITE],
        [_RED],
        (
            "The peer-reviewed chronology separates the White assault and Red "
            "surrender from the post-capture massacre. The raw Russian-"
            "Bolsheviks label is corrected to the documented Finnish Red "
            "defenders; Russian victims and atrocity evidence are not rated."
        ),
        confidence=0.99,
        expected_scale_level=2,
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    reviewed_actors: Iterable[str],
    point_review: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_FINNISH_CIVIL_WAR_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "disposition": "hold",
        "emit_rated_event": False,
        "hold_category": category,
        "reviewed_outcome": "unknown_not_draw",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "bound_scoring_sides": [],
        "reviewed_actor_description": list(map(str, reviewed_actors)),
        "reviewed_granularity": str(canonical_event["granularity"]),
        "location_review": {
            "modern_location_country": "retain:Finland",
            "point": point_review,
        },
        "hold_reason": reason,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "provisional_hced_hold",
        },
    }


WAVE8_FINNISH_CIVIL_WAR_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Aland1918-1": _hold(
        "hced-Aland1918-1",
        _canonical(
            "Åland intervention and occupation sequence",
            "14 February-late May 1918; non-scoring documentary envelope",
            "1918-02-14",
            None,
            "multilateral_intervention_and_occupation_sequence",
            date_precision="documentary_envelope",
        ),
        "multilateral_sequence_has_no_single_competitive_result",
        (
            "The year row combines Finnish local and expeditionary forces, "
            "Russian garrisons, Finnish Reds, Swedish intervention and mediation, "
            "and later German forces. Surrenders, occupations, and negotiated "
            "withdrawals do not establish one Finnish-White/Russian draw. The raw "
            "Draw is rejected: the result is unknown and no sides are scored."
        ),
        {
            "wave8_finnish_enqvist_coastal_defence",
            "wave8_finnish_sjoblom_aland",
            "wave8_finnish_swedish_archives_aland",
            "wave8_finnish_uppslagsverket_aland",
        },
        [
            "Finnish local and expeditionary forces",
            "Russian garrisons and Finnish Reds",
            "Swedish and German intervention forces",
        ],
        "quarantine_archipelago_centroid_in_hold_metadata_only",
    ),
    "hced-Ruovesi1918-1": _hold(
        "hced-Ruovesi1918-1",
        _canonical(
            "Ruovesi front operations",
            "5 February-19 March 1918; non-scoring documentary envelope",
            "1918-02-05",
            "1918-03-19",
            "multi_direction_multi_engagement_front",
            date_precision="documentary_envelope",
        ),
        "multi_engagement_front_cannot_supply_one_tactical_winner",
        (
            "The label covers distinct actions around Pekkala/Jäminkipohja, "
            "Väärinmaja, Pitkälä, and Pihlajalahti. A Baltic Fleet volunteer "
            "detachment participated briefly in one sector, so Bolsheviks cannot "
            "stand for the whole Red side. Strategic front success cannot invent "
            "one tactical result; the row remains unknown."
        ),
        {
            "wave8_finnish_ruovesi_doctoral_record",
            "wave8_finnish_ruovesi_thesis",
        },
        ["Finnish White forces", "Finnish Red forces", "limited Russian volunteers"],
        "quarantine_multi_site_municipal_geocode_in_hold_metadata_only",
    ),
    "hced-Sigurds1918-1": _hold(
        "hced-Sigurds1918-1",
        _canonical(
            "Sigurds-Ingels-Upinniemi-Mäkiluoto-Obbnäs sequence",
            "22-27 February 1918; non-scoring documentary envelope",
            "1918-02-22",
            "1918-02-27",
            "multi_site_escape_attack_dissolution_and_mediation_sequence",
            date_precision="documentary_envelope",
        ),
        "multiple_sites_opponents_and_results_cannot_be_one_red_victory",
        (
            "The Sigurds Guard escaped one encirclement, moved through several "
            "sites, separately failed against a Russian-held fort, and dissolved "
            "amid captures, surrenders, and Swedish mediation. These episodes do "
            "not constitute one Red tactical victory, and Swedish mediators are "
            "not promoted into a belligerent side."
        ),
        {
            "wave8_finnish_enqvist_coastal_defence",
            "wave8_finnish_kirkkonummi_1918",
            "wave8_finnish_yle_sigurds",
        },
        ["Sigurds White Guard", "Finnish Reds", "Russian fort garrison"],
        "quarantine_composite_multi_site_geocode_in_hold_metadata_only",
    ),
    "hced-Vilppula1918-1": _hold(
        "hced-Vilppula1918-1",
        _canonical(
            "Vilppula front operations",
            "2 February-17 March 1918; non-scoring documentary envelope",
            "1918-02-02",
            "1918-03-17",
            "six_week_static_front_with_multiple_actions",
            date_precision="documentary_envelope",
        ),
        "static_front_not_a_unified_battle_and_ussr_is_anachronistic",
        (
            "The official history describes a six-week front with multiple "
            "actions rather than one battle. Limited Russian aid cannot turn the "
            "whole Red side into the USSR, which did not exist in 1918, and the "
            "eventual withdrawal cannot be converted into a tactical White win."
        ),
        {
            "wave8_finnish_1914_1918_overview",
            "wave8_finnish_mantta_vilppula_history",
        },
        ["Finnish White forces", "Finnish Red forces", "limited Russian support"],
        "quarantine_multi_site_front_geocode_in_hold_metadata_only",
    ),
}


WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS = frozenset(
    WAVE8_FINNISH_CIVIL_WAR_CONTRACTS
)
WAVE8_FINNISH_CIVIL_WAR_HOLD_IDS = frozenset(WAVE8_FINNISH_CIVIL_WAR_HOLDS)
WAVE8_FINNISH_CIVIL_WAR_RESERVED_IDS = frozenset(
    WAVE8_FINNISH_CIVIL_WAR_ROW_HASHES
)
WAVE8_FINNISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Rautu1918-1"}
)
WAVE8_FINNISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = (
    frozenset()
)
WAVE8_FINNISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Rautu1918-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_finnish_hovilainen_rautu_dates",
            "wave8_finnish_lahteenmaki_rautu",
            "wave8_finnish_manninen_rautu",
        ],
        "raw_point": [30.2293083, 60.552312],
        "reason": (
            "The sources establish the prolonged station-centered battle at "
            "Rautu but do not independently audit HCED's modern locality point. "
            "Retain the modern-country assertion and withhold only the point."
        ),
    }
}


WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_MATCHES: dict[str, str] = {
    "Q10681754": "hced-Vilppula1918-1",
    "Q18661133": "hced-Oulo1918-1",
    "Q2043711": "hced-Tampere1918-1",
    "Q27839492": "hced-Rautu1918-1",
    "Q28721640": "hced-Ruovesi1918-1",
    "Q4060498": "hced-Aland1918-1",
    "Q4411911": "hced-Vyborg1918-1",
}
WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q10681754": (
        "a0967b46697774017ad330a25a95354bef77e2f46062f655d358c5e1829c266f"
    ),
    "Q18661133": (
        "a72ac94d73997f92a3e116f53b741079c5b4777ff2eede134eaa8d3fe9cdc8e1"
    ),
    "Q2043711": (
        "a58630f4a212bba77170322fc15a93189bb886d7d776fbabfb31340209dfebad"
    ),
    "Q27839492": (
        "1c731c305c26d57faa4b797856f93f605b8ce34bac13c251b6ab1b8acf1ebdae"
    ),
    "Q28721640": (
        "9029477ddab08b44335b43fdd61bbb7b816a9caee7b9d2f0adf25e4742a877a9"
    ),
    "Q4060498": (
        "e9268a7d4f7f02cc48e2ae4d127fe1aede62a63de9b7c0b592cf77d51326ef15"
    ),
    "Q4411911": (
        "6cc0fa9582d11522a3e203942dfa015b8b07d9d2f82e8f6beb56595943317ed4"
    ),
}
WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_EXPECTED: dict[str, dict[str, Any]] = {
    "Q10681754": {
        "date": "1918-03-18T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Vilppula",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
        "relationship": "point_date_front_label_not_rateable",
    },
    "Q18661133": {
        "date": "1918-02-03T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Oulu",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [
            "Russian Socialist Federative Soviet Republic",
            "The Red Guard of Finland",
            "Whites",
        ],
        "relationship": "probable_discovery_duplicate",
    },
    "Q2043711": {
        "date": "1918-03-08T00:00:00Z",
        "end_date": "1918-04-06T00:00:00Z",
        "kind": "engagement",
        "name": "Battle of Tampere",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
        "relationship": "broader_start_discovery_duplicate",
    },
    "Q27839492": {
        "date": "1918-04-05T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Rautu",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
        "relationship": "endpoint_only_discovery_duplicate",
    },
    "Q28721640": {
        "date": "1918-03-19T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Ruovesi",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
        "relationship": "front_endpoint_not_discrete_contract",
    },
    "Q4060498": {
        "date": "1918-02-15T00:00:00Z",
        "end_date": "1918-09-01T00:00:00Z",
        "kind": "engagement",
        "name": "Invasion of Åland",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
        "relationship": "broader_multilateral_container_overlap",
    },
    "Q4411911": {
        "date": "1918-04-24T00:00:00Z",
        "end_date": "1918-04-29T00:00:00Z",
        "kind": "engagement",
        "name": "Battle of Viipuri",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": ["The Red Guard of Finland", "Whites"],
        "relationship": "probable_discovery_duplicate",
    },
}
WAVE8_FINNISH_CIVIL_WAR_INTEGRATION_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    discovery_id: {
        "source_dataset": "wikidata-battles",
        "disposition": (
            "discovery_only_duplicate"
            if hced_id in WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS
            else "discovery_only_context_for_unknown_hold"
        ),
        "hced_candidate_id": hced_id,
        "outcome_disposition": "unknown_never_draw",
        "relationship": WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_EXPECTED[
            discovery_id
        ]["relationship"],
    }
    for discovery_id, hced_id in sorted(
        WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_MATCHES.items()
    )
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_FINNISH_CIVIL_WAR_CONTRACTS,
        "discovery_expected": WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_EXPECTED,
        "discovery_matches": WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_MATCHES,
        "discovery_row_hashes": WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_ROW_HASHES,
        "entities": WAVE8_FINNISH_CIVIL_WAR_ENTITIES,
        "funnel": WAVE8_FINNISH_CIVIL_WAR_FUNNEL_AUDIT,
        "holds": WAVE8_FINNISH_CIVIL_WAR_HOLDS,
        "integration_dispositions": (
            WAVE8_FINNISH_CIVIL_WAR_INTEGRATION_DISPOSITIONS
        ),
        "location_reasons": (
            WAVE8_FINNISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS
        ),
        "row_hashes": WAVE8_FINNISH_CIVIL_WAR_ROW_HASHES,
        "sources": WAVE8_FINNISH_CIVIL_WAR_SOURCES,
    }


def wave8_finnish_civil_war_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_FINNISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE = (
    "5649dc15a7bf9f8982eca6c7847814f418da4e6f9a0023b531a208dd0a3fbab9"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static(*, check_signature: bool = True) -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_FINNISH_CIVIL_WAR_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")

    entities = {
        str(entity["id"]): entity for entity in WAVE8_FINNISH_CIVIL_WAR_ENTITIES
    }
    expected_entities = {_WHITE, _RED, _OULU_GARRISON, _RAUTU_DETACHMENTS}
    if set(entities) != expected_entities:
        raise ValueError(f"{_LANE_NAME} identity inventory drift")
    for entity_id, entity in entities.items():
        note = str(entity["continuity_note"]).casefold()
        if (
            (entity["start_year"], entity["end_year"]) != (1918, 1918)
            or entity["aliases"]
            or entity["predecessors"]
            or not _is_sorted_unique(entity["source_ids"])
            or not set(entity["source_ids"]) <= source_ids
            or "rating" not in note
        ):
            raise ValueError(f"{_LANE_NAME} identity firewall drift: {entity_id}")

    if WAVE8_FINNISH_CIVIL_WAR_RESERVED_IDS != set(
        WAVE8_FINNISH_CIVIL_WAR_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} reservation inventory drift")
    if (
        WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS
        | WAVE8_FINNISH_CIVIL_WAR_HOLD_IDS
    ) != WAVE8_FINNISH_CIVIL_WAR_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} disposition partition drift")
    if (
        WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS
        & WAVE8_FINNISH_CIVIL_WAR_HOLD_IDS
    ):
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_FINNISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS != {
        "hced-Rautu1918-1"
    } or WAVE8_FINNISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} location quarantine drift")
    if set(WAVE8_FINNISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS) != {
        "hced-Rautu1918-1"
    }:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    expected_contracts = {
        "hced-Oulo1918-1": ([_WHITE], [_RED, _OULU_GARRISON], 0.96, 1),
        "hced-Rautu1918-1": ([_WHITE], [_RED, _RAUTU_DETACHMENTS], 0.95, 2),
        "hced-Tampere1918-1": ([_WHITE], [_RED], 0.99, 2),
        "hced-Vyborg1918-1": ([_WHITE], [_RED], 0.99, 2),
    }
    used_sources = {
        str(source_id)
        for entity in WAVE8_FINNISH_CIVIL_WAR_ENTITIES
        for source_id in entity["source_ids"]
    }
    for candidate_id, expected in expected_contracts.items():
        side_1, side_2, confidence, scale_level = expected
        contract = WAVE8_FINNISH_CIVIL_WAR_CONTRACTS[candidate_id]
        canonical = contract["canonical_event"]
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["side_1_entity_ids"] != side_1
            or contract["side_2_entity_ids"] != side_2
            or contract["confidence"] != confidence
            or contract["expected_scale_level"] != scale_level
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or contract["war_type"] != "civil_war"
            or canonical["year_low"] != 1918
            or canonical["year_high"] != 1918
            or canonical["date_precision"] != "day_range"
            or not canonical["start_date"]
            or not canonical["end_date"]
        ):
            raise ValueError(f"{_LANE_NAME} contract drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        date_sources = list(map(str, contract["date_source_ids"]))
        expected_sources = sorted(_EVENT_SOURCE_IDS[candidate_id])
        expected_outcome_sources = sorted(_EVENT_OUTCOME_SOURCE_IDS[candidate_id])
        families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if (
            evidence != expected_sources
            or outcomes != expected_outcome_sources
            or date_sources != evidence
            or not set(evidence) <= source_ids
            or contract["outcome_source_family_ids"] != families
            or len(families) < 2
            or contract["source_date_refinement"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} source closure drift: {candidate_id}")
        if any(
            "outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"]
            and "outcome_consistency_crosscheck"
            not in _SOURCE_BY_ID[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} non-outcome event evidence")
        used_sources.update(evidence)

    for candidate_id, hold in WAVE8_FINNISH_CIVIL_WAR_HOLDS.items():
        if (
            hold["disposition"] != "hold"
            or hold["emit_rated_event"] is not False
            or hold["result_type"] != "unknown"
            or hold["reviewed_outcome"] != "unknown_not_draw"
            or hold["unknown_is_never_draw"] is not True
            or hold["bound_scoring_sides"] != []
        ):
            raise ValueError(f"{_LANE_NAME} hold policy drift: {candidate_id}")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} hold evidence drift: {candidate_id}")
        used_sources.update(evidence)

    for reason in WAVE8_FINNISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS.values():
        evidence = list(map(str, reason["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} location evidence drift")
        used_sources.update(evidence)
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    discovery_ids = set(WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_ROW_HASHES)
    if (
        set(WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_MATCHES) != discovery_ids
        or set(WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_EXPECTED) != discovery_ids
        or set(WAVE8_FINNISH_CIVIL_WAR_INTEGRATION_DISPOSITIONS)
        != discovery_ids
        or set(WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_MATCHES.values())
        != WAVE8_FINNISH_CIVIL_WAR_RESERVED_IDS - {"hced-Sigurds1918-1"}
    ):
        raise ValueError(f"{_LANE_NAME} discovery inventory drift")
    if any(
        expected["outcome_disposition"] != "unknown_never_draw"
        for expected in WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_EXPECTED.values()
    ):
        raise ValueError(f"{_LANE_NAME} discovery unknown/draw guard drift")
    if check_signature and (
        wave8_finnish_civil_war_audit_signature()
        != WAVE8_FINNISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def _is_lane_row(row: Mapping[str, Any]) -> bool:
    if row.get("year_best") != 1918:
        return False
    if not set(map(str, row.get("war_names", []) or [])) & _LANE_WAR_NAMES:
        return False
    return (
        normalize_label(row.get("side_1_raw")) in _LANE_SIDE_LABELS
        and normalize_label(row.get("side_2_raw")) in _LANE_SIDE_LABELS
    )


def validate_wave8_finnish_civil_war_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [row for row in hced_rows if _is_lane_row(row)]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_FINNISH_CIVIL_WAR_RESERVED_IDS or len(exact) != len(
        exact_ids
    ):
        raise ValueError(f"{_LANE_NAME} exact cohort inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_FINNISH_CIVIL_WAR_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            (row.get("year_low"), row.get("year_best"), row.get("year_high"))
            != (1918, 1918, 1918)
            or row.get("do_not_rate_automatically") is not True
            or row.get("duplicate_source_id") is not False
            or row.get("massacre_raw") != "No"
        ):
            raise ValueError(f"{_LANE_NAME} source-row guard drift: {candidate_id}")

    promoted = {
        "hced-Oulo1918-1": ("Finland", "Bolsheviks", True),
        "hced-Rautu1918-1": ("Finland", "Russian Bolsheviks", True),
        "hced-Tampere1918-1": ("Finnish Whites", "Finnish Reds", True),
        "hced-Vyborg1918-1": ("Finnish Whites", "Russian Bolsheviks", True),
    }
    for candidate_id, expected in promoted.items():
        row = by_id[candidate_id]
        actual = (
            row.get("winner_raw"),
            row.get("loser_raw"),
            row.get("winner_loser_complete"),
        )
        if actual != expected or row.get("winner_raw") != row.get("side_1_raw"):
            raise ValueError(f"{_LANE_NAME} promoted outcome alignment drift: {candidate_id}")
        if row.get("loser_raw") != row.get("side_2_raw"):
            raise ValueError(f"{_LANE_NAME} promoted loser alignment drift: {candidate_id}")

    held = {
        "hced-Aland1918-1": ("Draw", None, False),
        "hced-Ruovesi1918-1": ("Finland", "Bolsheviks", True),
        "hced-Sigurds1918-1": ("Finnish Reds", "Finnish Whites", True),
        "hced-Vilppula1918-1": ("Finnish Whites", "USSR", True),
    }
    for candidate_id, expected in held.items():
        row = by_id[candidate_id]
        actual = (
            row.get("winner_raw"),
            row.get("loser_raw"),
            row.get("winner_loser_complete"),
        )
        if actual != expected:
            raise ValueError(f"{_LANE_NAME} unknown-hold guard drift: {candidate_id}")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_FINNISH_CIVIL_WAR_CONTRACTS,
        WAVE8_FINNISH_CIVIL_WAR_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_cohort_rows": len(exact)}


def validate_wave8_finnish_civil_war_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    actual: dict[str, dict[str, Any]] = {}
    for row in funnel.get("labels", []):
        label = str(row.get("label"))
        if label not in WAVE8_FINNISH_CIVIL_WAR_FUNNEL_AUDIT:
            continue
        actual[label] = {
            "candidate_ids": list(map(str, row.get("candidate_ids", []))),
            "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
            "events_touched": int(row.get("events_touched", -1)),
            "failure_cases": {
                key: int(row.get("failure_cases", {}).get(key, -1))
                for key in WAVE8_FINNISH_CIVIL_WAR_FUNNEL_AUDIT[label][
                    "failure_cases"
                ]
            },
            "label": label,
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
    if actual != WAVE8_FINNISH_CIVIL_WAR_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed: {actual}")
    return {
        "events_touched": sum(row["events_touched"] for row in actual.values()),
        "labels": len(actual),
        "sole_blocker_events": sum(
            row["sole_blocker_events"] for row in actual.values()
        ),
        "unresolved_side_attempts": sum(
            row["unresolved_side_attempts"] for row in actual.values()
        ),
        "zero_time_valid_candidates": sum(
            row["failure_cases"]["zero_time_valid_candidates"]
            for row in actual.values()
        ),
    }


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def validate_wave8_finnish_civil_war_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in (
        WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_ROW_HASHES.items()
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
        expected = WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_EXPECTED[candidate_id]
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
        "discovery_nonrating_records": len(
            WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_ROW_HASHES
        ),
        "discovery_promotions": 0,
        "unknown_never_draw_rows": len(
            WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_ROW_HASHES
        ),
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
    "hced-Aland1918-1": {"Aland", "Invasion of Åland", "Åland"},
    "hced-Oulo1918-1": {"Battle of Oulu", "Oulo", "Oulu"},
    "hced-Rautu1918-1": {"Battle of Rautu", "Rautu"},
    "hced-Ruovesi1918-1": {"Battle of Ruovesi", "Ruovesi"},
    "hced-Sigurds1918-1": {"Sigurds", "Sigurds Guard"},
    "hced-Tampere1918-1": {"Battle of Tampere", "Tampere"},
    "hced-Vilppula1918-1": {"Battle of Vilppula", "Vilppula"},
    "hced-Vyborg1918-1": {"Battle of Viipuri", "Viipuri", "Vyborg"},
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (1918, normalize_label(alias))
    for aliases in _EVENT_ALIASES.values()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_finnish_civil_war_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwd_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_finnish_civil_war_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_FINNISH_CIVIL_WAR_RESERVED_IDS
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
        if event.get("hced_candidate_id")
        in WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    if owned:
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        if owned_ids != WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS or len(owned) != len(
            owned_ids
        ):
            raise ValueError(f"{_LANE_NAME} current release ownership is partial")
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
            WAVE8_FINNISH_CIVIL_WAR_INTEGRATION_DISPOSITIONS
        ),
        "existing_release_owned_events": len(owned),
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwd_probable_twins": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_finnish_civil_war_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_FINNISH_CIVIL_WAR_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_finnish_civil_war_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_FINNISH_CIVIL_WAR_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_FINNISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_FINNISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def validate_wave8_finnish_civil_war_emissions(
    events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    owned = list(events)
    by_id = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_id) != WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS or len(owned) != len(
        by_id
    ):
        raise ValueError(f"{_LANE_NAME} emitted inventory drift")
    retained_points = {
        "hced-Oulo1918-1": ("Finland", [25.4650772, 65.0120888]),
        "hced-Tampere1918-1": ("Finland", [23.7609535, 61.4977524]),
        "hced-Vyborg1918-1": ("Russia", [28.7571571, 60.7139529]),
    }
    participant_count = 0
    coalition_events = 0
    for candidate_id, contract in WAVE8_FINNISH_CIVIL_WAR_CONTRACTS.items():
        event = by_id[candidate_id]
        canonical = contract["canonical_event"]
        expected_participants = expected_exact_hced_win_participants(
            contract["side_1_entity_ids"],
            contract["side_2_entity_ids"],
            confidence=float(contract["confidence"]),
            scale_level=int(contract["expected_scale_level"]),
            lane_name=_LANE_NAME,
        )
        if (
            event.get("id") != f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year")) != (1918, 1918)
            or event.get("date_precision") != "day_range"
            or event.get("reviewed_granularity") != canonical["granularity"]
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("event_type") != "engagement"
            or event.get("war_type") != "civil_war"
            or event.get("participants") != expected_participants
            or event.get("source_ids")
            != ["hced_dataset", *contract["evidence_refs"]]
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids")
            != contract["outcome_source_family_ids"]
            or float(event.get("confidence", -1.0))
            != float(contract["confidence"])
        ):
            raise ValueError(f"{_LANE_NAME} emitted contract drift: {candidate_id}")
        if any(
            "inconclusive" in str(participant.get("termination", ""))
            for participant in event["participants"]
        ):
            raise ValueError(f"{_LANE_NAME} emitted unknown/draw drift: {candidate_id}")
        participant_count += len(event["participants"])
        coalition_events += int(
            len(contract["side_1_entity_ids"]) > 1
            or len(contract["side_2_entity_ids"]) > 1
        )

        if candidate_id == "hced-Rautu1918-1":
            if (
                "geometry" in event
                or event.get("modern_location_country") != "Russia"
                or event.get("location_provenance", {}).get("assertion_status")
                != "unreviewed_source_assertion"
            ):
                raise ValueError(f"{_LANE_NAME} Rautu location policy drift")
        else:
            country, coordinates = retained_points[candidate_id]
            if (
                event.get("modern_location_country") != country
                or event.get("geometry", {}).get("type") != "Point"
                or event.get("geometry", {}).get("coordinates") != coordinates
                or event.get("location_provenance", {}).get("assertion_status")
                != "unreviewed_source_assertion"
            ):
                raise ValueError(f"{_LANE_NAME} retained location drift: {candidate_id}")
    return {
        "coalition_events": coalition_events,
        "events": len(owned),
        "participants": participant_count,
        "retained_countries": len(owned),
        "retained_points": len(retained_points),
    }


def promote_wave8_finnish_civil_war_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_finnish_civil_war_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_FINNISH_CIVIL_WAR_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine(events)
    validate_wave8_finnish_civil_war_emissions(events)
    return events


def wave8_finnish_civil_war_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_FINNISH_CIVIL_WAR_CONTRACTS.values(),
                    *WAVE8_FINNISH_CIVIL_WAR_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_finnish_civil_war_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_FINNISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_nonrating_records": len(
            WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_ROW_HASHES
        ),
        "holds": len(WAVE8_FINNISH_CIVIL_WAR_HOLDS),
        "integration_dispositions": len(
            WAVE8_FINNISH_CIVIL_WAR_INTEGRATION_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_FINNISH_CIVIL_WAR_ENTITIES),
        "new_sources": len(WAVE8_FINNISH_CIVIL_WAR_SOURCES),
        "newly_rated_events": len(WAVE8_FINNISH_CIVIL_WAR_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_FINNISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_FINNISH_CIVIL_WAR_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_FINNISH_CIVIL_WAR_RESERVED_IDS),
        "terminal_exclusions": 0,
        "unknown_discovery_outcomes": len(
            WAVE8_FINNISH_CIVIL_WAR_DISCOVERY_ROW_HASHES
        ),
    }


def wave8_finnish_civil_war_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_finnish_civil_war_counts(),
        "cohorts": wave8_finnish_civil_war_cohort_counts(),
        "country_quarantine_additions": sorted(
            WAVE8_FINNISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_FINNISH_CIVIL_WAR_INTEGRATION_DISPOSITIONS.items()
            )
        ],
        "final_audit_signature": (
            WAVE8_FINNISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE
        ),
        "held_candidate_ids": sorted(WAVE8_FINNISH_CIVIL_WAR_HOLD_IDS),
        "point_quarantine_additions": sorted(
            WAVE8_FINNISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS
        ),
        "promoted_candidate_ids": sorted(
            WAVE8_FINNISH_CIVIL_WAR_CONTRACT_IDS
        ),
    }


_validate_static()
