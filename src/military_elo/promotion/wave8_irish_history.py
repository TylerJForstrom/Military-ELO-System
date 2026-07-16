"""Exact Wave 8 audit for HCED rows carrying the generic label ``Ireland``.

The nine rows span unrelated medieval dynasties, urban lordships, Gaelic
coalitions, Crown expeditions, and seventeenth-century siege forces.  Every
promotion is therefore bound to the exact event force.  No timeless Ireland,
Irish, England, English, Viking, or Danish-Dublin identity is opened here.
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
    "WAVE8_IRISH_HISTORY_CONTRACTS",
    "WAVE8_IRISH_HISTORY_CONTRACT_IDS",
    "WAVE8_IRISH_HISTORY_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_IRISH_HISTORY_CROSS_SOURCE_DUPLICATE_DISPOSITIONS",
    "WAVE8_IRISH_HISTORY_ENTITIES",
    "WAVE8_IRISH_HISTORY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_IRISH_HISTORY_EXPECTED_CANDIDATE_IDS",
    "WAVE8_IRISH_HISTORY_FINAL_AUDIT_SIGNATURE",
    "WAVE8_IRISH_HISTORY_HOLDS",
    "WAVE8_IRISH_HISTORY_HOLD_IDS",
    "WAVE8_IRISH_HISTORY_INTEGRATION_DISPOSITIONS",
    "WAVE8_IRISH_HISTORY_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_IRISH_HISTORY_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_IRISH_HISTORY_LOCATION_QUARANTINE_REASONS",
    "WAVE8_IRISH_HISTORY_OUTCOME_OVERRIDES",
    "WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS",
    "WAVE8_IRISH_HISTORY_RESERVED_IDS",
    "WAVE8_IRISH_HISTORY_SOURCES",
    "WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS",
    "WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSION_IDS",
    "install_wave8_irish_history_entities",
    "install_wave8_irish_history_sources",
    "promote_wave8_irish_history_contracts",
    "validate_wave8_irish_history_integration_dispositions",
    "validate_wave8_irish_history_queue_contracts",
    "wave8_irish_history_audit_signature",
    "wave8_irish_history_cohort_counts",
    "wave8_irish_history_counts",
    "wave8_irish_history_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Irish-history forces"
_EVENT_ID_PREFIX = "hced_wave8_irish_history_"


_ROW_HASHES = {
    "hced-Blackwater1598-1": (
        "3856e57675bfc33a27de36c46393678898bd9853a8ab921f72a3acec748f0af2"
    ),
    "hced-Clontarf1014-1": (
        "10ce143fcee5ac4c83e0d828ddf333bfcd86d9c70fce8678e34773c8597379a0"
    ),
    "hced-Clontibret1595-1": (
        "5cba2e389591b53ab9a493ccafd185142358d2890919f07b4ff7d9ed7606abb4"
    ),
    "hced-Derry1600-1": (
        "31ae2b15b65e5d5bf9822002ccc1dc9ba9dafe81eac6a06512b30b27f37eeede"
    ),
    "hced-Dublin (2nd)1171-1": (
        "2c0bd03b6e0aaafc3fa1ee98166354025a7861aa657a129eb4fdcfa13f96d037"
    ),
    "hced-Dysert ODea1318-1": (
        "5e177ac95c49448dd5dae7dbbf07b429a1220eda44a144b2ad58bbcc33d3b7f0"
    ),
    "hced-Ford of the Biscuits1594-1": (
        "8ea79e23511d59ec80025085ad4ae780b037c5e0be1a27f73107f1df5cb43f81"
    ),
    "hced-Limerick1651-1": (
        "40415b651d07975979e9cec99571d87aba267083f9c1038c4fcba002dcd759f0"
    ),
    "hced-Tara980-1": (
        "0d318ac6a0e982e456e205ba70e59417a43ccc98309c6fb3d54d0341e2d6b905"
    ),
}


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


WAVE8_IRISH_HISTORY_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_irish_ucc_annals_ulster_980",
        "The Annals of Ulster, U980",
        "https://celt.ucc.ie/published/T100001A/text550.html",
        "University College Cork, Corpus of Electronic Texts",
        "edited_primary_source",
        "ucc_celt_annals_ulster",
    ),
    _source(
        "wave8_irish_aia_tara_landscape",
        "The Impact of the Proposed M3 Motorway on Tara and its Cultural Landscape",
        "https://www.archaeological.org/pdfs/archaeologywatch/Tara/Tara_statement.pdf",
        "Archaeological Institute of America",
        "academic_heritage_statement",
        "aia_tara_cultural_landscape",
        outcome=False,
    ),
    _source(
        "wave8_irish_tcd_clontarf_combat",
        "‘Emperor of the Irish’: Brian Boru and the Battle of Clontarf 1014 — The Combat",
        "https://www.tcd.ie/library/exhibitions/boru/combat.php",
        "Trinity College Dublin Library",
        "university_library_exhibition",
        "tcd_clontarf_1014",
    ),
    _source(
        "wave8_irish_ucc_annals_ulster_1014",
        "The Annals of Ulster, U1014",
        "https://celt.ucc.ie/published/T100001A/text585.html",
        "University College Cork, Corpus of Electronic Texts",
        "edited_primary_source",
        "ucc_celt_annals_ulster",
    ),
    _source(
        "wave8_irish_ucc_annals_tigernach_1171",
        "The Annals of Tigernach, T1171.7–T1171.10",
        "https://celt.ucc.ie/published/T100002A/text024.html",
        "University College Cork, Corpus of Electronic Texts",
        "edited_primary_source",
        "ucc_celt_annals_tigernach",
    ),
    _source(
        "wave8_irish_oxford_martin_1169_1172",
        "Allies and an Overlord, 1169–72",
        "https://academic.oup.com/book/26629/chapter-abstract/195321249",
        "Oxford University Press",
        "academic_book_chapter",
        "oxford_new_history_ireland_volume_2",
        outcome=False,
    ),
    _source(
        "wave8_irish_dublin_city_walls",
        "Dublin City Walls and Defences",
        "https://www.dublincity.ie/sites/default/files/media/file-uploads/2018-06/City_Walls_booklet_17_6_10.pdf",
        "Dublin City Council",
        "municipal_heritage_publication",
        "dublin_city_walls_heritage",
    ),
    _source(
        "wave8_irish_simms_dysert_odea",
        "The Battle of Dysert O’Dea and the Gaelic Resurgence in Thomond",
        "https://clarelibraries.ie/localstudies/history/battles-and-fortifications-in-clare/the-battle-of-dysert-odea-and-the-gaelic-resurgence-in-thomond/",
        "Clare County Library; originally Dál gCais 5 (1979)",
        "reproduced_academic_article",
        "simms_dysert_odea_1979",
    ),
    _source(
        "wave8_irish_ucc_beatha_aodha_ruaidh",
        "Beatha Aodha Ruaidh Uí Dhomhnaill",
        "https://celt.ucc.ie/document/T100080/",
        "University College Cork, Corpus of Electronic Texts",
        "edited_primary_source",
        "ucc_celt_beatha_aodha_ruaidh",
    ),
    _source(
        "wave8_irish_ucc_four_masters_1594_1598",
        "Annala Rioghachta Eireann: Annals of the Kingdom of Ireland, volume 6",
        "https://celt.ucc.ie/document/T100005F/",
        "University College Cork, Corpus of Electronic Texts",
        "edited_primary_source",
        "ucc_celt_four_masters",
    ),
    _source(
        "wave8_irish_ria_oneill_nine_years_war",
        "Spouses, spies and subterfuge: the role and experience of women during the Nine Years War (1593–1603)",
        "https://hdl.handle.net/10468/11583",
        "Proceedings of the Royal Irish Academy; UCC CORA repository",
        "peer_reviewed_academic_article",
        "ria_proceedings_oneill_2021",
    ),
    _source(
        "wave8_irish_cambridge_strategy_tactics",
        "Strategy and Tactics in Irish Warfare, 1593–1601",
        "https://www.cambridge.org/core/journals/irish-historical-studies/article/abs/strategy-and-tactics-in-irish-warfare-15931601/6E8AF18F2C9485861A4494C3A6097531",
        "Irish Historical Studies / Cambridge University Press",
        "academic_journal_article",
        "irish_historical_studies_warfare_1593_1601",
    ),
    _source(
        "wave8_irish_ucc_hanmer_yellow_ford",
        "Portions of a manuscript history relating to Ireland",
        "https://celt.ucc.ie/document/E590002/",
        "University College Cork, CELT edition of The National Archives State Papers",
        "edited_archival_primary_source",
        "tna_state_papers_hanmer_yellow_ford",
    ),
    _source(
        "wave8_irish_rct_limerick_1651",
        "Map of the siege of Limerick, 1651",
        "https://militarymaps.rct.uk/other-17th-century-conflicts/map-of-the-siege-of-limerick-1651-limerick-munster-ireland-52deg3953n-08deg3723w",
        "Royal Collection Trust",
        "royal_collection_catalogue",
        "royal_collection_military_maps_limerick",
    ),
    _source(
        "wave8_irish_ucc_ireton_limerick_1651",
        "A Letter from the Lord Deputy-General of Ireland upon the Surrender of Limerick, 1651",
        "https://celt.ucc.ie/document/E650001-024/",
        "University College Cork, Corpus of Electronic Texts",
        "digitized_primary_source",
        "ucc_celt_ireton_limerick_1651",
    ),
    _source(
        "wave8_irish_askaboutireland_docwra",
        "Sir Henry Dowcra",
        "https://www.askaboutireland.ie/reading-room/history-heritage/history-of-ireland/the-ulster-plantation/sir-henry-dowcra/",
        "AskAboutIreland / Irish public libraries",
        "national_heritage_reference",
        "askaboutireland_ulster_plantation",
        outcome=False,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    scope_note: str,
    source_ids: list[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": "Ireland and the Irish Sea",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            scope_note
            + " No rating is inherited by any broader Irish, English, Viking, "
            "Danish-Dublin, dynastic, confederate, lordship, rebel, or successor "
            "identity."
        ),
        "source_ids": sorted(set(source_ids)),
    }


WAVE8_IRISH_HISTORY_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "mael_sechnaill_clann_cholmain_tara_host_980",
        "Máel Sechnaill’s Clann Cholmáin Host at Tara (980)",
        "engagement_force",
        980,
        "The identity is limited to Máel Sechnaill mac Domnaill’s Tara field force.",
        [
            "wave8_irish_aia_tara_landscape",
            "wave8_irish_ucc_annals_ulster_980",
        ],
    ),
    _entity(
        "amlaib_cuaran_dublin_isles_tara_host_980",
        "Amlaíb Cúarán’s Dublin-and-Isles Host at Tara (980)",
        "engagement_force",
        980,
        "The identity is limited to the Dublin-and-Isles force opposed at Tara.",
        [
            "wave8_irish_aia_tara_landscape",
            "wave8_irish_ucc_annals_ulster_980",
        ],
    ),
    _entity(
        "brian_boruma_clontarf_field_coalition_1014",
        "Brian Bóruma’s Clontarf Field Coalition (1014)",
        "engagement_coalition",
        1014,
        "The identity is limited to Brian Bóruma’s field coalition at Clontarf.",
        [
            "wave8_irish_tcd_clontarf_combat",
            "wave8_irish_ucc_annals_ulster_1014",
        ],
    ),
    _entity(
        "leinster_dublin_overseas_clontarf_coalition_1014",
        "Leinster–Dublin–Overseas Coalition at Clontarf (1014)",
        "engagement_coalition",
        1014,
        "The identity is limited to the Leinster, Dublin, and overseas contingents at Clontarf.",
        [
            "wave8_irish_tcd_clontarf_combat",
            "wave8_irish_ucc_annals_ulster_1014",
        ],
    ),
    _entity(
        "strongbow_cogan_dublin_garrison_1171",
        "Strongbow and Miles de Cogan’s Dublin Garrison (1171)",
        "siege_garrison",
        1171,
        "The identity is limited to the Dublin garrison that sortied against Ruaidrí’s siege coalition.",
        [
            "wave8_irish_dublin_city_walls",
            "wave8_irish_oxford_martin_1169_1172",
            "wave8_irish_ucc_annals_tigernach_1171",
        ],
    ),
    _entity(
        "ruaidri_ua_conchobair_dublin_siege_coalition_1171",
        "Ruaidrí Ua Conchobair’s Dublin Siege Coalition (1171)",
        "siege_coalition",
        1171,
        "The identity is limited to Ruaidrí Ua Conchobair and the named allied forces besieging Dublin.",
        [
            "wave8_irish_dublin_city_walls",
            "wave8_irish_oxford_martin_1169_1172",
            "wave8_irish_ucc_annals_tigernach_1171",
        ],
    ),
    _entity(
        "muircheartach_obrien_thomond_dysert_coalition_1318",
        "Muircheartach O’Brien’s Thomond Coalition at Dysert O’Dea (1318)",
        "engagement_coalition",
        1318,
        "The identity is limited to the O’Brien, O’Dea, O’Connor, and O’Hehir coalition at Dysert O’Dea.",
        ["wave8_irish_simms_dysert_odea"],
    ),
    _entity(
        "richard_de_clare_dysert_army_1318",
        "Richard de Clare’s Army at Dysert O’Dea (1318)",
        "engagement_force",
        1318,
        "The identity is limited to Richard de Clare’s divided field army at Dysert O’Dea.",
        ["wave8_irish_simms_dysert_odea"],
    ),
    _entity(
        "maguire_allied_ford_biscuits_force_1594",
        "Maguire’s Allied Force at Ford of the Biscuits (1594)",
        "engagement_coalition",
        1594,
        "The identity is limited to Hugh Maguire’s force with Cormac MacBaron, Cenél Eóghain, and O’Donnell contingents at the ford.",
        [
            "wave8_irish_ria_oneill_nine_years_war",
            "wave8_irish_ucc_beatha_aodha_ruaidh",
            "wave8_irish_ucc_four_masters_1594_1598",
        ],
    ),
    _entity(
        "crown_enniskillen_relief_column_1594",
        "Crown Enniskillen Relief Column at Ford of the Biscuits (1594)",
        "relief_column",
        1594,
        "The identity is limited to the Crown column carrying supplies toward the Enniskillen garrison.",
        [
            "wave8_irish_ria_oneill_nine_years_war",
            "wave8_irish_ucc_beatha_aodha_ruaidh",
            "wave8_irish_ucc_four_masters_1594_1598",
        ],
    ),
    _entity(
        "hugh_oneill_clontibret_force_1595",
        "Hugh O’Neill’s Clontibret Force (1595)",
        "engagement_force",
        1595,
        "The identity is limited to Hugh O’Neill’s force in the Clontibret action.",
        [
            "wave8_irish_cambridge_strategy_tactics",
            "wave8_irish_ucc_four_masters_1594_1598",
        ],
    ),
    _entity(
        "bagenal_monaghan_relief_column_1595",
        "Henry Bagenal’s Monaghan Relief Column (1595)",
        "relief_column",
        1595,
        "The identity is limited to Bagenal’s Crown column returning from provisioning Monaghan.",
        [
            "wave8_irish_cambridge_strategy_tactics",
            "wave8_irish_ucc_four_masters_1594_1598",
        ],
    ),
    _entity(
        "oneill_odonnell_yellow_ford_host_1598",
        "O’Neill–O’Donnell Yellow Ford Host (1598)",
        "engagement_coalition",
        1598,
        "The identity is limited to the O’Neill, O’Donnell, and allied Ulster host at the Yellow Ford.",
        [
            "wave8_irish_ucc_beatha_aodha_ruaidh",
            "wave8_irish_ucc_four_masters_1594_1598",
            "wave8_irish_ucc_hanmer_yellow_ford",
        ],
    ),
    _entity(
        "bagenal_blackwater_relief_army_1598",
        "Henry Bagenal’s Blackwater Relief Army (1598)",
        "relief_army",
        1598,
        "The identity is limited to the Crown army sent to relieve the Blackwater fort in August 1598.",
        [
            "wave8_irish_ucc_beatha_aodha_ruaidh",
            "wave8_irish_ucc_four_masters_1594_1598",
            "wave8_irish_ucc_hanmer_yellow_ford",
        ],
    ),
    _entity(
        "docwra_lough_foyle_expedition_1600",
        "Henry Docwra’s Lough Foyle Expeditionary Force (1600)",
        "expeditionary_force",
        1600,
        "The identity is limited to Docwra’s Lough Foyle expedition and unopposed occupation of Derry.",
        ["wave8_irish_askaboutireland_docwra"],
    ),
    _entity(
        "ireton_new_model_army_limerick_1651",
        "Henry Ireton’s New Model Army at Limerick (1651)",
        "siege_army",
        1651,
        "The identity is limited to the English Parliamentarian besieging army at Limerick.",
        [
            "wave8_irish_rct_limerick_1651",
            "wave8_irish_ucc_ireton_limerick_1651",
        ],
    ),
    _entity(
        "hugh_dubh_oneill_limerick_garrison_1651",
        "Hugh Dubh O’Neill’s Confederate–Royalist Limerick Garrison (1651)",
        "siege_garrison",
        1651,
        "The identity is limited to the Irish Confederate Catholic and English Royalist garrison defending Limerick.",
        [
            "wave8_irish_rct_limerick_1651",
            "wave8_irish_ucc_ireton_limerick_1651",
        ],
    ),
)


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_IRISH_HISTORY_SOURCES
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str = "day",
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "name": name,
        "year_low": year,
        "year_high": year,
        "date_text": date_text,
        "date_precision": date_precision,
        "granularity": granularity,
        "canonical_key": f"{_slug(name)}:{year}:{year}",
    }


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: list[str],
    side_2_entity_ids: list[str],
    evidence_refs: list[str],
    outcome_source_ids: list[str],
    audit_note: str,
    war_type: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(outcome_source_ids))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": side_1_entity_ids,
        "side_2_entity_ids": side_2_entity_ids,
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": sorted(set(evidence_refs)),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "audit_note": audit_note,
    }


WAVE8_IRISH_HISTORY_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Tara980-1": _contract(
        "hced-Tara980-1",
        _canonical(
            "Battle of Tara",
            980,
            "980 (Annals of Ulster: AD 979 alias 980)",
            date_precision="year",
        ),
        "battle_of_tara_980",
        ["mael_sechnaill_clann_cholmain_tara_host_980"],
        ["amlaib_cuaran_dublin_isles_tara_host_980"],
        [
            "wave8_irish_aia_tara_landscape",
            "wave8_irish_ucc_annals_ulster_980",
        ],
        ["wave8_irish_ucc_annals_ulster_980"],
        (
            "The Annals of Ulster directly record Máel Sechnaill’s victory over "
            "the force of Dublin and the Isles. Archaeological scholarship binds "
            "the opposing ruler as Amlaíb Cúarán and the winner to Clann Cholmáin; "
            "the raw Danish-Dublin and Ireland labels are not retained as identities."
        ),
        "interstate",
        confidence=0.90,
    ),
    "hced-Clontarf1014-1": _contract(
        "hced-Clontarf1014-1",
        _canonical("Battle of Clontarf", 1014, "23 April 1014"),
        "battle_of_clontarf_1014",
        ["brian_boruma_clontarf_field_coalition_1014"],
        ["leinster_dublin_overseas_clontarf_coalition_1014"],
        [
            "wave8_irish_tcd_clontarf_combat",
            "wave8_irish_ucc_annals_ulster_1014",
        ],
        [
            "wave8_irish_tcd_clontarf_combat",
            "wave8_irish_ucc_annals_ulster_1014",
        ],
        (
            "Trinity and the Annals of Ulster identify Brian Bóruma’s coalition "
            "against the combined Leinster, Dublin, and overseas contingents and "
            "record the latter’s rout. This is not an Ireland-versus-Vikings rating."
        ),
        "interstate",
        confidence=0.94,
    ),
    "hced-Dublin (2nd)1171-1": _contract(
        "hced-Dublin (2nd)1171-1",
        _canonical(
            "Siege of Dublin",
            1171,
            "1171; Ruaidrí Ua Conchobair’s siege after Ascall’s distinct counterattack",
            date_precision="year",
            granularity="siege",
        ),
        "anglo_norman_dublin_1171",
        ["strongbow_cogan_dublin_garrison_1171"],
        ["ruaidri_ua_conchobair_dublin_siege_coalition_1171"],
        [
            "wave8_irish_dublin_city_walls",
            "wave8_irish_oxford_martin_1169_1172",
            "wave8_irish_ucc_annals_tigernach_1171",
        ],
        [
            "wave8_irish_dublin_city_walls",
            "wave8_irish_ucc_annals_tigernach_1171",
        ],
        (
            "The Annals of Tigernach bind Ruaidrí, Tigernán Ua Ruairc, and "
            "Muircheartach Ua Cearbhaill against the Earl and Miles de Cogan, "
            "whose sortie entered and despoiled the siege camp. Oxford and Dublin "
            "City sources distinguish this siege from Ascall mac Ragnaill’s earlier "
            "sea-borne counterattack, the adjacent HCED Dublin (1st) row."
        ),
        "state_formation_conflict",
        confidence=0.91,
    ),
    "hced-Dysert ODea1318-1": _contract(
        "hced-Dysert ODea1318-1",
        _canonical("Battle of Dysert O’Dea", 1318, "10 May 1318"),
        "thomond_de_clare_conflict_1318",
        ["muircheartach_obrien_thomond_dysert_coalition_1318"],
        ["richard_de_clare_dysert_army_1318"],
        ["wave8_irish_simms_dysert_odea"],
        ["wave8_irish_simms_dysert_odea"],
        (
            "Katharine Simms identifies Muircheartach O’Brien with the O’Dea, "
            "O’Connor, and O’Hehir vassal forces against Richard de Clare’s army, "
            "which was defeated. Neither side is a generic Ireland or England army."
        ),
        "interstate_limited",
        confidence=0.93,
    ),
    "hced-Ford of the Biscuits1594-1": _contract(
        "hced-Ford of the Biscuits1594-1",
        _canonical("Battle of the Ford of the Biscuits", 1594, "7 August 1594"),
        "nine_years_war_1594_1603",
        ["maguire_allied_ford_biscuits_force_1594"],
        ["crown_enniskillen_relief_column_1594"],
        [
            "wave8_irish_ria_oneill_nine_years_war",
            "wave8_irish_ucc_beatha_aodha_ruaidh",
            "wave8_irish_ucc_four_masters_1594_1598",
        ],
        [
            "wave8_irish_ria_oneill_nine_years_war",
            "wave8_irish_ucc_beatha_aodha_ruaidh",
            "wave8_irish_ucc_four_masters_1594_1598",
        ],
        (
            "The primary narratives identify Hugh Maguire with Cormac MacBaron, "
            "Cenél Eóghain, and O’Donnell contingents defeating the exact Crown "
            "column carrying supplies toward Enniskillen. The contract does not "
            "choose between differing commander descriptions where that is unnecessary."
        ),
        "anti_imperial_revolt",
        confidence=0.91,
    ),
    "hced-Clontibret1595-1": _contract(
        "hced-Clontibret1595-1",
        _canonical("Battle of Clontibret", 1595, "27 May 1595"),
        "nine_years_war_1594_1603",
        ["hugh_oneill_clontibret_force_1595"],
        ["bagenal_monaghan_relief_column_1595"],
        [
            "wave8_irish_cambridge_strategy_tactics",
            "wave8_irish_ucc_four_masters_1594_1598",
        ],
        [
            "wave8_irish_cambridge_strategy_tactics",
            "wave8_irish_ucc_four_masters_1594_1598",
        ],
        (
            "Academic and annalistic accounts bind Hugh O’Neill’s force against "
            "Henry Bagenal’s Crown column on its return from provisioning Monaghan "
            "and support the column’s defeat. The raw national labels are discarded."
        ),
        "anti_imperial_revolt",
        confidence=0.92,
    ),
    "hced-Blackwater1598-1": _contract(
        "hced-Blackwater1598-1",
        _canonical("Battle of the Yellow Ford", 1598, "14 August 1598"),
        "nine_years_war_1594_1603",
        ["oneill_odonnell_yellow_ford_host_1598"],
        ["bagenal_blackwater_relief_army_1598"],
        [
            "wave8_irish_ucc_beatha_aodha_ruaidh",
            "wave8_irish_ucc_four_masters_1594_1598",
            "wave8_irish_ucc_hanmer_yellow_ford",
        ],
        [
            "wave8_irish_ucc_beatha_aodha_ruaidh",
            "wave8_irish_ucc_four_masters_1594_1598",
            "wave8_irish_ucc_hanmer_yellow_ford",
        ],
        (
            "The raw Blackwater label is canonicalized to the Battle of the Yellow "
            "Ford. State-paper and Gaelic accounts identify the O’Neill–O’Donnell "
            "host defeating Henry Bagenal’s army sent to relieve Blackwater fort."
        ),
        "anti_imperial_revolt",
        confidence=0.96,
    ),
    "hced-Limerick1651-1": _contract(
        "hced-Limerick1651-1",
        _canonical(
            "Siege of Limerick",
            1651,
            "3 June–29 October 1651",
            date_precision="day_range",
            granularity="siege",
        ),
        "wars_of_three_kingdoms_1651",
        ["ireton_new_model_army_limerick_1651"],
        ["hugh_dubh_oneill_limerick_garrison_1651"],
        [
            "wave8_irish_rct_limerick_1651",
            "wave8_irish_ucc_ireton_limerick_1651",
        ],
        [
            "wave8_irish_rct_limerick_1651",
            "wave8_irish_ucc_ireton_limerick_1651",
        ],
        (
            "Royal Collection and contemporary surrender evidence identify Ireton’s "
            "English Parliamentarian New Model Army against Hugh Dubh O’Neill’s "
            "Irish Confederate Catholic and English Royalist garrison, ending in "
            "the city’s surrender. No generic England or Ireland actor is created."
        ),
        "civil_war",
        confidence=0.96,
    ),
}


WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Derry1600-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Derry1600-1"],
        "canonical_event": _canonical(
            "Unopposed occupation of Derry",
            1600,
            "1600",
            date_precision="year",
            granularity="unopposed_occupation",
        ),
        "disposition": "terminal_exclusion",
        "hold_category": "not_an_engagement_unopposed_occupation",
        "result_type": "unknown",
        "reviewed_outcome": "unknown",
        "unknown_is_never_draw": True,
        "side_1_entity_ids": ["docwra_lough_foyle_expedition_1600"],
        "side_2_entity_ids": [],
        "opposing_force_status": "none_evidenced",
        "actor_override": True,
        "evidence_refs": ["wave8_irish_askaboutireland_docwra"],
        "hold_reason": (
            "The national heritage account states that Henry Docwra occupied "
            "Derry without opposition. No opposing Tyrone, Gaelic, Irish, or other "
            "formation is evidenced for this occupation, so there is no competitive "
            "tactical result to rate. Unknown is excluded and never encoded as a draw."
        ),
    }
}

# The shared exact-wave inventory API names every nonpromotion a hold.  This
# row is a terminal exclusion, not a provisional research hold.
WAVE8_IRISH_HISTORY_HOLDS = WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS

WAVE8_IRISH_HISTORY_CONTRACT_IDS = frozenset(WAVE8_IRISH_HISTORY_CONTRACTS)
WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS
)
WAVE8_IRISH_HISTORY_HOLD_IDS = WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSION_IDS
WAVE8_IRISH_HISTORY_RESERVED_IDS = (
    WAVE8_IRISH_HISTORY_CONTRACT_IDS
    | WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSION_IDS
)
WAVE8_IRISH_HISTORY_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


# None of the locked IWBD rows or pre-lane release events is an exact or
# containing twin of this cohort.  The empty dispositions are intentional and
# signed, so a future match must be researched rather than silently duplicated.
WAVE8_IRISH_HISTORY_CROSS_SOURCE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_IRISH_HISTORY_IWBD_DUPLICATE_DISPOSITIONS = (
    WAVE8_IRISH_HISTORY_CROSS_SOURCE_DUPLICATE_DISPOSITIONS
)
WAVE8_IRISH_HISTORY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}


# This adjacent HCED row is not owned or reserved here.  Its fingerprint is
# pinned solely to prevent the two different 1171 Dublin actions being merged.
WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Dublin (1st)1171-1": {
        "source_dataset": "hced",
        "hced_candidate_id": "hced-Dublin (2nd)1171-1",
        "disposition": "distinct_same_year_engagement",
        "relationship": "earlier_Ascall_counterattack_not_Ruaidri_siege",
        "raw_row_sha256": (
            "8e0dfd1b4fca7a7bc416fd2fcddb7c8e200cbea30e822dbc51374268e5549e2f"
        ),
        "evidence_refs": sorted(
            [
                "wave8_irish_dublin_city_walls",
                "wave8_irish_oxford_martin_1169_1172",
                "wave8_irish_ucc_annals_tigernach_1171",
            ]
        ),
        "reason": (
            "Dublin (1st) is Ascall mac Ragnaill’s failed sea-borne counterattack; "
            "Dublin (2nd) is Ruaidrí Ua Conchobair’s later siege and the garrison "
            "sortie against its camp. Same city and year do not make them duplicates."
        ),
    }
}

WAVE8_IRISH_HISTORY_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS,
    **WAVE8_IRISH_HISTORY_CROSS_SOURCE_DUPLICATE_DISPOSITIONS,
}


WAVE8_IRISH_HISTORY_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    "hced-Blackwater1598-1": {
        "action": "withhold_point",
        "evidence_refs": ["wave8_irish_ucc_hanmer_yellow_ford"],
        "reason": (
            "The staged Blackwater coordinate identifies neither the Yellow Ford "
            "battle line nor a source-audited point on Bagenal’s approach."
        ),
    },
    "hced-Clontarf1014-1": {
        "action": "withhold_point",
        "evidence_refs": ["wave8_irish_tcd_clontarf_combat"],
        "reason": (
            "Trinity notes that the earliest accounts do not specify the precise "
            "battlefield; a modern Clontarf point is therefore too precise."
        ),
    },
    "hced-Clontibret1595-1": {
        "action": "withhold_point",
        "evidence_refs": ["wave8_irish_cambridge_strategy_tactics"],
        "reason": (
            "The action followed Bagenal’s returning column; the staged village "
            "coordinate is not a source-audited battlefield point."
        ),
    },
    "hced-Dublin (2nd)1171-1": {
        "action": "withhold_point",
        "evidence_refs": [
            "wave8_irish_dublin_city_walls",
            "wave8_irish_ucc_annals_tigernach_1171",
        ],
        "reason": (
            "The siege, camps, and garrison sortie form a multi-site urban action; "
            "Dublin’s city-centre coordinate is not an exact battlefield point."
        ),
    },
    "hced-Dysert ODea1318-1": {
        "action": "withhold_point",
        "evidence_refs": ["wave8_irish_simms_dysert_odea"],
        "reason": (
            "The battle unfolded across divided approaches and a fighting-ford; "
            "the place-name coordinate is not independently verified as the field."
        ),
    },
    "hced-Ford of the Biscuits1594-1": {
        "action": "withhold_point",
        "evidence_refs": ["wave8_irish_ucc_beatha_aodha_ruaidh"],
        "reason": (
            "The primary account identifies a rough, difficult ford but does not "
            "validate the staged modern coordinate as that exact crossing."
        ),
    },
    "hced-Limerick1651-1": {
        "action": "withhold_point",
        "evidence_refs": ["wave8_irish_rct_limerick_1651"],
        "reason": (
            "A four-month siege of the fortified city has an urban footprint, not "
            "a single source-supported city-centre battle point."
        ),
    },
    "hced-Tara980-1": {
        "action": "withhold_point",
        "evidence_refs": ["wave8_irish_aia_tara_landscape"],
        "reason": (
            "The academic heritage statement treats Tara and Skreen as a broad "
            "royal landscape; it does not establish the staged hill point as the field."
        ),
    },
}

WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_IRISH_HISTORY_LOCATION_QUARANTINE_REASONS
)
WAVE8_IRISH_HISTORY_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_IRISH_HISTORY_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_IRISH_HISTORY_COUNTRY_QUARANTINE_ADDITIONS,
}


# Every promoted result agrees with the raw HCED side orientation and direct
# sources.  Actor correction is explicit, but no result reversal is needed.
WAVE8_IRISH_HISTORY_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_IRISH_HISTORY_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_IRISH_HISTORY_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_source_duplicate_dispositions": (
            WAVE8_IRISH_HISTORY_CROSS_SOURCE_DUPLICATE_DISPOSITIONS
        ),
        "entities": WAVE8_IRISH_HISTORY_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_IRISH_HISTORY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(
            WAVE8_IRISH_HISTORY_EXPECTED_CANDIDATE_IDS
        ),
        "location_quarantine_reasons": (
            WAVE8_IRISH_HISTORY_LOCATION_QUARANTINE_REASONS
        ),
        "outcome_overrides": WAVE8_IRISH_HISTORY_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS,
        "sources": WAVE8_IRISH_HISTORY_SOURCES,
        "terminal_exclusions": WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS,
    }


def wave8_irish_history_audit_signature() -> str:
    """Return the SHA-256 pin over the complete researched lane state."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_IRISH_HISTORY_FINAL_AUDIT_SIGNATURE = (
    "cb8601506d8ce25cceb9fcf7df01e388fb589dc692ba12b83708d6af58fb4815"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_IRISH_HISTORY_CONTRACTS), len(WAVE8_IRISH_HISTORY_HOLDS)) != (
        8,
        1,
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_IRISH_HISTORY_ENTITIES), len(WAVE8_IRISH_HISTORY_SOURCES)) != (
        17,
        16,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_IRISH_HISTORY_RESERVED_IDS != WAVE8_IRISH_HISTORY_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_IRISH_HISTORY_CONTRACT_IDS & WAVE8_IRISH_HISTORY_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotions and exclusions overlap")
    if (
        wave8_irish_history_audit_signature()
        != WAVE8_IRISH_HISTORY_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_IRISH_HISTORY_SOURCES
    }
    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_IRISH_HISTORY_ENTITIES
    }
    if len(source_by_id) != len(WAVE8_IRISH_HISTORY_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(entity_by_id) != len(WAVE8_IRISH_HISTORY_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")

    forbidden_names = {
        "danish dublin",
        "england",
        "english",
        "ireland",
        "irish",
        "viking",
        "vikings",
    }
    for entity in WAVE8_IRISH_HISTORY_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity is not event-year bounded")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} opened a timeless generic identity")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity provenance is nondeterministic")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    for candidate_id, contract in WAVE8_IRISH_HISTORY_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} promotion hash table drifted")
        if contract["result_type"] != "win" or contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} promotion outcome orientation changed")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} contains an outcome reversal")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} provenance is nondeterministic")
        if not outcomes or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} lacks direct outcome provenance")
        if not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} promotion names an unknown source")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")

        canonical = contract["canonical_event"]
        year = int(canonical["year_low"])
        if year != int(canonical["year_high"]) or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical date contract changed")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing formations")
        for entity_id in (*side_1, *side_2):
            entity = entity_by_id.get(entity_id)
            if entity is None:
                raise ValueError(f"{_LANE_NAME} promotion uses a non-lane identity")
            if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} promotion exceeds an identity window")

    derry = WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS["hced-Derry1600-1"]
    if derry["raw_row_sha256"] != _ROW_HASHES["hced-Derry1600-1"]:
        raise ValueError(f"{_LANE_NAME} Derry hash changed")
    if (
        derry["disposition"] != "terminal_exclusion"
        or derry["result_type"] != "unknown"
        or derry["reviewed_outcome"] != "unknown"
        or derry["unknown_is_never_draw"] is not True
        or "winner_side" in derry
    ):
        raise ValueError(f"{_LANE_NAME} Derry exclusion became a result")
    if derry["side_2_entity_ids"] or derry["opposing_force_status"] != "none_evidenced":
        raise ValueError(f"{_LANE_NAME} invented an opposing Derry formation")
    if derry["side_1_entity_ids"] != ["docwra_lough_foyle_expedition_1600"]:
        raise ValueError(f"{_LANE_NAME} Derry expedition identity changed")
    if not set(derry["evidence_refs"]) <= set(source_by_id):
        raise ValueError(f"{_LANE_NAME} Derry evidence changed")

    if WAVE8_IRISH_HISTORY_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} invented an outcome override")
    if WAVE8_IRISH_HISTORY_CROSS_SOURCE_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} cross-source duplicate inventory changed")
    if WAVE8_IRISH_HISTORY_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} release duplicate inventory changed")
    if set(WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS) != {
        "hced-Dublin (1st)1171-1"
    }:
        raise ValueError(f"{_LANE_NAME} related HCED inventory changed")
    related = WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS[
        "hced-Dublin (1st)1171-1"
    ]
    if (
        related["hced_candidate_id"] != "hced-Dublin (2nd)1171-1"
        or related["disposition"] != "distinct_same_year_engagement"
    ):
        raise ValueError(f"{_LANE_NAME} Dublin event boundary changed")

    if WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS != WAVE8_IRISH_HISTORY_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_IRISH_HISTORY_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_IRISH_HISTORY_LOCATION_QUARANTINE_REASONS) != set(
        WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS
    ):
        raise ValueError(f"{_LANE_NAME} location reasons are incomplete")
    for record in WAVE8_IRISH_HISTORY_LOCATION_QUARANTINE_REASONS.values():
        if record["action"] != "withhold_point":
            raise ValueError(f"{_LANE_NAME} location action changed")
        if not set(record["evidence_refs"]) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location reason names an unknown source")


def validate_wave8_irish_history_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_IRISH_HISTORY_CONTRACTS,
        WAVE8_IRISH_HISTORY_HOLDS,
        lane_name=_LANE_NAME,
    )


_DUPLICATE_MATCH_KEYS = frozenset(
    {
        ("battle of tara", 980),
        ("tara", 980),
        ("battle of clontarf", 1014),
        ("clontarf", 1014),
        ("dublin", 1171),
        ("siege of dublin", 1171),
        ("battle of dysert o dea", 1318),
        ("dysert o dea", 1318),
        ("battle of the ford of the biscuits", 1594),
        ("ford of the biscuits", 1594),
        ("battle of clontibret", 1595),
        ("clontibret", 1595),
        ("battle of the yellow ford", 1598),
        ("blackwater", 1598),
        ("yellow ford", 1598),
        ("derry", 1600),
        ("unopposed occupation of derry", 1600),
        ("limerick", 1651),
        ("siege of limerick", 1651),
    }
)


def _row_year(row: Mapping[str, Any]) -> int | None:
    if row.get("year") is not None:
        return int(row["year"])
    start_date = str(row.get("start_date") or "")
    if len(start_date) >= 4 and start_date[:4].isdigit():
        return int(start_date[:4])
    return None


def validate_wave8_irish_history_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on Dublin disambiguation and newly appearing source twins."""

    _validate_static()
    related_id = "hced-Dublin (1st)1171-1"
    related_rows = [
        row for row in hced_rows if str(row.get("candidate_id")) == related_id
    ]
    if len(related_rows) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one related {related_id} row, "
            f"found {len(related_rows)}"
        )
    expected_hash = WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS[related_id][
        "raw_row_sha256"
    ]
    if canonical_hced_row_sha256(related_rows[0]) != expected_hash:
        raise ValueError(f"{_LANE_NAME} related Dublin fingerprint changed")

    iwbd_matches = sorted(
        str(row.get("candidate_id") or row.get("source_row") or "unknown")
        for row in iwbd_rows
        if (normalize_label(row.get("name")), _row_year(row))
        in _DUPLICATE_MATCH_KEYS
    )
    if iwbd_matches:
        raise ValueError(
            f"{_LANE_NAME} found unadjudicated IWBD duplicate candidates: "
            f"{iwbd_matches}"
        )

    release_matches = sorted(
        str(event.get("id") or "unknown")
        for event in existing_events
        if (
            normalize_label(event.get("name")),
            _row_year(event),
        )
        in _DUPLICATE_MATCH_KEYS
        and event.get("hced_candidate_id") not in WAVE8_IRISH_HISTORY_CONTRACT_IDS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} found unadjudicated release duplicates: {release_matches}"
        )

    return {
        "cross_source_duplicate_dispositions": len(
            WAVE8_IRISH_HISTORY_CROSS_SOURCE_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(
            WAVE8_IRISH_HISTORY_INTEGRATION_DISPOSITIONS
        ),
        "related_hced_dispositions": len(
            WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS
        ),
    }


def install_wave8_irish_history_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_IRISH_HISTORY_SOURCES,
        lane_name=_LANE_NAME,
    )


def install_wave8_irish_history_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_IRISH_HISTORY_ENTITIES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_IRISH_HISTORY_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_irish_history_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_irish_history_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_IRISH_HISTORY_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_irish_history_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_IRISH_HISTORY_CONTRACTS.values()
            ).items()
        )
    )


def wave8_irish_history_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_IRISH_HISTORY_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_source_duplicate_dispositions": len(
            WAVE8_IRISH_HISTORY_CROSS_SOURCE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_IRISH_HISTORY_HOLDS),
        "integration_dispositions": len(
            WAVE8_IRISH_HISTORY_INTEGRATION_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_IRISH_HISTORY_ENTITIES),
        "new_sources": len(WAVE8_IRISH_HISTORY_SOURCES),
        "newly_rated_events": len(WAVE8_IRISH_HISTORY_CONTRACTS),
        "outcome_overrides": len(WAVE8_IRISH_HISTORY_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_IRISH_HISTORY_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_IRISH_HISTORY_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_IRISH_HISTORY_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_IRISH_HISTORY_TERMINAL_EXCLUSIONS),
    }


def wave8_irish_history_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_IRISH_HISTORY_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_IRISH_HISTORY_POINT_QUARANTINE_ADDITIONS,
    }
