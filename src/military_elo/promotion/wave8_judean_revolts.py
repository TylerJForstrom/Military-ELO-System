"""Exact Wave 8 dispositions for HCED's generic ``Jewish Rebels`` rows."""

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


_LANE_NAME = "Wave 8 Judean revolts"
WAVE8_JUDEAN_REVOLTS_FINAL_AUDIT_SIGNATURE = (
    "6ce0b6bfee7d52aae4c786d0f7a1bf9c3b8ec42cdfaeed3e5afdfdfd68c6e3a2"
)


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    family: str,
    source_type: str,
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
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": family,
        "evidence_roles": roles,
    }


WAVE8_JUDEAN_REVOLTS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_judean_met_world_between_empires",
        "The World between Empires: Art and Identity in the Ancient Middle East",
        (
            "https://resources.metmuseum.org/resources/metpublications/pdf/"
            "The_World_between_Empires_Art_and_Identity_in_the_Ancient_Middle_East.pdf"
        ),
        "Metropolitan Museum of Art",
        "metropolitan_museum_ancient_middle_east",
        "museum_scholarly_catalogue",
    ),
    _source(
        "wave8_judean_josephus_jewish_war",
        "The Jewish War",
        "https://classics.mit.edu/Josephus/j.bj.html",
        "MIT Internet Classics Archive / Perseus Project",
        "josephus_jewish_war_primary",
        "primary_source_translation",
        outcome=True,
    ),
    _source(
        "wave8_judean_roy_pre_modern_warfare",
        "A Global History of Pre-Modern Warfare",
        (
            "https://www.routledge.com/A-Global-History-of-Pre-Modern-Warfare-"
            "Before-the-Rise-of-the-West-10000-BCE-1500-CE/Roy/p/book/9780367247171"
        ),
        "Routledge",
        "routledge_pre_modern_warfare",
        "academic_book",
        outcome=True,
    ),
    _source(
        "wave8_judean_1_maccabees_4",
        "The Book of Maccabees I, chapter 4",
        "https://www.sefaria.org/The_Book_of_Maccabees_I.4.1-35",
        "Sefaria Library",
        "first_maccabees_primary",
        "primary_source_translation",
        outcome=True,
    ),
    _source(
        "wave8_judean_cambridge_judas_maccabaeus",
        "Judas Maccabaeus: The Jewish Struggle against the Seleucids",
        (
            "https://www.cambridge.org/core/books/judas-maccabaeus/"
            "lysias-second-expedition-and-the-battle-at-beth-zacharia/"
            "0194BB737CA64265961A7B023D97E3CF"
        ),
        "Cambridge University Press",
        "cambridge_judas_maccabaeus",
        "academic_book",
    ),
)


WAVE8_JUDEAN_REVOLTS_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "maccabean_revolt_judean_forces_167_160_bce",
        "name": "Judean forces of the Maccabean Revolt (167–160 BCE)",
        "kind": "rebel_polity",
        "start_year": -167,
        "end_year": -160,
        "region": "Judea",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Conflict-bounded forces led by Mattathias and Judas Maccabaeus. No "
            "rating is inherited by the later Hasmonean state, other Judean "
            "revolts, modern Jewish polities, or a generic Jewish-rebels label."
        ),
        "source_ids": [
            "wave8_judean_roy_pre_modern_warfare",
            "wave8_judean_cambridge_judas_maccabaeus",
        ],
    },
    {
        "id": "great_jewish_revolt_judean_forces_66_73",
        "name": "Judean forces of the Great Jewish Revolt (66–73)",
        "kind": "rebel_polity",
        "start_year": 66,
        "end_year": 73,
        "region": "Roman Judea",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Conflict-bounded Judean revolt forces beginning in 66 CE. No rating "
            "is inherited by the Bar Kokhba revolt, ancient predecessor states, "
            "modern Jewish polities, or a generic Jewish-rebels label."
        ),
        "source_ids": [
            "wave8_judean_met_world_between_empires",
            "wave8_judean_josephus_jewish_war",
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


WAVE8_JUDEAN_REVOLTS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Beth Horon66-1": {
        "raw_row_sha256": (
            "0a0d69bc5034403fd2e369c63cac48097e107726b7e5f9d49b6c25fbf064d530"
        ),
        "canonical_event": _canonical("Battle of Beth Horon", 66),
        "cohort": "great_jewish_revolt",
        "side_1_entity_ids": ["great_jewish_revolt_judean_forces_66_73"],
        "side_2_entity_ids": ["roman_empire"],
        "winner_side": 1,
        "war_type": "anti_imperial_revolt",
        "evidence_refs": [
            "wave8_judean_met_world_between_empires",
            "wave8_judean_josephus_jewish_war",
        ],
        "outcome_source_ids": ["wave8_judean_josephus_jewish_war"],
        "outcome_source_family_ids": ["josephus_jewish_war_primary"],
        "source_outcome_override": False,
        "audit_note": (
            "Josephus directly describes Cestius Gallus's routed withdrawal in "
            "66 CE. The winning identity is confined to this revolt."
        ),
    },
    "hced-Emmaus-166-1": {
        "raw_row_sha256": (
            "4a18af24a42aa74db6da948b469fc8a421494f06949497b3edae8f6b688964c9"
        ),
        "canonical_event": _canonical("Battle of Emmaus", -166),
        "cohort": "maccabean_revolt",
        "side_1_entity_ids": ["maccabean_revolt_judean_forces_167_160_bce"],
        "side_2_entity_ids": ["clio_ir_seleucid_emp_bce318_21d0ee32"],
        "winner_side": 1,
        "war_type": "anti_imperial_revolt",
        "evidence_refs": [
            "wave8_judean_roy_pre_modern_warfare",
            "wave8_judean_1_maccabees_4",
        ],
        "outcome_source_ids": [
            "wave8_judean_1_maccabees_4",
            "wave8_judean_roy_pre_modern_warfare",
        ],
        "outcome_source_family_ids": [
            "first_maccabees_primary",
            "routledge_pre_modern_warfare",
        ],
        "source_outcome_override": False,
        "audit_note": (
            "The staged row cites Roy's academic chronology, while 1 Maccabees "
            "directly describes the Seleucid force's defeat and flight."
        ),
    },
}


WAVE8_JUDEAN_REVOLTS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Aelia133-135-1": {
        "raw_row_sha256": "aa41015a701b3f070aed3c920ffdb3fa8948fc6982e3e479d12b9daec36d817a",
        "canonical_event": _canonical("Aelia", 133),
        "hold_category": "campaign_or_massacre_not_distinct_engagement",
        "hold_reason": (
            "The source supports Roman suppression of the 132–135 revolt, but the "
            "row collapses Aelia, a massacre assertion, and the wider campaign into "
            "one year. No distinct tactical outcome is manufactured."
        ),
        "evidence_refs": ["wave8_judean_met_world_between_empires"],
    },
    "hced-Beth Zachariah-164-1": {
        "raw_row_sha256": "9a535ff8eb9776ccf80f8aa6c965978df3fcc623cdaa9849661a6501d8d92f55",
        "canonical_event": _canonical("Beth Zachariah", -164),
        "hold_category": "source_date_conflict",
        "hold_reason": (
            "The HCED year conflicts with the reviewed academic chronology, which "
            "places Lysias's second expedition and Beth Zachariah later."
        ),
        "evidence_refs": ["wave8_judean_cambridge_judas_maccabaeus"],
    },
    "hced-Beth Zur-166-1": {
        "raw_row_sha256": "2d8c4d98265bfe0e6a2f1281aeeb098d38043cbdad52d592e14b520fb5ecb347",
        "canonical_event": _canonical("Beth Zur", -166),
        "hold_category": "source_date_conflict",
        "hold_reason": (
            "Reviewed chronologies place the engagement in 165/164 BCE rather "
            "than the row's exact 166 BCE year."
        ),
        "evidence_refs": ["wave8_judean_cambridge_judas_maccabaeus"],
    },
    "hced-Elasa-161-1": {
        "raw_row_sha256": "1c6fd84e264ff160ef954b922689ff826da0eeafbc852cd02cb854558ee70467",
        "canonical_event": _canonical("Elasa", -161),
        "hold_category": "source_date_conflict",
        "hold_reason": (
            "The death of Judas is variously assigned to 161 or 160 BCE; the "
            "year-precision row remains staged pending one explicit chronology."
        ),
        "evidence_refs": ["wave8_judean_cambridge_judas_maccabaeus"],
    },
    "hced-Gophna-166-1": {
        "raw_row_sha256": "0d4fdbc1d5778b9c22a1a4f8044930211ef7ce4ad7477e0d39dccb07dfb2adf1",
        "canonical_event": _canonical("Gophna", -166),
        "hold_category": "distinct_engagement_unverified",
        "hold_reason": (
            "The reviewed sources do not establish a separate competitive battle "
            "at Gophna matching this row, so no result is inferred from the wider "
            "Maccabean campaign."
        ),
        "evidence_refs": [
            "wave8_judean_roy_pre_modern_warfare",
            "wave8_judean_1_maccabees_4",
        ],
    },
}


WAVE8_JUDEAN_REVOLTS_CONTRACT_IDS = frozenset(WAVE8_JUDEAN_REVOLTS_CONTRACTS)
WAVE8_JUDEAN_REVOLTS_HOLD_IDS = frozenset(WAVE8_JUDEAN_REVOLTS_HOLDS)
WAVE8_JUDEAN_REVOLTS_RESERVED_IDS = (
    WAVE8_JUDEAN_REVOLTS_CONTRACT_IDS | WAVE8_JUDEAN_REVOLTS_HOLD_IDS
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def wave8_judean_revolts_signature() -> str:
    return hashlib.sha256(
        _canonical_json(
            {
                "contracts": WAVE8_JUDEAN_REVOLTS_CONTRACTS,
                "holds": WAVE8_JUDEAN_REVOLTS_HOLDS,
            }
        ).encode()
    ).hexdigest()


def _validate_static() -> None:
    if (len(WAVE8_JUDEAN_REVOLTS_CONTRACTS), len(WAVE8_JUDEAN_REVOLTS_HOLDS)) != (2, 5):
        raise ValueError("Wave 8 Judean-revolts disposition inventory changed")
    if wave8_judean_revolts_signature() != WAVE8_JUDEAN_REVOLTS_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 Judean-revolts audit signature changed")
    if WAVE8_JUDEAN_REVOLTS_CONTRACT_IDS & WAVE8_JUDEAN_REVOLTS_HOLD_IDS:
        raise ValueError("Wave 8 Judean-revolts dispositions overlap")
    source_ids = {str(source["id"]) for source in WAVE8_JUDEAN_REVOLTS_SOURCES}
    if any(entity["aliases"] or entity["predecessors"] for entity in WAVE8_JUDEAN_REVOLTS_ENTITIES):
        raise ValueError("Wave 8 Judean-revolts identities must be alias-free")
    for entity in WAVE8_JUDEAN_REVOLTS_ENTITIES:
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError("Wave 8 Judean-revolts identity permits inheritance")
        if not set(map(str, entity["source_ids"])) <= source_ids:
            raise ValueError("Wave 8 Judean-revolts identity names an unknown source")
    for item in {**WAVE8_JUDEAN_REVOLTS_CONTRACTS, **WAVE8_JUDEAN_REVOLTS_HOLDS}.values():
        if not set(map(str, item["evidence_refs"])) <= source_ids:
            raise ValueError("Wave 8 Judean-revolts item names an unknown source")


def validate_wave8_judean_revolts_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_JUDEAN_REVOLTS_CONTRACTS,
        WAVE8_JUDEAN_REVOLTS_HOLDS,
        lane_name=_LANE_NAME,
    )


def install_wave8_judean_revolts_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_JUDEAN_REVOLTS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_judean_revolts_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_JUDEAN_REVOLTS_SOURCES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_judean_revolts_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_judean_revolts_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_JUDEAN_REVOLTS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix="hced_wave8_judean_revolts_",
    )


def wave8_judean_revolts_counts() -> dict[str, int]:
    return {
        "holds": len(WAVE8_JUDEAN_REVOLTS_HOLDS),
        "newly_rated_events": len(WAVE8_JUDEAN_REVOLTS_CONTRACTS),
        "promotion_contracts": len(WAVE8_JUDEAN_REVOLTS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_JUDEAN_REVOLTS_RESERVED_IDS),
    }
