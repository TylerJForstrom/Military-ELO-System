"""Candidate-keyed Wave 8 contracts for audited Xhosa Frontier War rows."""

from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


WAVE8_XHOSA_FINAL_AUDIT_SIGNATURE = (
    "1ba5fd37f8e3e1b0b0d48ac2a523cba03a66ea305c63d735da2a612b850bf700"
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


WAVE8_XHOSA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "samhs_boma_pass_1850",
        "The Eighth Frontier War: the opening at Boma Pass",
        "https://samilitaryhistory.org/vol153dw.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "uk_hansard_xhosa_war_1851",
        "The Kaffir War",
        "https://api.parliament.uk/historic-hansard/commons/1851/apr/15/the-kaffir-war",
        "UK Parliament",
        "parliamentary_record",
        "uk_parliament_hansard",
    ),
    _source(
        "samhs_burnshill_1846",
        "The War of the Axe and the Burnshill ambush",
        "https://samilitaryhistory.org/vol156ja.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "amathole_xhosa_leadership",
        "Xhosa Gallery",
        "https://museum.za.net/xhosa-gallery/",
        "Amathole Museum",
        "museum_history",
        "amathole_museum",
    ),
    _source(
        "narsa_burnshill_journals",
        "Burnshill journals archival catalogue record",
        "https://www.nationalarchives.gov.za/node/1402607",
        "National Archives and Records Service of South Africa",
        "archival_catalogue",
        "national_archives_south_africa",
    ),
    _source(
        "ward_fort_peddie_1846",
        "Five Years in Kaffirland: Attack on Fort Peddie",
        "https://readingroo.ms/3/5/3/0/35308/35308-h/35308-h.htm",
        "Project Gutenberg",
        "digitized_primary_account",
        "project_gutenberg",
    ),
    _source(
        "saho_peddie",
        "Peddie",
        "https://sahistory.org.za/place/peddie",
        "South African History Online",
        "historical_reference",
        "south_african_history_online",
    ),
    _source(
        "makana_history_culture",
        "History and culture of Makana",
        "https://www.makana.gov.za/history-culture/",
        "Makana Local Municipality",
        "local_government_history",
        "makana_municipality_history",
    ),
    _source(
        "makana_grahamstown_1819",
        "Grahamstown and the 1819 attack",
        "https://www.makana.gov.za/grahamstown/",
        "Makana Local Municipality",
        "local_government_history",
        "makana_municipality_history",
    ),
    _source(
        "govza_makana_1819",
        "Address bestowing freedom of the City of Makana Municipality",
        "https://www.gov.za/news/speeches/address-president-jacob-zuma-occasion-bestowing-freedom-city-makana-municipality",
        "Government of South Africa",
        "government_history",
        "south_african_government",
    ),
    _source(
        "nam_gwanga_1846",
        "Battle of Gwanga collection record",
        "https://collection.nam.ac.uk/detail.php?acc=1971-02-33-191-1",
        "National Army Museum",
        "museum_collection",
        "national_army_museum",
    ),
    _source(
        "up_gwanga_regimental_account",
        "Digitized regimental account of the Battle of Gwanga",
        "https://repository.up.ac.za/server/api/core/bitstreams/edbf29e3-a2a6-4ada-9d24-9853e811cb16/content",
        "University of Pretoria",
        "digitized_primary_account",
        "university_pretoria_repository",
    ),
    _source(
        "samhs_ibeka_nyumaga_1877_1878",
        "The Ninth Frontier War: Ibeka and Nyumaga",
        "https://samilitaryhistory.org/vol056pg.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "up_ninth_frontier_war_memoir",
        "Digitized contemporary memoir of the Ninth Frontier War",
        "https://repository.up.ac.za/bitstreams/e9bb0e9c-a5bc-418f-b295-eee9b5bbf896/download",
        "University of Pretoria",
        "digitized_primary_account",
        "university_pretoria_repository",
    ),
    _source(
        "london_gazette_centane_1878",
        "Official despatch on the Battle of Centane",
        "https://www.thegazette.co.uk/London/issue/24566/page/2187/data.pdf",
        "The London Gazette",
        "official_despatch",
        "uk_london_gazette",
    ),
    _source(
        "mnquma_centane_memorial",
        "Battle of Centane Heroes Monument",
        "https://www.mnquma.gov.za/battle-of-centane-heroes-monument/",
        "Mnquma Local Municipality",
        "local_government_history",
        "mnquma_municipality",
    ),
    _source(
        "scientia_ninth_frontier_war",
        "Study of the Ninth Cape Frontier War",
        "https://scientiamilitaria.journals.ac.za/pub/article/download/152/198/",
        "Scientia Militaria",
        "academic_study",
        "scientia_militaria",
    ),
    _source(
        "samhs_amalinde_1818",
        "The Battle of Amalinde and the Ngqika–Ndlambe conflict",
        "https://samilitaryhistory.org/vol135hk.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
        outcome=True,
    ),
    _source(
        "saho_ngqika_ndlambe",
        "The contentious relationship between Ngqika and Ndlambe",
        "https://sahistory.org.za/article/contentious-relationship-between-ngqika-and-ndlambe",
        "South African History Online",
        "historical_reference",
        "south_african_history_online",
        outcome=True,
    ),
    _source(
        "statssa_amalinde",
        "Amalinde historical place record",
        "https://www.statssa.gov.za/?id=2269&page_id=4286",
        "Statistics South Africa",
        "government_reference",
        "statistics_south_africa",
    ),
    _source(
        "samhs_fish_river_bush_1851",
        "The Battle of the Fish River Bush, 9 September 1851",
        "https://samilitaryhistory.org/vol094ds.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
        outcome=True,
    ),
    _source(
        "makana_frontier_wars_chronology",
        "Historical information: Cape Frontier Wars chronology",
        "https://www.makana.gov.za/history-culture/historical-information/",
        "Makana Local Municipality",
        "local_government_history",
        "makana_municipality_history",
    ),
    _source(
        "saho_eastern_cape_wars_overview",
        "Eastern Cape wars of dispossession, 1779–1878",
        "https://sahistory.org.za/article/eastern-cape-wars-dispossession-1779-1878",
        "South African History Online",
        "historical_reference",
        "south_african_history_online",
    ),
    _source(
        "justice_lcc_eastern_cape_history",
        "Land Claims Court historical findings on the Eastern Cape frontier",
        "https://justice.gov.za/lcc/jdgm/2014/lcc-217-2009.pdf",
        "Department of Justice and Constitutional Development",
        "judicial_record",
        "south_african_justice",
    ),
    _source(
        "samhs_fifth_frontier_war_campaign",
        "Campaign study of the Fifth Cape Frontier War",
        "https://samilitaryhistory.org/jnl2/vol183pi.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "yale_fort_white_archive",
        "Fort White attack archival finding aid",
        "https://ead-pdfs.library.yale.edu/4.pdf",
        "Yale University Library",
        "archival_finding_aid",
        "yale_library",
    ),
    _source(
        "gutenberg_king_campaign_1852",
        "Campaigning in Kaffirland, or Scenes and Adventures in the Kaffir War of 1851–2",
        "https://www.gutenberg.org/cache/epub/48550/pg48550-images.html",
        "Project Gutenberg",
        "digitized_primary_account",
        "project_gutenberg",
    ),
    _source(
        "gutenberg_60th_rifles_1852",
        "The History of the 60th Rifles",
        "https://www.gutenberg.org/cache/epub/57761/pg57761-images.html",
        "Project Gutenberg",
        "digitized_regimental_history",
        "project_gutenberg",
    ),
    _source(
        "samhs_waterkloof_campaign_1851",
        "The Waterkloof campaign of 1851–1852",
        "https://samilitaryhistory.org/vol134ds.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "govza_indigenous_systems_appendix",
        "Appendix: indigenous systems and resistance history",
        "https://www.gov.za/about-government/appendix-indigenous-systems-awards",
        "Government of South Africa",
        "government_history",
        "south_african_government",
    ),
    _source(
        "narsa_third_frontier_war_archive",
        "Archival material on the Third Cape Frontier War",
        "https://www.nationalarchives.gov.za/sites/default/files/ITEM_NEG-0070-0011-_-108.pdf",
        "National Archives and Records Service of South Africa",
        "archival_record",
        "national_archives_south_africa",
    ),
    _source(
        "saho_third_frontier_war_study",
        "Archival period study of the Third Cape Frontier War",
        "https://sahistory.org.za/sites/default/files/archive-files/LiAug56.1729.455X.000.020.Aug1956.6.pdf",
        "South African History Online",
        "archival_study",
        "south_african_history_online",
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    source_ids: list[str],
    note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": "Southern Africa",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            note
            + " This identity is event-bounded; no rating is inherited by a generic "
            "Xhosa, Mfengu, Khoi, Cape, colonial, clan, or successor identity."
        ),
        "source_ids": source_ids,
    }


WAVE8_XHOSA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "ngqika_force_boma_pass_1850",
        "Ngqika force at Boma Pass",
        "indigenous_war_party",
        1850,
        ["samhs_boma_pass_1850", "uk_hansard_xhosa_war_1851"],
        "The Ngqika force that ambushed Colonel Mackinnon's column at Boma Pass.",
    ),
    _entity(
        "sandile_ngqika_force_burnshill_1846",
        "Sandile's Ngqika force at Burnshill",
        "indigenous_war_party",
        1846,
        ["samhs_burnshill_1846", "amathole_xhosa_leadership", "narsa_burnshill_journals"],
        "The Ngqika attacking force associated with Sandile at the Burnshill ambush.",
    ),
    _entity(
        "fort_peddie_mfengu_contingent_1846",
        "Mfengu contingent defending Fort Peddie",
        "indigenous_allied_force",
        1846,
        ["ward_fort_peddie_1846", "saho_peddie"],
        "The Mfengu defenders who fought with the Fort Peddie garrison.",
    ),
    _entity(
        "pato_islambie_congo_ngqika_coalition_1846",
        "Pato–I'Slambie–Congo–Ngqika coalition at Fort Peddie",
        "indigenous_coalition",
        1846,
        ["ward_fort_peddie_1846", "saho_peddie"],
        "The branch-specific coalition identified in the attack on Fort Peddie.",
    ),
    _entity(
        "jan_boesak_khoi_hunters_1819",
        "Jan Boesak's Khoi hunters at Grahamstown",
        "indigenous_allied_force",
        1819,
        ["makana_history_culture", "makana_grahamstown_1819"],
        "The Khoi hunters under Jan Boesak who materially aided Grahamstown's defenders.",
    ),
    _entity(
        "makana_amandlambe_led_coalition_1819",
        "Makana's amaNdlambe-led coalition at Grahamstown",
        "indigenous_coalition",
        1819,
        ["makana_history_culture", "makana_grahamstown_1819", "govza_makana_1819"],
        "The attacking coalition led by Makana for Ndlambe at Grahamstown.",
    ),
    _entity(
        "mfengu_levies_gwanga_1846",
        "Mfengu levies at Gwanga",
        "indigenous_allied_force",
        1846,
        ["nam_gwanga_1846", "up_gwanga_regimental_account"],
        "The Mfengu component of the defending force at Gwanga.",
    ),
    _entity(
        "mhala_siyolo_force_gwanga_1846",
        "Mhala–Siyolo force at Gwanga",
        "indigenous_coalition",
        1846,
        ["nam_gwanga_1846", "up_gwanga_regimental_account"],
        "The combined force associated with Mhala and Siyolo at Gwanga.",
    ),
    _entity(
        "frontier_armed_mounted_police_ibeka_1877",
        "Frontier Armed and Mounted Police at Ibeka",
        "colonial_police_force",
        1877,
        ["samhs_ibeka_nyumaga_1877_1878", "up_ninth_frontier_war_memoir"],
        "The Cape colonial police and artillery formation defending at Ibeka.",
    ),
    _entity(
        "veldman_bikitsha_mfengu_levies_ibeka_1877",
        "Veldman Bikitsha's Mfengu levies at Ibeka",
        "indigenous_allied_force",
        1877,
        ["samhs_ibeka_nyumaga_1877_1878", "up_ninth_frontier_war_memoir"],
        "The Mfengu contingent associated with Veldman Bikitsha at Ibeka.",
    ),
    _entity(
        "sigcawu_sarhili_gcaleka_force_ibeka_1877",
        "Sigcawu–Sarhili Gcaleka force at Ibeka",
        "indigenous_war_party",
        1877,
        ["samhs_ibeka_nyumaga_1877_1878", "up_ninth_frontier_war_memoir"],
        "The Gcaleka attacking force associated with Sigcawu and Sarhili at Ibeka.",
    ),
    _entity(
        "cape_colonial_forces_centane_1878",
        "Cape colonial forces at Centane",
        "colonial_state_force",
        1878,
        ["london_gazette_centane_1878", "mnquma_centane_memorial"],
        "The Cape colonial units documented in the defensive coalition at Centane.",
    ),
    _entity(
        "veldman_poswa_mfengu_levies_centane_1878",
        "Veldman Poswa's Mfengu levies at Centane",
        "indigenous_allied_force",
        1878,
        ["london_gazette_centane_1878", "mnquma_centane_memorial"],
        "The Mfengu levies associated with Veldman Poswa at Centane.",
    ),
    _entity(
        "khiva_sigcawu_gcaleka_ngqika_force_centane_1878",
        "Khiva–Sigcawu Gcaleka–Ngqika force at Centane",
        "indigenous_coalition",
        1878,
        ["london_gazette_centane_1878", "mnquma_centane_memorial"],
        "The branch-specific attacking force associated with Khiva and Sigcawu at Centane.",
    ),
    _entity(
        "frontier_armed_mounted_police_nyumaga_1878",
        "Frontier Armed and Mounted Police at Nyumaga",
        "colonial_police_force",
        1878,
        ["samhs_ibeka_nyumaga_1877_1878", "scientia_ninth_frontier_war"],
        "The Cape colonial police component of Glyn's right column at Nyumaga.",
    ),
    _entity(
        "veldman_bikitsha_mfengu_levies_nyumaga_1878",
        "Veldman Bikitsha's Mfengu levies at Nyumaga",
        "indigenous_allied_force",
        1878,
        ["samhs_ibeka_nyumaga_1877_1878", "scientia_ninth_frontier_war"],
        "The Mfengu levies credited under Veldman Bikitsha at Nyumaga.",
    ),
    _entity(
        "gcaleka_ngqika_force_nyumaga_1878",
        "Gcaleka–Ngqika force at Nyumaga",
        "indigenous_coalition",
        1878,
        ["samhs_ibeka_nyumaga_1877_1878", "scientia_ninth_frontier_war"],
        "The combined Gcaleka–Ngqika opposing force at Nyumaga.",
    ),
    _entity(
        "maqoma_ngqika_rharhabe_force_1818",
        "Maqoma's Ngqika-Rharhabe force at Amalinde",
        "indigenous_war_party",
        1818,
        ["samhs_amalinde_1818", "saho_ngqika_ndlambe", "statssa_amalinde"],
        "The Ngqika-Rharhabe force associated with Maqoma at Amalinde.",
    ),
    _entity(
        "mdushane_ndlambe_hintsa_gcaleka_coalition_1818",
        "Mdushane–Ndlambe–Hintsa Gcaleka coalition at Amalinde",
        "indigenous_coalition",
        1818,
        ["samhs_amalinde_1818", "saho_ngqika_ndlambe", "statssa_amalinde"],
        "Mdushane's Ndlambe army and Hintsa's allied Gcaleka force at Amalinde.",
    ),
    _entity(
        "mfengu_irregulars_fish_river_1851",
        "Mfengu irregulars at Fish River Bush",
        "indigenous_allied_force",
        1851,
        ["samhs_fish_river_bush_1851"],
        "The Mfengu irregular component of Mackinnon's Fish River Bush column.",
    ),
    _entity(
        "siyolo_amandlambe_force_1851",
        "Siyolo's amaNdlambe force at Fish River Bush",
        "indigenous_war_party",
        1851,
        ["samhs_fish_river_bush_1851"],
        "Siyolo's amaNdlambe defenders in the Fish River Bush action.",
    ),
    _entity(
        "fish_river_khoi_rebel_contingent_1851",
        "Khoi rebel contingent at Fish River Bush",
        "rebel_force",
        1851,
        ["samhs_fish_river_bush_1851"],
        "The Khoi rebel contingent fighting with Siyolo at Fish River Bush.",
    ),
)


def _canonical(name: str, low: int, high: int | None = None) -> dict[str, Any]:
    end = low if high is None else high
    return {
        "canonical_key": f"{_slug(name)}:{low}:{end}",
        "date_precision": "year",
        "granularity": "engagement",
        "name": name,
        "year_low": low,
        "year_high": end,
    }


_ROW_DATA: dict[str, tuple[str, str, int, int]] = {
    "hced-Amalinda1818-1": ("e933e6b18a34b30c474a634b33be970d3dfbc0586da70fa12024fb3a7561e2e9", "Battle of Amalinde", 1818, 1818),
    "hced-Boomah Pass1850-1": ("5f0326a3642ea17d36af3729ee51aacacd253dd0719d1ddaa0bbe20ed41bc3da", "Boma Pass", 1850, 1850),
    "hced-Burnshill1846-1": ("1ba38ec0180388b1282f76a7bc7501ba26be8f09ff03bdda51fa172c6eaa075f", "Burnshill ambush", 1846, 1846),
    "hced-Fish River1851-1": ("435995d536b8c94206428a4a065679a0bec91249ff61acc994d7f73f48ae40dc", "Battle of the Fish River Bush", 1851, 1851),
    "hced-Fort Peddie1846-1": ("55df18c77f49a34a558c52e2d6e58c78f1e605265e91c75fa6334d38b7b9b0b8", "Attack on Fort Peddie", 1846, 1846),
    "hced-Grahamstown1819-1": ("8c240796789f0783b7ec8069f6bb2d042e0d62c5efe262bcc758a11fde261e94", "Battle of Grahamstown/Makhanda", 1819, 1819),
    "hced-Gwanga1846-1": ("5ad431e3f37ac838371be6c3ba1368a1d7b892ea80abd5274e0a179bebcb4cd5", "Battle of Gwanga", 1846, 1846),
    "hced-Ibeka1877-1": ("348db8e9f3f293230c19f01cd177cd9cacbd5882ab9ec94a53a9aa5fdef7adb7", "Battle of Ibeka", 1877, 1877),
    "hced-Kentani1878-1": ("e9a098d12c26d9e6bd6028cde6ccf53d86b66708e3bc6c32d07906dd5870be0b", "Battle of Centane", 1878, 1878),
    "hced-NAxama1878-1": ("069ea22bdc8245a3ba595840165e1067cf51a838e53c40e42a0a25c9354d65d2", "Battle of Nyumaga", 1878, 1878),
    "hced-Ciskei1834-1835-1": ("e5bab5fad7899a4ea10b1b12b127c47a2ee80d49180ada4da8879f9daa4972a2", "Ciskei", 1834, 1835),
    "hced-Fish River1781-1": ("b8ed106374c1b416738d82c071c22a56264beae5bab786a5baeef76b828c73cd", "Fish River", 1781, 1781),
    "hced-Fish River1819-1": ("8af823110805daa4de0f991c405b7406c2652b52b45a07c20dfcef171f76b805", "Fish River", 1819, 1819),
    "hced-Fort White1850-1": ("3514eaf10f57b9e3107bca18a7960d94d71c380a69d3693e418a090f1e7edf79", "Fort White", 1850, 1850),
    "hced-Iron Mountain, South Africa1852-1": ("ccd1d5510ad728ebdfbf9241dca8d568edd97909c240a03b2f62126ad7592da1", "Iron Mountain, South Africa", 1852, 1852),
    "hced-Roodewal, Cape Province1802-1": ("640c62d73916b46f27d86b40d11815fdcf5651346ef364537f9cd1bb06ada62f", "Roodewal, Cape Province", 1802, 1802),
    "hced-Sundays1802-1": ("9ede089ee3d52ea9300adb9afe433909061b9385c4d44f5ffd7b7a9d0ea972e7", "Sundays", 1802, 1802),
    "hced-Trompettersdrift1793-1": ("82b4ab9cb4f88fcf8758fdf071c0ecea934dfc4befce2d56fb1070009b2edf76", "Trompettersdrift", 1793, 1793),
    "hced-Waterkloof1851-1": ("07a6b588687f8f1cd93d9b72971e72a4f7b2c166f4516a4c30550acf5f2b8652", "Waterkloof", 1851, 1851),
}


def _contract(
    candidate_id: str,
    cohort: str,
    side_1: list[str],
    side_2: list[str],
    winner_side: int,
    evidence_refs: list[str],
    audit_note: str,
    *,
    outcome_source_ids: list[str] | None = None,
    outcome_source_family_ids: list[str] | None = None,
    war_type: str = "colonial_anti_colonial",
) -> dict[str, Any]:
    row_hash, name, low, high = _ROW_DATA[candidate_id]
    contract: dict[str, Any] = {
        "raw_row_sha256": row_hash,
        "canonical_event": _canonical(name, low, high),
        "cohort": cohort,
        "side_1_entity_ids": side_1,
        "side_2_entity_ids": side_2,
        "winner_side": winner_side,
        "evidence_refs": evidence_refs,
        "audit_note": audit_note,
        "source_outcome_override": outcome_source_ids is not None,
        "war_type": war_type,
    }
    if outcome_source_ids is not None:
        contract["outcome_source_ids"] = sorted(outcome_source_ids)
        contract["outcome_source_family_ids"] = sorted(
            outcome_source_family_ids or []
        )
    return contract


WAVE8_XHOSA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Amalinda1818-1": _contract(
        "hced-Amalinda1818-1",
        "xhosa_civil_war",
        ["maqoma_ngqika_rharhabe_force_1818"],
        ["mdushane_ndlambe_hintsa_gcaleka_coalition_1818"],
        2,
        ["samhs_amalinde_1818", "saho_ngqika_ndlambe", "statssa_amalinde"],
        "Direct evidence reverses HCED's result: Mdushane's Ndlambe–Hintsa coalition defeated Maqoma's Ngqika force at Amalinde.",
        outcome_source_ids=["samhs_amalinde_1818", "saho_ngqika_ndlambe"],
        outcome_source_family_ids=["south_african_history_online", "south_african_military_history_society"],
        war_type="civil_conflict",
    ),
    "hced-Boomah Pass1850-1": _contract(
        "hced-Boomah Pass1850-1",
        "eighth_frontier_war",
        ["ngqika_force_boma_pass_1850"],
        ["united_kingdom"],
        1,
        ["samhs_boma_pass_1850", "uk_hansard_xhosa_war_1851"],
        "The Ngqika ambush forced Mackinnon's British column back; the misspelling Boomah is normalized to Boma.",
    ),
    "hced-Burnshill1846-1": _contract(
        "hced-Burnshill1846-1",
        "seventh_frontier_war",
        ["sandile_ngqika_force_burnshill_1846"],
        ["united_kingdom"],
        1,
        ["samhs_burnshill_1846", "amathole_xhosa_leadership", "narsa_burnshill_journals"],
        "Sandile's branch-specific Ngqika force is bound to the successful Burnshill ambush.",
    ),
    "hced-Fish River1851-1": _contract(
        "hced-Fish River1851-1",
        "eighth_frontier_war",
        ["united_kingdom", "mfengu_irregulars_fish_river_1851"],
        ["siyolo_amandlambe_force_1851", "fish_river_khoi_rebel_contingent_1851"],
        2,
        ["samhs_fish_river_bush_1851"],
        "Direct battle evidence reverses HCED's result: Mackinnon's column failed to dislodge Siyolo's amaNdlambe and Khoi force and abandoned the operation.",
        outcome_source_ids=["samhs_fish_river_bush_1851"],
        outcome_source_family_ids=["south_african_military_history_society"],
    ),
    "hced-Fort Peddie1846-1": _contract(
        "hced-Fort Peddie1846-1",
        "seventh_frontier_war",
        ["united_kingdom", "fort_peddie_mfengu_contingent_1846"],
        ["pato_islambie_congo_ngqika_coalition_1846"],
        1,
        ["ward_fort_peddie_1846", "saho_peddie"],
        "The generic sides are replaced by the Fort Peddie garrison–Mfengu defense and the documented Pato–I'Slambie–Congo–Ngqika coalition.",
    ),
    "hced-Grahamstown1819-1": _contract(
        "hced-Grahamstown1819-1",
        "fifth_frontier_war",
        ["united_kingdom", "jan_boesak_khoi_hunters_1819"],
        ["makana_amandlambe_led_coalition_1819"],
        1,
        ["makana_history_culture", "makana_grahamstown_1819", "govza_makana_1819"],
        "The exact Makana-led amaNdlambe coalition and Jan Boesak's Khoi defenders replace generic Xhosa and British-only sides.",
    ),
    "hced-Gwanga1846-1": _contract(
        "hced-Gwanga1846-1",
        "seventh_frontier_war",
        ["united_kingdom", "mfengu_levies_gwanga_1846"],
        ["mhala_siyolo_force_gwanga_1846"],
        1,
        ["nam_gwanga_1846", "up_gwanga_regimental_account"],
        "The documented British–Mfengu defense and Mhala–Siyolo opposing force replace the two generic labels.",
    ),
    "hced-Ibeka1877-1": _contract(
        "hced-Ibeka1877-1",
        "ninth_frontier_war",
        ["frontier_armed_mounted_police_ibeka_1877", "veldman_bikitsha_mfengu_levies_ibeka_1877"],
        ["sigcawu_sarhili_gcaleka_force_ibeka_1877"],
        1,
        ["samhs_ibeka_nyumaga_1877_1878", "up_ninth_frontier_war_memoir"],
        "Cape colonial police and Mfengu, not a British imperial formation, are bound against Sigcawu and Sarhili's Gcaleka force.",
    ),
    "hced-Kentani1878-1": _contract(
        "hced-Kentani1878-1",
        "ninth_frontier_war",
        ["united_kingdom", "cape_colonial_forces_centane_1878", "veldman_poswa_mfengu_levies_centane_1878"],
        ["khiva_sigcawu_gcaleka_ngqika_force_centane_1878"],
        1,
        ["london_gazette_centane_1878", "mnquma_centane_memorial"],
        "Kentani is normalized to Centane and the official despatch supplies the imperial, Cape colonial, Mfengu, and branch-specific opposing coalition.",
    ),
    "hced-NAxama1878-1": _contract(
        "hced-NAxama1878-1",
        "ninth_frontier_war",
        ["united_kingdom", "frontier_armed_mounted_police_nyumaga_1878", "veldman_bikitsha_mfengu_levies_nyumaga_1878"],
        ["gcaleka_ngqika_force_nyumaga_1878"],
        1,
        ["samhs_ibeka_nyumaga_1877_1878", "scientia_ninth_frontier_war"],
        "The corrupt NAxama label is normalized to Nyumaga and both coalitions are reconstructed from the event evidence.",
    ),
}


def _hold(
    candidate_id: str,
    category: str,
    reason: str,
    evidence_refs: list[str],
) -> dict[str, Any]:
    row_hash, name, low, high = _ROW_DATA[candidate_id]
    return {
        "raw_row_sha256": row_hash,
        "canonical_event": _canonical(name, low, high),
        "hold_category": category,
        "hold_reason": reason,
        "evidence_refs": evidence_refs,
    }


WAVE8_XHOSA_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Ciskei1834-1835-1": _hold(
        "hced-Ciskei1834-1835-1",
        "campaign_aggregate",
        "The row is a region-wide Sixth Frontier War interval with changing Ngqika, Ndlambe, and other forces, not one bounded engagement.",
        ["makana_frontier_wars_chronology", "saho_eastern_cape_wars_overview"],
    ),
    "hced-Fish River1781-1": _hold(
        "hced-Fish River1781-1",
        "campaign_without_discrete_event",
        "The evidence supports a First Frontier War campaign around the Fish River but not a unique battle or exact commando and Gqunukhwebe sides.",
        ["makana_frontier_wars_chronology", "justice_lcc_eastern_cape_history"],
    ),
    "hced-Fish River1819-1": _hold(
        "hced-Fish River1819-1",
        "possible_campaign_duplicate",
        "No authoritative discrete Fish River battle matches the row; it likely aggregates or duplicates retaliation after Grahamstown.",
        ["makana_grahamstown_1819", "samhs_fifth_frontier_war_campaign", "justice_lcc_eastern_cape_history"],
    ),
    "hced-Fort White1850-1": _hold(
        "hced-Fort White1850-1",
        "date_and_actor_conflict",
        "The archival attack is dated 3 January 1851 while HCED says 1850, and the attacker is not branch-resolved; no year or actor is invented.",
        ["yale_fort_white_archive"],
    ),
    "hced-Iron Mountain, South Africa1852-1": _hold(
        "hced-Iron Mountain, South Africa1852-1",
        "ambiguous_event_boundary",
        "Contemporary accounts describe multiple 1852 Iron Mountain actions, so this row cannot be assigned without inventing an event boundary or victory.",
        ["gutenberg_king_campaign_1852", "gutenberg_60th_rifles_1852", "samhs_waterkloof_campaign_1851"],
    ),
    "hced-Roodewal, Cape Province1802-1": _hold(
        "hced-Roodewal, Cape Province1802-1",
        "unverified_event_and_sides",
        "No authoritative discrete engagement or result matching Roodewal was found, and period evidence indicates a broader Khoi–Xhosa coalition.",
        ["govza_indigenous_systems_appendix", "narsa_third_frontier_war_archive", "saho_third_frontier_war_study"],
    ),
    "hced-Sundays1802-1": _hold(
        "hced-Sundays1802-1",
        "unverified_event_and_sides",
        "No authoritative discrete engagement or result matching Sundays was found, and the two-party Boer/Xhosa formulation omits the period coalition.",
        ["govza_indigenous_systems_appendix", "narsa_third_frontier_war_archive", "saho_third_frontier_war_study"],
    ),
    "hced-Trompettersdrift1793-1": _hold(
        "hced-Trompettersdrift1793-1",
        "unknown_outcome_not_draw",
        "The loser is blank, so the nominal draw is structurally incomplete and remains unknown; the chronology also does not establish a unique engagement.",
        ["makana_frontier_wars_chronology", "justice_lcc_eastern_cape_history"],
    ),
    "hced-Waterkloof1851-1": _hold(
        "hced-Waterkloof1851-1",
        "campaign_aggregate",
        "Waterkloof denotes a month-long campaign with changing forces and no single set-piece battle or defensible overall tactical winner.",
        ["samhs_waterkloof_campaign_1851"],
    ),
}


WAVE8_XHOSA_CONTRACT_IDS = frozenset(WAVE8_XHOSA_CONTRACTS)
WAVE8_XHOSA_HOLD_IDS = frozenset(WAVE8_XHOSA_HOLDS)
WAVE8_XHOSA_RESERVED_IDS = WAVE8_XHOSA_CONTRACT_IDS | WAVE8_XHOSA_HOLD_IDS


def _audit_signature() -> str:
    lines: list[str] = []
    for disposition, inventory in (
        ("promote", WAVE8_XHOSA_CONTRACTS),
        ("hold", WAVE8_XHOSA_HOLDS),
    ):
        for candidate_id, item in sorted(inventory.items()):
            lines.append(
                "|".join(
                    (
                        disposition,
                        candidate_id,
                        str(item["raw_row_sha256"]),
                        str(item["canonical_event"]["canonical_key"]),
                        ",".join(map(str, item.get("side_1_entity_ids", []))),
                        ",".join(map(str, item.get("side_2_entity_ids", []))),
                        str(item.get("winner_side", "")),
                        str(bool(item.get("source_outcome_override"))),
                        ",".join(map(str, item.get("outcome_source_ids", []))),
                        str(item.get("hold_category", "")),
                    )
                )
            )
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


def _validate_static() -> None:
    if (len(WAVE8_XHOSA_CONTRACTS), len(WAVE8_XHOSA_HOLDS)) != (10, 9):
        raise ValueError("Wave 8 Xhosa disposition inventory changed")
    if (len(WAVE8_XHOSA_ENTITIES), len(WAVE8_XHOSA_SOURCES)) != (22, 32):
        raise ValueError("Wave 8 Xhosa identity/source inventory changed")
    if WAVE8_XHOSA_CONTRACT_IDS & WAVE8_XHOSA_HOLD_IDS:
        raise ValueError("Wave 8 Xhosa promotion and hold inventories overlap")
    if _audit_signature() != WAVE8_XHOSA_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 Xhosa final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_XHOSA_SOURCES}
    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_XHOSA_ENTITIES}
    if len(source_by_id) != len(WAVE8_XHOSA_SOURCES):
        raise ValueError("Wave 8 Xhosa source IDs are not unique")
    if len(entity_by_id) != len(WAVE8_XHOSA_ENTITIES):
        raise ValueError("Wave 8 Xhosa entity IDs are not unique")
    if {"xhosa", "xhosa_kingdom"} & set(entity_by_id):
        raise ValueError("Wave 8 Xhosa may not install a generic Xhosa identity")

    for entity in WAVE8_XHOSA_ENTITIES:
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"Wave 8 Xhosa identity is not event-bounded: {entity['id']}")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"Wave 8 Xhosa identity must be alias-free: {entity['id']}")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"Wave 8 Xhosa identity lacks a reset: {entity['id']}")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"Wave 8 Xhosa identity has an unknown source: {entity['id']}")

    override_ids: set[str] = set()
    for candidate_id, contract in WAVE8_XHOSA_CONTRACTS.items():
        evidence = set(map(str, contract["evidence_refs"]))
        if not evidence <= set(source_by_id):
            raise ValueError(f"Wave 8 Xhosa contract has an unknown source: {candidate_id}")
        participants = set(map(str, contract["side_1_entity_ids"])) | set(
            map(str, contract["side_2_entity_ids"])
        )
        if not participants & set(entity_by_id):
            raise ValueError(f"Wave 8 Xhosa contract lacks a lane identity: {candidate_id}")
        if contract.get("source_outcome_override"):
            override_ids.add(candidate_id)
            outcome_ids = set(map(str, contract.get("outcome_source_ids", [])))
            if not outcome_ids or not outcome_ids <= evidence:
                raise ValueError(f"Wave 8 Xhosa override source mismatch: {candidate_id}")
            if any("outcome" not in source_by_id[source_id]["evidence_roles"] for source_id in outcome_ids):
                raise ValueError(f"Wave 8 Xhosa override source lacks outcome role: {candidate_id}")
    if override_ids != {"hced-Amalinda1818-1", "hced-Fish River1851-1"}:
        raise ValueError("Wave 8 Xhosa outcome override inventory changed")

    for candidate_id, hold in WAVE8_XHOSA_HOLDS.items():
        if not set(map(str, hold["evidence_refs"])) <= set(source_by_id):
            raise ValueError(f"Wave 8 Xhosa hold has an unknown source: {candidate_id}")
        if not str(hold["hold_reason"]).strip():
            raise ValueError(f"Wave 8 Xhosa hold lacks a reason: {candidate_id}")


def validate_wave8_xhosa_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_XHOSA_CONTRACTS,
        WAVE8_XHOSA_HOLDS,
        lane_name="Wave 8 Xhosa",
    )


def install_wave8_xhosa_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_XHOSA_ENTITIES,
        lane_name="Wave 8 Xhosa",
    )


def install_wave8_xhosa_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_XHOSA_SOURCES,
        lane_name="Wave 8 Xhosa",
    )


def promote_wave8_xhosa_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_xhosa_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_XHOSA_CONTRACTS,
        lane_name="Wave 8 Xhosa",
        event_id_prefix="hced_wave8_xhosa_",
    )


def wave8_xhosa_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_XHOSA_CONTRACTS.values()
            ).items()
        )
    )
