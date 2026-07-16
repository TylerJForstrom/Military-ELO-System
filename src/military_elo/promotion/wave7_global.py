"""Fail-closed Global/South HCED promotions and identity migrations for Wave 7."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _domain, _event_key, _participants, _scale, _slug, normalize_label
from .hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
    build_hced_location_fields,
    hced_candidate_id,
)
from .wave7_global_data import (
    WAVE7_GLOBAL_ENTITIES,
    WAVE7_GLOBAL_FINAL_AUDIT_SIGNATURE,
    WAVE7_GLOBAL_HCED_CONTRACTS,
    WAVE7_GLOBAL_HCED_HOLDS,
    WAVE7_GLOBAL_ORANGE_MIGRATIONS,
    WAVE7_GLOBAL_SOURCES,
    WAVE7_GLOBAL_SUPERSESSIONS,
)


WAVE7_GLOBAL_HCED_CONTRACT_IDS = frozenset(WAVE7_GLOBAL_HCED_CONTRACTS)
WAVE7_GLOBAL_HCED_HOLD_IDS = frozenset(WAVE7_GLOBAL_HCED_HOLDS)
WAVE7_GLOBAL_MIGRATION_CANDIDATE_IDS = frozenset(
    str(spec["candidate_id"]) for spec in WAVE7_GLOBAL_ORANGE_MIGRATIONS.values()
)
WAVE7_GLOBAL_RESERVED_IDS = (
    WAVE7_GLOBAL_HCED_CONTRACT_IDS
    | WAVE7_GLOBAL_HCED_HOLD_IDS
    | WAVE7_GLOBAL_MIGRATION_CANDIDATE_IDS
)

_EXISTING_EVIDENCE_SOURCE_IDS = frozenset({"whe_kadesh"})
_ORANGE_OLD_ENTITY_ID = "clio_q218023_1856_cfb4e08e"
_ORANGE_NEW_ENTITY_ID = "orange_free_state_1854"

# These fields contain every source value used to identify, orient, locate, or
# score a reviewed HCED row. Queue workflow flags and generic extraction prose
# are intentionally excluded so the fingerprint is semantic rather than a
# serialization/version pin.
HCED_CANDIDATE_FINGERPRINT_FIELDS = (
    "candidate_id",
    "source_record_id",
    "source_row",
    "source_snapshot",
    "name",
    "year_low",
    "year_high",
    "side_1_raw",
    "side_2_raw",
    "winner_raw",
    "loser_raw",
    "participants_raw",
    "war_names",
    "consulted_source_raw",
    "duplicate_source_id",
    "seshat_side_1_candidates",
    "seshat_side_2_candidates",
    "theatre_raw",
    "scale_raw",
    "scale_inferred_raw",
    "latitude",
    "longitude",
    "modern_location_country",
)

CLIOPATRIA_SUPERSESSION_FINGERPRINT_FIELDS = (
    "candidate_id",
    "canonical_name_candidate",
    "start_year",
    "end_year",
    "identity_basis",
    "record_type",
    "source",
    "source_snapshot",
    "interval_segments",
    "temporal_coverage_groups",
    "seshat_ids",
    "wikidata_ids",
    "wikipedia_titles",
)


def canonical_object_sha256(value: Any) -> str:
    """Return the canonical SHA-256 used by all Wave 7 Global contracts."""

    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonical_hced_row_sha256(row: Mapping[str, Any]) -> str:
    return canonical_object_sha256(
        {field: row.get(field) for field in HCED_CANDIDATE_FINGERPRINT_FIELDS}
    )


def canonical_cliopatria_supersession_sha256(row: Mapping[str, Any]) -> str:
    return canonical_object_sha256(
        {field: row.get(field) for field in CLIOPATRIA_SUPERSESSION_FINGERPRINT_FIELDS}
    )


def canonical_event_sha256(event: Mapping[str, Any]) -> str:
    return canonical_object_sha256(dict(event))


def _rows_by_candidate_id(
    rows: Iterable[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            indexed.setdefault(candidate_id, []).append(row)
    return indexed


def _validate_exact_hced_rows(
    rows_by_id: Mapping[str, list[dict[str, Any]]],
    contracts: Mapping[str, Mapping[str, Any]],
    *,
    description: str,
) -> None:
    for candidate_id, contract in contracts.items():
        rows = rows_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"Wave 7 Global {description} {candidate_id} expected exactly one "
                f"queue row, found {len(rows)}"
            )
        actual = canonical_hced_row_sha256(rows[0])
        expected = str(contract["raw_row_sha256"])
        if actual != expected:
            raise ValueError(
                f"Wave 7 Global {description} {candidate_id} raw-row fingerprint "
                f"changed ({actual} != {expected})"
            )


def _audit_signature() -> str:
    lines: list[str] = []
    for candidate_id, contract in WAVE7_GLOBAL_HCED_CONTRACTS.items():
        lines.append(
            f"promote|{candidate_id}|{contract['raw_row_sha256']}|"
            f"{contract['canonical_event']['canonical_key']}"
        )
    for candidate_id, contract in WAVE7_GLOBAL_HCED_HOLDS.items():
        lines.append(
            f"hold|{candidate_id}|{contract['raw_row_sha256']}|"
            f"{contract['canonical_event']['canonical_key']}"
        )
    for event_id, migration in WAVE7_GLOBAL_ORANGE_MIGRATIONS.items():
        lines.append(
            f"migrate|{migration['candidate_id']}|{migration['raw_row_sha256']}|"
            f"{event_id}|{migration['source_event_sha256']}"
        )
    return hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode("utf-8")).hexdigest()


def _validate_fixture_inventory() -> None:
    if len(WAVE7_GLOBAL_HCED_CONTRACTS) != 37:
        raise ValueError("Wave 7 Global must contain exactly 37 new-event contracts")
    if len(WAVE7_GLOBAL_HCED_HOLDS) != 5:
        raise ValueError("Wave 7 Global must contain exactly 5 explicit holds")
    if len(WAVE7_GLOBAL_ORANGE_MIGRATIONS) != 5:
        raise ValueError("Wave 7 Global must contain exactly 5 Orange migrations")
    if len(WAVE7_GLOBAL_ENTITIES) != 8 or len(WAVE7_GLOBAL_SOURCES) != 13:
        raise ValueError("Wave 7 Global entity/source fixture inventory changed")
    if (
        WAVE7_GLOBAL_HCED_CONTRACT_IDS & WAVE7_GLOBAL_HCED_HOLD_IDS
        or WAVE7_GLOBAL_HCED_CONTRACT_IDS & WAVE7_GLOBAL_MIGRATION_CANDIDATE_IDS
        or WAVE7_GLOBAL_HCED_HOLD_IDS & WAVE7_GLOBAL_MIGRATION_CANDIDATE_IDS
    ):
        raise ValueError("Wave 7 Global promotion, hold, and migration rows overlap")
    if _audit_signature() != WAVE7_GLOBAL_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 7 Global final audit signature changed")

    source_ids = {str(source["id"]) for source in WAVE7_GLOBAL_SOURCES}
    entity_ids = {str(entity["id"]) for entity in WAVE7_GLOBAL_ENTITIES}
    if len(source_ids) != len(WAVE7_GLOBAL_SOURCES):
        raise ValueError("Wave 7 Global source IDs must be unique")
    if len(entity_ids) != len(WAVE7_GLOBAL_ENTITIES):
        raise ValueError("Wave 7 Global entity IDs must be unique")
    allowed_evidence = source_ids | _EXISTING_EVIDENCE_SOURCE_IDS

    reviewed: list[Mapping[str, Any]] = [
        *WAVE7_GLOBAL_HCED_CONTRACTS.values(),
        *WAVE7_GLOBAL_HCED_HOLDS.values(),
        *WAVE7_GLOBAL_ORANGE_MIGRATIONS.values(),
    ]
    raw_hashes: list[str] = []
    for contract in reviewed:
        if canonical_hced_row_sha256(contract["raw_row"]) != contract["raw_row_sha256"]:
            raise ValueError("Wave 7 Global embedded HCED row fingerprint changed")
        raw_hashes.append(str(contract["raw_row_sha256"]))
        if not set(map(str, contract["evidence_refs"])) <= allowed_evidence:
            raise ValueError("Wave 7 Global contract names an unknown evidence source")
    if len(raw_hashes) != len(set(raw_hashes)):
        raise ValueError("Wave 7 Global reviewed HCED raw-row hashes must be unique")

    for candidate_id, contract in {
        **WAVE7_GLOBAL_HCED_CONTRACTS,
        **WAVE7_GLOBAL_HCED_HOLDS,
    }.items():
        if contract["raw_row"].get("candidate_id") != candidate_id:
            raise ValueError("Wave 7 Global embedded candidate ID drift")

    migration_candidate_ids: list[str] = []
    for event_id, migration in WAVE7_GLOBAL_ORANGE_MIGRATIONS.items():
        if migration["event_id"] != event_id:
            raise ValueError("Wave 7 Global Orange event ID drift")
        if migration["raw_row"].get("candidate_id") != migration["candidate_id"]:
            raise ValueError("Wave 7 Global Orange candidate ID drift")
        if migration["from_entity_id"] != _ORANGE_OLD_ENTITY_ID:
            raise ValueError("Wave 7 Global Orange source identity drift")
        if migration["to_entity_id"] != _ORANGE_NEW_ENTITY_ID:
            raise ValueError("Wave 7 Global Orange target identity drift")
        if (
            len(str(migration["migrated_event_sha256"])) != 64
            or migration["migrated_event_sha256"] == migration["source_event_sha256"]
        ):
            raise ValueError("Wave 7 Global Orange migrated-event hash drift")
        migration_candidate_ids.append(str(migration["candidate_id"]))
    if len(migration_candidate_ids) != len(set(migration_candidate_ids)):
        raise ValueError("Wave 7 Global Orange candidate IDs must be unique")

    for entity in WAVE7_GLOBAL_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(
                f"Wave 7 Global entity {entity['id']} must be alias-free and non-inheriting"
            )
        if "no rating" not in str(entity["continuity_note"]).casefold():
            raise ValueError(
                f"Wave 7 Global entity {entity['id']} must state its rating reset"
            )
        if not set(map(str, entity["source_ids"])) <= source_ids:
            raise ValueError(
                f"Wave 7 Global entity {entity['id']} names an unknown source"
            )

    egypt_entities = {
        str(entity["id"]): entity
        for entity in WAVE7_GLOBAL_ENTITIES
        if str(entity["region"]) == "North Africa"
    }
    for entity in egypt_entities.values():
        if any(normalize_label(alias) == "egypt" for alias in entity["aliases"]):
            raise ValueError("Wave 7 Global must never add a cross-era Egypt alias")

    if set(WAVE7_GLOBAL_SUPERSESSIONS) != {"cliopatria-613", "cliopatria-661"}:
        raise ValueError("Wave 7 Global supersession inventory changed")
    for candidate_id, contract in WAVE7_GLOBAL_SUPERSESSIONS.items():
        if contract["raw_candidate"].get("candidate_id") != candidate_id:
            raise ValueError("Wave 7 Global supersession candidate ID drift")
        if (
            canonical_cliopatria_supersession_sha256(contract["raw_candidate"])
            != contract["raw_candidate_sha256"]
        ):
            raise ValueError("Wave 7 Global supersession fingerprint changed")


def validate_wave7_global_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate the entire 47-row promotion/hold/migration inventory."""

    _validate_fixture_inventory()
    rows_by_id = _rows_by_candidate_id(hced_rows)
    _validate_exact_hced_rows(
        rows_by_id,
        WAVE7_GLOBAL_HCED_CONTRACTS,
        description="promotion contract",
    )
    _validate_exact_hced_rows(
        rows_by_id,
        WAVE7_GLOBAL_HCED_HOLDS,
        description="hold contract",
    )
    migration_contracts = {
        str(spec["candidate_id"]): spec
        for spec in WAVE7_GLOBAL_ORANGE_MIGRATIONS.values()
    }
    _validate_exact_hced_rows(
        rows_by_id,
        migration_contracts,
        description="migration contract",
    )
    return {
        "new_event_contracts": 37,
        "holds": 5,
        "identity_migrations": 5,
        "reviewed_hced_rows": 47,
    }


def validate_wave7_global_supersession_candidates(
    cliopatria_rows: list[dict[str, Any]],
) -> dict[str, tuple[str, ...]]:
    """Fingerprint the two raw identities replaced by exact reviewed boundaries."""

    _validate_fixture_inventory()
    rows_by_id = _rows_by_candidate_id(cliopatria_rows)
    result: dict[str, tuple[str, ...]] = {}
    for candidate_id, contract in WAVE7_GLOBAL_SUPERSESSIONS.items():
        rows = rows_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"Wave 7 Global supersession {candidate_id} expected exactly one "
                f"queue row, found {len(rows)}"
            )
        actual = canonical_cliopatria_supersession_sha256(rows[0])
        expected = str(contract["raw_candidate_sha256"])
        if actual != expected:
            raise ValueError(
                f"Wave 7 Global supersession {candidate_id} fingerprint changed "
                f"({actual} != {expected})"
            )
        result[candidate_id] = tuple(map(str, contract["replacement_entity_ids"]))
    return result


def install_wave7_global_sources(sources_by_id: dict[str, dict[str, Any]]) -> None:
    _validate_fixture_inventory()
    for fixture in WAVE7_GLOBAL_SOURCES:
        source = copy.deepcopy(fixture)
        source_id = str(source["id"])
        existing = sources_by_id.get(source_id)
        if existing is not None and existing != source:
            raise ValueError(f"Wave 7 Global source ID collision for {source_id}")
        sources_by_id[source_id] = source


def install_wave7_global_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_fixture_inventory()
    for fixture in WAVE7_GLOBAL_ENTITIES:
        entity = copy.deepcopy(fixture)
        entity_id = str(entity["id"])
        existing = release_entities.get(entity_id)
        if existing is not None and existing != entity:
            raise ValueError(f"Wave 7 Global entity ID collision for {entity_id}")
        release_entities[entity_id] = entity


def _entity_covers(entity: Mapping[str, Any], low_year: int, high_year: int) -> bool:
    start_year = entity.get("start_year")
    end_year = entity.get("end_year")
    return (
        start_year is not None
        and int(start_year) <= low_year
        and (end_year is None or int(end_year) >= high_year)
    )


def promote_wave7_global_hced_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Promote only the 37 exact new-event contracts; no label fallback is used."""

    _validate_fixture_inventory()
    rows_by_id = _rows_by_candidate_id(hced_rows)
    _validate_exact_hced_rows(
        rows_by_id,
        WAVE7_GLOBAL_HCED_CONTRACTS,
        description="promotion contract",
    )
    existing_event_rows = list(existing_events)
    existing_candidate_ids = {
        str(event["hced_candidate_id"])
        for event in existing_event_rows
        if event.get("hced_candidate_id") is not None
    }
    collisions = sorted(existing_candidate_ids & WAVE7_GLOBAL_HCED_CONTRACT_IDS)
    if collisions:
        raise ValueError(f"Wave 7 Global HCED candidate already promoted: {collisions}")
    existing_keys = {
        _event_key(str(event["name"]), int(event["year"]))
        for event in existing_event_rows
    }

    promoted: list[dict[str, Any]] = []
    accepted_keys: set[tuple[str, int]] = set()
    ordered_contracts = sorted(
        WAVE7_GLOBAL_HCED_CONTRACTS.items(),
        key=lambda item: (
            int(item[1]["canonical_event"]["year_low"]),
            item[0],
        ),
    )
    for candidate_id, contract in ordered_contracts:
        candidate = rows_by_id[candidate_id][0]
        if hced_candidate_id(candidate) != candidate_id:
            raise ValueError(
                f"Wave 7 Global HCED candidate ID changed for {candidate_id}"
            )
        canonical = contract["canonical_event"]
        low_year = int(canonical["year_low"])
        high_year = int(canonical["year_high"])
        if (low_year, high_year) != (
            int(candidate["year_low"]),
            int(candidate["year_high"]),
        ):
            raise ValueError(f"Wave 7 Global canonical date drift for {candidate_id}")

        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"Wave 7 Global invalid opposing sides for {candidate_id}")
        for entity_id in (*side_1, *side_2):
            entity = release_entities.get(entity_id)
            if entity is None or not _entity_covers(entity, low_year, high_year):
                raise ValueError(
                    f"Wave 7 Global entity-window violation for {candidate_id}: "
                    f"{entity_id}"
                )

        winner_index = int(contract["result"]["winner_side"])
        if winner_index not in {1, 2}:
            raise ValueError(f"Wave 7 Global invalid winner side for {candidate_id}")
        winner_label = candidate[f"side_{winner_index}_raw"]
        loser_label = candidate[f"side_{3 - winner_index}_raw"]
        if (
            candidate.get("winner_raw") != winner_label
            or candidate.get("loser_raw") != loser_label
        ):
            raise ValueError(f"Wave 7 Global outcome/side drift for {candidate_id}")
        winner_side, loser_side = (
            (side_1, side_2) if winner_index == 1 else (side_2, side_1)
        )

        event_name = str(canonical["name"])
        event_key = _event_key(event_name, low_year)
        raw_event_key = _event_key(str(candidate["name"]), low_year)
        if event_key in existing_keys or raw_event_key in existing_keys:
            raise ValueError(
                f"Wave 7 Global source-family duplicate for {candidate_id}"
            )
        if event_key in accepted_keys:
            raise ValueError(
                f"Wave 7 Global duplicate canonical key for {candidate_id}"
            )
        accepted_keys.add(event_key)

        scale, scale_level = _scale(candidate)
        confidence = round(0.80 - (0.03 if low_year != high_year else 0.0), 2)
        war_names = list(map(str, candidate.get("war_names", [])))
        cluster = _slug(war_names[0]) if war_names else None
        raw_name = str(candidate["name"])
        source_ids = ["hced_dataset", *map(str, contract["evidence_refs"])]
        location_fields = build_hced_location_fields(
            candidate,
            point_quarantine_ids=HCED_POINT_QUARANTINE_IDS,
            country_quarantine_ids=HCED_COUNTRY_QUARANTINE_IDS,
        )
        promoted.append(
            {
                "id": f"hced_wave7_global_{_slug(candidate_id, 80)}",
                "name": event_name,
                "year": low_year,
                "end_year": high_year,
                "event_type": "engagement",
                "war_type": "interstate_limited",
                "scale": scale,
                "stakes": "major" if scale_level >= 4 else "limited",
                "decisiveness": round(min(0.90, 0.54 + 0.06 * scale_level), 2),
                "confidence": confidence,
                "geographic_scope": round(min(0.70, 0.08 + 0.09 * scale_level), 2),
                "domain": _domain(candidate.get("theatre_raw")),
                "cluster_id": f"hced_war_{cluster}" if cluster else None,
                "date_precision": "year",
                "sequence": int(candidate.get("source_row") or 0),
                "summary": (
                    "Candidate-keyed reviewed HCED tactical assertion. The exact source "
                    "row, participant identities, dates, and duplicate status are pinned "
                    "by the Wave 7 Global contract; the historical references support "
                    "identity boundaries and context, not an independently re-coded "
                    "outcome. No enclosing war result is inferred."
                ),
                "aliases": [raw_name] if raw_name != event_name else [],
                "participants": _participants(
                    winner_side,
                    loser_side,
                    False,
                    confidence,
                    scale_level,
                    note=(
                        "Candidate-keyed Wave 7 Global HCED tactical assertion; no label "
                        "fallback or strategic war outcome is inferred."
                    ),
                ),
                "source_ids": source_ids,
                "outcome_source_ids": ["hced_dataset"],
                "outcome_source_family_ids": ["hced"],
                "hced_candidate_id": candidate_id,
                "reviewed_granularity": str(canonical["granularity"]),
                "canonical_event_key": str(canonical["canonical_key"]),
                "identity_resolution": "candidate_keyed_exact",
                "status": "complete",
                **location_fields,
            }
        )

    if len(promoted) != 37:
        raise ValueError(f"Wave 7 Global promoted {len(promoted)} rows instead of 37")
    return promoted


def migrate_wave7_global_orange_events(
    hced_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Atomically replace the old Orange identity in exactly five rated events.

    The input is never mutated. Every candidate row and every complete source event is
    validated before any replacement is constructed or returned.
    """

    _validate_fixture_inventory()
    rows_by_id = _rows_by_candidate_id(hced_rows)
    migration_contracts = {
        str(spec["candidate_id"]): spec
        for spec in WAVE7_GLOBAL_ORANGE_MIGRATIONS.values()
    }
    _validate_exact_hced_rows(
        rows_by_id,
        migration_contracts,
        description="migration contract",
    )

    original = list(existing_events)
    by_event_id: dict[str, list[Mapping[str, Any]]] = {}
    for event in original:
        event_id = event.get("id")
        if isinstance(event_id, str):
            by_event_id.setdefault(event_id, []).append(event)

    validated: dict[str, Mapping[str, Any]] = {}
    states: set[str] = set()
    for event_id, spec in WAVE7_GLOBAL_ORANGE_MIGRATIONS.items():
        matches = by_event_id.get(event_id, [])
        if len(matches) != 1:
            raise ValueError(
                f"Wave 7 Global Orange migration {event_id} expected exactly one "
                f"event, found {len(matches)}"
            )
        event = matches[0]
        if event.get("hced_candidate_id") != spec["candidate_id"]:
            raise ValueError(
                f"Wave 7 Global Orange migration candidate drift for {event_id}"
            )
        actual_hash = canonical_event_sha256(event)
        source_hash = str(spec["source_event_sha256"])
        migrated_hash = str(spec["migrated_event_sha256"])
        if actual_hash == source_hash:
            state = "source"
            expected_entity_id = _ORANGE_OLD_ENTITY_ID
        elif actual_hash == migrated_hash:
            state = "migrated"
            expected_entity_id = _ORANGE_NEW_ENTITY_ID
        else:
            raise ValueError(
                f"Wave 7 Global Orange migration event fingerprint changed for "
                f"{event_id} ({actual_hash} matches neither {source_hash} nor "
                f"{migrated_hash})"
            )
        participants = event.get("participants")
        expected_count = (
            sum(
                participant.get("entity_id") == expected_entity_id
                for participant in participants
                if isinstance(participant, Mapping)
            )
            if isinstance(participants, list)
            else 0
        )
        if expected_count != 1:
            raise ValueError(
                f"Wave 7 Global Orange migration {event_id} expected exactly one "
                f"{state}-identity participant"
            )
        states.add(state)
        validated[event_id] = event

    if len(states) != 1:
        raise ValueError(
            "Wave 7 Global Orange migration cannot mix source and migrated events"
        )
    if states == {"migrated"}:
        return [copy.deepcopy(dict(event)) for event in original]

    replacements: dict[str, dict[str, Any]] = {}
    for event_id, event in validated.items():
        spec = WAVE7_GLOBAL_ORANGE_MIGRATIONS[event_id]
        replacement = copy.deepcopy(dict(event))
        migrated_side: str | None = None
        for participant in replacement["participants"]:
            if participant.get("entity_id") == _ORANGE_OLD_ENTITY_ID:
                participant["entity_id"] = _ORANGE_NEW_ENTITY_ID
                migrated_side = str(participant["side"])
        if migrated_side is None:
            raise ValueError(f"Wave 7 Global Orange migration failed for {event_id}")
        replacement["identity_resolution"] = "wave7_candidate_keyed_migration"
        side_resolution = dict(replacement.get("side_identity_resolution", {}))
        side_resolution[migrated_side] = "wave7_candidate_keyed_exact"
        replacement["side_identity_resolution"] = side_resolution
        replacement["source_ids"] = list(
            dict.fromkeys(
                [
                    *map(str, replacement.get("source_ids", [])),
                    *map(str, spec["evidence_refs"]),
                ]
            )
        )
        replacement["summary"] = (
            str(replacement.get("summary", ""))
            + " Wave 7 atomically migrated the fingerprinted Orange Free State "
            "participant to the reviewed 1854–1902 identity; tactical outcome fields "
            "are unchanged."
        ).strip()
        replacement["identity_migration"] = {
            "candidate_id": str(spec["candidate_id"]),
            "from_entity_id": _ORANGE_OLD_ENTITY_ID,
            "source_event_sha256": str(spec["source_event_sha256"]),
            "to_entity_id": _ORANGE_NEW_ENTITY_ID,
            "wave": "wave7_global",
        }
        if canonical_event_sha256(replacement) != spec["migrated_event_sha256"]:
            raise ValueError(
                f"Wave 7 Global Orange migrated event drift for {event_id}"
            )
        replacements[event_id] = replacement

    return [
        replacements.get(str(event.get("id")), copy.deepcopy(dict(event)))
        for event in original
    ]


def wave7_global_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE7_GLOBAL_HCED_CONTRACTS.values()
            ).items()
        )
    )
