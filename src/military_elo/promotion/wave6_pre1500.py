from __future__ import annotations

"""Fail-closed Wave 6 policy for audited HCED events through 1499.

The lane is deliberately self-contained.  Every safe row and every hold is
candidate-ID keyed and pinned to a semantic fingerprint from the content-locked
HCED review queue.  Generic label policies can resolve only within the declared
historical windows, while the promotion-level inventory guard prevents those
policies from admitting any row outside the audited candidate manifest.
"""

import hashlib
import json
import re
import unicodedata
from typing import Any


WAVE6_PRE1500_LABEL_POLICIES: dict[
    str, tuple[tuple[int, int, str], ...]
] = {
    "syracuse": ((-480, -213, "syracuse_city_state"),),
    "pontus": ((-281, -63, "mithridatid_kingdom_pontus"),),
    # The entity continues to 1797, but this lane's generic policy stops at
    # 1499 so the 1684 source row remains available to the 1500-1799 lane.
    "genoa": ((1099, 1499, "republic_genoa"),),
    "milan": ((1395, 1447, "duchy_milan_visconti"),),
    "castile": (
        (1065, 1229, "kingdom_castile_1065"),
        (1230, 1478, "crown_castile_1230"),
    ),
    "castille": (
        (1065, 1229, "kingdom_castile_1065"),
        (1230, 1478, "crown_castile_1230"),
    ),
    "aragon": ((1164, 1478, "crown_aragon_1164"),),
    "bulgaria": (
        (681, 1018, "clio_bg_bulgaria_early_682_95daf02a"),
        (1185, 1396, "second_bulgarian_empire"),
    ),
    "denmark": ((936, 1396, "kingdom_denmark_medieval"),),
    "seljuk turks": ((1040, 1092, "clio_ir_seljuk_sultanate_1040_577da931"),),
    "yorkists": (
        (1455, 1471, "yorkist_faction_1455"),
        (1487, 1487, "simnel_yorkist_rebellion_1487"),
    ),
    "lancastrians": ((1455, 1471, "lancastrian_faction_1455"),),
    "edward iv": ((1471, 1471, "yorkist_faction_1455"),),
    "earl of warwick": ((1471, 1471, "warwick_readeption_army_1471"),),
}


def _normalize_label(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(
        character for character in text if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def wave6_pre1500_label_policy_entity_id(
    label: Any,
    low_year: int,
    high_year: int,
) -> str | None:
    """Resolve only the lane's exact bounded label windows."""

    matches = {
        entity_id
        for start_year, end_year, entity_id in WAVE6_PRE1500_LABEL_POLICIES.get(
            _normalize_label(label), ()
        )
        if low_year >= start_year and high_year <= end_year
    }
    return next(iter(matches)) if len(matches) == 1 else None


WAVE6_PRE1500_HOLD_REASONS: dict[str, str] = {
    "hced-Sebastia1070-1": (
        "wrong state attribution: the victorious Turkoman commander Chrysoskoulos/"
        "Arisighi was a rebel or fugitive whom Sultan Alp Arslan sent Afshin to hunt, "
        "not an army of the Great Seljuk central state"
    ),
    "hced-Selinus-409-1": (
        "wrong-actor substitution: Selinus fell before Syracusan relief arrived; "
        "Syracuse was not the defeated polity"
    ),
    "hced-Himera-409-1": (
        "principal-actor omission: Himera was the defeated polity, while much "
        "of the Syracusan and Agrigentine aid withdrew before the city's fall"
    ),
    "hced-Syracuse-213-1": (
        "date-envelope error: the terminal siege and fall spans 213-212 BCE "
        "in the cited chronology, not a defensible 213 BCE point event"
    ),
    "hced-Tenedos-85-1": (
        "chronology unresolved: reputable accounts differ between 86 and 85 BCE, "
        "and the reviewed primary texts do not pin the selected year"
    ),
    "hced-Motya-397-1": (
        "outcome reversed: Diodorus reports Dionysius and Syracuse captured Motya"
    ),
    "hced-Zela-47-1": (
        "identity discontinuity: Pharnaces II attacked from the Bosporan kingdom "
        "after Pompey's 63 BCE destruction of the Mithridatid kingdom"
    ),
    "hced-Chioggia1379-1": (
        "compressed 1379-1380 siege with changing control and a Genoese-Paduan-"
        "Hungarian coalition"
    ),
    "hced-Kaffa1475-1": (
        "wrong governing actor: Caffa had been administered by the Bank of Saint "
        "George since 1453"
    ),
    "hced-Genoa1684-1": "outside this lane's 1499 cutoff; reserved for later review",
    "hced-Gottolengo1427-1": (
        "outcome conflict: HCED says draw while historical accounts describe a "
        "Visconti success or successful check"
    ),
    "hced-Caravaggio1448-1": (
        "Golden Ambrosian Republic actor after the Visconti duchy ended in 1447"
    ),
    "hced-Milan1449-1": (
        "Francesco Sforza versus the Golden Ambrosian Republic, not Visconti Milan"
    ),
    "hced-Tamaron1037-1": (
        "Ferdinand was Count of Castile; the Kingdom of Castile begins in 1065"
    ),
    "hced-Aljubarrota1385-1": (
        "winning-side crosswalk retains England but omits the principal Portuguese actor"
    ),
    "hced-Spercheios996-1": (
        "unresolved chronology: strong scholarship divides between 996 and 997"
    ),
    "hced-Nairn1009-1": (
        "late or legendary tradition with unstable date and participants"
    ),
    "hced-Mortlack1010-1": (
        "late or legendary tradition with unstable chronology and participants"
    ),
    "hced-Nesjar1016-1": (
        "wrong actors: Olav Haraldsson fought Sveinn Hakonarson and allied Norwegian magnates"
    ),
    "hced-Aasle1389-1": "duplicate of the same Asle/Falkoping action",
    "hced-Falkoping1389-1": "duplicate of the same Asle/Falkoping action",
    "hced-Tarq1002-1": (
        "Ghazni versus Buyid/Persian context decades before the Great Seljuk state"
    ),
    "hced-Myriocephalum1176-1": (
        "the Turkish actor was the Sultanate of Rum, not the Great Seljuk Empire"
    ),
    "hced-Ferrybridge1461-1": (
        "changing bridge action immediately before Towton, not a clean standalone victory"
    ),
    "hced-Dunstable1461-1": (
        "Warwick outpost action immediately before Second St Albans; component inflation"
    ),
    "hced-Twt Hill1463-1": "date error: the action occurred on 16 October 1461",
    "hced-Bamburgh1464-1": (
        "outcome reversed: Bamburgh fell to Yorkist royal forces"
    ),
    "hced-Caister Castle1469-1": (
        "Norfolk versus Paston retainers, not Yorkists versus Lancastrians"
    ),
    "hced-Lose-Coat Field1470-1": (
        "Welles's rebels and the Warwick-Clarence alignment are not a clean Lancastrian side"
    ),
    "hced-Bosworth Field1485-1": (
        "Henry Tudor's composite army cannot reopen the Lancastrian faction after 1471"
    ),
}


# All historical/semantic holds are enumerated in the first-pass exclusion
# table.  Genoa 1684 is the sole scope-only hold; it stays staged through the
# lane cutoff in the Genoa label policy so another lane is not pre-empted.
WAVE6_PRE1500_CURATED_EXCLUSIONS: dict[str, str] = {
    candidate_id: reason
    for candidate_id, reason in WAVE6_PRE1500_HOLD_REASONS.items()
    if candidate_id != "hced-Genoa1684-1"
}


WAVE6_PRE1500_SAFE_CANDIDATE_IDS: tuple[str, ...] = (
    "hced-Acragas-406-1",
    "hced-Alarcos1195-1",
    "hced-Antium1378-1",
    "hced-Arcadiopolis1194-1",
    "hced-Barnet1471-1",
    "hced-Blore Heath1459-1",
    "hced-Cabala-383-1",
    "hced-Cabira-72-1",
    "hced-Carthage, Tunisia-310-1",
    "hced-Chaeronea-86-1",
    "hced-Chalcedon-74-1",
    "hced-Cremona1431-1",
    "hced-Cronium-383-1",
    "hced-Curzola1298-1",
    "hced-Cyzicus-73-1",
    "hced-Dandanaqan1040-1",
    "hced-Gerona1285-1",
    "hced-Halys-82-1",
    "hced-Hedgeley Moor1464-1",
    "hced-Hexham1464-1",
    "hced-Himera-480-1",
    "hced-Kaffa1296-1",
    "hced-Laiazzo1294-1",
    "hced-Lantada1068-1",
    "hced-Las Hormigas1285-1",
    "hced-Lemnos-73-1",
    "hced-Lilybaeum-368-1",
    "hced-Ludford Bridge1459-1",
    "hced-Lycus-66-1",
    "hced-Maclodio1427-1",
    "hced-Maderno1439-1",
    "hced-Manzikert1054-1",
    "hced-Manzikert1071-1",
    "hced-Miletopolis-85-1",
    "hced-Mortimers Cross1461-1",
    "hced-Northampton1460-1",
    "hced-Orchomenus-86-1",
    "hced-Pula1379-1",
    "hced-Sandwich1460-1",
    "hced-Sapienza1354-1",
    "hced-Saseno1264-1",
    "hced-St Albans1455-1",
    "hced-St Albans1461-1",
    "hced-Stoke1487-1",
    "hced-Stralsund1184-1",
    "hced-Syracuse-311-1",
    "hced-Syracuse-396-1",
    "hced-Syracuse-415-1",
    "hced-Tewkesbury1471-1",
    "hced-Towton1461-1",
    "hced-Trajans Gate986-1",
    "hced-Trapani1266-1",
    "hced-Wakefield1460-1",
    "hced-Winchelsea1350-1",
    "hced-Zela-67-1",
)


WAVE6_PRE1500_FINGERPRINT_SHA256: dict[str, str] = {
    "hced-Aasle1389-1": "a14581eb6d2f119ef471d874bf6ab8dabf85afff949312b9e83fd10483a5f589",
    "hced-Acragas-406-1": "52590ac81ab4c4efd1eb0b19a633284de7eeb23af1d1583d2fd90bf2bd579055",
    "hced-Alarcos1195-1": "c24e5fed710ee22c875cb3e83627f850a76bb566eabbd8057a5b5ecf3ec4bb1b",
    "hced-Aljubarrota1385-1": "236850c72765270721a827fa965684444085bb1649ba32a29671b06da75b2835",
    "hced-Antium1378-1": "592eeffa2f9569d057eeb34ac16e2744e39ce20040dcf2413d8bd36bfcdf336b",
    "hced-Arcadiopolis1194-1": "cc6c73959891fd7a2af6caa3d3609eed9162afb9bed955c0f51745d7fd6bbd17",
    "hced-Bamburgh1464-1": "d6a812c3dfbc2c9aed45699320f8110bc5259806b29ed51deda03b16b8d0ec9f",
    "hced-Barnet1471-1": "31cc2f41d717ddec80d3861867b5dc469dd18cadc4d1a14b9a57233c0a918c4c",
    "hced-Blore Heath1459-1": "8fcecc7768ee9d8fcf3b06474d250a46b87e83c1f2db52e0fd9a03e6fa2afae9",
    "hced-Bosworth Field1485-1": "f185d12afa0d53db813d1db4486430cbe0f36aad484bd615656dafaf892e2f9d",
    "hced-Cabala-383-1": "b44bfe529fcaba339f63423caa71148df9828eed369024b735f52ad43fc780d5",
    "hced-Cabira-72-1": "d8b29c2afeafad6e1c4789dafcdd19b849af7db26603ef876ea5c0ab03b8f887",
    "hced-Caister Castle1469-1": "0435b069b1ade565804fd931a1084bdd2e07196e8c88bd71465ad7a64733f194",
    "hced-Caravaggio1448-1": "a37870de54ee7a0141ff002e8154ee637d08191f1df99b3b8bfe7fbaaff1ee58",
    "hced-Carthage, Tunisia-310-1": "ede2204b36d598660c15c666e70106d328d0ef45ba4b8062473e37d630d2bdfc",
    "hced-Chaeronea-86-1": "0b37fc6e86dc127433506ba61604604013fffce462ebb6fc02381faa3e139619",
    "hced-Chalcedon-74-1": "7fe80837df7b920b84429fc60b27d097967b2532891c48cb955af40af39dd3c9",
    "hced-Chioggia1379-1": "dfdb0e69262290d9ef4b69badbd40855815bb29ee29621c1753d2d92880efc4f",
    "hced-Cremona1431-1": "7ce082835b6ec4571b98228c8240f33bb8c63dd1090c9557bd2c4fc0f011acc9",
    "hced-Cronium-383-1": "4418ee7fe3cdbc1a38ece741d9b4da9fd7722decaf18f7b48889857e3678c7ba",
    "hced-Curzola1298-1": "ea4e579d9c2f8fba74b8a93000c9ffc161aef2d388d0be5c1844b371fdc0f1bd",
    "hced-Cyzicus-73-1": "1fef4bcc5be965c804839a6403591559ff6541d2d7d6c424c035a4a94bfbaefc",
    "hced-Dandanaqan1040-1": "9ecb771f47854d40cb577e8e8cc17c155cf79c3d5bee08a305b072a1b97db49a",
    "hced-Dunstable1461-1": "ebd177a6c6292bd48118df01f42f81f5fafeda3a046cddb98825101c80c73c20",
    "hced-Falkoping1389-1": "74148e3e55a6448fa6e64a544bfb858917fe04c20691342ff1eae85ff942df39",
    "hced-Ferrybridge1461-1": "126315b90041b4a6977621bfe08e309f9721606f81b47aed57c83e2a07f8d6d6",
    "hced-Genoa1684-1": "e6bb4600d9970e8b62aa41eb2d90c59905b186c67b48aae389eba6acbf074ea0",
    "hced-Gerona1285-1": "8e570314693d652a80c5776e2e81b6c6108762d538e08631fe7843cffca866c6",
    "hced-Gottolengo1427-1": "09f782a0adac6684258faa15554bb9674e924a6e2f053b39190ed8eb0bc68707",
    "hced-Halys-82-1": "47f967df505de3cf977e08355ee71d5decb3362b72fea35354aaed5333590685",
    "hced-Hedgeley Moor1464-1": "f4a378cdf3a0514e6243f912a19d7eeab0f6619337a67ef6377562ab146c395c",
    "hced-Hexham1464-1": "7d6afc6fa0194dc0b623435be724c5ff63cf63f57618c2e479bbacd04e6a2dc8",
    "hced-Himera-409-1": "8ecee94505c13498b659cb409823cc763a999e696111bce411dab996a2d67c5c",
    "hced-Himera-480-1": "d7d10d0d96f984258710d5d0919b46e3bb9d9da29512fa18538a890f7b7e2c2d",
    "hced-Kaffa1296-1": "0ae889be17dd16bbfefcc16ee4d77ab11ffa2c96d46bfcb96075f6f583c376f4",
    "hced-Kaffa1475-1": "5c2f1c521e5e331a4188fe6d85719c1e4d8d3e1d4e068aa568901eceb46cafe4",
    "hced-Laiazzo1294-1": "457229c1a49ccf9ea6b44296183b4e90e3ea11f290b3f1c1f86fcf05818437d3",
    "hced-Lantada1068-1": "2e83875e56a1a9ba212c3b0244b7aa3d2149a3e9d129a3386de8fc0fc56414e3",
    "hced-Las Hormigas1285-1": "ba2d42885c051b0ba6ed4af8a5104eec538fb39d040c3d23580694c2e8a1a60d",
    "hced-Lemnos-73-1": "8fe0be183956dda8919db36703dd527f3f2306ca3ac87031e76fb2c408872be3",
    "hced-Lilybaeum-368-1": "fa24f16269c795569eb5f771c10266c0968b9933f5bb56accebd17482b2a1405",
    "hced-Lose-Coat Field1470-1": "8e892b57389de8348f5968bacc803ee032b99769119df087610e2244211ee750",
    "hced-Ludford Bridge1459-1": "19e759277bae6120136456d0e87c5aca65eb4d30ae98e6fca6dc0fed77a6bf72",
    "hced-Lycus-66-1": "62a8c6452f5d7906cfe0b8f2aa3cb0174d354bc9b207314350ec6087d33297d6",
    "hced-Maclodio1427-1": "fe92051baf3bc63444cd0bb99ebfe309a95ca9b52d7ba497f8a49a8fada09758",
    "hced-Maderno1439-1": "b34e22352ab10c9067531bed128e8199a2eac44578d219f74be77a1f10d072f8",
    "hced-Manzikert1054-1": "478199ef36e1995c9805c6474ec56616be1f20af8bfd10afac0950ed38fb5b69",
    "hced-Manzikert1071-1": "f55bddd04229024a2fe72e4fdd58f4cfcdd157bd9927f1276828d4053937c24b",
    "hced-Milan1449-1": "8d5dc5a0674a09b42d9b9908033bf6de2a00d933618a006e4f22ccf753151501",
    "hced-Miletopolis-85-1": "89dbdb12ab59c504f7fd33243cf576986a92fc950e7e83bc112976003b1112d8",
    "hced-Mortimers Cross1461-1": "f29eab994d87fb5ebfa3979a41bea1d4018786ffc5a5a2b08af6821bf06c4f68",
    "hced-Mortlack1010-1": "ae5dd0e6e0f7af323c258d1e6a751a74cf83846664d499782dd9498a4d0f13cf",
    "hced-Motya-397-1": "8871e354c825e64e862aaa65c548aa41d8abd9220f50f0b94c04d6cd5b445a87",
    "hced-Myriocephalum1176-1": "ff21296e93ee1d5823addc7cc18adaea0e604aac5815a65c8d968a779246e0ab",
    "hced-Nairn1009-1": "de25f0b7bdf3e144c7b782a83c9b9c8c6bfee7db639e3a07dc548d37478d8cce",
    "hced-Nesjar1016-1": "623cecd6571dd3ee3c35e014dbbfa739d5cd714f2621c8eab64d9b28d1f6765f",
    "hced-Northampton1460-1": "afdb94cd18aa74d098de9c9f754fe4daa20f9993261e81250fd40debb6d662cd",
    "hced-Orchomenus-86-1": "e3f2a6e1b83384b22c64ea68b84dc764872f1484274a4ced36887556ff1a09c6",
    "hced-Pula1379-1": "88c697ef141b1c3c750aaa8a64e2d094b72b291cb65ff7d6c8317671556f0528",
    "hced-Sandwich1460-1": "acafac1253e84a07c60f126b905fc875b451b50329b055932d5b7375eef5ef75",
    "hced-Sapienza1354-1": "f79986ace4fcce12e65a75c1d5544ceacddb1ceb12f2ae9985c7f404cce85efb",
    "hced-Saseno1264-1": "c29012e2feac84782b8c23c3b6ff2f79447bb5f293d8bc411316987d832f68a8",
    "hced-Sebastia1070-1": "4ce727229b600e7c7ad69ccd5f9dbecea16792a5993ceb4649f815f03a38a16f",
    "hced-Selinus-409-1": "971bb960af328310bf7201aee79b92d4f0c4f6b0d3e3c47e3b8804467391af2e",
    "hced-Spercheios996-1": "3cfc4f10bf1b2debeec1a5a2397f152cb68b0091f19bc1ead54818eaa8c31856",
    "hced-St Albans1455-1": "11d988f7d514304910098bfc95e48f976f6ff42d7f9b2deab2b6be52be594afe",
    "hced-St Albans1461-1": "a89ff10cb0c41d20d0ac8abcb9004a7fd1aa9e3f0393928246c278369d097e94",
    "hced-Stoke1487-1": "10d00b028aab7b1f340bb55a9ab2bdcf553ad138b811cc03970ce7926c537578",
    "hced-Stralsund1184-1": "5b00376fc2bd9eed005648aa12fad03f7a3425027f9ea2b392a91f273476fe0c",
    "hced-Syracuse-213-1": "dee680fb764f169f19c1da5b7f4d1e536c4a4b3045919e53cadb0424e52e01ad",
    "hced-Syracuse-311-1": "824c1db3c9dce47f8e62df724e94b7a3929ad79c2806193f33c6501962ff947f",
    "hced-Syracuse-396-1": "9a5f86060453e041a1a16dabcd5286557de5f78de4ed554a0ad6e604e3f0f966",
    "hced-Syracuse-415-1": "efe681eed7d19f594823721e2675b3ae7759c7e6914c55bff582d42e3b382ded",
    "hced-Tamaron1037-1": "5582c9e8699948c42fdee4e96506d61c45fbceadd4b85f4d549c16ad0643bc54",
    "hced-Tarq1002-1": "44fe1e880851c3aac6bc11f49c876b111ceac50536fc32bb069496d8d2a0774c",
    "hced-Tenedos-85-1": "0d2add6641327da8ab187c05c0cf3db8572eb71c223f7fb90f6dd2afc8c2689d",
    "hced-Tewkesbury1471-1": "1f66abb98d15005b555bc94818f99d349cbd04c0548af1a291aa639c0c2af8e3",
    "hced-Towton1461-1": "405cef3d416a3d8b8e24e24efdc6fd2e675c94581c012be3a1d7fdea53d5eb6e",
    "hced-Trajans Gate986-1": "573e353f4564201a7a8bf17a5e5b9b0d4c3b915c3b6eeea20203c3826ce24a14",
    "hced-Trapani1266-1": "83ae9bc1649134505abe44e4c1e7c8ebecb6c6492b099ab2e9cbeab33a06addc",
    "hced-Twt Hill1463-1": "335d57890a3e5079a73a1c08ccd84faa7b1c45833a92c02b66bb76ba65a399d8",
    "hced-Wakefield1460-1": "965dc7057405d02055291a4125123b243559713f87ade29a9b394316a87dbc17",
    "hced-Winchelsea1350-1": "2fdfc1f62f96e272c7b075c73ac64fc6968e32033369f47ab03c7fdada4c0a31",
    "hced-Zela-47-1": "db8d8c314dde3326911c627a9f986a556f71d0e03a5ca353ad27d6333bfe74e9",
    "hced-Zela-67-1": "592c4f9cdd3ec0b6ac0831dbff13c7879b718addb271bf2f118522a03eb4a201",
}


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    identity: bool = False,
) -> dict[str, Any]:
    roles = ["curated_reference_pending_claim_level_outcome_locator"]
    if identity:
        roles.append("identity_boundary_or_context_reference")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-15",
        "source_family_id": source_family_id,
        "evidence_roles": roles,
    }


WAVE6_PRE1500_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave6_diodorus_sicily",
        "Diodorus Siculus, Library of History, Books 11 and 13-20",
        "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Diodorus_Siculus/home.html",
        "University of Chicago LacusCurtius",
        "primary_source_translation",
        "diodorus_siculus_library",
        identity=True,
    ),
    _source(
        "wave6_thucydides_sicily",
        "Thucydides, History of the Peloponnesian War, Books 6-7",
        "https://classics.mit.edu/Thucydides/pelopwar.html",
        "MIT Classics Archive",
        "primary_source_translation",
        "thucydides_peloponnesian_war",
        identity=True,
    ),
    _source(
        "wave6_livy_syracuse",
        "Livy, History of Rome, Books 24-25",
        "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.02.0159",
        "Perseus Digital Library, Tufts University",
        "primary_source_translation",
        "livy_history_rome",
        identity=True,
    ),
    _source(
        "wave6_appian_mithridatic",
        "Appian, The Mithridatic Wars",
        "https://www.livius.org/sources/content/appian/appian-the-mithridatic-wars/",
        "Livius.org primary-source edition",
        "primary_source_translation",
        "appian_mithridatic_wars",
    ),
    _source(
        "wave6_plutarch_lives",
        "Plutarch, Lives of Sulla, Lucullus, and Pompey",
        "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/home.html",
        "University of Chicago LacusCurtius",
        "primary_source_translation",
        "plutarch_parallel_lives",
    ),
    _source(
        "wave6_iranica_pontus",
        "Brian McGing, Pontus",
        "https://www.iranicaonline.org/articles/pontus/",
        "Encyclopaedia Iranica",
        "academic_reference",
        "encyclopaedia_iranica_editorial_corpus",
        identity=True,
    ),
    _source(
        "wave6_treccani_genoa",
        "Genova",
        "https://www.treccani.it/enciclopedia/genova_%28Enciclopedia-Italiana%29/",
        "Istituto della Enciclopedia Italiana",
        "academic_reference",
        "treccani_editorial_corpus",
        identity=True,
    ),
    _source(
        "wave6_dotson_medieval_seas",
        "John E. Dotson, Venice, Genoa and Control of the Seas in the Thirteenth and Fourteenth Centuries",
        "https://boydellandbrewer.com/9781843830726/war-at-sea-in-the-middle-ages-and-the-renaissance/",
        "Boydell & Brewer",
        "academic_reference",
        "dotson_medieval_seas",
    ),
    _source(
        "wave6_black_milan",
        "Jane Black, Absolutism in Renaissance Milan",
        "https://academic.oup.com/book/4274",
        "Oxford University Press",
        "academic_reference",
        "black_renaissance_milan",
        identity=True,
    ),
    _source(
        "wave6_treccani_ambrosian",
        "Repubblica Ambrosiana",
        "https://www.treccani.it/enciclopedia/repubblica-ambrosiana/",
        "Istituto della Enciclopedia Italiana",
        "academic_reference",
        "treccani_editorial_corpus",
        identity=True,
    ),
    _source(
        "wave6_treccani_maclodio",
        "Maclodio and the battle of 11 October 1427",
        "https://www.treccani.it/enciclopedia/maclodio_%28Enciclopedia-Italiana%29/",
        "Istituto della Enciclopedia Italiana",
        "academic_reference",
        "treccani_editorial_corpus",
    ),
    _source(
        "wave6_treccani_terraferma",
        "La conquista della terraferma",
        "https://www.treccani.it/enciclopedia/la-conquista-della-terraferma_%28Storia-di-Venezia%29/",
        "Istituto della Enciclopedia Italiana",
        "academic_reference",
        "treccani_editorial_corpus",
    ),
    _source(
        "wave6_moro_venice_rivers",
        "Federico Moro, Venice Rules the Rivers",
        "https://www.nam-sism.org/Articoli/articoli%20approvati%20NAM/NAM%20Articoli%20approvati/b%29%20Storia%20militare%20moderna/NAM%20n.%207.%201.%20MORO%20Venice%20Rules%20the%20Rivers.pdf",
        "Nuova Antologia Militare",
        "academic_article",
        "moro_venice_rivers",
    ),
    _source(
        "wave6_reilly_castile",
        "Bernard F. Reilly, The Kingdom of Leon-Castilla under King Alfonso VI, 1065-1109",
        "https://libro.uca.edu/alfonso6/alfonso.htm",
        "Library of Iberian Resources Online",
        "academic_monograph",
        "reilly_leon_castile",
        identity=True,
    ),
    _source(
        "wave6_ocallaghan_iberia",
        "Joseph F. O'Callaghan, Reconquest and Crusade in Medieval Spain",
        "https://www.pennpress.org/9780812218898/reconquest-and-crusade-in-medieval-spain/",
        "University of Pennsylvania Press",
        "academic_monograph",
        "ocallaghan_reconquest_crusade",
        identity=True,
    ),
    _source(
        "wave6_castilla_alarcos",
        "Castillo de Alarcos and the battle of 1195",
        "https://www.turismocastillalamancha.es/es/cultura-y-patrimonio/castillos/ciudad-real/castillo-de-alarcos",
        "Junta de Comunidades de Castilla-La Mancha",
        "official_history",
        "castilla_la_mancha_alarcos",
    ),
    _source(
        "wave6_cushway_winchelsea",
        "Graham Cushway, The Battle of Winchelsea (1350)",
        "https://www.cambridge.org/core/books/abs/edward-iii-and-the-war-at-sea/battle-of-winchelsea-1350/59AB97A8DF09285D60BCCD3F8DFD9D4C",
        "Cambridge University Press",
        "academic_monograph_chapter",
        "cushway_edward_iii_sea",
    ),
    _source(
        "wave6_stephenson_balkans",
        "Paul Stephenson, Byzantium's Balkan Frontier, 900-1204",
        "https://doi.org/10.1017/CBO9780511496615",
        "Cambridge University Press",
        "academic_monograph",
        "stephenson_balkan_frontier",
        identity=True,
    ),
    _source(
        "wave6_curta_southeastern",
        "Florin Curta, Southeastern Europe in the Middle Ages, 500-1250",
        "https://www.cambridge.org/core/books/southeastern-europe-in-the-middle-ages-5001250/7D99C2C9FC2A9DFE404BDB3AE6182E1A",
        "Cambridge University Press",
        "academic_monograph",
        "curta_southeastern_europe",
        identity=True,
    ),
    _source(
        "wave6_saxo_denmark",
        "Saxo Grammaticus, Gesta Danorum, Book 16",
        "https://global.oup.com/academic/product/saxo-grammaticus-gesta-danorum-9780198205234",
        "Oxford University Press",
        "primary_source_critical_edition",
        "saxo_gesta_danorum",
        identity=True,
    ),
    _source(
        "wave6_iranica_dandanqan",
        "C. E. Bosworth, Dandanqan",
        "https://www.iranicaonline.org/articles/dandanqan-a-small-town-of-medieval-khorasan-in-the-qara-qum-or-sandy-desert-between-marv-and-saraks-10-farsaks-from/",
        "Encyclopaedia Iranica",
        "academic_reference",
        "encyclopaedia_iranica_editorial_corpus",
        identity=True,
    ),
    _source(
        "wave6_peacock_seljuk",
        "A. C. S. Peacock, The Great Seljuk Empire",
        "https://edinburghuniversitypress.com/book-the-great-seljuk-empire.html",
        "Edinburgh University Press",
        "academic_monograph",
        "peacock_great_seljuk",
        identity=True,
    ),
    _source(
        "wave6_attaleiates_history",
        "Michael Attaleiates, The History",
        "https://www.hup.harvard.edu/books/9780674057999",
        "Harvard University Press",
        "primary_source_critical_edition",
        "attaleiates_history",
    ),
    _source(
        "wave6_watts_roses",
        "John Watts, The Wars of the Roses",
        "https://assets.cambridge.org/97810094/22161/frontmatter/9781009422161_frontmatter.pdf",
        "Cambridge University Press",
        "academic_monograph",
        "watts_wars_roses",
        identity=True,
    ),
    _source(
        "wave6_carpenter_roses",
        "Christine Carpenter, The Wars of the Roses",
        "https://www.cambridge.org/core/books/wars-of-the-roses/9EEFF52224669EB59CA404CD53D02106",
        "Cambridge University Press",
        "academic_monograph",
        "carpenter_wars_roses",
        identity=True,
    ),
    _source(
        "wave6_he_blore",
        "Battle of Blore Heath 1459",
        "https://historicengland.org.uk/listing/the-list/list-entry/1000002",
        "Historic England",
        "official_battlefield_register",
        "historic_england_battlefields_register",
    ),
    _source(
        "wave6_he_northampton",
        "Battle of Northampton 1460",
        "https://historicengland.org.uk/listing/the-list/list-entry/1000028",
        "Historic England",
        "official_battlefield_register",
        "historic_england_battlefields_register",
    ),
    _source(
        "wave6_he_towton",
        "Battle of Towton 1461",
        "https://historicengland.org.uk/listing/the-list/list-entry/1000040",
        "Historic England",
        "official_battlefield_register",
        "historic_england_battlefields_register",
    ),
    _source(
        "wave6_he_tewkesbury",
        "Battle of Tewkesbury 1471",
        "https://historicengland.org.uk/listing/the-list/list-entry/1000039",
        "Historic England",
        "official_battlefield_register",
        "historic_england_battlefields_register",
    ),
    _source(
        "wave6_he_barnet",
        "Battle of Barnet 1471",
        "https://historicengland.org.uk/listing/the-list/list-entry/1000001",
        "Historic England",
        "official_battlefield_register",
        "historic_england_battlefields_register",
        identity=True,
    ),
    _source(
        "wave6_he_stoke",
        "Battle of Stoke Field 1487",
        "https://historicengland.org.uk/listing/the-list/list-entry/1000036",
        "Historic England",
        "official_battlefield_register",
        "historic_england_battlefields_register",
        identity=True,
    ),
    _source(
        "wave6_ads_northumberland",
        "The Wars of the Roses in Northumberland",
        "https://archaeologydataservice.ac.uk/catalogue/adsdata/arch-3433-1/dissemination/AASeries2/AA214new/archael214-428-448-Appendix_L.pdf",
        "Archaeology Data Service / Archaeologia Aeliana",
        "academic_article",
        "archaeologia_aeliana_northumberland",
    ),
    _source(
        "wave6_cambridge_mortimers_stalbans",
        "The battles of Mortimer's Cross and Second St Albans: the regional dimension",
        "https://www.cambridge.org/core/books/abs/fifteenth-century-xiv/battles-of-mortimers-cross-and-second-st-albans-the-regional-dimension/32DB7AC978B866AB5F17EF451D635408",
        "Cambridge University Press",
        "academic_monograph_chapter",
        "cambridge_mortimers_stalbans",
    ),
)


_source_ids_by_family: dict[str, list[str]] = {}
for _wave6_source in WAVE6_PRE1500_SOURCES:
    _family_id = str(_wave6_source.get("source_family_id") or "")
    assert _family_id
    _source_ids_by_family.setdefault(_family_id, []).append(
        str(_wave6_source["id"])
    )
WAVE6_PRE1500_SOURCE_FAMILY_METADATA: tuple[dict[str, Any], ...] = tuple(
    {
        "source_family_id": _family_id,
        "source_ids": sorted(_source_ids),
        "deduplication_unit": "source_family_id",
        "independence_credit": "at_most_one_per_claim",
    }
    for _family_id, _source_ids in sorted(_source_ids_by_family.items())
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    continuity_note: str,
    source_ids: tuple[str, ...],
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
        "source_ids": list(source_ids),
    }


WAVE6_PRE1500_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "syracuse_city_state",
        "Syracuse",
        "city_state",
        -734,
        -212,
        "Sicily",
        "Continuous Syracusan city-polity identity through Roman capture; internal constitutional changes do not attach Carthaginian or Roman successors.",
        ("wave6_diodorus_sicily", "wave6_thucydides_sicily", "wave6_livy_syracuse"),
    ),
    _entity(
        "mithridatid_kingdom_pontus",
        "Mithridatid Kingdom of Pontus",
        "kingdom",
        -281,
        -63,
        "Anatolia and the Black Sea",
        "Ends with Mithridates VI and Pompey's settlement; Pharnaces II's later Bosporan reconquest receives no inherited rating.",
        ("wave6_iranica_pontus",),
    ),
    _entity(
        "republic_genoa",
        "Republic of Genoa",
        "republic",
        1099,
        1797,
        "Liguria and Genoese maritime possessions",
        "Republic identity only; separately administered Bank of Saint George colonies do not automatically inherit it.",
        ("wave6_treccani_genoa",),
    ),
    _entity(
        "duchy_milan_visconti",
        "Duchy of Milan (Visconti)",
        "duchy",
        1395,
        1447,
        "Northern Italy",
        "Ends with Filippo Maria Visconti; no rating crosses the Golden Ambrosian Republic to the Sforza duchy.",
        ("wave6_black_milan", "wave6_treccani_ambrosian"),
    ),
    _entity(
        "kingdom_castile_1065",
        "Kingdom of Castile",
        "kingdom",
        1065,
        1230,
        "Iberian Peninsula",
        "Does not back-extend to the County of Castile; the 1230 union is handled by a distinct Crown identity.",
        ("wave6_reilly_castile", "wave6_ocallaghan_iberia"),
    ),
    _entity(
        "crown_castile_1230",
        "Crown of Castile",
        "composite_monarchy",
        1230,
        1715,
        "Iberian Peninsula",
        "Distinct Crown identity; generic promotion stops before the 1479 dynastic union to avoid collision with the project Spain policy.",
        ("wave6_ocallaghan_iberia",),
    ),
    _entity(
        "crown_aragon_1164",
        "Crown of Aragon",
        "composite_monarchy",
        1164,
        1715,
        "Western Mediterranean",
        "Distinct Crown identity; generic promotion stops before the 1479 dynastic union and never becomes a Spain alias.",
        ("wave6_ocallaghan_iberia",),
    ),
    _entity(
        "clio_bg_bulgaria_early_682_95daf02a",
        "First Bulgarian Empire",
        "empire",
        681,
        1018,
        "Southeastern Europe",
        "Ends with Byzantine conquest; the Second Bulgarian Empire starts a new rating.",
        ("wave6_stephenson_balkans",),
    ),
    _entity(
        "second_bulgarian_empire",
        "Second Bulgarian Empire",
        "empire",
        1185,
        1396,
        "Southeastern Europe",
        "New polity after the Asen revolt; no rating is inherited from the First Bulgarian Empire.",
        ("wave6_stephenson_balkans", "wave6_curta_southeastern"),
    ),
    _entity(
        "kingdom_denmark_medieval",
        "Kingdom of Denmark (medieval)",
        "kingdom",
        936,
        1396,
        "Northern Europe and the Baltic",
        "Stops before the Kalmar Union and remains distinct from the modern Denmark identity beginning in 1523.",
        ("wave6_saxo_denmark",),
    ),
    _entity(
        "clio_ir_seljuk_sultanate_1040_577da931",
        "Great Seljuk Empire",
        "empire",
        1040,
        1194,
        "Iran, Iraq, and adjacent regions",
        "Bare HCED label promotion ends at Malik-Shah's death in 1092; Rum, Syria, Iraq, and Kirman Seljuks require separate identities.",
        ("wave6_iranica_dandanqan", "wave6_peacock_seljuk"),
    ),
    _entity(
        "yorkist_faction_1455",
        "Yorkist Forces (Wars of the Roses)",
        "civil_war_faction",
        1455,
        1471,
        "England and Wales",
        "Faction actor through 1471; Tudor-era pretender rebellions receive no inherited rating.",
        ("wave6_watts_roses", "wave6_carpenter_roses"),
    ),
    _entity(
        "lancastrian_faction_1455",
        "Lancastrian Forces (Wars of the Roses)",
        "civil_war_faction",
        1455,
        1471,
        "England and Wales",
        "Faction actor ends in 1471; Henry Tudor's composite 1485 army is not automatic continuation.",
        ("wave6_watts_roses", "wave6_carpenter_roses"),
    ),
    _entity(
        "simnel_yorkist_rebellion_1487",
        "Simnel Yorkist Rebellion",
        "rebel_coalition",
        1487,
        1487,
        "England and Ireland",
        "One-campaign rebel coalition; no rating is inherited from the 1455-1471 Yorkist faction.",
        ("wave6_he_stoke", "wave6_watts_roses"),
    ),
    _entity(
        "warwick_readeption_army_1471",
        "Warwick's Readeption Army",
        "rebel_coalition",
        1471,
        1471,
        "England",
        "One-campaign mixed Readeption coalition at Barnet; it is not coerced into either faction identity.",
        ("wave6_he_barnet", "wave6_watts_roses"),
    ),
)


WAVE6_PRE1500_ENTITY_IDS: frozenset[str] = frozenset(
    str(entity["id"]) for entity in WAVE6_PRE1500_ENTITIES
)
WAVE6_PRE1500_REUSED_ENTITY_IDS: frozenset[str] = frozenset(
    {
        "clio_bg_bulgaria_early_682_95daf02a",
        "clio_ir_seljuk_sultanate_1040_577da931",
    }
)
WAVE6_PRE1500_NEW_ENTITY_IDS: frozenset[str] = (
    WAVE6_PRE1500_ENTITY_IDS - WAVE6_PRE1500_REUSED_ENTITY_IDS
)
WAVE6_PRE1500_REUSED_BASELINE_ENTITY_BY_CANDIDATE_ID: dict[str, str] = {
    "hced-Adrianople718-1": "clio_bg_bulgaria_early_682_95daf02a",
    "hced-Anchialus708-1": "clio_bg_bulgaria_early_682_95daf02a",
    "hced-Anchialus763-1": "clio_bg_bulgaria_early_682_95daf02a",
    "hced-Marcellae759-1": "clio_bg_bulgaria_early_682_95daf02a",
    "hced-Marcellae792-1": "clio_bg_bulgaria_early_682_95daf02a",
    "hced-Verbitza811-1": "clio_bg_bulgaria_early_682_95daf02a",
    "hced-Versinikia813-1": "clio_bg_bulgaria_early_682_95daf02a",
    "hced-Antioch, Syria1085-1": "clio_ir_seljuk_sultanate_1040_577da931",
}


_SYRACUSE_IDS = {
    candidate_id
    for candidate_id in WAVE6_PRE1500_SAFE_CANDIDATE_IDS
    if any(
        token in candidate_id
        for token in (
            "Himera",
            "Syracuse",
            "Selinus",
            "Acragas",
            "Cabala",
            "Cronium",
            "Lilybaeum",
            "Carthage, Tunisia",
        )
    )
}
_PONTUS_IDS = {
    "hced-Chaeronea-86-1", "hced-Orchomenus-86-1", "hced-Miletopolis-85-1",
    "hced-Halys-82-1", "hced-Chalcedon-74-1",
    "hced-Cyzicus-73-1", "hced-Lemnos-73-1", "hced-Cabira-72-1",
    "hced-Zela-67-1", "hced-Lycus-66-1",
}
_GENOA_IDS = {
    "hced-Saseno1264-1", "hced-Trapani1266-1", "hced-Laiazzo1294-1",
    "hced-Kaffa1296-1", "hced-Curzola1298-1", "hced-Sapienza1354-1",
    "hced-Antium1378-1", "hced-Pula1379-1",
}
_ROSES_IDS = {
    "hced-St Albans1455-1", "hced-Blore Heath1459-1",
    "hced-Ludford Bridge1459-1", "hced-Northampton1460-1",
    "hced-Sandwich1460-1", "hced-Wakefield1460-1",
    "hced-Mortimers Cross1461-1", "hced-St Albans1461-1",
    "hced-Towton1461-1", "hced-Hedgeley Moor1464-1", "hced-Hexham1464-1",
    "hced-Barnet1471-1", "hced-Tewkesbury1471-1", "hced-Stoke1487-1",
}


WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE: dict[
    str, frozenset[str]
] = {}
for _candidate_id in _SYRACUSE_IDS:
    WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE[_candidate_id] = frozenset(
        {"syracuse_city_state"}
    )
for _candidate_id in _PONTUS_IDS:
    WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE[_candidate_id] = frozenset(
        {"mithridatid_kingdom_pontus"}
    )
for _candidate_id in _GENOA_IDS:
    WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE[_candidate_id] = frozenset(
        {"republic_genoa"}
    )
for _candidate_id in {"hced-Maclodio1427-1", "hced-Cremona1431-1", "hced-Maderno1439-1"}:
    WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE[_candidate_id] = frozenset(
        {"duchy_milan_visconti"}
    )
WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE.update(
    {
        "hced-Lantada1068-1": frozenset({"kingdom_castile_1065"}),
        "hced-Alarcos1195-1": frozenset({"kingdom_castile_1065"}),
        "hced-Gerona1285-1": frozenset({"crown_aragon_1164"}),
        "hced-Las Hormigas1285-1": frozenset({"crown_aragon_1164"}),
        "hced-Winchelsea1350-1": frozenset({"crown_castile_1230"}),
        "hced-Trajans Gate986-1": frozenset(
            {"clio_bg_bulgaria_early_682_95daf02a"}
        ),
        "hced-Arcadiopolis1194-1": frozenset({"second_bulgarian_empire"}),
        "hced-Stralsund1184-1": frozenset({"kingdom_denmark_medieval"}),
        "hced-Dandanaqan1040-1": frozenset(
            {"clio_ir_seljuk_sultanate_1040_577da931"}
        ),
        "hced-Manzikert1054-1": frozenset(
            {"clio_ir_seljuk_sultanate_1040_577da931"}
        ),
        "hced-Manzikert1071-1": frozenset(
            {"clio_ir_seljuk_sultanate_1040_577da931"}
        ),
    }
)


def resolve_wave6_pre1500_candidate_side_label(
    candidate: dict[str, Any],
    label: Any,
    low_year: int,
    high_year: int,
    context: dict[str, Any],
    resolve_generic: Any,
) -> tuple[str | None, dict[str, Any] | None, str | None, str | None]:
    """Resolve a lane label only for its fingerprint-pinned safe candidate."""

    candidate_id = str(candidate.get("candidate_id") or "")
    normalized = _normalize_label(label)
    if candidate_id in WAVE6_PRE1500_HOLD_REASONS:
        return None, None, "wave6_pre1500_curated_hold", None
    if normalized not in WAVE6_PRE1500_LABEL_POLICIES:
        return resolve_generic(label, low_year, high_year)

    if candidate_id not in WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE:
        # Denmark already has a later, central policy. Preserve it outside this
        # lane's medieval window while keeping every pre-1500 row candidate-keyed.
        if normalized == "denmark" and not wave6_pre1500_label_policy_entity_id(
            normalized, low_year, high_year
        ):
            return resolve_generic(label, low_year, high_year)
        return None, None, "wave6_pre1500_candidate_not_in_manifest", None

    entity_id = wave6_pre1500_label_policy_entity_id(
        normalized, low_year, high_year
    )
    expected_ids = WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE[
        candidate_id
    ]
    if entity_id is None or entity_id not in expected_ids:
        return None, None, "wave6_pre1500_candidate_policy_mismatch", None
    entity = context["release_entities"].get(entity_id)
    if entity is None:
        return None, None, "wave6_pre1500_target_entity_missing", None
    if low_year < int(entity["start_year"]) or high_year > int(entity["end_year"]):
        return None, None, "wave6_pre1500_target_outside_entity_window", None
    return entity_id, None, None, "wave6_pre1500_candidate_policy"
for _candidate_id in _ROSES_IDS - {"hced-Barnet1471-1", "hced-Stoke1487-1"}:
    WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE[_candidate_id] = frozenset(
        {"yorkist_faction_1455", "lancastrian_faction_1455"}
    )
WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE.update(
    {
        "hced-Barnet1471-1": frozenset(
            {"yorkist_faction_1455", "warwick_readeption_army_1471"}
        ),
        "hced-Stoke1487-1": frozenset({"simnel_yorkist_rebellion_1487"}),
    }
)


WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS: dict[str, tuple[str, ...]] = {}
for _candidate_id in _SYRACUSE_IDS:
    WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS[_candidate_id] = (
        "wave6_diodorus_sicily",
    )
WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS["hced-Syracuse-415-1"] = (
    "wave6_thucydides_sicily",
)
for _candidate_id in _PONTUS_IDS:
    WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS[_candidate_id] = (
        "wave6_appian_mithridatic",
        "wave6_plutarch_lives",
        "wave6_iranica_pontus",
    )
for _candidate_id in _GENOA_IDS:
    WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS[_candidate_id] = (
        "wave6_dotson_medieval_seas",
        "wave6_treccani_genoa",
    )
WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS.update(
    {
        "hced-Maclodio1427-1": ("wave6_treccani_maclodio", "wave6_treccani_terraferma"),
        "hced-Cremona1431-1": ("wave6_treccani_terraferma",),
        "hced-Maderno1439-1": ("wave6_moro_venice_rivers",),
        "hced-Lantada1068-1": ("wave6_reilly_castile",),
        "hced-Alarcos1195-1": ("wave6_ocallaghan_iberia", "wave6_castilla_alarcos"),
        "hced-Gerona1285-1": ("wave6_ocallaghan_iberia", "wave6_dotson_medieval_seas"),
        "hced-Las Hormigas1285-1": ("wave6_ocallaghan_iberia", "wave6_dotson_medieval_seas"),
        "hced-Winchelsea1350-1": ("wave6_cushway_winchelsea",),
        "hced-Trajans Gate986-1": ("wave6_stephenson_balkans",),
        "hced-Arcadiopolis1194-1": ("wave6_stephenson_balkans", "wave6_curta_southeastern"),
        "hced-Stralsund1184-1": ("wave6_saxo_denmark",),
        "hced-Dandanaqan1040-1": ("wave6_iranica_dandanqan", "wave6_peacock_seljuk"),
        "hced-Manzikert1054-1": ("wave6_attaleiates_history", "wave6_peacock_seljuk"),
        "hced-Manzikert1071-1": ("wave6_attaleiates_history", "wave6_peacock_seljuk"),
    }
)
for _candidate_id in _ROSES_IDS:
    WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS[_candidate_id] = (
        "wave6_watts_roses",
        "wave6_carpenter_roses",
    )
WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS.update(
    {
        "hced-Blore Heath1459-1": ("wave6_he_blore", "wave6_watts_roses"),
        "hced-Northampton1460-1": ("wave6_he_northampton", "wave6_watts_roses"),
        "hced-Mortimers Cross1461-1": ("wave6_cambridge_mortimers_stalbans",),
        "hced-St Albans1461-1": ("wave6_cambridge_mortimers_stalbans",),
        "hced-Towton1461-1": ("wave6_he_towton", "wave6_watts_roses"),
        "hced-Hedgeley Moor1464-1": ("wave6_ads_northumberland", "wave6_watts_roses"),
        "hced-Hexham1464-1": ("wave6_ads_northumberland", "wave6_watts_roses"),
        "hced-Barnet1471-1": ("wave6_he_barnet", "wave6_watts_roses"),
        "hced-Tewkesbury1471-1": ("wave6_he_tewkesbury", "wave6_watts_roses"),
        "hced-Stoke1487-1": ("wave6_he_stoke", "wave6_watts_roses"),
    }
)


_FINGERPRINT_SCALARS = (
    "source_row",
    "source_record_id",
    "name",
    "year_low",
    "year_best",
    "year_high",
    "side_1_raw",
    "side_2_raw",
    "winner_raw",
    "loser_raw",
    "theatre_raw",
)
_FINGERPRINT_SEQUENCES = (
    "seshat_side_1_candidates",
    "seshat_side_2_candidates",
    "war_names",
    "participants_raw",
)


def wave6_pre1500_fingerprint(candidate: dict[str, Any]) -> str:
    """Return the pinned semantic digest for one HCED review row."""

    payload: dict[str, str | list[str]] = {
        field: "" if candidate.get(field) is None else str(candidate.get(field))
        for field in _FINGERPRINT_SCALARS
    }
    for field in _FINGERPRINT_SEQUENCES:
        payload[field] = list(map(str, candidate.get(field, ())))
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def validate_wave6_pre1500_candidates(candidates: list[dict[str, Any]]) -> None:
    """Fail on any missing, repeated, or semantically changed manifest row."""

    rows_by_id: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        rows_by_id.setdefault(str(candidate.get("candidate_id") or ""), []).append(
            candidate
        )
    for candidate_id, expected_digest in WAVE6_PRE1500_FINGERPRINT_SHA256.items():
        rows = rows_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"stale Wave 6 pre-1500 manifest for {candidate_id}: expected "
                f"exactly one row, found {len(rows)}"
            )
        actual_digest = wave6_pre1500_fingerprint(rows[0])
        if actual_digest != expected_digest:
            raise ValueError(
                f"stale Wave 6 pre-1500 manifest for {candidate_id}: semantic "
                "fingerprint changed"
            )


def annotate_and_validate_wave6_pre1500_events(
    crosswalk_events: list[dict[str, Any]],
    label_events: list[dict[str, Any]],
) -> None:
    """Require the exact label-pass inventory and no hold or policy spillover.

    The function mutates only the audited label events by appending reviewed
    primary/academic references to ``source_ids``.  HCED remains the explicit
    outcome source until claim-level locators are curated for those references.
    """

    safe_ids = set(WAVE6_PRE1500_SAFE_CANDIDATE_IDS)
    hold_ids = set(WAVE6_PRE1500_HOLD_REASONS)
    crosswalk_by_id = {
        str(event.get("hced_candidate_id")): event for event in crosswalk_events
    }
    label_by_id = {str(event.get("hced_candidate_id")): event for event in label_events}
    all_candidate_ids = [
        str(event.get("hced_candidate_id") or "")
        for event in (*crosswalk_events, *label_events)
    ]
    repeated_manifest_ids = sorted(
        candidate_id
        for candidate_id in safe_ids
        if all_candidate_ids.count(candidate_id) != 1
    )
    if repeated_manifest_ids:
        raise ValueError(
            "Wave 6 pre-1500 safe rows must promote exactly once: "
            f"{repeated_manifest_ids}"
        )

    wrong_pass = sorted(safe_ids & set(crosswalk_by_id))
    if wrong_pass:
        raise ValueError(
            "Wave 6 pre-1500 expected label-pass-only promotion; crosswalk "
            f"accepted {wrong_pass}"
        )
    missing = sorted(safe_ids - set(label_by_id))
    if missing:
        raise ValueError(
            f"Wave 6 pre-1500 safe manifest did not promote: {missing}"
        )
    promoted_holds = sorted(hold_ids & (set(crosswalk_by_id) | set(label_by_id)))
    if promoted_holds:
        raise ValueError(f"Wave 6 pre-1500 hold promoted unexpectedly: {promoted_holds}")

    baseline_ids = set(WAVE6_PRE1500_REUSED_BASELINE_ENTITY_BY_CANDIDATE_ID)
    missing_baseline = sorted(baseline_ids - set(crosswalk_by_id))
    repeated_baseline = sorted(
        candidate_id
        for candidate_id in baseline_ids
        if all_candidate_ids.count(candidate_id) != 1
    )
    if missing_baseline or repeated_baseline:
        raise ValueError(
            "Wave 6 pre-1500 canonical-ID reuse lost or repeated Wave 5 events: "
            f"missing={missing_baseline}, repeated={repeated_baseline}"
        )
    for candidate_id, entity_id in (
        WAVE6_PRE1500_REUSED_BASELINE_ENTITY_BY_CANDIDATE_ID.items()
    ):
        participant_ids = {
            str(participant["entity_id"])
            for participant in crosswalk_by_id[candidate_id].get("participants", [])
        }
        if entity_id not in participant_ids:
            raise ValueError(
                "Wave 6 pre-1500 canonical-ID reuse changed a Wave 5 series: "
                f"{candidate_id} no longer references {entity_id}"
            )

    for candidate_id, expected_entity_ids in (
        WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE.items()
    ):
        participant_ids = {
            str(participant["entity_id"])
            for participant in label_by_id[candidate_id].get("participants", [])
        }
        actual_target_ids = participant_ids & WAVE6_PRE1500_ENTITY_IDS
        if actual_target_ids != expected_entity_ids:
            raise ValueError(
                "Wave 6 pre-1500 target identity mismatch for "
                f"{candidate_id}: expected={sorted(expected_entity_ids)}, "
                f"actual={sorted(actual_target_ids)}"
            )

    unexpected_target_users: list[str] = []
    for event in (*crosswalk_events, *label_events):
        candidate_id = str(event.get("hced_candidate_id") or "")
        participant_ids = {
            str(participant["entity_id"])
            for participant in event.get("participants", [])
        }
        if (
            participant_ids & WAVE6_PRE1500_ENTITY_IDS
            and candidate_id not in safe_ids | baseline_ids
        ):
            unexpected_target_users.append(candidate_id)
    if unexpected_target_users:
        raise ValueError(
            "Wave 6 pre-1500 label policy admitted rows outside the manifest: "
            f"{sorted(unexpected_target_users)}"
        )

    if set(WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS) != safe_ids:
        missing_evidence = sorted(
            safe_ids - set(WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS)
        )
        extra_evidence = sorted(
            set(WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS) - safe_ids
        )
        raise ValueError(
            "Wave 6 pre-1500 evidence inventory mismatch: "
            f"missing={missing_evidence}, extra={extra_evidence}"
        )
    for candidate_id in sorted(safe_ids):
        event = label_by_id[candidate_id]
        event["source_ids"] = list(
            dict.fromkeys(
                [
                    *map(str, event.get("source_ids", [])),
                    *WAVE6_PRE1500_EVENT_EVIDENCE_SOURCE_IDS[candidate_id],
                ]
            )
        )


assert len(WAVE6_PRE1500_SAFE_CANDIDATE_IDS) == 55
assert len(set(WAVE6_PRE1500_SAFE_CANDIDATE_IDS)) == 55
assert len(WAVE6_PRE1500_HOLD_REASONS) == 30
assert len(WAVE6_PRE1500_FINGERPRINT_SHA256) == 85
assert set(WAVE6_PRE1500_FINGERPRINT_SHA256) == {
    *WAVE6_PRE1500_SAFE_CANDIDATE_IDS,
    *WAVE6_PRE1500_HOLD_REASONS,
}
assert len(WAVE6_PRE1500_ENTITIES) == 15
assert len(WAVE6_PRE1500_ENTITY_IDS) == 15
assert len(WAVE6_PRE1500_REUSED_ENTITY_IDS) == 2
assert len(WAVE6_PRE1500_NEW_ENTITY_IDS) == 13
assert len(WAVE6_PRE1500_REUSED_BASELINE_ENTITY_BY_CANDIDATE_ID) == 8
assert set(WAVE6_PRE1500_EXPECTED_TARGET_ENTITY_IDS_BY_CANDIDATE) == set(
    WAVE6_PRE1500_SAFE_CANDIDATE_IDS
)
assert len({source["id"] for source in WAVE6_PRE1500_SOURCES}) == len(
    WAVE6_PRE1500_SOURCES
)
assert {
    str(source_id)
    for family in WAVE6_PRE1500_SOURCE_FAMILY_METADATA
    for source_id in family["source_ids"]
} == {str(source["id"]) for source in WAVE6_PRE1500_SOURCES}
