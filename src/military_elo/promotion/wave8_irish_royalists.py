"""Fail-closed exact audit of HCED's two ``Irish Royalists`` rows.

The shared label hides two different, short-lived forces.  Dungan's Hill is
bound to Michael Jones's Parliamentarian field army and Thomas Preston's
Confederate Leinster army, including its Redshank contingent.  Clonmel is
bound separately to Cromwell's New Model Army siege force and Hugh Dubh
O'Neill's Ormond-aligned Ulster garrison.  Every identity is event-bounded and
alias-free; no generic Irish Royalist, Parliamentarian, Commonwealth, English,
Irish, Confederate, or successor-state continuity is created.

Clonmel rates only the complete siege from 27 April through 18 May 1650: the
besiegers obtained the town after the garrison withdrew.  The nested 17 May
assault was a defender tactical victory and is explicitly excluded rather than
silently folded into the siege result or emitted as a second event.

The two matching Wikidata rows are discovery-only.  Both encode no winner, so
their outcomes remain unknown and are never converted to draws or allowed to
originate rated events.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    expected_exact_hced_win_participants,
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_IRISH_ROYALISTS_CONTRACT_IDS",
    "WAVE8_IRISH_ROYALISTS_CONTRACTS",
    "WAVE8_IRISH_ROYALISTS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_IRISH_ROYALISTS_DISCOVERY_EXPECTED",
    "WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES",
    "WAVE8_IRISH_ROYALISTS_DISCOVERY_TWINS",
    "WAVE8_IRISH_ROYALISTS_ENTITIES",
    "WAVE8_IRISH_ROYALISTS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_IRISH_ROYALISTS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_IRISH_ROYALISTS_FUNNEL_AUDIT",
    "WAVE8_IRISH_ROYALISTS_HOLDS",
    "WAVE8_IRISH_ROYALISTS_INTEGRATION_DISPOSITIONS",
    "WAVE8_IRISH_ROYALISTS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_IRISH_ROYALISTS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_IRISH_ROYALISTS_RESERVED_IDS",
    "WAVE8_IRISH_ROYALISTS_ROW_HASHES",
    "WAVE8_IRISH_ROYALISTS_SOURCES",
    "install_wave8_irish_royalists_entities",
    "install_wave8_irish_royalists_sources",
    "promote_wave8_irish_royalists_contracts",
    "validate_wave8_irish_royalists_current_artifact_state",
    "validate_wave8_irish_royalists_discovery_dispositions",
    "validate_wave8_irish_royalists_emissions",
    "validate_wave8_irish_royalists_funnel",
    "validate_wave8_irish_royalists_integration_dispositions",
    "validate_wave8_irish_royalists_queue_contracts",
    "wave8_irish_royalists_audit_signature",
    "wave8_irish_royalists_cohort_counts",
    "wave8_irish_royalists_counts",
    "wave8_irish_royalists_location_quarantine_additions",
    "wave8_irish_royalists_metadata",
)


_LANE_NAME = "Wave 8 exact Irish Royalists audit"
_MODULE_OWNER = "military_elo.promotion.wave8_irish_royalists"
_EVENT_ID_PREFIX = "hced_wave8_irish_royalists_"
_EXACT_LABEL = "irish royalists"
_COHORT = "irish_confederate_wars_exact_1647_1650"

_DUNGAN_PARLIAMENTARIANS = "dungans_hill_parliamentarian_field_army_1647"
_DUNGAN_CONFEDERATES = (
    "dungans_hill_confederate_leinster_redshank_force_1647"
)
_CLONMEL_NEW_MODEL = "clonmel_new_model_army_siege_force_1650"
_CLONMEL_GARRISON = "clonmel_ormond_aligned_ulster_garrison_1650"


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


WAVE8_IRISH_ROYALISTS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_irish_royalists_libris_dungans_hill_relation",
        (
            "An exact and full relation of the great victory obtained against "
            "the rebels at Dungons-Hill in Ireland, August 8, 1647"
        ),
        "https://libris.kb.se/bib/10747719",
        "LIBRIS, National Library of Sweden",
        "contemporary_parliamentary_print_catalogue_record",
        "commons_dungans_hill_relation_1647",
    ),
    _source(
        "wave8_irish_royalists_ucd_fitzpatrick_dungans_hill",
        "Thomas Fitzpatrick Papers: descriptive catalogue",
        (
            "https://www.ucd.ie/archives/t4media/"
            "la0012-fitzpatrick-thomas-descriptive-catalogue.pdf"
        ),
        "University College Dublin Archives",
        "university_archival_catalogue",
        "ucd_thomas_fitzpatrick_papers",
    ),
    _source(
        "wave8_irish_royalists_bcw_clonmel",
        "The Siege of Clonmel, 1650",
        (
            "https://bcw-project.org.uk/military/third-civil-war/"
            "cromwell-in-ireland/clonmel"
        ),
        "BCW Project",
        "curated_military_history_reference",
        "bcw_project_clonmel_1650",
    ),
    _source(
        "wave8_irish_royalists_history_ireland_hugh_dubh",
        "Hugh Dubh O'Neill—Cromwell's stoutest enemy",
        "https://historyireland.com/hugh-dubh-oneill-cromwells-stoutest-enemy/",
        "History Ireland",
        "scholarly_history_article",
        "history_ireland_hugh_dubh_oneill",
    ),
    _source(
        "wave8_irish_royalists_ucc_celt_parliamentary_proceedings",
        (
            "Proceedings of the forces in Ireland under Sir Hardress Waller "
            "and Lord-Deputy Ireton, 1650–1651"
        ),
        "https://celt.ucc.ie/document/E650001-001/",
        "University College Cork, Corpus of Electronic Texts",
        "edited_primary_source_transcription",
        "ucc_celt_parliamentary_proceedings_1650_1651",
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_IRISH_ROYALISTS_SOURCES
}

_DUNGAN_SOURCE_IDS = (
    "wave8_irish_royalists_libris_dungans_hill_relation",
    "wave8_irish_royalists_ucd_fitzpatrick_dungans_hill",
)
_CLONMEL_SOURCE_IDS = (
    "wave8_irish_royalists_bcw_clonmel",
    "wave8_irish_royalists_history_ireland_hugh_dubh",
    "wave8_irish_royalists_ucc_celt_parliamentary_proceedings",
)


def _entity(
    entity_id: str,
    name: str,
    year: int,
    kind: str,
    region: str,
    continuity_note: str,
    source_ids: Iterable[str],
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
        "continuity_note": continuity_note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_IRISH_ROYALISTS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _DUNGAN_PARLIAMENTARIANS,
        "Michael Jones's Parliamentarian field army at Dungan's Hill (1647)",
        1647,
        "event_bounded_field_army",
        "County Meath, Ireland",
        (
            "Bounded to Michael Jones's field army in the 8 August 1647 "
            "engagement. It receives no generic Parliamentarian, Commonwealth "
            "of England, Kingdom of England, Dublin-garrison, predecessor, or "
            "successor alias and inherits no Elo from any such identity."
        ),
        _DUNGAN_SOURCE_IDS,
    ),
    _entity(
        _DUNGAN_CONFEDERATES,
        (
            "Thomas Preston's Confederate Leinster–Redshank force at "
            "Dungan's Hill (1647)"
        ),
        1647,
        "event_bounded_coalition_field_force",
        "County Meath, Ireland",
        (
            "Bounded to Thomas Preston's Leinster Army and its Redshank "
            "contingent in the 8 August 1647 engagement. It receives no Irish "
            "Royalists, Irish Confederation, Catholic, Leinster, Highlander, "
            "ethnic, predecessor, or successor alias and inherits no Elo."
        ),
        _DUNGAN_SOURCE_IDS,
    ),
    _entity(
        _CLONMEL_NEW_MODEL,
        "New Model Army siege force at Clonmel (1650)",
        1650,
        "event_bounded_siege_force",
        "Clonmel, County Tipperary, Ireland",
        (
            "Bounded to Cromwell's besieging force during the 27 April–18 May "
            "1650 Clonmel operation. It receives no Parliamentarian, New Model "
            "Army, Commonwealth, England, predecessor, or successor alias and "
            "inherits no Elo from any broader identity."
        ),
        _CLONMEL_SOURCE_IDS,
    ),
    _entity(
        _CLONMEL_GARRISON,
        "Hugh Dubh O'Neill's Ormond-aligned Ulster garrison at Clonmel (1650)",
        1650,
        "event_bounded_garrison",
        "Clonmel, County Tipperary, Ireland",
        (
            "Bounded to Hugh Dubh O'Neill's Ulster force in Clonmel during the "
            "27 April–18 May 1650 siege under the Ormond alliance. It receives "
            "no Irish Royalists, Ulster Army, Confederation, Ireland, Catholic, "
            "predecessor, or successor alias and inherits no Elo."
        ),
        _CLONMEL_SOURCE_IDS,
    ),
)

_ENTITY_BY_ID = {
    str(entity["id"]): entity for entity in WAVE8_IRISH_ROYALISTS_ENTITIES
}


WAVE8_IRISH_ROYALISTS_ROW_HASHES: dict[str, str] = {
    "hced-Clonmel1650-1": (
        "9ef0c7f42df58a29f9081dfb5cee76b5af19b0edfa885a24f64c13639db1540d"
    ),
    "hced-Dungan Hill1647-1": (
        "774169d7d2da48902968f03a05c2b72ed4875558f5e1aedee9b7506e52e4f9a2"
    ),
}
WAVE8_IRISH_ROYALISTS_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_IRISH_ROYALISTS_ROW_HASHES
)


WAVE8_IRISH_ROYALISTS_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "1d6baa04aed05281afe720349b0040d3e69db4b1160041fb5a512c806186e8fb"
    ),
    "events_touched": 2,
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 2,
    },
    "label": _EXACT_LABEL,
    "rated_counterpart_entities": 2,
    "sole_blocker_events": 2,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 2,
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    start_date: str,
    end_date: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "day" if start_date == end_date else "day_range",
        "date_text": date_text,
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


_EVENT_SOURCE_IDS: dict[str, tuple[str, ...]] = {
    "hced-Dungan Hill1647-1": _DUNGAN_SOURCE_IDS,
    "hced-Clonmel1650-1": _CLONMEL_SOURCE_IDS,
}

_EVENT_EVIDENCE_ROLES: dict[str, dict[str, list[str]]] = {
    "hced-Dungan Hill1647-1": {
        "wave8_irish_royalists_libris_dungans_hill_relation": [
            "contemporary_parliamentary_victory_relation",
            "exact_engagement_date",
            "parliamentarian_field_army",
            "tactical_outcome",
        ],
        "wave8_irish_royalists_ucd_fitzpatrick_dungans_hill": [
            "confederate_leinster_army_identity",
            "exact_engagement_date_crosscheck",
            "irish_defeat_crosscheck",
            "thomas_preston_force_context",
        ],
    },
    "hced-Clonmel1650-1": {
        "wave8_irish_royalists_bcw_clonmel": [
            "exact_siege_interval",
            "full_siege_granularity",
            "new_model_besieger_identity",
            "town_surrender_outcome",
        ],
        "wave8_irish_royalists_history_ireland_hugh_dubh": [
            "garrison_identity",
            "garrison_withdrawal_before_town_surrender",
            "nested_assault_defender_victory",
            "ormond_alignment_context",
        ],
        "wave8_irish_royalists_ucc_celt_parliamentary_proceedings": [
            "clonmel_defence_crosscheck",
            "contemporary_parliamentarian_context",
            "hugh_dubh_garrison_crosscheck",
        ],
    },
}


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    reviewed_outcome: str,
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(_EVENT_SOURCE_IDS[candidate_id])
    return {
        "raw_row_sha256": WAVE8_IRISH_ROYALISTS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "civil_war",
        "confidence": confidence,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "event_evidence_roles": {
            source_id: list(roles)
            for source_id, roles in sorted(
                _EVENT_EVIDENCE_ROLES[candidate_id].items()
            )
        },
        "date_source_ids": outcomes,
        "source_date_refinement": True,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_alias_free_event_bounded_forces",
        "expected_scale_level": 2,
        "reviewed_outcome": reviewed_outcome,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_IRISH_ROYALISTS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Dungan Hill1647-1": _contract(
        "hced-Dungan Hill1647-1",
        _canonical(
            "Battle of Dungan's Hill",
            1647,
            "8 August 1647",
            "1647-08-08",
            "1647-08-08",
            "single_engagement_at_dungans_hill",
        ),
        [_DUNGAN_PARLIAMENTARIANS],
        [_DUNGAN_CONFEDERATES],
        "Parliamentarian tactical victory over Preston's Confederate force",
        (
            "The contemporary parliamentary relation identifies Michael "
            "Jones's victory on 8 August, and the UCD archive independently "
            "catalogues Preston's correspondence after the Irish defeat. The "
            "contract corrects HCED's anachronistic Commonwealth label without "
            "creating broad English or Parliamentarian continuity."
        ),
        confidence=0.96,
    ),
    "hced-Clonmel1650-1": {
        **_contract(
            "hced-Clonmel1650-1",
            _canonical(
                "Siege of Clonmel",
                1650,
                "27 April–18 May 1650",
                "1650-04-27",
                "1650-05-18",
                "full_siege_operation_excluding_nested_17_may_assault",
            ),
            [_CLONMEL_NEW_MODEL],
            [_CLONMEL_GARRISON],
            (
                "New Model Army siege-objective victory after the garrison "
                "withdrew and the town surrendered"
            ),
            (
                "This contract rates only the complete siege: the New Model "
                "Army obtained Clonmel after Hugh Dubh O'Neill withdrew his "
                "garrison and the town concluded surrender terms. The bloody "
                "17 May assault was a defender tactical victory; it is a nested "
                "constituent, is not emitted, and cannot reverse or duplicate "
                "the reviewed full-siege result."
            ),
            confidence=0.94,
        ),
        "nested_assault_date": "1650-05-17",
        "nested_assault_disposition": (
            "excluded_constituent_defender_tactical_victory"
        ),
        "full_siege_outcome_basis": (
            "town_surrendered_after_ormond_aligned_garrison_withdrawal"
        ),
    },
}


WAVE8_IRISH_ROYALISTS_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_IRISH_ROYALISTS_CONTRACT_IDS = frozenset(
    WAVE8_IRISH_ROYALISTS_CONTRACTS
)
WAVE8_IRISH_ROYALISTS_RESERVED_IDS = WAVE8_IRISH_ROYALISTS_CONTRACT_IDS


WAVE8_IRISH_ROYALISTS_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_IRISH_ROYALISTS_CONTRACT_IDS
)
WAVE8_IRISH_ROYALISTS_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Dungan Hill1647-1"}
)
WAVE8_IRISH_ROYALISTS_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    "hced-Dungan Hill1647-1": {
        "actions": ["withhold_country", "withhold_point"],
        "raw_country": "United Kingdom",
        "raw_point": [-6.7441695, 53.5752006],
        "reason": (
            "The engagement was in County Meath, Ireland, so HCED's modern "
            "United Kingdom country assertion is wrong. Its coordinate also "
            "conflicts materially with the staged discovery point and is not "
            "independently validated; withhold both fields."
        ),
        "evidence_refs": sorted(_DUNGAN_SOURCE_IDS),
    },
    "hced-Clonmel1650-1": {
        "actions": ["withhold_point"],
        "raw_country": "Ireland",
        "raw_point": [-7.6902551, 52.3558172],
        "reason": (
            "The sources establish Clonmel and modern Ireland but do not "
            "independently audit HCED's exact point. Retain country and "
            "provenance; withhold the coordinate."
        ),
        "evidence_refs": sorted(_CLONMEL_SOURCE_IDS),
    },
}


WAVE8_IRISH_ROYALISTS_DISCOVERY_TWINS: dict[str, str] = {
    "hced-Dungan Hill1647-1": "Q494896",
    "hced-Clonmel1650-1": "Q815132",
}
WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q494896": (
        "e283bbbd7894bc607ad261a8d8c25fa16d8b582b3134870f82f0b2a6b020e921"
    ),
    "Q815132": (
        "223794d7a350e3a27f244bde539beb4552add8b6fea0a46d6fac6b37f415a944"
    ),
}
WAVE8_IRISH_ROYALISTS_DISCOVERY_EXPECTED: dict[str, dict[str, Any]] = {
    "Q494896": {
        "date": "1647-08-01T00:00:00Z",
        "end_date": None,
        "kind": "engagement",
        "name": "Battle of Dungan's Hill",
        "participant_labels": ["Kingdom of England"],
        "outcome_disposition": "unknown_never_draw",
        "date_disposition": "discovery_month_value_not_used_for_exact_day",
    },
    "Q815132": {
        "date": "1650-04-01T00:00:00Z",
        "end_date": "1650-05-01T00:00:00Z",
        "kind": "siege",
        "name": "Siege of Clonmel",
        "participant_labels": [],
        "outcome_disposition": "unknown_never_draw",
        "date_disposition": "discovery_month_bounds_not_used_for_exact_interval",
    },
}
WAVE8_IRISH_ROYALISTS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    discovery_id: {
        "source_dataset": "wikidata-battles",
        "disposition": "discovery_only_duplicate",
        "hced_candidate_id": hced_id,
        "outcome_disposition": WAVE8_IRISH_ROYALISTS_DISCOVERY_EXPECTED[
            discovery_id
        ]["outcome_disposition"],
        "date_disposition": WAVE8_IRISH_ROYALISTS_DISCOVERY_EXPECTED[
            discovery_id
        ]["date_disposition"],
    }
    for hced_id, discovery_id in sorted(
        WAVE8_IRISH_ROYALISTS_DISCOVERY_TWINS.items()
    )
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_IRISH_ROYALISTS_CONTRACTS,
        "discovery_expected": WAVE8_IRISH_ROYALISTS_DISCOVERY_EXPECTED,
        "discovery_row_hashes": WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES,
        "discovery_twins": WAVE8_IRISH_ROYALISTS_DISCOVERY_TWINS,
        "entities": WAVE8_IRISH_ROYALISTS_ENTITIES,
        "funnel": WAVE8_IRISH_ROYALISTS_FUNNEL_AUDIT,
        "holds": WAVE8_IRISH_ROYALISTS_HOLDS,
        "integration_dispositions": WAVE8_IRISH_ROYALISTS_INTEGRATION_DISPOSITIONS,
        "location_reasons": WAVE8_IRISH_ROYALISTS_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_IRISH_ROYALISTS_ROW_HASHES,
        "sources": WAVE8_IRISH_ROYALISTS_SOURCES,
    }


def wave8_irish_royalists_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_IRISH_ROYALISTS_FINAL_AUDIT_SIGNATURE = (
    "63ef1b61661d017baada9704ff49f7146b4800014cc9bf6170450fb84101f684"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = set(_ENTITY_BY_ID)
    if len(source_ids) != len(WAVE8_IRISH_ROYALISTS_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if len(entity_ids) != len(WAVE8_IRISH_ROYALISTS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} duplicate entity id")
    if WAVE8_IRISH_ROYALISTS_HOLDS:
        raise ValueError(f"{_LANE_NAME} unexpected hold inventory")
    if (
        WAVE8_IRISH_ROYALISTS_RESERVED_IDS
        != WAVE8_IRISH_ROYALISTS_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if (
        WAVE8_IRISH_ROYALISTS_POINT_QUARANTINE_ADDITIONS
        != WAVE8_IRISH_ROYALISTS_CONTRACT_IDS
        or WAVE8_IRISH_ROYALISTS_COUNTRY_QUARANTINE_ADDITIONS
        != {"hced-Dungan Hill1647-1"}
        or set(WAVE8_IRISH_ROYALISTS_LOCATION_QUARANTINE_REASONS)
        != WAVE8_IRISH_ROYALISTS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location policy drift")

    expected_urls = {
        "wave8_irish_royalists_bcw_clonmel": (
            "https://bcw-project.org.uk/military/third-civil-war/"
            "cromwell-in-ireland/clonmel"
        ),
        "wave8_irish_royalists_history_ireland_hugh_dubh": (
            "https://historyireland.com/hugh-dubh-oneill-cromwells-stoutest-enemy/"
        ),
        "wave8_irish_royalists_libris_dungans_hill_relation": (
            "https://libris.kb.se/bib/10747719"
        ),
        "wave8_irish_royalists_ucc_celt_parliamentary_proceedings": (
            "https://celt.ucc.ie/document/E650001-001/"
        ),
        "wave8_irish_royalists_ucd_fitzpatrick_dungans_hill": (
            "https://www.ucd.ie/archives/t4media/"
            "la0012-fitzpatrick-thomas-descriptive-catalogue.pdf"
        ),
    }
    for source_id, source in _SOURCE_BY_ID.items():
        if source["url"] != expected_urls[source_id]:
            raise ValueError(f"{_LANE_NAME} canonical source URL drift: {source_id}")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source role order drift: {source_id}")
        if "outcome" not in source["evidence_roles"]:
            raise ValueError(f"{_LANE_NAME} non-outcome source used for result")

    expected_entity_windows = {
        _DUNGAN_PARLIAMENTARIANS: 1647,
        _DUNGAN_CONFEDERATES: 1647,
        _CLONMEL_NEW_MODEL: 1650,
        _CLONMEL_GARRISON: 1650,
    }
    for entity_id, year in expected_entity_windows.items():
        entity = _ENTITY_BY_ID[entity_id]
        if (
            entity["start_year"] != year
            or entity["end_year"] != year
            or entity["aliases"]
            or entity["predecessors"]
            or not _is_sorted_unique(entity["source_ids"])
            or not set(entity["source_ids"]) <= source_ids
            or "inherits no Elo" not in entity["continuity_note"]
        ):
            raise ValueError(f"{_LANE_NAME} event-bounded entity drift: {entity_id}")

    expected = {
        "hced-Dungan Hill1647-1": (
            "Battle of Dungan's Hill",
            1647,
            "8 August 1647",
            "1647-08-08",
            "1647-08-08",
            "day",
            "single_engagement_at_dungans_hill",
            [_DUNGAN_PARLIAMENTARIANS],
            [_DUNGAN_CONFEDERATES],
            0.96,
        ),
        "hced-Clonmel1650-1": (
            "Siege of Clonmel",
            1650,
            "27 April–18 May 1650",
            "1650-04-27",
            "1650-05-18",
            "day_range",
            "full_siege_operation_excluding_nested_17_may_assault",
            [_CLONMEL_NEW_MODEL],
            [_CLONMEL_GARRISON],
            0.94,
        ),
    }
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_IRISH_ROYALISTS_CONTRACTS.items():
        (
            name,
            year,
            date_text,
            start_date,
            end_date,
            precision,
            granularity,
            side_1,
            side_2,
            confidence,
        ) = expected[candidate_id]
        canonical = contract["canonical_event"]
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or int(contract["expected_scale_level"]) != 2
            or contract["side_1_entity_ids"] != side_1
            or contract["side_2_entity_ids"] != side_2
            or float(contract["confidence"]) != confidence
            or canonical["canonical_key"] != f"{_slug(name)}:{year}:{year}"
            or canonical["name"] != name
            or canonical["date_text"] != date_text
            or canonical["start_date"] != start_date
            or canonical["end_date"] != end_date
            or canonical["date_precision"] != precision
            or canonical["granularity"] != granularity
            or (canonical["year_low"], canonical["year_high"]) != (year, year)
        ):
            raise ValueError(f"{_LANE_NAME} exact contract drift: {candidate_id}")
        outcomes = list(map(str, contract["outcome_source_ids"]))
        expected_sources = sorted(_EVENT_SOURCE_IDS[candidate_id])
        expected_families = sorted(
            str(_SOURCE_BY_ID[source_id]["source_family_id"])
            for source_id in expected_sources
        )
        if (
            outcomes != expected_sources
            or contract["evidence_refs"] != outcomes
            or contract["date_source_ids"] != outcomes
            or contract["outcome_source_family_ids"] != expected_families
            or len(expected_families) < 2
            or contract["source_date_refinement"] is not True
            or set(contract["event_evidence_roles"]) != set(outcomes)
        ):
            raise ValueError(f"{_LANE_NAME} source closure drift: {candidate_id}")
        for roles in contract["event_evidence_roles"].values():
            if not roles or not _is_sorted_unique(roles):
                raise ValueError(f"{_LANE_NAME} event evidence role drift")
        used_sources.update(outcomes)
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    clonmel = WAVE8_IRISH_ROYALISTS_CONTRACTS["hced-Clonmel1650-1"]
    if (
        clonmel.get("nested_assault_date") != "1650-05-17"
        or clonmel.get("nested_assault_disposition")
        != "excluded_constituent_defender_tactical_victory"
        or clonmel.get("full_siege_outcome_basis")
        != "town_surrendered_after_ormond_aligned_garrison_withdrawal"
    ):
        raise ValueError(f"{_LANE_NAME} nested Clonmel assault guard drift")
    if set(WAVE8_IRISH_ROYALISTS_DISCOVERY_TWINS) != (
        WAVE8_IRISH_ROYALISTS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} discovery owner drift")
    if set(WAVE8_IRISH_ROYALISTS_DISCOVERY_TWINS.values()) != set(
        WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES
    ) or set(WAVE8_IRISH_ROYALISTS_DISCOVERY_EXPECTED) != set(
        WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} discovery inventory drift")
    if any(
        item["outcome_disposition"] != "unknown_never_draw"
        for item in WAVE8_IRISH_ROYALISTS_DISCOVERY_EXPECTED.values()
    ):
        raise ValueError(f"{_LANE_NAME} unknown-is-never-draw guard drift")
    if set(WAVE8_IRISH_ROYALISTS_INTEGRATION_DISPOSITIONS) != set(
        WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} integration disposition drift")
    if (
        wave8_irish_royalists_audit_signature()
        != WAVE8_IRISH_ROYALISTS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_irish_royalists_queue_contracts(
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
    if exact_ids != WAVE8_IRISH_ROYALISTS_RESERVED_IDS or len(exact) != len(
        exact_ids
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    expected_rows = {
        "hced-Dungan Hill1647-1": (
            1647,
            "Commonwealth of England",
            "Irish Royalists",
        ),
        "hced-Clonmel1650-1": (1650, "Parliamentarians", "Irish Royalists"),
    }
    for candidate_id, expected_hash in WAVE8_IRISH_ROYALISTS_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        year, winner, loser = expected_rows[candidate_id]
        if (
            (row.get("year_low"), row.get("year_best"), row.get("year_high"))
            != (year, year, year)
            or row.get("side_1_raw") != winner
            or row.get("side_2_raw") != loser
            or row.get("winner_raw") != winner
            or row.get("loser_raw") != loser
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("do_not_rate_automatically") is not True
            or row.get("duplicate_source_id") is not False
            or normalize_label(row.get("winner_raw"))
            in {"draw", "inconclusive", "stalemate", "unknown"}
        ):
            raise ValueError(f"{_LANE_NAME} locked outcome/actor row drift: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_IRISH_ROYALISTS_CONTRACTS,
        WAVE8_IRISH_ROYALISTS_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_irish_royalists_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    rows = [
        row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL
    ]
    if len(rows) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    row = rows[0]
    actual = {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "failure_cases": {
            key: int(row.get("failure_cases", {}).get(key, -1))
            for key in WAVE8_IRISH_ROYALISTS_FUNNEL_AUDIT["failure_cases"]
        },
        "label": str(row.get("label")),
        "rated_counterpart_entities": int(
            row.get("rated_counterpart_entities", -1)
        ),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, row.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
    }
    if actual != WAVE8_IRISH_ROYALISTS_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pin changed: {actual}")
    return {
        "events_touched": actual["events_touched"],
        "sole_blocker_events": actual["sole_blocker_events"],
        "unresolved_side_attempts": actual["unresolved_side_attempts"],
        "zero_time_valid_candidates": actual["failure_cases"][
            "zero_time_valid_candidates"
        ],
    }


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def validate_wave8_irish_royalists_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in (
        WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} discovery row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}")
        expected = WAVE8_IRISH_ROYALISTS_DISCOVERY_EXPECTED[candidate_id]
        participant_labels = sorted(
            str(participant.get("label"))
            for participant in row.get("participants", [])
        )
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("name") != expected["name"]
            or row.get("date") != expected["date"]
            or row.get("end_date") != expected["end_date"]
            or row.get("kind") != expected["kind"]
            or participant_labels != expected["participant_labels"]
            or row.get("winners") != []
        ):
            raise ValueError(
                f"{_LANE_NAME} discovery non-rating guard changed: {candidate_id}"
            )
    return {
        "discovery_nonrating_twins": len(
            WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES
        ),
        "discovery_promotions": 0,
        "unknown_never_draw_rows": len(
            WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES
        ),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "start_year", "batyear"):
        try:
            if row.get(key) is not None:
                return int(row[key])
        except (TypeError, ValueError):
            pass
    for key in ("start_date", "date"):
        value = str(row.get(key) or "")
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    values = [
        row.get("name"),
        row.get("battle_name"),
        row.get("batname"),
        row.get("event_name"),
        row.get("war_name"),
    ]
    aliases = row.get("aliases", []) or []
    if isinstance(aliases, str):
        values.append(aliases)
    else:
        values.extend(aliases)
    return {normalize_label(value) for value in values if normalize_label(value)}


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Dungan Hill1647-1": {
        "Dungan Hill",
        "Dungan's Hill",
        "Dungans Hill",
        "Dungons-Hill",
        "Battle of Dungan's Hill",
    },
    "hced-Clonmel1650-1": {
        "Clonmel",
        "Siege of Clonmel",
        "Assault on Clonmel",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(
            WAVE8_IRISH_ROYALISTS_CONTRACTS[candidate_id]["canonical_event"][
                "year_low"
            ]
        ),
        normalize_label(alias),
    )
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_irish_royalists_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwd_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_irish_royalists_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_IRISH_ROYALISTS_RESERVED_IDS
        and _is_probable_twin(row)
    )
    iwd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwd_rows
        if _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    existing = list(existing_events)
    owned = [
        event
        for event in existing
        if event.get("hced_candidate_id")
        in WAVE8_IRISH_ROYALISTS_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    if owned:
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        if owned_ids != WAVE8_IRISH_ROYALISTS_CONTRACT_IDS or len(owned) != len(
            owned_ids
        ):
            raise ValueError(f"{_LANE_NAME} current release ownership is partial")
        if any(
            not str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
            for event in owned
        ):
            raise ValueError(f"{_LANE_NAME} current release owner prefix changed")
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event not in owned and _is_probable_twin(event)
    )
    if hced_twins or iwd_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"iwd={iwd_twins}, iwbd={iwbd_twins}, release={release_twins}"
        )
    return {
        "discovery_nonrating_dispositions": len(
            WAVE8_IRISH_ROYALISTS_INTEGRATION_DISPOSITIONS
        ),
        "existing_release_owned_events": len(owned),
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwd_probable_twins": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_irish_royalists_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_IRISH_ROYALISTS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_irish_royalists_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_IRISH_ROYALISTS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_IRISH_ROYALISTS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_IRISH_ROYALISTS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def validate_wave8_irish_royalists_emissions(
    events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    owned = list(events)
    by_id = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_id) != WAVE8_IRISH_ROYALISTS_CONTRACT_IDS or len(owned) != len(
        by_id
    ):
        raise ValueError(f"{_LANE_NAME} emitted inventory drift")
    participant_count = 0
    for candidate_id, contract in WAVE8_IRISH_ROYALISTS_CONTRACTS.items():
        event = by_id[candidate_id]
        canonical = contract["canonical_event"]
        expected_participants = expected_exact_hced_win_participants(
            contract["side_1_entity_ids"],
            contract["side_2_entity_ids"],
            confidence=float(contract["confidence"]),
            scale_level=int(contract["expected_scale_level"]),
            lane_name=_LANE_NAME,
        )
        if (
            event.get("id") != f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year"))
            != (canonical["year_low"], canonical["year_high"])
            or event.get("date_precision") != canonical["date_precision"]
            or event.get("reviewed_granularity") != canonical["granularity"]
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("event_type") != "engagement"
            or event.get("war_type") != "civil_war"
            or event.get("participants") != expected_participants
            or event.get("source_ids")
            != ["hced_dataset", *contract["evidence_refs"]]
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids")
            != contract["outcome_source_family_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} emitted contract drift: {candidate_id}")
        if any(
            "inconclusive" in str(participant.get("termination", ""))
            for participant in event["participants"]
        ):
            raise ValueError(f"{_LANE_NAME} emitted unknown/draw drift: {candidate_id}")
        participant_count += len(event["participants"])

        if candidate_id == "hced-Dungan Hill1647-1":
            if any(
                key in event
                for key in (
                    "geometry",
                    "modern_location_country",
                    "location_provenance",
                )
            ):
                raise ValueError(f"{_LANE_NAME} Dungan location quarantine leaked")
        elif (
            "geometry" in event
            or event.get("modern_location_country") != "Ireland"
            or event.get("location_provenance", {}).get("assertion_status")
            != "unreviewed_source_assertion"
        ):
            raise ValueError(f"{_LANE_NAME} Clonmel location treatment drift")
    return {
        "events": len(owned),
        "participants": participant_count,
        "retained_countries": 1,
        "retained_points": 0,
    }


def promote_wave8_irish_royalists_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_irish_royalists_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_IRISH_ROYALISTS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine(events)
    validate_wave8_irish_royalists_emissions(events)
    return events


def _entity_covers(entity: Mapping[str, Any], low: int, high: int) -> bool:
    start = entity.get("start_year")
    end = entity.get("end_year")
    return (
        start is not None
        and int(start) <= low
        and (end is None or int(end) >= high)
    )


def validate_wave8_irish_royalists_current_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Require lane events, entities, and sources to be absent or complete."""

    _validate_static()
    events = list(release_events)
    owned = [
        event
        for event in events
        if event.get("hced_candidate_id")
        in WAVE8_IRISH_ROYALISTS_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    entity_by_id = {str(entity.get("id")): entity for entity in release_entities}
    present_entity_ids = set(entity_by_id) & set(_ENTITY_BY_ID)
    source_by_id = {str(source.get("id")): source for source in release_sources}
    present_source_ids = set(source_by_id) & set(_SOURCE_BY_ID)
    expected_counts = (
        len(WAVE8_IRISH_ROYALISTS_CONTRACT_IDS),
        len(_ENTITY_BY_ID),
        len(_SOURCE_BY_ID),
    )
    actual_counts = (len(owned), len(present_entity_ids), len(present_source_ids))
    if actual_counts == (0, 0, 0):
        return {
            "artifact_state": "absent",
            "installed_entities": 0,
            "installed_sources": 0,
            "promoted_events": 0,
        }
    if actual_counts != expected_counts:
        raise ValueError(
            f"{_LANE_NAME} current release artifacts are partial: {actual_counts}"
        )
    for entity_id, expected in _ENTITY_BY_ID.items():
        actual = entity_by_id[entity_id]
        if actual != expected or not _entity_covers(
            actual, int(expected["start_year"]), int(expected["end_year"])
        ):
            raise ValueError(f"{_LANE_NAME} current release entity drift: {entity_id}")
    for source_id, expected in _SOURCE_BY_ID.items():
        if source_by_id[source_id] != expected:
            raise ValueError(f"{_LANE_NAME} current release source drift: {source_id}")
    validate_wave8_irish_royalists_emissions(owned)
    return {
        "artifact_state": "integrated",
        "installed_entities": len(present_entity_ids),
        "installed_sources": len(present_source_ids),
        "promoted_events": len(owned),
    }


def wave8_irish_royalists_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_IRISH_ROYALISTS_CONTRACTS.values(),
                    *WAVE8_IRISH_ROYALISTS_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_irish_royalists_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_IRISH_ROYALISTS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_nonrating_records": len(
            WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES
        ),
        "holds": len(WAVE8_IRISH_ROYALISTS_HOLDS),
        "integration_dispositions": len(
            WAVE8_IRISH_ROYALISTS_INTEGRATION_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_IRISH_ROYALISTS_ENTITIES),
        "new_sources": len(WAVE8_IRISH_ROYALISTS_SOURCES),
        "newly_rated_events": len(WAVE8_IRISH_ROYALISTS_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_IRISH_ROYALISTS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_IRISH_ROYALISTS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_IRISH_ROYALISTS_RESERVED_IDS),
        "terminal_exclusions": 0,
        "unknown_discovery_outcomes": len(
            WAVE8_IRISH_ROYALISTS_DISCOVERY_ROW_HASHES
        ),
    }


def wave8_irish_royalists_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_IRISH_ROYALISTS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_IRISH_ROYALISTS_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_irish_royalists_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_irish_royalists_counts(),
        "cohorts": wave8_irish_royalists_cohort_counts(),
        "country_quarantine_additions": sorted(
            WAVE8_IRISH_ROYALISTS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_IRISH_ROYALISTS_INTEGRATION_DISPOSITIONS.items()
            )
        ],
        "final_audit_signature": WAVE8_IRISH_ROYALISTS_FINAL_AUDIT_SIGNATURE,
        "point_quarantine_additions": sorted(
            WAVE8_IRISH_ROYALISTS_POINT_QUARANTINE_ADDITIONS
        ),
        "promoted_candidate_ids": sorted(
            WAVE8_IRISH_ROYALISTS_CONTRACT_IDS
        ),
    }


_validate_static()
