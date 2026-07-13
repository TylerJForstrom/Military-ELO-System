import unittest

from military_elo.ingest.stage_open_data import _cluster_temporal_segments, _year_range


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


if __name__ == "__main__":
    unittest.main()
