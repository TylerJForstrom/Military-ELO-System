import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_kiowa import (
    WAVE8_KIOWA_CONTRACT_IDS,
    WAVE8_KIOWA_CONTRACTS,
    WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS,
    WAVE8_KIOWA_ENTITIES,
    WAVE8_KIOWA_EXPECTED_CANDIDATE_IDS,
    WAVE8_KIOWA_FINAL_AUDIT_SIGNATURE,
    WAVE8_KIOWA_HOLD_IDS,
    WAVE8_KIOWA_HOLDS,
    WAVE8_KIOWA_INTEGRATION_DISPOSITIONS,
    WAVE8_KIOWA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_KIOWA_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_KIOWA_OUTCOME_OVERRIDES,
    WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS,
    WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS,
    WAVE8_KIOWA_RESERVED_IDS,
    WAVE8_KIOWA_SOURCES,
    install_wave8_kiowa_entities,
    install_wave8_kiowa_sources,
    promote_wave8_kiowa_contracts,
    validate_wave8_kiowa_integration_dispositions,
    validate_wave8_kiowa_queue_contracts,
    wave8_kiowa_audit_signature,
    wave8_kiowa_cohort_counts,
    wave8_kiowa_counts,
    wave8_kiowa_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_kiowa_"

LITTLE_KIOWA = "kicking_bird_kiowa_war_party_little_wichita_1870"
LITTLE_CAVALRY = "mclellan_sixth_cavalry_detachment_1870"
LYMAN_BUFFALO_WARRIORS = "lyman_buffalo_wallow_kiowa_comanche_warriors_1874"
LYMAN_ESCORT = "lyman_supply_train_escort_1874"
BUFFALO_DETAIL = "buffalo_wallow_dispatch_detail_1874"
PALO_WARRIORS = "palo_duro_comanche_kiowa_cheyenne_war_parties_1874"
PALO_COLUMN = "mackenzie_fourth_cavalry_tonkawa_column_1874"


EXPECTED_WINNERS_AND_LOSERS = {
    "hced-Little Rock1870-1": ({LITTLE_KIOWA}, {LITTLE_CAVALRY}),
    "hced-Lymans Wagon Train1874-1": ({LYMAN_ESCORT}, {LYMAN_BUFFALO_WARRIORS}),
    "hced-Buffalo Wallow1874-1": ({BUFFALO_DETAIL}, {LYMAN_BUFFALO_WARRIORS}),
    "hced-Palo Duro1874-1": ({PALO_COLUMN}, {PALO_WARRIORS}),
}


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


class Wave8KiowaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.lane_rows = [
            row
            for row in cls.hced_rows
            if row.get("candidate_id") in WAVE8_KIOWA_RESERVED_IDS
        ]

    def _installed(self):
        entity_ids = {str(entity["id"]) for entity in WAVE8_KIOWA_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in entity_ids
        }
        install_wave8_kiowa_entities(entities)

        source_ids = {str(source["id"]) for source in WAVE8_KIOWA_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in source_ids
        }
        install_wave8_kiowa_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_KIOWA_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_kiowa_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return entities, sources, events

    def test_signature_inventory_counts_and_cohorts_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_KIOWA_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_KIOWA_ENTITIES,
            "expected_candidate_ids": sorted(WAVE8_KIOWA_EXPECTED_CANDIDATE_IDS),
            "holds": WAVE8_KIOWA_HOLDS,
            "integration_dispositions": WAVE8_KIOWA_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": WAVE8_KIOWA_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_zero_overlap_audit": WAVE8_KIOWA_IWBD_ZERO_OVERLAP_AUDIT,
            "outcome_overrides": WAVE8_KIOWA_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS
            ),
            "related_hced_dispositions": WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS,
            "sources": WAVE8_KIOWA_SOURCES,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent, WAVE8_KIOWA_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_kiowa_audit_signature(), independent)
        self.assertEqual(WAVE8_KIOWA_CONTRACT_IDS, set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertEqual(
            WAVE8_KIOWA_HOLD_IDS,
            {"hced-Lost Valley, Texas1874-1"},
        )
        self.assertEqual(
            WAVE8_KIOWA_RESERVED_IDS,
            WAVE8_KIOWA_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            wave8_kiowa_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 2,
                "holds": 1,
                "integration_dispositions": 4,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 7,
                "new_sources": 15,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "related_hced_dispositions": 2,
                "reviewed_hced_rows": 5,
            },
        )
        self.assertEqual(
            wave8_kiowa_cohort_counts(),
            {
                "little_wichita_campaign_1870": 1,
                "red_river_war_lyman_buffalo_actions_1874": 2,
                "red_river_war_palo_duro_1874": 1,
            },
        )

    def test_all_and_only_five_exact_kiowa_indian_rows_are_owned(self) -> None:
        exact_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if row.get("side_1_raw") == "Kiowa Indians"
            or row.get("side_2_raw") == "Kiowa Indians"
        }
        self.assertEqual(set(exact_rows), WAVE8_KIOWA_EXPECTED_CANDIDATE_IDS)
        self.assertEqual(
            validate_wave8_kiowa_queue_contracts(self.hced_rows),
            {"promotion_contracts": 4, "holds": 1, "reviewed_hced_rows": 5},
        )
        for candidate_id, row in exact_rows.items():
            disposition = (
                WAVE8_KIOWA_CONTRACTS.get(candidate_id)
                or WAVE8_KIOWA_HOLDS[candidate_id]
            )
            self.assertEqual(
                canonical_hced_row_sha256(row),
                disposition["raw_row_sha256"],
            )

        future = copy.deepcopy(self.hced_rows)
        future.append(
            {
                "candidate_id": "hced-FutureKiowa1880-1",
                "side_1_raw": "Kiowa Indians",
                "side_2_raw": "Unreviewed opponent",
            }
        )
        with self.assertRaisesRegex(ValueError, "exact Kiowa Indians inventory changed"):
            validate_wave8_kiowa_queue_contracts(future)

    def test_every_row_hash_is_pinned_and_drift_fails_closed(self) -> None:
        self.assertEqual(len(self.lane_rows), 5)
        for candidate_id in sorted(WAVE8_KIOWA_RESERVED_IDS):
            changed = copy.deepcopy(self.lane_rows)
            next(row for row in changed if row["candidate_id"] == candidate_id)[
                "name"
            ] += " tampered"
            with self.subTest(candidate_id=candidate_id):
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_kiowa_queue_contracts(changed)

        missing = [
            row
            for row in self.lane_rows
            if row["candidate_id"] != "hced-Little Rock1870-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_kiowa_queue_contracts(missing)

    def test_sources_and_event_bounded_identities_parse_and_install(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_KIOWA_SOURCES}
        self.assertEqual(len(source_by_id), 15)
        self.assertEqual(
            len({source["source_family_id"] for source in WAVE8_KIOWA_SOURCES}),
            15,
        )
        for source in WAVE8_KIOWA_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["evidence_roles"], sorted(set(source["evidence_roles"])))

        entity_by_id = {str(entity["id"]): entity for entity in WAVE8_KIOWA_ENTITIES}
        self.assertEqual(set(entity_by_id), {
            LITTLE_KIOWA,
            LITTLE_CAVALRY,
            LYMAN_BUFFALO_WARRIORS,
            LYMAN_ESCORT,
            BUFFALO_DETAIL,
            PALO_WARRIORS,
            PALO_COLUMN,
        })
        for entity in WAVE8_KIOWA_ENTITIES:
            Entity.from_dict(entity)
            self.assertIn(entity["start_year"], {1870, 1874})
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertNotIn(
                entity["name"].casefold(),
                {"kiowa", "kiowa indians", "kiowa tribe", "comanche", "united states"},
            )
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        entities, sources, _ = self._installed()
        install_wave8_kiowa_entities(entities)
        install_wave8_kiowa_sources(sources)
        for entity_id, entity in entity_by_id.items():
            self.assertEqual(entities[entity_id], entity)
        for source_id, source in source_by_id.items():
            self.assertEqual(sources[source_id], source)

    def test_lost_valley_is_unknown_not_a_draw_or_invented_result(self) -> None:
        hold = WAVE8_KIOWA_HOLDS["hced-Lost Valley, Texas1874-1"]
        self.assertEqual(hold["disposition"], "hold")
        self.assertEqual(
            hold["hold_category"],
            "contradictory_tactical_outcome_evidence",
        )
        self.assertEqual((hold["reviewed_outcome"], hold["result_type"]), ("unknown", "unknown"))
        self.assertTrue(hold["unknown_is_never_draw"])
        for forbidden in (
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "outcome_source_ids",
        ):
            self.assertNotIn(forbidden, hold)
        reason = hold["hold_reason"].casefold()
        self.assertIn("not promoted", reason)
        self.assertIn("reversed", reason)
        self.assertIn("draw", reason)
        self.assertIn("unknown remains unknown", reason)
        self.assertEqual(len(hold["evidence_refs"]), 4)

    def test_dates_coalitions_outcomes_and_provenance_are_exact(self) -> None:
        source_by_id = {str(source["id"]): source for source in WAVE8_KIOWA_SOURCES}
        expected_dates = {
            "hced-Little Rock1870-1": ("day", "12 July 1870"),
            "hced-Lymans Wagon Train1874-1": ("day_range", "9-14 September 1874"),
            "hced-Buffalo Wallow1874-1": ("day", "12 September 1874"),
            "hced-Palo Duro1874-1": ("day", "28 September 1874"),
        }
        for candidate_id, contract in WAVE8_KIOWA_CONTRACTS.items():
            self.assertEqual(
                (
                    contract["canonical_event"]["date_precision"],
                    contract["canonical_event"]["date_text"],
                ),
                expected_dates[candidate_id],
            )
            winners, losers = EXPECTED_WINNERS_AND_LOSERS[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), winners)
            self.assertEqual(set(contract["side_2_entity_ids"]), losers)
            self.assertEqual((contract["result_type"], contract["winner_side"]), ("win", 1))
            self.assertTrue(contract["actor_override"])
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])
            self.assertEqual(
                contract["duplicate_ownership"],
                {"owner_module": "wave8_kiowa", "status": "canonical_hced_owner"},
            )
            self.assertTrue(set(contract["outcome_source_ids"]) <= set(contract["evidence_refs"]))
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in contract["outcome_source_ids"]
                    }
                ),
            )
        self.assertEqual(WAVE8_KIOWA_OUTCOME_OVERRIDES, {})

    def test_emission_is_four_tactical_wins_without_an_ethnic_bridge(self) -> None:
        _, _, events = self._emit()
        self.assertEqual(len(events), 4)
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_WINNERS_AND_LOSERS))
        self.assertNotIn("hced-Lost Valley, Texas1874-1", by_candidate)
        forbidden_ids = {
            "kiowa",
            "kiowa_indians",
            "kiowa_tribe",
            "comanche",
            "cheyenne",
            "us_united_states_of_america_reconstruction",
        }
        for candidate_id, event in by_candidate.items():
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
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
            self.assertEqual((winners, losers), EXPECTED_WINNERS_AND_LOSERS[candidate_id])
            self.assertTrue((winners | losers).isdisjoint(forbidden_ids))
            terminations = {item["termination"] for item in event["participants"]}
            self.assertNotIn("inconclusive_engagement", terminations)
            self.assertFalse(any("draw" in item for item in terminations))
            self.assertEqual(
                event["outcome_source_ids"],
                WAVE8_KIOWA_CONTRACTS[candidate_id]["outcome_source_ids"],
            )

    def test_lyman_and_buffalo_are_linked_but_distinct_engagements(self) -> None:
        lyman = WAVE8_KIOWA_CONTRACTS["hced-Lymans Wagon Train1874-1"]
        buffalo = WAVE8_KIOWA_CONTRACTS["hced-Buffalo Wallow1874-1"]
        self.assertEqual(
            lyman["side_2_entity_ids"],
            [LYMAN_BUFFALO_WARRIORS],
        )
        self.assertEqual(
            buffalo["side_2_entity_ids"],
            [LYMAN_BUFFALO_WARRIORS],
        )
        self.assertNotEqual(
            lyman["side_1_entity_ids"],
            buffalo["side_1_entity_ids"],
        )
        self.assertNotEqual(
            lyman["canonical_event"]["canonical_key"],
            buffalo["canonical_event"]["canonical_key"],
        )
        boundary = WAVE8_KIOWA_RELATED_HCED_DISPOSITIONS[
            "hced-Buffalo Wallow1874-1"
        ]
        self.assertEqual(boundary["disposition"], "distinct_linked_engagements")
        self.assertEqual(
            boundary["related_hced_candidate_id"],
            "hced-Lymans Wagon Train1874-1",
        )

    def test_palo_duro_rates_war_parties_not_families_or_campaign_umbrella(self) -> None:
        entity = next(
            entity for entity in WAVE8_KIOWA_ENTITIES if entity["id"] == PALO_WARRIORS
        )
        note = entity["continuity_note"].casefold()
        self.assertIn("armed war parties", note)
        self.assertIn("families", note)
        self.assertIn("noncombatants", note)
        contract = WAVE8_KIOWA_CONTRACTS["hced-Palo Duro1874-1"]
        self.assertEqual(contract["side_1_entity_ids"], [PALO_COLUMN])
        self.assertEqual(contract["side_2_entity_ids"], [PALO_WARRIORS])
        self.assertIn("not extra Elo events", contract["audit_note"])

    def test_location_quarantine_is_promoted_only_and_strips_all_points(self) -> None:
        self.assertEqual(WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS, WAVE8_KIOWA_CONTRACT_IDS)
        self.assertEqual(WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS, set())
        self.assertNotIn(
            "hced-Lost Valley, Texas1874-1",
            WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS,
        )
        self.assertEqual(
            wave8_kiowa_location_quarantine_additions(),
            {
                "country": WAVE8_KIOWA_COUNTRY_QUARANTINE_ADDITIONS,
                "point": WAVE8_KIOWA_POINT_QUARANTINE_ADDITIONS,
            },
        )
        _, _, events = self._emit()
        for event in events:
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "United States")

    def test_related_cross_lane_and_iwbd_dispositions_fail_closed(self) -> None:
        self.assertEqual(WAVE8_KIOWA_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(set(WAVE8_KIOWA_IWBD_ZERO_OVERLAP_AUDIT), WAVE8_KIOWA_RESERVED_IDS)
        self.assertEqual(
            set(WAVE8_KIOWA_CROSS_LANE_DISPOSITIONS),
            {"wave8_algiers_cheyenne", "wave8_comanche"},
        )
        self.assertEqual(
            validate_wave8_kiowa_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
            ),
            {
                "cross_lane_hced_dispositions": 2,
                "integration_dispositions": 4,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 5,
                "related_hced_dispositions": 2,
            },
        )

        future_iwbd = [
            *self.iwbd_rows,
            {
                "candidate_id": "iwbd-future-palo-duro",
                "name": "Palo Duro Canyon",
                "start_date": "1874-09-28",
                "end_date": "1874-09-28",
            },
        ]
        with self.assertRaisesRegex(ValueError, "plausible IWBD overlap"):
            validate_wave8_kiowa_integration_dispositions(
                self.hced_rows,
                future_iwbd,
            )

        changed_hced = copy.deepcopy(self.hced_rows)
        next(
            row
            for row in changed_hced
            if row["candidate_id"] == "hced-Adobe Walls1874-1"
        )["name"] += " tampered"
        with self.assertRaisesRegex(ValueError, "Adobe Walls fingerprint changed"):
            validate_wave8_kiowa_integration_dispositions(
                changed_hced,
                self.iwbd_rows,
            )

    def test_duplicate_and_entity_window_guards_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        collision = [
            *existing,
            {
                "id": "synthetic_duplicate",
                "name": "Battle of Palo Duro Canyon",
                "year": 1874,
            },
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_kiowa_contracts(self.hced_rows, entities, collision)

        broken = copy.deepcopy(entities)
        broken[LITTLE_KIOWA]["end_year"] = 1869
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_kiowa_contracts(self.hced_rows, broken, existing)


if __name__ == "__main__":
    unittest.main()
