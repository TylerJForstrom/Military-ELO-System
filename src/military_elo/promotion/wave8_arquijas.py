"""Fail-closed exact-candidate audit of HCED's two Arquijas rows.

The lane rates only the First and Second Battles of Arquijas in the First
Carlist War.  Auñamendi/Eusko Ikaskuntza and Julio Albi de la Cuesta's
official Spanish Ministry of Defence history independently support the
bounded tactical results.  The contracts reuse the existing, conflict-bounded
Carlist and Isabeline identities and add no entity, alias, resolver rule, or
identity window.

Two Wikidata records are pinned as discovery-only twins.  The second has no
encoded winner: that absence remains unknown and is never converted to a draw.
Six nearby HCED rows are separately fingerprinted so an unrelated use of
``Liberals``, a distinct battle, or a hold owned by another exact lane cannot
be absorbed silently.
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
    "WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS",
    "WAVE8_ARQUIJAS_ALBI_DOI",
    "WAVE8_ARQUIJAS_CONTRACT_IDS",
    "WAVE8_ARQUIJAS_CONTRACTS",
    "WAVE8_ARQUIJAS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ARQUIJAS_DISCOVERY_EXPECTED",
    "WAVE8_ARQUIJAS_DISCOVERY_ROW_HASHES",
    "WAVE8_ARQUIJAS_DISCOVERY_TWINS",
    "WAVE8_ARQUIJAS_ENTITIES",
    "WAVE8_ARQUIJAS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ARQUIJAS_FUNNEL_AUDIT",
    "WAVE8_ARQUIJAS_HOLDS",
    "WAVE8_ARQUIJAS_INTEGRATION_DISPOSITIONS",
    "WAVE8_ARQUIJAS_LABEL_DISPOSITION_IDS",
    "WAVE8_ARQUIJAS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_ARQUIJAS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ARQUIJAS_RESERVED_IDS",
    "WAVE8_ARQUIJAS_ROW_HASHES",
    "WAVE8_ARQUIJAS_SOURCES",
    "install_wave8_arquijas_entities",
    "install_wave8_arquijas_sources",
    "promote_wave8_arquijas_contracts",
    "validate_wave8_arquijas_current_artifact_state",
    "validate_wave8_arquijas_discovery_dispositions",
    "validate_wave8_arquijas_funnel",
    "validate_wave8_arquijas_integration_dispositions",
    "validate_wave8_arquijas_queue_contracts",
    "wave8_arquijas_audit_signature",
    "wave8_arquijas_cohort_counts",
    "wave8_arquijas_counts",
    "wave8_arquijas_metadata",
)


_LANE_NAME = "Wave 8 exact Arquijas audit"
_MODULE_OWNER = "military_elo.promotion.wave8_arquijas"
_EVENT_ID_PREFIX = "hced_wave8_arquijas_"
_EXACT_LABEL = "liberals"
_COHORT = "first_carlist_war_arquijas_1834_1835"

_CARLIST_FORCES = "carlist_army_first_war"
_ISABELINE_FORCES = "isabeline_government_forces_first_carlist_war"


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
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    }


WAVE8_ARQUIJAS_ALBI_DOI = "https://doi.org/10.55553/504jnk066201"

WAVE8_ARQUIJAS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_arquijas_aunamendi_battles",
        "Batallas del Puente de Arquijas",
        (
            "https://aunamendi.eusko-ikaskuntza.eus/es/"
            "batallas-del-puente-de-arquijas/ar-4511/"
        ),
        "Auñamendi Eusko Entziklopedia / Eusko Ikaskuntza",
        "scholarly_regional_encyclopedia",
        "aunamendi_arquijas_battles",
    ),
    _source(
        "wave8_arquijas_albi_first_carlist_war_north",
        (
            "Julio Albi de la Cuesta, La Primera Guerra Carlista en el Norte "
            "(DOI 10.55553/504jnk066201)"
        ),
        (
            "https://publicaciones.defensa.gob.es/media/downloadable/files/"
            "links/r/h/rhm_extra_ii_2022_.pdf"
        ),
        "Ministerio de Defensa de España, Revista de Historia Militar",
        "official_peer_reviewed_military_history",
        "albi_first_carlist_war_north_2022",
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_ARQUIJAS_SOURCES}


# Both conflict-bounded participants already exist.  Keeping this fixture
# empty is a mechanical guarantee that the lane creates no identity or alias.
WAVE8_ARQUIJAS_ENTITIES: tuple[dict[str, Any], ...] = ()


WAVE8_ARQUIJAS_ROW_HASHES: dict[str, str] = {
    "hced-Arquijas1834-1": (
        "f8bafb6de9ca178ded97f44a16da4a9c0cc96a8cb1982f74da8ee49536ad3c11"
    ),
    "hced-Arquijas1835-1": (
        "89b168b4119b2c20de6cf8db9302b2e287afec914aed3dbab6218ab0a4b02794"
    ),
}


WAVE8_ARQUIJAS_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "db658445487517332b3cddadcac30d7b320d38d9c38823cfab77e540c9de99f0"
    ),
    "events_touched": 4,
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 4,
    },
    "label": _EXACT_LABEL,
    "rated_counterpart_entities": 1,
    "sole_blocker_events": 2,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 4,
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    exact_date: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "day",
        "date_text": date_text,
        "end_date": exact_date,
        "granularity": "single_battle_in_the_first_carlist_war",
        "name": name,
        "start_date": exact_date,
        "year_high": year,
        "year_low": year,
    }


_EVENT_EVIDENCE_ROLES: dict[str, list[str]] = {
    "wave8_arquijas_albi_first_carlist_war_north": [
        "competing_claims_context_for_first_battle",
        "exact_battle_date_crosscheck",
        "failed_attack_and_withdrawal_or_repulse",
        "independent_tactical_outcome_crosscheck",
    ],
    "wave8_arquijas_aunamendi_battles": [
        "exact_battle_date",
        "exact_belligerents",
        "single_battle_granularity",
        "tactical_outcome",
    ],
}


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(_SOURCE_BY_ID)
    return {
        "raw_row_sha256": WAVE8_ARQUIJAS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "side_1_entity_ids": [_CARLIST_FORCES],
        "side_2_entity_ids": [_ISABELINE_FORCES],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "civil_war",
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
            source_id: list(roles)
            for source_id, roles in sorted(_EVENT_EVIDENCE_ROLES.items())
        },
        "date_source_ids": outcomes,
        "source_date_refinement": True,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_exact_first_carlist_war_factions",
        "expected_scale_level": 2,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_ARQUIJAS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Arquijas1834-1": _contract(
        "hced-Arquijas1834-1",
        _canonical(
            "First Battle of Arquijas",
            1834,
            "15 December 1834",
            "1834-12-15",
        ),
        (
            "Auñamendi records Zumalacárregui's Carlists driving back the "
            "government forces on 15 December. Albi independently finds that "
            "Córdova could not force the defended position and withdrew while "
            "also documenting competing public victory claims. The contract "
            "therefore rates only the bounded Carlist defensive tactical win."
        ),
        confidence=0.90,
    ),
    "hced-Arquijas1835-1": _contract(
        "hced-Arquijas1835-1",
        _canonical(
            "Second Battle of Arquijas",
            1835,
            "5 February 1835",
            "1835-02-05",
        ),
        (
            "Auñamendi records Zumalacárregui again repelling Lorenzo's troops "
            "on 5 February; Albi independently describes the Lorenzo-Oráa "
            "operation against the Carlist position as a failure. Only that "
            "single tactical repulse is rated."
        ),
        confidence=0.95,
    ),
}


WAVE8_ARQUIJAS_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_ARQUIJAS_CONTRACT_IDS = frozenset(WAVE8_ARQUIJAS_CONTRACTS)
WAVE8_ARQUIJAS_RESERVED_IDS = WAVE8_ARQUIJAS_CONTRACT_IDS


# These records define the exact-label and nearby-event boundaries but are not
# owned by this lane.  Gatazo and Lircay prove that ``Liberals`` cannot become
# a broad alias; Artaza and Asarta remain holds in the Spanish-Liberals lane.
WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Artaza1834-1": {
        "raw_row_sha256": (
            "cd81f724365721250146a3c770797d27784a79b18a9381d3e770cf739db1dc79"
        ),
        "disposition": "external_lane_hold",
        "relationship": "different_first_carlist_war_action_with_bad_locked_year",
        "owner_module": "military_elo.promotion.wave8_spanish_liberals",
        "reason": (
            "Artaza remains the Spanish-Liberals lane's hold because its locked "
            "1834 year conflicts with the independently attested 1835 action."
        ),
    },
    "hced-Asarta1833-1": {
        "raw_row_sha256": (
            "bd305efe2efa6c551c7c6950bac089f478c4f689a6acae330e0e0d458ac07ddc"
        ),
        "disposition": "external_lane_hold",
        "relationship": "different_first_carlist_war_action_with_outcome_conflict",
        "owner_module": "military_elo.promotion.wave8_spanish_liberals",
        "reason": (
            "Asarta remains the Spanish-Liberals lane's hold because the locked "
            "Carlist winner conflicts with the reviewed Liberal tactical win."
        ),
    },
    "hced-Gatazo1895-1": {
        "raw_row_sha256": (
            "bec2c4765349f1ce17583376e2a18ad6db288ecf00b1b8e6a27ae06d34890596"
        ),
        "disposition": "adjacent_label_hold_not_owned",
        "relationship": "unrelated_ecuadorian_liberal_and_conservative_factions",
        "reason": (
            "Gatazo's Liberals and Conservatives are Ecuadorian civil-war "
            "formations; neither may inherit a First Carlist War identity."
        ),
    },
    "hced-Lircay1830-1": {
        "raw_row_sha256": (
            "dcdfed7c7f4dcec0abe1e4068fa1236ea13a505ba712f91f3610a948bc45c02b"
        ),
        "disposition": "adjacent_label_hold_not_owned",
        "relationship": "unrelated_chilean_liberal_and_conservative_factions",
        "reason": (
            "Lircay's Liberals and Conservatives are Chilean civil-war "
            "formations and predate the conflict-bounded Isabeline identity."
        ),
    },
    "hced-Mendaza1834-1": {
        "raw_row_sha256": (
            "34a724ced4b306041e69198c56605ac7d2f5a57190e5f41806f39f24792c7f02"
        ),
        "disposition": "adjacent_distinct_event_not_owned",
        "relationship": "distinct_battle_three_days_before_first_arquijas",
        "reason": (
            "Mendaza is the separate 12 December battle. Its noisy participant "
            "context mentions Arquijas, but its unresolved label is Cristinos."
        ),
    },
    "hced-Ormaiztegui1835-1": {
        "raw_row_sha256": (
            "cf9aaf84b0c5c98903a75a1fcf6ba8e8d3eff276cb2187c3478455ea8ec2147a"
        ),
        "disposition": "adjacent_distinct_event_not_owned",
        "relationship": "different_first_carlist_war_battle_with_cristinos_label",
        "reason": (
            "Ormaiztegui is a distinct battle whose participant context mentions "
            "Arquijas; it stays staged under its unresolved Cristinos identity."
        ),
    },
}

WAVE8_ARQUIJAS_LABEL_DISPOSITION_IDS = frozenset(
    {
        *WAVE8_ARQUIJAS_CONTRACT_IDS,
        "hced-Gatazo1895-1",
        "hced-Lircay1830-1",
    }
)


# Wikidata supplies exact dates and, for Q3755395, a consistent winner, but
# remains discovery-only.  Q12254001 has no winner and is explicitly unknown.
WAVE8_ARQUIJAS_DISCOVERY_TWINS: dict[str, str] = {
    "hced-Arquijas1834-1": "Q3755395",
    "hced-Arquijas1835-1": "Q12254001",
}
WAVE8_ARQUIJAS_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q12254001": (
        "6a066f59c78d6b04f454f02b2791968198d4d0e3557a54f69915470d0cdf1bd5"
    ),
    "Q3755395": (
        "af2321bf2edf2983cf323707e3bb22108702308587e28edede473684eed94071"
    ),
}
WAVE8_ARQUIJAS_DISCOVERY_EXPECTED: dict[str, dict[str, Any]] = {
    "Q12254001": {
        "date": "1835-02-05T00:00:00Z",
        "name": "Second Battle of Arquijas",
        "winner_labels": [],
        "outcome_disposition": "unknown_never_draw",
    },
    "Q3755395": {
        "date": "1834-12-15T00:00:00Z",
        "name": "First Battle of Arquijas",
        "winner_labels": ["Carlist army"],
        "outcome_disposition": "consistent_discovery_only_winner",
    },
}


WAVE8_ARQUIJAS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS,
    **{
        discovery_id: {
            "source_dataset": "wikidata-battles",
            "disposition": "discovery_only_duplicate",
            "hced_candidate_id": hced_id,
            "outcome_disposition": WAVE8_ARQUIJAS_DISCOVERY_EXPECTED[
                discovery_id
            ]["outcome_disposition"],
        }
        for hced_id, discovery_id in sorted(WAVE8_ARQUIJAS_DISCOVERY_TWINS.items())
    },
}


WAVE8_ARQUIJAS_POINT_QUARANTINE_ADDITIONS = WAVE8_ARQUIJAS_CONTRACT_IDS
WAVE8_ARQUIJAS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_ARQUIJAS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the Ega bridge-area battle and "
            "Spain but do not independently validate HCED's exact coordinate. "
            "Retain modern country and provenance; withhold the point."
        ),
        "evidence_refs": sorted(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_ARQUIJAS_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_hced_dispositions": WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS,
        "albi_doi": WAVE8_ARQUIJAS_ALBI_DOI,
        "contracts": WAVE8_ARQUIJAS_CONTRACTS,
        "discovery_expected": WAVE8_ARQUIJAS_DISCOVERY_EXPECTED,
        "discovery_row_hashes": WAVE8_ARQUIJAS_DISCOVERY_ROW_HASHES,
        "discovery_twins": WAVE8_ARQUIJAS_DISCOVERY_TWINS,
        "entities": WAVE8_ARQUIJAS_ENTITIES,
        "funnel": WAVE8_ARQUIJAS_FUNNEL_AUDIT,
        "holds": WAVE8_ARQUIJAS_HOLDS,
        "location_reasons": WAVE8_ARQUIJAS_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_ARQUIJAS_ROW_HASHES,
        "sources": WAVE8_ARQUIJAS_SOURCES,
    }


def wave8_arquijas_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_ARQUIJAS_FINAL_AUDIT_SIGNATURE = (
    "7ad64729af51fc9604d00a9dccbe9eaf50c80e84cf9a47aec7c77fd3011134f9"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_ARQUIJAS_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if WAVE8_ARQUIJAS_ENTITIES:
        raise ValueError(f"{_LANE_NAME} must not create identities")
    if WAVE8_ARQUIJAS_HOLDS:
        raise ValueError(f"{_LANE_NAME} exact inventory unexpectedly contains a hold")
    if WAVE8_ARQUIJAS_RESERVED_IDS != set(WAVE8_ARQUIJAS_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_ARQUIJAS_CONTRACT_IDS & set(
        WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} promotion/adjacent overlap")
    if WAVE8_ARQUIJAS_LABEL_DISPOSITION_IDS != {
        *WAVE8_ARQUIJAS_CONTRACT_IDS,
        "hced-Gatazo1895-1",
        "hced-Lircay1830-1",
    }:
        raise ValueError(f"{_LANE_NAME} exact-label boundary drift")
    if (
        WAVE8_ARQUIJAS_POINT_QUARANTINE_ADDITIONS
        != WAVE8_ARQUIJAS_CONTRACT_IDS
        or WAVE8_ARQUIJAS_COUNTRY_QUARANTINE_ADDITIONS
        or set(WAVE8_ARQUIJAS_LOCATION_QUARANTINE_REASONS)
        != WAVE8_ARQUIJAS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location policy drift")

    expected_urls = {
        "wave8_arquijas_albi_first_carlist_war_north": (
            "https://publicaciones.defensa.gob.es/media/downloadable/files/"
            "links/r/h/rhm_extra_ii_2022_.pdf"
        ),
        "wave8_arquijas_aunamendi_battles": (
            "https://aunamendi.eusko-ikaskuntza.eus/es/"
            "batallas-del-puente-de-arquijas/ar-4511/"
        ),
    }
    if WAVE8_ARQUIJAS_ALBI_DOI != "https://doi.org/10.55553/504jnk066201":
        raise ValueError(f"{_LANE_NAME} Albi DOI drift")
    for source_id, source in _SOURCE_BY_ID.items():
        if source["url"] != expected_urls[source_id]:
            raise ValueError(f"{_LANE_NAME} canonical source URL drift: {source_id}")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source role order drift: {source_id}")
        if "outcome" not in source["evidence_roles"]:
            raise ValueError(f"{_LANE_NAME} non-outcome source used for result")

    expected_dates = {
        "hced-Arquijas1834-1": (
            "First Battle of Arquijas",
            1834,
            "15 December 1834",
            "1834-12-15",
            0.90,
        ),
        "hced-Arquijas1835-1": (
            "Second Battle of Arquijas",
            1835,
            "5 February 1835",
            "1835-02-05",
            0.95,
        ),
    }
    expected_families = sorted(
        str(source["source_family_id"]) for source in WAVE8_ARQUIJAS_SOURCES
    )
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_ARQUIJAS_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome disposition drift: {candidate_id}")
        if (
            contract["side_1_entity_ids"],
            contract["side_2_entity_ids"],
        ) != ([_CARLIST_FORCES], [_ISABELINE_FORCES]):
            raise ValueError(f"{_LANE_NAME} exact actor drift: {candidate_id}")

        canonical = contract["canonical_event"]
        name, year, date_text, exact_date, confidence = expected_dates[candidate_id]
        expected_key = f"{_slug(name)}:{year}:{year}"
        if (
            canonical["canonical_key"] != expected_key
            or canonical["name"] != name
            or canonical["date_precision"] != "day"
            or canonical["granularity"]
            != "single_battle_in_the_first_carlist_war"
            or (canonical["year_low"], canonical["year_high"]) != (year, year)
            or canonical["date_text"] != date_text
            or (canonical["start_date"], canonical["end_date"])
            != (exact_date, exact_date)
            or float(contract["confidence"]) != confidence
            or int(contract["expected_scale_level"]) != 2
        ):
            raise ValueError(f"{_LANE_NAME} exact date/granularity drift: {candidate_id}")

        outcomes = list(map(str, contract["outcome_source_ids"]))
        evidence = list(map(str, contract["evidence_refs"]))
        date_sources = list(map(str, contract["date_source_ids"]))
        if (
            outcomes != sorted(source_ids)
            or evidence != outcomes
            or date_sources != outcomes
            or contract["outcome_source_family_ids"] != expected_families
            or len(expected_families) != 2
            or contract["source_date_refinement"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} source closure drift: {candidate_id}")
        role_map = contract["event_evidence_roles"]
        if set(role_map) != source_ids:
            raise ValueError(f"{_LANE_NAME} event source-role closure drift")
        for source_id, roles in role_map.items():
            if not _is_sorted_unique(roles) or not roles:
                raise ValueError(
                    f"{_LANE_NAME} event-specific role drift: "
                    f"{candidate_id}/{source_id}"
                )
        used_sources.update(outcomes)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")
    expected_adjacent = {
        "hced-Artaza1834-1",
        "hced-Asarta1833-1",
        "hced-Gatazo1895-1",
        "hced-Lircay1830-1",
        "hced-Mendaza1834-1",
        "hced-Ormaiztegui1835-1",
    }
    if set(WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS) != expected_adjacent:
        raise ValueError(f"{_LANE_NAME} adjacent HCED boundary drift")
    if set(WAVE8_ARQUIJAS_DISCOVERY_TWINS) != WAVE8_ARQUIJAS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} discovery owner drift")
    if set(WAVE8_ARQUIJAS_DISCOVERY_TWINS.values()) != set(
        WAVE8_ARQUIJAS_DISCOVERY_ROW_HASHES
    ) or set(WAVE8_ARQUIJAS_DISCOVERY_EXPECTED) != set(
        WAVE8_ARQUIJAS_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} discovery inventory drift")
    if WAVE8_ARQUIJAS_DISCOVERY_EXPECTED["Q12254001"][
        "outcome_disposition"
    ] != "unknown_never_draw":
        raise ValueError(f"{_LANE_NAME} unknown-is-never-draw guard drift")
    if len(WAVE8_ARQUIJAS_INTEGRATION_DISPOSITIONS) != 8:
        raise ValueError(f"{_LANE_NAME} integration disposition drift")
    if wave8_arquijas_audit_signature() != WAVE8_ARQUIJAS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def _hced_is_adjacent(row: Mapping[str, Any]) -> bool:
    side_labels = {
        normalize_label(row.get("side_1_raw")),
        normalize_label(row.get("side_2_raw")),
    }
    if _EXACT_LABEL in side_labels:
        return True
    name = normalize_label(row.get("name"))
    if name in {"artaza", "asarta"}:
        return True
    text_values = [row.get("name"), row.get("source_record_id")]
    text_values.extend(row.get("participants_raw", []) or [])
    return any("arquijas" in normalize_label(value) for value in text_values)


def validate_wave8_arquijas_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact_label_rows = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _EXACT_LABEL
        or normalize_label(row.get("side_2_raw")) == _EXACT_LABEL
    ]
    exact_label_ids = {str(row.get("candidate_id")) for row in exact_label_rows}
    if (
        exact_label_ids != WAVE8_ARQUIJAS_LABEL_DISPOSITION_IDS
        or len(exact_label_rows) != len(exact_label_ids)
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")

    adjacent = [row for row in hced_rows if _hced_is_adjacent(row)]
    adjacent_ids = {str(row.get("candidate_id")) for row in adjacent}
    expected_adjacent = {
        *WAVE8_ARQUIJAS_RESERVED_IDS,
        *WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS,
    }
    if adjacent_ids != expected_adjacent or len(adjacent) != len(adjacent_ids):
        raise ValueError(f"{_LANE_NAME} adjacent HCED inventory changed")

    by_id = {str(row["candidate_id"]): row for row in adjacent}
    for candidate_id, expected_hash in WAVE8_ARQUIJAS_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            row.get("side_1_raw") != "Carlists"
            or row.get("side_2_raw") != "Liberals"
            or row.get("winner_raw") != "Carlists"
            or row.get("loser_raw") != "Liberals"
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("do_not_rate_automatically") is not True
            or row.get("duplicate_source_id") is not False
        ):
            raise ValueError(f"{_LANE_NAME} locked outcome/actor row drift: {candidate_id}")
        year = 1834 if candidate_id.endswith("1834-1") else 1835
        if (row.get("year_low"), row.get("year_best"), row.get("year_high")) != (
            year,
            year,
            year,
        ):
            raise ValueError(f"{_LANE_NAME} locked year drift: {candidate_id}")

    for candidate_id, disposition in (
        WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS.items()
    ):
        if canonical_hced_row_sha256(by_id[candidate_id]) != disposition[
            "raw_row_sha256"
        ]:
            raise ValueError(
                f"{_LANE_NAME} adjacent HCED fingerprint changed: {candidate_id}"
            )

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ARQUIJAS_CONTRACTS,
        WAVE8_ARQUIJAS_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "adjacent_hced_rows": len(WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS),
        "exact_label_rows": len(exact_label_rows),
    }


def validate_wave8_arquijas_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
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
            for key in WAVE8_ARQUIJAS_FUNNEL_AUDIT["failure_cases"]
        },
        "label": str(row.get("label")),
        "rated_counterpart_entities": int(row.get("rated_counterpart_entities", -1)),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, row.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
    }
    if actual != WAVE8_ARQUIJAS_FUNNEL_AUDIT:
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


def validate_wave8_arquijas_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in WAVE8_ARQUIJAS_DISCOVERY_ROW_HASHES.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} discovery row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}")
        expected = WAVE8_ARQUIJAS_DISCOVERY_EXPECTED[candidate_id]
        winner_labels = [str(winner.get("label")) for winner in row.get("winners", [])]
        participant_labels = {
            str(participant.get("label")) for participant in row.get("participants", [])
        }
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("name") != expected["name"]
            or row.get("date") != expected["date"]
            or winner_labels != expected["winner_labels"]
            or participant_labels != {"Carlist army", "Christinos"}
        ):
            raise ValueError(
                f"{_LANE_NAME} discovery non-rating guard changed: {candidate_id}"
            )
        if (
            expected["outcome_disposition"] == "unknown_never_draw"
            and row.get("winners") != []
        ):
            raise ValueError(f"{_LANE_NAME} unknown discovery outcome changed")
    return {
        "discovery_nonrating_twins": len(WAVE8_ARQUIJAS_DISCOVERY_ROW_HASHES),
        "discovery_promotions": 0,
        "unknown_never_draw_rows": 1,
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
    start_date = str(row.get("start_date") or "")
    if len(start_date) >= 4 and start_date[:4].isdigit():
        return int(start_date[:4])
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
    "hced-Arquijas1834-1": {
        "Arquijas",
        "First Battle of Arquijas",
        "First Battle of the Bridge of Arquijas",
        "Primera Batalla de Arquijas",
    },
    "hced-Arquijas1835-1": {
        "Arquijas",
        "Second Battle of Arquijas",
        "Second Battle of the Bridge of Arquijas",
        "Segunda Batalla de Arquijas",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(WAVE8_ARQUIJAS_CONTRACTS[candidate_id]["canonical_event"]["year_low"]),
        normalize_label(alias),
    )
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
)
_ARQUIJAS_NAMES = frozenset(
    normalize_label(alias) for aliases in _EVENT_ALIASES.values() for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    names = _row_names(row)
    matched_names = names & _ARQUIJAS_NAMES
    if not matched_names:
        return False
    year = _row_year(row)
    if year is None:
        return True
    return any((year, name) in _DUPLICATE_MATCH_KEYS for name in matched_names)


def validate_wave8_arquijas_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwd_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin adjacent HCED rows and prove IWD/IWBD/release twin absence."""

    validate_wave8_arquijas_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_ARQUIJAS_RESERVED_IDS
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
        if event.get("hced_candidate_id") in WAVE8_ARQUIJAS_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    if owned:
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        if owned_ids != WAVE8_ARQUIJAS_CONTRACT_IDS or len(owned) != len(owned_ids):
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
        "adjacent_hced_dispositions": len(
            WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS
        ),
        "existing_release_owned_events": len(owned),
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwd_probable_twins": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_arquijas_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ARQUIJAS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_arquijas_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_ARQUIJAS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_ARQUIJAS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_ARQUIJAS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_arquijas_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_arquijas_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ARQUIJAS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def _entity_covers(entity: Mapping[str, Any], low: int, high: int) -> bool:
    start = entity.get("start_year")
    end = entity.get("end_year")
    return (
        start is not None
        and int(start) <= low
        and (end is None or int(end) >= high)
    )


def validate_wave8_arquijas_current_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Require Arquijas release events and sources to be absent or complete."""

    _validate_static()
    entity_by_id = {str(entity.get("id")): entity for entity in release_entities}
    for entity_id in (_CARLIST_FORCES, _ISABELINE_FORCES):
        entity = entity_by_id.get(entity_id)
        if entity is None or not _entity_covers(entity, 1834, 1835):
            raise ValueError(f"{_LANE_NAME} required identity missing: {entity_id}")
        if list(entity.get("aliases", [])):
            raise ValueError(f"{_LANE_NAME} identity alias inventory changed: {entity_id}")

    events = list(release_events)
    owned = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_ARQUIJAS_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    source_ids = set(_SOURCE_BY_ID)
    present_source_ids = {
        str(source.get("id"))
        for source in release_sources
        if str(source.get("id")) in source_ids
    }
    if len(owned) not in {0, len(WAVE8_ARQUIJAS_CONTRACT_IDS)}:
        raise ValueError(f"{_LANE_NAME} current release event inventory is partial")
    if len(present_source_ids) not in {0, len(source_ids)}:
        raise ValueError(f"{_LANE_NAME} current release source inventory is partial")
    if bool(owned) != bool(present_source_ids):
        raise ValueError(f"{_LANE_NAME} current release artifacts are out of sync")
    if not owned:
        return {
            "artifact_state": "absent",
            "installed_sources": 0,
            "promoted_events": 0,
        }

    by_candidate = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_candidate) != WAVE8_ARQUIJAS_CONTRACT_IDS or len(owned) != len(
        by_candidate
    ):
        raise ValueError(f"{_LANE_NAME} current release candidate inventory changed")
    for candidate_id, contract in WAVE8_ARQUIJAS_CONTRACTS.items():
        event = by_candidate[candidate_id]
        canonical = contract["canonical_event"]
        expected_id = f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        year = int(canonical["year_low"])
        if (
            event.get("id") != expected_id
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year")) != (year, year)
            or event.get("date_precision") != "day"
            or event.get("reviewed_granularity")
            != "single_battle_in_the_first_carlist_war"
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids")
            != contract["outcome_source_family_ids"]
            or float(event.get("confidence", -1.0)) != float(contract["confidence"])
        ):
            raise ValueError(f"{_LANE_NAME} current release event drift: {candidate_id}")
        expected_participants = expected_exact_hced_win_participants(
            [_CARLIST_FORCES],
            [_ISABELINE_FORCES],
            confidence=float(contract["confidence"]),
            scale_level=int(contract["expected_scale_level"]),
            lane_name=_LANE_NAME,
        )
        if event.get("participants") != expected_participants:
            raise ValueError(
                f"{_LANE_NAME} current release participant drift: {candidate_id}"
            )
        if (
            "geometry" in event
            or event.get("modern_location_country") != "Spain"
            or "location_provenance" not in event
        ):
            raise ValueError(f"{_LANE_NAME} current release location drift: {candidate_id}")

    return {
        "artifact_state": "integrated",
        "installed_sources": len(present_source_ids),
        "promoted_events": len(owned),
    }


def wave8_arquijas_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_ARQUIJAS_CONTRACTS.values(),
                    *WAVE8_ARQUIJAS_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_arquijas_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_hced_dispositions": len(
            WAVE8_ARQUIJAS_ADJACENT_HCED_DISPOSITIONS
        ),
        "country_quarantine_additions": 0,
        "discovery_nonrating_twins": len(WAVE8_ARQUIJAS_DISCOVERY_ROW_HASHES),
        "holds": 0,
        "integration_dispositions": len(WAVE8_ARQUIJAS_INTEGRATION_DISPOSITIONS),
        "new_entities": 0,
        "new_sources": len(WAVE8_ARQUIJAS_SOURCES),
        "newly_rated_events": len(WAVE8_ARQUIJAS_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_ARQUIJAS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_ARQUIJAS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_ARQUIJAS_RESERVED_IDS),
        "terminal_exclusions": 0,
        "unknown_discovery_outcomes": 1,
    }


def wave8_arquijas_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_arquijas_counts(),
        "cohorts": wave8_arquijas_cohort_counts(),
        "final_audit_signature": WAVE8_ARQUIJAS_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_ARQUIJAS_CONTRACT_IDS),
        "hold_candidate_ids": [],
        "discovery_nonrating_candidate_ids": sorted(
            WAVE8_ARQUIJAS_DISCOVERY_ROW_HASHES
        ),
    }


_validate_static()
