from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from military_elo.build import build_results


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit curated data and rebuild the dashboard")
    parser.add_argument("--data", default=str(ROOT / "data" / "release"))
    parser.add_argument(
        "--registry",
        default=str(ROOT / "data" / "catalog" / "registry.json"),
    )
    parser.add_argument("--output", default=str(ROOT / "web" / "data" / "results.json"))
    parser.add_argument("--audit", default=str(ROOT / "build" / "audit.json"))
    parser.add_argument("--config", default=str(ROOT / "config" / "model.default.json"))
    parser.add_argument("--simulations", type=int, default=200)
    args = parser.parse_args()
    results = build_results(
        args.data,
        args.output,
        config_path=args.config,
        audit_path=args.audit,
        simulations=max(0, args.simulations),
        registry_path=args.registry,
    )
    print(
        f"Built {len(results['entities'])} entities and {len(results['events'])} rated events "
        f"into {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
