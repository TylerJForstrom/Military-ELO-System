from __future__ import annotations

import ast
import csv
import io
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Iterable

from .provenance import write_review_candidates


def latest_snapshot(raw_root: str | Path, source_id: str) -> Path:
    files = [path for path in (Path(raw_root) / source_id).glob("*") if path.is_file()]
    if not files:
        raise FileNotFoundError(f"No raw snapshot found for {source_id}")
    return max(files, key=lambda path: path.stat().st_mtime_ns)


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
    numbers = [int(item) for item in re.findall(r"-?\d+", text)]
    if not numbers:
        return None, None, None
    if len(numbers) == 1:
        return numbers[0], numbers[0], numbers[0]
    low, high = min(numbers[0], numbers[1]), max(numbers[0], numbers[1])
    return low, round((low + high) / 2), high


def stage_hced(
    raw_root: str | Path = "data/raw",
    destination: str | Path = "data/review/hced-candidates.jsonl",
) -> list[dict[str, Any]]:
    source = latest_snapshot(raw_root, "hced")
    crosswalk_source = latest_snapshot(raw_root, "hced-seshat-crosswalk")
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
            winner = _clean(row.get("Winner"))
            loser = _clean(row.get("Loser"))
            candidates.append(
                {
                    "candidate_id": f"hced-{event_id}-{seen_ids[event_id]}",
                    "source": "hced",
                    "source_record_id": event_id,
                    "source_snapshot": source.as_posix(),
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
                    "side_1_raw": _clean(row.get("Participant 1")),
                    "side_2_raw": _clean(row.get("Participant 2")),
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
    write_review_candidates(candidates, destination)
    return candidates


def stage_iwbd(
    raw_root: str | Path = "data/raw",
    destination: str | Path = "data/review/iwbd-candidates.jsonl",
) -> list[dict[str, Any]]:
    source = latest_snapshot(raw_root, "iwbd")
    candidates: list[dict[str, Any]] = []
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            candidates.append(
                {
                    "candidate_id": f"iwbd-{row.get('cowNum')}-{row.get('iwdNum')}-{row_number}",
                    "source": "iwbd",
                    "source_snapshot": source.as_posix(),
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
    write_review_candidates(candidates, destination)
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
) -> list[dict[str, Any]]:
    source = latest_snapshot(raw_root, source_id)
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
                "source_snapshot": source.as_posix(),
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
    write_review_candidates(candidates, destination)
    return candidates


def stage_ucdp_csv(
    source_id: str,
    raw_root: str | Path = "data/raw",
    destination: str | Path | None = None,
) -> list[dict[str, Any]]:
    source = latest_snapshot(raw_root, source_id)
    destination = destination or f"data/review/{source_id}-candidates.jsonl"
    candidates: list[dict[str, Any]] = []
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            record_id = row.get("dyadid") or row.get("conflictid") or row.get("conflict_id") or row_number
            candidates.append(
                {
                    "candidate_id": f"{source_id}-{record_id}-{row_number}",
                    "source": source_id,
                    "source_snapshot": source.as_posix(),
                    "source_row": row_number,
                    "review_status": "needs_review",
                    "do_not_rate_automatically": True,
                    "raw": row,
                    "extraction_notes": [
                        "Termination categories inform strategic coding but do not replace participant-specific review."
                    ],
                }
            )
    write_review_candidates(candidates, destination)
    return candidates


def stage_cliopatria(
    raw_root: str | Path = "data/raw",
    destination: str | Path = "data/review/cliopatria-entity-candidates.jsonl",
) -> list[dict[str, Any]]:
    source = latest_snapshot(raw_root, "cliopatria-0.2.0")
    with zipfile.ZipFile(source) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.lower().endswith(".geojson") and not name.startswith("__MACOSX/")
        ]
        if not names:
            raise ValueError(f"No GeoJSON found in {source}")
        document = json.loads(archive.read(names[0]))
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for feature in document.get("features", []):
        properties = feature.get("properties", {})
        name = _clean(properties.get("Name"))
        entity_type = _clean(properties.get("Type")) or "POLITY"
        if not name:
            continue
        key = (name, entity_type)
        candidate = grouped.setdefault(
            key,
            {
                "candidate_id": f"cliopatria-{len(grouped) + 1}",
                "source": "cliopatria-0.2.0",
                "source_snapshot": source.as_posix(),
                "review_status": "needs_review",
                "do_not_rate_automatically": True,
                "canonical_name_candidate": name,
                "record_type": entity_type,
                "start_year": int(properties.get("FromYear")),
                "end_year": int(properties.get("ToYear")),
                "wikidata_ids": set(),
                "seshat_ids": set(),
                "wikipedia_titles": set(),
                "components_raw": set(),
                "member_of_raw": set(),
                "geometry_records": 0,
                "max_reported_area_km2": 0.0,
                "extraction_notes": [
                    "Cliopatria is an identity/boundary proposal, not a rating-continuity decision.",
                    "POLITY and RELATION records must not be merged automatically.",
                    "Predecessor links never imply Elo inheritance.",
                    "Small or short-lived polities may be outside Cliopatria coverage.",
                ],
            },
        )
        candidate["start_year"] = min(candidate["start_year"], int(properties.get("FromYear")))
        candidate["end_year"] = max(candidate["end_year"], int(properties.get("ToYear")))
        candidate["geometry_records"] += 1
        candidate["max_reported_area_km2"] = max(
            candidate["max_reported_area_km2"], float(properties.get("Area") or 0.0)
        )
        for source_key, output_key in (
            ("Wikidata", "wikidata_ids"),
            ("SeshatID", "seshat_ids"),
            ("Wikipedia", "wikipedia_titles"),
            ("Components", "components_raw"),
            ("MemberOf", "member_of_raw"),
        ):
            value = _clean(properties.get(source_key))
            if value:
                candidate[output_key].add(value)
    candidates = []
    for candidate in grouped.values():
        for key in (
            "wikidata_ids",
            "seshat_ids",
            "wikipedia_titles",
            "components_raw",
            "member_of_raw",
        ):
            candidate[key] = sorted(candidate[key])
        candidate["max_reported_area_km2"] = round(candidate["max_reported_area_km2"], 3)
        candidates.append(candidate)
    write_review_candidates(candidates, destination)
    return candidates
