"""Exact Wave 8 contracts for HCED rows blocked by the label ``Muslims``.

The source label is never an identity.  Every promoted row is bound to a
specific polity, campaign force, garrison, or event-bounded contingent.  Holds
and terminal exclusions reserve only rows that were fully audited, and no
unknown outcome is converted into a draw.
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
    "WAVE8_MUSLIM_FORCES_CONTRACTS",
    "WAVE8_MUSLIM_FORCES_CONTRACT_IDS",
    "WAVE8_MUSLIM_FORCES_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_MUSLIM_FORCES_DUPLICATE_DISPOSITIONS",
    "WAVE8_MUSLIM_FORCES_ENTITIES",
    "WAVE8_MUSLIM_FORCES_EXCLUSIONS",
    "WAVE8_MUSLIM_FORCES_EXCLUSION_IDS",
    "WAVE8_MUSLIM_FORCES_EXPECTED_CANDIDATE_IDS",
    "WAVE8_MUSLIM_FORCES_FINAL_AUDIT_SIGNATURE",
    "WAVE8_MUSLIM_FORCES_HOLDS",
    "WAVE8_MUSLIM_FORCES_HOLD_IDS",
    "WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS",
    "WAVE8_MUSLIM_FORCES_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_MUSLIM_FORCES_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_MUSLIM_FORCES_NONPROMOTIONS",
    "WAVE8_MUSLIM_FORCES_OUTCOME_OVERRIDE_METADATA",
    "WAVE8_MUSLIM_FORCES_OUTCOME_OVERRIDES",
    "WAVE8_MUSLIM_FORCES_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_MUSLIM_FORCES_RESERVED_IDS",
    "WAVE8_MUSLIM_FORCES_SOURCES",
    "WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS",
    "WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSION_IDS",
    "install_wave8_muslim_forces_entities",
    "install_wave8_muslim_forces_sources",
    "promote_wave8_muslim_forces_contracts",
    "validate_wave8_muslim_forces_queue_contracts",
    "wave8_muslim_forces_audit_signature",
    "wave8_muslim_forces_cohort_counts",
    "wave8_muslim_forces_counts",
)


_LANE_NAME = "Wave 8 exact HCED Muslim-forces audit"
_EVENT_ID_PREFIX = "hced_wave8_muslim_forces_"
WAVE8_MUSLIM_FORCES_FINAL_AUDIT_SIGNATURE = (
    "4249d0151a73002c77a32f63f0a053f349ce5c5a1e6daf430576b4ff640eeb13"
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
        "evidence_roles": sorted(roles),
    }


WAVE8_MUSLIM_FORCES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_muslim_forces_donner_early_conquests",
        "The Early Islamic Conquests",
        "https://oi.uchicago.edu/sites/default/files/uploads/shared/docs/lamine1.pdf",
        "University of Chicago Oriental Institute",
        "academic_monograph",
        "university_chicago_oriental_institute",
    ),
    _source(
        "wave8_muslim_forces_iranica_arab_conquest",
        "Arab conquest of Iran",
        "https://www.iranicaonline.org/articles/arab-ii/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica",
    ),
    _source(
        "wave8_muslim_forces_cambridge_egypt_641_868",
        "Egypt as a province in the Islamic caliphate, 641–868",
        "https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/FF5C416D97BB2C72F30F2E435B6AD7F4/9781139053372c3_p62-85_CBO.pdf/egypt_as_a_province_in_the_islamic_caliphate_641868.pdf",
        "Cambridge University Press",
        "academic_history",
        "cambridge_history_of_egypt",
    ),
    _source(
        "wave8_muslim_forces_cambridge_byzantine_egypt",
        "Byzantine Egypt: Economy, Society and Culture (excerpt)",
        "https://assets.cambridge.org/97805211/45879/excerpt/9780521145879_excerpt.pdf",
        "Cambridge University Press",
        "academic_monograph",
        "cambridge_byzantine_egypt",
    ),
    _source(
        "wave8_muslim_forces_garrood_aleppo",
        "The Byzantine conquest of Cilicia and the Hamdanids of Aleppo, 959–965",
        "https://www.cambridge.org/core/journals/anatolian-studies/article/abs/byzantine-conquest-of-cilicia-and-the-hamdanids-of-aleppo-959965/5C9F862B3ADFB1C123A58AB76F6BD157",
        "Cambridge University Press",
        "peer_reviewed_journal_article",
        "anatolian_studies",
    ),
    _source(
        "wave8_muslim_forces_cnrs_aleppo",
        "Alep, de la conquête arabe à la conquête ottomane",
        "https://books.openedition.org/editionscnrs/88878",
        "CNRS Éditions / OpenEdition",
        "academic_history_chapter",
        "cnrs_editions_aleppo",
    ),
    _source(
        "wave8_muslim_forces_bbaw_amida",
        "Prosopography of the Middle Byzantine Period: Melias entry",
        "https://telota.bbaw.de/pmbz/scripts/browse.xql?target=PMBZ24742",
        "Berlin-Brandenburg Academy of Sciences and Humanities",
        "institutional_prosopography",
        "bbaw_pmbz",
    ),
    _source(
        "wave8_muslim_forces_sorbonne_antioch",
        "Antioche au Xe siècle",
        "https://books.openedition.org/psorbonne/1932?lang=en",
        "Éditions de la Sorbonne / OpenEdition",
        "academic_history_chapter",
        "sorbonne_byzantine_syria",
    ),
    _source(
        "wave8_muslim_forces_konstanz_amorium",
        "The Arab occupation of Amorion in 669 and its later recovery",
        "https://wiki.uni-konstanz.de/transmed-de/index.php/785-791%3A_Papst_Hadrian_I._kritisiert_einen_Verfall_christlicher_Lehre_und_Praxis_auf_der_Iberischen_Halbinsel",
        "University of Konstanz Transmediterranean History",
        "academic_reference",
        "university_konstanz_transmed",
        outcome=False,
    ),
    _source(
        "wave8_muslim_forces_birmingham_amorium",
        "The first Arab siege of Constantinople: the campaign of Yazid b. Mu'awiya",
        "https://research.birmingham.ac.uk/en/publications/the-first-arab-siege-of-constantinople-the-campaign-of-yazid-b-mu/",
        "University of Birmingham Research Portal",
        "academic_book_chapter",
        "university_birmingham_research",
        outcome=False,
    ),
    _source(
        "wave8_muslim_forces_cambridge_buzakha",
        "The evolution of a Companion report",
        "https://www.cambridge.org/core/services/aop-cambridge-core/content/view/937D3E1F8957DE0D8AB1BC151F14DD91/S0041977X25100621a.pdf/he_was_penetrated_like_a_woman_the_evolution_of_a_companion_report.pdf",
        "Cambridge University Press",
        "peer_reviewed_journal_article",
        "bulletin_school_oriental_african_studies",
    ),
    _source(
        "wave8_muslim_forces_tabari_volume_10",
        "The History of al-Tabari, Volume 10: The Conquest of Arabia",
        "https://sunypress.edu/Books/T/The-History-of-al-abari-Vol.-102",
        "State University of New York Press",
        "translated_primary_chronicle",
        "suny_press_tabari",
    ),
    _source(
        "wave8_muslim_forces_metcalfe_sicily",
        "The Muslims of Medieval Italy",
        "https://edinburghuniversitypress.com/book-the-muslims-of-medieval-italy.html",
        "Edinburgh University Press",
        "academic_monograph",
        "edinburgh_university_press",
    ),
    _source(
        "wave8_muslim_forces_unesco_enna",
        "Arab-Norman Palermo and the Cathedral Churches: nomination dossier",
        "https://whc.unesco.org/uploads/nominations/1487.pdf",
        "UNESCO World Heritage Centre",
        "institutional_historical_dossier",
        "unesco_world_heritage_centre",
    ),
    _source(
        "wave8_muslim_forces_malaterra_cerami",
        "Geoffrey Malaterra, The Deeds of Count Roger, Book II",
        "https://eprints.whiterose.ac.uk/id/eprint/213518/1/Deeds%20of%20Count%20Roger%20part%20two.pdf",
        "White Rose Research Online, University of Leeds",
        "critical_translation_primary_chronicle",
        "white_rose_research_online",
    ),
    _source(
        "wave8_muslim_forces_cambridge_visigothic_conquest",
        "Coinage in Spain in the aftermath of the Islamic conquest",
        "https://www.cambridge.org/core/books/abs/minting-state-and-economy-in-the-visigothic-kingdom/coinage-in-spain-in-the-aftermath-of-the-islamic-conquest/5B18B6610F8A2E235F5312CA8464A575",
        "Cambridge University Press",
        "academic_history_chapter",
        "cambridge_visigothic_kingdom",
    ),
    _source(
        "wave8_muslim_forces_barcelona_iberia_711",
        "La conquista islámica de la península ibérica y la tergiversación del pasado",
        "https://diposit.ub.edu/dspace/bitstream/2445/116723/1/JSA_TESIS.pdf",
        "University of Barcelona Digital Repository",
        "doctoral_dissertation",
        "university_barcelona_repository",
    ),
    _source(
        "wave8_muslim_forces_cambridge_arqa",
        "The First Crusade and the conquest of Jerusalem",
        "https://www.cambridge.org/core/books/encountering-islam-on-the-first-crusade/first-crusade-and-the-conquest-of-jerusalem/F0BCDCA3818B44A9ABB1DEAA2C615A48",
        "Cambridge University Press",
        "academic_history_chapter",
        "cambridge_encountering_islam",
    ),
    _source(
        "wave8_muslim_forces_cambridge_siege_tactics",
        "Frankish siege tactics",
        "https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/ADB87140C73EA51F6CDA0E9A19B1C6A1/9780511497247c13_p203-216_CBO.pdf/frankish_siege_tactics.pdf",
        "Cambridge University Press",
        "academic_history_chapter",
        "cambridge_crusader_warfare",
    ),
    _source(
        "wave8_muslim_forces_routledge_baldwin",
        "Baldwin I of Jerusalem, 1100–1118",
        "https://www.routledge.com/Baldwin-I-of-Jerusalem-1100-1118/Edgington/p/book/9780367662370",
        "Routledge",
        "academic_monograph",
        "routledge_crusader_history",
    ),
    _source(
        "wave8_muslim_forces_gesta_harenc",
        "Gesta Francorum 6.17: Ridwan's relief army defeated near Antioch",
        "https://dcc.dickinson.edu/gesta-francorum/6-17-5%E2%80%936",
        "Dickinson College Commentaries",
        "critical_edition_primary_chronicle",
        "dickinson_college_commentaries",
    ),
    _source(
        "wave8_muslim_forces_cambridge_ceuta",
        "North Africa",
        "https://www.cambridge.org/core/books/abs/history-of-portugal-and-the-portuguese-empire/north-africa/EA59E9E8A1D96483B9650A5D0B251E3F",
        "Cambridge University Press",
        "academic_history_chapter",
        "cambridge_history_portugal",
    ),
    _source(
        "wave8_muslim_forces_cham_ceuta_sources",
        "Sources for the history of Portuguese expansion in Morocco, Volume I",
        "https://cham.fcsh.unl.pt/portugalemarrocos/files/sources_portugal_tomo_I.pdf",
        "CHAM, NOVA University Lisbon",
        "institutional_primary_source_collection",
        "cham_nova_portuguese_expansion",
    ),
    _source(
        "wave8_muslim_forces_cambridge_mongols_aleppo",
        "The Battle of 'Ayn Jalut and the Mongol conquest of Syria",
        "https://www.cambridge.org/core/books/abs/mongols-and-mamluks/battle-of-ayn-jalut/28AF2C512086301FC77D6DC25EAAF02D",
        "Cambridge University Press",
        "academic_monograph_chapter",
        "cambridge_mongols_and_mamluks",
    ),
    _source(
        "wave8_muslim_forces_cambridge_egypt_syria",
        "Egypt and Syria under the Mongols and Mamluks",
        "https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/2800F3B21E1FEA0881D0E757534113DC/9781139055024c6_p175-230_CBO.pdf/egypt_and_syria.pdf",
        "Cambridge University Press",
        "academic_history_chapter",
        "cambridge_history_mongol_empire",
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_MUSLIM_FORCES_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    source_ids: Iterable[str],
    boundary: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary
            + " No rating is inherited by a generic Muslim identity, another "
            "dynasty, a later polity, or a force in another century."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_ALEPPO_962 = "sayf_al_dawla_aleppo_force_962"
_ALEPPO_1260 = "ayyubid_aleppo_city_garrison_1260"
_GEORGIANS_1260 = "georgian_aleppo_contingent_1260"
_ARMENIANS_1260 = "cilician_armenian_aleppo_contingent_1260"
_RUM_1260 = "rum_seljuq_aleppo_contingent_1260"
_AMIDA_973 = "hamdanid_mosul_amida_relief_force_973"
_ANTIOCH_969 = "az_zughayli_antioch_garrison_969"
_BALDWIN_BEIRUT = "baldwin_i_beirut_siege_force_1110"
_BERTRAND_BEIRUT = "bertrand_tripoli_beirut_force_1110"
_GENOESE_BEIRUT = "genoese_beirut_blockade_fleet_1110"
_PISAN_BEIRUT = "pisan_beirut_blockade_fleet_1110"
_BEIRUT_GARRISON = "fatimid_beirut_garrison_1110"
_BEIRUT_RELIEF = "fatimid_coastal_relief_fleet_beirut_1110"
_BUZAKHA = "tulayha_asad_ghatafan_force_buzakha_632"
_ENNA_859 = "al_abbas_aghlabid_enna_force_859"
_ROGER_CERAMI = "roger_i_norman_force_cerami_1063"
_AFRICAN_CERAMI = "african_reinforcement_contingent_cerami_1063"
_SICILIAN_CERAMI = "sicilian_defending_force_cerami_1063"
_CEUTA_1415 = "salah_ben_salah_ceuta_defenders_1415"
_TARIQ_711 = "tariq_ibn_ziyad_invasion_army_711"
_RODERIC_711 = "roderic_visigothic_royal_army_711"
_ECIJA_711 = "ecija_visigothic_defenders_711"
_BOHEMOND_1098 = "bohemond_lake_antioch_cavalry_1098"
_RIDWAN_1098 = "ridwan_aleppo_relief_army_1098"


WAVE8_MUSLIM_FORCES_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _ALEPPO_962,
        "Sayf al-Dawla's Aleppo force in 962",
        "event_bounded_emirate_force",
        962,
        "Northern Syria",
        ["wave8_muslim_forces_cnrs_aleppo", "wave8_muslim_forces_garrood_aleppo"],
        "This identity ends with Nikephoros Phokas's December 962 capture and sack of Aleppo.",
    ),
    _entity(
        _ALEPPO_1260,
        "Ayyubid Aleppo city garrison in January 1260",
        "event_bounded_city_garrison",
        1260,
        "Northern Syria",
        ["wave8_muslim_forces_cambridge_mongols_aleppo"],
        "This identity covers Turanshah's defenders of Aleppo city, not the later citadel capitulation or another Ayyubid line.",
    ),
    _entity(
        _GEORGIANS_1260,
        "Georgian contingent at Aleppo in 1260",
        "event_bounded_allied_contingent",
        1260,
        "Northern Syria",
        ["wave8_muslim_forces_cambridge_mongols_aleppo"],
        "This identity is limited to the Georgian contingent accompanying Hülegü at Aleppo.",
    ),
    _entity(
        _ARMENIANS_1260,
        "Cilician Armenian contingent at Aleppo in 1260",
        "event_bounded_allied_contingent",
        1260,
        "Northern Syria",
        ["wave8_muslim_forces_cambridge_mongols_aleppo"],
        "This identity is limited to the Cilician Armenian contingent accompanying Hülegü at Aleppo.",
    ),
    _entity(
        _RUM_1260,
        "Rūm Seljuq contingent at Aleppo in 1260",
        "event_bounded_allied_contingent",
        1260,
        "Northern Syria",
        ["wave8_muslim_forces_cambridge_mongols_aleppo"],
        "This identity is limited to the Rūm Seljuq contingent accompanying Hülegü at Aleppo.",
    ),
    _entity(
        _AMIDA_973,
        "Hamdanid Mosul relief force at Amida in 973",
        "event_bounded_relief_army",
        973,
        "Upper Mesopotamia",
        ["wave8_muslim_forces_bbaw_amida"],
        "This identity covers Hibatallah's relief force at Amida on 3 July 973 and not a timeless Hamdanid actor.",
    ),
    _entity(
        _ANTIOCH_969,
        "Az-Zughayli's Antioch garrison in 969",
        "event_bounded_city_garrison",
        969,
        "Northern Syria",
        ["wave8_muslim_forces_sorbonne_antioch"],
        "This identity ends with the Byzantine capture of Antioch on 28 October 969.",
    ),
    _entity(
        _BALDWIN_BEIRUT,
        "Baldwin I's Jerusalem force at Beirut in 1110",
        "event_bounded_siege_force",
        1110,
        "Levantine coast",
        ["wave8_muslim_forces_cambridge_siege_tactics", "wave8_muslim_forces_routledge_baldwin"],
        "This identity covers Baldwin I's force in the February–May 1110 siege of Beirut only.",
    ),
    _entity(
        _BERTRAND_BEIRUT,
        "Bertrand of Tripoli's force at Beirut in 1110",
        "event_bounded_siege_force",
        1110,
        "Levantine coast",
        ["wave8_muslim_forces_cambridge_siege_tactics", "wave8_muslim_forces_routledge_baldwin"],
        "This identity covers Bertrand's attested force in the Beirut siege only.",
    ),
    _entity(
        _GENOESE_BEIRUT,
        "Genoese fleet at Beirut in 1110",
        "event_bounded_naval_contingent",
        1110,
        "Levantine coast",
        ["wave8_muslim_forces_cambridge_siege_tactics", "wave8_muslim_forces_routledge_baldwin"],
        "This identity covers the Genoese blockade contingent at Beirut only.",
    ),
    _entity(
        _PISAN_BEIRUT,
        "Pisan fleet at Beirut in 1110",
        "event_bounded_naval_contingent",
        1110,
        "Levantine coast",
        ["wave8_muslim_forces_cambridge_siege_tactics"],
        "This identity covers the Pisan blockade contingent at Beirut only.",
    ),
    _entity(
        _BEIRUT_GARRISON,
        "Fatimid Beirut garrison in 1110",
        "event_bounded_city_garrison",
        1110,
        "Levantine coast",
        ["wave8_muslim_forces_cambridge_siege_tactics", "wave8_muslim_forces_routledge_baldwin"],
        "This identity ends with the capture of Beirut on 13 May 1110.",
    ),
    _entity(
        _BEIRUT_RELIEF,
        "Fatimid coastal relief fleet at Beirut in 1110",
        "event_bounded_naval_force",
        1110,
        "Levantine coast",
        ["wave8_muslim_forces_cambridge_siege_tactics"],
        "This identity covers the Fatimid ships from Tyre and Sidon that attempted to break the Beirut blockade.",
    ),
    _entity(
        _BUZAKHA,
        "Tulayha's Asad–Ghatafan force at Buzakha in 632",
        "event_bounded_tribal_coalition",
        632,
        "Central Arabia",
        ["wave8_muslim_forces_cambridge_buzakha", "wave8_muslim_forces_tabari_volume_10"],
        "This identity is the source-attested force under Tulayha at Buzakha, not either tribe in other contexts.",
    ),
    _entity(
        _ENNA_859,
        "Al-Abbas ibn al-Fadl's Aghlabid Sicilian force at Enna in 859",
        "event_bounded_field_force",
        859,
        "Sicily",
        ["wave8_muslim_forces_metcalfe_sicily", "wave8_muslim_forces_unesco_enna"],
        "This identity ends with the January 859 capture of Enna and does not merge other Aghlabid campaigns.",
    ),
    _entity(
        _ROGER_CERAMI,
        "Roger I's Norman force at Cerami in 1063",
        "event_bounded_field_force",
        1063,
        "Sicily",
        ["wave8_muslim_forces_malaterra_cerami", "wave8_muslim_forces_metcalfe_sicily"],
        "This identity is Roger's force at Cerami and not a timeless Norman polity.",
    ),
    _entity(
        _AFRICAN_CERAMI,
        "African reinforcement contingent at Cerami in 1063",
        "event_bounded_allied_contingent",
        1063,
        "Sicily",
        ["wave8_muslim_forces_malaterra_cerami"],
        "This identity preserves Malaterra's separately attested African contingent at Cerami.",
    ),
    _entity(
        _SICILIAN_CERAMI,
        "Sicilian defending force at Cerami in 1063",
        "event_bounded_field_force",
        1063,
        "Sicily",
        ["wave8_muslim_forces_malaterra_cerami", "wave8_muslim_forces_metcalfe_sicily"],
        "This identity preserves the Sicilian force at Cerami without extending it to another emirate or campaign.",
    ),
    _entity(
        _CEUTA_1415,
        "Salah ben Salah's Ceuta defenders in 1415",
        "event_bounded_city_defence",
        1415,
        "Strait of Gibraltar",
        ["wave8_muslim_forces_cambridge_ceuta", "wave8_muslim_forces_cham_ceuta_sources"],
        "This identity covers the urban garrison and locally summoned defenders of Ceuta during the Portuguese assault.",
    ),
    _entity(
        _TARIQ_711,
        "Tariq ibn Ziyad's invasion army in Iberia in 711",
        "campaign_bounded_invasion_army",
        711,
        "Southern Iberia",
        ["wave8_muslim_forces_barcelona_iberia_711", "wave8_muslim_forces_cambridge_visigothic_conquest"],
        "This identity is limited to Tariq's 711 invasion campaign and does not absorb later Andalusi dynasties.",
    ),
    _entity(
        _RODERIC_711,
        "Roderic's Visigothic royal army in 711",
        "event_bounded_royal_army",
        711,
        "Southern Iberia",
        ["wave8_muslim_forces_barcelona_iberia_711", "wave8_muslim_forces_cambridge_visigothic_conquest"],
        "This identity ends with Roderic's defeat in the summer 711 battle traditionally called Guadalete.",
    ),
    _entity(
        _ECIJA_711,
        "Écija defenders and Visigothic survivors in 711",
        "event_bounded_city_field_force",
        711,
        "Southern Iberia",
        ["wave8_muslim_forces_barcelona_iberia_711"],
        "This identity covers the local defenders and survivors who fought Tariq near Écija after Guadalete.",
    ),
    _entity(
        _BOHEMOND_1098,
        "Bohemond's crusader cavalry at the Lake of Antioch in 1098",
        "event_bounded_field_force",
        1098,
        "Northern Syria and Antioch",
        ["wave8_muslim_forces_gesta_harenc"],
        "This identity is limited to the 9 February 1098 sortie against Ridwan's relief army.",
    ),
    _entity(
        _RIDWAN_1098,
        "Ridwan of Aleppo's relief army at Antioch in 1098",
        "event_bounded_relief_army",
        1098,
        "Northern Syria and Antioch",
        ["wave8_muslim_forces_gesta_harenc"],
        "This identity ends with the defeat of Ridwan's relief army on 9 February 1098.",
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
    "hced-Aleppo639-1": ("7dd4c3588cf1b3c40752ba02d55cf82caf62f23dc351ce15c7959a06ea12f39c", "Reported submission of Aleppo", 639),
    "hced-Aleppo962-1": ("337c99cb7e8553dce69bc2f9708ad18223c013898fdbe3231e4c29ed58a5895b", "Capture of Aleppo", 962),
    "hced-Aleppo969-1": ("6e97db73161cce95561bacac32e9e5db122cd7b2e9ca788a8f7b3f3ba31276f9", "Aleppo protectorate transition", 969),
    "hced-Aleppo1260-1": ("5d092bdf4347bb271701f747cc225f032dae2c684a14993653f9a5b2cefece23", "Capture of Aleppo city", 1260),
    "hced-Alexandria641-642-1": ("5bfb1a1c4a4216b3eccdb3baf0d48dffd1f97db685f3c6b899e35d881d332150", "First siege and treaty of Alexandria", 641),
    "hced-Alexandria645-1": ("fb7abbf7ecb8e9688d233735ab32247f2a693c0300e338ee4005b3c733ddfc98", "Alexandria reconquest assertion", 645),
    "hced-Amida973-1": ("c4386a42bd8d8c59e04e0902f720a62a0918a0ea63017a66e667ef8e5f6b27c4", "Battle of Amida", 973),
    "hced-Amorium669-1": ("f4dcf265ba30377dfa3ec489bf16d6e2ed4eebb56a41c6da26f28aaef083de66", "Reported Byzantine recovery of Amorium", 669),
    "hced-Antioch, Syria969-1": ("274a6d5dd8791211ab2dc8e313da7b17ac634b8c6a2c250ccced9282bbf27204", "Capture of Antioch", 969),
    "hced-Arqa1098-1": ("1c8f22de80a9be75edbe00915a654f5b9e67184ebd7e5f573d7592ee8102fee7", "Siege of Arqa assertion", 1098),
    "hced-Babylon, Egypt640-1": ("b256680a4b6890528f3fcb412f27a075f1bb6f4f6a1a2b22fc6294a71a5a6677", "Siege of Babylon fortress assertion", 640),
    "hced-Babylon, Iraq634-1": ("6bb0e1c392cab6d2fb277b7c68c7f435e744222e11a4471005b12fd45e6b7f8b", "Reported battle at Babylon in Iraq", 634),
    "hced-Beirut1110-1": ("e7b71fb2f0fd28abe41809e8dfdea2b2c6d674bf5f3a3916774326bae3e46eb2", "Siege and capture of Beirut", 1110),
    "hced-Bosra634-1": ("0a36af2bcc49fc3f7e405dc6c61c15748cbda69634cb5152b9ca828885ba1844", "Siege and capitulation of Bostra", 634),
    "hced-Bridge634-1": ("aa59c38557cd7933749a11b27a0722c585d3e595ea3bcebc71e968ab9d223887", "Battle of the Bridge", 634),
    "hced-Buwayb635-1": ("84a93ed5fc9ed8cc27bc65c713e280572d6ae28b5f7f946a6ab343bf1d54ba29", "Reported battle of Buwayb", 635),
    "hced-Buzakha632-1": ("06a1fa05e193857da2d305d3893450bc2389204e50a704bbeb6620603d54ce1f", "Battle of Buzakha", 632),
    "hced-Castrogiovanni859-1": ("0d3a412e4083c0ff1bbe14a88eb2bd1b9ad6f708155ca370719d56e8e09175e2", "Capture of Enna (Castrogiovanni)", 859),
    "hced-Cerami1063-1": ("c4894a71dde240515a84d42fc4328d5fd0eebc8b2f4facd2a1280544c37e4887", "Battle of Cerami", 1063),
    "hced-Ceuta1415-1": ("ebddf7b2aadd47083ceb80dfa80b59f64a12b51c13b0542eae34eef8a2a2b638", "Capture of Ceuta", 1415),
    "hced-Ecija711-1": ("0fee77ecb9cfa91a8f7b9cf843cd5519978798ecfa7d60243ae757519c2af04d", "Battle near Écija", 711),
    "hced-Guadalete711-1": ("3625f32799ce91a3aeb121d74c2872b7dbf4384c3db1c66a3225b5888f07e0e4", "Battle traditionally called Guadalete", 711),
    "hced-Harenc1098-1": ("07bddbda776deff8ed8c27c3578457e2f9a6c411faa59979cc02f1a1694ef76f", "Battle of the Lake of Antioch (Harenc)", 1098),
}


def _contract(
    candidate_id: str,
    cohort: str,
    side_1: Iterable[str],
    side_2: Iterable[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    reviewed_date: str,
    reviewed_sides: Iterable[str],
    reviewed_outcome: str,
    event_boundary: str,
    war_type: str = "interstate",
) -> dict[str, Any]:
    row_hash, name, year = _ROW_DATA[candidate_id]
    evidence = sorted(set(map(str, evidence_refs)))
    outcome_sources = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": row_hash,
        "canonical_event": _canonical(name, year),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "winner_side": winner_side,
        "result_type": "win",
        "war_type": war_type,
        "evidence_refs": evidence,
        "outcome_source_ids": outcome_sources,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcome_sources
            }
        ),
        "source_outcome_override": False,
        "actor_override": True,
        "outcome_reversal": False,
        "direct_provenance": {
            "reviewed_date": reviewed_date,
            "reviewed_sides": list(map(str, reviewed_sides)),
            "reviewed_outcome": reviewed_outcome,
            "event_boundary": event_boundary,
        },
        "audit_note": audit_note,
    }


WAVE8_MUSLIM_FORCES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Aleppo962-1": _contract(
        "hced-Aleppo962-1",
        "byzantine_arab_wars",
        ["byzantine_empire"],
        [_ALEPPO_962],
        1,
        ["wave8_muslim_forces_cnrs_aleppo", "wave8_muslim_forces_garrood_aleppo"],
        ["wave8_muslim_forces_garrood_aleppo"],
        "Nikephoros Phokas's force captured and sacked Sayf al-Dawla's Aleppo; the Hamdanid force is not extended to Aleppo in 969 or to Mosul in 973.",
        reviewed_date="18–23 December 962",
        reviewed_sides=["Byzantine army under Nikephoros Phokas", "Sayf al-Dawla's Aleppo force"],
        reviewed_outcome="Byzantine capture and sack of Aleppo",
        event_boundary="The six-day siege and capture, not the surrounding Cilician campaign.",
    ),
    "hced-Aleppo1260-1": _contract(
        "hced-Aleppo1260-1",
        "mongol_era_actors",
        ["mongol_empire", _GEORGIANS_1260, _ARMENIANS_1260, _RUM_1260],
        [_ALEPPO_1260],
        1,
        ["wave8_muslim_forces_cambridge_egypt_syria", "wave8_muslim_forces_cambridge_mongols_aleppo"],
        ["wave8_muslim_forces_cambridge_mongols_aleppo"],
        "The Mongol army and its Georgian, Cilician Armenian, and Rūm Seljuq contingents captured Aleppo city from Turanshah's defenders; the later citadel capitulation is outside this contract.",
        reviewed_date="18–24 January 1260",
        reviewed_sides=["Hülegü's Mongol army", "Georgian contingent", "Cilician Armenian contingent", "Rūm Seljuq contingent", "Ayyubid Aleppo city garrison under Turanshah"],
        reviewed_outcome="Capture of Aleppo city by Hülegü's army and named allied contingents",
        event_boundary="The investment and capture of the city; the separately timed citadel capitulation is excluded.",
    ),
    "hced-Amida973-1": _contract(
        "hced-Amida973-1",
        "byzantine_arab_wars",
        [_AMIDA_973],
        ["byzantine_empire"],
        1,
        ["wave8_muslim_forces_bbaw_amida"],
        ["wave8_muslim_forces_bbaw_amida"],
        "Hibatallah's Hamdanid relief army defeated the Byzantine force and captured Melias near Amida; it is not merged with Sayf al-Dawla's Aleppo force.",
        reviewed_date="3 July 973",
        reviewed_sides=["Hamdanid Mosul relief force under Hibatallah", "Byzantine army under Melias"],
        reviewed_outcome="Hamdanid relief victory and capture of Melias",
        event_boundary="The field action outside Amida, not a conquest of the city.",
    ),
    "hced-Antioch, Syria969-1": _contract(
        "hced-Antioch, Syria969-1",
        "byzantine_arab_wars",
        ["byzantine_empire"],
        [_ANTIOCH_969],
        1,
        ["wave8_muslim_forces_sorbonne_antioch"],
        ["wave8_muslim_forces_sorbonne_antioch"],
        "Michael Bourtzes and Peter Phokas captured Antioch from Az-Zughayli's garrison; this is distinct from Aleppo's negotiated protectorate transition in the same year.",
        reviewed_date="28 October 969",
        reviewed_sides=["Byzantine forces under Michael Bourtzes and Peter Phokas", "Az-Zughayli's Antioch garrison"],
        reviewed_outcome="Byzantine capture of Antioch",
        event_boundary="The assault and capture of Antioch, not the later regional settlement.",
    ),
    "hced-Beirut1110-1": _contract(
        "hced-Beirut1110-1",
        "crusades",
        [_BALDWIN_BEIRUT, _BERTRAND_BEIRUT, _GENOESE_BEIRUT, _PISAN_BEIRUT],
        [_BEIRUT_GARRISON, _BEIRUT_RELIEF],
        1,
        ["wave8_muslim_forces_cambridge_siege_tactics", "wave8_muslim_forces_routledge_baldwin"],
        ["wave8_muslim_forces_cambridge_siege_tactics", "wave8_muslim_forces_routledge_baldwin"],
        "Baldwin's and Bertrand's forces, supported by the Genoese and Pisan blockade, captured Fatimid Beirut after defeating the garrison's resistance and failed naval relief.",
        reviewed_date="February–13 May 1110",
        reviewed_sides=["Baldwin I's Jerusalem force", "Bertrand of Tripoli's force", "Genoese blockade fleet", "Pisan blockade fleet", "Fatimid Beirut garrison", "Fatimid relief ships from Tyre and Sidon"],
        reviewed_outcome="Capture of Beirut by the land-and-sea besieging side",
        event_boundary="The Beirut siege and blockade through 13 May; Sidon's later 1110 siege is excluded.",
    ),
    "hced-Bosra634-1": _contract(
        "hced-Bosra634-1",
        "early_caliphal_armies",
        ["rashidun_caliphate"],
        ["byzantine_empire"],
        1,
        ["wave8_muslim_forces_donner_early_conquests"],
        ["wave8_muslim_forces_donner_early_conquests"],
        "Bostra's Byzantine defenders capitulated to the Rashidun field force after a siege; no later Syrian conquest is folded into the result.",
        reviewed_date="late May 634",
        reviewed_sides=["Rashidun field army", "Byzantine Bostra garrison"],
        reviewed_outcome="Capitulation of Bostra to the Rashidun force",
        event_boundary="The siege and local capitulation of Bostra only.",
    ),
    "hced-Bridge634-1": _contract(
        "hced-Bridge634-1",
        "early_caliphal_armies",
        ["sasanian_empire"],
        ["rashidun_caliphate"],
        1,
        ["wave8_muslim_forces_donner_early_conquests", "wave8_muslim_forces_iranica_arab_conquest"],
        ["wave8_muslim_forces_donner_early_conquests", "wave8_muslim_forces_iranica_arab_conquest"],
        "The Sasanian army defeated Abu Ubayd's Rashidun force at the Euphrates crossing; the approximate HCED point is withheld.",
        reviewed_date="October 634",
        reviewed_sides=["Sasanian army under Bahman Jadhuyih", "Rashidun army under Abu Ubayd"],
        reviewed_outcome="Sasanian victory and destruction of much of Abu Ubayd's force",
        event_boundary="The Battle of the Bridge, not neighboring Iraq campaign actions.",
    ),
    "hced-Buzakha632-1": _contract(
        "hced-Buzakha632-1",
        "early_caliphal_armies",
        ["rashidun_caliphate"],
        [_BUZAKHA],
        1,
        ["wave8_muslim_forces_cambridge_buzakha", "wave8_muslim_forces_tabari_volume_10"],
        ["wave8_muslim_forces_cambridge_buzakha", "wave8_muslim_forces_tabari_volume_10"],
        "Khalid's Rashidun army defeated Tulayha's source-attested Asad–Ghatafan force; HCED's single-tribe loser is not accepted as the complete opposing side.",
        reviewed_date="632",
        reviewed_sides=["Rashidun army under Khalid ibn al-Walid", "Tulayha's Asad and Ghatafan force"],
        reviewed_outcome="Rashidun battlefield victory and flight of Tulayha",
        event_boundary="The Buzakha engagement, not the entire Ridda campaign.",
        war_type="state_formation_conflict",
    ),
    "hced-Castrogiovanni859-1": _contract(
        "hced-Castrogiovanni859-1",
        "sicily",
        [_ENNA_859],
        ["byzantine_empire"],
        1,
        ["wave8_muslim_forces_metcalfe_sicily", "wave8_muslim_forces_unesco_enna"],
        ["wave8_muslim_forces_metcalfe_sicily", "wave8_muslim_forces_unesco_enna"],
        "Al-Abbas ibn al-Fadl's Aghlabid Sicilian force captured Enna from its Byzantine defenders; the actor is not a generic Sicilian or Muslim line.",
        reviewed_date="24 January 859",
        reviewed_sides=["Aghlabid Sicilian force under al-Abbas ibn al-Fadl", "Byzantine defenders of Enna"],
        reviewed_outcome="Aghlabid capture of Enna",
        event_boundary="The capture of Enna, then called Castrogiovanni, not the wider conquest of Sicily.",
    ),
    "hced-Cerami1063-1": _contract(
        "hced-Cerami1063-1",
        "sicily",
        [_ROGER_CERAMI],
        [_AFRICAN_CERAMI, _SICILIAN_CERAMI],
        1,
        ["wave8_muslim_forces_malaterra_cerami", "wave8_muslim_forces_metcalfe_sicily"],
        ["wave8_muslim_forces_malaterra_cerami"],
        "Malaterra distinguishes Roger's Norman force from both African reinforcements and the Sicilian force; all three are retained as event-bounded actors.",
        reviewed_date="1063",
        reviewed_sides=["Roger I's Norman force", "African reinforcement contingent", "Sicilian defending force"],
        reviewed_outcome="Roger's force defeated the combined opposing contingents",
        event_boundary="The field battle near Cerami, not the subsequent conquest of the town or island.",
    ),
    "hced-Ceuta1415-1": _contract(
        "hced-Ceuta1415-1",
        "ceuta",
        ["kingdom_portugal"],
        [_CEUTA_1415],
        1,
        ["wave8_muslim_forces_cambridge_ceuta", "wave8_muslim_forces_cham_ceuta_sources"],
        ["wave8_muslim_forces_cambridge_ceuta", "wave8_muslim_forces_cham_ceuta_sources"],
        "The Kingdom of Portugal captured Ceuta from Salah ben Salah's urban and locally summoned defenders; no Marinid-wide or timeless North African opponent is invented.",
        reviewed_date="21 August 1415",
        reviewed_sides=["Kingdom of Portugal assault force", "Salah ben Salah's Ceuta garrison and locally summoned defenders"],
        reviewed_outcome="Portuguese capture of Ceuta",
        event_boundary="The assault and capture of Ceuta on 21 August, not the later occupation campaign.",
    ),
    "hced-Ecija711-1": _contract(
        "hced-Ecija711-1",
        "iberia",
        [_TARIQ_711],
        [_ECIJA_711],
        1,
        ["wave8_muslim_forces_barcelona_iberia_711", "wave8_muslim_forces_cambridge_visigothic_conquest"],
        ["wave8_muslim_forces_barcelona_iberia_711"],
        "After the battle traditionally called Guadalete, Tariq's 711 invasion army defeated Écija's local defenders and Visigothic survivors in a distinct hard-fought action.",
        reviewed_date="later in 711, after the battle traditionally called Guadalete",
        reviewed_sides=["Tariq ibn Ziyad's 711 invasion army", "Écija defenders and Visigothic survivors"],
        reviewed_outcome="Victory of Tariq's army near Écija",
        event_boundary="The distinct post-Guadalete battle near Écija, not the city's later administrative submission.",
    ),
    "hced-Guadalete711-1": _contract(
        "hced-Guadalete711-1",
        "iberia",
        [_TARIQ_711],
        [_RODERIC_711],
        1,
        ["wave8_muslim_forces_barcelona_iberia_711", "wave8_muslim_forces_cambridge_visigothic_conquest"],
        ["wave8_muslim_forces_barcelona_iberia_711", "wave8_muslim_forces_cambridge_visigothic_conquest"],
        "Tariq's invasion army defeated Roderic's royal army in summer 711. The traditional Guadalete name is retained, but the disputed battlefield point is withheld.",
        reviewed_date="summer 711",
        reviewed_sides=["Tariq ibn Ziyad's 711 invasion army", "Roderic's Visigothic royal army"],
        reviewed_outcome="Defeat of Roderic's royal army",
        event_boundary="The decisive summer 711 battle; no precise modern battlefield is asserted.",
    ),
    "hced-Harenc1098-1": _contract(
        "hced-Harenc1098-1",
        "crusades",
        [_BOHEMOND_1098],
        [_RIDWAN_1098],
        1,
        ["wave8_muslim_forces_gesta_harenc"],
        ["wave8_muslim_forces_gesta_harenc"],
        "The contaminated participant string is discarded. Gesta Francorum binds the row to Bohemond's 9 February victory over Ridwan's relief army near the Lake of Antioch and Harim.",
        reviewed_date="9 February 1098",
        reviewed_sides=["Bohemond's crusader cavalry sortie", "Ridwan of Aleppo's relief army"],
        reviewed_outcome="Crusader cavalry victory and flight of Ridwan's army",
        event_boundary="The February Lake of Antioch action, distinct from the 28 June battle against Kerbogha recorded as Orontes.",
    ),
}


def _nonpromotion(
    candidate_id: str,
    disposition: str,
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    *,
    reviewed_actors: Iterable[str],
    reviewed_event: str,
    reviewed_date: str,
    reviewed_outcome: str,
) -> dict[str, Any]:
    row_hash, name, year = _ROW_DATA[candidate_id]
    return {
        "raw_row_sha256": row_hash,
        "canonical_event": _canonical(name, year),
        "disposition": disposition,
        "terminal_exclusion": disposition == "terminal_exclusion",
        "hold_category": category,
        "hold_reason": reason,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "reviewed_actor_description": list(map(str, reviewed_actors)),
        "reviewed_granularity": "exact_row_assertion",
        "historical_event": {
            "name": reviewed_event,
            "reviewed_date": reviewed_date,
            "reviewed_outcome": reviewed_outcome,
        },
        "full_row_audited": True,
    }


WAVE8_MUSLIM_FORCES_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Aleppo639-1": _nonpromotion(
        "hced-Aleppo639-1",
        "hold",
        "chronology_and_event_sequence_unresolved",
        "The early conquest traditions disagree on the command, sequence, and date of Aleppo's submission; the reviewed evidence cannot bind the locked 639 row to one tactical engagement without invention.",
        ["wave8_muslim_forces_donner_early_conquests"],
        reviewed_actors=["Rashidun conquest forces", "Byzantine or local Aleppo defenders"],
        reviewed_event="Early Rashidun acquisition of Aleppo",
        reviewed_date="chronology disputed; not securely 639",
        reviewed_outcome="Regional submission is attested, but an exact 639 engagement result is not",
    ),
    "hced-Amorium669-1": _nonpromotion(
        "hced-Amorium669-1",
        "hold",
        "recovery_date_unresolved",
        "The evidence supports Arab occupation of Amorium in 669 and a later Byzantine recovery, but does not securely date a Byzantine victory to 669. Unknown timing is not converted into a win or draw.",
        ["wave8_muslim_forces_birmingham_amorium", "wave8_muslim_forces_konstanz_amorium"],
        reviewed_actors=["Umayyad campaign force", "Byzantine defenders or recovery force"],
        reviewed_event="Occupation and later recovery of Amorium",
        reviewed_date="Arab occupation in 669; Byzantine recovery date unresolved",
        reviewed_outcome="Later Byzantine recovery is known, but the locked row's exact outcome/date pairing is not",
    ),
    "hced-Babylon, Iraq634-1": _nonpromotion(
        "hced-Babylon, Iraq634-1",
        "hold",
        "single_tradition_event_binding",
        "Only one conquest tradition places al-Muthanna's victory at Babil, and the early chronology may duplicate or displace another Iraq action. The exact row is held rather than manufacturing certainty.",
        ["wave8_muslim_forces_donner_early_conquests", "wave8_muslim_forces_iranica_arab_conquest"],
        reviewed_actors=["Rashidun force under al-Muthanna", "Sasanian force reported at Babil"],
        reviewed_event="Reported action at Babil in Iraq",
        reviewed_date="reported in the 634 campaign chronology",
        reviewed_outcome="A Rashidun victory is reported in one tradition but is not independently secured",
    ),
    "hced-Buwayb635-1": _nonpromotion(
        "hced-Buwayb635-1",
        "hold",
        "historicity_and_granularity_disputed",
        "Iranica repeats the conventional Muslim victory, while Donner concludes that the grand battle account may synthesize smaller actions and may not describe one battle at all. The conflict is retained as an audited hold.",
        ["wave8_muslim_forces_donner_early_conquests", "wave8_muslim_forces_iranica_arab_conquest"],
        reviewed_actors=["Rashidun forces in lower Iraq", "Sasanian forces associated with Mihran"],
        reviewed_event="Traditions grouped as the Battle of Buwayb",
        reviewed_date="conventionally 635; exact constituent actions unresolved",
        reviewed_outcome="Conventional Rashidun victory account is not secure at exact-event granularity",
    ),
}


WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Aleppo969-1": _nonpromotion(
        "hced-Aleppo969-1",
        "terminal_exclusion",
        "negotiated_transition_not_binary_engagement",
        "Aleppo's 969–970 transition involved an internal Hamdanid struggle, a request for Byzantine intervention, and a negotiated protectorate. The locked binary Byzantine-versus-Muslims win is not one ratable engagement.",
        ["wave8_muslim_forces_cnrs_aleppo", "wave8_muslim_forces_sorbonne_antioch"],
        reviewed_actors=["Qarghuya and Bakjur in Aleppo", "Sa'd al-Dawla's rival force", "Byzantine authorities"],
        reviewed_event="Aleppo's negotiated Byzantine protectorate transition",
        reviewed_date="December 969–January 970",
        reviewed_outcome="Negotiated settlement following intra-Hamdanid conflict, not a binary Byzantine battlefield victory",
    ),
    "hced-Alexandria641-642-1": _nonpromotion(
        "hced-Alexandria641-642-1",
        "terminal_exclusion",
        "locked_interval_truncates_treaty_execution",
        "The locked queue interval is 641–641 although the source record and reviewed event run through the Byzantine evacuation in 642. Exact promotion would silently truncate the event boundary.",
        ["wave8_muslim_forces_cambridge_byzantine_egypt", "wave8_muslim_forces_cambridge_egypt_641_868"],
        reviewed_actors=["Rashidun army under Amr ibn al-As", "Byzantine authorities and garrison at Alexandria"],
        reviewed_event="First siege, treaty, and evacuation of Alexandria",
        reviewed_date="treaty in November 641; evacuation completed in September 642",
        reviewed_outcome="Negotiated evacuation and Rashidun occupation after the locked interval",
    ),
    "hced-Alexandria645-1": _nonpromotion(
        "hced-Alexandria645-1",
        "terminal_exclusion",
        "winner_and_conquest_phase_mismatch",
        "A Byzantine expedition under Manuel retook Alexandria in 645; the final Rashidun recovery belongs to 646. Reversing the winner or shifting the date would create a different event.",
        ["wave8_muslim_forces_cambridge_byzantine_egypt", "wave8_muslim_forces_cambridge_egypt_641_868"],
        reviewed_actors=["Byzantine expedition under Manuel", "Rashidun garrison or recovery force"],
        reviewed_event="Byzantine recapture and later Rashidun recovery of Alexandria",
        reviewed_date="Byzantine recapture in 645; Rashidun recovery in 646",
        reviewed_outcome="The locked 645 Rashidun win is the wrong phase and orientation",
    ),
    "hced-Arqa1098-1": _nonpromotion(
        "hced-Arqa1098-1",
        "terminal_exclusion",
        "event_year_mismatch",
        "The First Crusade siege of Arqa occurred in 1099 and ended without a crusader capture. The locked 1098 Muslim win cannot be repaired without changing the event and year.",
        ["wave8_muslim_forces_cambridge_arqa"],
        reviewed_actors=["Raymond of Saint-Gilles's crusader siege force", "Defenders of Arqa"],
        reviewed_event="Unsuccessful First Crusade siege of Arqa",
        reviewed_date="14 February–13 May 1099",
        reviewed_outcome="The crusaders abandoned the siege; no 1098 engagement matching the row was established",
    ),
    "hced-Babylon, Egypt640-1": _nonpromotion(
        "hced-Babylon, Egypt640-1",
        "terminal_exclusion",
        "locked_interval_truncates_siege",
        "The siege of Babylon fortress began in 640 but its surrender belongs to 641. A one-year 640 Rashidun win would attach the outcome before it occurred and violate exact event granularity.",
        ["wave8_muslim_forces_cambridge_byzantine_egypt", "wave8_muslim_forces_cambridge_egypt_641_868"],
        reviewed_actors=["Rashidun army under Amr ibn al-As", "Byzantine Babylon fortress garrison"],
        reviewed_event="Siege and surrender of Babylon fortress in Egypt",
        reviewed_date="siege in 640–641; surrender at Easter 641",
        reviewed_outcome="Rashidun acquisition followed a 641 surrender outside the locked interval",
    ),
}

# Compatibility aliases for consumers that use the shorter exclusion names.
WAVE8_MUSLIM_FORCES_EXCLUSIONS = WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS
WAVE8_MUSLIM_FORCES_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_MUSLIM_FORCES_HOLDS,
    **WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS,
}

WAVE8_MUSLIM_FORCES_CONTRACT_IDS = frozenset(WAVE8_MUSLIM_FORCES_CONTRACTS)
WAVE8_MUSLIM_FORCES_HOLD_IDS = frozenset(WAVE8_MUSLIM_FORCES_HOLDS)
WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS
)
WAVE8_MUSLIM_FORCES_EXCLUSION_IDS = WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSION_IDS
WAVE8_MUSLIM_FORCES_RESERVED_IDS = (
    WAVE8_MUSLIM_FORCES_CONTRACT_IDS
    | WAVE8_MUSLIM_FORCES_HOLD_IDS
    | WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSION_IDS
)
WAVE8_MUSLIM_FORCES_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_DATA)


# These source points encode a disputed battlefield, an approximate crossing,
# or (for Harenc) Aleppo rather than the reviewed engagement.  Harenc's modern
# country is likewise not asserted because the Lake of Antioch site straddles
# a modern frontier question that the source row does not resolve.
WAVE8_MUSLIM_FORCES_POINT_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Bridge634-1", "hced-Guadalete711-1", "hced-Harenc1098-1"}
)
WAVE8_MUSLIM_FORCES_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Harenc1098-1"}
)
WAVE8_MUSLIM_FORCES_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_MUSLIM_FORCES_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_MUSLIM_FORCES_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_MUSLIM_FORCES_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "aleppo_antioch_969": {
        "candidate_ids": ["hced-Aleppo969-1", "hced-Antioch, Syria969-1"],
        "disposition": "distinct_events",
        "reason": "Aleppo's negotiated protectorate transition and Antioch's armed capture are separate 969 events in different cities.",
    },
    "alexandria_phases_641_645": {
        "candidate_ids": ["hced-Alexandria641-642-1", "hced-Alexandria645-1"],
        "disposition": "distinct_conquest_phases",
        "reason": "The first treaty/evacuation and the later Byzantine recapture belong to separate phases and neither is emitted from its malformed locked row.",
    },
    "guadalete_ecija_711": {
        "candidate_ids": ["hced-Guadalete711-1", "hced-Ecija711-1"],
        "disposition": "distinct_engagements_same_campaign",
        "reason": "The Écija action followed the battle traditionally called Guadalete and is not a duplicate rating of Roderic's defeat.",
    },
    "harenc_orontes_1098": {
        "candidate_ids": ["hced-Harenc1098-1", "hced-Orontes1098-1"],
        "disposition": "distinct_engagements_same_campaign",
        "reason": "Harenc is the 9 February action against Ridwan; Orontes represents the later 28 June action against Kerbogha.",
    },
}

# IWBD begins in the modern period and contains no possible twin of this cohort.
WAVE8_MUSLIM_FORCES_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_MUSLIM_FORCES_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_MUSLIM_FORCES_OUTCOME_OVERRIDE_METADATA = (
    WAVE8_MUSLIM_FORCES_OUTCOME_OVERRIDES
)


_FUNNEL_SCOPE: dict[str, tuple[tuple[str, ...], bool, str | None, tuple[str, ...]]] = {
    "hced-Aleppo1260-1": (("muslims",), False, None, ("other_identity_blocker:faction_label_not_a_polity",)),
    "hced-Aleppo639-1": (("muslims",), True, "muslims", ()),
    "hced-Aleppo962-1": (("muslims",), True, "muslims", ()),
    "hced-Aleppo969-1": (("muslims",), True, "muslims", ()),
    "hced-Alexandria641-642-1": (("muslims",), True, "muslims", ()),
    "hced-Alexandria645-1": (("muslims",), True, "muslims", ()),
    "hced-Amida973-1": (("muslims",), True, "muslims", ()),
    "hced-Amorium669-1": (("muslims",), True, "muslims", ()),
    "hced-Antioch, Syria969-1": (("muslims",), True, "muslims", ()),
    "hced-Arqa1098-1": (("muslims",), False, None, ("other_identity_blocker:faction_label_not_a_polity",)),
    "hced-Babylon, Egypt640-1": (("muslims",), True, "muslims", ()),
    "hced-Babylon, Iraq634-1": (("muslims",), True, "muslims", ()),
    "hced-Beirut1110-1": (("kingdom of jerusalem crusaders", "muslims"), True, None, ()),
    "hced-Bosra634-1": (("muslims",), True, "muslims", ()),
    "hced-Bridge634-1": (("muslims", "sassanians"), True, None, ()),
    "hced-Buwayb635-1": (("muslims", "sassanids"), True, None, ()),
    "hced-Buzakha632-1": (("beni asad tribe", "muslims"), True, None, ()),
    "hced-Castrogiovanni859-1": (("muslims",), True, "muslims", ()),
    "hced-Cerami1063-1": (("muslims",), False, None, ("other_identity_blocker:faction_label_not_a_polity",)),
    "hced-Ceuta1415-1": (("muslims",), True, "muslims", ()),
    "hced-Ecija711-1": (("muslims", "visigothic spain"), True, None, ()),
    "hced-Guadalete711-1": (("muslims",), False, None, ("other_identity_blocker:faction_label_not_a_polity",)),
    "hced-Harenc1098-1": (("muslims",), False, None, ("other_identity_blocker:faction_label_not_a_polity",)),
}


def _integration_dispositions() -> dict[str, dict[str, Any]]:
    duplicate_by_candidate: dict[str, list[str]] = {}
    for duplicate_id, disposition in WAVE8_MUSLIM_FORCES_DUPLICATE_DISPOSITIONS.items():
        for candidate_id in disposition["candidate_ids"]:
            if candidate_id in _ROW_DATA:
                duplicate_by_candidate.setdefault(candidate_id, []).append(duplicate_id)
    result: dict[str, dict[str, Any]] = {}
    for candidate_id, (labels, eligible, sole, other) in _FUNNEL_SCOPE.items():
        if candidate_id in WAVE8_MUSLIM_FORCES_CONTRACTS:
            disposition = "PROMOTE"
            all_actors = True
        elif candidate_id in WAVE8_MUSLIM_FORCES_HOLDS:
            disposition = "HOLD"
            all_actors = False
        else:
            disposition = "EXCLUDE"
            all_actors = False
        result[candidate_id] = {
            "disposition": disposition,
            "full_row_audited": True,
            "blocker_labels": list(labels),
            "greedy_eligible": eligible,
            "sole_blocker_label": sole,
            "other_blockers": list(other),
            "all_opposing_actors_resolved": all_actors,
            "duplicate_review_ids": sorted(duplicate_by_candidate.get(candidate_id, [])),
            "release_duplicate_scan": "no_existing_release_event_twin_found",
        }
    return result


WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS = _integration_dispositions()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_MUSLIM_FORCES_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_MUSLIM_FORCES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "duplicate_dispositions": WAVE8_MUSLIM_FORCES_DUPLICATE_DISPOSITIONS,
        "entities": WAVE8_MUSLIM_FORCES_ENTITIES,
        "holds": WAVE8_MUSLIM_FORCES_HOLDS,
        "integration_dispositions": WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_MUSLIM_FORCES_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "outcome_overrides": WAVE8_MUSLIM_FORCES_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_MUSLIM_FORCES_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_MUSLIM_FORCES_SOURCES,
        "terminal_exclusions": WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS,
    }


def wave8_muslim_forces_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_MUSLIM_FORCES_CONTRACTS),
        len(WAVE8_MUSLIM_FORCES_HOLDS),
        len(WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS),
    ) != (14, 4, 5):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (
        len(WAVE8_MUSLIM_FORCES_ENTITIES),
        len(WAVE8_MUSLIM_FORCES_SOURCES),
    ) != (24, 25):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_MUSLIM_FORCES_RESERVED_IDS != WAVE8_MUSLIM_FORCES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservations are incomplete")
    dispositions = (
        WAVE8_MUSLIM_FORCES_CONTRACT_IDS,
        WAVE8_MUSLIM_FORCES_HOLD_IDS,
        WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(3)
        for j in range(i + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if wave8_muslim_forces_audit_signature() != WAVE8_MUSLIM_FORCES_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    if len(_SOURCE_BY_ID) != 25:
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_MUSLIM_FORCES_SOURCES:
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_MUSLIM_FORCES_ENTITIES
    }
    if len(entity_by_id) != 24:
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_exact = {"muslim", "muslims", "islam", "islamic forces"}
    for entity in WAVE8_MUSLIM_FORCES_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity is not event/campaign bounded")
        if str(entity["name"]).strip().casefold() in forbidden_exact:
            raise ValueError(f"{_LANE_NAME} installed a timeless religious identity")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} identity provenance is not canonical")
        if not set(map(str, entity["source_ids"])) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} identity names an unknown source")

    used_new_entities: set[str] = set()
    for candidate_id, contract in WAVE8_MUSLIM_FORCES_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_DATA[candidate_id][0]:
            raise ValueError(f"{_LANE_NAME} promotion hash drifted")
        if (
            contract["result_type"] != "win"
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or contract["actor_override"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} outcome/actor policy drifted")
        if not contract["side_1_entity_ids"] or not contract["side_2_entity_ids"]:
            raise ValueError(f"{_LANE_NAME} promotion has an empty side")
        evidence = list(map(str, contract["evidence_refs"]))
        outcome_sources = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcome_sources):
            raise ValueError(f"{_LANE_NAME} contract provenance is not canonical")
        if not outcome_sources or not set(outcome_sources) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} contract lacks direct outcome sources")
        if not set(evidence) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} contract names an unknown source")
        for source_id in outcome_sources:
            if "outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"]:
                raise ValueError(f"{_LANE_NAME} outcome source lacks outcome role")
        expected_families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcome_sources
            }
        )
        if contract["outcome_source_family_ids"] != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        provenance = contract["direct_provenance"]
        if not all(
            provenance.get(field)
            for field in (
                "reviewed_date",
                "reviewed_sides",
                "reviewed_outcome",
                "event_boundary",
            )
        ):
            raise ValueError(f"{_LANE_NAME} contract lacks direct provenance")
        for entity_id in (
            *map(str, contract["side_1_entity_ids"]),
            *map(str, contract["side_2_entity_ids"]),
        ):
            if entity_id in entity_by_id:
                used_new_entities.add(entity_id)
            if entity_id.casefold() in forbidden_exact:
                raise ValueError(f"{_LANE_NAME} uses a generic religious actor")
    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} has an unused bounded identity")

    for candidate_id, item in WAVE8_MUSLIM_FORCES_NONPROMOTIONS.items():
        if item["raw_row_sha256"] != _ROW_DATA[candidate_id][0]:
            raise ValueError(f"{_LANE_NAME} nonpromotion hash drifted")
        if item["full_row_audited"] is not True:
            raise ValueError(f"{_LANE_NAME} reserved an unaudited hold")
        if not set(map(str, item["evidence_refs"])) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} nonpromotion names an unknown source")
    if any(item["disposition"] != "hold" for item in WAVE8_MUSLIM_FORCES_HOLDS.values()):
        raise ValueError(f"{_LANE_NAME} hold disposition drifted")
    if any(
        item["disposition"] != "terminal_exclusion"
        or item["terminal_exclusion"] is not True
        for item in WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS.values()
    ):
        raise ValueError(f"{_LANE_NAME} exclusion disposition drifted")

    if WAVE8_MUSLIM_FORCES_POINT_QUARANTINE_ADDITIONS != {
        "hced-Bridge634-1",
        "hced-Guadalete711-1",
        "hced-Harenc1098-1",
    }:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_MUSLIM_FORCES_COUNTRY_QUARANTINE_ADDITIONS != {
        "hced-Harenc1098-1"
    }:
        raise ValueError(f"{_LANE_NAME} country quarantine inventory changed")
    if not (
        WAVE8_MUSLIM_FORCES_POINT_QUARANTINE_ADDITIONS
        | WAVE8_MUSLIM_FORCES_COUNTRY_QUARANTINE_ADDITIONS
    ) <= WAVE8_MUSLIM_FORCES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} quarantines a nonpromotion")
    if WAVE8_MUSLIM_FORCES_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an impossible IWBD duplicate")
    if WAVE8_MUSLIM_FORCES_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} acquired an outcome override")
    if set(WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS) != set(_ROW_DATA):
        raise ValueError(f"{_LANE_NAME} integration inventory is incomplete")
    if sum(
        bool(item["greedy_eligible"])
        for item in WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS.values()
    ) != 18:
        raise ValueError(f"{_LANE_NAME} greedy eligibility count drifted")
    if sum(
        item["sole_blocker_label"] == "muslims"
        for item in WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS.values()
    ) != 13:
        raise ValueError(f"{_LANE_NAME} greedy marginal count drifted")
    for candidate_id, disposition in WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS.items():
        if disposition["full_row_audited"] is not True:
            raise ValueError(f"{_LANE_NAME} integration row was not fully audited")
        if disposition["disposition"] == "PROMOTE" and not disposition[
            "all_opposing_actors_resolved"
        ]:
            raise ValueError(f"{_LANE_NAME} promoted an unresolved opposing side")
        expected = (
            "PROMOTE"
            if candidate_id in WAVE8_MUSLIM_FORCES_CONTRACTS
            else "HOLD"
            if candidate_id in WAVE8_MUSLIM_FORCES_HOLDS
            else "EXCLUDE"
        )
        if disposition["disposition"] != expected:
            raise ValueError(f"{_LANE_NAME} integration disposition drifted")


def validate_wave8_muslim_forces_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_MUSLIM_FORCES_CONTRACTS,
        WAVE8_MUSLIM_FORCES_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_MUSLIM_FORCES_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS),
    }


def install_wave8_muslim_forces_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_MUSLIM_FORCES_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_muslim_forces_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_MUSLIM_FORCES_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_MUSLIM_FORCES_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_MUSLIM_FORCES_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_muslim_forces_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_muslim_forces_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_MUSLIM_FORCES_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_muslim_forces_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_MUSLIM_FORCES_CONTRACTS.values()
            ).items()
        )
    )


def wave8_muslim_forces_counts() -> dict[str, int]:
    return {
        "duplicate_dispositions": len(WAVE8_MUSLIM_FORCES_DUPLICATE_DISPOSITIONS),
        "greedy_eligible_rows": sum(
            bool(item["greedy_eligible"])
            for item in WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS.values()
        ),
        "greedy_marginal_rows": sum(
            item["sole_blocker_label"] == "muslims"
            for item in WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS.values()
        ),
        "holds": len(WAVE8_MUSLIM_FORCES_HOLDS),
        "integration_dispositions": len(
            WAVE8_MUSLIM_FORCES_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_MUSLIM_FORCES_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_MUSLIM_FORCES_ENTITIES),
        "new_sources": len(WAVE8_MUSLIM_FORCES_SOURCES),
        "newly_rated_events": len(WAVE8_MUSLIM_FORCES_CONTRACTS),
        "outcome_overrides": len(WAVE8_MUSLIM_FORCES_OUTCOME_OVERRIDES),
        "promotion_contracts": len(WAVE8_MUSLIM_FORCES_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_MUSLIM_FORCES_RESERVED_IDS),
        "terminal_exclusions": len(
            WAVE8_MUSLIM_FORCES_TERMINAL_EXCLUSIONS
        ),
        "touched_rows": len(WAVE8_MUSLIM_FORCES_RESERVED_IDS),
    }
