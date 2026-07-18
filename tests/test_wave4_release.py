import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "data" / "release"
REGISTRY = ROOT / "data" / "catalog" / "registry.json"
RESULTS = ROOT / "web" / "data" / "results.json"

APPROVED_HCED = {
    "hced-Miletus-334-1",
    "hced-Issus-333-1",
    "hced-Sebastopolis692-1",
    "hced-Yaunis Khan1516-1",
    "hced-Slaak1631-1",
    "hced-Sas van Gent1644-1",
    "hced-Saints1782-1",
}
BLOCKED_HCED = {
    "hced-Megalopolis-331-1",
    "hced-Jaxartes-329-1",
    "hced-Antioch1268-1",
    "hced-Mons1572-1",
    "hced-Steenwijk1592-1",
    "hced-Amjhera1728-1",
    "hced-Abensberg1809-1",
    "hced-Hudayda1934-1",
}


class Wave5ReleaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = json.loads((RELEASE / "events.json").read_text(encoding="utf-8"))
        cls.entities = json.loads(
            (RELEASE / "entities.json").read_text(encoding="utf-8")
        )
        cls.sources = json.loads((RELEASE / "sources.json").read_text(encoding="utf-8"))
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.results = json.loads(RESULTS.read_text(encoding="utf-8"))
        cls.events_by_id = {event["id"]: event for event in cls.events}
        cls.registry_by_id = {
            entity["id"]: entity for entity in cls.registry["entities"]
        }

    def test_exact_release_composition_and_approved_candidate_set(self) -> None:
        families = Counter(
            tuple(event.get("outcome_source_family_ids", ())) for event in self.events
        )
        self.assertEqual(len(self.events), 5_414)
        self.assertEqual(len(self.entities), 1_024)
        self.assertEqual(len(self.registry_by_id), 2_372)
        self.assertEqual(
            families,
            {
            (): 40,
            ("academia_nacional_historia_argentina",): 1,
            ("academy_korean_studies_history_2019", "ahn_goguryeo_tang_war_2022"): 1,
            ("academy_korean_studies_history_2019", "hwang_history_korea_2021"): 1,
            ("academy_korean_studies_history_2019", "hwang_history_korea_2021", "lim_silla_fall_koguryo_2023"): 1,
            ("acosta_apuntes_historicos_sonorenses", "spicer_cycles_of_conquest_mayos_yaquis", "troncoso_yaqui_mayo_tomo_i"): 1,
            ("acta_periodica_duellatorum_carolingian_battles",): 1,
            ("acta_periodica_duellatorum_carolingian_battles", "lvr_portal_rheinische_geschichte"): 1,
            ("aethelweard_chronicle_book_four", "anglo_saxon_chronicle_ingram_yale"): 2,
            ("aethelweard_chronicle_book_four", "anglo_saxon_chronicle_ingram_yale", "surrey_archaeological_society_farnham_893"): 1,
            ("africa_watch_ethiopia_eritrea_reporting_1990_1991", "eplf_27_may_1991_final_offensive_communique", "hiltzik_latimes_26_may_1991", "upi_wire_assab_25_may_1991"): 1,
            ("africa_watch_ethiopia_eritrea_reporting_1990_1991", "eplf_27_may_1991_final_offensive_communique", "loc_ethiopia_country_study_1991"): 1,
            ("africa_watch_ethiopia_eritrea_reporting_1990_1991", "harding_lrb_eritrean_revolution_1987"): 1,
            ("africa_watch_ethiopia_eritrea_reporting_1990_1991", "tareke_ethiopian_revolution_massawa_2009"): 1,
            ("agency_cultural_affairs_satsuma_rebellion_sites", "japan_tourism_agency_tabaruzaka", "kumamoto_city_satsuma_rebellion"): 1,
            ("ageron_algerian_border_battle_1999", "connelly_diplomatic_revolution_2002", "fsale_tunisian_frontier_1958"): 1,
            ("air_university_prolonged_wars_chad", "french_defense_tacaud_ecpad", "loc_chad_country_study_1990", "powell_frances_wars_chad_2020"): 1,
            ("air_university_prolonged_wars_chad", "hrw_enabling_habre_2016", "loc_chad_country_study_1990"): 1,
            ("ajmer_singh_military_campaigns_thesis_1997", "hari_ram_gupta_history_sikhs_vol4", "punjabi_university_encyclopaedia_ram_singh_bedi"): 1,
            ("ajmer_singh_military_campaigns_thesis_1997", "harry_smith_autobiography_1903", "khushwant_singh_history_sikhs_vol2"): 1,
            ("alagappa_history_tamil_nadu", "orme_military_transactions_indostan"): 1,
            ("ami_praful_shah_sri_gursobha", "hari_ram_gupta_history_sikhs_vol1", "js_grewal_master_white_hawk_2020", "khushwant_singh_history_sikhs_vol1", "max_arthur_macauliffe_sikh_religion_vol5"): 1,
            ("ammianus_roman_history_loeb", "drinkwater_alamanni_and_rome_2007"): 3,
            ("amnesty_qala_i_jhangi_2001", "doj_lindh_affidavit_2002", "folse_army_cmh_oef_2022", "uk_hansard_qala_i_jhangi_2001", "us_army_mitchell_dsc_qala_2007"): 1,
            ("anatolian_studies",): 1,
            ("anglo_saxon_chronicle_ingram_yale",): 1,
            ("anna_komnene_alexiad", "istanbul_university_kilij_arslan"): 1,
            ("annales_maritimes_tamatave_1845", "mcleod_madagascar_people_1865"): 1,
            ("anu_muslim_mindanao_study", "first_battalion_22d_infantry_datu_ali", "us_army_campaign_summaries_philippines"): 1,
            ("anu_muslim_mindanao_study", "us_war_department_1904_philippines"): 1,
            ("appian_macedonian_wars", "livy_ab_urbe_condita"): 1,
            ("archaeological_atlas_vladar", "fudge_laurence_brezova_chronicle"): 1,
            ("argentina_gob_ar_independence_history",): 1,
            ("argentine_navy_independence_history",): 1,
            ("army_heritage_nez_perce_war_1877", "greene_nez_perce_summer_1877", "nps_nez_perce_battlefield_interpretation"): 1,
            ("army_historical_foundation_almanac_2025", "clodfelter_warfare_armed_conflicts", "nps_fort_union_historic_resource_study"): 1,
            ("army_history_lawton_frontier", "texas_beyond_history_red_river_battles", "tpwd_palo_duro_history", "tsha_palo_duro"): 1,
            ("army_history_magazine_74", "clodfelter_warfare_armed_conflicts", "santala_ute_campaign_1879"): 1,
            ("army_scouts_out_rafah_case", "pollack_air_power_six_day_war"): 1,
            ("aunamendi_alegria", "gran_enciclopedia_espana_alegria"): 1,
            ("australian_army_cove_tora_bora_2021", "commons_library_rp05_72", "folse_army_cmh_oef_2022", "senate_foreign_relations_tora_bora_2009"): 1,
            ("ayacucho_primary_document_compilation", "peru_agn_ayacucho_article", "peru_bicentenario_ayacucho_history"): 1,
            ("baburnama_beveridge_translation", "banglapedia_babur", "inflibnet_mughal_history_module"): 1,
            ("baburnama_beveridge_translation", "bregel_historical_atlas_central_asia"): 1,
            ("baddeley_russian_conquest_1908", "baumann_leavenworth_paper_20", "gammer_muslim_resistance_monograph"): 1,
            ("baddeley_russian_conquest_1908", "gammer_muslim_resistance_monograph", "great_russian_encyclopedia_ghazi_muhammad"): 1,
            ("bailony_transnational_rebellion_2025", "frus_1925_syrian_insurrection", "ieg_humanitarianism_atlas_damascus", "miller_ijmes_syrian_revolt_1977"): 1,
            ("bailony_ucla_dissertation", "foreign_legion_rachaya_archive", "frus_1925_syrian_insurrection"): 1,
            ("balcerek_daugava_wars_review", "frost_northern_wars_monograph"): 1,
            ("balkans_journal_berat_1281", "byzantina_symmeikta_berat"): 1,
            ("bamberg_gefrees_study", "gill_with_eagles_to_glory", "mcgill_napoleon_fifth_coalition_timeline"): 1,
            ("bangor_elizabeth_french_wars", "james_wood_kings_army"): 1,
            ("bangor_university_research", "saudipedia_heritage_commission"): 1,
            ("bangor_university_research", "university_east_anglia_repository"): 1,
            ("baranov_lake_smolino_reconsidered", "kirby_baltic_world_monograph"): 1,
            ("barmm_bcpch_lanao_validation", "us_army_campaign_summaries_philippines"): 1,
            ("barmm_bcpch_lanao_validation", "us_army_counterinsurgency_doctrine_history", "us_war_department_1904_philippines"): 1,
            ("basham_wonder_india", "goi_battle_raor_study"): 1,
            ("battlefields_trust_western_rebellion", "rose_troup_western_rebellion_1913"): 2,
            ("bauer_vilcabamba_2016", "murua_bauer_gamarra_gonzales_2024", "renard_casevitz_east_andes_2008"): 1,
            ("bavarian_general_staff_campaign_1809", "gill_thunder_danube_volume_two", "thiers_consulate_empire_volume_ten"): 1,
            ("bbaw_pmbz",): 1,
            ("bedfordshire_archives_bedford_castle", "norgate_minority_henry_iii_1912", "ray_fine_rolls_bedford_2007"): 1,
            ("beras_clio_1962_azua", "espinal_clio_2020_independence"): 1,
            ("berthier_egypt_campaign_primary", "fondation_napoleon_egypt_campaign", "napoleon_general_correspondence_chronology_2"): 1,
            ("betts_druze_yale", "frus_1925_syrian_insurrection", "provence_great_syrian_revolt_2005"): 1,
            ("black_hawk_wisconsin_heights_primary_account", "henry_dodge_wisconsin_heights_primary_account", "us_army_cmh_black_hawk_campaign", "wisconsin_shpo_historic_indians_context"): 1,
            ("bleckmann_alamanni_lake_garda_1999", "drinkwater_alamanni_and_rome_2007", "epitome_de_caesaribus_34_35", "ric_online_268_276_history"): 1,
            ("blondy_rhodes_arrival_2000", "rhodes_medieval_sieges_pur"): 1,
            ("bloomsbury_ib_tauris", "durham_university_etheses"): 1,
            ("bloomsbury_ib_tauris", "durham_university_etheses", "university_east_anglia_repository"): 1,
            ("bnf_siege_montauban_1621", "musee_protestant"): 1,
            ("boe_gaceta_madrid", "real_academia_historia_spain", "spanish_navy_history"): 1,
            ("borgomanero_municipal_battle_study", "treccani_fogliano_biography"): 1,
            ("bosworth_oxford_alexander_2015", "diodorus_library_oldfather", "flower_alexander_panhellenism_2000"): 1,
            ("brill_namibia_history", "cambridge_hidden_histories_gordonia"): 1,
            ("brill_namibia_history", "suub_bremen_german_colonial_collection"): 1,
            ("brill_peter_i_alexandria_1365", "ozkutlu_peter_i_alexandria_thesis"): 1,
            ("britannica_1911_arcot", "marshman_history_india"): 1,
            ("britannica_madagascar_1911", "ecpad_madagascar_1883_1885"): 1,
            ("british_library_dubba_correspondence", "lambrick_sind_battles_1943", "napier_conquest_scinde_1845"): 1,
            ("british_museum_collection", "diodorus_library_history_green_translation"): 1,
            ("bu_chosen_city_megiddo_609", "thiele_megiddo_609_chronology"): 1,
            ("buckler_beck_central_greece_2008", "lucas_boeotian_military_organization_2023", "plutarch_pelopidas_perrin", "xenophon_hellenica_brownson"): 1,
            ("buckler_beck_central_greece_2008", "plutarch_pelopidas_perrin"): 1,
            ("bulletin_school_oriental_african_studies", "suny_press_tabari"): 1,
            ("burton_fall_herat_1588", "iranica_ali_qoli_khan_shamlu"): 1,
            ("cambridge_ancient_history_pyrrhus", "cambridge_cicero_brutus_pyrrhic_war", "plutarch_life_pyrrhus_perrin_translation"): 2,
            ("cambridge_ancient_history_pyrrhus", "cambridge_roman_commonwealth_chronology", "plutarch_life_pyrrhus_perrin_translation"): 1,
            ("cambridge_ancient_history_pyrrhus", "plutarch_life_pyrrhus_perrin_translation"): 1,
            ("cambridge_ancient_history_roman_expansion_west", "hoyos_roman_strategy_cisalpina", "livy_book_33_roberts_translation", "rawlings_cisalpine_conquest_201_191"): 1,
            ("cambridge_ancient_history_roman_expansion_west", "livy_book_32_edmonds_translation", "rawlings_cisalpine_conquest_201_191"): 1,
            ("cambridge_ancient_history_south_italy", "livy_ab_urbe_condita_8_24"): 1,
            ("cambridge_central_european_history",): 1,
            ("cambridge_companion_crusades_chronology", "oneil_rhodes_bastion"): 1,
            ("cambridge_crusader_warfare", "routledge_crusader_history"): 1,
            ("cambridge_goffman_ottoman_europe", "pup_provence_renaissance_history"): 1,
            ("cambridge_hidden_histories_gordonia", "suub_bremen_german_colonial_collection"): 1,
            ("cambridge_history_portugal", "cham_nova_portuguese_expansion"): 1,
            ("cambridge_history_turkey_mediterranean_expansion", "oneil_rhodes_bastion"): 1,
            ("cambridge_medieval_history_riade", "medieval_review_riade"): 1,
            ("cambridge_ming_china_vietnam", "quang_ninh_military_bach_dang"): 1,
            ("cambridge_mongols_and_mamluks",): 1,
            ("cambridge_naples_1799", "treccani_neapolitan_republic_1799"): 1,
            ("cambridge_phillips_lisbon_letter", "oxford_phillips_second_crusade"): 1,
            ("cambridge_struve_southern_ming", "taiwan_waiji_volume_4", "wakeman_great_enterprise_volume_1"): 1,
            ("cambridge_visigothic_kingdom", "university_barcelona_repository"): 1,
            ("canadian_army_unit_history",): 1,
            ("cardenas_historia_mexicana_3421", "spicer_cycles_of_conquest_mayos_yaquis", "texas_band_of_yaqui_history", "troncoso_yaqui_mayo_tomo_i"): 1,
            ("carpenter_minority_henry_iii_1990", "norgate_minority_henry_iii_1912"): 1,
            ("carpenter_war_on_illahee_dissertation", "historylink_kamiakin_10096", "historylink_toppenish_5311", "usfs_gifford_pinchot_cultural_overview"): 1,
            ("cassius_dio_roman_history_cary_translation", "oxford_classical_dictionary_decebalus", "sidebottom_encyclopedia_ancient_battles_dacian_wars"): 1,
            ("cassius_dio_roman_history_cary_translation", "oxford_classical_dictionary_decebalus", "sidebottom_encyclopedia_ancient_battles_dacian_wars", "tekir_domitian_dacian_war"): 1,
            ("cathcart_king_krak_1949", "unesco_krak_nomination_dossier"): 1,
            ("catholic_encyclopedia_crescentius",): 1,
            ("catholic_encyclopedia_frederick_i", "italian_ministry_culture_legnano"): 1,
            ("caulk_egyptian_path_harar", "mprl_munzinger_northeast_africa"): 1,
            ("ceska_skalice_museum_battle", "cornej_jan_zizka_2019"): 1,
            ("cia_studies_intelligence_swords_review_2022", "commons_library_rp01_112", "folse_army_cmh_oef_2022", "un_hossain_afghanistan_2002"): 1,
            ("city_of_belgrade",): 1,
            ("cizek_jcu_zablati_2017", "czech_npu_buquoy_2021"): 1,
            ("clio_1950_el_numero_report", "espinal_clio_2020_independence"): 1,
            ("codrington_short_history_ceylon_1926", "cordiner_description_ceylon_1807", "jaques_dictionary_battles_2006", "powell_kandyan_wars_1973"): 1,
            ("clodfelter_warfare_armed_conflicts", "jaques_dictionary_battles_2006", "real_academia_historia_dbe"): 1,
            ("coghlan_harte_natalia_2005", "colenbrander_spencer_natalia_1906_report", "gillings_bambata_mome_1989"): 1,
            ("coghlan_harte_natalia_2005", "gillings_bambata_mome_1989", "saho_bambatha_rebellion"): 1,
            ("coghlan_umvoti_field_force_2006", "colenbrander_spencer_natalia_1906_report", "paterson_natal_rebellion_2006", "waikato_times_mpukunyoni_1906"): 1,
            ("collins_army_white_bird_staff_ride", "greene_nez_perce_summer_1877", "nps_nez_perce_battlefield_interpretation"): 1,
            ("comite_madagascar_bulletin_1895", "duchesne_madagascar_report_1897"): 1,
            ("commons_library_rp01_112", "folse_army_cmh_oef_2022", "hrw_kunduz_surrender_2001", "un_afghanistan_mission_2003"): 1,
            ("compton_european_military_adventurers", "francklin_george_thomas_1803", "ministry_culture_fatehpur_history"): 1,
            ("cornej_jan_zizka_2019", "horice_municipal_history"): 1,
            ("coskun_ptolemaioi_commanders", "livius_third_syrian_war"): 1,
            ("cox_green_count_monograph", "rennes_amadeus_vi_study"): 1,
            ("cutrer_tsha_aaron_burleson", "thompson_tsha_brushy_creek", "williamson_county_brushy_creek_history"): 1,
            ("czech_mod_white_mountain", "oxford_cabinet_white_mountain"): 1,
            ("danang_government_vijaya", "ebsco_battle_vijaya"): 1,
            ("david_bryson_queen_jeanne", "james_westfall_thompson_french_wars"): 1,
            ("dbnl", "scientia_militaria"): 1,
            ("de_wet_memoir", "south_african_military_history_society"): 2,
            ("demir_tigranocerta_2021", "oxford_classical_dictionary_tigranocerta", "plutarch_lucullus_dryden_clough"): 1,
            ("der_nersessian_cilician_armenia_1962", "ghazarian_cilician_armenia_2000", "smbat_sparapet_chronicle_bedrosian"): 1,
            ("derbyshire_her_mdr5341", "oakes_barons_war_thesis_2015"): 1,
            ("deutsche_biographie_hoyer", "deutsche_biographie_siegfried"): 1,
            ("deutsche_biographie_ottokar_ii", "habsburger_net_marchfeld", "orf_lbi_marchfeld_2022"): 1,
            ("deutsche_biographie_ottokar_ii", "rohac_kressenbrunn_2016"): 1,
            ("deutsches_historisches_museum", "german_federal_archives"): 1,
            ("deutsches_historisches_museum", "suub_bremen_german_colonial_collection"): 1,
            ("devries_infantry_warfare_1996", "france_culture_cassel_1328", "larousse_philip_vi", "pirenne_cassel_consequences_1899", "somme_devries_review_1999", "tebrake_plague_insurrection_1993"): 1,
            ("devries_infantry_warfare_1996", "lambert_guldensporenslag_2000", "verbruggen_golden_spurs_2002"): 1,
            ("devries_infantry_warfare_1996", "larousse_philip_iv", "somme_devries_review_1999"): 1,
            ("dia_ethiopia_1985_operations", "hrw_evil_days_barentu"): 1,
            ("dickinson_college_commentaries",): 1,
            ("dickinson_house_divided_little_robe_1858", "rea_ohs_antelope_hills_2010"): 1,
            ("dionysius_roman_antiquities", "oxford_classical_dictionary"): 1,
            ("dionysius_roman_antiquities", "treccani_enciclopedia_italiana"): 1,
            ("dnb_john_macdonald_1885", "nls_feuds_conflicts_clans"): 1,
            ("dorsainvil_manuel_histoire_haiti", "haiti_government_vertieres_commemoration", "thomas_madiou_histoire_haiti"): 1,
            ("dorsainvil_manuel_histoire_haiti", "ispan_bulletin_40_port_republicain", "thomas_madiou_histoire_haiti"): 1,
            ("dublin_city_walls_heritage", "ucc_celt_annals_tigernach"): 1,
            ("duchesne_madagascar_report_1897", "french_army_andriba_map_1897", "hauts_faits_armee_madagascar_1899"): 1,
            ("duchesne_madagascar_report_1897", "french_army_first_rca_history", "hauts_faits_armee_madagascar_1899"): 1,
            ("dull_coronea_orchomenus_1977", "thucydides_peloponnesian_war_crawley", "van_wijk_athens_and_boiotia_2024"): 1,
            ("durham_university_etheses", "kings_college_london_research"): 1,
            ("ebsco_bannock_war_history", "washington_guard_bannock_war_official_history"): 1,
            ("ecuador_academia_nacional_historia",): 1,
            ("ecuador_academia_nacional_historia", "ecuadorian_army_history"): 5,
            ("edinburgh_university_press", "unesco_world_heritage_centre"): 1,
            ("egan_early_stewart_lordship_article", "hes_inverlochy_btl34", "scots_peerage_volume_five_macdonald"): 1,
            ("egan_early_stewart_lordship_article", "scots_peerage_volume_five_macdonald"): 1,
            ("egypt_study_circle_eastern_sudan", "hansard_sinkat_1884"): 1,
            ("elishe_neumann_translation_1830", "iranica_avarayr_1987", "iranica_elise_thomson_1998"): 1,
            ("encyclopaedia_britannica_1926", "library_of_congress_country_studies", "university_east_anglia_repository"): 1,
            ("encyclopaedia_britannica_1926", "university_east_anglia_repository"): 1,
            ("encyclopaedia_iranica", "university_chicago_oriental_institute"): 1,
            ("encyclopaedia_iranica_bayju", "encyclopaedia_iranica_saljuqs_rum"): 1,
            ("encyclopedia_history_ukraine",): 1,
            ("english_heritage_rochester_history", "historic_england_rochester_1011030", "oakes_barons_war_thesis_2015"): 1,
            ("english_heritage_rochester_history", "historic_england_rochester_1011030", "vincent_magna_carta_rochester_1215"): 1,
            ("english_historical_review",): 1,
            ("epitome_de_caesaribus_34_35", "historia_augusta_aurelian_loeb", "watson_aurelian_third_century"): 2,
            ("esper_russia_baltic_article", "narva_city_official_history", "narva_museum_history"): 1,
            ("espinal_clio_2020_independence", "ricardo_clio_1956_sabana_larga"): 1,
            ("eutropius_dickinson_caesar_alexandria", "jrs_caesar_alexandria_departure"): 1,
            ("field_artillery_journal_bud_bagsak_1925", "ncca_sagisag_kultura_bud_bagsak", "us_army_campaign_summaries_philippines"): 1,
            ("filiu_gaza_history", "pollack_air_power_six_day_war"): 1,
            ("firro_history_druzes_1992", "neep_occupying_syria_2012", "provence_great_syrian_revolt_2005"): 1,
            ("first_maccabees_primary", "routledge_pre_modern_warfare"): 1,
            ("fondation_napoleon_egypt_campaign", "fondation_napoleon_jean_rapp", "napoleon_general_correspondence_chronology_2", "thibaudeau_egypt_campaign_volume_2"): 1,
            ("fondation_napoleon_jean_rapp", "thibaudeau_egypt_campaign_volume_2"): 1,
            ("foord_russian_campaign_1812", "great_russian_encyclopedia_polotsk", "napoleon_series_polotsk_chapter_six"): 1,
            ("fort_loudoun_state_historic_area", "tennessee_archaeology_research_series_17", "unc_press_french_indian_war_entry"): 1,
            ("founders_online_gaeta_1806", "treccani_gaeta_1806"): 1,
            ("founders_online_jefferson_papers",): 2,
            ("frederick_ii_ascalon_sourcebook", "tdv_al_salih_ayyub"): 1,
            ("fudge_laurence_brezova_chronicle", "hardy_alsatian_zatec_account"): 1,
            ("fudge_laurence_brezova_chronicle", "husitstvi_maly_bor"): 1,
            ("fudge_laurence_brezova_chronicle", "posazavi_porici_memorial"): 1,
            ("fudge_laurence_brezova_chronicle", "prague2_vysehrad_battle"): 1,
            ("fudge_laurence_brezova_chronicle", "vhu_pekar_vitkov_source_collection"): 1,
            ("gammer_muslim_resistance_monograph",): 1,
            ("gammer_muslim_resistance_monograph", "great_russian_encyclopedia_akhulgo", "milyutin_north_dagestan_1839", "takhnaeva_akhulgo_2020"): 1,
            ("gammer_muslim_resistance_monograph", "great_russian_encyclopedia_dargo_1845", "statiev_mountain_warfare_dargo"): 1,
            ("gammer_muslim_resistance_monograph", "great_russian_encyclopedia_gunib_1859", "tdv_islam_encyclopedia_shamil"): 1,
            ("gammer_muslim_resistance_monograph", "hadji_ali_eyewitness_account", "nplg_orbeliani_chronology"): 1,
            ("gammer_muslim_resistance_monograph", "milyutin_north_dagestan_1839"): 1,
            ("gammer_muslim_resistance_monograph", "tdv_islam_encyclopedia_shamil"): 1,
            ("garcia_camba_peru_military_memories", "puno_alto_peru_independence_article"): 1,
            ("gawrych_key_to_sinai", "pollack_air_power_six_day_war"): 3,
            ("geneva_state_archives_escalade", "swiss_national_museum_escalade"): 1,
            ("gibson_kickapoo_history", "no_koaht_little_concho_account"): 1,
            ("grant_duff_history_mahrattas_volume_3", "sahai_politics_patronage_protest", "usi_de_boigne_archive_study"): 2,
            ("great_russian_encyclopedia_pugachev",): 2,
            ("great_russian_encyclopedia_pugachev", "harvard_imperiia_pugachev"): 1,
            ("great_russian_encyclopedia_pugachev", "samara_university_pugachev_kazan"): 1,
            ("great_soviet_encyclopedia_caucasian_war", "hadji_ali_eyewitness_account", "nplg_orbeliani_chronology"): 1,
            ("greene_nez_perce_summer_1877", "nps_nez_perce_battlefield_interpretation"): 2,
            ("greene_nez_perce_summer_1877", "nps_nez_perce_battlefield_interpretation", "scott_big_hole_battlefield_archaeology"): 1,
            ("groome_ordnance_gazetteer_scotland", "historic_environment_scotland_craibstone"): 1,
            ("guerra_colonial_journal", "suub_bremen_german_colonial_collection"): 1,
            ("guerzoni_garibaldi_volume_1", "treccani_garibaldi_enciclopedia_italiana"): 1,
            ("gurvinderpal_kaur_anandpur_damdama_thesis", "hari_ram_gupta_history_sikhs_vol1", "khushwant_singh_history_sikhs_vol1", "max_arthur_macauliffe_sikh_religion_vol5"): 1,
            ("hamilton_leper_king_montgisard", "ifpo_saladin_montgisard"): 1,
            ("hanak_sviatoslav_1995", "leo_deacon_history_talbot_sullivan"): 2,
            ("hanoi_government_ngoc_hoi_dong_da", "scov_ngoc_hoi_dong_da", "vass_ngoc_hoi_dong_da"): 1,
            ("hari_ram_gupta_history_sikhs_vol1", "pashaura_singh_routledge_hargobind"): 1,
            ("hari_ram_gupta_history_sikhs_vol2", "khushwant_singh_banda_bahadur_chapter", "mirza_muhammad_harisi_ibratnamah"): 1,
            ("harvard_imperiia_riga", "springer_riga_capitulation"): 1,
            ("hayavadana_rao_history_mysore_1945", "tamil_nadu_arcot_municipality_history"): 1,
            ("hced",): 4690,
            ("henry_atkinson_bad_axe_primary_account", "patrick_jung_black_hawk_war_monograph", "sac_and_fox_nation_bad_axe_history", "us_army_cmh_black_hawk_campaign", "wisconsin_shpo_historic_indians_context"): 1,
            ("herath_kandy_1803_massacre_2024", "johnston_candy_expedition_narrative_1810", "powell_kandyan_wars_1973", "sivasundaram_tales_land_2007"): 1,
            ("heritage_malta_napoleon_invasion_document", "knobler_holy_wars_2006"): 1,
            ("himmerich_y_valencia_cuzco_1998", "lavalle_francisco_pizarro_2004", "sheppard_cuzco_2021", "titu_cusi_bauer_2005"): 1,
            ("historia_augusta_aurelian_loeb", "ric_online_268_276_history", "watson_aurelian_third_century"): 1,
            ("historic_england",): 3,
            ("historical_lexicon_montenegro_krusi", "jovicevic_montenegrin_code_1990", "national_museum_montenegro_history", "scekic_lekovic_premovic_balcanica_2015"): 2,
            ("historylink_union_gap_8124", "painter_oregon_volunteer_journals", "ruby_brown_indians_pacific_northwest"): 1,
            ("hrw_evil_days_afabet", "loc_ethiopia_country_study", "tareke_afabet_shire_2004"): 1,
            ("hrw_evil_days_total_war", "jude_war_state_formation_2022", "tareke_ethiopian_revolution_nakfa"): 1,
            ("hrw_evil_days_total_war", "ucalgary_secession_conflicts_eritrea"): 1,
            ("huang_liaotung_campaign_1619", "swope_military_collapse_ming"): 1,
            ("hummer_alemanni_suebi_1998", "sidonius_complete_poems_green_2022"): 1,
            ("hungarian_military_history_institute",): 2,
            ("hynd_imperial_incarceration_zulu_prisoners", "laband_divided_command_2003", "laband_historical_dictionary_zulu_wars"): 1,
            ("hynd_imperial_incarceration_zulu_prisoners", "laband_historical_dictionary_zulu_wars", "laband_natalia_ivuna_1980"): 1,
            ("ibn_al_jawzi_muntazam_translation", "tdv_islam_encyclopedia_besasiri"): 1,
            ("ignou_bhic132_invasions_resistance", "ignou_medieval_india_unit_12"): 2,
            ("ihp_huang_saerhu_artillery_2008", "swope_military_collapse_ming"): 1,
            ("illinois_dnr_apple_river_black_hawk_history", "patrick_jung_black_hawk_war_monograph", "us_army_cmh_black_hawk_campaign"): 1,
            ("international_encyclopedia_first_world_war", "latvia_estonia_military_heritage"): 1,
            ("iranica_abbas_i", "iranica_allahverdi_khan_1"): 1,
            ("iranica_abul_khayrids", "iranica_herat_medieval_history"): 1,
            ("iranica_abul_khayrids", "iranica_safavid_dynasty"): 1,
            ("iranica_abul_khayrids", "iranica_tahmasp_i"): 1,
            ("iranica_central_asia_vii", "iranica_ilbars_khan"): 1,
            ("iranica_damgan_town",): 1,
            ("iranica_iranian_history_chronology_1", "iranica_tahmasp_i"): 1,
            ("iranica_portugal_persia", "oman_news_agency_history"): 1,
            ("irish_historical_studies_warfare_1593_1601", "ucc_celt_four_masters"): 1,
            ("irish_military_archives",): 1,
            ("irish_military_archives", "ucc_atlas_irish_revolution"): 1,
            ("italian_army_civita_castellana",): 1,
            ("italian_army_garibaldi_biography", "treccani_mentana_1867"): 1,
            ("italian_army_rivista_militare_2007_3",): 1,
            ("italian_army_volturno_1860", "vive_museum_volturno_1860"): 1,
            ("italian_navy_history",): 1,
            ("iwbd",): 153,
            ("jaques_dictionary_battles_2006", "real_academia_historia_dbe"): 1,
            ("iwd",): 64,
            ("james_westfall_thompson_french_wars", "james_wood_kings_army"): 3,
            ("james_wood_kings_army", "musee_protestant"): 4,
            ("josephus_jewish_war_primary",): 1,
            ("jujuy_government_history",): 1,
            ("kagoshima_reimeikan_anglo_satsuma", "trull_cardiff_anglo_japanese_relations"): 1,
            ("kagoshima_reimeikan_hideyoshi_kyushu", "morton_olenik_japan_history_culture", "tokyo_historiographical_institute_iriki_148"): 1,
            ("kansas_historical_society", "us_national_park_service"): 1,
            ("karahan_hasan_pasha_egypt_1786", "tdv_islam_encyclopedia_ibrahim_bey"): 1,
            ("kate_fleet_early_ottoman_trade_1999", "luttrell_hospitallers_rhodes_prospects", "luttrell_zachariadou_hospitallers_turks"): 1,
            ("kenya_unesco_fort_jesus_nomination", "ucpress_inland_from_mombasa"): 1,
            ("kijo_official_second_takajo", "tokyo_historiographical_institute_iriki_148"): 1,
            ("kings_college_london_research", "saudipedia_king_abdulaziz_history", "university_east_anglia_repository"): 1,
            ("kralli_sellasia_encyclopedia", "polybius_histories"): 1,
            ("kumamoto_castle_official_history", "kumamoto_city_satsuma_rebellion"): 1,
            ("lambrick_sind_battles_1943", "napier_conquest_scinde_1845"): 1,
            ("lambrick_sind_battles_1943", "national_army_museum_scinde_medal", "sindh_heritage_miani_memorial"): 1,
            ("lang_son_provincial_history", "vietnam_national_museum_chi_lang", "vietnam_ndj_chi_lang"): 1,
            ("lavalle_francisco_pizarro_2004", "pbs_conquistadors_pizarro_2001", "sheppard_cuzco_2021"): 1,
            ("library_of_congress_country_studies", "university_east_anglia_repository"): 1,
            ("library_of_congress_federal_research", "university_east_anglia_repository"): 1,
            ("limerick_council_civil_war_history", "ucc_atlas_irish_revolution"): 1,
            ("livius_ancient_history_reference", "plutarch_parallel_lives"): 1,
            ("livy_ab_urbe_condita", "plutarch_parallel_lives"): 1,
            ("loc_chad_country_study_1990", "mays_oau_chad_1977_1982", "powell_frances_wars_chad_2020"): 1,
            ("loc_santo_domingo_1805_map", "reyes_clio_2022_dessalines"): 1,
            ("lucas_boeotian_military_organization_2023", "shipley_early_hellenistic_peloponnese_2018", "xenophon_hellenica_brownson"): 1,
            ("lucas_boeotian_military_organization_2023", "thucydides_peloponnesian_war_crawley"): 1,
            ("mac_evitt_afterlife_edessa", "mac_evitt_rough_tolerance"): 1,
            ("mack_holt_last_war_religion", "musee_protestant"): 1,
            ("major_et_al_margat_archaeology_2015", "michaudel_fall_rise_castles_2014"): 1,
            ("mark_oregon_encyclopedia_modoc_war", "nps_lava_beds_modoc_war_interpretation", "nps_thomas_wright_battlefield_interpretation", "thompson_modoc_war_1971"): 1,
            ("mcgrath_chinese_farm", "usmcu_crossing_under_fire"): 1,
            ("melis_stoke_rijmkroniek", "sayers_zierikzee_2006", "zierikzee_heritage_1304"): 1,
            ("ming_shi_yuan_chonghuan", "swope_military_collapse_ming"): 1,
            ("minnesota_historical_society",): 1,
            ("muhlenberg_shearer_vinegar_hill_account", "usfs_sheepeater_campaign_assessment"): 1,
            ("musee_armee_henri_de_guise", "robert_knecht_french_wars"): 2,
            ("musee_conde_coutras", "robert_knecht_french_wars"): 1,
            ("musee_protestant", "oxford_historical_research_french_fleet_1625"): 1,
            ("musei_civici_vicenza",): 1,
            ("museo_nazionale_storico_alpini",): 3,
            ("nas_ukraine_loyew_study",): 1,
            ("national_archives_krakow",): 1,
            ("national_army_museum",): 1,
            ("national_army_museum", "south_african_military_history_society"): 1,
            ("national_park_service_creek_war",): 1,
            ("national_park_service_revolution",): 1,
            ("nc_historical_marker_program_q5", "unc_press_encyclopedia_of_north_carolina"): 1,
            ("nc_historical_marker_program_q6", "unc_press_encyclopedia_of_north_carolina"): 1,
            ("nebraska_state_historical_society",): 1,
            ("nicol_byzantium_and_venice_chapter_10",): 1,
            ("nigeria_national_library_civil_war",): 1,
            ("nps_lava_beds_modoc_war_interpretation", "nrhp_captain_jacks_stronghold_nomination", "thompson_modoc_war_1971", "us_army_cmh_indian_wars_modocs", "wagner_captain_jacks_stronghold_1992"): 1,
            ("nps_lava_beds_modoc_war_interpretation", "nrhp_captain_jacks_stronghold_nomination", "thompson_modoc_war_1971", "wagner_captain_jacks_stronghold_1992"): 1,
            ("nzhistory",): 2,
            ("oakes_barons_war_thesis_2015", "prestwich_edward_i_1997"): 1,
            ("official_records_dove_creek_inquiry", "pool_dove_creek_study", "tsha_dove_creek_battle"): 1,
            ("oita_city_otomo_history", "tokyo_historiographical_institute_iriki_148"): 1,
            ("orosa_sulu_archipelago_1931", "us_war_department_1904_philippines"): 1,
            ("oszk_pressburg_907", "tortenelmi_szemle_pressburg"): 1,
            ("oxford_classical_dictionary_marcellus", "plutarch_marcellus_dryden_translation", "polybius_histories_book_2_shuckburgh", "rawlings_gallic_wars_225_222"): 1,
            ("oxford_german_history_kostick", "st_andrews_roche_second_crusade"): 1,
            ("papajik_historia_aperta_51", "vhu_pekar_kutna_brod_source_collection"): 3,
            ("parks_canada_northwest_resistance",): 2,
            ("pausanias_description_greece", "wallace_freedom_greeks_thesis"): 1,
            ("peru_bicentenario_cuzco_1814_readings", "peru_center_historical_military_apacheta"): 1,
            ("peru_bicentenario_junin_primary_part", "peruvian_army_junin_history"): 1,
            ("peru_bicentenario_torata_moquegua", "torata_municipal_history"): 1,
            ("phillips_navies_mediterranean_2000", "potter_michel_de_seure_2014"): 1,
            ("plutarch_parallel_lives", "polybius_histories"): 2,
            ("polish_land_forces_museum",): 1,
            ("polish_zpe_history",): 4,
            ("polito_pozzati_staffarda", "treccani_staffarda"): 1,
            ("pollack_air_power_six_day_war", "usni_six_day_war_1967"): 1,
            ("polybius_histories_book_2_shuckburgh", "rawlings_gallic_wars_225_222", "szubelak_telamon_2017"): 1,
            ("powell_fifth_crusade_military_history", "tandf_fifth_crusade_damietta"): 1,
            ("princeton_university_press", "university_east_anglia_repository"): 1,
            ("querengaesser_friedrich_hussites", "vhu_luzek_aussig"): 1,
            ("quinto_sol_unlpam_huaqui",): 1,
            ("raf_casps", "uk_london_gazette"): 2,
            ("rcahmw_coflein",): 1,
            ("rcahmw_coflein_battlefields",): 4,
            ("real_academia_historia_taranto", "treccani_taranto_1501_1502"): 1,
            ("republic_of_texas_official_rusk_battle_report", "thc_kickapoo_battlefield_marker", "tsha_cherokee_war"): 1,
            ("revue_deux_mondes_1851_gulina", "spanish_mod_memorial_infanteria_52"): 1,
            ("ria_proceedings_oneill_2021", "ucc_celt_beatha_aodha_ruaidh", "ucc_celt_four_masters"): 1,
            ("roma_capitale_villa_glori", "treccani_villa_glori_1867"): 1,
            ("royal_collection_military_maps_limerick", "ucc_celt_ireton_limerick_1651"): 1,
            ("royal_collection_siege_poitiers", "universite_poitiers_siege_1569"): 1,
            ("royal_museums_greenwich",): 1,
            ("sabanci_emin_pasha_dufile", "vandeleur_upper_nile_dufile"): 1,
            ("saudipedia_first_saudi_state",): 1,
            ("scov_dong_bo_dau", "vass_han_nom_dong_bo_dau", "vietnam_ndj_waterborne_warfare"): 1,
            ("serbian_ministry_of_defence",): 3,
            ("simms_dysert_odea_1979",): 1,
            ("somaliland_administration_history",): 1,
            ("sorbonne_byzantine_syria",): 1,
            ("south_african_history_online", "south_african_military_history_society"): 1,
            ("south_african_military_history_society",): 9,
            ("spicer_cycles_of_conquest_mayos_yaquis", "texas_band_of_yaqui_history", "troncoso_yaqui_mayo_tomo_i"): 1,
            ("sproule_livonian_mercenary_warfare", "viljandi_museum_fellin_history"): 1,
            ("st_andrews_after_empire", "transmediterranean_history_thietmar"): 1,
            ("swope_military_collapse_ming", "tang_dalinghe_military_thesis_2016"): 1,
            ("tcd_clontarf_1014", "ucc_celt_annals_ulster"): 1,
            ("texas_beyond_history_red_river_battles", "texas_historical_commission_red_river_guide"): 1,
            ("texas_beyond_history_red_river_battles", "tsha_lymans_wagontrain"): 1,
            ("texas_historical_commission",): 1,
            ("texas_state_historical_association",): 1,
            ("texas_state_historical_association_cherokee_war", "unt_miller_texas_indian_allies_thesis"): 1,
            ("thc_battle_creek_marker", "tsha_battle_creek_fight"): 1,
            ("tna_state_papers_hanmer_yellow_ford", "ucc_celt_beatha_aodha_ruaidh", "ucc_celt_four_masters"): 1,
            ("treccani_calatafimi_1860",): 1,
            ("treccani_catania_1849",): 1,
            ("treccani_milazzo_1860",): 1,
            ("treccani_risorgimento_1860",): 1,
            ("trinity_herman_reichenau_1044",): 1,
            ("tsha_little_wichita",): 1,
            ("ucc_atlas_irish_revolution",): 4,
            ("ucc_atlas_irish_revolution", "waterford_decies_journal"): 1,
            ("ucc_celt_annals_ulster",): 1,
            ("ucdp_conflict_termination",): 7,
            ("uk_parliament_hansard", "uk_war_office"): 2,
            ("uk_war_office",): 2,
            ("unc_belgrano_history",): 1,
            ("university_barcelona_repository",): 1,
            ("university_california_press",): 1,
            ("university_chicago_oriental_institute",): 1,
            ("university_of_oklahoma_press", "us_army_armor_history"): 1,
            ("university_oklahoma_press",): 1,
            ("us_army_armor_history",): 1,
            ("us_army_center_military_history",): 1,
            ("us_national_park_service", "wyoming_state_historical_society"): 1,
            ("us_naval_history_heritage_command",): 2,
            ("vass_vietnam_encyclopedia_lam_son", "vietnam_ndj_tot_dong"): 1,
            ("vietnam_government_news_dong_quan", "vietnam_national_museum_dong_quan"): 1,
            ("white_rose_research_online",): 1,
            },
        )
        hced_candidates = {
            event["hced_candidate_id"]
            for event in self.events
            if "hced_candidate_id" in event
        }
        self.assertTrue(APPROVED_HCED <= hced_candidates)
        self.assertTrue(BLOCKED_HCED.isdisjoint(hced_candidates))
        iwbd_candidates = {
            event["iwbd_candidate_id"]
            for event in self.events
            if "iwbd_candidate_id" in event
        }
        self.assertTrue({"iwbd-52-18-185", "iwbd-118-45-842"} <= iwbd_candidates)
        iwd_parents = {
            event["iwd_parent_war_id"]
            for event in self.events
            if "iwd_parent_war_id" in event
        }
        self.assertTrue({"15", "48"} <= iwd_parents)
        self.assertIn("1", iwd_parents)
        self.assertEqual(
            sum(len(event.get("iwd_components", ())) for event in self.events),
            100,
        )
        self.assertEqual(len(self.results["events"]), 5_414)

    def test_abtao_and_mishan_are_exact_candidate_keyed_events(self) -> None:
        abtao = self.events_by_id["iwbd_iwbd_52_18_185_abtao"]
        abtao_participants = {
            participant["entity_id"]: participant
            for participant in abtao["participants"]
        }
        self.assertEqual(
            set(abtao_participants),
            {
                "spanish_empire",
                "clio_ch_chile_rep_1_1812_3b31ba25",
                "clio_q419_1822_a6e12c5b",
            },
        )
        self.assertEqual(abtao_participants["spanish_empire"]["contribution"], 1.0)
        self.assertEqual(
            abtao_participants["clio_ch_chile_rep_1_1812_3b31ba25"]["contribution"],
            0.5,
        )
        self.assertEqual(
            abtao_participants["clio_q419_1822_a6e12c5b"]["contribution"],
            0.5,
        )
        self.assertTrue(
            all(
                participant["result_class"] == "stalemate_or_inconclusive"
                for participant in abtao["participants"]
            )
        )

        mishan = self.events_by_id["iwbd_iwbd_118_45_842_mishan"]
        self.assertEqual((mishan["year"], mishan["end_year"]), (1929, 1929))
        self.assertEqual(mishan["iwbd_duration_days"], "2")
        self.assertEqual(
            {participant["entity_id"] for participant in mishan["participants"]},
            {"soviet_union", "clio_cn_chinese_rep_1912_970b7032"},
        )

    def test_registry_absorption_and_saudi_migration_are_exact(self) -> None:
        for entity_id in (
            "united_states_colombia",
            "kingdom_saudi_arabia",
            "mutawakkilite_kingdom_yemen",
        ):
            self.assertIn(entity_id, self.registry_by_id)
            self.assertFalse(self.registry_by_id[entity_id].get("aliases"))

        self.assertNotIn("clio_q851_1936_a94f117c", self.registry_by_id)
        self.assertNotIn("clio_q1061488_1863_68491004", self.registry_by_id)
        self.assertIn("clio_q739_1866_25817025", self.registry_by_id)
        self.assertIn("clio_q1998401_1919_31438771", self.registry_by_id)

        saudi_event_ids = {
            event["id"]
            for event in self.events
            if any(
                participant["entity_id"] == "kingdom_saudi_arabia"
                for participant in event["participants"]
            )
        }
        self.assertEqual(
            saudi_event_ids,
            {
                "iwd_war_48_saudi_arabia_yemen_1934",
                "iwd_war_70_yom_kippur_1973",
                "iwd_war_82_gulf_war_1991",
            },
        )
        self.assertFalse(
            any(
                participant["entity_id"] == "clio_q851_1936_a94f117c"
                for event in self.events
                for participant in event["participants"]
            )
        )

    def test_source_expansion_is_narrow_and_canonical(self) -> None:
        self.assertEqual(len(self.sources), 1_457)
        self.assertEqual(
            len({source["source_family_id"] for source in self.sources}),
            1_193,
        )
        new_source_ids = {
            "colombia_constitution_1863",
            "state_department_colombia_history",
            "saudi_mofa_history",
            "uk_archives_yemen_1918",
            "oeaw_mutawakkilite_yemen",
        }
        by_id = {source["id"]: source for source in self.sources}
        self.assertTrue(new_source_ids <= set(by_id))
        for source_id in new_source_ids:
            self.assertEqual(
                by_id[source_id]["evidence_roles"],
                ["identity_boundary_or_context_reference"],
            )


if __name__ == "__main__":
    unittest.main()
