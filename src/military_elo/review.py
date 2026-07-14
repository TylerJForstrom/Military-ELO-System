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
import ipaddress
import math
import random
import re
from collections import defaultdict
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import urlparse

from .canonical import (
    CanonicalEvent,
    ParticipationEpisode,
    UncertainDateInterval,
    date_bounds,
    geometry_validation_error,
)
from .claims import (
    CLAIM_STATUSES,
    Claim,
    EvidenceLink,
    canonical_json,
    canonicalize_json,
    find_disagreements,
)


_ADJUDICATION_FIELDS = frozenset(
    {
        "id",
        "claim_id",
        "reviewer",
        "decision",
        "rationale",
        "codebook_version",
        "supersedes",
        "reviewed_at",
        "review_stage",
        "evidence_ids_considered",
        "blind_review",
        "confidence",
    }
)
_ADJUDICATION_REQUIRED_FIELDS = frozenset(
    {
        "id",
        "claim_id",
        "reviewer",
        "decision",
        "rationale",
        "codebook_version",
        "supersedes",
    }
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
        for field_name in (
            "id",
            "claim_id",
            "reviewer",
            "decision",
            "rationale",
            "codebook_version",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"Adjudication.{field_name} must be a string")
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
        if len(supersedes) != len(set(supersedes)):
            raise ValueError("Adjudication.supersedes must contain unique ids")
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError(
                "Adjudication.evidence_ids_considered must contain unique ids"
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
        if not isinstance(raw, dict):
            raise TypeError("Adjudication must be a JSON object")
        if any(not isinstance(key, str) for key in raw):
            raise TypeError("Adjudication object keys must be strings")
        unknown = sorted(set(raw) - _ADJUDICATION_FIELDS)
        if unknown:
            raise ValueError(
                "Adjudication contains unknown field(s): " + ", ".join(unknown)
            )
        missing = sorted(_ADJUDICATION_REQUIRED_FIELDS - set(raw))
        if missing:
            raise ValueError(
                "Adjudication is missing required field(s): " + ", ".join(missing)
            )

        def required_text(name: str) -> str:
            value = raw[name]
            if not isinstance(value, str):
                raise TypeError(f"Adjudication.{name} must be a string")
            if not value.strip():
                raise ValueError(f"Adjudication.{name} must be non-blank")
            return value

        def optional_text(name: str) -> str:
            value = raw[name] if name in raw else ""
            if not isinstance(value, str):
                raise TypeError(f"Adjudication.{name} must be a string")
            return value

        def nonblank_id_array(name: str) -> list[str]:
            value = raw[name] if name in raw else []
            if not isinstance(value, list):
                raise TypeError(
                    f"Adjudication.{name} must be an array of stable ids"
                )
            for item in value:
                if not isinstance(item, str):
                    raise TypeError(
                        f"Adjudication.{name} must contain string ids"
                    )
                if not item.strip():
                    raise ValueError(
                        f"Adjudication.{name} must contain non-blank ids"
                    )
            if len(value) != len(set(value)):
                raise ValueError(f"Adjudication.{name} must contain unique ids")
            return value

        supersedes_raw = nonblank_id_array("supersedes")
        evidence_ids_raw = nonblank_id_array("evidence_ids_considered")
        blind_review_raw = raw.get("blind_review")
        if blind_review_raw is not None and not isinstance(blind_review_raw, bool):
            raise TypeError("Adjudication.blind_review must be a boolean or null")
        review_stage_raw = raw.get("review_stage")
        if review_stage_raw is not None and not isinstance(review_stage_raw, str):
            raise TypeError("Adjudication.review_stage must be a string or null")
        if isinstance(review_stage_raw, str) and not review_stage_raw.strip():
            raise ValueError(
                "Adjudication.review_stage must be non-blank when supplied"
            )
        confidence_raw = raw.get("confidence")
        if confidence_raw is not None and (
            isinstance(confidence_raw, bool)
            or not isinstance(confidence_raw, (int, float))
        ):
            raise TypeError("Adjudication.confidence must be a number or null")
        if confidence_raw is not None and not 0 <= confidence_raw <= 1:
            raise ValueError("Adjudication.confidence must be in 0..1")
        return cls(
            id=required_text("id"),
            claim_id=required_text("claim_id"),
            reviewer=required_text("reviewer"),
            decision=required_text("decision"),
            rationale=required_text("rationale"),
            codebook_version=required_text("codebook_version"),
            supersedes=tuple(supersedes_raw),
            reviewed_at=optional_text("reviewed_at"),
            review_stage=review_stage_raw,
            evidence_ids_considered=tuple(evidence_ids_raw),
            blind_review=blind_review_raw,
            confidence=confidence_raw,
        )


def adjudication_history_errors(
    adjudications: Iterable[Adjudication],
) -> list[str]:
    """Validate ordering and referential rules for an append-only history."""

    if isinstance(adjudications, (set, frozenset)):
        raise TypeError("adjudication history must be an ordered iterable")
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
        if not isinstance(item.reviewed_at, str):
            errors.append(
                f"decision at position {index} requires string reviewed_at"
            )
        if item.review_stage is not None and (
            not isinstance(item.review_stage, str) or not item.review_stage.strip()
        ):
            errors.append(
                f"decision at position {index} requires non-blank review_stage when supplied"
            )
        for field_name, values in (
            ("supersedes", item.supersedes),
            ("evidence_ids_considered", item.evidence_ids_considered),
        ):
            if any(not isinstance(value, str) or not value.strip() for value in values):
                errors.append(
                    f"decision at position {index} {field_name} must contain non-blank string ids"
                )
        if item.confidence is not None and (
            isinstance(item.confidence, bool)
            or not isinstance(item.confidence, (int, float))
            or not math.isfinite(item.confidence)
            or not 0 <= item.confidence <= 1
        ):
            errors.append(
                f"decision at position {index} confidence must be finite and in 0..1"
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

    if isinstance(history, (set, frozenset)):
        raise TypeError("adjudication history must be an ordered iterable")
    result = tuple(history) + (decision,)
    errors = adjudication_history_errors(result)
    if errors:
        raise ValueError("Invalid append-only adjudication: " + "; ".join(errors))
    return result


def active_adjudications(
    history: Iterable[Adjudication],
) -> tuple[Adjudication, ...]:
    """Return every unsuperseded leaf, retaining parallel reviewer decisions."""

    if isinstance(history, (set, frozenset)):
        raise TypeError("adjudication history must be an ordered iterable")
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

    if isinstance(adjudications, (set, frozenset)):
        raise TypeError("adjudication history must be an ordered iterable")
    claim_list = list(claims)
    history = list(adjudications)
    errors = adjudication_history_errors(history)
    if errors:
        raise ValueError("Invalid adjudication history: " + "; ".join(errors))
    claim_by_id: dict[str, Claim] = {}
    for claim in claim_list:
        _validate_claim_structure(claim)
        if claim.id in claim_by_id:
            raise ValueError(f"Claims require unique stable ids: {claim.id!r}")
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
        value = record.get(id_field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Every sampled record requires explicit id field {id_field!r}")
        return value
    candidates = ["id", "candidate_id", "event_id", "claim_id"]
    for name in candidates:
        value = record.get(name)
        if value is not None:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Sampling id field {name!r} must be a non-blank string")
            return value
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
                bounds = date_bounds(value)
                if bounds is not None:
                    return bounds[0][0]
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
    _validate_sample_size(sample_size)
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")
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


def _validate_sample_size(sample_size: Any) -> None:
    if isinstance(sample_size, bool) or not isinstance(sample_size, int):
        raise TypeError("sample_size must be an integer")
    if sample_size < 0:
        raise ValueError("sample_size must be nonnegative")


def _normalize_stratify_by(value: Any) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, Mapping, set, frozenset)):
        raise TypeError("stratify_by must be an ordered sequence of field names")
    try:
        fields = tuple(value)
    except TypeError as error:
        raise TypeError(
            "stratify_by must be an ordered sequence of field names"
        ) from error
    if any(not isinstance(item, str) for item in fields):
        raise TypeError("stratify_by must contain only strings")
    if any(not item.strip() for item in fields):
        raise ValueError("stratify_by must contain only non-blank field names")
    if len(fields) != len(set(fields)):
        raise ValueError("stratify_by field names must be unique")
    return fields


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

    _validate_sample_size(sample_size)
    stratify_fields = _normalize_stratify_by(stratify_by)
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    population = [canonicalize_json(deepcopy(record)) for record in records]
    if sample_size > len(population):
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
        key = tuple(_stratum_value(record, name) for name in stratify_fields)
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
    _validate_sample_size(sample_size)
    stratify_fields = _normalize_stratify_by(stratify_by)
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    population = [canonicalize_json(deepcopy(record)) for record in records]
    selected = sample_gold_set(
        population,
        sample_size,
        seed=seed,
        stratify_by=stratify_fields,
        id_field=id_field,
    )

    def counts(values: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, ...], int] = defaultdict(int)
        for record in values:
            grouped[
                tuple(_stratum_value(record, name) for name in stratify_fields)
            ] += 1
        return [
            {
                "stratum": dict(zip(stratify_fields, key)),
                "count": grouped[key],
            }
            for key in sorted(grouped)
        ]

    population_manifest = [
        {
            "id": _record_id(record, id_field),
            "stratum": {
                name: _stratum_value(record, name)
                for name in stratify_fields
            },
        }
        for record in sorted(population, key=lambda item: _record_id(item, id_field))
    ]
    selected_ids = {_record_id(record, id_field) for record in selected}
    selected_manifest = [
        item for item in population_manifest if item["id"] in selected_ids
    ]
    canonical_population = sorted(
        population,
        key=lambda item: _record_id(item, id_field),
    )
    population_digest = hashlib.sha256(
        canonical_json(canonical_population).encode("utf-8")
    ).hexdigest()

    return {
        "format_version": "1.0",
        "seed": seed,
        "population_digest": f"sha256:{population_digest}",
        "id_field": id_field or "auto",
        "population_size": len(population),
        "sample_size": len(selected),
        "stratify_by": list(stratify_fields),
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

_MODEL_METRIC_LABEL_KEYS = {
    "field",
    "indicator",
    "measure",
    "metric",
    "output",
    "score_type",
    "statistic",
    "variable",
}
_LOCATOR_CHECKSUM_PATTERN = re.compile(r"^(?:sha256:)?[0-9a-fA-F]{64}$")
_LOCATOR_URL_PATTERN = re.compile(r"^https?://[^\s]+$")
_EVIDENCE_RELATIONSHIPS = {"supports", "contradicts", "context"}
_FINITE_NUMBER_TEXT = re.compile(
    r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$"
)
_COMMA_NUMBER_TEXT = re.compile(
    r"^[+-]?[0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$"
)
_NONFINITE_NUMBER_TEXT = re.compile(r"^[+-]?(?:nan|inf(?:inity)?)$", re.IGNORECASE)
_KNOWN_METRIC_PLURALS = {
    "deltas": "delta",
    "effects": "effect",
    "leaderboards": "leaderboard",
    "outputs": "output",
    "points": "point",
    "probabilities": "probability",
    "rankings": "ranking",
    "ranks": "rank",
    "ratings": "rating",
    "scores": "score",
}
_RANK_TITLE_TOKENS = {
    "admiral",
    "captain",
    "colonel",
    "commander",
    "corporal",
    "ensign",
    "general",
    "lieutenant",
    "major",
    "marshal",
    "officer",
    "private",
    "sergeant",
}
_MODEL_SECONDARY_TOKENS = {
    "assigned",
    "derived",
    "effect",
    "expected",
    "factor",
    "output",
    "placed",
    "point",
    "position",
    "predicted",
    "prediction",
    "probability",
    "rank",
    "ranking",
    "rating",
    "result",
    "score",
}
_FORBIDDEN_COMPACT_FIELDS = {
    "compositerating",
    "coveragefactor",
    "effectiveevents",
    "effectivewars",
    "entityrating",
    "evidenceweight",
    "expectation",
    "expectedscore",
    "historicalsuccess",
    "historicalsuccessindex",
    "historicalsuccessraw",
    "kfactor",
    "modeleffect",
    "modeloutput",
    "modelscore",
    "operationalrating",
    "ratingdelta",
    "ratingeffect",
    "strategicrating",
    "tacticalrating",
    "top10probability",
    "winprobability",
}
_NON_SEMANTIC_REFERENCE_FIELDS = {
    "adjudication_ids",
    "child_event_ids",
    "claim_id",
    "claim_ids",
    "claim_group_id",
    "codebook_version",
    "creator",
    "checksum",
    "contradicts",
    "entity_id",
    "edition",
    "event_id",
    "evidence_ids",
    "evidence_ids_considered",
    "id",
    "language",
    "page",
    "parent_event_id",
    "parent_event_ids",
    "source_id",
    "source_ids",
    "source_family",
    "subject",
    "supersedes",
    "row",
    "review_stage",
    "reviewed_at",
    "reviewer",
    "decision",
    "url",
}
_CLAIM_METADATA_FIELDS = {
    "claim_group_id",
    "contradicts",
    "evidence_ids",
    "exclusive",
    "id",
    "impact",
    "predicate",
    "status",
    "subject",
}
_REFERENCE_ARRAY_FIELDS = {
    "adjudication_ids",
    "child_event_ids",
    "claim_ids",
    "contradicts",
    "evidence_ids",
    "evidence_ids_considered",
    "parent_event_ids",
    "source_ids",
    "supersedes",
}


def _normalized_metric_tokens(value: str) -> tuple[str, ...]:
    separated = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", value)
    separated = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", separated)
    separated = re.sub(
        r"(?i)(?<![a-z0-9])e[^a-z0-9]*l[^a-z0-9]*o(?![a-z0-9])",
        " elo ",
        separated,
    )
    raw_tokens = re.findall(r"[a-z]+|[0-9]+", separated.lower())
    tokens: list[str] = []
    index = 0
    while index < len(raw_tokens):
        if raw_tokens[index : index + 2] == ["leader", "board"]:
            tokens.append("leaderboard")
            index += 2
            continue
        token = _KNOWN_METRIC_PLURALS.get(raw_tokens[index], raw_tokens[index])
        compact_expansions = {
            "coveragefactor": ("coverage", "factor"),
            "elorank": ("elo", "rank"),
            "eloranking": ("elo", "ranking"),
            "elorating": ("elo", "rating"),
            "eloscore": ("elo", "score"),
            "entityratings": ("entity", "rating"),
            "expectedscore": ("expected", "score"),
            "kfactor": ("k", "factor"),
            "leaderboardrank": ("leaderboard", "rank"),
            "leaderboardranking": ("leaderboard", "ranking"),
            "modelprediction": ("model", "prediction"),
            "modelrank": ("model", "rank"),
            "modelranking": ("model", "ranking"),
            "modelrating": ("model", "rating"),
            "modelscore": ("model", "score"),
            "top10probability": ("top", "10", "probability"),
            "winprobability": ("win", "probability"),
        }
        tokens.extend(compact_expansions.get(token, (token,)))
        index += 1
    return tuple(tokens)


def _reference_nested_payloads(field_name: str, value: Any) -> list[Any]:
    """Return only non-scalar payloads that still require leakage scanning.

    Stable reference strings never establish semantic context.  Reference
    arrays likewise ignore their scalar ID members, while malformed nested
    containers remain recursively inspectable and fail closed on model output.
    """

    if field_name in _REFERENCE_ARRAY_FIELDS and isinstance(value, (list, tuple)):
        return [item for item in value if isinstance(item, (Mapping, list, tuple))]
    if isinstance(value, (Mapping, list, tuple)):
        return [value]
    return []


def _named_geographic_delta_tokens(tokens: set[str]) -> bool:
    if "delta" not in tokens or len(tokens) < 2:
        return False
    forbidden_companions = {
        "after",
        "before",
        "change",
        "effect",
        "elo",
        "leaderboard",
        "metric",
        "model",
        "negative",
        "output",
        "positive",
        "rank",
        "ranking",
        "rating",
        "score",
        "value",
    }
    return bool(tokens - ({"delta"} | forbidden_companions)) and not bool(
        tokens & forbidden_companions
    )


def _historical_metric_kinds(tokens: set[str]) -> set[str]:
    if "elo" in tokens or "leaderboard" in tokens:
        return set()
    if "model" in tokens and tokens & _MODEL_SECONDARY_TOKENS:
        return set()
    if tokens & {"composite", "operational", "sensitivity", "strategic", "tactical"}:
        return set()
    kinds: set[str] = set()
    if "rank" in tokens:
        if tokens & (
            {
                "command",
                "commander",
                "formation",
                "military",
                "named",
                "officer",
                "organizational",
                "service",
                "unit",
            }
            | _RANK_TITLE_TOKENS
        ):
            kinds.add("rank")
    if "rating" in tokens:
        if tokens & {"naval", "ship", "vessel"}:
            kinds.add("rating")
    if "delta" in tokens and tokens & {
        "area",
        "danube",
        "estuary",
        "feature",
        "geographic",
        "geography",
        "location",
        "nile",
        "region",
        "river",
    }:
        kinds.add("delta")
    return kinds


def _historical_metric_kind(tokens: set[str]) -> str | None:
    kinds = _historical_metric_kinds(tokens)
    return sorted(kinds)[0] if kinds else None


def _is_historical_metric_semantics(tokens: set[str]) -> bool:
    return bool(_historical_metric_kinds(tokens))


def _is_forbidden_model_field(value: str) -> bool:
    if not isinstance(value, str):
        return False
    token_tuple = _normalized_metric_tokens(value)
    tokens = set(token_tuple)
    if not tokens or _is_historical_metric_semantics(tokens):
        return False
    if _named_geographic_delta_tokens(tokens):
        return False
    compact = "".join(token_tuple)
    if compact in _FORBIDDEN_COMPACT_FIELDS:
        return True
    if "elo" in tokens or "leaderboard" in tokens:
        return True
    if "model" in tokens:
        return bool(tokens & _MODEL_SECONDARY_TOKENS)
    if tokens & {"rank", "ranking", "rating", "sensitivity"}:
        return True
    if "delta" in tokens:
        return True
    if "expected" in tokens and tokens & {"probability", "score"}:
        return True
    if "win" in tokens and "probability" in tokens:
        return True
    if "top" in tokens and "probability" in tokens:
        return True
    if compact in {"kfactor", "coveragefactor"}:
        return True
    normalized_forbidden = {
        "".join(_normalized_metric_tokens(item))
        for item in FORBIDDEN_MODEL_OUTPUT_KEYS
    }
    return compact in normalized_forbidden


def _metric_label_kinds(value: Any) -> set[str]:
    if not isinstance(value, str):
        return set()
    token_tuple = _normalized_metric_tokens(value)
    tokens = set(token_tuple)
    if (
        not tokens
        or _is_historical_metric_semantics(tokens)
        or _named_geographic_delta_tokens(tokens)
    ):
        return set()
    kinds: set[str] = set()
    for kind in ("elo", "leaderboard", "model", "rank", "ranking", "rating", "delta"):
        if kind in tokens:
            kinds.add("rank" if kind == "ranking" else kind)
    for kind in (
        "effect",
        "factor",
        "output",
        "point",
        "position",
        "predicted",
        "prediction",
        "probability",
        "result",
        "score",
    ):
        if kind in tokens:
            kinds.add(kind)
    if "expected" in tokens and tokens & {"probability", "score"}:
        kinds.add("expected")
    compact = "".join(token_tuple)
    if compact in _FORBIDDEN_COMPACT_FIELDS:
        kinds.add("output")
    return kinds


def _model_metric_label(value: Any) -> str | None:
    return value if isinstance(value, str) and _metric_label_kinds(value) else None


def _is_finite_number_value(value: Any) -> bool:
    if not isinstance(value, bool) and isinstance(value, (int, float)):
        return math.isfinite(value)
    if isinstance(value, str) and _FINITE_NUMBER_TEXT.fullmatch(value.strip()):
        try:
            return math.isfinite(float(value))
        except ValueError:
            return False
    return False


def _is_model_value_like(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if _is_finite_number_value(value):
        return True
    if not isinstance(value, str):
        return False
    text = value.strip()
    if bool(
        _COMMA_NUMBER_TEXT.fullmatch(text)
        or _NONFINITE_NUMBER_TEXT.fullmatch(text)
    ):
        return True
    return bool(
        re.fullmatch(
            r"(?i)(?:bottom|first|higher|last|lower|second|third|top|"
            r"[0-9]+(?:st|nd|rd|th)?|position\s+(?:first|second|third|last))",
            text,
        )
    )


def _contains_forbidden_model_output_text(value: str) -> bool:
    prepared = re.sub(
        r"(?i)(?<![a-z0-9])e[^a-z0-9]*l[^a-z0-9]*o(?![a-z0-9])",
        " ELO ",
        value,
    )
    if re.search(
        r"(?i)\b(?:deltas?|ranks?|rankings?|ratings?)\s*[:=]\s*"
        r"(?:[+-]?(?:[0-9]+(?:[,.][0-9]+)*|nan|inf(?:inity)?)|"
        r"(?:bottom|first|higher|last|lower|second|third|top)"
        r"(?!\s+(?:lieutenant|sergeant|officer|rate)))\b",
        prepared,
    ):
        return True
    for clause in re.split(r"[:;\r\n,.!?]+", prepared):
        token_tuple = _normalized_metric_tokens(clause)
        tokens = set(token_tuple)
        if not tokens:
            continue
        historical_kinds = _historical_metric_kinds(tokens)
        if "elo" in tokens or "leaderboard" in tokens:
            return True
        if "model" in tokens and (
            tokens & _MODEL_SECONDARY_TOKENS
            or ("placed" in tokens and tokens & {"first", "second", "third", "last"})
        ):
            return True
        compact = "".join(token_tuple)
        if compact in _FORBIDDEN_COMPACT_FIELDS:
            return True
        if (
            ("expected" in tokens and tokens & {"probability", "score"})
            or ("win" in tokens and "probability" in tokens)
            or ("top" in tokens and "probability" in tokens)
            or ({"k", "factor"} <= tokens)
            or ({"coverage", "factor"} <= tokens)
        ):
            return True
        metric_tokens = {
            "rank" if token == "ranking" else token
            for token in tokens & {"delta", "rank", "ranking", "rating"}
        }
        metric_tokens -= historical_kinds
        if not metric_tokens:
            continue
        output_cues = {
            "advantage",
            "equal",
            "equals",
            "favored",
            "favoured",
            "higher",
            "lower",
            "point",
            "score",
            "stood",
        }
        if "ranking" in tokens or tokens & output_cues:
            return True
        if any(_is_model_value_like(token) for token in token_tuple):
            return True
    return False


def _json_scalar_values(value: Any) -> list[Any]:
    scalars: list[Any] = []
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, Mapping):
            pending.extend(item.values())
        elif isinstance(item, (list, tuple)):
            pending.extend(item)
        else:
            scalars.append(item)
    return scalars


def _paired_model_metric_label(
    value: Any,
    historical_context: frozenset[str] = frozenset(),
) -> str | None:
    if not isinstance(value, (Mapping, list, tuple)):
        return None
    labels: list[str] = []
    pending = [value]
    kinds: set[str] = set()
    scalar_values: list[Any] = []
    while pending:
        item = pending.pop()
        if isinstance(item, Mapping):
            for key, child in item.items():
                normalized_key = "_".join(_normalized_metric_tokens(key))
                if normalized_key in _NON_SEMANTIC_REFERENCE_FIELDS:
                    pending.extend(
                        _reference_nested_payloads(normalized_key, child)
                    )
                    continue
                labels.append(str(key))
                kinds.update(_metric_label_kinds(key))
                pending.append(child)
        elif isinstance(item, (list, tuple)):
            pending.extend(item)
        else:
            scalar_values.append(item)
            if isinstance(item, str):
                labels.append(item)
                kinds.update(_metric_label_kinds(item))
    if not any(_is_model_value_like(item) for item in scalar_values):
        return None
    if "elo" in kinds or "leaderboard" in kinds:
        return next((item for item in labels if _metric_label_kinds(item)), "model output")
    if "model" in kinds and kinds & _MODEL_SECONDARY_TOKENS:
        return next((item for item in labels if _metric_label_kinds(item)), "model output")
    for kind in ("rank", "rating", "delta"):
        if kind in kinds and kind not in historical_context:
            return next(
                (item for item in labels if kind in _metric_label_kinds(item)),
                kind,
            )
    if kinds & {
        "expected",
        "factor",
        "output",
        "predicted",
        "prediction",
        "probability",
        "score",
    }:
        return next((item for item in labels if _metric_label_kinds(item)), "model output")
    return None


def _obvious_historical_rank_value(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    text = value.strip()
    if _is_model_value_like(text):
        return False
    if re.fullmatch(r"(?i)(?:no\.?\s*)?[0-9]+(?:st|nd|rd|th)?", text):
        return False
    return _model_metric_label(text) is None


def _obvious_historical_rating_value(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return bool(
        re.fullmatch(
            r"(?i)(?:first|second|third|fourth|fifth|sixth)(?:\s+rate)?",
            value.strip(),
        )
    )


def _obvious_historical_delta_value(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and not _is_model_value_like(value)
        and _model_metric_label(value) is None
    )


def _validate_packet_locator(locator: Any, owner_id: str) -> None:
    for field_name in ("source_id", "edition", "checksum", "language", "source_family"):
        value = getattr(locator, field_name, None)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{owner_id} source locator requires non-blank {field_name}"
            )
    for field_name in ("creator", "citation"):
        if not isinstance(getattr(locator, field_name, None), str):
            raise ValueError(f"{owner_id} source locator {field_name} must be a string")
    for field_name in ("page", "row"):
        value = getattr(locator, field_name, None)
        if value is not None and (
            isinstance(value, bool)
            or not isinstance(value, (str, int))
            or (isinstance(value, str) and not value.strip())
        ):
            raise ValueError(
                f"{owner_id} source locator {field_name} must be a non-blank string or integer"
            )

    url = getattr(locator, "url", None)
    if url is not None:
        if not locator_url_is_valid(url):
            raise ValueError(
                f"{owner_id} source locator URL must be an absolute HTTP(S) URL"
            )
    if not getattr(locator, "has_exact_anchor", False):
        raise ValueError(f"{owner_id} source locator requires a page, row, or URL")
    if not _LOCATOR_CHECKSUM_PATTERN.fullmatch(locator.checksum):
        raise ValueError(f"{owner_id} source locator checksum must be a SHA-256 digest")


def locator_url_is_valid(value: Any) -> bool:
    """Validate a conservative absolute HTTP(S) evidence-locator URL."""

    if (
        not isinstance(value, str)
        or re.search(r"[\x00-\x20\x7f]", value)
        or not _LOCATOR_URL_PATTERN.fullmatch(value)
    ):
        return False
    try:
        parsed = urlparse(value)
        hostname = parsed.hostname
        parsed.port
    except ValueError:
        return False
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or not hostname
        or parsed.netloc.endswith(":")
    ):
        return False
    if ":" in hostname:
        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            return False
        return True
    labels = hostname.split(".")
    return all(
        label
        and len(label) <= 63
        and not label.startswith("-")
        and not label.endswith("-")
        and re.fullmatch(r"[A-Za-z0-9-]+", label) is not None
        for label in labels
    )


def _validate_claim_structure(claim: Claim) -> None:
    for field_name in ("id", "subject", "predicate"):
        value = getattr(claim, field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Claim requires non-blank {field_name}")
    if claim.status not in CLAIM_STATUSES:
        raise ValueError(
            f"Claim {claim.id} has invalid lifecycle status {claim.status!r}"
        )
    if claim.claim_group_id is not None and not claim.claim_group_id.strip():
        raise ValueError(f"Claim {claim.id} has a blank claim_group_id")
    if claim.exclusive is True and claim.claim_group_id is None:
        raise ValueError(f"Exclusive claim {claim.id} requires claim_group_id")
    if claim.impact not in (None, "ordinary", "high"):
        raise ValueError(f"Claim {claim.id} has invalid impact {claim.impact!r}")
    for field_name, values in (
        ("contradicts", claim.contradicts),
        ("evidence_ids", claim.evidence_ids),
    ):
        if any(not isinstance(item, str) or not item.strip() for item in values):
            raise ValueError(
                f"Claim {claim.id} {field_name} must contain non-blank ids"
            )
    if claim.id in claim.contradicts:
        raise ValueError(f"Claim {claim.id} cannot contradict itself")
    if not claim.provenance and not claim.evidence_ids:
        raise ValueError(
            f"Claim {claim.id} requires provenance or an evidence link"
        )
    for locator in claim.provenance:
        _validate_packet_locator(locator, claim.id)


def _validate_packet_evidence_link(link: EvidenceLink) -> None:
    for field_name in ("id", "claim_id", "source_family"):
        value = getattr(link, field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Evidence links require non-blank {field_name}")
    if link.relationship not in _EVIDENCE_RELATIONSHIPS:
        raise ValueError(
            f"Evidence link {link.id} relationship must be supports, contradicts, or context"
        )
    if link.source_family != link.locator.source_family:
        raise ValueError(
            f"Evidence link {link.id} and locator source families differ"
        )
    _validate_packet_locator(link.locator, link.id)


def _validate_packet_geometry(geometry: Any, event_id: str) -> None:
    if geometry is None:
        return
    error = geometry_validation_error(geometry)
    if error is not None:
        raise ValueError(
            f"Review packet event {event_id} has invalid geometry: {error}"
        )


def _uncertain_date_envelope(value: Any) -> tuple[tuple[int, int, int], tuple[int, int, int]] | None:
    bounds = [
        date_bounds(candidate)
        for candidate in (value.low, value.best, value.high)
        if candidate is not None
    ]
    valid = [item for item in bounds if item is not None]
    if not valid:
        return None
    return (min(item[0] for item in valid), max(item[1] for item in valid))


def _date_interval_envelope(
    interval: UncertainDateInterval | None,
) -> tuple[tuple[int, int, int], tuple[int, int, int]] | None:
    if interval is None:
        return None
    start = _uncertain_date_envelope(interval.start)
    end = _uncertain_date_envelope(interval.end)
    if start is None or end is None:
        return None
    return (start[0], end[1])


def _legacy_year_interval(raw: Mapping[str, Any]) -> UncertainDateInterval | None:
    if "year" not in raw:
        return None
    year = raw["year"]
    end_year = raw.get("end_year", year)
    for field_name, value in (("year", year), ("end_year", end_year)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Review event {field_name} must be an integer")
    interval = UncertainDateInterval.from_dict(
        {
            "start": {
                "low": year,
                "best": year,
                "high": year,
                "precision": "year",
            },
            "end": {
                "low": end_year,
                "best": end_year,
                "high": end_year,
                "precision": "year",
            },
        }
    )
    errors = interval.validation_errors()
    if errors:
        raise ValueError(
            "Review event has invalid year/end_year: " + "; ".join(errors)
        )
    return interval


def _validate_event_evidence_view(event: dict[str, Any]) -> CanonicalEvent:
    canonical_event = CanonicalEvent.from_dict(event)
    if canonical_event.date_interval is not None:
        errors = canonical_event.date_interval.validation_errors()
        if errors:
            raise ValueError(
                f"Review packet event {canonical_event.id} has an invalid date interval: "
                + "; ".join(errors)
            )
    _validate_packet_geometry(canonical_event.geometry, canonical_event.id)
    for episode in canonical_event.participation_episodes:
        errors = episode.validation_errors()
        if errors:
            raise ValueError(
                f"Participation episode {episode.id} is invalid: " + "; ".join(errors)
            )
        event_bounds = _date_interval_envelope(canonical_event.date_interval)
        for label, point in (("entry", episode.entry), ("exit", episode.exit)):
            point_bounds = (
                _uncertain_date_envelope(point) if point is not None else None
            )
            if (
                event_bounds is not None
                and point_bounds is not None
                and (
                    point_bounds[1] < event_bounds[0]
                    or point_bounds[0] > event_bounds[1]
                )
            ):
                raise ValueError(
                    f"Participation episode {episode.id} {label} does not overlap "
                    f"event {canonical_event.id}'s date interval"
                )
    return canonical_event


def _event_evidence_view(event: CanonicalEvent | dict[str, Any]) -> dict[str, Any]:
    if isinstance(event, dict):
        raw = canonicalize_json(deepcopy(event))
        if isinstance(raw.get("canonical_event"), dict):
            raw = raw["canonical_event"]
    elif hasattr(event, "to_dict") and callable(event.to_dict):
        raw = canonicalize_json(event.to_dict())
    else:
        raise TypeError("Review packet events must be objects or event model instances")
    for canonical_name, alias in (("id", "event_id"), ("name", "canonical_name")):
        if canonical_name in raw and alias in raw:
            raise ValueError(
                f"Review event cannot contain both {canonical_name} and {alias}"
            )
        if canonical_name not in raw and alias in raw:
            raw[canonical_name] = raw[alias]
    legacy_interval = _legacy_year_interval(raw)
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

    explicit_episodes = "participation_episodes" in raw
    if explicit_episodes:
        episodes = raw["participation_episodes"]
    elif "participants" in raw:
        episodes = raw["participants"]
    else:
        episodes = None
    if episodes is not None:
        if not isinstance(episodes, list):
            raise ValueError("participation_episodes must be an array")
        normalized_episodes: list[dict[str, Any]] = []
        episode_ids: set[str] = set()
        legacy_fingerprint_counts: dict[str, int] = defaultdict(int)
        for episode in episodes:
            if not isinstance(episode, dict):
                raise ValueError("participation_episodes must contain objects")
            if explicit_episodes:
                missing = [
                    name
                    for name in ("entity_id", "side", "role")
                    if name not in episode
                ]
                if "id" not in episode and "episode_id" not in episode:
                    missing.insert(0, "id")
                if missing:
                    raise ValueError(
                        "Explicit participation episode requires " + ", ".join(missing)
                    )
                normalized_episode = canonicalize_json(episode)
            else:
                normalized_episode = {
                    name: canonicalize_json(episode[name])
                    for name in _PARTICIPATION_FIELDS
                    if name in episode and episode[name] is not None
                }
                normalized_episode.setdefault("role", "unknown")
                for canonical_name, alias in (
                    ("entry", "entry_date"),
                    ("exit", "exit_date"),
                ):
                    if canonical_name in episode and alias in episode:
                        raise ValueError(
                            "Legacy participant cannot contain both "
                            f"{canonical_name} and {alias}"
                        )
                    if canonical_name not in normalized_episode and alias in episode:
                        normalized_episode[canonical_name] = canonicalize_json(
                            episode[alias]
                        )
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
            if not explicit_episodes and "id" not in normalized_episode:
                canonical_payload = ParticipationEpisode.from_dict(
                    {**normalized_episode, "id": "__pending_legacy_episode_id__"}
                ).to_dict()
                canonical_payload.pop("id", None)
                fingerprint = hashlib.sha256(
                    canonical_json(canonical_payload).encode("utf-8")
                ).hexdigest()
                legacy_fingerprint_counts[fingerprint] += 1
                ordinal = legacy_fingerprint_counts[fingerprint]
                normalized_episode = canonical_payload
                normalized_episode["id"] = (
                    f"{result['id']}:participant:{fingerprint}:{ordinal}"
                )
            parsed_episode = ParticipationEpisode.from_dict(normalized_episode)
            for field_name in ("id", "entity_id", "side", "role"):
                value = getattr(parsed_episode, field_name)
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(
                        f"Participation episode {field_name} must be a non-blank string"
                    )
            errors = parsed_episode.validation_errors()
            if errors:
                raise ValueError(
                    f"Participation episode {parsed_episode.id} is invalid: "
                    + "; ".join(errors)
                )
            episode_id = parsed_episode.id
            if episode_id in episode_ids:
                raise ValueError(f"Duplicate participation episode id {episode_id}")
            episode_ids.add(episode_id)
            normalized_episode = parsed_episode.to_dict()
            if "objectives" in normalized_episode:
                normalized_episode["objectives"] = sorted(
                    set(normalized_episode["objectives"])
                )
            normalized_episodes.append(normalized_episode)
        result["participation_episodes"] = sorted(
            normalized_episodes,
            key=canonical_json,
        )
    if "date_interval" not in result and legacy_interval is not None:
        result["date_interval"] = legacy_interval.to_dict()
    canonical_event = _validate_event_evidence_view(result)
    if canonical_event.date_interval is not None:
        result["date_interval"] = canonical_event.date_interval.to_dict()
        if legacy_interval is not None:
            legacy_bounds = _date_interval_envelope(legacy_interval)
            evidence_bounds = _date_interval_envelope(canonical_event.date_interval)
            if (
                legacy_bounds is not None
                and evidence_bounds is not None
                and (
                    evidence_bounds[1] < legacy_bounds[0]
                    or evidence_bounds[0] > legacy_bounds[1]
                )
            ):
                raise ValueError(
                    f"Review event {canonical_event.id} date_interval does not "
                    "overlap legacy year/end_year"
                )
    return result


def _find_forbidden_key(
    value: Any,
    path: str = "$",
    historical_context: frozenset[str] = frozenset(),
    structured_pairing: bool = False,
) -> tuple[str, str] | None:
    if isinstance(value, dict):
        is_claim_record = {
            "id",
            "subject",
            "predicate",
            "value",
        }.issubset(value)
        local_context = set(historical_context)
        semantic_tokens: set[str] = set()
        if is_claim_record:
            context_items = (("predicate", value["predicate"]),)
        elif structured_pairing:
            context_items = value.items()
        else:
            context_items = ()
        for key, item in context_items:
            context_key = "_".join(_normalized_metric_tokens(key))
            if context_key in _NON_SEMANTIC_REFERENCE_FIELDS:
                continue
            for candidate in (key, item if isinstance(item, str) else None):
                if not isinstance(candidate, str):
                    continue
                semantic_tokens.update(_normalized_metric_tokens(candidate))
        if (
            semantic_tokens & {"elo", "leaderboard"}
            or (
                "model" in semantic_tokens
                and semantic_tokens & _MODEL_SECONDARY_TOKENS
            )
        ):
            local_context.clear()
        else:
            local_context.update(_historical_metric_kinds(semantic_tokens))
        if structured_pairing or "value" in value or "precision" in value:
            pairing_payload = (
                {
                    key: value[key]
                    for key in ("value", "precision")
                    if key in value
                }
                if "value" in value or "precision" in value
                else value
            )
            pairing_tokens: set[str] = set()
            pending = [pairing_payload]
            while pending:
                item = pending.pop()
                if isinstance(item, Mapping):
                    for nested_key, nested_value in item.items():
                        normalized_nested_key = "_".join(
                            _normalized_metric_tokens(nested_key)
                        )
                        if normalized_nested_key in _NON_SEMANTIC_REFERENCE_FIELDS:
                            pending.extend(
                                _reference_nested_payloads(
                                    normalized_nested_key,
                                    nested_value,
                                )
                            )
                            continue
                        pairing_tokens.update(_normalized_metric_tokens(nested_key))
                        pending.append(nested_value)
                elif isinstance(item, (list, tuple)):
                    pending.extend(item)
                elif isinstance(item, str):
                    pairing_tokens.update(_normalized_metric_tokens(item))
            pairing_context = set(local_context)
            if (
                pairing_tokens & {"elo", "leaderboard"}
                or (
                    "model" in pairing_tokens
                    and pairing_tokens & _MODEL_SECONDARY_TOKENS
                )
            ):
                pairing_context.clear()
            else:
                pairing_context.update(
                    _historical_metric_kinds(pairing_tokens)
                )
            paired_label = _paired_model_metric_label(
                pairing_payload,
                frozenset(pairing_context),
            )
            if paired_label is not None:
                return (path, paired_label)
        for key, item in value.items():
            normalized_key = "_".join(_normalized_metric_tokens(key))
            if is_claim_record and normalized_key in _CLAIM_METADATA_FIELDS:
                continue
            if is_claim_record and normalized_key not in {"value", "precision"}:
                found = _find_forbidden_key(
                    item,
                    f"{path}.{key}",
                    frozenset(),
                    False,
                )
                if found:
                    return found
                continue
            if normalized_key in _NON_SEMANTIC_REFERENCE_FIELDS:
                for nested_payload in _reference_nested_payloads(
                    normalized_key,
                    item,
                ):
                    found = _find_forbidden_key(
                        nested_payload,
                        f"{path}.{key}",
                        frozenset(),
                        structured_pairing,
                    )
                    if found:
                        return found
                continue
            if _is_forbidden_model_field(key):
                key_tokens = set(_normalized_metric_tokens(key))
                if not (
                    key_tokens == {"rank"}
                    and "rank" in local_context
                    and _obvious_historical_rank_value(item)
                ) and not (
                    key_tokens == {"rating"}
                    and "rating" in local_context
                    and _obvious_historical_rating_value(item)
                ) and not (
                    key_tokens == {"delta"}
                    and "delta" in local_context
                    and _obvious_historical_delta_value(item)
                ):
                    return (f"{path}.{key}", key)
            if (
                normalized_key in {"namespace", "model_namespace"}
                and isinstance(item, str)
                and set(_normalized_metric_tokens(item)) & {"elo", "leaderboard"}
            ):
                return (f"{path}.{key}", item)
            if (
                normalized_key in _MODEL_METRIC_LABEL_KEYS
                and isinstance(item, str)
                and _is_forbidden_model_field(item)
            ):
                item_kinds = _metric_label_kinds(item)
                historical_kinds = item_kinds & {"rank", "rating", "delta"}
                if (
                    item_kinds & {"elo", "leaderboard", "model"}
                    or not historical_kinds
                    or not historical_kinds.issubset(local_context)
                ):
                    return (f"{path}.{key}", item)
            found = _find_forbidden_key(
                item,
                f"{path}.{key}",
                frozenset(local_context),
                structured_pairing or key in {"precision", "value"},
            )
            if found:
                return found
    elif isinstance(value, list):
        if structured_pairing:
            paired_label = _paired_model_metric_label(value, historical_context)
            if paired_label is not None:
                return (path, paired_label)
        for index, item in enumerate(value):
            found = _find_forbidden_key(
                item,
                f"{path}[{index}]",
                historical_context,
                structured_pairing,
            )
            if found:
                return found
    elif isinstance(value, str) and _contains_forbidden_model_output_text(value):
        return (path, value)
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
    """Build an internally evidence-complete packet without modeled Elo effects.

    Prior adjudications are excluded by default for independent review.  When
    explicitly requested they retain append order and the packet truthfully
    reports that it is no longer decision-blinded.  Neither packet inclusion
    nor an accepted adjudication makes a claim rating-eligible.  Event hierarchy
    and source metadata are external references rather than a closed world;
    unselected hierarchy endpoints are listed in ``external_event_ids`` and are
    never silently expanded into the review scope.
    """

    if not isinstance(include_prior_decisions, bool):
        raise TypeError("include_prior_decisions must be a boolean")
    if isinstance(adjudications, (set, frozenset)):
        raise TypeError("adjudications must be an ordered iterable")
    event_views = [_event_evidence_view(event) for event in events]
    by_event_id: dict[str, dict[str, Any]] = {}
    for event in event_views:
        event_id = event["id"]
        if event_id in by_event_id:
            raise ValueError(f"Duplicate event id {event_id}")
        by_event_id[event_id] = event

    if isinstance(event_ids, (str, bytes, dict)):
        raise ValueError("event_ids must be an array of stable event ids")
    if event_ids is not None:
        try:
            iter(event_ids)
        except TypeError as error:
            raise ValueError("event_ids must be an array of stable event ids") from error
    if event_ids is None:
        selected_ids = set(by_event_id)
    else:
        selected_ids = set()
        for item in event_ids:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("event_ids must contain non-blank string ids")
            selected_ids.add(item)
    unknown_ids = selected_ids - set(by_event_id)
    if unknown_ids:
        raise ValueError(f"Unknown review event ids: {', '.join(sorted(unknown_ids))}")
    selected_events = [by_event_id[event_id] for event_id in sorted(selected_ids)]
    hierarchy_edges: set[tuple[str, str]] = set()
    for event in event_views:
        event_id = event["id"]
        parent_id = event.get("parent_event_id")
        if parent_id is not None:
            if not isinstance(parent_id, str) or not parent_id.strip():
                raise ValueError(
                    f"Review event {event_id} has an invalid parent_event_id"
                )
            hierarchy_edges.add((parent_id, event_id))
        hierarchy_edges.update(
            (parent_id, event_id)
            for parent_id in (event.get("parent_event_ids") or [])
        )
        hierarchy_edges.update(
            (event_id, child_id)
            for child_id in (event.get("child_event_ids") or [])
        )
    self_links = sorted(
        endpoint
        for endpoint, child_id in hierarchy_edges
        if endpoint == child_id and endpoint in selected_ids
    )
    if self_links:
        raise ValueError(
            "Review events cannot be their own parent or child: "
            + ", ".join(self_links)
        )
    external_event_ids = sorted(
        {
            child_id if parent_id in selected_ids else parent_id
            for parent_id, child_id in hierarchy_edges
            if (parent_id in selected_ids) != (child_id in selected_ids)
        }
    )

    internal_edges = {
        (parent_id, child_id)
        for parent_id, child_id in hierarchy_edges
        if parent_id in selected_ids and child_id in selected_ids
    }
    children_by_parent: dict[str, set[str]] = defaultdict(set)
    indegree = {event_id: 0 for event_id in selected_ids}
    for parent_id, child_id in internal_edges:
        if child_id not in children_by_parent[parent_id]:
            children_by_parent[parent_id].add(child_id)
            indegree[child_id] += 1
    ready = sorted(event_id for event_id, degree in indegree.items() if degree == 0)
    visited = 0
    while ready:
        event_id = ready.pop(0)
        visited += 1
        for child_id in sorted(children_by_parent[event_id]):
            indegree[child_id] -= 1
            if indegree[child_id] == 0:
                ready.append(child_id)
                ready.sort()
    if visited != len(selected_ids):
        raise ValueError("Selected review events contain a hierarchy cycle")

    parsed_selected_events = {
        event["id"]: CanonicalEvent.from_dict(event) for event in selected_events
    }
    for parent_id, child_id in sorted(internal_edges):
        parent_bounds = _date_interval_envelope(
            parsed_selected_events[parent_id].date_interval
        )
        child_bounds = _date_interval_envelope(
            parsed_selected_events[child_id].date_interval
        )
        if (
            parent_bounds is not None
            and child_bounds is not None
            and (
                parent_bounds[1] < child_bounds[0]
                or child_bounds[1] < parent_bounds[0]
            )
        ):
            raise ValueError(
                f"Selected parent {parent_id} and child {child_id} have "
                "definitely disjoint date intervals"
            )

    claim_objects = [
        item if isinstance(item, Claim) else Claim.from_dict(item)
        for item in claims
    ]
    claim_by_id: dict[str, Claim] = {}
    for claim in claim_objects:
        _validate_claim_structure(claim)
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
        selected_group_ids = {
            claim_by_id[claim_id].claim_group_id
            for claim_id in selected_claim_ids
            if claim_by_id[claim_id].claim_group_id is not None
        }
        additions = {
            claim.id
            for claim in claim_objects
            if claim.id in outgoing
            or claim.assertion_key in selected_keys
            or claim.claim_group_id in selected_group_ids
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
    selected_groups: dict[str, list[Claim]] = defaultdict(list)
    for claim in selected_claims:
        if claim.claim_group_id is not None:
            selected_groups[claim.claim_group_id].append(claim)
    for group_id, members in selected_groups.items():
        if any(item.exclusive is True for item in members) and any(
            item.exclusive is not True for item in members
        ):
            raise ValueError(
                f"Claim group {group_id} has inconsistent exclusive declarations"
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
        _validate_packet_evidence_link(link)
        if link.id in link_by_id:
            raise ValueError(f"Duplicate evidence link id {link.id}")
        if link.claim_id not in claim_by_id:
            raise ValueError(f"Evidence link {link.id} references unknown claim {link.claim_id}")
        link_by_id[link.id] = link

    selected_decisions: list[Adjudication] = []
    decision_evidence_ids: set[str] = set()
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
            if item.claim_id not in selected_claim_ids:
                continue
            if _contains_forbidden_model_output_text(item.rationale):
                raise ValueError(
                    f"Adjudication {item.id} rationale contains a forbidden model output"
                )
            selected_decisions.append(item)
            for evidence_id in item.evidence_ids_considered:
                link = link_by_id.get(evidence_id)
                if link is None:
                    raise ValueError(
                        f"Adjudication {item.id} considers unknown evidence link "
                        f"{evidence_id}"
                    )
                if link.claim_id != item.claim_id:
                    raise ValueError(
                        f"Adjudication {item.id} considers evidence link {evidence_id} "
                        f"for claim {link.claim_id}, not {item.claim_id}"
                    )
                if evidence_id not in claim_by_id[item.claim_id].evidence_ids:
                    raise ValueError(
                        f"Adjudication {item.id} considers evidence link {evidence_id} "
                        f"that is not referenced by claim {item.claim_id}"
                    )
                decision_evidence_ids.add(evidence_id)

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
    selected_evidence_ids.update(decision_evidence_ids)
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
        "external_event_ids": external_event_ids,
        "events": selected_events,
        "claims": [claim.to_dict() for claim in selected_claims],
        "evidence_links": [link.to_dict() for link in selected_links],
        "disagreements": find_disagreements(selected_claims),
    }
    if include_prior_decisions:
        packet["adjudications"] = [
            item.to_dict()
            for item in selected_decisions
        ]

    for payload_name in ("events", "claims", "evidence_links", "adjudications"):
        if payload_name not in packet:
            continue
        for index, payload_item in enumerate(packet[payload_name]):
            forbidden = _find_forbidden_key(
                payload_item,
                f"$.{payload_name}[{index}]",
            )
            if forbidden:
                path, key = forbidden
                raise ValueError(
                    f"Review packet contains forbidden model field {key!r} at {path}"
                )
    return canonicalize_json(packet)
