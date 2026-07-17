import copy
import hashlib
import json
import unittest
from pathlib import Path

from military_elo.models import Entity, Event, Source
from military_elo.promotion.common import normalize_label
from military_elo.promotion.wave7_global import canonical_hced_row_sha256
from military_elo.promotion.wave8_cherokee import WAVE8_CHEROKEE_RESERVED_IDS
from military_elo.promotion.wave8_kickapoo import (
    WAVE8_KICKAPOO_CONTRACT_IDS,
    WAVE8_KICKAPOO_CONTRACTS,
    WAVE8_KICKAPOO_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS,
    WAVE8_KICKAPOO_ENTITIES,
    WAVE8_KICKAPOO_EXCLUSION_IDS,
    WAVE8_KICKAPOO_EXCLUSIONS,
    WAVE8_KICKAPOO_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_KICKAPOO_EXPECTED_CANDIDATE_IDS,
    WAVE8_KICKAPOO_FINAL_AUDIT_SIGNATURE,
    WAVE8_KICKAPOO_HCED_QUEUE_SHA256,
    WAVE8_KICKAPOO_HOLD_IDS,
    WAVE8_KICKAPOO_HOLDS,
    WAVE8_KICKAPOO_INTEGRATION_DISPOSITIONS,
    WAVE8_KICKAPOO_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_KICKAPOO_IWBD_QUEUE_SHA256,
    WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_KICKAPOO_LOCATION_QUARANTINE_ADDITIONS,
    WAVE8_KICKAPOO_LOCATION_QUARANTINE_REASONS,
    WAVE8_KICKAPOO_NONPROMOTIONS,
    WAVE8_KICKAPOO_OUTCOME_OVERRIDES,
    WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS,
    WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS,
    WAVE8_KICKAPOO_RESERVED_IDS,
    WAVE8_KICKAPOO_ROW_HASHES,
    WAVE8_KICKAPOO_SOURCES,
    WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS,
    WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS,
    install_wave8_kickapoo_entities,
    install_wave8_kickapoo_sources,
    promote_wave8_kickapoo_contracts,
    validate_wave8_kickapoo_integration_dispositions,
    validate_wave8_kickapoo_queue_contracts,
    wave8_kickapoo_audit_signature,
    wave8_kickapoo_cohort_counts,
    wave8_kickapoo_counts,
    wave8_kickapoo_location_quarantine_additions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_kickapoo_"

BATTLE_CREEK_WAR_PARTY_ID = "battle_creek_allied_indigenous_war_party_1838"
BATTLE_CREEK_SURVEY_PARTY_ID = "battle_creek_armed_surveying_party_1838"
KICKAPOO_TOWN_ALLIED_FORCE_ID = (
    "kickapoo_town_allied_indigenous_mexican_fighting_force_1838"
)
RUSK_MILITIA_COLUMN_ID = "rusk_texas_militia_column_kickapoo_town_1838"
LITTLE_CONCHO_DEFENDERS_ID = "machemanet_kickapoo_camp_defenders_1862"
LITTLE_CONCHO_PATROL_ID = "confederate_cavalry_patrol_little_concho_1862"
DOVE_CREEK_DEFENDERS_ID = "dove_creek_kickapoo_camp_defenders_1865"
DOVE_CREEK_ASSAULT_FORCE_ID = (
    "dove_creek_confederate_texas_militia_assault_force_1865"
)


EXPECTED_RAW_ROWS = {
    "hced-Battle Creek, Texas1838-1": {
        "side_1_raw": "Kickapoo Indians",
        "side_2_raw": "Texas",
        "winner_raw": "Kickapoo Indians",
        "loser_raw": "Texas",
        "year": 1838,
        "complete": True,
        "massacre": "No",
    },
    "hced-Dove Creek1865-1": {
        "side_1_raw": "Kickapoo Indians",
        "side_2_raw": "Confederate States of America",
        "winner_raw": "Kickapoo Indians",
        "loser_raw": "Confederate States of America",
        "year": 1865,
        "complete": True,
        "massacre": "No",
    },
    "hced-Kickapoo Town1838-1": {
        "side_1_raw": "Texas",
        "side_2_raw": "Kickapoo Indians",
        "winner_raw": "Texas",
        "loser_raw": "Kickapoo Indians",
        "year": 1838,
        "complete": True,
        "massacre": "No",
    },
    "hced-Killough Massacre1838-1": {
        "side_1_raw": "United States",
        "side_2_raw": "Kickapoo Indians",
        "winner_raw": "Massacre",
        "loser_raw": None,
        "year": 1838,
        "complete": False,
        "massacre": "Yes",
    },
    "hced-Little Concho1862-1": {
        "side_1_raw": "Kickapoo Indians",
        "side_2_raw": "Confederate States of America",
        "winner_raw": "Kickapoo Indians",
        "loser_raw": "Confederate States of America",
        "year": 1862,
        "complete": True,
        "massacre": "No",
    },
    "hced-Wichita Agency1862-1": {
        "side_1_raw": "Kickapoo Indians",
        "side_2_raw": "Confederate States of America, Tonkawa Indians",
        "winner_raw": "Kickapoo Indians",
        "loser_raw": "Confederate States of America, Tonkawa Indians",
        "year": 1862,
        "complete": True,
        "massacre": "Yes",
    },
}


EXPECTED_PROMOTIONS = {
    "hced-Battle Creek, Texas1838-1": {
        "name": "Battle Creek Fight",
        "year": 1838,
        "date_precision": "day",
        "date_text": "8 October 1838",
        "winner": {BATTLE_CREEK_WAR_PARTY_ID},
        "loser": {BATTLE_CREEK_SURVEY_PARTY_ID},
    },
    "hced-Dove Creek1865-1": {
        "name": "Battle of Dove Creek",
        "year": 1865,
        "date_precision": "day",
        "date_text": "8 January 1865",
        "winner": {DOVE_CREEK_DEFENDERS_ID},
        "loser": {DOVE_CREEK_ASSAULT_FORCE_ID},
    },
    "hced-Kickapoo Town1838-1": {
        "name": "Battle of Kickapoo Town",
        "year": 1838,
        "date_precision": "day",
        "date_text": "16 October 1838",
        "winner": {RUSK_MILITIA_COLUMN_ID},
        "loser": {KICKAPOO_TOWN_ALLIED_FORCE_ID},
    },
    "hced-Little Concho1862-1": {
        "name": "Little Concho engagement",
        "year": 1862,
        "date_precision": "month",
        "date_text": "December 1862",
        "winner": {LITTLE_CONCHO_DEFENDERS_ID},
        "loser": {LITTLE_CONCHO_PATROL_ID},
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


def _funnel_rows(value) -> list[dict]:
    rows: list[dict] = []

    def visit(item) -> None:
        if isinstance(item, dict):
            if "candidate_id" in item and "blocker_labels" in item:
                rows.append(item)
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(value)
    return rows


class Wave8KickapooTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_path = ROOT / "data" / "review" / "hced-candidates.jsonl"
        cls.iwbd_path = ROOT / "data" / "review" / "iwbd-candidates.jsonl"
        cls.hced_rows = _jsonl(cls.hced_path)
        cls.iwbd_rows = _jsonl(cls.iwbd_path)
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")
        cls.lane_rows = {
            str(row["candidate_id"]): row
            for row in cls.hced_rows
            if row.get("candidate_id") in WAVE8_KICKAPOO_RESERVED_IDS
        }

    def _installed(self):
        new_entity_ids = {str(entity["id"]) for entity in WAVE8_KICKAPOO_ENTITIES}
        entities = {
            str(entity["id"]): entity
            for entity in self.release_entities
            if str(entity["id"]) not in new_entity_ids
        }
        install_wave8_kickapoo_entities(entities)

        new_source_ids = {str(source["id"]) for source in WAVE8_KICKAPOO_SOURCES}
        sources = {
            str(source["id"]): source
            for source in self.release_sources
            if str(source["id"]) not in new_source_ids
        }
        install_wave8_kickapoo_sources(sources)

        existing = [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in WAVE8_KICKAPOO_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _events(self):
        entities, _, existing = self._installed()
        return promote_wave8_kickapoo_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def test_locked_queue_file_hashes_are_exact(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            WAVE8_KICKAPOO_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            WAVE8_KICKAPOO_IWBD_QUEUE_SHA256,
        )

    def test_current_exact_label_inventory_is_six_rows(self) -> None:
        exact_ids = {
            str(row.get("candidate_id"))
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "kickapoo indians"
            or normalize_label(row.get("side_2_raw")) == "kickapoo indians"
        }
        self.assertEqual(exact_ids, set(EXPECTED_RAW_ROWS))
        self.assertEqual(exact_ids, WAVE8_KICKAPOO_EXPECTED_CANDIDATE_IDS)
        self.assertEqual(len(exact_ids), 6)

    def test_stale_funnel_has_four_sole_blockers_not_the_exact_inventory(self) -> None:
        rows = _funnel_rows(self.funnel)
        sole = {
            str(row["candidate_id"])
            for row in rows
            if row.get("sole_blocker_label") == "kickapoo indians"
        }
        self.assertEqual(
            sole,
            {
                "hced-Battle Creek, Texas1838-1",
                "hced-Dove Creek1865-1",
                "hced-Kickapoo Town1838-1",
                "hced-Little Concho1862-1",
            },
        )
        self.assertNotIn("hced-Killough Massacre1838-1", sole)
        self.assertNotIn("hced-Wichita Agency1862-1", sole)
        self.assertEqual(len(WAVE8_KICKAPOO_EXPECTED_CANDIDATE_IDS), 6)

    def test_every_raw_row_field_and_fingerprint_is_pinned(self) -> None:
        self.assertEqual(set(self.lane_rows), set(EXPECTED_RAW_ROWS))
        self.assertEqual(set(WAVE8_KICKAPOO_ROW_HASHES), set(EXPECTED_RAW_ROWS))
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            row = self.lane_rows[candidate_id]
            self.assertEqual(row["side_1_raw"], expected["side_1_raw"])
            self.assertEqual(row["side_2_raw"], expected["side_2_raw"])
            self.assertEqual(row["winner_raw"], expected["winner_raw"])
            self.assertEqual(row["loser_raw"], expected["loser_raw"])
            self.assertEqual(row["year_low"], expected["year"])
            self.assertEqual(row["year_high"], expected["year"])
            self.assertEqual(row["winner_loser_complete"], expected["complete"])
            self.assertEqual(row["massacre_raw"], expected["massacre"])
            self.assertEqual(
                canonical_hced_row_sha256(row),
                WAVE8_KICKAPOO_ROW_HASHES[candidate_id],
            )

    def test_disposition_partitions_are_complete_and_disjoint(self) -> None:
        self.assertEqual(len(WAVE8_KICKAPOO_CONTRACT_IDS), 4)
        self.assertEqual(WAVE8_KICKAPOO_HOLD_IDS, frozenset())
        self.assertEqual(
            WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS,
            {
                "hced-Killough Massacre1838-1",
                "hced-Wichita Agency1862-1",
            },
        )
        self.assertEqual(
            WAVE8_KICKAPOO_EXCLUSION_IDS,
            WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS,
        )
        self.assertIs(WAVE8_KICKAPOO_EXCLUSIONS, WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS)
        self.assertEqual(
            set(WAVE8_KICKAPOO_NONPROMOTIONS),
            WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS,
        )
        self.assertEqual(
            WAVE8_KICKAPOO_RESERVED_IDS,
            WAVE8_KICKAPOO_EXPECTED_CANDIDATE_IDS,
        )
        self.assertFalse(WAVE8_KICKAPOO_CONTRACT_IDS & WAVE8_KICKAPOO_EXCLUSION_IDS)

    def test_complete_audit_signature_is_independently_reproducible(self) -> None:
        payload = {
            "contracts": WAVE8_KICKAPOO_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_KICKAPOO_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_KICKAPOO_ENTITIES,
            "existing_release_duplicate_dispositions": (
                WAVE8_KICKAPOO_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                WAVE8_KICKAPOO_EXPECTED_CANDIDATE_IDS
            ),
            "hced_queue_sha256": WAVE8_KICKAPOO_HCED_QUEUE_SHA256,
            "holds": WAVE8_KICKAPOO_HOLDS,
            "integration_dispositions": WAVE8_KICKAPOO_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": (
                WAVE8_KICKAPOO_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_queue_sha256": WAVE8_KICKAPOO_IWBD_QUEUE_SHA256,
            "iwbd_zero_overlap_audit": WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": (
                WAVE8_KICKAPOO_LOCATION_QUARANTINE_REASONS
            ),
            "outcome_overrides": WAVE8_KICKAPOO_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS
            ),
            "related_hced_dispositions": (
                WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS
            ),
            "row_hashes": WAVE8_KICKAPOO_ROW_HASHES,
            "sources": WAVE8_KICKAPOO_SOURCES,
            "terminal_exclusions": WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS,
        }
        measured = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        self.assertEqual(measured, WAVE8_KICKAPOO_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(measured, wave8_kickapoo_audit_signature())
        self.assertEqual(len(measured), 64)

    def test_counts_and_campaign_cohorts_are_exact(self) -> None:
        self.assertEqual(
            wave8_kickapoo_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 1,
                "existing_release_duplicate_dispositions": 0,
                "holds": 0,
                "integration_dispositions": 5,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 6,
                "new_entities": 8,
                "new_sources": 17,
                "newly_rated_events": 4,
                "outcome_overrides": 0,
                "point_quarantine_additions": 4,
                "promotion_contracts": 4,
                "related_hced_dispositions": 4,
                "reviewed_hced_rows": 6,
                "terminal_exclusions": 2,
            },
        )
        self.assertEqual(
            wave8_kickapoo_cohort_counts(),
            {
                "kickapoo_migration_confederate_conflict_1862_1865": 2,
                "republic_of_texas_frontier_conflict_1838": 3,
                "wichita_agency_tonkawa_massacre_1862": 1,
            },
        )

    def test_sources_are_valid_authoritative_and_direct(self) -> None:
        ids = [str(source["id"]) for source in WAVE8_KICKAPOO_SOURCES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 17)
        types = {str(source["source_type"]) for source in WAVE8_KICKAPOO_SOURCES}
        publishers = {str(source["publisher"]) for source in WAVE8_KICKAPOO_SOURCES}
        for source in WAVE8_KICKAPOO_SOURCES:
            parsed = Source.from_dict(source)
            self.assertEqual(parsed.id, source["id"])
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(source["accessed"], "2026-07-16")
            self.assertEqual(
                list(source["evidence_roles"]),
                sorted(set(source["evidence_roles"])),
            )
        self.assertTrue(any("official_tribal" in value for value in types))
        self.assertTrue(any("government" in value or "federal" in value for value in types))
        self.assertTrue(any("scholarly" in value for value in types))
        self.assertTrue(any("primary" in value for value in types))
        self.assertIn("Kickapoo Traditional Tribe of Texas", publishers)
        self.assertIn("U.S. National Park Service", publishers)
        self.assertIn("Texas Historical Commission", publishers)

    def test_every_source_fixture_is_consumed_by_a_signed_decision(self) -> None:
        used: set[str] = set()
        for entity in WAVE8_KICKAPOO_ENTITIES:
            used.update(map(str, entity["source_ids"]))
        for contract in WAVE8_KICKAPOO_CONTRACTS.values():
            used.update(map(str, contract["evidence_refs"]))
        for item in WAVE8_KICKAPOO_NONPROMOTIONS.values():
            used.update(map(str, item["evidence_refs"]))
        for item in WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS.values():
            used.update(map(str, item["evidence_refs"]))
        for item in WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS.values():
            used.update(map(str, item["evidence_refs"]))
        self.assertEqual(used, {str(source["id"]) for source in WAVE8_KICKAPOO_SOURCES})

    def test_promoted_outcomes_have_independent_attested_source_families(self) -> None:
        source_by_id = {
            str(source["id"]): source for source in WAVE8_KICKAPOO_SOURCES
        }
        for contract in WAVE8_KICKAPOO_CONTRACTS.values():
            outcomes = list(contract["outcome_source_ids"])
            families = list(contract["outcome_source_family_ids"])
            self.assertGreaterEqual(len(outcomes), 2)
            self.assertEqual(outcomes, sorted(set(outcomes)))
            self.assertTrue(set(outcomes) <= set(contract["evidence_refs"]))
            self.assertTrue(
                all("outcome" in source_by_id[item]["evidence_roles"] for item in outcomes)
            )
            self.assertEqual(
                families,
                sorted({source_by_id[item]["source_family_id"] for item in outcomes}),
            )
            self.assertGreaterEqual(len(families), 2)

    def test_entities_are_event_bounded_and_have_no_rating_bridge(self) -> None:
        ids = [str(entity["id"]) for entity in WAVE8_KICKAPOO_ENTITIES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 8)
        forbidden = {
            "kickapoo",
            "kickapoo indians",
            "kickapoo traditional tribe of texas",
            "texas",
            "united states",
            "confederate states of america",
        }
        for fixture in WAVE8_KICKAPOO_ENTITIES:
            entity = Entity.from_dict(fixture)
            self.assertEqual(entity.start_year, entity.end_year)
            self.assertIn(entity.start_year, {1838, 1862, 1865})
            self.assertEqual(entity.aliases, ())
            self.assertEqual(entity.predecessors, ())
            self.assertNotIn(normalize_label(entity.name), forbidden)
            note = entity.continuity_note.casefold()
            self.assertIn("no rating is inherited", note)
            self.assertIn("ethnic label", note)
            self.assertIn("noncombatants", note)
            self.assertIn("modern tribal government", note)

    def test_every_promotion_uses_two_opposing_bounded_formations(self) -> None:
        entity_by_id = {
            str(entity["id"]): entity for entity in WAVE8_KICKAPOO_ENTITIES
        }
        consumed: set[str] = set()
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            contract = WAVE8_KICKAPOO_CONTRACTS[candidate_id]
            side_1 = set(contract["side_1_entity_ids"])
            side_2 = set(contract["side_2_entity_ids"])
            self.assertEqual(side_1, expected["winner"])
            self.assertEqual(side_2, expected["loser"])
            self.assertEqual(len(side_1), 1)
            self.assertEqual(len(side_2), 1)
            self.assertFalse(side_1 & side_2)
            self.assertTrue((side_1 | side_2) <= set(entity_by_id))
            for entity_id in side_1 | side_2:
                fixture = entity_by_id[entity_id]
                self.assertEqual(fixture["start_year"], expected["year"])
                self.assertEqual(fixture["end_year"], expected["year"])
            consumed.update(side_1 | side_2)
        self.assertEqual(consumed, set(entity_by_id))

    def test_contract_dates_names_and_granularity_are_exact(self) -> None:
        for candidate_id, expected in EXPECTED_PROMOTIONS.items():
            canonical = WAVE8_KICKAPOO_CONTRACTS[candidate_id]["canonical_event"]
            self.assertEqual(canonical["name"], expected["name"])
            self.assertEqual(canonical["year_low"], expected["year"])
            self.assertEqual(canonical["year_high"], expected["year"])
            self.assertEqual(canonical["date_precision"], expected["date_precision"])
            self.assertEqual(canonical["date_text"], expected["date_text"])
            self.assertEqual(canonical["granularity"], "engagement")
            self.assertEqual(
                canonical["canonical_key"],
                f"{normalize_label(expected['name']).replace(' ', '_')}:"
                f"{expected['year']}:{expected['year']}",
            )

    def test_only_source_attested_wins_are_promotable(self) -> None:
        self.assertEqual(WAVE8_KICKAPOO_OUTCOME_OVERRIDES, {})
        for candidate_id, contract in WAVE8_KICKAPOO_CONTRACTS.items():
            row = self.lane_rows[candidate_id]
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertIs(contract["source_outcome_override"], False)
            self.assertIs(contract["outcome_reversal"], False)
            self.assertIs(contract["actor_override"], True)
            self.assertEqual(row["winner_raw"], row["side_1_raw"])
            self.assertEqual(row["loser_raw"], row["side_2_raw"])
            self.assertNotEqual(normalize_label(row["winner_raw"]), "draw")

    def test_terminal_exclusions_are_explicit_and_never_draws(self) -> None:
        forbidden = {
            "losers",
            "outcome_source_family_ids",
            "outcome_source_ids",
            "result_type",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "winner_side",
            "winners",
        }
        self.assertEqual(WAVE8_KICKAPOO_HOLDS, {})
        for candidate_id, item in WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS.items():
            self.assertEqual(item["disposition"], "terminal_exclusion")
            self.assertIs(item["terminal_exclusion"], True)
            self.assertEqual(item["reviewed_outcome"], "unknown")
            self.assertIs(item["unknown_is_never_draw"], True)
            self.assertFalse(forbidden & set(item))
            self.assertIn("draw", item["hold_reason"].casefold())
            self.assertEqual(
                item["raw_row_sha256"],
                WAVE8_KICKAPOO_ROW_HASHES[candidate_id],
            )
            self.assertTrue(item["evidence_refs"])
            self.assertEqual(
                item["duplicate_ownership"],
                {"owner_module": "wave8_kickapoo", "status": "terminal_hced_owner"},
            )

    def test_killough_exclusion_owns_actor_and_competition_failures(self) -> None:
        item = WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS[
            "hced-Killough Massacre1838-1"
        ]
        self.assertEqual(item["reviewed_granularity"], "civilian_massacre")
        self.assertEqual(
            item["hold_category"],
            "civilian_massacre_with_unresolved_attacker_composition",
        )
        review = item["historical_review"]
        self.assertIs(review["competitive_event"], False)
        self.assertEqual(review["exact_attacker_composition"], "unknown")
        self.assertIn("anachronistic", review["raw_side_problem"])

    def test_wichita_exclusion_owns_composite_massacre_failure(self) -> None:
        item = WAVE8_KICKAPOO_TERMINAL_EXCLUSIONS[
            "hced-Wichita Agency1862-1"
        ]
        self.assertEqual(
            item["reviewed_granularity"], "composite_noncompetitive_massacre"
        )
        self.assertEqual(
            item["hold_category"],
            "composite_agency_attack_and_civilian_massacre",
        )
        review = item["historical_review"]
        self.assertIs(review["competitive_event"], False)
        self.assertIn("23 October", review["episode_1"])
        self.assertIn("24 October", review["episode_2"])
        self.assertIn("rate civilian victims", review["repair_risk"])

    def test_queue_validator_reports_four_promotions_and_two_exclusions(self) -> None:
        self.assertEqual(
            validate_wave8_kickapoo_queue_contracts(self.hced_rows),
            {
                "promotion_contracts": 4,
                "holds": 0,
                "reviewed_hced_rows": 6,
                "terminal_exclusions": 2,
            },
        )

    def test_queue_validator_fails_on_each_raw_row_tamper(self) -> None:
        for candidate_id in sorted(WAVE8_KICKAPOO_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                rows = copy.deepcopy(self.hced_rows)
                row = next(item for item in rows if item.get("candidate_id") == candidate_id)
                row["participants_raw"] = [*row.get("participants_raw", []), "tamper"]
                with self.assertRaisesRegex(ValueError, "fingerprint"):
                    validate_wave8_kickapoo_queue_contracts(rows)

    def test_queue_validator_fails_on_missing_or_duplicate_reserved_row(self) -> None:
        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Little Concho1862-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            validate_wave8_kickapoo_queue_contracts(missing)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(copy.deepcopy(self.lane_rows["hced-Dove Creek1865-1"]))
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            validate_wave8_kickapoo_queue_contracts(duplicated)

    def test_queue_validator_fails_on_future_exact_label_row(self) -> None:
        rows = copy.deepcopy(self.hced_rows)
        future = copy.deepcopy(self.lane_rows["hced-Battle Creek, Texas1838-1"])
        future.update(
            {
                "candidate_id": "hced-Future Kickapoo Event1900-1",
                "name": "Future Kickapoo Event",
                "source_record_id": "Future Kickapoo Event1900",
                "source_row": 999999,
                "side_1_raw": "KICKAPOO INDIANS",
                "side_2_raw": "Future opponent",
                "winner_raw": "KICKAPOO INDIANS",
                "loser_raw": "Future opponent",
                "year_best": 1900,
                "year_low": 1900,
                "year_high": 1900,
            }
        )
        rows.append(future)
        with self.assertRaisesRegex(ValueError, "exact Kickapoo Indians inventory"):
            validate_wave8_kickapoo_queue_contracts(rows)

    def test_unrelated_queue_rows_do_not_change_exact_inventory(self) -> None:
        rows = copy.deepcopy(self.hced_rows)
        rows.append(
            {
                "candidate_id": "hced-Unrelated1900-1",
                "name": "Unrelated",
                "side_1_raw": "Unrelated A",
                "side_2_raw": "Unrelated B",
                "year_low": 1900,
                "year_high": 1900,
            }
        )
        self.assertEqual(
            validate_wave8_kickapoo_queue_contracts(rows)["reviewed_hced_rows"],
            6,
        )

    def test_promoter_emits_exactly_the_four_contract_events(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 4)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_KICKAPOO_CONTRACT_IDS,
        )
        self.assertFalse(
            {event["hced_candidate_id"] for event in events}
            & WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS
        )
        self.assertEqual(len({event["id"] for event in events}), 4)
        self.assertTrue(all(event["id"].startswith(EVENT_ID_PREFIX) for event in events))

    def test_promoted_events_parse_and_have_exact_winners_and_losers(self) -> None:
        for event in self._events():
            parsed = Event.from_dict(event)
            expected = EXPECTED_PROMOTIONS[event["hced_candidate_id"]]
            self.assertEqual(parsed.name, expected["name"])
            self.assertEqual(parsed.year, expected["year"])
            self.assertEqual(event["date_precision"], expected["date_precision"])
            winners = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["result_class"].endswith("victory")
            }
            losers = {
                participant["entity_id"]
                for participant in event["participants"]
                if participant["result_class"].endswith("defeat")
            }
            self.assertEqual(winners, expected["winner"])
            self.assertEqual(losers, expected["loser"])
            self.assertEqual(event["reviewed_granularity"], "engagement")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")

    def test_promoted_participants_never_use_timeless_or_modern_entities(self) -> None:
        bounded_ids = {str(entity["id"]) for entity in WAVE8_KICKAPOO_ENTITIES}
        forbidden_ids = {
            "kickapoo",
            "kickapoo_indians",
            "kickapoo_traditional_tribe_of_texas",
            "united_states",
            "clio_q170588_1836_8e422d86",
            "clio_q81931_1861_f3bc20bd",
        }
        participants = {
            participant["entity_id"]
            for event in self._events()
            for participant in event["participants"]
        }
        self.assertEqual(participants, bounded_ids)
        self.assertFalse(participants & forbidden_ids)

    def test_promoted_source_and_outcome_provenance_is_installed(self) -> None:
        _, sources, _ = self._installed()
        for event in self._events():
            contract = WAVE8_KICKAPOO_CONTRACTS[event["hced_candidate_id"]]
            self.assertEqual(event["source_ids"][0], "hced_dataset")
            self.assertEqual(
                event["source_ids"][1:],
                list(contract["evidence_refs"]),
            )
            self.assertEqual(
                event["outcome_source_ids"],
                list(contract["outcome_source_ids"]),
            )
            self.assertEqual(
                event["outcome_source_family_ids"],
                list(contract["outcome_source_family_ids"]),
            )
            self.assertTrue(set(event["source_ids"][1:]) <= set(sources))

    def test_location_declarations_are_promoted_only(self) -> None:
        self.assertEqual(
            WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS,
            WAVE8_KICKAPOO_CONTRACT_IDS,
        )
        self.assertEqual(WAVE8_KICKAPOO_COUNTRY_QUARANTINE_ADDITIONS, frozenset())
        self.assertEqual(
            set(WAVE8_KICKAPOO_LOCATION_QUARANTINE_REASONS),
            WAVE8_KICKAPOO_CONTRACT_IDS,
        )
        self.assertFalse(
            WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS
            & WAVE8_KICKAPOO_TERMINAL_EXCLUSION_IDS
        )
        self.assertEqual(
            WAVE8_KICKAPOO_LOCATION_QUARANTINE_ADDITIONS,
            {
                "point": WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS,
                "country": frozenset(),
            },
        )
        self.assertEqual(
            wave8_kickapoo_location_quarantine_additions(),
            {
                "point": WAVE8_KICKAPOO_POINT_QUARANTINE_ADDITIONS,
                "country": frozenset(),
            },
        )

    def test_location_reasons_pin_each_raw_point_and_review_reference(self) -> None:
        source_ids = {str(source["id"]) for source in WAVE8_KICKAPOO_SOURCES}
        for candidate_id, reason in WAVE8_KICKAPOO_LOCATION_QUARANTINE_REASONS.items():
            row = self.lane_rows[candidate_id]
            self.assertEqual(reason["field"], "geometry")
            self.assertEqual(
                reason["raw_point"],
                [float(row["longitude"]), float(row["latitude"])],
            )
            self.assertIn(reason["reference_source_id"], source_ids)
            self.assertEqual(len(reason["reviewed_reference_point"]), 2)
            self.assertTrue(reason["reason"])

    def test_promoter_withholds_points_but_retains_country_and_provenance(self) -> None:
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "United States")
            self.assertEqual(event["location_provenance"]["source_id"], "hced_dataset")
            self.assertEqual(
                event["location_provenance"]["assertion_status"],
                "unreviewed_source_assertion",
            )

    def test_related_hced_dispositions_pin_both_rows_and_boundaries(self) -> None:
        self.assertEqual(len(WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS), 4)
        for candidate_id, item in WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS.items():
            related_id = item["related_hced_candidate_id"]
            self.assertIn(candidate_id, WAVE8_KICKAPOO_RESERVED_IDS)
            self.assertIn(related_id, WAVE8_KICKAPOO_RESERVED_IDS)
            self.assertNotEqual(candidate_id, related_id)
            self.assertEqual(
                item["raw_row_sha256"],
                canonical_hced_row_sha256(self.lane_rows[candidate_id]),
            )
            self.assertEqual(
                item["related_raw_row_sha256"],
                canonical_hced_row_sha256(self.lane_rows[related_id]),
            )
            self.assertIn("distinct", item["disposition"])
            self.assertEqual(item["owner_module"], "wave8_kickapoo")

    def test_cross_lane_disposition_is_shared_component_not_duplicate(self) -> None:
        self.assertEqual(set(WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS), {"wave8_cherokee"})
        item = WAVE8_KICKAPOO_CROSS_LANE_DISPOSITIONS["wave8_cherokee"]
        self.assertEqual(item["disposition"], "shared_component_not_duplicate")
        self.assertEqual(
            item["owned_candidate_ids"],
            ["hced-Battle Creek, Texas1838-1"],
        )
        self.assertFalse(WAVE8_KICKAPOO_RESERVED_IDS & WAVE8_CHEROKEE_RESERVED_IDS)
        self.assertEqual(
            set(WAVE8_KICKAPOO_INTEGRATION_DISPOSITIONS),
            {
                *(f"related_hced:{item}" for item in WAVE8_KICKAPOO_RELATED_HCED_DISPOSITIONS),
                "cross_lane:wave8_cherokee",
            },
        )

    def test_duplicate_negative_audit_is_complete_and_canonical(self) -> None:
        self.assertEqual(WAVE8_KICKAPOO_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(WAVE8_KICKAPOO_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            set(WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_KICKAPOO_RESERVED_IDS,
        )
        pairs: set[tuple[int, str]] = set()
        for item in WAVE8_KICKAPOO_IWBD_ZERO_OVERLAP_AUDIT.values():
            aliases = list(item["aliases"])
            years = list(item["years"])
            self.assertEqual(aliases, sorted(set(aliases)))
            self.assertTrue(all(alias == normalize_label(alias) for alias in aliases))
            self.assertEqual(years, sorted(set(years)))
            pairs.update((year, alias) for year in years for alias in aliases)
        for item in (
            *WAVE8_KICKAPOO_CONTRACTS.values(),
            *WAVE8_KICKAPOO_NONPROMOTIONS.values(),
        ):
            canonical = item["canonical_event"]
            self.assertIn(
                (canonical["year_low"], normalize_label(canonical["name"])),
                pairs,
            )

    def test_current_integration_inventory_has_no_duplicate(self) -> None:
        _, _, existing = self._installed()
        self.assertEqual(
            validate_wave8_kickapoo_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_lane_hced_dispositions": 1,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 5,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "iwbd_zero_overlap_candidates": 6,
                "related_hced_dispositions": 4,
            },
        )

    def test_integration_validator_rejects_future_hced_twin(self) -> None:
        rows = copy.deepcopy(self.hced_rows)
        rows.append(
            {
                "candidate_id": "hced-Future Dove Creek1865-1",
                "name": "Dove Creek Battle",
                "side_1_raw": "Unrelated A",
                "side_2_raw": "Unrelated B",
                "year_low": 1865,
                "year_high": 1865,
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_kickapoo_integration_dispositions(rows, self.iwbd_rows)

    def test_integration_validator_rejects_future_iwbd_twin(self) -> None:
        iwbd = copy.deepcopy(self.iwbd_rows)
        iwbd.append(
            {
                "candidate_id": "iwbd-future-kickapoo-town",
                "name": "Kickapoo Battlefield",
                "start_date": "1838-10-16",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            validate_wave8_kickapoo_integration_dispositions(self.hced_rows, iwbd)

    def test_integration_validator_rejects_release_name_or_alias_twin(self) -> None:
        for event in (
            {"id": "future-name", "name": "Tonkawa Massacre", "year": 1862},
            {
                "id": "future-alias",
                "name": "Different title",
                "aliases": ["The Surveyors Fight"],
                "year": 1838,
            },
        ):
            with self.subTest(event=event["id"]):
                with self.assertRaisesRegex(ValueError, "existing-release twin"):
                    validate_wave8_kickapoo_integration_dispositions(
                        self.hced_rows,
                        self.iwbd_rows,
                        [event],
                    )

    def test_installers_are_idempotent_and_deep_copy_fixtures(self) -> None:
        entities: dict[str, dict] = {}
        install_wave8_kickapoo_entities(entities)
        first_entities = copy.deepcopy(entities)
        install_wave8_kickapoo_entities(entities)
        self.assertEqual(entities, first_entities)

        sources: dict[str, dict] = {}
        install_wave8_kickapoo_sources(sources)
        first_sources = copy.deepcopy(sources)
        install_wave8_kickapoo_sources(sources)
        self.assertEqual(sources, first_sources)

        entity_id = str(WAVE8_KICKAPOO_ENTITIES[0]["id"])
        source_id = str(WAVE8_KICKAPOO_SOURCES[0]["id"])
        entities[entity_id]["name"] = "mutated"
        sources[source_id]["title"] = "mutated"
        self.assertNotEqual(entities[entity_id], WAVE8_KICKAPOO_ENTITIES[0])
        self.assertNotEqual(sources[source_id], WAVE8_KICKAPOO_SOURCES[0])

    def test_installers_reject_conflicting_existing_fixtures(self) -> None:
        entity = copy.deepcopy(WAVE8_KICKAPOO_ENTITIES[0])
        entity["name"] = "collision"
        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_kickapoo_entities({str(entity["id"]): entity})

        source = copy.deepcopy(WAVE8_KICKAPOO_SOURCES[0])
        source["title"] = "collision"
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_kickapoo_sources({str(source["id"]): source})

    def test_promoter_rejects_missing_or_out_of_window_entity(self) -> None:
        entities, _, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(BATTLE_CREEK_WAR_PARTY_ID)
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_kickapoo_contracts(self.hced_rows, missing, existing)

        drifted = copy.deepcopy(entities)
        drifted[BATTLE_CREEK_WAR_PARTY_ID]["end_year"] = 1837
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_kickapoo_contracts(self.hced_rows, drifted, existing)

    def test_promoter_rejects_existing_candidate_or_event_twin(self) -> None:
        entities, _, _ = self._installed()
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            promote_wave8_kickapoo_contracts(
                self.hced_rows,
                entities,
                [
                    {
                        "id": "existing-candidate",
                        "name": "Different name",
                        "year": 1838,
                        "hced_candidate_id": "hced-Battle Creek, Texas1838-1",
                    }
                ],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_kickapoo_contracts(
                self.hced_rows,
                entities,
                [{"id": "existing-event", "name": "Battle of Dove Creek", "year": 1865}],
            )

    def test_promoter_does_not_mutate_inputs(self) -> None:
        entities, _, existing = self._installed()
        rows = copy.deepcopy(self.hced_rows)
        entity_copy = copy.deepcopy(entities)
        existing_copy = copy.deepcopy(existing)
        promote_wave8_kickapoo_contracts(rows, entity_copy, existing_copy)
        self.assertEqual(rows, self.hced_rows)
        self.assertEqual(entity_copy, entities)
        self.assertEqual(existing_copy, existing)


if __name__ == "__main__":
    unittest.main()
