import json
import re
import unittest
from dataclasses import replace
from pathlib import Path

from military_elo.canonical import (
    CanonicalEvent,
    ParticipationEpisode,
    UncertainDate,
    UncertainDateInterval,
    date_bounds,
    date_sort_key,
    geometry_validation_error,
)
from military_elo.models import Entity, Event, Participant


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

    def test_interval_constructor_requires_uncertain_date_endpoints(self):
        with self.assertRaises(TypeError):
            UncertainDateInterval(
                start={"best": 1914},
                end=UncertainDate.exact(1915),
            )
        with self.assertRaises(TypeError):
            UncertainDateInterval(
                start=UncertainDate.exact(1914),
                end=1915,
            )

    def test_boolean_dates_never_alias_integer_years(self):
        self.assertIsNone(date_bounds(True))
        with self.assertRaises(TypeError):
            UncertainDate(best=True, precision="year")
        with self.assertRaises(TypeError):
            UncertainDateInterval.from_dict(
                {
                    "start": {
                        "low": None,
                        "best": True,
                        "high": None,
                        "precision": "year",
                    },
                    "end": UncertainDate.exact(2, "year").to_dict(),
                }
            )

    def test_date_helpers_fail_closed_for_arbitrary_runtime_types(self):
        for malformed in (1.5, {}, [], object()):
            with self.subTest(value=type(malformed).__name__):
                self.assertIsNone(date_bounds(malformed))
                self.assertIsNone(date_sort_key(malformed))

    def test_nested_date_parsers_reject_unknown_keys_but_keep_bounded_aliases(self):
        with self.assertRaisesRegex(ValueError, "unknown field"):
            UncertainDate.from_dict(
                {
                    "low": 1914,
                    "best": 1914,
                    "high": 1914,
                    "precision": "year",
                    "calendar_guess": "Julian",
                }
            )
        with self.assertRaisesRegex(ValueError, "unknown field"):
            UncertainDateInterval.from_dict(
                {
                    "start": UncertainDate.exact(1914, "year").to_dict(),
                    "end": UncertainDate.exact(1915, "year").to_dict(),
                    "end_guess": 1916,
                }
            )

        aliased = UncertainDate.from_dict(
            {
                "earliest": 1914,
                "best": 1915,
                "latest": 1916,
                "precision": "range",
            }
        )
        self.assertEqual((aliased.low, aliased.high), (1914, 1916))
        flat_interval = UncertainDateInterval.from_dict(
            {
                "start_low": 1914,
                "start_best": 1914,
                "start_high": 1915,
                "end_low": 1915,
                "end_best": 1916,
                "end_high": 1916,
                "precision": "year",
            }
        )
        self.assertEqual(flat_interval.start.low, 1914)
        with self.assertRaisesRegex(ValueError, "cannot mix"):
            UncertainDateInterval.from_dict(
                {
                    "start": UncertainDate.exact(1914).to_dict(),
                    "end": UncertainDate.exact(1915).to_dict(),
                    "start_low": 1914,
                }
            )


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

    def test_parser_requires_nonblank_typed_identity_fields(self):
        base = {
            "id": "episode-1",
            "entity_id": "entity-1",
            "side": "a",
            "role": "primary",
        }
        for field_name in ("id", "entity_id", "side", "role"):
            with self.subTest(field=field_name, case="missing"):
                malformed = dict(base)
                malformed.pop(field_name)
                with self.assertRaises(ValueError):
                    ParticipationEpisode.from_dict(malformed)
            with self.subTest(field=field_name, case="blank"):
                with self.assertRaises(ValueError):
                    ParticipationEpisode.from_dict({**base, field_name: " \t"})
            with self.subTest(field=field_name, case="type"):
                with self.assertRaises(TypeError):
                    ParticipationEpisode.from_dict({**base, field_name: 7})

        with self.assertRaisesRegex(ValueError, "unknown field"):
            ParticipationEpisode.from_dict({**base, "objective": "hold"})
        with self.assertRaises(ValueError):
            ParticipationEpisode.from_dict({**base, "claim_ids": [" "]})

    def test_parser_keeps_only_explicit_episode_aliases(self):
        episode = ParticipationEpisode.from_dict(
            {
                "episode_id": "episode-legacy",
                "entity_id": "entity-1",
                "side": "a",
                "role": "primary",
                "entry_date": 1914,
                "exit_date": 1915,
            }
        )
        self.assertEqual(episode.id, "episode-legacy")
        self.assertEqual(episode.entry.best, 1914)
        with self.assertRaisesRegex(ValueError, "both id and episode_id"):
            ParticipationEpisode.from_dict(
                {
                    "id": "episode-1",
                    "episode_id": "episode-legacy",
                    "entity_id": "entity-1",
                    "side": "a",
                    "role": "primary",
                }
            )

    def test_direct_constructor_enforces_required_text_and_date_types(self):
        for field_name in ("id", "entity_id", "side", "role"):
            values = {
                "id": "episode-1",
                "entity_id": "entity-1",
                "side": "a",
                "role": "primary",
            }
            with self.subTest(field=field_name, case="blank"), self.assertRaises(
                ValueError
            ):
                ParticipationEpisode(**{**values, field_name: " "})
            with self.subTest(field=field_name, case="type"), self.assertRaises(
                TypeError
            ):
                ParticipationEpisode(**{**values, field_name: 7})
        with self.assertRaises(TypeError):
            ParticipationEpisode("episode-1", "entity-1", "a", "primary", entry=1914)
        with self.assertRaises(TypeError):
            ParticipationEpisode("episode-1", "entity-1", "a", "primary", exit={})
        with self.assertRaises(ValueError):
            ParticipationEpisode(
                "episode-1",
                "entity-1",
                "a",
                "primary",
                claim_ids=(" ",),
            )
        with self.assertRaisesRegex(ValueError, "both entry and entry_date"):
            ParticipationEpisode.from_dict(
                {
                    "id": "episode-1",
                    "entity_id": "entity-1",
                    "side": "a",
                    "role": "primary",
                    "entry": 1914,
                    "entry_date": 1914,
                }
            )


class CanonicalEventTests(unittest.TestCase):
    def test_baseline_positional_constructor_order_is_unchanged(self):
        interval = UncertainDateInterval(
            UncertainDate.exact(1900, "year"),
            UncertainDate.exact(1901, "year"),
        )
        episode = ParticipationEpisode(
            "episode-1",
            "entity-1",
            "a",
            "primary",
        )
        event = CanonicalEvent(
            "event-positional",
            "Positional Event",
            ("Alias",),
            ("parent-1",),
            ("child-1",),
            interval,
            {"type": "Point", "coordinates": [1, 2]},
            (episode,),
            ("claim-1",),
            ("decision-1",),
            "engagement",
            "tactical",
            "land",
            "Region",
            "accepted",
        )
        self.assertEqual(event.participation_episodes, (episode,))
        self.assertEqual(event.claim_ids, ("claim-1",))
        self.assertEqual(event.adjudication_ids, ("decision-1",))
        self.assertEqual(event.event_type, "engagement")
        self.assertEqual(event.status, "accepted")
        self.assertIsNone(event.hced_candidate_id)
        self.assertEqual(CanonicalEvent.from_dict(event.to_dict()), event)

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

    def test_parser_rejects_type_laundering_and_blank_stable_references(self):
        base = {"id": "event-1", "name": "Event"}
        for field_name in ("id", "name"):
            with self.subTest(field=field_name, case="missing"):
                malformed = dict(base)
                malformed.pop(field_name)
                with self.assertRaises(ValueError):
                    CanonicalEvent.from_dict(malformed)
            with self.subTest(field=field_name, case="blank"):
                with self.assertRaises(ValueError):
                    CanonicalEvent.from_dict({**base, field_name: " \n"})
            with self.subTest(field=field_name, case="type"):
                with self.assertRaises(TypeError):
                    CanonicalEvent.from_dict({**base, field_name: 7})

        for field_name in ("event_type", "layer", "domain", "region"):
            with self.subTest(optional=field_name), self.assertRaises(TypeError):
                CanonicalEvent.from_dict({**base, field_name: 7})
        with self.assertRaises(TypeError):
            CanonicalEvent.from_dict({**base, "status": None})
        for field_name in (
            "parent_event_ids",
            "child_event_ids",
            "claim_ids",
            "adjudication_ids",
        ):
            with self.subTest(reference=field_name), self.assertRaises(ValueError):
                CanonicalEvent.from_dict({**base, field_name: [" "]})
        with self.assertRaises(ValueError):
            CanonicalEvent.from_dict({**base, "parent_event_id": " "})

        compatible = CanonicalEvent.from_dict(
            {
                "event_id": "event-legacy",
                "canonical_name": "Legacy alias",
                "future_compatibility_field": {"kept_by_source": True},
            }
        )
        self.assertEqual((compatible.id, compatible.name), ("event-legacy", "Legacy alias"))
        for canonical, alias in (("id", "event_id"), ("name", "canonical_name")):
            with self.subTest(alias=alias), self.assertRaisesRegex(
                ValueError, f"both {canonical} and {alias}"
            ):
                CanonicalEvent.from_dict({**base, alias: f"duplicate-{alias}"})

    def test_direct_constructor_enforces_event_component_types(self):
        for field_name in ("id", "name", "status"):
            values = {"id": "event-1", "name": "Event", "status": "proposed"}
            with self.subTest(field=field_name, case="blank"), self.assertRaises(
                ValueError
            ):
                CanonicalEvent(**{**values, field_name: " "})
            with self.subTest(field=field_name, case="type"), self.assertRaises(
                TypeError
            ):
                CanonicalEvent(**{**values, field_name: 7})
        for field_name in ("event_type", "layer", "domain", "region"):
            with self.subTest(optional=field_name), self.assertRaises(TypeError):
                CanonicalEvent("event-1", "Event", **{field_name: 7})
        with self.assertRaises(TypeError):
            CanonicalEvent("event-1", "Event", date_interval={})
        with self.assertRaises(TypeError):
            CanonicalEvent("event-1", "Event", participation_episodes=({},))
        for field_name in (
            "parent_event_ids",
            "child_event_ids",
            "claim_ids",
            "adjudication_ids",
        ):
            with self.subTest(reference=field_name), self.assertRaises(ValueError):
                CanonicalEvent("event-1", "Event", **{field_name: (" ",)})

    def test_canonical_geometry_is_detached_deeply_frozen_and_thawed(self):
        geometry = {
            "type": "GeometryCollection",
            "geometries": [
                {"type": "Point", "coordinates": [6.1, 50.7]},
            ],
            "properties": {"labels": ["original"]},
        }
        event = CanonicalEvent("event-1", "Event", geometry=geometry)
        expected = event.to_dict()["geometry"]

        geometry["geometries"][0]["coordinates"][0] = 99.0
        geometry["properties"]["labels"][0] = "mutated"
        self.assertEqual(event.to_dict()["geometry"], expected)
        with self.assertRaises(TypeError):
            event.geometry["type"] = "Point"
        with self.assertRaises(TypeError):
            event.geometry["properties"]["labels"][0] = "mutated"

        exported = event.to_dict()
        self.assertIsInstance(exported["geometry"], dict)
        self.assertIsInstance(exported["geometry"]["geometries"], list)
        exported["geometry"]["properties"]["labels"][0] = "output mutation"
        self.assertEqual(event.to_dict()["geometry"], expected)
        self.assertEqual(CanonicalEvent.from_dict(event.to_dict()), event)

    def test_huge_integer_geometry_ordinates_do_not_overflow(self):
        huge = 10**10000
        for longitude in (huge, -huge):
            with self.subTest(sign=1 if longitude > 0 else -1):
                self.assertIsNone(
                    geometry_validation_error(
                        {"type": "Point", "coordinates": [longitude, 0]}
                    )
                )
        for coordinates in ([180, 90], [-180.0, -90.0]):
            with self.subTest(boundary=coordinates):
                self.assertIsNone(
                    geometry_validation_error(
                        {"type": "Point", "coordinates": coordinates}
                    )
                )

    def test_legacy_event_geometry_is_detached_deeply_frozen_and_thawed(self):
        geometry = {
            "type": "Point",
            "coordinates": [10.0, 20.0],
            "properties": {"labels": ["original"]},
        }
        raw = {
            "id": "event-legacy",
            "name": "Legacy event",
            "year": 1914,
            "event_type": "engagement",
            "participants": [
                {"entity_id": "a", "side": "one"},
                {"entity_id": "b", "side": "two"},
            ],
            "source_ids": [],
            "geometry": geometry,
        }
        event = Event.from_dict(raw)
        expected = event.to_dict()["geometry"]
        geometry["coordinates"][0] = 99.0
        geometry["properties"]["labels"][0] = "mutated"
        self.assertEqual(event.to_dict()["geometry"], expected)
        with self.assertRaises(TypeError):
            event.geometry["properties"]["labels"][0] = "mutated"
        exported = event.to_dict()
        exported["geometry"]["coordinates"][0] = 88.0
        self.assertEqual(event.to_dict()["geometry"], expected)
        self.assertEqual(Event.from_dict(event.to_dict()), event)

    def test_legacy_direct_constructors_guard_new_evidence_components(self):
        participant = Participant("entity-a", "a")
        with self.assertRaises(TypeError):
            replace(participant, entry=1914)
        with self.assertRaises(TypeError):
            replace(participant, exit={})
        for field_name in ("claim_ids", "adjudication_ids"):
            with self.subTest(participant_ref=field_name), self.assertRaises(ValueError):
                replace(participant, **{field_name: (" ",)})

        entity = Entity("entity-a", "A", "state", 1900)
        for field_name in ("claim_ids", "adjudication_ids"):
            with self.subTest(entity_ref=field_name), self.assertRaises(ValueError):
                replace(entity, **{field_name: (" ",)})

        event = Event.from_dict(
            {
                "id": "event-legacy",
                "name": "Legacy event",
                "year": 1914,
                "event_type": "engagement",
                "participants": [
                    {"entity_id": "a", "side": "one"},
                    {"entity_id": "b", "side": "two"},
                ],
                "source_ids": [],
            }
        )
        with self.assertRaises(TypeError):
            replace(event, date_interval={})
        with self.assertRaises(TypeError):
            replace(event, participation_episodes=({},))
        for invalid_parent in (123, " ", [], {}):
            with self.subTest(parent_event_id=invalid_parent), self.assertRaises(
                (TypeError, ValueError)
            ):
                replace(event, parent_event_id=invalid_parent)
            with self.subTest(parsed_parent=invalid_parent), self.assertRaises(
                (TypeError, ValueError)
            ):
                Event.from_dict({**event.to_dict(), "parent_event_id": invalid_parent})
        for field_name in (
            "parent_event_ids",
            "child_event_ids",
            "claim_ids",
            "adjudication_ids",
        ):
            with self.subTest(event_ref=field_name), self.assertRaises(ValueError):
                replace(event, **{field_name: (" ",)})

        for canonical, alias in (("entry", "entry_date"), ("exit", "exit_date")):
            with self.subTest(alias=alias), self.assertRaisesRegex(
                ValueError, f"both {canonical} and {alias}"
            ):
                Participant.from_dict(
                    {
                        "entity_id": "entity-a",
                        "side": "a",
                        canonical: 1914,
                        alias: 1914,
                    }
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
        nonblank_definitions = [
            schema["properties"]["id"],
            schema["properties"]["name"],
            schema["properties"]["source_ids"]["items"],
            schema["properties"]["parent_event_id"]["anyOf"][0],
            schema["properties"]["parent_event_ids"]["items"],
            schema["properties"]["child_event_ids"]["items"],
            schema["properties"]["claim_ids"]["items"],
            schema["properties"]["adjudication_ids"]["items"],
            schema["$defs"]["participationEpisode"]["properties"]["id"],
            schema["$defs"]["participationEpisode"]["properties"]["entity_id"],
            schema["$defs"]["participationEpisode"]["properties"]["side"],
            schema["$defs"]["participationEpisode"]["properties"]["role"],
            schema["$defs"]["participationEpisode"]["properties"]["claim_ids"]["items"],
            schema["$defs"]["legacyParticipant"]["properties"]["entity_id"],
            schema["$defs"]["legacyParticipant"]["properties"]["side"],
        ]
        for definition in nonblank_definitions:
            self.assertEqual(definition["pattern"], r".*\S.*")


if __name__ == "__main__":
    unittest.main()
