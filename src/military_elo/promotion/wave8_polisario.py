"""Fail-closed exact HCED audit for Polisario/ELPS labels.

The HCED queue contains three spellings for the Polisario military side and
six affected rows.  This lane does not turn any spelling into a resolver alias.
It creates an alias-free, time-bounded ELPS identity and an equally narrow
Mauritanian state identity, then rates only three independently documented
tactical outcomes.  The remaining three rows stay explicit unknown holds;
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
    expected_exact_hced_win_participants,
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)


__all__ = (
    "WAVE8_POLISARIO_CONTRACT_IDS",
    "WAVE8_POLISARIO_CONTRACTS",
    "WAVE8_POLISARIO_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_POLISARIO_DISCOVERY_CONTEXT",
    "WAVE8_POLISARIO_ENTITIES",
    "WAVE8_POLISARIO_FINAL_AUDIT_SIGNATURE",
    "WAVE8_POLISARIO_FUNNEL_AUDIT",
    "WAVE8_POLISARIO_HOLD_IDS",
    "WAVE8_POLISARIO_HOLDS",
    "WAVE8_POLISARIO_LOCATION_QUARANTINE_REASONS",
    "WAVE8_POLISARIO_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_POLISARIO_RESERVED_IDS",
    "WAVE8_POLISARIO_ROW_HASHES",
    "WAVE8_POLISARIO_SOURCES",
    "install_wave8_polisario_entities",
    "install_wave8_polisario_sources",
    "promote_wave8_polisario_contracts",
    "validate_wave8_polisario_emissions",
    "validate_wave8_polisario_funnel",
    "validate_wave8_polisario_integration_dispositions",
    "validate_wave8_polisario_queue_contracts",
    "wave8_polisario_audit_signature",
    "wave8_polisario_cohort_counts",
    "wave8_polisario_counts",
    "wave8_polisario_metadata",
)


_LANE_NAME = "Wave 8 exact Polisario/ELPS actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_polisario"
_EVENT_ID_PREFIX = "hced_wave8_polisario_"
_COHORT = "western_sahara_war_polisario_exact_1976_1980"
_EXACT_LABELS = frozenset({"polisaro", "polisario", "polisario rebels"})

_ELPS = "sahrawi_popular_liberation_army_1973_1991"
_MAURITANIA = "islamic_republic_mauritania_1960_1978"
_MOROCCO = "clio_q1028_1670_ae522447"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    evidence_roles: Iterable[str],
) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-21",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_POLISARIO_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_polisario_air_university_western_sahara",
        "War and Insurgency in the Western Sahara",
        "https://media.defense.gov/2023/May/04/2003215968/-1/-1/0/2224.PDF",
        "Strategic Studies Institute, U.S. Army War College",
        "professional_military_monograph",
        "mundy_zunes_western_sahara_monograph",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_polisario_cia_nouakchott_1976",
        "Weekly Summary: Mauritania (18 June 1976)",
        (
            "https://www.cia.gov/readingroom/docs/"
            "CIA-RDP79-00927A011300250001-1.pdf"
        ),
        "Central Intelligence Agency Reading Room",
        "declassified_contemporary_intelligence_assessment",
        "cia_weekly_summary_1976_06_18",
        ["outcome"],
    ),
    _source(
        "wave8_polisario_elpais_tan_tan_1979",
        "El Polisario afirma que ocupó durante varias horas una localidad marroquí",
        (
            "https://elpais.com/diario/1979/01/30/internacional/"
            "286498811_850215.html"
        ),
        "El País",
        "contemporary_newspaper_report",
        "elpais_tan_tan_1979_01_30",
        ["outcome", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_polisario_frus_oum_drouss_1977",
        "The Sahara Two Years After the Green March",
        "https://history.state.gov/historicaldocuments/frus1977-80v17p3/d218",
        "Office of the Historian, U.S. Department of State",
        "official_diplomatic_record",
        "frus_1977_1980_north_africa_document_218",
        ["outcome"],
    ),
    _source(
        "wave8_polisario_lemonde_oum_drouss_1977",
        (
            "Le conflit du Sahara occidental: deux techniciens français et "
            "vingt-quatre Mauritaniens ont disparu près de Zouérate"
        ),
        (
            "https://www.lemonde.fr/archives/article/1977/10/27/"
            "le-conflit-du-sahara-occidental-deux-techniciens-francais-et-"
            "vingt-quatre-mauritaniens-ont-disparu-pres-de-zouerate_"
            "3085579_1819218.html"
        ),
        "Le Monde",
        "contemporary_newspaper_report",
        "lemonde_oum_drouss_1977_10_27",
        ["outcome", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_polisario_loc_mauritania_country_study",
        "Mauritania: A Country Study",
        (
            "https://tile.loc.gov/storage-services/master/frd/frdcstdy/ma/"
            "mauritaniacountr00hand_0/mauritaniacountr00hand_0.pdf"
        ),
        "Federal Research Division, Library of Congress",
        "government_country_study",
        "loc_mauritania_country_study_1990",
        ["identity_boundary_or_context_reference", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_polisario_minurso_ceasefire",
        "MINURSO Fact Sheet and settlement-plan background",
        "https://peacekeeping.un.org/en/factsheet/minurso",
        "United Nations Peacekeeping",
        "official_international_organization_record",
        "un_minurso_fact_sheet",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_polisario_state_mauritania_recognition",
        "A Guide to the United States' History of Recognition: Mauritania",
        "https://history.state.gov/countries/mauritania",
        "Office of the Historian, U.S. Department of State",
        "official_diplomatic_history",
        "state_department_mauritania_recognition",
        ["identity_boundary_or_context_reference"],
    ),
    _source(
        "wave8_polisario_un_nouakchott_1976",
        (
            "Letter dated 14 June 1976 from the Permanent Representative of "
            "Mauritania to the United Nations"
        ),
        (
            "https://digitallibrary.un.org/record/224981/files/"
            "A_31_106--S_12095-EN.pdf"
        ),
        "United Nations Digital Library",
        "contemporary_official_diplomatic_record",
        "un_a31_106_s12095",
        ["outcome", "outcome_consistency_crosscheck"],
    ),
    _source(
        "wave8_polisario_un_western_sahara_1979",
        "Report of the Special Committee on the Situation, 1979",
        (
            "https://digitallibrary.un.org/record/15187/files/"
            "A_34_23_Rev.1%5EVol.II%5E--A_34_23_Rev.1--"
            "A_34_23_Rev.1Vol.II-EN.pdf"
        ),
        "United Nations Digital Library",
        "official_international_organization_report",
        "un_a34_23_rev1_volume2",
        [
            "identity_boundary_or_context_reference",
            "outcome",
            "outcome_consistency_crosscheck",
        ],
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_POLISARIO_SOURCES}


# Neither identity opens a generic source-label route.  The ELPS record covers
# the armed phase from the movement's 1973 formation through the UN-supervised
# 1991 ceasefire.  Mauritania is deliberately split at the July 1978 coup so
# no Elo crosses from Ould Daddah's war government into the military regime.
WAVE8_POLISARIO_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _ELPS,
        "name": "Sahrawi Popular Liberation Army (1973-1991)",
        "kind": "national_liberation_army",
        "start_year": 1973,
        "end_year": 1991,
        "region": "Western Sahara, southern Morocco, and Mauritania",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Time-bounded armed wing of the Polisario Front during the original "
            "armed phase, from the movement's 1973 foundation through the "
            "UN-supervised ceasefire effective 6 September 1991. Only exact, "
            "fingerprinted military rows may use this identity: the political "
            "front, the SADR government, later post-ceasefire forces, and bare "
            "Polisario/Polisaro labels inherit no rating and gain no alias."
        ),
        "source_ids": [
            "wave8_polisario_air_university_western_sahara",
            "wave8_polisario_minurso_ceasefire",
        ],
    },
    {
        "id": _MAURITANIA,
        "name": "Islamic Republic of Mauritania (Ould Daddah era)",
        "kind": "republic",
        "start_year": 1960,
        "end_year": 1978,
        "region": "Mauritania and the wartime Tiris al-Gharbiyya administration",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Independent Islamic Republic under Moktar Ould Daddah, bounded from "
            "independence on 28 November 1960 through the 10 July 1978 military "
            "coup. The two rated 1976-1977 actions fall wholly within this "
            "interval. The successor military governments, a generic Mauritania "
            "label, and later republics inherit no rating without separate review."
        ),
        "source_ids": [
            "wave8_polisario_loc_mauritania_country_study",
            "wave8_polisario_state_mauritania_recognition",
        ],
    },
)


WAVE8_POLISARIO_ROW_HASHES: dict[str, str] = {
    "hced-Nouakchott1976-1": (
        "7ccbe779e4264c744ea464506e72a56543a525434d3725d474b306ca0419b50c"
    ),
    "hced-Oum Droussa1977-1": (
        "08c92881fe52f6cfecc8e078b9da5f4c60f4f710d2a909bf5d9125bf71edd9d5"
    ),
    "hced-Smara1976-1": (
        "13c95eb5296ced5ced5b95159362276f85a857e259a2c7034430cb4f023b0f17"
    ),
    "hced-Tan-Tan1979-1": (
        "bdcad53b897455dbb2d9c599b9be5c15e547f401a7e7140b756d3a7aa618fc7a"
    ),
    "hced-Zag1980-1": (
        "4121b4b796474aec2d441d9d9c9bfaf3e1bfbd1e354308b0d99586314d2839bf"
    ),
    "hced-Zouerate1977-1": (
        "bdbd43f2cffd0c67246d80e8251f47729a56332203029b57ab9854d8f468bbd4"
    ),
}


WAVE8_POLISARIO_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "polisario": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "5c8ce1e2f47c4d044dde333e8063d08c35999ca114c85bc85eea73c10d1896e6"
        ),
        "events_touched": 2,
        "label": "polisario",
        "rated_counterpart_entities": 1,
        "sole_blocker_events": 2,
        "unresolved_side_attempts": 2,
        "zero_time_valid_candidates": 2,
    },
    "polisario rebels": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "d8afb9d97bfbfb755cb29ed4585c88110f36f8b71dc2925349b3e11612d3ad3e"
        ),
        "events_touched": 2,
        "label": "polisario rebels",
        "rated_counterpart_entities": 1,
        "sole_blocker_events": 2,
        "unresolved_side_attempts": 2,
        "zero_time_valid_candidates": 2,
    },
    "polisaro": {
        "candidate_ids": [],
        "event_candidate_id_sha256": (
            "0819ec6026615c7bc895d3529c5dc6253f5283dd70d127380d75cc99ede57258"
        ),
        "events_touched": 2,
        "label": "polisaro",
        "rated_counterpart_entities": 1,
        "sole_blocker_events": 2,
        "unresolved_side_attempts": 2,
        "zero_time_valid_candidates": 2,
    },
}


WAVE8_POLISARIO_DISCOVERY_CONTEXT: dict[str, Any] = {
    "ucdp_actor_candidate_id": "ucdp-actor-26.1-554--554",
    "ucdp_actor_id": "563",
    "ucdp_conflict_id": "331",
    "ucdp_dyad_id": "721",
    "disposition": "identity_and_conflict_context_only",
    "do_not_rate_automatically": True,
    "reason": (
        "UCDP actor/conflict rows identify parties and intensity, not tactical "
        "victors. They cannot emit an Elo event without an exact reviewed outcome."
    ),
}


def _canonical(
    name: str,
    year: int,
    date_precision: str,
    date_text: str,
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
    side_1: Iterable[str],
    side_2: Iterable[str],
    outcome_sources: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_sources)))
    return {
        "raw_row_sha256": WAVE8_POLISARIO_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "colonial_anti_colonial",
        "confidence": confidence,
        "evidence_refs": outcomes,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": "candidate_keyed_elps_and_time_bounded_state_identities",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_POLISARIO_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Nouakchott1976-1": _contract(
        "hced-Nouakchott1976-1",
        _canonical(
            "Nouakchott raid (June 1976)",
            1976,
            "day_range",
            "8-10 June 1976",
            "raid_on_the_capital_and_immediate_pursuit",
        ),
        [_MAURITANIA],
        [_ELPS],
        {
            "wave8_polisario_air_university_western_sahara",
            "wave8_polisario_cia_nouakchott_1976",
            "wave8_polisario_un_nouakchott_1976",
        },
        (
            "The declassified contemporary assessment records Mauritanian "
            "security forces quickly repulsing the capital attack and killing or "
            "capturing most raiders during the pursuit, including ELPS leader El-"
            "Ouali. The contract rates only that local defensive result, not the "
            "war's later strategic pressure on Mauritania."
        ),
        confidence=0.94,
    ),
    "hced-Oum Droussa1977-1": _contract(
        "hced-Oum Droussa1977-1",
        _canonical(
            "Battle of Sebkhat Oum Drouss",
            1977,
            "day_range",
            "13-14 October 1977",
            "ambush_of_joint_moroccan_mauritanian_column",
        ),
        [_ELPS],
        [_MOROCCO, _MAURITANIA],
        {
            "wave8_polisario_frus_oum_drouss_1977",
            "wave8_polisario_lemonde_oum_drouss_1977",
        },
        (
            "The U.S. diplomatic record calls the 13-14 October action a "
            "successful Polisario attack. Contemporary reporting identifies the "
            "target as a joint Moroccan-Mauritanian column and records both "
            "belligerents acknowledging severe coalition losses. The second raw "
            "side is therefore corrected from Morocco alone to the documented "
            "coalition without opening a reusable composite label."
        ),
        confidence=0.96,
    ),
    "hced-Tan-Tan1979-1": _contract(
        "hced-Tan-Tan1979-1",
        _canonical(
            "Battle of Tan-Tan (1979)",
            1979,
            "day",
            "28 January 1979",
            "raid_and_temporary_occupation_of_tan_tan",
        ),
        [_ELPS],
        [_MOROCCO],
        {
            "wave8_polisario_air_university_western_sahara",
            "wave8_polisario_elpais_tan_tan_1979",
            "wave8_polisario_un_western_sahara_1979",
        },
        (
            "The reviewed histories and contemporary reporting document ELPS "
            "penetration and temporary occupation of Tan-Tan, prisoner releases, "
            "captives, and destruction of military infrastructure. This is a "
            "bounded tactical raid victory, not a claim of lasting territorial or "
            "strategic control."
        ),
        confidence=0.94,
    ),
}


def _hold(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    category: str,
    reviewed_outcome: str,
    reason: str,
    evidence_refs: Iterable[str],
) -> dict[str, Any]:
    return {
        "raw_row_sha256": WAVE8_POLISARIO_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": _COHORT,
        "disposition": "hold",
        "hold_category": category,
        "reviewed_outcome": reviewed_outcome,
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_actor_description": [
            "Sahrawi Popular Liberation Army (ELPS)",
            "the exact time-bounded Moroccan or Mauritanian opponent, if identified",
        ],
        "reviewed_granularity": str(canonical_event["granularity"]),
        "hold_reason": reason,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "provisional_hced_hold",
        },
    }


WAVE8_POLISARIO_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Smara1976-1": _hold(
        "hced-Smara1976-1",
        _canonical(
            "Smara operations (1976)",
            1976,
            "year",
            "1976; exact episode unresolved",
            "ambiguous_annual_event_envelope",
        ),
        "source_draw_is_incomplete_and_no_discrete_1976_result_is_attested",
        "unknown_not_draw",
        (
            "HCED marks the winner/loser record incomplete and supplies no loser. "
            "The reviewed military history documents a major Smara action in "
            "1979, not a defensible discrete 1976 result matching this row. The "
            "literal source 'Draw' is therefore unknown and remains unrated; "
            "unknown is never a draw."
        ),
        {
            "wave8_polisario_air_university_western_sahara",
            "wave8_polisario_un_western_sahara_1979",
        },
    ),
    "hced-Zag1980-1": _hold(
        "hced-Zag1980-1",
        _canonical(
            "Zag operations (1980)",
            1980,
            "year",
            "1980; exact episode unresolved",
            "ambiguous_annual_event_envelope",
        ),
        "no_independent_match_for_hced_winner_claim",
        "unknown_not_draw",
        (
            "The audited sources establish repeated Polisario operations around "
            "Zag and southern Morocco but do not identify a discrete 1980 action "
            "whose participants and final tactical result match HCED's one-line "
            "Moroccan-victory claim. It remains unknown and is never treated as a "
            "draw or a win."
        ),
        {
            "wave8_polisario_air_university_western_sahara",
            "wave8_polisario_un_western_sahara_1979",
        },
    ),
    "hced-Zouerate1977-1": _hold(
        "hced-Zouerate1977-1",
        _canonical(
            "Zouerate operations (1977)",
            1977,
            "year",
            "1977; multiple distinct attacks",
            "multi_episode_annual_envelope",
        ),
        "multiple_1977_zouerate_actions_cannot_be_uniquely_aligned",
        "unknown_not_draw",
        (
            "The year contains distinct attacks on the mining city, railway, and "
            "maintenance parties in May and October, while HCED's participant "
            "tokens mix Morocco, Spanish context, the city, and the war. The row "
            "cannot be uniquely aligned to one tactical episode without inventing "
            "a result, so it remains unknown rather than a draw."
        ),
        {
            "wave8_polisario_air_university_western_sahara",
            "wave8_polisario_frus_oum_drouss_1977",
            "wave8_polisario_loc_mauritania_country_study",
        },
    ),
}


WAVE8_POLISARIO_CONTRACT_IDS = frozenset(WAVE8_POLISARIO_CONTRACTS)
WAVE8_POLISARIO_HOLD_IDS = frozenset(WAVE8_POLISARIO_HOLDS)
WAVE8_POLISARIO_RESERVED_IDS = frozenset(WAVE8_POLISARIO_ROW_HASHES)
WAVE8_POLISARIO_POINT_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Oum Droussa1977-1"}
)
WAVE8_POLISARIO_COUNTRY_QUARANTINE_ADDITIONS = frozenset(
    {"hced-Oum Droussa1977-1"}
)
WAVE8_POLISARIO_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Oum Droussa1977-1": {
        "actions": ["withhold_country", "withhold_point"],
        "evidence_refs": [
            "wave8_polisario_frus_oum_drouss_1977",
            "wave8_polisario_lemonde_oum_drouss_1977",
        ],
        "raw_country": "Mauritannia",
        "raw_point": [-11.9790041, 21.8864169],
        "reason": (
            "HCED's country string is misspelled and its point lies well south of "
            "the independently described Sebkhat Oum Drouss battlefield near Bir "
            "Moghrein. Withhold both rating-neutral assertions instead of silently "
            "normalizing or relocating them."
        ),
    }
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_POLISARIO_CONTRACTS,
        "discovery_context": WAVE8_POLISARIO_DISCOVERY_CONTEXT,
        "entities": WAVE8_POLISARIO_ENTITIES,
        "funnel": WAVE8_POLISARIO_FUNNEL_AUDIT,
        "holds": WAVE8_POLISARIO_HOLDS,
        "location_reasons": WAVE8_POLISARIO_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_POLISARIO_ROW_HASHES,
        "sources": WAVE8_POLISARIO_SOURCES,
    }


def wave8_polisario_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


# Filled after the static payload is assembled; unlike the runtime signature,
# this literal is a review seal and therefore must never be computed dynamically.
WAVE8_POLISARIO_FINAL_AUDIT_SIGNATURE = (
    "6c082497b0b7b60de2af0fd882767977abae57b9b78e715b2105b2a56952526e"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static(*, check_signature: bool = True) -> None:
    source_ids = set(_SOURCE_BY_ID)
    if len(source_ids) != len(WAVE8_POLISARIO_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")

    entities = {str(entity["id"]): entity for entity in WAVE8_POLISARIO_ENTITIES}
    if set(entities) != {_ELPS, _MAURITANIA}:
        raise ValueError(f"{_LANE_NAME} identity inventory drift")
    expected_windows = {_ELPS: (1973, 1991), _MAURITANIA: (1960, 1978)}
    for entity_id, entity in entities.items():
        if (
            (entity["start_year"], entity["end_year"])
            != expected_windows[entity_id]
            or entity["aliases"]
            or entity["predecessors"]
            or not _is_sorted_unique(entity["source_ids"])
            or not set(entity["source_ids"]) <= source_ids
            or "inherit no rating" not in str(entity["continuity_note"]).casefold()
        ):
            raise ValueError(f"{_LANE_NAME} identity firewall drift: {entity_id}")

    if WAVE8_POLISARIO_RESERVED_IDS != set(WAVE8_POLISARIO_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} reservation inventory drift")
    if WAVE8_POLISARIO_CONTRACT_IDS | WAVE8_POLISARIO_HOLD_IDS != (
        WAVE8_POLISARIO_RESERVED_IDS
    ):
        raise ValueError(f"{_LANE_NAME} disposition partition drift")
    if WAVE8_POLISARIO_CONTRACT_IDS & WAVE8_POLISARIO_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_POLISARIO_POINT_QUARANTINE_ADDITIONS != {
        "hced-Oum Droussa1977-1"
    } or WAVE8_POLISARIO_COUNTRY_QUARANTINE_ADDITIONS != {
        "hced-Oum Droussa1977-1"
    }:
        raise ValueError(f"{_LANE_NAME} location quarantine drift")
    if set(WAVE8_POLISARIO_LOCATION_QUARANTINE_REASONS) != {
        "hced-Oum Droussa1977-1"
    }:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    expected_contracts = {
        "hced-Nouakchott1976-1": ([_MAURITANIA], [_ELPS], 0.94),
        "hced-Oum Droussa1977-1": ([_ELPS], [_MOROCCO, _MAURITANIA], 0.96),
        "hced-Tan-Tan1979-1": ([_ELPS], [_MOROCCO], 0.94),
    }
    used_sources = {
        str(source_id)
        for entity in WAVE8_POLISARIO_ENTITIES
        for source_id in entity["source_ids"]
    }
    for candidate_id, (side_1, side_2, confidence) in expected_contracts.items():
        contract = WAVE8_POLISARIO_CONTRACTS[candidate_id]
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["confidence"] != confidence
            or contract["side_1_entity_ids"] != side_1
            or contract["side_2_entity_ids"] != side_2
            or contract["source_outcome_override"]
            or contract["outcome_reversal"]
        ):
            raise ValueError(f"{_LANE_NAME} outcome/actor drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or evidence != outcomes
            or not set(evidence) <= source_ids
        ):
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        if any("outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"] for source_id in outcomes):
            raise ValueError(f"{_LANE_NAME} non-outcome evidence: {candidate_id}")
        used_sources.update(evidence)

    for candidate_id, hold in WAVE8_POLISARIO_HOLDS.items():
        if (
            hold["disposition"] != "hold"
            or hold["result_type"] != "unknown"
            or hold["reviewed_outcome"] != "unknown_not_draw"
            or hold["unknown_is_never_draw"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} hold policy drift: {candidate_id}")
        evidence = list(map(str, hold["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} hold evidence drift: {candidate_id}")
        used_sources.update(evidence)

    for reason in WAVE8_POLISARIO_LOCATION_QUARANTINE_REASONS.values():
        evidence = list(map(str, reason["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} location evidence drift")
        used_sources.update(evidence)
    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")

    discovery = WAVE8_POLISARIO_DISCOVERY_CONTEXT
    if (
        discovery["do_not_rate_automatically"] is not True
        or discovery["disposition"] != "identity_and_conflict_context_only"
        or discovery["ucdp_actor_id"] != "563"
        or discovery["ucdp_conflict_id"] != "331"
        or discovery["ucdp_dyad_id"] != "721"
    ):
        raise ValueError(f"{_LANE_NAME} discovery firewall drift")
    if check_signature and (
        wave8_polisario_audit_signature()
        != WAVE8_POLISARIO_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_polisario_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_static()
    exact = [
        row
        for row in hced_rows
        if normalize_label(row.get("side_1_raw")) in _EXACT_LABELS
        or normalize_label(row.get("side_2_raw")) in _EXACT_LABELS
    ]
    exact_ids = {str(row.get("candidate_id")) for row in exact}
    if exact_ids != WAVE8_POLISARIO_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_POLISARIO_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            row.get("do_not_rate_automatically") is not True
            or row.get("duplicate_source_id") is not False
            or row.get("massacre_raw") != "No"
        ):
            raise ValueError(f"{_LANE_NAME} discovery/competitive guard drift: {candidate_id}")

    for candidate_id in WAVE8_POLISARIO_CONTRACT_IDS:
        row = by_id[candidate_id]
        if (
            row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
            or row.get("winner_loser_complete") is not True
        ):
            raise ValueError(f"{_LANE_NAME} promoted outcome alignment drift: {candidate_id}")

    expected_holds = {
        "hced-Smara1976-1": ("Draw", None, False),
        "hced-Zag1980-1": ("Morocco", "Polisario Rebels", True),
        "hced-Zouerate1977-1": ("Polisario Rebels", "Mauritania", True),
    }
    for candidate_id, expected in expected_holds.items():
        row = by_id[candidate_id]
        actual = (
            row.get("winner_raw"),
            row.get("loser_raw"),
            row.get("winner_loser_complete"),
        )
        if actual != expected:
            raise ValueError(f"{_LANE_NAME} unknown-hold guard drift: {candidate_id}")

    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_POLISARIO_CONTRACTS,
        WAVE8_POLISARIO_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {
        **counts,
        "exact_label_rows": len(exact),
        "exact_labels": len(_EXACT_LABELS),
    }


def validate_wave8_polisario_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    actual: dict[str, dict[str, Any]] = {}
    for row in funnel.get("labels", []):
        label = str(row.get("label"))
        if label not in _EXACT_LABELS:
            continue
        actual[label] = {
            "candidate_ids": list(map(str, row.get("candidate_ids", []))),
            "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
            "events_touched": int(row.get("events_touched", -1)),
            "label": label,
            "rated_counterpart_entities": int(row.get("rated_counterpart_entities", -1)),
            "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
            "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
            "zero_time_valid_candidates": int(
                row.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
            ),
        }
    if actual != WAVE8_POLISARIO_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed: {actual}")
    return {
        "events_touched": sum(row["events_touched"] for row in actual.values()),
        "labels": len(actual),
        "sole_blocker_events": sum(
            row["sole_blocker_events"] for row in actual.values()
        ),
        "zero_time_valid_candidates": sum(
            row["zero_time_valid_candidates"] for row in actual.values()
        ),
    }


def _row_year(row: Mapping[str, Any]) -> int | None:
    for key in ("year", "year_best", "year_low", "batyear"):
        try:
            if row.get(key) is not None:
                return int(row[key])
        except (TypeError, ValueError):
            pass
    return None


def _row_names(row: Mapping[str, Any]) -> set[str]:
    names = {
        normalize_label(row.get(key))
        for key in ("name", "battle_name", "batname", "event_name")
    }
    names.update(normalize_label(value) for value in row.get("aliases", []) or [])
    return {name for name in names if name}


_EVENT_ALIASES: dict[str, set[str]] = {
    "hced-Nouakchott1976-1": {
        "Nouakchott",
        "Nouakchott raid",
        "Nouakchott raid (June 1976)",
        "Raid on Nouakchott",
    },
    "hced-Oum Droussa1977-1": {
        "Battle of Sebkhat Oum Drouss",
        "Oum Drouss",
        "Oum Droussa",
        "Sebkhat Oum Drouss",
    },
    "hced-Smara1976-1": {"Battle of Smara", "Smara", "Smara operations"},
    "hced-Tan-Tan1979-1": {"Battle of Tan-Tan", "Battle of Tan-Tan (1979)", "Tan-Tan"},
    "hced-Zag1980-1": {"Battle of Zag", "Zag", "Zag operations"},
    "hced-Zouerate1977-1": {"Attack on Zouerate", "Zouerate", "Zouérate"},
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (
        int(
            (
                WAVE8_POLISARIO_CONTRACTS.get(candidate_id)
                or WAVE8_POLISARIO_HOLDS[candidate_id]
            )["canonical_event"]["year_low"]
        ),
        normalize_label(alias),
    )
    for candidate_id, aliases in _EVENT_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_polisario_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_polisario_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_POLISARIO_RESERVED_IDS
        and _is_probable_twin(row)
    )
    iwbd_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if _is_probable_twin(row)
    )
    release_twins = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing_events
        if event.get("hced_candidate_id") not in WAVE8_POLISARIO_CONTRACT_IDS
        and _is_probable_twin(event)
    )
    if hced_twins or iwbd_twins or release_twins:
        raise ValueError(
            f"{_LANE_NAME} unreviewed twin(s): hced={hced_twins}, "
            f"iwbd={iwbd_twins}, release={release_twins}"
        )
    return {
        "existing_release_probable_twins": 0,
        "hced_probable_twins": 0,
        "iwbd_probable_twins": 0,
    }


def install_wave8_polisario_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_POLISARIO_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_polisario_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_POLISARIO_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_POLISARIO_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_POLISARIO_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def validate_wave8_polisario_emissions(
    events: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    _validate_static()
    owned = list(events)
    by_id = {str(event.get("hced_candidate_id")): event for event in owned}
    if set(by_id) != WAVE8_POLISARIO_CONTRACT_IDS or len(owned) != len(by_id):
        raise ValueError(f"{_LANE_NAME} emitted inventory drift")
    expected_locations = {
        "hced-Nouakchott1976-1": ("Mauritania", [-15.9582372, 18.0735299]),
        "hced-Tan-Tan1979-1": ("Morocco", [-11.0987374, 28.4380408]),
    }
    participant_count = 0
    coalition_events = 0
    for candidate_id, contract in WAVE8_POLISARIO_CONTRACTS.items():
        event = by_id[candidate_id]
        canonical = contract["canonical_event"]
        expected_participants = expected_exact_hced_win_participants(
            contract["side_1_entity_ids"],
            contract["side_2_entity_ids"],
            confidence=float(contract["confidence"]),
            scale_level=2,
            lane_name=_LANE_NAME,
        )
        if (
            event.get("id") != f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
            or event.get("name") != canonical["name"]
            or (event.get("year"), event.get("end_year"))
            != (canonical["year_low"], canonical["year_high"])
            or event.get("date_precision") != canonical["date_precision"]
            or event.get("reviewed_granularity") != canonical["granularity"]
            or event.get("canonical_event_key") != canonical["canonical_key"]
            or event.get("identity_resolution") != "candidate_keyed_exact"
            or event.get("event_type") != "engagement"
            or event.get("war_type") != "colonial_anti_colonial"
            or event.get("participants") != expected_participants
            or event.get("source_ids")
            != ["hced_dataset", *contract["evidence_refs"]]
            or event.get("outcome_source_ids") != contract["outcome_source_ids"]
            or event.get("outcome_source_family_ids")
            != contract["outcome_source_family_ids"]
        ):
            raise ValueError(f"{_LANE_NAME} emitted contract drift: {candidate_id}")
        if any(
            "inconclusive" in str(participant.get("termination", ""))
            for participant in event["participants"]
        ):
            raise ValueError(f"{_LANE_NAME} emitted unknown/draw drift: {candidate_id}")
        participant_count += len(event["participants"])
        coalition_events += int(len(contract["side_2_entity_ids"]) > 1)

        if candidate_id == "hced-Oum Droussa1977-1":
            if any(
                key in event
                for key in ("geometry", "modern_location_country", "location_provenance")
            ):
                raise ValueError(f"{_LANE_NAME} quarantined location leaked")
        else:
            country, coordinates = expected_locations[candidate_id]
            if (
                event.get("modern_location_country") != country
                or event.get("geometry", {}).get("type") != "Point"
                or event.get("geometry", {}).get("coordinates") != coordinates
                or event.get("location_provenance", {}).get("assertion_status")
                != "unreviewed_source_assertion"
            ):
                raise ValueError(f"{_LANE_NAME} retained location drift: {candidate_id}")
    return {
        "coalition_events": coalition_events,
        "events": len(owned),
        "participants": participant_count,
        "retained_countries": len(expected_locations),
        "retained_points": len(expected_locations),
    }


def promote_wave8_polisario_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_polisario_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_POLISARIO_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine(events)
    validate_wave8_polisario_emissions(events)
    return events


def wave8_polisario_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_POLISARIO_CONTRACTS.values(),
                    *WAVE8_POLISARIO_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_polisario_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_POLISARIO_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "holds": len(WAVE8_POLISARIO_HOLDS),
        "new_entities": len(WAVE8_POLISARIO_ENTITIES),
        "new_sources": len(WAVE8_POLISARIO_SOURCES),
        "newly_rated_events": len(WAVE8_POLISARIO_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_POLISARIO_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_POLISARIO_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_POLISARIO_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_polisario_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_polisario_counts(),
        "cohorts": wave8_polisario_cohort_counts(),
        "country_quarantine_additions": sorted(
            WAVE8_POLISARIO_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "final_audit_signature": WAVE8_POLISARIO_FINAL_AUDIT_SIGNATURE,
        "held_candidate_ids": sorted(WAVE8_POLISARIO_HOLD_IDS),
        "point_quarantine_additions": sorted(
            WAVE8_POLISARIO_POINT_QUARANTINE_ADDITIONS
        ),
        "promoted_candidate_ids": sorted(WAVE8_POLISARIO_CONTRACT_IDS),
    }


_validate_static()
