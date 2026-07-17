"""Candidate-keyed audit of HCED's nine Arcot-related rows.

Three rows identify the recognized Nawabship of the Carnatic as a unique
belligerent: Dost Ali's army at Damalcherry in 1740, Anwaruddin's army at
St. Thome in 1746, and Muhammad Ali's Arcot garrison in 1780.  Three rows stay
staged because they collapse rival succession claimants or coalition sides.
Three existing United Kingdom-France crosswalk events remain unchanged and do
not gain a Carnatic participant.  No generic ``Arcot`` alias is opened.
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
    "WAVE8_CARNATIC_AUDITED_IDS",
    "WAVE8_CARNATIC_CONTRACT_IDS",
    "WAVE8_CARNATIC_CONTRACTS",
    "WAVE8_CARNATIC_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_CARNATIC_ENTITIES",
    "WAVE8_CARNATIC_FINAL_AUDIT_SIGNATURE",
    "WAVE8_CARNATIC_FUNNEL_AUDIT",
    "WAVE8_CARNATIC_HOLD_IDS",
    "WAVE8_CARNATIC_HOLDS",
    "WAVE8_CARNATIC_LEGACY_IDS",
    "WAVE8_CARNATIC_LOCATION_QUARANTINE_REASONS",
    "WAVE8_CARNATIC_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_CARNATIC_RESERVED_IDS",
    "WAVE8_CARNATIC_ROW_HASHES",
    "WAVE8_CARNATIC_SOURCES",
    "install_wave8_carnatic_entities",
    "install_wave8_carnatic_sources",
    "promote_wave8_carnatic_contracts",
    "validate_wave8_carnatic_funnel",
    "validate_wave8_carnatic_integration_dispositions",
    "validate_wave8_carnatic_queue_contracts",
    "wave8_carnatic_audit_signature",
    "wave8_carnatic_cohort_counts",
    "wave8_carnatic_counts",
    "wave8_carnatic_metadata",
)


_LANE_NAME = "Wave 8 exact Carnatic actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_carnatic"
_EVENT_ID_PREFIX = "hced_wave8_carnatic_"
_EXACT_LABELS = frozenset({"arcot", "nawab of arcot"})
_ARCOT_FIELDS = ("side_1_raw", "side_2_raw", "winner_raw", "loser_raw")

_CARNATIC = "clio_in_carnatic_sul_1713_80e63d27"
_FRANCE = "kingdom_france"
_MARATHAS = "maratha_confederacy"
_MYSORE = "kingdom_mysore"
_LEGACY_EVENT_IDS: dict[str, str] = {
    "hced-Arcot1751-1": "hced_hced_arcot1751_1",
    "hced-Seringham1752-1": "hced_hced_seringham1752_1",
    "hced-Tiruvadi1750-1": "hced_hced_tiruvadi1750_1",
}


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
        "accessed": "2026-07-17",
        "source_family_id": source_family_id,
        "evidence_roles": list(evidence_roles),
    }


WAVE8_CARNATIC_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_carnatic_goi_imperial_gazetteer",
        "Imperial Gazetteer of India, Provincial Series: Madras II",
        "https://ignca.gov.in/Asi_data/30077.pdf",
        "Government of India / Indira Gandhi National Centre for the Arts",
        "official_historical_gazetteer",
        "imperial_gazetteer_madras_provincial_series_1908",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_carnatic_tn_arcot_history",
        "Brief History of Arcot",
        (
            "https://www.tnurbantree.tn.gov.in/wp-content/uploads/sites/113/"
            "2020/08/briefhistory-PB-Arcot.pdf"
        ),
        "Government of Tamil Nadu, Arcot Municipality",
        "official_local_history",
        "tamil_nadu_arcot_municipality_history",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_carnatic_hayavadana_mysore",
        "C. Hayavadana Rao, History of Mysore, Volume II, Chapter IV",
        (
            "https://statearchives.karnataka.gov.in/gazetteer/public/storage/"
            "pdf-files/pdf/History%20of%20Mysore.%20Vol-II%20by%20C.%20"
            "Hayavadana%20Rao-1945/Chpt%20-%204.pdf"
        ),
        "Karnataka State Archives and Gazetteer Department",
        "official_state_history",
        "hayavadana_rao_history_mysore_1945",
        ["outcome"],
    ),
    _source(
        "wave8_carnatic_orme_transactions",
        "Robert Orme, A History of the Military Transactions of the British Nation in Indostan",
        (
            "https://www.tamildigitallibrary.in/admin/assets/book/"
            "TVA_BOK_0047482/TVA_BOK_0047482_military_transactions_of_"
            "British_Nation_in_Indostan_1745.pdf"
        ),
        "Tamil Digital Library; eighteenth-century original",
        "near_contemporary_narrative",
        "orme_military_transactions_indostan",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_carnatic_alagappa_tamil_nadu",
        "History of Tamil Nadu (Beginning to 1947 AD)",
        (
            "https://mis.alagappauniversity.ac.in/siteAdmin/dde-admin/uploads/"
            "5/__UG_B.A._History%20%28English%29_108%2051_History%20of%20"
            "Tamil%20Nadu%20%28Beginning%20to%201947%20AD%29_BA%20"
            "%28History%29_9683.pdf"
        ),
        "Alagappa University",
        "university_history_text",
        "alagappa_history_tamil_nadu",
        ["outcome"],
    ),
    _source(
        "wave8_carnatic_marshman_chapter14",
        "John Clark Marshman, History of India, Chapter XIV",
        "https://www.ibiblio.org/britishraj/Marshman1/chapter14.html",
        "ibiblio public-domain British Raj collection",
        "historical_monograph",
        "marshman_history_india",
        ["outcome"],
    ),
    _source(
        "wave8_carnatic_britannica_arcot",
        "1911 Encyclopaedia Britannica: Arcot",
        (
            "https://en.wikisource.org/wiki/"
            "1911_Encyclop%C3%A6dia_Britannica/Arcot"
        ),
        "Encyclopaedia Britannica / Wikisource transcription",
        "edited_reference_work",
        "britannica_1911_arcot",
        ["outcome"],
    ),
    _source(
        "wave8_carnatic_gingee_context",
        "J. Rickard, Battle of Gingee, 11 September 1750",
        "https://www.historyofwar.org/articles/battles_gingee_1750.html",
        "HistoryOfWar.org",
        "historical_reference",
        "rickard_gingee_1750",
        ["identity_boundary_or_context_reference"],
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_CARNATIC_SOURCES}


# Reuse and curate the matching Cliopatria registry identity.  The empty alias
# list is deliberate: Arcot labels remain available only to fingerprinted rows.
WAVE8_CARNATIC_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _CARNATIC,
        "name": "Carnatic Sultanate (Nawabship of Arcot)",
        "kind": "nawabship",
        "start_year": 1713,
        "end_year": 1802,
        "region": "South India",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Curated from the matching time-bounded Cliopatria candidate. The "
            "identity represents the Nawabship of the Carnatic across ordinary "
            "ruler succession, consistent with the project's treatment of other "
            "state polities; rival claimants are not merged into a battle side. "
            "Only fingerprinted, candidate-keyed events may use this identity. "
            "Neither 'Arcot' nor 'Nawab of Arcot' is opened as a global alias, "
            "and predecessors or successors inherit no Elo."
        ),
        "source_ids": [
            "cliopatria_v020",
            "wave8_carnatic_goi_imperial_gazetteer",
            "wave8_carnatic_tn_arcot_history",
        ],
    },
)


WAVE8_CARNATIC_ROW_HASHES: dict[str, str] = {
    "hced-Ambur1749-1": "a8d44dd1b958137fb22ce39f82ab79d99d89e6649c65d1a56319a6a9219d6fc6",
    "hced-Arcot1751-1": "4fb3a082bcb6452871af02828f681ad3e5b2eed0656e3d2b992981feda57170e",
    "hced-Arcot1780-1": "7c409b89a35938fab38be2a2b7ae7495667bfd0e150b4816a5fa50e24598e7ac",
    "hced-Damalcherry Pass1740-1": "3210dae7f4780428a8f49a0e65929ee7171e06ff90b936523dfa217ec59999ba",
    "hced-Gingee1750-1": "eee4c658041f717608a9d3c67b576aeb37d4ca3c8ddd94f040866dbb1e12fb4b",
    "hced-Seringham1752-1": "c996b8b1d8e11bc4c4ec7b7b643a153f4df3ab822dd0b760b01f5f9277796199",
    "hced-St Thome1746-1": "5b0d21a19bceac91713920ceb2b2be96c6a09cf03179247124e9ac0a76658ef8",
    "hced-Tiruvadi1750-1": "dab2d532966a0b0b195c8bc5a9c5fe885ece8e1750c3e239b42bd980189b3cbb",
    "hced-Trichinopoly1740-1741-1": "1456aa1ec2335f5c284becdf3e2cf37f2085ec6c8c866571ef0ffb199226d998",
}

WAVE8_CARNATIC_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "arcot": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "94bd58ae8bd79cc4c94249054916c3b0e6b29969334ccaeb08606353193614b5"
        ),
        "events_touched": 3,
        "sole_blocker_events": 3,
        "zero_time_valid_candidates": 3,
    },
    "nawab of arcot": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "a6a1227a8dc7c570158391963de8ae723e15a25d960ad55d0b4f8ffe6839bcf5"
        ),
        "events_touched": 2,
        "sole_blocker_events": 2,
        "zero_time_valid_candidates": 2,
    },
}


def _canonical(name: str, low: int, high: int, granularity: str) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{low}:{high}",
        "date_precision": "year" if low == high else "year_range",
        "date_text": str(low) if low == high else f"{low}-{high}",
        "granularity": granularity,
        "name": name,
        "year_low": low,
        "year_high": high,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    opponent_id: str,
    cohort: str,
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(map(str, outcome_source_ids))
    return {
        "raw_row_sha256": WAVE8_CARNATIC_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": [opponent_id],
        "side_2_entity_ids": [_CARNATIC],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate",
        "confidence": confidence,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_carnatic_nawabship",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_CARNATIC_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Damalcherry Pass1740-1": _contract(
        "hced-Damalcherry Pass1740-1",
        _canonical(
            "Battle of Damalcherry Pass",
            1740,
            1740,
            "single_land_battle_at_damalcheruvu_pass",
        ),
        _MARATHAS,
        "recognized_carnatic_state_forces",
        {
            "wave8_carnatic_hayavadana_mysore",
            "wave8_carnatic_tn_arcot_history",
        },
        (
            "Tamil Nadu's official Arcot history identifies Dost Ali, Nawab of "
            "the Carnatic, as the defeated and killed defender at Damalcherry; "
            "Hayavadana Rao independently records the pass, actors, and Maratha "
            "victory. The contract rates only that battle."
        ),
        confidence=0.95,
    ),
    "hced-St Thome1746-1": _contract(
        "hced-St Thome1746-1",
        _canonical(
            "Battle of St. Thome",
            1746,
            1746,
            "single_land_battle_on_the_adyar",
        ),
        _FRANCE,
        "recognized_carnatic_state_forces",
        {
            "wave8_carnatic_alagappa_tamil_nadu",
            "wave8_carnatic_orme_transactions",
        },
        (
            "Orme's near-contemporary narrative and Alagappa University's "
            "history independently identify Mahfuz Khan's army, sent by Nawab "
            "Anwaruddin, as defeated by the French at St. Thome. No result for "
            "the enclosing Carnatic War is inferred."
        ),
        confidence=0.95,
    ),
    "hced-Arcot1780-1": _contract(
        "hced-Arcot1780-1",
        _canonical(
            "Siege and Capture of Arcot",
            1780,
            1780,
            "siege_and_capitulation_of_the_nawabs_arcot_garrison",
        ),
        _MYSORE,
        "recognized_carnatic_state_forces",
        {
            "wave8_carnatic_britannica_arcot",
            "wave8_carnatic_marshman_chapter14",
        },
        (
            "Marshman identifies the fort as the Nawab's, its stores and "
            "commandant, and the garrison's capitulation to Hyder Ali; the 1911 "
            "Britannica independently records Hyder's 1780 capture and tenure. "
            "The event is not recoded as a British defeat."
        ),
        confidence=0.92,
    ),
}


def _hold(
    candidate_id: str,
    cohort: str,
    reason_code: str,
    evidence_refs: Iterable[str],
    audit_note: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_CARNATIC_ROW_HASHES[candidate_id],
        "cohort": cohort,
        "disposition": "hold",
        "reason_code": reason_code,
        "evidence_refs": sorted(map(str, evidence_refs)),
        "audit_note": audit_note,
    }


WAVE8_CARNATIC_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Trichinopoly1740-1741-1": _hold(
        "hced-Trichinopoly1740-1741-1",
        "succession_and_coalition_holds",
        "arcot_label_collapses_chanda_sahib_and_safdar_ali",
        {"wave8_carnatic_goi_imperial_gazetteer"},
        (
            "Chanda Sahib held Trichinopoly under a separate title and was "
            "removed after Dost Ali's death amid a succession struggle. The "
            "bare 'Arcot' label cannot uniquely assign his force to the generic "
            "Nawabship without merging rival political actors."
        ),
    ),
    "hced-Gingee1750-1": _hold(
        "hced-Gingee1750-1",
        "succession_and_coalition_holds",
        "rival_carnatic_claimants_on_opposing_sides",
        {
            "wave8_carnatic_gingee_context",
            "wave8_carnatic_orme_transactions",
        },
        (
            "The defeated troops belonged to British-backed claimant Muhammad "
            "Ali while the French fought for rival claimant Chanda Sahib. A "
            "generic Carnatic identity would therefore represent both conflict "
            "sides and is deliberately withheld."
        ),
    ),
    "hced-Ambur1749-1": _hold(
        "hced-Ambur1749-1",
        "succession_and_coalition_holds",
        "historically_contradictory_coalition_alignment",
        {
            "wave8_carnatic_gingee_context",
            "wave8_carnatic_orme_transactions",
        },
        (
            "HCED places France in the losing Arcot composite even though "
            "French support belonged to Chanda Sahib and Muzaffar Jang's "
            "victorious coalition. No side is reversed or invented."
        ),
    ),
}

WAVE8_CARNATIC_CONTRACT_IDS = frozenset(WAVE8_CARNATIC_CONTRACTS)
WAVE8_CARNATIC_HOLD_IDS = frozenset(WAVE8_CARNATIC_HOLDS)
WAVE8_CARNATIC_LEGACY_IDS = frozenset(_LEGACY_EVENT_IDS)
WAVE8_CARNATIC_RESERVED_IDS = frozenset(
    {*WAVE8_CARNATIC_CONTRACT_IDS, *WAVE8_CARNATIC_HOLD_IDS}
)
WAVE8_CARNATIC_AUDITED_IDS = frozenset(
    {*WAVE8_CARNATIC_RESERVED_IDS, *WAVE8_CARNATIC_LEGACY_IDS}
)
WAVE8_CARNATIC_POINT_QUARANTINE_ADDITIONS = WAVE8_CARNATIC_CONTRACT_IDS
WAVE8_CARNATIC_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_CARNATIC_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the named place and modern country "
            "but do not independently verify HCED's exact coordinate; retain "
            "the country assertion and withhold the point."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_CARNATIC_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "audited_ids": sorted(WAVE8_CARNATIC_AUDITED_IDS),
        "contracts": WAVE8_CARNATIC_CONTRACTS,
        "entities": WAVE8_CARNATIC_ENTITIES,
        "funnel": WAVE8_CARNATIC_FUNNEL_AUDIT,
        "holds": WAVE8_CARNATIC_HOLDS,
        "legacy_ids": sorted(WAVE8_CARNATIC_LEGACY_IDS),
        "location_reasons": WAVE8_CARNATIC_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_CARNATIC_ROW_HASHES,
        "sources": WAVE8_CARNATIC_SOURCES,
    }


def wave8_carnatic_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_CARNATIC_FINAL_AUDIT_SIGNATURE = (
    "9f0fb639464838660fdb1293803e473419f51dd87fdb1a81aceff74b189778b5"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = {str(entity["id"]) for entity in WAVE8_CARNATIC_ENTITIES}
    if len(source_ids) != len(WAVE8_CARNATIC_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if entity_ids != {_CARNATIC}:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_CARNATIC_CONTRACT_IDS & WAVE8_CARNATIC_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_CARNATIC_RESERVED_IDS & WAVE8_CARNATIC_LEGACY_IDS:
        raise ValueError(f"{_LANE_NAME} reserved/legacy overlap")
    if WAVE8_CARNATIC_AUDITED_IDS != set(WAVE8_CARNATIC_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} audited inventory drift")
    if WAVE8_CARNATIC_POINT_QUARANTINE_ADDITIONS != WAVE8_CARNATIC_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_CARNATIC_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_CARNATIC_LOCATION_QUARANTINE_REASONS) != WAVE8_CARNATIC_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    entity = WAVE8_CARNATIC_ENTITIES[0]
    if entity["aliases"] or (entity["start_year"], entity["end_year"]) != (1713, 1802):
        raise ValueError(f"{_LANE_NAME} identity boundary or alias drift")
    if normalize_label(entity["name"]) in _EXACT_LABELS:
        raise ValueError(f"{_LANE_NAME} generic Arcot label opened")
    if not _is_sorted_unique(entity["source_ids"]):
        raise ValueError(f"{_LANE_NAME} entity evidence order drift")

    used_sources = set(map(str, entity["source_ids"])) & source_ids
    allowed_opponents = {_FRANCE, _MARATHAS, _MYSORE}
    observed_opponents: set[str] = set()
    for candidate_id, contract in WAVE8_CARNATIC_CONTRACTS.items():
        if contract["disposition"] != "promote" or contract["result_type"] != "win":
            raise ValueError(f"{_LANE_NAME} disposition drift: {candidate_id}")
        if contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} winner-side drift: {candidate_id}")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} outcome override drift: {candidate_id}")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if len(side_1) != 1 or side_2 != [_CARNATIC] or side_1[0] not in allowed_opponents:
            raise ValueError(f"{_LANE_NAME} exact actor drift: {candidate_id}")
        observed_opponents.add(side_1[0])
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence order drift: {candidate_id}")
        if set(outcomes) != set(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        low = int(contract["canonical_event"]["year_low"])
        high = int(contract["canonical_event"]["year_high"])
        if not (1713 <= low <= high <= 1802):
            raise ValueError(f"{_LANE_NAME} identity-window drift: {candidate_id}")
        used_sources.update(evidence)
    if observed_opponents != allowed_opponents:
        raise ValueError(f"{_LANE_NAME} opponent inventory drift")

    for candidate_id, hold in WAVE8_CARNATIC_HOLDS.items():
        if hold["disposition"] != "hold" or not hold["reason_code"]:
            raise ValueError(f"{_LANE_NAME} hold drift: {candidate_id}")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} hold evidence drift: {candidate_id}")
        used_sources.update(evidence)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_carnatic_audit_signature() != WAVE8_CARNATIC_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def _mentions_arcot(row: Mapping[str, Any]) -> bool:
    return any("arcot" in normalize_label(row.get(key)) for key in _ARCOT_FIELDS)


def validate_wave8_carnatic_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    audited = [row for row in hced_rows if _mentions_arcot(row)]
    audited_ids = {str(row.get("candidate_id")) for row in audited}
    if audited_ids != WAVE8_CARNATIC_AUDITED_IDS or len(audited) != len(audited_ids):
        raise ValueError(f"{_LANE_NAME} Arcot-related inventory changed")
    by_id = {str(row["candidate_id"]): row for row in audited}
    for candidate_id, expected_hash in WAVE8_CARNATIC_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("winner_raw") not in {row.get("side_1_raw"), row.get("side_2_raw")}:
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True:
            raise ValueError(f"{_LANE_NAME} complete-outcome guard changed: {candidate_id}")
    for candidate_id in WAVE8_CARNATIC_CONTRACT_IDS:
        if by_id[candidate_id].get("massacre_raw") != "No":
            raise ValueError(f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_CARNATIC_CONTRACTS,
        WAVE8_CARNATIC_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "arcot_related_rows": len(audited),
        "legacy_crosswalk_rows": len(WAVE8_CARNATIC_LEGACY_IDS),
        "reserved_hced_rows": counts["reviewed_hced_rows"],
        "reviewed_hced_rows": len(WAVE8_CARNATIC_AUDITED_IDS),
    }


def validate_wave8_carnatic_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    actual: dict[str, dict[str, Any]] = {}
    for row in funnel.get("labels", []):
        label = str(row.get("label"))
        if label not in _EXACT_LABELS:
            continue
        actual[label] = {
            "candidate_ids": list(map(str, row.get("candidate_ids", []))),
            "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
            "events_touched": int(row.get("events_touched", -1)),
            "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
            "zero_time_valid_candidates": int(
                row.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
            ),
        }
    if actual != WAVE8_CARNATIC_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed: {actual}")
    return {
        "labels": len(actual),
        "events_touched": sum(row["events_touched"] for row in actual.values()),
        "sole_blocker_events": sum(
            row["sole_blocker_events"] for row in actual.values()
        ),
        "zero_time_valid_candidates": sum(
            row["zero_time_valid_candidates"] for row in actual.values()
        ),
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


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Damalcherry Pass1740-1": {
        "Battle of Damalcherry Pass",
        "Damalcherry Pass",
        "Damalcheruvu",
        "Damalcheruvu Pass",
    },
    "hced-St Thome1746-1": {
        "Adyar",
        "Battle of Adyar",
        "Battle of St Thome",
        "Battle of St. Thome",
        "St Thome",
    },
    "hced-Arcot1780-1": {
        "Arcot",
        "Capture of Arcot",
        "Siege and Capture of Arcot",
        "Siege of Arcot",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(WAVE8_CARNATIC_CONTRACTS[candidate_id]["canonical_event"]["year_low"]),
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


def validate_wave8_carnatic_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_carnatic_queue_contracts(hced_rows)
    events = list(existing_events)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_CARNATIC_AUDITED_IDS
        and _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in events
        if event.get("hced_candidate_id") not in WAVE8_CARNATIC_AUDITED_IDS
        and _is_probable_twin(event)
    )
    if hced_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"iwbd={iwbd_twins}, release={release_twins}"
        )

    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for event in events:
        candidate_id = event.get("hced_candidate_id")
        if isinstance(candidate_id, str):
            by_candidate.setdefault(candidate_id, []).append(event)
    held_promoted = sorted(WAVE8_CARNATIC_HOLD_IDS & set(by_candidate))
    if held_promoted:
        raise ValueError(f"{_LANE_NAME} held rows were promoted: {held_promoted}")
    for candidate_id in WAVE8_CARNATIC_CONTRACT_IDS:
        if len(by_candidate.get(candidate_id, [])) != 1:
            raise ValueError(f"{_LANE_NAME} promoted disposition drift: {candidate_id}")

    for candidate_id, event_id in _LEGACY_EVENT_IDS.items():
        legacy = by_candidate.get(candidate_id, [])
        if len(legacy) != 1 or legacy[0].get("id") != event_id:
            raise ValueError(f"{_LANE_NAME} legacy event drift: {candidate_id}")
        legacy_actor_ids = {
            str(participant.get("entity_id"))
            for participant in legacy[0].get("participants", [])
        }
        if legacy_actor_ids != {"united_kingdom", _FRANCE}:
            raise ValueError(f"{_LANE_NAME} legacy actor drift: {candidate_id}")
        if _CARNATIC in legacy_actor_ids:
            raise ValueError(f"{_LANE_NAME} legacy Carnatic actor leak: {candidate_id}")
    return {
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwbd_probable_twins": 0,
        "legacy_crosswalk_events_preserved": len(WAVE8_CARNATIC_LEGACY_IDS),
    }


def install_wave8_carnatic_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_CARNATIC_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_carnatic_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_CARNATIC_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_CARNATIC_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_CARNATIC_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_carnatic_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_carnatic_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_CARNATIC_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_carnatic_cohort_counts() -> dict[str, int]:
    _validate_static()
    cohorts = [
        *(str(item["cohort"]) for item in WAVE8_CARNATIC_CONTRACTS.values()),
        *(str(item["cohort"]) for item in WAVE8_CARNATIC_HOLDS.values()),
        *("legacy_crosswalk_event_preserved" for _ in WAVE8_CARNATIC_LEGACY_IDS),
    ]
    return dict(sorted(Counter(cohorts).items()))


def wave8_carnatic_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": len(WAVE8_CARNATIC_HOLDS),
        "legacy_crosswalk_rows": len(WAVE8_CARNATIC_LEGACY_IDS),
        "new_entities": len(WAVE8_CARNATIC_ENTITIES),
        "new_sources": len(WAVE8_CARNATIC_SOURCES),
        "newly_rated_events": len(WAVE8_CARNATIC_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_CARNATIC_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_CARNATIC_CONTRACTS),
        "reserved_hced_rows": len(WAVE8_CARNATIC_RESERVED_IDS),
        "reviewed_hced_rows": len(WAVE8_CARNATIC_AUDITED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_carnatic_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_carnatic_counts(),
        "cohorts": wave8_carnatic_cohort_counts(),
        "final_audit_signature": WAVE8_CARNATIC_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_CARNATIC_CONTRACT_IDS),
        "hold_candidate_ids": sorted(WAVE8_CARNATIC_HOLD_IDS),
        "legacy_candidate_ids": sorted(WAVE8_CARNATIC_LEGACY_IDS),
    }


_validate_static()
