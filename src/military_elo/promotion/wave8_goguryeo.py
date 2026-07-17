"""Candidate-keyed audit of HCED's three unresolved ``Koguryo`` rows.

All three rows have complete tactical outcomes and uniquely identify Goguryeo.
The 612 and 645 rows are reviewed Goguryeo victories over Sui and Tang.  The
668 fall of Pyongyang is represented as a Tang-Silla coalition victory because
the independent evidence explicitly places Silla in the siege.  No generic
``Koguryo`` or ``Goguryeo`` alias is opened.
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
    "WAVE8_GOGURYEO_CONTRACT_IDS",
    "WAVE8_GOGURYEO_CONTRACTS",
    "WAVE8_GOGURYEO_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_GOGURYEO_ENTITIES",
    "WAVE8_GOGURYEO_FINAL_AUDIT_SIGNATURE",
    "WAVE8_GOGURYEO_FUNNEL_AUDIT",
    "WAVE8_GOGURYEO_HOLD_IDS",
    "WAVE8_GOGURYEO_HOLDS",
    "WAVE8_GOGURYEO_LOCATION_QUARANTINE_REASONS",
    "WAVE8_GOGURYEO_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_GOGURYEO_RESERVED_IDS",
    "WAVE8_GOGURYEO_ROW_HASHES",
    "WAVE8_GOGURYEO_SOURCES",
    "install_wave8_goguryeo_entities",
    "install_wave8_goguryeo_sources",
    "promote_wave8_goguryeo_contracts",
    "validate_wave8_goguryeo_funnel",
    "validate_wave8_goguryeo_integration_dispositions",
    "validate_wave8_goguryeo_queue_contracts",
    "wave8_goguryeo_audit_signature",
    "wave8_goguryeo_cohort_counts",
    "wave8_goguryeo_counts",
    "wave8_goguryeo_metadata",
)


_LANE_NAME = "Wave 8 exact Goguryeo actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_goguryeo"
_EVENT_ID_PREFIX = "hced_wave8_goguryeo_"
_EXACT_LABEL = "koguryo"

_GOGURYEO = "clio_kr_goguryeo_k_bce36_8b810bef"
_SILLA = "clio_q28456_378_7ba3b7e4"
_SUI = "clio_cn_sui_dyn_587_af2a9518"
_TANG = "clio_cn_tang_dyn_1_623_3e98c37b"


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
        "evidence_roles": list(evidence_roles),
    }


WAVE8_GOGURYEO_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_goguryeo_aks_history",
        "Song Ho-jung et al., A History of Korea",
        (
            "https://contents.history.go.kr/resources/common/pdf/"
            "A%20History%20of%20Korea_The%20Understanding%20Korea%20Series.pdf"
        ),
        "Academy of Korean Studies",
        "scholarly_history",
        "academy_korean_studies_history_2019",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_goguryeo_ahn_645_thesis",
        "Ahn Hee-sang, The 645 Goguryeo-Tang War and Causes of Goguryeo's Victory",
        "https://www.dbpia.co.kr/journal/detail?nodeId=T16061002",
        "Dongguk University / DBpia",
        "graduate_thesis",
        "ahn_goguryeo_tang_war_2022",
        ["outcome"],
    ),
    _source(
        "wave8_goguryeo_hwang_history",
        "Kyung Moon Hwang, A History of Korea: An Episodic Narrative, 3rd ed.",
        (
            "https://api.pageplace.de/preview/"
            "DT0400.9781350932784_A42745559/preview-9781350932784_A42745559.pdf"
        ),
        "Macmillan Education / Red Globe Press",
        "scholarly_monograph",
        "hwang_history_korea_2021",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_goguryeo_lim_silla_2023",
        "Lim Gihwan, A Study on Silla's Military Activities during the Fall of Koguryo",
        (
            "https://www.kci.go.kr/kciportal/ci/sereArticleSearch/"
            "ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002935429"
        ),
        "The Society for the Studies of Korean History / KCI",
        "peer_reviewed_journal_article",
        "lim_silla_fall_koguryo_2023",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_GOGURYEO_SOURCES}


# Reuse the matching Cliopatria identities, but keep every alias list empty.
# These entities enter the release only through the three fingerprinted rows.
WAVE8_GOGURYEO_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _GOGURYEO,
        "name": "Goguryeo",
        "kind": "kingdom",
        "start_year": -36,
        "end_year": 681,
        "region": "Korean Peninsula and Manchuria",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Curated from the matching time-bounded Cliopatria candidate. Only "
            "fingerprinted, candidate-keyed events may use this identity. The "
            "HCED spelling 'Koguryo' is not opened as a global alias, the 668 "
            "defeat does not transfer Elo to a successor, and the source "
            "coverage end is not treated as evidence that the kingdom survived "
            "the reviewed fall of Pyongyang."
        ),
        "source_ids": [
            "cliopatria_v020",
            "wave8_goguryeo_aks_history",
            "wave8_goguryeo_hwang_history",
        ],
    },
    {
        "id": _SILLA,
        "name": "Silla",
        "kind": "kingdom",
        "start_year": 378,
        "end_year": 681,
        "region": "Korean Peninsula",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Curated from the matching time-bounded Cliopatria candidate for the "
            "reviewed 668 coalition participant. Only fingerprinted, candidate-"
            "keyed events may use this identity; no Elo is inherited by later "
            "Silla coverage or inferred from the Tang alliance itself."
        ),
        "source_ids": [
            "cliopatria_v020",
            "wave8_goguryeo_aks_history",
            "wave8_goguryeo_lim_silla_2023",
        ],
    },
    {
        "id": _TANG,
        "name": "Tang Dynasty",
        "kind": "dynastic_state",
        "start_year": 623,
        "end_year": 910,
        "region": "East Asia",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Curated from the matching time-bounded Cliopatria candidate for the "
            "reviewed 645 and 668 campaigns. Only fingerprinted, candidate-keyed "
            "events may use this identity; generic China labels remain closed and "
            "no dynastic predecessor or successor inherits Elo."
        ),
        "source_ids": [
            "cliopatria_v020",
            "wave8_goguryeo_aks_history",
            "wave8_goguryeo_hwang_history",
        ],
    },
)


WAVE8_GOGURYEO_ROW_HASHES: dict[str, str] = {
    "hced-Ansi-song645-1": "c6ababfac45d5377c09d6f2e27f50f8f6db1a074899801300db0f450c9a23209",
    "hced-Pyongyang668-1": "2a759a46f9d4f3c7884b4d82e72fc52573c4211ad0655807e200c91209e24ba0",
    "hced-Salsu612-1": "087ccc8d951977ca9da5b7529572e7321faa23dbde15325cae15a15757b926b0",
}

WAVE8_GOGURYEO_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "599aacf1db824924ef6bda94c6e48d07223ddff99ecab36cbd66810f0834d9b8"
    ),
    "events_touched": 3,
    "label": _EXACT_LABEL,
    "sole_blocker_events": 3,
    "zero_time_valid_candidates": 3,
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
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    outcome_sources: Iterable[str],
    actor_override: str,
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(map(str, outcome_sources))
    return {
        "raw_row_sha256": WAVE8_GOGURYEO_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "goguryeo_sui_tang_wars_612_668",
        "side_1_entity_ids": list(map(str, side_1_entity_ids)),
        "side_2_entity_ids": list(map(str, side_2_entity_ids)),
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
        "actor_override": actor_override,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_GOGURYEO_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Salsu612-1": _contract(
        "hced-Salsu612-1",
        _canonical(
            "Battle of Salsu",
            612,
            "single_land_battle_during_sui_retreat",
        ),
        [_GOGURYEO],
        [_SUI],
        {
            "wave8_goguryeo_aks_history",
            "wave8_goguryeo_hwang_history",
        },
        "candidate_keyed_goguryeo_and_sui",
        (
            "The Academy of Korean Studies records the retreating Sui army as "
            "routed by Goguryeo at the Salsu River; Hwang independently records "
            "the destruction and retreat of the Sui force. Only the tactical "
            "battle is rated, not a synthetic result for the full invasion."
        ),
        confidence=0.97,
    ),
    "hced-Ansi-song645-1": _contract(
        "hced-Ansi-song645-1",
        _canonical(
            "Siege of Ansi Fortress",
            645,
            "three_month_siege_and_tang_withdrawal",
        ),
        [_GOGURYEO],
        [_TANG],
        {
            "wave8_goguryeo_ahn_645_thesis",
            "wave8_goguryeo_aks_history",
        },
        "candidate_keyed_goguryeo_and_tang",
        (
            "The Academy of Korean Studies records Ansi holding for three months "
            "and Tang returning without victory; Ahn's source-critical study "
            "independently identifies the Ansi defense and Tang withdrawal as a "
            "Goguryeo victory. The separate Tang field victory outside the "
            "fortress is not conflated with this siege outcome."
        ),
        confidence=0.96,
    ),
    "hced-Pyongyang668-1": _contract(
        "hced-Pyongyang668-1",
        _canonical(
            "Siege and Fall of Pyongyang",
            668,
            "terminal_siege_and_fall_of_goguryeo_capital",
        ),
        [_TANG, _SILLA],
        [_GOGURYEO],
        {
            "wave8_goguryeo_aks_history",
            "wave8_goguryeo_hwang_history",
            "wave8_goguryeo_lim_silla_2023",
        },
        "source_attested_tang_silla_coalition_expansion",
        (
            "The Academy history and Hwang identify Goguryeo's 668 defeat by "
            "joint Silla-Tang forces. Lim's article independently reconstructs "
            "Silla's participation throughout the Pyongyang siege. The contract "
            "therefore expands HCED's abbreviated Tang label to the directly "
            "attested coalition while retaining its winner orientation."
        ),
        confidence=0.98,
    ),
}

WAVE8_GOGURYEO_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_GOGURYEO_CONTRACT_IDS = frozenset(WAVE8_GOGURYEO_CONTRACTS)
WAVE8_GOGURYEO_HOLD_IDS = frozenset(WAVE8_GOGURYEO_HOLDS)
WAVE8_GOGURYEO_RESERVED_IDS = frozenset(
    {*WAVE8_GOGURYEO_CONTRACT_IDS, *WAVE8_GOGURYEO_HOLD_IDS}
)
WAVE8_GOGURYEO_POINT_QUARANTINE_ADDITIONS = WAVE8_GOGURYEO_CONTRACT_IDS
WAVE8_GOGURYEO_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_GOGURYEO_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the named battlefield and modern "
            "country but do not independently verify HCED's exact coordinate; "
            "retain the country assertion and withhold the point."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_GOGURYEO_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_GOGURYEO_CONTRACTS,
        "entities": WAVE8_GOGURYEO_ENTITIES,
        "funnel": WAVE8_GOGURYEO_FUNNEL_AUDIT,
        "holds": WAVE8_GOGURYEO_HOLDS,
        "location_reasons": WAVE8_GOGURYEO_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_GOGURYEO_ROW_HASHES,
        "sources": WAVE8_GOGURYEO_SOURCES,
    }


def wave8_goguryeo_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_GOGURYEO_FINAL_AUDIT_SIGNATURE = (
    "01980649d57afd1468b7d61adacd768491265ad029bb5d42bf9e0b1f0e32fbba"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = {str(entity["id"]) for entity in WAVE8_GOGURYEO_ENTITIES}
    if len(source_ids) != len(WAVE8_GOGURYEO_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if entity_ids != {_GOGURYEO, _SILLA, _TANG}:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_GOGURYEO_CONTRACT_IDS & WAVE8_GOGURYEO_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_GOGURYEO_RESERVED_IDS != set(WAVE8_GOGURYEO_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_GOGURYEO_POINT_QUARANTINE_ADDITIONS != WAVE8_GOGURYEO_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_GOGURYEO_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_GOGURYEO_LOCATION_QUARANTINE_REASONS) != WAVE8_GOGURYEO_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    expected_windows = {
        _GOGURYEO: (-36, 681),
        _SILLA: (378, 681),
        _TANG: (623, 910),
    }
    used_sources: set[str] = set()
    for entity in WAVE8_GOGURYEO_ENTITIES:
        entity_id = str(entity["id"])
        if entity["aliases"] or (
            entity["start_year"],
            entity["end_year"],
        ) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} identity boundary or alias drift")
        if normalize_label(entity["name"]) == _EXACT_LABEL:
            raise ValueError(f"{_LANE_NAME} generic Koguryo label opened")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity evidence order drift")
        used_sources.update(set(map(str, entity["source_ids"])) & source_ids)

    expected_sides = {
        "hced-Salsu612-1": ([_GOGURYEO], [_SUI]),
        "hced-Ansi-song645-1": ([_GOGURYEO], [_TANG]),
        "hced-Pyongyang668-1": ([_TANG, _SILLA], [_GOGURYEO]),
    }
    for candidate_id, contract in WAVE8_GOGURYEO_CONTRACTS.items():
        if contract["disposition"] != "promote" or contract["result_type"] != "win":
            raise ValueError(f"{_LANE_NAME} disposition drift: {candidate_id}")
        if contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} winner-side drift: {candidate_id}")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} outcome override drift: {candidate_id}")
        sides = (
            list(map(str, contract["side_1_entity_ids"])),
            list(map(str, contract["side_2_entity_ids"])),
        )
        if sides != expected_sides[candidate_id]:
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
        used_sources.update(evidence)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_goguryeo_audit_signature() != WAVE8_GOGURYEO_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_goguryeo_queue_contracts(
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
    if exact_ids != WAVE8_GOGURYEO_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_GOGURYEO_ROW_HASHES.items():
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
        if row.get("massacre_raw") != "No":
            raise ValueError(f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_GOGURYEO_CONTRACTS,
        WAVE8_GOGURYEO_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_goguryeo_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
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
    if checks != WAVE8_GOGURYEO_FUNNEL_AUDIT:
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
    "hced-Salsu612-1": {
        "Battle of Salsu",
        "Battle of Salsu River",
        "Salsu",
    },
    "hced-Ansi-song645-1": {
        "Ansi",
        "Ansi-song",
        "Ansiseong",
        "Siege of Ansi",
        "Siege of Ansi Fortress",
    },
    "hced-Pyongyang668-1": {
        "Fall of Pyeongyang",
        "Fall of Pyongyang",
        "Pyeongyang",
        "Pyongyang",
        "Siege and Fall of Pyongyang",
        "Siege of Pyongyang",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(WAVE8_GOGURYEO_CONTRACTS[candidate_id]["canonical_event"]["year_low"]),
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


def validate_wave8_goguryeo_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_goguryeo_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_GOGURYEO_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_GOGURYEO_CONTRACT_IDS
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


def install_wave8_goguryeo_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_GOGURYEO_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_goguryeo_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_GOGURYEO_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_GOGURYEO_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_GOGURYEO_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_goguryeo_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_goguryeo_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_GOGURYEO_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_goguryeo_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_GOGURYEO_CONTRACTS.values(),
                    *WAVE8_GOGURYEO_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_goguryeo_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": len(WAVE8_GOGURYEO_HOLDS),
        "new_entities": len(WAVE8_GOGURYEO_ENTITIES),
        "new_sources": len(WAVE8_GOGURYEO_SOURCES),
        "newly_rated_events": len(WAVE8_GOGURYEO_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_GOGURYEO_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_GOGURYEO_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_GOGURYEO_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_goguryeo_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_goguryeo_counts(),
        "cohorts": wave8_goguryeo_cohort_counts(),
        "final_audit_signature": WAVE8_GOGURYEO_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_GOGURYEO_CONTRACT_IDS),
        "hold_candidate_ids": sorted(WAVE8_GOGURYEO_HOLD_IDS),
    }


_validate_static()
