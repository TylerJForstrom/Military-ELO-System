from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from military_elo.ingest.open_data import (
    CORE_DATASETS,
    DATASETS,
    download_dataset,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download immutable snapshots of approved open datasets")
    parser.add_argument("datasets", nargs="*", help="Dataset ids or 'core'")
    parser.add_argument("--raw-root", default="data/raw")
    parser.add_argument("--lock", default=str(PROJECT_ROOT / "data/corpus.lock.json"))
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list:
        for dataset_id, dataset in DATASETS.items():
            print(f"{dataset_id:30} {dataset.version:20} {dataset.title}")
        return 0
    if not args.datasets:
        parser.error("at least one dataset id or 'core' is required")
    selected: list[str] = []
    for item in args.datasets:
        if item == "core":
            selected.extend(CORE_DATASETS)
        elif item in DATASETS:
            selected.append(item)
        else:
            parser.error(f"Unknown dataset: {item}")
    for dataset_id in dict.fromkeys(selected):
        snapshot = download_dataset(dataset_id, args.raw_root, corpus_lock=args.lock)
        print(f"{dataset_id}: {snapshot.path} ({snapshot.sha256[:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
