import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_dacia import (
    WAVE8_DACIA_CONTRACT_IDS,
    WAVE8_DACIA_CONTRACTS,
    WAVE8_DACIA_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_DACIA_CROSS_LANE_DISPOSITIONS,
    WAVE8_DACIA_ENTITIES,
    WAVE8_DACIA_EXCLUSION_IDS,
    WAVE8_DACIA_EXCLUSIONS,
    WAVE8_DACIA_EXPECTED_CANDIDATE_IDS,
    WAVE8_DACIA_FINAL_AUDIT_SIGNATURE,
    WAVE8_DACIA_HOLD_IDS,
    WAVE8_DACIA_HOLDS,
    WAVE8_DACIA_INTEGRATION_DISPOSITIONS,
    WAVE8_DACIA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_DACIA_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_DACIA_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_DACIA_LOCATION_QUARANTINE_REASONS,
    WAVE8_DACIA_OUTCOME_OVERRIDES,
    WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS,
    WAVE8_DACIA_RESERVED_IDS,
    WAVE8_DACIA_SOURCES,
    WAVE8_DACIA_TERMINAL_EXCLUSION_IDS,
    WAVE8_DACIA_TERMINAL_EXCLUSIONS,
    install_wave8_dacia_entities,
    install_wave8_dacia_sources,
    promote_wave8_dacia_contracts,
    validate_wave8_dacia_integration_dispositions,
    validate_wave8_dacia_queue_contracts,
    wave8_dacia_audit_signature,
    wave8_dacia_cohort_counts,
    wave8_dacia_counts,
    wave8_dacia_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_dacia_"
ROMAN_ID = "roman_empire"
DACIA_ID = "decebalus_dacian_kingdom_87_106"


EXPECTED_RAW_LABELS = {
    "hced-Sarmizegethusa102-1": ("Rome", "Dacia", "Rome", "Dacia", 102),
    "hced-Sarmizegethusa105-1": ("Rome", "Dacia", "Rome", "Dacia", 105),
    "hced-Tapae101-1": ("Rome", "Dacia", "Draw", None, 101),
    "hced-Tapae86-1": ("Dacia", "Rome", "Dacia", "Rome", 86),
    "hced-Tapae88-1": ("Rome", "Dacia", "Rome", "Dacia", 88),
}

EXPECTED_PROMOTIONS = {
    "hced-Tapae88-1": {
        "name": "Battle of Tapae (Domitianic War)",
        "year": 88,
        "winner": {ROMAN_ID},
        "loser": {DACIA_ID},
        "override": False,
    },
    "hced-Tapae101-1": {
        "name": "Battle of Tapae (Trajan's First Dacian War)",
        "year": 101,
        "winner": {ROMAN_ID},
        "loser": {DACIA_ID},
        "override": True,
    },
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue is unavailable: {path.name}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Wave8DaciaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.lane_rows = [
            row
            for row in cls.hced_rows
            if row.get("candidate_id") in WAVE8_DACIA_RESERVED_IDS
        ]

    def _installed(self):
        new_entity_ids = {str(entity["id"]) for entity in WAVE8_DACIA_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        install_wave8_dacia_entities(entities)

        new_source_ids = {str(source["id"]) for source in WAVE8_DACIA_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        install_wave8_dacia_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_DACIA_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return promote_wave8_dacia_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_signature_inventory_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_DACIA_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_DACIA_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_DACIA_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_DACIA_ENTITIES,
            "expected_candidate_ids": sorted(WAVE8_DACIA_EXPECTED_CANDIDATE_IDS),
            "holds": WAVE8_DACIA_HOLDS,
            "integration_dispositions": WAVE8_DACIA_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": WAVE8_DACIA_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_zero_overlap_audit": WAVE8_DACIA_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": WAVE8_DACIA_LOCATION_QUARANTINE_REASONS,
            "outcome_overrides": WAVE8_DACIA_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_DACIA_SOURCES,
            "terminal_exclusions": WAVE8_DACIA_TERMINAL_EXCLUSIONS,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent, WAVE8_DACIA_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_dacia_audit_signature(), independent)
        self.assertEqual(WAVE8_DACIA_CONTRACT_IDS, set(EXPECTED_PROMOTIONS))
        self.assertEqual(
            WAVE8_DACIA_HOLD_IDS,
            {
                "hced-Sarmizegethusa102-1",
                "hced-Sarmizegethusa105-1",
                "hced-Tapae86-1",
            },
        )
        self.assertEqual(WAVE8_DACIA_TERMINAL_EXCLUSIONS, {})
        self.assertEqual(WAVE8_DACIA_EXCLUSIONS, {})
        self.assertEqual(WAVE8_DACIA_TERMINAL_EXCLUSION_IDS, frozenset())
        self.assertEqual(WAVE8_DACIA_EXCLUSION_IDS, frozenset())
        self.assertEqual(
            WAVE8_DACIA_RESERVED_IDS,
            WAVE8_DACIA_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            wave8_dacia_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "holds": 3,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 1,
                "new_sources": 7,
                "newly_rated_events": 2,
                "outcome_overrides": 1,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            wave8_dacia_cohort_counts(),
            {
                "domitianic_dacian_war_86_89": 2,
                "trajans_first_dacian_war_101_102": 2,
                "trajans_second_dacian_war_105_106": 1,
            },
        )

    def test_all_and_only_five_exact_dacia_rows_are_owned_and_hash_pinned(self) -> None:
        exact_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Dacia" or row.get("side_2_raw") == "Dacia"
        }
        self.assertEqual(set(exact_rows), set(EXPECTED_RAW_LABELS))
        self.assertEqual(
            validate_wave8_dacia_queue_contracts(self.hced_rows),
            {
                "promotion_contracts": 2,
                "holds": 3,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 0,
            },
        )
        for candidate_id, expected in EXPECTED_RAW_LABELS.items():
            row = exact_rows[candidate_id]
            self.assertEqual(
                (
                    row["side_1_raw"],
                    row["side_2_raw"],
                    row["winner_raw"],
                    row["loser_raw"],
                    row["year_best"],
                ),
                expected,
            )
            disposition = (
                WAVE8_DACIA_CONTRACTS.get(candidate_id)
                or WAVE8_DACIA_HOLDS[candidate_id]
            )
            self.assertEqual(
                canonical_hced_row_sha256(row),
                disposition["raw_row_sha256"],
            )

        future = copy.deepcopy(self.hced_rows)
        future.append(
            {
                "candidate_id": "hced-FutureDacia107-1",
                "side_1_raw": "Rome",
                "side_2_raw": "Dacia",
                "year_best": 107,
            }
        )
        future_exact_ids = {
            str(row["candidate_id"])
            for row in future
            if row.get("side_1_raw") == "Dacia" or row.get("side_2_raw") == "Dacia"
        }
        self.assertNotEqual(future_exact_ids, WAVE8_DACIA_RESERVED_IDS)

    def test_every_row_tamper_fails_closed(self) -> None:
        for candidate_id in sorted(WAVE8_DACIA_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                tampered = copy.deepcopy(self.hced_rows)
                row = next(
                    row for row in tampered if row.get("candidate_id") == candidate_id
                )
                row["name"] = str(row["name"]) + " changed"
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_dacia_queue_contracts(tampered)

    def test_sources_and_single_bounded_polity_parse_and_do_not_bridge(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_DACIA_SOURCES}
        self.assertEqual(len(source_by_id), 7)
        for source in WAVE8_DACIA_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )

        self.assertEqual(len(WAVE8_DACIA_ENTITIES), 1)
        entity = WAVE8_DACIA_ENTITIES[0]
        Entity.from_dict(entity)
        self.assertEqual(entity["id"], DACIA_ID)
        self.assertEqual((entity["start_year"], entity["end_year"]), (87, 106))
        self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
        self.assertNotEqual(entity["id"], "dacia")
        self.assertNotEqual(entity["name"].casefold(), "dacia")
        self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
        self.assertIn("modern romania", entity["continuity_note"].casefold())
        self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        entities, sources, _ = self._installed()
        self.assertIn(DACIA_ID, entities)
        self.assertIn(ROMAN_ID, entities)
        self.assertTrue(set(source_by_id) <= set(sources))

    def test_two_tapae_engagements_are_distinct_parseable_roman_wins(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 2)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_PROMOTIONS))
        self.assertTrue(WAVE8_DACIA_HOLD_IDS.isdisjoint(by_candidate))

        canonical_keys = set()
        canonical_names = set()
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["name"], expected["name"])
            self.assertEqual((event["year"], event["end_year"]), (expected["year"], expected["year"]))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            winners = {
                item["entity_id"]
                for item in event["participants"]
                if item["termination"] == "engagement_victory"
            }
            losers = {
                item["entity_id"]
                for item in event["participants"]
                if item["termination"] == "engagement_defeat"
            }
            self.assertEqual(winners, expected["winner"])
            self.assertEqual(losers, expected["loser"])
            self.assertEqual(
                {item["termination"] for item in event["participants"]},
                {"engagement_victory", "engagement_defeat"},
            )
            canonical_keys.add(event["canonical_event_key"])
            canonical_names.add(event["name"])
        self.assertEqual(len(canonical_keys), 2)
        self.assertEqual(len(canonical_names), 2)

    def test_tapae_101_draw_placeholder_is_explicitly_corrected_not_invented(self) -> None:
        raw = next(
            row for row in self.lane_rows if row["candidate_id"] == "hced-Tapae101-1"
        )
        self.assertEqual(raw["winner_raw"], "Draw")
        self.assertIsNone(raw["loser_raw"])
        self.assertFalse(raw["winner_loser_complete"])

        contract = WAVE8_DACIA_CONTRACTS["hced-Tapae101-1"]
        self.assertTrue(contract["source_outcome_override"])
        self.assertFalse(contract["outcome_reversal"])
        self.assertEqual(contract["result_type"], "win")
        self.assertEqual(contract["winner_side"], 1)
        self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
        self.assertEqual(
            set(WAVE8_DACIA_OUTCOME_OVERRIDES),
            {"hced-Tapae101-1"},
        )
        override = WAVE8_DACIA_OUTCOME_OVERRIDES["hced-Tapae101-1"]
        self.assertEqual(override["raw_winner_raw"], "Draw")
        self.assertIsNone(override["raw_loser_raw"])
        self.assertEqual(override["corrected_winner_entity_ids"], [ROMAN_ID])
        self.assertEqual(override["corrected_loser_entity_ids"], [DACIA_ID])
        self.assertEqual(override["outcome_source_ids"], contract["outcome_source_ids"])

        event = next(
            event
            for event in self._events()
            if event["hced_candidate_id"] == "hced-Tapae101-1"
        )
        self.assertNotIn(
            "inconclusive_engagement",
            {item["termination"] for item in event["participants"]},
        )

    def test_three_uncertain_rows_remain_unknown_never_draws_or_shifted_events(self) -> None:
        expected_categories = {
            "hced-Tapae86-1": "event_year_and_battle_site_not_uniquely_defensible",
            "hced-Sarmizegethusa102-1": "named_tactical_engagement_not_uniquely_attested",
            "hced-Sarmizegethusa105-1": "siege_year_and_event_boundary_not_uniquely_defensible",
        }
        emitted_ids = {event["hced_candidate_id"] for event in self._events()}
        for candidate_id, category in expected_categories.items():
            hold = WAVE8_DACIA_HOLDS[candidate_id]
            self.assertEqual(hold["hold_category"], category)
            self.assertEqual(hold["disposition"], "hold")
            self.assertEqual(hold["result_type"], "unknown")
            self.assertEqual(hold["reviewed_outcome"], "unknown")
            self.assertTrue(hold["unknown_is_never_draw"])
            self.assertNotIn("winner_side", hold)
            self.assertIn("draw", hold["hold_reason"].casefold())
            self.assertNotIn(candidate_id, emitted_ids)

        tapae = WAVE8_DACIA_HOLDS["hced-Tapae86-1"]
        self.assertEqual(tapae["historical_review"]["competing_year"], 87)
        self.assertIn("silently moved to 87", tapae["hold_reason"])
        first = WAVE8_DACIA_HOLDS["hced-Sarmizegethusa102-1"]
        self.assertIn("campaign occupation", first["hold_reason"].casefold())
        second = WAVE8_DACIA_HOLDS["hced-Sarmizegethusa105-1"]
        self.assertEqual(second["historical_review"]["capture_year"], 106)
        self.assertIn("single-year 105", second["hold_reason"])

    def test_promoted_only_location_quarantine_withholds_points_not_country(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)

        self.assertEqual(WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS, WAVE8_DACIA_CONTRACT_IDS)
        self.assertEqual(WAVE8_DACIA_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertTrue(WAVE8_DACIA_HOLD_IDS.isdisjoint(WAVE8_DACIA_POINT_QUARANTINE_ADDITIONS))
        self.assertEqual(set(WAVE8_DACIA_LOCATION_QUARANTINE_REASONS), WAVE8_DACIA_CONTRACT_IDS)
        self.assertEqual(
            WAVE8_DACIA_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_DACIA_CONTRACT_IDS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            wave8_dacia_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": WAVE8_DACIA_CONTRACT_IDS,
            },
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Romania")
            self.assertIn("location_provenance", event)

        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_zero_duplicate_audit_and_future_twins_fail_closed(self) -> None:
        self.assertEqual(WAVE8_DACIA_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_DACIA_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_DACIA_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(set(WAVE8_DACIA_IWBD_ZERO_OVERLAP_AUDIT), WAVE8_DACIA_RESERVED_IDS)
        self.assertEqual(
            validate_wave8_dacia_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
            },
        )

        hced_twin = copy.deepcopy(self.hced_rows)
        hced_twin.append(
            {
                "candidate_id": "hced-future-tapae-101",
                "name": "Battle of Tapae",
                "year_best": 101,
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_dacia_integration_dispositions(hced_twin, self.iwbd_rows)

        iwbd_twin = copy.deepcopy(self.iwbd_rows)
        iwbd_twin.append(
            {
                "candidate_id": "iwbd-future-sarmizegetusa",
                "name": "Siege of Sarmizegetusa",
                "start_date": "0106-01-01",
                "end_date": "0106-12-31",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            validate_wave8_dacia_integration_dispositions(self.hced_rows, iwbd_twin)

        release_twin = [
            *self.release_events,
            {"id": "future-tapae-twin", "name": "Battle of Tapae", "year": 88},
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_dacia_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release_twin,
            )

    def test_entity_window_and_duplicate_event_collisions_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        short = copy.deepcopy(entities)
        short[DACIA_ID]["start_year"] = 89
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_dacia_contracts(self.hced_rows, short, existing)

        events = promote_wave8_dacia_contracts(self.hced_rows, entities, existing)
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_dacia_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

        collision = [
            *existing,
            {"name": "Battle of Tapae (Domitianic War)", "year": 88},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_dacia_contracts(self.hced_rows, entities, collision)

    def test_installers_copy_and_reject_collisions(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        install_wave8_dacia_entities(entities)
        install_wave8_dacia_sources(sources)
        entities[DACIA_ID]["name"] = "tampered"
        sources["wave8_dacia_oxford_decebalus"]["title"] = "tampered"
        self.assertNotEqual(entities[DACIA_ID]["name"], WAVE8_DACIA_ENTITIES[0]["name"])
        self.assertNotEqual(
            sources["wave8_dacia_oxford_decebalus"]["title"],
            next(
                source["title"]
                for source in WAVE8_DACIA_SOURCES
                if source["id"] == "wave8_dacia_oxford_decebalus"
            ),
        )
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_dacia_entities(entities)
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_dacia_sources(sources)


if __name__ == "__main__":
    unittest.main()
