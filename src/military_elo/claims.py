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
        def text_field(name: str, *, alias: str | None = None) -> str:
            value = raw.get(name, raw.get(alias, "") if alias else "")
            if not isinstance(value, str):
                raise TypeError(f"SourceLocator.{name} must be a string")
            return value

        page = raw.get("page")
        row = raw.get("row", raw.get("source_row"))
        for name, value in (("page", page), ("row", row)):
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, (str, int))
            ):
                raise TypeError(f"SourceLocator.{name} must be a string, integer, or null")
        url = raw["url"] if raw.get("url") is not None else raw.get("source_url")
        if url is not None and not isinstance(url, str):
            raise TypeError("SourceLocator.url must be a string or null")
        return cls(
            edition=text_field("edition"),
            page=page,
            row=row,
            url=url,
            checksum=text_field("checksum"),
            language=text_field("language"),
            source_family=text_field("source_family", alias="family"),
            source_id=text_field("source_id", alias="source"),
            creator=text_field("creator", alias="author"),
            citation=text_field("citation"),
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
        def text_field(name: str, *, alias: str | None = None) -> str:
            value = raw.get(name, raw.get(alias, "") if alias else "")
            if not isinstance(value, str):
                raise TypeError(f"EvidenceLink.{name} must be a string")
            return value

        locator_raw = raw.get("locator")
        if not isinstance(locator_raw, dict):
            raise TypeError("EvidenceLink.locator must be a SourceLocator object")
        return cls(
            id=text_field("id", alias="evidence_id"),
            claim_id=text_field("claim_id"),
            locator=SourceLocator.from_dict(locator_raw),
            relationship=text_field("relationship", alias="relation"),
            source_family=text_field("source_family"),
            note=text_field("note"),
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
        def text_field(name: str, *, alias: str | None = None, default: str = "") -> str:
            value = raw.get(name, raw.get(alias, default) if alias else default)
            if not isinstance(value, str):
                raise TypeError(f"Claim.{name} must be a string")
            return value

        if "value" not in raw:
            raise ValueError("Claim.value is required; explicit null remains a valid assertion")
        provenance_raw = raw["provenance"] if "provenance" in raw else []
        if not isinstance(provenance_raw, (list, tuple)):
            raise TypeError("Claim.provenance must be an array of source locators")
        contradicts_raw = raw["contradicts"] if "contradicts" in raw else []
        if not isinstance(contradicts_raw, (list, tuple)):
            raise TypeError("Claim.contradicts must be an array of stable claim ids")
        evidence_ids_raw = raw["evidence_ids"] if "evidence_ids" in raw else []
        if not isinstance(evidence_ids_raw, (list, tuple)):
            raise TypeError("Claim.evidence_ids must be an array of stable evidence ids")
        if any(not isinstance(item, str) for item in contradicts_raw):
            raise TypeError("Claim.contradicts must contain string ids")
        if any(not isinstance(item, str) for item in evidence_ids_raw):
            raise TypeError("Claim.evidence_ids must contain string ids")
        exclusive_raw = raw.get("exclusive")
        if exclusive_raw is not None and not isinstance(exclusive_raw, bool):
            raise TypeError("Claim.exclusive must be a boolean or null")
        return cls(
            id=text_field("id", alias="claim_id"),
            subject=text_field("subject"),
            predicate=text_field("predicate"),
            value=raw.get("value"),
            precision=raw.get("precision"),
            status=text_field("status", default="active"),
            provenance=tuple(SourceLocator.from_dict(item) for item in provenance_raw),
            contradicts=tuple(str(item) for item in contradicts_raw),
            note=text_field("note"),
            claim_group_id=raw.get("claim_group_id"),
            exclusive=exclusive_raw,
            impact=raw.get("impact"),
            evidence_ids=tuple(str(item) for item in evidence_ids_raw),
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
