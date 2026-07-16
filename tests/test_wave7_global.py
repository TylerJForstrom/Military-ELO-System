import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.wave7_global import (
    WAVE7_GLOBAL_HCED_CONTRACT_IDS,
    WAVE7_GLOBAL_HCED_HOLD_IDS,
    WAVE7_GLOBAL_MIGRATION_CANDIDATE_IDS,
    WAVE7_GLOBAL_RESERVED_IDS,
    canonical_event_sha256,
    canonical_hced_row_sha256,
    install_wave7_global_entities,
    install_wave7_global_sources,
    migrate_wave7_global_orange_events,
    promote_wave7_global_hced_contracts,
    validate_wave7_global_queue_contracts,
    validate_wave7_global_supersession_candidates,
    wave7_global_cohort_counts,
)
from military_elo.promotion.wave7_global_data import (
    WAVE7_GLOBAL_ENTITIES,
    WAVE7_GLOBAL_FINAL_AUDIT_SIGNATURE,
    WAVE7_GLOBAL_HCED_CONTRACTS,
    WAVE7_GLOBAL_HCED_HOLDS,
    WAVE7_GLOBAL_ORANGE_MIGRATIONS,
    WAVE7_GLOBAL_SOURCES,
    WAVE7_GLOBAL_SUPERSESSIONS,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _embedded_hced_rows():
    return [
        *[contract["raw_row"] for contract in WAVE7_GLOBAL_HCED_CONTRACTS.values()],
        *[contract["raw_row"] for contract in WAVE7_GLOBAL_HCED_HOLDS.values()],
        *[contract["raw_row"] for contract in WAVE7_GLOBAL_ORANGE_MIGRATIONS.values()],
    ]


def _embedded_cliopatria_rows():
    return [
        contract["raw_candidate"]
        for contract in WAVE7_GLOBAL_SUPERSESSIONS.values()
    ]


class Wave7GlobalInventoryTests(unittest.TestCase):
    def test_exact_inventory_counts_and_audit_signature(self) -> None:
        self.assertEqual(
            wave7_global_cohort_counts(),
            {
                "egypt_ayyubid": 1,
                "egypt_fatimid": 2,
                "egypt_kingdom_1922": 3,
                "egypt_mamluk_forces_1798": 1,
                "egypt_mamluk_sultanate": 1,
                "egypt_ptolemaic": 1,
                "egypt_saite": 1,
                "orange_free_state": 11,
                "rio_de_la_plata_patriot_army": 15,
                "solomonic_ethiopia_pre1855": 1,
            },
        )
        self.assertEqual(len(WAVE7_GLOBAL_HCED_CONTRACT_IDS), 37)
        self.assertEqual(len(WAVE7_GLOBAL_HCED_HOLD_IDS), 5)
        self.assertEqual(len(WAVE7_GLOBAL_MIGRATION_CANDIDATE_IDS), 5)
        self.assertEqual(len(WAVE7_GLOBAL_RESERVED_IDS), 47)
        self.assertFalse(WAVE7_GLOBAL_HCED_CONTRACT_IDS & WAVE7_GLOBAL_HCED_HOLD_IDS)
        self.assertFalse(
            WAVE7_GLOBAL_HCED_CONTRACT_IDS
            & WAVE7_GLOBAL_MIGRATION_CANDIDATE_IDS
        )
        self.assertEqual(
            WAVE7_GLOBAL_FINAL_AUDIT_SIGNATURE,
            "7da16e99b2d1b8f99aa760c5d58e5a39007114dc34e79dec140cd8d51af0ae3f",
        )

        lines = []
        for candidate_id, contract in WAVE7_GLOBAL_HCED_CONTRACTS.items():
            lines.append(
                f"promote|{candidate_id}|{contract['raw_row_sha256']}|"
                f"{contract['canonical_event']['canonical_key']}"
            )
        for candidate_id, contract in WAVE7_GLOBAL_HCED_HOLDS.items():
            lines.append(
                f"hold|{candidate_id}|{contract['raw_row_sha256']}|"
                f"{contract['canonical_event']['canonical_key']}"
            )
        for event_id, migration in WAVE7_GLOBAL_ORANGE_MIGRATIONS.items():
            lines.append(
                f"migrate|{migration['candidate_id']}|"
                f"{migration['raw_row_sha256']}|{event_id}|"
                f"{migration['source_event_sha256']}"
            )
        signature = hashlib.sha256(
            ("\n".join(sorted(lines)) + "\n").encode("utf-8")
        ).hexdigest()
        self.assertEqual(signature, WAVE7_GLOBAL_FINAL_AUDIT_SIGNATURE)

    def test_every_reviewed_row_has_an_exact_semantic_sha256(self) -> None:
        for inventory in (
            WAVE7_GLOBAL_HCED_CONTRACTS,
            WAVE7_GLOBAL_HCED_HOLDS,
            WAVE7_GLOBAL_ORANGE_MIGRATIONS,
        ):
            for key, contract in inventory.items():
                with self.subTest(key=key):
                    self.assertEqual(
                        canonical_hced_row_sha256(contract["raw_row"]),
                        contract["raw_row_sha256"],
                    )
                    self.assertEqual(len(contract["raw_row_sha256"]), 64)

        self.assertEqual(
            validate_wave7_global_queue_contracts(_embedded_hced_rows()),
            {
                "new_event_contracts": 37,
                "holds": 5,
                "identity_migrations": 5,
                "reviewed_hced_rows": 47,
            },
        )

    def test_candidate_drift_missing_rows_and_duplicate_rows_fail_closed(self) -> None:
        original = _embedded_hced_rows()
        changed = copy.deepcopy(original)
        target = next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Antukyah1531-1"
        )
        target["winner_raw"] = "Ethiopia"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave7_global_queue_contracts(changed)

        missing = [
            row
            for row in original
            if row["candidate_id"] != "hced-Biddulphsberg1900-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave7_global_queue_contracts(missing)

        duplicate = [
            *original,
            WAVE7_GLOBAL_HCED_CONTRACTS["hced-Biddulphsberg1900-1"][
                "raw_row"
            ],
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave7_global_queue_contracts(duplicate)

    def test_holds_are_exact_and_kadesh_can_never_be_double_rated(self) -> None:
        expected = {
            "hced-Barrancas1819-1": "civil_war_faction_identity_unresolved",
            "hced-La Herradura1819-1": "civil_war_faction_identity_unresolved",
            "hced-San Ignacio1867-1": "civil_war_faction_identity_unresolved",
            "hced-Boomplaats1848-1": "pre_polity_identity_anachronism",
            "hced-Kadesh-1275-1": "duplicate_and_outcome_conflict",
        }
        self.assertEqual(
            {
                candidate_id: contract["hold_category"]
                for candidate_id, contract in WAVE7_GLOBAL_HCED_HOLDS.items()
            },
            expected,
        )
        kadesh = WAVE7_GLOBAL_HCED_HOLDS["hced-Kadesh-1275-1"]
        self.assertEqual(kadesh["duplicate_event_id"], "battle_kadesh_1274_bce")
        self.assertEqual(kadesh["canonical_event"]["year_low"], -1274)
        self.assertNotIn("hced-Kadesh-1275-1", WAVE7_GLOBAL_HCED_CONTRACTS)

        release_kadesh = next(
            event
            for event in _json(ROOT / "data" / "release" / "events.json")
            if event["id"] == "battle_kadesh_1274_bce"
        )
        self.assertEqual(release_kadesh["name"], "Battle of Kadesh")
        self.assertEqual(
            {participant["termination"] for participant in release_kadesh["participants"]},
            {"inconclusive"},
        )

    def test_all_47_rows_are_reserved_from_generic_fallbacks(self) -> None:
        for candidate_id in (
            "hced-Cerrito1812-1",
            "hced-Boomplaats1848-1",
            "hced-Graspan1899-1",
            "hced-Kadesh-1275-1",
        ):
            contract = (
                WAVE7_GLOBAL_HCED_CONTRACTS.get(candidate_id)
                or WAVE7_GLOBAL_HCED_HOLDS.get(candidate_id)
                or next(
                    migration
                    for migration in WAVE7_GLOBAL_ORANGE_MIGRATIONS.values()
                    if migration["candidate_id"] == candidate_id
                )
            )
            result = promote_hced_crosswalk_rows(
                [contract["raw_row"]],
                owners={},
                curated_seed_keys=set(),
                ensure_candidate_entity=lambda polity: None,
                reserved_candidate_ids=WAVE7_GLOBAL_RESERVED_IDS,
            )
            self.assertEqual(result["events"], [])
            self.assertEqual(result["deferred_label_rows"], [])
            self.assertEqual(result["rejections"]["reserved_candidate_contract"], 1)


class Wave7GlobalPromotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.release_entities = {
            entity["id"]: entity
            for entity in _json(ROOT / "data" / "release" / "entities.json")
        }
        cls.original_ethiopian_seed = copy.deepcopy(
            cls.release_entities["ethiopian_empire"]
        )
        install_wave7_global_entities(cls.release_entities)
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.promoted = promote_wave7_global_hced_contracts(
            _embedded_hced_rows(),
            cls.release_entities,
            cls.release_events,
        )
        cls.by_candidate = {
            event["hced_candidate_id"]: event for event in cls.promoted
        }

    def test_exact_37_new_events_parse_and_retain_hced_as_outcome_source(self) -> None:
        self.assertEqual(len(self.promoted), 37)
        self.assertEqual(set(self.by_candidate), WAVE7_GLOBAL_HCED_CONTRACT_IDS)
        self.assertEqual(len({event["id"] for event in self.promoted}), 37)
        self.assertEqual(
            len({event["canonical_event_key"] for event in self.promoted}),
            37,
        )
        self.assertFalse(WAVE7_GLOBAL_HCED_HOLD_IDS & set(self.by_candidate))
        self.assertFalse(
            WAVE7_GLOBAL_MIGRATION_CANDIDATE_IDS & set(self.by_candidate)
        )
        for event in self.promoted:
            Event.from_dict(event)
            self.assertEqual(event["outcome_source_ids"], ["hced_dataset"])
            self.assertEqual(event["outcome_source_family_ids"], ["hced"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertIn("not an independently re-coded outcome", event["summary"])

    def test_exact_participant_bindings_never_use_a_cross_era_egypt_alias(self) -> None:
        expected = {
            "hced-Alexandria-48-1": {
                "roman_republic",
                "ptolemaic_egypt_305_bce",
            },
            "hced-Alexandria1167-1": {
                "clio_il_jerusalem_k_1_1099_306afd1d",
                "clio_tn_fatimid_cal_911_d329b0b3",
            },
            "hced-Ascalon1123-1": {
                "republic_venice",
                "clio_tn_fatimid_cal_911_d329b0b3",
            },
            "hced-Damietta1218-1": {
                "clio_eg_ayyubid_sultanate_1177_95f5a3a5",
                "kingdom_france",
            },
            "hced-Fariskur1250-1": {"mamluk_sultanate", "kingdom_france"},
            "hced-Pelusium-525-1": {"achaemenid_empire", "saite_egypt_664_bce"},
            "hced-Pyramids1798-1": {
                "french_first_republic",
                "mamluk_egyptian_forces_1798",
            },
            "hced-Asluj1948-1": {
                "clio_q801_1948_5abea45e",
                "kingdom_egypt_1922",
            },
            "hced-Beersheba1948-1": {
                "clio_q801_1948_5abea45e",
                "kingdom_egypt_1922",
            },
            "hced-Faluja1948-1": {
                "clio_q801_1948_5abea45e",
                "kingdom_egypt_1922",
            },
        }
        for candidate_id, participant_ids in expected.items():
            actual = {
                participant["entity_id"]
                for participant in self.by_candidate[candidate_id]["participants"]
            }
            self.assertEqual(actual, participant_ids)
            self.assertNotIn("egypt", actual)

        antukyah = self.by_candidate["hced-Antukyah1531-1"]
        self.assertEqual(
            {participant["entity_id"] for participant in antukyah["participants"]},
            {
                "adal_campaign_forces_1531",
                "solomonic_ethiopian_empire_pre1855",
            },
        )

    def test_new_entity_windows_are_narrow_alias_free_and_non_inheriting(self) -> None:
        expected_windows = {
            "rio_de_la_plata_patriot_army_1810": (1810, 1816),
            "orange_free_state_1854": (1854, 1902),
            "saite_egypt_664_bce": (-664, -525),
            "ptolemaic_egypt_305_bce": (-305, -30),
            "mamluk_egyptian_forces_1798": (1798, 1798),
            "kingdom_egypt_1922": (1922, 1952),
            "solomonic_ethiopian_empire_pre1855": (1270, 1854),
            "adal_campaign_forces_1531": (1531, 1543),
        }
        self.assertEqual(len(WAVE7_GLOBAL_ENTITIES), 8)
        for entity in WAVE7_GLOBAL_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                expected_windows[entity["id"]],
            )
            self.assertEqual(entity["aliases"], [])
            self.assertEqual(entity["predecessors"], [])
            self.assertIn("no rating", entity["continuity_note"].casefold())

        self.assertEqual(
            self.release_entities["ethiopian_empire"],
            self.original_ethiopian_seed,
        )
        self.assertEqual(
            self.release_entities["solomonic_ethiopian_empire_pre1855"]["end_year"],
            1854,
        )
        self.assertEqual(self.release_entities["ethiopian_empire"]["start_year"], 1855)
        egypt_entities = [
            entity
            for entity in WAVE7_GLOBAL_ENTITIES
            if entity["region"] == "North Africa"
        ]
        self.assertTrue(egypt_entities)
        self.assertTrue(all("Egypt" not in entity["aliases"] for entity in egypt_entities))

    def test_every_contract_is_covered_by_each_exact_entity_window(self) -> None:
        for candidate_id, contract in WAVE7_GLOBAL_HCED_CONTRACTS.items():
            low = int(contract["canonical_event"]["year_low"])
            high = int(contract["canonical_event"]["year_high"])
            for entity_id in (
                *contract["side_1_entity_ids"],
                *contract["side_2_entity_ids"],
            ):
                entity = self.release_entities[entity_id]
                with self.subTest(candidate_id=candidate_id, entity_id=entity_id):
                    self.assertLessEqual(entity["start_year"], low)
                    if entity["end_year"] is not None:
                        self.assertGreaterEqual(entity["end_year"], high)

        self.assertLess(
            WAVE7_GLOBAL_HCED_HOLDS["hced-Boomplaats1848-1"]["raw_row"][
                "year_low"
            ],
            self.release_entities["orange_free_state_1854"]["start_year"],
        )

    def test_sources_are_parseable_identity_references_not_outcome_evidence(self) -> None:
        source_map: dict[str, dict] = {}
        install_wave7_global_sources(source_map)
        self.assertEqual(len(source_map), 13)
        for source in source_map.values():
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                ["identity_boundary_or_context_reference"],
            )
        for event in self.promoted:
            self.assertEqual(event["outcome_source_ids"], ["hced_dataset"])
            self.assertGreaterEqual(len(event["source_ids"]), 2)

    def test_duplicate_event_and_candidate_collisions_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "source-family duplicate"):
            promote_wave7_global_hced_contracts(
                _embedded_hced_rows(),
                self.release_entities,
                [{"id": "collision", "name": "Cerrito", "year": 1812}],
            )
        with self.assertRaisesRegex(ValueError, "already promoted"):
            promote_wave7_global_hced_contracts(
                _embedded_hced_rows(),
                self.release_entities,
                [
                    {
                        "id": "collision",
                        "name": "unrelated",
                        "year": 0,
                        "hced_candidate_id": "hced-Cerrito1812-1",
                    }
                ],
            )


class Wave7GlobalOrangeMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.migration_ids = set(WAVE7_GLOBAL_ORANGE_MIGRATIONS)

    def test_migration_is_atomic_pure_and_changes_exactly_five_events(self) -> None:
        original = copy.deepcopy(self.release_events)
        migrated = migrate_wave7_global_orange_events(
            _embedded_hced_rows(),
            original,
        )
        self.assertEqual(original, self.release_events)
        self.assertIsNot(migrated, original)
        self.assertEqual(len(migrated), len(original))
        self.assertEqual(
            [event["id"] for event in migrated],
            [event["id"] for event in original],
        )
        changed_ids = {
            before["id"]
            for before, after in zip(original, migrated)
            if before != after
        }
        self.assertEqual(changed_ids, self.migration_ids)

        before_by_id = {event["id"]: event for event in original}
        after_by_id = {event["id"]: event for event in migrated}
        for event_id in self.migration_ids:
            before = before_by_id[event_id]
            after = after_by_id[event_id]
            Event.from_dict(after)
            self.assertEqual(
                canonical_event_sha256(before),
                WAVE7_GLOBAL_ORANGE_MIGRATIONS[event_id][
                    "source_event_sha256"
                ],
            )
            self.assertEqual(before["hced_candidate_id"], after["hced_candidate_id"])
            self.assertEqual(before["outcome_source_ids"], after["outcome_source_ids"])
            self.assertEqual(before["outcome_source_family_ids"], after["outcome_source_family_ids"])
            self.assertEqual(before["confidence"], after["confidence"])
            self.assertEqual(before["decisiveness"], after["decisiveness"])

            old_participants = copy.deepcopy(before["participants"])
            new_participants = copy.deepcopy(after["participants"])
            self.assertEqual(
                sum(
                    participant["entity_id"] == "clio_q218023_1856_cfb4e08e"
                    for participant in old_participants
                ),
                1,
            )
            self.assertEqual(
                sum(
                    participant["entity_id"] == "orange_free_state_1854"
                    for participant in new_participants
                ),
                1,
            )
            for participant in old_participants:
                if participant["entity_id"] == "clio_q218023_1856_cfb4e08e":
                    participant["entity_id"] = "orange_free_state_1854"
            self.assertEqual(old_participants, new_participants)
            self.assertEqual(
                after["identity_migration"]["source_event_sha256"],
                WAVE7_GLOBAL_ORANGE_MIGRATIONS[event_id][
                    "source_event_sha256"
                ],
            )
            self.assertIn("tactical outcome fields are unchanged", after["summary"])

    def test_any_source_event_drift_or_missing_member_aborts_the_whole_migration(self) -> None:
        changed = copy.deepcopy(self.release_events)
        target = next(
            event
            for event in changed
            if event["id"] == "hced_label_hced_graspan1899_1"
        )
        target["confidence"] = 0.71
        snapshot = copy.deepcopy(changed)
        with self.assertRaisesRegex(ValueError, "event fingerprint changed"):
            migrate_wave7_global_orange_events(_embedded_hced_rows(), changed)
        self.assertEqual(changed, snapshot)

        missing = [
            event
            for event in self.release_events
            if event["id"] != "hced_label_hced_graspan1899_1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one event"):
            migrate_wave7_global_orange_events(_embedded_hced_rows(), missing)

    def test_candidate_drift_aborts_before_event_replacement(self) -> None:
        rows = copy.deepcopy(_embedded_hced_rows())
        target = next(
            row
            for row in rows
            if row["candidate_id"] == "hced-Graspan1899-1"
        )
        target["side_2_raw"] = "South African Republic"
        events = copy.deepcopy(self.release_events)
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            migrate_wave7_global_orange_events(rows, events)
        self.assertEqual(events, self.release_events)


class Wave7GlobalSupersessionTests(unittest.TestCase):
    def test_exact_raw_identity_supersessions_and_1855_reset(self) -> None:
        self.assertEqual(
            validate_wave7_global_supersession_candidates(
                _embedded_cliopatria_rows()
            ),
            {
                "cliopatria-613": (
                    "solomonic_ethiopian_empire_pre1855",
                    "ethiopian_empire",
                ),
                "cliopatria-661": ("orange_free_state_1854",),
            },
        )
        self.assertEqual(
            WAVE7_GLOBAL_SUPERSESSIONS["cliopatria-613"][
                "raw_candidate_sha256"
            ],
            "42de39e1a7ba3a9252fcfd8cdd0af1f98ff59b5395dbf580122d506043e4c396",
        )
        self.assertEqual(
            WAVE7_GLOBAL_SUPERSESSIONS["cliopatria-661"][
                "raw_candidate_sha256"
            ],
            "ed680e4fd0a82628b5f6fd17df2b3325c4ebccbb5da1e44f9b12e038d8dc97b5",
        )
        self.assertIn(
            "1855 reset",
            WAVE7_GLOBAL_SUPERSESSIONS["cliopatria-613"]["boundary_note"],
        )

    def test_supersession_drift_missing_rows_and_duplicates_fail_closed(self) -> None:
        changed = copy.deepcopy(_embedded_cliopatria_rows())
        changed[0]["end_year"] = 1936
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            validate_wave7_global_supersession_candidates(changed)

        missing = _embedded_cliopatria_rows()[:1]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave7_global_supersession_candidates(missing)

        duplicated = [
            *_embedded_cliopatria_rows(),
            copy.deepcopy(_embedded_cliopatria_rows()[0]),
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave7_global_supersession_candidates(duplicated)


if __name__ == "__main__":
    unittest.main()
