"""Exact-candidate audit for HCED's two unresolved Latrun rows.

The lane rates only the first two Israeli assaults on the Arab Legion position
at Latrun in May 1948.  David Rodman's battle study and Matthew Hughes's
peer-reviewed operational history independently identify the opposing forces
and the Arab Legion's tactical success.  The contracts reuse the existing
time-bounded Arab Legion and Israel identities; they add no identity, alias,
resolver rule, or date window.

IWBD contains exact twins for these two assaults plus two later Latrun
actions.  Those four records, the composite 1941 Arab Legion label, and a
Latrun place mention in the Lydda-Ramleh row are fingerprinted below so that
no adjacent event can be silently absorbed.  Unknown is never converted to a
draw, and no result beyond the two source-attested tactical repulses is rated.
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
    "WAVE8_LATRUN_ADJACENT_HCED_DISPOSITIONS",
    "WAVE8_LATRUN_CONTRACT_IDS",
    "WAVE8_LATRUN_CONTRACTS",
    "WAVE8_LATRUN_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_LATRUN_ENTITIES",
    "WAVE8_LATRUN_FINAL_AUDIT_SIGNATURE",
    "WAVE8_LATRUN_FUNNEL_AUDIT",
    "WAVE8_LATRUN_HOLDS",
    "WAVE8_LATRUN_INTEGRATION_DISPOSITIONS",
    "WAVE8_LATRUN_IWBD_ADJACENT_DISPOSITIONS",
    "WAVE8_LATRUN_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_LATRUN_LOCATION_QUARANTINE_REASONS",
    "WAVE8_LATRUN_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_LATRUN_RESERVED_IDS",
    "WAVE8_LATRUN_ROW_HASHES",
    "WAVE8_LATRUN_SOURCES",
    "install_wave8_latrun_entities",
    "install_wave8_latrun_sources",
    "promote_wave8_latrun_contracts",
    "validate_wave8_latrun_current_release",
    "validate_wave8_latrun_funnel",
    "validate_wave8_latrun_integration_dispositions",
    "validate_wave8_latrun_queue_contracts",
    "wave8_latrun_audit_signature",
    "wave8_latrun_cohort_counts",
    "wave8_latrun_counts",
    "wave8_latrun_metadata",
)


_LANE_NAME = "Wave 8 exact Latrun audit"
_MODULE_OWNER = "military_elo.promotion.wave8_latrun"
_EVENT_ID_PREFIX = "hced_wave8_latrun_"
_EXACT_LABEL = "arab legion"
_COHORT = "latrun_arab_legion_defensive_battles_may_1948"

_ARAB_LEGION = "arab_legion_transjordan"
_ISRAEL = "clio_q801_1948_5abea45e"


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


WAVE8_LATRUN_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_latrun_hughes_conduct_operations",
        (
            "The Conduct of Operations: Glubb Pasha, the Arab Legion, and "
            "the First Arab-Israeli War, 1948-49"
        ),
        "https://bura.brunel.ac.uk/handle/2438/16047",
        "War in History / Brunel University Research Archive",
        "peer_reviewed_scholarly_article",
        "hughes_glubb_arab_legion_2018",
    ),
    _source(
        "wave8_latrun_rodman_battle_chapter",
        "The Battle of Latrun",
        "https://www.jstor.org/stable/j.ctv333ktt8.7",
        "Liverpool University Press / JSTOR",
        "scholarly_monograph_chapter",
        "rodman_victory_defeat_or_draw_2021",
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_LATRUN_SOURCES}


# Both participants already exist in the release.  This empty fixture is a
# mechanical guarantee that the lane cannot create an identity or an alias.
WAVE8_LATRUN_ENTITIES: tuple[dict[str, Any], ...] = ()


WAVE8_LATRUN_ROW_HASHES: dict[str, str] = {
    "hced-Latrun (1st)1948-1": (
        "a9ea4fe32e2faaf06dc72487af6cc6670ed8cca1090ca978617d9249bca61b2d"
    ),
    "hced-Latrun (2nd)1948-1": (
        "c604369305d9de0d631fca49d4d0fa85adaa08725b4b119d606ab1e910ae97e0"
    ),
}


WAVE8_LATRUN_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "ac1537f1f36875340315f38a7e9492b2abf54d88165eef47ba511030db59955b"
    ),
    "events_touched": 2,
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 2,
    },
    "label": _EXACT_LABEL,
    "rated_counterpart_entities": 1,
    "sole_blocker_events": 2,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 2,
}


def _canonical(
    name: str,
    date_text: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:1948:1948",
        "date_precision": "day_range",
        "date_text": date_text,
        "end_date": end_date,
        "granularity": "single_assault_engagement",
        "name": name,
        "start_date": start_date,
        "year_high": 1948,
        "year_low": 1948,
    }


_EVENT_EVIDENCE_ROLES: dict[str, list[str]] = {
    "wave8_latrun_hughes_conduct_operations": [
        "independent_tactical_outcome_crosscheck",
        "latrun_series_belligerent_attribution",
        "single_assault_granularity_crosscheck",
    ],
    "wave8_latrun_rodman_battle_chapter": [
        "exact_attack_date",
        "exact_belligerents",
        "single_assault_granularity",
        "tactical_outcome",
    ],
}


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    audit_note: str,
) -> dict[str, Any]:
    outcomes = sorted(_SOURCE_BY_ID)
    return {
        "raw_row_sha256": WAVE8_LATRUN_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "side_1_entity_ids": [_ARAB_LEGION],
        "side_2_entity_ids": [_ISRAEL],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate_limited",
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
            for source_id, roles in sorted(_EVENT_EVIDENCE_ROLES.items())
        },
        "date_source_ids": outcomes,
        "source_date_refinement": True,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_existing_arab_legion_and_israel",
        "expected_scale_level": 2,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_LATRUN_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Latrun (1st)1948-1": _contract(
        "hced-Latrun (1st)1948-1",
        _canonical(
            "First Battle of Latrun (Operation Bin Nun Alef)",
            "24-25 May 1948",
            "1948-05-24",
            "1948-05-25",
        ),
        (
            "Rodman treats the first assault as a discrete battle and records "
            "the Israeli attack's defeat; Hughes independently identifies the "
            "Arab Legion as defeating Israel in the Latrun fighting. Only the "
            "24-25 May tactical repulse is rated."
        ),
    ),
    "hced-Latrun (2nd)1948-1": _contract(
        "hced-Latrun (2nd)1948-1",
        _canonical(
            "Second Battle of Latrun (Operation Bin Nun Bet)",
            "30-31 May 1948",
            "1948-05-30",
            "1948-05-31",
        ),
        (
            "Rodman separates the second assault and its failure from the other "
            "Latrun actions; Hughes independently confirms the Arab Legion's "
            "successful defense against the Israeli attack series. Only the "
            "30-31 May tactical repulse is rated."
        ),
    ),
}


WAVE8_LATRUN_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_LATRUN_CONTRACT_IDS = frozenset(WAVE8_LATRUN_CONTRACTS)
WAVE8_LATRUN_RESERVED_IDS = WAVE8_LATRUN_CONTRACT_IDS


# These are related queue records, not lane reservations.  Their hashes make
# the exact-label and duplicate-ownership boundary reviewable and fail-closed.
WAVE8_LATRUN_ADJACENT_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Lydda-Ramleh1948-1": {
        "raw_row_sha256": (
            "3376b013ca6f0a74ae478f3973bda1774d475fdf37a3a5ea168e49cbbd2b3e07"
        ),
        "disposition": "adjacent_distinct_event_not_owned",
        "relationship": "latrun_is_only_a_participant_context_place_mention",
        "reason": (
            "The row is the distinct Lydda-Ramleh engagement; Latrun appears "
            "only in noisy participant context and supplies neither actor."
        ),
    },
    "hced-Palmyra1941-1": {
        "raw_row_sha256": (
            "d14471c2e7c31ce10c545045d0a1605c26312bb8efc2d1df8f593186bbac753a"
        ),
        "disposition": "external_lane_owner",
        "relationship": "composite_arab_legion_label_unrelated_1941_event",
        "owner_module": "military_elo.promotion.wave7_root",
        "reason": (
            "Palmyra is a separately owned 1941 coalition event whose raw side "
            "is 'United Kingdom, Arab Legion'; it is not an exact Arab Legion "
            "label and cannot be absorbed into the 1948 Latrun lane."
        ),
    },
}


_IWBD_FINGERPRINT_FIELDS = (
    "source_row",
    "source_snapshot",
    "name",
    "war_name",
    "start_date",
    "end_date",
    "duration_days",
    "attacker_raw",
    "defender_raw",
    "winner_raw",
    "battle_level_victor_role",
    "war_level_victor_role",
)


def _iwbd_record(
    *,
    hced_candidate_id: str | None,
    disposition: str,
    relationship: str,
    source_row: str,
    name: str,
    start_date: str,
    end_date: str,
    duration_days: str,
    reason: str,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "source_dataset": "iwbd",
        "disposition": disposition,
        "relationship": relationship,
        "fingerprint": {
            "source_row": source_row,
            "source_snapshot": (
                "data/raw/iwbd/20260713T161518Z-fcf5747cf94b.bin"
            ),
            "name": name,
            "war_name": "Arab-Israeli",
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": duration_days,
            "attacker_raw": "Israel",
            "defender_raw": "Arab States",
            "winner_raw": "Arab States",
            "battle_level_victor_role": "Defender",
            "war_level_victor_role": "Initiator",
        },
        "reason": reason,
    }
    if hced_candidate_id is not None:
        record["hced_candidate_id"] = hced_candidate_id
    return record


WAVE8_LATRUN_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-148-55-1386": _iwbd_record(
        hced_candidate_id="hced-Latrun (1st)1948-1",
        disposition="deduplicate_to_hced",
        relationship="same_first_assault_same_date_same_tactical_outcome",
        source_row="1386",
        name="Latrun 1 (a)",
        start_date="1948-05-25",
        end_date="1948-05-25",
        duration_days="1",
        reason=(
            "IWBD's 25 May record is the first HCED Latrun assault. The "
            "source-reviewed HCED contract is the sole rating owner."
        ),
    ),
    "iwbd-148-55-1388": _iwbd_record(
        hced_candidate_id="hced-Latrun (2nd)1948-1",
        disposition="deduplicate_to_hced",
        relationship="same_second_assault_same_start_date_same_tactical_outcome",
        source_row="1388",
        name="Latrun 1 (b)",
        start_date="1948-05-30",
        end_date="1948-05-30",
        duration_days="1",
        reason=(
            "IWBD's 30 May record is the second HCED Latrun assault. Its "
            "single-day encoding falls within the reviewed 30-31 May battle, "
            "and the HCED contract is the sole rating owner."
        ),
    ),
}


WAVE8_LATRUN_IWBD_ADJACENT_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-148-55-1390": _iwbd_record(
        hced_candidate_id=None,
        disposition="adjacent_distinct_event_not_owned",
        relationship="later_third_assault_operation_yoram",
        source_row="1390",
        name="Latrun 1 (c)",
        start_date="1948-06-09",
        end_date="1948-06-09",
        duration_days="1",
        reason=(
            "The 9 June Operation Yoram action is a third, later assault and "
            "has no matching HCED contract in this lane."
        ),
    ),
    "iwbd-148-55-1395": _iwbd_record(
        hced_candidate_id=None,
        disposition="adjacent_distinct_event_not_owned",
        relationship="later_july_latrun_operations",
        source_row="1395",
        name="Latrun 2",
        start_date="1948-07-14",
        end_date="1948-07-18",
        duration_days="5",
        reason=(
            "The 14-18 July action belongs to the later Latrun operations and "
            "is not either May assault owned by this lane."
        ),
    ),
}


WAVE8_LATRUN_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_LATRUN_ADJACENT_HCED_DISPOSITIONS,
    **WAVE8_LATRUN_IWBD_DUPLICATE_DISPOSITIONS,
    **WAVE8_LATRUN_IWBD_ADJACENT_DISPOSITIONS,
}


WAVE8_LATRUN_POINT_QUARANTINE_ADDITIONS = WAVE8_LATRUN_CONTRACT_IDS
WAVE8_LATRUN_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_LATRUN_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the Latrun defensive position and "
            "modern country, but do not independently audit HCED's repeated "
            "decimal coordinate. Retain country and provenance; withhold point."
        ),
        "evidence_refs": sorted(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_LATRUN_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_LATRUN_CONTRACTS,
        "entities": WAVE8_LATRUN_ENTITIES,
        "funnel": WAVE8_LATRUN_FUNNEL_AUDIT,
        "holds": WAVE8_LATRUN_HOLDS,
        "integration_dispositions": WAVE8_LATRUN_INTEGRATION_DISPOSITIONS,
        "location_reasons": WAVE8_LATRUN_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_LATRUN_ROW_HASHES,
        "sources": WAVE8_LATRUN_SOURCES,
    }


def wave8_latrun_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_LATRUN_FINAL_AUDIT_SIGNATURE = (
    "88f181f06f5c45792a077befae74a160fa20bfa88a99c443e13fcad3ab6145ea"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_LATRUN_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if WAVE8_LATRUN_ENTITIES:
        raise ValueError(f"{_LANE_NAME} must not create identities")
    if WAVE8_LATRUN_HOLDS:
        raise ValueError(f"{_LANE_NAME} exact inventory unexpectedly contains a hold")
    if WAVE8_LATRUN_RESERVED_IDS != set(WAVE8_LATRUN_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_LATRUN_POINT_QUARANTINE_ADDITIONS != WAVE8_LATRUN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_LATRUN_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_LATRUN_LOCATION_QUARANTINE_REASONS) != WAVE8_LATRUN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    expected_urls = {
        "wave8_latrun_hughes_conduct_operations": (
            "https://bura.brunel.ac.uk/handle/2438/16047"
        ),
        "wave8_latrun_rodman_battle_chapter": (
            "https://www.jstor.org/stable/j.ctv333ktt8.7"
        ),
    }
    for source_id, source in _SOURCE_BY_ID.items():
        if source["url"] != expected_urls[source_id]:
            raise ValueError(f"{_LANE_NAME} canonical source URL drift: {source_id}")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source role order drift: {source_id}")
        if "outcome" not in source["evidence_roles"]:
            raise ValueError(f"{_LANE_NAME} non-outcome source used for result")

    expected_dates = {
        "hced-Latrun (1st)1948-1": (
            "24-25 May 1948",
            "1948-05-24",
            "1948-05-25",
        ),
        "hced-Latrun (2nd)1948-1": (
            "30-31 May 1948",
            "1948-05-30",
            "1948-05-31",
        ),
    }
    used_sources: set[str] = set()
    expected_families = sorted(
        str(source["source_family_id"]) for source in WAVE8_LATRUN_SOURCES
    )
    for candidate_id, contract in WAVE8_LATRUN_CONTRACTS.items():
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
        ) != ([_ARAB_LEGION], [_ISRAEL]):
            raise ValueError(f"{_LANE_NAME} exact actor drift: {candidate_id}")

        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        actual_dates = (
            str(canonical["date_text"]),
            str(canonical["start_date"]),
            str(canonical["end_date"]),
        )
        if (
            canonical["canonical_key"] != expected_key
            or canonical["date_precision"] != "day_range"
            or canonical["granularity"] != "single_assault_engagement"
            or (canonical["year_low"], canonical["year_high"]) != (1948, 1948)
            or actual_dates != expected_dates[candidate_id]
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
            or contract["source_date_refinement"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} source closure drift: {candidate_id}")
        role_map = contract["event_evidence_roles"]
        if set(role_map) != source_ids:
            raise ValueError(f"{_LANE_NAME} event source-role closure drift")
        for source_id, roles in role_map.items():
            if not _is_sorted_unique(roles) or not roles:
                raise ValueError(
                    f"{_LANE_NAME} event-specific role drift: {candidate_id}/{source_id}"
                )
        used_sources.update(outcomes)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")
    if set(WAVE8_LATRUN_ADJACENT_HCED_DISPOSITIONS) != {
        "hced-Lydda-Ramleh1948-1",
        "hced-Palmyra1941-1",
    }:
        raise ValueError(f"{_LANE_NAME} adjacent HCED boundary drift")
    if set(WAVE8_LATRUN_IWBD_DUPLICATE_DISPOSITIONS) != {
        "iwbd-148-55-1386",
        "iwbd-148-55-1388",
    }:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate boundary drift")
    if set(WAVE8_LATRUN_IWBD_ADJACENT_DISPOSITIONS) != {
        "iwbd-148-55-1390",
        "iwbd-148-55-1395",
    }:
        raise ValueError(f"{_LANE_NAME} IWBD adjacent boundary drift")
    if len(WAVE8_LATRUN_INTEGRATION_DISPOSITIONS) != 6:
        raise ValueError(f"{_LANE_NAME} integration inventory drift")
    if wave8_latrun_audit_signature() != WAVE8_LATRUN_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def _hced_is_adjacent(row: Mapping[str, Any]) -> bool:
    side_labels = (
        normalize_label(row.get("side_1_raw")),
        normalize_label(row.get("side_2_raw")),
    )
    if any("arab legion" in label for label in side_labels):
        return True
    text_values = [row.get("name"), row.get("source_record_id")]
    text_values.extend(row.get("participants_raw", []) or [])
    return any("latrun" in normalize_label(value) for value in text_values)


def validate_wave8_latrun_queue_contracts(
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
    if exact_ids != WAVE8_LATRUN_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")

    adjacent = [row for row in hced_rows if _hced_is_adjacent(row)]
    adjacent_ids = {str(row.get("candidate_id")) for row in adjacent}
    expected_adjacent_ids = {
        *WAVE8_LATRUN_RESERVED_IDS,
        *WAVE8_LATRUN_ADJACENT_HCED_DISPOSITIONS,
    }
    if adjacent_ids != expected_adjacent_ids or len(adjacent) != len(adjacent_ids):
        raise ValueError(f"{_LANE_NAME} adjacent HCED inventory changed")

    by_id = {str(row["candidate_id"]): row for row in adjacent}
    for candidate_id, expected_hash in WAVE8_LATRUN_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            row.get("side_1_raw") != "Arab Legion"
            or row.get("side_2_raw") != "Israel"
            or row.get("winner_raw") != "Arab Legion"
            or row.get("loser_raw") != "Israel"
            or (row.get("year_low"), row.get("year_best"), row.get("year_high"))
            != (1948, 1948, 1948)
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
        ):
            raise ValueError(f"{_LANE_NAME} locked outcome/actor row drift: {candidate_id}")

    for candidate_id, disposition in WAVE8_LATRUN_ADJACENT_HCED_DISPOSITIONS.items():
        if canonical_hced_row_sha256(by_id[candidate_id]) != disposition["raw_row_sha256"]:
            raise ValueError(
                f"{_LANE_NAME} adjacent HCED fingerprint changed: {candidate_id}"
            )

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_LATRUN_CONTRACTS,
        WAVE8_LATRUN_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "adjacent_hced_rows": len(WAVE8_LATRUN_ADJACENT_HCED_DISPOSITIONS),
        "exact_label_rows": len(exact),
    }


def validate_wave8_latrun_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
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
            for key in WAVE8_LATRUN_FUNNEL_AUDIT["failure_cases"]
        },
        "label": str(row.get("label")),
        "rated_counterpart_entities": int(row.get("rated_counterpart_entities", -1)),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, row.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
    }
    if actual != WAVE8_LATRUN_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pin changed: {actual}")
    return {
        "events_touched": actual["events_touched"],
        "sole_blocker_events": actual["sole_blocker_events"],
        "unresolved_side_attempts": actual["unresolved_side_attempts"],
        "zero_time_valid_candidates": actual["failure_cases"][
            "zero_time_valid_candidates"
        ],
    }


def _iwbd_fingerprint(row: Mapping[str, Any]) -> dict[str, str]:
    return {
        field: "" if row.get(field) is None else str(row.get(field))
        for field in _IWBD_FINGERPRINT_FIELDS
    }


def _is_latrun_iwbd(row: Mapping[str, Any]) -> bool:
    normalized = normalize_label(row.get("name"))
    return "latrun" in normalized or "bab al wad" in normalized


_DUPLICATE_ALIASES = {
    "hced-Latrun (1st)1948-1": {
        "First Battle of Latrun",
        "First Battle of Latrun (Operation Bin Nun Alef)",
        "Latrun (1st)",
        "Operation Bin Nun Alef",
    },
    "hced-Latrun (2nd)1948-1": {
        "Second Battle of Latrun",
        "Second Battle of Latrun (Operation Bin Nun Bet)",
        "Latrun (2nd)",
        "Operation Bin Nun Bet",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (1948, normalize_label(alias))
    for aliases in _DUPLICATE_ALIASES.values()
    for alias in aliases
)


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low"):
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
    values = [row.get("name"), row.get("battle_name"), row.get("event_name")]
    aliases = row.get("aliases", []) or []
    if isinstance(aliases, str):
        values.append(aliases)
    else:
        values.extend(aliases)
    return {normalize_label(value) for value in values if normalize_label(value)}


def _is_probable_release_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_latrun_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin adjacent rows, exact IWBD twins, and current release ownership."""

    validate_wave8_latrun_queue_contracts(hced_rows)
    latrun_iwbd = [row for row in iwbd_rows if _is_latrun_iwbd(row)]
    by_iwbd_id = {str(row.get("candidate_id")): row for row in latrun_iwbd}
    expected_iwbd = {
        *WAVE8_LATRUN_IWBD_DUPLICATE_DISPOSITIONS,
        *WAVE8_LATRUN_IWBD_ADJACENT_DISPOSITIONS,
    }
    if set(by_iwbd_id) != expected_iwbd or len(latrun_iwbd) != len(by_iwbd_id):
        raise ValueError(f"{_LANE_NAME} IWBD Latrun inventory changed")
    for candidate_id in sorted(expected_iwbd):
        disposition = WAVE8_LATRUN_INTEGRATION_DISPOSITIONS[candidate_id]
        if _iwbd_fingerprint(by_iwbd_id[candidate_id]) != disposition["fingerprint"]:
            raise ValueError(f"{_LANE_NAME} IWBD fingerprint changed: {candidate_id}")

    existing = list(existing_events)
    owned = [
        event
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_LATRUN_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    if owned:
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        if owned_ids != WAVE8_LATRUN_CONTRACT_IDS or len(owned) != len(owned_ids):
            raise ValueError(f"{_LANE_NAME} current release ownership is partial")
        if any(not str(event.get("id", "")).startswith(_EVENT_ID_PREFIX) for event in owned):
            raise ValueError(f"{_LANE_NAME} current release owner prefix changed")

    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event not in owned and _is_probable_release_twin(event)
    )
    if release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_twins}"
        )
    return {
        "adjacent_hced_dispositions": len(
            WAVE8_LATRUN_ADJACENT_HCED_DISPOSITIONS
        ),
        "existing_release_owned_events": len(owned),
        "existing_release_probable_twins": 0,
        "iwbd_adjacent_dispositions": len(
            WAVE8_LATRUN_IWBD_ADJACENT_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_LATRUN_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_latrun_rows": len(latrun_iwbd),
    }


def install_wave8_latrun_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_LATRUN_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_latrun_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_LATRUN_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_LATRUN_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_LATRUN_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_latrun_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_latrun_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_LATRUN_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def _entity_covers(entity: Mapping[str, Any], year: int) -> bool:
    start = entity.get("start_year")
    end = entity.get("end_year")
    return (
        start is not None
        and int(start) <= year
        and (end is None or int(end) >= year)
    )


def validate_wave8_latrun_current_release(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Require lane events and source fixtures to be absent or complete together."""

    _validate_static()
    entity_by_id = {str(entity.get("id")): entity for entity in release_entities}
    for entity_id in (_ARAB_LEGION, _ISRAEL):
        entity = entity_by_id.get(entity_id)
        if entity is None or not _entity_covers(entity, 1948):
            raise ValueError(f"{_LANE_NAME} required identity missing: {entity_id}")
    if list(entity_by_id[_ARAB_LEGION].get("aliases", [])):
        raise ValueError(f"{_LANE_NAME} Arab Legion alias inventory changed")

    events = list(release_events)
    owned = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_LATRUN_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    source_ids = set(_SOURCE_BY_ID)
    present_source_ids = {
        str(source.get("id"))
        for source in release_sources
        if str(source.get("id")) in source_ids
    }
    if len(owned) not in {0, len(WAVE8_LATRUN_CONTRACT_IDS)}:
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
    if set(by_candidate) != WAVE8_LATRUN_CONTRACT_IDS or len(owned) != len(by_candidate):
        raise ValueError(f"{_LANE_NAME} current release candidate inventory changed")
    for candidate_id, contract in WAVE8_LATRUN_CONTRACTS.items():
        event = by_candidate[candidate_id]
        canonical = contract["canonical_event"]
        expected_id = f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        if (
            event.get("id") != expected_id
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year")) != (1948, 1948)
            or event.get("date_precision") != "day_range"
            or event.get("reviewed_granularity") != "single_assault_engagement"
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids")
            != contract["outcome_source_family_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} current release event drift: {candidate_id}")
        expected_participants = expected_exact_hced_win_participants(
            [_ARAB_LEGION],
            [_ISRAEL],
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
            or event.get("modern_location_country") != "Israel"
            or "location_provenance" not in event
        ):
            raise ValueError(f"{_LANE_NAME} current release location drift: {candidate_id}")

    return {
        "artifact_state": "integrated",
        "installed_sources": len(present_source_ids),
        "promoted_events": len(owned),
    }


def wave8_latrun_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_LATRUN_CONTRACTS.values(),
                    *WAVE8_LATRUN_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_latrun_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_hced_dispositions": len(
            WAVE8_LATRUN_ADJACENT_HCED_DISPOSITIONS
        ),
        "country_quarantine_additions": 0,
        "holds": 0,
        "integration_dispositions": len(WAVE8_LATRUN_INTEGRATION_DISPOSITIONS),
        "iwbd_adjacent_dispositions": len(
            WAVE8_LATRUN_IWBD_ADJACENT_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_LATRUN_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": 0,
        "new_sources": len(WAVE8_LATRUN_SOURCES),
        "newly_rated_events": len(WAVE8_LATRUN_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_LATRUN_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_LATRUN_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_LATRUN_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_latrun_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_latrun_counts(),
        "cohorts": wave8_latrun_cohort_counts(),
        "final_audit_signature": WAVE8_LATRUN_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_LATRUN_CONTRACT_IDS),
        "hold_candidate_ids": [],
    }


_validate_static()
