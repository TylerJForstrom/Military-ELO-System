"""Fail-closed exact audit of HCED's two unresolved ``Alemanns`` rows.

The source label is not made into an alias.  Each reviewed contest receives
its own Roman and Alemannic formation: Julian's victory at Argentoratum in
August 357 and the victory of Nannienus and Mallobaudes over Priarius's
Lentienses at Argentaria in June 378.  The latter is not the Strasbourg
battle, despite HCED reusing ``Argentoratum`` and the Strasbourg coordinate.

The corresponding Wikidata records have no winner and remain discovery-only.
The IWBD Strasbourg record is the distinct 1870 siege and supplies no evidence
for either ancient result.  Unknown is never converted to a draw.
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
    "WAVE8_ALEMANNS_CONTRACT_IDS",
    "WAVE8_ALEMANNS_CONTRACTS",
    "WAVE8_ALEMANNS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ALEMANNS_DISCOVERY_EXPECTED",
    "WAVE8_ALEMANNS_DISCOVERY_ROW_HASHES",
    "WAVE8_ALEMANNS_ENTITIES",
    "WAVE8_ALEMANNS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ALEMANNS_FUNNEL_AUDIT",
    "WAVE8_ALEMANNS_HOLDS",
    "WAVE8_ALEMANNS_INTEGRATION_DISPOSITIONS",
    "WAVE8_ALEMANNS_IWBD_DISPOSITIONS",
    "WAVE8_ALEMANNS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_ALEMANNS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ALEMANNS_REQUIRED_EXISTING_SOURCES",
    "WAVE8_ALEMANNS_RESERVED_IDS",
    "WAVE8_ALEMANNS_ROW_HASHES",
    "WAVE8_ALEMANNS_SOURCES",
    "WAVE8_ALEMANNS_TERMINAL_EXCLUSIONS",
    "install_wave8_alemanns_entities",
    "install_wave8_alemanns_sources",
    "promote_wave8_alemanns_contracts",
    "validate_wave8_alemanns_discovery_dispositions",
    "validate_wave8_alemanns_funnel",
    "validate_wave8_alemanns_integration_dispositions",
    "validate_wave8_alemanns_iwbd_dispositions",
    "validate_wave8_alemanns_queue_contracts",
    "validate_wave8_alemanns_reused_sources",
    "wave8_alemanns_audit_signature",
    "wave8_alemanns_cohort_counts",
    "wave8_alemanns_counts",
    "wave8_alemanns_metadata",
)


_LANE_NAME = "Wave 8 exact Alemanns formation audit"
_MODULE_OWNER = "military_elo.promotion.wave8_alemanns"
_EVENT_ID_PREFIX = "hced_wave8_alemanns_"
_EXACT_LABEL = "alemanns"

_JULIAN_ROMANS = "julian_roman_field_army_argentoratum_357"
_CHNODOMARIUS_HOST = "chnodomarius_alemannic_confederate_host_argentoratum_357"
_GRATIAN_GENERALS = "nannienus_mallobaudes_roman_field_army_argentaria_378"
_PRIARIUS_LENTIENSES = "priarius_lentiensian_alemannic_host_argentaria_378"


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
            "curated_reference_pending_claim_level_outcome_locator",
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    }


# Exactly three new records.  Book 16 and Drinkwater are deliberately reused
# from wave8_alemanni and are pinned separately below rather than duplicated.
WAVE8_ALEMANNS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_alemanns_ammianus_book_31",
        "Ammianus Marcellinus, Roman History, Book 31",
        "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ammian/31%2A.html",
        "LacusCurtius; Loeb Classical Library translation",
        "translated_primary_source",
        "ammianus_roman_history_loeb",
    ),
    _source(
        "wave8_alemanns_drijvers_teitler_378_chronology",
        (
            "Gratian's Campaign against the Lentienses and his Journey to "
            "Thrace (Ammianus Marcellinus 31.10 & 31.11.6): A New Chronology"
        ),
        "https://doi.org/10.25162/historia-2019-0006",
        (
            "Jan Willem Drijvers and Hans Carel Teitler / Historia: "
            "Zeitschrift fuer Alte Geschichte 68 (2019)"
        ),
        "peer_reviewed_ancient_history_article",
        "drijvers_teitler_gratian_lentienses_2019",
    ),
    _source(
        "wave8_alemanns_ross_strasbourg",
        (
            "Strasbourg: Legitimizing Julian, in Ammianus' Julian: "
            "Narrative and Genre in the Res Gestae"
        ),
        "https://doi.org/10.1093/acprof:oso/9780198784951.003.0004",
        "Oxford University Press; Alan J. Ross",
        "scholarly_monograph_chapter",
        "ross_ammianus_julian_2016",
    ),
)

_NEW_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_ALEMANNS_SOURCES
}


WAVE8_ALEMANNS_REQUIRED_EXISTING_SOURCES: dict[str, dict[str, Any]] = {
    "wave8_alemanni_ammianus_book_16": {
        "title": "Ammianus Marcellinus, Roman History, Book 16",
        "url": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ammian/16%2A.html",
        "publisher": "LacusCurtius; Loeb Classical Library translation",
        "source_type": "translated_primary_source",
        "source_family_id": "ammianus_roman_history_loeb",
    },
    "wave8_alemanni_drinkwater_alamanni_rome": {
        "title": "The Alamanni and Rome 213-496: Caracalla to Clovis",
        "url": "https://doi.org/10.1093/acprof:oso/9780199295685.001.0001",
        "publisher": "Oxford University Press; John F. Drinkwater",
        "source_type": "scholarly_monograph",
        "source_family_id": "drinkwater_alamanni_and_rome_2007",
    },
}

_SOURCE_FAMILY_BY_ID = {
    **{
        source_id: str(source["source_family_id"])
        for source_id, source in WAVE8_ALEMANNS_REQUIRED_EXISTING_SOURCES.items()
    },
    **{
        source_id: str(source["source_family_id"])
        for source_id, source in _NEW_SOURCE_BY_ID.items()
    },
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    source_ids: Iterable[str],
    note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            note
            + " This event-bounded identity has no aliases, predecessor bridge, "
            "or rating inheritance outside the fingerprinted contest."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_ALEMANNS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _JULIAN_ROMANS,
        "Julian's Roman field army at Argentoratum (357)",
        "event_bounded_field_army",
        357,
        "Roman Gaul near Argentoratum",
        [
            "wave8_alemanni_ammianus_book_16",
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanns_ross_strasbourg",
        ],
        (
            "Bounded to Caesar Julian's Roman field force in the August 357 "
            "battle at Argentoratum."
        ),
    ),
    _entity(
        _CHNODOMARIUS_HOST,
        "Chnodomarius's Alemannic confederate host at Argentoratum (357)",
        "event_bounded_confederate_host",
        357,
        "Roman Gaul near Argentoratum",
        [
            "wave8_alemanni_ammianus_book_16",
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanns_ross_strasbourg",
        ],
        (
            "Bounded to the Alemannic coalition led by Chnodomarius and defeated "
            "by Julian at Argentoratum."
        ),
    ),
    _entity(
        _GRATIAN_GENERALS,
        "Nannienus and Mallobaudes's Roman field army at Argentaria (378)",
        "event_bounded_field_army",
        378,
        "Alsace near Argentaria",
        [
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanns_ammianus_book_31",
            "wave8_alemanns_drijvers_teitler_378_chronology",
        ],
        (
            "Bounded to the Western Roman army commanded by Nannienus and "
            "Mallobaudes in the June 378 battle at Argentaria."
        ),
    ),
    _entity(
        _PRIARIUS_LENTIENSES,
        "Priarius's Lentiensian Alemannic host at Argentaria (378)",
        "event_bounded_raiding_host",
        378,
        "Alsace near Argentaria",
        [
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanns_ammianus_book_31",
            "wave8_alemanns_drijvers_teitler_378_chronology",
        ],
        (
            "Bounded to Priarius's Lentiensian force defeated at Argentaria; it "
            "is not a timeless identity for every Alemannic group."
        ),
    ),
)


WAVE8_ALEMANNS_ROW_HASHES: dict[str, str] = {
    "hced-Argentoratum357-1": (
        "de208a00966d2d4cb5ef2cdab6a39df2edbe0f46d0494325b2c3e1f2e4d749b4"
    ),
    "hced-Argentoratum378-1": (
        "1d7ffd2c7857abe013030f1a05500d31efef0eb408c53dffdb73d2743b50b596"
    ),
}


WAVE8_ALEMANNS_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "fcdc555ad21a1ae808fd222cb2e258b4439ec4939a282fb221fe6d4f96a64e05"
    ),
    "events_touched": 2,
    "label": _EXACT_LABEL,
    "sole_blocker_events": 2,
    "unresolved_side_attempts": 2,
    "zero_time_valid_candidates": 2,
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    date_precision: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": "single_tactical_battle",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    winner_id: str,
    loser_id: str,
    evidence_refs: Iterable[str],
    date_source_ids: Iterable[str],
    audit_note: str,
    historical_review: Mapping[str, Any],
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    dates = sorted(set(map(str, date_source_ids)))
    return {
        "raw_row_sha256": WAVE8_ALEMANNS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "roman_alemannic_contests_357_378",
        "side_1_entity_ids": [winner_id],
        "side_2_entity_ids": [loser_id],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate_limited",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": evidence,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in evidence}
        ),
        "date_source_ids": dates,
        "source_date_override": False,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_event_bounded_historical_forces",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
        "historical_review": dict(historical_review),
    }


WAVE8_ALEMANNS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Argentoratum357-1": _contract(
        "hced-Argentoratum357-1",
        _canonical(
            "Battle of Argentoratum (Strasbourg)",
            357,
            "August 357",
            "month",
        ),
        _JULIAN_ROMANS,
        _CHNODOMARIUS_HOST,
        [
            "wave8_alemanni_ammianus_book_16",
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanns_ross_strasbourg",
        ],
        [
            "wave8_alemanni_ammianus_book_16",
            "wave8_alemanns_ross_strasbourg",
        ],
        (
            "Ammianus and modern source-critical scholarship identify Julian's "
            "complete tactical victory over Chnodomarius's Alemannic host at "
            "Argentoratum in August 357. No wider campaign result is inferred."
        ),
        {
            "date_disposition": "month_attested_august_357",
            "outcome": "roman_tactical_victory",
            "source_name_disposition": "Argentoratum and Strasbourg name one 357 battle",
        },
        confidence=0.97,
    ),
    "hced-Argentoratum378-1": _contract(
        "hced-Argentoratum378-1",
        _canonical(
            "Battle of Argentaria",
            378,
            "mid-June 378",
            "month_uncertain",
        ),
        _GRATIAN_GENERALS,
        _PRIARIUS_LENTIENSES,
        [
            "wave8_alemanni_drinkwater_alamanni_rome",
            "wave8_alemanns_ammianus_book_31",
            "wave8_alemanns_drijvers_teitler_378_chronology",
        ],
        [
            "wave8_alemanns_ammianus_book_31",
            "wave8_alemanns_drijvers_teitler_378_chronology",
        ],
        (
            "Ammianus reports that Nannienus and Mallobaudes defeated the "
            "Lentienses at Argentaria and that Priarius was killed. The reviewed "
            "chronology places the battle around mid-June 378; HCED's reused "
            "Argentoratum/Strasbourg label and point are not retained."
        ),
        {
            "date_disposition": "mid_june_inferred_from_reviewed_june_july_chronology",
            "outcome": "roman_tactical_victory",
            "source_name_disposition": "corrected_from_argentoratum_to_argentaria",
        },
        confidence=0.96,
    ),
}


WAVE8_ALEMANNS_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_ALEMANNS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_ALEMANNS_CONTRACT_IDS = frozenset(WAVE8_ALEMANNS_CONTRACTS)
WAVE8_ALEMANNS_RESERVED_IDS = WAVE8_ALEMANNS_CONTRACT_IDS
WAVE8_ALEMANNS_POINT_QUARANTINE_ADDITIONS = WAVE8_ALEMANNS_CONTRACT_IDS
WAVE8_ALEMANNS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_ALEMANNS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Argentoratum357-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The sources locate the battle at or near ancient Argentoratum but "
            "do not independently verify HCED's exact modern Strasbourg point."
        ),
        "evidence_refs": WAVE8_ALEMANNS_CONTRACTS[
            "hced-Argentoratum357-1"
        ]["evidence_refs"],
    },
    "hced-Argentoratum378-1": {
        "actions": ["withhold_point"],
        "reason": (
            "HCED copied the Strasbourg point into this row, but the reviewed "
            "battle is Argentaria/Argentovaria in the Colmar-Biesheim area."
        ),
        "evidence_refs": WAVE8_ALEMANNS_CONTRACTS[
            "hced-Argentoratum378-1"
        ]["evidence_refs"],
    },
}


WAVE8_ALEMANNS_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q1367199": "09087135a5f51c2c73178e79a6da9f52e1d963d22d159fc9d60762da2fa634b2",
    "Q767605": "8b89c3b2d273fac8958783f838e19d6824351d23595f321506d3a0d77fd73637",
}

WAVE8_ALEMANNS_DISCOVERY_EXPECTED: dict[str, dict[str, Any]] = {
    "Q1367199": {
        "date": "0357-08-01T00:00:00Z",
        "hced_candidate_id": "hced-Argentoratum357-1",
        "kind": "engagement",
        "name": "Battle of Strasbourg",
        "participant_labels": [
            "Alamanni",
            "Chnodomarius",
            "Julian",
            "Western Roman Empire",
        ],
        "relationship": "probable_duplicate_discovery_record",
    },
    "Q767605": {
        "date": "0378-05-01T00:00:00Z",
        "hced_candidate_id": "hced-Argentoratum378-1",
        "kind": "engagement",
        "name": "Battle of Argentovaria",
        "participant_labels": ["Lentienses", "Western Roman Empire"],
        "relationship": "probable_duplicate_discovery_record_with_month_conflict",
    },
}

WAVE8_ALEMANNS_IWBD_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-58-20-217": {
        "raw_row_sha256": (
            "37af19e972d19da72ac1f4f652c90c6d7246fb8f41b7fbdaabbb58b033cfbc21"
        ),
        "disposition": "non_authoritative_distinct_staged_record",
        "relationship": "distinct_1870_siege_sharing_only_the_strasbourg_name",
        "outcome_disposition": "not_evidence_for_ancient_contracts",
    }
}

WAVE8_ALEMANNS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        candidate_id: {
            "source_dataset": "wikidata-battles",
            "disposition": "discovery_only_probable_duplicate",
            "relationship": expected["relationship"],
            "hced_candidate_id": expected["hced_candidate_id"],
            "outcome_disposition": "unknown_never_draw",
            "rating_authority": False,
        }
        for candidate_id, expected in sorted(WAVE8_ALEMANNS_DISCOVERY_EXPECTED.items())
    },
    **{
        candidate_id: {
            "source_dataset": "iwbd",
            "disposition": disposition["disposition"],
            "relationship": disposition["relationship"],
            "hced_candidate_id": None,
            "outcome_disposition": disposition["outcome_disposition"],
            "rating_authority": False,
        }
        for candidate_id, disposition in sorted(WAVE8_ALEMANNS_IWBD_DISPOSITIONS.items())
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_ALEMANNS_CONTRACTS,
        "discovery_expected": WAVE8_ALEMANNS_DISCOVERY_EXPECTED,
        "discovery_hashes": WAVE8_ALEMANNS_DISCOVERY_ROW_HASHES,
        "entities": WAVE8_ALEMANNS_ENTITIES,
        "funnel": WAVE8_ALEMANNS_FUNNEL_AUDIT,
        "holds": WAVE8_ALEMANNS_HOLDS,
        "integration_dispositions": WAVE8_ALEMANNS_INTEGRATION_DISPOSITIONS,
        "iwbd_dispositions": WAVE8_ALEMANNS_IWBD_DISPOSITIONS,
        "location_reasons": WAVE8_ALEMANNS_LOCATION_QUARANTINE_REASONS,
        "reused_sources": WAVE8_ALEMANNS_REQUIRED_EXISTING_SOURCES,
        "row_hashes": WAVE8_ALEMANNS_ROW_HASHES,
        "sources": WAVE8_ALEMANNS_SOURCES,
        "terminal_exclusions": WAVE8_ALEMANNS_TERMINAL_EXCLUSIONS,
    }


def wave8_alemanns_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_ALEMANNS_FINAL_AUDIT_SIGNATURE = (
    "3d4bd6bf2bbc387b2b44c20d9b85a7ab306375b2a747b745f90bfd4717c03696"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_ALEMANNS_CONTRACTS) != 2
        or WAVE8_ALEMANNS_HOLDS
        or WAVE8_ALEMANNS_TERMINAL_EXCLUSIONS
        or WAVE8_ALEMANNS_RESERVED_IDS != set(WAVE8_ALEMANNS_ROW_HASHES)
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (
        WAVE8_ALEMANNS_POINT_QUARANTINE_ADDITIONS
        != WAVE8_ALEMANNS_CONTRACT_IDS
        or WAVE8_ALEMANNS_COUNTRY_QUARANTINE_ADDITIONS
        or set(WAVE8_ALEMANNS_LOCATION_QUARANTINE_REASONS)
        != WAVE8_ALEMANNS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location contract changed")

    new_source_ids = set(_NEW_SOURCE_BY_ID)
    reused_source_ids = set(WAVE8_ALEMANNS_REQUIRED_EXISTING_SOURCES)
    if (
        len(new_source_ids) != 3
        or len(reused_source_ids) != 2
        or new_source_ids & reused_source_ids
    ):
        raise ValueError(f"{_LANE_NAME} new/reused source inventory changed")
    if any(
        not str(source["url"]).startswith("https://")
        or not _is_sorted_unique(source["evidence_roles"])
        for source in WAVE8_ALEMANNS_SOURCES
    ):
        raise ValueError(f"{_LANE_NAME} source fixture changed")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_ALEMANNS_ENTITIES}
    if len(entity_by_id) != 4:
        raise ValueError(f"{_LANE_NAME} exact identity inventory changed")
    allowed_sources = new_source_ids | reused_source_ids
    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for entity in WAVE8_ALEMANNS_ENTITIES:
        if (
            entity["aliases"]
            or entity["predecessors"]
            or int(entity["start_year"]) != int(entity["end_year"])
        ):
            raise ValueError(f"{_LANE_NAME} opened an alias or continuity window")
        refs = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(refs) or not set(refs) <= allowed_sources:
            raise ValueError(f"{_LANE_NAME} entity evidence changed")
        used_sources.update(refs)

    for candidate_id, contract in WAVE8_ALEMANNS_CONTRACTS.items():
        if (
            contract["raw_row_sha256"] != WAVE8_ALEMANNS_ROW_HASHES[candidate_id]
            or contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_date_override"]
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome contract changed: {candidate_id}")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if (
            len(side_1) != 1
            or len(side_2) != 1
            or set(side_1) & set(side_2)
            or not set(side_1 + side_2) <= set(entity_by_id)
        ):
            raise ValueError(f"{_LANE_NAME} exact actor contract changed")
        used_entities.update(side_1 + side_2)
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        dates = list(map(str, contract["date_source_ids"]))
        expected_families = sorted({_SOURCE_FAMILY_BY_ID[item] for item in outcomes})
        if (
            not _is_sorted_unique(evidence)
            or outcomes != evidence
            or not _is_sorted_unique(dates)
            or not set(dates) <= set(evidence)
            or not set(evidence) <= allowed_sources
            or contract["outcome_source_family_ids"] != expected_families
            or len(expected_families) < 3
        ):
            raise ValueError(f"{_LANE_NAME} evidence closure changed: {candidate_id}")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id) or used_sources != allowed_sources:
        raise ValueError(f"{_LANE_NAME} fixture consumption changed")
    first = WAVE8_ALEMANNS_CONTRACTS["hced-Argentoratum357-1"]["canonical_event"]
    second = WAVE8_ALEMANNS_CONTRACTS["hced-Argentoratum378-1"]["canonical_event"]
    if (
        (first["name"], first["date_text"], first["date_precision"])
        != ("Battle of Argentoratum (Strasbourg)", "August 357", "month")
        or (second["name"], second["date_text"], second["date_precision"])
        != ("Battle of Argentaria", "mid-June 378", "month_uncertain")
        or "strasbourg" in normalize_label(second["name"])
    ):
        raise ValueError(f"{_LANE_NAME} canonical name/date changed")

    if set(WAVE8_ALEMANNS_DISCOVERY_EXPECTED) != set(
        WAVE8_ALEMANNS_DISCOVERY_ROW_HASHES
    ) or set(WAVE8_ALEMANNS_IWBD_DISPOSITIONS) != {"iwbd-58-20-217"}:
        raise ValueError(f"{_LANE_NAME} staged-input inventory changed")
    if set(WAVE8_ALEMANNS_INTEGRATION_DISPOSITIONS) != {
        *WAVE8_ALEMANNS_DISCOVERY_EXPECTED,
        *WAVE8_ALEMANNS_IWBD_DISPOSITIONS,
    } or any(
        disposition["rating_authority"] is not False
        for disposition in WAVE8_ALEMANNS_INTEGRATION_DISPOSITIONS.values()
    ):
        raise ValueError(f"{_LANE_NAME} non-authority guard changed")
    if (
        WAVE8_ALEMANNS_FINAL_AUDIT_SIGNATURE != "__PENDING__"
        and wave8_alemanns_audit_signature()
        != WAVE8_ALEMANNS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_alemanns_queue_contracts(
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
    if exact_ids != WAVE8_ALEMANNS_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed: {sorted(exact_ids)}")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_ALEMANNS_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            row.get("winner_loser_complete") is not True
            or row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
            or row.get("massacre_raw") != "No"
            or row.get("do_not_rate_automatically") is not True
        ):
            raise ValueError(f"{_LANE_NAME} source outcome guard changed: {candidate_id}")
    validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ALEMANNS_CONTRACTS,
        WAVE8_ALEMANNS_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        "exact_label_rows": len(exact),
        "holds": 0,
        "promotion_contracts": len(WAVE8_ALEMANNS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_ALEMANNS_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def validate_wave8_alemanns_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    records = [
        row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL
    ]
    if len(records) != 1:
        raise ValueError(f"{_LANE_NAME} expected one historical funnel label")
    record = records[0]
    actual = {
        "candidate_ids": list(map(str, record.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(record.get("event_candidate_id_sha256")),
        "events_touched": int(record.get("events_touched", -1)),
        "sole_blocker_events": int(record.get("sole_blocker_events", -1)),
        "unresolved_side_attempts": int(record.get("unresolved_side_attempts", -1)),
        "zero_time_valid_candidates": int(
            record.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
        ),
    }
    expected = {
        key: WAVE8_ALEMANNS_FUNNEL_AUDIT[key]
        for key in actual
    }
    if actual != expected:
        raise ValueError(f"{_LANE_NAME} historical funnel changed: {actual}")
    return {
        "events_touched": actual["events_touched"],
        "sole_blocker_events": actual["sole_blocker_events"],
        "zero_time_valid_candidates": actual["zero_time_valid_candidates"],
    }


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def validate_wave8_alemanns_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in WAVE8_ALEMANNS_DISCOVERY_ROW_HASHES.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} discovery row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}")
        expected = WAVE8_ALEMANNS_DISCOVERY_EXPECTED[candidate_id]
        labels = sorted(
            str(participant.get("label")) for participant in row.get("participants", [])
        )
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("winners") != []
            or row.get("name") != expected["name"]
            or row.get("date") != expected["date"]
            or row.get("kind") != expected["kind"]
            or labels != sorted(expected["participant_labels"])
        ):
            raise ValueError(
                f"{_LANE_NAME} discovery nonrating guard changed: {candidate_id}"
            )
    return {
        "discovery_nonrating_records": len(WAVE8_ALEMANNS_DISCOVERY_ROW_HASHES),
        "discovery_promotions": 0,
        "probable_duplicates": len(WAVE8_ALEMANNS_DISCOVERY_ROW_HASHES),
        "unknown_never_draw_rows": len(WAVE8_ALEMANNS_DISCOVERY_ROW_HASHES),
    }


def validate_wave8_alemanns_iwbd_dispositions(
    iwbd_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in iwbd_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, disposition in WAVE8_ALEMANNS_IWBD_DISPOSITIONS.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} IWBD row {candidate_id} expected once, found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} IWBD fingerprint changed: {candidate_id}")
        if (
            row.get("source") != "iwbd"
            or row.get("do_not_rate_automatically") is not True
            or row.get("name") != "Strasbourg"
            or row.get("start_date") != "1870-08-13"
            or row.get("end_date") != "1870-09-28"
            or row.get("winner_raw") != "Prussia"
        ):
            raise ValueError(f"{_LANE_NAME} IWBD distinct-event guard changed")
    return {
        "distinct_later_iwbd_records": len(WAVE8_ALEMANNS_IWBD_DISPOSITIONS),
        "iwbd_promotions": 0,
        "iwbd_rating_authorities": 0,
    }


def validate_wave8_alemanns_reused_sources(
    sources_by_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    for source_id, expected in WAVE8_ALEMANNS_REQUIRED_EXISTING_SOURCES.items():
        source = sources_by_id.get(source_id)
        if source is None:
            raise ValueError(f"{_LANE_NAME} missing reused source: {source_id}")
        actual = {key: source.get(key) for key in expected}
        if actual != expected:
            raise ValueError(f"{_LANE_NAME} reused source drift: {source_id}")
    return {"reused_sources": len(WAVE8_ALEMANNS_REQUIRED_EXISTING_SOURCES)}


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "batyear"):
        value = row.get(key)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                pass
    for key in ("date", "start_date"):
        value = str(row.get(key) or "")
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names: set[str] = set()
    for key in ("name", "battle_name", "batname", "event_name"):
        normalized = normalize_label(row.get(key))
        if normalized:
            names.add(normalized)
    for alias in row.get("aliases", []) or []:
        normalized = normalize_label(alias)
        if normalized:
            names.add(normalized)
    return names


_DUPLICATE_WINDOWS: tuple[tuple[int, frozenset[str]], ...] = (
    (
        357,
        frozenset(
            map(
                normalize_label,
                {
                    "Argentoratum",
                    "Battle of Argentoratum",
                    "Battle of Argentoratum (Strasbourg)",
                    "Battle of Strasbourg",
                },
            )
        ),
    ),
    (
        378,
        frozenset(
            map(
                normalize_label,
                {
                    "Argentaria",
                    "Argentovaria",
                    "Battle of Argentaria",
                    "Battle of Argentovaria",
                },
            )
        ),
    ),
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    names = _row_names(row)
    return year is not None and any(
        year == expected_year and bool(names & aliases)
        for expected_year, aliases in _DUPLICATE_WINDOWS
    )


def validate_wave8_alemanns_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    wikidata_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_alemanns_queue_contracts(hced_rows)
    discovery = validate_wave8_alemanns_discovery_dispositions(wikidata_rows)
    iwbd = validate_wave8_alemanns_iwbd_dispositions(iwbd_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_ALEMANNS_RESERVED_IDS
        and _is_probable_twin(row)
    )
    discovery_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in wikidata_rows
        if str(row.get("candidate_id")) not in WAVE8_ALEMANNS_DISCOVERY_EXPECTED
        and _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if str(row.get("candidate_id")) not in WAVE8_ALEMANNS_IWBD_DISPOSITIONS
        and _is_probable_twin(row)
    )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_ALEMANNS_CONTRACT_IDS
        and not str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
        and _is_probable_twin(event)
    )
    if hced_twins or discovery_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"discovery={discovery_twins}, iwbd={iwbd_twins}, "
            f"release={release_twins}"
        )
    return {
        "discovery_nonrating_records": discovery["discovery_nonrating_records"],
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwbd_distinct_nonrating_records": iwbd["distinct_later_iwbd_records"],
        "iwbd_probable_twins": 0,
        "wikidata_probable_twins": 0,
    }


def install_wave8_alemanns_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ALEMANNS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_alemanns_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    validate_wave8_alemanns_reused_sources(sources_by_id)
    install_exact_sources(
        sources_by_id,
        WAVE8_ALEMANNS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_ALEMANNS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_ALEMANNS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_alemanns_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_alemanns_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ALEMANNS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    for event in events:
        # HCED's shared Argentoratum spelling is wrong for the 378 battle, and
        # neither raw label is retained as a fallback alias.
        event["aliases"] = []
    _apply_location_quarantine(events)
    return events


def wave8_alemanns_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_ALEMANNS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_alemanns_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "discovery_nonrating_records": len(WAVE8_ALEMANNS_DISCOVERY_ROW_HASHES),
        "holds": 0,
        "integration_dispositions": len(WAVE8_ALEMANNS_INTEGRATION_DISPOSITIONS),
        "iwbd_nonrating_records": len(WAVE8_ALEMANNS_IWBD_DISPOSITIONS),
        "new_entities": len(WAVE8_ALEMANNS_ENTITIES),
        "new_sources": len(WAVE8_ALEMANNS_SOURCES),
        "newly_rated_events": len(WAVE8_ALEMANNS_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_ALEMANNS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_ALEMANNS_CONTRACTS),
        "reused_sources": len(WAVE8_ALEMANNS_REQUIRED_EXISTING_SOURCES),
        "reviewed_hced_rows": len(WAVE8_ALEMANNS_RESERVED_IDS),
        "terminal_exclusions": 0,
        "unknown_discovery_outcomes": len(WAVE8_ALEMANNS_DISCOVERY_ROW_HASHES),
    }


def wave8_alemanns_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_alemanns_counts(),
        "cohorts": wave8_alemanns_cohort_counts(),
        "final_audit_signature": WAVE8_ALEMANNS_FINAL_AUDIT_SIGNATURE,
        "hold_candidate_ids": [],
        "integration_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_ALEMANNS_INTEGRATION_DISPOSITIONS.items()
            )
        ],
        "promoted_candidate_ids": sorted(WAVE8_ALEMANNS_CONTRACT_IDS),
        "terminal_exclusion_candidate_ids": [],
    }


_validate_static()
