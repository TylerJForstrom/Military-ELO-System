"""Candidate-keyed completion audit for HCED's remaining Irish Civil War rows.

Two discrete urban battles are promoted: the National Army captures of
Limerick and Waterford in July 1922.  The generic ``Tipperary`` row is held as
a multi-place campaign umbrella that overlaps already-rated Clonmel and
Kilmallock fighting.  Béal na mBláth is also held: the source labels the Free
State the winner even though the anti-Treaty ambush killed Michael Collins,
and the reviewed evidence does not support inventing a tactical Free State
victory.  Unknown is never converted into a draw.

The lane reuses the already-curated, conflict-bounded National Army and
Anti-Treaty IRA identities.  It opens no label policy and creates no new
identity or continuity inheritance path.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS",
    "WAVE8_IRISH_CIVIL_WAR_CONTRACTS",
    "WAVE8_IRISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_IRISH_CIVIL_WAR_ENTITIES",
    "WAVE8_IRISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE",
    "WAVE8_IRISH_CIVIL_WAR_FUNNEL_AUDIT",
    "WAVE8_IRISH_CIVIL_WAR_HOLD_IDS",
    "WAVE8_IRISH_CIVIL_WAR_HOLDS",
    "WAVE8_IRISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS",
    "WAVE8_IRISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_IRISH_CIVIL_WAR_RESERVED_IDS",
    "WAVE8_IRISH_CIVIL_WAR_ROW_HASHES",
    "WAVE8_IRISH_CIVIL_WAR_SOURCES",
    "install_wave8_irish_civil_war_sources",
    "promote_wave8_irish_civil_war_contracts",
    "validate_wave8_irish_civil_war_funnel",
    "validate_wave8_irish_civil_war_integration_dispositions",
    "validate_wave8_irish_civil_war_queue_contracts",
    "wave8_irish_civil_war_audit_signature",
    "wave8_irish_civil_war_cohort_counts",
    "wave8_irish_civil_war_counts",
    "wave8_irish_civil_war_metadata",
)


_LANE_NAME = "Wave 8 Irish Civil War completion audit"
_MODULE_OWNER = "military_elo.promotion.wave8_irish_civil_war"
_EVENT_ID_PREFIX = "hced_wave8_irish_civil_war_"
_COHORT = "irish_civil_war_remaining_rows_1922"

_NATIONAL_ARMY = "irish_national_army_1922_1923"
_ANTI_TREATY = "anti_treaty_ira_1922_1923"

_PREVIOUSLY_OWNED_IDS = frozenset(
    {
        "hced-Clashmealcon Caves1923-1",
        "hced-Clonmel1922-1",
        "hced-Cork1922-1",
        "hced-Four Courts1922-1",
        "hced-Kilmallock1922-1",
        "hced-O'Connell Street1922-1",
    }
)


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


WAVE8_IRISH_CIVIL_WAR_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_irish_cw_rte_ucc_limerick_1922",
        "Urban warfare: the Battle for Limerick",
        "https://www.rte.ie/history/conventional-phase/2022/0713/1309991-the-battle-for-limerick/",
        "RTÉ and University College Cork",
        "academic_public_history",
        "ucc_atlas_irish_revolution",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_irish_cw_limerick_inevitable_conflict",
        "The Inevitable Conflict: Essays on the Civil War in County Limerick",
        (
            "https://www.limerick.ie/sites/default/files/media/documents/"
            "2022-08/The-Inevitable-Conflict.pdf"
        ),
        "Limerick City and County Council",
        "official_local_history_collection",
        "limerick_council_civil_war_history",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_irish_cw_ucc_1922_overview",
        "The Irish Revolution: 1922 Battle for Munster overview",
        "https://www.ucc.ie/en/theirishrevolution/",
        "University College Cork",
        "academic_public_history",
        "ucc_atlas_irish_revolution",
        ["outcome", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_irish_cw_decies_waterford_1922",
        "The Battle of Waterford, 1922",
        (
            "https://archive.waterfordcouncil.ie/Historical%20Newspapers%2C%20"
            "Books%20and%20Journals/Decies/Decies%20XXVI%20-%201984.pdf"
        ),
        "Waterford Archaeological and Historical Society / Decies",
        "local_history_journal_article",
        "waterford_decies_journal",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_irish_cw_ucc_cork_fatalities",
        "Cork Fatality Register: Research Findings",
        (
            "https://www.ucc.ie/en/theirishrevolution/collections/"
            "cork-fatality-register/register-research-findings/"
        ),
        "University College Cork",
        "academic_research_register",
        "ucc_irish_civil_war_fatalities",
        ["outcome_consistency_crosscheck"],
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_IRISH_CIVIL_WAR_SOURCES
}

# This lane deliberately reuses the two exact identities installed by the
# earlier Somali/Irish/South-Africa tranche.
WAVE8_IRISH_CIVIL_WAR_ENTITIES: tuple[dict[str, Any], ...] = ()


WAVE8_IRISH_CIVIL_WAR_ROW_HASHES: dict[str, str] = {
    "hced-Beal na mBlath1922-1": (
        "6eb889509435759e6a92b0b382b2b339382205aee5c70117fda5c62e83a5a1e2"
    ),
    "hced-Limerick1922-1": (
        "7610b06bcd603897e4b8b86303af91f701e7a7ba54a7e997807efad56d787fa2"
    ),
    "hced-Tipperary1922-1": (
        "8b5b3c8db4a959d81b87934817bbdcc06ee28650063064c9107ca9a1f84e3194"
    ),
    "hced-Waterford1922-1": (
        "4b5948fa083c850de9e1eff1773a05e1fec568f21f50be68ce605cd8b8052c97"
    ),
}


WAVE8_IRISH_CIVIL_WAR_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "anti treaty ira": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "40f6392765603c08b26cad0a1326a34cfeba1647cbd5466f364e674cafd89909"
        ),
        "events_touched": 3,
        "label": "anti treaty ira",
        "sole_blocker_events": 3,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 3,
        "zero_time_valid_candidates": 3,
    },
    "irish republican rebels": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "e9fda0cfa1d526b15478820fadcd3e8960707b8a62d3ff03f7707be3f63214cf"
        ),
        "events_touched": 1,
        "label": "irish republican rebels",
        "sole_blocker_events": 1,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 1,
        "zero_time_valid_candidates": 1,
    },
}


def _canonical(name: str, *, granularity: str) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:1922:1922",
        "date_precision": "year",
        "granularity": granularity,
        "name": name,
        "year_low": 1922,
        "year_high": 1922,
    }


def _contract(
    candidate_id: str,
    name: str,
    evidence_refs: Iterable[str],
    audit_note: str,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    return {
        "raw_row_sha256": WAVE8_IRISH_CIVIL_WAR_ROW_HASHES[candidate_id],
        "canonical_event": _canonical(name, granularity="urban_battle"),
        "cohort": _COHORT,
        "side_1_entity_ids": [_NATIONAL_ARMY],
        "side_2_entity_ids": [_ANTI_TREATY],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "civil_war",
        "confidence": 0.98,
        "evidence_refs": evidence,
        "outcome_source_ids": evidence,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in evidence
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_existing_civil_war_forces",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_IRISH_CIVIL_WAR_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Limerick1922-1": _contract(
        "hced-Limerick1922-1",
        "Battle of Limerick",
        {
            "wave8_irish_cw_limerick_inevitable_conflict",
            "wave8_irish_cw_rte_ucc_limerick_1922",
        },
        (
            "The UCC/RTÉ history and Limerick council's independent essay "
            "collection document the ten-day urban battle ending with the "
            "National Army clearing the anti-Treaty positions on 21 July. "
            "Only that tactical city battle is rated."
        ),
    ),
    "hced-Waterford1922-1": _contract(
        "hced-Waterford1922-1",
        "Battle of Waterford",
        {
            "wave8_irish_cw_decies_waterford_1922",
            "wave8_irish_cw_ucc_1922_overview",
        },
        (
            "The Decies battle study and UCC's Atlas overview independently "
            "record the 18-21 July fighting and National Army capture of the "
            "city. No later Munster offensive result is inferred."
        ),
    ),
}


WAVE8_IRISH_CIVIL_WAR_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Beal na mBlath1922-1": {
        "raw_row_sha256": WAVE8_IRISH_CIVIL_WAR_ROW_HASHES[
            "hced-Beal na mBlath1922-1"
        ],
        "canonical_event": _canonical(
            "Béal na mBláth ambush",
            granularity="ambush",
        ),
        "cohort": _COHORT,
        "disposition": "hold",
        "hold_category": "source_outcome_not_defensible",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "evidence_refs": ["wave8_irish_cw_ucc_cork_fatalities"],
        "hold_reason": (
            "UCC's research register identifies Michael Collins as killed in "
            "an anti-Treaty IRA ambush. That evidence contradicts HCED's bare "
            "Irish Free State victory label but does not establish a complete "
            "opposite tactical outcome, so the row stays unknown rather than "
            "being reversed or converted to a draw."
        ),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "review_hold_owner",
        },
    },
    "hced-Tipperary1922-1": {
        "raw_row_sha256": WAVE8_IRISH_CIVIL_WAR_ROW_HASHES[
            "hced-Tipperary1922-1"
        ],
        "canonical_event": _canonical(
            "Tipperary operations",
            granularity="multi_place_campaign_umbrella",
        ),
        "cohort": _COHORT,
        "disposition": "hold",
        "hold_category": "non_discrete_campaign_umbrella",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "evidence_refs": ["wave8_irish_cw_ucc_1922_overview"],
        "hold_reason": (
            "The raw participant tokens span Thurles, Golden, and Tipperary, "
            "while UCC describes a multi-town National Army push through the "
            "county. No discrete battle boundary can be recovered, and rating "
            "the umbrella would overlap the already-rated Clonmel and "
            "Kilmallock actions."
        ),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "review_hold_owner",
        },
    },
}


WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS = frozenset(
    WAVE8_IRISH_CIVIL_WAR_CONTRACTS
)
WAVE8_IRISH_CIVIL_WAR_HOLD_IDS = frozenset(WAVE8_IRISH_CIVIL_WAR_HOLDS)
WAVE8_IRISH_CIVIL_WAR_RESERVED_IDS = frozenset(
    {
        *WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS,
        *WAVE8_IRISH_CIVIL_WAR_HOLD_IDS,
    }
)
WAVE8_IRISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS
)
WAVE8_IRISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_IRISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "HCED supplies an unexplained city centroid rather than a reviewed "
            "urban battle footprint; retain the provenance-bound Ireland label "
            "and withhold geometry."
        ),
        "evidence_refs": sorted(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(
        WAVE8_IRISH_CIVIL_WAR_CONTRACTS.items()
    )
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_IRISH_CIVIL_WAR_CONTRACTS,
        "entities": WAVE8_IRISH_CIVIL_WAR_ENTITIES,
        "funnel": WAVE8_IRISH_CIVIL_WAR_FUNNEL_AUDIT,
        "holds": WAVE8_IRISH_CIVIL_WAR_HOLDS,
        "location_reasons": WAVE8_IRISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS,
        "previously_owned_ids": sorted(_PREVIOUSLY_OWNED_IDS),
        "row_hashes": WAVE8_IRISH_CIVIL_WAR_ROW_HASHES,
        "sources": WAVE8_IRISH_CIVIL_WAR_SOURCES,
    }


def wave8_irish_civil_war_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_IRISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE = (
    "0d00c1f9cc3379a6b997f8d1050aa83f4cb00552dcaf78781166d371d219dad2"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_IRISH_CIVIL_WAR_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if WAVE8_IRISH_CIVIL_WAR_ENTITIES:
        raise ValueError(f"{_LANE_NAME} must not create an identity")
    if WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS & WAVE8_IRISH_CIVIL_WAR_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_IRISH_CIVIL_WAR_RESERVED_IDS != set(
        WAVE8_IRISH_CIVIL_WAR_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_IRISH_CIVIL_WAR_RESERVED_IDS & _PREVIOUSLY_OWNED_IDS:
        raise ValueError(f"{_LANE_NAME} overlaps the prior Irish lane")
    if (
        WAVE8_IRISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS
        != WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS
        or WAVE8_IRISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location policy drift")
    if set(WAVE8_IRISH_CIVIL_WAR_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_IRISH_CIVIL_WAR_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["side_1_entity_ids"] != [_NATIONAL_ARMY]
            or contract["side_2_entity_ids"] != [_ANTI_TREATY]
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
        ):
            raise ValueError(f"{_LANE_NAME} actor/outcome drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or evidence != outcomes:
            raise ValueError(f"{_LANE_NAME} evidence order drift: {candidate_id}")
        if not set(evidence) <= source_ids:
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

    expected_hold_categories = {
        "hced-Beal na mBlath1922-1": "source_outcome_not_defensible",
        "hced-Tipperary1922-1": "non_discrete_campaign_umbrella",
    }
    for candidate_id, hold in WAVE8_IRISH_CIVIL_WAR_HOLDS.items():
        if (
            hold["disposition"] != "hold"
            or hold["hold_category"] != expected_hold_categories[candidate_id]
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} hold drift: {candidate_id}")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} hold evidence drift: {candidate_id}")
        used_sources.update(evidence)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if (
        wave8_irish_civil_war_audit_signature()
        != WAVE8_IRISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_irish_civil_war_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    civil_war_rows = [
        row
        for row in hced_rows
        if "Irish Civil War" in list(map(str, row.get("war_names", [])))
    ]
    by_id = {str(row.get("candidate_id")): row for row in civil_war_rows}
    expected_ids = _PREVIOUSLY_OWNED_IDS | WAVE8_IRISH_CIVIL_WAR_RESERVED_IDS
    if set(by_id) != expected_ids or len(civil_war_rows) != len(by_id):
        raise ValueError(f"{_LANE_NAME} complete war inventory changed")

    expected_sides = {
        "hced-Beal na mBlath1922-1": (
            "Irish Free State",
            "Irish Republican Rebels",
        ),
        "hced-Limerick1922-1": ("Irish Free State", "Anti Treaty IRA"),
        "hced-Tipperary1922-1": ("Irish Free State", "Anti-Treaty IRA"),
        "hced-Waterford1922-1": ("Irish Free State", "Anti-Treaty IRA"),
    }
    for candidate_id, expected_hash in WAVE8_IRISH_CIVIL_WAR_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        side_1, side_2 = expected_sides[candidate_id]
        if (
            (int(row["year_low"]), int(row["year_best"]), int(row["year_high"]))
            != (1922, 1922, 1922)
            or row.get("side_1_raw") != side_1
            or row.get("side_2_raw") != side_2
            or row.get("winner_raw") != side_1
            or row.get("loser_raw") != side_2
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
        ):
            raise ValueError(f"{_LANE_NAME} source semantics changed: {candidate_id}")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_IRISH_CIVIL_WAR_CONTRACTS,
        WAVE8_IRISH_CIVIL_WAR_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "complete_irish_civil_war_rows": len(civil_war_rows),
        "previously_owned_rows": len(_PREVIOUSLY_OWNED_IDS),
    }


def _funnel_projection(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "label": str(row.get("label")),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, row.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
        "zero_time_valid_candidates": int(
            row.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
        ),
    }


def validate_wave8_irish_civil_war_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    by_label = {
        str(row.get("label")): row for row in funnel.get("labels", [])
    }
    for label, expected in WAVE8_IRISH_CIVIL_WAR_FUNNEL_AUDIT.items():
        row = by_label.get(label)
        actual = _funnel_projection(row or {})
        if actual != expected:
            raise ValueError(f"{_LANE_NAME} funnel pin changed for {label}: {actual}")
    return {
        "labels": len(WAVE8_IRISH_CIVIL_WAR_FUNNEL_AUDIT),
        "events_touched": sum(
            item["events_touched"]
            for item in WAVE8_IRISH_CIVIL_WAR_FUNNEL_AUDIT.values()
        ),
        "sole_blocker_events": sum(
            item["sole_blocker_events"]
            for item in WAVE8_IRISH_CIVIL_WAR_FUNNEL_AUDIT.values()
        ),
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
    1922: {
        "Battle of Limerick",
        "Battle of Waterford",
        "Limerick",
        "Waterford",
    }
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


def validate_wave8_irish_civil_war_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_irish_civil_war_queue_contracts(hced_rows)
    events = list(existing_events)
    prior_owners = {
        str(event.get("hced_candidate_id"))
        for event in events
        if event.get("hced_candidate_id") in _PREVIOUSLY_OWNED_IDS
    }
    if prior_owners != _PREVIOUSLY_OWNED_IDS:
        raise ValueError(f"{_LANE_NAME} prior Irish ownership changed")

    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in (WAVE8_IRISH_CIVIL_WAR_RESERVED_IDS | _PREVIOUSLY_OWNED_IDS)
        and _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in events
        if event.get("hced_candidate_id")
        not in WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS
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
        "previously_owned_irish_events": len(prior_owners),
    }


def install_wave8_irish_civil_war_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_IRISH_CIVIL_WAR_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_IRISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_IRISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_irish_civil_war_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_irish_civil_war_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_IRISH_CIVIL_WAR_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_irish_civil_war_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_IRISH_CIVIL_WAR_CONTRACTS.values(),
                    *WAVE8_IRISH_CIVIL_WAR_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_irish_civil_war_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": len(WAVE8_IRISH_CIVIL_WAR_HOLDS),
        "new_entities": 0,
        "new_sources": len(WAVE8_IRISH_CIVIL_WAR_SOURCES),
        "newly_rated_events": len(WAVE8_IRISH_CIVIL_WAR_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_IRISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_IRISH_CIVIL_WAR_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_IRISH_CIVIL_WAR_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_irish_civil_war_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_irish_civil_war_counts(),
        "cohorts": wave8_irish_civil_war_cohort_counts(),
        "final_audit_signature": WAVE8_IRISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS),
        "hold_candidate_ids": sorted(WAVE8_IRISH_CIVIL_WAR_HOLD_IDS),
    }


_validate_static()
