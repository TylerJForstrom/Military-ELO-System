from __future__ import annotations

import ast
import csv
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

from .provenance import (
    DEFAULT_CORPUS_LOCK,
    CorpusLock,
    CorpusLockError,
    LockedInput,
    LockedTransformation,
    load_corpus_lock,
    locked_snapshot_reference,
    resolve_locked_snapshot,
    write_review_candidates,
)
from .wikidata import parse_wikidata_battle_rows


TRANSFORMATION_IDS_BY_DATASET = {
    "cliopatria-0.2.0": "cliopatria-review",
    "hced": "hced-review",
    "iwbd": "iwbd-review",
    "iwd-1.21": "iwd-review",
    "ucdp-conflict-26.1": "ucdp-conflict-review",
    "ucdp-dyadic-26.1": "ucdp-dyadic-review",
    "ucdp-actor-26.1": "ucdp-actor-review",
    "ucdp-termination-conflict": "ucdp-termination-conflict-review",
    "ucdp-termination-dyad": "ucdp-termination-dyad-review",
    "wikidata": "wikidata-review",
    "wikidata-battles": "wikidata-battles-review",
}

TRANSFORMERS_BY_DATASET = {
    "cliopatria-0.2.0": "stage_cliopatria",
    "hced": "stage_hced",
    "iwbd": "stage_iwbd",
    "iwd-1.21": "stage_iwd",
    "ucdp-conflict-26.1": "stage_ucdp_archive",
    "ucdp-dyadic-26.1": "stage_ucdp_archive",
    "ucdp-actor-26.1": "stage_ucdp_archive",
    "ucdp-termination-conflict": "stage_ucdp_csv",
    "ucdp-termination-dyad": "stage_ucdp_csv",
    "wikidata": "stage_wikidata",
    "wikidata-battles": "stage_wikidata_battles",
}

TRANSFORMATION_INPUT_DATASETS_BY_DATASET: dict[str, dict[str, str]] = {
    "cliopatria-0.2.0": {"data": "cliopatria-0.2.0"},
    "hced": {"events": "hced", "crosswalk": "hced-seshat-crosswalk"},
    "iwbd": {"data": "iwbd"},
    "iwd-1.21": {"data": "iwd-1.21"},
    "ucdp-conflict-26.1": {"data": "ucdp-conflict-26.1"},
    "ucdp-dyadic-26.1": {"data": "ucdp-dyadic-26.1"},
    "ucdp-actor-26.1": {"data": "ucdp-actor-26.1"},
    "ucdp-termination-conflict": {"data": "ucdp-termination-conflict"},
    "ucdp-termination-dyad": {"data": "ucdp-termination-dyad"},
}

TRANSFORMER_VERSIONS = {
    "stage_cliopatria": "1",
    "stage_hced": "1",
    "stage_iwbd": "1",
    "stage_iwd": "1",
    "stage_ucdp_archive": "1",
    "stage_ucdp_csv": "1",
    "stage_wikidata": "1",
    "stage_wikidata_battles": "1",
}


def _coerce_lock(corpus_lock: CorpusLock | str | Path) -> CorpusLock:
    return corpus_lock if isinstance(corpus_lock, CorpusLock) else load_corpus_lock(corpus_lock)


def verify_transformation_contracts(
    corpus_lock: CorpusLock,
    transformation_ids: Iterable[str] | None = None,
) -> None:
    """Validate locked transformer identities, versions, and named input roles."""

    dataset_by_transformation = {
        transformation_id: dataset_id
        for dataset_id, transformation_id in TRANSFORMATION_IDS_BY_DATASET.items()
    }
    selected = list(transformation_ids or corpus_lock.transformations.keys())
    for transformation_id in selected:
        try:
            dataset_id = dataset_by_transformation[transformation_id]
        except KeyError as exc:
            raise CorpusLockError(
                f"Locked transformation has no code contract: {transformation_id}"
            ) from exc
        transformation = corpus_lock.transformation(transformation_id)
        expected_transformer = TRANSFORMERS_BY_DATASET[dataset_id]
        expected_version = TRANSFORMER_VERSIONS[expected_transformer]
        if (
            transformation.transformer != expected_transformer
            or transformation.version != expected_version
        ):
            raise CorpusLockError(
                f"Transformation contract mismatch for {transformation_id}: lock has "
                f"{transformation.transformer}@{transformation.version}, code requires "
                f"{expected_transformer}@{expected_version}"
            )

        actual_inputs = {
            role: locked_input.dataset_id
            for role, locked_input in transformation.inputs.items()
        }
        if dataset_id in {"wikidata", "wikidata-battles"}:
            page_numbers: set[int] = set()
            for role, input_dataset_id in actual_inputs.items():
                match = re.fullmatch(r"page-(\d+)", role)
                if match is None or input_dataset_id != dataset_id:
                    raise CorpusLockError(
                        f"{transformation_id} requires numeric page-* roles from "
                        f"{dataset_id}"
                    )
                page_number = int(match.group(1))
                if page_number in page_numbers:
                    raise CorpusLockError(
                        f"{transformation_id} repeats numeric page {page_number}"
                    )
                page_numbers.add(page_number)
            if not page_numbers:
                raise CorpusLockError(
                    f"{transformation_id} must lock at least one page"
                )
        else:
            expected_inputs = TRANSFORMATION_INPUT_DATASETS_BY_DATASET[dataset_id]
            if actual_inputs != expected_inputs:
                raise CorpusLockError(
                    f"Transformation input contract mismatch for {transformation_id}: "
                    f"lock has {actual_inputs}, code requires {expected_inputs}"
                )


def _locked_transformation(
    raw_root: str | Path,
    corpus_lock: CorpusLock | str | Path,
    transformation_id: str,
    transformer: str,
) -> tuple[CorpusLock, LockedTransformation, dict[str, Path]]:
    lock = _coerce_lock(corpus_lock)
    transformation = lock.transformation(transformation_id)
    verify_transformation_contracts(lock, [transformation_id])
    if transformation.transformer != transformer:
        raise CorpusLockError(
            f"Stager requested {transformer} for {transformation_id}, but its code contract "
            f"uses {transformation.transformer}"
        )
    sources = {
        role: resolve_locked_snapshot(
            lock,
            raw_root,
            locked_input.dataset_id,
            locked_input.filename,
        )
        for role, locked_input in transformation.inputs.items()
    }
    return lock, transformation, sources


def _input_reference(locked_input: LockedInput) -> str:
    return locked_snapshot_reference(locked_input.dataset_id, locked_input.filename)


def latest_snapshot(
    raw_root: str | Path,
    source_id: str,
    *,
    corpus_lock: CorpusLock | str | Path = DEFAULT_CORPUS_LOCK,
) -> Path:
    """Resolve the one content-locked snapshot; filesystem mtime is never authoritative."""

    return resolve_locked_snapshot(_coerce_lock(corpus_lock), raw_root, source_id)


def verify_staging_inputs(
    raw_root: str | Path,
    dataset_ids: Iterable[str],
    *,
    corpus_lock: CorpusLock | str | Path = DEFAULT_CORPUS_LOCK,
) -> CorpusLock:
    lock = _coerce_lock(corpus_lock)
    for dataset_id in dict.fromkeys(dataset_ids):
        try:
            transformation_id = TRANSFORMATION_IDS_BY_DATASET[dataset_id]
        except KeyError as exc:
            raise CorpusLockError(f"No locked stager is registered for {dataset_id}") from exc
        _locked_transformation(
            raw_root,
            lock,
            transformation_id,
            TRANSFORMERS_BY_DATASET[dataset_id],
        )
    return lock


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return None if text in {"", "NA", "N/A", "null", "None"} else text


def _list_value(value: Any) -> list[str]:
    text = _clean(value)
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple)):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except (SyntaxError, ValueError):
        pass
    return [item.strip() for item in re.split(r"[;,|]", text) if item.strip()]


def _year_range(value: Any) -> tuple[int | None, int | None, int | None]:
    text = _clean(value)
    if not text:
        return None, None, None

    single = re.fullmatch(r"(-?\d+)", text)
    if single:
        year = int(single.group(1))
        return year, year, year

    span = re.fullmatch(r"(-?\d+)\s*(?:-|–|—|to)\s*(-?\d+)", text, flags=re.IGNORECASE)
    if not span:
        return None, None, None

    first_text, second_text = span.groups()
    first, second = int(first_text), int(second_text)
    if first >= 0 and second >= 0 and len(first_text) != len(second_text):
        # Quarantine abbreviated or malformed ranges such as 1817-1 instead of
        # silently converting them into multi-century spans.
        return None, None, None
    low, high = min(first, second), max(first, second)
    return low, round((low + high) / 2), high


def stage_hced(
    raw_root: str | Path = "data/raw",
    destination: str | Path = "data/review/hced-candidates.jsonl",
    *,
    corpus_lock: CorpusLock | str | Path = DEFAULT_CORPUS_LOCK,
) -> list[dict[str, Any]]:
    lock, transformation, sources = _locked_transformation(
        raw_root, corpus_lock, "hced-review", "stage_hced"
    )
    if set(sources) != {"events", "crosswalk"}:
        raise CorpusLockError("hced-review must lock events and crosswalk input roles")
    source = sources["events"]
    crosswalk_source = sources["crosswalk"]
    source_reference = _input_reference(transformation.inputs["events"])
    crosswalk: dict[str, dict[str, Any]] = {}
    with crosswalk_source.open("r", encoding="cp1252", errors="replace", newline="") as handle:
        for row in csv.DictReader(handle):
            event_id = _clean(row.get("ID"))
            if event_id:
                crosswalk[event_id] = row

    candidates: list[dict[str, Any]] = []
    seen_ids: dict[str, int] = {}
    with source.open("r", encoding="cp1252", errors="replace", newline="") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            event_id = _clean(row.get("ID"))
            if not event_id:
                continue
            seen_ids[event_id] = seen_ids.get(event_id, 0) + 1
            year_low, year_best, year_high = _year_range(row.get("Year"))
            link = crosswalk.get(event_id, {})
            side_1_codes = [
                code
                for index in range(1, 7)
                if (code := _clean(link.get(f"seshat_code_side_1_{index}")))
            ]
            side_2_codes = [
                code
                for index in range(1, 7)
                if (code := _clean(link.get(f"seshat_code_side_2_{index}")))
            ]
            winner = _clean(row.get("Winner")) or _clean(link.get("Winner"))
            loser = _clean(row.get("Loser")) or _clean(link.get("Loser"))
            candidates.append(
                {
                    "candidate_id": f"hced-{event_id}-{seen_ids[event_id]}",
                    "source": "hced",
                    "source_record_id": event_id,
                    "source_snapshot": source_reference,
                    "source_row": row_number,
                    "review_status": "needs_review",
                    "do_not_rate_automatically": True,
                    "proposed_event_type": "engagement",
                    "name": _clean(row.get("Battle")),
                    "year_low": year_low,
                    "year_best": year_best,
                    "year_high": year_high,
                    "modern_location_country": _clean(row.get("Country")),
                    "latitude": _clean(row.get("Latitude")),
                    "longitude": _clean(row.get("Longitude")),
                    "war_names": _list_value(row.get("War")),
                    "participants_raw": _list_value(row.get("Participants")),
                    "side_1_raw": _clean(row.get("Participant 1"))
                    or _clean(link.get("Participant.1")),
                    "side_2_raw": _clean(row.get("Participant 2"))
                    or _clean(link.get("Participant.2")),
                    "winner_raw": winner,
                    "loser_raw": loser,
                    "winner_loser_complete": bool(winner and loser),
                    "scale_raw": _clean(row.get("Lehmann Zhukov Scale")),
                    "scale_inferred_raw": _clean(row.get("Infered Scale")),
                    "theatre_raw": _clean(row.get("Theatre")),
                    "massacre_raw": _clean(row.get("Massacre")),
                    "consulted_source_raw": _clean(row.get("Alternative Sources Consulted")),
                    "seshat_side_1_candidates": side_1_codes,
                    "seshat_side_2_candidates": side_2_codes,
                    "duplicate_source_id": seen_ids[event_id] > 1,
                    "extraction_notes": [
                        "Country is modern event location, not a participant polity.",
                        "Winner/loser is a tactical proposal only; confirm identities, sides and confidence.",
                        "HCED participant strings may contain place or campaign terms and require cleaning.",
                    ],
                }
            )
    duplicate_ids = {event_id for event_id, count in seen_ids.items() if count > 1}
    for candidate in candidates:
        if candidate["source_record_id"] in duplicate_ids:
            candidate["duplicate_source_id"] = True
    write_review_candidates(
        candidates, destination, expected=transformation.output, corpus_lock=lock
    )
    return candidates


def stage_iwbd(
    raw_root: str | Path = "data/raw",
    destination: str | Path = "data/review/iwbd-candidates.jsonl",
    *,
    corpus_lock: CorpusLock | str | Path = DEFAULT_CORPUS_LOCK,
) -> list[dict[str, Any]]:
    lock, transformation, sources = _locked_transformation(
        raw_root, corpus_lock, "iwbd-review", "stage_iwbd"
    )
    if set(sources) != {"data"}:
        raise CorpusLockError("iwbd-review must lock one data input role")
    source = sources["data"]
    source_reference = _input_reference(transformation.inputs["data"])
    candidates: list[dict[str, Any]] = []
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            candidates.append(
                {
                    "candidate_id": f"iwbd-{row.get('cowNum')}-{row.get('iwdNum')}-{row_number}",
                    "source": "iwbd",
                    "source_snapshot": source_reference,
                    "source_row": row_number,
                    "review_status": "needs_review",
                    "do_not_rate_automatically": True,
                    "proposed_event_type": "engagement",
                    "name": _clean(row.get("battleName")),
                    "war_name": _clean(row.get("warName")),
                    "start_date": _clean(row.get("startDate")),
                    "end_date": _clean(row.get("endDate")),
                    "duration_days": _clean(row.get("battleLength")),
                    "attacker_raw": _clean(row.get("attacker")),
                    "defender_raw": _clean(row.get("defender")),
                    "winner_raw": _clean(row.get("victor")),
                    "war_level_victor_role": _clean(row.get("victorWarLevel")),
                    "battle_level_victor_role": _clean(row.get("victorBattleLevel")),
                    "extraction_notes": [
                        "Resolve attacker, defender and victor labels to time-bounded entities.",
                        "Keep battle outcome separate from the enclosing war outcome.",
                    ],
                }
            )
    write_review_candidates(
        candidates, destination, expected=transformation.output, corpus_lock=lock
    )
    return candidates


def _iwd_value(value: Any) -> str | None:
    text = _clean(value)
    if text in {None, "-9", "-9.0"}:
        return None
    return text[:-2] if text.endswith(".0") and text[:-2].lstrip("-").isdigit() else text


def stage_iwd(
    raw_root: str | Path = "data/raw",
    destination: str | Path = "data/review/iwd-1.21-candidates.jsonl",
    *,
    corpus_lock: CorpusLock | str | Path = DEFAULT_CORPUS_LOCK,
) -> list[dict[str, Any]]:
    lock, transformation, sources = _locked_transformation(
        raw_root, corpus_lock, "iwd-review", "stage_iwd"
    )
    if set(sources) != {"data"}:
        raise CorpusLockError("iwd-review must lock one data input role")
    source = sources["data"]
    source_reference = _input_reference(transformation.inputs["data"])
    grouped: dict[str, list[tuple[int, dict[str, str]]]] = {}
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        for row_number, row in enumerate(csv.DictReader(handle, delimiter="\t"), start=2):
            component_id = _iwd_value(row.get("initwarid"))
            if component_id:
                grouped.setdefault(component_id, []).append((row_number, row))

    outcome_labels = {"1": "initiator_victory", "2": "initiator_defeat", "3": "draw"}
    candidates: list[dict[str, Any]] = []
    for component_id, numbered_rows in sorted(
        grouped.items(),
        key=lambda item: (0, int(item[0])) if item[0].isdigit() else (1, item[0]),
    ):
        years = [
            int(float(row["year"]))
            for _, row in numbered_rows
            if _iwd_value(row.get("year")) is not None
        ]
        terminal_rows = [
            (row_number, row)
            for row_number, row in numbered_rows
            if _iwd_value(row.get("annualoutcome")) in outcome_labels
        ]
        terminal_year = max(
            (int(float(row["year"])) for _, row in terminal_rows),
            default=None,
        )
        terminal_codes = sorted(
            {
                _iwd_value(row.get("annualoutcome"))
                for _, row in terminal_rows
                if terminal_year is not None and int(float(row["year"])) == terminal_year
            }
            - {None}
        )
        outcome_code = terminal_codes[0] if len(terminal_codes) == 1 else None

        def parties(prefix: str, maximum: int) -> list[dict[str, str]]:
            values: dict[tuple[str, str | None], dict[str, str]] = {}
            for _, row in numbered_rows:
                for index in range(1 if prefix == "ally" else 2, maximum + 1):
                    name = _iwd_value(row.get(f"{prefix}{index}name"))
                    code = _iwd_value(row.get(f"{prefix}{index}ccode"))
                    if name:
                        values[(name, code)] = {
                            "name": name,
                            **({"cow_code": code} if code else {}),
                        }
            return sorted(values.values(), key=lambda item: (item["name"], item.get("cow_code", "")))

        initiators = sorted(
            {
                (_iwd_value(row.get("initname")), _iwd_value(row.get("initccode")))
                for _, row in numbered_rows
                if _iwd_value(row.get("initname"))
            },
            key=lambda item: (item[0] or "", item[1] or ""),
        )
        targets = sorted(
            {
                (_iwd_value(row.get("targetname")), _iwd_value(row.get("targetccode")))
                for _, row in numbered_rows
                if _iwd_value(row.get("targetname"))
            },
            key=lambda item: (item[0] or "", item[1] or ""),
        )
        first = numbered_rows[0][1]
        candidates.append(
            {
                "candidate_id": f"iwd-{component_id}",
                "source": "iwd-1.21",
                "source_snapshot": source_reference,
                "source_rows": [row_number for row_number, _ in numbered_rows],
                "source_component_id": component_id,
                "review_status": "needs_review",
                "do_not_rate_automatically": True,
                "proposed_event_type": "war",
                "name": _iwd_value(first.get("initwarname")),
                "parent_war_id": _iwd_value(first.get("largerwarid")),
                "parent_war_name": _iwd_value(first.get("largerwarname")),
                "start_year": min(years) if years else None,
                "end_year": max(years) if years else None,
                "terminal_outcome_code": outcome_code,
                "terminal_outcome": outcome_labels.get(outcome_code),
                "initiators": [
                    {"name": name, **({"cow_code": code} if code else {})}
                    for name, code in initiators
                    if name
                ],
                "targets": [
                    {"name": name, **({"cow_code": code} if code else {})}
                    for name, code in targets
                    if name
                ],
                "adversaries": parties("adv", 15),
                "allies": parties("ally", 16),
                "joiner_decision": any(_iwd_value(row.get("joiner")) == "1" for _, row in numbered_rows),
                "five_hundred_threshold": any(
                    _iwd_value(row.get("fivehun")) == "1" for _, row in numbered_rows
                ),
                "extraction_notes": [
                    "This is one component-war candidate per initwarid, not one rating per annual row.",
                    "Outcome is from the initiator perspective: 1 victory, 2 defeat, 3 draw.",
                    "The largerwarid record is an umbrella for display and must not receive a second rating.",
                    "Resolve every COW-coded participant to a time-bounded polity before promotion.",
                ],
            }
        )
    write_review_candidates(
        candidates, destination, expected=transformation.output, corpus_lock=lock
    )
    return candidates


def _rows_from_zip(path: Path) -> Iterable[tuple[str, int, dict[str, str]]]:
    with zipfile.ZipFile(path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise ValueError(f"No CSV found in {path}")
        for name in csv_names:
            payload = archive.read(name)
            try:
                text = payload.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = payload.decode("cp1252", errors="replace")
            for row_number, row in enumerate(csv.DictReader(io.StringIO(text)), start=2):
                yield name, row_number, row


def stage_ucdp_archive(
    source_id: str,
    raw_root: str | Path = "data/raw",
    destination: str | Path | None = None,
    *,
    corpus_lock: CorpusLock | str | Path = DEFAULT_CORPUS_LOCK,
) -> list[dict[str, Any]]:
    try:
        transformation_id = TRANSFORMATION_IDS_BY_DATASET[source_id]
    except KeyError as exc:
        raise CorpusLockError(f"No locked archive stager for {source_id}") from exc
    lock, transformation, sources = _locked_transformation(
        raw_root, corpus_lock, transformation_id, "stage_ucdp_archive"
    )
    if set(sources) != {"data"}:
        raise CorpusLockError(f"{transformation_id} must lock one data input role")
    source = sources["data"]
    source_reference = _input_reference(transformation.inputs["data"])
    destination = destination or f"data/review/{source_id}-candidates.jsonl"
    candidates: list[dict[str, Any]] = []
    for member_name, row_number, row in _rows_from_zip(source):
        record_id = (
            row.get("dyad_id")
            or row.get("conflict_id")
            or row.get("actor_id")
            or row.get("id")
            or row_number
        )
        candidates.append(
            {
                "candidate_id": f"{source_id}-{record_id}-{row.get('year', '')}-{row_number}",
                "source": source_id,
                "source_snapshot": source_reference,
                "source_member": member_name,
                "source_row": row_number,
                "review_status": "needs_review",
                "do_not_rate_automatically": True,
                "raw": row,
                "extraction_notes": [
                    "Intensity and battle-death fields do not establish tactical victory.",
                    "Map actors and government names to versioned entities before use.",
                    "Combine with termination, goal and settlement evidence for strategic outcomes.",
                ],
            }
        )
    write_review_candidates(
        candidates, destination, expected=transformation.output, corpus_lock=lock
    )
    return candidates


def stage_ucdp_csv(
    source_id: str,
    raw_root: str | Path = "data/raw",
    destination: str | Path | None = None,
    *,
    corpus_lock: CorpusLock | str | Path = DEFAULT_CORPUS_LOCK,
) -> list[dict[str, Any]]:
    try:
        transformation_id = TRANSFORMATION_IDS_BY_DATASET[source_id]
    except KeyError as exc:
        raise CorpusLockError(f"No locked CSV stager for {source_id}") from exc
    lock, transformation, sources = _locked_transformation(
        raw_root, corpus_lock, transformation_id, "stage_ucdp_csv"
    )
    if set(sources) != {"data"}:
        raise CorpusLockError(f"{transformation_id} must lock one data input role")
    source = sources["data"]
    source_reference = _input_reference(transformation.inputs["data"])
    destination = destination or f"data/review/{source_id}-candidates.jsonl"
    candidates: list[dict[str, Any]] = []
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            record_id = row.get("dyadid") or row.get("conflictid") or row.get("conflict_id") or row_number
            candidates.append(
                {
                    "candidate_id": f"{source_id}-{record_id}-{row_number}",
                    "source": source_id,
                    "source_snapshot": source_reference,
                    "source_row": row_number,
                    "review_status": "needs_review",
                    "do_not_rate_automatically": True,
                    "raw": row,
                    "extraction_notes": [
                        "Termination categories inform strategic coding but do not replace participant-specific review."
                    ],
                }
            )
    write_review_candidates(
        candidates, destination, expected=transformation.output, corpus_lock=lock
    )
    return candidates


def _wikidata_value(row: dict[str, Any], key: str) -> str | None:
    item = row.get(key)
    return str(item.get("value")) if isinstance(item, dict) and item.get("value") is not None else None


def _numbered_wikidata_pages(
    sources: Mapping[str, Path], transformation_id: str
) -> list[tuple[int, str]]:
    numbered_pages: list[tuple[int, str]] = []
    seen_page_numbers: set[int] = set()
    for role in sources:
        match = re.fullmatch(r"page-(\d+)", role)
        if match is None:
            raise CorpusLockError(
                f"{transformation_id} inputs must use numeric page-* roles"
            )
        page_number = int(match.group(1))
        if page_number in seen_page_numbers:
            raise CorpusLockError(
                f"{transformation_id} repeats numeric page {page_number}"
            )
        seen_page_numbers.add(page_number)
        numbered_pages.append((page_number, role))
    if not numbered_pages:
        raise CorpusLockError(f"{transformation_id} must lock at least one page")
    return sorted(numbered_pages)


def _load_wikidata_page_rows(
    sources: Mapping[str, Path], transformation_id: str
) -> list[dict[str, Any]]:
    all_rows: list[dict[str, Any]] = []
    for _, role in _numbered_wikidata_pages(sources, transformation_id):
        with sources[role].open("r", encoding="utf-8") as handle:
            document = json.load(handle)
        results = document.get("results")
        rows = results.get("bindings") if isinstance(results, dict) else None
        if not isinstance(rows, list):
            raise ValueError(f"Wikidata snapshot {sources[role]} has invalid bindings")
        all_rows.extend(rows)
    return all_rows


def stage_wikidata(
    raw_root: str | Path = "data/raw",
    destination: str | Path = "data/review/wikidata-candidates.jsonl",
    *,
    corpus_lock: CorpusLock | str | Path = DEFAULT_CORPUS_LOCK,
) -> list[dict[str, Any]]:
    lock, transformation, sources = _locked_transformation(
        raw_root, corpus_lock, "wikidata-review", "stage_wikidata"
    )
    all_rows = _load_wikidata_page_rows(sources, "wikidata-review")

    grouped: dict[str, dict[str, Any]] = {}
    for row in all_rows:
        event_uri = _wikidata_value(row, "event")
        if not event_uri:
            continue
        candidate = grouped.setdefault(
            event_uri,
            {
                "candidate_id": event_uri.rsplit("/", 1)[-1],
                "source": "wikidata",
                "source_url": event_uri,
                "review_status": "needs_review",
                "do_not_rate_automatically": True,
                "name": _wikidata_value(row, "eventLabel"),
                "kind": _wikidata_value(row, "kind"),
                "date": _wikidata_value(row, "date"),
                "end_date": _wikidata_value(row, "endDate"),
                "participants": {},
                "winners": {},
                "part_of": {},
                "locations": {},
                "extraction_notes": [
                    "Identity aliases, opposing sides, objectives, outcome severity and entity continuity require review."
                ],
            },
        )
        for field, label_field, output_key in (
            ("participant", "participantLabel", "participants"),
            ("winner", "winnerLabel", "winners"),
            ("partOf", "partOfLabel", "part_of"),
            ("location", "locationLabel", "locations"),
        ):
            uri = _wikidata_value(row, field)
            if uri:
                candidate[output_key][uri] = _wikidata_value(row, label_field) or uri.rsplit(
                    "/", 1
                )[-1]

    candidates: list[dict[str, Any]] = []
    for candidate in grouped.values():
        for key in ("participants", "winners", "part_of", "locations"):
            candidate[key] = [
                {"uri": uri, "label": label} for uri, label in candidate[key].items()
            ]
        candidates.append(candidate)
    write_review_candidates(
        candidates, destination, expected=transformation.output, corpus_lock=lock
    )
    return candidates


def stage_wikidata_battles(
    raw_root: str | Path = "data/raw",
    destination: str | Path = "data/review/wikidata-battle-candidates.jsonl",
    *,
    corpus_lock: CorpusLock | str | Path = DEFAULT_CORPUS_LOCK,
) -> list[dict[str, Any]]:
    lock, transformation, sources = _locked_transformation(
        raw_root,
        corpus_lock,
        "wikidata-battles-review",
        "stage_wikidata_battles",
    )
    candidates = parse_wikidata_battle_rows(
        _load_wikidata_page_rows(sources, "wikidata-battles-review")
    )
    write_review_candidates(
        candidates, destination, expected=transformation.output, corpus_lock=lock
    )
    return candidates


def _cluster_temporal_segments(
    segments: Iterable[dict[str, Any]],
) -> list[list[dict[str, Any]]]:
    ordered = sorted(
        segments,
        key=lambda row: (row["start_year"], row["end_year"], row.get("name", "")),
    )
    clusters: list[list[dict[str, Any]]] = []
    cluster_end: int | None = None
    for segment in ordered:
        if cluster_end is None or segment["start_year"] > cluster_end + 1:
            clusters.append([segment])
            cluster_end = segment["end_year"]
        else:
            clusters[-1].append(segment)
            cluster_end = max(cluster_end, segment["end_year"])
    return clusters


def stage_cliopatria(
    raw_root: str | Path = "data/raw",
    destination: str | Path = "data/review/cliopatria-entity-candidates.jsonl",
    *,
    corpus_lock: CorpusLock | str | Path = DEFAULT_CORPUS_LOCK,
) -> list[dict[str, Any]]:
    lock, transformation, sources = _locked_transformation(
        raw_root, corpus_lock, "cliopatria-review", "stage_cliopatria"
    )
    if set(sources) != {"data"}:
        raise CorpusLockError("cliopatria-review must lock one data input role")
    source = sources["data"]
    source_reference = _input_reference(transformation.inputs["data"])
    with zipfile.ZipFile(source) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.lower().endswith(".geojson") and not name.startswith("__MACOSX/")
        ]
        if not names:
            raise ValueError(f"No GeoJSON found in {source}")
        document = json.loads(archive.read(names[0]))

    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for feature in document.get("features", []):
        properties = feature.get("properties", {})
        name = _clean(properties.get("Name"))
        entity_type = _clean(properties.get("Type")) or "POLITY"
        if not name:
            continue
        try:
            start_year = int(properties.get("FromYear"))
            end_year = int(properties.get("ToYear"))
        except (TypeError, ValueError):
            continue
        if end_year < start_year:
            start_year, end_year = end_year, start_year

        seshat_id = _clean(properties.get("SeshatID"))
        wikidata_id = _clean(properties.get("Wikidata"))
        wikipedia_title = _clean(properties.get("Wikipedia"))
        if wikidata_id:
            # A Wikidata item is the strongest available cross-source identity.
            # Keep the source name in the key because broad items can still be
            # reused for differently named historical regimes.
            identity = (entity_type, "wikidata_name", wikidata_id, name.casefold())
        elif seshat_id:
            identity = (entity_type, "seshat", seshat_id, name.casefold())
        elif wikipedia_title:
            identity = (entity_type, "wikipedia_name", wikipedia_title.casefold(), name.casefold())
        else:
            identity = (entity_type, "name", name.casefold())

        grouped.setdefault(identity, []).append(
            {
                "name": name,
                "record_type": entity_type,
                "start_year": start_year,
                "end_year": end_year,
                "wikidata_id": wikidata_id,
                "seshat_id": seshat_id,
                "wikipedia_title": wikipedia_title,
                "components": _clean(properties.get("Components")),
                "member_of": _clean(properties.get("MemberOf")),
                "area": float(properties.get("Area") or 0.0),
            }
        )

    candidates: list[dict[str, Any]] = []
    for identity in sorted(grouped):
        rows = grouped[identity]
        name_counts = Counter(str(row["name"]) for row in rows)
        canonical_name = sorted(name_counts, key=lambda item: (-name_counts[item], item))[0]
        intervals = sorted(
            {(int(row["start_year"]), int(row["end_year"])) for row in rows}
        )
        coverage_groups = _cluster_temporal_segments(rows)
        candidates.append(
            {
                "candidate_id": f"cliopatria-{len(candidates) + 1}",
                "source": "cliopatria-0.2.0",
                "source_snapshot": source_reference,
                "review_status": "needs_review",
                "do_not_rate_automatically": True,
                "canonical_name_candidate": canonical_name,
                "aliases": sorted(name for name in name_counts if name != canonical_name),
                "record_type": rows[0]["record_type"],
                "identity_basis": identity[1],
                "start_year": min(start for start, _ in intervals),
                "end_year": max(end for _, end in intervals),
                "interval_segments": [
                    {"start_year": start, "end_year": end} for start, end in intervals
                ],
                "temporal_coverage_groups": [
                    {
                        "start_year": min(int(row["start_year"]) for row in group),
                        "end_year": max(int(row["end_year"]) for row in group),
                    }
                    for group in coverage_groups
                ],
                "wikidata_ids": sorted(
                    {row["wikidata_id"] for row in rows if row["wikidata_id"]}
                ),
                "seshat_ids": sorted(
                    {row["seshat_id"] for row in rows if row["seshat_id"]}
                ),
                "wikipedia_titles": sorted(
                    {row["wikipedia_title"] for row in rows if row["wikipedia_title"]}
                ),
                "components_raw": sorted(
                    {row["components"] for row in rows if row["components"]}
                ),
                "member_of_raw": sorted(
                    {row["member_of"] for row in rows if row["member_of"]}
                ),
                "geometry_records": len(rows),
                "max_reported_area_km2": round(
                    max(float(row["area"]) for row in rows), 3
                ),
                "extraction_notes": [
                    "Cliopatria is an identity and boundary proposal, not a final continuity decision.",
                    "Temporal gaps are preserved as source-coverage groups, not treated as new historical entities.",
                    "POLITY and RELATION records must not be merged automatically.",
                    "Predecessor links never imply Elo inheritance.",
                    "Small or short-lived polities may be outside Cliopatria coverage.",
                ],
            }
        )
    write_review_candidates(
        candidates, destination, expected=transformation.output, corpus_lock=lock
    )
    return candidates
