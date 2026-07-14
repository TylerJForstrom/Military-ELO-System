import json
import re
import unittest
from pathlib import Path

from military_elo.canonical import (
    CanonicalEvent,
    ParticipationEpisode,
    UncertainDate,
    UncertainDateInterval,
    date_bounds,
)


ROOT = Path(__file__).resolve().parents[1]


class UncertainDateTests(unittest.TestCase):
    def test_uncertain_interval_round_trip_preserves_bounds(self):
        interval = UncertainDateInterval(
            start=UncertainDate(-480, -480, -479, "year"),
            end=UncertainDate(-479, -479, -478, "year"),
        )
        self.assertEqual(interval.validation_errors(), [])
        self.assertEqual(UncertainDateInterval.from_dict(interval.to_dict()), interval)

    def test_year_zero_and_trailing_junk_are_invalid(self):
        zero = UncertainDate.exact(0, "year")
        junk = UncertainDate.exact("1914-01-01junk", "day")
        self.assertTrue(any("year zero" in item for item in zero.validation_errors()))
        self.assertTrue(any("signed year" in item for item in junk.validation_errors()))
        self.assertTrue(UncertainDate.exact("١٩١٤", "year").validation_errors())

    def test_month_day_and_proleptic_gregorian_leap_rules_are_validated(self):
        self.assertTrue(UncertainDate.exact("1914-13-01", "day").validation_errors())
        self.assertTrue(UncertainDate.exact("1900-02-29", "day").validation_errors())
        self.assertEqual(UncertainDate.exact("2000-02-29", "day").validation_errors(), [])
        self.assertTrue(UncertainDate.exact("2001-04-31", "day").validation_errors())

    def test_precision_aware_bounds_cover_whole_years_and_months(self):
        self.assertEqual(date_bounds(1914), ((1914, 1, 1), (1914, 12, 31)))
        self.assertEqual(
            date_bounds("2000-02"),
            ((2000, 2, 1), (2000, 2, 29)),
        )
        mixed = UncertainDate("1914", "1914-12-01", "1914", "range")
        self.assertEqual(mixed.validation_errors(), [])

    def test_whitespace_dates_and_blank_precision_are_invalid(self):
        self.assertTrue(UncertainDate.exact(" 1914 ", "year").validation_errors())
        self.assertTrue(UncertainDate.exact(1914, "").validation_errors())
        self.assertTrue(
            UncertainDate.from_dict(
                {"low": 1914, "best": None, "high": 1914, "precision": None}
            ).validation_errors()
        )

    def test_inverted_interval_is_invalid(self):
        interval = UncertainDateInterval(
            start=UncertainDate.exact(1918, "year"),
            end=UncertainDate.exact(1914, "year"),
        )
        self.assertTrue(any("start" in item for item in interval.validation_errors()))


class ParticipationEpisodeTests(unittest.TestCase):
    def test_unknown_contribution_is_not_fabricated(self):
        episode = ParticipationEpisode(
            id="episode-1",
            entity_id="entity-1",
            side="a",
            role="major_ally",
        )
        self.assertIsNone(episode.contribution)
        self.assertNotIn("contribution", episode.to_dict())

    def test_contribution_and_entry_exit_bounds_are_validated(self):
        episode = ParticipationEpisode(
            id="episode-1",
            entity_id="entity-1",
            side="a",
            role="primary",
            entry=UncertainDate.exact("1918-01-01", "day"),
            exit=UncertainDate.exact("1917-12-31", "day"),
            contribution=1.2,
        )
        errors = episode.validation_errors()
        self.assertTrue(any("contribution" in item for item in errors))
        self.assertTrue(any("entry" in item and "exit" in item for item in errors))
        with self.assertRaises(TypeError):
            ParticipationEpisode.from_dict(
                {
                    "id": "episode-bool",
                    "entity_id": "entity-1",
                    "side": "a",
                    "role": "primary",
                    "contribution": True,
                }
            )
        with self.assertRaises(TypeError):
            ParticipationEpisode.from_dict(
                {
                    "id": "episode-string",
                    "entity_id": "entity-1",
                    "side": "a",
                    "role": "primary",
                    "contribution": "0.5",
                }
            )


class CanonicalEventTests(unittest.TestCase):
    def test_aliases_hierarchy_date_geometry_and_episodes_round_trip(self):
        event = CanonicalEvent(
            id="event-1",
            name="Canonical Battle",
            aliases=("Battle B", "Battle A", "Battle A"),
            parent_event_ids=("war-1",),
            child_event_ids=("action-2", "action-1"),
            date_interval=UncertainDateInterval(
                start=UncertainDate(1914, 1914, 1915, "year"),
                end=UncertainDate(1915, 1915, 1916, "year"),
            ),
            geometry={"type": "Point", "coordinates": [6.1, 50.7]},
            participation_episodes=(
                ParticipationEpisode(
                    id="episode-a",
                    entity_id="entity-a",
                    side="a",
                    role="primary",
                    entry=UncertainDate.exact(1914, "year"),
                    exit=UncertainDate.exact(1915, "year"),
                    contribution=0.8,
                    objectives=("hold the position",),
                    claim_ids=("claim-1",),
                ),
            ),
            claim_ids=("claim-2", "claim-1"),
            adjudication_ids=("decision-2", "decision-1"),
            event_type="engagement",
            layer="tactical",
            domain="land",
            region="Western Europe",
        )
        output = event.to_dict()
        self.assertEqual(output["aliases"], ["Battle A", "Battle B"])
        self.assertEqual(output["child_event_ids"], ["action-1", "action-2"])
        self.assertEqual(output["adjudication_ids"], ["decision-1", "decision-2"])
        self.assertEqual(CanonicalEvent.from_dict(output), event)

    def test_singular_and_plural_parent_links_merge_deterministically(self):
        event = CanonicalEvent.from_dict(
            {
                "id": "event-1",
                "name": "Event",
                "parent_event_id": "war-1",
                "parent_event_ids": ["campaign-1", "war-1"],
            }
        )
        self.assertEqual(event.parent_event_ids, ("campaign-1", "war-1"))
        with self.assertRaises(TypeError):
            CanonicalEvent.from_dict(
                {"id": "bad", "name": "Bad", "claim_ids": "claim-1"}
            )
        for invalid in ("", False, {}):
            with self.subTest(invalid=invalid), self.assertRaises(TypeError):
                CanonicalEvent.from_dict(
                    {"id": "bad-parent", "name": "Bad", "parent_event_ids": invalid}
                )
        with self.assertRaises(TypeError):
            CanonicalEvent(
                "bad-episodes",
                "Bad",
                participation_episodes={
                    ParticipationEpisode("episode", "entity", "a", "primary")
                },
            )

    def test_event_schema_is_compatibility_oriented(self):
        schema = json.loads((ROOT / "schemas" / "event.schema.json").read_text(encoding="utf-8"))
        self.assertTrue(schema["additionalProperties"])
        self.assertEqual(schema["required"], ["id", "name"])
        self.assertIn("uncertainDateInterval", schema["$defs"])
        self.assertIn("participationEpisode", schema["$defs"])
        pattern = re.compile(schema["$defs"]["dateValue"]["oneOf"][1]["pattern"])
        for zero in ("0", "00", "0000", "-0", "-0000-01"):
            self.assertIsNone(pattern.fullmatch(zero))


if __name__ == "__main__":
    unittest.main()
