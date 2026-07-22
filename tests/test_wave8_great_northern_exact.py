import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_great_northern_exact as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_PREFIX = "hced_wave8_great_northern_exact_"

SWEDEN = "kingdom_sweden"
DENMARK = "kingdom_denmark"
SAXONY = "electorate_saxony_1356"
RUSSIA = "clio_ru_moskva_rurik_dyn_1547_93deb0e2"
PRUSSIA = "kingdom_prussia"

EXPECTED_HASHES = {
    "hced-Gadebusch1712-1": (
        "0ee27a3f3a8a53df31d880d82a31fb009a9537f4c0e0943c377e5709ef4ddf8d"
    ),
    "hced-Tonning1713-1": (
        "1eabbee1c511d4ac367234b412445364bd3d43133fc1f6bfad53e05db8b5d97b"
    ),
    "hced-Stralsund1714-1715-1": (
        "01951636c6c223ae71597edfc6df7ce65328b6e9b9a339c2078076a0c22dbddb"
    ),
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8GreatNorthernExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        entity_snapshot = copy.deepcopy(entities)
        lane.install_wave8_great_northern_exact_entities(entities)
        self.assertEqual(entities, entity_snapshot)

        lane_source_ids = {
            str(item["id"]) for item in lane.WAVE8_GREAT_NORTHERN_EXACT_SOURCES
        }
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        lane.install_wave8_great_northern_exact_sources(sources)

        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_great_northern_exact_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_candidate_set_and_full_locked_row_hashes_are_exact(self):
        self.assertEqual(lane.WAVE8_GREAT_NORTHERN_EXACT_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            lane.WAVE8_GREAT_NORTHERN_EXACT_EXPECTED_CANDIDATE_IDS,
            set(EXPECTED_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_GREAT_NORTHERN_EXACT_CONTRACT_IDS,
            set(EXPECTED_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_GREAT_NORTHERN_EXACT_RESERVED_IDS,
            set(EXPECTED_HASHES),
        )
        self.assertNotIn(
            "hced-Gotland1563-1",
            lane.WAVE8_GREAT_NORTHERN_EXACT_RESERVED_IDS,
        )
        self.assertFalse(lane.WAVE8_GREAT_NORTHERN_EXACT_HOLDS)

        rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if str(row.get("candidate_id")) in EXPECTED_HASHES
        }
        self.assertEqual(set(rows), set(EXPECTED_HASHES))
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_validator_pins_all_three_and_no_more(self):
        self.assertEqual(
            lane.validate_wave8_great_northern_exact_queue_contracts(
                self.hced_rows
            ),
            {
                "holds": 0,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 3,
            },
        )
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if str(row.get("candidate_id")) in EXPECTED_HASHES
        }
        self.assertEqual(
            (
                rows["hced-Gadebusch1712-1"]["side_1_raw"],
                rows["hced-Gadebusch1712-1"]["side_2_raw"],
                rows["hced-Gadebusch1712-1"]["winner_raw"],
            ),
            ("Sweden", "Denmark, Saxony", "Sweden"),
        )
        self.assertEqual(
            (
                rows["hced-Tonning1713-1"]["side_1_raw"],
                rows["hced-Tonning1713-1"]["side_2_raw"],
                rows["hced-Tonning1713-1"]["winner_raw"],
            ),
            ("Denmark, Saxony", "Sweden", "Denmark, Saxony"),
        )
        self.assertEqual(
            (
                rows["hced-Stralsund1714-1715-1"]["side_1_raw"],
                rows["hced-Stralsund1714-1715-1"]["side_2_raw"],
                rows["hced-Stralsund1714-1715-1"]["winner_raw"],
            ),
            ("Denmark, German states", "Sweden", "Denmark, German states"),
        )

    def test_existing_identity_windows_are_reused_without_alias_expansion(self):
        entities = {str(item["id"]): item for item in self.release_entities}
        self.assertEqual(
            lane.validate_wave8_great_northern_exact_existing_entities(entities),
            {"required_existing_entities": 5},
        )
        expected = {
            SWEDEN: ("Kingdom of Sweden", 1523, None),
            DENMARK: ("Kingdom of Denmark", 1523, None),
            SAXONY: ("Electorate of Saxony", 1356, 1806),
            RUSSIA: ("Tsardom of Russia", 1547, 1720),
            PRUSSIA: ("Kingdom of Prussia", 1701, 1871),
        }
        self.assertEqual(
            lane.WAVE8_GREAT_NORTHERN_EXACT_REQUIRED_EXISTING_ENTITY_IDS,
            set(expected),
        )
        self.assertFalse(lane.WAVE8_GREAT_NORTHERN_EXACT_ENTITIES)
        before = copy.deepcopy(entities)
        lane.install_wave8_great_northern_exact_entities(entities)
        self.assertEqual(entities, before)
        for entity_id, (name, start, end) in expected.items():
            with self.subTest(entity_id=entity_id):
                entity = entities[entity_id]
                self.assertEqual(entity["name"], name)
                self.assertEqual((entity["start_year"], entity["end_year"]), (start, end))
                Entity.from_dict(entity)

    def test_sources_parse_and_outcomes_have_independent_source_families(self):
        self.assertEqual(len(lane.WAVE8_GREAT_NORTHERN_EXACT_SOURCES), 7)
        for source in lane.WAVE8_GREAT_NORTHERN_EXACT_SOURCES:
            Source.from_dict(source)
            self.assertIn("outcome", source["evidence_roles"])
        for candidate_id, contract in lane.WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(
                    len(contract["outcome_source_family_ids"]),
                    2,
                )
                self.assertEqual(
                    contract["outcome_source_family_ids"],
                    sorted(set(contract["outcome_source_family_ids"])),
                )
                self.assertLessEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )

    def test_exact_coalitions_and_tactical_outcomes_are_pinned(self):
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        expected = {
            "hced-Gadebusch1712-1": ({SWEDEN}, {DENMARK, SAXONY}),
            "hced-Tonning1713-1": ({DENMARK, RUSSIA, SAXONY}, {SWEDEN}),
            "hced-Stralsund1714-1715-1": (
                {DENMARK, PRUSSIA, SAXONY},
                {SWEDEN},
            ),
        }
        self.assertEqual(set(events), set(expected))
        for candidate_id, (winners, losers) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if item["termination"] == "engagement_victory"
                    },
                    winners,
                )
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if item["termination"] == "engagement_defeat"
                    },
                    losers,
                )
                self.assertFalse(
                    any(
                        "inconclusive" in item["termination"]
                        for item in event["participants"]
                    )
                )
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                Event.from_dict(event)

        tonning = events["hced-Tonning1713-1"]
        tonning_winners = [
            item
            for item in tonning["participants"]
            if item["termination"] == "engagement_victory"
        ]
        self.assertEqual({item["role"] for item in tonning_winners}, {"major_ally"})
        self.assertEqual(
            {item["contribution"] for item in tonning_winners},
            {0.3333},
        )

    def test_canonical_names_ranges_types_and_date_override_are_exact(self):
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        expected = {
            "hced-Gadebusch1712-1": (
                "Battle of Gadebusch",
                1712,
                1712,
                "dual_calendar_day",
                "single_pitched_battle_at_wakenstadt_near_gadebusch",
            ),
            "hced-Tonning1713-1": (
                "Capitulation at Oldenswort",
                1713,
                1713,
                "dual_calendar_day",
                (
                    "stenbock_field_army_capitulation_at_oldenswort_not_the_"
                    "tonning_fortress_siege"
                ),
            ),
            "hced-Stralsund1714-1715-1": (
                "Siege of Stralsund (1715)",
                1715,
                1715,
                "day_range",
                "final_july_december_1715_siege_of_stralsund",
            ),
        }
        for candidate_id, (name, low, high, precision, granularity) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                contract = lane.WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS[candidate_id]
                self.assertEqual(event["name"], name)
                self.assertEqual((event["year"], event["end_year"]), (low, high))
                self.assertEqual(event["event_type"], "engagement")
                self.assertEqual(event["date_precision"], precision)
                self.assertEqual(event["reviewed_granularity"], granularity)
                self.assertEqual(contract["canonical_event"]["granularity"], granularity)

        rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if str(row.get("candidate_id")) in EXPECTED_HASHES
        }
        self.assertEqual(
            (
                rows["hced-Stralsund1714-1715-1"]["year_low"],
                rows["hced-Stralsund1714-1715-1"]["year_high"],
            ),
            (1714, 1715),
        )
        stralsund = lane.WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS[
            "hced-Stralsund1714-1715-1"
        ]
        self.assertIs(stralsund["source_date_override"], True)
        self.assertEqual(
            stralsund["date_source_ids"],
            [
                "wave8_great_northern_exact_ghdi_stralsund",
                "wave8_great_northern_exact_rct_stralsund",
            ],
        )
        self.assertNotIn(
            "source_date_override",
            lane.WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS[
                "hced-Tonning1713-1"
            ],
        )

    def test_event_source_provenance_is_closed_to_each_contract(self):
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        for candidate_id, event in events.items():
            with self.subTest(candidate_id=candidate_id):
                contract = lane.WAVE8_GREAT_NORTHERN_EXACT_CONTRACTS[candidate_id]
                self.assertEqual(
                    event["source_ids"],
                    ["hced_dataset", *contract["evidence_refs"]],
                )
                self.assertEqual(
                    event["outcome_source_ids"],
                    contract["outcome_source_ids"],
                )
                self.assertEqual(
                    event["outcome_source_family_ids"],
                    contract["outcome_source_family_ids"],
                )
                self.assertNotIn("hced_dataset", event["outcome_source_ids"])
                self.assertIn(contract["audit_note"], event["summary"])

    def test_geometry_decisions_withhold_two_points_and_retain_stralsund(self):
        self.assertEqual(
            lane.WAVE8_GREAT_NORTHERN_EXACT_POINT_QUARANTINE_ADDITIONS,
            {"hced-Gadebusch1712-1", "hced-Tonning1713-1"},
        )
        self.assertFalse(
            lane.WAVE8_GREAT_NORTHERN_EXACT_COUNTRY_QUARANTINE_ADDITIONS
        )
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        for candidate_id in (
            "hced-Gadebusch1712-1",
            "hced-Tonning1713-1",
        ):
            with self.subTest(candidate_id=candidate_id):
                self.assertNotIn("geometry", events[candidate_id])
                self.assertEqual(
                    events[candidate_id]["modern_location_country"],
                    "Germany",
                )
                self.assertIn("location_provenance", events[candidate_id])

        stralsund = events["hced-Stralsund1714-1715-1"]
        self.assertEqual(stralsund["modern_location_country"], "Germany")
        self.assertEqual(
            stralsund["geometry"],
            {"type": "Point", "coordinates": [13.0770347, 54.3090654]},
        )
        self.assertIn("location_provenance", stralsund)

    def test_duplicate_audit_is_zero_and_future_twins_fail_closed(self):
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_great_northern_exact_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )
        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-gadebusch-twin",
                "batname": "Battle of Wakenstadt",
                "batyear": 1712,
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed twin"):
            lane.validate_wave8_great_northern_exact_integration_dispositions(
                self.hced_rows,
                future_iwbd,
                existing,
            )

    def test_row_actor_window_and_duplicate_drift_fail_closed(self):
        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Tonning1713-1"
        )
        row["participants_raw"].append("invented participant")
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_great_northern_exact_queue_contracts(tampered)

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Gadebusch1712-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected one locked row"):
            lane.validate_wave8_great_northern_exact_queue_contracts(missing)

        entities, _, existing = self._installed()
        promoted = lane.promote_wave8_great_northern_exact_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "already promoted"):
            lane.promote_wave8_great_northern_exact_contracts(
                self.hced_rows,
                entities,
                [*existing, *promoted],
            )

        broken_entities = copy.deepcopy(entities)
        broken_entities[RUSSIA]["end_year"] = 1712
        with self.assertRaisesRegex(ValueError, "existing identity drift"):
            lane.promote_wave8_great_northern_exact_contracts(
                self.hced_rows,
                broken_entities,
                existing,
            )

    def test_unreviewed_discovery_row_never_rates_automatically(self):
        speculative = {
            "candidate_id": "hced-future-great-northern-discovery",
            "name": "Unreviewed Baltic action",
            "year_low": 1714,
            "year_high": 1714,
            "year_best": 1714,
            "side_1_raw": "Sweden",
            "side_2_raw": "Denmark, Saxony",
            "winner_raw": "Sweden",
            "loser_raw": "Denmark, Saxony",
        }
        entities, _, existing = self._installed()
        events = lane.promote_wave8_great_northern_exact_contracts(
            [*self.hced_rows, speculative],
            entities,
            existing,
        )
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            set(EXPECTED_HASHES),
        )

    def test_counts_signature_and_source_install_are_pinned(self):
        self.assertEqual(
            lane.wave8_great_northern_exact_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 0,
                "new_entities": 0,
                "new_sources": 7,
                "newly_rated_events": 3,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_great_northern_exact_cohort_counts(),
            {"great_northern_war_1712_1715": 3},
        )
        self.assertEqual(
            lane.wave8_great_northern_exact_audit_signature(),
            "fe532d1e548f2f52605070ef457ed05475241f274383ab0cd9064146b7fa484f",
        )
        self.assertEqual(
            lane.wave8_great_northern_exact_audit_signature(),
            lane.WAVE8_GREAT_NORTHERN_EXACT_FINAL_AUDIT_SIGNATURE,
        )
        source_ids = {
            str(source["id"])
            for source in lane.WAVE8_GREAT_NORTHERN_EXACT_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in source_ids
        }
        lane.install_wave8_great_northern_exact_sources(sources)
        once = copy.deepcopy(sources)
        lane.install_wave8_great_northern_exact_sources(sources)
        self.assertEqual(sources, once)
        self.assertLessEqual(source_ids, set(sources))


if __name__ == "__main__":
    unittest.main()
