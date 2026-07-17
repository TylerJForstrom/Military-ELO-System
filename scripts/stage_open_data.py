from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from military_elo.ingest.provenance import CorpusLock
from military_elo.ingest.stage_open_data import (
    TRANSFORMATION_IDS_BY_DATASET,
    stage_cliopatria,
    stage_hced,
    stage_iwd,
    stage_iwbd,
    stage_ucdp_archive,
    stage_ucdp_csv,
    stage_wikidata,
    stage_wikidata_battles,
    verify_staging_inputs,
)


Stager = Callable[[str | Path, str | Path, CorpusLock], list[dict[str, object]]]


STAGERS: dict[str, Stager] = {
    "cliopatria-0.2.0": lambda raw, output, lock: stage_cliopatria(
        raw, output, corpus_lock=lock
    ),
    "hced": lambda raw, output, lock: stage_hced(raw, output, corpus_lock=lock),
    "iwbd": lambda raw, output, lock: stage_iwbd(raw, output, corpus_lock=lock),
    "iwd-1.21": lambda raw, output, lock: stage_iwd(raw, output, corpus_lock=lock),
    "ucdp-conflict-26.1": lambda raw, output, lock: stage_ucdp_archive(
        "ucdp-conflict-26.1", raw, output, corpus_lock=lock
    ),
    "ucdp-dyadic-26.1": lambda raw, output, lock: stage_ucdp_archive(
        "ucdp-dyadic-26.1", raw, output, corpus_lock=lock
    ),
    "ucdp-actor-26.1": lambda raw, output, lock: stage_ucdp_archive(
        "ucdp-actor-26.1", raw, output, corpus_lock=lock
    ),
    "ucdp-termination-conflict": lambda raw, output, lock: stage_ucdp_csv(
        "ucdp-termination-conflict", raw, output, corpus_lock=lock
    ),
    "ucdp-termination-dyad": lambda raw, output, lock: stage_ucdp_csv(
        "ucdp-termination-dyad", raw, output, corpus_lock=lock
    ),
    "wikidata": lambda raw, output, lock: stage_wikidata(
        raw, output, corpus_lock=lock
    ),
    "wikidata-battles": lambda raw, output, lock: stage_wikidata_battles(
        raw, output, corpus_lock=lock
    ),
}

CORE_STAGERS = tuple(
    dataset_id
    for dataset_id in STAGERS
    if dataset_id not in {"wikidata", "wikidata-battles"}
)
CORPUS_STAGERS = tuple(STAGERS)


def stage_selected(
    dataset_ids: list[str],
    raw_root: str | Path,
    review_root: str | Path,
    corpus_lock: str | Path,
) -> dict[str, int]:
    """Restage selected queues as one verified batch, preserving decision journals."""

    selected = list(dict.fromkeys(dataset_ids))
    lock = verify_staging_inputs(raw_root, selected, corpus_lock=corpus_lock)
    destination_root = Path(review_root)
    destination_root.mkdir(parents=True, exist_ok=True)
    staged: dict[str, tuple[Path, Path, int]] = {}
    with tempfile.TemporaryDirectory(prefix=".corpus-stage-", dir=destination_root) as temporary:
        temporary_root = Path(temporary)
        for dataset_id in selected:
            transformation = lock.transformation(TRANSFORMATION_IDS_BY_DATASET[dataset_id])
            temporary_output = temporary_root / transformation.output.filename
            candidates = STAGERS[dataset_id](raw_root, temporary_output, lock)
            staged[dataset_id] = (
                temporary_output,
                destination_root / transformation.output.filename,
                len(candidates),
            )

        for temporary_output, final_output, _ in staged.values():
            os.replace(temporary_output, final_output)

    return {dataset_id: count for dataset_id, (_, _, count) in staged.items()}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministically restage content-locked open-data review queues"
    )
    parser.add_argument("datasets", nargs="+", help="Dataset ids, 'core', or 'corpus'")
    parser.add_argument("--raw-root", default="data/raw")
    parser.add_argument("--review-root", default="data/review")
    parser.add_argument("--lock", default=str(PROJECT_ROOT / "data/corpus.lock.json"))
    args = parser.parse_args()

    selected: list[str] = []
    for item in args.datasets:
        if item == "core":
            selected.extend(CORE_STAGERS)
        elif item == "corpus":
            selected.extend(CORPUS_STAGERS)
        elif item in STAGERS:
            selected.append(item)
        else:
            parser.error(f"Unknown or unstaged dataset: {item}")

    counts = stage_selected(selected, args.raw_root, args.review_root, args.lock)
    for dataset_id, count in counts.items():
        print(f"{dataset_id}: {count} candidates staged for review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
