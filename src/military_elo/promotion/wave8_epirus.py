"""Exact Wave 8 dispositions for HCED rows blocked by ``Epirus``.

The label spans unrelated ancient and medieval political formations.  This
lane therefore uses candidate-keyed, time-bounded identities only: Alexander
the Molossian's kingdom, Pyrrhus's kingdom, an Argos defensive coalition, and
the thirteenth-century Epirote and Latin successor states.  It deliberately
does not install an alias or a timeless ``Epirus`` identity.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_EPIRUS_CONTRACT_IDS",
    "WAVE8_EPIRUS_CONTRACTS",
    "WAVE8_EPIRUS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_EPIRUS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_EPIRUS_ENTITIES",
    "WAVE8_EPIRUS_EXCLUSION_IDS",
    "WAVE8_EPIRUS_EXCLUSIONS",
    "WAVE8_EPIRUS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_EPIRUS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_EPIRUS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_EPIRUS_HOLD_IDS",
    "WAVE8_EPIRUS_HOLDS",
    "WAVE8_EPIRUS_INTEGRATION_DISPOSITIONS",
    "WAVE8_EPIRUS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_EPIRUS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_EPIRUS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_EPIRUS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_EPIRUS_OUTCOME_OVERRIDES",
    "WAVE8_EPIRUS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_EPIRUS_RESERVED_IDS",
    "WAVE8_EPIRUS_SOURCES",
    "install_wave8_epirus_entities",
    "install_wave8_epirus_sources",
    "promote_wave8_epirus_contracts",
    "validate_wave8_epirus_integration_dispositions",
    "validate_wave8_epirus_queue_contracts",
    "wave8_epirus_audit_signature",
    "wave8_epirus_cohort_counts",
    "wave8_epirus_counts",
    "wave8_epirus_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Epirus identity audit"
_EVENT_ID_PREFIX = "hced_wave8_epirus_"

_ROMAN_REPUBLIC_ID = "roman_republic"
_CARTHAGE_ID = "carthage"
_ALEXANDER_EPIRUS_ID = "alexander_i_epirote_kingdom_343_331_bce"
_PANDOSIA_COALITION_ID = "lucanian_bruttian_pandosia_coalition_331_bce"
_PYRRHUS_EPIRUS_ID = "pyrrhus_epirote_kingdom_297_272_bce"
_ARGOS_COALITION_ID = "argos_antigonid_spartan_defensive_coalition_272_bce"
_THEODORE_EPIRUS_ID = "theodore_komnenos_doukas_epirote_state_1215_1230"
_LATIN_THESSALONICA_ID = "latin_kingdom_thessalonica_1204_1224"


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


WAVE8_EPIRUS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_epirus_cambridge_pyrrhus",
        "Pyrrhus",
        (
            "https://resolve.cambridge.org/core/services/aop-cambridge-core/"
            "content/view/65B53CFFF06DECD5AAFF25B3A082E8F0/"
            "9781139054355c10_p456-485_CBO.pdf/pyrrhus.pdf"
        ),
        "Cambridge University Press",
        "scholarly_history_chapter",
        "cambridge_ancient_history_pyrrhus",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_epirus_plutarch_pyrrhus",
        "Plutarch, Life of Pyrrhus",
        "https://penelope.uchicago.edu/Thayer/e/roman/texts/plutarch/lives/pyrrhus%2A.html",
        "University of Chicago LacusCurtius",
        "translated_primary_source",
        "plutarch_life_pyrrhus_perrin_translation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_epirus_cambridge_cicero_brutus",
        "The Politics and Poetics of Cicero's Brutus",
        (
            "https://resolve.cambridge.org/core/services/aop-cambridge-core/"
            "content/view/E3CFAF05525AFF343B0CA224E641DCF5/"
            "9781009281355AR.pdf/The_Politics_and_Poetics_of_Cicero_s__I_Brutus__I_.pdf"
        ),
        "Cambridge University Press",
        "scholarly_monograph",
        "cambridge_cicero_brutus_pyrrhic_war",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_epirus_cambridge_roman_commonwealth",
        "Law and Power in the Making of the Roman Commonwealth",
        "https://assets.cambridge.org/97811070/71971/frontmatter/9781107071971_frontmatter.pdf",
        "Cambridge University Press",
        "scholarly_monograph_chronology",
        "cambridge_roman_commonwealth_chronology",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_epirus_routledge_pyrrhic_war",
        "A History of the Pyrrhic War",
        "https://www.routledge.com/A-History-of-the-Pyrrhic-War/Kent/p/book/9781032090306",
        "Routledge",
        "scholarly_military_history_monograph",
        "kent_history_pyrrhic_war",
    ),
    _source(
        "wave8_epirus_cambridge_south_italy",
        "South Italy in the Fourth Century B.C.",
        (
            "https://resolve.cambridge.org/core/services/aop-cambridge-core/"
            "content/view/7495A504A36E668A627BBE7CA7D1B976/"
            "9781139054331c9b_p381-403_CBO.pdf/south_italy_in_the_fourth_century_bc.pdf"
        ),
        "Cambridge University Press",
        "scholarly_history_chapter",
        "cambridge_ancient_history_south_italy",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_epirus_livy_pandosia",
        "Livy 8.24: Alexander of Molossis at Pandosia",
        "https://www.livius.org/sources/content/livy/livy-on-alexander-of-molossis/",
        "Livius.org scholarly ancient-history reference",
        "translated_primary_source",
        "livy_ab_urbe_condita_8_24",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_epirus_cambridge_nicol_thessalonica",
        "Venice: champion of a lost cause",
        (
            "https://www.cambridge.org/core/books/byzantium-and-venice/"
            "venice-champion-of-a-lost-cause/26FEAAE54E8A0AF269FD67671CF9A510"
        ),
        "Cambridge University Press",
        "scholarly_history_chapter",
        "nicol_byzantium_and_venice_chapter_10",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_epirus_cambridge_byzantium_exile",
        "Byzantium in exile",
        (
            "https://www.cambridge.org/core/books/abs/new-cambridge-medieval-history/"
            "byzantium-in-exile/543456566FA16509830EC0FED0B8B871"
        ),
        "Cambridge University Press",
        "scholarly_history_chapter",
        "new_cambridge_medieval_history_byzantium_exile",
    ),
    _source(
        "wave8_epirus_ime_late_byzantine_politics",
        "Politics in the Late Byzantine Period: Operations in the Balkans",
        "https://www.ime.gr/CHRONOS/10/en/p/pb2/pb2b2.html",
        "Foundation of the Hellenic World",
        "institutional_historical_reference",
        "foundation_hellenic_world_late_byzantine_politics",
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    note: str,
    source_ids: Iterable[str],
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
        "continuity_note": note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_EPIRUS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _ALEXANDER_EPIRUS_ID,
        "Epirote kingdom under Alexander I (343-331 BCE)",
        "monarchical_polity",
        -343,
        -331,
        "Epirus and Alexander's southern Italian expedition",
        (
            "Bounded to Alexander I's reign and the expedition ending with his death "
            "at Pandosia. No rating is inherited by earlier or later Epirote states, "
            "Molossians generally, Pyrrhus, a medieval despotate, or a modern state."
        ),
        ["wave8_epirus_cambridge_south_italy", "wave8_epirus_livy_pandosia"],
    ),
    _entity(
        _PANDOSIA_COALITION_ID,
        "Lucanian-Bruttian coalition at Pandosia (331 BCE)",
        "event_bounded_coalition",
        -331,
        -331,
        "Lucania and Bruttium",
        (
            "Event-bounded coalition attested against Alexander I at Pandosia. No "
            "rating is inherited by Lucanians, Bruttians, later Italian polities, "
            "or a modern state, and the coalition is not projected beyond 331 BCE."
        ),
        ["wave8_epirus_cambridge_south_italy", "wave8_epirus_livy_pandosia"],
    ),
    _entity(
        _PYRRHUS_EPIRUS_ID,
        "Epirote kingdom under Pyrrhus (297-272 BCE)",
        "monarchical_polity",
        -297,
        -272,
        "Epirus and Pyrrhus's western campaigns",
        (
            "Bounded to Pyrrhus's restored Epirote reign through his death at Argos. "
            "No rating is inherited by Alexander I's earlier kingdom, Macedon, "
            "Sicilian allies, medieval Epirus, an ethnic label, or a modern state."
        ),
        ["wave8_epirus_cambridge_pyrrhus", "wave8_epirus_plutarch_pyrrhus"],
    ),
    _entity(
        _ARGOS_COALITION_ID,
        "Argive-Antigonid-Spartan defensive coalition at Argos (272 BCE)",
        "event_bounded_coalition",
        -272,
        -272,
        "Argos and the Argolid",
        (
            "Event-bounded defenders and relief forces opposing Pyrrhus inside Argos. "
            "No rating is inherited by Argos, Macedon, Sparta, Antigonus II, their "
            "later states, or a modern state outside this coalition event."
        ),
        ["wave8_epirus_plutarch_pyrrhus"],
    ),
    _entity(
        _THEODORE_EPIRUS_ID,
        "Epirote state under Theodore Komnenos Doukas (1215-1230)",
        "medieval_successor_polity",
        1215,
        1230,
        "Epirus, Thessaly, and Macedonia",
        (
            "Bounded to Theodore's rule before and after the 1224 capture of "
            "Thessalonica, ending at Klokotnitsa. No rating is inherited by ancient "
            "Epirus, later Epirote regimes, Byzantium generally, or a modern state."
        ),
        [
            "wave8_epirus_cambridge_byzantium_exile",
            "wave8_epirus_cambridge_nicol_thessalonica",
        ],
    ),
    _entity(
        _LATIN_THESSALONICA_ID,
        "Latin Kingdom of Thessalonica (1204-1224)",
        "crusader_successor_polity",
        1204,
        1224,
        "Macedonia and Thessaly",
        (
            "Bounded from the post-Fourth-Crusade kingdom to Theodore's capture of "
            "Thessalonica. No rating is inherited by the Latin Empire, a later titular "
            "claim, Thessaly, Byzantium, the city itself, or a modern state."
        ),
        [
            "wave8_epirus_cambridge_byzantium_exile",
            "wave8_epirus_cambridge_nicol_thessalonica",
        ],
    ),
)


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


_ROW_HASHES = {
    "hced-Argos-272-1": "57cfcdfd5a555caec0e8fe2710aa609eec702a0a66757d30263af3bba4242075",
    "hced-Asculum, Apulia-279-1": "a8647fa5b3bdef7af84a1dab2b1536dde43efc7f62cf241f5a7825d2a4245185",
    "hced-Beneventum-275-1": "1966261b413a4184e045a541bbaa6b3101843a6a33b13051d0630cad96fcd84d",
    "hced-Heraclea, Lucania-280-1": "caacbafa2e0bb60e28a4d02cfb16696ae04e2c426a6440a40a644aad73613f49",
    "hced-Lilybaeum-277-1": "b5a3431d7bbfa4e40d1658784b9e3e2bbc32f9e2605f752a8c2683cc3f15aba7",
    "hced-Pandosia-331-1": "2f6f7c4692aa647a8d4929a9f2ced4f8b5b3abd47f6cdd0fa91618799b768122",
    "hced-Thessalonica1224-1": "8573d4e988fd0d3c151f161ac51d3db7b5043ad825ee269066feb3065f51433b",
    "hced-Thessalonica1264-1": "d886ca74fb2dc085ffcc715f75fd6d8413d60bc808666681bb495000bbbb65c4",
}

_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_EPIRUS_SOURCES
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    war_type: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "audit_note": audit_note,
    }


WAVE8_EPIRUS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Pandosia-331-1": _contract(
        "hced-Pandosia-331-1",
        _canonical("Battle of Pandosia", -331, "331 BCE"),
        "alexander_i_south_italy_331_bce",
        [_PANDOSIA_COALITION_ID],
        [_ALEXANDER_EPIRUS_ID],
        ["wave8_epirus_cambridge_south_italy", "wave8_epirus_livy_pandosia"],
        ["wave8_epirus_cambridge_south_italy", "wave8_epirus_livy_pandosia"],
        (
            "Livy and the Cambridge history identify Lucanian and Bruttian forces "
            "destroying Alexander I's separated force and killing the Epirote king. "
            "The raw Lucania label is corrected to the attested event coalition."
        ),
        "interstate_limited",
        confidence=0.92,
    ),
    "hced-Heraclea, Lucania-280-1": _contract(
        "hced-Heraclea, Lucania-280-1",
        _canonical("Battle of Heraclea", -280, "280 BCE"),
        "pyrrhic_war_280_275_bce",
        [_PYRRHUS_EPIRUS_ID],
        [_ROMAN_REPUBLIC_ID],
        [
            "wave8_epirus_cambridge_cicero_brutus",
            "wave8_epirus_cambridge_pyrrhus",
            "wave8_epirus_plutarch_pyrrhus",
        ],
        [
            "wave8_epirus_cambridge_cicero_brutus",
            "wave8_epirus_cambridge_pyrrhus",
            "wave8_epirus_plutarch_pyrrhus",
        ],
        (
            "The independent ancient and modern accounts agree that Pyrrhus defeated "
            "the Roman army at Heraclea. The winner is his bounded Epirote polity, "
            "not a timeless regional or ethnic Epirus identity."
        ),
        "interstate",
        confidence=0.96,
    ),
    "hced-Asculum, Apulia-279-1": _contract(
        "hced-Asculum, Apulia-279-1",
        _canonical("Battle of Asculum", -279, "279 BCE"),
        "pyrrhic_war_280_275_bce",
        [_PYRRHUS_EPIRUS_ID],
        [_ROMAN_REPUBLIC_ID],
        [
            "wave8_epirus_cambridge_cicero_brutus",
            "wave8_epirus_cambridge_pyrrhus",
            "wave8_epirus_plutarch_pyrrhus",
        ],
        [
            "wave8_epirus_cambridge_cicero_brutus",
            "wave8_epirus_cambridge_pyrrhus",
            "wave8_epirus_plutarch_pyrrhus",
        ],
        (
            "The sources support Pyrrhus's exceptionally costly tactical victory. "
            "It remains a win rather than being recoded as a draw merely because the "
            "losses made 'Pyrrhic victory' proverbial."
        ),
        "interstate",
        confidence=0.95,
    ),
    "hced-Beneventum-275-1": _contract(
        "hced-Beneventum-275-1",
        _canonical("Battle of Beneventum", -275, "275 BCE"),
        "pyrrhic_war_280_275_bce",
        [_ROMAN_REPUBLIC_ID],
        [_PYRRHUS_EPIRUS_ID],
        [
            "wave8_epirus_cambridge_pyrrhus",
            "wave8_epirus_cambridge_roman_commonwealth",
            "wave8_epirus_plutarch_pyrrhus",
        ],
        [
            "wave8_epirus_cambridge_pyrrhus",
            "wave8_epirus_cambridge_roman_commonwealth",
            "wave8_epirus_plutarch_pyrrhus",
        ],
        (
            "Cambridge's chronology identifies the Roman defeat of Pyrrhus at "
            "Malventum/Beneventum, while Plutarch supplies the battlefield account. "
            "The raw Rome victory is retained with time-valid identities."
        ),
        "interstate",
        confidence=0.94,
    ),
    "hced-Argos-272-1": _contract(
        "hced-Argos-272-1",
        _canonical("Battle of Argos", -272, "272 BCE"),
        "pyrrhus_peloponnese_campaign_272_bce",
        [_ARGOS_COALITION_ID],
        [_PYRRHUS_EPIRUS_ID],
        ["wave8_epirus_cambridge_pyrrhus", "wave8_epirus_plutarch_pyrrhus"],
        ["wave8_epirus_cambridge_pyrrhus", "wave8_epirus_plutarch_pyrrhus"],
        (
            "Plutarch distinguishes Argive defenders, Antigonus's Macedonian force, "
            "and Spartan pressure during Pyrrhus's failed entry and death. The raw "
            "Macedonia label is therefore replaced by one event-bounded coalition."
        ),
        "interstate_limited",
        confidence=0.91,
    ),
    "hced-Thessalonica1224-1": _contract(
        "hced-Thessalonica1224-1",
        _canonical(
            "Siege and capture of Thessalonica",
            1224,
            "1224",
            granularity="siege",
        ),
        "epirote_latin_war_1215_1224",
        [_THEODORE_EPIRUS_ID],
        [_LATIN_THESSALONICA_ID],
        [
            "wave8_epirus_cambridge_byzantium_exile",
            "wave8_epirus_cambridge_nicol_thessalonica",
        ],
        ["wave8_epirus_cambridge_nicol_thessalonica"],
        (
            "Nicol identifies Theodore's expansion and the fall of the Latin Kingdom "
            "of Thessalonica in 1224. HCED's 'Kingdom of Thessaly' loser is corrected "
            "to the Latin kingdom; no medieval identity crosses into ancient Epirus."
        ),
        "state_formation_conflict",
        confidence=0.93,
    ),
}


WAVE8_EPIRUS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Lilybaeum-277-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Lilybaeum-277-1"],
        "canonical_event": _canonical(
            "Proposed siege of Lilybaeum",
            -277,
            "late 277 or 276 BCE",
            date_precision="year_uncertain",
            granularity="chronology_unresolved_siege",
        ),
        "hold_category": "event_year_not_uniquely_defensible",
        "evidence_refs": [
            "wave8_epirus_cambridge_pyrrhus",
            "wave8_epirus_routledge_pyrrhic_war",
        ],
        "hold_reason": (
            "The failed Carthaginian-held siege is historically attested, but the "
            "reviewed scholarship places it in late 277 or 276 BCE. The exact HCED "
            "year -277 cannot be widened by this candidate-keyed helper or silently "
            "treated as certain. The row stays unrated; uncertainty is never a draw."
        ),
    },
    "hced-Thessalonica1264-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Thessalonica1264-1"],
        "canonical_event": _canonical(
            "Unverified Thessalonica engagement",
            1264,
            "1264",
            granularity="unsupported_named_engagement",
        ),
        "hold_category": "named_engagement_not_attested_by_reviewed_sources",
        "evidence_refs": ["wave8_epirus_ime_late_byzantine_politics"],
        "hold_reason": (
            "The Foundation of the Hellenic World documents John Palaiologos's 1264 "
            "intervention in Epirus and the resulting peace and suzerainty, but not "
            "a distinct battle at Thessalonica. A campaign result cannot be invented "
            "as this tactical event, and the unknown event outcome is never a draw."
        ),
    },
}

WAVE8_EPIRUS_EXCLUSIONS = WAVE8_EPIRUS_HOLDS
WAVE8_EPIRUS_CONTRACT_IDS = frozenset(WAVE8_EPIRUS_CONTRACTS)
WAVE8_EPIRUS_HOLD_IDS = frozenset(WAVE8_EPIRUS_HOLDS)
WAVE8_EPIRUS_EXCLUSION_IDS = WAVE8_EPIRUS_HOLD_IDS
WAVE8_EPIRUS_RESERVED_IDS = WAVE8_EPIRUS_CONTRACT_IDS | WAVE8_EPIRUS_HOLD_IDS
WAVE8_EPIRUS_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


WAVE8_EPIRUS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Argos-272-1": {
        "actions": ["withhold_country", "withhold_point"],
        "reason": (
            "HCED assigns modern country Italy to Argos in Greece; its city centroid "
            "also does not identify the multi-site fighting inside ancient Argos."
        ),
    },
    "hced-Asculum, Apulia-279-1": {
        "actions": ["withhold_point"],
        "reason": "The modern town coordinate is not a reviewed ancient battlefield point.",
    },
    "hced-Beneventum-275-1": {
        "actions": ["withhold_point"],
        "reason": "The Benevento centroid is not a reviewed Malventum battlefield point.",
    },
    "hced-Heraclea, Lucania-280-1": {
        "actions": ["withhold_point"],
        "reason": "The Heraclea locality is not a source-audited point for the field battle.",
    },
    "hced-Pandosia-331-1": {
        "actions": ["withhold_point"],
        "reason": "Ancient Pandosia's battlefield location is not fixed by this staged point.",
    },
    "hced-Thessalonica1224-1": {
        "actions": ["withhold_point"],
        "reason": "A city-centre coordinate cannot represent the footprint of the 1224 siege.",
    },
}
WAVE8_EPIRUS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_EPIRUS_LOCATION_QUARANTINE_REASONS
)
WAVE8_EPIRUS_COUNTRY_QUARANTINE_ADDITIONS = frozenset({"hced-Argos-272-1"})
WAVE8_EPIRUS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_EPIRUS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_EPIRUS_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_EPIRUS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_EPIRUS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_EPIRUS_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_EPIRUS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_EPIRUS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {}


WAVE8_EPIRUS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, tuple[str, ...]] = {
    "-331": ("battle of pandosia", "pandosia"),
    "-280": ("battle of heraclea", "heraclea", "heraclea lucania"),
    "-279": ("asculum", "asculum apulia", "battle of asculum"),
    "-277": ("lilybaeum", "siege of lilybaeum"),
    "-275": ("battle of beneventum", "beneventum", "malventum"),
    "-272": ("argos", "battle of argos"),
    "1224": ("siege and capture of thessalonica", "thessalonica"),
    "1264": ("battle of thessalonica", "thessalonica"),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_EPIRUS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_EPIRUS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_EPIRUS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_EPIRUS_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_EPIRUS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_EPIRUS_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_EPIRUS_HOLDS,
        "integration_dispositions": WAVE8_EPIRUS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_EPIRUS_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_EPIRUS_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_EPIRUS_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_EPIRUS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_EPIRUS_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_EPIRUS_SOURCES,
    }


def wave8_epirus_audit_signature() -> str:
    """Return the immutable digest of the complete adjudication state."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_EPIRUS_FINAL_AUDIT_SIGNATURE = (
    "95886e660a445c7f982f340e7d4b612104aefe84b4943a3c50f0ed4227be08de"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_EPIRUS_CONTRACTS), len(WAVE8_EPIRUS_HOLDS)) != (6, 2):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_EPIRUS_ENTITIES), len(WAVE8_EPIRUS_SOURCES)) != (6, 10):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_EPIRUS_RESERVED_IDS != WAVE8_EPIRUS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_EPIRUS_CONTRACT_IDS & WAVE8_EPIRUS_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotions and holds overlap")
    if WAVE8_EPIRUS_EXCLUSIONS is not WAVE8_EPIRUS_HOLDS:
        raise ValueError(f"{_LANE_NAME} exclusions diverged from terminal holds")
    if wave8_epirus_audit_signature() != WAVE8_EPIRUS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_EPIRUS_SOURCES}
    if len(source_by_id) != len(WAVE8_EPIRUS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({source["source_family_id"] for source in WAVE8_EPIRUS_SOURCES}) != len(
        WAVE8_EPIRUS_SOURCES
    ):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_EPIRUS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_EPIRUS_ENTITIES}
    if len(entity_by_id) != len(WAVE8_EPIRUS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    for entity in WAVE8_EPIRUS_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern state" not in note:
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if normalize_label(entity["name"]) == "epirus":
            raise ValueError(f"{_LANE_NAME} installed a timeless Epirus identity")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    allowed_entities = {_ROMAN_REPUBLIC_ID, _CARTHAGE_ID, *entity_by_id}
    used_new_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_EPIRUS_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
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
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= allowed_entities:
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        used_new_entities.update((set(side_1) | set(side_2)) & set(entity_by_id))
        year = int(canonical["year_low"])
        for entity_id in (set(side_1) | set(side_2)) & set(entity_by_id):
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if contract["result_type"] != "win" or contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} invented a draw or unknown result")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} contains an outcome override")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if not outcomes or not _is_sorted_unique(outcomes) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if contract["outcome_source_family_ids"] != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_new_entities != set(entity_by_id):
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
    for candidate_id, hold in WAVE8_EPIRUS_HOLDS.items():
        if hold["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} hold hash drifted")
        if forbidden_hold_keys & set(hold):
            raise ValueError(f"{_LANE_NAME} hold contains a rateable result")
        reason = str(hold["hold_reason"]).casefold()
        if "never a draw" not in reason:
            raise ValueError(f"{_LANE_NAME} hold does not preserve unknown-not-draw")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence drifted")
        used_sources.update(evidence)

    used_sources.update(
        source_id
        for entity in WAVE8_EPIRUS_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_EPIRUS_POINT_QUARANTINE_ADDITIONS != WAVE8_EPIRUS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_EPIRUS_COUNTRY_QUARANTINE_ADDITIONS != {"hced-Argos-272-1"}:
        raise ValueError(f"{_LANE_NAME} country quarantine contract changed")
    if not WAVE8_EPIRUS_COUNTRY_QUARANTINE_ADDITIONS <= WAVE8_EPIRUS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} quarantine references an unpromoted row")
    if (
        WAVE8_EPIRUS_OUTCOME_OVERRIDES
        or WAVE8_EPIRUS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_EPIRUS_CROSS_LANE_DISPOSITIONS
        or WAVE8_EPIRUS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_EPIRUS_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")
    for aliases in WAVE8_EPIRUS_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(aliases):
            raise ValueError(f"{_LANE_NAME} duplicate aliases drifted")


def _is_exact_epirus_label(value: Any) -> bool:
    return normalize_label(value) == "epirus"


def validate_wave8_epirus_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all eight exact-label rows and their immutable fingerprints."""

    _validate_static()
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_EPIRUS_CONTRACTS,
        WAVE8_EPIRUS_HOLDS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_epirus_label(row.get("side_1_raw"))
        or _is_exact_epirus_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_EPIRUS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Epirus inventory changed: {sorted(exact_label_ids)}"
        )
    return counts


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
    (int(year), normalize_label(alias))
    for year, aliases in WAVE8_EPIRUS_IWBD_ZERO_OVERLAP_AUDIT.items()
    for alias in aliases
}


def validate_wave8_epirus_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed if another source or lane adds an unreviewed probable twin."""

    validate_wave8_epirus_queue_contracts(hced_rows)
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_EPIRUS_RESERVED_IDS
        and (_row_year(row), normalize_label(row.get("name"))) in _DUPLICATE_MATCH_KEYS
    )
    if hced_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_matches}")
    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name"))) in _DUPLICATE_MATCH_KEYS
    )
    if iwbd_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_matches}")
    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_EPIRUS_CONTRACT_IDS
        and (_row_year(event), normalize_label(event.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_matches}"
        )
    return {
        "cross_lane_hced_dispositions": 0,
        "existing_release_duplicate_dispositions": 0,
        "integration_dispositions": 0,
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_epirus_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(release_entities, WAVE8_EPIRUS_ENTITIES, lane_name=_LANE_NAME)


def install_wave8_epirus_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(sources_by_id, WAVE8_EPIRUS_SOURCES, lane_name=_LANE_NAME)


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_EPIRUS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_EPIRUS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_epirus_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_epirus_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_EPIRUS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_epirus_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(Counter(str(item["cohort"]) for item in WAVE8_EPIRUS_CONTRACTS.values()).items())
    )


def wave8_epirus_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(WAVE8_EPIRUS_COUNTRY_QUARANTINE_ADDITIONS),
        "cross_lane_hced_dispositions": len(WAVE8_EPIRUS_CROSS_LANE_DISPOSITIONS),
        "exclusions": len(WAVE8_EPIRUS_EXCLUSIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_EPIRUS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_EPIRUS_HOLDS),
        "integration_dispositions": len(WAVE8_EPIRUS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_EPIRUS_IWBD_DUPLICATE_DISPOSITIONS),
        "new_entities": len(WAVE8_EPIRUS_ENTITIES),
        "new_sources": len(WAVE8_EPIRUS_SOURCES),
        "newly_rated_events": len(WAVE8_EPIRUS_CONTRACTS),
        "outcome_overrides": len(WAVE8_EPIRUS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(WAVE8_EPIRUS_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_EPIRUS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_EPIRUS_RESERVED_IDS),
    }


def wave8_epirus_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_EPIRUS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_EPIRUS_POINT_QUARANTINE_ADDITIONS,
    }
