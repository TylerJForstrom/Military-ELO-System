from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from military_elo.review import build_review_packet, load_json_records


def _safe_output_path(path: str | Path, input_paths: list[str | Path]) -> Path:
    destination = Path(path).resolve()
    if destination.suffix.lower() != ".json":
        raise ValueError("Review packets must use a .json output path")
    resolved_inputs = {Path(item).resolve() for item in input_paths if item}
    if destination in resolved_inputs:
        raise ValueError("Output path must not overwrite an input document")
    repository = ROOT.resolve()
    build_root = (ROOT / "build").resolve()
    try:
        destination.relative_to(repository)
    except ValueError:
        pass
    else:
        try:
            destination.relative_to(build_root)
        except ValueError as error:
            raise ValueError("In-repository review output is allowed only under build/") from error
    return destination


def _write_json(destination: Path, document: dict) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(
        document,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(serialized)
            temporary_name = temporary.name
        os.replace(temporary_name, destination)
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)


def _selection_ids(path: str | Path) -> list[str]:
    records = load_json_records(path, container_keys=("records", "events"))
    ids: list[str] = []
    for record in records:
        value = record.get("id", record.get("candidate_id", record.get("event_id")))
        if value in (None, ""):
            raise ValueError(f"Selection record in {path} has no stable event id")
        ids.append(str(value))
    return ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a leaderboard-blind packet of canonical events and claim evidence"
    )
    parser.add_argument("--events", required=True, help="Canonical event JSON or JSONL")
    parser.add_argument("--claims", required=True, help="Claim JSON or JSONL")
    parser.add_argument("--evidence-links", help="Typed evidence-link JSON or JSONL")
    parser.add_argument("--adjudications", help="Optional prior decision JSON or JSONL")
    parser.add_argument("--selection", help="Gold-set document whose record ids select events")
    parser.add_argument("--event-id", action="append", default=[])
    parser.add_argument("--include-prior-decisions", action="store_true")
    parser.add_argument(
        "--output",
        default=str(ROOT / "build" / "review-packet.json"),
    )
    args = parser.parse_args(argv)

    event_ids = list(args.event_id)
    if args.selection:
        event_ids.extend(_selection_ids(args.selection))
    selection_requested = bool(args.event_id) or args.selection is not None
    selected = sorted(set(event_ids)) if selection_requested else None

    events = load_json_records(args.events, container_keys=("events", "records"))
    claims = load_json_records(args.claims, container_keys=("claims", "records"))
    evidence_links = (
        load_json_records(
            args.evidence_links,
            container_keys=("evidence_links", "records"),
        )
        if args.evidence_links
        else []
    )
    adjudications = (
        load_json_records(
            args.adjudications,
            container_keys=("adjudications", "records"),
        )
        if args.adjudications
        else []
    )
    packet = build_review_packet(
        events,
        claims,
        adjudications,
        evidence_links=evidence_links,
        event_ids=selected,
        include_prior_decisions=args.include_prior_decisions,
    )
    destination = _safe_output_path(
        args.output,
        [
            args.events,
            args.claims,
            args.evidence_links,
            args.adjudications,
            args.selection,
        ],
    )
    _write_json(destination, packet)
    qualifier = "decision-blind " if packet["blinded"] else ""
    print(f"Wrote {len(packet['events'])} {qualifier}review events to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
