import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_oran as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.policy import HCED_LABEL_POLICIES
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_oran_"
REGENCY = "dey_regency_of_algiers_1671_1830"
SPAIN = "spanish_empire"
MODERN_ALGERIA = "clio_q262_1963_de9ecdb4"

EXPECTED_HASHES = {
    "hced-Oran1704-1708-1": (
        "d2fc14ed22d8f4b534390e86df260140367e14ce13f503641352e5a10df83943"
    ),
    "hced-Oran1732-1": (
        "bc69deee0b2fe1c147708b834abd890123946effca5e953de3119aeb2b3216ad"
    ),
    "hced-Oran1780-1": (
        "4f2e74e9204c0033a11ec59ec3cd0e0279ead3e2e6ad000a8d623bbb87e6599d"
    ),
}
TINDOUF_HASH = "730d960692022b84aaf31fbe15e1fdfcacd93b3a1fd4c0dfbdc4de4dd746b108"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _historical_funnel():
    projection = copy.deepcopy(lane.WAVE8_ORAN_FUNNEL_AUDIT)
    wrong_interval = projection.pop("one_wrong_interval_candidate")
    projection["failure_cases"] = {
        "one_wrong_interval_candidate": wrong_interval,
    }
    return {"labels": [projection]}


class Wave8OranTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_metadata = _json(ROOT / "data/release/metadata.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.registry = _json(ROOT / "data/catalog/registry.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "algeria"
            or normalize_label(row.get("side_2_raw")) == "algeria"
        ]

    def _installed(self):
        entities = {
            str(item["id"]): copy.deepcopy(item) for item in self.release_entities
        }
        lane_source_ids = {str(item["id"]) for item in lane.WAVE8_ORAN_SOURCES}
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_ORAN_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        entities_before = copy.deepcopy(entities)
        lane.install_wave8_oran_entities(entities)
        self.assertEqual(entities, entities_before)
        lane.install_wave8_oran_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_oran_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_dispositions_and_row_hashes_are_pinned(self):
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        expected_ids = set(EXPECTED_HASHES) | {"hced-Tindouf1963-1"}
        self.assertEqual(set(by_id), expected_ids)
        self.assertEqual(lane.WAVE8_ORAN_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            lane.WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS[
                "hced-Tindouf1963-1"
            ]["raw_row_sha256"],
            TINDOUF_HASH,
        )
        for candidate_id, row in by_id.items():
            with self.subTest(candidate_id=candidate_id):
                expected = EXPECTED_HASHES.get(candidate_id, TINDOUF_HASH)
                self.assertEqual(canonical_hced_row_sha256(row), expected)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")
        self.assertEqual(
            lane.validate_wave8_oran_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 4,
                "holds": 1,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 3,
            },
        )

    def test_historical_funnel_projection_is_pinned_and_live_label_is_absent(self):
        self.assertEqual(
            lane.validate_wave8_oran_funnel(_historical_funnel()),
            {
                "events_touched": 3,
                "one_wrong_interval_candidate": 3,
                "sole_blocker_events": 3,
            },
        )
        live = [
            row
            for row in self.funnel.get("labels", [])
            if row.get("label") == "algeria"
        ]
        promotion = self.release_metadata.get("promotion", {})
        if "accepted_wave8_oran_hced_events" in promotion:
            self.assertFalse(
                live,
                "the integrated Oran lane must remove algeria from the live funnel",
            )
        else:
            self.assertEqual(
                lane.validate_wave8_oran_funnel(self.funnel),
                {
                    "events_touched": 3,
                    "one_wrong_interval_candidate": 3,
                    "sole_blocker_events": 3,
                },
            )

    def test_partition_has_two_wins_one_hold_and_one_existing_disposition(self):
        self.assertEqual(
            lane.WAVE8_ORAN_CONTRACT_IDS,
            {"hced-Oran1704-1708-1", "hced-Oran1732-1"},
        )
        self.assertEqual(
            lane.WAVE8_ORAN_RESERVED_IDS,
            set(EXPECTED_HASHES),
        )
        self.assertEqual(set(lane.WAVE8_ORAN_HOLDS), {"hced-Oran1780-1"})
        self.assertEqual(
            set(lane.WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS),
            {"hced-Tindouf1963-1"},
        )
        self.assertFalse(
            lane.WAVE8_ORAN_CONTRACT_IDS & set(lane.WAVE8_ORAN_HOLDS)
        )

    def test_unknown_1780_outcome_is_held_and_never_converted_to_a_draw(self):
        hold = lane.WAVE8_ORAN_HOLDS["hced-Oran1780-1"]
        self.assertEqual(hold["disposition"], "hold")
        self.assertEqual(
            hold["hold_category"],
            "insufficient_outcome_documentation",
        )
        self.assertIn("Unknown is not a draw", hold["hold_reason"])
        self.assertTrue(
            all(contract["result_type"] == "win" for contract in lane.WAVE8_ORAN_CONTRACTS.values())
        )
        events = self._events()
        self.assertNotIn(
            "hced-Oran1780-1",
            {event["hced_candidate_id"] for event in events},
        )
        self.assertFalse(
            any(
                "inconclusive" in participant["termination"]
                for event in events
                for participant in event["participants"]
            )
        )

    def test_sources_parse_and_each_promoted_outcome_has_independent_families(self):
        self.assertEqual(len(lane.WAVE8_ORAN_SOURCES), 4)
        for source in lane.WAVE8_ORAN_SOURCES:
            Source.from_dict(source)
        outcome_source_ids = {
            source_id
            for contract in lane.WAVE8_ORAN_CONTRACTS.values()
            for source_id in contract["outcome_source_ids"]
        }
        self.assertEqual(
            outcome_source_ids,
            {
                "wave8_oran_clodfelter_warfare",
                "wave8_oran_jaques_dictionary",
                "wave8_oran_rah_dbe_montemar",
            },
        )
        self.assertEqual(
            {str(source["id"]) for source in lane.WAVE8_ORAN_SOURCES}
            - outcome_source_ids,
            {"wave8_oran_wikipedia_spanish_algerian_war"},
        )
        self.assertNotIn(
            "wave8_oran_wikipedia_spanish_algerian_war",
            outcome_source_ids,
        )
        for candidate_id, contract in lane.WAVE8_ORAN_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertEqual(
                    contract["outcome_source_family_ids"],
                    sorted(set(contract["outcome_source_family_ids"])),
                )
                self.assertEqual(
                    set(contract["outcome_source_ids"]),
                    set(contract["evidence_refs"]),
                )
        override = lane.WAVE8_ORAN_CONTRACTS["hced-Oran1704-1708-1"]
        self.assertIs(override["source_date_override"], True)
        self.assertEqual(
            override["date_source_ids"],
            [
                "wave8_oran_jaques_dictionary",
                "wave8_oran_rah_dbe_montemar",
            ],
        )
        self.assertLessEqual(
            set(override["date_source_ids"]),
            set(override["evidence_refs"]),
        )

    def test_existing_identity_windows_are_unchanged_and_no_algeria_policy_opens(self):
        self.assertFalse(lane.WAVE8_ORAN_ENTITIES)
        self.assertNotIn("algeria", HCED_LABEL_POLICIES)
        entities = {str(item["id"]): item for item in self.release_entities}
        self.assertEqual(
            (entities[REGENCY]["start_year"], entities[REGENCY]["end_year"]),
            (1671, 1830),
        )
        self.assertEqual(entities[REGENCY]["aliases"], [])
        self.assertEqual(
            (entities[SPAIN]["start_year"], entities[SPAIN]["end_year"]),
            (1479, 1898),
        )
        self.assertEqual(
            (
                entities[MODERN_ALGERIA]["start_year"],
                entities[MODERN_ALGERIA]["end_year"],
            ),
            (1963, 2024),
        )
        for entity_id in (REGENCY, SPAIN, MODERN_ALGERIA):
            Entity.from_dict(entities[entity_id])

    def test_promoted_events_have_exact_actors_and_tactical_results(self):
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        expected = {
            "hced-Oran1704-1708-1": (
                "Siege of Oran (1707-1708)",
                {REGENCY},
                {SPAIN},
            ),
            "hced-Oran1732-1": (
                "Spanish reconquest of Oran (1732)",
                {SPAIN},
                {REGENCY},
            ),
        }
        self.assertEqual(set(events), set(expected))
        for candidate_id, (name, winners, losers) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(event["name"], name)
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                self.assertEqual(event["event_type"], "engagement")
                self.assertEqual(event["war_type"], "interstate")
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if item["termination"] == "engagement_victory"
                    },
                    winners,
                )
                self.assertEqual(
                    {
                        item["entity_id"]
                        for item in event["participants"]
                        if item["termination"] == "engagement_defeat"
                    },
                    losers,
                )
                Event.from_dict(event)

    def test_source_date_override_pins_1708_without_changing_the_queue_row(self):
        rows = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(
            (rows["hced-Oran1704-1708-1"]["year_low"], rows["hced-Oran1704-1708-1"]["year_high"]),
            (1704, 1708),
        )
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        self.assertEqual(
            (events["hced-Oran1704-1708-1"]["year"], events["hced-Oran1704-1708-1"]["end_year"]),
            (1708, 1708),
        )
        self.assertEqual(
            (events["hced-Oran1732-1"]["year"], events["hced-Oran1732-1"]["end_year"]),
            (1732, 1732),
        )
        self.assertEqual(
            events["hced-Oran1704-1708-1"]["canonical_event_key"],
            "siege_of_oran_1707_1708:1708:1708",
        )

    def test_reviewed_point_country_and_provenance_are_retained(self):
        self.assertFalse(lane.WAVE8_ORAN_POINT_QUARANTINE_ADDITIONS)
        self.assertFalse(lane.WAVE8_ORAN_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertFalse(lane.WAVE8_ORAN_LOCATION_QUARANTINE_REASONS)
        for event in self._events():
            self.assertEqual(event["modern_location_country"], "Algeria")
            self.assertEqual(event["geometry"]["type"], "Point")
            self.assertEqual(event["geometry"]["coordinates"], [-0.6307988, 35.6970697])
            self.assertEqual(
                event["location_provenance"]["assertion_status"],
                "unreviewed_source_assertion",
            )

    def test_preintegration_duplicate_audit_is_zero(self):
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_oran_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
        )

    def test_future_hced_iwbd_and_release_twins_fail_closed(self):
        _, _, existing = self._installed()
        fixtures = {
            "hced": (
                [
                    *copy.deepcopy(self.hced_rows),
                    {
                        "candidate_id": "hced-future-oran-twin",
                        "name": "Siege of Oran",
                        "year_low": 1708,
                        "side_1_raw": "Future A",
                        "side_2_raw": "Future B",
                    },
                ],
                self.iwbd_rows,
                existing,
            ),
            "iwbd": (
                self.hced_rows,
                [
                    *copy.deepcopy(self.iwbd_rows),
                    {
                        "candidate_id": "iwbd-future-oran-twin",
                        "batname": "Oran",
                        "batyear": 1732,
                    },
                ],
                existing,
            ),
            "release": (
                self.hced_rows,
                self.iwbd_rows,
                [
                    *copy.deepcopy(existing),
                    {
                        "id": "future-release-oran-twin",
                        "name": "Spanish conquest of Oran",
                        "year": 1732,
                    },
                ],
            ),
        }
        for view, (hced_rows, iwbd_rows, release_events) in fixtures.items():
            with self.subTest(view=view):
                with self.assertRaisesRegex(ValueError, "unreviewed twin"):
                    lane.validate_wave8_oran_integration_dispositions(
                        hced_rows,
                        iwbd_rows,
                        release_events,
                    )

    def test_queue_inventory_fingerprints_and_named_outcome_guards_fail_closed(self):
        future = copy.deepcopy(self.hced_rows)
        row = copy.deepcopy(
            next(item for item in future if item["candidate_id"] == "hced-Tindouf1963-1")
        )
        row["candidate_id"] = "hced-future-algeria-row"
        future.append(row)
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            lane.validate_wave8_oran_queue_contracts(future)

        disposition = copy.deepcopy(self.hced_rows)
        row = next(item for item in disposition if item["candidate_id"] == "hced-Tindouf1963-1")
        row["winner_raw"] = "Morocco"
        with self.assertRaisesRegex(ValueError, "disposition row fingerprint changed"):
            lane.validate_wave8_oran_queue_contracts(disposition)

        fingerprint = copy.deepcopy(self.hced_rows)
        row = next(item for item in fingerprint if item["candidate_id"] == "hced-Oran1732-1")
        row["winner_raw"] = "Algeria"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_oran_queue_contracts(fingerprint)

        def pinned_hash(row):
            candidate_id = str(row.get("candidate_id"))
            if candidate_id in EXPECTED_HASHES:
                return EXPECTED_HASHES[candidate_id]
            return canonical_hced_row_sha256(row)

        alignment = copy.deepcopy(self.hced_rows)
        row = next(item for item in alignment if item["candidate_id"] == "hced-Oran1732-1")
        row["winner_raw"] = "France"
        with patch.object(lane, "canonical_hced_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "outcome alignment changed"):
                lane.validate_wave8_oran_queue_contracts(alignment)

        competitive = copy.deepcopy(self.hced_rows)
        row = next(item for item in competitive if item["candidate_id"] == "hced-Oran1780-1")
        row["winner_loser_complete"] = False
        with patch.object(lane, "canonical_hced_row_sha256", side_effect=pinned_hash):
            with self.assertRaisesRegex(ValueError, "competitive-outcome guard changed"):
                lane.validate_wave8_oran_queue_contracts(competitive)

    def test_promoter_rejects_candidate_name_and_entity_window_collisions(self):
        entities, _, existing = self._installed()
        events = lane.promote_wave8_oran_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_oran_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_oran_contracts(
                self.hced_rows,
                entities,
                [
                    *existing,
                    {
                        "id": "future-duplicate-oran",
                        "name": "Siege of Oran (1707-1708)",
                        "year": 1708,
                    },
                ],
            )

        missing = dict(entities)
        missing.pop(REGENCY)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_oran_contracts(
                self.hced_rows,
                missing,
                existing,
            )

    def test_installers_are_idempotent_and_source_collisions_fail_closed(self):
        entities, sources, _ = self._installed()
        entities_before = copy.deepcopy(entities)
        lane.install_wave8_oran_entities(entities)
        self.assertEqual(entities, entities_before)

        once = copy.deepcopy(sources)
        lane.install_wave8_oran_sources(sources)
        self.assertEqual(sources, once)

        source_id = str(lane.WAVE8_ORAN_SOURCES[0]["id"])
        sources[source_id]["title"] = "tampered title"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_oran_sources(sources)

    def test_counts_cohorts_metadata_and_final_signature_are_pinned(self):
        self.assertEqual(
            lane.wave8_oran_counts(),
            {
                "country_quarantine_additions": 0,
                "existing_release_dispositions": 1,
                "holds": 1,
                "new_entities": 0,
                "new_sources": 4,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 3,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_oran_cohort_counts(),
            {"spanish_algerian_oran_contests_1707_1780": 3},
        )
        self.assertEqual(
            lane.wave8_oran_audit_signature(),
            "f7efdc3b87f9affed38dc67a0f8c80dba72d8b6bbef16e6babc19a3a0cb9bf4e",
        )
        self.assertEqual(
            lane.wave8_oran_audit_signature(),
            lane.WAVE8_ORAN_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_oran_metadata(),
            {
                "counts": lane.wave8_oran_counts(),
                "cohorts": lane.wave8_oran_cohort_counts(),
                "final_audit_signature": lane.WAVE8_ORAN_FINAL_AUDIT_SIGNATURE,
                "promoted_candidate_ids": sorted(lane.WAVE8_ORAN_CONTRACT_IDS),
            },
        )

    def test_current_release_is_all_or_none_and_matches_oran_artifact_pins(self):
        owned = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") in lane.WAVE8_ORAN_RESERVED_IDS
            or str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        owned_ids = {str(event.get("hced_candidate_id")) for event in owned}
        self.assertIn(owned_ids, (set(), set(lane.WAVE8_ORAN_CONTRACT_IDS)))
        promotion = self.release_metadata["promotion"]
        if not owned_ids:
            self.assertNotIn("accepted_wave8_oran_hced_events", promotion)
            return

        self.assertEqual(len(owned), len(lane.WAVE8_ORAN_CONTRACT_IDS))
        self.assertEqual(len({str(event["id"]) for event in owned}), len(owned))
        self.assertTrue(
            all(str(event["id"]).startswith(EVENT_ID_PREFIX) for event in owned)
        )
        self.assertNotIn("hced-Oran1780-1", owned_ids)
        for event in owned:
            Event.from_dict(event)

        tindouf = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") == "hced-Tindouf1963-1"
        ]
        self.assertEqual(len(tindouf), 1)
        self.assertEqual(
            tindouf[0]["id"],
            lane.WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS[
                "hced-Tindouf1963-1"
            ]["owner_event_id"],
        )
        self.assertIn(
            MODERN_ALGERIA,
            {participant["entity_id"] for participant in tindouf[0]["participants"]},
        )

        self.assertEqual(promotion["accepted_wave8_oran_hced_events"], 2)
        expected_metadata = {
            "wave8_oran_counts": lane.wave8_oran_counts(),
            "wave8_oran_cohort_counts": lane.wave8_oran_cohort_counts(),
            "wave8_oran_audit_signature": lane.wave8_oran_audit_signature(),
            "wave8_oran_final_audit_signature": (
                lane.WAVE8_ORAN_FINAL_AUDIT_SIGNATURE
            ),
            "wave8_oran_queue_validation": {
                "exact_label_rows": 4,
                "holds": 1,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 3,
            },
            "wave8_oran_integration_validation": {
                "existing_release_probable_twins": 0,
                "hced_probable_twins": 0,
                "iwbd_probable_twins": 0,
            },
            "wave8_oran_candidate_ids": sorted(lane.WAVE8_ORAN_CONTRACT_IDS),
            "wave8_oran_holds": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(lane.WAVE8_ORAN_HOLDS.items())
            ],
            "wave8_oran_existing_release_dispositions": [
                {"candidate_id": candidate_id, **contract}
                for candidate_id, contract in sorted(
                    lane.WAVE8_ORAN_EXISTING_RELEASE_DISPOSITIONS.items()
                )
            ],
            "wave8_oran_exact_label_funnel_audit": lane.WAVE8_ORAN_FUNNEL_AUDIT,
            "wave8_oran_entities_added": 0,
            "wave8_oran_sources_added": len(lane.WAVE8_ORAN_SOURCES),
        }
        self.assertEqual(
            {key: promotion[key] for key in expected_metadata},
            expected_metadata,
        )
        self.assertEqual(len(self.release_events), 5_585)

        coverage = self.registry["coverage"]
        self.assertEqual(coverage["candidate_keyed_wave8_oran_hced_events"], 2)
        self.assertEqual(coverage["rated_events"], 5_585)
        location = coverage["hced_location_assertions"]
        self.assertEqual(location["hced_candidate_bindings"], 5_318)
        self.assertEqual(location["candidate_keyed_reviewed_contracts"], 906)
        self.assertEqual(location["geojson_points"], 4_850)
        self.assertEqual(location["modern_location_country_assertions"], 5_218)
        self.assertEqual(location["location_provenance_objects"], 5_267)

        lane_source_ids = {str(item["id"]) for item in lane.WAVE8_ORAN_SOURCES}
        release_source_ids = {str(item["id"]) for item in self.release_sources}
        self.assertLessEqual(lane_source_ids, release_source_ids)


if __name__ == "__main__":
    unittest.main()
