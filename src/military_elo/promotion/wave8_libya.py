"""Candidate-keyed audit of HCED's unresolved ``Libya`` Chad-war rows.

The lane reuses the alias-free, time-bounded ``libyan_arab_jamahiriya``
identity for exactly three fingerprinted rows.  Faya-Largeau binds a separate
event-bounded GUNT co-belligerent; Aozou and Zouar record source-backed outcome
reversals.  No generic ``libya`` alias or identity window is changed.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import date
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_chadian_rebels import (
    WAVE8_CHADIAN_REBELS_FINAL_AUDIT_SIGNATURE,
    wave8_chadian_rebels_audit_signature,
)
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_LIBYA_CHADIAN_REBELS_SIGNATURE",
    "WAVE8_LIBYA_CONTRACT_IDS",
    "WAVE8_LIBYA_CONTRACTS",
    "WAVE8_LIBYA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_LIBYA_ENTITIES",
    "WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS",
    "WAVE8_LIBYA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_LIBYA_FUNNEL_AUDIT",
    "WAVE8_LIBYA_HOLDS",
    "WAVE8_LIBYA_IWBD_DISPOSITIONS",
    "WAVE8_LIBYA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_LIBYA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_LIBYA_RESERVED_IDS",
    "WAVE8_LIBYA_ROW_HASHES",
    "WAVE8_LIBYA_SOURCES",
    "install_wave8_libya_entities",
    "install_wave8_libya_sources",
    "promote_wave8_libya_contracts",
    "validate_wave8_libya_frozen_chadian_rebels",
    "validate_wave8_libya_funnel",
    "validate_wave8_libya_integration_dispositions",
    "validate_wave8_libya_queue_contracts",
    "wave8_libya_audit_signature",
    "wave8_libya_cohort_counts",
    "wave8_libya_counts",
    "wave8_libya_metadata",
)


_LANE_NAME = "Wave 8 exact Libyan Arab Jamahiriya Chad-war audit"
_MODULE_OWNER = "military_elo.promotion.wave8_libya"
_EVENT_ID_PREFIX = "hced_wave8_libya_"
_EXACT_LABEL = "libya"

_LIBYA = "libyan_arab_jamahiriya"
_CHAD = "republic_chad"
_FAYA_GUNT = "gunt_faya_largeau_assault_force_1983"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    crosscheck: bool = False,
    government_work: bool = False,
) -> dict[str, Any]:
    roles = {"identity_boundary_or_context_reference", "outcome"}
    if crosscheck:
        roles.add("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "U.S. Government work" if government_work else "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-18",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_LIBYA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_libya_loc_chad_country_study",
        "Chad: A Country Study",
        (
            "https://tile.loc.gov/storage-services/master/frd/frdcstdy/ch/"
            "chadcountrystudy00coll/chadcountrystudy00coll.pdf"
        ),
        "Library of Congress, Federal Research Division",
        "federal_country_study",
        "loc_chad_country_study_1990",
        crosscheck=True,
        government_work=True,
    ),
    _source(
        "wave8_libya_washpost_faya_1983",
        "Faya Largeau Falls to Libyans, Rebels",
        (
            "https://www.washingtonpost.com/archive/politics/1983/08/12/"
            "president-sets-limit-on-military-support-of-chad-in-struggle/"
            "b9214911-92b2-4df0-9eed-68fc67de9fa8/"
        ),
        "The Washington Post",
        "contemporaneous_independent_reporting",
        "washington_post_faya_largeau_1983",
    ),
    _source(
        "wave8_libya_un_yearbook_1987",
        "Yearbook of the United Nations 1987",
        (
            "https://digitallibrary.un.org/nanna/record/143313/files/"
            "278477-EN.pdf?registerDownload=1&version=1&withMetadata=0&"
            "withWatermark=0"
        ),
        "United Nations",
        "official_contemporaneous_yearbook",
        "un_yearbook_1987_chad_libya",
        crosscheck=True,
    ),
    _source(
        "wave8_libya_washpost_aozou_1987",
        "Libya Shows Retaken Town to Reporters",
        (
            "https://www.washingtonpost.com/archive/politics/1987/08/30/"
            "libya-shows-retaken-town-to-reporters/"
            "fedef462-4bbd-4fde-b6c2-e4ec46a06faf/"
        ),
        "The Washington Post",
        "contemporaneous_independent_reporting",
        "washington_post_aozou_1987",
    ),
    _source(
        "wave8_libya_iwbd_zouar",
        "International Wars and Battles Dataset: Zouar row",
        "https://dataverse.harvard.edu/api/access/datafile/4435240?format=original",
        "Harvard Dataverse",
        "research_dataset",
        "iwbd_dataverse_release",
        crosscheck=True,
    ),
    _source(
        "wave8_libya_elpais_zouar_1987",
        "Las fuerzas de Chad recuperan el control de un oasis tomado por Libia",
        (
            "https://elpais.com/diario/1987/01/02/internacional/"
            "536540419_850215.html"
        ),
        "El País",
        "contemporaneous_independent_reporting",
        "el_pais_zouar_1987",
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_LIBYA_SOURCES}


WAVE8_LIBYA_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _FAYA_GUNT,
        "name": "Goukouni GUNT assault force at Faya-Largeau (1983)",
        "kind": "event_bounded_rebel_co_belligerent_force",
        "start_year": 1983,
        "end_year": 1983,
        "region": "Northern Chad",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Only Goukouni Oueddei's GUNT-aligned force participating with Libyan "
            "units in the August 1983 Faya-Largeau assault is rated. No rating is "
            "inherited from or passed to generic GUNT, FROLINAT, Chadian rebels, "
            "Libya, Chad, or another campaign formation."
        ),
        "source_ids": [
            "wave8_libya_loc_chad_country_study",
            "wave8_libya_washpost_faya_1983",
        ],
    },
)


WAVE8_LIBYA_ROW_HASHES: dict[str, str] = {
    "hced-Aozou1987-1": (
        "7f972cd9cf50ca7a68c757194cb4a379c4f10c6aad20c89f03b89ffe5b8a1c7f"
    ),
    "hced-Faya Largeau1983-1": (
        "632d34a58b407b31fc8d7bbee9e89e8ad91f824cba437d95ff9a5b3e0ca9b6e0"
    ),
    "hced-Zouar1986-1987-1": (
        "5e45a4627804bb2f967845a7a410883774054fcd2cdde5f2decfb0ea93a6f1af"
    ),
}

WAVE8_LIBYA_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": ["clio_q1016_2014_0f60d924"],
    "event_candidate_id_sha256": (
        "c5e90ace8472b2e2235bbe09342762993e673e9c3617480f479384c7893d626b"
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
    winner_side: int,
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    reversal: bool,
    war_type: str,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    contract: dict[str, Any] = {
        "raw_row_sha256": WAVE8_LIBYA_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "chadian_libyan_war_1983_1987",
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": reversal,
        "outcome_reversal": reversal,
        "actor_override": "candidate_keyed_chad_war_belligerents",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }
    if reversal:
        contract["source_conflict_disposition"] = {
            "disposition": "reviewed_outcome_replaces_hced_source_coding",
            "direct_source_ids": outcomes,
            "raw_winner": "Chad" if candidate_id == "hced-Aozou1987-1" else "Libya",
            "reviewed_winner": "Libya" if candidate_id == "hced-Aozou1987-1" else "Chad",
        }
    return contract


WAVE8_LIBYA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Faya Largeau1983-1": _contract(
        "hced-Faya Largeau1983-1",
        _canonical(
            "Capture of Faya-Largeau (August 1983)",
            1983,
            1983,
            "day",
            "10 August 1983",
            "joint_libyan_gunt_assault_and_government_withdrawal",
        ),
        [_LIBYA, _FAYA_GUNT],
        [_CHAD],
        1,
        [
            "wave8_libya_loc_chad_country_study",
            "wave8_libya_washpost_faya_1983",
        ],
        (
            "Contemporaneous reporting and the federal country study record a "
            "joint Libyan and Goukouni-aligned assault driving Habré's forces from "
            "Faya-Largeau on 10 August. The contract rates that local tactical "
            "capture only. HCED's modern-location label is retained verbatim as a "
            "rating-neutral source assertion, not treated as sovereign truth."
        ),
        confidence=0.92,
        reversal=False,
        war_type="intrastate_with_foreign_intervention",
    ),
    "hced-Aozou1987-1": _contract(
        "hced-Aozou1987-1",
        _canonical(
            "Battle of Aozou (August 1987)",
            1987,
            1987,
            "day_range",
            "8-28 August 1987",
            "two_phase_chadian_capture_and_libyan_recapture",
        ),
        [_CHAD],
        [_LIBYA],
        2,
        [
            "wave8_libya_un_yearbook_1987",
            "wave8_libya_washpost_aozou_1987",
        ],
        (
            "The reviewed event is the complete August sequence: Chad captured "
            "Aozou on 8 August and Libya recaptured it on 28 August. The final local "
            "battlefield result therefore reverses HCED's Chad winner. The year-only "
            "HCED row is not claimed to align to IWBD's 8-27 August date range."
        ),
        confidence=0.78,
        reversal=True,
        war_type="interstate",
    ),
    "hced-Zouar1986-1987-1": _contract(
        "hced-Zouar1986-1987-1",
        _canonical(
            "Battle of Zouar (1986-1987)",
            1986,
            1987,
            "day_range",
            "14 December 1986-2 January 1987",
            "libyan_counterattack_and_definitive_chadian_recapture",
        ),
        [_LIBYA],
        [_CHAD],
        2,
        [
            "wave8_libya_elpais_zouar_1987",
            "wave8_libya_iwbd_zouar",
        ],
        (
            "IWBD and contemporaneous reporting record the Chadian recovery of "
            "Zouar by 2 January 1987 after the December Libyan counterattack. The "
            "reviewed Chadian tactical result reverses HCED's Libya winner; the "
            "IWBD row remains held so the same action is never rated twice."
        ),
        confidence=0.78,
        reversal=True,
        war_type="interstate",
    ),
}


WAVE8_LIBYA_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_LIBYA_CONTRACT_IDS = frozenset(WAVE8_LIBYA_CONTRACTS)
WAVE8_LIBYA_RESERVED_IDS = frozenset(WAVE8_LIBYA_ROW_HASHES)


# The other three exact-label HCED rows are already represented by distinct
# IWBD events.  They remain outside this lane and cannot be re-owned.
WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Fada1987-1": {
        "raw_row_sha256": "63a7cc4122190f20ce9af413fc9ebb56f47d470625164615b75db636e4701981",
        "owner_event_id": "iwbd_iwbd_207_80_1652_fada",
        "expected_name": "Fada",
        "expected_year": 1987,
        "expected_entity_ids": [_LIBYA, _CHAD],
        "disposition": "existing_iwbd_owner",
    },
    "hced-Maaten-as-Sarra1987-1": {
        "raw_row_sha256": "2add7231c5894860d7bca804c09140162e8f3db388e2f28f2d2a775a8dcc17b8",
        "owner_event_id": "iwbd_iwbd_207_80_1655_maaten_as_sarra",
        "expected_name": "Maaten-as-Sarra",
        "expected_year": 1987,
        "expected_entity_ids": [_LIBYA, _CHAD],
        "disposition": "existing_iwbd_owner",
    },
    "hced-Ouadi Doum1987-1": {
        "raw_row_sha256": "bc281cbb67c6f63ee838035ce8529007ad390df10061995989998f17b177a0db",
        "owner_event_id": "iwbd_iwbd_207_80_1653_ouadi_doum",
        "expected_name": "Ouadi Doum",
        "expected_year": 1987,
        "expected_entity_ids": [_LIBYA, _CHAD],
        "disposition": "existing_iwbd_owner",
    },
}


WAVE8_LIBYA_IWBD_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-207-80-1651": {
        "raw_row_sha256": "fb822bcdc8d2050a8248e27a51cc87cbe0dbdc33900b5b8dd12dff7eabaa8e1c",
        "owner_hced_candidate_id": "hced-Zouar1986-1987-1",
        "expected_name": "Zouar",
        "expected_start_date": "1986-12-14",
        "expected_end_date": "1987-01-02",
        "expected_attacker_raw": "Libya",
        "expected_defender_raw": "Chad",
        "expected_winner_raw": "Chad",
        "disposition": "same_action_wave6_hold_hced_reviewed_owner",
        "date_alignment_claimed": True,
        "reason": (
            "IWBD corroborates the reviewed Chadian result but remains on its frozen "
            "Wave 6 hold; the exact HCED contract owns the single rating."
        ),
    },
    "iwbd-207-80-1654": {
        "raw_row_sha256": "d217d3f995e608c2cb837539f0b692b5d81b508243968af86bbfda361aa9f7c7",
        "owner_hced_candidate_id": "hced-Aozou1987-1",
        "expected_name": "Aozou",
        "expected_start_date": "1987-08-08",
        "expected_end_date": "1987-08-27",
        "expected_attacker_raw": "Chad",
        "expected_defender_raw": "Libya",
        "expected_winner_raw": "Libya",
        "disposition": "related_august_sequence_wave6_hold_hced_reviewed_owner",
        "date_alignment_claimed": False,
        "reason": (
            "IWBD's 8-27 August range is related to the same named sequence but is "
            "not asserted as date-aligned with HCED. Independent sources establish "
            "the Libyan recapture on 28 August; IWBD remains non-emitting."
        ),
    },
}


# All three source points and source jurisdiction strings remain unreviewed,
# rating-neutral assertions.  This outcome lane neither authenticates nor
# rewrites them, and adds no location policy.
WAVE8_LIBYA_POINT_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_LIBYA_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_LIBYA_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {}

WAVE8_LIBYA_CHADIAN_REBELS_SIGNATURE = WAVE8_CHADIAN_REBELS_FINAL_AUDIT_SIGNATURE


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _canonical_object_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _signature_payload() -> dict[str, Any]:
    return {
        "chadian_rebels_signature": WAVE8_LIBYA_CHADIAN_REBELS_SIGNATURE,
        "contracts": WAVE8_LIBYA_CONTRACTS,
        "entities": WAVE8_LIBYA_ENTITIES,
        "existing_release_dispositions": WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS,
        "funnel": WAVE8_LIBYA_FUNNEL_AUDIT,
        "holds": WAVE8_LIBYA_HOLDS,
        "iwbd_dispositions": WAVE8_LIBYA_IWBD_DISPOSITIONS,
        "location_reasons": WAVE8_LIBYA_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_LIBYA_ROW_HASHES,
        "sources": WAVE8_LIBYA_SOURCES,
    }


def wave8_libya_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_LIBYA_FINAL_AUDIT_SIGNATURE = (
    "430735c63fd4b67ae76900b9f8f775343335896303cc8e7cbaf52fa52695dfa3"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def validate_wave8_libya_frozen_chadian_rebels() -> str:
    signature = wave8_chadian_rebels_audit_signature()
    if signature != WAVE8_LIBYA_CHADIAN_REBELS_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} changed the frozen Chadian Rebels lane")
    return signature


def _validate_static(*, check_signature: bool = True) -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_LIBYA_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if len(WAVE8_LIBYA_ENTITIES) != 1:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    entity = WAVE8_LIBYA_ENTITIES[0]
    if (
        entity["id"] != _FAYA_GUNT
        or (entity["start_year"], entity["end_year"]) != (1983, 1983)
        or entity["aliases"]
        or entity["predecessors"]
        or "no rating is inherited" not in str(entity["continuity_note"]).casefold()
    ):
        raise ValueError(f"{_LANE_NAME} GUNT continuity firewall drift")
    if not _is_sorted_unique(entity["source_ids"]) or not set(
        entity["source_ids"]
    ) <= source_ids:
        raise ValueError(f"{_LANE_NAME} entity source drift")
    if WAVE8_LIBYA_RESERVED_IDS != set(WAVE8_LIBYA_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} reservation inventory drift")
    if WAVE8_LIBYA_CONTRACT_IDS != WAVE8_LIBYA_RESERVED_IDS or WAVE8_LIBYA_HOLDS:
        raise ValueError(f"{_LANE_NAME} disposition partition drift")
    if (
        WAVE8_LIBYA_POINT_QUARANTINE_ADDITIONS
        or WAVE8_LIBYA_COUNTRY_QUARANTINE_ADDITIONS
        or WAVE8_LIBYA_LOCATION_QUARANTINE_REASONS
    ):
        raise ValueError(f"{_LANE_NAME} location policy drift")
    if set(WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS) != {
        "hced-Fada1987-1",
        "hced-Maaten-as-Sarra1987-1",
        "hced-Ouadi Doum1987-1",
    }:
        raise ValueError(f"{_LANE_NAME} existing-release inventory drift")
    if set(WAVE8_LIBYA_IWBD_DISPOSITIONS) != {
        "iwbd-207-80-1651",
        "iwbd-207-80-1654",
    }:
        raise ValueError(f"{_LANE_NAME} IWBD disposition inventory drift")
    if WAVE8_LIBYA_CHADIAN_REBELS_SIGNATURE != WAVE8_CHADIAN_REBELS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} Chadian Rebels signature pin drift")

    used_sources = set(map(str, entity["source_ids"]))
    for candidate_id, contract in WAVE8_LIBYA_CONTRACTS.items():
        reversal = candidate_id in {
            "hced-Aozou1987-1",
            "hced-Zouar1986-1987-1",
        }
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or bool(contract["source_outcome_override"]) != reversal
            or bool(contract["outcome_reversal"]) != reversal
        ):
            raise ValueError(f"{_LANE_NAME} outcome policy drift: {candidate_id}")
        if reversal:
            conflict = contract.get("source_conflict_disposition")
            if not isinstance(conflict, Mapping) or conflict.get("disposition") != (
                "reviewed_outcome_replaces_hced_source_coding"
            ):
                raise ValueError(f"{_LANE_NAME} missing conflict disposition: {candidate_id}")
        elif "source_conflict_disposition" in contract:
            raise ValueError(f"{_LANE_NAME} invented aligned conflict: {candidate_id}")
        actors = {
            *map(str, contract["side_1_entity_ids"]),
            *map(str, contract["side_2_entity_ids"]),
        }
        allowed = {_LIBYA, _CHAD, _FAYA_GUNT}
        if not actors <= allowed or _LIBYA not in actors or _CHAD not in actors:
            raise ValueError(f"{_LANE_NAME} actor drift: {candidate_id}")
        if candidate_id == "hced-Faya Largeau1983-1" and actors != allowed:
            raise ValueError(f"{_LANE_NAME} Faya coalition drift")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or evidence != outcomes
            or not set(outcomes) <= source_ids
        ):
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if check_signature and wave8_libya_audit_signature() != WAVE8_LIBYA_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_libya_queue_contracts(
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
    expected = WAVE8_LIBYA_RESERVED_IDS | set(
        WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS
    )
    if exact_ids != expected or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, disposition in WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS.items():
        if canonical_hced_row_sha256(by_id[candidate_id]) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} existing row changed: {candidate_id}")
    for candidate_id, expected_hash in WAVE8_LIBYA_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("do_not_rate_automatically") is not True:
            raise ValueError(f"{_LANE_NAME} discovery safety flag changed: {candidate_id}")
        if (
            row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("winner_raw")
            not in {row.get("side_1_raw"), row.get("side_2_raw")}
        ):
            raise ValueError(f"{_LANE_NAME} source outcome guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_LIBYA_CONTRACTS,
        WAVE8_LIBYA_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "exact_label_rows": len(exact),
        "existing_release_dispositions": len(
            WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS
        ),
        "outcome_reversals": 2,
    }


def validate_wave8_libya_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
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
        "one_wrong_interval_candidate": int(
            row.get("failure_cases", {}).get("one_wrong_interval_candidate", -1)
        ),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
    }
    if checks != WAVE8_LIBYA_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed: {checks}")
    return {
        "events_touched": checks["events_touched"],
        "one_wrong_interval_candidate": checks["one_wrong_interval_candidate"],
        "sole_blocker_events": checks["sole_blocker_events"],
    }


def _rows_by_id(rows: Iterable[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    result: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        result.setdefault(str(row.get("candidate_id")), []).append(row)
    return result


def _participant_ids(event: Mapping[str, Any]) -> set[str]:
    return {
        str(participant.get("entity_id"))
        for participant in event.get("participants", [])
        if isinstance(participant, Mapping) and participant.get("entity_id")
    }


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


def _row_years(row: Mapping[str, Any]) -> set[int]:
    years: set[int] = set()
    for key in ("year", "end_year", "year_low", "year_high", "year_best", "batyear"):
        try:
            if row.get(key) is not None:
                years.add(int(row[key]))
        except (TypeError, ValueError):
            pass
    for key in ("start_date", "end_date"):
        try:
            if row.get(key):
                years.add(date.fromisoformat(str(row[key])).year)
        except ValueError:
            pass
    return years


_AUDITED_NAME_MARKERS = {
    "aozou": {1987},
    "aouzou": {1987},
    "faya largeau": {1983},
    "zouar": {1986, 1987},
}


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    years = _row_years(row)
    return any(
        f" {marker} " in f" {name} " and bool(years & marker_years)
        for name in _row_names(row)
        for marker, marker_years in _AUDITED_NAME_MARKERS.items()
    )


def validate_wave8_libya_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_libya_queue_contracts(hced_rows)
    validate_wave8_libya_frozen_chadian_rebels()
    iwbd_index = _rows_by_id(iwbd_rows)
    for candidate_id, disposition in WAVE8_LIBYA_IWBD_DISPOSITIONS.items():
        rows = iwbd_index.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(f"{_LANE_NAME} missing IWBD disposition: {candidate_id}")
        row = rows[0]
        if _canonical_object_sha256(row) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} IWBD fingerprint changed: {candidate_id}")
        expected = {
            "name": disposition["expected_name"],
            "start_date": disposition["expected_start_date"],
            "end_date": disposition["expected_end_date"],
            "attacker_raw": disposition["expected_attacker_raw"],
            "defender_raw": disposition["expected_defender_raw"],
            "winner_raw": disposition["expected_winner_raw"],
        }
        if any(row.get(field) != value for field, value in expected.items()):
            raise ValueError(f"{_LANE_NAME} IWBD semantics changed: {candidate_id}")

    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_LIBYA_RESERVED_IDS
        and _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if str(row.get("candidate_id")) not in WAVE8_LIBYA_IWBD_DISPOSITIONS
        and _is_probable_twin(row)
    )
    events = list(existing_events)
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in events
        if event.get("hced_candidate_id") not in WAVE8_LIBYA_CONTRACT_IDS
        and _is_probable_twin(event)
    )
    if hced_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"iwbd={iwbd_twins}, release={release_twins}"
        )

    events_by_id: dict[str, list[Mapping[str, Any]]] = {}
    for event in events:
        events_by_id.setdefault(str(event.get("id")), []).append(event)
    for disposition in WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS.values():
        owner_events = events_by_id.get(str(disposition["owner_event_id"]), [])
        if len(owner_events) != 1:
            raise ValueError(
                f"{_LANE_NAME} missing or duplicate existing IWBD owner"
            )
        event = owner_events[0]
        if (
            event.get("name") != disposition["expected_name"]
            or int(event.get("year", -1)) != disposition["expected_year"]
            or _participant_ids(event) != set(disposition["expected_entity_ids"])
        ):
            raise ValueError(f"{_LANE_NAME} existing IWBD owner drift")

    lane_events = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_LIBYA_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    released_ids = {str(event.get("hced_candidate_id")) for event in lane_events}
    if released_ids not in (set(), set(WAVE8_LIBYA_CONTRACT_IDS)):
        raise ValueError(f"{_LANE_NAME} partial release state")
    if len(lane_events) != len(released_ids):
        raise ValueError(f"{_LANE_NAME} duplicate release ownership")
    return {
        "existing_release_dispositions": 3,
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwbd_dispositions": 2,
        "iwbd_probable_twins": 0,
    }


def install_wave8_libya_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_LIBYA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_libya_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_LIBYA_SOURCES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_libya_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_libya_queue_contracts(hced_rows)
    validate_wave8_libya_frozen_chadian_rebels()
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_LIBYA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )


def wave8_libya_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (*WAVE8_LIBYA_CONTRACTS.values(), *WAVE8_LIBYA_HOLDS.values())
            ).items()
        )
    )


def wave8_libya_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "existing_release_dispositions": len(WAVE8_LIBYA_EXISTING_RELEASE_DISPOSITIONS),
        "holds": 0,
        "iwbd_dispositions": len(WAVE8_LIBYA_IWBD_DISPOSITIONS),
        "new_entities": len(WAVE8_LIBYA_ENTITIES),
        "new_sources": len(WAVE8_LIBYA_SOURCES),
        "newly_rated_events": len(WAVE8_LIBYA_CONTRACTS),
        "outcome_overrides": 2,
        "point_quarantine_additions": 0,
        "promotion_contracts": len(WAVE8_LIBYA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_LIBYA_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_libya_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_libya_counts(),
        "cohorts": wave8_libya_cohort_counts(),
        "final_audit_signature": WAVE8_LIBYA_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_LIBYA_CONTRACT_IDS),
    }


_validate_static()
