from __future__ import annotations

"""Exact hold and companion-exclusion contracts for Wave 6 lane C."""

from typing import Any

from .wave6_1800_2021_policy import (
    HCED_SOURCE_CONTRACT_FIELDS,
    IWD_SOURCE_CONTRACT_FIELDS,
    WAVE6_HCED_IDENTITY_BOUNDARY_HOLD_CONTRACTS,
    WAVE6_HCED_IDENTITY_BOUNDARY_HOLD_REASONS,
    WAVE6_IWBD_IDENTITY_BOUNDARY_HOLD_CONTRACTS,
    WAVE6_IWBD_IDENTITY_BOUNDARY_HOLD_REASONS,
    WAVE6_IWD_IDENTITY_BOUNDARY_HOLD_CONTRACTS,
    WAVE6_IWD_IDENTITY_BOUNDARY_HOLD_REASONS,
)
from .wave6_1800_2021_iwbd_holds_1 import WAVE6_IWBD_HELD_SHA256_PART_1
from .wave6_1800_2021_iwbd_holds_2 import WAVE6_IWBD_HELD_SHA256_PART_2
from .wave6_1800_2021_iwbd_holds_3 import WAVE6_IWBD_HELD_SHA256_PART_3
from .wave6_1800_2021_policy import IWBD_SOURCE_CONTRACT_FIELDS

WAVE6_HCED_AUDITED_HOLD_IDS = frozenset(
    {
        "hced-Ambur1749-1",
        "hced-Balangiga1900-1",
        "hced-Baler1896-1",
        "hced-Caloocan1899-1",
        "hced-Chi Hoa1860-1861-1",
        "hced-Chihuahua1913-1",
        "hced-Danang1858-1",
        "hced-Doiran1917-1",
        "hced-Doiran1918-1",
        "hced-Gia Cuc1883-1",
        "hced-Hung Hoa1884-1",
        "hced-Khartoum1884-1",
        "hced-Kresna1913-1",
        "hced-Monastir1916-1",
        "hced-Naic1897-1",
        "hced-Nam Dinh1883-1",
        "hced-Ojinaga1913-1",
        "hced-Palan1883-1",
        "hced-Palanan1901-1",
        "hced-Puray1897-1",
        "hced-Quinqua1899-1",
        "hced-San Isidro1896-1",
        "hced-San Mateo, Philippines1899-1",
        "hced-Silang1897-1",
        "hced-Sucat1899-1",
        "hced-Vardar1915-1",
        "hced-Vardar1918-1",
        "hced-Zapote Bridge1896-1",
    }
) | frozenset(WAVE6_HCED_IDENTITY_BOUNDARY_HOLD_REASONS)

WAVE6_HCED_COMPANION_EXCLUSION_IDS = frozenset(
    {
        "hced-Scutari1912-1913-1",
        "hced-Adrianople1912-1913-1",
        "hced-Rome1849-1",
        "hced-Palestrina1849-1",
        "hced-Velletri1849-1",
        "hced-Rafa1967-1",
        "hced-Abu Ageila1967-1",
        "hced-Gaza1967-1",
        "hced-Jebel Libni1967-1",
        "hced-Mitla Pass1967-1",
        "hced-Bir Gafgafa1967-1",
        "hced-Golan Heights1967-1",
        "hced-Fada1987-1",
        "hced-Ouadi Doum1987-1",
        "hced-Maaten-as-Sarra1987-1",
    }
)

_HCED_HOLD_SHA256 = {
    "hced-Abu Ageila1967-1": "f3e0c0a3eaedfbf75fba7e594fdff1f07eba16311fdbe7838da96a2f1de2c5f2",
    "hced-Adrianople1912-1913-1": "acaaf84af730d5d51136cf8be1da18527f4730f455a6e3f5ce5b01836df6b9ab",
    "hced-Ambur1749-1": "beead70a4195d45c3f87a728ffbfec5954f0d3da700aaa2815d747eef1e51ab7",
    "hced-Balangiga1900-1": "22b6af518297610948c2f94c8040fa30e0a49ace8cbfa3e4962b28466e7318cf",
    "hced-Baler1896-1": "4200a43eb743f10f67dda311f6c02d47f5a927ed24a2794d7c717fe3228d7126",
    "hced-Bir Gafgafa1967-1": "f1027eeb93c51faa97530cc7bd064f3fd988446481e620dfa81333e433d0e942",
    "hced-Caloocan1899-1": "07ef54893d8ef54b8bb8a0016dc28ece5d804027469624bf5c0b52076793b662",
    "hced-Chi Hoa1860-1861-1": "7f2078f9e138086c1dff2e7b0d3a403d9d79d239a8693c35e74682974e0dd39a",
    "hced-Chihuahua1913-1": "188dd28e00c95c644d8ddd5ae38139bf7f450ef3469fc89e9d2a76176d41e5e2",
    "hced-Danang1858-1": "8c3dcab0dcef25a19e8d8d54b69bb4205b02f92fa2f41a160d4a2f1839a64897",
    "hced-Doiran1917-1": "b9febeb407085222efc61f3a85c37eb81545da1ae4ab5e57cdc1b674202be23e",
    "hced-Doiran1918-1": "a6b953542eb35d1efe980cb31ab5c92d0f0f14494339c42b9e69fbad0e7007d6",
    "hced-Fada1987-1": "4d353fa49410050720fb7cfa8b7f4c83c173383d3db66f832e7725155c47ba8d",
    "hced-Gaza1967-1": "61126c7b672f15b2e6616607bf474aa805c3116e87f86c3fcdf66a1b13e2fc54",
    "hced-Gia Cuc1883-1": "863be44210a11acd9cab7468623c1766ff7131d8d8abfd2be0aa8ab76b150c62",
    "hced-Golan Heights1967-1": "b830b35c2ebdad3bba3b879ee0f37955c38cf4e894183786ad42dd1a67801b92",
    "hced-Hung Hoa1884-1": "68c9426d4dc6b6aae4a04768a768f73925deab6ec7e4a74c632d9768ccaf892d",
    "hced-Jebel Libni1967-1": "f9eee37165848053724562dea6a8ca93479fe26e435ba8bf005c0479feb3f5f9",
    "hced-Khartoum1884-1": "dba585a421d8c948799da52a4959f8e31353fbe548ac959e78beecacb679ea82",
    "hced-Kresna1913-1": "229d5aa5d09c6dfa480c9a12a5198e0d125555cafbbb3cfb576bbad285a5ccc9",
    "hced-Maaten-as-Sarra1987-1": "cd9640e78a36dd71a0f4d3ff4a937debc097ec35672e4ac79415006354d69150",
    "hced-Mitla Pass1967-1": "15bc5d69290bc5312717da84b2030d13820367d403abc335f7c157c53b81c691",
    "hced-Monastir1916-1": "c1514239f20da0655e63c62f5f16f8ef864b5b9465afb6d22dba44aa05ea5cd2",
    "hced-Naic1897-1": "a54d973c6f9af3d1c940f36bca217851d3292ca1196dd4374ab0552d51bf1332",
    "hced-Nam Dinh1883-1": "80e37dad52d37831680452422d7fe0ed0c07c6de2cdc2f90ad3c4920d2d027aa",
    "hced-Ojinaga1913-1": "a638141ff4ed037a43cb1f65bfc7d6608e53a6ca06631ed32d90abaf1c3b949d",
    "hced-Ouadi Doum1987-1": "2bddaa157c786d7d48f52738d159047cc8ee8abb28d6e5ff4fc7b6a08baf5a51",
    "hced-Palan1883-1": "25d2df78ae592e5015427945b250fdef63af47301b431dbe19ffbcb81c688a1b",
    "hced-Palanan1901-1": "e285a68a72848beaffe5c804c8622cfd5c1fa690a18c815b9d05f88f7b7116a4",
    "hced-Palestrina1849-1": "69030ff9538cee529fc06065d0d4fc0032446b6ded87beb95e30fe197a912343",
    "hced-Puray1897-1": "2450105c2d07d18c33ff9ad3aea84cebea76d8f473f0a9c4b49f21cc615cbfba",
    "hced-Quinqua1899-1": "c7f7e2ad365d56694625de8d7cd80a52840c2ced3761b6d97dfd32db88bafc76",
    "hced-Rafa1967-1": "432733cc3eef22bba907dd296c047ac36767f97827b2d7a5fd4064b950b14e96",
    "hced-Rome1849-1": "7d2792f7717691de3b4a7fdcc08c0e5442bd4af7f46c59694344ff2510db7e81",
    "hced-San Isidro1896-1": "9b8e25fe6dd99fe40491955692ec7f968a07ca272e74083d9ddbc38384c1db18",
    "hced-San Mateo, Philippines1899-1": "bd59c37b9d85ed2b78e42ea1c5b9e320a800ccef0c67fcfaf9467b2497e51851",
    "hced-Scutari1912-1913-1": "9b454628f242d83c36e7a4ace86ca2021c3393e18f9244c05306a6c96e60d787",
    "hced-Silang1897-1": "178e450794599ed9dc54d8d4e98ee728d8372ca74444e9d7a0e8418023436096",
    "hced-Sucat1899-1": "8c1c56804714b6f8b149c7ec5efc1010f1f916a37603ef5a81c69106c7c37d5d",
    "hced-Vardar1915-1": "be834fa65a96fd3460766dbcaa0ee2cfc03ac8d2111216f6a65b1ede576cf405",
    "hced-Vardar1918-1": "8595998ee65c0faa0759691b29cb7f585eccca50299af0b5f3c225757221f274",
    "hced-Velletri1849-1": "804da50b641b2de32ca83b07f68b086fa51f4583a7e682737d97ef918e588d2e",
    "hced-Zapote Bridge1896-1": "f967c1f746b017731524b05245cdc84162d27159d5f87be9f9eed934d85ed05c",
}

WAVE6_HCED_HELD_SOURCE_CONTRACTS: dict[str, dict[str, Any]] = {
    candidate_id: {"field_names": HCED_SOURCE_CONTRACT_FIELDS, "sha256": sha256}
    for candidate_id, sha256 in _HCED_HOLD_SHA256.items()
}
WAVE6_HCED_HELD_SOURCE_CONTRACTS.update(
    {
        candidate_id: contract["source_contract"]
        for candidate_id, contract in WAVE6_HCED_IDENTITY_BOUNDARY_HOLD_CONTRACTS.items()
    }
)

WAVE6_HCED_CURATED_EXCLUSIONS = {
    candidate_id: (
        "cross_source_duplicate: reviewed IWBD tactical row retained"
        if candidate_id in WAVE6_HCED_COMPANION_EXCLUSION_IDS
        else "Wave 6 evidence audit hold"
    )
    for candidate_id in _HCED_HOLD_SHA256
}
WAVE6_HCED_CURATED_EXCLUSIONS.update(
    {
        "hced-Baler1896-1": "wrong opponent: Spanish garrison fought Filipino revolutionary forces",
        "hced-Quinqua1899-1": "likely reversed outcome; no authoritative Philippine-victory contract",
        "hced-Khartoum1884-1": "wrong date envelope: siege terminated 26 January 1885",
    }
)
WAVE6_HCED_CURATED_EXCLUSIONS.update(WAVE6_HCED_IDENTITY_BOUNDARY_HOLD_REASONS)

_IWD_HELD_COMPONENT_SHA256 = {
    "4": {
        "iwd-4": "137d20e05bd87ead24fccfab23af5da885d64649ee4e6ec67611ad47e4f8de71",
        "iwd-5": "417686249973bec34ce0f198edf10a30ccf56658180773304e24e95a6748a500",
        "iwd-6": "94981a9362c56c9e3fc4a3bff95eef5188736520b1a6328e451398bdb3fc2132",
    },
    "6": {
        "iwd-10": "cfbf66d51d782c861b7b239bc311462bab97193f57382a335b6298cb3e492441",
        "iwd-8": "166d7c97e32ed8e139e290898fa7e14d359c40c0ae8c3d58bacad0acf90fb692",
        "iwd-9": "4140ac9c1cff015512ac71dccd7552a37c1640dc10ea229100cae031c26986e0",
    },
    "13": {
        "iwd-21": "85e6ed962bff639dca7d4dad2d39e84ef97bf81fd82256f8a7e95d6f889bbc9f",
    },
    "19": {
        "iwd-30": "b2433049d1e8ab288cb8421aa3f92bc2a6ddde6816261d591d060bf684f1633c",
        "iwd-31": "fb985112c662867a89a154cc8243bc3bb850b2e5dc1a12f66c1f31528cf4185c",
        "iwd-32": "b2beb90f77c6e6aa682e268267616c16edee3b03070c8fd2fc5adf34e2754b07",
        "iwd-33": "ccc62700d4a5ffbd76a6782922786f1c36c56e674ea65f52418c495197ec4614",
        "iwd-34": "ce16f8caba11ca65b4c06c2f82b18f21058e4c4581d454bf34582d5be8fd0b93",
        "iwd-35": "503dd795ce511ef880aad56c08f45621a32980d9ed847a24efd4509d390b5468",
        "iwd-36": "8a9fab1b91228e5bbf388c061fd069b1da99cd0700980f59ab3d8f0e802e213b",
        "iwd-37": "8edb29b056b48d0f63364e2b3c26a73d99c995bc568d11fbb6f98ff4da7d0442",
        "iwd-38": "4d9a9f8a9af83184e5d20cb027809a3c2c688f710cba212e492096da50d06f2b",
        "iwd-39": "21c85d4aa35148185202663251030876879ef89f788d23bb026e5a2ed04bcdeb",
    },
    "20": {
        "iwd-40": "d597ce03061a75eda1322c24e1626e3e7c70325857bcdc4095607cd29aee98b7",
        "iwd-41": "8a03c67bc61025b25ac42b3e18bb0b6778b8252f8593f082abd3e5e6573f6d26",
        "iwd-42": "91bd13d3616fd33aaf5fb226b614f9cd5a07d83d796ca1d9aa1ad3f4fcc7a437",
        "iwd-43": "820deb2955278252ac6bec7bbba2fa8b52bb9ed2bb7fb6282ea13f790782e90d",
    },
    "36": {
        "iwd-66": "70224db2dcc5e4345c0f940be2a6a9619879be43120a236548a71d71b53e74d7",
        "iwd-67": "aa8cade7cf8de5c53e9719aaab4bcfac32ebf57cd6338161981c86d57c96edff",
        "iwd-68": "2d1838dbea30f33e0e2af746615c1e9fa6ce2e5270ff68b8a3fc46bff92752dd",
    },
    "37": {
        "iwd-69": "3e0b4620c29971a06e11f4200d2ae61b8a17c99ef4cfe1f80a37b010faa261ac",
        "iwd-70": "76a65a44554626d8020af6821f66eb0b8b05a74b150667900608610fbcc6027c",
        "iwd-71": "8f697fc1dca3fd5ce5c7e0ca294f5378dd3b157fe697e74db83a72d0ce752b2e",
        "iwd-72": "1d5dbfc3a5e3b9acd88163a837d2742c0edea8492b76ccdd53782ec1f219f620",
    },
    "56": {
        "iwd-165": "290fa9ca75fda8aeb0acfb90158e207574756aa8d26a49b3ba24f0382dd26f1e",
        "iwd-166": "cf7f827eb733a4e46de862599b13d597c7bd5cb2dd94490922498c26049d97f5",
        "iwd-167": "209d802ca25390cbbec782d1d1fe68612ca4aa12b83b5486d35ce23032b5ee79",
        "iwd-168": "f5f4fed4fbaf2bc667010bf4c18922ff0d6673b97e8170526ae3104cfb6601af",
        "iwd-169": "ee94ac1e41a91de2ab689043d08ed3e22f0f84e09a9e7f7bc0519a43fdfb3f53",
        "iwd-170": "67c0c212f934d49225f69f2da2699773dca82b4f41e8dcca891ea3d4bb63de78",
        "iwd-171": "c5cdda3e5a25405520c99d74bf7ae0771e4dad4840908e15024c4ba57159302b",
        "iwd-172": "5d13f6faac282c5af87400dde5321b73d1638824848db18d18cb5c2d171ef527",
        "iwd-173": "ffc66c8168641815777532ec3f505d88740caec8dff0b84016c1c40124114155",
        "iwd-174": "6dc90b188f9b7370ce9974923e6e000a21ff688808cb349a4175fe11f7d2e029",
        "iwd-175": "e03dd4ef346b9d922f9c585070c2a4466398ff45fb3713abdb081907d0dcd7f3",
        "iwd-176": "dd14a1987adb93cc5a7e4983992eea05af90d92231881e3d124a39ef4167da64",
        "iwd-177": "5b50f11826541ceded2d05319ec3653442125397b0e415e6432cfb8198152b3d",
        "iwd-178": "ac4d90751f8cc69c783e4d9ca6bf8f157f78ea959e0325782d5c16605b4a0517",
        "iwd-179": "31cf51d0ffecc5369033a826b2afb418c99d9b0a9e96dae8da5d8666c3bff2f3",
        "iwd-180": "64639d0f37e650953aebc61fad713899e62450ef4a4d000695d78700f6fa9897",
        "iwd-266": "a1d014409a02380149b73158f9ecd81f3ccb6904778e747af4303eaafadbbd76",
    },
    "64": {
        "iwd-195": "abcb45fed416d3e99b76a520826d3d8a200ca61bbdc3727b2fb5d07a43b5683a",
        "iwd-196": "d6b4e3120e5b34ae25cf320e59513139d5ed756913fdd2d36c9c55cb11e86902",
        "iwd-197": "15dc7a4f235bbb334456e323dc2325dfd0f116610f0922e422e25057177b01bf",
    },
    "65": {
        "iwd-198": "ecafa4a45fb51dd51d347198966de70f2c93a3b241574906897c1354df39a3ce",
    },
    "66": {
        "iwd-199": "93b58fec62966cd4dd2e7ad0c9a473e2000fbac3689b0815fded408378bd4eca",
    },
    "72": {
        "iwd-209": "3ddf7f7e4e684e13499465d05047fdecbc0dacc11d2af1067c86852f1aee4dd6",
        "iwd-210": "a63761450e0ec5a49242b5663d39b84cbd86c832c92aaad48a341997767dbc36",
    },
    "80": {
        "iwd-220": "a76ff80d78e14c020ecd038590a38f7fb7cb735cef8a8f5008052443fa257542",
    },
    "85": {
        "iwd-241": "3ae491e4302ea6eaccedb4dfea01e3e5880b2204516c1b9c69f6fcfe288cfd33",
    },
}

WAVE6_IWD_HELD_PARENT_CONTRACTS = {
    parent_id: {
        "component_source_contracts": {
            candidate_id: {"field_names": IWD_SOURCE_CONTRACT_FIELDS, "sha256": sha256}
            for candidate_id, sha256 in components.items()
        }
    }
    for parent_id, components in _IWD_HELD_COMPONENT_SHA256.items()
}
WAVE6_IWD_HELD_PARENT_CONTRACTS.update(WAVE6_IWD_IDENTITY_BOUNDARY_HOLD_CONTRACTS)

WAVE6_IWD_CURATED_PARENT_EXCLUSIONS = {
    parent_id: reason
    for parent_id, reason in {
        "4": "coalition_incomplete: Papal and revolutionary contingents are absent and COW Italy is not an exact Sardinian identity",
        "6": "coalition_incomplete: Spain is absent and the target must be the short-lived Roman Republic, not Papal States",
        "13": "actor_transition: Garibaldi's volunteer army and later Sardinian regular forces cannot be one Italy identity",
        "19": "coalition incomplete (independent German belligerents omitted)",
        "20": "regime_and_coalition_transition: France changes regime in September 1870 and Prussia is not the entire German coalition",
        "36": "coalition_incomplete: Montenegro is absent from the First Balkan War parent components",
        "37": "coalition incomplete (Montenegro omitted)",
        "56": "party_semantics_wrong: UN and Chinese forces are repeatedly substituted by South and North Korea; Soviet component is not a combatant contract",
        "64": "coalition incomplete (Iraq omitted)",
        "65": "outcome_and_actor_ambiguous: the Second Laotian umbrella cannot be reduced to Vietnam versus Laos with a draw",
        "66": "FRUS supports a standstill cease-fire, not Israeli strategic victory",
        "72": "domestic_principals_omitted: FNLA/UNITA and MPLA are essential parties to the internationalized Angolan conflict",
        "80": "coalition incomplete (direct French combat intervention omitted)",
        "85": "coalition_incomplete_and_envelope: USA cannot stand for NATO and the single IWBD row duplicates the whole campaign",
    }.items()
}
WAVE6_IWD_CURATED_PARENT_EXCLUSIONS.update(WAVE6_IWD_IDENTITY_BOUNDARY_HOLD_REASONS)

_IWBD_HELD_SHA256 = {
    **WAVE6_IWBD_HELD_SHA256_PART_1,
    **WAVE6_IWBD_HELD_SHA256_PART_2,
    **WAVE6_IWBD_HELD_SHA256_PART_3,
}
WAVE6_IWBD_HELD_SOURCE_CONTRACTS: dict[str, dict[str, Any]] = {
    candidate_id: {"field_names": IWBD_SOURCE_CONTRACT_FIELDS, "sha256": sha256}
    for candidate_id, sha256 in _IWBD_HELD_SHA256.items()
}
WAVE6_IWBD_HELD_SOURCE_CONTRACTS.update(
    {
        candidate_id: contract["source_contract"]
        for candidate_id, contract in WAVE6_IWBD_IDENTITY_BOUNDARY_HOLD_CONTRACTS.items()
    }
)

# These rows were already published at the audited Wave 5 checkpoint.  They
# remain fingerprinted audit concerns, but Wave 6 may not turn that broad audit
# into retroactive exclusions without an event-by-event correction decision.
WAVE6_IWBD_BASELINE_PUBLISHED_HOLD_IDS = frozenset(
    {
        "iwbd-58-20-257",
        "iwbd-151-56-1406",
        "iwbd-151-56-1418",
        "iwbd-151-56-1426",
        "iwbd-151-56-1431",
        "iwbd-151-56-1434",
        "iwbd-151-56-1435",
        "iwbd-151-56-1436",
        "iwbd-151-56-1441",
        "iwbd-151-56-1442",
        "iwbd-186-72-1580",
        "iwbd-186-72-1581",
        "iwbd-186-72-1583",
        "iwbd-186-72-1585",
        "iwbd-186-72-1587",
        "iwbd-186-72-1588",
        "iwbd-186-72-1589",
        "iwbd-186-72-1590",
        "iwbd-186-72-1591",
        "iwbd-186-72-1592",
        "iwbd-186-72-1593",
        "iwbd-186-72-1594",
    }
)
WAVE6_IWBD_BASELINE_PRESERVATION_REASONS = {
    candidate_id: (
        "Phase 1 flagged generic Korean-side substitution (UN/Chinese forces "
        "collapsed to South/North Korea), but the row was already published in Wave 5"
    )
    for candidate_id in WAVE6_IWBD_BASELINE_PUBLISHED_HOLD_IDS
    if candidate_id.startswith("iwbd-151-56-")
}
WAVE6_IWBD_BASELINE_PRESERVATION_REASONS.update(
    {
        candidate_id: (
            "Phase 1 flagged omitted Angolan domestic principals (MPLA/FNLA/UNITA), "
            "but the row was already published in Wave 5"
        )
        for candidate_id in WAVE6_IWBD_BASELINE_PUBLISHED_HOLD_IDS
        if candidate_id.startswith("iwbd-186-72-")
    }
)
WAVE6_IWBD_BASELINE_PRESERVATION_REASONS["iwbd-58-20-257"] = (
    "Phase 1 flagged an unaudited French/German regime-and-coalition transition, "
    "but Orleans was already published in Wave 5"
)
WAVE6_IWBD_CURATED_EXCLUSIONS = {
    candidate_id: "Wave 6 evidence audit hold"
    for candidate_id in _IWBD_HELD_SHA256
    if candidate_id not in WAVE6_IWBD_BASELINE_PUBLISHED_HOLD_IDS
}
WAVE6_IWBD_CURATED_EXCLUSIONS["iwbd-100-36-421"] = (
    "cross_source_duplicate: Wave 5 already rates Sarandaporon from HCED"
)
WAVE6_IWBD_CURATED_EXCLUSIONS.update(WAVE6_IWBD_IDENTITY_BOUNDARY_HOLD_REASONS)

WAVE6_CROSS_LANE_B_OMISSIONS = (
    "hced-Palkhed1728-1",
    "hced-Trichinopoly1743-1",
    "hced-Sindkhed1757-1",
    "hced-Udgir1760-1",
    "hced-Rakshasbhuvan1763-1",
    "hced-Koppal1790-1791-1",
)
