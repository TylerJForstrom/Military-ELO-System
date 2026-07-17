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
from military_elo.promotion.wave8_rebel_barons import (
    WAVE8_REBEL_BARONS_CONTRACT_IDS,
    WAVE8_REBEL_BARONS_CONTRACTS,
    WAVE8_REBEL_BARONS_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_REBEL_BARONS_CROSS_LANE_DISPOSITIONS,
    WAVE8_REBEL_BARONS_ENTITIES,
    WAVE8_REBEL_BARONS_EXCLUSION_IDS,
    WAVE8_REBEL_BARONS_EXCLUSIONS,
    WAVE8_REBEL_BARONS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS,
    WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS,
    WAVE8_REBEL_BARONS_EXTERNAL_OWNER_IDS,
    WAVE8_REBEL_BARONS_FINAL_AUDIT_SIGNATURE,
    WAVE8_REBEL_BARONS_HOLD_IDS,
    WAVE8_REBEL_BARONS_HOLDS,
    WAVE8_REBEL_BARONS_INTEGRATION_DISPOSITIONS,
    WAVE8_REBEL_BARONS_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_REBEL_BARONS_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_REASONS,
    WAVE8_REBEL_BARONS_NONPROMOTIONS,
    WAVE8_REBEL_BARONS_OUTCOME_OVERRIDES,
    WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS,
    WAVE8_REBEL_BARONS_RESERVED_IDS,
    WAVE8_REBEL_BARONS_ROW_HASHES,
    WAVE8_REBEL_BARONS_SOURCES,
    WAVE8_REBEL_BARONS_TERMINAL_EXCLUSION_IDS,
    WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS,
    install_wave8_rebel_barons_entities,
    install_wave8_rebel_barons_sources,
    promote_wave8_rebel_barons_contracts,
    validate_wave8_rebel_barons_integration_dispositions,
    validate_wave8_rebel_barons_queue_contracts,
    wave8_rebel_barons_audit_signature,
    wave8_rebel_barons_cohort_counts,
    wave8_rebel_barons_counts,
    wave8_rebel_barons_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_rebel_barons_"
FUNNEL_CANDIDATE_ID_SHA256 = (
    "7bfb4a70bf18044f377c1fddafeaedac4f03de5333a8985b32d4b2e5724d8050"
)
FINAL_AUDIT_SIGNATURE = (
    "00a0e4a8e50618b0c0da50750ad9e2af3e6f8adff2ca1af8a803045d7f3e1d45"
)

AXHOLME_ROYAL_ID = "lord_edward_royalist_containment_force_axholme_1265"
AXHOLME_REBEL_ID = "montfort_de_eyville_wake_disinherited_force_axholme_1265"
BYTHAM_ROYAL_ID = "henry_iii_royal_siege_host_bytham_1221"
BYTHAM_REBEL_ID = "aumale_bytham_garrison_1221"
BEDFORD_ROYAL_ID = "henry_iii_royal_siege_host_bedford_1224"
BEDFORD_REBEL_ID = "william_de_breaute_bedford_garrison_1224"
ROCHESTER_1215_ROYAL_ID = "king_john_royal_siege_army_rochester_1215"
ROCHESTER_1215_REBEL_ID = "william_d_aubigny_baronial_garrison_rochester_1215"
ROCHESTER_1264_ROYAL_ID = (
    "leybourne_warenne_garrison_and_royal_relief_force_rochester_1264"
)
ROCHESTER_1264_REBEL_ID = "montfort_clare_baronial_siege_force_rochester_1264"
CHESTERFIELD_ROYAL_ID = "henry_of_almain_royalist_force_chesterfield_1266"
CHESTERFIELD_REBEL_ID = "ferrers_de_eyville_disinherited_force_chesterfield_1266"


EXPECTED_RAW_HASHES = {
    "hced-Axholme1265-1": "8069ce55234af30bfe1b9cd01e413ed9d312a65aa9e23f64257fe88f775c7dd5",
    "hced-Bedford1224-1": "092fd67664ebd3d744544a5a5546b71357b6057143dd93c45a18e1724328e03d",
    "hced-Bytham1221-1": "24ad76f2441c847056deb44a3c04a65b7b3e5dd1cd57ea7b1598eaa50ab4d155",
    "hced-Chesterfield1266-1": "7750bc6e78bc3599ff1160506e6258c124f454d6d12b9f7896e185ceedbc51c9",
    "hced-Rochester1215-1": "1a1723a2fbf26a6072ec8841b36dac971692eb3b8bb42c2206773084d55fe6b0",
    "hced-Rochester1264-1": "717e7e878f901501d5a1de0ba59e48a3876b6609604f4bb059766237f7ea5fc2",
}

EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Axholme1265-1": ({AXHOLME_ROYAL_ID}, {AXHOLME_REBEL_ID}),
    "hced-Bedford1224-1": ({BEDFORD_ROYAL_ID}, {BEDFORD_REBEL_ID}),
    "hced-Bytham1221-1": ({BYTHAM_ROYAL_ID}, {BYTHAM_REBEL_ID}),
    "hced-Chesterfield1266-1": (
        {CHESTERFIELD_ROYAL_ID},
        {CHESTERFIELD_REBEL_ID},
    ),
    "hced-Rochester1215-1": (
        {ROCHESTER_1215_ROYAL_ID},
        {ROCHESTER_1215_REBEL_ID},
    ),
    "hced-Rochester1264-1": (
        {ROCHESTER_1264_ROYAL_ID},
        {ROCHESTER_1264_REBEL_ID},
    ),
}

EXPECTED_CANONICAL = {
    "hced-Axholme1265-1": (
        "Axholme campaign and submission",
        1265,
        "November-December 1265",
        "month_range",
        "campaign_and_submission",
    ),
    "hced-Bedford1224-1": (
        "Siege of Bedford Castle (1224)",
        1224,
        "20 June-15 August 1224",
        "day_range",
        "siege",
    ),
    "hced-Bytham1221-1": (
        "Siege of Castle Bytham",
        1221,
        "3-8 February 1221",
        "day_range",
        "siege",
    ),
    "hced-Chesterfield1266-1": (
        "Battle of Chesterfield",
        1266,
        "15 May 1266",
        "day",
        "engagement",
    ),
    "hced-Rochester1215-1": (
        "Siege of Rochester Castle (1215)",
        1215,
        "11 October-30 November 1215",
        "day_range",
        "siege",
    ),
    "hced-Rochester1264-1": (
        "Siege and relief of Rochester Castle (1264)",
        1264,
        "17-26 April 1264",
        "day_range",
        "siege_and_relief",
    ),
}

VARIANT_LABEL_IDS = {
    "hced-Ely1267-1",
    "hced-Evesham1265-1",
    "hced-Gartalunane1489-1",
    "hced-Hertogenbosch1629-1",
    "hced-Lewes1264-1",
    "hced-Lincoln1217-1",
    "hced-Sauchieburn1488-1",
    "hced-Skalice1424-1",
    "hced-Troia1462-1",
}


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class Wave8RebelBaronsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _load_jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _load_jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = json.loads(
            (ROOT / "build/hced-unresolved-label-funnel.json").read_text()
        )
        cls.release_entities = {
            str(entity["id"]): entity
            for entity in json.loads((ROOT / "data/release/entities.json").read_text())
        }
        cls.release_events = json.loads(
            (ROOT / "data/release/events.json").read_text()
        )
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced_rows
        }
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "rebel barons"
            or normalize_label(row.get("side_2_raw")) == "rebel barons"
        ]

    def _installed(self) -> tuple[dict, dict]:
        entities = copy.deepcopy(self.release_entities)
        sources: dict[str, dict] = {}
        install_wave8_rebel_barons_entities(entities)
        install_wave8_rebel_barons_sources(sources)
        return entities, sources

    def _emit(self, existing_events=None) -> tuple[dict, dict, list]:
        entities, sources = self._installed()
        existing = (
            copy.deepcopy(self.release_events)
            if existing_events is None
            else copy.deepcopy(existing_events)
        )
        events = promote_wave8_rebel_barons_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_funnel_and_queue_lock_the_complete_six_row_exact_cohort(self) -> None:
        scoped_rows = {
            str(row["candidate_id"]): row
            for row in self.funnel["row_label_data"]
            if "rebel barons" in row.get("blocker_labels", [])
        }
        exact_ids = {str(row["candidate_id"]) for row in self.exact_rows}
        self.assertEqual(len(scoped_rows), 6)
        self.assertEqual(exact_ids, set(EXPECTED_RAW_HASHES))
        self.assertEqual(set(scoped_rows), exact_ids)
        self.assertEqual(WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS, exact_ids)

        payload = "".join(f"{candidate_id}\n" for candidate_id in sorted(scoped_rows))
        self.assertEqual(
            hashlib.sha256(payload.encode()).hexdigest(),
            FUNNEL_CANDIDATE_ID_SHA256,
        )
        label_rows = [
            row
            for row in self.funnel["labels"]
            if row.get("label") == "rebel barons"
        ]
        self.assertEqual(len(label_rows), 1)
        label_row = label_rows[0]
        self.assertEqual(
            label_row["event_candidate_id_sha256"],
            FUNNEL_CANDIDATE_ID_SHA256,
        )
        self.assertEqual(label_row["events_touched"], 6)
        self.assertEqual(label_row["unresolved_side_attempts"], 6)
        self.assertEqual(label_row["centuries"], {"CE_13": 6})
        self.assertEqual(label_row["sole_blocker_events"], 4)
        self.assertEqual(label_row["components_touched"], 1)
        self.assertEqual(label_row["rated_counterpart_entities"], 1)
        self.assertEqual(label_row["failure_cases"]["zero_time_valid_candidates"], 6)
        sole_ids = {
            candidate_id
            for candidate_id, row in scoped_rows.items()
            if row.get("sole_blocker_label") == "rebel barons"
        }
        self.assertEqual(
            sole_ids,
            {
                "hced-Axholme1265-1",
                "hced-Bedford1224-1",
                "hced-Bytham1221-1",
                "hced-Chesterfield1266-1",
            },
        )
        for row in scoped_rows.values():
            self.assertTrue(
                any(
                    failure.get("label") == "rebel barons"
                    and failure.get("failure_case") == "zero_time_valid_candidates"
                    for failure in row.get("label_failures", [])
                )
            )

    def test_all_raw_hashes_contract_ids_and_signature_are_pinned(self) -> None:
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(WAVE8_REBEL_BARONS_ROW_HASHES, EXPECTED_RAW_HASHES)
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            self.assertEqual(
                canonical_hced_row_sha256(by_id[candidate_id]), expected_hash
            )
            self.assertEqual(
                WAVE8_REBEL_BARONS_CONTRACTS[candidate_id]["raw_row_sha256"],
                expected_hash,
            )
        self.assertEqual(WAVE8_REBEL_BARONS_CONTRACT_IDS, set(EXPECTED_RAW_HASHES))
        self.assertEqual(WAVE8_REBEL_BARONS_FINAL_AUDIT_SIGNATURE, FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_rebel_barons_audit_signature(), FINAL_AUDIT_SIGNATURE)

    def test_disposition_partition_is_complete_explicit_and_nonoverlapping(self) -> None:
        self.assertEqual(WAVE8_REBEL_BARONS_HOLDS, {})
        self.assertEqual(WAVE8_REBEL_BARONS_HOLD_IDS, frozenset())
        self.assertEqual(WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS, {})
        self.assertEqual(WAVE8_REBEL_BARONS_TERMINAL_EXCLUSION_IDS, frozenset())
        self.assertEqual(WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS, {})
        self.assertEqual(WAVE8_REBEL_BARONS_EXTERNAL_OWNER_IDS, frozenset())
        self.assertEqual(WAVE8_REBEL_BARONS_NONPROMOTIONS, {})
        self.assertEqual(WAVE8_REBEL_BARONS_EXCLUSION_IDS, frozenset())
        self.assertIs(
            WAVE8_REBEL_BARONS_EXCLUSIONS,
            WAVE8_REBEL_BARONS_TERMINAL_EXCLUSIONS,
        )
        self.assertIs(
            WAVE8_REBEL_BARONS_CROSS_LANE_DISPOSITIONS,
            WAVE8_REBEL_BARONS_EXTERNAL_OWNER_DISPOSITIONS,
        )
        self.assertEqual(WAVE8_REBEL_BARONS_RESERVED_IDS, set(EXPECTED_RAW_HASHES))
        self.assertEqual(
            WAVE8_REBEL_BARONS_RESERVED_IDS | WAVE8_REBEL_BARONS_EXTERNAL_OWNER_IDS,
            WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS,
        )

    def test_contracts_pin_dates_actors_outcomes_and_independent_sources(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_REBEL_BARONS_SOURCES
        }
        for candidate_id, contract in WAVE8_REBEL_BARONS_CONTRACTS.items():
            canonical = contract["canonical_event"]
            expected = EXPECTED_CANONICAL[candidate_id]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["year_low"],
                    canonical["date_text"],
                    canonical["date_precision"],
                    canonical["granularity"],
                ),
                expected,
            )
            self.assertEqual(canonical["year_low"], canonical["year_high"])
            winners, losers = EXPECTED_WINNERS_AND_LOSERS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), losers)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract["war_type"], "civil_war")
            self.assertIs(contract["actor_override"], True)
            self.assertIs(contract["source_outcome_override"], False)
            self.assertIs(contract["outcome_reversal"], False)
            self.assertEqual(
                contract["duplicate_ownership"],
                {
                    "owner_module": "military_elo.promotion.wave8_rebel_barons",
                    "status": "canonical_hced_owner",
                },
            )
            self.assertEqual(
                contract["evidence_refs"], sorted(set(contract["evidence_refs"]))
            )
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertLessEqual(
                set(contract["outcome_source_ids"]), set(contract["evidence_refs"])
            )
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in contract["outcome_source_ids"]
                    }
                ),
            )
        self.assertEqual(WAVE8_REBEL_BARONS_OUTCOME_OVERRIDES, {})
        self.assertFalse(
            any(
                contract["result_type"] in {"draw", "unknown"}
                for contract in WAVE8_REBEL_BARONS_CONTRACTS.values()
            )
        )

    def test_source_fixtures_are_parseable_independent_and_exactly_consumed(self) -> None:
        self.assertEqual(len(WAVE8_REBEL_BARONS_SOURCES), 11)
        source_ids = {str(source["id"]) for source in WAVE8_REBEL_BARONS_SOURCES}
        families = {
            str(source["source_family_id"]) for source in WAVE8_REBEL_BARONS_SOURCES
        }
        self.assertEqual(len(source_ids), 11)
        self.assertEqual(len(families), 11)
        used = set()
        for source in WAVE8_REBEL_BARONS_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertEqual(
                source["evidence_roles"], sorted(set(source["evidence_roles"]))
            )
        for contract in WAVE8_REBEL_BARONS_CONTRACTS.values():
            used.update(contract["evidence_refs"])
        for entity in WAVE8_REBEL_BARONS_ENTITIES:
            used.update(entity["source_ids"])
        self.assertEqual(used, source_ids)

    def test_entities_are_parseable_event_bounded_and_never_generic(self) -> None:
        self.assertEqual(len(WAVE8_REBEL_BARONS_ENTITIES), 12)
        entity_ids = {str(entity["id"]) for entity in WAVE8_REBEL_BARONS_ENTITIES}
        consumed = set()
        for entity in WAVE8_REBEL_BARONS_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertTrue(
                entity["kind"].startswith(("event_bounded_", "campaign_bounded_"))
            )
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("modern state", note)
            self.assertNotIn(
                normalize_label(entity["name"]),
                {"england", "king henry iii", "king john", "rebel barons"},
            )
            self.assertEqual(entity["source_ids"], sorted(set(entity["source_ids"])))
        for contract in WAVE8_REBEL_BARONS_CONTRACTS.values():
            consumed.update(contract["side_1_entity_ids"])
            consumed.update(contract["side_2_entity_ids"])
        self.assertEqual(consumed, entity_ids)

    def test_queue_validator_reports_exact_six_row_inventory(self) -> None:
        self.assertEqual(
            validate_wave8_rebel_barons_queue_contracts(self.hced_rows),
            {
                "external_owner_contracts": 0,
                "holds": 0,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 6,
                "terminal_exclusions": 0,
            },
        )

    def test_queue_validator_rejects_missing_duplicate_and_changed_rows(self) -> None:
        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Axholme1265-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_rebel_barons_queue_contracts(missing)

        duplicate = copy.deepcopy(self.hced_rows)
        duplicate.append(copy.deepcopy(self.hced_by_id["hced-Axholme1265-1"]))
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_rebel_barons_queue_contracts(duplicate)

        changed = copy.deepcopy(self.hced_rows)
        target = next(
            row for row in changed if row.get("candidate_id") == "hced-Bedford1224-1"
        )
        target["participants_raw"] = ["fingerprint drift"]
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_rebel_barons_queue_contracts(changed)

    def test_queue_validator_rejects_an_expanded_exact_label_inventory(self) -> None:
        expanded = copy.deepcopy(self.hced_rows)
        expanded.append(
            {
                "candidate_id": "hced-Synthetic1270-1",
                "name": "Synthetic",
                "side_1_raw": "Rebel Barons",
                "side_2_raw": "Someone else",
                "year_low": 1270,
                "year_high": 1270,
            }
        )
        with self.assertRaisesRegex(ValueError, "exact Rebel Barons inventory changed"):
            validate_wave8_rebel_barons_queue_contracts(expanded)

    def test_variant_baronial_labels_are_not_absorbed_into_exact_lane(self) -> None:
        self.assertLessEqual(VARIANT_LABEL_IDS, set(self.hced_by_id))
        self.assertFalse(VARIANT_LABEL_IDS & WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS)
        for candidate_id in VARIANT_LABEL_IDS:
            row = self.hced_by_id[candidate_id]
            self.assertNotEqual(normalize_label(row.get("side_1_raw")), "rebel barons")
            self.assertNotEqual(normalize_label(row.get("side_2_raw")), "rebel barons")

    def test_promoter_emits_six_parseable_victories_with_exact_participants(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 6)
        self.assertEqual(
            [event["year"] for event in events],
            [1215, 1221, 1224, 1264, 1265, 1266],
        )
        self.assertEqual(len({event["id"] for event in events}), 6)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), WAVE8_REBEL_BARONS_CONTRACT_IDS)
        for candidate_id, event in by_candidate.items():
            Event.from_dict(event)
            contract = WAVE8_REBEL_BARONS_CONTRACTS[candidate_id]
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["war_type"], "civil_war")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["status"], "complete")
            self.assertEqual(
                event["reviewed_granularity"],
                contract["canonical_event"]["granularity"],
            )
            self.assertEqual(
                event["date_precision"],
                contract["canonical_event"]["date_precision"],
            )
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertIn(contract["audit_note"], event["summary"])
            participants = event["participants"]
            winners = {
                participant["entity_id"]
                for participant in participants
                if participant["result_class"] == "limited_victory"
            }
            losers = {
                participant["entity_id"]
                for participant in participants
                if participant["result_class"] == "limited_defeat"
            }
            self.assertEqual((winners, losers), EXPECTED_WINNERS_AND_LOSERS[candidate_id])
            self.assertEqual(len(participants), 2)
            self.assertFalse(
                any(participant["result_class"] == "draw" for participant in participants)
            )

    def test_promoter_is_deterministic_and_installers_are_idempotent(self) -> None:
        entities, sources = self._installed()
        install_wave8_rebel_barons_entities(entities)
        install_wave8_rebel_barons_sources(sources)
        first = promote_wave8_rebel_barons_contracts(
            self.hced_rows, entities, self.release_events
        )
        second = promote_wave8_rebel_barons_contracts(
            copy.deepcopy(self.hced_rows),
            copy.deepcopy(entities),
            copy.deepcopy(self.release_events),
        )
        self.assertEqual(first, second)

    def test_installers_fail_closed_on_fixture_collisions(self) -> None:
        entities, sources = self._installed()
        entity_id = WAVE8_REBEL_BARONS_ENTITIES[0]["id"]
        entities[entity_id] = {**entities[entity_id], "name": "collision"}
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_rebel_barons_entities(entities)

        source_id = WAVE8_REBEL_BARONS_SOURCES[0]["id"]
        sources[source_id] = {**sources[source_id], "title": "collision"}
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_rebel_barons_sources(sources)

    def test_promoter_rejects_missing_or_out_of_window_entities(self) -> None:
        entities, _ = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(AXHOLME_ROYAL_ID)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_rebel_barons_contracts(self.hced_rows, missing, [])

        out_of_window = copy.deepcopy(entities)
        out_of_window[AXHOLME_ROYAL_ID]["end_year"] = 1264
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_rebel_barons_contracts(self.hced_rows, out_of_window, [])

    def test_promoter_rejects_candidate_canonical_and_raw_name_collisions(self) -> None:
        entities, _ = self._installed()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_rebel_barons_contracts(
                self.hced_rows,
                entities,
                [
                    {
                        "id": "existing_candidate",
                        "name": "Anything",
                        "year": 1265,
                        "hced_candidate_id": "hced-Axholme1265-1",
                    }
                ],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_rebel_barons_contracts(
                self.hced_rows,
                entities,
                [
                    {
                        "id": "existing_canonical",
                        "name": "Battle of Chesterfield",
                        "year": 1266,
                    }
                ],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_rebel_barons_contracts(
                self.hced_rows,
                entities,
                [{"id": "existing_raw", "name": "Bedford", "year": 1224}],
            )

    def test_duplicate_and_integration_dispositions_are_complete_and_zero(self) -> None:
        self.assertEqual(WAVE8_REBEL_BARONS_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_REBEL_BARONS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_REBEL_BARONS_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            set(WAVE8_REBEL_BARONS_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_REBEL_BARONS_EXPECTED_CANDIDATE_IDS,
        )
        for candidate_id, audit in WAVE8_REBEL_BARONS_IWBD_ZERO_OVERLAP_AUDIT.items():
            self.assertEqual(audit["aliases"], sorted(set(audit["aliases"])))
            self.assertTrue(audit["aliases"])
            self.assertTrue(
                all(alias == normalize_label(alias) for alias in audit["aliases"])
            )
            year = EXPECTED_CANONICAL[candidate_id][1]
            self.assertEqual(audit["years"], [year, year])
            self.assertIn(
                normalize_label(EXPECTED_CANONICAL[candidate_id][0]),
                audit["aliases"],
            )

        self.assertEqual(
            validate_wave8_rebel_barons_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "external_owner_hced_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 6,
            },
        )

    def test_integration_validator_rejects_unreviewed_hced_iwbd_and_release_twins(self) -> None:
        hced_with_twin = copy.deepcopy(self.hced_rows)
        hced_with_twin.append(
            {
                "candidate_id": "hced-other-lane-bedford",
                "name": "Bedford Castle",
                "side_1_raw": "A",
                "side_2_raw": "B",
                "year_low": 1224,
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_rebel_barons_integration_dispositions(
                hced_with_twin, self.iwbd_rows, self.release_events
            )

        iwbd_with_twin = copy.deepcopy(self.iwbd_rows)
        iwbd_with_twin.append(
            {
                "candidate_id": "iwbd-synthetic-rochester",
                "name": "Siege of Rochester Castle",
                "year": 1215,
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            validate_wave8_rebel_barons_integration_dispositions(
                self.hced_rows, iwbd_with_twin, self.release_events
            )

        release_with_twin = copy.deepcopy(self.release_events)
        release_with_twin.append(
            {
                "id": "release_synthetic_chesterfield",
                "name": "Battle of Chesterfield 1266",
                "year": 1266,
            }
        )
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_rebel_barons_integration_dispositions(
                self.hced_rows, self.iwbd_rows, release_with_twin
            )

    def test_location_review_is_promoted_only_local_and_withholds_every_point(self) -> None:
        point_globals_before = frozenset(HCED_POINT_QUARANTINE_IDS)
        country_globals_before = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(
            WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS,
            WAVE8_REBEL_BARONS_CONTRACT_IDS,
        )
        self.assertEqual(WAVE8_REBEL_BARONS_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertFalse(
            WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS
            & HCED_POINT_QUARANTINE_IDS
        )
        self.assertEqual(
            WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_REBEL_BARONS_POINT_QUARANTINE_ADDITIONS,
                "country": WAVE8_REBEL_BARONS_COUNTRY_QUARANTINE_ADDITIONS,
            },
        )
        self.assertEqual(
            wave8_rebel_barons_location_quarantine_additions(),
            WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_ADDITIONS,
        )
        self.assertEqual(
            set(WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_REASONS),
            WAVE8_REBEL_BARONS_CONTRACT_IDS,
        )
        for review in WAVE8_REBEL_BARONS_LOCATION_QUARANTINE_REASONS.values():
            self.assertEqual(review["actions"], ["withhold_point"])
            self.assertTrue(review["reason"])

        _, _, events = self._emit()
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "United Kingdom")
            self.assertEqual(
                event["location_provenance"]["assertion_status"],
                "unreviewed_source_assertion",
            )
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), point_globals_before)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), country_globals_before)

    def test_bedford_axholme_rochester_and_chesterfield_boundaries_are_explicit(self) -> None:
        bedford = WAVE8_REBEL_BARONS_CONTRACTS["hced-Bedford1224-1"]
        self.assertIn("Falkes was absent", bedford["audit_note"])
        self.assertIn("post-surrender execution", bedford["audit_note"])
        self.assertIn("not a second competitive result", bedford["audit_note"])
        self.assertEqual(
            self.hced_by_id["hced-Bedford1224-1"]["massacre_raw"],
            "Battle followed by massacre",
        )

        axholme = WAVE8_REBEL_BARONS_CONTRACTS["hced-Axholme1265-1"]
        self.assertIn("contain", axholme["audit_note"].casefold())
        self.assertIn("submission", axholme["audit_note"].casefold())
        self.assertIn("no later punishment", axholme["audit_note"].casefold())

        rochester = WAVE8_REBEL_BARONS_CONTRACTS["hced-Rochester1264-1"]
        self.assertEqual(
            rochester["canonical_event"]["granularity"], "siege_and_relief"
        )
        self.assertIn("retained the keep", rochester["audit_note"])
        self.assertIn("abandon the siege", rochester["audit_note"])

        chesterfield = WAVE8_REBEL_BARONS_CONTRACTS["hced-Chesterfield1266-1"]
        self.assertIn("away hunting", chesterfield["audit_note"])
        self.assertIn("excluded", chesterfield["audit_note"])

    def test_counts_and_cohorts_are_exact(self) -> None:
        self.assertEqual(
            wave8_rebel_barons_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "external_owner_hced_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 6,
                "new_entities": 12,
                "new_sources": 11,
                "newly_rated_events": 6,
                "outcome_overrides": 0,
                "point_quarantine_additions": 6,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 6,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            wave8_rebel_barons_cohort_counts(),
            {
                "first_barons_war_1215_1217": 1,
                "post_evesham_disinherited_1265_1266": 2,
                "post_first_barons_war_royal_recovery_1221_1224": 2,
                "second_barons_war_1264": 1,
            },
        )


if __name__ == "__main__":
    unittest.main()
