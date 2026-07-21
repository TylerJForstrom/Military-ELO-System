import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_latrun as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_latrun_"
ARAB_LEGION = "arab_legion_transjordan"
ISRAEL = "clio_q801_1948_5abea45e"

EXPECTED_HASHES = {
    "hced-Latrun (1st)1948-1": (
        "a9ea4fe32e2faaf06dc72487af6cc6670ed8cca1090ca978617d9249bca61b2d"
    ),
    "hced-Latrun (2nd)1948-1": (
        "c604369305d9de0d631fca49d4d0fa85adaa08725b4b119d606ab1e910ae97e0"
    ),
}

EXPECTED_ADJACENT_HCED = {
    "hced-Lydda-Ramleh1948-1",
    "hced-Palmyra1941-1",
}

EXPECTED_IWBD_DUPLICATES = {
    "iwbd-148-55-1386": "hced-Latrun (1st)1948-1",
    "iwbd-148-55-1388": "hced-Latrun (2nd)1948-1",
}

EXPECTED_IWBD_ADJACENT = {
    "iwbd-148-55-1390",
    "iwbd-148-55-1395",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class Wave8LatrunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")

    def _installed(self):
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
        }
        source_ids = {str(source["id"]) for source in lane.WAVE8_LATRUN_SOURCES}
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_LATRUN_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        before_entities = copy.deepcopy(entities)
        lane.install_wave8_latrun_entities(entities)
        self.assertEqual(entities, before_entities)
        lane.install_wave8_latrun_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_latrun_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_and_locked_row_fingerprints(self) -> None:
        exact = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "arab legion"
            or normalize_label(row.get("side_2_raw")) == "arab legion"
        ]
        by_id = {str(row["candidate_id"]): row for row in exact}
        self.assertEqual(set(by_id), set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_LATRUN_ROW_HASHES, EXPECTED_HASHES)
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertEqual(
                    (
                        row["side_1_raw"],
                        row["side_2_raw"],
                        row["winner_raw"],
                        row["loser_raw"],
                    ),
                    ("Arab Legion", "Israel", "Arab Legion", "Israel"),
                )
                self.assertEqual(
                    (row["year_low"], row["year_best"], row["year_high"]),
                    (1948, 1948, 1948),
                )
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_and_funnel_accounting_are_exact(self) -> None:
        self.assertEqual(
            lane.validate_wave8_latrun_queue_contracts(self.hced_rows),
            {
                "adjacent_hced_rows": 2,
                "exact_label_rows": 2,
                "holds": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
            },
        )
        labels = {str(row.get("label")) for row in self.funnel.get("labels", [])}
        if "arab legion" in labels:
            self.assertEqual(
                lane.validate_wave8_latrun_funnel(self.funnel),
                {
                    "events_touched": 2,
                    "sole_blocker_events": 2,
                    "unresolved_side_attempts": 2,
                    "zero_time_valid_candidates": 2,
                },
            )
        else:
            self.assertEqual(
                self.release_metadata["promotion"][
                    "wave8_latrun_exact_label_funnel_audit"
                ],
                lane.WAVE8_LATRUN_FUNNEL_AUDIT,
            )

    def test_only_two_rows_promote_with_no_holds_or_new_identity(self) -> None:
        self.assertEqual(lane.WAVE8_LATRUN_CONTRACT_IDS, set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_LATRUN_RESERVED_IDS, set(EXPECTED_HASHES))
        self.assertFalse(lane.WAVE8_LATRUN_HOLDS)
        self.assertFalse(lane.WAVE8_LATRUN_ENTITIES)
        for contract in lane.WAVE8_LATRUN_CONTRACTS.values():
            self.assertEqual(contract["disposition"], "promote")
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertNotIn("draw", contract["audit_note"].casefold())

    def test_exact_dates_names_and_single_assault_granularity_are_pinned(self) -> None:
        expected = {
            "hced-Latrun (1st)1948-1": (
                "First Battle of Latrun (Operation Bin Nun Alef)",
                "24-25 May 1948",
                "1948-05-24",
                "1948-05-25",
            ),
            "hced-Latrun (2nd)1948-1": (
                "Second Battle of Latrun (Operation Bin Nun Bet)",
                "30-31 May 1948",
                "1948-05-30",
                "1948-05-31",
            ),
        }
        for candidate_id, values in expected.items():
            canonical = lane.WAVE8_LATRUN_CONTRACTS[candidate_id]["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["date_text"],
                    canonical["start_date"],
                    canonical["end_date"],
                ),
                values,
            )
            self.assertEqual(canonical["date_precision"], "day_range")
            self.assertEqual(canonical["granularity"], "single_assault_engagement")

    def test_two_authoritative_source_families_and_event_roles_per_battle(self) -> None:
        sources = {str(source["id"]): source for source in lane.WAVE8_LATRUN_SOURCES}
        self.assertEqual(
            {source["url"] for source in sources.values()},
            {
                "https://bura.brunel.ac.uk/handle/2438/16047",
                "https://www.jstor.org/stable/j.ctv333ktt8.7",
            },
        )
        self.assertEqual(len(sources), 2)
        for source in sources.values():
            Source.from_dict(source)
            self.assertIn("outcome", source["evidence_roles"])
        for contract in lane.WAVE8_LATRUN_CONTRACTS.values():
            self.assertEqual(set(contract["outcome_source_ids"]), set(sources))
            self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(set(contract["event_evidence_roles"]), set(sources))
            self.assertIn(
                "tactical_outcome",
                contract["event_evidence_roles"][
                    "wave8_latrun_rodman_battle_chapter"
                ],
            )
            self.assertIn(
                "independent_tactical_outcome_crosscheck",
                contract["event_evidence_roles"][
                    "wave8_latrun_hughes_conduct_operations"
                ],
            )

    def test_existing_exact_identities_are_reused_without_lane_aliases(self) -> None:
        entities = {str(entity["id"]): entity for entity in self.release_entities}
        self.assertEqual(entities[ARAB_LEGION]["name"], "Arab Legion of Transjordan")
        self.assertEqual(
            (entities[ARAB_LEGION]["start_year"], entities[ARAB_LEGION]["end_year"]),
            (1923, 1956),
        )
        self.assertEqual(entities[ARAB_LEGION]["aliases"], [])
        self.assertEqual(entities[ISRAEL]["name"], "State of Israel")
        self.assertLessEqual(entities[ISRAEL]["start_year"], 1948)
        self.assertGreaterEqual(entities[ISRAEL]["end_year"], 1948)
        Entity.from_dict(entities[ARAB_LEGION])
        Entity.from_dict(entities[ISRAEL])
        self.assertFalse(lane.WAVE8_LATRUN_ENTITIES)

    def test_emitted_events_preserve_tactical_outcome_and_exact_participants(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(set(events), set(EXPECTED_HASHES))
        for candidate_id, event in events.items():
            outcomes = {
                participant["entity_id"]: participant["termination"]
                for participant in event["participants"]
            }
            self.assertEqual(
                outcomes,
                {
                    ARAB_LEGION: "engagement_victory",
                    ISRAEL: "engagement_defeat",
                },
            )
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["scale"], "battle")
            self.assertEqual(event["date_precision"], "day_range")
            self.assertEqual(
                event["reviewed_granularity"],
                "single_assault_engagement",
            )
            self.assertEqual(
                set(event["outcome_source_ids"]),
                {str(source["id"]) for source in lane.WAVE8_LATRUN_SOURCES},
            )
            self.assertIn("hced_dataset", event["source_ids"])
            self.assertEqual(event["confidence"], 0.96)
            Event.from_dict(event)

    def test_promoted_points_are_withheld_but_country_and_provenance_remain(self) -> None:
        self.assertEqual(
            lane.WAVE8_LATRUN_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_LATRUN_CONTRACT_IDS,
        )
        self.assertFalse(lane.WAVE8_LATRUN_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            set(lane.WAVE8_LATRUN_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_LATRUN_CONTRACT_IDS,
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Israel")
            self.assertIn("location_provenance", event)
            reason = lane.WAVE8_LATRUN_LOCATION_QUARANTINE_REASONS[
                event["hced_candidate_id"]
            ]
            self.assertEqual(reason["actions"], ["withhold_point"])
            self.assertEqual(
                set(reason["evidence_refs"]),
                set(event["outcome_source_ids"]),
            )

    def test_adjacent_hced_rows_are_fingerprinted_and_not_reserved(self) -> None:
        dispositions = lane.WAVE8_LATRUN_ADJACENT_HCED_DISPOSITIONS
        self.assertEqual(set(dispositions), EXPECTED_ADJACENT_HCED)
        self.assertFalse(set(dispositions) & lane.WAVE8_LATRUN_RESERVED_IDS)
        by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        for candidate_id, disposition in dispositions.items():
            self.assertEqual(
                canonical_hced_row_sha256(by_id[candidate_id]),
                disposition["raw_row_sha256"],
            )
        self.assertEqual(
            dispositions["hced-Palmyra1941-1"]["owner_module"],
            "military_elo.promotion.wave7_root",
        )
        self.assertIn(
            "place_mention",
            dispositions["hced-Lydda-Ramleh1948-1"]["relationship"],
        )

    def test_iwbd_twins_and_later_attacks_have_exact_dispositions(self) -> None:
        duplicate_dispositions = lane.WAVE8_LATRUN_IWBD_DUPLICATE_DISPOSITIONS
        adjacent_dispositions = lane.WAVE8_LATRUN_IWBD_ADJACENT_DISPOSITIONS
        self.assertEqual(
            {
                candidate_id: disposition["hced_candidate_id"]
                for candidate_id, disposition in duplicate_dispositions.items()
            },
            EXPECTED_IWBD_DUPLICATES,
        )
        self.assertEqual(set(adjacent_dispositions), EXPECTED_IWBD_ADJACENT)
        self.assertEqual(
            duplicate_dispositions["iwbd-148-55-1386"]["fingerprint"][
                "start_date"
            ],
            "1948-05-25",
        )
        self.assertEqual(
            duplicate_dispositions["iwbd-148-55-1388"]["fingerprint"][
                "start_date"
            ],
            "1948-05-30",
        )
        self.assertEqual(
            adjacent_dispositions["iwbd-148-55-1390"]["fingerprint"][
                "start_date"
            ],
            "1948-06-09",
        )
        self.assertEqual(
            (
                adjacent_dispositions["iwbd-148-55-1395"]["fingerprint"][
                    "start_date"
                ],
                adjacent_dispositions["iwbd-148-55-1395"]["fingerprint"][
                    "end_date"
                ],
            ),
            ("1948-07-14", "1948-07-18"),
        )
        self.assertEqual(
            lane.validate_wave8_latrun_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "adjacent_hced_dispositions": 2,
                "existing_release_owned_events": len(
                    [
                        event
                        for event in self.release_events
                        if event.get("hced_candidate_id")
                        in lane.WAVE8_LATRUN_CONTRACT_IDS
                    ]
                ),
                "existing_release_probable_twins": 0,
                "iwbd_adjacent_dispositions": 2,
                "iwbd_duplicate_dispositions": 2,
                "iwbd_latrun_rows": 4,
            },
        )

    def test_future_adjacent_rows_and_cross_source_twins_fail_closed(self) -> None:
        future_hced = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-latrun",
                "name": "Latrun future row",
                "side_1_raw": "Unrelated A",
                "side_2_raw": "Unrelated B",
                "participants_raw": [],
            },
        ]
        with self.assertRaisesRegex(ValueError, "adjacent HCED inventory changed"):
            lane.validate_wave8_latrun_queue_contracts(future_hced)

        future_iwbd = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-latrun",
                "name": "Latrun future attack",
            },
        ]
        with self.assertRaisesRegex(ValueError, "IWBD Latrun inventory changed"):
            lane.validate_wave8_latrun_integration_dispositions(
                self.hced_rows,
                future_iwbd,
                self.release_events,
            )

        future_release = [
            *copy.deepcopy(self.release_events),
            {
                "id": "future_first_latrun_twin",
                "name": "First Battle of Latrun",
                "year": 1948,
                "aliases": [],
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_latrun_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                future_release,
            )

    def test_queue_iwbd_and_release_drift_guards_reject_tampering(self) -> None:
        tampered_hced = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered_hced
            if item.get("candidate_id") == "hced-Latrun (1st)1948-1"
        )
        row["winner_raw"] = "Israel"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_latrun_queue_contracts(tampered_hced)

        tampered_iwbd = copy.deepcopy(self.iwbd_rows)
        row = next(
            item
            for item in tampered_iwbd
            if item.get("candidate_id") == "iwbd-148-55-1388"
        )
        row["winner_raw"] = "Israel"
        with self.assertRaisesRegex(ValueError, "IWBD fingerprint changed"):
            lane.validate_wave8_latrun_integration_dispositions(
                self.hced_rows,
                tampered_iwbd,
                self.release_events,
            )

        partial_release = [
            self._events()[0],
            *copy.deepcopy(self.release_events),
        ]
        with self.assertRaisesRegex(ValueError, "ownership is partial"):
            lane.validate_wave8_latrun_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                partial_release,
            )

    def test_promoter_rejects_missing_identity_and_duplicate_ownership(self) -> None:
        entities, _, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(ARAB_LEGION)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_latrun_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        events = lane.promote_wave8_latrun_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_latrun_contracts(
                self.hced_rows,
                entities,
                [*existing, *events],
            )
        duplicate_name = {
            "id": "future_duplicate_name",
            "name": events[0]["name"],
            "year": 1948,
        }
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_latrun_contracts(
                self.hced_rows,
                entities,
                [*existing, duplicate_name],
            )

    def test_source_installer_is_idempotent_and_collision_safe(self) -> None:
        _, sources, _ = self._installed()
        once = copy.deepcopy(sources)
        lane.install_wave8_latrun_sources(sources)
        self.assertEqual(sources, once)
        for source in lane.WAVE8_LATRUN_SOURCES:
            self.assertIn(str(source["id"]), sources)
            Source.from_dict(sources[str(source["id"])])

        source_id = str(lane.WAVE8_LATRUN_SOURCES[0]["id"])
        collision = copy.deepcopy(sources)
        collision[source_id]["title"] = "tampered"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_latrun_sources(collision)

    def test_current_release_and_source_artifacts_are_all_or_none(self) -> None:
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_LATRUN_SOURCES
        }
        base_events = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_LATRUN_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        base_sources = [
            copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        ]
        self.assertEqual(
            lane.validate_wave8_latrun_current_release(
                base_events,
                self.release_entities,
                base_sources,
            ),
            {
                "artifact_state": "absent",
                "installed_sources": 0,
                "promoted_events": 0,
            },
        )

        events = self._events()
        integrated_sources = [
            *base_sources,
            *copy.deepcopy(lane.WAVE8_LATRUN_SOURCES),
        ]
        self.assertEqual(
            lane.validate_wave8_latrun_current_release(
                [*base_events, *events],
                self.release_entities,
                integrated_sources,
            ),
            {
                "artifact_state": "integrated",
                "installed_sources": 2,
                "promoted_events": 2,
            },
        )

        with self.assertRaisesRegex(ValueError, "event inventory is partial"):
            lane.validate_wave8_latrun_current_release(
                [*base_events, events[0]],
                self.release_entities,
                integrated_sources,
            )
        with self.assertRaisesRegex(ValueError, "source inventory is partial"):
            lane.validate_wave8_latrun_current_release(
                base_events,
                self.release_entities,
                [*base_sources, lane.WAVE8_LATRUN_SOURCES[0]],
            )
        with self.assertRaisesRegex(ValueError, "artifacts are out of sync"):
            lane.validate_wave8_latrun_current_release(
                [*base_events, *events],
                self.release_entities,
                base_sources,
            )

    def test_counts_metadata_and_final_signature_are_deterministic(self) -> None:
        self.assertEqual(
            lane.wave8_latrun_counts(),
            {
                "adjacent_hced_dispositions": 2,
                "country_quarantine_additions": 0,
                "holds": 0,
                "integration_dispositions": 6,
                "iwbd_adjacent_dispositions": 2,
                "iwbd_duplicate_dispositions": 2,
                "new_entities": 0,
                "new_sources": 2,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_latrun_cohort_counts(),
            {"latrun_arab_legion_defensive_battles_may_1948": 2},
        )
        self.assertEqual(
            lane.wave8_latrun_audit_signature(),
            "88f181f06f5c45792a077befae74a160fa20bfa88a99c443e13fcad3ab6145ea",
        )
        self.assertEqual(
            lane.wave8_latrun_audit_signature(),
            lane.WAVE8_LATRUN_FINAL_AUDIT_SIGNATURE,
        )
        metadata = lane.wave8_latrun_metadata()
        self.assertEqual(metadata["hold_candidate_ids"], [])
        self.assertEqual(
            metadata["promoted_candidate_ids"],
            sorted(EXPECTED_HASHES),
        )


if __name__ == "__main__":
    unittest.main()
