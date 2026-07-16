import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_moros import (
    WAVE8_MOROS_CONTRACT_IDS,
    WAVE8_MOROS_CONTRACTS,
    WAVE8_MOROS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_MOROS_CROSS_LANE_DUPLICATE_DISPOSITIONS,
    WAVE8_MOROS_ENTITIES,
    WAVE8_MOROS_EXPECTED_CANDIDATE_IDS,
    WAVE8_MOROS_FINAL_AUDIT_SIGNATURE,
    WAVE8_MOROS_HOLD_IDS,
    WAVE8_MOROS_HOLDS,
    WAVE8_MOROS_INTEGRATION_DISPOSITIONS,
    WAVE8_MOROS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_MOROS_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_MOROS_LOCATION_REVIEW,
    WAVE8_MOROS_OUTCOME_OVERRIDES,
    WAVE8_MOROS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_MOROS_RESERVED_IDS,
    WAVE8_MOROS_SOURCES,
    install_wave8_moros_entities,
    install_wave8_moros_sources,
    promote_wave8_moros_contracts,
    validate_wave8_moros_queue_contracts,
    wave8_moros_audit_signature,
    wave8_moros_cohort_counts,
    wave8_moros_counts,
    wave8_moros_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_moros_"


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


EXPECTED = {
    "hced-Bacolod1903-1": {
        "canonical": ("Battle of Bacolod Grande", 1903, "6-8 April 1903", "day"),
        "sides": (("united_states",), ("bacolod_grande_defenders_1903",)),
        "override": False,
    },
    "hced-Bayan1902-1": {
        "canonical": ("Battle of Bayang", 1902, "2 May 1902", "day"),
        "sides": (("united_states",), ("bayang_pandapatan_defenders_1902",)),
        "override": False,
    },
    "hced-Bud Bagsak1913-1": {
        "canonical": ("Battle of Bud Bagsak", 1913, "11-15 June 1913", "day"),
        "sides": (
            ("philippine_scouts_bud_bagsak_column_1913", "united_states"),
            ("datu_amil_lati_bud_bagsak_defenders_1913",),
        ),
        "override": False,
    },
    "hced-Kudarangan1904-1": {
        "canonical": ("Battle of Kudarangan", 1904, "10-11 March 1904", "day"),
        "sides": (("united_states",), ("datu_ali_buayan_resistance_1902_1905",)),
        "override": True,
    },
    "hced-Lake Seit1903-1": {
        "canonical": ("Battle of Lake Siit", 1903, "November 1903", "month"),
        "sides": (("united_states",), ("panglima_hassan_luuk_force_1903",)),
        "override": False,
    },
    "hced-Malala1905-1": {
        "canonical": ("Battle of the Malala River", 1905, "22 October 1905", "day"),
        "sides": (("united_states",), ("datu_ali_buayan_resistance_1902_1905",)),
        "override": False,
    },
}


class Wave8MorosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _installed(self):
        fixture_entity_ids = {str(entity["id"]) for entity in WAVE8_MOROS_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in fixture_entity_ids
        }
        install_wave8_moros_entities(entities)

        fixture_source_ids = {str(source["id"]) for source in WAVE8_MOROS_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in fixture_source_ids
        }
        install_wave8_moros_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_MOROS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_moros_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_signature_inventory_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_MOROS_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_MOROS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_duplicate_dispositions": (
                WAVE8_MOROS_CROSS_LANE_DUPLICATE_DISPOSITIONS
            ),
            "entities": WAVE8_MOROS_ENTITIES,
            "holds": WAVE8_MOROS_HOLDS,
            "iwbd_duplicate_dispositions": WAVE8_MOROS_IWBD_DUPLICATE_DISPOSITIONS,
            "location_review": WAVE8_MOROS_LOCATION_REVIEW,
            "outcome_overrides": WAVE8_MOROS_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_MOROS_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_MOROS_SOURCES,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent, WAVE8_MOROS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_moros_audit_signature(), independent)
        self.assertEqual(WAVE8_MOROS_CONTRACT_IDS, frozenset(EXPECTED))
        self.assertEqual(WAVE8_MOROS_EXPECTED_CANDIDATE_IDS, frozenset(EXPECTED))
        self.assertEqual(WAVE8_MOROS_RESERVED_IDS, frozenset(EXPECTED))
        self.assertEqual(WAVE8_MOROS_HOLD_IDS, frozenset())
        self.assertEqual(
            wave8_moros_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_duplicate_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 6,
                "new_sources": 10,
                "newly_rated_events": 6,
                "outcome_overrides": 1,
                "point_quarantine_additions": 6,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 6,
            },
        )
        self.assertEqual(
            wave8_moros_cohort_counts(),
            {
                "bud_bagsak_disarmament_resistance_1913": 1,
                "datu_ali_buayan_resistance_1904_1905": 2,
                "hassan_uprising_1903": 1,
                "lanao_resistance_1902_1903": 2,
            },
        )

    def test_all_six_queue_rows_are_hash_pinned_and_drift_fails_closed(self) -> None:
        rows_by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        self.assertEqual(
            validate_wave8_moros_queue_contracts(self.hced_rows),
            {"promotion_contracts": 6, "holds": 0, "reviewed_hced_rows": 6},
        )
        for candidate_id, contract in WAVE8_MOROS_CONTRACTS.items():
            self.assertEqual(
                canonical_hced_row_sha256(rows_by_id[candidate_id]),
                contract["raw_row_sha256"],
            )

        changed = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Kudarangan1904-1"
        )["winner_raw"] = "Unknown"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_moros_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row["candidate_id"] != "hced-Bayan1902-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_moros_queue_contracts(missing)

    def test_sources_have_direct_roles_and_independent_family_provenance(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_MOROS_SOURCES}
        self.assertEqual(len(source_by_id), 10)
        for source in WAVE8_MOROS_SOURCES:
            Source.from_dict(source)
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
            self.assertTrue(source["source_family_id"])

        for contract in WAVE8_MOROS_CONTRACTS.values():
            outcomes = contract["outcome_source_ids"]
            expected_families = sorted(
                {source_by_id[source_id]["source_family_id"] for source_id in outcomes}
            )
            self.assertEqual(contract["outcome_source_family_ids"], expected_families)
            self.assertTrue(
                all(
                    "outcome" in source_by_id[source_id]["evidence_roles"]
                    for source_id in outcomes
                )
            )
            self.assertLessEqual(set(outcomes), set(contract["evidence_refs"]))

        _, installed_sources, _ = self._installed()
        for source in WAVE8_MOROS_SOURCES:
            Source.from_dict(installed_sources[source["id"]])

    def test_entities_are_bounded_and_never_create_a_generic_moro_identity(self) -> None:
        source_ids = {str(source["id"]) for source in WAVE8_MOROS_SOURCES}
        entity_by_id = {str(entity["id"]): entity for entity in WAVE8_MOROS_ENTITIES}
        self.assertEqual(len(entity_by_id), 6)
        for entity in WAVE8_MOROS_ENTITIES:
            Entity.from_dict(entity)
            self.assertIsNotNone(entity["start_year"])
            self.assertIsNotNone(entity["end_year"])
            self.assertLessEqual(entity["start_year"], entity["end_year"])
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertIn("modern", entity["continuity_note"].casefold())
            self.assertNotIn(
                entity["name"].casefold().strip(),
                {"moro", "moros", "moro people"},
            )
            self.assertLessEqual(set(entity["source_ids"]), source_ids)

        used = set()
        for contract in WAVE8_MOROS_CONTRACTS.values():
            used.update(contract["side_1_entity_ids"])
            used.update(contract["side_2_entity_ids"])
        self.assertEqual(used - {"united_states"}, set(entity_by_id))

        datu_ali_id = "datu_ali_buayan_resistance_1902_1905"
        self.assertEqual(entity_by_id[datu_ali_id]["start_year"], 1902)
        self.assertEqual(entity_by_id[datu_ali_id]["end_year"], 1905)

    def test_exact_dates_sides_and_outcomes_match_the_six_adjudications(self) -> None:
        for candidate_id, expected in EXPECTED.items():
            contract = WAVE8_MOROS_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["year_low"],
                    canonical["date_text"],
                    canonical["date_precision"],
                ),
                expected["canonical"],
            )
            self.assertEqual(canonical["year_low"], canonical["year_high"])
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(
                (
                    tuple(contract["side_1_entity_ids"]),
                    tuple(contract["side_2_entity_ids"]),
                ),
                expected["sides"],
            )
            self.assertIs(contract["source_outcome_override"], expected["override"])
            self.assertIs(contract["outcome_reversal"], expected["override"])
            self.assertEqual(contract["actor_override"], "bounded_exact_opposing_forces")

        self.assertEqual(
            set(WAVE8_MOROS_OUTCOME_OVERRIDES),
            {"hced-Kudarangan1904-1"},
        )
        self.assertEqual(
            WAVE8_MOROS_CONTRACTS["hced-Lake Seit1903-1"]["canonical_event"][
                "date_precision"
            ],
            "month",
        )

    def test_kudarangan_raw_draw_is_explicitly_rejected_not_emitted(self) -> None:
        raw = next(
            row
            for row in self.hced_rows
            if row["candidate_id"] == "hced-Kudarangan1904-1"
        )
        self.assertEqual(raw["winner_raw"], "Draw")
        self.assertIsNone(raw["loser_raw"])
        self.assertFalse(raw["winner_loser_complete"])

        _, _, events = self._emit()
        event = next(
            item
            for item in events
            if item["hced_candidate_id"] == "hced-Kudarangan1904-1"
        )
        by_entity = {participant["entity_id"]: participant for participant in event["participants"]}
        self.assertEqual(by_entity["united_states"]["side"], "side_a")
        self.assertEqual(
            by_entity["datu_ali_buayan_resistance_1902_1905"]["side"],
            "side_b",
        )
        self.assertTrue(
            by_entity["united_states"]["result_class"].endswith("victory")
        )
        self.assertTrue(
            by_entity["datu_ali_buayan_resistance_1902_1905"][
                "result_class"
            ].endswith("defeat")
        )
        self.assertFalse(
            any(participant["side"] == "draw" for participant in event["participants"])
        )

    def test_emitted_events_parse_and_never_contain_a_generic_bridge(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 6)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_MOROS_CONTRACT_IDS,
        )
        forbidden = {
            "moros",
            "moro",
            "moro people",
            "bangsamoro",
            "sultanate of sulu",
            "sultanate of maguindanao",
        }
        for event in events:
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertEqual(event["modern_location_country"], "Philippines")
            self.assertNotIn("geometry", event)
            self.assertTrue(event["outcome_source_ids"])
            self.assertTrue(event["outcome_source_family_ids"])
            self.assertFalse(
                any(participant["side"] == "draw" for participant in event["participants"])
            )
            self.assertTrue(
                all(
                    participant["entity_id"].casefold() not in forbidden
                    for participant in event["participants"]
                )
            )

    def test_location_audit_withholds_all_points_but_retains_country(self) -> None:
        self.assertEqual(set(WAVE8_MOROS_LOCATION_REVIEW), set(EXPECTED))
        self.assertEqual(WAVE8_MOROS_POINT_QUARANTINE_ADDITIONS, frozenset(EXPECTED))
        self.assertEqual(WAVE8_MOROS_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            WAVE8_MOROS_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": frozenset(EXPECTED),
                "country": frozenset(),
            },
        )
        self.assertEqual(
            wave8_moros_location_quarantine_additions(),
            {
                "point": frozenset(EXPECTED),
                "country": frozenset(),
            },
        )
        for review in WAVE8_MOROS_LOCATION_REVIEW.values():
            self.assertEqual(review["point_disposition"], "quarantine")
            self.assertEqual(review["country_disposition"], "retain")
            self.assertTrue(review["reason"])
            self.assertTrue(review["evidence_refs"])

    def test_iwbd_and_cross_lane_duplicate_audits_are_explicitly_empty(self) -> None:
        self.assertEqual(WAVE8_MOROS_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_MOROS_CROSS_LANE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_MOROS_INTEGRATION_DISPOSITIONS, {})
        raw_names = {
            "bacolod",
            "bayan",
            "bud bagsak",
            "kudarangan",
            "lake seit",
            "malala",
        }
        iwbd_names = {
            str(row.get("name") or "").strip().casefold() for row in self.iwbd_rows
        }
        self.assertFalse(raw_names & iwbd_names)

    def test_fail_closed_entity_window_duplicate_and_fixture_collisions(self) -> None:
        entities, sources, existing = self._installed()

        missing_us = copy.deepcopy(entities)
        missing_us.pop("united_states")
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_moros_contracts(self.hced_rows, missing_us, existing)

        duplicate = [
            *existing,
            {
                "id": "planted_duplicate",
                "name": "planted",
                "year": 1902,
                "hced_candidate_id": "hced-Bayan1902-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_moros_contracts(self.hced_rows, entities, duplicate)

        bad_entity_store = copy.deepcopy(entities)
        entity_id = WAVE8_MOROS_ENTITIES[0]["id"]
        bad_entity_store[entity_id]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_moros_entities(bad_entity_store)

        bad_source_store = copy.deepcopy(sources)
        source_id = WAVE8_MOROS_SOURCES[0]["id"]
        bad_source_store[source_id]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_moros_sources(bad_source_store)


if __name__ == "__main__":
    unittest.main()
