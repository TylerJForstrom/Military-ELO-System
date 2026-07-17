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
from military_elo.promotion.wave8_eritrea import (
    WAVE8_ERITREA_CONTRACT_IDS,
    WAVE8_ERITREA_CONTRACTS,
    WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_ERITREA_CROSS_LANE_DISPOSITIONS,
    WAVE8_ERITREA_ENTITIES,
    WAVE8_ERITREA_EXCLUSIONS,
    WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS,
    WAVE8_ERITREA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_ERITREA_EXISTING_RELEASE_IDS,
    WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS,
    WAVE8_ERITREA_EXTERNAL_OWNER_DISPOSITIONS,
    WAVE8_ERITREA_EXTERNAL_OWNER_IDS,
    WAVE8_ERITREA_FINAL_AUDIT_SIGNATURE,
    WAVE8_ERITREA_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_ERITREA_HCED_QUEUE_SHA256,
    WAVE8_ERITREA_HOLD_IDS,
    WAVE8_ERITREA_HOLDS,
    WAVE8_ERITREA_INTEGRATION_DISPOSITIONS,
    WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_ERITREA_IWBD_QUEUE_SHA256,
    WAVE8_ERITREA_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_ERITREA_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_ERITREA_LOCATION_QUARANTINE_REASONS,
    WAVE8_ERITREA_OUTCOME_OVERRIDES,
    WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS,
    WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS,
    WAVE8_ERITREA_RELATED_HCED_IDS,
    WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS,
    WAVE8_ERITREA_RESERVED_IDS,
    WAVE8_ERITREA_REVIEWED_CANDIDATE_IDS,
    WAVE8_ERITREA_ROW_HASHES,
    WAVE8_ERITREA_SOURCES,
    WAVE8_ERITREA_TERMINAL_EXCLUSION_IDS,
    WAVE8_ERITREA_TERMINAL_EXCLUSIONS,
    WAVE8_ERITREA_UNRESOLVED_IDS,
    install_wave8_eritrea_entities,
    install_wave8_eritrea_sources,
    promote_wave8_eritrea_contracts,
    validate_wave8_eritrea_integration_dispositions,
    validate_wave8_eritrea_queue_contracts,
    wave8_eritrea_audit_signature,
    wave8_eritrea_cohort_counts,
    wave8_eritrea_counts,
    wave8_eritrea_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_eritrea_"

ETHIOPIA_ID = "clio_q115_1942_f6caec22"
STATE_ERITREA_ID = "clio_q986_1992_ada8dae7"
KEREN_EPLF_ID = "eplf_keren_defense_force_1977_1978"
NAKFA_EPLF_ID = "eplf_nakfa_front_1977_1988"
BARENTU_EPLF_ID = "eplf_barentu_assault_force_1985"
AFABET_EPLF_ID = "eplf_afabet_field_force_1988"


EXPECTED_EXACT_ROWS = {
    "hced-Afabet1988-1": ("Eritrea", "Ethiopia", "Eritrea", 1988, 1988),
    "hced-Badme1998-1": ("Eritrea", "Ethiopia", "Eritrea", 1998, 1998),
    "hced-Badme1999-1": ("Ethiopia", "Eritrea", "Ethiopia", 1999, 1999),
    "hced-Barentu1985-1": ("Eritrea", "Ethiopia", "Eritrea", 1985, 1985),
    "hced-Barentu2000-1": ("Ethiopia", "Eritrea", "Ethiopia", 2000, 2000),
    "hced-Keren1977-1978-1": (
        "Ethiopia",
        "Eritrea",
        "Ethiopia",
        1977,
        1978,
    ),
    "hced-Nakfa1977-1988-1": (
        "Eritrea",
        "Ethiopia",
        "Eritrea",
        1977,
        1988,
    ),
    "hced-Tsorona1999-1": ("Eritrea", "Ethiopia", "Eritrea", 1999, 1999),
}

EXPECTED_PROMOTIONS = {
    "hced-Afabet1988-1": {
        "name": "Battle of Afabet",
        "years": (1988, 1988),
        "event_type": "engagement",
        "winner": AFABET_EPLF_ID,
        "loser": ETHIOPIA_ID,
        "date_precision": "day_range",
    },
    "hced-Barentu1985-1": {
        "name": "EPLF capture of Barentu",
        "years": (1985, 1985),
        "event_type": "engagement",
        "winner": BARENTU_EPLF_ID,
        "loser": ETHIOPIA_ID,
        "date_precision": "month",
    },
    "hced-Keren1977-1978-1": {
        "name": "Ethiopian campaign to recapture Keren",
        "years": (1977, 1978),
        "event_type": "campaign",
        "winner": ETHIOPIA_ID,
        "loser": KEREN_EPLF_ID,
        "date_precision": "year_range_end_day",
    },
    "hced-Nakfa1977-1988-1": {
        "name": "Defense of the Nakfa front",
        "years": (1977, 1988),
        "event_type": "campaign",
        "winner": NAKFA_EPLF_ID,
        "loser": ETHIOPIA_ID,
        "date_precision": "year_range",
    },
}

EXPECTED_RELATED_HCED_IDS = {
    "hced-Addis Ababa1991-1",
    "hced-Asosa1990-1991-1",
    "hced-Assab1991-1",
    "hced-Dekemhare1990-1991-1",
    "hced-Inda Silase1989-1",
    "hced-Massawa1977-1",
    "hced-Massawa1990-1",
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
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Wave8EritreaTests(unittest.TestCase):
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
        new_entity_ids = {str(item["id"]) for item in WAVE8_ERITREA_ENTITIES}
        entities = {
            str(item["id"]): item
            for item in self.release_entities
            if str(item["id"]) not in new_entity_ids
        }
        install_wave8_eritrea_entities(entities)

        new_source_ids = {str(item["id"]) for item in WAVE8_ERITREA_SOURCES}
        sources = {
            str(item["id"]): item
            for item in self.release_sources
            if str(item["id"]) not in new_source_ids
        }
        install_wave8_eritrea_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_ERITREA_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return promote_wave8_eritrea_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_locked_queue_hashes_are_exact(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            WAVE8_ERITREA_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            WAVE8_ERITREA_IWBD_QUEUE_SHA256,
        )

    def test_complete_exact_label_inventory_is_eight_rows(self) -> None:
        exact = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "eritrea"
            or normalize_label(row.get("side_2_raw")) == "eritrea"
        }
        self.assertEqual(set(exact), set(EXPECTED_EXACT_ROWS))
        self.assertEqual(set(exact), WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS)
        for candidate_id, expected in EXPECTED_EXACT_ROWS.items():
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

    def test_exact_inventory_partitions_new_and_existing_owners(self) -> None:
        self.assertEqual(len(WAVE8_ERITREA_CONTRACT_IDS), 4)
        self.assertEqual(len(WAVE8_ERITREA_EXISTING_RELEASE_IDS), 4)
        self.assertFalse(WAVE8_ERITREA_CONTRACT_IDS & WAVE8_ERITREA_EXISTING_RELEASE_IDS)
        self.assertEqual(
            WAVE8_ERITREA_CONTRACT_IDS | WAVE8_ERITREA_EXISTING_RELEASE_IDS,
            WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(WAVE8_ERITREA_RESERVED_IDS, WAVE8_ERITREA_CONTRACT_IDS)
        self.assertEqual(WAVE8_ERITREA_UNRESOLVED_IDS, WAVE8_ERITREA_RESERVED_IDS)
        self.assertEqual(WAVE8_ERITREA_HOLDS, {})
        self.assertEqual(WAVE8_ERITREA_HOLD_IDS, frozenset())
        self.assertEqual(WAVE8_ERITREA_TERMINAL_EXCLUSIONS, {})
        self.assertEqual(WAVE8_ERITREA_TERMINAL_EXCLUSION_IDS, frozenset())
        self.assertIs(WAVE8_ERITREA_EXCLUSIONS, WAVE8_ERITREA_TERMINAL_EXCLUSIONS)
        self.assertIs(
            WAVE8_ERITREA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
            WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS,
        )
        self.assertIs(
            WAVE8_ERITREA_EXTERNAL_OWNER_DISPOSITIONS,
            WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS,
        )
        self.assertEqual(WAVE8_ERITREA_EXTERNAL_OWNER_IDS, WAVE8_ERITREA_EXISTING_RELEASE_IDS)

    def test_adjacent_rebel_and_ethiopian_rows_are_explicitly_outside_lane(self) -> None:
        self.assertEqual(
            set(WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS),
            EXPECTED_RELATED_HCED_IDS,
        )
        self.assertEqual(WAVE8_ERITREA_RELATED_HCED_IDS, EXPECTED_RELATED_HCED_IDS)
        self.assertEqual(
            WAVE8_ERITREA_REVIEWED_CANDIDATE_IDS,
            WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS | EXPECTED_RELATED_HCED_IDS,
        )
        self.assertTrue(
            WAVE8_ERITREA_RELATED_HCED_IDS.isdisjoint(WAVE8_ERITREA_RESERVED_IDS)
        )
        eritrean_rebels = {
            str(row["candidate_id"])
            for row in self.hced_rows
            if "eritrean rebels"
            in {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
        }
        self.assertEqual(
            eritrean_rebels,
            {
                "hced-Assab1991-1",
                "hced-Dekemhare1990-1991-1",
                "hced-Massawa1977-1",
                "hced-Massawa1990-1",
            },
        )
        for item in WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS.values():
            self.assertEqual(item["disposition"], "outside_exact_eritrea_lane")
            self.assertTrue(item["actor_boundary"])
            self.assertNotIn("side_1_entity_ids", item)
            self.assertNotIn("winner_side", item)
        self.assertEqual(
            WAVE8_ERITREA_CROSS_LANE_DISPOSITIONS,
            WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS,
        )

    def test_all_reviewed_hced_fingerprints_are_pinned(self) -> None:
        self.assertEqual(
            set(WAVE8_ERITREA_ROW_HASHES),
            WAVE8_ERITREA_REVIEWED_CANDIDATE_IDS,
        )
        for candidate_id, expected in WAVE8_ERITREA_ROW_HASHES.items():
            self.assertEqual(
                canonical_hced_row_sha256(self.hced_by_id[candidate_id]),
                expected,
            )
        for candidate_id, contract in WAVE8_ERITREA_CONTRACTS.items():
            self.assertEqual(contract["raw_row_sha256"], WAVE8_ERITREA_ROW_HASHES[candidate_id])
        for candidate_id, item in WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS.items():
            self.assertEqual(item["raw_row_sha256"], WAVE8_ERITREA_ROW_HASHES[candidate_id])
        for candidate_id, item in WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS.items():
            self.assertEqual(item["raw_row_sha256"], WAVE8_ERITREA_ROW_HASHES[candidate_id])

    def test_signature_is_independently_reproducible(self) -> None:
        payload = {
            "contracts": WAVE8_ERITREA_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "entities": WAVE8_ERITREA_ENTITIES,
            "existing_release_dispositions": WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS,
            "expected_candidate_ids": sorted(WAVE8_ERITREA_EXPECTED_CANDIDATE_IDS),
            "hced_queue_sha256": WAVE8_ERITREA_HCED_QUEUE_SHA256,
            "holds": WAVE8_ERITREA_HOLDS,
            "integration_dispositions": WAVE8_ERITREA_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_queue_sha256": WAVE8_ERITREA_IWBD_QUEUE_SHA256,
            "iwbd_zero_overlap_audit": WAVE8_ERITREA_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": WAVE8_ERITREA_LOCATION_QUARANTINE_REASONS,
            "outcome_overrides": WAVE8_ERITREA_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS
            ),
            "related_hced_dispositions": WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS,
            "related_iwbd_dispositions": WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS,
            "row_hashes": WAVE8_ERITREA_ROW_HASHES,
            "sources": WAVE8_ERITREA_SOURCES,
            "terminal_exclusions": WAVE8_ERITREA_TERMINAL_EXCLUSIONS,
        }
        measured = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        self.assertEqual(measured, WAVE8_ERITREA_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(measured, wave8_eritrea_audit_signature())
        self.assertEqual(len(measured), 64)

    def test_counts_and_cohorts_are_exact(self) -> None:
        self.assertEqual(
            wave8_eritrea_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 7,
                "exact_label_rows": 8,
                "existing_release_dispositions": 4,
                "external_owner_contracts": 4,
                "holds": 0,
                "integration_dispositions": 16,
                "iwbd_duplicate_dispositions": 4,
                "iwbd_related_dispositions": 1,
                "iwbd_zero_overlap_candidates": 4,
                "new_entities": 4,
                "new_sources": 16,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "related_hced_dispositions": 7,
                "reviewed_hced_rows": 15,
                "terminal_exclusions": 0,
                "unresolved_exact_label_rows": 4,
            },
        )
        self.assertEqual(
            wave8_eritrea_cohort_counts(),
            {
                "eplf_afabet_1988": 1,
                "eplf_barentu_capture_1985": 1,
                "eplf_nakfa_defensive_front_1977_1988": 1,
                "ethiopian_keren_offensive_1977_1978": 1,
            },
        )

    def test_sources_parse_are_independent_and_all_consumed(self) -> None:
        source_by_id = {str(item["id"]): item for item in WAVE8_ERITREA_SOURCES}
        families = {str(item["source_family_id"]) for item in WAVE8_ERITREA_SOURCES}
        self.assertEqual(len(source_by_id), 16)
        self.assertEqual(len(families), 16)
        for source in WAVE8_ERITREA_SOURCES:
            parsed = Source.from_dict(source)
            self.assertEqual(parsed.id, source["id"])
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertEqual(source["evidence_roles"], sorted(set(source["evidence_roles"])))
        types = {str(item["source_type"]) for item in WAVE8_ERITREA_SOURCES}
        self.assertTrue(any("peer_reviewed" in item for item in types))
        self.assertTrue(any("united_nations" in item or "un_" in item for item in types))
        self.assertTrue(any("declassified" in item for item in types))
        self.assertTrue(any("arbitral" in item for item in types))

        used: set[str] = set()
        for entity in WAVE8_ERITREA_ENTITIES:
            used.update(map(str, entity["source_ids"]))
        for contract in WAVE8_ERITREA_CONTRACTS.values():
            used.update(map(str, contract["evidence_refs"]))
        for inventory in (
            WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS,
            WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS,
            WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS,
            WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS,
        ):
            for item in inventory.values():
                used.update(map(str, item["evidence_refs"]))
        self.assertEqual(used, set(source_by_id))

    def test_four_entities_are_bounded_eplf_formations_never_state_bridges(self) -> None:
        expected_windows = {
            KEREN_EPLF_ID: (1977, 1978),
            NAKFA_EPLF_ID: (1977, 1988),
            BARENTU_EPLF_ID: (1985, 1985),
            AFABET_EPLF_ID: (1988, 1988),
        }
        entities = {str(item["id"]): item for item in WAVE8_ERITREA_ENTITIES}
        self.assertEqual(set(entities), set(expected_windows))
        self.assertNotIn(STATE_ERITREA_ID, entities)
        for entity_id, fixture in entities.items():
            parsed = Entity.from_dict(fixture)
            self.assertEqual((parsed.start_year, parsed.end_year), expected_windows[entity_id])
            self.assertEqual(fixture["aliases"], [])
            self.assertEqual(fixture["predecessors"], [])
            note = fixture["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("state of eritrea", note)
            self.assertIn("generic eritrean rebels", note)
            self.assertIn("elf", note)

    def test_contracts_preserve_raw_outcomes_and_use_independent_sources(self) -> None:
        source_by_id = {str(item["id"]): item for item in WAVE8_ERITREA_SOURCES}
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            row = self.hced_by_id[candidate_id]
            contract = WAVE8_ERITREA_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            winner_side = contract["winner_side"]
            self.assertEqual(row["winner_raw"], row[f"side_{winner_side}_raw"])
            self.assertEqual(row["loser_raw"], row[f"side_{3 - winner_side}_raw"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertTrue(contract["actor_override"])
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(canonical["name"], expected["name"])
            self.assertEqual(
                (canonical["year_low"], canonical["year_high"]),
                expected["years"],
            )
            self.assertEqual(canonical["granularity"], expected["event_type"])
            self.assertEqual(canonical["date_precision"], expected["date_precision"])
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
            self.assertTrue(set(contract["outcome_source_ids"]) <= set(contract["evidence_refs"]))
            expected_families = sorted(
                {
                    source_by_id[source_id]["source_family_id"]
                    for source_id in contract["outcome_source_ids"]
                }
            )
            self.assertEqual(contract["outcome_source_family_ids"], expected_families)
            self.assertGreaterEqual(len(expected_families), 2)
        self.assertEqual(WAVE8_ERITREA_OUTCOME_OVERRIDES, {})

    def test_pre_independence_contracts_never_use_state_of_eritrea(self) -> None:
        new_entity_ids = {str(item["id"]) for item in WAVE8_ERITREA_ENTITIES}
        consumed: set[str] = set()
        for contract in WAVE8_ERITREA_CONTRACTS.values():
            participants = set(contract["side_1_entity_ids"]) | set(
                contract["side_2_entity_ids"]
            )
            self.assertNotIn(STATE_ERITREA_ID, participants)
            self.assertIn(ETHIOPIA_ID, participants)
            self.assertEqual(len(participants & new_entity_ids), 1)
            consumed.update(participants & new_entity_ids)
        self.assertEqual(consumed, new_entity_ids)

    def test_existing_state_rows_and_winners_are_pinned(self) -> None:
        expected = {
            "hced-Badme1998-1": STATE_ERITREA_ID,
            "hced-Badme1999-1": ETHIOPIA_ID,
            "hced-Barentu2000-1": ETHIOPIA_ID,
            "hced-Tsorona1999-1": STATE_ERITREA_ID,
        }
        for candidate_id, winner_id in expected.items():
            disposition = WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS[candidate_id]
            matches = [
                event
                for event in self.release_events
                if event.get("hced_candidate_id") == candidate_id
            ]
            self.assertEqual(len(matches), 1)
            event = matches[0]
            self.assertEqual(event["id"], disposition["owner_event_id"])
            participants = {item["entity_id"] for item in event["participants"]}
            winners = {
                item["entity_id"]
                for item in event["participants"]
                if "victory" in item["termination"]
            }
            self.assertEqual(participants, {ETHIOPIA_ID, STATE_ERITREA_ID})
            self.assertEqual(winners, {winner_id})
            self.assertEqual(disposition["reviewed_winner_id"], winner_id)

    def test_iwbd_duplicates_and_opposite_result_badme_action_are_explicit(self) -> None:
        expected_duplicates = {
            "iwbd-219-84-1691": ("Badme 1", "Eritrea"),
            "iwbd-219-84-1693": ("Badme 2 (b)", "Ethiopia"),
            "iwbd-219-84-1694": ("Tsorona", "Eritrea"),
            "iwbd-219-84-1695": ("Barentu", "Ethiopia"),
        }
        self.assertEqual(set(WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS), set(expected_duplicates))
        for candidate_id, expected in expected_duplicates.items():
            row = self.iwbd_by_id[candidate_id]
            item = WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS[candidate_id]
            self.assertEqual((row["name"], row["winner_raw"]), expected)
            self.assertEqual(row["name"], item["expected_name"])
            self.assertEqual(row["winner_raw"], item["expected_winner_raw"])
            self.assertIn(item["owner_hced_candidate_id"], WAVE8_ERITREA_EXISTING_RELEASE_IDS)

        self.assertEqual(set(WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS), {"iwbd-219-84-1692"})
        related = WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS["iwbd-219-84-1692"]
        row = self.iwbd_by_id["iwbd-219-84-1692"]
        self.assertEqual((row["name"], row["winner_raw"]), ("Badme 2 (a)", "Eritrea"))
        self.assertEqual(related["disposition"], "related_but_distinct_operation")
        self.assertEqual(related["not_owner_hced_candidate_id"], "hced-Badme1999-1")
        self.assertNotEqual(
            related["expected_winner_raw"],
            self.hced_by_id["hced-Badme1999-1"]["winner_raw"],
        )

    def test_queue_and_integration_validators_return_exact_counts(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            validate_wave8_eritrea_queue_contracts(self.hced_rows),
            {
                "existing_release_dispositions": 4,
                "holds": 0,
                "promotion_contracts": 4,
                "related_hced_dispositions": 7,
                "reviewed_exact_label_rows": 8,
                "reviewed_hced_rows": 15,
                "terminal_exclusions": 0,
                "unresolved_exact_label_rows": 4,
            },
        )
        self.assertEqual(
            validate_wave8_eritrea_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "existing_release_dispositions": 4,
                "integration_dispositions": 16,
                "iwbd_duplicate_dispositions": 4,
                "iwbd_probable_twins": 0,
                "iwbd_related_dispositions": 1,
                "iwbd_zero_overlap_candidates": 4,
                "related_hced_dispositions": 7,
            },
        )

    def test_integration_fails_closed_on_owner_or_iwbd_drift(self) -> None:
        _, _, existing = self._installed()
        missing_badme = [
            event
            for event in existing
            if event.get("hced_candidate_id") != "hced-Badme1998-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one event"):
            validate_wave8_eritrea_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                missing_badme,
            )

        changed_owner = copy.deepcopy(existing)
        badme = next(
            event
            for event in changed_owner
            if event.get("hced_candidate_id") == "hced-Badme1998-1"
        )
        badme["participants"][0]["entity_id"] = "fabricated_actor"
        with self.assertRaisesRegex(ValueError, "participants changed"):
            validate_wave8_eritrea_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                changed_owner,
            )

        changed_iwbd = copy.deepcopy(self.iwbd_rows)
        row = next(item for item in changed_iwbd if item["candidate_id"] == "iwbd-219-84-1694")
        row["winner_raw"] = "Unknown"
        with self.assertRaisesRegex(ValueError, "IWBD disposition changed"):
            validate_wave8_eritrea_integration_dispositions(
                self.hced_rows,
                changed_iwbd,
                existing,
            )

        future_twin = [
            *self.iwbd_rows,
            {
                "candidate_id": "iwbd-future-afabet",
                "name": "Battle of Afabet",
                "start_date": "1988-03-17",
                "end_date": "1988-03-19",
            },
        ]
        with self.assertRaisesRegex(ValueError, "undeclared probable IWBD twin"):
            validate_wave8_eritrea_integration_dispositions(
                self.hced_rows,
                future_twin,
                existing,
            )

    def test_emits_four_events_with_campaigns_kept_operational(self) -> None:
        events = self._events()
        by_candidate = {str(item["hced_candidate_id"]): item for item in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_PROMOTIONS))
        self.assertEqual(len({item["id"] for item in events}), 4)
        self.assertEqual(len({item["canonical_event_key"] for item in events}), 4)
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            event = by_candidate[candidate_id]
            parsed = Event.from_dict(event)
            self.assertEqual(parsed.event_type, expected["event_type"])
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["name"], expected["name"])
            self.assertEqual((event["year"], event["end_year"]), expected["years"])
            self.assertEqual(event["event_type"], expected["event_type"])
            self.assertEqual(event["reviewed_granularity"], expected["event_type"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["date_precision"], expected["date_precision"])
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
            self.assertEqual(winners, {expected["winner"]})
            self.assertEqual(losers, {expected["loser"]})
            if expected["event_type"] == "campaign":
                self.assertEqual(
                    {item["termination"] for item in event["participants"]},
                    {"campaign_victory", "campaign_defeat"},
                )
                self.assertIn("operational campaign", event["summary"])
                self.assertNotIn("tactical assertion", event["summary"])
            else:
                self.assertEqual(
                    {item["termination"] for item in event["participants"]},
                    {"engagement_victory", "engagement_defeat"},
                )

    def test_unknown_is_never_draw_and_no_override_is_invented(self) -> None:
        for contract in WAVE8_ERITREA_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
        for event in self._events():
            terminations = {item["termination"] for item in event["participants"]}
            self.assertTrue(any("victory" in item for item in terminations))
            self.assertTrue(any("defeat" in item for item in terminations))
            self.assertFalse(any("draw" in item or "inconclusive" in item for item in terminations))
        self.assertEqual(WAVE8_ERITREA_OUTCOME_OVERRIDES, {})

    def test_all_new_points_are_locally_withheld_and_country_is_retained(self) -> None:
        point_before = set(HCED_POINT_QUARANTINE_IDS)
        country_before = set(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS, WAVE8_ERITREA_CONTRACT_IDS)
        self.assertEqual(WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            WAVE8_ERITREA_LOCATION_QUARANTINE_ADDITIONS,
            {"point": WAVE8_ERITREA_CONTRACT_IDS, "country": frozenset()},
        )
        self.assertEqual(
            wave8_eritrea_location_quarantine_additions(),
            {"country": frozenset(), "point": WAVE8_ERITREA_CONTRACT_IDS},
        )
        self.assertEqual(set(WAVE8_ERITREA_LOCATION_QUARANTINE_REASONS), WAVE8_ERITREA_CONTRACT_IDS)
        events = self._events()
        self.assertEqual(set(HCED_POINT_QUARANTINE_IDS), point_before)
        self.assertEqual(set(HCED_COUNTRY_QUARANTINE_IDS), country_before)
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Eritrea")
            self.assertIn("location_provenance", event)
        for candidate_id in WAVE8_ERITREA_EXISTING_RELEASE_IDS:
            self.assertNotIn(candidate_id, WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS)

    def test_installers_are_idempotent_copy_and_collision_safe(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        install_wave8_eritrea_entities(entities)
        install_wave8_eritrea_sources(sources)
        expected_entities = copy.deepcopy(entities)
        expected_sources = copy.deepcopy(sources)
        install_wave8_eritrea_entities(entities)
        install_wave8_eritrea_sources(sources)
        self.assertEqual(entities, expected_entities)
        self.assertEqual(sources, expected_sources)

        entity_id = str(WAVE8_ERITREA_ENTITIES[0]["id"])
        source_id = str(WAVE8_ERITREA_SOURCES[0]["id"])
        entities[entity_id]["name"] = "tampered"
        sources[source_id]["title"] = "tampered"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_eritrea_entities(entities)
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_eritrea_sources(sources)

    def test_promotion_requires_exact_entity_windows_and_no_duplicate_owner(self) -> None:
        entities, _, existing = self._installed()
        missing = copy.deepcopy(entities)
        del missing[AFABET_EPLF_ID]
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_eritrea_contracts(self.hced_rows, missing, existing)

        wrong_window = copy.deepcopy(entities)
        wrong_window[NAKFA_EPLF_ID]["start_year"] = 1978
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_eritrea_contracts(self.hced_rows, wrong_window, existing)

        events = promote_wave8_eritrea_contracts(self.hced_rows, entities, existing)
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_eritrea_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_eritrea_contracts(
                self.hced_rows,
                entities,
                [*existing, {"name": "Battle of Afabet", "year": 1988}],
            )

    def test_queue_fingerprint_or_inventory_drift_fails_closed(self) -> None:
        changed = copy.deepcopy(self.hced_rows)
        row = next(item for item in changed if item["candidate_id"] == "hced-Afabet1988-1")
        row["winner_raw"] = "Draw"
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            validate_wave8_eritrea_queue_contracts(changed)

        missing = [
            row
            for row in self.hced_rows
            if row["candidate_id"] != "hced-Barentu1985-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_eritrea_queue_contracts(missing)

        extra = [
            *self.hced_rows,
            {
                **copy.deepcopy(self.hced_by_id["hced-Afabet1988-1"]),
                "candidate_id": "hced-FutureEritrea1987-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact Eritrea inventory changed"):
            validate_wave8_eritrea_queue_contracts(extra)

    def test_integration_disposition_union_is_complete(self) -> None:
        expected_keys = {
            *(
                f"existing_release:{key}"
                for key in WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS
            ),
            *(
                f"related_hced:{key}"
                for key in WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS
            ),
            *(
                f"iwbd_duplicate:{key}"
                for key in WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS
            ),
            *(
                f"iwbd_related:{key}"
                for key in WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS
            ),
        }
        self.assertEqual(set(WAVE8_ERITREA_INTEGRATION_DISPOSITIONS), expected_keys)
        self.assertEqual(len(expected_keys), 16)
        self.assertEqual(WAVE8_ERITREA_HCED_DUPLICATE_DISPOSITIONS, {})

    def test_public_api_exposes_lane_and_integration_contracts(self) -> None:
        module = __import__(
            "military_elo.promotion.wave8_eritrea",
            fromlist=["__all__"],
        )
        required = {
            "WAVE8_ERITREA_CONTRACTS",
            "WAVE8_ERITREA_COUNTRY_QUARANTINE_ADDITIONS",
            "WAVE8_ERITREA_ENTITIES",
            "WAVE8_ERITREA_EXISTING_RELEASE_DISPOSITIONS",
            "WAVE8_ERITREA_FINAL_AUDIT_SIGNATURE",
            "WAVE8_ERITREA_INTEGRATION_DISPOSITIONS",
            "WAVE8_ERITREA_IWBD_DUPLICATE_DISPOSITIONS",
            "WAVE8_ERITREA_IWBD_ZERO_OVERLAP_AUDIT",
            "WAVE8_ERITREA_POINT_QUARANTINE_ADDITIONS",
            "WAVE8_ERITREA_RELATED_HCED_DISPOSITIONS",
            "WAVE8_ERITREA_RELATED_IWBD_DISPOSITIONS",
            "WAVE8_ERITREA_RESERVED_IDS",
            "WAVE8_ERITREA_SOURCES",
            "install_wave8_eritrea_entities",
            "install_wave8_eritrea_sources",
            "promote_wave8_eritrea_contracts",
            "validate_wave8_eritrea_integration_dispositions",
            "validate_wave8_eritrea_queue_contracts",
            "wave8_eritrea_audit_signature",
            "wave8_eritrea_counts",
        }
        self.assertTrue(required <= set(module.__all__))


if __name__ == "__main__":
    unittest.main()
