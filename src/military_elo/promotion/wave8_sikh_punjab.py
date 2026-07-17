"""Candidate-keyed Wave 8 audit for HCED's exact ``Sikh Punjab`` label.

The locked cohort contains five rows spanning 1634--1846.  ``Sikh Punjab``
is not treated as one continuous polity: Guru Hargobind's Akal Sena, Banda
Singh Bahadur's besieged force, the late-eighteenth-century misl coalition,
and the Lahore Khalsa field army are separate military actors.  Their ratings
never bridge one another, the Sikh Empire, a modern state, or a religious or
ethnic community.

Four source-supported tactical outcomes are promoted.  Anandpur 1701 stays
held: reputable chronologies divide and date the nearby 1700--1701 Anandpur,
Nirmoh, and Basoli operations differently, while the locked row supplies no
event boundary capable of selecting one result.  That uncertainty is not a
draw.  All promoted points are withheld as unaudited locality centroids.  The
Gujrat 1797 country assertion is also withheld because the event and staged
coordinate are in present-day Pakistan while HCED says India.
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
    "WAVE8_SIKH_PUNJAB_CONTRACT_IDS",
    "WAVE8_SIKH_PUNJAB_CONTRACTS",
    "WAVE8_SIKH_PUNJAB_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS",
    "WAVE8_SIKH_PUNJAB_ENTITIES",
    "WAVE8_SIKH_PUNJAB_EXCLUSION_IDS",
    "WAVE8_SIKH_PUNJAB_EXCLUSIONS",
    "WAVE8_SIKH_PUNJAB_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_SIKH_PUNJAB_EXPECTED_CANDIDATE_IDS",
    "WAVE8_SIKH_PUNJAB_EXTERNAL_OWNER_DISPOSITIONS",
    "WAVE8_SIKH_PUNJAB_EXTERNAL_OWNER_IDS",
    "WAVE8_SIKH_PUNJAB_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SIKH_PUNJAB_HOLD_IDS",
    "WAVE8_SIKH_PUNJAB_HOLDS",
    "WAVE8_SIKH_PUNJAB_INTEGRATION_DISPOSITIONS",
    "WAVE8_SIKH_PUNJAB_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_SIKH_PUNJAB_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_SIKH_PUNJAB_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_SIKH_PUNJAB_LOCATION_QUARANTINE_REASONS",
    "WAVE8_SIKH_PUNJAB_NONPROMOTIONS",
    "WAVE8_SIKH_PUNJAB_OUTCOME_OVERRIDES",
    "WAVE8_SIKH_PUNJAB_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SIKH_PUNJAB_RESERVED_IDS",
    "WAVE8_SIKH_PUNJAB_ROW_HASHES",
    "WAVE8_SIKH_PUNJAB_SOURCES",
    "WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSION_IDS",
    "WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS",
    "install_wave8_sikh_punjab_entities",
    "install_wave8_sikh_punjab_sources",
    "promote_wave8_sikh_punjab_contracts",
    "validate_wave8_sikh_punjab_integration_dispositions",
    "validate_wave8_sikh_punjab_queue_contracts",
    "wave8_sikh_punjab_audit_signature",
    "wave8_sikh_punjab_cohort_counts",
    "wave8_sikh_punjab_counts",
    "wave8_sikh_punjab_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Sikh Punjab actor audit"
_EVENT_ID_PREFIX = "hced_wave8_sikh_punjab_"
_MODULE_OWNER = "military_elo.promotion.wave8_sikh_punjab"
_ANANDPUR_1700_CANDIDATE_ID = "hced-Anandpur1700-1"
_ANANDPUR_1700_ROW_SHA256 = (
    "3f992b5f13d444a3178aab638c90b8a7fd465615d6b8c6cc9f1fa95bf6146590"
)


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = True,
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


WAVE8_SIKH_PUNJAB_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_sikh_punjab_routledge_hargobind",
        "The Routledge Companion to the Life and Legacy of Guru Hargobind",
        (
            "https://www.routledge.com/The-Routledge-Companion-to-the-Life-and-"
            "Legacy-of-Guru-Hargobind-Sovereignty-Militancy-and-Empowerment-of-"
            "the-Sikh-Panth/Singh/p/book/9781032827421"
        ),
        "Routledge",
        "scholarly_companion",
        "pashaura_singh_routledge_hargobind",
    ),
    _source(
        "wave8_sikh_punjab_gupta_vol1",
        "History of the Sikhs, Volume I: The Sikh Gurus (1469-1708)",
        "https://apnaorg.com/books/english/history-of-sikhs-v1/history-of-sikhs-v1.pdf",
        "Munshiram Manoharlal Publishers",
        "scholarly_historical_monograph",
        "hari_ram_gupta_history_sikhs_vol1",
    ),
    _source(
        "wave8_sikh_punjab_eos_anandpur",
        "Anandpur",
        (
            "https://eos.learnpunjabi.org/ANANDPUR%20%2831%C2%BA-13%27N%2C%20"
            "76%C2%BA-32%27E%29.html"
        ),
        "Encyclopaedia of Sikhism, Punjabi University",
        "academic_encyclopedia_entry",
        "punjabi_university_encyclopaedia_anandpur",
        outcome=False,
    ),
    _source(
        "wave8_sikh_punjab_shah_sri_gursobha",
        "In Praise of the Guru: A Translation and Study of Sainapati's Sri Gursobha",
        (
            "https://www.gurmatveechar.com/books/English_Books/English_Thesis_Papers/"
            "In.Praise.of.the.Guru.A.Translation.and.Study.of.Sainapatis.Sri.Gursobha."
            "by.Ami.Praful.Shah.%28GurmatVeechar.com%29.pdf"
        ),
        "University of California, Santa Barbara",
        "doctoral_dissertation_and_primary_text_translation",
        "ami_praful_shah_sri_gursobha",
        outcome=False,
    ),
    _source(
        "wave8_sikh_punjab_eos_ram_singh_bedi",
        "Ram Singh Bedi, Baba (d. 1797)",
        (
            "https://eos.learnpunjabi.org/RAM%20SINGH%20BEDI%20BABA%20"
            "%28D.%201797%29.html"
        ),
        "Encyclopaedia of Sikhism, Punjabi University",
        "academic_encyclopedia_entry",
        "punjabi_university_encyclopaedia_ram_singh_bedi",
    ),
    _source(
        "wave8_sikh_punjab_smith_autobiography",
        "The Autobiography of Lieutenant-General Sir Harry Smith",
        "https://www.gutenberg.org/cache/epub/57094/pg57094-images.html",
        "John Murray; Project Gutenberg transcription",
        "edited_primary_military_memoir",
        "harry_smith_autobiography_1903",
    ),
    _source(
        "wave8_sikh_punjab_oxford_vol2",
        "A History of the Sikhs, Volume 2: 1839-2004",
        "https://academic.oup.com/book/40079",
        "Oxford University Press",
        "scholarly_historical_monograph",
        "khushwant_singh_history_sikhs_vol2",
    ),
    _source(
        "wave8_sikh_punjab_nam_aliwal",
        "Battle of Aliwal",
        "https://www.nam.ac.uk/explore/battle-aliwal",
        "National Army Museum",
        "national_military_museum_history",
        "national_army_museum_aliwal",
        outcome=False,
    ),
    _source(
        "wave8_sikh_punjab_gupta_vol4",
        "History of the Sikhs, Volume IV: The Sikh Commonwealth",
        "https://apnaorg.com/books/english/history-of-sikhs-v4/history-of-sikhs-v4.pdf",
        "Munshiram Manoharlal Publishers",
        "scholarly_historical_monograph",
        "hari_ram_gupta_history_sikhs_vol4",
    ),
    _source(
        "wave8_sikh_punjab_ajmer_singh_thesis",
        "Military Campaigns of Maharaja Ranjit Singh and Under His Successors",
        (
            "https://gurmatveechar.com/books/English_Books/English_Thesis_Papers/"
            "Military.campaigns.of.Maharaja.Ranjit.Singh.and.under.his.successors."
            "%28GurmatVeechar.com%29.pdf"
        ),
        "Panjab University Chandigarh",
        "doctoral_dissertation",
        "ajmer_singh_military_campaigns_thesis_1997",
    ),
    _source(
        "wave8_sikh_punjab_gupta_vol2",
        "History of the Sikhs, Volume II: Evolution of Sikh Confederacies",
        "https://apnaorg.com/books/english/history-of-sikhs-v2/history-of-sikhs-v2.pdf",
        "Munshiram Manoharlal Publishers",
        "scholarly_historical_monograph",
        "hari_ram_gupta_history_sikhs_vol2",
    ),
    _source(
        "wave8_sikh_punjab_ibratnamah",
        "Ibratnamah 2",
        "https://eos.learnpunjabi.org/IBRATNAMAH%202.html",
        "Encyclopaedia of Sikhism, Punjabi University",
        "academic_encyclopedia_of_contemporary_persian_source",
        "mirza_muhammad_harisi_ibratnamah",
    ),
    _source(
        "wave8_sikh_punjab_oxford_banda",
        "The Rise and Fall of Banda Bahadur",
        "https://academic.oup.com/book/25977/chapter-abstract/193789599",
        "Oxford University Press",
        "scholarly_historical_monograph_chapter",
        "khushwant_singh_banda_bahadur_chapter",
    ),
)


_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_SIKH_PUNJAB_SOURCES
}
_SOURCE_FAMILY_BY_ID = {
    source_id: str(source["source_family_id"])
    for source_id, source in _SOURCE_BY_ID.items()
}


_AMRITSAR_SIKH_ID = "guru_hargobind_akal_sena_amritsar_1634"
_AMRITSAR_MUGHAL_ID = "mukhlis_khan_mughal_expedition_amritsar_1634"
_BADDOWAL_SIKH_ID = "ranjodh_ajit_khalsa_field_force_baddowal_1846"
_BADDOWAL_BRITISH_INDIAN_ID = (
    "harry_smith_british_indian_relief_column_baddowal_1846"
)
_GUJRAT_SIKH_ID = "ram_singh_bedi_sikh_misl_coalition_gujrat_1797"
_GUJRAT_DURRANI_ID = "shahanchibashi_durrani_field_force_gujrat_1797"
_GURDAS_MUGHAL_ID = "mughal_imperial_siege_coalition_gurdas_nangal_1715"
_GURDAS_SIKH_ID = "banda_singh_sikh_garrison_gurdas_nangal_1715"


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    note: str,
    source_ids: Iterable[str],
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
            note
            + " No rating is inherited by another Sikh formation, a dynasty, "
            "religious or ethnic community, successor polity, or modern state."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_SIKH_PUNJAB_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _AMRITSAR_SIKH_ID,
        "Guru Hargobind's Akal Sena at Amritsar (1634)",
        "event_bounded_sikh_defense_force",
        1634,
        "Amritsar, Punjab",
        "Bounded to Guru Hargobind's armed followers defending near Amritsar.",
        ["wave8_sikh_punjab_gupta_vol1", "wave8_sikh_punjab_routledge_hargobind"],
    ),
    _entity(
        _AMRITSAR_MUGHAL_ID,
        "Mukhlis Khan's Mughal expedition at Amritsar (1634)",
        "event_bounded_imperial_expedition",
        1634,
        "Amritsar, Punjab",
        "Bounded to the Mughal detachment commanded by Mukhlis Khan in this action.",
        ["wave8_sikh_punjab_gupta_vol1", "wave8_sikh_punjab_routledge_hargobind"],
    ),
    _entity(
        _GURDAS_MUGHAL_ID,
        "Mughal imperial siege coalition at Gurdas Nangal (1715)",
        "event_bounded_imperial_siege_coalition",
        1715,
        "Gurdas Nangal, Punjab",
        (
            "Bounded to the Delhi, Lahore, Jammu, Sarhind, and local contingents "
            "that invested and captured the enclosure."
        ),
        [
            "wave8_sikh_punjab_gupta_vol2",
            "wave8_sikh_punjab_ibratnamah",
            "wave8_sikh_punjab_oxford_banda",
        ],
    ),
    _entity(
        _GURDAS_SIKH_ID,
        "Banda Singh Bahadur's Sikh garrison at Gurdas Nangal (1715)",
        "event_bounded_besieged_sikh_force",
        1715,
        "Gurdas Nangal, Punjab",
        "Bounded to Banda Singh Bahadur and the defenders captured after the siege.",
        [
            "wave8_sikh_punjab_gupta_vol2",
            "wave8_sikh_punjab_ibratnamah",
            "wave8_sikh_punjab_oxford_banda",
        ],
    ),
    _entity(
        _GUJRAT_SIKH_ID,
        "Ram Singh Bedi's Sikh misl coalition at Gujrat (1797)",
        "event_bounded_misl_field_coalition",
        1797,
        "Gujrat and Chenab approaches, Punjab",
        "Bounded to the Sikh sardars and volunteers assembled for the Gujrat action.",
        [
            "wave8_sikh_punjab_ajmer_singh_thesis",
            "wave8_sikh_punjab_eos_ram_singh_bedi",
            "wave8_sikh_punjab_gupta_vol4",
        ],
    ),
    _entity(
        _GUJRAT_DURRANI_ID,
        "Ahmad Khan Shahanchibashi's Durrani force at Gujrat (1797)",
        "event_bounded_durrani_field_force",
        1797,
        "Gujrat and Chenab approaches, Punjab",
        "Bounded to Shah Zaman's detachment commanded by Ahmad Khan Shahanchibashi.",
        [
            "wave8_sikh_punjab_ajmer_singh_thesis",
            "wave8_sikh_punjab_eos_ram_singh_bedi",
            "wave8_sikh_punjab_gupta_vol4",
        ],
    ),
    _entity(
        _BADDOWAL_SIKH_ID,
        "Ranjodh Singh Majithia-Ajit Singh Khalsa field force at Baddowal (1846)",
        "event_bounded_khalsa_field_force",
        1846,
        "Baddowal-Ludhiana corridor, Punjab",
        "Bounded to the Lahore Khalsa and allied Ladwa force harrying Smith's column.",
        [
            "wave8_sikh_punjab_ajmer_singh_thesis",
            "wave8_sikh_punjab_nam_aliwal",
            "wave8_sikh_punjab_oxford_vol2",
            "wave8_sikh_punjab_smith_autobiography",
        ],
    ),
    _entity(
        _BADDOWAL_BRITISH_INDIAN_ID,
        "Harry Smith's British-Indian relief column at Baddowal (1846)",
        "event_bounded_british_indian_relief_column",
        1846,
        "Baddowal-Ludhiana corridor, Punjab",
        "Bounded to the British-Indian column moving to relieve Ludhiana.",
        [
            "wave8_sikh_punjab_ajmer_singh_thesis",
            "wave8_sikh_punjab_nam_aliwal",
            "wave8_sikh_punjab_oxford_vol2",
            "wave8_sikh_punjab_smith_autobiography",
        ],
    ),
)


WAVE8_SIKH_PUNJAB_ROW_HASHES: dict[str, str] = {
    "hced-Amritsar1634-1": "cdd8d1bbe8184a53ea8e5d9058db7492ea3151b1679c491a30b587aaa46e0be0",
    "hced-Anandpur1701-1": "f67a4c4086cc928cdf58b7e704691a5f593035460d03011d684f5d2e82173e0e",
    "hced-Baddowal1846-1": "afddca7611c520558de29a1c545e089f1efd688ba8e4b84ca56989f8c838e6f4",
    "hced-Gujrat, Pakistan1797-1": "882db3889fa7363e0a8a6eed1a012a0dcfbf13352ac500e59046a82fb7fcffc5",
    "hced-Gurdas Nangal1715-1": "5598e77f7b5c04fb0685fbbb7dfedfda64f84feda3f45e273350373edbe1ce5e",
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str = "year",
    granularity: str = "engagement",
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
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    war_type: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_SIKH_PUNJAB_ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": war_type,
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


WAVE8_SIKH_PUNJAB_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Amritsar1634-1": _contract(
        "hced-Amritsar1634-1",
        _canonical(
            "Battle of Amritsar (1634)",
            1634,
            "14 April 1634",
            date_precision="day",
        ),
        "guru_hargobind_mughal_conflict_1634",
        [_AMRITSAR_SIKH_ID],
        [_AMRITSAR_MUGHAL_ID],
        1,
        ["wave8_sikh_punjab_gupta_vol1", "wave8_sikh_punjab_routledge_hargobind"],
        ["wave8_sikh_punjab_gupta_vol1", "wave8_sikh_punjab_routledge_hargobind"],
        (
            "The 14 April chronology and Mukhlis Khan's defeat are independently "
            "attested. The winner is Guru Hargobind's bounded Akal Sena, not a "
            "timeless Sikh Punjab polity."
        ),
        "anti_imperial_revolt",
        confidence=0.94,
    ),
    "hced-Gurdas Nangal1715-1": _contract(
        "hced-Gurdas Nangal1715-1",
        _canonical(
            "Siege of Gurdas Nangal",
            1715,
            "beginning of April-7 December 1715",
            date_precision="month_to_day_range",
            granularity="siege",
        ),
        "banda_singh_mughal_conflict_1715",
        [_GURDAS_MUGHAL_ID],
        [_GURDAS_SIKH_ID],
        1,
        [
            "wave8_sikh_punjab_gupta_vol2",
            "wave8_sikh_punjab_ibratnamah",
            "wave8_sikh_punjab_oxford_banda",
        ],
        [
            "wave8_sikh_punjab_gupta_vol2",
            "wave8_sikh_punjab_ibratnamah",
            "wave8_sikh_punjab_oxford_banda",
        ],
        (
            "The contract rates the Mughal capture of the fortified enclosure and "
            "Banda Singh's garrison after the prolonged 1715 siege. Later transport "
            "and executions are not encoded as additional outcomes."
        ),
        "anti_imperial_revolt",
        confidence=0.98,
    ),
    "hced-Gujrat, Pakistan1797-1": _contract(
        "hced-Gujrat, Pakistan1797-1",
        _canonical(
            "Battle of Gujrat (1797)",
            1797,
            "three-day battle ending 29 April 1797",
            date_precision="day_range",
        ),
        "sikh_durrani_gujrat_campaign_1797",
        [_GUJRAT_SIKH_ID],
        [_GUJRAT_DURRANI_ID],
        1,
        [
            "wave8_sikh_punjab_ajmer_singh_thesis",
            "wave8_sikh_punjab_eos_ram_singh_bedi",
            "wave8_sikh_punjab_gupta_vol4",
        ],
        [
            "wave8_sikh_punjab_ajmer_singh_thesis",
            "wave8_sikh_punjab_eos_ram_singh_bedi",
            "wave8_sikh_punjab_gupta_vol4",
        ],
        (
            "The first two days ended without a winner; the single three-day "
            "engagement ends with Ram Singh Bedi's assembled Sikh force and allied "
            "misl contingents defeating Ahmad Khan Shahanchibashi's Durrani force. "
            "No interim draw is emitted. The raw India country is wrong for Gujrat "
            "in present-day Pakistan and is withheld."
        ),
        "interstate_limited",
        confidence=0.91,
    ),
    "hced-Baddowal1846-1": _contract(
        "hced-Baddowal1846-1",
        _canonical(
            "Action at Baddowal",
            1846,
            "21 January 1846",
            date_precision="day",
        ),
        "first_anglo_sikh_war_baddowal_1846",
        [_BADDOWAL_SIKH_ID],
        [_BADDOWAL_BRITISH_INDIAN_ID],
        1,
        [
            "wave8_sikh_punjab_ajmer_singh_thesis",
            "wave8_sikh_punjab_nam_aliwal",
            "wave8_sikh_punjab_oxford_vol2",
            "wave8_sikh_punjab_smith_autobiography",
        ],
        [
            "wave8_sikh_punjab_ajmer_singh_thesis",
            "wave8_sikh_punjab_oxford_vol2",
            "wave8_sikh_punjab_smith_autobiography",
        ],
        (
            "The Sikh force harried Smith's moving column, captured baggage and "
            "stores, and imposed the bounded tactical reverse. It is not the later "
            "Aliwal result, and the opposing actor is Smith's British-Indian "
            "column, not the United Kingdom as a timeless national army."
        ),
        "interstate_limited",
        confidence=0.92,
    ),
}


WAVE8_SIKH_PUNJAB_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Anandpur1701-1": {
        "raw_row_sha256": WAVE8_SIKH_PUNJAB_ROW_HASHES["hced-Anandpur1701-1"],
        "canonical_event": _canonical(
            "Anandpur operations (1700-1701 chronology unresolved)",
            1701,
            "1700-1701 in competing chronologies",
            date_precision="year_uncertain",
            granularity="ambiguous_multi_operation_aggregate",
        ),
        "disposition": "hold",
        "hold_category": "ambiguous_event_boundary_date_and_tactical_outcome",
        "terminal_exclusion": False,
        "result_type": "unknown",
        "reviewed_outcome": "unknown",
        "unknown_is_never_draw": True,
        "hold_reason": (
            "The locked name and year cannot uniquely select among the Anandpur "
            "attacks, siege phases, withdrawal, Nirmoh fighting, and return described "
            "across 1700-1701 chronologies. Sources support Sikh tactical successes "
            "inside those operations but differ on the event boundary and enclosing "
            "result. HCED's winner is therefore not promoted and is never converted "
            "to a draw."
        ),
        "evidence_refs": [
            "wave8_sikh_punjab_eos_anandpur",
            "wave8_sikh_punjab_shah_sri_gursobha",
        ],
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "held_hced_owner",
        },
    }
}


WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_SIKH_PUNJAB_EXCLUSIONS = WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS
WAVE8_SIKH_PUNJAB_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_SIKH_PUNJAB_HOLDS,
    **WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS,
}

WAVE8_SIKH_PUNJAB_CONTRACT_IDS = frozenset(WAVE8_SIKH_PUNJAB_CONTRACTS)
WAVE8_SIKH_PUNJAB_HOLD_IDS = frozenset(WAVE8_SIKH_PUNJAB_HOLDS)
WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS
)
WAVE8_SIKH_PUNJAB_EXCLUSION_IDS = WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSION_IDS
WAVE8_SIKH_PUNJAB_RESERVED_IDS = (
    WAVE8_SIKH_PUNJAB_CONTRACT_IDS
    | WAVE8_SIKH_PUNJAB_HOLD_IDS
    | WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSION_IDS
)
WAVE8_SIKH_PUNJAB_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_SIKH_PUNJAB_ROW_HASHES
)


WAVE8_SIKH_PUNJAB_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Amritsar1634-1": {
        "actions": ["withhold_point"],
        "retained_country": "India",
        "reason": (
            "The staged Amritsar city point is not a source-audited battlefield "
            "footprint for the action outside the city."
        ),
    },
    "hced-Baddowal1846-1": {
        "actions": ["withhold_point"],
        "retained_country": "India",
        "reason": (
            "The action followed a moving relief column and rearguard along the "
            "Baddowal-Ludhiana corridor; a village centroid is not the footprint."
        ),
    },
    "hced-Gujrat, Pakistan1797-1": {
        "actions": ["withhold_country", "withhold_point"],
        "retained_country": None,
        "reviewed_country": "Pakistan",
        "reason": (
            "HCED says India although Gujrat and the staged coordinate are in "
            "present-day Pakistan; the multi-day action also ranged across the "
            "approaches to the Chenab rather than one city point."
        ),
    },
    "hced-Gurdas Nangal1715-1": {
        "actions": ["withhold_point"],
        "retained_country": "India",
        "reason": (
            "The locality centroid is not independently established as the exact "
            "fortified enclosure and months-long siege footprint."
        ),
    },
}
WAVE8_SIKH_PUNJAB_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_SIKH_PUNJAB_CONTRACT_IDS
)
WAVE8_SIKH_PUNJAB_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Gujrat, Pakistan1797-1"}
)
WAVE8_SIKH_PUNJAB_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_SIKH_PUNJAB_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_SIKH_PUNJAB_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_SIKH_PUNJAB_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_SIKH_PUNJAB_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_SIKH_PUNJAB_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_SIKH_PUNJAB_EXTERNAL_OWNER_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_SIKH_PUNJAB_EXTERNAL_OWNER_IDS: frozenset[str] = frozenset()
WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    _ANANDPUR_1700_CANDIDATE_ID: {
        "source_dataset": "hced",
        "disposition": "possible_chronology_twin_held",
        "relationship": "possible_same_anandpur_operation_or_adjacent_phase",
        "raw_row_sha256": _ANANDPUR_1700_ROW_SHA256,
        "related_candidate_id": "hced-Anandpur1701-1",
        "reason": (
            "The Punjabi Sikhs row at Anandpur 1700 may represent the same campaign "
            "sequence under a competing chronology. Neither row is emitted until a "
            "unique event boundary and result can be pinned, preventing double rating."
        ),
    }
}
WAVE8_SIKH_PUNJAB_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS,
    **WAVE8_SIKH_PUNJAB_IWBD_DUPLICATE_DISPOSITIONS,
    **WAVE8_SIKH_PUNJAB_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
}


def _duplicate_audit(low: int, high: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": sorted({normalize_label(alias) for alias in aliases}),
        "years": [low, high],
    }


WAVE8_SIKH_PUNJAB_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Amritsar1634-1": _duplicate_audit(
        1634,
        1634,
        "Amritsar",
        "Battle of Amritsar",
        "Battle of Amritsar (1634)",
    ),
    "hced-Anandpur1701-1": _duplicate_audit(
        1700,
        1701,
        "Anandpur",
        "Anandpur operations",
        "Anandpur operations (1700-1701 chronology unresolved)",
        "First siege of Anandpur",
        "Siege of Anandpur",
    ),
    "hced-Baddowal1846-1": _duplicate_audit(
        1846,
        1846,
        "Action at Baddowal",
        "Baddowal",
        "Battle of Baddowal",
        "Battle of Buddowal",
        "Buddowal",
    ),
    "hced-Gujrat, Pakistan1797-1": _duplicate_audit(
        1797,
        1797,
        "Battle of Gujarat",
        "Battle of Gujrat",
        "Battle of Gujrat (1797)",
        "Gujrat",
        "Gujrat, Pakistan",
    ),
    "hced-Gurdas Nangal1715-1": _duplicate_audit(
        1715,
        1715,
        "Battle of Gurdas Nangal",
        "Gurdas Nangal",
        "Gurdaspur Nangal",
        "Siege of Gurdas Nangal",
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_SIKH_PUNJAB_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_SIKH_PUNJAB_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_SIKH_PUNJAB_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_SIKH_PUNJAB_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(
            WAVE8_SIKH_PUNJAB_EXPECTED_CANDIDATE_IDS
        ),
        "holds": WAVE8_SIKH_PUNJAB_HOLDS,
        "integration_dispositions": WAVE8_SIKH_PUNJAB_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_SIKH_PUNJAB_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": WAVE8_SIKH_PUNJAB_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": (
            WAVE8_SIKH_PUNJAB_LOCATION_QUARANTINE_REASONS
        ),
        "outcome_overrides": WAVE8_SIKH_PUNJAB_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_SIKH_PUNJAB_POINT_QUARANTINE_ADDITIONS
        ),
        "row_hashes": WAVE8_SIKH_PUNJAB_ROW_HASHES,
        "sources": WAVE8_SIKH_PUNJAB_SOURCES,
        "terminal_exclusions": WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS,
    }


def wave8_sikh_punjab_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_SIKH_PUNJAB_FINAL_AUDIT_SIGNATURE = (
    "e9ed6765d051daa426bf9de099f4126be176d97457a3a2c7461ceda3a06909cb"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_SIKH_PUNJAB_CONTRACTS),
        len(WAVE8_SIKH_PUNJAB_HOLDS),
        len(WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS),
    ) != (4, 1, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_SIKH_PUNJAB_ENTITIES), len(WAVE8_SIKH_PUNJAB_SOURCES)) != (
        8,
        13,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_SIKH_PUNJAB_RESERVED_IDS != WAVE8_SIKH_PUNJAB_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    dispositions = (
        WAVE8_SIKH_PUNJAB_CONTRACT_IDS,
        WAVE8_SIKH_PUNJAB_HOLD_IDS,
        WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(len(dispositions))
        for j in range(i + 1, len(dispositions))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if (
        wave8_sikh_punjab_audit_signature()
        != WAVE8_SIKH_PUNJAB_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_SIKH_PUNJAB_SOURCES
    }
    if len(source_by_id) != len(WAVE8_SIKH_PUNJAB_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(
        {str(source["source_family_id"]) for source in WAVE8_SIKH_PUNJAB_SOURCES}
    ) != len(WAVE8_SIKH_PUNJAB_SOURCES):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_SIKH_PUNJAB_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_SIKH_PUNJAB_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_SIKH_PUNJAB_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "afghanistan",
        "mughal empire",
        "punjab",
        "sikh empire",
        "sikh punjab",
        "sikhs",
        "united kingdom",
    }
    for entity in WAVE8_SIKH_PUNJAB_ENTITIES:
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity is not event bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern state" not in note:
            raise ValueError(f"{_LANE_NAME} identity permits continuity bridging")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic identity")
        if not str(entity["kind"]).startswith("event_bounded_"):
            raise ValueError(f"{_LANE_NAME} identity is not explicitly bounded")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_SIKH_PUNJAB_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_SIKH_PUNJAB_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["granularity"] not in {"engagement", "siege"}:
            raise ValueError(f"{_LANE_NAME} promoted unsupported granularity")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        participants = set(side_1) | set(side_2)
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not participants <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses a non-bounded identity")
        used_entities.update(participants)
        year = int(canonical["year_low"])
        for entity_id in participants:
            entity = entity_by_id[entity_id]
            if (int(entity["start_year"]), int(entity["end_year"])) != (year, year):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] not in {1, 2}
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        if contract["actor_override"] != "event_bounded_exact_opposing_forces":
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")
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
        if not outcomes or not _is_sorted_unique(outcomes) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if len(outcomes) < 2 or any(
            "outcome" not in source_by_id[item]["evidence_roles"]
            for item in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} lacks direct outcome corroboration")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identities are not exactly consumed")
    hold = WAVE8_SIKH_PUNJAB_HOLDS.get("hced-Anandpur1701-1")
    if hold is None:
        raise ValueError(f"{_LANE_NAME} Anandpur hold disappeared")
    forbidden_hold_fields = {"side_1_entity_ids", "side_2_entity_ids", "winner_side"}
    if forbidden_hold_fields & set(hold):
        raise ValueError(f"{_LANE_NAME} hold contains a rateable side assertion")
    if (
        hold["result_type"] != "unknown"
        or hold["reviewed_outcome"] != "unknown"
        or hold["unknown_is_never_draw"] is not True
        or hold["terminal_exclusion"] is not False
    ):
        raise ValueError(f"{_LANE_NAME} Anandpur uncertainty changed")
    hold_refs = list(map(str, hold["evidence_refs"]))
    if not _is_sorted_unique(hold_refs) or not set(hold_refs) <= set(source_by_id):
        raise ValueError(f"{_LANE_NAME} hold provenance drifted")
    used_sources.update(hold_refs)
    used_sources.update(
        source_id
        for entity in WAVE8_SIKH_PUNJAB_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")

    if WAVE8_SIKH_PUNJAB_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} invented an outcome override")
    if (
        WAVE8_SIKH_PUNJAB_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_SIKH_PUNJAB_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_SIKH_PUNJAB_EXTERNAL_OWNER_DISPOSITIONS
        or WAVE8_SIKH_PUNJAB_EXTERNAL_OWNER_IDS
    ):
        raise ValueError(f"{_LANE_NAME} empty duplicate inventories changed")
    if set(WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS) != {
        _ANANDPUR_1700_CANDIDATE_ID
    }:
        raise ValueError(f"{_LANE_NAME} Anandpur twin audit changed")
    if WAVE8_SIKH_PUNJAB_POINT_QUARANTINE_ADDITIONS != WAVE8_SIKH_PUNJAB_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_SIKH_PUNJAB_COUNTRY_QUARANTINE_ADDITIONS != {
        "hced-Gujrat, Pakistan1797-1"
    }:
        raise ValueError(f"{_LANE_NAME} country quarantine inventory changed")
    if set(WAVE8_SIKH_PUNJAB_LOCATION_QUARANTINE_REASONS) != WAVE8_SIKH_PUNJAB_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    if set(WAVE8_SIKH_PUNJAB_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_SIKH_PUNJAB_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")


def _is_exact_label(value: Any) -> bool:
    return normalize_label(value) == "sikh punjab"


def _rows_by_candidate_id(
    rows: Iterable[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    indexed: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            indexed.setdefault(candidate_id, []).append(row)
    return indexed


def validate_wave8_sikh_punjab_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all five exact-label rows and the adjacent Anandpur twin."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SIKH_PUNJAB_CONTRACTS,
        WAVE8_SIKH_PUNJAB_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_label(row.get("side_1_raw"))
        or _is_exact_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_SIKH_PUNJAB_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Sikh Punjab inventory changed: {sorted(exact_ids)}"
        )
    indexed = _rows_by_candidate_id(hced_rows)
    adjacent = indexed.get(_ANANDPUR_1700_CANDIDATE_ID, [])
    if len(adjacent) != 1:
        raise ValueError(
            f"{_LANE_NAME} adjacent Anandpur twin expected exactly one row, "
            f"found {len(adjacent)}"
        )
    if canonical_hced_row_sha256(adjacent[0]) != _ANANDPUR_1700_ROW_SHA256:
        raise ValueError(f"{_LANE_NAME} adjacent Anandpur twin fingerprint changed")
    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS
        ),
        "holds": len(WAVE8_SIKH_PUNJAB_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS),
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
        value = row.get(field)
        if isinstance(value, str) and len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


_DUPLICATE_MATCH_KEYS = {
    (year, alias)
    for audit in WAVE8_SIKH_PUNJAB_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
}


def validate_wave8_sikh_punjab_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed if another queue or release lane adds an unreviewed twin."""

    validate_wave8_sikh_punjab_queue_contracts(hced_rows)
    allowed_hced = {
        *WAVE8_SIKH_PUNJAB_EXPECTED_CANDIDATE_IDS,
        *WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS,
    }
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in allowed_hced
        and (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if hced_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_matches}")
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
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_SIKH_PUNJAB_CONTRACT_IDS
        and (_row_year(event), normalize_label(event.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_matches}"
        )
    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_SIKH_PUNJAB_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(
            WAVE8_SIKH_PUNJAB_EXTERNAL_OWNER_IDS
        ),
        "integration_dispositions": len(
            WAVE8_SIKH_PUNJAB_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_SIKH_PUNJAB_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_SIKH_PUNJAB_IWBD_ZERO_OVERLAP_AUDIT
        ),
    }


def install_wave8_sikh_punjab_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SIKH_PUNJAB_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_sikh_punjab_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SIKH_PUNJAB_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SIKH_PUNJAB_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SIKH_PUNJAB_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_sikh_punjab_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_sikh_punjab_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SIKH_PUNJAB_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_sikh_punjab_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_SIKH_PUNJAB_CONTRACTS.values()
            ).items()
        )
    )


def wave8_sikh_punjab_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_SIKH_PUNJAB_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_SIKH_PUNJAB_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(
            WAVE8_SIKH_PUNJAB_EXTERNAL_OWNER_IDS
        ),
        "holds": len(WAVE8_SIKH_PUNJAB_HOLDS),
        "integration_dispositions": len(
            WAVE8_SIKH_PUNJAB_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_SIKH_PUNJAB_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_SIKH_PUNJAB_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_SIKH_PUNJAB_ENTITIES),
        "new_sources": len(WAVE8_SIKH_PUNJAB_SOURCES),
        "newly_rated_events": len(WAVE8_SIKH_PUNJAB_CONTRACTS),
        "outcome_overrides": len(WAVE8_SIKH_PUNJAB_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_SIKH_PUNJAB_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_SIKH_PUNJAB_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_SIKH_PUNJAB_EXPECTED_CANDIDATE_IDS),
        "terminal_exclusions": len(
            WAVE8_SIKH_PUNJAB_TERMINAL_EXCLUSIONS
        ),
    }


def wave8_sikh_punjab_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_SIKH_PUNJAB_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_SIKH_PUNJAB_POINT_QUARANTINE_ADDITIONS,
    }


_validate_static()
