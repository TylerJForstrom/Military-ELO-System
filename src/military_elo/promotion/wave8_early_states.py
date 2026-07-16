"""Exact Wave 8 contracts for early Islamic, Anglo-Nepalese, and Arsacid rows."""

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


WAVE8_EARLY_STATES_FINAL_AUDIT_SIGNATURE = (
    "ca6ee01f57dca47299c49d5e0bcc9ca2411e5a0e15dd8ca6ad8f93a67313eabc"
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


WAVE8_EARLY_STATES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "cambridge_history_islam_warfare",
        "Warfare",
        "https://www.cambridge.org/core/books/abs/cambridge-history-of-islam/warfare/4DDA9E79093E4F5D50262AA3EAD71F5A",
        "Cambridge University Press",
        "academic_history",
        "cambridge_history_of_islam",
    ),
    _source(
        "iranica_arab_conquest_iran",
        "Arab conquest of Iran",
        "https://www.iranicaonline.org/articles/arab-ii/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica",
    ),
    _source(
        "iranica_ctesiphon_early_states",
        "Ctesiphon",
        "https://www.iranicaonline.org/articles/ctesiphon/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica",
    ),
    _source(
        "uchicago_early_muslim_conquests",
        "The Early Islamic Conquests",
        "https://oi.uchicago.edu/sites/default/files/uploads/shared/docs/lamine1.pdf",
        "University of Chicago Oriental Institute",
        "academic_monograph",
        "university_chicago_oriental_institute",
    ),
    _source(
        "cambridge_egypt_caliphate_641_868",
        "Egypt as a province in the Islamic caliphate, 641–868",
        "https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/FF5C416D97BB2C72F30F2E435B6AD7F4/9781139053372c3_p62-85_CBO.pdf/egypt_as_a_province_in_the_islamic_caliphate_641868.pdf",
        "Cambridge University Press",
        "academic_history",
        "cambridge_history_of_egypt",
    ),
    _source(
        "sunypress_tabari_volume_8",
        "The History of al-Tabari, Volume 8",
        "https://sunypress.edu/Books/T/The-History-of-al-abari-Vol.-82",
        "State University of New York Press",
        "translated_primary_chronicle",
        "suny_press_tabari",
        outcome=True,
    ),
    _source(
        "ucpress_quran_and_conquest_chapter_1",
        "The Qur'an and Conquest, chapter 1",
        "https://content.ucpress.edu/chapters/10213001.ch01.pdf",
        "University of California Press",
        "academic_monograph",
        "university_california_press",
        outcome=True,
    ),
    _source(
        "abertay_first_islamic_conquest_aelia",
        "The first Islamic conquest of Aelia",
        "https://rke.abertay.ac.uk/files/15112996/Al_Tel_2002_The_first_islamic_conquest_of_Aelia_PhD.pdf",
        "Abertay University",
        "doctoral_dissertation",
        "abertay_research_repository",
    ),
    _source(
        "smithsonian_yarmuk_636",
        "Yarmuk AD 636: The Muslim Conquest of Syria",
        "https://www.si.edu/object/yarmuk-ad-636-muslim-conquest-syria-david-nicolle%3Asiris_sil_1146367",
        "Smithsonian Institution Libraries",
        "library_catalogue_reference",
        "smithsonian_libraries",
    ),
    _source(
        "british_army_gurkha_history",
        "Gurkha history",
        "https://www.army.mod.uk/learn-and-explore/about-the-army/corps-regiments-and-units/brigade-of-gurkhas/gurkha-history/",
        "British Army",
        "official_military_history",
        "british_army_history",
    ),
    _source(
        "national_army_museum_gurkhas",
        "The Gurkhas",
        "https://www.nam.ac.uk/explore/gurkhas",
        "National Army Museum",
        "museum_history",
        "national_army_museum",
    ),
    _source(
        "nepal_ifa_britain_relations",
        "200 Years of Nepal-Britain Relations: A Way Forward",
        "https://ifa.gov.np/media/publications/documents/200_Years_of_Nepal-Britain_Relations_A_Way_Forward.pdf",
        "Institute of Foreign Affairs, Nepal",
        "government_research_publication",
        "nepal_institute_foreign_affairs",
    ),
    _source(
        "nepal_archaeology_anglo_nepal_war",
        "Ancient Nepal 30–39",
        "https://giwmscdnone.gov.np/media/pdf_upload/ancient_nepal_30-39_full_1497252914_1581410181.pdf",
        "Department of Archaeology, Government of Nepal",
        "government_history_journal",
        "nepal_department_archaeology",
    ),
    _source(
        "nepal_president_jitgadhi",
        "Address at Jitgadhi victory celebrations",
        "https://president.gov.np/%E0%A4%B8%E0%A4%AE%E0%A5%8D%E0%A4%AE%E0%A4%BE%E0%A4%A8%E0%A4%A8%E0%A5%80%E0%A4%AF-%E0%A4%B0%E0%A4%BE%E0%A4%B7%E0%A5%8D%E0%A4%9F%E0%A5%8D%E0%A4%B0%E0%A4%AA%E0%A4%A4%E0%A4%BF-%E0%A4%B0%E0%A4%BE-4/",
        "Office of the President of Nepal",
        "government_commemoration",
        "nepal_presidency",
    ),
    _source(
        "london_gazette_kalanga_dispatch",
        "Official dispatch on the operations at Kalanga",
        "https://www.thegazette.co.uk/London/issue/17052/page/1685/data.pdf",
        "The London Gazette",
        "official_dispatch",
        "uk_london_gazette",
    ),
    _source(
        "london_gazette_almora_dispatch",
        "Official dispatch on the capture of Almora",
        "https://www.thegazette.co.uk/London/issue/17080/page/2293/data.pdf",
        "The London Gazette",
        "official_dispatch",
        "uk_london_gazette",
    ),
    _source(
        "coleman_special_corps_gurkhas",
        "A Special Corps: The Beginnings of Gorkha Service with the British",
        "https://www.philharding.net/harding/A-Special-Corps-by-A-P-Coleman-1999.pdf",
        "A. P. Coleman",
        "historical_monograph",
        "special_corps_gurkha_history",
    ),
    _source(
        "met_parthian_empire",
        "The Parthian Empire (247 B.C.–224 A.D.)",
        "https://www.metmuseum.org/pt/essays/the-parthian-empire-247-b-c-224-a-d",
        "The Metropolitan Museum of Art",
        "museum_scholarly_essay",
        "metropolitan_museum_heilbrunn_timeline",
    ),
    _source(
        "iranica_arsacids_ii",
        "Arsacids II: The Arsacid dynasty",
        "https://www.iranicaonline.org/articles/arsacids-ii/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica",
    ),
    _source(
        "iranica_armenia_ii",
        "Armenia and Iran II: The pre-Islamic period",
        "https://www.iranicaonline.org/articles/armenia-ii/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica",
    ),
    _source(
        "iranica_hatra",
        "Hatra",
        "https://www.iranicaonline.org/articles/hatra/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica",
    ),
    _source(
        "iranica_balas_v",
        "Balash VI",
        "https://www.iranicaonline.org/articles/balas/vi-balas-v/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica",
    ),
    _source(
        "iranica_ctesiphon_parthian",
        "Ctesiphon",
        "https://www.iranicaonline.org/articles/ctesiphon/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica",
    ),
    _source(
        "iranica_antioch_gindarus",
        "Antioch in northern Syria",
        "https://www.iranicaonline.org/articles/antioch-1-northern-syria/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica",
    ),
    _source(
        "iranica_hormozdgan",
        "Hormozdgan",
        "https://www.iranicaonline.org/articles/hormozdgan/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica",
    ),
    _source(
        "uchicago_political_history_parthia",
        "A Political History of Parthia",
        "https://isac.uchicago.edu/sites/default/files/uploads/shared/docs/political_history_parthia.pdf",
        "University of Chicago Institute for the Study of Ancient Cultures",
        "academic_monograph",
        "university_chicago_isac",
    ),
    _source(
        "iranica_ecbatana",
        "Ecbatana",
        "https://www.iranicaonline.org/articles/ecbatana/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica",
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start: int,
    end: int,
    region: str,
    source_ids: list[str],
    note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start,
        "end_year": end,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            note
            + " No rating is inherited by a broader religious, ethnic, regional, "
            "imperial, predecessor, or successor label."
        ),
        "source_ids": source_ids,
    }


WAVE8_EARLY_STATES_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "medinan_muslim_polity_622_632",
        "Medinan polity under Muhammad (622–632)",
        "city_state_religious_polity",
        622,
        632,
        "Western Arabia",
        ["sunypress_tabari_volume_8", "ucpress_quran_and_conquest_chapter_1"],
        "Time-bounded Medina-centered polity used only for candidate-keyed engagements before the Rashidun succession.",
    ),
    _entity(
        "hawazin_thaqif_coalition_hunayn_630",
        "Hawazin–Thaqif coalition at Hunayn",
        "tribal_coalition",
        630,
        630,
        "Western Arabia",
        ["sunypress_tabari_volume_8", "ucpress_quran_and_conquest_chapter_1"],
        "Engagement-bounded coalition opposing the Medinan force at Hunayn.",
    ),
    _entity(
        "khaybar_oasis_defenders_628",
        "Khaybar oasis defenders",
        "oasis_defense_coalition",
        628,
        628,
        "Western Arabia",
        ["sunypress_tabari_volume_8", "ucpress_quran_and_conquest_chapter_1"],
        "Engagement-bounded defenders of the Khaybar oasis settlements.",
    ),
    _entity(
        "quraysh_meccan_field_force_uhud_625",
        "Quraysh Meccan field force at Uhud",
        "tribal_field_force",
        625,
        625,
        "Western Arabia",
        ["sunypress_tabari_volume_8", "ucpress_quran_and_conquest_chapter_1"],
        "Engagement-bounded Quraysh-led force that defeated the Medinan force at Uhud.",
    ),
    _entity(
        "byzantine_pelusium_garrison_640",
        "Byzantine garrison of Pelusium",
        "imperial_garrison",
        640,
        640,
        "Nile Delta",
        ["cambridge_egypt_caliphate_641_868", "uchicago_early_muslim_conquests"],
        "Engagement-bounded Byzantine defense at Pelusium; it is not a generic Egypt identity.",
    ),
    _entity(
        "ullais_sasanian_christian_arab_coalition_633",
        "Sasanian–Christian Arab coalition at Ullais",
        "field_coalition",
        633,
        633,
        "Lower Mesopotamia",
        ["iranica_arab_conquest_iran", "uchicago_early_muslim_conquests"],
        "Engagement-bounded Sasanian-aligned and Christian Arab force at Ullais.",
    ),
    _entity(
        "walaja_sasanian_christian_arab_coalition_633",
        "Sasanian–Christian Arab coalition at Walaja",
        "field_coalition",
        633,
        633,
        "Lower Mesopotamia",
        ["iranica_arab_conquest_iran", "uchicago_early_muslim_conquests"],
        "Engagement-bounded Sasanian-aligned and Christian Arab force at Walaja.",
    ),
    _entity(
        "nicolls_eic_kumaon_field_force_1815",
        "Nicolls's East India Company Kumaon field force",
        "company_field_force",
        1815,
        1815,
        "Kumaon Himalaya",
        ["london_gazette_almora_dispatch", "nepal_ifa_britain_relations"],
        "Engagement-bounded East India Company command in the Almora operation.",
    ),
    _entity(
        "bam_shah_nepalese_kumaon_force_1815",
        "Bam Shah's Nepalese Kumaon force",
        "state_field_force",
        1815,
        1815,
        "Kumaon Himalaya",
        ["london_gazette_almora_dispatch", "nepal_ifa_britain_relations"],
        "Engagement-bounded Nepalese force defending Almora under Bam Shah.",
    ),
    _entity(
        "ujir_singh_thapa_jitgadhi_force_1815",
        "Ujir Singh Thapa's Jitgadhi force",
        "state_garrison",
        1815,
        1815,
        "Butwal",
        ["nepal_president_jitgadhi", "nepal_archaeology_anglo_nepal_war"],
        "Engagement-bounded Nepalese defense commanded by Ujir Singh Thapa at Jitgadhi.",
    ),
    _entity(
        "wood_eic_butwal_column_1815",
        "Wood's East India Company Butwal column",
        "company_field_force",
        1815,
        1815,
        "Butwal",
        ["nepal_president_jitgadhi", "nepal_archaeology_anglo_nepal_war"],
        "Engagement-bounded East India Company column commanded by John Sullivan Wood.",
    ),
    _entity(
        "gillespie_mawby_eic_doon_force_1814",
        "Gillespie–Mawby East India Company Doon force",
        "company_field_force",
        1814,
        1814,
        "Doon Valley",
        ["london_gazette_kalanga_dispatch", "national_army_museum_gurkhas"],
        "Engagement-bounded East India Company force in the Nalapani/Kalanga siege.",
    ),
    _entity(
        "balbhadra_kunwar_nalapani_garrison_1814",
        "Balbhadra Kunwar's Nalapani garrison",
        "state_garrison",
        1814,
        1814,
        "Doon Valley",
        ["london_gazette_kalanga_dispatch", "national_army_museum_gurkhas"],
        "Engagement-bounded Nepalese garrison defending Nalapani/Kalanga.",
    ),
    _entity(
        "ochterlony_eic_malaun_force_1815",
        "Ochterlony's East India Company Malaun force",
        "company_field_force",
        1815,
        1815,
        "Western Himalaya",
        ["british_army_gurkha_history", "coleman_special_corps_gurkhas"],
        "Engagement-bounded East India Company command in the Malaun/Deothal operation.",
    ),
    _entity(
        "amar_singh_thapa_malaun_force_1815",
        "Amar Singh Thapa's Malaun force",
        "state_field_force",
        1815,
        1815,
        "Western Himalaya",
        ["british_army_gurkha_history", "coleman_special_corps_gurkhas"],
        "Engagement-bounded Nepalese force under Amar Singh Thapa at Malaun.",
    ),
    _entity(
        "nepalese_parsa_attack_force_1815",
        "Nepalese attack force at Parsa",
        "state_field_force",
        1815,
        1815,
        "Parsa",
        ["nepal_archaeology_anglo_nepal_war", "nepal_ifa_britain_relations"],
        "Engagement-bounded Nepalese force attacking the Parsa outpost.",
    ),
    _entity(
        "eic_parsa_outpost_1815",
        "East India Company Parsa outpost",
        "company_garrison",
        1815,
        1815,
        "Parsa",
        ["nepal_archaeology_anglo_nepal_war", "nepal_ifa_britain_relations"],
        "Engagement-bounded East India Company outpost defense at Parsa.",
    ),
    _entity(
        "arsacid_empire",
        "Arsacid Empire",
        "empire",
        -247,
        224,
        "Iran, Mesopotamia, and adjacent regions",
        ["met_parthian_empire", "iranica_arsacids_ii"],
        "Time-bounded Arsacid state; candidate keys bind reviewed Parthian rows without opening a generic label resolver.",
    ),
    _entity(
        "hatra_kingdom_defenders_199",
        "Kingdom of Hatra defenders in the second siege",
        "city_kingdom_garrison",
        199,
        199,
        "Upper Mesopotamia",
        ["iranica_hatra", "iranica_balas_v"],
        "Engagement-bounded Hatra defenders; HCED's broad Parthia label is an identity error for this siege.",
    ),
)


def _canonical(name: str, year: int, high: int | None = None) -> dict[str, Any]:
    end = year if high is None else high
    return {
        "canonical_key": f"{_slug(name)}:{year}:{end}",
        "date_precision": "year",
        "granularity": "engagement",
        "name": name,
        "year_low": year,
        "year_high": end,
    }


_ROW_DATA: dict[str, tuple[str, str, int]] = {
    "hced-Ain Tamar634-1": ("6343455f1080d5d35250c232d6348fcd22e6f4c15145a367b80863ddc4a45ce0", "Ayn al-Tamr", 634),
    "hced-Ajnadin634-1": ("2136612322df3216872d0612a0ff35e6f303ea3793a5a26153f07488e3b3fc12", "Battle of Ajnadayn", 634),
    "hced-Hunain630-1": ("6c186c413651731cb009c6d0ce1c44be71abff6d8a645e3b0936847b9560859d", "Battle of Hunayn", 630),
    "hced-Khaybar628-1": ("71bb9671185261bb412c9782a51d85abef0b2f31d93f5f407284158e5719773a", "Conquest of Khaybar", 628),
    "hced-Madain637-1": ("3980bd6932826fb62174f43efbd435453c380c292f5016337af7b9e323134db2", "Capture of Ctesiphon/al-Mada’in", 637),
    "hced-Mecca630-1": ("c1d047beaf9ef321301f14fd8e2a8de11063f97b2142afbc1c2077ecf882f860", "Conquest of Mecca", 630),
    "hced-Medina, Saudi Arabia627-1": ("258a46d4a212bf80bf392ea80420d265889dadb8aed57a46c6119de561698f18", "Medina", 627),
    "hced-Memphis638-1": ("0065c0b95be4fab47ec4a212dad4ec34084baa01769e2c7b89a2cfa115357c16", "Memphis", 638),
    "hced-Muta629-1": ("aef72fd0ce4a36784f5d503ae42a3040e2857d9bbf731ae443b6b51d7558dfa2", "Mu’ta", 629),
    "hced-Ohud625-1": ("9cb8b3eea74d54487e22ea6becabad593dcabd22fc42a3da928cf01c7d638bc2", "Battle of Uhud", 625),
    "hced-Pelusium640-1": ("2056d0e32202789f3efce49db7e1380496768c006296b3603d393f4cc174a878", "Siege of Pelusium", 640),
    "hced-Ullais633-1": ("8d7a2458be945545988a9f64c791943a4e8c15288e50cbe88961fb94e910dcf7", "Battle of Ullais", 633),
    "hced-Wadi al-Arabah634-1": ("fc1449255eab901f43c48f008057aab65d7f1a4ae1a7b89184f9f37ca127c613", "Wadi al-Arabah", 634),
    "hced-Walaja633-1": ("5b2d9db639cf418d5cb6132c38938f84d09bc0dc4e231827bc2a7702cd0aa4bc", "Battle of Walaja", 633),
    "hced-Yarmuk634-1": ("e3274c504961f556163e1736fc7493923f74c474dd76dada92cfbb4d9502994b", "Yarmuk", 634),
    "hced-Yarmuk636-1": ("2d0f45f2ff4c0d77009ce7d909ede082b0a204a4b0a480933d3ac113e8f4b53e", "Battle of Yarmuk", 636),
    "hced-Almorah1815-1": ("1b832419d3975e23fe430142d91232de8c02eb8ec1802da4022bbccdfed1d545", "Battle and capture of Almora", 1815),
    "hced-Jaitak1814-1815-1": ("1425921ad3e3be2c8c3f0d67a70efc4ce2805b373744f38e9f7fae11a8f13cf3", "Jaitak operations", 1814),
    "hced-Jitgargh1815-1": ("24648a1abc684c4f4297881472f2aea63dabae0cbf2b65fa3584b15fabd529ca", "Battle of Jitgadhi", 1815),
    "hced-Kalanga1814-1": ("7451203bca0f1e336a80333dae9ecc7d0400d4c405b24629660f739fdfcdeff6", "Siege of Nalapani/Kalanga", 1814),
    "hced-Katalgarh1815-1": ("f9b0ac0d13685eadddd7444ac73becf13dc852fd1864ea061e6cf8c72efd98af", "Katalgarh", 1815),
    "hced-Malaon1815-1": ("1c7e9cf87f253442bd9d9d1a5cdc9bdd1a274ff4c1c7573a4a32ce2cc99218a2", "Battle of Malaun/Deothal", 1815),
    "hced-Parsa1815-1": ("29d979afa8700e3e02e922d96911cf1d7b20cf9a46e2c47362006dd796a2705c", "Attack on the Parsa outpost", 1815),
    "hced-Arsanias62-1": ("b6d1787a1a9b0327bad34d69b5f9c3dcd4bf90db63d5f70e832d541c62fbe66a", "Capitulation at Rhandeia on the Arsanias", 62),
    "hced-Atra199-1": ("2cb0144a2b1dffc4408375db5a61809cacf6d22838e8619ae90f9e4a2b23ab6d", "Second siege of Hatra", 199),
    "hced-Carrhae-53-1": ("c2a689e72c6e27def80483cb41d30ad8e80e770bbf6f75b2701dd2b5c508886d", "Battle of Carrhae", -53),
    "hced-Ctesiphon198-1": ("5cbeb673ed468b20356103ab28185991a2e1b7e677187d6cbf21c6147a752024", "Capture of Ctesiphon", 198),
    "hced-Ecbatana-129-1": ("558ea9617ac252d1f489fc44f9b6a7329eca4991c0d86bd9dadaa738f0953737", "Antiochus VII’s final campaign", -129),
    "hced-Gindarus-38-1": ("8e62542024a00ca2d19ea71ef2355bbb2b8a8a0449d99b96e135197dc8233de7", "Battle of Gindarus", -38),
    "hced-Hormizdagan224-1": ("016233bff324e02ca390c44b44848c27c8aad70d51b51f4068d062bc5dd3d15e", "Battle of Hormozdgan", 224),
    "hced-Zab-130-1": ("2eab071d8b21495d364e5a73cc3e52363872322a681104819367581c9b5c1346", "Battle of the Greater Zab", -130),
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
    war_type: str = "interstate",
) -> dict[str, Any]:
    row_hash, name, year = _ROW_DATA[candidate_id]
    contract: dict[str, Any] = {
        "raw_row_sha256": row_hash,
        "canonical_event": _canonical(name, year),
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


WAVE8_EARLY_STATES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Ajnadin634-1": _contract(
        "hced-Ajnadin634-1", "muslim_ummah_audit", ["rashidun_caliphate"], ["byzantine_empire"], 1,
        ["abertay_first_islamic_conquest_aelia", "cambridge_history_islam_warfare"],
        "The broad source label is bound to the Rashidun and Byzantine states at Ajnadayn.",
    ),
    "hced-Hunain630-1": _contract(
        "hced-Hunain630-1", "muslim_ummah_audit", ["medinan_muslim_polity_622_632"], ["hawazin_thaqif_coalition_hunayn_630"], 1,
        ["sunypress_tabari_volume_8", "ucpress_quran_and_conquest_chapter_1"],
        "The exact Medina polity and Hawazin–Thaqif coalition replace the religious collective label.",
        war_type="state_formation_conflict",
    ),
    "hced-Khaybar628-1": _contract(
        "hced-Khaybar628-1", "muslim_ummah_audit", ["medinan_muslim_polity_622_632"], ["khaybar_oasis_defenders_628"], 1,
        ["sunypress_tabari_volume_8", "ucpress_quran_and_conquest_chapter_1"],
        "The exact Medina polity and oasis defenders replace broad religious and place labels.",
        war_type="state_formation_conflict",
    ),
    "hced-Madain637-1": _contract(
        "hced-Madain637-1", "muslim_ummah_audit", ["rashidun_caliphate"], ["sasanian_empire"], 1,
        ["iranica_arab_conquest_iran", "iranica_ctesiphon_early_states"],
        "The capture is bound to the Rashidun and Sasanian states rather than generic religious and geographic labels.",
    ),
    "hced-Ohud625-1": _contract(
        "hced-Ohud625-1", "muslim_ummah_audit", ["medinan_muslim_polity_622_632"], ["quraysh_meccan_field_force_uhud_625"], 2,
        ["sunypress_tabari_volume_8", "ucpress_quran_and_conquest_chapter_1"],
        "HCED reverses the academically attested Quraysh victory at Uhud; the result is corrected directly from the cited evidence.",
        outcome_source_ids=["ucpress_quran_and_conquest_chapter_1"],
        outcome_source_family_ids=["university_california_press"],
        war_type="state_formation_conflict",
    ),
    "hced-Pelusium640-1": _contract(
        "hced-Pelusium640-1", "muslim_ummah_audit", ["rashidun_caliphate"], ["byzantine_pelusium_garrison_640"], 1,
        ["cambridge_egypt_caliphate_641_868", "uchicago_early_muslim_conquests"],
        "The broad Egypt label is replaced by the engagement-bounded Byzantine Pelusium garrison.",
    ),
    "hced-Ullais633-1": _contract(
        "hced-Ullais633-1", "muslim_ummah_audit", ["rashidun_caliphate"], ["ullais_sasanian_christian_arab_coalition_633"], 1,
        ["iranica_arab_conquest_iran", "uchicago_early_muslim_conquests"],
        "The opposing Persia label is resolved to the exact Sasanian-aligned and Christian Arab coalition at Ullais.",
    ),
    "hced-Walaja633-1": _contract(
        "hced-Walaja633-1", "muslim_ummah_audit", ["rashidun_caliphate"], ["walaja_sasanian_christian_arab_coalition_633"], 1,
        ["iranica_arab_conquest_iran", "uchicago_early_muslim_conquests"],
        "The opposing Persia label is resolved to the exact Sasanian-aligned and Christian Arab coalition at Walaja.",
    ),
    "hced-Yarmuk636-1": _contract(
        "hced-Yarmuk636-1", "muslim_ummah_audit", ["rashidun_caliphate"], ["byzantine_empire"], 1,
        ["abertay_first_islamic_conquest_aelia", "cambridge_history_islam_warfare", "smithsonian_yarmuk_636"],
        "The 636 row is the reviewed Yarmuk engagement; Armenian contingents remain within the Byzantine imperial side.",
    ),
    "hced-Almorah1815-1": _contract(
        "hced-Almorah1815-1", "gurkha_audit", ["nicolls_eic_kumaon_field_force_1815"], ["bam_shah_nepalese_kumaon_force_1815"], 1,
        ["london_gazette_almora_dispatch", "nepal_ifa_britain_relations"],
        "The generic UK and Gurkha labels are replaced by Nicolls's Company force and Bam Shah's Nepalese force.",
        war_type="colonial_anti_colonial",
    ),
    "hced-Jitgargh1815-1": _contract(
        "hced-Jitgargh1815-1", "gurkha_audit", ["ujir_singh_thapa_jitgadhi_force_1815"], ["wood_eic_butwal_column_1815"], 1,
        ["nepal_archaeology_anglo_nepal_war", "nepal_president_jitgadhi"],
        "The exact Ujir Singh Thapa defense and Wood Company column replace the ethnic and sovereign labels.",
        war_type="colonial_anti_colonial",
    ),
    "hced-Kalanga1814-1": _contract(
        "hced-Kalanga1814-1", "gurkha_audit", ["gillespie_mawby_eic_doon_force_1814"], ["balbhadra_kunwar_nalapani_garrison_1814"], 1,
        ["london_gazette_kalanga_dispatch", "national_army_museum_gurkhas"],
        "The exact Company siege force and Balbhadra Kunwar garrison replace generic UK and Gurkha labels.",
        war_type="colonial_anti_colonial",
    ),
    "hced-Malaon1815-1": _contract(
        "hced-Malaon1815-1", "gurkha_audit", ["ochterlony_eic_malaun_force_1815"], ["amar_singh_thapa_malaun_force_1815"], 1,
        ["british_army_gurkha_history", "coleman_special_corps_gurkhas", "national_army_museum_gurkhas"],
        "The exact Ochterlony and Amar Singh Thapa formations replace generic sovereign and ethnic labels.",
        war_type="colonial_anti_colonial",
    ),
    "hced-Parsa1815-1": _contract(
        "hced-Parsa1815-1", "gurkha_audit", ["nepalese_parsa_attack_force_1815"], ["eic_parsa_outpost_1815"], 1,
        ["nepal_archaeology_anglo_nepal_war", "nepal_ifa_britain_relations"],
        "The exact Nepalese attacking force and Company outpost replace the ethnic and sovereign labels.",
        war_type="colonial_anti_colonial",
    ),
    "hced-Arsanias62-1": _contract(
        "hced-Arsanias62-1", "parthia_audit", ["arsacid_empire"], ["roman_empire"], 1,
        ["iranica_armenia_ii", "iranica_arsacids_ii"],
        "The candidate-keyed contract binds the Arsacid state without opening a generic Parthia alias.",
    ),
    "hced-Atra199-1": _contract(
        "hced-Atra199-1", "parthia_audit", ["hatra_kingdom_defenders_199"], ["roman_empire"], 1,
        ["iranica_balas_v", "iranica_hatra"],
        "HCED's Parthia label is an identity error; Hatra's own defenders repelled the Roman siege.",
    ),
    "hced-Carrhae-53-1": _contract(
        "hced-Carrhae-53-1", "parthia_audit", ["arsacid_empire"], ["roman_republic"], 1,
        ["iranica_arsacids_ii", "met_parthian_empire"],
        "The Arsacid state is bound against republican, not imperial, Rome in 53 BCE.",
    ),
    "hced-Ctesiphon198-1": _contract(
        "hced-Ctesiphon198-1", "parthia_audit", ["roman_empire"], ["arsacid_empire"], 1,
        ["iranica_ctesiphon_parthian", "uchicago_political_history_parthia"],
        "The capture is bound to imperial Rome and the time-bounded Arsacid state.",
    ),
    "hced-Gindarus-38-1": _contract(
        "hced-Gindarus-38-1", "parthia_audit", ["roman_republic"], ["arsacid_empire"], 1,
        ["iranica_antioch_gindarus", "uchicago_political_history_parthia"],
        "The battle is bound to republican Rome and the time-bounded Arsacid state.",
    ),
    "hced-Hormizdagan224-1": _contract(
        "hced-Hormizdagan224-1", "parthia_audit", ["sasanian_empire"], ["arsacid_empire"], 1,
        ["iranica_hormozdgan", "iranica_arsacids_ii"],
        "The terminal Arsacid engagement is bound to the Sasanian and Arsacid states.",
    ),
    "hced-Zab-130-1": _contract(
        "hced-Zab-130-1", "parthia_audit", ["clio_ir_seleucid_emp_bce318_21d0ee32"], ["arsacid_empire"], 1,
        ["iranica_arsacids_ii", "uchicago_political_history_parthia"],
        "HCED's Syria label is replaced by the time-valid Seleucid state at the Greater Zab.",
    ),
}


def _hold(
    candidate_id: str,
    category: str,
    reason: str,
    evidence_refs: list[str],
    *,
    terminal_exclusion: bool = False,
    duplicate_of_candidate_id: str | None = None,
) -> dict[str, Any]:
    row_hash, name, year = _ROW_DATA[candidate_id]
    high = 1815 if candidate_id == "hced-Jaitak1814-1815-1" else year
    result: dict[str, Any] = {
        "raw_row_sha256": row_hash,
        "canonical_event": _canonical(name, year, high),
        "hold_category": category,
        "hold_reason": reason,
        "evidence_refs": evidence_refs,
    }
    if terminal_exclusion:
        result["terminal_exclusion"] = True
    if duplicate_of_candidate_id is not None:
        result["duplicate_of_candidate_id"] = duplicate_of_candidate_id
    return result


WAVE8_EARLY_STATES_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Ain Tamar634-1": _hold(
        "hced-Ain Tamar634-1", "date_conflict",
        "Authoritative chronology dates Ayn al-Tamr to 633, while the pinned row says 634; no corrected year is silently invented.",
        ["iranica_arab_conquest_iran", "uchicago_early_muslim_conquests"],
    ),
    "hced-Mecca630-1": _hold(
        "hced-Mecca630-1", "exclude_not_discrete_engagement",
        "The conquest was a capitulation and occupation rather than a clean competitive engagement, so no tactical win is rated.",
        ["sunypress_tabari_volume_8", "ucpress_quran_and_conquest_chapter_1"],
        terminal_exclusion=True,
    ),
    "hced-Medina, Saudi Arabia627-1": _hold(
        "hced-Medina, Saudi Arabia627-1", "composite_events_and_actors",
        "The row conflates the Quraysh-led Trench siege with the subsequent Banu Qurayza action and cannot support one outcome or opposing side.",
        ["sunypress_tabari_volume_8", "ucpress_quran_and_conquest_chapter_1"],
    ),
    "hced-Memphis638-1": _hold(
        "hced-Memphis638-1", "date_conflict",
        "The Egyptian conquest chronology begins in 639/640, making the pinned 638 date untenable; no corrected date is invented.",
        ["cambridge_egypt_caliphate_641_868", "uchicago_early_muslim_conquests"],
    ),
    "hced-Muta629-1": _hold(
        "hced-Muta629-1", "outcome_and_actor_disputed",
        "The extent of Byzantine participation and the tactical result remain disputed, so neither side nor outcome is asserted.",
        ["abertay_first_islamic_conquest_aelia", "cambridge_history_islam_warfare"],
    ),
    "hced-Wadi al-Arabah634-1": _hold(
        "hced-Wadi al-Arabah634-1", "event_binding_unproven",
        "The evidence distinguishes a Dathin action from a later encampment at Ghamr al-Arabat and does not bind this row to one engagement.",
        ["abertay_first_islamic_conquest_aelia", "cambridge_history_islam_warfare"],
    ),
    "hced-Yarmuk634-1": _hold(
        "hced-Yarmuk634-1", "exclude_duplicate_of_reviewed_candidate",
        "This wrong-year row duplicates the reviewed 636 Battle of Yarmuk candidate and must never be rated separately.",
        ["smithsonian_yarmuk_636"],
        terminal_exclusion=True,
        duplicate_of_candidate_id="hced-Yarmuk636-1",
    ),
    "hced-Jaitak1814-1815-1": _hold(
        "hced-Jaitak1814-1815-1", "campaign_interval_mixed_outcomes",
        "The interval combines repulsed Company assaults with the later evacuation after Malaun; no single tactical result covers the row.",
        ["british_army_gurkha_history", "nepal_ifa_britain_relations"],
    ),
    "hced-Katalgarh1815-1": _hold(
        "hced-Katalgarh1815-1", "event_binding_unproven",
        "Sources separate a failed Katalgarh siege from the later defeat of Hearsey's column elsewhere, so this row is not uniquely bound.",
        ["nepal_archaeology_anglo_nepal_war", "nepal_ifa_britain_relations"],
    ),
    "hced-Ecbatana-129-1": _hold(
        "hced-Ecbatana-129-1", "event_location_binding_disputed",
        "The Parthian victory over Antiochus VII is defensible, but Ecbatana is not securely established as the battle site for this candidate.",
        ["iranica_ecbatana", "uchicago_political_history_parthia"],
    ),
}


WAVE8_EARLY_STATES_CONTRACT_IDS = frozenset(WAVE8_EARLY_STATES_CONTRACTS)
WAVE8_EARLY_STATES_HOLD_IDS = frozenset(WAVE8_EARLY_STATES_HOLDS)
WAVE8_EARLY_STATES_RESERVED_IDS = (
    WAVE8_EARLY_STATES_CONTRACT_IDS | WAVE8_EARLY_STATES_HOLD_IDS
)


def wave8_early_states_audit_signature() -> str:
    lines: list[str] = []
    for disposition, inventory in (
        ("promote", WAVE8_EARLY_STATES_CONTRACTS),
        ("hold", WAVE8_EARLY_STATES_HOLDS),
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
                        str(bool(item.get("terminal_exclusion"))),
                        str(item.get("duplicate_of_candidate_id", "")),
                    )
                )
            )
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


def _validate_static() -> None:
    if (len(WAVE8_EARLY_STATES_CONTRACTS), len(WAVE8_EARLY_STATES_HOLDS)) != (21, 10):
        raise ValueError("Wave 8 early-states disposition inventory changed")
    if WAVE8_EARLY_STATES_CONTRACT_IDS & WAVE8_EARLY_STATES_HOLD_IDS:
        raise ValueError("Wave 8 early-states promotion and hold inventories overlap")
    if wave8_early_states_audit_signature() != WAVE8_EARLY_STATES_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 early-states final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_EARLY_STATES_SOURCES}
    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_EARLY_STATES_ENTITIES}
    if len(source_by_id) != len(WAVE8_EARLY_STATES_SOURCES):
        raise ValueError("Wave 8 early-states source IDs are not unique")
    if len(entity_by_id) != len(WAVE8_EARLY_STATES_ENTITIES):
        raise ValueError("Wave 8 early-states entity IDs are not unique")

    forbidden = {"muslim ummah", "gurkhas", "parthia"}
    for entity in WAVE8_EARLY_STATES_ENTITIES:
        labels = {str(entity["name"]).casefold(), *(str(alias).casefold() for alias in entity["aliases"])}
        if labels & forbidden or str(entity["id"]).casefold() in {"muslim_ummah", "gurkhas", "parthia"}:
            raise ValueError(f"Wave 8 early-states generic identity forbidden: {entity['id']}")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"Wave 8 early-states identity must be alias-free: {entity['id']}")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"Wave 8 early-states entity has an unknown source: {entity['id']}")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"Wave 8 early-states identity lacks a reset: {entity['id']}")

    if (entity_by_id["medinan_muslim_polity_622_632"]["start_year"], entity_by_id["medinan_muslim_polity_622_632"]["end_year"]) != (622, 632):
        raise ValueError("Wave 8 Medina polity window changed")
    if (entity_by_id["arsacid_empire"]["start_year"], entity_by_id["arsacid_empire"]["end_year"], entity_by_id["arsacid_empire"]["aliases"]) != (-247, 224, []):
        raise ValueError("Wave 8 Arsacid identity boundary changed")
    for entity_id, entity in entity_by_id.items():
        if entity_id not in {"medinan_muslim_polity_622_632", "arsacid_empire"} and entity["start_year"] != entity["end_year"]:
            raise ValueError(f"Wave 8 early-states formation is not event-bounded: {entity_id}")

    external_ids = {
        "byzantine_empire", "clio_ir_seleucid_emp_bce318_21d0ee32",
        "rashidun_caliphate", "roman_empire", "roman_republic", "sasanian_empire",
    }
    canonical_keys: set[str] = set()
    override_ids: set[str] = set()
    for candidate_id, contract in WAVE8_EARLY_STATES_CONTRACTS.items():
        evidence = set(map(str, contract["evidence_refs"]))
        if not evidence or not evidence <= set(source_by_id):
            raise ValueError(f"Wave 8 early-states contract source error: {candidate_id}")
        participants = set(map(str, contract["side_1_entity_ids"])) | set(map(str, contract["side_2_entity_ids"]))
        unknown = participants - set(entity_by_id) - external_ids
        if unknown:
            raise ValueError(f"Wave 8 early-states unknown participant {candidate_id}: {sorted(unknown)}")
        canonical_key = str(contract["canonical_event"]["canonical_key"])
        if canonical_key in canonical_keys:
            raise ValueError(f"Wave 8 early-states duplicate canonical key: {canonical_key}")
        canonical_keys.add(canonical_key)
        if contract.get("source_outcome_override"):
            override_ids.add(candidate_id)
            outcome_ids = set(map(str, contract.get("outcome_source_ids", [])))
            if not outcome_ids or not outcome_ids <= evidence:
                raise ValueError(f"Wave 8 early-states override source mismatch: {candidate_id}")
            if any("outcome" not in source_by_id[source_id]["evidence_roles"] for source_id in outcome_ids):
                raise ValueError(f"Wave 8 early-states override lacks direct outcome evidence: {candidate_id}")
    if override_ids != {"hced-Ohud625-1"}:
        raise ValueError("Wave 8 early-states outcome override inventory changed")

    for candidate_id, hold in WAVE8_EARLY_STATES_HOLDS.items():
        if not set(map(str, hold["evidence_refs"])) <= set(source_by_id):
            raise ValueError(f"Wave 8 early-states hold has an unknown source: {candidate_id}")
        if not str(hold["hold_reason"]).strip():
            raise ValueError(f"Wave 8 early-states hold lacks a reason: {candidate_id}")
    terminal = {candidate_id for candidate_id, hold in WAVE8_EARLY_STATES_HOLDS.items() if hold.get("terminal_exclusion")}
    if terminal != {"hced-Mecca630-1", "hced-Yarmuk634-1"}:
        raise ValueError("Wave 8 early-states terminal exclusion inventory changed")
    duplicate = WAVE8_EARLY_STATES_HOLDS["hced-Yarmuk634-1"]
    if duplicate.get("duplicate_of_candidate_id") != "hced-Yarmuk636-1":
        raise ValueError("Wave 8 Yarmuk duplicate guard changed")


def validate_wave8_early_states_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_EARLY_STATES_CONTRACTS,
        WAVE8_EARLY_STATES_HOLDS,
        lane_name="Wave 8 early states",
    )


def install_wave8_early_states_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_EARLY_STATES_ENTITIES,
        lane_name="Wave 8 early states",
    )


def install_wave8_early_states_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_EARLY_STATES_SOURCES,
        lane_name="Wave 8 early states",
    )


def promote_wave8_early_states_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_early_states_queue_contracts(hced_rows)
    return promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_EARLY_STATES_CONTRACTS,
        lane_name="Wave 8 early states",
        event_id_prefix="hced_wave8_early_states_",
    )


def wave8_early_states_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_EARLY_STATES_CONTRACTS.values()
            ).items()
        )
    )
