"""Exact Wave 8 dispositions for HCED rows blocked by ``Dacia``.

The five source rows collapse three separate Roman campaigns into a timeless
ethnic label.  This lane rates only the two Tapae engagements whose date,
opponents, and tactical outcome are independently defensible.  It installs one
polity bounded to Decebalus's reign, opens no generic Dacia alias, and leaves
the disputed 86 and Sarmizegetusa assertions unrated.  In particular, HCED's
incomplete ``Draw`` at Tapae in 101 is not accepted as a draw: direct evidence
supports a Roman victory and the correction is declared explicitly.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_DACIA_CONTRACT_IDS",
    "WAVE8_DACIA_CONTRACTS",
    "WAVE8_DACIA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_DACIA_CROSS_LANE_DISPOSITIONS",
    "WAVE8_DACIA_ENTITIES",
    "WAVE8_DACIA_EXCLUSION_IDS",
    "WAVE8_DACIA_EXCLUSIONS",
    "WAVE8_DACIA_EXPECTED_CANDIDATE_IDS",
    "WAVE8_DACIA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_DACIA_HOLD_IDS",
    "WAVE8_DACIA_HOLDS",
    "WAVE8_DACIA_INTEGRATION_DISPOSITIONS",
    "WAVE8_DACIA_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_DACIA_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_DACIA_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_DACIA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_DACIA_NONPROMOTIONS",
    "WAVE8_DACIA_OUTCOME_OVERRIDES",
    "WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_DACIA_RESERVED_IDS",
    "WAVE8_DACIA_SOURCES",
    "WAVE8_DACIA_TERMINAL_EXCLUSION_IDS",
    "WAVE8_DACIA_TERMINAL_EXCLUSIONS",
    "install_wave8_dacia_entities",
    "install_wave8_dacia_sources",
    "promote_wave8_dacia_contracts",
    "validate_wave8_dacia_integration_dispositions",
    "validate_wave8_dacia_queue_contracts",
    "wave8_dacia_audit_signature",
    "wave8_dacia_cohort_counts",
    "wave8_dacia_counts",
    "wave8_dacia_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Dacia campaign audit"
_MODULE_OWNER = "wave8_dacia"
_EVENT_ID_PREFIX = "hced_wave8_dacia_"
_ROMAN_EMPIRE_ID = "roman_empire"
_DECEBALUS_DACIA_ID = "decebalus_dacian_kingdom_87_106"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
    chronology: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if chronology:
        roles.append("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_DACIA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_dacia_oxford_decebalus",
        "Decebalus, king of Dacia",
        (
            "https://academic.oup.com/edited-volume/61673/"
            "chapter-abstract/548778681?login=false"
        ),
        "Oxford University Press, Oxford Classical Dictionary",
        "scholarly_classical_reference",
        "oxford_classical_dictionary_decebalus",
        outcome=True,
        chronology=True,
    ),
    _source(
        "wave8_dacia_sidebottom_dacian_wars",
        "The Dacian Wars, 84-106",
        "https://onlinelibrary.wiley.com/doi/abs/10.1002/9781119099000.wbabat0640",
        "Wiley, The Encyclopedia of Ancient Battles",
        "peer_reviewed_scholarly_reference",
        "sidebottom_encyclopedia_ancient_battles_dacian_wars",
        outcome=True,
        chronology=True,
    ),
    _source(
        "wave8_dacia_dio_book_67",
        "Cassius Dio, Roman History, Epitome of Book 67",
        (
            "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/"
            "Cassius_Dio/67%2A.html"
        ),
        "University of Chicago LacusCurtius; Loeb translation by Earnest Cary",
        "translated_primary_source",
        "cassius_dio_roman_history_cary_translation",
        outcome=True,
    ),
    _source(
        "wave8_dacia_dio_book_68",
        "Cassius Dio, Roman History, Epitome of Book 68",
        (
            "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/"
            "Cassius_Dio/68%2A.html"
        ),
        "University of Chicago LacusCurtius; Loeb translation by Earnest Cary",
        "translated_primary_source",
        "cassius_dio_roman_history_cary_translation",
        outcome=True,
    ),
    _source(
        "wave8_dacia_tekir_domitian_war",
        "Domitian's Dacian War",
        "https://dergipark.org.tr/en/pub/anasay/article/714329",
        "Anasay",
        "peer_reviewed_historical_article",
        "tekir_domitian_dacian_war",
        outcome=True,
        chronology=True,
    ),
    _source(
        "wave8_dacia_oltean_gis_conquest",
        (
            "GIS Analysis and Spatial Networking Patterns in Upland Ancient "
            "Warfare: The Roman Conquest of Dacia"
        ),
        "https://doi.org/10.3390/geosciences11010017",
        "Geosciences",
        "peer_reviewed_archaeological_article",
        "oltean_roman_conquest_dacia_gis",
        chronology=True,
    ),
    _source(
        "wave8_dacia_opreanu_first_war_topography",
        "The Topography of the First Dacian War of Trajan (A.D. 101-102)",
        "https://csiatim.uvt.ro/NOU/BHAUT/ro/pdf/2000_art4.pdf",
        "Bibliotheca Historica et Archaeologica Universitatis Timisiensis",
        "peer_reviewed_archaeological_article",
        "opreanu_first_dacian_war_topography",
        chronology=True,
    ),
)


WAVE8_DACIA_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _DECEBALUS_DACIA_ID,
        "name": "Dacian kingdom under Decebalus (87-106)",
        "kind": "monarchical_polity",
        "start_year": 87,
        "end_year": 106,
        "region": "Carpathian Dacia and the lower-Danube frontier",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Polity bounded to Decebalus's reign, including the client-kingdom "
            "interval between Domitian's and Trajan's wars, and ending with the "
            "Roman conquest in 106. No rating is inherited by Dacians as an ethnic "
            "group, an earlier Getic or Dacian kingdom, Roman Dacia, modern Romania, "
            "or any predecessor or successor."
        ),
        "source_ids": [
            "wave8_dacia_dio_book_67",
            "wave8_dacia_dio_book_68",
            "wave8_dacia_oxford_decebalus",
            "wave8_dacia_sidebottom_dacian_wars",
        ],
    },
)


_ROW_HASHES = {
    "hced-Sarmizegethusa102-1": (
        "6ff526de7f910b39f33f5779ee40c66a03a885f250d1b2f17e669af3b437f90a"
    ),
    "hced-Sarmizegethusa105-1": (
        "392b9d29a10565324a86ba335ee61b33c7b5fd0c3896eefb1f858e0d339badba"
    ),
    "hced-Tapae101-1": (
        "415ca192c8f8922b0adec7026e49ba799fdb8d2613bc83eb2725ee5b3731d8f5"
    ),
    "hced-Tapae86-1": (
        "5ccb8f512f244ba8063bd6290d51b75073bf030c8b27d5cf853bcc7803b8c886"
    ),
    "hced-Tapae88-1": (
        "41f1b773b776ca2a8fcc6a17bbd81c57560a5088acbd1b639e4840eb5b1ece66"
    ),
}

_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_DACIA_SOURCES
}


def _canonical(name: str, year: int, date_text: str) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "year",
        "date_text": date_text,
        "granularity": "engagement",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    historical_review: Mapping[str, Any],
    *,
    source_outcome_override: bool,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": [_ROMAN_EMPIRE_ID],
        "side_2_entity_ids": [_DECEBALUS_DACIA_ID],
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": False,
        "actor_override": True,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
        "historical_review": dict(historical_review),
    }


WAVE8_DACIA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Tapae88-1": _contract(
        "hced-Tapae88-1",
        _canonical("Battle of Tapae (Domitianic War)", 88, "88 CE"),
        "domitianic_dacian_war_86_89",
        [
            "wave8_dacia_dio_book_67",
            "wave8_dacia_oxford_decebalus",
            "wave8_dacia_sidebottom_dacian_wars",
            "wave8_dacia_tekir_domitian_war",
        ],
        [
            "wave8_dacia_dio_book_67",
            "wave8_dacia_oxford_decebalus",
            "wave8_dacia_sidebottom_dacian_wars",
            "wave8_dacia_tekir_domitian_war",
        ],
        (
            "Cassius Dio identifies Julianus's encounter at Tapae, the slaughter "
            "of many Dacians, and Decebalus's retreat stratagem; the independent "
            "modern references place that Roman victory in 88. This is distinct "
            "from Fuscus's earlier defeat and from Trajan's 101 battle."
        ),
        {
            "outcome": "roman_victory",
            "roman_commander": "Tettius Julianus",
            "dacian_ruler": "Decebalus",
            "boundary": "Domitianic campaign of 88",
        },
        source_outcome_override=False,
        confidence=0.96,
    ),
    "hced-Tapae101-1": _contract(
        "hced-Tapae101-1",
        _canonical(
            "Battle of Tapae (Trajan's First Dacian War)",
            101,
            "101 CE",
        ),
        "trajans_first_dacian_war_101_102",
        [
            "wave8_dacia_dio_book_68",
            "wave8_dacia_oltean_gis_conquest",
            "wave8_dacia_oxford_decebalus",
            "wave8_dacia_sidebottom_dacian_wars",
        ],
        [
            "wave8_dacia_dio_book_68",
            "wave8_dacia_oxford_decebalus",
            "wave8_dacia_sidebottom_dacian_wars",
        ],
        (
            "HCED's incomplete Draw is rejected. Cassius Dio describes Trajan "
            "engaging at Tapae, killing many of the enemy, and receiving envoys "
            "after Decebalus's defeat; the Oxford and Wiley references identify a "
            "hard-fought Roman victory in 101. The correction is source-declared, "
            "not an inference from a missing loser."
        ),
        {
            "outcome": "roman_victory",
            "roman_commander": "Trajan",
            "dacian_ruler": "Decebalus",
            "raw_outcome": "incomplete Draw with no loser",
            "boundary": "first engagement of Trajan's 101-102 war",
        },
        source_outcome_override=True,
        confidence=0.95,
    ),
}


def _hold(
    candidate_id: str,
    cohort: str,
    category: str,
    evidence_refs: Iterable[str],
    reason: str,
    review: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "cohort": cohort,
        "disposition": "hold",
        "hold_category": category,
        "result_type": "unknown",
        "reviewed_outcome": "unknown",
        "unknown_is_never_draw": True,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_nonpromotion",
        },
        "hold_reason": reason,
        "historical_review": dict(review),
    }


WAVE8_DACIA_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Tapae86-1": _hold(
        "hced-Tapae86-1",
        "domitianic_dacian_war_86_89",
        "event_year_and_battle_site_not_uniquely_defensible",
        [
            "wave8_dacia_dio_book_67",
            "wave8_dacia_sidebottom_dacian_wars",
            "wave8_dacia_tekir_domitian_war",
        ],
        (
            "The Wiley chronology places the Roman strike and Fuscus's defeat in "
            "86, while the reviewed campaign study dates Fuscus's expedition to "
            "87. Cassius Dio records the defeat but does not identify that episode "
            "as a battle at Tapae. A distinct Tapae engagement in exactly 86 is "
            "therefore not uniquely defensible; the row remains unknown and is "
            "never converted to a draw or silently moved to 87."
        ),
        {
            "raw_year": 86,
            "competing_year": 87,
            "raw_winner": "Dacia",
            "issue": "chronology and named-site attribution conflict",
        },
    ),
    "hced-Sarmizegethusa102-1": _hold(
        "hced-Sarmizegethusa102-1",
        "trajans_first_dacian_war_101_102",
        "named_tactical_engagement_not_uniquely_attested",
        [
            "wave8_dacia_dio_book_68",
            "wave8_dacia_oltean_gis_conquest",
            "wave8_dacia_opreanu_first_war_topography",
            "wave8_dacia_oxford_decebalus",
        ],
        (
            "The sources support Trajan's 102 campaign pressure, Decebalus's "
            "surrender, and a Roman garrison or occupation at Sarmizegetusa, but "
            "they do not isolate the HCED row as a distinct competitive battle at "
            "the city with its own tactical result. Scholarship also disputes the "
            "site sequence. Campaign occupation and treaty submission are not "
            "invented as an engagement or a draw."
        ),
        {
            "raw_year": 102,
            "raw_winner": "Rome",
            "attested_process": "campaign advance, surrender, and occupation",
            "issue": "distinct tactical battle boundary is unverified",
        },
    ),
    "hced-Sarmizegethusa105-1": _hold(
        "hced-Sarmizegethusa105-1",
        "trajans_second_dacian_war_105_106",
        "siege_year_and_event_boundary_not_uniquely_defensible",
        [
            "wave8_dacia_oltean_gis_conquest",
            "wave8_dacia_opreanu_first_war_topography",
            "wave8_dacia_oxford_decebalus",
        ],
        (
            "The second war began in 105, but the Oxford reference places the "
            "capture of the Dacian capital and creation of the province in 106. "
            "Archaeological scholarship treats the siege as a 105-106 campaign and "
            "questions which final Column scene belongs to Sarmizegetusa. The "
            "single-year 105 row cannot receive the later campaign outcome; its "
            "result remains unknown and never becomes a draw."
        ),
        {
            "raw_year": 105,
            "capture_year": 106,
            "raw_winner": "Rome",
            "issue": "multi-year siege and disputed site boundary",
        },
    ),
}


WAVE8_DACIA_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_DACIA_EXCLUSIONS = WAVE8_DACIA_TERMINAL_EXCLUSIONS
WAVE8_DACIA_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_DACIA_HOLDS,
    **WAVE8_DACIA_TERMINAL_EXCLUSIONS,
}

WAVE8_DACIA_CONTRACT_IDS = frozenset(WAVE8_DACIA_CONTRACTS)
WAVE8_DACIA_HOLD_IDS = frozenset(WAVE8_DACIA_HOLDS)
WAVE8_DACIA_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_DACIA_TERMINAL_EXCLUSIONS
)
WAVE8_DACIA_EXCLUSION_IDS = WAVE8_DACIA_TERMINAL_EXCLUSION_IDS
WAVE8_DACIA_RESERVED_IDS = frozenset(
    WAVE8_DACIA_CONTRACT_IDS
    | WAVE8_DACIA_HOLD_IDS
    | WAVE8_DACIA_TERMINAL_EXCLUSION_IDS
)
WAVE8_DACIA_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Tapae88-1", "hced-Tapae101-1"}
)
WAVE8_DACIA_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_DACIA_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_DACIA_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_DACIA_LOCATION_QUARANTINE_REASONS = {
    candidate_id: (
        "HCED supplies the same traditional Tapae point for distinct campaigns, "
        "while the reviewed literature does not establish that coordinate as the "
        "battlefield; retain Romania but withhold exact geometry."
    )
    for candidate_id in sorted(WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS)
}


WAVE8_DACIA_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Tapae101-1": {
        "raw_winner_raw": "Draw",
        "raw_loser_raw": None,
        "raw_winner_loser_complete": False,
        "corrected_result_type": "win",
        "corrected_winner_side": 1,
        "corrected_winner_entity_ids": [_ROMAN_EMPIRE_ID],
        "corrected_loser_entity_ids": [_DECEBALUS_DACIA_ID],
        "override_kind": "unknown_draw_placeholder_to_sourced_roman_victory",
        "outcome_source_ids": WAVE8_DACIA_CONTRACTS["hced-Tapae101-1"][
            "outcome_source_ids"
        ],
        "outcome_source_family_ids": WAVE8_DACIA_CONTRACTS["hced-Tapae101-1"][
            "outcome_source_family_ids"
        ],
    }
}

WAVE8_DACIA_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_DACIA_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_DACIA_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {}


# Candidate-keyed negative audit.  Adjacent 87 and 106 are intentionally
# included for the two chronology disputes, so a future duplicate cannot evade
# review merely by using the better-supported year.
WAVE8_DACIA_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Sarmizegethusa102-1": {
        "aliases": (
            "battle of sarmizegetusa",
            "sarmizegethusa",
            "sarmizegetusa",
            "siege of sarmizegetusa",
        ),
        "years": (102,),
    },
    "hced-Sarmizegethusa105-1": {
        "aliases": (
            "battle of sarmizegetusa",
            "sarmizegethusa",
            "sarmizegetusa",
            "siege of sarmizegetusa",
        ),
        "years": (105, 106),
    },
    "hced-Tapae101-1": {
        "aliases": (
            "battle of tapae",
            "battle of tapae trajans first dacian war",
            "tapae",
        ),
        "years": (101,),
    },
    "hced-Tapae86-1": {
        "aliases": ("battle of tapae", "tapae"),
        "years": (86, 87),
    },
    "hced-Tapae88-1": {
        "aliases": (
            "battle of tapae",
            "battle of tapae domitianic war",
            "tapae",
        ),
        "years": (88,),
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_DACIA_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_DACIA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_DACIA_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_DACIA_ENTITIES,
        "expected_candidate_ids": sorted(WAVE8_DACIA_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_DACIA_HOLDS,
        "integration_dispositions": WAVE8_DACIA_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_DACIA_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_DACIA_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_DACIA_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_DACIA_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_DACIA_SOURCES,
        "terminal_exclusions": WAVE8_DACIA_TERMINAL_EXCLUSIONS,
    }


def wave8_dacia_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_DACIA_FINAL_AUDIT_SIGNATURE = (
    "13aefd4ebd02647c202b2c67f1410842b12dfaa57b4a79447d186aa344dc01aa"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_DACIA_CONTRACTS),
        len(WAVE8_DACIA_HOLDS),
        len(WAVE8_DACIA_TERMINAL_EXCLUSIONS),
    ) != (2, 3, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_DACIA_ENTITIES), len(WAVE8_DACIA_SOURCES)) != (1, 7):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_DACIA_RESERVED_IDS != WAVE8_DACIA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    dispositions = (
        WAVE8_DACIA_CONTRACT_IDS,
        WAVE8_DACIA_HOLD_IDS,
        WAVE8_DACIA_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(3)
        for j in range(i + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if WAVE8_DACIA_EXCLUSIONS is not WAVE8_DACIA_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion inventory diverged")
    if wave8_dacia_audit_signature() != WAVE8_DACIA_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_DACIA_SOURCES}
    if len(source_by_id) != len(WAVE8_DACIA_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_DACIA_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_DACIA_ENTITIES}
    if set(entity_by_id) != {_DECEBALUS_DACIA_ID}:
        raise ValueError(f"{_LANE_NAME} bounded identity inventory changed")
    entity = entity_by_id[_DECEBALUS_DACIA_ID]
    if (entity["start_year"], entity["end_year"]) != (87, 106):
        raise ValueError(f"{_LANE_NAME} Dacian identity window changed")
    if entity["aliases"] or entity["predecessors"]:
        raise ValueError(f"{_LANE_NAME} opened a generic identity fallback")
    if normalize_label(entity["name"]) in {"dacia", "dacians", "romania"}:
        raise ValueError(f"{_LANE_NAME} installed a timeless identity")
    note = str(entity["continuity_note"]).casefold()
    if "no rating is inherited" not in note or "modern romania" not in note:
        raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
    if not _is_sorted_unique(entity["source_ids"]):
        raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
    if not set(map(str, entity["source_ids"])) <= set(source_by_id):
        raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_new_entities: set[str] = set()
    used_sources: set[str] = set()
    override_ids: set[str] = set()
    for candidate_id, contract in WAVE8_DACIA_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["year_low"] != canonical["year_high"]:
            raise ValueError(f"{_LANE_NAME} widened an HCED year")
        if canonical["granularity"] != "engagement":
            raise ValueError(f"{_LANE_NAME} promoted a non-engagement")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if side_1 != [_ROMAN_EMPIRE_ID] or side_2 != [_DECEBALUS_DACIA_ID]:
            raise ValueError(f"{_LANE_NAME} actor contract drifted")
        used_new_entities.update(set(side_1 + side_2) & set(entity_by_id))
        if contract["result_type"] != "win" or contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} invented a draw or outcome")
        if contract["outcome_reversal"] is not False:
            raise ValueError(f"{_LANE_NAME} mislabeled an outcome reversal")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor resolution is not explicit")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
        if contract["source_outcome_override"]:
            override_ids.add(candidate_id)

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if not outcomes or not _is_sorted_unique(outcomes) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        used_sources.update(evidence)

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identity is not exactly consumed")
    if override_ids != {"hced-Tapae101-1"}:
        raise ValueError(f"{_LANE_NAME} outcome override inventory changed")
    if set(WAVE8_DACIA_OUTCOME_OVERRIDES) != override_ids:
        raise ValueError(f"{_LANE_NAME} outcome override metadata drifted")
    override = WAVE8_DACIA_OUTCOME_OVERRIDES["hced-Tapae101-1"]
    contract = WAVE8_DACIA_CONTRACTS["hced-Tapae101-1"]
    if (
        override["corrected_winner_side"] != contract["winner_side"]
        or override["corrected_winner_entity_ids"]
        != contract["side_1_entity_ids"]
        or override["corrected_loser_entity_ids"]
        != contract["side_2_entity_ids"]
        or override["outcome_source_ids"] != contract["outcome_source_ids"]
        or override["outcome_source_family_ids"]
        != contract["outcome_source_family_ids"]
    ):
        raise ValueError(f"{_LANE_NAME} corrected outcome metadata drifted")

    for candidate_id, hold in WAVE8_DACIA_HOLDS.items():
        if hold["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} hold hash drifted")
        if (
            hold["disposition"] != "hold"
            or hold["result_type"] != "unknown"
            or hold["reviewed_outcome"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
            or "winner_side" in hold
        ):
            raise ValueError(f"{_LANE_NAME} unknown outcome became a draw or win")
        if hold["duplicate_ownership"]["owner_module"] != _MODULE_OWNER:
            raise ValueError(f"{_LANE_NAME} nonpromotion ownership drifted")
        refs = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence drifted")
        used_sources.update(refs)

    used_sources.update(map(str, entity["source_ids"]))
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS != WAVE8_DACIA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_DACIA_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_DACIA_LOCATION_QUARANTINE_REASONS) != WAVE8_DACIA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reasons are incomplete")
    if (
        WAVE8_DACIA_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_DACIA_CROSS_LANE_DISPOSITIONS
        or WAVE8_DACIA_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty duplicate inventories changed")
    if set(WAVE8_DACIA_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_DACIA_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")


def validate_wave8_dacia_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_DACIA_CONTRACTS,
        WAVE8_DACIA_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_DACIA_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_DACIA_TERMINAL_EXCLUSIONS),
    }


def _year(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _iwbd_year(row: Mapping[str, Any]) -> int | None:
    for field in ("start_date", "end_date"):
        text = str(row.get(field) or "")
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4])
    return _year(row.get("year"))


def _audited_name_year_pairs() -> set[tuple[int, str]]:
    return {
        (int(year), normalize_label(alias))
        for item in WAVE8_DACIA_IWBD_ZERO_OVERLAP_AUDIT.values()
        for year in item["years"]
        for alias in item["aliases"]
    }


def validate_wave8_dacia_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin zero duplicates and fail on any future probable event twin."""

    validate_wave8_dacia_queue_contracts(hced_rows)
    audited = _audited_name_year_pairs()

    hced_collisions = []
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id") or "")
        if candidate_id in WAVE8_DACIA_RESERVED_IDS:
            continue
        year = _year(row.get("year_best"))
        name = normalize_label(row.get("name"))
        if year is not None and (year, name) in audited:
            hced_collisions.append(candidate_id or "<missing-id>")
    if hced_collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): "
            f"{sorted(hced_collisions)}"
        )

    iwbd_collisions = []
    for row in iwbd_rows:
        year = _iwbd_year(row)
        name = normalize_label(row.get("name"))
        if year is not None and (year, name) in audited:
            iwbd_collisions.append(str(row.get("candidate_id") or "<missing-id>"))
    if iwbd_collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): "
            f"{sorted(iwbd_collisions)}"
        )

    release_collisions = []
    for event in existing_events:
        candidate_id = str(event.get("hced_candidate_id") or "")
        if candidate_id in WAVE8_DACIA_RESERVED_IDS:
            continue
        year = _year(event.get("year"))
        name = normalize_label(event.get("name"))
        aliases = {name, *map(normalize_label, event.get("aliases", []))}
        if year is not None and any((year, alias) in audited for alias in aliases):
            release_collisions.append(str(event.get("id") or "<missing-id>"))
    if release_collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): "
            f"{sorted(release_collisions)}"
        )

    return {
        "cross_lane_hced_dispositions": 0,
        "existing_release_duplicate_dispositions": 0,
        "integration_dispositions": 0,
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_dacia_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_DACIA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_dacia_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_DACIA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_DACIA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_dacia_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_dacia_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_DACIA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_dacia_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_DACIA_CONTRACTS.values(),
                    *WAVE8_DACIA_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_dacia_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_DACIA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(WAVE8_DACIA_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": 0,
        "holds": len(WAVE8_DACIA_HOLDS),
        "integration_dispositions": len(WAVE8_DACIA_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_DACIA_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_DACIA_ENTITIES),
        "new_sources": len(WAVE8_DACIA_SOURCES),
        "newly_rated_events": len(WAVE8_DACIA_CONTRACTS),
        "outcome_overrides": len(WAVE8_DACIA_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_DACIA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_DACIA_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_DACIA_TERMINAL_EXCLUSIONS),
    }


def wave8_dacia_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_DACIA_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS,
    }
