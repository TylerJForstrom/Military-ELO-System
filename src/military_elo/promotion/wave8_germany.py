"""Candidate-keyed Wave 8 audit for HCED's anachronistic ``Germany`` label.

The sixteen locked rows span East Francia, Ottonian and Salian royal forces,
Frederick Barbarossa's imperial contingents, a 1919 Baltic-German field
formation, and one Swedish-Russian siege mislabeled as Germany.  This lane
therefore never creates a generic Germany alias or bridges a rating across any
German regime.  Every accepted actor is an existing time-bounded polity or a
new event/campaign-bounded force.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_GERMANY_CONTRACTS",
    "WAVE8_GERMANY_CONTRACT_IDS",
    "WAVE8_GERMANY_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_GERMANY_CROSS_LANE_DISPOSITIONS",
    "WAVE8_GERMANY_ENTITIES",
    "WAVE8_GERMANY_EXCLUSIONS",
    "WAVE8_GERMANY_EXCLUSION_IDS",
    "WAVE8_GERMANY_EXPECTED_CANDIDATE_IDS",
    "WAVE8_GERMANY_FINAL_AUDIT_SIGNATURE",
    "WAVE8_GERMANY_HOLDS",
    "WAVE8_GERMANY_HOLD_IDS",
    "WAVE8_GERMANY_INTEGRATION_DISPOSITIONS",
    "WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_GERMANY_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_GERMANY_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_GERMANY_NONPROMOTIONS",
    "WAVE8_GERMANY_OUTCOME_OVERRIDE_METADATA",
    "WAVE8_GERMANY_OUTCOME_OVERRIDES",
    "WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_GERMANY_RESERVED_IDS",
    "WAVE8_GERMANY_SOURCES",
    "WAVE8_GERMANY_TERMINAL_EXCLUSIONS",
    "WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS",
    "install_wave8_germany_entities",
    "install_wave8_germany_sources",
    "promote_wave8_germany_contracts",
    "validate_wave8_germany_integration_dispositions",
    "validate_wave8_germany_queue_contracts",
    "wave8_germany_audit_signature",
    "wave8_germany_cohort_counts",
    "wave8_germany_counts",
    "wave8_germany_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Germany exact actor audit"
_EVENT_ID_PREFIX = "hced_wave8_germany_"
_MODULE_OWNER = "military_elo.promotion.wave8_germany"

_RUM_ID = "clio_tr_rum_sultanate_1094_835c76cf"
_HUNGARY_ID = "kingdom_hungary"
_SWEDEN_ID = "kingdom_sweden"
_TSARDOM_RUSSIA_ID = "clio_ru_moskva_rurik_dyn_1547_93deb0e2"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = True,
    crosscheck: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if crosscheck:
        roles.append("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_GERMANY_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_germany_treccani_cassano_1158",
        "Cassano d'Adda",
        (
            "https://www.treccani.it/enciclopedia/"
            "cassano-d-adda_%28Enciclopedia-Italiana%29/"
        ),
        "Istituto della Enciclopedia Italiana (Treccani)",
        "scholarly_encyclopedia",
        "treccani_cassano_adda",
    ),
    _source(
        "wave8_germany_ecomuseo_cassano_1158",
        "Cassano d'Adda, il castello",
        "https://www.ecomuseoaddadileonardo.it/cassano-castello/",
        "Ecomuseo Adda di Leonardo",
        "regional_heritage_history",
        "ecomuseo_adda_leonardo",
    ),
    _source(
        "wave8_germany_polish_land_forces_cedynia",
        "Military Land Forces: Medieval Times (Cedynia, 24 June 972)",
        "https://muzeumwl.pl/en/medieval-times/",
        "Muzeum Wojsk Lądowych (Polish Land Forces Museum)",
        "official_military_museum_history",
        "polish_land_forces_museum",
    ),
    _source(
        "wave8_germany_lingvaria_cedynia",
        "Gdzie walczył i jak miał na imię brat Mieszka I?",
        "https://journals.akademicka.pl/lv/article/view/2667",
        "LingVaria / Księgarnia Akademicka",
        "peer_reviewed_article",
        "lingvaria_cedynia_thietmar",
        crosscheck=True,
    ),
    _source(
        "wave8_germany_1914_1918_cesis",
        "Cēsis, Battle of",
        "https://encyclopedia.1914-1918-online.net/article/cesis-battle-of/",
        "1914-1918-online: International Encyclopedia of the First World War",
        "peer_reviewed_scholarly_encyclopedia",
        "international_encyclopedia_first_world_war",
    ),
    _source(
        "wave8_germany_latvia_estonia_cesis",
        "Battle of Cēsis (Võnnu lahing)",
        "https://militaryheritagetourism.info/en/military/topics/view/19",
        "Latvia-Estonia Military Heritage Programme",
        "public_military_heritage_history",
        "latvia_estonia_military_heritage",
        crosscheck=True,
    ),
    _source(
        "wave8_germany_st_andrews_stilo",
        "The Battle of Stilo, July 982",
        "https://arts.st-andrews.ac.uk/after-empire/2018/01/23/the-battle-of-stilo-july-982/",
        "University of St Andrews, After Empire project",
        "university_research_project",
        "st_andrews_after_empire",
    ),
    _source(
        "wave8_germany_transmed_thietmar_stilo",
        "982: Thietmar of Merseburg on the Battle at Capo Colonna",
        "https://ojs.ub.uni-konstanz.de/transmed/index.php/tmh/en/article/view/71",
        "Transmediterranean History / University of Konstanz",
        "peer_reviewed_primary_source_edition",
        "transmediterranean_history_thietmar",
    ),
    _source(
        "wave8_germany_st_andrews_dorylaeum",
        "Conrad III and the Second Crusade in the Byzantine Empire and Anatolia, 1147",
        "https://research-repository.st-andrews.ac.uk/handle/10023/524",
        "University of St Andrews research repository",
        "doctoral_thesis",
        "st_andrews_roche_second_crusade",
    ),
    _source(
        "wave8_germany_oxford_dorylaeum",
        "Social Unrest and the Failure of Conrad III's March Through Anatolia, 1147",
        "https://academic.oup.com/gh/article-abstract/28/2/125/558523",
        "German History / Oxford University Press",
        "peer_reviewed_article",
        "oxford_german_history_kostick",
        crosscheck=True,
    ),
    _source(
        "wave8_germany_bern_geul_dyle",
        "Carolingian battle evidence: the Geule and Dyle actions of 891",
        "https://bop.unibe.ch/apd/article/download/6866/9751/",
        "Acta Periodica Duellatorum / University of Bern",
        "peer_reviewed_article",
        "acta_periodica_duellatorum_carolingian_battles",
    ),
    _source(
        "wave8_germany_lvr_vikings_rhine",
        "Wikinger am Mittelrhein",
        (
            "https://www.rheinische-geschichte.lvr.de/Epochen-und-Themen/"
            "Themen/wikinger-am-mittelrhein/DE-2086/lido/57d11ffb5b1dd7.60977295"
        ),
        "Portal Rheinische Geschichte / Landschaftsverband Rheinland",
        "public_history_reference",
        "lvr_portal_rheinische_geschichte",
        crosscheck=True,
    ),
    _source(
        "wave8_germany_italian_culture_legnano",
        "Palio di Legnano - Rievocazioni Storiche",
        "https://rievocazionistoriche.cultura.gov.it/places/italy/lombardia/legnano/palio-di-legnano/",
        "Italian Ministry of Culture",
        "official_cultural_history",
        "italian_ministry_culture_legnano",
    ),
    _source(
        "wave8_germany_newadvent_frederick_i",
        "Frederick I (Barbarossa)",
        "https://www.newadvent.org/cathen/06252b.htm",
        "Catholic Encyclopedia (New Advent transcription)",
        "historical_encyclopedia",
        "catholic_encyclopedia_frederick_i",
        crosscheck=True,
    ),
    _source(
        "wave8_germany_oszk_pressburg_907",
        "1111 years ago: The Battle in Pressburg in 907",
        "https://vmek.oszk.hu/18400/18400/18400.pdf",
        "Hungarian Electronic Library, National Széchényi Library",
        "academic_military_history",
        "oszk_pressburg_907",
    ),
    _source(
        "wave8_germany_pressburg_academic_crosscheck",
        "The Battle of Pressburg and early Hungarian military history",
        "https://epa.oszk.hu/00600/00617/00052/pdf/EPA00617_tortenelmi_szemle_2007_01_001-017.pdf",
        "Történelmi Szemle",
        "peer_reviewed_article",
        "tortenelmi_szemle_pressburg",
        crosscheck=True,
    ),
    _source(
        "wave8_germany_psie_pole_source_study",
        "Czech involvement in King Henry V's expedition against Poland in 1109",
        "https://ejournals.eu/pliki_artykulu_czasopisma/pelny_tekst/677e21f4-6405-44f2-857c-05ef30c13370/pobierz",
        "Studia z Dziejów Średniowiecza / Jagiellonian University Press",
        "peer_reviewed_article",
        "studia_sredniowiecza_henry_v_poland",
    ),
    _source(
        "wave8_germany_wroclaw_psie_pole_legend",
        "Silesia and its past",
        "https://nowezycie.archidiecezja.wroc.pl/index.php/2019/12/03/silesia-and-its-past/",
        "Archdiocese of Wrocław, New Life",
        "regional_historical_review",
        "wroclaw_psie_pole_memory",
        crosscheck=True,
    ),
    _source(
        "wave8_germany_trinity_menfo_primary",
        "Herman of Reichenau, Chronicle 1044: Henry III and Hungary",
        "https://www.tcd.ie/history/assets/pdf/ug/ModuleHI1200handbook.pdf",
        "Trinity College Dublin, Department of History",
        "university_primary_source_translation",
        "trinity_herman_reichenau_1044",
    ),
    _source(
        "wave8_germany_indiana_riade_review",
        "Review of The Battle of Lechfeld and its antecedents",
        "https://scholarworks.iu.edu/journals/index.php/tmr/article/view/16527",
        "The Medieval Review / Indiana University",
        "academic_book_review",
        "medieval_review_riade",
    ),
    _source(
        "wave8_germany_cambridge_riade",
        "The Cambridge Medieval History: the battle at Riade",
        "https://en.wikisource.org/wiki/Page:Cambridge_Medieval_History_Volume_3.pdf/228",
        "Cambridge University Press (public-domain scan)",
        "academic_history_primary_scan",
        "cambridge_medieval_history_riade",
        crosscheck=True,
    ),
    _source(
        "wave8_germany_springer_riga_capitulation",
        "The Negotiations of the Riga Capitulation and the Adventus of 1710",
        "https://link.springer.com/chapter/10.1007/978-3-030-98527-1_7",
        "Palgrave Macmillan / Springer",
        "academic_book_chapter",
        "springer_riga_capitulation",
    ),
    _source(
        "wave8_germany_harvard_riga_1710",
        "Vignette 1: Siege of Riga 1710",
        "https://scalar.fas.harvard.edu/imperiia/vignette-1-siege-of-riga-1710",
        "Harvard University, Imperiia project",
        "university_digital_history",
        "harvard_imperiia_riga",
        crosscheck=True,
    ),
    _source(
        "wave8_germany_newadvent_crescentius",
        "Crescentius",
        "https://www.newadvent.org/cathen/04484c.htm",
        "Catholic Encyclopedia (New Advent transcription)",
        "historical_encyclopedia",
        "catholic_encyclopedia_crescentius",
    ),
    _source(
        "wave8_germany_leeds_crusade_1197",
        "The German Crusade of 1197-1198",
        "https://eprints.whiterose.ac.uk/id/eprint/82933/",
        "University of Leeds / White Rose Research Online",
        "peer_reviewed_article",
        "leeds_loud_german_crusade_1197",
    ),
    _source(
        "wave8_germany_deutsche_biographie_hoyer",
        "Hoyer I. von Mansfeld",
        "https://www.deutsche-biographie.de/sfz57862.html",
        "Deutsche Biographie / Bayerische Staatsbibliothek",
        "scholarly_national_biography",
        "deutsche_biographie_hoyer",
    ),
    _source(
        "wave8_germany_deutsche_biographie_siegfried",
        "Siegfried I, Pfalzgraf bei Rhein",
        "https://www.deutsche-biographie.de/downloadPDF?url=sfz121686.pdf",
        "Deutsche Biographie / Bayerische Staatsbibliothek",
        "scholarly_national_biography",
        "deutsche_biographie_siegfried",
        crosscheck=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
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
            f"{boundary_note} This identity is confined to {year}; no rating is "
            "inherited by a predecessor, successor, ethnic label, state namesake, "
            "or another field formation."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_GERMANY_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "mieszko_i_polans_field_army_cedynia_972",
        "Mieszko I's Polans field army at Cedynia (972)",
        "event_bounded_dynastic_field_army",
        972,
        "Central Europe",
        ["wave8_germany_lingvaria_cedynia", "wave8_germany_polish_land_forces_cedynia"],
        "The rated actor is Mieszko I's force attested at Cedynia, not every later polity called Poland.",
    ),
    _entity(
        "odo_lusatian_march_force_cedynia_972",
        "Margrave Odo's Lusatian march force at Cedynia (972)",
        "event_bounded_march_force",
        972,
        "Central Europe",
        ["wave8_germany_lingvaria_cedynia", "wave8_germany_polish_land_forces_cedynia"],
        "The rated actor is Odo's independently led march force, not an undifferentiated German or imperial state.",
    ),
    _entity(
        "estonian_latvian_cesis_field_coalition_1919",
        "Estonian 3rd Division and Northern Latvian Brigade at Cēsis (1919)",
        "event_bounded_independence_coalition",
        1919,
        "Northern Europe",
        ["wave8_germany_1914_1918_cesis", "wave8_germany_latvia_estonia_cesis"],
        "The rated actor is the joint Estonian-Latvian field coalition in the June Cēsis fighting.",
    ),
    _entity(
        "landeswehr_iron_division_cesis_force_1919",
        "Baltische Landeswehr and Iron Division at Cēsis (1919)",
        "event_bounded_baltic_german_formation",
        1919,
        "Northern Europe",
        ["wave8_germany_1914_1918_cesis", "wave8_germany_latvia_estonia_cesis"],
        "The rated actor is the Baltic-German Landeswehr/Iron Division formation, not Weimar Germany or a timeless German people.",
    ),
    _entity(
        "kalbid_sicilian_army_capo_colonna_982",
        "Abū al-Qāsim's Kalbid Sicilian army at Capo Colonna (982)",
        "event_bounded_emiral_field_army",
        982,
        "Southern Europe",
        ["wave8_germany_st_andrews_stilo", "wave8_germany_transmed_thietmar_stilo"],
        "The rated actor is the Kalbid field army that fought Otto II, without adding Byzantium to the victorious side.",
    ),
    _entity(
        "otto_ii_imperial_calabrian_army_982",
        "Otto II's imperial Calabrian army (982)",
        "event_bounded_imperial_field_army",
        982,
        "Southern Europe",
        ["wave8_germany_st_andrews_stilo", "wave8_germany_transmed_thietmar_stilo"],
        "The rated actor is Otto II's mixed imperial and Italo-Lombard expedition at Capo Colonna, not Germany across eras.",
    ),
    _entity(
        "conrad_iii_german_crusader_host_dorylaeum_1147",
        "Conrad III's German crusader host at Dorylaeum (1147)",
        "event_bounded_crusader_host",
        1147,
        "Anatolia",
        ["wave8_germany_oxford_dorylaeum", "wave8_germany_st_andrews_dorylaeum"],
        "The rated actor is Conrad III's Second Crusade host in Anatolia, not a German state or later crusader contingent.",
    ),
    _entity(
        "sunderold_east_frankish_force_geul_891",
        "Sunderold's East Frankish force at the Geul (891)",
        "event_bounded_royal_detachment",
        891,
        "Western Europe",
        ["wave8_germany_bern_geul_dyle"],
        "The rated actor is the East Frankish detachment defeated at the Geul before Arnulf's later royal counterstroke.",
    ),
    _entity(
        "arnulf_east_frankish_royal_army_dyle_891",
        "Arnulf's East Frankish royal army at the Dyle (891)",
        "event_bounded_royal_field_army",
        891,
        "Western Europe",
        ["wave8_germany_bern_geul_dyle", "wave8_germany_lvr_vikings_rhine"],
        "The rated actor is Arnulf's royal army at Leuven/Dyle, distinct from the force defeated at the Geul.",
    ),
    _entity(
        "viking_lotharingian_campaign_army_891",
        "Viking army in the Lotharingian campaign (891)",
        "campaign_bounded_raiding_army",
        891,
        "Western Europe",
        ["wave8_germany_bern_geul_dyle", "wave8_germany_lvr_vikings_rhine"],
        "The rated actor is the 891 campaigning army attested at the Geul and Dyle, not a timeless Danish or Viking identity.",
    ),
    _entity(
        "lombard_league_field_army_legnano_1176",
        "Lombard League field army at Legnano (1176)",
        "event_bounded_urban_league_army",
        1176,
        "Southern Europe",
        ["wave8_germany_italian_culture_legnano", "wave8_germany_newadvent_frederick_i"],
        "The rated actor is the allied northern Italian communal field army at Legnano.",
    ),
    _entity(
        "frederick_i_imperial_field_army_legnano_1176",
        "Frederick I's imperial field army at Legnano (1176)",
        "event_bounded_imperial_field_army",
        1176,
        "Southern Europe",
        ["wave8_germany_italian_culture_legnano", "wave8_germany_newadvent_frederick_i"],
        "The rated actor is Barbarossa's Legnano army, not every Holy Roman or German polity.",
    ),
    _entity(
        "liutpold_bavarian_east_frankish_army_pressburg_907",
        "Liutpold's Bavarian-East Frankish army at Pressburg (907)",
        "event_bounded_ducal_royal_army",
        907,
        "Central Europe",
        ["wave8_germany_oszk_pressburg_907", "wave8_germany_pressburg_academic_crosscheck"],
        "The rated actor is the predominantly Bavarian East Frankish expedition led by Liutpold.",
    ),
    _entity(
        "magyar_conquest_army_pressburg_907",
        "Magyar conquest-period army at Pressburg (907)",
        "event_bounded_steppe_field_army",
        907,
        "Central Europe",
        ["wave8_germany_oszk_pressburg_907", "wave8_germany_pressburg_academic_crosscheck"],
        "The rated actor is the conquest-period Magyar army at Pressburg, not a timeless ethnic label.",
    ),
    _entity(
        "henry_iii_imperial_army_menfo_1044",
        "Henry III's imperial army at Ménfő (1044)",
        "event_bounded_imperial_field_army",
        1044,
        "Central Europe",
        ["wave8_germany_trinity_menfo_primary"],
        "The rated actor is Henry III's 1044 intervention force, not a generic Germany identity.",
    ),
    _entity(
        "henry_i_east_frankish_royal_army_riade_933",
        "Henry I's East Frankish royal army at Riade (933)",
        "event_bounded_royal_field_army",
        933,
        "Central Europe",
        ["wave8_germany_cambridge_riade", "wave8_germany_indiana_riade_review"],
        "The rated actor is Henry I's assembled royal field army at Riade, not a later German empire.",
    ),
    _entity(
        "magyar_raiding_army_riade_933",
        "Magyar raiding army at Riade (933)",
        "event_bounded_raiding_army",
        933,
        "Central Europe",
        ["wave8_germany_cambridge_riade", "wave8_germany_indiana_riade_review"],
        "The rated actor is the particular Magyar raiding army defeated at Riade.",
    ),
    _entity(
        "otto_iii_imperial_roman_expedition_998",
        "Otto III's imperial Roman expedition (998)",
        "event_bounded_imperial_expedition",
        998,
        "Southern Europe",
        ["wave8_germany_newadvent_crescentius"],
        "The rated actor is Otto III's force restoring Gregory V in Rome and besieging Castel Sant'Angelo.",
    ),
    _entity(
        "crescentius_castel_santangelo_defenders_998",
        "Crescentius II's Castel Sant'Angelo defenders (998)",
        "event_bounded_urban_fortress_force",
        998,
        "Southern Europe",
        ["wave8_germany_newadvent_crescentius"],
        "The rated actor is Crescentius II's fortress party; the already-fled antipope John XVI is not merged into it.",
    ),
    _entity(
        "hoyer_imperial_loyalist_force_warnstedt_1113",
        "Hoyer of Mansfeld's imperial loyalist force at Warnstedt (1113)",
        "event_bounded_imperial_loyalist_force",
        1113,
        "Central Europe",
        ["wave8_germany_deutsche_biographie_hoyer", "wave8_germany_deutsche_biographie_siegfried"],
        "The rated actor is Hoyer's loyalist force acting for Henry V, not an all-regime Germany identity.",
    ),
    _entity(
        "saxon_princely_opposition_warnstedt_1113",
        "Saxon princely opposition at Warnstedt (1113)",
        "event_bounded_princely_coalition",
        1113,
        "Central Europe",
        ["wave8_germany_deutsche_biographie_hoyer", "wave8_germany_deutsche_biographie_siegfried"],
        "The rated actor is the meeting force around Siegfried, Wiprecht, and their Saxon-Thuringian allies.",
    ),
)


_ROW_HASHES: dict[str, str] = {
    "hced-Cassano1158-1": "6dffa003740e174c3ab83a37cf7788c99ee02b453cf4679d1e995f8740b98123",
    "hced-Cedynia972-1": "7f2cdaa193a71937d493a48a0312267077ebb2e2d10803c382cba84ff048c0df",
    "hced-Cesis1919-1": "5c46929071e0917eedee58d741b065c2f91a9d3e75455ed078c37d2707a83300",
    "hced-Cotrone982-1": "b24f37a40d430c5f57a0c2617a6717cac4ee327d0d3771a89fb0f5fbc545b9df",
    "hced-Dorylaeum1147-1": "19eeb036de9ac497b6d3e99856e5a6e7627fec13e2a47b8802b21d977e918b43",
    "hced-Dyle891-1": "2f33f1a8acb214c89abc890958622091d462899165fa0ee07f76a4f49b9bfeef",
    "hced-La Gueule891-1": "3e968135745eaf6e62b3c33b7854a1c85ce5fe5382c98e10e641321b9b9eaf3e",
    "hced-Legnano1176-1": "cf4a4ef42b58368a84a1fa3528d7bcf8430a46d108dfecfe5d4df51cee6f051f",
    "hced-Pressburg907-1": "5bb057d7aedc0d925c04c263e49b4b9fa6fcdbc50a4ab762bce4b1fcdacc1cf0",
    "hced-Psie Pole1109-1": "8ef7c2c52798ce733edc88c78eb594978c63d59adcda980af5431f4815cbd606",
    "hced-Raab1044-1": "08934f8effcef6769d1e3d1be80356e43c882066cc19a557ae3f2bd06d2c09dd",
    "hced-Riade933-1": "82402b09a4c09af072977d8d5087926fd52cd731f79a469130a8e11925d386eb",
    "hced-Riga1709-1710-1": "0251050bb72cd46bd0f001775be5b6abad8c75fa5fbd7166b89a5159d618ac2b",
    "hced-SantAngelo998-1": "c6c65bc2be57b881fec7718a1f088a589e68af5d5e3ab3ba9ec616fbdaa44595",
    "hced-Sidon1196-1": "12176aceb6dcb654acbd9f0c442aa643d4eb150b3ebfe37ff3c88ea211a1defc",
    "hced-Warmstadt1113-1": "5bd629bc1df7f942eb55265df3e8fd58a97c0708c7aff0a824b9e0820a260757",
}


def _canonical(
    name: str,
    year_low: int,
    year_high: int,
    date_text: str,
    *,
    date_precision: str = "day",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{year_high}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": "engagement",
        "name": name,
        "year_low": year_low,
        "year_high": year_high,
    }


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1: Iterable[str],
    side_2: Iterable[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    outcome_source_family_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    war_type: str,
    source_outcome_override: bool = False,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "winner_side": winner_side,
        "result_type": "win",
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": sorted(set(map(str, outcome_source_ids))),
        "outcome_source_family_ids": sorted(
            set(map(str, outcome_source_family_ids))
        ),
        "actor_override": True,
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": source_outcome_override,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_GERMANY_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Cedynia972-1": _contract(
        "hced-Cedynia972-1",
        _canonical("Battle of Cedynia", 972, 972, "24 June 972"),
        "odo_mieszko_border_conflict_972",
        ["mieszko_i_polans_field_army_cedynia_972"],
        ["odo_lusatian_march_force_cedynia_972"],
        1,
        ["wave8_germany_lingvaria_cedynia", "wave8_germany_polish_land_forces_cedynia"],
        ["wave8_germany_polish_land_forces_cedynia"],
        ["polish_land_forces_museum"],
        (
            "The official military museum identifies Mieszko I's force routing "
            "Margrave Odo's army. The row is not mapped to a transhistorical Poland "
            "or Germany identity."
        ),
        confidence=0.92,
        war_type="interstate_limited",
    ),
    "hced-Cesis1919-1": _contract(
        "hced-Cesis1919-1",
        _canonical(
            "Battle of Cēsis",
            1919,
            1919,
            "6-23 June 1919",
            date_precision="day_range",
        ),
        "baltic_independence_wars_1919",
        ["estonian_latvian_cesis_field_coalition_1919"],
        ["landeswehr_iron_division_cesis_force_1919"],
        1,
        ["wave8_germany_1914_1918_cesis", "wave8_germany_latvia_estonia_cesis"],
        ["wave8_germany_1914_1918_cesis", "wave8_germany_latvia_estonia_cesis"],
        ["international_encyclopedia_first_world_war", "latvia_estonia_military_heritage"],
        (
            "The direct sources identify an Estonian-Latvian victory over the "
            "Baltische Landeswehr and Iron Division. The HCED word Germany is an "
            "actor correction to those formations, not Weimar Germany."
        ),
        confidence=0.96,
        war_type="war_of_independence",
    ),
    "hced-Cotrone982-1": _contract(
        "hced-Cotrone982-1",
        _canonical(
            "Battle of Capo Colonna (Crotone/Stilo)",
            982,
            982,
            "13 or 14 July 982",
            date_precision="day_uncertain",
        ),
        "otto_ii_calabrian_campaign_982",
        ["kalbid_sicilian_army_capo_colonna_982"],
        ["otto_ii_imperial_calabrian_army_982"],
        1,
        ["wave8_germany_st_andrews_stilo", "wave8_germany_transmed_thietmar_stilo"],
        ["wave8_germany_st_andrews_stilo", "wave8_germany_transmed_thietmar_stilo"],
        ["st_andrews_after_empire", "transmediterranean_history_thietmar"],
        (
            "Thietmar and the St Andrews synthesis establish Otto II's crushing "
            "defeat by Abū al-Qāsim's Kalbid army. Byzantium is removed from the "
            "rated victor because it was not the opposing field army in this battle."
        ),
        confidence=0.96,
        war_type="interstate_limited",
    ),
    "hced-Dorylaeum1147-1": _contract(
        "hced-Dorylaeum1147-1",
        _canonical("Battle of Dorylaeum (1147)", 1147, 1147, "25 October 1147"),
        "second_crusade_1147",
        [_RUM_ID],
        ["conrad_iii_german_crusader_host_dorylaeum_1147"],
        1,
        ["wave8_germany_oxford_dorylaeum", "wave8_germany_st_andrews_dorylaeum"],
        ["wave8_germany_oxford_dorylaeum", "wave8_germany_st_andrews_dorylaeum"],
        ["oxford_german_history_kostick", "st_andrews_roche_second_crusade"],
        (
            "The contract rates the Sultanate of Rum against Conrad III's exact "
            "Second Crusade host. It does not convert 'Germany' into a state alias."
        ),
        confidence=0.95,
        war_type="religious_war",
    ),
    "hced-Dyle891-1": _contract(
        "hced-Dyle891-1",
        _canonical(
            "Battle of the Dyle (Leuven)",
            891,
            891,
            "September 891",
            date_precision="month",
        ),
        "east_frankish_viking_campaign_891",
        ["arnulf_east_frankish_royal_army_dyle_891"],
        ["viking_lotharingian_campaign_army_891"],
        1,
        ["wave8_germany_bern_geul_dyle", "wave8_germany_lvr_vikings_rhine"],
        ["wave8_germany_bern_geul_dyle", "wave8_germany_lvr_vikings_rhine"],
        ["acta_periodica_duellatorum_carolingian_battles", "lvr_portal_rheinische_geschichte"],
        (
            "Arnulf's royal East Frankish army defeated the same campaigning "
            "Viking army that had won at the Geul earlier in 891. The staged point "
            "is near Brussels rather than Leuven and is withheld."
        ),
        confidence=0.94,
        war_type="raiding_war",
    ),
    "hced-La Gueule891-1": _contract(
        "hced-La Gueule891-1",
        _canonical("Battle on the Geul", 891, 891, "26 June 891"),
        "east_frankish_viking_campaign_891",
        ["viking_lotharingian_campaign_army_891"],
        ["sunderold_east_frankish_force_geul_891"],
        1,
        ["wave8_germany_bern_geul_dyle", "wave8_germany_lvr_vikings_rhine"],
        ["wave8_germany_bern_geul_dyle"],
        ["acta_periodica_duellatorum_carolingian_battles"],
        (
            "The Geul and Dyle rows are distinct actions with opposite outcomes, "
            "not duplicate assertions. Sunderold's rashly attacking detachment was "
            "destroyed here before Arnulf's later victory at Leuven."
        ),
        confidence=0.91,
        war_type="raiding_war",
    ),
    "hced-Legnano1176-1": _contract(
        "hced-Legnano1176-1",
        _canonical("Battle of Legnano", 1176, 1176, "29 May 1176"),
        "lombard_league_wars_1176",
        ["lombard_league_field_army_legnano_1176"],
        ["frederick_i_imperial_field_army_legnano_1176"],
        1,
        ["wave8_germany_italian_culture_legnano", "wave8_germany_newadvent_frederick_i"],
        ["wave8_germany_italian_culture_legnano", "wave8_germany_newadvent_frederick_i"],
        ["catholic_encyclopedia_frederick_i", "italian_ministry_culture_legnano"],
        (
            "The Ministry of Culture and independent historical reference agree "
            "that the Lombard League defeated Frederick I's imperial army. Both "
            "sides are confined to the Legnano field formations."
        ),
        confidence=0.96,
        war_type="civil_war",
    ),
    "hced-Pressburg907-1": _contract(
        "hced-Pressburg907-1",
        _canonical(
            "Battle of Pressburg",
            907,
            907,
            "4-5 July 907",
            date_precision="day_range",
        ),
        "east_frankish_magyar_war_907",
        ["magyar_conquest_army_pressburg_907"],
        ["liutpold_bavarian_east_frankish_army_pressburg_907"],
        1,
        ["wave8_germany_oszk_pressburg_907", "wave8_germany_pressburg_academic_crosscheck"],
        ["wave8_germany_oszk_pressburg_907", "wave8_germany_pressburg_academic_crosscheck"],
        ["oszk_pressburg_907", "tortenelmi_szemle_pressburg"],
        (
            "The routed force was Liutpold's predominantly Bavarian East Frankish "
            "expedition, not a German nation-state. The victor is the event-bounded "
            "conquest-period Magyar army, not an ethnic label."
        ),
        confidence=0.93,
        war_type="interstate_limited",
    ),
    "hced-Raab1044-1": _contract(
        "hced-Raab1044-1",
        _canonical("Battle of Ménfő", 1044, 1044, "5 July 1044"),
        "henry_iii_hungarian_intervention_1044",
        ["henry_iii_imperial_army_menfo_1044"],
        [_HUNGARY_ID],
        1,
        ["wave8_germany_trinity_menfo_primary"],
        ["wave8_germany_trinity_menfo_primary"],
        ["trinity_herman_reichenau_1044"],
        (
            "Herman of Reichenau's translated account directly records Henry III "
            "defeating and routing King Samuel Aba's Hungarian army. The row's "
            "point is far west of Ménfő near Győr and is withheld."
        ),
        confidence=0.96,
        war_type="dynastic_intervention",
    ),
    "hced-Riade933-1": _contract(
        "hced-Riade933-1",
        _canonical("Battle of Riade", 933, 933, "15 March 933"),
        "east_frankish_magyar_war_933",
        ["henry_i_east_frankish_royal_army_riade_933"],
        ["magyar_raiding_army_riade_933"],
        1,
        ["wave8_germany_cambridge_riade", "wave8_germany_indiana_riade_review"],
        ["wave8_germany_cambridge_riade", "wave8_germany_indiana_riade_review"],
        ["cambridge_medieval_history_riade", "medieval_review_riade"],
        (
            "Henry I's East Frankish royal army defeated the Magyar raiding army. "
            "Because Riade's exact site is unresolved, HCED's precise point is "
            "withheld while its modern-country field remains usable."
        ),
        confidence=0.94,
        war_type="interstate_limited",
    ),
    "hced-Riga1709-1710-1": _contract(
        "hced-Riga1709-1710-1",
        _canonical(
            "Siege of Riga (1709-1710)",
            1709,
            1710,
            "27 October (6 November) 1709-4 (15) July 1710",
            date_precision="day_range_dual_calendar",
        ),
        "great_northern_war_riga_1709_1710",
        [_SWEDEN_ID],
        [_TSARDOM_RUSSIA_ID],
        2,
        ["wave8_germany_harvard_riga_1710", "wave8_germany_springer_riga_capitulation"],
        ["wave8_germany_harvard_riga_1710", "wave8_germany_springer_riga_capitulation"],
        ["harvard_imperiia_riga", "springer_riga_capitulation"],
        (
            "The staged row is not a World War I German-Russian battle. It is the "
            "Great Northern War siege in which Russia captured Sweden's Riga. Both "
            "actors and the raw German winner are corrected on direct evidence."
        ),
        confidence=0.97,
        war_type="interstate_limited",
        source_outcome_override=True,
    ),
    "hced-SantAngelo998-1": _contract(
        "hced-SantAngelo998-1",
        _canonical(
            "Siege of Castel Sant'Angelo",
            998,
            998,
            "February-April 998",
            date_precision="month_range",
        ),
        "otto_iii_roman_intervention_998",
        ["otto_iii_imperial_roman_expedition_998"],
        ["crescentius_castel_santangelo_defenders_998"],
        1,
        ["wave8_germany_newadvent_crescentius"],
        ["wave8_germany_newadvent_crescentius"],
        ["catholic_encyclopedia_crescentius"],
        (
            "Otto III's force took Rome and the fortress held by Crescentius II. "
            "The raw loser conflates Crescentius with antipope John XVI, who had "
            "already fled; only the fortress defenders are rated."
        ),
        confidence=0.94,
        war_type="civil_war",
    ),
    "hced-Warmstadt1113-1": _contract(
        "hced-Warmstadt1113-1",
        _canonical(
            "Battle of Warnstedt",
            1113,
            1113,
            "early March 1113 (before 9 March)",
            date_precision="approximate_day",
        ),
        "salian_saxon_conflict_1113",
        ["hoyer_imperial_loyalist_force_warnstedt_1113"],
        ["saxon_princely_opposition_warnstedt_1113"],
        1,
        ["wave8_germany_deutsche_biographie_hoyer", "wave8_germany_deutsche_biographie_siegfried"],
        ["wave8_germany_deutsche_biographie_hoyer", "wave8_germany_deutsche_biographie_siegfried"],
        ["deutsche_biographie_hoyer", "deutsche_biographie_siegfried"],
        (
            "The source name is corrected from Warmstadt to Warnstedt. Deutsche "
            "Biographie identifies Hoyer's surprise victory over the Saxon princely "
            "opposition; neither side is flattened to Germany."
        ),
        confidence=0.95,
        war_type="civil_war",
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: dict[str, Any],
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    reviewed_actors: Iterable[str],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "disposition": "hold",
        "hold_category": category,
        "hold_reason": reason,
        "reviewed_outcome": "unknown",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_actor_description": list(map(str, reviewed_actors)),
        "reviewed_granularity": "engagement",
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "held_hced_owner",
        },
    }


WAVE8_GERMANY_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Cassano1158-1": _hold(
        "hced-Cassano1158-1",
        _canonical(
            "Cassano d'Adda crossing action",
            1158,
            1158,
            "July-August 1158",
            date_precision="month_range",
        ),
        "irreconcilable_tactical_outcome",
        (
            "Treccani says the Milanese so strongly held the Cassano crossing that "
            "Frederick did not attempt it, while the regional heritage narrative "
            "calls the episode a battle connected with the destruction of Fara. "
            "Those claims do not establish one stable tactical German victory."
        ),
        ["wave8_germany_ecomuseo_cassano_1158", "wave8_germany_treccani_cassano_1158"],
        ["Frederick I's second Italian expedition", "Milanese crossing defenders"],
    ),
    "hced-Psie Pole1109-1": _hold(
        "hced-Psie Pole1109-1",
        _canonical(
            "Purported Battle of Psie Pole",
            1109,
            1109,
            "traditionally 24 August 1109",
            date_precision="traditional_day",
        ),
        "historicity_and_tactical_outcome_unresolved",
        (
            "The 1109 expedition is historical, but the named Psie Pole battle and "
            "its decisive outcome rest on later tradition rather than a sufficiently "
            "secure contemporary engagement record. The uncertainty remains unknown "
            "and is never converted into a draw."
        ),
        ["wave8_germany_psie_pole_source_study", "wave8_germany_wroclaw_psie_pole_legend"],
        ["Bolesław III's Polish forces", "Henry V's imperial-Bohemian expedition"],
    ),
}


def _terminal_exclusion(
    candidate_id: str,
    canonical_event: dict[str, Any],
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    reviewed_actors: Iterable[str],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "hold_category": category,
        "hold_reason": reason,
        "reviewed_actor_description": list(map(str, reviewed_actors)),
        "reviewed_granularity": "misdated_nonbattle_occupation",
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "terminal_hced_owner",
        },
    }


WAVE8_GERMANY_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Sidon1196-1": _terminal_exclusion(
        "hced-Sidon1196-1",
        _canonical(
            "Misdated Sidon occupation assertion",
            1196,
            1196,
            "HCED year 1196; documented German arrival and occupation in 1197",
            date_precision="year_conflict",
        ),
        "wrong_year_campaign_and_no_tactical_battle",
        (
            "The German crusading army reached the Levant in September 1197 and "
            "occupied already abandoned and damaged Sidon before advancing to "
            "Beirut. The row's 1196 date, Fourth Crusade label, and opposed Ayyubid "
            "battle cannot be reconciled without inventing an engagement."
        ),
        ["wave8_germany_leeds_crusade_1197"],
        ["German Crusade of 1197", "Ayyubid-held but abandoned Sidon"],
    )
}

WAVE8_GERMANY_EXCLUSIONS = WAVE8_GERMANY_TERMINAL_EXCLUSIONS
WAVE8_GERMANY_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_GERMANY_HOLDS,
    **WAVE8_GERMANY_TERMINAL_EXCLUSIONS,
}

WAVE8_GERMANY_CONTRACT_IDS = frozenset(WAVE8_GERMANY_CONTRACTS)
WAVE8_GERMANY_HOLD_IDS = frozenset(WAVE8_GERMANY_HOLDS)
WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_GERMANY_TERMINAL_EXCLUSIONS
)
WAVE8_GERMANY_EXCLUSION_IDS = WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS
WAVE8_GERMANY_RESERVED_IDS = (
    WAVE8_GERMANY_CONTRACT_IDS
    | WAVE8_GERMANY_HOLD_IDS
    | WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS
)
WAVE8_GERMANY_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


# The Dyle coordinate is near Brussels rather than Leuven; the Raab coordinate
# is far west of Ménfő; and the exact site of Riade remains unidentified.
WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Dyle891-1",
        "hced-Raab1044-1",
        "hced-Riade933-1",
    }
)
WAVE8_GERMANY_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_GERMANY_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_GERMANY_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_GERMANY_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Riga1709-1710-1": {
        "raw_winner_label": "Germany",
        "raw_loser_label": "Russia",
        "corrected_winner_side": 2,
        "corrected_winner_entity_ids": [_TSARDOM_RUSSIA_ID],
        "corrected_loser_entity_ids": [_SWEDEN_ID],
        "outcome_source_ids": [
            "wave8_germany_harvard_riga_1710",
            "wave8_germany_springer_riga_capitulation",
        ],
        "outcome_source_family_ids": [
            "harvard_imperiia_riga",
            "springer_riga_capitulation",
        ],
        "correction_note": (
            "The locked years identify the Great Northern War siege: Russia "
            "captured the Swedish fortress. The row's Germany winner and World "
            "War I campaign label are incompatible with the event."
        ),
    }
}
WAVE8_GERMANY_OUTCOME_OVERRIDE_METADATA = WAVE8_GERMANY_OUTCOME_OVERRIDES


WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-107-39-783": {
        "source_dataset": "iwbd",
        "hced_candidate_id": "hced-Cesis1919-1",
        "disposition": "deduplicate_to_hced",
        "relationship": "same_engagement_same_dates_matching_outcome",
        "fingerprint": {
            "source_row": "783",
            "source_snapshot": "data/raw/iwbd/20260713T161518Z-fcf5747cf94b.bin",
            "name": "Cesis",
            "war_name": "Estonian Liberation",
            "start_date": "1919-06-19",
            "end_date": "1919-06-23",
            "duration_days": "5",
            "attacker_raw": "Estonia",
            "defender_raw": "Russia",
            "winner_raw": "Estonia",
            "battle_level_victor_role": "Attacker",
        },
        "reason": (
            "This is the Estonian-source twin of the Cēsis engagement. Its Russia "
            "defender is overbroad; the source-reviewed HCED owner uses the "
            "Landeswehr/Iron Division and the joint Estonian-Latvian victor."
        ),
    },
    "iwbd-108-40-787": {
        "source_dataset": "iwbd",
        "hced_candidate_id": "hced-Cesis1919-1",
        "disposition": "deduplicate_to_hced",
        "relationship": "same_engagement_same_dates_matching_outcome",
        "fingerprint": {
            "source_row": "787",
            "source_snapshot": "data/raw/iwbd/20260713T161518Z-fcf5747cf94b.bin",
            "name": "Cesis",
            "war_name": "Latvian Liberation",
            "start_date": "1919-06-19",
            "end_date": "1919-06-23",
            "duration_days": "5",
            "attacker_raw": "Latvia",
            "defender_raw": "Russia",
            "winner_raw": "Latvia",
            "battle_level_victor_role": "Attacker",
        },
        "reason": (
            "This is the Latvian-source twin of the same Cēsis engagement. It is "
            "not a second Elo event, and its Russia defender is corrected by the "
            "candidate-keyed HCED contract."
        ),
    },
}


# Candidate-keyed aliases and spans pin the negative duplicate audit. The two
# known Cēsis rows above are the only permitted IWBD matches in this snapshot.
WAVE8_GERMANY_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Cassano1158-1": {"aliases": ("cassano", "cassano d adda"), "years": (1158, 1158)},
    "hced-Cedynia972-1": {"aliases": ("cedynia", "zehden"), "years": (972, 972)},
    "hced-Cesis1919-1": {"aliases": ("cesis", "cēsis", "wenden"), "years": (1919, 1919)},
    "hced-Cotrone982-1": {
        "aliases": ("capo colonna", "cape colonna", "cotrone", "crotone", "stilo"),
        "years": (982, 982),
    },
    "hced-Dorylaeum1147-1": {"aliases": ("dorylaeum", "dorylaion"), "years": (1147, 1147)},
    "hced-Dyle891-1": {"aliases": ("dyle", "leuven", "louvain"), "years": (891, 891)},
    "hced-La Gueule891-1": {"aliases": ("geul", "gueule", "la gueule"), "years": (891, 891)},
    "hced-Legnano1176-1": {"aliases": ("legnano",), "years": (1176, 1176)},
    "hced-Pressburg907-1": {
        "aliases": ("bratislava", "pozsony", "pressburg"),
        "years": (907, 907),
    },
    "hced-Psie Pole1109-1": {"aliases": ("hundsfeld", "psie pole"), "years": (1109, 1109)},
    "hced-Raab1044-1": {"aliases": ("menfo", "ménfő", "raab"), "years": (1044, 1044)},
    "hced-Riade933-1": {"aliases": ("merseburg", "riade"), "years": (933, 933)},
    "hced-Riga1709-1710-1": {"aliases": ("riga", "siege of riga"), "years": (1709, 1710)},
    "hced-SantAngelo998-1": {
        "aliases": ("castel sant angelo", "sant angelo", "santangelo"),
        "years": (998, 998),
    },
    "hced-Sidon1196-1": {"aliases": ("sidon",), "years": (1196, 1196)},
    "hced-Warmstadt1113-1": {
        "aliases": ("warmstadt", "warnstadt", "warnstedt"),
        "years": (1113, 1113),
    },
}

WAVE8_GERMANY_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_GERMANY_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_GERMANY_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_GERMANY_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_GERMANY_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_GERMANY_ENTITIES,
        "expected_candidate_ids": sorted(WAVE8_GERMANY_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_GERMANY_HOLDS,
        "integration_dispositions": WAVE8_GERMANY_INTEGRATION_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_GERMANY_IWBD_ZERO_OVERLAP_AUDIT,
        "outcome_overrides": WAVE8_GERMANY_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_GERMANY_SOURCES,
        "terminal_exclusions": WAVE8_GERMANY_TERMINAL_EXCLUSIONS,
    }


def wave8_germany_audit_signature() -> str:
    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


# Replaced with the measured payload digest after the audit fixtures are final.
WAVE8_GERMANY_FINAL_AUDIT_SIGNATURE = (
    "45a9e0dbcfa99dda40bfeeef1452d6a8514371f0061a21c068a9924e754b85a9"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_GERMANY_CONTRACTS),
        len(WAVE8_GERMANY_HOLDS),
        len(WAVE8_GERMANY_TERMINAL_EXCLUSIONS),
    ) != (13, 2, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_GERMANY_ENTITIES), len(WAVE8_GERMANY_SOURCES)) != (21, 27):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_GERMANY_RESERVED_IDS != WAVE8_GERMANY_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    dispositions = (
        WAVE8_GERMANY_CONTRACT_IDS,
        WAVE8_GERMANY_HOLD_IDS,
        WAVE8_GERMANY_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(3)
        for j in range(i + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if wave8_germany_audit_signature() != WAVE8_GERMANY_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_GERMANY_SOURCES}
    if len(source_by_id) != len(WAVE8_GERMANY_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_GERMANY_SOURCES:
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_GERMANY_ENTITIES}
    if len(entity_by_id) != len(WAVE8_GERMANY_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_entity_ids = {
        "german_empire",
        "nazi_germany",
        "weimar_germany",
        "federal_republic_germany",
        "german_democratic_republic",
    }
    for entity_id, entity in entity_by_id.items():
        if entity_id in forbidden_entity_ids:
            raise ValueError(f"{_LANE_NAME} bridged a German regime")
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} identity is not event bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if str(entity["name"]).strip().casefold() == "germany":
            raise ValueError(f"{_LANE_NAME} installed generic Germany")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    allowed_existing = {_HUNGARY_ID, _RUM_ID, _SWEDEN_ID, _TSARDOM_RUSSIA_ID}
    used_new_entities: set[str] = set()
    used_sources: set[str] = set()
    override_ids: set[str] = set()
    for candidate_id, contract in WAVE8_GERMANY_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["granularity"] != "engagement":
            raise ValueError(f"{_LANE_NAME} promoted a non-engagement")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (side_1 | side_2) <= (set(entity_by_id) | allowed_existing):
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        used_new_entities.update((side_1 | side_2) & set(entity_by_id))
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        for entity_id in (side_1 | side_2) & set(entity_by_id):
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= low <= high <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] not in {1, 2}
            or contract["actor_override"] is not True
            or contract["outcome_reversal"] is not contract["source_outcome_override"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome/actor policy drifted")
        if contract["source_outcome_override"]:
            override_ids.add(candidate_id)
        ownership = contract["duplicate_ownership"]
        if ownership != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if not outcomes or not _is_sorted_unique(outcomes) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        used_sources.update(evidence)

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} has an unused bounded identity")
    used_sources.update(
        source_id
        for entity in WAVE8_GERMANY_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    for candidate_id, item in WAVE8_GERMANY_NONPROMOTIONS.items():
        if item["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} nonpromotion hash drifted")
        if not set(map(str, item["evidence_refs"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} nonpromotion names an unknown source")
        if item["duplicate_ownership"]["owner_module"] != _MODULE_OWNER:
            raise ValueError(f"{_LANE_NAME} nonpromotion ownership drifted")
        used_sources.update(map(str, item["evidence_refs"]))
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    for hold in WAVE8_GERMANY_HOLDS.values():
        if (
            hold["disposition"] != "hold"
            or hold["result_type"] != "unknown"
            or hold["reviewed_outcome"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
            or "winner_side" in hold
        ):
            raise ValueError(f"{_LANE_NAME} unknown outcome became a draw or win")
    for exclusion in WAVE8_GERMANY_TERMINAL_EXCLUSIONS.values():
        if (
            exclusion["disposition"] != "terminal_exclusion"
            or exclusion["terminal_exclusion"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} terminal exclusion drifted")

    if override_ids != {"hced-Riga1709-1710-1"}:
        raise ValueError(f"{_LANE_NAME} outcome override inventory drifted")
    if set(WAVE8_GERMANY_OUTCOME_OVERRIDES) != override_ids:
        raise ValueError(f"{_LANE_NAME} override metadata drifted")
    for candidate_id, metadata in WAVE8_GERMANY_OUTCOME_OVERRIDES.items():
        contract = WAVE8_GERMANY_CONTRACTS[candidate_id]
        if (
            metadata["corrected_winner_side"] != contract["winner_side"]
            or metadata["corrected_winner_entity_ids"]
            != contract[f"side_{contract['winner_side']}_entity_ids"]
            or metadata["outcome_source_ids"] != contract["outcome_source_ids"]
            or metadata["outcome_source_family_ids"]
            != contract["outcome_source_family_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome override metadata drifted")

    expected_points = {"hced-Dyle891-1", "hced-Raab1044-1", "hced-Riade933-1"}
    if WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS != expected_points:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_GERMANY_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if not WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS <= WAVE8_GERMANY_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} quarantines a nonpromotion")

    expected_iwbd = {"iwbd-107-39-783", "iwbd-108-40-787"}
    if set(WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS) != expected_iwbd:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    for disposition in WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS.values():
        if (
            disposition["hced_candidate_id"] != "hced-Cesis1919-1"
            or disposition["disposition"] != "deduplicate_to_hced"
        ):
            raise ValueError(f"{_LANE_NAME} IWBD duplicate ownership changed")
    if WAVE8_GERMANY_CROSS_LANE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited cross-lane owner")
    if WAVE8_GERMANY_INTEGRATION_DISPOSITIONS != WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} integration dispositions drifted")
    if set(WAVE8_GERMANY_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_GERMANY_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} IWBD negative audit is incomplete")


def validate_wave8_germany_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_GERMANY_CONTRACTS,
        WAVE8_GERMANY_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_GERMANY_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_GERMANY_TERMINAL_EXCLUSIONS),
    }


def _iwbd_fingerprint(row: Mapping[str, Any]) -> dict[str, str]:
    fields = (
        "source_row",
        "source_snapshot",
        "name",
        "war_name",
        "start_date",
        "end_date",
        "duration_days",
        "attacker_raw",
        "defender_raw",
        "winner_raw",
        "battle_level_victor_role",
    )
    return {
        field: "" if row.get(field) is None else str(row.get(field)) for field in fields
    }


def _date_year(value: Any) -> int | None:
    text = str(value or "")
    if len(text) < 4 or not text[:4].isdigit():
        return None
    return int(text[:4])


def validate_wave8_germany_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin the two Cēsis twins and fail on any new plausible IWBD overlap."""

    validate_wave8_germany_queue_contracts(hced_rows)
    iwbd_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in iwbd_rows:
        iwbd_by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, disposition in WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS.items():
        rows = iwbd_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one IWBD duplicate {candidate_id}, "
                f"found {len(rows)}"
            )
        actual = _iwbd_fingerprint(rows[0])
        expected = disposition["fingerprint"]
        if actual != expected:
            changed = sorted(key for key in expected if actual.get(key) != expected[key])
            raise ValueError(
                f"{_LANE_NAME} IWBD duplicate fingerprint changed for "
                f"{candidate_id}: {changed}"
            )

    known_ids = set(WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS)
    normalized_audit = {
        hced_id: {
            "aliases": {normalize_label(alias) for alias in item["aliases"]},
            "years": tuple(map(int, item["years"])),
        }
        for hced_id, item in WAVE8_GERMANY_IWBD_ZERO_OVERLAP_AUDIT.items()
    }
    for row in iwbd_rows:
        iwbd_id = str(row.get("candidate_id") or "")
        if iwbd_id in known_ids:
            continue
        start = _date_year(row.get("start_date"))
        end = _date_year(row.get("end_date"))
        if start is None or end is None:
            continue
        name = normalize_label(row.get("name"))
        for hced_id, audit in normalized_audit.items():
            low, high = audit["years"]
            if start <= high and end >= low and name in audit["aliases"]:
                raise ValueError(
                    f"{_LANE_NAME} found unreviewed plausible IWBD overlap "
                    f"{iwbd_id} for {hced_id}"
                )
    return {
        "cross_lane_hced_dispositions": 0,
        "integration_dispositions": len(WAVE8_GERMANY_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_GERMANY_IWBD_ZERO_OVERLAP_AUDIT
        ),
    }


def install_wave8_germany_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_GERMANY_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_germany_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_GERMANY_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_GERMANY_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_germany_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_germany_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_GERMANY_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_germany_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_GERMANY_CONTRACTS.values()
            ).items()
        )
    )


def wave8_germany_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_GERMANY_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_GERMANY_CROSS_LANE_DISPOSITIONS
        ),
        "holds": len(WAVE8_GERMANY_HOLDS),
        "integration_dispositions": len(WAVE8_GERMANY_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_GERMANY_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_GERMANY_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_GERMANY_ENTITIES),
        "new_sources": len(WAVE8_GERMANY_SOURCES),
        "newly_rated_events": len(WAVE8_GERMANY_CONTRACTS),
        "outcome_overrides": len(WAVE8_GERMANY_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_GERMANY_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_GERMANY_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_GERMANY_TERMINAL_EXCLUSIONS),
    }


def wave8_germany_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_GERMANY_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_GERMANY_POINT_QUARANTINE_ADDITIONS,
    }
