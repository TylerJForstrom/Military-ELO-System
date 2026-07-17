from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from military_elo.ingest.wikidata import fetch_wikidata_battles


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Acquire the era-bucketed Wikidata battle and siege trees as "
            "immutable snapshots (acquisition area only; staging into the "
            "locked corpus is a separate reviewed step)"
        )
    )
    parser.add_argument(
        "--raw-root",
        default=str(PROJECT_ROOT / "build/acquisition/wikidata-battles/raw"),
    )
    parser.add_argument(
        "--review-path",
        default=str(
            PROJECT_ROOT
            / "build/acquisition/wikidata-battles/wikidata-battles-live.jsonl"
        ),
    )
    parser.add_argument("--pause-seconds", type=float, default=2.0)
    args = parser.parse_args()
    candidates = fetch_wikidata_battles(
        raw_root=args.raw_root,
        review_path=args.review_path,
        pause_seconds=args.pause_seconds,
    )
    print(f"fetched {len(candidates)} unique event candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
