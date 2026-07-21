from __future__ import annotations

"""Exact, lane-local policy contracts for the Wave 6 modern-history audit.

The Phase 1 package proposed 105 rows. Source/coalition, cross-lane, and
identity-boundary rechecks hold 36 rather than rewriting their reviewed
meaning. The implemented inventory is therefore 69 exact contracts
(60 HCED and nine IWBD battles). Egypt and transitional Spanish governments
remain held until an atomic, time-bounded identity migration is reviewed;
Syria's 1967 contract targets the reviewed post-UAR series.
"""

from typing import Any


HCED_SOURCE_SNAPSHOT = "data/raw/hced/20260713T161517Z-92a22e49c20d.csv"
IWD_SOURCE_SNAPSHOT = "data/raw/iwd-1.21/20260713T173251Z-fd6cfbcbebed.tsv"
IWBD_SOURCE_SNAPSHOT = "data/raw/iwbd/20260713T161518Z-fcf5747cf94b.bin"

HCED_SOURCE_CONTRACT_FIELDS = (
    "candidate_id",
    "loser_raw",
    "name",
    "participants_raw",
    "seshat_side_1_candidates",
    "seshat_side_2_candidates",
    "side_1_raw",
    "side_2_raw",
    "source_record_id",
    "source_row",
    "source_snapshot",
    "war_names",
    "winner_raw",
    "year_high",
    "year_low",
)
IWD_SOURCE_CONTRACT_FIELDS = (
    "adversaries",
    "allies",
    "candidate_id",
    "end_year",
    "initiators",
    "joiner_decision",
    "name",
    "parent_war_id",
    "parent_war_name",
    "source_component_id",
    "source_rows",
    "source_snapshot",
    "start_year",
    "targets",
    "terminal_outcome",
    "terminal_outcome_code",
)
IWBD_SOURCE_CONTRACT_FIELDS = (
    "attacker_raw",
    "battle_level_victor_role",
    "candidate_id",
    "defender_raw",
    "duration_days",
    "end_date",
    "name",
    "source_row",
    "source_snapshot",
    "start_date",
    "war_level_victor_role",
    "war_name",
    "winner_raw",
)


def _hced_contract(
    side_1_ids: tuple[str, ...],
    side_2_ids: tuple[str, ...],
    outcome: str,
    evidence_source_ids: tuple[str, ...],
    sha256: str,
) -> dict[str, Any]:
    return {
        "source_contract": {
            "field_names": HCED_SOURCE_CONTRACT_FIELDS,
            "sha256": sha256,
        },
        "side_1": side_1_ids,
        "side_2": side_2_ids,
        "outcome": outcome,
        "evidence_source_ids": evidence_source_ids,
    }


def _iwd_component_contract(sha256: str) -> dict[str, Any]:
    return {"field_names": IWD_SOURCE_CONTRACT_FIELDS, "sha256": sha256}


def _iwbd_contract(
    attacker_ids: tuple[str, ...],
    defender_ids: tuple[str, ...],
    evidence_source_ids: tuple[str, ...],
    sha256: str,
) -> dict[str, Any]:
    return {
        "source_contract": {
            "field_names": IWBD_SOURCE_CONTRACT_FIELDS,
            "sha256": sha256,
        },
        "attacker": tuple((entity_id, entity_id) for entity_id in attacker_ids),
        "defender": tuple((entity_id, entity_id) for entity_id in defender_ids),
        "evidence_source_ids": evidence_source_ids,
    }


WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Binakayan1896-1": _hced_contract(
        ("philippine_revolutionary_forces",),
        ("spanish_empire",),
        "side_1",
        (
            "philippines_loc_chronology",
            "philippines_army_cmh",
            "philippines_nhcp_binakayan",
        ),
        "89e767bfe55d0d85099db8b6afd13ac92ea4786a11d5c80f57bff76d86022bf4",
    ),
    "hced-Imus1896-1": _hced_contract(
        ("philippine_revolutionary_forces",),
        ("spanish_empire",),
        "side_1",
        ("philippines_loc_chronology", "philippines_army_cmh", "philippines_nhcp_imus"),
        "12ef5a93386649d00fc5b3295fa46dae3cf923039a7922060c3b30ed471b3c56",
    ),
    "hced-Imus1897-1": _hced_contract(
        ("spanish_empire",),
        ("philippine_revolutionary_forces",),
        "side_1",
        ("philippines_loc_chronology", "philippines_army_cmh", "philippines_nhcp_imus"),
        "1aeb98547226711e5ba054b24d35be0a4a5269997af42635d18c3160c5e3eaa8",
    ),
    "hced-Zapote Bridge1897-1": _hced_contract(
        ("philippine_revolutionary_forces",),
        ("spanish_empire",),
        "side_1",
        (
            "philippines_loc_chronology",
            "philippines_army_cmh",
            "philippines_nhcp_zapote",
            "philippines_nhcp_binakayan",
        ),
        "655d5dc632ff12ad105a5086409a914305cc113a881202600716678e444795e4",
    ),
    "hced-Bagbag1899-1": _hced_contract(
        ("united_states",),
        ("first_philippine_republic",),
        "side_1",
        ("philippines_loc_chronology", "philippines_army_cmh"),
        "c049e1caa8502e23f0d4aa39452207abba2f7daccc428750e43978e06b64c3cb",
    ),
    "hced-Calumpit1899-1": _hced_contract(
        ("united_states",),
        ("first_philippine_republic",),
        "side_1",
        ("philippines_loc_chronology", "philippines_army_cmh"),
        "d5e15637fa00976380d351ee00fb3675164ca921f994787b90a668a0702fbb2f",
    ),
    "hced-Iloilo1899-1": _hced_contract(
        ("united_states",),
        ("first_philippine_republic",),
        "side_1",
        ("philippines_loc_chronology", "philippines_army_cmh"),
        "c9e47bd7202080f69b757eb3003100a5b97dc7f3282108a8b13ee5fdee86cd35",
    ),
    "hced-Malolos1899-1": _hced_contract(
        ("united_states",),
        ("first_philippine_republic",),
        "side_1",
        ("philippines_loc_chronology", "philippines_army_cmh"),
        "78c57e602b1a88ccdd9fc60313e98c6b0edac1b57c783786f366f9e6416dbfc8",
    ),
    "hced-Manila1899-1": _hced_contract(
        ("united_states",),
        ("first_philippine_republic",),
        "side_1",
        ("philippines_loc_chronology", "philippines_army_cmh"),
        "b92c10b17c5b3a4d592f29527c093d5fe611d1583fc4a0c57fa486abce79d0b7",
    ),
    "hced-Polo1899-1": _hced_contract(
        ("united_states",),
        ("first_philippine_republic",),
        "side_1",
        ("philippines_loc_chronology", "philippines_army_cmh"),
        "9102d9149d6c235003477cded4dab6ff06c8e740700a7da0b72f53a65c945bbc",
    ),
    "hced-San Isidro1899-1": _hced_contract(
        ("united_states",),
        ("first_philippine_republic",),
        "side_1",
        ("philippines_loc_chronology", "philippines_army_cmh"),
        "de133db3be610785b1afda40f259cfdc7c258b29831567ef4273eea661ea1c5f",
    ),
    "hced-Tirad Pass1899-1": _hced_contract(
        ("united_states",),
        ("first_philippine_republic",),
        "side_1",
        (
            "philippines_loc_chronology",
            "philippines_army_cmh",
            "philippines_nhcp_tirad",
        ),
        "e784317b84fccdae874ebb0517d1500bafc5b4a9c89832d4c1c0ff9413bd7351",
    ),
    "hced-Vigan1899-1": _hced_contract(
        ("united_states",),
        ("first_philippine_republic",),
        "side_1",
        ("philippines_loc_chronology", "philippines_army_cmh"),
        "98c7ecb3dbad26351375e99afe8d9deaf1fcdbff402f5c689c89df4076e64314",
    ),
    "hced-Zapote River1899-1": _hced_contract(
        ("united_states",),
        ("first_philippine_republic",),
        "side_1",
        ("philippines_loc_chronology", "philippines_army_cmh"),
        "3ea6febb321778f2ef9497ef598dbce2fde4d9ec251487588e88b901a49d1e6e",
    ),
    "hced-Ciudad Juarez1913-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists",),
        "5548c62a6a72f0eeebb055ce7551a5856bc71f14a7d6fdfad47f611421dd33d6",
    ),
    "hced-Ciudad Victoria1913-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists",),
        "669fdc541f87e128b9f350aac55a1801b26be028998a5a85e13a7a95452a59af",
    ),
    "hced-Durango1913-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists",),
        "2492050f7730694104305a582370b21272cb3d1ff65e16e49d09ec08d1e4407e",
    ),
    "hced-Matamaros1913-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists",),
        "a49131586ca2b03951a875edf9e36ac6e05df377bbd0a05db7f424c9ac0735e1",
    ),
    "hced-San Andres1913-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists",),
        "88c21ff61aaf6afbed7a015a84f141d5c9d43700349e3457d3a348094214e0a5",
    ),
    "hced-Santa Maria1913-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists",),
        "5f806a86a40800e61aa94b8e1f1c1543b4e96b02d1122eb76391b284fd85286f",
    ),
    "hced-Santa Rosa1913-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists",),
        "59d051d9c4f1c80e7cf8dc559ee3f13cf91c3616255787bcfd14f08d526b839d",
    ),
    "hced-Satillo1913-1": _hced_contract(
        ("huerta_federal_army",),
        ("constitutionalist_army_mexico",),
        "side_1",
        ("mexico_constitutionalists",),
        "9b28699b61f8b957cfc8f2580ad0a117890faab6f394442621fbb72442295cf0",
    ),
    "hced-Tierra Blanca1913-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists",),
        "dd777ffd85c6da50e3065685330c420d8c18ee5f8e0a047913b85a5663a9dbf7",
    ),
    "hced-Torreon1913-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists",),
        "7b324b0296103e4bb22f0a0ba998563618ae88485f53f6b1b834f1be3d3d6ad4",
    ),
    "hced-Orendain1914-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists", "mexico_orendain"),
        "effbacf6efe54691721674431d0e3c9baf6d994227b86998fb474a9dc67c04b7",
    ),
    "hced-Paredon1914-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists",),
        "6360953b7ffe42f5d7e2af9d6bcab8ba0e8e63fbedacec3845ff6cec379df8d9",
    ),
    "hced-Tampico1914-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists",),
        "ad871fb0aa4e4e20d8a36b03c4ce61930f6c2daea22504c2e892cb412bf5d70a",
    ),
    "hced-Torreon1914-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists", "mexico_torreon"),
        "034eb152fddb9535929577b321987b12005014762e117d09d904efcbbe3e95e4",
    ),
    "hced-Zacatecas1914-1": _hced_contract(
        ("constitutionalist_army_mexico",),
        ("huerta_federal_army",),
        "side_1",
        ("mexico_constitutionalists", "mexico_zacatecas"),
        "b256910fab1a390f2f9bfbd5cc2467e43147969ab9816ca293691b72b8bcdd7c",
    ),
    "hced-El Teb (1st)1884-1": _hced_contract(
        ("mahdist_ansar_forces",),
        ("egypt_muhammad_ali",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "20dcda94600919f36e248814654f24824f6d6942a4cccf8c27f32155327ebaa7",
    ),
    "hced-El Teb (2nd)1884-1": _hced_contract(
        ("united_kingdom",),
        ("mahdist_ansar_forces",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "291cbd901aa193464171656580f6d8d78fe614d600125b047819e8f0ba76b608",
    ),
    "hced-Tamai1884-1": _hced_contract(
        ("united_kingdom",),
        ("mahdist_ansar_forces",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "ec76f05dce05dbf7a1e31941f06693f599b0ce3c8a0a8399eca01cd80832242b",
    ),
    "hced-Ginniss1885-1": _hced_contract(
        ("united_kingdom", "egypt_muhammad_ali"),
        ("mahdist_ansar_forces",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "bffeb1820032b973f161f4c6b5d59b0805287fdd0ee520bd2c5a1baed69e6c94",
    ),
    "hced-Hashin1885-1": _hced_contract(
        ("united_kingdom",),
        ("mahdist_ansar_forces",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "ee0cd55e9d819a629d21d68a0e63da928225e446981e849c7190580acbdbdf7f",
    ),
    "hced-Tofrek1885-1": _hced_contract(
        ("united_kingdom",),
        ("mahdist_ansar_forces",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "cdb5a98ab808fc6e9b34a9dbd4075290a147e16bb0e2063280e1188ca9826ceb",
    ),
    "hced-Gemaizeh1888-1": _hced_contract(
        ("united_kingdom", "egypt_muhammad_ali"),
        ("mahdist_ansar_forces",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "13d2c5de8047dd71cc98665d4e892b319251971eb276bb5096418cfdd1d91920",
    ),
    "hced-Toski1889-1": _hced_contract(
        ("egypt_muhammad_ali",),
        ("mahdist_ansar_forces",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "5a8bc17b2be2a8b3f2c0d02213df768f3f1ceabfb47ea7f5f7cd9e73b75d196c",
    ),
    "hced-Tokar1891-1": _hced_contract(
        ("egypt_muhammad_ali",),
        ("mahdist_ansar_forces",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "98930f851bdf1a9fd8649109ee60887e83be1d2377daf9f0889f73b9ea48da0c",
    ),
    "hced-Firket1896-1": _hced_contract(
        ("egypt_muhammad_ali",),
        ("mahdist_ansar_forces",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "cac049ba2a0fc55b1e590b82f125eb43aa4ee9407102e0fb842d1b4dd3f565bd",
    ),
    "hced-Hafir, Sudan1896-1": _hced_contract(
        ("egypt_muhammad_ali",),
        ("mahdist_ansar_forces",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "d19d83f7f7e1fa1452656bc7ca4288d7b2899817e4979f49d78842ee03c4e604",
    ),
    "hced-Um Diwaykarat1899-1": _hced_contract(
        ("egypt_muhammad_ali",),
        ("mahdist_ansar_forces",),
        "side_1",
        ("mahdist_nam", "mahdist_bm"),
        "16b21687c3ace785dff512baec743968ef9f86275a2584095242fcd712ea9224",
    ),
    "hced-Eshowe1879-1": _hced_contract(
        ("united_kingdom",),
        ("zulu_kingdom",),
        "side_1",
        ("zulu_nam",),
        "e502763a82a786ea12102edf7c718a875b3b3d7fc6b9bb4e887626954d8d417b",
    ),
    "hced-Gingindlovu1879-1": _hced_contract(
        ("united_kingdom",),
        ("zulu_kingdom",),
        "side_1",
        ("zulu_nam",),
        "0ed8618c994b67ff7cc31b6e640cb8d1c2f151d2566cd6a1f2e4e1563be6b587",
    ),
    "hced-Hlobane1879-1": _hced_contract(
        ("zulu_kingdom",),
        ("united_kingdom",),
        "side_1",
        ("zulu_nam",),
        "de621f81978fa318fb7423fbac4ff2ade8b833b365e39f053b6a979468fd7d91",
    ),
    "hced-Khambula1879-1": _hced_contract(
        ("united_kingdom",),
        ("zulu_kingdom",),
        "side_1",
        ("zulu_nam",),
        "7117a836b28dfc38c049d2f38aaeb1d05140d3d7c8dc3d9e134b0c8d106168b3",
    ),
    "hced-Myers Drift1879-1": _hced_contract(
        ("zulu_kingdom",),
        ("united_kingdom",),
        "side_1",
        ("zulu_nam",),
        "b61315eeac2383c57cfdf4ddc7ecdf2933bffecba2b7489256e2c482bc00d512",
    ),
    "hced-Nyezane1879-1": _hced_contract(
        ("united_kingdom",),
        ("zulu_kingdom",),
        "side_1",
        ("zulu_nam",),
        "f00c1fe51a6f61dc8dba7ac373ddc446f15fcfc219b234b2f3fb19a1564b00df",
    ),
    "hced-Rorkes Drift1879-1": _hced_contract(
        ("united_kingdom",),
        ("zulu_kingdom",),
        "side_1",
        ("zulu_nam",),
        "52905b63ab2affc4c73dd47b1455229d5303e94584ceb5c735e098eb49917ff2",
    ),
    "hced-Sihayos Kraal1879-1": _hced_contract(
        ("united_kingdom",),
        ("zulu_kingdom",),
        "side_1",
        ("zulu_nam",),
        "13cfe913e955e3c153d474158a8848ef8272718dbacc921efbacc16032f9d0f0",
    ),
    "hced-Ulundi1879-1": _hced_contract(
        ("united_kingdom",),
        ("zulu_kingdom",),
        "side_1",
        ("zulu_nam",),
        "1709d46df5a09e306074d908f1cb048d87333aae58dabf32f5e8cb01bc957f97",
    ),
    "hced-Saigon1859-1": _hced_contract(
        ("second_french_empire", "spanish_isabelline_monarchy"),
        ("nguyen_dai_nam",),
        "side_1",
        ("nguyen_vnmh", "nguyen_musee_armee"),
        "d4d730bdb65392048909dc6e469223ed9e5870a5c4b73a6d8c4839e9c04b124e",
    ),
    "hced-Hanoi1882-1": _hced_contract(
        ("french_third_republic",),
        ("nguyen_dai_nam",),
        "side_1",
        ("nguyen_vnmh", "nguyen_musee_armee"),
        "09763f834463478f6ea5275beaeb4690966a921ea42ee3089d43708b318080e2",
    ),
    "hced-Hue1883-1": _hced_contract(
        ("french_third_republic",),
        ("nguyen_dai_nam",),
        "side_1",
        ("nguyen_vnmh", "nguyen_musee_armee"),
        "7a5c2442463c11dfca2fa77b4fb14c0cba644919ed014f35e1d90fed390ba7c2",
    ),
    "hced-Oroquieta1872-1": _hced_contract(
        ("kingdom_spain_amadeo_i",),
        ("third_carlist_army",),
        "side_1",
        ("carlist_spanish_army", "carlist_governments"),
        "6f79ddf7c5aa4381b1824f7d45039a1182ee272bde1af6397eee3e5a70fa8266",
    ),
    "hced-Maneru1873-1": _hced_contract(
        ("third_carlist_army",),
        ("first_spanish_republic",),
        "side_1",
        ("carlist_spanish_army", "carlist_governments"),
        "e7b3d32c18f8cd0f9eecd7ddd9e9051bd32b71d97aa3b0529eec23f84c459dd4",
    ),
    "hced-Montejurra1873-1": _hced_contract(
        ("third_carlist_army",),
        ("first_spanish_republic",),
        "side_1",
        ("carlist_spanish_army", "carlist_governments"),
        "db74cfb378e5f1cc6adaffa4528a30b1dbe58edc06686a6f3fa9bcea57a8ca14",
    ),
    "hced-Somorrostro (1st)1874-1": _hced_contract(
        ("first_spanish_republic",),
        ("third_carlist_army",),
        "side_1",
        ("carlist_spanish_army", "carlist_governments"),
        "54ab84ce9c8c741b9e5bedc128e9965291690539969ba99626598e398963348c",
    ),
    "hced-Somorrostro (2nd)1874-1": _hced_contract(
        ("third_carlist_army",),
        ("first_spanish_republic",),
        "side_1",
        ("carlist_spanish_army", "carlist_governments"),
        "80c7d460a358681c1854a43c7f8387b005d8179c05b8dc4bf3108aaf27a13952",
    ),
    "hced-Trevino1875-1": _hced_contract(
        ("spanish_empire",),
        ("third_carlist_army",),
        "side_1",
        ("carlist_spanish_army", "carlist_governments"),
        "41f86ac42c3fd0e95d1912bfef7640e5ddf0c949b45bb2ddcffdcf42c38b75b1",
    ),
    "hced-Montejurra1876-1": _hced_contract(
        ("spanish_empire",),
        ("third_carlist_army",),
        "side_1",
        ("carlist_spanish_army", "carlist_governments"),
        "f081af2e6176244d1d36a61aecf2e982f319d7eae1269ab5f395ce1eb0bb67ee",
    ),
    "hced-Pirot1885-1": _hced_contract(
        ("principality_bulgaria",),
        ("kingdom_serbia",),
        "side_1",
        ("bulgaria_usni", "bulgaria_iwm"),
        "b4880ffb5288c2e1b4d4eaf8e5c8c304e8113a04c94fdf5c5539172cfab96a69",
    ),
    "hced-Slivnitza1885-1": _hced_contract(
        ("principality_bulgaria",),
        ("kingdom_serbia",),
        "side_1",
        ("bulgaria_usni", "bulgaria_iwm"),
        "df74aaae95d3fb4baea366f141da7070745b953572a35ef26a471ff3e8e83d70",
    ),
    "hced-Chataldja1912-1": _hced_contract(
        ("ottoman_empire",),
        ("kingdom_bulgaria",),
        "side_1",
        ("bulgaria_usni", "bulgaria_iwm"),
        "08fd4a296e7c42584da38d714f379a7248113da07c1d3ce59d6af570e6914d16",
    ),
    "hced-Kirk Kilissa1912-1": _hced_contract(
        ("kingdom_bulgaria",),
        ("ottoman_empire",),
        "side_1",
        ("bulgaria_usni", "bulgaria_iwm"),
        "5615d52cb404bfee60ad453beb5d8041ce314249d5d02689e8267b34cd9f1a8d",
    ),
    "hced-Luleburgaz1912-1": _hced_contract(
        ("kingdom_bulgaria",),
        ("ottoman_empire",),
        "side_1",
        ("bulgaria_usni", "bulgaria_iwm"),
        "7d1bd742a44e549ee9ff8f443c41c5c9110a74314736840699ebcb8cc8132332",
    ),
    "hced-Adrianople (2nd)1913-1": _hced_contract(
        ("ottoman_empire",),
        ("kingdom_bulgaria",),
        "side_1",
        ("bulgaria_usni", "bulgaria_iwm", "turkiye_culture_adrianople_1913"),
        "8a4de8053c0007fc25c5684925c1e231862806b8d3a3d4792d66194393ffbaf2",
    ),
    "hced-Bregalnica1913-1": _hced_contract(
        ("kingdom_serbia",),
        ("kingdom_bulgaria",),
        "side_1",
        ("bulgaria_usni", "bulgaria_iwm"),
        "c5e9739bfdadbe1ff56e999b567e6b81b3521fbf20ad21c014bd3d95f616baf4",
    ),
    "hced-Bulair1913-1": _hced_contract(
        ("kingdom_bulgaria",),
        ("ottoman_empire",),
        "side_1",
        ("bulgaria_usni", "bulgaria_iwm"),
        "7fecbb4663a75a25c843a182bbceb6bfa7608e864cc7a840230f21432054db43",
    ),
    "hced-Kilkis1913-1": _hced_contract(
        ("kingdom_greece",),
        ("kingdom_bulgaria",),
        "side_1",
        ("bulgaria_usni", "bulgaria_iwm"),
        "773487ec2fddba40e52a12b838555b8e5b3de4686c6e19aa419bc1085cc8e0ea",
    ),
    "hced-Kosturino1915-1": _hced_contract(
        ("kingdom_bulgaria",),
        ("united_kingdom",),
        "side_1",
        ("bulgaria_usni", "bulgaria_iwm"),
        "69f2aed60c9aa98217379330a21cc4c627b0e172b24c0f944e486aeec10c669c",
    ),
    "hced-Dobro Polje1918-1": _hced_contract(
        ("kingdom_serbia", "french_third_republic"),
        ("kingdom_bulgaria",),
        "side_1",
        ("bulgaria_usni", "bulgaria_iwm"),
        "eb47deecc8c128f56c1aaa7c97dcefb22ed4afe3650ffcf7e9c746ba5522a102",
    ),
    "hced-Kobryn1812-1": _hced_contract(
        ("russian_empire",),
        ("kingdom_saxony",),
        "side_1",
        ("saxony_kobryn", "saxony_maubeuge"),
        "abe2590ad2b388425733dd172ad7da07b06412d59c0ce071852ff0966bf84c42",
    ),
    "hced-Kalisch1813-1": _hced_contract(
        ("russian_empire",),
        ("kingdom_saxony",),
        "side_1",
        ("saxony_kobryn", "saxony_maubeuge"),
        "0936e23af78e48bcf1ff57873f90180f878c925d3bf6795cf4b46ef9cdac68fb",
    ),
    "hced-Maubeuge1814-1": _hced_contract(
        ("first_french_empire",),
        ("kingdom_saxony",),
        "side_1",
        ("saxony_kobryn", "saxony_maubeuge"),
        "ce33139e57f31a2ab10a3b421e1a84ef9d39db384005485da86ee6c89a1c0eeb",
    ),
}
WAVE6_IWD_REVIEWED_PARENT_CONTRACTS: dict[str, dict[str, Any]] = {
    "55": {
        "component_source_contracts": {
            "iwd-160": _iwd_component_contract(
                "5b3c4b9ed9be6a5aee52ed11065d0d6cfabb22c82909c581b3cb8d2e2e7f50ab"
            ),
            "iwd-161": _iwd_component_contract(
                "fcfd06d04ab1d9c1192df55e63122fb15bbe4e66cfa1d64c854abfc1f009b302"
            ),
            "iwd-162": _iwd_component_contract(
                "dc6c0d680dc07d141a91e0c1a3149deb5827a4c3826ae68563c75b9330e5601f"
            ),
            "iwd-163": _iwd_component_contract(
                "25b5c30a048002c7778fd68401d86e61cf4b07988c63eacbd4629f7e3a9f4c45"
            ),
            "iwd-164": _iwd_component_contract(
                "953089e1678a11a23624b6a37aa22041d3090e8a1d2547fc7b3773b60fc8c767"
            ),
        },
        "party_bindings": {
            "645": "kingdom_iraq",
            "651": "kingdom_egypt_1922",
            "652": "clio_sy_syria_modern_1946_86597c89",
            "660": "clio_q139708_1944_bc8bee86",
            "663": "clio_q810_1947_98de647a",
            "666": "clio_q801_1948_5abea45e",
        },
        "evidence_source_ids": ("arab_israeli_1948_state",),
    }
}
WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS: dict[str, dict[str, Any]] = {
    "iwbd-16-6-55": _iwbd_contract(
        ("second_french_republic",),
        ("roman_republic_1849",),
        ("roman_republic_italian_army",),
        "a8ebbf2e3e44d74da89aaaa06da711d671108ca3def063e39c8e330e7fe2cea4",
    ),
    "iwbd-16-6-56": _iwbd_contract(
        ("roman_republic_1849",),
        ("kingdom_two_sicilies",),
        ("roman_republic_italian_army",),
        "404d9d596c08060ce6f271d8a79baae22fdebf4903dbea34bf8a9409db3a2ea7",
    ),
    "iwbd-16-6-57": _iwbd_contract(
        ("roman_republic_1849",),
        ("kingdom_two_sicilies",),
        ("roman_republic_italian_army",),
        "a63c572183ad8c3214b49a31844a21c884fbfcb765a7751acda76ec011cd0dac",
    ),
    "iwbd-100-36-422": _iwbd_contract(
        ("kingdom_montenegro", "kingdom_serbia"),
        ("ottoman_empire",),
        ("bulgaria_usni",),
        "df37e0607ec3c072526c59879c88c965837a4e3e5b494802097fdfb578640bea",
    ),
    "iwbd-100-36-427": _iwbd_contract(
        ("kingdom_bulgaria", "kingdom_serbia"),
        ("ottoman_empire",),
        ("bulgaria_usni",),
        "49273ec45f7c4920f4b89f8cf0f14505d8a07bb700f9543ec73c17d950e3ba43",
    ),
    "iwbd-169-64-1523": _iwbd_contract(
        ("clio_q801_1948_5abea45e",),
        ("egypt_muhammad_ali",),
        ("six_day_state",),
        "e9c7dea9e3fb0d2aa6921bac98b4bb28d0144113c9255472f0ce571ec22c7c79",
    ),
    "iwbd-169-64-1524": _iwbd_contract(
        ("clio_q801_1948_5abea45e",),
        ("egypt_muhammad_ali",),
        ("six_day_state",),
        "d7628236a191197cb2359f1058428d470640b7d66ce6b6058d209d44c3cca8bf",
    ),
    "iwbd-169-64-1527": _iwbd_contract(
        ("clio_q801_1948_5abea45e",),
        ("egypt_muhammad_ali",),
        ("six_day_state",),
        "bc8383890b5da98a9da04b48ca9adc231fbf2f74e29594a983d22a35aefe5c81",
    ),
    "iwbd-169-64-1529": _iwbd_contract(
        ("clio_q801_1948_5abea45e",),
        ("egypt_muhammad_ali",),
        ("six_day_state",),
        "36dbdf68121c684fe1d0c4f68cb9dbee53dfc7576cd45179799b27772b839f0a",
    ),
    "iwbd-169-64-1530": _iwbd_contract(
        ("clio_q801_1948_5abea45e",),
        ("egypt_muhammad_ali",),
        ("six_day_state",),
        "594f355d6ccd26c0d683a07335eb6eedbccd0b783b2d14357145a3ca924e4ecc",
    ),
    "iwbd-169-64-1531": _iwbd_contract(
        ("clio_q801_1948_5abea45e",),
        ("egypt_muhammad_ali",),
        ("six_day_state",),
        "71d43e5659ebae697320336e16ee79fce02a66ba3e6f88da2e05c0956b9b3eee",
    ),
    "iwbd-169-64-1532": _iwbd_contract(
        ("clio_q801_1948_5abea45e",),
        ("clio_q41137_1973_b05dea50",),
        ("six_day_state",),
        "252e2e934c499a795a8af8bbffe7d787804ee3eb6a88c1952205ec64aaf3d059",
    ),
    "iwbd-207-80-1652": _iwbd_contract(
        ("republic_chad",),
        ("libyan_arab_jamahiriya",),
        ("chad_un_yearbook",),
        "d2136df7caa1c8fcb91903e10515080d86b6d0d060939439019f36f421e628b2",
    ),
    "iwbd-207-80-1653": _iwbd_contract(
        ("libyan_arab_jamahiriya",),
        ("republic_chad",),
        ("chad_un_yearbook",),
        "d780e559a3e92f1feb99804942a87b4d4ca009d2e5971bf6405c15f239bb7d98",
    ),
    "iwbd-207-80-1655": _iwbd_contract(
        ("republic_chad",),
        ("libyan_arab_jamahiriya",),
        ("chad_un_yearbook",),
        "6d73c2fa5939d251e5b3291d56e22c7250a52abf3183cbacf8ea6b79f10a0219",
    ),
}
WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS["iwbd-16-6-55"]["contained_candidate_ids"] = (
    "iwbd-16-6-56",
    "iwbd-16-6-57",
)
WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS["iwbd-100-36-422"]["contained_candidate_ids"] = (
    "iwbd-100-36-427",
)
for _candidate_id in (
    "iwbd-169-64-1523",
    "iwbd-169-64-1524",
    "iwbd-169-64-1527",
):
    WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS[_candidate_id]["contained_candidate_ids"] = (
        "iwbd-169-64-1529",
    )


WAVE6_IWBD_REVIEWED_IDENTITY_COHORTS: dict[str, tuple[str, ...]] = {
    "roman_republic_1849": ("iwbd-16-6-55", "iwbd-16-6-56", "iwbd-16-6-57"),
    "first_balkan_reviewed_parties": ("iwbd-100-36-422", "iwbd-100-36-427"),
    "six_day_fronts": (
        "iwbd-169-64-1523",
        "iwbd-169-64-1524",
        "iwbd-169-64-1527",
        "iwbd-169-64-1529",
        "iwbd-169-64-1530",
        "iwbd-169-64-1531",
        "iwbd-169-64-1532",
    ),
    "chad_libya_1987": ("iwbd-207-80-1652", "iwbd-207-80-1653", "iwbd-207-80-1655"),
}

# These exact contracts passed source-row review but failed the independent
# identity-boundary audit. Keep their fingerprints as holds so source drift is
# still detected, while ensuring none can reach a generic fallback path.
WAVE6_HCED_IDENTITY_BOUNDARY_HOLD_REASONS = {
    **{
        candidate_id: (
            "identity_boundary: post-1882 Egyptian events require sequential, "
            "time-bounded identities; do not widen the 1805-1882 Muhammad Ali series"
        )
        for candidate_id in (
            "hced-El Teb (1st)1884-1",
            "hced-Ginniss1885-1",
            "hced-Gemaizeh1888-1",
            "hced-Toski1889-1",
            "hced-Tokar1891-1",
            "hced-Firket1896-1",
            "hced-Hafir, Sudan1896-1",
            "hced-Um Diwaykarat1899-1",
        )
    },
    **{
        candidate_id: (
            "identity_boundary: transitional Spanish government requires an atomic "
            "split from the existing Spanish Empire Elo series"
        )
        for candidate_id in (
            "hced-Saigon1859-1",
            "hced-Oroquieta1872-1",
            "hced-Maneru1873-1",
            "hced-Montejurra1873-1",
            "hced-Somorrostro (1st)1874-1",
            "hced-Somorrostro (2nd)1874-1",
        )
    },
}
WAVE6_HCED_IDENTITY_BOUNDARY_HOLD_CONTRACTS = {
    candidate_id: WAVE6_HCED_REVIEWED_CANDIDATE_CONTRACTS.pop(candidate_id)
    for candidate_id in WAVE6_HCED_IDENTITY_BOUNDARY_HOLD_REASONS
}

WAVE6_IWD_IDENTITY_BOUNDARY_HOLD_REASONS: dict[str, str] = {}
WAVE6_IWD_IDENTITY_BOUNDARY_HOLD_CONTRACTS: dict[str, dict[str, Any]] = {}

WAVE6_IWBD_IDENTITY_BOUNDARY_HOLD_REASONS = {
    **{
        candidate_id: (
            "identity_boundary: 1967 Egypt requires a post-UAR, time-bounded identity; "
            "do not widen the 1805-1882 Muhammad Ali series"
        )
        for candidate_id in (
            "iwbd-169-64-1523",
            "iwbd-169-64-1524",
            "iwbd-169-64-1527",
            "iwbd-169-64-1529",
            "iwbd-169-64-1530",
            "iwbd-169-64-1531",
        )
    },
}
WAVE6_IWBD_IDENTITY_BOUNDARY_HOLD_CONTRACTS = {
    candidate_id: WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS.pop(candidate_id)
    for candidate_id in WAVE6_IWBD_IDENTITY_BOUNDARY_HOLD_REASONS
}
WAVE6_IWBD_REVIEWED_IDENTITY_COHORTS = {
    cohort: tuple(
        candidate_id
        for candidate_id in candidate_ids
        if candidate_id in WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS
    )
    for cohort, candidate_ids in WAVE6_IWBD_REVIEWED_IDENTITY_COHORTS.items()
    if any(
        candidate_id in WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS
        for candidate_id in candidate_ids
    )
}

# Montenegro is already represented by this rated, time-valid Cliopatria
# identity. Reuse it instead of creating a parallel Kingdom-of-Montenegro line.
WAVE6_IWBD_REVIEWED_IDENTITY_BINDINGS["iwbd-100-36-422"]["attacker"] = (
    ("clio_q236_1853_31d59baa", "clio_q236_1853_31d59baa"),
    ("kingdom_serbia", "kingdom_serbia"),
)

WAVE6_EXPECTED_IMPLEMENTED_COUNTS = {"hced": 60, "iwd": 1, "iwbd": 9, "total": 70}
WAVE6_EXPECTED_HELD_COUNTS = {"hced": 42, "iwd": 14, "iwbd": 225}
