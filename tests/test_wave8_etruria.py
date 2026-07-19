import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_etruria as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_exact import promote_exact_hced_contracts


ROOT = Path(__file__).resolve().parents[1]
VEII = "veii_city_state_reviewed_477_396_bce"
FABIAN_FORCE = "fabian_clan_client_force_cremera_477_bce"
CUMAE = "cumae_city_state_battle_474_bce"
ETRUSCAN_FLEET = "etruscan_maritime_force_cumae_474_bce"
LATIN_TARQUIN = "latin_tarquin_coalition_regillus_499_496_bce"
ROME = "roman_republic"
SYRACUSE = "syracuse_city_state"
EVENT_PREFIX = "hced_wave8_etruria_"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8EtruriaTests(unittest.TestCase):
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
        lane_entity_ids = {str(item["id"]) for item in lane.WAVE8_ETRURIA_ENTITIES}
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane.install_wave8_etruria_entities(entities)
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_ETRURIA_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_PREFIX)
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._installed()
        return lane.promote_wave8_etruria_contracts(self.hced, entities, existing)

    def _is_integrated(self) -> bool:
        return (
            "accepted_wave8_etruria_hced_events"
            in self.release_metadata.get("promotion", {})
        )

    def test_complete_label_inventory_and_raw_rows_are_pinned(self) -> None:
        relevant = {
            str(row["candidate_id"]): row
            for row in self.hced
            if any(
                normalize_label(row.get(key)) == "etruria"
                for key in ("side_1_raw", "side_2_raw")
            )
        }
        self.assertEqual(set(relevant), lane.WAVE8_ETRURIA_RESERVED_IDS)
        self.assertEqual(len(relevant), 4)
        for candidate_id, expected_hash in lane.WAVE8_ETRURIA_ROW_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(relevant[candidate_id]), expected_hash
                )

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_etruria_queue_contracts(self.hced),
            {
                "exact_label_rows": 4,
                "holds": 0,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
            },
        )
        if not self._is_integrated():
            self.assertEqual(
                lane.validate_wave8_etruria_funnel(self.funnel),
                {
                    "events_touched": 4,
                    "holds": 0,
                    "sole_blocker_events": 3,
                    "unresolved_side_attempts": 4,
                    "zero_time_valid_candidates": 4,
                },
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"]
                ["wave8_etruria_exact_label_funnel_audit"],
                lane.WAVE8_ETRURIA_FUNNEL_AUDIT,
            )

    def test_five_narrow_identities_open_no_generic_alias(self) -> None:
        entities = {str(item["id"]): item for item in lane.WAVE8_ETRURIA_ENTITIES}
        self.assertEqual(
            set(entities), {VEII, FABIAN_FORCE, CUMAE, ETRUSCAN_FLEET, LATIN_TARQUIN}
        )
        self.assertEqual(
            {
                entity_id: (item["start_year"], item["end_year"])
                for entity_id, item in entities.items()
            },
            {
                VEII: (-477, -396),
                FABIAN_FORCE: (-477, -477),
                CUMAE: (-474, -474),
                ETRUSCAN_FLEET: (-474, -474),
                LATIN_TARQUIN: (-499, -496),
            },
        )
        for entity in entities.values():
            self.assertEqual(entity["aliases"], [])
            self.assertNotEqual(normalize_label(entity["name"]), "etruria")
            Entity.from_dict(entity)

    def test_sources_parse_and_each_outcome_has_two_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_ETRURIA_SOURCES), 8)
        for source in lane.WAVE8_ETRURIA_SOURCES:
            Source.from_dict(source)
        for candidate_id, contract in lane.WAVE8_ETRURIA_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
                self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertLessEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )

    def test_four_events_have_reviewed_names_dates_and_granularities(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        self.assertEqual(set(events), lane.WAVE8_ETRURIA_CONTRACT_IDS)
        self.assertEqual(
            {
                candidate_id: (
                    event["name"],
                    event["year"],
                    event["end_year"],
                    event["date_precision"],
                    event["reviewed_granularity"],
                )
                for candidate_id, event in events.items()
            },
            {
                "hced-Cremera-477-1": (
                    "Battle of the Cremera",
                    -477,
                    -477,
                    "year",
                    "pitched_battle",
                ),
                "hced-Cumae-474-1": (
                    "Battle of Cumae",
                    -474,
                    -474,
                    "year",
                    "naval_battle",
                ),
                "hced-Lake Regillus-496-1": (
                    "Battle of Lake Regillus",
                    -499,
                    -496,
                    "range",
                    "pitched_battle",
                ),
                "hced-Veii-405-1": (
                    "Siege and capture of Veii",
                    -405,
                    -396,
                    "range",
                    "siege",
                ),
            },
        )
        for event in events.values():
            self.assertEqual(event["war_type"], "interstate_limited")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            Event.from_dict(event)

    def test_actor_bindings_are_exact_and_veii_is_reused(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}

        def outcomes(candidate_id):
            return {
                item["entity_id"]: item["termination"]
                for item in events[candidate_id]["participants"]
            }

        self.assertEqual(
            outcomes("hced-Cremera-477-1"),
            {VEII: "engagement_victory", FABIAN_FORCE: "engagement_defeat"},
        )
        self.assertEqual(
            outcomes("hced-Cumae-474-1"),
            {
                CUMAE: "engagement_victory",
                SYRACUSE: "engagement_victory",
                ETRUSCAN_FLEET: "engagement_defeat",
            },
        )
        self.assertEqual(
            outcomes("hced-Veii-405-1"),
            {ROME: "engagement_victory", VEII: "engagement_defeat"},
        )

    def test_regillus_is_an_explicit_low_confidence_sourced_reversal(self) -> None:
        contract = lane.WAVE8_ETRURIA_CONTRACTS["hced-Lake Regillus-496-1"]
        self.assertIs(contract["source_outcome_override"], True)
        self.assertIs(contract["outcome_reversal"], True)
        self.assertEqual(contract["winner_side"], 2)
        self.assertEqual(contract["confidence"], 0.70)
        self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
        event = {
            item["hced_candidate_id"]: item for item in self._events()
        }["hced-Lake Regillus-496-1"]
        self.assertEqual(
            {item["entity_id"]: item["termination"] for item in event["participants"]},
            {ROME: "engagement_victory", LATIN_TARQUIN: "engagement_defeat"},
        )
        self.assertIn("source-attested tradition", event["summary"])
        self.assertIn("not archaeological certainty", event["summary"])

    def test_veii_massacre_marker_is_not_a_second_outcome(self) -> None:
        event = {
            item["hced_candidate_id"]: item for item in self._events()
        }["hced-Veii-405-1"]
        self.assertIn("unscored aftermath", event["summary"])
        self.assertNotIn("massacre", event)
        self.assertEqual(len(event["participants"]), 2)

    def test_two_date_overrides_are_closed_and_fail_without_sources(self) -> None:
        self.assertEqual(
            {
                candidate_id
                for candidate_id, contract in lane.WAVE8_ETRURIA_CONTRACTS.items()
                if contract["source_date_override"]
            },
            {"hced-Lake Regillus-496-1", "hced-Veii-405-1"},
        )
        contracts = copy.deepcopy(lane.WAVE8_ETRURIA_CONTRACTS)
        contracts["hced-Veii-405-1"]["date_source_ids"] = []
        entities, existing = self._installed()
        with self.assertRaisesRegex(ValueError, "date override lacks"):
            promote_exact_hced_contracts(
                self.hced,
                entities,
                existing,
                contracts,
                lane_name="Etruria date-override test",
                event_id_prefix="test_",
            )

    def test_all_points_are_withheld_but_italy_is_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_ETRURIA_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_ETRURIA_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_ETRURIA_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            set(lane.WAVE8_ETRURIA_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_ETRURIA_CONTRACT_IDS,
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Italy")
            self.assertIn("location_provenance", event)

    def test_no_probable_cross_source_twins(self) -> None:
        _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_etruria_integration_dispositions(
                self.hced, self.iwbd, existing
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_installers_are_idempotent_and_collision_safe(self) -> None:
        entities = {}
        lane.install_wave8_etruria_entities(entities)
        lane.install_wave8_etruria_entities(entities)
        self.assertEqual(len(entities), 5)
        entities[VEII]["name"] = "drift"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_etruria_entities(entities)

        sources = {}
        lane.install_wave8_etruria_sources(sources)
        lane.install_wave8_etruria_sources(sources)
        self.assertEqual(len(sources), 8)
        first_id = str(lane.WAVE8_ETRURIA_SOURCES[0]["id"])
        sources[first_id]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_etruria_sources(sources)

    def test_row_drift_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Lake Regillus-496-1"
        )
        row["winner_raw"] = "Rome"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_etruria_queue_contracts(tampered)

        entities, existing = self._installed()
        existing.append(
            {
                "id": "duplicate",
                "name": "Battle of Cumae",
                "year": -474,
                "participants": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_etruria_contracts(self.hced, entities, existing)

    def test_signature_counts_and_cohorts_are_pinned(self) -> None:
        self.assertNotEqual(lane.WAVE8_ETRURIA_FINAL_AUDIT_SIGNATURE, "__PENDING__")
        self.assertEqual(
            lane.wave8_etruria_audit_signature(),
            lane.WAVE8_ETRURIA_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_etruria_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 0,
                "new_entities": 5,
                "new_sources": 8,
                "newly_rated_events": 4,
                "outcome_overrides": 1,
                "outcome_reversals": 1,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 4,
                "source_date_overrides": 2,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_etruria_cohort_counts(),
            {
                "early_roman_latin_war_regillus": 1,
                "syracusan_etruscan_war_cumae": 1,
                "third_veientine_war_siege": 1,
                "veientine_war_cremera": 1,
            },
        )

    def test_release_artifacts_are_preintegration_or_exactly_integrated(self) -> None:
        release_events = {
            str(row.get("hced_candidate_id")): row
            for row in self.release_events
            if row.get("hced_candidate_id") in lane.WAVE8_ETRURIA_RESERVED_IDS
        }
        if not self._is_integrated():
            self.assertFalse(release_events)
            return

        self.assertEqual(set(release_events), lane.WAVE8_ETRURIA_CONTRACT_IDS)
        release_entity_ids = {str(row["id"]) for row in self.release_entities}
        self.assertLessEqual(
            {VEII, FABIAN_FORCE, CUMAE, ETRUSCAN_FLEET, LATIN_TARQUIN},
            release_entity_ids,
        )
        release_source_ids = {str(row["id"]) for row in self.release_sources}
        self.assertLessEqual(
            {str(row["id"]) for row in lane.WAVE8_ETRURIA_SOURCES},
            release_source_ids,
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(promotion["accepted_wave8_etruria_hced_events"], 4)
        self.assertEqual(
            promotion["wave8_etruria_candidate_ids"],
            sorted(lane.WAVE8_ETRURIA_CONTRACT_IDS),
        )
        statuses = {
            row["id"]: row["status"]
            for row in self.registry["entities"]
            if row["id"] in {VEII, FABIAN_FORCE, CUMAE, ETRUSCAN_FLEET, LATIN_TARQUIN}
        }
        self.assertEqual(
            statuses,
            {
                VEII: "rated",
                FABIAN_FORCE: "rated",
                CUMAE: "rated",
                ETRUSCAN_FLEET: "rated",
                LATIN_TARQUIN: "rated",
            },
        )
        coverage = self.registry["coverage"]
        self.assertEqual(len(self.release_entities), 1_026)
        self.assertEqual(len(self.release_events), 5_419)
        self.assertEqual(len(self.registry["entities"]), 2_374)
        self.assertEqual(coverage["rated_entities"], 1_018)
        self.assertEqual(coverage["unresolved_event_candidates"], 36_929)
        location = coverage["hced_location_assertions"]
        self.assertEqual(location["hced_candidate_bindings"], 5_155)
        self.assertEqual(location["candidate_keyed_reviewed_contracts"], 787)
        self.assertEqual(location["geojson_points"], 4_798)
        self.assertEqual(location["modern_location_country_assertions"], 5_060)
        self.assertEqual(location["location_provenance_objects"], 5_109)
        self.assertEqual(location["point_fields_withheld_by_quarantine"], 357)
        self.assertEqual(location["unique_events_with_any_quarantined_field"], 405)


if __name__ == "__main__":
    unittest.main()
