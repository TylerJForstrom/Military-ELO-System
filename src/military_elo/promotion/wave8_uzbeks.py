"""Candidate-keyed audit of HCED's six unresolved ``Uzbeks`` rows.

The ethnonym spans several distinct Abu'l-Khayrid rulers and opposing
formations.  This lane therefore opens no generic ``Uzbeks`` alias.  Five
fingerprinted rows receive source-backed tactical dispositions.  Three reuse
one curated Muhammad Shaybani polity for 1500-1510; the later Herat sieges use
their own bounded actors.  The 1497-98 Samarkand row stays held because its
claimed Uzbek victory over Mughals reverses a Timurid siege whose Uzbek force
withdrew without battle.
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
from .wave8_uzbekistan import WAVE8_UZBEKISTAN_SOURCES


__all__ = (
    "WAVE8_UZBEKS_CONTRACT_IDS",
    "WAVE8_UZBEKS_CONTRACTS",
    "WAVE8_UZBEKS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_UZBEKS_ENTITIES",
    "WAVE8_UZBEKS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_UZBEKS_FUNNEL_AUDIT",
    "WAVE8_UZBEKS_HOLD_IDS",
    "WAVE8_UZBEKS_HOLDS",
    "WAVE8_UZBEKS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_UZBEKS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_UZBEKS_RELATED_HCED_DISPOSITIONS",
    "WAVE8_UZBEKS_RESERVED_IDS",
    "WAVE8_UZBEKS_ROW_HASHES",
    "WAVE8_UZBEKS_SOURCES",
    "install_wave8_uzbeks_entities",
    "install_wave8_uzbeks_sources",
    "promote_wave8_uzbeks_contracts",
    "validate_wave8_uzbeks_funnel",
    "validate_wave8_uzbeks_integration_dispositions",
    "validate_wave8_uzbeks_queue_contracts",
    "wave8_uzbeks_audit_signature",
    "wave8_uzbeks_cohort_counts",
    "wave8_uzbeks_counts",
    "wave8_uzbeks_metadata",
)


_LANE_NAME = "Wave 8 exact Uzbeks actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_uzbeks"
_EVENT_ID_PREFIX = "hced_wave8_uzbeks_"
_EXACT_LABELS = frozenset({"uzbeks"})

_SHAYBANI_STATE = "clio_uz_shaybanid_k_1497_9cfc6dff"
_AKHSI_WESTERN_MOGHUL = "sultan_mahmud_western_moghul_force_akhsi_1503"
_AKHSI_EASTERN_MOGHUL = "sultan_ahmad_alaq_eastern_moghul_force_akhsi_1503"
_AKHSI_BABUR = "babur_timurid_force_akhsi_1503"
_HERAT_TIMURID_GARRISON = "timurid_herat_citadel_garrison_1507"
_HERAT_UBAYDALLAH = "ubaydallah_shaybanid_herat_besieging_army_1528"
_ABDULLAH_STATE = "abdullah_ii_abul_khayrid_khanate_1583_1598"
_SAFAVID = "safavid_empire"


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
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_UZBEKS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_uzbeks_iranica_abukhayrids",
        "Abu'l-Khayrids",
        "https://www.iranicaonline.org/articles/abul-khayrids-dynasty/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_abul_khayrids",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_uzbeks_iranica_central_asia_vi",
        "Central Asia vi. In the 16th-18th Centuries",
        "https://www.iranicaonline.org/articles/central-asia-vi/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_central_asia_vi",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_uzbeks_iranica_safavids",
        "Safavid Dynasty",
        "https://www.iranicaonline.org/articles/safavids/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_safavid_dynasty",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_uzbeks_iranica_ali_qoli",
        "Ali-Qoli Khan Shamlu",
        "https://www.iranicaonline.org/articles/ali-qoli-khan-samlu-b/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_ali_qoli_khan_shamlu",
        [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    ),
    _source(
        "wave8_uzbeks_bregel_atlas",
        "An Historical Atlas of Central Asia",
        (
            "https://turkistanilibrary.com/sites/default/files/"
            "-yuri_bregel-an_historical_atlas_of_central_asia.pdf"
        ),
        "Yuri Bregel / Brill",
        "scholarly_historical_atlas",
        "bregel_historical_atlas_central_asia",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_uzbeks_burton_herat_1588",
        "The Fall of Herat to the Uzbegs in 1588",
        "https://www.tandfonline.com/doi/abs/10.1080/05786967.1988.11834352",
        "Audrey Burton / Iran",
        "peer_reviewed_historical_article",
        "burton_fall_herat_1588",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_uzbeks_haider_abdullah_akbar",
        "Relations of Abdullah Khan Uzbeg with Akbar",
        "https://www.persee.fr/doc/cmr_0008-0160_1982_num_23_3_1953",
        "Mansura Haider / Cahiers du Monde Russe",
        "peer_reviewed_historical_article",
        "haider_abdullah_khan_akbar",
        ["identity_boundary_or_context_reference"],
    ),
)

_REUSED_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_UZBEKISTAN_SOURCES
}
_SOURCE_BY_ID = {
    **_REUSED_SOURCE_BY_ID,
    **{str(source["id"]): source for source in WAVE8_UZBEKS_SOURCES},
}


def _bounded_entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: Iterable[str],
    note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start_year,
        "end_year": end_year,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_UZBEKS_ENTITIES: tuple[dict[str, Any], ...] = (
    _bounded_entity(
        _SHAYBANI_STATE,
        "Muhammad Shaybani's Abu'l-Khayrid Khanate",
        "khanate",
        1500,
        1510,
        "Transoxiana, Ferghana, Khwarazm, and Khorasan",
        [
            "cliopatria_v020",
            "wave8_uzbeks_iranica_abukhayrids",
            "wave8_uzbeks_iranica_central_asia_vi",
        ],
        (
            "Curated to Muhammad Shaybani's attested reign and state, from his "
            "1500 consolidation through his death at Merv in 1510. It reuses the "
            "Cliopatria Shaybanids candidate ID but opens no Uzbek or Uzbeks alias. "
            "Later Abu'l-Khayrid appanages and rulers inherit no rating."
        ),
    ),
    _bounded_entity(
        _AKHSI_WESTERN_MOGHUL,
        "Sultan Mahmud Khan's western Moghul force at Akhsi (1503)",
        "engagement_bounded_polity_force",
        1503,
        1503,
        "Ferghana",
        [
            "wave8_uzbekistan_baburnama_beveridge",
            "wave8_uzbeks_bregel_atlas",
        ],
        (
            "Bounded to Sultan Mahmud Khan's separately attested contingent at "
            "Akhsi. It creates no generic Moghulistan or Chagatai alias and no "
            "rating passes to later khanates."
        ),
    ),
    _bounded_entity(
        _AKHSI_EASTERN_MOGHUL,
        "Sultan Ahmad Alaq Khan's eastern Moghul force at Akhsi (1503)",
        "engagement_bounded_polity_force",
        1503,
        1503,
        "Ferghana",
        [
            "wave8_uzbekistan_baburnama_beveridge",
            "wave8_uzbeks_bregel_atlas",
        ],
        (
            "Bounded to Sultan Ahmad Alaq Khan's separately attested contingent "
            "at Akhsi. It does not merge the eastern and western Moghul domains "
            "or confer a rating on a modern population."
        ),
    ),
    _bounded_entity(
        _AKHSI_BABUR,
        "Babur's Timurid force at Akhsi (1503)",
        "engagement_bounded_polity_force",
        1503,
        1503,
        "Ferghana",
        [
            "wave8_uzbekistan_baburnama_beveridge",
            "wave8_uzbekistan_cambridge_babur",
            "wave8_uzbeks_bregel_atlas",
        ],
        (
            "Bounded to Babur's pre-Kabul, pre-Mughal Timurid following at Akhsi. "
            "The Mughal Empire was not founded until 1526 and inherits no result "
            "from this force."
        ),
    ),
    _bounded_entity(
        _HERAT_TIMURID_GARRISON,
        "Timurid citadel garrison at Herat (1507)",
        "siege_bounded_polity_garrison",
        1507,
        1507,
        "Herat, Khorasan",
        [
            "wave8_uzbekistan_iranica_herat",
            "wave8_uzbeks_iranica_abukhayrids",
        ],
        (
            "Bounded to the Timurid garrison that alone continued resistance in "
            "Herat's citadel after the city notables surrendered. It does not "
            "extend the broad Timurid Empire envelope beyond this final defense."
        ),
    ),
    _bounded_entity(
        _HERAT_UBAYDALLAH,
        "Ubaydallah Khan's besieging army at Herat (1528)",
        "siege_bounded_field_army",
        1528,
        1528,
        "Herat, Khorasan",
        [
            "wave8_uzbekistan_iranica_khorasan_safavid",
            "wave8_uzbekistan_iranica_tahmasp",
        ],
        (
            "Bounded to the seven-month Herat siege that Ubaydallah ended under "
            "pressure from Shah Tahmasp's relief advance. It is distinct from "
            "the later Jam field army and opens no generic Shaybanid alias."
        ),
    ),
    _bounded_entity(
        _ABDULLAH_STATE,
        "Abdullah Khan II's Abu'l-Khayrid Khanate",
        "khanate",
        1583,
        1598,
        "Bukhara, Transoxiana, and conquered Khorasan",
        [
            "wave8_uzbeks_burton_herat_1588",
            "wave8_uzbeks_haider_abdullah_akbar",
            "wave8_uzbeks_iranica_abukhayrids",
            "wave8_uzbeks_iranica_central_asia_vi",
        ],
        (
            "Curated to Abdullah II's formal khanship from 1583 until his death "
            "in 1598. Earlier appanage rule, successor claimants, Janids, later "
            "Bukhara, and the modern Republic of Uzbekistan inherit no rating."
        ),
    ),
)


WAVE8_UZBEKS_ROW_HASHES: dict[str, str] = {
    "hced-Akhsikath1503-1": "784f5688da9def81a962d48a60208b3c70ab14b6eb966f2bc1d56b72c8280b80",
    "hced-Herat1507-1": "53460fb224c6bbaac3f54e5c5d85b4a4f8829ab09a3cf4a0105b80fcf988c9cb",
    "hced-Herat1528-1": "d9f4a2ab2537692214c3ac693774b3a26ee1541eb077ca154567835039186e2a",
    "hced-Herat1588-1": "44d3689ecd0c6fa99b53a052b9dd4d41393509abe56918ba107a6bd8e0e830e7",
    "hced-Merv1510-1": "7cfef6cdf0e864aa96db60ff58d69c8ef81e08466a79270fe74b0ff7de653194",
    "hced-Samarkand1497-1498-1": "b500e31eca6f3c2b10268fb1ec08dcc22ffd63f60ddcb0ccaa8b5f25db3c7b85",
}

WAVE8_UZBEKS_FUNNEL_AUDIT: dict[str, Any] = {
    "event_candidate_id_sha256": (
        "12f5c770c6b3ca595f074fb0c046d91506b0f71f9ce3f9b8fa1d95462baead56"
    ),
    "events_touched": 6,
    "label": "uzbeks",
    "marginal_events": 3,
    "newly_unblocked_candidate_id_sha256": (
        "e4f816c932ea8b99ef822c2301eb4adb443b21fbaa806bd7b82533f313d9964b"
    ),
    "sole_blocker_events": 3,
    "unresolved_side_attempts": 6,
    "zero_time_valid_candidates": 6,
}


def _canonical(
    name: str,
    year_low: int,
    year_high: int,
    date_text: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{year_high}",
        "date_precision": "year" if year_low == year_high else "range",
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": year_high,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_sources: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    actor_override: str,
    date_source_ids: Iterable[str] = (),
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_sources)))
    date_sources = sorted(set(map(str, date_source_ids)))
    return {
        "raw_row_sha256": WAVE8_UZBEKS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1_entity_ids)),
        "side_2_entity_ids": list(map(str, side_2_entity_ids)),
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
        "source_date_override": bool(date_sources),
        "date_source_ids": date_sources,
        "actor_override": actor_override,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_UZBEKS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Akhsikath1503-1": _contract(
        "hced-Akhsikath1503-1",
        _canonical(
            "Battle of Akhsi (Archiyan)",
            1503,
            1503,
            "June 1503",
            "pitched_battle",
        ),
        "shaybani_conquests_1500_1510",
        [_SHAYBANI_STATE],
        [_AKHSI_WESTERN_MOGHUL, _AKHSI_EASTERN_MOGHUL, _AKHSI_BABUR],
        [
            "wave8_uzbekistan_baburnama_beveridge",
            "wave8_uzbekistan_cambridge_babur",
            "wave8_uzbeks_bregel_atlas",
        ],
        ["wave8_uzbekistan_baburnama_beveridge", "wave8_uzbeks_bregel_atlas"],
        (
            "Babur's narrative and Bregel's atlas identify Muhammad Shaybani's "
            "victory over the two Moghul khans and Babur near Akhsi. The raw "
            "Mughal Empire label is replaced by the three attested pre-1526 "
            "participants; no later Mughal result is inferred."
        ),
        confidence=0.94,
        actor_override="source_backed_pre_mughal_three_participant_coalition",
    ),
    "hced-Herat1507-1": _contract(
        "hced-Herat1507-1",
        _canonical(
            "Capture of the Herat citadel",
            1507,
            1507,
            "20 May 1507",
            "siege_and_capitulation",
        ),
        "shaybani_conquests_1500_1510",
        [_SHAYBANI_STATE],
        [_HERAT_TIMURID_GARRISON],
        [
            "wave8_uzbekistan_iranica_herat",
            "wave8_uzbeks_iranica_abukhayrids",
        ],
        [
            "wave8_uzbekistan_iranica_herat",
            "wave8_uzbeks_iranica_abukhayrids",
        ],
        (
            "Iranica reports that Herat's notables surrendered the town without "
            "fighting while the citadel garrison alone resisted. The contract "
            "rates only that bounded siege and capitulation, not civilians or a "
            "generic Timurid-Mughal envelope."
        ),
        confidence=0.91,
        actor_override="source_backed_herat_citadel_garrison",
    ),
    "hced-Herat1528-1": _contract(
        "hced-Herat1528-1",
        _canonical(
            "Relief of the siege of Herat",
            1528,
            1528,
            "Late summer 1528 after a seven-month siege",
            "siege_relief",
        ),
        "safavid_uzbek_khorasan_1528",
        [_SAFAVID],
        [_HERAT_UBAYDALLAH],
        [
            "wave8_uzbeks_iranica_abukhayrids",
            "wave8_uzbekistan_iranica_khorasan_safavid",
            "wave8_uzbekistan_iranica_tahmasp",
        ],
        [
            "wave8_uzbeks_iranica_abukhayrids",
            "wave8_uzbekistan_iranica_tahmasp",
        ],
        (
            "The reviewed synthesis says Tahmasp's advance forced Ubaydallah to "
            "end the seven-month siege. This siege result is distinct from the "
            "later Jam/Saruqamesh field battle already rated in the same campaign."
        ),
        confidence=0.87,
        actor_override="source_backed_siege_bounded_ubaydallah_force",
    ),
    "hced-Herat1588-1": _contract(
        "hced-Herat1588-1",
        _canonical(
            "Abu'l-Khayrid siege and capture of Herat",
            1587,
            1589,
            (
                "Siege began in 1587; dedicated scholarship dates the fall to "
                "1588 while one Iranica calendar conversion gives February 1589"
            ),
            "siege",
        ),
        "abdullah_ii_khorasan_conquest",
        [_ABDULLAH_STATE],
        [_SAFAVID],
        [
            "wave8_uzbeks_burton_herat_1588",
            "wave8_uzbeks_iranica_ali_qoli",
            "wave8_uzbeks_iranica_central_asia_vi",
        ],
        [
            "wave8_uzbeks_burton_herat_1588",
            "wave8_uzbeks_iranica_ali_qoli",
        ],
        (
            "Burton's dedicated study and Iranica agree that Abdullah II's force "
            "defeated the Safavid defense. The explicit 1587-89 range preserves "
            "their calendar disagreement; HCED's Mughal opponent is not retained."
        ),
        confidence=0.86,
        actor_override="source_backed_abul_khayrid_and_safavid_siege_sides",
        date_source_ids=[
            "wave8_uzbeks_burton_herat_1588",
            "wave8_uzbeks_iranica_ali_qoli",
        ],
    ),
    "hced-Merv1510-1": _contract(
        "hced-Merv1510-1",
        _canonical(
            "Battle of Mahmudi near Merv",
            1510,
            1510,
            "30 November-2 December 1510",
            "pitched_battle",
        ),
        "safavid_shaybani_war_1510",
        [_SAFAVID],
        [_SHAYBANI_STATE],
        [
            "wave8_uzbekistan_iranica_chronology",
            "wave8_uzbekistan_iranica_khorasan_safavid",
            "wave8_uzbeks_iranica_abukhayrids",
            "wave8_uzbeks_iranica_safavids",
        ],
        [
            "wave8_uzbeks_iranica_abukhayrids",
            "wave8_uzbeks_iranica_safavids",
        ],
        (
            "The Iranica sources independently identify Shah Ismail's victory "
            "over Muhammad Shaybani outside Merv and Shaybani's death. The battle "
            "is tactical evidence only; later conquest and executions are not "
            "additional rating outcomes."
        ),
        confidence=0.98,
        actor_override="curated_muhammad_shaybani_state",
    ),
}


WAVE8_UZBEKS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Samarkand1497-1498-1": {
        "raw_row_sha256": WAVE8_UZBEKS_ROW_HASHES[
            "hced-Samarkand1497-1498-1"
        ],
        "disposition": "hold",
        "hold_category": "wrong_actors_and_reversed_outcome",
        "hold_reason": (
            "Babur and Sultan Ali's Timurid forces captured Samarkand after the "
            "1497 siege. Muhammad Shaybani approached but withdrew without "
            "battle; the later Uzbek capture belongs to 1500-01. Replacing both "
            "HCED sides and reversing its outcome would turn this row into a "
            "different event, so it remains unrated rather than becoming a draw."
        ),
        "evidence_refs": [
            "wave8_uzbekistan_baburnama_beveridge",
            "wave8_uzbeks_bregel_atlas",
        ],
    }
}

WAVE8_UZBEKS_CONTRACT_IDS = frozenset(WAVE8_UZBEKS_CONTRACTS)
WAVE8_UZBEKS_HOLD_IDS = frozenset(WAVE8_UZBEKS_HOLDS)
WAVE8_UZBEKS_RESERVED_IDS = frozenset(
    {*WAVE8_UZBEKS_CONTRACT_IDS, *WAVE8_UZBEKS_HOLD_IDS}
)
WAVE8_UZBEKS_POINT_QUARANTINE_ADDITIONS = WAVE8_UZBEKS_CONTRACT_IDS
WAVE8_UZBEKS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_UZBEKS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the named city or battlefield and "
            "modern jurisdiction but do not bind HCED's exact coordinate to the "
            "closed release provenance contract. Retain the source country and "
            "withhold the unexplained point."
        ),
        "evidence_refs": sorted(contract["evidence_refs"]),
    }
    for candidate_id, contract in sorted(WAVE8_UZBEKS_CONTRACTS.items())
}

WAVE8_UZBEKS_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Maruchak1507-1": {
        "raw_row_sha256": "dabaf0de5cadeb1edb7c8699cf13e1c7f70ed2cf134ecdb50292d715ec5c209b",
        "related_candidate_id": "hced-Herat1507-1",
        "disposition": "herat_capture_owned_maruchak_remains_unbounded_hold",
    },
    "hced-Torbat-i-Jam1528-1": {
        "raw_row_sha256": "b36a6201b5395f2b0a7810db4c9a23150dcc40f201d15d0657debd4d8b38d89d",
        "related_candidate_id": "hced-Herat1528-1",
        "disposition": "distinct_siege_relief_and_later_field_battle",
    },
    "hced-Rabat-i-Pariyan1598-1": {
        "raw_row_sha256": "c7b1ecf9924f81efab76a1bda6f8326d0fb8f58758ef4e1ed4d10e7bd460c5a9",
        "related_candidate_id": "hced-Herat1588-1",
        "disposition": "distinct_ten_year_later_safavid_reconquest_battle",
    },
}

_DUPLICATE_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Akhsikath1503-1": {
        "aliases": ["akhsi", "akhsikath", "archiyan", "battle of akhsi"],
        "years": [1503, 1503],
    },
    "hced-Herat1507-1": {
        "aliases": ["capture of herat citadel", "herat"],
        "years": [1507, 1507],
    },
    "hced-Herat1528-1": {
        "aliases": ["herat", "relief of the siege of herat"],
        "years": [1528, 1528],
    },
    "hced-Herat1588-1": {
        "aliases": ["herat", "siege of herat"],
        "years": [1587, 1589],
    },
    "hced-Merv1510-1": {
        "aliases": ["battle of mahmudi", "battle of merv", "mahmudi", "merv"],
        "years": [1510, 1510],
    },
    "hced-Samarkand1497-1498-1": {
        "aliases": ["samarkand", "siege of samarkand"],
        "years": [1497, 1498],
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_UZBEKS_CONTRACTS,
        "duplicate_audit": _DUPLICATE_AUDIT,
        "entities": WAVE8_UZBEKS_ENTITIES,
        "funnel": WAVE8_UZBEKS_FUNNEL_AUDIT,
        "holds": WAVE8_UZBEKS_HOLDS,
        "location_reasons": WAVE8_UZBEKS_LOCATION_QUARANTINE_REASONS,
        "related_hced": WAVE8_UZBEKS_RELATED_HCED_DISPOSITIONS,
        "row_hashes": WAVE8_UZBEKS_ROW_HASHES,
        "sources": WAVE8_UZBEKS_SOURCES,
    }


def wave8_uzbeks_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_UZBEKS_FINAL_AUDIT_SIGNATURE = (
    "c5d6ab5ccc5624fadc17d20186fec95925cf5a99955cc10aba5c6b9d7fbcc524"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    new_source_ids = {str(source["id"]) for source in WAVE8_UZBEKS_SOURCES}
    if len(new_source_ids) != len(WAVE8_UZBEKS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if new_source_ids & set(_REUSED_SOURCE_BY_ID):
        raise ValueError(f"{_LANE_NAME} shadows a reused source")
    for source in WAVE8_UZBEKS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_ids = {str(entity["id"]) for entity in WAVE8_UZBEKS_ENTITIES}
    if len(entity_ids) != len(WAVE8_UZBEKS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    if _SHAYBANI_STATE not in entity_ids or _ABDULLAH_STATE not in entity_ids:
        raise ValueError(f"{_LANE_NAME} curated state identities are incomplete")
    for entity in WAVE8_UZBEKS_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} opened an alias or inheritance path")
        if int(entity["start_year"]) > int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} entity interval is inverted")
        if normalize_label(entity["name"]) in {"uzbek", "uzbeks", "uzbekistan"}:
            raise ValueError(f"{_LANE_NAME} installed a generic Uzbek identity")
        if not set(map(str, entity["source_ids"])) <= {
            "cliopatria_v020",
            *set(_SOURCE_BY_ID),
        }:
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    if set(WAVE8_UZBEKS_ROW_HASHES) != WAVE8_UZBEKS_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} row disposition inventory is incomplete")
    if WAVE8_UZBEKS_POINT_QUARANTINE_ADDITIONS != WAVE8_UZBEKS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine is not promotion-only")
    if WAVE8_UZBEKS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} unexpectedly withholds a country")
    if set(WAVE8_UZBEKS_LOCATION_QUARANTINE_REASONS) != WAVE8_UZBEKS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reasons are incomplete")

    allowed_entities = entity_ids | {_SAFAVID}
    used_entities: set[str] = set()
    for candidate_id, contract in WAVE8_UZBEKS_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_UZBEKS_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash drifted")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} contract sources are not canonical")
        if not set(outcomes) <= set(evidence) or not set(evidence) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} contract source closure failed")
        expected_families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome families drifted")
        if len(expected_families) < 2:
            raise ValueError(f"{_LANE_NAME} contract lacks two outcome families")
        sides = set(map(str, contract["side_1_entity_ids"])) | set(
            map(str, contract["side_2_entity_ids"])
        )
        if not sides <= allowed_entities:
            raise ValueError(f"{_LANE_NAME} contract names an unknown entity")
        used_entities.update(sides & entity_ids)
        date_sources = list(map(str, contract["date_source_ids"]))
        if bool(date_sources) != bool(contract["source_date_override"]):
            raise ValueError(f"{_LANE_NAME} date override metadata drifted")
        if date_sources and (not _is_sorted_unique(date_sources) or not set(date_sources) <= set(evidence)):
            raise ValueError(f"{_LANE_NAME} date sources are not closed")
    if used_entities != entity_ids:
        raise ValueError(f"{_LANE_NAME} installed an unused identity")

    if wave8_uzbeks_audit_signature() != WAVE8_UZBEKS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature drifted")


def validate_wave8_uzbeks_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin all six literal-label rows and their promotion/hold dispositions."""

    _validate_static()
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_UZBEKS_CONTRACTS,
        WAVE8_UZBEKS_HOLDS,
        lane_name=_LANE_NAME,
    )
    exact = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) in _EXACT_LABELS
        or normalize_label(row.get("side_2_raw")) in _EXACT_LABELS
    }
    if exact != WAVE8_UZBEKS_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed: {sorted(exact)}")
    for candidate_id, expected in WAVE8_UZBEKS_ROW_HASHES.items():
        row = next(row for row in hced_rows if row.get("candidate_id") == candidate_id)
        if canonical_hced_row_sha256(row) != expected:
            raise ValueError(f"{_LANE_NAME} raw-row fingerprint changed")
    return {"exact_label_rows": len(exact), **counts}


def validate_wave8_uzbeks_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    """Pin the six-row planning record and three historical sole blockers."""

    _validate_static()
    labels = funnel.get("labels")
    if not isinstance(labels, list):
        raise ValueError(f"{_LANE_NAME} funnel labels are unavailable")
    records = [item for item in labels if item.get("label") == "uzbeks"]
    if len(records) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    record = records[0]
    expected = WAVE8_UZBEKS_FUNNEL_AUDIT
    for key in (
        "event_candidate_id_sha256",
        "events_touched",
        "sole_blocker_events",
        "unresolved_side_attempts",
    ):
        if record.get(key) != expected[key]:
            raise ValueError(f"{_LANE_NAME} funnel {key} changed")
    failures = record.get("failure_cases")
    if not isinstance(failures, Mapping) or failures.get(
        "zero_time_valid_candidates"
    ) != expected["zero_time_valid_candidates"]:
        raise ValueError(f"{_LANE_NAME} funnel failure cases changed")

    rows = funnel.get("row_label_data")
    if not isinstance(rows, list):
        raise ValueError(f"{_LANE_NAME} row-label data are unavailable")
    scoped = {
        str(row.get("candidate_id"))
        for row in rows
        if any(
            item.get("label") == "uzbeks"
            for item in row.get("label_failures", [])
            if isinstance(item, Mapping)
        )
    }
    if scoped != WAVE8_UZBEKS_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} funnel row inventory changed")
    sole = {
        str(row.get("candidate_id"))
        for row in rows
        if row.get("sole_blocker_label") == "uzbeks"
    }
    if len(sole) != expected["sole_blocker_events"]:
        raise ValueError(f"{_LANE_NAME} funnel sole-blocker count changed")

    ranking = funnel.get("greedy_batch", {}).get("ranking", [])
    ranked = [item for item in ranking if item.get("label") == "uzbeks"]
    if len(ranked) != 1:
        raise ValueError(f"{_LANE_NAME} greedy ranking is unavailable")
    if (
        ranked[0].get("marginal_events") != expected["marginal_events"]
        or ranked[0].get("newly_unblocked_candidate_id_sha256")
        != expected["newly_unblocked_candidate_id_sha256"]
    ):
        raise ValueError(f"{_LANE_NAME} greedy audit changed")
    return {
        "events_touched": expected["events_touched"],
        "sole_blocker_events": expected["sole_blocker_events"],
        "unresolved_side_attempts": expected["unresolved_side_attempts"],
        "zero_time_valid_candidates": expected["zero_time_valid_candidates"],
    }


def _date_year(value: Any) -> int | None:
    text = str(value or "")
    if len(text) >= 4 and text[:4].isdigit():
        return int(text[:4])
    if isinstance(value, int):
        return value
    return None


def validate_wave8_uzbeks_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    release_events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    """Pin related rows and fail on any unreviewed duplicate surface."""

    validate_wave8_uzbeks_queue_contracts(hced_rows)
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        indexed.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, disposition in WAVE8_UZBEKS_RELATED_HCED_DISPOSITIONS.items():
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1 or canonical_hced_row_sha256(rows[0]) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} related HCED row changed: {candidate_id}")

    normalized = {
        candidate_id: {
            "aliases": {normalize_label(alias) for alias in item["aliases"]},
            "years": tuple(map(int, item["years"])),
        }
        for candidate_id, item in _DUPLICATE_AUDIT.items()
    }
    for row in iwbd_rows:
        low = _date_year(row.get("start_date"))
        high = _date_year(row.get("end_date"))
        if low is None or high is None:
            continue
        name = normalize_label(row.get("name"))
        for candidate_id, audit in normalized.items():
            start, end = audit["years"]
            if low <= end and high >= start and name in audit["aliases"]:
                raise ValueError(
                    f"{_LANE_NAME} found unreviewed IWBD overlap "
                    f"{row.get('candidate_id')} for {candidate_id}"
                )

    events = list(release_events)
    owned = {
        str(event.get("hced_candidate_id"))
        for event in events
        if event.get("hced_candidate_id") in WAVE8_UZBEKS_RESERVED_IDS
    }
    if owned and owned != WAVE8_UZBEKS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} release integration is partial")
    for event in events:
        if event.get("hced_candidate_id") in WAVE8_UZBEKS_CONTRACT_IDS:
            continue
        low = _date_year(event.get("year"))
        high = _date_year(event.get("end_year")) or low
        if low is None or high is None:
            continue
        name = normalize_label(event.get("name"))
        for candidate_id, audit in normalized.items():
            start, end = audit["years"]
            if low <= end and high >= start and name in audit["aliases"]:
                raise ValueError(
                    f"{_LANE_NAME} found unreviewed release overlap "
                    f"{event.get('id')} for {candidate_id}"
                )
    return {
        "integration_dispositions": len(WAVE8_UZBEKS_RELATED_HCED_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_zero_overlap_candidates": len(_DUPLICATE_AUDIT),
        "release_lane_events": len(owned),
        "related_hced_dispositions": len(WAVE8_UZBEKS_RELATED_HCED_DISPOSITIONS),
    }


def install_wave8_uzbeks_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_UZBEKS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_uzbeks_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_UZBEKS_SOURCES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_uzbeks_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit exactly five tactical events and withhold their unverified points."""

    _validate_static()
    validate_wave8_uzbeks_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_UZBEKS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    if {event["hced_candidate_id"] for event in events} != WAVE8_UZBEKS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} emitted an incomplete cohort")
    for event in events:
        event.pop("geometry", None)
        if "modern_location_country" not in event:
            raise ValueError(f"{_LANE_NAME} unexpectedly lost a country assertion")
        if "location_provenance" not in event:
            raise ValueError(f"{_LANE_NAME} unexpectedly lost location provenance")
    return events


def wave8_uzbeks_counts() -> dict[str, int]:
    return {
        "country_quarantine_additions": len(
            WAVE8_UZBEKS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "holds": len(WAVE8_UZBEKS_HOLD_IDS),
        "new_entities": len(WAVE8_UZBEKS_ENTITIES),
        "new_sources": len(WAVE8_UZBEKS_SOURCES),
        "newly_rated_events": len(WAVE8_UZBEKS_CONTRACT_IDS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(WAVE8_UZBEKS_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_UZBEKS_CONTRACT_IDS),
        "reviewed_hced_rows": len(WAVE8_UZBEKS_RESERVED_IDS),
        "source_date_overrides": sum(
            bool(contract["source_date_override"])
            for contract in WAVE8_UZBEKS_CONTRACTS.values()
        ),
    }


def wave8_uzbeks_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_UZBEKS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_uzbeks_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "audit": "candidate_keyed_exact_label_time_bounded_actors",
        "candidate_ids": sorted(WAVE8_UZBEKS_RESERVED_IDS),
        "cohorts": wave8_uzbeks_cohort_counts(),
        "counts": wave8_uzbeks_counts(),
        "final_audit_signature": WAVE8_UZBEKS_FINAL_AUDIT_SIGNATURE,
        "funnel_audit": WAVE8_UZBEKS_FUNNEL_AUDIT,
        "holds": WAVE8_UZBEKS_HOLDS,
        "location_quarantine_reasons": WAVE8_UZBEKS_LOCATION_QUARANTINE_REASONS,
        "module_owner": _MODULE_OWNER,
        "related_hced_dispositions": WAVE8_UZBEKS_RELATED_HCED_DISPOSITIONS,
        "row_dispositions": {
            candidate_id: (
                "promote" if candidate_id in WAVE8_UZBEKS_CONTRACT_IDS else "hold"
            )
            for candidate_id in sorted(WAVE8_UZBEKS_RESERVED_IDS)
        },
    }
