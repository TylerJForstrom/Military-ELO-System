"""Candidate-keyed Wave 8 audit for HCED's exact ``Kingdom of Kandy`` label.

Seven queue rows use the literal label.  Two seventeenth-century battles are
already owned by Wave 6 and Balane 1594 is already excluded there because its
name and date conflate Danture (1594) with Balana (1602).  Of the four current
funnel rows, two 1803 military outcomes are independently attested and promote:
the British repulse of the royal army at Hanwella and the Kandyan defeat of
Major Davie's garrison at Kandy.  Both use event-bounded opposing formations.

Kandy 1815 is not converted into a battle: the annexation followed political
manoeuvring and an unopposed occupation formalized by the Kandyan Convention.
Kandy 1818 is also excluded: it is an unbounded rebellion aggregate after the
kingdom's sovereignty had already been transferred, and its belligerent cannot
be called the Kingdom of Kandy.  Unknown is never a draw, no generic Kandy or
British alias is opened, and no rating crosses the 1815 sovereignty boundary.
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
    "WAVE8_KINGDOM_KANDY_ADJACENT_LANE_DISPOSITIONS",
    "WAVE8_KINGDOM_KANDY_CONTRACT_IDS",
    "WAVE8_KINGDOM_KANDY_CONTRACTS",
    "WAVE8_KINGDOM_KANDY_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_KINGDOM_KANDY_CROSS_LANE_DISPOSITIONS",
    "WAVE8_KINGDOM_KANDY_ENTITIES",
    "WAVE8_KINGDOM_KANDY_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_KINGDOM_KANDY_EXCLUSION_IDS",
    "WAVE8_KINGDOM_KANDY_EXCLUSIONS",
    "WAVE8_KINGDOM_KANDY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_KINGDOM_KANDY_EXPECTED_CANDIDATE_IDS",
    "WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS",
    "WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS",
    "WAVE8_KINGDOM_KANDY_FINAL_AUDIT_SIGNATURE",
    "WAVE8_KINGDOM_KANDY_FUNNEL_EVENT_CANDIDATE_ID_SHA256",
    "WAVE8_KINGDOM_KANDY_HCED_QUEUE_SHA256",
    "WAVE8_KINGDOM_KANDY_HOLD_IDS",
    "WAVE8_KINGDOM_KANDY_HOLDS",
    "WAVE8_KINGDOM_KANDY_INTEGRATION_DISPOSITIONS",
    "WAVE8_KINGDOM_KANDY_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_KINGDOM_KANDY_IWBD_QUEUE_SHA256",
    "WAVE8_KINGDOM_KANDY_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_KINGDOM_KANDY_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_KINGDOM_KANDY_LOCATION_QUARANTINE_REASONS",
    "WAVE8_KINGDOM_KANDY_NONPROMOTIONS",
    "WAVE8_KINGDOM_KANDY_OUTCOME_OVERRIDES",
    "WAVE8_KINGDOM_KANDY_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS",
    "WAVE8_KINGDOM_KANDY_RESERVED_IDS",
    "WAVE8_KINGDOM_KANDY_ROW_HASHES",
    "WAVE8_KINGDOM_KANDY_SOURCES",
    "WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS",
    "WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS",
    "install_wave8_kingdom_kandy_entities",
    "install_wave8_kingdom_kandy_sources",
    "promote_wave8_kingdom_kandy_contracts",
    "validate_wave8_kingdom_kandy_integration_dispositions",
    "validate_wave8_kingdom_kandy_queue_contracts",
    "wave8_kingdom_kandy_audit_signature",
    "wave8_kingdom_kandy_cohort_counts",
    "wave8_kingdom_kandy_counts",
    "wave8_kingdom_kandy_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Kingdom of Kandy actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_kingdom_kandy"
_EVENT_ID_PREFIX = "hced_wave8_kingdom_kandy_"

_HANWELLA_BRITISH_ID = "british_ceylon_hanwella_defense_force_1803"
_HANWELLA_KANDYAN_ID = "sri_vikrama_kandyan_hanwella_field_force_1803"
_KANDY_KANDYAN_ID = "sri_vikrama_kandyan_kandy_counterattack_force_1803"
_KANDY_BRITISH_ID = "davie_british_ceylon_garrison_kandy_1803"

_BALANE_ID = "hced-Balane1594-1"
_GANNORUWA_ID = "hced-Gannoruwa1638-1"
_RADENIVELA_ID = "hced-Radenivela1630-1"
_TRINCOMALEE_ID = "hced-Trincomalee1639-1"


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


WAVE8_KINGDOM_KANDY_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_kingdom_kandy_powell_wars",
        "The Kandyan Wars: The British Army in Ceylon, 1803-1818",
        "https://books.google.lk/books?id=FRNAAAAAIAAJ",
        "Leo Cooper / Navrang; Google Books",
        "scholarly_military_history_monograph",
        "powell_kandyan_wars_1973",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kingdom_kandy_cordiner_description",
        (
            "A Description of Ceylon, Volume 2: the Campaign in Candy in "
            "1803"
        ),
        "https://books.google.com/books?id=9M1CAAAAcAAJ",
        "Longman; Google Books",
        "near_contemporary_campaign_history",
        "cordiner_description_ceylon_1807",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kingdom_kandy_codrington_short_history",
        "A Short History of Ceylon",
        "https://noolaham.net/project/46/4531/4531.html",
        "Macmillan and Co.; Noolaham Foundation digitization",
        "scholarly_national_history",
        "codrington_short_history_ceylon_1926",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kingdom_kandy_jaques_dictionary",
        "Dictionary of Battles and Sieges",
        "https://books.google.com/books?id=w_XCEAAAQBAJ",
        "Greenwood / Bloomsbury Academic; Google Books",
        "expert_reviewed_military_reference",
        "jaques_dictionary_battles_2006",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kingdom_kandy_herath_massacre",
        "The British Army Massacre at Kandy in 1803?",
        "https://doi.org/10.4038/jdrra.v2i2.38",
        "Journal of Desk Research Review and Analysis, University of Kelaniya",
        "peer_reviewed_historical_article",
        "herath_kandy_1803_massacre_2024",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kingdom_kandy_sivasundaram_land",
        (
            "Tales of the Land: British Geography and Kandyan Resistance "
            "in Sri Lanka, c. 1803-1850"
        ),
        (
            "https://eprints.lse.ac.uk/21723/1/"
            "Tales_of_the_land-British_geography_and_Kandyan_resistance_"
            "in_Sri_Lanka__c_1803-1850.pdf"
        ),
        "Cambridge University Press, Modern Asian Studies",
        "peer_reviewed_historical_article",
        "sivasundaram_tales_land_2007",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kingdom_kandy_johnston_narrative",
        (
            "Narrative of the Operations of a Detachment in an Expedition "
            "to Candy in 1804, with Observations on the Previous Campaign"
        ),
        "https://www.gutenberg.org/ebooks/44408",
        "Project Gutenberg transcription of Arthur Johnston's account",
        "participant_primary_military_narrative",
        "johnston_candy_expedition_narrative_1810",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_kingdom_kandy_national_archives_1815",
        "Kandyan Convention, 1815",
        (
            "https://archives.gov.lk/English/online-exhibits/"
            "path-to-freedom/1-1815-convention"
        ),
        "Department of National Archives, Sri Lanka",
        "official_archival_exhibit_and_treaty_record",
        "slna_kandyan_convention_lk_na_6_12345",
    ),
    _source(
        "wave8_kingdom_kandy_national_archives_1818",
        "Freedom Struggle, 1818",
        (
            "https://archives.gov.lk/online-exhibits/"
            "path-to-freedom/freedom-struggle"
        ),
        "Department of National Archives, Sri Lanka",
        "official_archival_exhibit_and_colonial_records",
        "slna_freedom_struggle_lk_na_5_10",
    ),
    _source(
        "wave8_kingdom_kandy_sumana_1818",
        "A Source Related Study on the Preliminary Plan of the Upcountry Rebellion in 1818",
        "https://doi.org/10.4038/p.v14i2.48",
        "Pravacana, Bhiksu University of Sri Lanka",
        "peer_reviewed_historical_article",
        "sumana_upcountry_rebellion_2023",
    ),
    _source(
        "wave8_kingdom_kandy_kodikara_administration",
        (
            "British Administration in the Kandyan Provinces of Sri Lanka, "
            "1815-1833, with Special Reference to Social Change"
        ),
        (
            "https://soas-repository.worktribe.com/output/388221/"
            "british-administration-in-the-kandyan-provinces-of-sri-lanka-"
            "1815-1833-with-special-reference-to-social-change"
        ),
        "SOAS University of London",
        "doctoral_historical_thesis",
        "kodikara_kandyan_administration_1983",
    ),
    _source(
        "wave8_kingdom_kandy_official_chronology",
        "Sri Lankan history textbook chronology",
        "https://govdoc.lk/downloadFile/6943",
        "Department of Education, Sri Lanka",
        "official_education_history_reference",
        "sri_lanka_education_kandyan_chronology",
    ),
    _source(
        "wave8_kingdom_kandy_nova_ceylon",
        "Ceylon",
        "https://eve.fcsh.unl.pt/en/places/ceylon",
        "Encyclopaedia of Portuguese Expansion, NOVA FCSH",
        "academic_encyclopedia_entry",
        "nova_portuguese_expansion_ceylon",
    ),
)


_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_KINGDOM_KANDY_SOURCES
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
    note: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 1803,
        "end_year": 1803,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            note
            + " No rating is inherited by the Kingdom of Kandy as a timeless "
            "label, British Ceylon, the United Kingdom, post-1815 Kandyan "
            "rebels, a successor state, or a modern country."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_KINGDOM_KANDY_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _HANWELLA_BRITISH_ID,
        "British Ceylon garrison and relief force at Hanwella (1803)",
        "event_bounded_colonial_garrison_and_relief_force",
        "Hanwella, British Ceylon",
        (
            "Bounded to the troops that defended and relieved Hanwella during "
            "the September 1803 action."
        ),
        [
            "wave8_kingdom_kandy_codrington_short_history",
            "wave8_kingdom_kandy_cordiner_description",
            "wave8_kingdom_kandy_jaques_dictionary",
            "wave8_kingdom_kandy_powell_wars",
        ],
    ),
    _entity(
        _HANWELLA_KANDYAN_ID,
        "Sri Vikrama Rajasinha's Kandyan field force at Hanwella (1803)",
        "event_bounded_royal_invasion_force",
        "Hanwella and the western frontier of the Kingdom of Kandy",
        (
            "Bounded to the royal army repulsed at Hanwella after the Kandyan "
            "counter-invasion of the maritime provinces."
        ),
        [
            "wave8_kingdom_kandy_codrington_short_history",
            "wave8_kingdom_kandy_cordiner_description",
            "wave8_kingdom_kandy_powell_wars",
        ],
    ),
    _entity(
        _KANDY_KANDYAN_ID,
        "Sri Vikrama Rajasinha's Kandyan counterattack force at Kandy (1803)",
        "event_bounded_royal_counterattack_force",
        "Kandy and the Mahaweli crossing, Kingdom of Kandy",
        (
            "Bounded to the royal forces that compelled the British garrison's "
            "surrender and destroyed the withdrawing detachment in June 1803."
        ),
        [
            "wave8_kingdom_kandy_herath_massacre",
            "wave8_kingdom_kandy_johnston_narrative",
            "wave8_kingdom_kandy_powell_wars",
            "wave8_kingdom_kandy_sivasundaram_land",
        ],
    ),
    _entity(
        _KANDY_BRITISH_ID,
        "Major Davie's British Ceylon garrison at Kandy (1803)",
        "event_bounded_colonial_garrison",
        "Kandy and the Mahaweli crossing, Kingdom of Kandy",
        (
            "Bounded to Major Davie's British, Malay, and sepoy garrison and "
            "withdrawing detachment; the post-capitulation killings are not a "
            "second rated event."
        ),
        [
            "wave8_kingdom_kandy_herath_massacre",
            "wave8_kingdom_kandy_johnston_narrative",
            "wave8_kingdom_kandy_powell_wars",
            "wave8_kingdom_kandy_sivasundaram_land",
        ],
    ),
)


WAVE8_KINGDOM_KANDY_ROW_HASHES: dict[str, str] = {
    "hced-Balane1594-1": "83daa0566d2bbda3bf7d675c7327c957269073e2d020f0937ec81e3469684d8e",
    "hced-Gannoruwa1638-1": "ac98a1cbd242c2013a47c364154b3cdce3e0ebb794662fc67141f400ddfdc88c",
    "hced-Hanwella1803-1": "ae1addc255ca5f638c66efb18a261a75f04f3badcafdabcaf3ca83109d9f78a5",
    "hced-Kandy1803-1": "738947c6d1791bf96bb2ff44f72ce4e9d9ee6c975b3b3f1831bfb97db84bd0d9",
    "hced-Kandy1815-1": "362cabcf4a7cf955492a31a473ff40022e05dc7880ca96d9542c16be408223f2",
    "hced-Kandy1818-1": "fcbb39119bd5c3502f6b6a5cba515d22e3585f5aa49a4c6c66b80852c3578243",
    "hced-Radenivela1630-1": "0ddf33d14eaba4c3120532aea883bc5bd0caea3936863a26c14e95edf57fe73e",
}


def _canonical(
    name: str,
    date_text: str,
    date_precision: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:1803:1803",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": 1803,
        "year_high": 1803,
    }


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_KINGDOM_KANDY_ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": "first_kandyan_war_1803",
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "event_bounded_exact_opposing_forces",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_KINGDOM_KANDY_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Hanwella1803-1": _contract(
        "hced-Hanwella1803-1",
        _canonical(
            "Battle of Hanwella (1803)",
            "6 September 1803",
            "day",
            "fort_defense_and_relief_action",
        ),
        [_HANWELLA_BRITISH_ID],
        [_HANWELLA_KANDYAN_ID],
        [
            "wave8_kingdom_kandy_codrington_short_history",
            "wave8_kingdom_kandy_cordiner_description",
            "wave8_kingdom_kandy_jaques_dictionary",
            "wave8_kingdom_kandy_powell_wars",
        ],
        [
            "wave8_kingdom_kandy_codrington_short_history",
            "wave8_kingdom_kandy_cordiner_description",
            "wave8_kingdom_kandy_jaques_dictionary",
            "wave8_kingdom_kandy_powell_wars",
        ],
        (
            "Contemporary and later military histories agree that the Kandyan "
            "advance was repulsed at Hanwella. The contract is limited to the "
            "September fort action; it does not rate the whole war or merge the "
            "earlier August occupation into a second result."
        ),
        0.93,
    ),
    "hced-Kandy1803-1": _contract(
        "hced-Kandy1803-1",
        _canonical(
            "Siege and surrender of the British garrison at Kandy",
            "24-26 June 1803",
            "day_range",
            "siege_capitulation_and_force_destruction",
        ),
        [_KANDY_KANDYAN_ID],
        [_KANDY_BRITISH_ID],
        [
            "wave8_kingdom_kandy_herath_massacre",
            "wave8_kingdom_kandy_johnston_narrative",
            "wave8_kingdom_kandy_powell_wars",
            "wave8_kingdom_kandy_sivasundaram_land",
        ],
        [
            "wave8_kingdom_kandy_herath_massacre",
            "wave8_kingdom_kandy_johnston_narrative",
            "wave8_kingdom_kandy_powell_wars",
            "wave8_kingdom_kandy_sivasundaram_land",
        ],
        (
            "The rated outcome is the Kandyan military defeat of Major Davie's "
            "garrison and withdrawing detachment. The executions after "
            "capitulation are documented context, not a separately invented "
            "battle or an extra Elo update."
        ),
        0.95,
    ),
}


WAVE8_KINGDOM_KANDY_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Kandy1815-1": {
        "raw_row_sha256": WAVE8_KINGDOM_KANDY_ROW_HASHES["hced-Kandy1815-1"],
        "disposition": "terminal_exclusion",
        "exclusion_reason": "unopposed_annexation_and_treaty_cession_not_battle",
        "reviewed_granularity": "occupation_deposition_and_sovereignty_transfer",
        "reviewed_outcome": "not_rateable_no_contested_engagement",
        "evidence_refs": sorted(
            [
                "wave8_kingdom_kandy_national_archives_1815",
                "wave8_kingdom_kandy_powell_wars",
                "wave8_kingdom_kandy_sivasundaram_land",
                "wave8_kingdom_kandy_sumana_1818",
            ]
        ),
        "unknown_is_never_draw": True,
        "audit_note": (
            "The official Convention record and scholarship describe political "
            "manoeuvring, an occupation without resistance, deposition, and a "
            "transfer of sovereignty. HCED's winner label is not evidence of a "
            "competitive battle at Kandy."
        ),
    },
    "hced-Kandy1818-1": {
        "raw_row_sha256": WAVE8_KINGDOM_KANDY_ROW_HASHES["hced-Kandy1818-1"],
        "disposition": "terminal_exclusion",
        "exclusion_reason": "post_annexation_wrong_actor_and_unbounded_rebellion_aggregate",
        "reviewed_granularity": "multi_year_upcountry_rebellion_aggregate",
        "reviewed_outcome": "not_rateable_from_this_row",
        "evidence_refs": sorted(
            [
                "wave8_kingdom_kandy_kodikara_administration",
                "wave8_kingdom_kandy_national_archives_1815",
                "wave8_kingdom_kandy_national_archives_1818",
                "wave8_kingdom_kandy_sumana_1818",
            ]
        ),
        "unknown_is_never_draw": True,
        "audit_note": (
            "The uprising began after the 1815 transfer of sovereignty and was "
            "fought by changing chieftain, monastic, pretender, and local rebel "
            "formations. The generic Kandy city row identifies neither one "
            "engagement nor a time-bounded Kingdom of Kandy belligerent."
        ),
    },
}
WAVE8_KINGDOM_KANDY_EXCLUSIONS = WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS
WAVE8_KINGDOM_KANDY_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_KINGDOM_KANDY_HOLDS,
    **WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS,
}

WAVE8_KINGDOM_KANDY_CONTRACT_IDS = frozenset(WAVE8_KINGDOM_KANDY_CONTRACTS)
WAVE8_KINGDOM_KANDY_HOLD_IDS = frozenset(WAVE8_KINGDOM_KANDY_HOLDS)
WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS
)
WAVE8_KINGDOM_KANDY_EXCLUSION_IDS = WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS
WAVE8_KINGDOM_KANDY_RESERVED_IDS = frozenset(
    WAVE8_KINGDOM_KANDY_CONTRACT_IDS
    | WAVE8_KINGDOM_KANDY_HOLD_IDS
    | WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS
)


WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS: dict[str, dict[str, Any]] = {
    _BALANE_ID: {
        "disposition": "external_wave6_terminal_exclusion",
        "owner_module": "military_elo.promotion.wave6_1500_1799",
        "owner_event_id": None,
        "raw_row_sha256": WAVE8_KINGDOM_KANDY_ROW_HASHES[_BALANE_ID],
        "evidence_refs": sorted(
            [
                "wave8_kingdom_kandy_nova_ceylon",
                "wave8_kingdom_kandy_official_chronology",
            ]
        ),
        "reason": (
            "Wave 6 already excludes this compound: official chronology places "
            "the 1594 defeat at Danture and the battle of Balana in 1602. It "
            "cannot be renamed or redated silently in this exact-label lane."
        ),
    },
    _GANNORUWA_ID: {
        "disposition": "existing_release_owner",
        "owner_module": "military_elo.promotion.wave6_1500_1799",
        "owner_event_id": "hced_wave6_hced_gannoruwa1638_1",
        "canonical_event_name": "Battle of Gannoruwa",
        "raw_row_sha256": WAVE8_KINGDOM_KANDY_ROW_HASHES[_GANNORUWA_ID],
        "evidence_refs": sorted(
            [
                "wave8_kingdom_kandy_nova_ceylon",
                "wave8_kingdom_kandy_official_chronology",
            ]
        ),
        "reason": "The exact HCED row is already rated once by Wave 6.",
    },
    _RADENIVELA_ID: {
        "disposition": "existing_release_owner",
        "owner_module": "military_elo.promotion.wave6_1500_1799",
        "owner_event_id": "hced_wave6_hced_radenivela1630_1",
        "canonical_event_name": "Battle of Randeniwela",
        "raw_row_sha256": WAVE8_KINGDOM_KANDY_ROW_HASHES[_RADENIVELA_ID],
        "evidence_refs": sorted(
            [
                "wave8_kingdom_kandy_nova_ceylon",
                "wave8_kingdom_kandy_official_chronology",
            ]
        ),
        "reason": "The exact HCED row is already rated once by Wave 6.",
    },
}
WAVE8_KINGDOM_KANDY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS = {
    candidate_id: disposition
    for candidate_id, disposition in WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS.items()
    if disposition["disposition"] == "existing_release_owner"
}
WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS = frozenset(
    WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS
)
WAVE8_KINGDOM_KANDY_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_KINGDOM_KANDY_RESERVED_IDS | WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS
)

WAVE8_KINGDOM_KANDY_EXACT_CANDIDATE_ID_SHA256 = (
    "c7c8b70c07410269517d3e45ad226bba4f709daab21124c8128c9705f9094e69"
)
WAVE8_KINGDOM_KANDY_FUNNEL_EVENT_CANDIDATE_ID_SHA256 = (
    "df0340e6f4e99f3a1b782eba4cf6606b56243fe8bb0c5513a3708a56d9ce3c8a"
)
WAVE8_KINGDOM_KANDY_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_KINGDOM_KANDY_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)


WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    _TRINCOMALEE_ID: {
        "disposition": "adjacent_composite_label_outside_exact_lane",
        "raw_row_sha256": (
            "599382d1cf30cc7a64ad817299cab5872c684cdd232f94be3df0f30afffba020"
        ),
        "evidence_refs": sorted(
            [
                "wave8_kingdom_kandy_nova_ceylon",
                "wave8_kingdom_kandy_official_chronology",
            ]
        ),
        "reason": (
            "Trincomalee 1639 uses the distinct composite label 'Netherlands, "
            "Kingdom of Kandy'. It needs its own Dutch-Kandyan coalition and "
            "duplicate audit and is not captured by this literal-label lane."
        ),
    }
}
WAVE8_KINGDOM_KANDY_CROSS_LANE_DISPOSITIONS = (
    WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS
)
WAVE8_KINGDOM_KANDY_ADJACENT_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "1815_sovereignty_boundary": {
        "boundary_year": 1815,
        "disposition": "no_rating_bridge_after_kandyan_convention",
        "evidence_refs": sorted(
            [
                "wave8_kingdom_kandy_national_archives_1815",
                "wave8_kingdom_kandy_sivasundaram_land",
            ]
        ),
        "pre_boundary_candidate_ids": sorted(WAVE8_KINGDOM_KANDY_CONTRACT_IDS),
        "post_boundary_candidate_ids": ["hced-Kandy1818-1"],
    },
    "wave6_persistent_identity": {
        "disposition": "do_not_reuse_persistent_polity_for_event_bounded_forces",
        "existing_entity_id": "kingdom_kandy_1590",
        "evidence_refs": sorted(
            [
                "wave8_kingdom_kandy_national_archives_1815",
                "wave8_kingdom_kandy_powell_wars",
            ]
        ),
        "reason": (
            "Wave 6's reviewed polity remains its owner; the two new events use "
            "bounded field formations and do not alter that continuity policy."
        ),
    },
}

WAVE8_KINGDOM_KANDY_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_KINGDOM_KANDY_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


def _duplicate_audit(year: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": sorted(set(map(normalize_label, aliases))),
        "years": [year, year],
    }


WAVE8_KINGDOM_KANDY_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Hanwella1803-1": _duplicate_audit(
        1803,
        "Battle of Hanwella",
        "Battle of Hanwella (1803)",
        "Defense of Hanwella",
        "Hanwella",
        "Repulse at Hanwella",
    ),
    "hced-Kandy1803-1": _duplicate_audit(
        1803,
        "Destruction of Davie's detachment",
        "Kandy",
        "Kandy garrison",
        "Massacre at Kandy",
        "Siege and surrender of the British garrison at Kandy",
    ),
    "hced-Kandy1815-1": _duplicate_audit(
        1815,
        "Capture of Kandy",
        "Kandyan Convention",
        "Kandy",
        "Occupation of Kandy",
    ),
    "hced-Kandy1818-1": _duplicate_audit(
        1818,
        "Great Rebellion",
        "Kandy",
        "Third Kandyan War",
        "Uva Rebellion",
        "Uva-Wellassa Rebellion",
    ),
}


WAVE8_KINGDOM_KANDY_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Hanwella1803-1": {
        "actions": ["withhold_point"],
        "raw_point": [80.0814292, 6.8978344],
        "retained_country": "Sri Lanka",
        "evidence_refs": sorted(
            [
                "wave8_kingdom_kandy_codrington_short_history",
                "wave8_kingdom_kandy_cordiner_description",
            ]
        ),
        "reason": (
            "HCED supplies a locality point, not an authenticated position for "
            "the fort, defensive line, relief route, or September battlefield."
        ),
    },
    "hced-Kandy1803-1": {
        "actions": ["withhold_point"],
        "raw_point": [80.6337262, 7.2905715],
        "retained_country": "Sri Lanka",
        "evidence_refs": sorted(
            [
                "wave8_kingdom_kandy_herath_massacre",
                "wave8_kingdom_kandy_johnston_narrative",
            ]
        ),
        "reason": (
            "A Kandy city centroid cannot represent the garrison, its retreat, "
            "the Mahaweli crossing, and the sites of the force's destruction."
        ),
    },
}
WAVE8_KINGDOM_KANDY_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_KINGDOM_KANDY_LOCATION_QUARANTINE_REASONS
)
WAVE8_KINGDOM_KANDY_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_KINGDOM_KANDY_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_KINGDOM_KANDY_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_KINGDOM_KANDY_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_KINGDOM_KANDY_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"external:{candidate_id}": disposition
        for candidate_id, disposition in WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS.items()
    },
    **{
        f"related_hced:{candidate_id}": disposition
        for candidate_id, disposition in WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS.items()
    },
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
        "adjacent_lane_dispositions": WAVE8_KINGDOM_KANDY_ADJACENT_LANE_DISPOSITIONS,
        "contracts": WAVE8_KINGDOM_KANDY_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_KINGDOM_KANDY_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_KINGDOM_KANDY_ENTITIES,
        "exact_candidate_id_sha256": WAVE8_KINGDOM_KANDY_EXACT_CANDIDATE_ID_SHA256,
        "expected_candidate_ids": sorted(WAVE8_KINGDOM_KANDY_EXPECTED_CANDIDATE_IDS),
        "external_owner_dispositions": WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS,
        "funnel_candidate_id_sha256": (
            WAVE8_KINGDOM_KANDY_FUNNEL_EVENT_CANDIDATE_ID_SHA256
        ),
        "hced_queue_sha256": WAVE8_KINGDOM_KANDY_HCED_QUEUE_SHA256,
        "holds": WAVE8_KINGDOM_KANDY_HOLDS,
        "integration_dispositions": WAVE8_KINGDOM_KANDY_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_KINGDOM_KANDY_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_queue_sha256": WAVE8_KINGDOM_KANDY_IWBD_QUEUE_SHA256,
        "iwbd_zero_overlap_audit": WAVE8_KINGDOM_KANDY_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_KINGDOM_KANDY_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_KINGDOM_KANDY_OUTCOME_OVERRIDES,
        "related_hced_dispositions": WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS,
        "sources": WAVE8_KINGDOM_KANDY_SOURCES,
        "terminal_exclusions": WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS,
    }


def wave8_kingdom_kandy_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_KINGDOM_KANDY_FINAL_AUDIT_SIGNATURE = (
    "e82a63efa89efb1603c41bad435154a9918ea544d65cb6dd53ecc1b1bb0975e0"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(map(str, values)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_KINGDOM_KANDY_CONTRACTS),
        len(WAVE8_KINGDOM_KANDY_HOLDS),
        len(WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS),
        len(WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS),
    ) != (2, 0, 2, 3):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_KINGDOM_KANDY_ENTITIES), len(WAVE8_KINGDOM_KANDY_SOURCES)) != (
        4,
        13,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_KINGDOM_KANDY_EXPECTED_CANDIDATE_IDS != set(
        WAVE8_KINGDOM_KANDY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    partitions = (
        WAVE8_KINGDOM_KANDY_CONTRACT_IDS,
        WAVE8_KINGDOM_KANDY_HOLD_IDS,
        WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS,
        WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS,
    )
    for index, left in enumerate(partitions):
        for right in partitions[index + 1 :]:
            if left & right:
                raise ValueError(f"{_LANE_NAME} disposition partitions overlap")
    if WAVE8_KINGDOM_KANDY_RESERVED_IDS != {
        "hced-Hanwella1803-1",
        "hced-Kandy1803-1",
        "hced-Kandy1815-1",
        "hced-Kandy1818-1",
    }:
        raise ValueError(f"{_LANE_NAME} unresolved reservation inventory changed")
    if (
        _sorted_newline_sha256(WAVE8_KINGDOM_KANDY_EXPECTED_CANDIDATE_IDS)
        != WAVE8_KINGDOM_KANDY_EXACT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} exact candidate digest changed")
    if wave8_kingdom_kandy_audit_signature() != (
        WAVE8_KINGDOM_KANDY_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_KINGDOM_KANDY_SOURCES
    }
    if len(source_by_id) != len(WAVE8_KINGDOM_KANDY_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({source["source_family_id"] for source in WAVE8_KINGDOM_KANDY_SOURCES}) != 13:
        raise ValueError(f"{_LANE_NAME} source-family independence changed")
    for source in WAVE8_KINGDOM_KANDY_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_KINGDOM_KANDY_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_KINGDOM_KANDY_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "british ceylon",
        "kingdom of kandy",
        "sri lanka",
        "united kingdom",
    }
    used_sources: set[str] = set()
    used_entities: set[str] = set()
    for entity in WAVE8_KINGDOM_KANDY_ENTITIES:
        if int(entity["start_year"]) != 1803 or int(entity["end_year"]) != 1803:
            raise ValueError(f"{_LANE_NAME} identity is not event bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic identity")
        note = str(entity["continuity_note"]).casefold()
        for phrase in ("no rating is inherited", "post-1815", "modern country"):
            if phrase not in note:
                raise ValueError(f"{_LANE_NAME} identity boundary note drifted")
        refs = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity provenance changed")
        used_sources.update(refs)

    for candidate_id, contract in WAVE8_KINGDOM_KANDY_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_KINGDOM_KANDY_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract row hash drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        sides = (
            set(map(str, contract["side_1_entity_ids"])),
            set(map(str, contract["side_2_entity_ids"])),
        )
        if not all(sides) or sides[0] & sides[1] or not set.union(*sides) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} opposing identities changed")
        used_entities.update(set.union(*sides))
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or not contract["actor_override"]
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if (
            len(outcomes) < 4
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
            or any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes)
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        expected_families = sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        )
        if families != expected_families or len(families) < 4:
            raise ValueError(f"{_LANE_NAME} outcome-family provenance drifted")
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identities are not exactly consumed")

    forbidden_exclusion_keys = {
        "result_type",
        "winner_entity_ids",
        "winner_side",
    }
    for candidate_id, exclusion in WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS.items():
        if (
            exclusion["raw_row_sha256"] != WAVE8_KINGDOM_KANDY_ROW_HASHES[candidate_id]
            or exclusion["disposition"] != "terminal_exclusion"
            or exclusion["unknown_is_never_draw"] is not True
            or forbidden_exclusion_keys & set(exclusion)
        ):
            raise ValueError(f"{_LANE_NAME} terminal exclusion changed")
        refs = list(map(str, exclusion["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} exclusion provenance changed")
        used_sources.update(refs)

    if set(WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS) != {
        _BALANE_ID,
        _GANNORUWA_ID,
        _RADENIVELA_ID,
    }:
        raise ValueError(f"{_LANE_NAME} external ownership changed")
    if set(WAVE8_KINGDOM_KANDY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS) != {
        _GANNORUWA_ID,
        _RADENIVELA_ID,
    }:
        raise ValueError(f"{_LANE_NAME} existing-release ownership changed")
    for candidate_id, disposition in WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS.items():
        if disposition["raw_row_sha256"] != WAVE8_KINGDOM_KANDY_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} external row fingerprint changed")
        refs = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} external provenance changed")
        used_sources.update(refs)

    if set(WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS) != {_TRINCOMALEE_ID}:
        raise ValueError(f"{_LANE_NAME} related HCED inventory changed")
    for disposition in WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS.values():
        refs = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} related-row provenance changed")
        used_sources.update(refs)
    for disposition in WAVE8_KINGDOM_KANDY_ADJACENT_LANE_DISPOSITIONS.values():
        refs = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} adjacent-lane provenance changed")
        used_sources.update(refs)

    used_sources.update(
        source_id
        for review in WAVE8_KINGDOM_KANDY_LOCATION_QUARANTINE_REASONS.values()
        for source_id in map(str, review["evidence_refs"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if WAVE8_KINGDOM_KANDY_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} acquired an outcome override")
    if WAVE8_KINGDOM_KANDY_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unreviewed IWBD duplicate")
    if set(WAVE8_KINGDOM_KANDY_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_KINGDOM_KANDY_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    if WAVE8_KINGDOM_KANDY_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_KINGDOM_KANDY_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_KINGDOM_KANDY_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    expected_integration = {
        **{
            f"external:{candidate_id}": disposition
            for candidate_id, disposition in WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_DISPOSITIONS.items()
        },
        **{
            f"related_hced:{candidate_id}": disposition
            for candidate_id, disposition in WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS.items()
        },
    }
    if WAVE8_KINGDOM_KANDY_INTEGRATION_DISPOSITIONS != expected_integration:
        raise ValueError(f"{_LANE_NAME} integration dispositions changed")


def _is_exact_label(value: Any) -> bool:
    return normalize_label(value) == "kingdom of kandy"


def _rows_by_candidate_id(
    rows: Iterable[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    indexed: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            indexed.setdefault(candidate_id, []).append(row)
    return indexed


def validate_wave8_kingdom_kandy_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all seven literal-label rows and their disposition partition."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_KINGDOM_KANDY_CONTRACTS,
        WAVE8_KINGDOM_KANDY_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    indexed = _rows_by_candidate_id(hced_rows)
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_label(row.get("side_1_raw"))
        or _is_exact_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_KINGDOM_KANDY_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact label inventory changed: {sorted(exact_ids)}"
        )
    for candidate_id in WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS:
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} external disposition {candidate_id} expected "
                f"one row, found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != WAVE8_KINGDOM_KANDY_ROW_HASHES[
            candidate_id
        ]:
            raise ValueError(f"{_LANE_NAME} external row fingerprint changed")
    return {
        "external_owner_contracts": len(WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS),
        "holds": len(WAVE8_KINGDOM_KANDY_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": len(WAVE8_KINGDOM_KANDY_EXPECTED_CANDIDATE_IDS),
        "reviewed_unresolved_hced_rows": len(WAVE8_KINGDOM_KANDY_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSION_IDS),
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


_DUPLICATE_MATCH_KEYS = {
    (year, alias)
    for audit in WAVE8_KINGDOM_KANDY_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
}


def validate_wave8_kingdom_kandy_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin Wave 6 ownership and fail closed on any probable event twin."""

    validate_wave8_kingdom_kandy_queue_contracts(hced_rows)
    indexed = _rows_by_candidate_id(hced_rows)
    for candidate_id, disposition in WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS.items():
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} related HCED row {candidate_id} expected one row, "
                f"found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} related HCED fingerprint changed")

    existing = list(existing_events)
    if existing:
        for candidate_id, disposition in (
            WAVE8_KINGDOM_KANDY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
        ):
            owners = [
                event
                for event in existing
                if str(event.get("hced_candidate_id")) == candidate_id
            ]
            if len(owners) != 1 or str(owners[0].get("id")) != disposition[
                "owner_event_id"
            ]:
                raise ValueError(f"{_LANE_NAME} Wave 6 ownership changed for {candidate_id}")
        if any(
            str(event.get("hced_candidate_id")) == _BALANE_ID for event in existing
        ):
            raise ValueError(f"{_LANE_NAME} excluded Balane row acquired an event")

    lane_release_ids = {
        str(event.get("hced_candidate_id"))
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_KINGDOM_KANDY_CONTRACT_IDS
    }
    if lane_release_ids not in (set(), set(WAVE8_KINGDOM_KANDY_CONTRACT_IDS)):
        raise ValueError(f"{_LANE_NAME} release integration is partial")

    allowed_hced = {
        *WAVE8_KINGDOM_KANDY_EXPECTED_CANDIDATE_IDS,
        *WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS,
    }
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in allowed_hced
        and (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if hced_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed HCED twin(s): {hced_matches}")
    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if iwbd_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_matches}")
    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id")
        not in (
            WAVE8_KINGDOM_KANDY_CONTRACT_IDS
            | WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS
        )
        and (_row_year(event), normalize_label(event.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_matches}"
        )
    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_KINGDOM_KANDY_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_KINGDOM_KANDY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(
            WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS
        ),
        "integration_dispositions": len(
            WAVE8_KINGDOM_KANDY_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_KINGDOM_KANDY_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_KINGDOM_KANDY_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "related_hced_dispositions": len(
            WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS
        ),
    }


def install_wave8_kingdom_kandy_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_KINGDOM_KANDY_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_kingdom_kandy_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_KINGDOM_KANDY_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_KINGDOM_KANDY_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_KINGDOM_KANDY_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_kingdom_kandy_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_kingdom_kandy_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_KINGDOM_KANDY_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_kingdom_kandy_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_KINGDOM_KANDY_CONTRACTS.values()
            ).items()
        )
    )


def wave8_kingdom_kandy_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_KINGDOM_KANDY_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_KINGDOM_KANDY_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_KINGDOM_KANDY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(
            WAVE8_KINGDOM_KANDY_EXTERNAL_OWNER_IDS
        ),
        "holds": len(WAVE8_KINGDOM_KANDY_HOLDS),
        "integration_dispositions": len(
            WAVE8_KINGDOM_KANDY_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_KINGDOM_KANDY_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_KINGDOM_KANDY_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_KINGDOM_KANDY_ENTITIES),
        "new_sources": len(WAVE8_KINGDOM_KANDY_SOURCES),
        "newly_rated_events": len(WAVE8_KINGDOM_KANDY_CONTRACTS),
        "outcome_overrides": len(WAVE8_KINGDOM_KANDY_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_KINGDOM_KANDY_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_KINGDOM_KANDY_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_KINGDOM_KANDY_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_KINGDOM_KANDY_EXPECTED_CANDIDATE_IDS),
        "reviewed_unresolved_hced_rows": len(WAVE8_KINGDOM_KANDY_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_KINGDOM_KANDY_TERMINAL_EXCLUSIONS),
    }


def wave8_kingdom_kandy_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_KINGDOM_KANDY_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_KINGDOM_KANDY_POINT_QUARANTINE_ADDITIONS,
    }
