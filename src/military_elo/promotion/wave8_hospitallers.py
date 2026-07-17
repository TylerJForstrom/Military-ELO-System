"""Candidate-keyed Wave 8 audit for two Hospitaller source spellings.

HCED uses both ``Knights Hospitallier`` (a source misspelling) and
``Knights of St John`` for eight unresolved rows.  They are one audit lane,
not two aliases: the underlying events span the Order's last Levantine
castles, its conquest and defence of Rhodes, the Smyrna outpost, Tripoli,
and Malta.  Every promoted participant is therefore an event-bounded force;
no rating crosses the Levant, Rhodes, Smyrna, Tripoli, Malta, Byzantium,
Mamluk, Timurid, Ottoman, corsair, or Revolutionary-French boundaries.

All eight exact-label rows have independently attested outcomes.  The 1310
Rhodes row is explicitly the completion of the 1306--1310 conquest, not an
invented one-day battle; the literature's 1309/1310 dating disagreement is
recorded and reflected in lower confidence.  Five coalition spellings are
audited as adjacent rows but remain outside this exact-label lane, including
two already owned by the coded HCED pass.  Unknown is never a draw, and this
lane emits no draw, reversal, or unsupported result.
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
    "WAVE8_HOSPITALLERS_ADJACENT_CANDIDATE_IDS",
    "WAVE8_HOSPITALLERS_ADJACENT_LANE_DISPOSITIONS",
    "WAVE8_HOSPITALLERS_CONTRACT_IDS",
    "WAVE8_HOSPITALLERS_CONTRACTS",
    "WAVE8_HOSPITALLERS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_HOSPITALLERS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_HOSPITALLERS_CROSS_SPELLING_DUPLICATE_AUDIT",
    "WAVE8_HOSPITALLERS_ENTITIES",
    "WAVE8_HOSPITALLERS_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_HOSPITALLERS_EXACT_LABEL_FUNNEL_DIGESTS",
    "WAVE8_HOSPITALLERS_EXCLUSION_IDS",
    "WAVE8_HOSPITALLERS_EXCLUSIONS",
    "WAVE8_HOSPITALLERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_HOSPITALLERS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_HOSPITALLERS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_HOSPITALLERS_HOLD_IDS",
    "WAVE8_HOSPITALLERS_HOLDS",
    "WAVE8_HOSPITALLERS_INTEGRATION_DISPOSITIONS",
    "WAVE8_HOSPITALLERS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_HOSPITALLERS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_HOSPITALLERS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_HOSPITALLERS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_HOSPITALLERS_NONPROMOTIONS",
    "WAVE8_HOSPITALLERS_OPPOSITE_RESULT_AUDIT",
    "WAVE8_HOSPITALLERS_OUTCOME_OVERRIDES",
    "WAVE8_HOSPITALLERS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS",
    "WAVE8_HOSPITALLERS_RESERVED_IDS",
    "WAVE8_HOSPITALLERS_ROW_HASHES",
    "WAVE8_HOSPITALLERS_SOURCES",
    "WAVE8_HOSPITALLERS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS",
    "install_wave8_hospitallers_entities",
    "install_wave8_hospitallers_sources",
    "promote_wave8_hospitallers_contracts",
    "validate_wave8_hospitallers_integration_dispositions",
    "validate_wave8_hospitallers_queue_contracts",
    "wave8_hospitallers_audit_signature",
    "wave8_hospitallers_cohort_counts",
    "wave8_hospitallers_counts",
    "wave8_hospitallers_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 combined exact Hospitaller spellings audit"
_MODULE_OWNER = "military_elo.promotion.wave8_hospitallers"
_EVENT_ID_PREFIX = "hced_wave8_hospitallers_"
_EXACT_RAW_LABELS = frozenset({"Knights Hospitallier", "Knights of St John"})


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


WAVE8_HOSPITALLERS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_hospitallers_cambridge_krak_1271",
        "The taking of Le Krak des Chevaliers in 1271",
        "https://doi.org/10.1017/S0003598X0002007X",
        "Antiquity / Cambridge University Press",
        "peer_reviewed_archaeological_article",
        "cathcart_king_krak_1949",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_unesco_krak",
        "Crac des Chevaliers and Qal'at Salah El-Din nomination dossier",
        "https://whc.unesco.org/document/168916",
        "UNESCO World Heritage Centre",
        "official_heritage_nomination_dossier",
        "unesco_krak_nomination_dossier",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_edinburgh_margat",
        "Micromorphological and geochemical investigation of formation processes in the refectory at the Castle of Margat",
        "https://www.pure.ed.ac.uk/ws/portalfiles/portal/16836436/Micromorphological_and_Geochemical_Investigation_of_Formation_Processes_in_the_Refectory_at_the_Castle_of_Margat.pdf",
        "University of Edinburgh / Journal of Archaeological Science",
        "peer_reviewed_archaeological_article",
        "major_et_al_margat_archaeology_2015",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_michaudel_margat",
        "Fall and Rise of the Hospitaller and Templar Castles in Syria",
        "https://api.pageplace.de/preview/DT0400.9781317179863_A26662580/preview-9781317179863_A26662580.pdf",
        "Routledge, Archaeology and Architecture of the Military Orders",
        "scholarly_book_chapter",
        "michaudel_fall_rise_castles_2014",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_cnrs_rhodes_arrival",
        "Rhodes et l'ordre de Saint-Jean-de-Jerusalem: L'arrivee a Rhodes",
        "https://books.openedition.org/editionscnrs/2572",
        "CNRS Editions / OpenEdition Books",
        "scholarly_book_chapter",
        "blondy_rhodes_arrival_2000",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_pur_rhodes_conquest",
        "Le siege de Rhodes par les Hospitaliers en 1306-1310",
        "https://books.openedition.org/pur/36638",
        "Presses universitaires de Rennes / OpenEdition Books",
        "scholarly_book_chapter",
        "rhodes_medieval_sieges_pur",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_ehr_rhodes_town",
        "The Town of Rhodes, 1306-1356",
        "https://doi.org/10.1093/ehr/cel331",
        "The English Historical Review / Oxford University Press",
        "scholarly_review",
        "edbury_luttrell_rhodes_review_2006",
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_cambridge_rhodes_bastion",
        "Rhodes and the origin of the bastion",
        (
            "https://www.cambridge.org/core/journals/antiquaries-journal/"
            "article/abs/rhodes-and-the-origin-of-the-bastion/"
            "0F2FF1F28B0352EBA7A1DBB39023DC74"
        ),
        "The Antiquaries Journal / Cambridge University Press",
        "peer_reviewed_architectural_history_article",
        "oneil_rhodes_bastion",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_cambridge_ottoman_expansion",
        "Ottoman expansion in the Mediterranean",
        "https://doi.org/10.1017/CHO9781139049047.009",
        "Cambridge University Press, The Cambridge History of Turkey",
        "scholarly_reference_chapter",
        "cambridge_history_turkey_mediterranean_expansion",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_cambridge_crusades_chronology",
        "The Cambridge Companion to the Literature of the Crusades: Chronology",
        "https://assets.cambridge.org/97811084/74511/frontmatter/9781108474511_frontmatter.pdf",
        "Cambridge University Press",
        "scholarly_reference_chronology",
        "cambridge_companion_crusades_chronology",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_fleet_smyrna",
        "European and Islamic Trade in the Early Ottoman State: Historical outline",
        "https://assets.cambridge.org/052164/2213/sample/0521642213wsc00.pdf",
        "Cambridge University Press",
        "scholarly_monograph",
        "kate_fleet_early_ottoman_trade_1999",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_luttrell_smyrna",
        "The Hospitallers of Rhodes: Prospects, Problems, Possibilities",
        "https://journals.ub.uni-heidelberg.de/index.php/vuf/article/download/16541/10385",
        "University of Heidelberg Journals",
        "peer_reviewed_scholarly_article",
        "luttrell_hospitallers_rhodes_prospects",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_nhrf_smyrna",
        "The Hospitallers and the Turks",
        "https://helios-eie.ekt.gr/EIE/bitstream/10442/16515/2/%CE%9205.014.0.pdf",
        "National Hellenic Research Foundation",
        "scholarly_source_study",
        "luttrell_zachariadou_hospitallers_turks",
        outcome=True,
    ),
    _source(
        "wave8_hospitallers_cambridge_tripoli_1551",
        "A Knight of Malta at the Court of Elizabeth I: Introduction",
        "https://assets.cambridge.org/97811070/92938/excerpt/9781107092938_excerpt.pdf",
        "Cambridge University Press",
        "scholarly_edited_primary_correspondence",
        "potter_michel_de_seure_2014",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_phillips_tripoli_1551",
        "Navies and the Mediterranean in the Early Modern Period",
        (
            "https://api.pageplace.de/preview/"
            "DT0400.9781136713170_A24375320/"
            "preview-9781136713170_A24375320.pdf"
        ),
        "Frank Cass / Routledge",
        "scholarly_edited_volume_chapter",
        "phillips_navies_mediterranean_2000",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_cambridge_malta_1798",
        "Holy Wars, Empires, and the Portability of the Past",
        "https://doi.org/10.1017/S0010417506000120",
        "Comparative Studies in Society and History / Cambridge University Press",
        "peer_reviewed_historical_article",
        "knobler_holy_wars_2006",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_heritage_malta_invasion",
        "A pivotal moment in Malta's history features in a new Heritage Malta documentary",
        "https://heritagemalta.mt/news/a-pivotal-moment-in-maltas-history-features-in-a-new-heritage-malta-documentary/",
        "Heritage Malta",
        "official_museum_history",
        "heritage_malta_napoleon_invasion_document",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_hospitallers_cambridge_malta_regimes",
        "Malta's Archaeological Past",
        "https://doi.org/10.1017/CBO9781139030465.002",
        "Cambridge University Press",
        "scholarly_monograph_chapter",
        "sagona_archaeology_malta_2015",
        outcome=True,
        crosscheck=True,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    boundary: str,
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
        "continuity_note": (
            f"Event-bounded participant: {boundary} No rating is inherited by "
            "the Order of St John in another territorial era, a broad religious "
            "order, a namesake organization, an opponent's wider regime, or any "
            "modern state or population."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_KRAK_MAMLUK = "baybars_mamluk_siege_army_krak_1271"
_KRAK_HOSPITALLER = "hospitaller_krak_garrison_1271"
_MARGAT_MAMLUK = "qalawun_mamluk_siege_army_margat_1285"
_MARGAT_HOSPITALLER = "hospitaller_margat_garrison_1285"
_RHODES_1310_HOSPITALLER = "villaret_hospitaller_rhodes_conquest_force_1310"
_RHODES_1310_BYZANTINE = "byzantine_rhodes_defenders_1310"
_SMYRNA_TIMURID = "timur_siege_army_smyrna_1402"
_SMYRNA_HOSPITALLER = "hospitaller_smyrna_garrison_1402"
_RHODES_1480_HOSPITALLER = "hospitaller_rhodes_defenders_1480"
_RHODES_1480_OTTOMAN = "ottoman_rhodes_expedition_1480"
_RHODES_1522_OTTOMAN = "suleiman_ottoman_siege_army_rhodes_1522"
_RHODES_1522_HOSPITALLER = "hospitaller_rhodes_defenders_1522"
_TRIPOLI_OTTOMAN = "sinan_pasha_ottoman_force_tripoli_1551"
_TRIPOLI_CORSAIR = "turgut_reis_corsair_force_tripoli_1551"
_TRIPOLI_HOSPITALLER = "hospitaller_tripoli_garrison_1551"
_MALTA_FRENCH = "french_army_orient_malta_1798"
_MALTA_HOSPITALLER = "hompesch_hospitaller_malta_garrison_1798"


WAVE8_HOSPITALLERS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _KRAK_MAMLUK,
        "Baybars's Mamluk siege army at Krak des Chevaliers (1271)",
        "event_bounded_mamluk_siege_army",
        1271,
        "Krak des Chevaliers, Syria",
        "Bounded to Baybars's force in the March-April siege and capture.",
        ["wave8_hospitallers_cambridge_krak_1271", "wave8_hospitallers_unesco_krak"],
    ),
    _entity(
        _KRAK_HOSPITALLER,
        "Hospitaller garrison of Krak des Chevaliers (1271)",
        "event_bounded_hospitaller_castle_garrison",
        1271,
        "Krak des Chevaliers, Syria",
        "Bounded to the Order's castle garrison that capitulated in April 1271.",
        ["wave8_hospitallers_cambridge_krak_1271", "wave8_hospitallers_unesco_krak"],
    ),
    _entity(
        _MARGAT_MAMLUK,
        "Qalawun's Mamluk siege army at Margat (1285)",
        "event_bounded_mamluk_siege_army",
        1285,
        "Margat (Qal'at al-Marqab), Syria",
        "Bounded to Qalawun's force in the April-May siege and capture.",
        ["wave8_hospitallers_edinburgh_margat", "wave8_hospitallers_michaudel_margat"],
    ),
    _entity(
        _MARGAT_HOSPITALLER,
        "Hospitaller garrison of Margat (1285)",
        "event_bounded_hospitaller_castle_garrison",
        1285,
        "Margat (Qal'at al-Marqab), Syria",
        "Bounded to the Margat garrison that surrendered on 25 May 1285.",
        ["wave8_hospitallers_edinburgh_margat", "wave8_hospitallers_michaudel_margat"],
    ),
    _entity(
        _RHODES_1310_HOSPITALLER,
        "Villaret's Hospitaller conquest force on Rhodes (1310 completion)",
        "event_bounded_hospitaller_conquest_force",
        1310,
        "Rhodes, Dodecanese",
        "Bounded to the final phase of the 1306-1310 acquisition of Rhodes.",
        ["wave8_hospitallers_cnrs_rhodes_arrival", "wave8_hospitallers_pur_rhodes_conquest"],
    ),
    _entity(
        _RHODES_1310_BYZANTINE,
        "Byzantine defenders of Rhodes in the final Hospitaller conquest phase (1310)",
        "event_bounded_byzantine_island_defenders",
        1310,
        "Rhodes, Dodecanese",
        "Bounded to the remaining Byzantine-held Rhodian position in the conquest's final phase.",
        ["wave8_hospitallers_cnrs_rhodes_arrival", "wave8_hospitallers_pur_rhodes_conquest"],
    ),
    _entity(
        _SMYRNA_TIMURID,
        "Timur's siege army at Smyrna (1402)",
        "event_bounded_timurid_siege_army",
        1402,
        "Lower Smyrna, Anatolia",
        "Bounded to Timur's December assault on the Latin sea-castle.",
        ["wave8_hospitallers_fleet_smyrna", "wave8_hospitallers_luttrell_smyrna", "wave8_hospitallers_nhrf_smyrna"],
    ),
    _entity(
        _SMYRNA_HOSPITALLER,
        "Hospitaller garrison of the Smyrna sea-castle (1402)",
        "event_bounded_hospitaller_outpost_garrison",
        1402,
        "Lower Smyrna, Anatolia",
        "Bounded to the Order-administered Latin garrison attacked in December 1402.",
        ["wave8_hospitallers_fleet_smyrna", "wave8_hospitallers_luttrell_smyrna", "wave8_hospitallers_nhrf_smyrna"],
    ),
    _entity(
        _RHODES_1480_HOSPITALLER,
        "Hospitaller defenders of Rhodes (1480)",
        "event_bounded_hospitaller_island_defenders",
        1480,
        "Rhodes, Dodecanese",
        "Bounded to the Order and island defenders who repelled the 1480 expedition.",
        ["wave8_hospitallers_cambridge_ottoman_expansion", "wave8_hospitallers_cambridge_rhodes_bastion"],
    ),
    _entity(
        _RHODES_1480_OTTOMAN,
        "Ottoman expedition against Rhodes (1480)",
        "event_bounded_ottoman_siege_expedition",
        1480,
        "Rhodes, Dodecanese",
        "Bounded to the unsuccessful 1480 Ottoman siege expedition.",
        ["wave8_hospitallers_cambridge_ottoman_expansion", "wave8_hospitallers_cambridge_rhodes_bastion"],
    ),
    _entity(
        _RHODES_1522_OTTOMAN,
        "Suleiman I's Ottoman siege army at Rhodes (1522)",
        "event_bounded_ottoman_siege_army",
        1522,
        "Rhodes, Dodecanese",
        "Bounded to the 1522 Ottoman siege ending in the December capitulation.",
        ["wave8_hospitallers_cambridge_crusades_chronology", "wave8_hospitallers_cambridge_rhodes_bastion"],
    ),
    _entity(
        _RHODES_1522_HOSPITALLER,
        "Hospitaller defenders of Rhodes (1522)",
        "event_bounded_hospitaller_island_defenders",
        1522,
        "Rhodes, Dodecanese",
        "Bounded to the Order's final Rhodian defence and capitulation.",
        ["wave8_hospitallers_cambridge_crusades_chronology", "wave8_hospitallers_cambridge_rhodes_bastion"],
    ),
    _entity(
        _TRIPOLI_OTTOMAN,
        "Sinan Pasha's Ottoman force at Tripoli (1551)",
        "event_bounded_ottoman_siege_force",
        1551,
        "Tripoli, Libya",
        "Bounded to Sinan Pasha's Ottoman component in the August siege.",
        ["wave8_hospitallers_cambridge_tripoli_1551", "wave8_hospitallers_phillips_tripoli_1551"],
    ),
    _entity(
        _TRIPOLI_CORSAIR,
        "Turgut Reis's corsair force at Tripoli (1551)",
        "event_bounded_corsair_siege_force",
        1551,
        "Tripoli, Libya",
        "Bounded to Dragut/Turgut Reis's separately attested corsair component.",
        ["wave8_hospitallers_cambridge_tripoli_1551", "wave8_hospitallers_phillips_tripoli_1551"],
    ),
    _entity(
        _TRIPOLI_HOSPITALLER,
        "Hospitaller garrison of Tripoli (1551)",
        "event_bounded_hospitaller_outpost_garrison",
        1551,
        "Tripoli, Libya",
        "Bounded to the Order's Tripoli garrison from Malta that surrendered in 1551.",
        ["wave8_hospitallers_cambridge_tripoli_1551", "wave8_hospitallers_phillips_tripoli_1551"],
    ),
    _entity(
        _MALTA_FRENCH,
        "French Army of the Orient invasion force at Malta (1798)",
        "event_bounded_french_revolutionary_invasion_force",
        1798,
        "Malta",
        "Bounded to Bonaparte's June landings and acquisition of the islands.",
        ["wave8_hospitallers_cambridge_malta_1798", "wave8_hospitallers_heritage_malta_invasion"],
    ),
    _entity(
        _MALTA_HOSPITALLER,
        "Hompesch's Hospitaller Malta garrison and order-state forces (1798)",
        "event_bounded_hospitaller_island_garrison",
        1798,
        "Malta",
        "Bounded to the Order-state force that capitulated to the French in June 1798.",
        ["wave8_hospitallers_cambridge_malta_1798", "wave8_hospitallers_cambridge_malta_regimes", "wave8_hospitallers_heritage_malta_invasion"],
    ),
)


WAVE8_HOSPITALLERS_ROW_HASHES: dict[str, str] = {
    "hced-Krak de Chevaliers1271-1": "dd5af88b50f2e77ca54edecc22192d4cff57c72a06fbc1b44656e1b97d298500",
    "hced-Malta1798-1": "a2893a1d0219e9e3ae225ad762ed7923a317099e345bb0431dcd5cbdc1dbebc5",
    "hced-Marqab1285-1": "c8ab636dac864da42af7b87062844084bf0cfcf3a5e69de5746f6bdd2761a9a9",
    "hced-Rhodes1310-1": "281157c31631afd47e9baaf646e35fa694095c95049c43f3392c248a4b25c975",
    "hced-Rhodes1480-1": "ac9bfc57cbe980c2778e94a2fa216e8d83b16b930696602f442914021eed84d5",
    "hced-Rhodes1522-1": "46dc5fadffea1de0d8a25a03e0e327c21aa86bc7504880371548d77cf02e8619",
    "hced-Smyrna1402-1": "523f2f207f249861f8fa258fa5bde879402fce7d026b3d859d7924cee868f24d",
    "hced-Tripoli, Libya1551-1": "6b73a93fb5f3dda665544c343f5a03ad70ffdc640e50acd7ca52b7cb85f2ed06",
}

WAVE8_HOSPITALLERS_EXACT_CANDIDATE_ID_SHA256 = (
    "d4213bb30ec9e042c6d482fda78803462c0c131ffea482e204304c858961f46d"
)
WAVE8_HOSPITALLERS_EXACT_LABEL_FUNNEL_DIGESTS = {
    "knights hospitallier": "22745e39bf11454907bd3597ad27614fb314feb919e26e24eb6b8f2f4898f348",
    "knights of st john": "72e41e7b5b66a93b541564d21574c3b2eaea5e0405f3dbda5d429c1f1a32bb35",
}


_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_HOSPITALLERS_SOURCES
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str,
    granularity: str,
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
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    war_type: str,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_HOSPITALLERS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
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


WAVE8_HOSPITALLERS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Krak de Chevaliers1271-1": _contract(
        "hced-Krak de Chevaliers1271-1",
        _canonical(
            "Siege and capture of Krak des Chevaliers",
            1271,
            "March-8 April 1271",
            date_precision="month_to_day_range",
            granularity="siege",
        ),
        "final_levantine_hospitaller_castles",
        [_KRAK_MAMLUK],
        [_KRAK_HOSPITALLER],
        ["wave8_hospitallers_cambridge_krak_1271", "wave8_hospitallers_unesco_krak"],
        ["wave8_hospitallers_cambridge_krak_1271", "wave8_hospitallers_unesco_krak"],
        "Baybars's Mamluk army captured the Hospitaller fortress after a siege ending on 8 April. The contract rates that castle result only, not all Mamluk-Crusader operations.",
        confidence=0.98,
        war_type="interstate_religious",
    ),
    "hced-Marqab1285-1": _contract(
        "hced-Marqab1285-1",
        _canonical(
            "Siege of Margat (Marqab)",
            1285,
            "17 April-25 May 1285",
            date_precision="day_range",
            granularity="siege",
        ),
        "final_levantine_hospitaller_castles",
        [_MARGAT_MAMLUK],
        [_MARGAT_HOSPITALLER],
        ["wave8_hospitallers_edinburgh_margat", "wave8_hospitallers_michaudel_margat"],
        ["wave8_hospitallers_edinburgh_margat", "wave8_hospitallers_michaudel_margat"],
        "Qalawun's siege ended with the Hospitaller garrison's surrender on 25 May. Marqab and Margat are treated as one castle event, not two labels or two outcomes.",
        confidence=0.98,
        war_type="interstate_religious",
    ),
    "hced-Rhodes1310-1": _contract(
        "hced-Rhodes1310-1",
        _canonical(
            "Completion of the Hospitaller conquest of Rhodes",
            1310,
            "final phase conventionally completed in mid-August 1310",
            date_precision="year_with_disputed_completion_chronology",
            granularity="campaign_completion",
        ),
        "hospitaller_acquisition_of_rhodes",
        [_RHODES_1310_HOSPITALLER],
        [_RHODES_1310_BYZANTINE],
        [
            "wave8_hospitallers_cnrs_rhodes_arrival",
            "wave8_hospitallers_ehr_rhodes_town",
            "wave8_hospitallers_pur_rhodes_conquest",
        ],
        ["wave8_hospitallers_cnrs_rhodes_arrival", "wave8_hospitallers_pur_rhodes_conquest"],
        "The row is the completion of a conquest begun in 1306, not an invented single-day battle. Scholarly dates for the town's surrender vary between 1309 and 1310; the locked 1310 convention is retained at reduced confidence and never generalized into a timeless Hospitaller-Byzantine result.",
        confidence=0.74,
        war_type="territorial_conquest",
    ),
    "hced-Smyrna1402-1": _contract(
        "hced-Smyrna1402-1",
        _canonical(
            "Siege of the Hospitaller sea-castle at Smyrna",
            1402,
            "December 1402",
            date_precision="month",
            granularity="siege",
        ),
        "rhodian_hospitaller_outposts",
        [_SMYRNA_TIMURID],
        [_SMYRNA_HOSPITALLER],
        ["wave8_hospitallers_fleet_smyrna", "wave8_hospitallers_luttrell_smyrna", "wave8_hospitallers_nhrf_smyrna"],
        ["wave8_hospitallers_fleet_smyrna", "wave8_hospitallers_luttrell_smyrna", "wave8_hospitallers_nhrf_smyrna"],
        "Timur's army took and destroyed the Order-administered lower Smyrna sea-castle after the December siege. The massacre reported after capture is not emitted as a second military result.",
        confidence=0.97,
        war_type="interstate_religious",
    ),
    "hced-Rhodes1480-1": _contract(
        "hced-Rhodes1480-1",
        _canonical(
            "Siege of Rhodes (1480)",
            1480,
            "May-August 1480",
            date_precision="month_range",
            granularity="siege",
        ),
        "ottoman_hospitaller_rhodes_wars",
        [_RHODES_1480_HOSPITALLER],
        [_RHODES_1480_OTTOMAN],
        ["wave8_hospitallers_cambridge_ottoman_expansion", "wave8_hospitallers_cambridge_rhodes_bastion"],
        ["wave8_hospitallers_cambridge_ottoman_expansion", "wave8_hospitallers_cambridge_rhodes_bastion"],
        "The Order and Rhodian defenders repelled the 1480 Ottoman expedition. This defensive success is distinct from the Ottoman conquest and capitulation of 1522.",
        confidence=0.97,
        war_type="interstate_religious",
    ),
    "hced-Rhodes1522-1": _contract(
        "hced-Rhodes1522-1",
        _canonical(
            "Siege of Rhodes (1522)",
            1522,
            "1522; capitulation 20 December",
            date_precision="year_with_day_termination",
            granularity="siege",
        ),
        "ottoman_hospitaller_rhodes_wars",
        [_RHODES_1522_OTTOMAN],
        [_RHODES_1522_HOSPITALLER],
        ["wave8_hospitallers_cambridge_crusades_chronology", "wave8_hospitallers_cambridge_rhodes_bastion"],
        ["wave8_hospitallers_cambridge_crusades_chronology", "wave8_hospitallers_cambridge_rhodes_bastion"],
        "Suleiman's siege ended in the Order's 20 December capitulation and January 1523 departure. The event does not inherit the earlier 1480 defenders' rating.",
        confidence=0.99,
        war_type="interstate_religious",
    ),
    "hced-Tripoli, Libya1551-1": _contract(
        "hced-Tripoli, Libya1551-1",
        _canonical(
            "Siege and surrender of Tripoli (1551)",
            1551,
            "August 1551",
            date_precision="month",
            granularity="siege",
        ),
        "ottoman_hospitaller_tripoli_wars",
        [_TRIPOLI_OTTOMAN, _TRIPOLI_CORSAIR],
        [_TRIPOLI_HOSPITALLER],
        ["wave8_hospitallers_cambridge_tripoli_1551", "wave8_hospitallers_phillips_tripoli_1551"],
        ["wave8_hospitallers_cambridge_tripoli_1551", "wave8_hospitallers_phillips_tripoli_1551"],
        "The raw 'Turkey, Corsairs' coalition is preserved as Sinan Pasha's Ottoman force plus Turgut Reis's corsair component; the Order's Tripoli garrison surrendered. Neither component is collapsed into a generic modern Turkey or Libya.",
        confidence=0.96,
        war_type="interstate_religious",
    ),
    "hced-Malta1798-1": _contract(
        "hced-Malta1798-1",
        _canonical(
            "French invasion and Hospitaller capitulation of Malta",
            1798,
            "June 1798; French control established 12 June",
            date_precision="month_with_day_termination",
            granularity="invasion_and_capitulation",
        ),
        "french_invasion_of_hospitaller_malta",
        [_MALTA_FRENCH],
        [_MALTA_HOSPITALLER],
        ["wave8_hospitallers_cambridge_malta_1798", "wave8_hospitallers_cambridge_malta_regimes", "wave8_hospitallers_heritage_malta_invasion"],
        ["wave8_hospitallers_cambridge_malta_1798", "wave8_hospitallers_heritage_malta_invasion"],
        "Bonaparte's Army of the Orient took the islands and the independently recognized Hospitaller order-state capitulated. The result is the bounded 1798 invasion, not the later Maltese uprising or blockade.",
        confidence=0.98,
        war_type="interstate_revolutionary",
    ),
}


WAVE8_HOSPITALLERS_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_HOSPITALLERS_EXCLUSIONS = WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS
WAVE8_HOSPITALLERS_NONPROMOTIONS: dict[str, dict[str, Any]] = {}

WAVE8_HOSPITALLERS_CONTRACT_IDS = frozenset(WAVE8_HOSPITALLERS_CONTRACTS)
WAVE8_HOSPITALLERS_HOLD_IDS = frozenset(WAVE8_HOSPITALLERS_HOLDS)
WAVE8_HOSPITALLERS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS
)
WAVE8_HOSPITALLERS_EXCLUSION_IDS = WAVE8_HOSPITALLERS_TERMINAL_EXCLUSION_IDS
WAVE8_HOSPITALLERS_RESERVED_IDS = frozenset(
    WAVE8_HOSPITALLERS_CONTRACT_IDS
    | WAVE8_HOSPITALLERS_HOLD_IDS
    | WAVE8_HOSPITALLERS_TERMINAL_EXCLUSION_IDS
)
WAVE8_HOSPITALLERS_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_HOSPITALLERS_ROW_HASHES
)


WAVE8_HOSPITALLERS_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_HOSPITALLERS_CONTRACT_IDS
)
WAVE8_HOSPITALLERS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_HOSPITALLERS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_HOSPITALLERS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_HOSPITALLERS_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_HOSPITALLERS_LOCATION_QUARANTINE_REASONS = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "HCED supplies a castle, city, or island centroid rather than a "
            "source-audited footprint for the multi-day siege, campaign phase, "
            "or invasion; retain the reviewed modern country only."
        ),
    }
    for candidate_id in sorted(WAVE8_HOSPITALLERS_CONTRACT_IDS)
}


WAVE8_HOSPITALLERS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_HOSPITALLERS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_HOSPITALLERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}


WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Acre1291-1": {
        "raw_row_sha256": "6a2d152a9d39544a5b83f87eb64ed7929f65a1ba0e4c8a61e9e32980a2f8b989",
        "disposition": "adjacent_multi_order_coalition_outside_exact_lane",
        "relationship": "contains_source_misspelling_inside_four_member_coalition",
        "reason": "Acre combines Jerusalem, Hospitallers, Templars, and Teutonic Knights; this exact-label lane cannot silently collapse that coalition into one Hospitaller actor.",
    },
    "hced-Arsouf1191-1": {
        "raw_row_sha256": "6dac2eea873a203820c14f28ae4064550f67666316b8114a072c19fe25a3fc91",
        "disposition": "existing_coded_release_owner",
        "relationship": "hospitaller_name_inside_england_coalition",
        "owner_event_id": "hced_hced_arsouf1191_1",
        "reason": "The coded pass already owns the row as England versus the Ayyubids; this lane does not re-rate or append a second Hospitaller outcome.",
    },
    "hced-Cresson1187-1": {
        "raw_row_sha256": "f153d030c9e77de82a92d5405b5ee71bcad21287dcf82265cd9c9fd417645e14",
        "disposition": "adjacent_multi_order_coalition_outside_exact_lane",
        "relationship": "templar_hospitaller_joint_side",
        "reason": "Cresson is a Templar-Hospitaller coalition and requires its own joint-force identity audit; neither order is substituted for the whole side here.",
    },
    "hced-Malta1565-1": {
        "raw_row_sha256": "364eef3dd82e293d73606dff98f3be322e2418b0da697129f326d80abaaa9afd",
        "disposition": "existing_coded_release_owner",
        "relationship": "hospitaller_spain_coalition_variant",
        "owner_event_id": "hced_hced_malta1565_1",
        "reason": "The coded pass already owns the Great Siege row through Spain and the Ottoman Empire; the 1798 exact-label event is chronologically and operationally distinct.",
    },
    "hced-Smyrna1344-1": {
        "raw_row_sha256": "9ba48bc02ff693315bef98a48e662463774bdca1215f1de69a772631a2ef7fe0",
        "disposition": "adjacent_four_power_coalition_outside_exact_lane",
        "relationship": "venice_cyprus_papal_hospitaller_coalition",
        "reason": "The 1344 capture belongs to a four-power league and cannot be assigned solely to the Order; it is also distinct from Timur's 1402 capture of the Hospitaller sea-castle.",
    },
}
WAVE8_HOSPITALLERS_ADJACENT_LANE_DISPOSITIONS = (
    WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS
)
WAVE8_HOSPITALLERS_ADJACENT_CANDIDATE_IDS = frozenset(
    WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS
)
WAVE8_HOSPITALLERS_CROSS_LANE_DISPOSITIONS = (
    WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS
)
WAVE8_HOSPITALLERS_INTEGRATION_DISPOSITIONS = {
    **WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS,
    **WAVE8_HOSPITALLERS_IWBD_DUPLICATE_DISPOSITIONS,
    **WAVE8_HOSPITALLERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
}


WAVE8_HOSPITALLERS_CROSS_SPELLING_DUPLICATE_AUDIT = {
    "exact_source_labels": ["Knights Hospitallier", "Knights of St John"],
    "same_event_candidate_pairs": [],
    "finding": "no_same_name_and_year_pair_across_exact_spellings",
    "method": "candidate id, normalized place name, locked year, canonical event, and adjacent coalition inventory",
}
WAVE8_HOSPITALLERS_OPPOSITE_RESULT_AUDIT = {
    "same_event_opposite_result_pairs": [],
    "finding": "no_opposite_result_twin_in_hced_iwbd_or_release_snapshot",
}


def _duplicate_audit(low: int, high: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": sorted({normalize_label(alias) for alias in aliases}),
        "years": list(range(low, high + 1)),
    }


WAVE8_HOSPITALLERS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Krak de Chevaliers1271-1": _duplicate_audit(1271, 1271, "Crac des Chevaliers", "Krak de Chevaliers", "Krak des Chevaliers", "Siege of Krak des Chevaliers"),
    "hced-Marqab1285-1": _duplicate_audit(1285, 1285, "Margat", "Marqab", "Siege of Margat", "Siege of Marqab"),
    "hced-Rhodes1310-1": _duplicate_audit(1310, 1310, "Conquest of Rhodes", "Hospitaller conquest of Rhodes", "Rhodes"),
    "hced-Rhodes1480-1": _duplicate_audit(1480, 1480, "Rhodes", "Siege of Rhodes", "Siege of Rhodes 1480"),
    "hced-Rhodes1522-1": _duplicate_audit(1522, 1522, "Rhodes", "Siege of Rhodes", "Siege of Rhodes 1522"),
    "hced-Smyrna1402-1": _duplicate_audit(1402, 1402, "Smyrna", "Siege of Smyrna", "Smyrna sea-castle"),
    "hced-Tripoli, Libya1551-1": _duplicate_audit(1551, 1551, "Siege of Tripoli", "Tripoli", "Tripoli, Libya"),
    "hced-Malta1798-1": _duplicate_audit(1798, 1798, "French invasion of Malta", "Invasion of Malta", "Malta"),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_lane_dispositions": WAVE8_HOSPITALLERS_ADJACENT_LANE_DISPOSITIONS,
        "contracts": WAVE8_HOSPITALLERS_CONTRACTS,
        "country_quarantine_additions": sorted(WAVE8_HOSPITALLERS_COUNTRY_QUARANTINE_ADDITIONS),
        "cross_lane_dispositions": WAVE8_HOSPITALLERS_CROSS_LANE_DISPOSITIONS,
        "cross_spelling_duplicate_audit": WAVE8_HOSPITALLERS_CROSS_SPELLING_DUPLICATE_AUDIT,
        "entities": WAVE8_HOSPITALLERS_ENTITIES,
        "exact_candidate_id_sha256": WAVE8_HOSPITALLERS_EXACT_CANDIDATE_ID_SHA256,
        "exact_label_funnel_digests": WAVE8_HOSPITALLERS_EXACT_LABEL_FUNNEL_DIGESTS,
        "existing_release_duplicate_dispositions": WAVE8_HOSPITALLERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
        "expected_candidate_ids": sorted(WAVE8_HOSPITALLERS_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_HOSPITALLERS_HOLDS,
        "integration_dispositions": WAVE8_HOSPITALLERS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_HOSPITALLERS_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_HOSPITALLERS_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_HOSPITALLERS_LOCATION_QUARANTINE_REASONS,
        "opposite_result_audit": WAVE8_HOSPITALLERS_OPPOSITE_RESULT_AUDIT,
        "outcome_overrides": WAVE8_HOSPITALLERS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(WAVE8_HOSPITALLERS_POINT_QUARANTINE_ADDITIONS),
        "row_hashes": WAVE8_HOSPITALLERS_ROW_HASHES,
        "sources": WAVE8_HOSPITALLERS_SOURCES,
        "terminal_exclusions": WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS,
    }


def wave8_hospitallers_audit_signature() -> str:
    """Return the immutable digest of both spellings and their shared audit."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_HOSPITALLERS_FINAL_AUDIT_SIGNATURE = (
    "7c3ccc7cfb4c99369f3bf8b292146eb3a3210fc133fa206db7cefdd3e3078c42"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_HOSPITALLERS_CONTRACTS),
        len(WAVE8_HOSPITALLERS_HOLDS),
        len(WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS),
    ) != (8, 0, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_HOSPITALLERS_ENTITIES), len(WAVE8_HOSPITALLERS_SOURCES)) != (
        17,
        18,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_HOSPITALLERS_RESERVED_IDS != WAVE8_HOSPITALLERS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    if WAVE8_HOSPITALLERS_EXCLUSIONS is not WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion alias diverged")
    dispositions = (
        WAVE8_HOSPITALLERS_CONTRACT_IDS,
        WAVE8_HOSPITALLERS_HOLD_IDS,
        WAVE8_HOSPITALLERS_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(len(dispositions))
        for j in range(i + 1, len(dispositions))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    expected_digest = hashlib.sha256(
        "".join(
            f"{candidate_id}\n"
            for candidate_id in sorted(WAVE8_HOSPITALLERS_RESERVED_IDS)
        ).encode("utf-8")
    ).hexdigest()
    if expected_digest != WAVE8_HOSPITALLERS_EXACT_CANDIDATE_ID_SHA256:
        raise ValueError(f"{_LANE_NAME} exact candidate digest changed")
    if wave8_hospitallers_audit_signature() != WAVE8_HOSPITALLERS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_HOSPITALLERS_SOURCES
    }
    if len(source_by_id) != len(WAVE8_HOSPITALLERS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    source_families = {
        str(source["source_family_id"]) for source in WAVE8_HOSPITALLERS_SOURCES
    }
    if len(source_families) != len(WAVE8_HOSPITALLERS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source families are not independent")
    for source in WAVE8_HOSPITALLERS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_HOSPITALLERS_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_HOSPITALLERS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden = {
        "byzantium",
        "france",
        "knights hospitallier",
        "knights hospitaller",
        "knights of st john",
        "mamluk sultanate",
        "malta",
        "ottoman empire",
        "timurid empire",
        "turkey",
    }
    for entity in WAVE8_HOSPITALLERS_ENTITIES:
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity is not event bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if not str(entity["kind"]).startswith("event_bounded_"):
            raise ValueError(f"{_LANE_NAME} entity kind is not event bounded")
        if normalize_label(entity["name"]) in forbidden:
            raise ValueError(f"{_LANE_NAME} installed a generic actor")
        note = str(entity["continuity_note"]).casefold()
        if "no rating is inherited" not in note or "modern state" not in note:
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        refs = list(map(str, entity["source_ids"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity sources drifted")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    raw_name_years: set[tuple[int, str]] = set()
    for candidate_id, contract in WAVE8_HOSPITALLERS_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_HOSPITALLERS_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        canonical = contract["canonical_event"]
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        expected_key = f"{_slug(str(canonical['name']))}:{low}:{high}"
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if low != high:
            raise ValueError(f"{_LANE_NAME} widened a locked HCED year")
        if not canonical["granularity"]:
            raise ValueError(f"{_LANE_NAME} omitted reviewed granularity")
        key = (low, normalize_label(canonical["name"]))
        if key in raw_name_years:
            raise ValueError(f"{_LANE_NAME} cross-spelling event duplicate")
        raw_name_years.add(key)

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} invalid opposing sides")
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} actor sides are not canonical")
        if not set(side_1 + side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} contract uses an unbounded actor")
        if any(
            int(entity_by_id[entity_id]["start_year"]) != low
            or int(entity_by_id[entity_id]["end_year"]) != high
            for entity_id in (*side_1, *side_2)
        ):
            raise ValueError(f"{_LANE_NAME} actor window crossed an event")
        used_entities.update(side_1 + side_2)

        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        if contract["actor_override"] != "event_bounded_exact_forces":
            raise ValueError(f"{_LANE_NAME} actor resolution is not explicit")
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
        if (
            len(outcomes) < 2
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        expected_families = sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} event-bounded entities are not exactly consumed")
    for entity in WAVE8_HOSPITALLERS_ENTITIES:
        used_sources.update(map(str, entity["source_ids"]))
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if WAVE8_HOSPITALLERS_POINT_QUARANTINE_ADDITIONS != WAVE8_HOSPITALLERS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_HOSPITALLERS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_HOSPITALLERS_LOCATION_QUARANTINE_REASONS) != WAVE8_HOSPITALLERS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reasons are incomplete")
    if (
        WAVE8_HOSPITALLERS_OUTCOME_OVERRIDES
        or WAVE8_HOSPITALLERS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_HOSPITALLERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} zero disposition inventory changed")
    if WAVE8_HOSPITALLERS_ADJACENT_LANE_DISPOSITIONS is not WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} adjacent disposition alias diverged")
    if WAVE8_HOSPITALLERS_CROSS_LANE_DISPOSITIONS is not WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} cross-lane disposition alias diverged")
    if len(WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS) != 5:
        raise ValueError(f"{_LANE_NAME} adjacent variant inventory changed")
    if set(WAVE8_HOSPITALLERS_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_HOSPITALLERS_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    if WAVE8_HOSPITALLERS_CROSS_SPELLING_DUPLICATE_AUDIT[
        "same_event_candidate_pairs"
    ]:
        raise ValueError(f"{_LANE_NAME} has an unresolved cross-spelling duplicate")
    if WAVE8_HOSPITALLERS_OPPOSITE_RESULT_AUDIT[
        "same_event_opposite_result_pairs"
    ]:
        raise ValueError(f"{_LANE_NAME} has an unresolved opposite result")


def _is_hospitaller_variant(value: Any) -> bool:
    text = str(value or "").casefold()
    return "hospitallier" in text or "knights of st john" in text


def validate_wave8_hospitallers_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate both exact spellings and all adjacent variants fail-closed."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_HOSPITALLERS_CONTRACTS,
        WAVE8_HOSPITALLERS_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row["candidate_id"])
        for row in hced_rows
        if row.get("side_1_raw") in _EXACT_RAW_LABELS
        or row.get("side_2_raw") in _EXACT_RAW_LABELS
    }
    if exact_ids != WAVE8_HOSPITALLERS_RESERVED_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact-label inventory drifted: "
            f"{sorted(exact_ids ^ WAVE8_HOSPITALLERS_RESERVED_IDS)}"
        )

    adjacent_rows = {
        str(row["candidate_id"]): row
        for row in hced_rows
        if str(row.get("candidate_id") or "") not in WAVE8_HOSPITALLERS_RESERVED_IDS
        and (
            _is_hospitaller_variant(row.get("side_1_raw"))
            or _is_hospitaller_variant(row.get("side_2_raw"))
        )
    }
    if set(adjacent_rows) != WAVE8_HOSPITALLERS_ADJACENT_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} adjacent variant inventory drifted: "
            f"{sorted(set(adjacent_rows) ^ WAVE8_HOSPITALLERS_ADJACENT_CANDIDATE_IDS)}"
        )
    for candidate_id, disposition in WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS.items():
        actual = canonical_hced_row_sha256(adjacent_rows[candidate_id])
        if actual != disposition["raw_row_sha256"]:
            raise ValueError(
                f"{_LANE_NAME} adjacent row fingerprint changed for {candidate_id}"
            )

    return {
        "adjacent_hced_rows": len(adjacent_rows),
        "holds": len(WAVE8_HOSPITALLERS_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS),
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


def _audited_name_year_pairs() -> set[tuple[int, str]]:
    return {
        (int(year), normalize_label(alias))
        for item in WAVE8_HOSPITALLERS_IWBD_ZERO_OVERLAP_AUDIT.values()
        for year in item["years"]
        for alias in item["aliases"]
    }


def validate_wave8_hospitallers_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Verify adjacent owners, zero twins, and all-or-none lane integration."""

    validate_wave8_hospitallers_queue_contracts(hced_rows)
    audited = _audited_name_year_pairs()
    events = list(existing_events)

    event_by_candidate = {
        str(event["hced_candidate_id"]): event
        for event in events
        if event.get("hced_candidate_id") is not None
    }
    lane_overlap = WAVE8_HOSPITALLERS_CONTRACT_IDS & set(event_by_candidate)
    if len(lane_overlap) not in {0, len(WAVE8_HOSPITALLERS_CONTRACT_IDS)}:
        raise ValueError(
            f"{_LANE_NAME} partial release integration: {sorted(lane_overlap)}"
        )
    for candidate_id in lane_overlap:
        event = event_by_candidate[candidate_id]
        if not str(event.get("id", "")).startswith(_EVENT_ID_PREFIX):
            raise ValueError(f"{_LANE_NAME} release owner ID drifted for {candidate_id}")

    if events:
        for candidate_id, disposition in WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS.items():
            owner_event_id = disposition.get("owner_event_id")
            if not owner_event_id:
                if candidate_id in event_by_candidate:
                    raise ValueError(
                        f"{_LANE_NAME} adjacent coalition unexpectedly entered release: {candidate_id}"
                    )
                continue
            owner = event_by_candidate.get(candidate_id)
            if owner is None or str(owner.get("id")) != owner_event_id:
                raise ValueError(
                    f"{_LANE_NAME} adjacent release owner drifted for {candidate_id}"
                )

    hced_collisions: list[str] = []
    allowed_hced_ids = (
        WAVE8_HOSPITALLERS_RESERVED_IDS
        | WAVE8_HOSPITALLERS_ADJACENT_CANDIDATE_IDS
    )
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id") or "")
        if candidate_id in allowed_hced_ids:
            continue
        year = _year(row.get("year_best"))
        name = normalize_label(row.get("name"))
        if year is not None and (year, name) in audited:
            hced_collisions.append(candidate_id or "<missing-id>")
    if hced_collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): "
            f"{sorted(hced_collisions)}"
        )

    iwbd_collisions: list[str] = []
    for row in iwbd_rows:
        year = _iwbd_year(row)
        name = normalize_label(row.get("name"))
        if year is not None and (year, name) in audited:
            iwbd_collisions.append(str(row.get("candidate_id") or "<missing-id>"))
    if iwbd_collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD duplicate(s): "
            f"{sorted(iwbd_collisions)}"
        )

    allowed_release_ids = {
        str(item.get("owner_event_id"))
        for item in WAVE8_HOSPITALLERS_RELATED_HCED_DISPOSITIONS.values()
        if item.get("owner_event_id")
    }
    release_collisions: list[str] = []
    for event in events:
        event_id = str(event.get("id") or "")
        candidate_id = str(event.get("hced_candidate_id") or "")
        if candidate_id in WAVE8_HOSPITALLERS_CONTRACT_IDS:
            continue
        if event_id in allowed_release_ids:
            continue
        year = _year(event.get("year"))
        aliases = {
            normalize_label(event.get("name")),
            *map(normalize_label, event.get("aliases", [])),
        }
        if year is not None and any((year, alias) in audited for alias in aliases):
            release_collisions.append(event_id or "<missing-id>")
    if release_collisions:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): "
            f"{sorted(release_collisions)}"
        )

    return {
        "adjacent_existing_release_owners": 2,
        "cross_lane_hced_dispositions": len(WAVE8_HOSPITALLERS_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": 0,
        "integration_dispositions": len(WAVE8_HOSPITALLERS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "release_lane_overlap": len(lane_overlap),
    }


def install_wave8_hospitallers_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_HOSPITALLERS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_hospitallers_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_HOSPITALLERS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_HOSPITALLERS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_HOSPITALLERS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_hospitallers_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_hospitallers_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_HOSPITALLERS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_hospitallers_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_HOSPITALLERS_CONTRACTS.values(),
                    *WAVE8_HOSPITALLERS_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_hospitallers_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_existing_release_owners": 2,
        "adjacent_hced_rows": len(WAVE8_HOSPITALLERS_ADJACENT_CANDIDATE_IDS),
        "country_quarantine_additions": len(WAVE8_HOSPITALLERS_COUNTRY_QUARANTINE_ADDITIONS),
        "cross_lane_hced_dispositions": len(WAVE8_HOSPITALLERS_CROSS_LANE_DISPOSITIONS),
        "existing_release_duplicate_dispositions": len(WAVE8_HOSPITALLERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS),
        "holds": len(WAVE8_HOSPITALLERS_HOLDS),
        "integration_dispositions": len(WAVE8_HOSPITALLERS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(WAVE8_HOSPITALLERS_IWBD_DUPLICATE_DISPOSITIONS),
        "iwbd_zero_overlap_candidates": len(WAVE8_HOSPITALLERS_IWBD_ZERO_OVERLAP_AUDIT),
        "new_entities": len(WAVE8_HOSPITALLERS_ENTITIES),
        "new_sources": len(WAVE8_HOSPITALLERS_SOURCES),
        "newly_rated_events": len(WAVE8_HOSPITALLERS_CONTRACTS),
        "outcome_overrides": len(WAVE8_HOSPITALLERS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(WAVE8_HOSPITALLERS_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_HOSPITALLERS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_HOSPITALLERS_RESERVED_IDS),
        "terminal_exclusions": len(WAVE8_HOSPITALLERS_TERMINAL_EXCLUSIONS),
    }


def wave8_hospitallers_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_HOSPITALLERS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_HOSPITALLERS_POINT_QUARANTINE_ADDITIONS,
    }
