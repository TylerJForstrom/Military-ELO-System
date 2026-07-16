"""Audited, candidate-keyed Wave 7 contracts for the WEST lane.

The embedded queue rows are compressed only to keep this source reviewable.  They
are decoded at import, checked against literal SHA-256 values, and never used as a
label resolver.  The promotion inventory, explicit holds, and protected existing
ownership inventory are disjoint and together account for every reviewed row.
"""

from __future__ import annotations

import base64
import hashlib
import json
import zlib
from typing import Any


WAVE7_WEST_SOURCES: list[dict[str, Any]] = [
    {
        "id": "wave7_west_he_towton",
        "title": "Battle of Towton, 1461",
        "publisher": "Historic England",
        "url": "https://historicengland.org.uk/listing/the-list/list-entry/1000040",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "historic_england",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "wave7_west_he_bosworth",
        "title": "English Heritage Battlefield Report: Bosworth 1485",
        "publisher": "Historic England",
        "url": "https://historicengland.org.uk/content/docs/listing/battlefields/bosworth/",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "historic_england",
        "license": "Citation and link only",
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
        ],
    },
    {
        "id": "wave7_west_he_stoke",
        "title": "English Heritage Battlefield Report: Stoke Field 1487",
        "publisher": "Historic England",
        "url": "https://historicengland.org.uk/content/docs/listing/battlefields/stoke-field/",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "historic_england",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "wave7_west_hdbg_duchy",
        "title": "The Duchy of Bavaria",
        "publisher": "Haus der Bayerischen Geschichte",
        "url": "https://archiv.hdbg.de/geschichte-bayerns/en-02-die-geschichte-02.php",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "haus_der_bayerischen_geschichte",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "wave7_west_hdbg_electorate",
        "title": "The Electorate of Bavaria (1623-1806)",
        "publisher": "Haus der Bayerischen Geschichte",
        "url": "https://archiv.hdbg.de/geschichte-bayerns/en-02-die-geschichte-04.php",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "haus_der_bayerischen_geschichte",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "wave7_west_hdbg_kingdom",
        "title": "The Kingdom of Bavaria (1806-1918)",
        "publisher": "Haus der Bayerischen Geschichte",
        "url": "https://archiv.hdbg.de/geschichte-bayerns/en-02-die-geschichte-05.php",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "haus_der_bayerischen_geschichte",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "wave7_west_hdbg_schellenberg",
        "title": "Die Schlacht auf dem Schellenberg am 2. Juli 1704",
        "publisher": "Haus der Bayerischen Geschichte",
        "url": "https://hdbg.eu/karten/karten/detail/id/83",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "haus_der_bayerischen_geschichte",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "wave7_west_ukna_palatinate",
        "title": "1621-1622 grant for the defence of the Palatinate",
        "publisher": "The National Archives (United Kingdom)",
        "url": "https://www.nationalarchives.gov.uk/e179/notes.asp?action=3&slctgrantid=381",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "uk_national_archives",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "wave7_west_royal_house_netherlands",
        "title": "History of the Kingdom of the Netherlands",
        "publisher": "Royal House of the Netherlands",
        "url": "https://www.royal-house.nl/topics/history/history-of-the-kingdom-of-the-netherlands",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "royal_house_netherlands",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "wave7_west_nl_constitution_1815",
        "title": "Grondwetsherziening 1815",
        "publisher": "De Nederlandse Grondwet",
        "url": "https://www.denederlandsegrondwet.nl/grondwetsherziening-1815",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "de_nederlandse_grondwet",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "wave7_west_saho_blaauwberg",
        "title": "The Battle of Blaauwberg takes place",
        "publisher": "South African History Online",
        "url": "https://sahistory.org.za/dated-event/battle-blaauwberg-takes-place",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "south_african_history_online",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "wave7_west_elysee_1870",
        "title": "150 ans en Republique",
        "publisher": "Presidence de la Republique francaise",
        "url": "https://www.elysee.fr/emmanuel-macron/2020/09/04/150-ans-en-republique",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "elysee",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "wave7_west_rcahmw_twt",
        "title": "Battle of Twthill (Battlefields Inventory)",
        "publisher": "Royal Commission on the Ancient and Historical Monuments of Wales",
        "url": "https://coflein.gov.uk/en/sites/403421",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "rcahmw_coflein",
        "license": "Citation and link only",
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
        ],
    },
    {
        "id": "wave7_west_he_bamburgh",
        "title": "Bamburgh Castle, Bamburgh, Northumberland",
        "publisher": "Historic England",
        "url": "https://historicengland.org.uk/education/schools-resources/educational-images/bamburgh-castle-bamburgh-northumberland-ioe01-15211-01",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "historic_england",
        "license": "Citation and link only",
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
        ],
    },
    {
        "id": "wave7_west_he_caister",
        "title": "Caister Castle, West Caister",
        "publisher": "Historic England",
        "url": "https://historicengland.org.uk/listing/the-list/list-entry/1287573",
        "accessed": "2026-07-16",
        "source_type": "official_or_academic_reference",
        "source_family_id": "historic_england",
        "license": "Citation and link only",
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
        ],
    },
    {
        "id": "wave7_west_ehr_lincolnshire_1470",
        "title": "The Lincolnshire Rebellion of 1470 Revisited",
        "publisher": "Oxford University Press",
        "url": "https://doi.org/10.1093/ehr/ceab030",
        "accessed": "2026-07-16",
        "source_type": "academic_reference",
        "source_family_id": "english_historical_review",
        "license": "Citation and link only",
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
        ],
    },
    {
        "id": "wave7_west_richard_iii_st_albans",
        "title": "The Second Battle of St Albans",
        "publisher": "Richard III Society",
        "url": "https://richardiii.net/richard-iii-his-world/the-war-of-the-roses/the-battles/the-second-battle-of-st-albans/",
        "accessed": "2026-07-16",
        "source_type": "specialist_historical_reference",
        "source_family_id": "richard_iii_society",
        "license": "Citation and link only",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
]


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int | None,
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
        "continuity_note": (
            f"{note} No rating is inherited from a namesake, predecessor, "
            "successor, or broader polity without a separate reviewed contract."
        ),
        "source_ids": source_ids,
    }


WAVE7_WEST_ENTITIES: list[dict[str, Any]] = [
    _entity(
        "tudor_lancastrian_army_1485",
        "Henry Tudor's Army at Bosworth",
        "campaign_army",
        1485,
        1485,
        "England and Wales",
        ["wave7_west_he_bosworth"],
        "Candidate-specific composite army including Henry Tudor's French mercenaries.",
    ),
    _entity(
        "stanley_forces_1485",
        "Stanley Forces at Bosworth",
        "campaign_army",
        1485,
        1485,
        "England and Wales",
        ["wave7_west_he_bosworth"],
        "Candidate-specific force whose intervention supported Henry Tudor.",
    ),
    _entity(
        "yorkist_royal_army_1485",
        "Richard III's Royal Army at Bosworth",
        "campaign_army",
        1485,
        1485,
        "England",
        ["wave7_west_he_bosworth"],
        "Candidate-specific royal army; it is not the 1455-1471 Yorkist faction.",
    ),
    _entity(
        "duchy_bavaria_unified_1506",
        "Unified Duchy of Bavaria",
        "duchy",
        1506,
        1622,
        "Central Europe",
        ["wave7_west_hdbg_duchy"],
        "Begins with the 1506 inheritance statute and ends before electoral status.",
    ),
    _entity(
        "electorate_bavaria_1623",
        "Electorate of Bavaria",
        "electorate",
        1623,
        1805,
        "Central Europe",
        ["wave7_west_hdbg_electorate"],
        "Begins with the electoral dignity in 1623 and ends before the 1806 kingdom.",
    ),
    _entity(
        "kingdom_bavaria_1806",
        "Kingdom of Bavaria",
        "kingdom",
        1806,
        1918,
        "Central Europe",
        ["wave7_west_hdbg_kingdom"],
        "Bounded from 1 January 1806 through 8 November 1918.",
    ),
    _entity(
        "palatine_protestant_forces_1622",
        "Palatine Protestant Forces at Heidelberg",
        "campaign_force",
        1622,
        1622,
        "Central Europe",
        ["wave7_west_ukna_palatinate"],
        "Candidate-specific German Protestant component of the Heidelberg defence.",
    ),
    _entity(
        "baden_imperial_forces_1704",
        "Baden-led Imperial Forces at Schellenberg",
        "campaign_force",
        1704,
        1704,
        "Central Europe",
        ["wave7_west_hdbg_schellenberg"],
        "Candidate-specific Imperial and Reich force under Ludwig of Baden.",
    ),
    _entity(
        "batavian_republic_1795",
        "Batavian Republic",
        "republic",
        1795,
        1806,
        "Western Europe and overseas possessions",
        ["wave7_west_royal_house_netherlands"],
        "Bounded to the Batavian Republic before the Kingdom of Holland.",
    ),
    _entity(
        "kingdom_netherlands_1815",
        "Kingdom of the Netherlands",
        "kingdom",
        1815,
        None,
        "Western Europe and overseas possessions",
        [
            "wave7_west_royal_house_netherlands",
            "wave7_west_nl_constitution_1815",
        ],
        "Generic WEST dispatch begins in 1815; no alias-based dispatch is enabled.",
    ),
    _entity(
        "duke_norfolk_forces_1469",
        "Duke of Norfolk's Forces at Caister",
        "campaign_force",
        1469,
        1469,
        "England",
        ["wave7_west_he_caister"],
        "Candidate-specific force in the private ownership war at Caister Castle.",
    ),
    _entity(
        "paston_retainers_1469",
        "Paston Retainers at Caister Castle",
        "garrison",
        1469,
        1469,
        "England",
        ["wave7_west_he_caister"],
        "Candidate-specific defending garrison in the private war at Caister.",
    ),
    _entity(
        "edward_iv_royal_army_1470",
        "Edward IV's Royal Army at Losecoat Field",
        "campaign_army",
        1470,
        1470,
        "England",
        ["wave7_west_ehr_lincolnshire_1470"],
        "Candidate-specific royal army opposing the Lincolnshire rebellion.",
    ),
    _entity(
        "welles_rebel_army_1470",
        "Welles Rebel Army at Losecoat Field",
        "rebel_army",
        1470,
        1470,
        "England",
        ["wave7_west_ehr_lincolnshire_1470"],
        "Candidate-specific Lincolnshire rebel army led by Sir Robert Welles.",
    ),
]


WAVE7_WEST_EXPECTED_HASHES = dict(
    line.split("|", 1)
    for line in """
hced-Alnwick1462-1|8bdb2048dd6c00a7d0302302512b84c798f59208e4b64b2ffaa614c5b5e6d905
hced-Amberg1745-1|706993fa54e320c54a1fb015d074787160ac70595b86bc243897309a88f36ac2
hced-Ambon1796-1|a57f4039aa05d078a5d2ef70a02d42172dd17888551647a1ef67b4258e3dd831
hced-Bamburgh1464-1|f00c6542a2b47709556d32d8f05c691c0dff927f1930dc1ce2a07a48a86ac587
hced-Batavia1811-1|2c1996931830ae8a0163ce413425647f9f9a482e176f97bfdc1845bb082efee9
hced-Bazeilles1870-1|4d2f914ebfb86dfd4845f7095e9ec5e69756ad2b3ab51c48c1a5b69b243780a0
hced-Blore Heath1459-1|9975e3a7e8e49199a8765aaed9bd76fbdca73a6bef2d088686d18a500ed91804
hced-Blueberg1806-1|6d5cc433091b9e3a2c0d4246e415dd46e7aa0d07de5fbe6b49302106164816e0
hced-Boroughbridge1322-1|ac5a64b879ae6b8c625f162334ef6a1a8a042beb4771464f89157b7442620045
hced-Bosworth Field1485-1|f748e1957f3fd9299939d55ff2faae6b6b1d4b7d2cba429bf3891b6c3b8e7c2d
hced-Caister Castle1469-1|6236e02f718a8974312dabe8f2924a34f6800f1404a445dd676f8c166c630a35
hced-Camperdown1797-1|9cfc2bcbdc6cbc3e88ab36655ba580c14709a63d33434e3a1b291701614f5ab6
hced-Chatillon-sous-Bagneux1870-1|01ac09e2eb0f99070ea9b913bc134ede3ea41671f03b0027991d3b7bb81f6de2
hced-Colombo1796-1|55248e66aca148422cf96d323390a2b48e88be1cd7ecb3ec923b423c99c51fd1
hced-Coulmiers1870-1|8ee7008eb7c8f407c9ad769d336004a97680c9bf48ee5198573cdabe09dcef73
hced-Donauworth1704-1|adb3832c5aaa86ff870fee2e38af160b57f29d233ccd53a14773d8325351ee1e
hced-Dunstable1461-1|c1d2ec4f8e40251ddf41730a63c57e51b5acdc26c388a113894fed4873a43a14
hced-Edgecote1469-1|1baf4e13e887e5d6fefde411b0a93c9d926a2d6a4b104b90032406f02e3ba7c0
hced-Ferrybridge1461-1|744cad190548005a74134b4bf7cf4be188a3172b3f34e23b36ac129396893f17
hced-Freiburg, Wurttemberg1644-1|a70702634f6b479684385fe11b8d7b76267e507c4d5d87cf44280f0ccc97ff31
hced-Gammelsdorf1313-1|95211e4a0261d7861adfe44e734de3dd4bfe3ff3d9f913172d7d1d9b872385c0
hced-Gerchsheim1866-1|5f4651cacac6bb83c8e81303416188ea3deff7b255e9886aaa40e15720627f64
hced-Groote Keeten1799-1|7940e03400ea2839a066908a7d134e1c3273199dcd545312f88e0405528a3649
hced-Hammelburg1866-1|f119c7d3f1234f5e21e7492cb27ffc6141c22d1ccbdf4ebd462d857652d60e26
hced-Hanau1813-1|58cdd748323e817f7dca87aef948d55ab4106c2d8e7b9ffa4ec163357e3500d2
hced-Hedgeley Moor1464-1|6bb82f720b0dda7e45711435c083703675571cae39b837c6bf968d7829ba4d26
hced-Heidelberg1622-1|f18794f8bcd4a5823f4c4b160ea1359231bda7bac5fb51fe4515672de088ae6a
hced-Helmstadt1866-1|83cd84fd77bc53e38885a9ae10f0350e92621ba1c7f7da582023d61777ebb95d
hced-Hexham1464-1|f2e7117d19e50733ae0124f95da3d847028e783f929f0a68b415cf95c8a4ec55
hced-Java1811-1|181ccd6c3d7491cec1c5b0aa076aca7a0be856688f4a8882097f7abfdffed3c2
hced-Jogjakarta1948-1|089f9ba86cafed0d66ec90e468c12a13bc5da0cc49871d24c508ed17769ae4bc
hced-Kissingen1866-1|6df1d7ac84eddedfc2b1436fbcc7071072a77d4cde61701c853229baea6acda3
hced-Lombok Strait1942-1|3a9656d470bf31a63b4d3cbde249bcb0fbb8136b759dcaac9247614e9c4d4678
hced-Lose-Coat Field1470-1|17715d93c32e4e4659025cbe508c66717831f3cb3acace08d3774e81a745e2a9
hced-Ludford Bridge1459-1|a47bb3521281ef170acf7d262bf0b0dbb866b626bcc1d533a3b829f0c92a3f69
hced-Marga1946-1|b08ffe77e98629821504e4dd9d9e929c8a026c05b5cf363418e7e4d6381fec5f
hced-Mortimers Cross1461-1|d75566979863d158c59afd0d66e472cb1f28855759f8fdb3d03a38b15e2350a1
hced-Muhldorf1322-1|1e042b9e62c0c22ec63909a5de5e83b34451f9e1c82a29286ee0efec7a93703f
hced-Munderkingen1703-1|0d2d671fdaff3a799a309e480e6da2875f708f392324190b5fd78532549b4c5e
hced-Northampton1460-1|8a6ab3de8bbf7705059bc7b7ab00a9ed6fbf4333e62543ec13bbf23296f1c205
hced-Rattenberg1809-1|6e722d3e02725bc50d49c8f37c9e2157c0bf9ce0f18a58e6ae854b11d457e30b
hced-Saldanha Bay1796-1|7499d0546eab05a6aef59e094dfac4b8cf57118f421c95fcca252817749abff1
hced-Sandwich1460-1|f971b93fe03fd549567b589b024abd75da8d2e4b6154b9f7897a0c62c77179ed
hced-St Albans1455-1|31d5b052f4ad8487944405d0689f5c1095709cb9d525277964e4ea565a3c7c82
hced-St Albans1461-1|c7b22538d2473c4404d1a5bc54a7054fcc30ae7e8dd8a2e4e8b66dfa2c615155
hced-Stoke1487-1|8e2a5a0f63ccd1762f429a951285a146b5722fa6e326d445d0c82c0030331306
hced-Surinam1800-1|c73abfa9c3f457efc87a61836f2e7d767f71bf9ea7de368e4db4a9681b2468c5
hced-Surinam1804-1|425f7fdecba91969124f85b69430d0c3f9151293b0da86442e88d855ed803603
hced-Tewkesbury1471-1|c332866b6d068786d8d9697500d7a5aae6c612302213ee42fdd794258cffefa1
hced-Towton1461-1|cd22d7ffd3e3e7ae9bca43f8e0f76a557f18c2e926212ff06f7eba2348bdb74c
hced-Twt Hill1463-1|a49294775969d4c3412084b3655266094c6ecdd5b9df01eb4c4c3ad2dc2a24a7
hced-Villepion1870-1|68bf82efb5f704837eae4a0906b5964a6030845e0ca85341cb5ec1e2dfb02db7
hced-Wakefield1460-1|fab27047c3bca9a35779bb3d9918a423ccebe7de4e22cba93b61e0d66d611832
hced-Werbach1866-1|f9f5fba27b9303a5f4567be100f9b11d278414f6f1d59d1f9f3fe4a64207d715
hced-West Irian1962-1|ff6f689dc5979c8d8447373c173a92a1f559546cbdf9280cbf404deef6684ccb
hced-Wiesenthal1866-1|8e229e885e6b0e7cc237bbec44934734fca98e8136a2405c1f202cac5988ceef
hced-Zella1866-1|8b2f756e8d455ee7ecfacfb69c237acc446de898f2cdb5efd6baed1efa2ec0c9
""".strip().splitlines()
)


WAVE7_WEST_ROSES_NEW_IDS = frozenset(
    {
        "hced-Twt Hill1463-1",
        "hced-Bamburgh1464-1",
        "hced-Caister Castle1469-1",
        "hced-Lose-Coat Field1470-1",
        "hced-Bosworth Field1485-1",
    }
)

WAVE7_WEST_ROSES_PROTECTED_IDS = frozenset(
    {
        "hced-St Albans1455-1",
        "hced-Blore Heath1459-1",
        "hced-Ludford Bridge1459-1",
        "hced-Northampton1460-1",
        "hced-Sandwich1460-1",
        "hced-Wakefield1460-1",
        "hced-Mortimers Cross1461-1",
        "hced-St Albans1461-1",
        "hced-Towton1461-1",
        "hced-Hedgeley Moor1464-1",
        "hced-Hexham1464-1",
        "hced-Tewkesbury1471-1",
        "hced-Stoke1487-1",
    }
)

WAVE7_WEST_BAVARIA_NEW_IDS = frozenset(
    {
        "hced-Heidelberg1622-1",
        "hced-Freiburg, Wurttemberg1644-1",
        "hced-Munderkingen1703-1",
        "hced-Donauworth1704-1",
        "hced-Amberg1745-1",
        "hced-Rattenberg1809-1",
        "hced-Hanau1813-1",
        "hced-Gerchsheim1866-1",
        "hced-Hammelburg1866-1",
        "hced-Helmstadt1866-1",
        "hced-Kissingen1866-1",
        "hced-Werbach1866-1",
        "hced-Wiesenthal1866-1",
        "hced-Zella1866-1",
    }
)

WAVE7_WEST_NETHERLANDS_NEW_IDS = frozenset(
    {
        "hced-Ambon1796-1",
        "hced-Colombo1796-1",
        "hced-Saldanha Bay1796-1",
        "hced-Camperdown1797-1",
        "hced-Groote Keeten1799-1",
        "hced-Surinam1800-1",
        "hced-Surinam1804-1",
        "hced-Blueberg1806-1",
        "hced-Lombok Strait1942-1",
        "hced-West Irian1962-1",
    }
)

WAVE7_WEST_HOLD_IDS = frozenset(
    {
        "hced-Boroughbridge1322-1",
        "hced-Alnwick1462-1",
        "hced-Edgecote1469-1",
        "hced-Dunstable1461-1",
        "hced-Ferrybridge1461-1",
        "hced-Gammelsdorf1313-1",
        "hced-Muhldorf1322-1",
        "hced-Bazeilles1870-1",
        "hced-Chatillon-sous-Bagneux1870-1",
        "hced-Coulmiers1870-1",
        "hced-Villepion1870-1",
        "hced-Marga1946-1",
        "hced-Jogjakarta1948-1",
    }
)

WAVE7_WEST_DUTCH_PROTECTED_IDS = frozenset({"hced-Batavia1811-1", "hced-Java1811-1"})


_RAW_ROWS_ZLIB_B64 = """
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
cKzYWuUHnzVfCjFqoMW26I+Oln/9P3zt24A=
"""


def _canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


_EMBEDDED_ROWS: list[dict[str, Any]] = json.loads(
    zlib.decompress(base64.b64decode(_RAW_ROWS_ZLIB_B64)).decode("utf-8")
)
_ROWS_BY_ID = {str(row["candidate_id"]): row for row in _EMBEDDED_ROWS}


def _slug(value: str) -> str:
    output: list[str] = []
    previous_separator = False
    for char in value.casefold():
        if char.isalnum():
            output.append(char)
            previous_separator = False
        elif not previous_separator:
            output.append("_")
            previous_separator = True
    return "".join(output).strip("_")


def _bavaria_entity(year: int) -> str:
    if 1506 <= year <= 1622:
        return "duchy_bavaria_unified_1506"
    if 1623 <= year <= 1805:
        return "electorate_bavaria_1623"
    if 1806 <= year <= 1918:
        return "kingdom_bavaria_1806"
    raise ValueError(f"reviewed Bavaria row falls outside all identity windows: {year}")


def _side_entities(candidate_id: str, label: str, year: int) -> list[str]:
    if candidate_id == "hced-Bosworth Field1485-1":
        return (
            ["tudor_lancastrian_army_1485", "stanley_forces_1485"]
            if label == "Lancastrians"
            else ["yorkist_royal_army_1485"]
        )
    if candidate_id == "hced-Stoke1487-1":
        return (
            ["kingdom_england"]
            if label == "England"
            else ["simnel_yorkist_rebellion_1487"]
        )
    if candidate_id == "hced-Caister Castle1469-1":
        return (
            ["duke_norfolk_forces_1469"]
            if label == "Yorkists"
            else ["paston_retainers_1469"]
        )
    if candidate_id == "hced-Lose-Coat Field1470-1":
        return (
            ["edward_iv_royal_army_1470"]
            if label == "Yorkists"
            else ["welles_rebel_army_1470"]
        )
    if label == "Yorkists":
        return ["yorkist_faction_1455"]
    if label == "Lancastrians":
        return ["lancastrian_faction_1455"]
    if label == "Bavaria":
        return [_bavaria_entity(year)]
    if label == "Netherlands, England, German Protestants":
        return [
            "dutch_republic",
            "kingdom_england",
            "palatine_protestant_forces_1622",
        ]
    if label == "United Kingdom, Baden":
        return ["kingdom_england", "baden_imperial_forces_1704"]
    if label == "France":
        return ["kingdom_france" if year == 1644 else "first_french_empire"]
    if label == "Habsburg Empire":
        return ["habsburg_monarchy" if year <= 1804 else "austrian_empire"]
    if label == "Austria":
        return ["habsburg_monarchy"]
    if label == "Prussia":
        return ["kingdom_prussia"]
    if label == "United Kingdom":
        return ["united_kingdom"]
    if label == "United Kingdom, Russia":
        return ["united_kingdom", "russian_empire"]
    if label == "Netherlands":
        return [
            "batavian_republic_1795" if year <= 1806 else "kingdom_netherlands_1815"
        ]
    if label == "Japan":
        return ["empire_japan"]
    if label == "Indonesia":
        return ["clio_id_indonesian_rep_1946_87b95608"]
    raise ValueError(f"unreviewed WEST participant label: {label!r}")


def _cohort(candidate_id: str) -> str:
    if candidate_id in WAVE7_WEST_ROSES_NEW_IDS:
        return "wars_of_the_roses"
    if candidate_id in WAVE7_WEST_BAVARIA_NEW_IDS:
        return "bavaria_sequence"
    if candidate_id in WAVE7_WEST_NETHERLANDS_NEW_IDS:
        return "netherlands_sequence"
    raise ValueError(
        f"candidate is not in the WEST promotion inventory: {candidate_id}"
    )


def _canonical_event(candidate_id: str, row: dict[str, Any]) -> dict[str, Any]:
    year_low = int(row["year_low"])
    year_high = int(row["year_high"])
    name = str(row["name"])
    granularity = "engagement"
    exact_date: str | None = None
    if candidate_id == "hced-Bosworth Field1485-1":
        name = "Battle of Bosworth Field"
        exact_date = "1485-08-22"
    elif candidate_id == "hced-Twt Hill1463-1":
        name = "Battle of Twthill"
        year_low = year_high = 1461
        exact_date = "1461-10-16"
    elif candidate_id == "hced-Bamburgh1464-1":
        name = "Siege of Bamburgh Castle"
        granularity = "siege"
    elif candidate_id == "hced-Caister Castle1469-1":
        name = "Siege of Caister Castle"
        granularity = "siege"
    elif candidate_id == "hced-Lose-Coat Field1470-1":
        name = "Battle of Losecoat Field"
        exact_date = "1470-03-12"
    elif candidate_id == "hced-Heidelberg1622-1":
        name = "Siege of Heidelberg"
        granularity = "siege"
    elif candidate_id == "hced-Donauworth1704-1":
        name = "Battle of Schellenberg"
    elif candidate_id == "hced-Blueberg1806-1":
        name = "Battle of Blaauwberg"
        exact_date = "1806-01-08"
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{year_high}",
        "name": name,
        "year_low": year_low,
        "year_high": year_high,
        "date_precision": "exact_day" if exact_date else "year",
        "exact_date": exact_date,
        "granularity": granularity,
    }


def _evidence_refs(candidate_id: str, year: int) -> list[str]:
    if candidate_id in WAVE7_WEST_ROSES_NEW_IDS:
        roses_refs = {
            "hced-Twt Hill1463-1": ["wave7_west_rcahmw_twt"],
            "hced-Bamburgh1464-1": ["wave7_west_he_bamburgh"],
            "hced-Caister Castle1469-1": ["wave7_west_he_caister"],
            "hced-Lose-Coat Field1470-1": ["wave7_west_ehr_lincolnshire_1470"],
            "hced-Bosworth Field1485-1": ["wave7_west_he_bosworth"],
        }
        return roses_refs[candidate_id]
    if candidate_id in WAVE7_WEST_BAVARIA_NEW_IDS:
        if year <= 1622:
            refs = ["wave7_west_hdbg_duchy"]
        elif year <= 1805:
            refs = ["wave7_west_hdbg_electorate"]
        else:
            refs = ["wave7_west_hdbg_kingdom"]
        if candidate_id == "hced-Heidelberg1622-1":
            refs.append("wave7_west_ukna_palatinate")
        if candidate_id == "hced-Donauworth1704-1":
            refs.append("wave7_west_hdbg_schellenberg")
        return refs
    refs = ["wave7_west_royal_house_netherlands"]
    if candidate_id == "hced-Blueberg1806-1":
        refs.append("wave7_west_saho_blaauwberg")
    if year >= 1815:
        refs.append("wave7_west_nl_constitution_1815")
    return refs


def _promotion_contract(candidate_id: str) -> dict[str, Any]:
    row = _ROWS_BY_ID[candidate_id]
    year = int(row["year_low"])
    if candidate_id == "hced-Bamburgh1464-1":
        winner_side = 2
    elif row["winner_raw"] == row["side_1_raw"]:
        winner_side = 1
    elif row["winner_raw"] == row["side_2_raw"]:
        winner_side = 2
    else:
        raise ValueError(
            f"WEST outcome is not aligned to a source side: {candidate_id}"
        )
    corrected_roses = {
        "hced-Twt Hill1463-1": {
            "prior_wave6_hold_resolution": "corrected_exact_date",
            "outcome_source_ids": ["wave7_west_rcahmw_twt"],
            "outcome_source_family_ids": ["rcahmw_coflein"],
        },
        "hced-Bamburgh1464-1": {
            "prior_wave6_hold_resolution": "corrected_outcome",
            "outcome_source_ids": ["wave7_west_he_bamburgh"],
            "outcome_source_family_ids": ["historic_england"],
            "source_outcome_override": True,
        },
        "hced-Caister Castle1469-1": {
            "prior_wave6_hold_resolution": "corrected_participants",
            "outcome_source_ids": ["wave7_west_he_caister"],
            "outcome_source_family_ids": ["historic_england"],
        },
        "hced-Lose-Coat Field1470-1": {
            "prior_wave6_hold_resolution": "corrected_participants",
            "outcome_source_ids": ["wave7_west_ehr_lincolnshire_1470"],
            "outcome_source_family_ids": ["english_historical_review"],
        },
        "hced-Bosworth Field1485-1": {
            "prior_wave6_hold_resolution": "candidate_specific_coalition",
            "outcome_source_ids": ["wave7_west_he_bosworth"],
            "outcome_source_family_ids": ["historic_england"],
        },
    }
    correction = corrected_roses.get(
        candidate_id,
        {
            "outcome_source_ids": ["hced_dataset"],
            "outcome_source_family_ids": ["hced"],
        },
    )
    return {
        "cohort": _cohort(candidate_id),
        "raw_row": row,
        "raw_row_sha256": WAVE7_WEST_EXPECTED_HASHES[candidate_id],
        "canonical_event": _canonical_event(candidate_id, row),
        "side_1_entity_ids": _side_entities(candidate_id, str(row["side_1_raw"]), year),
        "side_2_entity_ids": _side_entities(candidate_id, str(row["side_2_raw"]), year),
        "result": {"type": "decisive", "winner_side": winner_side},
        "evidence_refs": _evidence_refs(candidate_id, year),
        **correction,
        "audit_note": (
            "Exact candidate fingerprint, tactical outcome, complete reviewed side "
            "roster, and identity windows are pinned by the WEST contract."
        ),
    }


WAVE7_WEST_HCED_CONTRACTS = {
    candidate_id: _promotion_contract(candidate_id)
    for candidate_id in sorted(
        WAVE7_WEST_ROSES_NEW_IDS
        | WAVE7_WEST_BAVARIA_NEW_IDS
        | WAVE7_WEST_NETHERLANDS_NEW_IDS
    )
}


_HOLD_SPECS = {
    "hced-Boroughbridge1322-1": (
        "wars_of_the_roses",
        "anachronistic_faction_label",
        "The 1322 row predates the 1455-1471 Lancastrian faction identity.",
        ["wave7_west_he_towton"],
    ),
    "hced-Alnwick1462-1": (
        "wars_of_the_roses",
        "coalition_incomplete_mandatory",
        "The composite France/Scotland/Lancastrian side needs candidate-level "
        "coalition adjudication before rating.",
        ["wave7_west_he_towton"],
    ),
    "hced-Edgecote1469-1": (
        "wars_of_the_roses",
        "party_identity_ambiguous",
        "The named Pembroke and Devon forces cannot be collapsed into a timeless "
        "Lancastrian label without candidate-level review.",
        ["wave7_west_he_towton"],
    ),
    "hced-Dunstable1461-1": (
        "wars_of_the_roses",
        "component_inflation_existing_wave6_hold",
        "Preserved Wave 6 hold: this was a small Yorkist outpost in the "
        "immediate Second St Albans operation, not a separately adjudicated "
        "battle contract.",
        ["wave7_west_richard_iii_st_albans"],
    ),
    "hced-Ferrybridge1461-1": (
        "wars_of_the_roses",
        "multi_phase_component_existing_wave6_hold",
        "Preserved Wave 6 hold: the changing bridge and Dintingdale actions "
        "immediately precede Towton and remain unseparated for Elo.",
        ["wave7_west_he_towton"],
    ),
    "hced-Gammelsdorf1313-1": (
        "bavaria_sequence",
        "divided_duchy_boundary",
        "The battle predates the unified 1506 duchy and the raw Bavaria label does "
        "not identify the correct divided duchy.",
        ["wave7_west_hdbg_duchy"],
    ),
    "hced-Muhldorf1322-1": (
        "bavaria_sequence",
        "divided_duchy_boundary",
        "The battle predates the unified 1506 duchy and the raw Bavaria label does "
        "not identify the correct divided duchy.",
        ["wave7_west_hdbg_duchy"],
    ),
    "hced-Bazeilles1870-1": (
        "bavaria_sequence",
        "year_only_france_transition",
        "A year-only France label cannot choose a side of the 4 September 1870 "
        "Second Empire/Third Republic boundary.",
        ["wave7_west_hdbg_kingdom", "wave7_west_elysee_1870"],
    ),
    "hced-Chatillon-sous-Bagneux1870-1": (
        "bavaria_sequence",
        "year_only_france_transition",
        "A year-only France label cannot choose a side of the 4 September 1870 "
        "Second Empire/Third Republic boundary.",
        ["wave7_west_hdbg_kingdom", "wave7_west_elysee_1870"],
    ),
    "hced-Coulmiers1870-1": (
        "bavaria_sequence",
        "year_only_france_transition",
        "A year-only France label cannot choose a side of the 4 September 1870 "
        "Second Empire/Third Republic boundary.",
        ["wave7_west_hdbg_kingdom", "wave7_west_elysee_1870"],
    ),
    "hced-Villepion1870-1": (
        "bavaria_sequence",
        "year_only_france_transition",
        "A year-only France label cannot choose a side of the 4 September 1870 "
        "Second Empire/Third Republic boundary.",
        ["wave7_west_hdbg_kingdom", "wave7_west_elysee_1870"],
    ),
    "hced-Marga1946-1": (
        "netherlands_sequence",
        "counterparty_identity_unresolved",
        "The Indonesian Rebels counterparty needs a candidate-specific identity.",
        ["wave7_west_nl_constitution_1815"],
    ),
    "hced-Jogjakarta1948-1": (
        "netherlands_sequence",
        "counterparty_identity_unresolved",
        "The Indonesian Rebels counterparty needs a candidate-specific identity.",
        ["wave7_west_nl_constitution_1815"],
    ),
}


WAVE7_WEST_HCED_HOLDS = {
    candidate_id: {
        "cohort": cohort,
        "hold_category": category,
        "hold_reason": reason,
        "evidence_refs": evidence_refs,
        "raw_row": _ROWS_BY_ID[candidate_id],
        "raw_row_sha256": WAVE7_WEST_EXPECTED_HASHES[candidate_id],
        "inherited_wave6_hold": candidate_id
        in {"hced-Dunstable1461-1", "hced-Ferrybridge1461-1"},
    }
    for candidate_id, (
        cohort,
        category,
        reason,
        evidence_refs,
    ) in sorted(_HOLD_SPECS.items())
}


def _protected_roster(candidate_id: str, row: dict[str, Any]) -> list[dict[str, str]]:
    if candidate_id in WAVE7_WEST_DUTCH_PROTECTED_IDS:
        side_1 = ["united_kingdom"]
        side_2 = ["clio_nl_dutch_emp_2_1811_2e0bb80e"]
    else:
        year = int(row["year_low"])
        side_1 = _side_entities(candidate_id, str(row["side_1_raw"]), year)
        side_2 = _side_entities(candidate_id, str(row["side_2_raw"]), year)
    winner_is_side_1 = row["winner_raw"] == row["side_1_raw"]
    roster: list[dict[str, str]] = []
    for side_index, entity_ids in ((1, side_1), (2, side_2)):
        termination = (
            "engagement_victory"
            if (side_index == 1) == winner_is_side_1
            else "engagement_defeat"
        )
        roster.extend(
            {"entity_id": entity_id, "termination": termination}
            for entity_id in entity_ids
        )
    return roster


WAVE7_WEST_PROTECTED_RATED = {
    candidate_id: {
        "cohort": (
            "netherlands_sequence"
            if candidate_id in WAVE7_WEST_DUTCH_PROTECTED_IDS
            else "wars_of_the_roses"
        ),
        "protection_category": (
            "rated_1811_dutch_identity_nonmigration"
            if candidate_id in WAVE7_WEST_DUTCH_PROTECTED_IDS
            else "correct_existing_candidate_ownership"
        ),
        "protection_reason": (
            "The 1811 Dutch Empire identity is already candidate-owned and must not "
            "be migrated into the post-1815 Kingdom of the Netherlands."
            if candidate_id in WAVE7_WEST_DUTCH_PROTECTED_IDS
            else "The existing candidate is already correctly owned by the narrow "
            "Wars of the Roses actor identities and must not be promoted twice."
        ),
        "raw_row": _ROWS_BY_ID[candidate_id],
        "raw_row_sha256": WAVE7_WEST_EXPECTED_HASHES[candidate_id],
        "expected_event_id": f"hced_label_{_slug(candidate_id)}",
        "expected_identity_resolution": "label",
        "expected_roster": _protected_roster(candidate_id, _ROWS_BY_ID[candidate_id]),
    }
    for candidate_id in sorted(
        WAVE7_WEST_ROSES_PROTECTED_IDS | WAVE7_WEST_DUTCH_PROTECTED_IDS
    )
}


WAVE7_WEST_AUDIT_SIGNATURE = (
    "0b183a29f69997bef7b6ac87c5e6e19791eba55713daee55fbae64432faf91af"
)
