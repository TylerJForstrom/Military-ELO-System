import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave6_pre1500 import (
    WAVE6_PRE1500_CURATED_EXCLUSIONS,
)
from military_elo.promotion.wave7_west import (
    WAVE7_WEST_HCED_CONTRACT_IDS,
    WAVE7_WEST_HCED_RESERVED_IDS,
    WAVE7_WEST_PROTECTED_RATED_IDS,
    _entity_covers,
    canonical_row_sha256,
    install_wave7_west_entities,
    install_wave7_west_sources,
    promote_wave7_west_hced_contracts,
    validate_wave7_west_protected_events,
    validate_wave7_west_queue_contracts,
    wave7_west_cohort_counts,
)
from military_elo.promotion.wave7_west_data import (
    WAVE7_WEST_AUDIT_SIGNATURE,
    WAVE7_WEST_BAVARIA_NEW_IDS,
    WAVE7_WEST_DUTCH_PROTECTED_IDS,
    WAVE7_WEST_ENTITIES,
    WAVE7_WEST_EXPECTED_HASHES,
    WAVE7_WEST_HCED_CONTRACTS,
    WAVE7_WEST_HCED_HOLDS,
    WAVE7_WEST_HOLD_IDS,
    WAVE7_WEST_NETHERLANDS_NEW_IDS,
    WAVE7_WEST_PROTECTED_RATED,
    WAVE7_WEST_ROSES_NEW_IDS,
    WAVE7_WEST_ROSES_PROTECTED_IDS,
    WAVE7_WEST_SOURCES,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _embedded_rows():
    reviewed = {
        **WAVE7_WEST_HCED_CONTRACTS,
        **WAVE7_WEST_HCED_HOLDS,
        **WAVE7_WEST_PROTECTED_RATED,
    }
    return [contract["raw_row"] for contract in reviewed.values()]


class Wave7WestInventoryTests(unittest.TestCase):
    def test_exact_reviewed_partition_and_audit_signature(self) -> None:
        self.assertEqual(len(WAVE7_WEST_EXPECTED_HASHES), 57)
        self.assertEqual(len(WAVE7_WEST_HCED_CONTRACT_IDS), 29)
        self.assertEqual(len(WAVE7_WEST_HOLD_IDS), 13)
        self.assertEqual(len(WAVE7_WEST_PROTECTED_RATED_IDS), 15)
        self.assertEqual(len(WAVE7_WEST_ROSES_NEW_IDS), 5)
        self.assertEqual(len(WAVE7_WEST_ROSES_PROTECTED_IDS), 13)
        self.assertEqual(len(WAVE7_WEST_BAVARIA_NEW_IDS), 14)
        self.assertEqual(len(WAVE7_WEST_NETHERLANDS_NEW_IDS), 10)
        self.assertEqual(len(WAVE7_WEST_DUTCH_PROTECTED_IDS), 2)
        self.assertEqual(
            WAVE7_WEST_HCED_RESERVED_IDS,
            frozenset(WAVE7_WEST_EXPECTED_HASHES),
        )
        self.assertFalse(WAVE7_WEST_HCED_CONTRACT_IDS & WAVE7_WEST_HOLD_IDS)
        self.assertFalse(WAVE7_WEST_HCED_CONTRACT_IDS & WAVE7_WEST_PROTECTED_RATED_IDS)
        self.assertFalse(WAVE7_WEST_HOLD_IDS & WAVE7_WEST_PROTECTED_RATED_IDS)
        self.assertEqual(
            wave7_west_cohort_counts(),
            {
                "bavaria_sequence": 14,
                "netherlands_sequence": 10,
                "wars_of_the_roses": 5,
            },
        )

        lines = []
        for candidate_id, contract in WAVE7_WEST_HCED_CONTRACTS.items():
            lines.append(f"{candidate_id}|{contract['raw_row_sha256']}|promote")
        for candidate_id, contract in WAVE7_WEST_HCED_HOLDS.items():
            lines.append(
                f"{candidate_id}|{contract['raw_row_sha256']}|"
                f"hold:{contract['hold_category']}"
            )
        for candidate_id, contract in WAVE7_WEST_PROTECTED_RATED.items():
            lines.append(
                f"{candidate_id}|{contract['raw_row_sha256']}|"
                f"protect:{contract['expected_event_id']}"
            )
        signature = hashlib.sha256(
            ("\n".join(sorted(lines)) + "\n").encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            WAVE7_WEST_AUDIT_SIGNATURE,
            "0b183a29f69997bef7b6ac87c5e6e19791eba55713daee55fbae64432faf91af",
        )
        self.assertEqual(signature, WAVE7_WEST_AUDIT_SIGNATURE)

    def test_all_57_complete_rows_are_fingerprinted_and_required(self) -> None:
        for candidate_id, expected in WAVE7_WEST_EXPECTED_HASHES.items():
            inventories = (
                WAVE7_WEST_HCED_CONTRACTS,
                WAVE7_WEST_HCED_HOLDS,
                WAVE7_WEST_PROTECTED_RATED,
            )
            contract = next(
                inventory[candidate_id]
                for inventory in inventories
                if candidate_id in inventory
            )
            self.assertEqual(canonical_row_sha256(contract["raw_row"]), expected)

        self.assertEqual(
            validate_wave7_west_queue_contracts(_embedded_rows()),
            {
                "reviewed": 57,
                "net_new_promotions": 29,
                "holds": 13,
                "protected_existing": 15,
                "roses_rated_total": 18,
                "roses_net_new": 5,
                "roses_preserved_holds": 2,
                "bavaria_net_new": 14,
                "netherlands_net_new": 10,
            },
        )

    def test_queue_drift_missing_and_duplicate_rows_fail_closed(self) -> None:
        rows = _embedded_rows()
        changed = [dict(row) for row in rows]
        target = next(
            row for row in changed if row["candidate_id"] == "hced-Blueberg1806-1"
        )
        target["winner_raw"] = "Netherlands"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave7_west_queue_contracts(changed)

        missing = [
            row for row in rows if row["candidate_id"] != "hced-Boroughbridge1322-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave7_west_queue_contracts(missing)

        duplicated = [*rows, WAVE7_WEST_HCED_HOLDS["hced-Marga1946-1"]["raw_row"]]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave7_west_queue_contracts(duplicated)

    def test_holds_are_explicit_and_boundary_specific(self) -> None:
        expected = {
            "hced-Boroughbridge1322-1": "anachronistic_faction_label",
            "hced-Alnwick1462-1": "coalition_incomplete_mandatory",
            "hced-Edgecote1469-1": "party_identity_ambiguous",
            "hced-Dunstable1461-1": "component_inflation_existing_wave6_hold",
            "hced-Ferrybridge1461-1": "multi_phase_component_existing_wave6_hold",
            "hced-Gammelsdorf1313-1": "divided_duchy_boundary",
            "hced-Muhldorf1322-1": "divided_duchy_boundary",
            "hced-Bazeilles1870-1": "year_only_france_transition",
            "hced-Chatillon-sous-Bagneux1870-1": "year_only_france_transition",
            "hced-Coulmiers1870-1": "year_only_france_transition",
            "hced-Villepion1870-1": "year_only_france_transition",
            "hced-Marga1946-1": "counterparty_identity_unresolved",
            "hced-Jogjakarta1948-1": "counterparty_identity_unresolved",
        }
        self.assertEqual(
            {
                candidate_id: hold["hold_category"]
                for candidate_id, hold in WAVE7_WEST_HCED_HOLDS.items()
            },
            expected,
        )
        for hold in WAVE7_WEST_HCED_HOLDS.values():
            self.assertTrue(hold["hold_reason"])
            self.assertTrue(hold["evidence_refs"])

    def test_direct_sources_and_new_identities_are_alias_free(self) -> None:
        self.assertEqual(len(WAVE7_WEST_SOURCES), 17)
        self.assertEqual(len(WAVE7_WEST_ENTITIES), 14)
        sources = {}
        install_wave7_west_sources(sources)
        for source in sources.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertIn(
                "identity_boundary_or_context_reference",
                source["evidence_roles"],
            )
        for entity in WAVE7_WEST_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("no rating", entity["continuity_note"].casefold())
            self.assertLessEqual(set(entity["source_ids"]), set(sources))


class Wave7WestPromotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.release_events = [
            event
            for event in _json(ROOT / "data" / "release" / "events.json")
            if event.get("hced_candidate_id") not in WAVE7_WEST_HCED_CONTRACT_IDS
        ]
        cls.entities = {
            entity["id"]: entity
            for entity in _json(ROOT / "data" / "release" / "entities.json")
        }
        install_wave7_west_entities(cls.entities)
        cls.events = promote_wave7_west_hced_contracts(
            _embedded_rows(),
            cls.entities,
            cls.release_events,
        )
        cls.by_candidate = {event["hced_candidate_id"]: event for event in cls.events}

    def test_exact_29_net_new_and_no_protected_duplicates(self) -> None:
        self.assertEqual(len(self.events), 29)
        self.assertEqual(set(self.by_candidate), WAVE7_WEST_HCED_CONTRACT_IDS)
        self.assertFalse(set(self.by_candidate) & WAVE7_WEST_PROTECTED_RATED_IDS)
        self.assertFalse(set(self.by_candidate) & WAVE7_WEST_HOLD_IDS)
        self.assertEqual(len({event["id"] for event in self.events}), 29)
        self.assertEqual(
            len({event["canonical_event_key"] for event in self.events}),
            29,
        )
        for event in self.events:
            Event.from_dict(event)

    def test_existing_13_roses_and_two_1811_dutch_rows_are_protected(self) -> None:
        self.assertEqual(
            validate_wave7_west_protected_events(self.release_events),
            {
                "protected_existing": 15,
                "protected_roses": 13,
                "protected_dutch_1811": 2,
            },
        )
        existing_candidates = {
            event.get("hced_candidate_id") for event in self.release_events
        }
        self.assertLessEqual(WAVE7_WEST_ROSES_PROTECTED_IDS, existing_candidates)
        self.assertLessEqual(WAVE7_WEST_DUTCH_PROTECTED_IDS, existing_candidates)

        for candidate_id in WAVE7_WEST_DUTCH_PROTECTED_IDS:
            contract = WAVE7_WEST_PROTECTED_RATED[candidate_id]
            entities = {item["entity_id"] for item in contract["expected_roster"]}
            self.assertIn("clio_nl_dutch_emp_2_1811_2e0bb80e", entities)
            self.assertNotIn("kingdom_netherlands_1815", entities)

        changed = copy.deepcopy(self.release_events)
        target = next(
            event
            for event in changed
            if event.get("hced_candidate_id") == "hced-Batavia1811-1"
        )
        target["participants"][1]["entity_id"] = "kingdom_netherlands_1815"
        with self.assertRaisesRegex(ValueError, "participant ownership changed"):
            validate_wave7_west_protected_events(changed)

        missing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") != "hced-Stoke1487-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one existing event"):
            validate_wave7_west_protected_events(missing)

    def test_inherited_wave6_holds_are_explicitly_preserved_or_resolved(self) -> None:
        resolved = {
            "hced-Twt Hill1463-1": "corrected_exact_date",
            "hced-Bamburgh1464-1": "corrected_outcome",
            "hced-Caister Castle1469-1": "corrected_participants",
            "hced-Lose-Coat Field1470-1": "corrected_participants",
            "hced-Bosworth Field1485-1": "candidate_specific_coalition",
        }
        preserved = {
            "hced-Dunstable1461-1",
            "hced-Ferrybridge1461-1",
        }
        self.assertLessEqual(
            set(resolved) | preserved,
            set(WAVE6_PRE1500_CURATED_EXCLUSIONS),
        )
        self.assertEqual(
            {
                candidate_id
                for candidate_id, hold in WAVE7_WEST_HCED_HOLDS.items()
                if hold.get("inherited_wave6_hold")
            },
            preserved,
        )
        for candidate_id, resolution in resolved.items():
            contract = WAVE7_WEST_HCED_CONTRACTS[candidate_id]
            self.assertEqual(contract["prior_wave6_hold_resolution"], resolution)
            self.assertNotEqual(contract["outcome_source_ids"], ["hced_dataset"])
            self.assertLessEqual(
                set(contract["outcome_source_ids"]),
                set(contract["evidence_refs"]),
            )

    def test_narrow_identity_windows_cover_only_the_reviewed_sequences(self) -> None:
        expected_windows = {
            "duchy_bavaria_unified_1506": (1506, 1622),
            "electorate_bavaria_1623": (1623, 1805),
            "kingdom_bavaria_1806": (1806, 1918),
            "batavian_republic_1795": (1795, 1806),
            "kingdom_netherlands_1815": (1815, None),
            "tudor_lancastrian_army_1485": (1485, 1485),
            "stanley_forces_1485": (1485, 1485),
            "yorkist_royal_army_1485": (1485, 1485),
            "duke_norfolk_forces_1469": (1469, 1469),
            "paston_retainers_1469": (1469, 1469),
            "edward_iv_royal_army_1470": (1470, 1470),
            "welles_rebel_army_1470": (1470, 1470),
        }
        for entity_id, window in expected_windows.items():
            entity = self.entities[entity_id]
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                window,
            )

        duchy = self.entities["duchy_bavaria_unified_1506"]
        electorate = self.entities["electorate_bavaria_1623"]
        kingdom = self.entities["kingdom_bavaria_1806"]
        self.assertFalse(_entity_covers(duchy, 1505, 1505))
        self.assertTrue(_entity_covers(duchy, 1506, 1622))
        self.assertFalse(_entity_covers(duchy, 1623, 1623))
        self.assertTrue(_entity_covers(electorate, 1623, 1805))
        self.assertFalse(_entity_covers(electorate, 1806, 1806))
        self.assertTrue(_entity_covers(kingdom, 1806, 1918))
        self.assertFalse(_entity_covers(kingdom, 1919, 1919))

        batavian = self.entities["batavian_republic_1795"]
        netherlands = self.entities["kingdom_netherlands_1815"]
        self.assertTrue(_entity_covers(batavian, 1795, 1806))
        self.assertFalse(_entity_covers(batavian, 1807, 1807))
        self.assertFalse(_entity_covers(netherlands, 1814, 1814))
        self.assertTrue(_entity_covers(netherlands, 1815, 1962))

    def test_bosworth_heidelberg_and_schellenberg_rosters_are_complete(self) -> None:
        expected = {
            "hced-Bosworth Field1485-1": {
                "tudor_lancastrian_army_1485",
                "stanley_forces_1485",
                "yorkist_royal_army_1485",
            },
            "hced-Heidelberg1622-1": {
                "duchy_bavaria_unified_1506",
                "dutch_republic",
                "kingdom_england",
                "palatine_protestant_forces_1622",
            },
            "hced-Donauworth1704-1": {
                "kingdom_england",
                "baden_imperial_forces_1704",
                "electorate_bavaria_1623",
            },
            "hced-Groote Keeten1799-1": {
                "united_kingdom",
                "russian_empire",
                "batavian_republic_1795",
            },
        }
        for candidate_id, expected_entities in expected.items():
            actual = {
                participant["entity_id"]
                for participant in self.by_candidate[candidate_id]["participants"]
            }
            self.assertEqual(actual, expected_entities)

    def test_corrected_roses_dates_outcome_and_candidate_forces_are_pinned(
        self,
    ) -> None:
        twt = self.by_candidate["hced-Twt Hill1463-1"]
        self.assertEqual(
            (twt["name"], twt["year"], twt["end_year"]),
            (
                "Battle of Twthill",
                1461,
                1461,
            ),
        )
        self.assertEqual(
            twt["date_interval"],
            {"start": "1461-10-16", "end": "1461-10-16"},
        )
        self.assertEqual(twt["outcome_source_ids"], ["wave7_west_rcahmw_twt"])

        bamburgh_contract = WAVE7_WEST_HCED_CONTRACTS["hced-Bamburgh1464-1"]
        self.assertEqual(
            bamburgh_contract["raw_row"]["winner_raw"],
            "Lancastrians",
        )
        bamburgh = self.by_candidate["hced-Bamburgh1464-1"]
        self.assertEqual(bamburgh["name"], "Siege of Bamburgh Castle")
        self.assertEqual(
            {
                participant["entity_id"]
                for participant in bamburgh["participants"]
                if participant["termination"] == "engagement_victory"
            },
            {"yorkist_faction_1455"},
        )
        self.assertEqual(
            bamburgh["outcome_source_ids"],
            ["wave7_west_he_bamburgh"],
        )

        caister = self.by_candidate["hced-Caister Castle1469-1"]
        self.assertEqual(caister["name"], "Siege of Caister Castle")
        self.assertEqual(
            {
                participant["entity_id"]: participant["termination"]
                for participant in caister["participants"]
            },
            {
                "duke_norfolk_forces_1469": "engagement_victory",
                "paston_retainers_1469": "engagement_defeat",
            },
        )

        losecoat = self.by_candidate["hced-Lose-Coat Field1470-1"]
        self.assertEqual(
            losecoat["date_interval"],
            {"start": "1470-03-12", "end": "1470-03-12"},
        )
        self.assertEqual(
            {
                participant["entity_id"]: participant["termination"]
                for participant in losecoat["participants"]
            },
            {
                "edward_iv_royal_army_1470": "engagement_victory",
                "welles_rebel_army_1470": "engagement_defeat",
            },
        )

        bosworth = self.by_candidate["hced-Bosworth Field1485-1"]
        self.assertEqual(
            bosworth["date_interval"],
            {"start": "1485-08-22", "end": "1485-08-22"},
        )
        self.assertEqual(
            {
                participant["entity_id"]
                for participant in bosworth["participants"]
                if participant["termination"] == "engagement_victory"
            },
            {"tudor_lancastrian_army_1485", "stanley_forces_1485"},
        )

    def test_blaauwberg_is_the_only_candidate_specific_1806_exception(self) -> None:
        batavian_candidates = {
            candidate_id
            for candidate_id, event in self.by_candidate.items()
            if any(
                participant["entity_id"] == "batavian_republic_1795"
                for participant in event["participants"]
            )
        }
        self.assertEqual(
            batavian_candidates,
            {
                "hced-Ambon1796-1",
                "hced-Colombo1796-1",
                "hced-Saldanha Bay1796-1",
                "hced-Camperdown1797-1",
                "hced-Groote Keeten1799-1",
                "hced-Surinam1800-1",
                "hced-Surinam1804-1",
                "hced-Blueberg1806-1",
            },
        )
        blueberg = self.by_candidate["hced-Blueberg1806-1"]
        self.assertEqual(blueberg["name"], "Battle of Blaauwberg")
        self.assertEqual(blueberg["date_precision"], "exact_day")
        self.assertEqual(
            blueberg["date_interval"],
            {"start": "1806-01-08", "end": "1806-01-08"},
        )
        self.assertIn("wave7_west_saho_blaauwberg", blueberg["source_ids"])
        self.assertEqual(
            sum(
                event["year"] == 1806
                and any(
                    participant["entity_id"] == "batavian_republic_1795"
                    for participant in event["participants"]
                )
                for event in self.events
            ),
            1,
        )

    def test_outcome_orientation_and_source_family_follow_exact_contract(self) -> None:
        for candidate_id, contract in WAVE7_WEST_HCED_CONTRACTS.items():
            event = self.by_candidate[candidate_id]
            winner_side = int(contract["result"]["winner_side"])
            expected_winner_entities = set(contract[f"side_{winner_side}_entity_ids"])
            actual_winner_entities = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["termination"] == "engagement_victory"
            }
            self.assertEqual(actual_winner_entities, expected_winner_entities)
            self.assertEqual(
                event["outcome_source_ids"],
                contract["outcome_source_ids"],
            )
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")

    def test_candidate_and_event_key_collisions_fail_closed(self) -> None:
        collision = copy.deepcopy(self.release_events[0])
        collision["hced_candidate_id"] = "hced-Twt Hill1463-1"
        with self.assertRaisesRegex(ValueError, "candidate already promoted"):
            promote_wave7_west_hced_contracts(
                _embedded_rows(),
                self.entities,
                [*self.release_events, collision],
            )

        key_collision = {
            "id": "key_collision",
            "name": "Bamburgh",
            "year": 1464,
        }
        with self.assertRaisesRegex(ValueError, "source-family duplicate"):
            promote_wave7_west_hced_contracts(
                _embedded_rows(),
                self.entities,
                [*self.release_events, key_collision],
            )


if __name__ == "__main__":
    unittest.main()
