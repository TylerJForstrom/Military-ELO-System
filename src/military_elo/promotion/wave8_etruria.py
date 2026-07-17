"""Candidate-keyed audit of HCED's four unresolved ``Etruria`` rows.

The source label is not a polity identity.  It denotes Veii in two Roman
engagements, a maritime Etruscan force at Cumae, and—incorrectly—the Latin
and Tarquin coalition at Lake Regillus.  This lane therefore opens no global
``Etruria`` or ``Etruscan`` alias.  Every row receives a narrow tactical
binding, while the Regillus reversal is explicitly source-backed and marked
as a low-confidence traditional account rather than silently repairing HCED.
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
    "WAVE8_ETRURIA_CONTRACT_IDS",
    "WAVE8_ETRURIA_CONTRACTS",
    "WAVE8_ETRURIA_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_ETRURIA_ENTITIES",
    "WAVE8_ETRURIA_FINAL_AUDIT_SIGNATURE",
    "WAVE8_ETRURIA_FUNNEL_AUDIT",
    "WAVE8_ETRURIA_HOLD_IDS",
    "WAVE8_ETRURIA_HOLDS",
    "WAVE8_ETRURIA_LOCATION_QUARANTINE_REASONS",
    "WAVE8_ETRURIA_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_ETRURIA_RESERVED_IDS",
    "WAVE8_ETRURIA_ROW_HASHES",
    "WAVE8_ETRURIA_SOURCES",
    "install_wave8_etruria_entities",
    "install_wave8_etruria_sources",
    "promote_wave8_etruria_contracts",
    "validate_wave8_etruria_funnel",
    "validate_wave8_etruria_integration_dispositions",
    "validate_wave8_etruria_queue_contracts",
    "wave8_etruria_audit_signature",
    "wave8_etruria_cohort_counts",
    "wave8_etruria_counts",
    "wave8_etruria_metadata",
)


_LANE_NAME = "Wave 8 exact Etruria actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_etruria"
_EVENT_ID_PREFIX = "hced_wave8_etruria_"
_EXACT_LABELS = frozenset({"etruria"})

_VEII = "veii_city_state_reviewed_477_396_bce"
_FABIAN_FORCE = "fabian_clan_client_force_cremera_477_bce"
_CUMAE = "cumae_city_state_battle_474_bce"
_ETRUSCAN_FLEET = "etruscan_maritime_force_cumae_474_bce"
_LATIN_TARQUIN_COALITION = "latin_tarquin_coalition_regillus_499_496_bce"
_ROME = "roman_republic"
_SYRACUSE = "syracuse_city_state"


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
        "accessed": "2026-07-17",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(set(map(str, evidence_roles))),
    }


WAVE8_ETRURIA_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_etruria_dionysius_cremera",
        "Dionysius of Halicarnassus, Roman Antiquities 9.15-23",
        (
            "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/"
            "Dionysius_of_Halicarnassus/9A%2A.html"
        ),
        "Dionysius of Halicarnassus / LacusCurtius",
        "translated_primary_source",
        "dionysius_roman_antiquities",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_etruria_treccani_cremera",
        "Cremera",
        "https://www.treccani.it/enciclopedia/cremera_%28Enciclopedia-Italiana%29/",
        "Istituto della Enciclopedia Italiana",
        "scholarly_encyclopedia_entry",
        "treccani_enciclopedia_italiana",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_etruria_diodorus_cumae",
        "Diodorus Siculus, Library of History 11.51 (Peter Green translation)",
        (
            "https://assets-us-01.kc-usercontent.com/"
            "c7bb3f89-eb78-007e-971a-d5864cf7a236/"
            "0fa32b90-feb4-4a8d-a853-9ddc8178f510/"
            "Diodorus-Siculus-11.50.pdf"
        ),
        "University of Texas Press",
        "translated_primary_source",
        "diodorus_library_history_green_translation",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_etruria_british_museum_cumae_helmet",
        "Etruscan helmet dedicated from the spoils at Cumae",
        "https://www.britishmuseum.org/collection/object/G_1823-0610-1",
        "The British Museum",
        "museum_collection_record",
        "british_museum_collection",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_etruria_dionysius_regillus",
        "Dionysius of Halicarnassus, Roman Antiquities 6.4-13",
        (
            "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/"
            "Dionysius_of_Halicarnassus/6A%2A.html"
        ),
        "Dionysius of Halicarnassus / LacusCurtius",
        "translated_primary_source",
        "dionysius_roman_antiquities",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_etruria_ocd_regillus",
        "Regillus lake",
        "https://academic.oup.com/edited-volume/61673/chapter/550490415",
        "Andrew Drummond / Oxford Classical Dictionary",
        "scholarly_encyclopedia_entry",
        "oxford_classical_dictionary",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_etruria_plutarch_veii",
        "Plutarch, Life of Camillus 4-5",
        (
            "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/"
            "Plutarch/Lives/Camillus%2A.html"
        ),
        "Plutarch / LacusCurtius",
        "translated_primary_source",
        "plutarch_parallel_lives",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
    _source(
        "wave8_etruria_livius_veii",
        "Veii",
        "https://www.livius.org/articles/place/veii/",
        "Livius.org",
        "expert_historical_reference",
        "livius_ancient_history_reference",
        ["identity_boundary_or_context_reference", "outcome"],
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_ETRURIA_SOURCES}


WAVE8_ETRURIA_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _VEII,
        "name": "Veii (reviewed 477-396 BCE series)",
        "kind": "city_state",
        "start_year": -477,
        "end_year": -396,
        "region": "Southern Etruria",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Release identity bounded to the two independently reviewed HCED "
            "actions at Cremera and the final Roman siege. The boundary is an "
            "evidence window, not a founding date. It opens no Veii, Etruria, or "
            "Etruscan alias and ends with the conventional 396 BCE Roman capture."
        ),
        "source_ids": [
            "wave8_etruria_dionysius_cremera",
            "wave8_etruria_livius_veii",
            "wave8_etruria_plutarch_veii",
            "wave8_etruria_treccani_cremera",
        ],
    },
    {
        "id": _FABIAN_FORCE,
        "name": "Fabian clan and client force at the Cremera (477 BCE)",
        "kind": "engagement_bounded_clan_client_force",
        "start_year": -477,
        "end_year": -477,
        "region": "Cremera frontier north of Rome",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the Fabii, clients, and friends who held the Cremera "
            "fortress and were destroyed in the reviewed engagement. It does not "
            "substitute for the Roman Republic, the wider Roman army, or the "
            "Fabian family in another year."
        ),
        "source_ids": [
            "wave8_etruria_dionysius_cremera",
            "wave8_etruria_treccani_cremera",
        ],
    },
    {
        "id": _CUMAE,
        "name": "Cumaean city force at the naval battle of 474 BCE",
        "kind": "engagement_bounded_city_polity",
        "start_year": -474,
        "end_year": -474,
        "region": "Cumae and the Bay of Naples",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the inhabitants of Cumae who joined Hieron's Syracusan "
            "squadron in Diodorus's account. It does not create a generic Cumae "
            "identity for the city's Greek, Oscan, or Roman periods."
        ),
        "source_ids": [
            "wave8_etruria_british_museum_cumae_helmet",
            "wave8_etruria_diodorus_cumae",
        ],
    },
    {
        "id": _ETRUSCAN_FLEET,
        "name": "Etruscan maritime force at Cumae (474 BCE)",
        "kind": "engagement_bounded_maritime_force",
        "start_year": -474,
        "end_year": -474,
        "region": "Tyrrhenian Sea off Cumae",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the Tyrrhenian ships defeated off Cumae and corroborated "
            "by Hieron's inscribed dedication of captured Etruscan spoils. No "
            "single Etruscan city, league, or people inherits this fleet rating."
        ),
        "source_ids": [
            "wave8_etruria_british_museum_cumae_helmet",
            "wave8_etruria_diodorus_cumae",
        ],
    },
    {
        "id": _LATIN_TARQUIN_COALITION,
        "name": "Latin and Tarquin coalition at Lake Regillus",
        "kind": "engagement_bounded_multistate_coalition",
        "start_year": -499,
        "end_year": -496,
        "region": "Latium near Tusculum",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Bounded to the traditional Lake Regillus opposing army: Latins led "
            "by Octavius Mamilius together with Tarquin supporters and Roman "
            "exiles. The 499-496 BCE window expresses the two ancient chronologies; "
            "it is not a continuous four-year polity or a generic Latin League."
        ),
        "source_ids": [
            "wave8_etruria_dionysius_regillus",
            "wave8_etruria_ocd_regillus",
        ],
    },
)


WAVE8_ETRURIA_ROW_HASHES: dict[str, str] = {
    "hced-Cremera-477-1": "144838ba04d8487ae21ba8503e428313cb738562f6766b7f399780f821d699b6",
    "hced-Cumae-474-1": "35766c541d15eea4fb3d7aaaa02faef778eea28a2675a9b1caaf6d7cedc32700",
    "hced-Lake Regillus-496-1": "c54004699326a9000d29192d215f5cc454f493a7a0769351fbbb94d393f59277",
    "hced-Veii-405-1": "36d8f008ca46a6892ac6ac240344055c386e0361094f9d188cf887c220e1d51c",
}

WAVE8_ETRURIA_FUNNEL_AUDIT: dict[str, dict[str, Any]] = {
    "etruria": {
        "candidate_ids": [],
        "centuries": {"BCE_05": 4},
        "components_bridged": 0,
        "components_touched": 1,
        "event_candidate_id_sha256": (
            "bfa71c0be064800bba01754aca6ccacfbd218a5134fdd58103efebf37ae309e7"
        ),
        "events_touched": 4,
        "failure_cases": {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 0,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 4,
        },
        "label": "etruria",
        "rated_counterpart_entities": 1,
        "sole_blocker_events": 3,
        "time_valid_candidate_ids": [],
        "unresolved_side_attempts": 4,
    }
}


def _canonical(
    name: str,
    year_low: int,
    year_high: int,
    date_text: str,
    granularity: str = "pitched_battle",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{year_high}",
        "date_precision": "year" if year_low == year_high else "range",
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": year_high,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_sources: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
    winner_side: int,
    actor_override: str,
    source_outcome_override: bool = False,
    outcome_reversal: bool = False,
    date_source_ids: Iterable[str] = (),
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_sources)))
    date_sources = sorted(set(map(str, date_source_ids)))
    return {
        "raw_row_sha256": WAVE8_ETRURIA_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": cohort,
        "side_1_entity_ids": list(map(str, side_1_entity_ids)),
        "side_2_entity_ids": list(map(str, side_2_entity_ids)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": winner_side,
        "war_type": "interstate_limited",
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": outcome_reversal,
        "source_date_override": bool(date_sources),
        "date_source_ids": date_sources,
        "actor_override": actor_override,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_ETRURIA_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Cremera-477-1": _contract(
        "hced-Cremera-477-1",
        _canonical(
            "Battle of the Cremera",
            -477,
            -477,
            "477 BCE in the Roman annalistic tradition",
        ),
        "veientine_war_cremera",
        [_VEII],
        [_FABIAN_FORCE],
        {
            "wave8_etruria_dionysius_cremera",
            "wave8_etruria_treccani_cremera",
        },
        {
            "wave8_etruria_dionysius_cremera",
            "wave8_etruria_treccani_cremera",
        },
        (
            "Dionysius identifies the Veientes' war, the Fabian clan and its "
            "clients, destruction of that force, and capture of the Cremera "
            "fortress; Treccani independently preserves the Veientine ambush. "
            "The narrow Fabian force is rated instead of all republican Rome."
        ),
        confidence=0.82,
        winner_side=1,
        actor_override="source_backed_veii_and_fabian_client_force",
    ),
    "hced-Cumae-474-1": _contract(
        "hced-Cumae-474-1",
        _canonical(
            "Battle of Cumae",
            -474,
            -474,
            "474 BCE (Diodorus 11.51 and Hieron's inscribed dedication)",
            "naval_battle",
        ),
        "syracusan_etruscan_war_cumae",
        [_CUMAE, _SYRACUSE],
        [_ETRUSCAN_FLEET],
        {
            "wave8_etruria_british_museum_cumae_helmet",
            "wave8_etruria_diodorus_cumae",
        },
        {
            "wave8_etruria_british_museum_cumae_helmet",
            "wave8_etruria_diodorus_cumae",
        },
        (
            "Diodorus says Hieron's squadron joined Cumae's inhabitants, "
            "destroyed Tyrrhenian ships, and won the sea battle. The British "
            "Museum helmet preserves Hieron and the Syracusans' dedication of "
            "Etruscan spoils from Cumae. No Etruscan city is guessed."
        ),
        confidence=0.98,
        winner_side=1,
        actor_override="source_backed_cumaean_syracusan_and_etruscan_fleet",
    ),
    "hced-Lake Regillus-496-1": _contract(
        "hced-Lake Regillus-496-1",
        _canonical(
            "Battle of Lake Regillus",
            -499,
            -496,
            (
                "Traditional chronologies differ between 499 and 496 BCE; the "
                "interval records uncertainty, not a four-year battle"
            ),
        ),
        "early_roman_latin_war_regillus",
        [_LATIN_TARQUIN_COALITION],
        [_ROME],
        {
            "wave8_etruria_dionysius_regillus",
            "wave8_etruria_ocd_regillus",
        },
        {
            "wave8_etruria_dionysius_regillus",
            "wave8_etruria_ocd_regillus",
        },
        (
            "HCED reverses the traditional result and mislabels the opposing "
            "army as Etruria. Dionysius instead identifies Latins, Tarquins, and "
            "Roman exiles and narrates a Roman victory; the Oxford Classical "
            "Dictionary calls it an alleged Roman victory over the Latini in "
            "499 or 496 BCE. The rating records that source-attested tradition "
            "at deliberately low confidence, not archaeological certainty."
        ),
        confidence=0.70,
        winner_side=2,
        actor_override="source_backed_latin_tarquin_coalition_and_roman_republic",
        source_outcome_override=True,
        outcome_reversal=True,
        date_source_ids={
            "wave8_etruria_dionysius_regillus",
            "wave8_etruria_ocd_regillus",
        },
    ),
    "hced-Veii-405-1": _contract(
        "hced-Veii-405-1",
        _canonical(
            "Siege and capture of Veii",
            -405,
            -396,
            (
                "Conventional ten-year siege from 405 through the Roman capture "
                "in 396 BCE"
            ),
            "siege",
        ),
        "third_veientine_war_siege",
        [_ROME],
        [_VEII],
        {
            "wave8_etruria_livius_veii",
            "wave8_etruria_plutarch_veii",
        },
        {
            "wave8_etruria_livius_veii",
            "wave8_etruria_plutarch_veii",
        },
        (
            "Plutarch describes Camillus taking Veii by storm in the tenth year, "
            "while Livius dates the Roman capture to 396 BCE and distinguishes "
            "the earlier siege. The HCED massacre marker is treated only as "
            "unscored aftermath; the competitive assertion is the siege capture."
        ),
        confidence=0.88,
        winner_side=1,
        actor_override="source_backed_roman_republic_and_veii_city_state",
        date_source_ids={
            "wave8_etruria_livius_veii",
            "wave8_etruria_plutarch_veii",
        },
    ),
}


WAVE8_ETRURIA_HOLDS: dict[str, dict[str, Any]] = {}
WAVE8_ETRURIA_CONTRACT_IDS = frozenset(WAVE8_ETRURIA_CONTRACTS)
WAVE8_ETRURIA_HOLD_IDS = frozenset(WAVE8_ETRURIA_HOLDS)
WAVE8_ETRURIA_RESERVED_IDS = frozenset(
    {*WAVE8_ETRURIA_CONTRACT_IDS, *WAVE8_ETRURIA_HOLD_IDS}
)
WAVE8_ETRURIA_POINT_QUARANTINE_ADDITIONS = WAVE8_ETRURIA_CONTRACT_IDS
WAVE8_ETRURIA_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_ETRURIA_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    "hced-Cremera-477-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed histories locate the action on the Cremera frontier "
            "but do not validate HCED's exact modern point. Retain Italy only."
        ),
        "evidence_refs": [
            "wave8_etruria_dionysius_cremera",
            "wave8_etruria_treccani_cremera",
        ],
    },
    "hced-Cumae-474-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The event was a naval battle off Cumae; HCED's city geocode is not "
            "a source-bound sea-battle coordinate. Retain Italy only."
        ),
        "evidence_refs": [
            "wave8_etruria_british_museum_cumae_helmet",
            "wave8_etruria_diodorus_cumae",
        ],
    },
    "hced-Lake Regillus-496-1": {
        "actions": ["withhold_point"],
        "reason": (
            "The Oxford Classical Dictionary gives multiple modern site "
            "possibilities for the alleged battle, so HCED's exact point is not "
            "promoted. Retain Italy only."
        ),
        "evidence_refs": ["wave8_etruria_ocd_regillus"],
    },
    "hced-Veii-405-1": {
        "actions": ["withhold_point"],
        "reason": (
            "HCED supplies a settlement geocode rather than a documented siege "
            "or breach coordinate. Retain Italy only."
        ),
        "evidence_refs": [
            "wave8_etruria_livius_veii",
            "wave8_etruria_plutarch_veii",
        ],
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_ETRURIA_CONTRACTS,
        "entities": WAVE8_ETRURIA_ENTITIES,
        "funnel": WAVE8_ETRURIA_FUNNEL_AUDIT,
        "holds": WAVE8_ETRURIA_HOLDS,
        "location_reasons": WAVE8_ETRURIA_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_ETRURIA_ROW_HASHES,
        "sources": WAVE8_ETRURIA_SOURCES,
    }


def wave8_etruria_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_ETRURIA_FINAL_AUDIT_SIGNATURE = (
    "5f880aa13df1c6b04e761323190f9641c075f844a0b29477aa2f5a85c2984969"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = {str(entity["id"]) for entity in WAVE8_ETRURIA_ENTITIES}
    expected_entity_ids = {
        _VEII,
        _FABIAN_FORCE,
        _CUMAE,
        _ETRUSCAN_FLEET,
        _LATIN_TARQUIN_COALITION,
    }
    if len(source_ids) != len(WAVE8_ETRURIA_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if entity_ids != expected_entity_ids:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_ETRURIA_RESERVED_IDS != set(WAVE8_ETRURIA_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_ETRURIA_HOLDS or WAVE8_ETRURIA_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} unexpected hold drift")
    if WAVE8_ETRURIA_POINT_QUARANTINE_ADDITIONS != WAVE8_ETRURIA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point policy drift")
    if WAVE8_ETRURIA_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country policy drift")
    if set(WAVE8_ETRURIA_LOCATION_QUARANTINE_REASONS) != WAVE8_ETRURIA_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    expected_windows = {
        _VEII: (-477, -396),
        _FABIAN_FORCE: (-477, -477),
        _CUMAE: (-474, -474),
        _ETRUSCAN_FLEET: (-474, -474),
        _LATIN_TARQUIN_COALITION: (-499, -496),
    }
    used_sources: set[str] = set()
    for entity in WAVE8_ETRURIA_ENTITIES:
        entity_id = str(entity["id"])
        if (
            entity["aliases"]
            or (entity["start_year"], entity["end_year"])
            != expected_windows[entity_id]
            or normalize_label(entity["name"]) in _EXACT_LABELS
            or not _is_sorted_unique(entity["source_ids"])
        ):
            raise ValueError(f"{_LANE_NAME} identity boundary or alias drift")
        used_sources.update(set(map(str, entity["source_ids"])) & source_ids)

    expected_contracts = {
        "hced-Cremera-477-1": (-477, -477, [_VEII], [_FABIAN_FORCE], 1),
        "hced-Cumae-474-1": (-474, -474, [_CUMAE, _SYRACUSE], [_ETRUSCAN_FLEET], 1),
        "hced-Lake Regillus-496-1": (
            -499,
            -496,
            [_LATIN_TARQUIN_COALITION],
            [_ROME],
            2,
        ),
        "hced-Veii-405-1": (-405, -396, [_ROME], [_VEII], 1),
    }
    for candidate_id, contract in WAVE8_ETRURIA_CONTRACTS.items():
        low, high, side_1, side_2, winner_side = expected_contracts[candidate_id]
        canonical = contract["canonical_event"]
        is_regillus = candidate_id == "hced-Lake Regillus-496-1"
        if (
            contract["disposition"] != "promote"
            or contract["result_type"] != "win"
            or contract["winner_side"] != winner_side
            or (canonical["year_low"], canonical["year_high"]) != (low, high)
            or contract["side_1_entity_ids"] != side_1
            or contract["side_2_entity_ids"] != side_2
            or contract["source_outcome_override"] is not is_regillus
            or contract["outcome_reversal"] is not is_regillus
        ):
            raise ValueError(f"{_LANE_NAME} contract drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        date_sources = list(map(str, contract["date_source_ids"]))
        if (
            not _is_sorted_unique(evidence)
            or not _is_sorted_unique(outcomes)
            or not _is_sorted_unique(date_sources)
            or not set(outcomes) <= set(evidence) <= source_ids
            or not set(date_sources) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        expected_date_override = candidate_id in {
            "hced-Lake Regillus-496-1",
            "hced-Veii-405-1",
        }
        if contract["source_date_override"] is not expected_date_override:
            raise ValueError(f"{_LANE_NAME} date-override drift: {candidate_id}")
        used_sources.update(evidence)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if (
        WAVE8_ETRURIA_FINAL_AUDIT_SIGNATURE != "__PENDING__"
        and wave8_etruria_audit_signature() != WAVE8_ETRURIA_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_etruria_queue_contracts(
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
    if exact_ids != WAVE8_ETRURIA_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    expected_rows = {
        "hced-Cremera-477-1": (-477, "Etruria", "Rome", "Etruria", "No"),
        "hced-Cumae-474-1": (-474, "Syracuse", "Etruria", "Syracuse", "No"),
        "hced-Lake Regillus-496-1": (-496, "Etruria", "Rome", "Etruria", "No"),
        "hced-Veii-405-1": (
            -405,
            "Rome",
            "Etruria",
            "Rome",
            "Battle followed by massacre",
        ),
    }
    for candidate_id, expected_hash in WAVE8_ETRURIA_ROW_HASHES.items():
        row = by_id[candidate_id]
        year, side_1, side_2, winner, massacre = expected_rows[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if (
            (row.get("year_low"), row.get("year_high")) != (year, year)
            or row.get("side_1_raw") != side_1
            or row.get("side_2_raw") != side_2
            or row.get("winner_raw") != winner
            or row.get("winner_raw") != row.get("side_1_raw")
            or row.get("loser_raw") != row.get("side_2_raw")
            or row.get("winner_loser_complete") is not True
            or row.get("massacre_raw") != massacre
        ):
            raise ValueError(f"{_LANE_NAME} raw-row semantics changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_ETRURIA_CONTRACTS,
        WAVE8_ETRURIA_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_etruria_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    _validate_static()
    rows = {
        str(row.get("label")): row
        for row in funnel.get("labels", [])
        if row.get("label") in _EXACT_LABELS
    }
    if set(rows) != _EXACT_LABELS:
        raise ValueError(f"{_LANE_NAME} funnel label missing")
    row = rows["etruria"]
    checks = {
        "candidate_ids": list(map(str, row.get("candidate_ids", []))),
        "centuries": dict(row.get("centuries", {})),
        "components_bridged": int(row.get("components_bridged", -1)),
        "components_touched": int(row.get("components_touched", -1)),
        "event_candidate_id_sha256": str(row.get("event_candidate_id_sha256")),
        "events_touched": int(row.get("events_touched", -1)),
        "failure_cases": {
            key: int(row.get("failure_cases", {}).get(key, -1))
            for key in WAVE8_ETRURIA_FUNNEL_AUDIT["etruria"]["failure_cases"]
        },
        "label": str(row.get("label")),
        "rated_counterpart_entities": int(row.get("rated_counterpart_entities", -1)),
        "sole_blocker_events": int(row.get("sole_blocker_events", -1)),
        "time_valid_candidate_ids": list(
            map(str, row.get("time_valid_candidate_ids", []))
        ),
        "unresolved_side_attempts": int(row.get("unresolved_side_attempts", -1)),
    }
    expected = WAVE8_ETRURIA_FUNNEL_AUDIT["etruria"]
    if checks != expected:
        raise ValueError(f"{_LANE_NAME} funnel pin changed: {checks}")
    return {
        "events_touched": expected["events_touched"],
        "holds": len(WAVE8_ETRURIA_HOLDS),
        "sole_blocker_events": expected["sole_blocker_events"],
        "unresolved_side_attempts": expected["unresolved_side_attempts"],
        "zero_time_valid_candidates": expected["failure_cases"][
            "zero_time_valid_candidates"
        ],
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


_DUPLICATE_ALIASES: dict[int, set[str]] = {
    -499: {"Lake Regillus", "Battle of Lake Regillus"},
    -498: {"Lake Regillus", "Battle of Lake Regillus"},
    -497: {"Lake Regillus", "Battle of Lake Regillus"},
    -496: {"Lake Regillus", "Battle of Lake Regillus"},
    -477: {"Cremera", "Battle of the Cremera", "Battle of Cremera"},
    -474: {"Cumae", "Battle of Cumae"},
    -405: {"Veii", "Siege of Veii", "Siege and capture of Veii"},
    -396: {"Veii", "Capture of Veii", "Siege and capture of Veii"},
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (year, normalize_label(alias))
    for year, aliases in _DUPLICATE_ALIASES.items()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_etruria_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_etruria_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_ETRURIA_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_ETRURIA_CONTRACT_IDS
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


def install_wave8_etruria_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_ETRURIA_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_etruria_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_ETRURIA_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_ETRURIA_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_ETRURIA_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_etruria_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_etruria_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_ETRURIA_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_etruria_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_ETRURIA_CONTRACTS.values()
            ).items()
        )
    )


def wave8_etruria_counts() -> dict[str, int]:
    return {
        "country_quarantine_additions": len(WAVE8_ETRURIA_COUNTRY_QUARANTINE_ADDITIONS),
        "holds": len(WAVE8_ETRURIA_HOLDS),
        "new_entities": len(WAVE8_ETRURIA_ENTITIES),
        "new_sources": len(WAVE8_ETRURIA_SOURCES),
        "newly_rated_events": len(WAVE8_ETRURIA_CONTRACTS),
        "outcome_overrides": sum(
            bool(contract.get("source_outcome_override"))
            for contract in WAVE8_ETRURIA_CONTRACTS.values()
        ),
        "outcome_reversals": sum(
            bool(contract.get("outcome_reversal"))
            for contract in WAVE8_ETRURIA_CONTRACTS.values()
        ),
        "point_quarantine_additions": len(WAVE8_ETRURIA_POINT_QUARANTINE_ADDITIONS),
        "promotion_contracts": len(WAVE8_ETRURIA_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_ETRURIA_RESERVED_IDS),
        "source_date_overrides": sum(
            bool(contract.get("source_date_override"))
            for contract in WAVE8_ETRURIA_CONTRACTS.values()
        ),
        "terminal_exclusions": 0,
    }


def wave8_etruria_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_etruria_counts(),
        "cohorts": wave8_etruria_cohort_counts(),
        "final_audit_signature": WAVE8_ETRURIA_FINAL_AUDIT_SIGNATURE,
        "promoted_candidate_ids": sorted(WAVE8_ETRURIA_CONTRACT_IDS),
        "hold_candidate_ids": sorted(WAVE8_ETRURIA_HOLD_IDS),
    }


_validate_static()
