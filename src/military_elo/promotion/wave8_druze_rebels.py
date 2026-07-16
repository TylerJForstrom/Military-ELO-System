"""Exact Wave 8 audit for HCED rows labelled ``Druze Rebels``.

The external label is never installed as an entity or alias.  Four rows bind to
documented, time-bounded Great Syrian Revolt field formations.  The year-only
Damascus 1926 row remains unrated because the locked source row cannot choose
between distinct February and May operations in the Maydan quarter.  Unknown
provenance is not converted into a draw or an invented engagement.
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
    "WAVE8_DRUZE_REBELS_CONTRACTS",
    "WAVE8_DRUZE_REBELS_CONTRACT_IDS",
    "WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS",
    "WAVE8_DRUZE_REBELS_ENTITIES",
    "WAVE8_DRUZE_REBELS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_DRUZE_REBELS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_DRUZE_REBELS_HOLDS",
    "WAVE8_DRUZE_REBELS_HOLD_IDS",
    "WAVE8_DRUZE_REBELS_INTEGRATION_DISPOSITIONS",
    "WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_DRUZE_REBELS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_DRUZE_REBELS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_DRUZE_REBELS_LOCATION_REVIEW",
    "WAVE8_DRUZE_REBELS_OUTCOME_OVERRIDES",
    "WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_DRUZE_REBELS_RESERVED_IDS",
    "WAVE8_DRUZE_REBELS_SOURCES",
    "install_wave8_druze_rebels_entities",
    "install_wave8_druze_rebels_sources",
    "promote_wave8_druze_rebels_contracts",
    "validate_wave8_druze_rebels_integration_dispositions",
    "validate_wave8_druze_rebels_queue_contracts",
    "wave8_druze_rebels_audit_signature",
    "wave8_druze_rebels_cohort_counts",
    "wave8_druze_rebels_counts",
    "wave8_druze_rebels_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Druze Rebels exact audit"
_EVENT_ID_PREFIX = "hced_wave8_druze_rebels_"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
    identity: bool = True,
    location: bool = False,
    ambiguity: bool = False,
    crosscheck: bool = False,
    government_work: bool = False,
) -> dict[str, Any]:
    roles: list[str] = []
    if ambiguity:
        roles.append("curated_reference_pending_claim_level_outcome_locator")
    if identity:
        roles.append("identity_boundary_or_context_reference")
    if location:
        roles.append("identity_boundary_or_context_reference")
    if outcome:
        roles.append("outcome")
    if crosscheck:
        roles.append("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "U.S. Government work" if government_work else "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(roles)),
    }


WAVE8_DRUZE_REBELS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_druze_rebels_provence_great_syrian_revolt",
        "The Great Syrian Revolt and the Rise of Arab Nationalism, pp. 59-64",
        "https://utpress.utexas.edu/9780292706804/",
        "University of Texas Press",
        "scholarly_monograph",
        "provence_great_syrian_revolt_2005",
        outcome=True,
        location=True,
        crosscheck=True,
    ),
    _source(
        "wave8_druze_rebels_neep_occupying_syria",
        "Occupying Syria Under the French Mandate, pp. 113-114",
        "https://books.google.com/books?id=1Z7TbtGaAX8C&pg=PA113",
        "Cambridge University Press",
        "scholarly_monograph",
        "neep_occupying_syria_2012",
        outcome=True,
        location=True,
        crosscheck=True,
    ),
    _source(
        "wave8_druze_rebels_firro_history_druzes",
        "A History of the Druzes, volume 1, p. 286",
        "https://books.google.com/books?id=usEUXYnYWxAC&pg=PA286",
        "Brill",
        "scholarly_monograph",
        "firro_history_druzes_1992",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_druze_rebels_khoury_syria_french_mandate",
        "Syria and the French Mandate, pp. 151, 189, 196",
        "https://books.google.com/books?id=tvP_AwAAQBAJ&pg=PA151",
        "Princeton University Press",
        "scholarly_monograph",
        "khoury_syria_french_mandate_1987",
        outcome=True,
        ambiguity=True,
        crosscheck=True,
    ),
    _source(
        "wave8_druze_rebels_betts_druze",
        "The Druze, Great Syrian Revolt account, pp. 87-88",
        "https://yalebooks.yale.edu/book/9780300048100/the-druze/",
        "Yale University Press",
        "scholarly_monograph",
        "betts_druze_yale",
        outcome=True,
        location=True,
        crosscheck=True,
    ),
    _source(
        "wave8_druze_rebels_bailony_transnational_rebellion",
        "Syria's Transnational Rebellion: Damascus and Rashaya chapters",
        "https://www.jstor.org/stable/10.3366/jj.25700607",
        "Edinburgh University Press / JSTOR",
        "scholarly_monograph",
        "bailony_transnational_rebellion_2025",
        outcome=True,
        location=True,
        crosscheck=True,
    ),
    _source(
        "wave8_druze_rebels_bailony_dissertation",
        "Transnationalism and the Syrian Migrant Politic, pp. 128, 142-145",
        "https://escholarship.org/uc/item/99q9f2k0",
        "UCLA Electronic Theses and Dissertations",
        "scholarly_dissertation_with_archival_sources",
        "bailony_ucla_dissertation",
        outcome=True,
        location=True,
        ambiguity=True,
        crosscheck=True,
    ),
    _source(
        "wave8_druze_rebels_wright_bombardment_damascus",
        "The Bombardment of Damascus",
        "https://doi.org/10.2307/2188917",
        "American Journal of International Law",
        "contemporary_scholarly_article_using_official_and_eyewitness_records",
        "wright_ajil_bombardment_1926",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_druze_rebels_ieg_damascus_atlas",
        "Damascus, 1925: The Bombing of the City",
        "https://hhr-atlas.ieg-mainz.de/articles/bogliolo-damascus",
        "Leibniz Institute of European History",
        "scholarly_research_atlas",
        "ieg_humanitarianism_atlas_damascus",
        outcome=True,
        location=True,
        crosscheck=True,
    ),
    _source(
        "wave8_druze_rebels_miller_syrian_revolt",
        "The Syrian Revolt of 1925",
        "https://doi.org/10.1017/S0020743800026118",
        "International Journal of Middle East Studies",
        "peer_reviewed_scholarly_article",
        "miller_ijmes_syrian_revolt_1977",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_druze_rebels_frus_1925_mazraa",
        "FRUS 1925, document 74: report on the battle of 3 August",
        "https://history.state.gov/historicaldocuments/frus1925v02/d74",
        "U.S. Department of State, Office of the Historian",
        "official_diplomatic_primary_record",
        "frus_1925_syrian_insurrection",
        outcome=True,
        crosscheck=True,
        government_work=True,
    ),
    _source(
        "wave8_druze_rebels_frus_1925_damascus",
        "FRUS 1925, document 78: revolutionists controlling Damascus",
        "https://history.state.gov/historicaldocuments/frus1925v02/d78",
        "U.S. Department of State, Office of the Historian",
        "official_diplomatic_primary_record",
        "frus_1925_syrian_insurrection",
        outcome=True,
        crosscheck=True,
        government_work=True,
    ),
    _source(
        "wave8_druze_rebels_frus_1925_rashaya",
        "FRUS 1925, document 110: relief of the Rashaya garrison",
        "https://history.state.gov/historicaldocuments/frus1925v02/d110",
        "U.S. Department of State, Office of the Historian",
        "official_diplomatic_primary_record",
        "frus_1925_syrian_insurrection",
        outcome=True,
        crosscheck=True,
        government_work=True,
    ),
    _source(
        "wave8_druze_rebels_frus_1926_february_maydan",
        "FRUS 1926, document 95: 17 February bombardment of the Meidan quarter",
        "https://history.state.gov/historicaldocuments/frus1926v02/d95",
        "U.S. Department of State, Office of the Historian",
        "official_diplomatic_primary_record",
        "frus_1926_syrian_insurrection",
        ambiguity=True,
        crosscheck=True,
        government_work=True,
    ),
    _source(
        "wave8_druze_rebels_kadhim_maydan_may_1926",
        "The Poetics of Anti-Colonialism: May 7, 1926 Maydan offensive",
        (
            "https://brill.com/display/book/9789047404408/"
            "9789047404408_webready_content_text.pdf"
        ),
        "Brill",
        "scholarly_monograph_chapter",
        "kadhim_poetics_anti_colonialism_2004",
        ambiguity=True,
        crosscheck=True,
    ),
    _source(
        "wave8_druze_rebels_foreign_legion_rachaya",
        "1925 Battle of Rachaya, including General Order no. 393",
        "https://foreignlegion.info/1925-battle-of-rachaya/",
        "French Foreign Legion Information historical archive",
        "specialist_unit_history_with_transcribed_primary_order",
        "foreign_legion_rachaya_archive",
        outcome=True,
        location=True,
        crosscheck=True,
    ),
)


_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_DRUZE_REBELS_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    continuity_note: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 1925,
        "end_year": 1925,
        "region": "Levant",
        "aliases": [],
        "predecessors": [],
        "continuity_note": continuity_note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_DRUZE_REBELS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "sultan_al_atrash_jabal_hawran_field_force_1925",
        "Sultan al-Atrash's Jabal Hawran field force (1925)",
        "campaign_bounded_anti_colonial_field_force",
        (
            "The armed field force assembled under Sultan al-Atrash for the opening "
            "Jabal Hawran campaign, including locally documented Druze and Bedouin "
            "fighters at al-Kafr and al-Mazraa. No rating is inherited by Druze "
            "people generally, another revolt formation, or any modern Syrian, "
            "Lebanese, Jordanian, or Israeli polity or community."
        ),
        [
            "wave8_druze_rebels_betts_druze",
            "wave8_druze_rebels_firro_history_druzes",
            "wave8_druze_rebels_neep_occupying_syria",
            "wave8_druze_rebels_provence_great_syrian_revolt",
        ],
    ),
    _entity(
        "normand_levant_column_al_kafr_1925",
        "Captain Normand's Army of the Levant column at al-Kafr (1925)",
        "engagement_bounded_colonial_column",
        (
            "The Algerian spahi, Syrian auxiliary, and Army of the Levant column "
            "commanded by Gabriel Normand at al-Kafr. No rating is inherited by "
            "the French Army as a whole, other colonial formations, or the modern "
            "French or Syrian state."
        ),
        [
            "wave8_druze_rebels_firro_history_druzes",
            "wave8_druze_rebels_neep_occupying_syria",
            "wave8_druze_rebels_provence_great_syrian_revolt",
        ],
    ),
    _entity(
        "michaud_levant_column_al_mazraa_1925",
        "General Michaud's Army of the Levant column at al-Mazraa (1925)",
        "engagement_bounded_colonial_column",
        (
            "The mixed French, colonial, and Syrian-auxiliary expedition commanded "
            "by General Roger Michaud at al-Mazraa. No rating is inherited by the "
            "French Army as a whole, its component peoples, or the modern French, "
            "Syrian, Senegalese, or Malagasy states."
        ),
        [
            "wave8_druze_rebels_betts_druze",
            "wave8_druze_rebels_frus_1925_mazraa",
            "wave8_druze_rebels_provence_great_syrian_revolt",
        ],
    ),
    _entity(
        "damascus_october_insurgent_force_1925",
        "Kharrat-Bakri Damascus insurgent force (October 1925)",
        "engagement_bounded_anti_colonial_urban_force",
        (
            "The armed Great Syrian Revolt bands led into Damascus by Hasan "
            "al-Kharrat and Nasib al-Bakri and joined by local insurgents during "
            "18-20 October. No rating is inherited by all Druze or Damascenes, "
            "another rebel band, or any modern Syrian polity or community."
        ),
        [
            "wave8_druze_rebels_bailony_transnational_rebellion",
            "wave8_druze_rebels_frus_1925_damascus",
            "wave8_druze_rebels_ieg_damascus_atlas",
            "wave8_druze_rebels_miller_syrian_revolt",
            "wave8_druze_rebels_wright_bombardment_damascus",
        ],
    ),
    _entity(
        "french_damascus_suppression_force_october_1925",
        "French Damascus suppression force (October 1925)",
        "engagement_bounded_colonial_garrison_and_fire_support",
        (
            "The Army of the Levant garrison, armor, artillery, and air elements "
            "used against the October Damascus incursion. Civilian victims are not "
            "participants. No rating is inherited by the French Army as a whole, "
            "another mandate formation, or the modern French or Syrian state."
        ),
        [
            "wave8_druze_rebels_bailony_transnational_rebellion",
            "wave8_druze_rebels_ieg_damascus_atlas",
            "wave8_druze_rebels_miller_syrian_revolt",
            "wave8_druze_rebels_wright_bombardment_damascus",
        ],
    ),
    _entity(
        "zayd_al_atrash_rashaya_besiegers_1925",
        "Zayd al-Atrash's Rashaya besieging force (1925)",
        "engagement_bounded_anti_colonial_siege_force",
        (
            "The armed force led from Syria into Wadi al-Taym by Zayd al-Atrash "
            "and committed against Rashaya citadel. No rating is inherited by "
            "Druze people generally, residents of Rashaya, other rebel bands, or "
            "any modern Syrian or Lebanese polity or community."
        ),
        [
            "wave8_druze_rebels_bailony_dissertation",
            "wave8_druze_rebels_bailony_transnational_rebellion",
            "wave8_druze_rebels_foreign_legion_rachaya",
        ],
    ),
    _entity(
        "rashaya_citadel_garrison_1925",
        "Rashaya citadel garrison and relief force (1925)",
        "engagement_bounded_colonial_garrison_and_relief_force",
        (
            "The Foreign Legion cavalry, Tunisian spahis, Lebanese gendarmes, and "
            "relief columns documented in the defense of Rashaya citadel. No "
            "rating is inherited by those component peoples, the French Army as a "
            "whole, or any modern French, Tunisian, Algerian, Lebanese, or Syrian state."
        ),
        [
            "wave8_druze_rebels_bailony_dissertation",
            "wave8_druze_rebels_foreign_legion_rachaya",
            "wave8_druze_rebels_frus_1925_rashaya",
        ],
    ),
)


_ROW_HASHES: dict[str, str] = {
    "hced-Damascus1925-1": "9afb944a7ee792d338ee88ba2c6517c18b97d388883b449141151af2933bec9a",
    "hced-Damascus1926-1": "5179f9de19d332ea46f4e71491552399d2f2e3bf738b87d9d15b436651111ade",
    "hced-Kafr1925-1": "0d4a287bf094009135134de8b33ef5ac3b169753a702901513fd264094280de9",
    "hced-Mazraa1925-1": "c6d519818d4c9523fbe79244b6c377d62eb2e1c33510a6940058d20af496caf9",
    "hced-Rashaya1925-1": "6518aa1e9ce37d3c1777ac70bc04bcabf6ed5f00ef8cb11411a5c8a552901350",
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str,
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "name": name,
        "year_low": year,
        "year_high": year,
        "date_text": date_text,
        "date_precision": date_precision,
        "granularity": granularity,
        "canonical_key": f"{_slug(name)}:{year}:{year}",
    }


def _families(source_ids: Iterable[str]) -> list[str]:
    return sorted(
        {
            str(_SOURCE_BY_ID[source_id]["source_family_id"])
            for source_id in source_ids
        }
    )


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
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "winner_side": 1,
        "result_type": "win",
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": _families(outcomes),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "bounded_exact_opposing_forces",
        "audit_note": audit_note,
    }


WAVE8_DRUZE_REBELS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Kafr1925-1": _contract(
        "hced-Kafr1925-1",
        _canonical(
            "Battle of al-Kafr",
            1925,
            "22 July 1925",
            date_precision="day",
        ),
        "jabal_hawran_opening_1925",
        ["sultan_al_atrash_jabal_hawran_field_force_1925"],
        ["normand_levant_column_al_kafr_1925"],
        [
            "wave8_druze_rebels_firro_history_druzes",
            "wave8_druze_rebels_khoury_syria_french_mandate",
            "wave8_druze_rebels_neep_occupying_syria",
            "wave8_druze_rebels_provence_great_syrian_revolt",
        ],
        [
            "wave8_druze_rebels_firro_history_druzes",
            "wave8_druze_rebels_neep_occupying_syria",
            "wave8_druze_rebels_provence_great_syrian_revolt",
        ],
        (
            "Sultan al-Atrash's field force routed Captain Normand's 166-man "
            "Army of the Levant column at its al-Kafr encampment on 22 July. "
            "The external ethnic label is replaced by the specific campaign force."
        ),
        confidence=0.96,
    ),
    "hced-Mazraa1925-1": _contract(
        "hced-Mazraa1925-1",
        _canonical(
            "Battle of al-Mazraa",
            1925,
            "2-3 August 1925",
            date_precision="day_range",
        ),
        "jabal_hawran_opening_1925",
        ["sultan_al_atrash_jabal_hawran_field_force_1925"],
        ["michaud_levant_column_al_mazraa_1925"],
        [
            "wave8_druze_rebels_betts_druze",
            "wave8_druze_rebels_frus_1925_mazraa",
            "wave8_druze_rebels_provence_great_syrian_revolt",
        ],
        [
            "wave8_druze_rebels_betts_druze",
            "wave8_druze_rebels_frus_1925_mazraa",
            "wave8_druze_rebels_provence_great_syrian_revolt",
        ],
        (
            "The al-Atrash field force defeated and routed General Michaud's "
            "mixed Army of the Levant expedition on 2-3 August. HCED's Lebanon "
            "country value is wrong for the Jabal al-Druze battlefield and is withheld."
        ),
        confidence=0.96,
    ),
    "hced-Damascus1925-1": _contract(
        "hced-Damascus1925-1",
        _canonical(
            "Battle and bombardment of Damascus",
            1925,
            "18-20 October 1925",
            date_precision="day_range",
        ),
        "damascus_october_offensive_1925",
        ["french_damascus_suppression_force_october_1925"],
        ["damascus_october_insurgent_force_1925"],
        [
            "wave8_druze_rebels_bailony_transnational_rebellion",
            "wave8_druze_rebels_frus_1925_damascus",
            "wave8_druze_rebels_ieg_damascus_atlas",
            "wave8_druze_rebels_miller_syrian_revolt",
            "wave8_druze_rebels_wright_bombardment_damascus",
        ],
        [
            "wave8_druze_rebels_bailony_transnational_rebellion",
            "wave8_druze_rebels_frus_1925_damascus",
            "wave8_druze_rebels_ieg_damascus_atlas",
            "wave8_druze_rebels_miller_syrian_revolt",
        ],
        (
            "Kharrat-Bakri insurgents captured much of Damascus before French "
            "armor, artillery, and aircraft forced their withdrawal and restored "
            "mandatory control. The armed contest and suppression are one composite "
            "engagement; civilian deaths and the bombardment are not scored as a "
            "second victory or as participants."
        ),
        confidence=0.89,
    ),
    "hced-Rashaya1925-1": _contract(
        "hced-Rashaya1925-1",
        _canonical(
            "Siege of Rashaya Citadel",
            1925,
            "21-24 November 1925",
            date_precision="day_range",
        ),
        "rashaya_anti_lebanon_campaign_1925",
        ["rashaya_citadel_garrison_1925"],
        ["zayd_al_atrash_rashaya_besiegers_1925"],
        [
            "wave8_druze_rebels_bailony_dissertation",
            "wave8_druze_rebels_bailony_transnational_rebellion",
            "wave8_druze_rebels_foreign_legion_rachaya",
            "wave8_druze_rebels_frus_1925_rashaya",
        ],
        [
            "wave8_druze_rebels_bailony_dissertation",
            "wave8_druze_rebels_foreign_legion_rachaya",
            "wave8_druze_rebels_frus_1925_rashaya",
        ],
        (
            "Zayd al-Atrash's force assaulted and besieged the citadel from 21 "
            "through 24 November; the garrison held until French relief columns "
            "arrived and the besiegers withdrew. Destruction and reprisals around "
            "Rashaya are not emitted as additional tactical outcomes."
        ),
        confidence=0.95,
    ),
}


WAVE8_DRUZE_REBELS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Damascus1926-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Damascus1926-1"],
        "canonical_event": _canonical(
            "Ambiguous Damascus operations of 1926",
            1926,
            "17 February and 7 May 1926 are distinct documented operations",
            date_precision="year",
            granularity="ambiguous_multi_event_aggregate",
        ),
        "cohort": "damascus_1926_unresolved_source_aggregate",
        "hold_category": "multiple_distinct_same_city_operations_in_source_year",
        "evidence_refs": [
            "wave8_druze_rebels_bailony_dissertation",
            "wave8_druze_rebels_frus_1926_february_maydan",
            "wave8_druze_rebels_kadhim_maydan_may_1926",
            "wave8_druze_rebels_khoury_syria_french_mandate",
        ],
        "hold_reason": (
            "At least two distinct French operations struck Damascus's Maydan "
            "quarter in 1926: a 17 February bombardment and the 7 May offensive. "
            "The year-only HCED row has no consulted-source lineage or date that "
            "can select one of them, and its generic Druze opponent is not a "
            "defensible formation for both. The row cannot produce an Elo until "
            "that linkage is resolved; unknown is never converted into a draw."
        ),
    }
}


WAVE8_DRUZE_REBELS_CONTRACT_IDS = frozenset(WAVE8_DRUZE_REBELS_CONTRACTS)
WAVE8_DRUZE_REBELS_HOLD_IDS = frozenset(WAVE8_DRUZE_REBELS_HOLDS)
WAVE8_DRUZE_REBELS_RESERVED_IDS = (
    WAVE8_DRUZE_REBELS_CONTRACT_IDS | WAVE8_DRUZE_REBELS_HOLD_IDS
)
WAVE8_DRUZE_REBELS_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


WAVE8_DRUZE_REBELS_LOCATION_REVIEW: dict[str, dict[str, Any]] = {
    "hced-Damascus1925-1": {
        "point_disposition": "quarantine",
        "country_disposition": "retain",
        "reason": (
            "The automated Damascus centroid is not a sourced battlefield point "
            "for the fighting across Shaghour, Maydan, and the old city."
        ),
        "evidence_refs": [
            "wave8_druze_rebels_bailony_transnational_rebellion",
            "wave8_druze_rebels_ieg_damascus_atlas",
        ],
    },
    "hced-Kafr1925-1": {
        "point_disposition": "quarantine",
        "country_disposition": "retain",
        "reason": (
            "HCED's coordinate lies far north of the documented al-Kafr battlefield "
            "in Jabal al-Druze and cannot be retained."
        ),
        "evidence_refs": [
            "wave8_druze_rebels_neep_occupying_syria",
            "wave8_druze_rebels_provence_great_syrian_revolt",
        ],
    },
    "hced-Mazraa1925-1": {
        "point_disposition": "quarantine",
        "country_disposition": "quarantine",
        "reason": (
            "The sources locate al-Mazraa in Jabal al-Druze near al-Suwayda, Syria, "
            "while HCED assigns modern country Lebanon; neither that country field "
            "nor the unsourced settlement coordinate is released."
        ),
        "evidence_refs": [
            "wave8_druze_rebels_betts_druze",
            "wave8_druze_rebels_provence_great_syrian_revolt",
        ],
    },
    "hced-Rashaya1925-1": {
        "point_disposition": "quarantine",
        "country_disposition": "retain",
        "reason": (
            "The sources establish Rashaya citadel in modern Lebanon but do not "
            "authenticate HCED's automated coordinate as a reviewed combat point."
        ),
        "evidence_refs": [
            "wave8_druze_rebels_bailony_dissertation",
            "wave8_druze_rebels_foreign_legion_rachaya",
        ],
    },
}

WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS = frozenset(
    candidate_id
    for candidate_id, review in WAVE8_DRUZE_REBELS_LOCATION_REVIEW.items()
    if review["point_disposition"] == "quarantine"
)
WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    candidate_id
    for candidate_id, review in WAVE8_DRUZE_REBELS_LOCATION_REVIEW.items()
    if review["country_disposition"] == "quarantine"
)
WAVE8_DRUZE_REBELS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
}


# The locked IWBD queue has Damascus only in 1918 and no 1925/1926 twin for
# any owned row.  Existing release events likewise contain no same-year twin.
WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_DRUZE_REBELS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
    **WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS,
}

WAVE8_DRUZE_REBELS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Damascus1925-1": {
        "aliases": ["battle and bombardment of damascus", "battle of damascus", "damascus"],
        "years": [1925, 1925],
    },
    "hced-Damascus1926-1": {
        "aliases": ["damascus", "maydan", "meidan"],
        "years": [1926, 1926],
    },
    "hced-Kafr1925-1": {
        "aliases": ["al kafr", "battle of al kafr", "kafr"],
        "years": [1925, 1925],
    },
    "hced-Mazraa1925-1": {
        "aliases": ["al mazraa", "battle of al mazraa", "mazraa"],
        "years": [1925, 1925],
    },
    "hced-Rashaya1925-1": {
        "aliases": ["battle of rachaya", "battle of rashaya", "rachaya", "rashaya", "siege of rashaya citadel"],
        "years": [1925, 1925],
    },
}


# Every promoted result preserves HCED's winner/loser ordering.  The lane only
# replaces generic actors and rejects the ambiguous 1926 aggregate.
WAVE8_DRUZE_REBELS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_DRUZE_REBELS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_duplicate_dispositions": (
            WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS
        ),
        "entities": WAVE8_DRUZE_REBELS_ENTITIES,
        "holds": WAVE8_DRUZE_REBELS_HOLDS,
        "iwbd_duplicate_dispositions": WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_DRUZE_REBELS_IWBD_ZERO_OVERLAP_AUDIT,
        "location_review": WAVE8_DRUZE_REBELS_LOCATION_REVIEW,
        "outcome_overrides": WAVE8_DRUZE_REBELS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_DRUZE_REBELS_SOURCES,
    }


def wave8_druze_rebels_audit_signature() -> str:
    """Return the SHA-256 pin over the complete lane adjudication."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_DRUZE_REBELS_FINAL_AUDIT_SIGNATURE = (
    "67b6d387a260c70df37a62af71aa482018e1b907760a68ef5f10957a7217136f"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_DRUZE_REBELS_CONTRACTS), len(WAVE8_DRUZE_REBELS_HOLDS)) != (4, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_DRUZE_REBELS_ENTITIES), len(WAVE8_DRUZE_REBELS_SOURCES)) != (7, 16):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_DRUZE_REBELS_RESERVED_IDS != WAVE8_DRUZE_REBELS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_DRUZE_REBELS_CONTRACT_IDS & WAVE8_DRUZE_REBELS_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotions and holds overlap")
    if wave8_druze_rebels_audit_signature() != WAVE8_DRUZE_REBELS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_DRUZE_REBELS_SOURCES
    }
    if len(source_by_id) != len(WAVE8_DRUZE_REBELS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_DRUZE_REBELS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not source["source_family_id"]:
            raise ValueError(f"{_LANE_NAME} source family is blank")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_DRUZE_REBELS_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_DRUZE_REBELS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_identity_labels = {
        "druze",
        "druze rebels",
        "druze people",
        "syrian rebels",
    }
    for entity in WAVE8_DRUZE_REBELS_ENTITIES:
        if (entity["start_year"], entity["end_year"]) != (1925, 1925):
            raise ValueError(f"{_LANE_NAME} installed an unbounded formation")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} opened a generic identity fallback")
        if normalize_label(entity["name"]) in forbidden_identity_labels:
            raise ValueError(f"{_LANE_NAME} installed a timeless ethnic identity")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern" not in note:
            raise ValueError(f"{_LANE_NAME} entity permits rating inheritance")
        entity_sources = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(entity_sources) or not set(entity_sources) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity provenance drifted")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    expected_precisions = {
        "hced-Damascus1925-1": "day_range",
        "hced-Kafr1925-1": "day",
        "hced-Mazraa1925-1": "day_range",
        "hced-Rashaya1925-1": "day_range",
    }
    for candidate_id, contract in WAVE8_DRUZE_REBELS_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} canonical key drifted")
        if canonical["granularity"] != "engagement":
            raise ValueError(f"{_LANE_NAME} promoted a non-engagement")
        if canonical["date_precision"] != expected_precisions[candidate_id]:
            raise ValueError(f"{_LANE_NAME} date precision drifted")

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory drifted")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unknown entity")
        used_entities.update(side_1)
        used_entities.update(side_2)
        if any(normalize_label(item) in forbidden_identity_labels for item in (*side_1, *side_2)):
            raise ValueError(f"{_LANE_NAME} rates a generic ethnic label")

        if contract["result_type"] != "win" or contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} invented a draw or unknown result")
        if contract["war_type"] != "colonial_anti_colonial":
            raise ValueError(f"{_LANE_NAME} war type drifted")
        if contract["actor_override"] != "bounded_exact_opposing_forces":
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} contains an outcome override")

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if not outcomes or not _is_sorted_unique(outcomes) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} direct outcome evidence drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        if families != _families(outcomes) or not _is_sorted_unique(families):
            raise ValueError(f"{_LANE_NAME} outcome-family provenance drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")

    forbidden_hold_keys = {
        "losers",
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
        "winners",
    }
    for candidate_id, hold in WAVE8_DRUZE_REBELS_HOLDS.items():
        if hold["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} hold hash drifted")
        if forbidden_hold_keys & set(hold):
            raise ValueError(f"{_LANE_NAME} hold contains a rateable result")
        if hold["canonical_event"]["granularity"] != "ambiguous_multi_event_aggregate":
            raise ValueError(f"{_LANE_NAME} hold granularity drifted")
        reason = str(hold["hold_reason"]).casefold()
        for phrase in ("at least two", "cannot produce an elo", "unknown", "draw"):
            if phrase not in reason:
                raise ValueError(f"{_LANE_NAME} hold rationale is incomplete")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence drifted")
        if any(
            "curated_reference_pending_claim_level_outcome_locator"
            not in source_by_id[item]["evidence_roles"]
            for item in evidence
        ):
            raise ValueError(f"{_LANE_NAME} hold lacks ambiguity evidence")
        used_sources.update(evidence)

    if set(WAVE8_DRUZE_REBELS_LOCATION_REVIEW) != WAVE8_DRUZE_REBELS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location audit inventory changed")
    if WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS != WAVE8_DRUZE_REBELS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS != {"hced-Mazraa1925-1"}:
        raise ValueError(f"{_LANE_NAME} country quarantine inventory changed")
    if WAVE8_DRUZE_REBELS_HOLD_IDS & (
        WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS
        | WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} quarantined a non-emitted hold")
    for review in WAVE8_DRUZE_REBELS_LOCATION_REVIEW.values():
        refs = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location provenance drifted")
        if any(
            "identity_boundary_or_context_reference"
            not in source_by_id[item]["evidence_roles"]
            for item in refs
        ):
            raise ValueError(f"{_LANE_NAME} location source lacks a location role")
        used_sources.update(refs)

    for entity in WAVE8_DRUZE_REBELS_ENTITIES:
        used_sources.update(map(str, entity["source_ids"]))
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source inventory is not exactly consumed")

    if WAVE8_DRUZE_REBELS_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} outcome override inventory changed")
    if WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    if WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} cross-lane duplicate inventory changed")
    if WAVE8_DRUZE_REBELS_INTEGRATION_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} integration disposition inventory changed")
    if set(WAVE8_DRUZE_REBELS_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_DRUZE_REBELS_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} zero-overlap audit inventory changed")


def validate_wave8_druze_rebels_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_DRUZE_REBELS_CONTRACTS,
        WAVE8_DRUZE_REBELS_HOLDS,
        lane_name=_LANE_NAME,
    )


def _row_year(row: Mapping[str, Any]) -> int | None:
    if row.get("year") is not None:
        return int(row["year"])
    value = str(row.get("start_date") or "")
    if len(value) >= 4 and value[:4].isdigit():
        return int(value[:4])
    return None


def validate_wave8_druze_rebels_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed if a new plausible IWBD or release twin appears."""

    validate_wave8_druze_rebels_queue_contracts(hced_rows)
    audits = [
        (
            candidate_id,
            {normalize_label(alias) for alias in item["aliases"]},
            tuple(map(int, item["years"])),
        )
        for candidate_id, item in WAVE8_DRUZE_REBELS_IWBD_ZERO_OVERLAP_AUDIT.items()
    ]

    iwbd_matches: list[str] = []
    for row in iwbd_rows:
        year = _row_year(row)
        if year is None:
            continue
        name = normalize_label(row.get("name"))
        for candidate_id, aliases, (low, high) in audits:
            if low <= year <= high and name in aliases:
                iwbd_matches.append(
                    f"{row.get('candidate_id') or row.get('source_row') or 'unknown'}->{candidate_id}"
                )
    if iwbd_matches:
        raise ValueError(
            f"{_LANE_NAME} found unadjudicated IWBD duplicate candidates: "
            f"{sorted(iwbd_matches)}"
        )

    release_matches: list[str] = []
    for event in existing_events:
        if event.get("hced_candidate_id") in WAVE8_DRUZE_REBELS_CONTRACT_IDS:
            continue
        year = _row_year(event)
        if year is None:
            continue
        names = {
            normalize_label(event.get("name")),
            *(
                normalize_label(alias)
                for alias in event.get("aliases", [])
                if isinstance(alias, str)
            ),
        }
        for candidate_id, aliases, (low, high) in audits:
            if low <= year <= high and names & aliases:
                release_matches.append(
                    f"{event.get('id') or 'unknown'}->{candidate_id}"
                )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} found unadjudicated release duplicates: "
            f"{sorted(release_matches)}"
        )

    return {
        "cross_lane_duplicate_dispositions": len(
            WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(WAVE8_DRUZE_REBELS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_DRUZE_REBELS_IWBD_ZERO_OVERLAP_AUDIT
        ),
    }


def install_wave8_druze_rebels_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_DRUZE_REBELS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_druze_rebels_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_DRUZE_REBELS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_druze_rebels_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_druze_rebels_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_DRUZE_REBELS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_druze_rebels_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_DRUZE_REBELS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_druze_rebels_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_duplicate_dispositions": len(
            WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_DRUZE_REBELS_HOLDS),
        "integration_dispositions": len(WAVE8_DRUZE_REBELS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_DRUZE_REBELS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_DRUZE_REBELS_ENTITIES),
        "new_sources": len(WAVE8_DRUZE_REBELS_SOURCES),
        "newly_rated_events": len(WAVE8_DRUZE_REBELS_CONTRACTS),
        "outcome_overrides": len(WAVE8_DRUZE_REBELS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_DRUZE_REBELS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_DRUZE_REBELS_RESERVED_IDS),
    }


def wave8_druze_rebels_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for shared location-manifest integration."""

    _validate_static()
    return {
        "country": WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS,
    }
