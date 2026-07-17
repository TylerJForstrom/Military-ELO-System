"""Candidate-keyed audit of HCED's four unresolved exact ``FLN`` rows.

HCED uses the political-front label ``FLN`` for the armed Algerian side in
four Algerian War records.  This lane does not open that label globally.  It
curates the time-bounded French Fourth Republic and the FLN's National
Liberation Army (ALN), then promotes only the discrete Battle of Souk Ahras.

The Battle of Algiers, the Tunisian-frontier campaign, and Operation Jumelles
remain explicit holds because each source row compresses a multi-phase or
multi-month operation into one apparent engagement.  Their broad tactical
orientation is not converted into a synthetic Elo result; unknown/unrated is
never treated as a draw.
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
    "WAVE8_FLN_CONTRACT_IDS",
    "WAVE8_FLN_CONTRACTS",
    "WAVE8_FLN_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_FLN_ENTITIES",
    "WAVE8_FLN_FINAL_AUDIT_SIGNATURE",
    "WAVE8_FLN_FUNNEL_AUDIT",
    "WAVE8_FLN_HOLD_IDS",
    "WAVE8_FLN_HOLDS",
    "WAVE8_FLN_LOCATION_QUARANTINE_REASONS",
    "WAVE8_FLN_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_FLN_RESERVED_IDS",
    "WAVE8_FLN_ROW_HASHES",
    "WAVE8_FLN_SOURCES",
    "install_wave8_fln_entities",
    "install_wave8_fln_sources",
    "promote_wave8_fln_contracts",
    "validate_wave8_fln_funnel",
    "validate_wave8_fln_integration_dispositions",
    "validate_wave8_fln_queue_contracts",
    "wave8_fln_audit_signature",
    "wave8_fln_cohort_counts",
    "wave8_fln_counts",
    "wave8_fln_metadata",
)


_LANE_NAME = "Wave 8 exact FLN actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_fln"
_EVENT_ID_PREFIX = "hced_wave8_fln_"
_EXACT_LABEL = "fln"
_COHORT = "algerian_war_fln_exact_label_1956_1959"

_FOURTH_REPUBLIC = "clio_fr_france_modern_2_1945_396ed149"
_ALN = "algerian_national_liberation_army_1954_1962"


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
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_FLN_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_fln_assemblee_fourth_republic",
        "Quatrième République",
        (
            "https://www.assemblee-nationale.fr/dyn/"
            "histoire-et-patrimoine/quatrieme-republique"
        ),
        "Assemblée nationale",
        "official_constitutional_history",
        "assemblee_nationale_fourth_republic",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_fln_constitutional_council_fifth_republic",
        "La Constitution et mes droits (1)",
        "https://qpc360.conseil-constitutionnel.fr/constitution-et-mes-droits-1",
        "Conseil constitutionnel",
        "official_constitutional_reference",
        "conseil_constitutionnel_fifth_republic",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_fln_algerian_mdn_aln_origin",
        "History of the National Liberation Army",
        (
            "https://www.mdn.dz/site_principal/sommaire/"
            "presentation/histoire_an.php"
        ),
        "Ministry of National Defence, Algeria",
        "official_military_history",
        "algerian_mdn_aln_history",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_fln_algerian_mdn_pna_transition",
        "From the National Liberation Army to the People's National Army",
        (
            "https://www.mdn.dz/site_principal/sommaire/"
            "presentation/histoire1_an.php"
        ),
        "Ministry of National Defence, Algeria",
        "official_military_history",
        "algerian_mdn_pna_history",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_fln_army_algiers_1957",
        "Algiers-1957: An Approach to Urban Counterinsurgency",
        (
            "https://www.armyupress.army.mil/Journals/Military-Review/"
            "English-Edition-Archives/mr-history-page/"
            "MR-Categories-Guerrilla-Warfare/Algiers-1957-Kee/"
        ),
        "Military Review / Army University Press",
        "professional_military_study",
        "kee_algiers_1957",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_fln_ecpad_algiers",
        "La seconde bataille d'Alger: le 3e RPC revient dans la capitale",
        (
            "https://imagesdefense.gouv.fr/fr/"
            "parachutistes-encadrant-la-foule-sur-la-place-du-gouvernement-a-alger.html"
        ),
        "ECPAD / ImagesDéfense",
        "official_archival_reportage_notice",
        "ecpad_second_battle_algiers",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_fln_chemins_1958",
        "1958, une nouvelle République en guerre",
        (
            "https://www.cheminsdememoire.gouv.fr/fr/revue/"
            "1958-une-nouvelle-republique-en-guerre"
        ),
        "Ministère des Armées, Chemins de mémoire",
        "official_historical_synthesis",
        "chemins_memoire_algeria_1958",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_fln_ageron_borders",
        "Un versant de la guerre d'Algérie: la bataille des frontières (1956-1962)",
        "https://www.persee.fr/doc/rhmc_0048-8003_1999_num_46_2_1966",
        "Revue d'histoire moderne & contemporaine / Persée",
        "peer_reviewed_journal_article",
        "ageron_algerian_border_battle_1999",
        ["outcome", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_fln_connelly_souk_ahras",
        "A Diplomatic Revolution: Algeria's Fight for Independence",
        (
            "https://global.oup.com/academic/product/"
            "a-diplomatic-revolution-9780195170955"
        ),
        "Oxford University Press",
        "scholarly_monograph",
        "connelly_diplomatic_revolution_2002",
        ["outcome"],
    ),
    _source(
        "wave8_fln_fsale_souk_ahras",
        "La bataille de la frontière tunisienne en 1958",
        (
            "https://www.legionetrangere.fr/la-fsale/actualites-de-la-fsale/"
            "1627-la-bataille-de-la-frontiere-tunisienne-en-1958.html"
        ),
        "Fédération des Sociétés d'Anciens de la Légion étrangère",
        "veterans_historical_synthesis",
        "fsale_tunisian_frontier_1958",
        ["outcome", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_fln_ecpad_jumelles",
        "L'opération Jumelles en Kabylie sous le commandement du général Challe",
        (
            "https://imagesdefense.gouv.fr/fr/"
            "l-operation-jumelles-en-kabylie-sous-le-commandement-du-general-challe.html"
        ),
        "ECPAD / ImagesDéfense",
        "official_archival_reportage_notice",
        "ecpad_operation_jumelles",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_FLN_SOURCES}


# Both aliases lists remain empty.  These identities can only be reached by the
# fingerprinted candidate contract below; neither ``France`` nor ``FLN`` gains
# a generic resolver path.
WAVE8_FLN_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _FOURTH_REPUBLIC,
        "name": "French Fourth Republic",
        "kind": "republic",
        "start_year": 1946,
        "end_year": 1958,
        "region": "France and the French Union",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Curates the preferred non-parenthesized Cliopatria source candidate "
            "to the constitutional Fourth Republic, inaugurated on 27 October "
            "1946 and ending when the Fifth Republic constitution entered force "
            "on 4 October 1958. The April-May 1958 Souk Ahras event is therefore "
            "inside this identity. No generic France alias is opened, no Elo is "
            "inherited from wartime or provisional regimes, and no rating crosses "
            "into the separately rated French Fifth Republic."
        ),
        "source_ids": [
            "cliopatria_v020",
            "wave8_fln_assemblee_fourth_republic",
            "wave8_fln_constitutional_council_fifth_republic",
        ],
    },
    {
        "id": _ALN,
        "name": "Algerian National Liberation Army",
        "kind": "national_liberation_army",
        "start_year": 1954,
        "end_year": 1962,
        "region": "Algeria and Tunisian-Moroccan border bases",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Time-bounded armed wing of the Algerian National Liberation Front "
            "during the 1954-1962 war. The 1 November 1954 declaration created "
            "the FLN and its armed section, the ALN; after independence in July "
            "1962 ALN cadres formed the army of the new republic. Only exact, "
            "fingerprinted military events may use this identity. The political "
            "FLN party, civilian networks, the post-independence People's National "
            "Army, and the modern Algerian state do not inherit its Elo."
        ),
        "source_ids": [
            "wave8_fln_algerian_mdn_aln_origin",
            "wave8_fln_algerian_mdn_pna_transition",
            "wave8_fln_army_algiers_1957",
        ],
    },
)


WAVE8_FLN_ROW_HASHES: dict[str, str] = {
    "hced-Algiers1956-1957-1": (
        "40802ae9cdff20369a8c16c448e6461a25e3480cc1e35f46303243322ce940bc"
    ),
    "hced-Frontier1958-1": (
        "f4cd85fddd524170cb57b8a33a7bad34714d2a5761f973585a8d58cee8186834"
    ),
    "hced-Kabylie1959-1": (
        "b61fa4b8a19dd02f6ef1ed2fa815faf0b9831ed7368f6359a558410336c14b12"
    ),
    "hced-Souk-Ahras1958-1": (
        "423d040cbb6853d136c327d7234849794694ad7658e1d7cdb36bd73e8d6e6a17"
    ),
}

WAVE8_FLN_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "59f7398284696021f111723f276fe0274096b6147df82c3d706288a30c550484"
    ),
    "events_touched": 4,
    "label": _EXACT_LABEL,
    "rated_counterpart_entities": 1,
    "sole_blocker_events": 3,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 4,
    "zero_time_valid_candidates": 4,
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    granularity: str,
    *,
    date_precision: str = "year",
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
    evidence_refs: Iterable[str],
    outcome_sources: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_sources)))
    return {
        "raw_row_sha256": WAVE8_FLN_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "side_1_entity_ids": [_FOURTH_REPUBLIC],
        "side_2_entity_ids": [_ALN],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
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
        "actor_override": "candidate_keyed_fourth_republic_and_aln",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_FLN_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Souk-Ahras1958-1": _contract(
        "hced-Souk-Ahras1958-1",
        _canonical(
            "Battle of Souk Ahras",
            1958,
            "28 April-3 May 1958",
            "multi_day_border_battle",
            date_precision="day_range",
        ),
        {
            "wave8_fln_ageron_borders",
            "wave8_fln_chemins_1958",
            "wave8_fln_connelly_souk_ahras",
            "wave8_fln_fsale_souk_ahras",
        },
        {
            "wave8_fln_ageron_borders",
            "wave8_fln_connelly_souk_ahras",
            "wave8_fln_fsale_souk_ahras",
        },
        (
            "The reviewed histories distinguish the six-day Souk Ahras battle "
            "from the January-May frontier campaign that contains it. They "
            "describe the ALN crossing force as largely killed, captured, or "
            "stopped, preserving HCED's French tactical-victory orientation. "
            "Only that bounded battlefield result is rated; neither the wider "
            "border campaign nor the eventual Algerian strategic victory is "
            "inferred from it."
        ),
        confidence=0.96,
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    category: str,
    reviewed_outcome: str,
    reason: str,
    evidence_refs: Iterable[str],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_FLN_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "disposition": "hold",
        "hold_category": category,
        "reviewed_outcome": reviewed_outcome,
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_actor_description": [
            "French Fourth or Fifth Republic forces, as date-bounded",
            "Algerian National Liberation Army and associated FLN networks",
        ],
        "reviewed_granularity": str(canonical_event["granularity"]),
        "hold_reason": reason,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "provisional_hced_hold",
        },
    }


WAVE8_FLN_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Algiers1956-1957-1": _hold(
        "hced-Algiers1956-1957-1",
        _canonical(
            "Battle of Algiers urban campaign",
            1956,
            "September 1956-October 1957",
            "multi_phase_urban_counterinsurgency_campaign",
            date_precision="month_range",
        ),
        "multi_episode_urban_campaign_not_single_elo_event",
        "broad_french_tactical_suppression_attested_but_not_a_single_engagement",
        (
            "The archival and military studies describe a nine-month sequence "
            "with distinct first and second phases, bombings, a general strike, "
            "police powers, arrests, intelligence operations, and destruction of "
            "urban networks. HCED's one-line 1956 row is therefore not a single "
            "head-to-head battle result. It remains unrated and is never encoded "
            "as a draw."
        ),
        {
            "wave8_fln_army_algiers_1957",
            "wave8_fln_chemins_1958",
            "wave8_fln_ecpad_algiers",
        },
    ),
    "hced-Frontier1958-1": _hold(
        "hced-Frontier1958-1",
        _canonical(
            "Battle of the Tunisian Frontier campaign",
            1958,
            "January-May 1958",
            "multi_month_border_campaign_envelope",
            date_precision="month_range",
        ),
        "campaign_envelope_contains_promoted_souk_ahras_battle",
        "broad_french_tactical_interdiction_success_not_rated_as_one_event",
        (
            "The sources identify a continuous series of attempted crossings and "
            "engagements from January through May. That umbrella contains the "
            "separately fingerprinted Souk Ahras battle promoted by this lane. "
            "Rating the Frontier row would double-count its constituent battle "
            "and collapse many other actions into a synthetic result, so it "
            "remains an explicit hold."
        ),
        {
            "wave8_fln_ageron_borders",
            "wave8_fln_chemins_1958",
            "wave8_fln_fsale_souk_ahras",
        },
    ),
    "hced-Kabylie1959-1": _hold(
        "hced-Kabylie1959-1",
        _canonical(
            "Operation Jumelles",
            1959,
            "22 July 1959-4 April 1960",
            "multi_month_counterinsurgency_sweep",
            date_precision="day_range",
        ),
        "multi_month_sweep_not_single_elo_event",
        "operation_level_attrition_claim_not_a_discrete_battle_outcome",
        (
            "ECPAD describes Operation Jumelles as a roughly eight-month effort "
            "using about 40,000 personnel to dismantle political, administrative, "
            "and military structures through repeated sweeps, patrols, searches, "
            "and engagements. HCED's Kabylie row cannot defensibly convert that "
            "aggregate operation into one tactical Elo result."
        ),
        {"wave8_fln_ecpad_jumelles"},
    ),
}

WAVE8_FLN_CONTRACT_IDS = frozenset(WAVE8_FLN_CONTRACTS)
WAVE8_FLN_HOLD_IDS = frozenset(WAVE8_FLN_HOLDS)
WAVE8_FLN_RESERVED_IDS = frozenset({*WAVE8_FLN_CONTRACT_IDS, *WAVE8_FLN_HOLD_IDS})
WAVE8_FLN_POINT_QUARANTINE_ADDITIONS = WAVE8_FLN_CONTRACT_IDS
WAVE8_FLN_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_FLN_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Souk-Ahras1958-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the Souk Ahras border battle and "
            "modern country but describe fighting across several nearby sectors; "
            "retain Algeria and withhold HCED's unexplained point."
        ),
        "evidence_refs": sorted(
            WAVE8_FLN_CONTRACTS["hced-Souk-Ahras1958-1"]["outcome_source_ids"]
        ),
    }
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_FLN_CONTRACTS,
        "entities": WAVE8_FLN_ENTITIES,
        "funnel": WAVE8_FLN_FUNNEL_AUDIT,
        "holds": WAVE8_FLN_HOLDS,
        "location_reasons": WAVE8_FLN_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_FLN_ROW_HASHES,
        "sources": WAVE8_FLN_SOURCES,
    }


def wave8_fln_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_FLN_FINAL_AUDIT_SIGNATURE = (
    "1e24533279bfe83a88bf62170f430f3507837e96b6195742d25d762e10b83966"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = {str(entity["id"]) for entity in WAVE8_FLN_ENTITIES}
    if len(source_ids) != len(WAVE8_FLN_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if entity_ids != {_FOURTH_REPUBLIC, _ALN}:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_FLN_CONTRACT_IDS & WAVE8_FLN_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_FLN_RESERVED_IDS != set(WAVE8_FLN_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_FLN_POINT_QUARANTINE_ADDITIONS != WAVE8_FLN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_FLN_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_FLN_LOCATION_QUARANTINE_REASONS) != WAVE8_FLN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    expected_windows = {
        _FOURTH_REPUBLIC: (1946, 1958),
        _ALN: (1954, 1962),
    }
    used_sources: set[str] = set()
    for entity in WAVE8_FLN_ENTITIES:
        entity_id = str(entity["id"])
        if entity["aliases"] or (
            entity["start_year"],
            entity["end_year"],
        ) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} identity boundary or alias drift")
        if normalize_label(entity["name"]) == _EXACT_LABEL:
            raise ValueError(f"{_LANE_NAME} generic FLN label opened")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity evidence order drift")
        used_sources.update(set(map(str, entity["source_ids"])) & source_ids)

    if WAVE8_FLN_CONTRACT_IDS != {"hced-Souk-Ahras1958-1"}:
        raise ValueError(f"{_LANE_NAME} promotion inventory drift")
    contract = WAVE8_FLN_CONTRACTS["hced-Souk-Ahras1958-1"]
    if (
        contract["disposition"] != "promote"
        or contract["result_type"] != "win"
        or contract["winner_side"] != 1
        or contract["source_outcome_override"]
        or contract["outcome_reversal"]
    ):
        raise ValueError(f"{_LANE_NAME} outcome orientation drift")
    if (
        contract["side_1_entity_ids"] != [_FOURTH_REPUBLIC]
        or contract["side_2_entity_ids"] != [_ALN]
    ):
        raise ValueError(f"{_LANE_NAME} exact actor drift")
    evidence = list(map(str, contract["evidence_refs"]))
    outcomes = list(map(str, contract["outcome_source_ids"]))
    if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
        raise ValueError(f"{_LANE_NAME} outcome evidence order drift")
    if not set(outcomes) <= set(evidence) or not set(evidence) <= source_ids:
        raise ValueError(f"{_LANE_NAME} outcome evidence closure failed")
    families = sorted(
        {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
    )
    if contract["outcome_source_family_ids"] != families or len(families) < 2:
        raise ValueError(f"{_LANE_NAME} outcome family drift")
    used_sources.update(evidence)

    expected_holds = {
        "hced-Algiers1956-1957-1": (
            "multi_episode_urban_campaign_not_single_elo_event",
            "multi_phase_urban_counterinsurgency_campaign",
        ),
        "hced-Frontier1958-1": (
            "campaign_envelope_contains_promoted_souk_ahras_battle",
            "multi_month_border_campaign_envelope",
        ),
        "hced-Kabylie1959-1": (
            "multi_month_sweep_not_single_elo_event",
            "multi_month_counterinsurgency_sweep",
        ),
    }
    for candidate_id, (category, granularity) in expected_holds.items():
        hold = WAVE8_FLN_HOLDS[candidate_id]
        if (
            hold["disposition"] != "hold"
            or hold["hold_category"] != category
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
            or hold["reviewed_granularity"] != granularity
        ):
            raise ValueError(f"{_LANE_NAME} hold disposition drift: {candidate_id}")
        hold_sources = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(hold_sources) or not set(hold_sources) <= source_ids:
            raise ValueError(f"{_LANE_NAME} hold evidence drift: {candidate_id}")
        used_sources.update(hold_sources)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_fln_audit_signature() != WAVE8_FLN_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_fln_queue_contracts(
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
    if exact_ids != WAVE8_FLN_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_FLN_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("year_low") != row.get("year_high") or row.get("year_best") != row.get(
            "year_low"
        ):
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if (
            row.get("side_1_raw") != "France"
            or row.get("side_2_raw") != "FLN"
            or row.get("winner_raw") != "France"
            or row.get("loser_raw") != "FLN"
        ):
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True:
            raise ValueError(f"{_LANE_NAME} complete-outcome guard changed: {candidate_id}")
        if row.get("massacre_raw") != "No":
            raise ValueError(f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_FLN_CONTRACTS,
        WAVE8_FLN_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_fln_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
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
        "rated_counterpart_entities": int(label.get("rated_counterpart_entities", -1)),
        "sole_blocker_events": int(label.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, label.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(label.get("unresolved_side_attempts", -1)),
        "zero_time_valid_candidates": int(
            label.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
        ),
    }
    if checks != WAVE8_FLN_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed: {checks}")
    return {
        "events_touched": checks["events_touched"],
        "sole_blocker_events": checks["sole_blocker_events"],
        "unresolved_side_attempts": checks["unresolved_side_attempts"],
        "zero_time_valid_candidates": checks["zero_time_valid_candidates"],
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "batyear"):
        try:
            if row.get(key) is not None:
                return int(row[key])
        except (TypeError, ValueError):
            pass
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


_SOUK_AHRAS_ALIASES = {
    "Battle of Souk Ahras",
    "Battle of Souk-Ahras",
    "Djebel el-Mouhadjene",
    "Souk Ahras",
    "Souk-Ahras",
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (1958, normalize_label(alias)) for alias in _SOUK_AHRAS_ALIASES
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_fln_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_fln_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_FLN_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_FLN_CONTRACT_IDS
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


def install_wave8_fln_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_FLN_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_fln_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_FLN_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_FLN_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_FLN_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_fln_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_fln_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_FLN_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_fln_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (*WAVE8_FLN_CONTRACTS.values(), *WAVE8_FLN_HOLDS.values())
            ).items()
        )
    )


def wave8_fln_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": len(WAVE8_FLN_HOLDS),
        "new_entities": len(WAVE8_FLN_ENTITIES),
        "new_sources": len(WAVE8_FLN_SOURCES),
        "newly_rated_events": len(WAVE8_FLN_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(WAVE8_FLN_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_FLN_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_FLN_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_fln_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_fln_counts(),
        "cohorts": wave8_fln_cohort_counts(),
        "final_audit_signature": WAVE8_FLN_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_FLN_CONTRACT_IDS),
        "hold_candidate_ids": sorted(WAVE8_FLN_HOLD_IDS),
    }


_validate_static()
