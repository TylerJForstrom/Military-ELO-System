from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from military_elo.promotion.hced_funnel import (  # noqa: E402
    build_hced_unresolved_funnel,
    write_hced_unresolved_funnel,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Rank unresolved HCED labels by conservative identity-resolution yield"
        )
    )
    parser.add_argument("--seed", default=str(ROOT / "data" / "seed"))
    parser.add_argument("--review", default=str(ROOT / "data" / "review"))
    parser.add_argument(
        "--ledger-events",
        default=str(ROOT / "data" / "release" / "events.json"),
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "build" / "hced-unresolved-label-funnel.json"),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Maximum greedy identity selections (20-50 is the intended review batch)",
    )
    args = parser.parse_args(argv)
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")

    report = build_hced_unresolved_funnel(
        args.seed,
        args.review,
        args.ledger_events,
        batch_size=args.batch_size,
    )
    write_hced_unresolved_funnel(report, args.output)
    summary = report["summary"]
    print(
        json.dumps(
            {
                "output": str(Path(args.output)),
                "unresolved_labels": summary["unresolved_labels"],
                "events_touched": summary["events_touched"],
                "sole_blocker_events": summary["sole_blocker_events"],
                "top_10_greedy": report["greedy_batch"]["ranking"][:10],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
