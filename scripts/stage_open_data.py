from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from military_elo.ingest.stage_open_data import (
    stage_cliopatria,
    stage_hced,
    stage_iwd,
    stage_iwbd,
    stage_ucdp_archive,
    stage_ucdp_csv,
)


STAGERS = {
    "cliopatria-0.2.0": stage_cliopatria,
    "hced": stage_hced,
    "iwbd": stage_iwbd,
    "iwd-1.21": stage_iwd,
    "ucdp-conflict-26.1": lambda raw_root: stage_ucdp_archive("ucdp-conflict-26.1", raw_root),
    "ucdp-dyadic-26.1": lambda raw_root: stage_ucdp_archive("ucdp-dyadic-26.1", raw_root),
    "ucdp-actor-26.1": lambda raw_root: stage_ucdp_archive("ucdp-actor-26.1", raw_root),
    "ucdp-termination-conflict": lambda raw_root: stage_ucdp_csv("ucdp-termination-conflict", raw_root),
    "ucdp-termination-dyad": lambda raw_root: stage_ucdp_csv("ucdp-termination-dyad", raw_root),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert raw open-data snapshots into review candidates")
    parser.add_argument("datasets", nargs="+", help="Dataset ids or 'core'")
    parser.add_argument("--raw-root", default="data/raw")
    args = parser.parse_args()
    selected = list(STAGERS) if "core" in args.datasets else args.datasets
    for dataset_id in selected:
        if dataset_id not in STAGERS:
            parser.error(f"Unknown or unstaged dataset: {dataset_id}")
        candidates = STAGERS[dataset_id](args.raw_root)
        print(f"{dataset_id}: {len(candidates)} candidates staged for review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
