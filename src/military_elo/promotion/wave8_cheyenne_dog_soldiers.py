"""Candidate-keyed audit of HCED's three unresolved ``Cheyenne`` rows.

The bare label is never opened as an alias.  Two fingerprinted 1868 rows bind
to the time-bounded Cheyenne Dog Soldiers band and one 1864 attack on a peace
village is terminally excluded.  The contracts rate tactical outcomes only;
they do not transfer a rating to Cheyenne ethnicity or a modern tribal nation.
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
    "WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_FUNNEL_AUDIT",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_HOLDS",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_RESERVED_IDS",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_ROW_HASHES",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES",
    "WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS",
    "install_wave8_cheyenne_dog_soldiers_entities",
    "install_wave8_cheyenne_dog_soldiers_sources",
    "promote_wave8_cheyenne_dog_soldiers_contracts",
    "validate_wave8_cheyenne_dog_soldiers_funnel",
    "validate_wave8_cheyenne_dog_soldiers_integration_dispositions",
    "validate_wave8_cheyenne_dog_soldiers_queue_contracts",
    "wave8_cheyenne_dog_soldiers_audit_signature",
    "wave8_cheyenne_dog_soldiers_cohort_counts",
    "wave8_cheyenne_dog_soldiers_counts",
    "wave8_cheyenne_dog_soldiers_metadata",
)


_LANE_NAME = "Wave 8 exact Cheyenne Dog Soldiers audit"
_MODULE_OWNER = "military_elo.promotion.wave8_cheyenne_dog_soldiers"
_EVENT_ID_PREFIX = "hced_wave8_cheyenne_dog_soldiers_"
_EXACT_LABEL = "cheyenne"

_DOG_SOLDIERS = "cheyenne_dog_soldiers_band_1849_1869"
_UNITED_STATES = "united_states"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
    government_work: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "U.S. Government work" if government_work else "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-18",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_dog_soldiers_cheyenne_wars_atlas",
        "The Cheyenne Wars Atlas",
        (
            "https://www.armyupress.army.mil/Portals/7/educational-services/"
            "staff-rides/StaffRideHB_AtlasofCheyenneWars.pdf"
        ),
        "U.S. Army University Press / Combat Studies Institute",
        "official_military_history_atlas",
        "us_army_university_press_cheyenne_wars_atlas",
        outcome=True,
        government_work=True,
    ),
    _source(
        "wave8_dog_soldiers_showalter_encyclopedia",
        "The Encyclopedia of Warfare (Dennis Showalter, 2013), p. 608",
        "https://archive.org/details/isbn_9781435151260",
        "Metro Books; Internet Archive catalogue record",
        "expert_military_reference",
        "showalter_encyclopedia_warfare",
        outcome=True,
    ),
    _source(
        "wave8_dog_soldiers_army_10th_cavalry",
        "10th Cavalry Regiment: the October 1868 Beaver Creek action",
        (
            "https://history.army.mil/Research/Reference-Topics/"
            "African-Americans-in-the-US-Army/10th-Cavalry-Regiment/"
        ),
        "U.S. Army Center of Military History",
        "official_regimental_history",
        "us_army_center_military_history",
        outcome=True,
        government_work=True,
    ),
    _source(
        "wave8_dog_soldiers_nps_10th_timeline",
        "10th Cavalry Timeline: Beaver Creek, October 1868",
        "https://www.nps.gov/fols/learn/historyculture/10th-cavalry-timeline.htm",
        "National Park Service, Fort Larned National Historic Site",
        "government_history_timeline",
        "us_national_park_service_fort_larned",
        outcome=True,
        government_work=True,
    ),
    _source(
        "wave8_dog_soldiers_colorado_history_ledgerbook",
        "Cheyenne Dog Soldiers: A Ledgerbook History of Coups and Combat",
        "https://books.google.com/books/about/Cheyenne_Dog_Soldiers.html?id=jY4OAQAAMAAJ",
        "Colorado Historical Society; Google Books catalogue record",
        "scholarly_museum_monograph",
        "colorado_historical_society_dog_soldiers",
    ),
    _source(
        "wave8_dog_soldiers_denver_cedar_canyon",
        "William N. Byers: Contributing to a Massacre",
        "https://history.denverlibrary.org/news/william-n-byers-contributing-massacre",
        "Denver Public Library, Western History and Genealogy",
        "public_history_research_article",
        "denver_public_library_western_history",
    ),
    _source(
        "wave8_dog_soldiers_fowler_cedar_canyon",
        "Arapaho and Cheyenne Perspectives: Sand Creek and the 1864 Plains Campaign",
        "https://www.jstor.org/stable/10.5250/amerindiquar.39.4.0364",
        "American Indian Quarterly / University of Nebraska Press",
        "peer_reviewed_historical_article",
        "american_indian_quarterly_fowler_2015",
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES
}


WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _DOG_SOLDIERS,
        "name": "Cheyenne Dog Soldiers band (1849–1869)",
        "kind": "indigenous_military_band",
        "start_year": 1849,
        "end_year": 1869,
        "region": "Central Great Plains of North America",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The identity is limited to the Dog Soldiers after the 1849 "
            "Masikota consolidation and through the destruction of Tall Bull's "
            "principal band at Summit Springs in 1869. No rating is inherited "
            "by Cheyenne ethnicity, another Cheyenne society or band, or any "
            "modern tribal government."
        ),
        "source_ids": [
            "wave8_dog_soldiers_cheyenne_wars_atlas",
            "wave8_dog_soldiers_colorado_history_ledgerbook",
        ],
    },
)


WAVE8_CHEYENNE_DOG_SOLDIERS_ROW_HASHES: dict[str, str] = {
    "hced-Beaver Creek1868-1": (
        "45311aec76e8bccab0d289675f9744df03cfcb5ec8bddd1b69919c07475ac133"
    ),
    "hced-Beecher Island1868-1": (
        "113f4c50482bc63292f945362e21a98a82606248e32636a019e933382f53c47f"
    ),
    "hced-Cedar Canyon1864-1": (
        "f4f5d0ea6f25277991d0e63b75e9aed46da0cb2f35ef1fd78892a0e4f1f6e843"
    ),
}


WAVE8_CHEYENNE_DOG_SOLDIERS_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "0a5cdc4c3ba57000a58e11f96b3cd8f8d8dd1d2db7bc7e588db0e5debac9c0b5"
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
    name: str,
    outcome_source_ids: Iterable[str],
    audit_note: str,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_CHEYENNE_DOG_SOLDIERS_ROW_HASHES[candidate_id],
        "canonical_event": _canonical(name, 1868, "single_tactical_engagement"),
        "cohort": "cheyenne_dog_soldiers_war_1864_1869",
        "side_1_entity_ids": [_UNITED_STATES],
        "side_2_entity_ids": [_DOG_SOLDIERS],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
        "confidence": 0.92,
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
        "actor_override": "candidate_keyed_cheyenne_dog_soldiers_band",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Beecher Island1868-1": _contract(
        "hced-Beecher Island1868-1",
        "Battle of Beecher Island",
        [
            "wave8_dog_soldiers_cheyenne_wars_atlas",
            "wave8_dog_soldiers_showalter_encyclopedia",
        ],
        (
            "Showalter's row-level reference codes the United States tactical "
            "win. The Army atlas independently records that Forsyth's scouts "
            "repelled the massed assaults and the attackers departed; its "
            "separate characterization of a costly Indigenous success concerns "
            "the wider objective of shielding the villages. This contract rates "
            "only the local defensive engagement, not that campaign outcome."
        ),
    ),
    "hced-Beaver Creek1868-1": _contract(
        "hced-Beaver Creek1868-1",
        "Battle of Beaver Creek (1868)",
        [
            "wave8_dog_soldiers_army_10th_cavalry",
            "wave8_dog_soldiers_nps_10th_timeline",
        ],
        (
            "The Army regimental history and the National Park Service both "
            "record Carpenter's 10th Cavalry command holding off the attacking "
            "force, completing its defensive stand, and continuing the escort. "
            "Only that tactical result is rated."
        ),
    ),
}


WAVE8_CHEYENNE_DOG_SOLDIERS_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Cedar Canyon1864-1": {
        "raw_row_sha256": WAVE8_CHEYENNE_DOG_SOLDIERS_ROW_HASHES[
            "hced-Cedar Canyon1864-1"
        ],
        "canonical_event": _canonical(
            "Attack at Cedar Canyon",
            1864,
            "non_ratable_attack",
        ),
        "cohort": "cheyenne_dog_soldiers_war_1864_1869",
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "hold_category": "noncompetitive_attack_on_peace_village",
        "reviewed_actor_description": [
            "Colorado territorial militia",
            "Cheyenne and Arapaho peace-village residents",
        ],
        "reviewed_granularity": "non_ratable_attack",
        "hold_reason": (
            "The reviewed episode was an attack on a peace-oriented Cheyenne-"
            "Arapaho village while most fighting men were absent, not a "
            "competitive opposing-force engagement. Civilian vulnerability is "
            "not converted into a Cheyenne tactical defeat."
        ),
        "evidence_refs": [
            "wave8_dog_soldiers_denver_cedar_canyon",
            "wave8_dog_soldiers_fowler_cedar_canyon",
        ],
    },
}

WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS = frozenset(
    WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS
)
WAVE8_CHEYENNE_DOG_SOLDIERS_RESERVED_IDS = frozenset(
    WAVE8_CHEYENNE_DOG_SOLDIERS_ROW_HASHES
)
WAVE8_CHEYENNE_DOG_SOLDIERS_POINT_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Beaver Creek1868-1"}
)
WAVE8_CHEYENNE_DOG_SOLDIERS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = (
    frozenset()
)
WAVE8_CHEYENNE_DOG_SOLDIERS_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    "hced-Beaver Creek1868-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_dog_soldiers_army_10th_cavalry",
            "wave8_dog_soldiers_nps_10th_timeline",
        ],
        "raw_point": [-106.5188996, 39.6042986],
        "retained_country": "United States",
        "reason": (
            "The reviewed histories identify the Beaver Creek action and its "
            "United States setting but do not authenticate HCED's point, which "
            "lies far west of the Kansas action. Retain the country assertion "
            "and withhold the coordinate."
        ),
    }
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS,
        "entities": WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES,
        "funnel": WAVE8_CHEYENNE_DOG_SOLDIERS_FUNNEL_AUDIT,
        "holds": WAVE8_CHEYENNE_DOG_SOLDIERS_HOLDS,
        "location_reasons": WAVE8_CHEYENNE_DOG_SOLDIERS_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_CHEYENNE_DOG_SOLDIERS_ROW_HASHES,
        "sources": WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES,
        "terminal_exclusions": WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS,
    }


def wave8_cheyenne_dog_soldiers_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_CHEYENNE_DOG_SOLDIERS_FINAL_AUDIT_SIGNATURE = (
    "da4f9e59326ecd1d04e507390170c2c26fbea562d1fe714251d6304a68cd7f3d"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if len(WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES) != 1:
        raise ValueError(f"{_LANE_NAME} identity inventory drift")
    entity = WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES[0]
    if (
        entity["id"] != _DOG_SOLDIERS
        or entity["start_year"] != 1849
        or entity["end_year"] != 1869
        or entity["aliases"]
        or entity["predecessors"]
        or normalize_label(entity["name"]) in {"cheyenne", "cheyenne indians"}
        or "no rating is inherited" not in str(entity["continuity_note"]).casefold()
    ):
        raise ValueError(f"{_LANE_NAME} identity firewall drift")
    if not _is_sorted_unique(entity["source_ids"]) or not set(entity["source_ids"]) <= source_ids:
        raise ValueError(f"{_LANE_NAME} identity source drift")
    if WAVE8_CHEYENNE_DOG_SOLDIERS_RESERVED_IDS != set(
        WAVE8_CHEYENNE_DOG_SOLDIERS_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} reservation inventory drift")
    if (
        WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS
        | set(WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS)
    ) != WAVE8_CHEYENNE_DOG_SOLDIERS_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} disposition partition drift")
    if WAVE8_CHEYENNE_DOG_SOLDIERS_HOLDS:
        raise ValueError(f"{_LANE_NAME} acquired an unknown-outcome hold")
    if WAVE8_CHEYENNE_DOG_SOLDIERS_POINT_QUARANTINE_ADDITIONS != {
        "hced-Beaver Creek1868-1"
    }:
        raise ValueError(f"{_LANE_NAME} point quarantine drift")
    if WAVE8_CHEYENNE_DOG_SOLDIERS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country quarantine drift")
    if set(WAVE8_CHEYENNE_DOG_SOLDIERS_LOCATION_QUARANTINE_REASONS) != set(
        WAVE8_CHEYENNE_DOG_SOLDIERS_POINT_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    used_sources = set(map(str, entity["source_ids"]))
    for candidate_id, contract in WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["confidence"] != 0.92
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome policy drift: {candidate_id}")
        if contract["side_1_entity_ids"] != [_UNITED_STATES] or contract[
            "side_2_entity_ids"
        ] != [_DOG_SOLDIERS]:
            raise ValueError(f"{_LANE_NAME} exact actor drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or evidence != outcomes
            or not set(outcomes) <= source_ids
        ):
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        if any("outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"] for source_id in outcomes):
            raise ValueError(f"{_LANE_NAME} non-outcome evidence: {candidate_id}")
        used_sources.update(evidence)

    exclusion = WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS[
        "hced-Cedar Canyon1864-1"
    ]
    if (
        exclusion["disposition"] != "terminal_exclusion"
        or exclusion["terminal_exclusion"] is not True
        or exclusion["hold_category"]
        != "noncompetitive_attack_on_peace_village"
    ):
        raise ValueError(f"{_LANE_NAME} terminal exclusion drift")
    if not _is_sorted_unique(exclusion["evidence_refs"]) or not set(
        exclusion["evidence_refs"]
    ) <= source_ids:
        raise ValueError(f"{_LANE_NAME} terminal evidence drift")
    used_sources.update(exclusion["evidence_refs"])
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if (
        wave8_cheyenne_dog_soldiers_audit_signature()
        != WAVE8_CHEYENNE_DOG_SOLDIERS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_cheyenne_dog_soldiers_queue_contracts(
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
    if exact_ids != WAVE8_CHEYENNE_DOG_SOLDIERS_RESERVED_IDS or len(exact) != len(
        exact_ids
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_CHEYENNE_DOG_SOLDIERS_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("do_not_rate_automatically") is not True:
            raise ValueError(f"{_LANE_NAME} discovery safety flag changed: {candidate_id}")
    for candidate_id in WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS:
        row = by_id[candidate_id]
        if (
            row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
        ):
            raise ValueError(f"{_LANE_NAME} competitive outcome drift: {candidate_id}")
    if by_id["hced-Cedar Canyon1864-1"].get("massacre_raw") != "Yes":
        raise ValueError(f"{_LANE_NAME} terminal-exclusion evidence drift")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS,
        WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS,
        lane_name=_LANE_NAME,
    )
    return {
        "promotion_contracts": counts["promotion_contracts"],
        "holds": len(WAVE8_CHEYENNE_DOG_SOLDIERS_HOLDS),
        "reviewed_hced_rows": counts["reviewed_hced_rows"],
        "exact_label_rows": len(exact),
        "terminal_exclusions": len(
            WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS
        ),
    }


def validate_wave8_cheyenne_dog_soldiers_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    labels = [row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL]
    if len(labels) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    row = labels[0]
    checks = {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "label": str(row.get("label")),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "zero_time_valid_candidates": int(
            row.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
        ),
    }
    if checks != WAVE8_CHEYENNE_DOG_SOLDIERS_FUNNEL_AUDIT:
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
    "hced-Beecher Island1868-1": {
        "Beecher Island",
        "Battle of Beecher Island",
        "Battle of Arikaree Fork",
    },
    "hced-Beaver Creek1868-1": {
        "Beaver Creek",
        "Battle of Beaver Creek",
        "Battle of Beaver Creek (1868)",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (year, normalize_label(alias))
    for aliases in _EVENT_ALIASES.values()
    for alias in aliases
    for year in range(1867, 1870)
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_cheyenne_dog_soldiers_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_cheyenne_dog_soldiers_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_CHEYENNE_DOG_SOLDIERS_RESERVED_IDS
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
        not in WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS
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


def install_wave8_cheyenne_dog_soldiers_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_cheyenne_dog_soldiers_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_CHEYENNE_DOG_SOLDIERS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_CHEYENNE_DOG_SOLDIERS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_cheyenne_dog_soldiers_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_cheyenne_dog_soldiers_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine(events)
    return events


def wave8_cheyenne_dog_soldiers_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS.values(),
                    *WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS.values(),
                )
            ).items()
        )
    )


def wave8_cheyenne_dog_soldiers_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": 0,
        "new_entities": len(WAVE8_CHEYENNE_DOG_SOLDIERS_ENTITIES),
        "new_sources": len(WAVE8_CHEYENNE_DOG_SOLDIERS_SOURCES),
        "newly_rated_events": len(WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_CHEYENNE_DOG_SOLDIERS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_CHEYENNE_DOG_SOLDIERS_RESERVED_IDS),
        "terminal_exclusions": len(
            WAVE8_CHEYENNE_DOG_SOLDIERS_TERMINAL_EXCLUSIONS
        ),
    }


def wave8_cheyenne_dog_soldiers_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_cheyenne_dog_soldiers_counts(),
        "cohorts": wave8_cheyenne_dog_soldiers_cohort_counts(),
        "final_audit_signature": WAVE8_CHEYENNE_DOG_SOLDIERS_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_CHEYENNE_DOG_SOLDIERS_CONTRACT_IDS),
    }


_validate_static()
