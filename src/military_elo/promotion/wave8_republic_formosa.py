"""Exact-candidate audit of HCED's two ``Republic of Formosa`` rows.

The Republic of Formosa existed only in 1895.  This lane creates one
alias-free, year-bounded identity and uses it only for the fingerprinted
Keelung and Baguashan candidates.  Both rows retain HCED's Japan-over-Formosa
tactical orientation because two independent outcome families support each
result.  The identity-only museum evidence is deliberately excluded from the
outcome-family count.

The March 1895 Pescadores action is pinned as an adjacent predecessor event:
it was fought by Qing China before the republic was proclaimed and already
has a canonical release owner.  No generic Formosa or Taiwan alias is opened,
unknown is never converted to a draw, and unreviewed source coordinates are
withheld without discarding country or provenance.
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
    "WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS",
    "WAVE8_REPUBLIC_FORMOSA_ADJACENT_LITERAL_LABEL_INVENTORY",
    "WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS",
    "WAVE8_REPUBLIC_FORMOSA_CONTRACTS",
    "WAVE8_REPUBLIC_FORMOSA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_REPUBLIC_FORMOSA_ENTITIES",
    "WAVE8_REPUBLIC_FORMOSA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_REPUBLIC_FORMOSA_FUNNEL_AUDIT",
    "WAVE8_REPUBLIC_FORMOSA_HOLD_IDS",
    "WAVE8_REPUBLIC_FORMOSA_HOLDS",
    "WAVE8_REPUBLIC_FORMOSA_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_REPUBLIC_FORMOSA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_REPUBLIC_FORMOSA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_REPUBLIC_FORMOSA_RESERVED_IDS",
    "WAVE8_REPUBLIC_FORMOSA_ROW_HASHES",
    "WAVE8_REPUBLIC_FORMOSA_SOURCES",
    "install_wave8_republic_formosa_entities",
    "install_wave8_republic_formosa_sources",
    "promote_wave8_republic_formosa_contracts",
    "validate_wave8_republic_formosa_current_artifact_state",
    "validate_wave8_republic_formosa_funnel",
    "validate_wave8_republic_formosa_integration_dispositions",
    "validate_wave8_republic_formosa_queue_contracts",
    "wave8_republic_formosa_audit_signature",
    "wave8_republic_formosa_cohort_counts",
    "wave8_republic_formosa_counts",
    "wave8_republic_formosa_metadata",
)


_LANE_NAME = "Wave 8 exact Republic of Formosa audit"
_MODULE_OWNER = "military_elo.promotion.wave8_republic_formosa"
_EVENT_ID_PREFIX = "hced_wave8_republic_formosa_"
_EXACT_LABEL = "republic of formosa"
_COHORT = "japanese_invasion_of_taiwan_1895"

_REPUBLIC_FORMOSA = "republic_of_formosa_1895"
_JAPAN = "empire_japan"


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
        "accessed": "2026-07-20",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_REPUBLIC_FORMOSA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_republic_formosa_ntm_flag",
        "The Flag of the Formosan Republic",
        "https://www.ntm.gov.tw/en/News_Content2.aspx?n=5699&s=149444",
        "National Taiwan Museum",
        "official_museum_history",
        "national_taiwan_museum_formosan_republic",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_republic_formosa_jacar_campaign",
        (
            "The Sino-Japanese War of 1894-1895: Taiwan, the Republic of "
            "Formosa, and the fighting at Keelung and Changhua"
        ),
        (
            "https://www.jacar.go.jp/english/exhibition/"
            "jacarbl-fsjwar-e/smart/about/p005.html"
        ),
        "Japan Center for Asian Historical Records, National Archives of Japan",
        "official_archival_exhibition",
        "jacar_sino_japanese_war_archives",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_republic_formosa_davidson_campaign",
        (
            "James W. Davidson, The Island of Formosa, Past and Present "
            "(1903), chapters on the Japanese occupation of north and mid Formosa"
        ),
        "https://archive.org/details/islandofformosap00davi",
        "Macmillan & Co.; Internet Archive scan from University of California",
        "contemporary_historical_monograph",
        "davidson_island_of_formosa_1903",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_REPUBLIC_FORMOSA_SOURCES
}


# Empty aliases and predecessors are mechanical safeguards.  The year-only
# entity envelope records the source schema's precision; the note pins the
# reviewed day boundaries and forbids continuity inheritance.
WAVE8_REPUBLIC_FORMOSA_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _REPUBLIC_FORMOSA,
        "name": "Republic of Formosa",
        "kind": "unrecognized_republic",
        "start_year": 1895,
        "end_year": 1895,
        "region": "Taiwan",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The year envelope represents only the short-lived Republic of "
            "Formosa: Tang Jingsong was inaugurated on 25 May 1895 and Japanese "
            "forces entered Tainan on 21 October, terminating the republic. Only "
            "the two fingerprinted post-proclamation battles in this lane activate "
            "its Elo. No rating is inherited from Qing Taiwan, local militias, "
            "later anti-Japanese resistance, Japanese Taiwan, or any modern Taiwan "
            "polity."
        ),
        "source_ids": [
            "wave8_republic_formosa_jacar_campaign",
            "wave8_republic_formosa_ntm_flag",
        ],
    },
)


WAVE8_REPUBLIC_FORMOSA_ROW_HASHES: dict[str, str] = {
    "hced-Baguashan1895-1": (
        "0fd6d74272e4d966b21945b43f06e379430fd5df8fdccd55850746519a9cddff"
    ),
    "hced-Keelung1895-1": (
        "970d4f5910dffe14462d32c48e4907a15fc468aa557ff0ccb7fcacc87d964ac2"
    ),
}


# Literal labels close enough to be dangerous are audited across the complete
# queue.  They are empty in the locked snapshot; retaining the empty buckets
# distinguishes "reviewed and absent" from "not checked".
_ADJACENT_LABELS = (
    "formosa republic",
    "formosan republic",
    "republic of taiwan",
    "taiwan republic",
)
WAVE8_REPUBLIC_FORMOSA_ADJACENT_LITERAL_LABEL_INVENTORY: dict[
    str, tuple[str, ...]
] = {label: () for label in _ADJACENT_LABELS}


# Pescadores was fought on 23-24 March, before the Republic was proclaimed.
# It is already correctly owned by the coded HCED pass as Japan versus Qing
# China and is pinned here so temporal/campaign adjacency cannot cause capture.
WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Pescadores1895-1": {
        "raw_row_sha256": (
            "10726f66b36555d7f1601238b18b4f40c55fe821b14b62776cddb2d3492986a5"
        ),
        "disposition": "pre_republic_existing_release_owner",
        "owner_event_id": "hced_hced_pescadores1895_1",
        "reviewed_date": "23-24 March 1895",
        "reviewed_sides": ["Empire of Japan", "Qing China"],
        "result_type": "win",
        "winner": "Empire of Japan",
        "evidence_refs": ["wave8_republic_formosa_jacar_campaign"],
        "reason": (
            "The Pescadores fighting preceded the May proclamation and therefore "
            "cannot be assigned to the Republic of Formosa; retain its existing "
            "Japan-versus-Qing release owner."
        ),
    }
}


WAVE8_REPUBLIC_FORMOSA_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "991d150c3d6810a759604ce2d54af6f088fc32efd80cd12103f16a933258fb0b"
    ),
    "events_touched": 2,
    "label": _EXACT_LABEL,
    "rated_counterpart_entities": 1,
    "sole_blocker_events": 2,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 2,
    "zero_time_valid_candidates": 2,
}


def _canonical(
    name: str,
    date_text: str,
    *,
    date_precision: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:1895:1895",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": 1895,
        "year_high": 1895,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    reviewed_outcome: str,
    event_boundary: str,
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(_SOURCE_BY_ID)
    outcomes = sorted(
        {
            "wave8_republic_formosa_davidson_campaign",
            "wave8_republic_formosa_jacar_campaign",
        }
    )
    return {
        "raw_row_sha256": WAVE8_REPUBLIC_FORMOSA_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "side_1_entity_ids": [_JAPAN],
        "side_2_entity_ids": [_REPUBLIC_FORMOSA],
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
        "actor_override": "candidate_keyed_republic_of_formosa_1895",
        "direct_provenance": {
            "reviewed_date": str(canonical_event["date_text"]),
            "reviewed_sides": [
                "Empire of Japan expeditionary force",
                "Republic of Formosa forces",
            ],
            "reviewed_outcome": reviewed_outcome,
            "event_boundary": event_boundary,
        },
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_REPUBLIC_FORMOSA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Keelung1895-1": _contract(
        "hced-Keelung1895-1",
        _canonical(
            "Battle of Keelung (1895)",
            "2-3 June 1895",
            date_precision="day_range",
            granularity="two_day_battle_and_port_capture",
        ),
        "Japanese tactical victory; Formosan attacks failed and Keelung fell",
        "2-3 June field and fortified fighting immediately east of Keelung",
        (
            "JACAR's archive-based campaign history and Davidson's contemporary "
            "account independently record the Republic's inability to stop the "
            "Japanese advance and the capture of Keelung. Only the bounded "
            "tactical battle is rated, not the occupation of Taipei or the war."
        ),
        confidence=0.97,
    ),
    "hced-Baguashan1895-1": _contract(
        "hced-Baguashan1895-1",
        _canonical(
            "Battle of Baguashan",
            "27 August 1895",
            date_precision="day",
            granularity="single_day_pitched_battle_and_fort_capture",
        ),
        "Japanese tactical victory; Baguashan fort and Changhua were taken",
        "27 August river crossing, Baguashan fort assault, and Changhua fighting",
        (
            "JACAR records the Formosan defeat and retreat at Changhua, while "
            "Davidson independently describes the 27 August crossing, capture of "
            "the Baguashan fort, and seizure of Changhua. No campaign-level "
            "collapse or later colonial result is inferred."
        ),
        confidence=0.98,
    ),
}


# The complete exact-label inventory is promotable; no uncertain exact or
# adjacent actor row is silently dropped.  Empty hold inventory is itself
# signature-pinned and queue-validated.
WAVE8_REPUBLIC_FORMOSA_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS = frozenset(
    WAVE8_REPUBLIC_FORMOSA_CONTRACTS
)
WAVE8_REPUBLIC_FORMOSA_HOLD_IDS = frozenset(WAVE8_REPUBLIC_FORMOSA_HOLDS)
WAVE8_REPUBLIC_FORMOSA_RESERVED_IDS = frozenset(
    {*WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS, *WAVE8_REPUBLIC_FORMOSA_HOLD_IDS}
)

WAVE8_REPUBLIC_FORMOSA_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS
)
WAVE8_REPUBLIC_FORMOSA_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = (
    frozenset()
)
WAVE8_REPUBLIC_FORMOSA_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "HCED provides an unexplained place centroid, not a reviewed battle "
            "position or battlefield footprint. Withhold point geometry while "
            "retaining the source-bound Taiwan jurisdiction and location provenance."
        ),
        "evidence_refs": sorted(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(
        WAVE8_REPUBLIC_FORMOSA_CONTRACTS.items()
    )
}


WAVE8_REPUBLIC_FORMOSA_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Keelung1895-1": {
        "aliases": [
            "battle of jilong",
            "battle of keelung",
            "chilung",
            "jilong",
            "keelung",
            "kelung",
        ],
        "years": [1895, 1895],
    },
    "hced-Baguashan1895-1": {
        "aliases": [
            "bagua mountain",
            "bagua shan",
            "baguashan",
            "battle of baguashan",
            "battle of changhua",
            "changhua",
            "changwha",
            "mount bagua",
        ],
        "years": [1895, 1895],
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_hced_dispositions": (
            WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS
        ),
        "adjacent_literal_label_inventory": (
            WAVE8_REPUBLIC_FORMOSA_ADJACENT_LITERAL_LABEL_INVENTORY
        ),
        "contracts": WAVE8_REPUBLIC_FORMOSA_CONTRACTS,
        "entities": WAVE8_REPUBLIC_FORMOSA_ENTITIES,
        "funnel": WAVE8_REPUBLIC_FORMOSA_FUNNEL_AUDIT,
        "holds": WAVE8_REPUBLIC_FORMOSA_HOLDS,
        "iwbd_zero_overlap_audit": (
            WAVE8_REPUBLIC_FORMOSA_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "location_reasons": WAVE8_REPUBLIC_FORMOSA_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_REPUBLIC_FORMOSA_ROW_HASHES,
        "sources": WAVE8_REPUBLIC_FORMOSA_SOURCES,
    }


def wave8_republic_formosa_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_REPUBLIC_FORMOSA_FINAL_AUDIT_SIGNATURE = (
    "4bde800edb6ad6d43c105eb9f008161db7620ec80e9f1de61c6c60512f29858c"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_REPUBLIC_FORMOSA_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if {str(entity["id"]) for entity in WAVE8_REPUBLIC_FORMOSA_ENTITIES} != {
        _REPUBLIC_FORMOSA
    }:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS != set(
        WAVE8_REPUBLIC_FORMOSA_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} exact disposition inventory drift")
    if WAVE8_REPUBLIC_FORMOSA_HOLDS or WAVE8_REPUBLIC_FORMOSA_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited hold")
    if (
        WAVE8_REPUBLIC_FORMOSA_POINT_QUARANTINE_ADDITIONS
        != WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS
        or WAVE8_REPUBLIC_FORMOSA_COUNTRY_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location policy drift")
    if set(WAVE8_REPUBLIC_FORMOSA_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")
    if set(WAVE8_REPUBLIC_FORMOSA_ADJACENT_LITERAL_LABEL_INVENTORY) != set(
        _ADJACENT_LABELS
    ) or any(WAVE8_REPUBLIC_FORMOSA_ADJACENT_LITERAL_LABEL_INVENTORY.values()):
        raise ValueError(f"{_LANE_NAME} adjacent literal-label audit drift")
    if set(WAVE8_REPUBLIC_FORMOSA_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for audit in WAVE8_REPUBLIC_FORMOSA_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, audit["aliases"]))
        years = list(map(int, audit["years"]))
        if (
            not _is_sorted_unique(aliases)
            or any(alias != normalize_label(alias) for alias in aliases)
            or years != [1895, 1895]
        ):
            raise ValueError(f"{_LANE_NAME} duplicate negative audit drift")

    entity = WAVE8_REPUBLIC_FORMOSA_ENTITIES[0]
    if entity["aliases"] or entity["predecessors"]:
        raise ValueError(f"{_LANE_NAME} broad alias or continuity inheritance opened")
    if (entity["start_year"], entity["end_year"]) != (1895, 1895):
        raise ValueError(f"{_LANE_NAME} identity window drift")
    if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
        raise ValueError(f"{_LANE_NAME} inheritance guard drift")
    if not _is_sorted_unique(entity["source_ids"]):
        raise ValueError(f"{_LANE_NAME} entity source order drift")

    identity_only_id = "wave8_republic_formosa_ntm_flag"
    if "outcome" in _SOURCE_BY_ID[identity_only_id]["evidence_roles"]:
        raise ValueError(f"{_LANE_NAME} identity-only evidence became an outcome")

    used_sources = set(map(str, entity["source_ids"]))
    expected_sides = ([_JAPAN], [_REPUBLIC_FORMOSA])
    for candidate_id, contract in WAVE8_REPUBLIC_FORMOSA_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or (
                contract["side_1_entity_ids"],
                contract["side_2_entity_ids"],
            )
            != expected_sides
        ):
            raise ValueError(f"{_LANE_NAME} actor or outcome drift: {candidate_id}")
        canonical = contract["canonical_event"]
        provenance = contract["direct_provenance"]
        if (
            canonical["year_low"] != 1895
            or canonical["year_high"] != 1895
            or provenance["reviewed_date"] != canonical["date_text"]
            or not provenance["reviewed_outcome"]
            or not provenance["event_boundary"]
        ):
            raise ValueError(f"{_LANE_NAME} date or granularity drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence order drift: {candidate_id}")
        if not set(outcomes) <= set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        if identity_only_id in outcomes or any(
            "outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} non-outcome evidence rates {candidate_id}")
        families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)

    adjacent = WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS[
        "hced-Pescadores1895-1"
    ]
    if (
        adjacent["disposition"] != "pre_republic_existing_release_owner"
        or adjacent["owner_event_id"] != "hced_hced_pescadores1895_1"
        or adjacent["result_type"] != "win"
        or adjacent["winner"] != "Empire of Japan"
    ):
        raise ValueError(f"{_LANE_NAME} Pescadores ownership drift")
    used_sources.update(map(str, adjacent["evidence_refs"]))

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_republic_formosa_audit_signature() != (
        WAVE8_REPUBLIC_FORMOSA_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def _actor_labels(row: Mapping[str, Any]) -> set[str]:
    return {
        normalize_label(row.get("side_1_raw")),
        normalize_label(row.get("side_2_raw")),
    }


def _is_1895_taiwan_campaign_row(row: Mapping[str, Any]) -> bool:
    try:
        overlaps_1895 = int(row.get("year_low")) <= 1895 <= int(
            row.get("year_high")
        )
    except (TypeError, ValueError):
        return False
    war_names = {normalize_label(name) for name in row.get("war_names", []) or []}
    return (
        overlaps_1895
        and row.get("modern_location_country") == "Taiwan"
        and "sino japanese war" in war_names
    )


def validate_wave8_republic_formosa_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin every exact, spelling-adjacent, and 1895 campaign-adjacent row."""

    _validate_static()
    exact_rows = [row for row in hced_rows if _EXACT_LABEL in _actor_labels(row)]
    exact_ids = {str(row.get("candidate_id")) for row in exact_rows}
    if exact_ids != WAVE8_REPUBLIC_FORMOSA_RESERVED_IDS or len(exact_rows) != len(
        exact_ids
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")

    actual_adjacent = {
        label: tuple(
            sorted(
                str(row.get("candidate_id"))
                for row in hced_rows
                if label in _actor_labels(row)
            )
        )
        for label in _ADJACENT_LABELS
    }
    if actual_adjacent != WAVE8_REPUBLIC_FORMOSA_ADJACENT_LITERAL_LABEL_INVENTORY:
        raise ValueError(f"{_LANE_NAME} adjacent-label inventory changed")

    expected_campaign_ids = {
        *WAVE8_REPUBLIC_FORMOSA_RESERVED_IDS,
        *WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS,
    }
    campaign_rows = [row for row in hced_rows if _is_1895_taiwan_campaign_row(row)]
    campaign_by_id = {str(row.get("candidate_id")): row for row in campaign_rows}
    if set(campaign_by_id) != expected_campaign_ids or len(campaign_rows) != len(
        campaign_by_id
    ):
        raise ValueError(f"{_LANE_NAME} 1895 Taiwan campaign inventory changed")

    by_id = {str(row["candidate_id"]): row for row in exact_rows}
    for candidate_id, expected_hash in WAVE8_REPUBLIC_FORMOSA_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            int(row["year_low"]),
            int(row["year_best"]),
            int(row["year_high"]),
        ) != (1895, 1895, 1895):
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if (
            row.get("side_1_raw") != "Japan"
            or row.get("side_2_raw") != "Republic of Formosa"
            or row.get("winner_raw") != "Japan"
            or row.get("loser_raw") != "Republic of Formosa"
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
        ):
            raise ValueError(f"{_LANE_NAME} actor or outcome alignment changed")

    for candidate_id, disposition in (
        WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS.items()
    ):
        row = campaign_by_id[candidate_id]
        if canonical_hced_row_sha256(row) != disposition["raw_row_sha256"]:
            raise ValueError(
                f"{_LANE_NAME} adjacent row fingerprint changed: {candidate_id}"
            )
        if (
            row.get("side_1_raw"),
            row.get("side_2_raw"),
            row.get("winner_raw"),
            row.get("loser_raw"),
        ) != ("Japan", "China", "Japan", "China"):
            raise ValueError(f"{_LANE_NAME} adjacent actor orientation changed")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_REPUBLIC_FORMOSA_CONTRACTS,
        WAVE8_REPUBLIC_FORMOSA_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "adjacent_campaign_rows": len(
            WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS
        ),
        "adjacent_literal_label_rows": sum(map(len, actual_adjacent.values())),
        "exact_label_rows": len(exact_rows),
        "full_1895_taiwan_campaign_rows": len(campaign_rows),
    }


def validate_wave8_republic_formosa_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    matches = [
        row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL
    ]
    if len(matches) != 1:
        raise ValueError(f"{_LANE_NAME} expected exactly one funnel row")
    row = matches[0]
    actual = {
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
    if actual != WAVE8_REPUBLIC_FORMOSA_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pin changed: {actual}")
    return {
        "events_touched": actual["events_touched"],
        "sole_blocker_events": actual["sole_blocker_events"],
        "unresolved_side_attempts": actual["unresolved_side_attempts"],
        "zero_time_valid_candidates": actual["zero_time_valid_candidates"],
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        try:
            if row.get(field) is not None:
                return int(row[field])
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        text = str(row.get(field) or "")
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4])
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


_DUPLICATE_MATCH_KEYS = frozenset(
    (year, alias)
    for audit in WAVE8_REPUBLIC_FORMOSA_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_republic_formosa_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Reject unreviewed twins, adjacent-owner drift, and partial integration."""

    validate_wave8_republic_formosa_queue_contracts(hced_rows)
    events = list(existing_events)
    event_by_candidate = {
        str(event["hced_candidate_id"]): event
        for event in events
        if event.get("hced_candidate_id") is not None
    }
    lane_overlap = WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS & set(event_by_candidate)
    if len(lane_overlap) not in {0, len(WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS)}:
        raise ValueError(f"{_LANE_NAME} partial release integration")
    for candidate_id in lane_overlap:
        if not str(event_by_candidate[candidate_id].get("id", "")).startswith(
            _EVENT_ID_PREFIX
        ):
            raise ValueError(f"{_LANE_NAME} release owner drift: {candidate_id}")

    if events:
        for candidate_id, disposition in (
            WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS.items()
        ):
            owner = event_by_candidate.get(candidate_id)
            if owner is None or str(owner.get("id")) != disposition["owner_event_id"]:
                raise ValueError(f"{_LANE_NAME} adjacent release owner drift")

    allowed_hced = {
        *WAVE8_REPUBLIC_FORMOSA_RESERVED_IDS,
        *WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS,
    }
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in allowed_hced
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
        if event.get("hced_candidate_id") not in (
            WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS
        )
        and _is_probable_twin(event)
    )
    if hced_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"iwbd={iwbd_twins}, release={release_twins}"
        )
    return {
        "adjacent_existing_release_owners": 1 if events else 0,
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwbd_probable_twins": 0,
        "release_lane_overlap": len(lane_overlap),
    }


def install_wave8_republic_formosa_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_REPUBLIC_FORMOSA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_republic_formosa_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_REPUBLIC_FORMOSA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_REPUBLIC_FORMOSA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_REPUBLIC_FORMOSA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_republic_formosa_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_republic_formosa_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_REPUBLIC_FORMOSA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def _records_by_id(
    records: Iterable[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    return {str(record["id"]): record for record in records}


def validate_wave8_republic_formosa_current_artifact_state(
    release_entities: Iterable[Mapping[str, Any]],
    release_events: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
    release_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Require release entity, sources, events, and metadata to move together."""

    _validate_static()
    entity_by_id = _records_by_id(release_entities)
    source_by_id = _records_by_id(release_sources)
    events = list(release_events)
    expected_source_ids = set(_SOURCE_BY_ID)
    source_overlap = expected_source_ids & set(source_by_id)
    target_events = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS
    ]
    prefixed_events = [
        event
        for event in events
        if str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    entity_present = _REPUBLIC_FORMOSA in entity_by_id
    promotion = (
        release_metadata.get("promotion", {}) if release_metadata is not None else {}
    )
    marker_present = "accepted_wave8_republic_formosa_hced_events" in promotion

    any_present = bool(
        entity_present
        or source_overlap
        or target_events
        or prefixed_events
        or marker_present
    )
    if not any_present:
        return {
            "entity_records": 0,
            "event_records": 0,
            "integration_state": "preintegration",
            "metadata_marker": 0,
            "source_records": 0,
        }

    fully_present = (
        entity_present
        and source_overlap == expected_source_ids
        and len(target_events) == len(WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS)
        and len(prefixed_events) == len(WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS)
        and (release_metadata is None or marker_present)
    )
    if not fully_present:
        raise ValueError(f"{_LANE_NAME} partial current-artifact integration")
    if entity_by_id[_REPUBLIC_FORMOSA] != WAVE8_REPUBLIC_FORMOSA_ENTITIES[0]:
        raise ValueError(f"{_LANE_NAME} current entity drift")
    for source_id in expected_source_ids:
        if source_by_id[source_id] != _SOURCE_BY_ID[source_id]:
            raise ValueError(f"{_LANE_NAME} current source drift: {source_id}")

    event_by_candidate = {
        str(event["hced_candidate_id"]): event for event in target_events
    }
    if set(event_by_candidate) != WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} current event inventory drift")
    for candidate_id, event in event_by_candidate.items():
        if not str(event.get("id", "")).startswith(_EVENT_ID_PREFIX):
            raise ValueError(f"{_LANE_NAME} current event owner drift")
        participant_ids = {
            str(participant.get("entity_id"))
            for participant in event.get("participants", [])
        }
        if participant_ids != {_JAPAN, _REPUBLIC_FORMOSA}:
            raise ValueError(f"{_LANE_NAME} current event actor drift")
        if "geometry" in event:
            raise ValueError(f"{_LANE_NAME} quarantined point entered release")
        if event.get("modern_location_country") != "Taiwan" or not event.get(
            "location_provenance"
        ):
            raise ValueError(f"{_LANE_NAME} country/provenance drift")
        if set(map(str, event.get("outcome_source_ids", []))) != set(
            WAVE8_REPUBLIC_FORMOSA_CONTRACTS[candidate_id]["outcome_source_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} current outcome provenance drift")

    if release_metadata is not None:
        if int(promotion["accepted_wave8_republic_formosa_hced_events"]) != 2:
            raise ValueError(f"{_LANE_NAME} current metadata count drift")
        candidate_ids = promotion.get("wave8_republic_formosa_candidate_ids")
        if candidate_ids is None or list(map(str, candidate_ids)) != sorted(
            WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS
        ):
            raise ValueError(f"{_LANE_NAME} current metadata inventory drift")

    return {
        "entity_records": 1,
        "event_records": len(target_events),
        "integration_state": "integrated",
        "metadata_marker": 1 if marker_present else 0,
        "source_records": len(source_overlap),
    }


def wave8_republic_formosa_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_REPUBLIC_FORMOSA_CONTRACTS.values(),
                    *WAVE8_REPUBLIC_FORMOSA_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_republic_formosa_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_campaign_dispositions": len(
            WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS
        ),
        "adjacent_literal_label_rows": sum(
            map(
                len,
                WAVE8_REPUBLIC_FORMOSA_ADJACENT_LITERAL_LABEL_INVENTORY.values(),
            )
        ),
        "country_quarantine_additions": 0,
        "holds": len(WAVE8_REPUBLIC_FORMOSA_HOLDS),
        "new_entities": len(WAVE8_REPUBLIC_FORMOSA_ENTITIES),
        "new_sources": len(WAVE8_REPUBLIC_FORMOSA_SOURCES),
        "newly_rated_events": len(WAVE8_REPUBLIC_FORMOSA_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_REPUBLIC_FORMOSA_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_REPUBLIC_FORMOSA_CONTRACTS),
        "reviewed_hced_rows": (
            len(WAVE8_REPUBLIC_FORMOSA_RESERVED_IDS)
            + len(WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS)
        ),
        "terminal_exclusions": 0,
    }


def wave8_republic_formosa_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "adjacent_hced_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_REPUBLIC_FORMOSA_ADJACENT_HCED_DISPOSITIONS.items()
            )
        ],
        "cohorts": wave8_republic_formosa_cohort_counts(),
        "counts": wave8_republic_formosa_counts(),
        "final_audit_signature": WAVE8_REPUBLIC_FORMOSA_FINAL_AUDIT_SIGNATURE,
        "hold_candidate_ids": sorted(WAVE8_REPUBLIC_FORMOSA_HOLD_IDS),
        "promoted_candidate_ids": sorted(WAVE8_REPUBLIC_FORMOSA_CONTRACT_IDS),
    }


_validate_static()
