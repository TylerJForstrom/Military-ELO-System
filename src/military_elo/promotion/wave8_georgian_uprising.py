"""Candidate-keyed audit of HCED's two ``Georgian Rebels`` rows.

The label describes the force raised in Kartli and Kakheti during the 1625
uprising against Safavid rule, not a timeless Georgian polity or a generic
rebel identity.  This lane therefore creates one alias-free, year-bounded
force and uses it only for the two fingerprinted rows: the Georgian victory at
Martqopi and the Safavid victory at Marabda.

The reviewed sources state 25 March and 1 July respectively, but do not state
which calendar style those dates use.  The contracts preserve the source text
and explicitly mark the calendar as unspecified; they do not manufacture
Gregorian ISO dates.  Both HCED points remain quarantined while the audited
modern-country assertion is retained.
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
    "WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS",
    "WAVE8_GEORGIAN_UPRISING_CONTRACTS",
    "WAVE8_GEORGIAN_UPRISING_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_GEORGIAN_UPRISING_ENTITIES",
    "WAVE8_GEORGIAN_UPRISING_EXPECTED_CANDIDATE_IDS",
    "WAVE8_GEORGIAN_UPRISING_FINAL_AUDIT_SIGNATURE",
    "WAVE8_GEORGIAN_UPRISING_FUNNEL_AUDIT",
    "WAVE8_GEORGIAN_UPRISING_HOLDS",
    "WAVE8_GEORGIAN_UPRISING_LOCATION_QUARANTINE_REASONS",
    "WAVE8_GEORGIAN_UPRISING_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_GEORGIAN_UPRISING_REQUIRED_EXISTING_ENTITIES",
    "WAVE8_GEORGIAN_UPRISING_RESERVED_IDS",
    "WAVE8_GEORGIAN_UPRISING_ROW_HASHES",
    "WAVE8_GEORGIAN_UPRISING_SOURCES",
    "install_wave8_georgian_uprising_entities",
    "install_wave8_georgian_uprising_sources",
    "promote_wave8_georgian_uprising_contracts",
    "validate_wave8_georgian_uprising_existing_entities",
    "validate_wave8_georgian_uprising_funnel",
    "validate_wave8_georgian_uprising_integration_dispositions",
    "validate_wave8_georgian_uprising_queue_contracts",
    "wave8_georgian_uprising_audit_signature",
    "wave8_georgian_uprising_cohort_counts",
    "wave8_georgian_uprising_counts",
    "wave8_georgian_uprising_location_quarantine_additions",
    "wave8_georgian_uprising_metadata",
)


_LANE_NAME = "Wave 8 exact Kartli-Kakheti uprising audit"
_MODULE_OWNER = "military_elo.promotion.wave8_georgian_uprising"
_EVENT_ID_PREFIX = "hced_wave8_georgian_uprising_"
_EXACT_LABEL = "georgian rebels"

_UPRISING_FORCE_ID = "kartli_kakheti_uprising_forces_1625"
_SAFAVID_ID = "safavid_empire"


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


WAVE8_GEORGIAN_UPRISING_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_georgian_uprising_georgian_encyclopedia_martqopi",
        "Martqopi, Battle of (1625)",
        "https://georgianencyclopedia.ge/ka/form/29982",
        (
            "Georgian National Academy of Sciences, Georgian Encyclopedia "
            "Main Scientific Editorial Board"
        ),
        "national_scholarly_encyclopedia",
        "georgian_encyclopedia_martqopi",
    ),
    _source(
        "wave8_georgian_uprising_georgian_encyclopedia_marabda",
        "Marabda, Battle of (1625)",
        "https://georgianencyclopedia.ge/ka/form/29845",
        (
            "Georgian National Academy of Sciences, Georgian Encyclopedia "
            "Main Scientific Editorial Board"
        ),
        "national_scholarly_encyclopedia",
        "georgian_encyclopedia_marabda",
    ),
    _source(
        "wave8_georgian_uprising_mikaberidze_marabda",
        "Marabda, Battle of (1625)",
        "https://www.allgeo.org/index.php/en/858-marabda-battle-of-1625",
        (
            "Allgeo.org transcription of Alexander Mikaberidze, Historical "
            "Dictionary of Georgia"
        ),
        "scholarly_historical_dictionary_transcription",
        "mikaberidze_historical_dictionary_georgia",
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_GEORGIAN_UPRISING_SOURCES
}


WAVE8_GEORGIAN_UPRISING_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _UPRISING_FORCE_ID,
        "name": "Kartli-Kakheti uprising forces (1625)",
        "kind": "uprising_bounded_joint_field_force",
        "start_year": 1625,
        "end_year": 1625,
        "region": "Kartli and Kakheti, eastern Georgia",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the Kartli-Kakheti force that fought the Safavid armies "
            "at Martqopi and Marabda during the 1625 uprising under Giorgi "
            "Saakadze and Teimuraz I. No generic Georgian Rebels, Georgia, "
            "Kartli, Kakheti, ethnic-population, dynasty, predecessor, successor, "
            "or modern-state alias resolves to this identity, and it inherits no "
            "Elo from any such polity."
        ),
        "source_ids": sorted(_SOURCE_BY_ID),
    },
)


WAVE8_GEORGIAN_UPRISING_REQUIRED_EXISTING_ENTITIES: dict[
    str, dict[str, Any]
] = {
    _SAFAVID_ID: {
        "name": "Safavid Iran",
        "kind": "empire",
        "start_year": 1501,
        "end_year": 1736,
    }
}


WAVE8_GEORGIAN_UPRISING_ROW_HASHES: dict[str, str] = {
    "hced-Marabda1625-1": (
        "5a7692f5ee88d488d2b16ad72c37e895ee19348823b8fcbeb737020a3f95abf2"
    ),
    "hced-Marqopi1625-1": (
        "dcbbafc3e6bc8ff1f99b7de9f8f8080aea7025c895b78015a966f0e4c37b3272"
    ),
}

WAVE8_GEORGIAN_UPRISING_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_GEORGIAN_UPRISING_ROW_HASHES
)

WAVE8_GEORGIAN_UPRISING_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "03c27677cedba86f0040739ef60641a5132045e7e51d5309ee7ebce306f09697"
    ),
    "events_touched": 2,
    "label": _EXACT_LABEL,
    "sole_blocker_events": 2,
    "zero_time_valid_candidates": 2,
}


def _canonical(name: str, date_text: str, granularity: str) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:1625:1625",
        "date_precision": "source_stated_day_calendar_unspecified",
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": 1625,
        "year_high": 1625,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    outcome_source_ids: Iterable[str],
    reviewed_outcome: str,
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_GEORGIAN_UPRISING_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "kartli_kakheti_uprising_1625",
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "anti_imperial_revolt",
        "confidence": confidence,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "source_date_override": False,
        "calendar_style": "unspecified_in_cited_sources",
        "actor_override": "candidate_keyed_uprising_force_and_existing_safavid",
        "reviewed_outcome": reviewed_outcome,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_GEORGIAN_UPRISING_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Marqopi1625-1": _contract(
        "hced-Marqopi1625-1",
        _canonical(
            "Battle of Martqopi",
            "25 March 1625; calendar style unspecified in the cited sources",
            "single_battle_in_the_kartli_kakheti_uprising",
        ),
        [_UPRISING_FORCE_ID],
        [_SAFAVID_ID],
        [
            "wave8_georgian_uprising_georgian_encyclopedia_martqopi",
            "wave8_georgian_uprising_mikaberidze_marabda",
        ],
        "Kartli-Kakheti uprising-force tactical victory over the Safavid army",
        (
            "The Georgian Encyclopedia records that the uprising force entered "
            "the Safavid camp and ended the full day's fighting in victory; the "
            "independent historical-dictionary account likewise describes the "
            "Safavid army as annihilated. The cited day is retained as source "
            "text because neither citation identifies its calendar style. Only "
            "the tactical battle is rated."
        ),
        confidence=0.96,
    ),
    "hced-Marabda1625-1": _contract(
        "hced-Marabda1625-1",
        _canonical(
            "Battle of Marabda",
            "1 July 1625; calendar style unspecified in the cited sources",
            "single_battle_in_the_kartli_kakheti_uprising",
        ),
        [_SAFAVID_ID],
        [_UPRISING_FORCE_ID],
        [
            "wave8_georgian_uprising_georgian_encyclopedia_marabda",
            "wave8_georgian_uprising_mikaberidze_marabda",
        ],
        "Safavid tactical victory over the Kartli-Kakheti uprising force",
        (
            "The Georgian Encyclopedia describes the Georgian line breaking "
            "after Safavid forces regrouped and received reinforcements, and the "
            "historical dictionary independently records the Georgian defeat. "
            "The cited day is retained as source text because neither citation "
            "identifies its calendar style. The later guerrilla resistance and "
            "Shah Abbas's failure to destroy the eastern Georgian states are not "
            "converted into this battle's outcome."
        ),
        confidence=0.96,
    ),
}


WAVE8_GEORGIAN_UPRISING_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS = frozenset(
    WAVE8_GEORGIAN_UPRISING_CONTRACTS
)
WAVE8_GEORGIAN_UPRISING_RESERVED_IDS = WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS
WAVE8_GEORGIAN_UPRISING_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS
)
WAVE8_GEORGIAN_UPRISING_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_GEORGIAN_UPRISING_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the named battlefield in eastern "
            "Georgia but do not independently audit HCED's exact coordinate; "
            "retain the country assertion and withhold the point."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(
        WAVE8_GEORGIAN_UPRISING_CONTRACTS.items()
    )
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_GEORGIAN_UPRISING_CONTRACTS,
        "entities": WAVE8_GEORGIAN_UPRISING_ENTITIES,
        "funnel": WAVE8_GEORGIAN_UPRISING_FUNNEL_AUDIT,
        "holds": WAVE8_GEORGIAN_UPRISING_HOLDS,
        "location_reasons": WAVE8_GEORGIAN_UPRISING_LOCATION_QUARANTINE_REASONS,
        "required_existing_entities": (
            WAVE8_GEORGIAN_UPRISING_REQUIRED_EXISTING_ENTITIES
        ),
        "row_hashes": WAVE8_GEORGIAN_UPRISING_ROW_HASHES,
        "sources": WAVE8_GEORGIAN_UPRISING_SOURCES,
    }


def wave8_georgian_uprising_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_GEORGIAN_UPRISING_FINAL_AUDIT_SIGNATURE = (
    "0eaa8d2d449b8852f2b2455e381221bbe75f54e4c32ea70deee403acce771424"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_GEORGIAN_UPRISING_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_GEORGIAN_UPRISING_ENTITIES
    }
    if set(entity_by_id) != {_UPRISING_FORCE_ID}:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    uprising = entity_by_id[_UPRISING_FORCE_ID]
    if (
        uprising["aliases"]
        or (uprising["start_year"], uprising["end_year"]) != (1625, 1625)
    ):
        raise ValueError(f"{_LANE_NAME} uprising identity escaped its boundary")
    if not _is_sorted_unique(uprising["source_ids"]):
        raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
    if set(uprising["source_ids"]) != source_ids:
        raise ValueError(f"{_LANE_NAME} entity evidence closure failed")
    if WAVE8_GEORGIAN_UPRISING_RESERVED_IDS != set(
        WAVE8_GEORGIAN_UPRISING_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_GEORGIAN_UPRISING_HOLDS:
        raise ValueError(f"{_LANE_NAME} unexpected hold inventory")
    if WAVE8_GEORGIAN_UPRISING_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_GEORGIAN_UPRISING_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_GEORGIAN_UPRISING_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    allowed_actors = {_UPRISING_FORCE_ID, _SAFAVID_ID}
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_GEORGIAN_UPRISING_CONTRACTS.items():
        if contract["disposition"] != "promote" or contract["result_type"] != "win":
            raise ValueError(f"{_LANE_NAME} disposition drift: {candidate_id}")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} outcome override drift: {candidate_id}")
        if contract["source_date_override"]:
            raise ValueError(f"{_LANE_NAME} unexpected year override: {candidate_id}")
        actors = {
            *map(str, contract["side_1_entity_ids"]),
            *map(str, contract["side_2_entity_ids"]),
        }
        if actors != allowed_actors:
            raise ValueError(f"{_LANE_NAME} exact actor drift: {candidate_id}")
        canonical = contract["canonical_event"]
        if (
            canonical["year_low"],
            canonical["year_high"],
            canonical["date_precision"],
            contract["calendar_style"],
        ) != (
            1625,
            1625,
            "source_stated_day_calendar_unspecified",
            "unspecified_in_cited_sources",
        ):
            raise ValueError(f"{_LANE_NAME} date treatment drift: {candidate_id}")
        if "calendar style unspecified" not in str(canonical["date_text"]):
            raise ValueError(f"{_LANE_NAME} calendar caveat missing: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence order drift: {candidate_id}")
        if set(outcomes) != set(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if (
        wave8_georgian_uprising_audit_signature()
        != WAVE8_GEORGIAN_UPRISING_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_georgian_uprising_existing_entities(
    release_entities: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    for entity_id, expected in (
        WAVE8_GEORGIAN_UPRISING_REQUIRED_EXISTING_ENTITIES.items()
    ):
        entity = release_entities.get(entity_id)
        if entity is None:
            raise ValueError(f"{_LANE_NAME} missing existing identity {entity_id}")
        projection = {key: entity.get(key) for key in expected}
        if projection != expected:
            raise ValueError(
                f"{_LANE_NAME} existing identity drift for {entity_id}: {projection}"
            )
    return {
        "required_existing_entities": len(
            WAVE8_GEORGIAN_UPRISING_REQUIRED_EXISTING_ENTITIES
        )
    }


def validate_wave8_georgian_uprising_queue_contracts(
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
    if exact_ids != WAVE8_GEORGIAN_UPRISING_EXPECTED_CANDIDATE_IDS or len(
        exact
    ) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_GEORGIAN_UPRISING_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            row.get("year_low"),
            row.get("year_best"),
            row.get("year_high"),
        ) != (1625, 1625, 1625):
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if row.get("winner_raw") not in {
            row.get("side_1_raw"),
            row.get("side_2_raw"),
        }:
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if normalize_label(row.get("winner_raw")) in {
            "draw",
            "inconclusive",
            "stalemate",
            "unknown",
        }:
            raise ValueError(f"{_LANE_NAME} unknown/draw outcome drift: {candidate_id}")
        if row.get("winner_loser_complete") is not True or row.get(
            "massacre_raw"
        ) != "No":
            raise ValueError(
                f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}"
            )
        if row.get("do_not_rate_automatically") is not True:
            raise ValueError(f"{_LANE_NAME} discovery guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_GEORGIAN_UPRISING_CONTRACTS,
        WAVE8_GEORGIAN_UPRISING_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_georgian_uprising_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    labels = [
        row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL
    ]
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
    if checks != WAVE8_GEORGIAN_UPRISING_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed: {checks}")
    return {
        "events_touched": checks["events_touched"],
        "sole_blocker_events": checks["sole_blocker_events"],
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


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Marqopi1625-1": {
        "Marqopi",
        "Martqopi",
        "Martkopi",
        "Battle of Martqopi",
    },
    "hced-Marabda1625-1": {"Marabda", "Battle of Marabda"},
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (1625, normalize_label(alias))
    for aliases in _EVENT_ALIASES.values()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_georgian_uprising_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_georgian_uprising_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_GEORGIAN_UPRISING_RESERVED_IDS
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
        if event.get("hced_candidate_id")
        not in WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS
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


def install_wave8_georgian_uprising_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_GEORGIAN_UPRISING_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_georgian_uprising_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_GEORGIAN_UPRISING_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_GEORGIAN_UPRISING_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_GEORGIAN_UPRISING_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_georgian_uprising_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_georgian_uprising_queue_contracts(hced_rows)
    validate_wave8_georgian_uprising_existing_entities(release_entities)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_GEORGIAN_UPRISING_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_georgian_uprising_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_GEORGIAN_UPRISING_CONTRACTS.values(),
                    *WAVE8_GEORGIAN_UPRISING_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_georgian_uprising_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_GEORGIAN_UPRISING_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "holds": len(WAVE8_GEORGIAN_UPRISING_HOLDS),
        "new_entities": len(WAVE8_GEORGIAN_UPRISING_ENTITIES),
        "new_sources": len(WAVE8_GEORGIAN_UPRISING_SOURCES),
        "newly_rated_events": len(WAVE8_GEORGIAN_UPRISING_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_GEORGIAN_UPRISING_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_GEORGIAN_UPRISING_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_GEORGIAN_UPRISING_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_georgian_uprising_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_GEORGIAN_UPRISING_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_GEORGIAN_UPRISING_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_georgian_uprising_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_georgian_uprising_counts(),
        "cohorts": wave8_georgian_uprising_cohort_counts(),
        "final_audit_signature": WAVE8_GEORGIAN_UPRISING_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(
            WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS
        ),
    }


_validate_static()
