from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion import wave8_eritrean_rebels as lane
from military_elo.promotion.wave8_eritrea import (
    WAVE8_ERITREA_ENTITIES,
    WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS,
    WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_eritrean_rebels_"

ETHIOPIA_ID = "clio_q115_1942_f6caec22"
SOVIET_UNION_ID = "soviet_union"
STATE_ERITREA_ID = "clio_q986_1992_ada8dae7"

EXPECTED_ROWS = {
    "hced-Assab1991-1": (
        "Eritrean Rebels",
        "Ethiopia",
        "Eritrean Rebels",
        1991,
        1991,
    ),
    "hced-Dekemhare1990-1991-1": (
        "Eritrean Rebels",
        "Ethiopia",
        "Eritrean Rebels",
        1990,
        1991,
    ),
    "hced-Massawa1977-1": (
        "Ethiopia, USSR",
        "Eritrean Rebels",
        "Ethiopia, USSR",
        1977,
        1977,
    ),
    "hced-Massawa1990-1": (
        "Eritrean Rebels",
        "Ethiopia",
        "Eritrean Rebels",
        1990,
        1990,
    ),
}

EXPECTED_ENTITIES = {
    "eplf_assab_offensive_force_1991": (1991, 1991),
    "eplf_dekemhare_front_force_1990_1991": (1990, 1991),
    "eplf_massawa_assault_force_1977": (1977, 1977),
    "eplf_operation_fenkil_force_1990": (1990, 1990),
}

EXPECTED_EVENTS = {
    "hced-Assab1991-1": {
        "name": "Siege and capture of Assab",
        "years": (1991, 1991),
        "event_type": "engagement",
        "date_precision": "day_range",
        "winners": {"eplf_assab_offensive_force_1991"},
        "losers": {ETHIOPIA_ID},
    },
    "hced-Dekemhare1990-1991-1": {
        "name": "Dekemhare front campaign and capture",
        "years": (1990, 1991),
        "event_type": "campaign",
        "date_precision": "year_range_end_day_variance",
        "winners": {"eplf_dekemhare_front_force_1990_1991"},
        "losers": {ETHIOPIA_ID},
    },
    "hced-Massawa1977-1": {
        "name": "First Battle of Massawa",
        "years": (1977, 1977),
        "event_type": "engagement",
        "date_precision": "month",
        "winners": {ETHIOPIA_ID, SOVIET_UNION_ID},
        "losers": {"eplf_massawa_assault_force_1977"},
    },
    "hced-Massawa1990-1": {
        "name": "Second Battle of Massawa (Operation Fenkil)",
        "years": (1990, 1990),
        "event_type": "engagement",
        "date_precision": "day_range",
        "winners": {"eplf_operation_fenkil_force_1990"},
        "losers": {ETHIOPIA_ID},
    },
}

RELATED_ETHIOPIA_ROWS = {
    "hced-Addis Ababa1991-1",
    "hced-Asosa1990-1991-1",
    "hced-Inda Silase1989-1",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _canonical_json(value) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _independent_signature() -> str:
    payload = {
        "contracts": lane.WAVE8_ERITREAN_REBELS_CONTRACTS,
        "country_quarantine_additions": sorted(
            lane.WAVE8_ERITREAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_lane_dispositions": (
            lane.WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS
        ),
        "entities": lane.WAVE8_ERITREAN_REBELS_ENTITIES,
        "existing_release_duplicate_dispositions": (
            lane.WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(
            lane.WAVE8_ERITREAN_REBELS_EXPECTED_CANDIDATE_IDS
        ),
        "hced_duplicate_dispositions": (
            lane.WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS
        ),
        "holds": lane.WAVE8_ERITREAN_REBELS_HOLDS,
        "integration_dispositions": (
            lane.WAVE8_ERITREAN_REBELS_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": (
            lane.WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_zero_overlap_audit": (
            lane.WAVE8_ERITREAN_REBELS_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "location_quarantine_reasons": (
            lane.WAVE8_ERITREAN_REBELS_LOCATION_QUARANTINE_REASONS
        ),
        "outcome_overrides": lane.WAVE8_ERITREAN_REBELS_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            lane.WAVE8_ERITREAN_REBELS_POINT_QUARANTINE_ADDITIONS
        ),
        "related_hced_dispositions": (
            lane.WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS
        ),
        "row_hashes": lane.WAVE8_ERITREAN_REBELS_ROW_HASHES,
        "sources": lane.WAVE8_ERITREAN_REBELS_SOURCES,
        "terminal_exclusions": lane.WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


class Wave8EritreanRebelsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_path = ROOT / "data/review/hced-candidates.jsonl"
        cls.iwbd_path = ROOT / "data/review/iwbd-candidates.jsonl"
        cls.hced_rows = _jsonl(cls.hced_path)
        cls.iwbd_rows = _jsonl(cls.iwbd_path)
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced_rows
        }
        cls.iwbd_by_id = {
            str(row["candidate_id"]): row for row in cls.iwbd_rows
        }

    def _installed(self):
        new_entity_ids = {
            str(item["id"]) for item in lane.WAVE8_ERITREAN_REBELS_ENTITIES
        }
        entities = {
            str(item["id"]): item
            for item in self.release_entities
            if str(item["id"]) not in new_entity_ids
        }
        lane.install_wave8_eritrean_rebels_entities(entities)

        new_source_ids = {
            str(item["id"]) for item in lane.WAVE8_ERITREAN_REBELS_SOURCES
        }
        sources = {
            str(item["id"]): item
            for item in self.release_sources
            if str(item["id"]) not in new_source_ids
        }
        lane.install_wave8_eritrean_rebels_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_ERITREAN_REBELS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_eritrean_rebels_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_locked_queue_hashes_and_row_fingerprints_are_exact(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            lane.WAVE8_ERITREAN_REBELS_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            lane.WAVE8_ERITREAN_REBELS_IWBD_QUEUE_SHA256,
        )
        for candidate_id, expected_hash in lane.WAVE8_ERITREAN_REBELS_ROW_HASHES.items():
            self.assertEqual(
                canonical_hced_row_sha256(self.hced_by_id[candidate_id]),
                expected_hash,
            )

    def test_complete_exact_label_inventory_is_four_rows(self) -> None:
        exact = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "eritrean rebels"
            or normalize_label(row.get("side_2_raw")) == "eritrean rebels"
        }
        self.assertEqual(set(exact), set(EXPECTED_ROWS))
        self.assertEqual(
            set(exact),
            lane.WAVE8_ERITREAN_REBELS_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            lane.WAVE8_ERITREAN_REBELS_RESERVED_IDS,
            lane.WAVE8_ERITREAN_REBELS_EXPECTED_CANDIDATE_IDS,
        )
        for candidate_id, expected in EXPECTED_ROWS.items():
            row = exact[candidate_id]
            self.assertEqual(
                (
                    row["side_1_raw"],
                    row["side_2_raw"],
                    row["winner_raw"],
                    row["year_low"],
                    row["year_high"],
                ),
                expected,
            )
            self.assertTrue(row["winner_loser_complete"])

    def test_signature_and_exact_counts_are_locked(self) -> None:
        self.assertEqual(
            lane.wave8_eritrean_rebels_audit_signature(),
            lane.WAVE8_ERITREAN_REBELS_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            _independent_signature(),
            lane.WAVE8_ERITREAN_REBELS_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            lane.wave8_eritrean_rebels_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 2,
                "existing_release_duplicate_dispositions": 1,
                "hced_duplicate_dispositions": 1,
                "holds": 0,
                "integration_dispositions": 8,
                "iwbd_duplicate_dispositions": 1,
                "iwbd_zero_overlap_candidates": 4,
                "new_entities": 4,
                "new_sources": 12,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "related_hced_dispositions": 3,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_eritrean_rebels_cohort_counts(),
            {
                "dekemhare_front_1990_1991": 1,
                "final_assab_offensive_1991": 1,
                "first_massawa_battle_1977": 1,
                "operation_fenkil_1990": 1,
            },
        )

    def test_sources_parse_and_outcomes_have_independent_families(self) -> None:
        source_by_id = {
            str(item["id"]): item
            for item in lane.WAVE8_ERITREAN_REBELS_SOURCES
        }
        self.assertEqual(len(source_by_id), 12)
        for source in source_by_id.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
        used: set[str] = set()
        for entity in lane.WAVE8_ERITREAN_REBELS_ENTITIES:
            used.update(map(str, entity["source_ids"]))
        for contract in lane.WAVE8_ERITREAN_REBELS_CONTRACTS.values():
            used.update(map(str, contract["evidence_refs"]))
            outcomes = list(map(str, contract["outcome_source_ids"]))
            self.assertGreaterEqual(len(outcomes), 2)
            self.assertTrue(set(outcomes) <= set(contract["evidence_refs"]))
            families = sorted(
                {source_by_id[source_id]["source_family_id"] for source_id in outcomes}
            )
            self.assertEqual(contract["outcome_source_family_ids"], families)
            self.assertGreaterEqual(len(families), 2)
        for inventory in (
            lane.WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS,
            lane.WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS,
            lane.WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS,
            lane.WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS,
            lane.WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
        ):
            for item in inventory.values():
                used.update(map(str, item["evidence_refs"]))
        self.assertEqual(used, set(source_by_id))

    def test_entities_are_alias_free_event_bounded_eplf_formations(self) -> None:
        entities = {
            str(item["id"]): item
            for item in lane.WAVE8_ERITREAN_REBELS_ENTITIES
        }
        self.assertEqual(set(entities), set(EXPECTED_ENTITIES))
        self.assertNotIn(STATE_ERITREA_ID, entities)
        for entity_id, fixture in entities.items():
            parsed = Entity.from_dict(fixture)
            self.assertEqual(
                (parsed.start_year, parsed.end_year),
                EXPECTED_ENTITIES[entity_id],
            )
            self.assertEqual(fixture["aliases"], [])
            self.assertEqual(fixture["predecessors"], [])
            note = fixture["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("generic eritrean rebels", note)
            self.assertIn("state of eritrea", note)
            self.assertIn("another eplf formation", note)

    def test_contracts_preserve_raw_winners_and_unknown_is_never_draw(self) -> None:
        self.assertEqual(lane.WAVE8_ERITREAN_REBELS_OUTCOME_OVERRIDES, {})
        self.assertEqual(lane.WAVE8_ERITREAN_REBELS_HOLDS, {})
        self.assertEqual(lane.WAVE8_ERITREAN_REBELS_TERMINAL_EXCLUSIONS, {})
        for candidate_id, contract in lane.WAVE8_ERITREAN_REBELS_CONTRACTS.items():
            row = self.hced_by_id[candidate_id]
            winner_side = int(contract["winner_side"])
            self.assertEqual(row["winner_raw"], row[f"side_{winner_side}_raw"])
            self.assertEqual(row["loser_raw"], row[f"side_{3 - winner_side}_raw"])
            self.assertNotIn(
                normalize_label(row["winner_raw"]),
                {"", "draw", "inconclusive", "stalemate"},
            )
            self.assertEqual(contract["result_type"], "win")
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertTrue(contract["actor_override"])

    def test_massawa_1977_keeps_attested_soviet_coalition_and_repulse(self) -> None:
        contract = lane.WAVE8_ERITREAN_REBELS_CONTRACTS[
            "hced-Massawa1977-1"
        ]
        self.assertEqual(
            contract["side_1_entity_ids"],
            [ETHIOPIA_ID, SOVIET_UNION_ID],
        )
        self.assertEqual(contract["winner_side"], 1)
        self.assertIn("repulsed", contract["direct_provenance"]["reviewed_outcome"])
        self.assertEqual(
            set(contract["outcome_source_ids"]),
            {
                "wave8_eritrean_rebels_africa_watch_evil_days",
                "wave8_eritrean_rebels_lrb_harding_1987",
            },
        )

    def test_later_operations_have_narrow_boundaries_without_false_precision(self) -> None:
        fenkil = lane.WAVE8_ERITREAN_REBELS_CONTRACTS[
            "hced-Massawa1990-1"
        ]["canonical_event"]
        self.assertEqual(fenkil["date_text"], "8-10 February 1990")
        self.assertEqual(fenkil["date_precision"], "day_range")

        dekemhare = lane.WAVE8_ERITREAN_REBELS_CONTRACTS[
            "hced-Dekemhare1990-1991-1"
        ]
        self.assertEqual(dekemhare["event_type"], "campaign")
        self.assertEqual(
            dekemhare["canonical_event"]["date_precision"],
            "year_range_end_day_variance",
        )
        self.assertIn("19-24 May", dekemhare["canonical_event"]["date_text"])

        assab = lane.WAVE8_ERITREAN_REBELS_CONTRACTS[
            "hced-Assab1991-1"
        ]
        self.assertEqual(
            assab["canonical_event"]["date_text"],
            "24-25 May 1991",
        )
        self.assertIn("final stronghold", assab["audit_note"])

    def test_concurrent_exact_eritrea_lane_is_disjoint_and_reciprocal(self) -> None:
        own_ids = set(lane.WAVE8_ERITREAN_REBELS_RESERVED_IDS)
        self.assertFalse(own_ids & set(WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS))
        self.assertFalse(
            {item["id"] for item in lane.WAVE8_ERITREAN_REBELS_ENTITIES}
            & {item["id"] for item in WAVE8_ERITREA_ENTITIES}
        )
        reciprocal = set(WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS)
        self.assertTrue(own_ids <= reciprocal)
        self.assertTrue(RELATED_ETHIOPIA_ROWS <= reciprocal)
        for candidate_id in own_ids | RELATED_ETHIOPIA_ROWS:
            self.assertEqual(
                WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS[candidate_id][
                    "raw_row_sha256"
                ],
                lane.WAVE8_ERITREAN_REBELS_ROW_HASHES[candidate_id],
            )

    def test_ethiopia_and_composite_rows_remain_separate(self) -> None:
        self.assertEqual(
            set(lane.WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS),
            RELATED_ETHIOPIA_ROWS,
        )
        self.assertFalse(
            RELATED_ETHIOPIA_ROWS & lane.WAVE8_ERITREAN_REBELS_RESERVED_IDS
        )
        dispositions = {
            item["disposition"]
            for item in lane.WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS.values()
        }
        self.assertEqual(
            dispositions,
            {
                "separate_ethiopian_rebel_coalition_lane",
                "separate_oromo_eritrean_composite_lane",
                "separate_tigrayan_eritrean_composite_lane",
            },
        )

    def test_queue_and_integration_validators_return_exact_counts(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            lane.validate_wave8_eritrean_rebels_queue_contracts(self.hced_rows),
            {
                "holds": 0,
                "promotion_contracts": 4,
                "related_hced_dispositions": 3,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.validate_wave8_eritrean_rebels_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_lane_hced_dispositions": 2,
                "existing_release_duplicate_dispositions": 1,
                "hced_duplicate_dispositions": 1,
                "integration_dispositions": 8,
                "iwbd_duplicate_dispositions": 1,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 4,
                "related_hced_dispositions": 3,
            },
        )

    def test_queue_validator_fails_closed_on_drift_missing_or_extra_label(self) -> None:
        changed = copy.deepcopy(self.hced_rows)
        row = next(
            item for item in changed if item["candidate_id"] == "hced-Assab1991-1"
        )
        row["winner_raw"] = ""
        with self.assertRaises(ValueError):
            lane.validate_wave8_eritrean_rebels_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row["candidate_id"] != "hced-Massawa1977-1"
        ]
        with self.assertRaises(ValueError):
            lane.validate_wave8_eritrean_rebels_queue_contracts(missing)

        synthetic = copy.deepcopy(self.hced_by_id["hced-Assab1991-1"])
        synthetic["candidate_id"] = "hced-SyntheticEritreanRebels1991-1"
        with self.assertRaisesRegex(ValueError, "inventory changed"):
            lane.validate_wave8_eritrean_rebels_queue_contracts(
                [*self.hced_rows, synthetic]
            )

    def test_duplicate_audit_pins_distinct_1941_massawa_records(self) -> None:
        hced = lane.WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS[
            "hced-Massawa1941-1"
        ]
        hced_row = self.hced_by_id["hced-Massawa1941-1"]
        self.assertEqual(
            (hced_row["name"], hced_row["year_low"], hced_row["year_high"]),
            (hced["expected_name"], 1941, 1941),
        )

        iwbd = lane.WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS[
            "iwbd-139-53-961"
        ]
        iwbd_row = self.iwbd_by_id["iwbd-139-53-961"]
        self.assertEqual(iwbd_row["name"], iwbd["expected_name"])
        self.assertEqual(iwbd_row["start_date"], iwbd["expected_start_date"])
        self.assertEqual(iwbd_row["winner_raw"], iwbd["expected_winner_raw"])

        released = [
            event
            for event in self.release_events
            if event["id"] == "hced_hced_massawa1941_1"
        ]
        self.assertEqual(len(released), 1)
        self.assertEqual(released[0]["hced_candidate_id"], "hced-Massawa1941-1")

    def test_integration_fails_closed_on_new_hced_iwbd_or_release_twin(self) -> None:
        _, _, existing = self._installed()
        hced_twin = {
            "candidate_id": "hced-future-assab",
            "name": "Assab",
            "year_low": 1991,
            "year_high": 1991,
            "side_1_raw": "A",
            "side_2_raw": "B",
        }
        with self.assertRaisesRegex(ValueError, "unreviewed cross-lane HCED twin"):
            lane.validate_wave8_eritrean_rebels_integration_dispositions(
                [*self.hced_rows, hced_twin],
                self.iwbd_rows,
                existing,
            )

        iwbd_twin = {
            "candidate_id": "iwbd-future-fenkil",
            "name": "Operation Fenkil",
            "start_date": "1990-02-08",
            "end_date": "1990-02-10",
        }
        with self.assertRaisesRegex(ValueError, "unreviewed probable IWBD twin"):
            lane.validate_wave8_eritrean_rebels_integration_dispositions(
                self.hced_rows,
                [*self.iwbd_rows, iwbd_twin],
                existing,
            )

        release_twin = {"id": "future-assab", "name": "Assab", "year": 1991}
        with self.assertRaisesRegex(ValueError, "unreviewed existing-release twin"):
            lane.validate_wave8_eritrean_rebels_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*existing, release_twin],
            )

    def test_emits_four_parseable_events_with_exact_results(self) -> None:
        events = self._events()
        by_candidate = {
            str(event["hced_candidate_id"]): event for event in events
        }
        self.assertEqual(set(by_candidate), set(EXPECTED_EVENTS))
        self.assertEqual(len({event["id"] for event in events}), 4)
        self.assertEqual(len({event["canonical_event_key"] for event in events}), 4)
        for candidate_id, expected in EXPECTED_EVENTS.items():
            event = by_candidate[candidate_id]
            parsed = Event.from_dict(event)
            self.assertEqual(parsed.event_type, expected["event_type"])
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["name"], expected["name"])
            self.assertEqual((event["year"], event["end_year"]), expected["years"])
            self.assertEqual(event["date_precision"], expected["date_precision"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["status"], "complete")
            winners = {
                item["entity_id"]
                for item in event["participants"]
                if "victory" in item["termination"]
            }
            losers = {
                item["entity_id"]
                for item in event["participants"]
                if "defeat" in item["termination"]
            }
            self.assertEqual(winners, expected["winners"])
            self.assertEqual(losers, expected["losers"])
            self.assertFalse(
                any(
                    "draw" in item["termination"]
                    or "inconclusive" in item["termination"]
                    for item in event["participants"]
                )
            )
            if expected["event_type"] == "campaign":
                self.assertEqual(
                    {item["termination"] for item in event["participants"]},
                    {"campaign_victory", "campaign_defeat"},
                )
                self.assertIn("operational campaign", event["summary"])

    def test_all_points_are_locally_quarantined_and_country_is_retained(self) -> None:
        point_before = set(HCED_POINT_QUARANTINE_IDS)
        country_before = set(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(
            lane.WAVE8_ERITREAN_REBELS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_ERITREAN_REBELS_RESERVED_IDS,
        )
        self.assertEqual(
            lane.WAVE8_ERITREAN_REBELS_COUNTRY_QUARANTINE_ADDITIONS,
            frozenset(),
        )
        self.assertEqual(
            lane.wave8_eritrean_rebels_location_quarantine_additions(),
            {
                "point": lane.WAVE8_ERITREAN_REBELS_RESERVED_IDS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            set(lane.WAVE8_ERITREAN_REBELS_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_ERITREAN_REBELS_RESERVED_IDS,
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Eritrea")
            self.assertIn("location_provenance", event)
        self.assertEqual(set(HCED_POINT_QUARANTINE_IDS), point_before)
        self.assertEqual(set(HCED_COUNTRY_QUARANTINE_IDS), country_before)

    def test_installers_are_idempotent_copy_and_collision_safe(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        lane.install_wave8_eritrean_rebels_entities(entities)
        lane.install_wave8_eritrean_rebels_sources(sources)
        expected_entities = copy.deepcopy(entities)
        expected_sources = copy.deepcopy(sources)
        lane.install_wave8_eritrean_rebels_entities(entities)
        lane.install_wave8_eritrean_rebels_sources(sources)
        self.assertEqual(entities, expected_entities)
        self.assertEqual(sources, expected_sources)

        entity_id = str(lane.WAVE8_ERITREAN_REBELS_ENTITIES[0]["id"])
        source_id = str(lane.WAVE8_ERITREAN_REBELS_SOURCES[0]["id"])
        entities[entity_id]["name"] = "tampered"
        sources[source_id]["title"] = "tampered"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_eritrean_rebels_entities(entities)
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_eritrean_rebels_sources(sources)

    def test_promotion_requires_entity_windows_and_unique_ownership(self) -> None:
        entities, _, existing = self._installed()
        missing = copy.deepcopy(entities)
        del missing["eplf_operation_fenkil_force_1990"]
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_eritrean_rebels_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        wrong_window = copy.deepcopy(entities)
        wrong_window["eplf_dekemhare_front_force_1990_1991"]["start_year"] = 1991
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_eritrean_rebels_contracts(
                self.hced_rows,
                wrong_window,
                existing,
            )

        events = lane.promote_wave8_eritrean_rebels_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_eritrean_rebels_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

    def test_integration_disposition_union_is_complete(self) -> None:
        expected = {
            *(f"cross_lane:{key}" for key in lane.WAVE8_ERITREAN_REBELS_CROSS_LANE_DISPOSITIONS),
            *(f"related_hced:{key}" for key in lane.WAVE8_ERITREAN_REBELS_RELATED_HCED_DISPOSITIONS),
            *(f"hced_duplicate:{key}" for key in lane.WAVE8_ERITREAN_REBELS_HCED_DUPLICATE_DISPOSITIONS),
            *(f"iwbd_duplicate:{key}" for key in lane.WAVE8_ERITREAN_REBELS_IWBD_DUPLICATE_DISPOSITIONS),
            *(f"existing_release:{key}" for key in lane.WAVE8_ERITREAN_REBELS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS),
        }
        self.assertEqual(
            set(lane.WAVE8_ERITREAN_REBELS_INTEGRATION_DISPOSITIONS),
            expected,
        )
        self.assertEqual(len(expected), 8)

    def test_public_api_exposes_lane_contracts_and_validators(self) -> None:
        required = {
            "WAVE8_ERITREAN_REBELS_CONTRACTS",
            "WAVE8_ERITREAN_REBELS_ENTITIES",
            "WAVE8_ERITREAN_REBELS_FINAL_AUDIT_SIGNATURE",
            "WAVE8_ERITREAN_REBELS_INTEGRATION_DISPOSITIONS",
            "WAVE8_ERITREAN_REBELS_LOCATION_QUARANTINE_ADDITIONS",
            "WAVE8_ERITREAN_REBELS_SOURCES",
            "install_wave8_eritrean_rebels_entities",
            "install_wave8_eritrean_rebels_sources",
            "promote_wave8_eritrean_rebels_contracts",
            "validate_wave8_eritrean_rebels_integration_dispositions",
            "validate_wave8_eritrean_rebels_queue_contracts",
            "wave8_eritrean_rebels_audit_signature",
            "wave8_eritrean_rebels_counts",
        }
        self.assertTrue(required <= set(lane.__all__))


if __name__ == "__main__":
    unittest.main()
