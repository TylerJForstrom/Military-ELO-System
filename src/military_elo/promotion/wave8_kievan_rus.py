"""Candidate-keyed audit of HCED's six unresolved ``Kiev`` rows.

Only the two tenth-century battles are promoted.  They are directly tied to
Sviatoslav's Rus' and independently attest Byzantine tactical victories at
Arcadiopolis and Dorostolon.  The later rows remain staged because ``Kiev`` can
then denote the broad Rus' realm, the Principality of Kiev, or a coalition of
Rurikid princes.  No generic ``Kiev`` alias is opened.
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
    "WAVE8_KIEVAN_RUS_CONTRACT_IDS",
    "WAVE8_KIEVAN_RUS_CONTRACTS",
    "WAVE8_KIEVAN_RUS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_KIEVAN_RUS_ENTITIES",
    "WAVE8_KIEVAN_RUS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_KIEVAN_RUS_FUNNEL_AUDIT",
    "WAVE8_KIEVAN_RUS_HOLD_IDS",
    "WAVE8_KIEVAN_RUS_HOLDS",
    "WAVE8_KIEVAN_RUS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_KIEVAN_RUS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_KIEVAN_RUS_RESERVED_IDS",
    "WAVE8_KIEVAN_RUS_ROW_HASHES",
    "WAVE8_KIEVAN_RUS_SOURCES",
    "install_wave8_kievan_rus_entities",
    "install_wave8_kievan_rus_sources",
    "promote_wave8_kievan_rus_contracts",
    "validate_wave8_kievan_rus_funnel",
    "validate_wave8_kievan_rus_integration_dispositions",
    "validate_wave8_kievan_rus_queue_contracts",
    "wave8_kievan_rus_audit_signature",
    "wave8_kievan_rus_cohort_counts",
    "wave8_kievan_rus_counts",
    "wave8_kievan_rus_metadata",
)


_LANE_NAME = "Wave 8 exact Kievan Rus actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_kievan_rus"
_EVENT_ID_PREFIX = "hced_wave8_kievan_rus_"
_EXACT_LABEL = "kiev"

_KIEVAN_RUS = "clio_ua_kievan_rus_882_b1e5ac40"
_BYZANTINE_EMPIRE = "byzantine_empire"


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
        "evidence_roles": list(evidence_roles),
    }


WAVE8_KIEVAN_RUS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_kievan_rus_encyclopedia_martin",
        "Janet Martin, Kievan Rus, Encyclopedia of Russian History",
        (
            "https://www.encyclopedia.com/history/modern-europe/"
            "russian-soviet-and-cis-history/kievan-rus"
        ),
        "Encyclopedia of Russian History / Gale",
        "edited_reference_work",
        "martin_encyclopedia_russian_history",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_kievan_rus_hanak_sviatoslav",
        "Walter K. Hanak, The Infamous Svjatoslav: Master of Duplicity in War and Peace?",
        (
            "https://deremilitari.org/2014/05/"
            "the-infamous-svjatoslav-master-of-duplicity-in-war-and-peace/"
        ),
        "De Re Militari; originally Catholic University of America Press",
        "scholarly_book_chapter_republication",
        "hanak_sviatoslav_1995",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_kievan_rus_leo_deacon",
        "Leo the Deacon, History, translated by Alice-Mary Talbot and Denis F. Sullivan",
        "https://terpconnect.umd.edu/~sullivan/LeoTheDeacon.pdf",
        "Dumbarton Oaks Research Library and Collection",
        "translated_primary_chronicle_scholarly_edition",
        "leo_deacon_history_talbot_sullivan",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_KIEVAN_RUS_SOURCES}


# Reuse and curate the exact Cliopatria identity already present in the registry.
# The empty alias list is deliberate: the broad label "Kiev" remains closed.
WAVE8_KIEVAN_RUS_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _KIEVAN_RUS,
        "name": "Kievan Rus'",
        "kind": "polity",
        "start_year": 882,
        "end_year": 1240,
        "region": "Eastern Europe",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Curated from the matching time-bounded Cliopatria candidate. Only "
            "fingerprinted, candidate-keyed events with reviewed actors may use "
            "this identity: the source label 'Kiev' is not a global alias and is "
            "not allowed to bridge the later Rus' principalities or coalitions. "
            "Predecessors and successors inherit no Elo."
        ),
        "source_ids": [
            "cliopatria_v020",
            "wave8_kievan_rus_encyclopedia_martin",
            "wave8_kievan_rus_hanak_sviatoslav",
        ],
    },
)


WAVE8_KIEVAN_RUS_ROW_HASHES: dict[str, str] = {
    "hced-Alta1068-1": "251585f1a2485fb52b9567ab1612729a274308d73de2715115a47e2971d438d2",
    "hced-Arcadiopolis970-1": "8204e16931d0ff9b23645fdaf6b0a7793aeb5626b04dc40c420edfb771cc9599",
    "hced-Dorostalon971-1": "6815706c60667a009a2a9d986a1464a66b10a373247153fa69f9c3c163c2f3b7",
    "hced-Kiev1240-1": "a4c5b70c24546af959be81d205dbd896b18e4cedd1fe713a7f31b5409fa62f24",
    "hced-Nemiga1067-1": "b4a61e912ef953a44085002ac05ae9f9a882a1947ed781f5eed738b1494d7f6d",
    "hced-Tripole1093-1": "158d359acd0ad1501b5ca331f1fef4f33f92b53e4f0695ecd19acb7b7ad321c4",
}

WAVE8_KIEVAN_RUS_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "9307ef14d4691d33ba87567bfb225b97de78ffc65481f3b93f19a096764fc72f"
    ),
    "events_touched": 6,
    "label": _EXACT_LABEL,
    "sole_blocker_events": 3,
    "zero_time_valid_candidates": 6,
}


def _canonical(name: str, year: int, granularity: str) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "year",
        "date_text": str(year),
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(
        {
            "wave8_kievan_rus_hanak_sviatoslav",
            "wave8_kievan_rus_leo_deacon",
        }
    )
    return {
        "raw_row_sha256": WAVE8_KIEVAN_RUS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "sviatoslav_byzantine_war_970_971",
        "side_1_entity_ids": [_BYZANTINE_EMPIRE],
        "side_2_entity_ids": [_KIEVAN_RUS],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate",
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
        "actor_override": "candidate_keyed_kievan_rus_under_sviatoslav",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_KIEVAN_RUS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Arcadiopolis970-1": _contract(
        "hced-Arcadiopolis970-1",
        _canonical(
            "Battle of Arcadiopolis",
            970,
            "single_land_battle_in_sviatoslav_byzantine_war",
        ),
        (
            "Leo the Deacon describes Bardas Skleros's ambush, the Rus-led "
            "force breaking formation, and the Byzantine pursuit; Hanak's "
            "source-critical account likewise identifies a sound Byzantine rout "
            "and explains why the contrary Rus' annalistic claim is rejected. "
            "Only the tactical result is rated, not every allied contingent."
        ),
        confidence=0.90,
    ),
    "hced-Dorostalon971-1": _contract(
        "hced-Dorostalon971-1",
        _canonical(
            "Siege and Battle of Dorostolon",
            971,
            "three_month_siege_and_terminal_battle_at_dorostolon",
        ),
        (
            "Leo the Deacon records the Roman battlefield victory, Sviatoslav's "
            "request for terms, and the surrender of Dorostolon; Hanak independently "
            "records the three-month siege, 21 July surrender, evacuation, and "
            "abandonment of Bulgaria. The contract rates that attested tactical "
            "defeat without inferring a broader strategic termination."
        ),
        confidence=0.96,
    ),
}


def _hold(candidate_id: str, reason_code: str, audit_note: str) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_KIEVAN_RUS_ROW_HASHES[candidate_id],
        "cohort": "later_kiev_identity_holds",
        "disposition": "hold",
        "reason_code": reason_code,
        "evidence_refs": ["wave8_kievan_rus_encyclopedia_martin"],
        "audit_note": audit_note,
    }


WAVE8_KIEVAN_RUS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Nemiga1067-1": _hold(
        "hced-Nemiga1067-1",
        "kiev_label_collapses_three_prince_coalition",
        (
            "The row's 'Kiev' winner does not uniquely identify the force of the "
            "three Yaroslavichi princes or distinguish the broad Rus' realm from "
            "the Principality of Kiev. Polotsk also lacks a reviewed opposing "
            "identity in this lane, so no outcome is promoted."
        ),
    ),
    "hced-Alta1068-1": _hold(
        "hced-Alta1068-1",
        "kiev_label_collapses_three_prince_coalition",
        (
            "The Alta defeat involved the Yaroslavichi coalition rather than an "
            "unambiguous single Kiev polity, and the Pecheneg side is unresolved. "
            "The complete winner string is retained but not rated."
        ),
    ),
    "hced-Tripole1093-1": _hold(
        "hced-Tripole1093-1",
        "later_rurikid_coalition_and_cuman_identity_unresolved",
        (
            "The place-only row collapses multiple Rus' princely forces into "
            "'Kiev' and supplies an unresolved Kuman Khanate opponent. Exact "
            "belligerent attribution requires a separate source-critical audit."
        ),
    ),
    "hced-Kiev1240-1": _hold(
        "hced-Kiev1240-1",
        "principality_not_broad_kievan_rus_and_massacre_review_pending",
        (
            "The 1240 defense belongs to the late Principality of Kiev rather "
            "than automatically to the broad Kievan Rus candidate. The Mongol "
            "army identity and HCED's battle-followed-by-massacre classification "
            "also require their own reviewed contract."
        ),
    ),
}

WAVE8_KIEVAN_RUS_CONTRACT_IDS = frozenset(WAVE8_KIEVAN_RUS_CONTRACTS)
WAVE8_KIEVAN_RUS_HOLD_IDS = frozenset(WAVE8_KIEVAN_RUS_HOLDS)
WAVE8_KIEVAN_RUS_RESERVED_IDS = frozenset(
    {*WAVE8_KIEVAN_RUS_CONTRACT_IDS, *WAVE8_KIEVAN_RUS_HOLD_IDS}
)
WAVE8_KIEVAN_RUS_POINT_QUARANTINE_ADDITIONS = WAVE8_KIEVAN_RUS_CONTRACT_IDS
WAVE8_KIEVAN_RUS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_KIEVAN_RUS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the named battlefield and modern "
            "country but do not independently verify HCED's exact coordinate; "
            "retain the country assertion and withhold the point."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_KIEVAN_RUS_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_KIEVAN_RUS_CONTRACTS,
        "entities": WAVE8_KIEVAN_RUS_ENTITIES,
        "funnel": WAVE8_KIEVAN_RUS_FUNNEL_AUDIT,
        "holds": WAVE8_KIEVAN_RUS_HOLDS,
        "location_reasons": WAVE8_KIEVAN_RUS_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_KIEVAN_RUS_ROW_HASHES,
        "sources": WAVE8_KIEVAN_RUS_SOURCES,
    }


def wave8_kievan_rus_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_KIEVAN_RUS_FINAL_AUDIT_SIGNATURE = (
    "062bce68f7595cb5519173ad0ca7747609ce0931502331dc8dd65112bc52eeb0"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = {str(entity["id"]) for entity in WAVE8_KIEVAN_RUS_ENTITIES}
    if len(source_ids) != len(WAVE8_KIEVAN_RUS_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if entity_ids != {_KIEVAN_RUS}:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_KIEVAN_RUS_CONTRACT_IDS & WAVE8_KIEVAN_RUS_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_KIEVAN_RUS_RESERVED_IDS != set(WAVE8_KIEVAN_RUS_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_KIEVAN_RUS_POINT_QUARANTINE_ADDITIONS != WAVE8_KIEVAN_RUS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_KIEVAN_RUS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_KIEVAN_RUS_LOCATION_QUARANTINE_REASONS) != WAVE8_KIEVAN_RUS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    entity = WAVE8_KIEVAN_RUS_ENTITIES[0]
    if entity["aliases"] or (entity["start_year"], entity["end_year"]) != (882, 1240):
        raise ValueError(f"{_LANE_NAME} identity boundary or alias drift")
    if normalize_label(entity["name"]) == _EXACT_LABEL:
        raise ValueError(f"{_LANE_NAME} generic Kiev label opened")
    if not _is_sorted_unique(entity["source_ids"]):
        raise ValueError(f"{_LANE_NAME} entity evidence order drift")

    used_sources = set(map(str, entity["source_ids"])) & source_ids
    allowed_actors = {_BYZANTINE_EMPIRE, _KIEVAN_RUS}
    for candidate_id, contract in WAVE8_KIEVAN_RUS_CONTRACTS.items():
        if contract["disposition"] != "promote" or contract["result_type"] != "win":
            raise ValueError(f"{_LANE_NAME} disposition drift: {candidate_id}")
        if contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} winner-side drift: {candidate_id}")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} outcome override drift: {candidate_id}")
        actors = {
            *map(str, contract["side_1_entity_ids"]),
            *map(str, contract["side_2_entity_ids"]),
        }
        if actors != allowed_actors:
            raise ValueError(f"{_LANE_NAME} exact actor drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence order drift: {candidate_id}")
        if set(outcomes) != set(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        low = int(contract["canonical_event"]["year_low"])
        high = int(contract["canonical_event"]["year_high"])
        if not (882 <= low <= high <= 1240):
            raise ValueError(f"{_LANE_NAME} identity-window drift: {candidate_id}")
        used_sources.update(evidence)

    for candidate_id, hold in WAVE8_KIEVAN_RUS_HOLDS.items():
        if hold["disposition"] != "hold" or not hold["reason_code"]:
            raise ValueError(f"{_LANE_NAME} hold drift: {candidate_id}")
        if not set(map(str, hold["evidence_refs"])) <= source_ids:
            raise ValueError(f"{_LANE_NAME} hold evidence drift: {candidate_id}")
        used_sources.update(map(str, hold["evidence_refs"]))

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_kievan_rus_audit_signature() != WAVE8_KIEVAN_RUS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_kievan_rus_queue_contracts(
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
    if exact_ids != WAVE8_KIEVAN_RUS_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_KIEVAN_RUS_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("year_low") != row.get("year_high") or row.get("year_best") != row.get(
            "year_low"
        ):
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if row.get("winner_raw") not in {row.get("side_1_raw"), row.get("side_2_raw")}:
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True:
            raise ValueError(f"{_LANE_NAME} complete-outcome guard changed: {candidate_id}")
    for candidate_id in WAVE8_KIEVAN_RUS_CONTRACT_IDS:
        if by_id[candidate_id].get("massacre_raw") != "No":
            raise ValueError(f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_KIEVAN_RUS_CONTRACTS,
        WAVE8_KIEVAN_RUS_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_kievan_rus_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
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
    if checks != WAVE8_KIEVAN_RUS_FUNNEL_AUDIT:
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
    "hced-Arcadiopolis970-1": {
        "Arcadiopolis",
        "Arkadiopolis",
        "Battle of Arcadiopolis",
    },
    "hced-Dorostalon971-1": {
        "Dorostalon",
        "Dorostolon",
        "Dorystolon",
        "Siege of Dorostolon",
        "Siege and Battle of Dorostolon",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(WAVE8_KIEVAN_RUS_CONTRACTS[candidate_id]["canonical_event"]["year_low"]),
        normalize_label(alias),
    )
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_kievan_rus_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_kievan_rus_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_KIEVAN_RUS_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_KIEVAN_RUS_CONTRACT_IDS
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


def install_wave8_kievan_rus_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_KIEVAN_RUS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_kievan_rus_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_KIEVAN_RUS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_KIEVAN_RUS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_KIEVAN_RUS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_kievan_rus_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_kievan_rus_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_KIEVAN_RUS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_kievan_rus_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_KIEVAN_RUS_CONTRACTS.values(),
                    *WAVE8_KIEVAN_RUS_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_kievan_rus_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": len(WAVE8_KIEVAN_RUS_HOLDS),
        "new_entities": len(WAVE8_KIEVAN_RUS_ENTITIES),
        "new_sources": len(WAVE8_KIEVAN_RUS_SOURCES),
        "newly_rated_events": len(WAVE8_KIEVAN_RUS_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_KIEVAN_RUS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_KIEVAN_RUS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_KIEVAN_RUS_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_kievan_rus_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_kievan_rus_counts(),
        "cohorts": wave8_kievan_rus_cohort_counts(),
        "final_audit_signature": WAVE8_KIEVAN_RUS_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_KIEVAN_RUS_CONTRACT_IDS),
        "hold_candidate_ids": sorted(WAVE8_KIEVAN_RUS_HOLD_IDS),
    }


_validate_static()
