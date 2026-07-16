import copy
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_exact import promote_exact_hced_contracts
from military_elo.promotion.wave8_wales import (
    WAVE8_WALES_CONTRACT_IDS,
    WAVE8_WALES_CONTRACTS,
    WAVE8_WALES_ENTITIES,
    WAVE8_WALES_FINAL_AUDIT_SIGNATURE,
    WAVE8_WALES_HOLD_IDS,
    WAVE8_WALES_HOLDS,
    WAVE8_WALES_OUTCOME_OVERRIDE_IDS,
    WAVE8_WALES_RESERVED_IDS,
    WAVE8_WALES_SOURCES,
    install_wave8_wales_entities,
    install_wave8_wales_sources,
    promote_wave8_wales_contracts,
    validate_wave8_wales_queue_contracts,
    wave8_wales_cohort_counts,
    wave8_wales_counts,
    wave8_wales_signature,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows():
    path = ROOT / "data" / "review" / "hced-candidates.jsonl"
    if not path.exists():
        raise unittest.SkipTest("locked HCED review queue is unavailable")
    return [json.loads(line) for line in path.read_text().splitlines() if line]


class Wave8WalesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.all_rows = _rows()
        cls.lane_rows = [
            row
            for row in cls.all_rows
            if row.get("candidate_id") in WAVE8_WALES_RESERVED_IDS
        ]
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")

    def _direct_inputs(self):
        """Build against either pre-lane or already-materialized artifacts."""

        lane_entity_ids = {entity["id"] for entity in WAVE8_WALES_ENTITIES}
        entities = {
            entity["id"]: entity
            for entity in self.release_entities
            if entity["id"] not in lane_entity_ids
        }
        install_wave8_wales_entities(entities)
        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_WALES_RESERVED_IDS
        ]
        return entities, existing

    def _direct_events(self):
        entities, existing = self._direct_inputs()
        return promote_wave8_wales_contracts(
            self.lane_rows,
            entities,
            existing,
        )

    def test_inventory_signature_counts_and_cohorts_are_exact(self) -> None:
        self.assertEqual(
            WAVE8_WALES_CONTRACT_IDS,
            {
                "hced-Aber Edw1282-1",
                "hced-Bangor1282-1",
                "hced-Coleshill1157-1",
                "hced-Pilleth1402-1",
            },
        )
        self.assertEqual(
            WAVE8_WALES_HOLD_IDS,
            {
                "hced-Aberdare, Wales1093-1",
                "hced-Beandun614-1",
                "hced-Conwy1295-1",
                "hced-Penselwood658-1",
                "hced-Ystradowen1032-1",
            },
        )
        self.assertEqual(
            WAVE8_WALES_RESERVED_IDS,
            WAVE8_WALES_CONTRACT_IDS | WAVE8_WALES_HOLD_IDS,
        )
        self.assertEqual(
            WAVE8_WALES_OUTCOME_OVERRIDE_IDS,
            {"hced-Coleshill1157-1"},
        )
        self.assertEqual(
            wave8_wales_signature(),
            WAVE8_WALES_FINAL_AUDIT_SIGNATURE,
        )
        self.assertEqual(
            wave8_wales_counts(),
            {
                "holds": 5,
                "newly_rated_events": 4,
                "outcome_overrides": 1,
                "promotion_contracts": 4,
                "reviewed_hced_rows": 9,
            },
        )
        self.assertEqual(
            wave8_wales_cohort_counts(),
            {
                "glyndwr_revolt_1402": 1,
                "llywelyn_final_war_1282": 2,
                "owain_gwynedd_1157": 1,
            },
        )

    def test_sources_and_entities_are_exact_bounded_and_alias_free(self) -> None:
        self.assertEqual((len(WAVE8_WALES_ENTITIES), len(WAVE8_WALES_SOURCES)), (3, 11))
        source_by_id = {source["id"]: source for source in WAVE8_WALES_SOURCES}
        self.assertEqual(len(source_by_id), len(WAVE8_WALES_SOURCES))
        for source in WAVE8_WALES_SOURCES:
            Source.from_dict(source)

        forbidden_identity_tokens = {"wales", "welsh", "cymru"}
        for entity in WAVE8_WALES_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual(entity["start_year"], entity["end_year"])
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertIn("no rating is inherited", entity["continuity_note"].casefold())
            self.assertNotIn(entity["id"].casefold(), forbidden_identity_tokens)
            self.assertNotIn(entity["name"].casefold(), forbidden_identity_tokens)
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        installed_sources = {
            source["id"]: source
            for source in self.release_sources
            if source["id"] not in source_by_id
        }
        install_wave8_wales_sources(installed_sources)
        for source_id, source in source_by_id.items():
            self.assertEqual(installed_sources[source_id], source)

    def test_all_nine_semantic_hashes_validate_and_each_drift_fails_closed(self) -> None:
        self.assertEqual(
            {row["candidate_id"] for row in self.lane_rows},
            WAVE8_WALES_RESERVED_IDS,
        )
        self.assertEqual(
            validate_wave8_wales_queue_contracts(self.lane_rows),
            {"promotion_contracts": 4, "holds": 5, "reviewed_hced_rows": 9},
        )
        indexed = {row["candidate_id"]: row for row in self.lane_rows}
        for inventory in (WAVE8_WALES_CONTRACTS, WAVE8_WALES_HOLDS):
            for candidate_id, item in inventory.items():
                self.assertEqual(
                    canonical_hced_row_sha256(indexed[candidate_id]),
                    item["raw_row_sha256"],
                )

        for candidate_id in sorted(WAVE8_WALES_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                changed = copy.deepcopy(self.lane_rows)
                next(
                    row for row in changed if row["candidate_id"] == candidate_id
                )["name"] += " tampered"
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_wales_queue_contracts(changed)

    def test_direct_construction_filters_current_artifacts_and_emits_only_four(self) -> None:
        events = self._direct_events()
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_WALES_CONTRACT_IDS,
        )
        self.assertTrue(
            WAVE8_WALES_HOLD_IDS.isdisjoint(
                {event["hced_candidate_id"] for event in events}
            )
        )
        self.assertEqual(len(events), 4)
        for event in events:
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith("hced_wave8_wales_"))
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertIn("Reservation:", event["summary"])

    def test_exact_names_dates_sides_outcomes_and_sources_are_pinned(self) -> None:
        expected = {
            "hced-Aber Edw1282-1": {
                "name": "Battle of Irfon Bridge",
                "date_text": "11 December 1282",
                "date_precision": "day",
                "winners": {"kingdom_england"},
                "losers": {"llywelyn_ap_gruffudd_final_war_forces_1282"},
                "outcome_source": "wave8_wales_coflein_irfon_bridge_1282",
            },
            "hced-Bangor1282-1": {
                "name": "Bridge of Boats",
                "date_text": "6 November 1282",
                "date_precision": "day",
                "winners": {"llywelyn_ap_gruffudd_final_war_forces_1282"},
                "losers": {"kingdom_england"},
                "outcome_source": "wave8_wales_coflein_bridge_of_boats_1282",
            },
            "hced-Coleshill1157-1": {
                "name": "Battle of Coleshill",
                "date_text": "1157 (exact day unresolved)",
                "date_precision": "year",
                "winners": {"dafydd_cynan_gwynedd_ambush_force_1157"},
                "losers": {"kingdom_england"},
                "outcome_source": "wave8_wales_coflein_coleshill_1157",
            },
            "hced-Pilleth1402-1": {
                "name": "Battle of Bryn Glas",
                "date_text": "22 June 1402",
                "date_precision": "day",
                "winners": {"owain_glyndwr_bryn_glas_force_1402"},
                "losers": {"kingdom_england"},
                "outcome_source": "wave8_wales_coflein_bryn_glas_1402",
            },
        }
        source_by_id = {source["id"]: source for source in WAVE8_WALES_SOURCES}
        by_candidate = {
            event["hced_candidate_id"]: event for event in self._direct_events()
        }
        self.assertEqual(set(by_candidate), set(expected))
        for candidate_id, event in by_candidate.items():
            contract = WAVE8_WALES_CONTRACTS[candidate_id]
            pinned = expected[candidate_id]
            self.assertEqual(event["name"], pinned["name"])
            self.assertEqual(event["date_precision"], pinned["date_precision"])
            self.assertEqual(
                contract["canonical_event"]["date_text"],
                pinned["date_text"],
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
            self.assertEqual(winners, pinned["winners"])
            self.assertEqual(losers, pinned["losers"])
            self.assertEqual(event["outcome_source_ids"], [pinned["outcome_source"]])
            self.assertEqual(
                event["outcome_source_family_ids"],
                ["rcahmw_coflein_battlefields"],
            )
            self.assertNotEqual(event["outcome_source_ids"], ["hced_dataset"])
            self.assertTrue(
                set(event["outcome_source_ids"]) <= set(event["source_ids"])
            )
            self.assertIn(
                "outcome",
                source_by_id[pinned["outcome_source"]]["evidence_roles"],
            )

    def test_coleshill_is_the_only_source_backed_outcome_override(self) -> None:
        self.assertEqual(
            {
                candidate_id
                for candidate_id, contract in WAVE8_WALES_CONTRACTS.items()
                if contract["source_outcome_override"]
            },
            {"hced-Coleshill1157-1"},
        )
        coleshill = WAVE8_WALES_CONTRACTS["hced-Coleshill1157-1"]
        self.assertEqual(coleshill["winner_side"], 2)
        self.assertEqual(
            coleshill["outcome_source_ids"],
            ["wave8_wales_coflein_coleshill_1157"],
        )
        self.assertIn("wider 1157 campaign", coleshill["audit_note"])

        entities, existing = self._direct_inputs()
        unsourced = {
            "hced-Coleshill1157-1": copy.deepcopy(coleshill),
        }
        unsourced["hced-Coleshill1157-1"].pop("outcome_source_ids")
        with self.assertRaisesRegex(
            ValueError,
            "outcome override lacks direct sources",
        ):
            promote_exact_hced_contracts(
                self.lane_rows,
                entities,
                existing,
                unsourced,
                lane_name="Wave 8 Wales test",
                event_id_prefix="test_wave8_wales_",
            )

    def test_five_holds_pin_the_historical_reservation_and_never_emit(self) -> None:
        expected_categories = {
            "hced-Aberdare, Wales1093-1": (
                "claimed_event_not_historically_supported"
            ),
            "hced-Beandun614-1": "exact_brittonic_belligerent_unresolved",
            "hced-Conwy1295-1": "event_conflation_and_location_unresolved",
            "hced-Penselwood658-1": "exact_brittonic_belligerent_unresolved",
            "hced-Ystradowen1032-1": "spurious_claimed_event",
        }
        self.assertEqual(set(expected_categories), WAVE8_WALES_HOLD_IDS)
        for candidate_id, category in expected_categories.items():
            hold = WAVE8_WALES_HOLDS[candidate_id]
            self.assertEqual(hold["hold_category"], category)
            self.assertTrue(hold["hold_reason"])
            self.assertTrue(hold["reservation"])
            self.assertTrue(hold["reviewed_outcome"])
            self.assertTrue(hold["unresolved_fields"])
            self.assertTrue(hold["evidence_refs"])

        self.assertIn(
            "forged by Iolo Morganwg",
            WAVE8_WALES_HOLDS["hced-Ystradowen1032-1"]["hold_reason"],
        )
        self.assertIn(
            "older placement",
            WAVE8_WALES_HOLDS["hced-Conwy1295-1"]["hold_reason"],
        )
        self.assertEqual(
            WAVE8_WALES_HOLDS["hced-Beandun614-1"]["known_side_entity_ids"],
            ["clio_gb_anglo_saxon_1_534_747d30b5"],
        )
        self.assertEqual(
            WAVE8_WALES_HOLDS["hced-Penselwood658-1"][
                "known_side_entity_ids"
            ],
            ["clio_gb_anglo_saxon_1_534_747d30b5"],
        )


if __name__ == "__main__":
    unittest.main()
