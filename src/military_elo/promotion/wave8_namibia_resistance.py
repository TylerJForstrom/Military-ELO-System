"""Exact Wave 8 contracts for Nama and Ovaherero resistance in Namibia."""

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
    rows_by_candidate_id,
    validate_exact_hced_inventory,
)


WAVE8_NAMIBIA_RESISTANCE_FINAL_AUDIT_SIGNATURE = (
    "1ba7dad4d4c391a0ad121ea2443cc57dc1921df843a3e6618ed0f8fa07c76fea"
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


WAVE8_NAMIBIA_RESISTANCE_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "suub_gswa_campaign_history",
        "Official campaign history of German South West Africa",
        "https://brema.suub.uni-bremen.de/dsdk/content/structure/1843541",
        "Staats- und Universitätsbibliothek Bremen",
        "digitized_official_history",
        "suub_bremen_german_colonial_collection",
        outcome=True,
    ),
    _source(
        "cambridge_hidden_histories_morenga",
        "The Marengo rebellion and Riemvasmaak, 1903–1907",
        "https://www.cambridge.org/core/books/abs/hidden-histories-of-gordonia/marengo-rebellion-and-riemvasmaak-19031907/162DA49365B4942E564B3444FE4AC0EB",
        "Cambridge University Press",
        "academic_book_chapter",
        "cambridge_hidden_histories_gordonia",
        outcome=True,
    ),
    _source(
        "brill_morenga_resistance_chapter",
        "Jakob Morenga and resistance in southern Namibia",
        "https://brill.com/display/book/9789004712454/BP000015.pdf",
        "Brill",
        "academic_book_chapter",
        "brill_namibia_history",
        outcome=True,
    ),
    _source(
        "nga_hartebeestmund_gazetteer",
        "Hartebeestmund geographic-name record",
        "https://geographic.org/geographic_names/namibia/h/ha.html",
        "Geographic.org (NGA-derived gazetteer)",
        "gazetteer",
        "nga_geographic_names",
    ),
    _source(
        "cambridge_witbooi_imperial_project",
        "Hendrik Witbooi and the evolution of Germany's imperial project",
        "https://www.cambridge.org/core/journals/central-european-history/article/from-boondoggle-to-settlement-colony-hendrik-witbooi-and-the-evolution-of-germanys-imperial-project-in-southwest-africa-18841894/FCFB2D98384A5380494F38821AF76DB8",
        "Cambridge University Press",
        "academic_journal_article",
        "cambridge_central_european_history",
        outcome=True,
    ),
    _source(
        "namibia_ancestral_land_commission",
        "Commission of Inquiry into Claims of Ancestral Land Rights and Restitution",
        "https://mfpe.gov.na/documents/1150081/1187317/REPORT%2B%2BOF%2BTHE%2BCOMMISSION%2BOF%2BINQUIRY%2B%2BINTO%2BCLAIMS%2BOF%2BANCESTRAL%2BLAND%2B%2BRIGHTS%2BAND%2BRESTITUTION%2B.pdf/e2973e3a-3767-4cbf-59da-16eeeed2fe1b?download=true&t=1663750331384",
        "Government of Namibia",
        "government_report",
        "namibia_government_reports",
    ),
    _source(
        "dhm_nama_resistance",
        "Resistance of the Nama",
        "https://www.dhm.de/lemo/kapitel/kaiserreich/aussenpolitik/widerstand-der-nama",
        "Deutsches Historisches Museum",
        "museum_history",
        "deutsches_historisches_museum",
        outcome=True,
    ),
    _source(
        "suub_onganjira_oviumbo_page",
        "Official campaign account: Onganjira and Oviumbo",
        "https://brema.suub.uni-bremen.de/dsdk/content/pagetext/1828982",
        "Staats- und Universitätsbibliothek Bremen",
        "digitized_official_history",
        "suub_bremen_german_colonial_collection",
        outcome=True,
    ),
    _source(
        "ddb_onganjira_provenance",
        "Onganjira collection provenance record",
        "https://ccc.deutsche-digitale-bibliothek.de/en/item/WNO5YFTFZWWL65AJCT673QNO5ISLVVZI",
        "Deutsche Digitale Bibliothek",
        "museum_provenance_record",
        "deutsche_digitale_bibliothek",
    ),
    _source(
        "urjc_german_southwest_campaign_analysis",
        "Campaign analysis of the 1904 war in German South West Africa",
        "https://guerracolonial.oa.urjc.es/index.php/gc/article/view/52/65",
        "Universidad Rey Juan Carlos",
        "academic_journal_article",
        "guerra_colonial_journal",
        outcome=True,
    ),
    _source(
        "scientia_witbooi_fahlgras",
        "Hendrik Witbooi and the action at Fahlgras",
        "https://scientiamilitaria.journals.ac.za/pub/article/download/1249/1336",
        "Scientia Militaria",
        "academic_journal_article",
        "scientia_militaria",
        outcome=True,
    ),
    _source(
        "dbnl_witbooi_papers",
        "The papers of Hendrik Witbooi",
        "https://www.dbnl.org/tekst/witb002dagb01_01/witb002dagb01_01_0002.php",
        "Digitale Bibliotheek voor de Nederlandse Letteren",
        "digitized_primary_source",
        "dbnl",
        outcome=True,
    ),
    _source(
        "nga_kleinvaalgras_gazetteer",
        "Kleinvaalgras geographic-name record",
        "https://geographic.org/geographic_names/name.php?c=namibia&fid=6697&uni=-3554806",
        "Geographic.org (NGA-derived gazetteer)",
        "gazetteer",
        "nga_geographic_names",
    ),
    _source(
        "namibia_meft_waterberg",
        "Waterberg Plateau Park",
        "https://www.meft.gov.na/national-parks/waterberg-plateau-park/231/",
        "Namibia Ministry of Environment, Forestry and Tourism",
        "government_history",
        "namibia_meft",
    ),
    _source(
        "dhm_waterberg_exhibit",
        "The Battle of Waterberg and its aftermath",
        "https://www.dhm.de/archiv/ausstellungen/namibia/rooms/02.htm",
        "Deutsches Historisches Museum",
        "museum_exhibit",
        "deutsches_historisches_museum",
        outcome=True,
    ),
    _source(
        "bundesarchiv_war_against_herero_1904",
        "The war against the Herero in 1904",
        "https://www.bundesarchiv.de/themen-entdecken/online-entdecken/geschichtsgalerien/der-krieg-gegen-die-herero-1904/",
        "German Federal Archives",
        "national_archive_history",
        "german_federal_archives",
        outcome=True,
    ),
    _source(
        "namibia_nhc_heritage_places",
        "National heritage places of Namibia",
        "https://nhc-nam.org/heritage-places/",
        "National Heritage Council of Namibia",
        "government_heritage_record",
        "namibia_national_heritage_council",
        outcome=True,
    ),
    _source(
        "saho_okaharui_1904",
        "Herero people defeat German forces",
        "https://sahistory.org.za/dated-event/herero-people-defeat-german-forces",
        "South African History Online",
        "historical_reference",
        "south_african_history_online",
        outcome=True,
    ),
    _source(
        "ghi_hull_oviumbo",
        "Military culture and the war in German South West Africa",
        "https://www.ghi-dc.org/fileadmin/publications/Bulletin/bu37.pdf",
        "German Historical Institute Washington",
        "academic_study",
        "german_historical_institute_washington",
        outcome=True,
    ),
    _source(
        "frankfurt_ovikokorero_record",
        "Ovikokorero colonial image-archive record",
        "https://sammlungen.ub.uni-frankfurt.de/kolonialesbildarchiv/content/titleinfo/11403260",
        "Goethe University Frankfurt Library",
        "archive_record",
        "frankfurt_colonial_image_archive",
    ),
    _source(
        "wits_kohler_ovaherero_history",
        "A history of the Ovaherero of South West Africa",
        "https://researcharchives.wits.ac.za/downloads/govt0001.pdf",
        "University of the Witwatersrand Historical Papers",
        "digitized_government_ethnology",
        "wits_historical_papers",
        outcome=True,
    ),
    _source(
        "proveana_hornkranz",
        "Assault on Hornkranz, 12 April 1893",
        "https://www.proveana.de/de/ereignis/ueberfall-auf-hornkranz-vom-12-april-1893",
        "German Lost Art Foundation",
        "provenance_event_record",
        "proveana",
        outcome=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start: int,
    end: int,
    source_ids: list[str],
    note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start,
        "end_year": end,
        "region": "Southern Africa",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            note
            + " This identity is conflict- or event-bounded; no rating is inherited "
            "by a generic Nama, Ovaherero, Herero, Damara, ethnic, colonial, or "
            "successor identity."
        ),
        "source_ids": source_ids,
    }


WAVE8_NAMIBIA_RESISTANCE_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "hendrik_witbooi_khowesin_resistance_1893_1894",
        "Hendrik Witbooi's ǀKhowesin resistance (1893–1894)",
        "indigenous_resistance_force",
        1893,
        1894,
        ["cambridge_witbooi_imperial_project", "namibia_ancestral_land_commission"],
        "The separately rated ǀKhowesin force in the 1893–1894 conflict phase.",
    ),
    _entity(
        "hendrik_witbooi_khowesin_resistance_1904_1905",
        "Hendrik Witbooi's ǀKhowesin resistance (1904–1905)",
        "indigenous_resistance_force",
        1904,
        1905,
        ["dhm_nama_resistance", "scientia_witbooi_fahlgras", "dbnl_witbooi_papers"],
        "The distinct 1904–1905 resistance phase under Hendrik Witbooi.",
    ),
    _entity(
        "jakob_morenga_resistance_force_1903_1907",
        "Jakob Morenga's resistance force (1903–1907)",
        "multi_community_resistance_force",
        1903,
        1907,
        ["cambridge_hidden_histories_morenga", "brill_morenga_resistance_chapter"],
        "Morenga's multi-community force, including Nama, Oorlam, Ovaherero, Baster, Damara, and other participants.",
    ),
    _entity(
        "morenga_johannes_christian_hartebeestmund_coalition_1905",
        "Morenga–Johannes Christian coalition at Hartebeestmund",
        "event_bounded_resistance_coalition",
        1905,
        1905,
        ["suub_gswa_campaign_history", "brill_morenga_resistance_chapter"],
        "The event-bounded Morenga–Johannes Christian coalition at Hartebeestmund.",
    ),
    _entity(
        "kandji_tjetjo_eastern_ovaherero_force_1904",
        "Kandji Tjetjo's eastern Ovaherero force (1904)",
        "indigenous_resistance_force",
        1904,
        1904,
        ["namibia_nhc_heritage_places", "urjc_german_southwest_campaign_analysis"],
        "The eastern force and community associated with Kandji Tjetjo during the 1904 campaign.",
    ),
    _entity(
        "samuel_maharero_main_ovaherero_force_1904",
        "Samuel Maharero's main Ovaherero field force (1904)",
        "indigenous_resistance_force",
        1904,
        1904,
        ["suub_onganjira_oviumbo_page", "dhm_waterberg_exhibit", "bundesarchiv_war_against_herero_1904"],
        "Samuel Maharero's main field force during the 1904 campaign.",
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


# The first hash is the repository's semantic HCED fingerprint. The second is a
# compact, sorted-key hash of the complete queue object, including massacre_raw
# and year_best, so a change to either field fails closed.
_ROW_DATA: dict[str, tuple[str, str, str, int]] = {
    "hced-Freyers Farm1904-1": (
        "0d9616d6a0807f13b6c03e635922898cd2fa425fc70bfe08442bed73d258c686",
        "54dce8999ad6a814496e3fb35c9b76cc8e7ca2a89621d6c6183c6161c917db37",
        "Kouchanas/Freyer's Farm",
        1904,
    ),
    "hced-Hartebeestmund1905-1": (
        "e970e5432f4acd9b248ea1048e1fc3ac2f067b4a9acf70cd0ad0a1c0aa5db862",
        "cc953ccbb3f3968de716b9a0ea90195f4218b6d88e52557ddfa53567d4d93788",
        "Hartebeestmund",
        1905,
    ),
    "hced-Hornkranz1893-1": (
        "5cb0b021e32c46c18dbcf808f8ab76c68a030c5f93f00e4a3dd516030419936d",
        "0fb8ef648a3a2e3d628a11fed09782f42ade688cb25f29deb9846210b89132b8",
        "Hornkranz",
        1893,
    ),
    "hced-Naris1904-1": (
        "7d5afe73c5295339af083ed55d0e0a37cf54ef87661e225fb07e06a1087d1eb5",
        "233b37d59d876e6aa947585070e62320133c56d46dc8350fe2f16dfdfe7b08b5",
        "Naris",
        1904,
    ),
    "hced-Naukluf1894-1": (
        "266ce475843ca7d09fafdab565d678fb99bd935626ceff89dbf9c498310e1721",
        "2beed9ba047b983e982cad9fb0b785e7c7ca91033cbccec727f3ebda5bc3c837",
        "Naukluft",
        1894,
    ),
    "hced-Okaharui1904-1": (
        "354321367133215c5fe16ee1c6cdc93443d5b03fd13b7cf4bc55ec9eb12423eb",
        "de886027df1999da4e795155c2ea5084008471a947095655a402bf9fd5364688",
        "Okaharui",
        1904,
    ),
    "hced-Onganjira1904-1": (
        "790747f4b878b628f2c9e65f537892e8ef5a57ef73674968ffcf9611158b7f61",
        "9c56b34fef0585d6ef82baff9dbcc03ef4688114e710d55925d8be2e1fbf440b",
        "Onganjira",
        1904,
    ),
    "hced-Oviumbo1904-1": (
        "86c3d3f9c52408d25d4ca2c81823ae45ef5a3f37f3244ad125b6fceec261bd6b",
        "789a8446764a8177602be4624fbad2112a96a17c3c35221237139ddb1266a9d1",
        "Oviumbo",
        1904,
    ),
    "hced-Owikokorero1904-1": (
        "5b6c24c21c14d4b14e0b7e2d9148bb4bb6337a8bbcd46f7b9f02fc3c1d1fafde",
        "eb4f6a4e21843b511cf27e3b0db86403b9fb071447df16e6cd697ed089741e75",
        "Ovikokorero",
        1904,
    ),
    "hced-Vaalgras1905-1": (
        "f225edf3771b8375b990820fae8f13ea8ab0f8abf40937fa2b4b1f040daa9508",
        "481e04ff89e9b85aef0dde2ec0e59eddf62cba81aa1939cff08833ddab5c1719",
        "Fahlgras/Kleinvaalgras (Koichas)",
        1905,
    ),
    "hced-Van Rooisvlei1928-1": (
        "2a196fde08f661701c62e6f1cf1832c4a5966db14c431eb40e53a87c6c4346c2",
        "f9ac1fbf9cce8a151689ecaa519e831256df0c8e65f35f53028c221be2cda93e",
        "Van Rooisvlei",
        1906,
    ),
    "hced-Waterberg1904-1": (
        "5499f8a1af2f34e97bdd1d730a3aac232df2652e8effdb020ba443f5a1c3a1f5",
        "d19b8868c43b2c3db25826aba804be46856847c5b72358eddd2e3a179a79db41",
        "Ohamakari (Waterberg)",
        1904,
    ),
}


def _contract(
    candidate_id: str,
    cohort: str,
    side_1: list[str],
    side_2: list[str],
    evidence_refs: list[str],
    outcome_source_ids: list[str],
    outcome_source_family_ids: list[str],
    audit_note: str,
) -> dict[str, Any]:
    semantic_hash, full_hash, name, year = _ROW_DATA[candidate_id]
    return {
        "raw_row_sha256": semantic_hash,
        "full_row_sha256": full_hash,
        "canonical_event": _canonical(name, year),
        "cohort": cohort,
        "side_1_entity_ids": side_1,
        "side_2_entity_ids": side_2,
        "winner_side": 1,
        "evidence_refs": evidence_refs,
        "outcome_source_ids": sorted(set(outcome_source_ids)),
        "outcome_source_family_ids": sorted(set(outcome_source_family_ids)),
        "source_outcome_override": False,
        "audit_note": audit_note,
        "war_type": "colonial_anti_colonial",
    }


WAVE8_NAMIBIA_RESISTANCE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Freyers Farm1904-1": _contract(
        "hced-Freyers Farm1904-1",
        "morenga_resistance",
        ["jakob_morenga_resistance_force_1903_1907"],
        ["german_empire"],
        ["suub_gswa_campaign_history", "cambridge_hidden_histories_morenga"],
        ["suub_gswa_campaign_history", "cambridge_hidden_histories_morenga"],
        ["cambridge_hidden_histories_gordonia", "suub_bremen_german_colonial_collection"],
        "Kouchanas/Freyer's Farm is bound to Morenga's multi-community force, which defeated the German Stempel detachment; the raw Herero label is rejected.",
    ),
    "hced-Hartebeestmund1905-1": _contract(
        "hced-Hartebeestmund1905-1",
        "morenga_resistance",
        ["morenga_johannes_christian_hartebeestmund_coalition_1905"],
        ["german_empire"],
        ["suub_gswa_campaign_history", "brill_morenga_resistance_chapter", "nga_hartebeestmund_gazetteer"],
        ["suub_gswa_campaign_history", "brill_morenga_resistance_chapter"],
        ["brill_namibia_history", "suub_bremen_german_colonial_collection"],
        "The exact Morenga–Johannes Christian coalition defeated the German Koppy detachment on 24–25 October 1905; Vaalgras is not inferred as a polity.",
    ),
    "hced-Naris1904-1": _contract(
        "hced-Naris1904-1",
        "witbooi_resistance_1904_1905",
        ["german_empire"],
        ["hendrik_witbooi_khowesin_resistance_1904_1905"],
        ["suub_gswa_campaign_history", "dhm_nama_resistance"],
        ["suub_gswa_campaign_history", "dhm_nama_resistance"],
        ["deutsches_historisches_museum", "suub_bremen_german_colonial_collection"],
        "Deimling's force drove Hendrik Witbooi's ǀKhowesin resistance from its position on 4 December 1904; only the narrow tactical result is rated.",
    ),
    "hced-Naukluf1894-1": _contract(
        "hced-Naukluf1894-1",
        "witbooi_resistance_1893_1894",
        ["german_empire"],
        ["hendrik_witbooi_khowesin_resistance_1893_1894"],
        ["cambridge_witbooi_imperial_project", "namibia_ancestral_land_commission"],
        ["cambridge_witbooi_imperial_project"],
        ["cambridge_central_european_history"],
        "Naukluf is normalized to Naukluft and bound to the separate 1893–1894 ǀKhowesin resistance phase ending in Witbooi's surrender.",
    ),
    "hced-Onganjira1904-1": _contract(
        "hced-Onganjira1904-1",
        "ovaherero_resistance_1904",
        ["german_empire"],
        ["samuel_maharero_main_ovaherero_force_1904"],
        ["suub_onganjira_oviumbo_page", "ddb_onganjira_provenance", "urjc_german_southwest_campaign_analysis"],
        ["suub_onganjira_oviumbo_page", "urjc_german_southwest_campaign_analysis"],
        ["guerra_colonial_journal", "suub_bremen_german_colonial_collection"],
        "German artillery took the Onganjira positions on 9 April 1904; this records only that narrow tactical result, not defeat of the wider resistance.",
    ),
    "hced-Vaalgras1905-1": _contract(
        "hced-Vaalgras1905-1",
        "witbooi_resistance_1904_1905",
        ["german_empire"],
        ["hendrik_witbooi_khowesin_resistance_1904_1905"],
        ["scientia_witbooi_fahlgras", "dbnl_witbooi_papers", "nga_kleinvaalgras_gazetteer"],
        ["scientia_witbooi_fahlgras", "dbnl_witbooi_papers"],
        ["dbnl", "scientia_militaria"],
        "Vaalgras is corrected to Fahlgras/Kleinvaalgras (Koichas); the German transport defense is rated narrowly, without treating the place name as an actor.",
    ),
    "hced-Van Rooisvlei1928-1": _contract(
        "hced-Van Rooisvlei1928-1",
        "morenga_resistance",
        ["german_empire"],
        ["jakob_morenga_resistance_force_1903_1907"],
        ["brill_morenga_resistance_chapter", "cambridge_hidden_histories_morenga"],
        ["brill_morenga_resistance_chapter", "cambridge_hidden_histories_morenga"],
        ["brill_namibia_history", "cambridge_hidden_histories_gordonia"],
        "The stale source-record suffix 1928 is rejected: the queue's reviewed 1906 event is bound to Morenga's force and the German cross-border attack.",
    ),
    "hced-Waterberg1904-1": _contract(
        "hced-Waterberg1904-1",
        "ovaherero_resistance_1904",
        ["german_empire"],
        ["samuel_maharero_main_ovaherero_force_1904"],
        ["namibia_meft_waterberg", "dhm_waterberg_exhibit", "bundesarchiv_war_against_herero_1904"],
        ["dhm_waterberg_exhibit", "bundesarchiv_war_against_herero_1904"],
        ["deutsches_historisches_museum", "german_federal_archives"],
        "Ohamakari/Waterberg is limited to the 11 August battlefield result against Samuel Maharero's main force; genocidal expulsion and desert deaths are separate aftermath.",
    ),
}


def _hold(
    candidate_id: str,
    category: str,
    side_1: list[str],
    side_2: list[str],
    reason: str,
    evidence_refs: list[str],
) -> dict[str, Any]:
    semantic_hash, full_hash, name, year = _ROW_DATA[candidate_id]
    return {
        "raw_row_sha256": semantic_hash,
        "full_row_sha256": full_hash,
        "canonical_event": _canonical(name, year),
        "side_1_entity_ids": side_1,
        "side_2_entity_ids": side_2,
        "hold_category": category,
        "hold_reason": reason,
        "evidence_refs": evidence_refs,
    }


WAVE8_NAMIBIA_RESISTANCE_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Hornkranz1893-1": _hold(
        "hced-Hornkranz1893-1",
        "massacre_without_rateable_outcome",
        ["hendrik_witbooi_khowesin_resistance_1893_1894"],
        ["german_empire"],
        "The surprise assault killed women and children while Witbooi and most fighters escaped. HCED's Nama win is rejected, but the massacre is never flipped into a German win or coerced into a draw.",
        ["cambridge_witbooi_imperial_project", "namibia_ancestral_land_commission", "proveana_hornkranz"],
    ),
    "hced-Okaharui1904-1": _hold(
        "hced-Okaharui1904-1",
        "contradictory_outcome_evidence",
        ["german_empire"],
        ["kandji_tjetjo_eastern_ovaherero_force_1904"],
        "Authoritative accounts conflict on the result and even the exact date. The HCED German win is rejected; no winner or draw is inferred.",
        ["namibia_nhc_heritage_places", "saho_okaharui_1904"],
    ),
    "hced-Oviumbo1904-1": _hold(
        "hced-Oviumbo1904-1",
        "outcome_unknown",
        ["samuel_maharero_main_ovaherero_force_1904"],
        ["german_empire"],
        "Sources characterize Oviumbo as a stand-off, tactical failure, nominal success, or strategic success. HCED's Ovaherero win is rejected and no draw is invented.",
        ["suub_onganjira_oviumbo_page", "ghi_hull_oviumbo", "urjc_german_southwest_campaign_analysis"],
    ),
    "hced-Owikokorero1904-1": _hold(
        "hced-Owikokorero1904-1",
        "outcome_unknown",
        ["german_empire"],
        ["kandji_tjetjo_eastern_ovaherero_force_1904"],
        "Owikokorero is normalized to Ovikokorero. Heavy German losses do not establish a winner, while a government ethnology calls it indecisive; no result is inferred.",
        ["namibia_nhc_heritage_places", "frankfurt_ovikokorero_record", "wits_kohler_ovaherero_history"],
    ),
}


WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS = frozenset(
    WAVE8_NAMIBIA_RESISTANCE_CONTRACTS
)
WAVE8_NAMIBIA_RESISTANCE_HOLD_IDS = frozenset(WAVE8_NAMIBIA_RESISTANCE_HOLDS)
WAVE8_NAMIBIA_RESISTANCE_RESERVED_IDS = (
    WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS | WAVE8_NAMIBIA_RESISTANCE_HOLD_IDS
)


# The shared exact engine currently accepts only global quarantine sets, not
# candidate-local corrected coordinates or countries. This exported map is the
# fail-closed integration contract for a later orchestrator/location pass.
WAVE8_NAMIBIA_LOCATION_REVIEW: dict[str, dict[str, Any]] = {
    "hced-Hartebeestmund1905-1": {
        "point_action": "override",
        "latitude": -28.8,
        "longitude": 18.88333,
        "country_action": "retain",
        "country": "Namibia",
        "evidence_refs": ["nga_hartebeestmund_gazetteer"],
        "audit_note": "HCED's point is in central Namibia; Hartebeestmund lies near the Orange River.",
    },
    "hced-Okaharui1904-1": {
        "point_action": "quarantine",
        "country_action": "retain",
        "country": "Namibia",
        "evidence_refs": ["namibia_nhc_heritage_places"],
        "audit_note": "The supplied point is Windhoek's default coordinate, not an audited battlefield point.",
    },
    "hced-Onganjira1904-1": {
        "point_action": "quarantine",
        "country_action": "retain",
        "country": "Namibia",
        "evidence_refs": ["ddb_onganjira_provenance"],
        "audit_note": "The supplied point is Windhoek's default coordinate and must not be published as the battlefield.",
    },
    "hced-Owikokorero1904-1": {
        "point_action": "quarantine",
        "country_action": "retain",
        "country": "Namibia",
        "evidence_refs": ["frankfurt_ovikokorero_record"],
        "audit_note": "The source point may identify a postal station rather than the battlefield.",
    },
    "hced-Vaalgras1905-1": {
        "point_action": "override",
        "latitude": -26.05,
        "longitude": 18.516667,
        "country_action": "retain",
        "country": "Namibia",
        "evidence_refs": ["nga_kleinvaalgras_gazetteer"],
        "audit_note": "Use the NGA-derived Kleinvaalgras point rather than HCED's central-Namibia point.",
    },
    "hced-Van Rooisvlei1928-1": {
        "point_action": "quarantine",
        "country_action": "retain",
        "country": "South Africa",
        "evidence_refs": ["brill_morenga_resistance_chapter"],
        "audit_note": "Retain the country but quarantine the point pending Van Rooisvlei/Van Rooysvlei disambiguation.",
    },
    "hced-Waterberg1904-1": {
        "point_action": "retain",
        "country_action": "override",
        "country": "Namibia",
        "evidence_refs": ["namibia_meft_waterberg"],
        "audit_note": "HCED's modern country South Africa is corrected to Namibia.",
    },
}


def full_hced_queue_row_sha256(row: Mapping[str, Any]) -> str:
    """Hash every queue field, including fields omitted by the semantic hash."""

    payload = json.dumps(
        dict(row), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _audit_signature() -> str:
    lines: list[str] = []
    for disposition, inventory in (
        ("promote", WAVE8_NAMIBIA_RESISTANCE_CONTRACTS),
        ("hold", WAVE8_NAMIBIA_RESISTANCE_HOLDS),
    ):
        for candidate_id, item in sorted(inventory.items()):
            lines.append(
                "|".join(
                    (
                        disposition,
                        candidate_id,
                        str(item["raw_row_sha256"]),
                        str(item["full_row_sha256"]),
                        str(item["canonical_event"]["canonical_key"]),
                        ",".join(map(str, item.get("side_1_entity_ids", []))),
                        ",".join(map(str, item.get("side_2_entity_ids", []))),
                        str(item.get("winner_side", "")),
                        ",".join(map(str, item.get("outcome_source_ids", []))),
                        str(item.get("hold_category", "")),
                    )
                )
            )
    for candidate_id, review in sorted(WAVE8_NAMIBIA_LOCATION_REVIEW.items()):
        lines.append(
            "|".join(
                (
                    "location",
                    candidate_id,
                    str(review["point_action"]),
                    str(review["country_action"]),
                    str(review.get("latitude", "")),
                    str(review.get("longitude", "")),
                    str(review.get("country", "")),
                )
            )
        )
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if len(WAVE8_NAMIBIA_RESISTANCE_CONTRACTS) != 8:
        raise ValueError("Wave 8 Namibia promotion inventory changed")
    if len(WAVE8_NAMIBIA_RESISTANCE_HOLDS) != 4:
        raise ValueError("Wave 8 Namibia hold inventory changed")
    if WAVE8_NAMIBIA_RESISTANCE_CONTRACT_IDS & WAVE8_NAMIBIA_RESISTANCE_HOLD_IDS:
        raise ValueError("Wave 8 Namibia dispositions overlap")
    if _audit_signature() != WAVE8_NAMIBIA_RESISTANCE_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 Namibia final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_NAMIBIA_RESISTANCE_SOURCES
    }
    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_NAMIBIA_RESISTANCE_ENTITIES
    }
    if len(source_by_id) != len(WAVE8_NAMIBIA_RESISTANCE_SOURCES):
        raise ValueError("Wave 8 Namibia source IDs are not unique")
    if len(entity_by_id) != len(WAVE8_NAMIBIA_RESISTANCE_ENTITIES):
        raise ValueError("Wave 8 Namibia entity IDs are not unique")
    forbidden_ids = {"nama", "nama_tribe", "herero", "hereros", "damara"}
    if forbidden_ids & set(entity_by_id):
        raise ValueError("Wave 8 Namibia may not install a timeless ethnic identity")

    for entity in WAVE8_NAMIBIA_RESISTANCE_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"Wave 8 Namibia identity must be alias-free: {entity['id']}")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"Wave 8 Namibia identity lacks a reset: {entity['id']}")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"Wave 8 Namibia identity has an unknown source: {entity['id']}")

    for candidate_id, item in {
        **WAVE8_NAMIBIA_RESISTANCE_CONTRACTS,
        **WAVE8_NAMIBIA_RESISTANCE_HOLDS,
    }.items():
        if len(str(item["full_row_sha256"])) != 64:
            raise ValueError(f"Wave 8 Namibia full-row hash is invalid: {candidate_id}")
        evidence = set(map(str, item["evidence_refs"]))
        if not evidence <= set(source_by_id):
            raise ValueError(f"Wave 8 Namibia item has an unknown source: {candidate_id}")
        participants = set(map(str, item["side_1_entity_ids"])) | set(
            map(str, item["side_2_entity_ids"])
        )
        if not participants & set(entity_by_id):
            raise ValueError(f"Wave 8 Namibia item lacks a lane identity: {candidate_id}")

    for candidate_id, contract in WAVE8_NAMIBIA_RESISTANCE_CONTRACTS.items():
        if contract.get("source_outcome_override"):
            raise ValueError(f"Wave 8 Namibia may not reverse the raw result: {candidate_id}")
        outcome_ids = set(map(str, contract["outcome_source_ids"]))
        if not outcome_ids or not outcome_ids <= set(map(str, contract["evidence_refs"])):
            raise ValueError(f"Wave 8 Namibia outcome source mismatch: {candidate_id}")
        if any("outcome" not in source_by_id[source_id]["evidence_roles"] for source_id in outcome_ids):
            raise ValueError(f"Wave 8 Namibia outcome source lacks outcome role: {candidate_id}")

    if set(WAVE8_NAMIBIA_LOCATION_REVIEW) - WAVE8_NAMIBIA_RESISTANCE_RESERVED_IDS:
        raise ValueError("Wave 8 Namibia location review references an unreserved row")
    for candidate_id, review in WAVE8_NAMIBIA_LOCATION_REVIEW.items():
        if review["point_action"] not in {"retain", "override", "quarantine"}:
            raise ValueError(f"Wave 8 Namibia point action invalid: {candidate_id}")
        if review["country_action"] not in {"retain", "override", "quarantine"}:
            raise ValueError(f"Wave 8 Namibia country action invalid: {candidate_id}")
        if not set(map(str, review["evidence_refs"])) <= set(source_by_id):
            raise ValueError(f"Wave 8 Namibia location source is unknown: {candidate_id}")


def validate_wave8_namibia_resistance_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_NAMIBIA_RESISTANCE_CONTRACTS,
        WAVE8_NAMIBIA_RESISTANCE_HOLDS,
        lane_name="Wave 8 Namibia resistance",
    )
    indexed = rows_by_candidate_id(hced_rows)
    for disposition, inventory in (
        ("promotion", WAVE8_NAMIBIA_RESISTANCE_CONTRACTS),
        ("hold", WAVE8_NAMIBIA_RESISTANCE_HOLDS),
    ):
        for candidate_id, item in inventory.items():
            actual = full_hced_queue_row_sha256(indexed[candidate_id][0])
            expected = str(item["full_row_sha256"])
            if actual != expected:
                raise ValueError(
                    f"Wave 8 Namibia resistance {disposition} {candidate_id} "
                    f"full queue-row fingerprint changed ({actual} != {expected})"
                )
    return result


def install_wave8_namibia_resistance_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_NAMIBIA_RESISTANCE_ENTITIES,
        lane_name="Wave 8 Namibia resistance",
    )


def install_wave8_namibia_resistance_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_NAMIBIA_RESISTANCE_SOURCES,
        lane_name="Wave 8 Namibia resistance",
    )


def promote_wave8_namibia_resistance_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_namibia_resistance_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_NAMIBIA_RESISTANCE_CONTRACTS,
        lane_name="Wave 8 Namibia resistance",
        event_id_prefix="hced_wave8_namibia_resistance_",
    )


def wave8_namibia_resistance_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_NAMIBIA_RESISTANCE_CONTRACTS.values()
            ).items()
        )
    )
