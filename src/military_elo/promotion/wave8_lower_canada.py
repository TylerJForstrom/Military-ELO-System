"""Fail-closed exact audit of four Lower Canada Rebellion battles.

The HCED label ``Quebecois Rebels`` does not describe one continuous army.
This lane therefore rates only four fingerprinted tactical engagements.  It
uses one conflict-bounded colonial Crown force, three separately commanded
1837 Patriote formations, and the independently organized 1838 Freres
chasseurs.  Every identity is alias-free and no rating flows to the United
Kingdom, the Dominion or modern Canada, a political party, or a generic
Quebecois/Patriote identity.

All four HCED points are withheld because the reviewed official records do
not authenticate those exact coordinates; the modern geographic country
``Canada`` and its provenance remain.  Four Wikidata same-event records are
discovery-only.  Their empty winner arrays are unknown and never draws.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    expected_exact_hced_win_participants,
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_LOWER_CANADA_CONTRACT_IDS",
    "WAVE8_LOWER_CANADA_CONTRACTS",
    "WAVE8_LOWER_CANADA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_LOWER_CANADA_DISCOVERY_EXPECTED",
    "WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES",
    "WAVE8_LOWER_CANADA_DISCOVERY_TWINS",
    "WAVE8_LOWER_CANADA_ENTITIES",
    "WAVE8_LOWER_CANADA_EXPECTED_CANDIDATE_IDS",
    "WAVE8_LOWER_CANADA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_LOWER_CANADA_FUNNEL_AUDIT",
    "WAVE8_LOWER_CANADA_HOLDS",
    "WAVE8_LOWER_CANADA_INTEGRATION_DISPOSITIONS",
    "WAVE8_LOWER_CANADA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_LOWER_CANADA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_LOWER_CANADA_RESERVED_IDS",
    "WAVE8_LOWER_CANADA_ROW_HASHES",
    "WAVE8_LOWER_CANADA_SOURCES",
    "install_wave8_lower_canada_entities",
    "install_wave8_lower_canada_sources",
    "promote_wave8_lower_canada_contracts",
    "validate_wave8_lower_canada_current_artifact_state",
    "validate_wave8_lower_canada_discovery_dispositions",
    "validate_wave8_lower_canada_funnel",
    "validate_wave8_lower_canada_integration_dispositions",
    "validate_wave8_lower_canada_queue_contracts",
    "wave8_lower_canada_audit_signature",
    "wave8_lower_canada_cohort_counts",
    "wave8_lower_canada_counts",
    "wave8_lower_canada_location_quarantine_additions",
    "wave8_lower_canada_metadata",
)


_LANE_NAME = "Wave 8 exact Lower Canada Rebellion audit"
_MODULE_OWNER = "military_elo.promotion.wave8_lower_canada"
_EVENT_ID_PREFIX = "hced_wave8_lower_canada_"
_EXACT_LABEL = "quebecois rebels"
_GRANULARITY = "single_battle_in_lower_canada_rebellion"
_PARENT_CONFLICT_ID = "lower_canada_rebellions_1837_1838"

_CROWN_FORCE = "lower_canada_crown_suppression_force_1837_1838"
_SAINT_DENIS_FORCE = "wolfred_nelson_saint_denis_force_1837"
_SAINT_CHARLES_FORCE = "thomas_storrow_brown_saint_charles_force_1837"
_SAINT_EUSTACHE_FORCE = "jean_olivier_chenier_saint_eustache_force_1837"
_FRERES_CHASSEURS = "robert_nelson_freres_chasseurs_force_1838"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    direct_outcome: bool,
) -> dict[str, Any]:
    roles = {
        "identity_boundary_or_context_reference",
        "outcome_consistency_crosscheck",
    }
    if direct_outcome:
        roles.add("outcome")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-21",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_LOWER_CANADA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_lower_canada_dcb_brown",
        "BROWN, THOMAS STORROW",
        "https://www.biographi.ca/en/bio/brown_thomas_storrow_11E.html",
        "Dictionary of Canadian Biography, University of Toronto/Universite Laval",
        "scholarly_national_biography",
        "dictionary_canadian_biography",
        direct_outcome=False,
    ),
    _source(
        "wave8_lower_canada_dcb_chenier",
        "CHENIER, JEAN-OLIVIER",
        "https://www.biographi.ca/en/bio/chenier_jean_olivier_7E.html",
        "Dictionary of Canadian Biography, University of Toronto/Universite Laval",
        "scholarly_national_biography",
        "dictionary_canadian_biography",
        direct_outcome=True,
    ),
    _source(
        "wave8_lower_canada_dcb_hindenlang",
        "HINDENLANG, CHARLES",
        "https://www.biographi.ca/en/bio/hindenlang_charles_7E.html",
        "Dictionary of Canadian Biography, University of Toronto/Universite Laval",
        "scholarly_national_biography",
        "dictionary_canadian_biography",
        direct_outcome=True,
    ),
    _source(
        "wave8_lower_canada_dcb_nelson",
        "NELSON, WOLFRED",
        "https://www.biographi.ca/en/bio/nelson_wolfred_9F.html",
        "Dictionary of Canadian Biography, University of Toronto/Universite Laval",
        "scholarly_national_biography",
        "dictionary_canadian_biography",
        direct_outcome=True,
    ),
    _source(
        "wave8_lower_canada_dcb_wetherall",
        "WETHERALL, Sir GEORGE AUGUSTUS",
        "https://www.biographi.ca/en/bio/wetherall_george_augustus_9E.html",
        "Dictionary of Canadian Biography, University of Toronto/Universite Laval",
        "scholarly_national_biography",
        "dictionary_canadian_biography",
        direct_outcome=True,
    ),
    _source(
        "wave8_lower_canada_dnd_saint_denis",
        "La bataille de Saint-Denis, 1837",
        (
            "https://www.canada.ca/content/dam/themes/defence/caf/"
            "militaryhistory/dhh/reports/batailles-canadiennes/"
            "livre-bataille-saint-denis-1837-fr.pdf"
        ),
        "Directorate of History and Heritage, Department of National Defence Canada",
        "official_military_history_monograph",
        "canadian_military_history_battle_series",
        direct_outcome=True,
    ),
    _source(
        "wave8_lower_canada_parks_saint_eustache",
        "Saint-Eustache Church, Saint-Eustache, Quebec",
        (
            "https://www.canada.ca/en/parks-canada/news/2017/05/"
            "saint-eustache_churchsaint-eustachequebec.html"
        ),
        "Parks Canada",
        "official_commemorative_history",
        "parks_canada_saint_eustache",
        direct_outcome=True,
    ),
    _source(
        "wave8_lower_canada_rpcq_freres_chasseurs",
        "Societe des Freres chasseurs",
        (
            "https://www.patrimoine-culturel.gouv.qc.ca/detail.do?"
            "id=26388&methode=consulter&type=pge"
        ),
        "Repertoire du patrimoine culturel du Quebec",
        "official_cultural_heritage_history",
        "quebec_cultural_heritage_lower_canada_rebellions",
        direct_outcome=False,
    ),
    _source(
        "wave8_lower_canada_rpcq_odelltown",
        "Bataille d'Odelltown",
        (
            "https://www.patrimoine-culturel.gouv.qc.ca/detail.do?"
            "id=8728&methode=consulter&type=pge"
        ),
        "Repertoire du patrimoine culturel du Quebec",
        "official_cultural_heritage_history",
        "quebec_cultural_heritage_lower_canada_rebellions",
        direct_outcome=True,
    ),
    _source(
        "wave8_lower_canada_rpcq_saint_charles",
        "Bataille de Saint-Charles",
        (
            "https://www.patrimoine-culturel.gouv.qc.ca/rpcq/detail.do?"
            "id=25484&methode=consulter&type=pge"
        ),
        "Repertoire du patrimoine culturel du Quebec",
        "official_cultural_heritage_history",
        "quebec_cultural_heritage_lower_canada_rebellions",
        direct_outcome=True,
    ),
    _source(
        "wave8_lower_canada_rpcq_saint_denis",
        "Bataille de Saint-Denis",
        (
            "https://www.patrimoine-culturel.gouv.qc.ca/rpcq/detail.do?"
            "id=18523&methode=consulter&type=pge"
        ),
        "Repertoire du patrimoine culturel du Quebec",
        "official_cultural_heritage_history",
        "quebec_cultural_heritage_lower_canada_rebellions",
        direct_outcome=True,
    ),
    _source(
        "wave8_lower_canada_state_trials_1839",
        "Report of the State Trials before a General Court Martial at Montreal, 1838-9",
        "https://www.canadiana.ca/view/oocihm.40101",
        "Armour and Ramsay; Canadiana digitization",
        "digitized_primary_trial_record",
        "lower_canada_state_trials_1839",
        direct_outcome=False,
    ),
    _source(
        "wave8_lower_canada_vac_odelltown",
        "Battle of Odelltown National Historic Site",
        (
            "https://www.veterans.gc.ca/en/remembrance/memorials/canada/"
            "battlefield-odelltown"
        ),
        "Veterans Affairs Canada",
        "official_battlefield_record",
        "veterans_affairs_canada_odelltown",
        direct_outcome=False,
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_LOWER_CANADA_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start_year: int,
    end_year: int,
    source_ids: Iterable[str],
    continuity_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start_year,
        "end_year": end_year,
        "region": "Lower Canada (present-day Quebec, Canada)",
        "aliases": [],
        "predecessors": [],
        "continuity_note": continuity_note,
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_LOWER_CANADA_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _CROWN_FORCE,
        "Lower Canada Crown suppression force (1837-1838)",
        "conflict_bounded_colonial_government_force",
        1837,
        1838,
        _SOURCE_BY_ID,
        (
            "Conflict-bounded British regular, artillery, colonial loyal-volunteer, "
            "and militia components on the government side of the Lower Canada "
            "risings. Event contracts delimit the components actually engaged. "
            "The identity creates no continuity to the United Kingdom generally, "
            "Lower Canada outside the conflict, the Province or Dominion of Canada, "
            "modern Canada, or loyalist civilians."
        ),
    ),
    _entity(
        _SAINT_DENIS_FORCE,
        "Wolfred Nelson's Saint-Denis force (1837)",
        "event_bounded_rebel_defense_force",
        1837,
        1837,
        (
            "wave8_lower_canada_dcb_nelson",
            "wave8_lower_canada_dnd_saint_denis",
            "wave8_lower_canada_rpcq_saint_denis",
        ),
        (
            "Only Wolfred Nelson's armed Saint-Denis defenders and engaged armed "
            "reinforcements. It excludes unarmed civilians, the political Parti "
            "patriote, the separately commanded Saint-Charles and Saint-Eustache "
            "forces, and every 1838 formation."
        ),
    ),
    _entity(
        _SAINT_CHARLES_FORCE,
        "Thomas Storrow Brown's Saint-Charles force (1837)",
        "event_bounded_rebel_camp",
        1837,
        1837,
        (
            "wave8_lower_canada_dcb_brown",
            "wave8_lower_canada_dcb_wetherall",
            "wave8_lower_canada_rpcq_saint_charles",
        ),
        (
            "Only Thomas Storrow Brown's entrenched Saint-Charles camp and armed "
            "defenders. It has no continuity from Nelson's or Chenier's separately "
            "commanded formations, a political party, or a generic Patriote actor."
        ),
    ),
    _entity(
        _SAINT_EUSTACHE_FORCE,
        "Jean-Olivier Chenier's Saint-Eustache force (1837)",
        "event_bounded_rebel_defense_force",
        1837,
        1837,
        (
            "wave8_lower_canada_dcb_chenier",
            "wave8_lower_canada_dcb_wetherall",
            "wave8_lower_canada_parks_saint_eustache",
        ),
        (
            "Only Jean-Olivier Chenier's locally commanded Saint-Eustache force. "
            "It excludes Girod's separately organized men and has no continuity "
            "to other Patriote camps, the political movement, or the 1838 rising."
        ),
    ),
    _entity(
        _FRERES_CHASSEURS,
        "Robert Nelson's Freres chasseurs force (1838)",
        "conflict_bounded_paramilitary_force",
        1838,
        1838,
        (
            "wave8_lower_canada_dcb_hindenlang",
            "wave8_lower_canada_rpcq_freres_chasseurs",
            "wave8_lower_canada_rpcq_odelltown",
            "wave8_lower_canada_state_trials_1839",
            "wave8_lower_canada_vac_odelltown",
        ),
        (
            "The army-model Freres chasseurs organization under Robert Nelson in "
            "the 1838 rising, bounded here to its Odelltown force. It inherits no "
            "rating from any separately commanded 1837 Patriote formation and is "
            "not a generic Quebecois, French-Canadian, or rebel identity."
        ),
    ),
)

_ENTITY_BY_ID = {
    str(entity["id"]): entity for entity in WAVE8_LOWER_CANADA_ENTITIES
}


WAVE8_LOWER_CANADA_ROW_HASHES: dict[str, str] = {
    "hced-Odelltown1838-1": (
        "644eb772027a9e7792adf559e91d8ca12956a829a6ab923bef0fcb90aca9df96"
    ),
    "hced-St Charles, Quebec1837-1": (
        "f668d63b5a94ced666576e36d99b88bea4ea183f4975da88297b8c5d26a93df0"
    ),
    "hced-St Denis, Quebec1837-1": (
        "6fb079ad496b4510d7c1e3fbac32a503462d8b8487340792fb90743e70b673de"
    ),
    "hced-St Eustache1837-1": (
        "0e5934860263ed51760fa0e9e7315d02cc1ed485d70b4760115f86557705a16e"
    ),
}
WAVE8_LOWER_CANADA_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_LOWER_CANADA_ROW_HASHES
)


WAVE8_LOWER_CANADA_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "25cc0516d7c40028a102d9ea2d74ffdb922799d69169870c7d375b3257de314c"
    ),
    "events_touched": 4,
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 4,
    },
    "label": _EXACT_LABEL,
    "rated_counterpart_entities": 1,
    "sole_blocker_events": 2,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 4,
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    exact_date: str,
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "day",
        "date_text": date_text,
        "end_date": exact_date,
        "granularity": _GRANULARITY,
        "name": name,
        "start_date": exact_date,
        "year_high": year,
        "year_low": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_id: str,
    side_2_entity_id: str,
    actor_override: str,
    evidence_refs: Iterable[str],
    date_source_ids: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    date_sources = sorted(set(map(str, date_source_ids)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    role_map: dict[str, list[str]] = {}
    for source_id in evidence:
        roles = {"exact_actor_boundary"}
        if source_id in date_sources:
            roles.add("exact_battle_date")
        if source_id in outcomes:
            roles.add("tactical_outcome")
        role_map[source_id] = sorted(roles)
    return {
        "raw_row_sha256": WAVE8_LOWER_CANADA_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "parent_conflict_id": _PARENT_CONFLICT_ID,
        "cohort": cohort,
        "side_1_entity_ids": [side_1_entity_id],
        "side_2_entity_ids": [side_2_entity_id],
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "internal_rebellion",
        "confidence": 0.96,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "event_evidence_roles": role_map,
        "date_source_ids": date_sources,
        "source_date_refinement": True,
        "source_date_override": False,
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": actor_override,
        "expected_scale_level": 1,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_LOWER_CANADA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Odelltown1838-1": _contract(
        "hced-Odelltown1838-1",
        _canonical(
            "Battle of Odelltown",
            1838,
            "9 November 1838",
            "1838-11-09",
        ),
        "lower_canada_rebellion_1838",
        _CROWN_FORCE,
        _FRERES_CHASSEURS,
        "taylor_odell_loyal_force_vs_nelson_freres_chasseurs",
        (
            "wave8_lower_canada_dcb_hindenlang",
            "wave8_lower_canada_rpcq_freres_chasseurs",
            "wave8_lower_canada_rpcq_odelltown",
            "wave8_lower_canada_state_trials_1839",
            "wave8_lower_canada_vac_odelltown",
        ),
        (
            "wave8_lower_canada_dcb_hindenlang",
            "wave8_lower_canada_rpcq_odelltown",
            "wave8_lower_canada_state_trials_1839",
            "wave8_lower_canada_vac_odelltown",
        ),
        (
            "wave8_lower_canada_dcb_hindenlang",
            "wave8_lower_canada_rpcq_odelltown",
        ),
        (
            "Taylor, Odell, and McAllister's loyal militia and reinforcements "
            "defeated Robert Nelson, Medard Hebert, and Charles Hindenlang's "
            "Odelltown Freres chasseurs force. The raw United Kingdom label is "
            "not converted into a UK-regular-only or enduring state assertion."
        ),
    ),
    "hced-St Charles, Quebec1837-1": _contract(
        "hced-St Charles, Quebec1837-1",
        _canonical(
            "Battle of Saint-Charles",
            1837,
            "25 November 1837",
            "1837-11-25",
        ),
        "lower_canada_rebellion_1837",
        _CROWN_FORCE,
        _SAINT_CHARLES_FORCE,
        "wetherall_column_vs_brown_saint_charles_force",
        (
            "wave8_lower_canada_dcb_brown",
            "wave8_lower_canada_dcb_wetherall",
            "wave8_lower_canada_rpcq_saint_charles",
        ),
        (
            "wave8_lower_canada_dcb_brown",
            "wave8_lower_canada_rpcq_saint_charles",
        ),
        (
            "wave8_lower_canada_dcb_wetherall",
            "wave8_lower_canada_rpcq_saint_charles",
        ),
        (
            "Wetherall's British regular, artillery, and cavalry column defeated "
            "Thomas Storrow Brown's separate Saint-Charles camp. The raw Canada "
            "member and ca_canada_dominion candidate are anachronistic for 1837."
        ),
    ),
    "hced-St Denis, Quebec1837-1": _contract(
        "hced-St Denis, Quebec1837-1",
        _canonical(
            "Battle of Saint-Denis",
            1837,
            "23 November 1837",
            "1837-11-23",
        ),
        "lower_canada_rebellion_1837",
        _SAINT_DENIS_FORCE,
        _CROWN_FORCE,
        "wolfred_nelson_force_vs_gore_column",
        (
            "wave8_lower_canada_dcb_nelson",
            "wave8_lower_canada_dnd_saint_denis",
            "wave8_lower_canada_rpcq_saint_denis",
        ),
        (
            "wave8_lower_canada_dcb_nelson",
            "wave8_lower_canada_dnd_saint_denis",
            "wave8_lower_canada_rpcq_saint_denis",
        ),
        (
            "wave8_lower_canada_dcb_nelson",
            "wave8_lower_canada_dnd_saint_denis",
            "wave8_lower_canada_rpcq_saint_denis",
        ),
        (
            "Wolfred Nelson's armed Saint-Denis defenders forced Gore's British "
            "column to retreat after the single-day engagement. The unarmed "
            "civilian population is excluded from the rated actor."
        ),
    ),
    "hced-St Eustache1837-1": _contract(
        "hced-St Eustache1837-1",
        _canonical(
            "Battle of Saint-Eustache",
            1837,
            "14 December 1837",
            "1837-12-14",
        ),
        "lower_canada_rebellion_1837",
        _CROWN_FORCE,
        _SAINT_EUSTACHE_FORCE,
        "colborne_force_vs_chenier_saint_eustache_force",
        (
            "wave8_lower_canada_dcb_chenier",
            "wave8_lower_canada_dcb_wetherall",
            "wave8_lower_canada_parks_saint_eustache",
        ),
        (
            "wave8_lower_canada_dcb_chenier",
            "wave8_lower_canada_parks_saint_eustache",
        ),
        (
            "wave8_lower_canada_dcb_chenier",
            "wave8_lower_canada_parks_saint_eustache",
        ),
        (
            "Colborne's British regular, artillery, and loyal-volunteer force "
            "defeated Jean-Olivier Chenier's separately commanded local defenders. "
            "No strategic termination is inferred from the battle."
        ),
    ),
}


WAVE8_LOWER_CANADA_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_LOWER_CANADA_CONTRACT_IDS = frozenset(WAVE8_LOWER_CANADA_CONTRACTS)
WAVE8_LOWER_CANADA_RESERVED_IDS = WAVE8_LOWER_CANADA_CONTRACT_IDS


WAVE8_LOWER_CANADA_DISCOVERY_TWINS: dict[str, str] = {
    "hced-Odelltown1838-1": "Q2888006",
    "hced-St Charles, Quebec1837-1": "Q2889850",
    "hced-St Denis, Quebec1837-1": "Q2889862",
    "hced-St Eustache1837-1": "Q862220",
}
WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES: dict[str, str] = {
    "Q2888006": (
        "017680f57e11d5a5cf7147e72f683d165dff76547b9beb19656bc790887f3860"
    ),
    "Q2889850": (
        "fcec2ee76c9450ed4c9ca29c80068a91d77ba0ffd9720c4c05474d07c8b91fb1"
    ),
    "Q2889862": (
        "4f5bd2157d311183adc4e15196801784195631fd8c70c40163b46759db294177"
    ),
    "Q862220": (
        "f818f33589748893106c806ffd2d18e9cce6bdb25e00ce143263f88c0edb6736"
    ),
}
WAVE8_LOWER_CANADA_DISCOVERY_EXPECTED: dict[str, dict[str, Any]] = {
    "Q2888006": {
        "date": "1838-11-09T00:00:00Z",
        "kind": "engagement",
        "name": "Battle of Odelltown",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": ["United Kingdom of Great Britain and Ireland"],
    },
    "Q2889850": {
        "date": "1837-11-25T00:00:00Z",
        "kind": "engagement",
        "name": "Battle of Saint-Charles",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [
            "Parti canadien",
            "United Kingdom of Great Britain and Ireland",
        ],
    },
    "Q2889862": {
        "date": "1837-11-23T00:00:00Z",
        "kind": "engagement",
        "name": "Battle of Saint-Denis",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": ["United Kingdom of Great Britain and Ireland"],
    },
    "Q862220": {
        "date": "1837-12-14T00:00:00Z",
        "kind": "engagement",
        "name": "Battle of Saint-Eustache",
        "outcome_disposition": "unknown_never_draw",
        "participant_labels": [
            "Patriote movement",
            "United Kingdom of Great Britain and Ireland",
        ],
    },
}
WAVE8_LOWER_CANADA_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    discovery_id: {
        "source_dataset": "wikidata-battles",
        "disposition": "discovery_only_duplicate",
        "hced_candidate_id": hced_id,
        "outcome_disposition": "unknown_never_draw",
    }
    for hced_id, discovery_id in sorted(WAVE8_LOWER_CANADA_DISCOVERY_TWINS.items())
}


WAVE8_LOWER_CANADA_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_LOWER_CANADA_CONTRACT_IDS
)
WAVE8_LOWER_CANADA_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()

_LOCATION_REASON_TEXT: dict[str, str] = {
    "hced-Odelltown1838-1": (
        "HCED's point is near the official church-centered battlefield locus, "
        "but no closed source authenticates that exact coordinate."
    ),
    "hced-St Charles, Quebec1837-1": (
        "HCED's point is several kilometres from the official battlefield site "
        "at 375 chemin des Patriotes."
    ),
    "hced-St Denis, Quebec1837-1": (
        "HCED's point is far from the independently documented Maison "
        "Jean-Baptiste-Masse battle locus."
    ),
    "hced-St Eustache1837-1": (
        "HCED's point is several kilometres from Saint-Eustache Church, the "
        "central defended position documented by Parks Canada."
    ),
}
WAVE8_LOWER_CANADA_LOCATION_QUARANTINE_REASONS: dict[
    str, dict[str, Any]
] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            f"{_LOCATION_REASON_TEXT[candidate_id]} Retain modern country Canada "
            "and location provenance; do not substitute a new point silently."
        ),
        "evidence_refs": sorted(contract["evidence_refs"]),
    }
    for candidate_id, contract in sorted(WAVE8_LOWER_CANADA_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_LOWER_CANADA_CONTRACTS,
        "discovery_expected": WAVE8_LOWER_CANADA_DISCOVERY_EXPECTED,
        "discovery_row_hashes": WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES,
        "discovery_twins": WAVE8_LOWER_CANADA_DISCOVERY_TWINS,
        "entities": WAVE8_LOWER_CANADA_ENTITIES,
        "funnel": WAVE8_LOWER_CANADA_FUNNEL_AUDIT,
        "holds": WAVE8_LOWER_CANADA_HOLDS,
        "integration_dispositions": WAVE8_LOWER_CANADA_INTEGRATION_DISPOSITIONS,
        "location_reasons": WAVE8_LOWER_CANADA_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_LOWER_CANADA_ROW_HASHES,
        "sources": WAVE8_LOWER_CANADA_SOURCES,
    }


def wave8_lower_canada_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_LOWER_CANADA_FINAL_AUDIT_SIGNATURE = (
    "38f50ee9d547513a8960cc748f2b719fcf572c1ec1a4f483f390d7be52bc195b"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = set(_ENTITY_BY_ID)
    if len(source_ids) != len(WAVE8_LOWER_CANADA_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if len(entity_ids) != len(WAVE8_LOWER_CANADA_ENTITIES):
        raise ValueError(f"{_LANE_NAME} duplicate entity id")
    if entity_ids != {
        _CROWN_FORCE,
        _SAINT_DENIS_FORCE,
        _SAINT_CHARLES_FORCE,
        _SAINT_EUSTACHE_FORCE,
        _FRERES_CHASSEURS,
    }:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_LOWER_CANADA_RESERVED_IDS != WAVE8_LOWER_CANADA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_LOWER_CANADA_HOLDS:
        raise ValueError(f"{_LANE_NAME} unexpected hold inventory")
    if (
        WAVE8_LOWER_CANADA_POINT_QUARANTINE_ADDITIONS
        != WAVE8_LOWER_CANADA_CONTRACT_IDS
        or WAVE8_LOWER_CANADA_COUNTRY_QUARANTINE_ADDITIONS
        or set(WAVE8_LOWER_CANADA_LOCATION_QUARANTINE_REASONS)
        != WAVE8_LOWER_CANADA_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location quarantine drift")

    for source_id, source in _SOURCE_BY_ID.items():
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} non-canonical source URL: {source_id}")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source role order drift: {source_id}")

    expected_entity_shape = {
        _CROWN_FORCE: (1837, 1838, "conflict_bounded_colonial_government_force"),
        _SAINT_DENIS_FORCE: (1837, 1837, "event_bounded_rebel_defense_force"),
        _SAINT_CHARLES_FORCE: (1837, 1837, "event_bounded_rebel_camp"),
        _SAINT_EUSTACHE_FORCE: (
            1837,
            1837,
            "event_bounded_rebel_defense_force",
        ),
        _FRERES_CHASSEURS: (1838, 1838, "conflict_bounded_paramilitary_force"),
    }
    forbidden_aliases = {
        "canada",
        "french canadians",
        "parti canadien",
        "parti patriote",
        "patriote movement",
        "patriotes",
        "quebec",
        "quebecois rebels",
        "united kingdom",
    }
    for entity_id, entity in _ENTITY_BY_ID.items():
        expected_start, expected_end, expected_kind = expected_entity_shape[entity_id]
        if (
            entity["start_year"],
            entity["end_year"],
            entity["kind"],
        ) != (expected_start, expected_end, expected_kind):
            raise ValueError(f"{_LANE_NAME} identity boundary drift: {entity_id}")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity continuity shortcut: {entity_id}")
        if not set(map(str, entity["source_ids"])) <= source_ids:
            raise ValueError(f"{_LANE_NAME} entity source closure drift: {entity_id}")
        if {
            normalize_label(alias) for alias in entity["aliases"]
        } & forbidden_aliases:
            raise ValueError(f"{_LANE_NAME} forbidden broad alias: {entity_id}")

    expected_contracts = {
        "hced-Odelltown1838-1": (
            "Battle of Odelltown",
            1838,
            "9 November 1838",
            "1838-11-09",
            [_CROWN_FORCE],
            [_FRERES_CHASSEURS],
        ),
        "hced-St Charles, Quebec1837-1": (
            "Battle of Saint-Charles",
            1837,
            "25 November 1837",
            "1837-11-25",
            [_CROWN_FORCE],
            [_SAINT_CHARLES_FORCE],
        ),
        "hced-St Denis, Quebec1837-1": (
            "Battle of Saint-Denis",
            1837,
            "23 November 1837",
            "1837-11-23",
            [_SAINT_DENIS_FORCE],
            [_CROWN_FORCE],
        ),
        "hced-St Eustache1837-1": (
            "Battle of Saint-Eustache",
            1837,
            "14 December 1837",
            "1837-12-14",
            [_CROWN_FORCE],
            [_SAINT_EUSTACHE_FORCE],
        ),
    }
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_LOWER_CANADA_CONTRACTS.items():
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["war_type"] != "internal_rebellion"
            or contract["parent_conflict_id"] != _PARENT_CONFLICT_ID
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
            or contract["source_date_override"]
            or contract["source_date_refinement"] is not True
            or float(contract["confidence"]) != 0.96
            or int(contract["expected_scale_level"]) != 1
        ):
            raise ValueError(f"{_LANE_NAME} contract disposition drift: {candidate_id}")
        name, year, date_text, exact_date, side_1, side_2 = expected_contracts[
            candidate_id
        ]
        canonical = contract["canonical_event"]
        if (
            canonical["canonical_key"] != f"{_slug(name)}:{year}:{year}"
            or canonical["name"] != name
            or canonical["date_precision"] != "day"
            or canonical["date_text"] != date_text
            or (canonical["start_date"], canonical["end_date"])
            != (exact_date, exact_date)
            or (canonical["year_low"], canonical["year_high"]) != (year, year)
            or canonical["granularity"] != _GRANULARITY
            or contract["side_1_entity_ids"] != side_1
            or contract["side_2_entity_ids"] != side_2
        ):
            raise ValueError(f"{_LANE_NAME} exact contract drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        date_sources = list(map(str, contract["date_source_ids"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or not _is_sorted_unique(date_sources)
            or not _is_sorted_unique(outcomes)
            or not set(date_sources) <= set(evidence)
            or not set(outcomes) <= set(evidence)
            or not set(evidence) <= source_ids
            or len(contract["outcome_source_family_ids"]) < 2
        ):
            raise ValueError(f"{_LANE_NAME} source closure drift: {candidate_id}")
        expected_families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract["outcome_source_family_ids"] != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        for source_id in outcomes:
            if "outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"]:
                raise ValueError(f"{_LANE_NAME} non-outcome source used: {source_id}")
        role_map = contract["event_evidence_roles"]
        if set(role_map) != set(evidence):
            raise ValueError(f"{_LANE_NAME} event source-role closure drift")
        for source_id, roles in role_map.items():
            if not _is_sorted_unique(roles) or not roles:
                raise ValueError(
                    f"{_LANE_NAME} event-specific role drift: "
                    f"{candidate_id}/{source_id}"
                )
        used_sources.update(evidence)
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    if set(WAVE8_LOWER_CANADA_DISCOVERY_TWINS) != WAVE8_LOWER_CANADA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} discovery owner drift")
    if set(WAVE8_LOWER_CANADA_DISCOVERY_TWINS.values()) != set(
        WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES
    ) or set(WAVE8_LOWER_CANADA_DISCOVERY_EXPECTED) != set(
        WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} discovery inventory drift")
    if any(
        expected["outcome_disposition"] != "unknown_never_draw"
        for expected in WAVE8_LOWER_CANADA_DISCOVERY_EXPECTED.values()
    ):
        raise ValueError(f"{_LANE_NAME} unknown-is-never-draw guard drift")
    if set(WAVE8_LOWER_CANADA_INTEGRATION_DISPOSITIONS) != set(
        WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} integration disposition drift")
    if (
        WAVE8_LOWER_CANADA_FINAL_AUDIT_SIGNATURE != "TO_BE_FILLED"
        and wave8_lower_canada_audit_signature()
        != WAVE8_LOWER_CANADA_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_lower_canada_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _EXACT_LABEL
        or normalize_label(row.get("side_2_raw")) == _EXACT_LABEL
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_LOWER_CANADA_RESERVED_IDS or len(exact) != len(
        exact_ids
    ):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    expected_raw = {
        "hced-Odelltown1838-1": (
            "United Kingdom",
            "Quebecois Rebels",
            "United Kingdom",
            "Quebecois Rebels",
            1838,
        ),
        "hced-St Charles, Quebec1837-1": (
            "United Kingdom, Canada",
            "Quebecois Rebels",
            "United Kingdom, Canada",
            "Quebecois Rebels",
            1837,
        ),
        "hced-St Denis, Quebec1837-1": (
            "Quebecois Rebels",
            "United Kingdom",
            "Quebecois Rebels",
            "United Kingdom",
            1837,
        ),
        "hced-St Eustache1837-1": (
            "United Kingdom, Canada",
            "Quebecois Rebels",
            "United Kingdom, Canada",
            "Quebecois Rebels",
            1837,
        ),
    }
    for candidate_id, expected_hash in WAVE8_LOWER_CANADA_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        side_1, side_2, winner, loser, year = expected_raw[candidate_id]
        if (
            row.get("side_1_raw"),
            row.get("side_2_raw"),
            row.get("winner_raw"),
            row.get("loser_raw"),
        ) != (side_1, side_2, winner, loser):
            raise ValueError(f"{_LANE_NAME} raw actor/outcome drift: {candidate_id}")
        if (
            row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != "No"
            or row.get("duplicate_source_id") is not False
            or row.get("do_not_rate_automatically") is not True
            or row.get("scale_raw") != "1"
            or row.get("modern_location_country") != "Canada"
            or row.get("theatre_raw") != "Land"
            or (row.get("year_low"), row.get("year_best"), row.get("year_high"))
            != (year, year, year)
        ):
            raise ValueError(f"{_LANE_NAME} locked queue row drift: {candidate_id}")
        if normalize_label(row.get("winner_raw")) in {
            "draw",
            "inconclusive",
            "stalemate",
            "unknown",
        }:
            raise ValueError(f"{_LANE_NAME} unknown/draw outcome drift: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_LOWER_CANADA_CONTRACTS,
        WAVE8_LOWER_CANADA_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_lower_canada_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    rows = [
        row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL
    ]
    if len(rows) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    row = rows[0]
    actual = {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "failure_cases": {
            key: int(row.get("failure_cases", {}).get(key, -1))
            for key in WAVE8_LOWER_CANADA_FUNNEL_AUDIT["failure_cases"]
        },
        "label": str(row.get("label")),
        "rated_counterpart_entities": int(row.get("rated_counterpart_entities", -1)),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, row.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
    }
    if actual != WAVE8_LOWER_CANADA_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pin changed: {actual}")
    return {
        "events_touched": actual["events_touched"],
        "sole_blocker_events": actual["sole_blocker_events"],
        "unresolved_side_attempts": actual["unresolved_side_attempts"],
        "zero_time_valid_candidates": actual["failure_cases"][
            "zero_time_valid_candidates"
        ],
    }


def _full_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def validate_wave8_lower_canada_discovery_dispositions(
    wikidata_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in wikidata_rows:
        by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, expected_hash in (
        WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} discovery row {candidate_id} expected once, "
                f"found {len(rows)}"
            )
        row = rows[0]
        if _full_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} discovery fingerprint changed: {candidate_id}")
        expected = WAVE8_LOWER_CANADA_DISCOVERY_EXPECTED[candidate_id]
        participant_labels = sorted(
            str(participant.get("label"))
            for participant in row.get("participants", [])
        )
        if (
            row.get("source") != "wikidata-battles"
            or row.get("do_not_rate_automatically") is not True
            or row.get("name") != expected["name"]
            or row.get("date") != expected["date"]
            or row.get("kind") != expected["kind"]
            or participant_labels != expected["participant_labels"]
            or row.get("winners") != []
        ):
            raise ValueError(
                f"{_LANE_NAME} discovery non-rating guard changed: {candidate_id}"
            )
    return {
        "discovery_nonrating_twins": len(WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES),
        "discovery_promotions": 0,
        "unknown_never_draw_rows": len(
            WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES
        ),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in (
        "year",
        "year_best",
        "year_low",
        "start_year",
        "year_start",
        "batyear",
    ):
        try:
            if row.get(key) is not None:
                return int(row[key])
        except (TypeError, ValueError):
            pass
    for key in ("start_date", "date"):
        value = str(row.get(key) or "")
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    values = [
        row.get("name"),
        row.get("battle_name"),
        row.get("batname"),
        row.get("event_name"),
    ]
    aliases = row.get("aliases", []) or []
    if isinstance(aliases, str):
        values.append(aliases)
    else:
        values.extend(aliases)
    return {normalize_label(value) for value in values if normalize_label(value)}


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Odelltown1838-1": {"Odelltown", "Battle of Odelltown"},
    "hced-St Charles, Quebec1837-1": {
        "St Charles, Quebec",
        "Saint-Charles",
        "Battle of Saint-Charles",
    },
    "hced-St Denis, Quebec1837-1": {
        "St Denis, Quebec",
        "Saint-Denis",
        "Battle of Saint-Denis",
    },
    "hced-St Eustache1837-1": {
        "St Eustache",
        "Saint-Eustache",
        "Battle of Saint-Eustache",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(WAVE8_LOWER_CANADA_CONTRACTS[candidate_id]["canonical_event"][
            "year_low"
        ]),
        normalize_label(alias),
    )
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
)
_EVENT_NAMES = frozenset(
    normalize_label(alias)
    for aliases in _EVENT_ALIASES.values()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    matched_names = _row_names(row) & _EVENT_NAMES
    if not matched_names:
        return False
    year = _row_year(row)
    if year is None:
        return True
    return any((year, name) in _DUPLICATE_MATCH_KEYS for name in matched_names)


def validate_wave8_lower_canada_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwd_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Prove exact discovery ownership and cross-source twin absence."""

    validate_wave8_lower_canada_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_LOWER_CANADA_RESERVED_IDS
        and _is_probable_twin(row)
    )
    iwd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwd_rows
        if _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    existing = list(existing_events)
    owned = [
        event
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_LOWER_CANADA_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    if owned:
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        if owned_ids != WAVE8_LOWER_CANADA_CONTRACT_IDS or len(owned) != len(
            owned_ids
        ):
            raise ValueError(f"{_LANE_NAME} current release ownership is partial")
        if any(
            not str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
            for event in owned
        ):
            raise ValueError(f"{_LANE_NAME} current release owner prefix changed")
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event not in owned and _is_probable_twin(event)
    )
    if hced_twins or iwd_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"iwd={iwd_twins}, iwbd={iwbd_twins}, release={release_twins}"
        )
    return {
        "discovery_nonrating_dispositions": len(
            WAVE8_LOWER_CANADA_INTEGRATION_DISPOSITIONS
        ),
        "existing_release_owned_events": len(owned),
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwd_probable_twins": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_lower_canada_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_LOWER_CANADA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_lower_canada_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_LOWER_CANADA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_LOWER_CANADA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_LOWER_CANADA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_lower_canada_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_lower_canada_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_LOWER_CANADA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def validate_wave8_lower_canada_current_artifact_state(
    release_events: Iterable[Mapping[str, Any]],
    release_entities: Iterable[Mapping[str, Any]],
    release_sources: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Require Lower Canada release artifacts to be wholly absent or complete."""

    _validate_static()
    events = list(release_events)
    owned = [
        event
        for event in events
        if event.get("hced_candidate_id") in WAVE8_LOWER_CANADA_RESERVED_IDS
        or str(event.get("id", "")).startswith(_EVENT_ID_PREFIX)
    ]
    entity_by_id = {
        str(entity.get("id")): entity
        for entity in release_entities
        if str(entity.get("id")) in _ENTITY_BY_ID
    }
    source_by_id = {
        str(source.get("id")): source
        for source in release_sources
        if str(source.get("id")) in _SOURCE_BY_ID
    }
    state_counts = (
        len(owned),
        len(entity_by_id),
        len(source_by_id),
    )
    absent = (0, 0, 0)
    complete = (
        len(WAVE8_LOWER_CANADA_CONTRACTS),
        len(WAVE8_LOWER_CANADA_ENTITIES),
        len(WAVE8_LOWER_CANADA_SOURCES),
    )
    if state_counts not in {absent, complete}:
        raise ValueError(
            f"{_LANE_NAME} current release artifacts are partial: {state_counts}"
        )
    if state_counts == absent:
        return {
            "artifact_state": "absent",
            "installed_entities": 0,
            "installed_sources": 0,
            "promoted_events": 0,
        }

    for entity_id, fixture in _ENTITY_BY_ID.items():
        entity = entity_by_id[entity_id]
        for key in (
            "name",
            "kind",
            "start_year",
            "end_year",
            "aliases",
            "predecessors",
            "source_ids",
        ):
            if entity.get(key) != fixture[key]:
                raise ValueError(
                    f"{_LANE_NAME} current release entity drift: {entity_id}/{key}"
                )
    for source_id, fixture in _SOURCE_BY_ID.items():
        if source_by_id[source_id] != fixture:
            raise ValueError(f"{_LANE_NAME} current release source drift: {source_id}")

    by_candidate = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_candidate) != WAVE8_LOWER_CANADA_CONTRACT_IDS or len(owned) != len(
        by_candidate
    ):
        raise ValueError(f"{_LANE_NAME} current release candidate inventory changed")
    for candidate_id, contract in WAVE8_LOWER_CANADA_CONTRACTS.items():
        event = by_candidate[candidate_id]
        canonical = contract["canonical_event"]
        year = int(canonical["year_low"])
        expected_id = f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        if (
            event.get("id") != expected_id
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year")) != (year, year)
            or event.get("event_type") != "engagement"
            or event.get("war_type") != "internal_rebellion"
            or event.get("scale") != "skirmish"
            or event.get("date_precision") != "day"
            or event.get("reviewed_granularity") != _GRANULARITY
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids")
            != contract["outcome_source_family_ids"]
            or float(event.get("confidence", -1.0)) != 0.96
        ):
            raise ValueError(f"{_LANE_NAME} current release event drift: {candidate_id}")
        expected_participants = expected_exact_hced_win_participants(
            contract["side_1_entity_ids"],
            contract["side_2_entity_ids"],
            confidence=0.96,
            scale_level=1,
            lane_name=_LANE_NAME,
        )
        if event.get("participants") != expected_participants:
            raise ValueError(
                f"{_LANE_NAME} current release participant drift: {candidate_id}"
            )
        if (
            "geometry" in event
            or event.get("modern_location_country") != "Canada"
            or "location_provenance" not in event
        ):
            raise ValueError(f"{_LANE_NAME} current release location drift: {candidate_id}")
    return {
        "artifact_state": "integrated",
        "installed_entities": len(entity_by_id),
        "installed_sources": len(source_by_id),
        "promoted_events": len(owned),
    }


def wave8_lower_canada_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_LOWER_CANADA_CONTRACTS.values(),
                    *WAVE8_LOWER_CANADA_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_lower_canada_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_LOWER_CANADA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "discovery_nonrating_twins": len(
            WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES
        ),
        "holds": len(WAVE8_LOWER_CANADA_HOLDS),
        "integration_dispositions": len(
            WAVE8_LOWER_CANADA_INTEGRATION_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_LOWER_CANADA_ENTITIES),
        "new_sources": len(WAVE8_LOWER_CANADA_SOURCES),
        "newly_rated_events": len(WAVE8_LOWER_CANADA_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_LOWER_CANADA_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_LOWER_CANADA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_LOWER_CANADA_RESERVED_IDS),
        "terminal_exclusions": 0,
        "unknown_discovery_outcomes": len(
            WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES
        ),
    }


def wave8_lower_canada_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_LOWER_CANADA_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_LOWER_CANADA_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_lower_canada_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_lower_canada_counts(),
        "cohorts": wave8_lower_canada_cohort_counts(),
        "final_audit_signature": WAVE8_LOWER_CANADA_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_LOWER_CANADA_CONTRACT_IDS),
        "hold_candidate_ids": [],
        "discovery_nonrating_candidate_ids": sorted(
            WAVE8_LOWER_CANADA_DISCOVERY_ROW_HASHES
        ),
    }


_validate_static()
