"""Candidate-keyed Wave 8 audit for HCED's exact ``Madagascar`` label.

The locked cohort contains five nineteenth-century rows: the repulse of the
Anglo-French assault on Tamatave in 1845, the French bombardment and occupation
of Tamatave in 1883, and three distinct engagements in the French advance on
Tananarive in 1895.  ``Madagascar`` is resolved only for these exact rows to the
time-bounded Kingdom of Madagascar under the Merina monarchy.  No alias or
generic label policy is opened for the colonial or modern Malagasy states.

All five tactical outcomes are independently attested.  In particular, the
1845 row is not inferred from a later political result: contemporary official
and historical accounts describe the landing force's failed fort assault and
repulse.  The 1895 Tsarasoatra, Andriba, and Tananarive rows are separate in
date and operation and therefore are not double-rated.  No unknown result is
treated as a draw and no strategic outcome is substituted for a battle result.
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
    "WAVE8_MADAGASCAR_CONTRACT_IDS",
    "WAVE8_MADAGASCAR_CONTRACTS",
    "WAVE8_MADAGASCAR_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_MADAGASCAR_CROSS_LANE_DISPOSITIONS",
    "WAVE8_MADAGASCAR_ENTITIES",
    "WAVE8_MADAGASCAR_EXCLUSION_IDS",
    "WAVE8_MADAGASCAR_EXCLUSIONS",
    "WAVE8_MADAGASCAR_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS",
    "WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS",
    "WAVE8_MADAGASCAR_EXTERNAL_OWNER_IDS",
    "WAVE8_MADAGASCAR_FINAL_AUDIT_SIGNATURE",
    "WAVE8_MADAGASCAR_HCED_DUPLICATE_DISPOSITIONS",
    "WAVE8_MADAGASCAR_HOLD_IDS",
    "WAVE8_MADAGASCAR_HOLDS",
    "WAVE8_MADAGASCAR_INTEGRATION_DISPOSITIONS",
    "WAVE8_MADAGASCAR_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_MADAGASCAR_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_MADAGASCAR_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_MADAGASCAR_LOCATION_QUARANTINE_REASONS",
    "WAVE8_MADAGASCAR_NONPROMOTIONS",
    "WAVE8_MADAGASCAR_OUTCOME_OVERRIDES",
    "WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_MADAGASCAR_RESERVED_IDS",
    "WAVE8_MADAGASCAR_ROW_HASHES",
    "WAVE8_MADAGASCAR_SOURCES",
    "WAVE8_MADAGASCAR_TERMINAL_EXCLUSION_IDS",
    "WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS",
    "install_wave8_madagascar_entities",
    "install_wave8_madagascar_sources",
    "promote_wave8_madagascar_contracts",
    "validate_wave8_madagascar_integration_dispositions",
    "validate_wave8_madagascar_queue_contracts",
    "wave8_madagascar_audit_signature",
    "wave8_madagascar_cohort_counts",
    "wave8_madagascar_counts",
    "wave8_madagascar_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Madagascar polity audit"
_EVENT_ID_PREFIX = "hced_wave8_madagascar_"
_MODULE_OWNER = "military_elo.promotion.wave8_madagascar"

_MERINA_KINGDOM_ID = "kingdom_madagascar_merina_1817_1895"
_JULY_MONARCHY_ID = "french_july_monarchy"
_UNITED_KINGDOM_ID = "united_kingdom"
_FRENCH_THIRD_REPUBLIC_ID = "french_third_republic"
_EXISTING_ENTITY_IDS = frozenset(
    {_UNITED_KINGDOM_ID, _FRENCH_THIRD_REPUBLIC_ID}
)


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


WAVE8_MADAGASCAR_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_madagascar_met_merina",
        "Kingdoms of Madagascar: Maroserana and Merina",
        "https://www.metmuseum.org/essays/kingdoms-of-madagascar-maroserana-and-merina",
        "Metropolitan Museum of Art",
        "museum_scholarly_history",
        "met_heilbrunn_merina_bortolot_2003",
    ),
    _source(
        "wave8_madagascar_cambridge_imperial",
        "An Economic History of Imperial Madagascar, 1750-1895",
        "https://assets.cambridge.org/052183/9351/excerpt/0521839351_excerpt.htm",
        "Cambridge University Press",
        "scholarly_historical_monograph",
        "campbell_imperial_madagascar_2005",
    ),
    _source(
        "wave8_madagascar_france_july_monarchy",
        "La Restauration et la Monarchie de Juillet (1815-1848)",
        (
            "https://formation-civique.interieur.gouv.fr/fiches-par-thematiques/"
            "histoire-geographie-et-culture/les-regimes-politiques-depuis-1789/"
            "la-restauration-et-la-monarchie-de-juillet-1815-1848/"
        ),
        "French Ministry of the Interior",
        "official_regime_history",
        "french_interior_july_monarchy_history",
    ),
    _source(
        "wave8_madagascar_cnrs_july_monarchy",
        "La monarchie de Juillet",
        "https://www.cnrseditions.fr/catalogue/histoire/la-monarchie-de-juillet/",
        "CNRS Editions",
        "scholarly_historical_monograph",
        "robert_july_monarchy_2017",
    ),
    _source(
        "wave8_madagascar_annales_tamatave_1845",
        "Madagascar: Combat livre a Tamatave le 15 juin 1845",
        "https://books.google.com/books?id=mesZAAAAYAAJ",
        "Imprimerie royale; French Ministry of Marine and Colonies",
        "contemporary_official_naval_report",
        "annales_maritimes_tamatave_1845",
        outcome=True,
    ),
    _source(
        "wave8_madagascar_mcleod_tamatave_1845",
        "Madagascar and Its People",
        (
            "https://archive.org/details/"
            "madagascaritspeo00mclerich/page/104/mode/2up"
        ),
        "Longmans, Green, and Co.; Internet Archive scan",
        "historical_monograph",
        "mcleod_madagascar_people_1865",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_madagascar_imagesdefense_tamatave_1883",
        "Promotion de Madagascar 83-85",
        (
            "https://imagesdefense.gouv.fr/fr/"
            "promotion-de-madagascar-83-85-menu-30-mars-1892-legende-d-origine.html"
        ),
        "ECPAD, French Ministry of the Armed Forces",
        "official_defence_archive",
        "ecpad_madagascar_1883_1885",
        outcome=True,
    ),
    _source(
        "wave8_madagascar_britannica_tamatave_1883",
        "Madagascar",
        "https://britannica11.org/article/17-0285-s2/madagascar",
        "Encyclopaedia Britannica, 11th edition",
        "reference_history",
        "britannica_madagascar_1911",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_madagascar_duchesne_report_1895",
        "Rapport sur l'expedition de Madagascar",
        (
            "https://www.deutsche-digitale-bibliothek.de/item/"
            "KPQU7XND5LCZYOZHTUIDTRF3Y5GUU3SZ"
        ),
        "Berger-Levrault; Bayerische Staatsbibliothek digitization",
        "commanding_general_primary_report",
        "duchesne_madagascar_report_1897",
        outcome=True,
    ),
    _source(
        "wave8_madagascar_bulletin_tsarasoatra",
        "Bulletin du Comite de Madagascar: Les evenements de Madagascar",
        "https://www.bibliothequemalgache.com/pdf/BME10.pdf",
        "Comite de Madagascar; Bibliotheque malgache numerique",
        "contemporary_campaign_bulletin",
        "comite_madagascar_bulletin_1895",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_madagascar_bnf_andriba_map",
        "Prise d'Andriba, journees des 21 et 22 aout 1895",
        "https://catalogue.bnf.fr/ark:/12148/cb45231187j",
        "Service geographique de l'Armee; Bibliotheque nationale de France",
        "official_campaign_map_catalogue",
        "french_army_andriba_map_1897",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_madagascar_high_deeds_1895",
        "Les hauts faits de l'armee: Madagascar",
        "https://gallica.bnf.fr/ark:/12148/bpt6k6365829c.pdf",
        "Librairie Hachette; Bibliotheque nationale de France",
        "contemporary_military_history",
        "hauts_faits_armee_madagascar_1899",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_madagascar_army_tananarive",
        "L'histoire du 1er regiment de chasseurs d'Afrique",
        (
            "https://www.terre.defense.gouv.fr/1rca/traditions-du-1er-rca/"
            "lhistoire-du-1er-rca"
        ),
        "French Army, Ministry of the Armed Forces",
        "official_unit_history",
        "french_army_first_rca_history",
        outcome=True,
        crosscheck=True,
    ),
)


WAVE8_MADAGASCAR_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _MERINA_KINGDOM_ID,
        "name": "Kingdom of Madagascar under the Merina monarchy (1817-1895)",
        "kind": "kingdom",
        "start_year": 1817,
        "end_year": 1895,
        "region": "Madagascar",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The internationally styled Kingdom of Madagascar governed by the "
            "Merina monarchy from Radama I's 1817 British recognition through the "
            "capitulation at Tananarive in 1895. No rating is inherited by the "
            "French protectorate or colony, the post-1960 republic, a generic "
            "Malagasy people, or any modern state. The identity is installed only "
            "for candidate-keyed contracts and opens no Madagascar alias fallback."
        ),
        "source_ids": sorted(
            {
                "wave8_madagascar_cambridge_imperial",
                "wave8_madagascar_met_merina",
            }
        ),
    },
    {
        "id": _JULY_MONARCHY_ID,
        "name": "French July Monarchy",
        "kind": "constitutional_monarchy",
        "start_year": 1830,
        "end_year": 1848,
        "region": "France and overseas operations",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The constitutional regime of Louis-Philippe from August 1830 until "
            "the February 1848 revolution. No rating is inherited by Bourbon "
            "Restoration France, the Second Republic, any later French regime, or "
            "the modern state. No generic France alias is opened."
        ),
        "source_ids": sorted(
            {
                "wave8_madagascar_cnrs_july_monarchy",
                "wave8_madagascar_france_july_monarchy",
            }
        ),
    },
)


WAVE8_MADAGASCAR_ROW_HASHES: dict[str, str] = {
    "hced-Andriba1895-1": (
        "5e96c02bdcaf85d7f20ee1716263747f616d2388811bfe1af940f54db58751d7"
    ),
    "hced-Tamatave1845-1": (
        "9212d2428f3c7954fbccfb8cc495df6ec76211a9f21cad1f53920cff25a7ea4f"
    ),
    "hced-Tamatave1883-1": (
        "b2921bfce984bb4a0e722b9768bc8e8b840b13f7d78c5e11f64f049661fac7d5"
    ),
    "hced-Tananarive1895-1": (
        "ad4b7b3e5c72bc71cedc5091adc1dff57f619b97df895ee0ea7489ab48d5e33e"
    ),
    "hced-Tsarasoatra1895-1": (
        "d920aea959b005a408aa0dc2646c169a49c25f9e60bd05a1c6dcd114071da682"
    ),
}

_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_MADAGASCAR_SOURCES
}


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
    canonical_event: dict[str, Any],
    cohort: str,
    side_1: Iterable[str],
    side_2: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    reviewed_sides: Iterable[str],
    reviewed_outcome: str,
    event_boundary: str,
    war_type: str,
    confidence: float,
    winner_side: int = 1,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_MADAGASCAR_ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1))),
        "side_2_entity_ids": sorted(set(map(str, side_2))),
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "direct_provenance": {
            "reviewed_date": canonical_event["date_text"],
            "reviewed_sides": list(map(str, reviewed_sides)),
            "reviewed_outcome": reviewed_outcome,
            "event_boundary": event_boundary,
        },
        "audit_note": audit_note,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
    }


WAVE8_MADAGASCAR_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Tamatave1845-1": _contract(
        "hced-Tamatave1845-1",
        _canonical(
            "Anglo-French assault on Tamatave (1845)",
            1845,
            "15 June 1845",
            date_precision="day",
            granularity="naval_bombardment_and_fort_assault",
        ),
        "anglo_french_tamatave_expedition_1845",
        [_MERINA_KINGDOM_ID],
        [_JULY_MONARCHY_ID, _UNITED_KINGDOM_ID],
        [
            "wave8_madagascar_annales_tamatave_1845",
            "wave8_madagascar_cambridge_imperial",
            "wave8_madagascar_cnrs_july_monarchy",
            "wave8_madagascar_france_july_monarchy",
            "wave8_madagascar_mcleod_tamatave_1845",
            "wave8_madagascar_met_merina",
        ],
        [
            "wave8_madagascar_annales_tamatave_1845",
            "wave8_madagascar_mcleod_tamatave_1845",
        ],
        (
            "The combined British and French squadron bombarded Tamatave and "
            "landed a force against the Hova fortifications on 15 June. The "
            "assault was repulsed, so HCED's Malagasy victory is retained. The "
            "result is bounded to the competitive shore action, not later policy."
        ),
        reviewed_sides=[
            "Kingdom of Madagascar (Merina/Hova defenders)",
            "British and French July Monarchy naval and landing forces",
        ],
        reviewed_outcome="Malagasy defensive victory; allied fort assault repulsed",
        event_boundary="15 June bombardment, landing, fort assault, and withdrawal",
        war_type="interstate_limited",
        confidence=0.96,
    ),
    "hced-Tamatave1883-1": _contract(
        "hced-Tamatave1883-1",
        _canonical(
            "Bombardment and occupation of Tamatave (1883)",
            1883,
            "10-11 June 1883",
            date_precision="day_range",
            granularity="naval_bombardment_and_port_capture",
        ),
        "first_franco_hova_war_1883_1885",
        [_FRENCH_THIRD_REPUBLIC_ID],
        [_MERINA_KINGDOM_ID],
        [
            "wave8_madagascar_britannica_tamatave_1883",
            "wave8_madagascar_cambridge_imperial",
            "wave8_madagascar_imagesdefense_tamatave_1883",
            "wave8_madagascar_met_merina",
        ],
        [
            "wave8_madagascar_britannica_tamatave_1883",
            "wave8_madagascar_imagesdefense_tamatave_1883",
        ],
        (
            "After the Merina government rejected the ultimatum, Admiral Pierre's "
            "squadron bombarded Tamatave and French marines occupied the port. "
            "The immediate capture supports HCED's French victory without using "
            "the wider war's later treaty as a substitute result."
        ),
        reviewed_sides=[
            "French Third Republic naval and marine force",
            "Kingdom of Madagascar (Merina/Hova defenders)",
        ],
        reviewed_outcome="French tactical victory; port bombarded and occupied",
        event_boundary="bombardment and immediate marine occupation of Tamatave",
        war_type="colonial_anti_colonial",
        confidence=0.98,
    ),
    "hced-Tsarasoatra1895-1": _contract(
        "hced-Tsarasoatra1895-1",
        _canonical(
            "Battles of Tsarasoatra and Beritsoka",
            1895,
            "29-30 June 1895",
            date_precision="day_range",
            granularity="two_day_engagement",
        ),
        "second_franco_hova_war_1894_1895",
        [_FRENCH_THIRD_REPUBLIC_ID],
        [_MERINA_KINGDOM_ID],
        [
            "wave8_madagascar_bulletin_tsarasoatra",
            "wave8_madagascar_cambridge_imperial",
            "wave8_madagascar_duchesne_report_1895",
            "wave8_madagascar_met_merina",
        ],
        [
            "wave8_madagascar_bulletin_tsarasoatra",
            "wave8_madagascar_duchesne_report_1895",
        ],
        (
            "The Hova attack on the French advanced post was repelled on 29 June; "
            "the reinforced French counterattack captured the adjacent camp on "
            "30 June. The two-day operation is distinct from Andriba in August "
            "and from the final fighting before Tananarive in September."
        ),
        reviewed_sides=[
            "French Third Republic expeditionary force",
            "Kingdom of Madagascar Hova field force",
        ],
        reviewed_outcome="French victory after defense and counterattack",
        event_boundary="29-30 June fighting around Tsarasoatra and Beritsoka",
        war_type="colonial_anti_colonial",
        confidence=0.97,
    ),
    "hced-Andriba1895-1": _contract(
        "hced-Andriba1895-1",
        _canonical(
            "Combat and capture of Andriba",
            1895,
            "21-22 August 1895",
            date_precision="day_range",
            granularity="fortified_position_assault",
        ),
        "second_franco_hova_war_1894_1895",
        [_FRENCH_THIRD_REPUBLIC_ID],
        [_MERINA_KINGDOM_ID],
        [
            "wave8_madagascar_bnf_andriba_map",
            "wave8_madagascar_cambridge_imperial",
            "wave8_madagascar_duchesne_report_1895",
            "wave8_madagascar_high_deeds_1895",
            "wave8_madagascar_met_merina",
        ],
        [
            "wave8_madagascar_bnf_andriba_map",
            "wave8_madagascar_duchesne_report_1895",
            "wave8_madagascar_high_deeds_1895",
        ],
        (
            "French forces attacked the fortified Andriba position on 21 August; "
            "the Hova defenders abandoned the works under pressure and the position "
            "was secured on 22 August. The contract rates that bounded action, not "
            "the later unopposed road-column occupation or campaign attrition."
        ),
        reviewed_sides=[
            "French Third Republic expeditionary force",
            "Kingdom of Madagascar Hova defenders at Andriba",
        ],
        reviewed_outcome="French tactical victory; fortified position taken",
        event_boundary="21-22 August action against the Andriba defensive works",
        war_type="colonial_anti_colonial",
        confidence=0.94,
    ),
    "hced-Tananarive1895-1": _contract(
        "hced-Tananarive1895-1",
        _canonical(
            "Final action and capture of Tananarive",
            1895,
            "29-30 September 1895",
            date_precision="day_range",
            granularity="capital_approach_and_capture",
        ),
        "second_franco_hova_war_1894_1895",
        [_FRENCH_THIRD_REPUBLIC_ID],
        [_MERINA_KINGDOM_ID],
        [
            "wave8_madagascar_army_tananarive",
            "wave8_madagascar_cambridge_imperial",
            "wave8_madagascar_duchesne_report_1895",
            "wave8_madagascar_high_deeds_1895",
            "wave8_madagascar_met_merina",
        ],
        [
            "wave8_madagascar_army_tananarive",
            "wave8_madagascar_duchesne_report_1895",
            "wave8_madagascar_high_deeds_1895",
        ],
        (
            "The light column drove back the capital's defending forces on the "
            "approach and occupied Tananarive after a short bombardment on 30 "
            "September. The event ends at the capture; the 1 October protectorate "
            "agreement is not converted into a separate or inferred battle result."
        ),
        reviewed_sides=[
            "French Third Republic light expeditionary column",
            "Kingdom of Madagascar Hova capital defense",
        ],
        reviewed_outcome="French tactical victory and capture of Tananarive",
        event_boundary="29-30 September approach fighting, bombardment, and capture",
        war_type="colonial_anti_colonial",
        confidence=0.95,
    ),
}


WAVE8_MADAGASCAR_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_MADAGASCAR_CROSS_LANE_DISPOSITIONS = (
    WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS
)
WAVE8_MADAGASCAR_EXCLUSIONS = WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS
WAVE8_MADAGASCAR_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_MADAGASCAR_HOLDS,
    **WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS,
}

WAVE8_MADAGASCAR_CONTRACT_IDS = frozenset(WAVE8_MADAGASCAR_CONTRACTS)
WAVE8_MADAGASCAR_HOLD_IDS = frozenset(WAVE8_MADAGASCAR_HOLDS)
WAVE8_MADAGASCAR_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS
)
WAVE8_MADAGASCAR_EXCLUSION_IDS = WAVE8_MADAGASCAR_TERMINAL_EXCLUSION_IDS
WAVE8_MADAGASCAR_EXTERNAL_OWNER_IDS = frozenset(
    WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS
)
WAVE8_MADAGASCAR_RESERVED_IDS = (
    WAVE8_MADAGASCAR_CONTRACT_IDS
    | WAVE8_MADAGASCAR_HOLD_IDS
    | WAVE8_MADAGASCAR_TERMINAL_EXCLUSION_IDS
)
WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_MADAGASCAR_ROW_HASHES
)

WAVE8_MADAGASCAR_HCED_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_MADAGASCAR_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_MADAGASCAR_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_MADAGASCAR_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_MADAGASCAR_CROSS_LANE_DISPOSITIONS,
    **WAVE8_MADAGASCAR_HCED_DUPLICATE_DISPOSITIONS,
    **WAVE8_MADAGASCAR_IWBD_DUPLICATE_DISPOSITIONS,
    **WAVE8_MADAGASCAR_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
}
WAVE8_MADAGASCAR_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


# Every staged coordinate is either a city/locality centroid, a wrong homonym,
# or too precise for the reviewed multi-day/naval footprint. Country is correct.
WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_MADAGASCAR_CONTRACT_IDS
)
WAVE8_MADAGASCAR_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_MADAGASCAR_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_MADAGASCAR_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_MADAGASCAR_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Andriba1895-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The staged longitude 41.185 is far west of the reviewed Andriba "
            "defensive position and cannot represent the 21-22 August battlefield."
        ),
    },
    "hced-Tamatave1845-1": {
        "actions": ["withhold_point"],
        "reason": (
            "A modern Toamasina city lookup cannot represent the roadstead, ships, "
            "landing route, fortifications, and withdrawal of the 1845 action."
        ),
    },
    "hced-Tamatave1883-1": {
        "actions": ["withhold_point"],
        "reason": (
            "A city centroid is too precise for the squadron bombardment, shore "
            "defenses, burned settlement, and marine occupation footprint."
        ),
    },
    "hced-Tananarive1895-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The capital centroid does not identify the approach positions, Hova "
            "defenses, artillery footprint, or occupation route reviewed here."
        ),
    },
    "hced-Tsarasoatra1895-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The staged point resolves to a capital-area namesake rather than the "
            "June 1895 Tsarasoatra/Beritsoka battlefield north-west of Tananarive."
        ),
    },
}


WAVE8_MADAGASCAR_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Andriba1895-1": {
        "aliases": sorted(
            {
                "andriba",
                "battle of andriba",
                "capture of andriba",
                "combat and capture of andriba",
                "combat of andriba",
            }
        ),
        "years": [1895, 1895],
    },
    "hced-Tamatave1845-1": {
        "aliases": sorted(
            {
                "anglo french assault on tamatave 1845",
                "assault on tamatave",
                "battle of tamatave",
                "tamatave",
                "toamasina",
            }
        ),
        "years": [1845, 1845],
    },
    "hced-Tamatave1883-1": {
        "aliases": sorted(
            {
                "bombardment and occupation of tamatave 1883",
                "bombardment of tamatave",
                "capture of tamatave",
                "tamatave",
                "toamasina",
            }
        ),
        "years": [1883, 1883],
    },
    "hced-Tananarive1895-1": {
        "aliases": sorted(
            {
                "antananarivo",
                "capture of antananarivo",
                "capture of tananarive",
                "final action and capture of tananarive",
                "tananarive",
            }
        ),
        "years": [1895, 1895],
    },
    "hced-Tsarasoatra1895-1": {
        "aliases": sorted(
            {
                "battle of tsarasoatra",
                "battles of tsarasoatra and beritsoka",
                "combat of tsarasoatra",
                "tsarasoatra",
                "tsarasotra",
            }
        ),
        "years": [1895, 1895],
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_MADAGASCAR_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_MADAGASCAR_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_MADAGASCAR_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_MADAGASCAR_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_MADAGASCAR_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(
            WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS
        ),
        "external_owner_dispositions": (
            WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS
        ),
        "hced_duplicate_dispositions": (
            WAVE8_MADAGASCAR_HCED_DUPLICATE_DISPOSITIONS
        ),
        "holds": WAVE8_MADAGASCAR_HOLDS,
        "integration_dispositions": WAVE8_MADAGASCAR_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_MADAGASCAR_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": WAVE8_MADAGASCAR_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": (
            WAVE8_MADAGASCAR_LOCATION_QUARANTINE_REASONS
        ),
        "outcome_overrides": WAVE8_MADAGASCAR_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS
        ),
        "row_hashes": WAVE8_MADAGASCAR_ROW_HASHES,
        "sources": WAVE8_MADAGASCAR_SOURCES,
        "terminal_exclusions": WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS,
    }


def wave8_madagascar_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label adjudication."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_MADAGASCAR_FINAL_AUDIT_SIGNATURE = (
    "cd30bd8b563e0bc002deab128dc6dd5b82b8364c8e42702bf359b3d3e395a001"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_MADAGASCAR_CONTRACTS),
        len(WAVE8_MADAGASCAR_HOLDS),
        len(WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS),
        len(WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS),
    ) != (5, 0, 0, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_MADAGASCAR_ENTITIES), len(WAVE8_MADAGASCAR_SOURCES)) != (
        2,
        13,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if (
        WAVE8_MADAGASCAR_RESERVED_IDS | WAVE8_MADAGASCAR_EXTERNAL_OWNER_IDS
        != WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    dispositions = (
        WAVE8_MADAGASCAR_CONTRACT_IDS,
        WAVE8_MADAGASCAR_HOLD_IDS,
        WAVE8_MADAGASCAR_TERMINAL_EXCLUSION_IDS,
        WAVE8_MADAGASCAR_EXTERNAL_OWNER_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(len(dispositions))
        for j in range(i + 1, len(dispositions))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if wave8_madagascar_audit_signature() != WAVE8_MADAGASCAR_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_MADAGASCAR_SOURCES}
    if len(source_by_id) != len(WAVE8_MADAGASCAR_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(
        {str(source["source_family_id"]) for source in WAVE8_MADAGASCAR_SOURCES}
    ) != len(WAVE8_MADAGASCAR_SOURCES):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_MADAGASCAR_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_MADAGASCAR_ENTITIES}
    if len(entity_by_id) != len(WAVE8_MADAGASCAR_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    if set(entity_by_id) & _EXISTING_ENTITY_IDS:
        raise ValueError(f"{_LANE_NAME} new and existing entity inventories overlap")
    expected_windows = {
        _MERINA_KINGDOM_ID: (1817, 1895),
        _JULY_MONARCHY_ID: (1830, 1848),
    }
    for entity_id, entity in entity_by_id.items():
        if (entity["start_year"], entity["end_year"]) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} entity window drifted")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern state" not in note:
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_new_entities: set[str] = set()
    used_sources: set[str] = set()
    allowed_granularities = {
        "capital_approach_and_capture",
        "fortified_position_assault",
        "naval_bombardment_and_fort_assault",
        "naval_bombardment_and_port_capture",
        "two_day_engagement",
    }
    for candidate_id, contract in WAVE8_MADAGASCAR_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_MADAGASCAR_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["year_low"] != canonical["year_high"]:
            raise ValueError(f"{_LANE_NAME} promoted an unbounded year window")
        if canonical["granularity"] not in allowed_granularities:
            raise ValueError(f"{_LANE_NAME} promoted unsupported granularity")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        participants = set(side_1) | set(side_2)
        allowed_participants = set(entity_by_id) | set(_EXISTING_ENTITY_IDS)
        if not participants <= allowed_participants:
            raise ValueError(f"{_LANE_NAME} uses an unreviewed identity")
        used_new_entities.update(participants & set(entity_by_id))
        year = int(canonical["year_low"])
        for entity_id in participants & set(entity_by_id):
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
            len(outcomes) < 2
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
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")
    used_sources.update(
        source_id
        for entity in WAVE8_MADAGASCAR_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if (
        WAVE8_MADAGASCAR_HOLDS
        or WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS
        or WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} acquired an unaudited nonpromotion")
    if WAVE8_MADAGASCAR_CROSS_LANE_DISPOSITIONS is not (
        WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} external ownership alias drifted")
    if WAVE8_MADAGASCAR_EXCLUSIONS is not WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion alias drifted")
    if (
        WAVE8_MADAGASCAR_OUTCOME_OVERRIDES
        or WAVE8_MADAGASCAR_HCED_DUPLICATE_DISPOSITIONS
        or WAVE8_MADAGASCAR_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_MADAGASCAR_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_MADAGASCAR_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")

    if WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS != WAVE8_MADAGASCAR_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_MADAGASCAR_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unsupported country quarantine")
    if set(WAVE8_MADAGASCAR_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location-review inventory changed")
    for review in WAVE8_MADAGASCAR_LOCATION_QUARANTINE_REASONS.values():
        if (
            not review["reason"]
            or not _is_sorted_unique(review["actions"])
            or review["actions"] != ["withhold_point"]
        ):
            raise ValueError(f"{_LANE_NAME} location review is not canonical")

    if set(WAVE8_MADAGASCAR_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for candidate_id, audit in WAVE8_MADAGASCAR_IWBD_ZERO_OVERLAP_AUDIT.items():
        aliases = list(map(str, audit["aliases"]))
        years = list(map(int, audit["years"]))
        if not aliases or not _is_sorted_unique(aliases):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if any(alias != normalize_label(alias) for alias in aliases):
            raise ValueError(f"{_LANE_NAME} duplicate alias is not normalized")
        if years != [years[0], years[0]]:
            raise ValueError(f"{_LANE_NAME} duplicate year window drifted")
        canonical = WAVE8_MADAGASCAR_CONTRACTS[candidate_id]["canonical_event"]
        canonical_key = (int(canonical["year_low"]), normalize_label(canonical["name"]))
        item_keys = {(years[0], alias) for alias in aliases}
        if canonical_key not in item_keys:
            raise ValueError(f"{_LANE_NAME} canonical duplicate audit is incomplete")


def _is_exact_madagascar_label(value: Any) -> bool:
    return normalize_label(value) == "madagascar"


def validate_wave8_madagascar_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate the complete exact-label cohort and immutable row fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_MADAGASCAR_CONTRACTS,
        WAVE8_MADAGASCAR_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_madagascar_label(row.get("side_1_raw"))
        or _is_exact_madagascar_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Madagascar inventory changed: "
            f"{sorted(exact_label_ids)}"
        )
    return {
        "external_owner_contracts": len(WAVE8_MADAGASCAR_EXTERNAL_OWNER_IDS),
        "holds": len(WAVE8_MADAGASCAR_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": (
            result["reviewed_hced_rows"]
            + len(WAVE8_MADAGASCAR_EXTERNAL_OWNER_IDS)
        ),
        "terminal_exclusions": len(WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS),
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
        if isinstance(value, str):
            text = value.lstrip("-")
            if len(text) >= 4 and text[:4].isdigit():
                year = int(text[:4])
                return -year if value.startswith("-") else year
    return None


_DUPLICATE_MATCH_KEYS = {
    (year, alias)
    for audit in WAVE8_MADAGASCAR_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
}


def validate_wave8_madagascar_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed if another queue or release lane adds an unreviewed twin."""

    validate_wave8_madagascar_queue_contracts(hced_rows)
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_MADAGASCAR_CONTRACT_IDS
        and (_row_year(event), normalize_label(event.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_matches}"
        )
    return {
        "cross_lane_hced_dispositions": len(WAVE8_MADAGASCAR_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_MADAGASCAR_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(
            WAVE8_MADAGASCAR_EXTERNAL_OWNER_IDS
        ),
        "hced_duplicate_dispositions": len(
            WAVE8_MADAGASCAR_HCED_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(WAVE8_MADAGASCAR_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_MADAGASCAR_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_MADAGASCAR_IWBD_ZERO_OVERLAP_AUDIT
        ),
    }


def install_wave8_madagascar_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_MADAGASCAR_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_madagascar_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_MADAGASCAR_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_MADAGASCAR_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_madagascar_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_madagascar_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_MADAGASCAR_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_madagascar_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_MADAGASCAR_CONTRACTS.values()
            ).items()
        )
    )


def wave8_madagascar_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_MADAGASCAR_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_MADAGASCAR_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_MADAGASCAR_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(
            WAVE8_MADAGASCAR_EXTERNAL_OWNER_IDS
        ),
        "hced_duplicate_dispositions": len(
            WAVE8_MADAGASCAR_HCED_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_MADAGASCAR_HOLDS),
        "integration_dispositions": len(
            WAVE8_MADAGASCAR_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_MADAGASCAR_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_MADAGASCAR_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_MADAGASCAR_ENTITIES),
        "new_sources": len(WAVE8_MADAGASCAR_SOURCES),
        "newly_rated_events": len(WAVE8_MADAGASCAR_CONTRACTS),
        "outcome_overrides": len(WAVE8_MADAGASCAR_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_MADAGASCAR_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS),
        "terminal_exclusions": len(WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS),
    }


def wave8_madagascar_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_MADAGASCAR_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS,
    }
