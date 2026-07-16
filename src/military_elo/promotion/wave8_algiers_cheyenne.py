"""Exact Wave 8 contracts for the audited Algiers and Cheyenne cohorts.

The source labels ``Algiers`` and ``Cheyenne Indians`` are never installed as
aliases.  Every promotion is tied to one locked HCED row and to an explicitly
bounded state, formation, band, camp force, or coalition.
"""

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


__all__ = (
    "WAVE8_ALGIERS_CHEYENNE_CONTRACTS",
    "WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS",
    "WAVE8_ALGIERS_CHEYENNE_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ALGIERS_CHEYENNE_ENTITIES",
    "WAVE8_ALGIERS_CHEYENNE_EXCLUSIONS",
    "WAVE8_ALGIERS_CHEYENNE_EXCLUSION_IDS",
    "WAVE8_ALGIERS_CHEYENNE_EXPECTED_CANDIDATE_IDS",
    "WAVE8_ALGIERS_CHEYENNE_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ALGIERS_CHEYENNE_HOLDS",
    "WAVE8_ALGIERS_CHEYENNE_HOLD_IDS",
    "WAVE8_ALGIERS_CHEYENNE_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_ALGIERS_CHEYENNE_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_ALGIERS_CHEYENNE_NONPROMOTIONS",
    "WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDE_METADATA",
    "WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDES",
    "WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS",
    "WAVE8_ALGIERS_CHEYENNE_SOURCES",
    "WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS",
    "WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS",
    "install_wave8_algiers_cheyenne_entities",
    "install_wave8_algiers_cheyenne_sources",
    "promote_wave8_algiers_cheyenne_contracts",
    "validate_wave8_algiers_cheyenne_queue_contracts",
    "wave8_algiers_cheyenne_audit_signature",
    "wave8_algiers_cheyenne_cohort_counts",
    "wave8_algiers_cheyenne_counts",
)


_LANE_NAME = "Wave 8 Algiers and Cheyenne exact audit"
_EVENT_ID_PREFIX = "hced_wave8_algiers_cheyenne_"

# Filled from the canonical JSON payload below.  Changing any audited row,
# fixture, disposition, quarantine, or duplicate decision changes this value.
WAVE8_ALGIERS_CHEYENNE_FINAL_AUDIT_SIGNATURE = (
    "8b83b457b6d4cdb76868054364c08af68a391b545e45951e086c99131a1aa12b"
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
    government_work: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "U.S. Government work" if government_work else "linked_reference",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_ALGIERS_CHEYENNE_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_cambridge_algeria_dey_regency",
        "Ecologies, Societies, Cultures and the State, 1516–1830",
        "https://www.cambridge.org/core/books/history-of-algeria/ecologies-societies-cultures-and-the-state-15161830/6C59DEAD9F70913EC060EDD1465FA6A5",
        "Cambridge University Press",
        "academic_book_chapter",
        "cambridge_history_algeria",
    ),
    _source(
        "wave8_rmg_bugia_bay_1671",
        "Action at Bugia Bay, 8 May 1671",
        "https://www.rmg.co.uk/collections/objects/rmgc-object-141785",
        "Royal Museums Greenwich",
        "museum_collection_record",
        "royal_museums_greenwich",
        outcome=True,
    ),
    _source(
        "wave8_louvre_algiers_1688",
        "Le bombardement d'Alger par le maréchal d'Estrées, 1er juillet 1688",
        "https://arts-graphiques.louvre.fr/detail/oeuvres/0/536169-Le-bombardement-dAlger-par-le-marechal-dEstrees-le-1er-juillet-1688",
        "Musée du Louvre",
        "museum_collection_record",
        "musee_du_louvre",
    ),
    _source(
        "wave8_pur_algiers_bombardments_1688",
        "Les bombardements d'Alger de 1682, 1683 et 1688",
        "https://books.openedition.org/pur/129300?lang=fr",
        "Presses universitaires de Rennes",
        "academic_book_chapter",
        "presses_universitaires_rennes",
    ),
    _source(
        "wave8_rah_algiers_landing_1775",
        "Desembarco español en Argel (8 July 1775)",
        "https://historia-hispanica.rah.es/hechos/1386877-1775-8-vii",
        "Real Academia de la Historia",
        "scholarly_chronology",
        "real_academia_historia_spain",
        outcome=True,
    ),
    _source(
        "wave8_boe_algiers_expedition_1775",
        "Historical account of the expedition against Algiers in 1775",
        "https://www.boe.es/gazeta/dias/1857/11/29/pdfs/GMD-1857-1790.pdf",
        "Gaceta de Madrid / Boletín Oficial del Estado",
        "government_historical_periodical",
        "boe_gaceta_madrid",
        outcome=True,
    ),
    _source(
        "wave8_armada_algiers_expedition_1775",
        "La expedición española contra Argel de 1775",
        "https://armada.defensa.gob.es/archivo/mardigitalrevistas/rhn/2018/2018n142.pdf",
        "Spanish Navy",
        "official_naval_history_journal",
        "spanish_navy_history",
        outcome=True,
    ),
    _source(
        "wave8_treccani_acton_algiers_1775",
        "John Francis Edward Acton",
        "https://www.treccani.it/enciclopedia/john-francis-edward-acton_%28Dizionario-Biografico%29/",
        "Treccani",
        "scholarly_encyclopedia",
        "treccani",
    ),
    _source(
        "wave8_armada_algiers_bombardment_1783",
        "El bombardeo de Argel de 1783",
        "https://armada.defensa.gob.es/archivo/mardigitalrevistas/cuadernosihcn/88cuaderno/Cuaderno88Cap03.pdf",
        "Spanish Navy",
        "official_naval_history",
        "spanish_navy_history",
    ),
    _source(
        "wave8_gilder_algiers_attack_orders_1824",
        "British orders concerning the 1824 expedition to Algiers",
        "https://www.gilderlehrman.org/collection/glc07895",
        "Gilder Lehrman Institute of American History",
        "digitized_primary_document",
        "gilder_lehrman",
    ),
    _source(
        "wave8_cambridge_menacing_tides_algiers_1824",
        "To Give Law to the World",
        "https://www.cambridge.org/core/books/menacing-tides/to-give-law-to-the-world/FC7703CC1A5129829598EDC7C1025BA2",
        "Cambridge University Press",
        "academic_book_chapter",
        "cambridge_menacing_tides",
    ),
    _source(
        "wave8_nhhc_mashouda_1815",
        "Capture of the Algerine frigate Mashouda, 17 June 1815",
        "https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/ships-us/ships-usn-c/uss-constellation-frigate-1797-1853/kn-3489.html",
        "Naval History and Heritage Command",
        "government_museum_record",
        "us_naval_history_heritage_command",
        outcome=True,
        government_work=True,
    ),
    _source(
        "wave8_nhhc_macedonian_1815",
        "Macedonian I",
        "https://www.history.navy.mil/research/histories/ship-histories/danfs/m/macedonian-i.html",
        "Naval History and Heritage Command",
        "official_ship_history",
        "us_naval_history_heritage_command",
        outcome=True,
        government_work=True,
    ),
    _source(
        "wave8_cambridge_yusuf_karamanli_1795",
        "Introduction: Tripoli and Yusuf Karamanli",
        "https://www.cambridge.org/core/journals/royal-historical-society-camden-fifth-series/article/introduction/711BCC84C67DDBD1C2CDCAEA59D8C04D",
        "Cambridge University Press / Royal Historical Society",
        "academic_critical_edition",
        "cambridge_camden_fifth_series",
    ),
    _source(
        "wave8_cambridge_yusuf_karamanli_1832",
        "Memoir of George Grey, 1809–1833",
        "https://www.cambridge.org/core/journals/royal-historical-society-camden-fifth-series/article/memoir-of-george-grey-18091833/A88A8E97EA795D967778D10F2473F570",
        "Cambridge University Press / Royal Historical Society",
        "academic_critical_edition",
        "cambridge_camden_fifth_series",
    ),
    _source(
        "wave8_nhhc_philadelphia_1803",
        "Capture of the Frigate USS Philadelphia",
        "https://www.history.navy.mil/research/library/online-reading-room/title-list-alphabetically/c/capture-of-the-frigate-uss-philadelphia.html",
        "Naval History and Heritage Command",
        "digitized_primary_documents",
        "us_naval_history_heritage_command",
        outcome=True,
        government_work=True,
    ),
    _source(
        "wave8_nps_sand_creek_timeline",
        "Sand Creek Massacre National Historic Site timeline",
        "https://www.nps.gov/sand/learn/timeline.htm",
        "National Park Service",
        "government_history",
        "us_national_park_service",
        outcome=True,
        government_work=True,
    ),
    _source(
        "wave8_wyohistory_dull_knife_1876",
        "The Dull Knife Fight of 1876",
        "https://www.wyohistory.org/encyclopedia/dull-knife-fight-1876-troops-attack-cheyenne-village-red-fork-powder-river",
        "Wyoming State Historical Society",
        "state_historical_society_history",
        "wyoming_state_historical_society",
        outcome=True,
    ),
    _source(
        "wave8_nps_dull_knife_nrhp",
        "Dull Knife Battlefield National Register nomination",
        "https://npgallery.nps.gov/NRHP/GetAsset/NRHP/79002609_text",
        "National Park Service",
        "national_register_nomination",
        "us_national_park_service",
        outcome=True,
        government_work=True,
    ),
    _source(
        "wave8_oupress_war_party_in_blue",
        "War Party in Blue: Pawnee Scouts in the U.S. Army",
        "https://www.oupress.com/9780806184418/war-party-in-blue/",
        "University of Oklahoma Press",
        "academic_monograph",
        "university_oklahoma_press",
        outcome=True,
    ),
    _source(
        "wave8_wyohistory_powder_1865",
        "The Battle of Bonepile Creek, 1865: The Sawyers Expedition",
        "https://www.wyohistory.org/encyclopedia/battle-bonepile-creek-1865-sawyers-expedition",
        "Wyoming State Historical Society",
        "state_historical_society_history",
        "wyoming_state_historical_society",
    ),
    _source(
        "wave8_kansas_shpo_sappa_1875",
        "Sappa Creek Battlefield National Register nomination",
        "https://khri.kansasgis.org/photos_docs/153-31_4.pdf",
        "Kansas State Historic Preservation Office / National Register",
        "national_register_nomination",
        "us_national_register_kansas",
        government_work=True,
    ),
    _source(
        "wave8_kshs_solomons_fork_1857",
        "The Kiowa and Comanche Campaign of 1860",
        "https://www.kansashistory.gov/p/the-kiowa-and-comanche-campaign-of-1860/13142",
        "Kansas Historical Society",
        "state_historical_society_journal",
        "kansas_historical_society",
        outcome=True,
    ),
    _source(
        "wave8_nps_black_kettle",
        "Black Kettle",
        "https://www.nps.gov/waba/learn/historyculture/black-kettle.htm",
        "National Park Service",
        "government_biography",
        "us_national_park_service",
        government_work=True,
    ),
    _source(
        "wave8_history_nebraska_warbonnet_1876",
        "Skirmish at Warbonnet Creek",
        "https://history.nebraska.gov/publications_section/skirmish-at-warbonnet-creek/",
        "Nebraska State Historical Society",
        "state_historical_society_history",
        "nebraska_state_historical_society",
        outcome=True,
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
    continuity_note: str,
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
        "continuity_note": continuity_note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_ALGIERS_CHEYENNE_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "dey_regency_of_algiers_1671_1830",
        "Dey-ruled Regency of Algiers (1671–1830)",
        "state",
        1671,
        1830,
        "North Africa",
        ["wave8_cambridge_algeria_dey_regency"],
        "The dey-ruled state is bounded from 1671 to the French conquest in 1830; it is neither the city of Algiers nor a timeless corsair label. No rating is inherited by colonial or modern Algeria.",
    ),
    _entity(
        "algerine_corsair_squadron_bugia_1671",
        "Algerine corsair squadron and Bugia garrison (1671)",
        "state_naval_garrison_force",
        1671,
        1671,
        "Mediterranean",
        ["wave8_rmg_bugia_bay_1671"],
        "Event-bounded Algerine squadron and Bugia garrison opposed in the 1671 action. No rating is inherited by the city, all corsairs, or another Algerine formation.",
    ),
    _entity(
        "tuscan_naval_contingent_algiers_1775",
        "Tuscan naval contingent at Algiers (1775)",
        "state_naval_force",
        1775,
        1775,
        "Mediterranean",
        [
            "wave8_armada_algiers_expedition_1775",
            "wave8_treccani_acton_algiers_1775",
        ],
        "Event-bounded Tuscan naval contingent serving with the Spanish expedition of 1775. No rating is inherited by Tuscany outside this expedition or by a later Italian state.",
    ),
    _entity(
        "yusuf_karamanli_regency_of_tripoli_1795_1832",
        "Yusuf Karamanli's Regency of Tripoli (1795–1832)",
        "state",
        1795,
        1832,
        "North Africa",
        [
            "wave8_cambridge_yusuf_karamanli_1795",
            "wave8_cambridge_yusuf_karamanli_1832",
        ],
        "The state identity is bounded to Yusuf Karamanli's rule and corrects HCED's Algiers label for the 1803 Tripoli action. No rating is inherited by the city, Ottoman Tripolitan formations outside the window, or modern Libya.",
    ),
    _entity(
        "mackenzie_scout_coalition_red_fork_1876",
        "Mackenzie's scout coalition at Red Fork (1876)",
        "indigenous_auxiliary_coalition",
        1876,
        1876,
        "North America",
        ["wave8_nps_dull_knife_nrhp", "wave8_wyohistory_dull_knife_1876"],
        "Event-bounded Indigenous scout coalition serving Mackenzie's column at Red Fork. No rating is inherited by any member people, later scout unit, or modern tribal government.",
    ),
    _entity(
        "red_fork_northern_cheyenne_camp_defenders_1876",
        "Northern Cheyenne camp defenders at Red Fork (1876)",
        "indigenous_camp_force",
        1876,
        1876,
        "North America",
        ["wave8_nps_dull_knife_nrhp", "wave8_wyohistory_dull_knife_1876"],
        "Event-bounded defenders of the Northern Cheyenne camp at Red Fork. No rating is inherited by Cheyenne ethnicity, another band, or a modern tribal government.",
    ),
    _entity(
        "davis_murie_pawnee_scout_detachments_plum_creek_1867",
        "Davis and Murie Pawnee scout detachments at Plum Creek (1867)",
        "indigenous_auxiliary_force",
        1867,
        1867,
        "North America",
        ["wave8_oupress_war_party_in_blue"],
        "Event-bounded Pawnee scout detachments led by Davis and Murie in the Plum Creek fight. No rating is inherited by the Pawnee people, another scout formation, or a modern tribal government.",
    ),
    _entity(
        "turkey_leg_northern_cheyenne_band_plum_creek_1867",
        "Turkey Leg's Northern Cheyenne band at Plum Creek (1867)",
        "indigenous_war_band",
        1867,
        1867,
        "North America",
        ["wave8_oupress_war_party_in_blue"],
        "Event-bounded Northern Cheyenne band under Turkey Leg in the Plum Creek fight. No rating is inherited by Cheyenne ethnicity, another band, or a modern tribal government.",
    ),
    _entity(
        "sumner_cheyenne_field_force_solomons_fork_1857",
        "Cheyenne field force opposed by Sumner at Solomon's Fork (1857)",
        "indigenous_field_force",
        1857,
        1857,
        "North America",
        ["wave8_kshs_solomons_fork_1857", "wave8_nps_sand_creek_timeline"],
        "Event-bounded Cheyenne field force in Sumner's 1857 Solomon's Fork action. No rating is inherited by Cheyenne ethnicity, another band, or a modern tribal government.",
    ),
    _entity(
        "red_cloud_agency_cheyenne_war_party_warbonnet_1876",
        "Red Cloud Agency Cheyenne war party at Warbonnet Creek (1876)",
        "indigenous_war_party",
        1876,
        1876,
        "North America",
        ["wave8_history_nebraska_warbonnet_1876", "wave8_nps_black_kettle"],
        "Event-bounded Cheyenne war party from the Red Cloud Agency at Warbonnet Creek. No rating is inherited by Cheyenne ethnicity, another war party, or a modern tribal government.",
    ),
)


def _canonical(name: str, year: int) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "year",
        "granularity": "engagement",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


_ROW_DATA: dict[str, tuple[str, str, int]] = {
    "hced-Bougie1671-1": (
        "5d0cfaaa5a2b0ec5248940c6646f7c8d01f755aa2f36c4358318621c340ce28e",
        "Action at Bugia Bay",
        1671,
    ),
    "hced-Algiers1688-1": (
        "1a297c79891c7464e6b6d6517460c4a28f147c0bcf442695a9d5ce41f2402b22",
        "Bombardment of Algiers",
        1688,
    ),
    "hced-Algiers1775-1": (
        "dd7ea93453a58cccaceebe47dbf37945d252ddce9fb0c9f45dbc06ec54d9f00f",
        "Spanish Landing at Algiers",
        1775,
    ),
    "hced-Algiers1783-1": (
        "5ed467957ba6db9d8305d7014d916391c7c530bf4dae7356b2126e85ed9cd017",
        "Bombardment of Algiers",
        1783,
    ),
    "hced-Tripoli, Libya1803-1": (
        "f36b1a46c7802e4367a77209619de823a7c9873e4fd72468d9e12f1d0d40050e",
        "Capture of USS Philadelphia",
        1803,
    ),
    "hced-Cabo de Gata1815-1": (
        "8c8dde8f45461125377a4ca4ef1b3f1e208b5fd71b619aebfd958c020e906332",
        "Capture of Mashouda off Cape Gata",
        1815,
    ),
    "hced-Algiers1824-1": (
        "a1fa47e450c07dbac57d041d7f2081b8d879a92d7da485ffe741ab3533351800",
        "British Attack on Algiers",
        1824,
    ),
    "hced-Solomon Forks1857-1": (
        "e96107900b07d81263b30c38a7d6370e931d3dd05216d55e233456da84abdebc",
        "Battle of Solomon's Fork",
        1857,
    ),
    "hced-Ash Creek1864-1": (
        "2a706c4dce2542b5feefdb936f8dab26dcdcf18332cd9b283ce678d963805c5e",
        "Attack on Lean Bear's Village",
        1864,
    ),
    "hced-Powder1865-1": (
        "550c63cb09262c4751beedc76402ad14a15f4c6b0a5f75f93ec87f21d37bf89c",
        "Powder River Village Attack",
        1865,
    ),
    "hced-Plum Creek, Nebraska1867-1": (
        "16e99b4dbd67197e243303c01c937f9c78b7d8d1c1380c2263ab705b61ffc9fa",
        "Plum Creek Fight",
        1867,
    ),
    "hced-Sappa Creek1875-1": (
        "0be149e65e633b40df14e940665d4660ae9aa671e7692616ec4d603bba0660af",
        "Sappa Creek Massacre",
        1875,
    ),
    "hced-Crazy Woman Creek1876-1": (
        "3abe584ad98753a7e063b5b958802536ad083f70befd54bf036ca8eb838199d9",
        "Dull Knife Fight at Red Fork",
        1876,
    ),
    "hced-War Bonnet Creek1876-1": (
        "e896a5108845e40c8e290cbc485e8c7c17f95129ed259649923ba0b6becb634b",
        "Skirmish at Warbonnet Creek",
        1876,
    ),
}


def _contract(
    candidate_id: str,
    cohort: str,
    side_1: Iterable[str],
    side_2: Iterable[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    outcome_source_family_ids: Iterable[str],
    audit_note: str,
    *,
    war_type: str,
) -> dict[str, Any]:
    row_hash, name, year = _ROW_DATA[candidate_id]
    return {
        "raw_row_sha256": row_hash,
        "canonical_event": _canonical(name, year),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "winner_side": winner_side,
        "result_type": "win",
        "war_type": war_type,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": sorted(set(map(str, outcome_source_ids))),
        "outcome_source_family_ids": sorted(
            set(map(str, outcome_source_family_ids))
        ),
        "actor_override": True,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "audit_note": audit_note,
    }


_ALGIERS = "dey_regency_of_algiers_1671_1830"

WAVE8_ALGIERS_CHEYENNE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Bougie1671-1": _contract(
        "hced-Bougie1671-1",
        "algiers",
        ["kingdom_england"],
        ["algerine_corsair_squadron_bugia_1671"],
        1,
        ["wave8_cambridge_algeria_dey_regency", "wave8_rmg_bugia_bay_1671"],
        ["wave8_rmg_bugia_bay_1671"],
        ["royal_museums_greenwich"],
        "The 8 May 1671 action is restricted to the English squadron against the Algerine ships and Bugia garrison; neither a city identity nor all corsairs are inferred.",
        war_type="interstate_limited",
    ),
    "hced-Algiers1775-1": _contract(
        "hced-Algiers1775-1",
        "algiers",
        [_ALGIERS],
        ["spanish_empire", "tuscan_naval_contingent_algiers_1775"],
        1,
        [
            "wave8_armada_algiers_expedition_1775",
            "wave8_boe_algiers_expedition_1775",
            "wave8_cambridge_algeria_dey_regency",
            "wave8_rah_algiers_landing_1775",
            "wave8_treccani_acton_algiers_1775",
        ],
        [
            "wave8_armada_algiers_expedition_1775",
            "wave8_boe_algiers_expedition_1775",
            "wave8_rah_algiers_landing_1775",
        ],
        [
            "boe_gaceta_madrid",
            "real_academia_historia_spain",
            "spanish_navy_history",
        ],
        "The contract rates the failed 8 July landing against the dey's Regency and preserves the attested Tuscan naval contribution on the Spanish side.",
        war_type="interstate_limited",
    ),
    "hced-Tripoli, Libya1803-1": _contract(
        "hced-Tripoli, Libya1803-1",
        "algiers",
        ["yusuf_karamanli_regency_of_tripoli_1795_1832"],
        ["united_states"],
        1,
        [
            "wave8_cambridge_yusuf_karamanli_1795",
            "wave8_cambridge_yusuf_karamanli_1832",
            "wave8_nhhc_philadelphia_1803",
        ],
        ["wave8_nhhc_philadelphia_1803"],
        ["us_naval_history_heritage_command"],
        "HCED's Algiers label is corrected to Yusuf Karamanli's Tripoli for the 31 October 1803 capture of USS Philadelphia; the tactical orientation is unchanged.",
        war_type="interstate_limited",
    ),
    "hced-Cabo de Gata1815-1": _contract(
        "hced-Cabo de Gata1815-1",
        "algiers",
        ["united_states"],
        [_ALGIERS],
        1,
        [
            "wave8_cambridge_algeria_dey_regency",
            "wave8_nhhc_macedonian_1815",
            "wave8_nhhc_mashouda_1815",
        ],
        ["wave8_nhhc_macedonian_1815", "wave8_nhhc_mashouda_1815"],
        ["us_naval_history_heritage_command"],
        "The contract rates only Decatur's 17 June 1815 capture of Mashouda off Cape Gata, not the strategic result of the Second Barbary War.",
        war_type="interstate_limited",
    ),
    "hced-Crazy Woman Creek1876-1": _contract(
        "hced-Crazy Woman Creek1876-1",
        "cheyenne_indians",
        ["united_states", "mackenzie_scout_coalition_red_fork_1876"],
        ["red_fork_northern_cheyenne_camp_defenders_1876"],
        1,
        ["wave8_nps_dull_knife_nrhp", "wave8_wyohistory_dull_knife_1876"],
        ["wave8_nps_dull_knife_nrhp", "wave8_wyohistory_dull_knife_1876"],
        ["us_national_park_service", "wyoming_state_historical_society"],
        "The row is the 25 November Dull Knife Fight at Red Fork, not Crazy Woman Creek. Mackenzie's Indigenous scouts and the exact Northern Cheyenne camp defenders are represented separately.",
        war_type="colonial_anti_colonial",
    ),
    "hced-Plum Creek, Nebraska1867-1": _contract(
        "hced-Plum Creek, Nebraska1867-1",
        "cheyenne_indians",
        ["united_states", "davis_murie_pawnee_scout_detachments_plum_creek_1867"],
        ["turkey_leg_northern_cheyenne_band_plum_creek_1867"],
        1,
        ["wave8_oupress_war_party_in_blue"],
        ["wave8_oupress_war_party_in_blue"],
        ["university_oklahoma_press"],
        "The contract isolates the 1867 Plum Creek fight and names the Davis-Murie Pawnee scout detachments and Turkey Leg's Northern Cheyenne band; no timeless people-level actor is created.",
        war_type="colonial_anti_colonial",
    ),
    "hced-Solomon Forks1857-1": _contract(
        "hced-Solomon Forks1857-1",
        "cheyenne_indians",
        ["united_states"],
        ["sumner_cheyenne_field_force_solomons_fork_1857"],
        1,
        ["wave8_kshs_solomons_fork_1857", "wave8_nps_sand_creek_timeline"],
        ["wave8_kshs_solomons_fork_1857", "wave8_nps_sand_creek_timeline"],
        ["kansas_historical_society", "us_national_park_service"],
        "The contract rates Sumner's discrete 29 July 1857 Solomon's Fork engagement against the event-bounded Cheyenne field force, not a generic Cheyenne identity.",
        war_type="colonial_anti_colonial",
    ),
    "hced-War Bonnet Creek1876-1": _contract(
        "hced-War Bonnet Creek1876-1",
        "cheyenne_indians",
        ["united_states"],
        ["red_cloud_agency_cheyenne_war_party_warbonnet_1876"],
        1,
        ["wave8_history_nebraska_warbonnet_1876", "wave8_nps_black_kettle"],
        ["wave8_history_nebraska_warbonnet_1876"],
        ["nebraska_state_historical_society"],
        "The contract is limited to the 17 July 1876 Warbonnet Creek skirmish against the identified Red Cloud Agency Cheyenne war party.",
        war_type="colonial_anti_colonial",
    ),
}


def _hold(
    candidate_id: str,
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    *,
    reviewed_sides: Iterable[str],
) -> dict[str, Any]:
    row_hash, name, year = _ROW_DATA[candidate_id]
    return {
        "raw_row_sha256": row_hash,
        "canonical_event": _canonical(name, year),
        "disposition": "hold",
        "hold_category": category,
        "reviewed_actor_entity_ids": list(map(str, reviewed_sides)),
        "reviewed_granularity": "engagement",
        "hold_reason": reason,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
    }


WAVE8_ALGIERS_CHEYENNE_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Algiers1688-1": _hold(
        "hced-Algiers1688-1",
        "tactical_outcome_not_directly_adjudicated",
        "The sources verify the 1688 French bombardment and the opposing dey-ruled Regency, but do not support converting survival, damage, or withdrawal into a mechanically defensible tactical victor.",
        [
            "wave8_cambridge_algeria_dey_regency",
            "wave8_louvre_algiers_1688",
            "wave8_pur_algiers_bombardments_1688",
        ],
        reviewed_sides=[_ALGIERS, "kingdom_france"],
    ),
    "hced-Algiers1783-1": _hold(
        "hced-Algiers1783-1",
        "tactical_outcome_not_directly_adjudicated",
        "The source confirms Barceló's 1783 bombardment against the Regency, but the available evidence does not adjudicate the engagement as the categorical Algerine win asserted by HCED.",
        ["wave8_armada_algiers_bombardment_1783", "wave8_cambridge_algeria_dey_regency"],
        reviewed_sides=[_ALGIERS, "spanish_empire"],
    ),
    "hced-Algiers1824-1": _hold(
        "hced-Algiers1824-1",
        "event_boundary_and_outcome_unresolved",
        "The reviewed sources attest British coercive operations against Algiers in 1824, but the locked row does not delimit one competitive engagement whose tactical result can be rated without invention.",
        [
            "wave8_cambridge_algeria_dey_regency",
            "wave8_cambridge_menacing_tides_algiers_1824",
            "wave8_gilder_algiers_attack_orders_1824",
        ],
        reviewed_sides=["united_kingdom", _ALGIERS],
    ),
}


def _terminal_exclusion(
    candidate_id: str,
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    *,
    reviewed_actors: Iterable[str],
) -> dict[str, Any]:
    row_hash, name, year = _ROW_DATA[candidate_id]
    return {
        "raw_row_sha256": row_hash,
        "canonical_event": _canonical(name, year),
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "hold_category": category,
        "reviewed_actor_description": list(map(str, reviewed_actors)),
        "reviewed_granularity": "non_ratable_attack",
        "hold_reason": reason,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
    }


WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Ash Creek1864-1": _terminal_exclusion(
        "hced-Ash Creek1864-1",
        "noncompetitive_attack_on_peace_village",
        "The reviewed episode was an attack on Lean Bear's peace village/delegation context rather than an opposing-force engagement. Civilian vulnerability is not converted into a Cheyenne tactical defeat.",
        ["wave8_nps_black_kettle", "wave8_nps_sand_creek_timeline"],
        reviewed_actors=["United States troops", "Lean Bear's Cheyenne peace village"],
    ),
    "hced-Powder1865-1": _terminal_exclusion(
        "hced-Powder1865-1",
        "village_attack_without_competitive_outcome",
        "The row conflates a Powder River/Sawyers-expedition village-attack setting with a generic Cheyenne loser. The evidence does not establish the exact competitive sides and result required for Elo.",
        ["wave8_oupress_war_party_in_blue", "wave8_wyohistory_powder_1865"],
        reviewed_actors=["United States expeditionary force and scouts", "Indigenous village or camp force"],
    ),
    "hced-Sappa Creek1875-1": _terminal_exclusion(
        "hced-Sappa Creek1875-1",
        "massacre_with_civilian_camp",
        "The National Register evidence classifies Sappa Creek as a massacre involving a Cheyenne camp with civilians, not a clean competitive engagement. It is permanently excluded from Elo.",
        ["wave8_kansas_shpo_sappa_1875", "wave8_nps_sand_creek_timeline"],
        reviewed_actors=["United States troops and scouts", "Cheyenne camp including civilians"],
    ),
}

# Compatibility alias for consumers that use the shorter exclusion name.
WAVE8_ALGIERS_CHEYENNE_EXCLUSIONS = (
    WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS
)
WAVE8_ALGIERS_CHEYENNE_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_ALGIERS_CHEYENNE_HOLDS,
    **WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS,
}

WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS = frozenset(
    WAVE8_ALGIERS_CHEYENNE_CONTRACTS
)
WAVE8_ALGIERS_CHEYENNE_HOLD_IDS = frozenset(WAVE8_ALGIERS_CHEYENNE_HOLDS)
WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS
)
WAVE8_ALGIERS_CHEYENNE_EXCLUSION_IDS = (
    WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS
)
WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS = (
    WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS
    | WAVE8_ALGIERS_CHEYENNE_HOLD_IDS
    | WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS
)
WAVE8_ALGIERS_CHEYENNE_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_DATA)

# The canonical events differ materially from these raw points.  The lane
# exports integration additions and also applies them to its own event output.
WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Crazy Woman Creek1876-1",
        "hced-Plum Creek, Nebraska1867-1",
        "hced-Solomon Forks1857-1",
    }
)
WAVE8_ALGIERS_CHEYENNE_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_ALGIERS_CHEYENNE_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_ALGIERS_CHEYENNE_COUNTRY_QUARANTINE_ADDITIONS,
}

# No IWBD row before 1900 matches any of the fourteen audited events.
WAVE8_ALGIERS_CHEYENNE_IWBD_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}

# Direct sources preserve the eight HCED outcome orientations.  The Tripoli
# row receives an actor correction (Algiers -> Tripoli), not an outcome change.
WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDE_METADATA = (
    WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDES
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_ALGIERS_CHEYENNE_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_ALGIERS_CHEYENNE_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_ALGIERS_CHEYENNE_ENTITIES,
        "holds": WAVE8_ALGIERS_CHEYENNE_HOLDS,
        "iwbd_duplicate_dispositions": (
            WAVE8_ALGIERS_CHEYENNE_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "outcome_overrides": WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_ALGIERS_CHEYENNE_SOURCES,
        "terminal_exclusions": WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS,
    }


def wave8_algiers_cheyenne_audit_signature() -> str:
    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_ALGIERS_CHEYENNE_CONTRACTS),
        len(WAVE8_ALGIERS_CHEYENNE_HOLDS),
        len(WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS),
    ) != (8, 3, 3):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (
        len(WAVE8_ALGIERS_CHEYENNE_ENTITIES),
        len(WAVE8_ALGIERS_CHEYENNE_SOURCES),
    ) != (10, 25):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS != (
        WAVE8_ALGIERS_CHEYENNE_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} reservations are incomplete")
    dispositions = (
        WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS,
        WAVE8_ALGIERS_CHEYENNE_HOLD_IDS,
        WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS,
    )
    if any(dispositions[i] & dispositions[j] for i in range(3) for j in range(i + 1, 3)):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if (
        wave8_algiers_cheyenne_audit_signature()
        != WAVE8_ALGIERS_CHEYENNE_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_ALGIERS_CHEYENNE_SOURCES
    }
    if len(source_by_id) != 25:
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_ALGIERS_CHEYENNE_SOURCES:
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_ALGIERS_CHEYENNE_ENTITIES
    }
    if len(entity_by_id) != 10:
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {"algiers", "cheyenne", "cheyenne indians"}
    for entity in WAVE8_ALGIERS_CHEYENNE_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if int(entity["start_year"]) > int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity has an invalid window")
        if str(entity["name"]).casefold() in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a timeless source label")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} identity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} identity names an unknown source")

    used_new_entities: set[str] = set()
    for candidate_id, contract in WAVE8_ALGIERS_CHEYENNE_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_DATA[candidate_id][0]:
            raise ValueError(f"{_LANE_NAME} promotion hash drifted")
        if (
            contract["result_type"] != "win"
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or contract["actor_override"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} outcome/actor policy drifted")
        evidence = list(map(str, contract["evidence_refs"]))
        outcome_sources = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcome_sources):
            raise ValueError(f"{_LANE_NAME} contract provenance is not canonical")
        if not outcome_sources or not set(outcome_sources) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} contract lacks direct outcome sources")
        if not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} contract names an unknown source")
        for source_id in outcome_sources:
            if "outcome" not in source_by_id[source_id]["evidence_roles"]:
                raise ValueError(f"{_LANE_NAME} outcome source lacks outcome role")
        expected_families = sorted(
            {
                str(source_by_id[source_id]["source_family_id"])
                for source_id in outcome_sources
            }
        )
        if contract["outcome_source_family_ids"] != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        for entity_id in (
            *map(str, contract["side_1_entity_ids"]),
            *map(str, contract["side_2_entity_ids"]),
        ):
            if entity_id in entity_by_id:
                used_new_entities.add(entity_id)
    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} has an unused bounded identity")

    for candidate_id, item in WAVE8_ALGIERS_CHEYENNE_NONPROMOTIONS.items():
        if item["raw_row_sha256"] != _ROW_DATA[candidate_id][0]:
            raise ValueError(f"{_LANE_NAME} nonpromotion hash drifted")
        if not set(map(str, item["evidence_refs"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} nonpromotion names an unknown source")
    if any(item["disposition"] != "hold" for item in WAVE8_ALGIERS_CHEYENNE_HOLDS.values()):
        raise ValueError(f"{_LANE_NAME} provisional hold disposition drifted")
    if any(
        item["disposition"] != "terminal_exclusion"
        or item["terminal_exclusion"] is not True
        for item in WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS.values()
    ):
        raise ValueError(f"{_LANE_NAME} terminal exclusion disposition drifted")

    if WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS != {
        "hced-Crazy Woman Creek1876-1",
        "hced-Plum Creek, Nebraska1867-1",
        "hced-Solomon Forks1857-1",
    }:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_ALGIERS_CHEYENNE_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unsupported country quarantine")
    if not WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS <= (
        WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} quarantines a nonpromotion")
    if WAVE8_ALGIERS_CHEYENNE_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited IWBD duplicate")
    if WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited outcome correction")


def validate_wave8_algiers_cheyenne_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ALGIERS_CHEYENNE_CONTRACTS,
        WAVE8_ALGIERS_CHEYENNE_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_ALGIERS_CHEYENNE_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(
            WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS
        ),
    }


def install_wave8_algiers_cheyenne_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ALGIERS_CHEYENNE_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_algiers_cheyenne_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_ALGIERS_CHEYENNE_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_ALGIERS_CHEYENNE_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_algiers_cheyenne_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_algiers_cheyenne_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ALGIERS_CHEYENNE_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_algiers_cheyenne_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_ALGIERS_CHEYENNE_CONTRACTS.values()
            ).items()
        )
    )


def wave8_algiers_cheyenne_counts() -> dict[str, int]:
    return {
        "holds": len(WAVE8_ALGIERS_CHEYENNE_HOLDS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_ALGIERS_CHEYENNE_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_ALGIERS_CHEYENNE_ENTITIES),
        "new_sources": len(WAVE8_ALGIERS_CHEYENNE_SOURCES),
        "newly_rated_events": len(WAVE8_ALGIERS_CHEYENNE_CONTRACTS),
        "outcome_overrides": len(WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDES),
        "promotion_contracts": len(WAVE8_ALGIERS_CHEYENNE_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS),
        "terminal_exclusions": len(
            WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS
        ),
    }
