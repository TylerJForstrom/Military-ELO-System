import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_exact import promote_exact_hced_contracts
from military_elo.promotion.wave8_naples import (
    WAVE8_NAPLES_CONTRACT_IDS,
    WAVE8_NAPLES_CONTRACTS,
    WAVE8_NAPLES_ENTITIES,
    WAVE8_NAPLES_EXPECTED_CANDIDATE_IDS,
    WAVE8_NAPLES_FINAL_AUDIT_SIGNATURE,
    WAVE8_NAPLES_HOLD_IDS,
    WAVE8_NAPLES_HOLDS,
    WAVE8_NAPLES_RESERVED_IDS,
    WAVE8_NAPLES_SOURCES,
    WAVE8_NAPLES_TERMINAL_EXCLUSION_IDS,
    WAVE8_NAPLES_TERMINAL_EXCLUSIONS,
    install_wave8_naples_entities,
    install_wave8_naples_sources,
    promote_wave8_naples_contracts,
    validate_wave8_naples_queue_contracts,
    wave8_naples_audit_signature,
    wave8_naples_cohort_counts,
    wave8_naples_counts,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class Wave8NaplesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows()
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _entities(self):
        entities = {entity["id"]: entity for entity in self.release_entities}
        install_wave8_naples_entities(entities)
        return entities

    def _pre_lane_events(self):
        return [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_NAPLES_CONTRACT_IDS
        ]

    def test_inventory_signature_cohorts_and_counts_are_exact(self) -> None:
        self.assertEqual(len(WAVE8_NAPLES_CONTRACT_IDS), 10)
        self.assertEqual(len(WAVE8_NAPLES_TERMINAL_EXCLUSION_IDS), 3)
        self.assertEqual(WAVE8_NAPLES_HOLD_IDS, WAVE8_NAPLES_TERMINAL_EXCLUSION_IDS)
        self.assertIs(WAVE8_NAPLES_HOLDS, WAVE8_NAPLES_TERMINAL_EXCLUSIONS)
        self.assertEqual(
            WAVE8_NAPLES_RESERVED_IDS,
            WAVE8_NAPLES_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            wave8_naples_audit_signature(),
            WAVE8_NAPLES_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_naples_counts(),
            {
                "holds": 3,
                "newly_rated_events": 10,
                "promotion_contracts": 10,
                "reviewed_hced_rows": 13,
                "terminal_exclusions": 3,
            },
        )
        self.assertEqual(
            wave8_naples_cohort_counts(),
            {
                "angevin_byzantine_war": 1,
                "bourbon_naples_french_invasion_1798_1799": 2,
                "garibaldian_campaign_1860": 4,
                "italian_war_naples_1501_1502": 1,
                "restored_bourbon_naples_1806": 1,
                "sicilian_revolution_1848_1849": 1,
            },
        )

    def test_sources_and_alias_free_bounded_identities_parse(self) -> None:
        self.assertEqual((len(WAVE8_NAPLES_ENTITIES), len(WAVE8_NAPLES_SOURCES)), (17, 21))
        source_ids = set()
        for source in WAVE8_NAPLES_SOURCES:
            Source.from_dict(source)
            source_ids.add(source["id"])
        self.assertEqual(len(source_ids), len(WAVE8_NAPLES_SOURCES))

        forbidden_names = {"naples", "neapolitan army", "kingdom of naples"}
        entity_ids = set()
        for entity in WAVE8_NAPLES_ENTITIES:
            Entity.from_dict(entity)
            entity_ids.add(entity["id"])
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertLessEqual(entity["start_year"], entity["end_year"])
            self.assertNotIn(entity["name"].casefold(), forbidden_names)
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertTrue(set(entity["source_ids"]) <= source_ids)
        self.assertEqual(len(entity_ids), len(WAVE8_NAPLES_ENTITIES))

        installed_sources = {source["id"]: source for source in self.release_sources}
        install_wave8_naples_sources(installed_sources)
        for fixture in WAVE8_NAPLES_SOURCES:
            self.assertEqual(installed_sources[fixture["id"]], fixture)

    def test_all_thirteen_semantic_hashes_and_dispositions_fail_closed(self) -> None:
        indexed = {row["candidate_id"]: row for row in self.rows}
        for inventory in (
            WAVE8_NAPLES_CONTRACTS,
            WAVE8_NAPLES_TERMINAL_EXCLUSIONS,
        ):
            for candidate_id, contract in inventory.items():
                self.assertEqual(
                    canonical_hced_row_sha256(indexed[candidate_id]),
                    contract["raw_row_sha256"],
                )
        self.assertEqual(
            validate_wave8_naples_queue_contracts(self.rows),
            {"promotion_contracts": 10, "holds": 3, "reviewed_hced_rows": 13},
        )

        changed_promotion = copy.deepcopy(self.rows)
        next(
            row
            for row in changed_promotion
            if row["candidate_id"] == "hced-Gaeta1806-1"
        )["side_2_raw"] = "timeless Naples"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_naples_queue_contracts(changed_promotion)

        changed_terminal = copy.deepcopy(self.rows)
        next(
            row
            for row in changed_terminal
            if row["candidate_id"] == "hced-Palermo1848-1"
        )["year_low"] = 1848
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_naples_queue_contracts(changed_terminal)

    def test_complete_reservations_block_the_generic_crosswalk(self) -> None:
        owned_rows = [
            row
            for row in self.rows
            if row.get("candidate_id") in WAVE8_NAPLES_RESERVED_IDS
        ]
        result = promote_hced_crosswalk_rows(
            owned_rows,
            owners={},
            curated_seed_keys=set(),
            ensure_candidate_entity=lambda _entity: None,
            reserved_candidate_ids=WAVE8_NAPLES_RESERVED_IDS,
        )
        self.assertEqual(len(owned_rows), 13)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["deferred_label_rows"], [])
        self.assertEqual(result["label_observations"], {})
        self.assertEqual(result["rejections"]["reserved_candidate_contract"], 13)

    def test_terminal_exclusions_pin_the_three_nonpromotions(self) -> None:
        expected_categories = {
            "hced-Ferrara1815-1": "source_conflation_and_duplicate_campaign_actions",
            "hced-Messina1860-1": "noncompetitive_negotiated_occupation",
            "hced-Palermo1848-1": "irreconcilable_year_conflict_and_duplicate",
        }
        self.assertEqual(
            {
                candidate_id: exclusion["hold_category"]
                for candidate_id, exclusion in WAVE8_NAPLES_TERMINAL_EXCLUSIONS.items()
            },
            expected_categories,
        )
        for exclusion in WAVE8_NAPLES_TERMINAL_EXCLUSIONS.values():
            self.assertEqual(exclusion["disposition"], "terminal_exclusion")

        ferrara = WAVE8_NAPLES_TERMINAL_EXCLUSIONS["hced-Ferrara1815-1"]
        self.assertEqual(
            ferrara["duplicate_of_candidate_ids"],
            ["hced-Casaglia1815-1", "hced-Occhiobello, 1815-1"],
        )
        messina = WAVE8_NAPLES_TERMINAL_EXCLUSIONS["hced-Messina1860-1"]
        self.assertIn("pact", messina["hold_reason"].casefold())
        palermo = WAVE8_NAPLES_TERMINAL_EXCLUSIONS["hced-Palermo1848-1"]
        self.assertEqual(
            (
                palermo["raw_identifier_year"],
                palermo["queue_year"],
                palermo["source_described_year"],
            ),
            (1848, 1849, 1860),
        )
        self.assertEqual(
            palermo["duplicate_of_candidate_ids"],
            ["hced-Palermo1860-1"],
        )

    def test_exact_sides_distinguish_every_regime_and_campaign(self) -> None:
        expected_sides = {
            "hced-Berat1281-1": (
                {"byzantine_berat_relief_army_1281"},
                {"angevin_sicily_berat_army_1281"},
            ),
            "hced-Taranto1501-1502-1": (
                {"spanish_taranto_besieging_force_1501_1502"},
                {"aragonese_neapolitan_taranto_garrison_1501_1502"},
            ),
            "hced-Civita Castelana1798-1": (
                {"macdonald_french_division_civita_castellana_1798"},
                {"bourbon_naples_field_army_1798"},
            ),
            "hced-Naples1799-1": (
                {
                    "championnet_french_army_naples_1799",
                    "parthenopean_republican_forces_1799",
                },
                {"neapolitan_royalist_lazzari_1799"},
            ),
            "hced-Gaeta1806-1": (
                {"massena_french_gaeta_corps_1806"},
                {"restored_bourbon_gaeta_garrison_1806"},
            ),
            "hced-Catania1849-1": (
                {"two_sicilies_royal_army_sicily_1848_1849"},
                {"sicilian_revolutionary_state_forces_1848_1849"},
            ),
            "hced-Calatafimi1860-1": (
                {"garibaldian_southern_army_1860"},
                {"two_sicilies_royal_army_1860"},
            ),
            "hced-Palermo1860-1": (
                {"garibaldian_southern_army_1860"},
                {"two_sicilies_royal_army_1860"},
            ),
            "hced-Milazzo1860-1": (
                {"garibaldian_southern_army_1860"},
                {"two_sicilies_royal_army_1860"},
            ),
            "hced-Volturno1860-1": (
                {"garibaldian_southern_army_1860"},
                {"two_sicilies_royal_army_1860"},
            ),
        }
        self.assertEqual(set(expected_sides), WAVE8_NAPLES_CONTRACT_IDS)
        for candidate_id, (side_1, side_2) in expected_sides.items():
            contract = WAVE8_NAPLES_CONTRACTS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), side_1)
            self.assertEqual(set(contract["side_2_entity_ids"]), side_2)
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

        all_ids = {item for sides in expected_sides.values() for side in sides for item in side}
        self.assertNotIn("kingdom_sardinia_piedmont", all_ids)
        self.assertNotIn("murat_kingdom_naples", all_ids)
        self.assertNotIn("kingdom_two_sicilies", all_ids)

    def test_ten_events_emit_with_direct_outcome_provenance(self) -> None:
        emitted = promote_wave8_naples_contracts(
            self.rows,
            self._entities(),
            self._pre_lane_events(),
        )
        self.assertEqual(len(emitted), 10)
        by_candidate = {event["hced_candidate_id"]: event for event in emitted}
        self.assertEqual(set(by_candidate), WAVE8_NAPLES_CONTRACT_IDS)
        source_by_id = {source["id"]: source for source in WAVE8_NAPLES_SOURCES}

        for candidate_id, event in by_candidate.items():
            Event.from_dict(event)
            contract = WAVE8_NAPLES_CONTRACTS[candidate_id]
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
            self.assertEqual(winners, set(contract["side_1_entity_ids"]))
            self.assertEqual(losers, set(contract["side_2_entity_ids"]))
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertNotIn("hced_dataset", event["outcome_source_ids"])
            self.assertTrue(set(event["outcome_source_ids"]) <= set(event["source_ids"]))
            for source_id in event["outcome_source_ids"]:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])

        taranto = by_candidate["hced-Taranto1501-1502-1"]
        self.assertEqual((taranto["year"], taranto["end_year"]), (1501, 1502))
        self.assertEqual(taranto["date_precision"], "year_range")
        civita = by_candidate["hced-Civita Castelana1798-1"]
        self.assertEqual(civita["name"], "Battle of Civita Castellana")
        self.assertEqual(civita["aliases"], ["Civita Castelana"])

    def test_volturno_actor_correction_does_not_reverse_the_outcome(self) -> None:
        contract = WAVE8_NAPLES_CONTRACTS["hced-Volturno1860-1"]
        participants = {
            *contract["side_1_entity_ids"],
            *contract["side_2_entity_ids"],
        }
        self.assertEqual(
            participants,
            {"garibaldian_southern_army_1860", "two_sicilies_royal_army_1860"},
        )
        self.assertFalse(any("piedmont" in item or "sardinia" in item for item in participants))
        self.assertEqual(contract["winner_side"], 1)
        self.assertFalse(contract["source_outcome_override"])

        changed = copy.deepcopy(WAVE8_NAPLES_CONTRACTS)
        changed["hced-Volturno1860-1"]["winner_side"] = 2
        with self.assertRaisesRegex(ValueError, "outcome drift"):
            promote_exact_hced_contracts(
                self.rows,
                self._entities(),
                self._pre_lane_events(),
                changed,
                lane_name="Wave 8 Naples reversal test",
                event_id_prefix="test_wave8_naples_",
            )

    def test_exact_helper_rejects_unproven_override_and_duplicate_promotion(self) -> None:
        changed = copy.deepcopy(WAVE8_NAPLES_CONTRACTS)
        changed["hced-Gaeta1806-1"]["source_outcome_override"] = True
        changed["hced-Gaeta1806-1"]["outcome_source_ids"] = []
        with self.assertRaisesRegex(ValueError, "outcome override lacks direct sources"):
            promote_exact_hced_contracts(
                self.rows,
                self._entities(),
                self._pre_lane_events(),
                changed,
                lane_name="Wave 8 Naples override test",
                event_id_prefix="test_wave8_naples_",
            )

        emitted = promote_wave8_naples_contracts(
            self.rows,
            self._entities(),
            self._pre_lane_events(),
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_naples_contracts(
                self.rows,
                self._entities(),
                [*self._pre_lane_events(), emitted[0]],
            )


if __name__ == "__main__":
    unittest.main()
