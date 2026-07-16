import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_algiers_cheyenne import (
    WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS,
    WAVE8_ALGIERS_CHEYENNE_CONTRACTS,
    WAVE8_ALGIERS_CHEYENNE_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_ALGIERS_CHEYENNE_ENTITIES,
    WAVE8_ALGIERS_CHEYENNE_EXCLUSIONS,
    WAVE8_ALGIERS_CHEYENNE_EXCLUSION_IDS,
    WAVE8_ALGIERS_CHEYENNE_EXPECTED_CANDIDATE_IDS,
    WAVE8_ALGIERS_CHEYENNE_FINAL_AUDIT_SIGNATURE,
    WAVE8_ALGIERS_CHEYENNE_HOLD_IDS,
    WAVE8_ALGIERS_CHEYENNE_HOLDS,
    WAVE8_ALGIERS_CHEYENNE_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_ALGIERS_CHEYENNE_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_ALGIERS_CHEYENNE_NONPROMOTIONS,
    WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDE_METADATA,
    WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDES,
    WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS,
    WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS,
    WAVE8_ALGIERS_CHEYENNE_SOURCES,
    WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS,
    WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS,
    install_wave8_algiers_cheyenne_entities,
    install_wave8_algiers_cheyenne_sources,
    promote_wave8_algiers_cheyenne_contracts,
    validate_wave8_algiers_cheyenne_queue_contracts,
    wave8_algiers_cheyenne_audit_signature,
    wave8_algiers_cheyenne_cohort_counts,
    wave8_algiers_cheyenne_counts,
)
from military_elo.promotion.wave8_exact import promote_exact_hced_contracts


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows() -> list[dict]:
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _independent_signature() -> str:
    payload = {
        "contracts": WAVE8_ALGIERS_CHEYENNE_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_ALGIERS_CHEYENNE_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_ALGIERS_CHEYENNE_ENTITIES,
        "holds": WAVE8_ALGIERS_CHEYENNE_HOLDS,
        "iwbd_duplicate_dispositions": (
            WAVE8_ALGIERS_CHEYENNE_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "outcome_overrides": WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_ALGIERS_CHEYENNE_SOURCES,
        "terminal_exclusions": WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class Wave8AlgiersCheyenneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _rows()
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _entities(self) -> dict[str, dict]:
        lane_ids = {str(entity["id"]) for entity in WAVE8_ALGIERS_CHEYENNE_ENTITIES}
        entities = {
            entity["id"]: entity
            for entity in self.release_entities
            if entity["id"] not in lane_ids
        }
        install_wave8_algiers_cheyenne_entities(entities)
        return entities

    def _pre_lane_events(self) -> list[dict]:
        return [
            event
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS
        ]

    def _events(self) -> list[dict]:
        return promote_wave8_algiers_cheyenne_contracts(
            self.rows,
            self._entities(),
            self._pre_lane_events(),
        )

    def test_inventory_counts_dispositions_and_signature_are_exact(self) -> None:
        self.assertEqual(
            (
                len(WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS),
                len(WAVE8_ALGIERS_CHEYENNE_HOLD_IDS),
                len(WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS),
            ),
            (8, 3, 3),
        )
        self.assertFalse(
            WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS
            & WAVE8_ALGIERS_CHEYENNE_HOLD_IDS
        )
        self.assertFalse(
            WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS
            & WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS
        )
        self.assertFalse(
            WAVE8_ALGIERS_CHEYENNE_HOLD_IDS
            & WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS
        )
        self.assertEqual(
            WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS,
            WAVE8_ALGIERS_CHEYENNE_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(len(WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS), 14)
        self.assertIs(
            WAVE8_ALGIERS_CHEYENNE_EXCLUSIONS,
            WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS,
        )
        self.assertEqual(
            WAVE8_ALGIERS_CHEYENNE_EXCLUSION_IDS,
            WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS,
        )
        self.assertEqual(
            set(WAVE8_ALGIERS_CHEYENNE_NONPROMOTIONS),
            WAVE8_ALGIERS_CHEYENNE_HOLD_IDS
            | WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSION_IDS,
        )
        self.assertEqual(
            _independent_signature(),
            WAVE8_ALGIERS_CHEYENNE_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_algiers_cheyenne_audit_signature(),
            WAVE8_ALGIERS_CHEYENNE_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_algiers_cheyenne_cohort_counts(),
            {"algiers": 4, "cheyenne_indians": 4},
        )
        self.assertEqual(
            wave8_algiers_cheyenne_counts(),
            {
                "holds": 3,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 10,
                "new_sources": 25,
                "newly_rated_events": 8,
                "outcome_overrides": 0,
                "promotion_contracts": 8,
                "reviewed_hced_rows": 14,
                "terminal_exclusions": 3,
            },
        )

    def test_all_fourteen_row_hashes_and_queue_validation_fail_closed(self) -> None:
        indexed = {row["candidate_id"]: row for row in self.rows}
        expected_hashes = {
            "hced-Bougie1671-1": "5d0cfaaa5a2b0ec5248940c6646f7c8d01f755aa2f36c4358318621c340ce28e",
            "hced-Algiers1688-1": "1a297c79891c7464e6b6d6517460c4a28f147c0bcf442695a9d5ce41f2402b22",
            "hced-Algiers1775-1": "dd7ea93453a58cccaceebe47dbf37945d252ddce9fb0c9f45dbc06ec54d9f00f",
            "hced-Algiers1783-1": "5ed467957ba6db9d8305d7014d916391c7c530bf4dae7356b2126e85ed9cd017",
            "hced-Tripoli, Libya1803-1": "f36b1a46c7802e4367a77209619de823a7c9873e4fd72468d9e12f1d0d40050e",
            "hced-Cabo de Gata1815-1": "8c8dde8f45461125377a4ca4ef1b3f1e208b5fd71b619aebfd958c020e906332",
            "hced-Algiers1824-1": "a1fa47e450c07dbac57d041d7f2081b8d879a92d7da485ffe741ab3533351800",
            "hced-Solomon Forks1857-1": "e96107900b07d81263b30c38a7d6370e931d3dd05216d55e233456da84abdebc",
            "hced-Ash Creek1864-1": "2a706c4dce2542b5feefdb936f8dab26dcdcf18332cd9b283ce678d963805c5e",
            "hced-Powder1865-1": "550c63cb09262c4751beedc76402ad14a15f4c6b0a5f75f93ec87f21d37bf89c",
            "hced-Plum Creek, Nebraska1867-1": "16e99b4dbd67197e243303c01c937f9c78b7d8d1c1380c2263ab705b61ffc9fa",
            "hced-Sappa Creek1875-1": "0be149e65e633b40df14e940665d4660ae9aa671e7692616ec4d603bba0660af",
            "hced-Crazy Woman Creek1876-1": "3abe584ad98753a7e063b5b958802536ad083f70befd54bf036ca8eb838199d9",
            "hced-War Bonnet Creek1876-1": "e896a5108845e40c8e290cbc485e8c7c17f95129ed259649923ba0b6becb634b",
        }
        self.assertEqual(set(expected_hashes), WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS)
        inventory = {
            **WAVE8_ALGIERS_CHEYENNE_CONTRACTS,
            **WAVE8_ALGIERS_CHEYENNE_NONPROMOTIONS,
        }
        for candidate_id, expected_hash in expected_hashes.items():
            self.assertEqual(
                canonical_hced_row_sha256(indexed[candidate_id]),
                expected_hash,
            )
            self.assertEqual(inventory[candidate_id]["raw_row_sha256"], expected_hash)
        self.assertEqual(
            validate_wave8_algiers_cheyenne_queue_contracts(self.rows),
            {
                "promotion_contracts": 8,
                "holds": 3,
                "reviewed_hced_rows": 14,
                "terminal_exclusions": 3,
            },
        )

        changed = copy.deepcopy(self.rows)
        next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Tripoli, Libya1803-1"
        )["side_1_raw"] = "timeless Algiers"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_algiers_cheyenne_queue_contracts(changed)

        changed_terminal = copy.deepcopy(self.rows)
        next(
            row
            for row in changed_terminal
            if row["candidate_id"] == "hced-Sappa Creek1875-1"
        )["winner_raw"] = "Unknown"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_algiers_cheyenne_queue_contracts(changed_terminal)

    def test_sources_and_ten_alias_free_bounded_entities_parse(self) -> None:
        self.assertEqual(
            (len(WAVE8_ALGIERS_CHEYENNE_ENTITIES), len(WAVE8_ALGIERS_CHEYENNE_SOURCES)),
            (10, 25),
        )
        source_by_id = {}
        for source in WAVE8_ALGIERS_CHEYENNE_SOURCES:
            Source.from_dict(source)
            source_by_id[source["id"]] = source
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
        self.assertEqual(len(source_by_id), 25)

        expected_windows = {
            "dey_regency_of_algiers_1671_1830": (1671, 1830),
            "algerine_corsair_squadron_bugia_1671": (1671, 1671),
            "tuscan_naval_contingent_algiers_1775": (1775, 1775),
            "yusuf_karamanli_regency_of_tripoli_1795_1832": (1795, 1832),
            "mackenzie_scout_coalition_red_fork_1876": (1876, 1876),
            "red_fork_northern_cheyenne_camp_defenders_1876": (1876, 1876),
            "davis_murie_pawnee_scout_detachments_plum_creek_1867": (1867, 1867),
            "turkey_leg_northern_cheyenne_band_plum_creek_1867": (1867, 1867),
            "sumner_cheyenne_field_force_solomons_fork_1857": (1857, 1857),
            "red_cloud_agency_cheyenne_war_party_warbonnet_1876": (1876, 1876),
        }
        self.assertEqual(
            {entity["id"] for entity in WAVE8_ALGIERS_CHEYENNE_ENTITIES},
            set(expected_windows),
        )
        for entity in WAVE8_ALGIERS_CHEYENNE_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                expected_windows[entity["id"]],
            )
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("No rating is inherited", entity["continuity_note"])
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))
            self.assertNotIn(entity["name"].casefold(), {"algiers", "cheyenne indians"})

        installed_entities = {
            entity["id"]: entity
            for entity in self.release_entities
            if entity["id"] not in expected_windows
        }
        install_wave8_algiers_cheyenne_entities(installed_entities)
        install_wave8_algiers_cheyenne_entities(installed_entities)
        for fixture in WAVE8_ALGIERS_CHEYENNE_ENTITIES:
            self.assertEqual(installed_entities[fixture["id"]], fixture)

        installed_sources = {source["id"]: source for source in self.release_sources}
        for fixture in WAVE8_ALGIERS_CHEYENNE_SOURCES:
            installed_sources.pop(fixture["id"], None)
        install_wave8_algiers_cheyenne_sources(installed_sources)
        install_wave8_algiers_cheyenne_sources(installed_sources)
        for fixture in WAVE8_ALGIERS_CHEYENNE_SOURCES:
            self.assertEqual(installed_sources[fixture["id"]], fixture)

    def test_complete_reservations_block_generic_crosswalk_promotion(self) -> None:
        owned_rows = [
            row
            for row in self.rows
            if row.get("candidate_id") in WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS
        ]
        result = promote_hced_crosswalk_rows(
            owned_rows,
            owners={},
            curated_seed_keys=set(),
            ensure_candidate_entity=lambda _entity: None,
            reserved_candidate_ids=WAVE8_ALGIERS_CHEYENNE_RESERVED_IDS,
        )
        self.assertEqual(len(owned_rows), 14)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["deferred_label_rows"], [])
        self.assertEqual(result["label_observations"], {})
        self.assertEqual(result["rejections"]["reserved_candidate_contract"], 14)

    def test_three_holds_and_three_terminal_exclusions_stay_distinct(self) -> None:
        self.assertEqual(
            {
                candidate_id: hold["hold_category"]
                for candidate_id, hold in WAVE8_ALGIERS_CHEYENNE_HOLDS.items()
            },
            {
                "hced-Algiers1688-1": "tactical_outcome_not_directly_adjudicated",
                "hced-Algiers1783-1": "tactical_outcome_not_directly_adjudicated",
                "hced-Algiers1824-1": "event_boundary_and_outcome_unresolved",
            },
        )
        self.assertEqual(
            {
                candidate_id: exclusion["hold_category"]
                for candidate_id, exclusion in WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS.items()
            },
            {
                "hced-Ash Creek1864-1": "noncompetitive_attack_on_peace_village",
                "hced-Powder1865-1": "village_attack_without_competitive_outcome",
                "hced-Sappa Creek1875-1": "massacre_with_civilian_camp",
            },
        )
        for hold in WAVE8_ALGIERS_CHEYENNE_HOLDS.values():
            self.assertEqual(hold["disposition"], "hold")
            self.assertNotIn("terminal_exclusion", hold)
            self.assertEqual(hold["reviewed_granularity"], "engagement")
        for exclusion in WAVE8_ALGIERS_CHEYENNE_TERMINAL_EXCLUSIONS.values():
            self.assertEqual(exclusion["disposition"], "terminal_exclusion")
            self.assertIs(exclusion["terminal_exclusion"], True)
            self.assertEqual(exclusion["reviewed_granularity"], "non_ratable_attack")

    def test_contracts_pin_exact_sides_and_preserve_all_outcomes(self) -> None:
        expected_sides = {
            "hced-Bougie1671-1": (
                {"kingdom_england"},
                {"algerine_corsair_squadron_bugia_1671"},
            ),
            "hced-Algiers1775-1": (
                {"dey_regency_of_algiers_1671_1830"},
                {"spanish_empire", "tuscan_naval_contingent_algiers_1775"},
            ),
            "hced-Tripoli, Libya1803-1": (
                {"yusuf_karamanli_regency_of_tripoli_1795_1832"},
                {"united_states"},
            ),
            "hced-Cabo de Gata1815-1": (
                {"united_states"},
                {"dey_regency_of_algiers_1671_1830"},
            ),
            "hced-Crazy Woman Creek1876-1": (
                {"united_states", "mackenzie_scout_coalition_red_fork_1876"},
                {"red_fork_northern_cheyenne_camp_defenders_1876"},
            ),
            "hced-Plum Creek, Nebraska1867-1": (
                {
                    "united_states",
                    "davis_murie_pawnee_scout_detachments_plum_creek_1867",
                },
                {"turkey_leg_northern_cheyenne_band_plum_creek_1867"},
            ),
            "hced-Solomon Forks1857-1": (
                {"united_states"},
                {"sumner_cheyenne_field_force_solomons_fork_1857"},
            ),
            "hced-War Bonnet Creek1876-1": (
                {"united_states"},
                {"red_cloud_agency_cheyenne_war_party_warbonnet_1876"},
            ),
        }
        self.assertEqual(set(expected_sides), WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS)
        source_by_id = {
            source["id"]: source for source in WAVE8_ALGIERS_CHEYENNE_SOURCES
        }
        for candidate_id, (side_1, side_2) in expected_sides.items():
            contract = WAVE8_ALGIERS_CHEYENNE_CONTRACTS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), side_1)
            self.assertEqual(set(contract["side_2_entity_ids"]), side_2)
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(contract["result_type"], "win")
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertEqual(contract["canonical_event"]["granularity"], "engagement")
            self.assertTrue(contract["outcome_source_ids"])
            self.assertTrue(
                set(contract["outcome_source_ids"]) <= set(contract["evidence_refs"])
            )
            for source_id in contract["outcome_source_ids"]:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])

        all_side_ids = {
            entity_id
            for sides in expected_sides.values()
            for side in sides
            for entity_id in side
        }
        self.assertNotIn("Algiers", all_side_ids)
        self.assertNotIn("Cheyenne Indians", all_side_ids)
        self.assertEqual(WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDES, {})
        self.assertIs(
            WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDE_METADATA,
            WAVE8_ALGIERS_CHEYENNE_OUTCOME_OVERRIDES,
        )

    def test_eight_events_emit_with_direct_provenance_and_exact_coalitions(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 8)
        by_candidate = {event["hced_candidate_id"]: event for event in events}
        self.assertEqual(set(by_candidate), WAVE8_ALGIERS_CHEYENNE_CONTRACT_IDS)
        for candidate_id, event in by_candidate.items():
            Event.from_dict(event)
            contract = WAVE8_ALGIERS_CHEYENNE_CONTRACTS[candidate_id]
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
            self.assertTrue(event["id"].startswith("hced_wave8_algiers_cheyenne_"))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertEqual(event["canonical_event_key"], contract["canonical_event"]["canonical_key"])
            self.assertEqual(event["source_ids"], ["hced_dataset", *contract["evidence_refs"]])
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertNotIn("hced_dataset", event["outcome_source_ids"])

        self.assertEqual(
            by_candidate["hced-Tripoli, Libya1803-1"]["name"],
            "Capture of USS Philadelphia",
        )
        self.assertEqual(
            by_candidate["hced-Crazy Woman Creek1876-1"]["name"],
            "Dull Knife Fight at Red Fork",
        )
        self.assertEqual(
            {
                participant["entity_id"]
                for participant in by_candidate["hced-Algiers1775-1"]["participants"]
                if participant["side"] == "side_b"
            },
            {"spanish_empire", "tuscan_naval_contingent_algiers_1775"},
        )

    def test_location_quarantine_additions_are_explicit_and_applied(self) -> None:
        self.assertEqual(
            WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS,
            {
                "hced-Crazy Woman Creek1876-1",
                "hced-Plum Creek, Nebraska1867-1",
                "hced-Solomon Forks1857-1",
            },
        )
        self.assertEqual(WAVE8_ALGIERS_CHEYENNE_COUNTRY_QUARANTINE_ADDITIONS, set())
        self.assertEqual(
            WAVE8_ALGIERS_CHEYENNE_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS,
                "country": WAVE8_ALGIERS_CHEYENNE_COUNTRY_QUARANTINE_ADDITIONS,
            },
        )
        by_candidate = {event["hced_candidate_id"]: event for event in self._events()}
        for candidate_id in WAVE8_ALGIERS_CHEYENNE_POINT_QUARANTINE_ADDITIONS:
            self.assertNotIn("geometry", by_candidate[candidate_id])
            self.assertEqual(
                by_candidate[candidate_id]["modern_location_country"],
                "United States",
            )

    def test_iwbd_audit_found_no_duplicate_dispositions(self) -> None:
        self.assertEqual(WAVE8_ALGIERS_CHEYENNE_IWBD_DUPLICATE_DISPOSITIONS, {})
        iwbd_path = ROOT / "data" / "review" / "iwbd-candidates.jsonl"
        if not iwbd_path.exists():
            raise unittest.SkipTest("locked IWBD review queue is unavailable")
        target_terms = {
            "action at bugia bay",
            "spanish landing at algiers",
            "capture of uss philadelphia",
            "capture of mashouda off cape gata",
            "dull knife fight at red fork",
            "plum creek fight",
            "battle of solomon's fork",
            "skirmish at warbonnet creek",
        }
        pre_1900_names = {
            str(row["name"]).casefold()
            for row in map(json.loads, iwbd_path.read_text().splitlines())
            if int(str(row.get("start_date", "9999"))[:4]) < 1900
        }
        self.assertFalse(target_terms & pre_1900_names)

    def test_exact_helper_rejects_outcome_drift_and_duplicate_promotion(self) -> None:
        changed = copy.deepcopy(WAVE8_ALGIERS_CHEYENNE_CONTRACTS)
        changed["hced-Bougie1671-1"]["winner_side"] = 2
        with self.assertRaisesRegex(ValueError, "outcome drift"):
            promote_exact_hced_contracts(
                self.rows,
                self._entities(),
                self._pre_lane_events(),
                changed,
                lane_name="Wave 8 Algiers-Cheyenne outcome test",
                event_id_prefix="test_wave8_algiers_cheyenne_",
            )

        emitted = self._events()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_algiers_cheyenne_contracts(
                self.rows,
                self._entities(),
                [*self._pre_lane_events(), emitted[0]],
            )

        colliding_entities = self._entities()
        colliding_entities["dey_regency_of_algiers_1671_1830"] = {
            **colliding_entities["dey_regency_of_algiers_1671_1830"],
            "name": "Timeless Algiers",
        }
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_algiers_cheyenne_entities(colliding_entities)


if __name__ == "__main__":
    unittest.main()
