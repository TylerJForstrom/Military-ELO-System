"""Exact Wave 8 contracts for Somali, Irish, and South African audit cohorts.

The lane is deliberately candidate-keyed.  Generic labels such as ``Somalia``,
``Ireland``, and ``South Africa`` never participate in identity resolution.
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
    "WAVE8_SOMALI_IRISH_SA_CONTRACTS",
    "WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS",
    "WAVE8_SOMALI_IRISH_SA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SOMALI_IRISH_SA_ENTITIES",
    "WAVE8_SOMALI_IRISH_SA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SOMALI_IRISH_SA_HOLDS",
    "WAVE8_SOMALI_IRISH_SA_HOLD_IDS",
    "WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_SOMALI_IRISH_SA_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDE_METADATA",
    "WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES",
    "WAVE8_SOMALI_IRISH_SA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SOMALI_IRISH_SA_RESERVED_IDS",
    "WAVE8_SOMALI_IRISH_SA_SOURCES",
    "install_wave8_somali_irish_sa_entities",
    "install_wave8_somali_irish_sa_sources",
    "promote_wave8_somali_irish_sa_contracts",
    "validate_wave8_somali_irish_sa_queue_contracts",
    "wave8_somali_irish_sa_audit_signature",
    "wave8_somali_irish_sa_cohort_counts",
    "wave8_somali_irish_sa_counts",
)


_LANE_NAME = "Wave 8 Somali Dervish, Irish Civil War, and South Africa WWI"
WAVE8_SOMALI_IRISH_SA_FINAL_AUDIT_SIGNATURE = (
    "1db9ca2d7cbec4fe94c42929f7f5d1eb15d2ab6e3724a78411486ec99636585d"
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


WAVE8_SOMALI_IRISH_SA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "uk_wo_somaliland_official_history_1907",
        "Official History of the Operations in Somaliland, 1901–04",
        "https://archive.org/details/officialhistory00stafgoog",
        "War Office",
        "digitized_official_history",
        "uk_war_office",
    ),
    _source(
        "uk_hansard_gumburu_1903",
        "The Disaster in Somaliland",
        "https://api.parliament.uk/historic-hansard/commons/1903/apr/23/the-disaster-in-somaliland",
        "UK Parliament",
        "parliamentary_record",
        "uk_parliament_hansard",
    ),
    _source(
        "uk_hansard_illig_1904",
        "The Capture of Fort Illig",
        "https://api.parliament.uk/historic-hansard/commons/1904/apr/28/the-capture-of-fort-illig",
        "UK Parliament",
        "parliamentary_record",
        "uk_parliament_hansard",
    ),
    _source(
        "uk_gazette_somaliland_1920",
        "Official despatch on operations in Somaliland, 1920",
        "https://www.thegazette.co.uk/London/issue/32107/supplement/10589/data.pdf",
        "The London Gazette",
        "official_despatch",
        "uk_london_gazette",
    ),
    _source(
        "jardine_mad_mullah_somaliland_1923",
        "The Mad Mullah of Somaliland",
        "https://archive.org/details/TheMadMullahOfSomaliland",
        "Herbert Jenkins Ltd.",
        "digitized_administration_history",
        "somaliland_administration_history",
    ),
    _source(
        "raf_casps_somaliland_1920",
        "Air Power Review: the 1920 Somaliland campaign",
        "https://www.raf.mod.uk/what-we-do/centre-for-air-and-space-power-studies/aspr/apr-vol21-iss1-5-pdf/",
        "Royal Air Force Centre for Air and Space Power Studies",
        "official_military_study",
        "raf_casps",
    ),
    _source(
        "ie_military_archives_four_courts_1922",
        "Attack on Four Courts",
        "https://www.militaryarchives.ie/en/online-collections/military-service-pensions-collection-1916-1923/brigade-activity-reports/operations/attack-on-four-courts",
        "Military Archives of Ireland",
        "government_archive",
        "irish_military_archives",
    ),
    _source(
        "ie_bmh_clonmel_ws1763",
        "Bureau of Military History Witness Statement 1763",
        "https://bmh.militaryarchives.ie/reels/bmh/BMH.WS1763.pdf",
        "Military Archives of Ireland",
        "digitized_primary_testimony",
        "irish_military_archives",
    ),
    _source(
        "ucc_atlas_civil_war_unit8",
        "Atlas of the Irish Revolution: The Civil War, Part 2",
        "https://www.ucc.ie/en/media/projectsandcentres/irishrevolution/documents/U8.TYPROJECTBOOK-THECIVILWAR%28P.2%29.pdf",
        "University College Cork",
        "academic_history",
        "ucc_atlas_irish_revolution",
    ),
    _source(
        "rte_ucc_battle_dublin_1922",
        "The Battle of Dublin",
        "https://www.rte.ie/history/battle-of-dublin/",
        "RTÉ and University College Cork",
        "academic_public_history",
        "ucc_atlas_irish_revolution",
    ),
    _source(
        "rte_ucc_kilmallock_1922",
        "The Battle of Kilmallock",
        "https://www.rte.ie/history/conventional-phase/2022/0630/1307775-the-battle-of-kilmallock/",
        "RTÉ and University College Cork",
        "academic_public_history",
        "ucc_atlas_irish_revolution",
    ),
    _source(
        "rte_ucc_cork_1922",
        "The Battle of Cork",
        "https://www.rte.ie/history/sea-landings/2022/0804/1313977-the-battle-of-cork/",
        "RTÉ and University College Cork",
        "academic_public_history",
        "ucc_atlas_irish_revolution",
    ),
    _source(
        "rte_ucc_clashmealcon_1923",
        "Cave men: cave hideouts in the Civil War",
        "https://www.rte.ie/history/2022/0830/1319586-cave-men-cave-hideouts-in-the-civil-war/",
        "RTÉ and University College Cork",
        "academic_public_history",
        "ucc_atlas_irish_revolution",
    ),
    _source(
        "nam_delville_wood_1916",
        "South African troops at Delville Wood, 1916",
        "https://collection.nam.ac.uk/detail.php?acc=1994-12-26-1",
        "National Army Museum",
        "museum_collection",
        "national_army_museum",
    ),
    _source(
        "samh_sandfontein_1914",
        "The Battle of Sandfontein, 26 September 1914",
        "https://samilitaryhistory.org/vol164ra.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "samh_gibeon_1915",
        "The Battle of Gibeon, 1915",
        "https://www.samilitaryhistory.org/vol132hp.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "nam_south_west_africa_campaign",
        "The South West Africa campaign",
        "https://www.nam.ac.uk/explore/south-west-african-campaign",
        "National Army Museum",
        "museum_history",
        "national_army_museum",
    ),
    _source(
        "samh_salaita_1916",
        "The Battle of Salaita Hill, 12 February 1916",
        "https://www.samilitaryhistory.org/vol166as.html",
        "South African Military History Society",
        "military_history_study",
        "south_african_military_history_society",
    ),
    _source(
        "historia_gswa_airpower_2017",
        "Air power in the German South West Africa campaign",
        "https://scielo.org.za/scielo.php?pid=S0018-229X2017000200001&script=sci_arttext",
        "Historia, Stellenbosch University",
        "academic_journal_article",
        "historia_stellenbosch",
    ),
    _source(
        "kenya_gazette_salaita_heritage_2015",
        "Gazette notice for Salaita Hill heritage site",
        "https://new.kenyalaw.org/akn/ke/officialGazette/2015-01-23/7/eng@2015-01-23/source",
        "The Kenya Gazette",
        "government_heritage_record",
        "kenya_gazette",
        outcome=False,
    ),
    _source(
        "namibia_meft_sandfontein_heritage_2024",
        "Heritage assessment covering the Sandfontein battlefield",
        "https://eia.meft.gov.na/screening/4874_241111_epl_9049_heritage.pdf",
        "Namibia Ministry of Environment, Forestry and Tourism",
        "government_heritage_report",
        "namibia_meft",
        outcome=False,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: list[str],
    note: str,
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
        "source_ids": source_ids,
    }


WAVE8_SOMALI_IRISH_SA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "somali_dervish_movement_1899_1920",
        "Somali Dervish movement (1899–1920)",
        "anti_colonial_movement_force",
        1899,
        1920,
        "Horn of Africa",
        ["uk_wo_somaliland_official_history_1907", "jardine_mad_mullah_somaliland_1923"],
        "Conflict-bounded movement and fighting force associated with Mohammed Abdullah Hassan. No rating is inherited by modern Somalia, Somaliland, Somali ethnicity, or any later Islamist movement.",
    ),
    _entity(
        "irish_national_army_1922_1923",
        "Irish National Army (1922–1923)",
        "state_army",
        1922,
        1923,
        "Ireland",
        ["ie_military_archives_four_courts_1922", "ucc_atlas_civil_war_unit8"],
        "The exact National Army formation spanning Provisional Government and Irish Free State Civil War service. No rating is inherited by the Irish Free State polity, later Defence Forces, or modern Ireland.",
    ),
    _entity(
        "anti_treaty_ira_1922_1923",
        "Anti-Treaty IRA (1922–1923)",
        "insurgent_army",
        1922,
        1923,
        "Ireland",
        ["ie_bmh_clonmel_ws1763", "ucc_atlas_civil_war_unit8"],
        "Civil-War-bounded anti-Treaty fighting force. No rating is inherited by modern Ireland or by any earlier or later organization using an IRA name.",
    ),
    _entity(
        "union_defence_force_gswa_1914_1915",
        "Union Defence Force in German South West Africa (1914–1915)",
        "campaign_force",
        1914,
        1915,
        "Southern Africa",
        ["nam_south_west_africa_campaign", "samh_sandfontein_1914", "samh_gibeon_1915"],
        "Campaign-bounded Union Defence Force formation. No rating is inherited by post-1932 South Africa, the later South African Defence Force, or a modern South African state identity.",
    ),
    _entity(
        "first_south_african_infantry_brigade_delville_1916",
        "1st South African Infantry Brigade at Delville Wood",
        "expeditionary_brigade",
        1916,
        1916,
        "Western Front",
        ["nam_delville_wood_1916"],
        "Event-bounded Delville Wood formation. No rating is inherited by post-1932 South Africa or any successor military formation.",
    ),
    _entity(
        "second_south_african_infantry_brigade_salaita_1916",
        "2nd South African Infantry Brigade at Salaita",
        "expeditionary_brigade",
        1916,
        1916,
        "East Africa",
        ["samh_salaita_1916"],
        "Event-bounded Salaita formation. No rating is inherited by post-1932 South Africa or any successor military formation.",
    ),
    _entity(
        "first_east_african_infantry_brigade_salaita_1916",
        "1st East African Infantry Brigade at Salaita",
        "expeditionary_brigade",
        1916,
        1916,
        "East Africa",
        ["samh_salaita_1916"],
        "Event-bounded Salaita formation. No rating is inherited by a modern East African state or any successor military formation.",
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
    "hced-Ferdiddin1901-1": ("9a1e86ae792c894d008be14ecdbacbdd4c5570a547e8edfad4fab3ef067ae972", "Battle of Ferdiddin", 1901),
    "hced-Galiabur1920-1": ("b6e0ced973d552bc889e0bcbf1f34ad9793a36b69553defb5b3cd4c2a5c9bba3", "Capture of Galbaribur Fort", 1920),
    "hced-Gumburu1903-1": ("97d395d0df097c6fbc8f3c809281da0f62e01d62d8b4408ad361ca3324d8aa73", "Battle of Gumburu", 1903),
    "hced-Illig1904-1": ("a404b33b3437f5dadce10b97b11a2ce2d70af1f706f1b1fdd9eefa5d727113c8", "Capture of Illig", 1904),
    "hced-OK Pass1919-1": ("c904b656816f98f9fc69f95f60a3569f764ae0f7e1d71fb67cf15bd9f754f0ea", "Battle of O.K. Pass", 1919),
    "hced-Samala1901-1": ("2909c56d70116245baa7abc44b6326873d226572147f34c77e8bd73580746abe", "Battle of Samala", 1901),
    "hced-Taleh1920-1": ("31aec59e797cb5be0e00cf4418a84f8ee7a9c4294023bcd0fd4be9c932ae8e1a", "Capture of Tale Forts", 1920),
    "hced-Clashmealcon Caves1923-1": ("52145253458e16ea3011c2ec940379337b8a13c8db7b303de0a681bdd2c5ac0a", "Siege of Clashmealcon Caves", 1923),
    "hced-Clonmel1922-1": ("b65205a46e124cf8c1eb7ca84a30904f1f9f1d65c0df1aa16ee88d08ecf2df29", "Clonmel rearguard action", 1922),
    "hced-Cork1922-1": ("043da1bce787e24eb7b821cdbbca67d733de899a0e4d48872661b9cebfeefa34", "Battle of Cork (Rochestown–Douglas)", 1922),
    "hced-Four Courts1922-1": ("9c9f74a1a0e7abb4b0f994fab647f1b1dd3ae72b4c3c5f2f9e0dc0e2bd134c06", "Battle of the Four Courts", 1922),
    "hced-Kilmallock1922-1": ("71ad09d82ccc99f58af8863d1d016e0b64610deae89744ae5ad881ae0de563c9", "Battle of Kilmallock", 1922),
    "hced-O'Connell Street1922-1": ("e316ec79493211d33f557bbf88d2edba8e3ab1395d6ccc5ace5c1b1f8438be47", "O'Connell Street Block fighting", 1922),
    "hced-Delville Wood1916-1": ("33d1d7d22a0184bbf9aeb9e9d974992e4b8304ed6ebb5337ce5a82fbbc59acb3", "South African defence of Delville Wood", 1916),
    "hced-Gibeon1915-1": ("8ea2de1faeafb19c8501dc3e82d89f0ec84ac9ef193e7c1ec5c659cf90c06d52", "Battle of Gibeon", 1915),
    "hced-Salaita1916-1": ("690e000d8edfff493d14d78b29891bbb6fb67061f1902fcb0d944c82ce62b1d0", "Battle of Salaita Hill", 1916),
    "hced-Sandfontein1914-1": ("0c168c107ea913817b9da4ba1e9680c322572ecc0dd9c952405ffc7e6b8384b8", "Battle of Sandfontein", 1914),
    "hced-Windhoek1915-1": ("009404963bebeeecdbcb9f656c6da10664214a90881dd898893eb399a774d923", "Unopposed occupation of Windhoek", 1915),
}


def _contract(
    candidate_id: str,
    cohort: str,
    side_1: list[str],
    side_2: list[str],
    winner_side: int,
    war_type: str,
    evidence_refs: list[str],
    outcome_source_ids: list[str],
    outcome_source_family_ids: list[str],
    audit_note: str,
    *,
    source_outcome_override: bool = False,
) -> dict[str, Any]:
    row_hash, name, year = _ROW_DATA[candidate_id]
    return {
        "raw_row_sha256": row_hash,
        "canonical_event": _canonical(name, year),
        "cohort": cohort,
        "side_1_entity_ids": side_1,
        "side_2_entity_ids": side_2,
        "winner_side": winner_side,
        "result_type": "win",
        "war_type": war_type,
        "evidence_refs": evidence_refs,
        "outcome_source_ids": sorted(set(outcome_source_ids)),
        "outcome_source_family_ids": sorted(set(outcome_source_family_ids)),
        "source_outcome_override": source_outcome_override,
        "audit_note": audit_note,
    }


_DERVISH = "somali_dervish_movement_1899_1920"
_NATIONAL_ARMY = "irish_national_army_1922_1923"
_ANTI_TREATY = "anti_treaty_ira_1922_1923"
_UDF_GSWA = "union_defence_force_gswa_1914_1915"

WAVE8_SOMALI_IRISH_SA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Ferdiddin1901-1": _contract(
        "hced-Ferdiddin1901-1", "somali_dervish_wars", ["united_kingdom"], [_DERVISH], 1,
        "colonial_anti_colonial", ["uk_wo_somaliland_official_history_1907", "jardine_mad_mullah_somaliland_1923"],
        ["uk_wo_somaliland_official_history_1907"], ["uk_war_office"],
        "The 17 July 1901 action was a British tactical success followed by withdrawal; no strategic defeat of the Dervish movement is inferred.",
    ),
    "hced-Galiabur1920-1": _contract(
        "hced-Galiabur1920-1", "somali_dervish_wars", ["united_kingdom"], [_DERVISH], 1,
        "colonial_anti_colonial", ["uk_gazette_somaliland_1920", "jardine_mad_mullah_somaliland_1923", "raf_casps_somaliland_1920"],
        ["uk_gazette_somaliland_1920", "raf_casps_somaliland_1920"], ["uk_london_gazette", "raf_casps"],
        "Galbaribur was bombarded on 7 February and stormed on 8 February 1920; the contract rates only the fort action.",
    ),
    "hced-Gumburu1903-1": _contract(
        "hced-Gumburu1903-1", "somali_dervish_wars", [_DERVISH], ["united_kingdom"], 1,
        "colonial_anti_colonial", ["uk_wo_somaliland_official_history_1907", "uk_hansard_gumburu_1903", "jardine_mad_mullah_somaliland_1923"],
        ["uk_wo_somaliland_official_history_1907", "uk_hansard_gumburu_1903"], ["uk_war_office", "uk_parliament_hansard"],
        "The Dervish force destroyed Plunkett's detachment at Gumburu on 17 April 1903. Unsafe source coordinates and country attribution are withheld.",
    ),
    "hced-Illig1904-1": _contract(
        "hced-Illig1904-1", "somali_dervish_wars", ["united_kingdom"], [_DERVISH], 1,
        "colonial_anti_colonial", ["uk_wo_somaliland_official_history_1907", "uk_hansard_illig_1904"],
        ["uk_wo_somaliland_official_history_1907", "uk_hansard_illig_1904"], ["uk_war_office", "uk_parliament_hansard"],
        "British naval and Hampshire troops stormed Illig on 21 April 1904; no Italian combatant is added, and the raw Sudan country label is withheld.",
    ),
    "hced-OK Pass1919-1": _contract(
        "hced-OK Pass1919-1", "somali_dervish_wars", ["united_kingdom"], [_DERVISH], 1,
        "colonial_anti_colonial", ["jardine_mad_mullah_somaliland_1923"],
        ["jardine_mad_mullah_somaliland_1923"], ["somaliland_administration_history"],
        "The contract covers the O.K. Pass action of the night of 28 February–1 March 1919 and does not merge the distinct 3 March ambush.",
    ),
    "hced-Samala1901-1": _contract(
        "hced-Samala1901-1", "somali_dervish_wars", ["united_kingdom"], [_DERVISH], 1,
        "colonial_anti_colonial", ["uk_wo_somaliland_official_history_1907", "jardine_mad_mullah_somaliland_1923"],
        ["uk_wo_somaliland_official_history_1907"], ["uk_war_office"],
        "McNeill's detachment repelled repeated Dervish attacks at Samala on 2 June 1901; only that defensive tactical result is rated.",
    ),
    "hced-Taleh1920-1": _contract(
        "hced-Taleh1920-1", "somali_dervish_wars", ["united_kingdom"], [_DERVISH], 1,
        "colonial_anti_colonial", ["uk_gazette_somaliland_1920", "jardine_mad_mullah_somaliland_1923", "raf_casps_somaliland_1920"],
        ["uk_gazette_somaliland_1920", "raf_casps_somaliland_1920"], ["uk_london_gazette", "raf_casps"],
        "Gibb's Tribal Levy rushed the lightly held Tale forts on 9 February 1920 after RAF shaping; the discrete ground engagement is rated.",
    ),
    "hced-Clashmealcon Caves1923-1": _contract(
        "hced-Clashmealcon Caves1923-1", "irish_civil_war", [_NATIONAL_ARMY], [_ANTI_TREATY], 1,
        "civil_war", ["rte_ucc_clashmealcon_1923", "ucc_atlas_civil_war_unit8"],
        ["rte_ucc_clashmealcon_1923"], ["ucc_atlas_irish_revolution"],
        "The 15–18 April 1923 siege ended in anti-Treaty surrender. Alleged killings after surrender are outside the rated engagement.",
    ),
    "hced-Clonmel1922-1": _contract(
        "hced-Clonmel1922-1", "irish_civil_war", [_NATIONAL_ARMY], [_ANTI_TREATY], 1,
        "civil_war", ["ie_bmh_clonmel_ws1763", "ucc_atlas_civil_war_unit8"],
        ["ie_bmh_clonmel_ws1763"], ["irish_military_archives"],
        "A primary witness statement records the 9 August 1922 armed rearguard action, machine-gun fire, and an abandoned armoured car; this was not a mere occupation.",
    ),
    "hced-Cork1922-1": _contract(
        "hced-Cork1922-1", "irish_civil_war", [_NATIONAL_ARMY], [_ANTI_TREATY], 1,
        "civil_war", ["rte_ucc_cork_1922", "ucc_atlas_civil_war_unit8"],
        ["rte_ucc_cork_1922"], ["ucc_atlas_irish_revolution"],
        "The contract is limited to the Rochestown–Douglas fighting of 8–10 August 1922 rather than treating all control of Cork as one event.",
    ),
    "hced-Four Courts1922-1": _contract(
        "hced-Four Courts1922-1", "irish_civil_war", [_NATIONAL_ARMY], [_ANTI_TREATY], 1,
        "civil_war", ["ie_military_archives_four_courts_1922", "rte_ucc_battle_dublin_1922"],
        ["ie_military_archives_four_courts_1922", "rte_ucc_battle_dublin_1922"], ["irish_military_archives", "ucc_atlas_irish_revolution"],
        "The 28–30 June 1922 Four Courts battle is separated from the later O'Connell Street block fighting.",
    ),
    "hced-Kilmallock1922-1": _contract(
        "hced-Kilmallock1922-1", "irish_civil_war", [_NATIONAL_ARMY], [_ANTI_TREATY], 1,
        "civil_war", ["rte_ucc_kilmallock_1922", "ucc_atlas_civil_war_unit8"],
        ["rte_ucc_kilmallock_1922"], ["ucc_atlas_irish_revolution"],
        "The rated event is the approximately 25 July–5 August 1922 battle; the final unopposed occupation alone is not treated as the win.",
    ),
    "hced-O'Connell Street1922-1": _contract(
        "hced-O'Connell Street1922-1", "irish_civil_war", [_NATIONAL_ARMY], [_ANTI_TREATY], 1,
        "civil_war", ["rte_ucc_battle_dublin_1922"],
        ["rte_ucc_battle_dublin_1922"], ["ucc_atlas_irish_revolution"],
        "The contract covers the distinct O'Connell Street block fighting of 1–5 July 1922. The raw coordinate is not in Dublin and is withheld.",
    ),
    "hced-Delville Wood1916-1": _contract(
        "hced-Delville Wood1916-1", "wwi_south_african_formations", ["first_south_african_infantry_brigade_delville_1916"], ["german_empire"], 1,
        "interstate", ["nam_delville_wood_1916"],
        ["nam_delville_wood_1916"], ["national_army_museum"],
        "The contract is restricted to the South African brigade's capture and defence of Delville Wood, 15–20 July 1916, not the Somme parent or a September campaign envelope.",
    ),
    "hced-Gibeon1915-1": _contract(
        "hced-Gibeon1915-1", "wwi_south_african_formations", ["german_empire"], [_UDF_GSWA], 2,
        "interstate", ["samh_gibeon_1915", "nam_south_west_africa_campaign"],
        ["samh_gibeon_1915", "nam_south_west_africa_campaign"], ["south_african_military_history_society", "national_army_museum"],
        "The approach action began on 26 April and the main battle occurred on 27 April 1915. Direct sources establish a Union Defence Force victory, correcting HCED's German winner.",
        source_outcome_override=True,
    ),
    "hced-Salaita1916-1": _contract(
        "hced-Salaita1916-1", "wwi_south_african_formations", ["german_empire"], ["second_south_african_infantry_brigade_salaita_1916", "first_east_african_infantry_brigade_salaita_1916"], 1,
        "interstate", ["samh_salaita_1916", "kenya_gazette_salaita_heritage_2015"],
        ["samh_salaita_1916"], ["south_african_military_history_society"],
        "German and askari forces defeated the two exact opposing brigades at Salaita Hill on 12 February 1916. The unsafe raw point is withheld.",
    ),
    "hced-Sandfontein1914-1": _contract(
        "hced-Sandfontein1914-1", "wwi_south_african_formations", ["german_empire"], [_UDF_GSWA], 1,
        "interstate", ["samh_sandfontein_1914", "namibia_meft_sandfontein_heritage_2024"],
        ["samh_sandfontein_1914"], ["south_african_military_history_society"],
        "The German victory occurred at Sandfontein in German South West Africa on 26 September 1914. The raw point and South Africa country value identify a namesake and are withheld.",
    ),
}


_windhoek_hash, _windhoek_name, _windhoek_year = _ROW_DATA["hced-Windhoek1915-1"]
WAVE8_SOMALI_IRISH_SA_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Windhoek1915-1": {
        "raw_row_sha256": _windhoek_hash,
        "canonical_event": _canonical(_windhoek_name, _windhoek_year),
        "hold_category": "not_an_engagement_unopposed_occupation",
        "hold_reason": "Windhoek was occupied without combat on 12 May 1915. Territorial control is not converted into a tactical win.",
        "evidence_refs": ["historia_gswa_airpower_2017", "nam_south_west_africa_campaign"],
    }
}


WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS = frozenset(WAVE8_SOMALI_IRISH_SA_CONTRACTS)
WAVE8_SOMALI_IRISH_SA_HOLD_IDS = frozenset(WAVE8_SOMALI_IRISH_SA_HOLDS)
WAVE8_SOMALI_IRISH_SA_RESERVED_IDS = (
    WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS | WAVE8_SOMALI_IRISH_SA_HOLD_IDS
)


WAVE8_SOMALI_IRISH_SA_POINT_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Gumburu1903-1",
        "hced-O'Connell Street1922-1",
        "hced-Salaita1916-1",
        "hced-Sandfontein1914-1",
    }
)
WAVE8_SOMALI_IRISH_SA_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Gumburu1903-1",
        "hced-Illig1904-1",
        "hced-Sandfontein1914-1",
    }
)
WAVE8_SOMALI_IRISH_SA_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_SOMALI_IRISH_SA_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_SOMALI_IRISH_SA_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-106-38-480": {
        "hced_candidate_id": "hced-Sandfontein1914-1",
        "disposition": "deduplicate_to_hced",
        "relationship": "same_engagement_matching_outcome",
        "iwbd_date_start": "1914-09-26",
        "iwbd_date_end": "1914-09-26",
        "reason": "Exact Sandfontein twin with the same German tactical result; retain the source-reviewed HCED assertion and stage IWBD.",
    },
    "iwbd-106-38-533": {
        "hced_candidate_id": "hced-Gibeon1915-1",
        "disposition": "hold_contradictory_duplicate",
        "relationship": "probable_twin_conflicting_date_and_outcome",
        "iwbd_date_start": "1915-04-25",
        "iwbd_date_end": "1915-04-26",
        "reason": "IWBD's inconclusive 25–26 April record conflicts with the directly sourced 27 April Union Defence Force victory; stage IWBD rather than emit twice.",
    },
    "iwbd-106-38-547": {
        "hced_candidate_id": "hced-Windhoek1915-1",
        "disposition": "exclude_not_an_engagement",
        "relationship": "same_unopposed_occupation",
        "iwbd_date_start": "1915-05-12",
        "iwbd_date_end": "1915-05-12",
        "reason": "The occupation of Windhoek was unopposed and supplies no competitive tactical outcome in either source.",
    },
    "iwbd-106-38-602": {
        "hced_candidate_id": "hced-Salaita1916-1",
        "disposition": "deduplicate_to_hced",
        "relationship": "same_engagement_matching_outcome",
        "iwbd_date_start": "1916-02-12",
        "iwbd_date_end": "1916-02-12",
        "reason": "Exact Salaita Hill twin with the same German tactical result; retain the source-reviewed HCED assertion and stage IWBD.",
    },
    "iwbd-106-38-636": {
        "hced_candidate_id": "hced-Delville Wood1916-1",
        "disposition": "hold_campaign_envelope_containment",
        "relationship": "broader_campaign_envelope_contains_hced_engagement",
        "iwbd_date_start": "1916-07-15",
        "iwbd_date_end": "1916-09-03",
        "reason": "IWBD spans a broad Delville Wood campaign envelope containing the 15–20 July HCED engagement; stage the envelope to prevent double rating.",
    },
}


WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Gibeon1915-1": {
        "raw_winner_label": "Germany",
        "raw_loser_label": "South Africa",
        "corrected_winner_side": 2,
        "corrected_winner_entity_ids": [_UDF_GSWA],
        "outcome_source_ids": ["nam_south_west_africa_campaign", "samh_gibeon_1915"],
        "outcome_source_family_ids": ["national_army_museum", "south_african_military_history_society"],
        "correction_note": "Direct campaign histories establish the Union Defence Force as the tactical victor at Gibeon on 27 April 1915.",
    }
}
# Descriptive alias for callers that prefer the longer export name.
WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDE_METADATA = (
    WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def wave8_somali_irish_sa_audit_signature() -> str:
    payload = {
        "contracts": WAVE8_SOMALI_IRISH_SA_CONTRACTS,
        "holds": WAVE8_SOMALI_IRISH_SA_HOLDS,
        "entities": WAVE8_SOMALI_IRISH_SA_ENTITIES,
        "sources": WAVE8_SOMALI_IRISH_SA_SOURCES,
        "point_quarantine_additions": sorted(
            WAVE8_SOMALI_IRISH_SA_POINT_QUARANTINE_ADDITIONS
        ),
        "country_quarantine_additions": sorted(
            WAVE8_SOMALI_IRISH_SA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "iwbd_duplicate_dispositions": WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS,
        "outcome_overrides": WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES,
    }
    return hashlib.sha256(_canonical_json(payload).encode()).hexdigest()


def _validate_static() -> None:
    if (len(WAVE8_SOMALI_IRISH_SA_CONTRACTS), len(WAVE8_SOMALI_IRISH_SA_HOLDS)) != (17, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_SOMALI_IRISH_SA_ENTITIES), len(WAVE8_SOMALI_IRISH_SA_SOURCES)) != (7, 21):
        raise ValueError(f"{_LANE_NAME} entity/source inventory changed")
    if wave8_somali_irish_sa_audit_signature() != WAVE8_SOMALI_IRISH_SA_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")
    if WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS & WAVE8_SOMALI_IRISH_SA_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion and hold inventories overlap")

    source_ids = {str(source["id"]) for source in WAVE8_SOMALI_IRISH_SA_SOURCES}
    entity_ids = {str(entity["id"]) for entity in WAVE8_SOMALI_IRISH_SA_ENTITIES}
    if len(source_ids) != 21 or len(entity_ids) != 7:
        raise ValueError(f"{_LANE_NAME} duplicate fixture ID")
    forbidden = {
        "clio_q1045_1960_b5c3f32e",
        "clio_sa_south_africa_rep_1932_8a5c7c70",
        "clio_ei_ireland_rep_1922_855f2448",
    }
    if entity_ids & forbidden:
        raise ValueError(f"{_LANE_NAME} inherited a forbidden modern identity")
    for entity in WAVE8_SOMALI_IRISH_SA_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback: {entity['id']}")
        if not set(entity["source_ids"]) <= source_ids:
            raise ValueError(f"{_LANE_NAME} identity has an unknown source: {entity['id']}")
        if "No rating is inherited" not in entity["continuity_note"]:
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall: {entity['id']}")

    for item in [
        *WAVE8_SOMALI_IRISH_SA_CONTRACTS.values(),
        *WAVE8_SOMALI_IRISH_SA_HOLDS.values(),
    ]:
        if not set(item["evidence_refs"]) <= source_ids:
            raise ValueError(f"{_LANE_NAME} disposition has an unknown source")
    overrides = {
        candidate_id
        for candidate_id, contract in WAVE8_SOMALI_IRISH_SA_CONTRACTS.items()
        if contract["source_outcome_override"]
    }
    if overrides != set(WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES):
        raise ValueError(f"{_LANE_NAME} outcome override manifest drift")
    for candidate_id, metadata in WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES.items():
        contract = WAVE8_SOMALI_IRISH_SA_CONTRACTS[candidate_id]
        if (
            metadata["corrected_winner_side"] != contract["winner_side"]
            or metadata["outcome_source_ids"] != contract["outcome_source_ids"]
            or metadata["outcome_source_family_ids"]
            != contract["outcome_source_family_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome override metadata drift")
    if not (
        WAVE8_SOMALI_IRISH_SA_POINT_QUARANTINE_ADDITIONS
        | WAVE8_SOMALI_IRISH_SA_COUNTRY_QUARANTINE_ADDITIONS
    ) <= WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location quarantine references a non-promotion")
    if len(WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS) != 5:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    if not {
        disposition["hced_candidate_id"]
        for disposition in WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS.values()
    } <= WAVE8_SOMALI_IRISH_SA_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} IWBD disposition has an unknown HCED row")


def validate_wave8_somali_irish_sa_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SOMALI_IRISH_SA_CONTRACTS,
        WAVE8_SOMALI_IRISH_SA_HOLDS,
        lane_name=_LANE_NAME,
    )


def install_wave8_somali_irish_sa_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SOMALI_IRISH_SA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_somali_irish_sa_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SOMALI_IRISH_SA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SOMALI_IRISH_SA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SOMALI_IRISH_SA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_somali_irish_sa_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_somali_irish_sa_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SOMALI_IRISH_SA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix="hced_wave8_somali_irish_sa_",
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_somali_irish_sa_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_SOMALI_IRISH_SA_CONTRACTS.values()
            ).items()
        )
    )


def wave8_somali_irish_sa_counts() -> dict[str, int]:
    return {
        "holds": len(WAVE8_SOMALI_IRISH_SA_HOLDS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_SOMALI_IRISH_SA_ENTITIES),
        "new_sources": len(WAVE8_SOMALI_IRISH_SA_SOURCES),
        "newly_rated_events": len(WAVE8_SOMALI_IRISH_SA_CONTRACTS),
        "outcome_overrides": len(WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES),
        "promotion_contracts": len(WAVE8_SOMALI_IRISH_SA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_SOMALI_IRISH_SA_RESERVED_IDS),
    }
