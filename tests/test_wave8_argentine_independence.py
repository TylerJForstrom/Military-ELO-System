import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_argentine_independence import (
    WAVE8_ARGENTINE_INDEPENDENCE_CONTRACT_IDS,
    WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS,
    WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES,
    WAVE8_ARGENTINE_INDEPENDENCE_EXPECTED_CANDIDATE_IDS,
    WAVE8_ARGENTINE_INDEPENDENCE_FINAL_AUDIT_SIGNATURE,
    WAVE8_ARGENTINE_INDEPENDENCE_HOLD_IDS,
    WAVE8_ARGENTINE_INDEPENDENCE_HOLDS,
    WAVE8_ARGENTINE_INDEPENDENCE_RESERVED_IDS,
    WAVE8_ARGENTINE_INDEPENDENCE_SOURCES,
    WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSION_IDS,
    WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS,
    install_wave8_argentine_independence_entities,
    install_wave8_argentine_independence_sources,
    promote_wave8_argentine_independence_contracts,
    validate_wave8_argentine_independence_queue_contracts,
    wave8_argentine_independence_cohort_counts,
    wave8_argentine_independence_counts,
    wave8_argentine_independence_signature,
)
from military_elo.promotion.wave8_exact import promote_exact_hced_contracts


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


EXPECTED_CANDIDATE_IDS = {
    "hced-Arroyo de la China1814-1",
    "hced-Ayohuma1813-1",
    "hced-Cancha Rayada1813-1",
    "hced-Cotagaita1810-1",
    "hced-Huaqui1811-1",
    "hced-Jujuy1821-1",
    "hced-Pequereque1813-1",
}


EXPECTED_PROMOTIONS = {
    "hced-Arroyo de la China1814-1": {
        "name": "Naval Combat of Arroyo de la China",
        "exact_date": "1814-03-28",
        "outcome": "royalist_victory",
        "revolutionary_commander": "Tomás Nother",
        "royalist_commander": "Jacinto de Romarate",
        "winners": {"romarate_montevideo_royalist_squadron_1814"},
        "losers": {"united_provinces_nother_naval_division_1814"},
    },
    "hced-Ayohuma1813-1": {
        "name": "Battle of Ayohuma",
        "exact_date": "1813-11-14",
        "outcome": "royalist_victory",
        "revolutionary_commander": "Manuel Belgrano",
        "royalist_commander": "Joaquín de la Pezuela",
        "winners": {"pezuela_royalist_army_ayohuma_1813"},
        "losers": {"united_provinces_army_north_ayohuma_1813"},
    },
    "hced-Cotagaita1810-1": {
        "name": "Combat of Cotagaita",
        "exact_date": "1810-10-27",
        "outcome": "royalist_victory",
        "revolutionary_commander": "Antonio González Balcarce",
        "royalist_commander": "José de Córdoba y Rojas",
        "winners": {"cordoba_royalist_force_cotagaita_1810"},
        "losers": {"primera_junta_auxiliary_army_cotagaita_1810"},
    },
    "hced-Huaqui1811-1": {
        "name": "Battle of Huaqui",
        "exact_date": "1811-06-20",
        "outcome": "royalist_victory",
        "revolutionary_commander": "Antonio González Balcarce",
        "royalist_commander": "José Manuel de Goyeneche",
        "winners": {"goyeneche_royalist_army_huaqui_1811"},
        "losers": {"junta_grande_auxiliary_army_huaqui_1811"},
    },
    "hced-Jujuy1821-1": {
        "name": "Battle of León (Día Grande de Jujuy)",
        "exact_date": "1821-04-27",
        "outcome": "revolutionary_victory",
        "revolutionary_commander": "José Ignacio Gorriti",
        "royalist_commander": "Guillermo Marquiegui",
        "winners": {"gorriti_jujuy_militia_leon_1821"},
        "losers": {"marquiegui_royalist_vanguard_leon_1821"},
    },
    "hced-Pequereque1813-1": {
        "name": "Combat of Pequereque",
        "exact_date": "1813-06-19",
        "outcome": "revolutionary_victory",
        "revolutionary_commander": "Cornelio Zelaya",
        "royalist_commander": "Pedro Antonio de Olañeta",
        "winners": {"united_provinces_zelaya_detachment_pequereque_1813"},
        "losers": {"olaneta_royalist_detachment_pequereque_1813"},
    },
}


class Wave8ArgentineIndependenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows()
        cls.entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.sources = _json(ROOT / "data" / "release" / "sources.json")

    def test_complete_inventory_signature_counts_and_cohorts_are_pinned(self) -> None:
        self.assertEqual(
            set(WAVE8_ARGENTINE_INDEPENDENCE_EXPECTED_CANDIDATE_IDS),
            EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            WAVE8_ARGENTINE_INDEPENDENCE_RESERVED_IDS,
            WAVE8_ARGENTINE_INDEPENDENCE_CONTRACT_IDS
            | WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSION_IDS,
        )
        self.assertEqual(
            WAVE8_ARGENTINE_INDEPENDENCE_HOLD_IDS,
            WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSION_IDS,
        )
        self.assertIs(
            WAVE8_ARGENTINE_INDEPENDENCE_HOLDS,
            WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS,
        )
        self.assertEqual(
            (len(WAVE8_ARGENTINE_INDEPENDENCE_CONTRACT_IDS), len(WAVE8_ARGENTINE_INDEPENDENCE_HOLD_IDS)),
            (6, 1),
        )
        self.assertEqual(
            wave8_argentine_independence_signature(),
            WAVE8_ARGENTINE_INDEPENDENCE_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_argentine_independence_cohort_counts(),
            {
                "first_upper_peru_campaign": 2,
                "jujuy_defense_1821": 1,
                "naval_campaign_1814": 1,
                "second_upper_peru_campaign": 2,
            },
        )
        self.assertEqual(
            wave8_argentine_independence_counts(),
            {
                "holds": 1,
                "newly_rated_events": 6,
                "promotion_contracts": 6,
                "reviewed_hced_rows": 7,
                "terminal_exclusions": 1,
            },
        )

    def test_sources_and_event_bounded_identities_parse_and_install(self) -> None:
        self.assertEqual(
            (
                len(WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES),
                len(WAVE8_ARGENTINE_INDEPENDENCE_SOURCES),
            ),
            (12, 14),
        )
        for source in WAVE8_ARGENTINE_INDEPENDENCE_SOURCES:
            Source.from_dict(source)
        for entity in WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertNotIn("argentinian rebels", entity["name"].casefold())
            self.assertNotIn("argentine rebels", entity["name"].casefold())

        entities = {entity["id"]: entity for entity in self.entities}
        sources = {source["id"]: source for source in self.sources}
        install_wave8_argentine_independence_entities(entities)
        install_wave8_argentine_independence_sources(sources)
        self.assertTrue(
            {entity["id"] for entity in WAVE8_ARGENTINE_INDEPENDENCE_ENTITIES}
            <= set(entities)
        )
        self.assertTrue(
            {source["id"] for source in WAVE8_ARGENTINE_INDEPENDENCE_SOURCES}
            <= set(sources)
        )

    def test_all_seven_semantic_row_hashes_fail_closed(self) -> None:
        indexed = {
            row["candidate_id"]: row
            for row in self.rows
            if row.get("candidate_id") in EXPECTED_CANDIDATE_IDS
        }
        self.assertEqual(set(indexed), EXPECTED_CANDIDATE_IDS)
        for inventory in (
            WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS,
            WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS,
        ):
            for candidate_id, disposition in inventory.items():
                self.assertEqual(
                    canonical_hced_row_sha256(indexed[candidate_id]),
                    disposition["raw_row_sha256"],
                )
        self.assertEqual(
            validate_wave8_argentine_independence_queue_contracts(self.rows),
            {"promotion_contracts": 6, "holds": 1, "reviewed_hced_rows": 7},
        )

        changed_promotion = copy.deepcopy(self.rows)
        next(
            row
            for row in changed_promotion
            if row["candidate_id"] == "hced-Pequereque1813-1"
        )["war_names"] = ["Chilean campaign"]
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_argentine_independence_queue_contracts(changed_promotion)

        changed_exclusion = copy.deepcopy(self.rows)
        next(
            row
            for row in changed_exclusion
            if row["candidate_id"] == "hced-Cancha Rayada1813-1"
        )["winner_raw"] = "Royalists"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_argentine_independence_queue_contracts(changed_exclusion)

    def test_exact_dates_commands_sides_outcomes_and_direct_sources_are_pinned(self) -> None:
        source_by_id = {
            source["id"]: source
            for source in WAVE8_ARGENTINE_INDEPENDENCE_SOURCES
        }
        self.assertEqual(set(WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS), set(EXPECTED_PROMOTIONS))
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            with self.subTest(candidate_id=candidate_id):
                contract = WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS[candidate_id]
                review = contract["historical_review"]
                self.assertEqual(contract["canonical_event"]["name"], expected["name"])
                self.assertEqual(contract["exact_date"], expected["exact_date"])
                self.assertEqual(review["outcome"], expected["outcome"])
                self.assertEqual(
                    review["revolutionary_commander"],
                    expected["revolutionary_commander"],
                )
                self.assertEqual(
                    review["royalist_commander"], expected["royalist_commander"]
                )
                self.assertFalse(contract["source_outcome_override"])
                self.assertTrue(contract["actor_override"])
                self.assertTrue(contract["outcome_source_ids"])
                self.assertTrue(
                    set(contract["outcome_source_ids"])
                    <= set(contract["evidence_refs"])
                )
                for source_id in contract["outcome_source_ids"]:
                    self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])
                self.assertTrue(contract["reservations"])

    def test_cancha_rayada_is_a_terminal_chilean_exclusion(self) -> None:
        self.assertEqual(
            WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSION_IDS,
            {"hced-Cancha Rayada1813-1"},
        )
        exclusion = WAVE8_ARGENTINE_INDEPENDENCE_TERMINAL_EXCLUSIONS[
            "hced-Cancha Rayada1813-1"
        ]
        self.assertEqual(exclusion["disposition"], "terminal_exclusion")
        self.assertEqual(
            exclusion["hold_category"], "misdated_reversed_chilean_event"
        )
        self.assertEqual(exclusion["raw_queue_assertion"]["year"], 1813)
        self.assertEqual(exclusion["canonical_event"]["year_low"], 1814)
        self.assertEqual(exclusion["reviewed_event"]["exact_date"], "1814-03-29")
        self.assertEqual(exclusion["reviewed_event"]["outcome"], "royalist_victory")
        self.assertEqual(
            exclusion["reviewed_event"]["revolutionary_commander"],
            "Manuel Blanco Encalada",
        )
        self.assertEqual(
            exclusion["reviewed_event"]["royalist_commander"], "Ángel Calvo"
        )
        self.assertEqual(
            exclusion["war_label_review"]["classification"],
            "confirmed_chilean_theatre_outside_argentine_lane",
        )
        self.assertNotIn(
            "hced-Cancha Rayada1813-1",
            WAVE8_ARGENTINE_INDEPENDENCE_CONTRACT_IDS,
        )

    def test_reservations_keep_all_rows_out_of_generic_crosswalks(self) -> None:
        owned_rows = [
            row
            for row in self.rows
            if row.get("candidate_id") in WAVE8_ARGENTINE_INDEPENDENCE_RESERVED_IDS
        ]
        result = promote_hced_crosswalk_rows(
            owned_rows,
            owners={},
            curated_seed_keys=set(),
            ensure_candidate_entity=lambda _entity: None,
            reserved_candidate_ids=WAVE8_ARGENTINE_INDEPENDENCE_RESERVED_IDS,
        )
        self.assertEqual(len(owned_rows), 7)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["deferred_label_rows"], [])
        self.assertEqual(result["label_observations"], {})
        self.assertEqual(result["rejections"]["reserved_candidate_contract"], 7)

    def test_six_promotions_emit_exact_sides_and_corrected_theatre(self) -> None:
        entities = {entity["id"]: entity for entity in self.entities}
        install_wave8_argentine_independence_entities(entities)
        emitted = promote_wave8_argentine_independence_contracts(
            self.rows,
            entities,
            existing_events=[],
        )
        self.assertEqual(
            {event["hced_candidate_id"] for event in emitted},
            WAVE8_ARGENTINE_INDEPENDENCE_CONTRACT_IDS,
        )
        by_id = {event["hced_candidate_id"]: event for event in emitted}
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            with self.subTest(candidate_id=candidate_id):
                event = by_id[candidate_id]
                Event.from_dict(event)
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
                self.assertEqual(event["name"], expected["name"])
                self.assertEqual(event["reviewed_exact_date"], expected["exact_date"])
                self.assertEqual(winners, expected["winners"])
                self.assertEqual(losers, expected["losers"])
                self.assertEqual(
                    event["cluster_id"],
                    "hced_war_argentine_war_of_independence",
                )
                self.assertEqual(
                    event["historical_theatre_review"]["reviewed_cluster_id"],
                    event["cluster_id"],
                )
                self.assertEqual(
                    event["outcome_source_ids"],
                    WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS[candidate_id][
                        "outcome_source_ids"
                    ],
                )
                self.assertTrue(event["reservations"])

        pequereque = by_id["hced-Pequereque1813-1"]
        self.assertEqual(
            pequereque["historical_theatre_review"]["expected_raw_cluster_id"],
            "hced_war_chilean_war_of_independence",
        )
        self.assertEqual(
            pequereque["historical_theatre_review"]["classification"],
            "corrected_mislabeled_chilean_theatre",
        )
        self.assertEqual(by_id["hced-Arroyo de la China1814-1"]["domain"], "naval")
        self.assertNotIn("hced-Cancha Rayada1813-1", by_id)

    def test_wave8_exact_rejects_an_unsourced_outcome_override(self) -> None:
        entities = {entity["id"]: entity for entity in self.entities}
        install_wave8_argentine_independence_entities(entities)
        candidate_id = "hced-Cotagaita1810-1"
        contract = copy.deepcopy(WAVE8_ARGENTINE_INDEPENDENCE_CONTRACTS[candidate_id])
        contract["source_outcome_override"] = True
        contract["outcome_source_ids"] = []
        with self.assertRaisesRegex(ValueError, "outcome override lacks direct sources"):
            promote_exact_hced_contracts(
                self.rows,
                entities,
                existing_events=[],
                contracts={candidate_id: contract},
                lane_name="Wave 8 Argentine-independence test",
                event_id_prefix="test_wave8_argentine_independence_",
            )


if __name__ == "__main__":
    unittest.main()
