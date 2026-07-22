"""Fail-closed exact dispositions for six HCED Sertorian War rows.

The source labels name commanders, places, and a timeless ``Rome`` rather than
two reusable polity identities.  This lane therefore installs one
conflict-bounded, alias-free Sertorian faction and binds it only to six fully
fingerprinted HCED rows.  Four rows have defensible tactical outcomes, Sucro
remains unresolved, and Murviedro is a false-draw duplicate of the reviewed
Turia/Segontia engagement.

The chronology of the middle campaigns differs by one year between modern
reconstructions.  Lauron, Turia/Segontia, and Calagurris retain explicit
one-year uncertainty ranges instead of silently selecting either chronology.
No generic commander, popularis, Lusitanian, Celtiberian, or place alias is
opened, and the three Wikidata records remain fingerprinted discovery-only
duplicates with no rating outcome.
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
    "WAVE8_SERTORIAN_CONTRACT_IDS",
    "WAVE8_SERTORIAN_CONTRACTS",
    "WAVE8_SERTORIAN_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SERTORIAN_DISCOVERY_DISPOSITIONS",
    "WAVE8_SERTORIAN_DISCOVERY_EXPECTED",
    "WAVE8_SERTORIAN_DISCOVERY_ROW_HASHES",
    "WAVE8_SERTORIAN_ENTITIES",
    "WAVE8_SERTORIAN_EXPECTED_CANDIDATE_IDS",
    "WAVE8_SERTORIAN_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SERTORIAN_HOLD_IDS",
    "WAVE8_SERTORIAN_HOLDS",
    "WAVE8_SERTORIAN_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_SERTORIAN_LOCATION_QUARANTINE_REASONS",
    "WAVE8_SERTORIAN_NONPROMOTIONS",
    "WAVE8_SERTORIAN_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SERTORIAN_RESERVED_IDS",
    "WAVE8_SERTORIAN_ROW_HASHES",
    "WAVE8_SERTORIAN_SOURCES",
    "WAVE8_SERTORIAN_TERMINAL_EXCLUSION_IDS",
    "WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS",
    "install_wave8_sertorian_entities",
    "install_wave8_sertorian_sources",
    "promote_wave8_sertorian_contracts",
    "validate_wave8_sertorian_discovery_dispositions",
    "validate_wave8_sertorian_queue_contracts",
    "wave8_sertorian_audit_signature",
    "wave8_sertorian_cohort_counts",
    "wave8_sertorian_counts",
    "wave8_sertorian_location_quarantine_additions",
    "wave8_sertorian_metadata",
)


_LANE_NAME = "Wave 8 exact Sertorian War audit"
_MODULE_OWNER = "military_elo.promotion.wave8_sertorian"
_EVENT_ID_PREFIX = "hced_wave8_sertorian_"

_ROMAN_REPUBLIC = "roman_republic"
_SERTORIAN_FACTION = "sertorian_faction_hispania_80_72_bce"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
    chronology: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if chronology:
        roles.append("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-21",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(roles)),
    }


WAVE8_SERTORIAN_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_sertorian_plutarch_sertorius",
        "Plutarch, Life of Sertorius, especially 11-23",
        "https://classics.mit.edu/Plutarch/sertoriu.html",
        "Internet Classics Archive, Massachusetts Institute of Technology",
        "ancient_primary_narrative_translation",
        "plutarch_parallel_lives_sertorius",
        outcome=True,
        chronology=True,
    ),
    _source(
        "wave8_sertorian_plutarch_pompey_19",
        "Plutarch, Life of Pompey 19: the doubtful issue at Sucro",
        "https://lexundria.com/plut_pomp/19/prr",
        "Lexundria; Bernadotte Perrin translation",
        "ancient_primary_narrative_translation",
        "plutarch_parallel_lives_pompey",
        outcome=True,
    ),
    _source(
        "wave8_sertorian_appian_civil_wars_1",
        "Appian, Civil Wars 1.108-112: Sertorian government and campaigns",
        (
            "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/"
            "Appian/Civil_Wars/1%2A.html"
        ),
        "LacusCurtius, University of Chicago; Horace White translation",
        "ancient_primary_narrative_translation",
        "appian_civil_wars_horace_white",
        outcome=True,
        chronology=True,
    ),
    _source(
        "wave8_sertorian_sallust_histories_translation",
        "Sallust, Histories fragments: the Baetis crossing and Sertorian War",
        "https://www.attalus.org/translate/sallust.html",
        "Attalus; translated fragments of Sallust's Histories",
        "ancient_primary_fragment_translation",
        "sallust_histories",
        outcome=True,
    ),
    _source(
        "wave8_sertorian_sallust_histories_2_latin",
        "Sallust, Histories book 2 fragments: Turia and Durium toponymy",
        "https://www.attalus.org/latin/sallust2.html",
        "Attalus; Latin fragments of Sallust's Histories",
        "ancient_primary_fragment_edition",
        "sallust_histories",
        chronology=True,
    ),
    _source(
        "wave8_sertorian_frontinus_strategemata_2",
        "Frontinus, Strategemata 2.5.31: Sertorius's Lauron operation",
        (
            "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/"
            "Frontinus/Strategemata/2%2A.html"
        ),
        "LacusCurtius, University of Chicago; Charles Bennett translation",
        "ancient_primary_military_treatise_translation",
        "frontinus_strategemata_bennett",
        outcome=True,
    ),
    _source(
        "wave8_sertorian_livy_periochae_91_95",
        "Livy, Periochae 92-93: Sucro, Segontia, and Calagurris",
        "https://www.livius.org/sources/content/livy/livy-periochae-91-95/",
        "Livius.org; translation of Livy's summaries",
        "ancient_primary_epitome_translation",
        "livy_periochae",
        outcome=True,
        chronology=True,
    ),
    _source(
        "wave8_sertorian_ladon_lauron",
        (
            "Pompejusz versus Sertoriusz: rozważania o bitwie pod Lauro "
            "(Pompey versus Sertorius: considerations about the battle of Lauro)"
        ),
        (
            "https://bazhum.muzhp.pl/media/texts/"
            "przeglad-historyczno-wojskowy/2014-tom-15-66-numer-1-247/"
            "przeglad_historyczno_wojskowy-r2014-t15_66-n1_247-s7-16.pdf"
        ),
        "Przegląd Historyczno-Wojskowy",
        "peer_reviewed_historical_article",
        "ladon_lauron_2014",
        outcome=True,
        chronology=True,
    ),
    _source(
        "wave8_sertorian_noguera_jra_chronology",
        "New perspectives on the Sertorian War in northeastern Hispania",
        (
            "https://www.cambridge.org/core/journals/"
            "journal-of-roman-archaeology/article/"
            "new-perspectives-on-the-sertorian-war-in-northeastern-hispania-"
            "archaeological-surveys-of-the-roman-camps-of-the-lower-river-ebro/"
            "9DD77C6186FE97AFBE0C388AFBCBCC08"
        ),
        "Cambridge University Press, Journal of Roman Archaeology",
        "peer_reviewed_archaeological_article",
        "noguera_et_al_jra_sertorian_camps",
        chronology=True,
    ),
    _source(
        "wave8_sertorian_konrad_commentary",
        "A Historical Commentary on Plutarch's Life of Sertorius",
        "https://www.proquest.com/docview/303354083/",
        "ProQuest; University of North Carolina at Chapel Hill",
        "scholarly_historical_commentary_dissertation",
        "konrad_plutarch_sertorius_commentary",
        chronology=True,
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_SERTORIAN_SOURCES
}


WAVE8_SERTORIAN_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _SERTORIAN_FACTION,
        "name": "Sertorian Faction in Hispania (80-72 BCE)",
        "kind": "civil_war_faction",
        "start_year": -80,
        "end_year": -72,
        "region": "Hispania",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Conflict-bounded to Sertorius's return from Africa and assumption "
            "of Lusitanian command in 80 BCE through the faction's terminal "
            "defeat under Perperna in 72 BCE. No rating is inherited from or "
            "transferred to the Roman Republic, earlier Marian forces, the "
            "populares as a timeless category, Lusitanians, Celtiberians, an "
            "individual commander, or any successor town or polity. Candidate-"
            "keyed contracts are the only resolution path."
        ),
        "source_ids": [
            "wave8_sertorian_appian_civil_wars_1",
            "wave8_sertorian_plutarch_sertorius",
        ],
    },
)


WAVE8_SERTORIAN_ROW_HASHES: dict[str, str] = {
    "hced-Baetis-80-1": (
        "e4bfa0914c69aa63ab8106b93454124e1823f19646f5e6cb8af679454fc4c00f"
    ),
    "hced-Calahorra-74-1": (
        "15a3db557af851255251e16fcdafb7ebf7edde27d9253972dac3059096b7a7d3"
    ),
    "hced-Lauron-76-1": (
        "38948074d54e19f89c12ad25a68d00c39c43f20513569eb69cdf68ec863d5f57"
    ),
    "hced-Murviedro-75-1": (
        "beb212f1a76123b4fc87e19017756f4f80e90abac9dc44569862a9614b9d8e6b"
    ),
    "hced-Sucro-75-1": (
        "eb4290476a96903ee66ce926ea8091c15c1875fc2349f1bc1a9aef1d724b4dd8"
    ),
    "hced-Turia-75-1": (
        "26573cc773383c3d86f8fcbd7d3935024b3a1d00a4d3523af816d96eb95bb557"
    ),
}


def _canonical(
    name: str,
    year_low: int,
    year_high: int,
    date_text: str,
    *,
    date_precision: str,
    granularity: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{year_high}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": year_high,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    source_date_override: bool = False,
    date_source_ids: Iterable[str] = (),
    boundary_guard: str | None = None,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    contract: dict[str, Any] = {
        "raw_row_sha256": WAVE8_SERTORIAN_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "sertorian_war_80_72_bce",
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "civil_war",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_conflict_bounded_faction",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "source_date_override": source_date_override,
        "date_source_ids": sorted(set(map(str, date_source_ids))),
        "audit_note": audit_note,
    }
    if boundary_guard is not None:
        contract["boundary_guard"] = boundary_guard
    return contract


_CHRONOLOGY_SOURCES = (
    "wave8_sertorian_konrad_commentary",
    "wave8_sertorian_noguera_jra_chronology",
)


WAVE8_SERTORIAN_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Baetis-80-1": _contract(
        "hced-Baetis-80-1",
        _canonical(
            "Battle on the Baetis",
            -80,
            -80,
            "80 BCE",
            date_precision="year",
            granularity="opposed_river_crossing_and_battle",
        ),
        [_SERTORIAN_FACTION],
        [_ROMAN_REPUBLIC],
        1,
        [
            "wave8_sertorian_plutarch_sertorius",
            "wave8_sertorian_sallust_histories_translation",
        ],
        [
            "wave8_sertorian_plutarch_sertorius",
            "wave8_sertorian_sallust_histories_translation",
        ],
        (
            "The contract is limited to Fufidius's opposed Baetis crossing and "
            "rout, for which Plutarch reports two thousand Roman dead and "
            "Sallust preserves the steep-bank and ford setting. It does not "
            "absorb Cotta's sea fight or the other early Sertorian victories."
        ),
        confidence=0.94,
    ),
    "hced-Lauron-76-1": _contract(
        "hced-Lauron-76-1",
        _canonical(
            "Lauron siege-relief operation",
            -77,
            -76,
            "77-76 BCE (chronology conflict)",
            date_precision="year_conflict",
            granularity="siege_relief_operation",
        ),
        [_SERTORIAN_FACTION],
        [_ROMAN_REPUBLIC],
        1,
        [
            "wave8_sertorian_appian_civil_wars_1",
            "wave8_sertorian_frontinus_strategemata_2",
            "wave8_sertorian_konrad_commentary",
            "wave8_sertorian_ladon_lauron",
            "wave8_sertorian_noguera_jra_chronology",
            "wave8_sertorian_plutarch_sertorius",
        ],
        [
            "wave8_sertorian_appian_civil_wars_1",
            "wave8_sertorian_frontinus_strategemata_2",
            "wave8_sertorian_ladon_lauron",
            "wave8_sertorian_plutarch_sertorius",
        ],
        (
            "The reviewed boundary combines the siege, Pompey's attempted "
            "relief, the foraging ambush, and destruction of the relief legion, "
            "ending when Pompey could not intervene and Lauron surrendered. The "
            "later burning and punitive execution of a cohort are excluded from "
            "the scored combat outcome."
        ),
        confidence=0.88,
        source_date_override=True,
        date_source_ids=_CHRONOLOGY_SOURCES,
    ),
    "hced-Turia-75-1": _contract(
        "hced-Turia-75-1",
        _canonical(
            "Battle of Segontia (Turia/Saguntum tradition)",
            -76,
            -75,
            "76-75 BCE (chronology conflict)",
            date_precision="year_conflict",
            granularity="whole_noon_to_night_field_battle",
        ),
        [_ROMAN_REPUBLIC],
        [_SERTORIAN_FACTION],
        1,
        [
            "wave8_sertorian_appian_civil_wars_1",
            "wave8_sertorian_konrad_commentary",
            "wave8_sertorian_livy_periochae_91_95",
            "wave8_sertorian_noguera_jra_chronology",
            "wave8_sertorian_plutarch_sertorius",
            "wave8_sertorian_sallust_histories_2_latin",
        ],
        [
            "wave8_sertorian_appian_civil_wars_1",
            "wave8_sertorian_livy_periochae_91_95",
            "wave8_sertorian_plutarch_sertorius",
        ],
        (
            "This guarded contract owns only the complete noon-to-night field "
            "battle, ending after the Roman rally reversed the initial action "
            "and Sertorius withdrew. It excludes the next evening's attempted "
            "encirclement of Metellus's camp. The sources disagree at wing level, "
            "so the whole-field result is retained only at reduced confidence."
        ),
        confidence=0.72,
        source_date_override=True,
        date_source_ids=_CHRONOLOGY_SOURCES,
        boundary_guard=(
            "rate_only_complete_field_battle_ending_in_sertorian_withdrawal; "
            "never reinterpret a single wing or the next-evening camp action"
        ),
    ),
    "hced-Calahorra-74-1": _contract(
        "hced-Calahorra-74-1",
        _canonical(
            "Sertorian relief of Calagurris",
            -75,
            -74,
            "75-74 BCE (chronology conflict)",
            date_precision="year_conflict",
            granularity="siege_relief_battle",
        ),
        [_SERTORIAN_FACTION],
        [_ROMAN_REPUBLIC],
        1,
        [
            "wave8_sertorian_appian_civil_wars_1",
            "wave8_sertorian_konrad_commentary",
            "wave8_sertorian_livy_periochae_91_95",
            "wave8_sertorian_noguera_jra_chronology",
        ],
        [
            "wave8_sertorian_appian_civil_wars_1",
            "wave8_sertorian_livy_periochae_91_95",
        ],
        (
            "Appian and Livy's epitome support Sertorius's attack on the "
            "senatorial camp around Calagurris, the besiegers' defeat, and the "
            "raising of the siege. The contract ends with that relief and does "
            "not absorb the final post-Sertorius destruction of Calagurris in "
            "72 BCE; HCED's participant-place noise is discarded."
        ),
        confidence=0.88,
        source_date_override=True,
        date_source_ids=_CHRONOLOGY_SOURCES,
    ),
}


WAVE8_SERTORIAN_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Sucro-75-1": {
        "raw_row_sha256": WAVE8_SERTORIAN_ROW_HASHES["hced-Sucro-75-1"],
        "canonical_event": _canonical(
            "Battle of Sucro",
            -76,
            -75,
            "76-75 BCE (chronology conflict)",
            date_precision="year_conflict",
            granularity="whole_battle_with_opposed_wing_results",
        ),
        "cohort": "sertorian_war_80_72_bce",
        "disposition": "hold",
        "hold_category": "whole_battle_outcome_not_unique_across_sectors",
        "result_type": "unknown",
        "reviewed_outcome": "unknown",
        "unknown_is_never_draw": True,
        "raw_winner_raw": "Rome",
        "raw_winner_loser_complete": True,
        "evidence_refs": [
            "wave8_sertorian_appian_civil_wars_1",
            "wave8_sertorian_konrad_commentary",
            "wave8_sertorian_livy_periochae_91_95",
            "wave8_sertorian_noguera_jra_chronology",
            "wave8_sertorian_plutarch_pompey_19",
            "wave8_sertorian_plutarch_sertorius",
        ],
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_nonpromotion",
        },
        "hold_reason": (
            "Plutarch calls the whole-battle issue doubtful because one wing on "
            "each side prevailed, Livy's epitome says the outcome was unclear, "
            "and Appian separates Sertorius-Pompey from Metellus-Perperna sectors. "
            "HCED's whole-row Roman victory is unsupported. The event remains "
            "unknown, never a draw; a future sector split requires a new audit."
        ),
    },
}


WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Murviedro-75-1": {
        "raw_row_sha256": WAVE8_SERTORIAN_ROW_HASHES["hced-Murviedro-75-1"],
        "canonical_event": _canonical(
            "Battle of Segontia (Turia/Saguntum tradition)",
            -76,
            -75,
            "76-75 BCE (chronology conflict)",
            date_precision="year_conflict",
            granularity="duplicate_of_reviewed_whole_field_battle",
        ),
        "cohort": "sertorian_war_80_72_bce",
        "disposition": "exclude_duplicate_of_reviewed_candidate",
        "hold_category": "duplicate_place_name_for_same_engagement",
        "terminal_exclusion": True,
        "result_type": "unknown",
        "reviewed_outcome": "invalid_duplicate",
        "unknown_is_never_draw": True,
        "raw_winner_raw": "Draw",
        "raw_winner_loser_complete": False,
        "duplicate_of_candidate_id": "hced-Turia-75-1",
        "false_source_draw_rejected": True,
        "evidence_refs": [
            "wave8_sertorian_appian_civil_wars_1",
            "wave8_sertorian_konrad_commentary",
            "wave8_sertorian_plutarch_sertorius",
            "wave8_sertorian_sallust_histories_2_latin",
        ],
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_duplicate_exclusion",
        },
        "hold_reason": (
            "Murviedro is modern Sagunto encoded as a second row for the same "
            "Turia/Segontia engagement owned by hced-Turia-75-1. Ancient and "
            "modern sources preserve competing Turia, Saguntum, Seguntia, and "
            "Durium toponymies, not two independently rateable battles. The "
            "incomplete source Draw is false and is rejected rather than emitted "
            "or inherited by the canonical owner."
        ),
    },
}


WAVE8_SERTORIAN_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_SERTORIAN_HOLDS,
    **WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS,
}
WAVE8_SERTORIAN_CONTRACT_IDS = frozenset(WAVE8_SERTORIAN_CONTRACTS)
WAVE8_SERTORIAN_HOLD_IDS = frozenset(WAVE8_SERTORIAN_HOLDS)
WAVE8_SERTORIAN_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS
)
WAVE8_SERTORIAN_RESERVED_IDS = frozenset(
    WAVE8_SERTORIAN_CONTRACT_IDS
    | WAVE8_SERTORIAN_HOLD_IDS
    | WAVE8_SERTORIAN_TERMINAL_EXCLUSION_IDS
)
WAVE8_SERTORIAN_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_SERTORIAN_ROW_HASHES)


WAVE8_SERTORIAN_POINT_QUARANTINE_ADDITIONS = WAVE8_SERTORIAN_RESERVED_IDS
WAVE8_SERTORIAN_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_SERTORIAN_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_SERTORIAN_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_SERTORIAN_COUNTRY_QUARANTINE_ADDITIONS,
}
_POINT_REASONS = {
    "hced-Baetis-80-1": (
        "Sources establish a Baetis bank or ford, not HCED's exact point."
    ),
    "hced-Lauron-76-1": (
        "The Llíria identification is disputed and cannot own an exact point."
    ),
    "hced-Sucro-75-1": (
        "Ancient Sucro and its battlefield remain archaeologically unresolved."
    ),
    "hced-Turia-75-1": (
        "The upper-Turia point conflicts with both Valencian and inland "
        "Segontia reconstructions."
    ),
    "hced-Calahorra-74-1": (
        "Calagurris-Calahorra is defensible, but the besieging camp and battle "
        "point are not."
    ),
    "hced-Murviedro-75-1": (
        "This duplicate Sagunto geocode cannot locate the disputed Segontia "
        "battlefield."
    ),
}
WAVE8_SERTORIAN_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": reason,
        "retain_modern_location_country": "Spain",
    }
    for candidate_id, reason in sorted(_POINT_REASONS.items())
}


WAVE8_SERTORIAN_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q60524412": (
        "4c4f0ae442491e3cd752c420ed3b21efca75c548f75fb6b1d908a28e97f97824"
    ),
    "Q60524449": (
        "bf8ba315fea27fd64b5fe1dc0290dc4eb7446b910f26ec514ec9584ac4fc6616"
    ),
    "Q9173528": (
        "e5182d2f4fdc8c828f66f5869aa5a436d060b3d858f54735ba7a6906c33c4686"
    ),
}
WAVE8_SERTORIAN_DISCOVERY_EXPECTED: dict[str, dict[str, Any]] = {
    "Q60524412": {
        "date": "-0075-01-01T00:00:00Z",
        "hced_candidate_id": "hced-Lauron-76-1",
        "name": "Battle of Lauron",
    },
    "Q60524449": {
        "date": "-0074-01-01T00:00:00Z",
        "hced_candidate_id": "hced-Sucro-75-1",
        "name": "Battle of Sucro",
    },
    "Q9173528": {
        "date": "-0074-01-01T00:00:00Z",
        "hced_candidate_id": "hced-Turia-75-1",
        "name": "Battle of Saguntum",
        "also_excludes_hced_candidate_id": "hced-Murviedro-75-1",
    },
}
WAVE8_SERTORIAN_DISCOVERY_DISPOSITIONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "source_dataset": "wikidata-battles",
        "disposition": "discovery_only_duplicate",
        "hced_candidate_id": str(expected["hced_candidate_id"]),
        "outcome_disposition": "unknown_never_draw",
        **(
            {
                "also_excludes_hced_candidate_id": str(
                    expected["also_excludes_hced_candidate_id"]
                )
            }
            if expected.get("also_excludes_hced_candidate_id")
            else {}
        ),
    }
    for candidate_id, expected in sorted(WAVE8_SERTORIAN_DISCOVERY_EXPECTED.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_SERTORIAN_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_SERTORIAN_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_dispositions": WAVE8_SERTORIAN_DISCOVERY_DISPOSITIONS,
        "discovery_expected": WAVE8_SERTORIAN_DISCOVERY_EXPECTED,
        "discovery_row_hashes": WAVE8_SERTORIAN_DISCOVERY_ROW_HASHES,
        "entities": WAVE8_SERTORIAN_ENTITIES,
        "holds": WAVE8_SERTORIAN_HOLDS,
        "location_quarantine_reasons": (
            WAVE8_SERTORIAN_LOCATION_QUARANTINE_REASONS
        ),
        "point_quarantine_additions": sorted(
            WAVE8_SERTORIAN_POINT_QUARANTINE_ADDITIONS
        ),
        "row_hashes": WAVE8_SERTORIAN_ROW_HASHES,
        "sources": WAVE8_SERTORIAN_SOURCES,
        "terminal_exclusions": WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS,
    }


def wave8_sertorian_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_SERTORIAN_FINAL_AUDIT_SIGNATURE = (
    "b906e94211e76b4a8f6250a38de16f607b543c5066a87279d3342c0cdfe7ac70"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_SERTORIAN_CONTRACTS),
        len(WAVE8_SERTORIAN_HOLDS),
        len(WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS),
    ) != (4, 1, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_SERTORIAN_ENTITIES), len(WAVE8_SERTORIAN_SOURCES)) != (1, 10):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_SERTORIAN_RESERVED_IDS != WAVE8_SERTORIAN_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    dispositions = (
        WAVE8_SERTORIAN_CONTRACT_IDS,
        WAVE8_SERTORIAN_HOLD_IDS,
        WAVE8_SERTORIAN_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(3)
        for j in range(i + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if wave8_sertorian_audit_signature() != WAVE8_SERTORIAN_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_SERTORIAN_SOURCES
    }
    if len(source_by_id) != len(WAVE8_SERTORIAN_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_SERTORIAN_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity = WAVE8_SERTORIAN_ENTITIES[0]
    if entity["id"] != _SERTORIAN_FACTION:
        raise ValueError(f"{_LANE_NAME} bounded identity changed")
    if (entity["start_year"], entity["end_year"]) != (-80, -72):
        raise ValueError(f"{_LANE_NAME} identity window changed")
    if entity["aliases"] or entity["predecessors"]:
        raise ValueError(f"{_LANE_NAME} opened a generic identity fallback")
    if normalize_label(entity["name"]) in {
        "sertorius",
        "quintus sertorius",
        "populares",
        "lusitanians",
        "celtiberians",
    }:
        raise ValueError(f"{_LANE_NAME} installed a timeless identity")
    note = str(entity["continuity_note"]).casefold()
    if (
        "no rating is inherited" not in note
        or "candidate-keyed contracts" not in note
    ):
        raise ValueError(f"{_LANE_NAME} identity lacks continuity firewalls")
    if not _is_sorted_unique(entity["source_ids"]):
        raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
    if not set(map(str, entity["source_ids"])) <= set(source_by_id):
        raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    expected_contracts = {
        "hced-Baetis-80-1": {
            "years": (-80, -80),
            "sides": ([_SERTORIAN_FACTION], [_ROMAN_REPUBLIC]),
            "winner_side": 1,
            "confidence": 0.94,
            "date_override": False,
        },
        "hced-Lauron-76-1": {
            "years": (-77, -76),
            "sides": ([_SERTORIAN_FACTION], [_ROMAN_REPUBLIC]),
            "winner_side": 1,
            "confidence": 0.88,
            "date_override": True,
        },
        "hced-Turia-75-1": {
            "years": (-76, -75),
            "sides": ([_ROMAN_REPUBLIC], [_SERTORIAN_FACTION]),
            "winner_side": 1,
            "confidence": 0.72,
            "date_override": True,
        },
        "hced-Calahorra-74-1": {
            "years": (-75, -74),
            "sides": ([_SERTORIAN_FACTION], [_ROMAN_REPUBLIC]),
            "winner_side": 1,
            "confidence": 0.88,
            "date_override": True,
        },
    }
    used_sources = set(map(str, entity["source_ids"]))
    for candidate_id, expected in expected_contracts.items():
        contract = WAVE8_SERTORIAN_CONTRACTS[candidate_id]
        if contract["raw_row_sha256"] != WAVE8_SERTORIAN_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract hash changed: {candidate_id}")
        canonical = contract["canonical_event"]
        years = (int(canonical["year_low"]), int(canonical["year_high"]))
        expected_key = f"{_slug(str(canonical['name']))}:{years[0]}:{years[1]}"
        if years != expected["years"] or canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} canonical event changed: {candidate_id}")
        sides = (
            list(map(str, contract["side_1_entity_ids"])),
            list(map(str, contract["side_2_entity_ids"])),
        )
        if sides != expected["sides"]:
            raise ValueError(f"{_LANE_NAME} actor contract changed: {candidate_id}")
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != expected["winner_side"]
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} invented an outcome: {candidate_id}")
        if float(contract["confidence"]) != expected["confidence"]:
            raise ValueError(f"{_LANE_NAME} confidence changed: {candidate_id}")
        if contract["source_date_override"] is not expected["date_override"]:
            raise ValueError(f"{_LANE_NAME} date override changed: {candidate_id}")
        date_sources = list(map(str, contract["date_source_ids"]))
        if expected["date_override"] != bool(date_sources):
            raise ValueError(f"{_LANE_NAME} date evidence changed: {candidate_id}")
        if date_sources and not _is_sorted_unique(date_sources):
            raise ValueError(f"{_LANE_NAME} date sources are not canonical")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} ownership changed: {candidate_id}")

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence changed: {candidate_id}")
        if (
            not outcomes
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome evidence changed: {candidate_id}")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        expected_families = sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families changed")
        if not set(date_sources) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} date source is outside evidence")
        used_sources.update(evidence)

    if "whole-field result" not in WAVE8_SERTORIAN_CONTRACTS[
        "hced-Turia-75-1"
    ]["audit_note"]:
        raise ValueError(f"{_LANE_NAME} Turia boundary guard changed")
    if "rate_only_complete_field_battle" not in WAVE8_SERTORIAN_CONTRACTS[
        "hced-Turia-75-1"
    ]["boundary_guard"]:
        raise ValueError(f"{_LANE_NAME} Turia boundary contract changed")

    sucro = WAVE8_SERTORIAN_HOLDS["hced-Sucro-75-1"]
    if (
        sucro["raw_row_sha256"]
        != WAVE8_SERTORIAN_ROW_HASHES["hced-Sucro-75-1"]
        or sucro["disposition"] != "hold"
        or sucro["result_type"] != "unknown"
        or sucro["reviewed_outcome"] != "unknown"
        or sucro["unknown_is_never_draw"] is not True
        or "winner_side" in sucro
    ):
        raise ValueError(f"{_LANE_NAME} Sucro unknown became an outcome")
    used_sources.update(map(str, sucro["evidence_refs"]))

    murviedro = WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS[
        "hced-Murviedro-75-1"
    ]
    if (
        murviedro["raw_row_sha256"]
        != WAVE8_SERTORIAN_ROW_HASHES["hced-Murviedro-75-1"]
        or murviedro["disposition"]
        != "exclude_duplicate_of_reviewed_candidate"
        or murviedro["terminal_exclusion"] is not True
        or murviedro["duplicate_of_candidate_id"] != "hced-Turia-75-1"
        or murviedro["false_source_draw_rejected"] is not True
        or murviedro["raw_winner_raw"] != "Draw"
        or murviedro["raw_winner_loser_complete"] is not False
        or "winner_side" in murviedro
    ):
        raise ValueError(f"{_LANE_NAME} Murviedro duplicate contract changed")
    used_sources.update(map(str, murviedro["evidence_refs"]))
    for candidate_id, item in WAVE8_SERTORIAN_NONPROMOTIONS.items():
        refs = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} nonpromotion evidence changed")
        if item["duplicate_ownership"]["owner_module"] != _MODULE_OWNER:
            raise ValueError(f"{_LANE_NAME} nonpromotion ownership changed")
        if item["unknown_is_never_draw"] is not True:
            raise ValueError(f"{_LANE_NAME} unknown became a draw: {candidate_id}")
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_SERTORIAN_POINT_QUARANTINE_ADDITIONS != WAVE8_SERTORIAN_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_SERTORIAN_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if (
        set(WAVE8_SERTORIAN_LOCATION_QUARANTINE_REASONS)
        != WAVE8_SERTORIAN_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location reasons are incomplete")
    if (
        set(WAVE8_SERTORIAN_DISCOVERY_ROW_HASHES)
        != set(WAVE8_SERTORIAN_DISCOVERY_EXPECTED)
        or set(WAVE8_SERTORIAN_DISCOVERY_EXPECTED)
        != set(WAVE8_SERTORIAN_DISCOVERY_DISPOSITIONS)
    ):
        raise ValueError(f"{_LANE_NAME} discovery inventory changed")


def validate_wave8_sertorian_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SERTORIAN_CONTRACTS,
        WAVE8_SERTORIAN_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_SERTORIAN_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS),
    }


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def validate_wave8_sertorian_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin the three discovery-only twins and their absent outcomes."""

    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in WAVE8_SERTORIAN_DISCOVERY_ROW_HASHES.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} discovery row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(
                f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}"
            )
        expected = WAVE8_SERTORIAN_DISCOVERY_EXPECTED[candidate_id]
        participant_labels = sorted(
            str(item.get("label")) for item in row.get("participants", [])
        )
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("name") != expected["name"]
            or row.get("date") != expected["date"]
            or row.get("winners") != []
            or participant_labels != ["optimates", "populares"]
        ):
            raise ValueError(
                f"{_LANE_NAME} discovery non-rating guard changed: {candidate_id}"
            )
    return {
        "discovery_nonrating_twins": len(WAVE8_SERTORIAN_DISCOVERY_ROW_HASHES),
        "discovery_promotions": 0,
        "unknown_never_draw_rows": len(WAVE8_SERTORIAN_DISCOVERY_ROW_HASHES),
    }


def install_wave8_sertorian_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SERTORIAN_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_sertorian_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SERTORIAN_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SERTORIAN_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SERTORIAN_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_sertorian_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_sertorian_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SERTORIAN_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_sertorian_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_SERTORIAN_CONTRACTS.values(),
                    *WAVE8_SERTORIAN_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_sertorian_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_SERTORIAN_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_nonrating_twins": len(
            WAVE8_SERTORIAN_DISCOVERY_ROW_HASHES
        ),
        "holds": len(WAVE8_SERTORIAN_HOLDS),
        "new_entities": len(WAVE8_SERTORIAN_ENTITIES),
        "new_sources": len(WAVE8_SERTORIAN_SOURCES),
        "newly_rated_events": len(WAVE8_SERTORIAN_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_SERTORIAN_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_SERTORIAN_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_SERTORIAN_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS),
    }


def wave8_sertorian_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_SERTORIAN_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_SERTORIAN_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_sertorian_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_sertorian_counts(),
        "cohorts": wave8_sertorian_cohort_counts(),
        "discovery_dispositions": [
            {"candidate_id": candidate_id, **disposition}
            for candidate_id, disposition in sorted(
                WAVE8_SERTORIAN_DISCOVERY_DISPOSITIONS.items()
            )
        ],
        "final_audit_signature": WAVE8_SERTORIAN_FINAL_AUDIT_SIGNATURE,
        "holds": [
            {"candidate_id": candidate_id, **contract}
            for candidate_id, contract in sorted(WAVE8_SERTORIAN_HOLDS.items())
        ],
        "promoted_candidate_ids": sorted(WAVE8_SERTORIAN_CONTRACT_IDS),
        "terminal_exclusions": [
            {"candidate_id": candidate_id, **contract}
            for candidate_id, contract in sorted(
                WAVE8_SERTORIAN_TERMINAL_EXCLUSIONS.items()
            )
        ],
    }


_validate_static()
