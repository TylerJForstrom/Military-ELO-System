"""Exact Wave 8 adjudication for HCED rows labelled ``Rajputs``.

The raw label spans unrelated dynastic kingdoms, ruler-bounded armies,
temporary coalitions, and campaign commands from 1191 to 1799.  This lane
therefore creates no timeless Rajput or ethnic identity.  Every rated actor is
bounded by a dynasty/regime, a ruler, a campaign, or one event, and no rating
may flow between those boundaries.

All seven exact-label rows are hash-pinned and explicitly dispositioned.  Six
become source-backed engagements.  Chitor is terminally excluded because the
locked 1567 interval truncates a siege whose fall occurred in 1568.  HCED's
Fatehpur orientation is reversed from direct evidence, and Merta's incomplete
``Draw`` placeholder is replaced by a sourced Scindia victory; an unknown
result is never treated as a draw.
"""

from __future__ import annotations

import hashlib
import json
import re
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
    "WAVE8_RAJPUTS_CONTRACT_IDS",
    "WAVE8_RAJPUTS_CONTRACTS",
    "WAVE8_RAJPUTS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_RAJPUTS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_RAJPUTS_ENTITIES",
    "WAVE8_RAJPUTS_EXCLUSION_IDS",
    "WAVE8_RAJPUTS_EXCLUSIONS",
    "WAVE8_RAJPUTS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_RAJPUTS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_RAJPUTS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_RAJPUTS_FUNNEL_SUMMARY",
    "WAVE8_RAJPUTS_GREEDY_AUDIT",
    "WAVE8_RAJPUTS_HCED_DUPLICATE_DISPOSITIONS",
    "WAVE8_RAJPUTS_HOLD_IDS",
    "WAVE8_RAJPUTS_HOLDS",
    "WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS",
    "WAVE8_RAJPUTS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_RAJPUTS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_RAJPUTS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_RAJPUTS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_RAJPUTS_NONPROMOTIONS",
    "WAVE8_RAJPUTS_OUTCOME_OVERRIDES",
    "WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_RAJPUTS_RESERVED_IDS",
    "WAVE8_RAJPUTS_ROW_DISPOSITIONS",
    "WAVE8_RAJPUTS_SOURCES",
    "WAVE8_RAJPUTS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS",
    "install_wave8_rajputs_entities",
    "install_wave8_rajputs_sources",
    "promote_wave8_rajputs_contracts",
    "validate_wave8_rajputs_funnel",
    "validate_wave8_rajputs_integration_dispositions",
    "validate_wave8_rajputs_queue_contracts",
    "wave8_rajputs_audit_signature",
    "wave8_rajputs_cohort_counts",
    "wave8_rajputs_counts",
    "wave8_rajputs_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Rajputs exact-label audit"
_MODULE_OWNER = "wave8_rajputs"
_EVENT_ID_PREFIX = "hced_wave8_rajputs_"

_GHAGHRA_MUGHAL = "babur_mughal_field_army_ghaghra_1529"
_GHAGHRA_DEFENSE = "afghan_bengal_river_defense_ghaghra_1529"
_FATEHPUR_EXPEDITION = "vaman_rao_george_thomas_fatehpur_expedition_1799"
_FATEHPUR_JAIPUR = "sawai_pratap_singh_jaipur_army_fatehpur_1799"
_SCINDIA_CAMPAIGN = "scindia_de_boigne_rajputana_campaign_army_1790"
_PATAN_COALITION = "jaipur_jodhpur_ismail_beg_coalition_patan_1790"
_MERTA_MARWAR = "vijai_singh_marwar_rathor_army_merta_1790"
_CHAHAMANA_REGIME = "prithviraja_iii_chahamana_regime_and_army_1178_1192"
_GHURID_EASTERN_ARMY = "muizz_al_din_ghurid_eastern_army_1173_1206"


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
    if crosscheck:
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


WAVE8_RAJPUTS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_rajputs_cambridge_kolff_chitor",
        "Naukar, Rajput and Sepoy: The Ethnohistory of the Military Labour Market in Hindustan, 1450-1850",
        "https://assets.cambridge.org/97805213/81321/sample/9780521381321ws.pdf",
        "Cambridge University Press",
        "scholarly_monograph",
        "kolff_naukar_rajput_sepoy",
        outcome=True,
    ),
    _source(
        "wave8_rajputs_unesco_chittorgarh",
        "Hill Forts of Rajasthan: World Heritage nomination dossier",
        "https://whc.unesco.org/uploads/nominations/247rev.pdf",
        "UNESCO World Heritage Centre; Archaeological Survey of India",
        "official_heritage_nomination_dossier",
        "unesco_hill_forts_rajasthan_nomination",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_rajputs_inflibnet_mughal_foundation",
        "Origin and Foundation of Mughal Empire: Babar, Humayun and Sher Shah Interregnum",
        "https://ebooks.inflibnet.ac.in/icp01/chapter/origin-and-foundation-of-mughal-empire-babar-humayun-and-sher-shah-interregnum/",
        "INFLIBNET Centre, University Grants Commission of India",
        "academic_history_module",
        "inflibnet_mughal_history_module",
        outcome=True,
    ),
    _source(
        "wave8_rajputs_banglapedia_babur",
        "Babur",
        "https://en.banglapedia.org/index.php/Babur",
        "Banglapedia, Asiatic Society of Bangladesh",
        "scholarly_national_encyclopedia",
        "banglapedia_babur",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_rajputs_baburnama_beveridge",
        "The Bābur-nāma in English (Annette Beveridge translation)",
        "https://www.gutenberg.org/ebooks/44608",
        "Project Gutenberg; translated primary chronicle",
        "digitized_translated_primary_narrative",
        "baburnama_beveridge_translation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_rajputs_culture_fatehpur",
        "Battle of Fatehpur, 1799",
        "https://cmsadmin.amritmahotsav.nic.in/district-reopsitory-detail.htm?17818=",
        "Ministry of Culture, Government of India",
        "government_historical_repository",
        "ministry_culture_fatehpur_history",
        outcome=True,
    ),
    _source(
        "wave8_rajputs_francklin_george_thomas",
        "Military Memoirs of Mr. George Thomas",
        "https://archive.org/download/dli.ernet.231230/231230-Military%20Memoirs%20Of%20Mr.%20George%20Thomas.pdf",
        "William Francklin (1803); Government of India Digital Library scan",
        "digitized_near_contemporary_military_memoir",
        "francklin_george_thomas_1803",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_rajputs_compton_adventurers",
        "A Particular Account of the European Military Adventurers of Hindustan, from 1784 to 1803",
        "https://upload.wikimedia.org/wikipedia/commons/9/9d/A_particular_account_of_the_European_military_adventures_of_Hindustan%2C_from_1784_to_1803_%28IA_particularaccoun00compiala%29.pdf",
        "Herbert Compton (1893); Internet Archive scan",
        "digitized_historical_military_study",
        "compton_european_military_adventurers",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_rajputs_usi_de_boigne",
        "From the Archives: The European Military Adventurers in India: Benoit de Boigne",
        "https://usiofindia.org/pdf/USI_Journal_July_Sept_2025_Issue_97_102.pdf",
        "United Service Institution of India",
        "scholarly_military_history_article",
        "usi_de_boigne_archive_study",
        outcome=True,
    ),
    _source(
        "wave8_rajputs_oxford_sahai",
        "Escalation in Stresses and Artisanal Responses",
        "https://academic.oup.com/book/27262/chapter-abstract/196884893",
        "Oxford University Press",
        "scholarly_monograph_chapter",
        "sahai_politics_patronage_protest",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_rajputs_cambridge_grant_duff",
        "A History of the Mahrattas, Volume 3",
        "https://www.cambridge.org/core/books/history-of-the-mahrattas/83A101524D6B33237889445DA674A6F9",
        "Cambridge University Press, Cambridge Library Collection",
        "scholarly_reissued_historical_monograph",
        "grant_duff_history_mahrattas_volume_3",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_rajputs_ignou_tarain",
        "Unit 12: Establishment and Territorial Consolidation of the Delhi Sultanate",
        "https://egyankosh.ac.in/bitstream/123456789/61926/1/Unit-12.pdf",
        "Indira Gandhi National Open University",
        "academic_history_module",
        "ignou_medieval_india_unit_12",
        outcome=True,
    ),
    _source(
        "wave8_rajputs_ignou_invasions_resistance",
        "Mahmud Ghazni and Mohd. Ghouri: Invasions and Resistance",
        "https://egyankosh.ac.in/bitstream/123456789/53714/1/BHIC-132E.pdf",
        "Indira Gandhi National Open University",
        "academic_history_course_block",
        "ignou_bhic132_invasions_resistance",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_rajputs_cambridge_talbot_prithviraj",
        "The Last Hindu Emperor: Prithviraj Chauhan and the Indian Past",
        "https://assets.cambridge.org/97811071/18560/excerpt/9781107118560_excerpt.pdf",
        "Cambridge University Press",
        "scholarly_monograph",
        "talbot_last_hindu_emperor",
        crosscheck=True,
    ),
    _source(
        "wave8_rajputs_iranica_ghurids",
        "Ghurids",
        "https://www.iranicaonline.org/articles/ghurids/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "iranica_ghurids",
        crosscheck=True,
    ),
)


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_RAJPUTS_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: Iterable[str],
    boundary: str,
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
        "continuity_note": (
            f"{boundary} No rating is inherited by or from a generic Rajput "
            "identity, another kingdom or dynasty, another ruler or command, "
            "a later state, or any modern ethnic or political community."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_RAJPUTS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _GHAGHRA_MUGHAL,
        "Babur's Mughal field army at Ghaghra (1529)",
        "event_bounded_imperial_field_army",
        1529,
        1529,
        "Ghaghra-Ganges confluence campaign, northern India",
        [
            "wave8_rajputs_baburnama_beveridge",
            "wave8_rajputs_banglapedia_babur",
            "wave8_rajputs_inflibnet_mughal_foundation",
        ],
        "Only Babur's army in the May 1529 river action is rated.",
    ),
    _entity(
        _GHAGHRA_DEFENSE,
        "Afghan-Bengal river defense at Ghaghra (1529)",
        "event_bounded_coalition",
        1529,
        1529,
        "Ghaghra-Ganges confluence campaign, northern India",
        [
            "wave8_rajputs_baburnama_beveridge",
            "wave8_rajputs_banglapedia_babur",
            "wave8_rajputs_inflibnet_mughal_foundation",
        ],
        (
            "Only the Afghan force associated with Mahmud Lodi and the Bengal "
            "river defense associated with Nusrat Shah in this action are rated."
        ),
    ),
    _entity(
        _FATEHPUR_EXPEDITION,
        "Vamana Rao-George Thomas Fatehpur expedition (1799)",
        "event_bounded_coalition_command",
        1799,
        1799,
        "Fatehpur Shekhawati, Rajasthan",
        [
            "wave8_rajputs_compton_adventurers",
            "wave8_rajputs_culture_fatehpur",
            "wave8_rajputs_francklin_george_thomas",
        ],
        (
            "Only the March 1799 Maratha-associated expedition under Vamana "
            "Rao with George Thomas's contingent is rated."
        ),
    ),
    _entity(
        _FATEHPUR_JAIPUR,
        "Sawai Pratap Singh's Jaipur army at Fatehpur (1799)",
        "ruler_and_event_bounded_kingdom_command",
        1799,
        1799,
        "Jaipur kingdom and Fatehpur Shekhawati, Rajasthan",
        [
            "wave8_rajputs_compton_adventurers",
            "wave8_rajputs_culture_fatehpur",
            "wave8_rajputs_francklin_george_thomas",
        ],
        (
            "Only the Jaipur kingdom's Fatehpur force under Sawai Pratap Singh's "
            "authority and its named field command is rated."
        ),
    ),
    _entity(
        _SCINDIA_CAMPAIGN,
        "Scindia-de Boigne Rajputana campaign army (1790)",
        "regime_bounded_campaign_command",
        1790,
        1790,
        "Rajputana campaign under Mahadji Scindia",
        [
            "wave8_rajputs_cambridge_grant_duff",
            "wave8_rajputs_oxford_sahai",
            "wave8_rajputs_usi_de_boigne",
        ],
        (
            "Only Mahadji Scindia's 1790 Hindustan army under de Boigne in the "
            "Patan-Merta campaign is rated."
        ),
    ),
    _entity(
        _PATAN_COALITION,
        "Jaipur-Jodhpur-Ismail Beg coalition at Patan (1790)",
        "event_bounded_coalition",
        1790,
        1790,
        "Patan, Rajputana",
        [
            "wave8_rajputs_cambridge_grant_duff",
            "wave8_rajputs_oxford_sahai",
            "wave8_rajputs_usi_de_boigne",
        ],
        (
            "Only the Jaipur and Jodhpur forces joined with Ismail Beg for the "
            "Patan engagement are rated."
        ),
    ),
    _entity(
        _MERTA_MARWAR,
        "Vijai Singh's Marwar Rathor army at Merta (1790)",
        "ruler_and_event_bounded_kingdom_command",
        1790,
        1790,
        "Marwar kingdom and Merta, Rajputana",
        [
            "wave8_rajputs_cambridge_grant_duff",
            "wave8_rajputs_oxford_sahai",
            "wave8_rajputs_usi_de_boigne",
        ],
        (
            "Only Maharaja Vijai Singh's Marwar Rathor army in the Merta action "
            "is rated."
        ),
    ),
    _entity(
        _CHAHAMANA_REGIME,
        "Prithviraja III's Chahamana kingdom and field army (1178-1192)",
        "ruler_bounded_dynastic_regime",
        1178,
        1192,
        "Ajmer-Delhi Chahamana realm",
        [
            "wave8_rajputs_cambridge_talbot_prithviraj",
            "wave8_rajputs_ignou_invasions_resistance",
            "wave8_rajputs_ignou_tarain",
            "wave8_rajputs_iranica_ghurids",
        ],
        (
            "Only the Chahamana regime and army under Prithviraja III are rated; "
            "later literary claims of a timeless pan-Rajput host are not adopted."
        ),
    ),
    _entity(
        _GHURID_EASTERN_ARMY,
        "Mu'izz al-Din Muhammad's Ghurid eastern army (1173-1206)",
        "ruler_bounded_regime_command",
        1173,
        1206,
        "Ghazna-Punjab-northern India campaign sphere",
        [
            "wave8_rajputs_cambridge_talbot_prithviraj",
            "wave8_rajputs_ignou_invasions_resistance",
            "wave8_rajputs_ignou_tarain",
            "wave8_rajputs_iranica_ghurids",
        ],
        (
            "Only the Ghurid eastern campaigning regime and command under Mu'izz "
            "al-Din Muhammad are rated."
        ),
    ),
)


_ROW_HASHES: dict[str, str] = {
    "hced-Chitor1567-1": "58def3bd76ea1d59bfdf3674e681f5561fce30370de465951be4e81b3bd2bab9",
    "hced-Fatehpur1799-1": "dd790e80afeec048dbaa65d9b6f3012dc0cf124577a9d05582c05e01012337e9",
    "hced-Gogra1529-1": "a4b7719c6574c5e1d94adf0e1fa81d58ea9e241490222a47624040842188e024",
    "hced-Merta1790-1": "86762101145c355cdcf254ef225ada2c71f275a69168fd888fa06b2fad7dd0f4",
    "hced-Patan1790-1": "e932fcd40bc646f8714811900f9f8e74340f40a9f645a213da9b9e8faa27fc50",
    "hced-Taraori1191-1": "3a13d444cefd83a90a5b15477d73ac2cfd6824318d9faa4c432833903e283eab",
    "hced-Taraori1192-1": "db938a751443b8d49c86b2275b308eb4da7d9c27cb31d37a1cd766d0f5bd6e5b",
}


_SOLE_BLOCKER_IDS = frozenset(
    {
        "hced-Chitor1567-1",
        "hced-Gogra1529-1",
        "hced-Merta1790-1",
        "hced-Patan1790-1",
    }
)


WAVE8_RAJPUTS_FUNNEL_SUMMARY: dict[str, Any] = {
    "candidate_ids": [],
    "centuries": {"CE_12": 2, "CE_16": 2, "CE_18": 3},
    "components_bridged": 0,
    "components_touched": 1,
    "event_candidate_id_sha256": "c39bff610c71388f144308649e960ed193ae0dfce339bdd678f8746be1e04264",
    "events_touched": 7,
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 7,
    },
    "label": "rajputs",
    "rated_counterpart_entities": 2,
    "sole_blocker_events": 4,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 7,
}


WAVE8_RAJPUTS_GREEDY_AUDIT: dict[str, Any] = {
    "events_touched": 7,
    "marginal_events": 4,
    "newly_unblocked_candidate_id_sha256": "0f9809cbae3d23bea7a0afd8aa0f8011d1cd2dc5efb058f0c675243413a35cae",
}


_FUNNEL_SCOPE: dict[
    str, tuple[tuple[str, ...], bool, str | None, tuple[str, ...], tuple[str, ...]]
] = {
    "hced-Chitor1567-1": (
        ("rajputs",),
        True,
        "rajputs",
        (),
        ("mughal_empire",),
    ),
    "hced-Fatehpur1799-1": (
        ("hariana", "rajputs"),
        True,
        None,
        (),
        (),
    ),
    "hced-Gogra1529-1": (
        ("rajputs",),
        True,
        "rajputs",
        (),
        ("mughal_empire",),
    ),
    "hced-Merta1790-1": (
        ("rajputs",),
        True,
        "rajputs",
        (),
        ("maratha_confederacy",),
    ),
    "hced-Patan1790-1": (
        ("rajputs",),
        True,
        "rajputs",
        (),
        ("maratha_confederacy",),
    ),
    "hced-Taraori1191-1": (
        ("ghor", "rajputs"),
        True,
        None,
        (),
        (),
    ),
    "hced-Taraori1192-1": (
        ("ghor", "rajputs"),
        True,
        None,
        (),
        (),
    ),
}


def _canonical(
    name: str,
    year_low: int,
    date_text: str,
    *,
    year_high: int | None = None,
    date_precision: str = "year",
    granularity: str = "engagement",
) -> dict[str, Any]:
    high = year_low if year_high is None else year_high
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{high}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": high,
    }


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    source_outcome_override: bool = False,
    outcome_reversal: bool = False,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "interstate_limited",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": outcome_reversal,
        "actor_override": "bounded_exact_opposing_forces",
        "audit_note": audit_note,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
    }


WAVE8_RAJPUTS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Fatehpur1799-1": _contract(
        "hced-Fatehpur1799-1",
        _canonical(
            "Battle of Fatehpur, Shekhawati",
            1799,
            "March 1799",
            date_precision="month",
        ),
        "jaipur_maratha_fatehpur_1799",
        [_FATEHPUR_EXPEDITION],
        [_FATEHPUR_JAIPUR],
        2,
        [
            "wave8_rajputs_compton_adventurers",
            "wave8_rajputs_culture_fatehpur",
            "wave8_rajputs_francklin_george_thomas",
        ],
        [
            "wave8_rajputs_compton_adventurers",
            "wave8_rajputs_culture_fatehpur",
            "wave8_rajputs_francklin_george_thomas",
        ],
        (
            "The Ministry of Culture locates the March 1799 battle at Fatehpur "
            "in present Sikar district and records a decisive Jaipur victory over "
            "the Vamana Rao-George Thomas expedition. This directly reverses "
            "HCED's Hariana-winner proposal; the Uttar Pradesh geocode is withheld."
        ),
        confidence=0.91,
        source_outcome_override=True,
        outcome_reversal=True,
    ),
    "hced-Gogra1529-1": _contract(
        "hced-Gogra1529-1",
        _canonical(
            "Battle of Ghaghra",
            1529,
            "May 1529",
            date_precision="month",
        ),
        "babur_eastern_campaign_1529",
        [_GHAGHRA_MUGHAL],
        [_GHAGHRA_DEFENSE],
        1,
        [
            "wave8_rajputs_baburnama_beveridge",
            "wave8_rajputs_banglapedia_babur",
            "wave8_rajputs_inflibnet_mughal_foundation",
        ],
        [
            "wave8_rajputs_baburnama_beveridge",
            "wave8_rajputs_banglapedia_babur",
            "wave8_rajputs_inflibnet_mughal_foundation",
        ],
        (
            "HCED's Gogra row matches Babur's May 1529 Ghaghra river victory, "
            "but the opposing force was an Afghan-Bengal defense rather than a "
            "Rajput identity. The corrected event actors retain the raw Mughal "
            "orientation; the raw Jharkhand point is unrelated and withheld."
        ),
        confidence=0.93,
    ),
    "hced-Merta1790-1": _contract(
        "hced-Merta1790-1",
        _canonical(
            "Battle of Merta",
            1790,
            "September 1790 (published day varies)",
            date_precision="month",
        ),
        "scindia_rajputana_campaign_1790",
        [_MERTA_MARWAR],
        [_SCINDIA_CAMPAIGN],
        2,
        [
            "wave8_rajputs_cambridge_grant_duff",
            "wave8_rajputs_oxford_sahai",
            "wave8_rajputs_usi_de_boigne",
        ],
        [
            "wave8_rajputs_cambridge_grant_duff",
            "wave8_rajputs_oxford_sahai",
            "wave8_rajputs_usi_de_boigne",
        ],
        (
            "The sources record de Boigne's Scindia army defeating Vijai Singh's "
            "Marwar Rathor force and taking Merta in September. HCED's incomplete "
            "Draw/unknown placeholder is not evidence of a draw and is replaced "
            "by the sourced tactical win; the town-centroid point is withheld."
        ),
        confidence=0.90,
        source_outcome_override=True,
        outcome_reversal=False,
    ),
    "hced-Patan1790-1": _contract(
        "hced-Patan1790-1",
        _canonical(
            "Battle of Patan",
            1790,
            "June 1790 (published day varies)",
            date_precision="month",
        ),
        "scindia_rajputana_campaign_1790",
        [_SCINDIA_CAMPAIGN],
        [_PATAN_COALITION],
        1,
        [
            "wave8_rajputs_cambridge_grant_duff",
            "wave8_rajputs_oxford_sahai",
            "wave8_rajputs_usi_de_boigne",
        ],
        [
            "wave8_rajputs_cambridge_grant_duff",
            "wave8_rajputs_oxford_sahai",
            "wave8_rajputs_usi_de_boigne",
        ],
        (
            "The event is narrowed to de Boigne's June 1790 victory over the "
            "Jaipur-Jodhpur-Ismail Beg coalition. It does not rate a generic "
            "Maratha or Rajput identity, and the town point is not asserted as a "
            "reviewed battlefield coordinate."
        ),
        confidence=0.92,
    ),
    "hced-Taraori1191-1": _contract(
        "hced-Taraori1191-1",
        _canonical("First Battle of Tarain", 1191, "1191"),
        "tarain_ghurid_chahamana_wars_1191_1192",
        [_CHAHAMANA_REGIME],
        [_GHURID_EASTERN_ARMY],
        1,
        [
            "wave8_rajputs_cambridge_talbot_prithviraj",
            "wave8_rajputs_ignou_invasions_resistance",
            "wave8_rajputs_ignou_tarain",
            "wave8_rajputs_iranica_ghurids",
        ],
        [
            "wave8_rajputs_ignou_invasions_resistance",
            "wave8_rajputs_ignou_tarain",
        ],
        (
            "The 1191 victory belongs to Prithviraja III's Chahamana force over "
            "Mu'izz al-Din's Ghurid army. Later expansive coalition traditions "
            "and HCED's malformed northern-Italy war name are not adopted; the "
            "Taraori geocode is withheld as an unverified battlefield point."
        ),
        confidence=0.91,
    ),
    "hced-Taraori1192-1": _contract(
        "hced-Taraori1192-1",
        _canonical("Second Battle of Tarain", 1192, "1192"),
        "tarain_ghurid_chahamana_wars_1191_1192",
        [_GHURID_EASTERN_ARMY],
        [_CHAHAMANA_REGIME],
        1,
        [
            "wave8_rajputs_cambridge_talbot_prithviraj",
            "wave8_rajputs_ignou_invasions_resistance",
            "wave8_rajputs_ignou_tarain",
            "wave8_rajputs_iranica_ghurids",
        ],
        [
            "wave8_rajputs_ignou_invasions_resistance",
            "wave8_rajputs_ignou_tarain",
        ],
        (
            "The 1192 Ghurid victory is attached only to Mu'izz al-Din's eastern "
            "army against Prithviraja III's Chahamana regime. No generic Ghor or "
            "Rajput continuity is inferred, and the unverified point is withheld."
        ),
        confidence=0.94,
    ),
}


WAVE8_RAJPUTS_HOLDS: dict[str, dict[str, Any]] = {}


WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Chitor1567-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Chitor1567-1"],
        "canonical_event": _canonical(
            "Siege of Chittor",
            1567,
            "October 1567-February 1568",
            year_high=1568,
            date_precision="month_range",
            granularity="siege",
        ),
        "disposition": "terminal_exclusion",
        "exclusion_category": "locked_interval_truncates_siege",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_actor_description": [
            "Akbar's Mughal siege army",
            "Mewar's Chittor garrison under Jaimal and Patta",
        ],
        "reviewed_granularity": "siege",
        "reviewed_date": "October 1567-February 1568",
        "reviewed_outcome": (
            "The Mughal capture followed the fortress's fall in February 1568, "
            "outside HCED's locked 1567 interval."
        ),
        "exclusion_reason": (
            "The direct scholarly chronology runs from October 1567 through the "
            "fall of Chittor in February 1568. Promotion against the locked "
            "1567-1567 row would attach Akbar's victory before it occurred and "
            "truncate the siege. The row is explicitly not promoted, and its "
            "unrateable locked result is never encoded as a draw."
        ),
        "evidence_refs": [
            "wave8_rajputs_cambridge_kolff_chitor",
            "wave8_rajputs_unesco_chittorgarh",
        ],
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "terminal_hced_owner",
        },
    }
}


WAVE8_RAJPUTS_EXCLUSIONS = WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS
WAVE8_RAJPUTS_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_RAJPUTS_HOLDS,
    **WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS,
}

WAVE8_RAJPUTS_CONTRACT_IDS = frozenset(WAVE8_RAJPUTS_CONTRACTS)
WAVE8_RAJPUTS_HOLD_IDS = frozenset(WAVE8_RAJPUTS_HOLDS)
WAVE8_RAJPUTS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS
)
WAVE8_RAJPUTS_EXCLUSION_IDS = WAVE8_RAJPUTS_TERMINAL_EXCLUSION_IDS
WAVE8_RAJPUTS_RESERVED_IDS = (
    WAVE8_RAJPUTS_CONTRACT_IDS
    | WAVE8_RAJPUTS_HOLD_IDS
    | WAVE8_RAJPUTS_TERMINAL_EXCLUSION_IDS
)
WAVE8_RAJPUTS_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)
WAVE8_RAJPUTS_ROW_DISPOSITIONS = {
    candidate_id: (
        "PROMOTE"
        if candidate_id in WAVE8_RAJPUTS_CONTRACT_IDS
        else "TERMINAL_EXCLUSION"
    )
    for candidate_id in sorted(WAVE8_RAJPUTS_RESERVED_IDS)
}


def _integration_dispositions() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for candidate_id, (labels, eligible, sole, other, counterparts) in sorted(
        _FUNNEL_SCOPE.items()
    ):
        result[candidate_id] = {
            "disposition": WAVE8_RAJPUTS_ROW_DISPOSITIONS[candidate_id],
            "full_row_audited": True,
            "blocker_labels": list(labels),
            "greedy_eligible": eligible,
            "sole_blocker_label": sole,
            "other_blockers": list(other),
            "resolved_counterpart_entity_ids": list(counterparts),
            "all_opposing_actors_resolved": True,
            "release_duplicate_scan": "no_existing_release_event_twin_found",
            "owner_module": _MODULE_OWNER,
        }
    return result


WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS = _integration_dispositions()


# These are local, promoted-only declarations.  Integration may later add them
# to the shared manifest, but this exact lane deliberately does not edit it.
WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_RAJPUTS_CONTRACT_IDS
)
WAVE8_RAJPUTS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_RAJPUTS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_RAJPUTS_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_RAJPUTS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Fatehpur1799-1": {
        "field": "geometry",
        "raw_point": [80.8986502, 25.8499808],
        "reason": (
            "The raw point is Fatehpur in Uttar Pradesh, while the reviewed "
            "battle occurred at Fatehpur Shekhawati in present Sikar, Rajasthan."
        ),
        "evidence_refs": ["wave8_rajputs_culture_fatehpur"],
    },
    "hced-Gogra1529-1": {
        "field": "geometry",
        "raw_point": [86.9530213, 23.459156],
        "reason": (
            "The raw Jharkhand point does not represent the Ghaghra river action "
            "in Babur's eastern campaign."
        ),
        "evidence_refs": [
            "wave8_rajputs_banglapedia_babur",
            "wave8_rajputs_inflibnet_mughal_foundation",
        ],
    },
    "hced-Merta1790-1": {
        "field": "geometry",
        "raw_point": [74.0309418, 26.644952],
        "reason": (
            "The HCED point is a town geocode; the reviewed sources do not "
            "establish it as an exact battlefield coordinate."
        ),
        "evidence_refs": ["wave8_rajputs_usi_de_boigne"],
    },
    "hced-Patan1790-1": {
        "field": "geometry",
        "raw_point": [75.9726329, 27.7865656],
        "reason": (
            "The HCED point is a locality geocode; the reviewed sources do not "
            "establish it as an exact battlefield coordinate."
        ),
        "evidence_refs": ["wave8_rajputs_usi_de_boigne"],
    },
    "hced-Taraori1191-1": {
        "field": "geometry",
        "raw_point": [76.9239727, 29.7996282],
        "reason": (
            "The Taraori locality point is not independently established as the "
            "exact 1191 battlefield coordinate."
        ),
        "evidence_refs": ["wave8_rajputs_ignou_tarain"],
    },
    "hced-Taraori1192-1": {
        "field": "geometry",
        "raw_point": [76.9124935, 29.795588],
        "reason": (
            "The Taraori locality point is not independently established as the "
            "exact 1192 battlefield coordinate."
        ),
        "evidence_refs": ["wave8_rajputs_ignou_tarain"],
    },
}


WAVE8_RAJPUTS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Fatehpur1799-1": {
        "raw_winner_raw": "Hariana",
        "raw_loser_raw": "Rajputs",
        "raw_winner_loser_complete": True,
        "corrected_result_type": "win",
        "corrected_winner_side": 2,
        "corrected_winner_entity_ids": [_FATEHPUR_JAIPUR],
        "corrected_loser_entity_ids": [_FATEHPUR_EXPEDITION],
        "override_kind": "sourced_tactical_outcome_reversal",
        "outcome_reversal": True,
        "outcome_source_ids": WAVE8_RAJPUTS_CONTRACTS[
            "hced-Fatehpur1799-1"
        ]["outcome_source_ids"],
        "outcome_source_family_ids": WAVE8_RAJPUTS_CONTRACTS[
            "hced-Fatehpur1799-1"
        ]["outcome_source_family_ids"],
    },
    "hced-Merta1790-1": {
        "raw_winner_raw": "Draw",
        "raw_loser_raw": None,
        "raw_winner_loser_complete": False,
        "corrected_result_type": "win",
        "corrected_winner_side": 2,
        "corrected_winner_entity_ids": [_SCINDIA_CAMPAIGN],
        "corrected_loser_entity_ids": [_MERTA_MARWAR],
        "override_kind": "unknown_draw_placeholder_to_sourced_scindia_victory",
        "outcome_reversal": False,
        "outcome_source_ids": WAVE8_RAJPUTS_CONTRACTS["hced-Merta1790-1"][
            "outcome_source_ids"
        ],
        "outcome_source_family_ids": WAVE8_RAJPUTS_CONTRACTS[
            "hced-Merta1790-1"
        ]["outcome_source_family_ids"],
    },
}


WAVE8_RAJPUTS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_RAJPUTS_HCED_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_RAJPUTS_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_RAJPUTS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}

WAVE8_RAJPUTS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Chitor1567-1": {
        "aliases": (
            "chitor",
            "chittor",
            "chittorgarh",
            "siege of chitor",
            "siege of chittor",
            "siege of chittorgarh",
        ),
        "years": (1567, 1568),
    },
    "hced-Fatehpur1799-1": {
        "aliases": (
            "battle of fatehpur",
            "battle of fatehpur shekhawati",
            "fatehpur",
            "fatehpur shekhawati",
        ),
        "years": (1799,),
    },
    "hced-Gogra1529-1": {
        "aliases": (
            "battle of ghaghra",
            "battle of gogra",
            "ghaghra",
            "ghagra",
            "gogra",
        ),
        "years": (1529,),
    },
    "hced-Merta1790-1": {
        "aliases": ("battle of merta", "merta", "mertha"),
        "years": (1790,),
    },
    "hced-Patan1790-1": {
        "aliases": ("battle of patan", "patan"),
        "years": (1790,),
    },
    "hced-Taraori1191-1": {
        "aliases": (
            "battle of tarain",
            "first battle of tarain",
            "first battle of taraori",
            "tarain",
            "taraori",
        ),
        "years": (1191,),
    },
    "hced-Taraori1192-1": {
        "aliases": (
            "battle of tarain",
            "second battle of tarain",
            "second battle of taraori",
            "tarain",
            "taraori",
        ),
        "years": (1192,),
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_RAJPUTS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_RAJPUTS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_RAJPUTS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_RAJPUTS_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_RAJPUTS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_RAJPUTS_EXPECTED_CANDIDATE_IDS),
        "funnel_summary": WAVE8_RAJPUTS_FUNNEL_SUMMARY,
        "greedy_audit": WAVE8_RAJPUTS_GREEDY_AUDIT,
        "hced_duplicate_dispositions": WAVE8_RAJPUTS_HCED_DUPLICATE_DISPOSITIONS,
        "holds": WAVE8_RAJPUTS_HOLDS,
        "integration_dispositions": WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_RAJPUTS_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_RAJPUTS_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_RAJPUTS_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_RAJPUTS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS
        ),
        "row_dispositions": WAVE8_RAJPUTS_ROW_DISPOSITIONS,
        "sources": WAVE8_RAJPUTS_SOURCES,
        "terminal_exclusions": WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS,
    }


def wave8_rajputs_audit_signature() -> str:
    """Return the deterministic digest of the complete exact-label audit."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_RAJPUTS_FINAL_AUDIT_SIGNATURE = (
    "dabc16f4566a9bd287dff08dd9a4eac35b7e2fb76f30fa9539c390601b43ddaf"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(map(str, values))))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_RAJPUTS_CONTRACTS),
        len(WAVE8_RAJPUTS_HOLDS),
        len(WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS),
    ) != (6, 0, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_RAJPUTS_ENTITIES), len(WAVE8_RAJPUTS_SOURCES)) != (9, 15):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_RAJPUTS_RESERVED_IDS != WAVE8_RAJPUTS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    dispositions = (
        WAVE8_RAJPUTS_CONTRACT_IDS,
        WAVE8_RAJPUTS_HOLD_IDS,
        WAVE8_RAJPUTS_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(3)
        for j in range(i + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if WAVE8_RAJPUTS_EXCLUSIONS is not WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion aliases diverged")
    if wave8_rajputs_audit_signature() != WAVE8_RAJPUTS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    if _sorted_newline_sha256(WAVE8_RAJPUTS_EXPECTED_CANDIDATE_IDS) != str(
        WAVE8_RAJPUTS_FUNNEL_SUMMARY["event_candidate_id_sha256"]
    ):
        raise ValueError(f"{_LANE_NAME} exact-cohort digest drifted")
    if _sorted_newline_sha256(_SOLE_BLOCKER_IDS) != str(
        WAVE8_RAJPUTS_GREEDY_AUDIT["newly_unblocked_candidate_id_sha256"]
    ):
        raise ValueError(f"{_LANE_NAME} sole-blocker digest drifted")

    source_by_id = {str(source["id"]): source for source in WAVE8_RAJPUTS_SOURCES}
    if len(source_by_id) != len(WAVE8_RAJPUTS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({source["source_family_id"] for source in WAVE8_RAJPUTS_SOURCES}) != len(
        WAVE8_RAJPUTS_SOURCES
    ):
        raise ValueError(f"{_LANE_NAME} source families are not independently pinned")
    for source in WAVE8_RAJPUTS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_RAJPUTS_ENTITIES}
    if len(entity_by_id) != len(WAVE8_RAJPUTS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "rajput",
        "rajput army",
        "rajput kingdom",
        "rajput kingdoms",
        "rajputs",
    }
    for entity in WAVE8_RAJPUTS_ENTITIES:
        if int(entity["start_year"]) > int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} entity has an invalid time window")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} opened an identity fallback")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a timeless Rajput identity")
        if "bounded" not in str(entity["kind"]):
            raise ValueError(f"{_LANE_NAME} entity is not explicitly bounded")
        note = str(entity["continuity_note"]).casefold()
        for phrase in ("no rating is inherited", "generic rajput", "modern"):
            if phrase not in note:
                raise ValueError(f"{_LANE_NAME} entity firewall is incomplete")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    expected_contracts = {
        "hced-Fatehpur1799-1": (
            [_FATEHPUR_EXPEDITION],
            [_FATEHPUR_JAIPUR],
            2,
            "month",
            True,
            True,
        ),
        "hced-Gogra1529-1": (
            [_GHAGHRA_MUGHAL],
            [_GHAGHRA_DEFENSE],
            1,
            "month",
            False,
            False,
        ),
        "hced-Merta1790-1": (
            [_MERTA_MARWAR],
            [_SCINDIA_CAMPAIGN],
            2,
            "month",
            True,
            False,
        ),
        "hced-Patan1790-1": (
            [_SCINDIA_CAMPAIGN],
            [_PATAN_COALITION],
            1,
            "month",
            False,
            False,
        ),
        "hced-Taraori1191-1": (
            [_CHAHAMANA_REGIME],
            [_GHURID_EASTERN_ARMY],
            1,
            "year",
            False,
            False,
        ),
        "hced-Taraori1192-1": (
            [_GHURID_EASTERN_ARMY],
            [_CHAHAMANA_REGIME],
            1,
            "year",
            False,
            False,
        ),
    }
    used_entities: set[str] = set()
    used_sources: set[str] = set()
    override_ids: set[str] = set()
    reversal_ids: set[str] = set()
    for candidate_id, contract in WAVE8_RAJPUTS_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1, side_2, winner, precision, override, reversal = expected_contracts[
            candidate_id
        ]
        if contract["side_1_entity_ids"] != side_1 or contract[
            "side_2_entity_ids"
        ] != side_2:
            raise ValueError(f"{_LANE_NAME} actor contract drifted")
        if canonical["date_precision"] != precision:
            raise ValueError(f"{_LANE_NAME} date precision drifted")
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != winner
            or contract["source_outcome_override"] is not override
            or contract["outcome_reversal"] is not reversal
            or contract["actor_override"] != "bounded_exact_opposing_forces"
        ):
            raise ValueError(f"{_LANE_NAME} outcome or actor contract drifted")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
        if override:
            override_ids.add(candidate_id)
        if reversal:
            reversal_ids.add(candidate_id)

        actor_ids = set(side_1) | set(side_2)
        if not actor_ids <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} contract names an unknown entity")
        low, high = int(canonical["year_low"]), int(canonical["year_high"])
        for entity_id in actor_ids:
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= low <= high <= int(
                entity["end_year"]
            ):
                raise ValueError(f"{_LANE_NAME} contract exceeds an entity window")
        used_entities.update(actor_ids)

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if (
            len(outcomes) < 2
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome result source")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identities are not exactly consumed")
    if override_ids != {"hced-Fatehpur1799-1", "hced-Merta1790-1"}:
        raise ValueError(f"{_LANE_NAME} outcome override inventory drifted")
    if reversal_ids != {"hced-Fatehpur1799-1"}:
        raise ValueError(f"{_LANE_NAME} outcome reversal inventory drifted")
    if set(WAVE8_RAJPUTS_OUTCOME_OVERRIDES) != override_ids:
        raise ValueError(f"{_LANE_NAME} override metadata is incomplete")
    for candidate_id, override in WAVE8_RAJPUTS_OUTCOME_OVERRIDES.items():
        contract = WAVE8_RAJPUTS_CONTRACTS[candidate_id]
        winner_side = int(override["corrected_winner_side"])
        if (
            override["corrected_result_type"] != "win"
            or winner_side != contract["winner_side"]
            or override["corrected_winner_entity_ids"]
            != contract[f"side_{winner_side}_entity_ids"]
            or override["corrected_loser_entity_ids"]
            != contract[f"side_{3 - winner_side}_entity_ids"]
            or override["outcome_source_ids"] != contract["outcome_source_ids"]
            or override["outcome_source_family_ids"]
            != contract["outcome_source_family_ids"]
            or override["outcome_reversal"] is not contract["outcome_reversal"]
        ):
            raise ValueError(f"{_LANE_NAME} corrected outcome metadata drifted")

    if WAVE8_RAJPUTS_HOLDS:
        raise ValueError(f"{_LANE_NAME} acquired a hold")
    exclusion = WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS.get("hced-Chitor1567-1")
    if exclusion is None:
        raise ValueError(f"{_LANE_NAME} lost the Chitor exclusion")
    if (
        exclusion["raw_row_sha256"] != _ROW_HASHES["hced-Chitor1567-1"]
        or exclusion["disposition"] != "terminal_exclusion"
        or exclusion["result_type"] != "unknown"
        or exclusion["unknown_is_never_draw"] is not True
        or exclusion["canonical_event"]["year_high"] != 1568
    ):
        raise ValueError(f"{_LANE_NAME} Chitor became rateable")
    for forbidden in (
        "winner_side",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "outcome_source_ids",
        "outcome_source_family_ids",
    ):
        if forbidden in exclusion:
            raise ValueError(f"{_LANE_NAME} exclusion asserts a rated field")
    exclusion_reason = str(exclusion["exclusion_reason"]).casefold()
    for phrase in ("not promoted", "draw", "1568", "truncate"):
        if phrase not in exclusion_reason:
            raise ValueError(f"{_LANE_NAME} exclusion policy text drifted")
    used_sources.update(map(str, exclusion["evidence_refs"]))

    used_sources.update(
        source_id
        for entity in WAVE8_RAJPUTS_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    for reason in WAVE8_RAJPUTS_LOCATION_QUARANTINE_REASONS.values():
        refs = list(map(str, reason["evidence_refs"]))
        if not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence drifted")
        used_sources.update(refs)
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")

    if WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS != WAVE8_RAJPUTS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine is not promoted-only")
    if WAVE8_RAJPUTS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_RAJPUTS_LOCATION_QUARANTINE_REASONS) != WAVE8_RAJPUTS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reasons are incomplete")
    if any(
        item["field"] != "geometry" or len(item["raw_point"]) != 2
        for item in WAVE8_RAJPUTS_LOCATION_QUARANTINE_REASONS.values()
    ):
        raise ValueError(f"{_LANE_NAME} location reason drifted")

    if (
        WAVE8_RAJPUTS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_RAJPUTS_HCED_DUPLICATE_DISPOSITIONS
        or WAVE8_RAJPUTS_CROSS_LANE_DISPOSITIONS
        or WAVE8_RAJPUTS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} acquired an unreviewed duplicate")
    if set(WAVE8_RAJPUTS_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_RAJPUTS_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for item in WAVE8_RAJPUTS_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(item["aliases"]) or any(
            alias != normalize_label(alias) for alias in item["aliases"]
        ):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if tuple(item["years"]) != tuple(sorted(set(map(int, item["years"])))):
            raise ValueError(f"{_LANE_NAME} duplicate years are not canonical")

    if set(WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS) != WAVE8_RAJPUTS_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} integration dispositions are incomplete")
    if sum(
        item["sole_blocker_label"] == "rajputs"
        for item in WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS.values()
    ) != 4:
        raise ValueError(f"{_LANE_NAME} sole-blocker count drifted")
    for candidate_id, item in WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS.items():
        if item["disposition"] != WAVE8_RAJPUTS_ROW_DISPOSITIONS[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row disposition drifted")


def _is_exact_rajputs_label(value: Any) -> bool:
    return normalize_label(value) == "rajputs"


def validate_wave8_rajputs_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all and only the seven exact-label rows and their raw hashes."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_RAJPUTS_CONTRACTS,
        WAVE8_RAJPUTS_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_rajputs_label(row.get("side_1_raw"))
        or _is_exact_rajputs_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_RAJPUTS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Rajputs inventory changed: {sorted(exact_ids)}"
        )
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_RAJPUTS_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_rajputs_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    """Fail closed if the authoritative seven-row/four-sole-blocker scope moves."""

    _validate_static()
    label_rows = [
        item
        for item in funnel.get("labels", [])
        if normalize_label(item.get("label")) == "rajputs"
    ]
    if len(label_rows) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one Rajputs funnel summary, found {len(label_rows)}"
        )
    actual_summary = {
        key: label_rows[0].get(key) for key in WAVE8_RAJPUTS_FUNNEL_SUMMARY
    }
    if actual_summary != WAVE8_RAJPUTS_FUNNEL_SUMMARY:
        raise ValueError(f"{_LANE_NAME} Rajputs funnel summary changed")

    greedy = funnel.get("greedy_batch")
    ranking = greedy.get("ranking") if isinstance(greedy, Mapping) else None
    if not isinstance(ranking, list):
        raise ValueError(f"{_LANE_NAME} funnel greedy ranking is unavailable")
    ranked = [
        item for item in ranking if normalize_label(item.get("label")) == "rajputs"
    ]
    if len(ranked) != 1:
        raise ValueError(f"{_LANE_NAME} expected one Rajputs greedy row")
    actual_greedy = {
        key: ranked[0].get(key) for key in WAVE8_RAJPUTS_GREEDY_AUDIT
    }
    if actual_greedy != WAVE8_RAJPUTS_GREEDY_AUDIT:
        raise ValueError(f"{_LANE_NAME} greedy sole-blocker audit changed")

    scoped = {
        str(row.get("candidate_id")): row
        for row in funnel.get("row_label_data", [])
        if "rajputs" in list(map(str, row.get("blocker_labels", [])))
    }
    if set(scoped) != WAVE8_RAJPUTS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact funnel cohort changed: {sorted(scoped)}")
    expected_failure = {
        "candidate_ids": [],
        "failure_case": "zero_time_valid_candidates",
        "label": "rajputs",
        "time_valid_candidate_ids": [],
    }
    for candidate_id, row in scoped.items():
        labels, eligible, sole, other, counterparts = _FUNNEL_SCOPE[candidate_id]
        actual = (
            tuple(map(str, row.get("blocker_labels", []))),
            bool(row.get("greedy_eligible")),
            row.get("sole_blocker_label"),
            tuple(map(str, row.get("other_blockers", []))),
            tuple(map(str, row.get("resolved_counterpart_entity_ids", []))),
        )
        if actual != (labels, eligible, sole, other, counterparts):
            raise ValueError(f"{_LANE_NAME} funnel row changed for {candidate_id}")
        failures = [
            item
            for item in row.get("label_failures", [])
            if normalize_label(item.get("label")) == "rajputs"
        ]
        if failures != [expected_failure]:
            raise ValueError(f"{_LANE_NAME} label failure changed for {candidate_id}")
    return {
        "events_touched": len(scoped),
        "greedy_eligible_rows": sum(bool(row["greedy_eligible"]) for row in scoped.values()),
        "sole_blocker_promotions": sum(
            candidate_id in WAVE8_RAJPUTS_CONTRACT_IDS
            and row.get("sole_blocker_label") == "rajputs"
            for candidate_id, row in scoped.items()
        ),
        "sole_blocker_rows": sum(
            row.get("sole_blocker_label") == "rajputs" for row in scoped.values()
        ),
    }


def _year_from_value(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    match = re.search(r"(?<!\d)(-?\d{1,4})(?!\d)", str(value or ""))
    return int(match.group(1)) if match else None


def _row_year_range(row: Mapping[str, Any]) -> tuple[int, int] | None:
    if row.get("year_low") is not None:
        low = int(row["year_low"])
        high = int(row.get("year_high", low))
        return low, high
    if row.get("year_best") is not None:
        low = int(row["year_best"])
        return low, low
    if row.get("year") is not None:
        low = int(row["year"])
        high = int(row.get("end_year", low))
        return low, high
    low = _year_from_value(row.get("start_date"))
    high = _year_from_value(row.get("end_date"))
    if low is None and high is None:
        return None
    return low if low is not None else high, high if high is not None else low


def _normalized_event_names(row: Mapping[str, Any]) -> set[str]:
    values = [row.get("name"), row.get("event_name")]
    aliases = row.get("aliases", [])
    if isinstance(aliases, list):
        values.extend(aliases)
    return {normalize_label(value) for value in values if normalize_label(value)}


def _duplicate_match(
    row: Mapping[str, Any],
) -> tuple[str, str] | None:
    year_range = _row_year_range(row)
    if year_range is None:
        return None
    low, high = year_range
    names = _normalized_event_names(row)
    for candidate_id, audit in WAVE8_RAJPUTS_IWBD_ZERO_OVERLAP_AUDIT.items():
        aliases = set(map(str, audit["aliases"]))
        if names & aliases and any(low <= int(year) <= high for year in audit["years"]):
            return candidate_id, sorted(names & aliases)[0]
    return None


def validate_wave8_rajputs_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin zero duplicate findings and fail on any future plausible event twin."""

    validate_wave8_rajputs_queue_contracts(hced_rows)
    for row in hced_rows:
        if str(row.get("candidate_id")) in WAVE8_RAJPUTS_RESERVED_IDS:
            continue
        match = _duplicate_match(row)
        if match is not None:
            raise ValueError(
                f"{_LANE_NAME} found unreviewed cross-lane HCED twin "
                f"{row.get('candidate_id')} for {match[0]}"
            )
    for row in iwbd_rows:
        match = _duplicate_match(row)
        if match is not None:
            raise ValueError(
                f"{_LANE_NAME} found probable IWBD duplicate "
                f"{row.get('candidate_id')} for {match[0]}"
            )
    for event in existing_events:
        candidate_id = str(event.get("hced_candidate_id") or "")
        if candidate_id in WAVE8_RAJPUTS_RESERVED_IDS:
            raise ValueError(
                f"{_LANE_NAME} candidate ownership collision in release: {candidate_id}"
            )
        match = _duplicate_match(event)
        if match is not None:
            raise ValueError(
                f"{_LANE_NAME} found existing-release twin "
                f"{event.get('id')} for {match[0]}"
            )
    return {
        "cross_lane_hced_dispositions": len(WAVE8_RAJPUTS_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_RAJPUTS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "hced_duplicate_dispositions": len(WAVE8_RAJPUTS_HCED_DUPLICATE_DISPOSITIONS),
        "integration_dispositions": len(WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_RAJPUTS_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_zero_overlap_candidates": len(WAVE8_RAJPUTS_IWBD_ZERO_OVERLAP_AUDIT),
    }


def install_wave8_rajputs_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_RAJPUTS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_rajputs_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_RAJPUTS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_RAJPUTS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_rajputs_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_rajputs_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_RAJPUTS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_rajputs_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_RAJPUTS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_rajputs_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_RAJPUTS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(WAVE8_RAJPUTS_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_RAJPUTS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "greedy_eligible_rows": sum(
            bool(item["greedy_eligible"])
            for item in WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS.values()
        ),
        "hced_duplicate_dispositions": len(WAVE8_RAJPUTS_HCED_DUPLICATE_DISPOSITIONS),
        "holds": len(WAVE8_RAJPUTS_HOLDS),
        "integration_dispositions": len(WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_RAJPUTS_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_zero_overlap_candidates": len(WAVE8_RAJPUTS_IWBD_ZERO_OVERLAP_AUDIT),
        "new_entities": len(WAVE8_RAJPUTS_ENTITIES),
        "new_sources": len(WAVE8_RAJPUTS_SOURCES),
        "newly_rated_events": len(WAVE8_RAJPUTS_CONTRACTS),
        "outcome_overrides": len(WAVE8_RAJPUTS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_RAJPUTS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_RAJPUTS_RESERVED_IDS),
        "sole_blocker_promotions": sum(
            candidate_id in WAVE8_RAJPUTS_CONTRACT_IDS
            and item["sole_blocker_label"] == "rajputs"
            for candidate_id, item in WAVE8_RAJPUTS_INTEGRATION_DISPOSITIONS.items()
        ),
        "sole_blocker_rows": len(_SOLE_BLOCKER_IDS),
        "terminal_exclusions": len(WAVE8_RAJPUTS_TERMINAL_EXCLUSIONS),
    }


def wave8_rajputs_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return local promoted-only quarantine additions for later integration."""

    _validate_static()
    return {
        "country": WAVE8_RAJPUTS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_RAJPUTS_POINT_QUARANTINE_ADDITIONS,
    }
