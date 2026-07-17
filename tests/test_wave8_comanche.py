import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_comanche import (
    WAVE8_COMANCHE_CONTRACT_IDS,
    WAVE8_COMANCHE_CONTRACTS,
    WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_COMANCHE_ENTITIES,
    WAVE8_COMANCHE_FINAL_AUDIT_SIGNATURE,
    WAVE8_COMANCHE_HOLD_IDS,
    WAVE8_COMANCHE_HOLDS,
    WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITION_IDS,
    WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_COMANCHE_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_COMANCHE_OUTCOME_OVERRIDE_IDS,
    WAVE8_COMANCHE_OUTCOME_OVERRIDES,
    WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS,
    WAVE8_COMANCHE_RESERVED_IDS,
    WAVE8_COMANCHE_SOURCES,
    install_wave8_comanche_entities,
    install_wave8_comanche_sources,
    promote_wave8_comanche_contracts,
    validate_wave8_comanche_queue_contracts,
    wave8_comanche_audit_signature,
    wave8_comanche_cohort_counts,
    wave8_comanche_counts,
    wave8_comanche_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue is unavailable: {path.name}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _independent_signature() -> str:
    payload = {
        "contracts": WAVE8_COMANCHE_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_COMANCHE_ENTITIES,
        "holds": WAVE8_COMANCHE_HOLDS,
        "iwbd_duplicate_dispositions": WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITIONS,
        "outcome_overrides": WAVE8_COMANCHE_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_COMANCHE_SOURCES,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class Wave8ComancheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.all_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.lane_rows = [
            row
            for row in cls.all_rows
            if row.get("candidate_id") in WAVE8_COMANCHE_RESERVED_IDS
        ]
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _direct_inputs(self):
        lane_entity_ids = {entity["id"] for entity in WAVE8_COMANCHE_ENTITIES}
        entities = {
            entity["id"]: entity
            for entity in self.release_entities
            if entity["id"] not in lane_entity_ids
        }
        install_wave8_comanche_entities(entities)
        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_COMANCHE_RESERVED_IDS
        ]
        return entities, existing

    def _events(self):
        entities, existing = self._direct_inputs()
        return promote_wave8_comanche_contracts(
            self.lane_rows,
            entities,
            existing,
        )

    def test_inventory_signature_counts_and_cohorts_are_exact(self) -> None:
        self.assertEqual(
            WAVE8_COMANCHE_CONTRACT_IDS,
            {
                "hced-Crooked Creek1859-1",
                "hced-Plum Creek, Texas1840-1",
                "hced-Rush Springs1858-1",
                "hced-Walkers Creek1844-1",
            },
        )
        self.assertEqual(
            WAVE8_COMANCHE_HOLD_IDS,
            {"hced-Adobe Walls1864-1", "hced-Colorado1840-1"},
        )
        self.assertEqual(
            WAVE8_COMANCHE_RESERVED_IDS,
            WAVE8_COMANCHE_CONTRACT_IDS | WAVE8_COMANCHE_HOLD_IDS,
        )
        self.assertEqual(_independent_signature(), WAVE8_COMANCHE_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            wave8_comanche_audit_signature(),
            WAVE8_COMANCHE_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_comanche_counts(),
            {
                "country_quarantine_additions": 0,
                "holds": 2,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 9,
                "new_sources": 10,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 6,
            },
        )
        self.assertEqual(
            wave8_comanche_cohort_counts(),
            {
                "texas_comanche_conflict_1840_1844": 2,
                "wichita_expedition_1858_1859": 2,
            },
        )

    def test_sources_and_identities_are_bounded_and_install_cleanly(self) -> None:
        self.assertEqual((len(WAVE8_COMANCHE_ENTITIES), len(WAVE8_COMANCHE_SOURCES)), (9, 10))
        source_by_id = {source["id"]: source for source in WAVE8_COMANCHE_SOURCES}
        self.assertEqual(len(source_by_id), len(WAVE8_COMANCHE_SOURCES))
        for source in WAVE8_COMANCHE_SOURCES:
            Source.from_dict(source)

        forbidden_exact_names = {
            "comanche",
            "comanche indians",
            "comanche nation",
            "kiowa",
            "tonkawa",
        }
        for entity in WAVE8_COMANCHE_ENTITIES:
            Entity.from_dict(entity)
            self.assertIsNotNone(entity["start_year"])
            self.assertIsNotNone(entity["end_year"])
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertIn("modern", entity["continuity_note"].casefold())
            self.assertNotIn(entity["name"].casefold(), forbidden_exact_names)
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        installed_sources = {
            source["id"]: source
            for source in self.release_sources
            if source["id"] not in source_by_id
        }
        install_wave8_comanche_sources(installed_sources)
        install_wave8_comanche_sources(installed_sources)
        for source_id, source in source_by_id.items():
            self.assertEqual(installed_sources[source_id], source)

    def test_all_six_queue_hashes_are_pinned_and_each_drift_fails_closed(self) -> None:
        self.assertEqual(
            {row["candidate_id"] for row in self.lane_rows},
            WAVE8_COMANCHE_RESERVED_IDS,
        )
        self.assertEqual(
            validate_wave8_comanche_queue_contracts(self.lane_rows),
            {"promotion_contracts": 4, "holds": 2, "reviewed_hced_rows": 6},
        )
        indexed = {row["candidate_id"]: row for row in self.lane_rows}
        for inventory in (WAVE8_COMANCHE_CONTRACTS, WAVE8_COMANCHE_HOLDS):
            for candidate_id, item in inventory.items():
                self.assertEqual(
                    canonical_hced_row_sha256(indexed[candidate_id]),
                    item["raw_row_sha256"],
                )

        for candidate_id in sorted(WAVE8_COMANCHE_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                changed = copy.deepcopy(self.lane_rows)
                next(
                    row for row in changed if row["candidate_id"] == candidate_id
                )["name"] += " tampered"
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_comanche_queue_contracts(changed)

    def test_adobe_walls_is_held_with_complete_coalitions_and_no_invented_draw(self) -> None:
        hold = WAVE8_COMANCHE_HOLDS["hced-Adobe Walls1864-1"]
        self.assertEqual(hold["hold_category"], "contradictory_outcome_evidence")
        self.assertEqual(
            hold["canonical_event"]["name"],
            "First Battle of Adobe Walls",
        )
        self.assertEqual(
            hold["documented_coalition_components"],
            {
                "carson_column": [
                    "First Cavalry, New Mexico Volunteers",
                    "Jicarilla Apache scouts",
                    "Ute scouts",
                ],
                "southern_plains_force": [
                    "Comanche participants",
                    "Kiowa participants",
                    "Kiowa-Apache participants",
                ],
            },
        )
        self.assertEqual(
            set(hold["evidence_refs"]),
            {
                "wave8_comanche_nps_indian_scouts",
                "wave8_comanche_nps_santa_fe_trail_four_tribes",
                "wave8_comanche_tsha_first_adobe_walls",
            },
        )
        self.assertNotIn("result_type", hold)
        self.assertNotIn("winner_side", hold)
        self.assertIn("nor reversed or converted into a draw", hold["hold_reason"])

    def test_colorado_is_excluded_without_aliasing_plum_creek_or_moores_attack(self) -> None:
        hold = WAVE8_COMANCHE_HOLDS["hced-Colorado1840-1"]
        self.assertEqual(
            hold["hold_category"],
            "ambiguous_event_identity_and_noncompetitive_massacre",
        )
        self.assertEqual(
            hold["canonical_event"]["granularity"],
            "unresolved_source_assertion",
        )
        self.assertEqual(hold["canonical_event"]["name"], "Colorado")
        raw = next(
            row
            for row in self.lane_rows
            if row["candidate_id"] == "hced-Colorado1840-1"
        )
        self.assertEqual(raw["massacre_raw"], "Battle followed by massacre")
        self.assertIn("Plum Creek", raw["participants_raw"])
        self.assertNotIn("result_type", hold)
        self.assertIn("No canonical engagement", hold["hold_reason"])

    def test_promotions_pin_names_dates_exact_sides_and_direct_outcomes(self) -> None:
        expected = {
            "hced-Plum Creek, Texas1840-1": {
                "name": "Battle of Plum Creek",
                "date_text": "12 August 1840",
                "winners": {
                    "plum_creek_texian_force_1840",
                    "plum_creek_tonkawa_allies_1840",
                },
                "losers": {"plum_creek_comanche_kiowa_war_party_1840"},
                "outcomes": {"wave8_comanche_thc_plum_creek"},
            },
            "hced-Walkers Creek1844-1": {
                "name": "Battle of Walker's Creek",
                "date_text": "8 June 1844",
                "winners": {"walkers_creek_hays_ranger_detachment_1844"},
                "losers": {
                    "walkers_creek_comanche_waco_mexican_raiding_party_1844"
                },
                "outcomes": {"wave8_comanche_tsha_walkers_creek"},
            },
            "hced-Rush Springs1858-1": {
                "name": "Battle of the Wichita Village",
                "date_text": "1 October 1858",
                "winners": {
                    "wichita_expedition_indigenous_auxiliaries_1858_1859",
                    "wichita_expedition_us_army_force_1858_1859",
                },
                "losers": {"wichita_village_comanche_fighting_force_1858"},
                "outcomes": {"wave8_comanche_army_mcoe_raids"},
            },
            "hced-Crooked Creek1859-1": {
                "name": "Battle of Crooked Creek",
                "date_text": "13 May 1859",
                "winners": {
                    "wichita_expedition_indigenous_auxiliaries_1858_1859",
                    "wichita_expedition_us_army_force_1858_1859",
                },
                "losers": {"crooked_creek_comanche_fighting_force_1859"},
                "outcomes": {
                    "wave8_comanche_army_mcoe_raids",
                    "wave8_comanche_uok_without_quarter",
                },
            },
        }
        source_by_id = {source["id"]: source for source in WAVE8_COMANCHE_SOURCES}
        for candidate_id, pinned in expected.items():
            contract = WAVE8_COMANCHE_CONTRACTS[candidate_id]
            self.assertEqual(contract["canonical_event"]["name"], pinned["name"])
            self.assertEqual(
                contract["canonical_event"]["date_text"],
                pinned["date_text"],
            )
            self.assertEqual(contract["canonical_event"]["date_precision"], "day")
            self.assertEqual(contract["canonical_event"]["granularity"], "engagement")
            self.assertEqual(set(contract["side_1_entity_ids"]), pinned["winners"])
            self.assertEqual(set(contract["side_2_entity_ids"]), pinned["losers"])
            self.assertEqual(set(contract["outcome_source_ids"]), pinned["outcomes"])
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertFalse(contract["source_outcome_override"])
            for source_id in contract["outcome_source_ids"]:
                self.assertIn("outcome", source_by_id[source_id]["evidence_roles"])

        self.assertEqual(WAVE8_COMANCHE_OUTCOME_OVERRIDES, {})
        self.assertEqual(WAVE8_COMANCHE_OUTCOME_OVERRIDE_IDS, frozenset())

    def test_direct_construction_emits_only_four_schema_valid_wins(self) -> None:
        events = self._events()
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_COMANCHE_CONTRACT_IDS,
        )
        self.assertEqual(len(events), 4)
        for event in events:
            Event.from_dict(event)
            contract = WAVE8_COMANCHE_CONTRACTS[event["hced_candidate_id"]]
            self.assertTrue(event["id"].startswith("hced_wave8_comanche_"))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertEqual(event["date_precision"], "day")
            self.assertEqual(
                event["canonical_event_key"],
                contract["canonical_event"]["canonical_key"],
            )
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
            self.assertNotIn(
                "inconclusive_engagement",
                {participant["termination"] for participant in event["participants"]},
            )

    def test_unsafe_points_are_quarantined_without_mutating_shared_manifests(self) -> None:
        before_points = HCED_POINT_QUARANTINE_IDS
        before_countries = HCED_COUNTRY_QUARANTINE_IDS
        self.assertEqual(
            WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS,
            WAVE8_COMANCHE_CONTRACT_IDS,
        )
        self.assertEqual(WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            WAVE8_COMANCHE_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS,
                "country": WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS,
            },
        )
        self.assertEqual(
            wave8_comanche_location_quarantine_additions(),
            {
                "country": WAVE8_COMANCHE_COUNTRY_QUARANTINE_ADDITIONS,
                "point": WAVE8_COMANCHE_POINT_QUARANTINE_ADDITIONS,
            },
        )

        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "United States")
            self.assertIn("location_provenance", event)
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_iwbd_duplicate_audit_is_explicitly_empty(self) -> None:
        self.assertEqual(WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            WAVE8_COMANCHE_IWBD_DUPLICATE_DISPOSITION_IDS,
            frozenset(),
        )
        possible_names = {
            ("adobe walls", "1864"),
            ("first battle of adobe walls", "1864"),
            ("colorado", "1840"),
            ("crooked creek", "1859"),
            ("battle of crooked creek", "1859"),
            ("plum creek, texas", "1840"),
            ("battle of plum creek", "1840"),
            ("rush springs", "1858"),
            ("battle of the wichita village", "1858"),
            ("walkers creek", "1844"),
            ("battle of walker's creek", "1844"),
        }
        iwbd_name_years = {
            (
                str(row.get("name", "")).casefold(),
                str(row.get("start_date", ""))[:4],
            )
            for row in self.iwbd_rows
        }
        self.assertTrue(possible_names.isdisjoint(iwbd_name_years))


if __name__ == "__main__":
    unittest.main()
