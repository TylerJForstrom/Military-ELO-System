import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_georgian_uprising as lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_georgian_uprising_"
UPRISING = "kartli_kakheti_uprising_forces_1625"
SAFAVID = "safavid_empire"

EXPECTED_HASHES = {
    "hced-Marabda1625-1": (
        "5a7692f5ee88d488d2b16ad72c37e895ee19348823b8fcbeb737020a3f95abf2"
    ),
    "hced-Marqopi1625-1": (
        "dcbbafc3e6bc8ff1f99b7de9f8f8080aea7025c895b78015a966f0e4c37b3272"
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


class Wave8GeorgianUprisingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "georgian rebels"
            or normalize_label(row.get("side_2_raw")) == "georgian rebels"
        ]

    def _installed(self):
        lane_entity_ids = {
            str(item["id"]) for item in lane.WAVE8_GEORGIAN_UPRISING_ENTITIES
        }
        entities = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_entities
            if str(item["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(item["id"]) for item in lane.WAVE8_GEORGIAN_UPRISING_SOURCES
        }
        sources = {
            str(item["id"]): copy.deepcopy(item)
            for item in self.release_sources
            if str(item["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_georgian_uprising_entities(entities)
        lane.install_wave8_georgian_uprising_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_georgian_uprising_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_label_inventory_and_complete_row_hashes_are_pinned(self) -> None:
        rows = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(set(rows), set(EXPECTED_HASHES))
        self.assertEqual(lane.WAVE8_GEORGIAN_UPRISING_ROW_HASHES, EXPECTED_HASHES)
        self.assertEqual(
            lane.WAVE8_GEORGIAN_UPRISING_EXPECTED_CANDIDATE_IDS,
            frozenset(EXPECTED_HASHES),
        )
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertIs(row["do_not_rate_automatically"], True)
                self.assertIs(row["winner_loser_complete"], True)
                self.assertEqual(row["massacre_raw"], "No")

    def test_queue_and_historical_funnel_are_fail_closed(self) -> None:
        self.assertEqual(
            lane.validate_wave8_georgian_uprising_queue_contracts(self.hced_rows),
            {
                "exact_label_rows": 2,
                "holds": 0,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
            },
        )
        historical = {
            "labels": [
                {
                    "candidate_ids": [],
                    "event_candidate_id_sha256": (
                        "03c27677cedba86f0040739ef60641a5132045e7e51d5309ee7ebce306f09697"
                    ),
                    "events_touched": 2,
                    "failure_cases": {"zero_time_valid_candidates": 2},
                    "label": "georgian rebels",
                    "sole_blocker_events": 2,
                }
            ]
        }
        self.assertEqual(
            lane.validate_wave8_georgian_uprising_funnel(historical),
            {
                "events_touched": 2,
                "sole_blocker_events": 2,
                "zero_time_valid_candidates": 2,
            },
        )

    def test_identity_is_alias_free_and_bounded_to_the_1625_uprising(self) -> None:
        self.assertEqual(len(lane.WAVE8_GEORGIAN_UPRISING_ENTITIES), 1)
        entity = lane.WAVE8_GEORGIAN_UPRISING_ENTITIES[0]
        self.assertEqual(entity["id"], UPRISING)
        self.assertEqual((entity["start_year"], entity["end_year"]), (1625, 1625))
        self.assertEqual(entity["aliases"], [])
        self.assertEqual(entity["predecessors"], [])
        self.assertIn("No generic Georgian Rebels", entity["continuity_note"])
        Entity.from_dict(entity)

        entities, _, _ = self._installed()
        self.assertEqual(
            lane.validate_wave8_georgian_uprising_existing_entities(entities),
            {"required_existing_entities": 1},
        )
        self.assertEqual(entities[SAFAVID]["name"], "Safavid Iran")
        self.assertLessEqual(
            entities[SAFAVID]["start_year"],
            1625,
        )
        self.assertGreaterEqual(entities[SAFAVID]["end_year"], 1625)

    def test_sources_parse_and_each_outcome_has_two_independent_families(self) -> None:
        self.assertEqual(len(lane.WAVE8_GEORGIAN_UPRISING_SOURCES), 3)
        for source in lane.WAVE8_GEORGIAN_UPRISING_SOURCES:
            Source.from_dict(source)
        for candidate_id, contract in lane.WAVE8_GEORGIAN_UPRISING_CONTRACTS.items():
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    contract["evidence_refs"],
                    contract["outcome_source_ids"],
                )
                self.assertEqual(len(contract["outcome_source_family_ids"]), 2)
                self.assertEqual(
                    contract["outcome_source_family_ids"],
                    sorted(set(contract["outcome_source_family_ids"])),
                )

    def test_only_the_two_fingerprinted_rows_promote_and_unknown_is_not_draw(self) -> None:
        self.assertEqual(
            lane.WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS,
            frozenset(EXPECTED_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_GEORGIAN_UPRISING_RESERVED_IDS,
            frozenset(EXPECTED_HASHES),
        )
        self.assertFalse(lane.WAVE8_GEORGIAN_UPRISING_HOLDS)
        for contract in lane.WAVE8_GEORGIAN_UPRISING_CONTRACTS.values():
            self.assertEqual(contract["disposition"], "promote")
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

    def test_promotions_pin_both_source_supported_tactical_outcomes(self) -> None:
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        expected = {
            "hced-Marqopi1625-1": (
                "Battle of Martqopi",
                UPRISING,
                SAFAVID,
            ),
            "hced-Marabda1625-1": (
                "Battle of Marabda",
                SAFAVID,
                UPRISING,
            ),
        }
        self.assertEqual(set(events), set(expected))
        for candidate_id, (name, winner, loser) in expected.items():
            with self.subTest(candidate_id=candidate_id):
                event = events[candidate_id]
                self.assertEqual(event["name"], name)
                self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
                outcomes = {
                    participant["entity_id"]: participant["termination"]
                    for participant in event["participants"]
                }
                self.assertEqual(outcomes[winner], "engagement_victory")
                self.assertEqual(outcomes[loser], "engagement_defeat")
                self.assertNotIn("inconclusive", set(outcomes.values()))
                Event.from_dict(event)

    def test_day_text_is_preserved_without_claiming_gregorian_iso_precision(self) -> None:
        expected_text = {
            "hced-Marqopi1625-1": (
                "25 March 1625; calendar style unspecified in the cited sources"
            ),
            "hced-Marabda1625-1": (
                "1 July 1625; calendar style unspecified in the cited sources"
            ),
        }
        events = {str(event["hced_candidate_id"]): event for event in self._events()}
        for candidate_id, date_text in expected_text.items():
            with self.subTest(candidate_id=candidate_id):
                contract = lane.WAVE8_GEORGIAN_UPRISING_CONTRACTS[candidate_id]
                canonical = contract["canonical_event"]
                self.assertEqual(canonical["date_text"], date_text)
                self.assertEqual(
                    canonical["date_precision"],
                    "source_stated_day_calendar_unspecified",
                )
                self.assertEqual(
                    contract["calendar_style"],
                    "unspecified_in_cited_sources",
                )
                self.assertFalse(contract["source_date_override"])
                self.assertEqual(events[candidate_id]["year"], 1625)
                self.assertEqual(events[candidate_id]["end_year"], 1625)
                self.assertEqual(
                    events[candidate_id]["date_precision"],
                    "source_stated_day_calendar_unspecified",
                )
                self.assertIn("calendar style", events[candidate_id]["summary"])
                self.assertNotIn("1625-", events[candidate_id]["summary"])

    def test_points_are_quarantined_while_audited_georgia_country_is_retained(self) -> None:
        self.assertEqual(
            lane.WAVE8_GEORGIAN_UPRISING_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_GEORGIAN_UPRISING_CONTRACT_IDS,
        )
        self.assertFalse(
            lane.WAVE8_GEORGIAN_UPRISING_COUNTRY_QUARANTINE_ADDITIONS
        )
        self.assertEqual(
            set(lane.WAVE8_GEORGIAN_UPRISING_LOCATION_QUARANTINE_REASONS),
            set(EXPECTED_HASHES),
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Georgia")
            self.assertIn("location_provenance", event)
            self.assertEqual(event["source_ids"][0], "hced_dataset")
            self.assertEqual(
                event["outcome_source_ids"],
                lane.WAVE8_GEORGIAN_UPRISING_CONTRACTS[
                    event["hced_candidate_id"]
                ]["outcome_source_ids"],
            )

    def test_no_unreviewed_cross_source_or_release_twins_exist(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_georgian_uprising_integration_dispositions(
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

    def test_row_drift_unknown_outcome_and_duplicate_promotion_fail_closed(self) -> None:
        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Marqopi1625-1"
        )
        row["winner_raw"] = "Unknown"
        row["loser_raw"] = "Unknown"
        with self.assertRaisesRegex(ValueError, "row fingerprint changed"):
            lane.validate_wave8_georgian_uprising_queue_contracts(tampered)

        entities, _, existing = self._installed()
        promoted = lane.promote_wave8_georgian_uprising_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "already promoted"):
            lane.promote_wave8_georgian_uprising_contracts(
                self.hced_rows,
                entities,
                [*existing, *promoted],
            )

    def test_entity_source_collisions_and_existing_identity_drift_fail_closed(self) -> None:
        entities, sources, _ = self._installed()
        bad_entities = copy.deepcopy(entities)
        bad_entities[UPRISING]["aliases"] = ["Georgian Rebels"]
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_georgian_uprising_entities(bad_entities)

        source_id = lane.WAVE8_GEORGIAN_UPRISING_SOURCES[0]["id"]
        bad_sources = copy.deepcopy(sources)
        bad_sources[source_id]["url"] = "https://example.invalid/drift"
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_georgian_uprising_sources(bad_sources)

        bad_existing = copy.deepcopy(entities)
        bad_existing[SAFAVID]["end_year"] = 1624
        with self.assertRaisesRegex(ValueError, "existing identity drift"):
            lane.validate_wave8_georgian_uprising_existing_entities(bad_existing)

    def test_counts_signature_and_integration_hooks_are_pinned(self) -> None:
        self.assertEqual(
            lane.wave8_georgian_uprising_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 0,
                "new_entities": 1,
                "new_sources": 3,
                "newly_rated_events": 2,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "reviewed_hced_rows": 2,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_georgian_uprising_cohort_counts(),
            {"kartli_kakheti_uprising_1625": 2},
        )
        self.assertEqual(
            lane.wave8_georgian_uprising_audit_signature(),
            "0eaa8d2d449b8852f2b2455e381221bbe75f54e4c32ea70deee403acce771424",
        )
        self.assertEqual(
            lane.wave8_georgian_uprising_audit_signature(),
            lane.WAVE8_GEORGIAN_UPRISING_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_georgian_uprising_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": frozenset(EXPECTED_HASHES),
            },
        )
        self.assertEqual(
            lane.wave8_georgian_uprising_metadata()["promoted_candidate_ids"],
            sorted(EXPECTED_HASHES),
        )


if __name__ == "__main__":
    unittest.main()
