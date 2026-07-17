"""Exact-label Wave 8 audit for HCED's ``Lordship of the Isles`` cohort.

The locked queue contains five, not merely an estimated five, rows with this
exact normalized participant label.  They do not describe one continuous
combatant.  The reviewed events involve an era-bounded lordship regime,
event-bounded island and royal coalitions, a Sutherland defence, and—at Bloody
Bay—two opposing factions inside the lordship rather than the Scottish Crown.

Three source-attested tactical victories are promoted.  Harlaw remains an
explicit unknown because the official battlefield record calls its military
outcome inconclusive.  The Bloody Bay row is terminally excluded because its
1480 Scotland-versus-unitary-Lordship assertion reverses the attested actors
and does not preserve the scholarly chronology.  Unknown is never a draw, and
no rating crosses a lordship, MacDonald dynasty, or clan boundary.
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
    "WAVE8_LORDSHIP_ISLES_CONTRACT_IDS",
    "WAVE8_LORDSHIP_ISLES_CONTRACTS",
    "WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS",
    "WAVE8_LORDSHIP_ISLES_ENTITIES",
    "WAVE8_LORDSHIP_ISLES_EXCLUSIONS",
    "WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS",
    "WAVE8_LORDSHIP_ISLES_FINAL_AUDIT_SIGNATURE",
    "WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT",
    "WAVE8_LORDSHIP_ISLES_HOLD_IDS",
    "WAVE8_LORDSHIP_ISLES_HOLDS",
    "WAVE8_LORDSHIP_ISLES_INTEGRATION_DISPOSITIONS",
    "WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_LORDSHIP_ISLES_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_LORDSHIP_ISLES_LOCATION_REVIEWS",
    "WAVE8_LORDSHIP_ISLES_NONPROMOTIONS",
    "WAVE8_LORDSHIP_ISLES_OUTCOME_OVERRIDES",
    "WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS",
    "WAVE8_LORDSHIP_ISLES_RESERVED_IDS",
    "WAVE8_LORDSHIP_ISLES_ROW_DISPOSITIONS",
    "WAVE8_LORDSHIP_ISLES_SOURCES",
    "WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSION_IDS",
    "WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS",
    "install_wave8_lordship_isles_entities",
    "install_wave8_lordship_isles_sources",
    "promote_wave8_lordship_isles_contracts",
    "validate_wave8_lordship_isles_funnel",
    "validate_wave8_lordship_isles_integration_dispositions",
    "validate_wave8_lordship_isles_queue_contracts",
    "wave8_lordship_isles_audit_signature",
    "wave8_lordship_isles_cohort_counts",
    "wave8_lordship_isles_counts",
    "wave8_lordship_isles_location_quarantine_additions",
    "wave8_lordship_isles_metadata",
    "wave8_lordship_isles_row_dispositions",
)


_LANE_NAME = "Wave 8 Lordship of the Isles exact-label audit"
_EVENT_ID_PREFIX = "hced_wave8_lordship_isles_"
_MODULE_OWNER = "wave8_lordship_isles"
_EXACT_LABEL = "lordship of the isles"


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


WAVE8_LORDSHIP_ISLES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_lordship_isles_munro_acts",
        "Acts of the Lords of the Isles, 1336-1493",
        "https://deriv.nls.uk/dcn23/1266/1366/126613661.23.pdf",
        "Scottish History Society; National Library of Scotland",
        "scholarly_calendar_of_primary_acts",
        "munro_acts_lords_isles",
    ),
    _source(
        "wave8_lordship_isles_hes_harlaw",
        "Battle of Harlaw (BTL11)",
        (
            "https://portal.historicenvironment.scot/apex/f?p=1505:300:::::"
            "VIEWTYPE,VIEWREF:designation,BTL11"
        ),
        "Historic Environment Scotland",
        "official_battlefield_designation",
        "hes_harlaw_btl11",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_lordship_isles_hes_inverlochy",
        "Battle of Inverlochy I (BTL34)",
        (
            "https://portal.historicenvironment.scot/apex/f?p=1505:300:::::"
            "VIEWTYPE,VIEWREF:designation,BTL34"
        ),
        "Historic Environment Scotland",
        "official_battlefield_designation",
        "hes_inverlochy_btl34",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_lordship_isles_egan_early_stewarts",
        (
            "The Early Stewart Kings, the Lordship of the Isles, and Ireland, "
            "c.1371-c.1433"
        ),
        "https://eprints.gla.ac.uk/180073/",
        "Northern Studies; University of Glasgow",
        "peer_reviewed_journal_article",
        "egan_early_stewart_lordship_article",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_lordship_isles_scots_peerage",
        "The Scots Peerage, Volume V: Macdonald, Lord of the Isles",
        "https://electricscotland.com/books/pdf/ScotsPeerageVol5.pdf",
        "David Douglas; digitized by Electric Scotland",
        "scholarly_peerage_reference",
        "scots_peerage_volume_five_macdonald",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_lordship_isles_cochran_yu_ross",
        "A Keystone of Contention: The Earldom of Ross, 1215-1517",
        "https://theses.gla.ac.uk/7242/",
        "University of Glasgow",
        "doctoral_dissertation",
        "cochran_yu_earldom_ross_thesis",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_lordship_isles_crawford_warfare",
        (
            "Warfare in the West Highlands and Isles of Scotland in the Late "
            "Middle Ages"
        ),
        "https://theses.gla.ac.uk/7310/",
        "University of Glasgow",
        "doctoral_dissertation",
        "crawford_west_highland_warfare_thesis",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_lordship_isles_caldwell_finlaggan",
        "The Archaeology of Finlaggan, Islay",
        (
            "https://books.socantscot.org/digital-books/catalog/download/"
            "23/21/1230?inline=1"
        ),
        "Society of Antiquaries of Scotland",
        "scholarly_archaeological_monograph",
        "caldwell_finlaggan_monograph",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_lordship_isles_nls_feuds",
        "The History of the Feuds and Conflicts among the Clans",
        "https://deriv.nls.uk/dcn23/7964/79641905.23.pdf",
        "National Library of Scotland digitization",
        "digitized_early_modern_primary_narrative",
        "nls_feuds_conflicts_clans",
        outcome=True,
    ),
    _source(
        "wave8_lordship_isles_dnb_john_macdonald",
        "Macdonald, John (d. 1498?)",
        (
            "https://en.wikisource.org/wiki/Dictionary_of_National_Biography,_"
            "1885-1900/Macdonald,_John_(d.1498%3F)"
        ),
        "Dictionary of National Biography; Wikisource transcription",
        "scholarly_biographical_reference",
        "dnb_john_macdonald_1885",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_lordship_isles_taggart_historicity",
        "The Historicity of Barbour's Bruce",
        "https://theses.gla.ac.uk/1423/",
        "University of Glasgow",
        "doctoral_dissertation",
        "taggart_historicity_barbour_bruce_thesis",
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
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
            boundary_note
            + " No rating is inherited from or transferred to a generic "
            "Lordship of the Isles, the MacDonald dynasty, Clan Donald or any "
            "other clan, the Scottish Crown, an omitted coalition partner, or a "
            "force in another campaign."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_ALEXANDER_REGIME_ID = "alexander_macdonald_lordship_regime_1423_1449"
_LOCHABER_ROYAL_COALITION_ID = "james_i_lochaber_royal_coalition_1429"
_INVERLOCHY_ISLAND_COALITION_ID = (
    "donald_balloch_alasdair_carrach_inverlochy_coalition_1431"
)
_INVERLOCHY_ROYAL_COALITION_ID = "mar_caithness_inverlochy_royal_coalition_1431"
_STRATHFLEET_SUTHERLAND_ID = "robert_sutherland_strathfleet_defence_1453"
_STRATHFLEET_ISLAND_ID = "john_macdonald_strathfleet_raid_detachment_1453"


WAVE8_LORDSHIP_ISLES_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _ALEXANDER_REGIME_ID,
        "Alexander MacDonald's lordship military regime (1423-1449)",
        "era_bounded_lordship_military_regime",
        1423,
        1449,
        "Western Highlands and Isles of Scotland",
        [
            "wave8_lordship_isles_egan_early_stewarts",
            "wave8_lordship_isles_munro_acts",
            "wave8_lordship_isles_scots_peerage",
        ],
        (
            "Bounded to Alexander MacDonald's tenure and used here only for his "
            "1429 field force after the Lochaber rising; it does not identify "
            "Donald's Harlaw host or Donald Balloch's later coalition."
        ),
    ),
    _entity(
        _LOCHABER_ROYAL_COALITION_ID,
        "James I's royal coalition in the Lochaber campaign (1429)",
        "event_bounded_royal_and_clan_coalition",
        1429,
        1429,
        "Lochaber, Scotland",
        [
            "wave8_lordship_isles_egan_early_stewarts",
            "wave8_lordship_isles_scots_peerage",
        ],
        (
            "Bounded to the royal host and the Cameron and Mackintosh elements "
            "that abandoned Alexander's standard during this campaign. Those "
            "contingents are coalition members, not aliases for Scotland."
        ),
    ),
    _entity(
        _INVERLOCHY_ISLAND_COALITION_ID,
        "Donald Balloch and Alasdair Carrach's island coalition at Inverlochy (1431)",
        "event_bounded_island_and_highland_coalition",
        1431,
        1431,
        "Lochaber, Scotland",
        [
            "wave8_lordship_isles_egan_early_stewarts",
            "wave8_lordship_isles_hes_inverlochy",
            "wave8_lordship_isles_scots_peerage",
        ],
        (
            "Bounded to Donald Balloch, Ranald Bane, the MacIain and Moidart "
            "contingents, their island clansmen, and Alasdair Carrach's force at "
            "Inverlochy. It is not Alexander's whole lordship regime."
        ),
    ),
    _entity(
        _INVERLOCHY_ROYAL_COALITION_ID,
        "Mar and Caithness royal coalition at Inverlochy (1431)",
        "event_bounded_royal_and_clan_coalition",
        1431,
        1431,
        "Lochaber, Scotland",
        [
            "wave8_lordship_isles_egan_early_stewarts",
            "wave8_lordship_isles_hes_inverlochy",
            "wave8_lordship_isles_scots_peerage",
        ],
        (
            "Bounded to the royal army led by the earls of Mar and Caithness, "
            "including its Cameron component, in September 1431. It is not a "
            "timeless Scottish Crown or Cameron-clan identity."
        ),
    ),
    _entity(
        _STRATHFLEET_SUTHERLAND_ID,
        "Robert Sutherland's defence on the sands of Strathfleet (1453)",
        "event_bounded_earldom_defence",
        1453,
        1453,
        "Sutherland, Scotland",
        [
            "wave8_lordship_isles_dnb_john_macdonald",
            "wave8_lordship_isles_nls_feuds",
        ],
        (
            "Bounded to the Sutherland force assembled under Robert Sutherland "
            "for this interception. It does not open an Earldom of Sutherland "
            "rating or absorb every Sutherland clan force."
        ),
    ),
    _entity(
        _STRATHFLEET_ISLAND_ID,
        "John MacDonald's island and Ross raid detachment at Strathfleet (1453)",
        "event_bounded_lordship_raid_detachment",
        1453,
        1453,
        "Sutherland, Scotland",
        [
            "wave8_lordship_isles_dnb_john_macdonald",
            "wave8_lordship_isles_nls_feuds",
        ],
        (
            "Bounded to the island and Ross detachment that continued through "
            "Sutherland and was intercepted at Strathfleet. It is not John "
            "MacDonald's whole regime or a generic MacDonald army."
        ),
    ),
)


_ROW_HASHES: dict[str, str] = {
    "hced-Bloody Bay1480-1": (
        "89db06da57b614ddbf91e8c75d1583eef673dc0d9b8c7e86f1e3b98bb1b4020c"
    ),
    "hced-Harlaw1411-1": (
        "fdf84b5432f9d91a4795444a6ba15af000055a005740882695b9c3cc912384b2"
    ),
    "hced-Inverlochy1431-1": (
        "d37c271a4ebc807431ba56dcb6984009dd3be8cc9d6daeaef53c7efeb1ee5027"
    ),
    "hced-Lochaber1429-1": (
        "0a4734e90bb3b18bfd38e432e1094eded48bf7798c3fdaf749ff97c76546aa37"
    ),
    "hced-Strathfleet1453-1": (
        "8e13882492bb41d110c00e6baf91ea89aa0510fa160fa49edd45d1675e971829"
    ),
}


_SOLE_BLOCKER_IDS = frozenset(
    {
        "hced-Bloody Bay1480-1",
        "hced-Harlaw1411-1",
        "hced-Inverlochy1431-1",
        "hced-Lochaber1429-1",
    }
)
_SHARED_LABEL_BLOCKER_IDS = frozenset({"hced-Strathfleet1453-1"})


WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT: dict[str, Any] = {
    "event_candidate_id_sha256": (
        "938a3bcac2b14bf5aa38e8ecce06c20ef8d0fa08f129038fbede9b0b82b32d9d"
    ),
    "events_touched": 5,
    "failure_case": "zero_time_valid_candidates",
    "failure_case_count": 5,
    "label": _EXACT_LABEL,
    "marginal_events": 4,
    "newly_unblocked_candidate_id_sha256": (
        "0bda68e4034b795d51cf50f82334912729d3be33914c1b72da8ebbf45b01963c"
    ),
    "shared_label_blocker_candidate_ids": sorted(_SHARED_LABEL_BLOCKER_IDS),
    "sole_blocker_candidate_ids": sorted(_SOLE_BLOCKER_IDS),
    "sole_blocker_events": 4,
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
    *,
    confidence: float,
) -> dict[str, Any]:
    source_by_id = {
        str(source["id"]): source for source in WAVE8_LORDSHIP_ISLES_SOURCES
    }
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
        "war_type": "civil_war",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(source_by_id[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "bounded_exact_opposing_forces",
        "audit_note": audit_note,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
    }


WAVE8_LORDSHIP_ISLES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Lochaber1429-1": _contract(
        "hced-Lochaber1429-1",
        _canonical(
            "Battle of Lochaber",
            1429,
            "23 June 1429",
            date_precision="day",
        ),
        "james_i_lordship_campaign_1429_1431",
        [_LOCHABER_ROYAL_COALITION_ID],
        [_ALEXANDER_REGIME_ID],
        1,
        [
            "wave8_lordship_isles_egan_early_stewarts",
            "wave8_lordship_isles_munro_acts",
            "wave8_lordship_isles_scots_peerage",
        ],
        [
            "wave8_lordship_isles_egan_early_stewarts",
            "wave8_lordship_isles_scots_peerage",
        ],
        (
            "Egan dates the royal victory over the MacDonald force in Lochaber "
            "to 23 June. The peerage account independently records the Cameron "
            "and Mackintosh change of standard and Alexander's forced submission. "
            "The winner is the bounded royal coalition, not generic Scotland; "
            "the loser is Alexander's tenure-bounded regime force."
        ),
        confidence=0.92,
    ),
    "hced-Inverlochy1431-1": _contract(
        "hced-Inverlochy1431-1",
        _canonical(
            "Battle of Inverlochy I",
            1431,
            "September 1431",
            date_precision="month",
        ),
        "james_i_lordship_campaign_1429_1431",
        [_INVERLOCHY_ISLAND_COALITION_ID],
        [_INVERLOCHY_ROYAL_COALITION_ID],
        1,
        [
            "wave8_lordship_isles_egan_early_stewarts",
            "wave8_lordship_isles_hes_inverlochy",
            "wave8_lordship_isles_scots_peerage",
        ],
        [
            "wave8_lordship_isles_egan_early_stewarts",
            "wave8_lordship_isles_hes_inverlochy",
            "wave8_lordship_isles_scots_peerage",
        ],
        (
            "Historic Environment Scotland identifies Donald Balloch's force, "
            "its named island and Highland partners, the Mar-Caithness royal "
            "army, and the crushing royal defeat. Egan and the peerage account "
            "independently confirm the island coalition's victory. Neither side "
            "is collapsed to a generic lordship, Crown, or clan identity."
        ),
        confidence=0.97,
    ),
    "hced-Strathfleet1453-1": _contract(
        "hced-Strathfleet1453-1",
        _canonical(
            "Battle on the Sands of Strathfleet",
            1453,
            "1453 (exact day unresolved)",
        ),
        "sutherland_lordship_raid_1453",
        [_STRATHFLEET_SUTHERLAND_ID],
        [_STRATHFLEET_ISLAND_ID],
        1,
        [
            "wave8_lordship_isles_dnb_john_macdonald",
            "wave8_lordship_isles_nls_feuds",
        ],
        [
            "wave8_lordship_isles_dnb_john_macdonald",
            "wave8_lordship_isles_nls_feuds",
        ],
        (
            "The digitized clan-conflict narrative distinguishes the detachment "
            "intercepted on Strathfleet's sands from the earlier fighting at "
            "Skibo and records its defeat by Robert Sutherland's force. The DNB "
            "account independently records the 1453 Sutherland victory. This "
            "contract owns both bounded actors despite the second unresolved "
            "exact label; it does not open a generic Sutherland or clan rating."
        ),
        confidence=0.80,
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    category: str,
    reviewed_outcome: str,
    actor_description: Iterable[str],
    reason: str,
    evidence_refs: Iterable[str],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "disposition": "hold",
        "hold_category": category,
        "reviewed_outcome": reviewed_outcome,
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_actor_description": list(map(str, actor_description)),
        "reviewed_granularity": canonical_event["granularity"],
        "hold_reason": reason,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "provisional_hced_hold",
        },
    }


WAVE8_LORDSHIP_ISLES_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Harlaw1411-1": _hold(
        "hced-Harlaw1411-1",
        _canonical(
            "Battle of Harlaw",
            1411,
            "24 July 1411",
            date_precision="day",
        ),
        "ross_succession_conflict_1411",
        "official_record_militarily_inconclusive",
        "tactical_winner_not_source_attested",
        [
            "Donald of Harlaw's Isles and Ross-claimant coalition",
            "Alexander Stewart, Earl of Mar's northeastern royal-aligned host",
        ],
        (
            "Historic Environment Scotland describes the military outcome as "
            "inconclusive and notes that both sides claimed victory. The battle's "
            "strategic check on Donald does not attest HCED's tactical Scotland "
            "win. The row is not promoted; its rating result remains unknown and "
            "is never encoded as a draw."
        ),
        [
            "wave8_lordship_isles_cochran_yu_ross",
            "wave8_lordship_isles_hes_harlaw",
            "wave8_lordship_isles_scots_peerage",
        ],
    )
}


WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Bloody Bay1480-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Bloody Bay1480-1"],
        "canonical_event": _canonical(
            "Battle of Bloody Bay",
            1481,
            "c. 1481 (early 1480s)",
            date_precision="circa_year",
        ),
        "cohort": "lordship_internal_conflict_early_1480s",
        "disposition": "terminal_exclusion",
        "hold_category": "wrong_belligerents_and_unpreserved_chronology",
        "reviewed_outcome": "angus_og_rebel_coalition_victory_attested",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_actor_description": [
            (
                "John II MacDonald's loyalist lordship coalition, including "
                "MacLean support"
            ),
            "Angus Og MacDonald's rebel lordship coalition",
        ],
        "reviewed_granularity": "engagement",
        "hold_reason": (
            "The scholarly studies place Bloody Bay around 1481 or in the early "
            "1480s and identify an internal lordship conflict in which Angus Og's "
            "coalition defeated his father John's loyalists. The Scottish Crown "
            "was not HCED's proposed winning belligerent, and a unitary Lordship "
            "cannot stand on only one side. Repair would replace both actor "
            "semantics and the locked 1480 chronology, so this exact row is "
            "terminally excluded rather than promoted or drawn."
        ),
        "evidence_refs": [
            "wave8_lordship_isles_caldwell_finlaggan",
            "wave8_lordship_isles_cochran_yu_ross",
            "wave8_lordship_isles_crawford_warfare",
        ],
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "terminal_hced_exclusion",
        },
    }
}


WAVE8_LORDSHIP_ISLES_EXCLUSIONS = WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS
WAVE8_LORDSHIP_ISLES_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_LORDSHIP_ISLES_HOLDS,
    **WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS,
}
WAVE8_LORDSHIP_ISLES_CONTRACT_IDS = frozenset(WAVE8_LORDSHIP_ISLES_CONTRACTS)
WAVE8_LORDSHIP_ISLES_HOLD_IDS = frozenset(WAVE8_LORDSHIP_ISLES_HOLDS)
WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS
)
WAVE8_LORDSHIP_ISLES_RESERVED_IDS = frozenset(
    {
        *WAVE8_LORDSHIP_ISLES_CONTRACTS,
        *WAVE8_LORDSHIP_ISLES_NONPROMOTIONS,
    }
)
WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)
WAVE8_LORDSHIP_ISLES_ROW_DISPOSITIONS = {
    candidate_id: (
        "promote"
        if candidate_id in WAVE8_LORDSHIP_ISLES_CONTRACT_IDS
        else (
            "hold"
            if candidate_id in WAVE8_LORDSHIP_ISLES_HOLD_IDS
            else "terminal_exclusion"
        )
    )
    for candidate_id in sorted(WAVE8_LORDSHIP_ISLES_RESERVED_IDS)
}


# These local declarations are promoted-only and intentionally do not mutate
# the shared hced_location manifests.  All three raw points are broader place
# geocodes rather than source-verified battlefield points.
WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_LORDSHIP_ISLES_CONTRACT_IDS
)
WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_LORDSHIP_ISLES_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_LORDSHIP_ISLES_LOCATION_REVIEWS: dict[str, dict[str, Any]] = {
    "hced-Lochaber1429-1": {
        "country_disposition": "retain_united_kingdom",
        "point_disposition": "quarantine_regional_lochaber_geocode",
        "reason": (
            "The sources locate the engagement in Lochaber but do not verify the "
            "raw coordinate as the battlefield. The modern-country assertion is "
            "retained while the point is withheld."
        ),
        "evidence_refs": [
            "wave8_lordship_isles_egan_early_stewarts",
            "wave8_lordship_isles_scots_peerage",
        ],
    },
    "hced-Inverlochy1431-1": {
        "country_disposition": "retain_united_kingdom",
        "point_disposition": "quarantine_unverified_raw_point",
        "reason": (
            "Historic Environment Scotland defines a battlefield area, but the "
            "HCED point is not identified as a reviewed point within that record. "
            "The modern-country assertion is retained."
        ),
        "evidence_refs": [
            "wave8_lordship_isles_egan_early_stewarts",
            "wave8_lordship_isles_hes_inverlochy",
        ],
    },
    "hced-Strathfleet1453-1": {
        "country_disposition": "retain_united_kingdom",
        "point_disposition": "quarantine_regional_strathfleet_geocode",
        "reason": (
            "The sources identify the sands of Strathfleet, while HCED supplies "
            "only a broad regional coordinate. The modern-country assertion is "
            "retained and the unverified point withheld."
        ),
        "evidence_refs": [
            "wave8_lordship_isles_dnb_john_macdonald",
            "wave8_lordship_isles_nls_feuds",
        ],
    },
}


# Each promoted row preserves the raw winner/loser orientation.  The actor
# replacements are identity resolutions, not outcome overrides.
WAVE8_LORDSHIP_ISLES_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Bloody Bay1480-1": {
        "aliases": ("battle of bloody bay", "bloody bay"),
        "years": (1480, 1483),
    },
    "hced-Harlaw1411-1": {
        "aliases": ("battle of harlaw", "harlaw", "red harlaw"),
        "years": (1411, 1411),
    },
    "hced-Inverlochy1431-1": {
        "aliases": (
            "battle of inverlochy",
            "battle of inverlochy i",
            "first battle of inverlochy",
            "inverlochy",
        ),
        "years": (1431, 1431),
    },
    "hced-Lochaber1429-1": {
        "aliases": ("battle of lochaber", "lochaber"),
        "years": (1429, 1429),
    },
    "hced-Strathfleet1453-1": {
        "aliases": (
            "battle of strathfleet",
            "battle on the sands of strathfleet",
            "sands of strathfleet",
            "strathfleet",
        ),
        "years": (1453, 1453),
    },
}


WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Dee1308-1": {
        "raw_row_sha256": (
            "b9aeeb6aaac6609c2da3d862df389905ba6946da89766fee46855cc678151c37"
        ),
        "related_candidate_ids": [],
        "disposition": "not_owned_non_exact_composite_and_anachronistic_title",
        "owner_module": None,
        "unknown_is_never_draw": True,
        "reason": (
            "Its exact side is 'Galloway, Lordship of the Isles', not this lane's "
            "label. The scholarly act calendar starts the Lords' surviving acts "
            "in 1336, while Taggart finds the 1308 Dee/Cree narrative internally "
            "inconsistent about Donald of the Isles and weakly supported. This "
            "lane neither splits the composite nor creates a backward dynastic "
            "or clan bridge; the row remains unowned and unknown, never a draw."
        ),
        "evidence_refs": [
            "wave8_lordship_isles_munro_acts",
            "wave8_lordship_isles_taggart_historicity",
        ],
    }
}


WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Strathfleet1453-1": {
        "source_dataset": "hced",
        "raw_row_sha256": _ROW_HASHES["hced-Strathfleet1453-1"],
        "other_exact_label": "earldom of sutherland",
        "disposition": "canonical_owner_here_for_shared_exact_row",
        "owner_module": _MODULE_OWNER,
        "reason": (
            "The same row is blocked by Earldom of Sutherland. This module owns "
            "the one candidate and both event-bounded sides; a future Sutherland "
            "lane must record external ownership and must not emit a second event."
        ),
    }
}


WAVE8_LORDSHIP_ISLES_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"related_hced:{candidate_id}": disposition
        for candidate_id, disposition in (
            WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS.items()
        )
    },
    **{
        f"cross_lane:{candidate_id}": disposition
        for candidate_id, disposition in (
            WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS.items()
        )
    },
    **{
        f"iwbd_duplicate:{candidate_id}": disposition
        for candidate_id, disposition in (
            WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS.items()
        )
    },
    **{
        f"existing_release:{candidate_id}": disposition
        for candidate_id, disposition in (
            WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS.items()
        )
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_LORDSHIP_ISLES_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_LORDSHIP_ISLES_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(
            WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS
        ),
        "funnel_audit": WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT,
        "holds": WAVE8_LORDSHIP_ISLES_HOLDS,
        "integration_dispositions": WAVE8_LORDSHIP_ISLES_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT,
        "location_reviews": WAVE8_LORDSHIP_ISLES_LOCATION_REVIEWS,
        "outcome_overrides": WAVE8_LORDSHIP_ISLES_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS,
        "row_dispositions": WAVE8_LORDSHIP_ISLES_ROW_DISPOSITIONS,
        "sources": WAVE8_LORDSHIP_ISLES_SOURCES,
        "terminal_exclusions": WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS,
    }


def wave8_lordship_isles_audit_signature() -> str:
    """Return the digest of every signed semantic decision in this lane."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_LORDSHIP_ISLES_FINAL_AUDIT_SIGNATURE = (
    "b5af4f7d3683add9f1931dc42ac24b97582618e1a3c79e7a7816b255aed68b89"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(map(str, values))))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_LORDSHIP_ISLES_CONTRACTS),
        len(WAVE8_LORDSHIP_ISLES_HOLDS),
        len(WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS),
    ) != (3, 1, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (
        len(WAVE8_LORDSHIP_ISLES_ENTITIES),
        len(WAVE8_LORDSHIP_ISLES_SOURCES),
    ) != (6, 11):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_LORDSHIP_ISLES_EXCLUSIONS is not (
        WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS
    ):
        raise ValueError(f"{_LANE_NAME} exclusion alias drifted")
    if WAVE8_LORDSHIP_ISLES_RESERVED_IDS != (
        WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if set(WAVE8_LORDSHIP_ISLES_ROW_DISPOSITIONS) != (
        WAVE8_LORDSHIP_ISLES_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} row dispositions are incomplete")
    if set(WAVE8_LORDSHIP_ISLES_ROW_DISPOSITIONS.values()) != {
        "hold",
        "promote",
        "terminal_exclusion",
    }:
        raise ValueError(f"{_LANE_NAME} row disposition vocabulary changed")
    if wave8_lordship_isles_audit_signature() != (
        WAVE8_LORDSHIP_ISLES_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    if _sorted_newline_sha256(WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS) != str(
        WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT["event_candidate_id_sha256"]
    ):
        raise ValueError(f"{_LANE_NAME} exact-cohort funnel digest drifted")
    if _sorted_newline_sha256(_SOLE_BLOCKER_IDS) != str(
        WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT[
            "newly_unblocked_candidate_id_sha256"
        ]
    ):
        raise ValueError(f"{_LANE_NAME} sole-blocker funnel digest drifted")
    if _SOLE_BLOCKER_IDS | _SHARED_LABEL_BLOCKER_IDS != (
        WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} funnel blocker partition changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_LORDSHIP_ISLES_SOURCES
    }
    if len(source_by_id) != len(WAVE8_LORDSHIP_ISLES_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(
        {
            str(source["source_family_id"])
            for source in WAVE8_LORDSHIP_ISLES_SOURCES
        }
    ) != len(WAVE8_LORDSHIP_ISLES_SOURCES):
        raise ValueError(f"{_LANE_NAME} source families are not unique")
    for source in WAVE8_LORDSHIP_ISLES_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS citation")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are nondeterministic")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_LORDSHIP_ISLES_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_LORDSHIP_ISLES_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "clan donald",
        "clan macdonald",
        "earldom of sutherland",
        "lordship of the isles",
        "macdonald dynasty",
        "scotland",
        "scottish crown",
    }
    for entity in WAVE8_LORDSHIP_ISLES_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a bridge")
        if int(entity["start_year"]) > int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity window is invalid")
        if str(entity["name"]).casefold() in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic identity")
        note = str(entity["continuity_note"]).casefold()
        if not all(
            phrase in note
            for phrase in (
                "no rating is inherited",
                "clan",
                "dynasty",
                "coalition",
                "another campaign",
            )
        ):
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are nondeterministic")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")
    if (
        int(entity_by_id[_ALEXANDER_REGIME_ID]["start_year"]),
        int(entity_by_id[_ALEXANDER_REGIME_ID]["end_year"]),
    ) != (1423, 1449):
        raise ValueError(f"{_LANE_NAME} Alexander regime boundary changed")
    for entity_id, entity in entity_by_id.items():
        if entity_id == _ALEXANDER_REGIME_ID:
            continue
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} campaign force is not event-bounded")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    expected_orientations = {
        "hced-Inverlochy1431-1": 1,
        "hced-Lochaber1429-1": 1,
        "hced-Strathfleet1453-1": 1,
    }
    for candidate_id, contract in WAVE8_LORDSHIP_ISLES_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} promotion fingerprint drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (side_1 | side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unbounded or unknown identity")
        used_entities.update(side_1 | side_2)
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        for entity_id in side_1 | side_2:
            entity = entity_by_id[entity_id]
            if not (
                int(entity["start_year"])
                <= low
                <= high
                <= int(entity["end_year"])
            ):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or int(contract["winner_side"]) != expected_orientations[candidate_id]
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"] != "bounded_exact_opposing_forces"
        ):
            raise ValueError(f"{_LANE_NAME} promotion semantics drifted")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} promotion evidence drifted")
        if (
            len(outcomes) < 2
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome evidence is insufficient")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        expected_families = sorted(
            {
                str(source_by_id[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identities are not exactly consumed")

    for candidate_id, hold in WAVE8_LORDSHIP_ISLES_HOLDS.items():
        if (
            hold["raw_row_sha256"] != _ROW_HASHES[candidate_id]
            or hold["disposition"] != "hold"
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} hold became rateable")
        for forbidden in (
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "outcome_source_ids",
            "outcome_source_family_ids",
        ):
            if forbidden in hold:
                raise ValueError(f"{_LANE_NAME} hold asserts a result")
        reason = str(hold["hold_reason"]).casefold()
        if "not promoted" not in reason or "draw" not in reason:
            raise ValueError(f"{_LANE_NAME} hold lost the no-draw policy")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence drifted")
        used_sources.update(evidence)

    exclusion = WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS[
        "hced-Bloody Bay1480-1"
    ]
    if (
        exclusion["raw_row_sha256"] != _ROW_HASHES["hced-Bloody Bay1480-1"]
        or exclusion["disposition"] != "terminal_exclusion"
        or exclusion["result_type"] != "unknown"
        or exclusion["unknown_is_never_draw"] is not True
        or int(exclusion["canonical_event"]["year_low"]) != 1481
        or "winner_side" in exclusion
    ):
        raise ValueError(f"{_LANE_NAME} Bloody Bay exclusion changed")
    exclusion_reason = str(exclusion["hold_reason"]).casefold()
    if not all(
        phrase in exclusion_reason
        for phrase in ("scottish crown", "unitary lordship", "1480", "draw")
    ):
        raise ValueError(f"{_LANE_NAME} Bloody Bay rationale is incomplete")
    exclusion_evidence = list(map(str, exclusion["evidence_refs"]))
    if not _is_sorted_unique(exclusion_evidence) or not set(exclusion_evidence) <= set(
        source_by_id
    ):
        raise ValueError(f"{_LANE_NAME} exclusion evidence drifted")
    used_sources.update(exclusion_evidence)

    if WAVE8_LORDSHIP_ISLES_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} invented an outcome override")
    if set(WAVE8_LORDSHIP_ISLES_LOCATION_REVIEWS) != (
        WAVE8_LORDSHIP_ISLES_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} promoted-only location review is incomplete")
    if WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_LORDSHIP_ISLES_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    for review in WAVE8_LORDSHIP_ISLES_LOCATION_REVIEWS.values():
        evidence = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence drifted")
        used_sources.update(evidence)

    if set(WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_LORDSHIP_ISLES_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for item in WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, item["aliases"]))
        if not _is_sorted_unique(aliases) or aliases != list(
            map(normalize_label, aliases)
        ):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are nondeterministic")
        years = tuple(map(int, item["years"]))
        if len(years) != 2 or years[0] > years[1]:
            raise ValueError(f"{_LANE_NAME} duplicate interval drifted")
    if (
        WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} acquired a duplicate disposition")

    if set(WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS) != {
        "hced-Dee1308-1"
    }:
        raise ValueError(f"{_LANE_NAME} related HCED boundary changed")
    related = WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS["hced-Dee1308-1"]
    if (
        related["owner_module"] is not None
        or related["unknown_is_never_draw"] is not True
        or "composite" not in str(related["disposition"])
    ):
        raise ValueError(f"{_LANE_NAME} Dee disposition changed")
    related_evidence = list(map(str, related["evidence_refs"]))
    if not _is_sorted_unique(related_evidence) or not set(related_evidence) <= set(
        source_by_id
    ):
        raise ValueError(f"{_LANE_NAME} related HCED evidence drifted")
    used_sources.update(related_evidence)

    if set(WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS) != {
        "hced-Strathfleet1453-1"
    }:
        raise ValueError(f"{_LANE_NAME} cross-lane boundary changed")
    cross_lane = WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS[
        "hced-Strathfleet1453-1"
    ]
    if (
        cross_lane["raw_row_sha256"]
        != _ROW_HASHES["hced-Strathfleet1453-1"]
        or cross_lane["owner_module"] != _MODULE_OWNER
        or cross_lane["other_exact_label"] != "earldom of sutherland"
    ):
        raise ValueError(f"{_LANE_NAME} Strathfleet ownership changed")

    expected_integration_keys = {
        "cross_lane:hced-Strathfleet1453-1",
        "related_hced:hced-Dee1308-1",
    }
    if set(WAVE8_LORDSHIP_ISLES_INTEGRATION_DISPOSITIONS) != (
        expected_integration_keys
    ):
        raise ValueError(f"{_LANE_NAME} integration inventory changed")

    used_sources.update(
        source_id
        for entity in WAVE8_LORDSHIP_ISLES_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")


def _is_exact_lordship_label(value: Any) -> bool:
    return normalize_label(value) == _EXACT_LABEL


def validate_wave8_lordship_isles_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin all and only the five exact-label rows in the locked queue."""

    _validate_static()
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_LORDSHIP_ISLES_CONTRACTS,
        WAVE8_LORDSHIP_ISLES_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_lordship_label(row.get("side_1_raw"))
        or _is_exact_lordship_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact-label inventory changed: {sorted(exact_ids)}"
        )
    by_id = {
        str(row.get("candidate_id")): row
        for row in hced_rows
        if str(row.get("candidate_id")) in WAVE8_LORDSHIP_ISLES_RESERVED_IDS
    }
    for candidate_id, row in by_id.items():
        exact_sides = sum(
            _is_exact_lordship_label(row.get(field))
            for field in ("side_1_raw", "side_2_raw")
        )
        if exact_sides != 1:
            raise ValueError(
                f"{_LANE_NAME} exact-side ownership changed: {candidate_id}"
            )
    if counts["reviewed_hced_rows"] != 5:
        raise ValueError(f"{_LANE_NAME} common inventory count changed")
    return {
        "holds": len(WAVE8_LORDSHIP_ISLES_HOLDS),
        "promotion_contracts": len(WAVE8_LORDSHIP_ISLES_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_LORDSHIP_ISLES_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_lordship_isles_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    """Pin the current five-row funnel independently of disposition choices."""

    _validate_static()
    labels = funnel.get("labels")
    if not isinstance(labels, list):
        raise ValueError(f"{_LANE_NAME} funnel labels are unavailable")
    rows = [item for item in labels if item.get("label") == _EXACT_LABEL]
    if len(rows) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label row")
    label = rows[0]
    expected_fields = {
        "event_candidate_id_sha256": WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT[
            "event_candidate_id_sha256"
        ],
        "events_touched": 5,
        "sole_blocker_events": 4,
    }
    for key, expected in expected_fields.items():
        if label.get(key) != expected:
            raise ValueError(f"{_LANE_NAME} funnel {key} changed")
    failures = label.get("failure_cases")
    if not isinstance(failures, Mapping) or failures.get(
        "zero_time_valid_candidates"
    ) != 5:
        raise ValueError(f"{_LANE_NAME} funnel failure case changed")

    greedy = funnel.get("greedy_batch")
    ranking = greedy.get("ranking") if isinstance(greedy, Mapping) else None
    if not isinstance(ranking, list):
        raise ValueError(f"{_LANE_NAME} greedy ranking is unavailable")
    ranked = [item for item in ranking if item.get("label") == _EXACT_LABEL]
    if len(ranked) != 1:
        raise ValueError(f"{_LANE_NAME} expected one greedy ranking row")
    if (
        ranked[0].get("events_touched") != 5
        or ranked[0].get("marginal_events") != 4
        or ranked[0].get("newly_unblocked_candidate_id_sha256")
        != WAVE8_LORDSHIP_ISLES_FUNNEL_AUDIT[
            "newly_unblocked_candidate_id_sha256"
        ]
    ):
        raise ValueError(f"{_LANE_NAME} greedy audit changed")

    row_label_data = funnel.get("row_label_data")
    if not isinstance(row_label_data, list):
        raise ValueError(f"{_LANE_NAME} row-label data are unavailable")
    audited_rows: list[Mapping[str, Any]] = []
    for row in row_label_data:
        label_failures = row.get("label_failures")
        matching = (
            [
                failure
                for failure in label_failures
                if failure.get("label") == _EXACT_LABEL
            ]
            if isinstance(label_failures, list)
            else []
        )
        if matching:
            if len(matching) != 1 or matching[0].get("failure_case") != (
                "zero_time_valid_candidates"
            ):
                raise ValueError(f"{_LANE_NAME} row failure changed")
            audited_rows.append(row)
    audited_ids = {str(row.get("candidate_id")) for row in audited_rows}
    sole_ids = {
        str(row.get("candidate_id"))
        for row in audited_rows
        if row.get("sole_blocker_label") == _EXACT_LABEL
    }
    shared_ids = audited_ids - sole_ids
    if audited_ids != WAVE8_LORDSHIP_ISLES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact funnel cohort changed")
    if sole_ids != _SOLE_BLOCKER_IDS:
        raise ValueError(f"{_LANE_NAME} sole-blocker cohort changed")
    if shared_ids != _SHARED_LABEL_BLOCKER_IDS:
        raise ValueError(f"{_LANE_NAME} shared-label blocker changed")
    return {
        "exact_label_rows": len(audited_ids),
        "shared_label_rows": len(shared_ids),
        "sole_blocker_rows": len(sole_ids),
    }


def _year_from_date(value: Any) -> int | None:
    text = str(value or "")
    if len(text) >= 4 and text[:4].isdigit():
        return int(text[:4])
    return None


def _row_interval(row: Mapping[str, Any]) -> tuple[int, int] | None:
    for field in ("year", "year_best"):
        value = row.get(field)
        try:
            if value is not None:
                year = int(value)
                return year, year
        except (TypeError, ValueError):
            pass
    start = _year_from_date(row.get("start_date"))
    end = _year_from_date(row.get("end_date"))
    if start is None and end is None:
        return None
    if start is None:
        start = end
    if end is None:
        end = start
    assert start is not None and end is not None
    return min(start, end), max(start, end)


def _normalized_duplicate_audit() -> dict[str, dict[str, Any]]:
    return {
        candidate_id: {
            "aliases": {normalize_label(alias) for alias in item["aliases"]},
            "years": tuple(map(int, item["years"])),
        }
        for candidate_id, item in (
            WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT.items()
        )
    }


def _matches_duplicate_audit(
    names: Iterable[Any],
    interval: tuple[int, int] | None,
    audit: Mapping[str, Mapping[str, Any]],
) -> str | None:
    if interval is None:
        return None
    normalized_names = {normalize_label(name) for name in names}
    start, end = interval
    for candidate_id, item in audit.items():
        low, high = map(int, item["years"])
        if start <= high and end >= low and normalized_names & set(item["aliases"]):
            return candidate_id
    return None


def validate_wave8_lordship_isles_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin related rows and fail closed on future HCED, IWBD, or release twins."""

    validate_wave8_lordship_isles_queue_contracts(hced_rows)
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, disposition in (
        WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one related HCED row {candidate_id}, "
                f"found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != disposition["raw_row_sha256"]:
            raise ValueError(
                f"{_LANE_NAME} related HCED fingerprint changed: {candidate_id}"
            )
    for candidate_id, disposition in (
        WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1 or canonical_hced_row_sha256(rows[0]) != disposition[
            "raw_row_sha256"
        ]:
            raise ValueError(
                f"{_LANE_NAME} cross-lane fingerprint changed: {candidate_id}"
            )

    audit = _normalized_duplicate_audit()
    related_ids = set(WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS)
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id") or "")
        if candidate_id in WAVE8_LORDSHIP_ISLES_RESERVED_IDS or candidate_id in (
            related_ids
        ):
            continue
        matched = _matches_duplicate_audit([row.get("name")], _row_interval(row), audit)
        if matched is not None:
            raise ValueError(
                f"{_LANE_NAME} unreviewed cross-lane HCED twin "
                f"{candidate_id or '<missing-id>'} for {matched}"
            )

    for row in iwbd_rows:
        matched = _matches_duplicate_audit([row.get("name")], _row_interval(row), audit)
        if matched is not None:
            raise ValueError(
                f"{_LANE_NAME} unreviewed probable IWBD duplicate "
                f"{row.get('candidate_id') or '<missing-id>'} for {matched}"
            )

    existing = list(existing_events)
    ownership_collisions = sorted(
        {
            str(event.get("hced_candidate_id"))
            for event in existing
            if event.get("hced_candidate_id") in WAVE8_LORDSHIP_ISLES_RESERVED_IDS
        }
    )
    if ownership_collisions:
        raise ValueError(
            f"{_LANE_NAME} candidate ownership collision in release: "
            f"{ownership_collisions}"
        )
    for event in existing:
        raw_aliases = event.get("aliases", [])
        aliases = [raw_aliases] if isinstance(raw_aliases, str) else list(raw_aliases)
        matched = _matches_duplicate_audit(
            [event.get("name"), *aliases],
            _row_interval(event),
            audit,
        )
        if matched is not None:
            raise ValueError(
                f"{_LANE_NAME} unreviewed existing-release twin "
                f"{event.get('id') or '<missing-id>'} for {matched}"
            )

    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(
            WAVE8_LORDSHIP_ISLES_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "related_hced_dispositions": len(
            WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS
        ),
    }


def install_wave8_lordship_isles_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_LORDSHIP_ISLES_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_lordship_isles_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_LORDSHIP_ISLES_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_lordship_isles_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit only the three source-attested, candidate-keyed tactical wins."""

    validate_wave8_lordship_isles_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_LORDSHIP_ISLES_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_lordship_isles_cohort_counts() -> dict[str, int]:
    """Count all five terminal review dispositions by historical cohort."""

    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_LORDSHIP_ISLES_CONTRACTS.values(),
                    *WAVE8_LORDSHIP_ISLES_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_lordship_isles_counts() -> dict[str, int]:
    """Return signed inventory, disposition, and quarantine counts."""

    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_LORDSHIP_ISLES_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_LORDSHIP_ISLES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_LORDSHIP_ISLES_HOLDS),
        "integration_dispositions": len(
            WAVE8_LORDSHIP_ISLES_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_LORDSHIP_ISLES_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_LORDSHIP_ISLES_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_LORDSHIP_ISLES_ENTITIES),
        "new_sources": len(WAVE8_LORDSHIP_ISLES_SOURCES),
        "newly_rated_events": len(WAVE8_LORDSHIP_ISLES_CONTRACTS),
        "outcome_overrides": len(WAVE8_LORDSHIP_ISLES_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_LORDSHIP_ISLES_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_LORDSHIP_ISLES_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_LORDSHIP_ISLES_RESERVED_IDS),
        "sole_blocker_rows": len(_SOLE_BLOCKER_IDS),
        "terminal_exclusions": len(
            WAVE8_LORDSHIP_ISLES_TERMINAL_EXCLUSIONS
        ),
    }


def wave8_lordship_isles_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    """Return immutable promoted-only additions for coordinated integration."""

    _validate_static()
    return {
        "country": WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_lordship_isles_row_dispositions() -> dict[str, str]:
    """Return a defensive copy of every exact row's terminal disposition."""

    _validate_static()
    return dict(WAVE8_LORDSHIP_ISLES_ROW_DISPOSITIONS)


def wave8_lordship_isles_metadata() -> dict[str, Any]:
    """Return deterministic integration metadata without mutating shared state."""

    _validate_static()
    return {
        "exact_label": _EXACT_LABEL,
        "module_owner": _MODULE_OWNER,
        "signature": WAVE8_LORDSHIP_ISLES_FINAL_AUDIT_SIGNATURE,
        "candidate_ids": sorted(WAVE8_LORDSHIP_ISLES_RESERVED_IDS),
        "counts": wave8_lordship_isles_counts(),
        "cohorts": wave8_lordship_isles_cohort_counts(),
        "row_dispositions": wave8_lordship_isles_row_dispositions(),
        "location_quarantines": {
            "country": sorted(WAVE8_LORDSHIP_ISLES_COUNTRY_QUARANTINE_ADDITIONS),
            "point": sorted(WAVE8_LORDSHIP_ISLES_POINT_QUARANTINE_ADDITIONS),
        },
    }
