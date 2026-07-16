"""Candidate-keyed Wave 8 contracts for North American frontier conflicts."""

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


WAVE8_NORTH_AMERICA_FINAL_AUDIT_SIGNATURE = (
    "fb0fecb1ec2ff5c56c99a5d0d5f36645de03ff7bbf90d357897430ac5ee04a00"
)

WAVE8_NORTH_AMERICA_SOURCES: tuple[dict[str, Any], ...] = (
    {"id": "nps_grattan_1854", "title": "War on the Oregon & California Trails", "url": "https://www.nps.gov/articles/000/war-on-the-oregon-california-trails.htm", "publisher": "U.S. National Park Service", "license": "US government work", "source_type": "government_history", "accessed": "2026-07-16", "source_family_id": "us_national_park_service", "evidence_roles": ["identity_boundary_or_context_reference"]},
    {"id": "mnhs_us_dakota_war_1862", "title": "During the War: The U.S.–Dakota War of 1862", "url": "https://www3.mnhs.org/history/war/during-war", "publisher": "Minnesota Historical Society", "license": "linked_reference", "source_type": "museum_history", "accessed": "2026-07-16", "source_family_id": "minnesota_historical_society", "evidence_roles": ["identity_boundary_or_context_reference"]},
    {"id": "mnhs_birch_coulee_1862", "title": "Mni Sota Wakpa: Birch Coulee", "url": "https://www.mnhs.org/usdakotawar/river-stories", "publisher": "Minnesota Historical Society", "license": "linked_reference", "source_type": "museum_history", "accessed": "2026-07-16", "source_family_id": "minnesota_historical_society", "evidence_roles": ["outcome", "identity_boundary_or_context_reference"]},
    {"id": "nps_inkpaduta", "title": "Inkpaduta", "url": "https://www.nps.gov/people/inkpaduta.htm", "publisher": "U.S. National Park Service", "license": "US government work", "source_type": "government_history", "accessed": "2026-07-16", "source_family_id": "us_national_park_service", "evidence_roles": ["identity_boundary_or_context_reference"]},
    {"id": "nps_whitestone_hill", "title": "Whitestone Hill battle detail", "url": "https://www.nps.gov/civilwar/search-battles-detail.htm?battleCode=nd004", "publisher": "U.S. National Park Service", "license": "US government work", "source_type": "government_history", "accessed": "2026-07-16", "source_family_id": "us_national_park_service", "evidence_roles": ["identity_boundary_or_context_reference"]},
    {"id": "nps_red_cloud_war", "title": "Settlement of the Upper Missouri", "url": "https://www.nps.gov/jeff/planyourvisit/settlement-of-the-upper-missouri.htm", "publisher": "U.S. National Park Service", "license": "US government work", "source_type": "government_history", "accessed": "2026-07-16", "source_family_id": "us_national_park_service", "evidence_roles": ["identity_boundary_or_context_reference"]},
    {"id": "army_indian_wars_summary", "title": "Army Campaigns: Indian Wars", "url": "https://history.army.mil/Research/Reference-Topics/Army-Campaigns/Brief-Summaries/Indian-Wars/", "publisher": "U.S. Army Center of Military History", "license": "US government work", "source_type": "official_history", "accessed": "2026-07-16", "source_family_id": "us_army_center_military_history", "evidence_roles": ["identity_boundary_or_context_reference"]},
    {"id": "nps_great_sioux_war", "title": "Fighting for the Black Hills: Indigenous Perspectives on the Great Sioux War", "url": "https://home.nps.gov/articles/000/fighting-for-the-black-hills-understanding-indigenous-perspectives-on-the-great-sioux-war-of-1876-1877.htm", "publisher": "U.S. National Park Service", "license": "US government work", "source_type": "government_history", "accessed": "2026-07-16", "source_family_id": "us_national_park_service", "evidence_roles": ["identity_boundary_or_context_reference"]},
    {"id": "nps_apache_pass_1862", "title": "Battle of Apache Pass", "url": "https://www.nps.gov/fobo/learn/historyculture/the-battle-of-apache-pass.htm", "publisher": "U.S. National Park Service", "license": "US government work", "source_type": "government_history", "accessed": "2026-07-16", "source_family_id": "us_national_park_service", "evidence_roles": ["outcome", "identity_boundary_or_context_reference"]},
    {"id": "nps_apache_wars_cochise", "title": "The Apache Wars Part I: Cochise", "url": "https://www.nps.gov/chir/learn/historyculture/apache-wars-cochise.htm", "publisher": "U.S. National Park Service", "license": "US government work", "source_type": "government_history", "accessed": "2026-07-16", "source_family_id": "us_national_park_service", "evidence_roles": ["identity_boundary_or_context_reference"]},
    {"id": "nps_fort_bowie_handbook", "title": "Fort Bowie National Historic Site historical handbook", "url": "https://www.nps.gov/parkhistory/online_books/fobo/utley.pdf", "publisher": "U.S. National Park Service", "license": "US government work", "source_type": "official_history", "accessed": "2026-07-16", "source_family_id": "us_national_park_service", "evidence_roles": ["outcome", "identity_boundary_or_context_reference"]},
    {"id": "army_upress_big_dry_wash_1882", "title": "The Battle of Big Dry Wash: Arizona's Last Great Apache Fight", "url": "https://www.armyupress.army.mil/Portals/7/educational-services/staff-rides/3_Battle_of_Big_Dry_Washpdf.pdf", "publisher": "U.S. Army University Press", "license": "linked scholarly reference", "source_type": "official_military_education", "accessed": "2026-07-16", "source_family_id": "us_army_university_press", "evidence_roles": ["outcome", "identity_boundary_or_context_reference"]},
    {"id": "army_cmh_victorio_campaign_1880", "title": "The Victorio Campaign", "url": "https://history.army.mil/portals/143/Images/Publications/catalog/70-111-1.pdf", "publisher": "U.S. Army Center of Military History", "license": "US government work", "source_type": "official_history", "accessed": "2026-07-16", "source_family_id": "us_army_center_military_history", "evidence_roles": ["outcome", "identity_boundary_or_context_reference"]},
    {"id": "nps_tonto_apache_war", "title": "Tonto Apache War", "url": "https://www.nps.gov/tont/learn/historyculture/tonto-apache-war.htm", "publisher": "U.S. National Park Service", "license": "US government work", "source_type": "government_history", "accessed": "2026-07-16", "source_family_id": "us_national_park_service", "evidence_roles": ["identity_boundary_or_context_reference"]},
    {"id": "army_history_cieneguilla_1854", "title": "Army History 77: Cieneguilla battlefield review", "url": "https://history.army.mil/Portals/143/Images/Publications/ArmyHistoryMag/pdf/20102019/AH77%28W%29.pdf", "publisher": "U.S. Army Center of Military History", "license": "US government work", "source_type": "official_history", "accessed": "2026-07-16", "source_family_id": "us_army_center_military_history", "evidence_roles": ["identity_boundary_or_context_reference"]},
)


def _entity(entity_id: str, name: str, kind: str, start: int, end: int, sources: list[str], context: str) -> dict[str, Any]:
    return {"id": entity_id, "name": name, "kind": kind, "start_year": start, "end_year": end, "region": "North America", "aliases": [], "predecessors": [], "continuity_note": context + " No rating is inherited by an umbrella ethnonym or a later tribal identity.", "source_ids": sources}


WAVE8_NORTH_AMERICA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity("brule_lakota_grattan_camp_1854", "Brulé Lakota camp in the Grattan fight", "indigenous_camp_force", 1854, 1854, ["nps_grattan_1854"], "Exact Brulé Lakota camp attacked by Lieutenant Grattan's detachment."),
    _entity("mdewakanton_wahpekute_resistance_1862", "Mdewakanton–Wahpekute resistance forces (1862)", "indigenous_coalition", 1862, 1862, ["mnhs_us_dakota_war_1862", "mnhs_birch_coulee_1862"], "Conflict-bounded Dakota forces, primarily Mdewakanton and Wahpekute, in the U.S.–Dakota War."),
    _entity("dakota_lakota_resistance_1863", "Dakota–Lakota resistance forces (1863–1864)", "indigenous_coalition", 1863, 1864, ["nps_inkpaduta", "nps_whitestone_hill"], "Campaign-bounded forces encountered by the Sibley and Sully expeditions; this does not imply one permanent nation or command."),
    _entity("red_cloud_plains_coalition_1866", "Red Cloud's Lakota–Cheyenne–Arapaho coalition", "indigenous_coalition", 1866, 1868, ["nps_red_cloud_war"], "Conflict-bounded coalition opposing the Bozeman Trail forts during Red Cloud's War."),
    _entity("lakota_northern_cheyenne_coalition_1876", "Lakota–Northern Cheyenne coalition (1876–1877)", "indigenous_coalition", 1876, 1877, ["army_indian_wars_summary", "nps_great_sioux_war"], "Conflict-bounded non-reservation coalition in the Great Sioux War."),
    _entity("cochise_mangas_chiricahua_coalition_1862", "Cochise–Mangas Chiricahua coalition at Apache Pass", "indigenous_coalition", 1862, 1862, ["nps_apache_pass_1862", "nps_apache_wars_cochise"], "Engagement-bounded Chokonen, Chihenne, and Bedonkohe force led by Cochise and Mangas Coloradas at Apache Pass."),
    _entity("cochise_chiricahua_force_1869", "Cochise's Chiricahua force (1869)", "indigenous_war_band", 1869, 1869, ["nps_apache_wars_cochise"], "Conflict-year identity for Cochise's Chiricahua resistance during the 1861–1872 war; it is not a generic Apache polity."),
    _entity("cibecue_apache_resistance_1881", "Cibecue Apache resistance force (1881)", "indigenous_coalition", 1881, 1881, ["nps_fort_bowie_handbook"], "Engagement-bounded warriors and mutinous Apache scouts who fought Carr's command at Cibecue Creek."),
    _entity("natiotish_apache_band_1882", "Natiotish's Apache band (1882)", "indigenous_war_band", 1882, 1882, ["army_upress_big_dry_wash_1882"], "Exact band led by Natiotish at Big Dry Wash; the source records uncertainty between White Mountain and Tonto affiliation, so neither broader identity is asserted."),
    _entity("victorio_mimbres_apache_band_1879", "Victorio's Mimbres Apache band (1879–1880)", "indigenous_war_band", 1879, 1880, ["army_cmh_victorio_campaign_1880"], "Campaign-bounded Mimbres/Chihenne force led by Victorio; it does not inherit ratings from other Chiricahua or Apache groups."),
    _entity("terrazas_tarahumara_auxiliaries_1880", "Terrazas's Tarahumara auxiliaries at Tres Castillos", "indigenous_auxiliary_force", 1880, 1880, ["army_cmh_victorio_campaign_1880"], "Engagement-bounded Tarahumara component of Colonel Joaquin Terrazas's Mexican column at Tres Castillos."),
)


def _canonical(name: str, low: int, high: int | None = None) -> dict[str, Any]:
    high = low if high is None else high
    return {"canonical_key": f"{_slug(name)}:{low}:{high}", "date_precision": "year", "granularity": "engagement", "name": name, "year_low": low, "year_high": high}


_ROW_DATA = {
    "hced-Big Mound1863-1": ("8410f62db5192e10f87e85098b2258c0f40def4b4baf6e6d2306bb27747f6d8c", "Big Mound", 1863, 1863),
    "hced-Birch Coulee1862-1": ("43a98db343411c93b2e56cac327176445d1ca5e91ff25d5048c3f2571003017f", "Birch Coulee", 1862, 1862),
    "hced-Dead Buffalo Lake1863-1": ("fb48d548915ef857bf72b5a94dfb4ee65cdc7ac0429d5a59a188d41528ae3fb1", "Dead Buffalo Lake", 1863, 1863),
    "hced-Fetterman Massacre1866-1": ("dd2067c4fb7b8bfae57cc0e61ca70d9ff8be259b50b11aff6017466560a5d5b9", "Fetterman Fight", 1866, 1866),
    "hced-Fort Laramie1854-1": ("d033d3e6988b66fd67daa5f59a3042758162124bf371c8becf6d086942fb6d62", "Grattan Fight", 1854, 1854),
    "hced-Fort Phil Kearney1866-1867-1": ("37e3ab1e924c562970d4cfc21de231048044e2a23b9348c82f1cc50621afbd37", "Fort Phil Kearny operations", 1866, 1867),
    "hced-Fort Ridgely1862-1": ("3b9d7b74e968e125f41b74a16c47b9b6da94fc0b77d55cb609084d81af9a9bf4", "Fort Ridgely", 1862, 1862),
    "hced-Killdeer Mountain1864-1": ("7c2a5bc62a3ea3ae0b17b72a10146a1397e4c07c64c43d8ba1042360a8ca3fc3", "Killdeer Mountain", 1864, 1864),
    "hced-Little Big Horn1876-1": ("ac43bd8a2c07c94000c833b7937fa8f86b969586ba5f8c9fde097f48ecbfdde4", "Little Bighorn", 1876, 1876),
    "hced-Muddy Creek1877-1": ("db70ce09ca19cafa5a7a33c25edef8faa32fda4aee04022db098de02d94b0022", "Muddy Creek", 1877, 1877),
    "hced-New Ulm1862-1": ("f7d86340da10d5e823eb812d2127bf6b32758f75b084da61b51ec545e1f7d870", "New Ulm", 1862, 1862),
    "hced-Rosebud1876-1": ("e3dab12a61aea24e4f61b61487835c803ba2f1e49054a77a844febdad2847e06", "Rosebud", 1876, 1876),
    "hced-Slim Buttes1876-1": ("413fe9f50b6a5d3d4fc3d0377b4967388f6451b62a98674411b84114d489b05b", "Slim Buttes", 1876, 1876),
    "hced-Spirit Lake1857-1": ("7a517d87374d71f03e6efed924682950c4e4ae9fea010610c1da747852ccfeb7", "Spirit Lake", 1857, 1857),
    "hced-Stony Lake1863-1": ("48e5f3bd0267bb2af258fbee1c8ac0304434db7b4697d5e592c8b25ec3cbd827", "Stony Lake", 1863, 1863),
    "hced-Whitestone Hill1863-1": ("6b63276eb9c57f95e1ed21c6de62d1ab960aa2121a41003c3631c6032333f60d", "Whitestone Hill", 1863, 1863),
    "hced-Wolf Mountain1877-1": ("83f6d8412a395ac5dbf82eab8c4f8201be3f8deb9cdef13c8f55dc34e0cd74ed", "Wolf Mountain", 1877, 1877),
    "hced-Wounded Knee Creek1890-1": ("a03c5b14d0dbfb16d1eed61e1017377a38aeab0e17b7279a675e305bc9d33d17", "Wounded Knee Creek", 1890, 1890),
    "hced-Apache Pass1862-1": ("563fc1049f70a45eb0019eff24a3aafc16d5b9ba3b40cba829c9498dd58066db", "Apache Pass", 1862, 1862),
    "hced-Arizpe1852-1": ("6b35583b7d1c88cfb65bcaa40c7c5ebb47f2f1b36ffe2ca650f761be9bd0c5f8", "Arizpe", 1852, 1852),
    "hced-Big Dry Wash1882-1": ("e511c605f4c7a268627ec016be4ed3918e7e5b5fc5d59f78ddefeec96e0957ac", "Big Dry Wash", 1882, 1882),
    "hced-Bloody Tanks1864-1": ("e725138660de795359c9f4a8b2a101b1e4c43c88c5a81ab70ed205a621dea42c", "Bloody Tanks", 1864, 1864),
    "hced-Canon de Ugalde1790-1": ("eb898e6e9ae3c11830d6245a85534c038b950ef46aa9f10c475cbe9ced553f6e", "Canon de Ugalde", 1790, 1790),
    "hced-Canyon of the Dead Sheep1857-1": ("2ba22fa3346750475b3963239dd16a4560a865765c89bab17e5ec5d1f4d8b551", "Canyon of the Dead Sheep", 1857, 1857),
    "hced-Chiricahua Pass1869-1": ("918d98f018d13faf6502d0aa16544dea6c217d8d923441c78a21fd17b6ec553b", "Chiricahua Pass", 1869, 1869),
    "hced-Cibecue Creek1881-1": ("521ec820b8a9f8cbe2d70ed19f0e81b3c13aa68e547b2c68e7fb269bac921193", "Cibecue Creek", 1881, 1881),
    "hced-Cieneguilla1854-1": ("6277589d940190b3e8f6e1d5c13e49b75c5a22f8d999860b6e8b6fb97e5daac3", "Cieneguilla", 1854, 1854),
    "hced-Diablo Mountains1854-1": ("c1cb61056a6fb14446803c7860fb3db620d882bcfab5111afe1fd20c43fe65a3", "Diablo Mountains", 1854, 1854),
    "hced-Gila River1857-1": ("37f2dfdf448046fb12ef4a9735d4a751df7534c7743c55e4824759d811253d64", "Gila River", 1857, 1857),
    "hced-Janos Massacre1851-1": ("c4aede561f559406f3120a3552c7de9ddd1b14831998bd72fbc22f8b5b62c194", "Janos Massacre", 1851, 1851),
    "hced-Pinos Altos1861-1": ("02be400b62127e119504d33f6dfd139599308e0e1edef8db61f8fba64e751ed4", "Pinos Altos", 1861, 1861),
    "hced-Rattlesnake Springs1880-1": ("4362b10022275804ff122f5cdcceeff59cde728ad9ef3a27369d7c44647c19a6", "Rattlesnake Springs", 1880, 1880),
    "hced-Rio Caliente1854-1": ("43a727006a92ef8994c92913341d199041de92a9569c069ea97c61ce992d977f", "Rio Caliente", 1854, 1854),
    "hced-Skeleton Cave1872-1": ("d98f32995dcaeb3fab8c3df7579bafd6ec917425a000fefaf7ae489a1ca0fb30", "Skeleton Cave", 1872, 1872),
    "hced-Tinaja las Palmas1880-1": ("09dd979127b05afebca729b62b4f2484d17a16d2b525fe0a2f6a5183e861af3d", "Tinaja de Las Palmas", 1880, 1880),
    "hced-Tres Castillos1880-1": ("5efa31720c41bb0c1b2059c1db4520f895780a021ac4d52fdb24d1d03fc5d0fc", "Tres Castillos", 1880, 1880),
    "hced-Turret Butte1873-1": ("b0d164f347dacb959778eeeb06343c0707742c476f3fd3b6dc90d3e42c7dae76", "Turret Butte", 1873, 1873),
}


def _contract(candidate_id: str, cohort: str, actor: str, actor_side: int, winner: int, evidence: list[str], note: str, *, override: bool = False) -> dict[str, Any]:
    row_hash, name, low, high = _ROW_DATA[candidate_id]
    result = {"raw_row_sha256": row_hash, "canonical_event": _canonical(name, low, high), "cohort": cohort, "side_1_entity_ids": [actor] if actor_side == 1 else ["united_states"], "side_2_entity_ids": [actor] if actor_side == 2 else ["united_states"], "winner_side": winner, "evidence_refs": evidence, "audit_note": note, "source_outcome_override": override}
    if override:
        result["outcome_source_ids"] = evidence
        result["outcome_source_family_ids"] = ["minnesota_historical_society"]
    return result


WAVE8_NORTH_AMERICA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Fort Laramie1854-1": _contract("hced-Fort Laramie1854-1", "grattan_1854", "brule_lakota_grattan_camp_1854", 1, 1, ["nps_grattan_1854"], "The generic labels are narrowed to the documented Brulé Lakota camp and Grattan fight."),
    "hced-Fort Ridgely1862-1": _contract("hced-Fort Ridgely1862-1", "dakota_1862", "mdewakanton_wahpekute_resistance_1862", 2, 1, ["mnhs_us_dakota_war_1862"], "Exact U.S.–Dakota War actor binding."),
    "hced-New Ulm1862-1": _contract("hced-New Ulm1862-1", "dakota_1862", "mdewakanton_wahpekute_resistance_1862", 2, 1, ["mnhs_us_dakota_war_1862"], "Exact U.S.–Dakota War actor binding."),
    "hced-Birch Coulee1862-1": _contract("hced-Birch Coulee1862-1", "dakota_1862", "mdewakanton_wahpekute_resistance_1862", 2, 2, ["mnhs_birch_coulee_1862"], "Minnesota Historical Society documents a major Dakota victory, correcting HCED's reversed orientation.", override=True),
    "hced-Big Mound1863-1": _contract("hced-Big Mound1863-1", "dakota_lakota_1863_1864", "dakota_lakota_resistance_1863", 2, 1, ["nps_inkpaduta"], "Campaign-bounded Dakota–Lakota identity."),
    "hced-Dead Buffalo Lake1863-1": _contract("hced-Dead Buffalo Lake1863-1", "dakota_lakota_1863_1864", "dakota_lakota_resistance_1863", 2, 1, ["nps_inkpaduta"], "Campaign-bounded Dakota–Lakota identity."),
    "hced-Stony Lake1863-1": _contract("hced-Stony Lake1863-1", "dakota_lakota_1863_1864", "dakota_lakota_resistance_1863", 2, 1, ["nps_inkpaduta"], "Campaign-bounded Dakota–Lakota identity."),
    "hced-Killdeer Mountain1864-1": _contract("hced-Killdeer Mountain1864-1", "dakota_lakota_1863_1864", "dakota_lakota_resistance_1863", 2, 1, ["nps_inkpaduta"], "Campaign-bounded Dakota–Lakota identity."),
    "hced-Fetterman Massacre1866-1": _contract("hced-Fetterman Massacre1866-1", "red_cloud_war", "red_cloud_plains_coalition_1866", 1, 1, ["nps_red_cloud_war"], "The term massacre is normalized to the documented Fetterman military engagement; both sides were armed combatants."),
    "hced-Fort Phil Kearney1866-1867-1": _contract("hced-Fort Phil Kearney1866-1867-1", "red_cloud_war", "red_cloud_plains_coalition_1866", 2, 1, ["nps_red_cloud_war"], "Conflict-bounded Red Cloud coalition binding."),
    "hced-Little Big Horn1876-1": _contract("hced-Little Big Horn1876-1", "great_sioux_war", "lakota_northern_cheyenne_coalition_1876", 1, 1, ["nps_great_sioux_war", "army_indian_wars_summary"], "Conflict-bounded Lakota–Northern Cheyenne coalition binding."),
    "hced-Rosebud1876-1": _contract("hced-Rosebud1876-1", "great_sioux_war", "lakota_northern_cheyenne_coalition_1876", 1, 1, ["army_indian_wars_summary", "nps_great_sioux_war"], "HCED's tactical assertion is retained while the exact coalition replaces the umbrella label."),
    "hced-Slim Buttes1876-1": _contract("hced-Slim Buttes1876-1", "great_sioux_war", "lakota_northern_cheyenne_coalition_1876", 2, 1, ["army_indian_wars_summary", "nps_great_sioux_war"], "Conflict-bounded Lakota–Northern Cheyenne coalition binding."),
    "hced-Muddy Creek1877-1": _contract("hced-Muddy Creek1877-1", "great_sioux_war", "lakota_northern_cheyenne_coalition_1876", 2, 1, ["army_indian_wars_summary", "nps_great_sioux_war"], "Conflict-bounded Lakota–Northern Cheyenne coalition binding."),
    "hced-Wolf Mountain1877-1": _contract("hced-Wolf Mountain1877-1", "great_sioux_war", "lakota_northern_cheyenne_coalition_1876", 2, 1, ["army_indian_wars_summary", "nps_great_sioux_war"], "Conflict-bounded Lakota–Northern Cheyenne coalition binding."),
    "hced-Apache Pass1862-1": _contract("hced-Apache Pass1862-1", "apache_pass_1862", "cochise_mangas_chiricahua_coalition_1862", 2, 1, ["nps_apache_pass_1862", "nps_apache_wars_cochise"], "The NPS identifies Cochise's Chokonen force and Mangas Coloradas's Chihenne and Bedonkohe bands and records an Army tactical victory."),
    "hced-Chiricahua Pass1869-1": _contract("hced-Chiricahua Pass1869-1", "cochise_war_1869", "cochise_chiricahua_force_1869", 1, 1, ["nps_apache_wars_cochise"], "The conflict-year identity is limited to Cochise's Chiricahua resistance and does not create a general Apache polity."),
    "hced-Cibecue Creek1881-1": _contract("hced-Cibecue Creek1881-1", "cibecue_1881", "cibecue_apache_resistance_1881", 2, 1, ["nps_fort_bowie_handbook"], "The NPS handbook identifies the engagement-bounded warriors and mutinous scouts and records Carr's command repulsing the attack."),
    "hced-Big Dry Wash1882-1": _contract("hced-Big Dry Wash1882-1", "big_dry_wash_1882", "natiotish_apache_band_1882", 2, 1, ["army_upress_big_dry_wash_1882"], "The Army-hosted study identifies Natiotish's band and explicitly concludes that the Army won a tactical victory."),
    "hced-Rattlesnake Springs1880-1": _contract("hced-Rattlesnake Springs1880-1", "victorio_campaign_1880", "victorio_mimbres_apache_band_1879", 2, 1, ["army_cmh_victorio_campaign_1880"], "The Army Center of Military History identifies Victorio's Mimbres force and the cavalry's successful denial of the water source."),
    "hced-Tinaja las Palmas1880-1": _contract("hced-Tinaja las Palmas1880-1", "victorio_campaign_1880", "victorio_mimbres_apache_band_1879", 2, 1, ["army_cmh_victorio_campaign_1880"], "The Army Center of Military History identifies Victorio's Mimbres force and describes the tactical defeat that forced its retreat."),
    "hced-Tres Castillos1880-1": {
        "raw_row_sha256": _ROW_DATA["hced-Tres Castillos1880-1"][0],
        "canonical_event": _canonical("Tres Castillos", 1880),
        "cohort": "victorio_campaign_1880",
        "side_1_entity_ids": ["clio_mx_mexico_1_1868_ffbcfbae", "terrazas_tarahumara_auxiliaries_1880"],
        "side_2_entity_ids": ["victorio_mimbres_apache_band_1879"],
        "winner_side": 1,
        "evidence_refs": ["army_cmh_victorio_campaign_1880"],
        "audit_note": "The Army Center of Military History contradicts HCED's draw: Terrazas's Mexican column, including a Tarahumara sharpshooter, surrounded and destroyed Victorio's force.",
        "source_outcome_override": True,
        "outcome_source_ids": ["army_cmh_victorio_campaign_1880"],
        "outcome_source_family_ids": ["us_army_center_military_history"],
    },
}

WAVE8_NORTH_AMERICA_HOLDS = {}
for _candidate_id, _category, _reason, _evidence in (
    ("hced-Spirit Lake1857-1", "massacre_without_competitive_outcome", "The Inkpaduta raid killed settlers and took captives; it is not converted into a battlefield victory.", ["nps_inkpaduta"]),
    ("hced-Whitestone Hill1863-1", "civilian_camp_and_belligerency_ambiguous", "The attack struck a large camp containing families and people not shown to be 1862 belligerents; one generic opponent identity would invent participation.", ["nps_whitestone_hill"]),
    ("hced-Wounded Knee Creek1890-1", "massacre_without_competitive_outcome", "HCED itself supplies only a Massacre marker and no competitive result; unknown is never a draw or victory.", ["nps_great_sioux_war"]),
    ("hced-Arizpe1852-1", "umbrella_identity_unresolved", "The row supplies only an Apache umbrella label; no exact band or coalition has been established for this engagement.", ["nps_apache_wars_cochise"]),
    ("hced-Bloody Tanks1864-1", "coalition_and_identity_unresolved", "The winning U.S.–Pima–Maricopa coalition and exact opposing Apache group require engagement-specific corroboration before rating.", []),
    ("hced-Canon de Ugalde1790-1", "colonial_actor_and_identity_unresolved", "The row's 1790 label Mexico is anachronistic for New Spain and the exact Apache force is unresolved.", []),
    ("hced-Canyon of the Dead Sheep1857-1", "umbrella_identity_unresolved", "The exact Apache local group or war band is not identified by the reviewed official sources.", []),
    ("hced-Cieneguilla1854-1", "outcome_and_coalition_require_adjudication", "The row's Apache-win label and the reviewed Army summary disagree, while accounts vary on Jicarilla and Ute participation; no result is invented.", ["army_history_cieneguilla_1854"]),
    ("hced-Diablo Mountains1854-1", "umbrella_identity_unresolved", "The exact Apache local group or war band is not identified by the reviewed official sources.", []),
    ("hced-Gila River1857-1", "umbrella_identity_unresolved", "The exact Apache local group or war band is not identified by the reviewed official sources.", []),
    ("hced-Janos Massacre1851-1", "massacre_without_competitive_outcome", "HCED supplies a massacre marker rather than a winner and loser; unknown is never converted to a draw or victory.", []),
    ("hced-Pinos Altos1861-1", "umbrella_identity_unresolved", "The exact Apache force opposed by Confederate Arizona troops is not established by the reviewed official sources.", ["nps_apache_wars_cochise"]),
    ("hced-Rio Caliente1854-1", "umbrella_identity_unresolved", "The exact Apache local group or war band is not identified by the reviewed official sources.", []),
    ("hced-Skeleton Cave1872-1", "massacre_and_identity_contested", "The NPS records women, children, and elders among those killed and notes conflicting Tonto Apache and Yavapai identifications; it is not rated as a competitive battle.", ["nps_tonto_apache_war"]),
    ("hced-Turret Butte1873-1", "umbrella_identity_unresolved", "The exact Tonto Apache or Yavapai force is not established for this row; the broader campaign identity cannot substitute for it.", ["nps_tonto_apache_war"]),
):
    _hash, _name, _low, _high = _ROW_DATA[_candidate_id]
    WAVE8_NORTH_AMERICA_HOLDS[_candidate_id] = {"raw_row_sha256": _hash, "canonical_event": _canonical(_name, _low, _high), "hold_category": _category, "hold_reason": _reason, "evidence_refs": _evidence}

WAVE8_NORTH_AMERICA_CONTRACT_IDS = frozenset(WAVE8_NORTH_AMERICA_CONTRACTS)
WAVE8_NORTH_AMERICA_HOLD_IDS = frozenset(WAVE8_NORTH_AMERICA_HOLDS)
WAVE8_NORTH_AMERICA_RESERVED_IDS = WAVE8_NORTH_AMERICA_CONTRACT_IDS | WAVE8_NORTH_AMERICA_HOLD_IDS


def _audit_signature() -> str:
    lines = []
    for disposition, inventory in (("promote", WAVE8_NORTH_AMERICA_CONTRACTS), ("hold", WAVE8_NORTH_AMERICA_HOLDS)):
        for candidate_id, contract in sorted(inventory.items()):
            lines.append(f"{disposition}|{candidate_id}|{contract['raw_row_sha256']}|{contract['canonical_event']['canonical_key']}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


def _validate_static() -> None:
    if len(WAVE8_NORTH_AMERICA_CONTRACTS) != 22 or len(WAVE8_NORTH_AMERICA_HOLDS) != 15:
        raise ValueError("Wave 8 North America disposition inventory changed")
    if len(WAVE8_NORTH_AMERICA_ENTITIES) != 11 or len(WAVE8_NORTH_AMERICA_SOURCES) != 15:
        raise ValueError("Wave 8 North America identity/source inventory changed")
    if _audit_signature() != WAVE8_NORTH_AMERICA_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 North America final audit signature changed")
    source_ids = {source["id"] for source in WAVE8_NORTH_AMERICA_SOURCES}
    for entity in WAVE8_NORTH_AMERICA_ENTITIES:
        if entity["aliases"] or entity["predecessors"] or "No rating" not in entity["continuity_note"]:
            raise ValueError(f"Wave 8 North America identity invariant failed: {entity['id']}")
        if not set(entity["source_ids"]) <= source_ids:
            raise ValueError(f"Wave 8 North America unknown entity source: {entity['id']}")
    for contract in [*WAVE8_NORTH_AMERICA_CONTRACTS.values(), *WAVE8_NORTH_AMERICA_HOLDS.values()]:
        if not set(contract["evidence_refs"]) <= source_ids:
            raise ValueError("Wave 8 North America contract has an unknown source")


def validate_wave8_north_america_queue_contracts(hced_rows: list[dict[str, Any]]) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(hced_rows, WAVE8_NORTH_AMERICA_CONTRACTS, WAVE8_NORTH_AMERICA_HOLDS, lane_name="Wave 8 North America")


def install_wave8_north_america_entities(release_entities: dict[str, dict[str, Any]]) -> None:
    _validate_static()
    install_exact_entities(release_entities, WAVE8_NORTH_AMERICA_ENTITIES, lane_name="Wave 8 North America")


def install_wave8_north_america_sources(sources_by_id: dict[str, dict[str, Any]]) -> None:
    _validate_static()
    install_exact_sources(sources_by_id, WAVE8_NORTH_AMERICA_SOURCES, lane_name="Wave 8 North America")


def promote_wave8_north_america_contracts(hced_rows: list[dict[str, Any]], release_entities: Mapping[str, Mapping[str, Any]], existing_events: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    validate_wave8_north_america_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(hced_rows, release_entities, existing_events, WAVE8_NORTH_AMERICA_CONTRACTS, lane_name="Wave 8 North America", event_id_prefix="hced_wave8_north_america_")


def wave8_north_america_cohort_counts() -> dict[str, int]:
    return dict(sorted(Counter(contract["cohort"] for contract in WAVE8_NORTH_AMERICA_CONTRACTS.values()).items()))
