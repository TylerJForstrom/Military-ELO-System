import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.common import normalize_label
from military_elo.promotion.hced_location import (
    HCED_COUNTRY_QUARANTINE_IDS,
    HCED_POINT_QUARANTINE_IDS,
)
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_nez_perce import (
    WAVE8_NEZ_PERCE_CONTRACT_IDS,
    WAVE8_NEZ_PERCE_CONTRACTS,
    WAVE8_NEZ_PERCE_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_NEZ_PERCE_CROSS_LANE_DISPOSITIONS,
    WAVE8_NEZ_PERCE_ENTITIES,
    WAVE8_NEZ_PERCE_EXCLUSION_IDS,
    WAVE8_NEZ_PERCE_EXCLUSIONS,
    WAVE8_NEZ_PERCE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_NEZ_PERCE_EXPECTED_CANDIDATE_IDS,
    WAVE8_NEZ_PERCE_FINAL_AUDIT_SIGNATURE,
    WAVE8_NEZ_PERCE_HOLD_IDS,
    WAVE8_NEZ_PERCE_HOLDS,
    WAVE8_NEZ_PERCE_INTEGRATION_DISPOSITIONS,
    WAVE8_NEZ_PERCE_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_NEZ_PERCE_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_REASONS,
    WAVE8_NEZ_PERCE_NONPROMOTIONS,
    WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES,
    WAVE8_NEZ_PERCE_POINT_QUARANTINE_ADDITIONS,
    WAVE8_NEZ_PERCE_RESERVED_IDS,
    WAVE8_NEZ_PERCE_SOURCES,
    WAVE8_NEZ_PERCE_TERMINAL_EXCLUSION_IDS,
    WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS,
    install_wave8_nez_perce_entities,
    install_wave8_nez_perce_sources,
    promote_wave8_nez_perce_contracts,
    validate_wave8_nez_perce_integration_dispositions,
    validate_wave8_nez_perce_queue_contracts,
    wave8_nez_perce_audit_signature,
    wave8_nez_perce_cohort_counts,
    wave8_nez_perce_counts,
    wave8_nez_perce_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_nez_perce_"
UNITED_STATES_ID = "united_states"
WHITE_BIRD_FORCE_ID = "white_bird_non_treaty_nimiipuu_fighting_force_1877"
CAMPAIGN_FORCE_ID = "non_treaty_nimiipuu_allied_campaign_force_1877"


EXPECTED_RAW_LABELS = {
    "hced-Bear Paw Mountains1877-1": (
        "United States",
        "Nez Perce Indians",
        "United States",
        "Nez Perce Indians",
        1877,
    ),
    "hced-Big Hole River1877-1": (
        "United States",
        "Nez Perce Indians",
        "United States",
        "Nez Perce Indians",
        1877,
    ),
    "hced-Canyon Creek1877-1": (
        "Nez Perce Indians",
        "United States",
        "Nez Perce Indians",
        "United States",
        1877,
    ),
    "hced-Clearwater1877-1": (
        "Nez Perce Indians",
        "United States",
        "Nez Perce Indians",
        "United States",
        1877,
    ),
    "hced-White Bird Canyon1877-1": (
        "Nez Perce Indians",
        "United States",
        "Nez Perce Indians",
        "United States",
        1877,
    ),
}


EXPECTED_PROMOTIONS = {
    "hced-Bear Paw Mountains1877-1": {
        "name": "Battle of Bear Paw",
        "date_precision": "day_range",
        "granularity": "battle_and_siege",
        "winner": {UNITED_STATES_ID},
        "loser": {CAMPAIGN_FORCE_ID},
        "override": False,
    },
    "hced-Big Hole River1877-1": {
        "name": "Battle of the Big Hole",
        "date_precision": "day_range",
        "granularity": "engagement",
        "winner": {CAMPAIGN_FORCE_ID},
        "loser": {UNITED_STATES_ID},
        "override": True,
    },
    "hced-Canyon Creek1877-1": {
        "name": "Battle of Canyon Creek",
        "date_precision": "day",
        "granularity": "engagement",
        "winner": {CAMPAIGN_FORCE_ID},
        "loser": {UNITED_STATES_ID},
        "override": False,
    },
    "hced-Clearwater1877-1": {
        "name": "Battle of the Clearwater",
        "date_precision": "day_range",
        "granularity": "engagement",
        "winner": {UNITED_STATES_ID},
        "loser": {CAMPAIGN_FORCE_ID},
        "override": True,
    },
    "hced-White Bird Canyon1877-1": {
        "name": "Battle of White Bird Canyon",
        "date_precision": "day",
        "granularity": "engagement",
        "winner": {WHITE_BIRD_FORCE_ID},
        "loser": {UNITED_STATES_ID},
        "override": False,
    },
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


def _sole_blocker_rows(value, label: str) -> list[dict]:
    rows: list[dict] = []

    def visit(item) -> None:
        if isinstance(item, dict):
            if item.get("sole_blocker_label") == label:
                rows.append(item)
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(value)
    return rows


class Wave8NezPerceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.lane_rows = {
            str(row["candidate_id"]): row
            for row in cls.hced_rows
            if row.get("candidate_id") in WAVE8_NEZ_PERCE_RESERVED_IDS
        }

    def _installed(self):
        new_entity_ids = {str(entity["id"]) for entity in WAVE8_NEZ_PERCE_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        install_wave8_nez_perce_entities(entities)

        new_source_ids = {str(source["id"]) for source in WAVE8_NEZ_PERCE_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        install_wave8_nez_perce_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_NEZ_PERCE_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return promote_wave8_nez_perce_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_signature_inventory_counts_and_cohort_are_exact(self) -> None:
        payload = {
            "contracts": WAVE8_NEZ_PERCE_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_NEZ_PERCE_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_NEZ_PERCE_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_NEZ_PERCE_ENTITIES,
            "existing_release_duplicate_dispositions": (
                WAVE8_NEZ_PERCE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                WAVE8_NEZ_PERCE_EXPECTED_CANDIDATE_IDS
            ),
            "holds": WAVE8_NEZ_PERCE_HOLDS,
            "integration_dispositions": WAVE8_NEZ_PERCE_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": (
                WAVE8_NEZ_PERCE_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": WAVE8_NEZ_PERCE_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": (
                WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_REASONS
            ),
            "outcome_overrides": WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_NEZ_PERCE_POINT_QUARANTINE_ADDITIONS
            ),
            "sources": WAVE8_NEZ_PERCE_SOURCES,
            "terminal_exclusions": WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS,
        }
        independent = hashlib.sha256(
            _canonical_json(payload).encode("utf-8")
        ).hexdigest()
        self.assertEqual(independent, WAVE8_NEZ_PERCE_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(wave8_nez_perce_audit_signature(), independent)
        self.assertEqual(WAVE8_NEZ_PERCE_CONTRACT_IDS, set(EXPECTED_PROMOTIONS))
        self.assertEqual(WAVE8_NEZ_PERCE_HOLDS, {})
        self.assertEqual(WAVE8_NEZ_PERCE_HOLD_IDS, frozenset())
        self.assertEqual(WAVE8_NEZ_PERCE_TERMINAL_EXCLUSIONS, {})
        self.assertEqual(WAVE8_NEZ_PERCE_TERMINAL_EXCLUSION_IDS, frozenset())
        self.assertEqual(WAVE8_NEZ_PERCE_EXCLUSIONS, {})
        self.assertEqual(WAVE8_NEZ_PERCE_EXCLUSION_IDS, frozenset())
        self.assertEqual(WAVE8_NEZ_PERCE_NONPROMOTIONS, {})
        self.assertEqual(
            WAVE8_NEZ_PERCE_RESERVED_IDS,
            WAVE8_NEZ_PERCE_EXPECTED_CANDIDATE_IDS,
        )
        self.assertEqual(
            wave8_nez_perce_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "new_entities": 2,
                "new_sources": 10,
                "newly_rated_events": 5,
                "outcome_overrides": 2,
                "point_quarantine_additions": 4,
                "promotion_contracts": 5,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(wave8_nez_perce_cohort_counts(), {"nez_perce_war_1877": 5})

    def test_funnel_and_queue_own_all_and_only_five_exact_rows(self) -> None:
        funnel_rows = _sole_blocker_rows(self.funnel, "nez perce indians")
        self.assertEqual(len(funnel_rows), 5)
        self.assertEqual(
            {str(row["candidate_id"]) for row in funnel_rows},
            WAVE8_NEZ_PERCE_EXPECTED_CANDIDATE_IDS,
        )
        self.assertTrue(all(row["greedy_eligible"] for row in funnel_rows))
        self.assertTrue(all(row["other_blockers"] == [] for row in funnel_rows))
        self.assertTrue(
            all(row["resolved_counterpart_entity_ids"] == [UNITED_STATES_ID] for row in funnel_rows)
        )

        exact_rows = {
            str(row["candidate_id"]): row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "nez perce indians"
            or normalize_label(row.get("side_2_raw")) == "nez perce indians"
        }
        self.assertEqual(set(exact_rows), set(EXPECTED_RAW_LABELS))
        self.assertEqual(
            validate_wave8_nez_perce_queue_contracts(self.hced_rows),
            {
                "promotion_contracts": 5,
                "holds": 0,
                "reviewed_hced_rows": 5,
                "terminal_exclusions": 0,
            },
        )
        for candidate_id, expected in EXPECTED_RAW_LABELS.items():
            row = exact_rows[candidate_id]
            self.assertEqual(
                (
                    row["side_1_raw"],
                    row["side_2_raw"],
                    row["winner_raw"],
                    row["loser_raw"],
                    row["year_best"],
                ),
                expected,
            )
            self.assertEqual(
                canonical_hced_row_sha256(row),
                WAVE8_NEZ_PERCE_CONTRACTS[candidate_id]["raw_row_sha256"],
            )

        future = copy.deepcopy(self.hced_rows)
        future.append(
            {
                "candidate_id": "hced-Future Nez Perce1878-1",
                "name": "Future Nez Perce",
                "side_1_raw": "Nez Perce Indians",
                "side_2_raw": "United States",
                "year_best": 1878,
            }
        )
        with self.assertRaisesRegex(ValueError, "exact Nez Perce Indians inventory changed"):
            validate_wave8_nez_perce_queue_contracts(future)

    def test_every_exact_row_hash_is_pinned_and_tamper_fails_closed(self) -> None:
        self.assertEqual(set(self.lane_rows), WAVE8_NEZ_PERCE_RESERVED_IDS)
        for candidate_id in sorted(WAVE8_NEZ_PERCE_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(
                    canonical_hced_row_sha256(self.lane_rows[candidate_id]),
                    WAVE8_NEZ_PERCE_CONTRACTS[candidate_id]["raw_row_sha256"],
                )
                tampered = copy.deepcopy(self.hced_rows)
                row = next(
                    row for row in tampered if row.get("candidate_id") == candidate_id
                )
                row["name"] = str(row["name"]) + " changed"
                with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
                    validate_wave8_nez_perce_queue_contracts(tampered)

        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Bear Paw Mountains1877-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_nez_perce_queue_contracts(missing)

    def test_sources_and_bounded_entities_parse_install_and_do_not_generalize(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_NEZ_PERCE_SOURCES
        }
        self.assertEqual(len(source_by_id), 10)
        for source in WAVE8_NEZ_PERCE_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
        self.assertEqual(
            {
                source["source_family_id"]
                for source in WAVE8_NEZ_PERCE_SOURCES
                if "outcome" in source["evidence_roles"]
            },
            {
                "army_heritage_nez_perce_war_1877",
                "collins_army_white_bird_staff_ride",
                "greene_nez_perce_summer_1877",
                "nps_nez_perce_battlefield_interpretation",
                "scott_big_hole_battlefield_archaeology",
            },
        )

        entity_by_id = {
            str(entity["id"]): entity for entity in WAVE8_NEZ_PERCE_ENTITIES
        }
        self.assertEqual(set(entity_by_id), {WHITE_BIRD_FORCE_ID, CAMPAIGN_FORCE_ID})
        for entity in WAVE8_NEZ_PERCE_ENTITIES:
            Entity.from_dict(entity)
            self.assertEqual((entity["start_year"], entity["end_year"]), (1877, 1877))
            self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
            self.assertNotIn(
                normalize_label(entity["name"]),
                {"nez perce", "nez perce indian", "nez perce indians", "nimiipuu"},
            )
            note = entity["continuity_note"].casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("noncombatants", note)
            self.assertIn("modern tribal government", note)
            self.assertTrue(set(entity["source_ids"]) <= set(source_by_id))

        self.assertIn("looking glass", entity_by_id[CAMPAIGN_FORCE_ID]["continuity_note"].casefold())
        self.assertIn("palouse", entity_by_id[CAMPAIGN_FORCE_ID]["continuity_note"].casefold())
        self.assertIn("cayuse", entity_by_id[CAMPAIGN_FORCE_ID]["continuity_note"].casefold())

        entities, sources, _ = self._installed()
        self.assertIn(UNITED_STATES_ID, entities)
        self.assertTrue(set(entity_by_id) <= set(entities))
        self.assertTrue(set(source_by_id) <= set(sources))

    def test_contract_dates_actors_outcomes_and_source_families_are_exact(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_NEZ_PERCE_SOURCES
        }
        events = self._events()
        by_candidate = {str(event["hced_candidate_id"]): event for event in events}
        self.assertEqual(set(by_candidate), set(EXPECTED_PROMOTIONS))
        self.assertEqual(len(events), 5)

        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            contract = WAVE8_NEZ_PERCE_CONTRACTS[candidate_id]
            canonical = contract["canonical_event"]
            self.assertEqual(canonical["name"], expected["name"])
            self.assertEqual(canonical["date_precision"], expected["date_precision"])
            self.assertEqual(canonical["granularity"], expected["granularity"])
            self.assertEqual((canonical["year_low"], canonical["year_high"]), (1877, 1877))
            self.assertEqual(
                canonical["canonical_key"],
                by_candidate[candidate_id]["canonical_event_key"],
            )
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(
                contract["source_outcome_override"],
                expected["override"],
            )
            self.assertTrue(contract["actor_override"])
            self.assertEqual(
                contract["duplicate_ownership"],
                {
                    "owner_module": "wave8_nez_perce",
                    "status": "canonical_hced_owner",
                },
            )
            outcomes = contract["outcome_source_ids"]
            families = contract["outcome_source_family_ids"]
            self.assertGreaterEqual(len(outcomes), 2)
            self.assertGreaterEqual(len(families), 2)
            self.assertEqual(
                families,
                sorted({source_by_id[source_id]["source_family_id"] for source_id in outcomes}),
            )
            self.assertTrue(set(outcomes) <= set(contract["evidence_refs"]))
            self.assertTrue(
                all("outcome" in source_by_id[source_id]["evidence_roles"] for source_id in outcomes)
            )

            event = by_candidate[candidate_id]
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["name"], expected["name"])
            self.assertEqual((event["year"], event["end_year"]), (1877, 1877))
            self.assertEqual(event["date_precision"], expected["date_precision"])
            self.assertEqual(event["reviewed_granularity"], expected["granularity"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["war_type"], "colonial_anti_colonial")
            self.assertIn("hced_dataset", event["source_ids"])
            self.assertEqual(
                event["outcome_source_ids"],
                contract["outcome_source_ids"],
            )
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            winners = {
                item["entity_id"]
                for item in event["participants"]
                if item["termination"] == "engagement_victory"
            }
            losers = {
                item["entity_id"]
                for item in event["participants"]
                if item["termination"] == "engagement_defeat"
            }
            self.assertEqual(winners, expected["winner"])
            self.assertEqual(losers, expected["loser"])
            self.assertEqual(
                {item["termination"] for item in event["participants"]},
                {"engagement_victory", "engagement_defeat"},
            )
            self.assertNotIn("inconclusive_engagement", {item["termination"] for item in event["participants"]})

        self.assertEqual(
            len({event["canonical_event_key"] for event in events}),
            5,
        )

    def test_big_hole_and_clearwater_reversals_are_explicit_and_sourced(self) -> None:
        expected = {
            "hced-Big Hole River1877-1": {
                "raw_winner": "United States",
                "raw_loser": "Nez Perce Indians",
                "winner": [CAMPAIGN_FORCE_ID],
                "loser": [UNITED_STATES_ID],
            },
            "hced-Clearwater1877-1": {
                "raw_winner": "Nez Perce Indians",
                "raw_loser": "United States",
                "winner": [UNITED_STATES_ID],
                "loser": [CAMPAIGN_FORCE_ID],
            },
        }
        self.assertEqual(set(WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES), set(expected))
        for candidate_id, values in expected.items():
            raw = self.lane_rows[candidate_id]
            contract = WAVE8_NEZ_PERCE_CONTRACTS[candidate_id]
            override = WAVE8_NEZ_PERCE_OUTCOME_OVERRIDES[candidate_id]
            self.assertEqual(raw["winner_raw"], values["raw_winner"])
            self.assertEqual(raw["loser_raw"], values["raw_loser"])
            self.assertTrue(raw["winner_loser_complete"])
            self.assertTrue(contract["source_outcome_override"])
            self.assertTrue(contract["outcome_reversal"])
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(override["raw_winner_raw"], values["raw_winner"])
            self.assertEqual(override["raw_loser_raw"], values["raw_loser"])
            self.assertEqual(override["corrected_winner_side"], contract["winner_side"])
            self.assertEqual(override["corrected_winner_entity_ids"], values["winner"])
            self.assertEqual(override["corrected_loser_entity_ids"], values["loser"])
            self.assertEqual(override["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                override["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)

        for candidate_id in WAVE8_NEZ_PERCE_CONTRACT_IDS - set(expected):
            contract = WAVE8_NEZ_PERCE_CONTRACTS[candidate_id]
            self.assertFalse(contract["source_outcome_override"])
            self.assertFalse(contract["outcome_reversal"])

        event_by_candidate = {
            event["hced_candidate_id"]: event for event in self._events()
        }
        big_hole_ids = {
            participant["entity_id"]
            for participant in event_by_candidate["hced-Big Hole River1877-1"]["participants"]
        }
        self.assertEqual(big_hole_ids, {UNITED_STATES_ID, CAMPAIGN_FORCE_ID})
        self.assertNotIn("Nez Perce Indians", big_hole_ids)
        self.assertIn(
            "does not turn the mixed campaign consequence into a draw",
            WAVE8_NEZ_PERCE_CONTRACTS["hced-Clearwater1877-1"]["audit_note"],
        )

    def test_white_bird_and_joined_campaign_identities_never_bridge_people_or_families(self) -> None:
        white = WAVE8_NEZ_PERCE_CONTRACTS["hced-White Bird Canyon1877-1"]
        self.assertEqual(white["side_1_entity_ids"], [WHITE_BIRD_FORCE_ID])
        later_ids = WAVE8_NEZ_PERCE_CONTRACT_IDS - {"hced-White Bird Canyon1877-1"}
        for candidate_id in later_ids:
            sides = {
                *WAVE8_NEZ_PERCE_CONTRACTS[candidate_id]["side_1_entity_ids"],
                *WAVE8_NEZ_PERCE_CONTRACTS[candidate_id]["side_2_entity_ids"],
            }
            self.assertIn(CAMPAIGN_FORCE_ID, sides)
            self.assertNotIn(WHITE_BIRD_FORCE_ID, sides)

        participant_ids = [
            participant["entity_id"]
            for event in self._events()
            for participant in event["participants"]
        ]
        self.assertEqual(participant_ids.count(WHITE_BIRD_FORCE_ID), 1)
        self.assertEqual(participant_ids.count(CAMPAIGN_FORCE_ID), 4)
        self.assertEqual(participant_ids.count(UNITED_STATES_ID), 5)
        self.assertNotIn("nez_perce", participant_ids)
        self.assertNotIn("nez_perce_indians", participant_ids)

        names = {normalize_label(entity["name"]) for entity in WAVE8_NEZ_PERCE_ENTITIES}
        self.assertTrue(
            names.isdisjoint(
                {"nez perce", "nez perce indian", "nez perce indians", "nimiipuu"}
            )
        )
        self.assertTrue(
            all(contract["result_type"] == "win" for contract in WAVE8_NEZ_PERCE_CONTRACTS.values())
        )
        self.assertFalse(
            any(contract["result_type"] == "draw" for contract in WAVE8_NEZ_PERCE_CONTRACTS.values())
        )

    def test_location_audit_is_promoted_only_point_quarantine_and_keeps_big_hole(self) -> None:
        before_points_object = HCED_POINT_QUARANTINE_IDS
        before_countries_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        expected_points = {
            "hced-Bear Paw Mountains1877-1",
            "hced-Canyon Creek1877-1",
            "hced-Clearwater1877-1",
            "hced-White Bird Canyon1877-1",
        }

        self.assertEqual(WAVE8_NEZ_PERCE_POINT_QUARANTINE_ADDITIONS, expected_points)
        self.assertEqual(WAVE8_NEZ_PERCE_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertTrue(expected_points <= WAVE8_NEZ_PERCE_CONTRACT_IDS)
        self.assertEqual(set(WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_REASONS), expected_points)
        self.assertEqual(
            WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_ADDITIONS,
            {"point": expected_points, "country": frozenset()},
        )
        self.assertEqual(
            wave8_nez_perce_location_quarantine_additions(),
            {"country": frozenset(), "point": expected_points},
        )

        by_candidate = {
            event["hced_candidate_id"]: event for event in self._events()
        }
        for candidate_id, event in by_candidate.items():
            self.assertEqual(event["modern_location_country"], "United States")
            self.assertIn("location_provenance", event)
            if candidate_id in expected_points:
                self.assertNotIn("geometry", event)
            else:
                self.assertEqual(candidate_id, "hced-Big Hole River1877-1")
                self.assertEqual(
                    event["geometry"],
                    {"type": "Point", "coordinates": [-113.6560106, 45.6450983]},
                )

        canyon_reason = WAVE8_NEZ_PERCE_LOCATION_QUARANTINE_REASONS[
            "hced-Canyon Creek1877-1"
        ]
        self.assertIn("280 kilometres", canyon_reason["reason"])
        self.assertEqual(
            canyon_reason["reference_source_id"],
            "wave8_nez_perce_nps_canyon_creek",
        )

        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_points_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_countries_object)
        self.assertEqual(HCED_POINT_QUARANTINE_IDS, before_points)
        self.assertEqual(HCED_COUNTRY_QUARANTINE_IDS, before_countries)

    def test_zero_duplicate_audit_and_future_twins_fail_closed(self) -> None:
        self.assertEqual(WAVE8_NEZ_PERCE_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_NEZ_PERCE_CROSS_LANE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_NEZ_PERCE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_NEZ_PERCE_INTEGRATION_DISPOSITIONS, {})
        self.assertEqual(
            set(WAVE8_NEZ_PERCE_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_NEZ_PERCE_RESERVED_IDS,
        )
        self.assertEqual(
            validate_wave8_nez_perce_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                self.release_events,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 0,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
            },
        )

        hced_twin = copy.deepcopy(self.hced_rows)
        hced_twin.append(
            {
                "candidate_id": "hced-future-big-hole-1877",
                "name": "Battle of the Big Hole",
                "year_best": 1877,
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_nez_perce_integration_dispositions(
                hced_twin,
                self.iwbd_rows,
            )

        iwbd_twin = copy.deepcopy(self.iwbd_rows)
        iwbd_twin.append(
            {
                "candidate_id": "iwbd-future-whitebird",
                "name": "Whitebird Canyon",
                "start_date": "1877-06-17",
                "end_date": "1877-06-17",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            validate_wave8_nez_perce_integration_dispositions(
                self.hced_rows,
                iwbd_twin,
            )

        release_twin = [
            *self.release_events,
            {"id": "future-bear-paw-twin", "name": "Bear Paw Mountains", "year": 1877},
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_nez_perce_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release_twin,
            )

    def test_entity_window_duplicate_event_and_installer_collisions_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        short = copy.deepcopy(entities)
        short[CAMPAIGN_FORCE_ID]["start_year"] = 1878
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_nez_perce_contracts(self.hced_rows, short, existing)

        events = promote_wave8_nez_perce_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_nez_perce_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )

        collision = [
            *existing,
            {"name": "Battle of Canyon Creek", "year": 1877},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_nez_perce_contracts(
                self.hced_rows,
                entities,
                collision,
            )

        installed_entities: dict[str, dict] = {}
        installed_sources: dict[str, dict] = {}
        install_wave8_nez_perce_entities(installed_entities)
        install_wave8_nez_perce_sources(installed_sources)
        installed_entities[WHITE_BIRD_FORCE_ID]["name"] = "tampered"
        installed_sources["wave8_nez_perce_nps_white_bird"]["title"] = "tampered"
        self.assertNotEqual(
            installed_entities[WHITE_BIRD_FORCE_ID]["name"],
            next(
                entity["name"]
                for entity in WAVE8_NEZ_PERCE_ENTITIES
                if entity["id"] == WHITE_BIRD_FORCE_ID
            ),
        )
        self.assertNotEqual(
            installed_sources["wave8_nez_perce_nps_white_bird"]["title"],
            next(
                source["title"]
                for source in WAVE8_NEZ_PERCE_SOURCES
                if source["id"] == "wave8_nez_perce_nps_white_bird"
            ),
        )
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_nez_perce_entities(installed_entities)
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_nez_perce_sources(installed_sources)


if __name__ == "__main__":
    unittest.main()
