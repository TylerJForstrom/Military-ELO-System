"""Exact Wave 8 audit for HCED's generic ``Garibaldi's Redshirts`` rows.

The raw label spans unrelated forces in 1848, 1859, 1866, and 1867.  This
lane therefore uses campaign- or formation-bounded identities and never opens
a timeless Redshirts alias.  Palermo 1860 is intentionally outside this lane:
the Wave 8 Naples module owns that exact HCED candidate.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_GARIBALDI_CONTRACTS",
    "WAVE8_GARIBALDI_CONTRACT_IDS",
    "WAVE8_GARIBALDI_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_GARIBALDI_CROSS_LANE_DISPOSITIONS",
    "WAVE8_GARIBALDI_ENTITIES",
    "WAVE8_GARIBALDI_EXPECTED_CANDIDATE_IDS",
    "WAVE8_GARIBALDI_FINAL_AUDIT_SIGNATURE",
    "WAVE8_GARIBALDI_HOLDS",
    "WAVE8_GARIBALDI_HOLD_IDS",
    "WAVE8_GARIBALDI_INTEGRATION_DISPOSITIONS",
    "WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_GARIBALDI_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_GARIBALDI_OUTCOME_OVERRIDES",
    "WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_GARIBALDI_RESERVED_IDS",
    "WAVE8_GARIBALDI_SOURCES",
    "install_wave8_garibaldi_entities",
    "install_wave8_garibaldi_sources",
    "promote_wave8_garibaldi_contracts",
    "validate_wave8_garibaldi_integration_dispositions",
    "validate_wave8_garibaldi_queue_contracts",
    "wave8_garibaldi_audit_signature",
    "wave8_garibaldi_cohort_counts",
    "wave8_garibaldi_counts",
    "wave8_garibaldi_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Garibaldi formations"
_EVENT_ID_PREFIX = "hced_wave8_garibaldi_"
_AUSTRIAN_EMPIRE_ID = "austrian_empire"
_PAPAL_STATES_ID = "clio_it_papal_state_1_755_50394c66"
_PALERMO_NAPLES_OWNER_ID = "hced-Palermo1860-1"


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


WAVE8_GARIBALDI_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_garibaldi_guerzoni_1889",
        "Garibaldi, volume I (1807-1859)",
        "https://www.gutenberg.org/files/75122/75122-h/75122-h.htm",
        "Project Gutenberg transcription of Giuseppe Guerzoni's 1889 third edition",
        "digitized_near_contemporary_history_with_documents",
        "guerzoni_garibaldi_volume_1",
        crosscheck=True,
    ),
    _source(
        "wave8_garibaldi_treccani_garibaldi",
        "Garibaldi, Giuseppe",
        (
            "https://www.treccani.it/enciclopedia/"
            "giuseppe-garibaldi_%28Enciclopedia-Italiana%29/"
        ),
        "Istituto della Enciclopedia Italiana (Treccani)",
        "scholarly_encyclopedia",
        "treccani_garibaldi_enciclopedia_italiana",
        crosscheck=True,
    ),
    _source(
        "wave8_garibaldi_italian_army_1859_inventory",
        "Inventario della Miscellanea G-17: Campagna 1859",
        (
            "https://www.esercito.difesa.it/storia/Ufficio-Storico-SME/"
            "Documents/150312/G-17%20Inventario%20della%20Miscellanea%20G17%20"
            "Campagna%201859.pdf"
        ),
        "Italian Army Historical Office",
        "official_military_archival_finding_aid",
        "italian_army_historical_office_1859",
        outcome=False,
    ),
    _source(
        "wave8_garibaldi_italian_army_biography",
        "Giuseppe Garibaldi",
        "https://www.esercito.difesa.it/storia/giuseppe-garibaldi/83206.html",
        "Italian Army",
        "official_military_biography",
        "italian_army_garibaldi_biography",
    ),
    _source(
        "wave8_garibaldi_italian_army_rivista_2007",
        "L'opinione pubblica e l'Esercito dall'Unità d'Italia ai giorni nostri",
        (
            "https://www.esercito.difesa.it/comunicazione/editoria/"
            "Rivista-Militare/archivio/Documents/2007/"
            "Rivista%20Militare%202007%20-%20Numero%203.pdf"
        ),
        "Rivista Militare, Italian Army",
        "official_military_history",
        "italian_army_rivista_militare_2007_3",
    ),
    _source(
        "wave8_garibaldi_treccani_mentana",
        "Mentana",
        (
            "https://www.treccani.it/enciclopedia/"
            "mentana_%28Enciclopedia-Italiana%29/"
        ),
        "Istituto della Enciclopedia Italiana (Treccani)",
        "scholarly_encyclopedia",
        "treccani_mentana_1867",
    ),
    _source(
        "wave8_garibaldi_treccani_villa_glori",
        "Villa Glori",
        (
            "https://www.treccani.it/enciclopedia/"
            "villa-glori_%28Enciclopedia-Italiana%29/"
        ),
        "Istituto della Enciclopedia Italiana (Treccani)",
        "scholarly_encyclopedia",
        "treccani_villa_glori_1867",
    ),
    _source(
        "wave8_garibaldi_roma_villa_glori",
        "Villa Glori",
        "https://www.turismoroma.it/en/node/1913",
        "Roma Capitale",
        "official_municipal_history_and_location",
        "roma_capitale_villa_glori",
    ),
    _source(
        "wave8_garibaldi_lombardia_monte_suello",
        "Anfo, Monte Suello - Sacrario militare ai caduti",
        (
            "https://www.lombardiabeniculturali.it/fotografie/"
            "schede/IMM-S0110-0000143/"
        ),
        "Lombardia Beni Culturali (SIRBeC)",
        "official_cultural_heritage_catalogue",
        "lombardia_beni_culturali_monte_suello",
        outcome=False,
    ),
)


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    continuity_note: str,
    source_ids: list[str],
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": "Southern Europe",
        "aliases": [],
        "predecessors": [],
        "continuity_note": continuity_note,
        "source_ids": sorted(source_ids),
    }


WAVE8_GARIBALDI_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        "garibaldi_lombard_volunteer_column_1848",
        "Garibaldi's Lombard volunteer column (1848 campaign)",
        "campaign_bounded_volunteer_column",
        1848,
        (
            "The mixed volunteers entrusted to Garibaldi by the Provisional "
            "Government of Lombardy and retained through the Luino-Morazzone "
            "operations of August 1848. No rating is inherited by the later "
            "Italian Legion, Cacciatori delle Alpi, a generic Redshirts force, "
            "Sardinia, Italy, or any predecessor or successor."
        ),
        [
            "wave8_garibaldi_guerzoni_1889",
            "wave8_garibaldi_treccani_garibaldi",
        ],
    ),
    _entity(
        "sardinian_cacciatori_delle_alpi_1859",
        "Cacciatori delle Alpi (1859 Sardinian campaign)",
        "campaign_bounded_state_volunteer_corps",
        1859,
        (
            "Garibaldi's Cacciatori delle Alpi while constituted as a distinct "
            "Sardinian formation for the 1859 campaign, including Varese and Tre "
            "Ponti. No rating is inherited by Sardinia, the 1848 volunteers, the "
            "1860 Southern Army, the 1866 corps, generic Redshirts, or successors."
        ),
        [
            "wave8_garibaldi_guerzoni_1889",
            "wave8_garibaldi_italian_army_1859_inventory",
            "wave8_garibaldi_italian_army_biography",
        ],
    ),
    _entity(
        "italian_volunteer_corps_1866",
        "Corpo Volontari Italiani (1866 campaign)",
        "campaign_bounded_state_volunteer_corps",
        1866,
        (
            "The Kingdom of Italy's volunteer corps commanded by Garibaldi in "
            "the 1866 campaign. It was institutionally and temporally distinct "
            "from the 1859 Cacciatori and later formations. No rating is inherited "
            "by Italy, generic Redshirts, or any predecessor or successor."
        ),
        [
            "wave8_garibaldi_italian_army_biography",
            "wave8_garibaldi_italian_army_rivista_2007",
        ],
    ),
    _entity(
        "garibaldian_agro_romano_volunteers_1867",
        "Garibaldian volunteers of the Agro Romano campaign (1867)",
        "campaign_bounded_volunteer_army",
        1867,
        (
            "The volunteer force Garibaldi commanded in the October-November "
            "1867 Agro Romano expedition, used here only at Monterotondo. No "
            "rating is inherited by the Cairoli band, Italy, the 1866 corps, "
            "generic Redshirts, or any predecessor or successor."
        ),
        [
            "wave8_garibaldi_italian_army_biography",
            "wave8_garibaldi_treccani_mentana",
        ],
    ),
    _entity(
        "cairoli_villa_glori_band_1867",
        "Enrico Cairoli's Villa Glori volunteer band (1867)",
        "formation_bounded_insurgent_band",
        1867,
        (
            "The roughly seventy volunteers separately led by Enrico Cairoli "
            "from Terni to Villa Glori to support a planned Roman uprising. No "
            "rating is inherited by Garibaldi's main 1867 campaign army, Italy, "
            "generic Redshirts, or any predecessor or successor."
        ),
        [
            "wave8_garibaldi_roma_villa_glori",
            "wave8_garibaldi_treccani_villa_glori",
        ],
    ),
)


def _canonical(name: str, year: int, date_text: str) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "day",
        "date_text": date_text,
        "granularity": "engagement",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


_ROW_HASHES = {
    "hced-Monte Suella1866-1": (
        "ebf2647f31f0ab1784d9bd353559d393075339b98a2a6eef692d41dace3fb2bb"
    ),
    "hced-Monterotondo1867-1": (
        "92a4a82511c4405f4a4fa505acbecf6fd6cfbdd2e6904dd01b2ff6f1f0997a5e"
    ),
    "hced-Morazzone1848-1": (
        "c3795422fc67d4708b92a4b3e87d0503c18a792cc104f9ff3961c5469fbb9ba3"
    ),
    "hced-Tre Ponti1859-1": (
        "685678851b4e50cdb6d9ff1214b0a29ed77e01ffc11e2e2285ffb8339b66814b"
    ),
    "hced-Varese1859-1": (
        "7e7e587f2dc8aafaa6ed1a7e17a703b960d86f0ca5db51645f99b14340430259"
    ),
    "hced-Villa Glori1867-1": (
        "9cac5db7489ec4f96ade9af2862245b25fb6c8b61fc53c025545a1ede3050a61"
    ),
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: list[str],
    side_2_entity_ids: list[str],
    winner_side: int,
    evidence_refs: list[str],
    outcome_source_ids: list[str],
    outcome_source_family_ids: list[str],
    audit_note: str,
    *,
    confidence: float,
    source_outcome_override: bool = False,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": side_1_entity_ids,
        "side_2_entity_ids": side_2_entity_ids,
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "interstate_limited",
        "confidence": confidence,
        "evidence_refs": sorted(evidence_refs),
        "outcome_source_ids": sorted(outcome_source_ids),
        "outcome_source_family_ids": sorted(outcome_source_family_ids),
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": source_outcome_override,
        "actor_override": True,
        "audit_note": audit_note,
    }


WAVE8_GARIBALDI_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Monte Suella1866-1": _contract(
        "hced-Monte Suella1866-1",
        _canonical("Battle of Monte Suello", 1866, "3 July 1866"),
        "third_italian_war_of_independence_1866",
        [_AUSTRIAN_EMPIRE_ID],
        ["italian_volunteer_corps_1866"],
        2,
        [
            "wave8_garibaldi_italian_army_biography",
            "wave8_garibaldi_italian_army_rivista_2007",
            "wave8_garibaldi_lombardia_monte_suello",
        ],
        ["wave8_garibaldi_italian_army_rivista_2007"],
        ["italian_army_rivista_militare_2007_3"],
        (
            "The canonical place is Monte Suello, not Monte Suella. The official "
            "Italian Army history states that Garibaldi's 1866 Corpo Volontari "
            "Italiani beat the Austrians there; HCED's Austrian winner is therefore "
            "reversed on direct outcome evidence. The staged point is far south of "
            "the reviewed Anfo/Monte Suello location and is withheld."
        ),
        confidence=0.90,
        source_outcome_override=True,
    ),
    "hced-Monterotondo1867-1": _contract(
        "hced-Monterotondo1867-1",
        _canonical(
            "Battle of Monterotondo",
            1867,
            "25-26 October 1867",
        ),
        "garibaldian_agro_romano_campaign_1867",
        ["garibaldian_agro_romano_volunteers_1867"],
        [_PAPAL_STATES_ID],
        1,
        [
            "wave8_garibaldi_italian_army_biography",
            "wave8_garibaldi_treccani_mentana",
        ],
        [
            "wave8_garibaldi_italian_army_biography",
            "wave8_garibaldi_treccani_mentana",
        ],
        ["italian_army_garibaldi_biography", "treccani_mentana_1867"],
        (
            "Garibaldi's campaign volunteers assaulted Monterotondo on 25 October "
            "and completed its capture from the Papal defenders by 26 October. "
            "The result belongs only to the bounded 1867 Agro Romano force."
        ),
        confidence=0.91,
    ),
    "hced-Varese1859-1": _contract(
        "hced-Varese1859-1",
        _canonical("Battle of Varese", 1859, "26 May 1859"),
        "second_italian_war_of_independence_1859",
        ["sardinian_cacciatori_delle_alpi_1859"],
        [_AUSTRIAN_EMPIRE_ID],
        1,
        [
            "wave8_garibaldi_guerzoni_1889",
            "wave8_garibaldi_italian_army_1859_inventory",
            "wave8_garibaldi_treccani_garibaldi",
        ],
        [
            "wave8_garibaldi_guerzoni_1889",
            "wave8_garibaldi_treccani_garibaldi",
        ],
        [
            "guerzoni_garibaldi_volume_1",
            "treccani_garibaldi_enciclopedia_italiana",
        ],
        (
            "The Cacciatori delle Alpi repelled Urban's Austrian attack and forced "
            "his force to retreat on 26 May. France and a generic Sardinia-Piedmont "
            "coalition are not invented as battlefield participants."
        ),
        confidence=0.92,
    ),
    "hced-Villa Glori1867-1": _contract(
        "hced-Villa Glori1867-1",
        _canonical("Battle of Villa Glori", 1867, "23 October 1867"),
        "garibaldian_agro_romano_campaign_1867",
        [_PAPAL_STATES_ID],
        ["cairoli_villa_glori_band_1867"],
        1,
        [
            "wave8_garibaldi_roma_villa_glori",
            "wave8_garibaldi_treccani_villa_glori",
        ],
        [
            "wave8_garibaldi_roma_villa_glori",
            "wave8_garibaldi_treccani_villa_glori",
        ],
        ["roma_capitale_villa_glori", "treccani_villa_glori_1867"],
        (
            "The roughly seventy volunteers were Enrico Cairoli's separate band, "
            "not Garibaldi's main 1867 army. Papal troops defeated them on 23 "
            "October; French troops were not the opponent at Villa Glori. The HCED "
            "point is on the Tuscan coast rather than Rome and is withheld."
        ),
        confidence=0.94,
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: list[str],
    side_2_entity_ids: list[str],
    evidence_refs: list[str],
    hold_reason: str,
    audit_note: str,
) -> dict[str, Any]:
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "disposition": "hold",
        "hold_category": "irreconcilable_tactical_outcome",
        "hold_reason": hold_reason,
        "reviewed_outcome": "unknown",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "side_1_entity_ids": side_1_entity_ids,
        "side_2_entity_ids": side_2_entity_ids,
        "evidence_refs": sorted(evidence_refs),
        "audit_note": audit_note,
    }


WAVE8_GARIBALDI_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Morazzone1848-1": _hold(
        "hced-Morazzone1848-1",
        _canonical("Battle of Morazzone", 1848, "26 August 1848"),
        "first_italian_war_of_independence_1848",
        [_AUSTRIAN_EMPIRE_ID],
        ["garibaldi_lombard_volunteer_column_1848"],
        [
            "wave8_garibaldi_guerzoni_1889",
            "wave8_garibaldi_treccani_garibaldi",
        ],
        (
            "The sources establish the sides, date, Garibaldi's breakout, and the "
            "subsequent dissolution and flight to Switzerland, but not one stable "
            "tactical victor. Treccani describes the Austrian attack as repelled; "
            "Guerzoni calls the Austrian result only a half victory."
        ),
        (
            "HCED and the duplicate IWBD row assert Austria, but direct sources do "
            "not resolve whether battlefield repulse/escape or forced campaign "
            "termination controls the tactical label. Unknown is held, never drawn."
        ),
    ),
    "hced-Tre Ponti1859-1": _hold(
        "hced-Tre Ponti1859-1",
        _canonical("Battle of Tre Ponti (Rezzato)", 1859, "15 June 1859"),
        "second_italian_war_of_independence_1859",
        [_AUSTRIAN_EMPIRE_ID],
        ["sardinian_cacciatori_delle_alpi_1859"],
        [
            "wave8_garibaldi_guerzoni_1889",
            "wave8_garibaldi_italian_army_1859_inventory",
        ],
        (
            "The detailed account records an initial Garibaldian retreat in "
            "disorder, a rally, Austrian withdrawal, and the Cacciatori holding "
            "their morning ground; it explicitly declines to classify the final "
            "result as victory, defeat, check, or reverse."
        ),
        (
            "Neither HCED's nor IWBD's Austrian winner can be promoted from the "
            "direct evidence, and the uncertainty is not converted into a draw. "
            "The staged point is near Montagnana rather than Rezzato and is withheld."
        ),
    ),
}


WAVE8_GARIBALDI_CONTRACT_IDS = frozenset(WAVE8_GARIBALDI_CONTRACTS)
WAVE8_GARIBALDI_HOLD_IDS = frozenset(WAVE8_GARIBALDI_HOLDS)
WAVE8_GARIBALDI_RESERVED_IDS = (
    WAVE8_GARIBALDI_CONTRACT_IDS | WAVE8_GARIBALDI_HOLD_IDS
)
WAVE8_GARIBALDI_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


# These are integration contracts only. This lane does not edit the shared
# location manifests; coordinated integration may union these exact IDs.
WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS = frozenset(
    {
        "hced-Monte Suella1866-1",
        "hced-Tre Ponti1859-1",
        "hced-Villa Glori1867-1",
    }
)
WAVE8_GARIBALDI_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_GARIBALDI_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_GARIBALDI_COUNTRY_QUARANTINE_ADDITIONS,
}


WAVE8_GARIBALDI_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Monte Suella1866-1": {
        "raw_winner_label": "Habsburg Empire",
        "raw_loser_label": "Garibaldi's Redshirts",
        "corrected_winner_side": 2,
        "corrected_winner_entity_ids": ["italian_volunteer_corps_1866"],
        "outcome_source_ids": ["wave8_garibaldi_italian_army_rivista_2007"],
        "outcome_source_family_ids": ["italian_army_rivista_militare_2007_3"],
        "correction_note": (
            "The official Italian Army history directly identifies Garibaldi's "
            "victory over the Austrians at Monte Suello."
        ),
    }
}


# Palermo is fingerprinted only to pin the ownership boundary. It is not a
# reservation, contract, hold, entity dependency, or promotion in this lane.
WAVE8_GARIBALDI_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    _PALERMO_NAPLES_OWNER_ID: {
        "source_dataset": "hced",
        "disposition": "external_lane_owner",
        "owner_module": "military_elo.promotion.wave8_naples",
        "raw_row_sha256": (
            "3de60e22c4a892ffb0b2896a68d8ec02fb71b1f850f366ecf52925d5e9a08eb4"
        ),
        "reason": (
            "The row's raw opponent is Naples and the concurrent Wave 8 Naples "
            "lane owns its exact 1860 Southern Army contract."
        ),
    }
}


WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "iwbd-10-4-43": {
        "source_dataset": "iwbd",
        "hced_candidate_id": "hced-Morazzone1848-1",
        "disposition": "hold_duplicate_with_unresolved_outcome",
        "relationship": "same_engagement_same_date_same_queued_winner",
        "fingerprint": {
            "source_row": "43",
            "source_snapshot": "data/raw/iwbd/20260713T161518Z-fcf5747cf94b.bin",
            "name": "Morazzone",
            "war_name": "Austro-Sardinian",
            "start_date": "1848-08-26",
            "end_date": "1848-08-26",
            "duration_days": "1",
            "attacker_raw": "Austria",
            "defender_raw": "Sardinia",
            "winner_raw": "Austria",
            "battle_level_victor_role": "Attacker",
        },
        "reason": (
            "Exact Morazzone twin. Its overbroad Sardinia defender and repeated "
            "Austrian assertion do not resolve the direct-source outcome conflict."
        ),
    },
    "iwbd-28-10-98": {
        "source_dataset": "iwbd",
        "hced_candidate_id": "hced-Varese1859-1",
        "disposition": "deduplicate_to_hced",
        "relationship": "same_engagement_same_date_matching_outcome",
        "fingerprint": {
            "source_row": "98",
            "source_snapshot": "data/raw/iwbd/20260713T161518Z-fcf5747cf94b.bin",
            "name": "Varese",
            "war_name": "Italian Unification",
            "start_date": "1859-05-26",
            "end_date": "1859-05-26",
            "duration_days": "1",
            "attacker_raw": "France/Sardinia/Piedmont",
            "defender_raw": "Austria",
            "winner_raw": "France/Sardinia/Piedmont",
            "battle_level_victor_role": "Attacker",
        },
        "reason": (
            "Exact Varese twin with the same anti-Austrian result. Retain the "
            "source-reviewed HCED event with the Cacciatori delle Alpi identity."
        ),
    },
    "iwbd-28-10-104": {
        "source_dataset": "iwbd",
        "hced_candidate_id": "hced-Tre Ponti1859-1",
        "disposition": "hold_duplicate_with_unresolved_outcome",
        "relationship": "same_engagement_same_date_same_queued_winner",
        "fingerprint": {
            "source_row": "104",
            "source_snapshot": "data/raw/iwbd/20260713T161518Z-fcf5747cf94b.bin",
            "name": "Tre Ponti",
            "war_name": "Italian Unification",
            "start_date": "1859-06-15",
            "end_date": "1859-06-15",
            "duration_days": "1",
            "attacker_raw": "France/Sardinia/Piedmont",
            "defender_raw": "Austria",
            "winner_raw": "Austria",
            "battle_level_victor_role": "Defender",
        },
        "reason": (
            "Exact Tre Ponti twin. Its Austrian label cannot overcome the direct "
            "account's explicit refusal to assign a final tactical classification."
        ),
    },
}


WAVE8_GARIBALDI_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **WAVE8_GARIBALDI_CROSS_LANE_DISPOSITIONS,
    **WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_GARIBALDI_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_GARIBALDI_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_GARIBALDI_ENTITIES,
        "expected_candidate_ids": sorted(WAVE8_GARIBALDI_EXPECTED_CANDIDATE_IDS),
        "holds": WAVE8_GARIBALDI_HOLDS,
        "integration_dispositions": WAVE8_GARIBALDI_INTEGRATION_DISPOSITIONS,
        "outcome_overrides": WAVE8_GARIBALDI_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_GARIBALDI_SOURCES,
    }


def wave8_garibaldi_audit_signature() -> str:
    return hashlib.sha256(_canonical_json(_signature_payload()).encode("utf-8")).hexdigest()


# Patched to the measured payload after the fixtures and dispositions are final.
WAVE8_GARIBALDI_FINAL_AUDIT_SIGNATURE = (
    "8cbd1ae341dd7056a626d973622fb3876b03c7da0f73563137ad5e77623d9c98"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (len(WAVE8_GARIBALDI_CONTRACTS), len(WAVE8_GARIBALDI_HOLDS)) != (4, 2):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_GARIBALDI_ENTITIES), len(WAVE8_GARIBALDI_SOURCES)) != (5, 9):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_GARIBALDI_RESERVED_IDS != WAVE8_GARIBALDI_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if WAVE8_GARIBALDI_CONTRACT_IDS & WAVE8_GARIBALDI_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotions and holds overlap")
    if _PALERMO_NAPLES_OWNER_ID in WAVE8_GARIBALDI_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} claimed the Naples-owned Palermo row")
    if wave8_garibaldi_audit_signature() != WAVE8_GARIBALDI_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_GARIBALDI_SOURCES}
    if len(source_by_id) != len(WAVE8_GARIBALDI_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_GARIBALDI_SOURCES:
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_GARIBALDI_ENTITIES}
    if len(entity_by_id) != len(WAVE8_GARIBALDI_ENTITIES):
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    for entity in WAVE8_GARIBALDI_ENTITIES:
        if entity["start_year"] != entity["end_year"]:
            raise ValueError(f"{_LANE_NAME} identity is not campaign bounded")
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity opens a generic fallback")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} identity permits rating inheritance")
        if "redshirts" in str(entity["name"]).casefold():
            raise ValueError(f"{_LANE_NAME} created a timeless Redshirts identity")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")

    allowed_existing_entities = {_AUSTRIAN_EMPIRE_ID, _PAPAL_STATES_ID}
    used_new_entities: set[str] = set()
    for candidate_id, disposition in {
        **WAVE8_GARIBALDI_CONTRACTS,
        **WAVE8_GARIBALDI_HOLDS,
    }.items():
        if disposition["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} queue hash table drifted")
        row_hash = str(disposition["raw_row_sha256"])
        if len(row_hash) != 64 or any(c not in "0123456789abcdef" for c in row_hash):
            raise ValueError(f"{_LANE_NAME} has an invalid queue hash")
        canonical = disposition["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} canonical key drifted")
        if canonical["date_precision"] != "day" or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} exact date contract drifted")

        side_1 = list(map(str, disposition["side_1_entity_ids"]))
        side_2 = list(map(str, disposition["side_2_entity_ids"]))
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        for entity_id in (*side_1, *side_2):
            entity = entity_by_id.get(entity_id)
            if entity is None and entity_id not in allowed_existing_entities:
                raise ValueError(f"{_LANE_NAME} uses an unknown identity")
            if entity is not None:
                year = int(canonical["year_low"])
                if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                    raise ValueError(f"{_LANE_NAME} exceeds an identity window")
                used_new_entities.add(entity_id)

        evidence = list(map(str, disposition["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")

    if used_new_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} new entities are not exactly consumed")

    override_ids: set[str] = set()
    for candidate_id, contract in WAVE8_GARIBALDI_CONTRACTS.items():
        if contract["result_type"] != "win" or contract["winner_side"] not in {1, 2}:
            raise ValueError(f"{_LANE_NAME} contains a non-win promotion")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor correction is not explicit")
        if contract["outcome_reversal"] is not contract["source_outcome_override"]:
            raise ValueError(f"{_LANE_NAME} outcome reversal metadata drifted")
        if contract["source_outcome_override"]:
            override_ids.add(candidate_id)

        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        evidence = list(map(str, contract["evidence_refs"]))
        if not outcomes or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} lacks canonical outcome provenance")
        if not _is_sorted_unique(families) or not set(outcomes) <= set(evidence):
            raise ValueError(f"{_LANE_NAME} outcome provenance drifted")
        if any("outcome" not in source_by_id[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source for a result")
        expected_families = sorted(
            {str(source_by_id[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families:
            raise ValueError(f"{_LANE_NAME} outcome family provenance drifted")

    if override_ids != set(WAVE8_GARIBALDI_OUTCOME_OVERRIDES):
        raise ValueError(f"{_LANE_NAME} outcome override inventory drifted")
    for candidate_id, metadata in WAVE8_GARIBALDI_OUTCOME_OVERRIDES.items():
        contract = WAVE8_GARIBALDI_CONTRACTS[candidate_id]
        if (
            metadata["corrected_winner_side"] != contract["winner_side"]
            or metadata["corrected_winner_entity_ids"]
            != contract[f"side_{contract['winner_side']}_entity_ids"]
            or metadata["outcome_source_ids"] != contract["outcome_source_ids"]
            or metadata["outcome_source_family_ids"]
            != contract["outcome_source_family_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome override metadata drifted")

    for hold in WAVE8_GARIBALDI_HOLDS.values():
        if (
            hold["disposition"] != "hold"
            or hold["result_type"] != "unknown"
            or hold["reviewed_outcome"] != "unknown"
            or hold["unknown_is_never_draw"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} unknown outcome became a draw or win")
        if "winner_side" in hold:
            raise ValueError(f"{_LANE_NAME} hold invents a winner")

    expected_points = {
        "hced-Monte Suella1866-1",
        "hced-Tre Ponti1859-1",
        "hced-Villa Glori1867-1",
    }
    if WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS != expected_points:
        raise ValueError(f"{_LANE_NAME} point quarantine contract changed")
    if WAVE8_GARIBALDI_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if not WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS <= WAVE8_GARIBALDI_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine references an unowned row")

    if set(WAVE8_GARIBALDI_CROSS_LANE_DISPOSITIONS) != {_PALERMO_NAPLES_OWNER_ID}:
        raise ValueError(f"{_LANE_NAME} cross-lane boundary changed")
    palermo = WAVE8_GARIBALDI_CROSS_LANE_DISPOSITIONS[_PALERMO_NAPLES_OWNER_ID]
    if (
        palermo["disposition"] != "external_lane_owner"
        or palermo["owner_module"] != "military_elo.promotion.wave8_naples"
    ):
        raise ValueError(f"{_LANE_NAME} Palermo owner changed")

    expected_iwbd = {
        "iwbd-10-4-43": "hced-Morazzone1848-1",
        "iwbd-28-10-98": "hced-Varese1859-1",
        "iwbd-28-10-104": "hced-Tre Ponti1859-1",
    }
    if set(WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS) != set(expected_iwbd):
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    for iwbd_id, hced_id in expected_iwbd.items():
        record = WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS[iwbd_id]
        if record["hced_candidate_id"] != hced_id or hced_id not in WAVE8_GARIBALDI_RESERVED_IDS:
            raise ValueError(f"{_LANE_NAME} IWBD duplicate target changed")
        fingerprint = record["fingerprint"]
        if fingerprint["start_date"] != fingerprint["end_date"]:
            raise ValueError(f"{_LANE_NAME} IWBD duplicate date changed")
    if set(WAVE8_GARIBALDI_INTEGRATION_DISPOSITIONS) != {
        _PALERMO_NAPLES_OWNER_ID,
        *expected_iwbd,
    }:
        raise ValueError(f"{_LANE_NAME} integration disposition inventory changed")


def validate_wave8_garibaldi_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    return validate_exact_hced_inventory(
        hced_rows,
        WAVE8_GARIBALDI_CONTRACTS,
        WAVE8_GARIBALDI_HOLDS,
        lane_name=_LANE_NAME,
    )


def _iwbd_fingerprint(row: Mapping[str, Any]) -> dict[str, str]:
    fields = (
        "source_row",
        "source_snapshot",
        "name",
        "war_name",
        "start_date",
        "end_date",
        "duration_days",
        "attacker_raw",
        "defender_raw",
        "winner_raw",
        "battle_level_victor_role",
    )
    return {
        field: "" if row.get(field) is None else str(row.get(field)) for field in fields
    }


def validate_wave8_garibaldi_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Fail closed on the Naples boundary and the three exact IWBD twins."""

    _validate_static()
    hced_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        hced_by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    palermo_rows = hced_by_id.get(_PALERMO_NAPLES_OWNER_ID, [])
    if len(palermo_rows) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one Naples-owned Palermo row, "
            f"found {len(palermo_rows)}"
        )
    expected_palermo_hash = WAVE8_GARIBALDI_CROSS_LANE_DISPOSITIONS[
        _PALERMO_NAPLES_OWNER_ID
    ]["raw_row_sha256"]
    if canonical_hced_row_sha256(palermo_rows[0]) != expected_palermo_hash:
        raise ValueError(f"{_LANE_NAME} Naples-owned Palermo fingerprint changed")

    iwbd_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in iwbd_rows:
        iwbd_by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, disposition in WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS.items():
        rows = iwbd_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one IWBD duplicate {candidate_id}, "
                f"found {len(rows)}"
            )
        actual = _iwbd_fingerprint(rows[0])
        expected = disposition["fingerprint"]
        if actual != expected:
            changed = sorted(key for key in expected if actual.get(key) != expected[key])
            raise ValueError(
                f"{_LANE_NAME} IWBD duplicate fingerprint changed for "
                f"{candidate_id}: {changed}"
            )
    return {
        "cross_lane_hced_dispositions": len(WAVE8_GARIBALDI_CROSS_LANE_DISPOSITIONS),
        "integration_dispositions": len(WAVE8_GARIBALDI_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS
        ),
    }


def install_wave8_garibaldi_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_GARIBALDI_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_garibaldi_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_GARIBALDI_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_GARIBALDI_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_garibaldi_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_garibaldi_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_GARIBALDI_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_garibaldi_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_GARIBALDI_CONTRACTS.values()
            ).items()
        )
    )


def wave8_garibaldi_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_GARIBALDI_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_GARIBALDI_CROSS_LANE_DISPOSITIONS
        ),
        "holds": len(WAVE8_GARIBALDI_HOLDS),
        "integration_dispositions": len(WAVE8_GARIBALDI_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_GARIBALDI_ENTITIES),
        "new_sources": len(WAVE8_GARIBALDI_SOURCES),
        "newly_rated_events": len(WAVE8_GARIBALDI_CONTRACTS),
        "outcome_overrides": len(WAVE8_GARIBALDI_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_GARIBALDI_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_GARIBALDI_RESERVED_IDS),
    }


def wave8_garibaldi_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return immutable additions for coordinated shared-location integration."""

    _validate_static()
    return {
        "country": WAVE8_GARIBALDI_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS,
    }
