"""Candidate-keyed audit of HCED's unresolved ``Spanish Liberals`` rows.

The label denotes the Isabeline government side in the First Carlist War,
not every Spanish liberal movement.  This lane therefore installs no alias.
It promotes only Alegría and Gulina, whose tactical results survive
independent review, and keeps Artaza and Asarta staged because the locked
year or outcome conflicts with the reviewed historical record.
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
    "WAVE8_SPANISH_LIBERALS_CONTRACT_IDS",
    "WAVE8_SPANISH_LIBERALS_CONTRACTS",
    "WAVE8_SPANISH_LIBERALS_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SPANISH_LIBERALS_ENTITIES",
    "WAVE8_SPANISH_LIBERALS_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SPANISH_LIBERALS_FUNNEL_AUDIT",
    "WAVE8_SPANISH_LIBERALS_HOLD_IDS",
    "WAVE8_SPANISH_LIBERALS_HOLDS",
    "WAVE8_SPANISH_LIBERALS_LOCATION_QUARANTINE_REASONS",
    "WAVE8_SPANISH_LIBERALS_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SPANISH_LIBERALS_RESERVED_IDS",
    "WAVE8_SPANISH_LIBERALS_ROW_HASHES",
    "WAVE8_SPANISH_LIBERALS_SOURCES",
    "install_wave8_spanish_liberals_entities",
    "install_wave8_spanish_liberals_sources",
    "promote_wave8_spanish_liberals_contracts",
    "validate_wave8_spanish_liberals_funnel",
    "validate_wave8_spanish_liberals_integration_dispositions",
    "validate_wave8_spanish_liberals_queue_contracts",
    "wave8_spanish_liberals_audit_signature",
    "wave8_spanish_liberals_cohort_counts",
    "wave8_spanish_liberals_counts",
    "wave8_spanish_liberals_metadata",
)


_LANE_NAME = "Wave 8 exact Spanish Liberal actor audit"
_MODULE_OWNER = "military_elo.promotion.wave8_spanish_liberals"
_EVENT_ID_PREFIX = "hced_wave8_spanish_liberals_"
_EXACT_LABEL = "spanish liberals"

_ISABELINE_FORCES = "isabeline_government_forces_first_carlist_war"
_CARLIST_FORCES = "carlist_army_first_war"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
    hold: bool = False,
) -> dict[str, Any]:
    roles = {"identity_boundary_or_context_reference"}
    if outcome:
        roles.add("outcome")
    if hold:
        roles.add("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-17",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_SPANISH_LIBERALS_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_spanish_liberals_aunamendi_alegria",
        "Batalla de Alegría",
        "https://aunamendi.eusko-ikaskuntza.eus/es/batalla-de-alegria/ar-8633/",
        "Auñamendi Eusko Entziklopedia / Eusko Ikaskuntza",
        "scholarly_regional_encyclopedia",
        "aunamendi_alegria",
        outcome=True,
    ),
    _source(
        "wave8_spanish_liberals_gee_alegria",
        "Batalla de Alegría",
        "https://gee.enciclo.es/articulo/batalla-de-alegria",
        "Gran Enciclopedia de España",
        "edited_national_encyclopedia",
        "gran_enciclopedia_espana_alegria",
        outcome=True,
    ),
    _source(
        "wave8_spanish_liberals_mod_gulina",
        "Infantes Caballeros de la Orden de San Fernando: Linares de Butrón",
        (
            "https://publicaciones.defensa.gob.es/media/downloadable/files/"
            "links/m/e/memorial_infanteria_52.pdf"
        ),
        "Ministerio de Defensa de España, Memorial de Infantería 52",
        "official_military_history",
        "spanish_mod_memorial_infanteria_52",
        outcome=True,
    ),
    _source(
        "wave8_spanish_liberals_revue_gulina",
        "Zumalacárregui et la guerre civile de Navarre: combat de Gulina",
        (
            "https://fr.wikisource.org/wiki/Page:Revue_des_Deux_Mondes_-_"
            "1851_-_tome_9.djvu/686"
        ),
        "Revue des Deux Mondes (1851 facsimile transcription)",
        "near_contemporary_historical_narrative",
        "revue_deux_mondes_1851_gulina",
        outcome=True,
    ),
    _source(
        "wave8_spanish_liberals_museum_asarta",
        "Nazar y Asarta (29-XII-1833)",
        (
            "https://www.zumalakarregimuseoa.eus/es/actividades/"
            "investigacion-y-documentacion/historia-del-siglo-xix-en-el-"
            "pais-vasco/batallas-y-acciones/nazar-y-asarta-29-xii-1833"
        ),
        "Museo Zumalakarregi Museoa",
        "official_museum_history",
        "zumalakarregi_museum_asarta",
        hold=True,
    ),
    _source(
        "wave8_spanish_liberals_gee_asarta",
        "Batalla de Asarta y Mendaza",
        "https://gee.enciclo.es/articulo/batalla-de-asarta-y-mendaza",
        "Gran Enciclopedia de España",
        "edited_national_encyclopedia",
        "gran_enciclopedia_espana_asarta",
        hold=True,
    ),
    _source(
        "wave8_spanish_liberals_museum_artaza",
        "Améscoas (19/24-IV-1835)",
        (
            "https://www.zumalakarregimuseoa.eus/es/actividades/"
            "investigacion-y-documentacion/historia-del-siglo-xix-en-el-"
            "pais-vasco/batallas-y-acciones/amescoas-19-24-iv-1835"
        ),
        "Museo Zumalakarregi Museoa",
        "official_museum_history",
        "zumalakarregi_museum_artaza",
        hold=True,
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_SPANISH_LIBERALS_SOURCES
}


WAVE8_SPANISH_LIBERALS_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": _ISABELINE_FORCES,
        "name": "Isabeline Government Forces (First Carlist War)",
        "kind": "civil_war_faction",
        "start_year": 1833,
        "end_year": 1840,
        "region": "Spain",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The armed forces supporting Isabella II and the regency during the "
            "First Carlist War. This conflict-bounded rating identity is not an "
            "alias for the Spanish state, every Spanish liberal movement, or "
            "later Isabeline forces, and it inherits no Elo from any of them. "
            "Only fingerprinted candidate-keyed contracts may use it."
        ),
        "source_ids": [
            "wave8_spanish_liberals_aunamendi_alegria",
            "wave8_spanish_liberals_gee_alegria",
            "wave8_spanish_liberals_mod_gulina",
            "wave8_spanish_liberals_revue_gulina",
        ],
    },
)


WAVE8_SPANISH_LIBERALS_ROW_HASHES: dict[str, str] = {
    "hced-Alegria1834-1": "5643b7e99363ca42123a63f29efc2d24b7293dd3b85d589b61ba614042a2a9c8",
    "hced-Artaza1834-1": "cd81f724365721250146a3c770797d27784a79b18a9381d3e770cf739db1dc79",
    "hced-Asarta1833-1": "bd305efe2efa6c551c7c6950bac089f478c4f689a6acae330e0e0d458ac07ddc",
    "hced-Gulina1834-1": "e67d3a294b116ddcf267b1bcd35aaf44cc63a44f478fdc3305f4dd55a3ad038e",
}

WAVE8_SPANISH_LIBERALS_FUNNEL_AUDIT: dict[str, Any] = {
    "candidate_ids": [],
    "event_candidate_id_sha256": (
        "935b85664b28e3be3f7262bb8fa3e72877b51169a4c11c7aa055409029005838"
    ),
    "events_touched": 4,
    "label": _EXACT_LABEL,
    "sole_blocker_events": 3,
    "zero_time_valid_candidates": 4,
}


def _canonical(name: str, date_text: str) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:1834:1834",
        "date_precision": "day",
        "date_text": date_text,
        "granularity": "single_battle_in_the_first_carlist_war",
        "name": name,
        "year_low": 1834,
        "year_high": 1834,
    }


def _contract(
    candidate_id: str,
    canonical_event: Mapping[str, Any],
    side_1: Iterable[str],
    side_2: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    confidence: float,
) -> dict[str, Any]:
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": WAVE8_SPANISH_LIBERALS_ROW_HASHES[candidate_id],
        "canonical_event": dict(canonical_event),
        "cohort": "first_carlist_war_1833_1840",
        "side_1_entity_ids": list(map(str, side_1)),
        "side_2_entity_ids": list(map(str, side_2)),
        "disposition": "promote",
        "result_type": "win",
        "winner_side": 1,
        "war_type": "civil_war",
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
        "actor_override": "candidate_keyed_exact_first_carlist_war_factions",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
        "audit_note": audit_note,
    }


WAVE8_SPANISH_LIBERALS_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Alegria1834-1": _contract(
        "hced-Alegria1834-1",
        _canonical("Battle of Alegría de Álava", "27 October 1834"),
        [_CARLIST_FORCES],
        [_ISABELINE_FORCES],
        [
            "wave8_spanish_liberals_aunamendi_alegria",
            "wave8_spanish_liberals_gee_alegria",
        ],
        (
            "Two independently edited Basque and Spanish encyclopedic sources "
            "identify Zumalacárregui's Carlist victory over O'Doyle's government "
            "troops on 27 October. Only that tactical battle is rated."
        ),
        confidence=0.94,
    ),
    "hced-Gulina1834-1": _contract(
        "hced-Gulina1834-1",
        _canonical("Battle of Gulina", "18 June 1834"),
        [_ISABELINE_FORCES],
        [_CARLIST_FORCES],
        [
            "wave8_spanish_liberals_mod_gulina",
            "wave8_spanish_liberals_revue_gulina",
        ],
        (
            "The Spanish military-history account says Linares's Isabeline line "
            "held and drove off the Carlists; the independent 1851 narrative "
            "likewise records six hours of combat ending when ammunition failure "
            "forced Zumalacárregui to order a retreat. The contract rates that "
            "tactical result, not casualties or later campaign effects."
        ),
        confidence=0.90,
    ),
}


WAVE8_SPANISH_LIBERALS_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Artaza1834-1": {
        "raw_row_sha256": WAVE8_SPANISH_LIBERALS_ROW_HASHES["hced-Artaza1834-1"],
        "cohort": "source_critical_holds",
        "disposition": "hold",
        "reason_code": "locked_year_conflicts_with_attested_action",
        "evidence_refs": ["wave8_spanish_liberals_museum_artaza"],
        "audit_note": (
            "The museum chronology places the Artaza action in the Améscoas "
            "operations of 19-24 April 1835, while the locked HCED row says 1834. "
            "The year cannot be silently repaired inside an exact-row promotion."
        ),
    },
    "hced-Asarta1833-1": {
        "raw_row_sha256": WAVE8_SPANISH_LIBERALS_ROW_HASHES["hced-Asarta1833-1"],
        "cohort": "source_critical_holds",
        "disposition": "hold",
        "reason_code": "locked_winner_conflicts_with_tactical_record",
        "evidence_refs": [
            "wave8_spanish_liberals_gee_asarta",
            "wave8_spanish_liberals_museum_asarta",
        ],
        "audit_note": (
            "HCED marks a Carlist win, but the museum account records a decisive "
            "Liberal flank attack followed by Zumalacárregui's retreat, and the "
            "edited national encyclopedia classifies the action as a Liberal "
            "triumph. A moral success or casualty imbalance cannot be substituted "
            "for the locked tactical winner."
        ),
    },
}

WAVE8_SPANISH_LIBERALS_CONTRACT_IDS = frozenset(
    WAVE8_SPANISH_LIBERALS_CONTRACTS
)
WAVE8_SPANISH_LIBERALS_HOLD_IDS = frozenset(WAVE8_SPANISH_LIBERALS_HOLDS)
WAVE8_SPANISH_LIBERALS_RESERVED_IDS = frozenset(
    {*WAVE8_SPANISH_LIBERALS_CONTRACT_IDS, *WAVE8_SPANISH_LIBERALS_HOLD_IDS}
)
WAVE8_SPANISH_LIBERALS_POINT_QUARANTINE_ADDITIONS = (
    WAVE8_SPANISH_LIBERALS_CONTRACT_IDS
)
WAVE8_SPANISH_LIBERALS_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_SPANISH_LIBERALS_LOCATION_QUARANTINE_REASONS: dict[str, dict[str, Any]] = {
    candidate_id: {
        "actions": ["withhold_point"],
        "reason": (
            "The reviewed sources establish the named battlefield and Spain but "
            "do not independently verify HCED's exact coordinate; retain the "
            "country assertion and withhold the point."
        ),
        "evidence_refs": list(contract["outcome_source_ids"]),
    }
    for candidate_id, contract in sorted(WAVE8_SPANISH_LIBERALS_CONTRACTS.items())
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_SPANISH_LIBERALS_CONTRACTS,
        "entities": WAVE8_SPANISH_LIBERALS_ENTITIES,
        "funnel": WAVE8_SPANISH_LIBERALS_FUNNEL_AUDIT,
        "holds": WAVE8_SPANISH_LIBERALS_HOLDS,
        "location_reasons": WAVE8_SPANISH_LIBERALS_LOCATION_QUARANTINE_REASONS,
        "row_hashes": WAVE8_SPANISH_LIBERALS_ROW_HASHES,
        "sources": WAVE8_SPANISH_LIBERALS_SOURCES,
    }


def wave8_spanish_liberals_audit_signature() -> str:
    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_SPANISH_LIBERALS_FINAL_AUDIT_SIGNATURE = (
    "3d259d1dcd15f760474a546d217970f8129a84c0afd29d3d587fa7cbe274a101"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    source_ids = set(_SOURCE_BY_ID)
    entity_ids = {str(entity["id"]) for entity in WAVE8_SPANISH_LIBERALS_ENTITIES}
    if len(source_ids) != len(WAVE8_SPANISH_LIBERALS_SOURCES):
        raise ValueError(f"{_LANE_NAME} duplicate source id")
    if entity_ids != {_ISABELINE_FORCES}:
        raise ValueError(f"{_LANE_NAME} entity inventory drift")
    if WAVE8_SPANISH_LIBERALS_CONTRACT_IDS & WAVE8_SPANISH_LIBERALS_HOLD_IDS:
        raise ValueError(f"{_LANE_NAME} promotion/hold overlap")
    if WAVE8_SPANISH_LIBERALS_RESERVED_IDS != set(
        WAVE8_SPANISH_LIBERALS_ROW_HASHES
    ):
        raise ValueError(f"{_LANE_NAME} disposition inventory drift")
    if WAVE8_SPANISH_LIBERALS_POINT_QUARANTINE_ADDITIONS != (
        WAVE8_SPANISH_LIBERALS_CONTRACT_IDS
    ) or WAVE8_SPANISH_LIBERALS_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} location policy drift")
    if set(WAVE8_SPANISH_LIBERALS_LOCATION_QUARANTINE_REASONS) != (
        WAVE8_SPANISH_LIBERALS_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} location reason inventory drift")

    used_sources: set[str] = set()
    entity = WAVE8_SPANISH_LIBERALS_ENTITIES[0]
    if entity["aliases"] or (entity["start_year"], entity["end_year"]) != (1833, 1840):
        raise ValueError(f"{_LANE_NAME} entity boundary drift")
    if not _is_sorted_unique(entity["source_ids"]):
        raise ValueError(f"{_LANE_NAME} entity evidence drift")
    used_sources.update(map(str, entity["source_ids"]))

    allowed_actors = {_ISABELINE_FORCES, _CARLIST_FORCES}
    for candidate_id, contract in WAVE8_SPANISH_LIBERALS_CONTRACTS.items():
        if contract["disposition"] != "promote" or contract["result_type"] != "win":
            raise ValueError(f"{_LANE_NAME} disposition drift: {candidate_id}")
        if contract["source_outcome_override"] or contract["outcome_reversal"]:
            raise ValueError(f"{_LANE_NAME} outcome override drift: {candidate_id}")
        actors = {
            *map(str, contract["side_1_entity_ids"]),
            *map(str, contract["side_2_entity_ids"]),
        }
        if actors != allowed_actors:
            raise ValueError(f"{_LANE_NAME} exact actor drift: {candidate_id}")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        if not _is_sorted_unique(evidence) or not _is_sorted_unique(outcomes):
            raise ValueError(f"{_LANE_NAME} evidence order drift: {candidate_id}")
        if set(outcomes) != set(evidence) or not set(evidence) <= source_ids:
            raise ValueError(f"{_LANE_NAME} evidence closure failed: {candidate_id}")
        families = sorted(
            {str(_SOURCE_BY_ID[source_id]["source_family_id"]) for source_id in outcomes}
        )
        if contract["outcome_source_family_ids"] != families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome family drift: {candidate_id}")
        used_sources.update(evidence)

    for candidate_id, hold in WAVE8_SPANISH_LIBERALS_HOLDS.items():
        evidence = list(map(str, hold["evidence_refs"]))
        if (
            hold["disposition"] != "hold"
            or not hold["reason_code"]
            or not _is_sorted_unique(evidence)
            or not set(evidence) <= source_ids
        ):
            raise ValueError(f"{_LANE_NAME} hold drift: {candidate_id}")
        used_sources.update(evidence)

    if used_sources != source_ids:
        raise ValueError(f"{_LANE_NAME} source fixtures are not exactly consumed")
    if wave8_spanish_liberals_audit_signature() != (
        WAVE8_SPANISH_LIBERALS_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")


def validate_wave8_spanish_liberals_queue_contracts(
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
    if exact_ids != WAVE8_SPANISH_LIBERALS_RESERVED_IDS or len(exact) != len(exact_ids):
        raise ValueError(f"{_LANE_NAME} exact-label inventory changed")
    by_id = {str(row["candidate_id"]): row for row in exact}
    for candidate_id, expected_hash in WAVE8_SPANISH_LIBERALS_ROW_HASHES.items():
        row = by_id[candidate_id]
        if canonical_hced_row_sha256(row) != expected_hash:
            raise ValueError(f"{_LANE_NAME} row fingerprint changed: {candidate_id}")
        if row.get("year_low") != row.get("year_high") or row.get("year_best") != row.get(
            "year_low"
        ):
            raise ValueError(f"{_LANE_NAME} year precision changed: {candidate_id}")
        if row.get("winner_raw") not in {row.get("side_1_raw"), row.get("side_2_raw")}:
            raise ValueError(f"{_LANE_NAME} outcome alignment changed: {candidate_id}")
        if row.get("winner_loser_complete") is not True or row.get("massacre_raw") != "No":
            raise ValueError(f"{_LANE_NAME} competitive-outcome guard changed: {candidate_id}")
    counts = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SPANISH_LIBERALS_CONTRACTS,
        WAVE8_SPANISH_LIBERALS_HOLDS,
        lane_name=_LANE_NAME,
    )
    return {**counts, "exact_label_rows": len(exact)}


def validate_wave8_spanish_liberals_funnel(
    funnel: Mapping[str, Any],
) -> dict[str, int]:
    _validate_static()
    labels = [row for row in funnel.get("labels", []) if row.get("label") == _EXACT_LABEL]
    if len(labels) != 1:
        raise ValueError(f"{_LANE_NAME} expected one funnel label")
    label = labels[0]
    checks = {
        "candidate_ids": list(map(str, label.get("candidate_ids", []))),
        "event_candidate_id_sha256": str(label.get("event_candidate_id_sha256")),
        "events_touched": int(label.get("events_touched", -1)),
        "label": str(label.get("label")),
        "sole_blocker_events": int(label.get("sole_blocker_events", -1)),
        "zero_time_valid_candidates": int(
            label.get("failure_cases", {}).get("zero_time_valid_candidates", -1)
        ),
    }
    if checks != WAVE8_SPANISH_LIBERALS_FUNNEL_AUDIT:
        raise ValueError(f"{_LANE_NAME} funnel pins changed: {checks}")
    return {
        "events_touched": checks["events_touched"],
        "sole_blocker_events": checks["sole_blocker_events"],
        "zero_time_valid_candidates": checks["zero_time_valid_candidates"],
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


_EVENT_ALIASES = {
    "hced-Alegria1834-1": {
        "Alegria",
        "Alegría",
        "Battle of Alegría de Álava",
        "Acción de Alegría de Álava",
    },
    "hced-Gulina1834-1": {
        "Gulina",
        "Battle of Gulina",
        "Venta de Gulina",
        "Erice",
    },
}
_DUPLICATE_MATCH_KEYS = frozenset(
    (1834, normalize_label(alias))
    for aliases in _EVENT_ALIASES.values()
    for alias in aliases
)


def _is_probable_twin(row: Mapping[str, Any]) -> bool:
    year = _row_year(row)
    return year is not None and any(
        (year, name) in _DUPLICATE_MATCH_KEYS for name in _row_names(row)
    )


def validate_wave8_spanish_liberals_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    validate_wave8_spanish_liberals_queue_contracts(hced_rows)
    hced_twins = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id")) not in WAVE8_SPANISH_LIBERALS_RESERVED_IDS
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
        if event.get("hced_candidate_id") not in WAVE8_SPANISH_LIBERALS_CONTRACT_IDS
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


def install_wave8_spanish_liberals_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SPANISH_LIBERALS_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_spanish_liberals_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SPANISH_LIBERALS_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SPANISH_LIBERALS_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SPANISH_LIBERALS_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_spanish_liberals_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_spanish_liberals_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SPANISH_LIBERALS_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_spanish_liberals_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(item["cohort"])
                for item in (
                    *WAVE8_SPANISH_LIBERALS_CONTRACTS.values(),
                    *WAVE8_SPANISH_LIBERALS_HOLDS.values(),
                )
            ).items()
        )
    )


def wave8_spanish_liberals_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": 0,
        "holds": len(WAVE8_SPANISH_LIBERALS_HOLDS),
        "new_entities": len(WAVE8_SPANISH_LIBERALS_ENTITIES),
        "new_sources": len(WAVE8_SPANISH_LIBERALS_SOURCES),
        "newly_rated_events": len(WAVE8_SPANISH_LIBERALS_CONTRACTS),
        "outcome_overrides": 0,
        "point_quarantine_additions": len(
            WAVE8_SPANISH_LIBERALS_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_SPANISH_LIBERALS_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_SPANISH_LIBERALS_RESERVED_IDS),
        "terminal_exclusions": 0,
    }


def wave8_spanish_liberals_metadata() -> dict[str, Any]:
    _validate_static()
    return {
        "counts": wave8_spanish_liberals_counts(),
        "cohorts": wave8_spanish_liberals_cohort_counts(),
        "final_audit_signature": WAVE8_SPANISH_LIBERALS_FINAL_AUDIT_SIGNATURE,
        "hold_ids": sorted(WAVE8_SPANISH_LIBERALS_HOLD_IDS),
        "promoted_candidate_ids": sorted(WAVE8_SPANISH_LIBERALS_CONTRACT_IDS),
    }


_validate_static()
