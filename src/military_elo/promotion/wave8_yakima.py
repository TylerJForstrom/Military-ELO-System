"""Candidate-keyed Wave 8 audit for the exact HCED label "Yakima Indians".

The locked queue contains four exact-label rows.  Two support bounded tactical
results: the Yakama-Palouse defeat of Haller's column at Toppenish Creek and
the displacement of Kamiakin's defenders from the Union Gap breastworks by
Rains's combined force.  The latter is deliberately limited to the field
action; Rains's wider suppression expedition failed.

Satus remains held because a successful Indigenous ambush, a volunteer
counterattack, stock capture, and both forces' withdrawals do not yield one
uniquely defensible winner.  Grande Ronde is terminally excluded because the
row mislabels Walla Walla, Umatilla, and Cayuse families as Yakima Indians and
describes a noncompetitive civilian massacre.

Every rated actor is event bounded.  Nothing in this lane creates a generic
Yakama, Yakima, Palouse, United States, U.S. Army, territorial-volunteer, or
modern Yakama Nation identity.  Unknown is never converted into a draw.
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
    "WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS",
    "WAVE8_YAKIMA_ADJACENT_ROW_HASHES",
    "WAVE8_YAKIMA_CONTRACT_IDS",
    "WAVE8_YAKIMA_CONTRACTS",
    "WAVE8_YAKIMA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS",
    "WAVE8_YAKIMA_ENTITIES",
    "WAVE8_YAKIMA_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_YAKIMA_EXCLUSION_IDS",
    "WAVE8_YAKIMA_EXCLUSIONS",
    "WAVE8_YAKIMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS",
    "WAVE8_YAKIMA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_YAKIMA_FUNNEL_EVENT_CANDIDATE_ID_SHA256",
    "WAVE8_YAKIMA_HCED_QUEUE_SHA256",
    "WAVE8_YAKIMA_HOLD_IDS",
    "WAVE8_YAKIMA_HOLDS",
    "WAVE8_YAKIMA_INTEGRATION_DISPOSITIONS",
    "WAVE8_YAKIMA_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_YAKIMA_IWBD_QUEUE_SHA256",
    "WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_YAKIMA_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_YAKIMA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_YAKIMA_NONPROMOTIONS",
    "WAVE8_YAKIMA_OUTCOME_OVERRIDES",
    "WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_YAKIMA_RELATED_HCED_DISPOSITIONS",
    "WAVE8_YAKIMA_RESERVED_IDS",
    "WAVE8_YAKIMA_ROW_HASHES",
    "WAVE8_YAKIMA_SOURCES",
    "WAVE8_YAKIMA_TERMINAL_EXCLUSION_IDS",
    "WAVE8_YAKIMA_TERMINAL_EXCLUSIONS",
    "WAVE8_YAKIMA_WAR_CANDIDATE_ID_SHA256",
    "WAVE8_YAKIMA_WAR_CANDIDATE_IDS",
    "install_wave8_yakima_entities",
    "install_wave8_yakima_sources",
    "promote_wave8_yakima_contracts",
    "validate_wave8_yakima_integration_dispositions",
    "validate_wave8_yakima_queue_contracts",
    "wave8_yakima_audit_signature",
    "wave8_yakima_cohort_counts",
    "wave8_yakima_counts",
    "wave8_yakima_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Yakima Indians exact-force audit"
_EVENT_ID_PREFIX = "hced_wave8_yakima_"
_MODULE_OWNER = "military_elo.promotion.wave8_yakima"

_TOPPENISH_INDIGENOUS_ID = (
    "kamiakin_yakama_palouse_coalition_toppenish_creek_1855"
)
_TOPPENISH_US_ID = "haller_fourth_infantry_column_toppenish_creek_1855"
_UNION_GAP_US_ID = "rains_regular_volunteer_force_union_gap_1855"
_UNION_GAP_INDIGENOUS_ID = "kamiakin_yakama_allied_defenders_union_gap_1855"


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
    scope_guard: bool = False,
) -> dict[str, Any]:
    roles = {"identity_boundary_or_context_reference"}
    if outcome:
        roles.add("outcome")
    if crosscheck:
        roles.add("outcome_consistency_crosscheck")
    if scope_guard:
        roles.add("identity_boundary_or_context_reference")
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


WAVE8_YAKIMA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_yakima_historylink_toppenish",
        "Yakama War begins on October 5, 1855",
        "https://www.historylink.org/file/5311",
        "HistoryLink",
        "state_historical_encyclopedia",
        "historylink_toppenish_5311",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_yakima_historylink_kamiakin",
        "Chief Kamiakin (ca. 1800-1877)",
        "https://www.historylink.org/file/10096",
        "HistoryLink",
        "scholarly_biographical_history",
        "historylink_kamiakin_10096",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_yakima_carpenter_dissertation",
        (
            "Rake Up No Old Stories of Evil: Settler Colonialism and the War "
            "on Illahee, 1846-1877"
        ),
        (
            "https://scholarsbank.uoregon.edu/server/api/core/bitstreams/"
            "da87f1de-6c77-42a6-95ed-1824a7a8155c/content"
        ),
        "University of Oregon",
        "doctoral_dissertation",
        "carpenter_war_on_illahee_dissertation",
        outcome=True,
        crosscheck=True,
        scope_guard=True,
    ),
    _source(
        "wave8_yakima_usfs_cultural_overview",
        "A Cultural Resource Overview of the Gifford Pinchot National Forest",
        "https://npshistory.com/publications/usfs/region/6/gifford-pinchot/cro.pdf",
        "U.S. Forest Service",
        "federal_cultural_resource_history",
        "usfs_gifford_pinchot_cultural_overview",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_yakima_historylink_union_gap",
        "Major Gabriel Rains and soldiers and volunteers skirmish at Union Gap",
        "https://www.historylink.org/File/8124",
        "HistoryLink",
        "state_historical_encyclopedia",
        "historylink_union_gap_8124",
        outcome=True,
        crosscheck=True,
        scope_guard=True,
    ),
    _source(
        "wave8_yakima_painter_journals",
        "Journals of the Indian War of 1855-56",
        (
            "https://journals.lib.washington.edu/index.php/WHQ/article/"
            "download/9230/8265"
        ),
        "Washington Historical Quarterly / University of Washington",
        "edited_participant_diaries",
        "painter_oregon_volunteer_journals",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_yakima_ruby_brown_pacific_northwest",
        "Indians of the Pacific Northwest: A History",
        "https://books.google.com/books?id=Ww8odDD86oAC&pg=PA264",
        "University of Oklahoma Press",
        "scholarly_monograph",
        "ruby_brown_indians_pacific_northwest",
        outcome=True,
        crosscheck=True,
        scope_guard=True,
    ),
    _source(
        "wave8_yakima_wa_parks_union_gap",
        "Yakima Sportsman State Park History",
        (
            "https://parks.wa.gov/about/news-center/field-guide-blog/"
            "yakima-sportsman-state-park-history"
        ),
        "Washington State Parks",
        "state_government_public_history",
        "washington_state_parks_union_gap",
        scope_guard=True,
    ),
    _source(
        "wave8_yakima_historylink_satus",
        "Oregon volunteers battle Yakamas and Klickitats along Satus Creek",
        "https://www.historylink.org/File/8152",
        "HistoryLink",
        "state_historical_encyclopedia",
        "historylink_satus_8152",
        scope_guard=True,
    ),
    _source(
        "wave8_yakima_splawn_kamiakin",
        "Ka-mi-akin, the Last Hero of the Yakimas",
        (
            "https://www.sos.wa.gov/library/research-collections/"
            "classics-washington-history/ka-mi-akin-last-hero-yakimas"
        ),
        "Washington State Library, Office of the Secretary of State",
        "digitized_regional_history_and_oral_accounts",
        "splawn_kamiakin_state_library",
        scope_guard=True,
    ),
    _source(
        "wave8_yakima_oregon_encyclopedia_grande_ronde",
        "Grande Ronde Massacre, 1856",
        "https://www.oregonencyclopedia.org/articles/grande-ronde-massacre/",
        "Oregon Historical Society and Portland State University",
        "scholarly_state_encyclopedia",
        "oregon_encyclopedia_grande_ronde",
        scope_guard=True,
    ),
    _source(
        "wave8_yakima_nara_bia_m5",
        (
            "Microfilm Publication M5: Records of the Washington "
            "Superintendency of Indian Affairs"
        ),
        "https://www.archives.gov/files/research/native-americans/bia/m5.pdf",
        "U.S. National Archives and Records Administration",
        "federal_archival_finding_aid",
        "nara_bia_m5_washington_superintendency",
        scope_guard=True,
    ),
    _source(
        "wave8_yakima_historylink_cascades",
        "Native Americans attack at the Cascades of the Columbia on March 26, 1856",
        "https://www.historylink.org/file/5190",
        "HistoryLink",
        "state_historical_encyclopedia",
        "historylink_cascades_5190",
        scope_guard=True,
    ),
    _source(
        "wave8_yakima_wa_parks_steptoe",
        "Steptoe Battlefield State Park Heritage Site History",
        (
            "https://parks.wa.gov/about/news-center/field-guide-blog/"
            "steptoe-battlefield-state-park-heritage-site-history"
        ),
        "Washington State Parks",
        "state_government_battlefield_history",
        "washington_state_parks_steptoe",
        scope_guard=True,
    ),
    _source(
        "wave8_yakima_historylink_four_lakes",
        "U.S. Army defeats Native Americans at Battle of Four Lakes",
        "https://www.historylink.org/File/5143",
        "HistoryLink",
        "state_historical_encyclopedia",
        "historylink_four_lakes_5143",
        scope_guard=True,
    ),
    _source(
        "wave8_yakima_govinfo_indian_disturbances",
        "Indian Disturbances in California, Oregon, and Washington",
        (
            "https://www.govinfo.gov/content/pkg/"
            "SERIALSET-00819_00_00-006-0026-0000/pdf/"
            "SERIALSET-00819_00_00-006-0026-0000.pdf"
        ),
        "U.S. War Department, 34th Congress, Senate Executive Document 26",
        "congressional_serial_set_primary_correspondence",
        "war_department_indian_disturbances_1855",
        scope_guard=True,
    ),
)


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_YAKIMA_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    source_ids: Iterable[str],
    scope: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 1855,
        "end_year": 1855,
        "region": "Columbia Plateau, North America",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            f"{scope} This identity exists only for the named 1855 event. "
            "No rating is inherited by the Yakama or Palouse peoples, the "
            "fourteen treaty tribes, the modern Yakama Nation, the United "
            "States, the U.S. Army, Oregon or Washington volunteers, "
            "noncombatants, families, or any later force."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_YAKIMA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _TOPPENISH_INDIGENOUS_ID,
        "Kamiakin-led Yakama-Palouse fighting coalition at Toppenish Creek (1855)",
        "event_bounded_indigenous_coalition",
        [
            "wave8_yakima_carpenter_dissertation",
            "wave8_yakima_historylink_kamiakin",
            "wave8_yakima_historylink_toppenish",
            "wave8_yakima_nara_bia_m5",
        ],
        (
            "Event-bounded fighters under Kamiakin, Owhi, Qualchan, and allied "
            "leaders who opposed Haller's column during the battle and retreat."
        ),
    ),
    _entity(
        _TOPPENISH_US_ID,
        "Haller's U.S. Fourth Infantry column at Toppenish Creek (1855)",
        "event_bounded_expeditionary_column",
        [
            "wave8_yakima_carpenter_dissertation",
            "wave8_yakima_historylink_toppenish",
            "wave8_yakima_usfs_cultural_overview",
        ],
        (
            "Event-bounded Fourth Infantry punitive column commanded by Major "
            "Granville O. Haller, including only its attached combatants and scouts."
        ),
    ),
    _entity(
        _UNION_GAP_US_ID,
        "Rains's combined regular-volunteer force at Union Gap (1855)",
        "event_bounded_combined_assault_force",
        [
            "wave8_yakima_govinfo_indian_disturbances",
            "wave8_yakima_historylink_union_gap",
            "wave8_yakima_painter_journals",
            "wave8_yakima_ruby_brown_pacific_northwest",
        ],
        (
            "Event-bounded U.S. regulars and Oregon and Washington volunteers "
            "that attacked the Two Buttes positions under Major Gabriel J. Rains."
        ),
    ),
    _entity(
        _UNION_GAP_INDIGENOUS_ID,
        "Kamiakin-led Yakama and allied defense force at Union Gap (1855)",
        "event_bounded_indigenous_defense_force",
        [
            "wave8_yakima_historylink_union_gap",
            "wave8_yakima_nara_bia_m5",
            "wave8_yakima_ruby_brown_pacific_northwest",
            "wave8_yakima_wa_parks_union_gap",
        ],
        (
            "Event-bounded warriors who defended and evacuated the Union Gap "
            "positions; unnamed allied participants are not expanded into tribes."
        ),
    ),
)


WAVE8_YAKIMA_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_YAKIMA_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)
WAVE8_YAKIMA_ROW_HASHES: dict[str, str] = {
    "hced-Grande Ronde Valley1856-1": (
        "b26008b8d496c7d4d7fbe80d3e75db87e05066117bae64bf4202ffe49574a643"
    ),
    "hced-Satus1856-1": (
        "a751cac298c4d60aba5453cea5adc6fe748e61d3bae9c0867cf9a8cc25314a37"
    ),
    "hced-Toppenish1855-1": (
        "c51feef022fa462fde32a2c8b87834c232b848fe36fd1cd89256c162bb0b353b"
    ),
    "hced-Union Gap1855-1": (
        "8546f447f6d08682d5af435f44d3677eb80dc511dcee2477218ca18416acf14a"
    ),
}
WAVE8_YAKIMA_ADJACENT_ROW_HASHES: dict[str, str] = {
    "hced-Cascades1856-1": (
        "d93d3ffc159854f35bf2c064fe922248d2c929f19b30e972c6a20d84aff0ee06"
    ),
    "hced-Four Lakes1858-1": (
        "be8b342066f693c95b755bd3ba28cdd7e5be4972ea3bd988b895a30f651c6b72"
    ),
    "hced-Pine Creek1858-1": (
        "92a1fb313385a973a7f4639e974da6ffada42406a45937e2e80926e49d0bf88a"
    ),
    "hced-Spokane Plain1858-1": (
        "af9198a2c2e5036babdaa4aaf6d54b981d433fa420d1f83f9bcb0a699d260ecc"
    ),
}
WAVE8_YAKIMA_EXACT_CANDIDATE_ID_SHA256 = (
    "65081d0328a98785942285646c7fccc6738acd1239f6acaa759337dc143a7519"
)
WAVE8_YAKIMA_FUNNEL_EVENT_CANDIDATE_ID_SHA256 = (
    "65081d0328a98785942285646c7fccc6738acd1239f6acaa759337dc143a7519"
)
WAVE8_YAKIMA_WAR_CANDIDATE_ID_SHA256 = (
    "f29b2e7e66d322f13781b49b7ad9e8056b7066119a422dce559f2886e53d89e3"
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
        "raw_row_sha256": WAVE8_YAKIMA_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_YAKIMA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Toppenish1855-1": _contract(
        "hced-Toppenish1855-1",
        _canonical(
            "Battle of Toppenish Creek (Haller's Defeat)",
            1855,
            "5-8 October 1855",
            date_precision="day_range",
            granularity="multi_day_battle_and_fighting_retreat",
        ),
        "yakama_war_1855_1856",
        [_TOPPENISH_INDIGENOUS_ID],
        [_TOPPENISH_US_ID],
        [
            "wave8_yakima_carpenter_dissertation",
            "wave8_yakima_historylink_kamiakin",
            "wave8_yakima_historylink_toppenish",
            "wave8_yakima_usfs_cultural_overview",
        ],
        [
            "wave8_yakima_carpenter_dissertation",
            "wave8_yakima_historylink_kamiakin",
            "wave8_yakima_historylink_toppenish",
            "wave8_yakima_usfs_cultural_overview",
        ],
        (
            "Independent scholarly, federal, and state histories identify Haller's "
            "defeat: Yakama and Palouse fighters surrounded his punitive column, "
            "forced its retreat to The Dalles, and captured or caused abandonment "
            "of supplies and the howitzer. The contract covers the bounded battle "
            "and fighting retreat, not a timeless Yakama or Palouse polity."
        ),
        confidence=0.96,
    ),
    "hced-Union Gap1855-1": _contract(
        "hced-Union Gap1855-1",
        _canonical(
            "Battle of Union Gap (Two Buttes)",
            1855,
            "9-10 November 1855",
            date_precision="day_range",
            granularity="two_day_breastwork_assault_and_field_withdrawal",
        ),
        "yakama_war_1855_1856",
        [_UNION_GAP_US_ID],
        [_UNION_GAP_INDIGENOUS_ID],
        [
            "wave8_yakima_govinfo_indian_disturbances",
            "wave8_yakima_historylink_union_gap",
            "wave8_yakima_painter_journals",
            "wave8_yakima_ruby_brown_pacific_northwest",
            "wave8_yakima_wa_parks_union_gap",
        ],
        [
            "wave8_yakima_historylink_union_gap",
            "wave8_yakima_painter_journals",
            "wave8_yakima_ruby_brown_pacific_northwest",
        ],
        (
            "The participant diary and independent histories attest that Rains's "
            "combined force used artillery and assaults to dislodge the defenders "
            "from the Two Buttes positions and held the field. This is a reduced-"
            "confidence tactical displacement only: Kamiakin evacuated the families "
            "and force, Rains failed to suppress the resistance, and no strategic "
            "victory or destruction is inferred."
        ),
        confidence=0.82,
    ),
}


WAVE8_YAKIMA_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Satus1856-1": {
        "raw_row_sha256": WAVE8_YAKIMA_ROW_HASHES["hced-Satus1856-1"],
        "canonical_event": _canonical(
            "Battle of Satus Creek",
            1856,
            "10 April 1856",
            date_precision="day",
            granularity="ambush_counterattack_and_disengagement",
        ),
        "cohort": "yakama_war_1855_1856",
        "disposition": "hold",
        "terminal_exclusion": False,
        "hold_category": "outcome_not_uniquely_defensible",
        "hold_reason": (
            "Yakama and Klickitat fighters successfully ambushed Hembree's scout "
            "party and captured much of the volunteer stock, but Cornelius's main "
            "body counterattacked, drove fighters from successive hills, and "
            "continued its withdrawal. The reviewed primary diary and secondary "
            "histories do not establish one common tactical winner for the whole "
            "row. HCED's Yakima win is therefore neither promoted, reversed, nor "
            "converted into a draw; unknown is never a draw."
        ),
        "reviewed_outcome": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_granularity": "ambush_counterattack_and_disengagement",
        "evidence_refs": [
            "wave8_yakima_historylink_satus",
            "wave8_yakima_painter_journals",
            "wave8_yakima_splawn_kamiakin",
        ],
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "held_hced_owner",
        },
        "historical_review": {
            "attested_indigenous_side": "Yakama and Klickitat fighters under Kamiakin",
            "attested_us_side": "Thomas Cornelius's Oregon volunteer column",
            "indigenous_successes": [
                "Hembree reconnaissance ambushed",
                "volunteer stock captured",
            ],
            "volunteer_successes": [
                "main camp held",
                "fighters driven from successive hill positions",
            ],
            "whole_event_winner": "not uniquely defensible",
        },
    }
}


WAVE8_YAKIMA_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Grande Ronde Valley1856-1": {
        "raw_row_sha256": WAVE8_YAKIMA_ROW_HASHES[
            "hced-Grande Ronde Valley1856-1"
        ],
        "canonical_event": _canonical(
            "Grande Ronde Massacre",
            1856,
            "17 July 1856",
            date_precision="day",
            granularity="civilian_village_massacre",
        ),
        "cohort": "yakama_war_1855_1856",
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "hold_category": "wrong_actor_and_noncompetitive_civilian_massacre",
        "hold_reason": (
            "The Oregon Encyclopedia and archival scholarship identify the victims "
            "as Walla Walla, Umatilla, and Cayuse families, with only a few armed "
            "young men, attacked while gathering food. The event was a massacre, "
            "not a competitive United States-versus-Yakima engagement. Repairing "
            "the row would require replacing its actor and rating civilian victims, "
            "so no Elo outcome is emitted; unknown is never a draw."
        ),
        "reviewed_outcome": "not_rateable_wrong_actor_massacre",
        "unknown_is_never_draw": True,
        "reviewed_granularity": "civilian_village_massacre",
        "evidence_refs": [
            "wave8_yakima_carpenter_dissertation",
            "wave8_yakima_oregon_encyclopedia_grande_ronde",
        ],
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "terminal_hced_owner",
        },
        "historical_review": {
            "raw_opposing_label": "Yakima Indians",
            "attested_communities": [
                "Cayuse families",
                "Umatilla families",
                "Walla Walla families",
            ],
            "competitive_event": False,
            "massacre_raw": "Yes",
            "repair_risk": "would substitute actors and rate civilian victims",
        },
    }
}

WAVE8_YAKIMA_EXCLUSIONS = WAVE8_YAKIMA_TERMINAL_EXCLUSIONS
WAVE8_YAKIMA_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_YAKIMA_HOLDS,
    **WAVE8_YAKIMA_TERMINAL_EXCLUSIONS,
}

WAVE8_YAKIMA_CONTRACT_IDS = frozenset(WAVE8_YAKIMA_CONTRACTS)
WAVE8_YAKIMA_HOLD_IDS = frozenset(WAVE8_YAKIMA_HOLDS)
WAVE8_YAKIMA_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_YAKIMA_TERMINAL_EXCLUSIONS
)
WAVE8_YAKIMA_EXCLUSION_IDS = WAVE8_YAKIMA_TERMINAL_EXCLUSION_IDS
WAVE8_YAKIMA_RESERVED_IDS = frozenset(
    WAVE8_YAKIMA_CONTRACT_IDS
    | WAVE8_YAKIMA_HOLD_IDS
    | WAVE8_YAKIMA_TERMINAL_EXCLUSION_IDS
)
WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_YAKIMA_ROW_HASHES)
WAVE8_YAKIMA_WAR_CANDIDATE_IDS = frozenset(
    WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS | set(WAVE8_YAKIMA_ADJACENT_ROW_HASHES)
)


WAVE8_YAKIMA_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Toppenish1855-1": {
        "actions": ["withhold_point"],
        "raw_point": [-120.3086667, 46.3773509],
        "retained_country": "United States",
        "evidence_refs": [
            "wave8_yakima_carpenter_dissertation",
            "wave8_yakima_historylink_toppenish",
        ],
        "reason": (
            "The staged locality point does not identify the multi-day ford, hill "
            "positions, retreat route, or full battlefield footprint."
        ),
    },
    "hced-Union Gap1855-1": {
        "actions": ["withhold_point"],
        "raw_point": [-120.5323975, 46.5551181],
        "retained_country": "United States",
        "evidence_refs": [
            "wave8_yakima_historylink_union_gap",
            "wave8_yakima_wa_parks_union_gap",
        ],
        "reason": (
            "The modern locality coordinate is not an authenticated point for the "
            "Two Buttes breastworks, approaches, camps, and withdrawal routes."
        ),
    },
}
WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_YAKIMA_LOCATION_QUARANTINE_REASONS
)
WAVE8_YAKIMA_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_YAKIMA_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_YAKIMA_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Cascades1856-1": {
        "raw_row_sha256": WAVE8_YAKIMA_ADJACENT_ROW_HASHES[
            "hced-Cascades1856-1"
        ],
        "disposition": "distinct_composite_coalition_event",
        "relationship": "different_date_place_scope_and_composite_label",
        "owner_scope": "separate Yakama-Klickitat-Cascades coalition audit",
        "reason": (
            "The 26 March Cascades attack is a distinct siege and civilian attack "
            "whose composite label is not the exact Yakima Indians lane."
        ),
        "evidence_refs": ["wave8_yakima_historylink_cascades"],
    },
    "hced-Pine Creek1858-1": {
        "raw_row_sha256": WAVE8_YAKIMA_ADJACENT_ROW_HASHES[
            "hced-Pine Creek1858-1"
        ],
        "disposition": "distinct_composite_coalition_event",
        "relationship": "different_campaign_year_and_allied_force",
        "owner_scope": "separate Steptoe-Tohotonimme coalition audit",
        "reason": (
            "The May 1858 Steptoe/Tohotonimme battle belongs to an allied "
            "Spokane-Coeur d'Alene-Palouse-Yakama context and is not a 1855 twin."
        ),
        "evidence_refs": ["wave8_yakima_wa_parks_steptoe"],
    },
    "hced-Four Lakes1858-1": {
        "raw_row_sha256": WAVE8_YAKIMA_ADJACENT_ROW_HASHES[
            "hced-Four Lakes1858-1"
        ],
        "disposition": "distinct_composite_coalition_event",
        "relationship": "different_campaign_year_battle_and_coalition",
        "owner_scope": "separate Four Lakes coalition audit",
        "reason": (
            "Four Lakes on 1 September 1858 is a separate Wright campaign battle "
            "with multiple allied nations, irrespective of its Yakima War tag."
        ),
        "evidence_refs": [
            "wave8_yakima_historylink_four_lakes",
            "wave8_yakima_wa_parks_steptoe",
        ],
    },
    "hced-Spokane Plain1858-1": {
        "raw_row_sha256": WAVE8_YAKIMA_ADJACENT_ROW_HASHES[
            "hced-Spokane Plain1858-1"
        ],
        "disposition": "distinct_composite_coalition_event",
        "relationship": "different_campaign_year_battle_and_explicit_composite_label",
        "owner_scope": "separate Spokane Plains coalition audit",
        "reason": (
            "Spokane Plains on 5 September 1858 explicitly names a multi-nation "
            "opposing side and remains outside this exact-label ownership."
        ),
        "evidence_refs": [
            "wave8_yakima_historylink_four_lakes",
            "wave8_yakima_historylink_kamiakin",
            "wave8_yakima_wa_parks_steptoe",
        ],
    },
}
WAVE8_YAKIMA_RELATED_HCED_DISPOSITIONS = WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS


WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "yakima_war_composite_labels": {
        "disposition": "adjacent_war_family_without_candidate_overlap",
        "owned_candidate_ids": sorted(WAVE8_YAKIMA_RESERVED_IDS),
        "adjacent_candidate_ids": sorted(WAVE8_YAKIMA_ADJACENT_ROW_HASHES),
        "evidence_refs": [
            "wave8_yakima_historylink_cascades",
            "wave8_yakima_historylink_four_lakes",
            "wave8_yakima_wa_parks_steptoe",
        ],
        "reason": (
            "A shared Yakima War tag or Yakama participant does not make four "
            "composite-coalition rows exact-label property or event duplicates."
        ),
    },
    "modern_yakama_nation": {
        "disposition": "modern_and_treaty_identity_not_retroactive_rating_alias",
        "owned_candidate_ids": sorted(WAVE8_YAKIMA_RESERVED_IDS),
        "forbidden_generic_entity_ids": [
            "yakama",
            "yakama_nation",
            "yakima",
            "yakima_indians",
        ],
        "evidence_refs": [
            "wave8_yakima_historylink_kamiakin",
            "wave8_yakima_nara_bia_m5",
        ],
        "reason": (
            "The modern Nation and fourteen treaty tribes are not replaced by one "
            "timeless military identity; only attested event formations are rated."
        ),
    },
    "united_states_and_territorial_volunteers": {
        "disposition": "event_bounded_formations_not_generic_state_or_service",
        "owned_candidate_ids": sorted(WAVE8_YAKIMA_CONTRACT_IDS),
        "forbidden_generic_entity_ids": [
            "united_states",
            "us_antebellum",
            "us_army",
        ],
        "evidence_refs": [
            "wave8_yakima_carpenter_dissertation",
            "wave8_yakima_govinfo_indian_disturbances",
            "wave8_yakima_painter_journals",
        ],
        "reason": (
            "Haller's regular column and Rains's mixed regular-volunteer force are "
            "separate event formations; no service or state rating bridges them."
        ),
    },
}

WAVE8_YAKIMA_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_YAKIMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_YAKIMA_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"related_hced:{candidate_id}": disposition
        for candidate_id, disposition in (
            WAVE8_YAKIMA_RELATED_HCED_DISPOSITIONS.items()
        )
    },
    **{
        f"cross_lane:{name}": disposition
        for name, disposition in WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS.items()
    },
}


WAVE8_YAKIMA_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


def _duplicate_audit(year: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": tuple(sorted(set(map(normalize_label, aliases)))),
        "years": (year,),
    }


WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Toppenish1855-1": _duplicate_audit(
        1855,
        "Battle of Toppenish",
        "Battle of Toppenish Creek",
        "Battle of Toppenish Creek (Haller's Defeat)",
        "Haller's Defeat",
        "Toppenish",
        "Toppenish Creek",
    ),
    "hced-Union Gap1855-1": _duplicate_audit(
        1855,
        "Battle at Union Gap",
        "Battle of Two Buttes",
        "Battle of Union Gap",
        "Battle of Union Gap (Two Buttes)",
        "Pah-Qy-Ti-Koot",
        "Two Buttes",
        "Union Gap",
    ),
    "hced-Satus1856-1": _duplicate_audit(
        1856,
        "Battle of Satus",
        "Battle of Satus Creek",
        "Hembree Fight",
        "Satus",
        "Satus Creek",
    ),
    "hced-Grande Ronde Valley1856-1": _duplicate_audit(
        1856,
        "Battle of Grande Ronde",
        "Grande Ronde",
        "Grande Ronde Massacre",
        "Grande Ronde Valley",
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_hced_dispositions": WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS,
        "adjacent_row_hashes": WAVE8_YAKIMA_ADJACENT_ROW_HASHES,
        "contracts": WAVE8_YAKIMA_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_YAKIMA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_YAKIMA_ENTITIES,
        "exact_candidate_id_sha256": WAVE8_YAKIMA_EXACT_CANDIDATE_ID_SHA256,
        "funnel_event_candidate_id_sha256": (
            WAVE8_YAKIMA_FUNNEL_EVENT_CANDIDATE_ID_SHA256
        ),
        "existing_release_duplicate_dispositions": (
            WAVE8_YAKIMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS),
        "hced_queue_sha256": WAVE8_YAKIMA_HCED_QUEUE_SHA256,
        "holds": WAVE8_YAKIMA_HOLDS,
        "integration_dispositions": WAVE8_YAKIMA_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_YAKIMA_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_queue_sha256": WAVE8_YAKIMA_IWBD_QUEUE_SHA256,
        "iwbd_zero_overlap_audit": WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_YAKIMA_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_YAKIMA_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS
        ),
        "row_hashes": WAVE8_YAKIMA_ROW_HASHES,
        "sources": WAVE8_YAKIMA_SOURCES,
        "terminal_exclusions": WAVE8_YAKIMA_TERMINAL_EXCLUSIONS,
        "war_candidate_id_sha256": WAVE8_YAKIMA_WAR_CANDIDATE_ID_SHA256,
        "war_candidate_ids": sorted(WAVE8_YAKIMA_WAR_CANDIDATE_IDS),
    }


def wave8_yakima_audit_signature() -> str:
    """Return the digest of every fixture, disposition, and audit boundary."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_YAKIMA_FINAL_AUDIT_SIGNATURE = (
    "7243679f4fb93b33795179522d04a486541a5350f8fa8f487dc1d34ce5b976a3"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(map(str, values)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_YAKIMA_CONTRACTS),
        len(WAVE8_YAKIMA_HOLDS),
        len(WAVE8_YAKIMA_TERMINAL_EXCLUSIONS),
    ) != (2, 1, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_YAKIMA_ENTITIES), len(WAVE8_YAKIMA_SOURCES)) != (4, 16):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_YAKIMA_RESERVED_IDS != WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    if set(WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS) != set(
        WAVE8_YAKIMA_ADJACENT_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} adjacent inventory changed")
    if WAVE8_YAKIMA_WAR_CANDIDATE_IDS != (
        WAVE8_YAKIMA_RESERVED_IDS | set(WAVE8_YAKIMA_ADJACENT_ROW_HASHES)
    ):
        raise ValueError(f"{_LANE_NAME} Yakima War inventory changed")
    if WAVE8_YAKIMA_EXCLUSIONS is not WAVE8_YAKIMA_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion alias drifted")
    dispositions = (
        WAVE8_YAKIMA_CONTRACT_IDS,
        WAVE8_YAKIMA_HOLD_IDS,
        WAVE8_YAKIMA_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[index] & dispositions[other]
        for index in range(len(dispositions))
        for other in range(index + 1, len(dispositions))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if any(
        len(value) != 64
        for value in (
            WAVE8_YAKIMA_HCED_QUEUE_SHA256,
            WAVE8_YAKIMA_IWBD_QUEUE_SHA256,
            WAVE8_YAKIMA_EXACT_CANDIDATE_ID_SHA256,
            WAVE8_YAKIMA_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
            WAVE8_YAKIMA_WAR_CANDIDATE_ID_SHA256,
            *WAVE8_YAKIMA_ROW_HASHES.values(),
            *WAVE8_YAKIMA_ADJACENT_ROW_HASHES.values(),
        )
    ):
        raise ValueError(f"{_LANE_NAME} hash inventory changed")
    if (
        _sorted_newline_sha256(WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS)
        != WAVE8_YAKIMA_EXACT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} exact candidate digest changed")
    if (
        WAVE8_YAKIMA_FUNNEL_EVENT_CANDIDATE_ID_SHA256
        != WAVE8_YAKIMA_EXACT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} funnel candidate digest changed")
    if (
        _sorted_newline_sha256(WAVE8_YAKIMA_WAR_CANDIDATE_IDS)
        != WAVE8_YAKIMA_WAR_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} war-family candidate digest changed")
    if wave8_yakima_audit_signature() != WAVE8_YAKIMA_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_YAKIMA_SOURCES
    }
    if len(source_by_id) != len(WAVE8_YAKIMA_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(
        {str(source["source_family_id"]) for source in WAVE8_YAKIMA_SOURCES}
    ) != len(WAVE8_YAKIMA_SOURCES):
        raise ValueError(f"{_LANE_NAME} source-family independence changed")
    for source in WAVE8_YAKIMA_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_YAKIMA_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_YAKIMA_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "oregon volunteers",
        "palouse",
        "united states",
        "u s army",
        "yakama",
        "yakama nation",
        "yakima",
        "yakima indians",
    }
    used_sources: set[str] = set()
    used_entities: set[str] = set()
    for entity in WAVE8_YAKIMA_ENTITIES:
        if int(entity["start_year"]) != 1855 or int(entity["end_year"]) != 1855:
            raise ValueError(f"{_LANE_NAME} identity is not event-year bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic actor")
        note = str(entity["continuity_note"]).casefold()
        for phrase in (
            "no rating is inherited",
            "modern yakama nation",
            "united states",
            "noncombatants",
        ):
            if phrase not in note:
                raise ValueError(f"{_LANE_NAME} identity firewall changed")
        refs = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity source references changed")
        used_sources.update(refs)

    expected_contract_sides = {
        "hced-Toppenish1855-1": (
            [_TOPPENISH_INDIGENOUS_ID],
            [_TOPPENISH_US_ID],
        ),
        "hced-Union Gap1855-1": (
            [_UNION_GAP_US_ID],
            [_UNION_GAP_INDIGENOUS_ID],
        ),
    }
    for candidate_id, contract in WAVE8_YAKIMA_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_YAKIMA_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract row hash changed")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if (
            canonical["canonical_key"] != expected_key
            or canonical["year_low"] != 1855
            or canonical["year_high"] != 1855
            or not canonical["date_text"]
        ):
            raise ValueError(f"{_LANE_NAME} canonical event changed")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if (side_1, side_2) != expected_contract_sides[candidate_id]:
            raise ValueError(f"{_LANE_NAME} actor contract changed")
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} actor lists are not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} opposing sides changed")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} contract uses an unknown actor")
        used_entities.update(side_1)
        used_entities.update(side_2)
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["war_type"] != "colonial_anti_colonial"
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"] is not True
            or contract["duplicate_ownership"]
            != {
                "owner_module": _MODULE_OWNER,
                "status": "canonical_hced_owner",
            }
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence references changed")
        if (
            len(outcomes) < 3
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance changed")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} outcome uses a context-only source")
        expected_families = sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        )
        if families != expected_families or len(families) < 3:
            raise ValueError(f"{_LANE_NAME} outcome corroboration changed")
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} identities are not exactly consumed")

    forbidden_nonpromotion_keys = {
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
    }
    for candidate_id, item in WAVE8_YAKIMA_NONPROMOTIONS.items():
        if item["raw_row_sha256"] != WAVE8_YAKIMA_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} nonpromotion hash changed")
        if forbidden_nonpromotion_keys & set(item):
            raise ValueError(f"{_LANE_NAME} nonpromotion became rateable")
        if (
            item["reviewed_outcome"] not in {
                "unknown",
                "not_rateable_wrong_actor_massacre",
            }
            or item["unknown_is_never_draw"] is not True
            or "draw" not in str(item["hold_reason"]).casefold()
        ):
            raise ValueError(f"{_LANE_NAME} unknown/draw policy changed")
        evidence = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} nonpromotion evidence changed")
        used_sources.update(evidence)
    if (
        WAVE8_YAKIMA_HOLDS["hced-Satus1856-1"]["disposition"] != "hold"
        or WAVE8_YAKIMA_HOLDS["hced-Satus1856-1"]["terminal_exclusion"] is not False
    ):
        raise ValueError(f"{_LANE_NAME} Satus hold changed")
    exclusion = WAVE8_YAKIMA_TERMINAL_EXCLUSIONS[
        "hced-Grande Ronde Valley1856-1"
    ]
    if (
        exclusion["disposition"] != "terminal_exclusion"
        or exclusion["terminal_exclusion"] is not True
        or exclusion["historical_review"]["competitive_event"] is not False
    ):
        raise ValueError(f"{_LANE_NAME} Grande Ronde exclusion changed")

    if WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS != WAVE8_YAKIMA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_YAKIMA_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_YAKIMA_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_YAKIMA_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    for candidate_id, item in WAVE8_YAKIMA_LOCATION_QUARANTINE_REASONS.items():
        if (
            item["actions"] != ["withhold_point"]
            or item["retained_country"] != "United States"
            or candidate_id not in WAVE8_YAKIMA_CONTRACT_IDS
        ):
            raise ValueError(f"{_LANE_NAME} location disposition changed")
        refs = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence changed")
        used_sources.update(refs)

    for candidate_id, item in WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS.items():
        if item["raw_row_sha256"] != WAVE8_YAKIMA_ADJACENT_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} adjacent row hash changed")
        if item["disposition"] != "distinct_composite_coalition_event":
            raise ValueError(f"{_LANE_NAME} adjacent ownership changed")
        refs = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} adjacent evidence changed")
        used_sources.update(refs)

    if set(WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS) != {
        "modern_yakama_nation",
        "united_states_and_territorial_volunteers",
        "yakima_war_composite_labels",
    }:
        raise ValueError(f"{_LANE_NAME} cross-lane inventory changed")
    for item in WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS.values():
        if not set(item["owned_candidate_ids"]) <= WAVE8_YAKIMA_RESERVED_IDS:
            raise ValueError(f"{_LANE_NAME} cross-lane ownership changed")
        refs = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} cross-lane evidence changed")
        used_sources.update(refs)
    expected_integration = {
        **{
            f"related_hced:{key}": value
            for key, value in WAVE8_YAKIMA_RELATED_HCED_DISPOSITIONS.items()
        },
        **{
            f"cross_lane:{key}": value
            for key, value in WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS.items()
        },
    }
    if WAVE8_YAKIMA_INTEGRATION_DISPOSITIONS != expected_integration:
        raise ValueError(f"{_LANE_NAME} integration inventory changed")

    if used_sources != set(source_by_id):
        raise ValueError(
            f"{_LANE_NAME} source fixtures are not exactly consumed: "
            f"{sorted(set(source_by_id) - used_sources)}"
        )
    if (
        WAVE8_YAKIMA_OUTCOME_OVERRIDES
        or WAVE8_YAKIMA_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_YAKIMA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")
    if set(WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_YAKIMA_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for candidate_id, audit in WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT.items():
        aliases = list(map(str, audit["aliases"]))
        years = tuple(map(int, audit["years"]))
        if (
            not _is_sorted_unique(aliases)
            or any(alias != normalize_label(alias) for alias in aliases)
            or years != tuple(sorted(set(years)))
        ):
            raise ValueError(f"{_LANE_NAME} duplicate audit changed")
        item = (
            WAVE8_YAKIMA_CONTRACTS.get(candidate_id)
            or WAVE8_YAKIMA_NONPROMOTIONS[candidate_id]
        )
        if normalize_label(item["canonical_event"]["name"]) not in aliases:
            raise ValueError(f"{_LANE_NAME} canonical duplicate alias is missing")


def _is_exact_yakima_label(value: Any) -> bool:
    return normalize_label(value) == "yakima indians"


def _is_yakima_war_row(row: Mapping[str, Any]) -> bool:
    return any(
        normalize_label(value) in {"yakima war", "yakima indian wars"}
        for value in row.get("war_names", [])
    )


def validate_wave8_yakima_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all and only the four exact-label rows and fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_YAKIMA_CONTRACTS,
        WAVE8_YAKIMA_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_yakima_label(row.get("side_1_raw"))
        or _is_exact_yakima_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_YAKIMA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Yakima Indians inventory changed: "
            f"{sorted(exact_ids)}"
        )
    return {
        "holds": len(WAVE8_YAKIMA_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_YAKIMA_TERMINAL_EXCLUSIONS),
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
        text = str(row.get(field) or "")
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4])
    return None


def _audited_name_year_pairs() -> set[tuple[int, str]]:
    return {
        (int(year), normalize_label(alias))
        for audit in WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT.values()
        for year in audit["years"]
        for alias in audit["aliases"]
    }


def validate_wave8_yakima_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin war-family ownership and fail closed on unreviewed event twins."""

    validate_wave8_yakima_queue_contracts(hced_rows)
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, expected_hash in WAVE8_YAKIMA_ADJACENT_ROW_HASHES.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one adjacent HCED row {candidate_id}, "
                f"found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != expected_hash:
            raise ValueError(
                f"{_LANE_NAME} adjacent HCED fingerprint changed: {candidate_id}"
            )
    war_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_yakima_war_row(row)
    }
    if war_ids != WAVE8_YAKIMA_WAR_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} Yakima War inventory changed: {sorted(war_ids)}"
        )

    audited = _audited_name_year_pairs()
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_YAKIMA_RESERVED_IDS
        and (_row_year(row), normalize_label(row.get("name"))) in audited
    )
    if hced_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_matches}"
        )
    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name"))) in audited
    )
    if iwbd_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_matches}"
        )

    existing = list(existing_events)
    release_matches: list[str] = []
    for event in existing:
        if str(event.get("hced_candidate_id")) in WAVE8_YAKIMA_RESERVED_IDS:
            continue
        year = _row_year(event)
        names = {
            normalize_label(event.get("name")),
            *map(normalize_label, event.get("aliases", [])),
        }
        if year is not None and any((year, name) in audited for name in names):
            release_matches.append(str(event.get("id") or "<missing-id>"))
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): "
            f"{sorted(release_matches)}"
        )

    release_overlap = {
        str(event.get("hced_candidate_id"))
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_YAKIMA_CONTRACT_IDS
    }
    if release_overlap not in (set(), set(WAVE8_YAKIMA_CONTRACT_IDS)):
        raise ValueError(
            f"{_LANE_NAME} partial release overlap: {sorted(release_overlap)}"
        )
    return {
        "adjacent_hced_dispositions": len(
            WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": 0,
        "integration_dispositions": len(WAVE8_YAKIMA_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "release_overlap": len(release_overlap),
        "yakima_war_rows_audited": len(WAVE8_YAKIMA_WAR_CANDIDATE_IDS),
    }


def install_wave8_yakima_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_YAKIMA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_yakima_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_YAKIMA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_YAKIMA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_yakima_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_yakima_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_YAKIMA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_yakima_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_YAKIMA_CONTRACTS.values(),
                    *WAVE8_YAKIMA_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_yakima_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_hced_dispositions": len(
            WAVE8_YAKIMA_ADJACENT_HCED_DISPOSITIONS
        ),
        "country_quarantine_additions": len(
            WAVE8_YAKIMA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_YAKIMA_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": 0,
        "holds": len(WAVE8_YAKIMA_HOLDS),
        "integration_dispositions": len(WAVE8_YAKIMA_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_YAKIMA_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_YAKIMA_ENTITIES),
        "new_sources": len(WAVE8_YAKIMA_SOURCES),
        "newly_rated_events": len(WAVE8_YAKIMA_CONTRACTS),
        "outcome_overrides": len(WAVE8_YAKIMA_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_YAKIMA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_YAKIMA_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_YAKIMA_TERMINAL_EXCLUSIONS),
        "yakima_war_rows_audited": len(WAVE8_YAKIMA_WAR_CANDIDATE_IDS),
    }


def wave8_yakima_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    """Return immutable promoted-only location-quarantine additions."""

    _validate_static()
    return {
        "country": WAVE8_YAKIMA_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_YAKIMA_POINT_QUARANTINE_ADDITIONS,
    }
