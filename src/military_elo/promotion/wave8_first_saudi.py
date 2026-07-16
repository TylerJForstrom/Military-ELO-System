"""Exact Wave 8 disposition for First Saudi State HCED rows."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

from .common import _slug
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


_LANE_NAME = "Wave 8 First Saudi State"
WAVE8_FIRST_SAUDI_FINAL_AUDIT_SIGNATURE = (
    "363d49e47f4be66693ad63b8a2b4cc0009bb4b5af5d4851b697ff3ea2c33c1b1"
)


def _source(
    source_id: str,
    title: str,
    url: str,
    family: str,
    *,
    outcome: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": "Saudipedia, Ministry of Media (Saudi Arabia)",
        "license": "Citation and link only",
        "source_type": "official_history",
        "accessed": "2026-07-16",
        "source_family_id": family,
        "evidence_roles": roles,
    }


WAVE8_FIRST_SAUDI_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_first_saudi_state_history",
        "First Saudi State",
        "https://saudipedia.com/en/first-saudi-state",
        "saudipedia_first_saudi_state",
        outcome=True,
    ),
    _source(
        "wave8_first_saudi_abdullah_diriyah",
        "Abdullah Bin Saud Bin Abdulaziz Al Saud",
        "https://saudipedia.com/en/abdullah-bin-saud-bin-abdulaziz-al-saud",
        "saudipedia_first_saudi_state",
        outcome=True,
    ),
    {
        "id": "wave8_first_saudi_rcrc_heart_of_call",
        "title": "Heart of the Call: Al-Bujairi and At-Turaif",
        "url": (
            "https://www.rcrc.gov.sa/res/ada/ar/Publications/Al-Bujairi_Eng/"
            "files/assets/common/downloads/publication.pdf"
        ),
        "publisher": "Royal Commission for Riyadh City",
        "license": "Citation and link only",
        "source_type": "official_history",
        "accessed": "2026-07-16",
        "source_family_id": "royal_commission_riyadh_history",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
)


WAVE8_FIRST_SAUDI_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "first_saudi_state",
        "name": "First Saudi State",
        "kind": "emirate",
        "start_year": 1727,
        "end_year": 1818,
        "region": "Arabian Peninsula",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The polity founded at Diriyah in 1727 and extinguished after the "
            "1818 siege. No rating is inherited by the Second Saudi State, the "
            "Emirate of Nejd and Hasa, or the modern Kingdom of Saudi Arabia; no "
            "generic House of Saud alias is opened."
        ),
        "source_ids": ["wave8_first_saudi_state_history"],
    },
)


def _canonical(name: str, year: int | None) -> dict[str, Any]:
    return {
        "canonical_key": (
            f"{_slug(name)}:{year}:{year}" if year is not None else f"{_slug(name)}:unknown"
        ),
        "date_precision": "year" if year is not None else "unknown",
        "granularity": "engagement",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


WAVE8_FIRST_SAUDI_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Diriyah1818-1": {
        "raw_row_sha256": (
            "2c47849c0b81c37cddae1cca6a622b88e64f6d87fe93be96932500659dcdeecb"
        ),
        "canonical_event": _canonical("Siege of Diriyah", 1818),
        "cohort": "ottoman_saudi_war",
        "side_1_entity_ids": ["egypt_muhammad_ali"],
        "side_2_entity_ids": ["first_saudi_state"],
        "winner_side": 1,
        "war_type": "interstate",
        "evidence_refs": [
            "wave8_first_saudi_state_history",
            "wave8_first_saudi_abdullah_diriyah",
        ],
        "outcome_source_ids": ["wave8_first_saudi_abdullah_diriyah"],
        "outcome_source_family_ids": ["saudipedia_first_saudi_state"],
        "source_outcome_override": False,
        "actor_override": "muhammad_ali_egyptian_field_army",
        "audit_note": (
            "The six-month siege, surrender, and destruction are directly "
            "attested. Ibrahim Pasha's field army is assigned to Muhammad Ali's "
            "autonomously commanded Egypt rather than mechanically crediting the "
            "Ottoman umbrella label in HCED."
        ),
    },
}


WAVE8_FIRST_SAUDI_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Al Safra1812-1": {
        "raw_row_sha256": (
            "a4698bdced9406da8357df88932e06ccb14a58cb21f264d8ba7daab26c47030c"
        ),
        "canonical_event": _canonical("Battle of Al-Safra", 1812),
        "hold_category": "source_date_conflict",
        "hold_reason": (
            "The encounter is attested, but reviewed chronologies disagree between "
            "late 1811 and 1812. A year-precision Elo event is not emitted until "
            "that conflict is adjudicated."
        ),
        "evidence_refs": ["wave8_first_saudi_state_history"],
    },
    "hced-Jeddah1813-1": {
        "raw_row_sha256": (
            "11d8ccc469f3e54e4215ff6a4c3977a04b5fb8310762c31ed71152e91c2cc47b"
        ),
        "canonical_event": _canonical("Jeddah", 1813),
        "hold_category": "noncompetitive_occupation",
        "hold_reason": (
            "The reviewed chronology describes control through negotiated or "
            "secret arrangements rather than a defensible competitive battle."
        ),
        "evidence_refs": ["wave8_first_saudi_state_history"],
    },
    "hced-Mecca1813-1": {
        "raw_row_sha256": (
            "5b04706bec80c45c3c6dd6ff538454f32560af89cbae1faddd91e0ffc9089735"
        ),
        "canonical_event": _canonical("Mecca", 1813),
        "hold_category": "noncompetitive_occupation",
        "hold_reason": (
            "The reviewed chronology supports entry and control, but not a "
            "competitive engagement with a defensible tactical outcome."
        ),
        "evidence_refs": ["wave8_first_saudi_state_history"],
    },
    "hced-Medina1812-1": {
        "raw_row_sha256": (
            "caa220a4b64e4f4599a8d179d2dbb2b742205c711da55edadb552cafd6ae5e9f"
        ),
        "canonical_event": _canonical("Medina", 1812),
        "hold_category": "outcome_mechanism_disputed",
        "hold_reason": (
            "Official reviewed accounts differ over siege pressure, surrender, "
            "and secret agreements. Control of Medina is not converted into an "
            "invented tactical victory."
        ),
        "evidence_refs": [
            "wave8_first_saudi_state_history",
            "wave8_first_saudi_rcrc_heart_of_call",
        ],
    },
    "hced-Nejd1817-1": {
        "raw_row_sha256": (
            "35d1c5e5001cf9cacb4de6cd5dd552d92de184a0fda04e54a369e73384f137d2"
        ),
        "canonical_event": _canonical("Nejd", None),
        "hold_category": "missing_event_date",
        "hold_reason": (
            "The staged row has no year_low, year_high, or year_best. No date is "
            "invented from the source-record identifier."
        ),
        "evidence_refs": ["wave8_first_saudi_state_history"],
    },
}


WAVE8_FIRST_SAUDI_CONTRACT_IDS = frozenset(WAVE8_FIRST_SAUDI_CONTRACTS)
WAVE8_FIRST_SAUDI_HOLD_IDS = frozenset(WAVE8_FIRST_SAUDI_HOLDS)
WAVE8_FIRST_SAUDI_RESERVED_IDS = (
    WAVE8_FIRST_SAUDI_CONTRACT_IDS | WAVE8_FIRST_SAUDI_HOLD_IDS
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def wave8_first_saudi_signature() -> str:
    return hashlib.sha256(
        _canonical_json(
            {
                "contracts": WAVE8_FIRST_SAUDI_CONTRACTS,
                "holds": WAVE8_FIRST_SAUDI_HOLDS,
            }
        ).encode()
    ).hexdigest()


def _validate_static() -> None:
    if (len(WAVE8_FIRST_SAUDI_CONTRACTS), len(WAVE8_FIRST_SAUDI_HOLDS)) != (1, 5):
        raise ValueError("Wave 8 First Saudi disposition inventory changed")
    if wave8_first_saudi_signature() != WAVE8_FIRST_SAUDI_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 First Saudi final audit signature changed")
    if WAVE8_FIRST_SAUDI_CONTRACT_IDS & WAVE8_FIRST_SAUDI_HOLD_IDS:
        raise ValueError("Wave 8 First Saudi promotion and hold inventories overlap")
    source_ids = {str(source["id"]) for source in WAVE8_FIRST_SAUDI_SOURCES}
    for entity in WAVE8_FIRST_SAUDI_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError("Wave 8 First Saudi identities must be alias-free")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError("Wave 8 First Saudi identity permits rating inheritance")
        if not set(map(str, entity["source_ids"])) <= source_ids:
            raise ValueError("Wave 8 First Saudi identity names an unknown source")
    for disposition in (WAVE8_FIRST_SAUDI_CONTRACTS, WAVE8_FIRST_SAUDI_HOLDS):
        for contract in disposition.values():
            if not set(map(str, contract["evidence_refs"])) <= source_ids:
                raise ValueError("Wave 8 First Saudi disposition names an unknown source")


def validate_wave8_first_saudi_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_FIRST_SAUDI_CONTRACTS,
        WAVE8_FIRST_SAUDI_HOLDS,
        lane_name=_LANE_NAME,
    )


def install_wave8_first_saudi_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_FIRST_SAUDI_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_first_saudi_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_FIRST_SAUDI_SOURCES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_first_saudi_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_first_saudi_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_FIRST_SAUDI_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix="hced_wave8_first_saudi_",
    )


def wave8_first_saudi_counts() -> dict[str, int]:
    return {
        "holds": len(WAVE8_FIRST_SAUDI_HOLDS),
        "newly_rated_events": len(WAVE8_FIRST_SAUDI_CONTRACTS),
        "promotion_contracts": len(WAVE8_FIRST_SAUDI_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_FIRST_SAUDI_RESERVED_IDS),
    }
