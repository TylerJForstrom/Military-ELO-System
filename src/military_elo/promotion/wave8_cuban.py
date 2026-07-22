"""Candidate-keyed audit of HCED's three ``Cuban Government`` rows.

The 1953 Moncada assault predates the organized 26th of July Movement, and
the 1957 Cienfuegos revolt joined dissident naval personnel with several
civilian opposition currents.  This lane therefore creates two alias-free,
event-bounded opponent identities instead of widening ``Cuban Rebels`` or
adding a generic ``Cuban Government`` alias.  Both fingerprinted engagements
are Republic of Cuba tactical wins.

The 1958 ``Sierra Maestra`` row stays on review hold.  Its broad campaign name
and raw ``El Jigue`` participant token do not identify whether HCED meant the
summer offensive as a whole or one constituent battle.  Its outcome remains
unknown and is never converted to a draw.  Wikidata's Moncada record is an
outcome-free discovery twin and can never originate a rating automatically.
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
    "WAVE8_CUBAN_CONTRACT_IDS",
    "WAVE8_CUBAN_CONTRACTS",
    "WAVE8_CUBAN_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_CUBAN_DISCOVERY_EXPECTED",
    "WAVE8_CUBAN_DISCOVERY_ROW_HASHES",
    "WAVE8_CUBAN_DISCOVERY_TWINS",
    "WAVE8_CUBAN_ENTITIES",
    "WAVE8_CUBAN_EXPECTED_CANDIDATE_IDS",
    "WAVE8_CUBAN_FINAL_AUDIT_SIGNATURE",
    "WAVE8_CUBAN_FUNNEL_AUDIT",
    "WAVE8_CUBAN_HOLD_IDS",
    "WAVE8_CUBAN_HOLDS",
    "WAVE8_CUBAN_INTEGRATION_DISPOSITIONS",
    "WAVE8_CUBAN_LOCATION_QUARANTINE_REASONS",
    "WAVE8_CUBAN_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_CUBAN_REQUIRED_EXISTING_ENTITIES",
    "WAVE8_CUBAN_RESERVED_IDS",
    "WAVE8_CUBAN_ROW_HASHES",
    "WAVE8_CUBAN_SOURCES",
    "install_wave8_cuban_entities",
    "install_wave8_cuban_sources",
    "promote_wave8_cuban_contracts",
    "validate_wave8_cuban_current_artifact_state",
    "validate_wave8_cuban_discovery_dispositions",
    "validate_wave8_cuban_existing_entities",
    "validate_wave8_cuban_funnel",
    "validate_wave8_cuban_integration_dispositions",
    "validate_wave8_cuban_queue_contracts",
    "wave8_cuban_audit_signature",
    "wave8_cuban_cohort_counts",
    "wave8_cuban_counts",
    "wave8_cuban_location_quarantine_additions",
    "wave8_cuban_metadata",
)


_LANE_NAME = "Wave 8 exact Cuban Revolution audit"
_MODULE_OWNER = "military_elo.promotion.wave8_cuban"
_EVENT_ID_PREFIX = "hced_wave8_cuban_"
_EXACT_LABEL = "cuban government"
_COHORT = "cuban_revolution_exact_rows_1953_1958"

_REPUBLIC_OF_CUBA = "clio_cu_cuba_rep_1_1905_9c789e65"
_JULY_26_MOVEMENT = "cuban_26_july_movement"
_MONCADA_ASSAULT_GROUP = "moncada_assault_group_1953"
_CIENFUEGOS_COALITION = "cienfuegos_naval_civilian_uprising_coalition_1957"


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


WAVE8_CUBAN_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_cuban_frus_moncada_1953",
        "Despatch From the Consulate at Santiago de Cuba to the Department of State",
        "https://history.state.gov/historicaldocuments/frus1958-60v06/d18",
        "Office of the Historian, U.S. Department of State",
        "edited_primary_diplomatic_document",
        "frus_cuba_1955_1960",
        [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    ),
    _source(
        "wave8_cuban_country_study_armed_forces",
        "Cuba: A Country Study — The Origins of the Revolutionary Armed Forces",
        (
            "https://www.marines.mil/Portals/1/Publications/"
            "Cuba%20Study_4.pdf?ver=2012-10-11-163311-187"
        ),
        "Federal Research Division, Library of Congress",
        "government_country_study",
        "library_of_congress_cuba_country_study",
        [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    ),
    _source(
        "wave8_cuban_frus_cienfuegos_1957",
        "Telegram From the Ambassador in Cuba to the Secretary of State",
        "https://history.state.gov/historicaldocuments/frus1955-57v06/d294",
        "Office of the Historian, U.S. Department of State",
        "edited_primary_diplomatic_document",
        "frus_cuba_1955_1960",
        [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    ),
    _source(
        "wave8_cuban_frus_summer_offensive_1958",
        "Military Causes for the Collapse of the Batista Regime",
        "https://history.state.gov/historicaldocuments/frus1958-60v06/d265",
        "Office of the Historian, U.S. Department of State",
        "edited_primary_diplomatic_document",
        "frus_cuba_1955_1960",
        [
            "identity_boundary_or_context_reference",
            "outcome_consistency_crosscheck",
        ],
    ),
    _source(
        "wave8_cuban_granma_el_jigue_1958",
        "En la batalla de El Jigüe la historia de la nación cubana comenzó a cambiar",
        (
            "https://www.granma.cu/granmad/secciones/"
            "60-aniversario-moncada/articulo-32.html"
        ),
        "Granma",
        "official_historical_feature",
        "granma_cuban_revolution_history",
        ["identity_boundary_or_context_reference"],
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_CUBAN_SOURCES}


WAVE8_CUBAN_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _MONCADA_ASSAULT_GROUP,
        "name": "Moncada assault group (1953)",
        "kind": "event_bounded_assault_group",
        "start_year": 1953,
        "end_year": 1953,
        "region": "Santiago de Cuba",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to Fidel Castro's armed group in the 26 July 1953 attacks "
            "on the Moncada and Carlos Manuel de Céspedes barracks. The organized "
            "26th of July Movement dates from 1955, so no rating is inherited by "
            "that movement, a generic Cuban Rebels label, later Rebel Army forces, "
            "or the post-1959 Cuban state."
        ),
        "source_ids": [
            "wave8_cuban_country_study_armed_forces",
            "wave8_cuban_frus_moncada_1953",
        ],
    },
    {
        "id": _CIENFUEGOS_COALITION,
        "name": "Cienfuegos naval–civilian uprising coalition (1957)",
        "kind": "event_bounded_naval_civilian_uprising_coalition",
        "start_year": 1957,
        "end_year": 1957,
        "region": "Cienfuegos, Cuba",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the dissident naval personnel and allied civilian "
            "opposition forces in the 5-6 September 1957 Cienfuegos revolt. No "
            "rating is inherited by the Cuban Navy, the 26th of July Movement, "
            "the Revolutionary Directorate, Auténtico organizations, civilians, "
            "or any later revolutionary government or armed force."
        ),
        "source_ids": [
            "wave8_cuban_country_study_armed_forces",
            "wave8_cuban_frus_cienfuegos_1957",
        ],
    },
)


WAVE8_CUBAN_REQUIRED_EXISTING_ENTITIES: dict[str, dict[str, Any]] = {
    _REPUBLIC_OF_CUBA: {
        "name": "Republic of Cuba",
        "kind": "republic",
        "start_year": 1905,
        "end_year": 1959,
        "aliases": ["Cuba"],
    },
    _JULY_26_MOVEMENT: {
        "name": "26th of July Movement",
        "kind": "revolutionary_movement",
        "start_year": 1955,
        "end_year": 1959,
        "aliases": [],
    },
}


WAVE8_CUBAN_ROW_HASHES: dict[str, str] = {
    "hced-Cienfuegos1957-1": (
        "4a8b96f2c126c62f26d8f664c08de4d77084f335481c856cae212b530c029747"
    ),
    "hced-Moncada1953-1": (
        "0cb81e3b5335b537b0b031141969aaaf087546ce143fc2c3f5ae17cea5ec02e1"
    ),
    "hced-Sierra Maestra1958-1": (
        "300074a1319c5f29274449bbbf77e52e9d187e052b90d270a229e75c5dab78aa"
    ),
}
WAVE8_CUBAN_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_CUBAN_ROW_HASHES)


WAVE8_CUBAN_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "22de611d12dccc8f96ecf5f8501eebe570302e1a4e5880bf2f226a99efdef4cf"
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
        "date_precision": "day",
        "date_text": date_text,
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


_EVENT_SOURCE_IDS: dict[str, tuple[str, ...]] = {
    "hced-Cienfuegos1957-1": (
        "wave8_cuban_country_study_armed_forces",
        "wave8_cuban_frus_cienfuegos_1957",
    ),
    "hced-Moncada1953-1": (
        "wave8_cuban_country_study_armed_forces",
        "wave8_cuban_frus_moncada_1953",
    ),
}

_EVENT_EVIDENCE_ROLES: dict[str, dict[str, list[str]]] = {
    "hced-Cienfuegos1957-1": {
        "wave8_cuban_country_study_armed_forces": [
            "exact_actor_coalition",
            "exact_date",
            "tactical_outcome_crosscheck",
        ],
        "wave8_cuban_frus_cienfuegos_1957": [
            "exact_date_range",
            "government_force_identity",
            "tactical_outcome",
        ],
    },
    "hced-Moncada1953-1": {
        "wave8_cuban_country_study_armed_forces": [
            "exact_actor_boundary",
            "exact_date",
            "tactical_outcome_crosscheck",
        ],
        "wave8_cuban_frus_moncada_1953": [
            "exact_assault_granularity",
            "exact_date",
            "tactical_outcome",
        ],
    },
}


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    opponent_id: str,
    audit_note: str,
) -> dict[str, Any]:
    outcomes = sorted(_EVENT_SOURCE_IDS[candidate_id])
    return {
        "raw_row_sha256": WAVE8_CUBAN_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "side_1_entity_ids": [_REPUBLIC_OF_CUBA],
        "side_2_entity_ids": [opponent_id],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "internal_rebellion",
        "confidence": 0.96,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "event_evidence_roles": {
            source_id: list(roles)
            for source_id, roles in sorted(
                _EVENT_EVIDENCE_ROLES[candidate_id].items()
            )
        },
        "date_source_ids": outcomes,
        "source_date_refinement": True,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_republic_and_event_bounded_opponent",
        "expected_scale_level": 1,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_CUBAN_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Moncada1953-1": _contract(
        "hced-Moncada1953-1",
        _canonical(
            "Attack on the Moncada Barracks",
            1953,
            "26 July 1953",
            "1953-07-26",
            "1953-07-26",
            "single_barracks_assault",
        ),
        _MONCADA_ASSAULT_GROUP,
        (
            "The diplomatic despatch and Library of Congress country study "
            "independently date the assault to 26 July and record its failure. "
            "The attackers are bounded to this assault because the organized "
            "26th of July Movement did not yet exist. Repression after capture "
            "is not converted into the engagement result."
        ),
    ),
    "hced-Cienfuegos1957-1": _contract(
        "hced-Cienfuegos1957-1",
        _canonical(
            "Cienfuegos uprising",
            1957,
            "5-6 September 1957",
            "1957-09-05",
            "1957-09-06",
            "single_naval_civilian_urban_uprising",
        ),
        _CIENFUEGOS_COALITION,
        (
            "The contemporary diplomatic record states that Batista's military "
            "quelled the 5-6 September anti-government attack, while the Library "
            "of Congress study independently records that 2,000 army troops "
            "successfully quashed the naval revolt. The mixed uprising coalition "
            "is not collapsed into the 26th of July Movement alone."
        ),
    ),
}


WAVE8_CUBAN_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Sierra Maestra1958-1": {
        "raw_row_sha256": WAVE8_CUBAN_ROW_HASHES[
            "hced-Sierra Maestra1958-1"
        ],
        "canonical_event": {
            "canonical_key": "sierra-maestra-operations:1958:1958",
            "date_precision": "year",
            "granularity": "campaign_umbrella_with_el_jigue_constituent_ambiguity",
            "name": "Sierra Maestra operations",
            "year_low": 1958,
            "year_high": 1958,
        },
        "cohort": _COHORT,
        "disposition": "hold",
        "hold_category": "campaign_umbrella_constituent_ambiguity",
        "reviewed_outcome": "unknown",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "side_1_entity_ids": [_JULY_26_MOVEMENT],
        "side_2_entity_ids": [_REPUBLIC_OF_CUBA],
        "evidence_refs": [
            "wave8_cuban_country_study_armed_forces",
            "wave8_cuban_frus_summer_offensive_1958",
            "wave8_cuban_granma_el_jigue_1958",
        ],
        "hold_reason": (
            "HCED names the Sierra Maestra campaign but also carries El Jigue as "
            "a raw participant token. The sources distinguish the broad summer "
            "offensive from the constituent Battle of El Jigüe, so this record "
            "cannot be assigned one defensible event boundary. No campaign or "
            "constituent outcome is inferred, and unknown is never a draw."
        ),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "review_hold_owner",
        },
    },
}


WAVE8_CUBAN_CONTRACT_IDS = frozenset(WAVE8_CUBAN_CONTRACTS)
WAVE8_CUBAN_HOLD_IDS = frozenset(WAVE8_CUBAN_HOLDS)
WAVE8_CUBAN_RESERVED_IDS = frozenset(
    {*WAVE8_CUBAN_CONTRACT_IDS, *WAVE8_CUBAN_HOLD_IDS}
)


# Both promoted rows carry reviewed city-level points and the source country's
# location assertion.  The hold emits nothing, so this lane adds no quarantine.
WAVE8_CUBAN_POINT_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_CUBAN_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_CUBAN_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {}


WAVE8_CUBAN_DISCOVERY_TWINS: dict[str, str] = {
    "hced-Moncada1953-1": "Q11211553",
}
WAVE8_CUBAN_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q11211553": (
        "29556145498096bc7e0694bf64a557a8f5af155aef1f466a8fd951602e7965f8"
    ),
}
WAVE8_CUBAN_DISCOVERY_EXPECTED: dict[str, dict[str, Any]] = {
    "Q11211553": {
        "date": "1953-07-26T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Attack on the Moncada Barracks",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [],
        "relationship": "exact_discovery_duplicate",
    },
}
WAVE8_CUBAN_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "Q11211553": {
        "source_dataset": "wikidata-battles",
        "disposition": "discovery_only_duplicate",
        "hced_candidate_id": "hced-Moncada1953-1",
        "outcome_disposition": "unknown_never_draw",
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_CUBAN_CONTRACTS,
        "discovery_expected": WAVE8_CUBAN_DISCOVERY_EXPECTED,
        "discovery_row_hashes": WAVE8_CUBAN_DISCOVERY_ROW_HASHES,
        "discovery_twins": WAVE8_CUBAN_DISCOVERY_TWINS,
        "entities": WAVE8_CUBAN_ENTITIES,
        "funnel": WAVE8_CUBAN_FUNNEL_AUDIT,
        "holds": WAVE8_CUBAN_HOLDS,
        "integration_dispositions": WAVE8_CUBAN_INTEGRATION_DISPOSITIONS,
        "location_reasons": WAVE8_CUBAN_LOCATION_QUARANTINE_REASONS,
        "required_existing_entities": WAVE8_CUBAN_REQUIRED_EXISTING_ENTITIES,
        "row_hashes": WAVE8_CUBAN_ROW_HASHES,
        "sources": WAVE8_CUBAN_SOURCES,
    }


def wave8_cuban_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_CUBAN_FINAL_AUDIT_SIGNATURE = (
    "d9f6174e7d01b50a77af029ede3150173c5bb874b2bc3148ff07dfb85f242ee8"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_CUBAN_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if {str(entity["id"]) for entity in WAVE8_CUBAN_ENTITIES} != {
        _MONCADA_ASSAULT_GROUP,
        _CIENFUEGOS_COALITION,
    }:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    for entity in WAVE8_CUBAN_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identities must remain alias-free")
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity is not event bounded")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity permits continuity inheritance")
        if not set(map(str, entity["source_ids"])) <= source_ids:
            raise ValueError(f"{_LANE_NAME} identity source closure drift")

    if WAVE8_CUBAN_RESERVED_IDS != WAVE8_CUBAN_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_CUBAN_CONTRACT_IDS & WAVE8_CUBAN_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if (len(WAVE8_CUBAN_CONTRACTS), len(WAVE8_CUBAN_HOLDS)) != (2, 1):
        raise ValueError(f"{_LANE_NAME} disposition count drift")
    if (
        WAVE8_CUBAN_POINT_QUARANTINE_ADDITIONS
        or WAVE8_CUBAN_COUNTRY_QUARANTINE_ADDITIONS
        or WAVE8_CUBAN_LOCATION_QUARANTINE_REASONS
    ):
        raise ValueError(f"{_LANE_NAME} location retention policy drift")

    expected_urls = {
        "wave8_cuban_country_study_armed_forces": (
            "https://www.marines.mil/Portals/1/Publications/"
            "Cuba%20Study_4.pdf?ver=2012-10-11-163311-187"
        ),
        "wave8_cuban_frus_cienfuegos_1957": (
            "https://history.state.gov/historicaldocuments/frus1955-57v06/d294"
        ),
        "wave8_cuban_frus_moncada_1953": (
            "https://history.state.gov/historicaldocuments/frus1958-60v06/d18"
        ),
        "wave8_cuban_frus_summer_offensive_1958": (
            "https://history.state.gov/historicaldocuments/frus1958-60v06/d265"
        ),
        "wave8_cuban_granma_el_jigue_1958": (
            "https://www.granma.cu/granmad/secciones/"
            "60-aniversario-moncada/articulo-32.html"
        ),
    }
    for source_id, source in _SOURCE_BY_ID.items():
        if source["url"] != expected_urls[source_id]:
            raise ValueError(f"{_LANE_NAME} canonical source URL drift: {source_id}")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source role order drift: {source_id}")

    expected_contracts = {
        "hced-Cienfuegos1957-1": (
            "Cienfuegos uprising",
            1957,
            "5-6 September 1957",
            "1957-09-05",
            "1957-09-06",
            "single_naval_civilian_urban_uprising",
            _CIENFUEGOS_COALITION,
        ),
        "hced-Moncada1953-1": (
            "Attack on the Moncada Barracks",
            1953,
            "26 July 1953",
            "1953-07-26",
            "1953-07-26",
            "single_barracks_assault",
            _MONCADA_ASSAULT_GROUP,
        ),
    }
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_CUBAN_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["side_1_entity_ids"] != [_REPUBLIC_OF_CUBA]
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or float(contract["confidence"]) != 0.96
            or int(contract["expected_scale_level"]) != 1
        ):
            raise ValueError(f"{_LANE_NAME} outcome disposition drift: {candidate_id}")
        expected = expected_contracts[candidate_id]
        canonical = contract["canonical_event"]
        name, year, date_text, start_date, end_date, granularity, opponent = expected
        if (
            contract["side_2_entity_ids"] != [opponent]
            or canonical["canonical_key"] != f"{_slug(name)}:{year}:{year}"
            or canonical["name"] != name
            or canonical["date_precision"] != "day"
            or canonical["date_text"] != date_text
            or (canonical["start_date"], canonical["end_date"])
            != (start_date, end_date)
            or (canonical["year_low"], canonical["year_high"]) != (year, year)
            or canonical["granularity"] != granularity
        ):
            raise ValueError(f"{_LANE_NAME} actor/date/granularity drift: {candidate_id}")

        outcomes = list(map(str, contract["outcome_source_ids"]))
        evidence = list(map(str, contract["evidence_refs"]))
        date_sources = list(map(str, contract["date_source_ids"]))
        expected_sources = sorted(_EVENT_SOURCE_IDS[candidate_id])
        expected_families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if (
            outcomes != expected_sources
            or evidence != outcomes
            or date_sources != outcomes
            or contract["outcome_source_family_ids"] != expected_families
            or len(expected_families) != 2
            or contract["source_date_refinement"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} source closure drift: {candidate_id}")
        if any("outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"] for source_id in outcomes):
            raise ValueError(f"{_LANE_NAME} non-outcome source used for result")
        role_map = contract["event_evidence_roles"]
        if set(role_map) != set(outcomes):
            raise ValueError(f"{_LANE_NAME} event source-role closure drift")
        for source_id, roles in role_map.items():
            if not _is_sorted_unique(roles) or not roles:
                raise ValueError(
                    f"{_LANE_NAME} event-specific role drift: {candidate_id}/{source_id}"
                )
        used_sources.update(outcomes)

    hold = WAVE8_CUBAN_HOLDS["hced-Sierra Maestra1958-1"]
    if (
        hold["disposition"] != "hold"
        or hold["hold_category"] != "campaign_umbrella_constituent_ambiguity"
        or hold["reviewed_outcome"] != "unknown"
        or hold["result_type"] != "unknown"
        or hold["unknown_is_never_draw"] is not True
        or "winner_side" in hold
        or hold["side_1_entity_ids"] != [_JULY_26_MOVEMENT]
        or hold["side_2_entity_ids"] != [_REPUBLIC_OF_CUBA]
    ):
        raise ValueError(f"{_LANE_NAME} unknown hold drift")
    hold_sources = list(map(str, hold["evidence_refs"]))
    if not _is_sorted_unique(hold_sources) or not set(hold_sources) <= source_ids:
        raise ValueError(f"{_LANE_NAME} hold evidence closure drift")
    if "El Jigüe" not in hold["hold_reason"] or "never a draw" not in hold["hold_reason"]:
        raise ValueError(f"{_LANE_NAME} campaign ambiguity guard drift")
    used_sources.update(hold_sources)
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if set(WAVE8_CUBAN_DISCOVERY_TWINS) != {"hced-Moncada1953-1"}:
        raise ValueError(f"{_LANE_NAME} discovery owner drift")
    if set(WAVE8_CUBAN_DISCOVERY_TWINS.values()) != set(
        WAVE8_CUBAN_DISCOVERY_ROW_HASHES
    ) or set(WAVE8_CUBAN_DISCOVERY_EXPECTED) != set(
        WAVE8_CUBAN_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} discovery inventory drift")
    if any(
        item["outcome_disposition"] != "unknown_never_draw"
        for item in WAVE8_CUBAN_DISCOVERY_EXPECTED.values()
    ):
        raise ValueError(f"{_LANE_NAME} discovery outcome guard drift")
    if set(WAVE8_CUBAN_INTEGRATION_DISPOSITIONS) != set(
        WAVE8_CUBAN_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} integration disposition drift")
    if wave8_cuban_audit_signature() != WAVE8_CUBAN_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_cuban_existing_entities(
    release_entities: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    for entity_id, expected in WAVE8_CUBAN_REQUIRED_EXISTING_ENTITIES.items():
        entity = release_entities.get(entity_id)
        if entity is None:
            raise ValueError(f"{_LANE_NAME} missing existing identity {entity_id}")
        projection = {key: entity.get(key) for key in expected}
        if projection != expected:
            raise ValueError(
                f"{_LANE_NAME} existing identity drift for {entity_id}: {projection}"
            )
    all_aliases = {
        normalize_label(alias)
        for entity in release_entities.values()
        for alias in entity.get("aliases", []) or []
    }
    if _EXACT_LABEL in all_aliases:
        raise ValueError(f"{_LANE_NAME} generic Cuban Government alias was introduced")
    return {
        "required_existing_entities": len(WAVE8_CUBAN_REQUIRED_EXISTING_ENTITIES)
    }


def validate_wave8_cuban_queue_contracts(
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
    if exact_ids != WAVE8_CUBAN_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    expected = {
        "hced-Cienfuegos1957-1": (
            "Cienfuegos",
            1957,
            "Cuban Government",
            "Cuban Rebels",
            "Cuban Government",
            "Cuban Rebels",
            ["San Roman"],
            "1",
        ),
        "hced-Moncada1953-1": (
            "Moncada",
            1953,
            "Cuban Government",
            "Cuban Rebels",
            "Cuban Government",
            "Cuban Rebels",
            ["Cuban", "Santiago"],
            "1",
        ),
        "hced-Sierra Maestra1958-1": (
            "Sierra Maestra",
            1958,
            "Cuban Rebels",
            "Cuban Government",
            "Cuban Rebels",
            "Cuban Government",
            ["Cuban", "El   Jigue"],
            "2",
        ),
    }
    for candidate_id, expected_hash in WAVE8_CUBAN_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        name, year, side_1, side_2, winner, loser, tokens, scale = expected[candidate_id]
        if (
            row.get("name") != name
            or (row.get("year_low"), row.get("year_best"), row.get("year_high"))
            != (year, year, year)
            or row.get("side_1_raw") != side_1
            or row.get("side_2_raw") != side_2
            or row.get("winner_raw") != winner
            or row.get("loser_raw") != loser
            or row.get("participants_raw") != tokens
            or row.get("scale_raw") != scale
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("do_not_rate_automatically") is not True
            or row.get("duplicate_source_id") is not False
        ):
            raise ValueError(f"{_LANE_NAME} locked source semantics changed: {candidate_id}")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_CUBAN_CONTRACTS,
        WAVE8_CUBAN_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_cuban_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    rows = [row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL]
    if len(rows) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    row = rows[0]
    actual = {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "failure_cases": {
            key: int(row.get("failure_cases", {}).get(key, -1))
            for key in WAVE8_CUBAN_FUNNEL_AUDIT["failure_cases"]
        },
        "label": str(row.get("label")),
        "rated_counterpart_entities": int(row.get("rated_counterpart_entities", -1)),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(map(str, row.get("time_valid_candidate_ids", []))),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
    }
    if actual != WAVE8_CUBAN_FUNNEL_AUDIT:
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


def validate_wave8_cuban_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in WAVE8_CUBAN_DISCOVERY_ROW_HASHES.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} discovery row {candidate_id} expected once, found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}")
        expected = WAVE8_CUBAN_DISCOVERY_EXPECTED[candidate_id]
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
            raise ValueError(f"{_LANE_NAME} discovery non-rating guard changed")
    return {
        "discovery_nonrating_records": len(WAVE8_CUBAN_DISCOVERY_ROW_HASHES),
        "discovery_promotions": 0,
        "unknown_never_draw_rows": len(WAVE8_CUBAN_DISCOVERY_ROW_HASHES),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "start_year", "year_start", "batyear"):
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
    if isinstance(aliases, str):
        values.append(aliases)
    else:
        values.extend(aliases)
    return {normalize_label(value) for value in values if normalize_label(value)}


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Cienfuegos1957-1": {
        "Cienfuegos uprising",
        "Cienfuegos naval revolt",
        "Cienfuegos revolt",
        "Cienfuegos",
    },
    "hced-Moncada1953-1": {
        "Attack on the Moncada Barracks",
        "Moncada Barracks",
        "Moncada",
    },
    "hced-Sierra Maestra1958-1": {
        "Battle of El Jigue",
        "Battle of El Jigüe",
        "El Jigue",
        "El Jigüe",
        "Operation Verano",
        "Sierra Maestra",
        "Sierra Maestra operations",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(
            (
                WAVE8_CUBAN_CONTRACTS.get(candidate_id)
                or WAVE8_CUBAN_HOLDS[candidate_id]
            )["canonical_event"]["year_low"]
        ),
        normalize_label(alias),
    )
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
)
_CUBAN_EVENT_NAMES = frozenset(
    normalize_label(alias) for aliases in _EVENT_ALIASES.values() for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    matched_names = _row_names(row) & _CUBAN_EVENT_NAMES
    if not matched_names:
        return False
    year = _row_year(row)
    if year is None:
        return True
    return any((year, name) in _DUPLICATE_MATCH_KEYS for name in matched_names)


def validate_wave8_cuban_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwd_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Prove that no unreviewed HCED/IWD/IWBD/release twin can double-rate."""

    validate_wave8_cuban_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_CUBAN_RESERVED_IDS
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
        if event.get("hced_candidate_id") in WAVE8_CUBAN_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    if owned:
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        if owned_ids != WAVE8_CUBAN_CONTRACT_IDS or len(owned) != len(owned_ids):
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
        "discovery_nonrating_dispositions": len(WAVE8_CUBAN_INTEGRATION_DISPOSITIONS),
        "existing_release_owned_events": len(owned),
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwd_probable_twins": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_cuban_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_CUBAN_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_cuban_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_CUBAN_SOURCES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_cuban_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_cuban_queue_contracts(hced_rows)
    validate_wave8_cuban_existing_entities(release_entities)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_CUBAN_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )


def _entity_covers(entity: Mapping[str, Any], low: int, high: int) -> bool:
    start = entity.get("start_year")
    end = entity.get("end_year")
    return (
        start is not None
        and int(start) <= low
        and (end is None or int(end) >= high)
    )


def validate_wave8_cuban_current_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Require Cuban lane entities, sources, and events to be absent or complete."""

    _validate_static()
    entity_by_id = {str(entity.get("id")): entity for entity in release_entities}
    validate_wave8_cuban_existing_entities(entity_by_id)
    source_by_id = {str(source.get("id")): source for source in release_sources}
    events = list(release_events)
    expected_entity_ids = {str(entity["id"]) for entity in WAVE8_CUBAN_ENTITIES}
    expected_source_ids = set(_SOURCE_BY_ID)
    entity_overlap = expected_entity_ids & set(entity_by_id)
    source_overlap = expected_source_ids & set(source_by_id)
    owned = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_CUBAN_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    any_present = bool(entity_overlap or source_overlap or owned)
    if not any_present:
        return {
            "artifact_state": "absent",
            "installed_entities": 0,
            "installed_sources": 0,
            "promoted_events": 0,
        }
    if (
        entity_overlap != expected_entity_ids
        or source_overlap != expected_source_ids
        or len(owned) != len(WAVE8_CUBAN_CONTRACT_IDS)
    ):
        raise ValueError(f"{_LANE_NAME} current release artifacts are partial")
    for entity in WAVE8_CUBAN_ENTITIES:
        if entity_by_id[str(entity["id"])] != entity:
            raise ValueError(f"{_LANE_NAME} current entity drift: {entity['id']}")
    for source_id in expected_source_ids:
        if source_by_id[source_id] != _SOURCE_BY_ID[source_id]:
            raise ValueError(f"{_LANE_NAME} current source drift: {source_id}")

    by_candidate = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_candidate) != WAVE8_CUBAN_CONTRACT_IDS or len(owned) != len(by_candidate):
        raise ValueError(f"{_LANE_NAME} current release candidate inventory changed")
    expected_locations = {
        "hced-Cienfuegos1957-1": [-80.4437781, 22.1599753],
        "hced-Moncada1953-1": [-75.8189458, 20.02586],
    }
    for candidate_id, contract in WAVE8_CUBAN_CONTRACTS.items():
        event = by_candidate[candidate_id]
        canonical = contract["canonical_event"]
        expected_id = f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        if (
            event.get("id") != expected_id
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year"))
            != (canonical["year_low"], canonical["year_high"])
            or event.get("event_type") != "engagement"
            or event.get("date_precision") != "day"
            or event.get("reviewed_granularity") != canonical["granularity"]
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids")
            != contract["outcome_source_family_ids"]
            or float(event.get("confidence", -1.0)) != float(contract["confidence"])
        ):
            raise ValueError(f"{_LANE_NAME} current release event drift: {candidate_id}")
        expected_participants = expected_exact_hced_win_participants(
            contract["side_1_entity_ids"],
            contract["side_2_entity_ids"],
            confidence=float(contract["confidence"]),
            scale_level=int(contract["expected_scale_level"]),
            lane_name=_LANE_NAME,
        )
        if event.get("participants") != expected_participants:
            raise ValueError(f"{_LANE_NAME} current participant drift: {candidate_id}")
        if (
            event.get("geometry")
            != {"type": "Point", "coordinates": expected_locations[candidate_id]}
            or event.get("modern_location_country") != "Cuba"
            or "location_provenance" not in event
        ):
            raise ValueError(f"{_LANE_NAME} current location drift: {candidate_id}")

    return {
        "artifact_state": "integrated",
        "installed_entities": len(entity_overlap),
        "installed_sources": len(source_overlap),
        "promoted_events": len(owned),
    }


def wave8_cuban_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (*WAVE8_CUBAN_CONTRACTS.values(), *WAVE8_CUBAN_HOLDS.values())
            ).items()
        )
    )


def wave8_cuban_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "discovery_nonrating_records": len(WAVE8_CUBAN_DISCOVERY_ROW_HASHES),
        "holds": len(WAVE8_CUBAN_HOLDS),
        "integration_dispositions": len(WAVE8_CUBAN_INTEGRATION_DISPOSITIONS),
        "new_entities": len(WAVE8_CUBAN_ENTITIES),
        "new_sources": len(WAVE8_CUBAN_SOURCES),
        "newly_rated_events": len(WAVE8_CUBAN_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": 0,
        "promotion_contracts": len(WAVE8_CUBAN_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_CUBAN_RESERVED_IDS),
        "terminal_exclusions": 0,
        "unknown_discovery_outcomes": len(WAVE8_CUBAN_DISCOVERY_ROW_HASHES),
    }


def wave8_cuban_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_CUBAN_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_CUBAN_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_cuban_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_cuban_counts(),
        "cohorts": wave8_cuban_cohort_counts(),
        "discovery_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_CUBAN_INTEGRATION_DISPOSITIONS.items()
            )
        ],
        "final_audit_signature": WAVE8_CUBAN_FINAL_AUDIT_SIGNATURE,
        "hold_candidate_ids": sorted(WAVE8_CUBAN_HOLD_IDS),
        "promoted_candidate_ids": sorted(WAVE8_CUBAN_CONTRACT_IDS),
    }


_validate_static()
