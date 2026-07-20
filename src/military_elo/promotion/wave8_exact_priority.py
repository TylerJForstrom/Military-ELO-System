"""Fail-closed candidate-keyed contracts for seven audited HCED priority rows.

This lane deliberately has no label policy.  Six independently corroborated
engagements are promoted through their exact HCED candidate IDs; the 1856
Granada row is reserved and held because the reviewed siege, relief, retreat,
and occupation sequence does not reduce to HCED's asserted allied tactical
win.  Every newly introduced military identity is event-bounded and alias-free.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    expected_exact_hced_win_participants,
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_EXACT_PRIORITY_AUDITED_IDS",
    "WAVE8_EXACT_PRIORITY_CONTRACT_IDS",
    "WAVE8_EXACT_PRIORITY_CONTRACTS",
    "WAVE8_EXACT_PRIORITY_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_EXACT_PRIORITY_ENTITIES",
    "WAVE8_EXACT_PRIORITY_FINAL_AUDIT_SIGNATURE",
    "WAVE8_EXACT_PRIORITY_HOLD_IDS",
    "WAVE8_EXACT_PRIORITY_HOLDS",
    "WAVE8_EXACT_PRIORITY_LOCATION_QUARANTINE_REASONS",
    "WAVE8_EXACT_PRIORITY_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_EXACT_PRIORITY_RESERVED_IDS",
    "WAVE8_EXACT_PRIORITY_ROW_DISPOSITIONS",
    "WAVE8_EXACT_PRIORITY_ROW_HASHES",
    "WAVE8_EXACT_PRIORITY_SOURCES",
    "WAVE8_EXACT_PRIORITY_TARGET_IDS",
    "install_wave8_exact_priority_entities",
    "install_wave8_exact_priority_sources",
    "promote_wave8_exact_priority_contracts",
    "validate_wave8_exact_priority_final_audit",
    "validate_wave8_exact_priority_integration_dispositions",
    "validate_wave8_exact_priority_queue_contracts",
    "validate_wave8_exact_priority_release_inventory",
    "wave8_exact_priority_audit_signature",
    "wave8_exact_priority_cohort_counts",
    "wave8_exact_priority_counts",
    "wave8_exact_priority_metadata",
)


_LANE_NAME = "Wave 8 exact priority candidate audit"
_MODULE_OWNER = "military_elo.promotion.wave8_exact_priority"
_EVENT_ID_PREFIX = "hced_wave8_exact_priority_"

_MEXICAN_LIBERALS = "mexican_liberal_forces"
_MEXICAN_CONSERVATIVES = "mexican_conservative_forces"
_UNITED_STATES = "united_states"
_TRIPOLI = "yusuf_karamanli_regency_of_tripoli_1795_1832"
_ROMAN_PRINCIPATE = "roman_empire"

_HAMET_DERNA = "hamet_karamanli_claimant_contingent_derna_1805"
_EATON_AUXILIARIES = "eaton_hamet_arab_greek_auxiliaries_derna_1805"
_WALKER_LA_VIRGEN = "walker_expeditionary_force_la_virgen_1855"
_NICARAGUAN_DEMOCRATS = "nicaraguan_democratic_force_la_virgen_1855"
_NICARAGUAN_LEGITIMISTS = "nicaraguan_legitimist_force_la_virgen_1855"
_COSTA_RICAN_ARMY = "costa_rican_national_army_santa_rosa_1856"
_SCHLESSINGER_DETACHMENT = (
    "schlessinger_walker_filibuster_detachment_santa_rosa_1856"
)
_ARMINIUS_COALITION = "arminius_led_germanic_coalition_teutoburg_9"
_TWIN_VILLAGES_COALITION = (
    "taovaya_fort_defending_coalition_twin_villages_1759"
)
_ORTIZ_PARRILLA_EXPEDITION = "ortiz_parrilla_spanish_led_expedition_1759"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-19",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_EXACT_PRIORITY_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_exact_priority_mexico_defensa_calpulalpan",
        "22 de diciembre de 1860, batalla de Calpulalpan",
        (
            "https://www.gob.mx/defensa/documentos/"
            "22-de-diciembre-de-1860-batalla-de-calpulalpan"
        ),
        "Secretaría de la Defensa Nacional, Gobierno de México",
        "official_military_history",
        "mexico_secretariat_defense_calpulalpan",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_inehrm_calpulalpan",
        "La vuelta del liberalismo a la Ciudad de México",
        (
            "https://www.inehrm.gob.mx/es/inehrm/"
            "La_vuelta_del_liberalismo_a_la_Ciudad_de_Mexico"
        ),
        "Instituto Nacional de Estudios Históricos de las Revoluciones de México",
        "official_scholarly_history",
        "inehrm_gonzalez_lezama_calpulalpan",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_nhhc_derna",
        "Barbary Wars, 1801-1805 and 1815-1816",
        (
            "https://www.history.navy.mil/content/history/nhhc/"
            "browse-by-topic/wars-conflicts-and-operations/barbary-wars.html"
        ),
        "Naval History and Heritage Command",
        "official_military_history",
        "naval_history_and_heritage_command_derna",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_usmcu_obannon_derna",
        "First Lieutenant Presley Neville O'Bannon",
        (
            "https://www.usmcu.edu/Research/Marine-Corps-History-Division/"
            "People/Whos-Who-in-Marine-Corps-History/Mackie-Ozbourn/"
            "First-Lieutenant-Presley-Neville-OBannon/"
        ),
        "Marine Corps History Division, Marine Corps University",
        "official_military_biography",
        "marine_corps_history_division_obannon",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_founders_eaton_hamet",
        "William Eaton to James Madison, 4 March 1805",
        "https://founders.archives.gov/documents/Madison/02-09-02-0103",
        "Founders Online, National Archives",
        "edited_primary_document",
        "papers_of_james_madison",
        outcome=False,
    ),
    _source(
        "wave8_exact_priority_usni_eaton_derne",
        "William Eaton—The Hero of Derne",
        (
            "https://www.usni.org/magazines/proceedings/1941/april/"
            "william-eaton-hero-derne"
        ),
        "U.S. Naval Institute Proceedings",
        "professional_history_article",
        "us_naval_institute_proceedings_derne",
        outcome=False,
    ),
    _source(
        "wave8_exact_priority_walker_war_nicaragua",
        "William Walker, The War in Nicaragua",
        "https://gutenberg.org/files/76898/76898-h/76898-h.htm",
        "Project Gutenberg",
        "participant_primary_memoir",
        "william_walker_war_in_nicaragua",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_bolanos_geyer_nicaragua",
        "William Walker: El predestinado de los ojos grises, tomo III",
        (
            "https://guerranacional.enriquebolanos.org/bibliografia_pdf/"
            "ABG-T3-NICARAGUA.pdf"
        ),
        "Fundación Enrique Bolaños",
        "scholarly_historical_monograph",
        "bolanos_geyer_gray_eyed_man_volume_3",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_scroggs_granada",
        "Filibusters and Financiers: The Story of William Walker and His Associates",
        (
            "https://books.google.com/books/about/"
            "Filibusters_and_Financiers.html?id=XbUWAAAAYAAJ"
        ),
        "Macmillan; digitized by Google Books",
        "scholarly_historical_monograph",
        "scroggs_filibusters_and_financiers",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_mep_santa_rosa",
        "Unidad didáctica: mes de la Gesta 1856-1857",
        (
            "https://mep.go.cr/sites/default/files/media/"
            "unidad-didactica-mes-de-la-gesta-1856-1857.pdf"
        ),
        "Ministerio de Educación Pública, Gobierno de Costa Rica",
        "official_educational_history",
        "costa_rica_mep_santa_rosa",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_museo_costa_rica_forces",
        "Las Fuerzas Armadas en Costa Rica: Campaña Nacional, 1856-1857",
        (
            "https://www.museocostarica.go.cr/museo/historia-cuartel/"
            "fuerzas-armadas-en-costa-rica/"
        ),
        "Museo Nacional de Costa Rica",
        "official_museum_history",
        "museo_nacional_costa_rica_campaign",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_kalkriese_varus",
        "The Varus Battle",
        "https://www.kalkriese-varusschlacht.de/en/the-varus-battle.html",
        "Museum and Park Kalkriese",
        "official_museum_history",
        "museum_park_kalkriese_varus_battle",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_oxford_arminius",
        "Resisting Roman Imperialism in Germania",
        "https://academic.oup.com/book/58059/chapter-abstract/477515317",
        "Oxford University Press",
        "scholarly_book_chapter",
        "oxford_cartography_resistance_arminius",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_tsha_ortiz_parrilla",
        "Ortiz Parrilla Red River Campaign",
        "https://www.tshaonline.org/handbook/entries/ortiz-parrilla-red-river-campaign",
        "Texas State Historical Association",
        "scholarly_state_handbook",
        "handbook_texas_ortiz_parrilla",
        outcome=True,
    ),
    _source(
        "wave8_exact_priority_ohs_twin_villages",
        "Twin Villages, Battle of the",
        "https://www.okhistory.org/publications/enc/entry?entry=TW005",
        "Oklahoma Historical Society",
        "scholarly_state_encyclopedia",
        "oklahoma_history_twin_villages",
        outcome=True,
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_EXACT_PRIORITY_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    source_ids: Iterable[str],
    boundary: str,
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
            f"{boundary} This identity exists only for the named engagement and "
            f"year {year}. No rating is inherited by a constituent people, party, "
            "state, claimant, noncombatant population, predecessor, successor, or "
            "other formation."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_EXACT_PRIORITY_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _HAMET_DERNA,
        "Hamet Karamanli's claimant contingent at Derna (1805)",
        "event_bounded_claimant_contingent",
        1805,
        "North Africa",
        [
            "wave8_exact_priority_founders_eaton_hamet",
            "wave8_exact_priority_nhhc_derna",
            "wave8_exact_priority_usni_eaton_derne",
        ],
        (
            "Event-bounded followers and personal escort attached to Hamet "
            "Karamanli's restoration attempt, excluding U.S. personnel and the "
            "separately represented Arab and Greek expeditionary auxiliaries."
        ),
    ),
    _entity(
        _EATON_AUXILIARIES,
        "Eaton-Hamet Arab and Greek expeditionary auxiliaries at Derna (1805)",
        "event_bounded_expeditionary_auxiliaries",
        1805,
        "North Africa",
        [
            "wave8_exact_priority_nhhc_derna",
            "wave8_exact_priority_usmcu_obannon_derna",
            "wave8_exact_priority_usni_eaton_derne",
        ],
        (
            "Event-bounded Arab and Greek expeditionary auxiliaries assembled "
            "around William Eaton and Hamet Karamanli, excluding U.S. personnel "
            "and Hamet's separately represented claimant contingent. The record "
            "does not imply one uniform contract or permanent organization."
        ),
    ),
    _entity(
        _WALKER_LA_VIRGEN,
        "Walker's expeditionary force at La Virgen (1855)",
        "event_bounded_filibuster_expeditionary_force",
        1855,
        "Central America",
        [
            "wave8_exact_priority_bolanos_geyer_nicaragua",
            "wave8_exact_priority_walker_war_nicaragua",
        ],
        (
            "Event-bounded foreign expeditionaries under William Walker in the "
            "3 September action, excluding the allied Nicaraguan Democratic force."
        ),
    ),
    _entity(
        _NICARAGUAN_DEMOCRATS,
        "Nicaraguan Democratic force at La Virgen (1855)",
        "event_bounded_civil_war_faction_force",
        1855,
        "Central America",
        [
            "wave8_exact_priority_bolanos_geyer_nicaragua",
            "wave8_exact_priority_walker_war_nicaragua",
        ],
        (
            "Event-bounded Nicaraguan Democratic troops fighting alongside Walker "
            "at La Virgen, kept distinct from the foreign expeditionaries."
        ),
    ),
    _entity(
        _NICARAGUAN_LEGITIMISTS,
        "Nicaraguan Legitimist force at La Virgen (1855)",
        "event_bounded_civil_war_faction_force",
        1855,
        "Central America",
        [
            "wave8_exact_priority_bolanos_geyer_nicaragua",
            "wave8_exact_priority_walker_war_nicaragua",
        ],
        (
            "Event-bounded Legitimist field force under José Santos Guardiola in "
            "the La Virgen action; it is not a timeless Nicaraguan identity."
        ),
    ),
    _entity(
        _COSTA_RICAN_ARMY,
        "Costa Rican national army at Santa Rosa (1856)",
        "event_bounded_national_army",
        1856,
        "Central America",
        [
            "wave8_exact_priority_mep_santa_rosa",
            "wave8_exact_priority_museo_costa_rica_forces",
        ],
        (
            "Event-bounded Costa Rican force that attacked Hacienda Santa Rosa on "
            "20 March, without creating a broad Costa Rica polity identity."
        ),
    ),
    _entity(
        _SCHLESSINGER_DETACHMENT,
        "Schlessinger's Walker filibuster detachment at Santa Rosa (1856)",
        "event_bounded_filibuster_detachment",
        1856,
        "Central America",
        [
            "wave8_exact_priority_mep_santa_rosa",
            "wave8_exact_priority_museo_costa_rica_forces",
        ],
        (
            "Event-bounded Walker-aligned detachment opposed at Hacienda Santa "
            "Rosa, distinct from Walker's 1855 La Virgen expeditionary force."
        ),
    ),
    _entity(
        _ARMINIUS_COALITION,
        "Arminius-led Germanic coalition in the Varus Battle (9 CE)",
        "event_bounded_germanic_coalition",
        9,
        "Germania",
        [
            "wave8_exact_priority_kalkriese_varus",
            "wave8_exact_priority_oxford_arminius",
        ],
        (
            "Event-bounded Germanic tribal warriors united under the Cheruscan "
            "leader Arminius for the Varus Battle; no unlisted tribal composition "
            "or later German identity is inferred."
        ),
    ),
    _entity(
        _TWIN_VILLAGES_COALITION,
        "Taovaya-fort defending coalition at Twin Villages (1759)",
        "event_bounded_indigenous_defense_coalition",
        1759,
        "Red River borderlands, North America",
        [
            "wave8_exact_priority_ohs_twin_villages",
            "wave8_exact_priority_tsha_ortiz_parrilla",
        ],
        (
            "Event-bounded defenders of the Taovaya fort, including source-named "
            "Taovaya/Wichita, Comanche, Yaceales, and Tawakoni elements. No formal "
            "multi-nation command hierarchy is inferred, and the contract does "
            "not merge their peoples or modern descendants."
        ),
    ),
    _entity(
        _ORTIZ_PARRILLA_EXPEDITION,
        "Ortiz Parrilla's Spanish-led expedition at Twin Villages (1759)",
        "event_bounded_colonial_expedition",
        1759,
        "Red River borderlands, North America",
        [
            "wave8_exact_priority_ohs_twin_villages",
            "wave8_exact_priority_tsha_ortiz_parrilla",
        ],
        (
            "Event-bounded Spanish-led expedition under Diego Ortiz Parrilla, "
            "including source-described Spanish troops, militia, Apache, "
            "Tlaxcaltecan, and mission allies. The loss is not assigned to the "
            "undifferentiated Spanish Empire or inherited by any constituent."
        ),
    ),
)

_ENTITY_BY_ID = {
    str(entity["id"]): entity for entity in WAVE8_EXACT_PRIORITY_ENTITIES
}


# These seven IDs are reserved as a unit before any generic HCED promotion.  A
# reserved row is either promoted by its exact contract or retained as an exact
# hold; no later label resolver may consume it.
WAVE8_EXACT_PRIORITY_TARGET_IDS = frozenset(
    {
        "hced-Calpulalpam1860-1",
        "hced-Derna1805-1",
        "hced-Granada, Nicaragua1856-1",
        "hced-La Virgen1855-1",
        "hced-Red River1759-1",
        "hced-Santa Rosa de Copan1856-1",
        "hced-Teutoburgwald9-1",
    }
)

WAVE8_EXACT_PRIORITY_ROW_HASHES: dict[str, str] = {
    "hced-Calpulalpam1860-1": (
        "f7e420f15234141959bd92b6cd103a4b82d15b0b4b33a4394fa01002c583a32d"
    ),
    "hced-Derna1805-1": (
        "821591e6a4733f91c25f30a2aba17cb199537c3941cf2b55840125a1ff716f87"
    ),
    "hced-Granada, Nicaragua1856-1": (
        "e00e51d575246bdd94bf6c25cb010d389c5fb90536c73168313973f2f49f7d74"
    ),
    "hced-La Virgen1855-1": (
        "22a82e98c7f20f21e1135ba5801acdc65c66765477614a18b800c27682367314"
    ),
    "hced-Red River1759-1": (
        "80dd300e8e760766faed4944f672fb597944822d850551f00506f0979876a083"
    ),
    "hced-Santa Rosa de Copan1856-1": (
        "0ca5fb235b393560bd5fef08cc2c13f4b39c3659c88209fc6f74a1b38f1fbc49"
    ),
    "hced-Teutoburgwald9-1": (
        "5eb0ca0863620e7f8cf42e3f64f2cd98744313e61d2d3bd18933096521389330"
    ),
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
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
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    cohort: str,
    war_type: str,
    actor_override: str,
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_EXACT_PRIORITY_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_date_override": False,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": actor_override,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_EXACT_PRIORITY_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Calpulalpam1860-1": _contract(
        "hced-Calpulalpam1860-1",
        _canonical(
            "Battle of Calpulalpan",
            1860,
            "22 December 1860",
            "day",
            "single_battle_in_the_war_of_reform",
        ),
        [_MEXICAN_LIBERALS],
        [_MEXICAN_CONSERVATIVES],
        [
            "wave8_exact_priority_inehrm_calpulalpan",
            "wave8_exact_priority_mexico_defensa_calpulalpan",
        ],
        [
            "wave8_exact_priority_inehrm_calpulalpan",
            "wave8_exact_priority_mexico_defensa_calpulalpan",
        ],
        "mexican_war_of_reform",
        "civil_war",
        "candidate_keyed_mexican_government_to_conservative_faction",
        (
            "The exact HCED 'Mexican Government' side is resolved only here to "
            "Miramón's Conservative army. Both official histories identify the "
            "Liberal victory; no global government or Mexico alias is introduced."
        ),
        confidence=0.96,
    ),
    "hced-Derna1805-1": _contract(
        "hced-Derna1805-1",
        _canonical(
            "Battle of Derna",
            1805,
            "27 April 1805",
            "day",
            "combined_land_sea_capture_engagement",
        ),
        [_UNITED_STATES, _HAMET_DERNA, _EATON_AUXILIARIES],
        [_TRIPOLI],
        [
            "wave8_exact_priority_founders_eaton_hamet",
            "wave8_exact_priority_nhhc_derna",
            "wave8_exact_priority_usmcu_obannon_derna",
            "wave8_exact_priority_usni_eaton_derne",
        ],
        [
            "wave8_exact_priority_nhhc_derna",
            "wave8_exact_priority_usmcu_obannon_derna",
        ],
        "first_barbary_war",
        "interstate_claimant_intervention",
        "candidate_keyed_us_hamet_and_expeditionary_auxiliaries",
        (
            "The U.S. participant is supplemented, not replaced, by separate "
            "event-bounded Hamet and Arab/Greek auxiliary identities. No uniform "
            "mercenary contract is inferred. Official naval and Marine histories "
            "corroborate the 27 April capture and victory."
        ),
        confidence=0.93,
    ),
    "hced-La Virgen1855-1": _contract(
        "hced-La Virgen1855-1",
        _canonical(
            "Battle of La Virgen",
            1855,
            "3 September 1855",
            "day",
            "single_battle_in_the_nicaraguan_civil_war",
        ),
        [_WALKER_LA_VIRGEN, _NICARAGUAN_DEMOCRATS],
        [_NICARAGUAN_LEGITIMISTS],
        [
            "wave8_exact_priority_bolanos_geyer_nicaragua",
            "wave8_exact_priority_walker_war_nicaragua",
        ],
        [
            "wave8_exact_priority_bolanos_geyer_nicaragua",
            "wave8_exact_priority_walker_war_nicaragua",
        ],
        "nicaragua_filibuster_conflict",
        "civil_war_foreign_intervention",
        "candidate_keyed_walker_and_nicaraguan_democratic_coalition",
        (
            "The raw Filibuster side is decomposed into Walker's foreign force and "
            "its Nicaraguan Democratic ally; Guardiola's opposing force is bounded "
            "to the Legitimist formation in this battle."
        ),
        confidence=0.92,
    ),
    "hced-Santa Rosa de Copan1856-1": _contract(
        "hced-Santa Rosa de Copan1856-1",
        _canonical(
            "Battle of Santa Rosa (Costa Rica)",
            1856,
            "20 March 1856",
            "day",
            "single_battle_at_hacienda_santa_rosa",
        ),
        [_COSTA_RICAN_ARMY],
        [_SCHLESSINGER_DETACHMENT],
        [
            "wave8_exact_priority_mep_santa_rosa",
            "wave8_exact_priority_museo_costa_rica_forces",
        ],
        [
            "wave8_exact_priority_mep_santa_rosa",
            "wave8_exact_priority_museo_costa_rica_forces",
        ],
        "nicaragua_filibuster_conflict",
        "foreign_filibuster_intervention",
        "candidate_keyed_costa_rican_army_and_schlessinger_detachment",
        (
            "The candidate title's 'de Copan' suffix is not propagated. Costa "
            "Rican official and museum accounts locate the battle at Hacienda "
            "Santa Rosa and record the Costa Rican defeat of Walker's force."
        ),
        confidence=0.96,
    ),
    "hced-Teutoburgwald9-1": _contract(
        "hced-Teutoburgwald9-1",
        _canonical(
            "Battle of the Teutoburg Forest",
            9,
            "9 CE",
            "year",
            "multi_day_varus_battle_engagement",
        ),
        [_ARMINIUS_COALITION],
        [_ROMAN_PRINCIPATE],
        [
            "wave8_exact_priority_kalkriese_varus",
            "wave8_exact_priority_oxford_arminius",
        ],
        [
            "wave8_exact_priority_kalkriese_varus",
            "wave8_exact_priority_oxford_arminius",
        ],
        "roman_germania_conflict",
        "anti_imperial_revolt",
        "candidate_keyed_arminius_coalition_to_roman_principate",
        (
            "The Germanic side is an event-bounded Arminius-led coalition, not a "
            "generic tribal or German polity. Sources support the coalition's "
            "destruction of Varus's three Roman legions in 9 CE; no exact day is "
            "asserted."
        ),
        confidence=0.95,
    ),
    "hced-Red River1759-1": _contract(
        "hced-Red River1759-1",
        _canonical(
            "Battle of the Twin Villages",
            1759,
            "7 October 1759",
            "day",
            "single_battle_at_the_taovaya_fort",
        ),
        [_TWIN_VILLAGES_COALITION],
        [_ORTIZ_PARRILLA_EXPEDITION],
        [
            "wave8_exact_priority_ohs_twin_villages",
            "wave8_exact_priority_tsha_ortiz_parrilla",
        ],
        [
            "wave8_exact_priority_ohs_twin_villages",
            "wave8_exact_priority_tsha_ortiz_parrilla",
        ],
        "spanish_northern_frontier",
        "colonial_anti_colonial",
        "candidate_keyed_taovaya_fort_defenders_and_ortiz_expedition",
        (
            "The misspelled HCED Commanche side is resolved only for this row to "
            "the source-named Taovaya-fort defenders. The opposing side is "
            "Ortiz Parrilla's event-bounded Spanish-led expedition, not the whole "
            "Spanish Empire. The four-hour battle ended with the expedition "
            "unable to take the fort and withdrawing in order."
        ),
        confidence=0.94,
    ),
}


WAVE8_EXACT_PRIORITY_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Granada, Nicaragua1856-1": {
        "raw_row_sha256": WAVE8_EXACT_PRIORITY_ROW_HASHES[
            "hced-Granada, Nicaragua1856-1"
        ],
        "cohort": "nicaragua_filibuster_conflict",
        "disposition": "hold",
        "reason_code": "mixed_siege_relief_retreat_and_occupation_outcome",
        "evidence_refs": sorted(
            [
                "wave8_exact_priority_scroggs_granada",
                "wave8_exact_priority_walker_war_nicaragua",
            ]
        ),
        "evidence_source_family_ids": sorted(
            [
                "scroggs_filibusters_and_financiers",
                "william_walker_war_in_nicaragua",
            ]
        ),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "reserved_hced_hold",
        },
        "audit_note": (
            "The allied army enclosed and reduced Henningsen's position, but "
            "Waters broke through and relieved it, after which the filibuster force "
            "completed its destruction of Granada and embarked while the allies "
            "occupied the ruins. The row's simple Central American Allies win is "
            "known but non-atomic and therefore unrateable as one tactical "
            "outcome. It remains unscored for Elo and is not converted to a draw."
        ),
    }
}

WAVE8_EXACT_PRIORITY_CONTRACT_IDS = frozenset(WAVE8_EXACT_PRIORITY_CONTRACTS)
WAVE8_EXACT_PRIORITY_HOLD_IDS = frozenset(WAVE8_EXACT_PRIORITY_HOLDS)
WAVE8_EXACT_PRIORITY_RESERVED_IDS = WAVE8_EXACT_PRIORITY_TARGET_IDS
WAVE8_EXACT_PRIORITY_AUDITED_IDS = WAVE8_EXACT_PRIORITY_TARGET_IDS
WAVE8_EXACT_PRIORITY_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_EXACT_PRIORITY_CONTRACT_IDS
)
WAVE8_EXACT_PRIORITY_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()

WAVE8_EXACT_PRIORITY_ROW_DISPOSITIONS: dict[str, str] = {
    candidate_id: (
        "promote" if candidate_id in WAVE8_EXACT_PRIORITY_CONTRACT_IDS else "hold"
    )
    for candidate_id in sorted(WAVE8_EXACT_PRIORITY_RESERVED_IDS)
}

_EXPECTED_COUNTRIES: dict[str, str] = {
    "hced-Calpulalpam1860-1": "Mexico",
    "hced-Derna1805-1": "Libya",
    "hced-La Virgen1855-1": "Nicaragua",
    "hced-Red River1759-1": "United States",
    "hced-Santa Rosa de Copan1856-1": "Costa Rica",
    "hced-Teutoburgwald9-1": "Germany",
}

WAVE8_EXACT_PRIORITY_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    "hced-Calpulalpam1860-1": {
        "actions": ["withhold_point"],
        "reason": (
            "Sources establish the action near San Miguel Calpulalpan but do not "
            "independently authenticate HCED's exact point."
        ),
        "evidence_refs": list(
            WAVE8_EXACT_PRIORITY_CONTRACTS["hced-Calpulalpam1860-1"][
                "outcome_source_ids"
            ]
        ),
    },
    "hced-Derna1805-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed combined operation establishes Derna, not the exact "
            "coordinate of the fighting represented by the HCED point."
        ),
        "evidence_refs": list(
            WAVE8_EXACT_PRIORITY_CONTRACTS["hced-Derna1805-1"][
                "outcome_source_ids"
            ]
        ),
    },
    "hced-La Virgen1855-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The sources establish La Virgen/Virgin Bay but do not independently "
            "verify HCED's exact battlefield coordinate."
        ),
        "evidence_refs": list(
            WAVE8_EXACT_PRIORITY_CONTRACTS["hced-La Virgen1855-1"][
                "outcome_source_ids"
            ]
        ),
    },
    "hced-Santa Rosa de Copan1856-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The raw title incorrectly adds 'de Copan'; official sources identify "
            "Hacienda Santa Rosa in Costa Rica, while the HCED point is not itself "
            "authenticated."
        ),
        "evidence_refs": list(
            WAVE8_EXACT_PRIORITY_CONTRACTS[
                "hced-Santa Rosa de Copan1856-1"
            ]["outcome_source_ids"]
        ),
    },
    "hced-Teutoburgwald9-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The Varus Battle unfolded across multiple days, and the museum source "
            "does not turn HCED's single coordinate into an exact battle point."
        ),
        "evidence_refs": list(
            WAVE8_EXACT_PRIORITY_CONTRACTS["hced-Teutoburgwald9-1"][
                "outcome_source_ids"
            ]
        ),
    },
    "hced-Red River1759-1": {
        "actions": ["withhold_point"],
        "reason": (
            "HCED's coordinate is in northern New Mexico, while both historical "
            "references place the Twin Villages on the Texas-Oklahoma Red River."
        ),
        "evidence_refs": list(
            WAVE8_EXACT_PRIORITY_CONTRACTS["hced-Red River1759-1"][
                "outcome_source_ids"
            ]
        ),
    },
}

_EXPECTED_ACTOR_VECTORS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "hced-Calpulalpam1860-1": (
        (_MEXICAN_LIBERALS,),
        (_MEXICAN_CONSERVATIVES,),
    ),
    "hced-Derna1805-1": (
        (_UNITED_STATES, _HAMET_DERNA, _EATON_AUXILIARIES),
        (_TRIPOLI,),
    ),
    "hced-La Virgen1855-1": (
        (_WALKER_LA_VIRGEN, _NICARAGUAN_DEMOCRATS),
        (_NICARAGUAN_LEGITIMISTS,),
    ),
    "hced-Santa Rosa de Copan1856-1": (
        (_COSTA_RICAN_ARMY,),
        (_SCHLESSINGER_DETACHMENT,),
    ),
    "hced-Teutoburgwald9-1": (
        (_ARMINIUS_COALITION,),
        (_ROMAN_PRINCIPATE,),
    ),
    "hced-Red River1759-1": (
        (_TWIN_VILLAGES_COALITION,),
        (_ORTIZ_PARRILLA_EXPEDITION,),
    ),
}

_EXPECTED_SCALE_LEVELS: dict[str, int] = {
    "hced-Calpulalpam1860-1": 2,
    "hced-Derna1805-1": 1,
    "hced-La Virgen1855-1": 1,
    "hced-Red River1759-1": 1,
    "hced-Santa Rosa de Copan1856-1": 1,
    "hced-Teutoburgwald9-1": 3,
}

_EXPECTED_DOMAINS: dict[str, str] = {
    candidate_id: (
        "mixed" if candidate_id == "hced-Derna1805-1" else "land"
    )
    for candidate_id in sorted(WAVE8_EXACT_PRIORITY_CONTRACT_IDS)
}

_RAW_ROW_SEMANTICS: dict[str, dict[str, Any]] = {
    "hced-Calpulalpam1860-1": {
        "name": "Calpulalpam",
        "year": 1860,
        "side_1_raw": "Mexican Liberals",
        "side_2_raw": "Mexican Government",
        "winner_raw": "Mexican Liberals",
        "loser_raw": "Mexican Government",
        "massacre_raw": "No",
        "modern_location_country": "Mexico",
    },
    "hced-Derna1805-1": {
        "name": "Derna",
        "year": 1805,
        "side_1_raw": "United States",
        "side_2_raw": "Tripoli",
        "winner_raw": "United States",
        "loser_raw": "Tripoli",
        "massacre_raw": "No",
        "modern_location_country": "Libya",
    },
    "hced-Granada, Nicaragua1856-1": {
        "name": "Granada, Nicaragua",
        "year": 1856,
        "side_1_raw": "Central American Allies",
        "side_2_raw": "Filibusters",
        "winner_raw": "Central American Allies",
        "loser_raw": "Filibusters",
        "massacre_raw": "No",
        "modern_location_country": "Nicaragua",
    },
    "hced-La Virgen1855-1": {
        "name": "La Virgen",
        "year": 1855,
        "side_1_raw": "Filibusters",
        "side_2_raw": "Legitimists",
        "winner_raw": "Filibusters",
        "loser_raw": "Legitimists",
        "massacre_raw": "No",
        "modern_location_country": "Nicaragua",
    },
    "hced-Red River1759-1": {
        "name": "Red River",
        "year": 1759,
        "side_1_raw": "Commanche",
        "side_2_raw": "Spain",
        "winner_raw": "Commanche",
        "loser_raw": "Spain",
        "massacre_raw": "No",
        "modern_location_country": "United States",
    },
    "hced-Santa Rosa de Copan1856-1": {
        "name": "Santa Rosa de Copan",
        "year": 1856,
        "side_1_raw": "Costa Rica",
        "side_2_raw": "Filibusters",
        "winner_raw": "Costa Rica",
        "loser_raw": "Filibusters",
        "massacre_raw": "No",
        "modern_location_country": "Costa Rica",
    },
    "hced-Teutoburgwald9-1": {
        "name": "Teutoburgwald",
        "year": 9,
        "side_1_raw": "Germanic Tribes",
        "side_2_raw": "Rome",
        "winner_raw": "Germanic Tribes",
        "loser_raw": "Rome",
        "massacre_raw": "Battle followed by massacre",
        "modern_location_country": "Germany",
    },
}

_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Calpulalpam1860-1": {
        "Calpulalpam",
        "Calpulalpan",
        "Battle of Calpulalpan",
    },
    "hced-Derna1805-1": {"Derna", "Derne", "Battle of Derna"},
    "hced-Granada, Nicaragua1856-1": {
        "Granada, Nicaragua",
        "Destruction of Granada",
        "Retreat from Granada",
    },
    "hced-La Virgen1855-1": {
        "La Virgen",
        "Virgin Bay",
        "Battle of La Virgen",
    },
    "hced-Red River1759-1": {
        "Red River",
        "Battle of the Twin Villages",
        "Twin Villages",
    },
    "hced-Santa Rosa de Copan1856-1": {
        "Santa Rosa de Copan",
        "Battle of Santa Rosa",
        "Battle of Santa Rosa (Costa Rica)",
    },
    "hced-Teutoburgwald9-1": {
        "Teutoburgwald",
        "Battle of the Teutoburg Forest",
        "Varus Battle",
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_EXACT_PRIORITY_CONTRACTS,
        "entities": WAVE8_EXACT_PRIORITY_ENTITIES,
        "event_aliases": {
            candidate_id: sorted(aliases)
            for candidate_id, aliases in sorted(_EVENT_ALIASES.items())
        },
        "expected_actor_vectors": _EXPECTED_ACTOR_VECTORS,
        "expected_countries": _EXPECTED_COUNTRIES,
        "expected_domains": _EXPECTED_DOMAINS,
        "expected_scale_levels": _EXPECTED_SCALE_LEVELS,
        "holds": WAVE8_EXACT_PRIORITY_HOLDS,
        "location_reasons": WAVE8_EXACT_PRIORITY_LOCATION_QUARANTINE_REASONS,
        "point_quarantine_ids": sorted(
            WAVE8_EXACT_PRIORITY_POINT_QUARANTINE_ADDITIONS
        ),
        "raw_row_semantics": _RAW_ROW_SEMANTICS,
        "row_dispositions": WAVE8_EXACT_PRIORITY_ROW_DISPOSITIONS,
        "row_hashes": WAVE8_EXACT_PRIORITY_ROW_HASHES,
        "sources": WAVE8_EXACT_PRIORITY_SOURCES,
    }


def wave8_exact_priority_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_EXACT_PRIORITY_FINAL_AUDIT_SIGNATURE = (
    "e4e46f76859cccf692191072e477281140851268fc84978ac9aa0fd10802f0a9"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static(*, check_signature: bool = True) -> None:
    source_by_id = {
        str(source["id"]): source for source in WAVE8_EXACT_PRIORITY_SOURCES
    }
    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_EXACT_PRIORITY_ENTITIES
    }
    if len(source_by_id) != len(WAVE8_EXACT_PRIORITY_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if source_by_id != _SOURCE_BY_ID:
        raise ValueError(f"{_LANE_NAME} source inventory drift")
    if len(entity_by_id) != len(WAVE8_EXACT_PRIORITY_ENTITIES):
        raise ValueError(f"{_LANE_NAME} duplicate entity id")
    if entity_by_id != _ENTITY_BY_ID or len(entity_by_id) != 10:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_EXACT_PRIORITY_TARGET_IDS != set(WAVE8_EXACT_PRIORITY_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} audited-row inventory drift")
    if WAVE8_EXACT_PRIORITY_RESERVED_IDS != (
        WAVE8_EXACT_PRIORITY_CONTRACT_IDS | WAVE8_EXACT_PRIORITY_HOLD_IDS
    ):
        raise ValueError(f"{_LANE_NAME} reservation partition drift")
    if len(WAVE8_EXACT_PRIORITY_CONTRACT_IDS) != 6 or len(
        WAVE8_EXACT_PRIORITY_HOLD_IDS
    ) != 1:
        raise ValueError(f"{_LANE_NAME} disposition count drift")
    if WAVE8_EXACT_PRIORITY_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_EXACT_PRIORITY_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine drift")
    if WAVE8_EXACT_PRIORITY_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country quarantine drift")
    if set(WAVE8_EXACT_PRIORITY_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_EXACT_PRIORITY_POINT_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location-reason inventory drift")
    if set(_EXPECTED_ACTOR_VECTORS) != WAVE8_EXACT_PRIORITY_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} actor contract inventory drift")
    if set(_EXPECTED_COUNTRIES) != WAVE8_EXACT_PRIORITY_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} country contract inventory drift")
    if set(_EXPECTED_SCALE_LEVELS) != WAVE8_EXACT_PRIORITY_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} scale-level contract inventory drift")
    if set(_EXPECTED_DOMAINS) != WAVE8_EXACT_PRIORITY_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} domain contract inventory drift")
    expected_dispositions = {
        candidate_id: (
            "promote"
            if candidate_id in WAVE8_EXACT_PRIORITY_CONTRACT_IDS
            else "hold"
        )
        for candidate_id in sorted(WAVE8_EXACT_PRIORITY_RESERVED_IDS)
    }
    if WAVE8_EXACT_PRIORITY_ROW_DISPOSITIONS != expected_dispositions:
        raise ValueError(f"{_LANE_NAME} row-disposition inventory drift")

    for source_id, source in source_by_id.items():
        roles = list(map(str, source.get("evidence_roles", [])))
        if (
            not source.get("source_family_id")
            or not _is_sorted_unique(roles)
            or "identity_boundary_or_context_reference" not in roles
        ):
            raise ValueError(f"{_LANE_NAME} source provenance drift: {source_id}")

    for entity_id, entity in entity_by_id.items():
        if (
            (entity.get("start_year"), entity.get("end_year"))
            not in {(9, 9), (1759, 1759), (1805, 1805), (1855, 1855), (1856, 1856)}
            or entity.get("aliases")
            or entity.get("predecessors")
            or "No rating is inherited" not in str(entity.get("continuity_note"))
        ):
            raise ValueError(f"{_LANE_NAME} identity boundary drift: {entity_id}")
        entity_sources = list(map(str, entity.get("source_ids", [])))
        if not _is_sorted_unique(entity_sources) or not set(entity_sources) <= set(
            source_by_id
        ):
            raise ValueError(f"{_LANE_NAME} entity source drift: {entity_id}")

    used_sources: set[str] = set()
    used_new_entities: set[str] = set()
    for candidate_id, contract in WAVE8_EXACT_PRIORITY_CONTRACTS.items():
        expected_side_1, expected_side_2 = _EXPECTED_ACTOR_VECTORS[candidate_id]
        side_1 = tuple(map(str, contract["side_1_entity_ids"]))
        side_2 = tuple(map(str, contract["side_2_entity_ids"]))
        canonical = contract["canonical_event"]
        year_low = int(canonical["year_low"])
        year_high = int(canonical["year_high"])
        expected_key = f"{_slug(str(canonical['name']))}:{year_low}:{year_high}"
        if contract["raw_row_sha256"] != WAVE8_EXACT_PRIORITY_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract row hash drift: {candidate_id}")
        if (
            contract.get("disposition") != "promote"
            or contract.get("result_type") != "win"
            or contract.get("winner_side") != 1
            or contract.get("source_date_override") is not False
            or contract.get("source_outcome_override") is not False
            or contract.get("outcome_reversal") is not False
        ):
            raise ValueError(f"{_LANE_NAME} outcome policy drift: {candidate_id}")
        if side_1 != expected_side_1 or side_2 != expected_side_2:
            raise ValueError(f"{_LANE_NAME} coalition decomposition drift: {candidate_id}")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} invalid opposing sides: {candidate_id}")
        if (
            year_low != year_high
            or canonical.get("canonical_key") != expected_key
            or canonical.get("date_precision") not in {"day", "year"}
            or not canonical.get("date_text")
        ):
            raise ValueError(f"{_LANE_NAME} chronology drift: {candidate_id}")
        evidence = list(map(str, contract.get("evidence_refs", [])))
        outcomes = list(map(str, contract.get("outcome_source_ids", [])))
        if (
            not _is_sorted_unique(evidence)
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence) <= set(source_by_id)
            or len(outcomes) < 2
        ):
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} non-outcome source cited: {candidate_id}")
        families = sorted(
            {
                str(source_by_id[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract.get("outcome_source_family_ids") != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)
        used_new_entities.update((set(side_1) | set(side_2)) & set(entity_by_id))

    hold = WAVE8_EXACT_PRIORITY_HOLDS.get("hced-Granada, Nicaragua1856-1")
    if not isinstance(hold, Mapping):
        raise ValueError(f"{_LANE_NAME} Granada hold missing")
    hold_evidence = list(map(str, hold.get("evidence_refs", [])))
    hold_families = sorted(
        {
            str(source_by_id[source_id]["source_family_id"])
            for source_id in hold_evidence
            if source_id in source_by_id
        }
    )
    if (
        hold.get("disposition") != "hold"
        or not hold.get("reason_code")
        or any(key in hold for key in ("result_type", "winner_side"))
        or not _is_sorted_unique(hold_evidence)
        or not set(hold_evidence) <= set(source_by_id)
        or hold.get("evidence_source_family_ids") != hold_families
        or len(hold_families) < 2
    ):
        raise ValueError(f"{_LANE_NAME} Granada hold drift")
    used_sources.update(hold_evidence)

    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new identities are not exactly consumed")
    if check_signature and (
        wave8_exact_priority_audit_signature()
        != WAVE8_EXACT_PRIORITY_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_exact_priority_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all seven rows, including the discovery safety firewall."""

    _validate_static()
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str) and candidate_id in (
            WAVE8_EXACT_PRIORITY_RESERVED_IDS
        ):
            indexed.setdefault(candidate_id, []).append(row)
    if set(indexed) != WAVE8_EXACT_PRIORITY_RESERVED_IDS or any(
        len(rows) != 1 for rows in indexed.values()
    ):
        raise ValueError(f"{_LANE_NAME} reserved candidate inventory changed")

    for candidate_id, expected_hash in WAVE8_EXACT_PRIORITY_ROW_HASHES.items():
        row = indexed[candidate_id][0]
        semantics = _RAW_ROW_SEMANTICS[candidate_id]
        year = semantics["year"]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            row.get("do_not_rate_automatically") is not True
            or row.get("winner_loser_complete") is not True
            or (row.get("year_low"), row.get("year_best"), row.get("year_high"))
            != (year, year, year)
            or any(
                row.get(key) != value
                for key, value in semantics.items()
                if key != "year"
            )
            or row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
        ):
            raise ValueError(f"{_LANE_NAME} raw-row semantics changed: {candidate_id}")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_EXACT_PRIORITY_CONTRACTS,
        WAVE8_EXACT_PRIORITY_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "audited_candidate_rows": len(WAVE8_EXACT_PRIORITY_AUDITED_IDS),
        "automated_discovery_rows": sum(
            row[0].get("do_not_rate_automatically") is True
            for row in indexed.values()
        ),
        "reserved_hced_rows": len(WAVE8_EXACT_PRIORITY_RESERVED_IDS),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "batyear"):
        try:
            if row.get(key) is not None:
                return int(row[key])
        except (TypeError, ValueError):
            pass
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(_RAW_ROW_SEMANTICS[candidate_id]["year"]),
        normalize_label(alias),
    )
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_exact_priority_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Reject unreviewed twins, held-row leakage, and partial integration."""

    validate_wave8_exact_priority_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_EXACT_PRIORITY_RESERVED_IDS
        and _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    existing = list(existing_events)
    hold_leaks = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_EXACT_PRIORITY_HOLD_IDS
    )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id") not in WAVE8_EXACT_PRIORITY_RESERVED_IDS
        and not str(event.get("id") or "").startswith(_EVENT_ID_PREFIX)
        and _is_probable_twin(event)
    )
    overlap = {
        str(event.get("hced_candidate_id"))
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_EXACT_PRIORITY_CONTRACT_IDS
    }
    if hced_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable twin(s): "
            f"hced={hced_twins}, iwbd={iwbd_twins}, release={release_twins}"
        )
    if hold_leaks:
        raise ValueError(f"{_LANE_NAME} held Granada row was rated: {hold_leaks}")
    if overlap not in (set(), set(WAVE8_EXACT_PRIORITY_CONTRACT_IDS)):
        raise ValueError(f"{_LANE_NAME} release overlap is partial: {sorted(overlap)}")
    return {
        "existing_release_probable_twins": 0,
        "held_release_events": 0,
        "hced_probable_twins": 0,
        "iwbd_probable_twins": 0,
        "release_lane_overlap": len(overlap),
    }


def install_wave8_exact_priority_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_EXACT_PRIORITY_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_exact_priority_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_EXACT_PRIORITY_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_EXACT_PRIORITY_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_EXACT_PRIORITY_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_exact_priority_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Promote exactly six rows and never emit the reserved Granada hold."""

    validate_wave8_exact_priority_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_EXACT_PRIORITY_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def _records_by_id(
    records: Mapping[str, Mapping[str, Any]] | Iterable[Mapping[str, Any]],
    *,
    record_type: str,
) -> dict[str, Mapping[str, Any]]:
    if isinstance(records, Mapping):
        result = {str(key): value for key, value in records.items()}
        if any(str(value.get("id")) != key for key, value in result.items()):
            raise ValueError(f"{_LANE_NAME} {record_type} mapping key/id drift")
        return result
    result: dict[str, Mapping[str, Any]] = {}
    for record in records:
        record_id = str(record.get("id") or "")
        if not record_id or record_id in result:
            raise ValueError(f"{_LANE_NAME} duplicate or blank {record_type} id")
        result[record_id] = record
    return result


def validate_wave8_exact_priority_release_inventory(
    release_entities: Mapping[str, Mapping[str, Any]]
    | Iterable[Mapping[str, Any]],
    release_sources: Mapping[str, Mapping[str, Any]]
    | Iterable[Mapping[str, Any]],
    release_events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    """Validate the complete projected release surface owned by this lane."""

    _validate_static()
    entities = _records_by_id(release_entities, record_type="entity")
    sources = _records_by_id(release_sources, record_type="source")
    for fixture in WAVE8_EXACT_PRIORITY_ENTITIES:
        entity_id = str(fixture["id"])
        if entities.get(entity_id) != fixture:
            raise ValueError(f"{_LANE_NAME} release entity drift: {entity_id}")
    for fixture in WAVE8_EXACT_PRIORITY_SOURCES:
        source_id = str(fixture["id"])
        if sources.get(source_id) != fixture:
            raise ValueError(f"{_LANE_NAME} release source provenance drift: {source_id}")

    all_actor_ids = {
        entity_id
        for sides in _EXPECTED_ACTOR_VECTORS.values()
        for side in sides
        for entity_id in side
    }
    missing_actors = sorted(all_actor_ids - set(entities))
    if missing_actors:
        raise ValueError(f"{_LANE_NAME} release actor inventory missing: {missing_actors}")
    for candidate_id, (side_1, side_2) in _EXPECTED_ACTOR_VECTORS.items():
        year = int(
            WAVE8_EXACT_PRIORITY_CONTRACTS[candidate_id]["canonical_event"][
                "year_low"
            ]
        )
        for entity_id in (*side_1, *side_2):
            entity = entities[entity_id]
            start = entity.get("start_year")
            end = entity.get("end_year")
            if start is None or int(start) > year or (
                end is not None and int(end) < year
            ):
                raise ValueError(
                    f"{_LANE_NAME} release identity-window violation: "
                    f"{candidate_id}/{entity_id}"
                )

    events = list(release_events)
    owned_events = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_EXACT_PRIORITY_RESERVED_IDS
        or str(event.get("id") or "").startswith(_EVENT_ID_PREFIX)
    ]
    held = [
        event
        for event in owned_events
        if event.get("hced_candidate_id") in WAVE8_EXACT_PRIORITY_HOLD_IDS
    ]
    if held:
        raise ValueError(f"{_LANE_NAME} held Granada row leaked into release")
    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for event in owned_events:
        candidate_id = str(event.get("hced_candidate_id") or "")
        by_candidate.setdefault(candidate_id, []).append(event)
    if set(by_candidate) != WAVE8_EXACT_PRIORITY_CONTRACT_IDS or any(
        len(events) != 1 for events in by_candidate.values()
    ):
        raise ValueError(f"{_LANE_NAME} release event inventory drift")

    for candidate_id, contract in WAVE8_EXACT_PRIORITY_CONTRACTS.items():
        event = by_candidate[candidate_id][0]
        canonical = contract["canonical_event"]
        scale_level = _EXPECTED_SCALE_LEVELS[candidate_id]
        expected_scale = "skirmish" if scale_level == 1 else "battle"
        expected_id = f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        expected_fields = {
            "id": expected_id,
            "name": canonical["name"],
            "year": canonical["year_low"],
            "end_year": canonical["year_high"],
            "event_type": "engagement",
            "war_type": contract["war_type"],
            "scale": expected_scale,
            "stakes": "limited",
            "decisiveness": round(min(0.90, 0.54 + 0.06 * scale_level), 2),
            "geographic_scope": round(
                min(0.70, 0.08 + 0.09 * scale_level), 2
            ),
            "domain": _EXPECTED_DOMAINS[candidate_id],
            "confidence": contract["confidence"],
            "date_precision": canonical["date_precision"],
            "canonical_event_key": canonical["canonical_key"],
            "reviewed_granularity": canonical["granularity"],
            "identity_resolution": "candidate_keyed_exact",
            "status": "complete",
            "modern_location_country": _EXPECTED_COUNTRIES[candidate_id],
        }
        if any(event.get(key) != value for key, value in expected_fields.items()):
            raise ValueError(f"{_LANE_NAME} release event provenance drift: {candidate_id}")
        if "geometry" in event or "location_provenance" not in event:
            raise ValueError(f"{_LANE_NAME} release point quarantine drift: {candidate_id}")
        raw_name = str(_RAW_ROW_SEMANTICS[candidate_id]["name"])
        expected_aliases = (
            [raw_name] if raw_name != str(canonical["name"]) else []
        )
        if list(map(str, event.get("aliases", []))) != expected_aliases:
            raise ValueError(f"{_LANE_NAME} release event alias drift: {candidate_id}")
        if list(map(str, event.get("source_ids", []))) != [
            "hced_dataset",
            *contract["evidence_refs"],
        ]:
            raise ValueError(f"{_LANE_NAME} release evidence drift: {candidate_id}")
        if (
            list(map(str, event.get("outcome_source_ids", [])))
            != contract["outcome_source_ids"]
            or list(map(str, event.get("outcome_source_family_ids", [])))
            != contract["outcome_source_family_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} release outcome provenance drift: {candidate_id}")

        side_1, side_2 = _EXPECTED_ACTOR_VECTORS[candidate_id]
        expected_participants = expected_exact_hced_win_participants(
            side_1,
            side_2,
            confidence=float(contract["confidence"]),
            scale_level=scale_level,
            lane_name=_LANE_NAME,
        )
        if list(event.get("participants", [])) != expected_participants:
            raise ValueError(f"{_LANE_NAME} release outcome drift: {candidate_id}")

    new_entity_ids = set(_ENTITY_BY_ID)
    outside_uses = sorted(
        str(event.get("id") or "<missing-id>")
        for event in events
        if event not in owned_events
        and new_entity_ids
        & {
            str(participant.get("entity_id"))
            for participant in event.get("participants", [])
        }
    )
    if outside_uses:
        raise ValueError(
            f"{_LANE_NAME} event-bounded identities used outside exact contracts: "
            f"{outside_uses}"
        )

    return {
        "held_candidate_events": 0,
        "lane_entities": len(WAVE8_EXACT_PRIORITY_ENTITIES),
        "lane_events": len(WAVE8_EXACT_PRIORITY_CONTRACTS),
        "lane_sources": len(WAVE8_EXACT_PRIORITY_SOURCES),
        "outside_entity_uses": 0,
        "reserved_candidate_ids": len(WAVE8_EXACT_PRIORITY_RESERVED_IDS),
    }


def validate_wave8_exact_priority_final_audit(
    release_entities: Mapping[str, Mapping[str, Any]]
    | Iterable[Mapping[str, Any]],
    release_sources: Mapping[str, Mapping[str, Any]]
    | Iterable[Mapping[str, Any]],
    release_events: Iterable[Mapping[str, Any]],
    lane_metadata: Mapping[str, Any],
) -> dict[str, Any]:
    """Pin release inventory and the complete lane metadata/audit contract."""

    release_counts = validate_wave8_exact_priority_release_inventory(
        release_entities,
        release_sources,
        release_events,
    )
    expected_metadata = wave8_exact_priority_metadata()
    if dict(lane_metadata) != expected_metadata:
        raise ValueError(f"{_LANE_NAME} final release metadata drift")
    return {
        **release_counts,
        "final_audit_signature": WAVE8_EXACT_PRIORITY_FINAL_AUDIT_SIGNATURE,
    }


def wave8_exact_priority_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_EXACT_PRIORITY_CONTRACTS.values(),
                    *WAVE8_EXACT_PRIORITY_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_exact_priority_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_EXACT_PRIORITY_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "holds": len(WAVE8_EXACT_PRIORITY_HOLDS),
        "new_entities": len(WAVE8_EXACT_PRIORITY_ENTITIES),
        "new_sources": len(WAVE8_EXACT_PRIORITY_SOURCES),
        "newly_rated_events": len(WAVE8_EXACT_PRIORITY_CONTRACTS),
        "outcome_overrides": 0,
        "outcome_reversals": 0,
        "point_quarantine_additions": len(
            WAVE8_EXACT_PRIORITY_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_EXACT_PRIORITY_CONTRACTS),
        "reserved_hced_rows": len(WAVE8_EXACT_PRIORITY_RESERVED_IDS),
        "reviewed_hced_rows": len(WAVE8_EXACT_PRIORITY_AUDITED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_exact_priority_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "audit": "candidate_keyed_exact_event_bounded_priority_rows",
        "counts": wave8_exact_priority_counts(),
        "cohorts": wave8_exact_priority_cohort_counts(),
        "final_audit_signature": WAVE8_EXACT_PRIORITY_FINAL_AUDIT_SIGNATURE,
        "held_candidate_ids": sorted(WAVE8_EXACT_PRIORITY_HOLD_IDS),
        "module_owner": _MODULE_OWNER,
        "promoted_candidate_ids": sorted(WAVE8_EXACT_PRIORITY_CONTRACT_IDS),
        "reserved_candidate_ids": sorted(WAVE8_EXACT_PRIORITY_RESERVED_IDS),
        "row_dispositions": dict(sorted(WAVE8_EXACT_PRIORITY_ROW_DISPOSITIONS.items())),
    }


_validate_static()
