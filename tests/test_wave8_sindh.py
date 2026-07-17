import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_sindh as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
DAHIR = "raja_dahir_sindh_force_raor_712"
MIANI = "talpur_amirs_coalition_miani_1843"
SHER_MUHAMMAD = "mir_sher_muhammad_talpur_resistance_1843"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8SindhTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        lane.install_wave8_sindh_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_SINDH_CONTRACT_IDS
            and not str(event.get("id", "")).startswith("hced_wave8_sindh_")
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_sindh_contracts(self.hced, entities, existing)

    def test_exact_inventory_and_row_hashes_are_pinned(self) -> None:
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if str(row.get("candidate_id")) in lane.WAVE8_SINDH_ROW_HASHES
        }
        self.assertEqual(set(rows), set(lane.WAVE8_SINDH_ROW_HASHES))
        self.assertEqual(len(rows), 4)
        for candidate_id, expected in lane.WAVE8_SINDH_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected)
                self.assertEqual(row["winner_raw"], row["side_1_raw"])
                self.assertEqual(row["loser_raw"], row["side_2_raw"])
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_sindh_queue_contracts(self.hced),
            {
                "exact_label_rows": 4,
                "holds": 0,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
            },
        )
        current_labels = {
            str(row.get("label")) for row in self.funnel.get("labels", [])
        }
        if {"sind", "sindh"} <= current_labels:
            self.assertEqual(
                lane.validate_wave8_sindh_funnel(self.funnel),
                {
                    "events_touched": 4,
                    "sole_blocker_events": 4,
                    "unresolved_side_attempts": 4,
                    "zero_time_valid_candidates": 4,
                },
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"][
                    "wave8_sindh_exact_label_funnel_audit"
                ],
                lane.WAVE8_SINDH_FUNNEL_AUDIT,
            )

    def test_three_narrow_identities_replace_no_generic_sind_alias(self) -> None:
        entities = {str(item["id"]): item for item in lane.WAVE8_SINDH_ENTITIES}
        self.assertEqual(set(entities), {DAHIR, MIANI, SHER_MUHAMMAD})
        self.assertEqual(
            (entities[DAHIR]["start_year"], entities[DAHIR]["end_year"]),
            (712, 712),
        )
        self.assertEqual(
            (entities[MIANI]["start_year"], entities[MIANI]["end_year"]),
            (1843, 1843),
        )
        self.assertEqual(
            (
                entities[SHER_MUHAMMAD]["start_year"],
                entities[SHER_MUHAMMAD]["end_year"],
            ),
            (1843, 1843),
        )
        for entity in entities.values():
            self.assertFalse(entity["aliases"])
            self.assertNotIn(entity["name"].casefold(), {"sind", "sindh"})
            Entity.from_dict(entity)

    def test_sources_parse_and_each_event_has_two_outcome_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_SINDH_SOURCES), 10)
        for source in lane.WAVE8_SINDH_SOURCES:
            Source.from_dict(source)
        for candidate_id, contract in lane.WAVE8_SINDH_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
                self.assertGreaterEqual(
                    len(contract["outcome_source_family_ids"]), 2
                )
                self.assertEqual(
                    contract["outcome_source_family_ids"],
                    sorted(set(contract["outcome_source_family_ids"])),
                )

    def test_all_four_distinct_battles_promote(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_SINDH_CONTRACT_IDS)
        expected = {
            "hced-Raor712-1": ("Battle of Raor", 712, "year", 0.94),
            "hced-Miani1843-1": ("Battle of Miani", 1843, "day", 0.99),
            "hced-Hyderabad, Pakistan1843-1": (
                "Battle of Dubba",
                1843,
                "day",
                0.99,
            ),
            "hced-Shahdadpur1843-1": (
                "Battle of Shahdadpur",
                1843,
                "day_range",
                0.97,
            ),
        }
        for candidate_id, values in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(
                    (
                        event["name"],
                        event["year"],
                        event["date_precision"],
                        event["confidence"],
                    ),
                    values,
                )
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                Event.from_dict(event)

    def test_actor_split_matches_the_reviewed_campaigns(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}

        def outcomes(candidate_id):
            return {
                item["entity_id"]: item["termination"]
                for item in events[candidate_id]["participants"]
            }

        self.assertEqual(
            outcomes("hced-Raor712-1"),
            {
                "umayyad_caliphate": "engagement_victory",
                DAHIR: "engagement_defeat",
            },
        )
        self.assertEqual(
            outcomes("hced-Miani1843-1"),
            {
                "united_kingdom": "engagement_victory",
                MIANI: "engagement_defeat",
            },
        )
        for candidate_id in (
            "hced-Hyderabad, Pakistan1843-1",
            "hced-Shahdadpur1843-1",
        ):
            self.assertEqual(
                outcomes(candidate_id),
                {
                    "united_kingdom": "engagement_victory",
                    SHER_MUHAMMAD: "engagement_defeat",
                },
            )

    def test_no_result_is_overridden_reversed_or_invented(self) -> None:
        self.assertFalse(lane.WAVE8_SINDH_HOLDS)
        self.assertFalse(lane.WAVE8_SINDH_HOLD_IDS)
        self.assertEqual(
            lane.WAVE8_SINDH_RESERVED_IDS,
            set(lane.WAVE8_SINDH_ROW_HASHES),
        )
        for contract in lane.WAVE8_SINDH_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_all_points_are_withheld_but_country_is_retained(self) -> None:
        events = self._events()
        self.assertEqual(
            lane.WAVE8_SINDH_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_SINDH_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_SINDH_COUNTRY_QUARANTINE_ADDITIONS)
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Pakistan")
            self.assertIn("location_provenance", event)

    def test_no_probable_cross_source_twins_exist(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_sindh_integration_dispositions(
                self.hced, self.iwbd, existing
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_current_release_activates_all_three_identities(self) -> None:
        events = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_SINDH_CONTRACT_IDS
        ]
        self.assertEqual(len(events), 4)
        self.assertEqual(
            {event["name"] for event in events},
            {
                "Battle of Dubba",
                "Battle of Miani",
                "Battle of Raor",
                "Battle of Shahdadpur",
            },
        )
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Pakistan")

        release_entities = {
            str(item["id"]): item for item in self.release_entities
        }
        registry_entities = {
            str(item["id"]): item for item in self.registry["entities"]
        }
        for entity_id in (DAHIR, MIANI, SHER_MUHAMMAD):
            self.assertIn(entity_id, release_entities)
            self.assertFalse(release_entities[entity_id]["aliases"])
            self.assertEqual(registry_entities[entity_id]["status"], "rated")

    def test_release_metadata_and_source_registry_publish_the_lane(self) -> None:
        source_ids = {str(item["id"]) for item in self.release_sources}
        self.assertTrue(
            {str(item["id"]) for item in lane.WAVE8_SINDH_SOURCES} <= source_ids
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_sindh_hced_events"], 4)
        self.assertEqual(
            promotion["wave8_sindh_candidate_ids"],
            sorted(lane.WAVE8_SINDH_CONTRACT_IDS),
        )
        self.assertFalse(promotion["wave8_sindh_holds"])
        self.assertEqual(
            self.registry["coverage"]["candidate_keyed_wave8_sindh_hced_events"],
            4,
        )

    def test_release_and_registry_counts_include_the_exact_sindh_delta(self) -> None:
        self.assertEqual(len(self.release_entities), 1_001)
        self.assertEqual(len(self.release_events), 5_345)
        self.assertEqual(len(self.registry["entities"]), 2_350)
        self.assertEqual(
            self.registry["coverage"]["unresolved_event_candidates"],
            18_049,
        )
        location = self.registry["coverage"]["hced_location_assertions"]
        self.assertEqual(location["hced_candidate_bindings"], 5_081)
        self.assertEqual(location["geojson_points"], 4_734)
        self.assertEqual(location["modern_location_country_assertions"], 4_986)

    def test_tampered_queue_row_fails_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Raor712-1"
        )
        row["winner_raw"] = "Sindh"
        with self.assertRaises(ValueError):
            lane.validate_wave8_sindh_queue_contracts(tampered)

    def test_existing_candidate_collision_fails_closed(self) -> None:
        entities, existing = self._installed()
        existing.append(
            {
                "id": "collision",
                "name": "Different title",
                "year": 712,
                "hced_candidate_id": "hced-Raor712-1",
            }
        )
        with self.assertRaises(ValueError):
            lane.promote_wave8_sindh_contracts(self.hced, entities, existing)

    def test_installers_are_idempotent_and_reject_drift(self) -> None:
        entities = {}
        lane.install_wave8_sindh_entities(entities)
        lane.install_wave8_sindh_entities(entities)
        entities[DAHIR]["name"] = "drift"
        with self.assertRaises(ValueError):
            lane.install_wave8_sindh_entities(entities)

        sources = {}
        lane.install_wave8_sindh_sources(sources)
        lane.install_wave8_sindh_sources(sources)
        sources["wave8_sindh_lambrick_battles"]["title"] = "drift"
        with self.assertRaises(ValueError):
            lane.install_wave8_sindh_sources(sources)

    def test_signature_and_counts_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_sindh_audit_signature(),
            lane.WAVE8_SINDH_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_sindh_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 0,
                "new_entities": 3,
                "new_sources": 10,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_sindh_cohort_counts(),
            {"sind_sindh_exact_labels_712_1843": 4},
        )


if __name__ == "__main__":
    unittest.main()
