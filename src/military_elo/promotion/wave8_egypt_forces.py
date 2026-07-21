"""Isolated Wave 8 audit for HCED's literal ``Egypt`` label.

The source label spans pharaonic, Ptolemaic, medieval, khedival, colonial,
republican, and expeditionary actors.  It is therefore never resolved to a
timeless Egyptian identity.  This lane inventories all 58 literal rows,
recognizes 31 existing release owners, promotes 16 source-supported outcomes
through event-bounded formations, holds nine uncertain assertions, and
terminally excludes two assertions whose proposed outcomes are disproved.

Unknown is never converted to a draw.  The lane emits only independently
supported wins, opens no generic alias, and owns no adjacent spelling except
through explicit duplicate audits.
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
    "WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES",
    "WAVE8_EGYPT_FORCES_CONTRACT_IDS",
    "WAVE8_EGYPT_FORCES_CONTRACTS",
    "WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_EGYPT_FORCES_CURRENT_RELEASE_EVENT_AUDIT",
    "WAVE8_EGYPT_FORCES_ENTITIES",
    "WAVE8_EGYPT_FORCES_EXACT_LABEL_FUNNEL_AUDIT",
    "WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES",
    "WAVE8_EGYPT_FORCES_EXCLUSION_IDS",
    "WAVE8_EGYPT_FORCES_EXCLUSIONS",
    "WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS",
    "WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS",
    "WAVE8_EGYPT_FORCES_FINAL_AUDIT_SIGNATURE",
    "WAVE8_EGYPT_FORCES_HCED_TWIN_DISPOSITIONS",
    "WAVE8_EGYPT_FORCES_HOLD_IDS",
    "WAVE8_EGYPT_FORCES_HOLDS",
    "WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT",
    "WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_EGYPT_FORCES_IWD_AUDIT",
    "WAVE8_EGYPT_FORCES_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_EGYPT_FORCES_LOCATION_QUARANTINE_REASONS",
    "WAVE8_EGYPT_FORCES_NONPROMOTIONS",
    "WAVE8_EGYPT_FORCES_OUTCOME_OVERRIDES",
    "WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_EGYPT_FORCES_RESERVED_IDS",
    "WAVE8_EGYPT_FORCES_SOURCES",
    "WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSION_IDS",
    "WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS",
    "install_wave8_egypt_forces_entities",
    "install_wave8_egypt_forces_sources",
    "promote_wave8_egypt_forces_contracts",
    "validate_wave8_egypt_forces_identity_boundaries",
    "validate_wave8_egypt_forces_integration_dispositions",
    "validate_wave8_egypt_forces_queue_contracts",
    "wave8_egypt_forces_audit_signature",
    "wave8_egypt_forces_cohort_counts",
    "wave8_egypt_forces_counts",
    "wave8_egypt_forces_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 HCED literal Egypt exact-label audit"
_MODULE_OWNER = "military_elo.promotion.wave8_egypt_forces"
_EVENT_ID_PREFIX = "hced_wave8_egypt_forces_"
_EXACT_RAW_LABEL = "Egypt"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
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


WAVE8_EGYPT_FORCES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_egypt_brill_alexandria_1365",
        "The Crusade of Peter I of Cyprus and the Sack of Alexandria",
        "https://brill.com/display/book/edcoll/9789047416241/front-7.pdf",
        "Brill",
        "scholarly_book_chapter",
        "brill_peter_i_alexandria_1365",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_egypt_birmingham_alexandria_1365",
        "The Crusade of Peter I of Cyprus against Alexandria",
        "https://etheses.bham.ac.uk/id/eprint/6111/1/Ozkutlu15PhD.pdf",
        "University of Birmingham",
        "doctoral_thesis",
        "ozkutlu_peter_i_alexandria_thesis",
        outcome=True,
    ),
    _source(
        "wave8_egypt_tdv_al_salih_ayyub",
        "el-Melikus-Salih Eyyub",
        "https://islamansiklopedisi.org.tr/el-melikus-salih-eyyub",
        "TDV Encyclopedia of Islam",
        "scholarly_encyclopedia",
        "tdv_al_salih_ayyub",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_egypt_fordham_ascalon_1247",
        "Frederick II: Letter on the Loss of Jerusalem and Ascalon",
        "https://sourcebooks.web.fordham.edu/source/1228frederick2.asp",
        "Fordham University Internet Medieval Sourcebook",
        "edited_primary_source",
        "frederick_ii_ascalon_sourcebook",
        outcome=True,
    ),
    _source(
        "wave8_egypt_jstor_munzinger_awsa",
        "The Egyptian Colonial Path to Harar",
        "https://www.jstor.org/stable/j.ctv14h511.8",
        "JSTOR / Red Sea Press",
        "scholarly_book_chapter",
        "caulk_egyptian_path_harar",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_egypt_mprl_munzinger",
        "Werner Munzinger and Northeast African Exploration",
        "https://www.mprl-series.mpg.de/studies/14/6/index.html",
        "Max Planck Research Library",
        "scholarly_book_chapter",
        "mprl_munzinger_northeast_africa",
        outcome=True,
    ),
    _source(
        "wave8_egypt_sabanci_dufile",
        "The Late Ottoman Imperialist Endeavor in Central Africa: The Province of Equatoria (Hatt-I Istiva)",
        "https://research.sabanciuniv.edu/id/eprint/48734/1/10473116.pdf",
        "Sabanci University",
        "graduate_thesis",
        "sabanci_emin_pasha_dufile",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_egypt_vandeleur_dufile",
        "Campaigning on the Upper Nile and Niger",
        "https://upload.wikimedia.org/wikipedia/commons/5/59/Campaigning_on_the_upper_Nile_and_Niger_%28IA_campaigningonupp00vand%29.pdf",
        "Methuen / Internet Archive scan",
        "participant_primary_account",
        "vandeleur_upper_nile_dufile",
        outcome=True,
    ),
    _source(
        "wave8_egypt_andrews_megiddo_609",
        "The Babylonian Chronicle and the Ancient Calendar of Judah",
        "https://www.andrews.edu/library/car/cardigital/Periodicals/AUSS/1967-1/1967-1-02.pdf",
        "Andrews University Seminary Studies",
        "peer_reviewed_chronology_article",
        "thiele_megiddo_609_chronology",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_egypt_bu_megiddo_609",
        "Chosen City: Jerusalem in the Persian and Hellenistic Periods",
        "https://www.bu.edu/mzank/Jerusalem/cp/ChosenCity.html",
        "Boston University",
        "university_history_resource",
        "bu_chosen_city_megiddo_609",
        outcome=True,
    ),
    _source(
        "wave8_egypt_cambridge_montgisard",
        "The Leper King and His Heirs: Epilogue",
        "https://www.cambridge.org/core/books/abs/leper-king-and-his-heirs/epilogue/A4BD507B706309EE9B2F1D6055764848",
        "Cambridge University Press",
        "scholarly_monograph",
        "hamilton_leper_king_montgisard",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_egypt_ifpo_montgisard",
        "Saladin and the Battle of Montgisard",
        "https://books.openedition.org/ifpo/23621",
        "Presses de l'Ifpo / OpenEdition Books",
        "scholarly_book_chapter",
        "ifpo_saladin_montgisard",
        outcome=True,
    ),
    _source(
        "wave8_egypt_cambridge_battle_nile",
        "The Date of Julius Caesar's Departure from Alexandria",
        "https://www.cambridge.org/core/journals/journal-of-roman-studies/article/abs/date-of-julius-caesars-departure-from-alexandria1/5DD2BE963C9905415C97879B091036B5",
        "Journal of Roman Studies / Cambridge University Press",
        "peer_reviewed_chronology_article",
        "jrs_caesar_alexandria_departure",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_egypt_dickinson_battle_nile",
        "Eutropius 6.22: Caesar at Alexandria",
        "https://dcc.dickinson.edu/eutropius/6-22",
        "Dickinson College Commentaries",
        "edited_primary_source",
        "eutropius_dickinson_caesar_alexandria",
        outcome=True,
    ),
    _source(
        "wave8_egypt_hansard_sinkat",
        "Vote of Censure: Egypt and the Soudan",
        "https://api.parliament.uk/historic-hansard/lords/1884/feb/12/vote-of-censure",
        "UK Parliament Historic Hansard",
        "contemporary_parliamentary_record",
        "hansard_sinkat_1884",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_egypt_study_circle_sudan",
        "The Egyptian Campaigns in the Eastern Sudan, 1883-1885",
        "https://www.egyptstudycircle.org.uk/QCs/QC062.pdf",
        "Egypt Study Circle",
        "archival_campaign_chronology",
        "egypt_study_circle_eastern_sudan",
        outcome=True,
    ),
    _source(
        "wave8_egypt_tandf_damietta",
        "Oliver of Paderborn and the Frisians at the Siege of Damietta, 1218-1219",
        "https://www.tandfonline.com/doi/full/10.1080/14765276.2023.2271408",
        "Taylor & Francis",
        "peer_reviewed_history_article",
        "tandf_fifth_crusade_damietta",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_egypt_oxford_fifth_crusade",
        "The Damietta Crusade, 1217-1221: A Military History",
        "https://academic.oup.com/book/57913",
        "Oxford University Press",
        "scholarly_monograph",
        "powell_fifth_crusade_military_history",
        outcome=True,
    ),
    _source(
        "wave8_egypt_army_key_sinai",
        "Key to the Sinai: The Battles for Abu Ageila in 1956 and 1967",
        "https://www.armyupress.army.mil/Portals/7/combat-studies-institute/csi-books/key-to-the-sinai.pdf",
        "U.S. Army Combat Studies Institute",
        "official_military_history",
        "gawrych_key_to_sinai",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_egypt_pollack_six_day_war",
        "Air Power in the Six-Day War",
        "https://www.warfaresims.com/temp/AirOps_AirPowerInTheSixDayWar.pdf",
        "Journal of Strategic Studies",
        "peer_reviewed_military_history",
        "pollack_air_power_six_day_war",
        outcome=True,
    ),
    _source(
        "wave8_egypt_army_scouts_out",
        "Scouts Out! The Development of Reconnaissance Units in Modern Armies",
        "https://www.armyupress.army.mil/Portals/7/combat-studies-institute/csi-books/scouts_out.pdf",
        "U.S. Army Combat Studies Institute",
        "official_military_history",
        "army_scouts_out_rafah_case",
        outcome=True,
    ),
    _source(
        "wave8_egypt_oxford_gaza_history",
        "Gaza: A History",
        "https://pal.k0de.org/Filiu%2C%20Jean-Pierre%20-%20Gaza_%20A%20History%20-%20Oxford%20University%20Press%20%282014%29.pdf",
        "Oxford University Press",
        "scholarly_monograph",
        "filiu_gaza_history",
        outcome=True,
    ),
    _source(
        "wave8_egypt_usni_six_day_war",
        "The Six-Day War, 1967",
        "https://www.usni.org/magazines/proceedings/1968/june/six-day-war-1967",
        "U.S. Naval Institute Proceedings",
        "professional_military_history",
        "usni_six_day_war_1967",
        outcome=True,
    ),
    _source(
        "wave8_egypt_army_chinese_farm",
        "Sinai 1973: Israeli Maneuver Organization and the Battle of the Chinese Farm",
        "https://www.armyupress.army.mil/Portals/7/combat-studies-institute/csi-books/AnArmyAtWar_ChangeInTheMidstOfConflict.pdf",
        "U.S. Army Combat Studies Institute",
        "official_military_history",
        "mcgrath_chinese_farm",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_egypt_usmc_crossing_under_fire",
        "Crossing under Fire: The 1973 Suez Canal Crossing",
        "https://www.usmcu.edu/Outreach/Marine-Corps-University-Press/Expeditions-with-MCUP-digital-journal/Crossing-under-Fire/",
        "Marine Corps University Press",
        "official_military_history",
        "usmcu_crossing_under_fire",
        outcome=True,
    ),
    _source(
        "wave8_egypt_barilan_azotus",
        "Ashdod in the Assyrian Period",
        "https://lisa.biu.ac.il/sites/lisa/files/shared/Ashdod%20in%20the%20Assyrian%20Period%20Aster%20JNES%20Offprint.pdf",
        "Journal of Near Eastern Studies / Bar-Ilan University",
        "peer_reviewed_history_article",
        "aster_ashdod_assyrian_period",
    ),
    _source(
        "wave8_egypt_treccani_azotus",
        "Ashdod",
        "https://www.treccani.it/enciclopedia/asdod_%28Enciclopedia-dell%27-Arte-Antica%29/",
        "Treccani Enciclopedia dell'Arte Antica",
        "scholarly_encyclopedia",
        "treccani_ashdod",
    ),
    _source(
        "wave8_egypt_bmcr_cos",
        "Review: The Ptolemaic Navy and the Battle of Cos",
        "https://bmcr.brynmawr.edu/2001/2001.03.17/",
        "Bryn Mawr Classical Review",
        "scholarly_review",
        "bmcr_ptolemaic_navy_cos",
    ),
    _source(
        "wave8_egypt_uganda_journal_masindi",
        "Sir Samuel Baker and Bunyoro",
        "https://ufdcimages.uflib.ufl.edu/UF/00/08/08/55/00044/UF00080855_00044.pdf",
        "The Uganda Journal / University of Florida Digital Collections",
        "scholarly_historical_article",
        "uganda_journal_baker_bunyoro",
    ),
    _source(
        "wave8_egypt_masindi_profile",
        "Masindi District Tourism Profile",
        "https://masindi.go.ug/sites/default/files/MASINDI%20DISTRICT%20TOURISM%20%20UPDATED%20PROFILE%20PDF%20final.pdf",
        "Masindi District Local Government",
        "official_local_history",
        "masindi_district_kabalega_baker",
    ),
    _source(
        "wave8_egypt_ucla_chronology",
        "Ancient Egyptian Chronology",
        "https://uee.ucla.edu/chronology",
        "UCLA Encyclopedia of Egyptology",
        "scholarly_chronology",
        "ucla_egyptian_chronology",
    ),
    _source(
        "wave8_egypt_osu_megiddo",
        "The Battle of Megiddo",
        "https://ehistory.osu.edu/battles/megiddo",
        "Ohio State University eHistory",
        "university_history_resource",
        "osu_megiddo_thutmose",
    ),
    _source(
        "wave8_egypt_emory_napata",
        "Psamtik II and the Nubian Campaign",
        "https://etd.library.emory.edu/downloads/wd375x259?locale=en",
        "Emory University",
        "doctoral_dissertation",
        "emory_psamtik_nubian_campaign",
    ),
    _source(
        "wave8_egypt_michigan_napata",
        "Graffiti as Devotion along the Nile",
        "https://lsa.umich.edu/content/dam/kelsey-assets/kelsey-publications/pdfs/Graffiti-as-Devotion.pdf",
        "University of Michigan Kelsey Museum",
        "scholarly_monograph",
        "kelsey_napata_psamtik_campaign",
    ),
    _source(
        "wave8_egypt_cambridge_panion",
        "The Battle of Panion, 200 BC",
        "https://www.cambridge.org/core/books/abs/seleucid-army/battle-of-panion-200-bc/CC125ED635D11BD09F305B9D1BDA3E0A",
        "Cambridge University Press",
        "scholarly_monograph_chapter",
        "bar_kochva_panion_200",
    ),
    _source(
        "wave8_egypt_army_yom_kippur",
        "The 1973 Arab-Israeli War: The Albatross of Decisive Victory",
        "https://www.armyupress.army.mil/Portals/7/combat-studies-institute/csi-books/the-1973-arab-israeli-war.pdf",
        "U.S. Army Combat Studies Institute",
        "official_military_history",
        "gawrych_1973_arab_israeli_war",
    ),
    _source(
        "wave8_egypt_world_history_kadesh",
        "Battle of Kadesh",
        "https://www.worldhistory.org/Kadesh/",
        "World History Encyclopedia",
        "editorially_reviewed_reference",
        "whe_kadesh_review",
    ),
    _source(
        "wave8_egypt_hansard_tokar",
        "Egypt and the Soudan: The Fall of Tokar",
        "https://hansard.parliament.uk/Commons/1884-02-25/debates/b072137c-ea9e-4cdd-858d-76a9f670b514/CommonsChamber",
        "UK Parliament Historic Hansard",
        "contemporary_parliamentary_record",
        "hansard_tokar_1884",
    ),
)


_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_EGYPT_FORCES_SOURCES}


def _entity(
    entity_id: str,
    name: str,
    low: int,
    high: int,
    region: str,
    source_ids: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": "event_bounded_formation",
        "start_year": low,
        "end_year": high,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            f"Event-bounded participant in {name}. It is not a generic polity or "
            "a timeless national force. No rating is inherited by a dynasty, "
            "predecessor, successor, namesake formation, modern state, or generic "
            "Egypt outside this event window."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_EGYPT_FORCES_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity("peter_i_alexandria_crusade_force_1365", "Peter I's Alexandria crusade force (1365)", 1365, 1365, "Alexandria, Egypt", {"wave8_egypt_brill_alexandria_1365", "wave8_egypt_birmingham_alexandria_1365"}),
    _entity("mamluk_alexandria_defenders_1365", "Mamluk defenders of Alexandria (1365)", 1365, 1365, "Alexandria, Egypt", {"wave8_egypt_brill_alexandria_1365", "wave8_egypt_birmingham_alexandria_1365"}),
    _entity("al_salih_ayyub_ascalon_siege_force_1247", "al-Salih Ayyub's Ascalon siege force (1247)", 1247, 1247, "Ascalon", {"wave8_egypt_tdv_al_salih_ayyub", "wave8_egypt_fordham_ascalon_1247"}),
    _entity("frankish_ascalon_garrison_1247", "Frankish garrison of Ascalon (1247)", 1247, 1247, "Ascalon", {"wave8_egypt_tdv_al_salih_ayyub", "wave8_egypt_fordham_ascalon_1247"}),
    _entity("afar_issa_awsa_defenders_1875", "Afar and Issa defenders at Awsa (1875)", 1875, 1875, "Awsa, Ethiopia", {"wave8_egypt_jstor_munzinger_awsa", "wave8_egypt_mprl_munzinger"}),
    _entity("munzinger_awsa_expedition_1875", "Munzinger's Egyptian Awsa expedition (1875)", 1875, 1875, "Awsa, Ethiopia", {"wave8_egypt_jstor_munzinger_awsa", "wave8_egypt_mprl_munzinger"}),
    _entity("dufile_garrison_1888", "Dufile garrison (1888)", 1888, 1888, "Dufile, Uganda", {"wave8_egypt_sabanci_dufile", "wave8_egypt_vandeleur_dufile"}),
    _entity("umar_salih_dufile_force_1888", "Umar Salih's Mahdist force at Dufile (1888)", 1888, 1888, "Dufile, Uganda", {"wave8_egypt_sabanci_dufile", "wave8_egypt_vandeleur_dufile"}),
    _entity("necho_ii_megiddo_force_609_bce", "Necho II's force at Megiddo (609 BCE)", -609, -609, "Megiddo", {"wave8_egypt_andrews_megiddo_609", "wave8_egypt_bu_megiddo_609"}),
    _entity("josiah_judah_force_609_bce", "Josiah's Judahite force at Megiddo (609 BCE)", -609, -609, "Megiddo", {"wave8_egypt_andrews_megiddo_609", "wave8_egypt_bu_megiddo_609"}),
    _entity("baldwin_iv_montgisard_force_1177", "Baldwin IV's Jerusalem-Templar force at Montgisard (1177)", 1177, 1177, "Montgisard", {"wave8_egypt_cambridge_montgisard", "wave8_egypt_ifpo_montgisard"}),
    _entity("saladin_montgisard_campaign_force_1177", "Saladin's campaign force at Montgisard (1177)", 1177, 1177, "Montgisard", {"wave8_egypt_cambridge_montgisard", "wave8_egypt_ifpo_montgisard"}),
    _entity("caesarian_pergamene_nile_coalition_47_bce", "Caesarian-Pergamene coalition at the Nile (47 BCE)", -47, -47, "Nile Delta", {"wave8_egypt_cambridge_battle_nile", "wave8_egypt_dickinson_battle_nile"}),
    _entity("ptolemy_xiii_nile_army_47_bce", "Ptolemy XIII's army at the Nile (47 BCE)", -47, -47, "Nile Delta", {"wave8_egypt_cambridge_battle_nile", "wave8_egypt_dickinson_battle_nile"}),
    _entity("osman_digna_sinkat_force_1884", "Osman Digna's force at Sinkat (1884)", 1884, 1884, "Sinkat, Sudan", {"wave8_egypt_hansard_sinkat", "wave8_egypt_study_circle_sudan"}),
    _entity("sinkat_egyptian_garrison_1884", "Egyptian garrison of Sinkat (1884)", 1884, 1884, "Sinkat, Sudan", {"wave8_egypt_hansard_sinkat", "wave8_egypt_study_circle_sudan"}),
    _entity("fifth_crusade_damietta_siege_host_1218_1219", "Fifth Crusade siege host at Damietta (1218-1219)", 1218, 1219, "Damietta, Egypt", {"wave8_egypt_tandf_damietta", "wave8_egypt_oxford_fifth_crusade"}),
    _entity("ayyubid_damietta_garrison_1218_1219", "Ayyubid garrison of Damietta (1218-1219)", 1218, 1219, "Damietta, Egypt", {"wave8_egypt_tandf_damietta", "wave8_egypt_oxford_fifth_crusade"}),
    _entity("israeli_abu_ageila_force_1967", "Israeli force at Abu Ageila (1967)", 1967, 1967, "Abu Ageila, Sinai", {"wave8_egypt_army_key_sinai", "wave8_egypt_pollack_six_day_war"}),
    _entity("egyptian_abu_ageila_force_1967", "Egyptian force at Abu Ageila (1967)", 1967, 1967, "Abu Ageila, Sinai", {"wave8_egypt_army_key_sinai", "wave8_egypt_pollack_six_day_war"}),
    _entity("israeli_rafah_force_1967", "Israeli force at Rafah (1967)", 1967, 1967, "Rafah", {"wave8_egypt_army_scouts_out", "wave8_egypt_pollack_six_day_war"}),
    _entity("egyptian_rafah_force_1967", "Egyptian force at Rafah (1967)", 1967, 1967, "Rafah", {"wave8_egypt_army_scouts_out", "wave8_egypt_pollack_six_day_war"}),
    _entity("israeli_gaza_force_1967", "Israeli force in the capture of Gaza (1967)", 1967, 1967, "Gaza", {"wave8_egypt_oxford_gaza_history", "wave8_egypt_pollack_six_day_war"}),
    _entity("egyptian_gaza_force_1967", "Egyptian force in the defense of Gaza (1967)", 1967, 1967, "Gaza", {"wave8_egypt_oxford_gaza_history", "wave8_egypt_pollack_six_day_war"}),
    _entity("israeli_jebel_libni_force_1967", "Israeli force at Jebel Libni (1967)", 1967, 1967, "Jebel Libni, Sinai", {"wave8_egypt_army_key_sinai", "wave8_egypt_pollack_six_day_war"}),
    _entity("egyptian_jebel_libni_force_1967", "Egyptian force at Jebel Libni (1967)", 1967, 1967, "Jebel Libni, Sinai", {"wave8_egypt_army_key_sinai", "wave8_egypt_pollack_six_day_war"}),
    _entity("israeli_mitla_interdiction_force_1967", "Israeli interdiction force at Mitla Pass (1967)", 1967, 1967, "Mitla Pass, Sinai", {"wave8_egypt_usni_six_day_war", "wave8_egypt_pollack_six_day_war"}),
    _entity("egyptian_mitla_retreat_force_1967", "Egyptian retreat force at Mitla Pass (1967)", 1967, 1967, "Mitla Pass, Sinai", {"wave8_egypt_usni_six_day_war", "wave8_egypt_pollack_six_day_war"}),
    _entity("israeli_bir_gafgafa_force_1967", "Israeli force at Bir Gafgafa (1967)", 1967, 1967, "Bir Gafgafa, Sinai", {"wave8_egypt_army_key_sinai", "wave8_egypt_pollack_six_day_war"}),
    _entity("egyptian_bir_gafgafa_force_1967", "Egyptian force at Bir Gafgafa (1967)", 1967, 1967, "Bir Gafgafa, Sinai", {"wave8_egypt_army_key_sinai", "wave8_egypt_pollack_six_day_war"}),
    _entity("israeli_chinese_farm_force_1973", "Israeli force at Chinese Farm (1973)", 1973, 1973, "Chinese Farm, Sinai", {"wave8_egypt_army_chinese_farm", "wave8_egypt_usmc_crossing_under_fire"}),
    _entity("egyptian_chinese_farm_defenders_1973", "Egyptian defenders at Chinese Farm (1973)", 1973, 1973, "Chinese Farm, Sinai", {"wave8_egypt_army_chinese_farm", "wave8_egypt_usmc_crossing_under_fire"}),
)


WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES: dict[str, str] = {
    "hced-Abu Ageila1956-1": "b1749fe5be1900e99ec5386e634e70d297c544fc6acac9006f86008133029ddb",
    "hced-Abu Ageila1967-1": "a7966876a65e460224171485c687f1c3785a7e391bb3bb52b64c35d4982518f1",
    "hced-Acre1831-1": "2203bb8e6a8405d48b3b4bbc57276c85bfe12dfb3fec5cc1dd0a7d501e320119",
    "hced-Acre1840-1": "843c9cda832b0893ecd52aa99035adae36e1ff58c94872e3ef6be1e5e222c570",
    "hced-Alexandria-48-1": "a6db82f40c262068522699bcc94fa3bd8d2e7e10b722a8eff668fbddd326ac5d",
    "hced-Alexandria1167-1": "08efcecd6ddaf0441da0b41bc9c0b1d5447403480e23384f6dc1a25535266239",
    "hced-Alexandria1365-1": "9e6d3a6ed84be3f18a43b0a6e3a6641ac1a29127547527e1499c813a0c88e33b",
    "hced-Alexandria1882-1": "5c064cdfb312fe7850ef25b4086e0aa36cc413ba289bc01f0a1cd98eaa0b0a32",
    "hced-Ascalon1123-1": "a171defc571446fdab9ccadefe06ceeeeb3f32031581d325e0bcc08ea2cb2d51",
    "hced-Ascalon1247-1": "96edaef632dfb8471c32c521375ea72573605d087bdf315de0bbbec232017779",
    "hced-Asluj1948-1": "5ddff8ea5ab61e32dce6817dd4890eb08630102c51a78cad59f108ee9e7ef457",
    "hced-Aussa1875-1": "ad774d9137eab5f0b21efc8b6fc05ce4a38b85f9dfad6f14e03e7ba48cd441e5",
    "hced-Azotus-659-1": "5a6ef97fecc27bf7a5f37aede95b6da9f6412551b42e8d3b167618db14d0daf2",
    "hced-Beersheba1948-1": "f3dfb1ee75cbafb3d25e85aeac4603e5c92e2e992fc761ef2a66e0586b38a757",
    "hced-Beirut1840-1": "0aa4025160e8dcc1b833d662ea3ca2ffb195e624e36ad75d7024c9e7299cb44a",
    "hced-Belen1832-1": "485ab2c3d85191eef7b1098d76cd56969267a9f7be11d64e958a900d47e691a8",
    "hced-Bir Gafgafa1967-1": "59db1b710230ead71eb882ceb04db5e279e206515d23246639522a7ab64a2f8c",
    "hced-Chinese Farm1973-1": "68f0a3272b164f9f877a9833e07adf237c231c807fd15dc8dde3cc05c4714807",
    "hced-Cos-254-1": "0781dc4cf0ccf333ce99cc9b8c6bbfe4cbeddd42565d15d5999522208d5455c1",
    "hced-Damietta1218-1": "bdf6d2f4ce6b08ea1fa519f3132b2bb35d740b6961a7462daa82fb0499d48458",
    "hced-Dufile1888-1": "aaafa0d57e732f7741a3fdefebe8ae214d2a279b15b03d3d5654b1c10a5a602e",
    "hced-Faluja1948-1": "b9cff0fb8da3cc4add122af5c09e47d6ddeaa8301e17acc91444020ffd9859e8",
    "hced-Fariskur1250-1": "f99d6ce6ee08cfdedb881ccc60f781075aee290d370b739261653c7301f8764d",
    "hced-Gaza1956-1": "7402eefa8544094b576efb51676f791812d37358200522587c054d61ff228400",
    "hced-Gaza1967-1": "bc8338aed612cbcfc5f393263814abafdad450622220214dbed3e91e4e9bd34d",
    "hced-Gundet1875-1": "8f22fbf4cdf8ec20a30664e55356200e9ac7c1183509681b9d13927bd855c4b6",
    "hced-Gura1876-1": "838ffe1fe23e7d6e0bd41c1cbf779a5f2150d6afc2e8cba858203f5898dfded9",
    "hced-Homs1832-1": "976363b14d328473d40c211f1f97acbd8f2b95bdbdef63e399415b86b10d4ad2",
    "hced-Jebel Libni1967-1": "85488388d4947d4f96f26630f38e6ab7e471d05f00c52601ac9d64e76cdfedcb",
    "hced-Kadesh-1275-1": "f4beff55c2138b889db199a18d4926e8ad3754be7a817f1d970fccd69e961531",
    "hced-Kassassin1882-1": "1ce9ae88ddf2032a146b07b51e4371598ef2306bd36e2177defc1b39c9164de7",
    "hced-Konya1832-1": "11aa2f2bba76355c3ef7b0888be2575bf4419d5c03a4f2c8b98a5bd85ef7e21b",
    "hced-Masindi1872-1": "7189079104efb18a269ae3ee0f1193675e406b20eeada769cd3c4c64cb642726",
    "hced-Megiddo-1468-1": "c2986da33d2ede9d02806d69228e99e92790194b2fbf26da607cbe36334a5e43",
    "hced-Megiddo-609-1": "4f813a4b117b75ecd42f8a7d67837b51948646b109b22a2380fdbbb154a369dd",
    "hced-Mitla Pass1956-1": "523c157b486b138268b5f6c3310058815967127beb3c29d1c535db94fe963ba5",
    "hced-Mitla Pass1967-1": "d98e513222c8193ea28d3d5e5517c50c88637479e4799a0334f9e8a16da50eaa",
    "hced-Montgisard1177-1": "e17a7d5d112712c6964b233fc72830f790a359b81c881ac3fd65a3949221af4b",
    "hced-Napata-593-1": "1bd577688524c0cc872bb5d1f583b67ffeeaaeb7047b935fdb30d67af7b8cb26",
    "hced-Navarino1825-1": "601fac2da0d8817aa6c660245eb7ef3fb2030a540561c0df09d9b3fe9b5b0baa",
    "hced-Nezib1839-1": "71c1a4e481195d9a80d6e316a3ac6ca91f0e590e0732c53b55db6d4c9e2541ea",
    "hced-Nile-47-1": "f88231f6c4341083fb03cb8741c90631d3de0a10b4edee2f00867f5346213ca9",
    "hced-Paneas-198-1": "64d054e173e56c6ff2f64071850d3bb00d13f1ee72cb7ba339d1e0c92734a7eb",
    "hced-Pelusium-525-1": "d83df32062ede6e630c095980ca8742f7ecba7b4aa9d3aa4820b3e73e3ddf64b",
    "hced-Pelusium640-1": "2056d0e32202789f3efce49db7e1380496768c006296b3603d393f4cc174a878",
    "hced-Port Said1956-1": "2c5034f6dc6b6858e924432c4324737ea3872cca5baace77f42f48d1b4e700b2",
    "hced-Pyramids1798-1": "1009989a5cd59f69b286a66ade6959b727517638297d486f7e35ed0591d06789",
    "hced-Rafa1956-1": "da81dc0ce98958b5d1ae72db66b7718540d660ba76d12cc7b815906690fabec5",
    "hced-Rafa1967-1": "e02c8b7de0f35d3b08f4365cc6e7f9f267ad89de0dd03171766ac65206286d68",
    "hced-Sinkat1884-1": "2602ddb860c460993ac414d65742ca93e7bdaf35526dd018fb1c059c57f04122",
    "hced-Straits of Tiran1956-1": "6ae500acdc7f96d77a377dae293d4a7f6b5d7ea5eb3fddc5928d703454e5e31e",
    "hced-Suez Canal (1st)1973-1": "de182498c56f50c3f33afbeaf9e5f371601e7235d9017f8e34063345ecb4e989",
    "hced-Suez Canal (2nd)1973-1": "ba1185cbd8a93139aaccdbd666cdac1635c462165c5addfe7d708223d5648d0b",
    "hced-Suez Canal (3rd)1973-1": "59916bd6ac011998c281f6091229306f667c2644e5a0766f3d8345a01a44532a",
    "hced-Tel-el-Kebir1882-1": "1bf1cfdc6f9cd48f9d5c012fade8c67737e828deec777fe1a8f98a681f6522cb",
    "hced-Tel-el-Maskhuta1882-1": "b73e0e4613a4f433c626fe9c26ba0bb5e85a53febb7f2fe000cbf8057fd41f5b",
    "hced-Tokar1883-1": "8c50131d3230eac5c0c0a1d2c411f052a09f213465aaccf7681bea192da690c0",
    "hced-al, Damietta1218-1219-1": "ec6e1a579469365ae3e2989e81bef85451288e6cdc1168dc0e79e9ecefc76ec8",
}


WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES: dict[str, str] = {
    "hced-Alexandria1798-1": "9e6416b28654cf8894fd1af4fdbfe597eca128709375e06b6d6d50df33f66386",
    "hced-Andros-245-1": "4e947f4d8b747454250c16e6a83b4bc00cf0d288dae964215bafdaa86b0570a1",
    "hced-Antioch, Syria-244-1": "cc8655fd087d3b1b2c9630b1a452aa1f2fed0cbe6791bc34961d23cd7f919815",
    "hced-Ashmoun Canal1221-1": "40591f29ced27854f46b796d9133b88baa4b0a84472ec926e14df1888a3ca18e",
    "hced-Ashmoun Canal1249-1": "1dffd9977e17d43b136ca252bac31a129f868847a4586d8aa07bbacdb992654b",
    "hced-Athens, Greece-264-1": "5c04e70ab1eac2d55dbf186a4536e8cae700bc277b230d956617a78c92dcaa89",
    "hced-Carchemish-605-1": "f5c94327fd18c4d490e3833dd693160f93438a1a0ac1b6819f8a18cfd71069f3",
    "hced-Chaul1508-1": "a6ed9eef765cd889554c98068cb0ca7f5a8cf834339dab4f8de6051e7ad1a192",
    "hced-Corinth, Greece-265-1": "d20ae01f3d2ffb41128bcaab8f13c501afbd0ac57e434f2ec8e14141b8d5cf17",
    "hced-Desert Storm1991-1": "77a26aea788cd13ceff95eb0ffc8bc14492c57f5c6142eaa2f8bd8114bc3980b",
    "hced-Diu1509-1": "57af48da39c8da1a5835fd12e919b18cb6b4b6ff3c6af1a6da339acd2929ab36",
    "hced-El Obeid1883-1": "47270dce86838a60d35e9a86809682d188e04d43579fdfbc556d13c16b3435c2",
    "hced-Elasa1167-1": "5dcf271f7e7f6424815c6820d8e0b4699013ec768819cb936ab2f9016d46ad03",
    "hced-Eltekeh-700-1": "c7caa03aab7ba1f23f922ab54d8b3600b6b2cfad9ae2f055f869994b56e1f486",
    "hced-Er Ridisiya1799-1": "f685fa5a0156beeadb7a5012ca429bdb3ad89b5afd93dfe732dbc9c7035d4363",
    "hced-Hejaz1812-1": "78b74e6f090e16ba418759c79d7142f1d7424a2f7daec2e9769e1a33f4d4e0ae",
    "hced-Jerusalem1098-1": "c1f43f43abcb6a50cd5cb8f0cbb3de4bb4d4e73a33188335a507d4adc3186c8f",
    "hced-Jerusalem1099-1": "011d3abe4ef0a841cd9799c1e50e787daa438a7a6e1d765d17e08a120cc5c90b",
    "hced-Joppa1102-1": "f949c96973fd466b71e73ef79229585dc1173dd1cc89ba7aee9897cd9e1ed91a",
    "hced-Kashgal1883-1": "48d9e02777714c84f2ff8e1a7bcc1f4082f01b5f8407253e333b8189b45c6c91",
    "hced-Khartoum1884-1": "03764638dffcb4f44bddd30157c091ee89fc9daede4d832b9734f4ae5334725d",
    "hced-Krommydi1825-1": "2aa67e92bf11b95c44ca990a1afcc762e523ce038f6073ac60fc322463c88620",
    "hced-La Forbie1244-1": "20a67c1b608dda91d32ee2b32531da0ecd41898432d1b38270d37e33c334a487",
    "hced-Mansura, Egypt1250-1": "723421a2f86036258e5e0a2c1e88520083e2c479833a8d54b8acbd1484a47049",
    "hced-Marj Dabik1516-1": "0eb60113f47e6f8f89cf6f4d7c016e1fc6c35cbe80efc459d9a871d31cfb2fc6",
    "hced-Mount Tabor1799-1": "3a01784e5f849b2e5bc53f3943f6150f59f8f9d572415c1d370bbb7de102fa2a",
    "hced-Navarino1827-1": "80213c4c25b864991d7d6ed27d76391f9f8871dcb0cd5598d2a7fd5da9d76420",
    "hced-Rahmaniyya1786-1": "460d690c31cc52c7743bbb8e112e8048df1d72ac07f53175bfd53c921ab065db",
    "hced-Raphia-217-1": "1648d7bcfa6325a5d72cf951cca30277b623c76723ff788e606a3921a59e833e",
    "hced-Rhodes-305-1": "b9e7bcd5fa596cfce32386380e7e0e78de307d7188b4641d6eb37c5b589318a7",
    "hced-Ridanieh1517-1": "260940e4918a9eb6c58cf7167e21ab665751a0668678db421abba26ef30072f7",
    "hced-Samhud1799-1": "7ec8600f16e89fd6efbbbffacf2663e272fa7a2d6ee1c5663e8f8daee9693b2d",
    "hced-Sediman1798-1": "d51eabdd58fb3cd1293e8d320590eaee927fe5a007abc7c49ff518366741812f",
    "hced-Shubra Khit1798-1": "6dc896a596bc505f61b01a80a5880f0e1e1cab683feafbf436b75baea7f37120",
    "hced-Sphakteria1825-1": "7ee40c7e0228e60cab33566f9340ada59c4d0febbca6ce4dee96ae8df7adaad6",
    "hced-Thymbria-546-1": "b497b75a8d6873fc109f2dc4e3f11ea15c274a9289cebc0365e363b20fe60608",
    "hced-Tokar1891-1": "80340496f1671488fe8ab8c9ae0c1e3124ab109cb0d75145490e2310b1e8fe2d",
    "hced-Toski1889-1": "8d93cc0484f65bd00d42d1d3c15e8ce93872a138921ddb2efab354cca52680ec",
}


def _canonical(
    name: str,
    low: int,
    high: int,
    date_text: str,
    *,
    date_precision: str,
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "name": name,
        "year_low": low,
        "year_high": high,
        "date_text": date_text,
        "date_precision": date_precision,
        "granularity": granularity,
        "canonical_key": f"{_slug(name)}:{low}:{high}",
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    war_type: str,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, source_ids)))
    return {
        "raw_row_sha256": WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "event_bounded_exact_forces",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_EGYPT_FORCES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Alexandria1365-1": _contract(
        "hced-Alexandria1365-1",
        _canonical("Sack of Alexandria (1365)", 1365, 1365, "9-16 October 1365", date_precision="day_range", granularity="assault_and_sack"),
        "medieval_egypt",
        {"peter_i_alexandria_crusade_force_1365"},
        {"mamluk_alexandria_defenders_1365"},
        {"wave8_egypt_brill_alexandria_1365", "wave8_egypt_birmingham_alexandria_1365"},
        "Peter I's crusading host captured and sacked Alexandria before withdrawing. The contract rates that bounded assault, not Cyprus or Mamluk Egypt across time.",
        confidence=0.91,
        war_type="interstate_religious",
    ),
    "hced-Ascalon1247-1": _contract(
        "hced-Ascalon1247-1",
        _canonical("Siege and capture of Ascalon (1247)", 1247, 1247, "1247", date_precision="year", granularity="siege_capture"),
        "medieval_egypt",
        {"al_salih_ayyub_ascalon_siege_force_1247"},
        {"frankish_ascalon_garrison_1247"},
        {"wave8_egypt_tdv_al_salih_ayyub", "wave8_egypt_fordham_ascalon_1247"},
        "The reviewed sources independently attest al-Salih Ayyub's recovery of Ascalon from its Frankish defenders in 1247.",
        confidence=0.88,
        war_type="interstate_religious",
    ),
    "hced-Aussa1875-1": _contract(
        "hced-Aussa1875-1",
        _canonical("Destruction of Munzinger's Awsa expedition", 1875, 1875, "14-15 November 1875", date_precision="day_range"),
        "khedival_periphery",
        {"afar_issa_awsa_defenders_1875"},
        {"munzinger_awsa_expedition_1875"},
        {"wave8_egypt_jstor_munzinger_awsa", "wave8_egypt_mprl_munzinger"},
        "Afar and Issa fighters destroyed Munzinger's expedition. The HCED country tag says Djibouti, but the Awsa action was in present-day Ethiopia and is quarantined.",
        confidence=0.92,
        war_type="colonial_anti_colonial",
    ),
    "hced-Dufile1888-1": _contract(
        "hced-Dufile1888-1",
        _canonical("Battle of Dufile", 1888, 1888, "26-28 November 1888", date_precision="day_range"),
        "equatoria_expeditionary",
        {"dufile_garrison_1888"},
        {"umar_salih_dufile_force_1888"},
        {"wave8_egypt_sabanci_dufile", "wave8_egypt_vandeleur_dufile"},
        "The Dufile garrison repelled Umar Salih's Mahdist force after severe fighting. Dufile is in present-day Uganda, not the queued Sudan country tag.",
        confidence=0.88,
        war_type="colonial_anti_colonial",
    ),
    "hced-Megiddo-609-1": _contract(
        "hced-Megiddo-609-1",
        _canonical("Battle of Megiddo (609 BCE)", -609, -609, "May or June 609 BCE", date_precision="month_uncertain"),
        "ancient_egypt",
        {"necho_ii_megiddo_force_609_bce"},
        {"josiah_judah_force_609_bce"},
        {"wave8_egypt_andrews_megiddo_609", "wave8_egypt_bu_megiddo_609"},
        "Necho II's force defeated Josiah's blocking force; Josiah was killed or mortally wounded. The month uncertainty is preserved.",
        confidence=0.87,
        war_type="interstate_limited",
    ),
    "hced-Montgisard1177-1": _contract(
        "hced-Montgisard1177-1",
        _canonical("Battle of Montgisard", 1177, 1177, "25 November 1177", date_precision="day"),
        "medieval_egypt",
        {"baldwin_iv_montgisard_force_1177"},
        {"saladin_montgisard_campaign_force_1177"},
        {"wave8_egypt_cambridge_montgisard", "wave8_egypt_ifpo_montgisard"},
        "Baldwin IV's Jerusalem-Templar force defeated Saladin's campaign army. Neither raw coalition is collapsed into a timeless polity.",
        confidence=0.94,
        war_type="interstate_religious",
    ),
    "hced-Nile-47-1": _contract(
        "hced-Nile-47-1",
        _canonical("Battle of the Nile (47 BCE)", -47, -47, "early 47 BCE", date_precision="part_of_year"),
        "ptolemaic_civil_war",
        {"caesarian_pergamene_nile_coalition_47_bce"},
        {"ptolemy_xiii_nile_army_47_bce"},
        {"wave8_egypt_cambridge_battle_nile", "wave8_egypt_dickinson_battle_nile"},
        "Caesar's reinforced coalition defeated Ptolemy XIII's army and ended the Alexandrian campaign; the exact day is not asserted.",
        confidence=0.89,
        war_type="internal_intervention",
    ),
    "hced-Sinkat1884-1": _contract(
        "hced-Sinkat1884-1",
        _canonical("Fall of Sinkat", 1884, 1884, "8 February 1884", date_precision="day", granularity="siege_termination"),
        "mahdist_war",
        {"osman_digna_sinkat_force_1884"},
        {"sinkat_egyptian_garrison_1884"},
        {"wave8_egypt_hansard_sinkat", "wave8_egypt_study_circle_sudan"},
        "After a prolonged siege, the Sinkat garrison attempted a breakout and was destroyed; the bounded siege termination is rated.",
        confidence=0.93,
        war_type="internal_rebellion",
    ),
    "hced-al, Damietta1218-1219-1": _contract(
        "hced-al, Damietta1218-1219-1",
        _canonical("Siege and capture of Damietta (1218-1219)", 1218, 1219, "May 1218-November 1219", date_precision="month_range", granularity="siege_capture"),
        "fifth_crusade",
        {"fifth_crusade_damietta_siege_host_1218_1219"},
        {"ayyubid_damietta_garrison_1218_1219"},
        {"wave8_egypt_tandf_damietta", "wave8_egypt_oxford_fifth_crusade"},
        "The Fifth Crusade siege host captured Damietta after the attested 1218-1219 siege. This is distinct from the mis-keyed HCED Damietta1218 row whose locked year is 1249.",
        confidence=0.94,
        war_type="interstate_religious",
    ),
    "hced-Abu Ageila1967-1": _contract(
        "hced-Abu Ageila1967-1",
        _canonical("Battle of Abu Ageila (1967)", 1967, 1967, "5-6 June 1967", date_precision="day_range"),
        "six_day_war_sinai",
        {"israeli_abu_ageila_force_1967"},
        {"egyptian_abu_ageila_force_1967"},
        {"wave8_egypt_army_key_sinai", "wave8_egypt_pollack_six_day_war"},
        "The U.S. Army study, informed by Israeli commanders and Egyptian military historians, identifies a decisive Israeli victory at Abu Ageila.",
        confidence=0.95,
        war_type="interstate_limited",
    ),
    "hced-Rafa1967-1": _contract(
        "hced-Rafa1967-1",
        _canonical("Battle of Rafah (1967)", 1967, 1967, "5 June 1967", date_precision="day"),
        "six_day_war_sinai",
        {"israeli_rafah_force_1967"},
        {"egyptian_rafah_force_1967"},
        {"wave8_egypt_army_scouts_out", "wave8_egypt_pollack_six_day_war"},
        "Israeli forces broke through the Egyptian position at Rafah and compelled its retreat; the contract is local and tactical.",
        confidence=0.88,
        war_type="interstate_limited",
    ),
    "hced-Gaza1967-1": _contract(
        "hced-Gaza1967-1",
        _canonical("Capture of Gaza (1967)", 1967, 1967, "5-7 June 1967", date_precision="day_range", granularity="urban_capture"),
        "six_day_war_sinai",
        {"israeli_gaza_force_1967"},
        {"egyptian_gaza_force_1967"},
        {"wave8_egypt_oxford_gaza_history", "wave8_egypt_pollack_six_day_war"},
        "The reviewed histories attest the Israeli capture and Egyptian surrender in Gaza; no wider war result is inferred.",
        confidence=0.88,
        war_type="interstate_limited",
    ),
    "hced-Jebel Libni1967-1": _contract(
        "hced-Jebel Libni1967-1",
        _canonical("Battle of Jebel Libni", 1967, 1967, "6 June 1967", date_precision="day"),
        "six_day_war_sinai",
        {"israeli_jebel_libni_force_1967"},
        {"egyptian_jebel_libni_force_1967"},
        {"wave8_egypt_army_key_sinai", "wave8_egypt_pollack_six_day_war"},
        "Israeli forces defeated the Egyptian blocking force at Jebel Libni during the Sinai advance.",
        confidence=0.87,
        war_type="interstate_limited",
    ),
    "hced-Mitla Pass1967-1": _contract(
        "hced-Mitla Pass1967-1",
        _canonical("Interdiction at Mitla Pass (1967)", 1967, 1967, "7 June 1967", date_precision="day", granularity="retreat_interdiction"),
        "six_day_war_sinai",
        {"israeli_mitla_interdiction_force_1967"},
        {"egyptian_mitla_retreat_force_1967"},
        {"wave8_egypt_usni_six_day_war", "wave8_egypt_pollack_six_day_war"},
        "The contract rates the source-attested interdiction and defeat of retreating Egyptian formations at the pass, not a timeless 'battle of Mitla'. The HCED point is in Oaxaca and is withheld.",
        confidence=0.82,
        war_type="interstate_limited",
    ),
    "hced-Bir Gafgafa1967-1": _contract(
        "hced-Bir Gafgafa1967-1",
        _canonical("Battle of Bir Gafgafa", 1967, 1967, "7 June 1967", date_precision="day"),
        "six_day_war_sinai",
        {"israeli_bir_gafgafa_force_1967"},
        {"egyptian_bir_gafgafa_force_1967"},
        {"wave8_egypt_army_key_sinai", "wave8_egypt_pollack_six_day_war"},
        "Israeli forces defeated the Egyptian rearguard at Bir Gafgafa; only that event-bounded action is rated.",
        confidence=0.86,
        war_type="interstate_limited",
    ),
    "hced-Chinese Farm1973-1": _contract(
        "hced-Chinese Farm1973-1",
        _canonical("Battle of the Chinese Farm", 1973, 1973, "15-17 October 1973", date_precision="day_range"),
        "yom_kippur_war_sinai",
        {"israeli_chinese_farm_force_1973"},
        {"egyptian_chinese_farm_defenders_1973"},
        {"wave8_egypt_army_chinese_farm", "wave8_egypt_usmc_crossing_under_fire"},
        "Independent U.S. military histories call the costly action an ultimate Israeli tactical victory that cleared the canal route. It is distinct from the release's strategic 1973 war rating; the queued Nile Delta point is withheld.",
        confidence=0.84,
        war_type="interstate_limited",
    ),
}


def _nonpromotion(
    candidate_id: str,
    cohort: str,
    disposition: str,
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    *,
    owner_event_id: str | None = None,
) -> dict[str, Any]:
    result = {
        "raw_row_sha256": WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES[candidate_id],
        "cohort": cohort,
        "disposition": disposition,
        "hold_category": category,
        "hold_reason": reason,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "terminal_exclusion": disposition == "terminal_exclusion",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": disposition,
        },
    }
    if owner_event_id is not None:
        result["duplicate_ownership"]["existing_owner_event_id"] = owner_event_id
    return result


WAVE8_EGYPT_FORCES_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Azotus-659-1": _nonpromotion(
        "hced-Azotus-659-1", "ancient_chronology", "hold", "pinned_year_unsupported",
        "The reviewed literature places Psammetichus I's Ashdod campaign around 636 BCE and preserves a prolonged-siege tradition; it does not support an Egyptian win at the locked 659 BCE date.",
        {"wave8_egypt_barilan_azotus", "wave8_egypt_treccani_azotus"},
    ),
    "hced-Cos-254-1": _nonpromotion(
        "hced-Cos-254-1", "hellenistic_chronology", "hold", "chronology_and_outcome_disputed",
        "The Battle of Cos chronology, belligerent alignment, and relationship to the Chremonidean War remain disputed; the HCED -254 assertion is not safe to rate.",
        {"wave8_egypt_bmcr_cos"},
    ),
    "hced-Masindi1872-1": _nonpromotion(
        "hced-Masindi1872-1", "khedival_periphery", "hold", "conflicting_tactical_traditions",
        "Accounts alternately describe Baker as locally victorious and as defeated by Kabalega before an insecure retreat. That conflict is unknown, not a draw.",
        {"wave8_egypt_uganda_journal_masindi", "wave8_egypt_masindi_profile"},
    ),
    "hced-Megiddo-1468-1": _nonpromotion(
        "hced-Megiddo-1468-1", "ancient_chronology", "hold", "pinned_year_unsupported",
        "Current Egyptian chronologies place Thutmose III's accession in 1479 BCE and commonly date Megiddo to 1479 or 1457 BCE; the locked -1468 row cannot be reconciled without choosing a chronology by invention.",
        {"wave8_egypt_ucla_chronology", "wave8_egypt_osu_megiddo"},
    ),
    "hced-Napata-593-1": _nonpromotion(
        "hced-Napata-593-1", "ancient_chronology", "hold", "campaign_date_and_event_granularity_uncertain",
        "Scholarship dates Psamtik II's Nubian campaign to 592 or 590 BCE and does not establish the queued -593 Napata record as a discrete engagement.",
        {"wave8_egypt_emory_napata", "wave8_egypt_michigan_napata"},
    ),
    "hced-Paneas-198-1": _nonpromotion(
        "hced-Paneas-198-1", "hellenistic_chronology", "hold", "battle_date_mismatch",
        "The battle normally identified as Panion is dated to 200 BCE. The 198 BCE date reflects territorial consequences and cannot be promoted as the same engagement.",
        {"wave8_egypt_cambridge_panion"},
    ),
    "hced-Suez Canal (1st)1973-1": _nonpromotion(
        "hced-Suez Canal (1st)1973-1", "yom_kippur_war_sinai", "hold", "generic_phase_not_discrete_event",
        "The ordinal label cannot be mapped uniquely to a discrete canal operation in the reviewed campaign histories; its proposed Egyptian win is therefore held.",
        {"wave8_egypt_army_yom_kippur", "wave8_egypt_usmc_crossing_under_fire"},
    ),
    "hced-Suez Canal (2nd)1973-1": _nonpromotion(
        "hced-Suez Canal (2nd)1973-1", "yom_kippur_war_sinai", "hold", "generic_phase_not_discrete_event",
        "The ordinal label cannot be mapped uniquely to a discrete operation. HCED's Draw proposal is not converted into a rating; ambiguity remains a hold.",
        {"wave8_egypt_army_yom_kippur", "wave8_egypt_usmc_crossing_under_fire"},
    ),
    "hced-Suez Canal (3rd)1973-1": _nonpromotion(
        "hced-Suez Canal (3rd)1973-1", "yom_kippur_war_sinai", "hold", "generic_phase_not_discrete_event",
        "The ordinal label cannot be mapped uniquely to a discrete canal operation in the reviewed campaign histories; its proposed Israeli win is therefore held.",
        {"wave8_egypt_army_yom_kippur", "wave8_egypt_usmc_crossing_under_fire"},
    ),
}


WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Kadesh-1275-1": _nonpromotion(
        "hced-Kadesh-1275-1", "ancient_duplicate_conflict", "terminal_exclusion", "existing_inconclusive_event_and_false_outcome",
        "The current release already owns the same Kadesh tradition at 1274 BCE as inconclusive, with the Hittites retaining Kadesh. The HCED -1275 unqualified Egyptian win would duplicate and contradict that adjudication.",
        {"wave8_egypt_world_history_kadesh"},
        owner_event_id="battle_kadesh_1274_bce",
    ),
    "hced-Tokar1883-1": _nonpromotion(
        "hced-Tokar1883-1", "mahdist_war", "terminal_exclusion", "proposed_outcome_disproved",
        "The Egyptian relief column sent toward Tokar on 6 November 1883 was annihilated; Tokar remained besieged and surrendered in February 1884. The queued Egyptian win is the opposite of the documented outcome.",
        {"wave8_egypt_study_circle_sudan", "wave8_egypt_hansard_tokar"},
    ),
}


WAVE8_EGYPT_FORCES_EXCLUSIONS = WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS
WAVE8_EGYPT_FORCES_NONPROMOTIONS = {
    **WAVE8_EGYPT_FORCES_HOLDS,
    **WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS,
}
WAVE8_EGYPT_FORCES_CONTRACT_IDS = frozenset(WAVE8_EGYPT_FORCES_CONTRACTS)
WAVE8_EGYPT_FORCES_HOLD_IDS = frozenset(WAVE8_EGYPT_FORCES_HOLDS)
WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS
)
WAVE8_EGYPT_FORCES_EXCLUSION_IDS = WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSION_IDS
WAVE8_EGYPT_FORCES_RESERVED_IDS = frozenset(
    WAVE8_EGYPT_FORCES_CONTRACT_IDS
    | WAVE8_EGYPT_FORCES_HOLD_IDS
    | WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSION_IDS
)
WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES
)


def _release_disposition(
    candidate_id: str,
    owner_event_id: str,
    participant_sides: Iterable[tuple[str, str]],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES[candidate_id],
        "disposition": "existing_release_owner",
        "owner_event_id": owner_event_id,
        "participant_sides": [list(item) for item in sorted(participant_sides)],
    }


WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Abu Ageila1956-1": _release_disposition("hced-Abu Ageila1956-1", "hced_label_hced_abu_ageila1956_1", {("clio_eg_egypt_modern_2_1953_a888d535", "side_b"), ("clio_q801_1948_5abea45e", "side_a")}),
    "hced-Acre1831-1": _release_disposition("hced-Acre1831-1", "hced_label_hced_acre1831_1", {("egypt_muhammad_ali", "side_a"), ("ottoman_empire", "side_b")}),
    "hced-Acre1840-1": _release_disposition("hced-Acre1840-1", "hced_label_hced_acre1840_1", {("austrian_empire", "side_a"), ("egypt_muhammad_ali", "side_b"), ("united_kingdom", "side_a")}),
    "hced-Alexandria-48-1": _release_disposition("hced-Alexandria-48-1", "hced_wave7_global_hced_alexandria_48_1", {("ptolemaic_egypt_305_bce", "side_b"), ("roman_republic", "side_a")}),
    "hced-Alexandria1167-1": _release_disposition("hced-Alexandria1167-1", "hced_wave7_global_hced_alexandria1167_1", {("clio_il_jerusalem_k_1_1099_306afd1d", "side_a"), ("clio_tn_fatimid_cal_911_d329b0b3", "side_b")}),
    "hced-Alexandria1882-1": _release_disposition("hced-Alexandria1882-1", "hced_label_hced_alexandria1882_1", {("egypt_muhammad_ali", "side_b"), ("united_kingdom", "side_a")}),
    "hced-Ascalon1123-1": _release_disposition("hced-Ascalon1123-1", "hced_wave7_global_hced_ascalon1123_1", {("clio_tn_fatimid_cal_911_d329b0b3", "side_b"), ("republic_venice", "side_a")}),
    "hced-Asluj1948-1": _release_disposition("hced-Asluj1948-1", "hced_wave7_global_hced_asluj1948_1", {("clio_q801_1948_5abea45e", "side_a"), ("kingdom_egypt_1922", "side_b")}),
    "hced-Beersheba1948-1": _release_disposition("hced-Beersheba1948-1", "hced_wave7_global_hced_beersheba1948_1", {("clio_q801_1948_5abea45e", "side_a"), ("kingdom_egypt_1922", "side_b")}),
    "hced-Beirut1840-1": _release_disposition("hced-Beirut1840-1", "hced_label_hced_beirut1840_1", {("austrian_empire", "side_a"), ("egypt_muhammad_ali", "side_b"), ("united_kingdom", "side_a")}),
    "hced-Belen1832-1": _release_disposition("hced-Belen1832-1", "hced_label_hced_belen1832_1", {("egypt_muhammad_ali", "side_a"), ("ottoman_empire", "side_b")}),
    "hced-Damietta1218-1": _release_disposition("hced-Damietta1218-1", "hced_wave7_global_hced_damietta1218_1", {("clio_eg_ayyubid_sultanate_1177_95f5a3a5", "side_a"), ("kingdom_france", "side_b")}),
    "hced-Faluja1948-1": _release_disposition("hced-Faluja1948-1", "hced_wave7_global_hced_faluja1948_1", {("clio_q801_1948_5abea45e", "side_b"), ("kingdom_egypt_1922", "side_a")}),
    "hced-Fariskur1250-1": _release_disposition("hced-Fariskur1250-1", "hced_wave7_global_hced_fariskur1250_1", {("kingdom_france", "side_b"), ("mamluk_sultanate", "side_a")}),
    "hced-Gaza1956-1": _release_disposition("hced-Gaza1956-1", "hced_label_hced_gaza1956_1", {("clio_eg_egypt_modern_2_1953_a888d535", "side_b"), ("clio_q801_1948_5abea45e", "side_a")}),
    "hced-Gundet1875-1": _release_disposition("hced-Gundet1875-1", "hced_label_hced_gundet1875_1", {("egypt_muhammad_ali", "side_b"), ("ethiopian_empire", "side_a")}),
    "hced-Gura1876-1": _release_disposition("hced-Gura1876-1", "hced_label_hced_gura1876_1", {("egypt_muhammad_ali", "side_b"), ("ethiopian_empire", "side_a")}),
    "hced-Homs1832-1": _release_disposition("hced-Homs1832-1", "hced_label_hced_homs1832_1", {("egypt_muhammad_ali", "side_a"), ("ottoman_empire", "side_b")}),
    "hced-Kassassin1882-1": _release_disposition("hced-Kassassin1882-1", "hced_label_hced_kassassin1882_1", {("egypt_muhammad_ali", "side_b"), ("united_kingdom", "side_a")}),
    "hced-Konya1832-1": _release_disposition("hced-Konya1832-1", "hced_label_hced_konya1832_1", {("egypt_muhammad_ali", "side_a"), ("ottoman_empire", "side_b")}),
    "hced-Mitla Pass1956-1": _release_disposition("hced-Mitla Pass1956-1", "hced_label_hced_mitla_pass1956_1", {("clio_eg_egypt_modern_2_1953_a888d535", "side_b"), ("clio_q801_1948_5abea45e", "side_a")}),
    "hced-Navarino1825-1": _release_disposition("hced-Navarino1825-1", "hced_label_hced_navarino1825_1", {("egypt_muhammad_ali", "side_a"), ("greek_revolutionaries_1821", "side_b")}),
    "hced-Nezib1839-1": _release_disposition("hced-Nezib1839-1", "hced_label_hced_nezib1839_1", {("egypt_muhammad_ali", "side_a"), ("ottoman_empire", "side_b")}),
    "hced-Pelusium-525-1": _release_disposition("hced-Pelusium-525-1", "hced_wave7_global_hced_pelusium_525_1", {("achaemenid_empire", "side_a"), ("saite_egypt_664_bce", "side_b")}),
    "hced-Pelusium640-1": _release_disposition("hced-Pelusium640-1", "hced_wave8_early_states_hced_pelusium640_1", {("byzantine_pelusium_garrison_640", "side_b"), ("rashidun_caliphate", "side_a")}),
    "hced-Port Said1956-1": _release_disposition("hced-Port Said1956-1", "hced_label_hced_port_said1956_1", {("clio_eg_egypt_modern_2_1953_a888d535", "side_b"), ("united_kingdom", "side_a")}),
    "hced-Pyramids1798-1": _release_disposition("hced-Pyramids1798-1", "hced_wave7_global_hced_pyramids1798_1", {("french_first_republic", "side_a"), ("mamluk_egyptian_forces_1798", "side_b")}),
    "hced-Rafa1956-1": _release_disposition("hced-Rafa1956-1", "hced_label_hced_rafa1956_1", {("clio_eg_egypt_modern_2_1953_a888d535", "side_b"), ("clio_q801_1948_5abea45e", "side_a")}),
    "hced-Straits of Tiran1956-1": _release_disposition("hced-Straits of Tiran1956-1", "hced_label_hced_straits_of_tiran1956_1", {("clio_eg_egypt_modern_2_1953_a888d535", "side_b"), ("clio_q801_1948_5abea45e", "side_a")}),
    "hced-Tel-el-Kebir1882-1": _release_disposition("hced-Tel-el-Kebir1882-1", "hced_label_hced_tel_el_kebir1882_1", {("egypt_muhammad_ali", "side_b"), ("united_kingdom", "side_a")}),
    "hced-Tel-el-Maskhuta1882-1": _release_disposition("hced-Tel-el-Maskhuta1882-1", "hced_label_hced_tel_el_maskhuta1882_1", {("egypt_muhammad_ali", "side_b"), ("united_kingdom", "side_a")}),
}


WAVE8_EGYPT_FORCES_EXACT_LABEL_FUNNEL_AUDIT = {
    "normalized_label": "egypt",
    "events_touched": 13,
    "unresolved_side_attempts": 13,
    "event_candidate_id_sha256": "693f2bd0faa9d2bc1b808980f598d62b7a54c91adc9e3c59b1df77d6e70c659d",
    "exact_inventory_candidate_id_sha256": "8ec9305eb28bc56ff94e53d8495a0385148d27e4edb1a178b2a04332ed7bf363",
    "exact_row_hash_mapping_sha256": "6ecf1744a5b71a88f449dade893007a6db6031524e28b94c0f7dd069b6cafb27",
    "finding": "the_funnel_is_a_13_row_unresolved_projection_not_the_58_row_literal_inventory",
}


WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT: dict[str, Any] = {
    "seed_entities": {
        "egypt_new_kingdom": [-1550, -1069],
        "egypt_muhammad_ali": [1805, 1882],
        "mamluk_sultanate": [1250, 1517],
    },
    "release_entities": {
        "egypt_new_kingdom": [-1550, -1069],
        "saite_egypt_664_bce": [-664, -525],
        "ptolemaic_egypt_305_bce": [-305, -30],
        "byzantine_pelusium_garrison_640": [640, 640],
        "clio_tn_fatimid_cal_911_d329b0b3": [911, 1176],
        "clio_eg_ayyubid_sultanate_1177_95f5a3a5": [1177, 1249],
        "mamluk_sultanate": [1250, 1517],
        "ayyubid_aleppo_city_garrison_1260": [1260, 1260],
        "baybars_mamluk_siege_army_krak_1271": [1271, 1271],
        "qalawun_mamluk_siege_army_margat_1285": [1285, 1285],
        "murad_bey_rahmaniyya_force_1786": [1786, 1786],
        "mamluk_egyptian_forces_1798": [1798, 1798],
        "murad_bey_egypt_campaign_force_1798": [1798, 1798],
        "murad_bey_samhud_coalition_1799": [1799, 1799],
        "egypt_muhammad_ali": [1805, 1882],
        "kingdom_egypt_1922": [1922, 1952],
        "clio_eg_egypt_modern_2_1953_a888d535": [1953, 1957],
        "clio_eg_egypt_modern_2_1973_e01853c2": [1973, 2024],
    },
    "seed_events": {
        "battle_kadesh_1274_bce": {
            "year": -1274,
            "entity_ids": ["egypt_new_kingdom", "hittite_empire"],
            "finding": "existing_inconclusive_owner_blocks_hced_1275_win",
        },
        "battle_ain_jalut_1260": {
            "year": 1260,
            "entity_ids": ["mamluk_sultanate", "mongol_empire"],
            "finding": "mamluk_sultanate_rating_is_time_bounded_and_not_generic_egypt",
        },
    },
    "findings": {
        "1967": "no_audited_existing_egypt_identity_covers_1967",
        "1973": "existing_republic_is_strategic_polity_only_chinese_farm_uses_event_formations",
        "adjacent_namesakes": "ayyubid_and_mamluk_event_forces_outside_egypt_are_never_reused",
        "generic_identity": "forbidden",
    },
}


WAVE8_EGYPT_FORCES_CURRENT_RELEASE_EVENT_AUDIT = {
    "audited_entity_ids": sorted(
        WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT["release_entities"]
    ),
    "audited_entity_id_sha256": "09b5ca9eeef1d2ce527057c0668a6101440179701824f2499d0a18aed61db25b",
    # Refreshed after the exact IWD Arab-Israeli War parent bound the audited
    # Kingdom of Egypt identity, adding a 58th Egypt-related release event.
    "event_count": 58,
    "event_id_sha256": "ba133683ac1907a7ff094702bc9a85e166073cf7ef24781455f6b2c0718ea925",
    "event_projection_sha256": "99c54b25058a70f719415cf7854c95bab5e7423e9cd5ed22d2e1bbe81fc10801",
    "projection_fields": [
        "end_year",
        "entity_ids",
        "hced_candidate_id",
        "id",
        "iwd_parent_war_id",
        "year",
    ],
}


WAVE8_EGYPT_FORCES_IWD_AUDIT = {
    "iwd-195": {
        "raw_row_sha256": "5372e7a72b547d359fafc9c4ad66746d08a2666b8431b08717fdbe1b0f89e59b",
        "name": "SixDay_Isr_Egypt_1967",
        "start_year": 1967,
        "end_year": 1967,
        "parent_war_id": "64",
        "disposition": "strategic_component_held_outside_tactical_lane",
        "release_parent_owner": None,
        "reason": "The IWD component is a strategic war candidate and cannot own or duplicate six separately sourced HCED/IWBD tactical engagements.",
    }
}


WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-148-55-1397": {"raw_row_sha256": "d74ed0a3470ab7645df35d2b9e5f61bb5e11e1f9d5aea92385b79accbb0cf741", "hced_owner_candidate_id": "hced-Beersheba1948-1", "owner_event_id": "hced_wave7_global_hced_beersheba1948_1", "name": "Beersheba", "year": 1948, "disposition": "source_duplicate_hced_owner"},
    "iwbd-148-55-1399": {"raw_row_sha256": "0183fc84cc1c0c5277de7c10880e40d789fae2e51ad1664c07279529b425a24d", "hced_owner_candidate_id": "hced-Faluja1948-1", "owner_event_id": "hced_wave7_global_hced_faluja1948_1", "name": "Faluja", "year": 1948, "disposition": "source_duplicate_hced_owner"},
    "iwbd-148-55-1401": {"raw_row_sha256": "e18861a9590ae4450b0afba4772629f3f0a0bceaf1d9f33e9759b0541780cac9", "hced_owner_candidate_id": "hced-Asluj1948-1", "owner_event_id": "hced_wave7_global_hced_asluj1948_1", "name": "Asluj", "year": 1948, "disposition": "source_duplicate_hced_owner"},
    "iwbd-155-58-1448": {"raw_row_sha256": "a2cc94737eb01ce14c4fbf96b2abaa3158889712d65299ecf75e1b98e9fc2910", "hced_owner_candidate_id": "hced-Mitla Pass1956-1", "owner_event_id": "hced_label_hced_mitla_pass1956_1", "name": "Mitla Pass", "year": 1956, "disposition": "source_duplicate_hced_owner"},
    "iwbd-155-58-1449": {"raw_row_sha256": "64b354275e9965ceb49015ad839aff0e265df135910a714f0751eb5f6aed3a6d", "hced_owner_candidate_id": "hced-Abu Ageila1956-1", "owner_event_id": "hced_label_hced_abu_ageila1956_1", "name": "Abu Ageila", "year": 1956, "disposition": "source_duplicate_hced_owner"},
    "iwbd-155-58-1450": {"raw_row_sha256": "44fad3910fc48e9973d08732b187369b551e767a3a8ba6a6c98d3a0ac095c924", "hced_owner_candidate_id": "hced-Rafa1956-1", "owner_event_id": "hced_label_hced_rafa1956_1", "name": "Rafa", "year": 1956, "disposition": "source_duplicate_hced_owner"},
    "iwbd-155-58-1451": {"raw_row_sha256": "81bbe178fecc4b71c8a80cdf7556f611dd03b97234bede9789066414738b28a2", "hced_owner_candidate_id": "hced-Straits of Tiran1956-1", "owner_event_id": "hced_label_hced_straits_of_tiran1956_1", "name": "Straits of Tiran", "year": 1956, "disposition": "source_duplicate_hced_owner"},
    "iwbd-155-58-1452": {"raw_row_sha256": "b77d03a06f7419fc5bf265a744dd244c417868d13fbdf8e0e57fcb7c67d6340b", "hced_owner_candidate_id": "hced-Gaza1956-1", "owner_event_id": "hced_label_hced_gaza1956_1", "name": "Gaza", "year": 1956, "disposition": "source_duplicate_hced_owner"},
    "iwbd-155-58-1453": {"raw_row_sha256": "1718495a32601d7b5c5c2b9652c7127b1124030c7b1f8d519b98d35dcd4eeb4d", "hced_owner_candidate_id": "hced-Port Said1956-1", "owner_event_id": "hced_label_hced_port_said1956_1", "name": "Port Said", "year": 1956, "disposition": "source_duplicate_hced_owner"},
    "iwbd-169-64-1523": {"raw_row_sha256": "9440cf793688bf417973786696b1ac0da7e44b36b633c9e1225abf0e58aa0e18", "hced_owner_candidate_id": "hced-Rafa1967-1", "owner_event_id": "hced_wave8_egypt_forces_hced_rafa1967_1", "name": "Rafa", "year": 1967, "disposition": "source_duplicate_hced_owner"},
    "iwbd-169-64-1524": {"raw_row_sha256": "1560128ba3169c92ebc46d8c544bf8d85d12758ed6072c54af053fa7a00b8e00", "hced_owner_candidate_id": "hced-Abu Ageila1967-1", "owner_event_id": "hced_wave8_egypt_forces_hced_abu_ageila1967_1", "name": "Abu Ageila", "year": 1967, "disposition": "source_duplicate_hced_owner"},
    "iwbd-169-64-1527": {"raw_row_sha256": "9c5356e7334a99fa8d6770fb651d656950d72bf550ff2bcf0f5b09935a209920", "hced_owner_candidate_id": "hced-Gaza1967-1", "owner_event_id": "hced_wave8_egypt_forces_hced_gaza1967_1", "name": "Gaza", "year": 1967, "disposition": "source_duplicate_hced_owner"},
    "iwbd-169-64-1529": {"raw_row_sha256": "6f8f0d4fa751ed9d696c2fc87de544db759bae55ceac90b22a314e71b796df44", "hced_owner_candidate_id": "hced-Jebel Libni1967-1", "owner_event_id": "hced_wave8_egypt_forces_hced_jebel_libni1967_1", "name": "Jebel Libni", "year": 1967, "disposition": "source_duplicate_hced_owner"},
    "iwbd-169-64-1530": {"raw_row_sha256": "c9139030cae6c2de6b22b3eac831bec557a20b42a8f005a2b9dcbee1317353ac", "hced_owner_candidate_id": "hced-Mitla Pass1967-1", "owner_event_id": "hced_wave8_egypt_forces_hced_mitla_pass1967_1", "name": "Mitla Pass", "year": 1967, "disposition": "source_duplicate_hced_owner"},
    "iwbd-169-64-1531": {"raw_row_sha256": "2173aef03686d77f287f1d9445d8aaf7b9f6f124211be87247eaf14e17a4509f", "hced_owner_candidate_id": "hced-Bir Gafgafa1967-1", "owner_event_id": "hced_wave8_egypt_forces_hced_bir_gafgafa1967_1", "name": "Bir Gafgafa", "year": 1967, "disposition": "source_duplicate_hced_owner"},
    "iwbd-181-70-1570": {"raw_row_sha256": "65aae876817960d608e784ac4d0be0737f160388add1917c762584c9db2c46aa", "hced_owner_candidate_id": "hced-Chinese Farm1973-1", "owner_event_id": "hced_wave8_egypt_forces_hced_chinese_farm1973_1", "name": "Chinese Farm", "year": 1973, "disposition": "source_duplicate_hced_owner"},
    "iwbd-65-24-314": {"raw_row_sha256": "52ce1c002cddc465f0cd157280e8445ea7cea9bffda7ecc5e881650fa74060b8", "hced_owner_candidate_id": "hced-Alexandria1882-1", "owner_event_id": "hced_label_hced_alexandria1882_1", "name": "Alexandria", "year": 1882, "disposition": "source_duplicate_hced_owner"},
    "iwbd-65-24-315": {"raw_row_sha256": "b82ee5290b859de95f1004a433e6539faabb321b1ac18038f75c677686d9ccc3", "hced_owner_candidate_id": "hced-Tel-el-Maskhuta1882-1", "owner_event_id": "hced_label_hced_tel_el_maskhuta1882_1", "name": "Tel-el-Maskhuta", "year": 1882, "disposition": "source_duplicate_hced_owner"},
    "iwbd-65-24-316": {"raw_row_sha256": "93506e4784a6058ae5b7f65a675a3f1a8ed825165b77e56dfdf10bac695d6740", "hced_owner_candidate_id": "hced-Kassassin1882-1", "owner_event_id": "hced_label_hced_kassassin1882_1", "name": "Kassassin", "year": 1882, "disposition": "source_duplicate_hced_owner"},
    "iwbd-65-24-317": {"raw_row_sha256": "11e05ed7995a47deeb1dc27b15c55e72e9392789e5eb7292ab02452f3487d69a", "hced_owner_candidate_id": "hced-Tel-el-Kebir1882-1", "owner_event_id": "hced_label_hced_tel_el_kebir1882_1", "name": "Tel-el-Kebir", "year": 1882, "disposition": "source_duplicate_hced_owner"},
}


WAVE8_EGYPT_FORCES_HCED_TWIN_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_EGYPT_FORCES_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS = WAVE8_EGYPT_FORCES_CONTRACT_IDS
WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Aussa1875-1", "hced-Dufile1888-1"}
)
WAVE8_EGYPT_FORCES_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_EGYPT_FORCES_LOCATION_QUARANTINE_REASONS = {
    candidate_id: {
        "actions": (
            ["withhold_country", "withhold_point"]
            if candidate_id in WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS
            else ["withhold_point"]
        ),
        "reason": (
            "HCED identifies Awsa as Djibouti although the action is in present-day Ethiopia; its point is not independently source-audited."
            if candidate_id == "hced-Aussa1875-1"
            else "HCED identifies Dufile as Sudan although the fort is in present-day Uganda; its point is not independently source-audited."
            if candidate_id == "hced-Dufile1888-1"
            else "The HCED point is not independently verified at engagement precision and is withheld; the reviewed modern country remains."
        ),
    }
    for candidate_id in sorted(WAVE8_EGYPT_FORCES_CONTRACT_IDS)
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _raw_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_row_hashes": WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES,
        "contracts": WAVE8_EGYPT_FORCES_CONTRACTS,
        "country_quarantine_additions": sorted(WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS),
        "current_release_event_audit": WAVE8_EGYPT_FORCES_CURRENT_RELEASE_EVENT_AUDIT,
        "entities": WAVE8_EGYPT_FORCES_ENTITIES,
        "exact_label_funnel_audit": WAVE8_EGYPT_FORCES_EXACT_LABEL_FUNNEL_AUDIT,
        "exact_row_hashes": WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES,
        "existing_release_dispositions": WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS,
        "hced_twin_dispositions": WAVE8_EGYPT_FORCES_HCED_TWIN_DISPOSITIONS,
        "holds": WAVE8_EGYPT_FORCES_HOLDS,
        "identity_boundary_audit": WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT,
        "iwbd_duplicate_dispositions": WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS,
        "iwd_audit": WAVE8_EGYPT_FORCES_IWD_AUDIT,
        "location_quarantine_reasons": WAVE8_EGYPT_FORCES_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_EGYPT_FORCES_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS),
        "sources": WAVE8_EGYPT_FORCES_SOURCES,
        "terminal_exclusions": WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS,
    }


def wave8_egypt_forces_audit_signature() -> str:
    """Return the deterministic signature of this exact-label audit."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_EGYPT_FORCES_FINAL_AUDIT_SIGNATURE = (
    "772f51dd8c3513c37f64d00b127bb1147c6ce4218d7326de0192da1f6ee5a05e"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_EGYPT_FORCES_CONTRACTS),
        len(WAVE8_EGYPT_FORCES_HOLDS),
        len(WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS),
        len(WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS),
    ) != (16, 9, 2, 31):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (
        len(WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES),
        len(WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES),
        len(WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS),
        len(WAVE8_EGYPT_FORCES_ENTITIES),
        len(WAVE8_EGYPT_FORCES_SOURCES),
    ) != (58, 38, 20, 32, 38):
        raise ValueError(f"{_LANE_NAME} audited fixture inventory changed")

    dispositions = (
        WAVE8_EGYPT_FORCES_CONTRACT_IDS,
        WAVE8_EGYPT_FORCES_HOLD_IDS,
        WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSION_IDS,
        frozenset(WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS),
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(len(dispositions))
        for j in range(i + 1, len(dispositions))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if frozenset().union(*dispositions) != WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    if len(WAVE8_EGYPT_FORCES_RESERVED_IDS) != 27:
        raise ValueError(f"{_LANE_NAME} unresolved reservation count changed")
    if WAVE8_EGYPT_FORCES_EXCLUSIONS is not WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion alias diverged")
    if set(WAVE8_EGYPT_FORCES_NONPROMOTIONS) != (
        WAVE8_EGYPT_FORCES_HOLD_IDS
        | WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSION_IDS
    ):
        raise ValueError(f"{_LANE_NAME} nonpromotion inventory changed")

    exact_mapping_digest = hashlib.sha256(
        _canonical_json(WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES).encode("utf-8")
    ).hexdigest()
    adjacent_mapping_digest = hashlib.sha256(
        _canonical_json(WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES).encode("utf-8")
    ).hexdigest()
    if exact_mapping_digest != "6ecf1744a5b71a88f449dade893007a6db6031524e28b94c0f7dd069b6cafb27":
        raise ValueError(f"{_LANE_NAME} exact row fingerprint table changed")
    if adjacent_mapping_digest != "61004fd914b6d13a028f29271dcbaf2fafe961e9788c951b46cbe77cc244bc88":
        raise ValueError(f"{_LANE_NAME} adjacent row fingerprint table changed")

    if len(_SOURCE_BY_ID) != len(WAVE8_EGYPT_FORCES_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({str(item["source_family_id"]) for item in WAVE8_EGYPT_FORCES_SOURCES}) != len(WAVE8_EGYPT_FORCES_SOURCES):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_EGYPT_FORCES_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_EGYPT_FORCES_ENTITIES}
    if len(entity_by_id) != len(WAVE8_EGYPT_FORCES_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    used_entities: set[str] = set()
    used_sources: set[str] = set()
    canonical_keys: set[str] = set()
    for candidate_id, contract in WAVE8_EGYPT_FORCES_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} contract hash drifted")
        canonical = contract["canonical_event"]
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        expected_key = f"{_slug(str(canonical['name']))}:{low}:{high}"
        if canonical["canonical_key"] != expected_key or expected_key in canonical_keys:
            raise ValueError(f"{_LANE_NAME} canonical event key drifted")
        canonical_keys.add(expected_key)
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if (
            not side_1
            or not side_2
            or set(side_1) & set(side_2)
            or not _is_sorted_unique(side_1)
            or not _is_sorted_unique(side_2)
        ):
            raise ValueError(f"{_LANE_NAME} actor sides are invalid")
        if not set(side_1 + side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} contract uses an external identity")
        if any(
            int(entity_by_id[entity_id]["start_year"]) != low
            or int(entity_by_id[entity_id]["end_year"]) != high
            for entity_id in (*side_1, *side_2)
        ):
            raise ValueError(f"{_LANE_NAME} actor crossed its event window")
        used_entities.update(side_1 + side_2)

        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"] != "event_bounded_exact_forces"
        ):
            raise ValueError(f"{_LANE_NAME} invented, reversed, or widened an outcome")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} contract ownership drifted")
        outcomes = list(map(str, contract["outcome_source_ids"]))
        evidence = list(map(str, contract["evidence_refs"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if (
            len(outcomes) < 2
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
            or not set(evidence) <= set(_SOURCE_BY_ID)
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        expected_families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        if any("outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"] for source_id in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} event formations are not exactly consumed")
    for entity in WAVE8_EGYPT_FORCES_ENTITIES:
        if not str(entity["kind"]).startswith("event_bounded_"):
            raise ValueError(f"{_LANE_NAME} entity is not event bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} entity opens a generic fallback")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "generic egypt" not in note:
            raise ValueError(f"{_LANE_NAME} entity lacks a continuity firewall")
        refs = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} entity sources drifted")
        used_sources.update(refs)

    for candidate_id, item in WAVE8_EGYPT_FORCES_NONPROMOTIONS.items():
        if item["raw_row_sha256"] != WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} nonpromotion hash drifted")
        if any(key in item for key in ("result_type", "winner_side", "side_1_entity_ids", "side_2_entity_ids")):
            raise ValueError(f"{_LANE_NAME} hold or exclusion contains a rated result")
        if not set(item["evidence_refs"]) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} nonpromotion evidence drifted")
        used_sources.update(map(str, item["evidence_refs"]))
    if used_sources != set(_SOURCE_BY_ID):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS != WAVE8_EGYPT_FORCES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine changed")
    if WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS != {
        "hced-Aussa1875-1",
        "hced-Dufile1888-1",
    }:
        raise ValueError(f"{_LANE_NAME} country quarantine changed")
    if set(WAVE8_EGYPT_FORCES_LOCATION_QUARANTINE_REASONS) != WAVE8_EGYPT_FORCES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reasons are incomplete")
    if WAVE8_EGYPT_FORCES_OUTCOME_OVERRIDES or WAVE8_EGYPT_FORCES_HCED_TWIN_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} zero audit inventory changed")

    owner_candidates = {
        str(item["hced_owner_candidate_id"])
        for item in WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS.values()
    }
    if not owner_candidates <= WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} IWBD owner leaves exact inventory")
    for item in WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS.values():
        candidate_id = str(item["hced_owner_candidate_id"])
        expected_owner = (
            WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS[candidate_id]["owner_event_id"]
            if candidate_id in WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS
            else f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        )
        if item["owner_event_id"] != expected_owner:
            raise ValueError(f"{_LANE_NAME} IWBD duplicate owner drifted")

    if (
        WAVE8_EGYPT_FORCES_FINAL_AUDIT_SIGNATURE != "PENDING"
        and wave8_egypt_forces_audit_signature()
        != WAVE8_EGYPT_FORCES_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def _rows_by_id(rows: Iterable[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    indexed: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            indexed.setdefault(candidate_id, []).append(row)
    return indexed


def _is_adjacent_egypt_row(row: Mapping[str, Any]) -> bool:
    sides = (row.get("side_1_raw"), row.get("side_2_raw"))
    return _EXACT_RAW_LABEL not in sides and any(
        "egypt" in str(value or "").casefold() for value in sides
    )


def validate_wave8_egypt_forces_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all literal and adjacent HCED rows, fingerprints, and twins."""

    _validate_static()
    validate_exact_hced_inventory(
        hced_rows,
        WAVE8_EGYPT_FORCES_CONTRACTS,
        WAVE8_EGYPT_FORCES_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    indexed = _rows_by_id(hced_rows)
    exact_rows = [
        row
        for row in hced_rows
        if row.get("side_1_raw") == _EXACT_RAW_LABEL
        or row.get("side_2_raw") == _EXACT_RAW_LABEL
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact_rows}
    if exact_ids != WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact-label inventory drifted: "
            f"{sorted(exact_ids ^ WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS)}"
        )
    for candidate_id, expected in WAVE8_EGYPT_FORCES_EXACT_ROW_HASHES.items():
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} exact row {candidate_id} expected once, found {len(rows)}"
            )
        if canonical_hced_row_sha256(dict(rows[0])) != expected:
            raise ValueError(f"{_LANE_NAME} exact row fingerprint changed for {candidate_id}")

    adjacent = {
        str(row.get("candidate_id")): row
        for row in hced_rows
        if _is_adjacent_egypt_row(row)
    }
    if set(adjacent) != set(WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES):
        raise ValueError(
            f"{_LANE_NAME} adjacent-label inventory drifted: "
            f"{sorted(set(adjacent) ^ set(WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES))}"
        )
    for candidate_id, expected in WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES.items():
        if canonical_hced_row_sha256(dict(adjacent[candidate_id])) != expected:
            raise ValueError(f"{_LANE_NAME} adjacent row fingerprint changed for {candidate_id}")

    exact_keys = {
        (normalize_label(row.get("name")), int(row["year_low"]), int(row["year_high"]))
        for row in exact_rows
    }
    if len(exact_keys) != len(exact_rows):
        raise ValueError(f"{_LANE_NAME} exact inventory contains a same-event twin")
    twins = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if str(row.get("candidate_id")) not in exact_ids
        and row.get("year_low") is not None
        and row.get("year_high") is not None
        and (
            normalize_label(row.get("name")),
            int(row["year_low"]),
            int(row["year_high"]),
        )
        in exact_keys
    }
    if twins != set(WAVE8_EGYPT_FORCES_HCED_TWIN_DISPOSITIONS):
        raise ValueError(f"{_LANE_NAME} unreviewed HCED same-event twin(s): {sorted(twins)}")

    return {
        "adjacent_hced_rows": len(adjacent),
        "exact_label_rows": len(exact_rows),
        "existing_release_dispositions": len(WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS),
        "holds": len(WAVE8_EGYPT_FORCES_HOLDS),
        "promotion_contracts": len(WAVE8_EGYPT_FORCES_CONTRACTS),
        "reviewed_hced_rows": len(exact_rows),
        "terminal_exclusions": len(WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS),
    }


def _records_by_id(
    records: Iterable[Mapping[str, Any]] | Mapping[str, Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    values = records.values() if isinstance(records, Mapping) else records
    result: dict[str, Mapping[str, Any]] = {}
    for record in values:
        record_id = str(record.get("id") or "")
        if not record_id or record_id in result:
            raise ValueError(f"{_LANE_NAME} duplicate or missing record ID: {record_id!r}")
        result[record_id] = record
    return result


def _current_release_event_projection(
    release_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    audited_ids = set(WAVE8_EGYPT_FORCES_CURRENT_RELEASE_EVENT_AUDIT["audited_entity_ids"])
    projection: list[dict[str, Any]] = []
    for event in release_events:
        related = sorted(
            {
                str(participant.get("entity_id"))
                for participant in event.get("participants", [])
                if str(participant.get("entity_id")) in audited_ids
            }
        )
        if not related:
            continue
        projection.append(
            {
                "id": str(event["id"]),
                "year": int(event["year"]),
                "end_year": event.get("end_year", event["year"]),
                "entity_ids": related,
                "hced_candidate_id": event.get("hced_candidate_id"),
                "iwd_parent_war_id": event.get("iwd_parent_war_id"),
            }
        )
    return sorted(projection, key=lambda item: str(item["id"]))


def _validate_current_release_event_inventory(
    release_events: Iterable[Mapping[str, Any]],
) -> None:
    projection = _current_release_event_projection(release_events)
    audit = WAVE8_EGYPT_FORCES_CURRENT_RELEASE_EVENT_AUDIT
    if len(projection) != int(audit["event_count"]):
        raise ValueError(f"{_LANE_NAME} Egypt-related release event count drifted")
    event_id_digest = hashlib.sha256(
        "".join(f"{item['id']}\n" for item in projection).encode("utf-8")
    ).hexdigest()
    projection_digest = hashlib.sha256(
        _canonical_json(projection).encode("utf-8")
    ).hexdigest()
    if event_id_digest != audit["event_id_sha256"]:
        raise ValueError(f"{_LANE_NAME} Egypt-related release event IDs drifted")
    if projection_digest != audit["event_projection_sha256"]:
        raise ValueError(f"{_LANE_NAME} Egypt-related release event projection drifted")


def validate_wave8_egypt_forces_identity_boundaries(
    seed_entities: Iterable[Mapping[str, Any]] | Mapping[str, Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]] | Mapping[str, Mapping[str, Any]],
    seed_events: Iterable[Mapping[str, Any]],
    release_events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    """Audit every existing Egypt-related identity window and release event."""

    _validate_static()
    seed_by_id = _records_by_id(seed_entities)
    release_by_id = _records_by_id(release_entities)
    for scope, actual in (
        ("seed_entities", seed_by_id),
        ("release_entities", release_by_id),
    ):
        for entity_id, expected_window in WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT[scope].items():
            entity = actual.get(entity_id)
            if entity is None:
                raise ValueError(f"{_LANE_NAME} missing audited identity {entity_id}")
            window = [int(entity["start_year"]), int(entity["end_year"])]
            if window != expected_window:
                raise ValueError(f"{_LANE_NAME} identity window drifted for {entity_id}")

    audited_release_ids = set(
        WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT["release_entities"]
    )
    covering_1967 = {
        entity_id
        for entity_id in audited_release_ids
        if int(release_by_id[entity_id]["start_year"]) <= 1967
        and int(release_by_id[entity_id]["end_year"]) >= 1967
    }
    if covering_1967:
        raise ValueError(
            f"{_LANE_NAME} an existing identity unexpectedly covers 1967: "
            f"{sorted(covering_1967)}"
        )

    seed_event_by_id = _records_by_id(seed_events)
    for event_id, expected in WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT["seed_events"].items():
        event = seed_event_by_id.get(event_id)
        if event is None or int(event["year"]) != int(expected["year"]):
            raise ValueError(f"{_LANE_NAME} seed event boundary drifted for {event_id}")
        participant_ids = sorted(
            str(participant["entity_id"]) for participant in event.get("participants", [])
        )
        if participant_ids != expected["entity_ids"]:
            raise ValueError(f"{_LANE_NAME} seed event actors drifted for {event_id}")

    release_event_list = list(release_events)
    _validate_current_release_event_inventory(release_event_list)
    release_event_by_id = _records_by_id(release_event_list)
    strategic_1973 = release_event_by_id.get("iwd_war_70_yom_kippur_1973")
    if strategic_1973 is None or "clio_eg_egypt_modern_2_1973_e01853c2" not in {
        str(participant["entity_id"])
        for participant in strategic_1973.get("participants", [])
    }:
        raise ValueError(f"{_LANE_NAME} 1973 strategic polity boundary drifted")

    return {
        "audited_release_entities": len(audited_release_ids),
        "audited_release_events": len(
            _current_release_event_projection(release_event_list)
        ),
        "audited_seed_entities": len(
            WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT["seed_entities"]
        ),
        "audited_seed_events": len(
            WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT["seed_events"]
        ),
        "existing_1967_identity_candidates": 0,
    }


def _year(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _iwbd_year(row: Mapping[str, Any]) -> int | None:
    for field in ("start_date", "end_date"):
        text = str(row.get(field) or "")
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4])
    return _year(row.get("year"))


def _event_participant_sides(event: Mapping[str, Any]) -> list[list[str]]:
    return sorted(
        [str(item["entity_id"]), str(item["side"])]
        for item in event.get("participants", [])
    )


def validate_wave8_egypt_forces_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
    iwd_rows: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Validate HCED/IWBD/IWD twins and all-or-none current-release ownership."""

    validate_wave8_egypt_forces_queue_contracts(hced_rows)
    events = list(existing_events)
    event_by_id = _records_by_id(events) if events else {}

    candidate_events: dict[str, list[Mapping[str, Any]]] = {}
    for event in events:
        candidate_id = event.get("hced_candidate_id")
        if candidate_id in WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS:
            candidate_events.setdefault(str(candidate_id), []).append(event)
    duplicates = {
        candidate_id for candidate_id, owners in candidate_events.items() if len(owners) != 1
    }
    if duplicates:
        raise ValueError(f"{_LANE_NAME} duplicate release owners: {sorted(duplicates)}")
    event_by_candidate = {
        candidate_id: owners[0] for candidate_id, owners in candidate_events.items()
    }

    lane_overlap = WAVE8_EGYPT_FORCES_CONTRACT_IDS & set(event_by_candidate)
    if len(lane_overlap) not in {0, len(WAVE8_EGYPT_FORCES_CONTRACT_IDS)}:
        raise ValueError(f"{_LANE_NAME} partial release integration: {sorted(lane_overlap)}")
    for candidate_id in lane_overlap:
        event = event_by_candidate[candidate_id]
        expected_id = f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        if str(event.get("id")) != expected_id:
            raise ValueError(f"{_LANE_NAME} lane owner ID drifted for {candidate_id}")
        contract = WAVE8_EGYPT_FORCES_CONTRACTS[candidate_id]
        expected_sides = sorted(
            [[entity_id, "side_a"] for entity_id in contract["side_1_entity_ids"]]
            + [[entity_id, "side_b"] for entity_id in contract["side_2_entity_ids"]]
        )
        if _event_participant_sides(event) != expected_sides:
            raise ValueError(f"{_LANE_NAME} lane owner actors drifted for {candidate_id}")

    if events:
        _validate_current_release_event_inventory(events)
        for candidate_id, disposition in WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS.items():
            event = event_by_candidate.get(candidate_id)
            if event is None or str(event.get("id")) != disposition["owner_event_id"]:
                raise ValueError(f"{_LANE_NAME} existing owner drifted for {candidate_id}")
            if _event_participant_sides(event) != disposition["participant_sides"]:
                raise ValueError(f"{_LANE_NAME} existing owner actors drifted for {candidate_id}")
        forbidden = WAVE8_EGYPT_FORCES_HOLD_IDS | WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSION_IDS
        if forbidden & set(event_by_candidate):
            raise ValueError(
                f"{_LANE_NAME} hold or exclusion entered release: "
                f"{sorted(forbidden & set(event_by_candidate))}"
            )
        kadesh = event_by_id.get("battle_kadesh_1274_bce")
        if kadesh is None or {
            str(participant.get("termination"))
            for participant in kadesh.get("participants", [])
        } != {"inconclusive"}:
            raise ValueError(f"{_LANE_NAME} Kadesh inconclusive owner drifted")

    exact_rows = [
        row
        for row in hced_rows
        if row.get("candidate_id") in WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS
    ]
    exact_by_name_year = {
        (normalize_label(row.get("name")), int(row["year_best"])): row
        for row in exact_rows
    }

    iwbd_overlap: dict[str, Mapping[str, Any]] = {}
    for row in iwbd_rows:
        year = _iwbd_year(row)
        key = (normalize_label(row.get("name")), year)
        if year is not None and key in exact_by_name_year:
            iwbd_overlap[str(row.get("candidate_id"))] = row
    if set(iwbd_overlap) != set(WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS):
        raise ValueError(
            f"{_LANE_NAME} IWBD exact twin inventory drifted: "
            f"{sorted(set(iwbd_overlap) ^ set(WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS))}"
        )
    for candidate_id, disposition in WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS.items():
        row = iwbd_overlap[candidate_id]
        if _raw_row_sha256(row) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} IWBD fingerprint changed for {candidate_id}")
        if (
            normalize_label(row.get("name")) != normalize_label(disposition["name"])
            or _iwbd_year(row) != disposition["year"]
        ):
            raise ValueError(f"{_LANE_NAME} IWBD duplicate key drifted for {candidate_id}")

    if events:
        released_iwbd_ids = {
            str(event.get("iwbd_candidate_id"))
            for event in events
            if event.get("iwbd_candidate_id") is not None
        }
        forbidden_iwbd = released_iwbd_ids & set(WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS)
        if forbidden_iwbd:
            raise ValueError(f"{_LANE_NAME} IWBD duplicate entered release: {sorted(forbidden_iwbd)}")
        for disposition in WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS.values():
            owner_candidate = str(disposition["hced_owner_candidate_id"])
            owner_required = (
                owner_candidate in WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS
                or bool(lane_overlap)
            )
            if owner_required and disposition["owner_event_id"] not in event_by_id:
                raise ValueError(
                    f"{_LANE_NAME} missing HCED owner for IWBD twin {owner_candidate}"
                )

        audited_pairs = set(exact_by_name_year)
        allowed_owner_ids = {
            str(item["owner_event_id"])
            for item in WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS.values()
        } | {
            f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
            for candidate_id in WAVE8_EGYPT_FORCES_CONTRACT_IDS
        }
        release_twins: list[str] = []
        for event in events:
            event_id = str(event.get("id") or "")
            if event_id in allowed_owner_ids:
                continue
            year = _year(event.get("year"))
            aliases = {
                normalize_label(event.get("name")),
                *map(normalize_label, event.get("aliases", [])),
            }
            if year is not None and any((alias, year) in audited_pairs for alias in aliases):
                release_twins.append(event_id or "<missing-id>")
        if release_twins:
            raise ValueError(f"{_LANE_NAME} unreviewed existing-release twin(s): {sorted(release_twins)}")

        parent_64 = [
            str(event.get("id"))
            for event in events
            if str(event.get("iwd_parent_war_id") or "") == "64"
        ]
        component_195 = [
            str(event.get("id"))
            for event in events
            for component in event.get("iwd_components", [])
            if component.get("candidate_id") == "iwd-195"
        ]
        if parent_64 or component_195:
            raise ValueError(f"{_LANE_NAME} IWD 1967 strategic duplicate entered release")

    iwd_list = list(iwd_rows)
    if iwd_list:
        matches = [row for row in iwd_list if row.get("candidate_id") == "iwd-195"]
        if len(matches) != 1:
            raise ValueError(f"{_LANE_NAME} IWD iwd-195 inventory drifted")
        row = matches[0]
        disposition = WAVE8_EGYPT_FORCES_IWD_AUDIT["iwd-195"]
        if _raw_row_sha256(row) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} IWD iwd-195 fingerprint changed")
        if (
            row.get("name") != disposition["name"]
            or int(row["start_year"]) != disposition["start_year"]
            or int(row["end_year"]) != disposition["end_year"]
            or str(row.get("parent_war_id")) != disposition["parent_war_id"]
        ):
            raise ValueError(f"{_LANE_NAME} IWD iwd-195 boundary drifted")

    return {
        "existing_release_dispositions": len(WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS),
        "hced_same_event_twins": len(WAVE8_EGYPT_FORCES_HCED_TWIN_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS),
        "iwd_related_rows": len(WAVE8_EGYPT_FORCES_IWD_AUDIT),
        "release_lane_overlap": len(lane_overlap),
    }


def install_wave8_egypt_forces_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_EGYPT_FORCES_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_egypt_forces_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_EGYPT_FORCES_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_egypt_forces_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Promote the 16 source-supported rows with local location quarantine."""

    validate_wave8_egypt_forces_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_EGYPT_FORCES_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_egypt_forces_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_EGYPT_FORCES_CONTRACTS.values(),
                    *WAVE8_EGYPT_FORCES_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_egypt_forces_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_hced_rows": len(WAVE8_EGYPT_FORCES_ADJACENT_ROW_HASHES),
        "audited_current_release_events": int(WAVE8_EGYPT_FORCES_CURRENT_RELEASE_EVENT_AUDIT["event_count"]),
        "audited_existing_identities": len(WAVE8_EGYPT_FORCES_IDENTITY_BOUNDARY_AUDIT["release_entities"]),
        "country_quarantine_additions": len(WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS),
        "exact_label_rows": len(WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS),
        "existing_release_dispositions": len(WAVE8_EGYPT_FORCES_EXISTING_RELEASE_DISPOSITIONS),
        "hced_same_event_twins": len(WAVE8_EGYPT_FORCES_HCED_TWIN_DISPOSITIONS),
        "holds": len(WAVE8_EGYPT_FORCES_HOLDS),
        "iwbd_duplicate_dispositions": len(WAVE8_EGYPT_FORCES_IWBD_DUPLICATE_DISPOSITIONS),
        "iwd_related_rows": len(WAVE8_EGYPT_FORCES_IWD_AUDIT),
        "new_entities": len(WAVE8_EGYPT_FORCES_ENTITIES),
        "new_sources": len(WAVE8_EGYPT_FORCES_SOURCES),
        "newly_rated_events": len(WAVE8_EGYPT_FORCES_CONTRACTS),
        "outcome_overrides": len(WAVE8_EGYPT_FORCES_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_EGYPT_FORCES_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_EGYPT_FORCES_EXPECTED_CANDIDATE_IDS),
        "terminal_exclusions": len(WAVE8_EGYPT_FORCES_TERMINAL_EXCLUSIONS),
    }


def wave8_egypt_forces_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for later coordinated shared integration."""

    _validate_static()
    return {
        "country": WAVE8_EGYPT_FORCES_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_EGYPT_FORCES_POINT_QUARANTINE_ADDITIONS,
    }


_validate_static()
