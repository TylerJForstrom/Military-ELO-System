import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave8_somali_irish_sa import (
    WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS,
    WAVE8_SOMALI_IRISH_SA_CONTRACTS,
    WAVE8_SOMALI_IRISH_SA_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_SOMALI_IRISH_SA_ENTITIES,
    WAVE8_SOMALI_IRISH_SA_FINAL_AUDIT_SIGNATURE,
    WAVE8_SOMALI_IRISH_SA_HOLD_IDS,
    WAVE8_SOMALI_IRISH_SA_HOLDS,
    WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_SOMALI_IRISH_SA_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDE_METADATA,
    WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES,
    WAVE8_SOMALI_IRISH_SA_POINT_QUARANTINE_ADDITIONS,
    WAVE8_SOMALI_IRISH_SA_RESERVED_IDS,
    WAVE8_SOMALI_IRISH_SA_SOURCES,
    install_wave8_somali_irish_sa_entities,
    install_wave8_somali_irish_sa_sources,
    promote_wave8_somali_irish_sa_contracts,
    validate_wave8_somali_irish_sa_queue_contracts,
    wave8_somali_irish_sa_audit_signature,
    wave8_somali_irish_sa_cohort_counts,
    wave8_somali_irish_sa_counts,
)


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
        "contracts": WAVE8_SOMALI_IRISH_SA_CONTRACTS,
        "holds": WAVE8_SOMALI_IRISH_SA_HOLDS,
        "entities": WAVE8_SOMALI_IRISH_SA_ENTITIES,
        "sources": WAVE8_SOMALI_IRISH_SA_SOURCES,
        "point_quarantine_additions": sorted(
            WAVE8_SOMALI_IRISH_SA_POINT_QUARANTINE_ADDITIONS
        ),
        "country_quarantine_additions": sorted(
            WAVE8_SOMALI_IRISH_SA_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "iwbd_duplicate_dispositions": WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS,
        "outcome_overrides": WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


class Wave8SomaliIrishSouthAfricaTests(unittest.TestCase):
    def _entities_and_existing(self):
        lane_ids = {str(entity["id"]) for entity in WAVE8_SOMALI_IRISH_SA_ENTITIES}
        entities = {
            entity["id"]: entity
            for entity in _json(ROOT / "data" / "release" / "entities.json")
            if entity["id"] not in lane_ids
        }
        install_wave8_somali_irish_sa_entities(entities)
        existing = [
            event
            for event in _json(ROOT / "data" / "release" / "events.json")
            if event.get("hced_candidate_id")
            not in WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS
        ]
        return entities, existing

    def _events(self) -> list[dict]:
        entities, existing = self._entities_and_existing()
        return promote_wave8_somali_irish_sa_contracts(
            _rows(), entities, existing
        )

    def test_inventory_counts_disjointness_and_full_audit_signature(self) -> None:
        self.assertEqual(
            (len(WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS), len(WAVE8_SOMALI_IRISH_SA_HOLD_IDS)),
            (17, 1),
        )
        self.assertFalse(
            WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS
            & WAVE8_SOMALI_IRISH_SA_HOLD_IDS
        )
        self.assertEqual(
            WAVE8_SOMALI_IRISH_SA_RESERVED_IDS,
            WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS
            | WAVE8_SOMALI_IRISH_SA_HOLD_IDS,
        )
        self.assertEqual(
            _independent_signature(),
            WAVE8_SOMALI_IRISH_SA_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_somali_irish_sa_audit_signature(),
            WAVE8_SOMALI_IRISH_SA_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_somali_irish_sa_cohort_counts(),
            {
                "irish_civil_war": 6,
                "somali_dervish_wars": 7,
                "wwi_south_african_formations": 4,
            },
        )
        self.assertEqual(
            wave8_somali_irish_sa_counts(),
            {
                "holds": 1,
                "iwbd_duplicate_dispositions": 5,
                "new_entities": 7,
                "new_sources": 21,
                "newly_rated_events": 17,
                "outcome_overrides": 1,
                "promotion_contracts": 17,
                "reviewed_hced_rows": 18,
            },
        )

    def test_exact_candidate_inventory_and_canonical_keys(self) -> None:
        expected_keys = {
            "hced-Ferdiddin1901-1": "battle_of_ferdiddin:1901:1901",
            "hced-Galiabur1920-1": "capture_of_galbaribur_fort:1920:1920",
            "hced-Gumburu1903-1": "battle_of_gumburu:1903:1903",
            "hced-Illig1904-1": "capture_of_illig:1904:1904",
            "hced-OK Pass1919-1": "battle_of_o_k_pass:1919:1919",
            "hced-Samala1901-1": "battle_of_samala:1901:1901",
            "hced-Taleh1920-1": "capture_of_tale_forts:1920:1920",
            "hced-Clashmealcon Caves1923-1": "siege_of_clashmealcon_caves:1923:1923",
            "hced-Clonmel1922-1": "clonmel_rearguard_action:1922:1922",
            "hced-Cork1922-1": "battle_of_cork_rochestown_douglas:1922:1922",
            "hced-Four Courts1922-1": "battle_of_the_four_courts:1922:1922",
            "hced-Kilmallock1922-1": "battle_of_kilmallock:1922:1922",
            "hced-O'Connell Street1922-1": "o_connell_street_block_fighting:1922:1922",
            "hced-Delville Wood1916-1": "south_african_defence_of_delville_wood:1916:1916",
            "hced-Gibeon1915-1": "battle_of_gibeon:1915:1915",
            "hced-Salaita1916-1": "battle_of_salaita_hill:1916:1916",
            "hced-Sandfontein1914-1": "battle_of_sandfontein:1914:1914",
            "hced-Windhoek1915-1": "unopposed_occupation_of_windhoek:1915:1915",
        }
        inventory = {
            **WAVE8_SOMALI_IRISH_SA_CONTRACTS,
            **WAVE8_SOMALI_IRISH_SA_HOLDS,
        }
        self.assertEqual(set(inventory), set(expected_keys))
        self.assertEqual(
            {
                candidate_id: item["canonical_event"]["canonical_key"]
                for candidate_id, item in inventory.items()
            },
            expected_keys,
        )
        for contract in WAVE8_SOMALI_IRISH_SA_CONTRACTS.values():
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["canonical_event"]["date_precision"], "year")
            self.assertEqual(contract["canonical_event"]["granularity"], "engagement")

    def test_entities_are_time_bounded_and_never_back_map_modern_states(self) -> None:
        expected_windows = {
            "somali_dervish_movement_1899_1920": (1899, 1920),
            "irish_national_army_1922_1923": (1922, 1923),
            "anti_treaty_ira_1922_1923": (1922, 1923),
            "union_defence_force_gswa_1914_1915": (1914, 1915),
            "first_south_african_infantry_brigade_delville_1916": (1916, 1916),
            "second_south_african_infantry_brigade_salaita_1916": (1916, 1916),
            "first_east_african_infantry_brigade_salaita_1916": (1916, 1916),
        }
        self.assertEqual(len(WAVE8_SOMALI_IRISH_SA_ENTITIES), 7)
        self.assertEqual(
            {entity["id"] for entity in WAVE8_SOMALI_IRISH_SA_ENTITIES},
            set(expected_windows),
        )
        for entity in WAVE8_SOMALI_IRISH_SA_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(
                (entity["start_year"], entity["end_year"]),
                expected_windows[entity["id"]],
            )
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("No rating is inherited", entity["continuity_note"])

        forbidden = {
            "clio_q1045_1960_b5c3f32e",
            "clio_sa_south_africa_rep_1932_8a5c7c70",
            "clio_ei_ireland_rep_1922_855f2448",
        }
        participant_ids = {
            entity_id
            for contract in WAVE8_SOMALI_IRISH_SA_CONTRACTS.values()
            for field in ("side_1_entity_ids", "side_2_entity_ids")
            for entity_id in contract[field]
        }
        self.assertTrue(forbidden.isdisjoint(participant_ids))

    def test_source_records_are_direct_and_parseable(self) -> None:
        expected_source_ids = {
            "uk_wo_somaliland_official_history_1907",
            "uk_hansard_gumburu_1903",
            "uk_hansard_illig_1904",
            "uk_gazette_somaliland_1920",
            "jardine_mad_mullah_somaliland_1923",
            "raf_casps_somaliland_1920",
            "ie_military_archives_four_courts_1922",
            "ie_bmh_clonmel_ws1763",
            "ucc_atlas_civil_war_unit8",
            "rte_ucc_battle_dublin_1922",
            "rte_ucc_kilmallock_1922",
            "rte_ucc_cork_1922",
            "rte_ucc_clashmealcon_1923",
            "nam_delville_wood_1916",
            "samh_sandfontein_1914",
            "samh_gibeon_1915",
            "nam_south_west_africa_campaign",
            "samh_salaita_1916",
            "historia_gswa_airpower_2017",
            "kenya_gazette_salaita_heritage_2015",
            "namibia_meft_sandfontein_heritage_2024",
        }
        self.assertEqual(len(WAVE8_SOMALI_IRISH_SA_SOURCES), 21)
        self.assertEqual(
            {source["id"] for source in WAVE8_SOMALI_IRISH_SA_SOURCES},
            expected_source_ids,
        )
        for source in WAVE8_SOMALI_IRISH_SA_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["license"], "linked_reference")
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertIn(
                "identity_boundary_or_context_reference",
                source["evidence_roles"],
            )

    def test_installers_are_exact_and_collision_safe(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        install_wave8_somali_irish_sa_entities(entities)
        install_wave8_somali_irish_sa_sources(sources)
        self.assertEqual(
            set(entities),
            {entity["id"] for entity in WAVE8_SOMALI_IRISH_SA_ENTITIES},
        )
        self.assertEqual(
            set(sources),
            {source["id"] for source in WAVE8_SOMALI_IRISH_SA_SOURCES},
        )
        bad_entities = {next(iter(entities)): {"id": next(iter(entities))}}
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_somali_irish_sa_entities(bad_entities)
        bad_sources = {next(iter(sources)): {"id": next(iter(sources))}}
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_somali_irish_sa_sources(bad_sources)

    def test_queue_hashes_validate_and_drift_fails_closed(self) -> None:
        rows = _rows()
        self.assertEqual(
            validate_wave8_somali_irish_sa_queue_contracts(rows),
            {"promotion_contracts": 17, "holds": 1, "reviewed_hced_rows": 18},
        )
        changed = copy.deepcopy(rows)
        target = next(
            row
            for row in changed
            if row["candidate_id"] == "hced-Gibeon1915-1"
        )
        target["winner_raw"] = "South Africa"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_somali_irish_sa_queue_contracts(changed)

    def test_contract_sides_are_exact_and_holds_never_emit(self) -> None:
        expected = {
            "hced-Ferdiddin1901-1": (("united_kingdom",), ("somali_dervish_movement_1899_1920",), 1),
            "hced-Galiabur1920-1": (("united_kingdom",), ("somali_dervish_movement_1899_1920",), 1),
            "hced-Gumburu1903-1": (("somali_dervish_movement_1899_1920",), ("united_kingdom",), 1),
            "hced-Illig1904-1": (("united_kingdom",), ("somali_dervish_movement_1899_1920",), 1),
            "hced-OK Pass1919-1": (("united_kingdom",), ("somali_dervish_movement_1899_1920",), 1),
            "hced-Samala1901-1": (("united_kingdom",), ("somali_dervish_movement_1899_1920",), 1),
            "hced-Taleh1920-1": (("united_kingdom",), ("somali_dervish_movement_1899_1920",), 1),
            "hced-Delville Wood1916-1": (("first_south_african_infantry_brigade_delville_1916",), ("german_empire",), 1),
            "hced-Gibeon1915-1": (("german_empire",), ("union_defence_force_gswa_1914_1915",), 2),
            "hced-Salaita1916-1": (("german_empire",), ("second_south_african_infantry_brigade_salaita_1916", "first_east_african_infantry_brigade_salaita_1916"), 1),
            "hced-Sandfontein1914-1": (("german_empire",), ("union_defence_force_gswa_1914_1915",), 1),
        }
        for candidate_id in {
            "hced-Clashmealcon Caves1923-1",
            "hced-Clonmel1922-1",
            "hced-Cork1922-1",
            "hced-Four Courts1922-1",
            "hced-Kilmallock1922-1",
            "hced-O'Connell Street1922-1",
        }:
            expected[candidate_id] = (
                ("irish_national_army_1922_1923",),
                ("anti_treaty_ira_1922_1923",),
                1,
            )
        self.assertEqual(set(expected), WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS)
        for candidate_id, (side_1, side_2, winner_side) in expected.items():
            contract = WAVE8_SOMALI_IRISH_SA_CONTRACTS[candidate_id]
            self.assertEqual(tuple(contract["side_1_entity_ids"]), side_1)
            self.assertEqual(tuple(contract["side_2_entity_ids"]), side_2)
            self.assertEqual(contract["winner_side"], winner_side)

        events = self._events()
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_SOMALI_IRISH_SA_CONTRACT_IDS,
        )
        self.assertTrue(
            WAVE8_SOMALI_IRISH_SA_HOLD_IDS.isdisjoint(
                {event["hced_candidate_id"] for event in events}
            )
        )

    def test_windhoek_is_the_exact_permanent_hold(self) -> None:
        self.assertEqual(WAVE8_SOMALI_IRISH_SA_HOLD_IDS, {"hced-Windhoek1915-1"})
        hold = WAVE8_SOMALI_IRISH_SA_HOLDS["hced-Windhoek1915-1"]
        self.assertEqual(
            hold["raw_row_sha256"],
            "009404963bebeeecdbcb9f656c6da10664214a90881dd898893eb399a774d923",
        )
        self.assertEqual(
            hold["canonical_event"],
            {
                "canonical_key": "unopposed_occupation_of_windhoek:1915:1915",
                "date_precision": "year",
                "granularity": "engagement",
                "name": "Unopposed occupation of Windhoek",
                "year_low": 1915,
                "year_high": 1915,
            },
        )
        self.assertEqual(
            hold["hold_category"],
            "not_an_engagement_unopposed_occupation",
        )
        self.assertEqual(
            hold["evidence_refs"],
            ["historia_gswa_airpower_2017", "nam_south_west_africa_campaign"],
        )
        self.assertIn("without combat", hold["hold_reason"])

    def test_gibeon_is_the_only_source_backed_outcome_override(self) -> None:
        override_ids = {
            candidate_id
            for candidate_id, contract in WAVE8_SOMALI_IRISH_SA_CONTRACTS.items()
            if contract["source_outcome_override"]
        }
        self.assertEqual(override_ids, {"hced-Gibeon1915-1"})
        self.assertEqual(set(WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES), override_ids)
        self.assertIs(
            WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDE_METADATA,
            WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES,
        )
        metadata = WAVE8_SOMALI_IRISH_SA_OUTCOME_OVERRIDES["hced-Gibeon1915-1"]
        self.assertEqual(
            (metadata["raw_winner_label"], metadata["corrected_winner_side"]),
            ("Germany", 2),
        )
        self.assertEqual(
            metadata["corrected_winner_entity_ids"],
            ["union_defence_force_gswa_1914_1915"],
        )
        by_id = {event["hced_candidate_id"]: event for event in self._events()}
        gibeon = by_id["hced-Gibeon1915-1"]
        self.assertEqual(
            {
                participant["entity_id"]
                for participant in gibeon["participants"]
                if participant["side"] == "side_a"
            },
            {"union_defence_force_gswa_1914_1915"},
        )
        self.assertEqual(
            {
                participant["entity_id"]
                for participant in gibeon["participants"]
                if participant["side"] == "side_b"
            },
            {"german_empire"},
        )
        self.assertEqual(gibeon["outcome_source_ids"], metadata["outcome_source_ids"])
        self.assertEqual(
            gibeon["outcome_source_family_ids"],
            metadata["outcome_source_family_ids"],
        )

    def test_location_quarantine_additions_are_explicit_and_applied(self) -> None:
        self.assertEqual(
            WAVE8_SOMALI_IRISH_SA_POINT_QUARANTINE_ADDITIONS,
            {
                "hced-Gumburu1903-1",
                "hced-O'Connell Street1922-1",
                "hced-Salaita1916-1",
                "hced-Sandfontein1914-1",
            },
        )
        self.assertEqual(
            WAVE8_SOMALI_IRISH_SA_COUNTRY_QUARANTINE_ADDITIONS,
            {
                "hced-Gumburu1903-1",
                "hced-Illig1904-1",
                "hced-Sandfontein1914-1",
            },
        )
        self.assertEqual(
            WAVE8_SOMALI_IRISH_SA_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_SOMALI_IRISH_SA_POINT_QUARANTINE_ADDITIONS,
                "country": WAVE8_SOMALI_IRISH_SA_COUNTRY_QUARANTINE_ADDITIONS,
            },
        )
        by_id = {event["hced_candidate_id"]: event for event in self._events()}
        for candidate_id in WAVE8_SOMALI_IRISH_SA_POINT_QUARANTINE_ADDITIONS:
            self.assertNotIn("geometry", by_id[candidate_id])
        for candidate_id in WAVE8_SOMALI_IRISH_SA_COUNTRY_QUARANTINE_ADDITIONS:
            self.assertNotIn("modern_location_country", by_id[candidate_id])
        self.assertNotIn("location_provenance", by_id["hced-Gumburu1903-1"])
        self.assertNotIn("location_provenance", by_id["hced-Sandfontein1914-1"])
        self.assertIn("geometry", by_id["hced-Illig1904-1"])
        self.assertEqual(
            by_id["hced-O'Connell Street1922-1"]["modern_location_country"],
            "Ireland",
        )
        self.assertEqual(
            by_id["hced-Salaita1916-1"]["modern_location_country"],
            "Kenya",
        )

    def test_iwbd_duplicate_dispositions_are_complete_and_non_emitting(self) -> None:
        expected = {
            "iwbd-106-38-480": ("hced-Sandfontein1914-1", "deduplicate_to_hced"),
            "iwbd-106-38-533": ("hced-Gibeon1915-1", "hold_contradictory_duplicate"),
            "iwbd-106-38-547": ("hced-Windhoek1915-1", "exclude_not_an_engagement"),
            "iwbd-106-38-602": ("hced-Salaita1916-1", "deduplicate_to_hced"),
            "iwbd-106-38-636": ("hced-Delville Wood1916-1", "hold_campaign_envelope_containment"),
        }
        self.assertEqual(set(WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS), set(expected))
        for iwbd_id, (hced_id, disposition) in expected.items():
            record = WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS[iwbd_id]
            self.assertEqual(record["hced_candidate_id"], hced_id)
            self.assertEqual(record["disposition"], disposition)
            self.assertTrue(record["reason"])
            self.assertRegex(record["iwbd_date_start"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertRegex(record["iwbd_date_end"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(
            WAVE8_SOMALI_IRISH_SA_IWBD_DUPLICATE_DISPOSITIONS["iwbd-106-38-547"]["hced_candidate_id"],
            next(iter(WAVE8_SOMALI_IRISH_SA_HOLD_IDS)),
        )

    def test_emitted_events_have_exact_provenance_and_schema(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 17)
        for event in events:
            Event.from_dict(event)
            candidate_id = event["hced_candidate_id"]
            contract = WAVE8_SOMALI_IRISH_SA_CONTRACTS[candidate_id]
            self.assertTrue(event["id"].startswith("hced_wave8_somali_irish_sa_"))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["event_type"], "engagement")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertEqual(event["date_precision"], "year")
            self.assertEqual(
                event["canonical_event_key"],
                contract["canonical_event"]["canonical_key"],
            )
            self.assertEqual(
                event["source_ids"],
                ["hced_dataset", *contract["evidence_refs"]],
            )
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertIn("Candidate-keyed Wave 8 tactical assertion", event["summary"])


if __name__ == "__main__":
    unittest.main()
