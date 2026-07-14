from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from military_elo.ingest.ucdp import fetch_ucdp
from military_elo.ingest.provenance import validate_review_destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage UCDP conflict records for review")
    parser.add_argument("--resource", default="dyadic", choices=["dyadic", "ucdpprioconflict", "gedevents"])
    parser.add_argument("--version", default="26.1")
    parser.add_argument("--raw-root", default="build/acquisition/ucdp/raw")
    parser.add_argument("--review", default="build/acquisition/ucdp/ucdp-api.jsonl")
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--max-pages", type=int, default=None)
    parser.add_argument("--api-token", default=os.environ.get("UCDP_API_TOKEN"))
    args = parser.parse_args()
    validate_review_destination(args.review)
    candidates = fetch_ucdp(
        args.resource,
        args.version,
        args.raw_root,
        args.review,
        args.page_size,
        args.max_pages,
        api_token=args.api_token,
    )
    print(f"Staged {len(candidates)} UCDP candidates; none were auto-rated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
