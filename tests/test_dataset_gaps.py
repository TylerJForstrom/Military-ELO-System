import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path

from scripts.build_brecke_war_registry import strip_brecke_date_suffix
from scripts.report_dataset_gaps import (
    EARTH_RADIUS_KM,
    brecke_coverage,
    build_report,
    century_bucket,
    deduplicate_wikidata_candidates,
    haversine_km,
    parse_signed_year,
    write_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _wikidata(
    *,
    candidate_id: str = "Q1",
    name: str = "Battle of Test",
    date: str = "1200-01-01T00:00:00Z",
    latitude: str | None = "10",
    longitude: str | None = "20",
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "name": name,
        "date": date,
        "latitude": latitude,
        "longitude": longitude,
        "countries": ["Q17"],
        "participants": [
            {"uri": "http://www.wikidata.org/entity/Q10"},
            {"uri": "http://www.wikidata.org/entity/Q20"},
        ],
        "kind": "engagement",
    }


def _hced(
    *,
    candidate_id: str = "hced-Test1200-1",
    name: str = "Test",
    year: int = 1200,
    latitude: str | None = "10",
    longitude: str | None = "20",
    war_names: list[str] | None = None,
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "name": name,
        "year_low": year,
        "year_best": year,
        "year_high": year,
        "latitude": latitude,
        "longitude": longitude,
        "war_names": war_names or [],
    }


def _latitude_at_distance(origin: float, distance_km: float) -> str:
    return str(origin + math.degrees(distance_km / EARTH_RADIUS_KM))


class WikidataGapDedupTests(unittest.TestCase):
    def test_signed_year_and_century_buckets_support_bce(self) -> None:
        self.assertEqual(parse_signed_year("-0213-01-01T00:00:00Z"), -213)
        self.assertEqual(century_bucket(-213)[1], "3rd century BCE")
        self.assertEqual(century_bucket(1200)[1], "12th century CE")

    def test_match_requires_name_year_and_distance_strictly_below_25_km(self) -> None:
        near = _hced(
            candidate_id="hced-near",
            year=1201,
            latitude=_latitude_at_distance(10.0, 24.999),
        )
        annotation = deduplicate_wikidata_candidates([_wikidata()], [near])[0]
        self.assertEqual(
            [row["candidate_id"] for row in annotation["hced_match_candidates"]],
            ["hced-near"],
        )

        boundary = _hced(
            candidate_id="hced-boundary",
            latitude=_latitude_at_distance(10.0, 25.0),
        )
        distance = haversine_km(
            (10.0, 20.0), (float(boundary["latitude"]), 20.0)
        )
        self.assertAlmostEqual(distance, 25.0, places=7)
        annotation = deduplicate_wikidata_candidates([_wikidata()], [boundary])[0]
        self.assertEqual(annotation["hced_match_candidates"], [])

    def test_missing_coordinates_and_year_gap_do_not_match(self) -> None:
        rows = [
            _hced(candidate_id="hced-no-point", latitude=None, longitude=None),
            _hced(candidate_id="hced-year-gap", year=1202),
        ]
        annotation = deduplicate_wikidata_candidates([_wikidata()], rows)[0]
        self.assertEqual(annotation["hced_match_candidates"], [])
        self.assertEqual(
            [row["candidate_id"] for row in annotation["hced_same_name_year_candidates"]],
            ["hced-no-point"],
        )

    def test_multiple_matches_are_sorted_by_distance_then_candidate_id(self) -> None:
        rows = [
            _hced(
                candidate_id="hced-farther",
                latitude=_latitude_at_distance(10.0, 10.0),
            ),
            _hced(
                candidate_id="hced-nearer",
                latitude=_latitude_at_distance(10.0, 2.0),
            ),
        ]
        annotation = deduplicate_wikidata_candidates([_wikidata()], rows)[0]
        self.assertEqual(
            [row["candidate_id"] for row in annotation["hced_match_candidates"]],
            ["hced-nearer", "hced-farther"],
        )


class BreckeGapTests(unittest.TestCase):
    def test_exact_suffix_rule_does_not_expand_abbreviated_one_digit_ranges(self) -> None:
        self.assertEqual(strip_brecke_date_suffix("Example, 1400-02"), "Example")
        self.assertEqual(
            strip_brecke_date_suffix("Example, 1400-2"), "Example, 1400-2"
        )

    def test_committed_sidecar_preserves_source_anomalies_and_has_no_outcomes(self) -> None:
        rows = [
            json.loads(line)
            for line in (PROJECT_ROOT / "data/reference/brecke-wars.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        statuses: dict[str, int] = {}
        for row in rows:
            statuses[row["interval_status"]] = statuses.get(row["interval_status"], 0) + 1
        self.assertEqual(len(rows), 3708)
        self.assertEqual(len({row["brecke_id"] for row in rows}), 3708)
        self.assertEqual(
            statuses, {"closed": 3681, "invalid_reversed": 1, "open_end": 26}
        )
        self.assertTrue(all(row["outcome_available"] is False for row in rows))
        self.assertTrue(
            all(row["rating_use"] == "coverage_cross_check_only" for row in rows)
        )
        self.assertEqual(
            {row["source_snapshot_sha256"] for row in rows},
            {"8e685bbf9c67b38e5ba1474cc2a836e6eb9bff98bc223beca681363523a14ea8"},
        )
        self.assertEqual(
            {row["source_url"] for row in rows},
            {
                "https://brecke.inta.gatech.edu/wp-content/uploads/sites/19/"
                "2018/09/Conflict-Catalog-18-vars.xlsx"
            },
        )

    def test_brecke_match_is_exact_and_time_overlapping(self) -> None:
        brecke = [
            {
                "brecke_id": "brecke-1",
                "aliases": ["Fixture War"],
                "war_name": "Fixture War",
                "start_year": 1190,
                "end_year": 1210,
                "interval_status": "closed",
                "region_code": 1,
                "region_label": "Brecke region 1",
            }
        ]
        result = brecke_coverage(
            brecke,
            [_hced(candidate_id="hced-war", year=1200, war_names=["Fixture War"])],
        )
        self.assertEqual(result["summary"]["verified_hced_match"], 1)
        self.assertEqual(
            result["records"][0]["hced_match_candidates"], ["hced-war"]
        )


class GapReportDeterminismTests(unittest.TestCase):
    def test_report_is_deterministic_and_does_not_rewrite_review_queue(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wikidata = root / "wikidata.jsonl"
            hced = root / "hced.jsonl"
            brecke = root / "brecke.jsonl"
            funnel = root / "funnel.json"
            wikidata.write_text(json.dumps(_wikidata()) + "\n", encoding="utf-8")
            hced.write_text(json.dumps(_hced()) + "\n", encoding="utf-8")
            brecke.write_text(
                json.dumps(
                    {
                        "brecke_id": "brecke-1",
                        "aliases": ["Fixture War"],
                        "war_name": "Fixture War",
                        "start_year": 1200,
                        "end_year": 1200,
                        "interval_status": "closed",
                        "region_code": 1,
                        "region_label": "Brecke region 1",
                        "source_snapshot": "brecke.xlsx",
                        "source_snapshot_sha256": "abc123",
                        "source_url": "https://example.test/brecke.xlsx",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            funnel.write_text(
                json.dumps(
                    {
                        "greedy_batch": {
                            "ranking": [
                                {
                                    "rank": 1,
                                    "label": "algeria",
                                    "marginal_events": 1,
                                    "cumulative_events": 1,
                                }
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )
            queue_hash = hashlib.sha256(wikidata.read_bytes()).hexdigest()
            outputs: list[tuple[bytes, bytes]] = []
            for suffix in ("a", "b"):
                report = build_report(wikidata, hced, brecke, funnel)
                output_json = root / f"report-{suffix}.json"
                output_markdown = root / f"report-{suffix}.md"
                write_report(report, output_json, output_markdown)
                outputs.append((output_json.read_bytes(), output_markdown.read_bytes()))

            self.assertEqual(outputs[0], outputs[1])
            report_payload = json.loads(outputs[0][0])
            self.assertEqual(
                report_payload["brecke_coverage"]["source_provenance"],
                {
                    "source_snapshot": "brecke.xlsx",
                    "source_snapshot_sha256": "abc123",
                    "source_url": "https://example.test/brecke.xlsx",
                },
            )
            self.assertIn(b"https://example.test/brecke.xlsx", outputs[0][1])
            self.assertIn(b"`abc123`", outputs[0][1])
            self.assertEqual(
                hashlib.sha256(wikidata.read_bytes()).hexdigest(), queue_hash
            )


if __name__ == "__main__":
    unittest.main()
