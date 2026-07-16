from __future__ import annotations

import copy
import json
import os
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_central import (
    WAVE7_CENTRAL_HOLD_IDS,
    WAVE7_CENTRAL_PROMOTION_IDS,
    WAVE7_CENTRAL_RESERVED_IDS,
    canonical_row_sha256,
    install_wave7_central_entities,
    install_wave7_central_sources,
    promote_wave7_central_hced_contracts,
    resolve_wave7_central_identity_ids,
    validate_wave7_central_queue_contracts,
    wave7_central_cohort_counts,
)
from military_elo.promotion.wave7_central_data import (
    WAVE7_CENTRAL_ENTITIES,
    WAVE7_CENTRAL_FINAL_AUDIT_SIGNATURE,
    WAVE7_CENTRAL_HOLDS,
    WAVE7_CENTRAL_PROMOTION_CONTRACTS,
    WAVE7_CENTRAL_SOURCES,
    WAVE7_CENTRAL_TRANSITION_YEAR_HOLDS,
)


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = Path(
    os.environ.get(
        "MILITARY_ELO_HCED_QUEUE",
        str(ROOT / "data" / "review" / "hced-candidates.jsonl"),
    )
)


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


class Wave7CentralInventoryTests(unittest.TestCase):
    def test_exact_frozen_inventory(self):
        self.assertEqual(len(WAVE7_CENTRAL_PROMOTION_IDS), 33)
        self.assertEqual(len(WAVE7_CENTRAL_HOLD_IDS), 9)
        self.assertEqual(len(WAVE7_CENTRAL_RESERVED_IDS), 42)
        self.assertTrue(WAVE7_CENTRAL_PROMOTION_IDS.isdisjoint(WAVE7_CENTRAL_HOLD_IDS))
        self.assertEqual(len(WAVE7_CENTRAL_ENTITIES), 15)
        self.assertEqual(len(WAVE7_CENTRAL_SOURCES), 13)
        self.assertEqual(
            WAVE7_CENTRAL_FINAL_AUDIT_SIGNATURE,
            "59293e0243abdbb36254452d7e15d7f454d51687183ab5f0b418b3a8179a57f6",
        )

    def test_exact_promotion_cohort_counts(self):
        self.assertEqual(
            wave7_central_cohort_counts(),
            {
                "greece_artemisium": 1,
                "greece_restored_kingdom": 1,
                "greece_revolutionary": 1,
                "iran_pahlavi": 1,
                "poland_bar_confederation": 3,
                "poland_commonwealth_1792": 1,
                "poland_kosciuszko_1794": 6,
                "poland_november_uprising": 7,
                "poland_warsaw_uprising": 1,
                "serbia_despotate": 1,
                "serbia_empire": 2,
                "serbia_grand_principality": 1,
                "serbia_medieval_kingdom": 1,
                "serbia_principality": 3,
                "serbia_revolutionary": 2,
                "serbian_krajina_knin": 1,
            },
        )

    def test_requested_lane_totals_are_exact(self):
        contracts = WAVE7_CENTRAL_PROMOTION_CONTRACTS.values()
        self.assertEqual(
            sum(row["cohort"].startswith("poland_") for row in contracts), 18
        )
        self.assertEqual(
            sum(
                row["cohort"].startswith("serbia_")
                or row["cohort"].startswith("serbian_")
                for row in contracts
            ),
            11,
        )
        self.assertEqual(
            sum(row["cohort"].startswith("greece_") for row in contracts), 3
        )
        self.assertEqual(sum(row["cohort"] == "iran_pahlavi" for row in contracts), 1)
        self.assertEqual(
            sum(
                row["cohort"] == "greece_civil_war"
                for row in WAVE7_CENTRAL_HOLDS.values()
            ),
            7,
        )

    def test_entities_are_alias_free_non_inheriting_and_parse(self):
        for raw in WAVE7_CENTRAL_ENTITIES:
            entity = Entity.from_dict(raw)
            self.assertEqual(entity.aliases, ())
            self.assertEqual(entity.predecessors, ())
            self.assertIn(
                "no predecessor or successor rating is inherited",
                entity.continuity_note,
            )

    def test_sources_are_direct_and_context_only(self):
        for raw in WAVE7_CENTRAL_SOURCES:
            source = Source.from_dict(raw)
            self.assertTrue(source.url.startswith("https://"))
            self.assertEqual(
                source.evidence_roles,
                ("identity_boundary_or_context_reference",),
            )
            self.assertEqual(source.source_type, "official_or_academic_reference")

    def test_installers_are_deterministic_and_reject_collisions(self):
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        install_wave7_central_entities(entities)
        install_wave7_central_sources(sources)
        first_entities = copy.deepcopy(entities)
        first_sources = copy.deepcopy(sources)
        install_wave7_central_entities(entities)
        install_wave7_central_sources(sources)
        self.assertEqual(entities, first_entities)
        self.assertEqual(sources, first_sources)

        entities[WAVE7_CENTRAL_ENTITIES[0]["id"]]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity ID collision"):
            install_wave7_central_entities(entities)
        sources[WAVE7_CENTRAL_SOURCES[0]["id"]]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source ID collision"):
            install_wave7_central_sources(sources)


class Wave7CentralPolicyTests(unittest.TestCase):
    def test_polish_rebel_series_is_split(self):
        self.assertEqual(
            resolve_wave7_central_identity_ids("Polish Rebels", 1769, 1771),
            ("bar_confederation_forces",),
        )
        self.assertIsNone(
            resolve_wave7_central_identity_ids("Polish Rebels", 1768, 1768)
        )
        self.assertIsNone(
            resolve_wave7_central_identity_ids("Polish Rebels", 1772, 1772)
        )
        self.assertEqual(
            resolve_wave7_central_identity_ids(
                "Polish Rebels",
                1792,
                1792,
                candidate_id="hced-Zielenice1792-1",
            ),
            ("polish_lithuanian_commonwealth_army_1792",),
        )
        self.assertIsNone(
            resolve_wave7_central_identity_ids("Polish Rebels", 1792, 1792)
        )
        self.assertEqual(
            resolve_wave7_central_identity_ids("Polish Rebels", 1794, 1794),
            ("kosciuszko_uprising_forces",),
        )
        self.assertEqual(
            resolve_wave7_central_identity_ids("Polish Rebels", 1830, 1831),
            ("november_uprising_polish_forces",),
        )
        self.assertEqual(
            resolve_wave7_central_identity_ids(
                "Polish Rebels",
                1944,
                1944,
                candidate_id="hced-Warsaw1944-1",
            ),
            ("warsaw_uprising_polish_forces_1944",),
        )
        self.assertIsNone(
            resolve_wave7_central_identity_ids("Polish Rebels", 1944, 1944)
        )

    def test_serbia_sequence_and_transition_years(self):
        safe = {
            1190: "serbian_grand_principality_nemanjic",
            1330: "kingdom_serbia_medieval",
            1355: "serbian_empire_medieval",
            1439: "serbian_despotate",
            1806: "serbian_revolutionary_forces_1804_1815",
            1876: "principality_serbia_1815",
        }
        for year, expected in safe.items():
            with self.subTest(year=year):
                self.assertEqual(
                    resolve_wave7_central_identity_ids("Serbia", year, year),
                    (expected,),
                )
        for year in WAVE7_CENTRAL_TRANSITION_YEAR_HOLDS["serbia"]:
            with self.subTest(transition_year=year):
                self.assertIsNone(
                    resolve_wave7_central_identity_ids("Serbia", year, year)
                )
        self.assertEqual(
            resolve_wave7_central_identity_ids(
                "Serbia", 1995, 1995, candidate_id="hced-Knin1995-1"
            ),
            ("republic_serbian_krajina_forces",),
        )
        self.assertIsNone(
            resolve_wave7_central_identity_ids(
                "Serbia", 1999, 1999, candidate_id="hced-Kossovo1999-1"
            )
        )

    def test_greece_exact_rows_and_civil_war_holds(self):
        self.assertEqual(
            resolve_wave7_central_identity_ids(
                "Greece", -480, -480, candidate_id="hced-Artemisium-480-1"
            ),
            ("hellenic_coalition_artemisium_480_bce",),
        )
        self.assertEqual(
            resolve_wave7_central_identity_ids("Greece", 1821, 1829),
            ("greek_revolutionaries_1821",),
        )
        self.assertEqual(
            resolve_wave7_central_identity_ids("Greece", 1940, 1940),
            ("kingdom_greece_restored",),
        )
        for candidate_id in (
            "hced-Florina1947-1",
            "hced-Florina1949-1",
            "hced-Karpenision1949-1",
            "hced-Kastoria1948-1",
            "hced-Litokhoro1946-1",
            "hced-Roumeli1948-1",
            "hced-Vitsi1949-1",
        ):
            self.assertIsNone(
                resolve_wave7_central_identity_ids(
                    "Greece",
                    WAVE7_CENTRAL_HOLDS[candidate_id]["raw_contract"]["year_low"],
                    WAVE7_CENTRAL_HOLDS[candidate_id]["raw_contract"]["year_high"],
                    candidate_id=candidate_id,
                )
            )

    def test_pahlavi_policy_excludes_both_transition_years(self):
        self.assertEqual(
            resolve_wave7_central_identity_ids("Iran", 1926, 1978),
            ("imperial_state_iran_pahlavi",),
        )
        self.assertIsNone(resolve_wave7_central_identity_ids("Iran", 1925, 1925))
        self.assertIsNone(resolve_wave7_central_identity_ids("Iran", 1979, 1979))
        self.assertEqual(
            resolve_wave7_central_identity_ids(
                "Iran", 1941, 1941, candidate_id="hced-Iran1941-1"
            ),
            ("imperial_state_iran_pahlavi",),
        )

    def test_unknown_candidate_never_falls_through_to_generic_policy(self):
        self.assertIsNone(
            resolve_wave7_central_identity_ids(
                "Iran", 1941, 1941, candidate_id="hced-unreviewed"
            )
        )


@unittest.skipUnless(QUEUE_PATH.exists(), "Wave 7 HCED queue is not available")
class Wave7CentralQueueAndBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hced = _jsonl(QUEUE_PATH)
        cls.release_entities = {
            entity["id"]: entity
            for entity in _json(ROOT / "data" / "release" / "entities.json")
        }
        install_wave7_central_entities(cls.release_entities)
        cls.existing_events = _json(ROOT / "data" / "release" / "events.json")

    def test_all_reviewed_rows_match_complete_queue_fingerprints(self):
        self.assertEqual(
            validate_wave7_central_queue_contracts(self.hced),
            {"reviewed": 42, "promoted": 33, "held": 9},
        )
        by_id = {row["candidate_id"]: row for row in self.hced}
        for candidate_id, contract in {
            **WAVE7_CENTRAL_PROMOTION_CONTRACTS,
            **WAVE7_CENTRAL_HOLDS,
        }.items():
            self.assertEqual(
                canonical_row_sha256(by_id[candidate_id]),
                contract["raw_row_sha256"],
            )

    def test_tamper_duplicate_and_missing_hold_fail_closed(self):
        tampered = copy.deepcopy(self.hced)
        target = next(
            row for row in tampered if row["candidate_id"] == "hced-Iran1941-1"
        )
        target["winner_raw"] = "Iran"
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            validate_wave7_central_queue_contracts(tampered)

        duplicated = list(self.hced)
        duplicated.append(
            copy.deepcopy(
                next(
                    row
                    for row in self.hced
                    if row["candidate_id"] == "hced-Zielenice1792-1"
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "expected one queue row, found 2"):
            validate_wave7_central_queue_contracts(duplicated)

        missing_hold = [
            row for row in self.hced if row["candidate_id"] != "hced-Kossovo1999-1"
        ]
        with self.assertRaisesRegex(ValueError, "hold contract.*found 0"):
            validate_wave7_central_queue_contracts(missing_hold)

    def test_promoter_is_deterministic_schema_valid_and_excludes_holds(self):
        first = promote_wave7_central_hced_contracts(
            self.hced, self.release_entities, self.existing_events
        )
        second = promote_wave7_central_hced_contracts(
            self.hced, self.release_entities, self.existing_events
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first), 33)
        self.assertEqual(
            {event["hced_candidate_id"] for event in first},
            WAVE7_CENTRAL_PROMOTION_IDS,
        )
        self.assertTrue(
            {event["hced_candidate_id"] for event in first}.isdisjoint(
                WAVE7_CENTRAL_HOLD_IDS
            )
        )
        self.assertEqual(
            [(event["year"], event["hced_candidate_id"]) for event in first],
            sorted((event["year"], event["hced_candidate_id"]) for event in first),
        )
        self.assertEqual(len({event["id"] for event in first}), 33)
        self.assertEqual(len({event["canonical_event_key"] for event in first}), 33)
        for event in first:
            Event.from_dict(event)
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["outcome_source_ids"], ["hced_dataset"])
            self.assertEqual(event["outcome_source_family_ids"], ["hced"])
            self.assertGreaterEqual(len(event["source_ids"]), 2)

    def test_high_risk_identity_and_outcome_bindings(self):
        events = {
            event["hced_candidate_id"]: event
            for event in promote_wave7_central_hced_contracts(
                self.hced, self.release_entities, self.existing_events
            )
        }

        artemisium = events["hced-Artemisium-480-1"]
        self.assertEqual(
            {participant["entity_id"] for participant in artemisium["participants"]},
            {"hellenic_coalition_artemisium_480_bce", "achaemenid_empire"},
        )
        self.assertTrue(
            all(
                participant["result_class"] == "stalemate_or_inconclusive"
                for participant in artemisium["participants"]
            )
        )

        knin = events["hced-Knin1995-1"]
        by_entity = {row["entity_id"]: row for row in knin["participants"]}
        self.assertEqual(by_entity["clio_q224_1992_4605be1c"]["side"], "side_a")
        self.assertEqual(by_entity["republic_serbian_krajina_forces"]["side"], "side_b")
        self.assertIn(
            "defeat", by_entity["republic_serbian_krajina_forces"]["result_class"]
        )

        iran = events["hced-Iran1941-1"]
        by_entity = {row["entity_id"]: row for row in iran["participants"]}
        self.assertEqual(by_entity["united_kingdom"]["side"], "side_a")
        self.assertEqual(by_entity["soviet_union"]["side"], "side_a")
        self.assertEqual(by_entity["united_kingdom"]["contribution"], 0.5)
        self.assertEqual(by_entity["imperial_state_iran_pahlavi"]["side"], "side_b")

        warsaw = events["hced-Warsaw1944-1"]
        by_entity = {row["entity_id"]: row for row in warsaw["participants"]}
        self.assertEqual(by_entity["nazi_germany"]["side"], "side_a")
        self.assertEqual(
            by_entity["warsaw_uprising_polish_forces_1944"]["side"], "side_b"
        )

    def test_entity_window_violation_and_existing_candidate_fail_closed(self):
        entities = copy.deepcopy(self.release_entities)
        entities["imperial_state_iran_pahlavi"]["end_year"] = 1940
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave7_central_hced_contracts(
                self.hced, entities, self.existing_events
            )

        collision = [
            {
                "id": "already-there",
                "name": "Unrelated name",
                "year": 1941,
                "hced_candidate_id": "hced-Iran1941-1",
            }
        ]
        with self.assertRaisesRegex(ValueError, "already promoted"):
            promote_wave7_central_hced_contracts(
                self.hced, self.release_entities, collision
            )


if __name__ == "__main__":
    unittest.main()
