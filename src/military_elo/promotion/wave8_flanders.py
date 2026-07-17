"""Candidate-keyed Wave 8 audit for HCED's exact ``Flanders`` label.

The unresolved funnel contains four exact-label rows, all in the fourteenth
century.  The shared label does not identify one timeless polity.  Courtrai
and Mons-en-Pevele concern different Flemish resistance field armies;
Zierikzee concerns Guy of Namur's fleet against a Franco-Genoese and
Holland-Zeeland coalition; and Cassel concerns the Flemish coastal rebels
against Philip VI's intervention on behalf of Count Louis of Flanders.

Every row has a source-attested tactical result.  The disputed memory of
Mons-en-Pevele is bounded to the French possession of the field after the
Flemish withdrawal and is not promoted into a claim of strategic destruction.
No generic Flanders or France alias is installed, no rating crosses into the
Burgundian or Dutch eras, and unknown is never converted into a draw.
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
    "WAVE8_FLANDERS_ADJACENT_LANE_DISPOSITIONS",
    "WAVE8_FLANDERS_CONTRACT_IDS",
    "WAVE8_FLANDERS_CONTRACTS",
    "WAVE8_FLANDERS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_FLANDERS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_FLANDERS_ENTITIES",
    "WAVE8_FLANDERS_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_FLANDERS_EXCLUSION_IDS",
    "WAVE8_FLANDERS_EXCLUSIONS",
    "WAVE8_FLANDERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_FLANDERS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_FLANDERS_FUNNEL_EVENT_CANDIDATE_ID_SHA256",
    "WAVE8_FLANDERS_HOLD_IDS",
    "WAVE8_FLANDERS_HOLDS",
    "WAVE8_FLANDERS_INTEGRATION_DISPOSITIONS",
    "WAVE8_FLANDERS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_FLANDERS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_FLANDERS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_FLANDERS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_FLANDERS_NONPROMOTIONS",
    "WAVE8_FLANDERS_OUTCOME_OVERRIDES",
    "WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS",
    "WAVE8_FLANDERS_RESERVED_IDS",
    "WAVE8_FLANDERS_ROW_HASHES",
    "WAVE8_FLANDERS_SOURCES",
    "WAVE8_FLANDERS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_FLANDERS_TERMINAL_EXCLUSIONS",
    "install_wave8_flanders_entities",
    "install_wave8_flanders_sources",
    "promote_wave8_flanders_contracts",
    "validate_wave8_flanders_integration_dispositions",
    "validate_wave8_flanders_queue_contracts",
    "wave8_flanders_audit_signature",
    "wave8_flanders_cohort_counts",
    "wave8_flanders_counts",
    "wave8_flanders_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact Flanders actor audit"
_EVENT_ID_PREFIX = "hced_wave8_flanders_"
_MODULE_OWNER = "military_elo.promotion.wave8_flanders"
_FURNES_CANDIDATE_ID = "hced-Furnes1297-1"
_FURNES_RELEASE_EVENT_ID = "hced_label_hced_furnes1297_1"
_COUNTY_OF_FLANDERS_ENTITY_ID = "clio_fr_capetian_k_1_990_39dc2541"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool,
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


WAVE8_FLANDERS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_flanders_verbruggen_golden_spurs",
        "The Battle of the Golden Spurs (Courtrai, 11 July 1302)",
        "https://www.jstor.org/stable/10.7722/j.ctt81svs",
        "Boydell Press / JSTOR",
        "scholarly_monograph",
        "verbruggen_golden_spurs_2002",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_devries_infantry",
        "Infantry Warfare in the Early Fourteenth Century",
        (
            "https://boydellandbrewer.com/book/"
            "infantry-warfare-in-the-early-fourteenth-century/"
        ),
        "Boydell & Brewer",
        "scholarly_monograph",
        "devries_infantry_warfare_1996",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_lambert_memory",
        (
            "De Guldensporenslag van fait-divers tot ankerpunt van de Vlaamse "
            "identiteit (1302-1838)"
        ),
        "https://doi.org/10.18352/bmgn-lchr.5285",
        "BMGN - Low Countries Historical Review",
        "peer_reviewed_scholarly_article",
        "lambert_guldensporenslag_2000",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_somme_devries_review",
        "Kelly De Vries, Infantry Warfare in the Early Fourteenth Century",
        (
            "https://www.persee.fr/doc/"
            "rnord_0035-2624_1999_num_91_331_2943_t1_0636_0000_2"
        ),
        "Revue du Nord / Persée",
        "scholarly_book_review",
        "somme_devries_review_1999",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_larousse_philip_iv",
        "Philippe IV le Bel",
        "https://www.larousse.fr/encyclopedie/personnage/Philippe_IV_le_Bel/137969",
        "Encyclopédie Larousse",
        "scholarly_reference_entry",
        "larousse_philip_iv",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_sayers_zierikzee",
        (
            "Naval Tactics at the Battle of Zierikzee (1304) in the Light of "
            "Mediterranean Praxis"
        ),
        (
            "https://www.cambridge.org/core/books/journal-of-medieval-military-"
            "history/naval-tactics-at-the-battle-of-zierikzee-1304-in-the-light-"
            "of-mediterranean-praxis/20F05855CF85624D9284CCDA8D8FAAC0"
        ),
        "Cambridge University Press / Boydell & Brewer",
        "peer_reviewed_scholarly_chapter",
        "sayers_zierikzee_2006",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_melis_stoke",
        "Rijmkroniek van Holland",
        "https://www.dbnl.org/titels/titel.php?id=stok001rijm01",
        "Digitale Bibliotheek voor de Nederlandse Letteren",
        "digitized_contemporary_chronicle",
        "melis_stoke_rijmkroniek",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_burgers_melis_stoke",
        "De loopbaan van de klerk Melis Stoke",
        (
            "https://www.dbnl.org/tekst/"
            "_bij005199301_01/_bij005199301_01_0004.php"
        ),
        "BMGN / Digitale Bibliotheek voor de Nederlandse Letteren",
        "peer_reviewed_source_criticism",
        "burgers_melis_stoke_1993",
        outcome=False,
    ),
    _source(
        "wave8_flanders_zierikzee_heritage",
        "Reizende Tentoonstelling 1304",
        "https://www.vriendenerfgoedzierikzee.nl/reizende-tentoonstelling-1304/",
        "Stichting Vrienden Erfgoed Zierikzee",
        "institutional_local_history",
        "zierikzee_heritage_1304",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_tebrake_insurrection",
        "A Plague of Insurrection: Popular Politics and Peasant Revolt in Flanders",
        "https://www.pennpress.org/9780812215267/a-plague-of-insurrection/",
        "University of Pennsylvania Press",
        "scholarly_monograph",
        "tebrake_plague_insurrection_1993",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_pirenne_cassel",
        "Les conséquences de la bataille de Cassel pour la ville de Bruges",
        "https://www.persee.fr/doc/bcrh_0770-6707_1899_num_68_9_2291",
        "Commission royale d'Histoire / Persée",
        "scholarly_document_study",
        "pirenne_cassel_consequences_1899",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_larousse_philip_vi",
        "Philippe VI de Valois",
        "https://www.larousse.fr/encyclopedie/personnage/wd/137971",
        "Encyclopédie Larousse",
        "scholarly_reference_entry",
        "larousse_philip_vi",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_france_culture_cassel",
        "Bataille de Cassel, 23 août 1328",
        "https://pop.culture.gouv.fr/notice/joconde/000PE005885",
        "Ministère de la Culture, France",
        "official_collection_record",
        "france_culture_cassel_1328",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_flanders_cambridge_dampierres",
        "The Dampierres, the comital family of Flanders",
        (
            "https://www.cambridge.org/core/books/abs/french-in-the-kingdom-of-"
            "sicily-12661305/dampierres-the-comital-family-of-flanders/"
            "51CEDF951380ECD92691D5D63DF0EC81"
        ),
        "Cambridge University Press",
        "scholarly_monograph_chapter",
        "dunbabin_dampierres_2011",
        outcome=False,
    ),
    _source(
        "wave8_flanders_cambridge_low_countries",
        (
            "Counts, cities and commerce: institutional foundations of trade "
            "in late medieval Flanders, Holland and Zeeland"
        ),
        (
            "https://www.cambridge.org/core/product/"
            "37D28A756288A8CCEC41456609F0739C/core-reader"
        ),
        "Cambridge University Press",
        "peer_reviewed_open_access_article",
        "zuijderduijn_et_al_low_countries_2025",
        outcome=False,
    ),
)


_COURTRAI_FLEMISH_ID = "flemish_communal_army_courtrai_1302"
_COURTRAI_FRENCH_ID = "robert_artois_french_royal_army_courtrai_1302"
_MONS_FRENCH_ID = "philip_iv_french_royal_army_mons_en_pevele_1304"
_MONS_FLEMISH_ID = "flemish_resistance_army_mons_en_pevele_1304"
_ZIERIKZEE_FRANCO_GENOESE_ID = (
    "rainier_grimaldi_french_genoese_fleet_zierikzee_1304"
)
_ZIERIKZEE_HOLLAND_ID = "william_avesnes_holland_zeeland_force_zierikzee_1304"
_ZIERIKZEE_FLEMISH_ID = "guy_namur_flemish_fleet_zierikzee_1304"
_CASSEL_FRENCH_ID = "philip_vi_french_royal_army_cassel_1328"
_CASSEL_FLEMISH_ID = "zannekin_flemish_coast_rebel_army_cassel_1328"


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    region: str,
    boundary_note: str,
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
            boundary_note
            + " No rating is inherited from or passed to generic France, the "
            "County of Flanders, a Burgundian polity, the Dutch Republic, or "
            "any modern Belgian, French, or Dutch state identity."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_FLANDERS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _COURTRAI_FLEMISH_ID,
        "Flemish communal resistance army at Courtrai (1302)",
        "event_bounded_rebel_field_army",
        1302,
        "Courtrai and the Groeninge field",
        (
            "Bounded to the Bruges, Ypres, Courtrai, Franc of Bruges, and allied "
            "contingents assembled under William of Jülich, Guy of Namur, and "
            "their commanders for the 11 July engagement."
        ),
        [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_lambert_memory",
            "wave8_flanders_verbruggen_golden_spurs",
        ],
    ),
    _entity(
        _COURTRAI_FRENCH_ID,
        "Robert of Artois's French royal army at Courtrai (1302)",
        "event_bounded_royal_field_army",
        1302,
        "Courtrai and the Groeninge field",
        (
            "Bounded to Robert II of Artois's royal cavalry, infantry, and allied "
            "contingents committed against the Flemish position on 11 July."
        ),
        [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_lambert_memory",
            "wave8_flanders_verbruggen_golden_spurs",
        ],
    ),
    _entity(
        _MONS_FRENCH_ID,
        "Philip IV's French royal army at Mons-en-Pévèle (1304)",
        "event_bounded_royal_field_army",
        1304,
        "Mons-en-Pévèle",
        (
            "Bounded to Philip IV's personally commanded royal army in the 18 "
            "August battle and the recovery of the field after the final attack."
        ),
        [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_larousse_philip_iv",
            "wave8_flanders_somme_devries_review",
        ],
    ),
    _entity(
        _MONS_FLEMISH_ID,
        "Flemish resistance army at Mons-en-Pévèle (1304)",
        "event_bounded_rebel_field_army",
        1304,
        "Mons-en-Pévèle",
        (
            "Bounded to the Flemish communal and comital resistance force led by "
            "William of Jülich, Philip of Chieti, and John of Namur in the 18 "
            "August engagement."
        ),
        [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_larousse_philip_iv",
            "wave8_flanders_somme_devries_review",
        ],
    ),
    _entity(
        _ZIERIKZEE_FRANCO_GENOESE_ID,
        "Rainier Grimaldi's French-paid Genoese fleet at Zierikzee (1304)",
        "event_bounded_allied_fleet",
        1304,
        "Gouwe channel off Zierikzee",
        (
            "Bounded to Rainier Grimaldi's French-financed Genoese-led naval "
            "contingent in the 10-11 August relief battle."
        ),
        [
            "wave8_flanders_melis_stoke",
            "wave8_flanders_sayers_zierikzee",
            "wave8_flanders_zierikzee_heritage",
        ],
    ),
    _entity(
        _ZIERIKZEE_HOLLAND_ID,
        "William of Avesnes's Holland-Zeeland force at Zierikzee (1304)",
        "event_bounded_comital_relief_force",
        1304,
        "Zierikzee and the Gouwe channel",
        (
            "Bounded to the Holland and Zeeland ships, troops, and Zierikzee "
            "defenders cooperating with Grimaldi's fleet; it predates the Dutch "
            "Republic by centuries."
        ),
        [
            "wave8_flanders_burgers_melis_stoke",
            "wave8_flanders_cambridge_low_countries",
            "wave8_flanders_melis_stoke",
            "wave8_flanders_sayers_zierikzee",
        ],
    ),
    _entity(
        _ZIERIKZEE_FLEMISH_ID,
        "Guy of Namur's Flemish fleet at Zierikzee (1304)",
        "event_bounded_comital_fleet",
        1304,
        "Gouwe channel off Zierikzee",
        (
            "Bounded to Guy of Namur's fleet and siege-supporting force defeated "
            "and captured in the 10-11 August naval engagement."
        ),
        [
            "wave8_flanders_melis_stoke",
            "wave8_flanders_sayers_zierikzee",
            "wave8_flanders_zierikzee_heritage",
        ],
    ),
    _entity(
        _CASSEL_FRENCH_ID,
        "Philip VI's French royal army at Cassel (1328)",
        "event_bounded_royal_intervention_army",
        1328,
        "Cassel and the Peene valley",
        (
            "Bounded to Philip VI's royal host intervening for Louis of Nevers "
            "and fighting the rebel assault on 23 August."
        ),
        [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_france_culture_cassel",
            "wave8_flanders_larousse_philip_vi",
            "wave8_flanders_somme_devries_review",
            "wave8_flanders_tebrake_insurrection",
        ],
    ),
    _entity(
        _CASSEL_FLEMISH_ID,
        "Nicolaas Zannekin's Flemish coastal rebel army at Cassel (1328)",
        "event_bounded_rebel_field_army",
        1328,
        "Cassel and maritime Flanders",
        (
            "Bounded to Zannekin's insurgent rural and urban militias from "
            "maritime Flanders in their final attack on the French camp."
        ),
        [
            "wave8_flanders_pirenne_cassel",
            "wave8_flanders_somme_devries_review",
            "wave8_flanders_tebrake_insurrection",
        ],
    ),
)


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str = "day",
    granularity: str = "pitched_battle",
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


WAVE8_FLANDERS_ROW_HASHES: dict[str, str] = {
    "hced-Cassel1328-1": (
        "b9fbf94bf147838713bbcc9c5523281e98b8b0b0e68d91be4b08bbb2f783905b"
    ),
    "hced-Courtrai1302-1": (
        "96c9568e26b8c6bd93186cf415c2e811bd978d1146792947b0f0a8464c0fc9aa"
    ),
    "hced-Mons-en-Pevele1304-1": (
        "59e4182daa03c314845e5dc76d09c83fd7e0931ca264c622eba98d6fce1c7f09"
    ),
    "hced-Zieriksee1304-1": (
        "7a671a835ba8d4c6d9c192d4a6b41571ce4280b5b7ac9bdfab99dd40b0853838"
    ),
}

_RELATED_ROW_HASHES = {
    "hced-Bruges1302-1": (
        "de7ab6229982ceb2334b030782ec31f3bab70e16ef15556ec90c6389372d3f0c"
    ),
    "hced-Furnes1297-1": (
        "a723935dcde264ef3474442b8a47faca832ee55c6eeeb2e08fec12798dec0c4a"
    ),
}

_SOURCE_FAMILY_BY_ID = {
    str(source["id"]): str(source["source_family_id"])
    for source in WAVE8_FLANDERS_SOURCES
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
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "audit_note": audit_note,
        "actor_override": True,
        "canonical_event": canonical_event,
        "cohort": cohort,
        "confidence": confidence,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "evidence_refs": evidence,
        "outcome_reversal": False,
        "outcome_source_family_ids": sorted(
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        ),
        "outcome_source_ids": outcomes,
        "raw_row_sha256": WAVE8_FLANDERS_ROW_HASHES[candidate_id],
        "result_type": "win",
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "source_outcome_override": False,
        "war_type": war_type,
        "winner_side": 1,
    }


WAVE8_FLANDERS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Courtrai1302-1": _contract(
        "hced-Courtrai1302-1",
        _canonical("Battle of the Golden Spurs", 1302, "11 July 1302"),
        "franco_flemish_war_1297_1305",
        [_COURTRAI_FLEMISH_ID],
        [_COURTRAI_FRENCH_ID],
        [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_lambert_memory",
            "wave8_flanders_verbruggen_golden_spurs",
        ],
        [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_lambert_memory",
            "wave8_flanders_verbruggen_golden_spurs",
        ],
        (
            "Verbruggen, DeVries, and Lambert attest the Flemish communal "
            "coalition's defeat of Robert of Artois's royal army. The actor is "
            "the assembled resistance force, not a timeless Flemish nation or "
            "the imprisoned count as a personal combatant."
        ),
        "anti_imperial_revolt",
        confidence=0.98,
    ),
    "hced-Zieriksee1304-1": _contract(
        "hced-Zieriksee1304-1",
        _canonical(
            "Battle of Zierikzee",
            1304,
            "10-11 August 1304",
            date_precision="day_range",
            granularity="naval_battle_and_siege_relief",
        ),
        "franco_flemish_war_1297_1305",
        [_ZIERIKZEE_FRANCO_GENOESE_ID, _ZIERIKZEE_HOLLAND_ID],
        [_ZIERIKZEE_FLEMISH_ID],
        [
            "wave8_flanders_burgers_melis_stoke",
            "wave8_flanders_cambridge_low_countries",
            "wave8_flanders_melis_stoke",
            "wave8_flanders_sayers_zierikzee",
            "wave8_flanders_zierikzee_heritage",
        ],
        [
            "wave8_flanders_melis_stoke",
            "wave8_flanders_sayers_zierikzee",
            "wave8_flanders_zierikzee_heritage",
        ],
        (
            "Sayers and the contemporary Holland chronicle attest the allied "
            "victory, destruction of the Flemish fleet, capture of Guy of Namur, "
            "and relief of Zierikzee. HCED's France label is narrowed to the "
            "French-paid Genoese fleet together with the distinct Holland-"
            "Zeeland relief force; it is not a Dutch Republic event."
        ),
        "interstate_limited",
        confidence=0.97,
    ),
    "hced-Mons-en-Pevele1304-1": _contract(
        "hced-Mons-en-Pevele1304-1",
        _canonical("Battle of Mons-en-Pévèle", 1304, "18 August 1304"),
        "franco_flemish_war_1297_1305",
        [_MONS_FRENCH_ID],
        [_MONS_FLEMISH_ID],
        [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_larousse_philip_iv",
            "wave8_flanders_somme_devries_review",
            "wave8_flanders_verbruggen_golden_spurs",
        ],
        [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_larousse_philip_iv",
            "wave8_flanders_somme_devries_review",
        ],
        (
            "The sources preserve competing victory claims, but also attest "
            "that Philip IV's recovered army held the battlefield after the "
            "Flemish withdrawal. This contract records only that bounded "
            "tactical field result at reduced confidence; it does not infer an "
            "annihilation or a decisive strategic war outcome."
        ),
        "interstate_limited",
        confidence=0.88,
    ),
    "hced-Cassel1328-1": _contract(
        "hced-Cassel1328-1",
        _canonical("Battle of Cassel (1328)", 1328, "23 August 1328"),
        "flemish_coast_revolt_1323_1328",
        [_CASSEL_FRENCH_ID],
        [_CASSEL_FLEMISH_ID],
        [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_france_culture_cassel",
            "wave8_flanders_larousse_philip_vi",
            "wave8_flanders_pirenne_cassel",
            "wave8_flanders_somme_devries_review",
            "wave8_flanders_tebrake_insurrection",
        ],
        [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_france_culture_cassel",
            "wave8_flanders_larousse_philip_vi",
            "wave8_flanders_pirenne_cassel",
            "wave8_flanders_somme_devries_review",
            "wave8_flanders_tebrake_insurrection",
        ],
        (
            "The revolt study, battle scholarship, and official French record "
            "attest Philip VI's defeat of Nicolaas Zannekin's attacking coastal "
            "militias. Raw Flanders therefore means the 1328 rebels, not Count "
            "Louis's government, the later Burgundian state, or modern Flanders."
        ),
        "internal_rebellion",
        confidence=0.98,
    ),
}


WAVE8_FLANDERS_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_FLANDERS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_FLANDERS_EXCLUSIONS = WAVE8_FLANDERS_TERMINAL_EXCLUSIONS
WAVE8_FLANDERS_NONPROMOTIONS: dict[str, dict[str, Any]] = {}
WAVE8_FLANDERS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}

WAVE8_FLANDERS_CONTRACT_IDS = frozenset(WAVE8_FLANDERS_CONTRACTS)
WAVE8_FLANDERS_HOLD_IDS = frozenset(WAVE8_FLANDERS_HOLDS)
WAVE8_FLANDERS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_FLANDERS_TERMINAL_EXCLUSIONS
)
WAVE8_FLANDERS_EXCLUSION_IDS = WAVE8_FLANDERS_TERMINAL_EXCLUSION_IDS
WAVE8_FLANDERS_RESERVED_IDS = frozenset(
    WAVE8_FLANDERS_CONTRACT_IDS
    | WAVE8_FLANDERS_HOLD_IDS
    | WAVE8_FLANDERS_TERMINAL_EXCLUSION_IDS
)
WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_FLANDERS_ROW_HASHES)
WAVE8_FLANDERS_EXACT_CANDIDATE_ID_SHA256 = (
    "c821571928ccf2f116c853868c1f7e36c4b150b8405a5fdb7478413c74f0a7bf"
)
WAVE8_FLANDERS_FUNNEL_EVENT_CANDIDATE_ID_SHA256 = (
    "c821571928ccf2f116c853868c1f7e36c4b150b8405a5fdb7478413c74f0a7bf"
)


WAVE8_FLANDERS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Courtrai1302-1": {
        "actions": ["withhold_point"],
        "raw_point": [3.2577263, 50.8194776],
        "retained_country": "Belgium",
        "evidence_refs": [
            "wave8_flanders_lambert_memory",
            "wave8_flanders_verbruggen_golden_spurs",
        ],
        "reason": (
            "The staged Courtrai locality point is not a source-audited point "
            "for the formations and battlefield footprint on the Groeninge field."
        ),
    },
    "hced-Zieriksee1304-1": {
        "actions": ["withhold_point"],
        "raw_point": [3.9184977, 51.6501218],
        "retained_country": "Netherlands",
        "evidence_refs": [
            "wave8_flanders_sayers_zierikzee",
            "wave8_flanders_zierikzee_heritage",
        ],
        "reason": (
            "A city locality point cannot represent the naval battle, siege, "
            "relief approaches, and fighting across the Gouwe channel."
        ),
    },
    "hced-Mons-en-Pevele1304-1": {
        "actions": ["withhold_point"],
        "raw_point": [3.099575, 50.480352],
        "retained_country": "France",
        "evidence_refs": [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_somme_devries_review",
        ],
        "reason": (
            "The commune coordinate is not an audited point for the camps, "
            "successive attacks, withdrawals, and full battlefield footprint."
        ),
    },
    "hced-Cassel1328-1": {
        "actions": ["withhold_point"],
        "raw_point": [2.486235, 50.8000619],
        "retained_country": "France",
        "evidence_refs": [
            "wave8_flanders_france_culture_cassel",
            "wave8_flanders_tebrake_insurrection",
        ],
        "reason": (
            "The Cassel town coordinate is not an audited point for the French "
            "camp, rebel assault, rout, and pursuit across the surrounding terrain."
        ),
    },
}
WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_FLANDERS_LOCATION_QUARANTINE_REASONS
)
WAVE8_FLANDERS_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_FLANDERS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_FLANDERS_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Bruges1302-1": {
        "disposition": "related_distinct_hced_event",
        "raw_row_sha256": _RELATED_ROW_HASHES["hced-Bruges1302-1"],
        "relation": (
            "Bruges Matins is a distinct uprising episode and remains owned by "
            "the exact Flemish Rebels label lane, not this battle inventory."
        ),
        "evidence_refs": [
            "wave8_flanders_lambert_memory",
            "wave8_flanders_verbruggen_golden_spurs",
        ],
    },
    _FURNES_CANDIDATE_ID: {
        "disposition": "related_distinct_existing_release_event",
        "raw_row_sha256": _RELATED_ROW_HASHES[_FURNES_CANDIDATE_ID],
        "owner_event_id": _FURNES_RELEASE_EVENT_ID,
        "owner_entity_id": _COUNTY_OF_FLANDERS_ENTITY_ID,
        "relation": (
            "Furnes 1297 is a separate earlier engagement already released by "
            "the medieval label resolver and is not a duplicate of these four rows."
        ),
        "evidence_refs": [
            "wave8_flanders_cambridge_dampierres",
            "wave8_flanders_devries_infantry",
        ],
    },
}


WAVE8_FLANDERS_ADJACENT_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "france": {
        "disposition": "shared_raw_counterpart_but_event_bounded_identities",
        "candidate_ids": sorted(WAVE8_FLANDERS_CONTRACT_IDS),
        "forbidden_generic_entity_ids": ["kingdom_france"],
        "evidence_refs": [
            "wave8_flanders_devries_infantry",
            "wave8_flanders_larousse_philip_iv",
            "wave8_flanders_larousse_philip_vi",
        ],
        "note": (
            "Philip IV's Capetian forces and Philip VI's Valois intervention "
            "are separate bounded formations; no generic France rating is reused."
        ),
    },
    "medieval_county_of_flanders": {
        "disposition": "related_identity_not_a_candidate_owner",
        "candidate_ids": sorted(WAVE8_FLANDERS_CONTRACT_IDS),
        "existing_entity_id": _COUNTY_OF_FLANDERS_ENTITY_ID,
        "related_existing_event_id": _FURNES_RELEASE_EVENT_ID,
        "evidence_refs": [
            "wave8_flanders_cambridge_dampierres",
            "wave8_flanders_cambridge_low_countries",
        ],
        "note": (
            "The generic County of Flanders interval is not substituted for "
            "communal rebels, a comital fleet, or the 1328 rebels."
        ),
    },
    "burgundy": {
        "disposition": "outside_identity_window",
        "candidate_ids": sorted(WAVE8_FLANDERS_CONTRACT_IDS),
        "burgundian_flanders_start_year": 1384,
        "evidence_refs": [
            "wave8_flanders_cambridge_dampierres",
            "wave8_flanders_cambridge_low_countries",
        ],
        "note": (
            "All four events predate the 1384 Burgundian succession; no "
            "Burgundian actor or inherited rating is admitted."
        ),
    },
    "dutch": {
        "disposition": "medieval_holland_zeeland_not_dutch_republic",
        "candidate_ids": ["hced-Zieriksee1304-1"],
        "evidence_refs": [
            "wave8_flanders_cambridge_low_countries",
            "wave8_flanders_sayers_zierikzee",
        ],
        "note": (
            "The 1304 Holland-Zeeland force is event bounded and receives no "
            "continuity to the much later Dutch Republic or Netherlands."
        ),
    },
}
WAVE8_FLANDERS_CROSS_LANE_DISPOSITIONS = (
    WAVE8_FLANDERS_ADJACENT_LANE_DISPOSITIONS
)
WAVE8_FLANDERS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_FLANDERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_FLANDERS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"related_hced:{key}": value
        for key, value in WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS.items()
    },
    **{
        f"cross_lane:{key}": value
        for key, value in WAVE8_FLANDERS_CROSS_LANE_DISPOSITIONS.items()
    },
}


def _duplicate_audit(year: int, *aliases: str) -> dict[str, Any]:
    return {
        "aliases": sorted(set(map(normalize_label, aliases))),
        "years": [year, year],
    }


WAVE8_FLANDERS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Courtrai1302-1": _duplicate_audit(
        1302,
        "Battle of Courtrai",
        "Battle of Kortrijk",
        "Battle of the Golden Spurs",
        "Courtrai",
        "Golden Spurs",
        "Kortrijk",
    ),
    "hced-Zieriksee1304-1": _duplicate_audit(
        1304,
        "Battle of Zieriksee",
        "Battle of Zierikzee",
        "Naval Battle of Zierikzee",
        "Slag op de Gouwe",
        "Zieriksee",
        "Zierikzee",
    ),
    "hced-Mons-en-Pevele1304-1": _duplicate_audit(
        1304,
        "Battle of Mons-en-Pevele",
        "Battle of Mons-en-Pévèle",
        "Battle of Pevelenberg",
        "Mons-en-Pevele",
        "Mons-en-Pévèle",
        "Pevelenberg",
    ),
    "hced-Cassel1328-1": _duplicate_audit(
        1328,
        "Battle of Cassel",
        "Battle of Cassel (1328)",
        "Battle of Kassel",
        "Cassel",
        "Cassel 1328",
        "Kassel",
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_lane_dispositions": WAVE8_FLANDERS_ADJACENT_LANE_DISPOSITIONS,
        "contracts": WAVE8_FLANDERS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_FLANDERS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_FLANDERS_ENTITIES,
        "exact_candidate_id_sha256": WAVE8_FLANDERS_EXACT_CANDIDATE_ID_SHA256,
        "existing_release_duplicate_dispositions": (
            WAVE8_FLANDERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_FLANDERS_HOLDS,
        "integration_dispositions": WAVE8_FLANDERS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_FLANDERS_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_FLANDERS_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_FLANDERS_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_FLANDERS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS,
        "sources": WAVE8_FLANDERS_SOURCES,
        "terminal_exclusions": WAVE8_FLANDERS_TERMINAL_EXCLUSIONS,
    }


def wave8_flanders_audit_signature() -> str:
    """Return the immutable digest of the complete exact-label adjudication."""

    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


WAVE8_FLANDERS_FINAL_AUDIT_SIGNATURE = (
    "034bfa92592342b07bfe8eed76ef2663063c7a2f7d2d165f952247c02458a0f3"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(map(str, values)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_FLANDERS_CONTRACTS),
        len(WAVE8_FLANDERS_HOLDS),
        len(WAVE8_FLANDERS_TERMINAL_EXCLUSIONS),
    ) != (4, 0, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_FLANDERS_ENTITIES), len(WAVE8_FLANDERS_SOURCES)) != (9, 15):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_FLANDERS_RESERVED_IDS != WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    if WAVE8_FLANDERS_EXCLUSIONS is not WAVE8_FLANDERS_TERMINAL_EXCLUSIONS:
        raise ValueError(f"{_LANE_NAME} exclusion alias drifted")
    if WAVE8_FLANDERS_NONPROMOTIONS:
        raise ValueError(f"{_LANE_NAME} acquired an unaudited nonpromotion")
    if (
        _sorted_newline_sha256(WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS)
        != WAVE8_FLANDERS_EXACT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} candidate-ID signature changed")
    if wave8_flanders_audit_signature() != WAVE8_FLANDERS_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_FLANDERS_SOURCES
    }
    if len(source_by_id) != len(WAVE8_FLANDERS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({source["source_family_id"] for source in WAVE8_FLANDERS_SOURCES}) != 15:
        raise ValueError(f"{_LANE_NAME} source-family inventory changed")
    for source in WAVE8_FLANDERS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_FLANDERS_ENTITIES
    }
    if len(entity_by_id) != len(WAVE8_FLANDERS_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "belgium",
        "burgundy",
        "county of flanders",
        "dutch republic",
        "flanders",
        "france",
        "netherlands",
    }
    for entity in WAVE8_FLANDERS_ENTITIES:
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} identity is not event bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic identity")
        note = str(entity["continuity_note"]).casefold()
        for phrase in (
            "no rating is inherited",
            "county of flanders",
            "burgundian",
            "dutch republic",
        ):
            if phrase not in note:
                raise ValueError(f"{_LANE_NAME} identity boundary note drifted")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_FLANDERS_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_FLANDERS_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} side inventory is not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unbounded identity")
        used_entities.update(set(side_1) | set(side_2))
        year = int(canonical["year_low"])
        for entity_id in set(side_1) | set(side_2):
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
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
            len(outcomes) < 3
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
            {_SOURCE_FAMILY_BY_ID[source_id] for source_id in outcomes}
        )
        if families != expected_families or len(families) < 3:
            raise ValueError(f"{_LANE_NAME} outcome source families drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded identities are not exactly consumed")
    if WAVE8_FLANDERS_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} acquired an outcome override")

    if WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS != WAVE8_FLANDERS_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_FLANDERS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_FLANDERS_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_FLANDERS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    for candidate_id, review in WAVE8_FLANDERS_LOCATION_QUARANTINE_REASONS.items():
        if review["actions"] != ["withhold_point"] or not review["reason"]:
            raise ValueError(f"{_LANE_NAME} location action drifted")
        refs = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence drifted")
        used_sources.update(refs)
        if candidate_id not in WAVE8_FLANDERS_CONTRACT_IDS:
            raise ValueError(f"{_LANE_NAME} quarantines a nonpromotion")

    if set(WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS) != set(_RELATED_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} related HCED inventory changed")
    for candidate_id, disposition in WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS.items():
        if disposition["raw_row_sha256"] != _RELATED_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} related HCED fingerprint drifted")
        refs = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} related HCED evidence drifted")
        used_sources.update(refs)

    if set(WAVE8_FLANDERS_ADJACENT_LANE_DISPOSITIONS) != {
        "burgundy",
        "dutch",
        "france",
        "medieval_county_of_flanders",
    }:
        raise ValueError(f"{_LANE_NAME} adjacent-lane audit changed")
    for disposition in WAVE8_FLANDERS_ADJACENT_LANE_DISPOSITIONS.values():
        if not set(disposition["candidate_ids"]) <= WAVE8_FLANDERS_CONTRACT_IDS:
            raise ValueError(f"{_LANE_NAME} adjacent lane claims an unknown row")
        refs = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(refs) or not set(refs) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} adjacent-lane evidence drifted")
        used_sources.update(refs)
    if (
        WAVE8_FLANDERS_ADJACENT_LANE_DISPOSITIONS["burgundy"][
            "burgundian_flanders_start_year"
        ]
        != 1384
    ):
        raise ValueError(f"{_LANE_NAME} Burgundian boundary drifted")

    used_sources.update(
        source_id
        for entity in WAVE8_FLANDERS_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if (
        WAVE8_FLANDERS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_FLANDERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty duplicate inventories changed")
    expected_integration = {
        **{
            f"related_hced:{key}": value
            for key, value in WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS.items()
        },
        **{
            f"cross_lane:{key}": value
            for key, value in WAVE8_FLANDERS_CROSS_LANE_DISPOSITIONS.items()
        },
    }
    if WAVE8_FLANDERS_INTEGRATION_DISPOSITIONS != expected_integration:
        raise ValueError(f"{_LANE_NAME} integration inventory changed")

    if set(WAVE8_FLANDERS_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_FLANDERS_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for candidate_id, audit in WAVE8_FLANDERS_IWBD_ZERO_OVERLAP_AUDIT.items():
        aliases = list(map(str, audit["aliases"]))
        years = list(map(int, audit["years"]))
        if not aliases or not _is_sorted_unique(aliases):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if any(alias != normalize_label(alias) for alias in aliases):
            raise ValueError(f"{_LANE_NAME} duplicate alias is not normalized")
        canonical = WAVE8_FLANDERS_CONTRACTS[candidate_id]["canonical_event"]
        if years != [int(canonical["year_low"]), int(canonical["year_high"])]:
            raise ValueError(f"{_LANE_NAME} duplicate year window drifted")
        if normalize_label(canonical["name"]) not in aliases:
            raise ValueError(f"{_LANE_NAME} canonical duplicate alias is missing")


def _is_exact_flanders_label(value: Any) -> bool:
    return normalize_label(value) == "flanders"


def validate_wave8_flanders_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all four exact-label rows and immutable queue fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_FLANDERS_CONTRACTS,
        WAVE8_FLANDERS_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_label_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_flanders_label(row.get("side_1_raw"))
        or _is_exact_flanders_label(row.get("side_2_raw"))
    }
    if exact_label_ids != WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact Flanders inventory changed: "
            f"{sorted(exact_label_ids)}"
        )
    return {
        "holds": len(WAVE8_FLANDERS_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_FLANDERS_TERMINAL_EXCLUSIONS),
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
        text = str(row.get(field) or "")
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4])
    return None


_DUPLICATE_MATCH_KEYS = {
    (year, alias)
    for audit in WAVE8_FLANDERS_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
}


def validate_wave8_flanders_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin adjacent ownership and fail closed on an unreviewed event twin."""

    validate_wave8_flanders_queue_contracts(hced_rows)
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, disposition in WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS.items():
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one related HCED row {candidate_id}, "
                f"found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} related HCED fingerprint changed")

    existing = list(existing_events)
    if existing:
        furnes_owners = [
            event
            for event in existing
            if str(event.get("id")) == _FURNES_RELEASE_EVENT_ID
            and str(event.get("hced_candidate_id")) == _FURNES_CANDIDATE_ID
        ]
        if len(furnes_owners) != 1:
            raise ValueError(f"{_LANE_NAME} Furnes release ownership changed")

    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS
        and (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if hced_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_matches}"
        )
    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if iwbd_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_matches}"
        )
    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if str(event.get("hced_candidate_id"))
        not in WAVE8_FLANDERS_CONTRACT_IDS
        and (_row_year(event), normalize_label(event.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): "
            f"{release_matches}"
        )
    return {
        "cross_lane_hced_dispositions": len(
            WAVE8_FLANDERS_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_FLANDERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "integration_dispositions": len(
            WAVE8_FLANDERS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_FLANDERS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_FLANDERS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "related_hced_dispositions": len(
            WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS
        ),
    }


def install_wave8_flanders_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_FLANDERS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_flanders_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_FLANDERS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_FLANDERS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_flanders_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_flanders_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_FLANDERS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_flanders_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_FLANDERS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_flanders_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_FLANDERS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_FLANDERS_CROSS_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_FLANDERS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_FLANDERS_HOLDS),
        "integration_dispositions": len(
            WAVE8_FLANDERS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_FLANDERS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_FLANDERS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_FLANDERS_ENTITIES),
        "new_sources": len(WAVE8_FLANDERS_SOURCES),
        "newly_rated_events": len(WAVE8_FLANDERS_CONTRACTS),
        "outcome_overrides": len(WAVE8_FLANDERS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_FLANDERS_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_FLANDERS_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(WAVE8_FLANDERS_EXPECTED_CANDIDATE_IDS),
        "terminal_exclusions": len(WAVE8_FLANDERS_TERMINAL_EXCLUSIONS),
    }


def wave8_flanders_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_FLANDERS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_FLANDERS_POINT_QUARANTINE_ADDITIONS,
    }
