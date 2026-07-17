"""Candidate-keyed Wave 8 audit for HCED's ``Mamluk Egypt`` label.

The literal label spans three incompatible actors: the Mamluk Sultanate in
1516-1517, an autonomous Mamluk household regime in 1786, and Murad Bey's
campaign forces in 1798-1799.  This lane promotes only four source-supported
tactical engagements.  It opens no generic alias and inherits no rating across
those boundaries.
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


_LANE_NAME = "Wave 8 Mamluk Egypt exact actors"
_EVENT_ID_PREFIX = "hced_wave8_mamluk_egypt_"
_FRENCH_REPUBLIC_ID = "french_first_republic"
_OTTOMAN_EMPIRE_ID = "ottoman_empire"
_RAHMANIYYA_FORCE_ID = "murad_bey_rahmaniyya_force_1786"
_MURAD_1798_FORCE_ID = "murad_bey_egypt_campaign_force_1798"
_SAMHUD_COALITION_ID = "murad_bey_samhud_coalition_1799"
_FORBIDDEN_BRIDGE_IDS = frozenset(
    {
        "egypt_muhammad_ali",
        "mamluk_egyptian_forces_1798",
        "mamluk_sultanate",
    }
)


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
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_MAMLUK_EGYPT_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_mamluk_egypt_karahan_1786",
        "The Expedition of Grand Admiral Djezairli Ghazi Hasan Pasha to Egypt",
        "https://doi.org/10.16985/MTAD.2017130406",
        "Marmara Türkiyat Araştırmaları Dergisi",
        "peer_reviewed_archival_history",
        "karahan_hasan_pasha_egypt_1786",
        {
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        },
    ),
    _source(
        "wave8_mamluk_egypt_tdv_ibrahim_bey",
        "İbrâhim Bey",
        "https://islamansiklopedisi.org.tr/ibrahim-bey",
        "TDV Encyclopedia of Islam",
        "scholarly_encyclopedia",
        "tdv_islam_encyclopedia_ibrahim_bey",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_mamluk_egypt_berthier_campaign",
        "Mémoires du maréchal Berthier: Campagne d'Égypte, première partie",
        "https://www.gutenberg.org/cache/epub/38737/pg38737-images.html",
        "Project Gutenberg transcription of the BnF/Gallica edition",
        "participant_primary_campaign_account",
        "berthier_egypt_campaign_primary",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_mamluk_egypt_fondation_campaign",
        "La campagne d'Égypte",
        "https://www.napoleon.org/histoire-des-2-empires/articles/la-campagne-degypte/",
        "Fondation Napoléon; Revue du Souvenir Napoléonien 383",
        "institutional_campaign_history",
        "fondation_napoleon_egypt_campaign",
        {"identity_boundary_or_context_reference", "outcome"},
    ),
    _source(
        "wave8_mamluk_egypt_fondation_correspondence",
        "Chronologie de la Correspondance générale de Napoléon Bonaparte, tome 2",
        (
            "https://www.napoleon.org/histoire-des-2-empires/chronologies/"
            "chronologie-de-la-correspondance-generale-de-napoleon-bonaparte-"
            "tome-2-la-campagne-degypte-et-lavenement-1798-1799/"
        ),
        "Fondation Napoléon",
        "edited_primary_correspondence_chronology",
        "napoleon_general_correspondence_chronology_2",
        {"outcome", "outcome_consistency_crosscheck"},
    ),
    _source(
        "wave8_mamluk_egypt_fondation_rapp",
        "Rapp, Jean",
        "https://www.napoleon.org/en/history-of-the-two-empires/biographies/rapp-jean/",
        "Fondation Napoléon",
        "institutional_participant_biography",
        "fondation_napoleon_jean_rapp",
        {"outcome", "outcome_consistency_crosscheck"},
    ),
    _source(
        "wave8_mamluk_egypt_thibaudeau_volume_2",
        "Histoire générale de Napoléon: Guerre d'Égypte, tome second",
        (
            "https://www.mediterranee-antique.fr/Fichiers_PdF/TUV/"
            "Thibaudeau/Guerre_Egypte_2.pdf"
        ),
        "Méditerranée antique; public-domain 1828 edition",
        "near_contemporary_campaign_history",
        "thibaudeau_egypt_campaign_volume_2",
        {
            "identity_boundary_or_context_reference",
            "outcome",
        },
    ),
    _source(
        "wave8_mamluk_egypt_alexandria_portal",
        "Alexandria in the Ottoman Era",
        "https://www.alexandria.gov.eg/alex/english/Ottoman%20Era.html",
        "Alexandria Governorate official portal",
        "official_local_history",
        "alexandria_governorate_ottoman_era",
        {
            "identity_boundary_or_context_reference",
        },
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    source_ids: Iterable[str],
    continuity_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": "Egypt",
        "aliases": [],
        "predecessors": [],
        "continuity_note": continuity_note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_MAMLUK_EGYPT_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _RAHMANIYYA_FORCE_ID,
        "Murad Bey's Rahmaniyya Field Force (1786)",
        "household_field_force",
        1786,
        {
            "wave8_mamluk_egypt_karahan_1786",
            "wave8_mamluk_egypt_tdv_ibrahim_bey",
        },
        (
            "Engagement-bounded force commanded by Murad Bey after his forces "
            "joined the detachments of Laçin and Mustafa Bey near Rahmaniyya. "
            "Ibrahim Bey was Murad's political partner but is not asserted as the "
            "field commander here. No rating is inherited by the Mamluk Sultanate, "
            "Ottoman Egypt, either household in another year, or generic Egypt."
        ),
    ),
    _entity(
        _MURAD_1798_FORCE_ID,
        "Murad Bey's Egyptian Campaign Force (1798)",
        "campaign_force",
        1798,
        {
            "wave8_mamluk_egypt_berthier_campaign",
            "wave8_mamluk_egypt_fondation_campaign",
            "wave8_mamluk_egypt_thibaudeau_volume_2",
        },
        (
            "Year-bounded field command of Murad Bey at Shubra Khit and Sediman, "
            "including his Mamluk cavalry and the attached infantry, river, and "
            "tribal components attested for those actions. It does not widen or "
            "reuse the committed Pyramids-only identity. No rating is inherited "
            "by the Mamluk Sultanate, Ottoman Egypt, a later Murad Bey coalition, "
            "or generic Egypt."
        ),
    ),
    _entity(
        _SAMHUD_COALITION_ID,
        "Murad Bey's Samhud Coalition (1799)",
        "engagement_coalition",
        1799,
        {
            "wave8_mamluk_egypt_fondation_campaign",
            "wave8_mamluk_egypt_fondation_correspondence",
            "wave8_mamluk_egypt_thibaudeau_volume_2",
        },
        (
            "Engagement-bounded coalition at Samhud: Murad Bey's Mamluks, Hassan "
            "Bey's contingent, infantry from Yanbu/Mecca, and allied Arab forces. "
            "The coalition is not reduced to a generic Mamluk or Egyptian polity. "
            "No rating is inherited from the 1798 campaign force, by Ottoman "
            "Egypt, by the Mamluk Sultanate, or by generic Egypt."
        ),
    ),
)


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": "engagement",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


_ROW_HASHES = {
    "hced-Alexandria1798-1": (
        "9e6416b28654cf8894fd1af4fdbfe597eca128709375e06b6d6d50df33f66386"
    ),
    "hced-Er Ridisiya1799-1": (
        "f685fa5a0156beeadb7a5012ca429bdb3ad89b5afd93dfe732dbc9c7035d4363"
    ),
    "hced-Marj Dabik1516-1": (
        "0eb60113f47e6f8f89cf6f4d7c016e1fc6c35cbe80efc459d9a871d31cfb2fc6"
    ),
    "hced-Mount Tabor1799-1": (
        "3a01784e5f849b2e5bc53f3943f6150f59f8f9d572415c1d370bbb7de102fa2a"
    ),
    "hced-Rahmaniyya1786-1": (
        "460d690c31cc52c7743bbb8e112e8048df1d72ac07f53175bfd53c921ab065db"
    ),
    "hced-Ridanieh1517-1": (
        "260940e4918a9eb6c58cf7167e21ab665751a0668678db421abba26ef30072f7"
    ),
    "hced-Samhud1799-1": (
        "7ec8600f16e89fd6efbbbffacf2663e272fa7a2d6ee1c5663e8f8daee9693b2d"
    ),
    "hced-Sediman1798-1": (
        "d51eabdd58fb3cd1293e8d320590eaee927fe5a007abc7c49ff518366741812f"
    ),
    "hced-Shubra Khit1798-1": (
        "6dc896a596bc505f61b01a80a5880f0e1e1cab683feafbf436b75baea7f37120"
    ),
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: list[str],
    side_2_entity_ids: list[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    war_type: str,
) -> dict[str, Any]:
    source_by_id = {
        str(source["id"]): source for source in WAVE8_MAMLUK_EGYPT_SOURCES
    }
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": side_1_entity_ids,
        "side_2_entity_ids": side_2_entity_ids,
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(source_by_id[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "actor_override": True,
        "audit_note": audit_note,
    }


WAVE8_MAMLUK_EGYPT_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Rahmaniyya1786-1": _contract(
        "hced-Rahmaniyya1786-1",
        _canonical(
            "Battle of Rahmaniyya",
            1786,
            "1786 (the reviewed sources do not securely identify a day)",
            date_precision="year",
        ),
        "ottoman_rahmaniyya_1786",
        [_OTTOMAN_EMPIRE_ID],
        [_RAHMANIYYA_FORCE_ID],
        {
            "wave8_mamluk_egypt_karahan_1786",
            "wave8_mamluk_egypt_tdv_ibrahim_bey",
        },
        (
            "Hasan Pasha's Ottoman expedition defeated Murad Bey after Murad "
            "joined the Rahmaniyya detachments. The loser is the exact field "
            "force, not the extinct sultanate or a continuous Egyptian state."
        ),
        confidence=0.89,
        war_type="internal_rebellion",
    ),
    "hced-Shubra Khit1798-1": _contract(
        "hced-Shubra Khit1798-1",
        _canonical(
            "Battle of Shubra Khit",
            1798,
            "13-14 July 1798 (source chronologies differ by one day)",
            date_precision="day_conflict",
        ),
        "murad_bey_campaign_1798",
        [_FRENCH_REPUBLIC_ID],
        [_MURAD_1798_FORCE_ID],
        {
            "wave8_mamluk_egypt_berthier_campaign",
            "wave8_mamluk_egypt_fondation_campaign",
            "wave8_mamluk_egypt_fondation_correspondence",
        },
        (
            "Bonaparte's army and Nile flotilla defeated Murad Bey's field and "
            "river force. The 13/14 July chronology conflict is preserved rather "
            "than resolved by invention; the staged Cairo point is quarantined."
        ),
        confidence=0.91,
        war_type="colonial_anti_colonial",
    ),
    "hced-Sediman1798-1": _contract(
        "hced-Sediman1798-1",
        _canonical(
            "Battle of Sediman",
            1798,
            "7-8 October 1798 (source chronologies differ by one day)",
            date_precision="day_conflict",
        ),
        "murad_bey_campaign_1798",
        [_FRENCH_REPUBLIC_ID],
        [_MURAD_1798_FORCE_ID],
        {
            "wave8_mamluk_egypt_fondation_rapp",
            "wave8_mamluk_egypt_thibaudeau_volume_2",
        },
        (
            "Desaix's French force defeated Murad Bey's Mamluk, Arab, and fellah "
            "field force. Thibaudeau gives 7 October while the Fondation "
            "Napoléon Rapp biography gives 8 October, so the conflict is explicit."
        ),
        confidence=0.92,
        war_type="colonial_anti_colonial",
    ),
    "hced-Samhud1799-1": _contract(
        "hced-Samhud1799-1",
        _canonical(
            "Battle of Samhud",
            1799,
            "22 January 1799",
            date_precision="day",
        ),
        "murad_bey_samhud_coalition_1799",
        [_FRENCH_REPUBLIC_ID],
        [_SAMHUD_COALITION_ID],
        {
            "wave8_mamluk_egypt_fondation_campaign",
            "wave8_mamluk_egypt_fondation_correspondence",
            "wave8_mamluk_egypt_fondation_rapp",
            "wave8_mamluk_egypt_thibaudeau_volume_2",
        },
        (
            "Desaix defeated the composite coalition of Murad Bey's Mamluks, "
            "Hassan Bey's contingent, Yanbu/Meccan infantry, and allied Arabs. "
            "The full opposing coalition is rated as one engagement actor."
        ),
        confidence=0.94,
        war_type="colonial_anti_colonial",
    ),
}


def _exclusion(
    candidate_id: str,
    canonical_event: dict[str, Any],
    hold_category: str,
    hold_reason: str,
    evidence_refs: Iterable[str],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "hold_category": hold_category,
        "hold_reason": hold_reason,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
    }


WAVE8_MAMLUK_EGYPT_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Alexandria1798-1": _exclusion(
        "hced-Alexandria1798-1",
        _canonical(
            "Capture of Alexandria",
            1798,
            "2 July 1798",
            date_precision="day",
        ),
        "terminal_exclusion_wrong_actor",
        (
            "The French captured Alexandria, but the defenders were the local "
            "Ottoman-era garrison and inhabitants led by governor Muhammad Karim, "
            "not Murad Bey's Mamluk field force. This terminally excludes the "
            "HCED Mamluk-Egypt assertion; it does not deny that a separately "
            "curated Alexandria-defenders event could be reviewed later."
        ),
        {"wave8_mamluk_egypt_alexandria_portal"},
    ),
    "hced-Er Ridisiya1799-1": _exclusion(
        "hced-Er Ridisiya1799-1",
        _canonical(
            "Belliard's pursuit toward Redesieh",
            1799,
            "1799 (no separately attested competitive engagement)",
            date_precision="year",
        ),
        "terminal_exclusion_noncompetitive_pursuit_attrition",
        (
            "Thibaudeau states that Belliard did not catch the Mamluks; losses "
            "on the desert route were horses, camels, servants, and women. A "
            "French tactical victory is therefore not rated, and the unknown "
            "competitive outcome is not converted into a draw."
        ),
        {"wave8_mamluk_egypt_thibaudeau_volume_2"},
    ),
}

WAVE8_MAMLUK_EGYPT_EXCLUSIONS = WAVE8_MAMLUK_EGYPT_HOLDS


def _release_disposition(
    candidate_id: str,
    event_id: str,
    expected_entity_ids: Iterable[str],
    note: str,
    *,
    disposition: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "disposition": disposition,
        "owner_event_id": event_id,
        "expected_entity_ids": sorted(set(map(str, expected_entity_ids))),
        "note": note,
    }


WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Marj Dabik1516-1": _release_disposition(
        "hced-Marj Dabik1516-1",
        "hced_label_hced_marj_dabik1516_1",
        {_OTTOMAN_EMPIRE_ID, "mamluk_sultanate"},
        (
            "Already rated as the Ottoman conquest battle against the still-"
            "extant, time-bounded Mamluk Sultanate."
        ),
        disposition="existing_release",
    ),
    "hced-Ridanieh1517-1": _release_disposition(
        "hced-Ridanieh1517-1",
        "hced_label_hced_ridanieh1517_1",
        {_OTTOMAN_EMPIRE_ID, "mamluk_sultanate"},
        (
            "Already rated as the Ottoman conquest battle against the still-"
            "extant, time-bounded Mamluk Sultanate."
        ),
        disposition="existing_release",
    ),
}

WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Mount Tabor1799-1": _release_disposition(
        "hced-Mount Tabor1799-1",
        "hced_label_hced_mount_tabor1799_1",
        {_FRENCH_REPUBLIC_ID, _OTTOMAN_EMPIRE_ID},
        (
            "The composite raw label 'Turkey, Mamluk Egypt' is already resolved "
            "to the Ottoman campaign force. No additional Mamluk participant is "
            "invented and the event is not emitted again."
        ),
        disposition="cross_lane_existing_release",
    )
}
WAVE8_MAMLUK_EGYPT_INTEGRATION_DISPOSITIONS = (
    WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS
)

WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_MAMLUK_EGYPT_IWBD_ZERO_OVERLAP_AUDIT: dict[str, tuple[str, ...]] = {
    "1516": ("battle of marj dabiq", "marj dabik", "marj dabiq"),
    "1517": ("battle of ridaniya", "ridanieh", "ridaniya"),
    "1786": ("battle of rahmaniyya", "rahmaniyya"),
    "1798": (
        "alexandria",
        "battle of sediman",
        "battle of shubra khit",
        "capture of alexandria",
        "chebreiss",
        "chobrakhit",
        "sediman",
        "shubra khit",
    ),
    "1799": (
        "battle of samhud",
        "er ridisiya",
        "mount tabor",
        "redecieh",
        "redesieh",
        "samhud",
    ),
}

WAVE8_MAMLUK_EGYPT_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}

WAVE8_MAMLUK_EGYPT_CONTRACT_IDS = frozenset(WAVE8_MAMLUK_EGYPT_CONTRACTS)
WAVE8_MAMLUK_EGYPT_HOLD_IDS = frozenset(WAVE8_MAMLUK_EGYPT_HOLDS)
WAVE8_MAMLUK_EGYPT_TERMINAL_EXCLUSION_IDS = frozenset(
    candidate_id
    for candidate_id, hold in WAVE8_MAMLUK_EGYPT_HOLDS.items()
    if hold.get("terminal_exclusion") is True
)
WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_IDS = frozenset(
    WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS
)
WAVE8_MAMLUK_EGYPT_CROSS_LANE_IDS = frozenset(
    WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS
)
WAVE8_MAMLUK_EGYPT_RESERVED_IDS = (
    WAVE8_MAMLUK_EGYPT_CONTRACT_IDS | WAVE8_MAMLUK_EGYPT_HOLD_IDS
)
WAVE8_MAMLUK_EGYPT_UNRESOLVED_IDS = WAVE8_MAMLUK_EGYPT_RESERVED_IDS
WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS = frozenset(
    {
        "hced-Alexandria1798-1",
        "hced-Er Ridisiya1799-1",
        "hced-Marj Dabik1516-1",
        "hced-Rahmaniyya1786-1",
        "hced-Ridanieh1517-1",
        "hced-Samhud1799-1",
        "hced-Sediman1798-1",
        "hced-Shubra Khit1798-1",
    }
)
WAVE8_MAMLUK_EGYPT_REVIEWED_CANDIDATE_IDS = (
    WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS
    | WAVE8_MAMLUK_EGYPT_CROSS_LANE_IDS
)

WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_MAMLUK_EGYPT_CONTRACT_IDS
)
WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_MAMLUK_EGYPT_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS,
}


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_MAMLUK_EGYPT_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_MAMLUK_EGYPT_ENTITIES,
        "existing_release_dispositions": (
            WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(
            WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS
        ),
        "holds": WAVE8_MAMLUK_EGYPT_HOLDS,
        "integration_dispositions": WAVE8_MAMLUK_EGYPT_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": WAVE8_MAMLUK_EGYPT_IWBD_ZERO_OVERLAP_AUDIT,
        "outcome_overrides": WAVE8_MAMLUK_EGYPT_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS
        ),
        "reserved_ids": sorted(WAVE8_MAMLUK_EGYPT_RESERVED_IDS),
        "sources": WAVE8_MAMLUK_EGYPT_SOURCES,
    }


def wave8_mamluk_egypt_audit_signature() -> str:
    payload = json.dumps(
        _signature_payload(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# Replaced after the final payload is measured.
WAVE8_MAMLUK_EGYPT_FINAL_AUDIT_SIGNATURE = (
    "79987df466a8b10aed82eb4e147bc39341dccf971708502760f688dc2c8de614"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_MAMLUK_EGYPT_CONTRACTS), len(WAVE8_MAMLUK_EGYPT_HOLDS)) != (
        4,
        2,
    ):
        raise ValueError(f"{_LANE_NAME} unresolved disposition inventory changed")
    if (
        len(WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS),
        len(WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS),
    ) != (2, 1):
        raise ValueError(f"{_LANE_NAME} integration disposition inventory changed")
    if WAVE8_MAMLUK_EGYPT_CONTRACT_IDS & WAVE8_MAMLUK_EGYPT_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotions and exclusions overlap")
    if WAVE8_MAMLUK_EGYPT_RESERVED_IDS != WAVE8_MAMLUK_EGYPT_UNRESOLVED_IDS:
        raise ValueError(f"{_LANE_NAME} unresolved reservation inventory changed")
    if (
        (
            WAVE8_MAMLUK_EGYPT_RESERVED_IDS
            | WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_IDS
        )
        != WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} literal-label inventory is incomplete")
    if WAVE8_MAMLUK_EGYPT_CROSS_LANE_IDS & (
        WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS
        | WAVE8_MAMLUK_EGYPT_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} composite cross-lane row was reserved")
    if WAVE8_MAMLUK_EGYPT_TERMINAL_EXCLUSION_IDS != WAVE8_MAMLUK_EGYPT_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} terminal exclusion inventory changed")
    if wave8_mamluk_egypt_audit_signature() != (
        WAVE8_MAMLUK_EGYPT_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_MAMLUK_EGYPT_SOURCES
    }
    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_MAMLUK_EGYPT_ENTITIES
    }
    if len(source_by_id) != 8 or len(source_by_id) != len(WAVE8_MAMLUK_EGYPT_SOURCES):
        raise ValueError(f"{_LANE_NAME} source inventory changed")
    if len(entity_by_id) != 3 or len(entity_by_id) != len(WAVE8_MAMLUK_EGYPT_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity inventory changed")
    source_families = [
        str(source["source_family_id"]) for source in WAVE8_MAMLUK_EGYPT_SOURCES
    ]
    if len(source_families) != len(set(source_families)):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_MAMLUK_EGYPT_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not stable HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    for entity in WAVE8_MAMLUK_EGYPT_ENTITIES:
        if entity["start_year"] is None or entity["end_year"] is None:
            raise ValueError(f"{_LANE_NAME} identity is not time bounded")
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity exceeds its audited year")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity provenance is not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity cites an unknown source")

    allowed_entities = {
        *entity_by_id,
        _FRENCH_REPUBLIC_ID,
        _OTTOMAN_EMPIRE_ID,
    }
    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_MAMLUK_EGYPT_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} canonical key drifted")
        if canonical["granularity"] != "engagement" or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} promoted a non-engagement")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        participants = side_1 | side_2
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} invalid opposing sides")
        if not participants <= allowed_entities:
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        if participants & _FORBIDDEN_BRIDGE_IDS:
            raise ValueError(f"{_LANE_NAME} bridges an anachronistic identity")
        year = int(canonical["year_low"])
        for entity_id in participants & set(entity_by_id):
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
            used_entities.add(entity_id)
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or evidence != outcomes:
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if len(outcomes) < 2 or not set(outcomes) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} lacks direct outcome corroboration")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} cites a non-outcome source as outcome")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")
    for hold in WAVE8_MAMLUK_EGYPT_HOLDS.values():
        forbidden = {
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
        }
        if forbidden & set(hold):
            raise ValueError(f"{_LANE_NAME} exclusion contains a rateable result")
        if (
            hold["disposition"] != "terminal_exclusion"
            or hold["terminal_exclusion"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} exclusion is not explicit")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} exclusion provenance drifted")
        if any(
            "identity_boundary_or_context_reference"
            not in source_by_id[item]["evidence_roles"]
            for item in evidence
        ):
            raise ValueError(f"{_LANE_NAME} exclusion lacks a direct basis")
        used_sources.update(evidence)
    used_sources.update(
        source_id
        for entity in WAVE8_MAMLUK_EGYPT_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")

    if WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_MAMLUK_EGYPT_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate disposition changed")
    if WAVE8_MAMLUK_EGYPT_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} invented an outcome override")


def _rows_by_candidate_id(
    rows: Iterable[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            indexed.setdefault(candidate_id, []).append(row)
    return indexed


def _validate_pinned_queue_rows(
    indexed: Mapping[str, list[dict[str, Any]]],
    dispositions: Mapping[str, Mapping[str, Any]],
    *,
    disposition_name: str,
) -> None:
    for candidate_id, disposition in dispositions.items():
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} {disposition_name} {candidate_id} expected exactly "
                f"one queue row, found {len(rows)}"
            )
        actual = canonical_hced_row_sha256(rows[0])
        expected = str(disposition["raw_row_sha256"])
        if actual != expected:
            raise ValueError(
                f"{_LANE_NAME} {disposition_name} {candidate_id} raw-row "
                f"fingerprint changed ({actual} != {expected})"
            )


def validate_wave8_mamluk_egypt_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate six unresolved rows, two existing rows, and one cross-lane row."""

    _validate_static()
    unresolved = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_MAMLUK_EGYPT_CONTRACTS,
        WAVE8_MAMLUK_EGYPT_HOLDS,
        lane_name=_LANE_NAME,
    )
    indexed = _rows_by_candidate_id(hced_rows)
    _validate_pinned_queue_rows(
        indexed,
        WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS,
        disposition_name="existing-release",
    )
    _validate_pinned_queue_rows(
        indexed,
        WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS,
        disposition_name="cross-lane",
    )
    literal_label_ids = {
        str(row["candidate_id"])
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == "mamluk egypt"
        or normalize_label(row.get("side_2_raw")) == "mamluk egypt"
    }
    if literal_label_ids != WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact-label inventory changed: "
            f"{sorted(literal_label_ids)}"
        )
    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_dispositions": len(
            WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS
        ),
        "holds": unresolved["holds"],
        "promotion_contracts": unresolved["promotion_contracts"],
        "reviewed_exact_label_rows": len(
            WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS
        ),
        "reviewed_hced_rows": len(WAVE8_MAMLUK_EGYPT_REVIEWED_CANDIDATE_IDS),
        "unresolved_exact_label_rows": len(WAVE8_MAMLUK_EGYPT_RESERVED_IDS),
    }


def _iwbd_year(row: Mapping[str, Any]) -> int | None:
    for field in ("start_date", "end_date"):
        value = row.get(field)
        if isinstance(value, str) and len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    try:
        return int(row["year"]) if row.get("year") is not None else None
    except (TypeError, ValueError):
        return None


def _event_entity_ids(event: Mapping[str, Any]) -> set[str]:
    return {
        str(participant["entity_id"])
        for participant in event.get("participants", [])
        if isinstance(participant, Mapping) and participant.get("entity_id") is not None
    }


def validate_wave8_mamluk_egypt_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin existing HCED owners and fail on a future probable IWBD twin."""

    validate_wave8_mamluk_egypt_queue_contracts(hced_rows)
    events = list(existing_events)
    dispositions = {
        **WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS,
        **WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS,
    }
    for candidate_id, disposition in dispositions.items():
        matches = [
            event
            for event in events
            if event.get("hced_candidate_id") == candidate_id
        ]
        if len(matches) != 1:
            raise ValueError(
                f"{_LANE_NAME} existing-release disposition {candidate_id} "
                f"expected exactly one event, found {len(matches)}"
            )
        event = matches[0]
        if str(event.get("id") or "") != disposition["owner_event_id"]:
            raise ValueError(
                f"{_LANE_NAME} existing-release owner changed for {candidate_id}"
            )
        if _event_entity_ids(event) != set(disposition["expected_entity_ids"]):
            raise ValueError(
                f"{_LANE_NAME} existing-release participants changed for "
                f"{candidate_id}"
            )

    audited = {
        (int(year), normalize_label(name))
        for year, names in WAVE8_MAMLUK_EGYPT_IWBD_ZERO_OVERLAP_AUDIT.items()
        for name in names
    }
    collisions = []
    for row in iwbd_rows:
        year = _iwbd_year(row)
        if year is not None and (year, normalize_label(row.get("name"))) in audited:
            collisions.append(str(row.get("candidate_id") or "<missing-id>"))
    if collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): "
            f"{sorted(collisions)}"
        )
    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_dispositions": len(
            WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS
        ),
        "integration_dispositions": len(
            WAVE8_MAMLUK_EGYPT_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
    }


def install_wave8_mamluk_egypt_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_MAMLUK_EGYPT_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_mamluk_egypt_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_MAMLUK_EGYPT_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_mamluk_egypt_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit the four exact tactical events; exclusions never reach the ledger."""

    validate_wave8_mamluk_egypt_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_MAMLUK_EGYPT_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_mamluk_egypt_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_MAMLUK_EGYPT_CONTRACTS.values()
            ).items()
        )
    )


def wave8_mamluk_egypt_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS
        ),
        "exact_label_rows": len(WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS),
        "existing_release_dispositions": len(
            WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS
        ),
        "holds": len(WAVE8_MAMLUK_EGYPT_HOLDS),
        "integration_dispositions": len(
            WAVE8_MAMLUK_EGYPT_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_MAMLUK_EGYPT_ENTITIES),
        "new_sources": len(WAVE8_MAMLUK_EGYPT_SOURCES),
        "newly_rated_events": len(WAVE8_MAMLUK_EGYPT_CONTRACTS),
        "outcome_overrides": len(WAVE8_MAMLUK_EGYPT_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_MAMLUK_EGYPT_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_MAMLUK_EGYPT_REVIEWED_CANDIDATE_IDS),
        "terminal_exclusions": len(
            WAVE8_MAMLUK_EGYPT_TERMINAL_EXCLUSION_IDS
        ),
        "unresolved_exact_label_rows": len(WAVE8_MAMLUK_EGYPT_RESERVED_IDS),
    }


def wave8_mamluk_egypt_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS,
    }


__all__ = (
    "WAVE8_MAMLUK_EGYPT_CONTRACT_IDS",
    "WAVE8_MAMLUK_EGYPT_CONTRACTS",
    "WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS",
    "WAVE8_MAMLUK_EGYPT_CROSS_LANE_IDS",
    "WAVE8_MAMLUK_EGYPT_ENTITIES",
    "WAVE8_MAMLUK_EGYPT_EXCLUSIONS",
    "WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS",
    "WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_IDS",
    "WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS",
    "WAVE8_MAMLUK_EGYPT_FINAL_AUDIT_SIGNATURE",
    "WAVE8_MAMLUK_EGYPT_HOLD_IDS",
    "WAVE8_MAMLUK_EGYPT_HOLDS",
    "WAVE8_MAMLUK_EGYPT_INTEGRATION_DISPOSITIONS",
    "WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_MAMLUK_EGYPT_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_MAMLUK_EGYPT_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_MAMLUK_EGYPT_OUTCOME_OVERRIDES",
    "WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_MAMLUK_EGYPT_RESERVED_IDS",
    "WAVE8_MAMLUK_EGYPT_REVIEWED_CANDIDATE_IDS",
    "WAVE8_MAMLUK_EGYPT_SOURCES",
    "WAVE8_MAMLUK_EGYPT_TERMINAL_EXCLUSION_IDS",
    "WAVE8_MAMLUK_EGYPT_UNRESOLVED_IDS",
    "install_wave8_mamluk_egypt_entities",
    "install_wave8_mamluk_egypt_sources",
    "promote_wave8_mamluk_egypt_contracts",
    "validate_wave8_mamluk_egypt_integration_dispositions",
    "validate_wave8_mamluk_egypt_queue_contracts",
    "wave8_mamluk_egypt_audit_signature",
    "wave8_mamluk_egypt_cohort_counts",
    "wave8_mamluk_egypt_counts",
    "wave8_mamluk_egypt_location_quarantine_additions",
)
