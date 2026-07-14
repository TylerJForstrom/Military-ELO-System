"""Immutable claim assertions and exact source-evidence links.

Claim ``status`` is assertion lifecycle only (active, withdrawn, superseded),
never accepted/rejected truth.  Contradictory values remain separate claims and
source-family labels describe provenance without voting.  Review acceptance is
stored only in append-only adjudications and does not itself make evidence
rating-eligible.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable


CLAIM_STATUSES = {
    "active",
    "withdrawn",
    "superseded",
}

_SOURCE_LOCATOR_FIELDS = frozenset(
    {
        "source_id",
        "edition",
        "page",
        "row",
        "url",
        "checksum",
        "language",
        "source_family",
        "creator",
        "citation",
    }
)
_SOURCE_LOCATOR_REQUIRED_FIELDS = frozenset(
    {"source_id", "edition", "checksum", "language", "source_family"}
)
_EVIDENCE_LINK_FIELDS = frozenset(
    {"id", "claim_id", "locator", "relationship", "source_family", "note"}
)
_EVIDENCE_LINK_REQUIRED_FIELDS = frozenset(
    {"id", "claim_id", "locator", "relationship", "source_family"}
)
_CLAIM_FIELDS = frozenset(
    {
        "id",
        "subject",
        "predicate",
        "value",
        "precision",
        "status",
        "provenance",
        "contradicts",
        "note",
        "claim_group_id",
        "exclusive",
        "impact",
        "evidence_ids",
    }
)
_CLAIM_REQUIRED_FIELDS = frozenset(
    {"id", "subject", "predicate", "value", "precision", "status", "provenance"}
)
_EVIDENCE_RELATIONSHIPS = frozenset({"supports", "contradicts", "context"})


def _validate_object_shape(
    raw: Any,
    *,
    model_name: str,
    allowed_fields: frozenset[str],
    required_fields: frozenset[str],
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise TypeError(f"{model_name} must be a JSON object")
    if any(not isinstance(key, str) for key in raw):
        raise TypeError(f"{model_name} object keys must be strings")
    unknown = sorted(set(raw) - allowed_fields)
    if unknown:
        raise ValueError(
            f"{model_name} contains unknown field(s): {', '.join(unknown)}"
        )
    missing = sorted(required_fields - set(raw))
    if missing:
        raise ValueError(
            f"{model_name} is missing required field(s): {', '.join(missing)}"
        )
    return raw


def _required_nonblank_text(
    raw: dict[str, Any], name: str, *, model_name: str
) -> str:
    value = raw[name]
    if not isinstance(value, str):
        raise TypeError(f"{model_name}.{name} must be a string")
    if not value.strip():
        raise ValueError(f"{model_name}.{name} must be non-blank")
    return value


def _optional_text(
    raw: dict[str, Any], name: str, *, model_name: str, default: str = ""
) -> str:
    value = raw[name] if name in raw else default
    if not isinstance(value, str):
        raise TypeError(f"{model_name}.{name} must be a string")
    return value


def _optional_nonblank_text_or_none(
    raw: dict[str, Any], name: str, *, model_name: str
) -> str | None:
    value = raw.get(name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{model_name}.{name} must be a string or null")
    if not value.strip():
        raise ValueError(f"{model_name}.{name} must be non-blank when supplied")
    return value


def _nonblank_string_array(
    raw: dict[str, Any],
    name: str,
    *,
    model_name: str,
    required: bool = False,
) -> list[str]:
    if name not in raw:
        if required:
            raise ValueError(f"{model_name}.{name} is required")
        return []
    value = raw[name]
    if not isinstance(value, list):
        raise TypeError(f"{model_name}.{name} must be an array of stable ids")
    for item in value:
        if not isinstance(item, str):
            raise TypeError(f"{model_name}.{name} must contain string ids")
        if not item.strip():
            raise ValueError(f"{model_name}.{name} must contain non-blank ids")
    if len(value) != len(set(value)):
        raise ValueError(f"{model_name}.{name} must contain unique ids")
    return value


def canonicalize_json(value: Any) -> Any:
    """Return a detached, JSON-safe value with deterministic object-key order.

    Evidence values deliberately remain schema-flexible.  This helper rejects
    Python-only values and non-finite numbers so two claims can be compared and
    serialized without implementation-dependent behavior.
    """

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("JSON evidence values cannot contain NaN or infinity")
        return value
    if isinstance(value, (list, tuple)):
        return [canonicalize_json(item) for item in value]
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise TypeError("JSON evidence object keys must be strings")
        return {
            key: canonicalize_json(value[key])
            for key in sorted(value)
        }
    if hasattr(value, "to_dict"):
        return canonicalize_json(value.to_dict())
    raise TypeError(f"Unsupported JSON evidence value: {type(value).__name__}")


def _freeze_json(value: Any) -> Any:
    """Deep-freeze a detached JSON value while retaining canonical conversion."""

    normalized = canonicalize_json(value)

    def freeze(item: Any) -> Any:
        if isinstance(item, dict):
            return MappingProxyType({key: freeze(item[key]) for key in sorted(item)})
        if isinstance(item, list):
            return tuple(freeze(child) for child in item)
        return item

    return freeze(normalized)


def canonical_json(value: Any) -> str:
    """Serialize a JSON-compatible value in the project's canonical form."""

    return json.dumps(
        canonicalize_json(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


@dataclass(frozen=True)
class SourceLocator:
    """An exact, claim-level pointer into one versioned source family.

    ``source_id`` identifies the source record in this project.  At least one
    of ``page``, ``row``, or ``url`` is required by the evidence audit.
    ``creator`` and ``citation`` retain historical source authorship when it is
    not already available through the source metadata keyed by ``source_id``;
    ``source_family`` is the independence/deduplication unit.
    """

    edition: str = ""
    page: str | int | None = None
    row: str | int | None = None
    url: str | None = None
    checksum: str = ""
    language: str = ""
    source_family: str = ""
    source_id: str = ""
    creator: str = ""
    citation: str = ""

    @property
    def has_exact_anchor(self) -> bool:
        page_or_row = any(
            not isinstance(value, bool)
            and isinstance(value, (str, int))
            and (not isinstance(value, str) or bool(value.strip()))
            for value in (self.page, self.row)
        )
        valid_url = isinstance(self.url, str) and bool(self.url.strip())
        return page_or_row or valid_url

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "source_id": self.source_id,
            "edition": self.edition,
        }
        if self.page is not None:
            result["page"] = self.page
        if self.row is not None:
            result["row"] = self.row
        if self.url is not None:
            result["url"] = self.url
        result.update(
            {
                "checksum": self.checksum,
                "language": self.language,
                "source_family": self.source_family,
            }
        )
        if self.creator:
            result["creator"] = self.creator
        if self.citation:
            result["citation"] = self.citation
        return result

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "SourceLocator":
        raw = _validate_object_shape(
            raw,
            model_name="SourceLocator",
            allowed_fields=_SOURCE_LOCATOR_FIELDS,
            required_fields=_SOURCE_LOCATOR_REQUIRED_FIELDS,
        )
        if not any(name in raw for name in ("page", "row", "url")):
            raise ValueError("SourceLocator requires page, row, or url")

        page = raw.get("page")
        row = raw.get("row")
        for name, value in (("page", page), ("row", row)):
            if name not in raw:
                continue
            if isinstance(value, bool) or not isinstance(value, (str, int)):
                raise TypeError(f"SourceLocator.{name} must be a string or integer")
            if isinstance(value, str) and not value.strip():
                raise ValueError(f"SourceLocator.{name} must be non-blank")
        url = raw.get("url")
        if "url" in raw:
            if not isinstance(url, str):
                raise TypeError("SourceLocator.url must be a string")
            if not url.strip():
                raise ValueError("SourceLocator.url must be non-blank")
        return cls(
            edition=_required_nonblank_text(raw, "edition", model_name="SourceLocator"),
            page=page,
            row=row,
            url=url,
            checksum=_required_nonblank_text(
                raw, "checksum", model_name="SourceLocator"
            ),
            language=_required_nonblank_text(
                raw, "language", model_name="SourceLocator"
            ),
            source_family=_required_nonblank_text(
                raw, "source_family", model_name="SourceLocator"
            ),
            source_id=_required_nonblank_text(
                raw, "source_id", model_name="SourceLocator"
            ),
            creator=_optional_text(raw, "creator", model_name="SourceLocator"),
            citation=_optional_text(raw, "citation", model_name="SourceLocator"),
        )


@dataclass(frozen=True)
class EvidenceLink:
    """A typed relationship between a claim and one exact source locator.

    Link counts are descriptive only.  They never vote a claim into an
    accepted state; only adjudications can resolve a claim.
    """

    id: str
    claim_id: str
    locator: SourceLocator
    relationship: str
    source_family: str
    note: str = ""

    def __post_init__(self) -> None:
        for field_name in ("id", "claim_id", "relationship", "source_family", "note"):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"EvidenceLink.{field_name} must be a string")
        if not isinstance(self.locator, SourceLocator):
            raise TypeError("EvidenceLink.locator must be a SourceLocator object")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "claim_id": self.claim_id,
            "locator": self.locator.to_dict(),
            "relationship": self.relationship,
            "source_family": self.source_family,
        }
        if self.note:
            result["note"] = self.note
        return result

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "EvidenceLink":
        raw = _validate_object_shape(
            raw,
            model_name="EvidenceLink",
            allowed_fields=_EVIDENCE_LINK_FIELDS,
            required_fields=_EVIDENCE_LINK_REQUIRED_FIELDS,
        )
        locator_raw = raw["locator"]
        if not isinstance(locator_raw, dict):
            raise TypeError("EvidenceLink.locator must be a SourceLocator object")
        relationship = _required_nonblank_text(
            raw, "relationship", model_name="EvidenceLink"
        )
        if relationship not in _EVIDENCE_RELATIONSHIPS:
            raise ValueError(
                "EvidenceLink.relationship must be supports, contradicts, or context"
            )
        return cls(
            id=_required_nonblank_text(raw, "id", model_name="EvidenceLink"),
            claim_id=_required_nonblank_text(
                raw, "claim_id", model_name="EvidenceLink"
            ),
            locator=SourceLocator.from_dict(locator_raw),
            relationship=relationship,
            source_family=_required_nonblank_text(
                raw, "source_family", model_name="EvidenceLink"
            ),
            note=_optional_text(raw, "note", model_name="EvidenceLink"),
        )


@dataclass(frozen=True)
class Claim:
    """One source assertion, preserved independently of competing assertions.

    ``status`` describes only the assertion row's lifecycle.  It must never
    encode whether a reviewer accepts or rejects the asserted value; that
    belongs exclusively to append-only :class:`review.Adjudication` records.
    """

    id: str
    subject: str
    predicate: str
    value: Any
    precision: Any = None
    status: str = "active"
    provenance: tuple[SourceLocator, ...] = field(default_factory=tuple)
    contradicts: tuple[str, ...] = field(default_factory=tuple)
    note: str = ""
    claim_group_id: str | None = None
    exclusive: bool | None = None
    impact: str | None = None
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for field_name in ("id", "subject", "predicate", "status", "note"):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"Claim.{field_name} must be a string")
        if self.claim_group_id is not None and not isinstance(self.claim_group_id, str):
            raise TypeError("Claim.claim_group_id must be a string or null")
        if self.impact is not None and not isinstance(self.impact, str):
            raise TypeError("Claim.impact must be a string or null")
        if self.exclusive is not None and not isinstance(self.exclusive, bool):
            raise TypeError("Claim.exclusive must be a boolean or null")
        if not isinstance(self.provenance, (list, tuple)):
            raise TypeError("Claim.provenance must be a sequence of SourceLocator objects")
        if not isinstance(self.contradicts, (list, tuple)):
            raise TypeError("Claim.contradicts must be an array of stable claim ids")
        if not isinstance(self.evidence_ids, (list, tuple)):
            raise TypeError("Claim.evidence_ids must be an array of stable evidence ids")
        if any(not isinstance(item, SourceLocator) for item in self.provenance):
            raise TypeError("Claim.provenance must contain SourceLocator objects")
        if any(not isinstance(item, str) for item in self.contradicts):
            raise TypeError("Claim.contradicts must contain string ids")
        if any(not isinstance(item, str) for item in self.evidence_ids):
            raise TypeError("Claim.evidence_ids must contain string ids")
        object.__setattr__(self, "value", _freeze_json(self.value))
        if self.precision is not None:
            object.__setattr__(self, "precision", _freeze_json(self.precision))
        object.__setattr__(self, "provenance", tuple(self.provenance))
        object.__setattr__(self, "contradicts", tuple(sorted(set(self.contradicts))))
        object.__setattr__(self, "evidence_ids", tuple(sorted(set(self.evidence_ids))))

    @property
    def assertion_key(self) -> tuple[str, str]:
        return (self.subject, self.predicate)

    @property
    def value_key(self) -> str:
        return canonical_json(self.value)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "subject": self.subject,
            "predicate": self.predicate,
            "value": canonicalize_json(self.value),
            "precision": canonicalize_json(self.precision),
            "status": self.status,
            "provenance": [locator.to_dict() for locator in self.provenance],
        }
        if self.contradicts:
            result["contradicts"] = sorted(set(self.contradicts))
        if self.note:
            result["note"] = self.note
        if self.claim_group_id is not None:
            result["claim_group_id"] = self.claim_group_id
        if self.exclusive is not None:
            result["exclusive"] = self.exclusive
        if self.impact is not None:
            result["impact"] = self.impact
        if self.evidence_ids:
            result["evidence_ids"] = sorted(set(self.evidence_ids))
        return result

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Claim":
        raw = _validate_object_shape(
            raw,
            model_name="Claim",
            allowed_fields=_CLAIM_FIELDS,
            required_fields=_CLAIM_REQUIRED_FIELDS,
        )
        provenance_raw = raw["provenance"]
        if not isinstance(provenance_raw, list):
            raise TypeError("Claim.provenance must be an array of source locators")
        if any(not isinstance(item, dict) for item in provenance_raw):
            raise TypeError("Claim.provenance must contain source locator objects")
        contradicts_raw = _nonblank_string_array(
            raw, "contradicts", model_name="Claim"
        )
        evidence_ids_raw = _nonblank_string_array(
            raw, "evidence_ids", model_name="Claim"
        )
        if not provenance_raw and not evidence_ids_raw:
            raise ValueError(
                "Claim requires at least one provenance locator or evidence id"
            )
        exclusive_raw = raw.get("exclusive")
        if exclusive_raw is not None and not isinstance(exclusive_raw, bool):
            raise TypeError("Claim.exclusive must be a boolean or null")
        claim_group_id = _optional_nonblank_text_or_none(
            raw, "claim_group_id", model_name="Claim"
        )
        impact = _optional_nonblank_text_or_none(raw, "impact", model_name="Claim")
        if impact not in (None, "ordinary", "high"):
            raise ValueError("Claim.impact must be ordinary, high, or null")
        status = _required_nonblank_text(raw, "status", model_name="Claim")
        if status not in CLAIM_STATUSES:
            raise ValueError(
                "Claim.status must be active, withdrawn, or superseded"
            )
        return cls(
            id=_required_nonblank_text(raw, "id", model_name="Claim"),
            subject=_required_nonblank_text(raw, "subject", model_name="Claim"),
            predicate=_required_nonblank_text(raw, "predicate", model_name="Claim"),
            value=raw["value"],
            precision=raw["precision"],
            status=status,
            provenance=tuple(SourceLocator.from_dict(item) for item in provenance_raw),
            contradicts=tuple(contradicts_raw),
            note=_optional_text(raw, "note", model_name="Claim"),
            claim_group_id=claim_group_id,
            exclusive=exclusive_raw,
            impact=impact,
            evidence_ids=tuple(evidence_ids_raw),
        )


def find_disagreements(claims: Iterable[Claim]) -> list[dict[str, Any]]:
    """Describe, but never resolve, exact value disagreements among claims."""

    grouped: dict[tuple[str, str], list[Claim]] = {}
    for claim in claims:
        grouped.setdefault(claim.assertion_key, []).append(claim)

    disagreements: list[dict[str, Any]] = []
    for (subject, predicate), group in sorted(grouped.items()):
        values: dict[str, list[str]] = {}
        materialized: dict[str, Any] = {}
        for claim in group:
            values.setdefault(claim.value_key, []).append(claim.id)
            materialized[claim.value_key] = canonicalize_json(claim.value)
        if len(values) < 2:
            continue
        disagreements.append(
            {
                "subject": subject,
                "predicate": predicate,
                "alternatives": [
                    {
                        "value": materialized[value_key],
                        "claim_ids": sorted(values[value_key]),
                    }
                    for value_key in sorted(values)
                ],
            }
        )
    return disagreements
