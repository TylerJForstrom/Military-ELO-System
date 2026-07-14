import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from military_elo.ingest.provenance import (
    CorpusLockError,
    review_candidates_bytes,
)
from military_elo.ingest.stage_open_data import (
    _cluster_temporal_segments,
    _year_range,
    stage_iwbd,
)
from scripts.stage_open_data import stage_selected


IWBD_FIXTURE = (
    "cowNum,iwdNum,warName,battleName,attacker,defender,startDate,endDate,"
    "battleLength,victor,victorWarLevel,victorBattleLevel\n"
    "7,9,Fixture War,Fixture Battle,Alpha,Beta,1900-01-01,1900-01-02,2,"
    "Alpha,attacker,attacker\n"
).encode("utf-8")


def _iwbd_candidate() -> dict[str, object]:
    return {
        "candidate_id": "iwbd-7-9-2",
        "source": "iwbd",
        "source_snapshot": "data/raw/iwbd/snapshot.bin",
        "source_row": 2,
        "review_status": "needs_review",
        "do_not_rate_automatically": True,
        "proposed_event_type": "engagement",
        "name": "Fixture Battle",
        "war_name": "Fixture War",
        "start_date": "1900-01-01",
        "end_date": "1900-01-02",
        "duration_days": "2",
        "attacker_raw": "Alpha",
        "defender_raw": "Beta",
        "winner_raw": "Alpha",
        "war_level_victor_role": "attacker",
        "battle_level_victor_role": "attacker",
        "extraction_notes": [
            "Resolve attacker, defender and victor labels to time-bounded entities.",
            "Keep battle outcome separate from the enclosing war outcome.",
        ],
    }


def _iwbd_lock() -> dict[str, object]:
    output = review_candidates_bytes([_iwbd_candidate()])
    return {
        "schema_version": 1,
        "corpus_id": "iwbd-fixture",
        "created_at": "2026-07-14T00:00:00Z",
        "transformation_version": "open-data-review-v1",
        "datasets": {
            "iwbd": {
                "title": "IWBD fixture",
                "source_url": "https://example.test/iwbd",
                "dataset_version": "v1",
                "license": {"id": "CC0-1.0", "classification": "open_core"},
                "retrieval": {
                    "retrieved_at": "2026-07-13T00:00:00Z",
                    "method": "https",
                },
                "files": [
                    {
                        "filename": "snapshot.bin",
                        "sha256": hashlib.sha256(IWBD_FIXTURE).hexdigest(),
                        "size_bytes": len(IWBD_FIXTURE),
                    }
                ],
            }
        },
        "transformations": {
            "iwbd-review": {
                "transformer": "stage_iwbd",
                "version": "1",
                "inputs": {"data": {"dataset": "iwbd", "filename": "snapshot.bin"}},
                "output": {
                    "kind": "generated_review_queue",
                    "filename": "iwbd-candidates.jsonl",
                    "sha256": hashlib.sha256(output).hexdigest(),
                    "size_bytes": len(output),
                    "record_count": 1,
                },
            }
        },
    }


class YearRangeTests(unittest.TestCase):
    def test_positive_range_keeps_both_years_positive(self) -> None:
        self.assertEqual(_year_range("1943-1944"), (1943, 1944, 1944))

    def test_single_bce_year_remains_negative(self) -> None:
        self.assertEqual(_year_range("-1468"), (-1468, -1468, -1468))

    def test_bce_range_is_supported(self) -> None:
        self.assertEqual(_year_range("-480--479"), (-480, -480, -479))

    def test_malformed_abbreviated_range_is_quarantined(self) -> None:
        self.assertEqual(_year_range("1817-1"), (None, None, None))


class CliopatriaIntervalTests(unittest.TestCase):
    def test_non_contiguous_segments_are_detected_as_coverage_groups(self) -> None:
        segments = [
            {"name": "Example Kingdom", "start_year": start, "end_year": end}
            for start, end in ((500, 600), (601, 650), (1800, 1900))
        ]
        clusters = _cluster_temporal_segments(segments)

        self.assertEqual(len(clusters), 2)
        self.assertEqual(
            [
                (
                    min(row["start_year"] for row in cluster),
                    max(row["end_year"] for row in cluster),
                )
                for cluster in clusters
            ],
            [(500, 650), (1800, 1900)],
        )


class LockedStagingTests(unittest.TestCase):
    def _write_lock(self, root: Path, document: dict[str, object] | None = None) -> Path:
        path = root / "corpus.lock.json"
        path.write_text(json.dumps(document or _iwbd_lock()), encoding="utf-8")
        return path

    def _write_raw(self, root: Path, payload: bytes = IWBD_FIXTURE) -> Path:
        raw_root = root / "raw"
        source_dir = raw_root / "iwbd"
        source_dir.mkdir(parents=True)
        (source_dir / "snapshot.bin").write_bytes(payload)
        stray = source_dir / "newer-unlocked.csv"
        stray.write_bytes(IWBD_FIXTURE)
        os.utime(stray, (2_000_000_000, 2_000_000_000))
        return raw_root

    def test_absolute_fixture_roots_restaged_byte_identically_and_ignore_newer_strays(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock_path = self._write_lock(root)
            outputs = []
            for name in ("machine-a", "machine-b"):
                machine = root / name
                raw_root = self._write_raw(machine)
                destination = machine / "review" / "iwbd-candidates.jsonl"
                stage_iwbd(raw_root, destination, corpus_lock=lock_path)
                outputs.append(destination.read_bytes())

            self.assertEqual(outputs[0], outputs[1])
            record = json.loads(outputs[0])
            self.assertEqual(record["source_snapshot"], "data/raw/iwbd/snapshot.bin")
            self.assertNotIn(str(root), outputs[0].decode("utf-8"))

    def test_batch_restaging_preserves_nested_human_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock_path = self._write_lock(root)
            raw_root = self._write_raw(root)
            review_root = root / "review"
            decision = review_root / "decisions" / "human.jsonl"
            decision.parent.mkdir(parents=True)
            decision.write_bytes(b'{"decision_id":"d-1"}\n')

            counts = stage_selected(["iwbd"], raw_root, review_root, lock_path)

            self.assertEqual(counts, {"iwbd": 1})
            self.assertEqual(decision.read_bytes(), b'{"decision_id":"d-1"}\n')
            self.assertEqual(
                (review_root / "iwbd-candidates.jsonl").read_bytes(),
                review_candidates_bytes([_iwbd_candidate()]),
            )

    def test_corrupt_input_fails_before_existing_queue_is_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock_path = self._write_lock(root)
            raw_root = self._write_raw(root, payload=b"corrupt")
            destination = root / "review" / "iwbd-candidates.jsonl"
            destination.parent.mkdir()
            destination.write_bytes(b"existing\n")

            with self.assertRaises(CorpusLockError):
                stage_iwbd(raw_root, destination, corpus_lock=lock_path)

            self.assertEqual(destination.read_bytes(), b"existing\n")

    def test_output_or_transform_version_drift_fails_before_replacement(self) -> None:
        for drift in ("output", "version"):
            with self.subTest(drift=drift), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                document = _iwbd_lock()
                if drift == "output":
                    document["transformations"]["iwbd-review"]["output"]["sha256"] = "0" * 64
                else:
                    document["transformations"]["iwbd-review"]["version"] = "2"
                lock_path = self._write_lock(root, document)
                raw_root = self._write_raw(root)
                destination = root / "review" / "iwbd-candidates.jsonl"
                destination.parent.mkdir()
                destination.write_bytes(b"existing\n")

                with self.assertRaises(CorpusLockError):
                    stage_iwbd(raw_root, destination, corpus_lock=lock_path)

                self.assertEqual(destination.read_bytes(), b"existing\n")


if __name__ == "__main__":
    unittest.main()
