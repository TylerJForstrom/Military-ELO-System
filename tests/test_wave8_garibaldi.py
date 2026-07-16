import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.hced import promote_hced_crosswalk_rows
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_garibaldi import (
    WAVE8_GARIBALDI_CONTRACT_IDS,
    WAVE8_GARIBALDI_CONTRACTS,
    WAVE8_GARIBALDI_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_GARIBALDI_CROSS_LANE_DISPOSITIONS,
    WAVE8_GARIBALDI_ENTITIES,
    WAVE8_GARIBALDI_EXPECTED_CANDIDATE_IDS,
    WAVE8_GARIBALDI_FINAL_AUDIT_SIGNATURE,
    WAVE8_GARIBALDI_HOLD_IDS,
    WAVE8_GARIBALDI_HOLDS,
    WAVE8_GARIBALDI_INTEGRATION_DISPOSITIONS,
    WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_GARIBALDI_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_GARIBALDI_OUTCOME_OVERRIDES,
    WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS,
    WAVE8_GARIBALDI_RESERVED_IDS,
    WAVE8_GARIBALDI_SOURCES,
    install_wave8_garibaldi_entities,
    install_wave8_garibaldi_sources,
    promote_wave8_garibaldi_contracts,
    validate_wave8_garibaldi_integration_dispositions,
    validate_wave8_garibaldi_queue_contracts,
    wave8_garibaldi_audit_signature,
    wave8_garibaldi_cohort_counts,
    wave8_garibaldi_counts,
    wave8_garibaldi_location_quarantine_additions,
)
from military_elo.promotion.wave8_naples import (
    WAVE8_NAPLES_CONTRACTS,
    WAVE8_NAPLES_RESERVED_IDS,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_garibaldi_"
PALERMO_ID = "hced-Palermo1860-1"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue is unavailable: {path.name}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


EXPECTED_PROMOTIONS = {
    "hced-Monte Suella1866-1": {
        "canonical": ("Battle of Monte Suello", 1866, "3 July 1866"),
        "sides": (("austrian_empire",), ("italian_volunteer_corps_1866",)),
        "winner_side": 2,
        "source_outcome_override": True,
    },
    "hced-Monterotondo1867-1": {
        "canonical": ("Battle of Monterotondo", 1867, "25-26 October 1867"),
        "sides": (
            ("garibaldian_agro_romano_volunteers_1867",),
            ("clio_it_papal_state_1_755_50394c66",),
        ),
        "winner_side": 1,
        "source_outcome_override": False,
    },
    "hced-Varese1859-1": {
        "canonical": ("Battle of Varese", 1859, "26 May 1859"),
        "sides": (
            ("sardinian_cacciatori_delle_alpi_1859",),
            ("austrian_empire",),
        ),
        "winner_side": 1,
        "source_outcome_override": False,
    },
    "hced-Villa Glori1867-1": {
        "canonical": ("Battle of Villa Glori", 1867, "23 October 1867"),
        "sides": (
            ("clio_it_papal_state_1_755_50394c66",),
            ("cairoli_villa_glori_band_1867",),
        ),
        "winner_side": 1,
        "source_outcome_override": False,
    },
}


class Wave8GaribaldiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _installed(self):
        fixture_entity_ids = {str(entity["id"]) for entity in WAVE8_GARIBALDI_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in fixture_entity_ids
        }
        install_wave8_garibaldi_entities(entities)

        fixture_source_ids = {str(source["id"]) for source in WAVE8_GARIBALDI_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in fixture_source_ids
        }
        install_wave8_garibaldi_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_GARIBALDI_CONTRACT_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_garibaldi_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_signature_inventory_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_GARIBALDI_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_GARIBALDI_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "entities": WAVE8_GARIBALDI_ENTITIES,
            "expected_candidate_ids": sorted(
                WAVE8_GARIBALDI_EXPECTED_CANDIDATE_IDS
            ),
            "holds": WAVE8_GARIBALDI_HOLDS,
            "integration_dispositions": WAVE8_GARIBALDI_INTEGRATION_DISPOSITIONS,
            "outcome_overrides": WAVE8_GARIBALDI_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_GARIBALDI_SOURCES,
        }
        independent_signature = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent_signature, WAVE8_GARIBALDI_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_garibaldi_audit_signature(), independent_signature)
        self.assertEqual(
            WAVE8_GARIBALDI_CONTRACT_IDS,
            frozenset(EXPECTED_PROMOTIONS),
        )
        self.assertEqual(
            WAVE8_GARIBALDI_HOLD_IDS,
            {"hced-Morazzone1848-1", "hced-Tre Ponti1859-1"},
        )
        self.assertEqual(
            WAVE8_GARIBALDI_RESERVED_IDS,
            WAVE8_GARIBALDI_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            wave8_garibaldi_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 1,
                "holds": 2,
                "integration_dispositions": 4,
                "iwbd_duplicate_dispositions": 3,
                "new_entities": 5,
                "new_sources": 9,
                "newly_rated_events": 4,
                "outcome_overrides": 1,
                "point_quarantine_additions": 3,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 6,
            },
        )
        self.assertEqual(
            wave8_garibaldi_cohort_counts(),
            {
                "garibaldian_agro_romano_campaign_1867": 2,
                "second_italian_war_of_independence_1859": 1,
                "third_italian_war_of_independence_1866": 1,
            },
        )

    def test_sources_and_campaign_bounded_entities_parse_and_install(self) -> None:
        source_ids = set()
        for source in WAVE8_GARIBALDI_SOURCES:
            Source.from_dict(source)
            source_ids.add(source["id"])
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
        self.assertEqual(len(source_ids), 9)

        entity_ids = set()
        expected_years = {1848, 1859, 1866, 1867}
        actual_years = set()
        for entity in WAVE8_GARIBALDI_ENTITIES:
            Entity.from_dict(entity)
            entity_ids.add(entity["id"])
            actual_years.add(entity["start_year"])
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertNotIn("redshirts", entity["name"].casefold())
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertTrue(set(entity["source_ids"]) <= source_ids)
        self.assertEqual(len(entity_ids), 5)
        self.assertEqual(actual_years, expected_years)

        entities, sources, _ = self._installed()
        for entity in WAVE8_GARIBALDI_ENTITIES:
            Entity.from_dict(entities[entity["id"]])
        for source in WAVE8_GARIBALDI_SOURCES:
            Source.from_dict(sources[source["id"]])

    def test_all_six_queue_hashes_are_pinned_and_drift_fails_closed(self) -> None:
        rows_by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        for inventory in (WAVE8_GARIBALDI_CONTRACTS, WAVE8_GARIBALDI_HOLDS):
            for candidate_id, disposition in inventory.items():
                self.assertEqual(
                    canonical_hced_row_sha256(rows_by_id[candidate_id]),
                    disposition["raw_row_sha256"],
                )
        self.assertEqual(
            validate_wave8_garibaldi_queue_contracts(self.hced_rows),
            {"promotion_contracts": 4, "holds": 2, "reviewed_hced_rows": 6},
        )

        changed_promotion = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed_promotion
            if row["candidate_id"] == "hced-Varese1859-1"
        )["winner_raw"] = "unknown"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_garibaldi_queue_contracts(changed_promotion)

        changed_hold = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed_hold
            if row["candidate_id"] == "hced-Morazzone1848-1"
        )["name"] = "Morazzone drift"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_garibaldi_queue_contracts(changed_hold)

    def test_exact_dates_sides_outcomes_and_direct_provenance(self) -> None:
        self.assertEqual(set(EXPECTED_PROMOTIONS), WAVE8_GARIBALDI_CONTRACT_IDS)
        sources = {str(source["id"]): source for source in WAVE8_GARIBALDI_SOURCES}
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            contract = WAVE8_GARIBALDI_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(
                (canonical["name"], canonical["year_low"], canonical["date_text"]),
                expected["canonical"],
            )
            self.assertEqual(canonical["year_low"], canonical["year_high"])
            self.assertEqual(canonical["date_precision"], "day")
            self.assertEqual(
                (
                    tuple(contract["side_1_entity_ids"]),
                    tuple(contract["side_2_entity_ids"]),
                ),
                expected["sides"],
            )
            self.assertEqual(contract["winner_side"], expected["winner_side"])
            self.assertIs(
                contract["source_outcome_override"],
                expected["source_outcome_override"],
            )
            self.assertIs(
                contract["outcome_reversal"],
                expected["source_outcome_override"],
            )
            self.assertTrue(contract["actor_override"])
            self.assertTrue(contract["outcome_source_ids"])
            self.assertEqual(
                contract["outcome_source_ids"],
                sorted(set(contract["outcome_source_ids"])),
            )
            self.assertLessEqual(
                set(contract["outcome_source_ids"]),
                set(contract["evidence_refs"]),
            )
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(
                    {
                        sources[source_id]["source_family_id"]
                        for source_id in contract["outcome_source_ids"]
                    }
                ),
            )
            self.assertTrue(
                all(
                    "outcome" in sources[source_id]["evidence_roles"]
                    for source_id in contract["outcome_source_ids"]
                )
            )

        self.assertEqual(set(WAVE8_GARIBALDI_OUTCOME_OVERRIDES), {"hced-Monte Suella1866-1"})
        villa_participants = {
            *WAVE8_GARIBALDI_CONTRACTS["hced-Villa Glori1867-1"][
                "side_1_entity_ids"
            ],
            *WAVE8_GARIBALDI_CONTRACTS["hced-Villa Glori1867-1"][
                "side_2_entity_ids"
            ],
        }
        self.assertNotIn("kingdom_france", villa_participants)
        self.assertNotIn("garibaldian_agro_romano_volunteers_1867", villa_participants)

    def test_morazzone_and_tre_ponti_remain_unknown_never_draw(self) -> None:
        expected = {
            "hced-Morazzone1848-1": (
                "26 August 1848",
                ("austrian_empire",),
                ("garibaldi_lombard_volunteer_column_1848",),
            ),
            "hced-Tre Ponti1859-1": (
                "15 June 1859",
                ("austrian_empire",),
                ("sardinian_cacciatori_delle_alpi_1859",),
            ),
        }
        for candidate_id, (date_text, side_1, side_2) in expected.items():
            hold = WAVE8_GARIBALDI_HOLDS[candidate_id]
            self.assertEqual(hold["canonical_event"]["date_text"], date_text)
            self.assertEqual(tuple(hold["side_1_entity_ids"]), side_1)
            self.assertEqual(tuple(hold["side_2_entity_ids"]), side_2)
            self.assertEqual(hold["disposition"], "hold")
            self.assertEqual(hold["hold_category"], "irreconcilable_tactical_outcome")
            self.assertEqual(hold["reviewed_outcome"], "unknown")
            self.assertEqual(hold["result_type"], "unknown")
            self.assertIs(hold["unknown_is_never_draw"], True)
            self.assertNotIn("winner_side", hold)

    def test_palermo_is_exclusively_owned_by_the_naples_lane(self) -> None:
        self.assertNotIn(PALERMO_ID, WAVE8_GARIBALDI_RESERVED_IDS)
        self.assertNotIn(PALERMO_ID, WAVE8_GARIBALDI_CONTRACTS)
        self.assertIn(PALERMO_ID, WAVE8_NAPLES_RESERVED_IDS)
        self.assertIn(PALERMO_ID, WAVE8_NAPLES_CONTRACTS)
        self.assertTrue(
            WAVE8_GARIBALDI_RESERVED_IDS.isdisjoint(WAVE8_NAPLES_RESERVED_IDS)
        )
        disposition = WAVE8_GARIBALDI_CROSS_LANE_DISPOSITIONS[PALERMO_ID]
        self.assertEqual(disposition["disposition"], "external_lane_owner")
        self.assertEqual(
            disposition["owner_module"],
            "military_elo.promotion.wave8_naples",
        )
        self.assertEqual(
            disposition["raw_row_sha256"],
            WAVE8_NAPLES_CONTRACTS[PALERMO_ID]["raw_row_sha256"],
        )

    def test_iwbd_duplicates_and_palermo_boundary_fail_closed(self) -> None:
        expected_iwbd = {
            "iwbd-10-4-43": "hced-Morazzone1848-1",
            "iwbd-28-10-98": "hced-Varese1859-1",
            "iwbd-28-10-104": "hced-Tre Ponti1859-1",
        }
        self.assertEqual(
            {
                candidate_id: disposition["hced_candidate_id"]
                for candidate_id, disposition in (
                    WAVE8_GARIBALDI_IWBD_DUPLICATE_DISPOSITIONS.items()
                )
            },
            expected_iwbd,
        )
        self.assertEqual(
            set(WAVE8_GARIBALDI_INTEGRATION_DISPOSITIONS),
            {PALERMO_ID, *expected_iwbd},
        )
        self.assertEqual(
            validate_wave8_garibaldi_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
            ),
            {
                "cross_lane_hced_dispositions": 1,
                "integration_dispositions": 4,
                "iwbd_duplicate_dispositions": 3,
            },
        )

        changed_iwbd = copy.deepcopy(self.iwbd_rows)
        next(
            row
            for row in changed_iwbd
            if row["candidate_id"] == "iwbd-28-10-104"
        )["winner_raw"] = "unknown"
        with self.assertRaisesRegex(ValueError, "IWBD duplicate fingerprint changed"):
            validate_wave8_garibaldi_integration_dispositions(
                self.hced_rows,
                changed_iwbd,
            )

        changed_hced = copy.deepcopy(self.hced_rows)
        next(row for row in changed_hced if row["candidate_id"] == PALERMO_ID)[
            "winner_raw"
        ] = "unknown"
        with self.assertRaisesRegex(ValueError, "Palermo fingerprint changed"):
            validate_wave8_garibaldi_integration_dispositions(
                changed_hced,
                self.iwbd_rows,
            )

    def test_reservations_block_generic_crosswalk(self) -> None:
        owned_rows = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") in WAVE8_GARIBALDI_RESERVED_IDS
        ]
        result = promote_hced_crosswalk_rows(
            owned_rows,
            owners={},
            curated_seed_keys=set(),
            ensure_candidate_entity=lambda _entity: None,
            reserved_candidate_ids=WAVE8_GARIBALDI_RESERVED_IDS,
        )
        self.assertEqual(len(owned_rows), 6)
        self.assertEqual(result["events"], [])
        self.assertEqual(result["deferred_label_rows"], [])
        self.assertEqual(result["label_observations"], {})
        self.assertEqual(result["rejections"]["reserved_candidate_contract"], 6)

    def test_four_events_emit_parse_and_apply_only_lane_location_additions(self) -> None:
        before_points = HCED_POINT_QUARANTINE_IDS
        before_countries = HCED_COUNTRY_QUARANTINE_IDS
        before_point_values = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_country_values = frozenset(HCED_COUNTRY_QUARANTINE_IDS)

        entities, sources, events = self._emit()
        self.assertEqual(len(events), 4)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), WAVE8_GARIBALDI_CONTRACT_IDS)
        self.assertTrue(WAVE8_GARIBALDI_HOLD_IDS.isdisjoint(by_candidate))
        self.assertNotIn(PALERMO_ID, by_candidate)

        for entity in WAVE8_GARIBALDI_ENTITIES:
            Entity.from_dict(entities[entity["id"]])
        for source in WAVE8_GARIBALDI_SOURCES:
            Source.from_dict(sources[source["id"]])
        for candidate_id, event in by_candidate.items():
            Event.from_dict(event)
            contract = WAVE8_GARIBALDI_CONTRACTS[candidate_id]
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["name"], contract["canonical_event"]["name"])
            self.assertEqual(event["date_precision"], "day")
            self.assertEqual(
                event["canonical_event_key"],
                contract["canonical_event"]["canonical_key"],
            )
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertEqual(event.get("modern_location_country"), "Italy")

            winner_side = int(contract["winner_side"])
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
            self.assertEqual(
                winners,
                set(contract[f"side_{winner_side}_entity_ids"]),
            )
            self.assertEqual(
                losers,
                set(contract[f"side_{3 - winner_side}_entity_ids"]),
            )

        self.assertNotIn("geometry", by_candidate["hced-Monte Suella1866-1"])
        self.assertNotIn("geometry", by_candidate["hced-Villa Glori1867-1"])
        self.assertIn("geometry", by_candidate["hced-Monterotondo1867-1"])
        self.assertIn("geometry", by_candidate["hced-Varese1859-1"])

        expected_points = {
            "hced-Monte Suella1866-1",
            "hced-Tre Ponti1859-1",
            "hced-Villa Glori1867-1",
        }
        self.assertEqual(WAVE8_GARIBALDI_POINT_QUARANTINE_ADDITIONS, expected_points)
        self.assertEqual(WAVE8_GARIBALDI_COUNTRY_QUARANTINE_ADDITIONS, set())
        self.assertEqual(
            WAVE8_GARIBALDI_LOCATION_QUARANTINE_ADDITIONS,
            {"point": expected_points, "country": set()},
        )
        self.assertEqual(
            wave8_garibaldi_location_quarantine_additions(),
            {"point": expected_points, "country": set()},
        )
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_point_values)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_country_values)

        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_garibaldi_contracts(
                self.hced_rows,
                entities,
                [*self._installed()[2], events[0]],
            )


if __name__ == "__main__":
    unittest.main()
