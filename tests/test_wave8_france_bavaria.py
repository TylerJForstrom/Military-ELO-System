from __future__ import annotations

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
from military_elo.promotion.wave7_west_data import WAVE7_WEST_BAVARIA_NEW_IDS
from military_elo.promotion.wave8_france_bavaria import (
    WAVE8_FRANCE_BAVARIA_CONTRACT_IDS,
    WAVE8_FRANCE_BAVARIA_CONTRACTS,
    WAVE8_FRANCE_BAVARIA_COUNTRY_QUARANTINE_ADDITIONS,
    WAVE8_FRANCE_BAVARIA_CROSS_LANE_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_ENTITIES,
    WAVE8_FRANCE_BAVARIA_EXCLUSIONS,
    WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT,
    WAVE8_FRANCE_BAVARIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS,
    WAVE8_FRANCE_BAVARIA_FINAL_AUDIT_SIGNATURE,
    WAVE8_FRANCE_BAVARIA_FUNNEL_AUDIT,
    WAVE8_FRANCE_BAVARIA_HOLD_IDS,
    WAVE8_FRANCE_BAVARIA_HOLDS,
    WAVE8_FRANCE_BAVARIA_INTEGRATION_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_IWBD_DUPLICATE_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT,
    WAVE8_FRANCE_BAVARIA_LOCATION_REVIEWS,
    WAVE8_FRANCE_BAVARIA_NONPROMOTIONS,
    WAVE8_FRANCE_BAVARIA_OUTCOME_OVERRIDES,
    WAVE8_FRANCE_BAVARIA_POINT_QUARANTINE_ADDITIONS,
    WAVE8_FRANCE_BAVARIA_REGIME_ENTITY_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_REQUIRED_EXISTING_ENTITY_IDS,
    WAVE8_FRANCE_BAVARIA_RESERVED_IDS,
    WAVE8_FRANCE_BAVARIA_ROW_DISPOSITIONS,
    WAVE8_FRANCE_BAVARIA_ROW_HASHES,
    WAVE8_FRANCE_BAVARIA_SOURCES,
    WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSION_IDS,
    WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS,
    install_wave8_france_bavaria_entities,
    install_wave8_france_bavaria_sources,
    promote_wave8_france_bavaria_contracts,
    validate_wave8_france_bavaria_existing_entities,
    validate_wave8_france_bavaria_funnel,
    validate_wave8_france_bavaria_integration_dispositions,
    validate_wave8_france_bavaria_queue_contracts,
    wave8_france_bavaria_audit_signature,
    wave8_france_bavaria_cohort_counts,
    wave8_france_bavaria_counts,
    wave8_france_bavaria_location_quarantine_additions,
    wave8_france_bavaria_metadata,
    wave8_france_bavaria_row_dispositions,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_ID_PREFIX = "hced_wave8_france_bavaria_"
EXACT_LABEL = "france bavaria"
NEW_FREE_CORPS = "black_brunswick_hesse_kassel_free_corps_gefrees_1809"
AUSTRIA = "austrian_empire"
FRANCE = "first_french_empire"
BAVARIA = "kingdom_bavaria_1806"
RUSSIA = "russian_empire"

EXPECTED_SIDES = {
    "hced-Gefrees1809-1": (
        {AUSTRIA, NEW_FREE_CORPS},
        {FRANCE, BAVARIA},
    ),
    "hced-Neumarkt-St-Viet1809-1": (
        {AUSTRIA},
        {FRANCE, BAVARIA},
    ),
    "hced-Polotsk (2nd)1812-1": (
        {RUSSIA},
        {FRANCE, BAVARIA},
    ),
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


class Wave8FranceBavariaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hced_rows = _jsonl(ROOT / "data" / "review" / "hced-candidates.jsonl")
        cls.iwbd_rows = _jsonl(ROOT / "data" / "review" / "iwbd-candidates.jsonl")
        cls.release_entities = _json(ROOT / "data" / "release" / "entities.json")
        cls.release_events = _json(ROOT / "data" / "release" / "events.json")
        cls.release_sources = _json(ROOT / "data" / "release" / "sources.json")
        cls.funnel = _json(ROOT / "build" / "hced-unresolved-label-funnel.json")

    def _installed(self):
        fixture_entity_ids = {
            str(entity["id"]) for entity in WAVE8_FRANCE_BAVARIA_ENTITIES
        }
        entities = {
            str(entity["id"]): copy.deepcopy(entity)
            for entity in self.release_entities
            if str(entity["id"]) not in fixture_entity_ids
        }
        install_wave8_france_bavaria_entities(entities)

        fixture_source_ids = {
            str(source["id"]) for source in WAVE8_FRANCE_BAVARIA_SOURCES
        }
        sources = {
            str(source["id"]): copy.deepcopy(source)
            for source in self.release_sources
            if str(source["id"]) not in fixture_source_ids
        }
        install_wave8_france_bavaria_sources(sources)

        existing = [
            copy.deepcopy(event)
            for event in self.release_events
            if event.get("hced_candidate_id")
            not in WAVE8_FRANCE_BAVARIA_RESERVED_IDS
            and not str(event.get("id", "")).startswith(EVENT_ID_PREFIX)
        ]
        return entities, sources, existing

    def _emit(self):
        entities, sources, existing = self._installed()
        events = promote_wave8_france_bavaria_contracts(
            self.hced_rows,
            entities,
            existing,
        )
        return events, entities, sources, existing

    def test_signature_counts_cohorts_and_metadata_are_pinned(self) -> None:
        payload = {
            "contracts": WAVE8_FRANCE_BAVARIA_CONTRACTS,
            "country_quarantine_additions": sorted(
                WAVE8_FRANCE_BAVARIA_COUNTRY_QUARANTINE_ADDITIONS
            ),
            "cross_lane_dispositions": WAVE8_FRANCE_BAVARIA_CROSS_LANE_DISPOSITIONS,
            "entities": WAVE8_FRANCE_BAVARIA_ENTITIES,
            "existing_lane_overlap_audit": (
                WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT
            ),
            "existing_release_duplicate_dispositions": (
                WAVE8_FRANCE_BAVARIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
            ),
            "expected_candidate_ids": sorted(
                WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS
            ),
            "funnel_audit": WAVE8_FRANCE_BAVARIA_FUNNEL_AUDIT,
            "holds": WAVE8_FRANCE_BAVARIA_HOLDS,
            "integration_dispositions": (
                WAVE8_FRANCE_BAVARIA_INTEGRATION_DISPOSITIONS
            ),
            "iwbd_duplicate_dispositions": (
                WAVE8_FRANCE_BAVARIA_IWBD_DUPLICATE_DISPOSITIONS
            ),
            "iwbd_zero_overlap_audit": (
                WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT
            ),
            "location_reviews": WAVE8_FRANCE_BAVARIA_LOCATION_REVIEWS,
            "outcome_overrides": WAVE8_FRANCE_BAVARIA_OUTCOME_OVERRIDES,
            "point_quarantine_additions": sorted(
                WAVE8_FRANCE_BAVARIA_POINT_QUARANTINE_ADDITIONS
            ),
            "regime_entity_dispositions": (
                WAVE8_FRANCE_BAVARIA_REGIME_ENTITY_DISPOSITIONS
            ),
            "related_hced_dispositions": (
                WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS
            ),
            "row_dispositions": WAVE8_FRANCE_BAVARIA_ROW_DISPOSITIONS,
            "sources": WAVE8_FRANCE_BAVARIA_SOURCES,
            "terminal_exclusions": WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS,
        }
        digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
        self.assertEqual(
            digest,
            "b798179295c3dc57a3a0715f450ea9c4c0e07d2a86626e49a0ae6578893598c2",
        )
        self.assertEqual(digest, wave8_france_bavaria_audit_signature())
        self.assertEqual(digest, WAVE8_FRANCE_BAVARIA_FINAL_AUDIT_SIGNATURE)
        self.assertEqual(
            wave8_france_bavaria_counts(),
            {
                "country_quarantine_additions": 0,
                "cross_lane_hced_dispositions": 0,
                "existing_lane_overlap_audits": 4,
                "existing_release_duplicate_dispositions": 0,
                "holds": 1,
                "integration_dispositions": 4,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_zero_overlap_candidates": 4,
                "new_entities": 1,
                "new_sources": 11,
                "newly_rated_events": 3,
                "outcome_overrides": 0,
                "point_quarantine_additions": 3,
                "promotion_contracts": 3,
                "related_hced_dispositions": 4,
                "required_existing_entities": 4,
                "reviewed_hced_rows": 4,
                "sole_blocker_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        self.assertEqual(
            wave8_france_bavaria_cohort_counts(),
            {
                "fifth_coalition_bavarian_campaign_1809": 1,
                "fifth_coalition_northern_theatre_1809": 1,
                "russian_campaign_polotsk_1812": 2,
            },
        )
        metadata = wave8_france_bavaria_metadata()
        self.assertEqual(metadata["exact_label"], EXACT_LABEL)
        self.assertEqual(metadata["module_owner"], "wave8_france_bavaria")
        self.assertEqual(metadata["signature"], digest)
        self.assertEqual(metadata["row_dispositions"], WAVE8_FRANCE_BAVARIA_ROW_DISPOSITIONS)
        self.assertEqual(
            wave8_france_bavaria_row_dispositions(),
            WAVE8_FRANCE_BAVARIA_ROW_DISPOSITIONS,
        )
        self.assertIsNot(
            wave8_france_bavaria_row_dispositions(),
            WAVE8_FRANCE_BAVARIA_ROW_DISPOSITIONS,
        )

    def test_locked_funnel_is_four_sole_blockers_with_two_counterpart_regimes(
        self,
    ) -> None:
        self.assertEqual(
            validate_wave8_france_bavaria_funnel(self.funnel),
            {"events_touched": 4, "sole_blocker_events": 4},
        )
        expected = WAVE8_FRANCE_BAVARIA_FUNNEL_AUDIT
        self.assertEqual(expected["events_touched"], 4)
        self.assertEqual(expected["failure_cases"]["zero_time_valid_candidates"], 4)
        self.assertEqual(
            {
                entity_id
                for values in expected["resolved_counterpart_entity_ids"].values()
                for entity_id in values
            },
            {AUSTRIA, RUSSIA},
        )
        tampered = copy.deepcopy(self.funnel)
        next(
            item for item in tampered["labels"] if item.get("label") == EXACT_LABEL
        )["events_touched"] = 5
        with self.assertRaisesRegex(ValueError, "funnel events_touched"):
            validate_wave8_france_bavaria_funnel(tampered)

        tampered = copy.deepcopy(self.funnel)
        row = next(
            item
            for item in tampered["row_label_data"]
            if item.get("candidate_id") == "hced-Gefrees1809-1"
        )
        row["resolved_counterpart_entity_ids"] = [RUSSIA]
        with self.assertRaisesRegex(ValueError, "sole-blocker row"):
            validate_wave8_france_bavaria_funnel(tampered)

    def test_exact_queue_inventory_hashes_and_label_order_are_pinned(self) -> None:
        self.assertEqual(
            validate_wave8_france_bavaria_queue_contracts(self.hced_rows),
            {
                "holds": 1,
                "promotion_contracts": 3,
                "reviewed_hced_rows": 4,
                "terminal_exclusions": 0,
            },
        )
        exact_rows = [
            row
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == EXACT_LABEL
            or normalize_label(row.get("side_2_raw")) == EXACT_LABEL
        ]
        self.assertEqual(
            {str(row["candidate_id"]) for row in exact_rows},
            WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS,
        )
        for row in exact_rows:
            candidate_id = str(row["candidate_id"])
            self.assertEqual(
                canonical_hced_row_sha256(row),
                WAVE8_FRANCE_BAVARIA_ROW_HASHES[candidate_id],
            )
        payload = "".join(
            f"{candidate_id}\n"
            for candidate_id in sorted(WAVE8_FRANCE_BAVARIA_EXPECTED_CANDIDATE_IDS)
        )
        self.assertEqual(
            hashlib.sha256(payload.encode("utf-8")).hexdigest(),
            "52b980eb0e9eb8290c1c387871606948063624dbbf7d9d9c069a2eef6fff3b22",
        )

        reverse_ids = {
            str(row["candidate_id"])
            for row in self.hced_rows
            if normalize_label(row.get("side_1_raw")) == "bavaria france"
            or normalize_label(row.get("side_2_raw")) == "bavaria france"
        }
        self.assertEqual(
            reverse_ids,
            {
                "hced-Berg Isel1809-1",
                "hced-Blenheim1704-1",
                "hced-Braunau1743-1",
                "hced-Hochstadt1703-1",
            },
        )
        self.assertFalse(reverse_ids & WAVE8_FRANCE_BAVARIA_RESERVED_IDS)

    def test_queue_contracts_fail_closed_on_missing_changed_or_future_exact_rows(
        self,
    ) -> None:
        missing = [
            row
            for row in self.hced_rows
            if row.get("candidate_id") != "hced-Gefrees1809-1"
        ]
        with self.assertRaisesRegex(ValueError, "expected exactly one queue row"):
            validate_wave8_france_bavaria_queue_contracts(missing)

        tampered = copy.deepcopy(self.hced_rows)
        row = next(
            item
            for item in tampered
            if item.get("candidate_id") == "hced-Neumarkt-St-Viet1809-1"
        )
        row["winner_raw"] = "France, Bavaria"
        with self.assertRaisesRegex(ValueError, "raw-row fingerprint changed"):
            validate_wave8_france_bavaria_queue_contracts(tampered)

        future = copy.deepcopy(self.hced_rows)
        extra = copy.deepcopy(
            next(
                item
                for item in future
                if item.get("candidate_id") == "hced-Gefrees1809-1"
            )
        )
        extra["candidate_id"] = "hced-Future-France-Bavaria1810-1"
        extra["name"] = "Future France Bavaria"
        extra["year_low"] = extra["year_high"] = 1810
        future.append(extra)
        with self.assertRaisesRegex(ValueError, "exact-label inventory changed"):
            validate_wave8_france_bavaria_queue_contracts(future)

    def test_sources_are_independent_parseable_https_authoritative_fixtures(self) -> None:
        self.assertEqual(len(WAVE8_FRANCE_BAVARIA_SOURCES), 11)
        self.assertEqual(
            len({source["source_family_id"] for source in WAVE8_FRANCE_BAVARIA_SOURCES}),
            11,
        )
        publishers = " ".join(
            str(source["publisher"]) for source in WAVE8_FRANCE_BAVARIA_SOURCES
        )
        for expected in (
            "University of Bamberg",
            "McGill University",
            "Bavarian General Staff",
            "Fondation Napoléon",
            "Great Russian Encyclopedia",
        ):
            self.assertIn(expected, publishers)
        source_types = {
            str(source["source_type"]) for source in WAVE8_FRANCE_BAVARIA_SOURCES
        }
        self.assertIn("official_military_history", source_types)
        self.assertIn("national_scholarly_encyclopedia", source_types)
        self.assertIn("scholarly_military_history_monograph", source_types)
        for source in WAVE8_FRANCE_BAVARIA_SOURCES:
            Source.from_dict(source)
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual(
                source["evidence_roles"],
                sorted(set(source["evidence_roles"])),
            )
            self.assertIn("outcome", source["evidence_roles"])
            self.assertEqual(source["accessed"], "2026-07-16")

    def test_actor_identity_is_one_event_fixture_plus_four_existing_regimes(self) -> None:
        self.assertEqual(
            {entity["id"] for entity in WAVE8_FRANCE_BAVARIA_ENTITIES},
            {NEW_FREE_CORPS},
        )
        entity = WAVE8_FRANCE_BAVARIA_ENTITIES[0]
        Entity.from_dict(entity)
        self.assertEqual((entity["start_year"], entity["end_year"]), (1809, 1809))
        self.assertEqual((entity["aliases"], entity["predecessors"]), ([], []))
        note = entity["continuity_note"].casefold()
        for phrase in (
            "no rating is inherited",
            "brunswick",
            "hesse-kassel",
            "dynasty",
            "another coalition",
            "another campaign",
        ):
            self.assertIn(phrase, note)

        self.assertEqual(
            WAVE8_FRANCE_BAVARIA_REQUIRED_EXISTING_ENTITY_IDS,
            {AUSTRIA, FRANCE, BAVARIA, RUSSIA},
        )
        self.assertEqual(
            validate_wave8_france_bavaria_existing_entities(
                {entity["id"]: entity for entity in self.release_entities}
            ),
            {"new_event_bounded_entities": 1, "reused_time_bounded_entities": 4},
        )
        expected_windows = {
            AUSTRIA: (1804, 1867),
            FRANCE: (1804, 1815),
            BAVARIA: (1806, 1918),
            RUSSIA: (1721, 1917),
        }
        self.assertEqual(
            {
                entity_id: (
                    disposition["start_year"],
                    disposition["end_year"],
                )
                for entity_id, disposition in (
                    WAVE8_FRANCE_BAVARIA_REGIME_ENTITY_DISPOSITIONS.items()
                )
            },
            expected_windows,
        )

    def test_existing_lane_overlap_reuses_bavaria_without_reowning_candidates(
        self,
    ) -> None:
        self.assertEqual(
            set(WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT),
            {AUSTRIA, FRANCE, BAVARIA, RUSSIA},
        )
        self.assertEqual(
            WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT[BAVARIA][
                "existing_owner"
            ],
            "wave7_west_bavaria_sequence",
        )
        self.assertFalse(
            WAVE8_FRANCE_BAVARIA_RESERVED_IDS & WAVE7_WEST_BAVARIA_NEW_IDS
        )
        for audit in WAVE8_FRANCE_BAVARIA_EXISTING_LANE_OVERLAP_AUDIT.values():
            self.assertEqual(audit["candidate_id_overlap"], [])
            self.assertEqual(
                audit["disposition"],
                "reuse_identity_without_reowning_existing_events",
            )
        release_candidate_ids = {
            event.get("hced_candidate_id") for event in self.release_events
        }
        self.assertFalse(
            WAVE8_FRANCE_BAVARIA_RESERVED_IDS & release_candidate_ids
        )

    def test_installers_are_idempotent_copy_fixtures_and_reject_collisions(
        self,
    ) -> None:
        entities, sources, _ = self._installed()
        entity_fixture = WAVE8_FRANCE_BAVARIA_ENTITIES[0]
        source_by_id = {
            str(source["id"]): source for source in WAVE8_FRANCE_BAVARIA_SOURCES
        }
        install_wave8_france_bavaria_entities(entities)
        install_wave8_france_bavaria_sources(sources)
        self.assertEqual(entities[NEW_FREE_CORPS], entity_fixture)
        self.assertIsNot(entities[NEW_FREE_CORPS], entity_fixture)
        for source_id, fixture in source_by_id.items():
            self.assertEqual(sources[source_id], fixture)
            self.assertIsNot(sources[source_id], fixture)

        with self.assertRaisesRegex(ValueError, "entity collision"):
            install_wave8_france_bavaria_entities(
                {NEW_FREE_CORPS: {"id": NEW_FREE_CORPS, "name": "collision"}}
            )
        first_source_id = next(iter(source_by_id))
        with self.assertRaisesRegex(ValueError, "source collision"):
            install_wave8_france_bavaria_sources(
                {first_source_id: {"id": first_source_id, "title": "collision"}}
            )

    def test_contracts_pin_actor_composition_dates_and_raw_outcome_orientation(
        self,
    ) -> None:
        row_by_id = {str(row.get("candidate_id")): row for row in self.hced_rows}
        source_by_id = {
            str(source["id"]): source for source in WAVE8_FRANCE_BAVARIA_SOURCES
        }
        expected_dates = {
            "hced-Gefrees1809-1": ("Battle of Gefrees", "day", "8 July 1809"),
            "hced-Neumarkt-St-Viet1809-1": (
                "Battle of Neumarkt-Sankt Veit",
                "day",
                "24 April 1809",
            ),
            "hced-Polotsk (2nd)1812-1": (
                "Second Battle of Polotsk",
                "day_range",
                "18-20 October 1812",
            ),
        }
        for candidate_id, contract in WAVE8_FRANCE_BAVARIA_CONTRACTS.items():
            side_1, side_2 = EXPECTED_SIDES[candidate_id]
            self.assertEqual(set(contract["side_1_entity_ids"]), side_1)
            self.assertEqual(set(contract["side_2_entity_ids"]), side_2)
            self.assertEqual(contract["winner_side"], 1)
            self.assertEqual(
                (
                    contract["canonical_event"]["name"],
                    contract["canonical_event"]["date_precision"],
                    contract["canonical_event"]["date_text"],
                ),
                expected_dates[candidate_id],
            )
            self.assertEqual(
                row_by_id[candidate_id]["winner_raw"],
                row_by_id[candidate_id]["side_1_raw"],
            )
            self.assertEqual(
                row_by_id[candidate_id]["loser_raw"],
                row_by_id[candidate_id]["side_2_raw"],
            )
            self.assertIs(contract["source_outcome_override"], False)
            self.assertIs(contract["outcome_reversal"], False)
            self.assertGreaterEqual(len(contract["outcome_source_family_ids"]), 2)
            self.assertEqual(
                contract["outcome_source_family_ids"],
                sorted(
                    {
                        source_by_id[source_id]["source_family_id"]
                        for source_id in contract["outcome_source_ids"]
                    }
                ),
            )
        self.assertFalse(WAVE8_FRANCE_BAVARIA_OUTCOME_OVERRIDES)

    def test_first_polotsk_is_an_explicit_unknown_not_a_draw(self) -> None:
        self.assertEqual(
            WAVE8_FRANCE_BAVARIA_HOLD_IDS,
            {"hced-Polotsk (1st)1812-1"},
        )
        hold = WAVE8_FRANCE_BAVARIA_HOLDS["hced-Polotsk (1st)1812-1"]
        self.assertEqual(hold["disposition"], "hold")
        self.assertEqual(hold["result_type"], "unknown")
        self.assertIs(hold["unknown_is_never_draw"], True)
        self.assertEqual(
            hold["hold_category"],
            "historiographically_contested_outcome",
        )
        for forbidden in (
            "winner_side",
            "side_1_entity_ids",
            "side_2_entity_ids",
            "outcome_source_ids",
            "outcome_source_family_ids",
        ):
            self.assertNotIn(forbidden, hold)
        reason = hold["hold_reason"].casefold()
        for phrase in ("conflict", "not promoted", "unknown", "draw"):
            self.assertIn(phrase, reason)
        positions = hold["conflicting_outcome_positions"]
        self.assertFalse(
            set(positions["french_tactical_victory"])
            & set(positions["failed_french_attack_or_russian_success"])
        )
        self.assertGreaterEqual(len(hold["evidence_refs"]), 3)
        self.assertFalse(WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS)
        self.assertFalse(WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSION_IDS)
        self.assertIs(
            WAVE8_FRANCE_BAVARIA_EXCLUSIONS,
            WAVE8_FRANCE_BAVARIA_TERMINAL_EXCLUSIONS,
        )
        self.assertEqual(
            WAVE8_FRANCE_BAVARIA_NONPROMOTIONS,
            WAVE8_FRANCE_BAVARIA_HOLDS,
        )

    def test_emission_rates_only_three_attested_tactical_wins(self) -> None:
        events, entities, sources, _ = self._emit()
        self.assertEqual(
            [event["hced_candidate_id"] for event in events],
            [
                "hced-Gefrees1809-1",
                "hced-Neumarkt-St-Viet1809-1",
                "hced-Polotsk (2nd)1812-1",
            ],
        )
        self.assertEqual(
            {event["hced_candidate_id"] for event in events},
            WAVE8_FRANCE_BAVARIA_CONTRACT_IDS,
        )
        self.assertFalse(
            {event["hced_candidate_id"] for event in events}
            & WAVE8_FRANCE_BAVARIA_HOLD_IDS
        )
        self.assertEqual(len(events), 3)
        self.assertEqual(len({event["id"] for event in events}), 3)
        for event in events:
            Event.from_dict(event)
            self.assertTrue(event["id"].startswith(EVENT_ID_PREFIX))
            self.assertEqual(event["status"], "complete")
            self.assertEqual(event["identity_resolution"], "candidate_keyed_exact")
            self.assertEqual(event["war_type"], "interstate_war")
            self.assertGreaterEqual(len(event["outcome_source_family_ids"]), 2)
            self.assertLessEqual(
                set(event["outcome_source_ids"]),
                set(event["source_ids"]),
            )
            self.assertLessEqual(
                set(event["outcome_source_ids"]),
                set(sources),
            )
            self.assertIn(NEW_FREE_CORPS, entities)

    def test_emitted_participants_match_the_audited_regime_splits(self) -> None:
        events, _, _, _ = self._emit()
        by_candidate = {event["hced_candidate_id"]: event for event in events}
        for candidate_id, (winners, losers) in EXPECTED_SIDES.items():
            participants = by_candidate[candidate_id]["participants"]
            actual_winners = {
                participant["entity_id"]
                for participant in participants
                if participant["outcome"]["battlefield_control"] > 0.5
            }
            actual_losers = {
                participant["entity_id"]
                for participant in participants
                if participant["outcome"]["battlefield_control"] < 0.5
            }
            self.assertEqual(actual_winners, winners)
            self.assertEqual(actual_losers, losers)
        gefrees = by_candidate["hced-Gefrees1809-1"]
        self.assertEqual(
            {participant["entity_id"] for participant in gefrees["participants"]},
            {AUSTRIA, NEW_FREE_CORPS, FRANCE, BAVARIA},
        )

    def test_location_review_withholds_points_without_mutating_shared_manifests(
        self,
    ) -> None:
        before_points = frozenset(HCED_POINT_QUARANTINE_IDS)
        before_countries = frozenset(HCED_COUNTRY_QUARANTINE_IDS)
        events, _, _, _ = self._emit()
        self.assertEqual(
            WAVE8_FRANCE_BAVARIA_POINT_QUARANTINE_ADDITIONS,
            WAVE8_FRANCE_BAVARIA_CONTRACT_IDS,
        )
        self.assertFalse(WAVE8_FRANCE_BAVARIA_COUNTRY_QUARANTINE_ADDITIONS)
        self.assertEqual(
            set(WAVE8_FRANCE_BAVARIA_LOCATION_REVIEWS),
            WAVE8_FRANCE_BAVARIA_CONTRACT_IDS,
        )
        for event in events:
            self.assertNotIn("geometry", event)
        self.assertEqual(frozenset(HCED_POINT_QUARANTINE_IDS), before_points)
        self.assertEqual(frozenset(HCED_COUNTRY_QUARANTINE_IDS), before_countries)
        additions = wave8_france_bavaria_location_quarantine_additions()
        self.assertEqual(additions["point"], WAVE8_FRANCE_BAVARIA_CONTRACT_IDS)
        self.assertEqual(additions["country"], frozenset())

    def test_related_hced_and_zero_overlap_duplicate_audits_are_pinned(self) -> None:
        expected_related = {
            "hced-Jacobovo1812-1",
            "hced-Neumarkt1796-1",
            "hced-Polotsk1563-1",
            "hced-Polotsk1579-1",
        }
        self.assertEqual(
            set(WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS),
            expected_related,
        )
        row_by_id = {str(row.get("candidate_id")): row for row in self.hced_rows}
        for candidate_id, disposition in (
            WAVE8_FRANCE_BAVARIA_RELATED_HCED_DISPOSITIONS.items()
        ):
            self.assertEqual(
                canonical_hced_row_sha256(row_by_id[candidate_id]),
                disposition["raw_row_sha256"],
            )
        self.assertEqual(
            set(WAVE8_FRANCE_BAVARIA_IWBD_ZERO_OVERLAP_AUDIT),
            WAVE8_FRANCE_BAVARIA_RESERVED_IDS,
        )
        self.assertFalse(WAVE8_FRANCE_BAVARIA_IWBD_DUPLICATE_DISPOSITIONS)
        self.assertFalse(WAVE8_FRANCE_BAVARIA_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS)
        self.assertFalse(WAVE8_FRANCE_BAVARIA_CROSS_LANE_DISPOSITIONS)
        _, _, existing = self._installed()
        self.assertEqual(
            validate_wave8_france_bavaria_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                existing,
            ),
            {
                "cross_lane_hced_dispositions": 0,
                "existing_release_duplicate_dispositions": 0,
                "integration_dispositions": 4,
                "iwbd_duplicate_dispositions": 0,
                "iwbd_probable_twins": 0,
                "related_hced_dispositions": 4,
            },
        )

    def test_integration_validator_rejects_future_twins_and_candidate_collisions(
        self,
    ) -> None:
        _, _, existing = self._installed()
        hced_twin = [
            *self.hced_rows,
            {
                "candidate_id": "hced-future-gefrees-twin",
                "name": "Battle of Gefrees",
                "year_low": 1809,
                "year_high": 1809,
                "side_1_raw": "Future A",
                "side_2_raw": "Future B",
            },
        ]
        with self.assertRaisesRegex(ValueError, "cross-lane HCED twin"):
            validate_wave8_france_bavaria_integration_dispositions(
                hced_twin,
                self.iwbd_rows,
                existing,
            )

        iwbd_twin = [
            *self.iwbd_rows,
            {
                "candidate_id": "iwbd-future-polotsk-twin",
                "name": "Second Battle of Polotsk",
                "year": 1812,
            },
        ]
        with self.assertRaisesRegex(ValueError, "probable IWBD twin"):
            validate_wave8_france_bavaria_integration_dispositions(
                self.hced_rows,
                iwbd_twin,
                existing,
            )

        release_twin = [
            *existing,
            {
                "id": "future_neumarkt_twin",
                "name": "Battle of Neumarkt-Sankt Veit",
                "year": 1809,
            },
        ]
        with self.assertRaisesRegex(ValueError, "existing-release twin"):
            validate_wave8_france_bavaria_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                release_twin,
            )

        ownership_collision = [
            *existing,
            {
                "id": "future_candidate_collision",
                "name": "Unrelated name",
                "year": 1809,
                "hced_candidate_id": "hced-Gefrees1809-1",
            },
        ]
        with self.assertRaisesRegex(ValueError, "candidate ownership collision"):
            validate_wave8_france_bavaria_integration_dispositions(
                self.hced_rows,
                self.iwbd_rows,
                ownership_collision,
            )

    def test_regime_and_event_entity_window_failures_are_closed(self) -> None:
        entities, _, existing = self._installed()
        missing = copy.deepcopy(entities)
        missing.pop(BAVARIA)
        with self.assertRaisesRegex(ValueError, "missing required existing entity"):
            validate_wave8_france_bavaria_existing_entities(missing)
        with self.assertRaisesRegex(ValueError, "missing required existing entity"):
            promote_wave8_france_bavaria_contracts(
                self.hced_rows,
                missing,
                existing,
            )

        drifted = copy.deepcopy(entities)
        drifted[BAVARIA]["end_year"] = 1917
        with self.assertRaisesRegex(ValueError, "existing entity boundary changed"):
            validate_wave8_france_bavaria_existing_entities(drifted)

        event_window_drift = copy.deepcopy(entities)
        event_window_drift[NEW_FREE_CORPS]["start_year"] = 1810
        with self.assertRaisesRegex(ValueError, "entity-window violation"):
            promote_wave8_france_bavaria_contracts(
                self.hced_rows,
                event_window_drift,
                existing,
            )

    def test_promoter_rejects_existing_canonical_event_duplicate(self) -> None:
        entities, _, existing = self._installed()
        existing.append(
            {
                "id": "future_gefrees_duplicate",
                "name": "Battle of Gefrees",
                "year": 1809,
            }
        )
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            promote_wave8_france_bavaria_contracts(
                self.hced_rows,
                entities,
                existing,
            )


if __name__ == "__main__":
    unittest.main()
