"""Candidate-keyed Wave 8 audit for HCED's exact ``Punjabi Sikhs`` label.

The four locked rows are not evidence for a timeless Punjabi, Sikh, or Sikh
Empire polity.  They describe Guru Gobind Singh's event-bounded Khalsa forces
at Anandpur/Anandgarh and during the ensuing withdrawal to the Sarsa.  Two
mechanically defensible outcomes are promoted: the besiegers achieved their
operational objective when the final Anandgarh garrison evacuated, and Wazir
Khan's pursuing force inflicted a bounded tactical defeat at the Sarsa.

The Anandpur 1700 row remains a reciprocal chronology-twin hold with the
``Sikh Punjab`` lane's Anandpur 1701 row.  ``Anandpur (1st)`` 1704 also stays
held: modern scholarship, the near-contemporary *Sri Gursobha*, and older
numbered chronologies do not identify that label and year as one unique battle
separate from the earlier Anandpur/Nirmoh/Basoli sequence and the final siege.
Neither uncertainty is converted to a draw.  No result is invented.

Both promoted coordinates are withheld.  Anandpur is a city centroid rather
than the multi-fort siege footprint; HCED's Sarsa point is in Gujarat, hundreds
of kilometres from the Punjab action.  The modern country India is retained.
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
    "WAVE8_PUNJABI_SIKHS_ADJACENT_LABEL_INVENTORY_PINS",
    "WAVE8_PUNJABI_SIKHS_COMPANY_ERA_CANDIDATE_IDS",
    "WAVE8_PUNJABI_SIKHS_COMPANY_ERA_CANDIDATE_ID_SHA256",
    "WAVE8_PUNJABI_SIKHS_CONTRACT_IDS",
    "WAVE8_PUNJABI_SIKHS_CONTRACTS",
    "WAVE8_PUNJABI_SIKHS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_PUNJABI_SIKHS_ENTITIES",
    "WAVE8_PUNJABI_SIKHS_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_PUNJABI_SIKHS_EXCLUSION_IDS",
    "WAVE8_PUNJABI_SIKHS_EXCLUSIONS",
    "WAVE8_PUNJABI_SIKHS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_PUNJABI_SIKHS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_PUNJABI_SIKHS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_PUNJABI_SIKHS_FUNNEL_EVENT_CANDIDATE_ID_SHA256",
    "WAVE8_PUNJABI_SIKHS_HOLD_IDS",
    "WAVE8_PUNJABI_SIKHS_HOLDS",
    "WAVE8_PUNJABI_SIKHS_INTEGRATION_DISPOSITIONS",
    "WAVE8_PUNJABI_SIKHS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_PUNJABI_SIKHS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_PUNJABI_SIKHS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_PUNJABI_SIKHS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_PUNJABI_SIKHS_NONPROMOTIONS",
    "WAVE8_PUNJABI_SIKHS_OUTCOME_OVERRIDES",
    "WAVE8_PUNJABI_SIKHS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS",
    "WAVE8_PUNJABI_SIKHS_RESERVED_IDS",
    "WAVE8_PUNJABI_SIKHS_ROW_HASHES",
    "WAVE8_PUNJABI_SIKHS_SOURCES",
    "WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSIONS",
    "WAVE8_PUNJABI_SIKHS_TOUCHED_CANDIDATE_IDS",
    "install_wave8_punjabi_sikhs_entities",
    "install_wave8_punjabi_sikhs_sources",
    "promote_wave8_punjabi_sikhs_contracts",
    "validate_wave8_punjabi_sikhs_integration_dispositions",
    "validate_wave8_punjabi_sikhs_queue_contracts",
    "wave8_punjabi_sikhs_audit_signature",
    "wave8_punjabi_sikhs_cohort_counts",
    "wave8_punjabi_sikhs_counts",
    "wave8_punjabi_sikhs_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Punjabi Sikhs actor audit"
_EVENT_ID_PREFIX = "hced_wave8_punjabi_sikhs_"
_MODULE_OWNER = "military_elo.promotion.wave8_punjabi_sikhs"
_SIKH_PUNJAB_MODULE = "military_elo.promotion.wave8_sikh_punjab"

_ANANDGARH_BESIEGERS_ID = "mughal_hill_siege_coalition_anandgarh_1704"
_ANANDGARH_KHALSA_ID = "guru_gobind_singh_khalsa_garrison_anandgarh_1704"
_SARSA_PURSUERS_ID = "wazir_khan_mughal_hill_pursuit_force_sarsa_1704"
_SARSA_KHALSA_ID = "guru_gobind_singh_withdrawal_column_sarsa_1704"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool,
    crosscheck: bool = True,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if outcome and crosscheck:
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


WAVE8_PUNJABI_SIKHS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_punjabi_sikhs_grewal_white_hawk",
        "Ouster from Anandpur (1699-1704)",
        "https://academic.oup.com/book/36926/chapter-abstract/322205546",
        "Oxford University Press",
        "scholarly_monograph_chapter",
        "js_grewal_master_white_hawk_2020",
        outcome=True,
    ),
    _source(
        "wave8_punjabi_sikhs_gupta_vol1",
        "History of the Sikhs, Volume I: The Sikh Gurus (1469-1708)",
        "https://apnaorg.com/books/english/history-of-sikhs-v1/history-of-sikhs-v1.pdf",
        "Munshiram Manoharlal Publishers",
        "scholarly_historical_monograph",
        "hari_ram_gupta_history_sikhs_vol1",
        outcome=True,
    ),
    _source(
        "wave8_punjabi_sikhs_shah_sri_gursobha",
        "In Praise of the Guru: A Translation and Study of Sainapati's Sri Gursobha",
        (
            "https://www.gurmatveechar.com/books/English_Books/"
            "English_Thesis_Papers/In.Praise.of.the.Guru.A.Translation.and."
            "Study.of.Sainapatis.Sri.Gursobha.by.Ami.Praful.Shah."
            "%28GurmatVeechar.com%29.pdf"
        ),
        "University of California, Santa Barbara",
        "doctoral_dissertation_and_near_contemporary_text_translation",
        "ami_praful_shah_sri_gursobha",
        outcome=True,
    ),
    _source(
        "wave8_punjabi_sikhs_khushwant_vol1",
        "A History of the Sikhs, Volume 1: 1469-1838",
        "https://academic.oup.com/book/25977",
        "Oxford University Press",
        "scholarly_historical_monograph",
        "khushwant_singh_history_sikhs_vol1",
        outcome=True,
    ),
    _source(
        "wave8_punjabi_sikhs_macauliffe_vol5",
        "The Sikh Religion, Volume 5",
        (
            "https://www.cambridge.org/core/books/the-sikh-religion/"
            "BCAD868779C7502C8A2727447DC9828B"
        ),
        "Cambridge University Press",
        "edited_historical_and_traditional_source_collection",
        "max_arthur_macauliffe_sikh_religion_vol5",
        outcome=True,
    ),
    _source(
        "wave8_punjabi_sikhs_kaur_march_thesis",
        (
            "Guru Gobind Singh's March from Anandpur Sahib to Damdama Sahib: "
            "An Historical Analysis of the Oral Tradition"
        ),
        (
            "https://gurmatveechar.com/books/English_Books/English_Thesis_Papers/"
            "Guru.Gobind.Singhs.march.from.Anandpur.Sahib.to.Damdama.Sahib.an."
            "historical.analysis.of.the.oral.tradition."
            "%28GurmatVeechar.com%29.pdf"
        ),
        "Punjabi University, Patiala",
        "doctoral_dissertation",
        "gurvinderpal_kaur_anandpur_damdama_thesis",
        outcome=True,
    ),
    _source(
        "wave8_punjabi_sikhs_eos_anandpur",
        "Anandpur",
        (
            "https://eos.learnpunjabi.org/ANANDPUR%20%2831%C2%BA-13%27N%2C%20"
            "76%C2%BA-32%27E%29.html"
        ),
        "Encyclopaedia of Sikhism, Punjabi University",
        "academic_encyclopedia_entry",
        "punjabi_university_encyclopaedia_anandpur",
        outcome=False,
        crosscheck=False,
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_PUNJABI_SIKHS_SOURCES
}
_SOURCE_FAMILY_BY_ID = {
    source_id: str(source["source_family_id"])
    for source_id, source in _SOURCE_BY_ID.items()
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    region: str,
    boundary_note: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 1704,
        "end_year": 1704,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No rating is inherited from or passed to a timeless Punjabi or "
            "Sikh identity, another Anandpur campaign phase, Banda Singh's force, "
            "the Sikh misls, the Sikh Empire, the Lahore Khalsa army, Punjab, "
            "modern India or Pakistan, or any religious or ethnic community."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_PUNJABI_SIKHS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _ANANDGARH_BESIEGERS_ID,
        "Mughal-hill siege coalition at Anandgarh (1704)",
        "event_bounded_mughal_hill_siege_coalition",
        "Anandpur-Anandgarh fort complex, Punjab",
        (
            "Bounded to the Wazir Khan/Sirhind, Lahore, Jammu, Ranghar, Gujar, "
            "Pathan, and allied hill-state forces maintaining the final blockade."
        ),
        [
            "wave8_punjabi_sikhs_eos_anandpur",
            "wave8_punjabi_sikhs_grewal_white_hawk",
            "wave8_punjabi_sikhs_gupta_vol1",
            "wave8_punjabi_sikhs_shah_sri_gursobha",
        ],
    ),
    _entity(
        _ANANDGARH_KHALSA_ID,
        "Guru Gobind Singh's Khalsa garrison at Anandgarh (1704)",
        "event_bounded_khalsa_fortress_garrison",
        "Anandpur-Anandgarh fort complex, Punjab",
        (
            "Bounded to Guru Gobind Singh, the remaining Khalsa formations, and "
            "the inhabitants defending the forts during the final blockade."
        ),
        [
            "wave8_punjabi_sikhs_grewal_white_hawk",
            "wave8_punjabi_sikhs_shah_sri_gursobha",
            "wave8_punjabi_sikhs_khushwant_vol1",
        ],
    ),
    _entity(
        _SARSA_PURSUERS_ID,
        "Wazir Khan's Mughal-hill pursuit force at the Sarsa (1704)",
        "event_bounded_mughal_hill_pursuit_force",
        "Sarsa crossing and eastern Punjab approaches",
        (
            "Bounded to the Mughal and allied hill contingents that attacked the "
            "evacuating columns before and during the Sarsa crossing."
        ),
        [
            "wave8_punjabi_sikhs_gupta_vol1",
            "wave8_punjabi_sikhs_kaur_march_thesis",
            "wave8_punjabi_sikhs_macauliffe_vol5",
        ],
    ),
    _entity(
        _SARSA_KHALSA_ID,
        "Guru Gobind Singh's withdrawing Khalsa column at the Sarsa (1704)",
        "event_bounded_khalsa_withdrawal_column",
        "Sarsa crossing and eastern Punjab approaches",
        (
            "Bounded to the Guru's withdrawing force, its rearguards, household "
            "groups, and escorts attacked during the crossing and dispersal."
        ),
        [
            "wave8_punjabi_sikhs_gupta_vol1",
            "wave8_punjabi_sikhs_kaur_march_thesis",
            "wave8_punjabi_sikhs_shah_sri_gursobha",
        ],
    ),
)


WAVE8_PUNJABI_SIKHS_ROW_HASHES: dict[str, str] = {
    "hced-Anandpur (1st)1704-1": (
        "aa3745fbe0ebe64ec9b7ed0869838758a688f787bba3fc513ca6736b97cd8994"
    ),
    "hced-Anandpur (2nd)1704-1": (
        "b89dadee7b359f6bb5ec32ef6a62404761a91d842fb7edce8c013631d8e2b9a7"
    ),
    "hced-Anandpur1700-1": (
        "3f992b5f13d444a3178aab638c90b8a7fd465615d6b8c6cc9f1fa95bf6146590"
    ),
    "hced-Sarsa1704-1": (
        "ea56823b804978afc538de6e7de6e145c8b9169f1822ea4a63b5df8b930c8d99"
    ),
}

WAVE8_PUNJABI_SIKHS_EXACT_CANDIDATE_ID_SHA256 = (
    "57a22918f5385d4ef906fe512d091de5b98881744ffd27b4a3d195df70de1715"
)
WAVE8_PUNJABI_SIKHS_FUNNEL_EVENT_CANDIDATE_ID_SHA256 = (
    WAVE8_PUNJABI_SIKHS_EXACT_CANDIDATE_ID_SHA256
)

WAVE8_PUNJABI_SIKHS_ADJACENT_LABEL_INVENTORY_PINS: dict[
    str, dict[str, Any]
] = {
    "punjab": {
        "count": 41,
        "candidate_id_sha256": (
            "afc7be9c1030aab12e1a944a7404eb0aaa5ec5f30e3c976a36411a024cd2c69d"
        ),
    },
    "sikh empire": {
        "count": 0,
        "candidate_id_sha256": (
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ),
    },
    "sikh punjab": {
        "count": 5,
        "candidate_id_sha256": (
            "9595b3b15abf30ad7649c48b4959eeca9a2361a21bc99876acb9fe7c0c67e929"
        ),
    },
    "sikhs": {
        "count": 1,
        "candidate_id_sha256": (
            "095378e177c93845ba14fe56cf2c3bdee99d0d1c5ed074192f24edc66cb597a2"
        ),
    },
}

WAVE8_PUNJABI_SIKHS_COMPANY_ERA_CANDIDATE_IDS = frozenset(
    {
        "hced-Aliwal1846-1",
        "hced-Baddowal1846-1",
        "hced-Chilianwallah1849-1",
        "hced-Dharmkot1846-1",
        "hced-Ferozeshah1845-1",
        "hced-Gujrat, Pakistan1849-1",
        "hced-Kineyre1848-1",
        "hced-Mudki1845-1",
        "hced-Multan1848-1849-1",
        "hced-Ramnagar1848-1",
        "hced-Sadulapur1848-1",
        "hced-Sadusam1848-1",
        "hced-Sobraon1846-1",
    }
)
WAVE8_PUNJABI_SIKHS_COMPANY_ERA_CANDIDATE_ID_SHA256 = (
    "7c7f906537f08820aad1388fe772a7fd9a908590b28f90ff10b2278f01b4896a"
)


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "actor_override": "event_bounded_exact_opposing_forces",
        "audit_note": audit_note,
        "canonical_event": canonical_event,
        "cohort": cohort,
        "confidence": confidence,
        "disposition": "promote",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "evidence_refs": evidence,
        "outcome_reversal": False,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "outcome_source_ids": outcomes,
        "raw_row_sha256": WAVE8_PUNJABI_SIKHS_ROW_HASHES[candidate_id],
        "result_type": "win",
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "source_outcome_override": False,
        "war_type": "anti_imperial_revolt",
        "winner_side": 1,
    }


WAVE8_PUNJABI_SIKHS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Anandpur (2nd)1704-1": _contract(
        "hced-Anandpur (2nd)1704-1",
        _canonical(
            "Final Siege and Evacuation of Anandgarh",
            1704,
            "final siege and evacuation, May-20/21 December 1704",
            date_precision="month_to_day_range",
            granularity="siege_termination_and_forced_evacuation",
        ),
        "final_anandgarh_siege_1704",
        [_ANANDGARH_BESIEGERS_ID],
        [_ANANDGARH_KHALSA_ID],
        [
            "wave8_punjabi_sikhs_grewal_white_hawk",
            "wave8_punjabi_sikhs_gupta_vol1",
            "wave8_punjabi_sikhs_khushwant_vol1",
            "wave8_punjabi_sikhs_macauliffe_vol5",
            "wave8_punjabi_sikhs_shah_sri_gursobha",
        ],
        [
            "wave8_punjabi_sikhs_grewal_white_hawk",
            "wave8_punjabi_sikhs_gupta_vol1",
            "wave8_punjabi_sikhs_khushwant_vol1",
            "wave8_punjabi_sikhs_macauliffe_vol5",
            "wave8_punjabi_sikhs_shah_sri_gursobha",
        ],
        (
            "The contract rates only the terminal operational result of the final "
            "blockade: the mixed Mughal-hill coalition cut supply, maintained the "
            "siege, and achieved evacuation of the fort complex. It does not rate "
            "each sortie, starvation, the broken safe-conduct promise, or the "
            "subsequent Sarsa attack as additional Anandpur outcomes."
        ),
        confidence=0.91,
    ),
    "hced-Sarsa1704-1": _contract(
        "hced-Sarsa1704-1",
        _canonical(
            "Battle at the Sarsa Crossing",
            1704,
            "21 December 1704",
            date_precision="day",
            granularity="withdrawal_column_attack_and_dispersal",
        ),
        "sarsa_withdrawal_action_1704",
        [_SARSA_PURSUERS_ID],
        [_SARSA_KHALSA_ID],
        [
            "wave8_punjabi_sikhs_gupta_vol1",
            "wave8_punjabi_sikhs_kaur_march_thesis",
            "wave8_punjabi_sikhs_khushwant_vol1",
            "wave8_punjabi_sikhs_macauliffe_vol5",
            "wave8_punjabi_sikhs_shah_sri_gursobha",
        ],
        [
            "wave8_punjabi_sikhs_gupta_vol1",
            "wave8_punjabi_sikhs_kaur_march_thesis",
            "wave8_punjabi_sikhs_khushwant_vol1",
            "wave8_punjabi_sikhs_macauliffe_vol5",
        ],
        (
            "The pursuing force attacked the separate withdrawing groups, killed "
            "or dispersed most of the bounded column, and forced the survivors "
            "through the flooded crossing. Guru Gobind Singh's escape and the "
            "next Chamkaur engagement remain separate facts; no strategic defeat "
            "or additional massacre outcome is inferred."
        ),
        confidence=0.93,
    ),
}


def _hold(
    candidate_id: str,
    name: str,
    year: int,
    date_text: str,
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
) -> dict[str, Any]:
    return {
        "canonical_event": _canonical(
            name,
            year,
            date_text,
            date_precision="year_uncertain",
            granularity="ambiguous_multi_operation_or_chronology_twin",
        ),
        "disposition": "hold",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "held_hced_owner",
        },
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "hold_category": category,
        "hold_reason": reason,
        "raw_row_sha256": WAVE8_PUNJABI_SIKHS_ROW_HASHES[candidate_id],
        "result_type": "unknown",
        "reviewed_outcome": "unknown",
        "terminal_exclusion": False,
        "unknown_is_never_draw": True,
    }


WAVE8_PUNJABI_SIKHS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Anandpur1700-1": _hold(
        "hced-Anandpur1700-1",
        "Anandpur operations (1700-1701 chronology unresolved)",
        1700,
        "1700-1701 in competing chronologies",
        "reciprocal_cross_lane_chronology_twin",
        (
            "This exact Punjabi Sikhs row and the Sikh Punjab lane's Anandpur 1701 "
            "row may encode the same first-siege/Nirmoh/Basoli sequence under "
            "different chronologies and side labels. Neither can be assigned a "
            "unique event boundary and tactical result, so neither is promoted or "
            "converted to a draw."
        ),
        [
            "wave8_punjabi_sikhs_grewal_white_hawk",
            "wave8_punjabi_sikhs_gupta_vol1",
            "wave8_punjabi_sikhs_shah_sri_gursobha",
        ],
    ),
    "hced-Anandpur (1st)1704-1": _hold(
        "hced-Anandpur (1st)1704-1",
        "Purported first Anandpur battle of 1704",
        1704,
        "1704 label; operation and chronology not uniquely established",
        "unsupported_unique_engagement_boundary",
        (
            "The HCED numbering is not reproduced by the reviewed independent "
            "chronologies. Grewal and Sainapati place the earlier Anandpur battle "
            "before Nirmoh and Basoli, while Gupta numbers several actions before "
            "the final 1704 siege. The row cannot be tied to one separate 1704 "
            "Sikh victory without inventing a boundary, and is held as unknown, "
            "never as a draw."
        ),
        [
            "wave8_punjabi_sikhs_grewal_white_hawk",
            "wave8_punjabi_sikhs_gupta_vol1",
            "wave8_punjabi_sikhs_shah_sri_gursobha",
        ],
    ),
}

WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_PUNJABI_SIKHS_EXCLUSIONS = WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSIONS
WAVE8_PUNJABI_SIKHS_NONPROMOTIONS = {
    **WAVE8_PUNJABI_SIKHS_HOLDS,
    **WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSIONS,
}
WAVE8_PUNJABI_SIKHS_CONTRACT_IDS = frozenset(WAVE8_PUNJABI_SIKHS_CONTRACTS)
WAVE8_PUNJABI_SIKHS_HOLD_IDS = frozenset(WAVE8_PUNJABI_SIKHS_HOLDS)
WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSIONS
)
WAVE8_PUNJABI_SIKHS_EXCLUSION_IDS = WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSION_IDS
WAVE8_PUNJABI_SIKHS_RESERVED_IDS = (
    WAVE8_PUNJABI_SIKHS_CONTRACT_IDS
    | WAVE8_PUNJABI_SIKHS_HOLD_IDS
    | WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSION_IDS
)
WAVE8_PUNJABI_SIKHS_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_PUNJABI_SIKHS_ROW_HASHES
)


WAVE8_PUNJABI_SIKHS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Anandpur (2nd)1704-1": {
        "actions": ["withhold_point"],
        "retained_country": "India",
        "reason": (
            "The city coordinate is not a reviewed geometry for the multi-fort, "
            "months-long Anandpur-Anandgarh siege footprint."
        ),
    },
    "hced-Sarsa1704-1": {
        "actions": ["withhold_point"],
        "retained_country": "India",
        "reason": (
            "HCED's coordinate (22.8300136, 72.6299003) is in Gujarat, not at the "
            "Sarsa crossing and pursuit corridor in Punjab."
        ),
    },
}
WAVE8_PUNJABI_SIKHS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_PUNJABI_SIKHS_CONTRACT_IDS
)
WAVE8_PUNJABI_SIKHS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_PUNJABI_SIKHS_LOCATION_QUARANTINE_ADDITIONS = {
    "country": WAVE8_PUNJABI_SIKHS_COUNTRY_QUARANTINE_ADDITIONS,
    "point": WAVE8_PUNJABI_SIKHS_POINT_QUARANTINE_ADDITIONS,
}

WAVE8_PUNJABI_SIKHS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_PUNJABI_SIKHS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_PUNJABI_SIKHS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}

_SIKH_PUNJAB_RESERVED_IDS = frozenset(
    {
        "hced-Amritsar1634-1",
        "hced-Anandpur1701-1",
        "hced-Baddowal1846-1",
        "hced-Gujrat, Pakistan1797-1",
        "hced-Gurdas Nangal1715-1",
    }
)

WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "wave8_sikh_punjab": {
        "counterpart_module": _SIKH_PUNJAB_MODULE,
        "counterpart_reserved_candidate_ids": sorted(_SIKH_PUNJAB_RESERVED_IDS),
        "disposition": "reciprocal_chronology_twin_hold",
        "evidence_refs": [
            "wave8_punjabi_sikhs_grewal_white_hawk",
            "wave8_punjabi_sikhs_gupta_vol1",
            "wave8_punjabi_sikhs_shah_sri_gursobha",
        ],
        "owner_module": _MODULE_OWNER,
        "owned_candidate_ids": sorted(WAVE8_PUNJABI_SIKHS_RESERVED_IDS),
        "related_candidate_id": "hced-Anandpur1701-1",
        "relationship": "possible_same_anandpur_operation_or_adjacent_phase",
        "shared_boundary_candidate_id": "hced-Anandpur1700-1",
    }
}

_RELATED_ROW_HASHES: dict[str, str] = {
    "hced-Anandpur1701-1": (
        "f67a4c4086cc928cdf58b7e704691a5f593035460d03011d684f5d2e82173e0e"
    ),
    "hced-Baddowal1846-1": (
        "afddca7611c520558de29a1c545e089f1efd688ba8e4b84ca56989f8c838e6f4"
    ),
    "hced-Basoli1702-1": (
        "33036f404dbb10982d8c875e9204b34ef4402dd2e4008a8d890efdecc20ccf6e"
    ),
    "hced-Chamkaur (1st)1704-1": (
        "a428499be12c5c3feff731d029662bd93f950a678eac230b7cde257546263122"
    ),
    "hced-Chamkaur (2nd)1704-1": (
        "64794620d65bfaf8183983028f0e37b260e6a69626164421aefb0412158071d9"
    ),
    "hced-Muktsar1705-1": (
        "030d0af0687ba7e5935cc68c517d51f0ad6e8a6cb48e311dd875943de4086baf"
    ),
    "hced-Nirmohgarh1702-1": (
        "ce4ee17069bfb62e2be6520aa5afcbfca84e7f6dd2341bc53c5ff06302acd75e"
    ),
}

WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Anandpur1701-1": {
        "disposition": "counterpart_lane_hold",
        "owner_module": _SIKH_PUNJAB_MODULE,
        "raw_row_sha256": _RELATED_ROW_HASHES["hced-Anandpur1701-1"],
        "relationship": "possible_chronology_twin_of_anandpur_1700",
    },
    "hced-Baddowal1846-1": {
        "disposition": "counterpart_lane_company_era_event",
        "owner_module": _SIKH_PUNJAB_MODULE,
        "raw_row_sha256": _RELATED_ROW_HASHES["hced-Baddowal1846-1"],
        "relationship": "different_lahore_khalsa_and_british_indian_war",
    },
    "hced-Basoli1702-1": {
        "disposition": "distinct_hced_engagement",
        "owner_module": "unassigned",
        "raw_row_sha256": _RELATED_ROW_HASHES["hced-Basoli1702-1"],
        "relationship": "earlier_distinct_anandpur_campaign_engagement",
    },
    "hced-Chamkaur (1st)1704-1": {
        "disposition": "distinct_hced_engagement_pending_its_own_audit",
        "owner_module": "unassigned",
        "raw_row_sha256": _RELATED_ROW_HASHES["hced-Chamkaur (1st)1704-1"],
        "relationship": "different_event_boundary_not_owned_by_sarsa_contract",
    },
    "hced-Chamkaur (2nd)1704-1": {
        "disposition": "distinct_follow_on_hced_engagement",
        "owner_module": "unassigned",
        "raw_row_sha256": _RELATED_ROW_HASHES["hced-Chamkaur (2nd)1704-1"],
        "relationship": "next_day_fortified_battle_not_sarsa_duplicate",
    },
    "hced-Muktsar1705-1": {
        "disposition": "distinct_later_hced_engagement",
        "owner_module": "unassigned",
        "raw_row_sha256": _RELATED_ROW_HASHES["hced-Muktsar1705-1"],
        "relationship": "later_campaign_battle_not_sarsa_duplicate",
    },
    "hced-Nirmohgarh1702-1": {
        "disposition": "distinct_hced_engagement",
        "owner_module": "unassigned",
        "raw_row_sha256": _RELATED_ROW_HASHES["hced-Nirmohgarh1702-1"],
        "relationship": "earlier_distinct_anandpur_campaign_engagement",
    },
}

WAVE8_PUNJABI_SIKHS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"cross_lane:{key}": value
        for key, value in WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS.items()
    },
    **{
        f"related_hced:{key}": value
        for key, value in WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS.items()
    },
}
WAVE8_PUNJABI_SIKHS_TOUCHED_CANDIDATE_IDS = frozenset(
    WAVE8_PUNJABI_SIKHS_RESERVED_IDS | set(_RELATED_ROW_HASHES)
)


def _duplicate_audit(years: Iterable[int], *aliases: str) -> dict[str, Any]:
    return {
        "aliases": sorted({normalize_label(alias) for alias in aliases}),
        "years": sorted(set(map(int, years))),
    }


WAVE8_PUNJABI_SIKHS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Anandpur1700-1": _duplicate_audit(
        [1699, 1700, 1701],
        "Anandpur",
        "First siege of Anandpur",
        "Anandpur operations",
    ),
    "hced-Anandpur (1st)1704-1": _duplicate_audit(
        [1703, 1704, 1705],
        "Anandpur (1st)",
        "First Battle of Anandpur",
        "First Battle of Anandpur (1704)",
    ),
    "hced-Anandpur (2nd)1704-1": _duplicate_audit(
        [1704, 1705],
        "Anandpur (2nd)",
        "Final Siege and Evacuation of Anandgarh",
        "Second Siege of Anandpur",
        "Siege of Anandgarh",
        "Siege of Anandpur",
    ),
    "hced-Sarsa1704-1": _duplicate_audit(
        [1704, 1705],
        "Battle at the Sarsa Crossing",
        "Battle of Sarsa",
        "Battle of Sirsa",
        "Sarsa",
        "Sarsa River",
        "Sirsa",
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_label_inventory_pins": (
            WAVE8_PUNJABI_SIKHS_ADJACENT_LABEL_INVENTORY_PINS
        ),
        "company_era_candidate_ids": sorted(
            WAVE8_PUNJABI_SIKHS_COMPANY_ERA_CANDIDATE_IDS
        ),
        "contracts": WAVE8_PUNJABI_SIKHS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_PUNJABI_SIKHS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_PUNJABI_SIKHS_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_PUNJABI_SIKHS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": WAVE8_PUNJABI_SIKHS_HOLDS,
        "integration_dispositions": WAVE8_PUNJABI_SIKHS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_PUNJABI_SIKHS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": WAVE8_PUNJABI_SIKHS_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": (
            WAVE8_PUNJABI_SIKHS_LOCATION_QUARANTINE_REASONS
        ),
        "outcome_overrides": WAVE8_PUNJABI_SIKHS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_PUNJABI_SIKHS_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": (
            WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS
        ),
        "row_hashes": WAVE8_PUNJABI_SIKHS_ROW_HASHES,
        "sources": WAVE8_PUNJABI_SIKHS_SOURCES,
        "terminal_exclusions": WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSIONS,
    }


def wave8_punjabi_sikhs_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_PUNJABI_SIKHS_FINAL_AUDIT_SIGNATURE = (
    "1567c5bbb41a7bd394dc82497cd96aaaa79b51e6c919403b5483b7ae27a4e48d"
)


def _candidate_id_sha256(values: Iterable[str]) -> str:
    return hashlib.sha256(
        "".join(f"{value}\n" for value in sorted(map(str, values))).encode("utf-8")
    ).hexdigest()


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_PUNJABI_SIKHS_CONTRACTS),
        len(WAVE8_PUNJABI_SIKHS_HOLDS),
        len(WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSIONS),
    ) != (2, 2, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_PUNJABI_SIKHS_ENTITIES), len(WAVE8_PUNJABI_SIKHS_SOURCES)) != (
        4,
        7,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_PUNJABI_SIKHS_RESERVED_IDS != (
        WAVE8_PUNJABI_SIKHS_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    if _candidate_id_sha256(WAVE8_PUNJABI_SIKHS_RESERVED_IDS) != (
        WAVE8_PUNJABI_SIKHS_EXACT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} exact candidate digest changed")
    if _candidate_id_sha256(WAVE8_PUNJABI_SIKHS_COMPANY_ERA_CANDIDATE_IDS) != (
        WAVE8_PUNJABI_SIKHS_COMPANY_ERA_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} company-era boundary digest changed")
    if wave8_punjabi_sikhs_audit_signature() != (
        WAVE8_PUNJABI_SIKHS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    dispositions = (
        WAVE8_PUNJABI_SIKHS_CONTRACT_IDS,
        WAVE8_PUNJABI_SIKHS_HOLD_IDS,
        WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSION_IDS,
    )
    for index, left in enumerate(dispositions):
        for right in dispositions[index + 1 :]:
            if left & right:
                raise ValueError(f"{_LANE_NAME} dispositions overlap")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_PUNJABI_SIKHS_SOURCES
    }
    if len(source_by_id) != len(WAVE8_PUNJABI_SIKHS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    source_families = {
        str(source["source_family_id"])
        for source in WAVE8_PUNJABI_SIKHS_SOURCES
    }
    if len(source_families) != len(WAVE8_PUNJABI_SIKHS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source-family independence changed")
    for source in WAVE8_PUNJABI_SIKHS_SOURCES:
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_PUNJABI_SIKHS_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_PUNJABI_SIKHS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_ids = {
        "punjab",
        "punjabi_sikhs",
        "sikh_empire",
        "sikh_punjab",
        "sikhs",
    }
    used_sources: set[str] = set()
    used_entities: set[str] = set()
    for entity in WAVE8_PUNJABI_SIKHS_ENTITIES:
        if str(entity["id"]) in forbidden_ids or entity["aliases"]:
            raise ValueError(f"{_LANE_NAME} installed a generic actor or alias")
        if (int(entity["start_year"]), int(entity["end_year"])) != (1704, 1704):
            raise ValueError(f"{_LANE_NAME} entity is not event bounded")
        source_ids = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(source_ids) or not set(source_ids) <= set(
            source_by_id
        ):
            raise ValueError(f"{_LANE_NAME} entity sources changed")
        used_sources.update(source_ids)

    for candidate_id, contract in WAVE8_PUNJABI_SIKHS_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_PUNJABI_SIKHS_ROW_HASHES[
            candidate_id
        ]:
            raise ValueError(f"{_LANE_NAME} contract hash drifted")
        for field in (
            "evidence_refs",
            "outcome_source_ids",
            "outcome_source_family_ids",
        ):
            if not _is_sorted_unique(contract[field]) or not contract[field]:
                raise ValueError(f"{_LANE_NAME} contract evidence is not canonical")
        evidence = set(map(str, contract["evidence_refs"]))
        outcomes = set(map(str, contract["outcome_source_ids"]))
        if not outcomes <= evidence or not evidence <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} contract evidence changed")
        expected_families = {
            _SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes
        }
        if set(contract["outcome_source_family_ids"]) != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome families changed")
        if len(expected_families) < 4:
            raise ValueError(f"{_LANE_NAME} outcome lacks independent corroboration")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} contract sides changed")
        if not (side_1 | side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} contract references unknown entity")
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} outcome semantics changed")
        used_sources.update(evidence)
        used_entities.update(side_1 | side_2)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")

    forbidden_nonpromotion_keys = {
        "outcome_source_ids",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
        "winners",
        "losers",
    }
    for candidate_id, hold in WAVE8_PUNJABI_SIKHS_HOLDS.items():
        if (
            hold["raw_row_sha256"]
            != WAVE8_PUNJABI_SIKHS_ROW_HASHES[candidate_id]
            or hold["disposition"] != "hold"
            or hold["reviewed_outcome"] != "unknown"
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
            or hold["terminal_exclusion"] is not False
            or forbidden_nonpromotion_keys & set(hold)
        ):
            raise ValueError(f"{_LANE_NAME} hold semantics changed")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence changed")
        used_sources.update(evidence)

    if set(WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS) != {
        "wave8_sikh_punjab"
    }:
        raise ValueError(f"{_LANE_NAME} cross-lane inventory changed")
    cross_lane = WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS[
        "wave8_sikh_punjab"
    ]
    if (
        set(cross_lane["owned_candidate_ids"])
        != WAVE8_PUNJABI_SIKHS_RESERVED_IDS
        or set(cross_lane["counterpart_reserved_candidate_ids"])
        != _SIKH_PUNJAB_RESERVED_IDS
        or cross_lane["shared_boundary_candidate_id"]
        != "hced-Anandpur1700-1"
        or cross_lane["related_candidate_id"] != "hced-Anandpur1701-1"
    ):
        raise ValueError(f"{_LANE_NAME} reciprocal Sikh boundary changed")
    cross_evidence = list(map(str, cross_lane["evidence_refs"]))
    if not _is_sorted_unique(cross_evidence) or not set(cross_evidence) <= set(
        source_by_id
    ):
        raise ValueError(f"{_LANE_NAME} cross-lane evidence changed")
    used_sources.update(cross_evidence)

    if set(WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS) != set(
        _RELATED_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} related HCED inventory changed")
    for candidate_id, item in WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS.items():
        if item["raw_row_sha256"] != _RELATED_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} related HCED hash changed")

    expected_integration = {
        **{
            f"cross_lane:{key}": value
            for key, value in WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS.items()
        },
        **{
            f"related_hced:{key}": value
            for key, value in WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS.items()
        },
    }
    if WAVE8_PUNJABI_SIKHS_INTEGRATION_DISPOSITIONS != expected_integration:
        raise ValueError(f"{_LANE_NAME} integration inventory changed")

    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if WAVE8_PUNJABI_SIKHS_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_PUNJABI_SIKHS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine changed")
    if WAVE8_PUNJABI_SIKHS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if (
        WAVE8_PUNJABI_SIKHS_OUTCOME_OVERRIDES
        or WAVE8_PUNJABI_SIKHS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_PUNJABI_SIKHS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")
    if set(WAVE8_PUNJABI_SIKHS_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_PUNJABI_SIKHS_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate audit is incomplete")


def _is_exact_punjabi_sikhs_label(value: Any) -> bool:
    return normalize_label(value) == "punjabi sikhs"


def _label_candidate_ids(
    hced_rows: Iterable[Mapping[str, Any]], label: str
) -> set[str]:
    return {
        str(row.get("candidate_id") or "")
        for row in hced_rows
        if label
        in {
            normalize_label(row.get("side_1_raw")),
            normalize_label(row.get("side_2_raw")),
        }
    }


def validate_wave8_punjabi_sikhs_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Fail closed on the exact cohort and every adjacent Sikh boundary."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_PUNJABI_SIKHS_CONTRACTS,
        WAVE8_PUNJABI_SIKHS_HOLDS,
        lane_name=_LANE_NAME,
    )
    exact_ids = _label_candidate_ids(hced_rows, "punjabi sikhs")
    if exact_ids != WAVE8_PUNJABI_SIKHS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Punjabi Sikhs inventory changed: "
            f"{sorted(exact_ids)}"
        )
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        indexed.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, expected_hash in _RELATED_ROW_HASHES.items():
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1 or canonical_hced_row_sha256(rows[0]) != expected_hash:
            raise ValueError(f"{_LANE_NAME} related HCED boundary changed: {candidate_id}")

    for label, pin in WAVE8_PUNJABI_SIKHS_ADJACENT_LABEL_INVENTORY_PINS.items():
        ids = _label_candidate_ids(hced_rows, label)
        if len(ids) != pin["count"] or _candidate_id_sha256(ids) != pin[
            "candidate_id_sha256"
        ]:
            raise ValueError(f"{_LANE_NAME} adjacent {label!r} inventory changed")
    company_ids = {
        str(row.get("candidate_id") or "")
        for row in hced_rows
        if row.get("year_low") is not None
        and row.get("year_high") is not None
        and int(row["year_low"]) >= 1845
        and int(row["year_high"]) <= 1849
        and {
            normalize_label(row.get("side_1_raw")),
            normalize_label(row.get("side_2_raw")),
        }
        & {"punjab", "punjabi sikhs", "sikh punjab", "sikhs"}
    }
    if company_ids != WAVE8_PUNJABI_SIKHS_COMPANY_ERA_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} company-era Sikh/Punjab inventory changed")

    from . import wave8_sikh_punjab as sikh_lane

    reciprocal = sikh_lane.WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS.get(
        "hced-Anandpur1700-1"
    )
    if (
        sikh_lane.WAVE8_SIKH_PUNJAB_RESERVED_IDS != _SIKH_PUNJAB_RESERVED_IDS
        or not reciprocal
        or reciprocal.get("related_candidate_id") != "hced-Anandpur1701-1"
        or reciprocal.get("raw_row_sha256")
        != WAVE8_PUNJABI_SIKHS_ROW_HASHES["hced-Anandpur1700-1"]
    ):
        raise ValueError(f"{_LANE_NAME} reciprocal Sikh Punjab contract changed")
    if WAVE8_PUNJABI_SIKHS_RESERVED_IDS & sikh_lane.WAVE8_SIKH_PUNJAB_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} overlaps Sikh Punjab exact ownership")

    return {
        "company_era_boundary_rows": len(company_ids),
        "cross_lane_dispositions": len(
            WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS
        ),
        "holds": result["holds"],
        "promotion_contracts": result["promotion_contracts"],
        "related_hced_dispositions": len(
            WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_PUNJABI_SIKHS_EXPECTED_CANDIDATE_IDS),
        "reviewed_unresolved_hced_rows": len(WAVE8_PUNJABI_SIKHS_RESERVED_IDS),
        "terminal_exclusions": len(
            WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSION_IDS
        ),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        value = row.get(field)
        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        value = str(row.get(field) or "")
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


def _validate_release_overlap(existing_events: list[Mapping[str, Any]]) -> int:
    lane_events = [
        event
        for event in existing_events
        if event.get("hced_candidate_id") in WAVE8_PUNJABI_SIKHS_CONTRACT_IDS
        or str(event.get("id") or "").startswith(_EVENT_ID_PREFIX)
    ]
    if not lane_events:
        return 0
    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for event in lane_events:
        by_candidate.setdefault(str(event.get("hced_candidate_id") or ""), []).append(
            event
        )
    if set(by_candidate) != WAVE8_PUNJABI_SIKHS_CONTRACT_IDS or any(
        len(events) != 1 for events in by_candidate.values()
    ):
        raise ValueError(f"{_LANE_NAME} partial or duplicate release overlap")
    if any(
        not str(event.get("id") or "").startswith(_EVENT_ID_PREFIX)
        for event in lane_events
    ):
        raise ValueError(f"{_LANE_NAME} release ownership prefix changed")
    return len(lane_events)


def validate_wave8_punjabi_sikhs_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on cross-lane ownership and probable dataset twins."""

    validate_wave8_punjabi_sikhs_queue_contracts(hced_rows)
    audited = {
        (year, alias)
        for review in WAVE8_PUNJABI_SIKHS_IWBD_ZERO_OVERLAP_AUDIT.values()
        for year in review["years"]
        for alias in review["aliases"]
    }
    unexpected_iwbd = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _row_year(row) is not None
        and (_row_year(row), normalize_label(row.get("name"))) in audited
    )
    if unexpected_iwbd:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD twin(s): {unexpected_iwbd}"
        )

    existing = list(existing_events)
    overlap_count = _validate_release_overlap(existing)
    unexpected_release = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id")
        not in WAVE8_PUNJABI_SIKHS_RESERVED_IDS
        and not str(event.get("id") or "").startswith(_EVENT_ID_PREFIX)
        and _row_year(event) is not None
        and (_row_year(event), normalize_label(event.get("name"))) in audited
    )
    if unexpected_release:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): "
            f"{unexpected_release}"
        )
    held_release = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_PUNJABI_SIKHS_HOLD_IDS
    )
    if held_release:
        raise ValueError(f"{_LANE_NAME} held rows were emitted: {held_release}")

    return {
        "cross_lane_dispositions": len(
            WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": 0,
        "integration_dispositions": len(
            WAVE8_PUNJABI_SIKHS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "related_hced_dispositions": len(
            WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS
        ),
        "release_lane_overlap": overlap_count,
        "release_probable_twins": 0,
    }


def install_wave8_punjabi_sikhs_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_PUNJABI_SIKHS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_punjabi_sikhs_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_PUNJABI_SIKHS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_PUNJABI_SIKHS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_PUNJABI_SIKHS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_punjabi_sikhs_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_punjabi_sikhs_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_PUNJABI_SIKHS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_punjabi_sikhs_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_PUNJABI_SIKHS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_punjabi_sikhs_counts() -> dict[str, int]:
    _validate_static()
    return {
        "company_era_boundary_rows": len(
            WAVE8_PUNJABI_SIKHS_COMPANY_ERA_CANDIDATE_IDS
        ),
        "country_quarantine_additions": len(
            WAVE8_PUNJABI_SIKHS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": len(
            WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_PUNJABI_SIKHS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_PUNJABI_SIKHS_HOLDS),
        "integration_dispositions": len(
            WAVE8_PUNJABI_SIKHS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_PUNJABI_SIKHS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_PUNJABI_SIKHS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_PUNJABI_SIKHS_ENTITIES),
        "new_sources": len(WAVE8_PUNJABI_SIKHS_SOURCES),
        "newly_rated_events": len(WAVE8_PUNJABI_SIKHS_CONTRACTS),
        "outcome_overrides": len(WAVE8_PUNJABI_SIKHS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_PUNJABI_SIKHS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_PUNJABI_SIKHS_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_PUNJABI_SIKHS_EXPECTED_CANDIDATE_IDS),
        "reviewed_unresolved_hced_rows": len(WAVE8_PUNJABI_SIKHS_RESERVED_IDS),
        "terminal_exclusions": len(
            WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSIONS
        ),
        "touched_hced_rows": len(WAVE8_PUNJABI_SIKHS_TOUCHED_CANDIDATE_IDS),
    }


def wave8_punjabi_sikhs_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_PUNJABI_SIKHS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_PUNJABI_SIKHS_POINT_QUARANTINE_ADDITIONS,
    }


_validate_static()
