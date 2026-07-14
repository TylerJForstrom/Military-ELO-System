from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .http import get_bytes
from .provenance import (
    DEFAULT_CORPUS_LOCK,
    CorpusLock,
    CorpusLockError,
    RawSnapshot,
    append_snapshot_manifest,
    install_locked_snapshot,
    load_corpus_lock,
    locked_file,
    locked_snapshot_reference,
    resolve_locked_snapshot,
)


@dataclass(frozen=True)
class OpenDataset:
    id: str
    title: str
    url: str
    license: str
    version: str
    extension: str
    notes: str


DATASETS: dict[str, OpenDataset] = {
    "cliopatria-0.2.0": OpenDataset(
        "cliopatria-0.2.0",
        "Cliopatria historical polity registry",
        "https://raw.githubusercontent.com/Seshat-Global-History-Databank/cliopatria/v0.2.0/cliopatria.geojson.zip",
        "CC-BY-4.0",
        "0.2.0 (3400 BCE-2024 CE)",
        "zip",
        "Polity identity and boundary candidates; predecessor continuity still requires adjudication",
    ),
    "hced": OpenDataset(
        "hced",
        "Historical Conflict Event Dataset",
        "https://dataverse.harvard.edu/api/access/datafile/13390255",
        "CC0-1.0",
        "Dataverse file 13390255",
        "csv",
        "8,881 encounters, 1468 BCE-2003; winner/loser fields require entity review",
    ),
    "hced-seshat-crosswalk": OpenDataset(
        "hced-seshat-crosswalk",
        "HCED-Seshat polity crosswalk",
        "https://dataverse.harvard.edu/api/access/datafile/11018172?format=original",
        "CC0-1.0",
        "Dataverse file 11018172",
        "csv",
        "Candidate polity mappings only; incomplete and subject to identity adjudication",
    ),
    "iwbd": OpenDataset(
        "iwbd",
        "Interstate War Battle Dataset",
        "https://dataverse.harvard.edu/api/access/datafile/4435240?format=original",
        "CC0-1.0",
        "Dataverse file 4435240",
        "csv",
        "1,708 battles in 97 interstate wars, 1823-2003",
    ),
    "iwbd-codebook": OpenDataset(
        "iwbd-codebook",
        "Interstate War Battle Dataset codebook",
        "https://dataverse.harvard.edu/api/access/datafile/4435241",
        "CC0-1.0",
        "Dataverse file 4435241",
        "pdf",
        "Variable definitions and coding rules",
    ),
    "iwd-1.21": OpenDataset(
        "iwd-1.21",
        "Interstate War Data",
        "https://dataverse.harvard.edu/api/access/datafile/5118363",
        "CC0-1.0",
        "1.21 (1823-2003)",
        "tsv",
        "Participant-specific outcomes for 265 interstate component wars; rate one final component outcome, not annual rows",
    ),
    "ucdp-conflict-26.1": OpenDataset(
        "ucdp-conflict-26.1",
        "UCDP/PRIO Armed Conflict Dataset",
        "https://ucdp.uu.se/downloads/ucdpprio/ucdp-prio-acd-261-csv.zip",
        "CC-BY-4.0",
        "26.1 (1946-2025)",
        "zip",
        "Conflict-year data; intensity is not a victory label",
    ),
    "ucdp-dyadic-26.1": OpenDataset(
        "ucdp-dyadic-26.1",
        "UCDP Dyadic Dataset",
        "https://ucdp.uu.se/downloads/dyadic/ucdp-dyadic-261-csv.zip",
        "CC-BY-4.0",
        "26.1 (1946-2025)",
        "zip",
        "Opposing actor pairs; map actors to versioned historical entities",
    ),
    "ucdp-actor-26.1": OpenDataset(
        "ucdp-actor-26.1",
        "UCDP Actor Dataset",
        "https://ucdp.uu.se/downloads/actor/ucdp-actor-261-csv.zip",
        "CC-BY-4.0",
        "26.1",
        "zip",
        "Actor aliases and identifiers for entity resolution",
    ),
    "ucdp-termination-conflict": OpenDataset(
        "ucdp-termination-conflict",
        "UCDP Conflict Termination Dataset",
        "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Conflict.csv",
        "CC-BY-4.0",
        "v4 2024",
        "csv",
        "Peace, ceasefire, victory, low activity and actor-ceased termination categories",
    ),
    "ucdp-termination-dyad": OpenDataset(
        "ucdp-termination-dyad",
        "UCDP Dyadic Conflict Termination Dataset",
        "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Dyad.csv",
        "CC-BY-4.0",
        "v4 2024",
        "csv",
        "Dyad-specific termination categories",
    ),
}

CORE_DATASETS = (
    "cliopatria-0.2.0",
    "hced",
    "hced-seshat-crosswalk",
    "iwbd",
    "iwbd-codebook",
    "iwd-1.21",
    "ucdp-conflict-26.1",
    "ucdp-dyadic-26.1",
    "ucdp-actor-26.1",
    "ucdp-termination-conflict",
    "ucdp-termination-dyad",
)


def _coerce_lock(corpus_lock: CorpusLock | str | Path) -> CorpusLock:
    return corpus_lock if isinstance(corpus_lock, CorpusLock) else load_corpus_lock(corpus_lock)


def validate_dataset_lock(dataset: OpenDataset, corpus_lock: CorpusLock) -> None:
    locked = corpus_lock.dataset(dataset.id)
    expected = {
        "title": dataset.title,
        "source_url": dataset.url,
        "dataset_version": dataset.version,
        "license_id": dataset.license,
        "license_classification": "open_core",
    }
    actual = {
        "title": locked.title,
        "source_url": locked.source_url,
        "dataset_version": locked.dataset_version,
        "license_id": locked.license_id,
        "license_classification": locked.license_classification,
    }
    if actual != expected:
        differences = ", ".join(
            f"{key}: catalog={expected[key]!r}, lock={actual[key]!r}"
            for key in expected
            if expected[key] != actual[key]
        )
        raise CorpusLockError(f"Dataset catalog does not match corpus lock for {dataset.id}: {differences}")


def download_dataset(
    dataset_id: str,
    raw_root: str | Path = "data/raw",
    *,
    corpus_lock: CorpusLock | str | Path = DEFAULT_CORPUS_LOCK,
) -> RawSnapshot:
    dataset = DATASETS[dataset_id]
    lock = _coerce_lock(corpus_lock)
    validate_dataset_lock(dataset, lock)
    locked_dataset = lock.dataset(dataset_id)
    expected = locked_file(locked_dataset)
    candidate = Path(raw_root) / dataset_id / expected.filename
    already_present = candidate.exists()
    if already_present:
        resolve_locked_snapshot(lock, raw_root, dataset_id, expected.filename)
    else:
        if (
            locked_dataset.license_classification != "open_core"
            or locked_dataset.retrieval_method != "https"
        ):
            raise CorpusLockError(
                f"Automatic download is disabled for {dataset_id}: lock class is "
                f"{locked_dataset.license_classification} and retrieval method is "
                f"{locked_dataset.retrieval_method}"
            )
        payload = get_bytes(
            dataset.url,
            accept="*/*",
            expected_sha256=expected.sha256,
            expected_size=expected.size_bytes,
        )
        install_locked_snapshot(payload, raw_root, locked_dataset, expected)

    snapshot = RawSnapshot(
        source_id=dataset.id,
        source_url=locked_dataset.source_url,
        retrieved_at=locked_dataset.retrieved_at,
        license=locked_dataset.license_id,
        sha256=expected.sha256,
        path=locked_snapshot_reference(dataset.id, expected.filename),
        source_version=locked_dataset.dataset_version,
        notes=dataset.notes,
    )
    if not already_present:
        append_snapshot_manifest(snapshot, Path(raw_root) / "manifest.jsonl")
    return snapshot
