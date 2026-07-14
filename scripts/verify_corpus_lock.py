from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from military_elo.ingest.provenance import (
    CorpusLockError,
    load_corpus_lock,
    resolve_locked_snapshot,
    verify_transformation_output,
)
from military_elo.ingest.stage_open_data import verify_transformation_contracts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify locked raw blobs and deterministic generated review queues offline"
    )
    parser.add_argument("datasets", nargs="*", help="Optional locked dataset ids")
    parser.add_argument("--lock", default=str(PROJECT_ROOT / "data/corpus.lock.json"))
    parser.add_argument("--raw-root", default="data/raw")
    parser.add_argument("--review-root", default="data/review")
    parser.add_argument(
        "--inputs-only",
        action="store_true",
        help="Verify raw inputs without requiring generated review queues",
    )
    args = parser.parse_args()

    try:
        lock = load_corpus_lock(args.lock)
        verify_transformation_contracts(lock)
        selected = list(dict.fromkeys(args.datasets or lock.datasets.keys()))
        unknown = [dataset_id for dataset_id in selected if dataset_id not in lock.datasets]
        if unknown:
            parser.error(f"Unknown locked dataset: {', '.join(unknown)}")

        verified_files = 0
        for dataset_id in selected:
            dataset = lock.dataset(dataset_id)
            for locked in dataset.files:
                resolve_locked_snapshot(
                    lock, args.raw_root, dataset_id, locked.filename
                )
                verified_files += 1

        verified_queues = 0
        if not args.inputs_only:
            declared_outputs = {
                transformation.output.filename
                for transformation in lock.transformations.values()
            }
            review_root = Path(args.review_root)
            unexpected_outputs = sorted(
                path.name
                for path in (review_root.iterdir() if review_root.is_dir() else ())
                if path.is_file()
                and path.suffix.casefold() == ".jsonl"
                if path.name not in declared_outputs
            )
            if unexpected_outputs:
                raise CorpusLockError(
                    "Review root contains unlocked top-level JSONL files: "
                    + ", ".join(unexpected_outputs)
                )
            selected_set = set(selected)
            transformation_ids = [
                transformation_id
                for transformation_id, transformation in lock.transformations.items()
                if any(
                    locked_input.dataset_id in selected_set
                    for locked_input in transformation.inputs.values()
                )
            ]
            dependency_ids = {
                locked_input.dataset_id
                for transformation_id in transformation_ids
                for locked_input in lock.transformation(transformation_id).inputs.values()
            }
            for dependency_id in sorted(dependency_ids - selected_set):
                dataset = lock.dataset(dependency_id)
                for locked in dataset.files:
                    resolve_locked_snapshot(
                        lock, args.raw_root, dependency_id, locked.filename
                    )
                    verified_files += 1
            for transformation_id in transformation_ids:
                verify_transformation_output(lock, args.review_root, transformation_id)
                verified_queues += 1
    except CorpusLockError as exc:
        print(f"Corpus lock verification failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"Verified corpus {lock.corpus_id}: {verified_files} locked raw files"
        + (
            " (review queues not requested)"
            if args.inputs_only
            else f" and {verified_queues} generated review queues"
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
