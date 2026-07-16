"""Exact Wave 8 dispositions for HCED rows labelled ``Insubrian Gauls``.

The five rows cover four different campaigns and one source-level conflation.
This lane therefore installs only event-bounded Roman commands and opposing
Insubrian or coalition formations.  It opens no generic Insubrian, Gallic, or
Roman alias and carries no rating from one campaign into another.

The 223 BCE ``Adda`` row is deliberately not rated.  Polybius separates the
Roman crossing near the Adua-Padus confluence, where the army was harassed and
then withdrew under terms, from the later Roman victory after a circuit through
Cenomanian territory.  Combining the named crossing with the later result
would invent a single event that the source does not attest.
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
    "WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS",
    "WAVE8_INSUBRIAN_GAULS_CONTRACTS",
    "WAVE8_INSUBRIAN_GAULS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_INSUBRIAN_GAULS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_INSUBRIAN_GAULS_ENTITIES",
    "WAVE8_INSUBRIAN_GAULS_EXCLUSION_IDS",
    "WAVE8_INSUBRIAN_GAULS_EXCLUSIONS",
    "WAVE8_INSUBRIAN_GAULS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_INSUBRIAN_GAULS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_INSUBRIAN_GAULS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_INSUBRIAN_GAULS_HOLD_IDS",
    "WAVE8_INSUBRIAN_GAULS_HOLDS",
    "WAVE8_INSUBRIAN_GAULS_INTEGRATION_DISPOSITIONS",
    "WAVE8_INSUBRIAN_GAULS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_INSUBRIAN_GAULS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_INSUBRIAN_GAULS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_INSUBRIAN_GAULS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_INSUBRIAN_GAULS_NONPROMOTIONS",
    "WAVE8_INSUBRIAN_GAULS_OUTCOME_OVERRIDES",
    "WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_INSUBRIAN_GAULS_RESERVED_IDS",
    "WAVE8_INSUBRIAN_GAULS_SOURCES",
    "WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS",
    "install_wave8_insubrian_gauls_entities",
    "install_wave8_insubrian_gauls_sources",
    "promote_wave8_insubrian_gauls_contracts",
    "validate_wave8_insubrian_gauls_integration_dispositions",
    "validate_wave8_insubrian_gauls_queue_contracts",
    "wave8_insubrian_gauls_audit_signature",
    "wave8_insubrian_gauls_cohort_counts",
    "wave8_insubrian_gauls_counts",
    "wave8_insubrian_gauls_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Insubrian-Gallic formation audit"
_MODULE_OWNER = "wave8_insubrian_gauls"
_EVENT_ID_PREFIX = "hced_wave8_insubrian_gauls_"

_TELAMON_ROMANS_ID = "aemilius_atilius_roman_consular_armies_telamon_225_bce"
_TELAMON_GAULS_ID = "boii_insubres_taurisci_gaesatae_coalition_telamon_225_bce"
_CLASTIDIUM_ROMANS_ID = "marcellus_roman_relief_detachment_clastidium_222_bce"
_CLASTIDIUM_GAULS_ID = "insubrian_gaesatae_diversionary_force_clastidium_222_bce"
_MINCIO_ROMANS_ID = "cethegus_roman_consular_army_mincio_197_bce"
_MINCIO_INSUBRES_ID = "insubrian_field_force_hamilcar_mincio_197_bce"
_COMUM_ROMANS_ID = "marcellus_roman_consular_army_comum_196_bce"
_COMUM_INSUBRES_ID = "insubrian_comenses_field_force_comum_196_bce"


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
    granularity: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if crosscheck:
        roles.append("outcome_consistency_crosscheck")
    if granularity:
        roles.append("curated_reference_pending_claim_level_outcome_locator")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(roles)),
    }


WAVE8_INSUBRIAN_GAULS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_insubrian_polybius_book_2",
        "Polybius, Histories, Book 2: the Gallic war in northern Italy",
        (
            "https://www.perseus.tufts.edu/hopper/text.jsp?"
            "doc=Perseus%3Atext%3A1999.01.0234%3Abook%3D2"
        ),
        "Perseus Digital Library; Evelyn S. Shuckburgh translation",
        "translated_primary_source",
        "polybius_histories_book_2_shuckburgh",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_insubrian_szubelak_telamon",
        "The Gallic disaster at Telamon in 225 BC: the military and psychological aspect",
        "https://doi.org/10.4467/20844069PH.17.024.6939",
        "Prace Historyczne, Jagiellonian University Press",
        "peer_reviewed_open_access_article",
        "szubelak_telamon_2017",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_insubrian_rawlings_225_222",
        "The Gallic Wars, Northern Italy, 225-222 BC",
        "https://doi.org/10.1002/9781119099000.wbabat0310",
        "Wiley, The Encyclopedia of Ancient Battles",
        "peer_reviewed_scholarly_reference",
        "rawlings_gallic_wars_225_222",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_insubrian_plutarch_marcellus",
        "Plutarch, Life of Marcellus",
        "https://classics.mit.edu/Plutarch/marcellu.html",
        "MIT Internet Classics Archive",
        "translated_primary_source",
        "plutarch_marcellus_dryden_translation",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_insubrian_oxford_marcellus",
        "Claudius Marcellus, Marcus, consul 222, 214, 210, 208 BCE",
        "https://academic.oup.com/edited-volume/61673/chapter-abstract/548730436",
        "Oxford University Press, Oxford Classical Dictionary",
        "scholarly_classical_reference",
        "oxford_classical_dictionary_marcellus",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_insubrian_livy_32_30",
        "Livy, History of Rome, Book 32, chapter 30",
        "https://www.perseus.tufts.edu/hopper/text?doc=Liv.+32.30",
        "Perseus Digital Library; Cyrus Edmonds translation",
        "translated_primary_source",
        "livy_book_32_edmonds_translation",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_insubrian_livy_33_36",
        "Livy, History of Rome, Book 33, chapter 36",
        "https://www.perseus.tufts.edu/hopper/text?doc=Liv.+33.36",
        "Perseus Digital Library; Canon Roberts translation",
        "translated_primary_source",
        "livy_book_33_roberts_translation",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_insubrian_rawlings_201_191",
        "The Roman Conquest of Cisalpine Gaul, 201-191 BC",
        "https://doi.org/10.1002/9781119099000.wbabat0330",
        "Wiley, The Encyclopedia of Ancient Battles",
        "peer_reviewed_scholarly_reference",
        "rawlings_cisalpine_conquest_201_191",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_insubrian_hoyos_strategy",
        "Roman Strategy in Cisalpina, 224-222 and 203-191 B.C.",
        "https://doi.org/10.1017/S0066477400002185",
        "Cambridge University Press, Antichthon",
        "peer_reviewed_historical_article",
        "hoyos_roman_strategy_cisalpina",
        outcome=True,
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_insubrian_una_cisalpine_towns",
        "Les agglomerations celtiques en Cisalpine a l'epreuve de la conquete romaine",
        "https://una-editions.fr/les-agglomerations-celtiques-en-cisalpine/",
        "Ausonius Editions, Universite Bordeaux Montaigne",
        "peer_reviewed_archaeological_chapter",
        "tarpin_cisalpine_settlements_conquest",
        crosscheck=True,
        granularity=True,
    ),
    _source(
        "wave8_insubrian_cambridge_expansion_west",
        "Roman expansion in the west",
        "https://doi.org/10.1017/CHOL9780521234481.006",
        "Cambridge University Press, The Cambridge Ancient History",
        "scholarly_history_chapter",
        "cambridge_ancient_history_roman_expansion_west",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_insubrian_oxford_insubres",
        "Insubres",
        "https://academic.oup.com/edited-volume/61673/chapter-abstract/548938739",
        "Oxford University Press, Oxford Classical Dictionary",
        "scholarly_classical_reference",
        "oxford_classical_dictionary_insubres",
        crosscheck=True,
    ),
)


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
        "continuity_note": note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


_NO_INHERITANCE = (
    "No rating is inherited by an ethnic Insubrian or Gallic label, another "
    "Roman command, an earlier or later campaign, or any modern state."
)


WAVE8_INSUBRIAN_GAULS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _TELAMON_ROMANS_ID,
        "Aemilius Papus-Atilius Regulus Roman consular armies at Telamon (225 BCE)",
        "event_bounded_joint_command",
        -225,
        "Etruria near Telamon",
        (
            "The two consular forces that trapped the returning Gallic army from "
            "opposite directions at Telamon. " + _NO_INHERITANCE
        ),
        ["wave8_insubrian_polybius_book_2", "wave8_insubrian_szubelak_telamon"],
    ),
    _entity(
        _TELAMON_GAULS_ID,
        "Boii-Insubres-Taurisci-Gaesatae coalition at Telamon (225 BCE)",
        "event_bounded_coalition",
        -225,
        "Etruria on the coalition's northward withdrawal",
        (
            "Polybius and the modern battle study identify all four formations in "
            "the double-facing battle line. " + _NO_INHERITANCE
        ),
        [
            "wave8_insubrian_polybius_book_2",
            "wave8_insubrian_rawlings_225_222",
            "wave8_insubrian_szubelak_telamon",
        ],
    ),
    _entity(
        _CLASTIDIUM_ROMANS_ID,
        "Marcellus's Roman relief detachment at Clastidium (222 BCE)",
        "event_bounded_field_command",
        -222,
        "Clastidium and the lower Po",
        (
            "The cavalry and light infantry detached by consul Marcus Claudius "
            "Marcellus to relieve Clastidium. " + _NO_INHERITANCE
        ),
        [
            "wave8_insubrian_oxford_marcellus",
            "wave8_insubrian_plutarch_marcellus",
            "wave8_insubrian_polybius_book_2",
        ],
    ),
    _entity(
        _CLASTIDIUM_GAULS_ID,
        "Insubrian-Gaesatae diversionary force at Clastidium (222 BCE)",
        "event_bounded_coalition",
        -222,
        "Clastidium and the lower Po",
        (
            "The Insubrian diversionary force, reinforced by hired Gaesatae, that "
            "raised its siege and met Marcellus in battle. " + _NO_INHERITANCE
        ),
        [
            "wave8_insubrian_plutarch_marcellus",
            "wave8_insubrian_polybius_book_2",
            "wave8_insubrian_rawlings_225_222",
        ],
    ),
    _entity(
        _MINCIO_ROMANS_ID,
        "Gaius Cornelius Cethegus's Roman consular army at the Mincio (197 BCE)",
        "event_bounded_field_command",
        -197,
        "The Mincius frontier near Cenomanian territory",
        (
            "The consular army commanded by Gaius Cornelius Cethegus in Livy's "
            "Mincio engagement. " + _NO_INHERITANCE
        ),
        [
            "wave8_insubrian_livy_32_30",
            "wave8_insubrian_rawlings_201_191",
        ],
    ),
    _entity(
        _MINCIO_INSUBRES_ID,
        "Insubrian field force with Hamilcar at the Mincio (197 BCE)",
        "event_bounded_field_force",
        -197,
        "The Mincius frontier near Cenomanian territory",
        (
            "The Insubrian force defeated at the Mincio, with the Carthaginian "
            "Hamilcar attested among the captives. Cenomanian allegiance is not "
            "invented because Livy reports neutrality or a rear attack in variant "
            "accounts. " + _NO_INHERITANCE
        ),
        [
            "wave8_insubrian_cambridge_expansion_west",
            "wave8_insubrian_livy_32_30",
            "wave8_insubrian_oxford_insubres",
        ],
    ),
    _entity(
        _COMUM_ROMANS_ID,
        "Marcus Claudius Marcellus's Roman consular army at Comum (196 BCE)",
        "event_bounded_field_command",
        -196,
        "Comum territory south of Lake Larius",
        (
            "The 196 BCE consular army in the distinct victory in Comum territory, "
            "separate from its Boian campaign action. " + _NO_INHERITANCE
        ),
        [
            "wave8_insubrian_hoyos_strategy",
            "wave8_insubrian_livy_33_36",
            "wave8_insubrian_rawlings_201_191",
        ],
    ),
    _entity(
        _COMUM_INSUBRES_ID,
        "Insubrian-Comenses field force in Comum territory (196 BCE)",
        "event_bounded_coalition",
        -196,
        "Comum territory south of Lake Larius",
        (
            "The Insubres and armed Comenses whom Livy places in camp in Comum "
            "territory before the Roman victory and capture of the town. "
            + _NO_INHERITANCE
        ),
        [
            "wave8_insubrian_livy_33_36",
            "wave8_insubrian_oxford_insubres",
            "wave8_insubrian_una_cisalpine_towns",
        ],
    ),
)


_ROW_HASHES = {
    "hced-Adda-223-1": "8c2c8fcc758cfe398f9c49f3cfeccc5e0e1f03cede11faf62e425c4620c80972",
    "hced-Clastidium-222-1": "ccedeefad71ee1c90cf7486f249972f79987ad6c6d18ff14f16ec793fcff3e1f",
    "hced-Lake Como-196-1": "f1b7118b97cdd46fcb6f820f7cb76751e01403914595802fe05182c75d2413b6",
    "hced-Mincio-197-1": "019b2dafc6e30e6afccc70a2f9a1ac37e2c5fb41045b876925390c005eb082bf",
    "hced-Telamon-225-1": "960aa1b7054167f6ffdf6e45b2b23cb65c08e7c63721096c9d3a56ae9e640989",
}

_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_INSUBRIAN_GAULS_SOURCES
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
    winner_ids: Iterable[str],
    loser_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    historical_review: Mapping[str, Any],
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, winner_ids))),
        "side_2_entity_ids": sorted(set(map(str, loser_ids))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": "interstate_limited",
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
        "historical_review": dict(historical_review),
    }


WAVE8_INSUBRIAN_GAULS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Telamon-225-1": _contract(
        "hced-Telamon-225-1",
        _canonical("Battle of Telamon", -225, "225 BCE"),
        "gallic_war_telamon_225_bce",
        [_TELAMON_ROMANS_ID],
        [_TELAMON_GAULS_ID],
        [
            "wave8_insubrian_polybius_book_2",
            "wave8_insubrian_rawlings_225_222",
            "wave8_insubrian_szubelak_telamon",
        ],
        [
            "wave8_insubrian_polybius_book_2",
            "wave8_insubrian_rawlings_225_222",
            "wave8_insubrian_szubelak_telamon",
        ],
        (
            "Polybius and the peer-reviewed battle study identify a decisive Roman "
            "victory by two converging consular armies over a four-part Boii, "
            "Insubrian, Tauriscan, and Gaesatae coalition. The raw single-tribe label "
            "is replaced by that event-bounded formation."
        ),
        {
            "roman_commands": ["Lucius Aemilius Papus", "Gaius Atilius Regulus"],
            "coalition_components": ["Boii", "Gaesatae", "Insubres", "Taurisci"],
            "outcome": "roman_victory",
        },
        confidence=0.97,
    ),
    "hced-Clastidium-222-1": _contract(
        "hced-Clastidium-222-1",
        _canonical("Battle of Clastidium", -222, "222 BCE"),
        "roman_insubrian_war_223_222_bce",
        [_CLASTIDIUM_ROMANS_ID],
        [_CLASTIDIUM_GAULS_ID],
        [
            "wave8_insubrian_oxford_marcellus",
            "wave8_insubrian_plutarch_marcellus",
            "wave8_insubrian_polybius_book_2",
            "wave8_insubrian_rawlings_225_222",
        ],
        [
            "wave8_insubrian_oxford_marcellus",
            "wave8_insubrian_plutarch_marcellus",
            "wave8_insubrian_polybius_book_2",
            "wave8_insubrian_rawlings_225_222",
        ],
        (
            "Polybius independently describes Marcellus's cavalry and light-infantry "
            "relief force defeating the Insubrian diversion at Clastidium; Plutarch "
            "preserves the Gaesatae reinforcement and commander tradition."
        ),
        {
            "roman_commander": "Marcus Claudius Marcellus",
            "opposing_formation": "Insubrian force reinforced by hired Gaesatae",
            "outcome": "roman_victory",
        },
        confidence=0.97,
    ),
    "hced-Mincio-197-1": _contract(
        "hced-Mincio-197-1",
        _canonical("Battle of the Mincio", -197, "197 BCE"),
        "cisalpine_reconquest_197_196_bce",
        [_MINCIO_ROMANS_ID],
        [_MINCIO_INSUBRES_ID],
        [
            "wave8_insubrian_cambridge_expansion_west",
            "wave8_insubrian_livy_32_30",
            "wave8_insubrian_rawlings_201_191",
        ],
        [
            "wave8_insubrian_cambridge_expansion_west",
            "wave8_insubrian_livy_32_30",
            "wave8_insubrian_rawlings_201_191",
        ],
        (
            "Livy locates Cethegus and the Insubrian army on the Mincius and reports "
            "the Roman rout. Cenomanian troops are not assigned to either rated side: "
            "Livy says their elders rejected the revolt and preserves variant reports "
            "that they stayed inactive or struck the Insubrian rear."
        ),
        {
            "roman_commander": "Gaius Cornelius Cethegus",
            "cenomani_disposition": "not rated; neutrality or rear attack reported",
            "carthaginian_presence": "Hamilcar captured with the Insubrian force",
            "outcome": "roman_victory",
        },
        confidence=0.94,
    ),
    "hced-Lake Como-196-1": _contract(
        "hced-Lake Como-196-1",
        _canonical("Battle in the Comum territory", -196, "196 BCE"),
        "cisalpine_reconquest_197_196_bce",
        [_COMUM_ROMANS_ID],
        [_COMUM_INSUBRES_ID],
        [
            "wave8_insubrian_cambridge_expansion_west",
            "wave8_insubrian_hoyos_strategy",
            "wave8_insubrian_livy_33_36",
            "wave8_insubrian_rawlings_201_191",
            "wave8_insubrian_una_cisalpine_towns",
        ],
        [
            "wave8_insubrian_cambridge_expansion_west",
            "wave8_insubrian_hoyos_strategy",
            "wave8_insubrian_livy_33_36",
            "wave8_insubrian_rawlings_201_191",
        ],
        (
            "The raw 'Lake Como' shorthand is narrowed to Livy's distinct field "
            "battle in Comum territory, followed separately by capture of the town. "
            "Modern strategy and conquest studies retain Marcellus's victory against "
            "the Insubrian resistance while separating the Boian campaign episode."
        ),
        {
            "roman_commander": "Marcus Claudius Marcellus",
            "opposing_formation": "Insubres and armed Comenses in Comum territory",
            "boundary": "field battle precedes the later capture of Comum",
            "outcome": "roman_victory",
        },
        confidence=0.92,
    ),
}


WAVE8_INSUBRIAN_GAULS_HOLDS: dict[str, dict[str, Any]] = {}


def _terminal_exclusion(
    candidate_id: str,
    canonical_event: dict[str, Any],
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    historical_review: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "hold_category": category,
        "hold_reason": reason,
        "reviewed_outcome": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_granularity": "conflated_campaign_episodes",
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "terminal_hced_owner",
        },
        "historical_review": dict(historical_review),
    }


WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Adda-223-1": _terminal_exclusion(
        "hced-Adda-223-1",
        _canonical(
            "Conflated Adda crossing and later Insubrian battle",
            -223,
            "223 BCE",
            granularity="conflated_campaign_episodes",
        ),
        "named_site_and_outcome_belong_to_separate_campaign_episodes",
        (
            "Polybius separates the Adua-Padus crossing, where the Romans were "
            "harassed before making terms and leaving Insubrian territory, from the "
            "later decisive Roman victory after a circuit through Cenomanian lands. "
            "The later battlefield is not named Adda. Rating HCED's 'Adda' as a Roman "
            "win would fuse the named crossing to another engagement. The assertion "
            "cannot produce an Elo result and unknown is never made a draw."
        ),
        [
            "wave8_insubrian_hoyos_strategy",
            "wave8_insubrian_polybius_book_2",
            "wave8_insubrian_rawlings_225_222",
        ],
        {
            "named_episode": "Adua-Padus crossing, harassment, terms, withdrawal",
            "winning_episode": "later battle after circuit through Cenomanian territory",
            "repair_risk": "would merge two events and invent the later battle site",
        },
    )
}


WAVE8_INSUBRIAN_GAULS_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_INSUBRIAN_GAULS_HOLDS,
    **WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS,
}
WAVE8_INSUBRIAN_GAULS_EXCLUSIONS = WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS

WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS = frozenset(WAVE8_INSUBRIAN_GAULS_CONTRACTS)
WAVE8_INSUBRIAN_GAULS_HOLD_IDS = frozenset(WAVE8_INSUBRIAN_GAULS_HOLDS)
WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS
)
WAVE8_INSUBRIAN_GAULS_EXCLUSION_IDS = (
    WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSION_IDS
)
WAVE8_INSUBRIAN_GAULS_RESERVED_IDS = frozenset(
    WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS
    | WAVE8_INSUBRIAN_GAULS_HOLD_IDS
    | WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSION_IDS
)
WAVE8_INSUBRIAN_GAULS_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


WAVE8_INSUBRIAN_GAULS_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    "hced-Clastidium-222-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The staged coordinate is the modern Casteggio settlement, not a "
            "source-audited point for the ancient battlefield."
        ),
    },
    "hced-Lake Como-196-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The staged point lies in northern Lake Como, while the source supports "
            "a field battle in Comum territory without fixing a battlefield point."
        ),
    },
    "hced-Mincio-197-1": {
        "actions": ["withhold_point"],
        "reason": (
            "Livy identifies the Mincius river and camp separation but not the exact "
            "modern coordinate asserted by HCED."
        ),
    },
    "hced-Telamon-225-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The modern Talamone locality is not itself a source-audited coordinate "
            "for the multi-front ancient battlefield."
        ),
    },
}
WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_INSUBRIAN_GAULS_LOCATION_QUARANTINE_REASONS
)
WAVE8_INSUBRIAN_GAULS_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_INSUBRIAN_GAULS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_INSUBRIAN_GAULS_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_INSUBRIAN_GAULS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_INSUBRIAN_GAULS_IWBD_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_INSUBRIAN_GAULS_CROSS_LANE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_INSUBRIAN_GAULS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_INSUBRIAN_GAULS_INTEGRATION_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}


WAVE8_INSUBRIAN_GAULS_IWBD_ZERO_OVERLAP_AUDIT: dict[
    str, dict[str, Any]
] = {
    "hced-Adda-223-1": {
        "aliases": ("adda", "addua", "battle of adda", "battle on the adda"),
        "years": (-223, -223),
    },
    "hced-Clastidium-222-1": {
        "aliases": ("battle of clastidium", "clastidium"),
        "years": (-222, -222),
    },
    "hced-Lake Como-196-1": {
        "aliases": (
            "battle in the comum territory",
            "battle near lake como",
            "comum",
            "lake como",
        ),
        "years": (-196, -196),
    },
    "hced-Mincio-197-1": {
        "aliases": ("battle of mincio", "battle of the mincio", "mincio", "mincius"),
        "years": (-197, -197),
    },
    "hced-Telamon-225-1": {
        "aliases": ("battle of telamon", "talamone", "telamon"),
        "years": (-225, -225),
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_INSUBRIAN_GAULS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_INSUBRIAN_GAULS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_INSUBRIAN_GAULS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_INSUBRIAN_GAULS_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_INSUBRIAN_GAULS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(
            WAVE8_INSUBRIAN_GAULS_EXPECTED_CANDIDATE_IDS
        ),
        "holds": WAVE8_INSUBRIAN_GAULS_HOLDS,
        "integration_dispositions": WAVE8_INSUBRIAN_GAULS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_INSUBRIAN_GAULS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": WAVE8_INSUBRIAN_GAULS_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": (
            WAVE8_INSUBRIAN_GAULS_LOCATION_QUARANTINE_REASONS
        ),
        "outcome_overrides": WAVE8_INSUBRIAN_GAULS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_INSUBRIAN_GAULS_SOURCES,
        "terminal_exclusions": WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS,
    }


def wave8_insubrian_gauls_audit_signature() -> str:
    """Return the SHA-256 pin over the complete lane adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_INSUBRIAN_GAULS_FINAL_AUDIT_SIGNATURE = (
    "920e300ef51dbd0ce6badbc07109d27bcd764f79c5ec4bae4d858a9b824428dd"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_INSUBRIAN_GAULS_CONTRACTS),
        len(WAVE8_INSUBRIAN_GAULS_HOLDS),
        len(WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS),
    ) != (4, 0, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (
        len(WAVE8_INSUBRIAN_GAULS_ENTITIES),
        len(WAVE8_INSUBRIAN_GAULS_SOURCES),
    ) != (8, 12):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if (
        WAVE8_INSUBRIAN_GAULS_RESERVED_IDS
        != WAVE8_INSUBRIAN_GAULS_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    dispositions = (
        WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS,
        WAVE8_INSUBRIAN_GAULS_HOLD_IDS,
        WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(3)
        for j in range(i + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if (
        wave8_insubrian_gauls_audit_signature()
        != WAVE8_INSUBRIAN_GAULS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_INSUBRIAN_GAULS_SOURCES
    }
    if len(source_by_id) != len(WAVE8_INSUBRIAN_GAULS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    families = [
        str(source["source_family_id"])
        for source in WAVE8_INSUBRIAN_GAULS_SOURCES
    ]
    if len(families) != len(set(families)):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_INSUBRIAN_GAULS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_INSUBRIAN_GAULS_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_INSUBRIAN_GAULS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {"gauls", "insubres", "insubrian gauls", "rome"}
    for entity in WAVE8_INSUBRIAN_GAULS_ENTITIES:
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} identity is not event bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a timeless identity")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern state" not in note:
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_INSUBRIAN_GAULS_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["granularity"] != "engagement":
            raise ValueError(f"{_LANE_NAME} promoted a non-engagement")

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unbounded identity")
        used_entities.update(side_1)
        used_entities.update(side_2)
        year = int(canonical["year_low"])
        for entity_id in (*side_1, *side_2):
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")

        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["actor_override"] is not True
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} outcome or actor policy drifted")
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
            not outcomes
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        expected_families = sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identities are not exactly consumed")

    forbidden_nonpromotion_keys = {
        "losers",
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
        "winners",
    }
    for candidate_id, item in WAVE8_INSUBRIAN_GAULS_NONPROMOTIONS.items():
        if item["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} nonpromotion hash drifted")
        if forbidden_nonpromotion_keys & set(item):
            raise ValueError(f"{_LANE_NAME} nonpromotion contains a rateable result")
        if item["duplicate_ownership"]["owner_module"] != _MODULE_OWNER:
            raise ValueError(f"{_LANE_NAME} nonpromotion ownership drifted")
        evidence = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} nonpromotion evidence drifted")
        used_sources.update(evidence)
    exclusion = WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS["hced-Adda-223-1"]
    if (
        exclusion["disposition"] != "terminal_exclusion"
        or exclusion["terminal_exclusion"] is not True
        or exclusion["reviewed_outcome"] != "unknown"
        or exclusion["unknown_is_never_draw"] is not True
    ):
        raise ValueError(f"{_LANE_NAME} Adda exclusion drifted")

    used_sources.update(
        source_id
        for entity in WAVE8_INSUBRIAN_GAULS_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if (
        WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS
        != WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_INSUBRIAN_GAULS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if (
        WAVE8_INSUBRIAN_GAULS_OUTCOME_OVERRIDES
        or WAVE8_INSUBRIAN_GAULS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_INSUBRIAN_GAULS_CROSS_LANE_DISPOSITIONS
        or WAVE8_INSUBRIAN_GAULS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_INSUBRIAN_GAULS_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")
    if (
        set(WAVE8_INSUBRIAN_GAULS_IWBD_ZERO_OVERLAP_AUDIT)
        != WAVE8_INSUBRIAN_GAULS_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for item in WAVE8_INSUBRIAN_GAULS_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(item["aliases"]):
            raise ValueError(f"{_LANE_NAME} duplicate aliases drifted")
        low, high = map(int, item["years"])
        if low > high:
            raise ValueError(f"{_LANE_NAME} duplicate year range drifted")


def _is_exact_insubrian_gauls_label(value: Any) -> bool:
    return normalize_label(value) == "insubrian gauls"


def validate_wave8_insubrian_gauls_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all five exact-label rows and their immutable fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_INSUBRIAN_GAULS_CONTRACTS,
        WAVE8_INSUBRIAN_GAULS_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_insubrian_gauls_label(row.get("side_1_raw"))
        or _is_exact_insubrian_gauls_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_INSUBRIAN_GAULS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Insubrian Gauls inventory changed: "
            f"{sorted(exact_label_ids)}"
        )
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_INSUBRIAN_GAULS_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(
            WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS
        ),
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
    (year, normalize_label(alias))
    for item in WAVE8_INSUBRIAN_GAULS_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(item["years"][0]), int(item["years"][1]) + 1)
    for alias in item["aliases"]
}


def validate_wave8_insubrian_gauls_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed if another queue, lane, or release adds a probable twin."""

    validate_wave8_insubrian_gauls_queue_contracts(hced_rows)
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_INSUBRIAN_GAULS_RESERVED_IDS
        and (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if hced_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_matches}"
        )

    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if iwbd_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_matches}"
        )

    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id")
        not in WAVE8_INSUBRIAN_GAULS_CONTRACT_IDS
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
        "iwbd_zero_overlap_candidates": len(
            WAVE8_INSUBRIAN_GAULS_IWBD_ZERO_OVERLAP_AUDIT
        ),
    }


def install_wave8_insubrian_gauls_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_INSUBRIAN_GAULS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_insubrian_gauls_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_INSUBRIAN_GAULS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_INSUBRIAN_GAULS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_insubrian_gauls_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_insubrian_gauls_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_INSUBRIAN_GAULS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_insubrian_gauls_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_INSUBRIAN_GAULS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_insubrian_gauls_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_INSUBRIAN_GAULS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_INSUBRIAN_GAULS_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_INSUBRIAN_GAULS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_INSUBRIAN_GAULS_HOLDS),
        "integration_dispositions": len(
            WAVE8_INSUBRIAN_GAULS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_INSUBRIAN_GAULS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_INSUBRIAN_GAULS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_INSUBRIAN_GAULS_ENTITIES),
        "new_sources": len(WAVE8_INSUBRIAN_GAULS_SOURCES),
        "newly_rated_events": len(WAVE8_INSUBRIAN_GAULS_CONTRACTS),
        "outcome_overrides": len(WAVE8_INSUBRIAN_GAULS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_INSUBRIAN_GAULS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_INSUBRIAN_GAULS_RESERVED_IDS),
        "terminal_exclusions": len(
            WAVE8_INSUBRIAN_GAULS_TERMINAL_EXCLUSIONS
        ),
    }


def wave8_insubrian_gauls_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    """Return immutable promoted-only location quarantine additions."""

    _validate_static()
    return {
        "country": WAVE8_INSUBRIAN_GAULS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_INSUBRIAN_GAULS_POINT_QUARANTINE_ADDITIONS,
    }
