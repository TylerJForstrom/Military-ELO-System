"""Candidate-keyed Wave 8 Polish audit promotions, holds, and corrections."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Iterable, Mapping

from .common import _participants, _slug
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


_LANE_NAME = "Wave 8 Polish audit"

# Filled from the complete disposition and correction contracts below. Both
# constants are intentionally pinned so changing evidence, identities, or an
# expected pre-correction orientation requires an explicit audit update.
WAVE8_POLISH_AUDIT_CORRECTION_SIGNATURE = (
    "f582b7d6ee183b8f8e1a51817f99c42eb586e445f509d95a832e3167d32f43cb"
)
WAVE8_POLISH_AUDIT_FINAL_AUDIT_SIGNATURE = (
    "e4a963f764739bf4c0708a65b88184920e8561f11e7fc49e87013edc2c889a17"
)


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
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
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": "official_or_academic_reference",
        "accessed": "2026-07-16",
        "source_family_id": family,
        "evidence_roles": roles,
    }


WAVE8_POLISH_AUDIT_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_polish_zpe_rokosz_1606_1607",
        "The Zebrzydowski rebellion and the Battle of Guzów",
        "https://zpe.gov.pl/a/przeczytaj/DYmT3989m",
        "Polish Integrated Educational Platform",
        "polish_zpe_history",
        outcome=True,
    ),
    _source(
        "wave8_polish_ujk_rokosz_review",
        "The Zebrzydowski rebellion and its leadership",
        "https://almanachhistoryczny.ujk.edu.pl/almanach/download/Almanach%20historyczny_tom_24_Szpaczy%C5%84ski.pdf?tennumer=24",
        "Jan Kochanowski University in Kielce",
        "jan_kochanowski_university_history",
    ),
    _source(
        "wave8_polish_zpe_kosciuszko_battles",
        "Battles of the Kościuszko Uprising",
        "https://zpe.gov.pl/a/bitwy-powstania-kosciuszkowskiego/D2QqJC2NL",
        "Polish Integrated Educational Platform",
        "polish_zpe_history",
        outcome=True,
    ),
    _source(
        "wave8_polish_krakow_archive_wawel_1772",
        "The Bar Confederation and the capitulation at Wawel",
        "https://ank.gov.pl/konfederacja/index.html",
        "National Archives in Kraków",
        "national_archives_krakow",
        outcome=True,
    ),
    _source(
        "wave8_polish_zpe_november_uprising_chronology",
        "The November Uprising: chronology and the Battle of Grochów",
        "https://zpe.gov.pl/a/odmowa-powstanie-listopadowe/DElrLAbcZ",
        "Polish Integrated Educational Platform",
        "polish_zpe_history",
        outcome=True,
    ),
    _source(
        "wave8_polish_czech_statistics_domazlice",
        "Domažlice and the Hussite victory of 1431",
        "https://csu.gov.cz/produkty/13-3231-06-za_rok_2005-domazlice",
        "Czech Statistical Office",
        "czech_statistical_office",
    ),
    _source(
        "wave8_polish_usilesia_grotniki",
        "Spytko of Melsztyn's confederation and the Battle of Grotniki",
        "https://journals.us.edu.pl/index.php/SPP/article/view/21114",
        "University of Silesia in Katowice",
        "university_silesia_history",
    ),
)


WAVE8_POLISH_AUDIT_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "guzow_rokosz_forces_1607",
        "name": "Rokosz forces at Guzów (1607)",
        "kind": "confederate_forces",
        "start_year": 1607,
        "end_year": 1607,
        "region": "Eastern Europe",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Event-bounded forces of the noble rokosz defeated at Guzów in 1607. "
            "The identity opens no generic Polish-rebel label and no rating is "
            "inherited by earlier or later confederations, rebels, or state armies."
        ),
        "source_ids": [
            "wave8_polish_zpe_rokosz_1606_1607",
            "wave8_polish_ujk_rokosz_review",
        ],
    },
)


def _canonical(name: str, year: int) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "year",
        "granularity": "engagement",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


WAVE8_POLISH_AUDIT_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Guzow1607-1": {
        "raw_row_sha256": (
            "4efe3218d8e17893f52f6d22421e4192d162a0a81db0e1a377f3318befd6c3d3"
        ),
        "canonical_event": _canonical("Battle of Guzów", 1607),
        "cohort": "zebrzydowski_rokosz",
        "side_1_entity_ids": ["polish_lithuanian_commonwealth"],
        "side_2_entity_ids": ["guzow_rokosz_forces_1607"],
        "winner_side": 1,
        "war_type": "civil_war",
        "evidence_refs": [
            "wave8_polish_zpe_rokosz_1606_1607",
            "wave8_polish_ujk_rokosz_review",
        ],
        "outcome_source_ids": ["wave8_polish_zpe_rokosz_1606_1607"],
        "outcome_source_family_ids": ["polish_zpe_history"],
        "audit_note": (
            "The official Polish educational history confirms the royal victory. "
            "The losing side is confined to the event-bounded rokosz force; a "
            "generic Polish-rebels identity is neither created nor inferred."
        ),
        "source_outcome_override": False,
    }
}


WAVE8_POLISH_AUDIT_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Brest-Litovsk1794-1": {
        "raw_row_sha256": (
            "5b512c935ddff849afdbc7cb4435973bca827c0d68779d585e4105611f3ffae6"
        ),
        "canonical_event": _canonical("Brest-Litovsk", 1794),
        "hold_category": "duplicate_of_reviewed_event",
        "hold_reason": (
            "The official battle chronology identifies Terespol on 19 September "
            "1794 as the Battle of Brest-Litovsk; rating this row would duplicate "
            "the published Terespol candidate."
        ),
        "duplicate_of_candidate_id": "hced-Terespol1794-1",
        "evidence_refs": ["wave8_polish_zpe_kosciuszko_battles"],
    },
    "hced-Janowiec1606-1": {
        "raw_row_sha256": (
            "31c228e2adf6babc7d7707b104cd33697d84dbd523f2f1117ab8b2a91f855b86"
        ),
        "canonical_event": _canonical("Janowiec", 1606),
        "hold_category": "agreement_not_battle",
        "hold_reason": (
            "The reviewed official chronology describes an agreement at Janowiec, "
            "not a competitive military result. No victory is manufactured from "
            "the HCED row."
        ),
        "evidence_refs": ["wave8_polish_zpe_rokosz_1606_1607"],
    },
    "hced-Domazlice1431-1": {
        "raw_row_sha256": (
            "70acb3918c284be0183bbd6739806ad8c7778cb73276c540fc4dae4f666006a9"
        ),
        "canonical_event": _canonical("Domažlice", 1431),
        "hold_category": "exact_belligerent_identities_unresolved",
        "hold_reason": (
            "The Czech source supports a Hussite victory, but the raw labels "
            "'Polish Hussites' and 'German Crusaders' do not identify the exact "
            "Bohemian field army and Fifth Crusade coalition."
        ),
        "evidence_refs": ["wave8_polish_czech_statistics_domazlice"],
    },
    "hced-Grotniki1439-1": {
        "raw_row_sha256": (
            "95201255e4fe69a0f4398b063214af455e54136b4cebb831e843a4e295fbf56c"
        ),
        "canonical_event": _canonical("Grotniki", 1439),
        "hold_category": "exact_belligerent_identities_unresolved",
        "hold_reason": (
            "The academic evidence identifies Spytko of Melsztyn's confederation "
            "and rejects a generic Polish-Hussite identity, while the exact royal "
            "or regency opponent also remains uncurated."
        ),
        "evidence_refs": ["wave8_polish_usilesia_grotniki"],
    },
}


WAVE8_POLISH_AUDIT_CORRECTIONS: dict[str, dict[str, Any]] = {
    "hced-Cracow1772-1": {
        "event_id": "hced_hced_cracow1772_1",
        "name": "Cracow",
        "year": 1772,
        "expected_orientation": (
            ("russian_empire", "side_a", "engagement_victory", "limited_victory"),
            ("kingdom_france", "side_b", "engagement_defeat", "limited_defeat"),
        ),
        "side_a_entity_ids": ["russian_empire"],
        "side_b_entity_ids": ["kingdom_france", "bar_confederation_forces"],
        "draw": False,
        "scale_level": 2,
        "outcome_source_ids": ["wave8_polish_krakow_archive_wawel_1772"],
        "outcome_source_family_ids": ["national_archives_krakow"],
        "correction_note": (
            "Russian victory is retained, and the Bar Confederation forces omitted "
            "by the original crosswalk promotion are added as a co-loser alongside "
            "the French contingent."
        ),
    },
    "hced-Bydgoszcz1794-1": {
        "event_id": "hced_wave7_central_hced_bydgoszcz1794_1",
        "name": "Bydgoszcz",
        "year": 1794,
        "expected_orientation": (
            (
                "kosciuszko_uprising_forces",
                "side_a",
                "engagement_victory",
                "limited_victory",
            ),
            ("russian_empire", "side_b", "engagement_defeat", "limited_defeat"),
        ),
        "side_a_entity_ids": ["kosciuszko_uprising_forces"],
        "side_b_entity_ids": ["kingdom_prussia"],
        "draw": False,
        "scale_level": 2,
        "outcome_source_ids": ["wave8_polish_zpe_kosciuszko_battles"],
        "outcome_source_family_ids": ["polish_zpe_history"],
        "correction_note": (
            "The Kościuszko force took Bydgoszcz from Prussian control; the losing "
            "opponent is corrected from the Russian Empire to the Kingdom of Prussia."
        ),
    },
    "hced-Szczekociny1794-1": {
        "event_id": "hced_wave7_central_hced_szczekociny1794_1",
        "name": "Szczekociny",
        "year": 1794,
        "expected_orientation": (
            ("kingdom_prussia", "side_a", "engagement_victory", "limited_victory"),
            (
                "kosciuszko_uprising_forces",
                "side_b",
                "engagement_defeat",
                "limited_defeat",
            ),
        ),
        "side_a_entity_ids": ["kingdom_prussia", "russian_empire"],
        "side_b_entity_ids": ["kosciuszko_uprising_forces"],
        "draw": False,
        "scale_level": 3,
        "outcome_source_ids": ["wave8_polish_zpe_kosciuszko_battles"],
        "outcome_source_family_ids": ["polish_zpe_history"],
        "correction_note": (
            "The victorious side is corrected from Prussia alone to the documented "
            "combined Prussian-Russian army."
        ),
    },
    "hced-Grochow1831-1": {
        "event_id": "hced_wave7_central_hced_grochow1831_1",
        "name": "Grochow",
        "year": 1831,
        "expected_orientation": (
            (
                "november_uprising_polish_forces",
                "side_a",
                "engagement_victory",
                "limited_victory",
            ),
            ("russian_empire", "side_b", "engagement_defeat", "limited_defeat"),
        ),
        "side_a_entity_ids": ["november_uprising_polish_forces"],
        "side_b_entity_ids": ["russian_empire"],
        "draw": True,
        "scale_level": 3,
        "outcome_source_ids": [
            "wave8_polish_zpe_november_uprising_chronology"
        ],
        "outcome_source_family_ids": ["polish_zpe_history"],
        "correction_note": (
            "The official Polish chronology characterizes Grochów as indecisive; "
            "the raw Polish-victory assertion is replaced by an inconclusive draw."
        ),
    },
}


WAVE8_POLISH_AUDIT_CONTRACT_IDS = frozenset(WAVE8_POLISH_AUDIT_CONTRACTS)
WAVE8_POLISH_AUDIT_HOLD_IDS = frozenset(WAVE8_POLISH_AUDIT_HOLDS)
WAVE8_POLISH_AUDIT_RESERVED_IDS = (
    WAVE8_POLISH_AUDIT_CONTRACT_IDS | WAVE8_POLISH_AUDIT_HOLD_IDS
)
WAVE8_POLISH_AUDIT_CORRECTION_IDS = frozenset(WAVE8_POLISH_AUDIT_CORRECTIONS)
WAVE8_POLISH_AUDIT_CORRECTION_COUNT = len(WAVE8_POLISH_AUDIT_CORRECTIONS)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def wave8_polish_audit_correction_signature() -> str:
    return hashlib.sha256(
        _canonical_json(WAVE8_POLISH_AUDIT_CORRECTIONS).encode("utf-8")
    ).hexdigest()


def wave8_polish_audit_signature() -> str:
    payload = {
        "contracts": WAVE8_POLISH_AUDIT_CONTRACTS,
        "corrections": WAVE8_POLISH_AUDIT_CORRECTIONS,
        "holds": WAVE8_POLISH_AUDIT_HOLDS,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if len(WAVE8_POLISH_AUDIT_CONTRACTS) != 1:
        raise ValueError("Wave 8 Polish audit promotion inventory changed")
    if len(WAVE8_POLISH_AUDIT_HOLDS) != 4:
        raise ValueError("Wave 8 Polish audit hold inventory changed")
    if WAVE8_POLISH_AUDIT_CORRECTION_COUNT != 4:
        raise ValueError("Wave 8 Polish audit correction inventory changed")
    if len(WAVE8_POLISH_AUDIT_ENTITIES) != 1:
        raise ValueError("Wave 8 Polish audit entity inventory changed")
    if len(WAVE8_POLISH_AUDIT_SOURCES) != 7:
        raise ValueError("Wave 8 Polish audit source inventory changed")
    if WAVE8_POLISH_AUDIT_CONTRACT_IDS & WAVE8_POLISH_AUDIT_HOLD_IDS:
        raise ValueError("Wave 8 Polish audit promotion and hold inventories overlap")
    if (
        wave8_polish_audit_correction_signature()
        != WAVE8_POLISH_AUDIT_CORRECTION_SIGNATURE
    ):
        raise ValueError("Wave 8 Polish audit correction signature changed")
    if wave8_polish_audit_signature() != WAVE8_POLISH_AUDIT_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 Polish audit final signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_POLISH_AUDIT_SOURCES
    }
    if len(source_by_id) != len(WAVE8_POLISH_AUDIT_SOURCES):
        raise ValueError("Wave 8 Polish audit source IDs must be unique")
    entity_ids = {str(entity["id"]) for entity in WAVE8_POLISH_AUDIT_ENTITIES}
    if "polish_rebels" in entity_ids:
        raise ValueError("Wave 8 Polish audit must not create a generic rebel identity")
    for entity in WAVE8_POLISH_AUDIT_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError("Wave 8 Polish audit entities must be alias-free")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError("Wave 8 Polish audit entity permits rating inheritance")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError("Wave 8 Polish audit entity names an unknown source")

    reviewed = [
        *WAVE8_POLISH_AUDIT_CONTRACTS.values(),
        *WAVE8_POLISH_AUDIT_HOLDS.values(),
    ]
    for contract in reviewed:
        if not set(map(str, contract["evidence_refs"])) <= set(source_by_id):
            raise ValueError("Wave 8 Polish audit contract names an unknown source")
    correction_event_ids = {
        str(contract["event_id"])
        for contract in WAVE8_POLISH_AUDIT_CORRECTIONS.values()
    }
    if len(correction_event_ids) != WAVE8_POLISH_AUDIT_CORRECTION_COUNT:
        raise ValueError("Wave 8 Polish correction event IDs must be unique")
    for correction in WAVE8_POLISH_AUDIT_CORRECTIONS.values():
        outcome_ids = list(map(str, correction["outcome_source_ids"]))
        if not outcome_ids or not set(outcome_ids) <= set(source_by_id):
            raise ValueError("Wave 8 Polish correction lacks a known outcome source")
        for source_id in outcome_ids:
            if "outcome" not in source_by_id[source_id]["evidence_roles"]:
                raise ValueError("Wave 8 Polish correction source lacks outcome role")
        corrected_entities = {
            *map(str, correction["side_a_entity_ids"]),
            *map(str, correction["side_b_entity_ids"]),
        }
        if "polish_rebels" in corrected_entities:
            raise ValueError("Wave 8 Polish correction uses a generic rebel identity")


def validate_wave8_polish_audit_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_POLISH_AUDIT_CONTRACTS,
        WAVE8_POLISH_AUDIT_HOLDS,
        lane_name=_LANE_NAME,
    )


def install_wave8_polish_audit_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_POLISH_AUDIT_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_polish_audit_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_POLISH_AUDIT_SOURCES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_polish_audit_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_polish_audit_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_POLISH_AUDIT_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix="hced_wave8_polish_audit_",
    )


def _participant_orientation(event: Mapping[str, Any]) -> tuple[tuple[str, ...], ...]:
    return tuple(
        (
            str(participant.get("entity_id")),
            str(participant.get("side")),
            str(participant.get("termination")),
            str(participant.get("result_class")),
        )
        for participant in event.get("participants", [])
    )


def validate_wave8_polish_audit_correction_inputs(
    events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    """Validate the exact currently-published targets before any mutation."""

    _validate_static()
    materialized = list(events)
    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for event in materialized:
        candidate_id = event.get("hced_candidate_id")
        if isinstance(candidate_id, str):
            by_candidate.setdefault(candidate_id, []).append(event)
    event_ids = [str(event.get("id")) for event in materialized]
    if len(event_ids) != len(set(event_ids)):
        raise ValueError(f"{_LANE_NAME} correction input contains duplicate event IDs")

    for candidate_id, correction in WAVE8_POLISH_AUDIT_CORRECTIONS.items():
        matches = by_candidate.get(candidate_id, [])
        if len(matches) != 1:
            raise ValueError(
                f"{_LANE_NAME} correction {candidate_id} expected exactly one "
                f"published event, found {len(matches)}"
            )
        event = matches[0]
        expected_header = (
            str(correction["event_id"]),
            candidate_id,
            str(correction["name"]),
            int(correction["year"]),
            int(correction["year"]),
        )
        actual_header = (
            str(event.get("id")),
            str(event.get("hced_candidate_id")),
            str(event.get("name")),
            int(event.get("year", -10**9)),
            int(event.get("end_year", -10**9)),
        )
        if actual_header != expected_header:
            raise ValueError(
                f"{_LANE_NAME} correction header changed for {candidate_id}: "
                f"{actual_header!r} != {expected_header!r}"
            )
        orientation = _participant_orientation(event)
        if orientation != tuple(correction["expected_orientation"]):
            raise ValueError(
                f"{_LANE_NAME} current participant orientation changed for "
                f"{candidate_id}"
            )
        if list(event.get("outcome_source_ids", [])) != ["hced_dataset"]:
            raise ValueError(
                f"{_LANE_NAME} current outcome provenance changed for {candidate_id}"
            )
        if event.get("wave8_polish_audit_correction"):
            raise ValueError(
                f"{_LANE_NAME} correction was already applied to {candidate_id}"
            )
    return {"correction_targets": WAVE8_POLISH_AUDIT_CORRECTION_COUNT}


def apply_wave8_polish_audit_corrections(
    events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return a corrected copy while preserving every event ID and list position."""

    materialized = [copy.deepcopy(dict(event)) for event in events]
    validate_wave8_polish_audit_correction_inputs(materialized)
    original_ids = [str(event["id"]) for event in materialized]

    for event in materialized:
        candidate_id = event.get("hced_candidate_id")
        if candidate_id not in WAVE8_POLISH_AUDIT_CORRECTIONS:
            continue
        correction = WAVE8_POLISH_AUDIT_CORRECTIONS[str(candidate_id)]
        confidence = float(event["confidence"])
        is_draw = bool(correction["draw"])
        event["participants"] = _participants(
            list(map(str, correction["side_a_entity_ids"])),
            list(map(str, correction["side_b_entity_ids"])),
            is_draw,
            confidence,
            int(correction["scale_level"]),
            note=(
                "Fail-closed candidate-keyed Wave 8 Polish audit correction; no "
                "generic Polish-rebel identity or strategic result is inferred."
            ),
        )
        if is_draw:
            event["decisiveness"] = 0.32
        outcome_ids = list(map(str, correction["outcome_source_ids"]))
        event["source_ids"] = list(
            dict.fromkeys([*map(str, event.get("source_ids", [])), *outcome_ids])
        )
        event["outcome_source_ids"] = outcome_ids
        event["outcome_source_family_ids"] = list(
            map(str, correction["outcome_source_family_ids"])
        )
        event["summary"] = (
            "Fail-closed Wave 8 Polish audit correction of an already-published "
            "HCED event. The event ID, candidate ID, and event count are preserved; "
            "the pre-correction participant orientation was validated exactly. "
            + str(correction["correction_note"])
        )
        event["identity_resolution"] = "candidate_keyed_exact_wave8_correction"
        event["historical_outcome_correction"] = True
        event["wave8_polish_audit_correction"] = {
            "candidate_id": str(candidate_id),
            "correction_signature": WAVE8_POLISH_AUDIT_CORRECTION_SIGNATURE,
            "outcome_source_ids": outcome_ids,
            "preserves_event_id": True,
        }

    corrected_ids = [str(event["id"]) for event in materialized]
    if corrected_ids != original_ids:
        raise ValueError(f"{_LANE_NAME} corrections changed event IDs or ordering")
    corrected_count = sum(
        bool(event.get("wave8_polish_audit_correction")) for event in materialized
    )
    if corrected_count != WAVE8_POLISH_AUDIT_CORRECTION_COUNT:
        raise ValueError(
            f"{_LANE_NAME} corrected {corrected_count} events instead of "
            f"{WAVE8_POLISH_AUDIT_CORRECTION_COUNT}"
        )
    return materialized


def correct_wave8_polish_audit_events(
    events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Compatibility spelling for the in-place-release correction pass."""

    return apply_wave8_polish_audit_corrections(events)


def wave8_polish_audit_counts() -> dict[str, int]:
    return {
        "correction_targets": WAVE8_POLISH_AUDIT_CORRECTION_COUNT,
        "holds": len(WAVE8_POLISH_AUDIT_HOLDS),
        "newly_rated_events": len(WAVE8_POLISH_AUDIT_CONTRACTS),
        "promotion_contracts": len(WAVE8_POLISH_AUDIT_CONTRACTS),
        "reviewed_hced_rows": (
            len(WAVE8_POLISH_AUDIT_CONTRACTS)
            + len(WAVE8_POLISH_AUDIT_HOLDS)
            + WAVE8_POLISH_AUDIT_CORRECTION_COUNT
        ),
    }
