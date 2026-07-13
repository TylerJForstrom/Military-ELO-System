from __future__ import annotations

import ast
import csv
import io
import json
import re
import zipfile
from collections import Counter
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
            winner = _clean(row.get("Winner")) or _clean(link.get("Winner"))
            loser = _clean(row.get("Loser")) or _clean(link.get("Loser"))
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


def _iwd_value(value: Any) -> str | None:
    text = _clean(value)
    if text in {None, "-9", "-9.0"}:
        return None
    return text[:-2] if text.endswith(".0") and text[:-2].lstrip("-").isdigit() else text


def stage_iwd(
    raw_root: str | Path = "data/raw",
    destination: str | Path = "data/review/iwd-1.21-candidates.jsonl",
) -> list[dict[str, Any]]:
    source = latest_snapshot(raw_root, "iwd-1.21")
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
                "source_snapshot": source.as_posix(),
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
                "source_snapshot": source.as_posix(),
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
    write_review_candidates(candidates, destination)
    return candidates
