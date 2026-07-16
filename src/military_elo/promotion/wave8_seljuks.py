"""Candidate-keyed Wave 8 audit of HCED's exact ``Seljuks`` cohort.

The locked rows use one generic label for unrelated actors: three different
Sultanate of Rum reigns, two Zengid regimes, and the Great Seljuk state.  This
lane resolves only source-attested, time-bounded actors.  It creates no
``Seljuks`` alias and leaves political transfers or disputed tactical outcomes
unrated.
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
    "WAVE8_SELJUKS_CONTRACT_IDS",
    "WAVE8_SELJUKS_CONTRACTS",
    "WAVE8_SELJUKS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SELJUKS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_SELJUKS_ENTITIES",
    "WAVE8_SELJUKS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_SELJUKS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SELJUKS_HOLD_IDS",
    "WAVE8_SELJUKS_HOLDS",
    "WAVE8_SELJUKS_INTEGRATION_DISPOSITIONS",
    "WAVE8_SELJUKS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_SELJUKS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_SELJUKS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_SELJUKS_OUTCOME_OVERRIDES",
    "WAVE8_SELJUKS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SELJUKS_RESERVED_IDS",
    "WAVE8_SELJUKS_SOURCES",
    "WAVE8_SELJUKS_TERMINAL_EXCLUSION_IDS",
    "install_wave8_seljuks_entities",
    "install_wave8_seljuks_sources",
    "promote_wave8_seljuks_contracts",
    "validate_wave8_seljuks_integration_dispositions",
    "validate_wave8_seljuks_queue_contracts",
    "wave8_seljuks_audit_signature",
    "wave8_seljuks_cohort_counts",
    "wave8_seljuks_counts",
    "wave8_seljuks_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Seljuks actor audit"
_EVENT_ID_PREFIX = "hced_wave8_seljuks_"
_GREAT_SELJUK_ID = "clio_ir_seljuk_sultanate_1040_577da931"
_MONGOL_EMPIRE_ID = "mongol_empire"

_RUM_KILIJ_ID = "rum_sultanate_kilij_arslan_i_1092_1107"
_PEOPLES_CRUSADE_ID = "peoples_crusade_asia_minor_force_1096"
_RUM_MESUD_ID = "rum_sultanate_mesud_i_1116_1156"
_GERMAN_CRUSADE_ID = "conrad_iii_german_crusader_army_1147"
_ZENGI_ID = "zengid_mosul_aleppo_imad_al_din_1127_1146"
_EDESSA_ID = "county_edessa_joscelin_ii_1131_1150"
_NUR_AL_DIN_ID = "zengid_aleppo_nur_al_din_1146_1154"
_RUM_KAYKHUSRAW_ID = "rum_sultanate_kaykhusraw_ii_1237_1246"
_BASASIRI_FORCE_ID = "al_basasiri_fatimid_aligned_field_force_1060"


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


WAVE8_SELJUKS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_seljuks_cambridge_baghdad",
        "Controlling and Developing Baghdad: Caliphs, Sultans and the Balance of Power",
        "https://www.cambridge.org/core/books/abs/seljuqs/controlling-and-developing-baghdad-caliphs-sultans-and-the-balance-of-power-in-the-abbasid-capital-mid5th11th-to-late-6th12th-centuries/F605C6E1758E5682CA57958C39E62A7B",
        "Cambridge University Press",
        "academic_book_chapter",
        "cambridge_seljuqs_baghdad",
    ),
    _source(
        "wave8_seljuks_cambridge_formation_islam",
        "A Sunni Revival?",
        "https://www.cambridge.org/highereducation/books/the-formation-of-islam/0C58C7DC69FC4FFE20933C00B54D839F/a-sunni-revival/1F645AE9E9E7FB3B067C16DB7E16D767",
        "Cambridge University Press",
        "academic_book_chapter",
        "cambridge_formation_islam",
    ),
    _source(
        "wave8_seljuks_civetot_article",
        "The First Turkish Leader against the Crusaders: Sultan Kilij Arslan I",
        "https://dergipark.org.tr/en/pub/iusarkiyat/article/438164",
        "Istanbul University, Sarkiyat Mecmuasi",
        "peer_reviewed_historical_article",
        "istanbul_university_kilij_arslan",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_seljuks_alexiad_primary",
        "Anna Komnene, The Alexiad, Book X",
        "https://sourcebooks.web.fordham.edu/source/comnena-cde.asp",
        "Fordham University Internet Medieval Sourcebook",
        "translated_primary_chronicle",
        "anna_komnene_alexiad",
        outcome=True,
    ),
    _source(
        "wave8_seljuks_tdv_mesud",
        "Mesud I",
        "https://islamansiklopedisi.org.tr/mesud-i",
        "TDV Encyclopedia of Islam",
        "scholarly_encyclopedia",
        "tdv_islam_encyclopedia_mesud",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_seljuks_iranica_rum",
        "Saljuqs III: Saljuqs of Rum",
        "https://www.iranicaonline.org/articles/saljuqs-iii/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica_saljuqs_rum",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_seljuks_oup_edessa_1144",
        "The Second Crusade, 1145-9",
        "https://academic.oup.com/book/25780/chapter-abstract/193358062",
        "Oxford University Press",
        "academic_book_chapter",
        "oxford_phillips_second_crusade",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_seljuks_cambridge_edessa_1144",
        "St Bernard of Clairvaux, the Low Countries and the Lisbon Letter",
        "https://www.cambridge.org/core/journals/journal-of-ecclesiastical-history/article/abs/st-bernard-of-clairvaux-the-low-countries-and-the-lisbon-letter-of-the-second-crusade/9E2707A74AE3CD481810EBDDB11B61A8",
        "Cambridge University Press",
        "peer_reviewed_historical_article",
        "cambridge_phillips_lisbon_letter",
        outcome=True,
    ),
    _source(
        "wave8_seljuks_cambridge_edessa_1146",
        "The Afterlife of Edessa: Remembering Frankish Rule, 1144 and After",
        "https://www.cambridge.org/core/books/syria-in-crusader-times/afterlife-of-edessa-remembering-frankish-rule-1144-and-after/F4AC432D4716A20DF947A37F44EA09FA",
        "Cambridge University Press / Edinburgh University Press",
        "academic_book_chapter",
        "mac_evitt_afterlife_edessa",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_seljuks_penn_edessa_1146",
        "Images of Authority in Edessa, 1100-1150",
        "https://www.thetbs.org/study-materials/wp-content/uploads/2023/03/The_Crusades_and_the_Christian_World_of_the_East_Rough_Tolerance.pdf",
        "University of Pennsylvania Press",
        "academic_monograph_chapter",
        "mac_evitt_rough_tolerance",
        outcome=True,
    ),
    _source(
        "wave8_seljuks_cambridge_egypt_1167",
        "The New Cambridge Medieval History, Volume IV: Egypt and Syria",
        "https://assets.cambridge.org/97805214/14104/excerpt/9780521414104_excerpt.pdf",
        "Cambridge University Press",
        "academic_reference_work",
        "new_cambridge_medieval_history_iv",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_seljuks_fordham_william_tyres_egypt",
        "William of Tyre: The Fiasco at Damascus and Revolution in Egypt",
        "https://sourcebooks.web.fordham.edu/source/tyre-cde.asp",
        "Fordham University Internet Medieval Sourcebook",
        "translated_primary_chronicle",
        "william_of_tyre_egypt_campaign",
        outcome=True,
    ),
    _source(
        "wave8_seljuks_kapetron_sources",
        "The Battle of Kaputru in the Light of Historical Sources",
        "https://dergipark.org.tr/tr/pub/ataunitaed/article/39809",
        "Ataturk University Journal of Turkic Research Institute",
        "peer_reviewed_historical_article",
        "ataturk_university_kapetron",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_seljuks_beihammer_anatolia",
        "Byzantium and the Emergence of Muslim-Turkish Anatolia, ca. 1040-1130",
        "https://kutuphane.ttk.gov.tr/details?id=588359&materialType=KT&query=Beihammer%2C+Alexander+Daniel.",
        "Routledge; Turkish Historical Society Library catalogue",
        "scholarly_monograph",
        "beihammer_muslim_turkish_anatolia",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_seljuks_iranica_bayju",
        "Bayju",
        "https://www.iranicaonline.org/articles/bayju-baiju-or-baicu-mongol-general-and-military-governor-in-northwestern-iran-fl/",
        "Encyclopaedia Iranica",
        "scholarly_encyclopedia",
        "encyclopaedia_iranica_bayju",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_seljuks_tdv_besasiri",
        "Besasiri",
        "https://islamansiklopedisi.org.tr/besasiri",
        "TDV Encyclopedia of Islam",
        "scholarly_encyclopedia",
        "tdv_islam_encyclopedia_besasiri",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_seljuks_ibn_al_jawzi_translation",
        "Information on the Seljuks in Ibn al-Jawzi's al-Muntazam, 430-485 AH",
        "https://belgeler.gov.tr/eng/full-text/32/tur",
        "Turkish Historical Society, Belgeler",
        "peer_reviewed_primary_source_translation",
        "ibn_al_jawzi_muntazam_translation",
        outcome=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: list[str],
    boundary_note: str,
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
            boundary_note
            + " No rating is inherited by a generic Seljuk, Turk, Muslim, "
            "crusader, German, Syrian, or modern-state label."
        ),
        "source_ids": sorted(source_ids),
    }


WAVE8_SELJUKS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _RUM_KILIJ_ID,
        "Sultanate of Rum under Kilij Arslan I",
        "sultanate_regime",
        1092,
        1107,
        "Anatolia",
        ["wave8_seljuks_civetot_article", "wave8_seljuks_iranica_rum"],
        "Reign-bounded Rum identity used only for the 1096 Civetot force.",
    ),
    _entity(
        _PEOPLES_CRUSADE_ID,
        "People's Crusade field force in Asia Minor",
        "campaign_force",
        1096,
        1096,
        "Northwestern Anatolia",
        ["wave8_seljuks_alexiad_primary", "wave8_seljuks_civetot_article"],
        "Campaign-bounded force destroyed near Civetot in October 1096.",
    ),
    _entity(
        _RUM_MESUD_ID,
        "Sultanate of Rum under Mesud I",
        "sultanate_regime",
        1116,
        1156,
        "Anatolia",
        ["wave8_seljuks_iranica_rum", "wave8_seljuks_tdv_mesud"],
        "Reign-bounded Rum identity used for Mesud's Second Crusade campaign.",
    ),
    _entity(
        _GERMAN_CRUSADE_ID,
        "Conrad III's German crusader army",
        "campaign_force",
        1147,
        1147,
        "Anatolia",
        ["wave8_seljuks_tdv_mesud"],
        "Campaign-bounded German royal army in the Anatolian phase of the Second Crusade.",
    ),
    _entity(
        _ZENGI_ID,
        "Zengid Atabegate of Mosul and Aleppo under Imad al-Din Zengi",
        "atabegate_regime",
        1127,
        1146,
        "Northern Mesopotamia and Syria",
        ["wave8_seljuks_oup_edessa_1144"],
        "Regime-bounded Zengid polity ending with Imad al-Din's death in 1146.",
    ),
    _entity(
        _EDESSA_ID,
        "County of Edessa under Joscelin II",
        "crusader_county_regime",
        1131,
        1150,
        "Upper Mesopotamia",
        [
            "wave8_seljuks_cambridge_edessa_1146",
            "wave8_seljuks_oup_edessa_1144",
        ],
        "Ruler-bounded county; after 1144 it denotes Joscelin's surviving western domains and restoration force, not uninterrupted possession of Edessa city.",
    ),
    _entity(
        _NUR_AL_DIN_ID,
        "Zengid Aleppo under Nur al-Din",
        "atabegate_regime",
        1146,
        1154,
        "Northern Syria",
        [
            "wave8_seljuks_cambridge_edessa_1146",
            "wave8_seljuks_penn_edessa_1146",
        ],
        "Aleppo-centered regime from Zengi's succession split through Nur al-Din's acquisition of Damascus in 1154.",
    ),
    _entity(
        _RUM_KAYKHUSRAW_ID,
        "Sultanate of Rum under Kaykhusraw II",
        "sultanate_regime",
        1237,
        1246,
        "Anatolia",
        ["wave8_seljuks_iranica_bayju", "wave8_seljuks_iranica_rum"],
        "Reign-bounded Rum identity spanning the Mongol defeat at Kose Dag.",
    ),
    _entity(
        _BASASIRI_FORCE_ID,
        "Al-Basasiri's Fatimid-aligned field force near Kufa",
        "campaign_force",
        1060,
        1060,
        "Iraq",
        ["wave8_seljuks_ibn_al_jawzi_translation", "wave8_seljuks_tdv_besasiri"],
        "Engagement-bounded force overtaken near Kufa in January 1060; it is not equated with the Fatimid state or an ethnic community.",
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
    "hced-Baghdad1055-1": "926a9a79d275b3ff54c17d6708c902a03e6012195404468386f8357ae824ac21",
    "hced-Civetot1096-1": "e44af3a2969e3a589427b9289b2a2e3ce79f73d91566652b7a5a1f8b2284d7c6",
    "hced-Dorylaeum1147-1": "19eeb036de9ac497b6d3e99856e5a6e7627fec13e2a47b8802b21d977e918b43",
    "hced-Edessa1144-1": "542403b69c559ed3ca3b1edf46cde5315e6085cdf98b19b2363708eed8818ba3",
    "hced-Edessa1146-1": "74fd84f55eba477f9a6306d762cf7279811951b9683aac826939c5b4a20b787c",
    "hced-Elasa1167-1": "5dcf271f7e7f6424815c6820d8e0b4699013ec768819cb936ab2f9016d46ad03",
    "hced-Hasankale1048-1": "fc88d6a2a76268eadaaa2e22855700237e5cd5c3691b94ddc505c196f3f0987c",
    "hced-Kose Dagh1243-1": "004d16d49718988bb4dbb23bff2ca3d4e5e132cbc2c241590441f1a663ec70ab",
    "hced-Kufah1060-1": "3ff27ae871b7fe17bac52047156ed6deb25f1e4c61593e4fbe05db8e58b90754",
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: list[str],
    side_2_entity_ids: list[str],
    winner_side: int,
    evidence_refs: list[str],
    audit_note: str,
    *,
    confidence: float,
    source_outcome_override: bool = False,
) -> dict[str, Any]:
    source_by_id = {str(item["id"]): item for item in WAVE8_SELJUKS_SOURCES}
    outcomes = sorted(evidence_refs)
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": side_1_entity_ids,
        "side_2_entity_ids": side_2_entity_ids,
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "interstate",
        "confidence": confidence,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        ),
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": source_outcome_override,
        "actor_override": True,
        "audit_note": audit_note,
    }


WAVE8_SELJUKS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Civetot1096-1": _contract(
        "hced-Civetot1096-1",
        _canonical("Battle of Civetot", 1096, "21 October 1096"),
        "kilij_arslan_peoples_crusade_1096",
        [_RUM_KILIJ_ID],
        [_PEOPLES_CRUSADE_ID],
        1,
        ["wave8_seljuks_alexiad_primary", "wave8_seljuks_civetot_article"],
        "Kilij Arslan I's Rum army destroyed the People's Crusade field force. The generic Seljuks label is not carried into another dynasty or reign.",
        confidence=0.94,
    ),
    "hced-Dorylaeum1147-1": _contract(
        "hced-Dorylaeum1147-1",
        _canonical("Second Battle of Dorylaeum", 1147, "26 October 1147"),
        "mesud_second_crusade_1147",
        [_RUM_MESUD_ID],
        [_GERMAN_CRUSADE_ID],
        1,
        ["wave8_seljuks_iranica_rum", "wave8_seljuks_tdv_mesud"],
        "Mesud I's Rum force inflicted a crushing defeat on Conrad III's German crusader army. No medieval Germany polity is invented.",
        confidence=0.95,
    ),
    "hced-Edessa1144-1": _contract(
        "hced-Edessa1144-1",
        _canonical(
            "Siege of Edessa (1144)",
            1144,
            "28 November-24 December 1144",
            date_precision="day_range",
        ),
        "zengid_edessa_1144",
        [_ZENGI_ID],
        [_EDESSA_ID],
        1,
        ["wave8_seljuks_cambridge_edessa_1144", "wave8_seljuks_oup_edessa_1144"],
        "Imad al-Din Zengi's Mosul-Aleppo regime captured Edessa; it was not the Great Seljuk Empire or the Sultanate of Rum.",
        confidence=0.97,
    ),
    "hced-Edessa1146-1": _contract(
        "hced-Edessa1146-1",
        _canonical(
            "Battle for Edessa (1146)",
            1146,
            "27 October-3 November 1146",
            date_precision="day_range",
        ),
        "nur_al_din_edessa_1146",
        [_NUR_AL_DIN_ID],
        [_EDESSA_ID],
        1,
        ["wave8_seljuks_cambridge_edessa_1146", "wave8_seljuks_penn_edessa_1146"],
        "Nur al-Din's new Aleppo regime defeated Joscelin II's restoration force. The result is separated from his father's 1144 conquest.",
        confidence=0.96,
    ),
    "hced-Kose Dagh1243-1": _contract(
        "hced-Kose Dagh1243-1",
        _canonical("Battle of Kose Dag", 1243, "26 June 1243"),
        "bayju_rum_campaign_1243",
        [_MONGOL_EMPIRE_ID],
        [_RUM_KAYKHUSRAW_ID],
        1,
        ["wave8_seljuks_iranica_bayju", "wave8_seljuks_iranica_rum"],
        "Bayju's Mongol army decisively defeated Kaykhusraw II's Rum army. The loser is a bounded Anatolian sultanate regime, not generic Seljuks.",
        confidence=0.98,
    ),
    "hced-Kufah1060-1": _contract(
        "hced-Kufah1060-1",
        _canonical("Battle of Saqi al-Furat near Kufa", 1060, "15 January 1060"),
        "tughril_basasiri_iraq_1060",
        [_BASASIRI_FORCE_ID],
        [_GREAT_SELJUK_ID],
        2,
        ["wave8_seljuks_ibn_al_jawzi_translation", "wave8_seljuks_tdv_besasiri"],
        "Seljuk cavalry overtook, defeated, and killed al-Basasiri near Kufa. HCED's al-Basasiri winner is directly reversed.",
        confidence=0.97,
        source_outcome_override=True,
    ),
}


WAVE8_SELJUKS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Baghdad1055-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Baghdad1055-1"],
        "canonical_event": _canonical(
            "Tughril Beg's entry into Baghdad",
            1055,
            "December 1055",
            date_precision="month",
            granularity="noncompetitive_political_transition",
        ),
        "hold_category": "terminal_exclusion_noncompetitive_transition_wrong_opponent",
        "terminal_exclusion": True,
        "hold_reason": (
            "Tughril entered Baghdad and displaced Buyid power; the Abbasid caliph "
            "was not a defeated battlefield opponent. No result against the "
            "Abbasid Caliphate is invented from a political transfer."
        ),
        "evidence_refs": [
            "wave8_seljuks_cambridge_baghdad",
            "wave8_seljuks_cambridge_formation_islam",
        ],
    },
    "hced-Elasa1167-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Elasa1167-1"],
        "canonical_event": _canonical("Battle of al-Babein", 1167, "18 March 1167"),
        "hold_category": "contradictory_or_inconclusive_tactical_outcome",
        "terminal_exclusion": False,
        "hold_reason": (
            "The row corresponds to Shirkuh's Zengid expedition against the "
            "Jerusalem-Fatimid coalition, not a Seljuk polity. Scholarly and "
            "primary-source traditions differ between a Syrian success and an "
            "inconclusive tactical action; unknown is not converted into a draw."
        ),
        "evidence_refs": [
            "wave8_seljuks_cambridge_egypt_1167",
            "wave8_seljuks_fordham_william_tyres_egypt",
        ],
    },
    "hced-Hasankale1048-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Hasankale1048-1"],
        "canonical_event": _canonical(
            "Battle of Kapetron",
            1048,
            "17-18 September 1048",
            date_precision="day_range",
        ),
        "hold_category": "contradictory_tactical_outcome_across_source_traditions",
        "terminal_exclusion": False,
        "hold_reason": (
            "The Byzantine flanks prevailed while Ibrahim Inal captured Liparit "
            "and withdrew with captives and booty. Source traditions classify the "
            "mixed action differently, so HCED's Seljuk win is not promoted and "
            "the uncertainty is not converted into a draw."
        ),
        "evidence_refs": [
            "wave8_seljuks_beihammer_anatolia",
            "wave8_seljuks_kapetron_sources",
        ],
    },
}


WAVE8_SELJUKS_CONTRACT_IDS = frozenset(WAVE8_SELJUKS_CONTRACTS)
WAVE8_SELJUKS_HOLD_IDS = frozenset(WAVE8_SELJUKS_HOLDS)
WAVE8_SELJUKS_RESERVED_IDS = WAVE8_SELJUKS_CONTRACT_IDS | WAVE8_SELJUKS_HOLD_IDS
WAVE8_SELJUKS_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)
WAVE8_SELJUKS_TERMINAL_EXCLUSION_IDS = frozenset(
    candidate_id
    for candidate_id, hold in WAVE8_SELJUKS_HOLDS.items()
    if hold.get("terminal_exclusion") is True
)


WAVE8_SELJUKS_POINT_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Edessa1144-1", "hced-Edessa1146-1"}
)
WAVE8_SELJUKS_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_SELJUKS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_SELJUKS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_SELJUKS_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_SELJUKS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Kufah1060-1": {
        "raw_winner_label": "Arslan al-Basasiri",
        "raw_loser_label": "Seljuks",
        "corrected_winner_side": 2,
        "corrected_winner_entity_ids": [_GREAT_SELJUK_ID],
        "outcome_source_ids": [
            "wave8_seljuks_ibn_al_jawzi_translation",
            "wave8_seljuks_tdv_besasiri",
        ],
        "outcome_source_family_ids": [
            "ibn_al_jawzi_muntazam_translation",
            "tdv_islam_encyclopedia_besasiri",
        ],
        "correction_note": (
            "The translated chronicle and TDV biography agree that Seljuk cavalry "
            "defeated al-Basasiri near Kufa and that he was killed."
        ),
    }
}


WAVE8_SELJUKS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, tuple[str, ...]] = {
    "1055": ("baghdad", "tughril entry into baghdad"),
    "1060": ("battle near kufa", "kufah", "saqi al furat"),
    "1096": ("battle of civetot", "civetot"),
    "1144": ("edessa", "siege of edessa"),
    "1146": ("battle for edessa", "edessa"),
    "1147": ("dorylaeum", "second battle of dorylaeum"),
    "1167": ("al babein", "babayn", "elasa"),
    "1243": ("battle of kose dag", "kose dag", "kose dagh"),
}
WAVE8_SELJUKS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_SELJUKS_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_SELJUKS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_SELJUKS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_SELJUKS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_SELJUKS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_SELJUKS_ENTITIES,
        "expected_candidate_ids": sorted(WAVE8_SELJUKS_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_SELJUKS_HOLDS,
        "integration_dispositions": WAVE8_SELJUKS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_SELJUKS_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_SELJUKS_IWBD_ZERO_OVERLAP_AUDIT,
        "outcome_overrides": WAVE8_SELJUKS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(WAVE8_SELJUKS_POINT_QUARANTINE_ADDITIONS),
        "sources": WAVE8_SELJUKS_SOURCES,
    }


def wave8_seljuks_audit_signature() -> str:
    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_SELJUKS_FINAL_AUDIT_SIGNATURE = (
    "5900c4545be1caed2d5bc9accfdc2021ce4ab8528c1d55d0a86eae20fb47dcc1"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    expected_contracts = {
        "hced-Civetot1096-1",
        "hced-Dorylaeum1147-1",
        "hced-Edessa1144-1",
        "hced-Edessa1146-1",
        "hced-Kose Dagh1243-1",
        "hced-Kufah1060-1",
    }
    expected_holds = {
        "hced-Baghdad1055-1",
        "hced-Elasa1167-1",
        "hced-Hasankale1048-1",
    }
    if set(WAVE8_SELJUKS_CONTRACTS) != expected_contracts:
        raise ValueError(f"{_LANE_NAME} promotion inventory changed")
    if set(WAVE8_SELJUKS_HOLDS) != expected_holds:
        raise ValueError(f"{_LANE_NAME} hold inventory changed")
    if WAVE8_SELJUKS_RESERVED_IDS != WAVE8_SELJUKS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_SELJUKS_CONTRACT_IDS & WAVE8_SELJUKS_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotions and holds overlap")
    if WAVE8_SELJUKS_TERMINAL_EXCLUSION_IDS != {"hced-Baghdad1055-1"}:
        raise ValueError(f"{_LANE_NAME} terminal exclusion inventory changed")
    if wave8_seljuks_audit_signature() != WAVE8_SELJUKS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_SELJUKS_SOURCES}
    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_SELJUKS_ENTITIES}
    if len(source_by_id) != 17 or len(entity_by_id) != 9:
        raise ValueError(f"{_LANE_NAME} source/entity inventory changed")
    if len(source_by_id) != len(WAVE8_SELJUKS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(entity_by_id) != len(WAVE8_SELJUKS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")

    for source in WAVE8_SELJUKS_SOURCES:
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    for entity in WAVE8_SELJUKS_ENTITIES:
        if entity["start_year"] is None or entity["end_year"] is None:
            raise ValueError(f"{_LANE_NAME} identity is not time bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        name = normalize_label(entity["name"])
        if name in {"seljuk", "seljuks", "seljuk turks", "germany", "muslims"}:
            raise ValueError(f"{_LANE_NAME} installed a generic identity")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity provenance is not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity cites an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    allowed_entities = {*entity_by_id, _GREAT_SELJUK_ID, _MONGOL_EMPIRE_ID}
    override_ids: set[str] = set()
    for candidate_id, contract in WAVE8_SELJUKS_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} canonical event key drifted")
        if canonical["granularity"] != "engagement" or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} promoted a non-engagement")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= allowed_entities:
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        year = int(canonical["year_low"])
        for entity_id in (set(side_1) | set(side_2)) & set(entity_by_id):
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
            used_entities.add(entity_id)
        if contract["result_type"] != "win" or contract["winner_side"] not in {1, 2}:
            raise ValueError(f"{_LANE_NAME} invented a draw or unknown result")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")
        if contract["outcome_reversal"] is not contract["source_outcome_override"]:
            raise ValueError(f"{_LANE_NAME} outcome override metadata drifted")
        if contract["source_outcome_override"]:
            override_ids.add(candidate_id)
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or evidence != outcomes:
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if not evidence or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} source provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome result source")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")
    for hold in WAVE8_SELJUKS_HOLDS.values():
        if {"winner_side", "result_type", "side_1_entity_ids", "side_2_entity_ids"} & set(hold):
            raise ValueError(f"{_LANE_NAME} hold contains a rateable result")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold provenance drifted")
        used_sources.update(evidence)
    used_sources.update(
        source_id
        for entity in WAVE8_SELJUKS_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")
    if override_ids != set(WAVE8_SELJUKS_OUTCOME_OVERRIDES):
        raise ValueError(f"{_LANE_NAME} outcome override inventory drifted")
    metadata = WAVE8_SELJUKS_OUTCOME_OVERRIDES["hced-Kufah1060-1"]
    contract = WAVE8_SELJUKS_CONTRACTS["hced-Kufah1060-1"]
    if (
        metadata["corrected_winner_side"] != contract["winner_side"]
        or metadata["corrected_winner_entity_ids"]
        != contract[f"side_{contract['winner_side']}_entity_ids"]
        or metadata["outcome_source_ids"] != contract["outcome_source_ids"]
        or metadata["outcome_source_family_ids"]
        != contract["outcome_source_family_ids"]
    ):
        raise ValueError(f"{_LANE_NAME} outcome override metadata drifted")

    if WAVE8_SELJUKS_POINT_QUARANTINE_ADDITIONS != {
        "hced-Edessa1144-1",
        "hced-Edessa1146-1",
    }:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_SELJUKS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if (
        WAVE8_SELJUKS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_SELJUKS_CROSS_LANE_DISPOSITIONS
        or WAVE8_SELJUKS_INTEGRATION_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate disposition audit changed")


def validate_wave8_seljuks_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SELJUKS_CONTRACTS,
        WAVE8_SELJUKS_HOLDS,
        lane_name=_LANE_NAME,
    )


def _iwbd_year(row: Mapping[str, Any]) -> int | None:
    for field in ("start_date", "end_date"):
        value = row.get(field)
        if isinstance(value, str) and len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    try:
        return int(row["year"]) if row.get("year") is not None else None
    except (TypeError, ValueError):
        return None


def validate_wave8_seljuks_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
) -> dict[str, int]:
    validate_wave8_seljuks_queue_contracts(hced_rows)
    audited = {
        (int(year), normalize_label(name))
        for year, names in WAVE8_SELJUKS_IWBD_ZERO_OVERLAP_AUDIT.items()
        for name in names
    }
    collisions = []
    for row in iwbd_rows:
        year = _iwbd_year(row)
        if year is not None and (year, normalize_label(row.get("name"))) in audited:
            collisions.append(str(row.get("candidate_id") or "<missing-id>"))
    if collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): {sorted(collisions)}"
        )
    return {
        "cross_lane_hced_dispositions": 0,
        "integration_dispositions": 0,
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_seljuks_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SELJUKS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_seljuks_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SELJUKS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SELJUKS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SELJUKS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_seljuks_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_seljuks_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SELJUKS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_seljuks_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_SELJUKS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_seljuks_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_SELJUKS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(WAVE8_SELJUKS_CROSS_LANE_DISPOSITIONS),
        "holds": len(WAVE8_SELJUKS_HOLDS),
        "integration_dispositions": len(WAVE8_SELJUKS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_SELJUKS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_SELJUKS_ENTITIES),
        "new_sources": len(WAVE8_SELJUKS_SOURCES),
        "newly_rated_events": len(WAVE8_SELJUKS_CONTRACTS),
        "outcome_overrides": len(WAVE8_SELJUKS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_SELJUKS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_SELJUKS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_SELJUKS_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_SELJUKS_TERMINAL_EXCLUSION_IDS),
    }


def wave8_seljuks_location_quarantine_additions() -> dict[str, frozenset[str]]:
    _validate_static()
    return {
        "country": WAVE8_SELJUKS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_SELJUKS_POINT_QUARANTINE_ADDITIONS,
    }
