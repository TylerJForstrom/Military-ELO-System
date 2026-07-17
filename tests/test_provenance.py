import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from military_elo.ingest.provenance import (
    CorpusLockError,
    LockedOutput,
    append_review_decision,
    load_corpus_lock,
    resolve_locked_snapshot,
    review_candidates_bytes,
    write_review_candidates,
)


def _lock_document(payload: bytes = b"fixture") -> dict[str, object]:
    records = [{"candidate_id": "fixture-1", "source": "fixture"}]
    output = review_candidates_bytes(records)
    return {
        "schema_version": 1,
        "corpus_id": "fixture-corpus",
        "created_at": "2026-07-14T00:00:00Z",
        "transformation_version": "open-data-review-v1",
        "datasets": {
            "fixture": {
                "title": "Fixture dataset",
                "source_url": "https://example.test/fixture.bin",
                "dataset_version": "v1",
                "license": {"id": "CC0-1.0", "classification": "open_core"},
                "retrieval": {
                    "retrieved_at": "2026-07-13T00:00:00Z",
                    "method": "https",
                },
                "files": [
                    {
                        "filename": "fixture.bin",
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "size_bytes": len(payload),
                    }
                ],
            }
        },
        "transformations": {
            "fixture-review": {
                "transformer": "stage_fixture",
                "version": "1",
                "inputs": {
                    "data": {"dataset": "fixture", "filename": "fixture.bin"}
                },
                "output": {
                    "kind": "generated_review_queue",
                    "filename": "fixture-candidates.jsonl",
                    "sha256": hashlib.sha256(output).hexdigest(),
                    "size_bytes": len(output),
                    "record_count": len(records),
                },
            }
        },
    }


class CorpusLockParsingTests(unittest.TestCase):
    def _write_lock(self, root: Path, document: dict[str, object]) -> Path:
        path = root / "corpus.lock.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    def test_default_lock_is_independent_of_current_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            previous = Path.cwd()
            try:
                os.chdir(temporary)
                lock = load_corpus_lock()
            finally:
                os.chdir(previous)
        self.assertEqual(lock.corpus_id, "military-history-elo-2026-07-13")

    def test_rejects_absolute_or_traversing_filenames(self) -> None:
        invalid = (
            "C:\\private\\blob.csv",
            "/private/blob.csv",
            "../blob.csv",
            "bad*name.csv",
            "bad?name.csv",
            'bad"name.csv',
            "bad<name.csv",
            "bad>name.csv",
            "bad|name.csv",
            "bad\x1fname.csv",
            "trailing-dot.csv.",
            "trailing-space.csv ",
            "CONIN$",
            "conout$.txt",
        )
        for filename in invalid:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                document = _lock_document()
                document["datasets"]["fixture"]["files"][0]["filename"] = filename
                with self.assertRaises(CorpusLockError):
                    load_corpus_lock(self._write_lock(root, document))

    def test_rejects_credentials_in_source_url(self) -> None:
        for query_key in (
            "access_token",
            "auth",
            "token",
            "key",
            "X-Amz-Signature",
            "token[]",
            "auth.token",
            "api.key",
            "access[token]",
        ):
            with self.subTest(query_key=query_key), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                document = _lock_document()
                document["datasets"]["fixture"]["source_url"] = (
                    f"https://example.test/blob?{query_key}=not-allowed"
                )
                with self.assertRaises(CorpusLockError):
                    load_corpus_lock(self._write_lock(root, document))

    def test_rejects_url_fragments_that_can_hide_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = _lock_document()
            document["datasets"]["fixture"]["source_url"] = (
                "https://example.test/blob#access_token=not-allowed"
            )
            with self.assertRaises(CorpusLockError):
                load_corpus_lock(self._write_lock(root, document))

    def test_rejects_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "corpus.lock.json"
            path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaises(CorpusLockError):
                load_corpus_lock(path)


class LockedFileTests(unittest.TestCase):
    def test_missing_and_mismatched_inputs_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = _lock_document(b"expected")
            lock_path = root / "corpus.lock.json"
            lock_path.write_text(json.dumps(document), encoding="utf-8")
            lock = load_corpus_lock(lock_path)
            raw_root = root / "raw"
            with self.assertRaises(CorpusLockError):
                resolve_locked_snapshot(lock, raw_root, "fixture")

            blob = raw_root / "fixture" / "fixture.bin"
            blob.parent.mkdir(parents=True)
            blob.write_bytes(b"wrong")
            with self.assertRaises(CorpusLockError):
                resolve_locked_snapshot(lock, raw_root, "fixture")

    def test_generated_queue_is_checked_before_existing_file_is_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "fixture-candidates.jsonl"
            destination.write_bytes(b"existing\n")
            expected = LockedOutput(
                kind="generated_review_queue",
                filename=destination.name,
                sha256="0" * 64,
                size_bytes=1,
                record_count=1,
            )
            with self.assertRaises(CorpusLockError):
                write_review_candidates(
                    [{"candidate_id": "new"}], destination, expected=expected
                )
            self.assertEqual(destination.read_bytes(), b"existing\n")

    def test_unlocked_writer_cannot_overwrite_a_locked_queue_basename(self) -> None:
        for basename in (
            "wikidata-candidates.jsonl",
            "wikidata-battle-candidates.jsonl",
        ):
            for filename in (
                basename,
                basename.upper(),
                basename + ".",
                basename + " ",
            ):
                with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temporary:
                    destination = Path(temporary) / filename
                    with self.assertRaises(CorpusLockError):
                        write_review_candidates(
                            [{"candidate_id": "live-fetch"}], destination
                        )
                    self.assertFalse((Path(temporary) / basename).exists())

    def test_fabricated_expected_contract_cannot_bypass_locked_queue_guard(self) -> None:
        records = [{"candidate_id": "fabricated"}]
        payload = review_candidates_bytes(records)
        fabricated = LockedOutput(
            kind="generated_review_queue",
            filename="wikidata-candidates.jsonl",
            sha256=hashlib.sha256(payload).hexdigest(),
            size_bytes=len(payload),
            record_count=1,
        )
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / fabricated.filename
            destination.write_bytes(b"existing\n")
            with self.assertRaises(CorpusLockError):
                write_review_candidates(records, destination, expected=fabricated)
            self.assertEqual(destination.read_bytes(), b"existing\n")

    def test_custom_lock_cannot_suppress_committed_locked_queue_guard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            custom_lock_path = root / "custom.lock.json"
            custom_lock_path.write_text(json.dumps(_lock_document()), encoding="utf-8")
            custom_lock = load_corpus_lock(custom_lock_path)
            destination = root / "wikidata-candidates.jsonl"
            destination.write_bytes(b"existing\n")

            with self.assertRaises(CorpusLockError):
                write_review_candidates(
                    [{"candidate_id": "live-fetch"}],
                    destination,
                    corpus_lock=custom_lock,
                )

            self.assertEqual(destination.read_bytes(), b"existing\n")


class ReviewDecisionTests(unittest.TestCase):
    def test_decisions_append_without_rewriting_and_reject_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "decisions" / "human.jsonl"
            first = {"decision_id": "d-1", "candidate_id": "candidate-1", "decision": "hold"}
            second = {"decision_id": "d-2", "candidate_id": "candidate-1", "decision": "exclude"}
            append_review_decision(first, path)
            original = path.read_bytes()
            append_review_decision(second, path)
            self.assertTrue(path.read_bytes().startswith(original))
            with self.assertRaises(ValueError):
                append_review_decision(first, path)

    def test_decisions_cannot_be_written_to_generated_queue_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture-candidates.jsonl"
            with self.assertRaises(ValueError):
                append_review_decision(
                    {"decision_id": "d-1", "candidate_id": "candidate-1"}, path
                )


if __name__ == "__main__":
    unittest.main()
