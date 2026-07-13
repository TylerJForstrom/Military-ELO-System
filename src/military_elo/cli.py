from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import audit_dataset, has_errors
from .build import build_results, load_records
from .config import ModelConfig


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="military-elo", description="Build and audit military-history Elo data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Audit the curated data and build dashboard JSON")
    build.add_argument("--data", default="data/seed")
    build.add_argument("--output", default="web/data/results.json")
    build.add_argument("--config", default=None)
    build.add_argument("--audit", default="build/audit.json")
    build.add_argument("--simulations", type=int, default=200)

    audit = subparsers.add_parser("audit", help="Validate data without calculating ratings")
    audit.add_argument("--data", default="data/seed")
    audit.add_argument("--config", default=None)
    audit.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "build":
        results = build_results(
            args.data,
            args.output,
            config_path=args.config,
            audit_path=args.audit,
            simulations=max(0, args.simulations),
        )
        print(
            f"Built {args.output}: {len(results['entities'])} entities, "
            f"{len(results['events'])} rated events"
        )
        return 0

    entities, events, sources, _ = load_records(args.data)
    config = ModelConfig.from_file(args.config) if args.config else ModelConfig()
    issues = audit_dataset(entities, events, sources, config)
    if args.json:
        print(json.dumps([issue.as_dict() for issue in issues], indent=2))
    else:
        for issue in issues:
            print(f"{issue.severity.upper():7} {issue.code:30} {issue.record_id}: {issue.message}")
        print(f"{len(issues)} issue(s), {sum(issue.severity == 'error' for issue in issues)} error(s)")
    return 1 if has_errors(issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
