import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_goguryeo as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
GOGURYEO = "clio_kr_goguryeo_k_bce36_8b810bef"
SILLA = "clio_q28456_378_7ba3b7e4"
SUI = "clio_cn_sui_dyn_587_af2a9518"
TANG = "clio_cn_tang_dyn_1_623_3e98c37b"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8GoguryeoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.cliopatria = _jsonl(
            ROOT / "data/review/cliopatria-entity-candidates.jsonl"
        )
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
        lane.install_wave8_goguryeo_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_GOGURYEO_CONTRACT_IDS
            and not str(event.get("id", "")).startswith("hced_wave8_goguryeo_")
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_goguryeo_contracts(
            self.hced, entities, existing
        )

    def test_exact_inventory_and_row_hashes_are_pinned(self) -> None:
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if str(row.get("candidate_id")) in lane.WAVE8_GOGURYEO_ROW_HASHES
        }
        self.assertEqual(set(rows), set(lane.WAVE8_GOGURYEO_ROW_HASHES))
        self.assertEqual(len(rows), 3)
        for candidate_id, expected in lane.WAVE8_GOGURYEO_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(canonical_hced_row_sha256(rows[candidate_id]), expected)
                self.assertIs(rows[candidate_id]["winner_loser_complete"], True)
                self.assertEqual(rows[candidate_id]["massacre_raw"], "No")

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_goguryeo_queue_contracts(self.hced),
            {
                "exact_label_rows": 3,
                "holds": 0,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 3,
            },
        )
        self.assertEqual(
            lane.validate_wave8_goguryeo_funnel(self.funnel),
            {
                "events_touched": 3,
                "sole_blocker_events": 3,
                "zero_time_valid_candidates": 3,
            },
        )

    def test_three_registry_candidates_are_curated_without_global_aliases(self) -> None:
        candidate_by_name = {
            str(row.get("canonical_name_candidate")): row for row in self.cliopatria
        }
        self.assertEqual(candidate_by_name["Goguryeo"]["candidate_id"], "cliopatria-840")
        self.assertEqual(candidate_by_name["Silla"]["candidate_id"], "cliopatria-844")
        self.assertEqual(
            candidate_by_name["Tang Dynasty"]["candidate_id"], "cliopatria-1571"
        )
        entities = {str(item["id"]): item for item in lane.WAVE8_GOGURYEO_ENTITIES}
        self.assertEqual(set(entities), {GOGURYEO, SILLA, TANG})
        self.assertEqual(
            {
                entity_id: (entity["start_year"], entity["end_year"])
                for entity_id, entity in entities.items()
            },
            {
                GOGURYEO: (-36, 681),
                SILLA: (378, 681),
                TANG: (623, 910),
            },
        )
        for entity in entities.values():
            self.assertFalse(entity["aliases"])
            Entity.from_dict(entity)
        self.assertNotIn(SUI, entities)

    def test_sources_parse_and_every_outcome_has_independent_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_GOGURYEO_SOURCES), 4)
        for source in lane.WAVE8_GOGURYEO_SOURCES:
            Source.from_dict(source)
        for contract in lane.WAVE8_GOGURYEO_CONTRACTS.values():
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(set(contract["outcome_source_family_ids"])),
            )

    def test_all_three_exact_rows_promote_and_none_are_held(self) -> None:
        self.assertEqual(
            lane.WAVE8_GOGURYEO_CONTRACT_IDS,
            {
                "hced-Ansi-song645-1",
                "hced-Pyongyang668-1",
                "hced-Salsu612-1",
            },
        )
        self.assertFalse(lane.WAVE8_GOGURYEO_HOLD_IDS)
        self.assertEqual(
            lane.WAVE8_GOGURYEO_RESERVED_IDS,
            set(lane.WAVE8_GOGURYEO_ROW_HASHES),
        )

    def test_locked_outcomes_and_pyongyang_coalition_are_preserved(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_GOGURYEO_CONTRACT_IDS)
        expected = {
            "hced-Salsu612-1": ({GOGURYEO}, {SUI}),
            "hced-Ansi-song645-1": ({GOGURYEO}, {TANG}),
            "hced-Pyongyang668-1": ({TANG, SILLA}, {GOGURYEO}),
        }
        for candidate_id, (winner_ids, loser_ids) in expected.items():
            event = events[candidate_id]
            outcomes = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(
                {entity_id for entity_id, result in outcomes.items() if result == "engagement_victory"},
                winner_ids,
            )
            self.assertEqual(
                {entity_id for entity_id, result in outcomes.items() if result == "engagement_defeat"},
                loser_ids,
            )
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertFalse(
                lane.WAVE8_GOGURYEO_CONTRACTS[candidate_id]["source_outcome_override"]
            )
            Event.from_dict(event)

    def test_canonical_names_years_and_confidence_are_pinned(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        expected = {
            "hced-Salsu612-1": ("Battle of Salsu", 612, 0.97),
            "hced-Ansi-song645-1": ("Siege of Ansi Fortress", 645, 0.96),
            "hced-Pyongyang668-1": ("Siege and Fall of Pyongyang", 668, 0.98),
        }
        for candidate_id, (name, year, confidence) in expected.items():
            event = events[candidate_id]
            self.assertEqual(event["name"], name)
            self.assertEqual((event["year"], event["end_year"]), (year, year))
            self.assertEqual(event["confidence"], confidence)

    def test_points_are_withheld_and_countries_are_retained(self) -> None:
        expected_countries = {
            "hced-Salsu612-1": "North Korea",
            "hced-Ansi-song645-1": "China",
            "hced-Pyongyang668-1": "North Korea",
        }
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(
                event["modern_location_country"],
                expected_countries[event["hced_candidate_id"]],
            )
            self.assertIn("location_provenance", event)

    def test_no_probable_cross_source_twins_exist(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_goguryeo_integration_dispositions(
                self.hced, self.iwbd, existing
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_current_release_activates_three_curated_identities(self) -> None:
        events = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_GOGURYEO_CONTRACT_IDS
        ]
        self.assertEqual(len(events), 3)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            lane.WAVE8_GOGURYEO_CONTRACT_IDS,
        )

        release_entities = {
            str(item["id"]): item for item in self.release_entities
        }
        registry_entities = {
            str(item["id"]): item for item in self.registry["entities"]
        }
        for entity_id in (GOGURYEO, SILLA, TANG):
            self.assertIn(entity_id, release_entities)
            self.assertFalse(release_entities[entity_id]["aliases"])
            self.assertEqual(registry_entities[entity_id]["status"], "rated")
            self.assertEqual(
                registry_entities[entity_id]["identity_status"],
                "curated",
            )

        source_ids = {str(item["id"]) for item in self.release_sources}
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_GOGURYEO_SOURCES},
            source_ids,
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_goguryeo_hced_events"], 3)
        self.assertEqual(
            promotion["wave8_goguryeo_candidate_ids"],
            sorted(lane.WAVE8_GOGURYEO_CONTRACT_IDS),
        )
        self.assertFalse(promotion["wave8_goguryeo_holds"])
        self.assertEqual(
            self.registry["coverage"][
                "candidate_keyed_wave8_goguryeo_hced_events"
            ],
            3,
        )

    def test_row_drift_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Ansi-song645-1"
        )
        row["winner_raw"] = "China"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_goguryeo_queue_contracts(tampered)

        entities, existing = self._installed()
        existing.append(
            {
                "id": "duplicate",
                "name": "Battle of Salsu",
                "year": 612,
                "participants": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_goguryeo_contracts(
                self.hced, entities, existing
            )

    def test_source_and_entity_installers_are_idempotent_and_collision_safe(self) -> None:
        entities, _ = self._installed()
        before = {entity_id: copy.deepcopy(entities[entity_id]) for entity_id in (GOGURYEO, SILLA, TANG)}
        lane.install_wave8_goguryeo_entities(entities)
        self.assertEqual(
            {entity_id: entities[entity_id] for entity_id in before},
            before,
        )

        sources = {}
        lane.install_wave8_goguryeo_sources(sources)
        lane.install_wave8_goguryeo_sources(sources)
        self.assertEqual(len(sources), 4)
        sources["wave8_goguryeo_aks_history"]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_goguryeo_sources(sources)

    def test_signature_counts_and_cohorts_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_goguryeo_audit_signature(),
            lane.WAVE8_GOGURYEO_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_goguryeo_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 0,
                "new_entities": 3,
                "new_sources": 4,
                "newly_rated_events": 3,
                "outcome_overrides": 0,
                "point_quarantine_additions": 3,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_goguryeo_cohort_counts(),
            {"goguryeo_sui_tang_wars_612_668": 3},
        )


if __name__ == "__main__":
    unittest.main()
