from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from military_elo.ingest.provenance import load_corpus_lock, verify_transformation_output


def build_ingestion_report(
    review_root: str | Path,
    corpus_lock: str | Path | None = PROJECT_ROOT / "data/corpus.lock.json",
) -> dict[str, Any]:
    root = Path(review_root)
    top_level_jsonl = sorted(
        path
        for path in (root.iterdir() if root.is_dir() else ())
        if path.is_file() and path.suffix.casefold() == ".jsonl"
    )
    candidate_paths = [
        path for path in top_level_jsonl if path.name.endswith("-candidates.jsonl")
    ]
    unexpected = sorted(
        path.name
        for path in top_level_jsonl
        if not path.name.endswith("-candidates.jsonl")
    )
    if unexpected:
        raise ValueError(
            "Unexpected top-level review JSONL files; human decisions belong under "
            f"review/decisions/: {', '.join(unexpected)}"
        )

    lock_id: str | None = None
    if corpus_lock is not None:
        lock = load_corpus_lock(corpus_lock)
        expected_names = {
            transformation.output.filename for transformation in lock.transformations.values()
        }
        actual_names = {path.name for path in candidate_paths}
        if actual_names != expected_names:
            missing = sorted(expected_names - actual_names)
            extra = sorted(actual_names - expected_names)
            details = []
            if missing:
                details.append(f"missing: {', '.join(missing)}")
            if extra:
                details.append(f"unlocked: {', '.join(extra)}")
            raise ValueError("Review queue set does not match corpus lock (" + "; ".join(details) + ")")
        for transformation_id in lock.transformations:
            verify_transformation_output(lock, root, transformation_id)
        lock_id = lock.corpus_id

    files: dict[str, dict[str, object]] = {}
    source_counts: Counter[str] = Counter()
    total = 0
    auto_rated = 0
    for path in candidate_paths:
        records = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        statuses = Counter(str(record.get("review_status", "unknown")) for record in records)
        for record in records:
            source_counts[str(record.get("source", "unknown"))] += 1
            auto_rated += int(not bool(record.get("do_not_rate_automatically", False)))
        files[path.name] = {"records": len(records), "statuses": dict(statuses)}
        total += len(records)
    return {
        "corpus_lock": lock_id,
        "total_review_candidates": total,
        "candidates_not_quarantined": auto_rated,
        "sources": dict(source_counts.most_common()),
        "files": files,
        "warning": "Review candidates are source assertions, not approved rating events.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize the unapproved ingestion review queue")
    parser.add_argument("--review-root", default="data/review")
    parser.add_argument("--output", default="build/ingestion-report.json")
    parser.add_argument("--lock", default=str(PROJECT_ROOT / "data/corpus.lock.json"))
    parser.add_argument(
        "--skip-lock-verification",
        action="store_true",
        help="Allow an intentionally partial temporary queue outside release workflows",
    )
    args = parser.parse_args()
    report = build_ingestion_report(
        args.review_root,
        None if args.skip_lock_verification else args.lock,
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"{report['total_review_candidates']} candidates across {len(report['files'])} "
        f"review files; report written to {destination}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
