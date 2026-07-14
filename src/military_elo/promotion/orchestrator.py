from __future__ import annotations

"""Deterministic orchestration for the expanded provisional release."""

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .common import (
    _candidate_entity_id,
    _candidate_labels,
    _candidate_overlaps_entity,
    _candidate_policy_seed,
    _count_review_records,
    _cross_source_event_keys,
    _declared_rejections,
    _deduplicate,
    _event_key,
    _infer_kind,
    _resolve_code,
    _resolve_label_tiers,
    _seed_entity_labels,
    _validate_seed_event_intervals,
    _write_json,
    normalize_label,
    read_jsonl,
)
from .hced import (
    promote_hced_crosswalk_rows,
    promote_hced_label_rows,
    resolve_hced_side_label,
)
from .iwd import aggregate_iwd_parent_wars, _seed_war_token_spans
from .iwbd import promote_iwbd_battles
from .policy import (
    HCED_CURATED_EXCLUSIONS,
    HCED_FACTION_LABELS,
    HCED_LABEL_CURATED_EXCLUSIONS,
    HCED_LABEL_POLICIES,
    HCED_LABEL_REJECTION_COUNTERS,
    HCED_PENDING_SPLIT_LABELS,
    IWBD_CURATED_EXCLUSIONS,
    IWBD_REJECTION_COUNTERS,
    IWD_COW_CODE_POLICIES,
    IWD_CURATED_PARENT_EXCLUSIONS,
    SEED_EVENT_INTERVAL_EXEMPTIONS,
    UCDP_ACTOR_PARTY_POLICIES,
    UCDP_CURATED_EXCLUSIONS,
    UCDP_REJECTION_COUNTERS,
    UCDP_WAR_TYPES,
    _cow_policy_seed_id,
)
from .ucdp import promote_ucdp_termination_episodes, resolve_ucdp_party

def build_expanded_release(
    seed_dir: str | Path,
    review_root: str | Path,
    release_dir: str | Path,
    registry_path: str | Path,
) -> dict[str, Any]:
    seed_root = Path(seed_dir)
    review = Path(review_root)
    release = Path(release_dir)
    seed_entities: list[dict[str, Any]] = json.loads(
        (seed_root / "entities.json").read_text(encoding="utf-8")
    )
    seed_events: list[dict[str, Any]] = json.loads(
        (seed_root / "events.json").read_text(encoding="utf-8")
    )
    sources: list[dict[str, Any]] = json.loads(
        (seed_root / "sources.json").read_text(encoding="utf-8")
    )
    seed_metadata: dict[str, Any] = json.loads(
        (seed_root / "metadata.json").read_text(encoding="utf-8")
    )
    seed_by_id = {str(entity["id"]): entity for entity in seed_entities}
    _validate_seed_event_intervals(seed_events, seed_by_id)
    seed_label_index: dict[str, set[str]] = {}
    for entity in seed_entities:
        for label in [entity.get("name"), *entity.get("aliases", [])]:
            normalized = normalize_label(label)
            if normalized:
                seed_label_index.setdefault(normalized, set()).add(str(entity["id"]))

    cliopatria = read_jsonl(review / "cliopatria-entity-candidates.jsonl")
    polities = [row for row in cliopatria if row.get("record_type") == "POLITY"]
    hced = read_jsonl(review / "hced-candidates.jsonl")
    owners: dict[str, list[dict[str, Any]]] = {}
    for candidate in polities:
        for code in candidate.get("seshat_ids", []):
            owners.setdefault(str(code), []).append(candidate)

    release_entities = {str(entity["id"]): dict(entity) for entity in seed_entities}
    candidate_by_release_id: dict[str, dict[str, Any]] = {}
    iwd_events: list[dict[str, Any]] = []
    iwd_rejections: Counter[str] = Counter()
    curated_seed_keys = {
        _event_key(str(event["name"]), int(event["year"])) for event in seed_events
    }

    def ensure_candidate_entity(polity: dict[str, Any]) -> str:
        entity_id = _candidate_entity_id(polity)
        candidate_by_release_id[entity_id] = polity
        if entity_id in release_entities:
            return entity_id
        canonical_name = str(polity["canonical_name_candidate"])
        release_entities[entity_id] = {
            "id": entity_id,
            "name": canonical_name,
            "kind": _infer_kind(canonical_name),
            "start_year": int(polity["start_year"]),
            "end_year": int(polity["end_year"]),
            "region": "Unclassified",
            "aliases": _deduplicate(
                [
                    *map(str, polity.get("aliases", [])),
                    *map(str, polity.get("wikipedia_titles", [])),
                ]
            ),
            "predecessors": [],
            "continuity_note": (
                "Time-bounded Cliopatria interval. Namesakes, predecessors, and successors "
                "receive no inherited rating without an explicit continuity decision."
            ),
            "source_ids": ["cliopatria_v020"],
        }
        return entity_id

    hced_crosswalk_pass = promote_hced_crosswalk_rows(
        hced,
        owners,
        curated_seed_keys,
        ensure_candidate_entity,
    )
    source_events: list[dict[str, Any]] = hced_crosswalk_pass["events"]
    rejections: Counter[str] = hced_crosswalk_pass["rejections"]
    deferred_label_rows: list[dict[str, Any]] = hced_crosswalk_pass[
        "deferred_label_rows"
    ]
    promoted_hced_keys: set[tuple[str, int]] = hced_crosswalk_pass[
        "promoted_event_keys"
    ]
    label_observations: dict[str, list[tuple[int, int, str]]] = hced_crosswalk_pass[
        "label_observations"
    ]
    hced_cluster_spans: dict[str, list[Any]] = hced_crosswalk_pass["cluster_spans"]

    polity_alias_index: dict[str, list[dict[str, Any]]] = {}
    for polity in polities:
        labels = _deduplicate(
            [
                str(polity.get("canonical_name_candidate") or ""),
                *map(str, polity.get("aliases", [])),
                *map(str, polity.get("wikipedia_titles", [])),
            ]
        )
        for label in labels:
            normalized = normalize_label(label)
            if normalized:
                polity_alias_index.setdefault(normalized, []).append(polity)

    # Own-label sets per entity, used by the observation-coherence guard in the
    # HCED label pass (the IWD path keeps the tier unguarded so the committed
    # IWD promotion stays pinned).
    entity_labels: dict[str, set[str]] = {
        str(entity["id"]): _seed_entity_labels(entity) for entity in seed_entities
    }
    for polity in polities:
        entity_labels.setdefault(_candidate_entity_id(polity), set()).update(
            _candidate_labels(polity)
        )

    label_context: dict[str, Any] = {
        "seed_entities": seed_entities,
        "seed_by_id": seed_by_id,
        "seed_label_index": seed_label_index,
        "label_observations": label_observations,
        "release_entities": release_entities,
        "entity_labels": entity_labels,
        "polity_alias_index": polity_alias_index,
    }

    def resolve_iwd_label(
        label: str,
        low_year: int,
        high_year: int,
    ) -> tuple[str | None, dict[str, Any] | None]:
        entity_id, polity, _ = _resolve_label_tiers(
            normalize_label(label),
            low_year,
            high_year,
            label_context,
            require_observation_coherence=False,
        )
        return entity_id, polity

    def resolve_iwd_party(
        name: str,
        cow_code: Any,
        low_year: int,
        high_year: int,
    ) -> tuple[str | None, dict[str, Any] | None]:
        code = str(cow_code) if cow_code else ""
        if code in IWD_COW_CODE_POLICIES:
            # An explicit COW-code policy is authoritative: outside its
            # intervals the party stays unresolved instead of falling back to
            # name matching.
            return _cow_policy_seed_id(code, low_year, high_year), None
        return resolve_iwd_label(name, low_year, high_year)

    iwd_path = review / "iwd-1.21-candidates.jsonl"
    iwd_candidates = read_jsonl(iwd_path) if iwd_path.exists() else []
    # IWD component records repeat one umbrella war across many dyads, so they
    # are rated only through parent-war coalition aggregation: at most one
    # strategic update per largerwarid, with every component row retained as
    # provenance. Parents whose sides, outcomes, or identities cannot be
    # reconstructed defensibly stay staged.
    iwd_aggregation = aggregate_iwd_parent_wars(
        iwd_candidates,
        _seed_war_token_spans(seed_events),
        resolve_iwd_party,
        curated_parent_exclusions=IWD_CURATED_PARENT_EXCLUSIONS,
    )
    iwd_events.extend(iwd_aggregation["events"])
    iwd_rejections.update(iwd_aggregation["parent_rejections"])
    for polity in iwd_aggregation["resolved_polities"].values():
        ensure_candidate_entity(polity)

    # Second HCED pass: rows deferred for missing Seshat coding re-enter
    # through the declared label-resolution ruleset. It runs after IWD
    # aggregation so the IWD inputs are identical with or without the label
    # pass, and entities materialize only after every gate has passed.
    hced_label_pass = promote_hced_label_rows(
        deferred_label_rows,
        curated_seed_keys,
        promoted_hced_keys,
        lambda code, low_year, high_year: _resolve_code(code, low_year, high_year, owners),
        lambda label, low_year, high_year: resolve_hced_side_label(
            label, low_year, high_year, label_context
        ),
    )
    label_events: list[dict[str, Any]] = hced_label_pass["events"]
    hced_label_rejections: Counter[str] = hced_label_pass["rejections"]
    for polity in hced_label_pass["resolved_polities"].values():
        ensure_candidate_entity(polity)
    for cluster_id, (tokens, low_year, high_year) in hced_label_pass["cluster_spans"].items():
        span = hced_cluster_spans.setdefault(cluster_id, [tokens, low_year, high_year])
        span[1] = min(span[1], low_year)
        span[2] = max(span[2], high_year)

    # IWBD battles are deduplicated against curated seed events and every
    # non-curated-excluded HCED candidate — promoted or staged, over the
    # candidate's full year range — because a mechanically rejected HCED row
    # may promote later and no event may ever enter the tactical stream twice.
    hced_event_keys: dict[tuple[str, int], dict[str, Any]] = {}

    def hced_index_entry(key: tuple[str, int]) -> dict[str, Any]:
        return hced_event_keys.setdefault(key, {"exact": False, "outcomes": set()})

    for candidate in hced:
        if str(candidate.get("candidate_id")) in {
            *HCED_CURATED_EXCLUSIONS,
            *HCED_LABEL_CURATED_EXCLUSIONS,
        }:
            continue
        name = str(candidate.get("name") or "")
        if not name:
            continue
        year_low = candidate.get("year_low")
        year_high = candidate.get("year_high")
        if year_low is None or year_high is None:
            for year in {
                candidate.get("year_low"),
                candidate.get("year_best"),
                candidate.get("year_high"),
            }:
                if year is not None:
                    hced_index_entry(_event_key(name, int(year)))["exact"] = True
            continue
        for year in range(int(year_low), int(year_high) + 1):
            hced_index_entry(_event_key(name, year))["exact"] = True

    # Fuzzy ordinal/base-name matches require one recognized suffix path to be
    # a strict extension of the other in the same year, with the same resolved
    # sides and outcome orientation. Different suffix branches never share a
    # key. Only promoted HCED rows can supply that identity signature; exact
    # names above continue to block against staged rows.
    for event in (*source_events, *label_events):
        winners = frozenset(
            str(participant["entity_id"])
            for participant in event["participants"]
            if "victory" in str(participant.get("termination", ""))
        )
        losers = frozenset(
            str(participant["entity_id"])
            for participant in event["participants"]
            if "defeat" in str(participant.get("termination", ""))
        )
        if winners or losers:
            outcome_signature = (winners, losers)
        else:
            outcome_signature = (
                frozenset(str(p["entity_id"]) for p in event["participants"]),
                frozenset(),
            )
        for year in range(int(event["year"]), int(event["end_year"]) + 1):
            for key in _cross_source_event_keys(str(event["name"]), year):
                hced_index_entry(key)["outcomes"].add(outcome_signature)

    iwbd_path = review / "iwbd-candidates.jsonl"
    iwbd_candidates = read_jsonl(iwbd_path) if iwbd_path.exists() else []
    iwd_parent_ids = {
        str(candidate.get("parent_war_id"))
        for candidate in iwd_candidates
        if candidate.get("parent_war_id") is not None
    }
    iwbd_promotion = promote_iwbd_battles(
        iwbd_candidates,
        curated_seed_keys,
        hced_event_keys,
        resolve_iwd_label,
        hced_cluster_spans,
        iwd_parent_ids,
    )
    iwbd_events: list[dict[str, Any]] = iwbd_promotion["events"]
    iwbd_rejections: Counter[str] = iwbd_promotion["rejections"]
    for polity in iwbd_promotion["resolved_polities"].values():
        ensure_candidate_entity(polity)

    # UCDP conflict-termination episodes: the strategic-layer promotion path.
    # The promoted-war index (curated seed wars plus IWD parents) drives the
    # entity-and-year duplicate gate so an episode already represented in the
    # ledger is never rated twice.
    ucdp_conflict_path = review / "ucdp-termination-conflict-candidates.jsonl"
    ucdp_dyad_path = review / "ucdp-termination-dyad-candidates.jsonl"
    ucdp_conflict_rows = read_jsonl(ucdp_conflict_path) if ucdp_conflict_path.exists() else []
    ucdp_dyad_rows = read_jsonl(ucdp_dyad_path) if ucdp_dyad_path.exists() else []
    promoted_war_index = [
        (
            str(event["id"]),
            event.get("cluster_id"),
            int(event["year"]),
            int(event.get("end_year", event["year"])),
            frozenset(
                str(participant["entity_id"]) for participant in event["participants"]
            ),
            {
                str(participant["entity_id"]): str(participant.get("termination", ""))
                for participant in event["participants"]
            },
        )
        for event in (*seed_events, *iwd_events)
        if event.get("event_type") == "war"
    ]
    ucdp_promotion = promote_ucdp_termination_episodes(
        ucdp_conflict_rows,
        ucdp_dyad_rows,
        promoted_war_index,
        lambda name, gwno, low_year, high_year: resolve_ucdp_party(
            name, gwno, low_year, high_year, label_context
        ),
    )
    ucdp_events: list[dict[str, Any]] = ucdp_promotion["events"]
    ucdp_rejections: Counter[str] = ucdp_promotion["rejections"]
    for polity in ucdp_promotion["resolved_polities"].values():
        ensure_candidate_entity(polity)

    sources_by_id = {str(source["id"]): source for source in sources}
    for source in (
        {
            "id": "hced_dataset",
            "title": "Historical Conflict Event Dataset (HCED), version 5.0 / data v3",
            "url": "https://doi.org/10.7910/DVN/6ZFC0V",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
            "source_family_id": "hced",
            "evidence_roles": ["outcome"],
        },
        {
            "id": "hced_seshat_crosswalk",
            "title": "HCED-to-Seshat polity crosswalk",
            "url": "https://dataverse.harvard.edu/api/access/datafile/11018172?format=original",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "identity_crosswalk",
            "accessed": "2026-07-13",
            "source_family_id": "hced_seshat_crosswalk_file_11018172",
            "evidence_roles": ["identity_crosswalk"],
        },
        {
            "id": "cliopatria_v020",
            "title": "Cliopatria historical polity registry v0.2.0",
            "url": "https://doi.org/10.5281/zenodo.20274630",
            "publisher": "Seshat Global History Databank / Zenodo",
            "license": "CC-BY-4.0",
            "source_type": "historical_polity_registry",
            "accessed": "2026-07-13",
            "source_family_id": "cliopatria_v0_2_0",
            "evidence_roles": ["identity_registry"],
        },
        {
            "id": "iwd_dataset",
            "title": "Interstate War Data v1.21",
            "url": "https://doi.org/10.7910/DVN/WGS1YX",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
            "source_family_id": "iwd",
            "evidence_roles": ["outcome"],
        },
        {
            "id": "iwbd_dataset",
            "title": "Interstate War Battle dataset (IWBD)",
            "url": "https://dataverse.harvard.edu/api/access/datafile/4435240?format=original",
            "publisher": "Harvard Dataverse",
            "license": "CC0-1.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
            "source_family_id": "iwbd",
            "evidence_roles": ["outcome"],
        },
        {
            "id": "ucdp_termination_conflict",
            "title": "UCDP Conflict Termination Dataset v4-2024, conflict level",
            "url": "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Conflict.csv",
            "publisher": "Uppsala Conflict Data Program",
            "license": "CC-BY-4.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
            "source_family_id": "ucdp_conflict_termination",
            "evidence_roles": ["outcome"],
        },
        {
            "id": "ucdp_termination_dyad",
            "title": "UCDP Conflict Termination Dataset v4-2024, dyad level",
            "url": "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Dyad.csv",
            "publisher": "Uppsala Conflict Data Program",
            "license": "CC-BY-4.0",
            "source_type": "structured_dataset",
            "accessed": "2026-07-13",
            "source_family_id": "ucdp_conflict_termination",
            "evidence_roles": ["outcome_consistency_crosscheck"],
        },
    ):
        sources_by_id[source["id"]] = source

    all_events = [
        *seed_events,
        *source_events,
        *iwd_events,
        *label_events,
        *iwbd_events,
        *ucdp_events,
    ]
    used_entity_ids = {
        str(participant["entity_id"])
        for event in all_events
        for participant in event["participants"]
    }
    release_entity_rows = sorted(
        release_entities.values(),
        key=lambda entity: (int(entity["start_year"]), str(entity["name"]), str(entity["id"])),
    )
    review_counts = _count_review_records(review)

    registry_entities: dict[str, dict[str, Any]] = {
        str(entity["id"]): {
            "id": str(entity["id"]),
            "name": str(entity["name"]),
            "kind": str(entity.get("kind") or "polity"),
            "start_year": int(entity["start_year"]),
            "end_year": int(entity["end_year"]) if entity.get("end_year") is not None else None,
            "status": "rated" if str(entity["id"]) in used_entity_ids else "unrated",
            "identity_status": "curated",
            "region": str(entity.get("region") or "Unclassified"),
        }
        for entity in seed_entities
    }
    used_candidate_ids = {
        str(candidate["candidate_id"]) for candidate in candidate_by_release_id.values()
    }
    for candidate in polities:
        mapped_seed = _candidate_policy_seed(candidate, seed_by_id)
        if not mapped_seed:
            name_matches = seed_label_index.get(
                normalize_label(candidate.get("canonical_name_candidate")), set()
            )
            if len(name_matches) == 1:
                named_seed = next(iter(name_matches))
                named_entity = seed_by_id.get(named_seed)
                # A name match alone must not bridge eras: a same-named polity
                # from a different century keeps its own registry row.
                if named_entity and _candidate_overlaps_entity(candidate, named_entity):
                    mapped_seed = named_seed
        if mapped_seed and mapped_seed in registry_entities:
            continue
        entity_id = _candidate_entity_id(candidate)
        registry_entities[entity_id] = {
            "id": entity_id,
            "name": str(candidate["canonical_name_candidate"]),
            "kind": _infer_kind(str(candidate["canonical_name_candidate"])),
            "start_year": int(candidate["start_year"]),
            "end_year": int(candidate["end_year"]),
            "status": (
                "provisional"
                if str(candidate["candidate_id"]) in used_candidate_ids
                else "unrated"
            ),
            "identity_status": "source_candidate",
            "coverage_discontinuous": len(
                candidate.get("temporal_coverage_groups", [])
            ) > 1,
            "region": "Unclassified",
        }

    registry_rows = sorted(
        registry_entities.values(),
        key=lambda entity: (str(entity["name"]), int(entity["start_year"]), str(entity["id"])),
    )
    staged_source_records = sum(review_counts.values())
    identity_queue_names = {
        "cliopatria-entity-candidates.jsonl",
        "ucdp-actor-26.1-candidates.jsonl",
    }
    unresolved_event_candidates = max(
        0,
        sum(
            count
            for name, count in review_counts.items()
            if name not in identity_queue_names
        )
        - len(source_events)
        - len(label_events)
        - len(iwbd_events)
        - len(ucdp_events)
        - iwd_aggregation["components_attached"],
    )
    latest_rated_event_year = max(int(event["end_year"]) for event in all_events)
    coverage = {
        "registry_polities": len(registry_rows),
        "rated_entities": len(used_entity_ids),
        "rated_events": len(all_events),
        "staged_source_records": staged_source_records,
        "unresolved_event_candidates": unresolved_event_candidates,
        "latest_rated_event_year": latest_rated_event_year,
        "curated_seed_events": len(seed_events),
        "provisional_hced_events": len(source_events),
        "provisional_hced_label_events": len(label_events),
        "provisional_iwd_wars": len(iwd_events),
        "provisional_iwbd_battles": len(iwbd_events),
        "iwbd_battles_total": iwbd_promotion["battles_total"],
        "provisional_ucdp_events": len(ucdp_events),
        "ucdp_termination_rows_total": ucdp_promotion["rows_total"],
        "iwd_parent_wars_total": iwd_aggregation["parents_total"],
        "iwd_component_records": iwd_aggregation["components_total"],
        "iwd_components_aggregated": iwd_aggregation["components_aggregated"],
        "source_queue_counts": review_counts,
    }
    registry = {"entities": registry_rows, "coverage": coverage}

    metadata = {
        **seed_metadata,
        "dataset_id": "military-elo-expanded-provisional-v0.2",
        "title": "Expanded provisional Military History Elo evidence release",
        "version": "0.2.0",
        "coverage_status": "expanded_provisional",
        "comprehensive": False,
        "description": (
            "The curated seed plus source-derived tactical tranches (crosswalk-resolved and "
            "label-resolved HCED engagements, deduplicated IWBD battles) and strategic "
            "tranches (aggregated IWD coalition wars, UCDP terminal-victory episodes). "
            "The separate registry publishes time-bounded Cliopatria polity candidates, "
            "including unrated entries, without assigning them invented Elo results."
        ),
        "coverage_note": (
            "Registry coverage is much broader than rating coverage. Source-derived HCED "
            "and IWBD engagements remain provisional; IWD component wars enter only as one "
            "aggregated coalition update per parent conflict, UCDP termination records only "
            "as conflict-level terminal victory episodes, and unresolved records do not affect Elo. "
            f"The latest rated event ends in {latest_rated_event_year}; later timeline years carry ratings forward."
        ),
        "footer_note": (
            "Known polities, entities with Elo, and staged source records are reported separately. "
            "Absence from the rating ledger is not evidence of military failure."
        ),
        "record_counts_expected": {
            "entities": len(release_entity_rows),
            "events": len(all_events),
            "sources": len(sources_by_id),
            "registry_polities": len(registry_rows),
        },
        "year_range": {
            "start": min(int(event["year"]) for event in all_events),
            "end": max(int(event["end_year"]) for event in all_events),
            "calendar_note": seed_metadata.get("year_range", {}).get("calendar_note", ""),
        },
        "promotion": {
            "policy": (
                "Only nonduplicate HCED rows with aligned outcomes, both Seshat-coded sides, "
                "and unique time-valid polity identities enter the provisional tactical ledger. "
                "Rows lacking Seshat coding on one or both sides are retried in a second, "
                "declared label-resolution pass: sides resolve only through explicit "
                "time-bounded label policies or exact-normalized alias matching with "
                "uniqueness, full event-interval validity, and name-coherence for "
                "observation-derived pairings; faction and collective-peoples labels never "
                "resolve; polity labels pending identity splits never resolve; ambiguity "
                "always stays staged. Label-resolved events carry reduced identity confidence "
                "and an identity_resolution provenance marker. "
                "IWD component wars never enter individually: each parent conflict is rated at "
                "most once, as a coalition event aggregated from its component dyads, and only "
                "when the reconstructed sides are consistent, the component outcomes are "
                "unanimous, no curated seed war overlaps, and every belligerent resolves to a "
                "unique time-bounded identity. All other parent wars stay staged. "
                "IWBD battles enter only when they are not a duplicate of any curated seed "
                "event, any non-curated-excluded HCED candidate (promoted or staged), or an "
                "earlier accepted IWBD row by exact normalized battle name and year within "
                "one year; "
                "broader ordinal/part matches require one recognized suffix path to extend "
                "the other in the same year with the same resolved outcome sides; "
                "their date span does not "
                "contain a differently-named battle of the same war (campaign umbrellas stay "
                "staged); the coded victor matches a named side; both sides are single "
                "polities resolving to unique time-bounded identities outside declared deny "
                "windows; and severity is capped at limited. Duplicate matches are excluded, "
                "never merged. "
                "UCDP conflict-termination episodes promote only as conflict-level terminal "
                "victory episodes (outcome codes 3/4): peace agreements, ceasefires, low "
                "activity, and actor cessation stay staged; every primary party must be a "
                "state resolving to a unique time-bounded identity through explicit "
                "Gleditsch-Ward code policies or exact time-valid alias matching; episodes "
                "duplicating an already-promoted strategic event, contradicted by a terminal "
                "dyad row, linked by end date to an oppositely-oriented victory assertion, or "
                "carrying a documented side-attribution dispute stay staged; severity is "
                "capped at limited and secondary supporters carry no outcome. "
                "A curated tranche of time-bounded state identities and label/code policy "
                "windows (second reviewer pending) resolves previously blocked bare labels "
                "and orphaned source codes era-correctly, with deliberate gaps for eras "
                "without a defensible single identity, and enumerated curated row exclusions "
                "for known wrong-actor and variant-spelling records - counted, never merged. "
                "A declared set of curated non-state actor identities moves seven former "
                "blocklist labels to authoritative time-bounded policies and covers five "
                "additional labels that were never blocklisted; labels for "
                "umbrella movements without unified command stay blocked. UCDP "
                "terminal-victory episodes may include a curated non-state primary party "
                "only through conflict-scoped actor policies whose windows are the actor's "
                "attested existence bounds; the government side must independently resolve. "
                "UCDP war_type follows the source's type_of_conflict under an exhaustive "
                "declared mapping; unmapped types are rejected, never coerced."
            ),
            "accepted_hced_events": len(source_events),
            "accepted_hced_label_events": len(label_events),
            "hced_label_pass_input_rows": hced_label_pass["rows_total"],
            "accepted_iwd_wars": len(iwd_events),
            "iwd_parent_wars_total": iwd_aggregation["parents_total"],
            "iwd_components_aggregated": iwd_aggregation["components_aggregated"],
            "iwd_components_attached_to_rated_parents": iwd_aggregation["components_attached"],
            "hced_rejections": dict(sorted(rejections.items())),
            "hced_label_rejections": _declared_rejections(
                hced_label_rejections, HCED_LABEL_REJECTION_COUNTERS
            ),
            "hced_label_policy_labels": sorted(HCED_LABEL_POLICIES),
            "hced_faction_labels_staged": sorted(HCED_FACTION_LABELS),
            "hced_pending_split_labels": sorted(HCED_PENDING_SPLIT_LABELS),
            "hced_label_observation_resolutions": hced_label_pass["observation_resolutions"],
            "hced_curated_exclusions": [
                {"candidate_id": key, "reason": reason}
                for key, reason in sorted(HCED_CURATED_EXCLUSIONS.items())
            ],
            "hced_label_curated_exclusions": [
                {"candidate_id": key, "reason": reason}
                for key, reason in sorted(HCED_LABEL_CURATED_EXCLUSIONS.items())
            ],
            "iwbd_curated_exclusions": [
                {"candidate_id": key, "reason": reason}
                for key, reason in sorted(IWBD_CURATED_EXCLUSIONS.items())
            ],
            "iwd_curated_parent_exclusions": [
                {"parent_war_id": key, "reason": reason}
                for key, reason in sorted(IWD_CURATED_PARENT_EXCLUSIONS.items())
            ],
            "seed_event_interval_exemptions": [
                {
                    "event_id": key[0],
                    "entity_id": key[1],
                    "event_interval": list(exemption["event_interval"]),
                    "entity_interval": list(exemption["entity_interval"]),
                    "reason": exemption["reason"],
                }
                for key, exemption in sorted(SEED_EVENT_INTERVAL_EXEMPTIONS.items())
            ],
            "ucdp_actor_party_policies": [
                {
                    "conflict_id": conflict_id,
                    "party_label": party,
                    "windows": [list(window) for window in windows],
                }
                for (conflict_id, party), windows in sorted(UCDP_ACTOR_PARTY_POLICIES.items())
            ],
            "ucdp_war_types": UCDP_WAR_TYPES,
            "iwd_rejections": dict(sorted(iwd_rejections.items())),
            "accepted_iwbd_battles": len(iwbd_events),
            "iwbd_battles_total": iwbd_promotion["battles_total"],
            "iwbd_rejections": _declared_rejections(iwbd_rejections, IWBD_REJECTION_COUNTERS),
            "accepted_ucdp_events": len(ucdp_events),
            "ucdp_termination_rows_total": ucdp_promotion["rows_total"],
            "ucdp_rejections": _declared_rejections(ucdp_rejections, UCDP_REJECTION_COUNTERS),
            "ucdp_curated_exclusions": [
                {"conflict_id": key[0], "episode_number": key[1], "reason": reason}
                for key, reason in sorted(UCDP_CURATED_EXCLUSIONS.items())
            ],
            "ucdp_duplicate_details": ucdp_promotion["duplicate_details"],
            "ucdp_dyad_rows_total": ucdp_promotion["dyad_rows_total"],
            "ucdp_dyad_rows_quarantined_corrupt": ucdp_promotion[
                "dyad_rows_quarantined_corrupt"
            ],
            "ucdp_dyad_terminal_blank_outcome": ucdp_promotion["dyad_terminal_blank_outcome"],
            "source_queue_counts": review_counts,
        },
        "known_limitations": [
            "The release is not a complete census and must not be presented as a definitive all-history ranking.",
            "Strategic war outcomes remain much less complete than tactical engagement outcomes.",
            "HCED winner labels and the Seshat crosswalk are source assertions pending claim-level human review.",
            "Label-resolved HCED events rest on side-name identity policies and exact alias matches rather than the Seshat crosswalk; they carry lower confidence and remain source assertions pending claim-level human review, and the label-policy entries are entity-boundary decisions pending second-reviewer sign-off.",
            "Cliopatria intervals are split at temporal gaps; final historiographic continuity still requires explicit decisions.",
            "Some Cliopatria identity intervals span successive regimes (for example one Cambodia identity covering 1956-2024), so events resolved to them can share a rating line across regime changes until those identities receive explicit curated splits.",
            "Aggregated IWD coalition events use declared uniform defaults for contribution, role, scale, and stakes because the source carries no per-participant data.",
            "IWBD events use declared uniform defaults for scale, stakes, contribution, and role because the source carries no per-battle magnitude data, and IWBD war-level victor codes are ignored: battle records never update strategic outcomes.",
            "Coalition-labelled IWBD battles (notably both world wars) remain staged pending curated coalition composition, and IWBD rows whose date span contains a sibling battle are staged as presumptive campaign umbrellas, which also quarantines some genuinely distinct long engagements.",
            "IWBD-HCED name and date matches are counted as exclusions only; they are not treated as independent corroboration and no HCED record is modified.",
            "UCDP episode-level termination outcomes may not describe every supporter: secondary parties are recorded without outcomes, and uniform strategic vectors with scale-linked participant uniforms are declared defaults, as with IWD.",
            "The 1967 Arab-Israeli fronts and the 1974 Paracel episode stay staged: the source carries mutually contradictory orientations for the former and a documented side-attribution dispute for the latter.",
            "Ancient, non-literate, small, defeated, and non-European polities remain systematically under-recorded.",
        ],
        "prohibited_interpretation": (
            "Do not treat provisional ratings or unrated registry entries as a definitive ranking "
            "of every country and empire in history."
        ),
    }

    _write_json(release / "entities.json", release_entity_rows)
    _write_json(release / "events.json", all_events)
    _write_json(release / "sources.json", sorted(sources_by_id.values(), key=lambda row: row["id"]))
    _write_json(release / "metadata.json", metadata)
    _write_json(registry_path, registry)
    return {
        "entities": len(release_entity_rows),
        "rated_entities": len(used_entity_ids),
        "events": len(all_events),
        "provisional_hced_events": len(source_events),
        "provisional_hced_label_events": len(label_events),
        "provisional_iwd_wars": len(iwd_events),
        "provisional_iwbd_battles": len(iwbd_events),
        "provisional_ucdp_events": len(ucdp_events),
        "registry_polities": len(registry_rows),
        "staged_source_records": staged_source_records,
        "unresolved_event_candidates": unresolved_event_candidates,
        "hced_rejections": dict(sorted(rejections.items())),
        "hced_label_rejections": _declared_rejections(
            hced_label_rejections, HCED_LABEL_REJECTION_COUNTERS
        ),
        "iwd_rejections": dict(sorted(iwd_rejections.items())),
        "iwbd_rejections": _declared_rejections(iwbd_rejections, IWBD_REJECTION_COUNTERS),
        "ucdp_rejections": _declared_rejections(ucdp_rejections, UCDP_REJECTION_COUNTERS),
    }
