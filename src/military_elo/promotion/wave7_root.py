"""High-yield, candidate-keyed Wave 7 contracts audited by the integration lane.

The source labels in these cohorts are historically meaningful but too broad for
global aliases (for example ``United States`` in 1775, ``Creek Indians`` in the
Creek civil war, and ``Austria-Hungary`` in an 1849 row).  Every admission is
therefore keyed to one content-locked HCED row and to an alias-free identity.
Rows with campaign/component overlap stay reserved as explicit holds.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _domain, _event_key, _participants, _scale, _slug, normalize_label
from .hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
    build_hced_location_fields,
    hced_candidate_id,
)


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    family: str,
) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": family,
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome_consistency_crosscheck",
        ],
    }


WAVE7_ROOT_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave7_loc_american_revolution",
        "The American Revolution, 1763-1783",
        "https://www.loc.gov/classroom-materials/united-states-history-primary-source-timeline/american-revolution-1763-1783/overview/",
        "Library of Congress",
        "official_history",
        "library_of_congress_american_revolution",
    ),
    _source(
        "wave7_army_revolution_campaigns",
        "Revolutionary War Campaigns",
        "https://history.army.mil/Research/Reference-Topics/Army-Campaigns/Brief-Summaries/Revolutionary-War-Campaigns/",
        "U.S. Army Center of Military History",
        "official_military_history",
        "us_army_revolutionary_war",
    ),
    _source(
        "wave7_nps_revolution_timeline",
        "Revolutionary War Timeline",
        "https://www.nps.gov/cowp/learn/historyculture/revolutionary-war-timeline.htm",
        "U.S. National Park Service",
        "official_history",
        "national_park_service_revolution",
    ),
    _source(
        "wave7_canada_longueuil",
        "Fort Longueuil Memorial Plaque",
        "https://www.veterans.gc.ca/en/remembrance/memorials/national-inventory-canadian-memorials/details/9457",
        "Veterans Affairs Canada",
        "official_commemorative_record",
        "veterans_affairs_canada_longueuil",
    ),
    _source(
        "wave7_un_biafra_identity",
        "Nigeria national history and the 1967 Biafran secession",
        "https://documents.un.org/doc/undoc/gen/n96/291/59/pdf/n9629159.pdf",
        "United Nations",
        "official_report",
        "united_nations_nigeria_history",
    ),
    _source(
        "wave7_state_biafra",
        "Background Paper on Nigeria/Biafra",
        "https://history.state.gov/historicaldocuments/frus1969-76ve05p1/d35",
        "U.S. Department of State, Office of the Historian",
        "official_diplomatic_record",
        "frus_nigeria_biafra",
    ),
    _source(
        "wave7_nigeria_civil_war_history",
        "A Journey in Service: Nigerian Civil War operational chronology",
        "https://nigeriareposit.nln.gov.ng/server/api/core/bitstreams/ff513b9c-508b-44e8-9e08-96d4a3c8828b/content",
        "National Library of Nigeria Repository",
        "national_repository_monograph",
        "nigeria_national_library_civil_war",
    ),
    _source(
        "wave7_army_creek_war",
        "The Creek War, 1813-1814",
        "https://history.army.mil/portals/143/Images/Publications/catalog/74-4.pdf",
        "U.S. Army Center of Military History",
        "official_military_history",
        "us_army_creek_war",
    ),
    _source(
        "wave7_nps_creek_war",
        "The Creek Indian War of 1813-1814",
        "https://www.nps.gov/ocmu/learn/historyculture/upload/Accessible-Creek-Indian-War-of-1813-1814-2.pdf",
        "U.S. National Park Service",
        "official_history",
        "national_park_service_creek_war",
    ),
    _source(
        "wave7_founders_emuckfaw",
        "William Cocke to Thomas Jefferson, 28 January 1814",
        "https://founders.archives.gov/documents/Jefferson/03-07-02-0094",
        "National Archives / Founders Online",
        "primary_source_critical_edition",
        "founders_online_jefferson_papers",
    ),
    _source(
        "wave7_treccani_murat",
        "Gioacchino Napoleone Murat, re di Napoli",
        "https://www.treccani.it/enciclopedia/gioacchino-napoleone-murat-re-di-napoli_%28Dizionario-Biografico%29/",
        "Istituto della Enciclopedia Italiana",
        "academic_reference",
        "treccani_editorial_corpus",
    ),
    _source(
        "wave7_italian_army_1815",
        "Rassegna dell'Esercito: Murat and the 1815 settlement",
        "https://www.esercito.difesa.it/comunicazione/editoria/Rassegna-Esercito/Tutti-i-numeri/2015/Documents/rassei-1-15.pdf",
        "Italian Army",
        "official_military_history",
        "italian_army_rassegna",
    ),
    _source(
        "wave7_treccani_tolentino",
        "Tolentino and the decisive combat of 1815",
        "https://www.treccani.it/enciclopedia/tolentino_%28Enciclopedia-Italiana%29/",
        "Istituto della Enciclopedia Italiana",
        "academic_reference",
        "treccani_editorial_corpus",
    ),
    _source(
        "wave7_hungary_military_museum",
        "Our Catchwords Were Patriotism and Progress",
        "https://m.militaria.hu/en/exhibitions/permanent-exhibitions/our-catchwords-were-patriotism-and-progress",
        "Hungarian Ministry of Defence Military History Institute and Museum",
        "official_military_history",
        "hungarian_military_history_institute",
    ),
    _source(
        "wave7_hungary_archives",
        "Operational records of the 1848-49 War of Independence",
        "https://adatbazisokonline.mnl.gov.hu/adatbazis/az-1848-49-evi-szabadsagharc-hadmuveleti-iratai/informacio",
        "National Archives of Hungary",
        "official_archival_catalogue",
        "hungarian_national_archives_1848",
    ),
    _source(
        "wave7_navy_torch",
        "Operation Torch: Invasion of North Africa",
        "https://www.history.navy.mil/browse-by-topic/wars-conflicts-and-operations/world-war-ii/1942/operation-torch.html",
        "U.S. Naval History and Heritage Command",
        "official_military_history",
        "us_navy_operation_torch",
    ),
    _source(
        "wave7_army_torch",
        "Algeria-French Morocco",
        "https://history.army.mil/Portals/143/Images/Publications/Publication%20By%20Title%20Images/C%20Img/campaigns-wwii/pdf/2.pdf",
        "U.S. Army Center of Military History",
        "official_military_history",
        "us_army_algeria_french_morocco",
    ),
    _source(
        "wave7_uk_madagascar",
        "Maritime manoeuvre: the Battle of Madagascar, 1942",
        "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/649524/doctrine_uk_maritime_power_jdp_0_10.pdf",
        "United Kingdom Ministry of Defence",
        "official_doctrine_history",
        "uk_mod_maritime_power",
    ),
    _source(
        "wave7_iwm_dakar",
        "Vichy France's Radio Propaganda on Collaboration",
        "https://www.iwm.org.uk/sites/default/files/files/2018-11/Vichy%20France%E2%80%99s%20Radio%20Propaganda%20on%20Collaboration%20-%20Karine%20Varley.pdf",
        "Imperial War Museums",
        "museum_research_paper",
        "imperial_war_museums_vichy",
    ),
    _source(
        "wave7_nam_syria",
        "Paddy Mayne and combat against Vichy forces in Syria",
        "https://www.nam.ac.uk/explore/paddy-mayne",
        "National Army Museum",
        "museum_history",
        "national_army_museum_syria",
    ),
)

_WAVE7_ROOT_DIRECT_OUTCOME_SOURCE_IDS = frozenset(
    {
        "wave7_nps_revolution_timeline",
        "wave7_nigeria_civil_war_history",
        "wave7_nps_creek_war",
        "wave7_founders_emuckfaw",
        "wave7_hungary_military_museum",
    }
)
WAVE7_ROOT_SOURCES = tuple(
    {
        **source,
        "evidence_roles": [*source["evidence_roles"], "outcome"],
    }
    if source["id"] in _WAVE7_ROOT_DIRECT_OUTCOME_SOURCE_IDS
    else source
    for source in WAVE7_ROOT_SOURCES
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: tuple[str, ...],
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
        "continuity_note": note
        + " No rating is inherited by a predecessor or successor.",
        "source_ids": list(source_ids),
    }


WAVE7_ROOT_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "american_revolutionary_forces_1775",
        "American Revolutionary Forces (1775-1776)",
        "revolutionary_force",
        1775,
        1776,
        "North America",
        ("wave7_loc_american_revolution", "wave7_army_revolution_campaigns"),
        "Campaign actor for colonial militia and the newly created Continental Army before and through the 1776 declaration; it is not an anachronistic United States state identity.",
    ),
    _entity(
        "republic_biafra",
        "Republic of Biafra",
        "secessionist_state",
        1967,
        1970,
        "West Africa",
        ("wave7_un_biafra_identity", "wave7_state_biafra"),
        "Secessionist republic from the May 1967 declaration through the January 1970 surrender.",
    ),
    _entity(
        "nigerian_federal_military_forces",
        "Nigerian Federal Military Government Forces",
        "state_force",
        1966,
        1979,
        "West Africa",
        ("wave7_state_biafra", "wave7_nigeria_civil_war_history"),
        "Federal military actor for the Nigerian Civil War, distinct from later civilian republic administrations.",
    ),
    _entity(
        "red_stick_creek_forces",
        "Red Stick Creek Forces",
        "indigenous_faction",
        1813,
        1814,
        "North America",
        ("wave7_army_creek_war", "wave7_nps_creek_war"),
        "Militant Upper Creek faction in the Creek civil war and war with United States forces, not the Creek Nation as a timeless collective.",
    ),
    _entity(
        "murat_kingdom_naples",
        "Kingdom of Naples under Joachim Murat",
        "kingdom",
        1808,
        1815,
        "Southern Europe",
        ("wave7_treccani_murat", "wave7_italian_army_1815"),
        "Murat's Napoleonic kingdom, ending with the 1815 Austrian campaign and Bourbon restoration.",
    ),
    _entity(
        "hungarian_honved_army_1848",
        "Hungarian Honved Army (1848-1849)",
        "revolutionary_state_force",
        1848,
        1849,
        "Central Europe",
        ("wave7_hungary_military_museum", "wave7_hungary_archives"),
        "Army of the Hungarian Revolution and War of Independence, not a generic timeless rebel identity.",
    ),
    _entity(
        "vichy_french_forces",
        "Vichy French Forces",
        "state_force",
        1940,
        1944,
        "Europe and French colonial territories",
        ("wave7_navy_torch", "wave7_army_torch"),
        "Forces owing allegiance to the Vichy government; kept distinct from Free French and Third Republic ratings.",
    ),
    _entity(
        "free_french_forces",
        "Free French Forces",
        "government_in_exile_force",
        1940,
        1944,
        "Europe and French colonial territories",
        ("wave7_iwm_dakar", "wave7_nam_syria"),
        "Free French wartime actor before the provisional government transition.",
    ),
    _entity(
        "arab_legion_transjordan",
        "Arab Legion of Transjordan",
        "state_force",
        1923,
        1956,
        "Middle East",
        ("wave7_nam_syria",),
        "Transjordan's Arab Legion, used only in an exact 1941 coalition contract.",
    ),
)


WAVE7_ROOT_ENTITY_IDS = frozenset(str(row["id"]) for row in WAVE7_ROOT_ENTITIES)
WAVE7_ROOT_SOURCE_IDS = frozenset(str(row["id"]) for row in WAVE7_ROOT_SOURCES)


# Full canonical JSON SHA-256 values pin every reviewed queue row.  The mapping
# value is the cohort that selects the only permitted raw-label-to-identity map.
_CONTRACT_ROWS: dict[str, tuple[str, str]] = {
    # American Revolution, 1775-1776 (15)
    "hced-Boston1775-1776-1": (
        "89a5a3357ae55958fc0573a8a3ce3cb3860d6c8a17fe94014c3e8a5fb5637177",
        "american_1775",
    ),
    "hced-Bunker Hill1775-1": (
        "d8b966e1a249aa739aaa61c74b86cf0219f7a2127e3d8d7049cd5327e3d87bd5",
        "american_1775",
    ),
    "hced-Chambly1775-1": (
        "2c7ab2b260de1c51d8e6c9b6b4c6a308fdfe3050a42e2ada0b85d15de6681d56",
        "american_1775",
    ),
    "hced-Concord1775-1": (
        "9e535dbee7f215dcaf001e9629ba75de16a872f61ef1944b3994a06b36968105",
        "american_1775",
    ),
    "hced-Crown Point (1st)1775-1": (
        "778b79f5d3df6e9dd1c0ad50f831c4e54f14d964749703dc1e12ad4dd8203614",
        "american_1775",
    ),
    "hced-Fort Ticonderoga1775-1": (
        "6a5a1c7febe9c756a59b3c2aadff8bceb83975324691185afe6c2e3210cc1011",
        "american_1775",
    ),
    "hced-Great Bridge1775-1": (
        "701c6dc3a60ec15565849fc1254b8d67438f766cc63a68ff4023a655017f6cbd",
        "american_1775",
    ),
    "hced-Hampton1775-1": (
        "af1eb32c4a5faafaef2f27bf364874518bb63f09f11c2947e1e69bb92e5380ef",
        "american_1775",
    ),
    "hced-Lexington, Massachusetts1775-1": (
        "82dac3e87b420bcae62172b20b0f082d4407ee341b8eacc86a622514b427c84e",
        "american_1775",
    ),
    "hced-Longueuil1775-1": (
        "2994767e9165ee91a2d15ebabf351bf647fa10ef38e4b3f1d2419a4c895f58c0",
        "american_1775",
    ),
    "hced-Machias1775-1": (
        "94386a5358aa9b4864bc924ee9d12cae84e3469ce36f1f36051abee6e6f4a075",
        "american_1775",
    ),
    "hced-Montreal1775-1": (
        "760b2dd8ddec91ba60a497e0864868e338f950dc83c187da41f8e4b7fb927059",
        "american_1775",
    ),
    "hced-Quebec1775-1776-1": (
        "77591a385a2f2ad419fce5b4bb3d4be3f31d06b9fee787c3c68d6f67f5253ecd",
        "american_1775",
    ),
    "hced-St Johns (1st)1775-1": (
        "fbfaf83c6dff004d54478560f0dadb7bd982ab3bee32ab5d6d38bc61f4697422",
        "american_1775",
    ),
    "hced-St Johns (2nd)1775-1": (
        "37164119b12db2ff8a4ce9ff465ccc510502dc2b4b8520f3ae974572253d381b",
        "american_1775",
    ),
    # Nigeria-Biafra War (8)
    "hced-Abagana1968-1": (
        "69f26a610726093e8f89744bd731190b77b3eb355faf765a5cca206db0442725",
        "biafra",
    ),
    "hced-Benin1967-1": (
        "e2fff0ec0a7f9bb41b53bfe43a9a369b2adab35e69853beb2fef5c68de0cc610",
        "biafra",
    ),
    "hced-Calabar1967-1": (
        "606fff789c4bacbbf8ea8be637340dd77779d96bcc28287a8df7771d9b256378",
        "biafra",
    ),
    "hced-Enugu1967-1": (
        "10ddb71200103c9c3fd069c37a2efb962a9111f7b27662a9582564c58bd68101",
        "biafra",
    ),
    "hced-Onitsha1967-1": (
        "24e2d1c05f405e1ba9a8b986e522332a429fbe3e6cb79279599d7a8bc0ae9a2a",
        "biafra",
    ),
    "hced-Owerri1968-1": (
        "fc673227ed3828e4a785fa49e23be20705d4b95a3888f50752835e7fbfb9be69",
        "biafra",
    ),
    "hced-Port Harcourt1968-1": (
        "0bd9823c7a13e25ab654e4cda08024aea9f0f64bef1b32c19faab0043a4f6ab4",
        "biafra",
    ),
    "hced-Umuahia1969-1": (
        "cc607561fdcc3ee5437f87ace6678986383202392ee07dc71e5d23a79a91fece",
        "biafra",
    ),
    # Red Stick Creek War (11)
    "hced-Autossee1813-1": (
        "f48dd28e75223a080c9a5b5c4683d2e676317d9d610052ced15d3da9330da877",
        "red_sticks",
    ),
    "hced-Burnt Corn1813-1": (
        "223f3b9613cf6e694a796ba0f1d73e182c407d28bc72e71d5d723fcf71f7882d",
        "red_sticks",
    ),
    "hced-Emuckfaw1814-1": (
        "199fda9bcab12ea3885f3ea4aeef330b39e8510689062aa857bbf073628f20c7",
        "red_sticks",
    ),
    "hced-Enotachopco1814-1": (
        "11fb3d43c3cb1ca43417eac44e9c7053da467633565845a31ad58a7231c8deb9",
        "red_sticks",
    ),
    "hced-Fort Mims1813-1": (
        "caa1650598946b33c64b21f4e0f9c63f88c28d929e7d06f6d462085c22425238",
        "red_sticks",
    ),
    "hced-Fort Sinquefield1813-1": (
        "4dfd587e5615dc9185ab27d2359ae09518288a97444be52d66d652d466248088",
        "red_sticks",
    ),
    "hced-Holy Ground1813-1": (
        "b611828e62976d0a0511368a37cd83456fe40278392154cb823f884453cf12c1",
        "red_sticks",
    ),
    "hced-Horseshoe Bend1814-1": (
        "af82e45d0b63a434e609095c26791cc6090aa383d01cf757a46dd990d38f0a60",
        "red_sticks",
    ),
    "hced-Littafatchee1813-1": (
        "9b11de213546704c85ed790f23161ced100e17ef96edee55472b8efcccb2e793",
        "red_sticks",
    ),
    "hced-Talladega1813-1": (
        "07b78619c70ab7810228b28c0ad6c29daf3336ac75081813c3d31299e80269f4",
        "red_sticks",
    ),
    "hced-Tallaseehatchee1813-1": (
        "bf4597ea1cca6224ec085e3a9e0b84e0c03604d6651d7499bef4c469cf6686e8",
        "red_sticks",
    ),
    # Murat's Kingdom of Naples (12)
    "hced-Ancona1815-1": (
        "9a5cfa6028b8c43f090120603c2354ab4ea36b41a631affca30ea95478bea8cb",
        "murat_naples",
    ),
    "hced-Capri, 1815-1": (
        "4b072a8b2577d37b951a12a14d1da52407a874b74ece544b5c57192dd7aac81d",
        "murat_naples",
    ),
    "hced-Casaglia1815-1": (
        "9954335f5aacda946f9a3c51921d0372c2300905fd249bf20adddf8e89c1d21b",
        "murat_naples",
    ),
    "hced-Castel di Sangro1815-1": (
        "7553b1c5409754be431b51bd99de2fca4e3679c63096b1ca896c695e25862902",
        "murat_naples",
    ),
    "hced-Cesenatico1815-1": (
        "85faaa522597615ae214a57ca2223e731369d44bc6d1138156ee117ecb71fd31",
        "murat_naples",
    ),
    "hced-Occhiobello, 1815-1": (
        "7b68d8cc658a81f8af11321284b28d8e6bfc197c7678593cb9e07deca7e0683c",
        "murat_naples",
    ),
    "hced-Panaro1815-1": (
        "1726ba0a2dad3ca1fcef4dd54171331b94fbd4a75616649fd57298039eaa7f40",
        "murat_naples",
    ),
    "hced-Pesaro1815-1": (
        "fc633519cb1f6465cc62bbe36d865f1f52aa8426fd383bf30dc7105b0ea2e091",
        "murat_naples",
    ),
    "hced-Ronco1815-1": (
        "a492c5b6441f1efd00702995b7ce6f1267ac8d0efaced5e93a2da3b35dcc3265",
        "murat_naples",
    ),
    "hced-San Germano1815-1": (
        "01ca4d3f53ec40d730f7f7808f0995c6ac1764b703bc1c849461a477c61db9b1",
        "murat_naples",
    ),
    "hced-Scapezzano1815-1": (
        "587618755e5fe1402057934bf58f49b8bf26cde8d0b3f2a2472aacb70212505a",
        "murat_naples",
    ),
    "hced-Tolentino1815-1": (
        "ccd786febc3fc990f4e5848e656154443f962652c7c335f45b313312b5e8b271",
        "murat_naples",
    ),
    # Hungarian War of Independence (10)
    "hced-Acs1849-1": (
        "50ed9a6da87c5c5396dc494734297bc3b2f831df77985242c5e1955ca5b7da92",
        "hungarian_honved",
    ),
    "hced-Buda1849-1": (
        "daf467cf7129488fb5841b5f0e08667599dc31a0dae660dbebaad6e335b42442",
        "hungarian_honved",
    ),
    "hced-Isaszeg1849-1": (
        "f6bf2f2da2eb52a3736f47cd245ccdc2af3f3c2e704e60fc5b865462fef62c5e",
        "hungarian_honved",
    ),
    "hced-Kapolna1849-1": (
        "15b2637943f953f3931ed0740a4af35c3ba3fecc6cc68502920dc4c12cfdeee9",
        "hungarian_honved",
    ),
    "hced-Komarom1849-1": (
        "3d6bee0d1c728bb6d73c9e6a36a72d0731fd10359200c0a731216369abea3cde",
        "hungarian_honved",
    ),
    "hced-Nagy Sallo1849-1": (
        "cd0fa8060b55cda25a67b527245af7ffa5307a5dd68b9fdc43b235d410cf5f31",
        "hungarian_honved",
    ),
    "hced-Pakozd1848-1": (
        "558b02977db1a58f59730052167d2800559a8b35571cfe25d0825f6f9a263bfe",
        "hungarian_honved",
    ),
    "hced-Pered1849-1": (
        "83c1bbc1fac710a9574ccd69a160aa2ac379a6abb578d23d200f0892ae49808f",
        "hungarian_honved",
    ),
    "hced-Temesvar1849-1": (
        "091eacd4a664e573e41f29edb3af246aa5df29ff656e9e93436c85347ec7a3bf",
        "hungarian_honved",
    ),
    "hced-Waitzen1849-1": (
        "f0c4e5c8751d6d224d294ff64e434e952f76336d76cd932d0ef8ae8a10c3148b",
        "hungarian_honved",
    ),
    # Exact Vichy actions; campaign umbrellas are held below (6)
    "hced-Algiers1942-1": (
        "71ce5969898e02d8895d6b8d4f21ae60e46ebf645942a68f8d06ad392370c173",
        "vichy",
    ),
    "hced-Casablanca1942-1": (
        "6cf4689e93ddaa4e9fd872bd9a725a52b7c6d8137c46fc07677e3fc85477a6c0",
        "vichy",
    ),
    "hced-Dakar1940-1": (
        "12e09a05be59f98026a6c910ca6c69082172ebd5e917c7694dbc6cf3be8bd029",
        "vichy",
    ),
    "hced-Madagascar1942-1": (
        "ecebceebbcf4af97172396c0150f2d0c2276205fab29b7b09523e1af08f641cf",
        "vichy",
    ),
    "hced-Oran1942-1": (
        "3f744fdfe71f9cf17d40fefde2e57d733b1996daf18bade81aa89edc969a3537",
        "vichy",
    ),
    "hced-Palmyra1941-1": (
        "3f7e65225efa421b125eced004aa4a495d41b362c284215d17b45ee59ac20d0a",
        "vichy",
    ),
}


WAVE7_ROOT_HOLDS: dict[str, dict[str, str]] = {
    "hced-Lebanon1941-1": {
        "raw_sha256": "ebd28f3da3f5908753826930791689af6038f19cea79b217e8ea075c5fa4dc58",
        "reason": "broad Lebanon campaign record overlaps the Syria-Lebanon campaign and component actions",
    },
    "hced-Syria1941-1": {
        "raw_sha256": "29070ceaa199ea799e85966e54400476aea2c53ba347a9603cafa60ef3c06f76",
        "reason": "broad Syria campaign record overlaps the Syria-Lebanon campaign and component actions",
    },
    "hced-Torch1942-1": {
        "raw_sha256": "263ceb8cfde113ae145a51ae27b2f1efd161bde2620d235ecfd8eb56ffcb0e91",
        "reason": "Operation Torch umbrella overlaps the separately rated Algiers, Casablanca, and Oran actions",
    },
    "hced-Vienna1848-1": {
        "raw_sha256": "14dd3bb49eb649f0559e5a0dd5cfcce704f06a161cc07e3cc5e8a10f967de1c7",
        "reason": "mixed Viennese and Hungarian rebel coalition cannot be assigned wholly to the Honved identity",
    },
}


WAVE7_ROOT_CONTRACT_IDS = frozenset(_CONTRACT_ROWS)
WAVE7_ROOT_HOLD_IDS = frozenset(WAVE7_ROOT_HOLDS)
WAVE7_ROOT_RESERVED_IDS = WAVE7_ROOT_CONTRACT_IDS | WAVE7_ROOT_HOLD_IDS


_SIDE_MAPS: dict[str, dict[str, tuple[str, ...]]] = {
    "american_1775": {
        "United States": ("american_revolutionary_forces_1775",),
        "United Kingdom": ("united_kingdom",),
    },
    "biafra": {
        "Biafran Rebels": ("republic_biafra",),
        "Nigeria": ("nigerian_federal_military_forces",),
    },
    "red_sticks": {
        "Creek Indians": ("red_stick_creek_forces",),
        "United States": ("united_states",),
    },
    "murat_naples": {
        "Kingdom of Naples": ("murat_kingdom_naples",),
        "Habsburg Empire": ("austrian_empire",),
    },
    "hungarian_honved": {
        "Hungarian Rebels": ("hungarian_honved_army_1848",),
        "Austria": ("austrian_empire",),
        "Habsburg Empire": ("austrian_empire",),
        "Austria-Hungary": ("austrian_empire",),
        "Austria, Russia": ("austrian_empire", "russian_empire"),
        "Russia, Austria": ("russian_empire", "austrian_empire"),
    },
    "vichy": {
        "Vichy France": ("vichy_french_forces",),
        "United Kingdom": ("united_kingdom",),
        "United States": ("united_states",),
        "United Kingdom, United States": ("united_kingdom", "united_states"),
        "United States, United Kingdom": ("united_states", "united_kingdom"),
        "Free France, United Kingdom": ("free_french_forces", "united_kingdom"),
        "United Kingdom, Arab Legion": ("united_kingdom", "arab_legion_transjordan"),
    },
}


_COHORT_EVIDENCE: dict[str, tuple[str, ...]] = {
    "american_1775": (
        "wave7_loc_american_revolution",
        "wave7_army_revolution_campaigns",
    ),
    "biafra": (
        "wave7_un_biafra_identity",
        "wave7_state_biafra",
        "wave7_nigeria_civil_war_history",
    ),
    "red_sticks": ("wave7_army_creek_war", "wave7_nps_creek_war"),
    "murat_naples": (
        "wave7_treccani_murat",
        "wave7_italian_army_1815",
        "wave7_treccani_tolentino",
    ),
    "hungarian_honved": ("wave7_hungary_military_museum", "wave7_hungary_archives"),
    "vichy": ("wave7_navy_torch", "wave7_army_torch"),
}


# These seven source outcomes are corrected rather than copied from HCED.
# The value is (result_type, winning_side, authoritative outcome source).
_OUTCOME_OVERRIDES: dict[str, tuple[str, int | None, str]] = {
    "hced-Concord1775-1": ("decisive", 2, "wave7_nps_revolution_timeline"),
    "hced-Onitsha1967-1": ("decisive", 2, "wave7_nigeria_civil_war_history"),
    "hced-Burnt Corn1813-1": ("draw", None, "wave7_nps_creek_war"),
    "hced-Emuckfaw1814-1": ("draw", None, "wave7_founders_emuckfaw"),
    "hced-Enotachopco1814-1": ("draw", None, "wave7_founders_emuckfaw"),
    "hced-Buda1849-1": ("decisive", 2, "wave7_hungary_military_museum"),
    "hced-Pakozd1848-1": ("decisive", 2, "wave7_hungary_military_museum"),
}
WAVE7_ROOT_OUTCOME_CORRECTION_IDS = frozenset(_OUTCOME_OVERRIDES)


_CANONICAL_NAMES = {
    "hced-Concord1775-1": "Battle of Concord",
    "hced-Onitsha1967-1": "First Battle of Onitsha",
    "hced-Capri, 1815-1": "Battle of Carpi (1815)",
}


def canonical_row_sha256(row: Mapping[str, Any]) -> str:
    payload = json.dumps(
        dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _rows_by_id(rows: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        indexed.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    return indexed


def validate_wave7_root_candidates(rows: list[dict[str, Any]]) -> dict[str, int]:
    indexed = _rows_by_id(rows)
    expected = {
        **{
            candidate_id: digest for candidate_id, (digest, _) in _CONTRACT_ROWS.items()
        },
        **{
            candidate_id: hold["raw_sha256"]
            for candidate_id, hold in WAVE7_ROOT_HOLDS.items()
        },
    }
    for candidate_id, digest in expected.items():
        candidates = indexed.get(candidate_id, [])
        if len(candidates) != 1:
            raise ValueError(
                f"Wave 7 root contract {candidate_id} expected exactly one queue row, found {len(candidates)}"
            )
        if canonical_row_sha256(candidates[0]) != digest:
            raise ValueError(
                f"Wave 7 root contract {candidate_id} raw-row fingerprint changed"
            )
    return {"reviewed": 66, "promoted": 62, "held": 4}


def install_wave7_root_entities(release_entities: dict[str, dict[str, Any]]) -> None:
    source_ids = {str(source["id"]) for source in WAVE7_ROOT_SOURCES}
    for fixture in WAVE7_ROOT_ENTITIES:
        if not set(map(str, fixture["source_ids"])) <= source_ids:
            raise ValueError(
                f"Wave 7 root entity {fixture['id']} names an unknown source"
            )
        entity = dict(fixture)
        entity_id = str(entity["id"])
        existing = release_entities.get(entity_id)
        if existing is not None and existing != entity:
            raise ValueError(f"Wave 7 root entity ID collision for {entity_id}")
        release_entities[entity_id] = entity


def install_wave7_root_sources(sources_by_id: dict[str, dict[str, Any]]) -> None:
    """Install the reviewed references without silently replacing a source."""

    for fixture in WAVE7_ROOT_SOURCES:
        source = dict(fixture)
        source["evidence_roles"] = list(fixture["evidence_roles"])
        source_id = str(source["id"])
        existing = sources_by_id.get(source_id)
        if existing is not None and existing != source:
            raise ValueError(f"Wave 7 root source ID collision for {source_id}")
        sources_by_id[source_id] = source


def _entity_covers(entity: Mapping[str, Any], low_year: int, high_year: int) -> bool:
    end = entity.get("end_year")
    return int(entity["start_year"]) <= low_year and (
        end is None or int(end) >= high_year
    )


def _resolved_sides(
    candidate: Mapping[str, Any], cohort: str
) -> tuple[list[str], list[str]]:
    side_map = _SIDE_MAPS[cohort]
    labels = (
        str(candidate.get("side_1_raw") or ""),
        str(candidate.get("side_2_raw") or ""),
    )
    try:
        return list(side_map[labels[0]]), list(side_map[labels[1]])
    except KeyError as exc:
        raise ValueError(
            f"Wave 7 root contract {candidate.get('candidate_id')} has an undeclared side label: {exc}"
        ) from exc


def _result(
    candidate_id: str,
    candidate: Mapping[str, Any],
) -> tuple[bool, int | None, list[str]]:
    override = _OUTCOME_OVERRIDES.get(candidate_id)
    if override is not None:
        result_type, winner_side, source_id = override
        return result_type == "draw", winner_side, [source_id]
    winner = normalize_label(candidate.get("winner_raw"))
    if winner in {"draw", "inconclusive", "stalemate"}:
        return True, None, ["hced_dataset"]
    if candidate.get("winner_raw") == candidate.get("side_1_raw") and candidate.get(
        "loser_raw"
    ) == candidate.get("side_2_raw"):
        return False, 1, ["hced_dataset"]
    if candidate.get("winner_raw") == candidate.get("side_2_raw") and candidate.get(
        "loser_raw"
    ) == candidate.get("side_1_raw"):
        return False, 2, ["hced_dataset"]
    raise ValueError(f"Wave 7 root outcome/side drift for {candidate_id}")


def promote_wave7_root_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Promote the exact 62 safe rows without consulting a generic resolver."""

    validate_wave7_root_candidates(hced_rows)
    indexed = _rows_by_id(hced_rows)
    existing_candidate_ids = {
        str(event["hced_candidate_id"])
        for event in existing_events
        if event.get("hced_candidate_id") is not None
    }
    collisions = sorted(existing_candidate_ids & WAVE7_ROOT_CONTRACT_IDS)
    if collisions:
        raise ValueError(f"Wave 7 root HCED candidate already promoted: {collisions}")
    existing_keys = {
        _event_key(str(event["name"]), int(event["year"])) for event in existing_events
    }
    accepted_keys: set[tuple[str, int]] = set()
    events: list[dict[str, Any]] = []

    for candidate_id, (expected_digest, cohort) in sorted(
        _CONTRACT_ROWS.items(),
        key=lambda item: (int(indexed[item[0]][0]["year_low"]), item[0]),
    ):
        candidate = indexed[candidate_id][0]
        if (
            hced_candidate_id(candidate) != candidate_id
            or canonical_row_sha256(candidate) != expected_digest
        ):
            raise ValueError(f"Wave 7 root queue drift for {candidate_id}")
        low_year = int(candidate["year_low"])
        high_year = int(candidate["year_high"])
        side_1, side_2 = _resolved_sides(candidate, cohort)
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"Wave 7 root invalid opposing sides for {candidate_id}")
        for entity_id in (*side_1, *side_2):
            entity = release_entities.get(entity_id)
            if entity is None or not _entity_covers(entity, low_year, high_year):
                raise ValueError(
                    f"Wave 7 root entity-window violation for {candidate_id}: {entity_id}"
                )

        draw, winner_index, outcome_sources = _result(candidate_id, candidate)
        if draw:
            winner_side, loser_side = side_1, side_2
        elif winner_index == 1:
            winner_side, loser_side = side_1, side_2
        elif winner_index == 2:
            winner_side, loser_side = side_2, side_1
        else:
            raise ValueError(f"Wave 7 root invalid result for {candidate_id}")

        raw_name = str(candidate["name"])
        event_name = _CANONICAL_NAMES.get(candidate_id, raw_name)
        event_key = _event_key(event_name, low_year)
        raw_key = _event_key(raw_name, low_year)
        if event_key in existing_keys or raw_key in existing_keys:
            raise ValueError(f"Wave 7 root source-family duplicate for {candidate_id}")
        if event_key in accepted_keys:
            raise ValueError(f"Wave 7 root duplicate canonical key for {candidate_id}")
        accepted_keys.add(event_key)

        scale, scale_level = _scale(candidate)
        confidence = round(0.82 - (0.03 if low_year != high_year else 0.0), 2)
        war_names = list(map(str, candidate.get("war_names", [])))
        cluster = _slug(war_names[0]) if war_names else None
        evidence = list(_COHORT_EVIDENCE[cohort])
        if candidate_id == "hced-Longueuil1775-1":
            evidence.append("wave7_canada_longueuil")
        if candidate_id in {"hced-Madagascar1942-1"}:
            evidence.append("wave7_uk_madagascar")
        if candidate_id in {"hced-Dakar1940-1"}:
            evidence.append("wave7_iwm_dakar")
        if candidate_id in {"hced-Palmyra1941-1"}:
            evidence.append("wave7_nam_syria")
        if candidate_id in _OUTCOME_OVERRIDES:
            evidence.append(_OUTCOME_OVERRIDES[candidate_id][2])
        evidence = list(dict.fromkeys(evidence))
        corrected = candidate_id in _OUTCOME_OVERRIDES

        events.append(
            {
                "id": f"hced_wave7_root_{_slug(candidate_id, 72)}",
                "name": event_name,
                "year": low_year,
                "end_year": high_year,
                "event_type": "engagement",
                "war_type": "interstate_limited",
                "scale": scale,
                "stakes": "major" if scale_level >= 4 else "limited",
                "decisiveness": 0.32
                if draw
                else round(min(0.90, 0.54 + 0.06 * scale_level), 2),
                "confidence": confidence,
                "geographic_scope": round(min(0.70, 0.08 + 0.09 * scale_level), 2),
                "domain": _domain(candidate.get("theatre_raw")),
                "cluster_id": f"hced_war_{cluster}" if cluster else None,
                "date_precision": "range" if low_year != high_year else "year",
                "sequence": int(candidate.get("source_row") or 0),
                "summary": (
                    "Candidate-keyed reviewed HCED result with a content-locked row, exact actor boundaries, "
                    "complete coalition roster, and duplicate guard. "
                    + (
                        "The source outcome was corrected by the cited official historical reference."
                        if corrected
                        else "The HCED tactical orientation is retained and cross-checked against the cited references."
                    )
                ),
                "aliases": [raw_name] if raw_name != event_name else [],
                "participants": _participants(
                    winner_side,
                    loser_side,
                    draw,
                    confidence,
                    scale_level,
                    note="Candidate-keyed Wave 7 tactical contract; no generic label or strategic-war inference.",
                ),
                "source_ids": ["hced_dataset", *evidence],
                "outcome_source_ids": outcome_sources,
                "outcome_source_family_ids": [
                    "hced"
                    if outcome_sources == ["hced_dataset"]
                    else str(
                        next(
                            source["source_family_id"]
                            for source in WAVE7_ROOT_SOURCES
                            if source["id"] == outcome_sources[0]
                        )
                    )
                ],
                "reviewed_granularity": "engagement",
                "canonical_event_key": f"{_slug(event_name)}:{low_year}:{high_year}",
                "identity_resolution": "candidate_keyed_exact",
                "historical_outcome_correction": corrected,
                "hced_candidate_id": candidate_id,
                "status": "complete",
                **build_hced_location_fields(
                    candidate,
                    point_quarantine_ids=HCED_POINT_QUARANTINE_IDS,
                    country_quarantine_ids=HCED_COUNTRY_QUARANTINE_IDS,
                ),
            }
        )

    if len(events) != 62:
        raise ValueError(f"Wave 7 root promoted {len(events)} HCED rows instead of 62")
    return events


def wave7_root_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(Counter(cohort for _, cohort in _CONTRACT_ROWS.values()).items())
    )


assert len(WAVE7_ROOT_SOURCES) == len({source["id"] for source in WAVE7_ROOT_SOURCES})
assert len(WAVE7_ROOT_SOURCE_IDS) == 20
assert len(WAVE7_ROOT_ENTITIES) == len(WAVE7_ROOT_ENTITY_IDS) == 9
assert len(WAVE7_ROOT_CONTRACT_IDS) == 62
assert len(WAVE7_ROOT_HOLD_IDS) == 4
assert not WAVE7_ROOT_CONTRACT_IDS & WAVE7_ROOT_HOLD_IDS
assert set(_OUTCOME_OVERRIDES) <= WAVE7_ROOT_CONTRACT_IDS
assert sum(wave7_root_cohort_counts().values()) == 62
