"""Candidate-keyed audit of HCED's three unresolved ``Algeria`` Oran rows.

``Algeria`` in these eighteenth-century rows denotes the Dey-ruled Regency of
Algiers, already registered and rated as ``dey_regency_of_algiers_1671_1830``;
the modern republic candidate the funnel offers is a wrong-interval match and
no ``algeria`` alias may ever open.  This lane binds exactly two adjudicated
Oran contests to the existing identity and holds the third: the 1707-1708
Algerian recapture under Bey Mustapha Bouchelaghem (event year pinned to 1708,
the year the city fell), the 1732 Spanish reconquest under the Duke of
Montemar, and a hold on the thinly documented 1780 row, whose coded Spanish
victory has no dedicated scholarly account of a discrete engagement.  Unknown
is not a draw, so the 1780 row stays unscored pending a documented override.
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
    "WAVE8_ORAN_CONTRACT_IDS",
    "WAVE8_ORAN_CONTRACTS",
    "WAVE8_ORAN_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ORAN_ENTITIES",
    "WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS",
    "WAVE8_ORAN_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ORAN_FUNNEL_AUDIT",
    "WAVE8_ORAN_HOLDS",
    "WAVE8_ORAN_LOCATION_QUARANTINE_REASONS",
    "WAVE8_ORAN_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ORAN_RESERVED_IDS",
    "WAVE8_ORAN_ROW_HASHES",
    "WAVE8_ORAN_SOURCES",
    "install_wave8_oran_entities",
    "install_wave8_oran_sources",
    "promote_wave8_oran_contracts",
    "validate_wave8_oran_funnel",
    "validate_wave8_oran_integration_dispositions",
    "validate_wave8_oran_queue_contracts",
    "wave8_oran_audit_signature",
    "wave8_oran_cohort_counts",
    "wave8_oran_counts",
    "wave8_oran_metadata",
)


_LANE_NAME = "Wave 8 exact Oran Regency of Algiers audit"
_MODULE_OWNER = "military_elo.promotion.wave8_oran"
_EVENT_ID_PREFIX = "hced_wave8_oran_"
_EXACT_LABEL = "algeria"

_REGENCY = "dey_regency_of_algiers_1671_1830"
_SPAIN = "spanish_empire"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    evidence_roles: tuple[str, ...] = (
        "identity_boundary_or_context_reference",
        "outcome",
    ),
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
        "evidence_roles": list(evidence_roles),
    }


WAVE8_ORAN_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_oran_rah_dbe_montemar",
        (
            "Diccionario Biografico espanol: Jose Ignacio Carrillo de Albornoz "
            "y Montiel, duque de Montemar"
        ),
        (
            "https://dbe.rah.es/biografias/13738/"
            "jose-ignacio-carrillo-de-albornoz-y-montiel"
        ),
        "Real Academia de la Historia",
        "national_academy_biographical_dictionary",
        "real_academia_historia_dbe",
    ),
    _source(
        "wave8_oran_jaques_dictionary",
        "Dictionary of Battles and Sieges",
        "https://books.google.com/books?id=w_XCEAAAQBAJ",
        "Greenwood / Bloomsbury Academic; Google Books",
        "expert_reviewed_military_reference",
        "jaques_dictionary_battles_2006",
    ),
    _source(
        "wave8_oran_clodfelter_warfare",
        "Warfare and Armed Conflicts: A Statistical Encyclopedia",
        "https://books.google.com/books?id=8urEDgAAQBAJ&pg=PA75&vq=Oran",
        "McFarland / Google Books",
        "scholarly_reference_work",
        "clodfelter_warfare_armed_conflicts",
    ),
    _source(
        "wave8_oran_wikipedia_spanish_algerian_war",
        "Spanish-Algerian War (1775-1785): campaign record without a discrete "
        "1780 Oran engagement",
        (
            "https://en.wikipedia.org/wiki/"
            "Spanish%E2%80%93Algerian_War_(1775%E2%80%931785)"
        ),
        "Wikipedia (context reference only)",
        "collaborative_encyclopedia_context_reference",
        "wikipedia_english",
        evidence_roles=("identity_boundary_or_context_reference",),
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_ORAN_SOURCES}


# Both belligerent identities already exist and are rated; an empty tranche is
# deliberate.  These contracts extend the Regency's Elo history without
# opening a generic ``algeria`` alias, without touching the wrong-interval
# modern-republic candidate, and without any window change anywhere.
WAVE8_ORAN_ENTITIES: tuple[dict[str, Any], ...] = ()


WAVE8_ORAN_ROW_HASHES: dict[str, str] = {
    "hced-Oran1704-1708-1": (
        "d2fc14ed22d8f4b534390e86df260140367e14ce13f503641352e5a10df83943"
    ),
    "hced-Oran1732-1": (
        "bc69deee0b2fe1c147708b834abd890123946effca5e953de3119aeb2b3216ad"
    ),
    "hced-Oran1780-1": (
        "4f2e74e9204c0033a11ec59ec3cd0e0279ead3e2e6ad000a8d623bbb87e6599d"
    ),
}

# Pre-promotion projection of the live funnel at this lane's audit moment: the
# three rows stalled as one_wrong_interval_candidate because the only offered
# identity was the 1963 modern republic.
WAVE8_ORAN_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": ["clio_q262_1963_de9ecdb4"],
    "event_candidate_id_sha256": (
        "b42353b5f80755294e7ddf3a9aed1dbccc61978d77696429b2deb23631188842"
    ),
    "events_touched": 3,
    "label": _EXACT_LABEL,
    "one_wrong_interval_candidate": 3,
    "sole_blocker_events": 3,
}


def _canonical(
    name: str,
    year_low: int,
    year_high: int,
    date_precision: str,
    date_text: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{year_high}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": year_high,
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
    contract_extras: dict[str, Any] = {}
    if candidate_id == "hced-Oran1704-1708-1":
        # The raw row spans 1704-1708 with a midpointed year_best of 1706; the
        # active siege ran only from November 1707 to the January 1708 fall,
        # so the event year is pinned to 1708 with direct date sources.
        contract_extras = {
            "source_date_override": True,
            "date_source_ids": [
                "wave8_oran_jaques_dictionary",
                "wave8_oran_rah_dbe_montemar",
            ],
        }
    return {
        "raw_row_sha256": WAVE8_ORAN_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        **contract_extras,
        "cohort": "spanish_algerian_oran_contests_1707_1780",
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
        "actor_override": "candidate_keyed_existing_regency_of_algiers_identity",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_ORAN_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Oran1704-1708-1": _contract(
        "hced-Oran1704-1708-1",
        _canonical(
            "Siege of Oran (1707-1708)",
            1708,
            1708,
            "year",
            "1708 (active siege November 1707 to January 1708)",
            "siege_and_recapture_of_oran_and_mers_el_kebir",
        ),
        [_REGENCY],
        [_SPAIN],
        [
            "wave8_oran_jaques_dictionary",
            "wave8_oran_rah_dbe_montemar",
        ],
        (
            "The Regency's western bey Mustapha Bouchelaghem, reinforced from "
            "Algiers, bombarded the Spanish forts from the Aidour heights and "
            "took the city on 20 January 1708. The Real Academia de la "
            "Historia's Montemar biography independently records Oran as lost "
            "in 1708, matching Jaques's coded Algerian victory. The event year "
            "is pinned to 1708 rather than the midpointed 1706 because the "
            "active siege ran only from November 1707 to the January 1708 "
            "fall."
        ),
        confidence=0.9,
    ),
    "hced-Oran1732-1": _contract(
        "hced-Oran1732-1",
        _canonical(
            "Spanish reconquest of Oran (1732)",
            1732,
            1732,
            "year",
            "15 June to 2 July 1732",
            "amphibious_reconquest_of_oran_and_mers_el_kebir",
        ),
        [_SPAIN],
        [_REGENCY],
        [
            "wave8_oran_clodfelter_warfare",
            "wave8_oran_jaques_dictionary",
            "wave8_oran_rah_dbe_montemar",
        ],
        (
            "Montemar's expedition of roughly thirty thousand landed near "
            "Mers el-Kebir and retook Oran within three weeks; the Real "
            "Academia de la Historia biography, Clodfelter, and Jaques all "
            "record the Spanish victory."
        ),
        confidence=0.96,
    ),
}


WAVE8_ORAN_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Oran1780-1": {
        "raw_row_sha256": WAVE8_ORAN_ROW_HASHES["hced-Oran1780-1"],
        "cohort": "spanish_algerian_oran_contests_1707_1780",
        "disposition": "hold",
        "hold_category": "insufficient_outcome_documentation",
        "hold_reason": (
            "No dedicated scholarly account records a discrete 1780 "
            "engagement at Oran: the coded Spanish victory rests on fallible "
            "reference transcription, and the Spanish-Algerian War campaign "
            "record for 1775-1785 shows no separate 1780 Oran action. Unknown "
            "is not a draw; re-scoring requires a future documented override."
        ),
        "evidence_refs": [
            "wave8_oran_jaques_dictionary",
            "wave8_oran_wikipedia_spanish_algerian_war",
        ],
    },
}

# The only other queue row carrying a bare ``Algeria`` side is Tindouf 1963,
# where the label denotes the modern republic inside its own interval; the
# generic label tier already resolved and published it, so this lane records
# the ownership and leaves it untouched.
WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Tindouf1963-1": {
        "raw_row_sha256": (
            "730d960692022b84aaf31fbe15e1fdfcacd93b3a1fd4c0dfbdc4de4dd746b108"
        ),
        "owner_event_id": "hced_label_hced_tindouf1963_1",
        "disposition": "already_resolved_modern_republic",
        "note": (
            "1963 falls inside the modern republic's registered interval, so "
            "the generic label tier already resolved this row to "
            "clio_q262_1963_de9ecdb4 against Morocco; it is outside this "
            "lane's eighteenth-century scope."
        ),
    },
}

WAVE8_ORAN_CONTRACT_IDS = frozenset(WAVE8_ORAN_CONTRACTS)
WAVE8_ORAN_RESERVED_IDS = frozenset(WAVE8_ORAN_ROW_HASHES)
# The reviewed sources attest the sieges at the fortified city of Oran and
# Mers el-Kebir, verifying HCED's city-level coordinate and modern country;
# both fields are retained.
WAVE8_ORAN_POINT_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_ORAN_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_ORAN_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_ORAN_CONTRACTS,
        "entities": WAVE8_ORAN_ENTITIES,
        "existing_release_dispositions": WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS,
        "funnel": WAVE8_ORAN_FUNNEL_AUDIT,
        "holds": WAVE8_ORAN_HOLDS,
        "location_reasons": WAVE8_ORAN_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_ORAN_ROW_HASHES,
        "sources": WAVE8_ORAN_SOURCES,
    }


def wave8_oran_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_ORAN_FINAL_AUDIT_SIGNATURE = (
    "f7efdc3b87f9affed38dc67a0f8c80dba72d8b6bbef16e6babc19a3a0cb9bf4e"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_ORAN_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if WAVE8_ORAN_ENTITIES:
        raise ValueError(f"{_LANE_NAME} must reuse the existing identities")
    if WAVE8_ORAN_RESERVED_IDS != set(WAVE8_ORAN_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if set(WAVE8_ORAN_HOLDS) != {"hced-Oran1780-1"}:
        raise ValueError(f"{_LANE_NAME} hold inventory drift")
    if WAVE8_ORAN_CONTRACT_IDS | set(WAVE8_ORAN_HOLDS) != WAVE8_ORAN_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} reserved partition drift")
    if WAVE8_ORAN_POINT_QUARANTINE_ADDITIONS or WAVE8_ORAN_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} location policy drift")
    if WAVE8_ORAN_LOCATION_QUARANTINE_REASONS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")
    if set(WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS) != {"hced-Tindouf1963-1"}:
        raise ValueError(f"{_LANE_NAME} existing-release disposition drift")
    if WAVE8_ORAN_RESERVED_IDS & set(WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS):
        raise ValueError(f"{_LANE_NAME} disposition and reservation overlap")

    used_sources: set[str] = set()
    allowed_actors = {_REGENCY, _SPAIN}
    for candidate_id, contract in WAVE8_ORAN_CONTRACTS.items():
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
        for source_id in outcomes:
            if "outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"]:
                raise ValueError(
                    f"{_LANE_NAME} non-outcome source in outcomes: {candidate_id}"
                )
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        year_low = int(contract["canonical_event"]["year_low"])
        year_high = int(contract["canonical_event"]["year_high"])
        if not (1671 <= year_low <= year_high <= 1830):
            raise ValueError(f"{_LANE_NAME} Regency identity-window drift: {candidate_id}")
        used_sources.update(evidence)

    for candidate_id, hold in WAVE8_ORAN_HOLDS.items():
        if hold["disposition"] != "hold":
            raise ValueError(f"{_LANE_NAME} hold disposition drift: {candidate_id}")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} hold evidence drift: {candidate_id}")
        used_sources.update(evidence)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_oran_audit_signature() != WAVE8_ORAN_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_oran_queue_contracts(
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
    expected_ids = WAVE8_ORAN_RESERVED_IDS | set(
        WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS
    )
    if exact_ids != expected_ids or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, disposition in WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS.items():
        if canonical_hced_row_sha256(by_id[candidate_id]) != str(
            disposition["raw_row_sha256"]
        ):
            raise ValueError(
                f"{_LANE_NAME} disposition row fingerprint changed: {candidate_id}"
            )
    for candidate_id, expected_hash in WAVE8_ORAN_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("winner_raw") not in {row.get("side_1_raw"), row.get("side_2_raw")}:
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True or row.get("massacre_raw") != "No":
            raise ValueError(
                f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}"
            )
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ORAN_CONTRACTS,
        WAVE8_ORAN_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_oran_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
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
        "one_wrong_interval_candidate": int(
            label.get("failure_cases", {}).get("one_wrong_interval_candidate", -1)
        ),
        "sole_blocker_events": int(label.get("sole_blocker_events", -1)),
    }
    if checks != WAVE8_ORAN_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed: {checks}")
    return {
        "events_touched": checks["events_touched"],
        "one_wrong_interval_candidate": checks["one_wrong_interval_candidate"],
        "sole_blocker_events": checks["sole_blocker_events"],
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
    "hced-Oran1704-1708-1": {
        "Oran",
        "Siege of Oran",
        "Siege of Oran (1707-1708)",
    },
    "hced-Oran1732-1": {
        "Oran",
        "Spanish conquest of Oran",
        "Spanish reconquest of Oran (1732)",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (year, normalize_label(alias))
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
    for year in range(
        int(WAVE8_ORAN_CONTRACTS[candidate_id]["canonical_event"]["year_low"]) - 1,
        int(WAVE8_ORAN_CONTRACTS[candidate_id]["canonical_event"]["year_high"]) + 2,
    )
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_oran_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_oran_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_ORAN_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_ORAN_CONTRACT_IDS
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


def install_wave8_oran_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ORAN_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_oran_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_ORAN_SOURCES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_oran_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_oran_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ORAN_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )


def wave8_oran_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_ORAN_CONTRACTS.values(),
                    *WAVE8_ORAN_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_oran_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "existing_release_dispositions": len(WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS),
        "holds": len(WAVE8_ORAN_HOLDS),
        "new_entities": 0,
        "new_sources": len(WAVE8_ORAN_SOURCES),
        "newly_rated_events": len(WAVE8_ORAN_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": 0,
        "promotion_contracts": len(WAVE8_ORAN_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_ORAN_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_oran_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_oran_counts(),
        "cohorts": wave8_oran_cohort_counts(),
        "final_audit_signature": WAVE8_ORAN_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_ORAN_CONTRACT_IDS),
    }


_validate_static()
