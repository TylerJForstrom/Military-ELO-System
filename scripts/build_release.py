from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from military_elo.release import build_expanded_release


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the versioned provisional release and full polity registry"
    )
    parser.add_argument("--seed", default=str(ROOT / "data" / "seed"))
    parser.add_argument("--review", default=str(ROOT / "data" / "review"))
    parser.add_argument("--release", default=str(ROOT / "data" / "release"))
    parser.add_argument(
        "--registry",
        default=str(ROOT / "data" / "catalog" / "registry.json"),
    )
    args = parser.parse_args()
    result = build_expanded_release(args.seed, args.review, args.release, args.registry)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
