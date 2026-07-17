import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_kievan_rus as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
KIEVAN_RUS = "clio_ua_kievan_rus_882_b1e5ac40"
BYZANTIUM = "byzantine_empire"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8KievanRusTests(unittest.TestCase):
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

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        lane.install_wave8_kievan_rus_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_KIEVAN_RUS_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(
                "hced_wave8_kievan_rus_"
            )
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_kievan_rus_contracts(
            self.hced, entities, existing
        )

    def test_exact_inventory_and_row_hashes_are_pinned(self) -> None:
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if str(row.get("candidate_id")) in lane.WAVE8_KIEVAN_RUS_ROW_HASHES
        }
        self.assertEqual(set(rows), set(lane.WAVE8_KIEVAN_RUS_ROW_HASHES))
        for candidate_id, expected in lane.WAVE8_KIEVAN_RUS_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(canonical_hced_row_sha256(rows[candidate_id]), expected)
                self.assertIs(rows[candidate_id]["winner_loser_complete"], True)

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_kievan_rus_queue_contracts(self.hced),
            {
                "exact_label_rows": 6,
                "holds": 4,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 6,
            },
        )
        self.assertEqual(
            lane.validate_wave8_kievan_rus_funnel(self.funnel),
            {
                "events_touched": 6,
                "sole_blocker_events": 3,
                "zero_time_valid_candidates": 6,
            },
        )

    def test_existing_registry_candidate_is_curated_without_kiev_alias(self) -> None:
        candidate = next(
            row
            for row in self.cliopatria
            if row.get("canonical_name_candidate") == "Kievan Rus'"
        )
        self.assertEqual(candidate["candidate_id"], "cliopatria-94")
        entity = lane.WAVE8_KIEVAN_RUS_ENTITIES[0]
        self.assertEqual(entity["id"], KIEVAN_RUS)
        self.assertEqual((entity["start_year"], entity["end_year"]), (882, 1240))
        self.assertFalse(entity["aliases"])
        self.assertNotEqual(entity["name"].lower(), "kiev")
        Entity.from_dict(entity)

    def test_sources_parse_and_each_promotion_has_two_outcome_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_KIEVAN_RUS_SOURCES), 3)
        for source in lane.WAVE8_KIEVAN_RUS_SOURCES:
            Source.from_dict(source)
        for contract in lane.WAVE8_KIEVAN_RUS_CONTRACTS.values():
            self.assertEqual(len(contract["outcome_source_ids"]), 2)
            self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(set(contract["outcome_source_family_ids"])),
            )

    def test_only_two_tenth_century_rows_promote(self) -> None:
        self.assertEqual(
            lane.WAVE8_KIEVAN_RUS_CONTRACT_IDS,
            {"hced-Arcadiopolis970-1", "hced-Dorostalon971-1"},
        )
        self.assertEqual(len(lane.WAVE8_KIEVAN_RUS_HOLD_IDS), 4)
        self.assertEqual(
            lane.WAVE8_KIEVAN_RUS_RESERVED_IDS,
            set(lane.WAVE8_KIEVAN_RUS_ROW_HASHES),
        )
        for hold in lane.WAVE8_KIEVAN_RUS_HOLDS.values():
            self.assertEqual(hold["disposition"], "hold")
            self.assertTrue(hold["reason_code"])

    def test_promotions_retain_locked_byzantine_winners(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_KIEVAN_RUS_CONTRACT_IDS)
        for candidate_id, event in events.items():
            outcomes = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(outcomes[BYZANTIUM], "engagement_victory")
            self.assertEqual(outcomes[KIEVAN_RUS], "engagement_defeat")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(
                set(event["outcome_source_ids"]),
                {
                    "wave8_kievan_rus_hanak_sviatoslav",
                    "wave8_kievan_rus_leo_deacon",
                },
            )
            self.assertFalse(
                lane.WAVE8_KIEVAN_RUS_CONTRACTS[candidate_id][
                    "source_outcome_override"
                ]
            )
            Event.from_dict(event)

    def test_canonical_names_and_confidence_are_pinned(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(
            events["hced-Arcadiopolis970-1"]["name"],
            "Battle of Arcadiopolis",
        )
        self.assertEqual(
            events["hced-Dorostalon971-1"]["name"],
            "Siege and Battle of Dorostolon",
        )
        self.assertEqual(events["hced-Arcadiopolis970-1"]["confidence"], 0.90)
        self.assertEqual(events["hced-Dorostalon971-1"]["confidence"], 0.96)
        self.assertEqual(
            {event["year"] for event in events.values()},
            {970, 971},
        )

    def test_points_are_withheld_and_countries_are_retained(self) -> None:
        expected_countries = {
            "hced-Arcadiopolis970-1": "Turkey",
            "hced-Dorostalon971-1": "Bulgaria",
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
            lane.validate_wave8_kievan_rus_integration_dispositions(
                self.hced, self.iwbd, existing
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_row_drift_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Arcadiopolis970-1"
        )
        row["winner_raw"] = "Kiev"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_kievan_rus_queue_contracts(tampered)

        entities, existing = self._installed()
        existing.append(
            {
                "id": "duplicate",
                "name": "Battle of Arcadiopolis",
                "year": 970,
                "participants": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_kievan_rus_contracts(
                self.hced, entities, existing
            )

    def test_source_and_entity_installers_are_idempotent_and_collision_safe(self) -> None:
        entities, _ = self._installed()
        before = copy.deepcopy(entities[KIEVAN_RUS])
        lane.install_wave8_kievan_rus_entities(entities)
        self.assertEqual(entities[KIEVAN_RUS], before)

        sources = {}
        lane.install_wave8_kievan_rus_sources(sources)
        lane.install_wave8_kievan_rus_sources(sources)
        self.assertEqual(len(sources), 3)
        sources["wave8_kievan_rus_leo_deacon"]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_kievan_rus_sources(sources)

    def test_signature_counts_and_cohorts_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_kievan_rus_audit_signature(),
            lane.WAVE8_KIEVAN_RUS_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_kievan_rus_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 4,
                "new_entities": 1,
                "new_sources": 3,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 6,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_kievan_rus_cohort_counts(),
            {
                "later_kiev_identity_holds": 4,
                "sviatoslav_byzantine_war_970_971": 2,
            },
        )


if __name__ == "__main__":
    unittest.main()
