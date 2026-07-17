from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_mamluk_egypt import (
    WAVE8_MAMLUK_EGYPT_CONTRACT_IDS,
    WAVE8_MAMLUK_EGYPT_CONTRACTS,
    WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS,
    WAVE8_MAMLUK_EGYPT_CROSS_LANE_IDS,
    WAVE8_MAMLUK_EGYPT_ENTITIES,
    WAVE8_MAMLUK_EGYPT_EXCLUSIONS,
    WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS,
    WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_IDS,
    WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS,
    WAVE8_MAMLUK_EGYPT_FINAL_AUDIT_SIGNATURE,
    WAVE8_MAMLUK_EGYPT_HOLD_IDS,
    WAVE8_MAMLUK_EGYPT_HOLDS,
    WAVE8_MAMLUK_EGYPT_INTEGRATION_DISPOSITIONS,
    WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_MAMLUK_EGYPT_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_MAMLUK_EGYPT_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_MAMLUK_EGYPT_OUTCOME_OVERRIDES,
    WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS,
    WAVE8_MAMLUK_EGYPT_RESERVED_IDS,
    WAVE8_MAMLUK_EGYPT_REVIEWED_CANDIDATE_IDS,
    WAVE8_MAMLUK_EGYPT_SOURCES,
    WAVE8_MAMLUK_EGYPT_TERMINAL_EXCLUSION_IDS,
    WAVE8_MAMLUK_EGYPT_UNRESOLVED_IDS,
    install_wave8_mamluk_egypt_entities,
    install_wave8_mamluk_egypt_sources,
    promote_wave8_mamluk_egypt_contracts,
    validate_wave8_mamluk_egypt_integration_dispositions,
    validate_wave8_mamluk_egypt_queue_contracts,
    wave8_mamluk_egypt_audit_signature,
    wave8_mamluk_egypt_cohort_counts,
    wave8_mamluk_egypt_counts,
    wave8_mamluk_egypt_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_mamluk_egypt_"

EXPECTED_HASHES = {
    "hced-Alexandria1798-1": (
        "9e6416b28654cf8894fd1af4fdbfe597eca128709375e06b6d6d50df33f66386"
    ),
    "hced-Er Ridisiya1799-1": (
        "f685fa5a0156beeadb7a5012ca429bdb3ad89b5afd93dfe732dbc9c7035d4363"
    ),
    "hced-Marj Dabik1516-1": (
        "0eb60113f47e6f8f89cf6f4d7c016e1fc6c35cbe80efc459d9a871d31cfb2fc6"
    ),
    "hced-Mount Tabor1799-1": (
        "3a01784e5f849b2e5bc53f3943f6150f59f8f9d572415c1d370bbb7de102fa2a"
    ),
    "hced-Rahmaniyya1786-1": (
        "460d690c31cc52c7743bbb8e112e8048df1d72ac07f53175bfd53c921ab065db"
    ),
    "hced-Ridanieh1517-1": (
        "260940e4918a9eb6c58cf7167e21ab665751a0668678db421abba26ef30072f7"
    ),
    "hced-Samhud1799-1": (
        "7ec8600f16e89fd6efbbbffacf2663e272fa7a2d6ee1c5663e8f8daee9693b2d"
    ),
    "hced-Sediman1798-1": (
        "d51eabdd58fb3cd1293e8d320590eaee927fe5a007abc7c49ff518366741812f"
    ),
    "hced-Shubra Khit1798-1": (
        "6dc896a596bc505f61b01a80a5880f0e1e1cab683feafbf436b75baea7f37120"
    ),
}

EXPECTED_LITERAL_ROWS = {
    "hced-Alexandria1798-1": ("France", "Mamluk Egypt", "France", 1798),
    "hced-Er Ridisiya1799-1": ("France", "Mamluk Egypt", "France", 1799),
    "hced-Marj Dabik1516-1": (
        "Ottoman Empire",
        "Mamluk Egypt",
        "Ottoman Empire",
        1516,
    ),
    "hced-Rahmaniyya1786-1": (
        "Ottoman Empire",
        "Mamluk Egypt",
        "Ottoman Empire",
        1786,
    ),
    "hced-Ridanieh1517-1": (
        "Ottoman Empire",
        "Mamluk Egypt",
        "Ottoman Empire",
        1517,
    ),
    "hced-Samhud1799-1": ("France", "Mamluk Egypt", "France", 1799),
    "hced-Sediman1798-1": ("France", "Mamluk Egypt", "France", 1798),
    "hced-Shubra Khit1798-1": ("France", "Mamluk Egypt", "France", 1798),
}

EXPECTED_PROMOTIONS = {
    "hced-Rahmaniyya1786-1": {
        "date_precision": "year",
        "date_text": "1786 (the reviewed sources do not securely identify a day)",
        "loser": "murad_bey_rahmaniyya_force_1786",
        "name": "Battle of Rahmaniyya",
        "winner": "ottoman_empire",
        "year": 1786,
    },
    "hced-Shubra Khit1798-1": {
        "date_precision": "day_conflict",
        "date_text": "13-14 July 1798 (source chronologies differ by one day)",
        "loser": "murad_bey_egypt_campaign_force_1798",
        "name": "Battle of Shubra Khit",
        "winner": "french_first_republic",
        "year": 1798,
    },
    "hced-Sediman1798-1": {
        "date_precision": "day_conflict",
        "date_text": "7-8 October 1798 (source chronologies differ by one day)",
        "loser": "murad_bey_egypt_campaign_force_1798",
        "name": "Battle of Sediman",
        "winner": "french_first_republic",
        "year": 1798,
    },
    "hced-Samhud1799-1": {
        "date_precision": "day",
        "date_text": "22 January 1799",
        "loser": "murad_bey_samhud_coalition_1799",
        "name": "Battle of Samhud",
        "winner": "french_first_republic",
        "year": 1799,
    },
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue unavailable: {path}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Wave8MamlukEgyptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.rows_by_id = {
            str(row["candidate_id"]): row
            for row in cls.hced_rows
            if row.get("candidate_id") in WAVE8_MAMLUK_EGYPT_REVIEWED_CANDIDATE_IDS
        }

    def _installed(self):
        new_entity_ids = {
            str(entity["id"]) for entity in WAVE8_MAMLUK_EGYPT_ENTITIES
        }
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        install_wave8_mamluk_egypt_entities(entities)

        new_source_ids = {
            str(source["id"]) for source in WAVE8_MAMLUK_EGYPT_SOURCES
        }
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        install_wave8_mamluk_egypt_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_MAMLUK_EGYPT_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return promote_wave8_mamluk_egypt_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_full_literal_inventory_and_integration_partitions_are_exact(self) -> None:
        literal_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Mamluk Egypt"
            or row.get("side_2_raw") == "Mamluk Egypt"
        }
        self.assertEqual(set(literal_rows), set(EXPECTED_LITERAL_ROWS))
        self.assertEqual(
            WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS,
            frozenset(EXPECTED_LITERAL_ROWS),
        )
        self.assertEqual(
            WAVE8_MAMLUK_EGYPT_RESERVED_IDS,
            WAVE8_MAMLUK_EGYPT_CONTRACT_IDS | WAVE8_MAMLUK_EGYPT_HOLD_IDS,
        )
        self.assertEqual(
            WAVE8_MAMLUK_EGYPT_RESERVED_IDS,
            WAVE8_MAMLUK_EGYPT_UNRESOLVED_IDS,
        )
        self.assertEqual(len(WAVE8_MAMLUK_EGYPT_RESERVED_IDS), 6)
        self.assertEqual(
            WAVE8_MAMLUK_EGYPT_RESERVED_IDS
            | WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_IDS,
            WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            WAVE8_MAMLUK_EGYPT_CROSS_LANE_IDS,
            frozenset({"hced-Mount Tabor1799-1"}),
        )
        self.assertTrue(
            WAVE8_MAMLUK_EGYPT_CROSS_LANE_IDS.isdisjoint(
                WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS
            )
        )
        self.assertEqual(
            WAVE8_MAMLUK_EGYPT_REVIEWED_CANDIDATE_IDS,
            frozenset(EXPECTED_HASHES),
        )
        for candidate_id, expected in EXPECTED_LITERAL_ROWS.items():
            row = literal_rows[candidate_id]
            self.assertEqual(
                (
                    row["side_1_raw"],
                    row["side_2_raw"],
                    row["winner_raw"],
                    row["year_best"],
                ),
                expected,
            )
        mount_tabor = self.rows_by_id["hced-Mount Tabor1799-1"]
        self.assertEqual(mount_tabor["side_2_raw"], "Turkey, Mamluk Egypt")

    def test_queue_validation_counts_all_six_unresolved_rows(self) -> None:
        self.assertEqual(
            validate_wave8_mamluk_egypt_queue_contracts(self.hced_rows),
            {
                "cross_lane_hced_dispositions": 1,
                "existing_release_dispositions": 2,
                "holds": 2,
                "promotion_contracts": 4,
                "reviewed_exact_label_rows": 8,
                "reviewed_hced_rows": 9,
                "unresolved_exact_label_rows": 6,
            },
        )

    def test_every_reviewed_row_is_canonically_hash_pinned(self) -> None:
        dispositions = {
            **WAVE8_MAMLUK_EGYPT_CONTRACTS,
            **WAVE8_MAMLUK_EGYPT_HOLDS,
            **WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS,
            **WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS,
        }
        self.assertEqual(set(dispositions), set(EXPECTED_HASHES))
        for candidate_id, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(candidate_id=candidate_id):
                row = self.rows_by_id[candidate_id]
                self.assertEqual(canonical_hced_row_sha256(row), expected_hash)
                self.assertEqual(
                    dispositions[candidate_id]["raw_row_sha256"],
                    expected_hash,
                )

    def test_hash_changes_duplicates_missing_rows_and_new_labels_fail_closed(self) -> None:
        for candidate_id in sorted(WAVE8_MAMLUK_EGYPT_REVIEWED_CANDIDATE_IDS):
            with self.subTest(candidate_id=candidate_id):
                tampered = copy.deepcopy(self.hced_rows)
                row = next(
                    item for item in tampered if item.get("candidate_id") == candidate_id
                )
                row["name"] = f"{row['name']} changed"
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_mamluk_egypt_queue_contracts(tampered)

        duplicate = [*self.hced_rows, copy.deepcopy(self.rows_by_id["hced-Samhud1799-1"])]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_mamluk_egypt_queue_contracts(duplicate)

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Alexandria1798-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_mamluk_egypt_queue_contracts(missing)

        future = [
            *self.hced_rows,
            {
                "candidate_id": "hced-FutureMamlukEgypt1800-1",
                "side_1_raw": "France",
                "side_2_raw": "Mamluk Egypt",
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            validate_wave8_mamluk_egypt_queue_contracts(future)

    def test_immutable_signature_counts_and_cohorts_are_independent(self) -> None:
        payload = {
            "contracts": WAVE8_MAMLUK_EGYPT_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_MAMLUK_EGYPT_ENTITIES,
            "existing_release_dispositions": (
                WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                WAVE8_MAMLUK_EGYPT_EXPECTED_CANDIDATE_IDS
            ),
            "holds": WAVE8_MAMLUK_EGYPT_HOLDS,
            "integration_dispositions": WAVE8_MAMLUK_EGYPT_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": (
                WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": WAVE8_MAMLUK_EGYPT_IWBD_ZERO_OVERLAP_AUDIT,
            "outcome_overrides": WAVE8_MAMLUK_EGYPT_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS
            ),
            "reserved_ids": sorted(WAVE8_MAMLUK_EGYPT_RESERVED_IDS),
            "sources": WAVE8_MAMLUK_EGYPT_SOURCES,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent, WAVE8_MAMLUK_EGYPT_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_mamluk_egypt_audit_signature(), independent)
        self.assertEqual(
            wave8_mamluk_egypt_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 1,
                "exact_label_rows": 8,
                "existing_release_dispositions": 2,
                "holds": 2,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 3,
                "new_sources": 8,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 9,
                "terminal_exclusions": 2,
                "unresolved_exact_label_rows": 6,
            },
        )
        self.assertEqual(
            wave8_mamluk_egypt_cohort_counts(),
            {
                "murad_bey_campaign_1798": 2,
                "murad_bey_samhud_coalition_1799": 1,
                "ottoman_rahmaniyya_1786": 1,
            },
        )

    def test_sources_parse_with_stable_families_and_exact_evidence_roles(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_MAMLUK_EGYPT_SOURCES
        }
        families = {
            str(source["source_family_id"])
            for source in WAVE8_MAMLUK_EGYPT_SOURCES
        }
        self.assertEqual(len(source_by_id), 8)
        self.assertEqual(len(families), 8)
        for source in WAVE8_MAMLUK_EGYPT_SOURCES:
            Source.from_dict(source)
            self.assertTrue(str(source["url"]).startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )

        outcome_ids = {
            source_id
            for contract in WAVE8_MAMLUK_EGYPT_CONTRACTS.values()
            for source_id in contract["outcome_source_ids"]
        }
        exclusion_ids = {
            source_id
            for hold in WAVE8_MAMLUK_EGYPT_HOLDS.values()
            for source_id in hold["evidence_refs"]
        }
        self.assertTrue(outcome_ids <= set(source_by_id))
        self.assertTrue(exclusion_ids <= set(source_by_id))
        self.assertTrue(
            all("outcome" in source_by_id[item]["evidence_roles"] for item in outcome_ids)
        )
        self.assertTrue(
            all(
                "identity_boundary_or_context_reference"
                in source_by_id[item]["evidence_roles"]
                for item in exclusion_ids
            )
        )

    def test_three_new_entities_are_narrow_time_bounded_and_nonheritable(self) -> None:
        expected_windows = {
            "murad_bey_rahmaniyya_force_1786": (1786, 1786),
            "murad_bey_egypt_campaign_force_1798": (1798, 1798),
            "murad_bey_samhud_coalition_1799": (1799, 1799),
        }
        entity_by_id = {
            str(entity["id"]): entity for entity in WAVE8_MAMLUK_EGYPT_ENTITIES
        }
        self.assertEqual(set(entity_by_id), set(expected_windows))
        for entity_id, entity in entity_by_id.items():
            Entity.from_dict(entity)
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                expected_windows[entity_id],
            )
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
        self.assertTrue(
            set(entity_by_id).isdisjoint(
                {
                    "egypt_muhammad_ali",
                    "mamluk_egyptian_forces_1798",
                    "mamluk_sultanate",
                }
            )
        )

    def test_installers_are_idempotent_copy_and_reject_collisions(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        install_wave8_mamluk_egypt_entities(entities)
        install_wave8_mamluk_egypt_sources(sources)
        expected_entities = copy.deepcopy(entities)
        expected_sources = copy.deepcopy(sources)
        install_wave8_mamluk_egypt_entities(entities)
        install_wave8_mamluk_egypt_sources(sources)
        self.assertEqual(entities, expected_entities)
        self.assertEqual(sources, expected_sources)

        first_entity = str(WAVE8_MAMLUK_EGYPT_ENTITIES[0]["id"])
        first_source = str(WAVE8_MAMLUK_EGYPT_SOURCES[0]["id"])
        entities[first_entity]["name"] = "tampered"
        sources[first_source]["title"] = "tampered"
        self.assertNotEqual(
            entities[first_entity]["name"],
            WAVE8_MAMLUK_EGYPT_ENTITIES[0]["name"],
        )
        self.assertNotEqual(
            sources[first_source]["title"],
            WAVE8_MAMLUK_EGYPT_SOURCES[0]["title"],
        )
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_mamluk_egypt_entities(entities)
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_mamluk_egypt_sources(sources)

    def test_contract_dates_sides_and_direct_outcome_provenance_are_exact(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_MAMLUK_EGYPT_SOURCES
        }
        forbidden = {
            "egypt_muhammad_ali",
            "mamluk_egyptian_forces_1798",
            "mamluk_sultanate",
        }
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            contract = WAVE8_MAMLUK_EGYPT_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            participants = set(contract["side_1_entity_ids"]) | set(
                contract["side_2_entity_ids"]
            )
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            self.assertTrue(contract["actor_override"])
            self.assertEqual(contract["side_1_entity_ids"], [expected["winner"]])
            self.assertEqual(contract["side_2_entity_ids"], [expected["loser"]])
            self.assertTrue(participants.isdisjoint(forbidden))
            self.assertEqual(canonical["name"], expected["name"])
            self.assertEqual(
                (canonical["year_low"], canonical["year_high"]),
                (expected["year"], expected["year"]),
            )
            self.assertEqual(canonical["date_precision"], expected["date_precision"])
            self.assertEqual(canonical["date_text"], expected["date_text"])
            self.assertEqual(
                contract["evidence_refs"],
                contract["outcome_source_ids"],
            )
            expected_families = sorted(
                {
                    source_by_id[source_id]["source_family_id"]
                    for source_id in contract["outcome_source_ids"]
                }
            )
            self.assertEqual(
                contract["outcome_source_family_ids"],
                expected_families,
            )
            self.assertGreaterEqual(len(expected_families), 2)

    def test_terminal_exclusions_are_explicit_hash_pinned_and_never_draws(self) -> None:
        self.assertIs(WAVE8_MAMLUK_EGYPT_EXCLUSIONS, WAVE8_MAMLUK_EGYPT_HOLDS)
        self.assertEqual(
            WAVE8_MAMLUK_EGYPT_TERMINAL_EXCLUSION_IDS,
            frozenset(
                {"hced-Alexandria1798-1", "hced-Er Ridisiya1799-1"}
            ),
        )
        forbidden_result_fields = {
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
        }
        for candidate_id, hold in WAVE8_MAMLUK_EGYPT_HOLDS.items():
            self.assertEqual(hold["disposition"], "terminal_exclusion")
            self.assertTrue(hold["terminal_exclusion"])
            self.assertTrue(forbidden_result_fields.isdisjoint(hold))
            self.assertEqual(
                hold["raw_row_sha256"],
                EXPECTED_HASHES[candidate_id],
            )
        alexandria = WAVE8_MAMLUK_EGYPT_HOLDS["hced-Alexandria1798-1"]
        self.assertEqual(
            alexandria["hold_category"],
            "terminal_exclusion_wrong_actor",
        )
        self.assertIn("Muhammad Karim", alexandria["hold_reason"])
        self.assertIn("not Murad Bey", alexandria["hold_reason"])
        ridisiya = WAVE8_MAMLUK_EGYPT_HOLDS["hced-Er Ridisiya1799-1"]
        self.assertEqual(
            ridisiya["hold_category"],
            "terminal_exclusion_noncompetitive_pursuit_attrition",
        )
        self.assertIn("did not catch", ridisiya["hold_reason"])
        self.assertIn("not converted into a draw", ridisiya["hold_reason"])
        self.assertEqual(WAVE8_MAMLUK_EGYPT_OUTCOME_OVERRIDES, {})

    def test_four_events_parse_and_have_only_victory_defeat_results(self) -> None:
        events = self._events()
        by_candidate = {
            str(event["hced_candidate_id"]): event for event in events
        }
        self.assertEqual(set(by_candidate), set(EXPECTED_PROMOTIONS))
        self.assertTrue(WAVE8_MAMLUK_EGYPT_HOLD_IDS.isdisjoint(by_candidate))
        self.assertTrue(WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_IDS.isdisjoint(by_candidate))
        self.assertTrue(WAVE8_MAMLUK_EGYPT_CROSS_LANE_IDS.isdisjoint(by_candidate))
        self.assertEqual(len({event["id"] for event in events}), 4)
        self.assertEqual(len({event["canonical_event_key"] for event in events}), 4)

        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            contract = WAVE8_MAMLUK_EGYPT_CONTRACTS[candidate_id]
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["name"], expected["name"])
            self.assertEqual(
                (event["year"], event["end_year"]),
                (expected["year"], expected["year"]),
            )
            self.assertEqual(event["date_precision"], expected["date_precision"])
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["status"], "complete")
            winners = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["termination"] == "engagement_victory"
            }
            losers = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["termination"] == "engagement_defeat"
            }
            terminations = {
                participant["termination"] for participant in event["participants"]
            }
            self.assertEqual(winners, {expected["winner"]})
            self.assertEqual(losers, {expected["loser"]})
            self.assertEqual(
                terminations,
                {"engagement_victory", "engagement_defeat"},
            )
            self.assertNotIn("inconclusive_engagement", terminations)
            self.assertEqual(
                event["source_ids"],
                ["hced_dataset", *contract["evidence_refs"]],
            )
            self.assertEqual(
                event["outcome_source_ids"],
                contract["outcome_source_ids"],
            )
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )

    def test_all_promoted_points_are_quarantined_but_egypt_country_is_retained(self) -> None:
        self.assertEqual(
            WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS,
            WAVE8_MAMLUK_EGYPT_CONTRACT_IDS,
        )
        self.assertEqual(WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            WAVE8_MAMLUK_EGYPT_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_MAMLUK_EGYPT_CONTRACT_IDS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            wave8_mamluk_egypt_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": WAVE8_MAMLUK_EGYPT_CONTRACT_IDS,
            },
        )
        for candidate_id in WAVE8_MAMLUK_EGYPT_CONTRACT_IDS:
            raw = self.rows_by_id[candidate_id]
            self.assertTrue(raw["latitude"])
            self.assertTrue(raw["longitude"])
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Egypt")
            self.assertEqual(
                event["location_provenance"]["assertion_status"],
                "unreviewed_source_assertion",
            )

    def test_iwbd_zero_overlap_and_existing_cross_lane_owners_validate(self) -> None:
        self.assertEqual(WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            WAVE8_MAMLUK_EGYPT_INTEGRATION_DISPOSITIONS,
            WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS,
        )
        self.assertEqual(
            set(WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS),
            {"hced-Mount Tabor1799-1"},
        )
        self.assertEqual(
            set(WAVE8_MAMLUK_EGYPT_EXISTING_RELEASE_DISPOSITIONS),
            {"hced-Marj Dabik1516-1", "hced-Ridanieh1517-1"},
        )
        self.assertEqual(
            validate_wave8_mamluk_egypt_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 1,
                "existing_release_dispositions": 2,
                "integration_dispositions": 1,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
            },
        )
        iwbd_years = [
            int(str(row["start_date"])[:4])
            for row in self.iwbd_rows
            if row.get("start_date") and str(row["start_date"])[:4].isdigit()
        ]
        self.assertGreaterEqual(min(iwbd_years), 1823)

    def test_future_iwbd_and_changed_existing_owners_fail_closed(self) -> None:
        fake_iwbd = [
            *self.iwbd_rows,
            {
                "candidate_id": "iwbd-future-samhud",
                "name": "Battle of Samhud",
                "start_date": "1799-01-22",
            },
        ]
        with self.assertRaisesRegex(ValueError, "unreviewed probable IWBD duplicate"):
            validate_wave8_mamluk_egypt_integration_dispositions(
                self.hced_rows,
                fake_iwbd,
                self.release_events,
            )

        missing_marj = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") != "hced-Marj Dabik1516-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one event"):
            validate_wave8_mamluk_egypt_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                missing_marj,
            )

        changed_mount_tabor = copy.deepcopy(self.release_events)
        mount_tabor = next(
            event
            for event in changed_mount_tabor
            if event.get("hced_candidate_id") == "hced-Mount Tabor1799-1"
        )
        mount_tabor["participants"][0]["entity_id"] = "mamluk_sultanate"
        with self.assertRaisesRegex(ValueError, "participants changed"):
            validate_wave8_mamluk_egypt_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                changed_mount_tabor,
            )

    def test_promotion_requires_entity_windows_and_rejects_duplicate_events(self) -> None:
        entities, _, existing = self._installed()
        missing_entity = copy.deepcopy(entities)
        del missing_entity["murad_bey_rahmaniyya_force_1786"]
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_mamluk_egypt_contracts(
                self.hced_rows,
                missing_entity,
                existing,
            )

        wrong_window = copy.deepcopy(entities)
        wrong_window["murad_bey_egypt_campaign_force_1798"]["start_year"] = 1799
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_mamluk_egypt_contracts(
                self.hced_rows,
                wrong_window,
                existing,
            )

        emitted = promote_wave8_mamluk_egypt_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_mamluk_egypt_contracts(
                self.hced_rows,
                entities,
                [*existing, emitted[0]],
            )
        duplicate_name = [
            *existing,
            {"name": "Battle of Samhud", "year": 1799},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_mamluk_egypt_contracts(
                self.hced_rows,
                entities,
                duplicate_name,
            )

    def test_public_api_exposes_all_lane_integration_contracts(self) -> None:
        module = __import__(
            "military_elo.promotion.wave8_mamluk_egypt",
            fromlist=["__all__"],
        )
        required = {
            "WAVE8_MAMLUK_EGYPT_CONTRACTS",
            "WAVE8_MAMLUK_EGYPT_COUNTRY_QUARANTINE_ADDITIONS",
            "WAVE8_MAMLUK_EGYPT_CROSS_LANE_DISPOSITIONS",
            "WAVE8_MAMLUK_EGYPT_ENTITIES",
            "WAVE8_MAMLUK_EGYPT_EXCLUSIONS",
            "WAVE8_MAMLUK_EGYPT_FINAL_AUDIT_SIGNATURE",
            "WAVE8_MAMLUK_EGYPT_HOLDS",
            "WAVE8_MAMLUK_EGYPT_INTEGRATION_DISPOSITIONS",
            "WAVE8_MAMLUK_EGYPT_IWBD_DUPLICATE_DISPOSITIONS",
            "WAVE8_MAMLUK_EGYPT_IWBD_ZERO_OVERLAP_AUDIT",
            "WAVE8_MAMLUK_EGYPT_OUTCOME_OVERRIDES",
            "WAVE8_MAMLUK_EGYPT_POINT_QUARANTINE_ADDITIONS",
            "WAVE8_MAMLUK_EGYPT_RESERVED_IDS",
            "WAVE8_MAMLUK_EGYPT_SOURCES",
            "install_wave8_mamluk_egypt_entities",
            "install_wave8_mamluk_egypt_sources",
            "promote_wave8_mamluk_egypt_contracts",
            "validate_wave8_mamluk_egypt_integration_dispositions",
            "validate_wave8_mamluk_egypt_queue_contracts",
            "wave8_mamluk_egypt_audit_signature",
            "wave8_mamluk_egypt_cohort_counts",
            "wave8_mamluk_egypt_counts",
            "wave8_mamluk_egypt_location_quarantine_additions",
        }
        self.assertTrue(required <= set(module.__all__))


if __name__ == "__main__":
    unittest.main()
