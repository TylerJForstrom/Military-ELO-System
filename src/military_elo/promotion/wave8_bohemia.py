"""Candidate-keyed audit of HCED's four unresolved ``Bohemia`` rows.

The raw label spans two unrelated military actors: Ottokar II's royal host in
1260-1278 and the forces raised by the rebellious Bohemian Estates in
1618-1620.  This lane never opens a generic ``Bohemia`` alias.  It promotes
only the four fingerprinted rows, replaces each shorthand side with the exact
documented opposing force, and retains tactical outcomes only.
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
    "WAVE8_BOHEMIA_CONTRACT_IDS",
    "WAVE8_BOHEMIA_CONTRACTS",
    "WAVE8_BOHEMIA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_BOHEMIA_ENTITIES",
    "WAVE8_BOHEMIA_EXPECTED_CANDIDATE_IDS",
    "WAVE8_BOHEMIA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_BOHEMIA_FUNNEL_AUDIT",
    "WAVE8_BOHEMIA_HOLDS",
    "WAVE8_BOHEMIA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_BOHEMIA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_BOHEMIA_RESERVED_IDS",
    "WAVE8_BOHEMIA_ROW_HASHES",
    "WAVE8_BOHEMIA_SOURCES",
    "install_wave8_bohemia_entities",
    "install_wave8_bohemia_sources",
    "promote_wave8_bohemia_contracts",
    "validate_wave8_bohemia_funnel",
    "validate_wave8_bohemia_integration_dispositions",
    "validate_wave8_bohemia_queue_contracts",
    "wave8_bohemia_audit_signature",
    "wave8_bohemia_cohort_counts",
    "wave8_bohemia_counts",
)


_LANE_NAME = "Wave 8 exact Bohemia actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_bohemia"
_EVENT_ID_PREFIX = "hced_wave8_bohemia_"
_EXACT_LABEL = "bohemia"

_OTTOKAR_HOST = "ottokar_ii_bohemian_royal_host_1260_1278"
_BELA_COALITION = "bela_iv_hungarian_led_coalition_kressenbrunn_1260"
_RUDOLF_LADISLAUS_COALITION = "rudolf_ladislaus_allied_host_marchfeld_1278"
_BOHEMIAN_ESTATES = "bohemian_estates_revolt_forces_1618_1620"
_BUQUOY_FORCE = "buquoy_imperial_army_zablati_1619"
_IMPERIAL_LEAGUE_FORCE = "imperial_catholic_league_army_white_mountain_1620"


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


WAVE8_BOHEMIA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_bohemia_czech_mfa_history",
        "Czech History: the Přemyslid Dynasty and the Bohemian Estates",
        "https://mzv.gov.cz/abuja/en/about_the_czech_republic/history/index.html",
        "Ministry of Foreign Affairs of the Czech Republic",
        "official_state_history",
        "czech_mfa_history",
        crosscheck=True,
    ),
    _source(
        "wave8_bohemia_national_museum_premyslids",
        "The Přemyslids: A Ruling Dynasty and Its Age",
        (
            "https://www.nm.cz/en/e-shop/publications-in-english/"
            "the-premyslids-a-ruling-dynasty-and-its-age"
        ),
        "National Museum, Prague",
        "official_museum_scholarly_catalogue",
        "czech_national_museum_premyslids",
        crosscheck=True,
    ),
    _source(
        "wave8_bohemia_vhu_kressenbrunn",
        (
            "The Second Czech-Hungarian War over the Babenberg Heritage and "
            "the Battle at Kressenbrunn"
        ),
        (
            "https://www.vhu.sk/8653-sk/ii-cesko-uhorska-vojna-o-"
            "babenberske-dedicstvo-1260-a-bitka-pri-kressenbrune/"
        ),
        "Military History Institute, Bratislava / Vojenská história 20.2",
        "peer_reviewed_military_history_article",
        "rohac_kressenbrunn_2016",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_bohemia_deutsche_biographie_ottokar",
        "Přemysl Otakar II (Ottokar II), King of Bohemia",
        "https://www.deutsche-biographie.de/sfz74566.html",
        "Historische Kommission bei der Bayerischen Akademie der Wissenschaften",
        "scholarly_national_biography",
        "deutsche_biographie_ottokar_ii",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_bohemia_habsburger_marchfeld",
        "Rudolf I: The decisive battle",
        "https://www.habsburger.net/en/chapter/rudolf-i-decisive-battle",
        "Schönbrunn Group / Die Welt der Habsburger",
        "official_museum_public_history",
        "habsburger_net_marchfeld",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_bohemia_orf_lbi_marchfeld",
        "1278: Mass graves from the Battle of Marchfeld discovered",
        "https://science.orf.at/stories/3210776/",
        "ORF Science with Ludwig Boltzmann Institute battlefield archaeology",
        "public_broadcaster_archaeology_report",
        "orf_lbi_marchfeld_2022",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_bohemia_jcu_zablati",
        "The Communicative Image of Military Clashes during the Czech Estates Uprising",
        (
            "https://dspace.jcu.cz/bitstream/handle/20.500.14390/36154/"
            "Komunikativni_obraz_vojenskych_stretu_za_ceskeho_"
            "stavovskeho_povstani.pdf?sequence=1"
        ),
        "University of South Bohemia in České Budějovice",
        "university_source_critical_history_thesis",
        "cizek_jcu_zablati_2017",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_bohemia_npu_buquoy",
        "Four hundred years since the death of Karel Bonaventura Buquoy",
        (
            "https://www.npu.cz/cs/novinky/74148-ctyri-sta-let-od-"
            "hrdinske-smrti-karla-bonaventury-buquoye"
        ),
        "National Heritage Institute of the Czech Republic",
        "official_heritage_history",
        "czech_npu_buquoy_2021",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_bohemia_oxford_white_mountain",
        "Battle of White Mountain, 8 November 1620",
        "https://www.cabinet.ox.ac.uk/battle-white-mountain-8-november-1620",
        "University of Oxford Cabinet",
        "university_public_history",
        "oxford_cabinet_white_mountain",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_bohemia_czech_mod_white_mountain",
        "Battle of White Mountain",
        "https://valecnehroby.mo.gov.cz/aktuality/bitva-na-bile-hore",
        "Ministry of Defence of the Czech Republic",
        "official_military_commemoration_history",
        "czech_mod_white_mountain",
        outcome=True,
        crosscheck=True,
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_BOHEMIA_SOURCES}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
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
            boundary_note
            + " No generic Bohemia, Czechia, Germany, Hungary, Habsburg, or "
            "religious-population alias resolves to this identity. It inherits no "
            "Elo from a predecessor, successor, dynasty, state namesake, or modern "
            "country."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_BOHEMIA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _OTTOKAR_HOST,
        "Ottokar II's Bohemian royal host (1260-1278)",
        "ruler_bounded_royal_force",
        1260,
        1278,
        "Bohemia, Austria, Styria, and the Marchfeld",
        [
            "wave8_bohemia_czech_mfa_history",
            "wave8_bohemia_deutsche_biographie_ottokar",
            "wave8_bohemia_national_museum_premyslids",
            "wave8_bohemia_vhu_kressenbrunn",
        ],
        (
            "Bounded from the Kressenbrunn campaign through Ottokar II's death at "
            "Marchfeld. It represents the king's Bohemian-led royal host in these "
            "two reviewed actions, not every contingent or the Kingdom of Bohemia "
            "under another ruler."
        ),
    ),
    _entity(
        _BELA_COALITION,
        "Béla IV's Hungarian-led coalition at Kressenbrunn (1260)",
        "event_bounded_royal_coalition",
        1260,
        1260,
        "Hungary, Galicia, and the Marchfeld",
        [
            "wave8_bohemia_deutsche_biographie_ottokar",
            "wave8_bohemia_vhu_kressenbrunn",
        ],
        (
            "Bounded to Béla IV's Hungarian-led coalition defeated at "
            "Kressenbrunn; it is not the Kingdom of Hungary alone or its forces in "
            "another war."
        ),
    ),
    _entity(
        _RUDOLF_LADISLAUS_COALITION,
        "Rudolf I and Ladislaus IV's allied host at Marchfeld (1278)",
        "event_bounded_royal_coalition",
        1278,
        1278,
        "Dürnkrut-Jedenspeigen, Marchfeld",
        [
            "wave8_bohemia_deutsche_biographie_ottokar",
            "wave8_bohemia_habsburger_marchfeld",
            "wave8_bohemia_orf_lbi_marchfeld",
        ],
        (
            "Bounded to the allied German-royal, Austrian, Hungarian, and Cuman "
            "host that defeated Ottokar II on 26 August 1278. It does not merge "
            "the Holy Roman Empire and Hungary outside this event."
        ),
    ),
    _entity(
        _BOHEMIAN_ESTATES,
        "Bohemian Estates' revolt forces (1618-1620)",
        "conflict_bounded_estates_force",
        1618,
        1620,
        "Crown of Bohemia",
        [
            "wave8_bohemia_czech_mfa_history",
            "wave8_bohemia_czech_mod_white_mountain",
            "wave8_bohemia_jcu_zablati",
            "wave8_bohemia_oxford_white_mountain",
        ],
        (
            "Bounded to the military forces of the rebellious Bohemian Estates, "
            "including Mansfeld's corps at Záblatí and the estates-and-mercenary "
            "army at White Mountain. It ends with the revolt's battlefield defeat."
        ),
    ),
    _entity(
        _BUQUOY_FORCE,
        "Buquoy's imperial army at Záblatí (1619)",
        "event_bounded_imperial_force",
        1619,
        1619,
        "South Bohemia",
        ["wave8_bohemia_jcu_zablati", "wave8_bohemia_npu_buquoy"],
        (
            "Bounded to Karel Bonaventura Buquoy's imperial mercenary corps in "
            "the 10 June 1619 battle, not the Habsburg Monarchy or every imperial "
            "army in the Bohemian Revolt."
        ),
    ),
    _entity(
        _IMPERIAL_LEAGUE_FORCE,
        "Combined Imperial-Catholic League army at White Mountain (1620)",
        "event_bounded_allied_army",
        1620,
        1620,
        "White Mountain near Prague",
        [
            "wave8_bohemia_czech_mod_white_mountain",
            "wave8_bohemia_oxford_white_mountain",
        ],
        (
            "Bounded to Ferdinand II's imperial army and the German Catholic "
            "League force combined for White Mountain. The umbrella prevents the "
            "source shorthand 'Habsburg Empire' from omitting a decisive ally."
        ),
    ),
)


WAVE8_BOHEMIA_ROW_HASHES: dict[str, str] = {
    "hced-Kressenbrunn1260-1": "8bf1d9b26f3835952a23dfc78f0e31666e52ce0348f08579c56e3d22b91989f2",
    "hced-Marchfeld1278-1": "b252599622656fdbeeeede39402f849c566a0f62cd0f7b5f6c901e132032f4fb",
    "hced-Sablat1619-1": "5336ea6198b45d7675cac966b3cbac6c93eebd31e97a3ed3f71fb7ff6a2cd403",
    "hced-White Mountain1620-1": "f26b7b81236eae2a1399070e9f110767c7df6138e7b7b20a5447d22e6421e084",
}
WAVE8_BOHEMIA_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_BOHEMIA_ROW_HASHES)

WAVE8_BOHEMIA_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "74e0345fa1ff4b4929c547db72cdc8430464a4e91f7f0cc66dce1e90281c3650"
    ),
    "events_touched": 4,
    "label": _EXACT_LABEL,
    "sole_blocker_events": 3,
    "zero_time_valid_candidates": 4,
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
    side_1: Iterable[str],
    side_2: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    cohort: str,
    confidence: float,
    war_type: str,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_BOHEMIA_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_exact_historical_forces",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_BOHEMIA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Kressenbrunn1260-1": _contract(
        "hced-Kressenbrunn1260-1",
        _canonical(
            "Battle of Kressenbrunn",
            1260,
            "12 July 1260",
            "day",
            "single_battle_in_the_babenberg_succession_war",
        ),
        [_OTTOKAR_HOST],
        [_BELA_COALITION],
        [
            "wave8_bohemia_czech_mfa_history",
            "wave8_bohemia_deutsche_biographie_ottokar",
            "wave8_bohemia_national_museum_premyslids",
            "wave8_bohemia_vhu_kressenbrunn",
        ],
        [
            "wave8_bohemia_deutsche_biographie_ottokar",
            "wave8_bohemia_vhu_kressenbrunn",
        ],
        (
            "The military-history study and scholarly biography independently "
            "identify Ottokar II's victory over Béla IV's Hungarian-led army. "
            "The contract does not assign the coalition result to Hungary alone."
        ),
        cohort="ottokar_ii_royal_wars",
        confidence=0.93,
        war_type="interstate",
    ),
    "hced-Marchfeld1278-1": _contract(
        "hced-Marchfeld1278-1",
        _canonical(
            "Battle on the Marchfeld",
            1278,
            "26 August 1278",
            "day",
            "single_battle_at_durnkrut_and_jedenspeigen",
        ),
        [_RUDOLF_LADISLAUS_COALITION],
        [_OTTOKAR_HOST],
        [
            "wave8_bohemia_deutsche_biographie_ottokar",
            "wave8_bohemia_habsburger_marchfeld",
            "wave8_bohemia_orf_lbi_marchfeld",
        ],
        [
            "wave8_bohemia_deutsche_biographie_ottokar",
            "wave8_bohemia_habsburger_marchfeld",
            "wave8_bohemia_orf_lbi_marchfeld",
        ],
        (
            "Three independent institutional sources agree that Rudolf I and "
            "Ladislaus IV's allied host defeated Ottokar II, who died after the "
            "battle. No strategic Habsburg succession result is inferred."
        ),
        cohort="ottokar_ii_royal_wars",
        confidence=0.96,
        war_type="interstate",
    ),
    "hced-Sablat1619-1": _contract(
        "hced-Sablat1619-1",
        _canonical(
            "Battle of Záblatí",
            1619,
            "10 June 1619",
            "day",
            "single_battle_in_the_bohemian_estates_revolt",
        ),
        [_BUQUOY_FORCE],
        [_BOHEMIAN_ESTATES],
        ["wave8_bohemia_jcu_zablati", "wave8_bohemia_npu_buquoy"],
        ["wave8_bohemia_jcu_zablati", "wave8_bohemia_npu_buquoy"],
        (
            "The university source study and Czech National Heritage Institute "
            "independently identify Buquoy's victory over Mansfeld's force in the "
            "service of the rebellious Bohemian Estates."
        ),
        cohort="bohemian_estates_revolt",
        confidence=0.94,
        war_type="civil_war",
    ),
    "hced-White Mountain1620-1": _contract(
        "hced-White Mountain1620-1",
        _canonical(
            "Battle of White Mountain",
            1620,
            "8 November 1620",
            "day",
            "single_battle_in_the_bohemian_estates_revolt",
        ),
        [_IMPERIAL_LEAGUE_FORCE],
        [_BOHEMIAN_ESTATES],
        [
            "wave8_bohemia_czech_mfa_history",
            "wave8_bohemia_czech_mod_white_mountain",
            "wave8_bohemia_oxford_white_mountain",
        ],
        [
            "wave8_bohemia_czech_mod_white_mountain",
            "wave8_bohemia_oxford_white_mountain",
        ],
        (
            "Oxford and the Czech Ministry of Defence independently identify the "
            "defeat of the Bohemian Estates by the combined Imperial-Catholic "
            "League army. The source's Habsburg shorthand is not allowed to erase "
            "the Catholic League side component."
        ),
        cohort="bohemian_estates_revolt",
        confidence=0.97,
        war_type="civil_war",
    ),
}

WAVE8_BOHEMIA_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_BOHEMIA_CONTRACT_IDS = frozenset(WAVE8_BOHEMIA_CONTRACTS)
WAVE8_BOHEMIA_RESERVED_IDS = WAVE8_BOHEMIA_CONTRACT_IDS
WAVE8_BOHEMIA_POINT_QUARANTINE_ADDITIONS = WAVE8_BOHEMIA_CONTRACT_IDS
WAVE8_BOHEMIA_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_BOHEMIA_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources identify the named battlefield and present-day "
            "country but do not independently establish HCED's exact coordinate; "
            "retain the country assertion and withhold the point."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_BOHEMIA_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_BOHEMIA_CONTRACTS,
        "entities": WAVE8_BOHEMIA_ENTITIES,
        "funnel": WAVE8_BOHEMIA_FUNNEL_AUDIT,
        "holds": WAVE8_BOHEMIA_HOLDS,
        "location_reasons": WAVE8_BOHEMIA_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_BOHEMIA_ROW_HASHES,
        "sources": WAVE8_BOHEMIA_SOURCES,
    }


def wave8_bohemia_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_BOHEMIA_FINAL_AUDIT_SIGNATURE = (
    "903e280d26411c4605be5f97b1a42124ff98bec40184c5fa82334b1dee782813"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_BOHEMIA_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_BOHEMIA_ENTITIES}
    if len(entity_by_id) != len(WAVE8_BOHEMIA_ENTITIES):
        raise ValueError(f"{_LANE_NAME} duplicate entity id")
    if WAVE8_BOHEMIA_CONTRACT_IDS != WAVE8_BOHEMIA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} candidate inventory drift")
    if WAVE8_BOHEMIA_HOLDS or WAVE8_BOHEMIA_RESERVED_IDS != WAVE8_BOHEMIA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} reservation drift")
    if WAVE8_BOHEMIA_POINT_QUARANTINE_ADDITIONS != WAVE8_BOHEMIA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point review incomplete")
    if WAVE8_BOHEMIA_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    if set(WAVE8_BOHEMIA_LOCATION_QUARANTINE_REASONS) != WAVE8_BOHEMIA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for entity in WAVE8_BOHEMIA_ENTITIES:
        if entity["aliases"] or int(entity["start_year"]) > int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} entity boundary drift")
        refs = list(map(str, entity["source_ids"]))
        if not refs or not _is_sorted_unique(refs) or not set(refs) <= source_ids:
            raise ValueError(f"{_LANE_NAME} entity source drift")
        used_sources.update(refs)

    for candidate_id, contract in WAVE8_BOHEMIA_CONTRACTS.items():
        if contract["disposition"] != "promote" or contract["result_type"] != "win":
            raise ValueError(f"{_LANE_NAME} disposition drift: {candidate_id}")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} outcome override drift: {candidate_id}")
        for side_key in ("side_1_entity_ids", "side_2_entity_ids"):
            side = list(map(str, contract[side_key]))
            if not side or not set(side) <= set(entity_by_id):
                raise ValueError(f"{_LANE_NAME} unknown exact actor: {candidate_id}")
            used_entities.update(side)
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence is not canonical: {candidate_id}")
        if not set(outcomes) <= set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} contains an unused entity fixture")
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_bohemia_audit_signature() != WAVE8_BOHEMIA_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_bohemia_queue_contracts(
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
    if exact_ids != WAVE8_BOHEMIA_EXPECTED_CANDIDATE_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_BOHEMIA_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("year_low") != row.get("year_high") or row.get("year_best") != row.get(
            "year_low"
        ):
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if row.get("winner_raw") not in {row.get("side_1_raw"), row.get("side_2_raw")}:
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True or row.get("massacre_raw") != "No":
            raise ValueError(f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_BOHEMIA_CONTRACTS,
        WAVE8_BOHEMIA_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_bohemia_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    labels = [row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL]
    if len(labels) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    label = labels[0]
    checks = {
        "candidate_ids": list(map(str, label.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(label.get("event_candidate_id_sha256")),
        "events_touched": int(label.get("events_touched", -1)),
        "label": str(label.get("label")),
        "sole_blocker_events": int(label.get("sole_blocker_events", -1)),
        "zero_time_valid_candidates": int(
            label.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
        ),
    }
    if checks != WAVE8_BOHEMIA_FUNNEL_AUDIT:
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


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Kressenbrunn1260-1": {"Kressenbrunn", "Groissenbrunn", "Groißenbrunn"},
    "hced-Marchfeld1278-1": {
        "Marchfeld",
        "Battle on the Marchfeld",
        "Dürnkrut and Jedenspeigen",
    },
    "hced-Sablat1619-1": {"Sablat", "Záblatí", "Zablati"},
    "hced-White Mountain1620-1": {"White Mountain", "Bílá Hora", "Bila Hora"},
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (int(contract["canonical_event"]["year_low"]), normalize_label(alias))
    for candidate_id, contract in WAVE8_BOHEMIA_CONTRACTS.items()
    for alias in {
        str(contract["canonical_event"]["name"]),
        *_EVENT_ALIASES[candidate_id],
    }
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_bohemia_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_bohemia_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_BOHEMIA_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_BOHEMIA_CONTRACT_IDS
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


def install_wave8_bohemia_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_BOHEMIA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_bohemia_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_BOHEMIA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_BOHEMIA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_BOHEMIA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_bohemia_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_bohemia_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_BOHEMIA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_bohemia_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(Counter(str(item["cohort"]) for item in WAVE8_BOHEMIA_CONTRACTS.values()).items())
    )


def wave8_bohemia_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": 0,
        "new_entities": len(WAVE8_BOHEMIA_ENTITIES),
        "new_sources": len(WAVE8_BOHEMIA_SOURCES),
        "newly_rated_events": len(WAVE8_BOHEMIA_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(WAVE8_BOHEMIA_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_BOHEMIA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_BOHEMIA_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


_validate_static()
