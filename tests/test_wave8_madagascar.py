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
from military_elo.promotion.wave8_exact import promote_exact_hced_contracts
from military_elo.promotion.wave8_madagascar import (
    WAVE8_MADAGASCAR_CONTRACT_IDS,
    WAVE8_MADAGASCAR_CONTRACTS,
    WAVE8_MADAGASCAR_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_MADAGASCAR_CROSS_LANE_DISPOSITIONS,
    WAVE8_MADAGASCAR_ENTITIES,
    WAVE8_MADAGASCAR_EXCLUSION_IDS,
    WAVE8_MADAGASCAR_EXCLUSIONS,
    WAVE8_MADAGASCAR_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS,
    WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS,
    WAVE8_MADAGASCAR_EXTERNAL_OWNER_IDS,
    WAVE8_MADAGASCAR_FINAL_AUDIT_SIGNATURE,
    WAVE8_MADAGASCAR_HCED_DUPLICATE_DISPOSITIONS,
    WAVE8_MADAGASCAR_HOLD_IDS,
    WAVE8_MADAGASCAR_HOLDS,
    WAVE8_MADAGASCAR_INTEGRATION_DISPOSITIONS,
    WAVE8_MADAGASCAR_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_MADAGASCAR_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_MADAGASCAR_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_MADAGASCAR_LOCATION_QUARANTINE_REASONS,
    WAVE8_MADAGASCAR_NONPROMOTIONS,
    WAVE8_MADAGASCAR_OUTCOME_OVERRIDES,
    WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS,
    WAVE8_MADAGASCAR_RESERVED_IDS,
    WAVE8_MADAGASCAR_ROW_HASHES,
    WAVE8_MADAGASCAR_SOURCES,
    WAVE8_MADAGASCAR_TERMINAL_EXCLUSION_IDS,
    WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS,
    install_wave8_madagascar_entities,
    install_wave8_madagascar_sources,
    promote_wave8_madagascar_contracts,
    validate_wave8_madagascar_integration_dispositions,
    validate_wave8_madagascar_queue_contracts,
    wave8_madagascar_audit_signature,
    wave8_madagascar_cohort_counts,
    wave8_madagascar_counts,
    wave8_madagascar_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_madagascar_"
FUNNEL_CANDIDATE_ID_SHA256 = (
    "923d9d1f1140c2dd3ae7f4d7b60dd744d0c48d4b56059936f80a2f024eb4cc8d"
)
FINAL_AUDIT_SIGNATURE = (
    "cd30bd8b563e0bc002deab128dc6dd5b82b8364c8e42702bf359b3d3e395a001"
)

MERINA_ID = "kingdom_madagascar_merina_1817_1895"
JULY_MONARCHY_ID = "french_july_monarchy"
UNITED_KINGDOM_ID = "united_kingdom"
FRENCH_THIRD_REPUBLIC_ID = "french_third_republic"

EXPECTED_RAW_HASHES = {
    "hced-Andriba1895-1": "5e96c02bdcaf85d7f20ee1716263747f616d2388811bfe1af940f54db58751d7",
    "hced-Tamatave1845-1": "9212d2428f3c7954fbccfb8cc495df6ec76211a9f21cad1f53920cff25a7ea4f",
    "hced-Tamatave1883-1": "b2921bfce984bb4a0e722b9768bc8e8b840b13f7d78c5e11f64f049661fac7d5",
    "hced-Tananarive1895-1": "ad4b7b3e5c72bc71cedc5091adc1dff57f619b97df895ee0ea7489ab48d5e33e",
    "hced-Tsarasoatra1895-1": "d920aea959b005a408aa0dc2646c169a49c25f9e60bd05a1c6dcd114071da682",
}

EXPECTED_CANONICAL = {
    "hced-Andriba1895-1": (
        "Combat and capture of Andriba",
        1895,
        "21-22 August 1895",
        "day_range",
        "fortified_position_assault",
    ),
    "hced-Tamatave1845-1": (
        "Anglo-French assault on Tamatave (1845)",
        1845,
        "15 June 1845",
        "day",
        "naval_bombardment_and_fort_assault",
    ),
    "hced-Tamatave1883-1": (
        "Bombardment and occupation of Tamatave (1883)",
        1883,
        "10-11 June 1883",
        "day_range",
        "naval_bombardment_and_port_capture",
    ),
    "hced-Tananarive1895-1": (
        "Final action and capture of Tananarive",
        1895,
        "29-30 September 1895",
        "day_range",
        "capital_approach_and_capture",
    ),
    "hced-Tsarasoatra1895-1": (
        "Battles of Tsarasoatra and Beritsoka",
        1895,
        "29-30 June 1895",
        "day_range",
        "two_day_engagement",
    ),
}

EXPECTED_SIDES = {
    "hced-Andriba1895-1": (
        {FRENCH_THIRD_REPUBLIC_ID},
        {MERINA_ID},
    ),
    "hced-Tamatave1845-1": (
        {MERINA_ID},
        {JULY_MONARCHY_ID, UNITED_KINGDOM_ID},
    ),
    "hced-Tamatave1883-1": (
        {FRENCH_THIRD_REPUBLIC_ID},
        {MERINA_ID},
    ),
    "hced-Tananarive1895-1": (
        {FRENCH_THIRD_REPUBLIC_ID},
        {MERINA_ID},
    ),
    "hced-Tsarasoatra1895-1": (
        {FRENCH_THIRD_REPUBLIC_ID},
        {MERINA_ID},
    ),
}


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class Wave8MadagascarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _load_jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _load_jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = json.loads(
            (ROOT / "build/hced-unresolved-label-funnel.json").read_text(encoding="utf-8")
        )
        cls.release_entities = {
            str(entity["id"]): entity
            for entity in json.loads((ROOT / "data/release/entities.json").read_text(encoding="utf-8"))
        }
        cls.release_events = json.loads(
            (ROOT / "data/release/events.json").read_text(encoding="utf-8")
        )
        cls.existing_events_without_lane = [
            event
            for event in cls.release_events
            if event.get("hced_candidate_id") not in WAVE8_MADAGASCAR_CONTRACT_IDS
        ]
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced_rows
        }
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if normalize_label(row.get("side_1_raw")) == "madagascar"
            or normalize_label(row.get("side_2_raw")) == "madagascar"
        ]

    def _installed(self) -> tuple[dict, dict]:
        entities = copy.deepcopy(self.release_entities)
        sources: dict[str, dict] = {}
        install_wave8_madagascar_entities(entities)
        install_wave8_madagascar_sources(sources)
        return entities, sources

    def _emit(self, existing_events=None) -> tuple[dict, dict, list]:
        entities, sources = self._installed()
        existing = (
            copy.deepcopy(self.existing_events_without_lane)
            if existing_events is None
            else copy.deepcopy(existing_events)
        )
        events = promote_wave8_madagascar_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_funnel_and_queue_lock_complete_five_row_exact_cohort(self) -> None:
        scoped_rows = {
            str(row["candidate_id"]): row
            for row in self.funnel["row_label_data"]
            if "madagascar" in row.get("blocker_labels", [])
        }
        exact_ids = {str(row["candidate_id"]) for row in self.exact_rows}
        self.assertEqual(len(scoped_rows), 5)
        self.assertEqual(exact_ids, set(EXPECTED_RAW_HASHES))
        self.assertEqual(set(scoped_rows), exact_ids)
        self.assertEqual(WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS, exact_ids)

        payload = "".join(f"{candidate_id}\n" for candidate_id in sorted(scoped_rows))
        self.assertEqual(
            hashlib.sha256(payload.encode()).hexdigest(),
            FUNNEL_CANDIDATE_ID_SHA256,
        )
        label_rows = [
            row for row in self.funnel["labels"] if row.get("label") == "madagascar"
        ]
        self.assertEqual(len(label_rows), 1)
        label_row = label_rows[0]
        self.assertEqual(label_row["event_candidate_id_sha256"], FUNNEL_CANDIDATE_ID_SHA256)
        self.assertEqual(label_row["events_touched"], 5)
        self.assertEqual(label_row["unresolved_side_attempts"], 5)
        self.assertEqual(label_row["sole_blocker_events"], 4)
        self.assertEqual(label_row["failure_cases"], {
            "multiple_time_valid_candidates": 0,
            "one_wrong_interval_candidate": 5,
            "policy_denied_window": 0,
            "resolver_guard_or_tier_conflict": 0,
            "zero_time_valid_candidates": 0,
        })
        self.assertEqual(
            {
                candidate_id
                for candidate_id, row in scoped_rows.items()
                if row.get("sole_blocker_label") == "madagascar"
            },
            set(EXPECTED_RAW_HASHES) - {"hced-Tamatave1845-1"},
        )
        self.assertIn(
            "other_identity_blocker:outside_continuity_policy",
            scoped_rows["hced-Tamatave1845-1"]["other_blockers"],
        )

    def test_raw_hashes_contract_ids_and_signature_are_pinned(self) -> None:
        by_id = {str(row["candidate_id"]): row for row in self.exact_rows}
        self.assertEqual(WAVE8_MADAGASCAR_ROW_HASHES, EXPECTED_RAW_HASHES)
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            self.assertEqual(canonical_hced_row_sha256(by_id[candidate_id]), expected_hash)
            self.assertEqual(
                WAVE8_MADAGASCAR_CONTRACTS[candidate_id]["raw_row_sha256"],
                expected_hash,
            )
        self.assertEqual(WAVE8_MADAGASCAR_CONTRACT_IDS, set(EXPECTED_RAW_HASHES))
        self.assertEqual(WAVE8_MADAGASCAR_FINAL_AUDIT_SIGNATURE, FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_madagascar_audit_signature(), FINAL_AUDIT_SIGNATURE)

    def test_disposition_partition_is_complete_and_all_five_promote(self) -> None:
        self.assertEqual(WAVE8_MADAGASCAR_HOLDS, {})
        self.assertEqual(WAVE8_MADAGASCAR_HOLD_IDS, frozenset())
        self.assertEqual(WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS, {})
        self.assertEqual(WAVE8_MADAGASCAR_TERMINAL_EXCLUSION_IDS, frozenset())
        self.assertEqual(WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS, {})
        self.assertEqual(WAVE8_MADAGASCAR_EXTERNAL_OWNER_IDS, frozenset())
        self.assertEqual(WAVE8_MADAGASCAR_NONPROMOTIONS, {})
        self.assertEqual(WAVE8_MADAGASCAR_EXCLUSION_IDS, frozenset())
        self.assertIs(WAVE8_MADAGASCAR_EXCLUSIONS, WAVE8_MADAGASCAR_TERMINAL_EXCLUSIONS)
        self.assertIs(
            WAVE8_MADAGASCAR_CROSS_LANE_DISPOSITIONS,
            WAVE8_MADAGASCAR_EXTERNAL_OWNER_DISPOSITIONS,
        )
        self.assertEqual(WAVE8_MADAGASCAR_RESERVED_IDS, set(EXPECTED_RAW_HASHES))
        self.assertEqual(
            WAVE8_MADAGASCAR_RESERVED_IDS | WAVE8_MADAGASCAR_EXTERNAL_OWNER_IDS,
            WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS,
        )

    def test_contracts_pin_dates_sides_outcomes_and_direct_provenance(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_MADAGASCAR_SOURCES
        }
        for candidate_id, contract in WAVE8_MADAGASCAR_CONTRACTS.items():
            canonical = contract["canonical_event"]
            self.assertEqual(
                (
                    canonical["name"],
                    canonical["year_low"],
                    canonical["date_text"],
                    canonical["date_precision"],
                    canonical["granularity"],
                ),
                EXPECTED_CANONICAL[candidate_id],
            )
            self.assertEqual(canonical["year_low"], canonical["year_high"])
            expected_side_1, expected_side_2 = EXPECTED_SIDES[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), expected_side_1)
            self.assertEqual(set(contract["side_2_entity_ids"]), expected_side_2)
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertIs(contract["actor_override"], True)
            self.assertIs(contract["source_outcome_override"], False)
            self.assertIs(contract["outcome_reversal"], False)
            self.assertEqual(
                contract["duplicate_ownership"],
                {
                    "owner_module": "military_elo.promotion.wave8_madagascar",
                    "status": "canonical_hced_owner",
                },
            )
            self.assertEqual(
                contract["direct_provenance"]["reviewed_date"],
                canonical["date_text"],
            )
            self.assertTrue(contract["direct_provenance"]["reviewed_outcome"])
            self.assertTrue(contract["direct_provenance"]["event_boundary"])
            self.assertGreaterEqual(len(contract["outcome_source_ids"]), 2)
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertLessEqual(
                set(contract["outcome_source_ids"]),
                set(contract["evidence_refs"]),
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
        self.assertEqual(WAVE8_MADAGASCAR_OUTCOME_OVERRIDES, {})

    def test_unknown_is_never_a_draw_and_raw_outcomes_all_align(self) -> None:
        for candidate_id, contract in WAVE8_MADAGASCAR_CONTRACTS.items():
            row = self.hced_by_id[candidate_id]
            self.assertTrue(str(row["winner_raw"]).strip())
            self.assertNotIn(normalize_label(row["winner_raw"]), {"draw", "inconclusive", "stalemate"})
            self.assertEqual(row["winner_raw"], row[f"side_{contract['winner_side']}_raw"])
            self.assertEqual(row["loser_raw"], row[f"side_{3 - contract['winner_side']}_raw"])
            self.assertEqual(contract["result_type"], "win")

        rows = copy.deepcopy(self.hced_rows)
        target = next(
            row for row in rows if row.get("candidate_id") == "hced-Tamatave1845-1"
        )
        target["winner_raw"] = ""
        local_contracts = copy.deepcopy(WAVE8_MADAGASCAR_CONTRACTS)
        local_contracts["hced-Tamatave1845-1"]["raw_row_sha256"] = (
            canonical_hced_row_sha256(target)
        )
        entities, _ = self._installed()
        with self.assertRaisesRegex(ValueError, "outcome drift"):
            promote_exact_hced_contracts(
                rows,
                entities,
                self.existing_events_without_lane,
                local_contracts,
                lane_name="Madagascar unknown-result regression",
                event_id_prefix="test_madagascar_",
            )

    def test_tamatave_1845_is_a_bounded_coalition_defeat_not_a_hold(self) -> None:
        contract = WAVE8_MADAGASCAR_CONTRACTS["hced-Tamatave1845-1"]
        self.assertEqual(contract["canonical_event"]["date_text"], "15 June 1845")
        self.assertEqual(set(contract["side_1_entity_ids"]), {MERINA_ID})
        self.assertEqual(
            set(contract["side_2_entity_ids"]),
            {JULY_MONARCHY_ID, UNITED_KINGDOM_ID},
        )
        self.assertIn("assault was repulsed", contract["audit_note"])
        self.assertIn("not later policy", contract["audit_note"])
        self.assertIn(
            "wave8_madagascar_annales_tamatave_1845",
            contract["outcome_source_ids"],
        )
        self.assertIn(
            "wave8_madagascar_mcleod_tamatave_1845",
            contract["outcome_source_ids"],
        )

    def test_1895_rows_are_three_distinct_operations(self) -> None:
        tsarasoatra = WAVE8_MADAGASCAR_CONTRACTS["hced-Tsarasoatra1895-1"]
        andriba = WAVE8_MADAGASCAR_CONTRACTS["hced-Andriba1895-1"]
        tananarive = WAVE8_MADAGASCAR_CONTRACTS["hced-Tananarive1895-1"]
        self.assertEqual(
            [
                tsarasoatra["canonical_event"]["date_text"],
                andriba["canonical_event"]["date_text"],
                tananarive["canonical_event"]["date_text"],
            ],
            [
                "29-30 June 1895",
                "21-22 August 1895",
                "29-30 September 1895",
            ],
        )
        self.assertIn("distinct from Andriba", tsarasoatra["audit_note"])
        self.assertIn("later unopposed", andriba["audit_note"])
        self.assertIn("not converted", tananarive["audit_note"])
        self.assertEqual(
            len(
                {
                    contract["canonical_event"]["canonical_key"]
                    for contract in (tsarasoatra, andriba, tananarive)
                }
            ),
            3,
        )

    def test_sources_are_parseable_independent_and_exactly_consumed(self) -> None:
        self.assertEqual(len(WAVE8_MADAGASCAR_SOURCES), 13)
        source_ids = {str(source["id"]) for source in WAVE8_MADAGASCAR_SOURCES}
        families = {
            str(source["source_family_id"]) for source in WAVE8_MADAGASCAR_SOURCES
        }
        self.assertEqual(len(source_ids), 13)
        self.assertEqual(len(families), 13)
        used = set()
        for source in WAVE8_MADAGASCAR_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertEqual(source["evidence_roles"], sorted(set(source["evidence_roles"])))
        for contract in WAVE8_MADAGASCAR_CONTRACTS.values():
            used.update(contract["evidence_refs"])
        for entity in WAVE8_MADAGASCAR_ENTITIES:
            used.update(entity["source_ids"])
        self.assertEqual(used, source_ids)

    def test_entities_are_parseable_time_bounded_and_alias_free(self) -> None:
        self.assertEqual(len(WAVE8_MADAGASCAR_ENTITIES), 2)
        by_id = {str(entity["id"]): entity for entity in WAVE8_MADAGASCAR_ENTITIES}
        self.assertEqual(set(by_id), {MERINA_ID, JULY_MONARCHY_ID})
        self.assertEqual(
            (by_id[MERINA_ID]["start_year"], by_id[MERINA_ID]["end_year"]),
            (1817, 1895),
        )
        self.assertEqual(
            (
                by_id[JULY_MONARCHY_ID]["start_year"],
                by_id[JULY_MONARCHY_ID]["end_year"],
            ),
            (1830, 1848),
        )
        for entity in by_id.values():
            Entity.from_dict(entity)
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("modern state", note)
            self.assertEqual(entity["source_ids"], sorted(set(entity["source_ids"])))
        self.assertNotIn("Madagascar", by_id[MERINA_ID]["aliases"])
        self.assertNotIn("France", by_id[JULY_MONARCHY_ID]["aliases"])

    def test_queue_validator_reports_exact_inventory_and_fails_closed(self) -> None:
        self.assertEqual(
            validate_wave8_madagascar_queue_contracts(self.hced_rows),
            {
                "external_owner_contracts": 0,
                "holds": 0,
                "promotion_contracts": 5,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 0,
            },
        )
        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Andriba1895-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_madagascar_queue_contracts(missing)

        duplicate = copy.deepcopy(self.hced_rows)
        duplicate.append(copy.deepcopy(self.hced_by_id["hced-Tamatave1883-1"]))
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_madagascar_queue_contracts(duplicate)

        changed = copy.deepcopy(self.hced_rows)
        target = next(
            row for row in changed if row.get("candidate_id") == "hced-Tsarasoatra1895-1"
        )
        target["participants_raw"] = ["fingerprint drift"]
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_madagascar_queue_contracts(changed)

        expanded = copy.deepcopy(self.hced_rows)
        expanded.append(
            {
                "candidate_id": "hced-SyntheticMadagascar1900-1",
                "name": "Synthetic",
                "side_1_raw": "Madagascar",
                "side_2_raw": "Someone else",
                "year_low": 1900,
                "year_high": 1900,
            }
        )
        with self.assertRaisesRegex(ValueError, "exact Madagascar inventory changed"):
            validate_wave8_madagascar_queue_contracts(expanded)

    def test_promoter_emits_five_parseable_victories_with_exact_participants(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 5)
        self.assertEqual([event["year"] for event in events], [1845, 1883, 1895, 1895, 1895])
        self.assertEqual(len({event["id"] for event in events}), 5)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), WAVE8_MADAGASCAR_CONTRACT_IDS)
        for candidate_id, event in by_candidate.items():
            Event.from_dict(event)
            contract = WAVE8_MADAGASCAR_CONTRACTS[candidate_id]
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["status"], "complete")
            self.assertEqual(
                event["reviewed_granularity"],
                contract["canonical_event"]["granularity"],
            )
            self.assertEqual(event["date_precision"], contract["canonical_event"]["date_precision"])
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertIn(contract["audit_note"], event["summary"])
            winners = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["result_class"] in {"limited_victory", "major_tactical_victory"}
            }
            losers = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["result_class"] in {"limited_defeat", "major_tactical_defeat"}
            }
            self.assertEqual((winners, losers), EXPECTED_SIDES[candidate_id])
            self.assertFalse(
                any(
                    participant["result_class"] == "stalemate_or_inconclusive"
                    for participant in event["participants"]
                )
            )

    def test_promoter_is_deterministic_and_installers_are_idempotent(self) -> None:
        entities, sources = self._installed()
        install_wave8_madagascar_entities(entities)
        install_wave8_madagascar_sources(sources)
        first = promote_wave8_madagascar_contracts(
            self.hced_rows, entities, self.existing_events_without_lane
        )
        second = promote_wave8_madagascar_contracts(
            copy.deepcopy(self.hced_rows),
            copy.deepcopy(entities),
            copy.deepcopy(self.existing_events_without_lane),
        )
        self.assertEqual(first, second)

    def test_installers_and_promoter_fail_closed_on_collisions(self) -> None:
        entities, sources = self._installed()
        entity_id = WAVE8_MADAGASCAR_ENTITIES[0]["id"]
        entities[entity_id] = {**entities[entity_id], "name": "collision"}
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_madagascar_entities(entities)

        source_id = WAVE8_MADAGASCAR_SOURCES[0]["id"]
        sources[source_id] = {**sources[source_id], "title": "collision"}
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_madagascar_sources(sources)

        entities, _ = self._installed()
        entities.pop(MERINA_ID)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_madagascar_contracts(self.hced_rows, entities, [])

        entities, _ = self._installed()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_madagascar_contracts(
                self.hced_rows,
                entities,
                [
                    {
                        "id": "existing_candidate",
                        "name": "Anything",
                        "year": 1895,
                        "hced_candidate_id": "hced-Andriba1895-1",
                    }
                ],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_madagascar_contracts(
                self.hced_rows,
                entities,
                [{"id": "existing_raw", "name": "Tamatave", "year": 1883}],
            )

    def test_duplicate_audits_are_complete_and_current_queues_have_zero_twins(self) -> None:
        self.assertEqual(WAVE8_MADAGASCAR_HCED_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_MADAGASCAR_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_MADAGASCAR_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_MADAGASCAR_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            set(WAVE8_MADAGASCAR_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_MADAGASCAR_EXPECTED_CANDIDATE_IDS,
        )
        for candidate_id, audit in WAVE8_MADAGASCAR_IWBD_ZERO_OVERLAP_AUDIT.items():
            self.assertEqual(audit["aliases"], sorted(set(audit["aliases"])))
            self.assertTrue(all(alias == normalize_label(alias) for alias in audit["aliases"]))
            year = EXPECTED_CANONICAL[candidate_id][1]
            self.assertEqual(audit["years"], [year, year])
            self.assertIn(normalize_label(EXPECTED_CANONICAL[candidate_id][0]), audit["aliases"])

        self.assertEqual(
            validate_wave8_madagascar_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "external_owner_hced_dispositions": 0,
                "hced_duplicate_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 5,
            },
        )

    def test_integration_validator_rejects_new_hced_iwbd_and_release_twins(self) -> None:
        hced_with_twin = copy.deepcopy(self.hced_rows)
        hced_with_twin.append(
            {
                "candidate_id": "hced-other-lane-tamatave",
                "name": "Tamatave",
                "side_1_raw": "A",
                "side_2_raw": "B",
                "year_low": 1883,
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_madagascar_integration_dispositions(
                hced_with_twin, self.iwbd_rows, self.release_events
            )

        iwbd_with_twin = copy.deepcopy(self.iwbd_rows)
        iwbd_with_twin.append(
            {
                "candidate_id": "iwbd-synthetic-tsarasoatra",
                "name": "Tsarasoatra",
                "start_date": "1895-06-29",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            validate_wave8_madagascar_integration_dispositions(
                self.hced_rows, iwbd_with_twin, self.release_events
            )

        release_with_twin = copy.deepcopy(self.release_events)
        release_with_twin.append(
            {
                "id": "release_synthetic_andriba",
                "name": "Andriba",
                "year": 1895,
            }
        )
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_madagascar_integration_dispositions(
                self.hced_rows, self.iwbd_rows, release_with_twin
            )

    def test_location_review_withholds_all_points_and_retains_country(self) -> None:
        point_globals_before = frozenset(HCED_POINT_QUARANTINE_IDS)
        country_globals_before = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(
            WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS,
            WAVE8_MADAGASCAR_CONTRACT_IDS,
        )
        self.assertEqual(WAVE8_MADAGASCAR_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        point_overlap = (
            WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS
            & HCED_POINT_QUARANTINE_IDS
        )
        self.assertIn(
            point_overlap,
            (frozenset(), WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS),
        )
        self.assertEqual(
            WAVE8_MADAGASCAR_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_MADAGASCAR_POINT_QUARANTINE_ADDITIONS,
                "country": WAVE8_MADAGASCAR_COUNTRY_QUARANTINE_ADDITIONS,
            },
        )
        self.assertEqual(
            wave8_madagascar_location_quarantine_additions(),
            WAVE8_MADAGASCAR_LOCATION_QUARANTINE_ADDITIONS,
        )
        self.assertEqual(
            set(WAVE8_MADAGASCAR_LOCATION_QUARANTINE_REASONS),
            WAVE8_MADAGASCAR_CONTRACT_IDS,
        )
        self.assertIn("41.185", WAVE8_MADAGASCAR_LOCATION_QUARANTINE_REASONS["hced-Andriba1895-1"]["reason"])
        self.assertIn("namesake", WAVE8_MADAGASCAR_LOCATION_QUARANTINE_REASONS["hced-Tsarasoatra1895-1"]["reason"])

        _, _, events = self._emit()
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "Madagascar")
            self.assertIn("location_provenance", event)
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), point_globals_before)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), country_globals_before)

    def test_release_artifact_is_either_preintegration_or_fully_integrated(self) -> None:
        release_ids = {
            str(event.get("hced_candidate_id"))
            for event in self.release_events
            if event.get("hced_candidate_id") in WAVE8_MADAGASCAR_CONTRACT_IDS
        }
        self.assertIn(release_ids, (set(), set(WAVE8_MADAGASCAR_CONTRACT_IDS)))
        if release_ids:
            events = [
                event
                for event in self.release_events
                if event.get("hced_candidate_id") in WAVE8_MADAGASCAR_CONTRACT_IDS
            ]
            self.assertEqual(len(events), 5)
            self.assertTrue(all(event["id"].startswith(EVENT_ID_PREFIX) for event in events))
            self.assertTrue(all("geometry" not in event for event in events))

    def test_counts_and_cohorts_are_exact(self) -> None:
        self.assertEqual(
            wave8_madagascar_cohort_counts(),
            {
                "anglo_french_tamatave_expedition_1845": 1,
                "first_franco_hova_war_1883_1885": 1,
                "second_franco_hova_war_1894_1895": 3,
            },
        )
        self.assertEqual(
            wave8_madagascar_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "external_owner_hced_dispositions": 0,
                "hced_duplicate_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 5,
                "new_entities": 2,
                "new_sources": 13,
                "newly_rated_events": 5,
                "outcome_overrides": 0,
                "point_quarantine_additions": 5,
                "promotion_contracts": 5,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 0,
            },
        )


if __name__ == "__main__":
    unittest.main()
