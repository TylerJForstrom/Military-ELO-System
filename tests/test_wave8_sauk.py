import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_sauk as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_sauk_"
FINAL_AUDIT_SIGNATURE = (
    "ec90a3cb838235b310db77628cea405066d7e46e0b306ecef369b0c4b8178b93"
)
EXACT_CANDIDATE_ID_SHA256 = (
    "d309fd7b74d14a6eb9795fda0cfdb111d934cfcdf61edef0273b123ccc82942f"
)

STILLMAN_BAND_ID = "black_hawk_british_band_war_party_stillmans_run_1832"
STILLMAN_MILITIA_ID = "stillman_bailey_illinois_militia_detachment_1832"
WISCONSIN_BAND_ID = (
    "black_hawk_british_band_rearguard_wisconsin_heights_1832"
)
WISCONSIN_MILITIA_ID = (
    "henry_dodge_combined_militia_wisconsin_heights_1832"
)
BAD_AXE_BAND_ID = "black_hawk_british_band_fighting_remnant_bad_axe_1832"
BAD_AXE_US_FORCE_ID = "atkinson_combined_us_force_bad_axe_1832"

EXPECTED_RAW_ROWS = {
    "hced-Bad Axe1832-1": {
        "hash": "b3424ee2b465fb9f8de8fc90cccafc3b15265560d73362edce6b2325a4521f82",
        "name": "Bad Axe",
        "side_1_raw": "United States",
        "side_2_raw": "Sauk Indians",
        "winner_raw": "United States",
        "loser_raw": "Sauk Indians",
        "massacre_raw": "Battle followed by massacre",
        "source_row": 1451,
    },
    "hced-Kelloggs Grove1832-1": {
        "hash": "b0bb092a16351619c4c692cb803540cb81fffa40ac486d9e3b9b4d505fe3487c",
        "name": "Kelloggs Grove",
        "side_1_raw": "United States",
        "side_2_raw": "Sauk Indians",
        "winner_raw": "United States",
        "loser_raw": "Sauk Indians",
        "massacre_raw": "No",
        "source_row": 8161,
    },
    "hced-Rock River1832-1": {
        "hash": "e50eda3594bbec024d32fcff66b4c1589d71efc709eee582cf2b404c9431ab77",
        "name": "Rock River",
        "side_1_raw": "Sauk Indians",
        "side_2_raw": "United States",
        "winner_raw": "Sauk Indians",
        "loser_raw": "United States",
        "massacre_raw": "No",
        "source_row": 13487,
    },
    "hced-Wisconsin Heights1832-1": {
        "hash": "c496f0b04d8e4e0787443680ab74f11a0276ab142d3170e9d37bea053d4e80e7",
        "name": "Wisconsin Heights",
        "side_1_raw": "United States",
        "side_2_raw": "Sauk Indians",
        "winner_raw": "United States",
        "loser_raw": "Sauk Indians",
        "massacre_raw": "No",
        "source_row": 17337,
    },
}

EXPECTED_PROMOTIONS = {
    "hced-Rock River1832-1": {
        "name": "Battle of Stillman's Run",
        "date_precision": "day",
        "granularity": "engagement",
        "confidence": 0.96,
        "winner": STILLMAN_BAND_ID,
        "loser": STILLMAN_MILITIA_ID,
    },
    "hced-Wisconsin Heights1832-1": {
        "name": "Battle of Wisconsin Heights",
        "date_precision": "day",
        "granularity": "engagement",
        "confidence": 0.82,
        "winner": WISCONSIN_MILITIA_ID,
        "loser": WISCONSIN_BAND_ID,
    },
    "hced-Bad Axe1832-1": {
        "name": "Battle and massacre at Bad Axe",
        "date_precision": "day_range",
        "granularity": "engagement_followed_by_massacre",
        "confidence": 0.94,
        "winner": BAD_AXE_US_FORCE_ID,
        "loser": BAD_AXE_BAND_ID,
    },
}

EXPECTED_ADJACENT_HASHES = {
    "hced-Pecatonica1832-1": (
        "d721827b8f598cd586833273241de24a88e1c9dc6af3dfda65e22e4cf69936f6"
    ),
    "hced-Rock Island Rapids1814-1": (
        "c7cb00b6e3a9c82f92320c8a8e187ca6713a55d71735da69198c191779b3f1d5"
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


class Wave8SaukTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_path = ROOT / "data/review/hced-candidates.jsonl"
        cls.iwbd_path = ROOT / "data/review/iwbd-candidates.jsonl"
        cls.hced_rows = _jsonl(cls.hced_path)
        cls.iwbd_rows = _jsonl(cls.iwbd_path)
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced_rows
        }
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "sauk indians"
            or normalize_label(row.get("side_2_raw")) == "sauk indians"
        ]

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_SAUK_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_SAUK_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_SAUK_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_sauk_entities(entities)
        lane.install_wave8_sauk_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_sauk_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_locked_queue_files_and_exact_candidate_ids_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            lane.WAVE8_SAUK_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            lane.WAVE8_SAUK_IWBD_QUEUE_SHA256,
        )
        payload = "".join(
            f"{candidate_id}\n" for candidate_id in sorted(EXPECTED_RAW_ROWS)
        )
        self.assertEqual(
            hashlib.sha256(payload.encode()).hexdigest(),
            EXACT_CANDIDATE_ID_SHA256,
        )
        self.assertEqual(
            lane.WAVE8_SAUK_EXACT_CANDIDATE_ID_SHA256,
            EXACT_CANDIDATE_ID_SHA256,
        )

    def test_complete_exact_label_inventory_and_raw_fields_are_pinned(self) -> None:
        exact_by_id = {
            str(row["candidate_id"]): row for row in self.exact_rows
        }
        self.assertEqual(set(exact_by_id), set(EXPECTED_RAW_ROWS))
        self.assertEqual(
            lane.WAVE8_SAUK_EXPECTED_CANDIDATE_IDS,
            frozenset(EXPECTED_RAW_ROWS),
        )
        self.assertEqual(
            lane.WAVE8_SAUK_RESERVED_IDS,
            frozenset(EXPECTED_RAW_ROWS),
        )
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            row = exact_by_id[candidate_id]
            for field in (
                "name",
                "side_1_raw",
                "side_2_raw",
                "winner_raw",
                "loser_raw",
                "massacre_raw",
                "source_row",
            ):
                self.assertEqual(row[field], expected[field])
            self.assertEqual((row["year_low"], row["year_high"]), (1832, 1832))
            self.assertIs(row["winner_loser_complete"], True)
            self.assertEqual(
                canonical_hced_row_sha256(row),
                expected["hash"],
            )
            self.assertEqual(
                lane.WAVE8_SAUK_ROW_HASHES[candidate_id],
                expected["hash"],
            )

    def test_queue_validator_partitions_three_promotions_and_one_hold(self) -> None:
        self.assertEqual(
            lane.validate_wave8_sauk_queue_contracts(self.hced_rows),
            {
                "holds": 1,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.WAVE8_SAUK_CONTRACT_IDS,
            frozenset(EXPECTED_PROMOTIONS),
        )
        self.assertEqual(
            lane.WAVE8_SAUK_HOLD_IDS,
            frozenset({"hced-Kelloggs Grove1832-1"}),
        )
        self.assertFalse(lane.WAVE8_SAUK_TERMINAL_EXCLUSIONS)
        self.assertFalse(lane.WAVE8_SAUK_OUTCOME_OVERRIDES)
        self.assertEqual(
            lane.wave8_sauk_row_dispositions(),
            {
                "hced-Bad Axe1832-1": "promote",
                "hced-Kelloggs Grove1832-1": "hold",
                "hced-Rock River1832-1": "promote",
                "hced-Wisconsin Heights1832-1": "promote",
            },
        )

    def test_funnel_pins_four_sole_blockers_without_generic_identity(self) -> None:
        self.assertEqual(
            lane.validate_wave8_sauk_funnel(self.funnel),
            {
                "exact_label_rows": 4,
                "shared_label_rows": 0,
                "sole_blocker_rows": 4,
            },
        )
        label = next(
            row for row in self.funnel["labels"] if row["label"] == "sauk indians"
        )
        self.assertEqual(label["event_candidate_id_sha256"], EXACT_CANDIDATE_ID_SHA256)
        self.assertEqual(label["events_touched"], 4)
        self.assertEqual(label["sole_blocker_events"], 4)
        self.assertEqual(label["candidate_ids"], [])
        self.assertEqual(label["time_valid_candidate_ids"], [])
        self.assertEqual(label["failure_cases"]["zero_time_valid_candidates"], 4)

    def test_kelloggs_grove_remains_unknown_not_a_draw(self) -> None:
        hold = lane.WAVE8_SAUK_HOLDS["hced-Kelloggs Grove1832-1"]
        self.assertEqual(hold["disposition"], "hold")
        self.assertEqual(hold["result_type"], "unknown")
        self.assertIs(hold["unknown_is_never_draw"], True)
        self.assertEqual(
            hold["canonical_event"]["date_text"],
            "16 and 25 June 1832",
        )
        self.assertEqual(
            hold["canonical_event"]["granularity"],
            "ambiguous_same_place_multi_engagement_record",
        )
        reason = hold["hold_reason"].casefold()
        for phrase in (
            "not promoted",
            "separate actions",
            "accounts conflict",
            "invent certainty",
            "not a draw",
        ):
            self.assertIn(phrase, reason)
        for forbidden in (
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "outcome_source_ids",
            "outcome_source_family_ids",
        ):
            self.assertNotIn(forbidden, hold)

    def test_sources_are_model_valid_and_independent(self) -> None:
        self.assertEqual(len(lane.WAVE8_SAUK_SOURCES), 17)
        source_ids = {source["id"] for source in lane.WAVE8_SAUK_SOURCES}
        families = {
            source["source_family_id"] for source in lane.WAVE8_SAUK_SOURCES
        }
        self.assertEqual(len(source_ids), 17)
        self.assertGreaterEqual(len(families), 14)
        for source in lane.WAVE8_SAUK_SOURCES:
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["evidence_roles"], sorted(set(source["evidence_roles"])))
            self.assertEqual(Source.from_dict(source).to_dict(), source)

    def test_entities_are_event_bounded_and_never_generic_peoples_or_states(self) -> None:
        expected_ids = {
            STILLMAN_BAND_ID,
            STILLMAN_MILITIA_ID,
            WISCONSIN_BAND_ID,
            WISCONSIN_MILITIA_ID,
            BAD_AXE_BAND_ID,
            BAD_AXE_US_FORCE_ID,
        }
        by_id = {entity["id"]: entity for entity in lane.WAVE8_SAUK_ENTITIES}
        self.assertEqual(set(by_id), expected_ids)
        for entity in by_id.values():
            self.assertEqual((entity["start_year"], entity["end_year"]), (1832, 1832))
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            note = entity["continuity_note"].casefold()
            for phrase in (
                "only for the named 1832 action",
                "no rating is inherited",
                "sauk or meskwaki peoples",
                "modern tribal government",
                "united states as a whole",
                "noncombatants",
            ):
                self.assertIn(phrase, note)
            self.assertEqual(Entity.from_dict(entity).to_dict(), entity)
        bad_axe_note = by_id[BAD_AXE_BAND_ID]["continuity_note"].casefold()
        for boundary in ("women", "children", "elders", "noncombatant"):
            self.assertIn(boundary, bad_axe_note)

    def test_promotions_emit_exact_actions_dates_and_event_bounded_sides(self) -> None:
        events = self._events()
        by_candidate = {event["hced_candidate_id"]: event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_PROMOTIONS))
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            event = by_candidate[candidate_id]
            self.assertEqual(event["name"], expected["name"])
            self.assertEqual(event["year"], 1832)
            self.assertEqual(event["end_year"], 1832)
            self.assertEqual(event["date_precision"], expected["date_precision"])
            self.assertEqual(event["reviewed_granularity"], expected["granularity"])
            self.assertEqual(event["confidence"], expected["confidence"])
            self.assertEqual(event["war_type"], "colonial_anti_colonial")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            participants = {item["entity_id"]: item for item in event["participants"]}
            self.assertEqual(
                set(participants),
                {expected["winner"], expected["loser"]},
            )
            self.assertIn("victory", participants[expected["winner"]]["result_class"])
            self.assertIn("defeat", participants[expected["loser"]]["result_class"])
            self.assertFalse(
                any(item.get("result_class") == "draw" for item in event["participants"])
            )
        self.assertNotIn("hced-Kelloggs Grove1832-1", by_candidate)

    def test_promoted_outcomes_align_with_hced_without_override(self) -> None:
        for candidate_id, contract in lane.WAVE8_SAUK_CONTRACTS.items():
            row = self.hced_by_id[candidate_id]
            winner_side = int(contract["winner_side"])
            self.assertEqual(row["winner_raw"], row[f"side_{winner_side}_raw"])
            self.assertEqual(row["loser_raw"], row[f"side_{3 - winner_side}_raw"])
            self.assertIs(contract["source_outcome_override"], False)
            self.assertIs(contract["outcome_reversal"], False)
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 3)
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 3)
        self.assertEqual(
            lane.WAVE8_SAUK_CONTRACTS["hced-Rock River1832-1"]["winner_side"],
            1,
        )
        self.assertEqual(
            lane.WAVE8_SAUK_CONTRACTS["hced-Wisconsin Heights1832-1"]["winner_side"],
            1,
        )

    def test_wisconsin_heights_preserves_rearguard_success_without_flipping_result(self) -> None:
        contract = lane.WAVE8_SAUK_CONTRACTS["hced-Wisconsin Heights1832-1"]
        note = contract["audit_note"].casefold()
        for phrase in (
            "battlefield victory",
            "holding action",
            "protective purpose",
            "reduced confidence",
            "contested-field result",
        ):
            self.assertIn(phrase, note)
        self.assertEqual(contract["confidence"], 0.82)
        audit = lane.WAVE8_SAUK_SCOPE_AND_OPPOSITE_RESULT_AUDIT[
            "hced-Wisconsin Heights1832-1"
        ]
        self.assertEqual(audit["reviewed_result"], "U.S. battlefield victory")

    def test_bad_axe_rates_combat_only_and_preserves_massacre_scope(self) -> None:
        contract = lane.WAVE8_SAUK_CONTRACTS["hced-Bad Axe1832-1"]
        self.assertEqual(
            contract["canonical_event"]["granularity"],
            "engagement_followed_by_massacre",
        )
        self.assertEqual(contract["canonical_event"]["date_text"], "1-2 August 1832")
        note = contract["audit_note"].casefold()
        for phrase in (
            "combat victory",
            "killing of fleeing noncombatants",
            "only the event-bounded fighting formations are rated",
            "civilian deaths are not transformed into an elo result",
        ):
            self.assertIn(phrase, note)
        self.assertEqual(
            lane.WAVE8_SAUK_SCOPE_AND_OPPOSITE_RESULT_AUDIT[
                "hced-Bad Axe1832-1"
            ]["scope"],
            "engagement followed by massacre",
        )

    def test_promoted_points_are_withheld_and_us_country_is_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_SAUK_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_SAUK_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_SAUK_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            set(lane.WAVE8_SAUK_LOCATION_QUARANTINE_REASONS),
            set(EXPECTED_PROMOTIONS),
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "United States")
            self.assertIn("location_provenance", event)

    def test_local_promotion_does_not_mutate_global_quarantine_sets(self) -> None:
        point_before = frozenset(HCED_POINT_QUARANTINE_IDS)
        country_before = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        self._events()
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), point_before)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), country_before)

    def test_installed_fixtures_and_emitted_events_are_model_valid(self) -> None:
        entities, sources, _ = self._installed()
        for fixture in lane.WAVE8_SAUK_ENTITIES:
            Entity.from_dict(entities[fixture["id"]])
        for fixture in lane.WAVE8_SAUK_SOURCES:
            Source.from_dict(sources[fixture["id"]])
        for event in self._events():
            Event.from_dict(event)

    def test_promotion_is_deterministic_and_does_not_mutate_inputs(self) -> None:
        entities, _, existing = self._installed()
        rows_before = copy.deepcopy(self.hced_rows)
        entities_before = copy.deepcopy(entities)
        existing_before = copy.deepcopy(existing)
        first = lane.promote_wave8_sauk_contracts(self.hced_rows, entities, existing)
        second = lane.promote_wave8_sauk_contracts(self.hced_rows, entities, existing)
        self.assertEqual(first, second)
        self.assertEqual(self.hced_rows, rows_before)
        self.assertEqual(entities, entities_before)
        self.assertEqual(existing, existing_before)

    def test_adjacent_sawk_and_composite_labels_are_explicitly_outside_lane(self) -> None:
        self.assertEqual(
            set(lane.WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS),
            set(EXPECTED_ADJACENT_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_SAUK_ADJACENT_LITERAL_LABEL_INVENTORY,
            {
                "sauk indians fox indians kickapoo indians": frozenset(
                    {"hced-Rock Island Rapids1814-1"}
                ),
                "sawk indians": frozenset({"hced-Pecatonica1832-1"}),
            },
        )
        for candidate_id, expected_hash in EXPECTED_ADJACENT_HASHES.items():
            row = self.hced_by_id[candidate_id]
            disposition = lane.WAVE8_SAUK_ADJACENT_HCED_DISPOSITIONS[candidate_id]
            self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
            self.assertEqual(disposition["raw_row_sha256"], expected_hash)
            self.assertIs(disposition["outcome_not_adjudicated"], True)
            self.assertIsNone(disposition["owner_module"])
            self.assertNotIn(candidate_id, lane.WAVE8_SAUK_RESERVED_IDS)

    def test_black_hawk_and_kickapoo_overlap_never_creates_cross_lane_ownership(self) -> None:
        disposition = lane.WAVE8_SAUK_CROSS_LANE_DISPOSITIONS["wave8_kickapoo"]
        self.assertEqual(
            disposition["candidate_ids"],
            ["hced-Rock Island Rapids1814-1"],
        )
        self.assertIn(
            "outside_both_exact_label_lanes",
            disposition["disposition"],
        )
        self.assertIn("neither lane claims", disposition["reason"].casefold())
        self.assertEqual(
            set(lane.WAVE8_SAUK_SCOPE_AND_OPPOSITE_RESULT_AUDIT),
            set(EXPECTED_RAW_ROWS) | set(EXPECTED_ADJACENT_HASHES),
        )

    def test_iwbd_hced_release_and_alternate_name_duplicate_audits_are_zero(self) -> None:
        _, _, existing = self._installed()
        result = lane.validate_wave8_sauk_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            existing,
        )
        self.assertEqual(
            result,
            {
                "adjacent_hced_dispositions": 2,
                "cross_lane_dispositions": 1,
                "existing_release_duplicate_dispositions": 0,
                "hced_duplicate_dispositions": 0,
                "integration_dispositions": 3,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 4,
            },
        )
        self.assertFalse(lane.WAVE8_SAUK_HCED_DUPLICATE_DISPOSITIONS)
        self.assertFalse(lane.WAVE8_SAUK_IWBD_DUPLICATE_DISPOSITIONS)
        self.assertFalse(lane.WAVE8_SAUK_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS)
        self.assertEqual(
            set(lane.WAVE8_SAUK_IWBD_ZERO_OVERLAP_AUDIT),
            set(EXPECTED_RAW_ROWS),
        )

    def test_integration_validator_fails_closed_on_new_hced_twin(self) -> None:
        planted = copy.deepcopy(self.hced_by_id["hced-Rock River1832-1"])
        planted["candidate_id"] = "hced-PlantedStillmansRun1832-1"
        planted["source_record_id"] = "PlantedStillmansRun1832"
        planted["name"] = "Stillman's Run"
        planted["side_1_raw"] = "Unrelated A"
        planted["side_2_raw"] = "Unrelated B"
        with self.assertRaisesRegex(ValueError, "unreviewed HCED twin"):
            lane.validate_wave8_sauk_integration_dispositions(
                [*self.hced_rows, planted],
                self.iwbd_rows,
                (),
            )

    def test_integration_validator_fails_closed_on_new_iwbd_twin(self) -> None:
        planted = {
            "candidate_id": "iwbd-planted-bad-axe",
            "name": "Bad Axe Massacre",
            "start_date": "1832-08-01",
            "end_date": "1832-08-02",
        }
        with self.assertRaisesRegex(ValueError, "unreviewed IWBD twin"):
            lane.validate_wave8_sauk_integration_dispositions(
                self.hced_rows,
                [*self.iwbd_rows, planted],
                (),
            )

    def test_integration_validator_fails_closed_on_new_release_twin(self) -> None:
        planted = {
            "id": "planted_wisconsin_heights_twin",
            "name": "Battle of Wisconsin Heights",
            "year": 1832,
        }
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_sauk_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [planted],
            )

    def test_queue_and_adjacent_validators_fail_closed_on_drift(self) -> None:
        rows = copy.deepcopy(self.hced_rows)
        target = next(
            row for row in rows if row["candidate_id"] == "hced-Bad Axe1832-1"
        )
        target["winner_raw"] = "Sauk Indians"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            lane.validate_wave8_sauk_queue_contracts(rows)

        rows = copy.deepcopy(self.hced_rows)
        adjacent = next(
            row for row in rows if row["candidate_id"] == "hced-Pecatonica1832-1"
        )
        adjacent["winner_raw"] = "Sawk Indians"
        with self.assertRaisesRegex(ValueError, "adjacent HCED row changed"):
            lane.validate_wave8_sauk_integration_dispositions(rows, self.iwbd_rows, ())

    def test_installers_are_idempotent_and_fail_on_conflicting_fixtures(self) -> None:
        entities, sources, _ = self._installed()
        lane.install_wave8_sauk_entities(entities)
        lane.install_wave8_sauk_sources(sources)
        self.assertIn(STILLMAN_BAND_ID, entities)

        conflicting_entities = copy.deepcopy(entities)
        conflicting_entities[STILLMAN_BAND_ID]["name"] = "tampered"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_sauk_entities(conflicting_entities)

        source_id = lane.WAVE8_SAUK_SOURCES[0]["id"]
        conflicting_sources = copy.deepcopy(sources)
        conflicting_sources[source_id]["title"] = "tampered"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_sauk_sources(conflicting_sources)

    def test_promotion_fails_closed_on_existing_event_collision(self) -> None:
        entities, _, existing = self._installed()
        collision = {
            "id": "planted_stillman_collision",
            "name": "Battle of Stillman's Run",
            "year": 1832,
        }
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_sauk_contracts(
                self.hced_rows,
                entities,
                [*existing, collision],
            )

    def test_current_release_is_unwired_or_fully_wired_never_partial(self) -> None:
        released_candidates = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
            if str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
            or event.get("hced_candidate_id") in lane.WAVE8_SAUK_CONTRACT_IDS
        }
        expected = set(lane.WAVE8_SAUK_CONTRACT_IDS)
        self.assertIn(released_candidates, (set(), expected))

    def test_counts_cohort_metadata_and_signature_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_sauk_cohort_counts(),
            {"black_hawk_war_1832": 4},
        )
        counts = lane.wave8_sauk_counts()
        self.assertEqual(counts["reviewed_hced_rows"], 4)
        self.assertEqual(counts["promotion_contracts"], 3)
        self.assertEqual(counts["holds"], 1)
        self.assertEqual(counts["terminal_exclusions"], 0)
        self.assertEqual(counts["new_entities"], 6)
        self.assertEqual(counts["new_sources"], 17)
        self.assertEqual(counts["point_quarantine_additions"], 3)
        self.assertEqual(counts["country_quarantine_additions"], 0)
        self.assertEqual(counts["outcome_overrides"], 0)
        self.assertEqual(counts["adjacent_hced_dispositions"], 2)
        self.assertEqual(counts["cross_lane_dispositions"], 1)
        metadata = lane.wave8_sauk_metadata()
        self.assertEqual(metadata["counts"], counts)
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            sorted(EXPECTED_PROMOTIONS),
        )
        self.assertEqual(
            metadata["hold_ids"],
            ["hced-Kelloggs Grove1832-1"],
        )
        self.assertEqual(lane.wave8_sauk_audit_signature(), FINAL_AUDIT_SIGNATURE)
        self.assertEqual(lane.WAVE8_SAUK_FINAL_AUDIT_SIGNATURE, FINAL_AUDIT_SIGNATURE)


if __name__ == "__main__":
    unittest.main()
