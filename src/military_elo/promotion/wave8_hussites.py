"""Candidate-keyed Wave 8 audit for HCED's exact ``Hussites`` label.

The locked cohort contains fourteen rows from 1420 through 1427.  ``Hussites``
does not identify one stable military actor across that span: the rows concern
different Prague, Taborite, Orebite, civic-defender, and later field coalitions.
This lane therefore installs only event- or campaign-bounded forces, never a
generic Hussite alias, religious identity, ethnic identity, or modern polity.

Twelve source-supported engagements are promoted.  Kutna Hora is held because
the staged row collapses a city occupation, a small urban defending element,
and the field army's successful breakout into one unsafe ``Hungary`` win.
Zwettl is held because the reviewed account records an Austrian rout of the
Hussites followed by a Hussite counterattack that drove the Austrians into the
city.  In both cases the tactical result remains unknown, never a draw.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_HUSSITES_CONTRACT_IDS",
    "WAVE8_HUSSITES_CONTRACTS",
    "WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_HUSSITES_CROSS_LANE_DISPOSITIONS",
    "WAVE8_HUSSITES_ENTITIES",
    "WAVE8_HUSSITES_EXCLUSION_IDS",
    "WAVE8_HUSSITES_EXCLUSIONS",
    "WAVE8_HUSSITES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS",
    "WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS",
    "WAVE8_HUSSITES_EXTERNAL_OWNER_IDS",
    "WAVE8_HUSSITES_FINAL_AUDIT_SIGNATURE",
    "WAVE8_HUSSITES_HOLD_IDS",
    "WAVE8_HUSSITES_HOLDS",
    "WAVE8_HUSSITES_INTEGRATION_DISPOSITIONS",
    "WAVE8_HUSSITES_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_HUSSITES_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_HUSSITES_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_HUSSITES_LOCATION_QUARANTINE_REASONS",
    "WAVE8_HUSSITES_NONPROMOTIONS",
    "WAVE8_HUSSITES_OUTCOME_OVERRIDES",
    "WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_HUSSITES_RESERVED_IDS",
    "WAVE8_HUSSITES_SOURCES",
    "WAVE8_HUSSITES_TERMINAL_EXCLUSION_IDS",
    "WAVE8_HUSSITES_TERMINAL_EXCLUSIONS",
    "install_wave8_hussites_entities",
    "install_wave8_hussites_sources",
    "promote_wave8_hussites_contracts",
    "validate_wave8_hussites_integration_dispositions",
    "validate_wave8_hussites_queue_contracts",
    "wave8_hussites_audit_signature",
    "wave8_hussites_cohort_counts",
    "wave8_hussites_counts",
    "wave8_hussites_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Hussites actor audit"
_EVENT_ID_PREFIX = "hced_wave8_hussites_"
_MODULE_OWNER = "military_elo.promotion.wave8_hussites"


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


WAVE8_HUSSITES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_hussites_fudge_chronicle",
        (
            "Origins of the Hussite Uprising: The Chronicle of Laurence of "
            "Brezova (1414-1421)"
        ),
        (
            "https://www.routledge.com/Origins-of-the-Hussite-Uprising-The-"
            "Chronicle-of-Laurence-of-Brezova/Fudge/p/book/9780367438111"
        ),
        "Routledge",
        "academic_edition_of_translated_primary_source",
        "fudge_laurence_brezova_chronicle",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_cornej_zizka",
        "Jan Zizka: zivot a doba husitskeho valecnika",
        "https://books.google.com/books/about/Jan_%C5%BDi%C5%BEka.html?id=Xq5HzQEACAAJ",
        "Paseka",
        "scholarly_historical_monograph",
        "cornej_jan_zizka_2019",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_vhu_vitkov",
        "Zpravy pramenu o boji na hore Vitkove 14. cervence 1420",
        (
            "https://www.vhu.cz/exhibit/jofef-pekar-zpravy-pramenu-o-boji-na-"
            "hore-vitkove-14-cervence-1420/"
        ),
        "Military History Institute Prague (VHU Praha)",
        "institutional_primary_source_collection_reference",
        "vhu_pekar_vitkov_source_collection",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_vhu_kutna_brod",
        "Zpravy pramenu o bojich u Hory a Brodu kol Vanoc 1421",
        "https://vhu.cz/exhibit/zpravy-pramenu-o-bojich-u-hory-a-brodu-kol-vanoc-1421/",
        "Military History Institute Prague (VHU Praha)",
        "institutional_primary_source_collection_reference",
        "vhu_pekar_kutna_brod_source_collection",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_papajik_kutna",
        "Hasek z Valdstejna a Kutna Hora",
        (
            "https://www.uhk.cz/file/edee/filozoficka-fakulta/veda-a-vyzkum/"
            "ha_51_2024.pdf"
        ),
        "Historia Aperta, University of Hradec Kralove",
        "peer_reviewed_scholarly_article",
        "papajik_historia_aperta_51",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_posazavi_porici",
        "Zizka and the battle of Porici nad Sazavou (1420)",
        "https://tourist.posazavi.com/en/Memory/Memory.aspx?Id=7607",
        "Posazavi regional heritage portal",
        "regional_institutional_historical_reference",
        "posazavi_porici_memorial",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_husitstvi_maly_bor",
        "Bitva u Maleho Boru",
        "https://husitstvi.cz/vojenstvi/bitvy-a-tazeni/bitva-u-maleho-boru/",
        "Husitstvi.cz specialist history portal",
        "specialist_historical_reference",
        "husitstvi_maly_bor",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_prague2_vysehrad",
        "Bitva u Vysehradu",
        "https://encyklopedie.praha2.cz/udalosti/795-bitva-u-vysehradu",
        "Encyclopedia of Prague 2",
        "municipal_institutional_historical_reference",
        "prague2_vysehrad_battle",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_hardy_zatec",
        (
            "An Alsatian Nobleman's Account of the Second Crusade against the "
            "Hussites in 1421: A New Edition, Translation, and Interpretation"
        ),
        "https://doi.org/10.1080/28327861.2016.12220069",
        "Crusades (Routledge)",
        "peer_reviewed_primary_source_edition",
        "hardy_alsatian_zatec_account",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_archaeological_atlas_vladar",
        "Zahorice: prehistoric hillfort Vladar",
        "https://www.archeologickyatlas.cz/en/lokace/zahorice_kv_hradiste_vladar",
        "Archaeological Atlas of the Czech Republic",
        "czech_academy_institutional_site_reference",
        "archaeological_atlas_vladar",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_horice_history",
        "History of Horice",
        "https://infocentrum.horice.org/the-town/history",
        "Municipal Information Centre Horice",
        "municipal_institutional_historical_reference",
        "horice_municipal_history",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_ceska_skalice_history",
        "Mala vzpominka na kulate husitske vyroci",
        (
            "https://www.ceskaskalice.cz/prakticke-info/aktuality/"
            "mala-vzpominka-na-kulate-husitske-vyroci-2664cs.html"
        ),
        "City of Ceska Skalice and Bozena Nemcova Museum",
        "municipal_museum_historical_reference",
        "ceska_skalice_museum_battle",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_querengaesser_aussig",
        "Friedrich der Streitbare und die Hussitenbewegung",
        "https://doi.org/10.52410/shb.Bd.64.2018.H.2.S.109-113",
        "Sachsische Heimatblatter",
        "peer_reviewed_scholarly_article",
        "querengaesser_friedrich_hussites",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_vhu_aussig",
        "Po stopach husitstvi v Usteckem kraji",
        (
            "https://vhu.cz/exhibit/luzek-borivoj-po-stopach-husitstvi-"
            "v-usteckem-kraji/"
        ),
        "Military History Institute Prague (VHU Praha)",
        "institutional_military_history_reference",
        "vhu_luzek_aussig",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_zwettl_history",
        "Hussiten belagern die Stadt Zwettl",
        "https://www.zwettl.gv.at/Hussiten_belagern_die_Stadt_Zwettl_2",
        "Stadtgemeinde Zwettl",
        "municipal_archival_history",
        "zwettl_municipal_hussite_history",
        crosscheck=True,
    ),
    _source(
        "wave8_hussites_theisen_austria",
        "Herzog Albrecht V. und die Auswirkungen der Hussitenkriege: Neue Aspekte",
        "https://doi.org/10.7767/9783205219583",
        "Bohlau",
        "peer_reviewed_edited_scholarly_volume",
        "theisen_albrecht_v_hussite_wars",
        outcome=False,
    ),
)


_PORICI_HUSSITE_ID = "zizka_tabor_marching_force_porici_1420"
_PORICI_ROYALIST_ID = "sternberg_bohemian_royalist_interception_force_porici_1420"
_VITKOV_HUSSITE_ID = "zizka_prague_vitkov_defensive_force_1420"
_VITKOV_CRUSADER_ID = "meissen_austrian_crusader_assault_force_vitkov_1420"
_BOR_HUSSITE_ID = "zizka_tabor_field_force_pansky_bor_1420"
_BOR_ROYALIST_ID = "rosenberg_svamberk_plauen_royalist_coalition_pansky_bor_1420"
_VYSEHRAD_HUSSITE_ID = "prague_orebite_tabor_field_coalition_vysehrad_1420"
_VYSEHRAD_CRUSADER_ID = "sigismund_crusader_relief_army_vysehrad_1420"
_ZATEC_HUSSITE_ID = "zatec_hussite_garrison_and_civic_defenders_1421"
_ZATEC_CRUSADER_ID = "western_second_crusade_besieging_army_zatec_1421"
_VLADAR_HUSSITE_ID = "zizka_hussite_retreating_force_vladar_1421"
_VLADAR_LANDFRIED_ID = "pilsen_landfrieden_pursuit_force_vladar_1421"
_KUTNA_CAMPAIGN_HUSSITE_ID = "prague_tabor_hussite_counteroffensive_army_1422"
_NEBOVIDY_CRUSADER_ID = "sigismund_crusader_resistance_force_nebovidy_1422"
_HABRY_CRUSADER_ID = "sigismund_crusader_rear_guard_habry_1422"
_BROD_CRUSADER_ID = "sigismund_crusader_defenders_nemecky_brod_1422"
_HORICE_HUSSITE_ID = "zizka_orebite_field_army_horice_1423"
_HORICE_LORDS_ID = "cenek_vartenberk_lords_union_force_horice_1423"
_SKALICE_HUSSITE_ID = "zizka_hradec_field_force_ceska_skalice_1424"
_SKALICE_LORDS_ID = "eastern_bohemian_catholic_lords_force_skalice_1424"
_AUSSIG_HUSSITE_ID = "hussite_field_coalition_aussig_1426"
_AUSSIG_RELIEF_ID = "saxon_meissen_thuringian_lusatian_relief_army_aussig_1426"


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    note: str,
    source_ids: Iterable[str],
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
        "continuity_note": note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_HUSSITES_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _PORICI_HUSSITE_ID,
        "Zizka's Taborite marching force at Porici (1420)",
        "event_bounded_field_force",
        1420,
        "Porici nad Sazavou, Bohemia",
        (
            "Bounded to the Taborite column marching to Prague and fighting at "
            "Porici. No rating is inherited by Hussites generally, later Taborite "
            "armies, Bohemia, a religious population, or any modern state."
        ),
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_posazavi_porici"],
    ),
    _entity(
        _PORICI_ROYALIST_ID,
        "Sternberg-led Bohemian royalist interception force at Porici (1420)",
        "event_bounded_field_force",
        1420,
        "Porici nad Sazavou, Bohemia",
        (
            "Bounded to the Catholic-royalist force that intercepted the Taborite "
            "march at Porici. No rating is inherited by Habsburgs, Bohemian nobles "
            "generally, a German identity, or any modern state."
        ),
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_posazavi_porici"],
    ),
    _entity(
        _VITKOV_HUSSITE_ID,
        "Zizka-Prague defensive force at Vitkov Hill (1420)",
        "event_bounded_defensive_force",
        1420,
        "Vitkov Hill, Prague, Bohemia",
        (
            "Bounded to the small hill defenders and Prague reinforcement at "
            "Vitkov. No rating is inherited by Hussites, Prague, Taborites, the "
            "Czech people, or any modern state."
        ),
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_vhu_vitkov"],
    ),
    _entity(
        _VITKOV_CRUSADER_ID,
        "Meissen-Austrian crusader assault force at Vitkov Hill (1420)",
        "event_bounded_assault_force",
        1420,
        "Vitkov Hill, Prague, Bohemia",
        (
            "Bounded to the mounted assault contingent, chiefly from Meissen and "
            "Austria, committed against the hill works. No rating is inherited by "
            "Hungary, the Empire, Germans, Austrians, or any modern state."
        ),
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_vhu_vitkov"],
    ),
    _entity(
        _BOR_HUSSITE_ID,
        "Zizka's Taborite field force at Pansky Bor (1420)",
        "event_bounded_field_force",
        1420,
        "Pansky Bor (Maly Bor), Bohemia",
        (
            "Bounded to Zizka's force defending near Pansky Bor on 12 October. No "
            "rating is inherited by Hussites generally, another Taborite army, "
            "Bohemia, or any modern state."
        ),
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_husitstvi_maly_bor"],
    ),
    _entity(
        _BOR_ROYALIST_ID,
        "Rosenberg-Svamberk-Plauen royalist coalition at Pansky Bor (1420)",
        "event_bounded_coalition",
        1420,
        "Pansky Bor (Maly Bor), Bohemia",
        (
            "Bounded to the south- and west-Bohemian Catholic coalition assembled "
            "for this action. No rating is inherited by a Habsburg empire, the "
            "named lords separately, Germans, or any modern state."
        ),
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_husitstvi_maly_bor"],
    ),
    _entity(
        _VYSEHRAD_HUSSITE_ID,
        "Prague-Orebite-Tabor field coalition at Vysehrad (1420)",
        "event_bounded_field_coalition",
        1420,
        "Pankrac plain and Vysehrad, Prague, Bohemia",
        (
            "Bounded to the Prague-led coalition holding the siege lines on 1 "
            "November. No rating is inherited by Hussites generally, any member "
            "town or faction, the Czech people, or any modern state."
        ),
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_prague2_vysehrad"],
    ),
    _entity(
        _VYSEHRAD_CRUSADER_ID,
        "Sigismund's crusader relief army at Vysehrad (1420)",
        "event_bounded_relief_army",
        1420,
        "Pankrac plain and Vysehrad, Prague, Bohemia",
        (
            "Bounded to Sigismund's German, Hungarian, Silesian, Lusatian, Czech, "
            "and Moravian relief contingents in this battle. No rating is inherited "
            "by those polities or peoples, the Empire, or any modern state."
        ),
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_prague2_vysehrad"],
    ),
    _entity(
        _ZATEC_HUSSITE_ID,
        "Zatec Hussite garrison and civic defenders (1421)",
        "event_bounded_siege_defenders",
        1421,
        "Zatec, Bohemia",
        (
            "Bounded to the armed garrison and civic defense of Zatec during the "
            "Second Crusade siege. No rating is inherited by Hussites, the city in "
            "other years, Bohemia, or any modern state."
        ),
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_hardy_zatec"],
    ),
    _entity(
        _ZATEC_CRUSADER_ID,
        "Western Second Crusade besieging army at Zatec (1421)",
        "event_bounded_siege_force",
        1421,
        "Zatec, Bohemia",
        (
            "Bounded to the western imperial and princely contingents that besieged "
            "Zatec and disintegrated on 2 October. No rating is inherited by the "
            "Holy Roman Empire, its estates, Germans generally, or any modern state."
        ),
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_hardy_zatec"],
    ),
    _entity(
        _VLADAR_HUSSITE_ID,
        "Zizka's retreating Hussite force at Vladar Hill (1421)",
        "event_bounded_defensive_force",
        1421,
        "Vladar Hill near Zlutice, Bohemia",
        (
            "Bounded to the force that defended its wagon position and broke away "
            "from Vladar. No rating is inherited by Hussites generally, Zizka's "
            "other armies, Bohemia, or any modern state."
        ),
        [
            "wave8_hussites_archaeological_atlas_vladar",
            "wave8_hussites_fudge_chronicle",
        ],
    ),
    _entity(
        _VLADAR_LANDFRIED_ID,
        "Pilsen Landfrieden pursuit force at Vladar Hill (1421)",
        "event_bounded_pursuit_force",
        1421,
        "Vladar Hill near Zlutice, Bohemia",
        (
            "Bounded to the Pilsen Landfrieden force surrounding Zizka at Vladar. "
            "No rating is inherited by Pilsen, Catholic Bohemian estates, Germans, "
            "or any modern state."
        ),
        [
            "wave8_hussites_archaeological_atlas_vladar",
            "wave8_hussites_fudge_chronicle",
        ],
    ),
    _entity(
        _KUTNA_CAMPAIGN_HUSSITE_ID,
        "Prague-Tabor Hussite counteroffensive army (January 1422)",
        "campaign_bounded_field_army",
        1422,
        "Nebovidy-Habry-Nemecky Brod campaign, Bohemia",
        (
            "Bounded to the joined Prague and Tabor forces counterattacking from "
            "Kolin through Nemecky Brod in January 1422. No rating is inherited by "
            "Hussites generally, either faction in other campaigns, or any modern state."
        ),
        ["wave8_hussites_papajik_kutna", "wave8_hussites_vhu_kutna_brod"],
    ),
    _entity(
        _NEBOVIDY_CRUSADER_ID,
        "Sigismund's crusader resistance force at Nebovidy (1422)",
        "event_bounded_field_force",
        1422,
        "Nebovidy near Kutna Hora, Bohemia",
        (
            "Bounded to the dispersed royal-crusader troops attempting resistance "
            "before Nebovidy on 6 January. No rating is inherited by Hungary, "
            "Austria, the Empire, crusaders generally, or any modern state."
        ),
        ["wave8_hussites_papajik_kutna", "wave8_hussites_vhu_kutna_brod"],
    ),
    _entity(
        _HABRY_CRUSADER_ID,
        "Sigismund's crusader rear guard at Habry (1422)",
        "event_bounded_rear_guard",
        1422,
        "Habry, Bohemia",
        (
            "Bounded to the rear guard ordered to delay the Hussite pursuit at "
            "Habry. No rating is inherited by Hungary, German crusaders, Sigismund's "
            "whole army, or any modern state."
        ),
        ["wave8_hussites_papajik_kutna", "wave8_hussites_vhu_kutna_brod"],
    ),
    _entity(
        _BROD_CRUSADER_ID,
        "Sigismund's crusader defenders at Nemecky Brod (1422)",
        "event_bounded_urban_defenders",
        1422,
        "Nemecky Brod (Havlickuv Brod), Bohemia",
        (
            "Bounded to the crusader elements that formed for defense in Nemecky "
            "Brod on 9-10 January. No rating is inherited by Hungary, the town, "
            "German crusaders generally, or any modern state."
        ),
        ["wave8_hussites_papajik_kutna", "wave8_hussites_vhu_kutna_brod"],
    ),
    _entity(
        _HORICE_HUSSITE_ID,
        "Zizka's Orebite field army at Horice (1423)",
        "event_bounded_field_army",
        1423,
        "Gothard Hill at Horice, Bohemia",
        (
            "Bounded to Zizka's field army at Horice in April 1423. No rating is "
            "inherited by Hussites, Orebites, Zizka's other armies, Bohemia, or any "
            "modern state."
        ),
        ["wave8_hussites_cornej_zizka", "wave8_hussites_horice_history"],
    ),
    _entity(
        _HORICE_LORDS_ID,
        "Cenek of Vartenberk's Lords' Union force at Horice (1423)",
        "event_bounded_field_coalition",
        1423,
        "Gothard Hill at Horice, Bohemia",
        (
            "Bounded to the Bohemian lordly coalition led by Cenek of Vartenberk "
            "at Horice. No rating is inherited by a Habsburg empire, the Lords' "
            "Union in other actions, Bohemia, or any modern state."
        ),
        ["wave8_hussites_cornej_zizka", "wave8_hussites_horice_history"],
    ),
    _entity(
        _SKALICE_HUSSITE_ID,
        "Zizka-Hradec field force at Ceska Skalice (1424)",
        "event_bounded_field_force",
        1424,
        "Ceska Skalice, Bohemia",
        (
            "Bounded to Zizka and the Hradec contingent at Ceska Skalice on 6 "
            "January. No rating is inherited by Hussites, Hradec, Zizka's other "
            "forces, the Czech people, or any modern state."
        ),
        ["wave8_hussites_ceska_skalice_history", "wave8_hussites_cornej_zizka"],
    ),
    _entity(
        _SKALICE_LORDS_ID,
        "Eastern Bohemian Catholic lords' force at Skalice (1424)",
        "event_bounded_field_coalition",
        1424,
        "Ceska Skalice, Bohemia",
        (
            "Bounded to the named eastern-Bohemian Catholic lords and their men at "
            "Skalice. No rating is inherited by royalist barons generally, their "
            "families, Bohemia, or any modern state."
        ),
        ["wave8_hussites_ceska_skalice_history", "wave8_hussites_cornej_zizka"],
    ),
    _entity(
        _AUSSIG_HUSSITE_ID,
        "Combined Hussite field coalition at Aussig (1426)",
        "event_bounded_field_coalition",
        1426,
        "Behani heights near Usti nad Labem, Bohemia",
        (
            "Bounded to the Taborite, Orphan, Prague, and Lithuanian-linked forces "
            "assembled at Aussig on 16 June. No rating is inherited by Hussites "
            "generally, any member faction, Bohemia, or any modern state."
        ),
        ["wave8_hussites_querengaesser_aussig", "wave8_hussites_vhu_aussig"],
    ),
    _entity(
        _AUSSIG_RELIEF_ID,
        "Saxon-Meissen-Thuringian-Lusatian relief army at Aussig (1426)",
        "event_bounded_relief_army",
        1426,
        "Behani heights near Usti nad Labem, Bohemia",
        (
            "Bounded to the regional relief contingents that assaulted the Hussite "
            "wagon fort at Aussig. No rating is inherited by Germans generally, "
            "Saxony, Meissen, Thuringia, Lusatia, or any modern state."
        ),
        ["wave8_hussites_querengaesser_aussig", "wave8_hussites_vhu_aussig"],
    ),
)


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str = "day",
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


_ROW_HASHES = {
    "hced-Aussig1426-1": "9c13e1a73ff676dce63ce047175186d9a6ea667932c9f1309095d27a0ba0418a",
    "hced-Bor Pansky1420-1": "bdc250c918919b6e78024f7f82afe8770b19e2dbc6a2fd2f8c8621d2a019cea0",
    "hced-Habry1422-1": "f4c479cbec3400776a625b3283f567d76d03c07e54b9acdf1f27d367f675b322",
    "hced-Horice1423-1": "62a97f84db55d81bf317a4f4e3fc8cecc2821bb57639737c86016bc76a8d19f1",
    "hced-Kutna Hora1421-1": "1dfaeed1298adef4f1f2884d2bf194138daa81060df1613740560ecc9e013069",
    "hced-Nebovidy1422-1": "533cf7f274b37ccd55306483d1b9934b9ef2ae2dd5d5fb338c0cf8a535181b1f",
    "hced-Nemecky Brod1422-1": "e611517f7a12b77a0c7fd371fe36d932634d77af32e79265008a3e7ba040010a",
    "hced-Porici1420-1": "dac2bf7ba4f20d570116dfe9ddc643639d0a72abf33669d9e6d07a768f9b4105",
    "hced-Skalice1424-1": "1536af2f8b8e123203e3e42588043726b9e977fce622c96131bc2233dc488661",
    "hced-Vitkov Hill1420-1": "d395932b8ff1c9e470ca879f1fab796792df1058c8aeb852dc8729e6f14c4a5d",
    "hced-Vladar1421-1": "bd1647e64134313eafe30d855b2553bb3a77d31cb91af97735ebe1c8b647834e",
    "hced-Vysehrad1420-1": "8831cd0aa7c47920cbae1e51bd69e6ac9692c9bdaa34404ad101cf43db80f598",
    "hced-Zatec1421-1": "1e99ddf6f96f2cf434b6f5d75c05590fad0f85f017e1de9c5261c23cb88114e3",
    "hced-Zwettl-1": "ae3514bdfa173cb574a252cc1b4cac70398e97b10e1d1acfea006ec73324e3e5",
}

_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_HUSSITES_SOURCES
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    war_type: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_HUSSITES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Porici1420-1": _contract(
        "hced-Porici1420-1",
        _canonical(
            "Battle of Porici nad Sazavou",
            1420,
            "night of 19-20 May 1420",
            date_precision="day_range",
        ),
        "hussite_war_1420",
        [_PORICI_HUSSITE_ID],
        [_PORICI_ROYALIST_ID],
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_posazavi_porici"],
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_posazavi_porici"],
        (
            "The Taborite column defeated the Bohemian Catholic-royalist force "
            "that tried to stop its march to Prague. HCED's Habsburg label is "
            "replaced by the exact interception force."
        ),
        "civil_war",
        confidence=0.91,
    ),
    "hced-Vitkov Hill1420-1": _contract(
        "hced-Vitkov Hill1420-1",
        _canonical("Battle of Vitkov Hill", 1420, "14 July 1420"),
        "hussite_war_1420",
        [_VITKOV_HUSSITE_ID],
        [_VITKOV_CRUSADER_ID],
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_vhu_vitkov"],
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_vhu_vitkov"],
        (
            "The hill defenders, reinforced from Prague, repelled and routed the "
            "Meissen-Austrian assault contingent. The row's Hungary label is not "
            "projected onto Sigismund's whole host."
        ),
        "religious_war",
        confidence=0.96,
    ),
    "hced-Bor Pansky1420-1": _contract(
        "hced-Bor Pansky1420-1",
        _canonical("Battle of Pansky Bor (Maly Bor)", 1420, "12 October 1420"),
        "hussite_war_1420",
        [_BOR_HUSSITE_ID],
        [_BOR_ROYALIST_ID],
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_husitstvi_maly_bor"],
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_husitstvi_maly_bor"],
        (
            "Zizka's Taborite force held its defensive position and defeated the "
            "Rosenberg-Svamberk-Plauen coalition. The opposing force was not a "
            "fifteenth-century Habsburg empire."
        ),
        "civil_war",
        confidence=0.90,
    ),
    "hced-Vysehrad1420-1": _contract(
        "hced-Vysehrad1420-1",
        _canonical("Battle of Vysehrad", 1420, "1 November 1420"),
        "hussite_war_1420",
        [_VYSEHRAD_HUSSITE_ID],
        [_VYSEHRAD_CRUSADER_ID],
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_prague2_vysehrad"],
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_prague2_vysehrad"],
        (
            "The Prague-led coalition defeated Sigismund's multi-regional relief "
            "army on the Pankrac plain; the Vysehrad garrison did not join the "
            "attack and is not rated as part of the losing side."
        ),
        "religious_war",
        confidence=0.94,
    ),
    "hced-Zatec1421-1": _contract(
        "hced-Zatec1421-1",
        _canonical(
            "Siege of Zatec",
            1421,
            "September-2 October 1421",
            date_precision="month_to_day_range",
            granularity="siege",
        ),
        "second_crusade_zatec_1421",
        [_ZATEC_HUSSITE_ID],
        [_ZATEC_CRUSADER_ID],
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_hardy_zatec"],
        ["wave8_hussites_fudge_chronicle", "wave8_hussites_hardy_zatec"],
        (
            "Zatec's armed defenders withstood the western Second Crusade siege "
            "until the besieging army disintegrated and fled on 2 October. Neither "
            "side is flattened to Hussites or the Holy Roman Empire generally."
        ),
        "religious_war",
        confidence=0.94,
    ),
    "hced-Vladar1421-1": _contract(
        "hced-Vladar1421-1",
        _canonical(
            "Defense and breakout at Vladar Hill",
            1421,
            "mid-November 1421",
            date_precision="month_uncertain",
            granularity="defensive_breakout",
        ),
        "western_bohemian_campaign_1421",
        [_VLADAR_HUSSITE_ID],
        [_VLADAR_LANDFRIED_ID],
        [
            "wave8_hussites_archaeological_atlas_vladar",
            "wave8_hussites_fudge_chronicle",
        ],
        [
            "wave8_hussites_archaeological_atlas_vladar",
            "wave8_hussites_fudge_chronicle",
        ],
        (
            "The reviewed actor achieved the bounded defensive objective: it "
            "resisted the Pilsen Landfrieden on Vladar and broke away intact. This "
            "does not assert a wider campaign victory or rate the city of Pilsen."
        ),
        "civil_war",
        confidence=0.88,
    ),
    "hced-Nebovidy1422-1": _contract(
        "hced-Nebovidy1422-1",
        _canonical("Battle of Nebovidy", 1422, "6 January 1422"),
        "kutna_brod_counteroffensive_1422",
        [_KUTNA_CAMPAIGN_HUSSITE_ID],
        [_NEBOVIDY_CRUSADER_ID],
        ["wave8_hussites_papajik_kutna", "wave8_hussites_vhu_kutna_brod"],
        ["wave8_hussites_papajik_kutna", "wave8_hussites_vhu_kutna_brod"],
        (
            "The joined Prague-Tabor counteroffensive defeated the attempted "
            "crusader resistance before Nebovidy and precipitated Sigismund's "
            "withdrawal. The loser is the local resistance force, not Hungary."
        ),
        "religious_war",
        confidence=0.91,
    ),
    "hced-Habry1422-1": _contract(
        "hced-Habry1422-1",
        _canonical("Battle of Habry", 1422, "8 January 1422"),
        "kutna_brod_counteroffensive_1422",
        [_KUTNA_CAMPAIGN_HUSSITE_ID],
        [_HABRY_CRUSADER_ID],
        ["wave8_hussites_papajik_kutna", "wave8_hussites_vhu_kutna_brod"],
        ["wave8_hussites_papajik_kutna", "wave8_hussites_vhu_kutna_brod"],
        (
            "The pursuing Prague-Tabor army crushed the rear guard assigned to "
            "delay it at Habry. The bounded rear guard replaces HCED's composite "
            "Hungary-and-German-crusaders label."
        ),
        "religious_war",
        confidence=0.95,
    ),
    "hced-Nemecky Brod1422-1": _contract(
        "hced-Nemecky Brod1422-1",
        _canonical(
            "Battle and storm of Nemecky Brod",
            1422,
            "9-10 January 1422",
            date_precision="day_range",
            granularity="battle_and_storm",
        ),
        "kutna_brod_counteroffensive_1422",
        [_KUTNA_CAMPAIGN_HUSSITE_ID],
        [_BROD_CRUSADER_ID],
        ["wave8_hussites_papajik_kutna", "wave8_hussites_vhu_kutna_brod"],
        ["wave8_hussites_papajik_kutna", "wave8_hussites_vhu_kutna_brod"],
        (
            "The Hussite field army defeated the formed crusader defenders and "
            "stormed Nemecky Brod. Civilians killed after entry are not rated "
            "participants, and the raw Hungary label is not retained."
        ),
        "religious_war",
        confidence=0.94,
    ),
    "hced-Horice1423-1": _contract(
        "hced-Horice1423-1",
        _canonical(
            "Battle of Horice",
            1423,
            "April 1423",
            date_precision="month",
        ),
        "zizka_internal_campaigns_1423_1424",
        [_HORICE_HUSSITE_ID],
        [_HORICE_LORDS_ID],
        ["wave8_hussites_cornej_zizka", "wave8_hussites_horice_history"],
        ["wave8_hussites_cornej_zizka", "wave8_hussites_horice_history"],
        (
            "Zizka's field army defeated the Lords' Union force led by Cenek of "
            "Vartenberk on Gothard Hill. The source actor is a Bohemian coalition, "
            "not HCED's anachronistic Habsburg Empire."
        ),
        "civil_war",
        confidence=0.91,
    ),
    "hced-Skalice1424-1": _contract(
        "hced-Skalice1424-1",
        _canonical("Battle of Ceska Skalice", 1424, "6 January 1424"),
        "zizka_internal_campaigns_1423_1424",
        [_SKALICE_HUSSITE_ID],
        [_SKALICE_LORDS_ID],
        [
            "wave8_hussites_ceska_skalice_history",
            "wave8_hussites_cornej_zizka",
        ],
        [
            "wave8_hussites_ceska_skalice_history",
            "wave8_hussites_cornej_zizka",
        ],
        (
            "The Old Czech Annals tradition and the museum review identify Zizka "
            "and the Hradec contingent defeating the named eastern-Bohemian lords. "
            "The row's generic Royalist Barons label is not installed."
        ),
        "civil_war",
        confidence=0.90,
    ),
    "hced-Aussig1426-1": _contract(
        "hced-Aussig1426-1",
        _canonical("Battle of Usti nad Labem (Aussig)", 1426, "16 June 1426"),
        "aussig_campaign_1426",
        [_AUSSIG_HUSSITE_ID],
        [_AUSSIG_RELIEF_ID],
        ["wave8_hussites_querengaesser_aussig", "wave8_hussites_vhu_aussig"],
        ["wave8_hussites_querengaesser_aussig", "wave8_hussites_vhu_aussig"],
        (
            "The combined Hussite field coalition repelled the assault on its "
            "wagon fort and routed the Saxon-Meissen-Thuringian-Lusatian relief "
            "army. The loser is not a generic German Catholic identity."
        ),
        "religious_war",
        confidence=0.97,
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: dict[str, Any],
    category: str,
    reason: str,
    evidence_refs: Iterable[str],
    reviewed_actors: Iterable[str],
    reviewed_granularity: str,
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
        "reviewed_granularity": reviewed_granularity,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "held_hced_owner",
        },
    }


WAVE8_HUSSITES_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Kutna Hora1421-1": _hold(
        "hced-Kutna Hora1421-1",
        _canonical(
            "Kutna Hora battle, occupation, and breakout",
            1421,
            "21-22 December 1421",
            date_precision="day_range",
            granularity="composite_battle_occupation_breakout",
        ),
        "row_conflates_distinct_actors_and_opposed_tactical_phases",
        (
            "The reviewed sources distinguish Catholic infiltration and occupation "
            "of Kutna Hora, the killing of the small Hussite element left inside, "
            "and the field army's orderly breakout. The peer-reviewed study says "
            "the field army withdrew but was not defeated. HCED's single Hungary "
            "win cannot be attached to one event-bounded opponent without splitting "
            "the row; the result remains unknown and is never a draw."
        ),
        [
            "wave8_hussites_fudge_chronicle",
            "wave8_hussites_papajik_kutna",
            "wave8_hussites_vhu_kutna_brod",
        ],
        [
            "Sigismund's attacking army and Catholic Kutna Hora infiltrators",
            "Hussite field army outside Kutna Hora",
            "small Hussite defending element left inside Kutna Hora",
        ],
        "composite_battle_occupation_breakout",
    ),
    "hced-Zwettl-1": _hold(
        "hced-Zwettl-1",
        _canonical("Battle near Zwettl", 1427, "25 March 1427"),
        "reciprocal_two_phase_tactical_outcome",
        (
            "Zwettl's municipal archival history records an Austrian relief force "
            "routing the Hussites, then stopping to plunder the wagon fort, after "
            "which the regrouped Hussites counterattacked and drove the Austrians "
            "into the city. The Hussites withdrew three days later. The undivided "
            "row does not identify which phase its winner describes, so the overall "
            "tactical result remains unknown and is never a draw."
        ),
        ["wave8_hussites_theisen_austria", "wave8_hussites_zwettl_history"],
        [
            "Prokop Holy's Hussite field army near Zwettl",
            "Austrian relief army assembled by Duke Albrecht V",
        ],
        "reciprocal_two_phase_engagement",
    ),
}


WAVE8_HUSSITES_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_HUSSITES_CROSS_LANE_DISPOSITIONS = (
    WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS
)
WAVE8_HUSSITES_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_HUSSITES_HOLDS,
    **WAVE8_HUSSITES_TERMINAL_EXCLUSIONS,
}
WAVE8_HUSSITES_EXCLUSIONS = WAVE8_HUSSITES_TERMINAL_EXCLUSIONS

WAVE8_HUSSITES_CONTRACT_IDS = frozenset(WAVE8_HUSSITES_CONTRACTS)
WAVE8_HUSSITES_HOLD_IDS = frozenset(WAVE8_HUSSITES_HOLDS)
WAVE8_HUSSITES_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_HUSSITES_TERMINAL_EXCLUSIONS
)
WAVE8_HUSSITES_EXCLUSION_IDS = WAVE8_HUSSITES_TERMINAL_EXCLUSION_IDS
WAVE8_HUSSITES_EXTERNAL_OWNER_IDS = frozenset(
    WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS
)
WAVE8_HUSSITES_RESERVED_IDS = (
    WAVE8_HUSSITES_CONTRACT_IDS
    | WAVE8_HUSSITES_HOLD_IDS
    | WAVE8_HUSSITES_TERMINAL_EXCLUSION_IDS
)
WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


WAVE8_HUSSITES_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Aussig1426-1": {
        "actions": ["withhold_point"],
        "reason": (
            "HCED gives the Usti city coordinate, while the battle was on the "
            "Behani heights; VHU notes that mining and reclamation destroyed the "
            "original terrain."
        ),
    },
    "hced-Bor Pansky1420-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The staged Maly Bor locality is not independently sourced as a precise "
            "point for the defensive position and battlefield footprint."
        ),
    },
    "hced-Habry1422-1": {
        "actions": ["withhold_point"],
        "reason": "The Habry settlement coordinate is not a source-audited battlefield point.",
    },
    "hced-Horice1423-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources locate the battle on Gothard Hill but do not "
            "authenticate HCED's staged coordinate as the battle point."
        ),
    },
    "hced-Nebovidy1422-1": {
        "actions": ["withhold_point"],
        "reason": (
            "A village coordinate does not establish the field position before "
            "Nebovidy where crusader resistance was attempted."
        ),
    },
    "hced-Nemecky Brod1422-1": {
        "actions": ["withhold_country", "withhold_point"],
        "reason": (
            "HCED assigns Slovakia to Nemecky Brod (modern Havlickuv Brod in "
            "Czechia), and a town coordinate cannot represent the battle-and-storm "
            "footprint."
        ),
    },
    "hced-Porici1420-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The staged locality is not independently established as the night "
            "battle's precise field position."
        ),
    },
    "hced-Skalice1424-1": {
        "actions": ["withhold_point"],
        "reason": (
            "HCED's point is far from Ceska Skalice and cannot represent the "
            "reviewed 6 January 1424 engagement."
        ),
    },
    "hced-Vitkov Hill1420-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The action involved hill works, an assault route, and a Prague relief "
            "counterattack; HCED's single landmark point is not source-provenanced."
        ),
    },
    "hced-Vladar1421-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The Archaeological Atlas locates the defended Vladar hill well east "
            "of HCED's staged longitude, so the point is not retained."
        ),
    },
    "hced-Vysehrad1420-1": {
        "actions": ["withhold_point"],
        "reason": (
            "HCED points to Vysehrad, while the field battle occurred across the "
            "Pankrac siege lines; a fortress centroid is not the battle footprint."
        ),
    },
    "hced-Zatec1421-1": {
        "actions": ["withhold_point"],
        "reason": "A city-centre coordinate cannot represent the 1421 siege footprint.",
    },
}
WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_HUSSITES_LOCATION_QUARANTINE_REASONS
)
WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Nemecky Brod1422-1"}
)
WAVE8_HUSSITES_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_HUSSITES_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_HUSSITES_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_HUSSITES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_HUSSITES_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS,
    **WAVE8_HUSSITES_IWBD_DUPLICATE_DISPOSITIONS,
    **WAVE8_HUSSITES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
}


def _duplicate_audit(year: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": sorted({normalize_label(alias) for alias in aliases}),
        "years": [year, year],
    }


WAVE8_HUSSITES_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Aussig1426-1": _duplicate_audit(
        1426,
        "Aussig",
        "Battle of Aussig",
        "Battle of Usti nad Labem",
        "Battle of Usti nad Labem (Aussig)",
        "Usti nad Labem",
    ),
    "hced-Bor Pansky1420-1": _duplicate_audit(
        1420,
        "Battle of Maly Bor",
        "Battle of Pansky Bor",
        "Battle of Pansky Bor (Maly Bor)",
        "Bor Pansky",
        "Maly Bor",
        "Pansky Bor",
    ),
    "hced-Habry1422-1": _duplicate_audit(
        1422,
        "Battle of Habry",
        "Habry",
    ),
    "hced-Horice1423-1": _duplicate_audit(
        1423,
        "Battle of Horice",
        "Horice",
    ),
    "hced-Kutna Hora1421-1": _duplicate_audit(
        1421,
        "Battle of Kutna Hora",
        "Capture of Kutna Hora",
        "Kutna Hora",
        "Kutna Hora battle, occupation, and breakout",
        "Kuttenberg",
    ),
    "hced-Nebovidy1422-1": _duplicate_audit(
        1422,
        "Battle of Nebovidy",
        "Nebovidy",
    ),
    "hced-Nemecky Brod1422-1": _duplicate_audit(
        1422,
        "Battle and storm of Nemecky Brod",
        "Battle of Deutschbrod",
        "Battle of Nemecky Brod",
        "Deutschbrod",
        "Havlickuv Brod",
        "Nemecky Brod",
    ),
    "hced-Porici1420-1": _duplicate_audit(
        1420,
        "Battle of Porici",
        "Battle of Porici nad Sazavou",
        "Porici",
        "Porici nad Sazavou",
    ),
    "hced-Skalice1424-1": _duplicate_audit(
        1424,
        "Battle of Ceska Skalice",
        "Battle of Skalice",
        "Ceska Skalice",
        "Skalice",
    ),
    "hced-Vitkov Hill1420-1": _duplicate_audit(
        1420,
        "Battle of Vitkov",
        "Battle of Vitkov Hill",
        "Vitkov",
        "Vitkov Hill",
    ),
    "hced-Vladar1421-1": _duplicate_audit(
        1421,
        "Battle of Vladar",
        "Defense and breakout at Vladar Hill",
        "Vladar",
        "Vladar Hill",
    ),
    "hced-Vysehrad1420-1": _duplicate_audit(
        1420,
        "Battle of Vysehrad",
        "Vysehrad",
    ),
    "hced-Zatec1421-1": _duplicate_audit(
        1421,
        "Saaz",
        "Siege of Saaz",
        "Siege of Zatec",
        "Zatec",
    ),
    "hced-Zwettl-1": _duplicate_audit(
        1427,
        "Battle near Zwettl",
        "Battle of Zwettl",
        "Siege of Zwettl",
        "Zwettl",
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_HUSSITES_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_HUSSITES_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_HUSSITES_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_HUSSITES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS),
        "external_owner_dispositions": WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS,
        "holds": WAVE8_HUSSITES_HOLDS,
        "integration_dispositions": WAVE8_HUSSITES_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_HUSSITES_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_HUSSITES_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_HUSSITES_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_HUSSITES_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_HUSSITES_SOURCES,
        "terminal_exclusions": WAVE8_HUSSITES_TERMINAL_EXCLUSIONS,
    }


def wave8_hussites_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label adjudication."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_HUSSITES_FINAL_AUDIT_SIGNATURE = (
    "1450fa3f575c25c8b53a3a65dd92781d41547641241f05e8e6dcb22dcc1b39bf"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_HUSSITES_CONTRACTS),
        len(WAVE8_HUSSITES_HOLDS),
        len(WAVE8_HUSSITES_TERMINAL_EXCLUSIONS),
        len(WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS),
    ) != (12, 2, 0, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_HUSSITES_ENTITIES), len(WAVE8_HUSSITES_SOURCES)) != (22, 16):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if (
        WAVE8_HUSSITES_RESERVED_IDS | WAVE8_HUSSITES_EXTERNAL_OWNER_IDS
        != WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    dispositions = (
        WAVE8_HUSSITES_CONTRACT_IDS,
        WAVE8_HUSSITES_HOLD_IDS,
        WAVE8_HUSSITES_TERMINAL_EXCLUSION_IDS,
        WAVE8_HUSSITES_EXTERNAL_OWNER_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(len(dispositions))
        for j in range(i + 1, len(dispositions))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if wave8_hussites_audit_signature() != WAVE8_HUSSITES_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_HUSSITES_SOURCES}
    if len(source_by_id) != len(WAVE8_HUSSITES_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({source["source_family_id"] for source in WAVE8_HUSSITES_SOURCES}) != len(
        WAVE8_HUSSITES_SOURCES
    ):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_HUSSITES_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_HUSSITES_ENTITIES}
    if len(entity_by_id) != len(WAVE8_HUSSITES_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    for entity in WAVE8_HUSSITES_ENTITIES:
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} identity is not event/campaign bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern state" not in note:
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if normalize_label(entity["name"]) in {"hussite", "hussites"}:
            raise ValueError(f"{_LANE_NAME} installed a generic Hussite identity")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_new_entities: set[str] = set()
    used_sources: set[str] = set()
    allowed_granularities = {
        "battle_and_storm",
        "defensive_breakout",
        "engagement",
        "siege",
    }
    for candidate_id, contract in WAVE8_HUSSITES_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["granularity"] not in allowed_granularities:
            raise ValueError(f"{_LANE_NAME} promoted unsupported granularity")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses a non-bounded identity")
        used_new_entities.update(set(side_1) | set(side_2))
        year = int(canonical["year_low"])
        for entity_id in set(side_1) | set(side_2):
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["actor_override"] is not True
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} outcome or actor policy drifted")
        if contract["duplicate_ownership"] != {
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
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")

    forbidden_hold_keys = {
        "losers",
        "outcome_source_family_ids",
        "outcome_source_ids",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
        "winners",
    }
    for candidate_id, hold in WAVE8_HUSSITES_HOLDS.items():
        if hold["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} hold hash drifted")
        if forbidden_hold_keys & set(hold):
            raise ValueError(f"{_LANE_NAME} hold contains a rateable result")
        if (
            hold["disposition"] != "hold"
            or hold["reviewed_outcome"] != "unknown"
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
            or "never a draw" not in str(hold["hold_reason"]).casefold()
        ):
            raise ValueError(f"{_LANE_NAME} unknown outcome became a draw or win")
        if hold["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "held_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} hold ownership drifted")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence drifted")
        used_sources.update(evidence)

    used_sources.update(
        source_id
        for entity in WAVE8_HUSSITES_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_HUSSITES_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited terminal exclusion")
    if WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited external owner")
    if WAVE8_HUSSITES_CROSS_LANE_DISPOSITIONS is not (
        WAVE8_HUSSITES_EXTERNAL_OWNER_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} external ownership alias drifted")
    if (
        WAVE8_HUSSITES_OUTCOME_OVERRIDES
        or WAVE8_HUSSITES_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_HUSSITES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_HUSSITES_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")

    if WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS != WAVE8_HUSSITES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS != {
        "hced-Nemecky Brod1422-1"
    }:
        raise ValueError(f"{_LANE_NAME} country quarantine contract changed")
    if not WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS <= WAVE8_HUSSITES_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} quarantines a nonpromotion")
    if set(WAVE8_HUSSITES_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location-review inventory changed")
    for candidate_id, review in WAVE8_HUSSITES_LOCATION_QUARANTINE_REASONS.items():
        if not review["reason"] or not _is_sorted_unique(review["actions"]):
            raise ValueError(f"{_LANE_NAME} location review is not canonical")
        expected_actions = {"withhold_point"}
        if candidate_id in WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS:
            expected_actions.add("withhold_country")
        if set(review["actions"]) != expected_actions:
            raise ValueError(f"{_LANE_NAME} location-review action drifted")

    if set(WAVE8_HUSSITES_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    audited_keys: set[tuple[int, str]] = set()
    for candidate_id, audit in WAVE8_HUSSITES_IWBD_ZERO_OVERLAP_AUDIT.items():
        aliases = list(map(str, audit["aliases"]))
        years = list(map(int, audit["years"]))
        if not aliases or not _is_sorted_unique(aliases):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if any(alias != normalize_label(alias) for alias in aliases):
            raise ValueError(f"{_LANE_NAME} duplicate alias is not normalized")
        if years != [years[0], years[0]]:
            raise ValueError(f"{_LANE_NAME} duplicate year window drifted")
        audited_keys.update((years[0], alias) for alias in aliases)
        disposition = (
            WAVE8_HUSSITES_CONTRACTS.get(candidate_id)
            or WAVE8_HUSSITES_NONPROMOTIONS.get(candidate_id)
        )
        canonical = disposition["canonical_event"]
        canonical_key = (
            int(canonical["year_low"]),
            normalize_label(canonical["name"]),
        )
        if canonical_key not in audited_keys:
            raise ValueError(f"{_LANE_NAME} canonical duplicate audit is incomplete")


def _is_exact_hussites_label(value: Any) -> bool:
    return normalize_label(value) == "hussites"


def validate_wave8_hussites_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all fourteen exact-label rows and immutable queue fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_HUSSITES_CONTRACTS,
        WAVE8_HUSSITES_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_hussites_label(row.get("side_1_raw"))
        or _is_exact_hussites_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Hussites inventory changed: {sorted(exact_label_ids)}"
        )
    return {
        "external_owner_contracts": len(WAVE8_HUSSITES_EXTERNAL_OWNER_IDS),
        "holds": len(WAVE8_HUSSITES_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": (
            result["reviewed_hced_rows"] + len(WAVE8_HUSSITES_EXTERNAL_OWNER_IDS)
        ),
        "terminal_exclusions": len(WAVE8_HUSSITES_TERMINAL_EXCLUSIONS),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        value = row.get(field)
        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        value = row.get(field)
        if isinstance(value, str):
            text = value.lstrip("-")
            if len(text) >= 4 and text[:4].isdigit():
                year = int(text[:4])
                return -year if value.startswith("-") else year
    return None


_DUPLICATE_MATCH_KEYS = {
    (year, alias)
    for audit in WAVE8_HUSSITES_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
}


def validate_wave8_hussites_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed if another queue or release lane adds an unreviewed twin."""

    validate_wave8_hussites_queue_contracts(hced_rows)
    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS
        and (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if hced_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_matches}")
    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if iwbd_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_matches}")
    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_HUSSITES_CONTRACT_IDS
        and (_row_year(event), normalize_label(event.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_matches}"
        )
    return {
        "cross_lane_hced_dispositions": len(WAVE8_HUSSITES_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_HUSSITES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(WAVE8_HUSSITES_EXTERNAL_OWNER_IDS),
        "integration_dispositions": len(WAVE8_HUSSITES_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_HUSSITES_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_HUSSITES_IWBD_ZERO_OVERLAP_AUDIT
        ),
    }


def install_wave8_hussites_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_HUSSITES_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_hussites_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_HUSSITES_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_hussites_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_hussites_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_HUSSITES_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_hussites_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_HUSSITES_CONTRACTS.values()
            ).items()
        )
    )


def wave8_hussites_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(WAVE8_HUSSITES_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(
            WAVE8_HUSSITES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_hced_dispositions": len(WAVE8_HUSSITES_EXTERNAL_OWNER_IDS),
        "holds": len(WAVE8_HUSSITES_HOLDS),
        "integration_dispositions": len(WAVE8_HUSSITES_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_HUSSITES_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_HUSSITES_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_HUSSITES_ENTITIES),
        "new_sources": len(WAVE8_HUSSITES_SOURCES),
        "newly_rated_events": len(WAVE8_HUSSITES_CONTRACTS),
        "outcome_overrides": len(WAVE8_HUSSITES_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_HUSSITES_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_HUSSITES_EXPECTED_CANDIDATE_IDS),
        "terminal_exclusions": len(WAVE8_HUSSITES_TERMINAL_EXCLUSIONS),
    }


def wave8_hussites_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_HUSSITES_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_HUSSITES_POINT_QUARANTINE_ADDITIONS,
    }
