"""Candidate-keyed audit of HCED's three ``Catholic Rebels`` rows.

The raw label joins unrelated forces in the 1549 Western Rebellion and the
1571 Marian civil war.  This lane therefore opens no generic Catholic or rebel
alias.  It reuses the Kingdom of England for the two 1549 loyalist sides and
creates three narrow identities: the Western insurgent army, Adam Gordon's
Marian force at Craibstone, and the Forbes/Regent force that opposed it.

Clyst St Mary and Sampford Courtenay preserve HCED's loyalist victories.
Craibstone is promoted only with a declared source-outcome reversal: official
Scottish heritage and gazetteer records agree that Gordon's Marian force, not
the Forbes/Regent force represented by HCED's ``Scotland`` side, won.  No
strategic result, religious-population rating, or cross-conflict continuity is
inferred.
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
    "WAVE8_CATHOLIC_REBELS_CONTRACT_IDS",
    "WAVE8_CATHOLIC_REBELS_CONTRACTS",
    "WAVE8_CATHOLIC_REBELS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_CATHOLIC_REBELS_ENTITIES",
    "WAVE8_CATHOLIC_REBELS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_CATHOLIC_REBELS_FUNNEL_AUDIT",
    "WAVE8_CATHOLIC_REBELS_HOLD_IDS",
    "WAVE8_CATHOLIC_REBELS_HOLDS",
    "WAVE8_CATHOLIC_REBELS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_CATHOLIC_REBELS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_CATHOLIC_REBELS_RESERVED_IDS",
    "WAVE8_CATHOLIC_REBELS_ROW_HASHES",
    "WAVE8_CATHOLIC_REBELS_SOURCES",
    "install_wave8_catholic_rebels_entities",
    "install_wave8_catholic_rebels_sources",
    "promote_wave8_catholic_rebels_contracts",
    "validate_wave8_catholic_rebels_funnel",
    "validate_wave8_catholic_rebels_integration_dispositions",
    "validate_wave8_catholic_rebels_queue_contracts",
    "wave8_catholic_rebels_audit_signature",
    "wave8_catholic_rebels_cohort_counts",
    "wave8_catholic_rebels_counts",
    "wave8_catholic_rebels_metadata",
)


_LANE_NAME = "Wave 8 exact Catholic Rebels actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_catholic_rebels"
_EVENT_ID_PREFIX = "hced_wave8_catholic_rebels_"
_EXACT_LABELS = frozenset({"catholic rebels"})
_WESTERN_COHORT = "western_rebellion_catholic_rebels_1549"
_CRAIBSTONE_COHORT = "marian_civil_war_catholic_rebels_1571"

_KINGDOM_ENGLAND = "kingdom_england"
_WESTERN_REBELS = "western_rebellion_insurgent_army_1549"
_GORDON_MARIAN_FORCE = "adam_gordon_marian_force_craibstone_1571"
_FORBES_REGENT_FORCE = "forbes_regent_force_craibstone_1571"


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
        "accessed": "2026-07-17",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_CATHOLIC_REBELS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_catholic_rebels_battlefields_clyst",
        "Battle of Clyst St Mary, 4 August 1549",
        (
            "https://www.battlefieldstrust.com/resource-centre/early-modern/"
            "battleview.asp?BattleFieldId=108"
        ),
        "Battlefields Trust",
        "expert_battlefield_record",
        "battlefields_trust_western_rebellion",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_catholic_rebels_battlefields_sampford",
        "Battle of Sampford Courtenay, 18 August 1549",
        (
            "https://www.battlefieldstrust.com/resource-centre/"
            "battleview.asp?BattleFieldId=110"
        ),
        "Battlefields Trust",
        "expert_battlefield_record",
        "battlefields_trust_western_rebellion",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_catholic_rebels_hodgkins_thesis",
        "Rebellion and Warfare in the Tudor State",
        (
            "https://etheses.whiterose.ac.uk/id/eprint/6439/1/"
            "Alexander%20Hodgkins%20eThesis.pdf"
        ),
        "University of Leeds / White Rose eTheses",
        "doctoral_historical_thesis",
        "hodgkins_tudor_rebellion_thesis",
        [
            "identity_boundary_or_context_reference",
            "outcome_consistency_crosscheck",
        ],
    ),
    _source(
        "wave8_catholic_rebels_rose_troup",
        "The Western Rebellion of 1549",
        "https://archive.org/details/westernrebellion00rose",
        "Frances Rose-Troup / Internet Archive",
        "scholarly_campaign_monograph",
        "rose_troup_western_rebellion_1913",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_catholic_rebels_stoyle_western_rising",
        "The Western Rising of 1549",
        (
            "https://books.google.com/books/about/"
            "The_Western_Rising_of_1549.html?id=XvR-EAAAQBAJ"
        ),
        "Mark Stoyle / Yale University Press",
        "scholarly_campaign_monograph",
        "stoyle_western_rising_1549",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_catholic_rebels_hes_craibstone",
        "Aberdeen, Crabe Stone",
        "https://www.trove.scot/place/20119",
        "Historic Environment Scotland / trove.scot",
        "national_historic_environment_record",
        "historic_environment_scotland_craibstone",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_catholic_rebels_nls_gazetteer",
        "Ordnance Gazetteer of Scotland: Aberdeen and Craibstone",
        "https://deriv.nls.uk/dcn23/9736/97368777.23.pdf",
        "National Library of Scotland",
        "digitized_historical_gazetteer",
        "groome_ordnance_gazetteer_scotland",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_catholic_rebels_scottish_state_papers",
        "Calendar of the State Papers Relating to Scotland, 1571-1574",
        (
            "https://books.google.com/books/about/"
            "Calendar_of_the_State_Papers_Relating_to.html?id=kW79vwEACAAJ"
        ),
        "Great Britain Public Record Office / Google Books",
        "edited_primary_source_calendar",
        "calendar_state_papers_scotland_1571_1574",
        [
            "identity_boundary_or_context_reference",
            "outcome_consistency_crosscheck",
        ],
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_CATHOLIC_REBELS_SOURCES
}


WAVE8_CATHOLIC_REBELS_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _WESTERN_REBELS,
        "name": "Western Rebellion insurgent army (1549)",
        "kind": "conflict_bounded_rebel_force",
        "start_year": 1549,
        "end_year": 1549,
        "region": "Devon and Cornwall",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the armed Devonian and Cornish insurgent force in the "
            "Western or Prayer Book Rebellion from its 1549 mobilization through "
            "the final field action at Sampford Courtenay. It is not a rating for "
            "Catholics, Cornwall, Devon, later religious resistance, or a modern "
            "community, and it inherits no Elo from any of them."
        ),
        "source_ids": [
            "wave8_catholic_rebels_battlefields_clyst",
            "wave8_catholic_rebels_battlefields_sampford",
            "wave8_catholic_rebels_hodgkins_thesis",
            "wave8_catholic_rebels_rose_troup",
            "wave8_catholic_rebels_stoyle_western_rising",
        ],
    },
    {
        "id": _GORDON_MARIAN_FORCE,
        "name": "Adam Gordon's Marian force at Craibstone (1571)",
        "kind": "engagement_bounded_civil_war_force",
        "start_year": 1571,
        "end_year": 1571,
        "region": "Aberdeen and north-eastern Scotland",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to Adam Gordon of Auchindoun's Gordon and allied force at "
            "Craibstone on 20 November 1571 while fighting in Mary, Queen of "
            "Scots' cause. It is not a generic Gordon clan, Catholic, Marian, or "
            "Scottish polity and carries no rating beyond this reviewed action."
        ),
        "source_ids": [
            "wave8_catholic_rebels_hes_craibstone",
            "wave8_catholic_rebels_nls_gazetteer",
            "wave8_catholic_rebels_scottish_state_papers",
        ],
    },
    {
        "id": _FORBES_REGENT_FORCE,
        "name": "Forbes and Regent force at Craibstone (1571)",
        "kind": "engagement_bounded_civil_war_force",
        "start_year": 1571,
        "end_year": 1571,
        "region": "Aberdeen and north-eastern Scotland",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the Forbes force and attached Regent soldiers that "
            "opposed Adam Gordon at Craibstone on 20 November 1571. It is not "
            "the whole Kingdom of Scotland, a generic Forbes clan identity, or "
            "every supporter of James VI, and it inherits no national Elo."
        ),
        "source_ids": [
            "wave8_catholic_rebels_hes_craibstone",
            "wave8_catholic_rebels_nls_gazetteer",
            "wave8_catholic_rebels_scottish_state_papers",
        ],
    },
)


WAVE8_CATHOLIC_REBELS_ROW_HASHES: dict[str, str] = {
    "hced-Craibstane1571-1": (
        "49b8343ca88f331e56560ac42959631b8d3e18cf5a392d56f59282f1529a9541"
    ),
    "hced-Sampford Courtenay1549-1": (
        "66529d57268a49ba6a60449a012c46dc8d74d13552ac204219c9f4f6b39aadb9"
    ),
    "hced-St Marys Clyst1549-1": (
        "53e51ac6c2f53a5a23b2c1ecd3ce81353301ac992855ef77f57555bc4825a9ed"
    ),
}

WAVE8_CATHOLIC_REBELS_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "catholic rebels": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "d3c9642b88174e8a0759b85351f1eeb192b648507662a65380963783f060796f"
        ),
        "events_touched": 3,
        "label": "catholic rebels",
        "rated_counterpart_entities": 2,
        "sole_blocker_events": 3,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 3,
        "zero_time_valid_candidates": 3,
    }
}


def _canonical(name: str, year: int, date_text: str) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "year",
        "date_text": date_text,
        "granularity": "pitched_battle",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_sources: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    winner_side: int,
    source_outcome_override: bool,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_sources)))
    return {
        "raw_row_sha256": WAVE8_CATHOLIC_REBELS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1_entity_ids)),
        "side_2_entity_ids": list(map(str, side_2_entity_ids)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": winner_side,
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
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": source_outcome_override,
        "actor_override": "candidate_keyed_event_bounded_civil_war_forces",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_CATHOLIC_REBELS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-St Marys Clyst1549-1": _contract(
        "hced-St Marys Clyst1549-1",
        _canonical(
            "Battle of Clyst St Mary",
            1549,
            "4 August 1549 in the Battlefields Trust reconstruction; year-only "
            "precision retained because older narratives differ by one day",
        ),
        _WESTERN_COHORT,
        [_KINGDOM_ENGLAND],
        [_WESTERN_REBELS],
        {
            "wave8_catholic_rebels_battlefields_clyst",
            "wave8_catholic_rebels_hodgkins_thesis",
            "wave8_catholic_rebels_rose_troup",
            "wave8_catholic_rebels_stoyle_western_rising",
        },
        {
            "wave8_catholic_rebels_battlefields_clyst",
            "wave8_catholic_rebels_rose_troup",
        },
        (
            "The reviewed battlefield record and campaign history independently "
            "support a loyalist tactical victory over the Western insurgents. "
            "The later killing of prisoners at Clyst Heath is a separate atrocity "
            "and is not converted into a competitive result here."
        ),
        confidence=0.98,
        winner_side=1,
        source_outcome_override=False,
    ),
    "hced-Sampford Courtenay1549-1": _contract(
        "hced-Sampford Courtenay1549-1",
        _canonical(
            "Battle of Sampford Courtenay",
            1549,
            "18 August 1549 in the Battlefields Trust reconstruction; year-only "
            "precision retained because published chronologies differ",
        ),
        _WESTERN_COHORT,
        [_KINGDOM_ENGLAND],
        [_WESTERN_REBELS],
        {
            "wave8_catholic_rebels_battlefields_sampford",
            "wave8_catholic_rebels_hodgkins_thesis",
            "wave8_catholic_rebels_rose_troup",
            "wave8_catholic_rebels_stoyle_western_rising",
        },
        {
            "wave8_catholic_rebels_battlefields_sampford",
            "wave8_catholic_rebels_rose_troup",
        },
        (
            "The reviewed battlefield record and campaign history independently "
            "support the loyalist overrunning of the insurgent camp and final "
            "field defeat. Later reprisals and executions are not rated."
        ),
        confidence=0.98,
        winner_side=1,
        source_outcome_override=False,
    ),
    "hced-Craibstane1571-1": _contract(
        "hced-Craibstane1571-1",
        _canonical(
            "Battle of Craibstone",
            1571,
            "20 November 1571; year-only precision retained to match HCED",
        ),
        _CRAIBSTONE_COHORT,
        [_FORBES_REGENT_FORCE],
        [_GORDON_MARIAN_FORCE],
        {
            "wave8_catholic_rebels_hes_craibstone",
            "wave8_catholic_rebels_nls_gazetteer",
            "wave8_catholic_rebels_scottish_state_papers",
        },
        {
            "wave8_catholic_rebels_hes_craibstone",
            "wave8_catholic_rebels_nls_gazetteer",
        },
        (
            "HCED's result is explicitly reversed. Historic Environment Scotland "
            "and the independent gazetteer record both identify the Gordons as "
            "victors over the Forbes force. The generic Scotland/Catholic labels "
            "are replaced with the two engagement-bounded civil-war forces."
        ),
        confidence=0.97,
        winner_side=2,
        source_outcome_override=True,
    ),
}

WAVE8_CATHOLIC_REBELS_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_CATHOLIC_REBELS_CONTRACT_IDS = frozenset(WAVE8_CATHOLIC_REBELS_CONTRACTS)
WAVE8_CATHOLIC_REBELS_HOLD_IDS = frozenset(WAVE8_CATHOLIC_REBELS_HOLDS)
WAVE8_CATHOLIC_REBELS_RESERVED_IDS = frozenset(
    {*WAVE8_CATHOLIC_REBELS_CONTRACT_IDS, *WAVE8_CATHOLIC_REBELS_HOLD_IDS}
)
WAVE8_CATHOLIC_REBELS_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_CATHOLIC_REBELS_CONTRACT_IDS
)
WAVE8_CATHOLIC_REBELS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_CATHOLIC_REBELS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the named action and modern United "
            "Kingdom jurisdiction, but their grid/site records are not bound into "
            "the release's closed HCED location-provenance contract. Retain the "
            "source-transcribed country and withhold the unexplained HCED point."
        ),
        "evidence_refs": sorted(contract["evidence_refs"]),
    }
    for candidate_id, contract in sorted(WAVE8_CATHOLIC_REBELS_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_CATHOLIC_REBELS_CONTRACTS,
        "entities": WAVE8_CATHOLIC_REBELS_ENTITIES,
        "funnel": WAVE8_CATHOLIC_REBELS_FUNNEL_AUDIT,
        "holds": WAVE8_CATHOLIC_REBELS_HOLDS,
        "location_reasons": WAVE8_CATHOLIC_REBELS_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_CATHOLIC_REBELS_ROW_HASHES,
        "sources": WAVE8_CATHOLIC_REBELS_SOURCES,
    }


def wave8_catholic_rebels_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_CATHOLIC_REBELS_FINAL_AUDIT_SIGNATURE = (
    "a7bd59959eb77cf5f21a4e48cde24cbad599f7b645ebeb73f2e3a991edbd2af1"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = {str(entity["id"]) for entity in WAVE8_CATHOLIC_REBELS_ENTITIES}
    if len(source_ids) != len(WAVE8_CATHOLIC_REBELS_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if entity_ids != {
        _WESTERN_REBELS,
        _GORDON_MARIAN_FORCE,
        _FORBES_REGENT_FORCE,
    }:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_CATHOLIC_REBELS_RESERVED_IDS != set(
        WAVE8_CATHOLIC_REBELS_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_CATHOLIC_REBELS_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_CATHOLIC_REBELS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_CATHOLIC_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_CATHOLIC_REBELS_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_CATHOLIC_REBELS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    used_sources: set[str] = set()
    for entity in WAVE8_CATHOLIC_REBELS_ENTITIES:
        if entity["aliases"] or entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} identity boundary or alias drift")
        if normalize_label(entity["name"]) in _EXACT_LABELS:
            raise ValueError(f"{_LANE_NAME} generic label opened")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity evidence order drift")
        used_sources.update(set(map(str, entity["source_ids"])) & source_ids)

    expected_results = {
        "hced-St Marys Clyst1549-1": (1, False),
        "hced-Sampford Courtenay1549-1": (1, False),
        "hced-Craibstane1571-1": (2, True),
    }
    for candidate_id, contract in WAVE8_CATHOLIC_REBELS_CONTRACTS.items():
        winner_side, override = expected_results[candidate_id]
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != winner_side
            or contract["source_outcome_override"] is not override
            or contract["outcome_reversal"] is not override
        ):
            raise ValueError(f"{_LANE_NAME} outcome drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence order drift: {candidate_id}")
        if not set(outcomes) <= set(evidence) or not set(evidence) <= source_ids:
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
        wave8_catholic_rebels_audit_signature()
        != WAVE8_CATHOLIC_REBELS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_catholic_rebels_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) in _EXACT_LABELS
        or normalize_label(row.get("side_2_raw")) in _EXACT_LABELS
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_CATHOLIC_REBELS_RESERVED_IDS or len(exact) != len(
        exact_ids
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_CATHOLIC_REBELS_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
        ):
            raise ValueError(f"{_LANE_NAME} raw outcome changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_CATHOLIC_REBELS_CONTRACTS,
        WAVE8_CATHOLIC_REBELS_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_catholic_rebels_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    rows = {
        str(row.get("label")): row
        for row in funnel.get("labels", [])
        if row.get("label") in _EXACT_LABELS
    }
    if set(rows) != _EXACT_LABELS:
        raise ValueError(f"{_LANE_NAME} funnel label missing")
    row = rows["catholic rebels"]
    checks = {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "label": str(row.get("label")),
        "rated_counterpart_entities": int(row.get("rated_counterpart_entities", -1)),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, row.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
        "zero_time_valid_candidates": int(
            row.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
        ),
    }
    expected = WAVE8_CATHOLIC_REBELS_FUNNEL_AUDIT["catholic rebels"]
    if checks != expected:
        raise ValueError(f"{_LANE_NAME} funnel pin changed: {checks}")
    return {
        "events_touched": expected["events_touched"],
        "sole_blocker_events": expected["sole_blocker_events"],
        "unresolved_side_attempts": expected["unresolved_side_attempts"],
        "zero_time_valid_candidates": expected["zero_time_valid_candidates"],
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


_DUPLICATE_ALIASES: dict[int, set[str]] = {
    1549: {
        "Battle of Clyst St Mary",
        "Clyst St Mary",
        "Clist St Mary",
        "St Marys Clyst",
        "Battle of Sampford Courtenay",
        "Sampford Courtenay",
        "Samford Courtenay",
    },
    1571: {
        "Aberdeen Bridge",
        "Battle of Craibstane",
        "Battle of Craibstone",
        "Crabe Stone",
        "Craibstane",
        "Craibstone",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (year, normalize_label(alias))
    for year, aliases in _DUPLICATE_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_catholic_rebels_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_catholic_rebels_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_CATHOLIC_REBELS_RESERVED_IDS
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
        not in WAVE8_CATHOLIC_REBELS_CONTRACT_IDS
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


def install_wave8_catholic_rebels_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_CATHOLIC_REBELS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_catholic_rebels_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_CATHOLIC_REBELS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_CATHOLIC_REBELS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_CATHOLIC_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_catholic_rebels_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_catholic_rebels_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_CATHOLIC_REBELS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_catholic_rebels_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_CATHOLIC_REBELS_CONTRACTS.values(),
                    *WAVE8_CATHOLIC_REBELS_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_catholic_rebels_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": len(WAVE8_CATHOLIC_REBELS_HOLDS),
        "new_entities": len(WAVE8_CATHOLIC_REBELS_ENTITIES),
        "new_sources": len(WAVE8_CATHOLIC_REBELS_SOURCES),
        "newly_rated_events": len(WAVE8_CATHOLIC_REBELS_CONTRACTS),
        "outcome_overrides": sum(
            bool(contract["source_outcome_override"])
            for contract in WAVE8_CATHOLIC_REBELS_CONTRACTS.values()
        ),
        "point_quarantine_additions": len(
            WAVE8_CATHOLIC_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_CATHOLIC_REBELS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_CATHOLIC_REBELS_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_catholic_rebels_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_catholic_rebels_counts(),
        "cohorts": wave8_catholic_rebels_cohort_counts(),
        "final_audit_signature": WAVE8_CATHOLIC_REBELS_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_CATHOLIC_REBELS_CONTRACT_IDS),
        "hold_candidate_ids": sorted(WAVE8_CATHOLIC_REBELS_HOLD_IDS),
    }


_validate_static()
