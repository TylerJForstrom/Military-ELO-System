from __future__ import annotations

"""Shared deterministic helpers used by the source promotion modules."""

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

from .policy import (
    IDENTITY_DENY_WINDOWS,
    SEED_CODE_POLICIES,
    SEED_EVENT_INTERVAL_EXEMPTIONS,
    _policy_seed_id,
)


def _declared_rejections(
    rejections: Counter[str], declared: tuple[str, ...]
) -> dict[str, int]:
    return {key: rejections.get(key, 0) for key in sorted({*rejections, *declared})}


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def validate_exact_source_contract(
    row: dict[str, Any],
    contract: dict[str, Any],
    *,
    description: str,
) -> None:
    """Fail closed unless every declared source semantic matches its audit hash."""

    field_names = tuple(contract.get("field_names", ()))
    expected_sha256 = str(contract.get("sha256") or "")
    if not field_names or len(field_names) != len(set(field_names)):
        raise ValueError(
            f"invalid {description}: source contract fields are empty or duplicated"
        )
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError(f"invalid {description}: source contract SHA-256 is malformed")
    value = {field: row.get(field) for field in field_names}
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    actual_sha256 = hashlib.sha256(payload).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ValueError(f"stale {description}: source fingerprint changed")


def validate_exact_candidate_contracts(
    candidates: list[dict[str, Any]],
    contracts: dict[str, dict[str, Any]],
    *,
    description: str,
    require_complete: bool = False,
) -> None:
    """Validate exact candidate IDs, uniqueness, and full semantic hashes."""

    rows_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in candidates:
        rows_by_id.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, contract in contracts.items():
        rows = rows_by_id.get(candidate_id, [])
        if not rows:
            if require_complete:
                raise ValueError(
                    f"stale {description} {candidate_id}: target row is missing"
                )
            continue
        if len(rows) != 1:
            raise ValueError(
                f"stale {description} {candidate_id}: expected exactly one target row, "
                f"found {len(rows)}"
            )
        validate_exact_source_contract(
            rows[0],
            contract,
            description=f"{description} {candidate_id}",
        )


def _write_json(path: str | Path, value: object) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def normalize_label(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(
        character for character in text if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def _slug(value: str, maximum: int = 54) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", normalize_label(value)).strip("_")
    return (slug or "polity")[:maximum].rstrip("_")


_EVENT_ORDINAL_WORDS: dict[str, str] = {
    "first": "1",
    "second": "2",
    "third": "3",
    "fourth": "4",
    "fifth": "5",
    "sixth": "6",
    "seventh": "7",
    "eighth": "8",
    "ninth": "9",
    "tenth": "10",
}


def _normalized_event_name(name: str) -> str:
    normalized = normalize_label(name)
    normalized = re.sub(r"^(battle|siege|campaign|war) (of |at )?", "", normalized)
    normalized = re.sub(r"\b(\d+)(?:st|nd|rd|th)\b", r"\1", normalized)
    for word, number in _EVENT_ORDINAL_WORDS.items():
        normalized = re.sub(rf"\b{word}\b", number, normalized)
    return normalized


def _event_key(name: str, year: int) -> tuple[str, int]:
    return _normalized_event_name(name), year


def _cross_source_event_keys(
    name: str, year: int, *, lookup: bool = False
) -> set[tuple[str, int]]:
    """Directional keys for compatible HCED/IWBD event-name suffix paths.

    Exact names are handled separately. Recognized terminal suffixes form a
    path, so ``Plevna 1 a`` can match its parent ``Plevna 1`` and either can
    match bare ``Plevna``. Different branches (``1``/``2`` or ``1 a``/``1 b``)
    never share a fuzzy key. Bare numeric suffixes are recognized only from 1
    through 10, avoiding false bases for names such as ``Hill 203``.
    ``lookup=True`` emits keys compatible with the indexed HCED path.
    """
    normalized = _normalized_event_name(name)
    tokens = normalized.split()
    suffix_reversed: list[str] = []
    while len(tokens) > 1 and re.fullmatch(r"10|[1-9]|[ab]", tokens[-1]):
        suffix_reversed.append(tokens.pop())
    base = " ".join(tokens)
    suffix = tuple(reversed(suffix_reversed))

    def key(kind: str, path: tuple[str, ...]) -> tuple[str, int]:
        return (f"\x00fuzzy:{kind}:{base}:{'/'.join(path)}", year)

    prefixes = [suffix[:length] for length in range(len(suffix))]
    if lookup:
        # Match a less-specific indexed HCED path via its exact-path key, or a
        # more-specific indexed path via its declared-prefix key.
        return {key("actual", prefix) for prefix in prefixes} | {key("extends", suffix)}
    # The HCED index records its actual path and every strict parent it extends.
    return {key("actual", suffix)} | {key("extends", prefix) for prefix in prefixes}


def _candidate_entity_id(candidate: dict[str, Any]) -> str:
    identifiers = (
        list(candidate.get("seshat_ids", []))
        or list(candidate.get("wikidata_ids", []))
        or [str(candidate.get("canonical_name_candidate", "polity"))]
    )
    identity = "|".join(
        [
            *map(str, identifiers),
            str(candidate.get("canonical_name_candidate", "")),
            str(candidate.get("start_year", "")),
            str(candidate.get("end_year", "")),
        ]
    )
    digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:8]
    year = int(candidate["start_year"])
    year_token = f"bce{abs(year)}" if year < 0 else str(year)
    return f"clio_{_slug(str(identifiers[0]))}_{year_token}_{digest}"


def _infer_kind(name: str) -> str:
    lowered = normalize_label(name)
    for token, kind in (
        ("city state", "city_state"),
        ("empire", "empire"),
        ("caliphate", "caliphate"),
        ("sultanate", "sultanate"),
        ("khanate", "khanate"),
        ("kingdom", "kingdom"),
        ("republic", "republic"),
        ("confeder", "confederation"),
        ("dynasty", "dynastic_state"),
    ):
        if token in lowered:
            return kind
    return "polity"


def _normalized_labels(labels: Iterable[Any]) -> set[str]:
    normalized = {normalize_label(label) for label in labels}
    normalized.discard("")
    return normalized


def _candidate_labels(candidate: dict[str, Any]) -> set[str]:
    return _normalized_labels(
        [
            candidate.get("canonical_name_candidate"),
            *candidate.get("aliases", []),
            *candidate.get("wikipedia_titles", []),
        ]
    )


def _seed_entity_labels(entity: dict[str, Any]) -> set[str]:
    return _normalized_labels([entity.get("name"), *entity.get("aliases", [])])


def _candidate_overlaps_entity(
    candidate: dict[str, Any], entity: dict[str, Any]
) -> bool:
    entity_end = entity.get("end_year")
    return int(candidate["end_year"]) >= int(entity["start_year"]) and (
        entity_end is None or int(candidate["start_year"]) <= int(entity_end)
    )


def _candidate_policy_seed(
    candidate: dict[str, Any],
    seed_by_id: dict[str, dict[str, Any]],
) -> str | None:
    start = int(candidate["start_year"])
    end = int(candidate["end_year"])
    matches: set[str] = set()
    for code in candidate.get("seshat_ids", []):
        for policy_start, policy_end, entity_id in SEED_CODE_POLICIES.get(code, ()):
            overlap = max(0, min(end, policy_end) - max(start, policy_start) + 1)
            duration = max(1, end - start + 1)
            if overlap / duration >= 0.80:
                matches.add(entity_id)
    if len(matches) != 1:
        return None
    mapped_seed = next(iter(matches))
    seed_entity = seed_by_id.get(mapped_seed)
    # Vassal and client polities can carry the sovereign's crosswalk codes, so
    # a code-window match alone must not merge a distinct polity (for example
    # the Duchy of Burgundy) into the seed identity; the candidate also has to
    # share one of the seed's names.
    if not seed_entity or not (
        _candidate_labels(candidate) & _seed_entity_labels(seed_entity)
    ):
        return None
    return mapped_seed


def _resolve_code(
    code: str,
    low_year: int,
    high_year: int,
    owners: dict[str, list[dict[str, Any]]],
) -> tuple[str | None, dict[str, Any] | None, str | None]:
    if code in SEED_CODE_POLICIES:
        seed_id = _policy_seed_id(code, low_year, high_year)
        return seed_id, None, None if seed_id else "outside_continuity_policy"

    active = [
        candidate
        for candidate in owners.get(code, [])
        if int(candidate["start_year"]) <= low_year
        and int(candidate["end_year"]) >= high_year
    ]
    if len(active) != 1:
        return None, None, "no_unique_time_valid_polity"
    return _candidate_entity_id(active[0]), active[0], None


def _scale(candidate: dict[str, Any]) -> tuple[str, int]:
    raw = candidate.get("scale_raw") or candidate.get("scale_inferred_raw")
    try:
        level = max(1, min(5, int(float(raw))))
    except (TypeError, ValueError):
        level = 2
    if level <= 1:
        return "skirmish", level
    if level <= 3:
        return "battle", level
    if level == 4:
        return "campaign", level
    return "theater", level


def _domain(value: Any) -> str:
    normalized = normalize_label(value)
    domains: set[str] = set()
    if any(token in normalized for token in ("sea", "naval", "maritime", "water")):
        domains.add("naval")
    if "air" in normalized:
        domains.add("air")
    if any(token in normalized for token in ("land", "ground")):
        domains.add("land")
    return next(iter(domains)) if len(domains) == 1 else "mixed"


def _split_composite_label(raw: Any) -> list[str]:
    """Split one explicitly delimited coalition label into its members.

    ``and`` is deliberately not a delimiter because it occurs inside polity
    names such as Bosnia and Herzegovina.  The leading ``and`` in an Oxford
    comma member is stripped only after a comma, semicolon, or ampersand has
    already established that the raw value is composite.
    """

    members: list[str] = []
    for part in re.split(r"[;,&]", str(raw or "")):
        cleaned = part.strip()
        if cleaned.lower().startswith("and "):
            cleaned = cleaned[4:].strip()
        if cleaned:
            members.append(cleaned)
    return members if len(members) >= 2 else []


def _participants(
    side_a: list[str],
    side_b: list[str],
    draw: bool,
    confidence: float,
    scale_level: int,
    note: str | None = None,
) -> list[dict[str, Any]]:
    if draw:
        winner_values = {
            "battlefield_control": 0.50,
            "mission_objective": 0.50,
            "force_preservation": 0.50,
            "positional_gain": 0.50,
        }
        loser_values = dict(winner_values)
        winner_class = loser_class = "stalemate_or_inconclusive"
        termination = "inconclusive_engagement"
    else:
        margin = min(0.40, 0.22 + 0.035 * scale_level)
        winner_values = {
            "battlefield_control": 0.50 + margin,
            "mission_objective": 0.48 + margin,
            "force_preservation": 0.50 + margin * 0.45,
            "positional_gain": 0.48 + margin * 0.75,
        }
        loser_values = {key: 1.0 - value for key, value in winner_values.items()}
        winner_class = (
            "major_tactical_victory" if scale_level >= 4 else "limited_victory"
        )
        loser_class = "major_tactical_defeat" if scale_level >= 4 else "limited_defeat"
        termination = "engagement_victory"

    output: list[dict[str, Any]] = []
    for side, entity_ids, outcome, result_class, side_termination in (
        ("side_a", side_a, winner_values, winner_class, termination),
        (
            "side_b",
            side_b,
            loser_values,
            loser_class,
            termination if draw else "engagement_defeat",
        ),
    ):
        contribution = round(1.0 / len(entity_ids), 4)
        for entity_id in entity_ids:
            output.append(
                {
                    "entity_id": entity_id,
                    "side": side,
                    "role": "primary" if len(entity_ids) == 1 else "major_ally",
                    "contribution": contribution,
                    "stakes": 0.50 if scale_level < 4 else 0.68,
                    "national_scale": min(0.75, 0.12 + 0.10 * scale_level),
                    "termination": side_termination,
                    "evidence_confidence": confidence,
                    "result_class": result_class,
                    "outcome": outcome,
                    "note": note
                    or "Provisional HCED tactical coding; strategic war outcome is not inferred.",
                }
            )
    return output


def _strategic_participants(
    side_a: list[str],
    side_b: list[str],
    outcome: str,
    confidence: float,
    *,
    stakes: float = 0.72,
    national_scale: float = 0.72,
    note: str | None = None,
) -> list[dict[str, Any]]:
    draw_values = {
        "battlefield_outcome": 0.50,
        "political_objectives": 0.50,
        "territorial_outcome": 0.50,
        "sovereignty_survival": 0.95,
        "settlement_durability": 0.50,
        "force_preservation": 0.50,
    }
    victor_values = {
        "battlefield_outcome": 0.80,
        "political_objectives": 0.76,
        "territorial_outcome": 0.66,
        "sovereignty_survival": 0.96,
        "settlement_durability": 0.70,
        "force_preservation": 0.62,
    }
    defeated_values = {
        "battlefield_outcome": 0.20,
        "political_objectives": 0.24,
        "territorial_outcome": 0.34,
        "sovereignty_survival": 0.78,
        "settlement_durability": 0.30,
        "force_preservation": 0.38,
    }
    if outcome == "draw":
        side_values = (draw_values, draw_values)
        result_classes = ("stalemate_or_inconclusive", "stalemate_or_inconclusive")
        terminations = ("draw", "draw")
    elif outcome == "side_a":
        side_values = (victor_values, defeated_values)
        result_classes = ("limited_victory", "limited_defeat")
        terminations = ("victory", "defeat")
    else:
        side_values = (defeated_values, victor_values)
        result_classes = ("limited_defeat", "limited_victory")
        terminations = ("defeat", "victory")

    output: list[dict[str, Any]] = []
    for index, (side, entity_ids) in enumerate(
        (("side_a", side_a), ("side_b", side_b))
    ):
        contribution = round(1.0 / len(entity_ids), 4)
        for entity_id in entity_ids:
            output.append(
                {
                    "entity_id": entity_id,
                    "side": side,
                    "role": "primary" if len(entity_ids) == 1 else "major_ally",
                    "contribution": contribution,
                    "stakes": stakes,
                    "national_scale": national_scale,
                    "termination": terminations[index],
                    "evidence_confidence": confidence,
                    "result_class": result_classes[index],
                    "outcome": side_values[index],
                    "note": note
                    or (
                        "Coalition-aggregated IWD parent-war outcome; existential or "
                        "regime-ending severity is never inferred from IWD outcome codes."
                    ),
                }
            )
    return output


_WAR_NUMERAL_TOKENS = {
    "first": "1",
    "second": "2",
    "third": "3",
    "fourth": "4",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "i": "1",
    "ii": "2",
    "iii": "3",
    "iv": "4",
}


_WAR_STOP_TOKENS = {"war", "wars", "the", "of", "in", "on", "and"}


def _war_tokens(value: Any) -> frozenset[str]:
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", str(value or ""))
    text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)
    tokens: set[str] = set()
    for token in normalize_label(text).split():
        if token.isdigit() or token in _WAR_STOP_TOKENS:
            continue
        tokens.add(_WAR_NUMERAL_TOKENS.get(token, token))
    return frozenset(tokens)


def _war_tokens_match(left: frozenset[str], right: frozenset[str]) -> bool:
    if not left or not right:
        return False
    smaller, larger = (left, right) if len(left) <= len(right) else (right, left)
    if sum(len(token) for token in smaller) < 4:
        return False
    return smaller <= larger


def _entity_covers(entity: dict[str, Any], low_year: int, high_year: int) -> bool:
    end_year = entity.get("end_year")
    return int(entity["start_year"]) <= low_year and (
        end_year is None or int(end_year) >= high_year
    )


def _canonicalize_superseded_identity(
    entity_id: str,
    polity: dict[str, Any] | None,
    low_year: int,
    high_year: int,
    supersessions: Mapping[str, tuple[str, ...]],
    target_entities: Mapping[str, dict[str, Any]],
) -> tuple[str | None, dict[str, Any] | None]:
    """Resolve one superseded ID to a unique time-valid canonical target.

    The helper is wave-neutral: callers supply the complete, already-audited
    supersession inventory and a non-label-indexed target catalog.  A mapped
    identity fails closed when no target, or more than one target, covers the
    full event interval.  Returning no source-candidate payload after a remap
    prevents the superseded Cliopatria proposal from being materialized as the
    canonical target.
    """

    source_id = str(entity_id)
    if source_id not in supersessions:
        return entity_id, polity
    replacement_ids = tuple(dict.fromkeys(map(str, supersessions[source_id])))
    if not replacement_ids:
        return None, None
    time_valid_targets = [
        replacement_id
        for replacement_id in replacement_ids
        if replacement_id != source_id
        and replacement_id not in supersessions
        and replacement_id in target_entities
        and _entity_covers(target_entities[replacement_id], low_year, high_year)
    ]
    if len(time_valid_targets) != 1:
        return None, None
    return time_valid_targets[0], None


def _validate_seed_event_intervals(
    seed_events: list[dict[str, Any]],
    seed_by_id: dict[str, dict[str, Any]],
) -> None:
    """Enforce full seed-event containment except for declared envelopes."""
    used_exemptions: set[tuple[str, str]] = set()
    violations: list[str] = []
    for event in seed_events:
        low_year = int(event["year"])
        high_year = int(event.get("end_year", low_year))
        for participant in event.get("participants", []):
            entity_id = str(participant.get("entity_id") or "")
            entity = seed_by_id.get(entity_id)
            if entity is None:
                violations.append(
                    f"{event['id']} references missing entity {entity_id}"
                )
                continue
            if _entity_covers(entity, low_year, high_year):
                continue
            key = (str(event["id"]), entity_id)
            exemption = SEED_EVENT_INTERVAL_EXEMPTIONS.get(key)
            if exemption is not None:
                used_exemptions.add(key)
                actual_event_interval = (low_year, high_year)
                actual_entity_interval = (
                    int(entity["start_year"]),
                    int(entity["end_year"])
                    if entity.get("end_year") is not None
                    else None,
                )
                if (
                    actual_event_interval != exemption["event_interval"]
                    or actual_entity_interval != exemption["entity_interval"]
                ):
                    violations.append(
                        f"{event['id']} / {entity_id} interval exemption expected "
                        f"event {exemption['event_interval']} and entity "
                        f"{exemption['entity_interval']}, got event "
                        f"{actual_event_interval} and entity {actual_entity_interval}"
                    )
                continue
            violations.append(
                f"{event['id']} [{low_year},{high_year}] exceeds {entity_id} "
                f"[{entity['start_year']},{entity.get('end_year')}]"
            )
    stale_exemptions = set(SEED_EVENT_INTERVAL_EXEMPTIONS) - used_exemptions
    if stale_exemptions:
        violations.append(f"stale seed interval exemptions: {sorted(stale_exemptions)}")
    if violations:
        raise ValueError(
            "Seed event interval validation failed: " + "; ".join(violations)
        )


def _resolve_label_tiers(
    normalized: str,
    low_year: int,
    high_year: int,
    context: dict[str, Any],
    require_observation_coherence: bool,
) -> tuple[str | None, dict[str, Any] | None, str | None]:
    """Exact-normalized label resolution: seed alias, then crosswalk
    observations, then Cliopatria alias with the seed-mapping guards.

    Every tier requires exactly one match that covers the full
    ``[low_year, high_year]`` interval; ambiguity always fails. The
    observation-coherence flag additionally requires an observed entity's own
    labels to contain the queried label (guards against crosswalk
    mis-pairings); the IWD caller keeps it off so the committed IWD promotion
    stays pinned. Declared identity deny windows are enforced first, in every
    pipeline: within a deny window the label never resolves.
    """
    for deny_low, deny_high in IDENTITY_DENY_WINDOWS.get(normalized, ()):
        if not (high_year < deny_low or low_year > deny_high):
            return None, None, None
    seed_matches = {
        str(entity["id"])
        for entity in context["seed_entities"]
        if _entity_covers(entity, low_year, high_year)
        and normalized
        in {
            normalize_label(entity.get("name")),
            *[normalize_label(alias) for alias in entity.get("aliases", [])],
        }
    }
    if len(seed_matches) == 1:
        return next(iter(seed_matches)), None, "seed_alias"

    release_entities = context["release_entities"]
    entity_labels = context["entity_labels"]
    observed_matches = {
        entity_id
        for _, _, entity_id in context["label_observations"].get(normalized, [])
        if entity_id in release_entities
        and _entity_covers(release_entities[entity_id], low_year, high_year)
        and (
            not require_observation_coherence
            or normalized in entity_labels.get(entity_id, set())
        )
    }
    if len(observed_matches) == 1:
        return next(iter(observed_matches)), None, "crosswalk_observation"

    seed_by_id = context["seed_by_id"]
    candidate_matches = [
        polity
        for polity in context["polity_alias_index"].get(normalized, [])
        if int(polity["start_year"]) <= low_year
        and int(polity["end_year"]) >= high_year
    ]
    candidate_ids = {_candidate_entity_id(polity) for polity in candidate_matches}
    if len(candidate_ids) == 1:
        polity = candidate_matches[0]
        # A candidate that maps onto a curated seed identity must resolve to
        # the seed entity; otherwise one polity would hold two parallel
        # rating identities.
        mapped_seed = _candidate_policy_seed(polity, seed_by_id)
        if not mapped_seed:
            name_matches = context["seed_label_index"].get(
                normalize_label(polity.get("canonical_name_candidate")), set()
            )
            if len(name_matches) == 1:
                named_seed = next(iter(name_matches))
                named_entity = seed_by_id.get(named_seed)
                # A name match alone must not bridge eras: a same-named
                # polity from a different century stays its own identity.
                if named_entity and _candidate_overlaps_entity(polity, named_entity):
                    mapped_seed = named_seed
        if mapped_seed:
            seed_entity = seed_by_id.get(mapped_seed)
            if seed_entity and _entity_covers(seed_entity, low_year, high_year):
                return mapped_seed, None, "cliopatria_alias_to_seed"
            return None, None, None
        return _candidate_entity_id(polity), polity, "cliopatria_alias"
    return None, None, None


def _count_review_records(review_root: str | Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in sorted(Path(review_root).glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            counts[path.name] = sum(1 for line in handle if line.strip())
    return counts


def _deduplicate(values: Iterable[str]) -> list[str]:
    return sorted({value for value in values if value})
