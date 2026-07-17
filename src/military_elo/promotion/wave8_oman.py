"""Candidate-keyed audit of HCED's three unresolved ``Oman`` rows.

All three rows fall within the Ya'rubid period, but only two carry outcomes
that survive independent review.  The capture of Muscat in 1650 and the fall
of Fort Jesus after the 1696-1698 siege are retained as tactical Ya'rubid
victories.  The 1652 Zanzibar row remains staged: reviewed accounts disagree
about whether the expedition sacked the settlement or was ultimately repulsed,
and some attribute the action to a local Arab-Swahili coalition rather than a
single Omani force.

The lane opens no generic ``Oman`` alias.  Unknown is never converted into a
draw, no strategic result is inferred, and all three source rows are owned by
fingerprinted promote-or-hold contracts.
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
    "WAVE8_OMAN_CONTRACT_IDS",
    "WAVE8_OMAN_CONTRACTS",
    "WAVE8_OMAN_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_OMAN_ENTITIES",
    "WAVE8_OMAN_FINAL_AUDIT_SIGNATURE",
    "WAVE8_OMAN_FUNNEL_AUDIT",
    "WAVE8_OMAN_HOLD_IDS",
    "WAVE8_OMAN_HOLDS",
    "WAVE8_OMAN_LOCATION_QUARANTINE_REASONS",
    "WAVE8_OMAN_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_OMAN_RESERVED_IDS",
    "WAVE8_OMAN_ROW_HASHES",
    "WAVE8_OMAN_SOURCES",
    "install_wave8_oman_entities",
    "install_wave8_oman_sources",
    "promote_wave8_oman_contracts",
    "validate_wave8_oman_funnel",
    "validate_wave8_oman_integration_dispositions",
    "validate_wave8_oman_queue_contracts",
    "wave8_oman_audit_signature",
    "wave8_oman_cohort_counts",
    "wave8_oman_counts",
    "wave8_oman_metadata",
)


_LANE_NAME = "Wave 8 exact Ya'rubid Oman audit"
_MODULE_OWNER = "military_elo.promotion.wave8_oman"
_EVENT_ID_PREFIX = "hced_wave8_oman_"
_EXACT_LABEL = "oman"
_COHORT = "yarubid_portuguese_wars_1650_1698"

_YARUBID_OMAN = "yarubid_imamate_oman_1624_1742"
_PORTUGAL = "kingdom_portugal"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    evidence_roles: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_OMAN_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_oman_nyuad_state_formation",
        "Slavery in Arabia and East Africa, 1800-1913",
        (
            "https://nyuad.nyu.edu/content/dam/nyuad/academics/divisions/"
            "social-science/working-papers/2021/0066.pdf"
        ),
        "Robert C. Allen / New York University Abu Dhabi",
        "scholarly_working_paper",
        "nyuad_allen_slavery_arabia",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_oman_ona_yarubis",
        "The Ya'rubis and the expulsion of the Portuguese",
        "https://omannews.gov.om/pages/161/show/572",
        "Oman News Agency",
        "official_state_history",
        "oman_news_agency_history",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_oman_iranica_portugal",
        "Portugal i. Relations with Persia in the Early Modern Age (1500-1750)",
        "https://www.iranicaonline.org/articles/portugal-i/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_portugal_persia",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_oman_ucpress_mombasa",
        "Inland from Mombasa: East Africa and the Making of the Indian Ocean World",
        "https://webfiles.ucpress.edu/oa/9780520400498_WEB.pdf",
        "University of California Press",
        "scholarly_monograph",
        "ucpress_inland_from_mombasa",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_oman_unesco_fort_jesus",
        "Fort Jesus, Mombasa: World Heritage nomination dossier",
        "https://whc.unesco.org/uploads/nominations/1295rev.pdf",
        "Republic of Kenya / UNESCO World Heritage Centre",
        "official_heritage_nomination",
        "kenya_unesco_fort_jesus_nomination",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_oman_indian_ocean_history",
        "Indian Ocean in World History: Historical Background",
        (
            "https://www.indianoceanhistory.org/An-Ocean-of-Paper/"
            "Historical-Background.aspx"
        ),
        "Indian Ocean in World History educational project",
        "scholarly_educational_synthesis",
        "indian_ocean_world_history_project",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_oman_kunstkamera_zanzibar",
        "From Oases to the Cities: The Origin of Urbanization in Oman and Zanzibar",
        (
            "https://etnografia.kunstkamera.ru/files/etnografia_journal/"
            "2018_02/as_salmi.pdf"
        ),
        "Peter the Great Museum of Anthropology and Ethnography / Etnografia",
        "peer_reviewed_journal_article",
        "kunstkamera_etnografia_al_salmi",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_OMAN_SOURCES}


# Empty aliases are deliberate.  This polity can be reached only through the
# exact contracts below, never by a timeless Oman label.
WAVE8_OMAN_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _YARUBID_OMAN,
        "name": "Ya'rubid Imamate of Oman",
        "kind": "ibadi_imamate",
        "start_year": 1624,
        "end_year": 1742,
        "region": "Oman and the western Indian Ocean",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The time-bounded Ya'rubid state begins with Nasir bin Murshid's "
            "election in 1624 and ends with the dynasty's loss of effective rule "
            "amid the 1742 succession crisis. Only the two fingerprinted "
            "Portuguese-war events below activate its Elo. No rating is inherited "
            "by earlier Omani imamates, the later Al Bu Sa'id state, modern Oman, "
            "or any East African successor or governor."
        ),
        "source_ids": [
            "wave8_oman_nyuad_state_formation",
            "wave8_oman_ona_yarubis",
        ],
    },
)


WAVE8_OMAN_ROW_HASHES: dict[str, str] = {
    "hced-Mombasa1696-1698-1": (
        "186f90eabd04f5c19481530bec32e7845573112766c9c9f9ab4a239e0a73f7f8"
    ),
    "hced-Muscat1650-1": (
        "a32f9a69ac4985d50dd0db2bd3bb7ddcb07150f5a11aee6d746e1b99d5f1218d"
    ),
    "hced-Zanzibar1652-1": (
        "93463f26ff2a4649a44471c1e0b185485bbc86ec905c54f98bffed7035fd7bf9"
    ),
}

# The modern Imamate Revolt row is already owned by the generic label pass and
# resolves to the time-valid Al Bu Sa'id candidate.  Pin it as an explicit
# out-of-cohort row so this early-modern audit cannot silently absorb it.
_OUT_OF_COHORT_ROW_HASHES: dict[str, str] = {
    "hced-Rustaq1955-1": (
        "1d91283feb7f04ca10183ce4b5d32b9b731947d7e45143fdf6bea836b20a7755"
    ),
}


WAVE8_OMAN_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": ["clio_om_busaidi_imamate_1_1744_c23501c3"],
    "event_candidate_id_sha256": (
        "34e19a1aa5fd593d47f4ce723a29ff10690e27d7bbce842026567c86f471129e"
    ),
    "events_touched": 3,
    "label": "oman",
    "one_wrong_interval_candidate": 3,
    "rated_counterpart_entities": 1,
    "sole_blocker_events": 3,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 3,
}


def _canonical(
    name: str,
    year_low: int,
    year_high: int | None = None,
    *,
    date_precision: str = "year",
    granularity: str = "engagement",
) -> dict[str, Any]:
    high = year_low if year_high is None else year_high
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{high}",
        "date_precision": date_precision,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": high,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_OMAN_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "side_1_entity_ids": [_YARUBID_OMAN],
        "side_2_entity_ids": [_PORTUGAL],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate_limited",
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
        "actor_override": "candidate_keyed_yarubid_imamate",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_OMAN_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Muscat1650-1": _contract(
        "hced-Muscat1650-1",
        _canonical(
            "Capture of Muscat",
            1650,
            granularity="siege_and_capture",
        ),
        {
            "wave8_oman_iranica_portugal",
            "wave8_oman_ona_yarubis",
        },
        {
            "wave8_oman_iranica_portugal",
            "wave8_oman_ona_yarubis",
        },
        (
            "The official Omani history and Encyclopaedia Iranica independently "
            "identify Sultan bin Saif's Ya'rubid force as expelling the "
            "Portuguese from Muscat in 1650. Only the tactical capture is rated."
        ),
        confidence=0.99,
    ),
    "hced-Mombasa1696-1698-1": _contract(
        "hced-Mombasa1696-1698-1",
        _canonical(
            "Siege of Fort Jesus",
            1696,
            1698,
            date_precision="year_range",
            granularity="siege",
        ),
        {
            "wave8_oman_ucpress_mombasa",
            "wave8_oman_unesco_fort_jesus",
        },
        {
            "wave8_oman_ucpress_mombasa",
            "wave8_oman_unesco_fort_jesus",
        },
        (
            "The Kenya-UNESCO dossier and the University of California Press "
            "history independently record the 1696-1698 Omani siege ending with "
            "the fall of Fort Jesus. No later East African sovereignty is inferred."
        ),
        confidence=0.99,
    ),
}


WAVE8_OMAN_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Zanzibar1652-1": {
        "raw_row_sha256": WAVE8_OMAN_ROW_HASHES["hced-Zanzibar1652-1"],
        "canonical_event": _canonical(
            "Zanzibar expedition",
            1652,
            granularity="raiding_expedition",
        ),
        "cohort": _COHORT,
        "disposition": "hold",
        "hold_category": "contradictory_outcome_and_actor_evidence",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_granularity": "raiding_expedition",
        "evidence_refs": [
            "wave8_oman_indian_ocean_history",
            "wave8_oman_kunstkamera_zanzibar",
        ],
        "hold_reason": (
            "One reviewed synthesis says the Ya'rubid expedition sacked Zanzibar, "
            "while the peer-reviewed account says the attack killed Portuguese "
            "defenders but was ultimately repulsed; other histories foreground a "
            "local Arab-Swahili uprising. HCED's unqualified Omani victory is "
            "therefore not promoted, and the unknown result is not a draw."
        ),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "review_hold_owner",
        },
    },
}


WAVE8_OMAN_CONTRACT_IDS = frozenset(WAVE8_OMAN_CONTRACTS)
WAVE8_OMAN_HOLD_IDS = frozenset(WAVE8_OMAN_HOLDS)
WAVE8_OMAN_RESERVED_IDS = frozenset(
    {*WAVE8_OMAN_CONTRACT_IDS, *WAVE8_OMAN_HOLD_IDS}
)
WAVE8_OMAN_POINT_QUARANTINE_ADDITIONS = WAVE8_OMAN_CONTRACT_IDS
WAVE8_OMAN_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_OMAN_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "HCED supplies an unexplained city centroid rather than an "
            "independently verified battlefield or siege-footprint point; retain "
            "the provenance-bound modern jurisdiction and withhold geometry."
        ),
        "evidence_refs": sorted(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_OMAN_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_OMAN_CONTRACTS,
        "entities": WAVE8_OMAN_ENTITIES,
        "funnel": WAVE8_OMAN_FUNNEL_AUDIT,
        "holds": WAVE8_OMAN_HOLDS,
        "location_reasons": WAVE8_OMAN_LOCATION_QUARANTINE_REASONS,
        "out_of_cohort_row_hashes": _OUT_OF_COHORT_ROW_HASHES,
        "row_hashes": WAVE8_OMAN_ROW_HASHES,
        "sources": WAVE8_OMAN_SOURCES,
    }


def wave8_oman_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_OMAN_FINAL_AUDIT_SIGNATURE = (
    "5cdfe2633a6bd2bbba482b4e92054b708588037e518c88bbb29913206864c83b"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = {str(entity["id"]) for entity in WAVE8_OMAN_ENTITIES}
    if len(source_ids) != len(WAVE8_OMAN_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if entity_ids != {_YARUBID_OMAN}:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_OMAN_CONTRACT_IDS & WAVE8_OMAN_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_OMAN_RESERVED_IDS != set(WAVE8_OMAN_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_OMAN_POINT_QUARANTINE_ADDITIONS != WAVE8_OMAN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_OMAN_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_OMAN_LOCATION_QUARANTINE_REASONS) != WAVE8_OMAN_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    entity = WAVE8_OMAN_ENTITIES[0]
    if entity["aliases"] or entity["predecessors"]:
        raise ValueError(f"{_LANE_NAME} generic alias or inheritance opened")
    if (entity["start_year"], entity["end_year"]) != (1624, 1742):
        raise ValueError(f"{_LANE_NAME} identity window drift")
    if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
        raise ValueError(f"{_LANE_NAME} continuity inheritance guard drift")
    if not _is_sorted_unique(entity["source_ids"]):
        raise ValueError(f"{_LANE_NAME} entity source order drift")

    used_sources = set(map(str, entity["source_ids"]))
    expected_sides = ([_YARUBID_OMAN], [_PORTUGAL])
    for candidate_id, contract in WAVE8_OMAN_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or (
                contract["side_1_entity_ids"],
                contract["side_2_entity_ids"],
            )
            != expected_sides
        ):
            raise ValueError(f"{_LANE_NAME} outcome or actor drift: {candidate_id}")
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
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)

    hold = WAVE8_OMAN_HOLDS["hced-Zanzibar1652-1"]
    if (
        hold["disposition"] != "hold"
        or hold["hold_category"] != "contradictory_outcome_and_actor_evidence"
        or hold["result_type"] != "unknown"
        or hold["unknown_is_never_draw"] is not True
    ):
        raise ValueError(f"{_LANE_NAME} Zanzibar hold drift")
    hold_sources = list(map(str, hold["evidence_refs"]))
    if not _is_sorted_unique(hold_sources) or not set(hold_sources) <= source_ids:
        raise ValueError(f"{_LANE_NAME} hold evidence drift")
    used_sources.update(hold_sources)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_oman_audit_signature() != WAVE8_OMAN_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_oman_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact_all = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _EXACT_LABEL
        or normalize_label(row.get("side_2_raw")) == _EXACT_LABEL
    ]
    exact = [
        row
        for row in exact_all
        if int(row.get("year_low")) <= 1742 and int(row.get("year_high")) >= 1624
    ]
    out_of_cohort = [row for row in exact_all if row not in exact]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_OMAN_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    outside_by_id = {str(row.get("candidate_id")): row for row in out_of_cohort}
    if set(outside_by_id) != set(_OUT_OF_COHORT_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} out-of-cohort exact-label inventory changed")
    for candidate_id, expected_hash in _OUT_OF_COHORT_ROW_HASHES.items():
        if canonical_hced_row_sha256(outside_by_id[candidate_id]) != expected_hash:
            raise ValueError(
                f"{_LANE_NAME} out-of-cohort row fingerprint changed: {candidate_id}"
            )
    by_id = {str(row["candidate_id"]): row for row in exact}
    expected_years = {
        "hced-Mombasa1696-1698-1": (1696, 1697, 1698),
        "hced-Muscat1650-1": (1650, 1650, 1650),
        "hced-Zanzibar1652-1": (1652, 1652, 1652),
    }
    for candidate_id, expected_hash in WAVE8_OMAN_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            int(row["year_low"]),
            int(row["year_best"]),
            int(row["year_high"]),
        ) != expected_years[candidate_id]:
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if (
            row.get("side_1_raw") != "Oman"
            or row.get("side_2_raw") != "Portugal"
            or row.get("winner_raw") != "Oman"
            or row.get("loser_raw") != "Portugal"
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
        ):
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_OMAN_CONTRACTS,
        WAVE8_OMAN_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "exact_label_rows": len(exact_all),
        "out_of_cohort_exact_label_rows": len(out_of_cohort),
        "target_exact_label_rows": len(exact),
    }


def validate_wave8_oman_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    matches = [
        row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL
    ]
    if len(matches) != 1:
        raise ValueError(f"{_LANE_NAME} expected exactly one Oman funnel row")
    row = matches[0]
    actual = {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "label": str(row.get("label")),
        "one_wrong_interval_candidate": int(
            row.get("failure_cases", {}).get("one_wrong_interval_candidate", -1)
        ),
        "rated_counterpart_entities": int(row.get("rated_counterpart_entities", -1)),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, row.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
    }
    if actual != WAVE8_OMAN_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pin changed: {actual}")
    return {
        "events_touched": actual["events_touched"],
        "sole_blocker_events": actual["sole_blocker_events"],
        "unresolved_side_attempts": actual["unresolved_side_attempts"],
        "one_wrong_interval_candidate": actual["one_wrong_interval_candidate"],
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


_DUPLICATE_ALIASES: dict[int, set[str]] = {
    1650: {"Capture of Muscat", "Muscat", "Siege of Muscat"},
    1696: {
        "Fort Jesus",
        "Mombasa",
        "Siege of Fort Jesus",
        "Siege of Mombasa",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (year, normalize_label(alias))
    for year, aliases in _DUPLICATE_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_oman_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_oman_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_OMAN_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_OMAN_CONTRACT_IDS
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


def install_wave8_oman_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_OMAN_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_oman_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_OMAN_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_OMAN_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_OMAN_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_oman_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_oman_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_OMAN_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_oman_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (*WAVE8_OMAN_CONTRACTS.values(), *WAVE8_OMAN_HOLDS.values())
            ).items()
        )
    )


def wave8_oman_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": len(WAVE8_OMAN_HOLDS),
        "new_entities": len(WAVE8_OMAN_ENTITIES),
        "new_sources": len(WAVE8_OMAN_SOURCES),
        "newly_rated_events": len(WAVE8_OMAN_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(WAVE8_OMAN_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_OMAN_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_OMAN_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_oman_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_oman_counts(),
        "cohorts": wave8_oman_cohort_counts(),
        "final_audit_signature": WAVE8_OMAN_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_OMAN_CONTRACT_IDS),
        "hold_candidate_ids": sorted(WAVE8_OMAN_HOLD_IDS),
    }


_validate_static()
