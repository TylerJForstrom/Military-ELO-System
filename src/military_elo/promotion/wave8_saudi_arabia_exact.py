"""Fail-closed exact-label audit of HCED's ``Saudi Arabia`` rows.

The staged label is a routing key, not an identity.  This lane promotes only
the fingerprinted Hamdh and Jahra records and gives each side a separate,
event-bounded formation with no aliases or continuity outside the engagement.
It does not route either event through modern Saudi Arabia, Kuwait, a generic
Ikhwan identity, or another broad polity or movement label.

Hamdh remains year-only because the reviewed sources conflict on its day in
1920.  Jahra is bounded to 10--11 October 1920.  The 1934 Hudayda row is
terminally excluded: contemporary reporting describes Yemeni authorities
withdrawing before Saudi forces entered the port, and the enclosing war
already has one strategic IWD owner.  Unknown or noncompetitive records are
never converted to draws.

Two Wikidata event twins, one modern false twin, and the IWBD Hudayda record
are pinned as discovery-only/nonrating records.  None can emit an additional
rating update.
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
    "WAVE8_SAUDI_ARABIA_EXACT_CONTRACT_IDS",
    "WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS",
    "WAVE8_SAUDI_ARABIA_EXACT_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SAUDI_ARABIA_EXACT_DISCOVERY_ROW_HASHES",
    "WAVE8_SAUDI_ARABIA_EXACT_ENTITIES",
    "WAVE8_SAUDI_ARABIA_EXACT_EXPECTED_CANDIDATE_IDS",
    "WAVE8_SAUDI_ARABIA_EXACT_EXISTING_RELEASE_DUPLICATE_DISPOSITION",
    "WAVE8_SAUDI_ARABIA_EXACT_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SAUDI_ARABIA_EXACT_HOLD_IDS",
    "WAVE8_SAUDI_ARABIA_EXACT_HOLDS",
    "WAVE8_SAUDI_ARABIA_EXACT_INTEGRATION_DISPOSITIONS",
    "WAVE8_SAUDI_ARABIA_EXACT_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_SAUDI_ARABIA_EXACT_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_SAUDI_ARABIA_EXACT_LOCATION_REVIEWS",
    "WAVE8_SAUDI_ARABIA_EXACT_NONPROMOTIONS",
    "WAVE8_SAUDI_ARABIA_EXACT_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SAUDI_ARABIA_EXACT_RESERVED_IDS",
    "WAVE8_SAUDI_ARABIA_EXACT_ROW_HASHES",
    "WAVE8_SAUDI_ARABIA_EXACT_SOURCES",
    "WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSION_IDS",
    "WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSIONS",
    "WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_DUPLICATE_DISPOSITIONS",
    "WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_FALSE_TWIN_DISPOSITIONS",
    "install_wave8_saudi_arabia_exact_entities",
    "install_wave8_saudi_arabia_exact_sources",
    "promote_wave8_saudi_arabia_exact_contracts",
    "validate_wave8_saudi_arabia_exact_discovery_dispositions",
    "validate_wave8_saudi_arabia_exact_entities",
    "validate_wave8_saudi_arabia_exact_existing_parent_war",
    "validate_wave8_saudi_arabia_exact_integration_dispositions",
    "validate_wave8_saudi_arabia_exact_queue_contracts",
    "wave8_saudi_arabia_exact_audit_signature",
    "wave8_saudi_arabia_exact_cohort_counts",
    "wave8_saudi_arabia_exact_counts",
    "wave8_saudi_arabia_exact_location_quarantine_additions",
    "wave8_saudi_arabia_exact_metadata",
)


_LANE_NAME = "Wave 8 exact HCED Saudi Arabia audit"
_MODULE_OWNER = "military_elo.promotion.wave8_saudi_arabia_exact"
_EVENT_ID_PREFIX = "hced_wave8_saudi_arabia_exact_"
_EXACT_LABEL = "saudi arabia"
_PARENT_WAR_EVENT_ID = "iwd_war_48_saudi_arabia_yemen_1934"

_HAMDH_IKHWAN = "faisal_al_duwaish_ikhwan_force_hamdh_1920"
_HAMDH_KUWAITI = "duaij_al_sabah_kuwaiti_detachment_hamdh_1920"
_JAHRA_IKHWAN = "faisal_al_duwaish_ikhwan_force_jahra_1920"
_JAHRA_DEFENDERS = "salim_al_mubarak_jahra_defenders_1920"


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


WAVE8_SAUDI_ARABIA_EXACT_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_saudi_arabia_exact_al_shehabi_kcl_2015",
        "The Evolution of the Role of Merchants in Kuwaiti Politics",
        (
            "https://kclpure.kcl.ac.uk/portal/en/theses/"
            "the-evolution-of-the-role-of-merchants-in-kuwaiti-politics"
            "%286857c175-f2f8-41ba-8231-b67acb9f81a1%29.html"
        ),
        "King's College London Research Portal",
        "doctoral_dissertation",
        "al_shehabi_kcl_thesis_2015",
    ),
    _source(
        "wave8_saudi_arabia_exact_tetreault_columbia_2000",
        (
            "Stories of Democracy: Politics and Society in Contemporary "
            "Kuwait, chapter 3"
        ),
        "https://ciaotest.cc.columbia.edu/book/tetreault/ch03.html",
        "Columbia University Press / Columbia International Affairs Online",
        "academic_monograph_chapter",
        "tetreault_stories_of_democracy_2000",
    ),
    _source(
        "wave8_saudi_arabia_exact_al_sabah_duaij_profile",
        "Shaikh Duaij bin Salman Al Sabah",
        "https://alsabahkuwait.com/en-who-we-are-2",
        "Al Sabah Kuwait family-history project",
        "curated_family_history",
        "al_sabah_kuwait_duaij_profile",
    ),
    _source(
        "wave8_saudi_arabia_exact_kuna_hamdh_1920",
        "Events in Kuwait's history: the Hamdh attack of 1920",
        "https://www.kuna.net.kw/ArticleDetails.aspx?id=1744648&language=en",
        "Kuwait News Agency",
        "state_news_agency_historical_notice",
        "kuwait_news_agency_history",
    ),
    _source(
        "wave8_saudi_arabia_exact_hansard_yemen_1934",
        "The Yemen, House of Commons debate, 7 May 1934",
        (
            "https://hansard.parliament.uk/Commons/1934-05-07/debates/"
            "198f301d-9a21-479d-b8c9-78d7ef50f4fb/TheYemen"
        ),
        "UK Parliament",
        "official_parliamentary_record",
        "uk_hansard_yemen_1934",
    ),
    _source(
        "wave8_saudi_arabia_exact_qdl_saudi_yemen_1934",
        "File 6/27 Foreign Interests: Sa'udi-Yemen Dispute, folio 26r",
        "https://www.qdl.qa/en/archive/81055/vdc_100059310911.0x000034",
        "British Library India Office Records / Qatar Digital Library",
        "digitized_primary_source",
        "british_library_ior_r_15_6_163",
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_SAUDI_ARABIA_EXACT_SOURCES
}
_SOURCE_FAMILY_BY_ID = {
    source_id: str(source["source_family_id"])
    for source_id, source in _SOURCE_BY_ID.items()
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    source_ids: Iterable[str],
    boundary: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 1920,
        "end_year": 1920,
        "region": "Arabian Peninsula",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary
            + " No rating is inherited by Saudi Arabia, Kuwait, Nejd, the "
            "Ikhwan generally, Mutayr, a ruling house, a commander personally, "
            "or any other campaign formation."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_HAMDH_SOURCE_IDS = (
    "wave8_saudi_arabia_exact_al_sabah_duaij_profile",
    "wave8_saudi_arabia_exact_al_shehabi_kcl_2015",
    "wave8_saudi_arabia_exact_kuna_hamdh_1920",
    "wave8_saudi_arabia_exact_tetreault_columbia_2000",
)
_JAHRA_SOURCE_IDS = (
    "wave8_saudi_arabia_exact_al_sabah_duaij_profile",
    "wave8_saudi_arabia_exact_al_shehabi_kcl_2015",
    "wave8_saudi_arabia_exact_tetreault_columbia_2000",
)

WAVE8_SAUDI_ARABIA_EXACT_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _HAMDH_IKHWAN,
        "Faisal al-Duwaish's Ikhwan force at Hamdh in 1920",
        "event_bounded_attacking_force",
        _HAMDH_SOURCE_IDS,
        (
            "This identity contains only al-Duwaish's source-attested force in "
            "the reviewed Hamdh engagement."
        ),
    ),
    _entity(
        _HAMDH_KUWAITI,
        "Duaij bin Salman Al Sabah's Kuwaiti detachment at Hamdh in 1920",
        "event_bounded_field_detachment",
        _HAMDH_SOURCE_IDS,
        (
            "This identity contains only the Kuwaiti cavalry and infantry "
            "detachment under Duaij in the reviewed Hamdh engagement."
        ),
    ),
    _entity(
        _JAHRA_IKHWAN,
        "Faisal al-Duwaish's Ikhwan force at Jahra in 1920",
        "event_bounded_attacking_force",
        _JAHRA_SOURCE_IDS,
        (
            "This identity contains only al-Duwaish's attacking and besieging "
            "force at Jahra through 11 October 1920."
        ),
    ),
    _entity(
        _JAHRA_DEFENDERS,
        "Salim al-Mubarak's Kuwaiti and allied defenders at Jahra in 1920",
        "event_bounded_defending_force",
        _JAHRA_SOURCE_IDS,
        (
            "This identity contains only Salim al-Mubarak's Kuwaiti, local, "
            "and source-attested allied defenders in the reviewed Jahra battle."
        ),
    ),
)

_ENTITY_BY_ID = {
    str(entity["id"]): entity for entity in WAVE8_SAUDI_ARABIA_EXACT_ENTITIES
}


WAVE8_SAUDI_ARABIA_EXACT_ROW_HASHES: dict[str, str] = {
    "hced-Hamad1920-1": (
        "8291d96904e856d55195e476e1c99fd1360fa544106dbed6ebed1c179caebf83"
    ),
    "hced-Hudayda1934-1": (
        "982b0581cd30aeebb9ba4f52f1b1c629d0a7c5e07a59e8a2b1f6b35d9642739e"
    ),
    "hced-Jahrah1920-1": (
        "2fd206a6b25d96db0af552f974e0638f251bf1f57a31c164f3dd4560a3d83cea"
    ),
}
WAVE8_SAUDI_ARABIA_EXACT_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_SAUDI_ARABIA_EXACT_ROW_HASHES
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
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    date_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    source_date_conflict: bool,
    source_date_refinement: bool,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    dates = sorted(set(map(str, date_source_ids)))
    return {
        "raw_row_sha256": WAVE8_SAUDI_ARABIA_EXACT_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "kuwait_najd_border_war_1920",
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
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "date_source_ids": dates,
        "source_date_conflict": source_date_conflict,
        "source_date_refinement": source_date_refinement,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_exact_event_bounded_formations",
        "event_type": "engagement",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Hamad1920-1": _contract(
        "hced-Hamad1920-1",
        _canonical(
            "Battle of Hamdh",
            1920,
            "1920 (source-day conflict: 16 May versus 18-24 May)",
            date_precision="year",
            granularity="bounded_hamdh_engagement_not_the_broader_border_war",
        ),
        [_HAMDH_IKHWAN],
        [_HAMDH_KUWAITI],
        _HAMDH_SOURCE_IDS,
        [
            "wave8_saudi_arabia_exact_al_sabah_duaij_profile",
            "wave8_saudi_arabia_exact_kuna_hamdh_1920",
            "wave8_saudi_arabia_exact_tetreault_columbia_2000",
        ],
        _HAMDH_SOURCE_IDS,
        (
            "The rated unit is the Hamdh clash only. Al-Duwaish's bounded force "
            "defeated Duaij's Kuwaiti detachment; the result is not assigned to "
            "a generic Saudi, Kuwaiti, Nejd, or Ikhwan identity. Conflicting "
            "source days are preserved by retaining year-only precision."
        ),
        confidence=0.90,
        source_date_conflict=True,
        source_date_refinement=False,
    ),
    "hced-Jahrah1920-1": _contract(
        "hced-Jahrah1920-1",
        _canonical(
            "Battle of Jahra",
            1920,
            "1920-10-10 through 1920-10-11",
            date_precision="day_range",
            granularity="jahra_battle_and_red_fort_defense_through_11_october",
        ),
        [_JAHRA_DEFENDERS],
        [_JAHRA_IKHWAN],
        _JAHRA_SOURCE_IDS,
        [
            "wave8_saudi_arabia_exact_al_sabah_duaij_profile",
            "wave8_saudi_arabia_exact_tetreault_columbia_2000",
        ],
        [
            "wave8_saudi_arabia_exact_al_shehabi_kcl_2015",
            "wave8_saudi_arabia_exact_tetreault_columbia_2000",
        ],
        (
            "The rated unit begins with the 10 October attack and ends with the "
            "11 October defense and relief boundary. Salim's bounded defenders "
            "repelled the fort assaults and al-Duwaish's bounded attacking force "
            "withdrew. Later diplomacy and broad British deterrence are not "
            "installed as combatants or merged into this tactical result."
        ),
        confidence=0.91,
        source_date_conflict=False,
        source_date_refinement=True,
    ),
}


WAVE8_SAUDI_ARABIA_EXACT_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_SAUDI_ARABIA_EXACT_CONTRACT_IDS = frozenset(
    WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS
)
WAVE8_SAUDI_ARABIA_EXACT_HOLD_IDS = frozenset(
    WAVE8_SAUDI_ARABIA_EXACT_HOLDS
)


WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Hudayda1934-1": {
        "raw_row_sha256": WAVE8_SAUDI_ARABIA_EXACT_ROW_HASHES[
            "hced-Hudayda1934-1"
        ],
        "canonical_event": _canonical(
            "Saudi occupation of al-Hudaydah",
            1934,
            "1934-05-05",
            date_precision="day",
            granularity=(
                "unopposed_entry_after_yemeni_withdrawal_not_a_competitive_engagement"
            ),
        ),
        "cohort": "saudi_yemeni_war_1934",
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "exclusion_category": "unopposed_occupation_duplicate_parent_war",
        "reviewed_outcome": "not_rateable_unopposed_occupation",
        "unknown_is_never_draw": True,
        "raw_winner_raw": "Saudi Arabia",
        "raw_winner_loser_complete": True,
        "duplicate_of_existing_event_id": _PARENT_WAR_EVENT_ID,
        "evidence_refs": [
            "wave8_saudi_arabia_exact_hansard_yemen_1934",
            "wave8_saudi_arabia_exact_qdl_saudi_yemen_1934",
        ],
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_nonrating_exclusion",
        },
        "exclusion_reason": (
            "Contemporary reporting records that Yemeni civil and military "
            "authorities withdrew before Saudi forces entered Hodeida on 5 May. "
            "That occupation is not a contested engagement, and the enclosing "
            "Saudi-Yemen war already receives one strategic update from the IWD "
            "parent-war owner. No tactical win or draw is emitted."
        ),
    }
}
WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSIONS
)
WAVE8_SAUDI_ARABIA_EXACT_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSIONS,
}
WAVE8_SAUDI_ARABIA_EXACT_RESERVED_IDS = frozenset(
    WAVE8_SAUDI_ARABIA_EXACT_CONTRACT_IDS
    | WAVE8_SAUDI_ARABIA_EXACT_HOLD_IDS
    | WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSION_IDS
)


WAVE8_SAUDI_ARABIA_EXACT_EXISTING_RELEASE_DUPLICATE_DISPOSITION: dict[
    str, Any
] = {
    "existing_event_id": _PARENT_WAR_EVENT_ID,
    "hced_candidate_id": "hced-Hudayda1934-1",
    "disposition": "existing_parent_war_owner",
    "rating_scope": "single_strategic_update_for_saudi_yemeni_war_1934",
}


WAVE8_SAUDI_ARABIA_EXACT_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q16839041": (
        "1854f4206f1eee996162b1cd19c506e8856c9d64f1182c122de00fb3987c8e1d"
    ),
    "Q4871302": (
        "0ae349ffb9300fdeb98a21f3c3ffc234ea86a654d24dc200e5fee039c9ebec41"
    ),
    "Q48735086": (
        "dc0afcf2b7260e3bc515525aed6e2e181445df339fa9aeb5f791fcb9772ff54c"
    ),
}

_WIKIDATA_EXPECTED: dict[str, dict[str, Any]] = {
    "Q16839041": {
        "date": "1920-05-18T00:00:00Z",
        "end_date": None,
        "name": "Battle of Hamdh",
        "participant_labels": [],
        "part_of_labels": ["Kuwait–Nejd Border War"],
        "winner_labels": [],
    },
    "Q4871302": {
        "date": "1920-10-10T00:00:00Z",
        "end_date": None,
        "name": "Battle of Jahra",
        "participant_labels": ["House of Al Sabah", "Ikhwan"],
        "part_of_labels": ["Kuwait–Nejd Border War"],
        "winner_labels": [],
    },
    "Q48735086": {
        "date": "2018-06-13T00:00:00Z",
        "end_date": None,
        "name": "Battle of Al Hudaydah",
        "participant_labels": [
            "Abd al-Malik al-Houthi",
            "Saudi Arabia",
            "Supreme Political Council",
            "Tareq Saleh",
            "United Arab Emirates",
        ],
        "part_of_labels": [
            "Al Hudaydah governorate offensive",
            "Yemeni Civil War",
        ],
        "winner_labels": [],
    },
}

WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "Q16839041": {
        "source_dataset": "wikidata-battles",
        "disposition": "discovery_only_duplicate",
        "hced_candidate_id": "hced-Hamad1920-1",
        "rating_disposition": "nonrating",
        "outcome_disposition": "unknown_never_draw",
    },
    "Q4871302": {
        "source_dataset": "wikidata-battles",
        "disposition": "discovery_only_duplicate",
        "hced_candidate_id": "hced-Jahrah1920-1",
        "rating_disposition": "nonrating",
        "outcome_disposition": "unknown_never_draw",
    },
}

WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_FALSE_TWIN_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "Q48735086": {
        "source_dataset": "wikidata-battles",
        "disposition": "discovery_only_false_twin",
        "related_hced_candidate_id": "hced-Hudayda1934-1",
        "rating_disposition": "nonrating",
        "outcome_disposition": "unknown_never_draw",
        "reason": (
            "The normalized Hudaydah name resembles the 1934 row, but this is "
            "a separate 2018 Yemeni Civil War engagement with different actors."
        ),
    }
}

_IWBD_ID = "iwbd-125-48-872"
_IWBD_EXPECTED: dict[str, Any] = {
    "attacker_raw": "Yemen",
    "battle_level_victor_role": "Defender",
    "defender_raw": "Saudi Arabia",
    "duration_days": "54",
    "end_date": "1934-05-12",
    "name": "Hudayda",
    "start_date": "1934-03-20",
    "war_level_victor_role": "Initiator",
    "war_name": "Saudi-Yemeni",
    "winner_raw": "Saudi Arabia",
}
WAVE8_SAUDI_ARABIA_EXACT_IWBD_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    _IWBD_ID: {
        "raw_row_sha256": (
            "a2a2c654330cadc5e469c31d2875487cef692b36a4220fcef6b94507465eb5e2"
        ),
        "source_dataset": "iwbd",
        "disposition": "discovery_only_duplicate",
        "rating_disposition": "nonrating",
        "hced_candidate_id": "hced-Hudayda1934-1",
        "existing_release_event_id": _PARENT_WAR_EVENT_ID,
        "reason": (
            "IWBD's campaign-length Hudayda row is not a second tactical battle. "
            "It overlaps the excluded HCED occupation record and the existing "
            "strategic IWD parent-war update."
        ),
    }
}

WAVE8_SAUDI_ARABIA_EXACT_INTEGRATION_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    **WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_DUPLICATE_DISPOSITIONS,
    **WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_FALSE_TWIN_DISPOSITIONS,
    **WAVE8_SAUDI_ARABIA_EXACT_IWBD_DUPLICATE_DISPOSITIONS,
    f"existing:{_PARENT_WAR_EVENT_ID}": (
        WAVE8_SAUDI_ARABIA_EXACT_EXISTING_RELEASE_DUPLICATE_DISPOSITION
    ),
}


WAVE8_SAUDI_ARABIA_EXACT_POINT_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Hamad1920-1", "hced-Jahrah1920-1"}
)
WAVE8_SAUDI_ARABIA_EXACT_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = (
    frozenset()
)
WAVE8_SAUDI_ARABIA_EXACT_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_SAUDI_ARABIA_EXACT_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_SAUDI_ARABIA_EXACT_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_SAUDI_ARABIA_EXACT_LOCATION_REVIEWS: dict[str, dict[str, Any]] = {
    "hced-Hamad1920-1": {
        "point_disposition": "withhold_unverified_geocoder_point",
        "country_disposition": "retain_saudi_arabia",
        "raw_point": [48.1887573, 27.944825],
        "reason": (
            "The sources bound the Hamdh engagement but do not authenticate "
            "HCED's single geocoder coordinate as a battlefield point."
        ),
    },
    "hced-Jahrah1920-1": {
        "point_disposition": "withhold_unverified_geocoder_point",
        "country_disposition": "retain_kuwait",
        "raw_point": [47.6755291, 29.3365728],
        "reason": (
            "The sources establish Jahra and the Red Fort but do not authenticate "
            "HCED's single point as the battle or fort coordinate."
        ),
    },
    "hced-Hudayda1934-1": {
        "point_disposition": "not_emitted_terminal_exclusion",
        "country_disposition": "not_emitted_terminal_exclusion",
        "raw_point": [42.9708838, 14.7909118],
        "reason": (
            "The row emits no event because the reviewed record is an unopposed "
            "occupation and duplicate parent-war record."
        ),
    },
}


_EXPECTED_RAW_ROWS: dict[str, dict[str, Any]] = {
    "hced-Hamad1920-1": {
        "name": "Hamad",
        "side_1_raw": "Saudi Arabia",
        "side_2_raw": "Kuwait",
        "winner_raw": "Saudi Arabia",
        "loser_raw": "Kuwait",
        "modern_location_country": "Saudi Arabia",
        "latitude": "27.944825",
        "longitude": "48.1887573",
        "year": 1920,
    },
    "hced-Hudayda1934-1": {
        "name": "Hudayda",
        "side_1_raw": "Saudi Arabia",
        "side_2_raw": "Yemen",
        "winner_raw": "Saudi Arabia",
        "loser_raw": "Yemen",
        "modern_location_country": "Yemen",
        "latitude": "14.7909118",
        "longitude": "42.9708838",
        "year": 1934,
    },
    "hced-Jahrah1920-1": {
        "name": "Jahrah",
        "side_1_raw": "Kuwait",
        "side_2_raw": "Saudi Arabia",
        "winner_raw": "Kuwait",
        "loser_raw": "Saudi Arabia",
        "modern_location_country": "Kuwait",
        "latitude": "29.3365728",
        "longitude": "47.6755291",
        "year": 1920,
    },
}

_EXPECTED_SIDES: dict[str, tuple[list[str], list[str]]] = {
    "hced-Hamad1920-1": ([_HAMDH_IKHWAN], [_HAMDH_KUWAITI]),
    "hced-Jahrah1920-1": ([_JAHRA_DEFENDERS], [_JAHRA_IKHWAN]),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS,
        "discovery_row_hashes": WAVE8_SAUDI_ARABIA_EXACT_DISCOVERY_ROW_HASHES,
        "entities": WAVE8_SAUDI_ARABIA_EXACT_ENTITIES,
        "existing_release_duplicate_disposition": (
            WAVE8_SAUDI_ARABIA_EXACT_EXISTING_RELEASE_DUPLICATE_DISPOSITION
        ),
        "iwbd_duplicate_dispositions": (
            WAVE8_SAUDI_ARABIA_EXACT_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "location_reviews": WAVE8_SAUDI_ARABIA_EXACT_LOCATION_REVIEWS,
        "row_hashes": WAVE8_SAUDI_ARABIA_EXACT_ROW_HASHES,
        "sources": WAVE8_SAUDI_ARABIA_EXACT_SOURCES,
        "terminal_exclusions": WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSIONS,
        "wikidata_duplicate_dispositions": (
            WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_DUPLICATE_DISPOSITIONS
        ),
        "wikidata_expected": _WIKIDATA_EXPECTED,
        "wikidata_false_twin_dispositions": (
            WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_FALSE_TWIN_DISPOSITIONS
        ),
    }


def wave8_saudi_arabia_exact_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_SAUDI_ARABIA_EXACT_FINAL_AUDIT_SIGNATURE = (
    "1345c7103f37f0b1234f63c0da8d7b9e3e4f23b8ae0372c14fa54377b50ee1f1"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS),
        len(WAVE8_SAUDI_ARABIA_EXACT_HOLDS),
        len(WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSIONS),
        len(WAVE8_SAUDI_ARABIA_EXACT_ENTITIES),
        len(WAVE8_SAUDI_ARABIA_EXACT_SOURCES),
    ) != (2, 0, 1, 4, 6):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_SAUDI_ARABIA_EXACT_RESERVED_IDS != (
        WAVE8_SAUDI_ARABIA_EXACT_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    disposition_sets = (
        WAVE8_SAUDI_ARABIA_EXACT_CONTRACT_IDS,
        WAVE8_SAUDI_ARABIA_EXACT_HOLD_IDS,
        WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        disposition_sets[left] & disposition_sets[right]
        for left in range(len(disposition_sets))
        for right in range(left + 1, len(disposition_sets))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")

    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_SAUDI_ARABIA_EXACT_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(set(_SOURCE_FAMILY_BY_ID.values())) != len(source_ids):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_SAUDI_ARABIA_EXACT_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS reference")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    if len(_ENTITY_BY_ID) != len(WAVE8_SAUDI_ARABIA_EXACT_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_generic = {
        "house of al sabah",
        "ikhwan",
        "kuwait",
        "mutayr",
        "nejd",
        "saudi",
        "saudi arabia",
    }
    used_sources: set[str] = set()
    for entity in WAVE8_SAUDI_ARABIA_EXACT_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} entity opened an alias or predecessor")
        if entity["start_year"] != 1920 or entity["end_year"] != 1920:
            raise ValueError(f"{_LANE_NAME} entity window changed")
        if not str(entity["kind"]).startswith("event_bounded_"):
            raise ValueError(f"{_LANE_NAME} entity is not event-bounded")
        if normalize_label(entity["name"]) in forbidden_generic:
            raise ValueError(f"{_LANE_NAME} installed a broad identity")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} entity lacks a continuity firewall")
        entity_sources = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(entity_sources) or not set(entity_sources) <= source_ids:
            raise ValueError(f"{_LANE_NAME} entity source closure changed")
        used_sources.update(entity_sources)

    used_entities: set[str] = set()
    for candidate_id, contract in WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_SAUDI_ARABIA_EXACT_ROW_HASHES[
            candidate_id
        ]:
            raise ValueError(f"{_LANE_NAME} contract hash changed: {candidate_id}")
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["event_type"] != "engagement"
        ):
            raise ValueError(f"{_LANE_NAME} result contract changed: {candidate_id}")
        sides = (
            list(map(str, contract["side_1_entity_ids"])),
            list(map(str, contract["side_2_entity_ids"])),
        )
        if sides != _EXPECTED_SIDES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} exact actor boundary changed: {candidate_id}")
        actors = {*sides[0], *sides[1]}
        if not actors <= set(_ENTITY_BY_ID):
            raise ValueError(f"{_LANE_NAME} contract names an unknown bounded actor")
        used_entities.update(actors)

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        dates = list(map(str, contract["date_source_ids"]))
        if not all(_is_sorted_unique(values) and values for values in (evidence, outcomes, dates)):
            raise ValueError(f"{_LANE_NAME} evidence is not canonical: {candidate_id}")
        if not set(outcomes) <= set(evidence) or not set(dates) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        if not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} contract names an unknown source")
        families = sorted({_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes})
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families changed")
        used_sources.update(evidence)

    if used_entities != set(_ENTITY_BY_ID):
        raise ValueError(f"{_LANE_NAME} entity fixtures are not exactly consumed")

    hamdh = WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS["hced-Hamad1920-1"]
    jahra = WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS["hced-Jahrah1920-1"]
    if (
        hamdh["canonical_event"]["date_precision"] != "year"
        or hamdh["canonical_event"]["date_text"]
        != "1920 (source-day conflict: 16 May versus 18-24 May)"
        or hamdh["source_date_conflict"] is not True
        or hamdh["source_date_refinement"] is not False
        or "source_date_override" in hamdh
    ):
        raise ValueError(f"{_LANE_NAME} Hamdh date conflict was over-resolved")
    if (
        jahra["canonical_event"]["date_precision"] != "day_range"
        or jahra["canonical_event"]["date_text"]
        != "1920-10-10 through 1920-10-11"
        or jahra["source_date_conflict"] is not False
        or jahra["source_date_refinement"] is not True
        or "source_date_override" in jahra
    ):
        raise ValueError(f"{_LANE_NAME} Jahra date boundary changed")

    exclusion = WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSIONS[
        "hced-Hudayda1934-1"
    ]
    forbidden_outcome_keys = {
        "loser_entity_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_entity_ids",
        "winner_side",
    }
    if (
        exclusion["raw_row_sha256"]
        != WAVE8_SAUDI_ARABIA_EXACT_ROW_HASHES["hced-Hudayda1934-1"]
        or exclusion["disposition"] != "terminal_exclusion"
        or exclusion["terminal_exclusion"] is not True
        or exclusion["reviewed_outcome"] != "not_rateable_unopposed_occupation"
        or exclusion["unknown_is_never_draw"] is not True
        or exclusion["duplicate_of_existing_event_id"] != _PARENT_WAR_EVENT_ID
        or forbidden_outcome_keys & set(exclusion)
    ):
        raise ValueError(f"{_LANE_NAME} Hudayda exclusion changed")
    exclusion_sources = list(map(str, exclusion["evidence_refs"]))
    if not _is_sorted_unique(exclusion_sources) or not set(exclusion_sources) <= source_ids:
        raise ValueError(f"{_LANE_NAME} Hudayda evidence closure changed")
    used_sources.update(exclusion_sources)
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_SAUDI_ARABIA_EXACT_POINT_QUARANTINE_ADDITIONS != {
        "hced-Hamad1920-1",
        "hced-Jahrah1920-1",
    }:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_SAUDI_ARABIA_EXACT_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    if set(WAVE8_SAUDI_ARABIA_EXACT_LOCATION_REVIEWS) != (
        WAVE8_SAUDI_ARABIA_EXACT_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location review inventory is incomplete")

    if set(WAVE8_SAUDI_ARABIA_EXACT_DISCOVERY_ROW_HASHES) != set(
        _WIKIDATA_EXPECTED
    ):
        raise ValueError(f"{_LANE_NAME} Wikidata discovery inventory changed")
    if set(WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_DUPLICATE_DISPOSITIONS) != {
        "Q16839041",
        "Q4871302",
    }:
        raise ValueError(f"{_LANE_NAME} Wikidata duplicate inventory changed")
    if set(WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_FALSE_TWIN_DISPOSITIONS) != {
        "Q48735086"
    }:
        raise ValueError(f"{_LANE_NAME} Wikidata false-twin inventory changed")
    if set(WAVE8_SAUDI_ARABIA_EXACT_IWBD_DUPLICATE_DISPOSITIONS) != {_IWBD_ID}:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    if len(WAVE8_SAUDI_ARABIA_EXACT_INTEGRATION_DISPOSITIONS) != 5:
        raise ValueError(f"{_LANE_NAME} integration inventory changed")
    for disposition in (
        *WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_DUPLICATE_DISPOSITIONS.values(),
        *WAVE8_SAUDI_ARABIA_EXACT_WIKIDATA_FALSE_TWIN_DISPOSITIONS.values(),
        *WAVE8_SAUDI_ARABIA_EXACT_IWBD_DUPLICATE_DISPOSITIONS.values(),
    ):
        if disposition["rating_disposition"] != "nonrating":
            raise ValueError(f"{_LANE_NAME} discovery row became rating-eligible")

    if (
        wave8_saudi_arabia_exact_audit_signature()
        != WAVE8_SAUDI_ARABIA_EXACT_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_saudi_arabia_exact_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin all and only the three exact ``Saudi Arabia`` HCED rows."""

    _validate_static()
    exact_rows = [
        row
        for row in hced_rows
        if _EXACT_LABEL
        in {
            normalize_label(row.get("side_1_raw")),
            normalize_label(row.get("side_2_raw")),
        }
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact_rows}
    if (
        exact_ids != WAVE8_SAUDI_ARABIA_EXACT_EXPECTED_CANDIDATE_IDS
        or len(exact_rows) != len(exact_ids)
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")

    by_id = {str(row["candidate_id"]): row for row in exact_rows}
    for candidate_id, expected_hash in WAVE8_SAUDI_ARABIA_EXACT_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        expected = _EXPECTED_RAW_ROWS[candidate_id]
        actual = {
            key: row.get(key)
            for key in (
                "name",
                "side_1_raw",
                "side_2_raw",
                "winner_raw",
                "loser_raw",
                "modern_location_country",
                "latitude",
                "longitude",
            )
        }
        if actual != {key: value for key, value in expected.items() if key != "year"}:
            raise ValueError(f"{_LANE_NAME} source actor/location row changed: {candidate_id}")
        year = int(expected["year"])
        if (row.get("year_low"), row.get("year_best"), row.get("year_high")) != (
            year,
            year,
            year,
        ):
            raise ValueError(f"{_LANE_NAME} source year changed: {candidate_id}")
        if (
            row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("do_not_rate_automatically") is not True
            or row.get("duplicate_source_id") is not False
        ):
            raise ValueError(f"{_LANE_NAME} review guard changed: {candidate_id}")

    inventory = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS,
        WAVE8_SAUDI_ARABIA_EXACT_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    return {
        "exact_label_rows": len(exact_rows),
        "holds": 0,
        "promotion_contracts": inventory["promotion_contracts"],
        "reviewed_hced_rows": inventory["reviewed_hced_rows"],
        "terminal_exclusions": len(
            WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSION_IDS
        ),
    }


def validate_wave8_saudi_arabia_exact_entities(
    release_entities: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    for entity_id, expected in _ENTITY_BY_ID.items():
        actual = release_entities.get(entity_id)
        if actual is None:
            raise ValueError(f"{_LANE_NAME} missing bounded entity: {entity_id}")
        if dict(actual) != expected:
            raise ValueError(f"{_LANE_NAME} bounded entity drift: {entity_id}")
    return {"required_bounded_entities": len(_ENTITY_BY_ID)}


def validate_wave8_saudi_arabia_exact_existing_parent_war(
    existing_events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    """Pin the sole strategic owner that makes Hudayda a duplicate record."""

    _validate_static()
    owners = [
        event
        for event in existing_events
        if str(event.get("id")) == _PARENT_WAR_EVENT_ID
    ]
    if len(owners) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one 1934 parent-war owner, found {len(owners)}"
        )
    owner = owners[0]
    participants = {
        (str(item.get("entity_id")), str(item.get("termination")))
        for item in owner.get("participants", [])
    }
    if (
        owner.get("name") != "Saudi Arabia-Yemen 1934"
        or (owner.get("year"), owner.get("end_year")) != (1934, 1934)
        or owner.get("event_type") != "war"
        or owner.get("iwd_parent_war_id") != "48"
        or owner.get("iwd_parent_war_name") != "SaudiArabia-Yemen1934"
        or participants
        != {
            ("kingdom_saudi_arabia", "victory"),
            ("mutawakkilite_kingdom_yemen", "defeat"),
        }
    ):
        raise ValueError(f"{_LANE_NAME} 1934 parent-war owner changed")
    return {"existing_parent_war_owners": 1}


def validate_wave8_saudi_arabia_exact_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin all discovery twins and prove that none is rating-eligible."""

    _validate_static()
    wikidata_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        wikidata_by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in (
        WAVE8_SAUDI_ARABIA_EXACT_DISCOVERY_ROW_HASHES.items()
    ):
        rows = wikidata_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} Wikidata row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(
                f"{_LANE_NAME} Wikidata fingerprint changed: {candidate_id}"
            )
        expected = _WIKIDATA_EXPECTED[candidate_id]
        participant_labels = sorted(
            str(item.get("label")) for item in row.get("participants", [])
        )
        part_of_labels = sorted(
            str(item.get("label")) for item in row.get("part_of", [])
        )
        winner_labels = sorted(
            str(item.get("label")) for item in row.get("winners", [])
        )
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("name") != expected["name"]
            or row.get("date") != expected["date"]
            or row.get("end_date") != expected["end_date"]
            or participant_labels != sorted(expected["participant_labels"])
            or part_of_labels != sorted(expected["part_of_labels"])
            or winner_labels != expected["winner_labels"]
        ):
            raise ValueError(
                f"{_LANE_NAME} Wikidata nonrating guard changed: {candidate_id}"
            )

    iwbd_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in iwbd_rows:
        iwbd_by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    iwbd_matches = iwbd_by_id.get(_IWBD_ID, [])
    if len(iwbd_matches) != 1:
        raise ValueError(
            f"{_LANE_NAME} IWBD row {_IWBD_ID} expected once, "
            f"found {len(iwbd_matches)}"
        )
    iwbd_row = iwbd_matches[0]
    iwbd_disposition = WAVE8_SAUDI_ARABIA_EXACT_IWBD_DUPLICATE_DISPOSITIONS[
        _IWBD_ID
    ]
    if _full_row_sha256(iwbd_row) != iwbd_disposition["raw_row_sha256"]:
        raise ValueError(f"{_LANE_NAME} IWBD fingerprint changed: {_IWBD_ID}")
    actual_iwbd = {key: iwbd_row.get(key) for key in _IWBD_EXPECTED}
    if (
        actual_iwbd != _IWBD_EXPECTED
        or iwbd_row.get("source") != "iwbd"
        or iwbd_row.get("do_not_rate_automatically") is not True
    ):
        raise ValueError(f"{_LANE_NAME} IWBD nonrating guard changed")

    return {
        "discovery_promotions": 0,
        "iwbd_discovery_duplicates": 1,
        "unknown_never_draw_wikidata_rows": 3,
        "wikidata_discovery_duplicates": 2,
        "wikidata_false_twins": 1,
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low", "batyear"):
        value = row.get(field)
        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            pass
    for field in ("date", "start_date", "end_date"):
        value = str(row.get(field) or "")
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


_EVENT_ALIASES: dict[int, set[str]] = {
    1920: {
        normalize_label(alias)
        for alias in (
            "Battle of Hamdh",
            "Hamdh",
            "Hamad",
            "Battle of Jahra",
            "Jahra",
            "Jahrah",
        )
    },
    1934: {
        normalize_label(alias)
        for alias in (
            "Hudayda",
            "Hudaydah",
            "Hodeida",
            "Hodeidah",
            "Al Hudaydah",
            "Saudi occupation of al-Hudaydah",
        )
    },
}


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year in _EVENT_ALIASES and bool(_row_names(row) & _EVENT_ALIASES[year])


def validate_wave8_saudi_arabia_exact_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    wikidata_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    """Validate declared duplicates and fail closed on any undeclared twin."""

    validate_wave8_saudi_arabia_exact_queue_contracts(hced_rows)
    validate_wave8_saudi_arabia_exact_discovery_dispositions(
        wikidata_rows,
        iwbd_rows,
    )
    existing = list(existing_events)
    validate_wave8_saudi_arabia_exact_existing_parent_war(existing)

    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_SAUDI_ARABIA_EXACT_RESERVED_IDS
        and _is_probable_twin(row)
    )
    declared_wikidata = set(WAVE8_SAUDI_ARABIA_EXACT_DISCOVERY_ROW_HASHES)
    wikidata_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in wikidata_rows
        if str(row.get("candidate_id")) not in declared_wikidata
        and _is_probable_twin(row)
    )
    declared_iwbd = set(WAVE8_SAUDI_ARABIA_EXACT_IWBD_DUPLICATE_DISPOSITIONS)
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if str(row.get("candidate_id")) not in declared_iwbd
        and _is_probable_twin(row)
    )

    owned_lane_events = [
        event
        for event in existing
        if event.get("hced_candidate_id")
        in WAVE8_SAUDI_ARABIA_EXACT_CONTRACT_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    if owned_lane_events:
        owned_ids = {
            str(event.get("hced_candidate_id")) for event in owned_lane_events
        }
        if (
            owned_ids != WAVE8_SAUDI_ARABIA_EXACT_CONTRACT_IDS
            or len(owned_lane_events) != len(owned_ids)
            or any(
                not str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
                for event in owned_lane_events
            )
        ):
            raise ValueError(f"{_LANE_NAME} current release ownership is partial")
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event not in owned_lane_events
        and str(event.get("id")) != _PARENT_WAR_EVENT_ID
        and _is_probable_twin(event)
    )
    if hced_twins or wikidata_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"wikidata={wikidata_twins}, iwbd={iwbd_twins}, "
            f"release={release_twins}"
        )
    return {
        "existing_parent_war_owners": 1,
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwbd_discovery_duplicates": 1,
        "iwbd_probable_twins": 0,
        "wikidata_discovery_duplicates": 2,
        "wikidata_false_twins": 1,
        "wikidata_probable_twins": 0,
    }


def install_wave8_saudi_arabia_exact_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SAUDI_ARABIA_EXACT_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_saudi_arabia_exact_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SAUDI_ARABIA_EXACT_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_reviews(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SAUDI_ARABIA_EXACT_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SAUDI_ARABIA_EXACT_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_saudi_arabia_exact_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_saudi_arabia_exact_queue_contracts(hced_rows)
    validate_wave8_saudi_arabia_exact_entities(release_entities)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    for event in events:
        contract = WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS[
            str(event["hced_candidate_id"])
        ]
        event["event_type"] = str(contract["event_type"])
    _apply_location_reviews(events)
    return events


def wave8_saudi_arabia_exact_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS.values()
            ).items()
        )
    )


def wave8_saudi_arabia_exact_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "discovery_nonrating_rows": 4,
        "holds": 0,
        "integration_dispositions": len(
            WAVE8_SAUDI_ARABIA_EXACT_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_discovery_duplicates": 1,
        "new_entities": len(WAVE8_SAUDI_ARABIA_EXACT_ENTITIES),
        "new_sources": len(WAVE8_SAUDI_ARABIA_EXACT_SOURCES),
        "newly_rated_events": len(WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_SAUDI_ARABIA_EXACT_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_SAUDI_ARABIA_EXACT_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_SAUDI_ARABIA_EXACT_RESERVED_IDS),
        "terminal_exclusions": len(
            WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSION_IDS
        ),
        "wikidata_discovery_duplicates": 2,
        "wikidata_false_twins": 1,
    }


def wave8_saudi_arabia_exact_location_quarantine_additions() -> dict[str, int]:
    _validate_static()
    return {
        "country": len(WAVE8_SAUDI_ARABIA_EXACT_COUNTRY_QUARANTINE_ADDITIONS),
        "point": len(WAVE8_SAUDI_ARABIA_EXACT_POINT_QUARANTINE_ADDITIONS),
    }


def wave8_saudi_arabia_exact_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_saudi_arabia_exact_counts(),
        "cohorts": wave8_saudi_arabia_exact_cohort_counts(),
        "final_audit_signature": WAVE8_SAUDI_ARABIA_EXACT_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_SAUDI_ARABIA_EXACT_CONTRACT_IDS),
        "hold_candidate_ids": [],
        "terminal_exclusion_candidate_ids": sorted(
            WAVE8_SAUDI_ARABIA_EXACT_TERMINAL_EXCLUSION_IDS
        ),
        "discovery_nonrating_candidate_ids": sorted(
            {
                *WAVE8_SAUDI_ARABIA_EXACT_DISCOVERY_ROW_HASHES,
                *WAVE8_SAUDI_ARABIA_EXACT_IWBD_DUPLICATE_DISPOSITIONS,
            }
        ),
    }


_validate_static()
