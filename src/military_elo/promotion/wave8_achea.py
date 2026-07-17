"""Candidate-keyed audit of HCED's three unresolved ``Achea`` rows.

``Achea`` is a source misspelling for the already catalogued Achaean League,
not a new polity and not a safe global alias.  This lane therefore reuses the
time-bounded Cliopatria identity only for the three fingerprinted battles whose
actors and tactical outcomes are independently attested: Ladoceia, Mantinea
(207 BCE), and the fighting near Mount Barbosthenes (192 BCE).
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
    "WAVE8_ACHEA_CONTRACT_IDS",
    "WAVE8_ACHEA_CONTRACTS",
    "WAVE8_ACHEA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ACHEA_ENTITIES",
    "WAVE8_ACHEA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ACHEA_FUNNEL_AUDIT",
    "WAVE8_ACHEA_HOLDS",
    "WAVE8_ACHEA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_ACHEA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ACHEA_RESERVED_IDS",
    "WAVE8_ACHEA_ROW_HASHES",
    "WAVE8_ACHEA_SOURCES",
    "install_wave8_achea_entities",
    "install_wave8_achea_sources",
    "promote_wave8_achea_contracts",
    "validate_wave8_achea_funnel",
    "validate_wave8_achea_integration_dispositions",
    "validate_wave8_achea_queue_contracts",
    "wave8_achea_audit_signature",
    "wave8_achea_cohort_counts",
    "wave8_achea_counts",
    "wave8_achea_metadata",
)


_LANE_NAME = "Wave 8 exact Achea actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_achea"
_EVENT_ID_PREFIX = "hced_wave8_achea_"
_EXACT_LABEL = "achea"

_ACHAEAN_LEAGUE = "clio_q244796_bce279_0be1ca53"
_SPARTA = "sparta"


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
        "accessed": "2026-07-17",
        "source_family_id": source_family_id,
        "evidence_roles": ["identity_boundary_or_context_reference", "outcome"],
    }


WAVE8_ACHEA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_achea_polybius_book2_ladoceia",
        "Polybius, Histories 2.51: the Achaean defeat at Ladoceia",
        (
            "https://www.perseus.tufts.edu/hopper/text?doc="
            "Perseus%3Atext%3A1999.01.0234%3Abook%3D2"
        ),
        "Perseus Digital Library, Tufts University",
        "ancient_primary_narrative_in_scholarly_edition",
        "polybius_histories",
    ),
    _source(
        "wave8_achea_plutarch_cleomenes_ladoceia",
        "Plutarch, Life of Cleomenes 6: Lydiadas and the rout of the Achaeans",
        (
            "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/"
            "Lives/Cleomenes%2A.html"
        ),
        "LacusCurtius, University of Chicago",
        "ancient_primary_narrative_in_scholarly_edition",
        "plutarch_parallel_lives",
    ),
    _source(
        "wave8_achea_polybius_book11_mantinea",
        "Polybius, Histories 11.11-18: the Battle of Mantinea (207 BCE)",
        (
            "https://www.perseus.tufts.edu/hopper/text?doc="
            "Perseus%3Atext%3A1999.01.0234%3Abook%3D11"
        ),
        "Perseus Digital Library, Tufts University",
        "ancient_primary_narrative_in_scholarly_edition",
        "polybius_histories",
    ),
    _source(
        "wave8_achea_plutarch_philopoemen",
        "Plutarch, Life of Philopoemen: Mantinea and the campaign against Nabis",
        "https://classics.mit.edu/Plutarch/philopoe.html",
        "Internet Classics Archive, Massachusetts Institute of Technology",
        "ancient_primary_narrative_translation",
        "plutarch_parallel_lives",
    ),
    _source(
        "wave8_achea_livy_book35_barbosthenes",
        "Livy, History of Rome 35.29-30: Philopoemen's victory over Nabis",
        (
            "https://www.perseus.tufts.edu/hopper/text?doc="
            "Perseus%3Atext%3A1999.02.0165%3Abook%3D35"
        ),
        "Perseus Digital Library, Tufts University",
        "ancient_primary_narrative_in_scholarly_edition",
        "livy_ab_urbe_condita",
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_ACHEA_SOURCES}


# The correct identity already exists in the release candidate catalogue and
# already participates in provisional events.  An empty tranche is intentional:
# these exact contracts extend that Elo history without manufacturing a
# duplicate identity, opening a generic alias, or silently upgrading the
# source-candidate identity to curated status.
WAVE8_ACHEA_ENTITIES: tuple[dict[str, Any], ...] = ()


WAVE8_ACHEA_ROW_HASHES: dict[str, str] = {
    "hced-Ladoceia-227-1": (
        "23092227dcae3210d2243a74b8eba96675ac51ee49b7e8809eaaad436a6ccd7e"
    ),
    "hced-Mantinea-207-1": (
        "2d4412bf39ab55704cf03db9689900b6edb353fe95dd35ea936d3d6deb448c51"
    ),
    "hced-Mount Barbosthene-192-1": (
        "504f679e2d700f5f99813c787f6fb72bb581ca07e8020f182e204efab2b39171"
    ),
}

WAVE8_ACHEA_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "38f02d97127f467d00b055bd789b10ba4b1fe93c29b00e5e81b3be87b86aa657"
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
        "date_text": f"{abs(year)} BCE",
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_ACHEA_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "achaean_league_spartan_wars_227_192_bce",
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
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
        "actor_override": "candidate_keyed_existing_achaean_league_identity",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_ACHEA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Ladoceia-227-1": _contract(
        "hced-Ladoceia-227-1",
        _canonical(
            "Battle of Ladoceia",
            -227,
            "single_battle_in_the_cleomenean_war",
        ),
        [_SPARTA],
        [_ACHAEAN_LEAGUE],
        [
            "wave8_achea_plutarch_cleomenes_ladoceia",
            "wave8_achea_polybius_book2_ladoceia",
        ],
        (
            "Polybius identifies Ladoceia as a pitched Achaean defeat, and "
            "Plutarch describes Cleomenes routing the entire Achaean army after "
            "Lydiadas fell. The contract retains only that tactical result."
        ),
        confidence=0.92,
    ),
    "hced-Mantinea-207-1": _contract(
        "hced-Mantinea-207-1",
        _canonical(
            "Battle of Mantinea (207 BCE)",
            -207,
            "single_battle_against_machanidas_spartan_army",
        ),
        [_ACHAEAN_LEAGUE],
        [_SPARTA],
        [
            "wave8_achea_plutarch_philopoemen",
            "wave8_achea_polybius_book11_mantinea",
        ],
        (
            "Polybius's detailed battle narrative records the Lacedaemonian "
            "defeat and rout; Plutarch independently preserves Philopoemen's "
            "Achaean victory and the death of Machanidas."
        ),
        confidence=0.96,
    ),
    "hced-Mount Barbosthene-192-1": _contract(
        "hced-Mount Barbosthene-192-1",
        _canonical(
            "Battle near Mount Barbosthenes",
            -192,
            "single_land_battle_in_philopoemen_nabis_campaign",
        ),
        [_ACHAEAN_LEAGUE],
        [_SPARTA],
        [
            "wave8_achea_livy_book35_barbosthenes",
            "wave8_achea_plutarch_philopoemen",
        ],
        (
            "Livy records Philopoemen routing Nabis's force, pursuing it, and "
            "cutting off most fugitives near the Barbosthenes route; Plutarch "
            "preserves the same Achaean tactical victory in rough terrain."
        ),
        confidence=0.92,
    ),
}


WAVE8_ACHEA_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_ACHEA_CONTRACT_IDS = frozenset(WAVE8_ACHEA_CONTRACTS)
WAVE8_ACHEA_RESERVED_IDS = WAVE8_ACHEA_CONTRACT_IDS
WAVE8_ACHEA_POINT_QUARANTINE_ADDITIONS = WAVE8_ACHEA_CONTRACT_IDS
WAVE8_ACHEA_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_ACHEA_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed texts establish the named battlefield and Greek "
            "setting but do not independently verify HCED's exact coordinate; "
            "retain the country assertion and withhold the point."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_ACHEA_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_ACHEA_CONTRACTS,
        "entities": WAVE8_ACHEA_ENTITIES,
        "funnel": WAVE8_ACHEA_FUNNEL_AUDIT,
        "holds": WAVE8_ACHEA_HOLDS,
        "location_reasons": WAVE8_ACHEA_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_ACHEA_ROW_HASHES,
        "sources": WAVE8_ACHEA_SOURCES,
    }


def wave8_achea_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_ACHEA_FINAL_AUDIT_SIGNATURE = (
    "54a097ca2b6d7b7ce28d68ad6eecf0a5692903f777137f1c53257af176a62291"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_ACHEA_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if WAVE8_ACHEA_ENTITIES:
        raise ValueError(f"{_LANE_NAME} must reuse the existing Achaean identity")
    if WAVE8_ACHEA_RESERVED_IDS != set(WAVE8_ACHEA_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_ACHEA_HOLDS:
        raise ValueError(f"{_LANE_NAME} unexpected hold inventory")
    if WAVE8_ACHEA_POINT_QUARANTINE_ADDITIONS != WAVE8_ACHEA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_ACHEA_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_ACHEA_LOCATION_QUARANTINE_REASONS) != WAVE8_ACHEA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    used_sources: set[str] = set()
    allowed_actors = {_ACHAEAN_LEAGUE, _SPARTA}
    for candidate_id, contract in WAVE8_ACHEA_CONTRACTS.items():
        if contract["disposition"] != "promote" or contract["result_type"] != "win":
            raise ValueError(f"{_LANE_NAME} disposition drift: {candidate_id}")
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
        year_low = int(contract["canonical_event"]["year_low"])
        year_high = int(contract["canonical_event"]["year_high"])
        if not (-279 <= year_low <= year_high <= -145):
            raise ValueError(f"{_LANE_NAME} Achaean identity-window drift: {candidate_id}")
        used_sources.update(evidence)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_achea_audit_signature() != WAVE8_ACHEA_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_achea_queue_contracts(
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
    if exact_ids != WAVE8_ACHEA_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_ACHEA_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("year_low") != row.get("year_high") or row.get("year_best") != row.get(
            "year_low"
        ):
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if row.get("winner_raw") not in {row.get("side_1_raw"), row.get("side_2_raw")}:
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True or row.get("massacre_raw") != "No":
            raise ValueError(f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ACHEA_CONTRACTS,
        WAVE8_ACHEA_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_achea_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
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
    if checks != WAVE8_ACHEA_FUNNEL_AUDIT:
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
    "hced-Ladoceia-227-1": {"Ladoceia", "Ladocaea", "Battle of Ladoceia"},
    "hced-Mantinea-207-1": {
        "Mantinea",
        "Mantineia",
        "Battle of Mantinea (207 BCE)",
    },
    "hced-Mount Barbosthene-192-1": {
        "Mount Barbosthene",
        "Mount Barbosthenes",
        "Mount Barnosthenes",
        "Battle near Mount Barbosthenes",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (int(WAVE8_ACHEA_CONTRACTS[candidate_id]["canonical_event"]["year_low"]), normalize_label(alias))
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_achea_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_achea_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_ACHEA_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_ACHEA_CONTRACT_IDS
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


def install_wave8_achea_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ACHEA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_achea_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_ACHEA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_ACHEA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_ACHEA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_achea_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_achea_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ACHEA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_achea_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_ACHEA_CONTRACTS.values(),
                    *WAVE8_ACHEA_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_achea_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": 0,
        "new_entities": 0,
        "new_sources": len(WAVE8_ACHEA_SOURCES),
        "newly_rated_events": len(WAVE8_ACHEA_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(WAVE8_ACHEA_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_ACHEA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_ACHEA_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_achea_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_achea_counts(),
        "cohorts": wave8_achea_cohort_counts(),
        "final_audit_signature": WAVE8_ACHEA_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_ACHEA_CONTRACT_IDS),
    }


_validate_static()
