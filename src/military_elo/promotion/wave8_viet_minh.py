"""Candidate-keyed audit of HCED's unresolved ``Viet Minh`` rows.

The bare label is never opened as an alias.  Nine fingerprinted First
Indochina War rows bind to an alias-free, time-bounded Viet Minh field-force
identity; Muong-Khoua binds a separate event-bounded Lao-French garrison.
Three rows remain explicit holds because their source assertions describe a
mixed campaign, an unbounded regional campaign, or a wrong-year bundled
campaign.  Unknown or unbounded is never converted to a draw.
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
    "WAVE8_VIET_MINH_CONTRACT_IDS",
    "WAVE8_VIET_MINH_CONTRACTS",
    "WAVE8_VIET_MINH_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_VIET_MINH_ENTITIES",
    "WAVE8_VIET_MINH_FINAL_AUDIT_SIGNATURE",
    "WAVE8_VIET_MINH_FUNNEL_AUDIT",
    "WAVE8_VIET_MINH_HOLDS",
    "WAVE8_VIET_MINH_LOCATION_QUARANTINE_REASONS",
    "WAVE8_VIET_MINH_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_VIET_MINH_RESERVED_IDS",
    "WAVE8_VIET_MINH_ROW_HASHES",
    "WAVE8_VIET_MINH_SOURCES",
    "install_wave8_viet_minh_entities",
    "install_wave8_viet_minh_sources",
    "promote_wave8_viet_minh_contracts",
    "validate_wave8_viet_minh_funnel",
    "validate_wave8_viet_minh_integration_dispositions",
    "validate_wave8_viet_minh_queue_contracts",
    "wave8_viet_minh_audit_signature",
    "wave8_viet_minh_cohort_counts",
    "wave8_viet_minh_counts",
    "wave8_viet_minh_metadata",
)


_LANE_NAME = "Wave 8 exact Viet Minh First Indochina War audit"
_MODULE_OWNER = "military_elo.promotion.wave8_viet_minh"
_EVENT_ID_PREFIX = "hced_wave8_viet_minh_"
_EXACT_LABEL = "viet minh"

_VIET_MINH = "viet_minh_first_indochina_war_forces_1950_1954"
_MUONG_KHOUA_GARRISON = "muong_khoua_lao_french_garrison_1953"
_FRENCH_FOURTH_REPUBLIC = "clio_fr_france_modern_2_1945_396ed149"

_CLODFELTER = "wave8_viet_minh_clodfelter_warfare"
_AUSTRALIAN_WAR_MEMORIAL = "wave8_viet_minh_australian_war_memorial"
_NGHIA_LO_1951 = "wave8_viet_minh_gras_nghia_lo_1951"
_NGHIA_LO_1952 = "wave8_viet_minh_us_army_advice_support"
_MUONG_KHOUA = "wave8_viet_minh_wolfson_ford_laos"
_HOLD_SOURCES = sorted([_AUSTRALIAN_WAR_MEMORIAL, _CLODFELTER])


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_family_id: str,
) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": "expert_reviewed_military_reference",
        "accessed": "2026-07-20",
        "source_family_id": source_family_id,
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
        ],
    }


WAVE8_VIET_MINH_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        _AUSTRALIAN_WAR_MEMORIAL,
        "Road to Dien Bien Phu",
        "https://www.awm.gov.au/wartime/92/article-five",
        "Australian War Memorial",
        "australian_war_memorial_first_indochina_war",
    ),
    _source(
        _CLODFELTER,
        (
            "Warfare and Armed Conflicts: A Statistical Encyclopedia of "
            "Casualty and Other Figures, 1492-2015, 4th ed., pp. 612-616"
        ),
        "https://books.google.com/books?id=8urEDgAAQBAJ&pg=PA612",
        "McFarland / Google Books",
        "clodfelter_warfare_armed_conflicts",
    ),
    _source(
        _MUONG_KHOUA,
        (
            "Ryan Wolfson-Ford, 'Parting Ways: Two Civil Wars amid the First "
            "Indochina War in Laos (1945-1954),' Southeast Asian Studies "
            "15(1), pp. 3-26"
        ),
        "https://doi.org/10.20495/seas.26001",
        "Center for Southeast Asian Studies, Kyoto University / J-STAGE",
        "wolfson_ford_first_indochina_war_laos",
    ),
    _source(
        _NGHIA_LO_1951,
        (
            "Yves Gras, 'Nghia-Lo. Indochine, octobre 1951,' Revue "
            "historique des Armées 26(4), pp. 133-153"
        ),
        "https://doi.org/10.3406/rharm.1970.8539",
        "Revue historique des Armées / Persée",
        "gras_revue_historique_armees_nghia_lo",
    ),
    _source(
        _NGHIA_LO_1952,
        (
            "Ronald H. Spector, Advice and Support: The Early Years, "
            "1941-1960, pp. 156-157"
        ),
        "https://history.army.mil/portals/143/Images/Publications/catalog/91-1.pdf",
        "United States Army Center of Military History",
        "us_army_cmh_advice_support_early_years",
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_VIET_MINH_SOURCES}


WAVE8_VIET_MINH_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _VIET_MINH,
        "name": "Viet Minh First Indochina War field forces (1950-1954)",
        "kind": "anti_colonial_military_organization",
        "start_year": 1950,
        "end_year": 1954,
        "region": "French Indochina",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Rates only the Viet Minh field forces in the nine reviewed "
            "First Indochina War engagements from the 1950 Border Campaign "
            "through Dien Bien Phu. No rating is inherited from or passed to "
            "generic Vietnamese identity, the Democratic Republic of Vietnam, "
            "the later People's Army of Vietnam, or a Viet Minh formation "
            "outside this reviewed 1950-1954 interval."
        ),
        "source_ids": sorted(
            {
                _AUSTRALIAN_WAR_MEMORIAL,
                _CLODFELTER,
                _NGHIA_LO_1951,
                _NGHIA_LO_1952,
            }
        ),
    },
    {
        "id": _MUONG_KHOUA_GARRISON,
        "name": "Lao-French garrison at Muong-Khoua (1953)",
        "kind": "event_bounded_lao_french_garrison_force",
        "start_year": 1953,
        "end_year": 1953,
        "region": "Muong Khoua, Laos",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Rates only the mixed Lao-French garrison besieged at Muong-Khoua "
            "in 1953. No rating is inherited from or passed to Laos, France, "
            "the French Union, another garrison, or a later Lao force."
        ),
        "source_ids": sorted({_CLODFELTER, _MUONG_KHOUA}),
    },
)


WAVE8_VIET_MINH_ROW_HASHES: dict[str, str] = {
    "hced-Cao-Bang1950-1": (
        "4c506cebadcead570cb678750e80ae8606f50e52b0d1f2efa9be55401f45523b"
    ),
    "hced-Day River1951-1": (
        "e2bdb5afb898df2c847422e630969fb8c7a8852ea127e7bffb77053861033c1c"
    ),
    "hced-Dien Bien Phu1953-1": (
        "e4161cf4e0b2864c610932214f2bb2863498413848e320c1b0bdf125786db4a8"
    ),
    "hced-Dong-Khe1950-1": (
        "299dab6330de54f62cf41dbe14697bb6d407effae559ed676f710e04f586e360"
    ),
    "hced-Hoa Binh1951-1": (
        "a8b1e3cc9ebc9616514fa54f64e37bf127e45d083f2cf976db473a2c1652d2a1"
    ),
    "hced-Mao Khe1951-1": (
        "07699487709f2dce9ea0662a37489ca9e1d90940951f98fdaa0f2cfa9956bfc2"
    ),
    "hced-Muong-Khoua1953-1": (
        "424d78e9383e3143932d9a5b949a5f328c9e7c8338545450b9f7b5aa36dc56a2"
    ),
    "hced-Nghia Lo1951-1": (
        "cd7024ef52f7bb7eed9a56c83e47f42d753ba2e05419e72afa31adbd521bf453"
    ),
    "hced-Nghia Lo1952-1": (
        "ffa5c456b4ec7d680e62fe5e425264a1f2cb4f130f30b82d8d29ec1f6adb17e4"
    ),
    "hced-Red River Delta1950-1": (
        "69ccef8acc2dd36c828ddfdaaeed47a95c0a35f4b5af1f21c8ff59fff94fc15b"
    ),
    "hced-Viet Bac1946-1": (
        "3fa5921cf32077c451c26a389e459a96732f61651a1dcaa342017c0c01272bf3"
    ),
    "hced-Vinh Yen1951-1": (
        "132772b394826b56a9b22d540a3f9f5d1b04612b57d0cccddb89f841cf8ba436"
    ),
}


WAVE8_VIET_MINH_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "58df797ab7ab18b8bc5eeb69ba063da2508dec195d19a3a1fe3cf4839e68c542"
    ),
    "events_touched": 12,
    "label": _EXACT_LABEL,
    "sole_blocker_events": 0,
    "zero_time_valid_candidates": 12,
}


def _canonical(
    name: str,
    year: int,
    granularity: str = "single_tactical_engagement",
) -> dict[str, Any]:
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
    year: int,
    side_1: str,
    side_2: str,
    outcome_sources: Iterable[str],
    audit_note: str,
    *,
    date_override: bool = False,
) -> dict[str, Any]:
    sources = sorted(map(str, outcome_sources))
    extras: dict[str, Any] = {}
    if date_override:
        extras = {
            "source_date_override": True,
            "date_source_ids": sources,
        }
    return {
        "raw_row_sha256": WAVE8_VIET_MINH_ROW_HASHES[candidate_id],
        "canonical_event": _canonical(name, year),
        **extras,
        "cohort": "first_indochina_war_viet_minh_engagements_1950_1954",
        "side_1_entity_ids": [side_1],
        "side_2_entity_ids": [side_2],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
        "confidence": 0.92,
        "evidence_refs": sources,
        "outcome_source_ids": sources,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in sources
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_exact_first_indochina_war_forces",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_VIET_MINH_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Cao-Bang1950-1": _contract(
        "hced-Cao-Bang1950-1",
        "Battle of Cao-Bang (1950)",
        1950,
        _VIET_MINH,
        _FRENCH_FOURTH_REPUBLIC,
        (_AUSTRALIAN_WAR_MEMORIAL, _CLODFELTER),
        (
            "The reviewed references identify the bounded 1950 Cao-Bang "
            "action as a Viet Minh tactical victory over French Union forces."
        ),
    ),
    "hced-Day River1951-1": _contract(
        "hced-Day River1951-1",
        "Battle of the Day River (1951)",
        1951,
        _FRENCH_FOURTH_REPUBLIC,
        _VIET_MINH,
        (_AUSTRALIAN_WAR_MEMORIAL, _CLODFELTER),
        (
            "The reviewed references identify the bounded Day River battle "
            "as a French tactical victory over the attacking Viet Minh force."
        ),
    ),
    "hced-Dien Bien Phu1953-1": _contract(
        "hced-Dien Bien Phu1953-1",
        "Battle of Dien Bien Phu (1954)",
        1954,
        _VIET_MINH,
        _FRENCH_FOURTH_REPUBLIC,
        (_AUSTRALIAN_WAR_MEMORIAL, _CLODFELTER),
        (
            "The staged HCED row is misdated 1953. Both reviewed references "
            "place the decisive siege and French capitulation in 1954, so the "
            "audited event date is corrected without altering the source row."
        ),
        date_override=True,
    ),
    "hced-Dong-Khe1950-1": _contract(
        "hced-Dong-Khe1950-1",
        "Battle of Dong-Khe (1950)",
        1950,
        _VIET_MINH,
        _FRENCH_FOURTH_REPUBLIC,
        (_AUSTRALIAN_WAR_MEMORIAL, _CLODFELTER),
        (
            "The reviewed references identify the 1950 Dong-Khe engagement "
            "as a Viet Minh tactical victory over the French garrison."
        ),
    ),
    "hced-Mao Khe1951-1": _contract(
        "hced-Mao Khe1951-1",
        "Battle of Mao Khe (1951)",
        1951,
        _FRENCH_FOURTH_REPUBLIC,
        _VIET_MINH,
        (_AUSTRALIAN_WAR_MEMORIAL, _CLODFELTER),
        (
            "The reviewed references identify the bounded Mao Khe battle as "
            "a French defensive victory over the Viet Minh assault."
        ),
    ),
    "hced-Muong-Khoua1953-1": _contract(
        "hced-Muong-Khoua1953-1",
        "Battle of Muong-Khoua (1953)",
        1953,
        _VIET_MINH,
        _MUONG_KHOUA_GARRISON,
        (_CLODFELTER, _MUONG_KHOUA),
        (
            "The reviewed references identify the fall of the mixed Lao-French "
            "Muong-Khoua garrison as a Viet Minh tactical victory. The garrison "
            "is event-bounded rather than generalized to Laos or France."
        ),
    ),
    "hced-Nghia Lo1951-1": _contract(
        "hced-Nghia Lo1951-1",
        "Battle of Nghia Lo (1951)",
        1951,
        _FRENCH_FOURTH_REPUBLIC,
        _VIET_MINH,
        (_CLODFELTER, _NGHIA_LO_1951),
        (
            "The reviewed references distinguish the 1951 defense of Nghia Lo "
            "and record a French tactical victory."
        ),
    ),
    "hced-Nghia Lo1952-1": _contract(
        "hced-Nghia Lo1952-1",
        "Battle of Nghia Lo (1952)",
        1952,
        _VIET_MINH,
        _FRENCH_FOURTH_REPUBLIC,
        (_CLODFELTER, _NGHIA_LO_1952),
        (
            "The reviewed references distinguish the 1952 battle from the "
            "prior year's defense and record a Viet Minh tactical victory."
        ),
    ),
    "hced-Vinh Yen1951-1": _contract(
        "hced-Vinh Yen1951-1",
        "Battle of Vinh Yen (1951)",
        1951,
        _FRENCH_FOURTH_REPUBLIC,
        _VIET_MINH,
        (_AUSTRALIAN_WAR_MEMORIAL, _CLODFELTER),
        (
            "The reviewed references identify the bounded Vinh Yen battle as "
            "a French tactical victory over the Viet Minh offensive."
        ),
    ),
}


def _hold(candidate_id: str, category: str, reason: str) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_VIET_MINH_ROW_HASHES[candidate_id],
        "cohort": "first_indochina_war_viet_minh_engagements_1946_1954",
        "disposition": "hold",
        "hold_category": category,
        "hold_reason": reason,
        "evidence_refs": list(_HOLD_SOURCES),
    }


WAVE8_VIET_MINH_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Hoa Binh1951-1": _hold(
        "hced-Hoa Binh1951-1",
        "mixed_campaign_outcome",
        (
            "Hoa Binh denotes the 1951-1952 campaign, whose occupation, relief, "
            "attrition, and withdrawal phases do not reduce to HCED's single "
            "Viet Minh victory assertion. A bounded event contract is required; "
            "the mixed campaign is not scored and is not a draw."
        ),
    ),
    "hced-Red River Delta1950-1": _hold(
        "hced-Red River Delta1950-1",
        "unbounded_regional_campaign",
        (
            "The row names an entire geographic theater rather than a discrete, "
            "source-bounded engagement. No tactical outcome is invented for the "
            "Red River Delta label, and unbounded is not a draw."
        ),
    ),
    "hced-Viet Bac1946-1": _hold(
        "hced-Viet Bac1946-1",
        "wrong_year_bundled_campaign",
        (
            "The cited Viet Bac campaign belongs to 1947, while the staged row "
            "is dated 1946 and bundles a campaign rather than one adjudicable "
            "engagement. It remains staged instead of receiving a guessed date "
            "or result; unknown is not a draw."
        ),
    ),
}


WAVE8_VIET_MINH_CONTRACT_IDS = frozenset(WAVE8_VIET_MINH_CONTRACTS)
WAVE8_VIET_MINH_RESERVED_IDS = frozenset(WAVE8_VIET_MINH_ROW_HASHES)
WAVE8_VIET_MINH_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_VIET_MINH_CONTRACT_IDS
)
WAVE8_VIET_MINH_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()

_RAW_LOCATION_ASSERTIONS: dict[str, tuple[list[float], str]] = {
    "hced-Cao-Bang1950-1": ([106.2522143, 22.635689], "Vietnam"),
    "hced-Day River1951-1": ([106.0805726, 20.0917047], "Vietnam"),
    "hced-Dien Bien Phu1953-1": ([103.0061505, 21.4139983], "Vietnam"),
    "hced-Dong-Khe1950-1": ([106.4435319, 22.4220178], "Vietnam"),
    "hced-Mao Khe1951-1": ([106.5873383, 21.0646444], "Vietnam"),
    "hced-Muong-Khoua1953-1": ([102.5038963, 21.078335], "Laos"),
    "hced-Nghia Lo1951-1": ([104.4563763, 21.5988562], "Vietnam"),
    "hced-Nghia Lo1952-1": ([104.4563763, 21.5988562], "Vietnam"),
    "hced-Vinh Yen1951-1": ([105.5593214, 21.5332244], "Vietnam"),
}

WAVE8_VIET_MINH_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "evidence_refs": list(
            WAVE8_VIET_MINH_CONTRACTS[candidate_id]["evidence_refs"]
        ),
        "raw_point": raw_point,
        "retained_country": country,
        "reason": (
            "The reviewed references authenticate the named battle and country "
            "but do not independently authenticate HCED's exact coordinate. "
            "Retain the country assertion and withhold the point."
        ),
    }
    for candidate_id, (raw_point, country) in sorted(_RAW_LOCATION_ASSERTIONS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_VIET_MINH_CONTRACTS,
        "entities": WAVE8_VIET_MINH_ENTITIES,
        "funnel": WAVE8_VIET_MINH_FUNNEL_AUDIT,
        "holds": WAVE8_VIET_MINH_HOLDS,
        "location_reasons": WAVE8_VIET_MINH_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_VIET_MINH_ROW_HASHES,
        "sources": WAVE8_VIET_MINH_SOURCES,
    }


def wave8_viet_minh_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_VIET_MINH_FINAL_AUDIT_SIGNATURE = (
    "b70b8bdb751435802c41898a27e198e8e8f89f643b1ca1144c5ec3a4f92f4c7f"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != 5 or len(source_ids) != len(WAVE8_VIET_MINH_SOURCES):
        raise ValueError(f"{_LANE_NAME} source inventory drift")
    if len(WAVE8_VIET_MINH_ENTITIES) != 2:
        raise ValueError(f"{_LANE_NAME} identity inventory drift")
    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_VIET_MINH_ENTITIES
    }
    if set(entity_by_id) != {_VIET_MINH, _MUONG_KHOUA_GARRISON}:
        raise ValueError(f"{_LANE_NAME} exact identity IDs drifted")
    expected_windows = {
        _VIET_MINH: (1950, 1954),
        _MUONG_KHOUA_GARRISON: (1953, 1953),
    }
    expected_entity_sources = {
        _VIET_MINH: {
            _AUSTRALIAN_WAR_MEMORIAL,
            _CLODFELTER,
            _NGHIA_LO_1951,
            _NGHIA_LO_1952,
        },
        _MUONG_KHOUA_GARRISON: {_CLODFELTER, _MUONG_KHOUA},
    }
    for entity_id, entity in entity_by_id.items():
        if (
            (entity["start_year"], entity["end_year"]) != expected_windows[entity_id]
            or entity["aliases"]
            or entity["predecessors"]
            or not _is_sorted_unique(entity["source_ids"])
            or set(entity["source_ids"]) != expected_entity_sources[entity_id]
            or "no rating is inherited" not in str(entity["continuity_note"]).casefold()
        ):
            raise ValueError(f"{_LANE_NAME} identity firewall drift: {entity_id}")

    if WAVE8_VIET_MINH_RESERVED_IDS != set(WAVE8_VIET_MINH_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} reservation inventory drift")
    if (
        WAVE8_VIET_MINH_CONTRACT_IDS | set(WAVE8_VIET_MINH_HOLDS)
        != WAVE8_VIET_MINH_RESERVED_IDS
        or WAVE8_VIET_MINH_CONTRACT_IDS & set(WAVE8_VIET_MINH_HOLDS)
        or len(WAVE8_VIET_MINH_CONTRACT_IDS) != 9
        or len(WAVE8_VIET_MINH_HOLDS) != 3
    ):
        raise ValueError(f"{_LANE_NAME} disposition partition drift")
    if WAVE8_VIET_MINH_POINT_QUARANTINE_ADDITIONS != WAVE8_VIET_MINH_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine drift")
    if WAVE8_VIET_MINH_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country quarantine drift")
    if set(WAVE8_VIET_MINH_LOCATION_QUARANTINE_REASONS) != set(
        WAVE8_VIET_MINH_POINT_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_VIET_MINH_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["confidence"] != 0.92
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome policy drift: {candidate_id}")
        actors = {
            *map(str, contract["side_1_entity_ids"]),
            *map(str, contract["side_2_entity_ids"]),
        }
        expected_actors = (
            {_VIET_MINH, _MUONG_KHOUA_GARRISON}
            if candidate_id == "hced-Muong-Khoua1953-1"
            else {_VIET_MINH, _FRENCH_FOURTH_REPUBLIC}
        )
        if actors != expected_actors:
            raise ValueError(f"{_LANE_NAME} exact actor drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or evidence != outcomes
            or len(outcomes) != 2
            or not set(outcomes) <= source_ids
            or any(
                "outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"]
                for source_id in outcomes
            )
        ):
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families or len(families) != 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        year = int(contract["canonical_event"]["year_low"])
        if not 1950 <= year <= 1954:
            raise ValueError(f"{_LANE_NAME} Viet Minh identity-window drift")
        used_sources.update(evidence)

    override_ids = {
        candidate_id
        for candidate_id, contract in WAVE8_VIET_MINH_CONTRACTS.items()
        if contract.get("source_date_override") is True
    }
    if override_ids != {"hced-Dien Bien Phu1953-1"}:
        raise ValueError(f"{_LANE_NAME} date override inventory drift")
    override = WAVE8_VIET_MINH_CONTRACTS["hced-Dien Bien Phu1953-1"]
    if (
        override["canonical_event"]["year_low"] != 1954
        or override["canonical_event"]["year_high"] != 1954
        or override["date_source_ids"] != override["outcome_source_ids"]
    ):
        raise ValueError(f"{_LANE_NAME} Dien Bien Phu date correction drift")

    expected_hold_categories = {
        "hced-Hoa Binh1951-1": "mixed_campaign_outcome",
        "hced-Red River Delta1950-1": "unbounded_regional_campaign",
        "hced-Viet Bac1946-1": "wrong_year_bundled_campaign",
    }
    for candidate_id, hold in WAVE8_VIET_MINH_HOLDS.items():
        if (
            hold["disposition"] != "hold"
            or hold["hold_category"] != expected_hold_categories[candidate_id]
            or not _is_sorted_unique(hold["evidence_refs"])
            or hold["evidence_refs"] != _HOLD_SOURCES
            or "draw" not in str(hold["hold_reason"]).casefold()
        ):
            raise ValueError(f"{_LANE_NAME} hold policy drift: {candidate_id}")
        used_sources.update(map(str, hold["evidence_refs"]))

    for candidate_id, reason in WAVE8_VIET_MINH_LOCATION_QUARANTINE_REASONS.items():
        if (
            reason["actions"] != ["withhold_point"]
            or reason["evidence_refs"]
            != WAVE8_VIET_MINH_CONTRACTS[candidate_id]["evidence_refs"]
            or reason["raw_point"] != _RAW_LOCATION_ASSERTIONS[candidate_id][0]
            or reason["retained_country"] != _RAW_LOCATION_ASSERTIONS[candidate_id][1]
        ):
            raise ValueError(f"{_LANE_NAME} location evidence drift: {candidate_id}")
        used_sources.update(map(str, reason["evidence_refs"]))

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_viet_minh_audit_signature() != WAVE8_VIET_MINH_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_viet_minh_queue_contracts(
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
    if exact_ids != WAVE8_VIET_MINH_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_VIET_MINH_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("do_not_rate_automatically") is not True:
            raise ValueError(f"{_LANE_NAME} discovery safety flag changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True or row.get("massacre_raw") != "No":
            raise ValueError(f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}")
    for candidate_id in WAVE8_VIET_MINH_CONTRACT_IDS:
        row = by_id[candidate_id]
        if (
            row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
        ):
            raise ValueError(f"{_LANE_NAME} named outcome drift: {candidate_id}")
    if (
        by_id["hced-Dien Bien Phu1953-1"].get("year_low") != 1953
        or by_id["hced-Dien Bien Phu1953-1"].get("year_high") != 1953
    ):
        raise ValueError(f"{_LANE_NAME} staged Dien Bien Phu date drift")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_VIET_MINH_CONTRACTS,
        WAVE8_VIET_MINH_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact), "date_overrides": 1}


def validate_wave8_viet_minh_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
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
    if checks != WAVE8_VIET_MINH_FUNNEL_AUDIT:
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
    for key in ("start_date", "end_date"):
        value = str(row.get(key) or "")
        if len(value) >= 4 and value[:4].lstrip("-").isdigit():
            return int(value[:4])
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Cao-Bang1950-1": {"Cao-Bang", "Cao Bang", "Battle of Cao-Bang"},
    "hced-Day River1951-1": {"Day River", "Battle of the Day River"},
    "hced-Dien Bien Phu1953-1": {"Dien Bien Phu", "Battle of Dien Bien Phu"},
    "hced-Dong-Khe1950-1": {"Dong-Khe", "Dong Khe", "Battle of Dong-Khe"},
    "hced-Mao Khe1951-1": {"Mao Khe", "Battle of Mao Khe"},
    "hced-Muong-Khoua1953-1": {"Muong-Khoua", "Muong Khoua", "Battle of Muong-Khoua"},
    "hced-Nghia Lo1951-1": {"Nghia Lo", "Battle of Nghia Lo"},
    "hced-Nghia Lo1952-1": {"Nghia Lo", "Battle of Nghia Lo"},
    "hced-Vinh Yen1951-1": {"Vinh Yen", "Battle of Vinh Yen"},
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (year, normalize_label(alias))
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
    for year in range(
        int(WAVE8_VIET_MINH_CONTRACTS[candidate_id]["canonical_event"]["year_low"]) - 1,
        int(WAVE8_VIET_MINH_CONTRACTS[candidate_id]["canonical_event"]["year_high"]) + 2,
    )
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_viet_minh_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_viet_minh_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_VIET_MINH_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_VIET_MINH_CONTRACT_IDS
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


def install_wave8_viet_minh_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_VIET_MINH_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_viet_minh_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_VIET_MINH_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_VIET_MINH_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_VIET_MINH_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_viet_minh_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_viet_minh_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_VIET_MINH_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine(events)
    return events


def wave8_viet_minh_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_VIET_MINH_CONTRACTS.values(),
                    *WAVE8_VIET_MINH_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_viet_minh_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "date_overrides": 1,
        "holds": len(WAVE8_VIET_MINH_HOLDS),
        "new_entities": len(WAVE8_VIET_MINH_ENTITIES),
        "new_sources": len(WAVE8_VIET_MINH_SOURCES),
        "newly_rated_events": len(WAVE8_VIET_MINH_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_VIET_MINH_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_VIET_MINH_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_VIET_MINH_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_viet_minh_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_viet_minh_counts(),
        "cohorts": wave8_viet_minh_cohort_counts(),
        "final_audit_signature": WAVE8_VIET_MINH_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_VIET_MINH_CONTRACT_IDS),
    }


_validate_static()
