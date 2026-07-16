import hashlib
import inspect
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.policy import HCED_LABEL_POLICIES
from military_elo.promotion.wave6_1500_1799 import (
    WAVE6_HCED_CONTRACT_IDS,
    WAVE6_HCED_EXCLUSION_IDS,
    WAVE6_HCED_HOLD_IDS,
    WAVE6_HCED_RESERVED_IDS,
    WAVE6_WIKIDATA_EXCLUSION_IDS,
    canonical_row_sha256,
    _entity_covers,
    install_wave6_entities,
    promote_wave6_hced_contracts,
    validate_wave6_queue_contracts,
    wave6_cohort_counts,
)
from military_elo.promotion.wave6_1500_1799_data import (
    WAVE6_ENTITIES,
    WAVE6_HCED_CONTRACTS,
    WAVE6_HCED_EXCLUSIONS,
    WAVE6_HCED_HOLDS,
    WAVE6_FINAL_AUDIT_SIGNATURE,
    WAVE6_PHASE1_SIGNATURE,
    WAVE6_SOURCES,
    WAVE6_WIKIDATA_EXCLUSIONS,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _embedded_hced_rows():
    return [
        *[contract["raw_row"] for contract in WAVE6_HCED_CONTRACTS.values()],
        *[contract["raw_row"] for contract in WAVE6_HCED_HOLDS.values()],
        *[contract["raw_row"] for contract in WAVE6_HCED_EXCLUSIONS.values()],
    ]


def _embedded_wikidata_rows():
    return [contract["raw_row"] for contract in WAVE6_WIKIDATA_EXCLUSIONS.values()]


class Wave6EarlyModernInventoryTests(unittest.TestCase):
    def test_exact_inventory_and_phase1_signature(self) -> None:
        expected_cohorts = {
            "ahmadnagar_sultanate": 6,
            "bengal_states": 8,
            "bijapur_sultanate": 4,
            "brandenburg_prussia": 2,
            "electorate_saxony": 6,
            "gujarat_sultanate": 3,
            "hyderabad_asaf_jahi": 6,
            "jacobite_campaign_forces": 14,
            "kingdom_kandy": 2,
            "principality_transylvania": 6,
            "songhai_morocco": 1,
            "vendee_1793": 18,
        }
        self.assertEqual(wave6_cohort_counts(), expected_cohorts)
        self.assertEqual(len(WAVE6_HCED_CONTRACT_IDS), 76)
        self.assertEqual(len(WAVE6_HCED_HOLD_IDS), 4)
        self.assertEqual(len(WAVE6_HCED_EXCLUSION_IDS), 39)
        self.assertEqual(len(WAVE6_WIKIDATA_EXCLUSION_IDS), 8)
        self.assertFalse(WAVE6_HCED_CONTRACT_IDS & WAVE6_HCED_EXCLUSION_IDS)
        self.assertFalse(WAVE6_HCED_CONTRACT_IDS & WAVE6_HCED_HOLD_IDS)

        signature_lines = [
            f"{candidate_id}|{contract['raw_row_sha256']}|"
            f"{contract['canonical_event']['canonical_key']}"
            for candidate_id, contract in {
                **WAVE6_HCED_CONTRACTS,
                **WAVE6_HCED_HOLDS,
            }.items()
        ]
        signature = hashlib.sha256(
            ("\n".join(sorted(signature_lines)) + "\n").encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            WAVE6_PHASE1_SIGNATURE,
            "097343ce99ac260d7965dc71cede5199606eafbc774a7ebe9d9bd7539388a24c",
        )
        self.assertEqual(signature, WAVE6_FINAL_AUDIT_SIGNATURE)

    def test_every_embedded_row_and_queue_contract_is_fingerprinted(self) -> None:
        for inventory in (
            WAVE6_HCED_CONTRACTS,
            WAVE6_HCED_HOLDS,
            WAVE6_HCED_EXCLUSIONS,
            WAVE6_WIKIDATA_EXCLUSIONS,
        ):
            for candidate_id, contract in inventory.items():
                with self.subTest(candidate_id=candidate_id):
                    self.assertEqual(
                        canonical_row_sha256(contract["raw_row"]),
                        contract["raw_row_sha256"],
                    )
        self.assertEqual(
            validate_wave6_queue_contracts(
                _embedded_hced_rows(),
                _embedded_wikidata_rows(),
            ),
            {
                "promotion_contracts": 76,
                "hced_holds": 4,
                "hced_exclusions": 39,
                "hced_held_total": 43,
                "wikidata_exclusions": 8,
            },
        )

    def test_raw_hash_drift_and_missing_cohort_members_fail_closed(self) -> None:
        hced = _embedded_hced_rows()
        changed = [dict(row) for row in hced]
        target = next(
            row for row in changed if row["candidate_id"] == "hced-Tondibi1591-1"
        )
        target["winner_raw"] = "Songhai"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave6_queue_contracts(changed, _embedded_wikidata_rows())

        missing = [row for row in hced if row["candidate_id"] != "hced-Tondibi1591-1"]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave6_queue_contracts(missing, _embedded_wikidata_rows())

        duplicated = [*hced, WAVE6_HCED_CONTRACTS["hced-Tondibi1591-1"]["raw_row"]]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave6_queue_contracts(duplicated, _embedded_wikidata_rows())

    def test_exact_exclusions_include_all_material_holds_and_generic_hre(self) -> None:
        material = {
            "hced-Chemille1793-1",
            "hced-Tiffauges1793-1",
            "hced-Kesseldorf1745-1",
            "hced-Warsaw1657-1",
            "hced-Ambur1749-1",
            "hced-Koppal1677-1",
            "hced-Limerick1690-1",
        }
        self.assertLessEqual(material, WAVE6_HCED_EXCLUSION_IDS)
        hre = {
            candidate_id
            for candidate_id, exclusion in WAVE6_HCED_EXCLUSIONS.items()
            if exclusion["category"] == "unsafe_imperial_collapse"
        }
        self.assertEqual(len(hre), 11)
        for candidate_id in hre:
            row = WAVE6_HCED_EXCLUSIONS[candidate_id]["raw_row"]
            self.assertIn(
                "Holy Roman Empire",
                {
                    row.get("side_1_raw"),
                    row.get("side_2_raw"),
                    row.get("winner_raw"),
                    row.get("loser_raw"),
                },
            )
        self.assertEqual(
            {row["category"] for row in WAVE6_WIKIDATA_EXCLUSIONS.values()},
            {"war_umbrella_no_result"},
        )

        expected_holds = {
            "hced-Boyne1690-1": "coalition_incomplete_mandatory",
            "hced-Falkirk1746-1": "coalition_incomplete_mandatory",
            "hced-Stirling1745-1746-1": "coalition_incomplete_mandatory",
            "hced-Culloden1746-1": "coalition_incomplete_mandatory",
        }
        self.assertEqual(
            {
                candidate_id: contract["hold_category"]
                for candidate_id, contract in WAVE6_HCED_HOLDS.items()
            },
            expected_holds,
        )
        for candidate_id, contract in WAVE6_HCED_HOLDS.items():
            self.assertNotIn(candidate_id, WAVE6_HCED_CONTRACTS)
            self.assertTrue(contract["hold_reason"])
        self.assertIn(
            "nam_nine_years",
            WAVE6_HCED_HOLDS["hced-Boyne1690-1"]["evidence_refs"],
        )
        for candidate_id in {
            "hced-Falkirk1746-1",
            "hced-Stirling1745-1746-1",
            "hced-Culloden1746-1",
        }:
            self.assertIn(
                "nam_jacobites",
                WAVE6_HCED_HOLDS[candidate_id]["evidence_refs"],
            )
        self.assertEqual(
            WAVE6_HCED_HOLDS["hced-Stirling1745-1746-1"]["canonical_event"],
            {
                "canonical_key": "siege_of_stirling_castle:1746:1746",
                "date_precision": "year",
                "exact_date": None,
                "granularity": "siege",
                "name": "Siege of Stirling Castle",
                "year_high": 1746,
                "year_low": 1746,
            },
        )

    def test_reserved_rows_never_enter_generic_crosswalk_or_label_fallback(
        self,
    ) -> None:
        row = WAVE6_HCED_CONTRACTS["hced-Tondibi1591-1"]["raw_row"]
        result = promote_hced_crosswalk_rows(
            [row],
            owners={},
            curated_seed_keys=set(),
            ensure_candidate_entity=lambda polity: None,
            reserved_candidate_ids=WAVE6_HCED_RESERVED_IDS,
        )
        self.assertEqual(result["events"], [])
        self.assertEqual(result["deferred_label_rows"], [])
        self.assertEqual(result["rejections"]["reserved_candidate_contract"], 1)

        prohibited_labels = {
            "hyderabad",
            "saxony",
            "transylvania",
            "bengal",
            "holy roman empire",
            "morocco",
            "songhai",
            "jacobites",
            "williamites",
        }
        self.assertFalse(prohibited_labels & set(HCED_LABEL_POLICIES))
        policy_targets = {
            entity_id
            for windows in HCED_LABEL_POLICIES.values()
            for _, _, entity_id in windows
        }
        self.assertFalse(
            policy_targets & {str(entity["id"]) for entity in WAVE6_ENTITIES}
        )


class Wave6EarlyModernPromotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.entities = {
            row["id"]: row for row in _json(ROOT / "data" / "release" / "entities.json")
        }
        install_wave6_entities(cls.entities)
        cls.base_events = [
            event
            for event in _json(ROOT / "data" / "release" / "events.json")
            if event.get("hced_candidate_id") not in WAVE6_HCED_CONTRACT_IDS
        ]
        cls.events = promote_wave6_hced_contracts(
            _embedded_hced_rows(),
            cls.entities,
            cls.base_events,
        )
        cls.by_candidate = {row["hced_candidate_id"]: row for row in cls.events}

    def test_exact_76_event_promotion_and_duplicate_suppression(self) -> None:
        self.assertEqual(len(self.events), 76)
        self.assertEqual(set(self.by_candidate), WAVE6_HCED_CONTRACT_IDS)
        self.assertEqual(len({row["id"] for row in self.events}), 76)
        self.assertEqual(len({row["canonical_event_key"] for row in self.events}), 76)
        self.assertFalse(WAVE6_HCED_EXCLUSION_IDS & set(self.by_candidate))
        self.assertFalse(WAVE6_HCED_HOLD_IDS & set(self.by_candidate))
        for event in self.events:
            Event.from_dict(event)

        collision = {
            "id": "collision",
            "name": "Battle of Tondibi",
            "year": 1591,
        }
        with self.assertRaisesRegex(ValueError, "source-family duplicate"):
            promote_wave6_hced_contracts(
                _embedded_hced_rows(), self.entities, [collision]
            )

    def test_entity_windows_are_exact_non_inheriting_and_cover_every_event(
        self,
    ) -> None:
        expected_windows = {
            "electorate_saxony_1356": (1356, 1806),
            "principality_transylvania_1541": (1541, 1691),
            "hyderabad_asaf_jahi_state_1724": (1724, 1948),
            "bengal_sultanate_1352": (1352, 1576),
            "bengal_nawabate_1717": (1717, 1765),
            "brandenburg_prussia_1618": (1618, 1700),
            "saadi_morocco_1549": (1549, 1659),
        }
        for entity_id, window in expected_windows.items():
            entity = self.entities[entity_id]
            self.assertEqual((entity["start_year"], entity["end_year"]), window)
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("no rating", entity["continuity_note"].casefold())

        for candidate_id, contract in WAVE6_HCED_CONTRACTS.items():
            low = int(contract["canonical_event"]["year_low"])
            high = int(contract["canonical_event"]["year_high"])
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            ):
                entity = self.entities[entity_id]
                with self.subTest(candidate_id=candidate_id, entity_id=entity_id):
                    self.assertLessEqual(entity["start_year"], low)
                    if entity["end_year"] is not None:
                        self.assertGreaterEqual(entity["end_year"], high)

    def test_saxony_and_brandenburg_prussia_boundaries_fail_closed(self) -> None:
        saxony = self.entities["electorate_saxony_1356"]
        kingdom_saxony = {
            "start_year": 1807,
            "end_year": 1918,
        }
        self.assertTrue(_entity_covers(saxony, 1806, 1806))
        self.assertFalse(_entity_covers(saxony, 1806, 1807))
        self.assertFalse(_entity_covers(kingdom_saxony, 1806, 1806))
        self.assertTrue(_entity_covers(kingdom_saxony, 1807, 1807))

        brandenburg_prussia = self.entities["brandenburg_prussia_1618"]
        kingdom_prussia = self.entities["kingdom_prussia"]
        self.assertTrue(_entity_covers(brandenburg_prussia, 1700, 1700))
        self.assertFalse(_entity_covers(brandenburg_prussia, 1701, 1701))
        self.assertFalse(_entity_covers(brandenburg_prussia, 1700, 1701))
        self.assertTrue(_entity_covers(kingdom_prussia, 1701, 1701))
        self.assertFalse(_entity_covers(kingdom_prussia, 1700, 1701))

    def test_global_hced_integration_precedes_iwbd_and_uses_one_location_bijection(
        self,
    ) -> None:
        from military_elo.promotion.orchestrator import build_expanded_release

        source = inspect.getsource(build_expanded_release)
        self.assertLess(
            source.index("wave6_events = promote_wave6_hced_contracts"),
            source.index("iwbd_promotion = promote_iwbd_battles"),
        )
        hced_release_block = source[
            source.index("hced_events = [") : source.index(
                "hced_location_coverage = _validate_hced_location_release"
            )
        ]
        dedup_block = source[
            source.index("# Fuzzy ordinal/base-name matches") : source.index(
                "iwbd_promotion = promote_iwbd_battles"
            )
        ]
        for event_list in (
            "source_events",
            "label_events",
            "wave6_events",
            "wave7_root_events",
            "wave7_central_events",
            "wave7_central_pass2_events",
            "wave7_global_events",
            "wave7_west_events",
        ):
            self.assertIn(f"*{event_list}", hced_release_block)
            self.assertIn(f"*{event_list}", dedup_block)
        self.assertIn("WAVE6_HCED_CONTRACT_IDS", source)

    def test_bengal_company_and_jacobite_identities_never_collapse(self) -> None:
        bengal_ids = {
            candidate_id
            for candidate_id, contract in WAVE6_HCED_CONTRACTS.items()
            if contract["cohort"] == "bengal_states"
        }
        bengal_participants = {
            participant["entity_id"]
            for candidate_id in bengal_ids
            for participant in self.by_candidate[candidate_id]["participants"]
        }
        self.assertIn("east_india_company_forces_1757", bengal_participants)
        self.assertNotIn("united_kingdom", bengal_participants)

        rising_entities = {
            1689: {
                "scottish_jacobite_army_1689",
                "scottish_williamite_army_1689",
                "irish_jacobite_army_1689",
                "irish_williamite_army_1689",
            },
            1715: {"jacobite_army_1715", "british_government_army_1715"},
            1745: {"jacobite_army_1745", "british_government_army_1745"},
        }
        for _, entity_ids in rising_entities.items():
            self.assertEqual(len(entity_ids), len(set(entity_ids)))
        self.assertTrue(
            set.union(*rising_entities.values())
            <= {str(entity["id"]) for entity in WAVE6_ENTITIES}
        )

    def test_outcomes_coalitions_and_granularity_match_the_review(self) -> None:
        sheriffmuir = self.by_candidate["hced-Sheriffmuir1715-1"]
        self.assertTrue(
            all(
                participant["termination"] == "inconclusive_engagement"
                for participant in sheriffmuir["participants"]
            )
        )
        expected_rosters = {
            "hced-Bhatavadi1624-1": {
                "ahmadnagar_sultanate_1490",
                "mughal_empire",
                "clio_in_bijapur_sultanate_1492_49a19c59",
            },
            "hced-Aughrim1691-1": {
                "irish_jacobite_army_1689",
                "irish_williamite_army_1689",
                "kingdom_france",
            },
            "hced-Gannoruwa1638-1": {"kingdom_kandy_1590", "kingdom_portugal"},
            "hced-Koppal1790-1791-1": {
                "hyderabad_asaf_jahi_state_1724",
                "east_india_company_forces_1757",
                "kingdom_mysore",
            },
        }
        for candidate_id, expected in expected_rosters.items():
            actual = {
                participant["entity_id"]
                for participant in self.by_candidate[candidate_id]["participants"]
            }
            self.assertEqual(actual, expected)

        koppal_contract = WAVE6_HCED_CONTRACTS["hced-Koppal1790-1791-1"]
        self.assertIn("British", koppal_contract["raw_row"]["participants_raw"])
        self.assertIn("ignca_tipu_sultan", koppal_contract["evidence_refs"])
        hyderabad_ids = {
            entity_id
            for candidate_id, contract in WAVE6_HCED_CONTRACTS.items()
            if contract["cohort"] == "hyderabad_asaf_jahi"
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            )
            if "hyderabad" in entity_id
        }
        self.assertEqual(hyderabad_ids, {"hyderabad_asaf_jahi_state_1724"})

        pirna = self.by_candidate["hced-Pirna1756-1"]
        self.assertEqual(pirna["name"], "Investment and Capitulation of Pirna")
        self.assertEqual(pirna["reviewed_granularity"], "operational_encirclement")
        self.assertIn("bounded investment/capitulation", pirna["summary"])
        self.assertNotIn("field battle", pirna["name"].casefold())

    def test_direct_sources_and_non_inheriting_entity_contracts_parse(self) -> None:
        sources = {source["id"]: source for source in WAVE6_SOURCES}
        self.assertEqual(len(sources), 40)
        for source in sources.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                ["identity_boundary_or_context_reference"],
            )
        for entity in WAVE6_ENTITIES:
            Entity.from_dict(entity)
            self.assertLessEqual(set(entity["source_ids"]), set(sources))
        for event in self.events:
            self.assertIn("hced_dataset", event["outcome_source_ids"])
            self.assertEqual(event["outcome_source_family_ids"], ["hced"])
            self.assertGreaterEqual(len(event["source_ids"]), 2)


if __name__ == "__main__":
    unittest.main()
