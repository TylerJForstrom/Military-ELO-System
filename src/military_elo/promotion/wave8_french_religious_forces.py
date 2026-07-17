"""Coordinated Wave 8 audit for two exact HCED French religious labels.

``French Protestants`` and ``French Catholics`` overlap on eleven source rows,
so they are deliberately adjudicated in one candidate-keyed lane.  The labels
are confessional descriptions, not durable military entities.  Every promoted
side is therefore an event-bounded army, fleet, garrison, detachment, or civic
defence force tied to a named action and year.  No rating passes to a religion,
population, crown, dynasty, generic Huguenot/Catholic actor, or later force.

Sixteen independently supported tactical outcomes are promoted.  Five rows
remain unknown because the source row conflates dates, formations, or result
granularity; unknown is never converted to a draw.  Vassy is terminally
excluded because the row itself records a civilian-congregation massacre, not
a competitive military result.  All twenty-two raw rows, the eleven cross-
label twins, adjacent spellings, same-name events, duplicate surfaces, and
local location quarantines are pinned below.
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
    "WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_EVENT_BOUNDARIES",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_LABEL_DISPOSITIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_DIGESTS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_EXCLUSION_IDS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_EXCLUSIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_BOUNDARIES",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_FINAL_AUDIT_SIGNATURE",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_FUNNEL_AUDIT",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_QUEUE_SHA256",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_HOLD_IDS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_INTEGRATION_DISPOSITIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_QUEUE_SHA256",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_QUARANTINE_REASONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_REVIEWS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_NONPROMOTIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_OUTCOME_OVERRIDES",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_RESERVED_IDS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_DISPOSITIONS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_HASHES",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSION_IDS",
    "WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS",
    "install_wave8_french_religious_forces_entities",
    "install_wave8_french_religious_forces_sources",
    "promote_wave8_french_religious_forces_contracts",
    "validate_wave8_french_religious_forces_funnel",
    "validate_wave8_french_religious_forces_integration_dispositions",
    "validate_wave8_french_religious_forces_queue_contracts",
    "wave8_french_religious_forces_audit_signature",
    "wave8_french_religious_forces_cohort_counts",
    "wave8_french_religious_forces_counts",
    "wave8_french_religious_forces_location_quarantine_additions",
    "wave8_french_religious_forces_metadata",
    "wave8_french_religious_forces_row_dispositions",
)


_LANE_NAME = "Wave 8 exact French Protestant/Catholic forces audit"
_MODULE_OWNER = "military_elo.promotion.wave8_french_religious_forces"
_EVENT_ID_PREFIX = "hced_wave8_french_religious_forces_"
_EXACT_LABELS = frozenset({"french catholics", "french protestants"})


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
        roles.extend(("outcome", "outcome_consistency_crosscheck"))
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(roles)),
    }


WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_french_religious_wood_kings_army",
        "The King's Army: Warfare, Soldiers and Society during the Wars of Religion in France, 1562-1576",
        "https://www.cambridge.org/core/books/kings-army/716F6506ECD0412E1AAAB3E63A6CE011",
        "Cambridge University Press",
        "scholarly_military_history_monograph",
        "james_wood_kings_army",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_musee_eight_wars",
        "The eight wars of religion (1562-1598)",
        "https://museeprotestant.org/notice/les-huit-guerres-de-religion-1562-1598/",
        "Musée protestant",
        "institutional_historical_synthesis",
        "musee_protestant",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_thompson_wars",
        "The Wars of Religion in France, 1559-1576",
        "https://www.loc.gov/item/09014063/",
        "University of Chicago Press; Library of Congress catalog",
        "scholarly_history_monograph",
        "james_westfall_thompson_french_wars",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_knecht_wars",
        "The French Wars of Religion, 1559-1598",
        "https://www.routledge.com/The-French-Wars-of-Religion-1559-1598/Knecht/p/book/9781138418301",
        "Routledge",
        "scholarly_history_monograph",
        "robert_knecht_french_wars",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_musee_armee_guise",
        "Henri de Guise",
        "https://www.musee-armee.fr/au-programme/expositions/haine-des-clans-personnages/henri-de-guise.html",
        "Musée de l'Armée",
        "national_museum_historical_reference",
        "musee_armee_henri_de_guise",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_musee_conde_coutras",
        "Bataille de Coutras, 20 octobre 1587",
        "https://www.musee-conde.fr/fr/notice/est-h-71-bataille-de-coutras-20-octobre-1587-0802df74-374f-4c61-affc-c6c84797e399",
        "Musée Condé",
        "museum_collection_historical_record",
        "musee_conde_coutras",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_bryson_queen_jeanne",
        "Queen Jeanne and the Promised Land: Dynasty, Homeland, Religion and Violence in Sixteenth-Century France",
        "https://brill.com/display/title/6641",
        "Brill",
        "scholarly_history_monograph",
        "david_bryson_queen_jeanne",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_tierce_poitiers",
        "Poitiers assiégée en 1569",
        "https://tierce.edel.univ-poitiers.fr/index.php?id=437",
        "Université de Poitiers",
        "peer_reviewed_historical_article",
        "universite_poitiers_siege_1569",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_royal_collection_poitiers",
        "View of the Siege of Poitiers, 1569",
        "https://militarymaps.rct.uk/other-16th-century-conflicts/view-of-the-siege-of-poitiers-1569-poitiers-poitou-charentes-france-46deg3500n-00deg2000e-0",
        "Royal Collection Trust",
        "royal_collection_military_map_record",
        "royal_collection_siege_poitiers",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_bangor_elizabeth_wars",
        "Elizabeth's French Wars, 1562-1598: English intervention in the French Wars of Religion",
        "https://research.bangor.ac.uk/en/studentTheses/elizabeths-french-wars-1562-1598/",
        "Bangor University",
        "doctoral_historical_thesis",
        "bangor_elizabeth_french_wars",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_oxford_orleans",
        "The Assassination of François de Lorraine, Duke of Guise, February 1563",
        "https://academic.oup.com/fh/article-abstract/21/3/247/593198",
        "Oxford University Press, French History",
        "peer_reviewed_historical_article",
        "oxford_french_history_guise_assassination",
    ),
    _source(
        "wave8_french_religious_cambridge_rouen_1591",
        "Queen Elizabeth and the Siege of Rouen, 1591",
        "https://www.cambridge.org/core/journals/transactions-of-the-royal-historical-society/article/abs/queen-elizabeth-and-the-siege-of-rouen-1591/B53F2D7E420C6B6FDD8AFD63170ECF9E",
        "Cambridge University Press; Royal Historical Society",
        "peer_reviewed_historical_article",
        "wernham_elizabeth_rouen_1591",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_bnf_montauban",
        "Siège de Montauban (1621)",
        "https://catalogue.bnf.fr/ark:/12148/cb14423376m",
        "Bibliothèque nationale de France",
        "national_library_authority_record",
        "bnf_siege_montauban_1621",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_musee_last_wars",
        "The last religious wars (1610-1629)",
        "https://museeprotestant.org/en/notice/the-last-religious-wars/",
        "Musée protestant",
        "institutional_historical_synthesis",
        "musee_protestant",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_holt_last_war",
        "Epilogue: The Last War of Religion, 1610-1629",
        "https://www.cambridge.org/core/services/aop-cambridge-core/content/view/A4AF17F3A3C9C0C78BE41CC0F3DBBB72/9780511817922c7_p178-194_CBO.pdf/epilogue_the_last_war_of_religion_16101629.pdf",
        "Cambridge University Press",
        "scholarly_book_chapter",
        "mack_holt_last_war_religion",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_pennington_1625",
        "The ships and seamen of the French Mediterranean fleet in 1625",
        "https://academic.oup.com/histres/article/96/273/318/7143618",
        "Oxford University Press, Historical Research",
        "peer_reviewed_historical_article",
        "oxford_historical_research_french_fleet_1625",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_tolosana_re_1625",
        "Combat naval de l'île de Ré, 1625: digitized source record",
        "https://tolosana.univ-toulouse.fr/fr/notice/24488532x",
        "Université Toulouse Capitole, Tolosana",
        "academic_library_primary_source_record",
        "tolosana_naval_re_1625",
    ),
    _source(
        "wave8_french_religious_culture_paris_1590",
        "Siège de Paris par Henri IV en 1590",
        "https://pop.culture.gouv.fr/notice/joconde/50170005866",
        "Ministère de la Culture, France",
        "national_museum_collection_record",
        "french_ministry_culture_pop",
    ),
    _source(
        "wave8_french_religious_michigan_henry_iv",
        "A Prince-like Soldier and a Soldier-like Prince: Contemporary Views of Henry IV",
        "https://quod.lib.umich.edu/w/wsfh/0642292.0033.004/--princelike-soldier-and-soldierlike-prince-contemporary-views?rgn=main%3Bview%3Dfulltext",
        "University of Michigan Library",
        "scholarly_historical_article",
        "michigan_henry_iv_military_image",
        outcome=True,
    ),
    _source(
        "wave8_french_religious_culture_vassy",
        "Massacre de Vassy, 1er mars 1562",
        "https://pop.culture.gouv.fr/notice/joconde/50170005854",
        "Ministère de la Culture, France",
        "national_museum_collection_record",
        "french_ministry_culture_pop",
    ),
    _source(
        "wave8_french_religious_british_museum_vassy",
        "The massacre at Vassy, 1562",
        "https://www.britishmuseum.org/collection/object/P_1855-0414-189",
        "British Museum",
        "national_museum_collection_record",
        "british_museum_vassy",
    ),
)


_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES
}


WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_QUEUE_SHA256 = (
    "7466f5c9db3cde0d74ee39a4e0c209d9a397457435986a1ace156f9d6aa2aabf"
)
WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_QUEUE_SHA256 = (
    "2ae0b16256c472c62a78f451b0532ff1676e37db35a8a8c6cd2519abe38e5fc7"
)
WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_HASHES: dict[str, str] = {
    "hced-Arnay-le-Duc1570-1": "13cad0aecfea5749e90ef645006a7c1f8f505379d4861891e09dacc45fbc2cbb",
    "hced-Auneau1587-1": "ad83416d7a4b0330ec9f6dcf0e5d9a056cd6431f4f86e3a7f139a59820b0dbb9",
    "hced-Caudebec1592-1": "efae7cf23eb895cf2beb23ab1a623e3bb7cc71837a4b69328ac379244b86cb2b",
    "hced-Coutras1587-1": "30f4251cb53d3e5e3a50ab1e9a6df37f92f0e4b70636b97fbfec6d1e4c320abd",
    "hced-Dormans1575-1": "6625e3af5daf8ae169d81371b5cd9f51f42b3b77096bc47e0c6e896913c5b9c6",
    "hced-Dreux1562-1": "5fb72b9d0c6ce35be86dbcfa3eaa2703e0055b463c4f49ab02a5928d082d4114",
    "hced-Jarnac1569-1": "518856899a604c04272dbb6ce64ef276029c5c8b976c6c1c411fdd18b83f4b12",
    "hced-La Roche-LAbeille1569-1": "e06fc6e708fa5c25a402451a715c221225c1f34ab337f229ba9a35eb81115af4",
    "hced-La Rochelle1572-1": "76216489e2747c83938abacc25018f62e79a6048011fab366c18eb228652e733",
    "hced-La Rochelle1625-1": "438c068b0e68f5418868a84cc57038e3c6a1c830e36cfca669f6f4cc7b66d743",
    "hced-Moncontour1569-1": "ec16b2f2e9d25ced3abf51cce394baac6e53adf8dae600edad464e3110497ae5",
    "hced-Montauban1621-1": "5de093403012133090997dc51f6bf6283c800f88f4e73cf010ea3514c6cd7271",
    "hced-Orleans1563-1": "be505efe254719fb1ce447b70c04792795554e53cdcff5702881b9569ceb4c67",
    "hced-Orthez1569-1": "cd771a92c114310993840d3f8c58cd8c43f36997fe365ae29ed57176e561251a",
    "hced-Paris1590-1": "07e8b3c944f82fc2a5f7fc67c8677741b585920ee238843ffd82e710297dd4c1",
    "hced-Poitiers1569-1": "110f8c121a94f6a6ff9514d3dc597735fbe03d826ffbb96b2aa1f269020ba5cb",
    "hced-Rouen1562-1": "b82a47acce32568db414954bcb4daadd774bc1a6ba53aeb048282cb26fcf3ac0",
    "hced-Rouen1591-1": "cfcc4a7a84e8b7d33e748a396387392a0cdba056a1d70959159da128eed32691",
    "hced-St Denis, France1567-1": "55c075c45c352134fdf91017a43d45aa6f3b214d290982f360c03410ab8c865e",
    "hced-St Jean dAngely1621-1": "2cbeff4bc1938d344f057b80a41086f88aac872e5a7a506b56e41517a3ffca13",
    "hced-Vassy1562-1": "aaa336e4a6665261ce0c6ea07831a6ed5d76141786ddcc3c7af34ad3f1288d94",
    "hced-Vergt1562-1": "2e3725453cec199c1242ca60ce445ad1eee4dc82756c761aeaf11cb7b479ac81",
}


_CATHOLIC_EXACT_IDS = (
    "hced-Arnay-le-Duc1570-1",
    "hced-Auneau1587-1",
    "hced-Caudebec1592-1",
    "hced-Coutras1587-1",
    "hced-Dormans1575-1",
    "hced-Dreux1562-1",
    "hced-Jarnac1569-1",
    "hced-La Roche-LAbeille1569-1",
    "hced-La Rochelle1572-1",
    "hced-Montauban1621-1",
    "hced-Orleans1563-1",
    "hced-Orthez1569-1",
    "hced-Poitiers1569-1",
    "hced-Rouen1562-1",
    "hced-St Denis, France1567-1",
    "hced-Vassy1562-1",
    "hced-Vergt1562-1",
)
_PROTESTANT_EXACT_IDS = (
    "hced-Arnay-le-Duc1570-1",
    "hced-Caudebec1592-1",
    "hced-Coutras1587-1",
    "hced-La Rochelle1572-1",
    "hced-La Rochelle1625-1",
    "hced-Moncontour1569-1",
    "hced-Montauban1621-1",
    "hced-Orleans1563-1",
    "hced-Orthez1569-1",
    "hced-Paris1590-1",
    "hced-Poitiers1569-1",
    "hced-Rouen1591-1",
    "hced-St Denis, France1567-1",
    "hced-St Jean dAngely1621-1",
    "hced-Vassy1562-1",
    "hced-Vergt1562-1",
)
WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES = {
    "french catholics": frozenset(_CATHOLIC_EXACT_IDS),
    "french protestants": frozenset(_PROTESTANT_EXACT_IDS),
}
WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_DIGESTS = {
    "french catholics": "4ce4b7550abeb80060b2e0075b7d2e20b09576d62e922580ab5653752c36d475",
    "french protestants": "1987e8717d053c927e84f35492dd77ffd5db82f079b46ccf4590a4e8c75f606e",
}
WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS = frozenset(
    set(_CATHOLIC_EXACT_IDS) & set(_PROTESTANT_EXACT_IDS)
)
WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS = frozenset(
    set(_CATHOLIC_EXACT_IDS) | set(_PROTESTANT_EXACT_IDS)
)


_EVENT_EVIDENCE: dict[str, tuple[str, ...]] = {
    "hced-Arnay-le-Duc1570-1": (
        "wave8_french_religious_musee_eight_wars",
        "wave8_french_religious_wood_kings_army",
    ),
    "hced-Auneau1587-1": (
        "wave8_french_religious_knecht_wars",
        "wave8_french_religious_musee_armee_guise",
    ),
    "hced-Coutras1587-1": (
        "wave8_french_religious_knecht_wars",
        "wave8_french_religious_musee_conde_coutras",
    ),
    "hced-Dormans1575-1": (
        "wave8_french_religious_knecht_wars",
        "wave8_french_religious_musee_armee_guise",
    ),
    "hced-Dreux1562-1": (
        "wave8_french_religious_thompson_wars",
        "wave8_french_religious_wood_kings_army",
    ),
    "hced-Jarnac1569-1": (
        "wave8_french_religious_musee_eight_wars",
        "wave8_french_religious_wood_kings_army",
    ),
    "hced-La Roche-LAbeille1569-1": (
        "wave8_french_religious_thompson_wars",
        "wave8_french_religious_wood_kings_army",
    ),
    "hced-La Rochelle1625-1": (
        "wave8_french_religious_musee_last_wars",
        "wave8_french_religious_pennington_1625",
        "wave8_french_religious_tolosana_re_1625",
    ),
    "hced-Moncontour1569-1": (
        "wave8_french_religious_musee_eight_wars",
        "wave8_french_religious_wood_kings_army",
    ),
    "hced-Montauban1621-1": (
        "wave8_french_religious_bnf_montauban",
        "wave8_french_religious_musee_last_wars",
    ),
    "hced-Orthez1569-1": (
        "wave8_french_religious_bryson_queen_jeanne",
        "wave8_french_religious_thompson_wars",
    ),
    "hced-Poitiers1569-1": (
        "wave8_french_religious_royal_collection_poitiers",
        "wave8_french_religious_tierce_poitiers",
    ),
    "hced-Rouen1562-1": (
        "wave8_french_religious_bangor_elizabeth_wars",
        "wave8_french_religious_wood_kings_army",
    ),
    "hced-St Denis, France1567-1": (
        "wave8_french_religious_musee_eight_wars",
        "wave8_french_religious_wood_kings_army",
    ),
    "hced-St Jean dAngely1621-1": (
        "wave8_french_religious_holt_last_war",
        "wave8_french_religious_musee_last_wars",
    ),
    "hced-Vergt1562-1": (
        "wave8_french_religious_thompson_wars",
        "wave8_french_religious_wood_kings_army",
    ),
}
_EVENT_OUTCOME_SOURCES: dict[str, tuple[str, ...]] = {
    candidate_id: tuple(
        source_id
        for source_id in evidence
        if "outcome" in _SOURCE_BY_ID[source_id]["evidence_roles"]
    )
    for candidate_id, evidence in _EVENT_EVIDENCE.items()
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    source_ids: Iterable[str],
    scope: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": "France",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            f"{scope} This fighting identity exists only for the named action and "
            f"the year {year}. No rating is inherited by or transferred to the "
            "generic HCED labels French Protestants or French Catholics, a "
            "religion or denomination, a civilian population, the French Crown, "
            "a dynasty, a commander personally, a later formation, or another event."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


# Each tuple is (id, display name, kind).  Side ordering follows the pinned HCED
# row exactly; compound raw sides become one explicitly bounded coalition force.
_ENTITY_SPECS: dict[
    str, tuple[tuple[str, str, str], tuple[str, str, str]]
] = {
    "hced-Arnay-le-Duc1570-1": (
        (
            "coligny_huguenot_field_army_arnay_1570",
            "Coligny's Huguenot field army at Arnay-le-Duc (1570)",
            "event_bounded_huguenot_field_army",
        ),
        (
            "cosse_royal_interception_force_arnay_1570",
            "Cossé's royal interception force at Arnay-le-Duc (1570)",
            "event_bounded_royal_field_force",
        ),
    ),
    "hced-Auneau1587-1": (
        (
            "guise_catholic_league_army_auneau_1587",
            "Guise's Catholic League army at Auneau (1587)",
            "event_bounded_catholic_league_army",
        ),
        (
            "dohna_german_protestant_relief_army_auneau_1587",
            "Dohna's German Protestant relief army at Auneau (1587)",
            "event_bounded_foreign_relief_army",
        ),
    ),
    "hced-Coutras1587-1": (
        (
            "navarre_huguenot_army_coutras_1587",
            "Navarre's Huguenot army at Coutras (1587)",
            "event_bounded_huguenot_field_army",
        ),
        (
            "joyeuse_royal_army_coutras_1587",
            "Joyeuse's royal army at Coutras (1587)",
            "event_bounded_royal_field_army",
        ),
    ),
    "hced-Dormans1575-1": (
        (
            "guise_royal_army_dormans_1575",
            "Guise's royal army at Dormans (1575)",
            "event_bounded_royal_field_army",
        ),
        (
            "thore_german_malcontent_army_dormans_1575",
            "Thoré's German-Protestant and Malcontent army at Dormans (1575)",
            "event_bounded_mixed_relief_army",
        ),
    ),
    "hced-Dreux1562-1": (
        (
            "montmorency_guise_royal_army_dreux_1562",
            "Montmorency-Guise royal army at Dreux (1562)",
            "event_bounded_royal_field_army",
        ),
        (
            "conde_coligny_huguenot_german_army_dreux_1562",
            "Condé-Coligny Huguenot-German army at Dreux (1562)",
            "event_bounded_huguenot_foreign_coalition_army",
        ),
    ),
    "hced-Jarnac1569-1": (
        (
            "anjou_tavannes_royal_army_jarnac_1569",
            "Anjou-Tavannes royal army at Jarnac (1569)",
            "event_bounded_royal_field_army",
        ),
        (
            "conde_coligny_huguenot_army_jarnac_1569",
            "Condé-Coligny Huguenot army at Jarnac (1569)",
            "event_bounded_huguenot_field_army",
        ),
    ),
    "hced-La Roche-LAbeille1569-1": (
        (
            "coligny_huguenot_german_force_roche_1569",
            "Coligny's Huguenot-German force at La Roche-l'Abeille (1569)",
            "event_bounded_huguenot_foreign_force",
        ),
        (
            "strozzi_royal_detachment_roche_1569",
            "Strozzi's royal detachment at La Roche-l'Abeille (1569)",
            "event_bounded_royal_detachment",
        ),
    ),
    "hced-La Rochelle1625-1": (
        (
            "montmorency_royal_fleet_re_1625",
            "Montmorency's royal fleet off Île de Ré (1625)",
            "event_bounded_royal_fleet",
        ),
        (
            "soubise_rochelais_fleet_re_1625",
            "Soubise's Rochelais-Huguenot fleet off Île de Ré (1625)",
            "event_bounded_huguenot_fleet",
        ),
    ),
    "hced-Moncontour1569-1": (
        (
            "anjou_royal_coalition_army_moncontour_1569",
            "Anjou's royal and foreign coalition army at Moncontour (1569)",
            "event_bounded_royal_foreign_coalition_army",
        ),
        (
            "coligny_huguenot_army_moncontour_1569",
            "Coligny's Huguenot army at Moncontour (1569)",
            "event_bounded_huguenot_field_army",
        ),
    ),
    "hced-Montauban1621-1": (
        (
            "montauban_huguenot_garrison_civic_defenders_1621",
            "Montauban Huguenot garrison and civic defenders (1621)",
            "event_bounded_garrison_civic_defence_force",
        ),
        (
            "louis_xiii_royal_siege_army_montauban_1621",
            "Louis XIII's royal siege army at Montauban (1621)",
            "event_bounded_royal_siege_army",
        ),
    ),
    "hced-Orthez1569-1": (
        (
            "montgomery_huguenot_bearn_force_orthez_1569",
            "Montgomery's Huguenot-Béarn force at Orthez (1569)",
            "event_bounded_huguenot_regional_force",
        ),
        (
            "terride_royalist_bearn_force_orthez_1569",
            "Terride's royalist Béarn force at Orthez (1569)",
            "event_bounded_royalist_regional_force",
        ),
    ),
    "hced-Poitiers1569-1": (
        (
            "guise_poitiers_royalist_garrison_1569",
            "Guise's Poitiers royalist garrison and defenders (1569)",
            "event_bounded_royalist_garrison",
        ),
        (
            "coligny_huguenot_siege_army_poitiers_1569",
            "Coligny's Huguenot siege army at Poitiers (1569)",
            "event_bounded_huguenot_siege_army",
        ),
    ),
    "hced-Rouen1562-1": (
        (
            "guise_royal_siege_army_rouen_1562",
            "Guise's royal siege army at Rouen (1562)",
            "event_bounded_royal_siege_army",
        ),
        (
            "rouen_huguenot_english_garrison_1562",
            "Rouen Huguenot-English garrison (1562)",
            "event_bounded_huguenot_foreign_garrison",
        ),
    ),
    "hced-St Denis, France1567-1": (
        (
            "montmorency_royal_army_saint_denis_1567",
            "Montmorency's royal army at Saint-Denis (1567)",
            "event_bounded_royal_field_army",
        ),
        (
            "conde_huguenot_field_army_saint_denis_1567",
            "Condé's Huguenot field army at Saint-Denis (1567)",
            "event_bounded_huguenot_field_army",
        ),
    ),
    "hced-St Jean dAngely1621-1": (
        (
            "louis_xiii_royal_siege_army_saint_jean_1621",
            "Louis XIII's royal siege army at Saint-Jean-d'Angély (1621)",
            "event_bounded_royal_siege_army",
        ),
        (
            "soubise_saint_jean_huguenot_garrison_1621",
            "Soubise's Saint-Jean-d'Angély Huguenot garrison (1621)",
            "event_bounded_huguenot_garrison",
        ),
    ),
    "hced-Vergt1562-1": (
        (
            "montluc_royalist_army_vergt_1562",
            "Montluc's royalist army at Vergt (1562)",
            "event_bounded_royalist_field_army",
        ),
        (
            "duras_huguenot_relief_army_vergt_1562",
            "Duras's Huguenot relief army at Vergt (1562)",
            "event_bounded_huguenot_relief_army",
        ),
    ),
}

_EVENT_YEARS = {
    candidate_id: int(candidate_id.rsplit("-", 1)[0][-4:])
    for candidate_id in _ENTITY_SPECS
}
_ENTITY_SCOPE = (
    "The side is the commander-led formation actually contesting this action, "
    "including named allied contingents where the HCED side is compound."
)
WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES: tuple[dict[str, Any], ...] = tuple(
    _entity(
        entity_id,
        name,
        kind,
        _EVENT_YEARS[candidate_id],
        _EVENT_EVIDENCE[candidate_id],
        _ENTITY_SCOPE,
    )
    for candidate_id in sorted(_ENTITY_SPECS)
    for entity_id, name, kind in _ENTITY_SPECS[candidate_id]
)
_ENTITY_IDS_BY_CANDIDATE = {
    candidate_id: (specs[0][0], specs[1][0])
    for candidate_id, specs in _ENTITY_SPECS.items()
}


_FUNNEL_CATHOLIC_IDS = frozenset(
    WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES["french catholics"]
    - {"hced-Vassy1562-1"}
)
_FUNNEL_PROTESTANT_IDS = frozenset(
    WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES["french protestants"]
    - {"hced-Vassy1562-1"}
)
_FUNNEL_UNION_IDS = frozenset(_FUNNEL_CATHOLIC_IDS | _FUNNEL_PROTESTANT_IDS)
_FUNNEL_GREEDY_IDS = frozenset(_FUNNEL_UNION_IDS - {"hced-Paris1590-1"})
_FUNNEL_SOLE_BLOCKERS = {
    "hced-La Rochelle1625-1": "french protestants",
    "hced-Moncontour1569-1": "french protestants",
    "hced-Rouen1562-1": "french catholics",
    "hced-St Jean dAngely1621-1": "french protestants",
}
WAVE8_FRENCH_RELIGIOUS_FORCES_FUNNEL_AUDIT: dict[str, Any] = {
    "labels": {
        "french catholics": {
            "candidate_ids": [],
            "centuries": {"CE_16": 15, "CE_17": 1},
            "components_bridged": 0,
            "components_touched": 1,
            "event_candidate_id_sha256": "8a2ac2c2783e2e8c11c538a233853f6114fbd0f413cc0958220e91260620f0bd",
            "events_touched": 16,
            "failure_cases": {
                "multiple_time_valid_candidates": 0,
                "one_wrong_interval_candidate": 0,
                "policy_denied_window": 0,
                "resolver_guard_or_tier_conflict": 0,
                "zero_time_valid_candidates": 16,
            },
            "label": "french catholics",
            "rated_counterpart_entities": 1,
            "sole_blocker_events": 1,
            "time_valid_candidate_ids": [],
            "unresolved_side_attempts": 16,
        },
        "french protestants": {
            "candidate_ids": [],
            "centuries": {"CE_15": 1, "CE_16": 11, "CE_17": 3},
            "components_bridged": 0,
            "components_touched": 1,
            "event_candidate_id_sha256": "04cbc352e3049810b7f5781f5871d91ceaf5b2178502b486691119e15b216608",
            "events_touched": 15,
            "failure_cases": {
                "multiple_time_valid_candidates": 0,
                "one_wrong_interval_candidate": 0,
                "policy_denied_window": 0,
                "resolver_guard_or_tier_conflict": 0,
                "zero_time_valid_candidates": 15,
            },
            "label": "french protestants",
            "rated_counterpart_entities": 2,
            "sole_blocker_events": 3,
            "time_valid_candidate_ids": [],
            "unresolved_side_attempts": 15,
        },
    },
    "funnel_candidate_id_sha256": "a4e12d53e61a9ab7edc5a4dcd70bb9499bf249eb9be2525c6aae805d9f060f77",
    "funnel_rows": 21,
    "greedy_candidate_id_sha256": "183dbadafc58c7096610533dd906eeba35b81de995ffea5756cff439555da4cb",
    "greedy_rows": 20,
    "non_greedy_candidate_ids": ["hced-Paris1590-1"],
    "shared_candidate_id_sha256": "4ec5a35d54e51ae9b2ae191306b4e69e9fb2d551c5b82c56e0c5369f5873de44",
    "shared_rows": 10,
    "sole_blocker_candidate_ids": sorted(_FUNNEL_SOLE_BLOCKERS),
}


def _canonical(
    name: str,
    year_low: int,
    date_text: str,
    *,
    year_high: int | None = None,
    date_precision: str = "day",
    granularity: str = "engagement",
) -> dict[str, Any]:
    high = year_low if year_high is None else year_high
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{high}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": high,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    confidence: float,
    audit_note: str,
) -> dict[str, Any]:
    side_1_id, side_2_id = _ENTITY_IDS_BY_CANDIDATE[candidate_id]
    evidence = sorted(set(_EVENT_EVIDENCE[candidate_id]))
    outcomes = sorted(set(_EVENT_OUTCOME_SOURCES[candidate_id]))
    return {
        "raw_row_sha256": WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "disposition": "promote",
        "side_1_entity_ids": [side_1_id],
        "side_2_entity_ids": [side_2_id],
        "result_type": "win",
        "winner_side": 1,
        "war_type": "civil_war",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "event_bounded_huguenot_catholic_formation",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Arnay-le-Duc1570-1": _contract(
        "hced-Arnay-le-Duc1570-1",
        _canonical(
            "Battle of Arnay-le-Duc",
            1570,
            "June 1570",
            date_precision="month",
        ),
        "third_french_war_1568_1570",
        0.88,
        (
            "Wood's campaign study and the Musée protestant independently support "
            "a Huguenot tactical victory. The rating stops at this field action."
        ),
    ),
    "hced-Auneau1587-1": _contract(
        "hced-Auneau1587-1",
        _canonical("Battle of Auneau", 1587, "24 November 1587"),
        "eighth_french_war_1587",
        0.91,
        (
            "The Guise force's defeat of the German Protestant relief army is "
            "independently supported; it is not a result for all Catholics."
        ),
    ),
    "hced-Coutras1587-1": _contract(
        "hced-Coutras1587-1",
        _canonical("Battle of Coutras", 1587, "20 October 1587"),
        "eighth_french_war_1587",
        0.95,
        (
            "The Musée Condé record and Knecht support Navarre's battlefield "
            "victory over Joyeuse's army, with no strategic-war inference."
        ),
    ),
    "hced-Dormans1575-1": _contract(
        "hced-Dormans1575-1",
        _canonical("Battle of Dormans", 1575, "10 October 1575"),
        "fifth_french_war_1575",
        0.90,
        (
            "Guise's victory is bounded to his royal force against Thoré's mixed "
            "German-Protestant and Malcontent army, preserving the compound side."
        ),
    ),
    "hced-Dreux1562-1": _contract(
        "hced-Dreux1562-1",
        _canonical("Battle of Dreux", 1562, "19 December 1562"),
        "first_french_war_1562_1563",
        0.94,
        (
            "Independent military histories support the royal army's contested-"
            "field victory over Condé and Coligny's Huguenot-German army."
        ),
    ),
    "hced-Jarnac1569-1": _contract(
        "hced-Jarnac1569-1",
        _canonical("Battle of Jarnac", 1569, "13 March 1569"),
        "third_french_war_1568_1570",
        0.95,
        (
            "The Anjou-Tavannes army's victory at Jarnac is independently "
            "attested; Condé's death is context, not a separate Elo event."
        ),
    ),
    "hced-La Roche-LAbeille1569-1": _contract(
        "hced-La Roche-LAbeille1569-1",
        _canonical(
            "Battle of La Roche-l'Abeille",
            1569,
            "25 June 1569",
        ),
        "third_french_war_1568_1570",
        0.88,
        (
            "The promoted side is Coligny's event-specific Huguenot-German force, "
            "not a generic Protestant actor; sources support its tactical victory."
        ),
    ),
    "hced-La Rochelle1625-1": _contract(
        "hced-La Rochelle1625-1",
        _canonical(
            "Naval Battle off Île de Ré",
            1625,
            "September 1625",
            date_precision="month",
            granularity="naval_engagement",
        ),
        "huguenot_rebellion_1625",
        0.89,
        (
            "The French fleet's defeat of Soubise's Rochelais fleet is supported "
            "by independent institutional and scholarly accounts; it is not the "
            "later 1627-1628 siege."
        ),
    ),
    "hced-Moncontour1569-1": _contract(
        "hced-Moncontour1569-1",
        _canonical("Battle of Moncontour", 1569, "3 October 1569"),
        "third_french_war_1568_1570",
        0.95,
        (
            "The rated winner is Anjou's event-bounded royal and foreign coalition, "
            "preserving HCED's Spanish, Italian, and Swiss composition."
        ),
    ),
    "hced-Montauban1621-1": _contract(
        "hced-Montauban1621-1",
        _canonical(
            "Siege of Montauban (1621)",
            1621,
            "August-November 1621",
            date_precision="month_range",
            granularity="siege",
        ),
        "huguenot_rebellion_1621",
        0.88,
        (
            "The BnF authority record and Musée protestant support the failed royal "
            "siege and withdrawal. Only Montauban's bounded defenders receive the win."
        ),
    ),
    "hced-Orthez1569-1": _contract(
        "hced-Orthez1569-1",
        _canonical(
            "Battle and Capture of Orthez",
            1569,
            "11-15 August 1569",
            date_precision="day_range",
            granularity="engagement_and_capture",
        ),
        "third_french_war_1568_1570",
        0.84,
        (
            "The result is bounded to Montgomery's Béarn campaign force defeating "
            "Terride's local royalists and taking Orthez, not to confessions at large."
        ),
    ),
    "hced-Poitiers1569-1": _contract(
        "hced-Poitiers1569-1",
        _canonical(
            "Siege of Poitiers (1569)",
            1569,
            "24 July-7 September 1569",
            date_precision="day_range",
            granularity="siege",
        ),
        "third_french_war_1568_1570",
        0.90,
        (
            "University and Royal Collection records support the garrison's defence "
            "and Coligny's abandonment of the siege; no later campaign result is inferred."
        ),
    ),
    "hced-Rouen1562-1": _contract(
        "hced-Rouen1562-1",
        _canonical(
            "Siege of Rouen (1562)",
            1562,
            "September-October 1562",
            date_precision="month_range",
            granularity="siege",
        ),
        "first_french_war_1562_1563",
        0.89,
        (
            "The royal capture is rated against the bounded Rouen Huguenot-English "
            "garrison. English intervention is retained inside the losing formation."
        ),
    ),
    "hced-St Denis, France1567-1": _contract(
        "hced-St Denis, France1567-1",
        _canonical("Battle of Saint-Denis", 1567, "10 November 1567"),
        "second_french_war_1567",
        0.87,
        (
            "Independent sources support the royal contested-field advantage. The "
            "narrow confidence preserves the Huguenot army's orderly withdrawal."
        ),
    ),
    "hced-St Jean dAngely1621-1": _contract(
        "hced-St Jean dAngely1621-1",
        _canonical(
            "Siege of Saint-Jean-d'Angély (1621)",
            1621,
            "May-June 1621",
            date_precision="month_range",
            granularity="siege",
        ),
        "huguenot_rebellion_1621",
        0.90,
        (
            "The garrison's surrender supports a royal siege victory. The rating is "
            "limited to Louis XIII's siege army and Soubise's named garrison."
        ),
    ),
    "hced-Vergt1562-1": _contract(
        "hced-Vergt1562-1",
        _canonical("Battle of Vergt", 1562, "9 October 1562"),
        "first_french_war_1562_1563",
        0.87,
        (
            "Military histories support Montluc's victory over Duras's relief army. "
            "The event identity does not extend to later royal or Huguenot forces."
        ),
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    hold_category: str,
    evidence_refs: Iterable[str],
    hold_reason: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "disposition": "hold",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "hold_category": hold_category,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "hold_reason": hold_reason,
    }


WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Caudebec1592-1": _hold(
        "hced-Caudebec1592-1",
        _canonical(
            "Caudebec campaign action",
            1592,
            "May 1592",
            date_precision="month",
            granularity="compound_trap_relief_and_escape_maneuver",
        ),
        "ninth_french_war_1589_1598",
        "compound_maneuver_without_undivided_tactical_result",
        (
            "wave8_french_religious_knecht_wars",
            "wave8_french_religious_michigan_henry_iv",
        ),
        (
            "Not promoted: the Caudebec episode combines investment, Parma's relief, "
            "and Henry IV's escape across the Seine. HCED marks a draw but leaves the "
            "winner/loser incomplete; the bounded tactical result remains unknown, "
            "and unknown is not a draw."
        ),
    ),
    "hced-La Rochelle1572-1": _hold(
        "hced-La Rochelle1572-1",
        _canonical(
            "Siege of La Rochelle (1572-1573)",
            1572,
            "November 1572-July 1573",
            year_high=1573,
            date_precision="month_range",
            granularity="multi_year_siege_and_negotiated_settlement",
        ),
        "fourth_french_war_1572_1573",
        "truncated_multi_year_siege_and_nuanced_settlement",
        (
            "wave8_french_religious_knecht_wars",
            "wave8_french_religious_thompson_wars",
        ),
        (
            "Not promoted: HCED truncates the 1572-1573 siege to 1572 and assigns a "
            "simple Protestant win. The siege, losses, and negotiated settlement do "
            "not yield a defensible undivided tactical winner at that row granularity. "
            "The result is unknown, never a draw."
        ),
    ),
    "hced-Orleans1563-1": _hold(
        "hced-Orleans1563-1",
        _canonical(
            "Siege of Orléans (1563)",
            1563,
            "February 1563",
            date_precision="month",
            granularity="siege_terminated_by_assassination_and_peace",
        ),
        "first_french_war_1562_1563",
        "siege_terminated_without_clean_competitive_winner",
        (
            "wave8_french_religious_knecht_wars",
            "wave8_french_religious_oxford_orleans",
            "wave8_french_religious_wood_kings_army",
        ),
        (
            "Not promoted: Guise's assassination interrupted the royal siege and the "
            "Edict of Amboise followed. Treating that interruption as the HCED side's "
            "tactical victory would invent an outcome; it remains unknown, not a draw."
        ),
    ),
    "hced-Paris1590-1": _hold(
        "hced-Paris1590-1",
        _canonical(
            "Siege of Paris (1590)",
            1590,
            "May-September 1590",
            date_precision="month_range",
            granularity="siege_and_external_relief",
        ),
        "ninth_french_war_1589_1598",
        "raw_date_contamination_and_existing_event_collision",
        (
            "wave8_french_religious_culture_paris_1590",
            "wave8_french_religious_knecht_wars",
            "wave8_french_religious_michigan_henry_iv",
        ),
        (
            "Not promoted: source_record_id and participants identify the 1590 siege, "
            "but every HCED year field is 1436, colliding with the distinct released "
            "liberation of Paris in 1436. Repairing the date and choosing a single "
            "siege/relief result exceeds this lane; the result is unknown, not a draw."
        ),
    ),
    "hced-Rouen1591-1": _hold(
        "hced-Rouen1591-1",
        _canonical(
            "Siege of Rouen (1591-1592)",
            1591,
            "November 1591-April 1592",
            year_high=1592,
            date_precision="month_range",
            granularity="multi_year_siege_and_relief",
        ),
        "ninth_french_war_1589_1598",
        "truncated_siege_and_misbounded_royal_coalition",
        (
            "wave8_french_religious_bangor_elizabeth_wars",
            "wave8_french_religious_cambridge_rouen_1591",
            "wave8_french_religious_knecht_wars",
        ),
        (
            "Not promoted: the siege crosses 1591-1592, and Henry IV's besieging army "
            "included royal, English, and Dutch forces rather than a clean generic "
            "French-Protestant side. The siege/relief result is unknown here, not a draw."
        ),
    ),
}


WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Vassy1562-1": {
        "raw_row_sha256": WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_HASHES[
            "hced-Vassy1562-1"
        ],
        "canonical_event": _canonical(
            "Massacre of Vassy",
            1562,
            "1 March 1562",
            granularity="civilian_congregation_massacre",
        ),
        "cohort": "first_french_war_1562_1563",
        "disposition": "terminal_exclude",
        "result_type": "not_rateable",
        "exclusion_category": "civilian_massacre_without_competitive_military_outcome",
        "outcome_not_adjudicated": True,
        "evidence_refs": sorted(
            {
                "wave8_french_religious_british_museum_vassy",
                "wave8_french_religious_culture_vassy",
                "wave8_french_religious_knecht_wars",
            }
        ),
        "exclusion_reason": (
            "Terminally excluded: HCED itself records 'Massacre', no loser, an "
            "incomplete result, and massacre=Yes. The attack on a worshipping civilian "
            "congregation was not a competitive engagement, so no winner, loser, draw, "
            "or military formation rating may be invented."
        ),
    }
}
WAVE8_FRENCH_RELIGIOUS_FORCES_EXCLUSIONS = (
    WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS
)
WAVE8_FRENCH_RELIGIOUS_FORCES_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS,
    **WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS,
}
WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS = frozenset(
    WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS
)
WAVE8_FRENCH_RELIGIOUS_FORCES_HOLD_IDS = frozenset(
    WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS
)
WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS
)
WAVE8_FRENCH_RELIGIOUS_FORCES_EXCLUSION_IDS = (
    WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSION_IDS
)
WAVE8_FRENCH_RELIGIOUS_FORCES_RESERVED_IDS = frozenset(
    WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS
    | WAVE8_FRENCH_RELIGIOUS_FORCES_HOLD_IDS
    | WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSION_IDS
)
WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_DISPOSITIONS = {
    **{
        candidate_id: "promote"
        for candidate_id in WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS
    },
    **{
        candidate_id: "hold"
        for candidate_id in WAVE8_FRENCH_RELIGIOUS_FORCES_HOLD_IDS
    },
    **{
        candidate_id: "terminal_exclude"
        for candidate_id in WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSION_IDS
    },
}


WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_LABEL_DISPOSITIONS = {
    candidate_id: {
        "exact_labels": ["french catholics", "french protestants"],
        "disposition": WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_DISPOSITIONS[candidate_id],
        "owner_module": _MODULE_OWNER,
        "single_candidate_single_disposition": True,
        "boundary_note": (
            "This raw row is an exact-label twin, reviewed once in the coordinated "
            "lane; it must never be emitted or reserved independently by either label."
        ),
    }
    for candidate_id in sorted(WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS)
}


_RAW_POINTS: dict[str, tuple[float, float]] = {
    "hced-Arnay-le-Duc1570-1": (4.485898, 47.130623),
    "hced-Auneau1587-1": (1.773238, 48.4622839),
    "hced-Coutras1587-1": (-0.129361, 45.04067),
    "hced-Dormans1575-1": (3.638479, 49.07464),
    "hced-Dreux1562-1": (1.370889, 48.736134),
    "hced-Jarnac1569-1": (-0.1739169, 45.681389),
    "hced-La Roche-LAbeille1569-1": (1.2402, 45.5968),
    "hced-La Rochelle1625-1": (-1.2114931, 46.1620459),
    "hced-Moncontour1569-1": (-0.066707, 46.8768841),
    "hced-Montauban1621-1": (1.3529599, 44.0221252),
    "hced-Orthez1569-1": (-0.7739279, 43.48756),
    "hced-Poitiers1569-1": (0.340375, 46.580224),
    "hced-Rouen1562-1": (1.099971, 49.443232),
    "hced-St Denis, France1567-1": (2.3306832, 48.9267935),
    "hced-St Jean dAngely1621-1": (-0.5537696, 45.9432656),
    "hced-Vergt1562-1": (0.7193119, 45.026165),
}
_SIEGE_LOCATION_IDS = frozenset(
    {
        "hced-Montauban1621-1",
        "hced-Poitiers1569-1",
        "hced-Rouen1562-1",
        "hced-St Jean dAngely1621-1",
    }
)


def _location_reason(candidate_id: str) -> str:
    if candidate_id == "hced-La Rochelle1625-1":
        return (
            "HCED supplies the La Rochelle city centroid for a naval action off Île "
            "de Ré; that point cannot represent the fleet engagement. France is retained."
        )
    if candidate_id == "hced-Orthez1569-1":
        return (
            "The action combined approaches, crossing, town fighting, and capture; "
            "the Orthez settlement centroid cannot stand for the whole footprint. "
            "France is retained."
        )
    if candidate_id in _SIEGE_LOCATION_IDS:
        return (
            "The HCED settlement centroid is not an authenticated point for the siege "
            "lines, approaches, and garrison positions. France is retained."
        )
    return (
        "HCED provides a modern settlement-name geocode, while the reviewed sources "
        "do not authenticate that coordinate as the battlefield footprint. France is retained."
    )


WAVE8_FRENCH_RELIGIOUS_FORCES_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS
)
WAVE8_FRENCH_RELIGIOUS_FORCES_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = (
    frozenset()
)
WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_QUARANTINE_ADDITIONS = {
    "country": WAVE8_FRENCH_RELIGIOUS_FORCES_COUNTRY_QUARANTINE_ADDITIONS,
    "point": WAVE8_FRENCH_RELIGIOUS_FORCES_POINT_QUARANTINE_ADDITIONS,
}
WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_QUARANTINE_REASONS = {
    candidate_id: {
        "actions": ["withhold_point"],
        "retained_country": "France",
        "raw_point": list(_RAW_POINTS[candidate_id]),
        "evidence_refs": sorted(_EVENT_EVIDENCE[candidate_id]),
        "reason": _location_reason(candidate_id),
    }
    for candidate_id in sorted(WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS)
}
WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_REVIEWS = (
    WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_QUARANTINE_REASONS
)
WAVE8_FRENCH_RELIGIOUS_FORCES_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "hced-Havana1555-1": {
        "raw_row_sha256": "1de7eb7513b9a087ceee6845b8f7f9edd9e00e8a884eac8f71117e29d97766ef",
        "literal_label": "hugenot pirate jacques de sores",
        "disposition": "distinct_named_privateering_force_outside_exact_labels",
        "owner_module": None,
        "outcome_not_adjudicated": True,
        "evidence_refs": [],
        "boundary_note": (
            "A named Huguenot privateer at Havana is not the exact French "
            "Protestants actor and cannot inherit a French field-army identity."
        ),
    },
    "hced-Ivry1590-1": {
        "raw_row_sha256": "b989307ae7765f7d142a280732c021818a87bf42982c72faaeca8ea0f5a73d88",
        "literal_label": "hugenots",
        "disposition": "distinct_plural_spelling_separate_exact_lane",
        "owner_module": None,
        "outcome_not_adjudicated": True,
        "evidence_refs": [
            "wave8_french_religious_knecht_wars",
            "wave8_french_religious_michigan_henry_iv",
        ],
        "boundary_note": (
            "Ivry uses the literal Hugenots/Catholics pair rather than either exact "
            "label. This lane records the adjacency but does not adjudicate or own it."
        ),
    },
    "hced-La Rochelle1627-1": {
        "raw_row_sha256": "2f82ca248892bdd779f9251cdcc14a6826a9cf44034224d876af155db2909ff0",
        "literal_label": "england french protestants",
        "disposition": "distinct_compound_side_and_later_siege",
        "owner_module": "existing_release",
        "outcome_not_adjudicated": True,
        "evidence_refs": [
            "wave8_french_religious_holt_last_war",
            "wave8_french_religious_musee_last_wars",
        ],
        "boundary_note": (
            "The 1627 row is a later France-versus-English/Huguenot episode already "
            "owned by the release, not the 1625 naval battle in this lane."
        ),
    },
}


WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "hced-Paris1436-1": {
        "raw_row_sha256": "dcba1619d6bc4a918e73b3c8c5d564d08c4804d8a619c94d3cc8bf1a19d729ea",
        "matched_exact_candidate_id": "hced-Paris1590-1",
        "disposition": "distinct_1436_event_exposes_1590_row_date_contamination",
        "owner_module": "existing_release",
        "outcome_not_adjudicated": True,
        "boundary_note": (
            "This France/Burgundy-versus-England liberation of Paris is the genuine "
            "1436 row already released. The exact-label Paris1590 source record's "
            "1436 year fields are contamination, not authority to duplicate this event."
        ),
    }
}
WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}


WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_BOUNDARIES: dict[
    str, dict[str, Any]
] = {
    "hced_hced_la_rochelle1627_1": {
        "candidate_id": "hced-La Rochelle1627-1",
        "name": "La Rochelle",
        "year": 1627,
        "participant_entity_ids": ["kingdom_england", "kingdom_france"],
        "disposition": "retain_distinct_existing_release_owner",
        "boundary_note": (
            "The released 1627 English expedition/siege row is later than and "
            "compositionally distinct from the lane's 1625 fleet action."
        ),
    },
    "hced_hced_paris1436_1": {
        "candidate_id": "hced-Paris1436-1",
        "name": "Paris",
        "year": 1436,
        "participant_entity_ids": ["kingdom_england", "kingdom_france"],
        "disposition": "retain_distinct_existing_release_owner",
        "boundary_note": (
            "The released 1436 liberation is genuine; the exact-label Paris1590 "
            "row is held because its year fields collide with this event."
        ),
    },
}


WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_EVENT_BOUNDARIES: dict[str, dict[str, Any]] = {
    "la_rochelle_1572_1625_1627": {
        "candidate_ids": [
            "hced-La Rochelle1572-1",
            "hced-La Rochelle1625-1",
            "hced-La Rochelle1627-1",
        ],
        "dispositions": ["hold", "promote", "existing_release"],
        "boundary_note": (
            "The 1572-1573 siege, 1625 naval battle, and 1627 expedition/siege "
            "are three events; place-name equality grants no duplicate ownership."
        ),
    },
    "paris_1436_1590": {
        "candidate_ids": ["hced-Paris1436-1", "hced-Paris1590-1"],
        "dispositions": ["existing_release", "hold"],
        "boundary_note": (
            "A malformed year creates a raw name/year collision, but the participant "
            "and source-record evidence identifies distinct fifteenth- and sixteenth-"
            "century events. The malformed row stays held."
        ),
    },
    "rouen_1562_1591": {
        "candidate_ids": ["hced-Rouen1562-1", "hced-Rouen1591-1"],
        "dispositions": ["promote", "hold"],
        "boundary_note": (
            "The 1562 royal capture and 1591-1592 siege/relief are distinct. Only "
            "the formation- and time-bounded 1562 result is promoted."
        ),
    },
}


def _duplicate_review(
    aliases: Iterable[str], years: Iterable[int]
) -> dict[str, tuple[Any, ...]]:
    return {
        "aliases": tuple(sorted(set(map(normalize_label, aliases)) - {""})),
        "years": tuple(sorted(set(map(int, years)))),
    }


WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_ZERO_OVERLAP_AUDIT: dict[
    str, dict[str, tuple[Any, ...]]
] = {
    "hced-Arnay-le-Duc1570-1": _duplicate_review(
        ("Arnay-le-Duc", "Battle of Arnay-le-Duc"), (1570,)
    ),
    "hced-Auneau1587-1": _duplicate_review(
        ("Auneau", "Battle of Auneau"), (1587,)
    ),
    "hced-Caudebec1592-1": _duplicate_review(
        ("Caudebec", "Battle of Caudebec", "Siege of Caudebec"), (1592,)
    ),
    "hced-Coutras1587-1": _duplicate_review(
        ("Coutras", "Battle of Coutras"), (1587,)
    ),
    "hced-Dormans1575-1": _duplicate_review(
        ("Dormans", "Battle of Dormans"), (1575,)
    ),
    "hced-Dreux1562-1": _duplicate_review(
        ("Dreux", "Battle of Dreux"), (1562,)
    ),
    "hced-Jarnac1569-1": _duplicate_review(
        ("Jarnac", "Battle of Jarnac"), (1569,)
    ),
    "hced-La Roche-LAbeille1569-1": _duplicate_review(
        ("La Roche-LAbeille", "La Roche-l'Abeille", "Battle of La Roche-l'Abeille"),
        (1569,),
    ),
    "hced-La Rochelle1572-1": _duplicate_review(
        ("La Rochelle", "Siege of La Rochelle", "Siege of La Rochelle 1572 1573"),
        (1572, 1573),
    ),
    "hced-La Rochelle1625-1": _duplicate_review(
        ("La Rochelle", "Battle of Ré", "Naval Battle off Île de Ré"), (1625,)
    ),
    "hced-Moncontour1569-1": _duplicate_review(
        ("Moncontour", "Battle of Moncontour"), (1569,)
    ),
    "hced-Montauban1621-1": _duplicate_review(
        ("Montauban", "Siege of Montauban", "Siege of Montauban 1621"), (1621,)
    ),
    "hced-Orleans1563-1": _duplicate_review(
        ("Orleans", "Orléans", "Siege of Orleans", "Siege of Orléans"), (1563,)
    ),
    "hced-Orthez1569-1": _duplicate_review(
        ("Orthez", "Battle of Orthez", "Battle and Capture of Orthez"), (1569,)
    ),
    "hced-Paris1590-1": _duplicate_review(
        ("Paris", "Siege of Paris", "Siege of Paris 1590"), (1436, 1590)
    ),
    "hced-Poitiers1569-1": _duplicate_review(
        ("Poitiers", "Siege of Poitiers", "Siege of Poitiers 1569"), (1569,)
    ),
    "hced-Rouen1562-1": _duplicate_review(
        ("Rouen", "Siege of Rouen", "Siege of Rouen 1562"), (1562,)
    ),
    "hced-Rouen1591-1": _duplicate_review(
        ("Rouen", "Siege of Rouen", "Siege of Rouen 1591"), (1591, 1592)
    ),
    "hced-St Denis, France1567-1": _duplicate_review(
        ("St Denis France", "Saint Denis", "Battle of Saint-Denis"), (1567,)
    ),
    "hced-St Jean dAngely1621-1": _duplicate_review(
        (
            "St Jean dAngely",
            "Saint-Jean-d'Angély",
            "Siege of Saint-Jean-d'Angély 1621",
        ),
        (1621,),
    ),
    "hced-Vassy1562-1": _duplicate_review(
        ("Vassy", "Wassy", "Massacre of Vassy", "Massacre of Wassy"), (1562,)
    ),
    "hced-Vergt1562-1": _duplicate_review(
        ("Vergt", "Battle of Vergt"), (1562,)
    ),
}


WAVE8_FRENCH_RELIGIOUS_FORCES_INTEGRATION_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    **{
        f"cross_label:{candidate_id}": disposition
        for candidate_id, disposition in (
            WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_LABEL_DISPOSITIONS.items()
        )
    },
    **{
        f"adjacent_hced:{candidate_id}": disposition
        for candidate_id, disposition in (
            WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS.items()
        )
    },
    **{
        f"hced_duplicate:{candidate_id}": disposition
        for candidate_id, disposition in (
            WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS.items()
        )
    },
    **{
        f"release_boundary:{event_id}": disposition
        for event_id, disposition in (
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_BOUNDARIES.items()
        )
    },
    **{
        f"cross_event:{boundary_id}": disposition
        for boundary_id, disposition in (
            WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_EVENT_BOUNDARIES.items()
        )
    },
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return [_jsonable(item) for item in sorted(value, key=str)]
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _jsonable(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_hced_dispositions": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS
        ),
        "contracts": WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS,
        "country_quarantine_additions": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_event_boundaries": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_EVENT_BOUNDARIES
        ),
        "cross_label_dispositions": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_LABEL_DISPOSITIONS
        ),
        "entities": WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES,
        "exact_label_digests": WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_DIGESTS,
        "exact_label_inventories": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES
        ),
        "existing_release_boundaries": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_BOUNDARIES
        ),
        "existing_release_duplicate_dispositions": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS
        ),
        "funnel_audit": WAVE8_FRENCH_RELIGIOUS_FORCES_FUNNEL_AUDIT,
        "hced_duplicate_dispositions": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS
        ),
        "hced_queue_sha256": WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_QUEUE_SHA256,
        "holds": WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS,
        "integration_dispositions": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_queue_sha256": WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_QUEUE_SHA256,
        "iwbd_zero_overlap_audit": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "location_reviews": WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_REVIEWS,
        "outcome_overrides": WAVE8_FRENCH_RELIGIOUS_FORCES_OUTCOME_OVERRIDES,
        "point_quarantine_additions": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_POINT_QUARANTINE_ADDITIONS
        ),
        "row_dispositions": WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_DISPOSITIONS,
        "row_hashes": WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_HASHES,
        "shared_exact_ids": WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS,
        "sources": WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES,
        "terminal_exclusions": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS
        ),
    }


def wave8_french_religious_forces_audit_signature() -> str:
    """Return the SHA-256 pin over every semantic decision in this lane."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_FRENCH_RELIGIOUS_FORCES_FINAL_AUDIT_SIGNATURE = (
    "cbca7f8a20ae78e87ea5becc5a73df0cde6272771015e8019d98e77f08df2a70"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(map(str, values))))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS),
        len(WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS),
        len(WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS),
    ) != (16, 5, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (
        len(WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES),
        len(WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES),
    ) != (32, 21):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_FRENCH_RELIGIOUS_FORCES_RESERVED_IDS != (
        WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS
    ) or set(WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_HASHES) != (
        WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} reservation/fingerprint inventory changed")
    if WAVE8_FRENCH_RELIGIOUS_FORCES_EXCLUSIONS is not (
        WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS
    ):
        raise ValueError(f"{_LANE_NAME} exclusion alias changed")
    if set(WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_DISPOSITIONS) != (
        WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS
    ) or Counter(WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_DISPOSITIONS.values()) != {
        "hold": 5,
        "promote": 16,
        "terminal_exclude": 1,
    }:
        raise ValueError(f"{_LANE_NAME} row partition changed")
    if (
        WAVE8_FRENCH_RELIGIOUS_FORCES_FINAL_AUDIT_SIGNATURE != "__PENDING__"
        and wave8_french_religious_forces_audit_signature()
        != WAVE8_FRENCH_RELIGIOUS_FORCES_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    expected_label_counts = {
        "french catholics": 17,
        "french protestants": 16,
    }
    if set(WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES) != _EXACT_LABELS:
        raise ValueError(f"{_LANE_NAME} exact-label inventory keys changed")
    for label, inventory in (
        WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES.items()
    ):
        if len(inventory) != expected_label_counts[label]:
            raise ValueError(f"{_LANE_NAME} exact-label count changed for {label}")
        if _sorted_newline_sha256(inventory) != (
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_DIGESTS[label]
        ):
            raise ValueError(f"{_LANE_NAME} exact-label digest changed for {label}")
    if (
        len(WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS),
        len(WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS),
        _sorted_newline_sha256(
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS
        ),
        _sorted_newline_sha256(WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS),
    ) != (
        22,
        11,
        "024a66ce3bf6944d3375eead318cf8419794c79a82da20691c912bf6899dc264",
        "2067ae5f6bffa6787d58b2bf17e5523e128ee728f8e5615172438b53723eec01",
    ):
        raise ValueError(f"{_LANE_NAME} union/shared-label inventory changed")
    if set(WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_LABEL_DISPOSITIONS) != (
        WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} cross-label twin audit changed")

    source_by_id = {
        str(source["id"]): source
        for source in WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES
    }
    if len(source_by_id) != len(WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES:
        if (
            not str(source["url"]).startswith("https://")
            or source["accessed"] != "2026-07-16"
            or not str(source["source_family_id"]).strip()
            or not _is_sorted_unique(source["evidence_roles"])
        ):
            raise ValueError(f"{_LANE_NAME} source provenance changed")

    entity_by_id = {
        str(entity["id"]): entity
        for entity in WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES
    }
    expected_entity_ids = {
        spec[0]
        for specs in _ENTITY_SPECS.values()
        for spec in specs
    }
    if set(entity_by_id) != expected_entity_ids:
        raise ValueError(f"{_LANE_NAME} entity identity inventory changed")
    for entity in WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES:
        if (
            int(entity["start_year"]) != int(entity["end_year"])
            or entity["aliases"]
            or entity["predecessors"]
            or not _is_sorted_unique(entity["source_ids"])
            or not set(entity["source_ids"]) <= set(source_by_id)
        ):
            raise ValueError(f"{_LANE_NAME} event-bounded entity changed")
        note = str(entity["continuity_note"]).casefold()
        for phrase in (
            "only for the named action",
            "no rating is inherited",
            "french protestants",
            "french catholics",
            "civilian population",
            "another event",
        ):
            if phrase not in note:
                raise ValueError(f"{_LANE_NAME} continuity firewall changed")
        if normalize_label(entity["name"]) in _EXACT_LABELS:
            raise ValueError(f"{_LANE_NAME} created a generic religious entity")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in (
        WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS.items()
    ):
        if contract["raw_row_sha256"] != (
            WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_HASHES[candidate_id]
        ):
            raise ValueError(f"{_LANE_NAME} promotion fingerprint changed")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        raw_year = _EVENT_YEARS[candidate_id]
        if (
            canonical["canonical_key"] != expected_key
            or (int(canonical["year_low"]), int(canonical["year_high"]))
            != (raw_year, raw_year)
            or not canonical["date_text"]
        ):
            raise ValueError(f"{_LANE_NAME} canonical promotion date changed")
        expected_sides = _ENTITY_IDS_BY_CANDIDATE[candidate_id]
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if (
            side_1 != [expected_sides[0]]
            or side_2 != [expected_sides[1]]
            or set(side_1) & set(side_2)
        ):
            raise ValueError(f"{_LANE_NAME} formation boundary changed")
        used_entities.update(side_1 + side_2)
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"]
            != "event_bounded_huguenot_catholic_formation"
            or contract["duplicate_ownership"]
            != {
                "owner_module": _MODULE_OWNER,
                "status": "canonical_hced_owner",
            }
        ):
            raise ValueError(f"{_LANE_NAME} outcome/ownership semantics changed")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        expected_families = sorted(
            {
                str(source_by_id[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if (
            not _is_sorted_unique(evidence)
            or not set(evidence) <= set(source_by_id)
            or len(outcomes) < 2
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
            or families != expected_families
            or len(families) < 2
            or any(
                "outcome" not in source_by_id[source_id]["evidence_roles"]
                for source_id in outcomes
            )
        ):
            raise ValueError(f"{_LANE_NAME} independent outcome evidence changed")
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")

    for candidate_id, hold in WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS.items():
        if (
            hold["raw_row_sha256"]
            != WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_HASHES[candidate_id]
            or hold["disposition"] != "hold"
            or hold["result_type"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} hold became rateable")
        for forbidden in (
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "outcome_source_ids",
            "outcome_source_family_ids",
        ):
            if forbidden in hold:
                raise ValueError(f"{_LANE_NAME} hold asserts a result")
        reason = str(hold["hold_reason"]).casefold()
        if not all(
            phrase in reason
            for phrase in ("not promoted", "unknown", "draw")
        ):
            raise ValueError(f"{_LANE_NAME} unknown/no-draw contract weakened")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence changed")
        used_sources.update(evidence)

    exclusion = WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS[
        "hced-Vassy1562-1"
    ]
    if (
        exclusion["disposition"] != "terminal_exclude"
        or exclusion["result_type"] != "not_rateable"
        or exclusion["outcome_not_adjudicated"] is not True
        or "civilian" not in exclusion["exclusion_category"]
        or "no winner" not in exclusion["exclusion_reason"].casefold()
    ):
        raise ValueError(f"{_LANE_NAME} Vassy exclusion changed")
    for forbidden in (
        "winner_side",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "outcome_source_ids",
        "outcome_source_family_ids",
    ):
        if forbidden in exclusion:
            raise ValueError(f"{_LANE_NAME} exclusion asserts a result")
    used_sources.update(map(str, exclusion["evidence_refs"]))
    if WAVE8_FRENCH_RELIGIOUS_FORCES_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} acquired an outcome override")

    if (
        WAVE8_FRENCH_RELIGIOUS_FORCES_POINT_QUARANTINE_ADDITIONS
        != WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS
        or WAVE8_FRENCH_RELIGIOUS_FORCES_COUNTRY_QUARANTINE_ADDITIONS
        or set(WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_REVIEWS)
        != WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location quarantine changed")
    for candidate_id, review in WAVE8_FRENCH_RELIGIOUS_FORCES_LOCATION_REVIEWS.items():
        if (
            review["actions"] != ["withhold_point"]
            or review["retained_country"] != "France"
            or tuple(review["raw_point"]) != _RAW_POINTS[candidate_id]
            or not review["reason"]
            or not _is_sorted_unique(review["evidence_refs"])
        ):
            raise ValueError(f"{_LANE_NAME} location contract changed")
        used_sources.update(map(str, review["evidence_refs"]))

    if set(WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} IWBD negative audit is incomplete")
    for review in WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, review["aliases"]))
        years = list(map(int, review["years"]))
        if (
            not aliases
            or not years
            or not _is_sorted_unique(aliases)
            or aliases != list(map(normalize_label, aliases))
            or years != sorted(set(years))
        ):
            raise ValueError(f"{_LANE_NAME} duplicate search contract changed")
    if (
        WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} acquired an unreviewed duplicate owner")
    if set(WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS) != {
        "hced-Havana1555-1",
        "hced-Ivry1590-1",
        "hced-La Rochelle1627-1",
    } or set(WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS) != {
        "hced-Paris1436-1"
    }:
        raise ValueError(f"{_LANE_NAME} HCED adjacency/duplicate audit changed")
    for disposition in (
        *WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS.values(),
    ):
        evidence = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} adjacent evidence changed")
        used_sources.update(evidence)
    if set(WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_BOUNDARIES) != {
        "hced_hced_la_rochelle1627_1",
        "hced_hced_paris1436_1",
    } or set(WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_EVENT_BOUNDARIES) != {
        "la_rochelle_1572_1625_1627",
        "paris_1436_1590",
        "rouen_1562_1591",
    }:
        raise ValueError(f"{_LANE_NAME} same-name event boundaries changed")

    used_sources.update(
        source_id
        for entity in WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(
            f"{_LANE_NAME} sources are not exactly consumed: "
            f"{sorted(set(source_by_id) - used_sources)}"
        )


def _exact_labels_for_row(row: Mapping[str, Any]) -> frozenset[str]:
    return frozenset(
        label
        for label in (
            normalize_label(row.get("side_1_raw")),
            normalize_label(row.get("side_2_raw")),
        )
        if label in _EXACT_LABELS
    )


def validate_wave8_french_religious_forces_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin every row containing either exact label and its sole disposition."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS,
        WAVE8_FRENCH_RELIGIOUS_FORCES_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    actual_by_label = {
        label: {
            str(row.get("candidate_id"))
            for row in hced_rows
            if label in _exact_labels_for_row(row)
        }
        for label in _EXACT_LABELS
    }
    if actual_by_label != {
        label: set(inventory)
        for label, inventory in (
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES.items()
        )
    }:
        raise ValueError(f"{_LANE_NAME} exact-label inventories changed")
    actual_union = set().union(*actual_by_label.values())
    actual_shared = set.intersection(*actual_by_label.values())
    if actual_union != WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label union changed")
    if actual_shared != WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS:
        raise ValueError(f"{_LANE_NAME} cross-label twin inventory changed")

    by_id = {
        str(row.get("candidate_id")): row
        for row in hced_rows
        if str(row.get("candidate_id")) in actual_union
    }
    vassy = by_id["hced-Vassy1562-1"]
    if (
        vassy.get("winner_raw") != "Massacre"
        or vassy.get("loser_raw") is not None
        or vassy.get("winner_loser_complete") is not False
        or vassy.get("massacre_raw") != "Yes"
    ):
        raise ValueError(f"{_LANE_NAME} Vassy raw exclusion premise changed")
    paris = by_id["hced-Paris1590-1"]
    if (
        paris.get("source_record_id") != "Paris1590"
        or (paris.get("year_low"), paris.get("year_best"), paris.get("year_high"))
        != (1436, 1436, 1436)
    ):
        raise ValueError(f"{_LANE_NAME} Paris date contamination changed")
    return {
        "french_catholic_exact_rows": len(actual_by_label["french catholics"]),
        "french_protestant_exact_rows": len(actual_by_label["french protestants"]),
        "holds": len(WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": len(actual_union),
        "shared_exact_rows": len(actual_shared),
        "terminal_exclusions": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS
        ),
    }


def _validate_release_lane_overlap(
    existing_events: list[Mapping[str, Any]],
) -> int:
    lane_events = [
        event
        for event in existing_events
        if event.get("hced_candidate_id")
        in WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS
        or str(event.get("id") or "").startswith(_EVENT_ID_PREFIX)
    ]
    if not lane_events:
        return 0
    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    for event in lane_events:
        by_candidate.setdefault(
            str(event.get("hced_candidate_id") or ""), []
        ).append(event)
    if set(by_candidate) != WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS or any(
        len(events) != 1 for events in by_candidate.values()
    ):
        raise ValueError(f"{_LANE_NAME} release overlap is partial or duplicated")
    for candidate_id, events in by_candidate.items():
        event = events[0]
        contract = WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS[candidate_id]
        expected_id = f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        participant_ids = sorted(
            str(participant.get("entity_id"))
            for participant in event.get("participants", [])
            if participant.get("entity_id") is not None
        )
        expected_participants = sorted(
            [
                *map(str, contract["side_1_entity_ids"]),
                *map(str, contract["side_2_entity_ids"]),
            ]
        )
        canonical = contract["canonical_event"]
        if (
            event.get("id") != expected_id
            or event.get("name") != canonical["name"]
            or event.get("year") != canonical["year_low"]
            or participant_ids != expected_participants
        ):
            raise ValueError(
                f"{_LANE_NAME} integrated release ownership changed: {candidate_id}"
            )
    return len(lane_events)


def validate_wave8_french_religious_forces_funnel(
    funnel: Mapping[str, Any],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin both funnel records, shared blockers, and zero/full integration."""

    _validate_static()
    labels = funnel.get("labels")
    if not isinstance(labels, list):
        raise ValueError(f"{_LANE_NAME} funnel labels are unavailable")
    matches = {
        str(record.get("label")): record
        for record in labels
        if normalize_label(record.get("label")) in _EXACT_LABELS
    }
    if matches != WAVE8_FRENCH_RELIGIOUS_FORCES_FUNNEL_AUDIT["labels"]:
        raise ValueError(f"{_LANE_NAME} funnel label records changed")

    row_data = funnel.get("row_label_data")
    if not isinstance(row_data, list):
        raise ValueError(f"{_LANE_NAME} row-label data are unavailable")
    audited = {label: set() for label in _EXACT_LABELS}
    sole_blockers: dict[str, str] = {}
    greedy_ids: set[str] = set()
    non_greedy_ids: set[str] = set()
    for row in row_data:
        candidate_id = str(row.get("candidate_id"))
        failures = row.get("label_failures")
        exact_failures = [
            item
            for item in failures
            if normalize_label(item.get("label")) in _EXACT_LABELS
        ] if isinstance(failures, list) else []
        if not exact_failures:
            continue
        for failure in exact_failures:
            label = normalize_label(failure.get("label"))
            if (
                failure.get("failure_case") != "zero_time_valid_candidates"
                or failure.get("candidate_ids")
                or failure.get("time_valid_candidate_ids")
            ):
                raise ValueError(f"{_LANE_NAME} funnel failure semantics changed")
            audited[label].add(candidate_id)
        sole_label = row.get("sole_blocker_label")
        if normalize_label(sole_label) in _EXACT_LABELS:
            sole_blockers[candidate_id] = normalize_label(sole_label)
        if row.get("greedy_eligible") is True:
            greedy_ids.add(candidate_id)
        else:
            non_greedy_ids.add(candidate_id)
            if candidate_id != "hced-Paris1590-1" or row.get("other_blockers") != [
                "duplicate_of_existing_event"
            ]:
                raise ValueError(f"{_LANE_NAME} non-greedy boundary changed")
    expected_audited = {
        "french catholics": set(_FUNNEL_CATHOLIC_IDS),
        "french protestants": set(_FUNNEL_PROTESTANT_IDS),
    }
    if audited != expected_audited:
        raise ValueError(f"{_LANE_NAME} funnel exact-label row inventory changed")
    if set().union(*audited.values()) != _FUNNEL_UNION_IDS:
        raise ValueError(f"{_LANE_NAME} funnel union changed")
    if set.intersection(*audited.values()) != (
        WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS
        - {"hced-Vassy1562-1"}
    ):
        raise ValueError(f"{_LANE_NAME} funnel shared-label rows changed")
    if sole_blockers != _FUNNEL_SOLE_BLOCKERS:
        raise ValueError(f"{_LANE_NAME} sole-blocker ownership changed")
    if greedy_ids & _FUNNEL_UNION_IDS != _FUNNEL_GREEDY_IDS or (
        non_greedy_ids & _FUNNEL_UNION_IDS
    ) != {"hced-Paris1590-1"}:
        raise ValueError(f"{_LANE_NAME} funnel greedy eligibility changed")
    if any(
        normalize_label(item.get("label")) in _EXACT_LABELS
        for item in funnel.get("greedy_batch", {}).get("ranking", [])
    ):
        raise ValueError(f"{_LANE_NAME} unexpectedly acquired a generic identity rank")
    release_overlap = _validate_release_lane_overlap(list(existing_events))
    return {
        "french_catholic_funnel_rows": len(_FUNNEL_CATHOLIC_IDS),
        "french_protestant_funnel_rows": len(_FUNNEL_PROTESTANT_IDS),
        "funnel_rows": len(_FUNNEL_UNION_IDS),
        "greedy_eligible_rows": len(_FUNNEL_GREEDY_IDS),
        "release_lane_overlap": release_overlap,
        "shared_funnel_rows": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS
            - {"hced-Vassy1562-1"}
        ),
        "sole_blocker_rows": len(_FUNNEL_SOLE_BLOCKERS),
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
        value = str(row.get(field) or "")
        text = value.lstrip("-")
        if len(text) >= 4 and text[:4].isdigit():
            year = int(text[:4])
            return -year if value.startswith("-") else year
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {normalize_label(row.get("name"))}
    aliases = row.get("aliases")
    if isinstance(aliases, list):
        names.update(normalize_label(alias) for alias in aliases)
    return names - {""}


_DUPLICATE_MATCH_KEYS = {
    (int(year), str(alias))
    for review in WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in review["years"]
    for alias in review["aliases"]
}


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def _validate_existing_release_boundaries(
    existing_events: list[Mapping[str, Any]],
) -> int:
    by_candidate: dict[str, list[Mapping[str, Any]]] = {}
    boundary_candidate_ids = {
        str(review["candidate_id"])
        for review in WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_BOUNDARIES.values()
    }
    for event in existing_events:
        candidate_id = str(event.get("hced_candidate_id") or "")
        if candidate_id in boundary_candidate_ids:
            by_candidate.setdefault(candidate_id, []).append(event)
    found = 0
    for event_id, expected in (
        WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_BOUNDARIES.items()
    ):
        candidate_id = str(expected["candidate_id"])
        events = by_candidate.get(candidate_id, [])
        if not events:
            continue
        found += 1
        if len(events) != 1:
            raise ValueError(
                f"{_LANE_NAME} duplicate existing-release boundary: {candidate_id}"
            )
        event = events[0]
        participants = sorted(
            str(item.get("entity_id"))
            for item in event.get("participants", [])
            if item.get("entity_id") is not None
        )
        if (
            event.get("id") != event_id
            or event.get("name") != expected["name"]
            or event.get("year") != expected["year"]
            or participants != expected["participant_entity_ids"]
        ):
            raise ValueError(
                f"{_LANE_NAME} existing-release boundary changed: {candidate_id}"
            )
    return found


def validate_wave8_french_religious_forces_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on twins, ownership leakage, and partial lane integration."""

    validate_wave8_french_religious_forces_queue_contracts(hced_rows)
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)

    for candidate_id, disposition in (
        WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1 or canonical_hced_row_sha256(rows[0]) != disposition[
            "raw_row_sha256"
        ]:
            raise ValueError(f"{_LANE_NAME} adjacent HCED row changed: {candidate_id}")
        labels = {
            normalize_label(rows[0].get("side_1_raw")),
            normalize_label(rows[0].get("side_2_raw")),
        }
        if disposition["literal_label"] not in labels:
            raise ValueError(
                f"{_LANE_NAME} adjacent literal label changed: {candidate_id}"
            )
    for candidate_id, disposition in (
        WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1 or canonical_hced_row_sha256(rows[0]) != disposition[
            "raw_row_sha256"
        ]:
            raise ValueError(f"{_LANE_NAME} reviewed HCED twin changed: {candidate_id}")

    reviewed_nonlane_ids = set(
        WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS
    ) | set(WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS
        and str(row.get("candidate_id")) not in reviewed_nonlane_ids
        and _is_probable_twin(row)
    )
    if hced_twins:
        raise ValueError(f"{_LANE_NAME} unreviewed HCED twin(s): {hced_twins}")
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    if iwbd_twins:
        raise ValueError(f"{_LANE_NAME} unreviewed IWBD twin(s): {iwbd_twins}")

    existing = list(existing_events)
    nonpromotion_leaks = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id")
        in (
            WAVE8_FRENCH_RELIGIOUS_FORCES_HOLD_IDS
            | WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSION_IDS
        )
    )
    if nonpromotion_leaks:
        raise ValueError(
            f"{_LANE_NAME} held/excluded row was rated: {nonpromotion_leaks}"
        )
    release_overlap = _validate_release_lane_overlap(existing)
    boundary_count = _validate_existing_release_boundaries(existing)
    release_boundary_ids = set(
        WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_BOUNDARIES
    )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id")
        not in WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS
        and str(event.get("id") or "") not in release_boundary_ids
        and not str(event.get("id") or "").startswith(_EVENT_ID_PREFIX)
        and _is_probable_twin(event)
    )
    if release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_twins}"
        )
    return {
        "adjacent_hced_dispositions": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS
        ),
        "cross_event_boundaries": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_EVENT_BOUNDARIES
        ),
        "cross_label_twins": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_LABEL_DISPOSITIONS
        ),
        "existing_release_boundaries_found": boundary_count,
        "existing_release_duplicate_dispositions": 0,
        "hced_duplicate_dispositions": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "release_lane_overlap": release_overlap,
        "release_probable_twins": 0,
    }


def install_wave8_french_religious_forces_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_french_religious_forces_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_FRENCH_RELIGIOUS_FORCES_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_FRENCH_RELIGIOUS_FORCES_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_french_religious_forces_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit exactly the sixteen independently supported bounded outcomes."""

    validate_wave8_french_religious_forces_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_french_religious_forces_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS.values(),
                    *WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS.values(),
                    *WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS.values(),
                )
            ).items()
        )
    )


def wave8_french_religious_forces_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_hced_dispositions": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_ADJACENT_HCED_DISPOSITIONS
        ),
        "country_quarantine_additions": 0,
        "cross_event_boundaries": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_EVENT_BOUNDARIES
        ),
        "cross_label_twins": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_CROSS_LABEL_DISPOSITIONS
        ),
        "existing_release_boundaries": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXISTING_RELEASE_BOUNDARIES
        ),
        "existing_release_duplicate_dispositions": 0,
        "french_catholic_exact_rows": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES[
                "french catholics"
            ]
        ),
        "french_protestant_exact_rows": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_INVENTORIES[
                "french protestants"
            ]
        ),
        "hced_duplicate_dispositions": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_HCED_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_FRENCH_RELIGIOUS_FORCES_HOLDS),
        "integration_dispositions": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_FRENCH_RELIGIOUS_FORCES_ENTITIES),
        "new_sources": len(WAVE8_FRENCH_RELIGIOUS_FORCES_SOURCES),
        "newly_rated_events": len(WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACTS),
        "reviewed_hced_rows": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXPECTED_CANDIDATE_IDS
        ),
        "shared_exact_rows": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS
        ),
        "terminal_exclusions": len(
            WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSIONS
        ),
    }


def wave8_french_religious_forces_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_FRENCH_RELIGIOUS_FORCES_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_FRENCH_RELIGIOUS_FORCES_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_french_religious_forces_row_dispositions() -> dict[str, str]:
    _validate_static()
    return dict(sorted(WAVE8_FRENCH_RELIGIOUS_FORCES_ROW_DISPOSITIONS.items()))


def wave8_french_religious_forces_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_french_religious_forces_counts(),
        "cohorts": wave8_french_religious_forces_cohort_counts(),
        "exact_label_digests": dict(
            WAVE8_FRENCH_RELIGIOUS_FORCES_EXACT_LABEL_DIGESTS
        ),
        "final_audit_signature": (
            WAVE8_FRENCH_RELIGIOUS_FORCES_FINAL_AUDIT_SIGNATURE
        ),
        "hold_ids": sorted(WAVE8_FRENCH_RELIGIOUS_FORCES_HOLD_IDS),
        "promoted_candidate_ids": sorted(
            WAVE8_FRENCH_RELIGIOUS_FORCES_CONTRACT_IDS
        ),
        "shared_exact_candidate_ids": sorted(
            WAVE8_FRENCH_RELIGIOUS_FORCES_SHARED_EXACT_IDS
        ),
        "terminal_exclusion_ids": sorted(
            WAVE8_FRENCH_RELIGIOUS_FORCES_TERMINAL_EXCLUSION_IDS
        ),
    }


_validate_static()
