"""Candidate-keyed Great Northern War audit for three locked HCED rows.

The source rows compress coalition names and, for Tönning and Stralsund,
event boundaries.  This lane therefore promotes only the three fingerprinted
records below.  It reuses five already-curated, time-valid identities, expands
each coalition only from direct evidence, and never installs a label alias.

The 1713 record is Stenbock's field-army capitulation at Oldenswort.  It is not
the later siege and surrender of Tönning fortress.  The Stralsund record is
narrowed to the final July--December 1715 siege.  ``hced-Gotland1563-1`` is
outside this lane: its draw is supported, but a time-valid Lübeck identity is
still absent.  Unknown or incomplete identity is never converted to a draw.
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
    "WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS",
    "WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS",
    "WAVE8_GREAT_NORTHERN_EXACT_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_GREAT_NORTHERN_EXACT_ENTITIES",
    "WAVE8_GREAT_NORTHERN_EXACT_EXPECTED_CANDIDATE_IDS",
    "WAVE8_GREAT_NORTHERN_EXACT_FINAL_AUDIT_SIGNATURE",
    "WAVE8_GREAT_NORTHERN_EXACT_HOLDS",
    "WAVE8_GREAT_NORTHERN_EXACT_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_GREAT_NORTHERN_EXACT_LOCATION_REVIEWS",
    "WAVE8_GREAT_NORTHERN_EXACT_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_GREAT_NORTHERN_EXACT_REQUIRED_EXISTING_ENTITY_IDS",
    "WAVE8_GREAT_NORTHERN_EXACT_RESERVED_IDS",
    "WAVE8_GREAT_NORTHERN_EXACT_ROW_HASHES",
    "WAVE8_GREAT_NORTHERN_EXACT_SOURCES",
    "install_wave8_great_northern_exact_entities",
    "install_wave8_great_northern_exact_sources",
    "promote_wave8_great_northern_exact_contracts",
    "validate_wave8_great_northern_exact_existing_entities",
    "validate_wave8_great_northern_exact_integration_dispositions",
    "validate_wave8_great_northern_exact_queue_contracts",
    "wave8_great_northern_exact_audit_signature",
    "wave8_great_northern_exact_cohort_counts",
    "wave8_great_northern_exact_counts",
    "wave8_great_northern_exact_location_quarantine_additions",
    "wave8_great_northern_exact_metadata",
)


_LANE_NAME = "Wave 8 candidate-keyed Great Northern exact audit"
_MODULE_OWNER = "military_elo.promotion.wave8_great_northern_exact"
_EVENT_ID_PREFIX = "hced_wave8_great_northern_exact_"

_SWEDEN = "kingdom_sweden"
_DENMARK = "kingdom_denmark"
_SAXONY = "electorate_saxony_1356"
_RUSSIA = "clio_ru_moskva_rurik_dyn_1547_93deb0e2"
_PRUSSIA = "kingdom_prussia"


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
        "accessed": "2026-07-21",
        "source_family_id": source_family_id,
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    }


WAVE8_GREAT_NORTHERN_EXACT_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_great_northern_exact_landers_field_forge",
        "The Field and the Forge: Population, Production, and Power in the Pre-Industrial West",
        "https://academic.oup.com/book/1842",
        "Oxford University Press",
        "scholarly_military_history_monograph",
        "landers_field_forge",
    ),
    _source(
        "wave8_great_northern_exact_clodfelter_warfare",
        "Warfare and Armed Conflicts: A Statistical Encyclopedia, p. 89",
        "https://books.google.com/books?id=8urEDgAAQBAJ&pg=PA89",
        "McFarland / Google Books",
        "scholarly_military_reference",
        "clodfelter_warfare_armed_conflicts",
    ),
    _source(
        "wave8_great_northern_exact_danish_general_staff_v4",
        "Bidrag til den Store Nordiske Krigs Historie, bind IV",
        "https://www.marinehist.dk/orlogsbib/SNK/SNK-bind4.pdf",
        "Danish General Staff historical section / Marinehistorisk Selskab",
        "official_military_history_digitization",
        "danish_general_staff_great_northern_war_volume_four",
    ),
    _source(
        "wave8_great_northern_exact_riksarkivet_stenbock",
        "Magnus Stenbock",
        "https://sok.riksarkivet.se/sbl/Presentation.aspx?id=20072",
        "Svenskt biografiskt lexikon / National Archives of Sweden",
        "national_scholarly_biography",
        "swedish_biographical_lexicon_stenbock",
    ),
    _source(
        "wave8_great_northern_exact_svmm_gadebusch",
        "1712 Slaget vid Gadebusch",
        "https://svmm.se/slaget-vid-gadebusch-1712-ty16/",
        "Svenska militära minnesmärken",
        "institutional_military_memorial_history",
        "swedish_military_memorials_gadebusch",
    ),
    _source(
        "wave8_great_northern_exact_ghdi_stralsund",
        "Commemorative Diagram of the Siege of Stralsund in the Year 1715",
        (
            "https://germanhistorydocs.org/en/the-holy-roman-empire-1648-1815/"
            "commemorative-diagram-of-the-siege-of-stralsund-in-the-year-1715-1718"
        ),
        "German History in Documents and Images / German Historical Institute",
        "scholarly_document_exhibit",
        "ghdi_stralsund_1715",
    ),
    _source(
        "wave8_great_northern_exact_rct_stralsund",
        "Map of the siege of Stralsund, 1715 (RCIN 726091)",
        (
            "https://militarymaps.rct.uk/other-18th/19th-century-conflicts/"
            "map-of-the-siege-of-stralsund-1715-stralsund-mecklenburg-"
            "vorpommern-germany-54deg1832n-13deg0454e-1"
        ),
        "Royal Collection Trust",
        "curated_historical_map_catalogue",
        "royal_collection_stralsund_1715_map",
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_GREAT_NORTHERN_EXACT_SOURCES
}


# All five actors already exist in the release.  An empty fixture is a
# mechanical guarantee that this lane cannot add aliases or duplicate them.
WAVE8_GREAT_NORTHERN_EXACT_ENTITIES: tuple[dict[str, Any], ...] = ()


_EXISTING_ENTITY_PINS: dict[str, dict[str, Any]] = {
    _SWEDEN: {
        "id": _SWEDEN,
        "name": "Kingdom of Sweden",
        "kind": "kingdom",
        "start_year": 1523,
        "end_year": None,
    },
    _DENMARK: {
        "id": _DENMARK,
        "name": "Kingdom of Denmark",
        "kind": "kingdom",
        "start_year": 1523,
        "end_year": None,
    },
    _SAXONY: {
        "id": _SAXONY,
        "name": "Electorate of Saxony",
        "kind": "electorate",
        "start_year": 1356,
        "end_year": 1806,
    },
    _RUSSIA: {
        "id": _RUSSIA,
        "name": "Tsardom of Russia",
        "kind": "tsardom",
        "start_year": 1547,
        "end_year": 1720,
    },
    _PRUSSIA: {
        "id": _PRUSSIA,
        "name": "Kingdom of Prussia",
        "kind": "kingdom",
        "start_year": 1701,
        "end_year": 1871,
    },
}
WAVE8_GREAT_NORTHERN_EXACT_REQUIRED_EXISTING_ENTITY_IDS = frozenset(
    _EXISTING_ENTITY_PINS
)


WAVE8_GREAT_NORTHERN_EXACT_ROW_HASHES: dict[str, str] = {
    "hced-Gadebusch1712-1": (
        "0ee27a3f3a8a53df31d880d82a31fb009a9537f4c0e0943c377e5709ef4ddf8d"
    ),
    "hced-Tonning1713-1": (
        "1eabbee1c511d4ac367234b412445364bd3d43133fc1f6bfad53e05db8b5d97b"
    ),
    "hced-Stralsund1714-1715-1": (
        "01951636c6c223ae71597edfc6df7ce65328b6e9b9a339c2078076a0c22dbddb"
    ),
}
WAVE8_GREAT_NORTHERN_EXACT_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_GREAT_NORTHERN_EXACT_ROW_HASHES
)


def _canonical(
    name: str,
    year_low: int,
    year_high: int,
    date_text: str,
    *,
    date_precision: str,
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
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    source_date_override: bool = False,
    date_source_ids: Iterable[str] = (),
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    contract: dict[str, Any] = {
        "raw_row_sha256": WAVE8_GREAT_NORTHERN_EXACT_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "great_northern_war_1712_1715",
        "side_1_entity_ids": sorted(set(map(str, side_1))),
        "side_2_entity_ids": sorted(set(map(str, side_2))),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate",
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
        "actor_override": "candidate_keyed_exact_great_northern_coalition",
        "event_type": "engagement",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }
    if source_date_override:
        contract["source_date_override"] = True
        contract["date_source_ids"] = sorted(set(map(str, date_source_ids)))
    return contract


WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Gadebusch1712-1": _contract(
        "hced-Gadebusch1712-1",
        _canonical(
            "Battle of Gadebusch",
            1712,
            1712,
            "9 December 1712 Old Style (20 December Gregorian)",
            date_precision="dual_calendar_day",
            granularity="single_pitched_battle_at_wakenstadt_near_gadebusch",
        ),
        [_SWEDEN],
        [_DENMARK, _SAXONY],
        [
            "wave8_great_northern_exact_clodfelter_warfare",
            "wave8_great_northern_exact_danish_general_staff_v4",
            "wave8_great_northern_exact_landers_field_forge",
            "wave8_great_northern_exact_svmm_gadebusch",
        ],
        [
            "wave8_great_northern_exact_clodfelter_warfare",
            "wave8_great_northern_exact_danish_general_staff_v4",
            "wave8_great_northern_exact_landers_field_forge",
            "wave8_great_northern_exact_svmm_gadebusch",
        ],
        (
            "Stenbock's Swedish army defeated the combined Danish and Saxon "
            "army at Wakenstädt near Gadebusch. The contract retains only that "
            "tactical victory and does not infer the later campaign result."
        ),
        confidence=0.96,
    ),
    "hced-Tonning1713-1": _contract(
        "hced-Tonning1713-1",
        _canonical(
            "Capitulation at Oldenswort",
            1713,
            1713,
            "5 May 1713 Old Style (16 May Gregorian)",
            date_precision="dual_calendar_day",
            granularity=(
                "stenbock_field_army_capitulation_at_oldenswort_not_the_"
                "tonning_fortress_siege"
            ),
        ),
        [_DENMARK, _RUSSIA, _SAXONY],
        [_SWEDEN],
        [
            "wave8_great_northern_exact_clodfelter_warfare",
            "wave8_great_northern_exact_danish_general_staff_v4",
            "wave8_great_northern_exact_riksarkivet_stenbock",
        ],
        [
            "wave8_great_northern_exact_clodfelter_warfare",
            "wave8_great_northern_exact_danish_general_staff_v4",
            "wave8_great_northern_exact_riksarkivet_stenbock",
        ],
        (
            "The Danish, Russian, and Saxon encirclement compelled Magnus "
            "Stenbock to capitulate his Swedish field army at Oldenswort. This "
            "contract ends with that army surrender; it is not the separate "
            "1713-1714 siege and capitulation of Tönning fortress."
        ),
        confidence=0.94,
    ),
    "hced-Stralsund1714-1715-1": _contract(
        "hced-Stralsund1714-1715-1",
        _canonical(
            "Siege of Stralsund (1715)",
            1715,
            1715,
            "12 July to 24 December 1715",
            date_precision="day_range",
            granularity="final_july_december_1715_siege_of_stralsund",
        ),
        [_DENMARK, _PRUSSIA, _SAXONY],
        [_SWEDEN],
        [
            "wave8_great_northern_exact_ghdi_stralsund",
            "wave8_great_northern_exact_landers_field_forge",
            "wave8_great_northern_exact_rct_stralsund",
        ],
        [
            "wave8_great_northern_exact_ghdi_stralsund",
            "wave8_great_northern_exact_landers_field_forge",
            "wave8_great_northern_exact_rct_stralsund",
        ],
        (
            "The reviewed unit is the final 1715 siege, in which Danish, "
            "Prussian, and Saxon forces compelled the Swedish garrison's "
            "surrender. The earlier 1711-1714 approaches and interruptions are "
            "not merged into this rated event."
        ),
        confidence=0.97,
        source_date_override=True,
        date_source_ids=[
            "wave8_great_northern_exact_ghdi_stralsund",
            "wave8_great_northern_exact_rct_stralsund",
        ],
    ),
}


WAVE8_GREAT_NORTHERN_EXACT_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS = frozenset(
    WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS
)
WAVE8_GREAT_NORTHERN_EXACT_RESERVED_IDS = (
    WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS
)


WAVE8_GREAT_NORTHERN_EXACT_LOCATION_REVIEWS: dict[str, dict[str, Any]] = {
    "hced-Gadebusch1712-1": {
        "point_disposition": "withhold_unverified_source_point",
        "country_disposition": "retain_germany",
        "reason": (
            "The sources establish the Wakenstädt battlefield near Gadebusch, "
            "but do not independently validate HCED's exact coordinate."
        ),
        "evidence_refs": [
            "wave8_great_northern_exact_danish_general_staff_v4",
            "wave8_great_northern_exact_svmm_gadebusch",
        ],
    },
    "hced-Tonning1713-1": {
        "point_disposition": "withhold_wrong_event_locality_point",
        "country_disposition": "retain_germany",
        "reason": (
            "HCED's point is Tönning, while the rated event is the field army's "
            "capitulation negotiated and signed at Oldenswort. A fortress or "
            "town point must not be presented as the capitulation site."
        ),
        "evidence_refs": [
            "wave8_great_northern_exact_danish_general_staff_v4",
            "wave8_great_northern_exact_riksarkivet_stenbock",
        ],
    },
    "hced-Stralsund1714-1715-1": {
        "point_disposition": "retain_source_city_siege_point",
        "country_disposition": "retain_germany",
        "reason": (
            "The reviewed event is the siege of Stralsund itself, and the source "
            "point is retained as a city-siege reference rather than a claim for "
            "one trench, battery, or surrender location."
        ),
        "evidence_refs": [
            "wave8_great_northern_exact_ghdi_stralsund",
            "wave8_great_northern_exact_rct_stralsund",
        ],
    },
}
WAVE8_GREAT_NORTHERN_EXACT_POINT_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Gadebusch1712-1", "hced-Tonning1713-1"}
)
WAVE8_GREAT_NORTHERN_EXACT_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = (
    frozenset()
)
WAVE8_GREAT_NORTHERN_EXACT_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_GREAT_NORTHERN_EXACT_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_GREAT_NORTHERN_EXACT_COUNTRY_QUARANTINE_ADDITIONS,
}


_EXPECTED_SIDES: dict[str, tuple[list[str], list[str]]] = {
    "hced-Gadebusch1712-1": (
        [_SWEDEN],
        sorted([_DENMARK, _SAXONY]),
    ),
    "hced-Tonning1713-1": (
        sorted([_DENMARK, _RUSSIA, _SAXONY]),
        [_SWEDEN],
    ),
    "hced-Stralsund1714-1715-1": (
        sorted([_DENMARK, _PRUSSIA, _SAXONY]),
        [_SWEDEN],
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS,
        "entities": WAVE8_GREAT_NORTHERN_EXACT_ENTITIES,
        "existing_entity_pins": _EXISTING_ENTITY_PINS,
        "holds": WAVE8_GREAT_NORTHERN_EXACT_HOLDS,
        "location_reviews": WAVE8_GREAT_NORTHERN_EXACT_LOCATION_REVIEWS,
        "row_hashes": WAVE8_GREAT_NORTHERN_EXACT_ROW_HASHES,
        "sources": WAVE8_GREAT_NORTHERN_EXACT_SOURCES,
    }


def wave8_great_northern_exact_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_GREAT_NORTHERN_EXACT_FINAL_AUDIT_SIGNATURE = (
    "fe532d1e548f2f52605070ef457ed05475241f274383ab0cd9064146b7fa484f"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_GREAT_NORTHERN_EXACT_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if WAVE8_GREAT_NORTHERN_EXACT_ENTITIES:
        raise ValueError(f"{_LANE_NAME} must not install entities or aliases")
    if (
        WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS
        != WAVE8_GREAT_NORTHERN_EXACT_EXPECTED_CANDIDATE_IDS
        or WAVE8_GREAT_NORTHERN_EXACT_RESERVED_IDS
        != WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS
        or WAVE8_GREAT_NORTHERN_EXACT_HOLDS
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if "hced-Gotland1563-1" in WAVE8_GREAT_NORTHERN_EXACT_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} must leave Gotland 1563 staged")
    if WAVE8_GREAT_NORTHERN_EXACT_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    if WAVE8_GREAT_NORTHERN_EXACT_POINT_QUARANTINE_ADDITIONS != {
        "hced-Gadebusch1712-1",
        "hced-Tonning1713-1",
    }:
        raise ValueError(f"{_LANE_NAME} point disposition drift")
    if (
        set(WAVE8_GREAT_NORTHERN_EXACT_LOCATION_REVIEWS)
        != WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location review inventory drift")

    used_sources: set[str] = set()
    used_actors: set[str] = set()
    for candidate_id, contract in WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS.items():
        if contract["disposition"] != "promote" or contract["result_type"] != "win":
            raise ValueError(f"{_LANE_NAME} disposition drift: {candidate_id}")
        if contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} winner polarity drift: {candidate_id}")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} outcome override drift: {candidate_id}")
        if contract["event_type"] != "engagement":
            raise ValueError(f"{_LANE_NAME} event type drift: {candidate_id}")
        sides = (
            list(map(str, contract["side_1_entity_ids"])),
            list(map(str, contract["side_2_entity_ids"])),
        )
        if sides != _EXPECTED_SIDES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} coalition drift: {candidate_id}")
        actors = {*sides[0], *sides[1]}
        if not actors <= WAVE8_GREAT_NORTHERN_EXACT_REQUIRED_EXISTING_ENTITY_IDS:
            raise ValueError(f"{_LANE_NAME} unknown exact actor: {candidate_id}")
        used_actors.update(actors)

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence order drift: {candidate_id}")
        if not set(outcomes) <= set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} source-family drift: {candidate_id}")
        used_sources.update(evidence)

    if used_actors != WAVE8_GREAT_NORTHERN_EXACT_REQUIRED_EXISTING_ENTITY_IDS:
        raise ValueError(f"{_LANE_NAME} existing actor inventory is not exact")
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    stralsund = WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS[
        "hced-Stralsund1714-1715-1"
    ]
    if stralsund.get("source_date_override") is not True or stralsund.get(
        "date_source_ids"
    ) != sorted(
        {
            "wave8_great_northern_exact_ghdi_stralsund",
            "wave8_great_northern_exact_rct_stralsund",
        }
    ):
        raise ValueError(f"{_LANE_NAME} Stralsund date-boundary drift")
    if any(
        contract.get("source_date_override")
        for candidate_id, contract in WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS.items()
        if candidate_id != "hced-Stralsund1714-1715-1"
    ):
        raise ValueError(f"{_LANE_NAME} unexpected date override")
    if (
        wave8_great_northern_exact_audit_signature()
        != WAVE8_GREAT_NORTHERN_EXACT_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_great_northern_exact_existing_entities(
    release_entities: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    for entity_id, expected in _EXISTING_ENTITY_PINS.items():
        entity = release_entities.get(entity_id)
        if entity is None:
            raise ValueError(f"{_LANE_NAME} missing existing identity: {entity_id}")
        actual = {key: entity.get(key) for key in expected}
        if actual != expected:
            raise ValueError(
                f"{_LANE_NAME} existing identity drift: {entity_id}: {actual}"
            )
    return {"required_existing_entities": len(_EXISTING_ENTITY_PINS)}


_EXPECTED_RAW_SIDES: dict[str, tuple[str, str, str, str]] = {
    "hced-Gadebusch1712-1": (
        "Sweden",
        "Denmark, Saxony",
        "Sweden",
        "Denmark, Saxony",
    ),
    "hced-Tonning1713-1": (
        "Denmark, Saxony",
        "Sweden",
        "Denmark, Saxony",
        "Sweden",
    ),
    "hced-Stralsund1714-1715-1": (
        "Denmark, German states",
        "Sweden",
        "Denmark, German states",
        "Sweden",
    ),
}


def validate_wave8_great_northern_exact_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            indexed.setdefault(candidate_id, []).append(row)
    for candidate_id, expected_hash in WAVE8_GREAT_NORTHERN_EXACT_ROW_HASHES.items():
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one locked row for {candidate_id}, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        actual_sides = (
            str(row.get("side_1_raw")),
            str(row.get("side_2_raw")),
            str(row.get("winner_raw")),
            str(row.get("loser_raw")),
        )
        if actual_sides != _EXPECTED_RAW_SIDES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} source polarity changed: {candidate_id}")
        if (
            row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("do_not_rate_automatically") is not True
        ):
            raise ValueError(f"{_LANE_NAME} competitive review guard changed: {candidate_id}")
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS,
        WAVE8_GREAT_NORTHERN_EXACT_HOLDS,
        lane_name=_LANE_NAME,
    )


def _row_year_range(row: Mapping[str, Any]) -> tuple[int, int] | None:
    low = row.get("year_low", row.get("year", row.get("year_best", row.get("batyear"))))
    high = row.get("year_high", row.get("end_year", low))
    try:
        return int(low), int(high)
    except (TypeError, ValueError):
        return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Gadebusch1712-1": {
        "Battle of Gadebusch",
        "Gadebusch",
        "Battle of Wakenstädt",
        "Wakenstädt",
        "Wakenstadt",
    },
    "hced-Tonning1713-1": {
        "Capitulation at Oldenswort",
        "Oldenswort",
        "Tönning",
        "Tonning",
        "Capitulation of Tönning",
    },
    "hced-Stralsund1714-1715-1": {
        "Siege of Stralsund (1715)",
        "Siege of Stralsund",
        "Stralsund",
    },
}
_DUPLICATE_KEYS = frozenset(
    (
        int(WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS[candidate_id]["canonical_event"]["year_low"]),
        normalize_label(alias),
    )
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    years = _row_year_range(row)
    if years is None:
        return False
    low, high = years
    return any(
        low <= year <= high and name == candidate_name
        for year, candidate_name in _DUPLICATE_KEYS
        for name in _row_names(row)
    )


def validate_wave8_great_northern_exact_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_great_northern_exact_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_GREAT_NORTHERN_EXACT_RESERVED_IDS
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
        not in WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS
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


def install_wave8_great_northern_exact_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    validate_wave8_great_northern_exact_existing_entities(release_entities)
    install_exact_entities(
        release_entities,
        WAVE8_GREAT_NORTHERN_EXACT_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_great_northern_exact_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_GREAT_NORTHERN_EXACT_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_reviews(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_GREAT_NORTHERN_EXACT_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_GREAT_NORTHERN_EXACT_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_great_northern_exact_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_great_northern_exact_queue_contracts(hced_rows)
    validate_wave8_great_northern_exact_existing_entities(release_entities)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    for event in events:
        contract = WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS[
            str(event["hced_candidate_id"])
        ]
        event["event_type"] = str(contract["event_type"])
    _apply_location_reviews(events)
    return events


def wave8_great_northern_exact_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS.values()
            ).items()
        )
    )


def wave8_great_northern_exact_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": 0,
        "new_entities": 0,
        "new_sources": len(WAVE8_GREAT_NORTHERN_EXACT_SOURCES),
        "newly_rated_events": len(WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_GREAT_NORTHERN_EXACT_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_GREAT_NORTHERN_EXACT_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_great_northern_exact_location_quarantine_additions() -> dict[str, int]:
    _validate_static()
    return {
        "country": len(WAVE8_GREAT_NORTHERN_EXACT_COUNTRY_QUARANTINE_ADDITIONS),
        "point": len(WAVE8_GREAT_NORTHERN_EXACT_POINT_QUARANTINE_ADDITIONS),
    }


def wave8_great_northern_exact_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_great_northern_exact_counts(),
        "cohorts": wave8_great_northern_exact_cohort_counts(),
        "final_audit_signature": WAVE8_GREAT_NORTHERN_EXACT_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS),
        "required_existing_entity_ids": sorted(
            WAVE8_GREAT_NORTHERN_EXACT_REQUIRED_EXISTING_ENTITY_IDS
        ),
    }


_validate_static()
