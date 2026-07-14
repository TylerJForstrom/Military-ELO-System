"""Append-only evidence review and reproducible gold-set utilities.

Claims retain assertions while adjudications retain parallel reviewer decisions.
Supersession appends a new decision instead of mutating history.  Exclusive
claim groups and high-impact secondary review are derived audit constraints;
even an accepted claim remains evidence-only until a separate future promotion
workflow explicitly makes it rating-eligible.  Gold-set source families must be
declared as such and are never inferred from a generic ``source`` label.
"""

from __future__ import annotations

import json
import hashlib
import random
import re
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

from .canonical import CanonicalEvent
from .claims import (
    CLAIM_STATUSES,
    Claim,
    EvidenceLink,
    canonical_json,
    canonicalize_json,
    find_disagreements,
)


@dataclass(frozen=True)
class Adjudication:
    """An immutable review decision in an append-only supersession history."""

    id: str
    claim_id: str
    reviewer: str
    decision: str
    rationale: str
    codebook_version: str
    supersedes: tuple[str, ...] = field(default_factory=tuple)
    reviewed_at: str = ""
    review_stage: str | None = None
    evidence_ids_considered: tuple[str, ...] = field(default_factory=tuple)
    blind_review: bool | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        if self.blind_review is not None and not isinstance(self.blind_review, bool):
            raise TypeError("Adjudication.blind_review must be a boolean or null")
        if self.review_stage is not None and not isinstance(self.review_stage, str):
            raise TypeError("Adjudication.review_stage must be a string or null")
        if self.confidence is not None and (
            isinstance(self.confidence, bool)
            or not isinstance(self.confidence, (int, float))
        ):
            raise TypeError("Adjudication.confidence must be a number or null")
        supersedes = self.supersedes
        if not isinstance(supersedes, (list, tuple)):
            raise TypeError("Adjudication.supersedes must be an array of stable ids")
        evidence_ids = self.evidence_ids_considered
        if not isinstance(evidence_ids, (list, tuple)):
            raise TypeError(
                "Adjudication.evidence_ids_considered must be an array of stable ids"
            )
        if any(not isinstance(item, str) for item in supersedes):
            raise TypeError("Adjudication.supersedes must contain string ids")
        if any(not isinstance(item, str) for item in evidence_ids):
            raise TypeError(
                "Adjudication.evidence_ids_considered must contain string ids"
            )
        object.__setattr__(self, "supersedes", tuple(sorted(set(supersedes))))
        object.__setattr__(
            self,
            "evidence_ids_considered",
            tuple(sorted(set(evidence_ids))),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "claim_id": self.claim_id,
            "reviewer": self.reviewer,
            "decision": self.decision,
            "rationale": self.rationale,
            "codebook_version": self.codebook_version,
            "supersedes": sorted(set(self.supersedes)),
        }
        if self.reviewed_at:
            result["reviewed_at"] = self.reviewed_at
        if self.review_stage is not None:
            result["review_stage"] = self.review_stage
        if self.evidence_ids_considered:
            result["evidence_ids_considered"] = sorted(
                set(self.evidence_ids_considered)
            )
        if self.blind_review is not None:
            result["blind_review"] = self.blind_review
        if self.confidence is not None:
            result["confidence"] = self.confidence
        return result

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Adjudication":
        def text_field(name: str, *, alias: str | None = None) -> str:
            value = raw.get(name, raw.get(alias, "") if alias else "")
            if not isinstance(value, str):
                raise TypeError(f"Adjudication.{name} must be a string")
            return value

        supersedes_raw = raw["supersedes"] if "supersedes" in raw else []
        if not isinstance(supersedes_raw, (list, tuple)):
            raise TypeError("Adjudication.supersedes must be an array of stable ids")
        evidence_ids_raw = (
            raw["evidence_ids_considered"]
            if "evidence_ids_considered" in raw
            else []
        )
        if not isinstance(evidence_ids_raw, (list, tuple)):
            raise TypeError(
                "Adjudication.evidence_ids_considered must be an array of stable ids"
            )
        if any(not isinstance(item, str) for item in supersedes_raw):
            raise TypeError("Adjudication.supersedes must contain string ids")
        if any(not isinstance(item, str) for item in evidence_ids_raw):
            raise TypeError(
                "Adjudication.evidence_ids_considered must contain string ids"
            )
        blind_review_raw = raw.get("blind_review")
        if blind_review_raw is not None and not isinstance(blind_review_raw, bool):
            raise TypeError("Adjudication.blind_review must be a boolean or null")
        review_stage_raw = raw.get("review_stage")
        if review_stage_raw is not None and not isinstance(review_stage_raw, str):
            raise TypeError("Adjudication.review_stage must be a string or null")
        confidence_raw = raw.get("confidence")
        if confidence_raw is not None and (
            isinstance(confidence_raw, bool)
            or not isinstance(confidence_raw, (int, float))
        ):
            raise TypeError("Adjudication.confidence must be a number or null")
        return cls(
            id=text_field("id", alias="adjudication_id"),
            claim_id=text_field("claim_id"),
            reviewer=text_field("reviewer"),
            decision=text_field("decision"),
            rationale=text_field("rationale"),
            codebook_version=text_field("codebook_version"),
            supersedes=tuple(str(item) for item in supersedes_raw),
            reviewed_at=text_field("reviewed_at"),
            review_stage=review_stage_raw,
            evidence_ids_considered=tuple(
                str(item) for item in evidence_ids_raw
            ),
            blind_review=blind_review_raw,
            confidence=confidence_raw,
        )


def adjudication_history_errors(
    adjudications: Iterable[Adjudication],
) -> list[str]:
    """Validate ordering and referential rules for an append-only history."""

    history = list(adjudications)
    by_id: dict[str, Adjudication] = {}
    positions: dict[str, int] = {}
    errors: list[str] = []
    for index, item in enumerate(history):
        for field_name in (
            "id",
            "claim_id",
            "reviewer",
            "decision",
            "rationale",
            "codebook_version",
        ):
            value = getattr(item, field_name)
            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"decision at position {index} requires non-blank {field_name}"
                )
        if not item.id:
            errors.append(f"decision at position {index} has no stable id")
            continue
        if item.id in by_id:
            errors.append(f"duplicate adjudication id {item.id}")
            continue
        by_id[item.id] = item
        positions[item.id] = index

    for index, item in enumerate(history):
        for prior_id in item.supersedes:
            if prior_id == item.id:
                errors.append(f"{item.id} cannot supersede itself")
                continue
            prior = by_id.get(prior_id)
            if prior is None:
                errors.append(f"{item.id} supersedes unknown adjudication {prior_id}")
                continue
            if positions[prior_id] >= index:
                errors.append(
                    f"{item.id} must appear after superseded adjudication {prior_id}"
                )
            if prior.claim_id != item.claim_id:
                errors.append(
                    f"{item.id} cannot supersede {prior_id} for a different claim"
                )

    graph = {item.id: set(item.supersedes) for item in history if item.id}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            errors.append(f"adjudication supersession cycle includes {node}")
            return
        visiting.add(node)
        for target in graph.get(node, set()):
            if target in graph:
                visit(target)
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return errors


def append_adjudication(
    history: Iterable[Adjudication],
    decision: Adjudication,
) -> tuple[Adjudication, ...]:
    """Append a decision without modifying or replacing any prior record."""

    result = tuple(history) + (decision,)
    errors = adjudication_history_errors(result)
    if errors:
        raise ValueError("Invalid append-only adjudication: " + "; ".join(errors))
    return result


def active_adjudications(
    history: Iterable[Adjudication],
) -> tuple[Adjudication, ...]:
    """Return every unsuperseded leaf, retaining parallel reviewer decisions."""

    decisions = tuple(history)
    superseded = {
        prior_id
        for decision in decisions
        for prior_id in decision.supersedes
    }
    return tuple(
        sorted(
            (decision for decision in decisions if decision.id not in superseded),
            key=lambda item: item.id,
        )
    )


@dataclass(frozen=True)
class ClaimResolution:
    """A derived view over immutable claims and decisions, never stored in-place."""

    claim_id: str
    state: str
    adjudication_ids: tuple[str, ...] = field(default_factory=tuple)
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "state": self.state,
            "adjudication_ids": list(self.adjudication_ids),
            "reasons": list(self.reasons),
        }


def resolve_claims(
    claims: Iterable[Claim],
    adjudications: Iterable[Adjudication],
) -> dict[str, ClaimResolution]:
    """Derive effective decisions without mutating claims or decision history.

    High-impact acceptance requires explicit primary and secondary acceptance
    by distinct reviewer identifiers.  Mutually exclusive claims in the same
    group are all left unresolved if more than one would otherwise resolve as
    accepted.
    """

    claim_list = list(claims)
    history = list(adjudications)
    errors = adjudication_history_errors(history)
    if errors:
        raise ValueError("Invalid adjudication history: " + "; ".join(errors))
    claim_by_id: dict[str, Claim] = {}
    for claim in claim_list:
        if not claim.id or claim.id in claim_by_id:
            raise ValueError(f"Claims require unique stable ids: {claim.id!r}")
        if claim.status not in CLAIM_STATUSES:
            raise ValueError(f"Claim {claim.id} has invalid lifecycle status {claim.status!r}")
        if claim.impact not in (None, "ordinary", "high"):
            raise ValueError(f"Claim {claim.id} has invalid impact {claim.impact!r}")
        if claim.claim_group_id is not None and not claim.claim_group_id.strip():
            raise ValueError(f"Claim {claim.id} has a blank claim_group_id")
        if claim.exclusive is True and claim.claim_group_id is None:
            raise ValueError(f"Exclusive claim {claim.id} requires claim_group_id")
        claim_by_id[claim.id] = claim
    unknown_claims = sorted(
        {item.claim_id for item in history if item.claim_id not in claim_by_id}
    )
    if unknown_claims:
        raise ValueError(
            "Adjudications reference unknown claims: " + ", ".join(unknown_claims)
        )

    active = active_adjudications(history)
    active_by_claim: dict[str, list[Adjudication]] = defaultdict(list)
    for item in active:
        active_by_claim[item.claim_id].append(item)

    resolutions: dict[str, ClaimResolution] = {}
    for claim in claim_list:
        leaves = sorted(active_by_claim[claim.id], key=lambda item: item.id)
        leaf_ids = tuple(item.id for item in leaves)
        if claim.status != "active":
            resolutions[claim.id] = ClaimResolution(
                claim.id,
                "inactive",
                leaf_ids,
                (f"claim lifecycle status is {claim.status}",),
            )
            continue
        if not leaves:
            resolutions[claim.id] = ClaimResolution(
                claim.id, "unreviewed", (), ("no active adjudication",)
            )
            continue
        decisions = {item.decision for item in leaves}
        if len(decisions) != 1:
            resolutions[claim.id] = ClaimResolution(
                claim.id,
                "unresolved",
                leaf_ids,
                ("active adjudications disagree",),
            )
            continue
        decision = next(iter(decisions))
        if decision != "accepted":
            state = "rejected" if decision == "rejected" else "unresolved"
            resolutions[claim.id] = ClaimResolution(
                claim.id, state, leaf_ids, (f"active decision is {decision}",)
            )
            continue
        if claim.impact == "high":
            accepted_history = [item for item in leaves if item.decision == "accepted"]
            primary_reviewers = {
                item.reviewer.strip()
                for item in accepted_history
                if item.review_stage == "primary" and item.reviewer.strip()
            }
            secondary_reviewers = {
                item.reviewer.strip()
                for item in accepted_history
                if item.review_stage == "secondary" and item.reviewer.strip()
            }
            has_distinct_pair = any(
                primary != secondary
                for primary in primary_reviewers
                for secondary in secondary_reviewers
            )
            if not has_distinct_pair:
                resolutions[claim.id] = ClaimResolution(
                    claim.id,
                    "unresolved",
                    leaf_ids,
                    ("high-impact acceptance requires distinct primary and secondary reviewers",),
                )
                continue
        resolutions[claim.id] = ClaimResolution(claim.id, "accepted", leaf_ids)

    claim_groups: dict[str, list[Claim]] = defaultdict(list)
    for claim in claim_list:
        if claim.claim_group_id:
            claim_groups[claim.claim_group_id].append(claim)
    for group_id, group_claims in claim_groups.items():
        if not any(claim.exclusive is True for claim in group_claims):
            continue
        claim_ids = [claim.id for claim in group_claims]
        accepted_ids = [
            claim_id
            for claim_id in claim_ids
            if resolutions[claim_id].state == "accepted"
        ]
        if len(accepted_ids) < 2:
            continue
        reason = f"mutually exclusive group {group_id} has multiple accepted claims"
        for claim_id in accepted_ids:
            current = resolutions[claim_id]
            resolutions[claim_id] = ClaimResolution(
                claim_id,
                "unresolved",
                current.adjudication_ids,
                current.reasons + (reason,),
            )
    return dict(sorted(resolutions.items()))


def load_json_records(
    path: str | Path,
    *,
    container_keys: Sequence[str] = ("records", "events", "claims", "adjudications"),
) -> list[dict[str, Any]]:
    """Load a JSON array/document or a JSONL stream without mutating it."""

    source = Path(path)
    text = source.read_text(encoding="utf-8")
    if source.suffix.lower() == ".jsonl":
        values = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        document = json.loads(text)
        if isinstance(document, list):
            values = document
        elif isinstance(document, dict):
            values = None
            for key in container_keys:
                if key not in document:
                    continue
                if not isinstance(document[key], list):
                    raise ValueError(f"{source} field {key!r} must be an array")
                values = document[key]
                break
            if values is None:
                values = [document]
        else:
            raise ValueError(f"{source} must contain a JSON object or array")
    if any(not isinstance(item, dict) for item in values):
        raise ValueError(f"{source} contains a non-object record")
    return [canonicalize_json(item) for item in values]


def _record_id(record: dict[str, Any], id_field: str | None) -> str:
    if id_field is not None:
        if record.get(id_field) in (None, ""):
            raise ValueError(f"Every sampled record requires explicit id field {id_field!r}")
        return str(record[id_field])
    candidates = ["id", "candidate_id", "event_id", "claim_id"]
    for name in candidates:
        if name and record.get(name) not in (None, ""):
            return str(record[name])
    raise ValueError("Every sampled record requires a stable id")


def _normalized_label(value: Any) -> str:
    if value in (None, "", [], {}):
        return "unknown"
    if isinstance(value, (list, tuple, set)):
        labels = sorted({_normalized_label(item) for item in value})
        return "+".join(labels) if labels else "unknown"
    if isinstance(value, dict):
        return json.dumps(
            canonicalize_json(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    return str(value).strip() or "unknown"


def _extract_year(record: dict[str, Any]) -> int | None:
    raw = record.get("raw") if isinstance(record.get("raw"), dict) else {}
    for name in ("year_best", "year", "start_year", "end_year"):
        value = record.get(name, raw.get(name))
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, str):
            match = re.match(r"^(-?\d{1,6})", value.strip())
            if match:
                return int(match.group(1))
    for name in ("start_date", "date", "end_date"):
        value = record.get(name, raw.get(name))
        if isinstance(value, str):
            match = re.match(r"^(-?\d{1,6})", value.strip())
            if match:
                return int(match.group(1))
    date_interval = record.get("date_interval")
    if isinstance(date_interval, dict):
        start = date_interval.get("start")
        if isinstance(start, dict):
            for name in ("best", "low", "high"):
                value = start.get(name)
                if isinstance(value, int):
                    return value
    return None


def _era_label(record: dict[str, Any]) -> str:
    if record.get("era") not in (None, ""):
        return _normalized_label(record["era"])
    year = _extract_year(record)
    if year is None:
        return "unknown"
    if year < 500:
        return "ancient"
    if year < 1500:
        return "medieval"
    if year < 1800:
        return "early_modern"
    if year < 1946:
        return "modern"
    return "contemporary"


def _stratum_value(record: dict[str, Any], field_name: str) -> str:
    if field_name == "era":
        return _era_label(record)
    if record.get(field_name) not in (None, ""):
        return _normalized_label(record[field_name])

    raw = record.get("raw") if isinstance(record.get("raw"), dict) else {}
    if field_name == "region":
        for name in ("modern_location_country", "region", "location", "country"):
            value = record.get(name, raw.get(name))
            if value not in (None, ""):
                return _normalized_label(value)
    elif field_name == "layer":
        event_type = record.get(
            "event_type",
            record.get("proposed_event_type", record.get("track")),
        )
        return {
            "engagement": "tactical",
            "battle": "tactical",
            "campaign": "operational",
            "operation": "operational",
            "war": "strategic",
            "conflict": "strategic",
        }.get(str(event_type).lower(), _normalized_label(event_type))
    elif field_name == "domain":
        for name in ("domain", "theatre_raw", "theater", "theatre"):
            value = record.get(name, raw.get(name))
            if value not in (None, ""):
                return _normalized_label(value).lower()
    elif field_name == "source_family":
        if record.get("source_family") not in (None, ""):
            return _normalized_label(record["source_family"])
        provenance = record.get("provenance")
        if isinstance(provenance, list):
            families = [
                item.get("source_family")
                for item in provenance
                if isinstance(item, dict) and item.get("source_family")
            ]
            if families:
                return _normalized_label(families)
    elif raw.get(field_name) not in (None, ""):
        return _normalized_label(raw[field_name])
    return "unknown"


def _allocate_sample(
    sizes: dict[tuple[str, ...], int],
    sample_size: int,
    *,
    seed: int,
) -> dict[tuple[str, ...], int]:
    keys = sorted(sizes)
    allocation = {key: 0 for key in keys}
    remaining = sample_size

    if sample_size >= len(keys):
        for key in keys:
            allocation[key] = 1
        remaining -= len(keys)

    capacity = {key: sizes[key] - allocation[key] for key in keys}
    total_capacity = sum(capacity.values())
    if remaining <= 0 or total_capacity <= 0:
        return allocation

    quota_numerators = {
        key: remaining * capacity[key]
        for key in keys
    }
    floors = {
        key: min(capacity[key], quota_numerators[key] // total_capacity)
        for key in keys
    }
    for key in keys:
        allocation[key] += floors[key]
    leftover = remaining - sum(floors.values())

    def seeded_tie_break(key: tuple[str, ...]) -> bytes:
        payload = f"{seed}\0{canonical_json(list(key))}".encode("utf-8")
        return hashlib.sha256(payload).digest()

    eligible = [key for key in keys if allocation[key] < sizes[key]]
    eligible.sort(
        key=lambda key: (
            -(quota_numerators[key] % total_capacity),
            seeded_tie_break(key),
            key,
        )
    )
    for key in eligible[:leftover]:
        allocation[key] += 1
    return allocation


def sample_gold_set(
    records: Iterable[dict[str, Any]],
    sample_size: int,
    *,
    seed: int,
    stratify_by: Sequence[str] = (
        "era",
        "region",
        "layer",
        "domain",
        "source_family",
    ),
    id_field: str | None = None,
) -> list[dict[str, Any]]:
    """Select a reproducible, input-order-independent stratified sample."""

    population = [canonicalize_json(deepcopy(record)) for record in records]
    if sample_size < 0 or sample_size > len(population):
        raise ValueError("sample_size must be between zero and the population size")
    indexed: dict[str, dict[str, Any]] = {}
    for record in population:
        record_id = _record_id(record, id_field)
        if record_id in indexed:
            raise ValueError(f"Duplicate sampling id {record_id}")
        indexed[record_id] = record
    if sample_size == 0:
        return []

    groups: dict[tuple[str, ...], list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for record_id in sorted(indexed):
        record = indexed[record_id]
        key = tuple(_stratum_value(record, name) for name in stratify_by)
        groups[key].append((record_id, record))

    allocation = _allocate_sample(
        {key: len(group) for key, group in groups.items()},
        sample_size,
        seed=seed,
    )
    rng = random.Random(seed)
    selected: list[tuple[str, dict[str, Any]]] = []
    for key in sorted(groups):
        candidates = sorted(groups[key], key=lambda item: item[0])
        rng.shuffle(candidates)
        selected.extend(candidates[: allocation[key]])
    selected.sort(key=lambda item: item[0])
    return [canonicalize_json(item) for _, item in selected]


def build_gold_set_document(
    records: Iterable[dict[str, Any]],
    sample_size: int,
    *,
    seed: int,
    stratify_by: Sequence[str] = (
        "era",
        "region",
        "layer",
        "domain",
        "source_family",
    ),
    id_field: str | None = None,
) -> dict[str, Any]:
    population = [canonicalize_json(deepcopy(record)) for record in records]
    selected = sample_gold_set(
        population,
        sample_size,
        seed=seed,
        stratify_by=stratify_by,
        id_field=id_field,
    )

    def counts(values: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, ...], int] = defaultdict(int)
        for record in values:
            grouped[tuple(_stratum_value(record, name) for name in stratify_by)] += 1
        return [
            {
                "stratum": dict(zip(stratify_by, key)),
                "count": grouped[key],
            }
            for key in sorted(grouped)
        ]

    population_manifest = [
        {
            "id": _record_id(record, id_field),
            "stratum": {
                name: _stratum_value(record, name)
                for name in stratify_by
            },
        }
        for record in sorted(population, key=lambda item: _record_id(item, id_field))
    ]
    selected_ids = {_record_id(record, id_field) for record in selected}
    selected_manifest = [
        item for item in population_manifest if item["id"] in selected_ids
    ]
    population_digest = hashlib.sha256(
        canonical_json(population_manifest).encode("utf-8")
    ).hexdigest()

    return {
        "format_version": "1.0",
        "seed": seed,
        "population_digest": f"sha256:{population_digest}",
        "id_field": id_field or "auto",
        "population_size": len(population),
        "sample_size": len(selected),
        "stratify_by": list(stratify_by),
        "strata_population": counts(population),
        "strata_sample": counts(selected),
        "population_manifest": population_manifest,
        "records": selected_manifest,
    }


_EVENT_FIELDS = (
    "id",
    "name",
    "aliases",
    "parent_event_id",
    "parent_event_ids",
    "child_event_ids",
    "date_interval",
    "geometry",
    "participation_episodes",
    "claim_ids",
    "event_type",
    "layer",
    "domain",
    "region",
    "status",
    "source_ids",
)

_PARTICIPATION_FIELDS = (
    "id",
    "entity_id",
    "side",
    "role",
    "entry",
    "exit",
    "contribution",
    "objectives",
    "claim_ids",
)

_EVENT_SET_FIELDS = (
    "aliases",
    "parent_event_ids",
    "child_event_ids",
    "claim_ids",
    "source_ids",
)


def _normalized_string_array(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple, set)):
        raise ValueError(f"{field_name} must be an array of strings")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{field_name} must contain non-blank strings")
    return sorted(set(value))

FORBIDDEN_MODEL_OUTPUT_KEYS = {
    "composite_rating",
    "coverage_factor",
    "delta",
    "elo",
    "effective_events",
    "effective_wars",
    "evidence_weight",
    "historical_success",
    "historical_success_index",
    "historical_success_raw",
    "k_factor",
    "leaderboard",
    "leaderboard_effect",
    "model_effect",
    "model_output",
    "model_outputs",
    "model_score",
    "operational_rating",
    "rank",
    "rating",
    "rating_effect",
    "sensitivity",
    "strategic_rating",
    "tactical_rating",
}

_FORBIDDEN_MODEL_FIELD_TOKENS = {
    "delta",
    "elo",
    "leaderboard",
    "rank",
    "rating",
    "sensitivity",
}

_FORBIDDEN_MODEL_OUTPUT_TEXT = re.compile(
    r"(?:\bleaderboard\b|\b(?:elo|rating|rank|delta)\b\s*(?:(?:is|of)\s*|[:=]\s*)?[+-]?[0-9]+(?:\.[0-9]+)?)",
    re.IGNORECASE,
)


def _is_forbidden_model_field(value: str) -> bool:
    separated = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", value)
    normalized = re.sub(r"[^a-z0-9]+", "_", separated.lower()).strip("_")
    tokens = {token for token in normalized.split("_") if token}
    return (
        any(
            normalized == forbidden
            or normalized.startswith(f"{forbidden}_")
            or normalized.endswith(f"_{forbidden}")
            for forbidden in FORBIDDEN_MODEL_OUTPUT_KEYS
        )
        or bool(tokens & _FORBIDDEN_MODEL_FIELD_TOKENS)
    )


def _event_evidence_view(event: CanonicalEvent | dict[str, Any]) -> dict[str, Any]:
    if isinstance(event, CanonicalEvent):
        raw = event.to_dict()
    else:
        raw = canonicalize_json(deepcopy(event))
        if isinstance(raw.get("canonical_event"), dict):
            raw = raw["canonical_event"]
    result = {
        name: canonicalize_json(raw[name])
        for name in _EVENT_FIELDS
        if name not in _EVENT_SET_FIELDS
        if name in raw and raw[name] is not None
    }
    if (
        not isinstance(result.get("id"), str)
        or not result["id"].strip()
        or not isinstance(result.get("name"), str)
        or not result["name"].strip()
    ):
        raise ValueError("Review packet events require stable id and name fields")
    for field_name in _EVENT_SET_FIELDS:
        if field_name in raw:
            normalized = _normalized_string_array(raw[field_name], field_name)
            if normalized:
                result[field_name] = normalized

    episodes = raw.get("participation_episodes")
    if episodes is None and isinstance(raw.get("participants"), list):
        episodes = raw["participants"]
    if episodes is not None:
        if not isinstance(episodes, list):
            raise ValueError("participation_episodes must be an array")
        normalized_episodes: list[dict[str, Any]] = []
        episode_ids: set[str] = set()
        for episode in episodes:
            if not isinstance(episode, dict):
                raise ValueError("participation_episodes must contain objects")
            normalized_episode = {
                name: canonicalize_json(episode[name])
                for name in _PARTICIPATION_FIELDS
                if name in episode
                and episode[name] is not None
            }
            if "claim_ids" in normalized_episode:
                normalized_episode["claim_ids"] = _normalized_string_array(
                    normalized_episode["claim_ids"],
                    "participation_episodes[].claim_ids",
                )
            if "objectives" in normalized_episode:
                normalized_episode["objectives"] = _normalized_string_array(
                    normalized_episode["objectives"],
                    "participation_episodes[].objectives",
                )
            episode_id = normalized_episode.get("id")
            if episode_id is not None:
                if not isinstance(episode_id, str) or not episode_id.strip():
                    raise ValueError("Participation episode ids must be non-blank strings")
                if episode_id in episode_ids:
                    raise ValueError(f"Duplicate participation episode id {episode_id}")
                episode_ids.add(episode_id)
            normalized_episodes.append(normalized_episode)
        result["participation_episodes"] = sorted(
            normalized_episodes,
            key=canonical_json,
        )
    return result


def _find_forbidden_key(value: Any, path: str = "$") -> tuple[str, str] | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if _is_forbidden_model_field(key):
                return (f"{path}.{key}", key)
            found = _find_forbidden_key(item, f"{path}.{key}")
            if found:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = _find_forbidden_key(item, f"{path}[{index}]")
            if found:
                return found
    return None


def build_review_packet(
    events: Iterable[CanonicalEvent | dict[str, Any]],
    claims: Iterable[Claim | dict[str, Any]],
    adjudications: Iterable[Adjudication | dict[str, Any]] = (),
    *,
    evidence_links: Iterable[EvidenceLink | dict[str, Any]] = (),
    event_ids: Iterable[str] | None = None,
    include_prior_decisions: bool = False,
) -> dict[str, Any]:
    """Build an internally complete packet without modeled Elo effects.

    Prior adjudications are excluded by default for independent review.  When
    explicitly requested they retain append order and the packet truthfully
    reports that it is no longer decision-blinded.  Neither packet inclusion
    nor an accepted adjudication makes a claim rating-eligible.
    """

    event_views = [_event_evidence_view(event) for event in events]
    by_event_id: dict[str, dict[str, Any]] = {}
    for event in event_views:
        event_id = event["id"]
        if event_id in by_event_id:
            raise ValueError(f"Duplicate event id {event_id}")
        by_event_id[event_id] = event

    if isinstance(event_ids, (str, bytes)):
        raise ValueError("event_ids must be an array of stable event ids")
    selected_ids = (
        {str(item) for item in event_ids}
        if event_ids is not None
        else set(by_event_id)
    )
    unknown_ids = selected_ids - set(by_event_id)
    if unknown_ids:
        raise ValueError(f"Unknown review event ids: {', '.join(sorted(unknown_ids))}")
    selected_events = [by_event_id[event_id] for event_id in sorted(selected_ids)]

    claim_objects = [
        item if isinstance(item, Claim) else Claim.from_dict(item)
        for item in claims
    ]
    claim_by_id: dict[str, Claim] = {}
    for claim in claim_objects:
        if not claim.id.strip() or not claim.subject.strip() or not claim.predicate.strip():
            raise ValueError("Review packet claims require stable id, subject, and predicate")
        if claim.id in claim_by_id:
            raise ValueError(f"Duplicate claim id {claim.id}")
        claim_by_id[claim.id] = claim

    referenced_claim_ids = {
        claim_id
        for event in selected_events
        for claim_id in (event.get("claim_ids") or [])
    }
    referenced_claim_ids.update(
        claim_id
        for event in selected_events
        for episode in (event.get("participation_episodes") or [])
        for claim_id in (episode.get("claim_ids") or [])
    )
    missing_referenced_claims = referenced_claim_ids - set(claim_by_id)
    if missing_referenced_claims:
        raise ValueError(
            "Selected events reference unknown claims: "
            + ", ".join(sorted(missing_referenced_claims))
        )

    event_subjects = selected_ids | {f"event:{item}" for item in selected_ids}
    selected_claim_ids = {
        claim.id
        for claim in claim_objects
        if claim.id in referenced_claim_ids or claim.subject in event_subjects
    }
    while True:
        outgoing = {
            contradicted_id
            for claim_id in selected_claim_ids
            for contradicted_id in claim_by_id[claim_id].contradicts
        }
        missing_contradictions = outgoing - set(claim_by_id)
        if missing_contradictions:
            raise ValueError(
                "Selected claims contradict unknown claims: "
                + ", ".join(sorted(missing_contradictions))
            )
        selected_keys = {
            claim_by_id[claim_id].assertion_key
            for claim_id in selected_claim_ids
        }
        additions = {
            claim.id
            for claim in claim_objects
            if claim.id in outgoing
            or claim.assertion_key in selected_keys
            or any(selected_id in claim.contradicts for selected_id in selected_claim_ids)
        }
        expanded = selected_claim_ids | additions
        if expanded == selected_claim_ids:
            break
        selected_claim_ids = expanded

    selected_claims = sorted(
        (claim_by_id[claim_id] for claim_id in selected_claim_ids),
        key=lambda item: item.id,
    )
    for claim in selected_claims:
        if _is_forbidden_model_field(claim.predicate):
            raise ValueError(
                f"Review packet contains forbidden model predicate {claim.predicate!r}"
            )

    link_objects = [
        item if isinstance(item, EvidenceLink) else EvidenceLink.from_dict(item)
        for item in evidence_links
    ]
    link_by_id: dict[str, EvidenceLink] = {}
    for link in link_objects:
        if not link.id.strip() or not link.claim_id.strip():
            raise ValueError("Evidence links require stable id and claim_id fields")
        if link.id in link_by_id:
            raise ValueError(f"Duplicate evidence link id {link.id}")
        if link.claim_id not in claim_by_id:
            raise ValueError(f"Evidence link {link.id} references unknown claim {link.claim_id}")
        link_by_id[link.id] = link

    selected_evidence_ids: set[str] = set()
    for claim in selected_claims:
        for evidence_id in claim.evidence_ids:
            link = link_by_id.get(evidence_id)
            if link is None:
                raise ValueError(
                    f"Selected claim {claim.id} references unknown evidence link {evidence_id}"
                )
            if link.claim_id != claim.id:
                raise ValueError(
                    f"Evidence link {evidence_id} belongs to {link.claim_id}, not {claim.id}"
                )
            selected_evidence_ids.add(evidence_id)
    for link in link_objects:
        if (
            link.claim_id in selected_claim_ids
            and link.id not in claim_by_id[link.claim_id].evidence_ids
        ):
            raise ValueError(
                f"Evidence link {link.id} is not referenced by claim {link.claim_id}"
            )
    selected_links = [link_by_id[item] for item in sorted(selected_evidence_ids)]

    packet: dict[str, Any] = {
        "format_version": "1.0",
        "blinded": not include_prior_decisions,
        "prior_decisions_included": include_prior_decisions,
        "leaderboard_effects_included": False,
        "events": selected_events,
        "claims": [claim.to_dict() for claim in selected_claims],
        "evidence_links": [link.to_dict() for link in selected_links],
        "disagreements": find_disagreements(selected_claims),
    }
    if include_prior_decisions:
        decision_objects = [
            item if isinstance(item, Adjudication) else Adjudication.from_dict(item)
            for item in adjudications
        ]
        history_errors = adjudication_history_errors(decision_objects)
        if history_errors:
            raise ValueError(
                "Invalid append-only adjudication history: " + "; ".join(history_errors)
            )
        unknown_decision_claims = {
            item.claim_id for item in decision_objects if item.claim_id not in claim_by_id
        }
        if unknown_decision_claims:
            raise ValueError(
                "Adjudications reference unknown claims: "
                + ", ".join(sorted(unknown_decision_claims))
            )
        for item in decision_objects:
            if _FORBIDDEN_MODEL_OUTPUT_TEXT.search(item.rationale):
                raise ValueError(
                    f"Adjudication {item.id} rationale contains a forbidden model output"
                )
        packet["adjudications"] = [
            item.to_dict()
            for item in decision_objects
            if item.claim_id in selected_claim_ids
        ]

    for payload_name in ("events", "claims", "evidence_links", "adjudications"):
        if payload_name not in packet:
            continue
        forbidden = _find_forbidden_key(packet[payload_name], f"$.{payload_name}")
        if forbidden:
            path, key = forbidden
            raise ValueError(
                f"Review packet contains forbidden model field {key!r} at {path}"
            )
    return canonicalize_json(packet)
