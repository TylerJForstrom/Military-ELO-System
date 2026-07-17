"""Candidate-keyed Wave 8 audit for HCED's exact ``Murids`` label.

The four locked rows do not describe a timeless religious or ethnic polity.
Gimrah belongs to Ghazi Muhammad's 1829--1832 Dagestani Imamate; the two
Darghiyya rows and Gunib belong to Shamil's 1834--1859 Caucasian Imamate.
The opposing Russian formations are bounded to the Russian Empire.

The two Darghiyya records are distinct operational expeditions toward Dargo:
Grabbe's failed Ichkeria expedition in 1842 and Vorontsov's failed Dargo
expedition in 1845.  Their campaign outcomes are not collapsed into invented
point battles, and the temporary Russian occupation of burned Dargo in 1845
is not substituted for the independently attested result of the full
expedition.  Gimrah and Gunib are separately bounded assaults.  No generic
``Murids``, Dagestan, Chechnya, Muslim, or modern-state alias is installed;
unknown is never converted to a draw.
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
    operationalize_campaign_outcomes,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS",
    "WAVE8_MURIDS_ADJACENT_LITERAL_LABEL_INVENTORY",
    "WAVE8_MURIDS_CAMPAIGN_CONTRACT_IDS",
    "WAVE8_MURIDS_CONTRACT_IDS",
    "WAVE8_MURIDS_CONTRACTS",
    "WAVE8_MURIDS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS",
    "WAVE8_MURIDS_ENTITIES",
    "WAVE8_MURIDS_EXACT_CANDIDATE_ID_SHA256",
    "WAVE8_MURIDS_EXCLUSION_IDS",
    "WAVE8_MURIDS_EXCLUSIONS",
    "WAVE8_MURIDS_EXISTING_LANE_OVERLAP_AUDIT",
    "WAVE8_MURIDS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_MURIDS_EXPECTED_CANDIDATE_IDS",
    "WAVE8_MURIDS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_MURIDS_FUNNEL_AUDIT",
    "WAVE8_MURIDS_HOLD_IDS",
    "WAVE8_MURIDS_HOLDS",
    "WAVE8_MURIDS_INTEGRATION_DISPOSITIONS",
    "WAVE8_MURIDS_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_MURIDS_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_MURIDS_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_MURIDS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_MURIDS_NONPROMOTIONS",
    "WAVE8_MURIDS_OUTCOME_OVERRIDES",
    "WAVE8_MURIDS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_MURIDS_REQUIRED_EXISTING_ENTITY_IDS",
    "WAVE8_MURIDS_RESERVED_IDS",
    "WAVE8_MURIDS_ROW_DISPOSITIONS",
    "WAVE8_MURIDS_ROW_HASHES",
    "WAVE8_MURIDS_SCOPE_AND_OPPOSITE_RESULT_AUDIT",
    "WAVE8_MURIDS_SOURCES",
    "WAVE8_MURIDS_TERMINAL_EXCLUSION_IDS",
    "WAVE8_MURIDS_TERMINAL_EXCLUSIONS",
    "install_wave8_murids_entities",
    "install_wave8_murids_sources",
    "promote_wave8_murids_contracts",
    "validate_wave8_murids_existing_entities",
    "validate_wave8_murids_funnel",
    "validate_wave8_murids_integration_dispositions",
    "validate_wave8_murids_queue_contracts",
    "wave8_murids_audit_signature",
    "wave8_murids_cohort_counts",
    "wave8_murids_counts",
    "wave8_murids_location_quarantine_additions",
    "wave8_murids_metadata",
    "wave8_murids_row_dispositions",
)


_LANE_NAME = "Wave 8 exact Murids imamate-regime audit"
_MODULE_OWNER = "military_elo.promotion.wave8_murids"
_EVENT_ID_PREFIX = "hced_wave8_murids_"
_EXACT_LABEL = "murids"

_RUSSIAN_EMPIRE_ID = "russian_empire"
_GHAZI_IMAMATE_ID = "dagestani_imamate_ghazi_muhammad_1829_1832"
_SHAMIL_IMAMATE_ID = "caucasian_imamate_shamil_1834_1859"


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
        "evidence_roles": sorted(set(roles)),
    }


WAVE8_MURIDS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_murids_gammer_muslim_resistance",
        (
            "Muslim Resistance to the Tsar: Shamil and the Conquest of "
            "Chechnia and Daghestan"
        ),
        (
            "https://api.pageplace.de/preview/"
            "DT0400.9781135308988_A24427534/preview-9781135308988_A24427534.pdf"
        ),
        "Routledge",
        "scholarly_monograph_preview",
        "gammer_muslim_resistance_monograph",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_murids_baddeley_russian_conquest",
        "The Russian Conquest of the Caucasus",
        (
            "https://commons.wikimedia.org/wiki/"
            "File:The_Russian_conquest_of_the_Caucasus_(IA_cu31924028754616).pdf"
        ),
        "Longmans, Green and Co.; Cornell University / Internet Archive scan",
        "digitized_historical_monograph",
        "baddeley_russian_conquest_1908",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_murids_bre_ghazi_muhammad",
        "Ghazi Muhammad",
        "https://old.bigenc.ru/domestic_history/text/2339442",
        "Great Russian Encyclopedia",
        "scholarly_encyclopedia",
        "great_russian_encyclopedia_ghazi_muhammad",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_murids_bre_shamil",
        "Shamil",
        "https://old.bigenc.ru/domestic_history/text/4690031",
        "Great Russian Encyclopedia",
        "scholarly_encyclopedia",
        "great_russian_encyclopedia_shamil",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_murids_bre_dargo_1845",
        "Dargo Expedition of 1845",
        "https://old.bigenc.ru/military_science/text/1941105",
        "Great Russian Encyclopedia",
        "scholarly_military_encyclopedia",
        "great_russian_encyclopedia_dargo_1845",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_murids_bre_gunib_1859",
        "Storming of Gunib, 1859",
        "https://old.bigenc.ru/military_science/text/1935832",
        "Great Russian Encyclopedia",
        "scholarly_military_encyclopedia",
        "great_russian_encyclopedia_gunib_1859",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_murids_baumann_unconventional_wars",
        (
            "Russian-Soviet Unconventional Wars in the Caucasus, Central Asia, "
            "and Afghanistan"
        ),
        (
            "https://history.army.mil/Publications/Publications-Catalog/"
            "Leavenworth-Papers-No20-Russian-Soviet/"
        ),
        "U.S. Army Center of Military History",
        "official_military_history",
        "baumann_leavenworth_paper_20",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_murids_statiev_mountain_warfare",
        "Russia's Historical Experience in Mountain Warfare",
        (
            "https://www.cambridge.org/core/books/at-wars-summit/"
            "russias-historical-experience-in-mountain-warfare/"
            "DDFF5F586D273F8165ED1DED9431C8D1"
        ),
        "Cambridge University Press",
        "scholarly_military_history_chapter",
        "statiev_mountain_warfare_dargo",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_murids_tdv_shamil",
        "Seyh Samil",
        "https://islamansiklopedisi.org.tr/seyh-samil",
        "TDV Encyclopedia of Islam",
        "scholarly_encyclopedia",
        "tdv_islam_encyclopedia_shamil",
        outcome=True,
        crosscheck=True,
    ),
)


# This lane deliberately creates no entity.  The two imamate identities were
# curated by the Dagestan lane and are reused only inside their exact windows.
WAVE8_MURIDS_ENTITIES: tuple[dict[str, Any], ...] = ()


WAVE8_MURIDS_EXISTING_LANE_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    _GHAZI_IMAMATE_ID: {
        "name": "Dagestani Imamate under Ghazi Muhammad",
        "kind": "theocratic_imamate",
        "start_year": 1829,
        "end_year": 1832,
        "existing_owner": "military_elo.promotion.wave8_dagestan",
        "disposition": "reuse_exact_regime_without_generic_murid_alias",
        "candidate_id_overlap": [],
    },
    _SHAMIL_IMAMATE_ID: {
        "name": "Caucasian Imamate under Imam Shamil",
        "kind": "theocratic_imamate",
        "start_year": 1834,
        "end_year": 1859,
        "existing_owner": "military_elo.promotion.wave8_dagestan",
        "disposition": "reuse_exact_regime_without_generic_murid_alias",
        "candidate_id_overlap": [],
    },
    _RUSSIAN_EMPIRE_ID: {
        "name": "Russian Empire",
        "kind": "empire",
        "start_year": 1721,
        "end_year": 1917,
        "existing_owner": "curated_release",
        "disposition": "reuse_time_bounded_russian_regime",
        "candidate_id_overlap": [],
    },
}
WAVE8_MURIDS_REQUIRED_EXISTING_ENTITY_IDS = frozenset(
    WAVE8_MURIDS_EXISTING_LANE_OVERLAP_AUDIT
)


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


WAVE8_MURIDS_ROW_HASHES: dict[str, str] = {
    "hced-Darghiyya1842-1": (
        "52e36312d55cd70376d75d7f778a8c4aa8b78ed7c6e05bb1e616934d1b23bc57"
    ),
    "hced-Darghiyya1845-1": (
        "960268777a79c16d34cf5d2fcff751f7d41036594faf3c59c2be3ceffe5ff80e"
    ),
    "hced-Gimrah1832-1": (
        "ab038040242931609ed8d2784a32fbd7ff129266a68ad7c84da298a00ba7db2b"
    ),
    "hced-Gunib1859-1": (
        "cdf06a3969b21eac601427b0a2ec2be893a081642b4009b1cb80b28fd4b9abc2"
    ),
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: list[str],
    side_2_entity_ids: list[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    reviewed_sides: list[str],
    reviewed_outcome: str,
    event_boundary: str,
    event_type: str,
    confidence: float,
) -> dict[str, Any]:
    source_by_id = {
        str(source["id"]): source for source in WAVE8_MURIDS_SOURCES
    }
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_MURIDS_ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": side_1_entity_ids,
        "side_2_entity_ids": side_2_entity_ids,
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "audited_label_split_into_time_bounded_imamate_regimes",
        "disposition": "promote",
        "reviewed_sides": reviewed_sides,
        "reviewed_outcome": reviewed_outcome,
        "event_boundary": event_boundary,
        "event_type": event_type,
        "audit_note": audit_note,
    }


WAVE8_MURIDS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Gimrah1832-1": _contract(
        "hced-Gimrah1832-1",
        _canonical(
            "Assault of Gimry",
            1832,
            "17 October 1832 Old Style (29 October New Style)",
            date_precision="dual_calendar_day",
            granularity="fortified_village_assault",
        ),
        "ghazi_muhammad_final_gimry_1832",
        [_RUSSIAN_EMPIRE_ID],
        [_GHAZI_IMAMATE_ID],
        1,
        [
            "wave8_murids_baddeley_russian_conquest",
            "wave8_murids_bre_ghazi_muhammad",
            "wave8_murids_bre_shamil",
            "wave8_murids_gammer_muslim_resistance",
        ],
        [
            "wave8_murids_baddeley_russian_conquest",
            "wave8_murids_bre_ghazi_muhammad",
            "wave8_murids_gammer_muslim_resistance",
        ],
        (
            "The Russian assault broke the fortified Gimry position and killed "
            "Ghazi Muhammad with most of the murids defending it; wounded Shamil "
            "escaped. The loser is Ghazi Muhammad's 1829-1832 imamate, not a "
            "religious class, generic Dagestan, or Shamil's later regime."
        ),
        reviewed_sides=[
            "Rosen and Velyaminov's Russian imperial assault force",
            "Ghazi Muhammad's Gimry imamate defenders",
        ],
        reviewed_outcome="Russian assault victory; Gimry position captured",
        event_boundary="the October assault on the fortified Gimry position",
        event_type="engagement",
        confidence=0.97,
    ),
    "hced-Darghiyya1842-1": _contract(
        "hced-Darghiyya1842-1",
        _canonical(
            "Ichkeria Expedition toward Dargo (1842)",
            1842,
            "May-June 1842; exact day framing varies by calendar and account",
            date_precision="month_range",
            granularity="multi_day_operational_expedition",
        ),
        "shamil_dargo_operations_1842_1845",
        [_SHAMIL_IMAMATE_ID],
        [_RUSSIAN_EMPIRE_ID],
        1,
        [
            "wave8_murids_baddeley_russian_conquest",
            "wave8_murids_baumann_unconventional_wars",
            "wave8_murids_bre_shamil",
            "wave8_murids_gammer_muslim_resistance",
        ],
        [
            "wave8_murids_baddeley_russian_conquest",
            "wave8_murids_baumann_unconventional_wars",
            "wave8_murids_gammer_muslim_resistance",
        ],
        (
            "Grabbe's column attempted to reach and destroy Shamil's Dargo base "
            "through the Ichkeria forests, was stopped by Imamate-aligned local "
            "forces and repeated ambushes, and withdrew without reaching its "
            "objective. This is the bounded expedition result, not an invented "
            "single battle at the HCED locality point."
        ),
        reviewed_sides=[
            "Shamil-imamate naib and local Ichkeria defensive forces",
            "Grabbe's Russian imperial expeditionary column",
        ],
        reviewed_outcome="Imamate operational victory; Russian expedition repulsed",
        event_boundary="Grabbe's 1842 advance toward Dargo and compelled withdrawal",
        event_type="campaign",
        confidence=0.92,
    ),
    "hced-Darghiyya1845-1": _contract(
        "hced-Darghiyya1845-1",
        _canonical(
            "Dargo Expedition (1845)",
            1845,
            (
                "5 June-20 July 1845 Old Style "
                "(17 June-1 August New Style)"
            ),
            date_precision="dual_calendar_day_range",
            granularity="multi_week_operational_expedition",
        ),
        "shamil_dargo_operations_1842_1845",
        [_SHAMIL_IMAMATE_ID],
        [_RUSSIAN_EMPIRE_ID],
        1,
        [
            "wave8_murids_bre_dargo_1845",
            "wave8_murids_bre_shamil",
            "wave8_murids_gammer_muslim_resistance",
            "wave8_murids_statiev_mountain_warfare",
        ],
        [
            "wave8_murids_bre_dargo_1845",
            "wave8_murids_gammer_muslim_resistance",
            "wave8_murids_statiev_mountain_warfare",
        ],
        (
            "Vorontsov's force occupied Dargo only after Shamil ordered it burned, "
            "then became trapped, lost its supply column, suffered catastrophic "
            "losses, and escaped only after a relief force arrived. The temporary "
            "occupation is a nested Russian tactical success; independent sources "
            "identify the complete expedition as a decisive Russian defeat."
        ),
        reviewed_sides=[
            "Shamil's Caucasian Imamate forces defending the Dargo approaches",
            "Vorontsov's Russian imperial Dargo expedition",
        ],
        reviewed_outcome="Imamate operational victory; Dargo expedition defeated",
        event_boundary="the full June-July Dargo expedition and Russian escape",
        event_type="campaign",
        confidence=0.98,
    ),
    "hced-Gunib1859-1": _contract(
        "hced-Gunib1859-1",
        _canonical(
            "Assault and surrender of Gunib",
            1859,
            (
                "9-25 August 1859 Old Style "
                "(21 August-6 September New Style)"
            ),
            date_precision="dual_calendar_day_range",
            granularity="blockade_assault_and_capitulation",
        ),
        "shamil_final_gunib_1859",
        [_RUSSIAN_EMPIRE_ID],
        [_SHAMIL_IMAMATE_ID],
        1,
        [
            "wave8_murids_baddeley_russian_conquest",
            "wave8_murids_bre_gunib_1859",
            "wave8_murids_bre_shamil",
            "wave8_murids_gammer_muslim_resistance",
            "wave8_murids_tdv_shamil",
        ],
        [
            "wave8_murids_bre_gunib_1859",
            "wave8_murids_gammer_muslim_resistance",
            "wave8_murids_tdv_shamil",
        ],
        (
            "Russian forces blockaded and stormed the Gunib plateau, drove the "
            "remaining defenders from their works, and accepted Shamil's surrender. "
            "The result is bounded to the Gunib operation; it does not transfer "
            "rating to modern Dagestan, Chechnya, or a generic Muslim actor."
        ),
        reviewed_sides=[
            "Baryatinsky's Russian imperial Gunib force",
            "Shamil's final Caucasian Imamate defenders at Gunib",
        ],
        reviewed_outcome="Russian victory; Gunib taken and Shamil surrendered",
        event_boundary="the August blockade, assault, and capitulation at Gunib",
        event_type="engagement",
        confidence=0.98,
    ),
}


WAVE8_MURIDS_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_MURIDS_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_MURIDS_EXCLUSIONS = WAVE8_MURIDS_TERMINAL_EXCLUSIONS
WAVE8_MURIDS_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_MURIDS_HOLDS,
    **WAVE8_MURIDS_TERMINAL_EXCLUSIONS,
}
WAVE8_MURIDS_CONTRACT_IDS = frozenset(WAVE8_MURIDS_CONTRACTS)
WAVE8_MURIDS_HOLD_IDS = frozenset(WAVE8_MURIDS_HOLDS)
WAVE8_MURIDS_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_MURIDS_TERMINAL_EXCLUSIONS
)
WAVE8_MURIDS_EXCLUSION_IDS = WAVE8_MURIDS_TERMINAL_EXCLUSION_IDS
WAVE8_MURIDS_RESERVED_IDS = frozenset(
    WAVE8_MURIDS_CONTRACT_IDS
    | WAVE8_MURIDS_HOLD_IDS
    | WAVE8_MURIDS_TERMINAL_EXCLUSION_IDS
)
WAVE8_MURIDS_EXPECTED_CANDIDATE_IDS = frozenset(WAVE8_MURIDS_ROW_HASHES)
WAVE8_MURIDS_CAMPAIGN_CONTRACT_IDS = frozenset(
    candidate_id
    for candidate_id, contract in WAVE8_MURIDS_CONTRACTS.items()
    if contract["event_type"] == "campaign"
)
WAVE8_MURIDS_ROW_DISPOSITIONS = {
    candidate_id: "promote" for candidate_id in sorted(WAVE8_MURIDS_RESERVED_IDS)
}
WAVE8_MURIDS_EXACT_CANDIDATE_ID_SHA256 = (
    "cf7a001984f30436292b572b4ffc3edc4dd5228eee06f3f95ca11e19375e57c1"
)


WAVE8_MURIDS_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "centuries": {"CE_19": 4},
    "components_bridged": 0,
    "components_touched": 1,
    "event_candidate_id_sha256": WAVE8_MURIDS_EXACT_CANDIDATE_ID_SHA256,
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
    "sole_blocker_events": 4,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 4,
}


WAVE8_MURIDS_SCOPE_AND_OPPOSITE_RESULT_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Gimrah1832-1": {
        "audited_unit": "fortified_village_assault",
        "attested_result": "russian_assault_victory",
        "opposite_result_disposition": "no_supported_imamate_victory",
        "scope_note": "The assault and capture are rated, not the whole Caucasus War.",
    },
    "hced-Darghiyya1842-1": {
        "audited_unit": "multi_day_operational_expedition",
        "attested_result": "imamate_operational_victory",
        "opposite_result_disposition": "no_russian_objective_reached",
        "scope_note": (
            "The complete failed advance and withdrawal are rated; no point battle "
            "at Darghiyya is invented."
        ),
    },
    "hced-Darghiyya1845-1": {
        "audited_unit": "multi_week_operational_expedition",
        "attested_result": "imamate_operational_victory",
        "opposite_result_disposition": (
            "temporary_russian_occupation_of_burned_dargo_is_nested_subaction"
        ),
        "scope_note": (
            "The full expedition is rated; its component fights and temporary "
            "occupation are not emitted as additional outcomes."
        ),
    },
    "hced-Gunib1859-1": {
        "audited_unit": "blockade_assault_and_capitulation",
        "attested_result": "russian_assault_and_capitulation_victory",
        "opposite_result_disposition": "no_supported_imamate_holdout_victory",
        "scope_note": "The bounded Gunib operation is rated, not later Caucasian fighting.",
    },
}


WAVE8_MURIDS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Gimrah1832-1": {
        "actions": ["withhold_point"],
        "retained_country": "Russia",
        "reason": (
            "The HCED coordinate is a modern Gimry locality point, not a source-audited "
            "point for the gorge, fortified approaches, and assault footprint."
        ),
        "evidence_refs": [
            "wave8_murids_bre_ghazi_muhammad",
            "wave8_murids_gammer_muslim_resistance",
        ],
    },
    "hced-Darghiyya1842-1": {
        "actions": ["withhold_point"],
        "retained_country": "Russia",
        "reason": (
            "The expedition fought along a forest route toward Dargo and withdrew; "
            "one village coordinate cannot represent the audited operation."
        ),
        "evidence_refs": [
            "wave8_murids_baddeley_russian_conquest",
            "wave8_murids_baumann_unconventional_wars",
        ],
    },
    "hced-Darghiyya1845-1": {
        "actions": ["withhold_point"],
        "retained_country": "Russia",
        "reason": (
            "The multi-week expedition crossed Andi, Dargo, supply-road, retreat, "
            "and relief actions; the Dargo locality point is not the campaign footprint."
        ),
        "evidence_refs": [
            "wave8_murids_bre_dargo_1845",
            "wave8_murids_statiev_mountain_warfare",
        ],
    },
    "hced-Gunib1859-1": {
        "actions": ["withhold_point"],
        "retained_country": "Russia",
        "reason": (
            "A modern Gunib locality coordinate does not identify the full plateau "
            "blockade, climbing assaults, defensive works, and surrender site."
        ),
        "evidence_refs": [
            "wave8_murids_bre_gunib_1859",
            "wave8_murids_tdv_shamil",
        ],
    },
}
WAVE8_MURIDS_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_MURIDS_LOCATION_QUARANTINE_REASONS
)
WAVE8_MURIDS_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_MURIDS_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_MURIDS_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_MURIDS_COUNTRY_QUARANTINE_ADDITIONS,
}


_DAGESTAN_ROW_HASHES = {
    "hced-Aghdash Awkh1831-1": (
        "5635a7072bf490c68cf2d692e429ab59ee88afbedebae681aead7c3bdf3e1130"
    ),
    "hced-Akhulgo1839-1": (
        "483b74e08c8da8308115a51462f852a26f377a63907986109c3caf19d5693a68"
    ),
    "hced-Burtinah1839-1": (
        "c5cc816acd0ee80ee738cb2edfee935859c0612873b31e355b735ff7f5380f79"
    ),
    "hced-Girgil1847-1": (
        "a571f76e08358a4871d253ea40c9c6cd7e455b3d53f6b188af96f5e289e5abeb"
    ),
    "hced-Saltah1847-1": (
        "cd3afc6860b7ac4d3390ff279e93d17cfa31ef4926e91b658800a77f7b0a4a2e"
    ),
    "hced-Zakataly1853-1": (
        "72be61df57fa08a282ad29b8cc7b78392e59ae833ba058538956b24a93b90972"
    ),
}
WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Aghdash Awkh1831-1": {
        "raw_row_sha256": _DAGESTAN_ROW_HASHES["hced-Aghdash Awkh1831-1"],
        "owner_module": "military_elo.promotion.wave8_dagestan",
        "owner_event_id": "hced_wave8_dagestan_hced_aghdash_awkh1831_1",
        "owner_entity_id": _GHAZI_IMAMATE_ID,
        "disposition": "distinct_prior_engagement_same_regime",
    },
    "hced-Akhulgo1839-1": {
        "raw_row_sha256": _DAGESTAN_ROW_HASHES["hced-Akhulgo1839-1"],
        "owner_module": "military_elo.promotion.wave8_dagestan",
        "owner_event_id": "hced_wave8_dagestan_hced_akhulgo1839_1",
        "owner_entity_id": _SHAMIL_IMAMATE_ID,
        "disposition": "distinct_siege",
    },
    "hced-Burtinah1839-1": {
        "raw_row_sha256": _DAGESTAN_ROW_HASHES["hced-Burtinah1839-1"],
        "owner_module": "military_elo.promotion.wave8_dagestan",
        "owner_event_id": "hced_wave8_dagestan_hced_burtinah1839_1",
        "owner_entity_id": _SHAMIL_IMAMATE_ID,
        "disposition": "distinct_battle",
    },
    "hced-Girgil1847-1": {
        "raw_row_sha256": _DAGESTAN_ROW_HASHES["hced-Girgil1847-1"],
        "owner_module": "military_elo.promotion.wave8_dagestan",
        "owner_event_id": "hced_wave8_dagestan_hced_girgil1847_1",
        "owner_entity_id": _SHAMIL_IMAMATE_ID,
        "disposition": "distinct_later_battle_with_reviewed_opposite_raw_result",
    },
    "hced-Saltah1847-1": {
        "raw_row_sha256": _DAGESTAN_ROW_HASHES["hced-Saltah1847-1"],
        "owner_module": "military_elo.promotion.wave8_dagestan",
        "owner_event_id": "hced_wave8_dagestan_hced_saltah1847_1",
        "owner_entity_id": _SHAMIL_IMAMATE_ID,
        "disposition": "distinct_later_siege",
    },
    "hced-Zakataly1853-1": {
        "raw_row_sha256": _DAGESTAN_ROW_HASHES["hced-Zakataly1853-1"],
        "owner_module": "military_elo.promotion.wave8_dagestan",
        "owner_event_id": "hced_wave8_dagestan_hced_zakataly1853_1",
        "owner_entity_id": _SHAMIL_IMAMATE_ID,
        "disposition": "distinct_later_battle",
    },
}


_ADJACENT_ROW_HASHES = {
    "hced-Anapa1789-1": (
        "5081861ce9beff84380a73fede9bb074ee11c71e2e79732c74edd5cc207f1445"
    ),
    "hced-Grozny1995-1": (
        "256bbb6c2f8ef129737f43bb33e0aa3e9293bdb5f8ec459806e8d3775e9db138"
    ),
    "hced-Grozny2000-1": (
        "6c38219e9c2726c114a7261e7dc38f5f2ef218cf3cea5194349f29519f88aa9b"
    ),
}
WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Anapa1789-1": {
        "raw_row_sha256": _ADJACENT_ROW_HASHES["hced-Anapa1789-1"],
        "literal_label": "ottoman empire chechen rebels",
        "disposition": "distinct_pre_imamate_composite_actor_event",
        "owner_event_id": "hced_hced_anapa1789_1",
        "boundary_note": "Forty years before Ghazi Muhammad's imamate; no identity continuity.",
    },
    "hced-Grozny1995-1": {
        "raw_row_sha256": _ADJACENT_ROW_HASHES["hced-Grozny1995-1"],
        "literal_label": "chechen rebels",
        "disposition": "distinct_post_soviet_chechen_conflict",
        "owner_event_id": None,
        "boundary_note": "A post-Soviet actor cannot inherit Shamil's 1834-1859 Elo.",
    },
    "hced-Grozny2000-1": {
        "raw_row_sha256": _ADJACENT_ROW_HASHES["hced-Grozny2000-1"],
        "literal_label": "chechen rebels",
        "disposition": "distinct_post_soviet_chechen_conflict",
        "owner_event_id": None,
        "boundary_note": "A post-Soviet actor cannot inherit Shamil's 1834-1859 Elo.",
    },
}


WAVE8_MURIDS_ADJACENT_LITERAL_LABEL_INVENTORY: dict[str, frozenset[str]] = {
    "caucasian imamate": frozenset(),
    "chechen rebels": frozenset({"hced-Grozny1995-1", "hced-Grozny2000-1"}),
    "chechnya": frozenset(),
    "dagestan": frozenset(WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS),
    "ichkeria": frozenset(),
    "imamate": frozenset(),
    "murids": WAVE8_MURIDS_EXPECTED_CANDIDATE_IDS,
    "ottoman empire chechen rebels": frozenset({"hced-Anapa1789-1"}),
}


WAVE8_MURIDS_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Gimrah1832-1": {
        "aliases": tuple(
            sorted(
                {
                    "assault of gimrah",
                    "assault of gimry",
                    "battle of gimrah",
                    "battle of gimry",
                    "gimrah",
                    "gimry",
                }
            )
        ),
        "years": (1832, 1832),
    },
    "hced-Darghiyya1842-1": {
        "aliases": tuple(
            sorted(
                {
                    "battle of ichkeria",
                    "dargo expedition 1842",
                    "darghiyya",
                    "grabbe dargo expedition",
                    "ichkeria expedition",
                    "itchkeri expedition",
                }
            )
        ),
        "years": (1842, 1842),
    },
    "hced-Darghiyya1845-1": {
        "aliases": tuple(
            sorted(
                {
                    "battle of dargo",
                    "darghiyya",
                    "dargin expedition",
                    "dargo campaign",
                    "dargo expedition",
                    "dargo expedition 1845",
                    "vorontsov dargo expedition",
                }
            )
        ),
        "years": (1845, 1845),
    },
    "hced-Gunib1859-1": {
        "aliases": tuple(
            sorted(
                {
                    "assault of ghunib",
                    "assault of gunib",
                    "battle of ghunib",
                    "battle of gunib",
                    "capture of gunib",
                    "ghunib",
                    "gunib",
                    "siege of ghunib",
                    "siege of gunib",
                    "storming of gunib",
                }
            )
        ),
        "years": (1859, 1859),
    },
}
WAVE8_MURIDS_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_MURIDS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_MURIDS_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


WAVE8_MURIDS_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"dagestan_lane:{candidate_id}": disposition
        for candidate_id, disposition in WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS.items()
    },
    **{
        f"adjacent_hced:{candidate_id}": disposition
        for candidate_id, disposition in WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS.items()
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(map(str, values))))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _signature_payload() -> dict[str, Any]:
    return {
        "adjacent_hced_dispositions": WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS,
        "adjacent_literal_label_inventory": {
            label: sorted(candidate_ids)
            for label, candidate_ids in (
                WAVE8_MURIDS_ADJACENT_LITERAL_LABEL_INVENTORY.items()
            )
        },
        "contracts": WAVE8_MURIDS_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_MURIDS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "dagestan_lane_dispositions": WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS,
        "entities": WAVE8_MURIDS_ENTITIES,
        "existing_lane_overlap_audit": WAVE8_MURIDS_EXISTING_LANE_OVERLAP_AUDIT,
        "existing_release_duplicate_dispositions": (
            WAVE8_MURIDS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_MURIDS_EXPECTED_CANDIDATE_IDS),
        "funnel_audit": WAVE8_MURIDS_FUNNEL_AUDIT,
        "holds": WAVE8_MURIDS_HOLDS,
        "integration_dispositions": WAVE8_MURIDS_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_MURIDS_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_MURIDS_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_MURIDS_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_MURIDS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(WAVE8_MURIDS_POINT_QUARANTINE_ADDITIONS),
        "scope_and_opposite_result_audit": WAVE8_MURIDS_SCOPE_AND_OPPOSITE_RESULT_AUDIT,
        "sources": WAVE8_MURIDS_SOURCES,
        "terminal_exclusions": WAVE8_MURIDS_TERMINAL_EXCLUSIONS,
    }


def wave8_murids_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_MURIDS_FINAL_AUDIT_SIGNATURE = (
    "6b312e21d254917756958209cf5a136072231b88b9a3e52c2c2139849ae318d8"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_MURIDS_CONTRACTS),
        len(WAVE8_MURIDS_HOLDS),
        len(WAVE8_MURIDS_TERMINAL_EXCLUSIONS),
    ) != (4, 0, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if WAVE8_MURIDS_ENTITIES or len(WAVE8_MURIDS_SOURCES) != 9:
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_MURIDS_RESERVED_IDS != WAVE8_MURIDS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if set(WAVE8_MURIDS_ROW_DISPOSITIONS) != WAVE8_MURIDS_RESERVED_IDS or set(
        WAVE8_MURIDS_ROW_DISPOSITIONS.values()
    ) != {"promote"}:
        raise ValueError(f"{_LANE_NAME} row dispositions changed")
    if _sorted_newline_sha256(WAVE8_MURIDS_EXPECTED_CANDIDATE_IDS) != (
        WAVE8_MURIDS_EXACT_CANDIDATE_ID_SHA256
    ):
        raise ValueError(f"{_LANE_NAME} exact-candidate digest changed")
    if (
        WAVE8_MURIDS_FINAL_AUDIT_SIGNATURE != "__PENDING__"
        and wave8_murids_audit_signature() != WAVE8_MURIDS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    source_by_id = {str(source["id"]): source for source in WAVE8_MURIDS_SOURCES}
    if len(source_by_id) != len(WAVE8_MURIDS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(
        {str(source["source_family_id"]) for source in WAVE8_MURIDS_SOURCES}
    ) != len(WAVE8_MURIDS_SOURCES):
        raise ValueError(f"{_LANE_NAME} source families are not unique")
    for source in WAVE8_MURIDS_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    if set(WAVE8_MURIDS_EXISTING_LANE_OVERLAP_AUDIT) != (
        WAVE8_MURIDS_REQUIRED_EXISTING_ENTITY_IDS
    ) or WAVE8_MURIDS_REQUIRED_EXISTING_ENTITY_IDS != {
        _GHAZI_IMAMATE_ID,
        _SHAMIL_IMAMATE_ID,
        _RUSSIAN_EMPIRE_ID,
    }:
        raise ValueError(f"{_LANE_NAME} existing entity dependency changed")
    for entity_id, disposition in WAVE8_MURIDS_EXISTING_LANE_OVERLAP_AUDIT.items():
        if disposition["candidate_id_overlap"]:
            raise ValueError(f"{_LANE_NAME} reowns an existing lane candidate")
        if int(disposition["start_year"]) > int(disposition["end_year"]):
            raise ValueError(f"{_LANE_NAME} existing identity window is invalid")
        if normalize_label(disposition["name"]) in {
            "murids",
            "dagestan",
            "chechnya",
            "muslims",
        }:
            raise ValueError(f"{_LANE_NAME} depends on a generic actor identity")

    expected_sides = {
        "hced-Gimrah1832-1": (
            {_RUSSIAN_EMPIRE_ID},
            {_GHAZI_IMAMATE_ID},
            1,
            "engagement",
        ),
        "hced-Darghiyya1842-1": (
            {_SHAMIL_IMAMATE_ID},
            {_RUSSIAN_EMPIRE_ID},
            1,
            "campaign",
        ),
        "hced-Darghiyya1845-1": (
            {_SHAMIL_IMAMATE_ID},
            {_RUSSIAN_EMPIRE_ID},
            1,
            "campaign",
        ),
        "hced-Gunib1859-1": (
            {_RUSSIAN_EMPIRE_ID},
            {_SHAMIL_IMAMATE_ID},
            1,
            "engagement",
        ),
    }
    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_MURIDS_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_MURIDS_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} raw-row fingerprint changed")
        row_hash = str(contract["raw_row_sha256"])
        if len(row_hash) != 64 or any(c not in "0123456789abcdef" for c in row_hash):
            raise ValueError(f"{_LANE_NAME} raw-row hash is invalid")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event changed")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        expected_1, expected_2, winner_side, event_type = expected_sides[candidate_id]
        if (side_1, side_2, int(contract["winner_side"]), contract["event_type"]) != (
            expected_1,
            expected_2,
            winner_side,
            event_type,
        ):
            raise ValueError(f"{_LANE_NAME} actor or result composition changed")
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} opposing sides are invalid")
        if not (side_1 | side_2) <= WAVE8_MURIDS_REQUIRED_EXISTING_ENTITY_IDS:
            raise ValueError(f"{_LANE_NAME} uses an unreviewed identity")
        year = int(canonical["year_low"])
        for entity_id in side_1 | side_2:
            disposition = WAVE8_MURIDS_EXISTING_LANE_OVERLAP_AUDIT[entity_id]
            if not int(disposition["start_year"]) <= year <= int(
                disposition["end_year"]
            ):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        used_entities.update(side_1 | side_2)
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or "winner_side" not in contract
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or not set(evidence) <= set(source_by_id)
            or len(outcomes) < 2
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} outcome evidence changed")
        expected_families = sorted(
            {str(source_by_id[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} independent source families changed")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        if not contract["reviewed_sides"] or not contract["reviewed_outcome"]:
            raise ValueError(f"{_LANE_NAME} participant audit changed")
        used_sources.update(evidence)
    if used_entities != WAVE8_MURIDS_REQUIRED_EXISTING_ENTITY_IDS:
        raise ValueError(f"{_LANE_NAME} existing identities are not exactly consumed")
    if WAVE8_MURIDS_CAMPAIGN_CONTRACT_IDS != {
        "hced-Darghiyya1842-1",
        "hced-Darghiyya1845-1",
    }:
        raise ValueError(f"{_LANE_NAME} campaign inventory changed")

    if set(WAVE8_MURIDS_SCOPE_AND_OPPOSITE_RESULT_AUDIT) != (
        WAVE8_MURIDS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} scope audit is incomplete")
    for candidate_id, audit in WAVE8_MURIDS_SCOPE_AND_OPPOSITE_RESULT_AUDIT.items():
        contract = WAVE8_MURIDS_CONTRACTS[candidate_id]
        if audit["audited_unit"] != contract["canonical_event"]["granularity"]:
            raise ValueError(f"{_LANE_NAME} campaign-versus-battle scope changed")
        if not audit["opposite_result_disposition"] or not audit["scope_note"]:
            raise ValueError(f"{_LANE_NAME} opposite-result audit changed")

    if set(WAVE8_MURIDS_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_MURIDS_CONTRACT_IDS
    ) or WAVE8_MURIDS_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_MURIDS_CONTRACT_IDS
    ) or WAVE8_MURIDS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} location quarantine changed")
    for review in WAVE8_MURIDS_LOCATION_QUARANTINE_REASONS.values():
        if review["actions"] != ["withhold_point"] or review["retained_country"] != (
            "Russia"
        ):
            raise ValueError(f"{_LANE_NAME} location disposition changed")
        evidence = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence changed")
        used_sources.update(evidence)
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")

    if set(WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS) != set(_DAGESTAN_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} Dagestan lane audit changed")
    if set(WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS) != set(_ADJACENT_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} adjacent HCED audit changed")
    if set(WAVE8_MURIDS_ADJACENT_LITERAL_LABEL_INVENTORY) != {
        "caucasian imamate",
        "chechen rebels",
        "chechnya",
        "dagestan",
        "ichkeria",
        "imamate",
        "murids",
        "ottoman empire chechen rebels",
    }:
        raise ValueError(f"{_LANE_NAME} adjacent literal-label audit changed")
    expected_integration = {
        *(f"dagestan_lane:{item}" for item in _DAGESTAN_ROW_HASHES),
        *(f"adjacent_hced:{item}" for item in _ADJACENT_ROW_HASHES),
    }
    if set(WAVE8_MURIDS_INTEGRATION_DISPOSITIONS) != expected_integration:
        raise ValueError(f"{_LANE_NAME} integration disposition audit changed")
    if set(WAVE8_MURIDS_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_MURIDS_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} IWBD negative audit is incomplete")
    for item in WAVE8_MURIDS_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, item["aliases"]))
        if not _is_sorted_unique(aliases) or aliases != list(
            map(normalize_label, aliases)
        ):
            raise ValueError(f"{_LANE_NAME} alternate-name audit changed")
        low, high = map(int, item["years"])
        if low > high:
            raise ValueError(f"{_LANE_NAME} duplicate interval changed")
    if (
        WAVE8_MURIDS_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_MURIDS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_MURIDS_OUTCOME_OVERRIDES
    ):
        raise ValueError(f"{_LANE_NAME} acquired an undeclared duplicate or override")


def validate_wave8_murids_existing_entities(
    release_entities: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    """Fail closed if a reused regime or its continuity firewall changes."""

    _validate_static()
    for entity_id, expected in WAVE8_MURIDS_EXISTING_LANE_OVERLAP_AUDIT.items():
        entity = release_entities.get(entity_id)
        if entity is None:
            raise ValueError(f"{_LANE_NAME} missing required existing entity: {entity_id}")
        actual = {
            "name": str(entity.get("name")),
            "kind": str(entity.get("kind")),
            "start_year": int(entity["start_year"]),
            "end_year": int(entity["end_year"]),
        }
        pinned = {
            "name": str(expected["name"]),
            "kind": str(expected["kind"]),
            "start_year": int(expected["start_year"]),
            "end_year": int(expected["end_year"]),
        }
        if actual != pinned:
            raise ValueError(f"{_LANE_NAME} existing entity boundary changed: {entity_id}")
        aliases = {normalize_label(alias) for alias in entity.get("aliases", [])}
        if aliases & {"murids", "murid", "dagestan", "chechnya"}:
            raise ValueError(f"{_LANE_NAME} existing entity gained a generic alias")
        if entity_id in {_GHAZI_IMAMATE_ID, _SHAMIL_IMAMATE_ID}:
            note = normalize_label(entity.get("continuity_note"))
            if "no rating is inherited" not in note:
                raise ValueError(f"{_LANE_NAME} imamate continuity firewall changed")
    return {
        "new_entities": 0,
        "reused_time_bounded_entities": len(
            WAVE8_MURIDS_REQUIRED_EXISTING_ENTITY_IDS
        ),
    }


def _is_exact_label(value: Any) -> bool:
    return normalize_label(value) == _EXACT_LABEL


def validate_wave8_murids_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin all and only the four literal ``Murids`` source rows."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_MURIDS_CONTRACTS,
        WAVE8_MURIDS_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_label(row.get("side_1_raw"))
        or _is_exact_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_MURIDS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed: {sorted(exact_ids)}")
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id"))
        if candidate_id not in WAVE8_MURIDS_RESERVED_IDS:
            continue
        exact_sides = sum(
            _is_exact_label(row.get(field)) for field in ("side_1_raw", "side_2_raw")
        )
        if exact_sides != 1:
            raise ValueError(f"{_LANE_NAME} exact-side ownership changed: {candidate_id}")

    literal_actual: dict[str, set[str]] = {
        label: set() for label in WAVE8_MURIDS_ADJACENT_LITERAL_LABEL_INVENTORY
    }
    for row in hced_rows:
        candidate_id = str(row.get("candidate_id"))
        for field in ("side_1_raw", "side_2_raw"):
            label = normalize_label(row.get(field))
            if label in literal_actual:
                literal_actual[label].add(candidate_id)
    expected = {
        label: set(candidate_ids)
        for label, candidate_ids in WAVE8_MURIDS_ADJACENT_LITERAL_LABEL_INVENTORY.items()
    }
    if literal_actual != expected:
        raise ValueError(f"{_LANE_NAME} adjacent literal-label inventory changed")
    return {
        "holds": len(WAVE8_MURIDS_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_MURIDS_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_murids_funnel(
    funnel: Mapping[str, Any],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin the sole-blocker funnel while allowing a fully integrated release."""

    _validate_static()
    overlap = {
        str(event.get("hced_candidate_id"))
        for event in existing_events
        if event.get("hced_candidate_id") in WAVE8_MURIDS_CONTRACT_IDS
    }
    if overlap not in (set(), set(WAVE8_MURIDS_CONTRACT_IDS)):
        raise ValueError(f"{_LANE_NAME} release overlap is partial")
    labels = funnel.get("labels")
    if not isinstance(labels, list):
        raise ValueError(f"{_LANE_NAME} funnel labels are unavailable")
    matching = [item for item in labels if item.get("label") == _EXACT_LABEL]
    if not matching and overlap == set(WAVE8_MURIDS_CONTRACT_IDS):
        return {"events_touched": 4, "sole_blocker_events": 4}
    if len(matching) != 1:
        raise ValueError(f"{_LANE_NAME} expected one unresolved funnel label row")
    label = matching[0]
    for field, expected in WAVE8_MURIDS_FUNNEL_AUDIT.items():
        if label.get(field) != expected:
            raise ValueError(f"{_LANE_NAME} funnel field changed: {field}")

    row_label_data = funnel.get("row_label_data")
    if not isinstance(row_label_data, list):
        raise ValueError(f"{_LANE_NAME} funnel row-label data are unavailable")
    audited: dict[str, Mapping[str, Any]] = {}
    for row in row_label_data:
        failures = row.get("label_failures")
        if isinstance(failures, list) and any(
            failure.get("label") == _EXACT_LABEL for failure in failures
        ):
            audited[str(row.get("candidate_id"))] = row
    if set(audited) != WAVE8_MURIDS_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} funnel row inventory changed")
    for candidate_id, row in audited.items():
        if (
            row.get("sole_blocker_label") != _EXACT_LABEL
            or row.get("blocker_labels") != [_EXACT_LABEL]
            or row.get("other_blockers") != []
            or row.get("resolved_counterpart_entity_ids") != [_RUSSIAN_EMPIRE_ID]
        ):
            raise ValueError(f"{_LANE_NAME} sole-blocker row changed: {candidate_id}")
    return {"events_touched": 4, "sole_blocker_events": 4}


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


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {normalize_label(row.get("name"))}
    aliases = row.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]
    if isinstance(aliases, (list, tuple, set)):
        names.update(normalize_label(alias) for alias in aliases)
    return {name for name in names if name}


_DUPLICATE_MATCH_KEYS = {
    (year, normalize_label(alias))
    for item in WAVE8_MURIDS_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(item["years"][0]), int(item["years"][1]) + 1)
    for alias in item["aliases"]
}


def _probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return any((year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row))


def validate_wave8_murids_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Audit neighboring ownership and fail on a future probable duplicate."""

    validate_wave8_murids_queue_contracts(hced_rows)
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        indexed.setdefault(str(row.get("candidate_id")), []).append(row)
    related = {
        **WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS,
        **WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS,
    }
    for candidate_id, disposition in related.items():
        rows = indexed.get(candidate_id, [])
        if len(rows) != 1 or canonical_hced_row_sha256(rows[0]) != disposition[
            "raw_row_sha256"
        ]:
            raise ValueError(f"{_LANE_NAME} related HCED row changed: {candidate_id}")

    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _probable_twin(row)
    )
    if iwbd_twins:
        raise ValueError(f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_twins}")

    existing = list(existing_events)
    overlap_events = [
        event
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_MURIDS_CONTRACT_IDS
    ]
    overlap_ids = {str(event.get("hced_candidate_id")) for event in overlap_events}
    if overlap_ids not in (set(), set(WAVE8_MURIDS_CONTRACT_IDS)):
        raise ValueError(f"{_LANE_NAME} release candidate overlap is partial")
    for event in overlap_events:
        if not str(event.get("id", "")).startswith(_EVENT_ID_PREFIX):
            raise ValueError(f"{_LANE_NAME} release candidate has a foreign owner")

    if existing:
        by_event_id = {str(event.get("id")): event for event in existing}
        for disposition in WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS.values():
            owner_event_id = str(disposition["owner_event_id"])
            event = by_event_id.get(owner_event_id)
            if event is None or event.get("hced_candidate_id") not in (
                WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS
            ):
                raise ValueError(f"{_LANE_NAME} Dagestan owner event changed")
        anapa_owner = WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS[
            "hced-Anapa1789-1"
        ]["owner_event_id"]
        if str(anapa_owner) not in by_event_id:
            raise ValueError(f"{_LANE_NAME} adjacent Anapa owner event changed")

    related_ids = set(related)
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id") not in WAVE8_MURIDS_CONTRACT_IDS
        and event.get("hced_candidate_id") not in related_ids
        and _probable_twin(event)
    )
    if release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_twins}"
        )
    return {
        "adjacent_hced_dispositions": len(
            WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS
        ),
        "dagestan_lane_dispositions": len(
            WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS
        ),
        "existing_release_duplicate_dispositions": 0,
        "integration_dispositions": len(WAVE8_MURIDS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "release_lane_overlap": len(overlap_ids),
    }


def install_wave8_murids_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_MURIDS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_murids_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_MURIDS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_event_review(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        contract = WAVE8_MURIDS_CONTRACTS[candidate_id]
        if candidate_id in WAVE8_MURIDS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_MURIDS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)
        event_type = str(contract["event_type"])
        event["event_type"] = event_type
        if event_type == "campaign":
            event["summary"] = (
                "Candidate-keyed Wave 8 operational campaign assertion. The "
                "complete HCED row, expedition boundary, time-bounded identities, "
                "and independent outcome evidence are pinned; no point battle, "
                "component-action duplicate, or whole-war result is invented. "
                + str(contract["audit_note"])
            )
            operationalize_campaign_outcomes(event)
            for participant in event["participants"]:
                if participant["side"] == "side_a":
                    participant["termination"] = "campaign_victory"
                    participant["result_class"] = "operational_campaign_victory"
                else:
                    participant["termination"] = "campaign_defeat"
                    participant["result_class"] = "operational_campaign_defeat"
                participant["note"] = (
                    f"Candidate-keyed {_LANE_NAME} operational contract; no generic "
                    "label fallback, component-action duplicate, or whole-war result."
                )


def promote_wave8_murids_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit four bounded outcomes and no generic-Murid identity."""

    validate_wave8_murids_queue_contracts(hced_rows)
    validate_wave8_murids_existing_entities(release_entities)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_MURIDS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_event_review(events)
    return events


def wave8_murids_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_MURIDS_CONTRACTS.values()
            ).items()
        )
    )


def wave8_murids_counts() -> dict[str, int]:
    _validate_static()
    return {
        "adjacent_hced_dispositions": len(
            WAVE8_MURIDS_ADJACENT_HCED_DISPOSITIONS
        ),
        "campaign_events": len(WAVE8_MURIDS_CAMPAIGN_CONTRACT_IDS),
        "country_quarantine_additions": len(
            WAVE8_MURIDS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "dagestan_lane_dispositions": len(
            WAVE8_MURIDS_DAGESTAN_LANE_DISPOSITIONS
        ),
        "engagement_events": len(
            WAVE8_MURIDS_CONTRACT_IDS - WAVE8_MURIDS_CAMPAIGN_CONTRACT_IDS
        ),
        "existing_lane_overlap_audits": len(
            WAVE8_MURIDS_EXISTING_LANE_OVERLAP_AUDIT
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_MURIDS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_MURIDS_HOLDS),
        "integration_dispositions": len(WAVE8_MURIDS_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_MURIDS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_MURIDS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_MURIDS_ENTITIES),
        "new_sources": len(WAVE8_MURIDS_SOURCES),
        "newly_rated_events": len(WAVE8_MURIDS_CONTRACTS),
        "outcome_overrides": len(WAVE8_MURIDS_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_MURIDS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_MURIDS_CONTRACTS),
        "required_existing_entities": len(
            WAVE8_MURIDS_REQUIRED_EXISTING_ENTITY_IDS
        ),
        "reviewed_hced_rows": len(WAVE8_MURIDS_EXPECTED_CANDIDATE_IDS),
        "sole_blocker_rows": int(WAVE8_MURIDS_FUNNEL_AUDIT["sole_blocker_events"]),
        "terminal_exclusions": len(WAVE8_MURIDS_TERMINAL_EXCLUSIONS),
    }


def wave8_murids_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_MURIDS_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_MURIDS_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_murids_row_dispositions() -> dict[str, str]:
    _validate_static()
    return dict(WAVE8_MURIDS_ROW_DISPOSITIONS)


def wave8_murids_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "audit": "candidate_keyed_exact_label_with_time_bounded_regime_reuse",
        "counts": wave8_murids_counts(),
        "cohorts": wave8_murids_cohort_counts(),
        "final_audit_signature": WAVE8_MURIDS_FINAL_AUDIT_SIGNATURE,
        "module_owner": _MODULE_OWNER,
        "row_dispositions": wave8_murids_row_dispositions(),
    }
