"""Exact Wave 8 audit for HCED rows whose unresolved label is ``Savoy``.

The seven source rows do not describe one timeless actor.  Gallipoli belongs
to Amadeus VI's mixed 1366 crusading expedition; Borgomanero, Geneva, Nice,
and Staffarda involve the ducal Savoyard state and reviewed coalitions;
Cassano's ``Savoy`` is Prince Eugene's surname rather than a belligerent
polity; and the 1628 Casale row conflates the actual siege belligerents.  This
lane therefore opens no generic Savoy, Savoyard, Piedmont, or dynastic alias
and transfers no rating across the county, duchy, or royal-state boundaries.
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
    "WAVE8_SAVOY_CONTRACT_IDS",
    "WAVE8_SAVOY_CONTRACTS",
    "WAVE8_SAVOY_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SAVOY_CROSS_LANE_DISPOSITIONS",
    "WAVE8_SAVOY_ENTITIES",
    "WAVE8_SAVOY_EXCLUSION_IDS",
    "WAVE8_SAVOY_EXCLUSIONS",
    "WAVE8_SAVOY_EXPECTED_CANDIDATE_IDS",
    "WAVE8_SAVOY_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SAVOY_HOLD_IDS",
    "WAVE8_SAVOY_HOLDS",
    "WAVE8_SAVOY_INTEGRATION_DISPOSITIONS",
    "WAVE8_SAVOY_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_SAVOY_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_SAVOY_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_SAVOY_LOCATION_REVIEWS",
    "WAVE8_SAVOY_NONPROMOTIONS",
    "WAVE8_SAVOY_OUTCOME_OVERRIDES",
    "WAVE8_SAVOY_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SAVOY_RELATED_HCED_DISPOSITIONS",
    "WAVE8_SAVOY_RESERVED_IDS",
    "WAVE8_SAVOY_SOURCES",
    "install_wave8_savoy_entities",
    "install_wave8_savoy_sources",
    "promote_wave8_savoy_contracts",
    "validate_wave8_savoy_integration_dispositions",
    "validate_wave8_savoy_queue_contracts",
    "wave8_savoy_audit_signature",
    "wave8_savoy_cohort_counts",
    "wave8_savoy_counts",
    "wave8_savoy_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Savoy exact-label audit"
_EVENT_ID_PREFIX = "hced_wave8_savoy_"

_SAVOYARD_CRUSADE_ID = "amadeus_vi_savoyard_crusade_1366_1367"
_DUCAL_SAVOY_ID = "savoyard_state_ducal_1416_1713"
_SFORZA_VENETIAN_ID = "sforza_venetian_borgomanero_coalition_1449"
_GENEVA_REPUBLIC_ID = "republic_geneva_1536_1798"

_FRANCE_ID = "kingdom_france"
_OTTOMAN_ID = "ottoman_empire"
_SPAIN_ID = "spanish_empire"


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


WAVE8_SAVOY_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_savoy_borgomanero_municipality",
        "La Battaglia di Borgomanero: 22 aprile 1449",
        (
            "https://www.comune.borgomanero.no.it/Borgomanero/pdf/"
            "Battaglia_di_Borgomanero.pdf"
        ),
        "Citta di Borgomanero",
        "municipal_commissioned_battle_study",
        "borgomanero_municipal_battle_study",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_treccani_fogliano",
        "Fogliano, Corrado da",
        (
            "https://www.treccani.it/enciclopedia/corrado-da-fogliano_"
            "%28Dizionario-Biografico%29/"
        ),
        "Dizionario Biografico degli Italiani, Treccani",
        "scholarly_biographical_encyclopedia",
        "treccani_fogliano_biography",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_cox_green_count",
        "The Green Count of Savoy: Amadeus VI and Transalpine Savoy",
        "https://doi.org/10.1515/9781400874996",
        "Princeton University Press; De Gruyter Brill",
        "scholarly_monograph",
        "cox_green_count_monograph",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_rennes_amadeus_vi",
        (
            "Les entreprises d'Amedee VI, entre aventures etrangeres et "
            "guerres intestines (1355-1383)"
        ),
        "https://books.openedition.org/pur/194446?lang=fr",
        "Presses universitaires de Rennes",
        "scholarly_history_chapter",
        "rennes_amadeus_vi_study",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_cambridge_dynasty_diplomacy",
        "Dynasty and Diplomacy in the Court of Savoy",
        "https://assets.cambridge.org/052165/2685/sample/0521652685ws.pdf",
        "Cambridge University Press",
        "scholarly_monograph_sample",
        "cambridge_osborne_dynasty_diplomacy",
    ),
    _source(
        "wave8_savoy_cambridge_rise_1690_1720",
        "War, Diplomacy and the Rise of Savoy, 1690-1720: Introduction",
        (
            "https://www.cambridge.org/core/books/war-diplomacy-and-the-rise-"
            "of-savoy-16901720/introduction/1BEFEC9929F1231657C9B285E752887D"
        ),
        "Cambridge University Press",
        "scholarly_monograph_chapter",
        "cambridge_storrs_rise_of_savoy",
    ),
    _source(
        "wave8_savoy_hls_geneva_republic",
        "Geneve (canton): La Republique (1536-1798)",
        "https://hls-dhs-dss.ch/fr/articles/007398/",
        "Dictionnaire historique de la Suisse",
        "national_scholarly_encyclopedia",
        "hls_geneva_republic",
    ),
    _source(
        "wave8_savoy_geneva_archives_escalade",
        "L'Escalade: premier recit du 12 decembre 1602",
        "https://archives-etat-ge.ch/page_de_base/premier-recit-de-lescalade/",
        "Archives d'Etat de Geneve",
        "state_archive_historical_exhibit",
        "geneva_state_archives_escalade",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_swiss_museum_escalade",
        "Swiss History: The Geneva Escalade",
        "https://blog.nationalmuseum.ch/en/2020/12/geneva-escalade/",
        "Swiss National Museum",
        "national_museum_historical_article",
        "swiss_national_museum_escalade",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_cambridge_ottoman_europe",
        "The Ottoman Empire and Early Modern Europe",
        (
            "https://assets.cambridge.org/97805214/52809/frontmatter/"
            "9780521452809_frontmatter.pdf"
        ),
        "Cambridge University Press",
        "scholarly_monograph_chronology",
        "cambridge_goffman_ottoman_europe",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_pup_provence_nice",
        "La Provence des rois de France: De Charles VIII a Henri II",
        "https://books.openedition.org/pup/13488?lang=en",
        "Presses universitaires de Provence",
        "scholarly_history_chapter",
        "pup_provence_renaissance_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_treccani_staffarda",
        "Staffarda: La battaglia di Staffarda",
        (
            "https://www.treccani.it/enciclopedia/staffarda_"
            "%28Enciclopedia-Italiana%29/"
        ),
        "Enciclopedia Italiana, Treccani",
        "scholarly_encyclopedia",
        "treccani_staffarda",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_polito_staffarda",
        (
            "La difesa dello stato: il progetto delle piazzeforti milanesi "
            "di Joseph Chafrion alla fine del XVII secolo"
        ),
        "https://doi.org/10.17401/studiericerche.7.2020-pozzati",
        "Politecnico di Torino; Studi e Ricerche di Storia dell'Architettura",
        "peer_reviewed_historical_article",
        "polito_pozzati_staffarda",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_pur_vendome_cassano",
        "Le duc de Vendome en Italie (1702-1706)",
        "https://books.openedition.org/pur/155462?lang=fr",
        "Presses universitaires de Rennes",
        "scholarly_history_chapter",
        "pur_vendome_italy_cassano",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_bnf_cassano",
        (
            "La Victoire remportee par l'armee du Roy sur l'armee "
            "Imperialle pres de Cassano, 16 aout 1705"
        ),
        "https://catalogue.bnf.fr/ark:/12148/cb415058702",
        "Bibliotheque nationale de France",
        "national_library_contemporary_print_catalogue",
        "bnf_cassano_victory_print",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_savoy_treccani_mantua_monferrato",
        "Mantova e Monferrato, Guerra di successione di",
        (
            "https://www.treccani.it/enciclopedia/mantova-e-monferrato-"
            "guerra-di-successione-di_%28Enciclopedia-Italiana%29/"
        ),
        "Enciclopedia Italiana, Treccani",
        "scholarly_encyclopedia",
        "treccani_mantua_monferrato_succession",
        crosscheck=True,
    ),
)


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_SAVOY_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    region: str,
    source_ids: list[str],
    continuity_note: str,
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
        "source_ids": sorted(source_ids),
    }


WAVE8_SAVOY_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _SAVOYARD_CRUSADE_ID,
        "Amadeus VI's Savoyard Crusading Expedition (1366-1367)",
        "campaign_bounded_crusading_coalition",
        1366,
        1367,
        "Dardanelles, Black Sea, and Balkans",
        ["wave8_savoy_cox_green_count", "wave8_savoy_rennes_amadeus_vi"],
        (
            "Campaign-bounded expedition led and financed by Amadeus VI, Count "
            "of Savoy, including joined Gattilusio and Byzantine elements at "
            "Gallipoli. No rating is inherited by the County or Duchy of Savoy, "
            "a generic crusader identity, Byzantium, Lesbos, a dynasty, or any "
            "predecessor, successor, ethnic group, or modern state."
        ),
    ),
    _entity(
        _SFORZA_VENETIAN_ID,
        "Sforza-Venetian Coalition at Borgomanero (1449)",
        "engagement_bounded_claimant_coalition",
        1449,
        1449,
        "Novarese, northern Italy",
        [
            "wave8_savoy_borgomanero_municipality",
            "wave8_savoy_treccani_fogliano",
        ],
        (
            "The exact Sforza formations and Venetian-service troops under "
            "Bartolomeo Colleoni that fought at Borgomanero. No rating is "
            "inherited by Milan, the Ambrosian Republic, the later Sforza duchy, "
            "Venice as a whole, another claimant army, or any successor."
        ),
    ),
    _entity(
        _DUCAL_SAVOY_ID,
        "Savoyard State under the Dukes (1416-1713)",
        "composite_ducal_state",
        1416,
        1713,
        "Savoy, Piedmont, Aosta, and Nice",
        [
            "wave8_savoy_cambridge_dynasty_diplomacy",
            "wave8_savoy_cambridge_rise_1690_1720",
        ],
        (
            "Composite Savoyard state from the elevation of Amadeus VIII to duke "
            "in 1416 through Victor Amadeus II's internationally recognized royal "
            "crown of Sicily in 1713. No rating is inherited by the earlier County "
            "of Savoy, the House of Savoy, Prince Eugene's Imperial service, the "
            "1713-1720 Sicilian monarchy, Sardinia-Piedmont, Italy, or a modern state."
        ),
    ),
    _entity(
        _GENEVA_REPUBLIC_ID,
        "Republic of Geneva (1536-1798)",
        "sovereign_city_republic",
        1536,
        1798,
        "Geneva and its subject territories",
        [
            "wave8_savoy_geneva_archives_escalade",
            "wave8_savoy_hls_geneva_republic",
            "wave8_savoy_swiss_museum_escalade",
        ],
        (
            "Independent sovereign Reformed republic from the 1536 political "
            "emancipation through French annexation in 1798. No rating is inherited "
            "by the earlier episcopal principality, Bernese forces, the French "
            "department of Leman, the post-1815 canton, Switzerland, or a modern state."
        ),
    ),
)


_ROW_HASHES = {
    "hced-Borgomanero1449-1": (
        "5ad9b2e9ba9dba94c86106400394216e8ca1d8b9a1a67ad5b1235cd2e4fd6d19"
    ),
    "hced-Casale1628-1": (
        "fe4a1f4a2b090cf61bf28108039f44b7559fab3bcf28f62ee151a0802662b03d"
    ),
    "hced-Cassano1705-1": (
        "a4cf2aef945218d3d30687d5006e1bcab0fea7fbd32d5dc740ecfd36c07b0d3f"
    ),
    "hced-Gallipoli1366-1": (
        "c18d7daf3413db7c7d4b6b01c253c164def81e35155c1ccbc98210de25ffd8f6"
    ),
    "hced-Geneva1602-1": (
        "427e5481e255d16744ea54fd64767612a9e36fd9d4ec6dfcfa395bd756c64e34"
    ),
    "hced-Nice1543-1": (
        "2aca66888096de16a02af6c63e7c4905cebaf8086b6f6c365e76219718d82b15"
    ),
    "hced-Staffarda1690-1": (
        "239ab51cf8f3058a46bdfd56e1dfc41ed2e80a0e9d9c1dd4caabd61b836c3775"
    ),
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
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
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
    *,
    confidence: float,
    war_type: str = "interstate_limited",
) -> dict[str, Any]:
    outcomes = sorted(outcome_source_ids)
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(side_1_entity_ids),
        "side_2_entity_ids": sorted(side_2_entity_ids),
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": sorted(evidence_refs),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "audit_note": audit_note,
    }


WAVE8_SAVOY_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Gallipoli1366-1": _contract(
        "hced-Gallipoli1366-1",
        _canonical(
            "Capture of Gallipoli by the Savoyard Crusade",
            1366,
            "22-26 August 1366",
            date_precision="day_range",
        ),
        "savoyard_crusade_gallipoli_1366",
        [_SAVOYARD_CRUSADE_ID],
        [_OTTOMAN_ID],
        ["wave8_savoy_cox_green_count", "wave8_savoy_rennes_amadeus_vi"],
        ["wave8_savoy_cox_green_count", "wave8_savoy_rennes_amadeus_vi"],
        (
            "Amadeus VI's mixed crusading expedition attacked Gallipoli and had "
            "the town and citadel in its hands by 26 August. The actor is the "
            "campaign coalition led by the Count of Savoy, not a timeless Savoy "
            "polity and not the later Duchy."
        ),
        confidence=0.94,
    ),
    "hced-Borgomanero1449-1": _contract(
        "hced-Borgomanero1449-1",
        _canonical(
            "Battle of Borgomanero",
            1449,
            "20-23 April 1449 (source date variance)",
            date_precision="day_range",
        ),
        "milanese_succession_borgomanero_1449",
        [_SFORZA_VENETIAN_ID],
        [_FRANCE_ID, _DUCAL_SAVOY_ID],
        [
            "wave8_savoy_borgomanero_municipality",
            "wave8_savoy_treccani_fogliano",
        ],
        [
            "wave8_savoy_borgomanero_municipality",
            "wave8_savoy_treccani_fogliano",
        ],
        (
            "Colleoni's Sforza-Venetian force defeated the Savoyard and French "
            "force near Borgomanero. HCED's generic Milan winner is corrected to "
            "the claimant coalition, while the day is retained as a narrow range "
            "because the reviewed sources give 20, 22, and 23 April."
        ),
        confidence=0.91,
        war_type="state_formation_conflict",
    ),
    "hced-Nice1543-1": _contract(
        "hced-Nice1543-1",
        _canonical(
            "Capture of the lower town of Nice",
            1543,
            "10-22 August 1543",
            date_precision="day_range",
        ),
        "italian_war_nice_1543",
        [_FRANCE_ID, _OTTOMAN_ID],
        [_DUCAL_SAVOY_ID],
        [
            "wave8_savoy_cambridge_ottoman_europe",
            "wave8_savoy_pup_provence_nice",
        ],
        [
            "wave8_savoy_cambridge_ottoman_europe",
            "wave8_savoy_pup_provence_nice",
        ],
        (
            "The exact rated phase is the joint Franco-Ottoman capture of Nice's "
            "lower town on 22 August. The castle held and the allies later withdrew, "
            "so this contract does not invent a result for the entire strategic "
            "siege or omit France from the attacking coalition."
        ),
        confidence=0.90,
    ),
    "hced-Geneva1602-1": _contract(
        "hced-Geneva1602-1",
        _canonical(
            "Escalade of Geneva",
            1602,
            (
                "night of 11-12 December 1602 Old Style "
                "(21-22 December New Style)"
            ),
            date_precision="day_range",
        ),
        "geneva_escalade_1602",
        [_GENEVA_REPUBLIC_ID],
        [_DUCAL_SAVOY_ID],
        [
            "wave8_savoy_geneva_archives_escalade",
            "wave8_savoy_hls_geneva_republic",
            "wave8_savoy_swiss_museum_escalade",
        ],
        [
            "wave8_savoy_geneva_archives_escalade",
            "wave8_savoy_swiss_museum_escalade",
        ],
        (
            "Geneva's civic defense defeated Charles Emmanuel I's surprise "
            "Savoyard assault before dawn. The winner is the sovereign Republic "
            "of Geneva, not Switzerland or a generic Swiss formation."
        ),
        confidence=0.98,
    ),
    "hced-Staffarda1690-1": _contract(
        "hced-Staffarda1690-1",
        _canonical("Battle of Staffarda", 1690, "18 August 1690"),
        "nine_years_war_staffarda_1690",
        [_FRANCE_ID],
        [_DUCAL_SAVOY_ID, _SPAIN_ID],
        [
            "wave8_savoy_cambridge_rise_1690_1720",
            "wave8_savoy_polito_staffarda",
            "wave8_savoy_treccani_staffarda",
        ],
        ["wave8_savoy_polito_staffarda", "wave8_savoy_treccani_staffarda"],
        (
            "Catinat's French army defeated Victor Amadeus II's Savoyard army "
            "and its Spanish reinforcements. Imperial troops promised for the "
            "theatre had not yet joined, so no Habsburg participant is invented."
        ),
        confidence=0.96,
    ),
}


WAVE8_SAVOY_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Cassano1705-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Cassano1705-1"],
        "canonical_event": _canonical(
            "Battle of Cassano",
            1705,
            "16 August 1705",
        ),
        "cohort": "war_of_spanish_succession_cassano_1705",
        "disposition": "research_hold",
        "hold_category": "conflicting_tactical_outcome_and_false_savoy_actor",
        "reviewed_outcome": "unresolved_conflict",
        "unknown_is_never_draw": True,
        "evidence_refs": sorted(
            ["wave8_savoy_bnf_cassano", "wave8_savoy_pur_vendome_cassano"]
        ),
        "hold_reason": (
            "Savoy in this row is Prince Eugene's surname: he commanded an "
            "Imperial army, not the Savoyard polity. The contemporary French "
            "victory print and modern scholarly account (which calls the combat "
            "indecisive) do not support one uncontested tactical result. The row "
            "remains unrated; uncertainty is not encoded as a draw."
        ),
    }
}


WAVE8_SAVOY_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Casale1628-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Casale1628-1"],
        "canonical_event": _canonical(
            "Conflated Casale siege assertion",
            1628,
            "1628",
            date_precision="year",
            granularity="source_conflation",
        ),
        "cohort": "mantuan_succession_source_conflation",
        "disposition": "terminal_exclusion",
        "hold_category": "source_conflates_siege_location_and_belligerents",
        "reviewed_outcome": "not_a_valid_event_assertion",
        "unknown_is_never_draw": True,
        "evidence_refs": sorted(
            [
                "wave8_savoy_cambridge_dynasty_diplomacy",
                "wave8_savoy_treccani_mantua_monferrato",
            ]
        ),
        "hold_reason": (
            "In 1628 Savoyard troops attacked Trino, Alba, and Moncalvo while "
            "Spanish troops besieged Casale; France was still committed at La "
            "Rochelle and did not defeat Savoy at Casale. A French-associated "
            "relief force was instead defeated by Savoy at Sampeyre. The row "
            "cannot be repaired without replacing its location, sides, and event, "
            "so it is terminally excluded and never converted to a draw."
        ),
    }
}


WAVE8_SAVOY_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_SAVOY_HOLDS,
    **WAVE8_SAVOY_EXCLUSIONS,
}
WAVE8_SAVOY_CONTRACT_IDS = frozenset(WAVE8_SAVOY_CONTRACTS)
WAVE8_SAVOY_HOLD_IDS = frozenset(WAVE8_SAVOY_HOLDS)
WAVE8_SAVOY_EXCLUSION_IDS = frozenset(WAVE8_SAVOY_EXCLUSIONS)
WAVE8_SAVOY_RESERVED_IDS = (
    WAVE8_SAVOY_CONTRACT_IDS
    | WAVE8_SAVOY_HOLD_IDS
    | WAVE8_SAVOY_EXCLUSION_IDS
)
WAVE8_SAVOY_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


# All five promoted coordinates identify the documented city, fortress, or
# battlefield and carry the correct modern country.  Nonpromotions are not
# added to the shared quarantine manifest because they emit no event.
WAVE8_SAVOY_LOCATION_REVIEWS: dict[str, dict[str, Any]] = {
    "hced-Borgomanero1449-1": {
        "action": "retain_point_and_country",
        "evidence_refs": ["wave8_savoy_borgomanero_municipality"],
        "reason": "The point is Borgomanero beside the documented battle area.",
    },
    "hced-Gallipoli1366-1": {
        "action": "retain_point_and_country",
        "evidence_refs": ["wave8_savoy_cox_green_count"],
        "reason": "The point and Turkey field identify the Gallipoli fortress.",
    },
    "hced-Geneva1602-1": {
        "action": "retain_point_and_country",
        "evidence_refs": ["wave8_savoy_geneva_archives_escalade"],
        "reason": "The point identifies the walled city attacked in the Escalade.",
    },
    "hced-Nice1543-1": {
        "action": "retain_point_and_country",
        "evidence_refs": ["wave8_savoy_pup_provence_nice"],
        "reason": "The point identifies Nice, and modern France is correct.",
    },
    "hced-Staffarda1690-1": {
        "action": "retain_point_and_country",
        "evidence_refs": ["wave8_savoy_treccani_staffarda"],
        "reason": "The point identifies Staffarda Abbey and the battle locality.",
    },
}
WAVE8_SAVOY_POINT_QUARANTINE_ADDITIONS = frozenset()
WAVE8_SAVOY_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_SAVOY_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_SAVOY_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_SAVOY_COUNTRY_QUARANTINE_ADDITIONS,
}


# Every promoted winner orientation agrees with HCED after actor correction.
# Cassano is held rather than converted into either an override or a draw.
WAVE8_SAVOY_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_SAVOY_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}


# Casale 1629 is already a separately keyed release assertion for the actual
# siege/relief sequence.  Its pin prevents the corrupt 1628 row from being
# silently shifted into that later record.
WAVE8_SAVOY_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Casale1629-1": {
        "source_dataset": "hced",
        "hced_candidate_id": "hced-Casale1628-1",
        "disposition": "related_later_siege_phase_already_separately_keyed",
        "relationship": "same_campaign_not_a_repair_target",
        "raw_row_sha256": (
            "75418ba7be825e6ad1b4e151879d9379fe18d5facc24276713ac843443f7578e"
        ),
        "evidence_refs": ["wave8_savoy_treccani_mantua_monferrato"],
        "reason": (
            "The 1629 row represents the later French relief phase against the "
            "Spanish siege. It does not validate HCED's separate 1628 France-versus-"
            "Savoy assertion and must not be merged into or duplicated by this lane."
        ),
    }
}
WAVE8_SAVOY_CROSS_LANE_DISPOSITIONS = WAVE8_SAVOY_RELATED_HCED_DISPOSITIONS
WAVE8_SAVOY_INTEGRATION_DISPOSITIONS = WAVE8_SAVOY_RELATED_HCED_DISPOSITIONS


# No same-name/same-year probable twin occurs in the locked IWBD snapshot.
# Exact aliases are pinned so a future source revision fails closed.
WAVE8_SAVOY_IWBD_ZERO_OVERLAP_AUDIT: dict[str, tuple[str, ...]] = {
    "1366": (
        "capture of gallipoli",
        "capture of gallipoli by the savoyard crusade",
        "gallipoli",
    ),
    "1449": ("battle of borgomanero", "borgomanero"),
    "1543": ("capture of nice", "nice", "siege of nice"),
    "1602": ("escalade of geneva", "geneva", "geneva escalade"),
    "1628": ("casale", "siege of casale"),
    "1690": ("battle of staffarda", "staffarda"),
    "1705": ("battle of cassano", "cassano"),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_SAVOY_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_SAVOY_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_SAVOY_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_SAVOY_ENTITIES,
        "exclusions": WAVE8_SAVOY_EXCLUSIONS,
        "expected_candidate_ids": sorted(WAVE8_SAVOY_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_SAVOY_HOLDS,
        "integration_dispositions": WAVE8_SAVOY_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_SAVOY_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_SAVOY_IWBD_ZERO_OVERLAP_AUDIT,
        "location_reviews": WAVE8_SAVOY_LOCATION_REVIEWS,
        "outcome_overrides": WAVE8_SAVOY_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_SAVOY_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_SAVOY_SOURCES,
    }


def wave8_savoy_audit_signature() -> str:
    """Return the immutable SHA-256 pin over the complete lane semantics."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_SAVOY_FINAL_AUDIT_SIGNATURE = (
    "3fb9510fb6966289c104698a3b7e8f8a7e41721440cf0766b93dfa3b225fb8d1"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_SAVOY_CONTRACTS),
        len(WAVE8_SAVOY_HOLDS),
        len(WAVE8_SAVOY_EXCLUSIONS),
    ) != (5, 1, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_SAVOY_ENTITIES), len(WAVE8_SAVOY_SOURCES)) != (4, 16):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_SAVOY_RESERVED_IDS != WAVE8_SAVOY_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if (
        WAVE8_SAVOY_CONTRACT_IDS & WAVE8_SAVOY_HOLD_IDS
        or WAVE8_SAVOY_CONTRACT_IDS & WAVE8_SAVOY_EXCLUSION_IDS
        or WAVE8_SAVOY_HOLD_IDS & WAVE8_SAVOY_EXCLUSION_IDS
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if wave8_savoy_audit_signature() != WAVE8_SAVOY_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_SAVOY_SOURCES}
    if len(source_by_id) != len(WAVE8_SAVOY_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    families = [str(source["source_family_id"]) for source in WAVE8_SAVOY_SOURCES]
    if len(families) != len(set(families)):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_SAVOY_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_SAVOY_ENTITIES}
    expected_windows = {
        _SAVOYARD_CRUSADE_ID: (1366, 1367),
        _DUCAL_SAVOY_ID: (1416, 1713),
        _SFORZA_VENETIAN_ID: (1449, 1449),
        _GENEVA_REPUBLIC_ID: (1536, 1798),
    }
    if set(entity_by_id) != set(expected_windows):
        raise ValueError(f"{_LANE_NAME} identity inventory changed")
    forbidden_generic_names = {
        "house of savoy",
        "piedmont",
        "savoy",
        "savoyards",
        "savoyard",
    }
    for entity_id, entity in entity_by_id.items():
        if (entity["start_year"], entity["end_year"]) != expected_windows[entity_id]:
            raise ValueError(f"{_LANE_NAME} identity window changed")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if normalize_label(entity["name"]) in forbidden_generic_names:
            raise ValueError(f"{_LANE_NAME} installed a timeless Savoy identity")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity provenance is nondeterministic")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    allowed_entities = {
        _FRANCE_ID,
        _OTTOMAN_ID,
        _SPAIN_ID,
        *entity_by_id,
    }
    used_new_entities: set[str] = set()
    used_sources: set[str] = set()
    expected_precisions = {
        "hced-Borgomanero1449-1": "day_range",
        "hced-Gallipoli1366-1": "day_range",
        "hced-Geneva1602-1": "day_range",
        "hced-Nice1543-1": "day_range",
        "hced-Staffarda1690-1": "day",
    }
    for candidate_id, contract in WAVE8_SAVOY_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} promotion hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["granularity"] != "engagement":
            raise ValueError(f"{_LANE_NAME} promoted a non-engagement")
        if canonical["date_precision"] != expected_precisions[candidate_id]:
            raise ValueError(f"{_LANE_NAME} date precision drifted")

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is nondeterministic")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= allowed_entities:
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        if "savoy" in {normalize_label(value) for value in (*side_1, *side_2)}:
            raise ValueError(f"{_LANE_NAME} rates a generic Savoy label")
        used_new_entities.update((set(side_1) | set(side_2)) & set(entity_by_id))
        year = int(canonical["year_low"])
        for entity_id in (set(side_1) | set(side_2)) & set(entity_by_id):
            start, end = expected_windows[entity_id]
            if not start <= year <= end:
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")

        if contract["result_type"] != "win" or contract["winner_side"] != 1:
            raise ValueError(f"{_LANE_NAME} invented a draw or unknown result")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} contains an outcome reversal")

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
            raise ValueError(f"{_LANE_NAME} outcome-family provenance drifted")
        used_sources.update(evidence)

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new identities are not exactly consumed")

    forbidden_nonpromotion_keys = {
        "losers",
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
        "winners",
    }
    for candidate_id, disposition in WAVE8_SAVOY_NONPROMOTIONS.items():
        if disposition["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} nonpromotion hash table drifted")
        if forbidden_nonpromotion_keys & set(disposition):
            raise ValueError(f"{_LANE_NAME} nonpromotion contains a rated result")
        if disposition["unknown_is_never_draw"] is not True:
            raise ValueError(f"{_LANE_NAME} permits unknown to become a draw")
        reason = str(disposition["hold_reason"]).casefold()
        if "draw" not in reason:
            raise ValueError(f"{_LANE_NAME} nonpromotion omits the no-draw rule")
        evidence = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} nonpromotion evidence drifted")
        used_sources.update(evidence)

    if WAVE8_SAVOY_HOLDS["hced-Cassano1705-1"]["disposition"] != "research_hold":
        raise ValueError(f"{_LANE_NAME} Cassano hold changed")
    cassano_reason = WAVE8_SAVOY_HOLDS["hced-Cassano1705-1"]["hold_reason"].casefold()
    if "prince eugene" not in cassano_reason or "imperial army" not in cassano_reason:
        raise ValueError(f"{_LANE_NAME} Cassano actor audit changed")
    if WAVE8_SAVOY_EXCLUSIONS["hced-Casale1628-1"]["disposition"] != "terminal_exclusion":
        raise ValueError(f"{_LANE_NAME} Casale exclusion changed")

    if set(WAVE8_SAVOY_LOCATION_REVIEWS) != WAVE8_SAVOY_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location review inventory changed")
    for review in WAVE8_SAVOY_LOCATION_REVIEWS.values():
        if review["action"] != "retain_point_and_country":
            raise ValueError(f"{_LANE_NAME} location disposition changed")
        evidence = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence drifted")
        used_sources.update(evidence)
    if WAVE8_SAVOY_POINT_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_SAVOY_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country quarantine contract changed")
    if WAVE8_SAVOY_OUTCOME_OVERRIDES or WAVE8_SAVOY_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} outcome or IWBD disposition changed")

    if set(WAVE8_SAVOY_RELATED_HCED_DISPOSITIONS) != {"hced-Casale1629-1"}:
        raise ValueError(f"{_LANE_NAME} related-HCED inventory changed")
    for disposition in WAVE8_SAVOY_RELATED_HCED_DISPOSITIONS.values():
        evidence = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} integration evidence drifted")
        used_sources.update(evidence)

    used_sources.update(
        source_id
        for entity in WAVE8_SAVOY_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if set(WAVE8_SAVOY_IWBD_ZERO_OVERLAP_AUDIT) != {
        "1366",
        "1449",
        "1543",
        "1602",
        "1628",
        "1690",
        "1705",
    }:
        raise ValueError(f"{_LANE_NAME} IWBD zero-overlap years changed")
    for aliases in WAVE8_SAVOY_IWBD_ZERO_OVERLAP_AUDIT.values():
        if not _is_sorted_unique(aliases):
            raise ValueError(f"{_LANE_NAME} IWBD aliases are nondeterministic")


def _is_exact_savoy_label(value: Any) -> bool:
    return normalize_label(value) == "savoy"


def validate_wave8_savoy_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin all and only the seven exact ``Savoy`` queue rows."""

    _validate_static()
    validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SAVOY_CONTRACTS,
        WAVE8_SAVOY_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_savoy_label(row.get("side_1_raw"))
        or _is_exact_savoy_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_SAVOY_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Savoy inventory changed: {sorted(exact_label_ids)}"
        )
    return {
        "promotion_contracts": len(WAVE8_SAVOY_CONTRACTS),
        "holds": len(WAVE8_SAVOY_HOLDS),
        "exclusions": len(WAVE8_SAVOY_EXCLUSIONS),
        "reviewed_hced_rows": len(WAVE8_SAVOY_RESERVED_IDS),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    value = row.get("year")
    if value is not None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    for field in ("start_date", "end_date"):
        text = str(row.get(field) or "")
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4])
    return None


_DUPLICATE_MATCH_KEYS = frozenset(
    {
        ("battle of borgomanero", 1449),
        ("borgomanero", 1449),
        ("capture of gallipoli", 1366),
        ("capture of gallipoli by the savoyard crusade", 1366),
        ("capture of nice", 1543),
        ("capture of the lower town of nice", 1543),
        ("escalade of geneva", 1602),
        ("gallipoli", 1366),
        ("geneva", 1602),
        ("nice", 1543),
        ("staffarda", 1690),
        ("battle of staffarda", 1690),
    }
)


def validate_wave8_savoy_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on related HCED drift and future cross-source twins."""

    validate_wave8_savoy_queue_contracts(hced_rows)
    related_id = "hced-Casale1629-1"
    related_rows = [
        row for row in hced_rows if str(row.get("candidate_id")) == related_id
    ]
    if len(related_rows) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one related {related_id} row, "
            f"found {len(related_rows)}"
        )
    expected_hash = WAVE8_SAVOY_RELATED_HCED_DISPOSITIONS[related_id][
        "raw_row_sha256"
    ]
    if canonical_hced_row_sha256(related_rows[0]) != expected_hash:
        raise ValueError(f"{_LANE_NAME} related Casale fingerprint changed")

    audited = {
        (int(year), normalize_label(name))
        for year, names in WAVE8_SAVOY_IWBD_ZERO_OVERLAP_AUDIT.items()
        for name in names
    }
    iwbd_matches = sorted(
        str(row.get("candidate_id") or row.get("source_row") or "unknown")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name"))) in audited
    )
    if iwbd_matches:
        raise ValueError(
            f"{_LANE_NAME} found unadjudicated IWBD duplicate candidates: "
            f"{iwbd_matches}"
        )

    release_matches = sorted(
        str(event.get("id") or "unknown")
        for event in existing_events
        if (normalize_label(event.get("name")), _row_year(event))
        in _DUPLICATE_MATCH_KEYS
        and event.get("hced_candidate_id") not in WAVE8_SAVOY_CONTRACT_IDS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} found unadjudicated release duplicates: {release_matches}"
        )

    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_SAVOY_CROSS_LANE_DISPOSITIONS
        ),
        "integration_dispositions": len(WAVE8_SAVOY_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_SAVOY_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "release_probable_twins": 0,
    }


def install_wave8_savoy_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SAVOY_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_savoy_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SAVOY_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SAVOY_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SAVOY_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_savoy_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_savoy_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SAVOY_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_savoy_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_SAVOY_CONTRACTS.values()
            ).items()
        )
    )


def wave8_savoy_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_SAVOY_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_SAVOY_CROSS_LANE_DISPOSITIONS
        ),
        "exclusions": len(WAVE8_SAVOY_EXCLUSIONS),
        "holds": len(WAVE8_SAVOY_HOLDS),
        "integration_dispositions": len(WAVE8_SAVOY_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_SAVOY_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "location_reviews": len(WAVE8_SAVOY_LOCATION_REVIEWS),
        "new_entities": len(WAVE8_SAVOY_ENTITIES),
        "new_sources": len(WAVE8_SAVOY_SOURCES),
        "newly_rated_events": len(WAVE8_SAVOY_CONTRACTS),
        "outcome_overrides": len(WAVE8_SAVOY_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_SAVOY_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_SAVOY_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_SAVOY_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_SAVOY_EXCLUSIONS),
    }


def wave8_savoy_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_SAVOY_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_SAVOY_POINT_QUARANTINE_ADDITIONS,
    }
