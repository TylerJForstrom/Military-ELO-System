import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_fln as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
FOURTH_REPUBLIC = "clio_fr_france_modern_2_1945_396ed149"
ALN = "algerian_national_liberation_army_1954_1962"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8FlnTests(unittest.TestCase):
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
        lane.install_wave8_fln_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_FLN_CONTRACT_IDS
            and not str(event.get("id", "")).startswith("hced_wave8_fln_")
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_fln_contracts(self.hced, entities, existing)

    def test_exact_inventory_and_row_hashes_are_pinned(self) -> None:
        rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if str(row.get("candidate_id")) in lane.WAVE8_FLN_ROW_HASHES
        }
        self.assertEqual(set(rows), set(lane.WAVE8_FLN_ROW_HASHES))
        self.assertEqual(len(rows), 4)
        for candidate_id, expected in lane.WAVE8_FLN_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected)
                self.assertEqual((row["side_1_raw"], row["side_2_raw"]), ("France", "FLN"))
                self.assertEqual((row["winner_raw"], row["loser_raw"]), ("France", "FLN"))
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_fln_queue_contracts(self.hced),
            {
                "exact_label_rows": 4,
                "holds": 3,
                "promotion_contracts": 1,
                "reviewed_hced_rows": 4,
            },
        )
        current_labels = {
            str(row.get("label")) for row in self.funnel.get("labels", [])
        }
        if "fln" in current_labels:
            self.assertEqual(
                lane.validate_wave8_fln_funnel(self.funnel),
                {
                    "events_touched": 4,
                    "sole_blocker_events": 3,
                    "unresolved_side_attempts": 4,
                    "zero_time_valid_candidates": 4,
                },
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"][
                    "wave8_fln_exact_label_funnel_audit"
                ],
                lane.WAVE8_FLN_FUNNEL_AUDIT,
            )

    def test_preferred_fourth_republic_candidate_is_curated_without_aliases(self) -> None:
        candidates = {
            str(row.get("canonical_name_candidate")): row for row in self.cliopatria
        }
        self.assertEqual(
            candidates["French Fourth Republic"]["candidate_id"],
            "cliopatria-1291",
        )
        self.assertEqual(
            candidates["(French Fourth Republic)"]["candidate_id"],
            "cliopatria-1290",
        )
        entities = {str(item["id"]): item for item in lane.WAVE8_FLN_ENTITIES}
        self.assertEqual(set(entities), {FOURTH_REPUBLIC, ALN})
        self.assertEqual(
            (
                entities[FOURTH_REPUBLIC]["name"],
                entities[FOURTH_REPUBLIC]["start_year"],
                entities[FOURTH_REPUBLIC]["end_year"],
            ),
            ("French Fourth Republic", 1946, 1958),
        )
        self.assertEqual(
            (
                entities[ALN]["name"],
                entities[ALN]["start_year"],
                entities[ALN]["end_year"],
            ),
            ("Algerian National Liberation Army", 1954, 1962),
        )
        for entity in entities.values():
            self.assertFalse(entity["aliases"])
            Entity.from_dict(entity)

    def test_sources_parse_and_souk_ahras_has_independent_outcome_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_FLN_SOURCES), 11)
        for source in lane.WAVE8_FLN_SOURCES:
            Source.from_dict(source)
        contract = lane.WAVE8_FLN_CONTRACTS["hced-Souk-Ahras1958-1"]
        self.assertEqual(len(contract["outcome_source_ids"]), 3)
        self.assertEqual(len(contract["outcome_source_family_ids"]), 3)
        self.assertEqual(
            contract["outcome_source_family_ids"],
            sorted(set(contract["outcome_source_family_ids"])),
        )

    def test_only_souk_ahras_promotes_and_other_exact_rows_are_held(self) -> None:
        self.assertEqual(
            lane.WAVE8_FLN_CONTRACT_IDS,
            {"hced-Souk-Ahras1958-1"},
        )
        self.assertEqual(
            lane.WAVE8_FLN_HOLD_IDS,
            {
                "hced-Algiers1956-1957-1",
                "hced-Frontier1958-1",
                "hced-Kabylie1959-1",
            },
        )
        self.assertEqual(
            lane.WAVE8_FLN_RESERVED_IDS,
            set(lane.WAVE8_FLN_ROW_HASHES),
        )
        for hold in lane.WAVE8_FLN_HOLDS.values():
            self.assertEqual(hold["disposition"], "hold")
            self.assertEqual(hold["result_type"], "unknown")
            self.assertIs(hold["unknown_is_never_draw"], True)

    def test_hold_granularities_prevent_campaign_double_counting(self) -> None:
        expected = {
            "hced-Algiers1956-1957-1": (
                "multi_episode_urban_campaign_not_single_elo_event",
                "multi_phase_urban_counterinsurgency_campaign",
            ),
            "hced-Frontier1958-1": (
                "campaign_envelope_contains_promoted_souk_ahras_battle",
                "multi_month_border_campaign_envelope",
            ),
            "hced-Kabylie1959-1": (
                "multi_month_sweep_not_single_elo_event",
                "multi_month_counterinsurgency_sweep",
            ),
        }
        for candidate_id, (category, granularity) in expected.items():
            hold = lane.WAVE8_FLN_HOLDS[candidate_id]
            self.assertEqual(hold["hold_category"], category)
            self.assertEqual(hold["reviewed_granularity"], granularity)
            self.assertTrue(hold["evidence_refs"])
        self.assertIn(
            "Souk Ahras",
            lane.WAVE8_FLN_HOLDS["hced-Frontier1958-1"]["hold_reason"],
        )

    def test_souk_ahras_tactical_result_and_actors_are_locked(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["hced_candidate_id"], "hced-Souk-Ahras1958-1")
        self.assertEqual(event["name"], "Battle of Souk Ahras")
        self.assertEqual((event["year"], event["end_year"]), (1958, 1958))
        self.assertEqual(event["date_precision"], "day_range")
        self.assertEqual(event["confidence"], 0.96)
        self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
        outcomes = {
            participant["entity_id"]: participant["termination"]
            for participant in event["participants"]
        }
        self.assertEqual(
            outcomes,
            {
                FOURTH_REPUBLIC: "engagement_victory",
                ALN: "engagement_defeat",
            },
        )
        contract = lane.WAVE8_FLN_CONTRACTS["hced-Souk-Ahras1958-1"]
        self.assertFalse(contract["source_outcome_override"])
        self.assertFalse(contract["outcome_reversal"])
        Event.from_dict(event)

    def test_souk_ahras_point_is_withheld_and_country_is_retained(self) -> None:
        event = self._events()[0]
        self.assertNotIn("geometry", event)
        self.assertEqual(event["modern_location_country"], "Algeria")
        self.assertIn("location_provenance", event)
        self.assertEqual(
            lane.WAVE8_FLN_POINT_QUARANTINE_ADDITIONS,
            {"hced-Souk-Ahras1958-1"},
        )
        self.assertFalse(lane.WAVE8_FLN_COUNTRY_QUARANTINE_ADDITIONS)

    def test_no_probable_cross_source_souk_ahras_twin_exists(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_fln_integration_dispositions(
                self.hced, self.iwbd, existing
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_current_release_activates_both_curated_identities(self) -> None:
        events = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_FLN_CONTRACT_IDS
        ]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["name"], "Battle of Souk Ahras")
        self.assertNotIn("geometry", events[0])
        self.assertEqual(events[0]["modern_location_country"], "Algeria")

        release_entities = {
            str(item["id"]): item for item in self.release_entities
        }
        registry_entities = {
            str(item["id"]): item for item in self.registry["entities"]
        }
        for entity_id in (FOURTH_REPUBLIC, ALN):
            self.assertIn(entity_id, release_entities)
            self.assertFalse(release_entities[entity_id]["aliases"])
            self.assertEqual(registry_entities[entity_id]["status"], "rated")
            self.assertEqual(
                registry_entities[entity_id]["identity_status"],
                "curated",
            )

        source_ids = {str(item["id"]) for item in self.release_sources}
        self.assertLessEqual(
            {str(item["id"]) for item in lane.WAVE8_FLN_SOURCES},
            source_ids,
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_fln_hced_events"], 1)
        self.assertEqual(
            promotion["wave8_fln_candidate_ids"],
            ["hced-Souk-Ahras1958-1"],
        )
        self.assertEqual(len(promotion["wave8_fln_holds"]), 3)
        self.assertEqual(
            self.registry["coverage"]["candidate_keyed_wave8_fln_hced_events"],
            1,
        )

    def test_release_and_registry_counts_include_the_exact_fln_delta(self) -> None:
        self.assertEqual(len(self.release_entities), 995)
        self.assertEqual(len(self.release_events), 5_338)
        self.assertEqual(len(self.registry["entities"]), 2_345)
        self.assertEqual(
            self.registry["coverage"]["unresolved_event_candidates"],
            18_056,
        )
        location = self.registry["coverage"]["hced_location_assertions"]
        self.assertEqual(
            location["hced_candidate_bindings"],
            5_074,
        )
        self.assertEqual(
            location["geojson_points"],
            4_734,
        )
        self.assertEqual(
            location["modern_location_country_assertions"],
            4_979,
        )

    def test_row_drift_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Souk-Ahras1958-1"
        )
        row["winner_raw"] = "FLN"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_fln_queue_contracts(tampered)

        entities, existing = self._installed()
        existing.append(
            {
                "id": "duplicate",
                "name": "Battle of Souk Ahras",
                "year": 1958,
                "participants": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_fln_contracts(self.hced, entities, existing)

    def test_source_and_entity_installers_are_idempotent_and_collision_safe(self) -> None:
        entities, _ = self._installed()
        before = {
            entity_id: copy.deepcopy(entities[entity_id])
            for entity_id in (FOURTH_REPUBLIC, ALN)
        }
        lane.install_wave8_fln_entities(entities)
        self.assertEqual(
            {entity_id: entities[entity_id] for entity_id in before},
            before,
        )
        entities[ALN]["name"] = "drift"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_fln_entities(entities)

        sources = {}
        lane.install_wave8_fln_sources(sources)
        lane.install_wave8_fln_sources(sources)
        self.assertEqual(len(sources), 11)
        sources["wave8_fln_connelly_souk_ahras"]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_fln_sources(sources)

    def test_signature_counts_and_cohorts_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_fln_audit_signature(),
            lane.WAVE8_FLN_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_fln_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 3,
                "new_entities": 2,
                "new_sources": 11,
                "newly_rated_events": 1,
                "outcome_overrides": 0,
                "point_quarantine_additions": 1,
                "promotion_contracts": 1,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_fln_cohort_counts(),
            {"algerian_war_fln_exact_label_1956_1959": 4},
        )


if __name__ == "__main__":
    unittest.main()
