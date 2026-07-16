"""Exact Wave 8 contracts for the audited post-Wave-8 fast-17 HCED lane."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


_LANE_NAME = "Wave 8 fast 17"
_EVENT_ID_PREFIX = "hced_wave8_fast17_"

# This signature covers the complete lane contract: promotions, holds, entities,
# sources, location quarantines, and the cross-dataset IWBD duplicate hold.
WAVE8_FAST17_FINAL_AUDIT_SIGNATURE = (
    "ca5ad66ac0a6782c0be88ba9c0eadb702a8716ec36e96e7f39314c3643d818a2"
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
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "linked_reference",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": roles,
    }


WAVE8_FAST17_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "post_wave8_samhs_groenkloof_1901",
        "The Capture of Lotter's Commando",
        "https://samilitaryhistory.org/vol015hk.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "post_wave8_samhs_harrismith",
        "Harrismith",
        "https://samilitaryhistory.org/vol081sw.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "post_wave8_samhs_moedwil_1901",
        "The Imperial Yeomanry, Part Two: 1901",
        "https://www.samilitaryhistory.org/vol141sw.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "post_wave8_samhs_poplar_grove_1900",
        "French Military Attaché in South Africa, February–June 1900",
        "https://www.samilitaryhistory.org/vol091cj.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "post_wave8_de_wet_three_years_war",
        "Three Years' War",
        "https://www.gutenberg.org/files/18794/18794-h/18794-h.htm",
        "Project Gutenberg — C. R. de Wet memoir",
        "primary_memoir",
        "de_wet_memoir",
    ),
    _source(
        "post_wave8_awm_nsw_mounted_rifles",
        "1st New South Wales Mounted Rifles",
        "https://www.awm.gov.au/collection/U52007",
        "Australian War Memorial",
        "official_military_history",
        "australian_war_memorial",
        outcome=False,
    ),
    _source(
        "post_wave8_samhs_vaalkrans_1900",
        "The Battle of Vaalkrans",
        "https://samilitaryhistory.org/vol072sw.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "post_wave8_museo_alpini_part1",
        "La guerra sulle Alpi nel '700 — Prima Parte",
        "https://www.museonazionalealpini.it/la-guerra-sulle-alpini-nel-700/",
        "Museo Nazionale Storico degli Alpini",
        "military_museum_history",
        "museo_nazionale_storico_alpini",
    ),
    _source(
        "post_wave8_museo_alpini_part2",
        "La guerra sulle Alpi nel '700 — Seconda Parte",
        "https://www.museonazionalealpini.it/la-guerra-sulle-alpi-nel-700-seconda-parte/",
        "Museo Nazionale Storico degli Alpini",
        "military_museum_history",
        "museo_nazionale_storico_alpini",
    ),
    _source(
        "post_wave8_italian_navy_la_maddalena_1793",
        "La difesa dell'isola di La Maddalena",
        (
            "https://www.marina.difesa.it/cosa-facciamo/storia/la-nostra-storia/"
            "medaglie/Pagine/maddalena.aspx"
        ),
        "Marina Militare Italiana",
        "official_military_history",
        "italian_navy_history",
    ),
    _source(
        "post_wave8_vicenza_museum_1848",
        "Vicenza 1848 — Museo del Risorgimento e della Resistenza guide",
        "https://www.museicivicivicenza.it/file/doc1-10911.pdf",
        "Musei Civici di Vicenza",
        "municipal_museum_history",
        "musei_civici_vicenza",
    ),
    _source(
        "post_wave8_serbia_mod_ivankovac_1805",
        "Boj na Ivankovcu — 18. avgust 1805. godine",
        (
            "https://www.mod.gov.rs/lat/11331/"
            "boj-na-ivankovcu-18-avgust-1805-godine-11331"
        ),
        "Ministry of Defence of the Republic of Serbia",
        "official_military_history",
        "serbian_ministry_of_defence",
    ),
    _source(
        "post_wave8_serbia_mod_deligrad_1806",
        "Obeležena 212. godišnjica boja na Deligradu",
        (
            "https://www.mod.gov.rs/lat/12974/"
            "obelezena-212-godisnjica-boja-na-deligradu-12974"
        ),
        "Ministry of Defence of the Republic of Serbia",
        "official_military_history",
        "serbian_ministry_of_defence",
    ),
    _source(
        "post_wave8_belgrade_fortress_1807",
        "About the complex: Belgrade Fortress in the New Age",
        "https://www.beogradskatvrdjava.co.rs/o-kompleksu/?lang=en",
        "JP Beogradska tvrđava, City of Belgrade",
        "municipal_history",
        "city_of_belgrade",
    ),
    _source(
        "post_wave8_serbia_mod_cegar_1809",
        "Obeležena godišnjica bitke na Čegru",
        (
            "https://www.mod.gov.rs/lat/11077/"
            "obelezena-godisnjica-bitke-na-cegru-11077"
        ),
        "Ministry of Defence of the Republic of Serbia",
        "official_military_history",
        "serbian_ministry_of_defence",
    ),
)


WAVE8_FAST17_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "lotter_commando_1901",
        "name": "Commandant Lotter's Commando (1901)",
        "kind": "event_bounded_boer_commando",
        "start_year": 1901,
        "end_year": 1901,
        "region": "Southern Africa",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The distinct commando under Commandant Lotter captured at "
            "Groenkloof/Bouwershoek on 5 September 1901. This identity is "
            "event-bounded; no rating is inherited by either Boer republic, a "
            "generic Boer or Cape-rebel identity, or any successor."
        ),
        "source_ids": ["post_wave8_samhs_groenkloof_1901"],
    },
    {
        "id": "durando_vicenza_defense_force_1848",
        "name": "Durando's Vicenza Defense Force (1848)",
        "kind": "event_bounded_defense_coalition",
        "start_year": 1848,
        "end_year": 1848,
        "region": "Southern Europe",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The Papal-service militias and Venetian and Romagnol volunteers "
            "under General Giovanni Durando that defended Vicenza and capitulated "
            "on 10–11 June 1848. This identity is event-bounded; no rating is "
            "inherited by Sardinia, the Papal States, Venice, a generic "
            "Italian-volunteer identity, or any successor."
        ),
        "source_ids": ["post_wave8_vicenza_museum_1848"],
    },
)


def _canonical(
    name: str,
    year_low: int,
    year_high: int | None = None,
    *,
    granularity: str = "engagement",
) -> dict[str, Any]:
    high = year_low if year_high is None else year_high
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{high}",
        "date_precision": "year",
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": high,
    }


def _contract(
    row_hash: str,
    canonical: dict[str, Any],
    cohort: str,
    side_1: list[str],
    side_2: list[str],
    evidence_refs: list[str],
    outcome_source_ids: list[str],
    outcome_source_family_ids: list[str],
    audit_note: str,
    *,
    war_type: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": row_hash,
        "canonical_event": canonical,
        "cohort": cohort,
        "side_1_entity_ids": side_1,
        "side_2_entity_ids": side_2,
        "winner_side": 1,
        "war_type": war_type,
        "evidence_refs": evidence_refs,
        "outcome_source_ids": outcome_source_ids,
        "outcome_source_family_ids": outcome_source_family_ids,
        "source_outcome_override": False,
        "audit_note": audit_note,
    }


WAVE8_FAST17_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Groenkloof1901-1": _contract(
        "c7d16764a31c90e39b0313b65d0a1785b31f82be52e826e670e97825a2b07719",
        _canonical("Battle of Groenkloof", 1901),
        "second_anglo_boer_war",
        ["united_kingdom"],
        ["lotter_commando_1901"],
        ["post_wave8_samhs_groenkloof_1901"],
        ["post_wave8_samhs_groenkloof_1901"],
        ["south_african_military_history_society"],
        (
            "The British victory is retained without reversal, while the raw "
            "two-republic coalition is replaced by Lotter's exact event-bounded "
            "commando. The staged point is quarantined as a false Groenkloof."
        ),
        war_type="colonial_anti_colonial",
    ),
    "hced-Ladysmith1899-1900-1": _contract(
        "2a3333250f47f52616d8047be8cc06eedcb27d8de3331fa471a6904f9efd4e97",
        _canonical("Siege of Ladysmith", 1899, 1900, granularity="siege"),
        "second_anglo_boer_war",
        ["united_kingdom"],
        ["south_african_republic", "orange_free_state_1854"],
        ["post_wave8_samhs_harrismith"],
        ["post_wave8_samhs_harrismith"],
        ["south_african_military_history_society"],
        (
            "The relief ending the 1899–1900 siege is a British tactical victory "
            "over the two time-valid Boer republics; the HCED outcome is not "
            "reversed."
        ),
        war_type="colonial_anti_colonial",
    ),
    "hced-Moedwil1901-1": _contract(
        "3c484b643d46d53098e547d5695f41342dd242ec62c455b01ca886b5b9363ec0",
        _canonical("Battle of Moedwil", 1901),
        "second_anglo_boer_war",
        ["united_kingdom"],
        ["south_african_republic"],
        ["post_wave8_samhs_moedwil_1901"],
        ["post_wave8_samhs_moedwil_1901"],
        ["south_african_military_history_society"],
        (
            "The source confirms the British tactical victory and identifies the "
            "opposing commando with the South African Republic, not an invented "
            "two-republic coalition."
        ),
        war_type="colonial_anti_colonial",
    ),
    "hced-Poplar Grove1900-1": _contract(
        "7df08ead305dd3582038915b4712cf42788e3e71f7a2395e67011169d305d82c",
        _canonical("Battle of Poplar Grove", 1900),
        "second_anglo_boer_war",
        ["united_kingdom"],
        ["south_african_republic", "orange_free_state_1854"],
        [
            "post_wave8_awm_nsw_mounted_rifles",
            "post_wave8_de_wet_three_years_war",
            "post_wave8_samhs_poplar_grove_1900",
        ],
        [
            "post_wave8_de_wet_three_years_war",
            "post_wave8_samhs_poplar_grove_1900",
        ],
        ["de_wet_memoir", "south_african_military_history_society"],
        (
            "The British victory is retained. Australian troops are evidenced as "
            "units of the British force, not promoted as a separate polity; both "
            "Boer republics are retained as opposing belligerents."
        ),
        war_type="colonial_anti_colonial",
    ),
    "hced-Sannahs Post1916-1": _contract(
        "cfcc5d99d9ef957c4d2351afa960289b23e4d1654d1bc113e1d344aeff9ea248",
        _canonical("Battle of Sanna's Post", 1900),
        "second_anglo_boer_war",
        ["orange_free_state_1854"],
        ["united_kingdom"],
        [
            "post_wave8_de_wet_three_years_war",
            "post_wave8_samhs_poplar_grove_1900",
        ],
        [
            "post_wave8_de_wet_three_years_war",
            "post_wave8_samhs_poplar_grove_1900",
        ],
        ["de_wet_memoir", "south_african_military_history_society"],
        (
            "The direct sources confirm the 1900 Orange Free State victory. The "
            "1916 text in the HCED record identifier is not treated as an event "
            "date, and Transvaal is not added to De Wet's force."
        ),
        war_type="colonial_anti_colonial",
    ),
    "hced-Tugela Heights1900-1": _contract(
        "ea01591115c454c2534b2a5fdcb731c37c22144a7ec88c8adb116a5726e5f00f",
        _canonical(
            "Battle of Tugela Heights",
            1900,
            granularity="engagement_series",
        ),
        "second_anglo_boer_war",
        ["united_kingdom"],
        ["south_african_republic", "orange_free_state_1854"],
        ["post_wave8_samhs_harrismith"],
        ["post_wave8_samhs_harrismith"],
        ["south_african_military_history_society"],
        (
            "The linked engagement series ending in the relief of Ladysmith is "
            "rated once as the staged British victory over both Boer republics."
        ),
        war_type="colonial_anti_colonial",
    ),
    "hced-Vaal Kranz1900-1": _contract(
        "0b471b70ba08b25796d61d40d444d7db65e0927ddb24ead1682f81337c981366",
        _canonical("Battle of Vaalkrans", 1900),
        "second_anglo_boer_war",
        ["orange_free_state_1854", "south_african_republic"],
        ["united_kingdom"],
        ["post_wave8_samhs_vaalkrans_1900"],
        ["post_wave8_samhs_vaalkrans_1900"],
        ["south_african_military_history_society"],
        (
            "The source confirms the Boer tactical success without reversing the "
            "staged winner. The HCED coordinates are quarantined because they "
            "resolve to a different South African locality."
        ),
        war_type="colonial_anti_colonial",
    ),
    "hced-Wagon Hill1900-1": _contract(
        "11f3741582cae6ae396d603743851eed912397e9d8620f8e74817a13cf604217",
        _canonical("Battle of Wagon Hill", 1900),
        "second_anglo_boer_war",
        ["united_kingdom"],
        ["orange_free_state_1854"],
        ["post_wave8_samhs_harrismith"],
        ["post_wave8_samhs_harrismith"],
        ["south_african_military_history_society"],
        (
            "The British defensive victory is retained, and the attacking force "
            "is confined to the Orange Free State rather than the raw generic "
            "two-republic coalition."
        ),
        war_type="colonial_anti_colonial",
    ),
    "hced-Assietta1747-1": _contract(
        "3bb131c6b769f24555e570744dc1b98fbd3ff843e8c2f0c5f37af78d27aea1e8",
        _canonical("Battle of Assietta", 1747),
        "war_of_austrian_succession",
        ["kingdom_sardinia_piedmont", "habsburg_monarchy"],
        ["kingdom_france"],
        ["post_wave8_museo_alpini_part2"],
        ["post_wave8_museo_alpini_part2"],
        ["museo_nazionale_storico_alpini"],
        (
            "The institutional military-museum history confirms the defensive "
            "victory and the Austrian contingent allied with Sardinia; no outcome "
            "reversal is introduced."
        ),
        war_type="interstate_limited",
    ),
    "hced-Casteldelfino1744-1": _contract(
        "86c07309452e1ce13703780d232d9047e877232ee8e71ca91c5cb5f4bb0d8eba",
        _canonical("Second Battle of Casteldelfino (Pietralunga)", 1744),
        "war_of_austrian_succession",
        ["kingdom_france"],
        ["kingdom_sardinia_piedmont"],
        ["post_wave8_museo_alpini_part1"],
        ["post_wave8_museo_alpini_part1"],
        ["museo_nazionale_storico_alpini"],
        (
            "The second Casteldelfino action at Pietralunga is distinguished from "
            "the earlier action and retains the directly attested French victory."
        ),
        war_type="interstate_limited",
    ),
    "hced-La Maddalena1793-1": _contract(
        "6b8f259508b92255e41e98937862eb22b23777a16a02120999fd63a252da7afd",
        _canonical("Defense of La Maddalena", 1793),
        "french_revolutionary_wars",
        ["kingdom_sardinia_piedmont"],
        ["french_first_republic"],
        ["post_wave8_italian_navy_la_maddalena_1793"],
        ["post_wave8_italian_navy_la_maddalena_1793"],
        ["italian_navy_history"],
        (
            "The Italian Navy history confirms Sardinia's defense against the "
            "French Republic. The raw modern-country value France is quarantined "
            "because the engagement occurred at La Maddalena in present-day Italy."
        ),
        war_type="interstate_limited",
    ),
    "hced-Madonna del Olmo1744-1": _contract(
        "086640ec185608b30288f1f553daf831d0f2dda0157a8e5ba9a65ba3744b9207",
        _canonical("Battle of Madonna dell'Olmo", 1744),
        "war_of_austrian_succession",
        ["kingdom_france", "spanish_empire"],
        ["kingdom_sardinia_piedmont"],
        ["post_wave8_museo_alpini_part1"],
        ["post_wave8_museo_alpini_part1"],
        ["museo_nazionale_storico_alpini"],
        (
            "The institutional account confirms the Franco-Spanish battlefield "
            "victory over Sardinia and the canonical Italian event name."
        ),
        war_type="interstate_limited",
    ),
    "hced-Vicenza1848-1": _contract(
        "915c27a7bbed953358ae4320dcea0cdc37a2e530af4a11e980f41a70c8cacf21",
        _canonical("Battle of Vicenza", 1848),
        "first_italian_war_of_independence",
        ["austrian_empire"],
        ["durando_vicenza_defense_force_1848"],
        ["post_wave8_vicenza_museum_1848"],
        ["post_wave8_vicenza_museum_1848"],
        ["musei_civici_vicenza"],
        (
            "The museum guide confirms the Austrian victory, but identifies the "
            "defenders as Durando's Papal-service and volunteer force rather than "
            "Sardinia. The matching IWBD row is held as a duplicate."
        ),
        war_type="interstate_limited",
    ),
    "hced-Belgrade1807-1": _contract(
        "448df7bbbc18f190656bba681f9a415c4f77c4587e7c22277e2323f9b3486073",
        _canonical("Capture of Belgrade Fortress", 1807, granularity="siege"),
        "first_serbian_uprising",
        ["serbian_revolutionary_forces_1804_1815"],
        ["ottoman_empire"],
        ["post_wave8_belgrade_fortress_1807"],
        ["post_wave8_belgrade_fortress_1807"],
        ["city_of_belgrade"],
        (
            "The municipal fortress history distinguishes the town's late-1806 "
            "capture from the fortress capture at the beginning of 1807. This "
            "contract rates only the staged 1807 fortress result."
        ),
        war_type="interstate_limited",
    ),
    "hced-Deligrad1806-1": _contract(
        "f90ea4ba6450a161cdb1572b156bc837431f948dfe87ea001709ea93aae3f5f8",
        _canonical("Battle of Deligrad", 1806),
        "first_serbian_uprising",
        ["serbian_revolutionary_forces_1804_1815"],
        ["ottoman_empire"],
        ["post_wave8_serbia_mod_deligrad_1806"],
        ["post_wave8_serbia_mod_deligrad_1806"],
        ["serbian_ministry_of_defence"],
        (
            "The Serbian Ministry of Defence chronology directly confirms the "
            "1806 Serbian defense and defeat of the Ottoman force."
        ),
        war_type="interstate_limited",
    ),
    "hced-Ivanovatz1805-1": _contract(
        "1a05909bcc998bd4b3d0ca96e5dc961eeadb185b05858e8e1d87e4bb5c722e4e",
        _canonical("Battle of Ivankovac", 1805),
        "first_serbian_uprising",
        ["serbian_revolutionary_forces_1804_1815"],
        ["ottoman_empire"],
        ["post_wave8_serbia_mod_ivankovac_1805"],
        ["post_wave8_serbia_mod_ivankovac_1805"],
        ["serbian_ministry_of_defence"],
        (
            "The Serbian Ministry of Defence confirms the first major Serbian "
            "victory over Ottoman imperial troops; the canonical spelling is "
            "Ivankovac rather than the HCED transliteration Ivanovatz."
        ),
        war_type="interstate_limited",
    ),
    "hced-Nish1809-1": _contract(
        "bc49237be4194ceed7e5c4854232970925c1bf1259588c42afb50868b7d196ae",
        _canonical("Battle of Čegar", 1809),
        "first_serbian_uprising",
        ["ottoman_empire"],
        ["serbian_revolutionary_forces_1804_1815"],
        ["post_wave8_serbia_mod_cegar_1809"],
        ["post_wave8_serbia_mod_cegar_1809"],
        ["serbian_ministry_of_defence"],
        (
            "The Ministry of Defence account identifies the 1809 event near Niš "
            "as the Battle of Čegar and confirms the Serbian defeat. The staged "
            "point for central Niš is quarantined."
        ),
        war_type="interstate_limited",
    ),
}


# The audit found no HCED holds among the 17 selected rows.
WAVE8_FAST17_HOLDS: dict[str, dict[str, Any]] = {}

WAVE8_FAST17_CONTRACT_IDS = frozenset(WAVE8_FAST17_CONTRACTS)
WAVE8_FAST17_HOLD_IDS = frozenset(WAVE8_FAST17_HOLDS)
WAVE8_FAST17_RESERVED_IDS = WAVE8_FAST17_CONTRACT_IDS | WAVE8_FAST17_HOLD_IDS

# These are integration contracts only. This lane deliberately does not mutate
# the shared location manifests; the orchestrator may union these additions in a
# separate, coordinated change.
WAVE8_FAST17_POINT_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Groenkloof1901-1",
        "hced-Nish1809-1",
        "hced-Vaal Kranz1900-1",
    }
)
WAVE8_FAST17_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {"hced-La Maddalena1793-1"}
)

# The IWBD row describes the same 11 June 1848 Vicenza action and also repeats
# the incorrect Sardinia defender label corrected by the HCED exact contract.
WAVE8_FAST17_IWBD_DUPLICATE_HOLDS: dict[str, dict[str, str]] = {
    "iwbd-10-4-40": {
        "duplicate_of_hced_candidate_id": "hced-Vicenza1848-1",
        "hold_category": "duplicate_of_exact_hced_event",
        "hold_reason": (
            "Same Battle of Vicenza on 11 June 1848; the IWBD defender label "
            "Sardinia is also contradicted by the reviewed municipal-museum source."
        ),
    }
}
WAVE8_FAST17_IWBD_DUPLICATE_HOLD_IDS = frozenset(
    WAVE8_FAST17_IWBD_DUPLICATE_HOLDS
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_FAST17_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_FAST17_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_FAST17_ENTITIES,
        "holds": WAVE8_FAST17_HOLDS,
        "iwbd_duplicate_holds": WAVE8_FAST17_IWBD_DUPLICATE_HOLDS,
        "point_quarantine_additions": sorted(
            WAVE8_FAST17_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_FAST17_SOURCES,
    }


def wave8_fast17_signature() -> str:
    return hashlib.sha256(_canonical_json(_signature_payload()).encode()).hexdigest()


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(values)
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_FAST17_CONTRACTS), len(WAVE8_FAST17_HOLDS)) != (17, 0):
        raise ValueError("Wave 8 fast-17 disposition inventory changed")
    if (len(WAVE8_FAST17_ENTITIES), len(WAVE8_FAST17_SOURCES)) != (2, 15):
        raise ValueError("Wave 8 fast-17 fixture inventory changed")
    if wave8_fast17_signature() != WAVE8_FAST17_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 fast-17 final audit signature changed")
    if WAVE8_FAST17_CONTRACT_IDS & WAVE8_FAST17_HOLD_IDS:
        raise ValueError("Wave 8 fast-17 promotions and holds overlap")

    source_by_id = {str(source["id"]): source for source in WAVE8_FAST17_SOURCES}
    if len(source_by_id) != len(WAVE8_FAST17_SOURCES):
        raise ValueError("Wave 8 fast-17 source IDs are not unique")
    for source in WAVE8_FAST17_SOURCES:
        roles = list(map(str, source["evidence_roles"]))
        if not _is_sorted_unique(roles):
            raise ValueError("Wave 8 fast-17 source roles are not canonical")

    entity_ids = {str(entity["id"]) for entity in WAVE8_FAST17_ENTITIES}
    if len(entity_ids) != len(WAVE8_FAST17_ENTITIES):
        raise ValueError("Wave 8 fast-17 entity IDs are not unique")
    for entity in WAVE8_FAST17_ENTITIES:
        if entity["start_year"] != entity["end_year"]:
            raise ValueError("Wave 8 fast-17 entities must be event-bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError("Wave 8 fast-17 entities must be alias-free")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError("Wave 8 fast-17 entity permits rating inheritance")
        source_ids = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(source_ids) or not set(source_ids) <= set(source_by_id):
            raise ValueError("Wave 8 fast-17 entity provenance is not canonical")

    used_new_entities: set[str] = set()
    for candidate_id, contract in WAVE8_FAST17_CONTRACTS.items():
        row_hash = str(contract["raw_row_sha256"])
        if len(row_hash) != 64 or any(char not in "0123456789abcdef" for char in row_hash):
            raise ValueError(f"Wave 8 fast-17 invalid queue hash for {candidate_id}")
        if contract.get("source_outcome_override") is not False:
            raise ValueError(f"Wave 8 fast-17 outcome reversal for {candidate_id}")
        if contract.get("result_type", "win") != "win" or contract["winner_side"] != 1:
            raise ValueError(f"Wave 8 fast-17 non-direct win for {candidate_id}")

        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"Wave 8 fast-17 canonical key drift for {candidate_id}")

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"Wave 8 fast-17 source provenance drift for {candidate_id}")
        if not _is_sorted_unique(families):
            raise ValueError(f"Wave 8 fast-17 family provenance drift for {candidate_id}")
        if not outcomes or not set(outcomes) <= set(evidence) <= set(source_by_id):
            raise ValueError(f"Wave 8 fast-17 direct source gap for {candidate_id}")
        if any("outcome" not in source_by_id[source_id]["evidence_roles"] for source_id in outcomes):
            raise ValueError(f"Wave 8 fast-17 non-outcome source for {candidate_id}")
        expected_families = sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"Wave 8 fast-17 outcome family drift for {candidate_id}")

        used_new_entities.update(
            (set(contract["side_1_entity_ids"]) | set(contract["side_2_entity_ids"]))
            & entity_ids
        )
    if used_new_entities != entity_ids:
        raise ValueError("Wave 8 fast-17 new entities are not exactly consumed")

    if WAVE8_FAST17_POINT_QUARANTINE_ADDITIONS != {
        "hced-Groenkloof1901-1",
        "hced-Nish1809-1",
        "hced-Vaal Kranz1900-1",
    }:
        raise ValueError("Wave 8 fast-17 point quarantine contract changed")
    if WAVE8_FAST17_COUNTRY_QUARANTINE_ADDITIONS != {
        "hced-La Maddalena1793-1"
    }:
        raise ValueError("Wave 8 fast-17 country quarantine contract changed")
    if set(WAVE8_FAST17_IWBD_DUPLICATE_HOLDS) != {"iwbd-10-4-40"}:
        raise ValueError("Wave 8 fast-17 IWBD duplicate inventory changed")
    duplicate_target = WAVE8_FAST17_IWBD_DUPLICATE_HOLDS["iwbd-10-4-40"][
        "duplicate_of_hced_candidate_id"
    ]
    if duplicate_target != "hced-Vicenza1848-1" or duplicate_target not in WAVE8_FAST17_CONTRACTS:
        raise ValueError("Wave 8 fast-17 IWBD duplicate target changed")


def validate_wave8_fast17_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_FAST17_CONTRACTS,
        WAVE8_FAST17_HOLDS,
        lane_name=_LANE_NAME,
    )


def install_wave8_fast17_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_FAST17_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_fast17_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_FAST17_SOURCES,
        lane_name=_LANE_NAME,
    )


def promote_wave8_fast17_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_fast17_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_FAST17_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )


def wave8_fast17_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_FAST17_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "holds": len(WAVE8_FAST17_HOLDS),
        "iwbd_duplicate_holds": len(WAVE8_FAST17_IWBD_DUPLICATE_HOLDS),
        "new_entities": len(WAVE8_FAST17_ENTITIES),
        "new_sources": len(WAVE8_FAST17_SOURCES),
        "newly_rated_events": len(WAVE8_FAST17_CONTRACTS),
        "point_quarantine_additions": len(WAVE8_FAST17_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_FAST17_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_FAST17_RESERVED_IDS),
    }


def wave8_fast17_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(Counter(str(item["cohort"]) for item in WAVE8_FAST17_CONTRACTS.values()).items())
    )


def wave8_fast17_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_FAST17_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_FAST17_POINT_QUARANTINE_ADDITIONS,
    }
