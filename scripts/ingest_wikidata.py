from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from military_elo.ingest.wikidata import fetch_wikidata


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage Wikidata military-event candidates for review")
    parser.add_argument("--raw-root", default="build/acquisition/wikidata/raw")
    parser.add_argument(
        "--review", default="build/acquisition/wikidata/wikidata-live.jsonl"
    )
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--max-pages", type=int, default=None)
    args = parser.parse_args()
    candidates = fetch_wikidata(args.raw_root, args.review, args.page_size, args.max_pages)
    print(f"Staged {len(candidates)} Wikidata candidates; none were auto-rated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
