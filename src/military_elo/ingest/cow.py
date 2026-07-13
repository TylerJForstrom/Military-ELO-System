from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .provenance import write_review_candidates


def import_cow_csv(
    input_path: str | Path,
    review_path: str | Path = "data/review/cow-candidates.jsonl",
    dataset_name: str = "cow-war",
    dataset_version: str = "user-supplied",
) -> list[dict[str, Any]]:
    source_path = Path(input_path)
    with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    candidates = [
        {
            "candidate_id": f"{dataset_name}-{index + 1}",
            "source": dataset_name,
            "source_version": dataset_version,
            "source_file": source_path.as_posix(),
            "review_status": "needs_review",
            "do_not_rate_automatically": True,
            "raw": row,
            "extraction_notes": [
                "Respect the dataset's war type and participant entry/exit dates.",
                "Do not assume every state on opposing coalitions fought every other state.",
                "Resolve COW state codes through the versioned entity registry before rating.",
            ],
        }
        for index, row in enumerate(rows)
    ]
    write_review_candidates(candidates, review_path)
    return candidates
