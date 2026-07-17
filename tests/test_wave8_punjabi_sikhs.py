import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion import wave8_punjabi_sikhs as lane
from military_elo.promotion import wave8_sikh_punjab as sikh_lane
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_punjabi_sikhs_"
FINAL_AUDIT_SIGNATURE = (
    "1567c5bbb41a7bd394dc82497cd96aaaa79b51e6c919403b5483b7ae27a4e48d"
)
EXACT_CANDIDATE_ID_SHA256 = (
    "57a22918f5385d4ef906fe512d091de5b98881744ffd27b4a3d195df70de1715"
)

ANANDGARH_BESIEGERS_ID = "mughal_hill_siege_coalition_anandgarh_1704"
ANANDGARH_KHALSA_ID = "guru_gobind_singh_khalsa_garrison_anandgarh_1704"
SARSA_PURSUERS_ID = "wazir_khan_mughal_hill_pursuit_force_sarsa_1704"
SARSA_KHALSA_ID = "guru_gobind_singh_withdrawal_column_sarsa_1704"

EXPECTED_RAW_HASHES = {
    "hced-Anandpur (1st)1704-1": (
        "aa3745fbe0ebe64ec9b7ed0869838758a688f787bba3fc513ca6736b97cd8994"
    ),
    "hced-Anandpur (2nd)1704-1": (
        "b89dadee7b359f6bb5ec32ef6a62404761a91d842fb7edce8c013631d8e2b9a7"
    ),
    "hced-Anandpur1700-1": (
        "3f992b5f13d444a3178aab638c90b8a7fd465615d6b8c6cc9f1fa95bf6146590"
    ),
    "hced-Sarsa1704-1": (
        "ea56823b804978afc538de6e7de6e145c8b9169f1822ea4a63b5df8b930c8d99"
    ),
}

EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Anandpur (2nd)1704-1": (
        {ANANDGARH_BESIEGERS_ID},
        {ANANDGARH_KHALSA_ID},
    ),
    "hced-Sarsa1704-1": ({SARSA_PURSUERS_ID}, {SARSA_KHALSA_ID}),
}

EXPECTED_CANONICAL = {
    "hced-Anandpur (2nd)1704-1": (
        "Final Siege and Evacuation of Anandgarh",
        "final siege and evacuation, May-20/21 December 1704",
        "month_to_day_range",
        "siege_termination_and_forced_evacuation",
        0.91,
    ),
    "hced-Sarsa1704-1": (
        "Battle at the Sarsa Crossing",
        "21 December 1704",
        "day",
        "withdrawal_column_attack_and_dispersal",
        0.93,
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


def _candidate_digest(values):
    return hashlib.sha256(
        "".join(f"{value}\n" for value in sorted(map(str, values))).encode()
    ).hexdigest()


class Wave8PunjabiSikhsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data/review/hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data/review/iwbd-candidates.jsonl")
        cls.funnel = _json(ROOT / "build/hced-unresolved-label-funnel.json")
        cls.release_entities = _json(ROOT / "data/release/entities.json")
        cls.release_events = _json(ROOT / "data/release/events.json")
        cls.release_sources = _json(ROOT / "data/release/sources.json")
        cls.hced_by_id = {
            str(row["candidate_id"]): row for row in cls.hced_rows
        }
        cls.exact_rows = [
            row
            for row in cls.hced_rows
            if "punjabi sikhs"
            in {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
        ]

    def _installed(self):
        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_PUNJABI_SIKHS_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in lane_entity_ids
        }
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_PUNJABI_SIKHS_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in lane_source_ids
        }
        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_PUNJABI_SIKHS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        lane.install_wave8_punjabi_sikhs_entities(entities)
        lane.install_wave8_punjabi_sikhs_sources(sources)
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_punjabi_sikhs_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_exact_inventory_funnel_and_raw_rows_are_pinned(self) -> None:
        exact_by_id = {
            str(row["candidate_id"]): row for row in self.exact_rows
        }
        self.assertEqual(set(exact_by_id), set(EXPECTED_RAW_HASHES))
        self.assertEqual(
            lane.WAVE8_PUNJABI_SIKHS_EXPECTED_CANDIDATE_IDS,
            set(EXPECTED_RAW_HASHES),
        )
        self.assertEqual(
            lane.WAVE8_PUNJABI_SIKHS_ROW_HASHES,
            EXPECTED_RAW_HASHES,
        )
        self.assertEqual(_candidate_digest(exact_by_id), EXACT_CANDIDATE_ID_SHA256)
        for candidate_id, expected_hash in EXPECTED_RAW_HASHES.items():
            self.assertEqual(
                canonical_hced_row_sha256(exact_by_id[candidate_id]),
                expected_hash,
            )

        self.assertEqual(
            lane.WAVE8_PUNJABI_SIKHS_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
            EXACT_CANDIDATE_ID_SHA256,
        )
        historical_funnel = {
            "labels": [
                {
                    "centuries": {"CE_17": 1, "CE_18": 3},
                    "event_candidate_id_sha256": (
                        lane.WAVE8_PUNJABI_SIKHS_FUNNEL_EVENT_CANDIDATE_ID_SHA256
                    ),
                    "events_touched": 4,
                    "failure_cases": {"zero_time_valid_candidates": 4},
                    "label": "punjabi sikhs",
                    "sole_blocker_events": 4,
                    "unresolved_side_attempts": 4,
                }
            ],
            "row_label_data": [
                {
                    "blocker_labels": ["punjabi sikhs"],
                    "candidate_id": candidate_id,
                    "greedy_eligible": True,
                    "sole_blocker_label": "punjabi sikhs",
                }
                for candidate_id in sorted(EXPECTED_RAW_HASHES)
            ],
        }
        labels = [
            item
            for item in historical_funnel["labels"]
            if item.get("label") == "punjabi sikhs"
        ]
        self.assertEqual(len(labels), 1)
        label = labels[0]
        self.assertEqual(label["event_candidate_id_sha256"], EXACT_CANDIDATE_ID_SHA256)
        self.assertEqual(label["events_touched"], 4)
        self.assertEqual(label["unresolved_side_attempts"], 4)
        self.assertEqual(label["sole_blocker_events"], 4)
        self.assertEqual(label["failure_cases"]["zero_time_valid_candidates"], 4)
        self.assertEqual(label["centuries"], {"CE_17": 1, "CE_18": 3})
        funnel_rows = {
            str(item["candidate_id"]): item
            for item in historical_funnel["row_label_data"]
            if "punjabi sikhs" in item.get("blocker_labels", [])
        }
        self.assertEqual(set(funnel_rows), set(EXPECTED_RAW_HASHES))
        for item in funnel_rows.values():
            self.assertEqual(item["sole_blocker_label"], "punjabi sikhs")
            self.assertTrue(item["greedy_eligible"])

        self.assertFalse(
            any(
                item.get("label") == "punjabi sikhs"
                for item in self.funnel.get("labels", [])
            ),
            "the completed Punjabi Sikhs lane must not remain unresolved",
        )
        self.assertFalse(
            any(
                "punjabi sikhs" in item.get("blocker_labels", [])
                for item in self.funnel.get("row_label_data", [])
            ),
            "no live funnel row may still cite the resolved 'punjabi sikhs' blocker",
        )
        live_row_candidate_ids = {
            str(item.get("candidate_id"))
            for item in self.funnel.get("row_label_data", [])
        }
        self.assertFalse(
            set(lane.WAVE8_PUNJABI_SIKHS_CONTRACT_IDS) & live_row_candidate_ids,
            "promoted Punjabi Sikhs candidates must be absent from the live funnel",
        )

    def test_adjacent_label_and_company_era_boundaries_are_complete(self) -> None:
        for label, pin in lane.WAVE8_PUNJABI_SIKHS_ADJACENT_LABEL_INVENTORY_PINS.items():
            candidate_ids = {
                str(row["candidate_id"])
                for row in self.hced_rows
                if label
                in {
                    normalize_label(row.get("side_1_raw")),
                    normalize_label(row.get("side_2_raw")),
                }
            }
            self.assertEqual(len(candidate_ids), pin["count"])
            self.assertEqual(_candidate_digest(candidate_ids), pin["candidate_id_sha256"])
        self.assertEqual(
            lane.WAVE8_PUNJABI_SIKHS_ADJACENT_LABEL_INVENTORY_PINS["sikh empire"][
                "count"
            ],
            0,
        )
        company_ids = {
            str(row["candidate_id"])
            for row in self.hced_rows
            if row.get("year_low") is not None
            and row.get("year_high") is not None
            and 1845 <= int(row["year_low"])
            and int(row["year_high"]) <= 1849
            and {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
            & {"punjab", "punjabi sikhs", "sikh punjab", "sikhs"}
        }
        self.assertEqual(
            company_ids,
            lane.WAVE8_PUNJABI_SIKHS_COMPANY_ERA_CANDIDATE_IDS,
        )
        self.assertEqual(len(company_ids), 13)
        self.assertEqual(
            _candidate_digest(company_ids),
            lane.WAVE8_PUNJABI_SIKHS_COMPANY_ERA_CANDIDATE_ID_SHA256,
        )
        self.assertIn("hced-Baddowal1846-1", company_ids)
        self.assertFalse(company_ids & lane.WAVE8_PUNJABI_SIKHS_RESERVED_IDS)

    def test_sikh_punjab_reciprocal_boundary_is_exact_and_disjoint(self) -> None:
        self.assertFalse(
            lane.WAVE8_PUNJABI_SIKHS_RESERVED_IDS
            & sikh_lane.WAVE8_SIKH_PUNJAB_RESERVED_IDS
        )
        self.assertEqual(
            set(sikh_lane.WAVE8_SIKH_PUNJAB_RESERVED_IDS),
            set(
                lane.WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS[
                    "wave8_sikh_punjab"
                ]["counterpart_reserved_candidate_ids"]
            ),
        )
        reciprocal = sikh_lane.WAVE8_SIKH_PUNJAB_CROSS_LANE_DISPOSITIONS[
            "hced-Anandpur1700-1"
        ]
        self.assertEqual(reciprocal["related_candidate_id"], "hced-Anandpur1701-1")
        self.assertEqual(
            reciprocal["raw_row_sha256"],
            EXPECTED_RAW_HASHES["hced-Anandpur1700-1"],
        )
        local = lane.WAVE8_PUNJABI_SIKHS_CROSS_LANE_DISPOSITIONS[
            "wave8_sikh_punjab"
        ]
        self.assertEqual(local["shared_boundary_candidate_id"], "hced-Anandpur1700-1")
        self.assertEqual(local["related_candidate_id"], "hced-Anandpur1701-1")
        self.assertEqual(local["disposition"], "reciprocal_chronology_twin_hold")
        self.assertEqual(
            local["counterpart_module"],
            "military_elo.promotion.wave8_sikh_punjab",
        )

    def test_dispositions_counts_cohorts_and_signature_are_frozen(self) -> None:
        self.assertEqual(
            lane.WAVE8_PUNJABI_SIKHS_CONTRACT_IDS,
            {"hced-Anandpur (2nd)1704-1", "hced-Sarsa1704-1"},
        )
        self.assertEqual(
            lane.WAVE8_PUNJABI_SIKHS_HOLD_IDS,
            {"hced-Anandpur1700-1", "hced-Anandpur (1st)1704-1"},
        )
        self.assertEqual(lane.WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSION_IDS, set())
        self.assertEqual(lane.WAVE8_PUNJABI_SIKHS_EXCLUSION_IDS, set())
        self.assertIs(
            lane.WAVE8_PUNJABI_SIKHS_EXCLUSIONS,
            lane.WAVE8_PUNJABI_SIKHS_TERMINAL_EXCLUSIONS,
        )
        self.assertEqual(
            lane.validate_wave8_punjabi_sikhs_queue_contracts(self.hced_rows),
            {
                "company_era_boundary_rows": 13,
                "cross_lane_dispositions": 1,
                "holds": 2,
                "promotion_contracts": 2,
                "related_hced_dispositions": 7,
                "reviewed_hced_rows": 4,
                "reviewed_unresolved_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            lane.wave8_punjabi_sikhs_cohort_counts(),
            {"final_anandgarh_siege_1704": 1, "sarsa_withdrawal_action_1704": 1},
        )
        counts = lane.wave8_punjabi_sikhs_counts()
        self.assertEqual(counts["newly_rated_events"], 2)
        self.assertEqual(counts["new_entities"], 4)
        self.assertEqual(counts["new_sources"], 7)
        self.assertEqual(counts["holds"], 2)
        self.assertEqual(counts["terminal_exclusions"], 0)
        self.assertEqual(counts["point_quarantine_additions"], 2)
        self.assertEqual(counts["country_quarantine_additions"], 0)
        self.assertEqual(counts["integration_dispositions"], 8)
        self.assertEqual(counts["touched_hced_rows"], 11)
        self.assertEqual(
            lane.WAVE8_PUNJABI_SIKHS_FINAL_AUDIT_SIGNATURE,
            FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(lane.wave8_punjabi_sikhs_audit_signature(), FINAL_AUDIT_SIGNATURE)
        self.assertEqual(len(bytes.fromhex(FINAL_AUDIT_SIGNATURE)), 32)

    def test_sources_are_parseable_independent_and_authoritative(self) -> None:
        self.assertEqual(len(lane.WAVE8_PUNJABI_SIKHS_SOURCES), 7)
        source_ids = {
            str(source["id"]) for source in lane.WAVE8_PUNJABI_SIKHS_SOURCES
        }
        families = {
            str(source["source_family_id"])
            for source in lane.WAVE8_PUNJABI_SIKHS_SOURCES
        }
        self.assertEqual(len(source_ids), 7)
        self.assertEqual(len(families), 7)
        publishers = {
            str(source["publisher"])
            for source in lane.WAVE8_PUNJABI_SIKHS_SOURCES
        }
        self.assertIn("Oxford University Press", publishers)
        self.assertIn("Cambridge University Press", publishers)
        self.assertIn("Punjabi University, Patiala", publishers)
        for source in lane.WAVE8_PUNJABI_SIKHS_SOURCES:
            Source.from_dict(source)
            self.assertTrue(str(source["url"]).startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
        for contract in lane.WAVE8_PUNJABI_SIKHS_CONTRACTS.values():
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 4)
            self.assertEqual(
                len(contract["outcome_source_family_ids"]),
                len(contract["outcome_source_ids"]),
            )
            for source_id in contract["outcome_source_ids"]:
                source = next(
                    source
                    for source in lane.WAVE8_PUNJABI_SIKHS_SOURCES
                    if source["id"] == source_id
                )
                self.assertIn("outcome", source["evidence_roles"])

    def test_entities_are_parseable_event_bounded_and_never_generic(self) -> None:
        self.assertEqual(len(lane.WAVE8_PUNJABI_SIKHS_ENTITIES), 4)
        entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_PUNJABI_SIKHS_ENTITIES
        }
        used_ids = {
            str(entity_id)
            for contract in lane.WAVE8_PUNJABI_SIKHS_CONTRACTS.values()
            for field in ("side_1_entity_ids", "side_2_entity_ids")
            for entity_id in contract[field]
        }
        self.assertEqual(used_ids, entity_ids)
        source_ids = {
            str(source["id"]) for source in lane.WAVE8_PUNJABI_SIKHS_SOURCES
        }
        forbidden = {
            "punjab",
            "punjabi sikhs",
            "sikh empire",
            "sikh punjab",
            "sikhs",
        }
        for entity in lane.WAVE8_PUNJABI_SIKHS_ENTITIES:
            parsed = Entity.from_dict(entity)
            self.assertEqual((parsed.start_year, parsed.end_year), (1704, 1704))
            self.assertTrue(parsed.kind.startswith("event_bounded_"))
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertTrue(set(entity["source_ids"]) <= source_ids)
            self.assertIn("No rating is inherited", entity["continuity_note"])
            self.assertIn("Sikh Empire", entity["continuity_note"])
            self.assertNotIn(normalize_label(entity["name"]), forbidden)

    def test_contract_dates_actors_outcomes_and_scope_are_exact(self) -> None:
        source_by_id = {
            str(source["id"]): source
            for source in lane.WAVE8_PUNJABI_SIKHS_SOURCES
        }
        for candidate_id, contract in lane.WAVE8_PUNJABI_SIKHS_CONTRACTS.items():
            name, date_text, precision, granularity, confidence = EXPECTED_CANONICAL[
                candidate_id
            ]
            canonical = contract["canonical_event"]
            self.assertEqual(canonical["name"], name)
            self.assertEqual((canonical["year_low"], canonical["year_high"]), (1704, 1704))
            self.assertEqual(canonical["date_text"], date_text)
            self.assertEqual(canonical["date_precision"], precision)
            self.assertEqual(canonical["granularity"], granularity)
            self.assertEqual(contract["confidence"], confidence)
            winners, losers = EXPECTED_WINNERS_AND_LOSERS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), losers)
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract["result_type"], "win")
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertEqual(
                contract["actor_override"],
                "event_bounded_exact_opposing_forces",
            )
            self.assertEqual(
                contract["duplicate_ownership"],
                {
                    "owner_module": "military_elo.promotion.wave8_punjabi_sikhs",
                    "status": "canonical_hced_owner",
                },
            )
            expected_families = sorted(
                {
                    source_by_id[source_id]["source_family_id"]
                    for source_id in contract["outcome_source_ids"]
                }
            )
            self.assertEqual(contract["outcome_source_family_ids"], expected_families)
            row = self.hced_by_id[candidate_id]
            self.assertEqual(row["winner_raw"], row["side_1_raw"])
            self.assertEqual(row["loser_raw"], row["side_2_raw"])
        self.assertIn(
            "does not rate each sortie",
            lane.WAVE8_PUNJABI_SIKHS_CONTRACTS[
                "hced-Anandpur (2nd)1704-1"
            ]["audit_note"],
        )
        self.assertIn(
            "next Chamkaur engagement",
            lane.WAVE8_PUNJABI_SIKHS_CONTRACTS["hced-Sarsa1704-1"]["audit_note"],
        )

    def test_both_uncertain_rows_are_holds_and_unknown_is_never_draw(self) -> None:
        forbidden = {
            "losers",
            "outcome_source_family_ids",
            "outcome_source_ids",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
            "winners",
        }
        for candidate_id, hold in lane.WAVE8_PUNJABI_SIKHS_HOLDS.items():
            self.assertTrue(forbidden.isdisjoint(hold))
            self.assertEqual(hold["disposition"], "hold")
            self.assertEqual(hold["result_type"], "unknown")
            self.assertEqual(hold["reviewed_outcome"], "unknown")
            self.assertTrue(hold["unknown_is_never_draw"])
            self.assertFalse(hold["terminal_exclusion"])
            self.assertIn("draw", hold["hold_reason"].casefold())
            self.assertGreaterEqual(len(hold["evidence_refs"]), 3)
            self.assertEqual(
                hold["duplicate_ownership"]["status"],
                "held_hced_owner",
            )
            self.assertEqual(
                hold["canonical_event"]["year_low"],
                self.hced_by_id[candidate_id]["year_low"],
            )
        self.assertEqual(
            lane.WAVE8_PUNJABI_SIKHS_HOLDS["hced-Anandpur1700-1"][
                "hold_category"
            ],
            "reciprocal_cross_lane_chronology_twin",
        )
        self.assertEqual(
            lane.WAVE8_PUNJABI_SIKHS_HOLDS["hced-Anandpur (1st)1704-1"][
                "hold_category"
            ],
            "unsupported_unique_engagement_boundary",
        )

    def test_related_hced_rows_pin_engagement_and_company_boundaries(self) -> None:
        expected = {
            "hced-Anandpur1701-1",
            "hced-Baddowal1846-1",
            "hced-Basoli1702-1",
            "hced-Chamkaur (1st)1704-1",
            "hced-Chamkaur (2nd)1704-1",
            "hced-Muktsar1705-1",
            "hced-Nirmohgarh1702-1",
        }
        self.assertEqual(
            set(lane.WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS),
            expected,
        )
        for candidate_id, review in (
            lane.WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS.items()
        ):
            self.assertEqual(
                canonical_hced_row_sha256(self.hced_by_id[candidate_id]),
                review["raw_row_sha256"],
            )
        self.assertIn(
            "not_sarsa_duplicate",
            lane.WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS[
                "hced-Chamkaur (2nd)1704-1"
            ]["relationship"],
        )
        self.assertIn(
            "company_era",
            lane.WAVE8_PUNJABI_SIKHS_RELATED_HCED_DISPOSITIONS[
                "hced-Baddowal1846-1"
            ]["disposition"],
        )

    def test_queue_contracts_fail_closed_on_every_relevant_drift(self) -> None:
        for candidate_id in EXPECTED_RAW_HASHES:
            with self.subTest(candidate_id=candidate_id):
                mutated = copy.deepcopy(self.hced_rows)
                next(
                    row for row in mutated if row["candidate_id"] == candidate_id
                )["name"] += " drift"
                with self.assertRaisesRegex(ValueError, "fingerprint changed"):
                    lane.validate_wave8_punjabi_sikhs_queue_contracts(mutated)

        missing = [
            row
            for row in self.hced_rows
            if row["candidate_id"] != "hced-Sarsa1704-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            lane.validate_wave8_punjabi_sikhs_queue_contracts(missing)
        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(copy.deepcopy(self.hced_by_id["hced-Sarsa1704-1"]))
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            lane.validate_wave8_punjabi_sikhs_queue_contracts(duplicated)
        future = [
            *copy.deepcopy(self.hced_rows),
            {
                "candidate_id": "hced-future-punjabi-sikhs-row",
                "name": "Future row",
                "side_1_raw": "Punjabi Sikhs",
                "side_2_raw": "Future opponent",
                "year_low": 1710,
                "year_high": 1710,
            },
        ]
        with self.assertRaisesRegex(ValueError, "exact Punjabi Sikhs inventory changed"):
            lane.validate_wave8_punjabi_sikhs_queue_contracts(future)
        missing_related = [
            row
            for row in self.hced_rows
            if row["candidate_id"] != "hced-Chamkaur (2nd)1704-1"
        ]
        with self.assertRaisesRegex(ValueError, "related HCED boundary changed"):
            lane.validate_wave8_punjabi_sikhs_queue_contracts(missing_related)
        missing_company = [
            row
            for row in self.hced_rows
            if row["candidate_id"] != "hced-Aliwal1846-1"
        ]
        with self.assertRaisesRegex(ValueError, "adjacent 'punjab' inventory changed"):
            lane.validate_wave8_punjabi_sikhs_queue_contracts(missing_company)

    def test_emission_is_two_parseable_wins_with_exact_participants(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 2)
        by_candidate = {
            str(event["hced_candidate_id"]): event for event in events
        }
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertFalse(lane.WAVE8_PUNJABI_SIKHS_HOLD_IDS & set(by_candidate))
        forbidden_ids = {
            "punjab",
            "punjabi_sikhs",
            "sikh_empire",
            "sikh_punjab",
            "sikhs",
        }
        for candidate_id, (expected_winners, expected_losers) in (
            EXPECTED_WINNERS_AND_LOSERS.items()
        ):
            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["year"], 1704)
            self.assertEqual(event["end_year"], 1704)
            self.assertEqual(event["name"], EXPECTED_CANONICAL[candidate_id][0])
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
            self.assertEqual((winners, losers), (expected_winners, expected_losers))
            self.assertFalse((winners | losers) & forbidden_ids)
            terminations = {
                participant["termination"] for participant in event["participants"]
            }
            self.assertNotIn("inconclusive_engagement", terminations)
            self.assertFalse(any("draw" in item for item in terminations))
            contract = lane.WAVE8_PUNJABI_SIKHS_CONTRACTS[candidate_id]
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
        self.assertEqual(
            [event["hced_candidate_id"] for event in events],
            ["hced-Anandpur (2nd)1704-1", "hced-Sarsa1704-1"],
        )

    def test_installs_are_idempotent_and_entity_windows_fail_closed(self) -> None:
        entities, sources, existing = self._installed()
        entities_once = copy.deepcopy(entities)
        sources_once = copy.deepcopy(sources)
        lane.install_wave8_punjabi_sikhs_entities(entities)
        lane.install_wave8_punjabi_sikhs_sources(sources)
        self.assertEqual(entities, entities_once)
        self.assertEqual(sources, sources_once)
        events_1 = lane.promote_wave8_punjabi_sikhs_contracts(
            self.hced_rows, entities, copy.deepcopy(existing)
        )
        events_2 = lane.promote_wave8_punjabi_sikhs_contracts(
            self.hced_rows, entities, copy.deepcopy(existing)
        )
        self.assertEqual(events_1, events_2)

        colliding_entities = copy.deepcopy(entities)
        colliding_entities[ANANDGARH_BESIEGERS_ID] = {"id": ANANDGARH_BESIEGERS_ID}
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_punjabi_sikhs_entities(colliding_entities)
        first_source = str(lane.WAVE8_PUNJABI_SIKHS_SOURCES[0]["id"])
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_punjabi_sikhs_sources(
                {first_source: {"id": first_source}}
            )
        missing_entity = copy.deepcopy(entities)
        missing_entity.pop(SARSA_KHALSA_ID)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_punjabi_sikhs_contracts(
                self.hced_rows, missing_entity, existing
            )
        wrong_window = copy.deepcopy(entities)
        wrong_window[ANANDGARH_KHALSA_ID]["start_year"] = 1705
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_punjabi_sikhs_contracts(
                self.hced_rows, wrong_window, existing
            )

    def test_candidate_canonical_and_raw_duplicate_guards_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        candidate_collision = [
            *copy.deepcopy(existing),
            {
                "id": "future-owner",
                "name": "Unrelated",
                "year": 1704,
                "hced_candidate_id": "hced-Sarsa1704-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_punjabi_sikhs_contracts(
                self.hced_rows, entities, candidate_collision
            )
        canonical_collision = [
            *copy.deepcopy(existing),
            {
                "id": "future-canonical-twin",
                "name": "Battle at the Sarsa Crossing",
                "year": 1704,
            },
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_punjabi_sikhs_contracts(
                self.hced_rows, entities, canonical_collision
            )
        raw_collision = [
            *copy.deepcopy(existing),
            {"id": "future-raw-twin", "name": "Anandpur (2nd)", "year": 1704},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_punjabi_sikhs_contracts(
                self.hced_rows, entities, raw_collision
            )

    def test_duplicate_audit_and_integration_guards_are_complete(self) -> None:
        self.assertEqual(
            set(lane.WAVE8_PUNJABI_SIKHS_IWBD_ZERO_OVERLAP_AUDIT),
            set(EXPECTED_RAW_HASHES),
        )
        for review in lane.WAVE8_PUNJABI_SIKHS_IWBD_ZERO_OVERLAP_AUDIT.values():
            self.assertEqual(review["aliases"], sorted(set(review["aliases"])))
            self.assertTrue(
                all(alias == normalize_label(alias) for alias in review["aliases"])
            )
            self.assertEqual(review["years"], sorted(set(review["years"])))
        self.assertEqual(lane.WAVE8_PUNJABI_SIKHS_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            lane.WAVE8_PUNJABI_SIKHS_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
            {},
        )
        result = lane.validate_wave8_punjabi_sikhs_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            self.release_events,
        )
        self.assertIn(result["release_lane_overlap"], {0, 2})
        self.assertEqual(result["iwbd_probable_twins"], 0)
        self.assertEqual(result["release_probable_twins"], 0)
        self.assertEqual(result["integration_dispositions"], 8)

        iwbd_twin = [
            *copy.deepcopy(self.iwbd_rows),
            {
                "candidate_id": "iwbd-future-sarsa-twin",
                "name": "Battle of Sirsa",
                "start_date": "1704-12-21",
                "end_date": "1704-12-21",
            },
        ]
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            lane.validate_wave8_punjabi_sikhs_integration_dispositions(
                self.hced_rows, iwbd_twin, self.release_events
            )
        release_twin = [
            *copy.deepcopy(self.release_events),
            {
                "id": "future-release-anandgarh-twin",
                "name": "Siege of Anandgarh",
                "year": 1704,
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_punjabi_sikhs_integration_dispositions(
                self.hced_rows, self.iwbd_rows, release_twin
            )
        held_release = [
            *copy.deepcopy(self.release_events),
            {
                "id": "bad-held-owner",
                "name": "Anandpur",
                "year": 1700,
                "hced_candidate_id": "hced-Anandpur1700-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "held rows were emitted"):
            lane.validate_wave8_punjabi_sikhs_integration_dispositions(
                self.hced_rows, self.iwbd_rows, held_release
            )

    def test_integration_release_overlap_is_strictly_all_or_none(self) -> None:
        generated = self._events()
        base = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in lane.WAVE8_PUNJABI_SIKHS_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        empty_result = lane.validate_wave8_punjabi_sikhs_integration_dispositions(
            self.hced_rows, self.iwbd_rows, base
        )
        self.assertEqual(empty_result["release_lane_overlap"], 0)
        full_result = lane.validate_wave8_punjabi_sikhs_integration_dispositions(
            self.hced_rows, self.iwbd_rows, [*base, *generated]
        )
        self.assertEqual(full_result["release_lane_overlap"], 2)
        with self.assertRaisesRegex(ValueError, "partial or duplicate release overlap"):
            lane.validate_wave8_punjabi_sikhs_integration_dispositions(
                self.hced_rows, self.iwbd_rows, [*base, generated[0]]
            )
        with self.assertRaisesRegex(ValueError, "partial or duplicate release overlap"):
            lane.validate_wave8_punjabi_sikhs_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*base, *generated, copy.deepcopy(generated[0])],
            )

    def test_location_quarantines_are_local_complete_and_non_mutating(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        self.assertEqual(
            lane.WAVE8_PUNJABI_SIKHS_POINT_QUARANTINE_ADDITIONS,
            lane.WAVE8_PUNJABI_SIKHS_CONTRACT_IDS,
        )
        self.assertEqual(lane.WAVE8_PUNJABI_SIKHS_COUNTRY_QUARANTINE_ADDITIONS, set())
        self.assertEqual(
            lane.wave8_punjabi_sikhs_location_quarantine_additions(),
            lane.WAVE8_PUNJABI_SIKHS_LOCATION_QUARANTINE_ADDITIONS,
        )
        self.assertEqual(
            set(lane.WAVE8_PUNJABI_SIKHS_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_PUNJABI_SIKHS_CONTRACT_IDS,
        )
        by_candidate = {
            str(event["hced_candidate_id"]): event for event in self._events()
        }
        for candidate_id, event in by_candidate.items():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "India")
            self.assertIn("location_provenance", event)
            self.assertEqual(
                lane.WAVE8_PUNJABI_SIKHS_LOCATION_QUARANTINE_REASONS[candidate_id][
                    "actions"
                ],
                ["withhold_point"],
            )
        sarsa_reason = lane.WAVE8_PUNJABI_SIKHS_LOCATION_QUARANTINE_REASONS[
            "hced-Sarsa1704-1"
        ]["reason"]
        self.assertIn("Gujarat", sarsa_reason)
        self.assertFalse(
            lane.WAVE8_PUNJABI_SIKHS_HOLD_IDS
            & lane.WAVE8_PUNJABI_SIKHS_POINT_QUARANTINE_ADDITIONS
        )
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), before_points)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), before_countries)

    def test_release_artifacts_overlap_all_or_none_without_cross_lane_leakage(self) -> None:
        event_overlap = {
            str(event["hced_candidate_id"]): event
            for event in self.release_events
            if event.get("hced_candidate_id")
            in lane.WAVE8_PUNJABI_SIKHS_CONTRACT_IDS
        }
        self.assertIn(
            set(event_overlap),
            (set(), set(lane.WAVE8_PUNJABI_SIKHS_CONTRACT_IDS)),
        )
        sikh_entity_ids = {
            str(entity["id"]) for entity in sikh_lane.WAVE8_SIKH_PUNJAB_ENTITIES
        }
        for event in event_overlap.values():
            Event.from_dict(event)
            self.assertTrue(str(event["id"]).startswith(EVENT_ID_PREFIX))
            participant_ids = {
                str(participant["entity_id"])
                for participant in event["participants"]
            }
            self.assertFalse(participant_ids & sikh_entity_ids)

        lane_entity_ids = {
            str(entity["id"]) for entity in lane.WAVE8_PUNJABI_SIKHS_ENTITIES
        }
        release_entity_ids = {
            str(entity["id"]) for entity in self.release_entities
        }
        self.assertIn(lane_entity_ids & release_entity_ids, (set(), lane_entity_ids))
        lane_source_ids = {
            str(source["id"]) for source in lane.WAVE8_PUNJABI_SIKHS_SOURCES
        }
        release_source_ids = {
            str(source["id"]) for source in self.release_sources
        }
        self.assertIn(lane_source_ids & release_source_ids, (set(), lane_source_ids))


if __name__ == "__main__":
    unittest.main()
