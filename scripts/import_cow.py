from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from military_elo.ingest.cow import import_cow_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage a downloaded Correlates of War CSV for review")
    parser.add_argument("input")
    parser.add_argument(
        "--review", default="build/acquisition/cow/cow-candidates.jsonl"
    )
    parser.add_argument("--dataset", default="cow-war")
    parser.add_argument("--version", default="user-supplied")
    args = parser.parse_args()
    candidates = import_cow_csv(args.input, args.review, args.dataset, args.version)
    print(f"Staged {len(candidates)} COW rows; none were auto-rated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
