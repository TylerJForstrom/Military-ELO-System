import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Event, Source
from military_elo.promotion import wave8_irish_civil_war as lane
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
NATIONAL_ARMY = "irish_national_army_1922_1923"
ANTI_TREATY = "anti_treaty_ira_1922_1923"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8IrishCivilWarTests(unittest.TestCase):
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

    def _existing(self):
        return [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(
                "hced_wave8_irish_civil_war_"
            )
        ]

    def _events(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        return lane.promote_wave8_irish_civil_war_contracts(
            self.hced,
            entities,
            self._existing(),
        )

    def _is_integrated(self) -> bool:
        return (
            "accepted_wave8_irish_civil_war_hced_events"
            in self.release_metadata.get("promotion", {})
        )

    def test_complete_war_inventory_and_target_hashes_are_pinned(self) -> None:
        civil_war_rows = {
            str(row["candidate_id"]): row
            for row in self.hced
            if "Irish Civil War" in row.get("war_names", [])
        }
        self.assertEqual(len(civil_war_rows), 10)
        self.assertEqual(
            set(lane.WAVE8_IRISH_CIVIL_WAR_ROW_HASHES),
            lane.WAVE8_IRISH_CIVIL_WAR_RESERVED_IDS,
        )
        for candidate_id, expected_hash in (
            lane.WAVE8_IRISH_CIVIL_WAR_ROW_HASHES.items()
        ):
            with self.subTest(candidate_id=candidate_id):
                row = civil_war_rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertEqual(
                    (row["year_low"], row["year_best"], row["year_high"]),
                    (1922, 1922, 1922),
                )
                self.assertEqual(row["winner_raw"], row["side_1_raw"])
                self.assertEqual(row["loser_raw"], row["side_2_raw"])
                self.assertIs(row["winner_loser_complete"], True)

    def test_queue_and_historical_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_irish_civil_war_queue_contracts(self.hced),
            {
                "complete_irish_civil_war_rows": 10,
                "holds": 2,
                "previously_owned_rows": 6,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
            },
        )
        labels = {str(row.get("label")) for row in self.funnel.get("labels", [])}
        if {"anti treaty ira", "irish republican rebels"} <= labels:
            self.assertEqual(
                lane.validate_wave8_irish_civil_war_funnel(self.funnel),
                {"events_touched": 4, "labels": 2, "sole_blocker_events": 4},
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"][
                    "wave8_irish_civil_war_exact_label_funnel_audit"
                ],
                lane.WAVE8_IRISH_CIVIL_WAR_FUNNEL_AUDIT,
            )

    def test_lane_reuses_exact_existing_identities_without_new_entity(self) -> None:
        self.assertFalse(lane.WAVE8_IRISH_CIVIL_WAR_ENTITIES)
        entities = {str(row["id"]): row for row in self.release_entities}
        self.assertEqual(
            (entities[NATIONAL_ARMY]["start_year"], entities[NATIONAL_ARMY]["end_year"]),
            (1922, 1923),
        )
        self.assertEqual(
            (entities[ANTI_TREATY]["start_year"], entities[ANTI_TREATY]["end_year"]),
            (1922, 1923),
        )
        self.assertFalse(entities[NATIONAL_ARMY]["aliases"])
        self.assertFalse(entities[ANTI_TREATY]["aliases"])

    def test_sources_parse_and_promotions_use_two_independent_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_IRISH_CIVIL_WAR_SOURCES), 5)
        for source in lane.WAVE8_IRISH_CIVIL_WAR_SOURCES:
            Source.from_dict(source)
        for candidate_id, contract in (
            lane.WAVE8_IRISH_CIVIL_WAR_CONTRACTS.items()
        ):
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(len(contract["outcome_source_ids"]), 2)
                self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertFalse(contract["source_outcome_override"])
                self.assertFalse(contract["outcome_reversal"])

    def test_only_limerick_and_waterford_promote(self) -> None:
        self.assertEqual(
            lane.WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS,
            {"hced-Limerick1922-1", "hced-Waterford1922-1"},
        )
        self.assertEqual(
            lane.WAVE8_IRISH_CIVIL_WAR_HOLD_IDS,
            {"hced-Beal na mBlath1922-1", "hced-Tipperary1922-1"},
        )
        events = self._events()
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            lane.WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS,
        )

    def test_holds_never_invent_reverse_or_draw_outcomes(self) -> None:
        beal = lane.WAVE8_IRISH_CIVIL_WAR_HOLDS[
            "hced-Beal na mBlath1922-1"
        ]
        self.assertEqual(beal["hold_category"], "source_outcome_not_defensible")
        self.assertEqual(beal["result_type"], "unknown")
        self.assertIs(beal["unknown_is_never_draw"], True)
        self.assertIn("does not establish a complete opposite", beal["hold_reason"])

        tipperary = lane.WAVE8_IRISH_CIVIL_WAR_HOLDS[
            "hced-Tipperary1922-1"
        ]
        self.assertEqual(
            tipperary["hold_category"], "non_discrete_campaign_umbrella"
        )
        self.assertEqual(tipperary["result_type"], "unknown")
        self.assertIs(tipperary["unknown_is_never_draw"], True)
        self.assertIn("Clonmel", tipperary["hold_reason"])
        self.assertIn("Kilmallock", tipperary["hold_reason"])

    def test_promoted_events_lock_actors_dates_and_tactical_results(self) -> None:
        events = {event["hced_candidate_id"]: event for event in self._events()}
        self.assertEqual(events["hced-Limerick1922-1"]["name"], "Battle of Limerick")
        self.assertEqual(
            events["hced-Waterford1922-1"]["name"], "Battle of Waterford"
        )
        for event in events.values():
            self.assertEqual((event["year"], event["end_year"]), (1922, 1922))
            self.assertEqual(event["date_precision"], "year")
            self.assertEqual(event["reviewed_granularity"], "urban_battle")
            self.assertEqual(event["war_type"], "civil_war")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            terminations = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(
                terminations,
                {
                    NATIONAL_ARMY: "engagement_victory",
                    ANTI_TREATY: "engagement_defeat",
                },
            )
            Event.from_dict(event)

    def test_unreviewed_city_centroids_are_withheld_but_country_remains(self) -> None:
        self.assertEqual(
            lane.WAVE8_IRISH_CIVIL_WAR_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_IRISH_CIVIL_WAR_COUNTRY_QUARANTINE_ADDITIONS)
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Ireland")
            self.assertIn("location_provenance", event)

    def test_no_probable_cross_source_twins_and_prior_owners_are_intact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_irish_civil_war_integration_dispositions(
                self.hced,
                self.iwbd,
                self._existing(),
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
                "previously_owned_irish_events": 6,
            },
        )

    def test_source_installer_is_idempotent_and_collision_safe(self) -> None:
        sources = {}
        lane.install_wave8_irish_civil_war_sources(sources)
        lane.install_wave8_irish_civil_war_sources(sources)
        self.assertEqual(len(sources), 5)
        source_id = str(lane.WAVE8_IRISH_CIVIL_WAR_SOURCES[0]["id"])
        sources[source_id]["title"] = "drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_irish_civil_war_sources(sources)

    def test_row_drift_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Limerick1922-1"
        )
        row["winner_raw"] = "Anti Treaty IRA"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            lane.validate_wave8_irish_civil_war_queue_contracts(tampered)

        entities = {str(item["id"]): item for item in self.release_entities}
        existing = self._existing()
        existing.append(
            {
                "id": "duplicate",
                "name": "Battle of Limerick",
                "year": 1922,
                "participants": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_irish_civil_war_contracts(
                self.hced,
                entities,
                existing,
            )

    def test_signature_counts_and_cohort_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_irish_civil_war_audit_signature(),
            lane.WAVE8_IRISH_CIVIL_WAR_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_irish_civil_war_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 2,
                "new_entities": 0,
                "new_sources": 5,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_irish_civil_war_cohort_counts(),
            {"irish_civil_war_remaining_rows_1922": 4},
        )

    def test_release_artifacts_are_preintegration_or_exactly_integrated(self) -> None:
        release_events = {
            str(row.get("hced_candidate_id")): row
            for row in self.release_events
            if row.get("hced_candidate_id")
            in lane.WAVE8_IRISH_CIVIL_WAR_RESERVED_IDS
        }
        if not self._is_integrated():
            self.assertFalse(release_events)
            return

        self.assertEqual(set(release_events), lane.WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS)
        source_ids = {str(row["id"]) for row in self.release_sources}
        self.assertLessEqual(
            {str(row["id"]) for row in lane.WAVE8_IRISH_CIVIL_WAR_SOURCES},
            source_ids,
        )
        promotion = self.release_metadata["promotion"]
        self.assertEqual(
            promotion["accepted_wave8_irish_civil_war_hced_events"], 2
        )
        self.assertEqual(
            promotion["wave8_irish_civil_war_candidate_ids"],
            sorted(lane.WAVE8_IRISH_CIVIL_WAR_CONTRACT_IDS),
        )
        self.assertEqual(len(promotion["wave8_irish_civil_war_holds"]), 2)
        coverage = self.registry["coverage"]
        self.assertEqual(len(self.release_entities), 1_115)
        self.assertEqual(len(self.release_events), 5_546)
        self.assertEqual(len(self.registry["entities"]), 2_454)
        self.assertEqual(coverage["unresolved_event_candidates"], 36_797)
        location = coverage["hced_location_assertions"]
        self.assertEqual(location["hced_candidate_bindings"], 5_279)
        self.assertEqual(location["geojson_points"], 4_848)
        self.assertEqual(location["modern_location_country_assertions"], 5_181)


if __name__ == "__main__":
    unittest.main()
