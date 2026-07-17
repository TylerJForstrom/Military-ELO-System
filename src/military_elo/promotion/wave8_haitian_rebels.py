"""Candidate-keyed Wave 8 audit for HCED's exact ``Haitian Rebels`` label.

The four locked rows do not describe one timeless Haitian polity.  Two rows
belong to Toussaint Louverture's autonomous Saint-Domingue army during the
first 1802 campaign against Leclerc.  The other two belong to Dessalines's
united Indigenous Army during the 1803 war of independence.  Neither actor is
the independent Haitian state proclaimed in 1804, either side of the Haitian
civil-war split after 1806, or a generic ethnic or rebel identity.

Only Port-au-Prince and Vertieres are promoted.  Their Indigenous Army
victories and opposing Rochambeau-command expedition are supported by
independent Haitian, archival, and scholarly sources.  Gonaives is HCED's
place-name for Ravine-a-Couleuvres, whose tactical winner is contradicted by
reputable Haitian and French accounts.  Crete-a-Perriot compresses repulsed
assaults, a successful defender breakout, and eventual French occupation of
the fort into one year-only record.  Both 1802 rows therefore remain unknown;
unknown is never converted into a draw.
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
    "WAVE8_HAITIAN_REBELS_CONTRACT_IDS",
    "WAVE8_HAITIAN_REBELS_CONTRACTS",
    "WAVE8_HAITIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_HAITIAN_REBELS_CROSS_LANE_DISPOSITIONS",
    "WAVE8_HAITIAN_REBELS_ENTITIES",
    "WAVE8_HAITIAN_REBELS_EXCLUSION_IDS",
    "WAVE8_HAITIAN_REBELS_EXCLUSIONS",
    "WAVE8_HAITIAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_HAITIAN_REBELS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_HAITIAN_REBELS_EXTERNAL_OWNER_DISPOSITIONS",
    "WAVE8_HAITIAN_REBELS_EXTERNAL_OWNER_IDS",
    "WAVE8_HAITIAN_REBELS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_HAITIAN_REBELS_FUNNEL_AUDIT",
    "WAVE8_HAITIAN_REBELS_HCED_DUPLICATE_DISPOSITIONS",
    "WAVE8_HAITIAN_REBELS_HOLD_IDS",
    "WAVE8_HAITIAN_REBELS_HOLDS",
    "WAVE8_HAITIAN_REBELS_INTEGRATION_DISPOSITIONS",
    "WAVE8_HAITIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_HAITIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_HAITIAN_REBELS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_HAITIAN_REBELS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_HAITIAN_REBELS_NONPROMOTIONS",
    "WAVE8_HAITIAN_REBELS_OUTCOME_OVERRIDES",
    "WAVE8_HAITIAN_REBELS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS",
    "WAVE8_HAITIAN_REBELS_RESERVED_IDS",
    "WAVE8_HAITIAN_REBELS_ROW_HASHES",
    "WAVE8_HAITIAN_REBELS_SOURCES",
    "WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSIONS",
    "install_wave8_haitian_rebels_entities",
    "install_wave8_haitian_rebels_sources",
    "promote_wave8_haitian_rebels_contracts",
    "validate_wave8_haitian_rebels_funnel",
    "validate_wave8_haitian_rebels_integration_dispositions",
    "validate_wave8_haitian_rebels_queue_contracts",
    "wave8_haitian_rebels_audit_signature",
    "wave8_haitian_rebels_cohort_counts",
    "wave8_haitian_rebels_counts",
    "wave8_haitian_rebels_location_quarantine_additions",
    "wave8_haitian_rebels_metadata",
)


_LANE_NAME = "Wave 8 exact Haitian Rebels actor audit"
_EVENT_ID_PREFIX = "hced_wave8_haitian_rebels_"
_MODULE_OWNER = "military_elo.promotion.wave8_haitian_rebels"
_EXACT_LABEL = "haitian rebels"


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
    if outcome and crosscheck:
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


WAVE8_HAITIAN_REBELS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_haitian_rebels_oxford_leclerc",
        "The Leclerc Expedition to Saint-Domingue and the Independence of Haiti, 1802-1804",
        "https://academic.oup.com/edited-volume/61800/chapter-abstract/546414970",
        "Oxford Research Encyclopedia of Latin American History",
        "scholarly_reference_chapter",
        "oxford_research_encyclopedia_leclerc_expedition",
    ),
    _source(
        "wave8_haitian_rebels_cambridge_defenders",
        "Defenders of Liberty: The Congos and the Question of African Agency in the Haitian Revolution",
        (
            "https://www.cambridge.org/core/journals/americas/article/"
            "defenders-of-liberty-the-congos-and-the-question-of-african-agency-"
            "in-the-haitian-revolution/4F0DAEF562FF70B55AD47135E376150C"
        ),
        "Cambridge University Press",
        "peer_reviewed_journal_article",
        "mobley_defenders_of_liberty",
    ),
    _source(
        "wave8_haitian_rebels_shd_leclerc_archive",
        "Saint-Domingue Expedition Leclerc (1802-1803)",
        "https://www.servicehistorique.sga.defense.gouv.fr/ark/489234",
        "Service historique de la Defense",
        "official_archival_collection_description",
        "shd_leclerc_expedition_archive",
    ),
    _source(
        "wave8_haitian_rebels_fondation_land_operations",
        "L'expedition de Saint-Domingue: les operations terrestres (fevrier-juin 1802)",
        (
            "https://www.napoleon.org/histoire-des-2-empires/articles/"
            "lexpedition-de-saint-domingue-les-operations-terrestres-fevrier-juin-1802/"
        ),
        "Fondation Napoleon",
        "scholarly_campaign_history",
        "fondation_napoleon_saint_domingue_land_operations",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haitian_rebels_fondation_santo_domingo",
        "Napoleon and Santo Domingo (Haiti and Santo Domingo)",
        (
            "https://www.napoleon.org/en/history-of-the-two-empires/articles/"
            "napoleon-the-dark-side-napoleon-and-santo-domingo-haiti-and-santo-"
            "domingo-4-min-read/"
        ),
        "Fondation Napoleon",
        "scholarly_campaign_synthesis",
        "fondation_napoleon_santo_domingo_synthesis",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haitian_rebels_ardouin_tome5",
        "Etudes sur l'histoire d'Haiti, Tome V, chapter 3",
        (
            "https://fr.wikisource.org/wiki/"
            "%C3%89tudes_sur_l%E2%80%99histoire_d%E2%80%99Ha%C3%AFti/Tome_5/5.3"
        ),
        "Dezobry et E. Magdeleine; Wikisource transcription",
        "haitian_historical_monograph",
        "beaubrun_ardouin_etudes_haiti_tome5",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haitian_rebels_ispan_crete",
        "La Crete-a-Pierrot, site de hauts faits d'armes",
        (
            "https://www.haiti.org/wp-content/uploads/2012/09/"
            "BULLETIN%20DE%20L%27ISPAN%20No%2022%20WEB.pdf"
        ),
        "Institut de Sauvegarde du Patrimoine National d'Haiti",
        "official_historic_site_bulletin",
        "ispan_bulletin_22_crete_a_pierrot",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haitian_rebels_dorsainvil_manual",
        "Manuel d'histoire d'Haiti",
        "https://beta-omk.manioc.org/files/original/2821/PAP11077.pdf",
        "Procure des Freres de l'Instruction Chretienne; Manioc",
        "haitian_historical_manual",
        "dorsainvil_manuel_histoire_haiti",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haitian_rebels_madiou_tome2",
        "Histoire d'Haiti, Tome II: 1799-1803",
        "https://cidihca.com/couvertures/LCID2744.pdf",
        "Editions Henri Deschamps; CIDIHCA",
        "haitian_historical_monograph",
        "thomas_madiou_histoire_haiti",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haitian_rebels_madiou_capitulation",
        "Capitulation du Cap (1803): episode de l'histoire d'Haiti",
        "https://www.manioc.org/en/patrimon/BBX19098",
        "Imprimerie de la Feuille du Commerce; Manioc",
        "haitian_near_contemporary_history",
        "thomas_madiou_histoire_haiti",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haitian_rebels_embassy_flag",
        "Flag and Coat of Arms: flags of Haiti, 1697-1986",
        "https://www.haiti.org/flag-and-coat-of-arms/",
        "Embassy of Haiti in the United States",
        "official_state_history",
        "haiti_embassy_flag_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haitian_rebels_government_vertieres",
        "18 novembre 1803: au nom de la liberte et de la dignite",
        (
            "https://communication.gouv.ht/in/18-novembre-1803-18-novembre-"
            "2020-au-nom-de-la-liberte-et-de-la-dignite/"
        ),
        "Government of the Republic of Haiti",
        "official_commemoration",
        "haiti_government_vertieres_commemoration",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_haitian_rebels_ispan_port_republicain",
        "Prise de possession du Port Republicain par l'armee indigene",
        (
            "https://ambassade-haiti.ca/wp-content/uploads/Patrimoine%20culturelle/"
            "HTML5/files/basic-html/page20.html"
        ),
        "Institut de Sauvegarde du Patrimoine National d'Haiti",
        "official_historic_site_bulletin",
        "ispan_bulletin_40_port_republicain",
        outcome=True,
        crosscheck=True,
    ),
)


_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_HAITIAN_REBELS_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    source_ids: Iterable[str],
    boundary_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": 1803,
        "end_year": 1803,
        "region": "French Saint-Domingue",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No rating is inherited from or transferred to Louverture's 1802 "
            "autonomous colonial army, a generic Haitian or French identity, the "
            "independent Haitian state proclaimed in 1804, or the northern and "
            "southern civil-war regimes and armies created after 1806."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_INDIGENOUS_ARMY_ID = "dessalines_indigenous_army_arcahaie_coalition_1803"
_FRENCH_EXPEDITION_ID = "rochambeau_saint_domingue_expedition_1803"


WAVE8_HAITIAN_REBELS_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _INDIGENOUS_ARMY_ID,
        "Dessalines's united Indigenous Army (1803)",
        "campaign_bounded_independence_army",
        [
            "wave8_haitian_rebels_cambridge_defenders",
            "wave8_haitian_rebels_dorsainvil_manual",
            "wave8_haitian_rebels_embassy_flag",
            "wave8_haitian_rebels_madiou_tome2",
            "wave8_haitian_rebels_oxford_leclerc",
        ],
        (
            "Bounded to the Black and free-coloured military coalition united "
            "under Dessalines in 1803 and represented at Port-au-Prince and "
            "Vertieres; it is not a retroactive name for Haiti before independence."
        ),
    ),
    _entity(
        _FRENCH_EXPEDITION_ID,
        "French Saint-Domingue expedition under Rochambeau (1803)",
        "campaign_and_command_bounded_colonial_expedition",
        [
            "wave8_haitian_rebels_dorsainvil_manual",
            "wave8_haitian_rebels_fondation_santo_domingo",
            "wave8_haitian_rebels_oxford_leclerc",
            "wave8_haitian_rebels_shd_leclerc_archive",
        ],
        (
            "Bounded to the expedition's Rochambeau-command phase in 1803, "
            "including Lavalette's Port-au-Prince garrison and Rochambeau's "
            "Vertieres force; it does not stand for France in other theatres."
        ),
    ),
)


WAVE8_HAITIAN_REBELS_ROW_HASHES: dict[str, str] = {
    "hced-Crete-a-Perriot1802-1": (
        "475b546926eed3714b697787d43ed5b58b3805b59c85408f9d9457322b539ea1"
    ),
    "hced-Gonaives1802-1": (
        "823cf0351421929b0ceddfa9ebe93d388f4fe34db3402033cb87bce96de651d4"
    ),
    "hced-Port-au-Prince1803-1": (
        "f8e6710adcdc1e997544feb0c1ab7e7c3381d81980ecb9fd4a5b6a596b4d4c16"
    ),
    "hced-Vertieres1803-1": (
        "616156618886ffae516e762ab30a9afe033045ec1d945c207b6a27930245deff"
    ),
}


WAVE8_HAITIAN_REBELS_FUNNEL_AUDIT: dict[str, Any] = {
    "event_candidate_id_sha256": (
        "f29f50e86e7f9a7bb36ee51b166d5efc4826578d50b546f92fb66182e700a078"
    ),
    "events_touched": 4,
    "failure_case": "zero_time_valid_candidates",
    "failure_case_count": 4,
    "label": _EXACT_LABEL,
    "marginal_events": 4,
    "newly_unblocked_candidate_id_sha256": (
        "f29f50e86e7f9a7bb36ee51b166d5efc4826578d50b546f92fb66182e700a078"
    ),
    "sole_blocker_events": 4,
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
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_HAITIAN_REBELS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": [_INDIGENOUS_ARMY_ID],
        "side_2_entity_ids": [_FRENCH_EXPEDITION_ID],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "regime_bounded_exact_opposing_forces",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_HAITIAN_REBELS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Port-au-Prince1803-1": _contract(
        "hced-Port-au-Prince1803-1",
        _canonical(
            "Siege and evacuation of Port-au-Prince (1803)",
            1803,
            "September-October 1803",
            date_precision="month_range",
            granularity="siege_and_city_evacuation",
        ),
        "dessalines_indigenous_army_1803",
        [
            "wave8_haitian_rebels_dorsainvil_manual",
            "wave8_haitian_rebels_embassy_flag",
            "wave8_haitian_rebels_ispan_port_republicain",
            "wave8_haitian_rebels_madiou_tome2",
            "wave8_haitian_rebels_oxford_leclerc",
        ],
        [
            "wave8_haitian_rebels_dorsainvil_manual",
            "wave8_haitian_rebels_ispan_port_republicain",
            "wave8_haitian_rebels_madiou_tome2",
        ],
        (
            "Dorsainvil describes Lavalette's capitulation after the Indigenous "
            "Army investment and the army's October entry; ISPAN independently "
            "records Indigenous Army possession. The bounded result is capture "
            "of the defended city, not every action around Port-au-Prince."
        ),
        confidence=0.82,
    ),
    "hced-Vertieres1803-1": _contract(
        "hced-Vertieres1803-1",
        _canonical(
            "Battle of Vertieres",
            1803,
            "18 November 1803",
            date_precision="day",
            granularity="engagement_and_fort_evacuation",
        ),
        "dessalines_indigenous_army_1803",
        [
            "wave8_haitian_rebels_dorsainvil_manual",
            "wave8_haitian_rebels_embassy_flag",
            "wave8_haitian_rebels_government_vertieres",
            "wave8_haitian_rebels_madiou_capitulation",
            "wave8_haitian_rebels_oxford_leclerc",
        ],
        [
            "wave8_haitian_rebels_dorsainvil_manual",
            "wave8_haitian_rebels_government_vertieres",
            "wave8_haitian_rebels_madiou_capitulation",
        ],
        (
            "Haitian official, Dorsainvil, and Madiou accounts converge on the "
            "Indigenous Army forcing evacuation of the Vertieres position and "
            "the ensuing French capitulation. The rating is the 18 November "
            "battle, not the whole revolution or the later independent state."
        ),
        confidence=0.86,
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    evidence_refs: Iterable[str],
    hold_reason: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_HAITIAN_REBELS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "disposition": "hold",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "hold_reason": hold_reason,
    }


WAVE8_HAITIAN_REBELS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Crete-a-Perriot1802-1": _hold(
        "hced-Crete-a-Perriot1802-1",
        _canonical(
            "Siege of Crete-a-Pierrot",
            1802,
            "4-24 March 1802",
            date_precision="day_range",
            granularity="multi_assault_siege_and_breakout",
        ),
        "louverture_autonomous_saint_domingue_army_1802",
        [
            "wave8_haitian_rebels_fondation_land_operations",
            "wave8_haitian_rebels_ispan_crete",
            "wave8_haitian_rebels_madiou_tome2",
            "wave8_haitian_rebels_shd_leclerc_archive",
        ],
        (
            "Not promoted: the year-only row merges French assaults repulsed by "
            "the garrison, Lamartiniere's successful breakout, and final French "
            "occupation of the abandoned fort. Those tactical endpoints do not "
            "support one unqualified winner; uncertainty is not a draw."
        ),
    ),
    "hced-Gonaives1802-1": _hold(
        "hced-Gonaives1802-1",
        _canonical(
            "Battle of Ravine-a-Couleuvres",
            1802,
            "23 February 1802",
            date_precision="day",
            granularity="engagement",
        ),
        "louverture_autonomous_saint_domingue_army_1802",
        [
            "wave8_haitian_rebels_ardouin_tome5",
            "wave8_haitian_rebels_dorsainvil_manual",
            "wave8_haitian_rebels_fondation_land_operations",
            "wave8_haitian_rebels_madiou_tome2",
        ],
        (
            "Not promoted: HCED's Gonaives record identifies Ravine-a-Couleuvres, "
            "but reputable accounts conflict over whether Toussaint held the "
            "field or Rochambeau forced his withdrawal. Selecting either tactical "
            "winner would invent certainty; the conflict is not encoded as a draw."
        ),
    ),
}


WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_HAITIAN_REBELS_EXCLUSIONS = WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSIONS
WAVE8_HAITIAN_REBELS_EXTERNAL_OWNER_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_HAITIAN_REBELS_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_HAITIAN_REBELS_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_HAITIAN_REBELS_HOLDS,
    **WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSIONS,
}

WAVE8_HAITIAN_REBELS_CONTRACT_IDS = frozenset(
    WAVE8_HAITIAN_REBELS_CONTRACTS
)
WAVE8_HAITIAN_REBELS_HOLD_IDS = frozenset(WAVE8_HAITIAN_REBELS_HOLDS)
WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSIONS
)
WAVE8_HAITIAN_REBELS_EXCLUSION_IDS = (
    WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSION_IDS
)
WAVE8_HAITIAN_REBELS_EXTERNAL_OWNER_IDS = frozenset(
    WAVE8_HAITIAN_REBELS_EXTERNAL_OWNER_DISPOSITIONS
)
WAVE8_HAITIAN_REBELS_RESERVED_IDS = frozenset(
    WAVE8_HAITIAN_REBELS_CONTRACT_IDS
    | WAVE8_HAITIAN_REBELS_HOLD_IDS
    | WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSION_IDS
)
WAVE8_HAITIAN_REBELS_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_HAITIAN_REBELS_ROW_HASHES
)


WAVE8_HAITIAN_REBELS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_HAITIAN_REBELS_CONTRACT_IDS
)
WAVE8_HAITIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_HAITIAN_REBELS_LOCATION_QUARANTINE_ADDITIONS = {
    "country": WAVE8_HAITIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
    "point": WAVE8_HAITIAN_REBELS_POINT_QUARANTINE_ADDITIONS,
}
WAVE8_HAITIAN_REBELS_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    "hced-Port-au-Prince1803-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_haitian_rebels_dorsainvil_manual",
            "wave8_haitian_rebels_ispan_port_republicain",
        ],
        "reason": (
            "HCED supplies a modern city point, while the reviewed event spans "
            "the siege lines, heights, forts, and evacuation of Port-au-Prince. "
            "Haiti is the correct modern country and remains published."
        ),
    },
    "hced-Vertieres1803-1": {
        "actions": ["withhold_point"],
        "evidence_refs": [
            "wave8_haitian_rebels_dorsainvil_manual",
            "wave8_haitian_rebels_government_vertieres",
        ],
        "reason": (
            "The staged coordinate is not independently authenticated to the "
            "reviewed fortification and assault footprint. Haiti is the correct "
            "modern country and remains published."
        ),
    },
}


WAVE8_HAITIAN_REBELS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_HAITIAN_REBELS_HCED_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_HAITIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_HAITIAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}


WAVE8_HAITIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Crete-a-Perriot1802-1": {
        "aliases": sorted(
            {
                "battle of crete a pierrot",
                "crete a perriot",
                "crete a pierrot",
                "siege of crete a pierrot",
            }
        ),
        "years": [1802, 1802],
    },
    "hced-Gonaives1802-1": {
        "aliases": sorted(
            {
                "battle of ravine a couleuvres",
                "gonaives",
                "ravine a couleuvres",
                "ravine aux couleuvres",
            }
        ),
        "years": [1802, 1802],
    },
    "hced-Port-au-Prince1803-1": {
        "aliases": sorted(
            {
                "port au prince",
                "siege and evacuation of port au prince 1803",
                "siege of port au prince",
            }
        ),
        "years": [1803, 1803],
    },
    "hced-Vertieres1803-1": {
        "aliases": sorted({"battle of vertieres", "vertieres"}),
        "years": [1803, 1803],
    },
}


WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {
    "hced-Azua1844-1": {
        "raw_row_sha256": (
            "2c59fbed65521ed79b5d5b6004c5275db64da25638db65d2f6d97fbae1b6c4cb"
        ),
        "disposition": "distinct_post_independence_haitian_state_campaign",
        "owner_module": None,
        "outcome_not_adjudicated": True,
        "boundary_note": "Dominican independence war; not the 1803 Indigenous Army.",
    },
    "hced-Cabeza de las Marias and las Hicoteas1844-1": {
        "raw_row_sha256": (
            "60efe67f6f9cff2c3305003890e4c01cc30ce90278fe010caa125266c99eb8b4"
        ),
        "disposition": "distinct_post_independence_haitian_state_campaign",
        "owner_module": None,
        "outcome_not_adjudicated": True,
        "boundary_note": "Dominican independence war; not the 1803 Indigenous Army.",
    },
    "hced-El Numero1849-1": {
        "raw_row_sha256": (
            "fac408e00c7ebe0beae2880f30a8640bfa254fd48dbcb5be557256b9b92d27a2"
        ),
        "disposition": "distinct_post_independence_haitian_state_campaign",
        "owner_module": None,
        "outcome_not_adjudicated": True,
        "boundary_note": "Later Soulouque-era campaign; not the 1803 Indigenous Army.",
    },
    "hced-Sabana Larga1856-1": {
        "raw_row_sha256": (
            "b1e041908f7fcf8f14bb28f203671a43c9929f485b7b2a3e737c1d2757dfc3cf"
        ),
        "disposition": "distinct_post_independence_haitian_state_campaign",
        "owner_module": None,
        "outcome_not_adjudicated": True,
        "boundary_note": "Later Soulouque-era campaign; not the 1803 Indigenous Army.",
    },
    "hced-Santo Domingo1802-1803-1": {
        "raw_row_sha256": (
            "557c799311d8310f1c7ce76107b663d802d3f30de1d873007169bf93ecd30082"
        ),
        "disposition": "distinct_british_french_naval_event",
        "owner_module": None,
        "outcome_not_adjudicated": True,
        "boundary_note": (
            "Same expedition period but a British-French naval record, not one "
            "of the four exact Haitian Rebels engagements."
        ),
    },
    "hced-Santo Domingo1805-1": {
        "raw_row_sha256": (
            "100b9326b4d08e44f7e10a2bc51ab70346637df2d57ffa692e551cf4033f36fe"
        ),
        "disposition": "distinct_post_independence_haitian_imperial_campaign",
        "owner_module": None,
        "outcome_not_adjudicated": True,
        "boundary_note": (
            "Dessalines's independent 1805 empire and Napoleon's First Empire "
            "are outside both 1802 and 1803 actor windows."
        ),
    },
}


WAVE8_HAITIAN_REBELS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    f"related_hced:{candidate_id}": dict(disposition)
    for candidate_id, disposition in sorted(
        WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS.items()
    )
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_HAITIAN_REBELS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_HAITIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_HAITIAN_REBELS_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_HAITIAN_REBELS_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_HAITIAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "external_owner_dispositions": (
            WAVE8_HAITIAN_REBELS_EXTERNAL_OWNER_DISPOSITIONS
        ),
        "funnel_audit": WAVE8_HAITIAN_REBELS_FUNNEL_AUDIT,
        "hced_duplicate_dispositions": (
            WAVE8_HAITIAN_REBELS_HCED_DUPLICATE_DISPOSITIONS
        ),
        "holds": WAVE8_HAITIAN_REBELS_HOLDS,
        "integration_dispositions": WAVE8_HAITIAN_REBELS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_HAITIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": WAVE8_HAITIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": (
            WAVE8_HAITIAN_REBELS_LOCATION_QUARANTINE_REASONS
        ),
        "outcome_overrides": WAVE8_HAITIAN_REBELS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_HAITIAN_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": (
            WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS
        ),
        "row_hashes": WAVE8_HAITIAN_REBELS_ROW_HASHES,
        "sources": WAVE8_HAITIAN_REBELS_SOURCES,
        "terminal_exclusions": WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSIONS,
    }


def wave8_haitian_rebels_audit_signature() -> str:
    """Return the immutable digest of the complete four-row adjudication."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_HAITIAN_REBELS_FINAL_AUDIT_SIGNATURE = (
    "3a9c3a7d8dd4c85de829abaff58bf11673346f7789a325357bff1b2596d5436b"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_HAITIAN_REBELS_CONTRACTS),
        len(WAVE8_HAITIAN_REBELS_HOLDS),
        len(WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSIONS),
        len(WAVE8_HAITIAN_REBELS_EXTERNAL_OWNER_DISPOSITIONS),
    ) != (2, 2, 0, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_HAITIAN_REBELS_ENTITIES), len(WAVE8_HAITIAN_REBELS_SOURCES)) != (
        2,
        13,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_HAITIAN_REBELS_RESERVED_IDS != (
        WAVE8_HAITIAN_REBELS_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} exact-label ownership is incomplete")
    dispositions = (
        WAVE8_HAITIAN_REBELS_CONTRACT_IDS,
        WAVE8_HAITIAN_REBELS_HOLD_IDS,
        WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSION_IDS,
        WAVE8_HAITIAN_REBELS_EXTERNAL_OWNER_IDS,
    )
    if any(
        dispositions[i] & dispositions[j]
        for i in range(len(dispositions))
        for j in range(i + 1, len(dispositions))
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if (
        wave8_haitian_rebels_audit_signature()
        != WAVE8_HAITIAN_REBELS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = dict(_SOURCE_BY_ID)
    if len(source_by_id) != len(WAVE8_HAITIAN_REBELS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({str(source["source_family_id"]) for source in source_by_id.values()}) < 12:
        raise ValueError(f"{_LANE_NAME} source-family independence weakened")
    for source in source_by_id.values():
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_HAITIAN_REBELS_ENTITIES
    }
    if set(entity_by_id) != {_INDIGENOUS_ARMY_ID, _FRENCH_EXPEDITION_ID}:
        raise ValueError(f"{_LANE_NAME} entity inventory changed")
    for entity in entity_by_id.values():
        if (entity["start_year"], entity["end_year"]) != (1803, 1803):
            raise ValueError(f"{_LANE_NAME} entity window drifted")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} opened a generic identity fallback")
        note = str(entity["continuity_note"]).casefold()
        if not all(
            phrase in note
            for phrase in ("no rating is inherited", "1802", "1804", "civil-war")
        ):
            raise ValueError(f"{_LANE_NAME} continuity boundary weakened")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_HAITIAN_REBELS_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_HAITIAN_REBELS_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row hash table drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if (
            canonical["canonical_key"] != expected_key
            or canonical["year_low"] != 1803
            or canonical["year_high"] != 1803
            or not canonical["date_text"]
        ):
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if side_1 != [_INDIGENOUS_ARMY_ID] or side_2 != [_FRENCH_EXPEDITION_ID]:
            raise ValueError(f"{_LANE_NAME} opposing actor boundary changed")
        used_entities.update(side_1 + side_2)
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or int(contract["winner_side"]) != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"]
            != "regime_bounded_exact_opposing_forces"
        ):
            raise ValueError(f"{_LANE_NAME} promotion semantics drifted")
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
            raise ValueError(f"{_LANE_NAME} outcome provenance weakened")
        expected_families = sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if families != expected_families or len(families) < 3:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        used_sources.update(evidence)
    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")

    for candidate_id, hold in WAVE8_HAITIAN_REBELS_HOLDS.items():
        if (
            hold["raw_row_sha256"] != WAVE8_HAITIAN_REBELS_ROW_HASHES[candidate_id]
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
        if "not promoted" not in reason or "draw" not in reason:
            raise ValueError(f"{_LANE_NAME} hold lost the no-draw policy")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} hold evidence drifted")
        used_sources.update(evidence)
    if "conflict" not in str(
        WAVE8_HAITIAN_REBELS_HOLDS["hced-Gonaives1802-1"]["hold_reason"]
    ).casefold():
        raise ValueError(f"{_LANE_NAME} Ravine contradiction disappeared")
    crete_reason = str(
        WAVE8_HAITIAN_REBELS_HOLDS["hced-Crete-a-Perriot1802-1"]["hold_reason"]
    ).casefold()
    if not all(phrase in crete_reason for phrase in ("assaults", "breakout", "occupation")):
        raise ValueError(f"{_LANE_NAME} Crete granularity boundary weakened")

    if (
        WAVE8_HAITIAN_REBELS_TERMINAL_EXCLUSIONS
        or WAVE8_HAITIAN_REBELS_EXTERNAL_OWNER_DISPOSITIONS
        or WAVE8_HAITIAN_REBELS_CROSS_LANE_DISPOSITIONS
        or WAVE8_HAITIAN_REBELS_OUTCOME_OVERRIDES
        or WAVE8_HAITIAN_REBELS_HCED_DUPLICATE_DISPOSITIONS
        or WAVE8_HAITIAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_HAITIAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} empty disposition inventory changed")
    if WAVE8_HAITIAN_REBELS_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_HAITIAN_REBELS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_HAITIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} acquired a country quarantine")
    if set(WAVE8_HAITIAN_REBELS_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_HAITIAN_REBELS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location review is incomplete")
    for review in WAVE8_HAITIAN_REBELS_LOCATION_QUARANTINE_REASONS.values():
        if review["actions"] != ["withhold_point"] or not review["reason"]:
            raise ValueError(f"{_LANE_NAME} location policy drifted")
        evidence = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence drifted")
        used_sources.update(evidence)

    if set(WAVE8_HAITIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_HAITIAN_REBELS_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for audit in WAVE8_HAITIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, audit["aliases"]))
        years = list(map(int, audit["years"]))
        if not aliases or not _is_sorted_unique(aliases):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
        if aliases != list(map(normalize_label, aliases)) or years != [years[0], years[0]]:
            raise ValueError(f"{_LANE_NAME} duplicate audit drifted")

    expected_related = {
        "hced-Azua1844-1",
        "hced-Cabeza de las Marias and las Hicoteas1844-1",
        "hced-El Numero1849-1",
        "hced-Sabana Larga1856-1",
        "hced-Santo Domingo1802-1803-1",
        "hced-Santo Domingo1805-1",
    }
    if set(WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS) != expected_related:
        raise ValueError(f"{_LANE_NAME} related identity audit changed")
    if set(WAVE8_HAITIAN_REBELS_INTEGRATION_DISPOSITIONS) != {
        f"related_hced:{candidate_id}" for candidate_id in expected_related
    }:
        raise ValueError(f"{_LANE_NAME} integration disposition inventory changed")

    used_sources.update(
        source_id
        for entity in WAVE8_HAITIAN_REBELS_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")


def _is_exact_label(value: Any) -> bool:
    return normalize_label(value) == _EXACT_LABEL


def validate_wave8_haitian_rebels_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin all and only the four exact-label rows and their dispositions."""

    _validate_static()
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_HAITIAN_REBELS_CONTRACTS,
        WAVE8_HAITIAN_REBELS_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_label(row.get("side_1_raw"))
        or _is_exact_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_HAITIAN_REBELS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact-label inventory changed: {sorted(exact_ids)}"
        )
    return {
        "external_owner_contracts": 0,
        "holds": len(WAVE8_HAITIAN_REBELS_HOLDS),
        "promotion_contracts": counts["promotion_contracts"],
        "reviewed_hced_rows": len(WAVE8_HAITIAN_REBELS_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def validate_wave8_haitian_rebels_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    """Pin the four-row unresolved-label funnel independently of outcomes."""

    _validate_static()
    labels = funnel.get("labels")
    if not isinstance(labels, list):
        raise ValueError(f"{_LANE_NAME} funnel labels are unavailable")
    matches = [item for item in labels if item.get("label") == _EXACT_LABEL]
    if len(matches) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label row")
    label = matches[0]
    for key in ("event_candidate_id_sha256", "events_touched", "sole_blocker_events"):
        if label.get(key) != WAVE8_HAITIAN_REBELS_FUNNEL_AUDIT[key]:
            raise ValueError(f"{_LANE_NAME} funnel {key} changed")
    failures = label.get("failure_cases")
    if not isinstance(failures, Mapping) or failures.get(
        "zero_time_valid_candidates"
    ) != 4:
        raise ValueError(f"{_LANE_NAME} funnel failure case changed")
    if label.get("candidate_ids") or label.get("time_valid_candidate_ids"):
        raise ValueError(f"{_LANE_NAME} unexpectedly acquired a generic identity")

    greedy = funnel.get("greedy_batch")
    ranking = greedy.get("ranking") if isinstance(greedy, Mapping) else None
    if not isinstance(ranking, list):
        raise ValueError(f"{_LANE_NAME} greedy ranking is unavailable")
    ranked = [item for item in ranking if item.get("label") == _EXACT_LABEL]
    if len(ranked) != 1:
        raise ValueError(f"{_LANE_NAME} expected one greedy ranking row")
    if (
        ranked[0].get("events_touched") != 4
        or ranked[0].get("marginal_events") != 4
        or ranked[0].get("newly_unblocked_candidate_id_sha256")
        != WAVE8_HAITIAN_REBELS_FUNNEL_AUDIT[
            "newly_unblocked_candidate_id_sha256"
        ]
    ):
        raise ValueError(f"{_LANE_NAME} greedy audit changed")

    row_data = funnel.get("row_label_data")
    if not isinstance(row_data, list):
        raise ValueError(f"{_LANE_NAME} row-label data are unavailable")
    audited: set[str] = set()
    for row in row_data:
        failures = row.get("label_failures")
        matching = (
            [item for item in failures if item.get("label") == _EXACT_LABEL]
            if isinstance(failures, list)
            else []
        )
        if matching:
            if (
                len(matching) != 1
                or matching[0].get("failure_case")
                != "zero_time_valid_candidates"
                or row.get("sole_blocker_label") != _EXACT_LABEL
            ):
                raise ValueError(f"{_LANE_NAME} row funnel boundary changed")
            audited.add(str(row.get("candidate_id")))
    if audited != WAVE8_HAITIAN_REBELS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} funnel cohort changed")
    return {"exact_label_rows": 4, "shared_label_rows": 0, "sole_blocker_rows": 4}


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
    for audit in WAVE8_HAITIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(audit["years"][0]), int(audit["years"][1]) + 1)
    for alias in map(str, audit["aliases"])
}


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {normalize_label(row.get("name"))}
    aliases = row.get("aliases")
    if isinstance(aliases, list):
        names.update(normalize_label(alias) for alias in aliases)
    return names - {""}


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_haitian_rebels_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on future twins and pin nearby Haiti/France lane boundaries."""

    validate_wave8_haitian_rebels_queue_contracts(hced_rows)
    hced_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        hced_by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, disposition in (
        WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS.items()
    ):
        rows = hced_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one related HCED row {candidate_id}, "
                f"found {len(rows)}"
            )
        if canonical_hced_row_sha256(rows[0]) != disposition["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} related HCED row changed: {candidate_id}")

    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_HAITIAN_REBELS_EXPECTED_CANDIDATE_IDS
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
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id")
        not in WAVE8_HAITIAN_REBELS_CONTRACT_IDS
        and _is_probable_twin(event)
    )
    if release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_twins}"
        )
    return {
        "cross_lane_hced_dispositions": 0,
        "existing_release_duplicate_dispositions": 0,
        "external_owner_hced_dispositions": 0,
        "hced_duplicate_dispositions": 0,
        "integration_dispositions": len(
            WAVE8_HAITIAN_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_HAITIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "related_hced_dispositions": len(
            WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS
        ),
    }


def install_wave8_haitian_rebels_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_HAITIAN_REBELS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_haitian_rebels_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_HAITIAN_REBELS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_HAITIAN_REBELS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_HAITIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_haitian_rebels_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_haitian_rebels_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_HAITIAN_REBELS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_haitian_rebels_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_HAITIAN_REBELS_CONTRACTS.values(),
                    *WAVE8_HAITIAN_REBELS_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_haitian_rebels_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "cross_lane_hced_dispositions": 0,
        "existing_release_duplicate_dispositions": 0,
        "external_owner_hced_dispositions": 0,
        "hced_duplicate_dispositions": 0,
        "holds": len(WAVE8_HAITIAN_REBELS_HOLDS),
        "integration_dispositions": len(
            WAVE8_HAITIAN_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_HAITIAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_HAITIAN_REBELS_ENTITIES),
        "new_sources": len(WAVE8_HAITIAN_REBELS_SOURCES),
        "newly_rated_events": len(WAVE8_HAITIAN_REBELS_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_HAITIAN_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_HAITIAN_REBELS_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS
        ),
        "reviewed_hced_rows": len(
            WAVE8_HAITIAN_REBELS_EXPECTED_CANDIDATE_IDS
        ),
        "terminal_exclusions": 0,
    }


def wave8_haitian_rebels_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_HAITIAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_HAITIAN_REBELS_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_haitian_rebels_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_haitian_rebels_counts(),
        "cohorts": wave8_haitian_rebels_cohort_counts(),
        "final_audit_signature": WAVE8_HAITIAN_REBELS_FINAL_AUDIT_SIGNATURE,
        "hold_ids": sorted(WAVE8_HAITIAN_REBELS_HOLD_IDS),
        "promoted_candidate_ids": sorted(WAVE8_HAITIAN_REBELS_CONTRACT_IDS),
        "related_hced_candidate_ids": sorted(
            WAVE8_HAITIAN_REBELS_RELATED_HCED_DISPOSITIONS
        ),
    }
