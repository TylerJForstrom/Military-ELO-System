"""Fail-closed exact HCED lane for Banu Bu Ali and Berad Tribes rows.

The two raw labels are routing keys, not reusable polity identities.  This
lane promotes four source-audited events with event-bounded, alias-free
formations; only the already-curated Mughal Empire identity is reused.  The
similarly spelled ``Bani Bu Ali`` Ras al-Khaimah row remains a separately
fingerprinted hold and is neither reserved nor rated here.

Wikidata discovery records never originate outcomes.  The malformed 1704
Wagingera record is superseded by the source-audited 1705 siege, while Battle
of Bedara is a lexical false positive.  Both have unknown outcomes, which are
never converted to draws.
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
    "WAVE8_BANU_BU_ALI_BERAD_CONTRACT_IDS",
    "WAVE8_BANU_BU_ALI_BERAD_CONTRACTS",
    "WAVE8_BANU_BU_ALI_BERAD_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_DISPOSITIONS",
    "WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_EXPECTED",
    "WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_ROW_HASHES",
    "WAVE8_BANU_BU_ALI_BERAD_ENTITIES",
    "WAVE8_BANU_BU_ALI_BERAD_FINAL_AUDIT_SIGNATURE",
    "WAVE8_BANU_BU_ALI_BERAD_FUNNEL_AUDIT",
    "WAVE8_BANU_BU_ALI_BERAD_HOLDS",
    "WAVE8_BANU_BU_ALI_BERAD_LOCATION_QUARANTINE_REASONS",
    "WAVE8_BANU_BU_ALI_BERAD_OUTSIDE_LANE_HOLDS",
    "WAVE8_BANU_BU_ALI_BERAD_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_BANU_BU_ALI_BERAD_RESERVED_IDS",
    "WAVE8_BANU_BU_ALI_BERAD_ROW_HASHES",
    "WAVE8_BANU_BU_ALI_BERAD_SOURCES",
    "install_wave8_banu_bu_ali_berad_entities",
    "install_wave8_banu_bu_ali_berad_sources",
    "promote_wave8_banu_bu_ali_berad_contracts",
    "validate_wave8_banu_bu_ali_berad_current_artifact_state",
    "validate_wave8_banu_bu_ali_berad_discovery_dispositions",
    "validate_wave8_banu_bu_ali_berad_emissions",
    "validate_wave8_banu_bu_ali_berad_funnel",
    "validate_wave8_banu_bu_ali_berad_queue_contracts",
    "wave8_banu_bu_ali_berad_audit_signature",
    "wave8_banu_bu_ali_berad_cohort_counts",
    "wave8_banu_bu_ali_berad_counts",
    "wave8_banu_bu_ali_berad_location_quarantine_additions",
    "wave8_banu_bu_ali_berad_metadata",
)


_LANE_NAME = "Wave 8 exact Banu Bu Ali and Berad Tribes audit"
_MODULE_OWNER = "military_elo.promotion.wave8_banu_bu_ali_berad"
_EVENT_ID_PREFIX = "hced_wave8_banu_berad_"
_OWNED_LABELS = frozenset({"banu bu ali", "berad tribes"})
_SEPARATE_LABEL = "bani bu ali"

_MUHAMMAD_JALAN_1820 = "muhammad_bin_ali_jalan_defenders_1820"
_THOMPSON_COLUMN_1820 = "thompson_eic_jalan_column_1820"
_SAID_LEVY_1820 = "sayyid_said_jalan_levy_1820"
_SMITH_EXPEDITION_1821 = "lionel_smith_bombay_expedition_bani_bu_ali_1821"
_MUHAMMAD_DEFENDERS_1821 = "muhammad_bin_ali_bani_bu_ali_defenders_1821"
_PAM_NAYAK_1680 = "pam_nayak_sagar_defenders_1680"
_PIDIA_NAYAK_1705 = "pidia_nayak_wagingera_garrison_1705"
_DHANA_JADAV_1705 = "dhana_jadav_hindu_rao_wagingera_relief_force_1705"
_MUGHAL_EMPIRE = "mughal_empire"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
    crosscheck: bool = False,
) -> dict[str, Any]:
    roles = {"identity_boundary_or_context_reference"}
    if outcome:
        roles.add("outcome")
    if crosscheck:
        roles.add("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-21",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_BANU_BU_ALI_BERAD_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_banu_berad_qdl_india_office_1820",
        "India Office proceedings on the first Bani Bu Ali expedition",
        "https://www.qdl.qa/archive/81055/vdc_100000001741.0x000173",
        "Qatar Digital Library / British Library India Office Records",
        "digitized_primary_source",
        "british_india_office_bani_bu_ali_dispatches",
        outcome=True,
    ),
    _source(
        "wave8_banu_berad_qdl_persian_gulf_admin_1820",
        "Persian Gulf administration report on the Bani Bu Ali expedition",
        "https://www.qdl.qa/en/archive/81055/vdc_100023549644.0x00002f",
        "Qatar Digital Library / British Library",
        "official_administration_report",
        "persian_gulf_residency_administration_reports",
        outcome=True,
    ),
    _source(
        "wave8_banu_berad_qdl_lorimer_bani_bu_ali",
        "Gazetteer of the Persian Gulf: Bani Bu Ali and Ja'alan",
        "https://www.qdl.qa/en/archive/81055/vdc_100023575942.0x000091",
        "Government of India / Qatar Digital Library",
        "official_historical_gazetteer",
        "lorimer_goi_persian_gulf_gazetteer",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_banu_berad_london_gazette_1821",
        "Official dispatch on the capture of Bani Bu Ali",
        "https://www.thegazette.co.uk/London/issue/17762/page/2198/data.pdf",
        "The London Gazette",
        "contemporary_official_dispatch",
        "east_india_company_official_dispatches",
        outcome=True,
    ),
    _source(
        "wave8_banu_berad_qdl_said_nonparticipation_1821",
        "Administrative account of Sa'id bin Sultan and the 1821 expedition",
        "https://www.qdl.qa/en/archive/81055/vdc_100023373225.0x000022",
        "Qatar Digital Library / British Library India Office Records",
        "digitized_primary_source",
        "british_india_office_bani_bu_ali_dispatches",
    ),
    _source(
        "wave8_banu_berad_lees_forgotten_battle",
        "A Forgotten Battle",
        "https://www.jstor.org/stable/i40176598",
        "Journal of the Society for Army Historical Research / JSTOR",
        "scholarly_military_history_article",
        "lees_jsahr_military_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_banu_berad_sarkar_aurangzib_iv",
        "History of Aurangzib, Volume IV",
        (
            "https://ir.nbu.ac.in/server/api/core/bitstreams/"
            "835a5186-cf8c-4761-a2c4-8aa41d445a4c/content"
        ),
        "University of North Bengal Institutional Repository",
        "scholarly_history_monograph",
        "sarkar_history_aurangzib",
        outcome=True,
    ),
    _source(
        "wave8_banu_berad_singh_sagar_2007",
        "The Last Great Battle of the Mughal Empire",
        (
            "https://epe.lac-bac.gc.ca/100/201/300/asian_social_science/"
            "2007/ASS200705.pdf?nodisclaimer=1"
        ),
        "Asian Social Science / Library and Archives Canada mirror",
        "scholarly_history_article",
        "singh_asian_social_science",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_banu_berad_guha_environment_ethnicity",
        "Environment and Ethnicity in India, 1200-1991",
        (
            "https://www.cambridge.org/core/books/environment-and-ethnicity-"
            "in-india-12001991/2B29D4A6B96257B427EDD9C085876EA1"
        ),
        "Cambridge University Press",
        "academic_monograph",
        "guha_environment_ethnicity",
    ),
    _source(
        "wave8_banu_berad_maasir_i_alamgiri",
        "Ma'asir-i-'Alamgiri",
        "https://library.bjp.org/jspui/handle/123456789/694",
        "Bharatiya Jana Parishad Digital Library",
        "translated_primary_chronicle",
        "maasir_i_alamgiri_primary_chronicle",
        outcome=True,
    ),
    _source(
        "wave8_banu_berad_sarkar_aurangzib_v",
        "History of Aurangzib, Volume V",
        (
            "https://library.bjp.org/jspui/bitstream/123456789/680/1/"
            "History%20of%20Aurangzib%20Vol5.pdf"
        ),
        "Bharatiya Jana Parishad Digital Library",
        "scholarly_history_monograph",
        "sarkar_history_aurangzib",
        outcome=True,
    ),
    _source(
        "wave8_banu_berad_sarkar_studies_aurangzib",
        "Studies in Aurangzib's Reign",
        "https://ignca.gov.in/Asi_data/35129.pdf",
        "Indira Gandhi National Centre for the Arts",
        "scholarly_history_monograph",
        "sarkar_history_aurangzib",
        outcome=True,
        crosscheck=True,
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_BANU_BU_ALI_BERAD_SOURCES
}

_SUR_SOURCE_IDS = (
    "wave8_banu_berad_qdl_india_office_1820",
    "wave8_banu_berad_qdl_lorimer_bani_bu_ali",
    "wave8_banu_berad_qdl_persian_gulf_admin_1820",
)
_BANI_1821_SOURCE_IDS = (
    "wave8_banu_berad_lees_forgotten_battle",
    "wave8_banu_berad_london_gazette_1821",
    "wave8_banu_berad_qdl_lorimer_bani_bu_ali",
    "wave8_banu_berad_qdl_said_nonparticipation_1821",
)
_SAGAR_SOURCE_IDS = (
    "wave8_banu_berad_guha_environment_ethnicity",
    "wave8_banu_berad_sarkar_aurangzib_iv",
    "wave8_banu_berad_singh_sagar_2007",
)
_WAGINGERA_SOURCE_IDS = (
    "wave8_banu_berad_guha_environment_ethnicity",
    "wave8_banu_berad_maasir_i_alamgiri",
    "wave8_banu_berad_sarkar_aurangzib_v",
    "wave8_banu_berad_sarkar_studies_aurangzib",
    "wave8_banu_berad_singh_sagar_2007",
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    source_ids: Iterable[str],
    boundary: str,
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
            boundary
            + " It receives no broad tribal, dynastic, imperial, colonial, "
            "predecessor, or successor alias and inherits no Elo."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_BANU_BU_ALI_BERAD_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _MUHAMMAD_JALAN_1820,
        "Muhammad bin Ali's Ja'alan defenders near Bilad Bani Bu Ali (1820)",
        "event_bounded_defending_force",
        1820,
        "Ja'alan, Oman",
        _SUR_SOURCE_IDS,
        "Bounded to the force that defeated the first expedition on 9 November 1820.",
    ),
    _entity(
        _THOMPSON_COLUMN_1820,
        "Captain Thompson's East India Company Ja'alan column (1820)",
        "event_bounded_expeditionary_column",
        1820,
        "Ja'alan, Oman",
        _SUR_SOURCE_IDS,
        "Bounded to the Company-led column defeated near Bilad Bani Bu Ali.",
    ),
    _entity(
        _SAID_LEVY_1820,
        "Sayyid Sa'id's Ja'alan levy in the first Bani Bu Ali expedition (1820)",
        "event_bounded_allied_levy",
        1820,
        "Ja'alan, Oman",
        _SUR_SOURCE_IDS,
        "Bounded to the Muscat levy that fought with Thompson's column in 1820.",
    ),
    _entity(
        _SMITH_EXPEDITION_1821,
        "Lionel Smith's Bombay expedition at Bani Bu Ali (1821)",
        "event_bounded_expeditionary_force",
        1821,
        "Ja'alan, Oman",
        _BANI_1821_SOURCE_IDS,
        "Bounded to Smith's mixed Bombay, Company, and Crown expedition on 2 March 1821.",
    ),
    _entity(
        _MUHAMMAD_DEFENDERS_1821,
        "Muhammad bin Ali's Bani Bu Ali defenders (1821)",
        "event_bounded_defending_force",
        1821,
        "Ja'alan, Oman",
        _BANI_1821_SOURCE_IDS,
        "Bounded to the fortified defending force defeated on 2 March 1821.",
    ),
    _entity(
        _PAM_NAYAK_1680,
        "Pam Nayak's Sagar defenders at Shahpur (1680)",
        "event_bounded_defending_force",
        1680,
        "Sagar-Shahpur, Deccan",
        _SAGAR_SOURCE_IDS,
        "Bounded to Pam Nayak's force in the 20-21 February 1680 battle.",
    ),
    _entity(
        _PIDIA_NAYAK_1705,
        "Pidia Nayak's Wagingera garrison (1705)",
        "event_bounded_fortress_garrison",
        1705,
        "Wagingera, Deccan",
        _WAGINGERA_SOURCE_IDS,
        "Bounded to the garrison during the 8 February-27 April 1705 siege.",
    ),
    _entity(
        _DHANA_JADAV_1705,
        "Dhana Jadav and Hindu Rao's Wagingera relief force (1705)",
        "event_bounded_relief_force",
        1705,
        "Wagingera, Deccan",
        _WAGINGERA_SOURCE_IDS,
        "Bounded to the named auxiliary relief force in the 1705 siege.",
    ),
)

_ENTITY_BY_ID = {
    str(entity["id"]): entity for entity in WAVE8_BANU_BU_ALI_BERAD_ENTITIES
}


WAVE8_BANU_BU_ALI_BERAD_ROW_HASHES: dict[str, str] = {
    "hced-Bani Bu Ali1821-1": (
        "71b69d563942cd10c8b296420c06ce6931ae92e8f016df4c2e48512a3c930e49"
    ),
    "hced-Sagar1680-1": (
        "6b6ede291b02b5cb709f6e2073587ca29ad41c3afd728c333740dea3f37ce8e2"
    ),
    "hced-Sur1820-1": (
        "0ecbbf80b4876af3eaf31daf7dac31991bc006c0e3a9f8e85e432291a9100d4c"
    ),
    "hced-Wagingera1705-1": (
        "13e8b37410eb1167bc36cc194b95ae4fb6e877e6aa4e6b42b5d62daa09f1af20"
    ),
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


_EVENT_EVIDENCE_REFS: dict[str, tuple[str, ...]] = {
    "hced-Sur1820-1": _SUR_SOURCE_IDS,
    "hced-Bani Bu Ali1821-1": _BANI_1821_SOURCE_IDS,
    "hced-Sagar1680-1": _SAGAR_SOURCE_IDS,
    "hced-Wagingera1705-1": _WAGINGERA_SOURCE_IDS,
}
_EVENT_OUTCOME_SOURCE_IDS: dict[str, tuple[str, ...]] = {
    "hced-Sur1820-1": (
        "wave8_banu_berad_qdl_india_office_1820",
        "wave8_banu_berad_qdl_persian_gulf_admin_1820",
    ),
    "hced-Bani Bu Ali1821-1": (
        "wave8_banu_berad_lees_forgotten_battle",
        "wave8_banu_berad_london_gazette_1821",
        "wave8_banu_berad_qdl_lorimer_bani_bu_ali",
    ),
    "hced-Sagar1680-1": (
        "wave8_banu_berad_sarkar_aurangzib_iv",
        "wave8_banu_berad_singh_sagar_2007",
    ),
    "hced-Wagingera1705-1": (
        "wave8_banu_berad_maasir_i_alamgiri",
        "wave8_banu_berad_sarkar_aurangzib_v",
        "wave8_banu_berad_sarkar_studies_aurangzib",
    ),
}


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    reviewed_outcome: str,
    audit_note: str,
    *,
    cohort: str,
    confidence: float,
    expected_scale_level: int,
    war_type: str,
) -> dict[str, Any]:
    evidence_refs = sorted(_EVENT_EVIDENCE_REFS[candidate_id])
    outcome_source_ids = sorted(_EVENT_OUTCOME_SOURCE_IDS[candidate_id])
    return {
        "raw_row_sha256": WAVE8_BANU_BU_ALI_BERAD_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": evidence_refs,
        "outcome_source_ids": outcome_source_ids,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcome_source_ids
            }
        ),
        "date_source_ids": outcome_source_ids,
        "source_date_refinement": True,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_alias_free_event_bounded_forces",
        "expected_scale_level": expected_scale_level,
        "reviewed_outcome": reviewed_outcome,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_BANU_BU_ALI_BERAD_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Sur1820-1": _contract(
        "hced-Sur1820-1",
        _canonical(
            "Battle near Bilad Bani Bu Ali",
            1820,
            "9 November 1820",
            "1820-11-09",
            "1820-11-09",
            "single_field_battle_not_sur_landing_or_full_expedition",
        ),
        [_MUHAMMAD_JALAN_1820],
        [_THOMPSON_COLUMN_1820, _SAID_LEVY_1820],
        "Decisive tactical victory for Muhammad bin Ali's Ja'alan defenders",
        (
            "The audited sources place the field battle inland near Bilad Bani "
            "Bu Ali on 9 November. Sur was the expedition's maritime staging "
            "point, not the battlefield, and the full campaign is not rated."
        ),
        cohort="bani_bu_ali_expeditions_1820_1821",
        confidence=0.95,
        expected_scale_level=1,
        war_type="colonial_anti_colonial",
    ),
    "hced-Bani Bu Ali1821-1": _contract(
        "hced-Bani Bu Ali1821-1",
        _canonical(
            "Battle and capture of Bani Bu Ali",
            1821,
            "2 March 1821",
            "1821-03-02",
            "1821-03-02",
            "same_day_battle_and_capture_not_full_campaign",
        ),
        [_SMITH_EXPEDITION_1821],
        [_MUHAMMAD_DEFENDERS_1821],
        "Decisive tactical victory for Lionel Smith's mixed Bombay expedition",
        (
            "The contemporary dispatch and Lorimer identify the 2 March battle "
            "and capture. Sa'id bin Sultan accompanied the operation but did "
            "not participate, so no generic Muscat or Oman entity is rated."
        ),
        cohort="bani_bu_ali_expeditions_1820_1821",
        confidence=0.97,
        expected_scale_level=1,
        war_type="colonial_anti_colonial",
    ),
    "hced-Sagar1680-1": _contract(
        "hced-Sagar1680-1",
        _canonical(
            "Battle of Sagar (Shahpur)",
            1680,
            "20-21 February 1680",
            "1680-02-20",
            "1680-02-21",
            "two_day_assault_and_field_rout_below_sagar",
        ),
        [_PAM_NAYAK_1680],
        [_MUGHAL_EMPIRE],
        "Decisive tactical victory for Pam Nayak's Sagar defenders",
        (
            "The contract is limited to the Shahpur-Sagar action and Dilir "
            "Khan's field-army rout. Nominal Bijapur overlordship does not "
            "establish a Bijapur combatant and creates no co-participant."
        ),
        cohort="mughal_nayak_wars_1680_1705",
        confidence=0.93,
        expected_scale_level=2,
        war_type="interstate_limited",
    ),
    "hced-Wagingera1705-1": _contract(
        "hced-Wagingera1705-1",
        _canonical(
            "Siege and capture of Wagingera",
            1705,
            "8 February-27 April 1705",
            "1705-02-08",
            "1705-04-27",
            "full_three_month_siege_not_separate_final_assault",
        ),
        [_MUGHAL_EMPIRE],
        [_PIDIA_NAYAK_1705, _DHANA_JADAV_1705],
        "Limited Mughal tactical victory through capture of the siege objective",
        (
            "The full siege rates once. Mughal forces occupied the fort and "
            "pettah after evacuation, but the contract infers neither surrender "
            "nor annihilation and does not create a second final-assault event."
        ),
        cohort="mughal_nayak_wars_1680_1705",
        confidence=0.96,
        expected_scale_level=2,
        war_type="interstate_limited",
    ),
}

WAVE8_BANU_BU_ALI_BERAD_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_BANU_BU_ALI_BERAD_CONTRACT_IDS = frozenset(
    WAVE8_BANU_BU_ALI_BERAD_CONTRACTS
)
WAVE8_BANU_BU_ALI_BERAD_RESERVED_IDS = (
    WAVE8_BANU_BU_ALI_BERAD_CONTRACT_IDS
)

WAVE8_BANU_BU_ALI_BERAD_OUTSIDE_LANE_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Ras al-Khaimah1809-1": {
        "raw_row_sha256": (
            "8c8ff4497f3b7e6a2a0f88a105576b65746f322628fa112dad7f5fa4747361eb"
        ),
        "disposition": "hold_separate_lane",
        "label": "bani bu ali",
        "reason": (
            "The differently spelled label is an attribution collision in the "
            "1809 Ras al-Khaimah/Qawasim operation. It cannot inherit the exact "
            "1820-1821 Banu Bu Ali formations or outcome contract."
        ),
        "outcome_disposition": "staged_pending_separate_actor_audit",
        "unknown_is_never_draw": True,
    }
}


WAVE8_BANU_BU_ALI_BERAD_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_BANU_BU_ALI_BERAD_CONTRACT_IDS
)
WAVE8_BANU_BU_ALI_BERAD_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = (
    frozenset()
)
WAVE8_BANU_BU_ALI_BERAD_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    "hced-Sur1820-1": {
        "actions": ["withhold_point"],
        "raw_country": "Oman",
        "raw_point": [59.5066376, 22.5652759],
        "reason": (
            "Sur was the departure and staging port, roughly 60 kilometres "
            "from the inland Bilad Bani Bu Ali battle area."
        ),
        "evidence_refs": sorted(_SUR_SOURCE_IDS),
    },
    "hced-Bani Bu Ali1821-1": {
        "actions": ["withhold_point"],
        "raw_country": "Oman",
        "raw_point": [59.3063443, 22.0093158],
        "reason": (
            "The point is near the modern locality but does not independently "
            "establish the fortified position or battlefield."
        ),
        "evidence_refs": sorted(_BANI_1821_SOURCE_IDS),
    },
    "hced-Sagar1680-1": {
        "actions": ["withhold_point"],
        "raw_country": "India",
        "raw_point": [76.8005838, 16.6248219],
        "reason": (
            "The action spans Shahpur, Gogi, fort approaches, and the field "
            "rout; the source point is only a locality centroid."
        ),
        "evidence_refs": sorted(_SAGAR_SOURCE_IDS),
    },
    "hced-Wagingera1705-1": {
        "actions": ["withhold_point"],
        "raw_country": "India",
        "raw_point": [76.6932438, 16.5119876],
        "reason": (
            "The siege footprint includes fort, pettah, and surrounding "
            "hillocks; neither staged point establishes an exact geometry."
        ),
        "evidence_refs": sorted(_WAGINGERA_SOURCE_IDS),
    },
}


WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q16931469": (
        "2e30bd1f0eaeb64120e305b3966c379734d63e0996166aaa157903b455442ac9"
    ),
    "Q4870440": (
        "ca46b0d1ad3d907f318e7ddbee1ff6d90177029525920e47dc02ac6f1b2e94ea"
    ),
}
WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_EXPECTED: dict[str, dict[str, Any]] = {
    "Q16931469": {
        "name": "Siege of Wagingera",
        "kind": "siege",
        "date": "1704-03-27T00:00:00Z",
        "end_date": "1704-03-28T00:00:00Z",
        "winners": [],
        "disposition": "duplicate_superseded_discovery",
        "canonical_owner": "hced-Wagingera1705-1",
        "date_disposition": "malformed_1704_subaction_date_not_imported",
        "outcome_disposition": "unknown_never_draw",
    },
    "Q4870440": {
        "name": "Battle of Bedara",
        "kind": "engagement",
        "date": "1759-01-01T00:00:00Z",
        "end_date": None,
        "winners": [],
        "disposition": "lexical_false_positive",
        "canonical_owner": None,
        "date_disposition": "unrelated_bengal_event_not_imported",
        "outcome_disposition": "unknown_never_draw",
    },
}
WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "source_dataset": "wikidata-battles",
        "disposition": expected["disposition"],
        "canonical_owner": expected["canonical_owner"],
        "date_disposition": expected["date_disposition"],
        "outcome_disposition": expected["outcome_disposition"],
        "automatic_rating": False,
    }
    for candidate_id, expected in sorted(
        WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_EXPECTED.items()
    )
}


WAVE8_BANU_BU_ALI_BERAD_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "banu bu ali": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "b4f6c360c9256053622f5f67049e9681e14c2b805a2fa89ac302130afc59199a"
        ),
        "events_touched": 2,
        "sole_blocker_events": 2,
        "unresolved_side_attempts": 2,
        "rated_counterpart_entities": 1,
        "failure_cases": {"zero_time_valid_candidates": 2},
    },
    "berad tribes": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "469157c3cead8dcbedd67d5b470815be5272592fe8f0ad995fa6c398034d808c"
        ),
        "events_touched": 2,
        "sole_blocker_events": 2,
        "unresolved_side_attempts": 2,
        "rated_counterpart_entities": 1,
        "failure_cases": {"zero_time_valid_candidates": 2},
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_BANU_BU_ALI_BERAD_CONTRACTS,
        "country_quarantine": sorted(
            WAVE8_BANU_BU_ALI_BERAD_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_dispositions": WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_DISPOSITIONS,
        "discovery_expected": WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_EXPECTED,
        "discovery_row_hashes": WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_ROW_HASHES,
        "entities": WAVE8_BANU_BU_ALI_BERAD_ENTITIES,
        "funnel": WAVE8_BANU_BU_ALI_BERAD_FUNNEL_AUDIT,
        "holds": WAVE8_BANU_BU_ALI_BERAD_HOLDS,
        "location_reasons": WAVE8_BANU_BU_ALI_BERAD_LOCATION_QUARANTINE_REASONS,
        "outside_lane_holds": WAVE8_BANU_BU_ALI_BERAD_OUTSIDE_LANE_HOLDS,
        "point_quarantine": sorted(
            WAVE8_BANU_BU_ALI_BERAD_POINT_QUARANTINE_ADDITIONS
        ),
        "row_hashes": WAVE8_BANU_BU_ALI_BERAD_ROW_HASHES,
        "sources": WAVE8_BANU_BU_ALI_BERAD_SOURCES,
    }


def wave8_banu_bu_ali_berad_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_BANU_BU_ALI_BERAD_FINAL_AUDIT_SIGNATURE = (
    "e56bf90fd868b654a8345e5a546ac799dfde773d216e1089022fde5de75c6361"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = set(_ENTITY_BY_ID)
    contract_ids = set(WAVE8_BANU_BU_ALI_BERAD_CONTRACTS)
    if len(source_ids) != len(WAVE8_BANU_BU_ALI_BERAD_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if len(entity_ids) != len(WAVE8_BANU_BU_ALI_BERAD_ENTITIES):
        raise ValueError(f"{_LANE_NAME} duplicate entity id")
    if (
        len(contract_ids) != 4
        or WAVE8_BANU_BU_ALI_BERAD_HOLDS
        or WAVE8_BANU_BU_ALI_BERAD_RESERVED_IDS != contract_ids
        or contract_ids != set(WAVE8_BANU_BU_ALI_BERAD_ROW_HASHES)
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if (
        len(entity_ids) != 8
        or _MUGHAL_EMPIRE in entity_ids
        or len(WAVE8_BANU_BU_ALI_BERAD_SOURCES) != 12
    ):
        raise ValueError(f"{_LANE_NAME} fixture cardinality drift")
    if (
        WAVE8_BANU_BU_ALI_BERAD_POINT_QUARANTINE_ADDITIONS != contract_ids
        or WAVE8_BANU_BU_ALI_BERAD_COUNTRY_QUARANTINE_ADDITIONS
        or set(WAVE8_BANU_BU_ALI_BERAD_LOCATION_QUARANTINE_REASONS)
        != contract_ids
    ):
        raise ValueError(f"{_LANE_NAME} location policy drift")

    for source in WAVE8_BANU_BU_ALI_BERAD_SOURCES:
        if (
            not str(source["url"]).startswith("https://")
            or not _is_sorted_unique(source["evidence_roles"])
        ):
            raise ValueError(f"{_LANE_NAME} source fixture drift: {source['id']}")
    for entity_id, entity in _ENTITY_BY_ID.items():
        if (
            entity["start_year"] != entity["end_year"]
            or entity["aliases"]
            or entity["predecessors"]
            or not _is_sorted_unique(entity["source_ids"])
            or not set(entity["source_ids"]) <= source_ids
            or "inherits no Elo" not in entity["continuity_note"]
        ):
            raise ValueError(f"{_LANE_NAME} entity boundary drift: {entity_id}")

    expected = {
        "hced-Sur1820-1": (
            "Battle near Bilad Bani Bu Ali",
            "1820-11-09",
            "1820-11-09",
            [_MUHAMMAD_JALAN_1820],
            [_THOMPSON_COLUMN_1820, _SAID_LEVY_1820],
            1,
        ),
        "hced-Bani Bu Ali1821-1": (
            "Battle and capture of Bani Bu Ali",
            "1821-03-02",
            "1821-03-02",
            [_SMITH_EXPEDITION_1821],
            [_MUHAMMAD_DEFENDERS_1821],
            1,
        ),
        "hced-Sagar1680-1": (
            "Battle of Sagar (Shahpur)",
            "1680-02-20",
            "1680-02-21",
            [_PAM_NAYAK_1680],
            [_MUGHAL_EMPIRE],
            2,
        ),
        "hced-Wagingera1705-1": (
            "Siege and capture of Wagingera",
            "1705-02-08",
            "1705-04-27",
            [_MUGHAL_EMPIRE],
            [_PIDIA_NAYAK_1705, _DHANA_JADAV_1705],
            2,
        ),
    }
    consumed_sources: set[str] = set()
    reused_entities: set[str] = set()
    for candidate_id, contract in WAVE8_BANU_BU_ALI_BERAD_CONTRACTS.items():
        name, start_date, end_date, side_1, side_2, scale_level = expected[
            candidate_id
        ]
        canonical = contract["canonical_event"]
        participant_ids = set(side_1) | set(side_2)
        reused_entities.update(participant_ids - entity_ids)
        outcome_ids = list(map(str, contract["outcome_source_ids"]))
        evidence_refs = list(map(str, contract["evidence_refs"]))
        expected_families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcome_ids
            }
        )
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or contract["side_1_entity_ids"] != side_1
            or contract["side_2_entity_ids"] != side_2
            or contract["expected_scale_level"] != scale_level
            or canonical["name"] != name
            or canonical["start_date"] != start_date
            or canonical["end_date"] != end_date
            or canonical["canonical_key"]
            != f"{_slug(name)}:{canonical['year_low']}:{canonical['year_high']}"
            or not _is_sorted_unique(evidence_refs)
            or not _is_sorted_unique(outcome_ids)
            or not set(outcome_ids) <= set(evidence_refs)
            or contract["outcome_source_family_ids"] != expected_families
            or len(expected_families) < 2
        ):
            raise ValueError(f"{_LANE_NAME} exact contract drift: {candidate_id}")
        consumed_sources.update(evidence_refs)
    if reused_entities != {_MUGHAL_EMPIRE}:
        raise ValueError(f"{_LANE_NAME} reused identity boundary drift")
    if consumed_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if set(WAVE8_BANU_BU_ALI_BERAD_OUTSIDE_LANE_HOLDS) != {
        "hced-Ras al-Khaimah1809-1"
    }:
        raise ValueError(f"{_LANE_NAME} separate-lane hold drift")
    if set(WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_ROW_HASHES) != {
        "Q16931469",
        "Q4870440",
    } or set(WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_DISPOSITIONS) != set(
        WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} discovery inventory drift")
    if any(
        item["outcome_disposition"] != "unknown_never_draw"
        or item["automatic_rating"] is not False
        for item in WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_DISPOSITIONS.values()
    ):
        raise ValueError(f"{_LANE_NAME} unknown-is-never-draw guard drift")
    if WAVE8_BANU_BU_ALI_BERAD_FINAL_AUDIT_SIGNATURE != "TO_BE_SEALED" and (
        wave8_banu_bu_ali_berad_audit_signature()
        != WAVE8_BANU_BU_ALI_BERAD_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_banu_bu_ali_berad_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    owned = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) in _OWNED_LABELS
        or normalize_label(row.get("side_2_raw")) in _OWNED_LABELS
    ]
    by_id = {str(row.get("candidate_id")): row for row in owned}
    if set(by_id) != WAVE8_BANU_BU_ALI_BERAD_RESERVED_IDS or len(owned) != len(
        by_id
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")

    expected = {
        "hced-Sur1820-1": (1820, "Banu Bu Ali", "United Kingdom, Muscat"),
        "hced-Bani Bu Ali1821-1": (1821, "United Kingdom", "Banu Bu Ali"),
        "hced-Sagar1680-1": (1680, "Berad Tribes", "Mughal Empire"),
        "hced-Wagingera1705-1": (1705, "Mughal Empire", "Berad Tribes"),
    }
    for candidate_id, (year, winner, loser) in expected.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != WAVE8_BANU_BU_ALI_BERAD_ROW_HASHES[
            candidate_id
        ]:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
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

    separate_rows = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _SEPARATE_LABEL
        or normalize_label(row.get("side_2_raw")) == _SEPARATE_LABEL
    ]
    if len(separate_rows) != 1 or separate_rows[0].get("candidate_id") not in (
        WAVE8_BANU_BU_ALI_BERAD_OUTSIDE_LANE_HOLDS
    ):
        raise ValueError(f"{_LANE_NAME} separate Bani Bu Ali inventory changed")
    separate = separate_rows[0]
    separate_id = str(separate["candidate_id"])
    if (
        canonical_hced_row_sha256(separate)
        != WAVE8_BANU_BU_ALI_BERAD_OUTSIDE_LANE_HOLDS[separate_id][
            "raw_row_sha256"
        ]
        or separate.get("name") != "Ras al-Khaimah"
        or separate.get("year_best") != 1809
        or separate.get("side_2_raw") != "Bani Bu Ali"
        or separate.get("do_not_rate_automatically") is not True
    ):
        raise ValueError(f"{_LANE_NAME} separate-lane hold fingerprint changed")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_BANU_BU_ALI_BERAD_CONTRACTS,
        WAVE8_BANU_BU_ALI_BERAD_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "exact_label_rows": len(owned),
        "separate_lane_holds": len(separate_rows),
    }


def validate_wave8_banu_bu_ali_berad_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, dict[str, int]]:
    _validate_static()
    by_label = {
        str(row.get("label")): row
        for row in funnel.get("labels", [])
        if str(row.get("label")) in _OWNED_LABELS
    }
    if set(by_label) != _OWNED_LABELS:
        raise ValueError(f"{_LANE_NAME} funnel label inventory changed")
    result: dict[str, dict[str, int]] = {}
    for label, expected in WAVE8_BANU_BU_ALI_BERAD_FUNNEL_AUDIT.items():
        row = by_label[label]
        actual = {
            "candidate_ids": list(map(str, row.get("candidate_ids", []))),
            "event_candidate_id_sha256": str(
                row.get("event_candidate_id_sha256")
            ),
            "events_touched": int(row.get("events_touched", -1)),
            "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
            "unresolved_side_attempts": int(
                row.get("unresolved_side_attempts", -1)
            ),
            "rated_counterpart_entities": int(
                row.get("rated_counterpart_entities", -1)
            ),
            "failure_cases": {
                "zero_time_valid_candidates": int(
                    row.get("failure_cases", {}).get(
                        "zero_time_valid_candidates", -1
                    )
                )
            },
        }
        if actual != expected:
            raise ValueError(f"{_LANE_NAME} funnel pin changed for {label}: {actual}")
        result[label] = {
            "events_touched": actual["events_touched"],
            "sole_blocker_events": actual["sole_blocker_events"],
            "unresolved_side_attempts": actual["unresolved_side_attempts"],
            "zero_time_valid_candidates": actual["failure_cases"][
                "zero_time_valid_candidates"
            ],
        }
    return result


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def validate_wave8_banu_bu_ali_berad_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in (
        WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_ROW_HASHES.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} discovery row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        expected = WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_EXPECTED[candidate_id]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}")
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("name") != expected["name"]
            or row.get("kind") != expected["kind"]
            or row.get("date") != expected["date"]
            or row.get("end_date") != expected["end_date"]
            or row.get("winners") != expected["winners"]
        ):
            raise ValueError(
                f"{_LANE_NAME} discovery non-rating guard changed: {candidate_id}"
            )
    return {
        "discovery_nonrating_records": 2,
        "duplicate_superseded_records": 1,
        "lexical_false_positives": 1,
        "unknown_never_draw_rows": 2,
    }


def install_wave8_banu_bu_ali_berad_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    mughal = release_entities.get(_MUGHAL_EMPIRE)
    if (
        mughal is None
        or int(mughal.get("start_year", 0)) > 1680
        or int(mughal.get("end_year", 0)) < 1705
    ):
        raise ValueError(f"{_LANE_NAME} Mughal Empire identity-window drift")
    install_exact_entities(
        release_entities,
        WAVE8_BANU_BU_ALI_BERAD_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_banu_bu_ali_berad_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_BANU_BU_ALI_BERAD_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_BANU_BU_ALI_BERAD_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_BANU_BU_ALI_BERAD_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def validate_wave8_banu_bu_ali_berad_emissions(
    events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    owned = list(events)
    by_id = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_id) != WAVE8_BANU_BU_ALI_BERAD_CONTRACT_IDS or len(owned) != len(
        by_id
    ):
        raise ValueError(f"{_LANE_NAME} emitted inventory drift")
    participant_count = 0
    for candidate_id, contract in WAVE8_BANU_BU_ALI_BERAD_CONTRACTS.items():
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
            or event.get("date_interval")
            != {"start": canonical["start_date"], "end": canonical["end_date"]}
            or event.get("reviewed_granularity") != canonical["granularity"]
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("event_type") != "engagement"
            or event.get("war_type") != contract["war_type"]
            or event.get("participants") != expected_participants
            or event.get("aliases") != []
            or event.get("source_ids")
            != ["hced_dataset", *contract["evidence_refs"]]
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids")
            != contract["outcome_source_family_ids"]
            or "geometry" in event
            or event.get("modern_location_country")
            != WAVE8_BANU_BU_ALI_BERAD_LOCATION_QUARANTINE_REASONS[candidate_id][
                "raw_country"
            ]
        ):
            raise ValueError(f"{_LANE_NAME} emitted contract drift: {candidate_id}")
        if any(
            "inconclusive" in str(participant.get("termination", ""))
            for participant in event["participants"]
        ):
            raise ValueError(f"{_LANE_NAME} emitted unknown/draw drift: {candidate_id}")
        participant_count += len(event["participants"])
    return {
        "events": len(owned),
        "participants": participant_count,
        "retained_countries": len(owned),
        "retained_points": 0,
    }


def promote_wave8_banu_bu_ali_berad_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_banu_bu_ali_berad_queue_contracts(hced_rows)
    mughal = release_entities.get(_MUGHAL_EMPIRE)
    if (
        mughal is None
        or int(mughal.get("start_year", 0)) > 1680
        or int(mughal.get("end_year", 0)) < 1705
    ):
        raise ValueError(f"{_LANE_NAME} Mughal Empire identity-window drift")
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_BANU_BU_ALI_BERAD_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        canonical = WAVE8_BANU_BU_ALI_BERAD_CONTRACTS[candidate_id][
            "canonical_event"
        ]
        event["aliases"] = []
        event["date_interval"] = {
            "start": str(canonical["start_date"]),
            "end": str(canonical["end_date"]),
        }
    _apply_location_quarantine(events)
    validate_wave8_banu_bu_ali_berad_emissions(events)
    return events


def _entity_covers(entity: Mapping[str, Any], low: int, high: int) -> bool:
    start = entity.get("start_year")
    end = entity.get("end_year")
    return (
        start is not None
        and int(start) <= low
        and (end is None or int(end) >= high)
    )


def validate_wave8_banu_bu_ali_berad_current_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    _validate_static()
    owned = [
        event
        for event in release_events
        if event.get("hced_candidate_id")
        in WAVE8_BANU_BU_ALI_BERAD_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    entity_by_id = {str(entity.get("id")): entity for entity in release_entities}
    source_by_id = {str(source.get("id")): source for source in release_sources}
    present_entities = set(entity_by_id) & set(_ENTITY_BY_ID)
    present_sources = set(source_by_id) & set(_SOURCE_BY_ID)
    expected_counts = (
        len(WAVE8_BANU_BU_ALI_BERAD_CONTRACT_IDS),
        len(_ENTITY_BY_ID),
        len(_SOURCE_BY_ID),
    )
    actual_counts = (len(owned), len(present_entities), len(present_sources))
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
    if _MUGHAL_EMPIRE not in entity_by_id or not _entity_covers(
        entity_by_id[_MUGHAL_EMPIRE], 1680, 1705
    ):
        raise ValueError(f"{_LANE_NAME} current Mughal identity drift")
    for entity_id, expected in _ENTITY_BY_ID.items():
        if entity_by_id[entity_id] != expected:
            raise ValueError(f"{_LANE_NAME} current release entity drift: {entity_id}")
    for source_id, expected in _SOURCE_BY_ID.items():
        if source_by_id[source_id] != expected:
            raise ValueError(f"{_LANE_NAME} current release source drift: {source_id}")
    validate_wave8_banu_bu_ali_berad_emissions(owned)
    return {
        "artifact_state": "integrated",
        "installed_entities": len(present_entities),
        "installed_sources": len(present_sources),
        "promoted_events": len(owned),
    }


def wave8_banu_bu_ali_berad_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_BANU_BU_ALI_BERAD_CONTRACTS.values()
            ).items()
        )
    )


def wave8_banu_bu_ali_berad_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "discovery_nonrating_records": len(
            WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_ROW_HASHES
        ),
        "holds": 0,
        "new_entities": len(WAVE8_BANU_BU_ALI_BERAD_ENTITIES),
        "new_sources": len(WAVE8_BANU_BU_ALI_BERAD_SOURCES),
        "newly_rated_events": len(WAVE8_BANU_BU_ALI_BERAD_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_BANU_BU_ALI_BERAD_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_BANU_BU_ALI_BERAD_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_BANU_BU_ALI_BERAD_RESERVED_IDS),
        "separate_lane_holds": len(
            WAVE8_BANU_BU_ALI_BERAD_OUTSIDE_LANE_HOLDS
        ),
        "terminal_exclusions": 0,
        "unknown_discovery_outcomes": len(
            WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_ROW_HASHES
        ),
    }


def wave8_banu_bu_ali_berad_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_BANU_BU_ALI_BERAD_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_BANU_BU_ALI_BERAD_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_banu_bu_ali_berad_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_banu_bu_ali_berad_counts(),
        "cohorts": wave8_banu_bu_ali_berad_cohort_counts(),
        "country_quarantine_additions": [],
        "discovery_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_BANU_BU_ALI_BERAD_DISCOVERY_DISPOSITIONS.items()
            )
        ],
        "final_audit_signature": WAVE8_BANU_BU_ALI_BERAD_FINAL_AUDIT_SIGNATURE,
        "outside_lane_holds": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_BANU_BU_ALI_BERAD_OUTSIDE_LANE_HOLDS.items()
            )
        ],
        "point_quarantine_additions": sorted(
            WAVE8_BANU_BU_ALI_BERAD_POINT_QUARANTINE_ADDITIONS
        ),
        "promoted_candidate_ids": sorted(
            WAVE8_BANU_BU_ALI_BERAD_CONTRACT_IDS
        ),
        "reserved_candidate_ids": sorted(
            WAVE8_BANU_BU_ALI_BERAD_RESERVED_IDS
        ),
    }


if WAVE8_BANU_BU_ALI_BERAD_FINAL_AUDIT_SIGNATURE != "TO_BE_SEALED":
    _validate_static()
