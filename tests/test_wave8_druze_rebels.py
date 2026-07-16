import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_druze_rebels import (
    WAVE8_DRUZE_REBELS_CONTRACT_IDS,
    WAVE8_DRUZE_REBELS_CONTRACTS,
    WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS,
    WAVE8_DRUZE_REBELS_ENTITIES,
    WAVE8_DRUZE_REBELS_EXPECTED_CANDIDATE_IDS,
    WAVE8_DRUZE_REBELS_FINAL_AUDIT_SIGNATURE,
    WAVE8_DRUZE_REBELS_HOLD_IDS,
    WAVE8_DRUZE_REBELS_HOLDS,
    WAVE8_DRUZE_REBELS_INTEGRATION_DISPOSITIONS,
    WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_DRUZE_REBELS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_DRUZE_REBELS_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_DRUZE_REBELS_LOCATION_REVIEW,
    WAVE8_DRUZE_REBELS_OUTCOME_OVERRIDES,
    WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_DRUZE_REBELS_RESERVED_IDS,
    WAVE8_DRUZE_REBELS_SOURCES,
    install_wave8_druze_rebels_entities,
    install_wave8_druze_rebels_sources,
    promote_wave8_druze_rebels_contracts,
    validate_wave8_druze_rebels_integration_dispositions,
    validate_wave8_druze_rebels_queue_contracts,
    wave8_druze_rebels_audit_signature,
    wave8_druze_rebels_cohort_counts,
    wave8_druze_rebels_counts,
    wave8_druze_rebels_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_druze_rebels_"


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
    "hced-Damascus1925-1": {
        "canonical": (
            "Battle and bombardment of Damascus",
            1925,
            "18-20 October 1925",
            "day_range",
        ),
        "sides": (
            ("french_damascus_suppression_force_october_1925",),
            ("damascus_october_insurgent_force_1925",),
        ),
    },
    "hced-Kafr1925-1": {
        "canonical": ("Battle of al-Kafr", 1925, "22 July 1925", "day"),
        "sides": (
            ("sultan_al_atrash_jabal_hawran_field_force_1925",),
            ("normand_levant_column_al_kafr_1925",),
        ),
    },
    "hced-Mazraa1925-1": {
        "canonical": (
            "Battle of al-Mazraa",
            1925,
            "2-3 August 1925",
            "day_range",
        ),
        "sides": (
            ("sultan_al_atrash_jabal_hawran_field_force_1925",),
            ("michaud_levant_column_al_mazraa_1925",),
        ),
    },
    "hced-Rashaya1925-1": {
        "canonical": (
            "Siege of Rashaya Citadel",
            1925,
            "21-24 November 1925",
            "day_range",
        ),
        "sides": (
            ("rashaya_citadel_garrison_1925",),
            ("zayd_al_atrash_rashaya_besiegers_1925",),
        ),
    },
}


class Wave8DruzeRebelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _installed(self):
        fixture_entity_ids = {
            str(entity["id"]) for entity in WAVE8_DRUZE_REBELS_ENTITIES
        }
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in fixture_entity_ids
        }
        install_wave8_druze_rebels_entities(entities)

        fixture_source_ids = {
            str(source["id"]) for source in WAVE8_DRUZE_REBELS_SOURCES
        }
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in fixture_source_ids
        }
        install_wave8_druze_rebels_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_DRUZE_REBELS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_druze_rebels_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_signature_inventory_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_DRUZE_REBELS_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_duplicate_dispositions": (
                WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS
            ),
            "entities": WAVE8_DRUZE_REBELS_ENTITIES,
            "holds": WAVE8_DRUZE_REBELS_HOLDS,
            "iwbd_duplicate_dispositions": (
                WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": WAVE8_DRUZE_REBELS_IWBD_ZERO_OVERLAP_AUDIT,
            "location_review": WAVE8_DRUZE_REBELS_LOCATION_REVIEW,
            "outcome_overrides": WAVE8_DRUZE_REBELS_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_DRUZE_REBELS_SOURCES,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent, WAVE8_DRUZE_REBELS_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_druze_rebels_audit_signature(), independent)

        expected_all = frozenset({*EXPECTED, "hced-Damascus1926-1"})
        self.assertEqual(WAVE8_DRUZE_REBELS_CONTRACT_IDS, frozenset(EXPECTED))
        self.assertEqual(WAVE8_DRUZE_REBELS_HOLD_IDS, {"hced-Damascus1926-1"})
        self.assertEqual(WAVE8_DRUZE_REBELS_RESERVED_IDS, expected_all)
        self.assertEqual(WAVE8_DRUZE_REBELS_EXPECTED_CANDIDATE_IDS, expected_all)
        self.assertEqual(
            wave8_druze_rebels_counts(),
            {
                "country_quarantine_additions": 1,
                "cross_lane_duplicate_dispositions": 0,
                "holds": 1,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 5,
                "new_entities": 7,
                "new_sources": 16,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 5,
            },
        )
        self.assertEqual(
            wave8_druze_rebels_cohort_counts(),
            {
                "damascus_october_offensive_1925": 1,
                "jabal_hawran_opening_1925": 2,
                "rashaya_anti_lebanon_campaign_1925": 1,
            },
        )

    def test_all_five_queue_rows_are_hash_pinned_and_drift_fails_closed(self) -> None:
        rows_by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        self.assertEqual(
            validate_wave8_druze_rebels_queue_contracts(self.hced_rows),
            {"promotion_contracts": 4, "holds": 1, "reviewed_hced_rows": 5},
        )
        inventories = {
            **WAVE8_DRUZE_REBELS_CONTRACTS,
            **WAVE8_DRUZE_REBELS_HOLDS,
        }
        for candidate_id, disposition in inventories.items():
            self.assertEqual(
                canonical_hced_row_sha256(rows_by_id[candidate_id]),
                disposition["raw_row_sha256"],
            )

        changed = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Damascus1926-1"
        )["theatre_raw"] = "Land and Air"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_druze_rebels_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row["candidate_id"] != "hced-Rashaya1925-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_druze_rebels_queue_contracts(missing)

    def test_sources_are_direct_canonical_and_fully_consumed(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_DRUZE_REBELS_SOURCES
        }
        self.assertEqual(len(source_by_id), 16)
        used = set()
        for source in WAVE8_DRUZE_REBELS_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
            self.assertTrue(source["source_family_id"])

        for contract in WAVE8_DRUZE_REBELS_CONTRACTS.values():
            outcomes = contract["outcome_source_ids"]
            expected_families = sorted(
                {source_by_id[source_id]["source_family_id"] for source_id in outcomes}
            )
            self.assertEqual(contract["outcome_source_family_ids"], expected_families)
            self.assertTrue(outcomes)
            self.assertLessEqual(set(outcomes), set(contract["evidence_refs"]))
            self.assertTrue(
                all(
                    "outcome" in source_by_id[source_id]["evidence_roles"]
                    for source_id in outcomes
                )
            )
            used.update(contract["evidence_refs"])

        hold = WAVE8_DRUZE_REBELS_HOLDS["hced-Damascus1926-1"]
        used.update(hold["evidence_refs"])
        self.assertTrue(
            all(
                "curated_reference_pending_claim_level_outcome_locator"
                in source_by_id[source_id]["evidence_roles"]
                for source_id in hold["evidence_refs"]
            )
        )
        for entity in WAVE8_DRUZE_REBELS_ENTITIES:
            used.update(entity["source_ids"])
        for review in WAVE8_DRUZE_REBELS_LOCATION_REVIEW.values():
            used.update(review["evidence_refs"])
        self.assertEqual(used, set(source_by_id))

        _, installed_sources, _ = self._installed()
        for source_id in source_by_id:
            Source.from_dict(installed_sources[source_id])

    def test_entities_are_bounded_formations_without_an_ethnic_or_state_bridge(self) -> None:
        source_ids = {str(source["id"]) for source in WAVE8_DRUZE_REBELS_SOURCES}
        entity_by_id = {
            str(entity["id"]): entity for entity in WAVE8_DRUZE_REBELS_ENTITIES
        }
        self.assertEqual(len(entity_by_id), 7)
        for entity in WAVE8_DRUZE_REBELS_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["start_year"], entity["end_year"]), (1925, 1925))
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertIn("modern", entity["continuity_note"].casefold())
            self.assertLessEqual(set(entity["source_ids"]), source_ids)
            self.assertNotIn(
                entity["name"].casefold().strip(),
                {"druze", "druze rebels", "druze people", "syrian rebels"},
            )

        used = set()
        for contract in WAVE8_DRUZE_REBELS_CONTRACTS.values():
            used.update(contract["side_1_entity_ids"])
            used.update(contract["side_2_entity_ids"])
        self.assertEqual(used, set(entity_by_id))
        self.assertFalse(
            any(entity_id in {"druze", "druze_rebels", "syria", "france"} for entity_id in used)
        )

    def test_exact_dates_actors_and_outcomes_match_the_four_adjudications(self) -> None:
        for candidate_id, expected in EXPECTED.items():
            contract = WAVE8_DRUZE_REBELS_CONTRACTS[candidate_id]
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
            self.assertEqual(canonical["granularity"], "engagement")
            self.assertEqual(
                (
                    tuple(contract["side_1_entity_ids"]),
                    tuple(contract["side_2_entity_ids"]),
                ),
                expected["sides"],
            )
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["war_type"], "colonial_anti_colonial")
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertEqual(
                contract["actor_override"],
                "bounded_exact_opposing_forces",
            )
        self.assertEqual(WAVE8_DRUZE_REBELS_OUTCOME_OVERRIDES, {})

    def test_damascus_1926_is_an_ambiguous_multi_event_hold_not_a_draw(self) -> None:
        hold = WAVE8_DRUZE_REBELS_HOLDS["hced-Damascus1926-1"]
        self.assertEqual(
            hold["hold_category"],
            "multiple_distinct_same_city_operations_in_source_year",
        )
        self.assertEqual(
            hold["canonical_event"]["granularity"],
            "ambiguous_multi_event_aggregate",
        )
        self.assertIn("17 February", hold["canonical_event"]["date_text"])
        self.assertIn("7 May", hold["canonical_event"]["date_text"])
        self.assertIn("cannot produce an Elo", hold["hold_reason"])
        self.assertIn("unknown is never converted into a draw", hold["hold_reason"])
        forbidden = {
            "result_type",
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "outcome_source_ids",
        }
        self.assertFalse(forbidden & set(hold))

        raw = next(
            row
            for row in self.hced_rows
            if row["candidate_id"] == "hced-Damascus1926-1"
        )
        self.assertIsNone(raw["consulted_source_raw"])
        self.assertEqual(raw["year_low"], raw["year_high"])
        self.assertEqual(raw["theatre_raw"], "Air")

        _, _, events = self._emit()
        self.assertNotIn(
            "hced-Damascus1926-1",
            {event["hced_candidate_id"] for event in events},
        )
        self.assertFalse(
            any(
                participant["side"] == "draw"
                for event in events
                for participant in event["participants"]
            )
        )

    def test_emitted_events_parse_and_never_rate_civilians_or_generic_druze(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 4)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_DRUZE_REBELS_CONTRACT_IDS,
        )
        for event in events:
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertTrue(event["outcome_source_ids"])
            self.assertTrue(event["outcome_source_family_ids"])
            self.assertNotIn("geometry", event)
            self.assertFalse(
                any(participant["side"] == "draw" for participant in event["participants"])
            )
            participant_ids = {
                participant["entity_id"] for participant in event["participants"]
            }
            self.assertFalse(
                participant_ids
                & {"druze", "druze_rebels", "druze_people", "civilians", "syria", "france"}
            )

    def test_location_review_quarantines_only_promoted_fields(self) -> None:
        self.assertEqual(set(WAVE8_DRUZE_REBELS_LOCATION_REVIEW), set(EXPECTED))
        self.assertEqual(
            WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS,
            frozenset(EXPECTED),
        )
        self.assertEqual(
            WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
            {"hced-Mazraa1925-1"},
        )
        self.assertNotIn(
            "hced-Damascus1926-1",
            WAVE8_DRUZE_REBELS_POINT_QUARANTINE_ADDITIONS
            | WAVE8_DRUZE_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
        )
        self.assertEqual(
            WAVE8_DRUZE_REBELS_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": frozenset(EXPECTED),
                "country": frozenset({"hced-Mazraa1925-1"}),
            },
        )
        self.assertEqual(
            wave8_druze_rebels_location_quarantine_additions(),
            {
                "point": frozenset(EXPECTED),
                "country": frozenset({"hced-Mazraa1925-1"}),
            },
        )

        _, _, events = self._emit()
        by_id = {event["hced_candidate_id"]: event for event in events}
        self.assertEqual(by_id["hced-Damascus1925-1"]["modern_location_country"], "Syria")
        self.assertEqual(by_id["hced-Kafr1925-1"]["modern_location_country"], "Syria")
        self.assertEqual(by_id["hced-Rashaya1925-1"]["modern_location_country"], "Lebanon")
        self.assertNotIn("modern_location_country", by_id["hced-Mazraa1925-1"])
        self.assertNotIn("location_provenance", by_id["hced-Mazraa1925-1"])

    def test_iwbd_and_cross_lane_zero_overlap_audits_fail_on_new_twins(self) -> None:
        entities, _, existing = self._installed()
        self.assertTrue(entities)
        self.assertEqual(WAVE8_DRUZE_REBELS_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_DRUZE_REBELS_CROSS_LANE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_DRUZE_REBELS_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(set(WAVE8_DRUZE_REBELS_IWBD_ZERO_OVERLAP_AUDIT), WAVE8_DRUZE_REBELS_RESERVED_IDS)
        self.assertEqual(
            validate_wave8_druze_rebels_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_lane_duplicate_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 5,
            },
        )

        planted_iwbd = [
            *self.iwbd_rows,
            {
                "candidate_id": "iwbd-planted-kafr",
                "name": "Battle of al-Kafr",
                "start_date": "1925-07-22",
                "end_date": "1925-07-22",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unadjudicated IWBD duplicate"):
            validate_wave8_druze_rebels_integration_dispositions(
                self.hced_rows,
                planted_iwbd,
                existing,
            )

        planted_release = [
            *existing,
            {"id": "planted_mazraa", "name": "Battle of al-Mazraa", "year": 1925},
        ]
        with self.assertRaisesRegex(ValueError, "unadjudicated release duplicates"):
            validate_wave8_druze_rebels_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                planted_release,
            )

    def test_fail_closed_entity_window_duplicate_and_fixture_collisions(self) -> None:
        entities, sources, existing = self._installed()

        bad_window = copy.deepcopy(entities)
        bad_window["normand_levant_column_al_kafr_1925"]["start_year"] = 1926
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_druze_rebels_contracts(
                self.hced_rows,
                bad_window,
                existing,
            )

        duplicate = [
            *existing,
            {
                "id": "planted_candidate_duplicate",
                "name": "planted",
                "year": 1925,
                "hced_candidate_id": "hced-Kafr1925-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_druze_rebels_contracts(
                self.hced_rows,
                entities,
                duplicate,
            )

        bad_entity_store = copy.deepcopy(entities)
        entity_id = WAVE8_DRUZE_REBELS_ENTITIES[0]["id"]
        bad_entity_store[entity_id]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_druze_rebels_entities(bad_entity_store)

        bad_source_store = copy.deepcopy(sources)
        source_id = WAVE8_DRUZE_REBELS_SOURCES[0]["id"]
        bad_source_store[source_id]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_druze_rebels_sources(bad_source_store)

    def test_promoter_is_deterministic_and_provenance_is_complete(self) -> None:
        entities, sources, existing = self._installed()
        first = promote_wave8_druze_rebels_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        second = promote_wave8_druze_rebels_contracts(
            copy.deepcopy(self.hced_rows),
            copy.deepcopy(entities),
            copy.deepcopy(existing),
        )
        self.assertEqual(first, second)
        source_ids = set(sources)
        for event in first:
            contract = WAVE8_DRUZE_REBELS_CONTRACTS[event["hced_candidate_id"]]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertLessEqual(set(event["source_ids"]), source_ids)
            self.assertIn("hced_dataset", event["source_ids"])


if __name__ == "__main__":
    unittest.main()
