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
from military_elo.promotion import wave8_ute as lane


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_ute_"

PONCHA_UTE_FORCE_ID = "blancos_moache_ute_fighting_force_poncha_1855"
PONCHA_US_COLUMN_ID = "fauntleroy_poncha_pass_column_1855"
MILK_CREEK_UTE_FORCE_ID = "chief_jack_white_river_ute_force_milk_creek_1879"
MILK_CREEK_US_COLUMN_ID = "thornburgh_5th_cavalry_expedition_milk_creek_1879"


EXPECTED_RAW_ROWS = {
    "hced-Poncha Pass1855-1": {
        "name": "Poncha Pass",
        "side_1_raw": "United States",
        "side_2_raw": "Ute Indians",
        "winner_raw": "United States",
        "loser_raw": "Ute Indians",
        "year": 1855,
        "source_row": 12691,
    },
    "hced-Red Canyon1879-1": {
        "name": "Red Canyon",
        "side_1_raw": "United States",
        "side_2_raw": "Ute Indians",
        "winner_raw": "United States",
        "loser_raw": "Ute Indians",
        "year": 1879,
        "source_row": 13269,
    },
    "hced-Spanish Fork Canon1863-1": {
        "name": "Spanish Fork Canon",
        "side_1_raw": "United States",
        "side_2_raw": "Ute Indians",
        "winner_raw": "United States",
        "loser_raw": "Ute Indians",
        "year": 1863,
        "source_row": 15105,
    },
    "hced-White River1879-1": {
        "name": "White River",
        "side_1_raw": "Ute Indians",
        "side_2_raw": "United States",
        "winner_raw": "Ute Indians",
        "loser_raw": "United States",
        "year": 1879,
        "source_row": 17255,
    },
}


EXPECTED_PROMOTIONS = {
    "hced-Poncha Pass1855-1": {
        "name": "Battle near Poncha Pass",
        "year": 1855,
        "date_text": "28 April 1855",
        "granularity": "engagement",
        "winner": {PONCHA_US_COLUMN_ID},
        "loser": {PONCHA_UTE_FORCE_ID},
    },
    "hced-White River1879-1": {
        "name": "Opening action at Milk Creek",
        "year": 1879,
        "date_text": "29 September 1879",
        "granularity": "engagement_phase",
        "winner": {MILK_CREEK_UTE_FORCE_ID},
        "loser": {MILK_CREEK_US_COLUMN_ID},
    },
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    if not path.exists():
        raise unittest.SkipTest(f"locked review queue unavailable: {path.name}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Wave8UteTests(unittest.TestCase):
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
            if row.get("candidate_id") in lane.WAVE8_UTE_RESERVED_IDS
        }

    def _base_release_events(self):
        return [
            event
            for event in self.release_events
            if event.get("hced_candidate_id") not in lane.WAVE8_UTE_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]

    def _installed(self):
        entity_ids = {str(item["id"]) for item in lane.WAVE8_UTE_ENTITIES}
        entities = {
            str(item["id"]): item
            for item in self.release_entities
            if str(item["id"]) not in entity_ids
        }
        lane.install_wave8_ute_entities(entities)

        source_ids = {str(item["id"]) for item in lane.WAVE8_UTE_SOURCES}
        sources = {
            str(item["id"]): item
            for item in self.release_sources
            if str(item["id"]) not in source_ids
        }
        lane.install_wave8_ute_sources(sources)
        return entities, sources, self._base_release_events()

    def _events(self):
        entities, _, existing = self._installed()
        return lane.promote_wave8_ute_contracts(
            self.hced_rows,
            entities,
            existing,
        )

    def _funnel_label(self):
        return next(
            item
            for item in self.funnel["labels"]
            if item.get("label") == "ute indians"
        )

    def test_locked_queue_and_exact_candidate_hashes_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.hced_path.read_bytes()).hexdigest(),
            lane.WAVE8_UTE_HCED_QUEUE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.iwbd_path.read_bytes()).hexdigest(),
            lane.WAVE8_UTE_IWBD_QUEUE_SHA256,
        )
        measured_ids = sorted(self.lane_rows)
        digest = hashlib.sha256(
            ("\n".join(measured_ids) + "\n").encode("utf-8")
        ).hexdigest()
        self.assertEqual(digest, lane.WAVE8_UTE_EXACT_CANDIDATE_ID_SHA256)
        self.assertEqual(
            digest,
            lane.WAVE8_UTE_FUNNEL_EVENT_CANDIDATE_ID_SHA256,
        )

    def test_complete_exact_label_inventory_is_four_rows(self) -> None:
        exact_ids = {
            str(row["candidate_id"])
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "ute indians"
            or normalize_label(row.get("side_2_raw")) == "ute indians"
        }
        self.assertEqual(exact_ids, lane.WAVE8_UTE_EXPECTED_CANDIDATE_IDS)
        self.assertEqual(exact_ids, set(EXPECTED_RAW_ROWS))
        for candidate_id, expected in EXPECTED_RAW_ROWS.items():
            row = self.lane_rows[candidate_id]
            for field in ("name", "side_1_raw", "side_2_raw", "winner_raw", "loser_raw"):
                self.assertEqual(row[field], expected[field])
            self.assertEqual(row["year_low"], expected["year"])
            self.assertEqual(row["year_high"], expected["year"])
            self.assertEqual(row["source_row"], expected["source_row"])
            self.assertTrue(row["winner_loser_complete"])
            self.assertEqual(
                canonical_hced_row_sha256(row),
                lane.WAVE8_UTE_ROW_HASHES[candidate_id],
            )

    def test_funnel_inventory_and_failure_shape_are_exact(self) -> None:
        item = self._funnel_label()
        self.assertEqual(item["events_touched"], 4)
        self.assertEqual(item["sole_blocker_events"], 4)
        self.assertEqual(item["unresolved_side_attempts"], 4)
        self.assertEqual(item["centuries"], {"CE_19": 4})
        self.assertEqual(item["rated_counterpart_entities"], 1)
        self.assertEqual(item["time_valid_candidate_ids"], [])
        self.assertEqual(item["candidate_ids"], [])
        self.assertEqual(item["failure_cases"]["zero_time_valid_candidates"], 4)
        self.assertEqual(sum(item["failure_cases"].values()), 4)
        self.assertEqual(
            item["event_candidate_id_sha256"],
            lane.WAVE8_UTE_EXACT_CANDIDATE_ID_SHA256,
        )

    def test_dispositions_partition_exact_inventory_two_one_one(self) -> None:
        self.assertEqual(
            lane.WAVE8_UTE_CONTRACT_IDS,
            {"hced-Poncha Pass1855-1", "hced-White River1879-1"},
        )
        self.assertEqual(
            lane.WAVE8_UTE_HOLD_IDS,
            {"hced-Spanish Fork Canon1863-1"},
        )
        self.assertEqual(
            lane.WAVE8_UTE_TERMINAL_EXCLUSION_IDS,
            {"hced-Red Canyon1879-1"},
        )
        self.assertEqual(
            lane.WAVE8_UTE_EXCLUSION_IDS,
            lane.WAVE8_UTE_TERMINAL_EXCLUSION_IDS,
        )
        self.assertIs(lane.WAVE8_UTE_EXCLUSIONS, lane.WAVE8_UTE_TERMINAL_EXCLUSIONS)
        self.assertEqual(
            set(lane.WAVE8_UTE_NONPROMOTIONS),
            lane.WAVE8_UTE_HOLD_IDS | lane.WAVE8_UTE_EXCLUSION_IDS,
        )
        self.assertEqual(
            lane.WAVE8_UTE_RESERVED_IDS,
            lane.WAVE8_UTE_EXPECTED_CANDIDATE_IDS,
        )

    def test_audit_signature_is_independently_reproducible(self) -> None:
        payload = {
            "adjacent_hced_dispositions": lane.WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS,
            "alternate_label_audit": lane.WAVE8_UTE_ALTERNATE_LABEL_AUDIT,
            "contracts": lane.WAVE8_UTE_CONTRACTS,
            "country_quarantine_additions": sorted(
                lane.WAVE8_UTE_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_spelling_duplicate_audit": lane.WAVE8_UTE_CROSS_SPELLING_DUPLICATE_AUDIT,
            "entities": lane.WAVE8_UTE_ENTITIES,
            "exact_candidate_id_sha256": lane.WAVE8_UTE_EXACT_CANDIDATE_ID_SHA256,
            "existing_release_duplicate_dispositions": (
                lane.WAVE8_UTE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(lane.WAVE8_UTE_EXPECTED_CANDIDATE_IDS),
            "hced_queue_sha256": lane.WAVE8_UTE_HCED_QUEUE_SHA256,
            "holds": lane.WAVE8_UTE_HOLDS,
            "integration_dispositions": lane.WAVE8_UTE_INTEGRATION_DISPOSITIONS,
            "iwbd_duplicate_dispositions": lane.WAVE8_UTE_IWBD_DUPLICATE_DISPOSITIONS,
            "iwbd_queue_sha256": lane.WAVE8_UTE_IWBD_QUEUE_SHA256,
            "iwbd_zero_overlap_audit": lane.WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT,
            "location_quarantine_reasons": lane.WAVE8_UTE_LOCATION_QUARANTINE_REASONS,
            "opposite_result_audit": lane.WAVE8_UTE_OPPOSITE_RESULT_AUDIT,
            "outcome_overrides": lane.WAVE8_UTE_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                lane.WAVE8_UTE_POINT_QUARANTINE_ADDITIONS
            ),
            "related_hced_dispositions": lane.WAVE8_UTE_RELATED_HCED_DISPOSITIONS,
            "row_hashes": lane.WAVE8_UTE_ROW_HASHES,
            "sources": lane.WAVE8_UTE_SOURCES,
            "terminal_exclusions": lane.WAVE8_UTE_TERMINAL_EXCLUSIONS,
        }
        measured = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        self.assertEqual(measured, lane.WAVE8_UTE_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(measured, lane.wave8_ute_audit_signature())
        self.assertEqual(len(measured), 64)

    def test_counts_and_cohorts_are_deterministic(self) -> None:
        self.assertEqual(
            lane.wave8_ute_counts(),
            {
                "adjacent_hced_dispositions": 4,
                "country_quarantine_additions": 0,
                "existing_release_duplicate_dispositions": 0,
                "holds": 1,
                "integration_dispositions": 9,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 4,
                "new_entities": 4,
                "new_sources": 13,
                "newly_rated_events": 2,
                "opposite_result_pairs": 1,
                "outcome_overrides": 0,
                "point_quarantine_additions": 2,
                "promotion_contracts": 2,
                "related_hced_dispositions": 1,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 1,
            },
        )
        self.assertEqual(
            lane.wave8_ute_cohort_counts(),
            {
                "fauntleroy_ute_campaign_1855": 1,
                "utah_black_hawk_war_precursor_1863": 1,
                "white_river_ute_campaign_1879": 2,
            },
        )

    def test_sources_are_direct_authoritative_parseable_and_consumed(self) -> None:
        source_ids = [str(item["id"]) for item in lane.WAVE8_UTE_SOURCES]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertEqual(len(source_ids), 13)
        publishers = {str(item["publisher"]) for item in lane.WAVE8_UTE_SOURCES}
        types = {str(item["source_type"]) for item in lane.WAVE8_UTE_SOURCES}
        for fixture in lane.WAVE8_UTE_SOURCES:
            parsed = Source.from_dict(fixture)
            self.assertEqual(parsed.id, fixture["id"])
            self.assertTrue(fixture["url"].startswith("https://"))
            self.assertEqual(fixture["accessed"], "2026-07-16")
            self.assertEqual(
                list(fixture["evidence_roles"]),
                sorted(set(fixture["evidence_roles"])),
            )
        self.assertIn("U.S. National Park Service", publishers)
        self.assertIn("Southern Ute Indian Tribe", publishers)
        self.assertIn("U.S. Army Combat Studies Institute Press", publishers)
        self.assertTrue(any("primary" in value for value in types))
        self.assertTrue(any("scholarly" in value for value in types))
        self.assertTrue(any("official_tribal" in value for value in types))

        consumed: set[str] = set()
        for entity in lane.WAVE8_UTE_ENTITIES:
            consumed.update(map(str, entity["source_ids"]))
        for contract in lane.WAVE8_UTE_CONTRACTS.values():
            consumed.update(map(str, contract["evidence_refs"]))
        for item in lane.WAVE8_UTE_NONPROMOTIONS.values():
            consumed.update(map(str, item["evidence_refs"]))
        for item in lane.WAVE8_UTE_RELATED_HCED_DISPOSITIONS.values():
            consumed.update(map(str, item["evidence_refs"]))
        self.assertEqual(consumed, set(source_ids))

    def test_entities_are_event_year_bounded_and_never_generic(self) -> None:
        ids = [str(item["id"]) for item in lane.WAVE8_UTE_ENTITIES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {
            PONCHA_UTE_FORCE_ID,
            PONCHA_US_COLUMN_ID,
            MILK_CREEK_UTE_FORCE_ID,
            MILK_CREEK_US_COLUMN_ID,
        })
        forbidden = {
            "ute",
            "ute indians",
            "white river utes",
            "united states",
            "us army",
        }
        for fixture in lane.WAVE8_UTE_ENTITIES:
            parsed = Entity.from_dict(fixture)
            self.assertEqual(parsed.start_year, parsed.end_year)
            self.assertIn(parsed.start_year, {1855, 1879})
            self.assertEqual(parsed.aliases, ())
            self.assertEqual(parsed.predecessors, ())
            self.assertNotIn(normalize_label(parsed.name), forbidden)
            note = parsed.continuity_note.casefold()
            for phrase in (
                "no rating is inherited",
                "ethnic label",
                "noncombatants",
                "modern tribal government",
                "united states",
            ):
                self.assertIn(phrase, note)

    def test_promoted_outcomes_have_independent_source_families(self) -> None:
        source_by_id = {
            str(item["id"]): item for item in lane.WAVE8_UTE_SOURCES
        }
        for candidate_id, contract in lane.WAVE8_UTE_CONTRACTS.items():
            outcomes = list(contract["outcome_source_ids"])
            families = list(contract["outcome_source_family_ids"])
            self.assertGreaterEqual(len(outcomes), 2)
            self.assertGreaterEqual(len(families), 2)
            self.assertEqual(outcomes, sorted(set(outcomes)))
            self.assertTrue(set(outcomes) <= set(contract["evidence_refs"]))
            self.assertEqual(
                families,
                sorted({source_by_id[item]["source_family_id"] for item in outcomes}),
            )
            self.assertTrue(
                all("outcome" in source_by_id[item]["evidence_roles"] for item in outcomes)
            )
            row = self.lane_rows[candidate_id]
            self.assertEqual(contract["result_type"], "win")
            self.assertEqual(contract["winner_side"], 1)
            self.assertIs(contract["source_outcome_override"], False)
            self.assertIs(contract["outcome_reversal"], False)
            self.assertEqual(row["winner_raw"], row["side_1_raw"])
            self.assertEqual(row["loser_raw"], row["side_2_raw"])

    def test_poncha_contract_is_narrow_and_era_correct(self) -> None:
        item = lane.WAVE8_UTE_CONTRACTS["hced-Poncha Pass1855-1"]
        canonical = item["canonical_event"]
        self.assertEqual(canonical["name"], "Battle near Poncha Pass")
        self.assertEqual(canonical["date_text"], "28 April 1855")
        self.assertEqual(canonical["date_precision"], "day")
        self.assertEqual(canonical["granularity"], "engagement")
        self.assertEqual(item["side_1_entity_ids"], [PONCHA_US_COLUMN_ID])
        self.assertEqual(item["side_2_entity_ids"], [PONCHA_UTE_FORCE_ID])
        self.assertIn("Chief Blanco", item["audit_note"])
        self.assertIn("Moache", item["audit_note"])
        self.assertIn("tactical action only", item["audit_note"])

    def test_white_river_contract_is_only_opening_milk_creek_action(self) -> None:
        item = lane.WAVE8_UTE_CONTRACTS["hced-White River1879-1"]
        canonical = item["canonical_event"]
        self.assertEqual(canonical["name"], "Opening action at Milk Creek")
        self.assertEqual(canonical["date_text"], "29 September 1879")
        self.assertEqual(canonical["date_precision"], "day")
        self.assertEqual(canonical["granularity"], "engagement_phase")
        self.assertEqual(item["side_1_entity_ids"], [MILK_CREEK_UTE_FORCE_ID])
        self.assertEqual(item["side_2_entity_ids"], [MILK_CREEK_US_COLUMN_ID])
        for excluded_scope in ("ensuing siege", "relief", "Meeker", "campaign settlement"):
            self.assertIn(excluded_scope.casefold(), item["audit_note"].casefold())

    def test_spanish_fork_is_held_between_two_documented_actions(self) -> None:
        item = lane.WAVE8_UTE_HOLDS["hced-Spanish Fork Canon1863-1"]
        self.assertEqual(item["disposition"], "hold")
        self.assertIs(item["terminal_exclusion"], False)
        self.assertEqual(item["reviewed_outcome"], "unknown")
        self.assertIs(item["unknown_is_never_draw"], True)
        self.assertEqual(
            item["hold_category"],
            "same_name_same_year_actions_and_actor_ambiguity",
        )
        review = item["historical_review"]
        self.assertEqual(review["alternative_1"]["date"], "4 April 1863")
        self.assertEqual(review["alternative_2"]["date"], "15 April 1863")
        self.assertIn("Price", review["alternative_1"]["us_formation"])
        self.assertIn("Evans", review["alternative_2"]["us_formation"])
        self.assertIn("Ute and Gosiute", review["source_actor_boundary"])
        self.assertIn("never a draw", item["hold_reason"])

    def test_red_canyon_is_opposite_result_duplicate_owned_by_white_river(self) -> None:
        item = lane.WAVE8_UTE_TERMINAL_EXCLUSIONS["hced-Red Canyon1879-1"]
        owner = lane.WAVE8_UTE_CONTRACTS["hced-White River1879-1"]
        self.assertEqual(item["disposition"], "terminal_exclusion")
        self.assertIs(item["terminal_exclusion"], True)
        self.assertEqual(item["reviewed_outcome"], "unknown")
        self.assertIs(item["unknown_is_never_draw"], True)
        self.assertEqual(
            item["canonical_event"]["canonical_key"],
            owner["canonical_event"]["canonical_key"],
        )
        review = item["historical_review"]
        self.assertEqual(review["canonical_owner_candidate_id"], "hced-White River1879-1")
        self.assertEqual(review["raw_claimed_result"], "United States victory")
        self.assertEqual(review["reviewed_opening_result"], "White River Ute tactical victory")
        self.assertIs(review["independent_second_engagement"], False)
        self.assertIn("not a draw", item["hold_reason"])
        self.assertEqual(
            lane.WAVE8_UTE_OPPOSITE_RESULT_AUDIT["same_event_opposite_result_pairs"],
            [["hced-Red Canyon1879-1", "hced-White River1879-1"]],
        )
        self.assertIs(
            lane.WAVE8_UTE_OPPOSITE_RESULT_AUDIT["campaign_result_inferred"],
            False,
        )

    def test_nonpromotions_carry_no_rateable_result_fields(self) -> None:
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
        for candidate_id, item in lane.WAVE8_UTE_NONPROMOTIONS.items():
            self.assertFalse(forbidden & set(item))
            self.assertEqual(item["reviewed_outcome"], "unknown")
            self.assertIs(item["unknown_is_never_draw"], True)
            self.assertEqual(
                item["raw_row_sha256"],
                lane.WAVE8_UTE_ROW_HASHES[candidate_id],
            )
        self.assertEqual(lane.WAVE8_UTE_OUTCOME_OVERRIDES, {})

    def test_alternate_band_names_and_spelling_boundaries_are_explicit(self) -> None:
        audit = lane.WAVE8_UTE_ALTERNATE_LABEL_AUDIT
        alternates = audit["reviewed_alternate_side_labels"]
        self.assertEqual(alternates, sorted(set(alternates)))
        for expected in (
            "moache ute",
            "mouache ute",
            "muache ute",
            "uintah ute",
            "uncompahgre ute",
            "ute",
            "utes",
            "white river utes",
        ):
            self.assertIn(expected, alternates)
        matched = {
            str(row["candidate_id"])
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) in set(alternates)
            or normalize_label(row.get("side_2_raw")) in set(alternates)
        }
        self.assertEqual(matched, set())
        self.assertEqual(audit["matched_alternate_side_candidate_ids"], [])
        self.assertNotIn("jute", alternates)
        self.assertNotIn("paiute indians", alternates)

    def test_adjacent_actor_and_noisy_token_ownership_is_pinned(self) -> None:
        expected = {
            "hced-Adobe Walls1864-1": ("wave8_comanche", "separate_comanche_lane_hold"),
            "hced-Bear River1863-1": ("not_wave8_ute", "separate_shoshone_event"),
            "hced-Cieneguilla1854-1": ("wave8_north_america", "existing_north_america_lane_hold"),
            "hced-Spanish Armada1588-1": ("not_wave8_ute", "participant_token_false_positive"),
        }
        by_id = {str(row["candidate_id"]): row for row in self.hced_rows}
        self.assertIs(
            lane.WAVE8_UTE_CROSS_LANE_DISPOSITIONS,
            lane.WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS,
        )
        for candidate_id, (owner, disposition) in expected.items():
            item = lane.WAVE8_UTE_ADJACENT_HCED_DISPOSITIONS[candidate_id]
            self.assertEqual(item["owner_module"], owner)
            self.assertEqual(item["disposition"], disposition)
            self.assertEqual(
                canonical_hced_row_sha256(by_id[candidate_id]),
                item["raw_row_sha256"],
            )
        armada = by_id["hced-Spanish Armada1588-1"]
        self.assertIn("Ute", armada["participants_raw"])
        self.assertEqual({armada["side_1_raw"], armada["side_2_raw"]}, {"England", "Spain"})
        self.assertEqual(by_id["hced-Bear River1863-1"]["side_2_raw"], "Shoshone Indians")

    def test_duplicate_alias_audit_covers_hced_iwbd_and_release_surfaces(self) -> None:
        self.assertEqual(lane.WAVE8_UTE_IWBD_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(lane.WAVE8_UTE_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS, {})
        self.assertEqual(
            set(lane.WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT),
            lane.WAVE8_UTE_RESERVED_IDS,
        )
        for item in lane.WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT.values():
            self.assertEqual(list(item["aliases"]), sorted(set(item["aliases"])))
            self.assertTrue(all(alias == normalize_label(alias) for alias in item["aliases"]))
        red = set(lane.WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT["hced-Red Canyon1879-1"]["aliases"])
        white = set(lane.WAVE8_UTE_IWBD_ZERO_OVERLAP_AUDIT["hced-White River1879-1"]["aliases"])
        self.assertEqual(red, white)
        self.assertTrue({"milk creek", "red canyon", "white river", "thornburgh disaster"} <= red)

    def test_queue_validator_reports_exact_dispositions(self) -> None:
        self.assertEqual(
            lane.validate_wave8_ute_queue_contracts(self.hced_rows),
            {
                "promotion_contracts": 2,
                "holds": 1,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 1,
            },
        )

    def test_queue_validator_fails_on_every_exact_row_tamper(self) -> None:
        for candidate_id in sorted(lane.WAVE8_UTE_RESERVED_IDS):
            with self.subTest(candidate_id=candidate_id):
                rows = copy.deepcopy(self.hced_rows)
                row = next(item for item in rows if item.get("candidate_id") == candidate_id)
                row["participants_raw"] = [*row.get("participants_raw", []), "tamper"]
                with self.assertRaisesRegex(ValueError, "fingerprint"):
                    lane.validate_wave8_ute_queue_contracts(rows)

    def test_queue_validator_fails_on_missing_duplicate_or_new_exact_row(self) -> None:
        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Poncha Pass1855-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            lane.validate_wave8_ute_queue_contracts(missing)

        duplicated = copy.deepcopy(self.hced_rows)
        duplicated.append(copy.deepcopy(self.lane_rows["hced-White River1879-1"]))
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            lane.validate_wave8_ute_queue_contracts(duplicated)

        future = copy.deepcopy(self.hced_rows)
        row = copy.deepcopy(self.lane_rows["hced-Poncha Pass1855-1"])
        row.update(
            {
                "candidate_id": "hced-Future Ute Event1900-1",
                "name": "Future Ute Event",
                "source_record_id": "Future Ute Event1900",
                "source_row": 999999,
                "year_best": 1900,
                "year_low": 1900,
                "year_high": 1900,
            }
        )
        future.append(row)
        with self.assertRaisesRegex(ValueError, "exact Ute Indians inventory"):
            lane.validate_wave8_ute_queue_contracts(future)

    def test_queue_validator_fails_on_new_alternate_label_and_unrelated_drift(self) -> None:
        alternate = copy.deepcopy(self.hced_rows)
        row = copy.deepcopy(self.lane_rows["hced-Poncha Pass1855-1"])
        row.update(
            {
                "candidate_id": "hced-Future Mouache1900-1",
                "name": "Future Mouache",
                "source_record_id": "Future Mouache1900",
                "source_row": 999998,
                "side_2_raw": "Mouache Ute",
                "loser_raw": "Mouache Ute",
                "year_best": 1900,
                "year_low": 1900,
                "year_high": 1900,
            }
        )
        alternate.append(row)
        with self.assertRaisesRegex(ValueError, "alternate Ute side-label inventory"):
            lane.validate_wave8_ute_queue_contracts(alternate)

        unrelated = copy.deepcopy(self.hced_rows)
        unrelated.append(
            {
                "candidate_id": "hced-Unrelated1900-1",
                "name": "Unrelated",
                "side_1_raw": "Unrelated A",
                "side_2_raw": "Unrelated B",
                "year_low": 1900,
                "year_high": 1900,
            }
        )
        with self.assertRaisesRegex(ValueError, "HCED queue snapshot changed"):
            lane.validate_wave8_ute_queue_contracts(unrelated)

    def test_integration_validator_pins_adjacent_rows_and_zero_duplicates(self) -> None:
        result = lane.validate_wave8_ute_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            self._base_release_events(),
        )
        self.assertEqual(
            result,
            {
                "adjacent_hced_dispositions": 4,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 9,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "release_lane_overlap": 0,
                "related_hced_dispositions": 1,
            },
        )
        tampered = copy.deepcopy(self.hced_rows)
        row = next(item for item in tampered if item.get("candidate_id") == "hced-Cieneguilla1854-1")
        row["participants_raw"] = [*row["participants_raw"], "tamper"]
        with self.assertRaisesRegex(ValueError, "adjacent HCED fingerprint"):
            lane.validate_wave8_ute_integration_dispositions(
                tampered,
                self.iwbd_rows,
            )

    def test_integration_validator_rejects_future_hced_iwbd_and_release_twins(self) -> None:
        hced = copy.deepcopy(self.hced_rows)
        hced.append(
            {
                "candidate_id": "hced-Future Poncha Twin1855-1",
                "name": "Battle of Poncha Pass",
                "year_best": 1855,
            }
        )
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            lane.validate_wave8_ute_integration_dispositions(hced, self.iwbd_rows)

        iwbd = copy.deepcopy(self.iwbd_rows)
        iwbd.append(
            {
                "candidate_id": "iwbd-future-milk-creek-1879",
                "name": "Battle of Milk Creek",
                "start_date": "1879-09-29",
                "end_date": "1879-10-05",
            }
        )
        with self.assertRaisesRegex(ValueError, "probable IWBD duplicate"):
            lane.validate_wave8_ute_integration_dispositions(self.hced_rows, iwbd)

        release = [
            *self._base_release_events(),
            {"id": "future-milk-creek-twin", "name": "Milk Creek", "year": 1879},
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            lane.validate_wave8_ute_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release,
            )

    def test_release_overlap_is_all_or_none_and_nonpromotions_never_enter(self) -> None:
        events = self._events()
        base = self._base_release_events()
        full = lane.validate_wave8_ute_integration_dispositions(
            self.hced_rows,
            self.iwbd_rows,
            [*base, *events],
        )
        self.assertEqual(full["release_lane_overlap"], 2)

        with self.assertRaisesRegex(ValueError, "partial release integration"):
            lane.validate_wave8_ute_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*base, events[0]],
            )
        with self.assertRaisesRegex(ValueError, "partial or duplicate release overlap"):
            lane.validate_wave8_ute_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [*base, *events, copy.deepcopy(events[0])],
            )
        with self.assertRaisesRegex(ValueError, "nonpromotion entered release"):
            lane.validate_wave8_ute_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                [
                    *base,
                    {
                        "id": "invalid-red-canyon",
                        "name": "Red Canyon",
                        "year": 1879,
                        "hced_candidate_id": "hced-Red Canyon1879-1",
                    },
                ],
            )

    def test_promoter_emits_only_two_defensible_unique_events(self) -> None:
        events = self._events()
        self.assertEqual(len(events), 2)
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            lane.WAVE8_UTE_CONTRACT_IDS,
        )
        self.assertFalse(
            {event["hced_candidate_id"] for event in events}
            & set(lane.WAVE8_UTE_NONPROMOTIONS)
        )
        self.assertEqual(len({event["id"] for event in events}), 2)
        self.assertTrue(all(event["id"].startswith(EVENT_ID_PREFIX) for event in events))
        self.assertEqual(events, self._events())

    def test_promoted_events_parse_with_exact_winners_losers_and_provenance(self) -> None:
        for event in self._events():
            parsed = Event.from_dict(event)
            expected = EXPECTED_PROMOTIONS[event["hced_candidate_id"]]
            self.assertEqual(parsed.name, expected["name"])
            self.assertEqual(parsed.year, expected["year"])
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
            self.assertEqual(event["date_precision"], "day")
            self.assertEqual(event["reviewed_granularity"], expected["granularity"])
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["status"], "complete")
            contract = lane.WAVE8_UTE_CONTRACTS[event["hced_candidate_id"]]
            self.assertEqual(event["canonical_event_key"], contract["canonical_event"]["canonical_key"])
            self.assertEqual(event["outcome_source_ids"], contract["outcome_source_ids"])
            self.assertEqual(
                event["outcome_source_family_ids"],
                contract["outcome_source_family_ids"],
            )

    def test_promoted_participants_are_exactly_four_bounded_formations(self) -> None:
        bounded_ids = {str(item["id"]) for item in lane.WAVE8_UTE_ENTITIES}
        participants = {
            participant["entity_id"]
            for event in self._events()
            for participant in event["participants"]
        }
        self.assertEqual(participants, bounded_ids)
        self.assertFalse(
            participants
            & {
                "ute",
                "ute_indians",
                "white_river_utes",
                "united_states",
                "us_army",
            }
        )

    def test_local_location_quarantine_strips_only_geometry(self) -> None:
        before_point_object = HCED_POINT_QUARANTINE_IDS
        before_country_object = HCED_COUNTRY_QUARANTINE_IDS
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)

        self.assertEqual(
            lane.wave8_ute_location_quarantine_additions(),
            {
                "country": frozenset(),
                "point": lane.WAVE8_UTE_CONTRACT_IDS,
            },
        )
        self.assertEqual(
            set(lane.WAVE8_UTE_LOCATION_QUARANTINE_REASONS),
            lane.WAVE8_UTE_CONTRACT_IDS,
        )
        for event in self._events():
            self.assertNotIn("geometry", event)
            self.assertEqual(event["modern_location_country"], "United States")
            self.assertIn("location_provenance", event)
        self.assertIs(HCED_POINT_QUARANTINE_IDS, before_point_object)
        self.assertIs(HCED_COUNTRY_QUARANTINE_IDS, before_country_object)
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), before_points)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), before_countries)

    def test_entity_windows_and_existing_event_collisions_fail_closed(self) -> None:
        entities, _, existing = self._installed()
        shortened = copy.deepcopy(entities)
        shortened[PONCHA_US_COLUMN_ID]["start_year"] = 1856
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            lane.promote_wave8_ute_contracts(
                self.hced_rows,
                shortened,
                existing,
            )

        events = lane.promote_wave8_ute_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        with self.assertRaisesRegex(ValueError, "candidates already promoted"):
            lane.promote_wave8_ute_contracts(
                self.hced_rows,
                entities,
                [*existing, events[0]],
            )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            lane.promote_wave8_ute_contracts(
                self.hced_rows,
                entities,
                [*existing, {"name": "Poncha Pass", "year": 1855}],
            )

    def test_installers_are_idempotent_copy_fixtures_and_reject_collisions(self) -> None:
        entities: dict[str, dict] = {}
        sources: dict[str, dict] = {}
        lane.install_wave8_ute_entities(entities)
        lane.install_wave8_ute_sources(sources)
        lane.install_wave8_ute_entities(entities)
        lane.install_wave8_ute_sources(sources)
        self.assertEqual(len(entities), 4)
        self.assertEqual(len(sources), 13)

        first_entity = str(lane.WAVE8_UTE_ENTITIES[0]["id"])
        first_source = str(lane.WAVE8_UTE_SOURCES[0]["id"])
        entities[first_entity]["name"] = "tampered local copy"
        sources[first_source]["title"] = "tampered local copy"
        self.assertNotEqual(entities[first_entity], lane.WAVE8_UTE_ENTITIES[0])
        self.assertNotEqual(sources[first_source], lane.WAVE8_UTE_SOURCES[0])

        bad_entity = {first_entity: {**lane.WAVE8_UTE_ENTITIES[0], "name": "collision"}}
        with self.assertRaisesRegex(ValueError, "entity collision"):
            lane.install_wave8_ute_entities(bad_entity)
        bad_source = {first_source: {**lane.WAVE8_UTE_SOURCES[0], "title": "collision"}}
        with self.assertRaisesRegex(ValueError, "source collision"):
            lane.install_wave8_ute_sources(bad_source)

    def test_public_api_contains_required_lane_operations(self) -> None:
        required = {
            "install_wave8_ute_entities",
            "install_wave8_ute_sources",
            "promote_wave8_ute_contracts",
            "validate_wave8_ute_integration_dispositions",
            "validate_wave8_ute_queue_contracts",
            "wave8_ute_audit_signature",
            "wave8_ute_cohort_counts",
            "wave8_ute_counts",
            "wave8_ute_location_quarantine_additions",
        }
        self.assertTrue(required <= set(lane.__all__))
        self.assertTrue(all(callable(getattr(lane, name)) for name in required))


if __name__ == "__main__":
    unittest.main()
