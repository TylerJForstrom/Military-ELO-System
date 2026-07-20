"""Fail-closed exact contracts for four deferred Wave 8 HCED rows.

This lane owns only Kharda (1795), Sikasso (1887-1888), Balapur (1720),
and Ratanpur (1720). It deliberately opens no label policy or alias. The
Kharda composite is interpreted only inside its fingerprinted row; the two
1720 rows use separate event-bounded formations on both sides and never the
post-1724 Hyderabad state; and Tieba's Kenedougou defense exists only for the
exact Sikasso siege. Unknown outcomes are rejected rather than converted to
draws.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from ..canonical import hced_point_geometry_validation_error
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
    "WAVE8_FOLLOWUP_B_CONTRACT_IDS",
    "WAVE8_FOLLOWUP_B_CONTRACTS",
    "WAVE8_FOLLOWUP_B_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_FOLLOWUP_B_ENTITIES",
    "WAVE8_FOLLOWUP_B_EXISTING_ENTITY_CONTRACTS",
    "WAVE8_FOLLOWUP_B_EXPECTED_CANDIDATE_IDS",
    "WAVE8_FOLLOWUP_B_EXPECTED_RELEASE_EVENT_IDS",
    "WAVE8_FOLLOWUP_B_FINAL_AUDIT_SIGNATURE",
    "WAVE8_FOLLOWUP_B_FUNNEL_AUDIT",
    "WAVE8_FOLLOWUP_B_FUNNEL_LABELS",
    "WAVE8_FOLLOWUP_B_HOLDS",
    "WAVE8_FOLLOWUP_B_LOCATION_QUARANTINE_REASONS",
    "WAVE8_FOLLOWUP_B_NEW_SOURCE_IDS",
    "WAVE8_FOLLOWUP_B_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_FOLLOWUP_B_RAW_ROW_CONTRACTS",
    "WAVE8_FOLLOWUP_B_RESERVED_IDS",
    "WAVE8_FOLLOWUP_B_REUSED_SOURCE_IDS",
    "WAVE8_FOLLOWUP_B_ROW_HASHES",
    "WAVE8_FOLLOWUP_B_SOURCES",
    "install_wave8_followup_b_entities",
    "install_wave8_followup_b_sources",
    "promote_wave8_followup_b_contracts",
    "validate_wave8_followup_b_final_audit",
    "validate_wave8_followup_b_funnel",
    "validate_wave8_followup_b_integration_dispositions",
    "validate_wave8_followup_b_queue_contracts",
    "validate_wave8_followup_b_release_inventory",
    "wave8_followup_b_audit_signature",
    "wave8_followup_b_cohort_counts",
    "wave8_followup_b_counts",
    "wave8_followup_b_metadata",
)


_LANE_NAME = "Wave 8 exact deferred-row follow-up B audit"
_MODULE_OWNER = "military_elo.promotion.wave8_followup_b"
_EVENT_ID_PREFIX = "hced_wave8_followup_b_"

_MARATHA = "maratha_confederacy"
_HYDERABAD = "hyderabad_asaf_jahi_state_1724"
_KENEDOUGOU = "tieba_led_kenedougou_defense_sikasso_1887_1888"
_WASSOULOU = "wassoulou_empire_samori_ture"
_NIZAM_FORCE = "nizam_ul_mulk_deccan_campaign_force_1720"
_ALAM_ALI_FORCE = "alam_ali_khan_sayyid_aligned_coalition_balapur_1720"
_DILAWAR_ALI_FORCE = "dilawar_ali_khan_sayyid_aligned_force_ratanpur_1720"

_KHARDA = "hced-Kharda1795-1"
_SIKASSO = "hced-Sikasso1887-1888-1"
_BALAPUR = "hced-Balapur1720-1"
_RATANPUR = "hced-Ratanpur1720-1"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    evidence_roles: Iterable[str],
    *,
    accessed: str = "2026-07-19",
) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": accessed,
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


# ``telangana_asaf_jahi`` is an existing canonical source record and is
# repeated byte-for-byte here so installation verifies rather than mutates it.
WAVE8_FOLLOWUP_B_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "telangana_asaf_jahi",
        "History of Ranga Reddy district",
        "https://rangareddy.telangana.gov.in/history/",
        "Government of Telangana",
        "official_or_academic_reference",
        "telangana_district_history",
        ["identity_boundary_or_context_reference"],
        accessed="2026-07-15",
    ),
    _source(
        "wave8_followup_b_ird_etats_kong",
        "Louis Tauxier, Les Etats de Kong (Cote d'Ivoire)",
        (
            "https://horizon.documentation.ird.fr/exl-doc/pleins_textes/"
            "2022-12/010075008.pdf"
        ),
        "Editions Karthala; hosted by IRD Horizon",
        "scholarly_critical_edition",
        "tauxier_etats_kong_karthala_2003",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_followup_b_maharashtra_akola_history",
        "Akola District Gazetteer: History and Archaeology",
        (
            "https://gazetteers.maharashtra.gov.in/"
            "cultural.maharashtra.gov.in/english/gazetteer/"
            "Akola%20District/history.html"
        ),
        "Maharashtra State Gazetteers",
        "official_district_gazetteer",
        "maharashtra_akola_district_gazetteer",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_followup_b_maharashtra_balapur_places",
        "Akola District Gazetteer: Balapur",
        (
            "https://www.gazetteers.maharashtra.gov.in/"
            "cultural.maharashtra.gov.in/english/gazetteer/AKOLA/"
            "places_Balapur.html"
        ),
        "Maharashtra State Gazetteers",
        "official_district_gazetteer",
        "maharashtra_akola_district_gazetteer",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_followup_b_maharashtra_history_ch8",
        "History of Maharashtra: Maratha Period, Chapter VIII",
        (
            "https://gazetteers.maharashtra.gov.in/"
            "cultural.maharashtra.gov.in/english/gazetteer/"
            "History%20Part/History_III/chapter_8.pdf"
        ),
        "Maharashtra State Gazetteers",
        "official_state_history",
        "maharashtra_state_history_maratha_period",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_followup_b_maharashtra_kharda_places",
        "Kharda Fort",
        "https://ahmednagar.nic.in/tourist-place/kharda-fort/",
        "District Administration Ahilyanagar, Government of Maharashtra",
        "official_district_history",
        "ahilyanagar_district_kharda_fort",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_followup_b_maharashtra_solapur_maratha",
        "Solapur District Gazetteer: Maratha Period",
        (
            "https://www.gazetteers.maharashtra.gov.in/"
            "cultural.maharashtra.gov.in/english/gazetteer/Solapur/"
            "his_maratha%20period.html"
        ),
        "Maharashtra State Gazetteers",
        "official_district_gazetteer",
        "maharashtra_solapur_district_gazetteer",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_followup_b_openedition_ird_cotton",
        "Thomas J. Bassett, Le choc des empires, 1880-1911",
        "https://books.openedition.org/irdeditions/10199",
        "IRD Editions / OpenEdition Books",
        "scholarly_monograph_chapter",
        "bassett_cotton_cote_ivoire_2002",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_followup_b_persee_sikasso_1898",
        "La prise de Sikaso",
        (
            "https://education.persee.fr/doc/"
            "magen_1257-5593_1898_num_65_34_32710"
        ),
        "Manuel general de l'instruction primaire / Persee",
        "digitized_near_contemporary_periodical",
        "manuel_general_instruction_primaire_1898",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_followup_b_persee_tymowski_sikasso",
        (
            "Michal Tymowski, Le developpement de Sikasso, capitale du "
            "Kenedugu"
        ),
        (
            "https://www.persee.fr/doc/"
            "outre_0300-9513_1981_num_68_250_2316"
        ),
        "Revue francaise d'histoire d'outre-mer / Persee",
        "peer_reviewed_history_article",
        "tymowski_sikasso_1981",
        ["identity_boundary_or_context_reference"],
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_FOLLOWUP_B_SOURCES
}


WAVE8_FOLLOWUP_B_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _KENEDOUGOU,
        "name": "Tieba-led Kenedougou defense at Sikasso (1887-1888)",
        "kind": "siege_bounded_defending_formation",
        "start_year": 1887,
        "end_year": 1888,
        "region": "Sikasso and the southern Niger bend",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Alias-free formation for Tieba's Kenedougou defenders during "
            "Samori's 1887-1888 siege of Sikasso. Sources disagree about broader "
            "ruler chronology, so this contract asserts neither a reign date nor "
            "the state's historical lifetime. No Kenedougou, Sikasso, Traore, "
            "Mandingo, Mali, or modern-country alias is opened. This identity is "
            "never Wassoulou and no predecessor or successor inherits its Elo."
        ),
        "source_ids": [
            "wave8_followup_b_ird_etats_kong",
            "wave8_followup_b_openedition_ird_cotton",
            "wave8_followup_b_persee_sikasso_1898",
            "wave8_followup_b_persee_tymowski_sikasso",
        ],
    },
    {
        "id": _NIZAM_FORCE,
        "name": "Nizam-ul-Mulk's Deccan campaign force (1720)",
        "kind": "campaign_bounded_mughal_formation",
        "start_year": 1720,
        "end_year": 1720,
        "region": "Khandesh, Berar, and the northern Deccan",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to Chin Kilich Khan Nizam-ul-Mulk's 1720 formation in the "
            "campaign against the Sayyid-aligned imperial forces at Ratanpur "
            "and Balapur. It was a Mughal-era personal campaign formation, not "
            "the Asaf Jahi State of Hyderabad. Telangana's official history "
            "places the autonomous Deccan and Asaf Jahi dynastic boundary at "
            "Shakarkheda in 1724, so this identity must never be extended to or "
            "merged with Hyderabad State (1724-1948). No Nizam, Hyderabad, "
            "Deccan, or Mughal label alias is opened, and no successor inherits "
            "its Elo."
        ),
        "source_ids": [
            "telangana_asaf_jahi",
            "wave8_followup_b_maharashtra_akola_history",
            "wave8_followup_b_maharashtra_balapur_places",
            "wave8_followup_b_maharashtra_history_ch8",
        ],
    },
    {
        "id": _ALAM_ALI_FORCE,
        "name": "Alam Ali Khan's Sayyid-aligned coalition at Balapur (1720)",
        "kind": "event_bounded_imperial_coalition",
        "start_year": 1720,
        "end_year": 1720,
        "region": "Berar and the northern Deccan",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Event-bounded opposing coalition at Balapur under Alam Ali Khan, "
            "aligned with the Sayyid brothers and including source-named Maratha "
            "supporters. It is not the undifferentiated Mughal Empire, and no "
            "imperial, Maratha, Hyderabad, predecessor, or successor rating is "
            "inherited."
        ),
        "source_ids": [
            "wave8_followup_b_maharashtra_akola_history",
            "wave8_followup_b_maharashtra_balapur_places",
            "wave8_followup_b_maharashtra_history_ch8",
        ],
    },
    {
        "id": _DILAWAR_ALI_FORCE,
        "name": "Dilawar Ali Khan's Sayyid-aligned force at Ratanpur (1720)",
        "kind": "event_bounded_imperial_force",
        "start_year": 1720,
        "end_year": 1720,
        "region": "Khandesh and the northern Deccan",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Event-bounded opposing force at Ratanpur under Dilawar Ali Khan in "
            "the Sayyid-aligned campaign against Nizam-ul-Mulk. It is not the "
            "undifferentiated Mughal Empire, and no imperial, Hyderabad, "
            "predecessor, or successor rating is inherited."
        ),
        "source_ids": [
            "wave8_followup_b_maharashtra_akola_history",
            "wave8_followup_b_maharashtra_history_ch8",
        ],
    },
)


# Existing records are read-only dependencies.  Their projections are pinned
# so a widened window or alias mutation cannot silently change this lane.
WAVE8_FOLLOWUP_B_EXISTING_ENTITY_CONTRACTS: dict[str, dict[str, Any]] = {
    _HYDERABAD: {
        "id": _HYDERABAD,
        "name": "Asaf Jahi State of Hyderabad",
        "kind": "princely_state",
        "start_year": 1724,
        "end_year": 1948,
        "aliases": [],
    },
    _MARATHA: {
        "id": _MARATHA,
        "name": "Maratha Confederacy",
        "kind": "confederation",
        "start_year": 1674,
        "end_year": 1818,
        "aliases": ["Marathas", "Maratha Empire"],
    },
    _WASSOULOU: {
        "id": _WASSOULOU,
        "name": "Wassoulou Empire (Samori Ture)",
        "kind": "empire",
        "start_year": 1878,
        "end_year": 1898,
        "aliases": ["Mandingos"],
    },
}


WAVE8_FOLLOWUP_B_ROW_HASHES: dict[str, str] = {
    _BALAPUR: "6c8a5c665b336e0bacd5602d1bb923b1267ea6a0b2f97e8ef8e96186823f42a2",
    _KHARDA: "83be482c4b3d480c1339f7e7d5d3b551742322f23a551c10fca992562b2d12eb",
    _RATANPUR: "692aad2edf66fc1ea31585e2900fee5990ac92c7df626fb2a4a2d2c08d3e476f",
    _SIKASSO: "2787ccfe72f8d8b9dc04323dd69ad8b175a57047f3622102d8ab9c89b5684c4b",
}

WAVE8_FOLLOWUP_B_RAW_ROW_CONTRACTS: dict[str, dict[str, Any]] = {
    _BALAPUR: {
        "source_record_id": "Balapur1720",
        "name": "Balapur",
        "year_low": 1720,
        "year_high": 1720,
        "year_best": 1720,
        "side_1_raw": "Hyderabad",
        "side_2_raw": "Mughal Empire",
        "winner_raw": "Hyderabad",
        "loser_raw": "Mughal Empire",
    },
    _KHARDA: {
        "source_record_id": "Kharda1795",
        "name": "Kharda",
        "year_low": 1795,
        "year_high": 1795,
        "year_best": 1795,
        "side_1_raw": "Marathas, Tukaji Hulkar, Berar",
        "side_2_raw": "Hyderabad",
        "winner_raw": "Marathas, Tukaji Hulkar, Berar",
        "loser_raw": "Hyderabad",
    },
    _RATANPUR: {
        "source_record_id": "Ratanpur1720",
        "name": "Ratanpur",
        "year_low": 1720,
        "year_high": 1720,
        "year_best": 1720,
        "side_1_raw": "Hyderabad",
        "side_2_raw": "Mughal Empire",
        "winner_raw": "Hyderabad",
        "loser_raw": "Mughal Empire",
    },
    _SIKASSO: {
        "source_record_id": "Sikasso1887-1888",
        "name": "Sikasso",
        "year_low": 1887,
        "year_high": 1888,
        "year_best": 1888,
        "side_1_raw": "Kenedougou",
        "side_2_raw": "Mandingos",
        "winner_raw": "Kenedougou",
        "loser_raw": "Mandingos",
    },
}

WAVE8_FOLLOWUP_B_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_FOLLOWUP_B_ROW_HASHES
)


WAVE8_FOLLOWUP_B_FUNNEL_LABELS = frozenset(
    {"kenedougou", "marathas tukaji hulkar berar"}
)
WAVE8_FOLLOWUP_B_FUNNEL_AUDIT: dict[str, Any] = {
    "required_absent_labels": sorted(WAVE8_FOLLOWUP_B_FUNNEL_LABELS),
    "reserved_candidate_ids": sorted(WAVE8_FOLLOWUP_B_EXPECTED_CANDIDATE_IDS),
}


def _canonical(
    name: str,
    low: int,
    high: int,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{low}:{high}",
        "date_precision": "year" if low == high else "year_range",
        "date_text": str(low) if low == high else f"{low}-{high}",
        "granularity": granularity,
        "name": name,
        "year_low": low,
        "year_high": high,
    }


def _source_families(source_ids: Iterable[str]) -> list[str]:
    return sorted(
        {
            str(_SOURCE_BY_ID[str(source_id)]["source_family_id"])
            for source_id in source_ids
        }
    )


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    identity_source_ids: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    boundary_source_ids: Iterable[str] = (),
    cohort: str,
    confidence: float,
    war_type: str,
    actor_override: str,
) -> dict[str, Any]:
    identities = sorted(set(map(str, identity_source_ids)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    boundaries = sorted(set(map(str, boundary_source_ids)))
    evidence = sorted(set((*identities, *outcomes, *boundaries)))
    return {
        "raw_row_sha256": WAVE8_FOLLOWUP_B_ROW_HASHES[candidate_id],
        "raw_actor_contract": dict(
            WAVE8_FOLLOWUP_B_RAW_ROW_CONTRACTS[candidate_id]
        ),
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": evidence,
        "identity_source_ids": identities,
        "identity_source_family_ids": _source_families(identities),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": _source_families(outcomes),
        "boundary_source_ids": boundaries,
        "boundary_source_family_ids": _source_families(boundaries),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "source_date_override": False,
        "actor_override": actor_override,
        "candidate_key_required": True,
        "generic_label_fallback": False,
        "unknown_outcome_policy": "reject",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_FOLLOWUP_B_CONTRACTS: dict[str, dict[str, Any]] = {
    _BALAPUR: _contract(
        _BALAPUR,
        _canonical(
            "Battle of Balapur",
            1720,
            1720,
            "single_battle_in_nizam_ul_mulks_1720_deccan_campaign",
        ),
        [_NIZAM_FORCE],
        [_ALAM_ALI_FORCE],
        [
            "telangana_asaf_jahi",
            "wave8_followup_b_maharashtra_akola_history",
            "wave8_followup_b_maharashtra_balapur_places",
            "wave8_followup_b_maharashtra_history_ch8",
        ],
        [
            "wave8_followup_b_maharashtra_akola_history",
            "wave8_followup_b_maharashtra_balapur_places",
            "wave8_followup_b_maharashtra_history_ch8",
        ],
        (
            "Maharashtra's Akola and statewide histories identify "
            "Nizam-ul-Mulk's victory over Alam Ali Khan's Sayyid-aligned "
            "coalition at Balapur in 1720. Both sides are bounded formations: "
            "the raw 'Hyderabad' shorthand is not back-projected before 1724, "
            "and the opposing coalition is not charged to the whole Mughal "
            "Empire."
        ),
        boundary_source_ids=["telangana_asaf_jahi"],
        cohort="nizam_ul_mulk_1720_deccan_campaign",
        confidence=0.92,
        war_type="civil_war",
        actor_override="candidate_keyed_pre_asaf_jahi_campaign_force",
    ),
    _KHARDA: _contract(
        _KHARDA,
        _canonical(
            "Battle of Kharda",
            1795,
            1795,
            "single_battle_in_the_maratha_nizam_war",
        ),
        [_MARATHA],
        [_HYDERABAD],
        [
            "wave8_followup_b_maharashtra_kharda_places",
            "wave8_followup_b_maharashtra_solapur_maratha",
        ],
        [
            "wave8_followup_b_maharashtra_kharda_places",
            "wave8_followup_b_maharashtra_solapur_maratha",
        ],
        (
            "Two Maharashtra government gazetteer volumes identify the "
            "combined Maratha victory over Nizam Ali Khan's Asaf Jahi Hyderabad "
            "force at Kharda. The source's "
            "composite 'Marathas, Tukaji Hulkar, Berar' is mapped to the "
            "existing Maratha Confederacy only for this fingerprinted row and "
            "never becomes an alias."
        ),
        cohort="maratha_nizam_war_1795",
        confidence=0.90,
        war_type="interstate",
        actor_override="candidate_keyed_exact_composite_maratha_row",
    ),
    _RATANPUR: _contract(
        _RATANPUR,
        _canonical(
            "Battle of Ratanpur",
            1720,
            1720,
            "single_battle_in_nizam_ul_mulks_1720_deccan_campaign",
        ),
        [_NIZAM_FORCE],
        [_DILAWAR_ALI_FORCE],
        [
            "telangana_asaf_jahi",
            "wave8_followup_b_maharashtra_akola_history",
            "wave8_followup_b_maharashtra_history_ch8",
        ],
        [
            "wave8_followup_b_maharashtra_akola_history",
            "wave8_followup_b_maharashtra_history_ch8",
        ],
        (
            "Maharashtra's Akola history and statewide Maratha-period history "
            "identify Nizam-ul-Mulk's 1720 defeat of Dilawar Ali Khan's "
            "Sayyid-aligned force at Ratanpur. Both sides are bounded to this "
            "campaign: the winner is never the post-1724 Hyderabad State and "
            "the loser is never the undifferentiated Mughal Empire."
        ),
        boundary_source_ids=["telangana_asaf_jahi"],
        cohort="nizam_ul_mulk_1720_deccan_campaign",
        confidence=0.90,
        war_type="civil_war",
        actor_override="candidate_keyed_pre_asaf_jahi_campaign_force",
    ),
    _SIKASSO: _contract(
        _SIKASSO,
        _canonical(
            "Siege of Sikasso",
            1887,
            1888,
            "protracted_siege_of_tiebas_kenedougou_capital",
        ),
        [_KENEDOUGOU],
        [_WASSOULOU],
        [
            "wave8_followup_b_ird_etats_kong",
            "wave8_followup_b_openedition_ird_cotton",
            "wave8_followup_b_persee_sikasso_1898",
            "wave8_followup_b_persee_tymowski_sikasso",
        ],
        [
            "wave8_followup_b_ird_etats_kong",
            "wave8_followup_b_openedition_ird_cotton",
            "wave8_followup_b_persee_sikasso_1898",
        ],
        (
            "IRD/OpenEdition scholarship and the near-contemporary account "
            "agree that Samori's long siege failed and Tieba's Kenedougou "
            "retained Sikasso. The contract distinguishes the two neighboring "
            "states and never treats Kenedougou as a Mandingo/Wassoulou alias."
        ),
        cohort="tieba_kenedougou_wassoulou_war",
        confidence=0.94,
        war_type="interstate",
        actor_override="candidate_keyed_tieba_kenedougou_state",
    ),
}


WAVE8_FOLLOWUP_B_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_FOLLOWUP_B_CONTRACT_IDS = frozenset(WAVE8_FOLLOWUP_B_CONTRACTS)
WAVE8_FOLLOWUP_B_RESERVED_IDS = WAVE8_FOLLOWUP_B_CONTRACT_IDS
WAVE8_FOLLOWUP_B_POINT_QUARANTINE_ADDITIONS = frozenset(
    {_BALAPUR, _RATANPUR}
)
WAVE8_FOLLOWUP_B_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_FOLLOWUP_B_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    _BALAPUR: {
        "actions": ["withhold_point"],
        "reason": (
            "The gazetteer places the 1720 battle six to eight miles west of "
            "Balapur, so HCED's town-adjacent coordinate is not an independently "
            "verified battlefield point. Retain India and withhold geometry."
        ),
        "evidence_refs": [
            "wave8_followup_b_maharashtra_akola_history",
            "wave8_followup_b_maharashtra_balapur_places",
        ],
    },
    _RATANPUR: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed histories identify Ratanpur within the campaign near "
            "Burhanpur but do not independently establish HCED's exact point. "
            "Retain India and withhold geometry."
        ),
        "evidence_refs": [
            "wave8_followup_b_maharashtra_akola_history",
            "wave8_followup_b_maharashtra_history_ch8",
        ],
    },
}

WAVE8_FOLLOWUP_B_EXPECTED_RELEASE_EVENT_IDS: dict[str, str] = {
    candidate_id: f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
    for candidate_id in sorted(WAVE8_FOLLOWUP_B_CONTRACT_IDS)
}

_EXPECTED_SCALE_LEVELS: dict[str, int] = {
    _BALAPUR: 3,
    _KHARDA: 4,
    _RATANPUR: 2,
    _SIKASSO: 2,
}

WAVE8_FOLLOWUP_B_REUSED_SOURCE_IDS = frozenset({"telangana_asaf_jahi"})
WAVE8_FOLLOWUP_B_NEW_SOURCE_IDS = frozenset(_SOURCE_BY_ID) - (
    WAVE8_FOLLOWUP_B_REUSED_SOURCE_IDS
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_FOLLOWUP_B_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_FOLLOWUP_B_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_FOLLOWUP_B_ENTITIES,
        "existing_entity_contracts": WAVE8_FOLLOWUP_B_EXISTING_ENTITY_CONTRACTS,
        "expected_release_event_ids": WAVE8_FOLLOWUP_B_EXPECTED_RELEASE_EVENT_IDS,
        "expected_scale_levels": _EXPECTED_SCALE_LEVELS,
        "event_aliases": {
            candidate_id: sorted(aliases)
            for candidate_id, aliases in sorted(_EVENT_ALIASES.items())
        },
        "funnel": WAVE8_FOLLOWUP_B_FUNNEL_AUDIT,
        "holds": WAVE8_FOLLOWUP_B_HOLDS,
        "location_reasons": WAVE8_FOLLOWUP_B_LOCATION_QUARANTINE_REASONS,
        "new_source_ids": sorted(WAVE8_FOLLOWUP_B_NEW_SOURCE_IDS),
        "point_quarantine_additions": sorted(
            WAVE8_FOLLOWUP_B_POINT_QUARANTINE_ADDITIONS
        ),
        "raw_row_contracts": WAVE8_FOLLOWUP_B_RAW_ROW_CONTRACTS,
        "reserved_ids": sorted(WAVE8_FOLLOWUP_B_RESERVED_IDS),
        "reused_source_ids": sorted(WAVE8_FOLLOWUP_B_REUSED_SOURCE_IDS),
        "row_hashes": WAVE8_FOLLOWUP_B_ROW_HASHES,
        "sources": WAVE8_FOLLOWUP_B_SOURCES,
        "twin_match_keys": sorted(
            [year, normalized_name]
            for year, normalized_name in _DUPLICATE_MATCH_KEYS
        ),
    }


def wave8_followup_b_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_FOLLOWUP_B_FINAL_AUDIT_SIGNATURE = (
    "1e8a20c5479c7b887db23b56a948e38bf1a1097d1e6f353e47f9f7440e722061"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _entity_projection(
    entity: Mapping[str, Any], contract: Mapping[str, Any]
) -> dict[str, Any]:
    return {key: entity.get(key) for key in contract}


def _validate_release_entity_contracts(
    release_entities: Mapping[str, Mapping[str, Any]],
) -> None:
    for fixture in WAVE8_FOLLOWUP_B_ENTITIES:
        entity_id = str(fixture["id"])
        actual = release_entities.get(entity_id)
        if actual is None or dict(actual) != fixture:
            raise ValueError(f"{_LANE_NAME} exact entity drift: {entity_id}")
    for entity_id, contract in WAVE8_FOLLOWUP_B_EXISTING_ENTITY_CONTRACTS.items():
        actual = release_entities.get(entity_id)
        if actual is None or _entity_projection(actual, contract) != contract:
            raise ValueError(f"{_LANE_NAME} existing entity drift: {entity_id}")


def _validate_static() -> None:
    source_by_id = {
        str(source["id"]): source for source in WAVE8_FOLLOWUP_B_SOURCES
    }
    if len(source_by_id) != len(WAVE8_FOLLOWUP_B_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if set(source_by_id) != set(_SOURCE_BY_ID):
        raise ValueError(f"{_LANE_NAME} source inventory drift")
    if WAVE8_FOLLOWUP_B_REUSED_SOURCE_IDS != {"telangana_asaf_jahi"}:
        raise ValueError(f"{_LANE_NAME} reused source inventory drift")
    if WAVE8_FOLLOWUP_B_NEW_SOURCE_IDS != set(source_by_id) - {
        "telangana_asaf_jahi"
    }:
        raise ValueError(f"{_LANE_NAME} new source inventory drift")
    for source_id, source in source_by_id.items():
        roles = list(map(str, source.get("evidence_roles", [])))
        family = source.get("source_family_id")
        if not family or not roles or not _is_sorted_unique(roles):
            raise ValueError(f"{_LANE_NAME} source provenance drift: {source_id}")
        if not str(source.get("url", "")).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL drift: {source_id}")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_FOLLOWUP_B_ENTITIES
    }
    expected_windows = {
        _KENEDOUGOU: (1887, 1888),
        _NIZAM_FORCE: (1720, 1720),
        _ALAM_ALI_FORCE: (1720, 1720),
        _DILAWAR_ALI_FORCE: (1720, 1720),
    }
    if set(entity_by_id) != set(expected_windows):
        raise ValueError(f"{_LANE_NAME} new entity inventory drift")
    used_sources: set[str] = set()
    for entity_id, entity in entity_by_id.items():
        if (entity.get("start_year"), entity.get("end_year")) != expected_windows[
            entity_id
        ]:
            raise ValueError(f"{_LANE_NAME} identity boundary drift: {entity_id}")
        if entity.get("aliases") != [] or entity.get("predecessors") != []:
            raise ValueError(f"{_LANE_NAME} alias or predecessor drift: {entity_id}")
        refs = list(map(str, entity.get("source_ids", [])))
        if not refs or not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity source drift: {entity_id}")
        used_sources.update(refs)
    if "never be extended to or merged with Hyderabad State" not in str(
        entity_by_id[_NIZAM_FORCE]["continuity_note"]
    ):
        raise ValueError(f"{_LANE_NAME} Hyderabad boundary declaration drift")
    if "asserts neither a reign date nor the state's historical lifetime" not in str(
        entity_by_id[_KENEDOUGOU]["continuity_note"]
    ):
        raise ValueError(f"{_LANE_NAME} Kenedougou chronology guard drift")

    if WAVE8_FOLLOWUP_B_CONTRACT_IDS != WAVE8_FOLLOWUP_B_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} candidate inventory drift")
    if WAVE8_FOLLOWUP_B_HOLDS:
        raise ValueError(f"{_LANE_NAME} unexpectedly acquired holds")
    if WAVE8_FOLLOWUP_B_RESERVED_IDS != WAVE8_FOLLOWUP_B_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} reservation drift")
    if WAVE8_FOLLOWUP_B_POINT_QUARANTINE_ADDITIONS != {
        _BALAPUR,
        _RATANPUR,
    }:
        raise ValueError(f"{_LANE_NAME} point quarantine drift")
    if WAVE8_FOLLOWUP_B_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    if set(WAVE8_FOLLOWUP_B_LOCATION_QUARANTINE_REASONS) != {
        _BALAPUR,
        _RATANPUR,
    }:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    expected_sides = {
        _BALAPUR: ([_NIZAM_FORCE], [_ALAM_ALI_FORCE]),
        _KHARDA: ([_MARATHA], [_HYDERABAD]),
        _RATANPUR: ([_NIZAM_FORCE], [_DILAWAR_ALI_FORCE]),
        _SIKASSO: ([_KENEDOUGOU], [_WASSOULOU]),
    }
    expected_confidences = {
        _BALAPUR: 0.92,
        _KHARDA: 0.90,
        _RATANPUR: 0.90,
        _SIKASSO: 0.94,
    }
    new_entity_uses: set[str] = set()
    for candidate_id, contract in WAVE8_FOLLOWUP_B_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_FOLLOWUP_B_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash contract drift: {candidate_id}")
        if contract["raw_actor_contract"] != WAVE8_FOLLOWUP_B_RAW_ROW_CONTRACTS[
            candidate_id
        ]:
            raise ValueError(f"{_LANE_NAME} raw actor contract drift: {candidate_id}")
        if (
            contract.get("disposition") != "promote"
            or contract.get("result_type") != "win"
            or contract.get("winner_side") != 1
            or contract.get("source_outcome_override") is not False
            or contract.get("outcome_reversal") is not False
            or contract.get("source_date_override") is not False
            or contract.get("candidate_key_required") is not True
            or contract.get("generic_label_fallback") is not False
            or contract.get("unknown_outcome_policy") != "reject"
        ):
            raise ValueError(f"{_LANE_NAME} outcome or exact-key drift: {candidate_id}")
        if float(contract["confidence"]) != expected_confidences[candidate_id]:
            raise ValueError(f"{_LANE_NAME} confidence drift: {candidate_id}")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if (side_1, side_2) != expected_sides[candidate_id]:
            raise ValueError(f"{_LANE_NAME} exact actor drift: {candidate_id}")
        new_entity_uses.update((set(side_1) | set(side_2)) & set(entity_by_id))

        raw = WAVE8_FOLLOWUP_B_RAW_ROW_CONTRACTS[candidate_id]
        canonical = contract["canonical_event"]
        if (
            int(canonical["year_low"]) != int(raw["year_low"])
            or int(canonical["year_high"]) != int(raw["year_high"])
        ):
            raise ValueError(f"{_LANE_NAME} chronology drift: {candidate_id}")

        evidence = list(map(str, contract["evidence_refs"]))
        identities = list(map(str, contract["identity_source_ids"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        boundaries = list(map(str, contract["boundary_source_ids"]))
        for field_name, values in (
            ("evidence", evidence),
            ("identity", identities),
            ("outcome", outcomes),
            ("boundary", boundaries),
        ):
            if not _is_sorted_unique(values):
                raise ValueError(
                    f"{_LANE_NAME} {field_name} source order drift: {candidate_id}"
                )
        if not identities or not outcomes:
            raise ValueError(f"{_LANE_NAME} empty source contract: {candidate_id}")
        if set(evidence) != set(identities) | set(outcomes) | set(boundaries):
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        if not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} unknown source: {candidate_id}")
        for source_id in identities:
            if "identity_boundary_or_context_reference" not in source_by_id[
                source_id
            ]["evidence_roles"]:
                raise ValueError(
                    f"{_LANE_NAME} identity source role drift: {candidate_id}"
                )
        for source_id in outcomes:
            if "outcome" not in source_by_id[source_id]["evidence_roles"]:
                raise ValueError(
                    f"{_LANE_NAME} outcome source role drift: {candidate_id}"
                )
        for source_id in boundaries:
            if "identity_boundary_or_context_reference" not in source_by_id[
                source_id
            ]["evidence_roles"]:
                raise ValueError(
                    f"{_LANE_NAME} boundary source role drift: {candidate_id}"
                )
        for ids_key, families_key in (
            ("identity_source_ids", "identity_source_family_ids"),
            ("outcome_source_ids", "outcome_source_family_ids"),
            ("boundary_source_ids", "boundary_source_family_ids"),
        ):
            expected_families = sorted(
                {
                    str(source_by_id[source_id]["source_family_id"])
                    for source_id in contract[ids_key]
                }
            )
            if contract[families_key] != expected_families:
                raise ValueError(
                    f"{_LANE_NAME} source family drift: {candidate_id}"
                )
        if len(contract["outcome_source_family_ids"]) < 2:
            raise ValueError(
                f"{_LANE_NAME} outcome lacks two source families: {candidate_id}"
            )
        used_sources.update(evidence)

    if new_entity_uses != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} unused new entity fixture")
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    actual_signature = wave8_followup_b_audit_signature()
    if actual_signature != WAVE8_FOLLOWUP_B_FINAL_AUDIT_SIGNATURE:
        raise ValueError(
            f"{_LANE_NAME} final audit signature changed: {actual_signature}"
        )


def validate_wave8_followup_b_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    expected_records = {
        str(contract["source_record_id"]): candidate_id
        for candidate_id, contract in WAVE8_FOLLOWUP_B_RAW_ROW_CONTRACTS.items()
    }
    exact = [
        row
        for row in hced_rows
        if row.get("candidate_id") in WAVE8_FOLLOWUP_B_EXPECTED_CANDIDATE_IDS
        or row.get("source_record_id") in expected_records
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_FOLLOWUP_B_EXPECTED_CANDIDATE_IDS or len(exact) != len(
        exact_ids
    ):
        raise ValueError(f"{_LANE_NAME} exact candidate inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_FOLLOWUP_B_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        raw_contract = WAVE8_FOLLOWUP_B_RAW_ROW_CONTRACTS[candidate_id]
        actual = {key: row.get(key) for key in raw_contract}
        if actual != raw_contract:
            raise ValueError(f"{_LANE_NAME} raw row contract changed: {candidate_id}")
        if (
            row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
        ):
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if row.get("do_not_rate_automatically") is not True:
            raise ValueError(f"{_LANE_NAME} automatic-rating guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_FOLLOWUP_B_CONTRACTS,
        WAVE8_FOLLOWUP_B_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_candidate_rows": len(exact)}


def validate_wave8_followup_b_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    labels_raw = funnel.get("labels")
    rows_raw = funnel.get("row_label_data")
    if not isinstance(labels_raw, list) or not isinstance(rows_raw, list):
        raise ValueError(f"{_LANE_NAME} funnel schema changed")
    labels = [str(row.get("label")) for row in labels_raw if isinstance(row, Mapping)]
    if len(labels) != len(set(labels)):
        raise ValueError(f"{_LANE_NAME} duplicate funnel label")
    leaked_labels = sorted(WAVE8_FOLLOWUP_B_FUNNEL_LABELS & set(labels))
    leaked_candidates = sorted(
        WAVE8_FOLLOWUP_B_EXPECTED_CANDIDATE_IDS
        & {
            str(row.get("candidate_id"))
            for row in rows_raw
            if isinstance(row, Mapping)
        }
    )
    if leaked_labels or leaked_candidates:
        raise ValueError(
            f"{_LANE_NAME} promoted rows leaked into funnel: "
            f"labels={leaked_labels}, candidates={leaked_candidates}"
        )
    return {
        "leaked_labels": len(leaked_labels),
        "required_absent_labels": len(WAVE8_FOLLOWUP_B_FUNNEL_LABELS),
        "reserved_candidate_ids": len(WAVE8_FOLLOWUP_B_EXPECTED_CANDIDATE_IDS),
        "reserved_candidate_rows_present": len(leaked_candidates),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "batyear"):
        value = row.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


_EVENT_ALIASES: dict[str, set[str]] = {
    _BALAPUR: {"Balapur", "Battle of Balapur"},
    _KHARDA: {"Kharda", "Battle of Kharda"},
    _RATANPUR: {"Ratanpur", "Battle of Ratanpur", "Pandhar", "Husainpur"},
    _SIKASSO: {"Sikasso", "Siege of Sikasso"},
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(WAVE8_FOLLOWUP_B_CONTRACTS[candidate_id]["canonical_event"][
            "year_low"
        ]),
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


def validate_wave8_followup_b_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_followup_b_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_FOLLOWUP_B_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_FOLLOWUP_B_RESERVED_IDS
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


def install_wave8_followup_b_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_FOLLOWUP_B_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_followup_b_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_FOLLOWUP_B_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_FOLLOWUP_B_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_FOLLOWUP_B_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_followup_b_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_followup_b_queue_contracts(hced_rows)
    _validate_release_entity_contracts(release_entities)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_FOLLOWUP_B_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def _records_by_id(
    records: Mapping[str, Mapping[str, Any]] | Iterable[Mapping[str, Any]],
    *,
    record_type: str,
) -> dict[str, Mapping[str, Any]]:
    if isinstance(records, Mapping):
        result = {str(key): value for key, value in records.items()}
        for key, value in result.items():
            if str(value.get("id")) != key:
                raise ValueError(f"{_LANE_NAME} {record_type} mapping key drift: {key}")
        return result
    result: dict[str, Mapping[str, Any]] = {}
    for record in records:
        record_id = str(record.get("id"))
        if record_id in result:
            raise ValueError(f"{_LANE_NAME} duplicate {record_type}: {record_id}")
        result[record_id] = record
    return result


def validate_wave8_followup_b_release_inventory(
    release_entities: Mapping[str, Mapping[str, Any]]
    | Iterable[Mapping[str, Any]],
    release_sources: Mapping[str, Mapping[str, Any]]
    | Iterable[Mapping[str, Any]],
    release_events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    """Validate the materialized lane and reject all out-of-contract uses."""

    _validate_static()
    entity_by_id = _records_by_id(release_entities, record_type="entity")
    source_by_id = _records_by_id(release_sources, record_type="source")
    _validate_release_entity_contracts(entity_by_id)
    for fixture in WAVE8_FOLLOWUP_B_SOURCES:
        source_id = str(fixture["id"])
        actual = source_by_id.get(source_id)
        if actual is None or dict(actual) != fixture:
            raise ValueError(f"{_LANE_NAME} release source drift: {source_id}")

    events = list(release_events)
    lane_events = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_FOLLOWUP_B_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    if len(lane_events) != len(WAVE8_FOLLOWUP_B_CONTRACT_IDS):
        raise ValueError(f"{_LANE_NAME} release event inventory changed")
    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for event in lane_events:
        by_candidate.setdefault(str(event.get("hced_candidate_id")), []).append(event)
    if set(by_candidate) != WAVE8_FOLLOWUP_B_CONTRACT_IDS or any(
        len(matches) != 1 for matches in by_candidate.values()
    ):
        raise ValueError(f"{_LANE_NAME} release candidate inventory changed")

    expected_countries = {
        _BALAPUR: "India",
        _KHARDA: "India",
        _RATANPUR: "India",
        _SIKASSO: "Mali",
    }
    for candidate_id, contract in WAVE8_FOLLOWUP_B_CONTRACTS.items():
        event = by_candidate[candidate_id][0]
        canonical = contract["canonical_event"]
        scale_level = _EXPECTED_SCALE_LEVELS[candidate_id]
        expected_scale = (
            "skirmish"
            if scale_level == 1
            else "battle"
            if scale_level <= 3
            else "campaign"
            if scale_level == 4
            else "theater"
        )
        raw_name = str(WAVE8_FOLLOWUP_B_RAW_ROW_CONTRACTS[candidate_id]["name"])
        expected_aliases = [raw_name] if raw_name != canonical["name"] else []
        if (
            event.get("id")
            != WAVE8_FOLLOWUP_B_EXPECTED_RELEASE_EVENT_IDS[candidate_id]
            or event.get("name") != canonical["name"]
            or event.get("year") != canonical["year_low"]
            or event.get("end_year") != canonical["year_high"]
            or event.get("event_type") != "engagement"
            or event.get("war_type") != contract["war_type"]
            or event.get("scale") != expected_scale
            or event.get("stakes")
            != ("major" if scale_level >= 4 else "limited")
            or event.get("decisiveness")
            != round(min(0.90, 0.54 + 0.06 * scale_level), 2)
            or event.get("geographic_scope")
            != round(min(0.70, 0.08 + 0.09 * scale_level), 2)
            or event.get("domain") != "land"
            or event.get("date_precision") != canonical["date_precision"]
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("reviewed_granularity") != canonical["granularity"]
            or list(map(str, event.get("aliases", []))) != expected_aliases
            or event.get("confidence") != contract["confidence"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("status") != "complete"
        ):
            raise ValueError(f"{_LANE_NAME} release event drift: {candidate_id}")
        if list(map(str, event.get("source_ids", []))) != [
            "hced_dataset",
            *contract["evidence_refs"],
        ]:
            raise ValueError(f"{_LANE_NAME} release evidence drift: {candidate_id}")
        if list(map(str, event.get("outcome_source_ids", []))) != contract[
            "outcome_source_ids"
        ]:
            raise ValueError(f"{_LANE_NAME} release outcome source drift: {candidate_id}")
        if list(map(str, event.get("outcome_source_family_ids", []))) != contract[
            "outcome_source_family_ids"
        ]:
            raise ValueError(f"{_LANE_NAME} release source family drift: {candidate_id}")

        expected_participants = expected_exact_hced_win_participants(
            contract["side_1_entity_ids"],
            contract["side_2_entity_ids"],
            confidence=float(contract["confidence"]),
            scale_level=scale_level,
            lane_name=_LANE_NAME,
        )
        if list(event.get("participants", [])) != expected_participants:
            raise ValueError(f"{_LANE_NAME} release outcome drift: {candidate_id}")
        if event.get("modern_location_country") != expected_countries[candidate_id]:
            raise ValueError(f"{_LANE_NAME} release country drift: {candidate_id}")
        if candidate_id in WAVE8_FOLLOWUP_B_POINT_QUARANTINE_ADDITIONS:
            if "geometry" in event:
                raise ValueError(f"{_LANE_NAME} quarantined point leaked: {candidate_id}")
        elif hced_point_geometry_validation_error(event.get("geometry")) is not None:
            raise ValueError(f"{_LANE_NAME} unexpected point quarantine: {candidate_id}")

    new_entity_ids = {str(entity["id"]) for entity in WAVE8_FOLLOWUP_B_ENTITIES}
    outside_uses = sorted(
        str(event.get("id") or "<missing-id>")
        for event in events
        if event not in lane_events
        and new_entity_ids
        & {
            str(participant.get("entity_id"))
            for participant in event.get("participants", [])
        }
    )
    if outside_uses:
        raise ValueError(
            f"{_LANE_NAME} new identities used outside exact contracts: {outside_uses}"
        )
    return {
        "lane_entities": len(WAVE8_FOLLOWUP_B_ENTITIES),
        "lane_events": len(lane_events),
        "new_source_records": len(WAVE8_FOLLOWUP_B_NEW_SOURCE_IDS),
        "outside_entity_uses": 0,
        "point_quarantines": len(WAVE8_FOLLOWUP_B_POINT_QUARANTINE_ADDITIONS),
        "reused_source_records": len(WAVE8_FOLLOWUP_B_REUSED_SOURCE_IDS),
        "source_contracts": len(WAVE8_FOLLOWUP_B_SOURCES),
    }


def validate_wave8_followup_b_final_audit(
    release_entities: Mapping[str, Mapping[str, Any]]
    | Iterable[Mapping[str, Any]],
    release_sources: Mapping[str, Mapping[str, Any]]
    | Iterable[Mapping[str, Any]],
    release_events: Iterable[Mapping[str, Any]],
    lane_metadata: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate the pinned audit against the complete materialized release."""

    _validate_static()
    expected_metadata = wave8_followup_b_metadata()
    if dict(lane_metadata) != expected_metadata:
        raise ValueError(f"{_LANE_NAME} final release metadata drift")
    result: dict[str, Any] = {
        "candidate_ids": sorted(WAVE8_FOLLOWUP_B_CONTRACT_IDS),
        "final_audit_signature": WAVE8_FOLLOWUP_B_FINAL_AUDIT_SIGNATURE,
        "measured_audit_signature": wave8_followup_b_audit_signature(),
        "row_hashes": dict(WAVE8_FOLLOWUP_B_ROW_HASHES),
    }
    result["release_inventory"] = validate_wave8_followup_b_release_inventory(
        release_entities,
        release_sources,
        release_events,
    )
    return result


def wave8_followup_b_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_FOLLOWUP_B_CONTRACTS.values()
            ).items()
        )
    )


def wave8_followup_b_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": 0,
        "new_entities": len(WAVE8_FOLLOWUP_B_ENTITIES),
        "new_sources": len(WAVE8_FOLLOWUP_B_NEW_SOURCE_IDS),
        "newly_rated_events": len(WAVE8_FOLLOWUP_B_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_FOLLOWUP_B_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_FOLLOWUP_B_CONTRACTS),
        "reused_sources": len(WAVE8_FOLLOWUP_B_REUSED_SOURCE_IDS),
        "reviewed_hced_rows": len(WAVE8_FOLLOWUP_B_RESERVED_IDS),
        "source_contracts": len(WAVE8_FOLLOWUP_B_SOURCES),
        "terminal_exclusions": 0,
    }


def wave8_followup_b_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_followup_b_counts(),
        "cohorts": wave8_followup_b_cohort_counts(),
        "final_audit_signature": WAVE8_FOLLOWUP_B_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_FOLLOWUP_B_CONTRACT_IDS),
        "reserved_candidate_ids": sorted(WAVE8_FOLLOWUP_B_RESERVED_IDS),
        "point_quarantine_candidate_ids": sorted(
            WAVE8_FOLLOWUP_B_POINT_QUARANTINE_ADDITIONS
        ),
    }


_validate_static()
