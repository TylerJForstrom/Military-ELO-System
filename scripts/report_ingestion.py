from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize the unapproved ingestion review queue")
    parser.add_argument("--review-root", default="data/review")
    parser.add_argument("--output", default="build/ingestion-report.json")
    args = parser.parse_args()
    root = Path(args.review_root)
    files: dict[str, dict[str, object]] = {}
    source_counts: Counter[str] = Counter()
    total = 0
    auto_rated = 0
    for path in sorted(root.glob("*.jsonl")):
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
    report = {
        "total_review_candidates": total,
        "candidates_not_quarantined": auto_rated,
        "sources": dict(source_counts.most_common()),
        "files": files,
        "warning": "Review candidates are source assertions, not approved rating events.",
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{total} candidates across {len(files)} review files; report written to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
