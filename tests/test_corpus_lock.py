import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from military_elo.ingest.open_data import (
    CORE_DATASETS,
    DATASETS,
    OpenDataset,
    download_dataset,
    validate_dataset_lock,
)
from military_elo.ingest.provenance import CorpusLockError, load_corpus_lock
from military_elo.ingest.wikidata import fetch_wikidata
from scripts.report_ingestion import build_ingestion_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _raw_only_lock(
    payload: bytes,
    classification: str = "open_core",
    retrieval_method: str = "https",
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "corpus_id": "download-fixture",
        "created_at": "2026-07-14T00:00:00Z",
        "transformation_version": "open-data-review-v1",
        "datasets": {
            "fixture": {
                "title": "Fixture",
                "source_url": "https://example.test/fixture",
                "dataset_version": "v1",
                "license": {"id": "CC0-1.0", "classification": classification},
                "retrieval": {
                    "retrieved_at": "2026-07-13T00:00:00Z",
                    "method": retrieval_method,
                },
                "files": [
                    {
                        "filename": "locked.snapshot",
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "size_bytes": len(payload),
                    }
                ],
            }
        },
        "transformations": {},
    }


class CommittedCorpusLockTests(unittest.TestCase):
    def test_open_dataset_catalog_matches_committed_lock(self) -> None:
        lock = load_corpus_lock()
        self.assertEqual(set(DATASETS), set(CORE_DATASETS))
        for dataset in DATASETS.values():
            validate_dataset_lock(dataset, lock)

    def test_bounded_wikidata_snapshot_is_locked_but_not_an_automatic_download(self) -> None:
        lock = load_corpus_lock()
        self.assertNotIn("wikidata", DATASETS)
        self.assertIn("bounded", lock.dataset("wikidata").title.casefold())
        transformation = lock.transformation("wikidata-review")
        self.assertEqual(list(transformation.inputs), ["page-0001"])
        self.assertEqual(transformation.output.filename, "wikidata-candidates.jsonl")

    def test_locked_queue_counts_reconcile_with_committed_release_metadata(self) -> None:
        lock = load_corpus_lock()
        locked_counts = {
            transformation.output.filename: transformation.output.record_count
            for transformation in lock.transformations.values()
        }
        metadata = json.loads(
            (PROJECT_ROOT / "data/release/metadata.json").read_text(encoding="utf-8")
        )
        release_counts = metadata["promotion"]["source_queue_counts"]

        self.assertEqual(locked_counts, release_counts)
        self.assertEqual(sum(locked_counts.values()), sum(release_counts.values()))

    def test_lock_contains_no_machine_paths_or_credential_fields(self) -> None:
        text = (PROJECT_ROOT / "data/corpus.lock.json").read_text(encoding="utf-8")
        self.assertNotIn("C:\\", text)
        self.assertNotIn(str(Path.home()), text)
        for forbidden in ('"headers"', '"token"', '"password"', '"secret"'):
            self.assertNotIn(forbidden, text.casefold())


class LockedDownloadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = OpenDataset(
            "fixture",
            "Fixture",
            "https://example.test/fixture",
            "CC0-1.0",
            "v1",
            "bin",
            "temporary offline fixture",
        )

    def _write_lock(self, root: Path, payload: bytes) -> Path:
        path = root / "corpus.lock.json"
        path.write_text(json.dumps(_raw_only_lock(payload)), encoding="utf-8")
        return path

    def test_existing_verified_blob_skips_network(self) -> None:
        payload = b"locked bytes"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock_path = self._write_lock(root, payload)
            raw_root = root / "raw"
            blob = raw_root / "fixture" / "locked.snapshot"
            blob.parent.mkdir(parents=True)
            blob.write_bytes(payload)
            with patch.dict(DATASETS, {"fixture": self.dataset}), patch(
                "military_elo.ingest.open_data.get_bytes"
            ) as get_bytes:
                snapshot = download_dataset("fixture", raw_root, corpus_lock=lock_path)
            get_bytes.assert_not_called()
            self.assertEqual(snapshot.path, "data/raw/fixture/locked.snapshot")
            self.assertFalse((raw_root / "manifest.jsonl").exists())

    def test_mismatched_download_is_never_installed_or_manifested(self) -> None:
        expected = b"expected bytes"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock_path = self._write_lock(root, expected)
            raw_root = root / "raw"
            with patch.dict(DATASETS, {"fixture": self.dataset}), patch(
                "military_elo.ingest.open_data.get_bytes", return_value=b"changed upstream"
            ):
                with self.assertRaises(CorpusLockError):
                    download_dataset("fixture", raw_root, corpus_lock=lock_path)
            self.assertFalse((raw_root / "fixture" / "locked.snapshot").exists())
            self.assertFalse((raw_root / "manifest.jsonl").exists())

    def test_authorized_copy_is_never_auto_fetched(self) -> None:
        expected = b"authorized bytes"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock_path = root / "corpus.lock.json"
            lock_path.write_text(
                json.dumps(_raw_only_lock(expected, retrieval_method="authorized_copy")),
                encoding="utf-8",
            )
            raw_root = root / "raw"
            with patch.dict(DATASETS, {"fixture": self.dataset}), patch(
                "military_elo.ingest.open_data.get_bytes"
            ) as get_bytes:
                with self.assertRaises(CorpusLockError):
                    download_dataset("fixture", raw_root, corpus_lock=lock_path)
            get_bytes.assert_not_called()
            self.assertFalse((raw_root / "fixture" / "locked.snapshot").exists())


class OfflineVerificationAndReportingTests(unittest.TestCase):
    def test_live_wikidata_preflights_locked_queue_before_network_or_raw_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw_root = root / "raw"
            review_path = root / "wikidata-candidates.jsonl"
            with patch("military_elo.ingest.wikidata.get_bytes") as get_bytes:
                with self.assertRaises(CorpusLockError):
                    fetch_wikidata(
                        raw_root=raw_root,
                        review_path=review_path,
                        max_pages=1,
                        pause_seconds=0,
                    )
            get_bytes.assert_not_called()
            self.assertFalse(raw_root.exists())
            self.assertFalse(review_path.exists())

    def test_live_acquisition_script_defaults_stay_outside_data_review(self) -> None:
        commands = (
            ("ingest_wikidata.py", "build/acquisition/wikidata/wikidata-live.jsonl", []),
            (
                "ingest_ucdp.py",
                "build/acquisition/ucdp/ucdp-api.jsonl",
                ["--api-token", "offline-fixture"],
            ),
        )
        for script, expected_output, extra_arguments in commands:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                result = subprocess.run(
                    [
                        sys.executable,
                        str(PROJECT_ROOT / "scripts" / script),
                        "--max-pages",
                        "0",
                        *extra_arguments,
                    ],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((root / expected_output).is_file())
                self.assertFalse((root / "data/review").exists())

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "authorized-cow.csv"
            source.write_text("WarNum\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts/import_cow.py"),
                    str(source),
                ],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(
                (root / "build/acquisition/cow/cow-candidates.jsonl").is_file()
            )
            self.assertFalse((root / "data/review").exists())

    def test_verifier_rejects_stale_transformer_version_and_hced_input_contract(self) -> None:
        committed = json.loads(
            (PROJECT_ROOT / "data/corpus.lock.json").read_text(encoding="utf-8")
        )
        for drift in ("version", "hced-crosswalk"):
            with self.subTest(drift=drift), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                document = json.loads(json.dumps(committed))
                if drift == "version":
                    document["transformations"]["hced-review"]["version"] = "stale"
                else:
                    del document["transformations"]["hced-review"]["inputs"]["crosswalk"]
                lock_path = root / "corpus.lock.json"
                lock_path.write_text(json.dumps(document), encoding="utf-8")

                result = subprocess.run(
                    [
                        sys.executable,
                        str(PROJECT_ROOT / "scripts/verify_corpus_lock.py"),
                        "--lock",
                        str(lock_path),
                        "--raw-root",
                        str(root / "missing-raw"),
                        "--inputs-only",
                    ],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 1)
                self.assertIn("contract mismatch", result.stderr.casefold())

    def test_verifier_runs_from_non_repository_working_directory(self) -> None:
        payload = b"fixture"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock_path = root / "corpus.lock.json"
            lock_path.write_text(json.dumps(_raw_only_lock(payload)), encoding="utf-8")
            raw_root = root / "raw"
            blob = raw_root / "fixture" / "locked.snapshot"
            blob.parent.mkdir(parents=True)
            blob.write_bytes(payload)
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts/verify_corpus_lock.py"),
                    "--lock",
                    str(lock_path),
                    "--raw-root",
                    str(raw_root),
                    "--inputs-only",
                ],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("1 locked raw files", result.stdout)

    def test_verifier_rejects_unlocked_top_level_review_queue(self) -> None:
        payload = b"fixture"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock_path = root / "corpus.lock.json"
            lock_path.write_text(json.dumps(_raw_only_lock(payload)), encoding="utf-8")
            raw_root = root / "raw"
            blob = raw_root / "fixture" / "locked.snapshot"
            blob.parent.mkdir(parents=True)
            blob.write_bytes(payload)
            review_root = root / "review"
            review_root.mkdir()
            (review_root / "legacy-candidates.JSONL").write_text("{}\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts/verify_corpus_lock.py"),
                    "--lock",
                    str(lock_path),
                    "--raw-root",
                    str(raw_root),
                    "--review-root",
                    str(review_root),
                ],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("unlocked top-level jsonl", result.stderr.casefold())

    def test_report_counts_only_replaceable_queues_not_nested_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            review_root = Path(temporary) / "review"
            review_root.mkdir()
            queue = review_root / "fixture-candidates.jsonl"
            queue.write_text(
                json.dumps(
                    {
                        "candidate_id": "fixture-1",
                        "source": "fixture",
                        "review_status": "needs_review",
                        "do_not_rate_automatically": True,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            decision = review_root / "decisions" / "human.jsonl"
            decision.parent.mkdir()
            decision.write_text('{"decision_id":"d-1"}\n', encoding="utf-8")

            report = build_ingestion_report(review_root, corpus_lock=None)

            self.assertEqual(report["total_review_candidates"], 1)
            self.assertEqual(set(report["files"]), {queue.name})
            self.assertEqual(decision.read_text(encoding="utf-8"), '{"decision_id":"d-1"}\n')

    def test_report_rejects_top_level_human_decision_file(self) -> None:
        for filename in ("human-decisions.jsonl", "human-decisions.JSONL"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temporary:
                review_root = Path(temporary)
                (review_root / filename).write_text("{}\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    build_ingestion_report(review_root, corpus_lock=None)


if __name__ == "__main__":
    unittest.main()
