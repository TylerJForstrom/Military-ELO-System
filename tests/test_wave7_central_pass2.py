from __future__ import annotations

import copy
import json
import os
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_central_pass2 import (
    WAVE7_CENTRAL_PASS2_HOLD_IDS,
    WAVE7_CENTRAL_PASS2_PROMOTION_IDS,
    WAVE7_CENTRAL_PASS2_RESERVED_IDS,
    canonical_row_sha256,
    install_wave7_central_pass2_entities,
    install_wave7_central_pass2_sources,
    promote_wave7_central_pass2_hced_contracts,
    resolve_wave7_central_pass2_identity_ids,
    validate_wave7_central_pass2_queue_contracts,
    wave7_central_pass2_cohort_counts,
    wave7_central_pass2_hold_counts,
)
from military_elo.promotion.wave7_central_pass2_data import (
    WAVE7_CENTRAL_PASS2_ENTITIES,
    WAVE7_CENTRAL_PASS2_FINAL_AUDIT_SIGNATURE,
    WAVE7_CENTRAL_PASS2_HOLDS,
    WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS,
    WAVE7_CENTRAL_PASS2_SOURCES,
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


class Wave7CentralPass2InventoryTests(unittest.TestCase):
    def test_exact_frozen_inventory(self):
        self.assertEqual(len(WAVE7_CENTRAL_PASS2_PROMOTION_IDS), 31)
        self.assertEqual(len(WAVE7_CENTRAL_PASS2_HOLD_IDS), 11)
        self.assertEqual(len(WAVE7_CENTRAL_PASS2_RESERVED_IDS), 42)
        self.assertTrue(
            WAVE7_CENTRAL_PASS2_PROMOTION_IDS.isdisjoint(WAVE7_CENTRAL_PASS2_HOLD_IDS)
        )
        self.assertEqual(len(WAVE7_CENTRAL_PASS2_ENTITIES), 7)
        self.assertEqual(len(WAVE7_CENTRAL_PASS2_SOURCES), 16)
        self.assertEqual(
            WAVE7_CENTRAL_PASS2_FINAL_AUDIT_SIGNATURE,
            "1b80ab5a498c802125f0870864a90d14f64aa72243acbaa08b0f5bb3ffeccd01",
        )

    def test_cohort_and_hold_counts_are_frozen(self):
        self.assertEqual(
            wave7_central_pass2_cohort_counts(),
            {
                "abushiri_revolt": 1,
                "albania_lezhe": 6,
                "albania_savra": 1,
                "hashemite_arab_revolt": 7,
                "piedmont_sardinia": 10,
                "samnite_social_war": 1,
                "samnite_wars": 5,
            },
        )
        self.assertEqual(
            wave7_central_pass2_hold_counts(),
            {
                "chronology_or_duplicate": 1,
                "coalition_or_party_gap": 7,
                "cross_year_chronology": 1,
                "disputed_outcome": 1,
                "published_duplicate": 1,
            },
        )
        self.assertEqual(
            sum(row["latent"] for row in WAVE7_CENTRAL_PASS2_HOLDS.values()),
            10,
        )

    def test_current_inventory_has_fourteen_samnite_labelled_rows(self):
        reviewed = {
            **WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS,
            **WAVE7_CENTRAL_PASS2_HOLDS,
        }
        samnite = {
            candidate_id
            for candidate_id, row in reviewed.items()
            if "samnit" in row["raw_contract"]["side_1_raw"].casefold()
            or "samnit" in row["raw_contract"]["side_2_raw"].casefold()
        }
        self.assertEqual(len(samnite), 14)
        self.assertEqual(
            len(samnite & WAVE7_CENTRAL_PASS2_PROMOTION_IDS),
            6,
        )
        self.assertEqual(len(samnite & WAVE7_CENTRAL_PASS2_HOLD_IDS), 8)

    def test_entities_are_alias_free_non_inheriting_and_parse(self):
        for raw in WAVE7_CENTRAL_PASS2_ENTITIES:
            entity = Entity.from_dict(raw)
            self.assertEqual(entity.aliases, ())
            self.assertEqual(entity.predecessors, ())
            self.assertIn(
                "no predecessor or successor rating is inherited",
                entity.continuity_note,
            )

    def test_sources_are_direct_context_only_and_parse(self):
        for raw in WAVE7_CENTRAL_PASS2_SOURCES:
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
        install_wave7_central_pass2_entities(entities)
        install_wave7_central_pass2_sources(sources)
        first_entities = copy.deepcopy(entities)
        first_sources = copy.deepcopy(sources)
        install_wave7_central_pass2_entities(entities)
        install_wave7_central_pass2_sources(sources)
        self.assertEqual(entities, first_entities)
        self.assertEqual(sources, first_sources)

        entities[WAVE7_CENTRAL_PASS2_ENTITIES[0]["id"]]["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity ID collision"):
            install_wave7_central_pass2_entities(entities)
        sources[WAVE7_CENTRAL_PASS2_SOURCES[0]["id"]]["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source ID collision"):
            install_wave7_central_pass2_sources(sources)


class Wave7CentralPass2PolicyTests(unittest.TestCase):
    def test_piedmont_is_sardinia_without_successor_inheritance(self):
        self.assertEqual(
            resolve_wave7_central_pass2_identity_ids("Piedmont", 1796, 1860),
            ("kingdom_sardinia_piedmont",),
        )
        self.assertIsNone(
            resolve_wave7_central_pass2_identity_ids("Piedmont", 1861, 1861)
        )
        self.assertIsNone(
            resolve_wave7_central_pass2_identity_ids(
                "Piedmont", 1860, 1860, candidate_id="hced-Gaeta1860-1"
            )
        )

    def test_albania_is_candidate_specific_at_savra_and_held_in_1939(self):
        self.assertEqual(
            resolve_wave7_central_pass2_identity_ids(
                "Albania", 1385, 1385, candidate_id="hced-Savra1385-1"
            ),
            ("balsa_ii_forces_savra_1385",),
        )
        self.assertIsNone(
            resolve_wave7_central_pass2_identity_ids("Albania", 1385, 1385)
        )
        self.assertEqual(
            resolve_wave7_central_pass2_identity_ids("Albania", 1444, 1468),
            ("league_lezhe_forces",),
        )
        self.assertIsNone(
            resolve_wave7_central_pass2_identity_ids(
                "Albania", 1939, 1939, candidate_id="hced-Albania1939-1"
            )
        )

    def test_arab_rebel_label_does_not_cross_revolts(self):
        self.assertEqual(
            resolve_wave7_central_pass2_identity_ids(
                "Arab Rebels", 1889, 1889, candidate_id="hced-Pangani1889-1"
            ),
            ("abushiri_revolt_forces",),
        )
        self.assertIsNone(
            resolve_wave7_central_pass2_identity_ids("Arab Rebels", 1889, 1889)
        )
        self.assertEqual(
            resolve_wave7_central_pass2_identity_ids("Arab Rebels", 1916, 1919),
            ("hashemite_arab_revolt_forces",),
        )

    def test_samnite_identity_splits_ancient_and_social_war_actors(self):
        self.assertEqual(
            resolve_wave7_central_pass2_identity_ids("Samnites", -342, -293),
            ("samnite_confederation_wars",),
        )
        self.assertIsNone(
            resolve_wave7_central_pass2_identity_ids("Samnites", -289, -92)
        )
        self.assertEqual(
            resolve_wave7_central_pass2_identity_ids("Samnites", -90, -90),
            ("samnite_social_war_insurgents",),
        )
        self.assertEqual(
            resolve_wave7_central_pass2_identity_ids("Samnite Rebels", -89, -89),
            ("samnite_social_war_insurgents",),
        )

    def test_all_holds_and_unknown_candidates_fail_closed(self):
        for candidate_id, hold in WAVE7_CENTRAL_PASS2_HOLDS.items():
            raw = hold["raw_contract"]
            for label in (raw["side_1_raw"], raw["side_2_raw"]):
                self.assertIsNone(
                    resolve_wave7_central_pass2_identity_ids(
                        label,
                        raw["year_low"],
                        raw["year_high"],
                        candidate_id=candidate_id,
                    ),
                    candidate_id,
                )
        self.assertIsNone(
            resolve_wave7_central_pass2_identity_ids(
                "Piedmont", 1848, 1848, candidate_id="hced-unreviewed"
            )
        )


@unittest.skipUnless(QUEUE_PATH.exists(), "Wave 7 HCED queue is not available")
class Wave7CentralPass2QueueAndBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hced = _jsonl(QUEUE_PATH)
        cls.release_entities = {
            entity["id"]: entity
            for entity in _json(ROOT / "data" / "release" / "entities.json")
        }
        install_wave7_central_pass2_entities(cls.release_entities)
        cls.existing_events = [
            event
            for event in _json(ROOT / "data" / "release" / "events.json")
            if event.get("hced_candidate_id") not in WAVE7_CENTRAL_PASS2_PROMOTION_IDS
        ]

    def test_all_reviewed_rows_match_complete_queue_fingerprints(self):
        self.assertEqual(
            validate_wave7_central_pass2_queue_contracts(self.hced),
            {
                "reviewed": 42,
                "promoted": 31,
                "held": 11,
                "latent_held": 10,
                "duplicate_held": 1,
            },
        )
        by_id = {row["candidate_id"]: row for row in self.hced}
        for candidate_id, contract in {
            **WAVE7_CENTRAL_PASS2_PROMOTION_CONTRACTS,
            **WAVE7_CENTRAL_PASS2_HOLDS,
        }.items():
            self.assertEqual(
                canonical_row_sha256(by_id[candidate_id]),
                contract["raw_row_sha256"],
            )

    def test_tamper_duplicate_and_missing_hold_fail_closed(self):
        tampered = copy.deepcopy(self.hced)
        target = next(
            row for row in tampered if row["candidate_id"] == "hced-Caudine Forks-321-1"
        )
        target["winner_raw"] = "Rome"
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            validate_wave7_central_pass2_queue_contracts(tampered)

        duplicated = list(self.hced)
        duplicated.append(
            copy.deepcopy(
                next(
                    row
                    for row in self.hced
                    if row["candidate_id"] == "hced-Mondovi1796-1"
                )
            )
        )
        with self.assertRaisesRegex(ValueError, "expected one queue row, found 2"):
            validate_wave7_central_pass2_queue_contracts(duplicated)

        missing_hold = [
            row for row in self.hced if row["candidate_id"] != "hced-Albania1939-1"
        ]
        with self.assertRaisesRegex(ValueError, "hold contract.*found 0"):
            validate_wave7_central_pass2_queue_contracts(missing_hold)

    def test_promoter_is_deterministic_schema_valid_and_excludes_holds(self):
        first = promote_wave7_central_pass2_hced_contracts(
            self.hced, self.release_entities, self.existing_events
        )
        second = promote_wave7_central_pass2_hced_contracts(
            self.hced, self.release_entities, self.existing_events
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first), 31)
        self.assertEqual(
            {event["hced_candidate_id"] for event in first},
            WAVE7_CENTRAL_PASS2_PROMOTION_IDS,
        )
        self.assertTrue(
            {event["hced_candidate_id"] for event in first}.isdisjoint(
                WAVE7_CENTRAL_PASS2_HOLD_IDS
            )
        )
        self.assertEqual(
            [(event["year"], event["hced_candidate_id"]) for event in first],
            sorted((event["year"], event["hced_candidate_id"]) for event in first),
        )
        self.assertEqual(len({event["id"] for event in first}), 31)
        self.assertEqual(len({event["canonical_event_key"] for event in first}), 31)
        for event in first:
            Event.from_dict(event)
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["outcome_source_ids"], ["hced_dataset"])
            self.assertEqual(event["outcome_source_family_ids"], ["hced"])
            self.assertGreaterEqual(len(event["source_ids"]), 2)

    def test_high_risk_identity_and_outcome_bindings(self):
        events = {
            event["hced_candidate_id"]: event
            for event in promote_wave7_central_pass2_hced_contracts(
                self.hced, self.release_entities, self.existing_events
            )
        }

        savra = {
            row["entity_id"]: row for row in events["hced-Savra1385-1"]["participants"]
        }
        self.assertEqual(savra["ottoman_empire"]["side"], "side_a")
        self.assertEqual(savra["balsa_ii_forces_savra_1385"]["side"], "side_b")

        pangani = {
            row["entity_id"]: row
            for row in events["hced-Pangani1889-1"]["participants"]
        }
        self.assertEqual(pangani["german_empire"]["side"], "side_a")
        self.assertEqual(pangani["abushiri_revolt_forces"]["side"], "side_b")
        self.assertNotIn("hashemite_arab_revolt_forces", pangani)

        medina_event = events["hced-Medina, Saudi Arabia1916-1919-1"]
        medina = {row["entity_id"]: row for row in medina_event["participants"]}
        self.assertEqual(medina_event["end_year"], 1919)
        self.assertEqual(medina["ottoman_empire"]["side"], "side_a")
        self.assertEqual(medina["hashemite_arab_revolt_forces"]["side"], "side_b")

        caudine = {
            row["entity_id"]: row
            for row in events["hced-Caudine Forks-321-1"]["participants"]
        }
        self.assertEqual(caudine["samnite_confederation_wars"]["side"], "side_a")
        acerrae = {
            row["entity_id"]: row for row in events["hced-Acerrae-90-1"]["participants"]
        }
        self.assertEqual(acerrae["roman_republic"]["side"], "side_a")
        self.assertEqual(acerrae["samnite_social_war_insurgents"]["side"], "side_b")
        self.assertNotIn("samnite_confederation_wars", acerrae)

        aqaba = {
            row["entity_id"]: row for row in events["hced-Aqaba1917-1"]["participants"]
        }
        self.assertEqual(aqaba["hashemite_arab_revolt_forces"]["side"], "side_a")
        self.assertEqual(aqaba["ottoman_empire"]["side"], "side_b")

        ancona = {
            row["entity_id"]: row for row in events["hced-Ancona1860-1"]["participants"]
        }
        self.assertEqual(ancona["kingdom_sardinia_piedmont"]["side"], "side_a")
        self.assertEqual(
            ancona["clio_it_papal_state_1_755_50394c66"]["side"],
            "side_b",
        )

    def test_published_albania_duplicate_is_held_not_emitted(self):
        self.assertEqual(
            WAVE7_CENTRAL_PASS2_HOLDS["hced-Albania1939-1"]["category"],
            "published_duplicate",
        )
        events = promote_wave7_central_pass2_hced_contracts(
            self.hced, self.release_entities, self.existing_events
        )
        self.assertNotIn(
            "hced-Albania1939-1",
            {event["hced_candidate_id"] for event in events},
        )

    def test_entity_window_and_existing_candidate_collisions_fail_closed(self):
        entities = copy.deepcopy(self.release_entities)
        entities["kingdom_sardinia_piedmont"]["end_year"] = 1847
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave7_central_pass2_hced_contracts(
                self.hced, entities, self.existing_events
            )

        collision = [
            {
                "id": "already-there",
                "name": "Unrelated name",
                "year": 1796,
                "hced_candidate_id": "hced-Mondovi1796-1",
            }
        ]
        with self.assertRaisesRegex(ValueError, "already promoted"):
            promote_wave7_central_pass2_hced_contracts(
                self.hced, self.release_entities, collision
            )


if __name__ == "__main__":
    unittest.main()
