"""Exact Wave 8 contracts for the Dahomey and Ndebele state lanes."""

from __future__ import annotations

import copy
import hashlib
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _domain, _event_key, _participants, _scale, _slug
from .hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
    build_hced_location_fields,
    hced_candidate_id,
)
from .wave7_global import canonical_hced_row_sha256


WAVE8_AFRICAN_STATES_FINAL_AUDIT_SIGNATURE = (
    "6a4cd9eb970c17fe0e121b3904242ec5de63c29e53e5c7e0c27a42cc0d8f544e"
)

WAVE8_AFRICAN_STATES_SOURCES: tuple[dict[str, Any], ...] = (
    {
        "id": "fr_shd_dahomey_1890_1894",
        "title": "The conquest of Dahomey (1890–1894)",
        "url": "https://www.servicehistorique.sga.defense.gouv.fr/en/thematic-topics/conquest-dahomey-1890-1894",
        "publisher": "Service historique de la Défense",
        "license": "linked_reference",
        "source_type": "official_history",
        "accessed": "2026-07-16",
        "source_family_id": "french_defence_historical_service",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "nam_lobengula_ndebele",
        "title": "Lobengula's daughter, 1890 (c)",
        "url": "https://collection.nam.ac.uk/detail.php?acc=2016-10-4--4",
        "publisher": "National Army Museum",
        "license": "linked_reference",
        "source_type": "museum_collection",
        "accessed": "2026-07-16",
        "source_family_id": "national_army_museum",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "nam_bsac_matabeleland_1893",
        "title": "British South Africa Company's Medal 1890–97, Matabeleland 1893",
        "url": "https://collection.nam.ac.uk/detail.php?acc=1958-11-97-9",
        "publisher": "National Army Museum",
        "license": "linked_reference",
        "source_type": "museum_collection",
        "accessed": "2026-07-16",
        "source_family_id": "national_army_museum",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
    {
        "id": "zimluanda_colonialism_1893",
        "title": "Colonialism: the 1893 Anglo-Ndebele War",
        "url": "https://www.zimluanda.gov.zw/?page_id=23091",
        "publisher": "City of Luanda, Zimbabwe",
        "license": "linked_reference",
        "source_type": "government_history",
        "accessed": "2026-07-16",
        "source_family_id": "zimbabwe_local_government_history",
        "evidence_roles": ["identity_boundary_or_context_reference"],
    },
)

WAVE8_AFRICAN_STATES_ENTITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "dahomey_kingdom_behanzin",
        "name": "Kingdom of Dahomey under Béhanzin",
        "kind": "kingdom",
        "start_year": 1889,
        "end_year": 1894,
        "region": "West Africa",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Béhanzin's independent reign and armed resistance to French conquest, "
            "bounded 1889–1894. No rating is inherited from earlier Dahomean reigns "
            "or the later French-controlled kingdom and colony."
        ),
        "source_ids": ["fr_shd_dahomey_1890_1894"],
    },
    {
        "id": "ndebele_kingdom_lobengula",
        "name": "Ndebele Kingdom under Lobengula",
        "kind": "kingdom",
        "start_year": 1870,
        "end_year": 1894,
        "region": "Southern Africa",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "The Ndebele kingdom under its second and last king, Lobengula, through "
            "the 1893–1894 conquest. No rating is inherited by later Ndebele "
            "resistance movements or modern namesakes."
        ),
        "source_ids": ["nam_lobengula_ndebele", "zimluanda_colonialism_1893"],
    },
    {
        "id": "british_south_africa_company_forces_1893",
        "name": "British South Africa Company forces (1893 Matabele campaign)",
        "kind": "chartered_company_force",
        "start_year": 1893,
        "end_year": 1894,
        "region": "Southern Africa",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            "Candidate-keyed identity for the company police and settler columns in "
            "the First Matabele War. The HCED label 'United Kingdom' is not treated "
            "as proof that the British state army was the tactical belligerent. No "
            "rating is inherited by Britain, Rhodesia, or later company forces."
        ),
        "source_ids": ["nam_bsac_matabeleland_1893", "zimluanda_colonialism_1893"],
    },
)


def _canonical(name: str, year: int) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": "year",
        "granularity": "engagement",
        "name": name,
        "year_low": year,
        "year_high": year,
    }


_DAHOMEY_HASHES = {
    "hced-Abomey1892-1": "61835ec58063878777a454afef1eb3f3b57ef9a3df31e3c78af4cb8c5b8fac85",
    "hced-Acheribe1893-1": "073adc96af5177cfc277b6f25e620c14bffebbc51ae54165398b953dd48a7d68",
    "hced-Atchoupa1890-1": "7caa4c6845d7d2496b2d1e8dfb0e8658addb7df845284f01ce2d5ac720628562",
    "hced-Cotonou1890-1": "4dd2e8771fdadc21af4f2bee2c74eb2160b1f2312b61f20d7aaae25addcf2996",
    "hced-Dogba1892-1": "4bad69cdee33315049715e42c97f7b25b0b53c01cfa2b91bada79c4096c7005a",
}
_NDEBELE_HASHES = {
    "hced-Bembesi1893-1": "ed0e4e620fdad1fa2aadbfd0eb21ad7c0ef1e7af0911d851a09ecc314af8bfa3",
    "hced-Empadine1893-1": "879a1a096509fa909aed99a9c6f317886b8c869bccf9a908bccb568c18cbece7",
    "hced-Shangani1893-1": "a75936773e56a563ba1890b0e9ec115e135c836cecbca1b909f52228e2c98bfc",
    "hced-Shangani Incident1893-1": "35dede01fe55c141536db2aed769eed6c4815af98fc0c30935c866ab7fb287e5",
}

_EVENT_NAMES = {
    "hced-Abomey1892-1": ("Abomey", 1892),
    "hced-Acheribe1893-1": ("Acheribe", 1893),
    "hced-Atchoupa1890-1": ("Atchoupa", 1890),
    "hced-Cotonou1890-1": ("Cotonou", 1890),
    "hced-Dogba1892-1": ("Dogba", 1892),
    "hced-Bembesi1893-1": ("Bembesi", 1893),
    "hced-Empadine1893-1": ("Empadine", 1893),
    "hced-Shangani1893-1": ("Shangani", 1893),
    "hced-Shangani Incident1893-1": ("Shangani Incident", 1893),
}

WAVE8_AFRICAN_STATES_CONTRACTS: dict[str, dict[str, Any]] = {}
for _candidate_id, _row_hash in _DAHOMEY_HASHES.items():
    _name, _year = _EVENT_NAMES[_candidate_id]
    _dahomey_is_side_1 = _candidate_id == "hced-Atchoupa1890-1"
    WAVE8_AFRICAN_STATES_CONTRACTS[_candidate_id] = {
        "raw_row_sha256": _row_hash,
        "canonical_event": _canonical(_name, _year),
        "cohort": "dahomey_behanzin",
        "side_1_entity_ids": [
            "dahomey_kingdom_behanzin"
            if _dahomey_is_side_1
            else "french_third_republic"
        ],
        "side_2_entity_ids": [
            "french_third_republic"
            if _dahomey_is_side_1
            else "dahomey_kingdom_behanzin"
        ],
        "winner_side": 1,
        "evidence_refs": ["fr_shd_dahomey_1890_1894"],
        "actor_override": False,
    }

for _candidate_id, _row_hash in _NDEBELE_HASHES.items():
    _name, _year = _EVENT_NAMES[_candidate_id]
    _ndebele_is_side_1 = _candidate_id == "hced-Shangani Incident1893-1"
    WAVE8_AFRICAN_STATES_CONTRACTS[_candidate_id] = {
        "raw_row_sha256": _row_hash,
        "canonical_event": _canonical(_name, _year),
        "cohort": "ndebele_lobengula",
        "side_1_entity_ids": [
            "ndebele_kingdom_lobengula"
            if _ndebele_is_side_1
            else "british_south_africa_company_forces_1893"
        ],
        "side_2_entity_ids": [
            "british_south_africa_company_forces_1893"
            if _ndebele_is_side_1
            else "ndebele_kingdom_lobengula"
        ],
        "winner_side": 1,
        "evidence_refs": [
            "nam_lobengula_ndebele",
            "nam_bsac_matabeleland_1893",
            "zimluanda_colonialism_1893",
        ],
        "actor_override": True,
    }

WAVE8_AFRICAN_STATES_CONTRACT_IDS = frozenset(WAVE8_AFRICAN_STATES_CONTRACTS)
WAVE8_AFRICAN_STATES_RESERVED_IDS = WAVE8_AFRICAN_STATES_CONTRACT_IDS


def _rows_by_id(rows: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        candidate_id = row.get("candidate_id")
        if isinstance(candidate_id, str):
            result.setdefault(candidate_id, []).append(row)
    return result


def _audit_signature() -> str:
    lines = []
    for candidate_id, contract in sorted(WAVE8_AFRICAN_STATES_CONTRACTS.items()):
        lines.append(
            "|".join(
                (
                    candidate_id,
                    str(contract["raw_row_sha256"]),
                    str(contract["canonical_event"]["canonical_key"]),
                    ",".join(map(str, contract["side_1_entity_ids"])),
                    ",".join(map(str, contract["side_2_entity_ids"])),
                )
            )
        )
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


def _validate_inventory() -> None:
    if len(WAVE8_AFRICAN_STATES_CONTRACTS) != 9:
        raise ValueError("Wave 8 African states contract inventory changed")
    if len(WAVE8_AFRICAN_STATES_ENTITIES) != 3:
        raise ValueError("Wave 8 African states entity inventory changed")
    if len(WAVE8_AFRICAN_STATES_SOURCES) != 4:
        raise ValueError("Wave 8 African states source inventory changed")
    if _audit_signature() != WAVE8_AFRICAN_STATES_FINAL_AUDIT_SIGNATURE:
        raise ValueError("Wave 8 African states final audit signature changed")
    source_ids = {str(source["id"]) for source in WAVE8_AFRICAN_STATES_SOURCES}
    entity_ids = {str(entity["id"]) for entity in WAVE8_AFRICAN_STATES_ENTITIES}
    for entity in WAVE8_AFRICAN_STATES_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"Wave 8 entity {entity['id']} must be alias-free")
        if "no rating" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"Wave 8 entity {entity['id']} must declare a reset")
        if not set(map(str, entity["source_ids"])) <= source_ids:
            raise ValueError(f"Wave 8 entity {entity['id']} has an unknown source")
    for contract in WAVE8_AFRICAN_STATES_CONTRACTS.values():
        if not set(map(str, contract["evidence_refs"])) <= source_ids:
            raise ValueError("Wave 8 contract has an unknown evidence source")
        if not (
            set(map(str, contract["side_1_entity_ids"]))
            | set(map(str, contract["side_2_entity_ids"]))
        ) & entity_ids:
            raise ValueError("Wave 8 contract does not use a lane identity")


def validate_wave8_african_states_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    _validate_inventory()
    rows_by_id = _rows_by_id(hced_rows)
    for candidate_id, contract in WAVE8_AFRICAN_STATES_CONTRACTS.items():
        rows = rows_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"Wave 8 African states {candidate_id} expected exactly one row, "
                f"found {len(rows)}"
            )
        actual = canonical_hced_row_sha256(rows[0])
        expected = str(contract["raw_row_sha256"])
        if actual != expected:
            raise ValueError(
                f"Wave 8 African states {candidate_id} raw-row fingerprint changed "
                f"({actual} != {expected})"
            )
    return {"promotion_contracts": 9, "reviewed_hced_rows": 9}


def install_wave8_african_states_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_inventory()
    for fixture in WAVE8_AFRICAN_STATES_SOURCES:
        source = copy.deepcopy(fixture)
        source_id = str(source["id"])
        existing = sources_by_id.get(source_id)
        if existing is not None and existing != source:
            raise ValueError(f"Wave 8 source collision for {source_id}")
        sources_by_id[source_id] = source


def install_wave8_african_states_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_inventory()
    for fixture in WAVE8_AFRICAN_STATES_ENTITIES:
        entity = copy.deepcopy(fixture)
        entity_id = str(entity["id"])
        existing = release_entities.get(entity_id)
        if existing is not None and existing != entity:
            raise ValueError(f"Wave 8 entity collision for {entity_id}")
        release_entities[entity_id] = entity


def _entity_covers(entity: Mapping[str, Any], low: int, high: int) -> bool:
    start = entity.get("start_year")
    end = entity.get("end_year")
    return start is not None and int(start) <= low and (end is None or int(end) >= high)


def promote_wave8_african_states_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_african_states_queue_contracts(hced_rows)
    rows_by_id = _rows_by_id(hced_rows)
    existing = list(existing_events)
    existing_candidates = {
        str(event["hced_candidate_id"])
        for event in existing
        if event.get("hced_candidate_id") is not None
    }
    collisions = sorted(existing_candidates & WAVE8_AFRICAN_STATES_CONTRACT_IDS)
    if collisions:
        raise ValueError(f"Wave 8 candidates already promoted: {collisions}")
    existing_keys = {
        _event_key(str(event["name"]), int(event["year"])) for event in existing
    }
    accepted_keys: set[tuple[str, int]] = set()
    events: list[dict[str, Any]] = []
    for candidate_id, contract in sorted(
        WAVE8_AFRICAN_STATES_CONTRACTS.items(),
        key=lambda item: (int(item[1]["canonical_event"]["year_low"]), item[0]),
    ):
        candidate = rows_by_id[candidate_id][0]
        if hced_candidate_id(candidate) != candidate_id:
            raise ValueError(f"Wave 8 candidate ID drift for {candidate_id}")
        canonical = contract["canonical_event"]
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        if (low, high) != (int(candidate["year_low"]), int(candidate["year_high"])):
            raise ValueError(f"Wave 8 date drift for {candidate_id}")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"Wave 8 invalid sides for {candidate_id}")
        for entity_id in (*side_1, *side_2):
            entity = release_entities.get(entity_id)
            if entity is None or not _entity_covers(entity, low, high):
                raise ValueError(
                    f"Wave 8 entity-window violation for {candidate_id}: {entity_id}"
                )
        winner_side = int(contract["winner_side"])
        if candidate.get("winner_raw") != candidate.get(f"side_{winner_side}_raw"):
            raise ValueError(f"Wave 8 outcome drift for {candidate_id}")
        loser_side = 3 - winner_side
        if candidate.get("loser_raw") != candidate.get(f"side_{loser_side}_raw"):
            raise ValueError(f"Wave 8 loser drift for {candidate_id}")
        winners, losers = (side_1, side_2) if winner_side == 1 else (side_2, side_1)
        name = str(canonical["name"])
        key = _event_key(name, low)
        raw_key = _event_key(str(candidate["name"]), low)
        if key in existing_keys or raw_key in existing_keys or key in accepted_keys:
            raise ValueError(f"Wave 8 duplicate event for {candidate_id}")
        accepted_keys.add(key)
        scale, scale_level = _scale(candidate)
        confidence = 0.80
        war_names = list(map(str, candidate.get("war_names", [])))
        cluster = _slug(war_names[0]) if war_names else None
        actor_note = (
            " The source's United Kingdom label is corrected to the exact British "
            "South Africa Company tactical actor."
            if contract["actor_override"]
            else ""
        )
        events.append(
            {
                "id": f"hced_wave8_african_states_{_slug(candidate_id, 80)}",
                "name": name,
                "year": low,
                "end_year": high,
                "event_type": "engagement",
                "war_type": "colonial_anti_colonial",
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
                    "Candidate-keyed Wave 8 HCED tactical assertion. The complete "
                    "source row, participant identities, dates, and disposition are "
                    "pinned; historical references support actor identity and context, "
                    "while HCED remains the outcome source. No strategic result is "
                    f"inferred.{actor_note}"
                ),
                "aliases": [],
                "participants": _participants(
                    winners,
                    losers,
                    False,
                    confidence,
                    scale_level,
                    note=(
                        "Candidate-keyed Wave 8 tactical contract; no label fallback "
                        "or strategic war outcome is inferred."
                    ),
                ),
                "source_ids": ["hced_dataset", *map(str, contract["evidence_refs"])],
                "outcome_source_ids": ["hced_dataset"],
                "outcome_source_family_ids": ["hced"],
                "hced_candidate_id": candidate_id,
                "reviewed_granularity": "engagement",
                "canonical_event_key": str(canonical["canonical_key"]),
                "identity_resolution": "candidate_keyed_exact",
                "status": "complete",
                **build_hced_location_fields(
                    candidate,
                    point_quarantine_ids=HCED_POINT_QUARANTINE_IDS,
                    country_quarantine_ids=HCED_COUNTRY_QUARANTINE_IDS,
                ),
            }
        )
    if len(events) != 9:
        raise ValueError(f"Wave 8 African states promoted {len(events)} rows instead of 9")
    return events


def wave8_african_states_cohort_counts() -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_AFRICAN_STATES_CONTRACTS.values()
            ).items()
        )
    )
