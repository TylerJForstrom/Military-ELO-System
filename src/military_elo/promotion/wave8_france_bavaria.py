"""Audited Wave 8 lane for HCED's exact ``France, Bavaria`` label.

The four locked rows describe Napoleonic field forces, not a durable compound
polity.  The three rateable engagements therefore split the compound into the
already-curated First French Empire and Kingdom of Bavaria identities.  The
Gefrees winner additionally receives one event-bounded identity for the Black
Brunswick and Hesse-Kassel free corps that fought with Kienmayer's Austrians.

Gefrees, Neumarkt-Sankt Veit, and the Second Battle of Polotsk have independently
attested tactical winners.  Accounts of the First Battle of Polotsk conflict at
the rating granularity, so it remains an explicit unknown hold.  Unknown is
never converted to a draw, and no label fallback, continuity bridge, outcome
override, location assertion, or duplicate event is introduced here.
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
    "WAVE8_FRANCE_BAVARIA_CONTRACT_IDS",
    "WAVE8_FRANCE_BAVARIA_CONTRACTS",
    "WAVE8_FRANCE_BAVARIA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_FRANCE_BAVARIA_CROSS_LANE_DISPOSITIONS",
    "WAVE8_FRANCE_BAVARIA_ENTITIES",
    "WAVE8_FRANCE_BAVARIA_EXCLUSIONS",
    "WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT",
    "WAVE8_FRANCE_BAVARIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS",
    "WAVE8_FRANCE_BAVARIA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_FRANCE_BAVARIA_FUNNEL_AUDIT",
    "WAVE8_FRANCE_BAVARIA_HOLD_IDS",
    "WAVE8_FRANCE_BAVARIA_HOLDS",
    "WAVE8_FRANCE_BAVARIA_INTEGRATION_DISPOSITIONS",
    "WAVE8_FRANCE_BAVARIA_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_FRANCE_BAVARIA_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_FRANCE_BAVARIA_LOCATION_REVIEWS",
    "WAVE8_FRANCE_BAVARIA_NONPROMOTIONS",
    "WAVE8_FRANCE_BAVARIA_OUTCOME_OVERRIDES",
    "WAVE8_FRANCE_BAVARIA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_FRANCE_BAVARIA_REGIME_ENTITY_DISPOSITIONS",
    "WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS",
    "WAVE8_FRANCE_BAVARIA_REQUIRED_EXISTING_ENTITY_IDS",
    "WAVE8_FRANCE_BAVARIA_RESERVED_IDS",
    "WAVE8_FRANCE_BAVARIA_ROW_DISPOSITIONS",
    "WAVE8_FRANCE_BAVARIA_ROW_HASHES",
    "WAVE8_FRANCE_BAVARIA_SOURCES",
    "WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSION_IDS",
    "WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS",
    "install_wave8_france_bavaria_entities",
    "install_wave8_france_bavaria_sources",
    "promote_wave8_france_bavaria_contracts",
    "validate_wave8_france_bavaria_existing_entities",
    "validate_wave8_france_bavaria_funnel",
    "validate_wave8_france_bavaria_integration_dispositions",
    "validate_wave8_france_bavaria_queue_contracts",
    "wave8_france_bavaria_audit_signature",
    "wave8_france_bavaria_cohort_counts",
    "wave8_france_bavaria_counts",
    "wave8_france_bavaria_location_quarantine_additions",
    "wave8_france_bavaria_metadata",
    "wave8_france_bavaria_row_dispositions",
)


_LANE_NAME = "Wave 8 France-Bavaria exact-label audit"
_MODULE_OWNER = "wave8_france_bavaria"
_EVENT_ID_PREFIX = "hced_wave8_france_bavaria_"
_EXACT_LABEL = "france bavaria"
_REVERSE_LABEL = "bavaria france"

_AUSTRIAN_EMPIRE_ID = "austrian_empire"
_FIRST_FRENCH_EMPIRE_ID = "first_french_empire"
_KINGDOM_BAVARIA_ID = "kingdom_bavaria_1806"
_RUSSIAN_EMPIRE_ID = "russian_empire"
_GEFREES_FREE_CORPS_ID = "black_brunswick_hesse_kassel_free_corps_gefrees_1809"


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


WAVE8_FRANCE_BAVARIA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_france_bavaria_gill_with_eagles",
        "With Eagles to Glory: Napoleon and His German Allies in the 1809 Campaign",
        "https://www.casematepublishers.com/9781784383107/with-eagles-to-glory/",
        "Greenhill Books; Casemate Publishers",
        "scholarly_military_history_monograph",
        "gill_with_eagles_to_glory",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_france_bavaria_bamberg_gefrees",
        "Noth, Thränen und Excesse aller Art: Der Krieg von 1806/07 in Franken",
        (
            "https://fis.uni-bamberg.de/bitstreams/"
            "20ed743a-9bb6-49f6-887a-123f78db4827/download"
        ),
        "University of Bamberg",
        "academic_historical_study",
        "bamberg_gefrees_study",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_france_bavaria_mcgill_fifth_coalition",
        "The Fifth Coalition, 1809: Chronology",
        "https://digital.library.mcgill.ca/napoleon/english/timeline-5th.htm",
        "McGill University Napoleon Collection",
        "academic_library_curated_chronology",
        "mcgill_napoleon_fifth_coalition_timeline",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_france_bavaria_gill_neumarkt",
        "1809: Thunder on the Danube, Volume II",
        "https://www.casematepublishers.com/9781848327580/1809-thunder-on-the-danube/",
        "Frontline Books; Casemate Publishers",
        "scholarly_military_history_monograph",
        "gill_thunder_danube_volume_two",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_france_bavaria_bavarian_general_staff_1809",
        "Der Feldzug von 1809 in Süddeutschland",
        "https://www.digitale-sammlungen.de/de/view/bsb10347307",
        "Bavarian General Staff; Bavarian State Library digitization",
        "official_military_history",
        "bavarian_general_staff_campaign_1809",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_france_bavaria_thiers_neumarkt",
        "History of the Consulate and the Empire of France, Volume X",
        (
            "https://upload.wikimedia.org/wikipedia/commons/0/0a/"
            "History_of_the_Consulate_and_the_Empire_of_France_Under_Napoleon%"
            "2C_20_Vols.%28Vol.X%29_%28IA_dli.granth.40667%29.pdf"
        ),
        "Internet Archive scan via Wikimedia Commons",
        "digitized_nineteenth_century_history",
        "thiers_consulate_empire_volume_ten",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_france_bavaria_fondation_napoleon_1812",
        "Napoleon's Russian Campaign: From the Niemen to Moscow",
        (
            "https://www.napoleon.org/en/history-of-the-two-empires/timelines/"
            "napoleons-russian-campaign-from-the-niemen-to-moscow/"
        ),
        "Fondation Napoléon",
        "institutional_curated_history",
        "fondation_napoleon_russian_campaign_timeline",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_france_bavaria_russian_encyclopedia_polotsk",
        "Polotsk Battles of 1812",
        "https://old.bigenc.ru/military_science/text/3155926",
        "Great Russian Encyclopedia",
        "national_scholarly_encyclopedia",
        "great_russian_encyclopedia_polotsk",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_france_bavaria_foord_1812",
        "Napoleon's Russian Campaign of 1812",
        "https://www.gutenberg.org/cache/epub/57185/pg57185-images.html",
        "Project Gutenberg digitization of Edward Foord",
        "digitized_scholarly_military_history",
        "foord_russian_campaign_1812",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_france_bavaria_napoleon_series_polotsk_first",
        "The First Battle of Polotsk",
        (
            "https://www.napoleon-series.org/military-info/battles/1812/"
            "Russia/Pultusk/PultuskChapter5.pdf"
        ),
        "The Napoleon Series",
        "scholarly_campaign_study",
        "napoleon_series_polotsk_chapter_five",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_france_bavaria_napoleon_series_polotsk_second",
        "The Second Battle of Polotsk",
        (
            "https://www.napoleon-series.org/military-info/battles/1812/"
            "Russia/Pultusk/PultuskChapter6.pdf"
        ),
        "The Napoleon Series",
        "scholarly_campaign_study",
        "napoleon_series_polotsk_chapter_six",
        outcome=True,
        crosscheck=True,
    ),
)


WAVE8_FRANCE_BAVARIA_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _GEFREES_FREE_CORPS_ID,
        "name": "Black Brunswick and Hesse-Kassel free corps at Gefrees (1809)",
        "kind": "event_bounded_volunteer_free_corps_coalition",
        "start_year": 1809,
        "end_year": 1809,
        "region": "Franconia, Central Europe",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the Black Brunswick and attached Hesse-Kassel free-corps "
            "contingents that fought with Kienmayer's Austrian force at Gefrees. "
            "No rating is inherited from or transferred to the Duchy of "
            "Brunswick, Hesse-Kassel, a dynasty, a later state, another coalition, "
            "or any formation in another campaign."
        ),
        "source_ids": [
            "wave8_france_bavaria_bamberg_gefrees",
            "wave8_france_bavaria_gill_with_eagles",
        ],
    },
)


WAVE8_FRANCE_BAVARIA_REGIME_ENTITY_DISPOSITIONS: dict[str, dict[str, Any]] = {
    _AUSTRIAN_EMPIRE_ID: {
        "name": "Austrian Empire",
        "kind": "empire",
        "start_year": 1804,
        "end_year": 1867,
        "disposition": "reuse_curated_time_bounded_regime",
        "actor_use": "Kienmayer and Hiller Austrian formations in 1809",
    },
    _FIRST_FRENCH_EMPIRE_ID: {
        "name": "First French Empire",
        "kind": "empire",
        "start_year": 1804,
        "end_year": 1815,
        "disposition": "reuse_curated_time_bounded_regime",
        "actor_use": "French imperial formations in all three promoted events",
    },
    _KINGDOM_BAVARIA_ID: {
        "name": "Kingdom of Bavaria",
        "kind": "kingdom",
        "start_year": 1806,
        "end_year": 1918,
        "disposition": "reuse_wave7_west_time_bounded_regime",
        "actor_use": "Bavarian contingents in all three promoted events",
    },
    _RUSSIAN_EMPIRE_ID: {
        "name": "Russian Empire",
        "kind": "empire",
        "start_year": 1721,
        "end_year": 1917,
        "disposition": "reuse_curated_time_bounded_regime",
        "actor_use": "Wittgenstein and Steinheil Russian formations at Polotsk",
    },
}
WAVE8_FRANCE_BAVARIA_REQUIRED_EXISTING_ENTITY_IDS = frozenset(
    WAVE8_FRANCE_BAVARIA_REGIME_ENTITY_DISPOSITIONS
)


WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    _AUSTRIAN_EMPIRE_ID: {
        "existing_owner": "curated_release_and_central_europe_lanes",
        "candidate_id_overlap": [],
        "identity_window": [1804, 1867],
        "disposition": "reuse_identity_without_reowning_existing_events",
    },
    _FIRST_FRENCH_EMPIRE_ID: {
        "existing_owner": "curated_release_and_france_lanes",
        "candidate_id_overlap": [],
        "identity_window": [1804, 1815],
        "disposition": "reuse_identity_without_reowning_existing_events",
    },
    _KINGDOM_BAVARIA_ID: {
        "existing_owner": "wave7_west_bavaria_sequence",
        "candidate_id_overlap": [],
        "identity_window": [1806, 1918],
        "disposition": "reuse_identity_without_reowning_existing_events",
    },
    _RUSSIAN_EMPIRE_ID: {
        "existing_owner": "curated_release_and_russia_lanes",
        "candidate_id_overlap": [],
        "identity_window": [1721, 1917],
        "disposition": "reuse_identity_without_reowning_existing_events",
    },
}


WAVE8_FRANCE_BAVARIA_ROW_HASHES: dict[str, str] = {
    "hced-Gefrees1809-1": (
        "1eebf3bcb95339c334947717efe368c4235a7ea21d45d24312c580bb7d9329c9"
    ),
    "hced-Neumarkt-St-Viet1809-1": (
        "d621c1fc1466c6dd060f2d7be726bb001c576db1e938d198ea67adf3643f43e1"
    ),
    "hced-Polotsk (1st)1812-1": (
        "c2cea72b37d778e14f56cf3eae8a8aff5110c61672bb1f83d4a01c7ea223923d"
    ),
    "hced-Polotsk (2nd)1812-1": (
        "224b6dbeea50c87978f4aef344cd3b180030f510075984b340f7403f2bf2ad22"
    ),
}


WAVE8_FRANCE_BAVARIA_FUNNEL_AUDIT: dict[str, Any] = {
    "event_candidate_id_sha256": (
        "52b980eb0e9eb8290c1c387871606948063624dbbf7d9d9c069a2eef6fff3b22"
    ),
    "events_touched": 4,
    "unresolved_side_attempts": 4,
    "sole_blocker_events": 4,
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 0,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 4,
    },
    "centuries": {"CE_19": 4},
    "components_touched": 1,
    "components_bridged": 0,
    "rated_counterpart_entities": 2,
    "label": _EXACT_LABEL,
    "resolved_counterpart_entity_ids": {
        "hced-Gefrees1809-1": [_AUSTRIAN_EMPIRE_ID],
        "hced-Neumarkt-St-Viet1809-1": [_AUSTRIAN_EMPIRE_ID],
        "hced-Polotsk (1st)1812-1": [_RUSSIAN_EMPIRE_ID],
        "hced-Polotsk (2nd)1812-1": [_RUSSIAN_EMPIRE_ID],
    },
}


def _canonical(
    name: str,
    year: int,
    date_text: str,
    *,
    date_precision: str,
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
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    winner_side: int,
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    source_by_id = {
        str(source["id"]): source for source in WAVE8_FRANCE_BAVARIA_SOURCES
    }
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_FRANCE_BAVARIA_ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "interstate_war",
        "confidence": confidence,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(source_by_id[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "audited_compound_split_into_time_bounded_regimes",
        "audit_note": audit_note,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
    }


WAVE8_FRANCE_BAVARIA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Gefrees1809-1": _contract(
        "hced-Gefrees1809-1",
        _canonical(
            "Battle of Gefrees",
            1809,
            "8 July 1809",
            date_precision="day",
        ),
        "fifth_coalition_northern_theatre_1809",
        [_AUSTRIAN_EMPIRE_ID, _GEFREES_FREE_CORPS_ID],
        [_FIRST_FRENCH_EMPIRE_ID, _KINGDOM_BAVARIA_ID],
        1,
        [
            "wave8_france_bavaria_bamberg_gefrees",
            "wave8_france_bavaria_gill_with_eagles",
            "wave8_france_bavaria_mcgill_fifth_coalition",
        ],
        [
            "wave8_france_bavaria_bamberg_gefrees",
            "wave8_france_bavaria_gill_with_eagles",
            "wave8_france_bavaria_mcgill_fifth_coalition",
        ],
        (
            "Kienmayer's Austrian force, including the Black Brunswick and "
            "attached Hesse-Kassel free corps, defeated Junot's French formation "
            "and its Bavarian depot battalion. The raw compound sides are split "
            "without creating a France-Bavaria polity or a Brunswick continuity "
            "bridge; the omitted Hessian component is captured only inside the "
            "event-bounded free-corps coalition."
        ),
        confidence=0.94,
    ),
    "hced-Neumarkt-St-Viet1809-1": _contract(
        "hced-Neumarkt-St-Viet1809-1",
        _canonical(
            "Battle of Neumarkt-Sankt Veit",
            1809,
            "24 April 1809",
            date_precision="day",
        ),
        "fifth_coalition_bavarian_campaign_1809",
        [_AUSTRIAN_EMPIRE_ID],
        [_FIRST_FRENCH_EMPIRE_ID, _KINGDOM_BAVARIA_ID],
        1,
        [
            "wave8_france_bavaria_bavarian_general_staff_1809",
            "wave8_france_bavaria_gill_neumarkt",
            "wave8_france_bavaria_thiers_neumarkt",
        ],
        [
            "wave8_france_bavaria_bavarian_general_staff_1809",
            "wave8_france_bavaria_gill_neumarkt",
            "wave8_france_bavaria_thiers_neumarkt",
        ],
        (
            "Hiller's Austrian left wing defeated Bessières's force, which "
            "combined Wrede's Bavarian division, Molitor's French division, and "
            "French cavalry. The 1809 Habsburg label is assigned to the already "
            "bounded Austrian Empire and the compound loser is split into its "
            "French and Bavarian regimes."
        ),
        confidence=0.96,
    ),
    "hced-Polotsk (2nd)1812-1": _contract(
        "hced-Polotsk (2nd)1812-1",
        _canonical(
            "Second Battle of Polotsk",
            1812,
            "18-20 October 1812",
            date_precision="day_range",
            granularity="multi_day_engagement",
        ),
        "russian_campaign_polotsk_1812",
        [_RUSSIAN_EMPIRE_ID],
        [_FIRST_FRENCH_EMPIRE_ID, _KINGDOM_BAVARIA_ID],
        1,
        [
            "wave8_france_bavaria_foord_1812",
            "wave8_france_bavaria_napoleon_series_polotsk_second",
            "wave8_france_bavaria_russian_encyclopedia_polotsk",
        ],
        [
            "wave8_france_bavaria_foord_1812",
            "wave8_france_bavaria_napoleon_series_polotsk_second",
            "wave8_france_bavaria_russian_encyclopedia_polotsk",
        ],
        (
            "Wittgenstein's and Steinheil's Russian forces compelled Saint-Cyr's "
            "Franco-Bavarian army to evacuate Polotsk, after which Russian forces "
            "occupied the city. A local Bavarian counterattack is not promoted "
            "to the result of the complete multi-day engagement."
        ),
        confidence=0.96,
    ),
}


WAVE8_FRANCE_BAVARIA_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Polotsk (1st)1812-1": {
        "raw_row_sha256": WAVE8_FRANCE_BAVARIA_ROW_HASHES[
            "hced-Polotsk (1st)1812-1"
        ],
        "canonical_event": _canonical(
            "First Battle of Polotsk",
            1812,
            "17-18 August 1812",
            date_precision="day_range",
            granularity="multi_day_engagement",
        ),
        "cohort": "russian_campaign_polotsk_1812",
        "disposition": "hold",
        "hold_category": "historiographically_contested_outcome",
        "reviewed_outcome": "tactical_result_not_uniquely_source_attested",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_actor_description": [
            "Oudinot's French II Corps and Saint-Cyr's Bavarian VI Corps",
            "Wittgenstein's Russian I Corps",
        ],
        "reviewed_granularity": "multi_day_engagement",
        "hold_reason": (
            "Authoritative accounts conflict at the rating granularity: some "
            "describe a French tactical victory after Wittgenstein withdrew, "
            "while the Great Russian Encyclopedia describes failed French attacks "
            "and a failed operational plan. Strategic effect cannot substitute for "
            "a uniquely attested tactical result. This row is not promoted; its "
            "outcome remains unknown and is never encoded as a draw."
        ),
        "evidence_refs": [
            "wave8_france_bavaria_fondation_napoleon_1812",
            "wave8_france_bavaria_foord_1812",
            "wave8_france_bavaria_napoleon_series_polotsk_first",
            "wave8_france_bavaria_russian_encyclopedia_polotsk",
        ],
        "conflicting_outcome_positions": {
            "french_tactical_victory": [
                "wave8_france_bavaria_foord_1812",
                "wave8_france_bavaria_fondation_napoleon_1812",
            ],
            "failed_french_attack_or_russian_success": [
                "wave8_france_bavaria_russian_encyclopedia_polotsk"
            ],
        },
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "provisional_hced_hold",
        },
    }
}


WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {}
WAVE8_FRANCE_BAVARIA_EXCLUSIONS = WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS
WAVE8_FRANCE_BAVARIA_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_FRANCE_BAVARIA_HOLDS,
    **WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS,
}
WAVE8_FRANCE_BAVARIA_CONTRACT_IDS = frozenset(WAVE8_FRANCE_BAVARIA_CONTRACTS)
WAVE8_FRANCE_BAVARIA_HOLD_IDS = frozenset(WAVE8_FRANCE_BAVARIA_HOLDS)
WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS
)
WAVE8_FRANCE_BAVARIA_RESERVED_IDS = frozenset(
    {
        *WAVE8_FRANCE_BAVARIA_CONTRACTS,
        *WAVE8_FRANCE_BAVARIA_NONPROMOTIONS,
    }
)
WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS = frozenset(
    WAVE8_FRANCE_BAVARIA_ROW_HASHES
)
WAVE8_FRANCE_BAVARIA_ROW_DISPOSITIONS = {
    candidate_id: (
        "promote" if candidate_id in WAVE8_FRANCE_BAVARIA_CONTRACT_IDS else "hold"
    )
    for candidate_id in sorted(WAVE8_FRANCE_BAVARIA_RESERVED_IDS)
}


WAVE8_FRANCE_BAVARIA_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_FRANCE_BAVARIA_CONTRACT_IDS
)
WAVE8_FRANCE_BAVARIA_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_FRANCE_BAVARIA_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_FRANCE_BAVARIA_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_FRANCE_BAVARIA_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_FRANCE_BAVARIA_LOCATION_REVIEWS: dict[str, dict[str, Any]] = {
    "hced-Gefrees1809-1": {
        "country_disposition": "retain_germany_if_staged",
        "point_disposition": "quarantine_town_centroid_or_unverified_point",
        "reason": (
            "The engagement spread across the Gefrees, Lützenreuth, Kesselberg, "
            "and Bad Berneck area; no cited source verifies one HCED point as the "
            "battlefield. The modern-country assertion may be retained."
        ),
        "evidence_refs": [
            "wave8_france_bavaria_bamberg_gefrees",
            "wave8_france_bavaria_gill_with_eagles",
        ],
    },
    "hced-Neumarkt-St-Viet1809-1": {
        "country_disposition": "retain_germany_if_staged",
        "point_disposition": "quarantine_city_centroid_or_unverified_point",
        "reason": (
            "The deployment and fighting extended south of Neumarkt and around "
            "the Rott crossing; a city centroid is not an audited battlefield "
            "point. The modern-country assertion may be retained."
        ),
        "evidence_refs": [
            "wave8_france_bavaria_bavarian_general_staff_1809",
            "wave8_france_bavaria_gill_neumarkt",
        ],
    },
    "hced-Polotsk (2nd)1812-1": {
        "country_disposition": "retain_belarus_if_staged",
        "point_disposition": "quarantine_city_centroid_or_unverified_point",
        "reason": (
            "The three-day engagement included field, river, urban, and evacuation "
            "actions; a city centroid cannot represent the complete engagement. "
            "The modern-country assertion may be retained."
        ),
        "evidence_refs": [
            "wave8_france_bavaria_foord_1812",
            "wave8_france_bavaria_russian_encyclopedia_polotsk",
        ],
    },
}


WAVE8_FRANCE_BAVARIA_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}
WAVE8_FRANCE_BAVARIA_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_FRANCE_BAVARIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_FRANCE_BAVARIA_CROSS_LANE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Gefrees1809-1": {
        "aliases": ("battle of gefrees", "gefrees"),
        "years": (1809, 1809),
    },
    "hced-Neumarkt-St-Viet1809-1": {
        "aliases": (
            "battle of neumarkt sankt veit",
            "battle of neumarkt st veit",
            "neumarkt sankt veit",
            "neumarkt st viet",
        ),
        "years": (1809, 1809),
    },
    "hced-Polotsk (1st)1812-1": {
        "aliases": (
            "first battle of polotsk",
            "polotsk 1st",
            "polotsk first",
        ),
        "years": (1812, 1812),
    },
    "hced-Polotsk (2nd)1812-1": {
        "aliases": (
            "polotsk 2nd",
            "polotsk second",
            "second battle of polotsk",
        ),
        "years": (1812, 1812),
    },
}


WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Jacobovo1812-1": {
        "raw_row_sha256": (
            "77ae8eaa411701af3a6d8faa0f83771f57bb6d5e359b8a8af2836e639a1515f1"
        ),
        "disposition": "separate_klyastitsy_jakubowo_engagement",
        "owner_module": "existing_release",
        "reason": (
            "Jacobovo/Jakubowo belongs to the late-July Klyastitsy fighting, not "
            "either August or October Battle of Polotsk. Its existing candidate "
            "ownership is untouched."
        ),
    },
    "hced-Neumarkt1796-1": {
        "raw_row_sha256": (
            "7ecbd24dbdf4cb4861d465dbc460d0380077e6747cded047028fed9043669cdb"
        ),
        "disposition": "separate_1796_neumarkt_engagement",
        "owner_module": "existing_release",
        "reason": "The 1796 event is thirteen years earlier and is not Neumarkt-Sankt Veit.",
    },
    "hced-Polotsk1563-1": {
        "raw_row_sha256": (
            "d95e376f8617a4176b97d021e3c8bcb965d38c2aaf1ae2fb175f44cdcac4f4b0"
        ),
        "disposition": "separate_sixteenth_century_siege",
        "owner_module": None,
        "reason": "The 1563 siege is unrelated to the 1812 Russian campaign.",
    },
    "hced-Polotsk1579-1": {
        "raw_row_sha256": (
            "fc738f56ff035563110c936701085b0562914061eef1ea1c286b38ed8a118582"
        ),
        "disposition": "separate_sixteenth_century_siege",
        "owner_module": "existing_release",
        "reason": "The 1579 siege is unrelated to the 1812 Russian campaign.",
    },
}


WAVE8_FRANCE_BAVARIA_INTEGRATION_DISPOSITIONS: dict[str, dict[str, Any]] = {
    **{
        f"related_hced:{candidate_id}": disposition
        for candidate_id, disposition in (
            WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS.items()
        )
    },
    **{
        f"cross_lane:{candidate_id}": disposition
        for candidate_id, disposition in (
            WAVE8_FRANCE_BAVARIA_CROSS_LANE_DISPOSITIONS.items()
        )
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_FRANCE_BAVARIA_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_FRANCE_BAVARIA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": WAVE8_FRANCE_BAVARIA_CROSS_LANE_DISPOSITIONS,
        "entities": WAVE8_FRANCE_BAVARIA_ENTITIES,
        "existing_lane_overlap_audit": (
            WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT
        ),
        "existing_release_duplicate_dispositions": (
            WAVE8_FRANCE_BAVARIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(
            WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS
        ),
        "funnel_audit": WAVE8_FRANCE_BAVARIA_FUNNEL_AUDIT,
        "holds": WAVE8_FRANCE_BAVARIA_HOLDS,
        "integration_dispositions": WAVE8_FRANCE_BAVARIA_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": (
            WAVE8_FRANCE_BAVARIA_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT,
        "location_reviews": WAVE8_FRANCE_BAVARIA_LOCATION_REVIEWS,
        "outcome_overrides": WAVE8_FRANCE_BAVARIA_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_FRANCE_BAVARIA_POINT_QUARANTINE_ADDITIONS
        ),
        "regime_entity_dispositions": (
            WAVE8_FRANCE_BAVARIA_REGIME_ENTITY_DISPOSITIONS
        ),
        "related_hced_dispositions": (
            WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS
        ),
        "row_dispositions": WAVE8_FRANCE_BAVARIA_ROW_DISPOSITIONS,
        "sources": WAVE8_FRANCE_BAVARIA_SOURCES,
        "terminal_exclusions": WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS,
    }


def wave8_france_bavaria_audit_signature() -> str:
    """Return the digest of every signed semantic decision in this lane."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_FRANCE_BAVARIA_FINAL_AUDIT_SIGNATURE = (
    "b798179295c3dc57a3a0715f450ea9c4c0e07d2a86626e49a0ae6578893598c2"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _sorted_newline_sha256(values: Iterable[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(map(str, values))))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_FRANCE_BAVARIA_CONTRACTS),
        len(WAVE8_FRANCE_BAVARIA_HOLDS),
        len(WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS),
    ) != (3, 1, 0):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_FRANCE_BAVARIA_ENTITIES), len(WAVE8_FRANCE_BAVARIA_SOURCES)) != (
        1,
        11,
    ):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_FRANCE_BAVARIA_EXCLUSIONS is not (
        WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS
    ):
        raise ValueError(f"{_LANE_NAME} exclusion alias drifted")
    if WAVE8_FRANCE_BAVARIA_RESERVED_IDS != (
        WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    if set(WAVE8_FRANCE_BAVARIA_ROW_DISPOSITIONS) != (
        WAVE8_FRANCE_BAVARIA_RESERVED_IDS
    ) or set(WAVE8_FRANCE_BAVARIA_ROW_DISPOSITIONS.values()) != {"hold", "promote"}:
        raise ValueError(f"{_LANE_NAME} row dispositions changed")
    if (
        WAVE8_FRANCE_BAVARIA_FINAL_AUDIT_SIGNATURE != "__PENDING__"
        and wave8_france_bavaria_audit_signature()
        != WAVE8_FRANCE_BAVARIA_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")
    if _sorted_newline_sha256(WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS) != str(
        WAVE8_FRANCE_BAVARIA_FUNNEL_AUDIT["event_candidate_id_sha256"]
    ):
        raise ValueError(f"{_LANE_NAME} exact-cohort digest changed")

    source_by_id = {
        str(source["id"]): source for source in WAVE8_FRANCE_BAVARIA_SOURCES
    }
    if len(source_by_id) != len(WAVE8_FRANCE_BAVARIA_SOURCES):
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len(
        {str(source["source_family_id"]) for source in WAVE8_FRANCE_BAVARIA_SOURCES}
    ) != len(WAVE8_FRANCE_BAVARIA_SOURCES):
        raise ValueError(f"{_LANE_NAME} source families are not unique")
    for source in WAVE8_FRANCE_BAVARIA_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles changed")

    new_entity_ids = {str(entity["id"]) for entity in WAVE8_FRANCE_BAVARIA_ENTITIES}
    if new_entity_ids != {_GEFREES_FREE_CORPS_ID}:
        raise ValueError(f"{_LANE_NAME} new identity inventory changed")
    entity = WAVE8_FRANCE_BAVARIA_ENTITIES[0]
    if (
        int(entity["start_year"]),
        int(entity["end_year"]),
        entity["aliases"],
        entity["predecessors"],
    ) != (1809, 1809, [], []):
        raise ValueError(f"{_LANE_NAME} event-bounded identity changed")
    note = str(entity["continuity_note"]).casefold()
    for phrase in (
        "no rating is inherited",
        "brunswick",
        "hesse-kassel",
        "dynasty",
        "another coalition",
        "another campaign",
    ):
        if phrase not in note:
            raise ValueError(f"{_LANE_NAME} continuity firewall changed")
    if not _is_sorted_unique(entity["source_ids"]) or not set(entity["source_ids"]) <= set(
        source_by_id
    ):
        raise ValueError(f"{_LANE_NAME} entity sources changed")

    if set(WAVE8_FRANCE_BAVARIA_REGIME_ENTITY_DISPOSITIONS) != (
        WAVE8_FRANCE_BAVARIA_REQUIRED_EXISTING_ENTITY_IDS
    ) or set(WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT) != (
        WAVE8_FRANCE_BAVARIA_REQUIRED_EXISTING_ENTITY_IDS
    ):
        raise ValueError(f"{_LANE_NAME} regime dependency inventory changed")
    for entity_id, disposition in WAVE8_FRANCE_BAVARIA_REGIME_ENTITY_DISPOSITIONS.items():
        overlap = WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT[entity_id]
        if overlap["candidate_id_overlap"]:
            raise ValueError(f"{_LANE_NAME} reowns an existing lane candidate")
        if overlap["identity_window"] != [
            int(disposition["start_year"]),
            int(disposition["end_year"]),
        ]:
            raise ValueError(f"{_LANE_NAME} identity-overlap window changed")

    allowed_entities = new_entity_ids | set(
        WAVE8_FRANCE_BAVARIA_REQUIRED_EXISTING_ENTITY_IDS
    )
    used_entities: set[str] = set()
    used_sources: set[str] = set(map(str, entity["source_ids"]))
    expected_sides = {
        "hced-Gefrees1809-1": (
            {_AUSTRIAN_EMPIRE_ID, _GEFREES_FREE_CORPS_ID},
            {_FIRST_FRENCH_EMPIRE_ID, _KINGDOM_BAVARIA_ID},
            1,
        ),
        "hced-Neumarkt-St-Viet1809-1": (
            {_AUSTRIAN_EMPIRE_ID},
            {_FIRST_FRENCH_EMPIRE_ID, _KINGDOM_BAVARIA_ID},
            1,
        ),
        "hced-Polotsk (2nd)1812-1": (
            {_RUSSIAN_EMPIRE_ID},
            {_FIRST_FRENCH_EMPIRE_ID, _KINGDOM_BAVARIA_ID},
            1,
        ),
    }
    for candidate_id, contract in WAVE8_FRANCE_BAVARIA_CONTRACTS.items():
        if contract["raw_row_sha256"] != WAVE8_FRANCE_BAVARIA_ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} promotion fingerprint changed")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event changed")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        expected_1, expected_2, winner_side = expected_sides[candidate_id]
        if (side_1, side_2, int(contract["winner_side"])) != (
            expected_1,
            expected_2,
            winner_side,
        ):
            raise ValueError(f"{_LANE_NAME} actor composition changed")
        if not side_1 or not side_2 or side_1 & side_2 or not (side_1 | side_2) <= allowed_entities:
            raise ValueError(f"{_LANE_NAME} opposing sides are invalid")
        used_entities.update(side_1 | side_2)
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"]
            != "audited_compound_split_into_time_bounded_regimes"
        ):
            raise ValueError(f"{_LANE_NAME} promotion semantics changed")
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
            raise ValueError(f"{_LANE_NAME} promotion evidence changed")
        expected_families = sorted(
            {
                str(source_by_id[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} independent outcomes changed")
        if any(
            "outcome" not in source_by_id[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} outcome source role changed")
        used_sources.update(evidence)
    if used_entities != allowed_entities:
        raise ValueError(f"{_LANE_NAME} actor identities are not exactly consumed")

    hold = WAVE8_FRANCE_BAVARIA_HOLDS["hced-Polotsk (1st)1812-1"]
    if (
        hold["raw_row_sha256"]
        != WAVE8_FRANCE_BAVARIA_ROW_HASHES["hced-Polotsk (1st)1812-1"]
        or hold["disposition"] != "hold"
        or hold["result_type"] != "unknown"
        or hold["unknown_is_never_draw"] is not True
        or hold["hold_category"] != "historiographically_contested_outcome"
    ):
        raise ValueError(f"{_LANE_NAME} First Polotsk hold changed")
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
    if not all(phrase in reason for phrase in ("conflict", "not promoted", "unknown", "draw")):
        raise ValueError(f"{_LANE_NAME} no-draw hold rationale changed")
    hold_evidence = list(map(str, hold["evidence_refs"]))
    if not _is_sorted_unique(hold_evidence) or not set(hold_evidence) <= set(source_by_id):
        raise ValueError(f"{_LANE_NAME} hold evidence changed")
    positions = hold["conflicting_outcome_positions"]
    if set(positions) != {
        "french_tactical_victory",
        "failed_french_attack_or_russian_success",
    } or not all(positions.values()):
        raise ValueError(f"{_LANE_NAME} conflicting source positions changed")
    if set(positions["french_tactical_victory"]) & set(
        positions["failed_french_attack_or_russian_success"]
    ):
        raise ValueError(f"{_LANE_NAME} hold source positions overlap")
    used_sources.update(hold_evidence)

    if WAVE8_FRANCE_BAVARIA_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} acquired an outcome override")
    if set(WAVE8_FRANCE_BAVARIA_LOCATION_REVIEWS) != (
        WAVE8_FRANCE_BAVARIA_CONTRACT_IDS
    ) or WAVE8_FRANCE_BAVARIA_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_FRANCE_BAVARIA_CONTRACT_IDS
    ) or WAVE8_FRANCE_BAVARIA_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} location quarantine changed")
    for review in WAVE8_FRANCE_BAVARIA_LOCATION_REVIEWS.values():
        evidence = list(map(str, review["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(source_by_id):
            raise ValueError(f"{_LANE_NAME} location evidence changed")
        used_sources.update(evidence)

    if set(WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT) != (
        WAVE8_FRANCE_BAVARIA_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate negative audit is incomplete")
    for item in WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, item["aliases"]))
        if not _is_sorted_unique(aliases) or aliases != list(map(normalize_label, aliases)):
            raise ValueError(f"{_LANE_NAME} duplicate aliases changed")
        low, high = map(int, item["years"])
        if low > high:
            raise ValueError(f"{_LANE_NAME} duplicate interval changed")
    if (
        WAVE8_FRANCE_BAVARIA_IWBD_DUPLICATE_DISPOSITIONS
        or WAVE8_FRANCE_BAVARIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        or WAVE8_FRANCE_BAVARIA_CROSS_LANE_DISPOSITIONS
    ):
        raise ValueError(f"{_LANE_NAME} acquired an overlapping owner")
    if set(WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS) != {
        "hced-Jacobovo1812-1",
        "hced-Neumarkt1796-1",
        "hced-Polotsk1563-1",
        "hced-Polotsk1579-1",
    }:
        raise ValueError(f"{_LANE_NAME} related-HCED audit changed")
    if set(WAVE8_FRANCE_BAVARIA_INTEGRATION_DISPOSITIONS) != {
        f"related_hced:{candidate_id}"
        for candidate_id in WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS
    }:
        raise ValueError(f"{_LANE_NAME} integration audit changed")

    used_sources.update(
        source_id
        for fixture in WAVE8_FRANCE_BAVARIA_ENTITIES
        for source_id in map(str, fixture["source_ids"])
    )
    if used_sources != set(source_by_id):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")


def validate_wave8_france_bavaria_existing_entities(
    release_entities: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    """Fail closed if a reused polity's time-bounded identity changes."""

    _validate_static()
    for entity_id, expected in WAVE8_FRANCE_BAVARIA_REGIME_ENTITY_DISPOSITIONS.items():
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
    return {
        "new_event_bounded_entities": len(WAVE8_FRANCE_BAVARIA_ENTITIES),
        "reused_time_bounded_entities": len(
            WAVE8_FRANCE_BAVARIA_REQUIRED_EXISTING_ENTITY_IDS
        ),
    }


def _is_exact_label(value: Any) -> bool:
    return normalize_label(value) == _EXACT_LABEL


def validate_wave8_france_bavaria_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Pin all and only the four exact-order ``France, Bavaria`` rows."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_FRANCE_BAVARIA_CONTRACTS,
        WAVE8_FRANCE_BAVARIA_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if _is_exact_label(row.get("side_1_raw"))
        or _is_exact_label(row.get("side_2_raw"))
    }
    if exact_ids != WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed: {sorted(exact_ids)}")
    by_id = {
        str(row.get("candidate_id")): row
        for row in hced_rows
        if str(row.get("candidate_id")) in WAVE8_FRANCE_BAVARIA_RESERVED_IDS
    }
    for candidate_id, row in by_id.items():
        exact_sides = sum(
            _is_exact_label(row.get(field)) for field in ("side_1_raw", "side_2_raw")
        )
        if exact_sides != 1:
            raise ValueError(f"{_LANE_NAME} exact-side ownership changed: {candidate_id}")
    reverse_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) == _REVERSE_LABEL
        or normalize_label(row.get("side_2_raw")) == _REVERSE_LABEL
    }
    if reverse_ids & WAVE8_FRANCE_BAVARIA_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} swept reverse-order labels into the lane")
    return {
        "holds": len(WAVE8_FRANCE_BAVARIA_HOLDS),
        "promotion_contracts": result["promotion_contracts"],
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_france_bavaria_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    """Pin the four-row sole-blocker funnel independently of adjudication."""

    _validate_static()
    labels = funnel.get("labels")
    if not isinstance(labels, list):
        raise ValueError(f"{_LANE_NAME} funnel labels are unavailable")
    matching = [item for item in labels if item.get("label") == _EXACT_LABEL]
    if len(matching) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label row")
    label = matching[0]
    for field in (
        "event_candidate_id_sha256",
        "events_touched",
        "unresolved_side_attempts",
        "sole_blocker_events",
        "failure_cases",
        "centuries",
        "components_touched",
        "components_bridged",
        "rated_counterpart_entities",
    ):
        if label.get(field) != WAVE8_FRANCE_BAVARIA_FUNNEL_AUDIT[field]:
            raise ValueError(f"{_LANE_NAME} funnel {field} changed")

    row_label_data = funnel.get("row_label_data")
    if not isinstance(row_label_data, list):
        raise ValueError(f"{_LANE_NAME} row-label data are unavailable")
    audited: dict[str, Mapping[str, Any]] = {}
    for row in row_label_data:
        failures = row.get("label_failures")
        if isinstance(failures, list) and any(
            failure.get("label") == _EXACT_LABEL for failure in failures
        ):
            audited[str(row.get("candidate_id"))] = row
    if set(audited) != WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} funnel row inventory changed")
    counterpart_map = WAVE8_FRANCE_BAVARIA_FUNNEL_AUDIT[
        "resolved_counterpart_entity_ids"
    ]
    for candidate_id, row in audited.items():
        if (
            row.get("sole_blocker_label") != _EXACT_LABEL
            or row.get("blocker_labels") != [_EXACT_LABEL]
            or row.get("other_blockers") != []
            or row.get("resolved_counterpart_entity_ids")
            != counterpart_map[candidate_id]
        ):
            raise ValueError(f"{_LANE_NAME} sole-blocker row changed: {candidate_id}")
    greedy = funnel.get("greedy_batch")
    ranking = greedy.get("ranking") if isinstance(greedy, Mapping) else None
    if not isinstance(ranking, list):
        raise ValueError(f"{_LANE_NAME} greedy ranking is unavailable")
    ranked = [item for item in ranking if item.get("label") == _EXACT_LABEL]
    if len(ranked) != 1 or any(
        ranked[0].get(field) != expected
        for field, expected in (
            ("events_touched", 4),
            ("marginal_events", 4),
            (
                "newly_unblocked_candidate_id_sha256",
                WAVE8_FRANCE_BAVARIA_FUNNEL_AUDIT[
                    "event_candidate_id_sha256"
                ],
            ),
        )
    ):
        raise ValueError(f"{_LANE_NAME} greedy audit changed")
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
    for item in WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT.values()
    for year in range(int(item["years"][0]), int(item["years"][1]) + 1)
    for alias in item["aliases"]
}


def _probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return any((year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row))


def validate_wave8_france_bavaria_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin related rows and fail closed on future HCED, IWBD, or release twins."""

    validate_wave8_france_bavaria_queue_contracts(hced_rows)
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, disposition in (
        WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS.items()
    ):
        rows = by_id.get(candidate_id, [])
        if len(rows) != 1 or canonical_hced_row_sha256(rows[0]) != disposition[
            "raw_row_sha256"
        ]:
            raise ValueError(f"{_LANE_NAME} related HCED row changed: {candidate_id}")

    related_ids = set(WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_FRANCE_BAVARIA_RESERVED_IDS
        and str(row.get("candidate_id")) not in related_ids
        and _probable_twin(row)
    )
    if hced_twins:
        raise ValueError(f"{_LANE_NAME} unreviewed cross-lane HCED twin(s): {hced_twins}")
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _probable_twin(row)
    )
    if iwbd_twins:
        raise ValueError(f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_twins}")

    existing = list(existing_events)
    ownership_collisions = sorted(
        {
            str(event.get("hced_candidate_id"))
            for event in existing
            if event.get("hced_candidate_id") in WAVE8_FRANCE_BAVARIA_RESERVED_IDS
        }
    )
    if ownership_collisions:
        raise ValueError(
            f"{_LANE_NAME} candidate ownership collision in release: "
            f"{ownership_collisions}"
        )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if _probable_twin(event)
    )
    if release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed existing-release twin(s): {release_twins}"
        )
    return {
        "cross_lane_hced_dispositions": 0,
        "existing_release_duplicate_dispositions": 0,
        "integration_dispositions": len(
            WAVE8_FRANCE_BAVARIA_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_probable_twins": 0,
        "related_hced_dispositions": len(
            WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS
        ),
    }


def install_wave8_france_bavaria_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_FRANCE_BAVARIA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_france_bavaria_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_FRANCE_BAVARIA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_FRANCE_BAVARIA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_FRANCE_BAVARIA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_france_bavaria_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Emit only the three independently attested tactical wins."""

    validate_wave8_france_bavaria_queue_contracts(hced_rows)
    validate_wave8_france_bavaria_existing_entities(release_entities)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_FRANCE_BAVARIA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_france_bavaria_cohort_counts() -> dict[str, int]:
    """Return cohort counts across promotions and explicit holds."""

    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_FRANCE_BAVARIA_CONTRACTS.values(),
                    *WAVE8_FRANCE_BAVARIA_NONPROMOTIONS.values(),
                )
            ).items()
        )
    )


def wave8_france_bavaria_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_FRANCE_BAVARIA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_hced_dispositions": len(
            WAVE8_FRANCE_BAVARIA_CROSS_LANE_DISPOSITIONS
        ),
        "existing_lane_overlap_audits": len(
            WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT
        ),
        "existing_release_duplicate_dispositions": len(
            WAVE8_FRANCE_BAVARIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_FRANCE_BAVARIA_HOLDS),
        "integration_dispositions": len(
            WAVE8_FRANCE_BAVARIA_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_FRANCE_BAVARIA_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_candidates": len(
            WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "new_entities": len(WAVE8_FRANCE_BAVARIA_ENTITIES),
        "new_sources": len(WAVE8_FRANCE_BAVARIA_SOURCES),
        "newly_rated_events": len(WAVE8_FRANCE_BAVARIA_CONTRACTS),
        "outcome_overrides": len(WAVE8_FRANCE_BAVARIA_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_FRANCE_BAVARIA_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_FRANCE_BAVARIA_CONTRACTS),
        "related_hced_dispositions": len(
            WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS
        ),
        "required_existing_entities": len(
            WAVE8_FRANCE_BAVARIA_REQUIRED_EXISTING_ENTITY_IDS
        ),
        "reviewed_hced_rows": len(WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS),
        "sole_blocker_rows": int(
            WAVE8_FRANCE_BAVARIA_FUNNEL_AUDIT["sole_blocker_events"]
        ),
        "terminal_exclusions": len(WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS),
    }


def wave8_france_bavaria_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    _validate_static()
    return {
        "country": WAVE8_FRANCE_BAVARIA_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_FRANCE_BAVARIA_POINT_QUARANTINE_ADDITIONS,
    }


def wave8_france_bavaria_row_dispositions() -> dict[str, str]:
    _validate_static()
    return dict(WAVE8_FRANCE_BAVARIA_ROW_DISPOSITIONS)


def wave8_france_bavaria_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "audit": "candidate_keyed_exact_label_with_time_bounded_actor_split",
        "counts": wave8_france_bavaria_counts(),
        "cohort_counts": wave8_france_bavaria_cohort_counts(),
        "exact_label": _EXACT_LABEL,
        "module_owner": _MODULE_OWNER,
        "row_dispositions": wave8_france_bavaria_row_dispositions(),
        "signature": wave8_france_bavaria_audit_signature(),
    }


_validate_static()
